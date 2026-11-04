#!/usr/bin/env node
/**
 * verify-capabilities.mjs —— 能力卡静态校验（契约来源：docs/CAPABILITY-SPEC.md §3.1 / §3.2）
 *
 * 用法：
 *   node scripts/verify-capabilities.mjs            # 等价于 all
 *   node scripts/verify-capabilities.mjs all        # 校验 data/capabilities/*.json 全部
 *   node scripts/verify-capabilities.mjs stats      # 只校验 data/capabilities/stats.json
 *
 * 退出码：0 = 无错误（可能有 warning）；1 = 至少一条 ERROR（含文件缺失、catalog 缺失、JSON 不可解析）。
 * 只依赖 node 内置模块；只读，不写任何文件。
 */

import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const CAP_DIR = path.join(ROOT, 'data', 'capabilities');
const CATALOG = path.join(ROOT, 'knowledge', 'catalog.json');

/** SPEC §3.2 每域能力数区间（下限, 上限） */
const DOMAIN_RANGE = {
  writing: [8, 12],
  polish: [5, 7],
  figures: [7, 10],
  stats: [12, 18],
  ideation: [5, 7],
  review: [5, 8],
  slides: [5, 7],
  literature: [8, 12],
  format: [5, 7],
};

const ID_RE = /^[a-z][a-z0-9]*\.[a-z0-9-]+$/;
const VERDICTS = new Set(['主用', '补强', '兜底', '弃用']);
const TOP_REQUIRED = ['domain', 'label', 'skill', 'version', 'summary'];
const CAP_KNOWN_KEYS = new Set([
  'id', 'label', 'summary', 'triggers', 'inputs', 'members',
  'protocol', 'decide', 'gates', 'outputs', 'kb',
]);

// ---------- 文本/长度工具 ----------

/** 按“字”计长：中文按字、emoji/代理对按 1 计。 */
const len = (s) => [...String(s)].length;

const isNonEmptyStr = (v) => typeof v === 'string' && v.trim() !== '';

/** 逐条检查字符串数组的元素是否满足长度区间，返回问题列表。 */
function checkStrList(arr, field, minCount, maxCount, minLen, maxLen) {
  const problems = [];
  if (!Array.isArray(arr)) {
    problems.push(`${field}: 必须是数组，实际是 ${describeType(arr)}`);
    return problems;
  }
  if (arr.length < minCount) problems.push(`${field}: 至少 ${minCount} 条，实际 ${arr.length} 条`);
  if (maxCount != null && arr.length > maxCount) {
    problems.push(`${field}: 至多 ${maxCount} 条，实际 ${arr.length} 条`);
  }
  arr.forEach((item, i) => {
    if (typeof item !== 'string') {
      problems.push(`${field}[${i}]: 必须是字符串，实际是 ${describeType(item)}`);
      return;
    }
    const t = item.trim();
    if (t === '') {
      problems.push(`${field}[${i}]: 空字符串`);
      return;
    }
    const n = len(t);
    if (minLen != null && n < minLen) problems.push(`${field}[${i}]: 只有 ${n} 字，至少 ${minLen} 字（"${clip(t)}"）`);
    if (maxLen != null && n > maxLen) problems.push(`${field}[${i}]: 有 ${n} 字，超过 ${maxLen} 字（"${clip(t)}"）`);
  });
  return problems;
}

function describeType(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return 'array';
  return typeof v;
}

const clip = (s, n = 24) => (len(s) > n ? [...s].slice(0, n).join('') + '…' : s);

/** Levenshtein 距离（用于“最接近的 3 个候选”） */
function lev(a, b) {
  const m = a.length, n = b.length;
  if (!m) return n;
  if (!n) return m;
  let prev = Array.from({ length: n + 1 }, (_, j) => j);
  for (let i = 1; i <= m; i++) {
    const cur = [i];
    for (let j = 1; j <= n; j++) {
      cur[j] = Math.min(
        prev[j] + 1,
        cur[j - 1] + 1,
        prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1),
      );
    }
    prev = cur;
  }
  return prev[n];
}

// ---------- 收集诊断 ----------

class Report {
  constructor() { this.items = []; }
  error(where, field, msg) { this.items.push({ level: 'ERROR', where, field, msg }); }
  warn(where, field, msg) { this.items.push({ level: 'WARN', where, field, msg }); }
  get errors() { return this.items.filter((i) => i.level === 'ERROR'); }
  get warns() { return this.items.filter((i) => i.level === 'WARN'); }
}

/** 把字段级问题按级别落到 report */
function land(report, where, field, problems) {
  for (const p of problems) {
    const idx = p.indexOf(':');
    const sub = idx > 0 ? p.slice(0, idx) : '';
    const msg = idx > 0 ? p.slice(idx + 1).trim() : p;
    report.error(where, sub || field, msg);
  }
}

// ---------- catalog ----------

function loadCatalog(report) {
  if (!existsSync(CATALOG)) {
    report.error('knowledge/catalog.json', '-', '文件不存在，无法对账 skill / kb / from');
    return null;
  }
  let data;
  try {
    data = JSON.parse(stripBom(readFileSync(CATALOG, 'utf8')));
  } catch (e) {
    report.error('knowledge/catalog.json', '-', `JSON 解析失败：${e.message}`);
    return null;
  }
  if (!Array.isArray(data)) {
    report.error('knowledge/catalog.json', '-', `顶层必须是数组，实际是 ${describeType(data)}`);
    return null;
  }
  const names = new Set();
  for (const entry of data) {
    if (entry && isNonEmptyStr(entry.name)) names.add(entry.name);
  }
  return { names, list: [...names].sort() };
}

/** 名字不存在时给“最接近的 3 个候选” */
function suggest(name, catalogNames) {
  const all = [...catalogNames];
  if (!all.length) return '';
  const scored = all
    .map((n) => ({ n, d: lev(String(name).toLowerCase(), n.toLowerCase()) }))
    .sort((a, b) => a.d - b.d || a.n.localeCompare(b.n))
    .slice(0, 3);
  return `；最接近的候选：${scored.map((s) => s.n).join(' / ')}`;
}

function requireInCatalog(report, catalog, where, field, name) {
  if (!isNonEmptyStr(name)) {
    report.error(where, field, '技能名为空或不是字符串');
    return false;
  }
  if (catalog && !catalog.names.has(name)) {
    report.error(where, field, `技能名不在 knowledge/catalog.json 中（禁止编造）：${name}${suggest(name, catalog.names)}`);
    return false;
  }
  return true;
}

const stripBom = (s) => (s.charCodeAt(0) === 0xfeff ? s.slice(1) : s);

/**
 * 解析 protocol.step.from 里的技能名。
 * 语法：`技能名[#该技能里的哪一节]`，多个用 `+` 连接。
 * 坑：catalog 里确实存在名字含 `+` 的技能（如 "Self-Improving + Proactive Agent"），
 * 所以不能盲切 `+`，要按 catalog 做贪心最长合并。
 * @returns {{names: string[], unresolved: string[]}}
 */
function resolveFrom(raw, catalogNames) {
  const base = raw.split('#')[0].trim(); // 去掉尾部的整段 #小节说明
  const out = { names: [], unresolved: [] };
  if (!base) return out;
  if (catalogNames.has(base)) { out.names.push(base); return out; }

  // 先按 + 切开，再贪心把相邻片段合并回 catalog 里含 + 的长名
  const segs = raw.split('#')[0].split(/[+＋]/).map((s) => s.trim());
  let i = 0;
  while (i < segs.length) {
    if (segs[i] === '') { i++; continue; }
    let matched = null;
    for (let j = segs.length; j > i; j--) {
      const joined = segs.slice(i, j).join(' + ').trim();
      if (catalogNames.has(joined)) { matched = { name: joined, next: j }; break; }
    }
    if (matched) {
      out.names.push(matched.name);
      i = matched.next;
    } else {
      out.unresolved.push(segs[i]);
      i++;
    }
  }
  return out;
}

// ---------- 单文件校验 ----------

function validateFile(domain, report, catalog, globalIds) {
  const rel = `data/capabilities/${domain}.json`;
  const abs = path.join(CAP_DIR, `${domain}.json`);
  if (!existsSync(abs)) {
    report.error(rel, '-', '文件不存在');
    return { capabilities: 0 };
  }

  let doc;
  try {
    doc = JSON.parse(stripBom(readFileSync(abs, 'utf8')));
  } catch (e) {
    report.error(rel, '-', `JSON 解析失败：${e.message}`);
    return { capabilities: 0 };
  }
  if (!doc || typeof doc !== 'object' || Array.isArray(doc)) {
    report.error(rel, '-', `顶层必须是对象，实际是 ${describeType(doc)}`);
    return { capabilities: 0 };
  }

  // —— 顶层字段 ——
  for (const key of TOP_REQUIRED) {
    if (!isNonEmptyStr(doc[key])) {
      report.error(rel, key, `${key} 缺失、为空或不是字符串`);
    }
  }
  if (isNonEmptyStr(doc.domain) && doc.domain !== domain) {
    report.error(rel, 'domain', `domain="${doc.domain}" 与文件名 "${domain}" 不一致`);
  }
  if (isNonEmptyStr(doc.skill) && doc.skill !== `research-${domain}`) {
    report.warn(rel, 'skill', `按 SPEC §四 约定应为 "research-${domain}"，实际为 "${doc.skill}"（需与 skills/research-${domain}.md 的 frontmatter name 一致）`);
  }
  if (isNonEmptyStr(doc.version) && !/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/.test(doc.version.trim())) {
    report.warn(rel, 'version', `"${doc.version}" 不是 semver，package.json.version 对账会失败`);
  }

  const caps = doc.capabilities;
  if (!Array.isArray(caps)) {
    report.error(rel, 'capabilities', `必须是数组，实际是 ${describeType(caps)}`);
    return { capabilities: 0 };
  }

  // —— 域级数量区间（SPEC §3.2）——
  const range = DOMAIN_RANGE[domain];
  if (!range) {
    report.warn(rel, 'domain', `"${domain}" 不在 SPEC §3.2 的 9 个能力域内，无法核对能力数区间`);
  } else {
    const [lo, hi] = range;
    if (caps.length < lo) report.error(rel, 'capabilities', `能力数 ${caps.length} 少于下限 ${lo}（聚类没做完）`);
    if (caps.length > hi) report.error(rel, 'capabilities', `能力数 ${caps.length} 多于上限 ${hi}（该拆域或合并）`);
  }

  const seenIds = new Map();   // id -> 位置
  const seenLabels = new Map(); // label -> 位置

  caps.forEach((cap, i) => {
    const at = `#${i + 1}`;
    if (!cap || typeof cap !== 'object' || Array.isArray(cap)) {
      report.error(`${rel}${at}`, '-', `capabilities[${i}] 必须是对象，实际是 ${describeType(cap)}`);
      return;
    }
    const where = isNonEmptyStr(cap.id) ? `${rel}/${cap.id}` : `${rel}${at}`;

    // 未知字段（多半是拼写错）
    for (const k of Object.keys(cap)) {
      if (!CAP_KNOWN_KEYS.has(k)) report.warn(where, k, `未知字段（拼写错？SPEC §三 无此键）`);
    }

    // id
    if (!isNonEmptyStr(cap.id)) {
      report.error(where, 'id', '缺失或不是字符串');
    } else {
      const id = cap.id.trim();
      if (!ID_RE.test(id)) {
        report.error(where, 'id', `不匹配 ^[a-z][a-z0-9]*\\.[a-z0-9-]+$（形如 stats.psm）：${id}`);
      }
      if (!id.startsWith(`${domain}.`)) {
        report.error(where, 'id', `必须以 "<domain>." 开头，即 "${domain}."，实际 "${id}"`);
      }
      if (seenIds.has(id)) {
        report.error(where, 'id', `域内重复，已被 ${seenIds.get(id)} 使用`);
      } else {
        seenIds.set(id, at);
      }
      if (globalIds.has(id)) {
        report.error(where, 'id', `全局重复，已被 ${globalIds.get(id)} 使用（SPEC §3.1 要求全局唯一）`);
      } else {
        globalIds.set(id, where);
      }
    }

    // label / summary
    if (!isNonEmptyStr(cap.label)) report.error(where, 'label', '缺失或为空');
    else if (seenLabels.has(cap.label)) report.error(where, 'label', `域内重复，已被 ${seenLabels.get(cap.label)} 使用`);
    else seenLabels.set(cap.label, at);
    if (!isNonEmptyStr(cap.summary)) report.error(where, 'summary', '缺失或为空');

    // triggers：3～10 条，每条 ≥2 字
    land(report, where, 'triggers', checkStrList(cap.triggers, 'triggers', 3, 10, 2, null));
    if (Array.isArray(cap.triggers)) {
      const dups = cap.triggers.filter((t, i) => typeof t === 'string' && cap.triggers.indexOf(t) !== i);
      if (dups.length) report.warn(where, 'triggers', `重复条目：${[...new Set(dups)].join(' / ')}`);
    }

    // inputs（可选字段）
    if (cap.inputs !== undefined) {
      land(report, where, 'inputs', checkStrList(cap.inputs, 'inputs', 1, null, 2, null).map((p) => p.replace(/^inputs/, 'inputs')));
    }

    // members：2～6 个
    if (!Array.isArray(cap.members)) {
      report.error(where, 'members', `必须是数组，实际是 ${describeType(cap.members)}`);
    } else {
      const n = cap.members.length;
      if (n < 2) report.error(where, 'members', `至少 2 个（少于 2 无融合可言，直接写通用步骤），实际 ${n} 个`);
      if (n > 6) report.error(where, 'members', `至多 6 个（多于 6 说明聚类没做完），实际 ${n} 个`);
      const seenSkill = new Set();
      cap.members.forEach((m, j) => {
        const mw = `${where}/members[${j}]`;
        if (!m || typeof m !== 'object' || Array.isArray(m)) {
          report.error(mw, '-', `必须是对象，实际是 ${describeType(m)}`);
          return;
        }
        if (requireInCatalog(report, catalog, mw, 'skill', m.skill) && m.skill) {
          if (seenSkill.has(m.skill)) report.warn(mw, 'skill', `同一能力内重复出现：${m.skill}`);
          seenSkill.add(m.skill);
        }
        if (!VERDICTS.has(m.verdict)) {
          report.error(mw, 'verdict', `必须 ∈ {主用,补强,兜底,弃用}，实际 ${JSON.stringify(m.verdict)}`);
        }
        land(report, mw, 'best_at', checkStrList(m.best_at, 'best_at', 1, null, 8, 40));
        land(report, mw, 'limits', checkStrList(m.limits, 'limits', 1, null, 8, 40));
        land(report, mw, 'take', checkStrList(m.take, 'take', 1, null, 8, 40));
      });
    }

    // protocol：3～8 步
    if (!Array.isArray(cap.protocol)) {
      report.error(where, 'protocol', `必须是数组，实际是 ${describeType(cap.protocol)}`);
    } else {
      const n = cap.protocol.length;
      if (n < 3) report.error(where, 'protocol', `至少 3 步，实际 ${n} 步`);
      if (n > 8) report.error(where, 'protocol', `至多 8 步，实际 ${n} 步`);
      cap.protocol.forEach((s, j) => {
        const sw = `${where}/protocol[${j}]`;
        if (!s || typeof s !== 'object' || Array.isArray(s)) {
          report.error(sw, '-', `必须是对象，实际是 ${describeType(s)}`);
          return;
        }
        for (const key of ['step', 'from', 'do', 'detail']) {
          if (!isNonEmptyStr(s[key])) report.error(sw, key, `${key} 缺失、为空或不是字符串`);
        }
        if (isNonEmptyStr(s.detail) && len(s.detail.trim()) < 40) {
          report.error(sw, 'detail', `只有 ${len(s.detail.trim())} 字，至少 40 字（SPEC §六 禁止只写步骤名不写怎么做）`);
        }
        if (isNonEmptyStr(s.step) && len(s.step.trim()) < 3) {
          report.warn(sw, 'step', `只有 ${len(s.step.trim())} 字，步骤名建议写明"动词 + 对象"`);
        }
        // from：技能名[#小节] (+ 技能名[#小节])*
        if (isNonEmptyStr(s.from) && catalog) {
          const { names, unresolved } = resolveFrom(s.from, catalog.names);
          if (names.length === 0 && unresolved.length === 0) {
            report.error(sw, 'from', `无法解析出技能名："${clip(s.from, 40)}"（格式：技能名 或 技能名#小节）`);
          }
          for (const bad of unresolved) {
            report.error(sw, 'from', `技能名不在 knowledge/catalog.json 中（禁止编造）：${bad}${suggest(bad, catalog.names)}`);
          }
        }
      });
    }

    // decide：0～4 条
    if (cap.decide !== undefined) {
      if (!Array.isArray(cap.decide)) {
        report.error(where, 'decide', `必须是数组，实际是 ${describeType(cap.decide)}`);
      } else {
        if (cap.decide.length > 4) report.error(where, 'decide', `至多 4 条，实际 ${cap.decide.length} 条`);
        cap.decide.forEach((d, j) => {
          const dw = `${where}/decide[${j}]`;
          if (!d || typeof d !== 'object' || Array.isArray(d)) {
            report.error(dw, '-', `必须是对象，实际是 ${describeType(d)}`);
            return;
          }
          for (const key of ['when', 'use', 'instead_of', 'why']) {
            if (!isNonEmptyStr(d[key])) report.error(dw, key, `${key} 缺失、为空或不是字符串`);
          }
        });
      }
    } else {
      report.warn(where, 'decide', '未提供 decide（0 条合法，但请确认确实没有真正的分歧点）');
    }

    // gates ≥2 / outputs ≥1
    land(report, where, 'gates', checkStrList(cap.gates, 'gates', 2, null, 4, null));
    land(report, where, 'outputs', checkStrList(cap.outputs, 'outputs', 1, null, 2, null));

    // kb：1～4 个且都在 catalog
    if (!Array.isArray(cap.kb)) {
      report.error(where, 'kb', `必须是数组，实际是 ${describeType(cap.kb)}`);
    } else {
      const n = cap.kb.length;
      if (n < 1) report.error(where, 'kb', '至少 1 个供 research_kb_read 深读的技能名');
      if (n > 4) report.error(where, 'kb', `至多 4 个，实际 ${n} 个`);
      cap.kb.forEach((name, j) => requireInCatalog(report, catalog, `${where}/kb[${j}]`, 'kb', name));
    }
  });

  // notes.md 体积（可选文件，SPEC §二 约定 ≤4 KB）
  const notes = path.join(CAP_DIR, `${domain}.notes.md`);
  if (existsSync(notes)) {
    const size = statSync(notes).size;
    if (size > 4096) report.warn(`data/capabilities/${domain}.notes.md`, '-', `${size} 字节，超过 SPEC §二 的 4 KB 上限`);
  }

  return { capabilities: caps.length };
}

// ---------- 主流程 ----------

function main() {
  const argv = process.argv.slice(2).filter((a) => !a.startsWith('-'));
  const target = (argv[0] || 'all').trim();
  if (target === '-h' || target === '--help' || process.argv.includes('--help')) {
    console.log('用法：node scripts/verify-capabilities.mjs [domain|all]');
    console.log('  domain ∈ ' + Object.keys(DOMAIN_RANGE).join(' | '));
    console.log('  退出码 0 = 通过，1 = 有 ERROR。只读，不写文件。');
    return 0;
  }

  const report = new Report();
  const catalog = loadCatalog(report);
  const globalIds = new Map();

  if (!existsSync(CAP_DIR)) {
    report.error('data/capabilities', '-', '目录不存在');
    return finish(report, 0, target, []);
  }

  const files = readdirSync(CAP_DIR)
    .filter((f) => f.endsWith('.json') && !f.endsWith('.notes.json'))
    .map((f) => f.slice(0, -'.json'.length))
    .sort();

  let domains;
  if (target === 'all') {
    if (files.length === 0) {
      report.error('data/capabilities', '-', '目录下没有任何 *.json 能力卡文件（尚未开始产出？）');
      return finish(report, 0, target, []);
    }
    domains = files;
  } else {
    if (!files.includes(target)) {
      const hint = files.length ? `现有：${files.join(', ')}` : '目录下没有任何 *.json 能力卡文件';
      report.error(`data/capabilities/${target}.json`, '-', `文件不存在。${hint}`);
      return finish(report, 0, target, []);
    }
    domains = [target];
  }

  let totalCaps = 0;
  const perDomain = [];
  for (const d of domains) {
    const before = report.items.length;
    const { capabilities } = validateFile(d, report, catalog, globalIds);
    totalCaps += capabilities;
    const slice = report.items.slice(before);
    perDomain.push({
      domain: d,
      caps: capabilities,
      errors: slice.filter((x) => x.level === 'ERROR').length,
      warns: slice.filter((x) => x.level === 'WARN').length,
    });
  }

  return finish(report, totalCaps, target, perDomain);
}

function finish(report, totalCaps, target, perDomain) {
  const { items } = report;
  console.log(`论衡 · 能力卡校验  dsh-research-suite  target=${target}`);
  console.log(`包根：${ROOT}`);
  console.log('');

  if (items.length) {
    for (const it of items) {
      console.log(`[${it.level}] ${it.where}: ${it.field ? it.field + ': ' : ''}${it.msg}`);
    }
    console.log('');
  }

  if (perDomain.length > 1) {
    console.log('按域：');
    for (const d of perDomain) {
      const flag = d.errors ? '✗' : '✓';
      console.log(`  ${flag} ${d.domain.padEnd(12)} 能力 ${String(d.caps).padStart(3)}  ERROR ${d.errors}  WARN ${d.warns}`);
    }
    console.log('');
  }

  const e = report.errors.length;
  const w = report.warns.length;
  console.log(`${totalCaps} capabilities, ${e} errors, ${w} warnings`);
  if (e === 0) console.log('结果：通过（exit 0）');
  else console.log('结果：不通过（exit 1）');
  return e === 0 ? 0 : 1;
}

process.exitCode = main();
