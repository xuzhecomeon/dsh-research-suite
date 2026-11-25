/**
 * lib/paper.js — 论文工坊：十阶段状态机 + 主张账本 + 机械核验 + 审稿门禁
 *
 * 融合自 ARIS 论文流水线（paper-plan / paper-write / paper-compile /
 * auto-paper-improvement-loop），但只保留与宿主无关的部分：
 *   - 不依赖 LaTeX 才能推进（有 .tex 就核 LaTeX，没有就核 Markdown）；
 *   - 不依赖任何外部审稿模型，审稿报告由调用方（人或模型）写成 JSON 后交回本模块判分；
 *   - 所有状态落在 <cwd>/.dsh-research/paper/state.json，可随时查看、可手工修。
 *
 * 零依赖：只用 node:fs / node:path。
 */
import fs from 'node:fs';
import path from 'node:path';

export const STAGES = [
  'intake',
  'ideation',
  'literature',
  'plan',
  'figures',
  'draft',
  'compile',
  'review',
  'submission',
];

export const GATES = ['claims', 'figures', 'manuscript', 'citations', 'compile', 'review'];

const STAGE_LABEL = {
  intake: '接料：把结果、图表、笔记收成一份材料',
  ideation: '立题：研究问题、假说、贡献点',
  literature: '文献：检索、精读、引用骨架',
  plan: '计划：主张—证据矩阵、章节页数、图计划',
  figures: '图件：主图与统计图先于正文',
  draft: '起草：分节写正文，逐条挂账',
  compile: '编译：LaTeX 或 docx，机械核验',
  review: '审稿：独立评审、评分阈值、阻断项清零',
  submission: '投稿：投稿包、格式、附件清单',
};

const GATE_LABEL = {
  claims: '主张—证据矩阵已冻结',
  figures: '图件齐备且分辨率达标',
  manuscript: '正文无占位符、无未解析引用',
  citations: '参考文献逐条可查、编号自洽',
  compile: '稿件能编译或能导出',
  review: '审稿收敛（总分与阻断项）',
};

/** 进入某阶段前应已通过的门禁：不通过只告警，不硬拦。 */
const ENTRY_GATES = {
  draft: ['claims', 'figures'],
  compile: ['manuscript'],
  review: ['compile'],
  submission: ['claims', 'figures', 'manuscript', 'citations', 'compile', 'review'],
};

const STAGE_ORDER = new Map(STAGES.map((s, i) => [s, i]));

const CLAIM_STATUS = new Set(['verified', 'partial', 'no-evidence', 'contradicted']);

const REVIEW_SCHEMA = 'research-suite/review@1';
const MIN_OVERALL = 6;
const PASS_VERDICTS = new Set(['ready', 'almost']);

const nowIso = () => new Date().toISOString();
const str = (v) => (typeof v === 'string' ? v : v == null ? '' : String(v));

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
}

/** 原子写：先写临时文件再改名，避免半截 JSON。 */
function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp-${process.pid}-${Date.now()}`;
  fs.writeFileSync(tmp, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
  fs.renameSync(tmp, file);
}

function rel(root, file) {
  return path.relative(root, file).split(path.sep).join('/');
}

function isInside(root, file) {
  const r = path.resolve(root);
  const f = path.resolve(file);
  return f === r || f.startsWith(`${r}${path.sep}`);
}

/** 在目录里按候选名找一个文件。 */
function findFirst(root, candidates) {
  for (const c of candidates) {
    const p = path.isAbsolute(c) ? c : path.join(root, c);
    if (fs.existsSync(p) && fs.statSync(p).isFile()) return p;
  }
  return null;
}

/** 简单递归收集文本文件，跳过依赖与内部目录。 */
function collectFiles(root, exts, limit = 300) {
  const out = [];
  const skip = new Set(['node_modules', '.git', '.dsh-research', 'dist', 'build', '__pycache__']);
  const walk = (dir, depth) => {
    if (out.length >= limit || depth > 6) return;
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      if (out.length >= limit) return;
      if (e.name.startsWith('.') && e.name !== '.') continue;
      if (skip.has(e.name)) continue;
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p, depth + 1);
      else if (e.isFile() && exts.includes(path.extname(e.name).toLowerCase())) out.push(p);
    }
  };
  walk(root, 0);
  return out;
}

function gateOf(state, name) {
  return state?.gates?.[name] ?? 'pending';
}

function gateMark(v) {
  if (v === 'passed') return '✓';
  if (v === 'failed') return '✗';
  return '·';
}

function summarizeClaims(claims) {
  const counts = { verified: 0, partial: 0, 'no-evidence': 0, contradicted: 0, invalid: 0 };
  for (const c of claims) counts[c.status] = (counts[c.status] ?? 0) + 1;
  return counts;
}

function normalizeClaimStatus(raw) {
  const s = str(raw).trim().toLowerCase();
  if (['verified', 'yes', 'supported', 'supported-by-data', 'ok', 'pass'].includes(s)) return 'verified';
  if (['partial', 'partly', 'mixed', 'weak'].includes(s)) return 'partial';
  if (['no-evidence', 'no', 'unverified', 'missing', 'none', 'unknown', 'fail'].includes(s)) return 'no-evidence';
  if (['contradicted', 'contradiction', 'against', 'refuted'].includes(s)) return 'contradicted';
  return 'invalid';
}

export function createPaper({ root = process.cwd() } = {}) {
  const projectRoot = path.resolve(root);
  const dir = path.join(projectRoot, '.dsh-research', 'paper');
  const statePath = path.join(dir, 'state.json');

  function blank() {
    return {
      schema: 'research-suite/paper@1',
      createdAt: nowIso(),
      updatedAt: nowIso(),
      title: '',
      venue: '',
      stage: 'intake',
      gates: Object.fromEntries(GATES.map((g) => [g, 'pending'])),
      artifacts: {},
      history: [],
    };
  }

  function load() {
    if (!fs.existsSync(statePath)) return null;
    try {
      const s = readJson(statePath);
      s.gates = { ...Object.fromEntries(GATES.map((g) => [g, 'pending'])), ...(s.gates ?? {}) };
      s.artifacts = s.artifacts ?? {};
      s.history = Array.isArray(s.history) ? s.history : [];
      s.stage = STAGES.includes(s.stage) ? s.stage : 'intake';
      return s;
    } catch {
      return null;
    }
  }

  function save(state) {
    state.updatedAt = nowIso();
    writeJson(statePath, state);
  }

  function touch(state, event, detail) {
    state.history.push({ at: nowIso(), event, detail: str(detail) });
    if (state.history.length > 200) state.history = state.history.slice(-200);
  }

  function requireState() {
    const s = load();
    if (!s) {
      return { error: `尚未初始化论文工坊。先执行 research_paper action=init（会在 ${rel(projectRoot, statePath)} 建状态文件）。` };
    }
    return { state: s };
  }

  function statusText(state) {
    const lines = [];
    lines.push(`## 论文工坊：${state.title || '（未命名）'}`);
    lines.push('');
    if (state.venue) lines.push(`目标venue：${state.venue}`);
    const idx = STAGE_ORDER.get(state.stage) ?? 0;
    lines.push(`当前阶段：${state.stage}（${idx + 1}/${STAGES.length}）— ${STAGE_LABEL[state.stage] ?? ''}`);
    lines.push('');
    lines.push('门禁：');
    for (const g of GATES) lines.push(`  ${gateMark(gateOf(state, g))} ${g} — ${GATE_LABEL[g]}`);
    const pending = GATES.filter((g) => gateOf(state, g) !== 'passed');
    if (pending.length) lines.push(`未通过：${pending.join('、')}`);
    else lines.push('六道门禁全部通过。');
    if (Object.keys(state.artifacts).length) {
      lines.push('');
      lines.push('产物：');
      for (const [k, v] of Object.entries(state.artifacts)) lines.push(`  ${k} → ${v}`);
    }
    lines.push('');
    lines.push(`状态文件：${rel(projectRoot, statePath)}`);
    return lines.join('\n');
  }

  function init(args = {}) {
    const existed = load();
    if (existed) {
      return [`论文工坊已存在，未覆盖。`, '', statusText(existed)].join('\n');
    }
    const s = blank();
    s.title = str(args.title).trim();
    s.venue = str(args.venue).trim();
    touch(s, 'init', s.venue ? `venue=${s.venue}` : '');
    save(s);
    return [`已初始化论文工坊：${rel(projectRoot, statePath)}`, '', statusText(s)].join('\n');
  }

  function setStage(args = {}) {
    const { state, error } = requireState();
    if (error) return error;
    const target = str(args.stage).trim();
    if (!STAGES.includes(target)) {
      return `阶段无效：${target || '（空）'}。可选：${STAGES.join('、')}。`;
    }
    const from = state.stage;
    const warnings = [];
    const need = ENTRY_GATES[target] ?? [];
    const blocked = need.filter((g) => gateOf(state, g) !== 'passed');
    if (blocked.length) {
      warnings.push(`进入 ${target} 前应已通过：${blocked.map((g) => `${g}（${gateOf(state, g)}）`).join('、')}。`);
    }
    if ((STAGE_ORDER.get(target) ?? 0) < (STAGE_ORDER.get(from) ?? 0)) {
      warnings.push(`回退阶段：${from} → ${target}。`);
    }
    state.stage = target;
    touch(state, 'stage', `${from} -> ${target}${str(args.note) ? `；${str(args.note)}` : ''}`);
    save(state);
    const out = [`阶段已设为：${target}（${STAGE_LABEL[target]}）`];
    if (warnings.length) out.push('', ...warnings.map((w) => `⚠ ${w}`));
    const idx = STAGE_ORDER.get(target) ?? 0;
    if (STAGES[idx + 1]) out.push('', `下一步通常是：${STAGES[idx + 1]}`);
    return out.join('\n');
  }

  function setGate(args = {}) {
    const { state, error } = requireState();
    if (error) return error;
    const gate = str(args.gate).trim();
    const result = str(args.result).trim() || 'pending';
    if (!GATES.includes(gate)) return `门禁名无效：${gate || '（空）'}。可选：${GATES.join('、')}。`;
    if (!['pending', 'passed', 'failed'].includes(result)) return `门禁状态无效：${result}。可选：pending、passed、failed。`;
    const before = gateOf(state, gate);
    state.gates[gate] = result;
    touch(state, 'gate', `${gate}: ${before} -> ${result}${str(args.note) ? `；${str(args.note)}` : ''}`);
    save(state);
    return `门禁 ${gate} 已记为 ${result}（${GATE_LABEL[gate]}）。`;
  }

  function findLedger(args = {}) {
    if (str(args.path)) {
      const p = path.resolve(projectRoot, str(args.path));
      if (!isInside(projectRoot, p)) return { error: '账本路径越界：必须位于当前工作目录内。' };
      if (!fs.existsSync(p)) return { error: `账本不存在：${rel(projectRoot, p)}。` };
      return { file: p };
    }
    const found = findFirst(projectRoot, [
      'paper/plan/CLAIM_LEDGER.json',
      '.dsh-research/paper/CLAIM_LEDGER.json',
      'paper/CLAIM_LEDGER.json',
      'CLAIM_LEDGER.json',
    ]);
    return found ? { file: found } : { error: '没找到 CLAIM_LEDGER.json。用 path 指定，或先按 templates/CLAIM_LEDGER.json 建一份。' };
  }

  function ledger(args = {}) {
    const { file, error } = findLedger(args);
    if (error) return error;
    let doc;
    try {
      doc = readJson(file);
    } catch (err) {
      return `账本不是合法 JSON：${rel(projectRoot, file)}（${err.message}）`;
    }
    const raw = Array.isArray(doc) ? doc : Array.isArray(doc?.claims) ? doc.claims : Array.isArray(doc?.entries) ? doc.entries : null;
    if (!raw) return '账本结构不认识：应为数组，或含 claims / entries 数组的对象。';
    const claims = raw.map((c, i) => {
      const claim = str(c?.claim ?? c?.statement ?? c?.text).trim();
      return {
        id: str(c?.id).trim() || `C${String(i + 1).padStart(2, '0')}`,
        claim,
        status: normalizeClaimStatus(c?.status ?? c?.verdict),
        evidence: str(c?.evidence ?? c?.source ?? c?.anchor).trim(),
      };
    });
    const counts = summarizeClaims(claims);
    const blocking = claims.filter((c) => c.status === 'contradicted' || c.status === 'no-evidence' || c.status === 'invalid');
    const bad = claims.filter((c) => !c.claim);
    const lines = [];
    lines.push(`## 主张—证据账本：${rel(projectRoot, file)}`);
    lines.push('');
    lines.push(`共 ${claims.length} 条：verified ${counts.verified}｜partial ${counts.partial}｜no-evidence ${counts['no-evidence']}｜contradicted ${counts.contradicted}${counts.invalid ? `｜状态非法 ${counts.invalid}` : ''}`);
    if (bad.length) lines.push(`⚠ ${bad.length} 条缺主张文本（id：${bad.map((c) => c.id).join('、')}）。`);
    if (blocking.length) {
      lines.push('');
      lines.push('必须处理（投稿前清零）：');
      for (const c of blocking.slice(0, 40)) {
        const label = c.status === 'invalid' ? '状态非法' : c.status === 'contradicted' ? '与证据矛盾' : '无证据';
        lines.push(`  - ${c.id}［${label}］${c.claim.slice(0, 80) || '（空）'}${c.evidence ? ` → ${c.evidence}` : ''}`);
      }
      if (blocking.length > 40) lines.push(`  … 另有 ${blocking.length - 40} 条`);
    }
    const partial = claims.filter((c) => c.status === 'partial');
    if (partial.length) {
      lines.push('');
      lines.push('需要弱化表述（partial）：');
      for (const c of partial.slice(0, 20)) lines.push(`  - ${c.id} ${c.claim.slice(0, 80)}`);
    }
    const verdict = blocking.length ? 'FAIL' : partial.length ? 'WARN' : 'PASS';
    lines.push('');
    lines.push(`结论：${verdict}${verdict === 'PASS' ? '（可进入下一阶段）' : verdict === 'WARN' ? '（可继续，但正文需按 partial 降调）' : '（先补证据或删主张，不要写进正文）'}`);
    const s = load();
    if (s) {
      touch(s, 'ledger', `${rel(projectRoot, file)}: ${verdict}`);
      s.artifacts.claims = rel(projectRoot, file);
      save(s);
    }
    return lines.join('\n');
  }

  /** 解析 .bib 里的 key 集合；找不到就返回 null。 */
  function loadBibKeys(args = {}) {
    let bib = str(args.bib).trim() ? path.resolve(projectRoot, str(args.bib)) : null;
    if (bib && !isInside(projectRoot, bib)) return { error: 'bib 路径越界。' };
    if (!bib) {
      const bibs = collectFiles(projectRoot, ['.bib'], 5);
      if (bibs.length) bib = bibs[0];
    }
    if (!bib || !fs.existsSync(bib)) return { bib: null, keys: null };
    const text = fs.readFileSync(bib, 'utf8');
    const keys = new Set();
    for (const m of text.matchAll(/@\w+\s*\{\s*([^,\s]+)\s*,/g)) keys.add(m[1].trim());
    return { bib: rel(projectRoot, bib), keys };
  }

  function analyzeText(file, text, bibKeys, begins, ends) {
    const findings = [];
    const lines = text.split(/\r?\n/);
    const relFile = rel(projectRoot, file);
    const add = (lineNo, code, message, severity = 'error') => {
      findings.push({ file: relFile, line: lineNo, code, message, severity });
    };
    const markerRe = /\b(TODO|FIXME|NEED-CITE|CITATION[- ]NEEDED|TBD|XXX|\?\?\?)\b/i;
    const priorityRe = /\b(novel|first[- ]ever|state[- ]of[- ]the[- ]art|SOTA|breakthrough)\b|首次|首个|国际领先|填补空白|最佳结果/i;
    let heading = null;
    let headingLine = 0;
    let contentSinceHeading = 0;
    const citeKeys = new Set();
    let bibHits = 0;
    lines.forEach((line, i) => {
      const lineNo = i + 1;
      if (markerRe.test(line)) add(lineNo, 'TODO_MARKER', `占位标记：${line.trim().slice(0, 90)}`);
      if (/\\(?:todo|missingcite)\s*\{/.test(line) || /\[待补\]|\[待定\]|【待补】/.test(line)) {
        add(lineNo, 'TODO_MARKER', `占位内容：${line.trim().slice(0, 90)}`);
      }
      if (priorityRe.test(line)) add(lineNo, 'PRIORITY_WORD', `优先性/绝对化措辞，需证据或改写：${line.trim().slice(0, 90)}`, 'warn');
      // 标题与空章节
      const h = line.match(/^\s*#{1,6}\s+(.+)$/) || line.match(/^\s*\\(section|subsection|subsubsection)\*?\{([^}]*)\}/);
      if (h) {
        if (heading && contentSinceHeading === 0) {
          add(headingLine, 'EMPTY_SECTION', `章节「${heading}」没有正文。`);
        }
        heading = (h[2] ?? h[1] ?? '').trim();
        headingLine = lineNo;
        contentSinceHeading = 0;
        return;
      }
      if (line.trim()) contentSinceHeading += 1;
      // 引用键
      for (const m of line.matchAll(/\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}/g)) {
        for (const k of m[1].split(',')) {
          const key = k.trim();
          if (!key) continue;
          citeKeys.add(key);
          if (bibKeys && bibKeys.size && !bibKeys.has(key)) {
            bibHits += 1;
            add(lineNo, 'CITE_UNKNOWN', `引用键不在 bib 中：${key}`);
          }
        }
      }
      if (/\\begin\{(\w+)\}/.test(line)) {
        for (const m of line.matchAll(/\\begin\{(\w+)\}/g)) begins[m[1]] = (begins[m[1]] ?? 0) + 1;
      }
      if (/\\end\{(\w+)\}/.test(line)) {
        for (const m of line.matchAll(/\\end\{(\w+)\}/g)) ends[m[1]] = (ends[m[1]] ?? 0) + 1;
      }
    });
    for (const env of new Set([...Object.keys(begins), ...Object.keys(ends)])) {
      if ((begins[env] ?? 0) !== (ends[env] ?? 0)) {
        add(0, 'ENV_MISMATCH', `环境 ${env} 起止不匹配（begin ${begins[env] ?? 0} / end ${ends[env] ?? 0}）。`);
      }
    }
    return { findings, citeKeys, bibHits };
  }

  function lint(args = {}) {
    const targetArg = str(args.path).trim();
    const target = targetArg ? path.resolve(projectRoot, targetArg) : projectRoot;
    if (!isInside(projectRoot, target)) return '路径越界：只能核验当前工作目录内的文件。';
    if (!fs.existsSync(target)) return `路径不存在：${rel(projectRoot, target)}。`;
    const { bib, keys: bibKeys, error: bibError } = loadBibKeys(args);
    if (bibError) return bibError;
    const files = fs.statSync(target).isDirectory() ? collectFiles(target, ['.md', '.tex', '.txt']) : [target];
    if (!files.length) return '没找到可核验的 .md / .tex / .txt 文件。';
    const all = [];
    let words = 0;
    const begins = {};
    const ends = {};
    for (const file of files) {
      const text = fs.readFileSync(file, 'utf8');
      words += text.split(/\s+/).filter(Boolean).length;
      const r = analyzeText(file, text, bibKeys, begins, ends);
      all.push(...r.findings);
    }
    const errors = all.filter((f) => f.severity !== 'warn');
    const warns = all.filter((f) => f.severity === 'warn');
    const lines = [];
    lines.push(`## 稿件机械核验：${files.length} 个文件｜${words} 词`);
    if (bib) lines.push(`参考文献：${bib}（${bibKeys?.size ?? 0} 个 key）`);
    else lines.push('参考文献：未找到 .bib，跳过引用键核对。');
    lines.push('');
    if (!errors.length && !warns.length) lines.push('没有发现问题：无占位符、无未解析引用、环境配对正常。');
    for (const f of all.slice(0, 80)) {
      lines.push(`${f.file}${f.line ? `:${f.line}` : ''} [${f.code}] ${f.message}`);
    }
    if (all.length > 80) lines.push(`… 另有 ${all.length - 80} 条`);
    lines.push('');
    lines.push(`结论：${errors.length ? 'FAIL' : warns.length ? 'WARN' : 'PASS'}（错误 ${errors.length} 条，提示 ${warns.length} 条）`);
    const s = load();
    if (s) {
      touch(s, 'lint', `${files.length} 文件，错误 ${errors.length}`);
      save(s);
    }
    return lines.join('\n');
  }

  function normalizeVerdict(raw) {
    const v = str(raw).trim().toLowerCase();
    if (['ready', 'accept', 'accept-with-minor', 'almost', 'minor', 'minor-revision', 'accept-after-minor'].includes(v)) {
      return v === 'almost' || v === 'minor' || v === 'minor-revision' || v === 'accept-after-minor' ? 'almost' : v === 'accept' ? 'ready' : 'almost';
    }
    if (['revise', 'major', 'major-revision', 'not-ready', 'reject'].includes(v)) return ['revise', 'major', 'major-revision'].includes(v) ? 'revise' : 'reject';
    return 'unknown';
  }

  function scoreMean(scores) {
    if (!scores) return null;
    const vals = Array.isArray(scores)
      ? scores.map((x) => Number(x?.score ?? x))
      : Object.values(scores).map((x) => Number(x?.score ?? x));
    const nums = vals.filter((n) => Number.isFinite(n));
    if (!nums.length) return null;
    return nums.reduce((a, b) => a + b, 0) / nums.length;
  }

  function review(args = {}) {
    const given = str(args.path).trim();
    const file = given
      ? path.resolve(projectRoot, given)
      : findFirst(projectRoot, [
          '.dsh-research/paper/REVIEW_REPORT.json',
          'paper/review/REVIEW_REPORT.json',
          'paper/REVIEW_REPORT.json',
          'REVIEW_REPORT.json',
        ]);
    if (!file) return '没找到 REVIEW_REPORT.json。用 path 指定，或按 templates/REVIEW_REPORT.md 的机读 JSON 段写一份。';
    if (!isInside(projectRoot, file)) return '路径越界：审稿报告必须在当前工作目录内。';
    let doc;
    try {
      doc = readJson(file);
    } catch (err) {
      return `审稿报告不是合法 JSON：${rel(projectRoot, file)}（${err.message}）。注意门禁只认 JSON，不认 Markdown 表格。`;
    }
    const scores = doc.scores ?? doc.dimensions ?? doc.rubric;
    let overall = Number(doc.overall ?? doc.score ?? doc.total);
    if (!Number.isFinite(overall)) overall = scoreMean(scores);
    if (!Number.isFinite(overall)) return '审稿报告缺 overall 或可解析的 scores，无法判分。';
    if (overall < 0 || overall > 10) return `overall=${overall} 越界，应为 0–10。`;
    const verdict = normalizeVerdict(doc.verdict ?? doc.decision);
    const blocking = Array.isArray(doc.blocking) ? doc.blocking : [];
    const nonBlocking = Array.isArray(doc.non_blocking) ? doc.non_blocking : Array.isArray(doc.nonBlocking) ? doc.nonBlocking : [];
    const blockingProblems = blocking.map((b) => (typeof b === 'string' ? b : str(b?.problem ?? b?.issue ?? b?.message))).filter(Boolean);
    const pass = overall >= MIN_OVERALL && PASS_VERDICTS.has(verdict) && blocking.length === 0;
    const lines = [];
    lines.push(`## 审稿门禁：${rel(projectRoot, file)}`);
    const round = doc.round ?? doc.review_round;
    if (round != null) lines.push(`轮次：${round}`);
    const reviewer = doc.reviewer;
    if (reviewer) {
      const kind = typeof reviewer === 'string' ? reviewer : str(reviewer.kind ?? reviewer.model ?? reviewer.independence);
      if (kind) lines.push(`评审：${kind}`);
    }
    lines.push(`总分：${overall.toFixed(1)}/10（阈值 ≥${MIN_OVERALL}）｜verdict：${verdict}`);
    lines.push(`阻断项：${blocking.length} 条${nonBlocking.length ? `｜非阻断 ${nonBlocking.length} 条` : ''}`);
    if (blockingProblems.length) {
      for (const p of blockingProblems.slice(0, 20)) lines.push(`  - ${p.slice(0, 120)}`);
    }
    lines.push('');
    if (verdict === 'unknown') lines.push('⚠ verdict 无法识别，按不通过处理。可用 ready / almost / revise / reject。');
    if (overall < MIN_OVERALL) lines.push(`⚠ 总分低于阈值：还差 ${(MIN_OVERALL - overall).toFixed(1)} 分。`);
    if (blocking.length) lines.push('⚠ 先清零阻断项，再复评；不要用平均分掩盖单点硬伤。');
    lines.push(`结论：${pass ? 'PASS，可进入投稿阶段' : 'FAIL，继续修'}。`);
    const s = load();
    if (s) {
      s.gates.review = pass ? 'passed' : 'failed';
      s.artifacts.review = rel(projectRoot, file);
      touch(s, 'review', `${overall.toFixed(1)}/${verdict} → ${pass ? 'passed' : 'failed'}`);
      save(s);
    }
    return lines.join('\n');
  }

  function next() {
    const { state, error } = requireState();
    if (error) return error;
    const stage = state.stage;
    const idx = STAGE_ORDER.get(stage) ?? 0;
    const lines = [`当前阶段：${stage}（${STAGE_LABEL[stage]}）`, ''];
    const pending = GATES.filter((g) => gateOf(state, g) !== 'passed');
    if (stage === 'submission' && pending.length) {
      lines.push(`还没到投稿：先补 ${pending.join('、')}。`);
    } else if (stage === 'review') {
      lines.push('下一步：把审稿报告写成 JSON，跑 research_paper action=review；PASS 后 action=stage stage=submission。');
    } else if (stage === 'draft') {
      lines.push('下一步：分节写正文，逐条挂账；写完后 action=lint 机械核验，再 action=stage stage=compile。');
    } else if (idx + 1 < STAGES.length) {
      const n = STAGES[idx + 1];
      lines.push(`下一步：进入 ${n}（${STAGE_LABEL[n]}）。`);
      const need = ENTRY_GATES[n] ?? [];
      for (const g of need) lines.push(`  - ${gateOf(state, g) === 'passed' ? '✓' : '·'} ${g}（当前 ${gateOf(state, g)}）`);
    } else {
      lines.push('已到投稿阶段：核对投稿包与附件清单。');
    }
    lines.push('');
    lines.push('提醒：门禁只是机械底线，正文的主张与数字仍要回账本核对。');
    return lines.join('\n');
  }

  function runAction(action, args = {}) {
    switch (action) {
      case 'init':
        return init(args);
      case 'status': {
        const s = load();
        return s ? statusText(s) : '尚未初始化论文工坊。先执行 research_paper action=init。';
      }
      case 'stage':
        return setStage(args);
      case 'gate':
        return setGate(args);
      case 'ledger':
        return ledger(args);
      case 'lint':
        return lint(args);
      case 'review':
        return review(args);
      case 'next':
        return next();
      default:
        return `未知 action：${action}。可用：init、status、stage、gate、ledger、lint、review、next。`;
    }
  }

  return { projectRoot, dir, statePath, runAction, load, STAGES, GATES };
}
