/**
 * dsh-research-suite v3.0.1 · 入口
 *
 * 设计约束（DSH 0.2.1-rc.5 与 0.2.2-rc.1 实测）：
 * 1. 不得静态 import 任何 @deepseek-ai/*（pnpm 布局下在本包位置解析不到）。
 * 2. ctx.skills.register() 必须当场内联 content 字符串——runtime provider 的
 *    get(candidate) 直接返回 locator，校验要求 typeof content === 'string'。
 * 3. 技能与工具都是硬依赖，必须写进 inject：0.2.2-rc.1 里 `tools` 服务在 apply
 *    执行时常常还没就绪，同步 ctx.get('tools') 会拿到 undefined，7 个工具就静默
 *    丢失（技能与策略段却都正常，极难发现）。cordis 的 inject 会等依赖就绪。
 * 4. systemPrompt 仍然按可选处理：同步拿不到时用 ctx.inject() 延迟补装，避免
 *    在某些 profile（无 agent 运行时）里把整插件卡死在 pending。
 * 5. 不要导出 Config：Standard Schema 的 toJSON() 会被 Host 的 settings 服务当
 *    schemastery 信封水合，读 schema.meta.volatile 时崩溃导致 DSH 起不来。
 */

import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { createCore } from './core.js';
import { createTools } from './tools.js';
import { buildPolicy, SECTION_NAME, SECTION_ORDER } from './prompt.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(HERE);

export const name = 'dsh-research-suite';

/** 技能注册是能力底座；工具是第二个硬依赖（见文件头第 3 条）。 */
export const inject = ['skills', 'tools'];

const DEFAULTS = { autoTakeover: true, sectionOrder: SECTION_ORDER, verbose: false };

function validateConfig(value) {
  const issues = [];
  const out = { ...DEFAULTS };
  if (value === undefined || value === null) return { value: out };
  if (typeof value !== 'object' || Array.isArray(value)) {
    return { issues: [{ message: '配置必须是一个对象', path: [] }] };
  }
  if ('autoTakeover' in value) {
    if (typeof value.autoTakeover !== 'boolean') issues.push({ message: 'autoTakeover 必须是布尔值', path: ['autoTakeover'] });
    else out.autoTakeover = value.autoTakeover;
  }
  if ('sectionOrder' in value) {
    const n = value.sectionOrder;
    if (!Number.isFinite(n) || n < 100 || n > 5000) issues.push({ message: 'sectionOrder 必须是 100~5000 之间的数字', path: ['sectionOrder'] });
    else out.sectionOrder = Math.trunc(n);
  }
  if ('verbose' in value) {
    if (typeof value.verbose !== 'boolean') issues.push({ message: 'verbose 必须是布尔值', path: ['verbose'] });
    else out.verbose = value.verbose;
  }
  if (issues.length) return { issues };
  return { value: out };
}

// 2026-11-06 修复：原实现把 Config 定义成 Standard Schema（`~standard`）+ 返回
// JSON-Schema 的 toJSON()。loader 的 resolveConfig() 确实接受 `~standard`，但
// Host 的 settings 服务（settings/describe）会把 Config.toJSON() 的结果当作
// **schemastery 信封**用 `new Schema(json)` 重新水合；这里返回的是 JSON-Schema，
// 水合后 schema.meta 为 undefined，settings/describe 随即抛
// "Cannot read properties of undefined (reading 'volatile')"，
// 桌面端 openInitialWindow 因此在欢迎页阶段直接崩溃（Web RPC failed）。
// 本插件无法静态 import @deepseek-ai/schemastery（pnpm 下按真实路径解析不到），
// 故不再对外暴露 Config：配置由 apply() 内部的 validateConfig() 兜底默认值，
// 需要覆盖时在 profile 的 cordis.patch.yml 里直接写 entry config 即可。


/** 极简 frontmatter 解析：只认 `key: value` 与 `key: |` 块标量。 */
function parseFrontmatter(text) {
  const meta = {};
  if (!text.startsWith('---')) return { meta, body: text };
  const end = text.indexOf('\n---', 3);
  if (end < 0) return { meta, body: text };
  const head = text.slice(3, end);
  const body = text.slice(end + 4).replace(/^\r?\n/, '');
  const lines = head.split(/\r?\n/);
  let key = null;
  let block = null;
  for (const raw of lines) {
    if (block !== null) {
      if (/^\s+\S/.test(raw) || raw.trim() === '') {
        block.push(raw.replace(/^\s{0,4}/, ''));
        continue;
      }
      meta[key] = block.join('\n').trim();
      block = null;
      key = null;
    }
    const m = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(raw);
    if (!m) continue;
    const k = m[1];
    const v = m[2].trim();
    if (v === '|' || v === '>') {
      key = k;
      block = [];
    } else {
      meta[k] = v.replace(/^["']|["']$/g, '');
    }
  }
  if (block !== null && key) meta[key] = block.join('\n').trim();
  return { meta, body };
}

const SKILL_NAME = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function readSkills(root, log) {
  const dir = join(root, 'skills');
  const out = [];
  if (!existsSync(dir)) {
    log('warn', `skills/ 不存在，跳过技能注册：${dir}`);
    return out;
  }
  for (const entry of readdirSync(dir).sort()) {
    if (!entry.endsWith('.md')) continue;
    const file = join(dir, entry);
    if (!statSync(file).isFile()) continue;
    let text;
    try {
      text = readFileSync(file, 'utf8');
    } catch (err) {
      log('warn', `技能文件读取失败，跳过：${entry}（${err.message}）`);
      continue;
    }
    const { meta } = parseFrontmatter(text);
    const skillName = String(meta.name ?? entry.replace(/\.md$/, '')).trim();
    const description = String(meta.description ?? '').trim();
    if (!SKILL_NAME.test(skillName)) {
      log('warn', `技能名不合规（要求 kebab-case），跳过：${entry} → ${skillName}`);
      continue;
    }
    if (!description) {
      log('warn', `技能缺 description，跳过：${entry}`);
      continue;
    }
    out.push({ name: skillName, description, whenToUse: meta.whenToUse ? String(meta.whenToUse) : undefined, file, text });
  }
  return out;
}

function readVersion(root) {
  try {
    return JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')).version ?? '0.0.0';
  } catch {
    return '0.0.0';
  }
}

/**
 * 安全取服务：先试 ctx.<name>（cordis 注入后的属性），再试 ctx.get('<name>')。
 * 两条路都 try/catch——某些 cordis 版本访问未就绪的服务属性会抛错，
 * 不能让一次取服务把整个 apply 掀翻（技能已经注册成功了）。
 */
function readService(ctx, name) {
  if (!ctx) return undefined;
  try {
    const direct = ctx[name];
    if (direct !== undefined && direct !== null) return direct;
  } catch {
    /* 服务未就绪，走 get() */
  }
  try {
    if (typeof ctx.get === 'function') return ctx.get(name) ?? undefined;
  } catch {
    /* 服务不存在 */
  }
  return undefined;
}

export function apply(ctx, config) {
  const log = (level, message) => {
    const logger = ctx?.logger;
    const fn = logger && typeof logger[level] === 'function' ? logger[level].bind(logger) : null;
    if (fn) fn(message);
  };

  let settings;
  try {
    const result = validateConfig(config);
    if (result.issues?.length) {
      const msg = result.issues.map((i) => i.message).join('；');
      throw new Error(`配置校验失败：${msg}`);
    }
    settings = result.value;
  } catch (err) {
    log('error', err.message);
    throw err;
  }

  const version = readVersion(ROOT);
  const core = createCore(ROOT, settings);
  const disposers = [];
  // 装载结果写进策略段（系统提示）里，方便一眼看出工具是否真的注册上了。
  const loadStatus = { skills: 0, tools: 0 };
  const track = (dispose) => {
    if (typeof dispose === 'function') disposers.push(dispose);
  };

  // ---- 1) 技能：10 份融合 SOP，content 必须内联 ----
  const skills = readSkills(ROOT, log);
  let registeredSkills = 0;
  for (const skill of skills) {
    try {
      track(
        ctx.skills.register({
          name: skill.name,
          description: skill.description,
          whenToUse: skill.whenToUse,
          content: skill.text,
          path: skill.file,
          source: 'runtime',
          provider: 'dsh-research-suite',
          invocation: { modelInvocable: true, userInvocable: true },
          resourceBase: { kind: 'directory', path: dirname(skill.file) },
          metadata: { suite: 'dsh-research-suite', version },
        }),
      );
      registeredSkills += 1;
      loadStatus.skills = registeredSkills;
    } catch (err) {
      log('warn', `技能注册失败：${skill.name}（${err.message}）`);
    }
  }

  // ---- 2) 工具：7 个只读工具（tools 已写进 inject，正常情况下此刻必就绪） ----
  let registeredTools = 0;
  const installTools = (tools, why) => {
    if (!tools || typeof tools.register !== 'function') {
      log('warn', `tools 服务不可用（${why}），7 个研究工具未注册。`);
      return false;
    }
    try {
      for (const definition of createTools(core)) {
        track(tools.register(definition));
        registeredTools += 1;
        loadStatus.tools = registeredTools;
      }
      return true;
    } catch (err) {
      log('error', `工具注册失败：${err.message}`);
      return false;
    }
  };

  const injectedTools = readService(ctx, 'tools');
  if (!installTools(injectedTools, 'apply 同步阶段未拿到服务')) {
    // 兜底：极少数宿主把服务晚一帧挂上，用 inject 子 fiber 再补一次。
    if (typeof ctx.inject === 'function') {
      try {
        ctx.inject(['tools'], (scope) => {
          installTools(readService(scope, 'tools'), '延迟注入阶段');
        });
      } catch (err) {
        log('warn', `tools 延迟注入失败：${err.message}`);
      }
    }
  }

  // ---- 3) 系统提示：自动接管科研任务的关键杠杆 ----
  let promptInstalled = false;
  const installPolicy = (systemPrompt, why) => {
    if (!systemPrompt || typeof systemPrompt.section !== 'function') {
      log('warn', `systemPrompt 服务不可用（${why}），自动接管策略段未注入。`);
      return false;
    }
    track(systemPrompt.section({ name: SECTION_NAME, order: settings.sectionOrder, text: () => buildPolicy(core, loadStatus) }));
    promptInstalled = true;
    return true;
  };

  if (settings.autoTakeover) {
    const injectedPrompt = readService(ctx, 'systemPrompt');
    if (!installPolicy(injectedPrompt, 'apply 同步阶段未拿到服务') && typeof ctx.inject === 'function') {
      try {
        ctx.inject(['systemPrompt'], (scope) => {
          installPolicy(readService(scope, 'systemPrompt'), '延迟注入阶段');
        });
      } catch (err) {
        log('warn', `systemPrompt 延迟注入失败：${err.message}`);
      }
    }
  }

  const dispose = () => {
    while (disposers.length) {
      const fn = disposers.pop();
      try {
        fn();
      } catch {
        /* 卸载失败不阻塞其他清理 */
      }
    }
  };
  if (typeof ctx.effect === 'function') ctx.effect(() => dispose);
  else if (typeof ctx.on === 'function') ctx.on('dispose', dispose);

  const stats = core.stats;
  log(
    'info',
    `[dsh-research-suite ${version}] 技能 ${registeredSkills}/${skills.length}｜工具 ${registeredTools}｜策略段 ${promptInstalled ? 'on' : 'off'}｜能力卡 ${stats.capabilities} 张 / ${stats.domains} 域｜技能索引 ${stats.skills} 条`,
  );
  if (settings.verbose) {
    log('info', `[dsh-research-suite] 包根 ${ROOT}`);
    for (const d of core.domains) log('info', `[dsh-research-suite] 域 ${d.domain}（${d.label}）${d.count} 张 → ${d.skill}`);
  }
}
