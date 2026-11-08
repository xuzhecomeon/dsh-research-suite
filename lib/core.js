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

// 断言性极限词：只有真的在给结论时才可疑，所以在语境里判断（见 checkText 的 absolute 分支）。
const ABSOLUTE_CLAIM_WORDS = ['最佳', '最优', '最强', '最差', '史无前例', '填补空白', '首创', '独一无二', '无可替代'];

const CLASSICAL_SINGLE = ['盖', '矣', '焉', '岂'];
const CLASSICAL_MULTI = ['然则', '之于', '之谓'];
// 「所谓/亦/故/夫」在学术书面语里合法存在（「所谓选择偏倚，是指…」「亦应」「故本研究」），
// 专家实测把它们当文言虚词报出来全是误报，因此降为提示级、且默认不计入问题数。
const CLASSICAL_SOFT = ['所谓', '亦', '故', '夫'];

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
    // 英文句子里、公式/DOI/URL 里的半角符号是合法的：左右两侧都是 ASCII 就跳过（v3.1 起）。
    if (isAsciiNeighbor(src, i)) continue;
    if (ch === '(' || ch === ')') {
      if (nearbyCjk(src, i)) {
        findings.push({ rule: '半角括号', level: 'error', line: lineOf(src, i), snippet: src.slice(Math.max(0, i - 8), i + 8), hint: '中文语境改用全角（）' });
      }
      continue;
    }
    if (ch === '"') {
      if (nearbyCjk(src, i)) {
        findings.push({ rule: '半角直引号', level: 'error', line: lineOf(src, i), snippet: src.slice(Math.max(0, i - 8), i + 8), hint: '改用「」或全角引号' });
      }
      continue;
    }
    if (nearbyCjk(src, i)) {
      findings.push({ rule: '半角标点', level: 'error', line: lineOf(src, i), snippet: src.slice(Math.max(0, i - 8), i + 8), hint: '中文语境改用全角标点' });
    }
  }

  // 白名单遮罩：命中白名单短语的位置替换成等长占位符，索引不变，
  // 这样「完全缓解」里的「完全」、「覆盖」里的「盖」不会再被当成问题（专家实测的核心误报）。
  const masked = maskWhitelisted(src);

  for (const p of AI_PHRASES) {
    let idx = masked.indexOf(p);
    while (idx >= 0) {
      findings.push({ rule: 'AI 套话', level: 'warn', line: lineOf(src, idx), snippet: p, hint: '删掉或换成具体陈述' });
      idx = masked.indexOf(p, idx + p.length);
    }
  }

  for (const w of [...ABSOLUTE_WORDS, ...ABSOLUTE_CLAIM_WORDS]) {
    const isClaimWord = ABSOLUTE_CLAIM_WORDS.includes(w);
    let idx = masked.indexOf(w);
    while (idx >= 0) {
      // 极限词只有在「给结论」的语境才报：同一分句里带 P 值/显著性表述的，才是主张；
      // 单纯出现在方法或结果描述里（「最佳截断值」）降为提示。
      const clause = clauseAround(src, idx);
      const claimish = /P\s*[<>=]|显著|优于|提高|降低|改善|证实|表明|优于|胜于|优于/.test(clause);
      findings.push({
        rule: '绝对化措辞',
        level: isClaimWord && claimish ? 'warn' : 'info',
        line: lineOf(src, idx),
        snippet: src.slice(Math.max(0, idx - 10), idx + 10),
        hint: isClaimWord && claimish ? '结论里出现极限词，改为可证伪的限定表述' : '提示：确认这是否是给结论；白名单术语（完全缓解/首次给药等）已自动跳过',
      });
      idx = masked.indexOf(w, idx + w.length);
    }
  }

  // 单字文言虚词只在句首/标点后命中，且不落在「覆盖/涵盖/遮盖」这类常用词里（已由遮罩保证）。
  for (const w of CLASSICAL_SINGLE) {
    let idx = masked.indexOf(w);
    while (idx >= 0) {
      const prev = masked[idx - 1] ?? '';
      const atClauseStart = idx === 0 || /[。；：！？\n，、（）]/.test(prev);
      if (atClauseStart) {
        findings.push({ rule: '文言虚词', level: 'warn', line: lineOf(src, idx), snippet: src.slice(Math.max(0, idx - 8), idx + 8), hint: '学术书面语不用「盖/矣/焉/岂」这类文言发语词' });
      }
      idx = masked.indexOf(w, idx + w.length);
    }
  }

  for (const w of CLASSICAL_MULTI) {
    let idx = masked.indexOf(w);
    while (idx >= 0) {
      findings.push({ rule: '文言虚词', level: 'warn', line: lineOf(src, idx), snippet: src.slice(Math.max(0, idx - 8), idx + 8), hint: '学术书面语不用文言句式' });
      idx = masked.indexOf(w, idx + w.length);
    }
  }

  // 「所谓/亦/故/夫」在现代学术书面语里是合法用法，只做提示，不计入问题数。
  for (const w of CLASSICAL_SOFT) {
    let idx = masked.indexOf(w);
    let n = 0;
    while (idx >= 0 && n < 5) {
      findings.push({ rule: '文言腔提示（低置信）', level: 'info', line: lineOf(src, idx), snippet: src.slice(Math.max(0, idx - 8), idx + 8), hint: '「所谓X，是指…」属正常学术写法；仅在读起来像古文时才改' });
      idx = masked.indexOf(w, idx + w.length);
      n++;
    }
  }

  const plainCites = [...src.matchAll(/\[\d+(?:[-,]\d+)*\]/g)].map((m) => m[0]);
  if (plainCites.length) {
    findings.push({
      rule: '引用编号上标待确认',
      level: 'info',
      line: 0,
      snippet: plainCites.slice(0, 10).join(' '),
      hint: `纯文本无法判断是否上标；中文期刊要求 ${plainCites.length} 处编号为上标，交付前逐处确认（本工具不做判断）`,
    });
  }

  const unitMiss = src.match(/(?<=\d)(?:mg|ml|mL|kg|cm|mm|min|mmHg|mol|mmol|μg|ng|IU)(?![a-zA-Z])/g);
  if (unitMiss) {
    findings.push({ rule: '数值与单位缺空格', level: 'info', line: 0, snippet: [...new Set(unitMiss)].slice(0, 10).join(' '), hint: '写作 5 mg/kg、37 ℃' });
  }

  const counts = {};
  const summary = { error: 0, warn: 0, info: 0 };
  for (const f of findings) {
    counts[f.rule] = (counts[f.rule] ?? 0) + 1;
    summary[f.level ?? 'info'] = (summary[f.level ?? 'info'] ?? 0) + 1;
  }
  // total 只算「确实要改」的两档：error（规范硬伤）与 warn（高置信）；info 是提示，不算问题数。
  return { counts, findings, total: summary.error + summary.warn, summary };
}

// ---------- v3.1 识别层：白名单、域词典、匹配规则（参数都在 data/ 下的 JSON 里，可调可测） ----------

function loadJsonUrl(url, fallback) {
  try {
    const raw = fs.readFileSync(url, 'utf8');
    const clean = raw.charCodeAt(0) === 0xfeff ? raw.slice(1) : raw;
    return JSON.parse(clean);
  } catch {
    return fallback;
  }
}

const GATE_WHITELIST = loadJsonUrl(new URL('../data/gate-whitelist.json', import.meta.url), {
  absoluteWhitelist: [],
  classicalCompoundWhitelist: [],
});

const MATCH_RULES = loadJsonUrl(new URL('../data/match-rules.json', import.meta.url), {
  floor: 26,
  strongFloor: 15,
  margin: 6,
  stopSegments: [],
  stopTokens: [],
  researchCues: [],
  negativePatterns: [],
  cues: [],
  ambiguous: [],
});

// 域词典：用户原话里出现这些词，给该域所有卡一点基础分。
// 只作底分（最多 12 分），不能靠它单独把一张卡顶到接管门槛，否则「数据」两个字就能抢走整句话。
const DOMAIN_HINTS = {
  writing: ['写论文', '论著', '写作', '投稿', '摘要', '引言', '讨论', '方法学', '病例报告', '学位论文', '开题'],
  polish: ['润色', '改稿', '语体', 'ai 味', 'AI味', '查重', '降重', '改写', '通顺', '不够顺'],
  figures: ['画图', '作图', '机制图', '示意图', '流程图', '统计图', '柱状图', '生存曲线', '森林图', '配色', '分辨率', '图注', '多面板', '导图'],
  stats: ['统计', '回归', '生存分析', 'cox', 'logistic', '样本量', '倾向评分', 'PSM', '中介', '敏感性分析', 'p 值', 'P 值', '置信区间', '基线表', '亚组', '插补', '方差分析'],
  ideation: ['选题', '创新点', '查新', '假说', '研究设计', '标书', '基金', '伦理', '预注册', '技术路线', '课题'],
  review: ['审稿', '审稿意见', '自审', '返修', '修回', 'rebuttal', '回复信', '被拒', '申诉', '论证不足'],
  slides: ['ppt', '幻灯片', '幻灯', '汇报', '答辩', '组会', '讲课', '海报', '演讲', '备注', '讲稿'],
  literature: ['文献', '检索', '检索式', '精读', '读论文', '证据表', '偏倚', 'prisma', 'pubmed', '查文献', '查新文献'],
  format: ['参考文献', '格式', '排版', '上标', '三线表', '投稿包', 'docx', 'pdf', 'endnote', 'zotero', '字号', '页数', '题注'],
  data: ['数据下载', 'GEO', 'TCGA', 'GWAS', '变异', '基因', '通路', '富集', '组学', '代谢组', '蛋白结构', '单细胞', '数据库'],
};

function isAsciiNeighbor(text, i) {
  const ascii = (c) => c !== '' && c.charCodeAt(0) < 128;
  return ascii(text[i - 1] ?? '') && ascii(text[i + 1] ?? '');
}

/** 把白名单短语整段替换成等长占位符：长度不变，索引可复用，误报直接消失。 */
function maskWhitelisted(src) {
  const phrases = [...(GATE_WHITELIST.absoluteWhitelist ?? []), ...(GATE_WHITELIST.classicalCompoundWhitelist ?? [])]
    .filter((p) => typeof p === 'string' && p.length >= 2)
    .sort((a, b) => b.length - a.length);
  if (!phrases.length) return src;
  const escaped = phrases.map((p) => p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  try {
    return src.replace(new RegExp(escaped.join('|'), 'g'), (m) => '□'.repeat(m.length));
  } catch {
    return src;
  }
}

/** 取命中位置所在的分句（±40 字），用来判断极限词是不是在给结论。 */
function clauseAround(src, idx) {
  const marks = ['。', '；', '\n', '！', '？'];
  let start = 0;
  for (const ch of marks) start = Math.max(start, src.lastIndexOf(ch, idx - 1) + 1);
  let end = src.length;
  for (const ch of marks) {
    const at = src.indexOf(ch, idx);
    if (at >= 0 && at < end) end = at;
  }
  return src.slice(start, Math.min(src.length, end + 1));
}

/**
 * v3.1 匹配：先判「这是不是科研任务」，再算分；分数不到门槛就明说认不出，不给候选。
 * 返回 { matches, candidates, takeover, confidence, score, gap, reason, negative, cueHits, researchCues, ambiguous, domain }
 * matches 为空 = 不接管（这正是专家要求的「认不出就不接管」闸门）。
 */
function normalizeKey(input) {
  return String(input ?? '')
    .toLowerCase()
    .replace(/[\uff01-\uff5a]/g, (c) => String.fromCharCode(c.charCodeAt(0) - 0xfee0))
    .replace(/[\s\u3000]/g, '')
    .replace(/[^0-9a-z\u3400-\u9fff]/g, '');
}

// ---------- v3.2 检索式识别层：能力卡全文 BM25 + accept/ask/reject 三出口 ----------
// 为什么换掉 v3.1 的「triggers 字面命中 + cues 正则」：
// 1) 能力卡的 triggers 是长句，用户换一种说法就整句落空，只能退化到片段匹配；
// 2) cues 把口语说法硬绑到单张卡上，表达多样性是开放的，规则表只会越补越长；
// 3) 阈值闸门治不了「候选生成不足」，只能压掉误接管、同时也压掉召回。
// 现在：把每张卡的 label / triggers / summary / protocol / decide / outputs 拼成检索文档，
// 建倒排索引算 BM25（字段加权 + 文档长度归一化）；口语差异靠「同义归一表」处理，只归一不绑卡。
const SIGNAL_MIN = 2; // 接管前至少要有的科研信号数
const BM25_K1 = 1.2;
const BM25_B = 0.75;
const FIELD_WEIGHTS = { label: 3, triggers: 2.5, summary: 1.5, protocol: 1, decide: 1, outputs: 1 };
const CARD_INDEX_CACHE = new WeakMap();

function addDocField(tf, text, weight) {
  let len = 0;
  for (const tok of tokenize(String(text ?? ''))) {
    tf.set(tok, (tf.get(tok) ?? 0) + weight);
    len += weight;
  }
  return len;
}

function getCardIndex(caps) {
  const cached = CARD_INDEX_CACHE.get(caps);
  if (cached) return cached;
  const docs = [];
  const df = new Map();
  let totalLen = 0;
  for (const cap of caps) {
    const tf = new Map();
    let len = 0;
    len += addDocField(tf, cap.label, FIELD_WEIGHTS.label);
    for (const t of cap.triggers ?? []) len += addDocField(tf, t, FIELD_WEIGHTS.triggers);
    len += addDocField(tf, cap.summary, FIELD_WEIGHTS.summary);
    for (const step of cap.protocol ?? []) {
      len += addDocField(tf, step.do, FIELD_WEIGHTS.protocol);
      len += addDocField(tf, step.when, FIELD_WEIGHTS.protocol);
    }
    for (const d of cap.decide ?? []) {
      len += addDocField(tf, d.when, FIELD_WEIGHTS.decide);
      len += addDocField(tf, d.use, FIELD_WEIGHTS.decide);
    }
    for (const o of cap.outputs ?? []) len += addDocField(tf, o, FIELD_WEIGHTS.outputs);
    for (const tok of tf.keys()) df.set(tok, (df.get(tok) ?? 0) + 1);
    totalLen += len;
    docs.push({ cap, tf, len });
  }
  const N = Math.max(1, docs.length);
  const avgLen = totalLen / N || 1;
  const idf = new Map();
  for (const [tok, n] of df) idf.set(tok, Math.log(1 + (N - n + 0.5) / (n + 0.5)));
  const built = { docs, df, idf, avgLen, N };
  CARD_INDEX_CACHE.set(caps, built);
  return built;
}

// 同义归一：把口语说法归一成领域用词，归一后的词照常走 BM25，可被多张卡共享，
// 不会像 cues 那样一条正则独占绑定到某张卡。
function expandQuery(text) {
  const lower = String(text ?? '').toLowerCase();
  const extra = [];
  for (const syn of MATCH_RULES.synonyms ?? []) {
    for (const from of syn.from ?? []) {
      const f = String(from ?? '').toLowerCase();
      if (f && lower.includes(f)) {
        extra.push(syn.to);
        break;
      }
    }
  }
  return extra.join(' ');
}

function countHits(text, words) {
  const lower = String(text ?? '').toLowerCase();
  const hit = [];
  for (const w of words ?? []) {
    const s = String(w ?? '').toLowerCase();
    if (s && lower.includes(s)) hit.push(String(w));
  }
  return hit;
}

/**
 * v3.2 匹配：BM25 检索 + 三出口。返回
 * { route:'takeover'|'ask'|'reject', takeover, confidence, matches, candidates, ask, reason,
 *   score, gap, marginRatio, negative:[{category,why}], researchSignal, cues, ambiguous, notes, domain, hits }
 * 出口语义（评审要求）：
 *   takeover —— 相关度够且明显领先（score≥accept.score 且 marginRatio≥accept.marginRatio）
 *   ask      —— 相关度够但拉不开（或只到 ask.score），给出两张候选 + 一句二选一提问
 *   reject   —— 不像科研任务（命中非科研模式且科研线索 < 2），或相关度低于 ask 门槛
 */
function resolveAffinity(text, table) {
  const out = [];
  for (const rule of table ?? []) {
    let matched = false;
    try {
      matched = new RegExp(rule.re, 'i').test(text);
    } catch {
      matched = false;
    }
    if (matched && Array.isArray(rule.ids) && rule.ids.length) {
      out.push({ label: rule.label ?? rule.re, delta: Number(rule.delta ?? 0), ids: rule.ids, matched: true });
    }
  }
  return out;
}

export function matchIn(caps, task, { limit = 3, domain, force = null } = {}) {
  const text = String(task ?? '');
  const policy = MATCH_RULES.policy ?? {};
  const acceptScore = Number(policy.accept?.score ?? 45);
  const acceptRatio = Number(policy.accept?.marginRatio ?? 1.1);
  const askScore = Number(policy.ask?.score ?? 25);
  const pool = domain ? caps.filter((c) => c.domain === domain) : caps;

  // 0) 用户显式点名某张卡（"按 format.ref-style 来"）
  if (force) {
    const cap = caps.find((c) => c.id === String(force)) ?? null;
    if (cap) {
      const one = { cap, score: 100, raw: 99, hitTriggers: ['force'], strong: true };
      return {
        route: 'takeover', takeover: true, confidence: 'high', matches: [one], candidates: [one],
        ask: '', score: 100, gap: 100, marginRatio: 99, negative: [], researchSignal: 99,
        cues: [], ambiguous: [], notes: [], domain: cap.domain, hits: ['force'],
      };
    }
  }

  // 1) 非科研语义闸门（规则轨；分类轨用 researchSignal 兜底）
  const negative = [];
  for (const p of MATCH_RULES.negativePatterns ?? []) {
    try {
      if (new RegExp(p.re, 'i').test(text)) negative.push({ category: p.category ?? 'other', why: p.why });
    } catch {
      /* 单条规则写错不影响整体 */
    }
  }

  // 2) 科研信号：领域线索词 + 研究对象词 + 交付物动词
  const cueWords = countHits(text, MATCH_RULES.researchCues);
  const objectHits = countHits(text, MATCH_RULES.objectWords);
  const deliverableHits = countHits(text, MATCH_RULES.deliverableWords);
  const researchSignal =
    cueWords.length + Math.min(2, objectHits.length) + Math.min(1, deliverableHits.length);
  // 强科研信号：命中负例词时，只有高特异性科研词≥2、科研线索≥3、且有明确交付动词才允许翻盘
  const strongTermHits = countHits(text, MATCH_RULES.strongResearchTerms);
  const strongResearch = researchSignal >= 3 && deliverableHits.length >= 1 && strongTermHits.length >= 2;

  // 3) BM25 打分 + 长度归一化 + 动词亲和
  const index = getCardIndex(pool);
  const queryText = text + ' ' + expandQuery(text);
  const qTokens = [...new Set(tokenize(queryText))];
  const qLen = Math.max(1, qTokens.length);
  const normK = Number(policy.normK ?? 5);
  const denom = normK * Math.sqrt(qLen);
  const affinities = resolveAffinity(text, MATCH_RULES.verbAffinity);
  const scored = [];
  for (const doc of index.docs) {
    let raw = 0;
    const hits = [];
    for (const q of qTokens) {
      const tf = doc.tf.get(q);
      if (!tf) continue;
      const idf = index.idf.get(q) ?? 0;
      raw += (idf * (tf * (BM25_K1 + 1))) / (tf + BM25_K1 * (1 - BM25_B + (BM25_B * doc.len) / index.avgLen));
      hits.push(q);
    }
    if (raw <= 0) continue;
    let boost = 0;
    for (const aff of affinities) {
      if (aff.matched) boost += aff.delta;
    }
    const adj = raw + boost;
    const score = Math.round((100 * adj) / (adj + denom));
    scored.push({ cap: doc.cap, score, raw: Number(adj.toFixed(3)), hitTriggers: hits.slice(0, 6), strong: score >= 45 });
    // 亲和命中条件在下面按 cap 判定（affinities 是「查询侧」条件，逐卡累加）
  }
  // 按卡判定亲和（同一查询条件对不同卡族只加一次）
  for (const item of scored) {
    let boost = 0;
    for (const aff of affinities) {
      if (!aff.matched) continue;
      if (aff.ids.some((tok) => item.cap.id.includes(tok))) boost += aff.delta;
    }
    if (boost > 0) {
      const adj = item.raw + boost;
      item.raw = Number(adj.toFixed(3));
      item.score = Math.round((100 * adj) / (adj + denom));
      item.strong = item.score >= 45;
    }
  }
  scored.sort((x, y) => y.score - x.score || y.raw - x.raw);
  const top = scored[0] ?? null;
  const second = scored[1] ?? null;
  const gap = top ? top.score - (second?.score ?? 0) : 0;
  const marginRatioRaw = top && second && second.score > 0 ? top.score / second.score : 99;

  // 3.5) 执行类意图：跑代码/脚本不落到能力卡，直接指向 research_run
  const runVerbRe = /(跑一下|跑个|跑下|执行一下|帮我跑|运行一下|跑这段|跑一遍|执行这段)/;
  const runCodeRe = /(代码|脚本|script|\.R\b|\.py\b|python|命令行|报错|报错信息)/i;
  if (runVerbRe.test(text) && runCodeRe.test(text)) {
    return {
      route: 'takeover',
      takeover: true,
      runIntent: true,
      confidence: 'high',
      score: 0,
      gap: 0,
      marginRatio: 1,
      matches: [],
      candidates: (scored ?? []).slice(0, 3),
      ask: '',
      reason: '这是执行类任务（跑代码/脚本），应直接用 research_run 工具，不需要能力卡',
      negative,
      researchSignal,
      cues: [],
      ambiguous: [],
      notes: ['执行类意图：已指向 research_run（两段式：先预览脚本，再确认执行）'],
      domain,
      hits: [],
    };
  }

  // 4) 三出口
  const preNotes = [];
  let route = 'reject';
  let reason = '';
  let ask = '';
  // 信号闸：接管前必须先有科研信号（否则「帮我翻译课文」这种也会因为匹配到 polish 卡而被接管）
  const signalOk = strongTermHits.length >= 1 || researchSignal >= 3;
  if (!top) {
    reason = '没有任何能力卡与这句话相关（候选为 0）';
  } else if (negative.length && !strongResearch) {
    route = 'reject';
    reason = `判定为非科研任务（${negative.map((n) => n.category).join('、')}）：${negative[0].why}`;
  } else if (top.score >= acceptScore && marginRatioRaw >= acceptRatio) {
    route = 'takeover';
  } else if (top.score >= acceptScore && second && top.cap.domain === second.cap.domain) {
    // 同域近似：前两名在同一能力域内，风险低，直接按 top1 执行，并在 note 里提示回看次优卡判据
    route = 'takeover';
    preNotes.push(`同域近似：次优是同域的「${second.cap.label}」（${second.cap.id}，${second.score}），按 top1 执行；若判据不符请改走次优卡`);
  } else if (top.score >= askScore) {
    route = 'ask';
    const two = scored.slice(0, 2);
    ask = two.length === 2
      ? `你更想要「${two[0].cap.label}」（${two[0].cap.id}），还是「${two[1].cap.label}」（${two[1].cap.id}）？`
      : `你要的是「${two[0].cap.label}」（${two[0].cap.id}）吗？`;
    reason = top.score >= acceptScore
      ? `最高分 ${top.score} 与次高 ${second?.score ?? 0} 太接近（领先倍率 ${marginRatioRaw.toFixed(2)} < ${acceptRatio}），先确认再动手`
      : `相关度只到 ${top.score}（接管门槛 ${acceptScore}），先确认再动手`;
  } else {
    reason = `最高相关度 ${top.score}，低于接管门槛 ${acceptScore}`;
  }

  const notes = [...preNotes];
  if (negative.length && route === 'takeover') {
    notes.push(`这句同时命中了「${negative[0].category}」的特征，但科研线索有 ${researchSignal} 条，按科研任务处理`);
  }
  const affHits = affinities.filter((x) => x.matched).map((x) => x.label);
  if (affHits.length) notes.push(`动词亲和命中：${affHits.join('、')}`);

  const ambiguous = [];
  for (const item of MATCH_RULES.ambiguous ?? []) {
    try {
      if (new RegExp(item.re).test(text)) ambiguous.push({ why: item.why, ask: item.ask });
    } catch {
      /* ignore */
    }
  }

  const takeover = route === 'takeover';
  const confidence = takeover
    ? marginRatioRaw >= acceptRatio * 1.25 && top.score >= acceptScore * 1.3
      ? 'high'
      : 'medium'
    : 'low';

  return {
    route,
    takeover,
    confidence,
    matches: takeover ? scored.slice(0, Math.max(1, Math.min(5, limit))) : [],
    candidates: scored.slice(0, 3),
    ask,
    reason,
    score: top?.score ?? 0,
    gap,
    marginRatio: Number(marginRatioRaw.toFixed(2)),
    negative,
    researchSignal,
    cues: cueWords.slice(0, 8),
    ambiguous,
    notes,
    domain: top?.cap.domain ?? null,
    hits: top ? top.hitTriggers : [],
  };
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

  // v3.1：真正的打分与「认不出就不接管」闸门在模块级 matchIn() 里，参数在 data/match-rules.json。
  function matchCapabilities(task, opts = {}) {
    return matchIn(caps, task, opts)
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
