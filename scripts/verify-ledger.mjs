// 账本校验：证明「每一个源技能都被判定过」，且 fused 的判定能在能力卡里核到。
// 用法：node scripts/verify-ledger.mjs <domain|all> [--root=<插件根>] [--src=<源清单根>]
//
// 数据源优先级：
//   1) 默认只用包内 knowledge/catalog.json —— CI（GitHub Actions）上不存在本地分析目录，必须可移植。
//   2) --src=<目录> 时改用 <目录>/analysis/domains/<domain>.json 作为源清单（仅供本地核对构建输入，CI 不传）。
//
// 账本契约（data/ledger/<domain>.json）：
//   { domain, version?, entries: [ { dir, name?, verdict, why, cards?[] } ] }
//   - dir     = knowledge/catalog.json 里的 dir（该域每条源技能一条，唯一）
//   - verdict = fused | index-only | deprecated | out-of-scope
//   - why     = 判定理由，至少 4 字
//   - cards   = verdict=fused 时必填：融入的能力卡 id 列表，且该卡 members[].skill 必须含本技能 name
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = process.argv.slice(2);
const target = (args.find((a) => !a.startsWith('--')) || 'all').trim();
const rootArg = args.find((a) => a.startsWith('--root='));
const srcArg = args.find((a) => a.startsWith('--src='));
const ROOT = rootArg ? path.resolve(rootArg.slice(7)) : HERE;
const SRC = srcArg ? path.resolve(srcArg.slice(6)) : null;

const DOMAINS = ['writing', 'polish', 'figures', 'stats', 'ideation', 'review', 'slides', 'literature', 'format', 'data', 'toolbox'];
const VERDICTS = new Set(['fused', 'index-only', 'deprecated', 'out-of-scope']);

const errors = [];
const warnings = [];
const rows = [];

function readJson(file, label) {
  if (!fs.existsSync(file)) return null;
  const raw = fs.readFileSync(file, 'utf8');
  const clean = raw.charCodeAt(0) === 0xfeff ? raw.slice(1) : raw;
  try { return JSON.parse(clean); } catch (e) { errors.push(`${label}: JSON 解析失败 ${e.message}`); return null; }
}

// 源清单：默认从包内 catalog 汇总；给了 --src 才回落到本地分析目录
const catalog = readJson(path.join(ROOT, 'knowledge', 'catalog.json'), 'knowledge/catalog.json');
if (!catalog || !Array.isArray(catalog)) {
  console.error('ERROR 读不到 knowledge/catalog.json（账本校验的源清单只能来自包内）');
  process.exit(1);
}
const catalogByDomain = new Map();
const byDir = new Map();
for (const c of catalog) {
  if (!c || typeof c.dir !== 'string') continue;
  byDir.set(c.dir, c);
  if (!catalogByDomain.has(c.domain)) catalogByDomain.set(c.domain, []);
  catalogByDomain.get(c.domain).push(c);
}

function domainSource(domain) {
  const local = catalogByDomain.get(domain) || [];
  if (!SRC) {
    if (!local.length) errors.push(`${domain}: knowledge/catalog.json 里没有该域的技能`);
    return { dirs: local.map((c) => c.dir), names: new Map(local.map((c) => [c.dir, c.name])) };
  }
  const f = path.join(SRC, 'analysis', 'domains', `${domain}.json`);
  if (!fs.existsSync(f)) { errors.push(`缺少源清单 ${f}`); return null; }
  const data = JSON.parse(fs.readFileSync(f, 'utf8'));
  const list = Array.isArray(data) ? data : data.skills || [];
  const dirSet = new Set(local.map((c) => c.dir));
  for (const s of list) {
    if (!dirSet.has(s.dir)) warnings.push(`${domain}: 源清单里的 ${s.dir} 不在 catalog 该域列表里（清单与包内数据不同步）`);
  }
  return { dirs: list.map((s) => s.dir), names: new Map(local.map((c) => [c.dir, c.name])) };
}

for (const domain of DOMAINS) {
  if (target !== 'all' && target !== domain) continue;

  const src = domainSource(domain);
  if (!src) continue;
  const srcDirs = src.dirs;
  const srcSet = new Set(srcDirs);

  const ledger = readJson(path.join(ROOT, 'data', 'ledger', `${domain}.json`), `ledger/${domain}.json`);
  if (!ledger) { errors.push(`账本缺失：data/ledger/${domain}.json`); continue; }

  if (ledger.domain && ledger.domain !== domain) {
    errors.push(`ledger/${domain}.json: 顶层 domain 是「${ledger.domain}」，与文件名不一致`);
  }

  // 能力卡索引：toolbox 只进 catalog、没有能力卡，其余域必须有
  const caps = readJson(path.join(ROOT, 'data', 'capabilities', `${domain}.json`), `capabilities/${domain}.json`);
  const capIndex = new Map();
  let capCount = 0;
  if (caps && Array.isArray(caps.capabilities)) {
    capCount = caps.capabilities.length;
    for (const cap of caps.capabilities) capIndex.set(cap.id, cap);
  } else if (domain !== 'toolbox') {
    errors.push(`capabilities/${domain}.json 缺失或没有 capabilities 数组（fused 判定无从核对）`);
  }

  const entries = Array.isArray(ledger.entries) ? ledger.entries : null;
  if (!entries) { errors.push(`ledger/${domain}.json: 缺 entries 数组`); continue; }

  const seen = new Map();
  for (const e of entries) {
    if (!e || typeof e !== 'object') { errors.push(`${domain}: 存在非对象条目`); continue; }
    let dir = typeof e.dir === 'string' ? e.dir.trim() : '';
    const declared = typeof e.name === 'string' ? e.name.trim() : '';
    if (!dir && declared) {
      // 容忍只写 name 的账本：用 catalog 反查 dir
      const hit = (catalogByDomain.get(domain) || []).find((c) => c.name === declared);
      if (hit) dir = hit.dir;
    }
    if (!dir) { errors.push(`${domain}: 存在没有 dir/name 的条目`); continue; }
    if (seen.has(dir)) { errors.push(`${domain}: dir 重复 ${dir}`); continue; }
    seen.set(dir, e);

    if (!srcSet.has(dir)) {
      errors.push(`${domain}: 账本条目 ${dir} 不属于本域源技能（多写或串域）`);
    }

    const verdict = e.verdict;
    if (!VERDICTS.has(verdict)) {
      errors.push(`${domain}: ${dir} 的 verdict 非法「${verdict}」（只能是 ${[...VERDICTS].join('/')}）`);
      continue;
    }
    if (!e.why || String(e.why).trim().length < 4) errors.push(`${domain}: ${dir} 缺 why（判定理由至少 4 字）`);

    const cards = Array.isArray(e.cards) ? e.cards : [];
    if (verdict === 'fused') {
      if (cards.length === 0) errors.push(`${domain}: ${dir} 判为 fused 但没写 cards`);
      const name = declared || (byDir.get(dir) || {}).name || '';
      for (const id of cards) {
        const cap = capIndex.get(id);
        if (!cap) { errors.push(`${domain}: ${dir} 引用的能力卡不存在 ${id}`); continue; }
        const inCap = (cap.members || []).some((m) => m.skill === name);
        if (!inCap) errors.push(`${domain}: ${dir}（${name}）声称融进 ${id}，但该卡 members[].skill 里没有它`);
      }
    } else if (cards.length > 0) {
      warnings.push(`${domain}: ${dir} 判为 ${verdict} 却写了 cards（${cards.join(',')}）`);
    }
  }

  const missing = srcDirs.filter((d) => !seen.has(d));
  const extra = [...seen.keys()].filter((d) => !srcSet.has(d));
  if (missing.length) errors.push(`${domain}: 有 ${missing.length} 个源技能未进账本 → ${missing.slice(0, 6).join(', ')}${missing.length > 6 ? ' …' : ''}`);
  if (extra.length) errors.push(`${domain}: 账本里有 ${extra.length} 个不属于本域源清单的 dir → ${extra.slice(0, 6).join(', ')}`);

  const byVerdict = {};
  for (const e of entries) byVerdict[e.verdict] = (byVerdict[e.verdict] || 0) + 1;
  rows.push({ domain, src: srcDirs.length, ledger: entries.length, ...byVerdict, cards: capCount });
}

const pad = (s, n) => String(s).padEnd(n);
let totalEntries = 0;
if (rows.length) {
  console.log(pad('domain', 12), pad('src', 5), pad('ledger', 7), pad('fused', 6), pad('index', 6), pad('depr', 6), pad('oosc', 6), 'cards');
  for (const r of rows) {
    totalEntries += r.ledger;
    console.log(
      pad(r.domain, 12), pad(r.src, 5), pad(r.ledger, 7),
      pad(r.fused ?? 0, 6), pad(r['index-only'] ?? 0, 6), pad(r.deprecated ?? 0, 6), pad(r['out-of-scope'] ?? 0, 6), r.cards,
    );
  }
  console.log('');
}
for (const w of warnings) console.log('WARN ', w);
for (const e of errors) console.log('ERROR', e);
console.log('');
console.log(`verify-ledger ${target}：${rows.length} domains, ${totalEntries} entries, ${errors.length} errors, ${warnings.length} warnings`);
process.exit(errors.length ? 1 : 0);
