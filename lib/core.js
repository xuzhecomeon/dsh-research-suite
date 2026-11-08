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

// 触发词索引：把 103 张卡的 triggers 拆成「关键词 → 卡」的反查表，匹配时用最长命中计分。
// 这样做的好处是准确、可解释（能说清命中了哪个词），而且阈值可以定得比 token 重叠高得多。
const TRIGGER_INDEX_CACHE = new WeakMap();

function getTriggerIndex(caps) {
  const cached = TRIGGER_INDEX_CACHE.get(caps);
  if (cached) return cached;
  const stop = new Set((MATCH_RULES.stopSegments ?? []).map((s) => normalizeKey(s)));
  const index = new Map();
  const add = (capId, key) => {
    if (key.length < 2 || stop.has(key)) return;
    let set = index.get(key);
    if (!set) {
      set = new Set();
      index.set(key, set);
    }
    set.add(capId);
  };
  for (const cap of caps) {
    for (const trig of cap.triggers ?? []) {
      const norm = normalizeKey(trig);
      if (!norm) continue;
      if (norm.length <= 12) add(cap.id, norm);
      // 长触发词（「帮我做基线表」这种整句）切 3~6 字窗口，避免整句匹配不上就零分
      if (norm.length > 6) {
        const noise = String(MATCH_RULES.windowStopChars ?? '');
        for (const size of [6, 5, 4, 3]) {
          for (let i = 0; i + size <= norm.length; i++) {
            const win = norm.slice(i, i + size);
            // 含虚词的窗口基本是「帮我写个」这类粘连片段，留在索引里只会制造误接管
            let dirty = false;
            for (const ch of win) if (noise.includes(ch)) dirty = true;
            if (!dirty) add(cap.id, win);
          }
        }
      }
    }
  }
  TRIGGER_INDEX_CACHE.set(caps, index);
  return index;
}

/**
 * v3.1 匹配：先判「这是不是科研任务」，再用「最长关键词命中 + 卡名 + 域底分 + 口语线索」算分；
 * 分数不够或领先不足就明说认不出，返回空 matches —— 这就是专家要求的「认不出就不接管」闸门。
 * 返回 { matches, candidates, takeover, confidence, score, gap, reason, negative, cueHits, researchCues, ambiguous, domain, hits }
 */
export function matchIn(caps, task, { limit = 3, domain } = {}) {
  const rules = MATCH_RULES;
  const text = String(task ?? '');
  const lower = text.toLowerCase();
  const norm = normalizeKey(text);
  const tokens = tokenize(text);
  const floor = Number(rules.floor ?? 20);
  const strongFloor = Number(rules.strongFloor ?? 12);
  const margin = Number(rules.margin ?? 5);
  const index = getTriggerIndex(caps);

  // 1) 非科研语义闸门（生活/娱乐/行政/通用工程）
  const negative = [];
  for (const p of rules.negativePatterns ?? []) {
    try {
      if (new RegExp(p.re, 'i').test(text)) negative.push(p.why);
    } catch {
      /* 单条规则写错不影响整体 */
    }
  }

  // 2) 口语线索：专家点出的「不够硬 / 有没有影响」这类说法，直接改投到语义正确的卡
  const cueHits = [];
  const cueScore = new Map();
  for (const c of rules.cues ?? []) {
    let hit = false;
    try {
      hit = new RegExp(c.re, 'i').test(text);
    } catch {
      hit = false;
    }
    if (!hit) continue;
    cueHits.push({ why: c.why });
    for (const [id, pts] of Object.entries(c.caps ?? {})) cueScore.set(id, (cueScore.get(id) ?? 0) + Number(pts));
  }
  const researchCues = (rules.researchCues ?? []).filter((w) => lower.includes(String(w).toLowerCase()));

  // 3) 关键词命中：对每个长度从长到短扫窗口，记录每张卡命中的最长词与全部词
  const hits = new Map();
  for (let L = 8; L >= 2; L--) {
    for (let i = 0; i + L <= norm.length; i++) {
      const ids = index.get(norm.slice(i, i + L));
      if (!ids) continue;
      for (const id of ids) {
        const rec = hits.get(id) ?? { len: 0, keys: new Set(), df: 99 };
        if (L > rec.len || (L === rec.len && ids.size < rec.df)) {
          rec.len = L;
          rec.df = ids.size;
        }
        rec.keys.add(norm.slice(i, i + L));
        hits.set(id, rec);
      }
    }
  }

  // 4) 域底分：命中 >=2 个域词才给分，单词命中只给 2 分
  const domainBoost = new Map();
  for (const [d, words] of Object.entries(DOMAIN_HINTS)) {
    let n = 0;
    for (const w of words) if (lower.includes(String(w).toLowerCase())) n++;
    if (n >= 2) domainBoost.set(d, Math.min(12, (n - 1) * 4));
    else if (n === 1) domainBoost.set(d, 2);
  }

  const scored = [];
  for (const cap of caps) {
    if (domain && cap.domain !== domain) continue;
    let score = 0;
    const hitKeys = [];
    let strong = false;
    const rec = hits.get(cap.id);
    if (rec) {
      // 特异性：这个词只被 1 张卡收录 +10，被 2 张 +7，被 3 张 +4 …… 共享词几乎不给分
      const spec = Math.max(0, 10 - 3 * (rec.df - 1));
      score += 10 + 4 * rec.len + spec + Math.min(9, (rec.keys.size - 1) * 3);
      hitKeys.push(...rec.keys);
      if (rec.len >= 3 && rec.df <= 3) strong = true;
    }
    const bareLabel = String(cap.label ?? '').replace(/[（(][^）)]*[）)]/g, '').trim();
    if (bareLabel.length >= 3 && norm.includes(normalizeKey(bareLabel))) {
      score += 32;
      strong = true;
      hitKeys.push(bareLabel);
    }
    if (norm.includes(normalizeKey(cap.id))) {
      score += 200;
      strong = true;
      hitKeys.push(cap.id);
    }
    // token 重叠只做辅助分：中文二元组很容易撞车，权重压到 8 分封顶
    let tokHit = 0;
    for (const t of tokenize(String(cap.summary ?? ''))) {
      if (t.length >= 2 && !(rules.stopTokens ?? []).includes(t) && lower.includes(t)) tokHit++;
    }
    score += Math.min(8, tokHit * 2);
    score += domainBoost.get(cap.domain) ?? 0;
    score += cueScore.get(cap.id) ?? 0;
    if (score > 0) scored.push({ cap, score, hitTriggers: [...new Set(hitKeys)].slice(0, 6), strong });
  }
  scored.sort((x, y) => y.score - x.score);

  const top = scored[0] ?? null;
  const second = scored[1] ?? null;
  const gap = top ? top.score - (second?.score ?? 0) : 0;

  let confidence = 'low';
  if (top) {
    if (top.score >= 38 && (gap >= 6 || !second) && (top.strong || cueHits.length)) confidence = 'high';
    else if (top.score >= floor && gap >= margin) confidence = 'medium';
  }

  let takeover = Boolean(top) && top.score >= floor && confidence !== 'low';
  let reason = '';
  if (!top) reason = '没有任何能力卡命中触发词或卡名';
  else if (top.score < strongFloor) reason = `最高分 ${top.score}，低于强命中下限 ${strongFloor}`;
  else if (top.score < floor) reason = `最高分 ${top.score}，低于接管门槛 ${floor}`;
  else if (confidence === 'low') reason = `最高分 ${top.score} 但领先第二名仅 ${gap}（需 ≥${margin}）或缺强信号，判为歧义`;

  // 5) 非科研闸门生效：除非同时有多条科研线索 + 口语线索 + 足够高分，否则不接管
  if (negative.length) {
    const overridden = researchCues.length >= 2 && Boolean(top) && top.score >= 45 && cueHits.length > 0;
    if (!overridden) {
      takeover = false;
      confidence = 'low';
      reason = `判定为非科研任务：${negative.join('；')}`;
    }
  }
  if (!takeover && !reason) reason = '综合分未达接管门槛';

  const ambiguous = [];
  for (const item of rules.ambiguous ?? []) {
    try {
      if (new RegExp(item.re).test(text)) ambiguous.push({ why: item.why, ask: item.ask });
    } catch {
      /* ignore */
    }
  }

  return {
    matches: takeover ? scored.slice(0, Math.max(1, Math.min(5, limit))) : [],
    candidates: scored.slice(0, 3),
    takeover,
    confidence,
    score: top?.score ?? 0,
    gap,
    reason,
    negative,
    cueHits,
    researchCues: researchCues.slice(0, 8),
    ambiguous,
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
