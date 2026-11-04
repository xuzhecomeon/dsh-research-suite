/**
 * dsh-research-suite v2 · 入口
 *
 * 设计约束（DSH 0.2.1-rc.5 实测）：
 * 1. 不得静态 import 任何 @deepseek-ai/*（pnpm 布局下在本包位置解析不到）。
 * 2. ctx.skills.register() 必须当场内联 content 字符串——runtime provider 的
 *    get(candidate) 直接返回 locator，校验要求 typeof content === 'string'。
 * 3. 技能是硬依赖（inject: ['skills']）；tools / systemPrompt 走 ctx.get() 有则装。
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

/** 技能注册是能力底座，缺它整个插件没有意义。 */
export const inject = ['skills'];

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

export const Config = {
  '~standard': { version: 1, vendor: 'dsh-research-suite', validate: validateConfig },
  toJSON() {
    return {
      type: 'object',
      additionalProperties: false,
      properties: {
        autoTakeover: { type: 'boolean', default: true, title: '自动接管科研任务', description: '在工作区里注入"科研任务接管"策略段；关闭后只保留显式工具与技能。' },
        sectionOrder: { type: 'number', default: SECTION_ORDER, title: '策略段排序值', description: '系统提示中的排序位置，默认 650（团队策略之后、工具说明之前）。' },
        verbose: { type: 'boolean', default: false, title: '详细日志', description: '装载时输出更多诊断信息。' },
      },
    };
  },
};

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
    } catch (err) {
      log('warn', `技能注册失败：${skill.name}（${err.message}）`);
    }
  }

  // ---- 2) 工具：7 个只读工具，有 tools 服务才装 ----
  let registeredTools = 0;
  try {
    const tools = typeof ctx.get === 'function' ? ctx.get('tools') : ctx.tools;
    if (tools && typeof tools.register === 'function') {
      for (const definition of createTools(core)) {
        track(tools.register(definition));
        registeredTools += 1;
      }
    } else if (settings.verbose) {
      log('warn', '未找到 tools 服务，7 个研究工具未注册（技能与策略段仍然可用）。');
    }
  } catch (err) {
    log('warn', `工具注册失败：${err.message}`);
  }

  // ---- 3) 系统提示：自动接管科研任务的关键杠杆 ----
  let promptInstalled = false;
  if (settings.autoTakeover) {
    try {
      const systemPrompt = typeof ctx.get === 'function' ? ctx.get('systemPrompt') : ctx.systemPrompt;
      if (systemPrompt && typeof systemPrompt.section === 'function') {
        track(systemPrompt.section({ name: SECTION_NAME, order: settings.sectionOrder, text: () => buildPolicy(core) }));
        promptInstalled = true;
      } else if (settings.verbose) {
        log('warn', '未找到 systemPrompt 服务，自动接管策略段未注入（工具与技能仍然可用）。');
      }
    } catch (err) {
      log('warn', `策略段注入失败：${err.message}`);
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
