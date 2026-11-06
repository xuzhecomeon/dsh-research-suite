// 生成 toolbox 域的判定账本：toolbox 是索引桶，不建能力卡，全部 index-only。
// 用法：node tools/make-toolbox-ledger.mjs
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(dirname(fileURLToPath(import.meta.url)));
const catalog = JSON.parse(readFileSync(join(HERE, 'knowledge', 'catalog.json'), 'utf8'));
const items = Array.isArray(catalog) ? catalog : catalog.items || catalog.skills || [];

const tb = items.filter((it) => (it.domain || '') === 'toolbox');
if (!tb.length) {
  console.error('catalog 里没有 domain=toolbox 的条目');
  process.exit(1);
}

const SOFT = new Set(['通用软件工程', '社交通讯', '商业运营', '素材创作', '金融交易']);
function why(it) {
  const cat = it.category || '通用';
  const base = SOFT.has(cat)
    ? `非科研主线（${cat}），仅作索引备用`
    : `与科研写作无直接关系（${cat}），仅在 research_catalog 按需借用`;
  if (it.name && it.name.toLowerCase().startsWith('airs-')) return `airs 工具族成员，${cat}类，仅索引备用`;
  return base;
}

const entries = tb.map((it) => ({ dir: it.dir, name: it.name, verdict: 'index-only', why: why(it) }));

const out = {
  domain: 'toolbox',
  version: '3.0.0',
  sourceTotal: entries.length,
  note: 'toolbox 是索引桶：收 233 个与科研写作无直接关系但可能被借用的技能（科学计算库、ML 工程、airs 工具族、通用办公等），不建能力卡，只进账本以便 research_catalog 检索。',
  entries,
};

mkdirSync(join(HERE, 'data', 'ledger'), { recursive: true });
const file = join(HERE, 'data', 'ledger', 'toolbox.json');
writeFileSync(file, JSON.stringify(out, null, 2) + '\n', 'utf8');
console.log(`已写 ${file}：${entries.length} 条 index-only`);
