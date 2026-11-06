/**
 * dsh-research-suite v3 · core
 *
 * 负责三件事，全部零宿主依赖（只用 node:fs / node:path）：
 *   1) 打开插件自带的知识层：592 个源技能索引（含兄弟资产）、10 个能力域能力卡 + toolbox 索引桶、references 规范、门禁数据。
 *   2) 能力匹配：把用户原话映射到「能力卡」（不是映射到某个技能）。
 *   3) 安全读取与机械自检：越界路径拒绝；标点/引用/套话/单位等可机械判定的问题直接给计数。
 */

import fs from 'node:fs';
import path from 'node:path';

const SKILL_FILE_RE = /^\d\d_.*\.md$/;
const CJK_RE = /[\u3400-\u9fff]/;

function readJson(file) {
  // 容忍 BOM：队友/编辑器保存的 JSON 常带 U+FEFF，JSON.parse 会直接抛错。
  const raw = fs.readFileSync(file, 'utf8');
  return JSON.parse(raw.charCodeAt(0) === 0xfeff ? raw.slice(1) : raw);
}

function isDir(p) {
  try {
    return fs.statSync(p).isDirectory();
  } catch {
    return false;
  }
}

function listMarkdown(dir) {
  if (!isDir(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((n) => n.endsWith('.md'))
    .sort();
}

function firstHeading(file) {
  try {
    const text = fs.readFileSync(file, 'utf8');
    const m = text.match(/^#\s+(.+)$/m);
    return m ? m[1].trim() : path.basename(file, '.md');
  } catch {
    return path.basename(file, '.md');
  }
}

/** 中文按二元组切、英文按词切，得到用于粗匹配的 token 集。 */
export function tokenize(text) {
  const out = new Set();
  const lower = String(text ?? '').toLowerCase();
  for (const m of lower.matchAll(/[a-z][a-z0-9+#.-]{1,}/g)) {
    if (m[0].length >= 2) out.add(m[0]);
  }
  for (const seg of lower.split(/[^\u3400-\u9fff]+/)) {
    if (!seg) continue;
    if (seg.length === 1) continue;
    for (let i = 0; i + 2 <= seg.length; i++) out.add(seg.slice(i, i + 2));
  }
  return out;
}

function overlap(tokens, text) {
  if (!tokens.size) return 0;
  const hay = String(text ?? '').toLowerCase();
  let hit = 0;
  for (const t of tokens) if (hay.includes(t)) hit++;
  return hit;
}

/** 中文语境里的半角标点、套话、绝对化措辞、单位空格、文言虚词等可机械判定的清单。 */
const AI_PHRASES = [
  '值得注意的是', '综上所述', '总而言之', '众所周知', '毋庸置疑', '不言而喻',
  '至关重要', '举足轻重', '日益凸显', '不断深入', '蓬勃发展', '方兴未艾',
  '不仅……而且', '在当今社会', '随着……的发展', '具有重要的现实意义',
  '为……提供了新的思路', '奠定了坚实的基础', '发挥着不可替代的作用',
];

const ABSOLUTE_WORDS = ['首次', '从未', '完全', '必然', '彻底', '唯一', '绝对', '无可争议', '最高', '最优'];

const CLASSICAL_WORDS = ['盖', '然则', '亦', '所谓', '之于', '之谓', '岂', '矣', '焉'];

const HALF_WIDTH = [',', '.', ';', ':', '?', '!', '(', ')', '"'];

function nearbyCjk(text, i) {
  const prev = text[i - 1] ?? '';
  const next = text[i + 1] ?? '';
  return CJK_RE.test(prev) || CJK_RE.test(next);
}

function lineOf(text, index) {
  let line = 1;
  for (let i = 0; i < index && i < text.length; i++) if (text[i] === '\n') line++;
  return line;
}

/**
 * 机械检查：只报「能用规则判定」的问题，判不了的（逻辑、证据、创新性）不在这里冒充判断。
 * 返回 { counts, findings[] }，findings 每条形如 { rule, line, snippet, hint }
 */
export function checkText(text) {
  const findings = [];
  const src = String(text ?? '');

  for (let i = 0; i < src.length; i++) {
    const ch = src[i];
    if (!HALF_WIDTH.includes(ch)) continue;
    if (ch === '(' || ch === ')') {
      if (nearbyCjk(src, i)) {
        findings.push({ rule: '半角括号', line: lineOf(src, i), snippet: src.slice(Math.max(0, i - 8), i + 8), hint: '中文语境改用全角（）' });
      }
      continue;
    }
    if (ch === '"') {
      if (nearbyCjk(src, i)) {
        findings.push({ rule: '半角直引号', line: lineOf(src, i), snippet: src.slice(Math.max(0, i - 8), i + 8), hint: '改用「」或全角引号' });
      }
      continue;
    }
    if (nearbyCjk(src, i)) {
      findings.push({ rule: '半角标点', line: lineOf(src, i), snippet: src.slice(Math.max(0, i - 8), i + 8), hint: '中文语境改用全角标点' });
    }
  }

  for (const p of AI_PHRASES) {
    let idx = src.indexOf(p);
    while (idx >= 0) {
      findings.push({ rule: 'AI 套话', line: lineOf(src, idx), snippet: p, hint: '删掉或换成具体陈述' });
      idx = src.indexOf(p, idx + p.length);
    }
  }

  for (const w of ABSOLUTE_WORDS) {
    let idx = src.indexOf(w);
    while (idx >= 0) {
      findings.push({ rule: '绝对化措辞', line: lineOf(src, idx), snippet: src.slice(Math.max(0, idx - 10), idx + 10), hint: '改为可证伪的限定表述' });
      idx = src.indexOf(w, idx + w.length);
    }
  }

  for (const w of CLASSICAL_WORDS) {
    let idx = src.indexOf(w);
    while (idx >= 0) {
      findings.push({ rule: '文言虚词', line: lineOf(src, idx), snippet: src.slice(Math.max(0, idx - 8), idx + 8), hint: '学术书面语禁用文言腔' });
      idx = src.indexOf(w, idx + w.length);
    }
  }

  const plainCites = [...src.matchAll(/\[\d+(?:[-,]\d+)*\]/g)].map((m) => m[0]);
  if (plainCites.length) {
    findings.push({
      rule: '引用编号上标待确认',
      line: 0,
      snippet: plainCites.slice(0, 10).join(' '),
      hint: `纯文本无法判断是否上标；中文期刊要求 ${plainCites.length} 处编号为上标，交付前逐处确认`,
    });
  }

  const unitMiss = src.match(/(?<=\d)(?:mg|ml|mL|kg|cm|mm|min|mmHg|mol|mmol|μg|ng|IU)(?![a-zA-Z])/g);
  if (unitMiss) {
    findings.push({ rule: '数值与单位缺空格', line: 0, snippet: [...new Set(unitMiss)].slice(0, 10).join(' '), hint: '写作 5 mg/kg、37 ℃' });
  }

  const counts = {};
  for (const f of findings) counts[f.rule] = (counts[f.rule] ?? 0) + 1;
  return { counts, findings, total: findings.length };
}

export function createCore(pluginRoot, options = {}) {
  const knowledgeDir = path.join(pluginRoot, 'knowledge');
  const dataDir = path.join(pluginRoot, 'data');
  const refsDir = path.join(pluginRoot, 'references');
  const skillsDir = path.join(pluginRoot, 'skills');
  const capsDir = path.join(dataDir, 'capabilities');

  const catalog = readJson(path.join(knowledgeDir, 'catalog.json'));
  const byName = new Map();
  const bySlug = new Map();
  const nameGroups = new Map();
  for (const item of catalog) {
    if (item.slug && !bySlug.has(item.slug)) bySlug.set(item.slug, item);
    const group = nameGroups.get(item.name);
    if (group) group.push(item);
    else nameGroups.set(item.name, [item]);
  }
  // v3：592 个源技能里有 8 组重名（如 scientific-visualization×3、docx×2）。
  // 同名解析优先级：插件内置版 > 字节数更大的版本 > catalog 顺序。
  const rank = (item) => (item.source === 'builtin' ? 0 : 1);
  for (const [name, group] of nameGroups) {
    const sorted = [...group].sort((a, b) => rank(a) - rank(b) || (b.bytes ?? 0) - (a.bytes ?? 0));
    byName.set(name, sorted[0]);
  }
  const duplicateNames = [...nameGroups.entries()].filter(([, g]) => g.length > 1).map(([n, g]) => ({ name: n, count: g.length }));

  const domains = [];
  const caps = [];
  if (isDir(capsDir)) {
    const capFiles = fs
      .readdirSync(capsDir)
      .filter((n) => n.endsWith('.json'))
      .sort();
    for (const file of capFiles) {
      const domain = file.replace(/\.json$/, '');
      const jsonFile = path.join(capsDir, file);
      let doc;
      try {
        doc = readJson(jsonFile);
      } catch (err) {
        throw new Error(`能力卡解析失败 ${domain}.json: ${err.message}`);
      }
      domains.push({
        domain,
        label: doc.label ?? domain,
        skill: doc.skill ?? `research-${domain}`,
        summary: doc.summary ?? '',
        count: (doc.capabilities ?? []).length,
      });
      for (const cap of doc.capabilities ?? []) {
        caps.push({ ...cap, domain, domainLabel: doc.label ?? domain });
      }
    }
  }
  const capById = new Map(caps.map((c) => [c.id, c]));

  let gates = null;
  const gatesFile = path.join(dataDir, 'gates.json');
  if (fs.existsSync(gatesFile)) {
    try {
      gates = readJson(gatesFile);
    } catch {
      gates = null;
    }
  }

  const standards = listMarkdown(refsDir)
    .filter((n) => SKILL_FILE_RE.test(n))
    .map((n) => ({ file: n, title: firstHeading(path.join(refsDir, n)) }));

  let version = '';
  try {
    version = JSON.parse(fs.readFileSync(path.join(pluginRoot, 'package.json'), 'utf8')).version ?? '';
  } catch {
    version = '';
  }

  const stats = {
    version,
    skills: catalog.length,
    researchSkills: catalog.filter((i) => i.research).length,
    domains: domains.length,
    capabilities: caps.length,
    standards: standards.length,
    duplicateNames: duplicateNames.length,
    assets: { files: catalog.reduce((a, i) => a + (i.assets?.included ? i.assets.files : 0), 0) },
    byDomain: catalog.reduce((acc, i) => {
      acc[i.domain] = (acc[i.domain] ?? 0) + 1;
      return acc;
    }, {}),
  };

  function resolveInside(rel) {
    const target = path.resolve(pluginRoot, rel);
    const root = pluginRoot.endsWith(path.sep) ? pluginRoot : pluginRoot + path.sep;
    if (target !== pluginRoot && !target.startsWith(root)) {
      throw new Error(`路径越界，拒绝读取: ${rel}`);
    }
    if (!fs.existsSync(target) || !fs.statSync(target).isFile()) {
      throw new Error(`文件不存在: ${rel}`);
    }
    return target;
  }

  function read(rel, { offset = 0, limit = options.maxReadChars ?? 24000 } = {}) {
    const target = resolveInside(rel);
    const text = fs.readFileSync(target, 'utf8');
    const from = Math.max(0, Math.min(Number(offset) || 0, text.length));
    const size = Math.max(1000, Math.min(Number(limit) || 24000, 120000));
    const slice = text.slice(from, from + size);
    return {
      path: path.relative(pluginRoot, target).split(path.sep).join('/'),
      bytes: Buffer.byteLength(text, 'utf8'),
      chars: text.length,
      offset: from,
      returned: slice.length,
      truncated: from + slice.length < text.length,
      nextOffset: from + slice.length < text.length ? from + slice.length : null,
      text: slice,
    };
  }

  // catalog 里的 file 是相对 knowledge/ 的路径（如 skills/polish/xxx.md），
  // 而 read() 解析的是相对插件根的路径，所以这里统一补 knowledge/ 前缀。
  function catalogPath(item) {
    const rel = item.file ?? `skills/${item.domain}/${item.slug}.md`;
    return rel.startsWith('knowledge/') ? rel : `knowledge/${rel}`;
  }

  function skillPath(name) {
    const item = byName.get(name) ?? bySlug.get(name);
    if (!item) return null;
    return catalogPath(item);
  }

  // 域融合技能（skills/research-<域>.md）不在 592 条 catalog 里，
  // 不能走 skillPath（那里查的是原始技能目录）。这里直接按包内文件判定。
  function domainSkillPath(skill) {
    if (typeof skill !== 'string' || !skill.trim()) return null;
    const rel = `skills/${skill.trim()}.md`;
    return fs.existsSync(path.join(pluginRoot, rel)) ? rel : null;
  }

  function readSkill(name, opts) {
    const rel = skillPath(name);
    if (!rel) {
      const near = [...byName.keys()].filter((k) => k.includes(String(name).slice(0, 3))).slice(0, 5);
      throw new Error(`技能不存在: ${name}${near.length ? `；相近名字: ${near.join(', ')}` : ''}`);
    }
    const item = byName.get(name) ?? bySlug.get(name);
    return { skill: name, assets: item?.assets ?? { included: false }, ...read(rel, opts) };
  }

  /** v3：技能自带的 references/ scripts/ templates/ 等兄弟资产目录（相对包内路径）。 */
  function assetDirOf(item) {
    if (!item) return null;
    return path.join(knowledgeDir, 'skills', item.domain, `${item.slug}__assets`);
  }

  function listAssets(name) {
    const item = byName.get(name) ?? bySlug.get(name);
    if (!item) throw new Error(`技能不存在: ${name}`);
    const dir = assetDirOf(item);
    if (!item.assets?.included || !isDir(dir)) {
      const would = item.assets?.wouldBe ?? 0;
      return {
        skill: name,
        included: false,
        reason: would ? `该技能兄弟资产共 ${Math.round(would / 1024)} KB，超出随包体积预算，未收录` : '该技能没有文本型兄弟资产',
        files: [],
      };
    }
    const out = [];
    const walk = (cur, prefix) => {
      for (const e of fs.readdirSync(cur, { withFileTypes: true })) {
        const full = path.join(cur, e.name);
        const rel = prefix ? `${prefix}/${e.name}` : e.name;
        if (e.isDirectory()) walk(full, rel);
        else out.push({ path: rel, bytes: fs.statSync(full).size });
      }
    };
    walk(dir, '');
    return { skill: name, included: true, count: out.length, files: out.sort((a, b) => a.path.localeCompare(b.path)) };
  }

  function readAsset(name, inner) {
    const item = byName.get(name) ?? bySlug.get(name);
    if (!item) throw new Error(`技能不存在: ${name}`);
    const dir = assetDirOf(item);
    if (!item.assets?.included || !isDir(dir)) throw new Error(`技能 ${name} 的兄弟资产未随包收录`);
    const target = path.resolve(dir, String(inner ?? ''));
    const root = dir.endsWith(path.sep) ? dir : dir + path.sep;
    if (!target.startsWith(root)) throw new Error(`路径越界，拒绝读取: ${inner}`);
    if (!fs.existsSync(target) || !fs.statSync(target).isFile()) throw new Error(`资产文件不存在: ${inner}`);
    const rel = path.relative(pluginRoot, target).split(path.sep).join('/');
    return read(rel, {});
  }

  function searchSkills(query, { domain, limit = 10 } = {}) {
    const tokens = tokenize(query);
    const scored = [];
    for (const item of catalog) {
      if (domain && item.domain !== domain) continue;
      let score = 0;
      const lower = String(query ?? '').toLowerCase();
      if (lower && item.name.toLowerCase() === lower) score += 120;
      if (lower && item.name.toLowerCase().includes(lower)) score += 40;
      score += Math.min(36, overlap(tokens, item.name) * 12);
      score += Math.min(24, overlap(tokens, item.description) * 4);
      score += Math.min(12, overlap(tokens, (item.tags ?? []).join(' ')) * 4);
      if (item.research) score += 3;
      else score -= 6;
      if (score > 0) scored.push({ item, score });
    }
    scored.sort((a, b) => b.score - a.score || b.item.bytes - a.item.bytes);
    return scored.slice(0, Math.max(1, Math.min(40, limit))).map(({ item, score }) => ({
      name: item.name,
      domain: item.domain,
      bytes: item.bytes,
      path: catalogPath(item),
      score,
      assets: item.assets?.included ? item.assets.files : 0,
      description: String(item.description ?? '').replace(/\s+/g, ' ').slice(0, 220),
    }));
  }

  // 域词典：用户原话里出现这些词，给该域所有卡一点基础分。
  // 目的不是"精确分类"，而是保证常见说法（检索、润色、统计、画图…）至少进入候选，
  // 不让某张卡的 summary 里恰好有"数据"两个字就把整句话抢走。
  const DOMAIN_HINTS = {
    writing: ['写论文', '论著', '论文', '写作', '投稿', '摘要', '引言', '讨论', '方法学', '病例报告', '学位论文', '综述'],
    polish: ['润色', '改稿', '语体', 'ai 味', 'AI味', '查重', '降重', '改写', '通顺'],
    figures: ['画图', '作图', '机制图', '示意图', '流程图', '统计图', '柱状图', '生存曲线', '森林图', '配色', '分辨率', '图注', '多面板'],
    stats: ['统计', '回归', '生存分析', 'cox', 'logistic', '样本量', '倾向评分', 'PSM', '中介', '敏感性分析', 'p 值', '置信区间', '基线表', '亚组'],
    ideation: ['选题', '创新点', '查新', '假说', '研究设计', '标书', '基金', '伦理', '预注册', '技术路线'],
    review: ['审稿', '审稿意见', '自审', '返修', '修回', 'rebuttal', '回复信', '被拒', '申诉'],
    slides: ['ppt', '幻灯', '汇报', '答辩', '组会', '讲课', '海报', '演讲', '备注', '讲稿'],
    literature: ['文献', '检索', '检索式', '精读', '读论文', '综述', '证据表', '偏倚', 'prisma', 'pubmed', '查文献'],
    format: ['参考文献', '格式', '排版', '上标', '三线表', '投稿包', 'docx', 'pdf', 'endnote', 'zotero', '字号', '页数'],
    data: ['数据下载', 'GEO', 'TCGA', 'GWAS', '变异', '基因', '通路', '富集', '组学', '代谢组', '蛋白结构', '单细胞'],
  };

  function matchCapabilities(task, { limit = 3, domain } = {}) {
    const text = String(task ?? '');
    const tokens = tokenize(text);
    const lower = text.toLowerCase();
    // 域命中：一个域命中几个词就给它底分（每个 5 分，最多 15）
    const domainBoost = new Map();
    for (const [d, words] of Object.entries(DOMAIN_HINTS)) {
      let n = 0;
      for (const w of words) if (lower.includes(w.toLowerCase())) n++;
      if (n) domainBoost.set(d, Math.min(15, n * 5));
    }
    const scored = [];
    for (const cap of caps) {
      if (domain && cap.domain !== domain) continue;
      let score = 0;
      const hitTriggers = [];
      for (const trig of cap.triggers ?? []) {
        const t = String(trig);
        if (!t) continue;
        const tl = t.toLowerCase();
        if (lower.includes(tl)) {
          // 整句触发词：长匹配给高分
          score += 10 + Math.min(12, t.length * 2);
          hitTriggers.push(t);
          continue;
        }
        // 触发词整句没命中时，退一步按词片段匹配（"检索式怎么写才查得全" → "检索式"）
        let parts = 0;
        for (const seg of t.split(/[\s/、，,。；;？?（）()「」]+/)) {
          if (seg.length >= 2 && seg.length <= 8 && lower.includes(seg.toLowerCase())) {
            parts++;
            hitTriggers.push(seg);
          }
        }
        if (parts) score += Math.min(12, parts * 4);
      }
      if (lower.includes(cap.id.toLowerCase())) score += 200;
      // 卡名本身出现在原话里 = 最强信号（"机制图" → figures.mechanism）；
      // 卡名常带括号补充说明，比对时把括号部分去掉再试一次。
      const bareLabel = String(cap.label ?? '').replace(/[（(][^）)]*[）)]/g, '').trim();
      if (bareLabel && lower.includes(bareLabel.toLowerCase())) score += 25;
      else if (cap.label && lower.includes(String(cap.label).toLowerCase())) score += 25;
      score += Math.min(20, overlap(tokens, `${cap.label} ${cap.summary}`) * 3);
      score += Math.min(10, overlap(tokens, cap.domainLabel) * 2);
      score += domainBoost.get(cap.domain) ?? 0;
      if (score > 0) scored.push({ cap, score, hitTriggers: [...new Set(hitTriggers)] });
    }
    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, Math.max(1, Math.min(5, limit))).map(({ cap, score, hitTriggers }) => ({ cap, score, hitTriggers }));
  }

  function capabilityList(domain) {
    const filtered = domain ? caps.filter((c) => c.domain === domain) : caps;
    return filtered.map((c) => ({
      id: c.id,
      domain: c.domain,
      label: c.label,
      summary: c.summary,
      triggers: c.triggers ?? [],
      members: (c.members ?? []).map((m) => `${m.skill}(${m.verdict})`),
    }));
  }

  function domainDigest() {
    return domains.map((d) => `${d.domain}（${d.label}，${d.count} 张能力卡）`);
  }

  return {
    pluginRoot,
    knowledgeDir,
    dataDir,
    refsDir,
    skillsDir,
    capsDir,
    catalog,
    byName,
    bySlug,
    domains,
    caps,
    capById,
    gates,
    standards,
    stats,
    options,
    read,
    readSkill,
    listAssets,
    readAsset,
    skillPath,
    domainSkillPath,
    searchSkills,
    matchCapabilities,
    capabilityList,
    domainDigest,
    checkText,
  };
}
