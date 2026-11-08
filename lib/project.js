// lib/project.js
// v3.2.0 项目级记忆：把「这个项目已经定过的术语、目标期刊、排版口径、定稿段落」落成一个
// 本地档案，供后续会话读取，避免每次从零重问。
//
// 设计约束（写代码前先钉死，改实现时不要破）：
// 1. 零依赖：只用 node:fs / node:path / node:crypto，不引入任何第三方包，也不 import 本包其它模块。
// 2. 只碰一个文件：<root>/.dsh-research/project.json。不动用户目录里的其它任何东西。
// 3. 坏档只备份不销毁：JSON 解析失败时复制为 project.json.bak，原文件保持不动，调用方自己决定怎么修。
// 4. 写盘原子：先写同目录下的临时文件，再 fs.renameSync 覆盖；任何失败都清掉临时文件，不留半截档案。
// 5. 全部方法返回 {ok, ...} 且不抛异常：读写失败一律折成 {ok:false, reason}，调用方按字段分支即可。
// 6. 路径不越界：档案路径必须落在 root 之内；options.project 里带 ../ 或绝对路径时直接拒绝，
//    这样「多项目」模式不会因为一个项目名把写入引到别处。

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

/** 档案格式版本。结构不兼容变更时 +1，并在 normalizeProject 里写迁移分支。 */
export const SCHEMA_VERSION = 1;

/** 档案目录名与文件名（相对项目根）。 */
export const ARCHIVE_DIR = '.dsh-research';
export const ARCHIVE_FILE = 'project.json';

/** list() 最多枚举多少个项目，防止在一个巨型工作区里扫出上千条。 */
export const MAX_PROJECTS = 50;

/** 追加语义的三组列表，以及各自的去重键。 */
export const SEQUENCE_KEYS = Object.freeze({
  terms: 'zh',
  decisions: 'what',
  sections: 'name',
});

/** style 支持的字段与类型。写错字段名比写错值更难发现，所以未知字段也报 invalid。 */
const STYLE_FIELDS = Object.freeze({
  citation: 'string',
  superscript: 'boolean',
  language: 'string',
  unitStyle: 'string',
});

/** 三组列表各自允许的字段。未知字段一律报 invalid，避免拼错 key 静默丢失。 */
const LIST_FIELDS = Object.freeze({
  terms: ['zh', 'en', 'abbr', 'firstUse', 'note'],
  decisions: ['date', 'what', 'why', 'by'],
  sections: ['name', 'status', 'hash', 'note', 'text'],
});

/** 顶层允许出现的字段（其余字段放行但要求可 JSON 序列化）。 */
const TOP_FIELDS = ['schemaVersion', 'project', 'targetJournal', 'style', 'terms', 'decisions', 'sections', 'updatedAt'];

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;

// ---------------------------------------------------------------------------
// 基础判定
// ---------------------------------------------------------------------------

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

/** 去掉 .dsh-research 与常见噪声目录，其余子目录都当候选项目根参与 list() 扫描。 */
const SKIP_SUBDIR = new Set([ARCHIVE_DIR, 'node_modules', '.git', '.cache', 'dist', 'build', '__pycache__']);

function resolveRoot(options) {
  const raw = options && typeof options.root === 'string' && options.root.trim() ? options.root : process.cwd();
  return path.resolve(raw);
}

/**
 * 拼档案路径。options.project 为空时就是 <root>/.dsh-research/project.json；
 * 给了项目子目录名时是 <root>/<project>/.dsh-research/project.json（多项目工作区）。
 */
function resolveArchivePath(root, options) {
  const sub = options && typeof options.project === 'string' ? options.project.trim() : '';
  if (!sub) return path.join(root, ARCHIVE_DIR, ARCHIVE_FILE);
  return path.join(root, sub, ARCHIVE_DIR, ARCHIVE_FILE);
}

/** 判断 target 是否落在 root 之内（含 root 自身）。 */
function isInside(root, target) {
  const rel = path.relative(root, target);
  return rel === '' || (!rel.startsWith('..') && !path.isAbsolute(rel));
}

function emptyProject() {
  return {
    schemaVersion: SCHEMA_VERSION,
    project: null,
    targetJournal: null,
    style: {},
    terms: [],
    decisions: [],
    sections: [],
    updatedAt: null,
  };
}

/** 补齐缺字段、纠正 schemaVersion；不做类型强转（类型问题在写入前已经拦过）。 */
function normalizeProject(raw) {
  const out = isPlainObject(raw) ? { ...raw } : {};
  out.schemaVersion = SCHEMA_VERSION;
  if (!isPlainObject(out.style)) out.style = {};
  for (const field of Object.keys(SEQUENCE_KEYS)) {
    if (!Array.isArray(out[field])) out[field] = [];
  }
  if (typeof out.updatedAt !== 'string' || !out.updatedAt) out.updatedAt = null;
  return out;
}

function nextTimestamp(prev) {
  let t = Date.now();
  const p = typeof prev === 'string' ? Date.parse(prev) : NaN;
  if (Number.isFinite(p) && t <= p) t = p + 1;
  return new Date(t).toISOString();
}

/** 段落哈希：sections[].text 传原文进来时自动算，正文本身不入档（避免档案里囤长文本）。 */
export function hashText(text) {
  const digest = crypto.createHash('sha256').update(String(text ?? ''), 'utf8').digest('hex');
  return `sha256:${digest}`;
}

// ---------------------------------------------------------------------------
// 校验
// ---------------------------------------------------------------------------

function validatePatch(patch) {
  const issues = [];
  const push = (at, message) => issues.push({ path: at, message });

  if (!isPlainObject(patch)) {
    push('', 'patch 必须是一个对象');
    return { issues };
  }

  for (const key of ['project', 'targetJournal']) {
    if (key in patch && patch[key] !== null && typeof patch[key] !== 'string') {
      push(key, `${key} 必须是字符串或 null`);
    }
  }

  if ('style' in patch) {
    if (!isPlainObject(patch.style)) {
      push('style', 'style 必须是对象');
    } else {
      for (const [key, value] of Object.entries(patch.style)) {
        const expected = STYLE_FIELDS[key];
        if (!expected) {
          push(`style.${key}`, `style 不支持字段 ${key}`);
        } else if (typeof value !== expected) {
          push(`style.${key}`, `style.${key} 必须是 ${expected}`);
        }
      }
    }
  }

  for (const [field, key] of Object.entries(SEQUENCE_KEYS)) {
    if (!(field in patch)) continue;
    const list = patch[field];
    if (!Array.isArray(list)) {
      push(field, `${field} 必须是数组`);
      continue;
    }
    const allowed = LIST_FIELDS[field];
    list.forEach((item, index) => {
      const at = `${field}[${index}]`;
      if (!isPlainObject(item)) {
        push(at, '条目必须是对象');
        return;
      }
      if (typeof item[key] !== 'string' || !item[key].trim()) {
        push(`${at}.${key}`, `${key} 必须是非空字符串`);
      }
      for (const name of Object.keys(item)) {
        if (!allowed.includes(name)) {
          push(`${at}.${name}`, `${field} 不支持字段 ${name}`);
        } else if (name !== key && typeof item[name] !== 'string') {
          push(`${at}.${name}`, `${name} 必须是字符串`);
        }
      }
      if (field === 'decisions') {
        if (typeof item.date !== 'string') push(`${at}.date`, 'date 必须是 YYYY-MM-DD 字符串');
        else if (!DATE_RE.test(item.date)) push(`${at}.date`, `date 格式应为 YYYY-MM-DD，实际 ${item.date}`);
      }
    });
  }

  for (const key of Object.keys(patch)) {
    if (TOP_FIELDS.includes(key)) continue;
    try {
      JSON.stringify(patch[key]);
    } catch {
      push(key, `${key} 无法序列化为 JSON`);
    }
  }

  return { issues };
}

// ---------------------------------------------------------------------------
// 追加合并
// ---------------------------------------------------------------------------

function mergeSequence(current, incoming, key, field) {
  const out = Array.isArray(current) ? current.map((item) => ({ ...item })) : [];
  const index = new Map(out.map((item, i) => [String(item?.[key] ?? ''), i]));
  for (const raw of incoming) {
    const item = { ...raw };
    if (field === 'sections' && typeof item.text === 'string') {
      if (typeof item.hash !== 'string' || !item.hash) item.hash = hashText(item.text);
      delete item.text;
    }
    const id = String(item[key]);
    if (index.has(id)) {
      const at = index.get(id);
      out[at] = { ...out[at], ...item };
    } else {
      index.set(id, out.length);
      out.push(item);
    }
  }
  return out;
}

function mergeProject(base, patch) {
  const out = { ...base };
  for (const [key, value] of Object.entries(patch)) {
    if (key === 'schemaVersion' || key === 'updatedAt') continue;
    const dedupeKey = SEQUENCE_KEYS[key];
    if (dedupeKey) out[key] = mergeSequence(base[key], value, dedupeKey, key);
    else out[key] = value;
  }
  return out;
}

// ---------------------------------------------------------------------------
// 原子写
// ---------------------------------------------------------------------------

function writeAtomic(file, text) {
  const dir = path.dirname(file);
  fs.mkdirSync(dir, { recursive: true });
  const tmp = path.join(dir, `.project-${process.pid}-${crypto.randomBytes(6).toString('hex')}.tmp`);
  try {
    fs.writeFileSync(tmp, text, 'utf8');
    fs.renameSync(tmp, file);
  } catch (err) {
    try {
      fs.rmSync(tmp, { force: true });
    } catch {
      /* 清理失败不掩盖原始错误 */
    }
    throw err;
  }
}

// ---------------------------------------------------------------------------
// 档案读写
// ---------------------------------------------------------------------------

/**
 * 读档案，区分三种状态：
 * - { outside: true }          档案路径越出 root
 * - { exists: false }          没有档案（不创建目录与文件）
 * - { corrupt: true, backup }  JSON 坏了；坏文件已复制为 .bak，原文件不动
 * - { exists: true, project }  正常
 */
function readArchive(file, root) {
  if (!isInside(root, file)) return { outside: true };
  if (!fs.existsSync(file)) return { exists: false, project: null };

  let raw;
  try {
    raw = fs.readFileSync(file, 'utf8');
  } catch (err) {
    return { ioError: String(err?.message ?? err) };
  }

  try {
    const parsed = JSON.parse(raw);
    if (!isPlainObject(parsed)) throw new Error('档案顶层必须是对象');
    return { exists: true, project: normalizeProject(parsed) };
  } catch (err) {
    const backup = `${file}.bak`;
    let backupOk = false;
    try {
      fs.copyFileSync(file, backup);
      backupOk = true;
    } catch {
      backupOk = false;
    }
    return {
      corrupt: true,
      backup: backupOk ? backup : null,
      message: String(err?.message ?? err),
    };
  }
}

// ---------------------------------------------------------------------------
// diff：扁平化成 JSON 路径再比较
// ---------------------------------------------------------------------------

const META_KEYS = new Set(['schemaVersion', 'updatedAt']);

function identifyKey(value) {
  if (!Array.isArray(value) || value.length === 0) return null;
  if (!value.every((item) => isPlainObject(item))) return null;
  for (const key of Object.values(SEQUENCE_KEYS)) {
    if (value.every((item) => typeof item[key] === 'string' && item[key].trim())) return key;
  }
  return null;
}

function flatten(value, base, out) {
  if (Array.isArray(value)) {
    if (value.length === 0) {
      if (base) out.set(base, '[]');
      return out;
    }
    const idKey = identifyKey(value);
    value.forEach((item, index) => {
      const id = idKey ? String(item[idKey]) : String(index);
      const childBase = base ? `${base}[${id}]` : `[${id}]`;
      if (isPlainObject(item) || Array.isArray(item)) flatten(item, childBase, out);
      else out.set(childBase, item);
    });
    return out;
  }
  if (isPlainObject(value)) {
    for (const [key, child] of Object.entries(value)) {
      if (!base && META_KEYS.has(key)) continue;
      const childBase = base ? `${base}.${key}` : key;
      if (isPlainObject(child) || Array.isArray(child)) flatten(child, childBase, out);
      else out.set(childBase, child);
    }
    return out;
  }
  if (base) out.set(base, value);
  return out;
}

function sameValue(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

/**
 * diff 前先抹掉「未设置」的噪声：null 与空数组都表示这个字段没填过，
 * 否则一份档案 vs 一份 patch 会冒出一堆 `project: removed` 之类的假差异。
 */
function stripEmpty(map) {
  for (const [key, value] of map) {
    if (value === null || value === '' || value === '[]') map.delete(key);
  }
  return map;
}

function readOther(other) {
  if (isPlainObject(other)) return { ok: true, project: normalizeProject(other) };
  if (typeof other !== 'string' || !other.trim()) {
    return { ok: false, issues: [{ path: '', message: 'diff 需要对象或档案文件路径' }] };
  }
  const candidate = path.resolve(other);
  if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
    try {
      const parsed = JSON.parse(fs.readFileSync(candidate, 'utf8'));
      if (!isPlainObject(parsed)) return { ok: false, issues: [{ path: '', message: '文件顶层不是对象' }] };
      return { ok: true, project: normalizeProject(parsed) };
    } catch (err) {
      return { ok: false, issues: [{ path: '', message: `无法解析 ${candidate}：${String(err?.message ?? err)}` }] };
    }
  }
  try {
    const parsed = JSON.parse(other);
    if (!isPlainObject(parsed)) return { ok: false, issues: [{ path: '', message: '传入的 JSON 顶层不是对象' }] };
    return { ok: true, project: normalizeProject(parsed) };
  } catch {
    return { ok: false, issues: [{ path: '', message: `既不是存在的文件，也不是合法 JSON：${other.slice(0, 80)}` }] };
  }
}

// ---------------------------------------------------------------------------
// 术语命中
// ---------------------------------------------------------------------------

function escapeRegExp(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * en / abbr 用「非字母数字边界」匹配：EHS 不该在 EHSS 里命中，A 也不该在任意单词中间命中。
 * zh 直接子串匹配——中文没有词边界，加边界反而漏。
 */
function formMatches(text, needle, form) {
  if (form === 'zh') return text.includes(needle);
  const re = new RegExp(`(^|[^A-Za-z0-9])${escapeRegExp(needle)}($|[^A-Za-z0-9])`, 'i');
  return re.test(text);
}

/**
 * 找出在 text 里出现过的术语。每条返回 {term, matchedForm, matchedBy, firstUse}：
 * - term：terms 里的原对象（拿得到 abbr、note）
 * - matchedForm：实际命中的那个写法（中文形 / 英文形 / 缩写）
 * - matchedBy：命中的字段名 'zh' | 'en' | 'abbr'
 * - firstUse：该术语登记的首现位置，用于提示「已定义于 X 段，此处不必再解释」
 */
export function findTerm(project, value) {
  if (!isPlainObject(project) || typeof value !== 'string' || !value) return [];
  const terms = Array.isArray(project.terms) ? project.terms : [];
  const found = [];
  for (const term of terms) {
    if (!isPlainObject(term)) continue;
    for (const form of ['zh', 'en', 'abbr']) {
      const needle = term[form];
      if (typeof needle !== 'string' || !needle.trim()) continue;
      if (!formMatches(value, needle, form)) continue;
      found.push({
        term,
        matchedForm: needle,
        matchedBy: form,
        firstUse: typeof term.firstUse === 'string' ? term.firstUse : '',
      });
      break;
    }
  }
  return found;
}

// ---------------------------------------------------------------------------
// 对外工厂
// ---------------------------------------------------------------------------

/**
 * 创建项目记忆句柄。
 * @param {object} core  宿主核心对象。当前实现只用它占位（后续若要写日志/遥测从这里拿），不读取其内部状态。
 * @param {{root?: string, project?: string}} [options]
 *        root：工作区根，默认 process.cwd()；project：多项目模式下的项目子目录名。
 * @returns {{path: string, root: string, get: Function, set: Function, diff: Function, list: Function}}
 */
export function createProject(core, options = {}) {
  const root = resolveRoot(options);
  const file = resolveArchivePath(root, options);
  const handle = { root, path: file, core };

  const outside = () => ({ ok: false, reason: 'outside', path: file, root });

  /** 读取档案。不存在时返回 exists:false（不创建任何目录/文件）。 */
  handle.get = function get() {
    const result = readArchive(file, root);
    if (result.outside) return outside();
    if (result.ioError) return { ok: false, reason: 'io', path: file, message: result.ioError };
    if (result.corrupt) {
      return { ok: false, reason: 'corrupt', path: file, backup: result.backup, message: result.message };
    }
    if (!result.exists) return { ok: true, exists: false, project: null, path: file };
    return { ok: true, exists: true, project: result.project, path: file };
  };

  /**
   * 浅合并顶层字段；terms / decisions / sections 追加（同键更新）；原子写盘。
   * @returns {{ok:true, project:object, path:string, created:boolean}
   *          | {ok:false, reason:'invalid', issues:Array<{path:string,message:string}>}
   *          | {ok:false, reason:'corrupt'|'outside'|'io'|'schema', ...}}
   */
  handle.set = function set(patch) {
    const { issues } = validatePatch(patch);
    if (issues.length > 0) return { ok: false, reason: 'invalid', issues, path: file };

    const result = readArchive(file, root);
    if (result.outside) return outside();
    if (result.ioError) return { ok: false, reason: 'io', path: file, message: result.ioError };
    if (result.corrupt) {
      return { ok: false, reason: 'corrupt', path: file, backup: result.backup, message: result.message };
    }

    const base = result.project ? normalizeProject(result.project) : emptyProject();
    const merged = mergeProject(base, patch);
    merged.schemaVersion = SCHEMA_VERSION;
    merged.updatedAt = nextTimestamp(base.updatedAt);

    try {
      writeAtomic(file, `${JSON.stringify(merged, null, 2)}\n`);
    } catch (err) {
      return { ok: false, reason: 'io', path: file, message: String(err?.message ?? err) };
    }

    return { ok: true, project: merged, path: file, created: !result.exists };
  };

  /**
   * 与另一个 patch 或档案文件比较。
   * @returns {{ok:true, added:string[], changed:string[], removed:string[], path:string}}
   *          | {ok:false, reason:'outside'|'corrupt'|'invalid', ...}
   */
  handle.diff = function diff(other) {
    const selfResult = readArchive(file, root);
    if (selfResult.outside) return outside();
    if (selfResult.corrupt) {
      return { ok: false, reason: 'corrupt', path: file, backup: selfResult.backup, message: selfResult.message };
    }
    const otherResult = readOther(other);
    if (!otherResult.ok) return { ok: false, reason: 'invalid', issues: otherResult.issues, path: file };

    const current = selfResult.project ?? emptyProject();
    const left = stripEmpty(flatten(current, '', new Map()));
    const right = stripEmpty(flatten(otherResult.project, '', new Map()));
    const added = [];
    const changed = [];
    const removed = [];
    for (const [key, value] of right) {
      if (!left.has(key)) added.push(key);
      else if (!sameValue(left.get(key), value)) changed.push(key);
    }
    for (const key of left.keys()) {
      if (!right.has(key)) removed.push(key);
    }
    added.sort();
    changed.sort();
    removed.sort();
    return { ok: true, added, changed, removed, path: file };
  };

  /**
   * 枚举工作区里的项目档案：root 自身 + 一级子目录，最多 MAX_PROJECTS 个。
   * 坏档跳过（不阻断枚举），返回项里给 path 以便调用方自行修复。
   * @returns {{ok:true, root:string, projects:Array<object>, scanned:number}}
   */
  handle.list = function list() {
    const found = [];
    const seen = new Set();
    const candidates = [root];
    let entries = [];
    try {
      entries = fs.readdirSync(root, { withFileTypes: true });
    } catch {
      entries = [];
    }
    for (const entry of entries) {
      if (found.length >= MAX_PROJECTS) break;
      if (!entry.isDirectory() || SKIP_SUBDIR.has(entry.name) || entry.name.startsWith('.')) continue;
      candidates.push(path.join(root, entry.name));
    }

    for (const dir of candidates) {
      if (found.length >= MAX_PROJECTS) break;
      const candidate = path.join(dir, ARCHIVE_DIR, ARCHIVE_FILE);
      if (!isInside(root, candidate) || seen.has(candidate)) continue;
      seen.add(candidate);
      let parsed;
      try {
        if (!fs.existsSync(candidate) || !fs.statSync(candidate).isFile()) continue;
        parsed = JSON.parse(fs.readFileSync(candidate, 'utf8'));
      } catch {
        continue;
      }
      if (!isPlainObject(parsed)) continue;
      found.push({
        project: typeof parsed.project === 'string' ? parsed.project : null,
        targetJournal: typeof parsed.targetJournal === 'string' ? parsed.targetJournal : null,
        updatedAt: typeof parsed.updatedAt === 'string' ? parsed.updatedAt : null,
        path: candidate,
        root: dir,
      });
    }

    return { ok: true, root, projects: found, scanned: candidates.length };
  };

  return handle;
}

export default createProject;
