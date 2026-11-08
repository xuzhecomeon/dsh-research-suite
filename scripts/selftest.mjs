#!/usr/bin/env node
/**
 * dsh-research-suite · 自测
 *
 * 不安装、不启动宿主：用假的 ctx 调用 apply()，验证
 *   1) 入口契约（name / inject / apply / Config）
 *   2) 9 份融合技能是否以「内联 content 字符串」注册（DSH runtime provider 的硬要求）
 *   3) 15 个工具是否符合 ToolDefinition 形态，并逐个真实执行一次
 *   4) 系统提示策略段是否注入且含关键铁律
 *   5) 能力卡 / 门禁 / 知识库是否可读
 *
 * 用法：node scripts/selftest.mjs        （退出码 0 = 全过）
 */

import { readdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = dirname(HERE);

let passed = 0;
const failures = [];
const warnings = [];

function ok(label, extra) {
  passed += 1;
  console.log(`  ✓ ${label}${extra ? `  ${extra}` : ''}`);
}
function bad(label, detail) {
  failures.push(`${label}${detail ? `：${detail}` : ''}`);
  console.log(`  ✗ ${label}${detail ? `  ${detail}` : ''}`);
}
function warn(label, detail) {
  warnings.push(`${label}${detail ? `：${detail}` : ''}`);
  console.log(`  ! ${label}${detail ? `  ${detail}` : ''}`);
}
function check(label, condition, detail) {
  if (condition) ok(label);
  else bad(label, detail);
}
function section(title) {
  console.log(`\n${title}`);
}

function fakeServices(record) {
  return {
    skills: {
      register(registration) {
        record.skills.push(registration);
        return () => {};
      },
    },
    tools: {
      register(definition) {
        record.tools.push(definition);
        return () => {};
      },
    },
    systemPrompt: {
      section(sectionDef) {
        record.sections.push(sectionDef);
        return () => {};
      },
    },
  };
}

function fakeContext() {
  const record = { skills: [], tools: [], sections: [], effects: [], logs: [], deferred: [] };
  const services = fakeServices(record);
  const ctx = {
    logger: {
      info: (m) => record.logs.push(['info', m]),
      warn: (m) => record.logs.push(['warn', m]),
      error: (m) => record.logs.push(['error', m]),
      debug: (m) => record.logs.push(['debug', m]),
    },
    get: (name) => services[name],
    // cordis 注入后的服务就是 ctx 上的属性
    skills: services.skills,
    tools: services.tools,
    systemPrompt: services.systemPrompt,
    effect: (fn) => record.effects.push(fn),
    inject: (deps, cb) => record.deferred.push({ deps, cb }),
  };
  return { ctx, record };
}

/**
 * 模拟 0.2.2-rc.1 的真实时序：apply 执行时 tools / systemPrompt 还没就绪，
 * 只能靠 ctx.inject() 子 fiber 等依赖到齐后再装。
 */
function lateContext() {
  const record = { skills: [], tools: [], sections: [], effects: [], logs: [], deferred: [] };
  const services = fakeServices(record);
  const ctx = {
    logger: {
      info: (m) => record.logs.push(['info', m]),
      warn: (m) => record.logs.push(['warn', m]),
      error: (m) => record.logs.push(['error', m]),
      debug: (m) => record.logs.push(['debug', m]),
    },
    // 关键：此刻还没有 tools / systemPrompt
    get: (name) => (name === 'skills' ? services.skills : undefined),
    skills: services.skills,
    effect: (fn) => record.effects.push(fn),
    inject: (deps, cb) => record.deferred.push({ deps, cb }),
  };
  return { ctx, record, services };
}

async function main() {
  console.log('dsh-research-suite · selftest');
  console.log(`包根：${ROOT}`);

  // ---------- 1) 入口契约 ----------
  section('1. 入口契约');
  let mod;
  try {
    mod = await import(new URL('../lib/index.js', import.meta.url).href);
  } catch (err) {
    bad('入口可 import', err.message);
    return finish();
  }
  check('导出 name', mod.name === 'dsh-research-suite', `实际 ${mod.name}`);
  check('导出 inject 含 skills', Array.isArray(mod.inject) && mod.inject.includes('skills'), JSON.stringify(mod.inject));
  // 0.2.2-rc.1 实测：tools 服务在 apply 时可能未就绪，必须写进 inject 让 cordis 等它，
  // 否则 全部研究工具会静默丢失（技能和策略段却都正常）。
  check('导出 inject 含 tools（0.2.2 工具丢失防线）', Array.isArray(mod.inject) && mod.inject.includes('tools'), JSON.stringify(mod.inject));
  check('导出 apply 函数', typeof mod.apply === 'function');

  // v3：Config 必须不存在。
  // 事故记录（2026-11-06）：曾导出 `export const Config`（Standard Schema + 返回 JSON Schema 的 toJSON()），
  // Host 的 settings 服务会把它当 schemastery 信封水合 → schema.meta 为 undefined → 读 .volatile 崩溃
  // → DSH Desktop 启动失败（"The application could not start" / "desktop welcome: Web RPC failed"）。
  // 现在配置由 apply() 内部的 validateConfig() 兜底，**不要补回 Config**。
  check('不导出 Config（v3 事故防线）', mod.Config === undefined, `实际 typeof ${typeof mod.Config}`);

  const { readFileSync: rfs } = await import('node:fs');
  const entrySrc = rfs(new URL('../lib/index.js', import.meta.url), 'utf8');
  check('入口不含 export const Config', !/export\s+const\s+Config\b/.test(entrySrc));
  check('入口含 validateConfig 兜底', /function\s+validateConfig\s*\(/.test(entrySrc));

  // 静态 import 禁令：本包不得在加载期依赖 @deepseek-ai/*
  let entryText = '';
  try {
    const { readFileSync } = await import('node:fs');
    for (const f of ['lib/index.js', 'lib/core.js', 'lib/tools.js', 'lib/prompt.js']) {
      entryText += readFileSync(join(ROOT, f), 'utf8');
    }
    const staticImport = /^\s*import\s[^;]*from\s+['"]@deepseek-ai\//m.test(entryText);
    check('无静态 @deepseek-ai/* import', !staticImport);
  } catch (err) {
    warn('静态 import 检查跳过', err.message);
  }

  // ---------- 2) apply 装配 ----------
  section('2. apply 装配');
  const { ctx, record } = fakeContext();
  try {
    mod.apply(ctx, { verbose: false });
    ok('apply 未抛错');
  } catch (err) {
    bad('apply 未抛错', err.message);
    return finish();
  }

  const skillFiles = existsSync(join(ROOT, 'skills'))
    ? readdirSync(join(ROOT, 'skills')).filter((f) => f.endsWith('.md'))
    : [];
  check(`技能注册数 = skills/*.md 数（${skillFiles.length}）`, record.skills.length === skillFiles.length, `注册 ${record.skills.length}`);
  if (skillFiles.length < 10) warn(`技能文件只有 ${skillFiles.length} 个（期望 10：入口 1 + 九域）`);

  const badSkill = record.skills.filter((s) => typeof s.content !== 'string' || !s.content.trim());
  check('每个技能都内联了 content 字符串', badSkill.length === 0, badSkill.map((s) => s.name).join(','));

  const badName = record.skills.filter((s) => !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(s.name));
  check('技能名全为 kebab-case', badName.length === 0, badName.map((s) => s.name).join(','));

  const badDesc = record.skills.filter((s) => !s.description || !s.description.trim());
  check('技能 description 非空', badDesc.length === 0, badDesc.map((s) => s.name).join(','));

  const badInv = record.skills.filter((s) => typeof s.invocation?.modelInvocable !== 'boolean' || typeof s.invocation?.userInvocable !== 'boolean');
  check('技能 invocation 两布尔齐备', badInv.length === 0, badInv.map((s) => s.name).join(','));

  const badBase = record.skills.filter((s) => s.resourceBase?.kind !== 'directory' || typeof s.resourceBase?.path !== 'string');
  check('技能 resourceBase 为目录型', badBase.length === 0, badBase.map((s) => s.name).join(','));

  check('工具注册数 = 15', record.tools.length === 15, `注册 ${record.tools.length}`);
  check('策略段注册数 = 1', record.sections.length === 1, `注册 ${record.sections.length}`);
  check('注册了 ctx.effect 清理钩子', record.effects.length >= 1);

  // ---------- 2b) 服务晚到时的延迟注入（0.2.2-rc.1 真实时序） ----------
  section('2b. 延迟注入（tools / systemPrompt 在 apply 时尚未就绪）');
  const late = lateContext();
  try {
    mod.apply(late.ctx, { verbose: false });
    ok('apply 在无 tools 服务的 ctx 上未抛错');
  } catch (err) {
    bad('apply 在无 tools 服务的 ctx 上未抛错', err.message);
  }
  check('技能仍然注册成功', late.record.skills.length === skillFiles.length, `注册 ${late.record.skills.length}`);
  check('申请了延迟注入（≥2 个依赖）', late.record.deferred.length >= 2, JSON.stringify(late.record.deferred.map((d) => d.deps)));
  const deferredDeps = late.record.deferred.flatMap((d) => d.deps);
  check('延迟依赖含 tools', deferredDeps.includes('tools'), JSON.stringify(deferredDeps));
  check('延迟依赖含 systemPrompt', deferredDeps.includes('systemPrompt'), JSON.stringify(deferredDeps));

  // 触发延迟回调：模拟 cordis 依赖到齐后建子 fiber
  for (const { deps, cb } of late.record.deferred) {
    try {
      cb(late.services);
    } catch (err) {
      bad(`延迟注入回调（${deps.join(',')}）未抛错`, err.message);
    }
  }
  check('延迟注入后工具数 = 15', late.record.tools.length === 15, `注册 ${late.record.tools.length}`);
  check('延迟注入后策略段数 = 1', late.record.sections.length === 1, `注册 ${late.record.sections.length}`);

  // ---------- 3) 工具形态 ----------
  section('3. 工具形态（ToolDefinition）');
  const seen = new Set();
  for (const tool of record.tools) {
    if (seen.has(tool.name)) bad(`工具名重复 ${tool.name}`);
    seen.add(tool.name);
    if (!/^[a-z][a-z0-9_]*$/.test(tool.name)) bad(`工具名不合规 ${tool.name}`);
    if (tool.name === 'run_code') bad('占用了保留名 run_code');
    if (typeof tool.description !== 'string' || tool.description.length < 20) bad(`工具 ${tool.name} 缺 description`);
    if (tool.parameters?.type !== 'object') bad(`工具 ${tool.name} parameters 不是 object schema`);
    if (tool.parameters && tool.parameters.additionalProperties !== false) warn(`工具 ${tool.name} additionalProperties 未设为 false`);
    if (typeof tool.output?.render !== 'function') bad(`工具 ${tool.name} output.render 不是函数`);
    if (tool.output?.schema?.type !== 'string') bad(`工具 ${tool.name} output.schema 不是 string`);
    if (typeof tool.execute !== 'function') bad(`工具 ${tool.name} execute 不是函数`);
  }
  ok(`15 个工具形态检查完成（${[...seen].join('、')}）`);

  const expectTools = [
  'research_playbook',
  'research_capability',
  'research_catalog',
  'research_kb_read',
  'research_standard',
  'research_gate',
  'research_suite_status',
  'research_run',
  'research_data_check',
  'research_output_check',
  'research_doi_check',
  'research_ref_audit',
  'research_project',
  'research_docx',
  'research_litsearch',
];
  const missingTools = expectTools.filter((n) => !seen.has(n));
  check('15 个约定工具全部存在', missingTools.length === 0, missingTools.join(','));

  // render 契约
  const sampleTool = record.tools[0];
  const blocks = sampleTool.output.render({}, 'hello');
  check('output.render 返回 ContentBlock[]', Array.isArray(blocks) && blocks[0]?.type === 'text' && blocks[0]?.text === 'hello');

  // ---------- 4) 工具真实执行 ----------
  section('4. 工具真实执行');
  const byName = Object.fromEntries(record.tools.map((t) => [t.name, t]));
  const execCtx = { deferContext() {}, concludeTurn() {} };

  async function run(name, args) {
    const tool = byName[name];
    if (!tool) return bad(`执行 ${name}`, '工具不存在');
    try {
      const value = await tool.execute(args, execCtx);
      if (typeof value !== 'string' || !value.trim()) return bad(`执行 ${name}`, `返回 ${typeof value}`);
      if (value.startsWith('[research-suite]') && value.includes('执行失败')) return bad(`执行 ${name}`, value.slice(0, 160));
      ok(`执行 ${name}`, `${String(value).length} 字符`);
      return value;
    } catch (err) {
      bad(`执行 ${name}`, err.message);
    }
  }

  const playbook = await run('research_playbook', { task: '帮我把这段讨论去 AI 味，字数别变' });
  if (playbook && !playbook.includes('融合协议')) bad('playbook 输出含融合协议', playbook.slice(0, 120));
  else if (playbook) ok('playbook 输出含融合协议与成员账本', playbook.includes('成员账本') ? '' : '（缺成员账本）');

  const playbook2 = await run('research_playbook', { task: '跑个多因素 logistic 回归并做倾向评分匹配' });
  if (playbook2 && !/stats\./.test(playbook2)) warn('stats 原话未匹配到 stats 域能力卡（能力卡未落盘时正常）');

  const caps = await run('research_capability', {});
  const cat = await run('research_catalog', { query: '倾向评分匹配', limit: 3 });
  const kb = await run('research_kb_read', { name: 'paper-deweight', limit: 2000 });
  const std = await run('research_standard', {});
  const gate = await run('research_gate', {});
  const gateText = await run('research_gate', { text: '值得注意的是，本研究首次证明了该方法完全有效, 结果显著(P<0.05)[1,2]。' });
  const status = await run('research_suite_status', {});

  if (gateText) {
    const hits = ['半角标点', 'AI 套话', '绝对化', '引用编号'].filter((k) => gateText.includes(k));
    check('research_gate 能命中机械问题', hits.length >= 2, `命中 ${hits.join('、') || '无'}`);
  }
  if (gate) check('research_gate 渲染出门禁小节', /数据六道闸门|交付自检/.test(gate), gate.slice(0, 80));
  if (status) check('research_suite_status 报告装载规模', /能力卡/.test(status));

  // 路径穿越
  const escape = await byName.research_kb_read.execute({ file: '../../../package.json' }, execCtx);
  check('research_kb_read 拒绝路径穿越', typeof escape === 'string' && (escape.includes('越界') || escape.includes('拒绝')), String(escape).slice(0, 80));

  // ---------- 5) 策略段 ----------
  section('5. 系统提示策略段');
  const promptText = typeof record.sections[0]?.text === 'function' ? record.sections[0].text({}) : record.sections[0]?.text;
  if (typeof promptText !== 'string' || promptText.length < 200) bad('策略段文本非空', `${typeof promptText}`);
  else {
    ok('策略段文本长度', `${promptText.length} 字符`);
    const needed = ['research_playbook', '全角', 'GB/T 7714', 'research_gate'];
    const missing = needed.filter((k) => !promptText.includes(k));
    check('策略段含关键铁律与入口指令', missing.length === 0, `缺 ${missing.join('、')}`);
    check('策略段不含 v1 遗留说法（research_route / 任务原型 Ax）', !/research_route|任务原型/.test(promptText));
    // 装载自检行：0.2.2-rc.1 工具丢失事故的可视化防线（模型每轮都能看到工具到底注册上没有）
    check('策略段含装载自检行', /装载自检：技能 \d+ 份｜工具 \d+ 个/.test(promptText));
    check('自检行报告工具已就绪', /工具 1[5-9] 个（`research_\*` 全部就绪）/.test(promptText));
    if (typeof record.sections[0].order !== 'number') bad('策略段 order 不是数字');
    else ok('策略段 order', String(record.sections[0].order));
  }

  // ---------- 6) 数据面 ----------
  section('6. 数据面');
  const capsDir = join(ROOT, 'data', 'capabilities');
  const capFiles = existsSync(capsDir) ? readdirSync(capsDir).filter((f) => f.endsWith('.json')) : [];
  check('存在能力卡文件', capFiles.length >= 1, `找到 ${capFiles.length} 个`);
  const domainsFound = new Set();
  let capTotal = 0;
  for (const f of capFiles) {
    try {
      const { readFileSync } = await import('node:fs');
      const doc = JSON.parse(readFileSync(join(capsDir, f), 'utf8'));
      const caps = doc.capabilities ?? [];
      capTotal += caps.length;
      for (const cap of caps) {
        if (!cap.id) bad(`${f} 有卡片缺 id`);
        else if (!cap.id.startsWith(`${doc.domain}.`)) warn(`${f} 卡片 id 前缀与域名不符：${cap.id}`);
        if (!Array.isArray(cap.members) || cap.members.length < 2) bad(`${f} ${cap.id} members < 2`);
        if (!Array.isArray(cap.protocol) || cap.protocol.length < 3) bad(`${f} ${cap.id} protocol < 3 步`);
        if (!Array.isArray(cap.gates) || cap.gates.length === 0) warn(`${f} ${cap.id} 无 gates`);
        for (const m of cap.members ?? []) {
          if (!m.skill) bad(`${f} ${cap.id} 成员缺 skill`);
        }
      }
      if (doc.domain) domainsFound.add(doc.domain);
      ok(`${f}`, `${caps.length} 张卡，域 ${doc.domain ?? '未标注'}`);
    } catch (err) {
      bad(`${f} 可解析`, err.message);
    }
  }
  console.log(`  能力卡合计 ${capTotal} 张，覆盖域 ${domainsFound.size} 个：${[...domainsFound].join('、') || '无'}`);
  const expectDomains = ['writing', 'polish', 'figures', 'stats', 'literature', 'format', 'ideation', 'review', 'slides'];
  const missingDomains = expectDomains.filter((d) => !domainsFound.has(d));
  if (missingDomains.length) warn('部分域尚无能力卡', missingDomains.join('、'));
  else ok('9 个域能力卡齐备');

  try {
    const { readFileSync } = await import('node:fs');
    const gates = JSON.parse(readFileSync(join(ROOT, 'data', 'gates.json'), 'utf8'));
    const sectionsNeeded = ['dataGates', 'selfCheck', 'mutex', 'forbidden', 'handoffs'];
    const missingGates = sectionsNeeded.filter((k) => !Array.isArray(gates[k]) || gates[k].length === 0);
    check('gate 数据面完整', missingGates.length === 0, missingGates.join('、'));
    check('gate 含 hardRules', Array.isArray(gates.hardRules) && gates.hardRules.length >= 8, `${gates.hardRules?.length} 条`);
  } catch (err) {
    bad('data/gates.json 可解析', err.message);
  }

  for (const rel of ['knowledge/catalog.json', 'knowledge/INDEX.md', 'knowledge/FUSION.md']) {
    check(`存在 ${rel}`, existsSync(join(ROOT, rel)));
  }
  check('references 有内置规范', existsSync(join(ROOT, 'references')) && readdirSync(join(ROOT, 'references')).filter((f) => /^\d\d_.*\.md$/.test(f)).length >= 5);

  return finish();
}

function finish() {
  console.log('');
  if (warnings.length) {
    console.log(`警告 ${warnings.length} 条：`);
    for (const w of warnings) console.log(`  ! ${w}`);
  }
  if (failures.length) {
    console.log(`\n失败 ${failures.length} 条：`);
    for (const f of failures) console.log(`  ✗ ${f}`);
    console.log(`\n结果：失败（通过 ${passed} 项）`);
    process.exitCode = 1;
    return;
  }
  console.log(`\n结果：通过（${passed} 项检查${warnings.length ? `，${warnings.length} 条警告` : ''}）`);
  process.exitCode = 0;
}

main().catch((err) => {
  console.error('selftest 内部错误：', err);
  process.exitCode = 1;
});
