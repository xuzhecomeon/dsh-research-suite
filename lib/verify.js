/**
 * dsh-research-suite v3.1 · verify
 *
 * 「知道怎么做」与「做出来」之间的执行与核验层。
 * 5 个 async 方法：runScript / checkData / checkOutputs / checkDois / auditRefs，
 * 由 lib/tools.js 包成工具暴露给模型。
 *
 * 设计约束（为什么这么写）：
 * 1) 只用 node 内置模块（fs/path/os/zlib/child_process），零第三方依赖——插件装进
 *    profile 的 node_modules 后，第三方包不一定解析得到，内置模块永远在。
 * 2) 绝不 import 任何 `@deepseek-ai/*`：入口静态 import 宿主包会在 profile 里解析失败，
 *    导致整个插件加载期抛错、技能全不注册（v1 的真实故障）。
 * 3) 所有方法都「不抛异常」：失败一律折成 {ok:false, error|blocked, hint}。工具层
 *    再把对象渲染成文本；若这里抛错，模型只能看到堆栈，拿不到可执行的下一步。
 */

import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import zlib from 'node:zlib';
import { spawnSync } from 'node:child_process';

const VERSION = '3.1.0';
const DEFAULT_TIMEOUT_MS = 600000;
const MAX_CAPTURE_BYTES = 8 * 1024 * 1024; // 单次执行 stdout/stderr 上限，防止死循环刷屏

// 解释器优先探测本机实际安装位置（Dr. Xu 这台机器上 R 与 Python 都不在 PATH 里）
const R_CANDIDATES = ['C:\\Program Files\\R\\R-4.6.1\\bin\\Rscript.exe'];
const PY_CANDIDATES = [
  'D:\\nodehome\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe',
];

// 执行前静态拦截：这些动作会改机器状态、装包、外联下载，不该由「跑一段分析脚本」触发。
// 注意 `format` 只匹配真正的格式化命令（format C:），不匹配 R 的 format() 函数——
// R 代码里 format(round(x, 2)) 极其常见，按裸字符串拦会误伤正常分析脚本。
const BLOCK_RULES = [
  { re: /install\.packages\s*\(/i, reason: '禁止在脚本里安装 R 包（install.packages）' },
  { re: /\bpip\s+install\b/i, reason: '禁止在脚本里安装 Python 包（pip install）' },
  { re: /devtools::install/i, reason: '禁止在脚本里安装 R 包（devtools::install）' },
  { re: /\brm\s+-rf?\b/i, reason: '禁止递归删除（rm -rf）' },
  { re: /\bRemove-Item\b/i, reason: '禁止 Remove-Item' },
  { re: /\bformat\s+[a-z]:[\\/]/i, reason: '禁止格式化磁盘（format C:）' },
  { re: /curl\b[^\n]*\|/i, reason: '禁止 curl 管道执行' },
  { re: /\biwr\s/i, reason: '禁止 Invoke-WebRequest 简写 iwr' },
  { re: /\bInvoke-WebRequest\b/i, reason: '禁止 Invoke-WebRequest' },
];

const SKIP_DIRS = new Set(['.git', 'node_modules', '__pycache__', '.cache']);
const MISSING_TOKENS = new Set(['', 'na', 'n/a', 'nan', 'null', 'none', '.', '-', '—', '缺失']);

// ---------------------------------------------------------------------------
// 通用小工具
// ---------------------------------------------------------------------------

function toText(buf) {
  let s = Buffer.isBuffer(buf) ? buf.toString('utf8') : String(buf ?? '');
  if (s.charCodeAt(0) === 0xfeff) s = s.slice(1); // 去 BOM：读配置/CSV 时 BOM 会污染首列列名
  return s;
}

function readTextFile(file) {
  return toText(fs.readFileSync(file));
}

function isInside(parent, child) {
  const rel = path.relative(path.resolve(parent), path.resolve(child));
  if (rel === '') return true;
  if (path.isAbsolute(rel)) return false;
  return rel !== '..' && !rel.startsWith(`..${path.sep}`);
}

function quoteCmd(command, arg) {
  return `"${command}" "${arg}"`;
}

function isMissingValue(v) {
  return MISSING_TOKENS.has(String(v ?? '').trim().toLowerCase());
}

function numericValue(v) {
  const s = String(v ?? '').trim();
  if (!/^[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?$/.test(s)) return null;
  const n = Number(s);
  return Number.isFinite(n) ? n : null;
}

function pad2(n) {
  return String(n).padStart(2, '0');
}

function round(n, digits = 2) {
  const f = 10 ** digits;
  return Math.round(n * f) / f;
}

function summarizeText(text, max = 4000) {
  const s = String(text ?? '');
  return s.length > max ? `${s.slice(0, max)}\n…（已截断，共 ${s.length} 字符）` : s;
}

// ---------------------------------------------------------------------------
// runScript：把一段 R/Python 代码真正跑起来，并交代「跑了什么、改了什么」
// ---------------------------------------------------------------------------

function cleanEnv() {
  const env = { ...process.env };
  // 本机 R 在 Windows 上遇到中文/英文混合的 LC_ALL 会直接报 locale 错，
  // 连 library() 都读不到。清掉这三个变量让 R 用系统默认 locale。
  for (const key of ['LC_ALL', 'LANG', 'LANGUAGE']) delete env[key];
  return env;
}

function pickRuntime(kind, candidates, allowPathFallback = true) {
  const tried = [];
  for (const candidate of candidates) {
    tried.push(candidate);
    if (fs.existsSync(candidate)) return { command: candidate, tried };
  }
  // 调用方显式给了候选清单时不再做 PATH 兜底：否则测试/运维想验证「解释器缺失」会被系统里另一个版本顶替
  if (!allowPathFallback) return { command: null, tried };
  // PATH 兜底：只在绝对路径探测失败后才试，避免把系统里另一个版本的解释器静默顶替掉。
  const names = kind === 'r' ? ['Rscript.exe', 'Rscript'] : ['python.exe', 'python3.exe', 'python', 'python3'];
  for (const name of names) {
    try {
      const res = spawnSync('where', [name], { encoding: 'utf8', timeout: 3000, windowsHide: true });
      if (res.status === 0 && res.stdout) {
        const first = res.stdout.split(/\r?\n/).map((s) => s.trim()).filter(Boolean)[0];
        if (first && fs.existsSync(first)) {
          tried.push(first);
          return { command: first, tried };
        }
      }
    } catch {
      /* 宿主禁止子进程时探测失败是正常情况，继续走 runtime_missing */
    }
  }
  return { command: null, tried };
}

function snapshotTree(root, limit = 20000) {
  const files = new Map();
  let truncated = false;
  const stack = [root];
  while (stack.length) {
    const dir = stack.pop();
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      if (files.size >= limit) {
        truncated = true;
        break;
      }
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (!SKIP_DIRS.has(entry.name)) stack.push(full);
        continue;
      }
      if (!entry.isFile()) continue;
      try {
        const st = fs.statSync(full);
        files.set(path.relative(root, full), { bytes: st.size, mtime: st.mtimeMs });
      } catch {
        /* 文件在扫描过程中被删掉：忽略 */
      }
    }
  }
  return { files, truncated };
}

function diffTree(before, after) {
  const changed = [];
  for (const [rel, info] of after) {
    const old = before.get(rel);
    // mtime 在部分文件系统上精度只有秒，留 1ms 容差避免「读取动作本身」被当成修改
    if (!old || old.bytes !== info.bytes || Math.abs(old.mtime - info.mtime) > 1) {
      changed.push({ path: rel.split(path.sep).join('/'), bytes: info.bytes, mtime: new Date(info.mtime).toISOString() });
    }
  }
  return changed.sort((a, b) => a.path.localeCompare(b.path));
}

async function runScript({ kind, code, workdir, timeoutMs = DEFAULT_TIMEOUT_MS } = {}, runtimeOpts = {}) {
  const startedAt = Date.now();
  const k = String(kind ?? '').trim().toLowerCase();
  if (k !== 'r' && k !== 'python') {
    return { ok: false, error: 'bad_kind', hint: "kind 只能是 'r' 或 'python'" };
  }
  if (typeof code !== 'string' || !code.trim()) {
    return { ok: false, error: 'empty_code', hint: 'code 不能为空' };
  }

  const base = workdir ? path.resolve(String(workdir)) : process.cwd();
  const allowedRoots = [process.cwd(), os.tmpdir()];
  if (!allowedRoots.some((root) => isInside(root, base))) {
    // 只在工作区/临时目录里写脚本：避免模型把脚本写进系统目录后被执行
    return { ok: false, blocked: true, reason: 'workdir_outside', hint: 'workdir 必须落在 process.cwd() 或系统临时目录内' };
  }

  const hit = BLOCK_RULES.find((rule) => rule.re.test(code));
  if (hit) {
    return { ok: false, blocked: true, reason: 'dangerous_code', hint: hit.reason };
  }

  // 显式传入 interpreters 时严格照办（不再 PATH 兜底），便于测试与部署时定位「装了但路径不对」
  const explicit = runtimeOpts.runtimes && runtimeOpts.runtimes[k];
  const candidates = explicit || (k === 'r' ? R_CANDIDATES : PY_CANDIDATES);
  const runtime = pickRuntime(k, candidates, !explicit);
  if (!runtime.command) {
    return { ok: false, error: 'runtime_missing', tried: runtime.tried };
  }

  fs.mkdirSync(base, { recursive: true });
  const ext = k === 'r' ? 'R' : 'py';
  const script = path.join(
    base,
    `.dsh-verify-${Date.now()}-${Math.random().toString(36).slice(2, 8)}.${ext}`,
  );
  fs.writeFileSync(script, code, 'utf8'); // 无 BOM：R/Python 带 BOM 的解释器会在首行报语法错

  // 快照放在脚本写入之后：脚本文件本身不算「执行产生的文件」，减少噪音
  const before = snapshotTree(base);
  const timeout = Number.isFinite(Number(timeoutMs)) && Number(timeoutMs) > 0
    ? Math.max(1000, Number(timeoutMs))
    : DEFAULT_TIMEOUT_MS;

  const res = spawnSync(runtime.command, [script], {
    cwd: base,
    env: cleanEnv(),
    encoding: 'utf8',
    timeout,
    windowsHide: true,
    maxBuffer: MAX_CAPTURE_BYTES,
  });
  const after = snapshotTree(base);
  const files = diffTree(before.files, after.files);
  const command = quoteCmd(runtime.command, script);
  const durationMs = Date.now() - startedAt;

  if (res.error) {
    const codeName = res.error.code;
    if (codeName === 'ENOENT') {
      // 探测到路径但实际不可执行（常见于文件被删/权限变更）
      return { ok: false, error: 'runtime_missing', tried: runtime.tried, command };
    }
    if (codeName === 'EPERM' || codeName === 'EACCES') {
      return {
        ok: false,
        error: 'spawn_blocked',
        hint: '宿主未允许子进程，请用宿主的 shell 工具跑返回的 command',
        command,
      };
    }
    if (codeName === 'ETIMEDOUT') {
      return {
        ok: false,
        timedOut: true,
        exitCode: res.status,
        signal: res.signal,
        stdout: summarizeText(res.stdout),
        stderr: summarizeText(res.stderr),
        script,
        command,
        kind: k,
        files,
        durationMs,
      };
    }
    return {
      ok: false,
      error: 'spawn_failed',
      hint: String(res.error.message ?? res.error),
      command,
      kind: k,
      durationMs,
    };
  }

  const timedOut = res.signal === 'SIGTERM' && res.status === null;
  return {
    ok: res.status === 0 && !timedOut,
    exitCode: res.status,
    signal: res.signal ?? null,
    stdout: summarizeText(res.stdout),
    stderr: summarizeText(res.stderr),
    script,
    command,
    kind: k,
    files,
    durationMs,
    ...(timedOut ? { timedOut: true } : {}),
  };
}

// ---------------------------------------------------------------------------
// checkData：数据六道闸门的机械部分（结构、缺失、重复、不可能值、EPV）
// ---------------------------------------------------------------------------

function detectDelimiter(text) {
  const sample = text.slice(0, 8192);
  let commas = 0;
  let tabs = 0;
  let quoted = false;
  for (let i = 0; i < sample.length; i += 1) {
    const ch = sample[i];
    if (ch === '"') {
      if (quoted && sample[i + 1] === '"') i += 1;
      else quoted = !quoted;
    } else if (!quoted) {
      if (ch === ',') commas += 1;
      else if (ch === '\t') tabs += 1;
    }
  }
  return tabs > commas ? '\t' : ',';
}

function parseDelimited(text, delimiter) {
  const rows = [];
  let row = [];
  let field = '';
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i += 1;
        } else {
          quoted = false;
        }
      } else {
        field += ch;
      }
      continue;
    }
    if (ch === '"') {
      quoted = true;
    } else if (ch === delimiter) {
      row.push(field);
      field = '';
    } else if (ch === '\n') {
      row.push(field);
      rows.push(row);
      row = [];
      field = '';
    } else if (ch !== '\r') {
      field += ch;
    }
  }
  if (field !== '' || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  while (rows.length > 0 && rows[rows.length - 1].every((c) => String(c).trim() === '')) rows.pop();
  return rows;
}

function classifyColumn(values) {
  const present = values.filter((v) => !isMissingValue(v));
  if (present.length === 0) return 'empty';
  if (present.every((v) => numericValue(v) !== null)) return 'numeric';
  if (present.every((v) => /^\d{4}[-/]\d{1,2}([-/]\d{1,2})?/.test(String(v).trim()))) return 'date';
  return 'text';
}

const ID_NAME_RE = /(?:^|[_\-\s])(id|编号|序号|编码|code)$/i;
const AGE_NAME_RE = /(age|年龄)/i;
const COUNT_NAME_RE = /(count|计数|频数|次数|n_|_n$|number)/i;
const PERCENT_NAME_RE = /(percent|rate|pct|proportion|率|百分比|占比)/i;

function inferEvents(values) {
  const present = values.map((v) => String(v ?? '').trim()).filter((v) => !isMissingValue(v));
  if (present.length === 0) return { events: 0, how: 'no-data' };
  const lower = present.map((v) => v.toLowerCase());
  const binary01 = lower.every((v) => v === '0' || v === '1');
  if (binary01) {
    return { events: lower.filter((v) => v === '1').length, how: 'binary-0/1（取 1 为事件）' };
  }
  const positives = new Set(['1', 'yes', 'true', 'y', '是', '有', '阳性', 'event', '死亡', '发生', '复发', '进展']);
  const hit = lower.filter((v) => positives.has(v)).length;
  if (hit > 0) return { events: hit, how: '阳性标记词（是/yes/true/死亡/发生…）' };
  // 二分变量但两个水平都不是常见阳性词：取较少的一类作为事件（保守估计，宁少不多）
  const counts = new Map();
  for (const v of lower) counts.set(v, (counts.get(v) ?? 0) + 1);
  const sorted = [...counts.values()].sort((a, b) => a - b);
  return { events: sorted[0] ?? 0, how: '二分变量取较少类为事件（自动推断）' };
}

async function checkData({ file, outcome, predictors } = {}) {
  const findings = [];
  if (!file || typeof file !== 'string') {
    return { file: file ?? null, rows: 0, cols: 0, delimiter: null, columns: [], findings: [{ rule: 'bad_args', level: 'error', detail: 'file 参数缺失' }], epv: { events: null, predictors: null, epv: null, ok: false } };
  }
  if (!fs.existsSync(file)) {
    return { file, rows: 0, cols: 0, delimiter: null, columns: [], findings: [{ rule: 'not_found', level: 'error', detail: `文件不存在：${file}` }], epv: { events: null, predictors: null, epv: null, ok: false } };
  }

  let text;
  try {
    text = readTextFile(file);
  } catch (err) {
    return { file, rows: 0, cols: 0, delimiter: null, columns: [], findings: [{ rule: 'read_failed', level: 'error', detail: String(err?.message ?? err) }], epv: { events: null, predictors: null, epv: null, ok: false } };
  }

  const delimiter = detectDelimiter(text);
  const table = parseDelimited(text, delimiter);
  if (table.length === 0) {
    return { file, rows: 0, cols: 0, delimiter, columns: [], findings: [{ rule: 'empty_file', level: 'error', detail: '文件没有可解析的表格行' }], epv: { events: null, predictors: null, epv: null, ok: false } };
  }

  const header = table[0].map((h, i) => {
    const name = String(h ?? '').trim() || `col_${i + 1}`;
    if (!name) findings.push({ rule: 'empty_header', level: 'error', detail: `第 ${i + 1} 列列名为空` });
    return name;
  });
  const dataRows = table.slice(1);
  const cols = header.length;

  // 表头重名：重名列在后续按列名取值时会静默取错（例如两个 "value" 列）
  const seenHeaders = new Map();
  const uniqueHeader = header.map((name, i) => {
    const n = (seenHeaders.get(name) ?? 0) + 1;
    seenHeaders.set(name, n);
    if (n === 1) return name;
    findings.push({ rule: 'duplicate_header', level: 'error', detail: `列名「${name}」重复（第 ${i + 1} 次出现），已重命名为 ${name}_${n}` });
    return `${name}_${n}`;
  });

  // 行宽不一致：多/少一格通常意味着分隔符或引号解析出问题，直接误导后续统计
  let ragged = 0;
  dataRows.forEach((row, idx) => {
    if (row.length !== cols) {
      ragged += 1;
      if (ragged <= 5) findings.push({ rule: 'ragged_row', level: 'warn', detail: `第 ${idx + 2} 行有 ${row.length} 列，表头是 ${cols} 列` });
    }
  });
  if (ragged > 5) findings.push({ rule: 'ragged_row', level: 'warn', detail: `共 ${ragged} 行宽度与表头不一致（只列前 5 行）` });

  const columns = [];
  const rawByCol = [];
  for (let c = 0; c < cols; c += 1) {
    const name = uniqueHeader[c];
    const values = dataRows.map((row) => (c < row.length ? row[c] : ''));
    rawByCol.push(values);
    const present = values.filter((v) => !isMissingValue(v));
    const missing = values.length - present.length;
    const missingRate = values.length ? round(missing / values.length, 4) : 0;
    const type = classifyColumn(values);
    const unique = new Set(present.map((v) => String(v).trim())).size;
    let min = null;
    let max = null;
    let bad = 0;
    if (type === 'numeric') {
      const nums = present.map((v) => numericValue(v)).filter((n) => n !== null);
      min = nums.length ? Math.min(...nums) : null;
      max = nums.length ? Math.max(...nums) : null;
      bad = present.length - nums.length;
    }
    columns.push({ name, type, missing, missingRate, unique, min, max, bad });

    if (missingRate > 0.5) findings.push({ rule: 'missing_rate', level: 'error', detail: `列「${name}」缺失率 ${(missingRate * 100).toFixed(1)}%（>50%，该列不可用于主分析）` });
    else if (missingRate > 0.2) findings.push({ rule: 'missing_rate', level: 'warn', detail: `列「${name}」缺失率 ${(missingRate * 100).toFixed(1)}%（>20%，需说明缺失机制）` });

    if (present.length > 0 && unique === 1) findings.push({ rule: 'constant_column', level: 'warn', detail: `列「${name}」只有 1 个取值「${present[0]}」，无信息量` });

    if (ID_NAME_RE.test(name) && present.length > 0 && unique < present.length) {
      findings.push({ rule: 'id_duplicate', level: 'error', detail: `疑似 ID 列「${name}」有重复值（${present.length} 行只有 ${unique} 个唯一值），可能导致一对一匹配错位` });
    }

    if (type === 'numeric') {
      const nums = present.map((v) => numericValue(v)).filter((n) => n !== null);
      if (AGE_NAME_RE.test(name)) {
        const badAge = nums.filter((v) => v < 0 || v > 120);
        if (badAge.length) findings.push({ rule: 'impossible_age', level: 'error', detail: `列「${name}」有 ${badAge.length} 个年龄值越界（<0 或 >120），如 ${badAge.slice(0, 3).join('、')}` });
      }
      if (COUNT_NAME_RE.test(name)) {
        const neg = nums.filter((v) => v < 0);
        if (neg.length) findings.push({ rule: 'negative_count', level: 'error', detail: `列「${name}」是计数列但有 ${neg.length} 个负值` });
      }
      if (PERCENT_NAME_RE.test(name)) {
        const over = nums.filter((v) => v < 0 || v > 100);
        if (over.length) findings.push({ rule: 'percent_range', level: 'error', detail: `列「${name}」是百分比/率但 ${over.length} 个值越界（<0 或 >100）` });
      }
      if (unique > 20 && !ID_NAME_RE.test(name) && /(code|编码)$/i.test(name)) {
        findings.push({ rule: 'too_many_levels', level: 'warn', detail: `列「${name}」有 ${unique} 个水平，疑似分类变量被当成连续变量` });
      }
    } else if (type === 'text' && unique > 20 && !ID_NAME_RE.test(name)) {
      findings.push({ rule: 'too_many_levels', level: 'warn', detail: `列「${name}」有 ${unique} 个文本水平（>20），若本应是分类变量请先归并` });
    }
  }

  // 完全重复行：多为合并/追加数据时的复制粘贴，直接违反独立观测假设
  const rowIndex = new Map();
  const dupRows = [];
  dataRows.forEach((row, idx) => {
    const key = row.map((v) => String(v).trim()).join('\u0001');
    if (!rowIndex.has(key)) rowIndex.set(key, []);
    rowIndex.get(key).push(idx + 2);
  });
  for (const lines of rowIndex.values()) {
    if (lines.length > 1) dupRows.push(lines);
  }
  if (dupRows.length) {
    const examples = dupRows.slice(0, 5).map((lines) => lines.join('=')).join('；');
    findings.push({ rule: 'duplicate_rows', level: 'error', detail: `${dupRows.length} 组行完全重复（行号：${examples}），独立样本假设被破坏` });
  }

  // EPV：每个自变量能分到几个事件。EPV<10 时回归系数与 CI 都不可信（Peduzzi 等）
  const epv = { events: null, predictors: null, epv: null, ok: false };
  if (outcome) {
    const idx = uniqueHeader.indexOf(String(outcome));
    if (idx < 0) {
      findings.push({ rule: 'epv_outcome_missing', level: 'warn', detail: `outcome 列「${outcome}」不在表头里，跳过 EPV` });
    } else {
      const inferred = inferEvents(rawByCol[idx]);
      const preds = Array.isArray(predictors) ? predictors.map(String) : [];
      const existing = preds.filter((p) => uniqueHeader.includes(p));
      for (const p of preds) {
        if (!uniqueHeader.includes(p)) findings.push({ rule: 'epv_predictor_missing', level: 'warn', detail: `predictor「${p}」不在表头里，未计入 EPV` });
      }
      epv.events = inferred.events;
      epv.how = inferred.how;
      epv.predictors = existing.length;
      if (existing.length > 0) {
        epv.epv = round(inferred.events / existing.length, 2);
        epv.ok = epv.epv >= 10;
        if (!epv.ok) findings.push({ rule: 'epv_low', level: 'error', detail: `EPV=${epv.epv}（${inferred.events} 事件 / ${existing.length} 自变量）<10，回归模型自由度不足` });
      } else if (preds.length === 0) {
        findings.push({ rule: 'epv_no_predictors', level: 'warn', detail: '给了 outcome 但 predictors 为空，EPV 未计算' });
      }
    }
  }

  return { file, rows: dataRows.length, cols, delimiter, columns, findings, epv };
}

// ---------------------------------------------------------------------------
// checkOutputs：交付物「真的能打开吗」——格式、尺寸、页数、文本层、表格数
// ---------------------------------------------------------------------------

function inspectPng(buf) {
  if (buf.length < 33 || buf.readUInt32BE(0) !== 0x89504e47) return { error: '不是 PNG（签名不符）' };
  const width = buf.readUInt32BE(16);
  const height = buf.readUInt32BE(20);
  const bitDepth = buf[24];
  const colorType = buf[25];
  let dpi = null;
  let hasPhys = false;
  let offset = 8;
  while (offset + 12 <= buf.length) {
    const len = buf.readUInt32BE(offset);
    const type = buf.toString('latin1', offset + 4, offset + 8);
    if (type === 'pHYs' && len >= 9) {
      hasPhys = true;
      const px = buf.readUInt32BE(offset + 8);
      const unit = buf[offset + 16];
      // pHYs 单位 1 = 每米像素。期刊要求 300 DPI ≈ 11811 像素/米
      if (unit === 1 && px > 0) dpi = Math.round(px * 0.0254);
    }
    if (type === 'IEND') break;
    offset += 12 + len;
    if (len <= 0) break;
  }
  return { width, height, bitDepth, colorType, dpi, hasPhys };
}

function inspectPdf(buf) {
  const raw = buf.toString('latin1');
  const pages = (raw.match(/\/Type\s*\/Page[^s]/g) ?? []).length;
  // 文本层判定：有字体资源或内容流里出现 BT...Tj/TJ —— 只有图片没有文字的 PDF 无法被审稿人检索
  const hasText = /\/Font\b/.test(raw) || /\bBT\b[\s\S]{0,4000}?\b(Tj|TJ)\b/.test(raw);
  return { pages, hasText, bytes: buf.length };
}

function readZipDirectory(buf) {
  let eocd = -1;
  const stop = Math.max(0, buf.length - 65557);
  for (let i = buf.length - 22; i >= stop; i -= 1) {
    if (buf.readUInt32LE(i) === 0x06054b50) {
      eocd = i;
      break;
    }
  }
  if (eocd < 0) return null;
  const total = buf.readUInt16LE(eocd + 10);
  let offset = buf.readUInt32LE(eocd + 16);
  const entries = new Map();
  for (let i = 0; i < total; i += 1) {
    if (offset + 46 > buf.length || buf.readUInt32LE(offset) !== 0x02014b50) break;
    const method = buf.readUInt16LE(offset + 10);
    const compSize = buf.readUInt32LE(offset + 20);
    const nameLen = buf.readUInt16LE(offset + 28);
    const extraLen = buf.readUInt16LE(offset + 30);
    const commentLen = buf.readUInt16LE(offset + 32);
    const localOffset = buf.readUInt32LE(offset + 42);
    const name = buf.toString('utf8', offset + 46, offset + 46 + nameLen);
    entries.set(name, { method, compSize, localOffset });
    offset += 46 + nameLen + extraLen + commentLen;
  }
  return entries;
}

function readZipEntry(buf, entry, maxBytes = 8 * 1024 * 1024) {
  const local = entry.localOffset;
  if (local + 30 > buf.length || buf.readUInt32LE(local) !== 0x04034b50) return null;
  const nameLen = buf.readUInt16LE(local + 26);
  const extraLen = buf.readUInt16LE(local + 28);
  const start = local + 30 + nameLen + extraLen;
  const data = buf.subarray(start, start + entry.compSize);
  try {
    if (entry.method === 0) return data;
    if (entry.method === 8) return zlib.inflateRawSync(data, { maxOutputLength: maxBytes }); // 防 zip 炸弹
  } catch {
    return null;
  }
  return null;
}

function countMatches(text, re) {
  return (text.match(re) ?? []).length;
}

function inspectDocx(buf, zip) {
  const docEntry = zip.get('word/document.xml');
  if (!docEntry) {
    return { ok: false, facts: { entries: zip.size }, findings: [{ rule: 'docx_missing_document', level: 'error', detail: 'zip 里没有 word/document.xml，Word 打开会报「文件已损坏」' }] };
  }
  const xmlBuf = readZipEntry(buf, docEntry);
  if (!xmlBuf) {
    return { ok: false, facts: { entries: zip.size }, findings: [{ rule: 'docx_unreadable', level: 'error', detail: 'word/document.xml 解压失败（zip 方法不支持或文件截断）' }] };
  }
  const xml = xmlBuf.toString('utf8');
  const paragraphs = countMatches(xml, /<w:p[ >]/g);
  const tables = countMatches(xml, /<w:tbl[ >]/g);
  const findings = [];
  if (paragraphs === 0) findings.push({ rule: 'docx_empty', level: 'warn', detail: 'document.xml 里没有任何段落' });
  return { ok: true, facts: { paragraphs, tables, entries: zip.size, documentBytes: xmlBuf.length }, findings };
}

function inspectXlsx(buf, zip) {
  const wb = zip.get('xl/workbook.xml');
  if (!wb) {
    return { ok: false, facts: { entries: zip.size }, findings: [{ rule: 'xlsx_missing_workbook', level: 'error', detail: 'zip 里没有 xl/workbook.xml，Excel 打开会报错' }] };
  }
  const xmlBuf = readZipEntry(buf, wb);
  const xml = xmlBuf ? xmlBuf.toString('utf8') : '';
  const sheets = countMatches(xml, /<sheet\b/g);
  const sheetsOnDisk = [...zip.keys()].filter((n) => /^xl\/worksheets\/sheet\d+\.xml$/.test(n)).length;
  const findings = [];
  if (sheets > 0 && sheetsOnDisk < sheets) {
    findings.push({ rule: 'xlsx_sheet_missing', level: 'warn', detail: `workbook 里有 ${sheets} 个 sheet，磁盘上只有 ${sheetsOnDisk} 个 worksheet XML` });
  }
  return { ok: sheets > 0, facts: { sheets, sheetsOnDisk, entries: zip.size }, findings };
}

async function checkOutputs({ files } = {}) {
  const list = Array.isArray(files) ? files : typeof files === 'string' ? [files] : [];
  const results = [];
  const kinds = {};

  for (const raw of list) {
    const file = String(raw ?? '').trim();
    const ext = path.extname(file).toLowerCase();
    const findings = [];
    let kind = ext.replace(/^\./, '') || 'unknown';
    let facts = {};
    let ok = false;

    if (!file) {
      results.push({ file: '', kind: 'unknown', ok: false, facts: {}, findings: [{ rule: 'bad_args', level: 'error', detail: '文件路径为空' }] });
      continue;
    }
    if (!fs.existsSync(file)) {
      results.push({ file, kind, ok: false, facts: {}, findings: [{ rule: 'not_found', level: 'error', detail: `文件不存在：${file}` }] });
      kinds[kind] = (kinds[kind] ?? 0) + 1;
      continue;
    }

    try {
      if (ext === '.png') {
        const info = inspectPng(fs.readFileSync(file));
        if (info.error) {
          findings.push({ rule: 'png_invalid', level: 'error', detail: info.error });
        } else {
          facts = info;
          ok = true;
          if (!info.hasPhys) {
            findings.push({ rule: 'png_no_dpi', level: 'warn', detail: 'PNG 没有 pHYs 块，无法判定 DPI（投稿图件必须显式写 300+ DPI）' });
          } else if (info.dpi !== null && info.dpi < 150) {
            findings.push({ rule: 'png_dpi_low', level: 'error', detail: `PNG 只有 ${info.dpi} DPI（<150），印刷会明显虚边` });
          } else if (info.dpi !== null && info.dpi < 300) {
            findings.push({ rule: 'png_dpi_low', level: 'warn', detail: `PNG 为 ${info.dpi} DPI（<300），多数期刊要求 300 DPI` });
          }
        }
      } else if (ext === '.pdf') {
        facts = inspectPdf(fs.readFileSync(file));
        ok = facts.pages > 0;
        if (!ok) findings.push({ rule: 'pdf_no_pages', level: 'error', detail: 'PDF 里找不到页面对象，可能不是完整 PDF' });
        if (!facts.hasText) findings.push({ rule: 'pdf_no_text', level: 'warn', detail: 'PDF 没有文本层（纯图片扫描件），审稿人无法检索/复制，投稿前建议 OCR' });
      } else if (ext === '.docx' || ext === '.xlsx') {
        const buf = fs.readFileSync(file);
        const zip = readZipDirectory(buf);
        if (!zip) {
          findings.push({ rule: 'zip_invalid', level: 'error', detail: `${kind.toUpperCase()} 应是一个 zip 容器，但没有找到 zip 目录（可能被改过扩展名）` });
        } else {
          const inner = ext === '.docx' ? inspectDocx(buf, zip) : inspectXlsx(buf, zip);
          facts = inner.facts;
          ok = inner.ok;
          findings.push(...inner.findings);
        }
      } else if (ext === '.csv' || ext === '.tsv') {
        const text = readTextFile(file);
        const delimiter = ext === '.tsv' ? '\t' : detectDelimiter(text);
        const table = parseDelimited(text, delimiter);
        facts = { rows: Math.max(0, table.length - 1), cols: table[0]?.length ?? 0, bytes: Buffer.byteLength(text) };
        ok = facts.rows > 0;
        if (!ok) findings.push({ rule: 'csv_empty', level: 'error', detail: 'CSV 只有表头或完全为空' });
      } else if (ext === '.md' || ext === '.markdown') {
        const text = readTextFile(file);
        const chars = text.replace(/\s/g, '').length;
        facts = { chars, lines: text.split(/\r?\n/).length, headings: countMatches(text, /^#{1,6}\s/gm), bytes: Buffer.byteLength(text) };
        ok = chars > 0;
        if (!ok) findings.push({ rule: 'md_empty', level: 'error', detail: 'Markdown 文件没有正文' });
      } else {
        findings.push({ rule: 'unsupported_type', level: 'error', detail: `暂不核验 ${ext || '（无扩展名）'} 类型，支持 png/pdf/docx/xlsx/csv/tsv/md` });
      }
    } catch (err) {
      findings.push({ rule: 'read_failed', level: 'error', detail: String(err?.message ?? err) });
    }

    kinds[kind] = (kinds[kind] ?? 0) + 1;
    results.push({ file, kind, ok, facts, findings });
  }

  const error = results.filter((r) => r.findings.some((f) => f.level === 'error')).length;
  const warn = results.filter((r) => r.findings.some((f) => f.level === 'warn')).length;
  return {
    results,
    summary: { files: results.length, ok: results.filter((r) => r.ok).length, error, warn, kinds },
  };
}

// ---------------------------------------------------------------------------
// checkDois：CrossRef 核验「这条参考文献真的存在吗」
// ---------------------------------------------------------------------------

function normalizeDoi(input) {
  return String(input ?? '')
    .trim()
    .replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, '')
    .replace(/^doi:\s*/i, '')
    .trim()
    .toLowerCase();
}

function firstOf(v) {
  return Array.isArray(v) && v.length ? String(v[0]) : null;
}

function crossrefYear(message) {
  const parts = message?.issued?.['date-parts']?.[0] ?? message?.published?.['date-parts']?.[0] ?? null;
  return Array.isArray(parts) && Number.isFinite(Number(parts[0])) ? Number(parts[0]) : null;
}

function crossrefAuthors(message) {
  const list = Array.isArray(message?.author) ? message.author : [];
  return list
    .slice(0, 12)
    .map((a) => [a?.given, a?.family].filter(Boolean).join(' ').trim())
    .filter(Boolean);
}

async function checkDois({ dois } = {}, runtime = {}) {
  const input = Array.isArray(dois) ? dois : typeof dois === 'string' ? [dois] : [];
  // fetchImpl 由工厂注入（测试用假 fetch，运行时用 globalThis.fetch）
  const fetchImpl = runtime.fetchImpl ?? globalThis.fetch;

  async function lookup(raw) {
    const doi = normalizeDoi(raw);
    const empty = { doi, ok: false, status: null, title: null, container: null, year: null, type: null, authors: [], error: null };
    if (!doi) return { ...empty, error: 'invalid_doi' };
    if (typeof fetchImpl !== 'function') return { ...empty, error: 'network' };

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 5000); // CrossRef 官方建议 5s 内返回；超时当作网络失败而非数据错误
    try {
      const url = `https://api.crossref.org/works/${encodeURIComponent(doi)}`;
      const res = await fetchImpl(url, {
        headers: { 'User-Agent': `dsh-research-suite/${VERSION}`, Accept: 'application/json' },
        signal: controller.signal,
      });
      if (!res.ok) {
        return { ...empty, status: res.status, error: res.status === 404 ? 'not_found' : `http_${res.status}` };
      }
      const json = await res.json();
      const message = json?.message ?? {};
      return {
        doi,
        ok: true,
        status: res.status,
        title: firstOf(message.title),
        container: firstOf(message['container-title']),
        year: crossrefYear(message),
        type: message.type ?? null,
        authors: crossrefAuthors(message),
        error: null,
      };
    } catch {
      // 网络断开、DNS 失败、代理拦截、超时：一律 network。绝不把异常抛给工具层。
      return { ...empty, error: 'network' };
    } finally {
      clearTimeout(timer);
    }
  }

  const out = new Array(input.length);
  let cursor = 0;
  const workers = Array.from({ length: Math.min(4, Math.max(1, input.length)) }, async () => {
    while (cursor < input.length) {
      const i = cursor;
      cursor += 1;
      out[i] = await lookup(input[i]);
    }
  });
  await Promise.all(workers);
  return out;
}

// ---------------------------------------------------------------------------
// auditRefs：正文引用编号 ↔ 文献表的机械对账
// ---------------------------------------------------------------------------

function extractCiteNumbers(text) {
  const numbers = [];
  const re = /\[(\d+(?:\s*[-,–]\s*\d+)?(?:\s*[,，]\s*\d+(?:\s*[-,–]\s*\d+)?)*)\]/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    for (const chunk of m[1].split(/[,，]/)) {
      const range = chunk.trim().match(/^(\d+)\s*[-–]\s*(\d+)$/);
      if (range) {
        const [a, b] = [Number(range[1]), Number(range[2])];
        if (a <= b && b - a <= 200) {
          for (let n = a; n <= b; n += 1) numbers.push(n);
        }
      } else {
        const n = Number(chunk.trim());
        if (Number.isFinite(n) && n > 0 && n < 10000) numbers.push(n);
      }
    }
  }
  return numbers;
}

function extractDois(text) {
  const out = new Map();
  const re = /10\.\d{4,9}\/[-._;()/:A-Za-z0-9]+/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    const doi = normalizeDoi(m[0].replace(/[.,;)\]]+$/, ''));
    if (!doi) continue;
    if (!out.has(doi)) out.set(doi, 0);
    out.set(doi, out.get(doi) + 1);
  }
  return out;
}

function findReferenceEntries(lines) {
  const heading = /^(?:#{1,6}\s*)?(参考文献|references?|literature\s+cited|引用文献)\s*[:：]?\s*$/i;
  let start = -1;
  for (let i = 0; i < lines.length; i += 1) {
    if (heading.test(lines[i].trim())) start = i;
  }
  const source = start >= 0 ? lines.slice(start + 1) : lines;
  const entries = [];
  for (const line of source) {
    const m = line.match(/^\s*(?:\[(\d+)\]|(\d+)[.)、]\s+)/);
    if (!m) continue;
    const n = Number(m[1] ?? m[2]);
    if (!Number.isFinite(n) || n <= 0) continue;
    if (entries.some((e) => e.n === n)) continue; // 同一编号重复出现时以第一条为准
    entries.push({ n, text: line.trim() });
  }
  return { start, entries };
}

async function auditRefs({ text } = {}) {
  const findings = [];
  const body = String(text ?? '');
  if (!body.trim()) {
    return { cites: [], uniqueCites: 0, dois: [], findings: [{ rule: 'empty_text', level: 'error', detail: 'text 为空，无法核对引用' }] };
  }

  const lines = body.split(/\r?\n/);
  const { start, entries } = findReferenceEntries(lines);
  // 文献表里的 [1] [2] 是条目编号，不是正文引用；先切掉文献表再统计引用，否则每条文献
  // 都会被当成一次「正文引用」，导致编号重复/跳号全部误报。
  const bodyOnly = start >= 0 ? lines.slice(0, start).join('\n') : body;

  const citeList = extractCiteNumbers(bodyOnly);
  const counts = new Map();
  for (const n of citeList) counts.set(n, (counts.get(n) ?? 0) + 1);
  const unique = [...counts.keys()].sort((a, b) => a - b);
  const maxCite = unique.length ? unique[unique.length - 1] : 0;

  const doiCounts = extractDois(bodyOnly);
  const dois = [...doiCounts.keys()];

  // 1) 编号跳号：1..max 里没出现的编号，通常意味着正文删改时漏掉了引用
  const gaps = [];
  for (let n = 1; n <= maxCite; n += 1) if (!counts.has(n)) gaps.push(n);
  if (gaps.length) findings.push({ rule: 'cite_gap', level: 'warn', detail: `引用编号跳号：缺 ${gaps.slice(0, 12).join('、')}${gaps.length > 12 ? ' …' : ''}` });

  // 2) 编号重复：同一编号在正文出现多次多半是复制粘贴，也可能是有意多次引用
  const repeated = [...counts].filter(([, c]) => c > 1).map(([n, c]) => `${n}×${c}`);
  if (repeated.length) findings.push({ rule: 'cite_duplicate', level: 'warn', detail: `编号被多次引用：${repeated.slice(0, 12).join('、')}${repeated.length > 12 ? ' …' : ''}` });

  if (entries.length === 0) {
    findings.push({ rule: 'no_reference_list', level: 'warn', detail: '没有识别到文献表条目（需以 [n] 或 n. 开头；若文献表格式不同请人工核对）' });
  } else {
    if (maxCite !== entries.length) {
      findings.push({ rule: 'cite_count_mismatch', level: 'error', detail: `正文最大编号 ${maxCite} 与文献表 ${entries.length} 条不一致（正文引用 ${unique.length} 个编号）` });
    }
    const missingDoi = entries.filter((e) => !/10\.\d{4,9}\//.test(e.text)).map((e) => e.n);
    if (missingDoi.length) findings.push({ rule: 'entry_missing_doi', level: 'warn', detail: `文献表条目缺 DOI：${missingDoi.slice(0, 15).join('、')}${missingDoi.length > 15 ? ' …' : ''}（共 ${missingDoi.length} 条）` });

    const currentYear = new Date().getFullYear();
    const future = entries.filter((e) => {
      const years = (e.text.match(/\b(19|20)\d{2}\b/g) ?? []).map(Number);
      return years.some((y) => y > currentYear);
    }).map((e) => e.n);
    if (future.length) findings.push({ rule: 'entry_future_year', level: 'error', detail: `文献表条目年份晚于当前年（${currentYear}）：${future.join('、')}，疑似编造或年份笔误` });

    const byDoi = new Map();
    for (const e of entries) {
      const m = e.text.match(/10\.\d{4,9}\/[-._;()/:A-Za-z0-9]+/g) ?? [];
      for (const d of m) {
        const doi = normalizeDoi(d.replace(/[.,;)\]]+$/, ''));
        if (!byDoi.has(doi)) byDoi.set(doi, []);
        byDoi.get(doi).push(e.n);
      }
    }
    const dupDoi = [...byDoi].filter(([, ns]) => new Set(ns).size > 1);
    if (dupDoi.length) findings.push({ rule: 'duplicate_doi', level: 'error', detail: `同一条文献在文献表里出现多次（同一 DOI 对应多个条目）：${dupDoi.slice(0, 5).map(([d, ns]) => `${d} → ${[...new Set(ns)].join('/')}`).join('；')}` });
  }

  // 3) 同一 DOI 在正文多次出现：可能是同一文献重复引用，也可能是把不同文献写成了同一 DOI
  const repeatedDoi = [...doiCounts].filter(([, c]) => c > 1).map(([d, c]) => `${d}×${c}`);
  if (repeatedDoi.length) findings.push({ rule: 'repeated_doi', level: 'warn', detail: `正文中同一 DOI 出现多次：${repeatedDoi.slice(0, 8).join('、')}${repeatedDoi.length > 8 ? ' …' : ''}` });

  // 4) 正文引用了文献表里没有的编号（跳号规则的补充：编号在表里但没在 1..max 区间内）
  if (entries.length) {
    const entryNums = new Set(entries.map((e) => e.n));
    const beyond = unique.filter((n) => n > entries.length && !entryNums.has(n));
    if (beyond.length) findings.push({ rule: 'cite_beyond_entries', level: 'error', detail: `正文引用编号超出文献表条数：${beyond.join('、')}` });
  }

  return { cites: citeList, uniqueCites: unique.length, dois, findings };
}

// ---------------------------------------------------------------------------
// 工厂
// ---------------------------------------------------------------------------

export function createVerify(core, options = {}) {
  void core; // 保留参数与 lib/core.js 的工厂约定一致；本模块不依赖 core 的索引状态
  return {
    // 同样绑定 options：测试可用 options.runtimes 指定不存在的解释器来覆盖 runtime_missing 分支
    runScript: (args, runtime) => runScript(args, runtime ?? options),
    checkData,
    checkOutputs,
    // 在这里绑定 options：checkDois 需要注入 fetchImpl，而模块级函数不能直接读工厂参数
    checkDois: (args, runtime) => checkDois(args, runtime ?? options),
    auditRefs,
    version: VERSION,
  };
}
