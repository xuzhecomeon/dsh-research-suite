// 生成 knowledge/INDEX.md（v3）：全量技能索引 + 能力卡覆盖标记
// 用法：node scripts/build-index.mjs [包根，默认当前目录]
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const root = process.argv[2] ?? '.';
const catalog = JSON.parse(readFileSync(join(root, 'knowledge/catalog.json'), 'utf8'));
const caps = [];
for (const f of readdirSync(join(root, 'data/capabilities')).filter((x) => x.endsWith('.json')).sort()) {
	const j = JSON.parse(readFileSync(join(root, 'data/capabilities', f), 'utf8'));
	const dom = f.replace(/\.json$/, '');
	for (const c of j.capabilities ?? []) caps.push({ ...c, domain: dom });
}

const refs = new Map();
for (const c of caps) {
	for (const m of c.members ?? []) {
		const role = m.role ?? 'member';
		const list = refs.get(m.skill) ?? [];
		list.push(`${c.id}(${role})`);
		refs.set(m.skill, list);
	}
}

const DOMAIN_LABEL = {
	writing: '论文撰写',
	polish: '润色与去 AI 痕迹',
	figures: '科研绘图',
	stats: '科研统计',
	ideation: '科研思路与标书',
	review: '审稿与修回',
	slides: '科研汇报与 PPT',
	literature: '文献与引文',
	format: '格式与交付',
	data: '数据获取与组学',
	toolbox: '工具箱（索引桶，不建能力卡）',
	general: '通用（不进融合，仅编目）',
};
const ORDER = [...Object.keys(DOMAIN_LABEL)];
const byDomain = new Map();
for (const item of catalog) {
	const d = ORDER.includes(item.domain) ? item.domain : 'general';
	if (!byDomain.has(d)) byDomain.set(d, []);
	byDomain.get(d).push(item);
}

const lines = [];
lines.push('# 技能索引（全量编目）');
lines.push('');
lines.push('本文件由 `scripts/build-index.mjs` 从 `knowledge/catalog.json` 与 `data/capabilities/*.json` 生成，');
lines.push('是**目录层**的索引：告诉你包里到底有哪些技能、每题正文在哪、被哪张能力卡引用。');
lines.push('');
lines.push('- 想知道“这个任务该怎么做”：走 `research_playbook`，看**能力卡**，不要在本索引里挑技能。');
lines.push('- 想知道某个技能原文：`research_kb_read(name=\"<技能名>\")`，按 `file` 列的相对路径读取。');
lines.push('- 本索引只在“同名近似技能到底哪个更全”这类**证据等级**问题上使用。');
lines.push('');
const total = catalog.length;
const researchCount = catalog.filter((x) => x.research).length;
const dirs = new Set(catalog.map((x) => x.dir));
const dupNote = dirs.size === total ? '' : `（去重后 ${dirs.size} 个技能目录：6 组同目录重复记录各计一条）`;
lines.push(`合计 ${total} 条源记录${dupNote}，科研相关 ${researchCount} 条，分布在 ${ORDER.length - 2} 个能力域 + 1 个工具箱索引桶；`);
lines.push(`被能力卡引用 ${refs.size} 个，其余仅编目留档。`);
lines.push('');
lines.push('## 域目录');
lines.push('');
lines.push('| 域 | 技能数 | 科研相关 | 被能力卡引用 | 对应技能文件 |');
lines.push('|---|---:|---:|---:|---|');
const SKILL_FILE = {
	writing: 'research-writing',
	polish: 'research-polish',
	figures: 'research-figures',
	stats: 'research-stats',
	ideation: 'research-ideation',
	review: 'research-review',
	slides: 'research-slides',
	literature: 'research-literature',
	format: 'research-format',
	data: 'research-data',
};
for (const d of ORDER) {
	const items = byDomain.get(d) ?? [];
	if (!items.length) continue;
	const r = items.filter((x) => x.research).length;
	const c = items.filter((x) => refs.has(x.name) || refs.has(x.slug)).length;
	lines.push(`| ${DOMAIN_LABEL[d]} | ${items.length} | ${r} | ${c} | ${SKILL_FILE[d] ? `\`skills/${SKILL_FILE[d]}.md\`` : '—'} |`);
}
lines.push('');
for (const d of ORDER) {
	const items = (byDomain.get(d) ?? []).slice().sort((a, b) => a.name.localeCompare(b.name));
	if (!items.length) continue;
	lines.push(`## ${DOMAIN_LABEL[d]}（${items.length}）`);
	lines.push('');
	lines.push('| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |');
	lines.push('|---|---:|:--:|---|---|');
	for (const it of items) {
		const used = (refs.get(it.name) ?? refs.get(it.slug) ?? []).join('、') || '—';
		const desc = (it.description ?? '').replace(/\s+/g, ' ').trim();
		lines.push(`| \`${it.name}\` | ${(it.bytes / 1024).toFixed(1)}K | ${it.research ? '✓' : ''} | ${used} | \`${it.file}\` |`);
		if (desc) lines.push(`| ↳ | | | | ${desc.slice(0, 140)}${desc.length > 140 ? '…' : ''} |`);
	}
	lines.push('');
}
const out = join(root, 'knowledge/INDEX.md');
writeFileSync(out, lines.join('\n'), 'utf8');
console.log(`INDEX.md: ${lines.length} 行 / ${Buffer.byteLength(lines.join('\n'), 'utf8')} 字节；域 ${ORDER.length}，技能 ${total}，被引用 ${refs.size}`);
const unused = caps.flatMap((c) => (c.members ?? []).map((m) => m.skill)).filter((s) => !catalog.some((i) => i.name === s || i.slug === s));
console.log('能力卡引用但 catalog 里没有的技能：', unused.length ? unused.join(', ') : '无');
