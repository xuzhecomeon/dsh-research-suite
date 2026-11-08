/**
 * dsh-research-suite v3.2 · verify（执行与核验层 + 安全层）
 *
 * 「知道怎么做」与「做出来」之间的执行与核验层。
 * 5 个 async 方法：runScript / checkData / checkOutputs / checkDois / auditRefs，
 * 另导出 detectRuntime / detectRuntimes / loadPolicy 供状态工具与运维使用。
 *
 * 安全设计（对应外部评审 DEF-02 / DEF-03 / DEF-05）：
 * 1) 执行默认关闭：data/exec-policy.json 里 run.enabled=false 时 runScript 只返回预览，
 *    绝不落盘、绝不 spawn。开启后脚本以当前用户权限运行——这一点必须对使用者讲清楚，
 *    不能像 v3.1 那样在文档里写「只读、不联网」而与实现相反。
 * 2) 两段式：先预览（脚本前 60 行 + previewHash + 策略摘要 + 预计拦截项），
 *    调用方核对后传 confirm:true 且 previewHash 与原代码一致才执行；代码在预览后
 *    被改过（哈希不一致）一律拒绝，防止「看的是 A、跑的是 B」。
 * 3) 正向约束取代黑名单：包白名单 + 网络调用禁令 + 写文件只允许 workdir 内相对路径
 *    + PHI 关键词拒写 + 安装类动作永久拒绝。硬编码作者机器路径已全部移除，
 *    解释器改由 exec-policy → 环境变量 → PATH 三级探测。
 *
 * 设计约束（为什么这么写）：
 * 1) 只用 node 内置模块（fs/path/os/zlib/child_process/crypto/url），零第三方依赖——
 *    插件装进 profile 的 node_modules 后，第三方包不一定解析得到，内置模块永远在。
 * 2) 绝不 import 任何宿主命名空间包：入口静态 import 会在 profile 里解析失败，
 *    导致整个插件加载期抛错、技能全不注册（v1 的真实故障）。
 * 3) 所有方法都「不抛异常」：失败一律折成 {ok:false, blocked|reason, hint}。工具层
 *    再把对象渲染成文本；若这里抛错，模型只能看到堆栈，拿不到可执行的下一步。
 */

import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const VERSION = '3.1.0';
const DEFAULT_TIMEOUT_MS = 120000;
const MAX_CAPTURE_BYTES = 1024 * 1024; // 单次执行 stdout/stderr 上限，防止死循环刷屏

// 策略默认值必须与 data/exec-policy.json 保持一致：文件缺失/损坏时按「全关」处理，
// 绝不因为配置读不到就悄悄放开执行。
const DEFAULT_POLICY = {
  run: {
    enabled: false,
    requireConsent: true,
    allowNetwork: false,
    workdir: '.dsh-research/run',
    timeoutMs: DEFAULT_TIMEOUT_MS,
    maxOutputBytes: MAX_CAPTURE_BYTES,
  },
  runtimes: { r: null, python: null },
  allowedPackages: {
    r: ['base', 'stats', 'survival', 'lme4', 'pROC', 'metafor', 'ggplot2', 'tableone', 'rms', 'survminer'],
    python: ['pandas', 'numpy', 'scipy', 'statsmodels', 'matplotlib', 'sklearn', 'lifelines', 'seaborn'],
  },
  denyPathPatterns: ['patient', '患者', '病历', 'phi', 'idcard', '身份证'],
  notes: '',
};

// 永久拒绝（与 run.enabled / allowNetwork 无关）：装包与破坏性系统命令永远不该由
// 「跑一段分析脚本」触发。
const PERMANENT_DENY = [
  { re: /install\.packages\s*\(/i, detail: 'install.packages 安装 R 包' },
  { re: /\bpip\s+install\b/i, detail: 'pip install 安装 Python 包' },
  { re: /devtools::install/i, detail: 'devtools::install 安装 R 包' },
  { re: /\brm\s+-rf?\b/i, detail: 'rm -rf 递归删除' },
  { re: /\bRemove-Item\b/i, detail: 'PowerShell Remove-Item' },
  { re: /\bformat\s+[a-z]:[\\/]/i, detail: '格式化磁盘（format C:）' },
  { re: /\biwr\s/i, detail: 'Invoke-WebRequest 简写 iwr' },
  { re: /\bInvoke-WebRequest\b/i, detail: 'Invoke-WebRequest 外联下载' },
];

// 网络/外部进程：allowNetwork=false 时一律拒绝（这些动作能把数据发出去、也能拉东西进来）
const NETWORK_DENY_R = [
  { re: /\bsystem\s*\(/, detail: 'R system() 调用外部命令' },
  { re: /\bsystem2\s*\(/, detail: 'R system2() 调用外部命令' },
  { re: /\bdownload\.file\s*\(/, detail: 'R download.file() 联网下载' },
  { re: /\burl\s*\(/, detail: 'R url() 打开网络连接' },
  { re: /\bcurl\b/, detail: 'R curl 联网' },
  { re: /\bwget\b/, detail: 'wget 联网下载' },
];
const NETWORK_DENY_PY = [
  { re: /\brequests\b/, detail: 'Python requests 联网' },
  { re: /\burllib3?\b/, detail: 'Python urllib 联网' },
  { re: /\bhttp\.client\b/, detail: 'Python http.client 联网' },
  { re: /\bsocket\b/, detail: 'Python socket 联网' },
  { re: /\bsubprocess\b/, detail: 'Python subprocess 启动子进程' },
  { re: /\bos\.system\s*\(/, detail: 'Python os.system 执行外部命令' },
  { re: /\bos\.popen\s*\(/, detail: 'Python os.popen 执行外部命令' },
  { re: /\bhttpx\b/, detail: 'Python httpx 联网' },
];

// 写文件调用：只允许写 workdir 内的相对路径；绝对路径、~、.. 一律拒绝。
const WRITE_CALLS_R = [
  /\bwrite\.csv\s*\(/,
  /\bwrite\.csv2\s*\(/,
  /\bwrite\.table\s*\(/,
  /\bwriteLines\s*\(/,
  /\bsaveRDS\s*\(/,
  /\bsave\s*\(/,
  /\bpdf\s*\(/,
  /\bpng\s*\(/,
  /\bjpeg\s*\(/,
  /\btiff\s*\(/,
  /\bsvg\s*\(/,
  /\bsink\s*\(/,
  /\bopen\s*\(/,
];
const WRITE_CALLS_PY = [
  /\bto_csv\s*\(/,
  /\bto_excel\s*\(/,
  /\bto_pickle\s*\(/,
  /\bsavetxt\s*\(/,
  /\bsavefig\s*\(/,
  /\bwrite\s*\(/,
  /\bopen\s*\(/,
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

// 子进程环境：清掉语言/编码变量，避免 R/Python 输出按宿主 locale 变成看不懂的编码。
function cleanEnv() {
  const env = { ...process.env };
  for (const key of ['LC_ALL', 'LANG', 'LANGUAGE']) delete env[key];
  env.R_DEFAULT_INTERNET_TIMEOUT = env.R_DEFAULT_INTERNET_TIMEOUT || '30';
  return env;
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
// 执行策略：data/exec-policy.json（默认全关）→ 内存覆盖（测试用）→ 兜底默认值
// ---------------------------------------------------------------------------

function policyPath() {
  // lib/verify.js → ../data/exec-policy.json。用 fileURLToPath 而不是 import.meta.dirname：
  // dirname 要 Node ≥20.11，engines 虽写 ^22，但少一个 API 依赖少一类现场故障。
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', 'data', 'exec-policy.json');
}

function mergePolicy(base, extra) {
  const out = { ...base };
  for (const [key, value] of Object.entries(extra ?? {})) {
    if (Array.isArray(value)) out[key] = value.slice();
    else if (value && typeof value === 'object') out[key] = mergePolicy(base[key] ?? {}, value);
    else if (value !== undefined) out[key] = value;
  }
  return out;
}

function clampNumber(value, fallback, min, max) {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(max, Math.max(min, Math.floor(n)));
}

function loadPolicy() {
  try {
    const parsed = JSON.parse(readTextFile(policyPath()));
    return { source: policyPath(), error: null, policy: parsed };
  } catch (err) {
    // 配置缺失/损坏一律按「全关」处理：绝不因为读不到策略就悄悄放开执行。
    if (err && err.code === 'ENOENT') return { source: policyPath(), error: null, policy: {} };
    return { source: policyPath(), error: toText(err && err.message ? err.message : String(err)), policy: {} };
  }
}

function resolvePolicy(options = {}) {
  const loaded = loadPolicy();
  const withFile = mergePolicy(DEFAULT_POLICY, loaded.policy);
  const merged = options.policy ? mergePolicy(withFile, options.policy) : withFile;
  if (options.runtimes) merged.runtimes = { ...merged.runtimes, ...options.runtimes };
  merged.run = { ...merged.run };
  merged.run.enabled = merged.run.enabled === true;
  merged.run.allowNetwork = merged.run.allowNetwork === true;
  merged.run.requireConsent = merged.run.requireConsent !== false;
  merged.run.timeoutMs = clampNumber(merged.run.timeoutMs, DEFAULT_TIMEOUT_MS, 1000, 3600000);
  merged.run.maxOutputBytes = clampNumber(merged.run.maxOutputBytes, MAX_CAPTURE_BYTES, 65536, 64 * 1024 * 1024);
  // workdir 必须是相对路径：绝对路径等于把执行半径交给调用方
  const wdRaw = typeof merged.run.workdir === 'string' ? merged.run.workdir.trim() : '';
  merged.run.workdir = wdRaw && !path.isAbsolute(wdRaw) && !wdRaw.split(/[\\/]/).includes('..')
    ? wdRaw
    : DEFAULT_POLICY.run.workdir;
  merged.allowedPackages = {
    r: Array.isArray(merged.allowedPackages?.r)
      ? merged.allowedPackages.r.map((s) => String(s).toLowerCase())
      : DEFAULT_POLICY.allowedPackages.r.slice(),
    python: Array.isArray(merged.allowedPackages?.python)
      ? merged.allowedPackages.python.map((s) => String(s).toLowerCase())
      : DEFAULT_POLICY.allowedPackages.python.slice(),
  };
  merged.denyPathPatterns = Array.isArray(merged.denyPathPatterns)
    ? merged.denyPathPatterns.map((s) => String(s)).filter(Boolean)
    : DEFAULT_POLICY.denyPathPatterns.slice();
  // 测试与「只想看配置里写了什么」的自检可以关掉 PATH 探测；默认开着
  merged.pathProbe = merged.pathProbe !== false;
  return { policy: merged, source: loaded.source, error: loaded.error };
}

function sha256(text) {
  return createHash('sha256').update(String(text), 'utf8').digest('hex');
}

// ---------------------------------------------------------------------------
// 解释器探测：exec-policy → 环境变量 → PATH（不再硬编码任何作者机器路径）
// ---------------------------------------------------------------------------

function pathProbe(kind) {
  // 自己扫 PATH，而不是调 where/which：中文 Windows 上 where 输出是 GBK，按 UTF-8 解码会得到
  // 乱码路径（文件明明在、existsSync 却失败）。PATH 环境变量本身已由 Node 正确解码。
  const names = kind === 'r' ? ['Rscript.exe', 'Rscript'] : ['python.exe', 'python3.exe', 'python', 'python3'];
  const pathVar = process.env.PATH || process.env.Path || '';
  const dirs = pathVar.split(path.delimiter).filter(Boolean);
  const tried = [];
  for (const dir of dirs) {
    for (const name of names) {
      const candidate = path.join(dir, name);
      if (tried.length < 3) tried.push(candidate);
      try {
        if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) return { command: candidate, source: 'path', tried };
      } catch {
        /* 无权限的目录直接跳过 */
      }
    }
  }
  return { command: null, source: null, tried };
}

function envCandidates(kind) {
  const list = [];
  if (kind === 'r') {
    if (process.env.R_HOME) {
      list.push({ command: path.join(process.env.R_HOME, 'bin', process.platform === 'win32' ? 'Rscript.exe' : 'Rscript'), source: 'env:R_HOME' });
      list.push({ command: path.join(process.env.R_HOME, 'Rscript.exe'), source: 'env:R_HOME' });
    }
    if (process.env.RSCRIPT) list.push({ command: process.env.RSCRIPT, source: 'env:RSCRIPT' });
  } else {
    if (process.env.PYTHON) list.push({ command: process.env.PYTHON, source: 'env:PYTHON' });
    if (process.env.CONDA_PREFIX) {
      list.push({
        command: path.join(process.env.CONDA_PREFIX, process.platform === 'win32' ? 'python.exe' : path.join('bin', 'python')),
        source: 'env:CONDA_PREFIX',
      });
    }
  }
  return list;
}

function probeRuntime(kind, configured, policy) {
  const tried = [];
  const hints = kind === 'r'
    ? [
        '在 data/exec-policy.json 的 runtimes.r 里填 Rscript 绝对路径（例如 R_HOME 下的 bin\\Rscript.exe）',
        '设置环境变量 R_HOME 指向 R 安装目录，然后完全退出并重启 DSH Desktop',
        '把 Rscript 所在目录加入 PATH，再重启 DSH Desktop',
      ]
    : [
        '在 data/exec-policy.json 的 runtimes.python 里填 python 绝对路径',
        '设置环境变量 PYTHON 或 CONDA_PREFIX，然后完全退出并重启 DSH Desktop',
        '把 python 所在目录加入 PATH，再重启 DSH Desktop',
      ];
  const candidates = [];
  if (configured) candidates.push({ command: String(configured), source: `exec-policy.runtimes.${kind}` });
  candidates.push(...envCandidates(kind));
  for (const candidate of candidates) {
    if (tried.length < 3) tried.push(candidate.command);
    try {
      if (candidate.command && fs.existsSync(candidate.command)) {
        return { ok: true, kind, command: candidate.command, source: candidate.source, tried };
      }
    } catch {
      /* 路径含非法字符时 existsSync 也可能抛：当作不存在 */
    }
  }
  const fromPath = policy && policy.pathProbe === false ? { command: null, tried: [] } : pathProbe(kind);
  for (const p of fromPath.tried) if (tried.length < 3) tried.push(p);
  if (fromPath.command) return { ok: true, kind, command: fromPath.command, source: fromPath.source, tried };
  return { ok: false, kind, reason: 'runtime_missing', tried, hints };
}

export function detectRuntime(kind, policy) {
  const k = kind === 'r' ? 'r' : 'python';
  const effective = policy ?? resolvePolicy().policy;
  const configured = effective.runtimes ? effective.runtimes[k] : null;
  return probeRuntime(k, configured, effective);
}

export function detectRuntimes(policy) {
  const effective = policy ?? resolvePolicy().policy;
  return { r: detectRuntime('r', effective), python: detectRuntime('python', effective) };
}

// ---------------------------------------------------------------------------
// workdir 与脚本静态扫描（正向约束：白名单 + 写半径 + PHI）
// ---------------------------------------------------------------------------

function validateWorkdir(raw) {
  if (raw === undefined || raw === null || String(raw).trim() === '') return { ok: true, sub: '' };
  const value = String(raw).trim();
  if (path.isAbsolute(value)) return { ok: false, detail: `workdir 不允许绝对路径：${value}` };
  const parts = value.split(/[\\/]+/).filter(Boolean);
  if (parts.includes('..')) return { ok: false, detail: `workdir 不允许包含 ..：${value}` };
  return { ok: true, sub: parts.join(path.sep) };
}

function lineOfIndex(code, index) {
  let line = 1;
  for (let i = 0; i < index && i < String(code).length; i += 1) if (code[i] === '\n') line += 1;
  return line;
}

function scanScript({ kind, code, policy }) {
  const violations = [];
  const text = String(code ?? '');
  const lines = text.split(/\r?\n/);
  const add = (violationKind, detail, line) => {
    if (violations.length >= 50) return; // 上限：坏脚本可能每行都违规，没必要全量回吐
    violations.push({ kind: violationKind, detail, line: Math.max(1, Math.floor(Number(line) || 0)) });
  };

  // 1) 安装/破坏性命令：永久拒绝，与 enabled 无关
  lines.forEach((line, idx) => {
    for (const rule of PERMANENT_DENY) if (rule.re.test(line)) add('permanent_deny', rule.detail, idx + 1);
  });

  // 2) 包白名单：只允许 policy 里列出的包（R 取 library/require/requireNamespace 与 pkg::，
  //    Python 取 import 与 from ... import 的根包名）
  const allowed = new Set(kind === 'r' ? policy.allowedPackages.r : policy.allowedPackages.python);
  if (kind === 'r') {
    const libRe = /\b(?:library|require|requireNamespace)\s*\(\s*(?:package\s*=\s*)?(?:["']([A-Za-z0-9._]+)["']|([A-Za-z][A-Za-z0-9._]*))/g;
    let m;
    while ((m = libRe.exec(text))) {
      const name = String(m[1] || m[2] || '').trim();
      if (!name) continue;
      const pkg = name.toLowerCase();
      if (!allowed.has(pkg)) add('package_not_allowed', `R 包 ${name} 不在白名单（allowedPackages.r）`, lineOfIndex(text, m.index));
    }
    const nsRe = /\b([A-Za-z][A-Za-z0-9._]*)::/g;
    while ((m = nsRe.exec(text))) {
      const pkg = String(m[1]).toLowerCase();
      if (!allowed.has(pkg)) add('package_not_allowed', `R 包 ${m[1]} 不在白名单（allowedPackages.r）`, lineOfIndex(text, m.index));
    }
  } else {
    const importRe = /^[ \t]*import[ \t]+([^\n#]+)/gm;
    let m;
    while ((m = importRe.exec(text))) {
      for (const part of String(m[1]).split(',')) {
        const name = part.trim().split(/\s+as\s+/)[0].trim();
        if (!name) continue;
        const root = name.split('.')[0].toLowerCase();
        if (root !== '__future__' && !allowed.has(root)) add('package_not_allowed', `Python 包 ${root} 不在白名单（allowedPackages.python）`, lineOfIndex(text, m.index));
      }
    }
    const fromRe = /^[ \t]*from[ \t]+([A-Za-z_][\w.]*)[ \t]+import\b/gm;
    while ((m = fromRe.exec(text))) {
      const root = String(m[1]).split('.')[0].toLowerCase();
      if (root !== '__future__' && !allowed.has(root)) add('package_not_allowed', `Python 包 ${root} 不在白名单（allowedPackages.python）`, lineOfIndex(text, m.index));
    }
  }

  // 3) 网络/子进程调用：allowNetwork=false 时一律拒绝
  if (!policy.run.allowNetwork) {
    const rules = kind === 'r' ? NETWORK_DENY_R : NETWORK_DENY_PY;
    for (const rule of rules) {
      const re = new RegExp(rule.re.source, rule.re.flags.includes('g') ? rule.re.flags : `${rule.re.flags}g`);
      let m;
      while ((m = re.exec(text))) add('network', rule.detail, lineOfIndex(text, m.index));
    }
  }

  // 4) 写文件：只允许 workdir 内的相对路径；绝对路径、~、.. 一律拒绝
  const writeCalls = kind === 'r' ? WRITE_CALLS_R : WRITE_CALLS_PY;
  for (const callRe of writeCalls) {
    const re = new RegExp(callRe.source, 'g');
    let m;
    while ((m = re.exec(text))) {
      const open = text.indexOf('(', m.index);
      const chunk = text.slice(open, Math.min(text.length, open + 260));
      // open(...) 只拦写模式：open("x.csv") 读文件是正常分析脚本
      if (callRe.source.includes('open')) {
        const modeMatch = /['"]([rwa][b+t]?|rb\+?|wb\+?|ab\+?)['"]/i.exec(chunk);
        const mode = modeMatch ? modeMatch[1].toLowerCase() : '';
        if (!mode || mode.startsWith('r')) continue;
      }
      // 收集这一段里的全部引号字面量：写调用的参数顺序各不相同（writeLines 内容在前、路径在后；
      // pdf/png 路径在前），只取第一个会拿「内容字符串」当路径，漏掉真正的落点。
      const literals = [...chunk.matchAll(/['"]([^'"]{1,220})['"]/g)].map((x) => x[1].trim()).filter(Boolean);
      // open(...) 只拦写模式：open("x.csv") 读文件是正常分析脚本
      if (callRe.source.includes('open')) {
        const modeLiteral = literals.find((v) => /^[rwax][b+]*$/i.test(v)) || '';
        const mode = modeLiteral.toLowerCase();
        if (!mode || mode.startsWith('r')) continue;
      }
      if (!literals.length) {
        add('write_path_dynamic', '写文件的路径是变量/表达式，无法静态确认落点', lineOfIndex(text, m.index));
        continue;
      }
      for (const target of literals) {
        const isAbsolute = /^([A-Za-z]:[\\/]|\\\\|\/|~[\\/])/.test(target);
        const escapes = target.split(/[\\/]+/).includes('..');
        if (isAbsolute || escapes) add('write_path_outside', `写入路径越界：${target}（只允许 workdir 内相对路径）`, lineOfIndex(text, m.index));
      }
    }
  }

  // 5) PHI：脚本里出现敏感路径关键词即拒绝（不做内容脱敏，直接不跑）
  const lower = text.toLowerCase();
  for (const pattern of policy.denyPathPatterns) {
    const needle = String(pattern).toLowerCase();
    if (!needle) continue;
    const at = lower.indexOf(needle);
    if (at >= 0) add('phi_pattern', `脚本包含受保护路径关键词「${pattern}」`, lineOfIndex(text, at));
  }

  return violations;
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

async function runScript(args = {}, runtimeOpts = {}) {
  const startedAt = Date.now();
  const { policy, source: policySource, error: policyError } = resolvePolicy(runtimeOpts);
  const k = String(args.kind ?? '').trim().toLowerCase();
  if (k !== 'r' && k !== 'python') {
    return { ok: false, blocked: true, reason: 'bad_kind', hint: "kind 只能是 'r' 或 'python'" };
  }
  const code = typeof args.code === 'string' ? args.code : '';
  if (!code.trim()) return { ok: false, blocked: true, reason: 'empty_code', hint: 'code 不能为空' };

  const previewHash = sha256(code);
  const wd = validateWorkdir(args.workdir);
  const violations = scanScript({ kind: k, code, policy });
  if (!wd.ok) violations.push({ kind: 'workdir_invalid', detail: wd.detail, line: 0 });

  const totalLines = code.split(/\r?\n/).length;
  const scriptInfo = {
    lines: totalLines,
    totalLines,
    excerpt: code.split(/\r?\n/).slice(0, 60).join('\n'),
    truncated: totalLines > 60,
  };
  const policySummary = {
    enabled: policy.run.enabled,
    allowNetwork: policy.run.allowNetwork,
    workdir: policy.run.workdir,
    timeoutMs: policy.run.timeoutMs,
    maxOutputBytes: policy.run.maxOutputBytes,
    allowedPackages: { r: policy.allowedPackages.r.slice(), python: policy.allowedPackages.python.slice() },
    source: policySource,
    ...(policyError ? { error: policyError } : {}),
  };
  const runtimes = detectRuntimes(policy);
  const runtimeHint = k === 'r'
    ? '先把 R 装好并让 Rscript 能被探测到（位置顺序见 data/exec-policy.json 与 docs/SECURITY.md）'
    : '先把 Python 装好并让 python 能被探测到（位置顺序见 data/exec-policy.json 与 docs/SECURITY.md）';

  // 第一段：不传 confirm:true 就只回预览——绝不写脚本、绝不 spawn、绝不 mkdir
  if (args.confirm !== true) {
    const blocked = violations.length > 0;
    return {
      ok: false,
      preview: true,
      blocked,
      kind: k,
      previewHash,
      script: scriptInfo,
      policy: policySummary,
      violations,
      reason: blocked ? 'policy_violation' : (!policy.run.enabled ? 'exec_disabled' : null),
      hint: blocked
        ? '有预计拦截项：修正脚本后重新预览；确认后传 confirm:true 且 previewHash 一致才会执行'
        : (!policy.run.enabled
          ? '执行默认关闭：在 data/exec-policy.json 把 run.enabled 改为 true 后再调用；开启意味着脚本以你的用户权限运行'
          : '预览不执行。核对脚本与 previewHash 后，传 confirm:true 与同一个 previewHash 才会执行'),
      runtimes: { r: { ok: runtimes.r.ok }, python: { ok: runtimes.python.ok } },
    };
  }

  // 第二段：确认执行——哈希、开关、策略三道闸必须全过
  if (typeof args.previewHash !== 'string' || args.previewHash !== previewHash) {
    return {
      ok: false,
      blocked: true,
      preview: false,
      reason: 'preview_mismatch',
      hint: 'previewHash 与当前 code 不一致：预览后代码被改过（或没带哈希）。请重新预览并核对哈希。',
      previewHash,
    };
  }
  if (!policy.run.enabled) {
    return {
      ok: false,
      blocked: true,
      reason: 'exec_disabled',
      hint: '在 data/exec-policy.json 把 run.enabled 改为 true 后再调用；开启意味着脚本以你的用户权限运行',
      policy: policySummary,
    };
  }
  if (violations.length) {
    return { ok: false, blocked: true, reason: 'policy_violation', violations, hint: '命中执行策略，脚本未运行' };
  }

  const runtime = k === 'r' ? runtimes.r : runtimes.python;
  if (!runtime.ok) {
    return { ok: false, blocked: true, reason: 'runtime_missing', tried: runtime.tried, hints: runtime.hints, hint: runtimeHint };
  }

  // 执行半径：<cwd>/<policy.run.workdir>/<runId>；不再接受 cwd 或系统临时目录
  const runRoot = path.resolve(process.cwd(), policy.run.workdir);
  const runId = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  const runDir = path.resolve(runRoot, runId, wd.sub);
  if (!(runDir === runRoot || isInside(runRoot, runDir))) {
    return { ok: false, blocked: true, reason: 'workdir_invalid', hint: '解析后的 workdir 越出执行目录' };
  }
  try {
    fs.mkdirSync(runDir, { recursive: true });
  } catch (err) {
    return {
      ok: false,
      blocked: true,
      reason: 'workdir_invalid',
      hint: `无法创建执行目录：${toText(err && err.message ? err.message : String(err))}`,
    };
  }

  const ext = k === 'r' ? 'R' : 'py';
  const script = path.join(runDir, `script-${runId}.${ext}`);
  fs.writeFileSync(script, code, 'utf8'); // 无 BOM：R/Python 带 BOM 的解释器会在首行报语法错

  // 快照放在脚本写入之后：脚本文件本身不算「执行产生的文件」，减少噪音
  const before = snapshotTree(runDir);
  const timeout = Math.min(
    policy.run.timeoutMs,
    Number.isFinite(Number(args.timeoutMs)) && Number(args.timeoutMs) > 0
      ? Math.max(1000, Number(args.timeoutMs))
      : policy.run.timeoutMs,
  );
  const res = spawnSync(runtime.command, [script], {
    cwd: runDir,
    env: cleanEnv(),
    encoding: 'utf8',
    timeout,
    windowsHide: true,
    maxBuffer: policy.run.maxOutputBytes,
  });
  const after = snapshotTree(runDir);
  const files = diffTree(before.files, after.files);
  const command = quoteCmd(runtime.command, script);
  const durationMs = Date.now() - startedAt;
  const base = { kind: k, script, command, runId, workdir: runDir, previewHash, policy: { path: policySource } };

  if (res.error) {
    const codeName = res.error.code;
    if (codeName === 'ENOENT') {
      return { ok: false, blocked: true, reason: 'runtime_missing', tried: runtime.tried, hints: runtime.hints, hint: runtimeHint, ...base };
    }
    if (codeName === 'EPERM' || codeName === 'EACCES') {
      return {
        ok: false,
        blocked: true,
        reason: 'spawn_blocked',
        hint: '宿主未允许子进程，请用宿主的 shell 工具跑返回的 command',
        ...base,
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
        files,
        durationMs,
        ...base,
      };
    }
    return { ok: false, reason: 'spawn_failed', hint: String(res.error.message ?? res.error), ...base };
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
    runId,
    workdir: runDir,
    files,
    durationMs,
    previewHash,
    policy: { path: policySource },
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
    // 绑定 options：测试可用 options.policy 打开执行开关、用 options.runtimes 指定不存在的解释器
    runScript: (args, runtime) => runScript(args, runtime ?? options),
    checkData,
    checkOutputs,
    // 在这里绑定 options：checkDois 需要注入 fetchImpl，而模块级函数不能直接读工厂参数
    checkDois: (args, runtime) => checkDois(args, runtime ?? options),
    auditRefs,
    // 策略与解释器探测：research_suite_status 用它报「本机默认关、能探测到什么解释器」
    policy: () => resolvePolicy(options).policy,
    detectRuntimes: () => detectRuntimes(resolvePolicy(options).policy),
    version: VERSION,
  };
}
