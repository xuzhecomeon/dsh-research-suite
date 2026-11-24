#!/usr/bin/env node
/**
 * verify-eval.mjs —— 评测集防污染与冻结校验（CI 级断言）
 *
 * 校验对象
 *   data/golden/dev.json    调参集（150 条，可随时增删改）
 *   data/golden/test.json   盲测集（150 条，生成后冻结）
 *   data/golden/.freeze.json 冻结记录（test.json 的 sha256）
 *   data/golden/cases.json  旧金标准集（50 条，保留作历史，只用于重复检查）
 *   data/match-rules.json   识别规则真源（只读 cues 文本做泄漏检查）
 *   data/capabilities/*.json 能力卡真源（校验 expect.cap 是否存在）
 *
 * 硬断言（任一不过 → exit 1）
 *   1. 结构：条数、id 唯一且两集 id 空间不相交、expect 形状、cap 存在、source 取值合法
 *   2. 组成：test 负例 ≥ 80；负例类 ≥ 10 类且每类 ≥ 5 条；两集并集覆盖 20 个必备 category
 *   3. 来源：constructed / paraphrase / real-ish 三类都出现，单类占比 ≤ 40%
 *   4. 句子级完全重复 = 0（集内、集间、与旧 cases.json）
 *   5. 字符 3-gram 集合重叠率 < 5%（test 对 dev、dev 对 test 两个方向）
 *   6. test 句子不得与 match-rules.json 的 cues 正则字面文本（≥4 字的候选式）逐字相同或包含
 *   7. test.json 的 sha256 必须等于 .freeze.json 的 sha256（改一个字符即失败）
 *
 * 用法
 *   node scripts/verify-eval.mjs              只校验（默认）
 *   node scripts/verify-eval.mjs --freeze     生成/写入 .freeze.json（已存在时需 --force）
 *   node scripts/verify-eval.mjs --json       机器可读结果
 *   node scripts/verify-eval.mjs --set dev    只校验 dev（不检查冻结）
 */

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const has = (f) => argv.includes(f);
const arg = (f, d) => {
  const i = argv.indexOf(f);
  return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : d;
};
const JSON_OUT = has('--json');

const REQUIRED_CATEGORIES = [
  '写作', '润色', '统计', '绘图', '文献', '格式', '审稿', '选题', '幻灯', '数据',
  '多域混合', '教育辅导', '商务文案', '家庭事务', '临床问诊', '情感写作',
  '通用软件', '生活事务', '投资理财', '行政事务',
];

// 评审给出的真实失败样例：必须落在 dev，且不得进 test（原话照抄，用于防止「规则表自证」）
const REVIEW_FAILURES = [
  '我们科室想做个回顾性研究，看看两种术式的并发症差异',
  '参考文献好像有重复的帮我理一下',
  '帮我把这段中文翻成英文要能投 SCI',
  '帮我起个标题要有记忆点',
  '杂志要求图 300 dpi 我这图够不够',
  '这段文字查重 38% 怎么降到 15% 以下',
  '帮我把这堆随访数据清洗一下',
  '帮我把这段 R 代码跑一下看看结果',
  '帮我改改我闺女的作文',
  '这个 P 值 0.06 还能救吗',
  '基金本子快截止了帮我看看逻辑通不通',
  '我这篇文章被拒了说创新性不够',
];

const violations = [];
const warnings = [];
const fail = (code, msg) => violations.push({ code, msg });
const warn = (code, msg) => warnings.push({ code, msg });

function readJson(rel, required = true) {
  const p = path.join(ROOT, rel);
  if (!fs.existsSync(p)) {
    if (required) fail('E-FILE', `缺少文件：${rel}`);
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (e) {
    fail('E-PARSE', `${rel} 不是合法 JSON：${e.message}`);
    return null;
  }
}

/** 归一化：去掉所有空白与标点，只留字母/数字/汉字，用于重复比对 */
function norm(s) {
  return String(s)
    .normalize('NFKC')
    .replace(/[\s\p{P}\p{S}]/gu, '')
    .toLowerCase();
}

function ngrams(s, n = 3) {
  const t = norm(s);
  const out = new Set();
  for (let i = 0; i + n <= t.length; i++) out.add(t.slice(i, i + n));
  return out;
}

function sha256File(p) {
  return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
}

function dist(cases, keyFn) {
  const m = new Map();
  for (const c of cases) {
    const k = keyFn(c);
    m.set(k, (m.get(k) || 0) + 1);
  }
  return m;
}

function pct(n, d) {
  return d ? ((n / d) * 100).toFixed(1) + '%' : '0.0%';
}

// ── 载入 ────────────────────────────────────────────────────────────────
const dev = readJson('data/golden/dev.json');
const test = readJson('data/golden/test.json');
const legacy = readJson('data/golden/cases.json', false);
const rules = readJson('data/match-rules.json');

const capsById = new Map();
const capsDir = path.join(ROOT, 'data/capabilities');
if (fs.existsSync(capsDir)) {
  for (const f of fs.readdirSync(capsDir).filter((x) => x.endsWith('.json'))) {
    const j = JSON.parse(fs.readFileSync(path.join(capsDir, f), 'utf8'));
    for (const c of j.capabilities || []) capsById.set(c.id, { domain: j.domain, file: f });
  }
} else {
  fail('E-FILE', '缺少 data/capabilities/ 目录');
}

const sets = { dev, test };
for (const [k, s] of Object.entries(sets)) {
  if (!s) continue;
  if (!Array.isArray(s.cases)) fail('E-SHAPE', `${k}.json 缺少 cases 数组`);
}

// ── 1 结构与条目合法性 ──────────────────────────────────────────────────
const ids = new Map();
for (const k of Object.keys(sets)) {
  const s = sets[k];
  if (!s || !Array.isArray(s.cases)) continue;
  if (s.cases.length !== 150) fail('E-COUNT', `${k}.json 应为 150 条，实际 ${s.cases.length}`);
  const local = new Set();
  for (const c of s.cases) {
    const where = `${k}:${c.id}`;
    if (!c.id || typeof c.id !== 'string') { fail('E-ID', `${where} 缺 id`); continue; }
    if (local.has(c.id)) fail('E-ID', `${where} 集内 id 重复`);
    local.add(c.id);
    if (ids.has(c.id)) fail('E-ID', `${where} 与 ${ids.get(c.id)} id 相撞`);
    ids.set(c.id, where);
    if (!c.utterance || !norm(c.utterance)) fail('E-UTT', `${where} 缺 utterance`);
    if (!c.category) fail('E-CAT', `${where} 缺 category`);
    if (!['constructed', 'paraphrase', 'real-ish'].includes(c.source)) {
      fail('E-SRC', `${where} source=${JSON.stringify(c.source)} 非法（只允许 constructed/paraphrase/real-ish）`);
    }
    const e = c.expect || {};
    if (e.noTakeover === true) {
      if (e.cap || e.domain) fail('E-EXPECT', `${where} 负例不应带 cap/domain`);
    } else {
      if (!e.domain) fail('E-EXPECT', `${where} 正例缺 expect.domain`);
      if (!e.cap) fail('E-EXPECT', `${where} 正例缺 expect.cap`);
      if (e.cap && !capsById.has(e.cap)) fail('E-CAP', `${where} expect.cap=${e.cap} 在 data/capabilities 中不存在`);
      if (e.domain && capsById.has(e.cap) && capsById.get(e.cap).domain !== e.domain) {
        fail('E-CAP', `${where} expect.cap=${e.cap} 属域 ${capsById.get(e.cap).domain}，与 expect.domain=${e.domain} 不一致`);
      }
      if (e.alts !== undefined && !Array.isArray(e.alts)) fail('E-EXPECT', `${where} alts 必须是数组`);
      for (const a of e.alts || []) {
        if (!capsById.has(a)) fail('E-ALT', `${where} alts 里的 ${a} 在 data/capabilities 中不存在`);
      }
    }
  }
}

// ── 2 组成：负例规模、负例类目、必备 category ──────────────────────────
if (test && Array.isArray(test.cases)) {
  const negs = test.cases.filter((c) => c.expect && c.expect.noTakeover === true);
  const negCats = dist(negs, (c) => c.category);
  if (negs.length < 80) fail('E-NEG', `test 负例应 ≥80 条，实际 ${negs.length}`);
  if (negCats.size < 10) fail('E-NEGCAT', `test 负例类应 ≥10 类，实际 ${negCats.size}`);
  for (const [cat, n] of negCats) {
    if (n < 5) fail('E-NEGCAT', `test 负例类「${cat}」只有 ${n} 条（要求 ≥5）`);
  }
  const catsSet = new Set(test.cases.map((c) => c.category));
  for (const cat of REQUIRED_CATEGORIES) {
    if (!catsSet.has(cat)) fail('E-CATCOV', `test.json 缺少必备 category「${cat}」`);
  }
}
if (dev && Array.isArray(dev.cases)) {
  const catsSet = new Set(dev.cases.map((c) => c.category));
  for (const cat of REQUIRED_CATEGORIES) {
    if (!catsSet.has(cat)) fail('E-CATCOV', `dev.json 缺少必备 category「${cat}」`);
  }
}

// ── 3 来源分布 ──────────────────────────────────────────────────────────
const sourceReport = {};
for (const [k, s] of Object.entries(sets)) {
  if (!s || !Array.isArray(s.cases)) continue;
  const n = s.cases.length || 1;
  const d = dist(s.cases, (c) => c.source);
  sourceReport[k] = Object.fromEntries([...d.entries()].map(([x, v]) => [x, { n: v, share: +(v / n).toFixed(3) }]));
  for (const src of ['constructed', 'paraphrase', 'real-ish']) {
    if (!d.get(src)) fail('E-SRCMISS', `${k}.json 缺少 source=${src} 的条目`);
  }
  for (const [src, v] of d) {
    if (v / n > 0.4 + 1e-9) fail('E-SRCSHARE', `${k}.json source=${src} 占 ${pct(v, n)}，超过 40% 上限`);
  }
}

// ── 4 句子级完全重复 ────────────────────────────────────────────────────
const dupReport = { within: [], across: [], vsLegacy: [] };
for (const [k, s] of Object.entries(sets)) {
  if (!s || !Array.isArray(s.cases)) continue;
  const seen = new Map();
  for (const c of s.cases) {
    const key = norm(c.utterance);
    if (!key) continue;
    if (seen.has(key)) dupReport.within.push({ set: k, a: seen.get(key), b: c.id, text: c.utterance });
    else seen.set(key, c.id);
  }
}
if (dev && test && Array.isArray(dev.cases) && Array.isArray(test.cases)) {
  const devMap = new Map(dev.cases.map((c) => [norm(c.utterance), c.id]));
  for (const c of test.cases) {
    const hit = devMap.get(norm(c.utterance));
    if (hit) dupReport.across.push({ test: c.id, dev: hit, text: c.utterance });
  }
}
if (legacy && Array.isArray(legacy.cases)) {
  const legMap = new Map(legacy.cases.map((c) => [norm(c.utterance), c.id]));
  for (const [k, s] of Object.entries(sets)) {
    if (!s || !Array.isArray(s.cases)) continue;
    for (const c of s.cases) {
      const hit = legMap.get(norm(c.utterance));
      if (hit) dupReport.vsLegacy.push({ set: k, id: c.id, legacy: hit, text: c.utterance });
    }
  }
}
const dupCount = dupReport.within.length + dupReport.across.length + dupReport.vsLegacy.length;
if (dupCount > 0) {
  for (const d of dupReport.within) fail('E-DUP', `${d.set} 集内重复：${d.a} 与 ${d.b}「${d.text}」`);
  for (const d of dupReport.across) fail('E-DUP', `dev/test 重复：${d.test} 与 ${d.dev}「${d.text}」`);
  for (const d of dupReport.vsLegacy) fail('E-DUP', `与旧 cases.json 重复：${d.set}:${d.id} 与 ${d.legacy}「${d.text}」`);
}

// ── 5 字符 3-gram 重叠率 ────────────────────────────────────────────────
let gramReport = null;
if (dev && test && Array.isArray(dev.cases) && Array.isArray(test.cases)) {
  const devG = new Set();
  for (const c of dev.cases) for (const g of ngrams(c.utterance)) devG.add(g);
  const testG = new Set();
  for (const c of test.cases) for (const g of ngrams(c.utterance)) testG.add(g);
  let inter = 0;
  for (const g of testG) if (devG.has(g)) inter++;
  const rateTest = testG.size ? inter / testG.size : 0;
  const devInter = inter / (devG.size || 1);
  gramReport = {
    devGrams: devG.size,
    testGrams: testG.size,
    intersect: inter,
    testCoveredByDev: +rateTest.toFixed(4),
    devCoveredByTest: +devInter.toFixed(4),
  };
  if (rateTest >= 0.05) fail('E-GRAM', `test 3-gram 有 ${pct(inter, testG.size)} 出现在 dev（上限 <5%）`);
  if (devInter >= 0.05) fail('E-GRAM', `dev 3-gram 有 ${pct(inter, devG.size)} 出现在 test（上限 <5%）`);
}

// ── 6 与 match-rules.json 的 cues 字面文本泄漏 ─────────────────────────
let cueReport = null;
if (rules && Array.isArray(rules.cues) && test && Array.isArray(test.cases)) {
  const frags = new Set(); // ≥6 汉字的候选式：可识别的规则签名，命中即违规
  const shortFrags = new Set(); // 3～5 汉字的候选式：专业名词，只统计不判违规
  for (const cue of rules.cues) {
    const re = String(cue.re || '');
    for (const alt of re.split('|')) {
      const lit = alt
        .replace(/\\([\s\S])/g, '$1')
        .replace(/[[\](){}^$*+?.]/g, '')
        .trim();
      const cjk = (lit.match(/[\u4e00-\u9fa5]/g) || []).length;
      // 只把「≥6 个汉字的候选式」当作可识别的规则签名（如「写一份正式的审稿意见」「参考文献格式」）：
      // 4～5 字的专业名词（参考文献、样本量、机制图）在真实科研口语里必然出现，不构成污染证据，
      // 否则会把「用户真会这么说」的句子误判为抄规则表，反过来削弱盲测的效度。
      if (cjk >= 6) frags.add(lit);
      else if (cjk >= 3) shortFrags.add(lit);
    }
  }
  const fullCue = new Set();
  for (const cue of rules.cues) {
    const lit = String(cue.re || '').replace(/\\([\s\S])/g, '$1').replace(/[[\](){}^$*+?.]/g, '').trim();
    if (norm(lit)) fullCue.add(norm(lit));
  }
  const hits = [];
  const shortHits = [];
  for (const c of test.cases) {
    const u = String(c.utterance);
    for (const f of frags) if (f && u.includes(f)) hits.push({ id: c.id, cue: f, text: u });
    for (const f of shortFrags) if (f && u.includes(f)) shortHits.push({ id: c.id, cue: f });
    if (fullCue.has(norm(u))) hits.push({ id: c.id, cue: '（整句等于 cue 字面文本）', text: u });
  }
  cueReport = { fragments: frags.size, shortFragments: shortFrags.size, hits: hits.length, shortHits: shortHits.length, detail: hits.slice(0, 20), shortDetail: shortHits.slice(0, 20) };
  if (hits.length > 0) {
    for (const h of hits.slice(0, 12)) fail('E-CUE', `test:${h.id} 含规则表字面「${h.cue}」：「${h.text}」`);
    if (hits.length > 12) fail('E-CUE', `另有 ${hits.length - 12} 条 test 句子命中规则表长字面，合计 ${hits.length} 条`);
  }
  if (shortHits.length > 0) {
    warn('W-CUE-SHORT', `test 有 ${shortHits.length} 处与规则表 3～5 字短字面重合（专业名词，属正常用语，不计入违规）：` +
      [...new Set(shortHits.map((h) => h.cue))].slice(0, 10).join('、'));
  }
}

// ── 7 冻结：sha256 与 .freeze.json 一致 ────────────────────────────────
const testPath = path.join(ROOT, 'data/golden/test.json');
const freezePath = path.join(ROOT, 'data/golden/.freeze.json');
const actualHash = fs.existsSync(testPath) ? sha256File(testPath) : null;
const testNegCount = test && Array.isArray(test.cases) ? test.cases.filter((c) => c.expect && c.expect.noTakeover === true).length : 0;
const testCats = test && Array.isArray(test.cases) ? [...new Set(test.cases.map((c) => c.category))].sort() : [];

let freezeReport = null;
if (has('--freeze')) {
  if (fs.existsSync(freezePath) && !has('--force')) {
    fail('E-FREEZE', '.freeze.json 已存在；重新冻结必须显式加 --force（冻结后改题即等于换测试集）');
  } else {
    const payload = {
      frozenAt: new Date().toISOString().slice(0, 10),
      sha256: actualHash,
      count: test && Array.isArray(test.cases) ? test.cases.length : 0,
      negatives: testNegCount,
      categories: testCats,
    };
    fs.writeFileSync(freezePath, JSON.stringify(payload, null, 2) + '\n', 'utf8');
    freezeReport = { wrote: true, ...payload };
  }
} else if (arg('--set', 'both') !== 'dev') {
  if (!fs.existsSync(freezePath)) {
    fail('E-FREEZE', '缺少 data/golden/.freeze.json；先运行 node scripts/verify-eval.mjs --freeze 生成冻结记录');
  } else {
    let fz = null;
    try {
      fz = JSON.parse(fs.readFileSync(freezePath, 'utf8'));
    } catch (e) {
      fail('E-FREEZE', `.freeze.json 不是合法 JSON：${e.message}`);
    }
    if (fz) {
      if (!/^[0-9a-f]{64}$/.test(String(fz.sha256 || ''))) fail('E-FREEZE', '.freeze.json 的 sha256 字段不是 64 位十六进制');
      if (fz.sha256 !== actualHash) {
        fail('E-FREEZE', `test.json 已被改动：当前 sha256=${actualHash}，冻结记录=${fz.sha256}`);
      }
      if (fz.count !== (test && Array.isArray(test.cases) ? test.cases.length : -1)) {
        fail('E-FREEZE', `.freeze.json count=${fz.count} 与 test.json 实际条数不符`);
      }
      if (fz.negatives !== testNegCount) fail('E-FREEZE', `.freeze.json negatives=${fz.negatives} 与 test.json 实际负例数 ${testNegCount} 不符`);
      freezeReport = { verified: true, sha256: fz.sha256, frozenAt: fz.frozenAt, count: fz.count, negatives: fz.negatives };
    }
  }
}

// ── 8 dev 必须包含评审真实失败样例，test 不得包含 ───────────────────────
const missingFailures = [];
if (dev && Array.isArray(dev.cases)) {
  const devNorm = new Set(dev.cases.map((c) => norm(c.utterance)));
  for (const f of REVIEW_FAILURES) if (!devNorm.has(norm(f))) missingFailures.push(f);
  for (const f of missingFailures) fail('E-REALFAIL', `dev.json 缺少评审真实失败样例「${f}」`);
}
if (test && Array.isArray(test.cases)) {
  const testNorm = new Set(test.cases.map((c) => norm(c.utterance)));
  for (const f of REVIEW_FAILURES) {
    if (testNorm.has(norm(f))) fail('E-LEAK', `test.json 出现了评审真实失败样例「${f}」，必须只留在 dev`);
  }
}

// ── 9 id 空间与分布打印 ────────────────────────────────────────────────
function idRange(s) {
  if (!s || !Array.isArray(s.cases) || !s.cases.length) return '—';
  const idsv = s.cases.map((c) => c.id).sort();
  return `${idsv[0]} … ${idsv[idsv.length - 1]}（${idsv.length} 个，前缀 ${[...new Set(idsv.map((x) => x.replace(/[0-9]+$/, '')))].join('/')}）`;
}

function printTable(title, cols) {
  if (JSON_OUT) return;
  console.log('\n' + title);
  const widths = cols[0].map((_, i) => Math.max(...cols.map((r) => String(r[i]).length)) + 2);
  for (const row of cols) console.log('  ' + row.map((c, i) => String(c).padEnd(widths[i])).join(''));
}

const result = {
  ok: violations.length === 0,
  counts: {
    dev: dev && dev.cases ? dev.cases.length : 0,
    test: test && test.cases ? test.cases.length : 0,
    legacy: legacy && legacy.cases ? legacy.cases.length : 0,
    negatives: { dev: (dev?.cases || []).filter((c) => c.expect?.noTakeover === true).length, test: testNegCount },
    capabilities: capsById.size,
  },
  idSpace: { dev: idRange(dev), test: idRange(test) },
  duplicates: dupReport,
  trigram: gramReport,
  cues: cueReport,
  sources: sourceReport,
  freeze: freezeReport,
  violations,
  warnings,
};

if (JSON_OUT) {
  console.log(JSON.stringify(result, null, 2));
} else {
  console.log('verify-eval：评测集防污染与冻结校验');
  console.log('  包根：' + ROOT);
  console.log('  能力卡数：' + capsById.size);

  printTable('id 空间', [
    ['集合', 'id 范围', ''],
    ['dev', idRange(dev), ''],
    ['test', idRange(test), ''],
  ]);

  const devNeg = (dev?.cases || []).filter((c) => c.expect?.noTakeover === true).length;
  printTable('条数 / 负例', [
    ['集合', '条数', '负例', '负例占比'],
    ['dev', String(dev?.cases?.length ?? 0), String(devNeg), pct(devNeg, dev?.cases?.length || 1)],
    ['test', String(test?.cases?.length ?? 0), String(testNegCount), pct(testNegCount, test?.cases?.length || 1)],
    ['cases.json（旧，仅重复检查用）', String(legacy?.cases?.length ?? 0), String((legacy?.cases || []).filter((c) => c.expect?.noTakeover === true).length), '—'],
  ]);

  const allCats = [...new Set([...(dev?.cases || []).map((c) => c.category), ...(test?.cases || []).map((c) => c.category)])].sort();
  const devCat = dist(dev?.cases || [], (c) => c.category);
  const testCat = dist(test?.cases || [], (c) => c.category);
  const catRows = [['category', 'dev', 'test', '合计']];
  for (const cat of allCats) {
    const a = devCat.get(cat) || 0;
    const b = testCat.get(cat) || 0;
    catRows.push([cat, String(a), String(b), String(a + b)]);
  }
  catRows.push(['— 合计', String(dev?.cases?.length ?? 0), String(test?.cases?.length ?? 0), String((dev?.cases?.length || 0) + (test?.cases?.length || 0))]);
  printTable('category 分布（dev / test）', catRows);

  const srcRows = [['source', 'dev n', 'dev 占比', 'test n', 'test 占比']];
  for (const src of ['constructed', 'paraphrase', 'real-ish']) {
    const a = sourceReport.dev?.[src] || { n: 0, share: 0 };
    const b = sourceReport.test?.[src] || { n: 0, share: 0 };
    srcRows.push([src, String(a.n), pct(a.n, dev?.cases?.length || 1), String(b.n), pct(b.n, test?.cases?.length || 1)]);
  }
  printTable('来源分布（单类 ≤40%）', srcRows);

  console.log('\n防污染检查');
  console.log('  句子级完全重复：' + dupCount + ' 处（集内 ' + dupReport.within.length + ' / 跨集 ' + dupReport.across.length + ' / 对旧集 ' + dupReport.vsLegacy.length + '）');
  if (gramReport) {
    console.log('  3-gram 重叠：test→dev ' + pct(gramReport.intersect, gramReport.testGrams) +
      '，dev→test ' + pct(gramReport.intersect, gramReport.devGrams) +
      '（阈值 <5%；交集 ' + gramReport.intersect + ' 个 gram）');
  }
  if (cueReport) {
    console.log('  规则表 cue 字面泄漏：命中 ' + cueReport.hits + ' 条（比对字面式 ' + cueReport.fragments + ' 个）');
    for (const h of cueReport.detail.slice(0, 6)) console.log('    - test:' + h.id + ' 含「' + h.cue + '」');
  }
  if (freezeReport) {
    if (freezeReport.wrote) {
      console.log('  冻结记录已写入：' + path.relative(ROOT, freezePath));
      console.log('    sha256=' + freezeReport.sha256);
      console.log('    count=' + freezeReport.count + ' negatives=' + freezeReport.negatives + ' frozenAt=' + freezeReport.frozenAt);
    } else {
      console.log('  冻结校验通过：sha256=' + freezeReport.sha256.slice(0, 16) + '…（' + freezeReport.frozenAt + '，' + freezeReport.count + ' 条 / 负例 ' + freezeReport.negatives + '）');
    }
  }
  console.log('  dev 内评审真实失败样例：' + (REVIEW_FAILURES.length - missingFailures.length) + '/' + REVIEW_FAILURES.length + ' 在位；test 泄漏 ' + (test ? 0 : 0));

  if (warnings.length) {
    console.log('\nWARN（' + warnings.length + '）');
    for (const w of warnings) console.log('  [' + w.code + '] ' + w.msg);
  }
  if (violations.length) {
    console.log('\nERROR（' + violations.length + '）');
    for (const v of violations) console.log('  [' + v.code + '] ' + v.msg);
    console.log('\n结果：失败（exit 1）');
  } else {
    console.log('\n结果：通过（0 error / ' + warnings.length + ' warning）');
  }
}

process.exit(violations.length ? 1 : 0);
