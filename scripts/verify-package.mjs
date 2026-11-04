#!/usr/bin/env node
/**
 * verify-package.mjs —— dsh-research-suite 发布前静态校验（不联网、不调 npm）
 *
 * 用法：
 *   node scripts/verify-package.mjs
 *
 * 退出码：0 = 无 ERROR；1 = 至少一条 ERROR。
 * 覆盖：
 *   A. package.json 必填字段 / files 白名单实际存在性 / main 文件存在
 *   B. cordis.patch.yml 结构与 id、name 两行
 *   C. 入口禁止静态或动态 import '@deepseek-ai/*'（profile 里解析不到 → 技能全不注册）
 *   D. skills/*.md frontmatter（name kebab-case、description ≤500 字符）、UTF-8 无 BOM、
 *      与 data/capabilities/*.json 的 skill 字段一一对应
 *   E. data/**.json 与 knowledge/**.json 全部可解析；catalog 里每个 file 真实存在
 *   F. package.json.version = CHANGELOG 最新条目 = data/capabilities/*.json 的 version
 *   G. references/ 编号连续；docs/ 无空文件；包体积与文件数统计
 *
 * `npm pack --dry-run` 由 CI 单独跑，本脚本不调用 npm。
 */

import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');

const PKG_FILE = 'package.json';
const PATCH_FILE = 'cordis.patch.yml';
const CHANGELOG = 'CHANGELOG.md';
const CAP_DIR = path.join(ROOT, 'data', 'capabilities');
const CATALOG = path.join(ROOT, 'knowledge', 'catalog.json');

/** 必须出现在 package.json.files 里的条目（用户/发布契约） */
const REQUIRED_FILES = [
  'lib', 'data', 'skills', 'knowledge', 'references', 'scripts',
  'docs', 'cordis.patch.yml', 'README.md', 'CHANGELOG.md', 'LICENSE', 'icon.svg',
];

/** 权威 engines（dsh 0.2.1-rc.5 环境给定） */
const EXPECT_ENGINES = { node: '^22.19.0 || >=24.0.0', dsh: '>=0.2.0-0 <0.3.0' };

const PLUGIN_ID = 'dsh-research-suite';

// ---------- 工具 ----------

const len = (s) => [...String(s)].length;
const isNonEmptyStr = (v) => typeof v === 'string' && v.trim() !== '';
const rel = (abs) => path.relative(ROOT, abs).replaceAll('\\', '/');
const stripBom = (s) => (s.charCodeAt(0) === 0xfeff ? s.slice(1) : s);
const clip = (s, n = 30) => (len(s) > n ? [...s].slice(0, n).join('') + '…' : s);
const describeType = (v) => (v === null ? 'null' : Array.isArray(v) ? 'array' : typeof v);

class Report {
  constructor() { this.items = []; }
  error(where, msg) { this.items.push({ level: 'ERROR', where, msg }); }
  warn(where, msg) { this.items.push({ level: 'WARN', where, msg }); }
  info(where, msg) { this.items.push({ level: 'INFO', where, msg }); }
  get errors() { return this.items.filter((i) => i.level === 'ERROR'); }
  get warns() { return this.items.filter((i) => i.level === 'WARN'); }
}

/** 递归列出文件（跳过 node_modules / .git），返回绝对路径数组 */
function walk(dir, out = [], skip = new Set(['node_modules', '.git'])) {
  if (!existsSync(dir)) return out;
  for (const name of readdirSync(dir)) {
    if (skip.has(name)) continue;
    const abs = path.join(dir, name);
    const st = statSync(abs);
    if (st.isDirectory()) walk(abs, out, skip);
    else out.push(abs);
  }
  return out;
}

/** 宽松读取：返回 {text, bytes, bom, utf8Ok} */
function readText(abs) {
  const buf = readFileSync(abs);
  const bom = buf.length >= 3 && buf[0] === 0xef && buf[1] === 0xbb && buf[2] === 0xbf;
  let text = '';
  let utf8Ok = true;
  try {
    text = new TextDecoder('utf-8', { fatal: true }).decode(buf);
  } catch {
    utf8Ok = false;
    text = buf.toString('utf8');
  }
  return { text, bytes: buf.length, bom, utf8Ok };
}

// ---------- A. package.json ----------

function checkPackageJson(report) {
  const abs = path.join(ROOT, PKG_FILE);
  if (!existsSync(abs)) {
    report.error(PKG_FILE, '文件不存在（入口与发布清单都从这里读）');
    return null;
  }
  const { text, bom, utf8Ok } = readText(abs);
  if (bom) report.error(PKG_FILE, '带 UTF-8 BOM，建议无 BOM');
  if (!utf8Ok) report.error(PKG_FILE, '不是合法 UTF-8');
  let pkg;
  try {
    pkg = JSON.parse(stripBom(text));
  } catch (e) {
    report.error(PKG_FILE, `JSON 解析失败：${e.message}`);
    return null;
  }
  const need = ['name', 'version', 'description', 'type', 'main', 'license', 'engines', 'files', 'dsh'];
  for (const k of need) {
    if (pkg[k] === undefined || pkg[k] === null || pkg[k] === '') report.error(PKG_FILE, `缺少必填字段 ${k}`);
  }
  if (pkg.name !== PLUGIN_ID) {
    report.error(PKG_FILE, `name 应为 "${PLUGIN_ID}"，实际 ${JSON.stringify(pkg.name)}`);
  }
  if (pkg.version !== undefined && !/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/.test(String(pkg.version))) {
    report.error(PKG_FILE, `version 不是 semver：${JSON.stringify(pkg.version)}`);
  }
  if (pkg.type !== 'module') {
    report.error(PKG_FILE, `type 必须是 "module"（cordis 插件入口是 ESM），实际 ${JSON.stringify(pkg.type)}`);
  }
  if (pkg.license !== 'MIT') {
    report.error(PKG_FILE, `license 必须是 "MIT"，实际 ${JSON.stringify(pkg.license)}`);
  }
  if (pkg.main !== 'lib/index.js') {
    report.error(PKG_FILE, `main 必须是 "lib/index.js"（与 cordis.patch.yml 的入口约定一致），实际 ${JSON.stringify(pkg.main)}`);
  }
  if (!Array.isArray(pkg.files)) {
    report.error(PKG_FILE, `files 必须是数组，实际 ${describeType(pkg.files)}`);
  }
  if (!pkg.engines || typeof pkg.engines !== 'object') {
    report.error(PKG_FILE, 'engines 必须是对象');
  } else {
    for (const [k, v] of Object.entries(EXPECT_ENGINES)) {
      if (!isNonEmptyStr(pkg.engines[k])) {
        report.error(PKG_FILE, `engines.${k} 缺失`);
      } else if (pkg.engines[k] !== v) {
        report.warn(PKG_FILE, `engines.${k} = ${JSON.stringify(pkg.engines[k])}，与权威值 ${JSON.stringify(v)} 不一致（装不上或装到不该装的地方）`);
      }
    }
  }
  if (!pkg.description || len(String(pkg.description)) < 10) {
    report.warn(PKG_FILE, 'description 太短，npm 与 DSH 插件列表都会显示它');
  }
  for (const k of ['repository', 'keywords', 'author', 'homepage']) {
    if (!pkg[k]) report.warn(PKG_FILE, `建议补 ${k}（npm 页面 / 溯源用）`);
  }
  if (pkg.publishConfig && pkg.publishConfig.registry) {
    report.info(PKG_FILE, `publishConfig.registry = ${pkg.publishConfig.registry}`);
  }
  if (pkg.private === true) report.error(PKG_FILE, 'private:true 会让 npm publish 直接失败');
  return pkg;
}

/** 入口与 main 文件存在性 */
function checkMain(report, pkg) {
  const main = (pkg && isNonEmptyStr(pkg.main)) ? pkg.main : 'lib/index.js';
  const abs = path.join(ROOT, main);
  if (!existsSync(abs)) {
    report.error(main, 'main 指向的文件不存在（DSH 加载期会 import 失败）');
    return;
  }
  const st = statSync(abs);
  if (st.size === 0) report.error(main, '入口文件是 0 字节');
}

/** files 白名单：条目必须在数组里且磁盘上真实存在 */
/**
 * files 里允许出现的"额外"条目：双语 README 与常见元数据文件，不算越界。
 * 其它额外条目只 WARN（确认是有意为之），但仍要求磁盘真实存在。
 */
const OPTIONAL_FILES_RE = /^(README(\.[A-Za-z-]+)*\.md|\.npmignore|\.gitignore|package\.json)$/;

function isOptionalFilesEntry(name) {
  return OPTIONAL_FILES_RE.test(name);
}

function checkFilesWhitelist(report, pkg) {
  if (!pkg || !Array.isArray(pkg.files)) return;
  const files = pkg.files.map(String);
  for (const want of REQUIRED_FILES) {
    if (!files.includes(want)) report.error(PKG_FILE, `files 白名单缺少 "${want}"（发布后该目录不会被装进 profile）`);
    else if (!existsSync(path.join(ROOT, want))) report.error(PKG_FILE, `files 列了 "${want}"，但磁盘上不存在 → npm pack 会静默丢掉它`);
  }
  for (const extra of files) {
    if (REQUIRED_FILES.includes(extra)) {
      continue;
    }
    // extra 也必须在磁盘上真实存在（除非是 glob），否则 npm pack 静默丢掉
    if (extra.includes('*')) {
      report.warn(PKG_FILE, `files 里的 glob 条目 "${extra}" 未做存在性检查（glob 由 npm 展开）`);
    } else if (!existsSync(path.join(ROOT, extra))) {
      report.error(PKG_FILE, `files 列了 "${extra}"，但磁盘上不存在 → npm pack 会静默丢掉它`);
    } else if (!isOptionalFilesEntry(extra)) {
      report.warn(PKG_FILE, `files 里多出非约定条目 "${extra}"（确认是有意为之）`);
    }
  }
  if (files.includes('lib') && existsSync(path.join(ROOT, 'lib'))) {
    const n = walk(path.join(ROOT, 'lib')).length;
    if (n === 0) report.error('lib', 'lib/ 是空目录，package 里 main 会指向不存在的文件');
  }
}

// ---------- B. cordis.patch.yml ----------

function checkPatch(report, pkg) {
  const abs = path.join(ROOT, PATCH_FILE);
  if (!existsSync(abs)) {
    report.error(PATCH_FILE, '文件不存在（没有 patch，loader 永不 import 入口 → 技能全不注册）');
    return;
  }
  const { text, bom } = readText(abs);
  if (bom) report.error(PATCH_FILE, '带 UTF-8 BOM，YAML 解析可能出错');
  if (!text.trim()) {
    report.error(PATCH_FILE, '文件为空');
    return;
  }
  if (!/^\s*-?\s*insert\s*:/m.test(text)) {
    report.error(PATCH_FILE, '缺少 `- insert:` 列表（没它 loader 不会插入插件）');
  }
  const hasId = new RegExp(`-?\\s*id\\s*:\\s*['"]?${PLUGIN_ID}['"]?`).test(text);
  const hasName = new RegExp(`\\bname\\s*:\\s*['"]?${PLUGIN_ID}['"]?`).test(text);
  if (!hasId) report.error(PATCH_FILE, `缺少 \`- id: ${PLUGIN_ID}\` 行`);
  if (!hasName) report.error(PATCH_FILE, `缺少 \`name: ${PLUGIN_ID}\` 行`);
  if (hasId && hasName) {
    // 两行必须落在同一个 list item 里：粗略确认 name 行在 id 行之后 200 字符内
    const idIdx = text.search(new RegExp(`-?\\s*id\\s*:\\s*['"]?${PLUGIN_ID}`));
    const nameIdx = text.search(new RegExp(`\\bname\\s*:\\s*['"]?${PLUGIN_ID}`));
    if (idIdx >= 0 && nameIdx >= 0 && (nameIdx < idIdx || nameIdx - idIdx > 200)) {
      report.warn(PATCH_FILE, 'id 行与 name 行相距过远，确认它们属于同一个 insert item');
    }
  }
  if (pkg && pkg.dsh && pkg.dsh.bundle && pkg.dsh.bundle.patch) {
    const p = String(pkg.dsh.bundle.patch).replace(/^\.\//, '');
    if (p !== PATCH_FILE) report.error(PKG_FILE, `dsh.bundle.patch 指向 "${pkg.dsh.bundle.patch}"，实际文件是 ${PATCH_FILE}`);
    else if (!existsSync(path.join(ROOT, PATCH_FILE))) report.error(PKG_FILE, 'dsh.bundle.patch 指向的 patch 文件不存在');
  } else if (pkg) {
    report.error(PKG_FILE, '缺少 dsh.bundle.patch 字段');
  }
}

// ---------- C. 禁止 @deepseek-ai 依赖 ----------

function checkForbiddenImports(report) {
  const targets = [];
  const entry = path.join(ROOT, 'index.js');
  if (existsSync(entry)) targets.push(entry);
  for (const f of walk(path.join(ROOT, 'lib'))) {
    if (/\.(?:js|mjs|cjs)$/.test(f)) targets.push(f);
  }
  if (targets.length === 0) {
    report.warn('lib/', '没有可扫描的 .js/.mjs 文件（入口还没写？）');
    return 0;
  }
  const patterns = [
    { re: /\bfrom\s*['"]@deepseek-ai\//, what: "静态 import from '@deepseek-ai/…'" },
    { re: /\bimport\s*\(\s*['"]@deepseek-ai\//, what: "动态 import('@deepseek-ai/…')" },
    { re: /\brequire\s*\(\s*['"]@deepseek-ai\//, what: "require('@deepseek-ai/…')" },
  ];
  let hits = 0;
  for (const abs of targets) {
    const { text } = readText(abs);
    const lines = text.split(/\r?\n/);
    lines.forEach((line, i) => {
      for (const { re, what } of patterns) {
        if (re.test(line)) {
          hits++;
          report.error(`${rel(abs)}:${i + 1}`, `${what} —— 入口禁止依赖 @deepseek-ai/*（profile 的 node_modules 解析不到，会导致入口 import 失败、技能全不注册）：${clip(line.trim(), 80)}`);
        }
      }
    });
  }
  return hits;
}

// ---------- D. skills/*.md ----------

const KEBAB = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;

function parseFrontmatter(text) {
  const m = /^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/.exec(text);
  if (!m) return null;
  const body = m[1];
  const out = {};
  const lines = body.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const kv = /^([A-Za-z_][\w-]*)\s*:\s*(.*)$/.exec(line);
    if (!kv) continue;
    const key = kv[1];
    let val = kv[2].trim();
    if (val === '' || val === '|' || val === '>' || val === '|-' || val === '>-') {
      const block = [];
      for (let j = i + 1; j < lines.length; j++) {
        if (/^\s+\S/.test(lines[j]) || lines[j].trim() === '') block.push(lines[j]);
        else break;
      }
      out[key] = block.map((s) => s.trim()).join('\n').trim();
    } else {
      out[key] = val.replace(/^['"]|['"]$/g, '');
    }
  }
  return out;
}

/** 收集 data/capabilities/*.json 的 skill 字段与 version 字段 */
function collectCapabilityMeta(report) {
  const skills = new Map(); // skill -> file
  const versions = [];      // {file, version}
  if (!existsSync(CAP_DIR)) {
    report.warn('data/capabilities', '目录不存在');
    return { skills, versions };
  }
  const files = readdirSync(CAP_DIR).filter((f) => f.endsWith('.json')).sort();
  if (files.length === 0) report.warn('data/capabilities', '目录下没有 *.json 能力卡');
  for (const f of files) {
    const abs = path.join(CAP_DIR, f);
    let doc;
    try {
      doc = JSON.parse(stripBom(readFileSync(abs, 'utf8')));
    } catch {
      continue; // JSON 解析错误由 checkJsonParse 统一报
    }
    if (!doc || typeof doc !== 'object') continue;
    if (isNonEmptyStr(doc.skill)) {
      const where = `data/capabilities/${f}`;
      if (skills.has(doc.skill)) report.error(where, `skill="${doc.skill}" 与 ${skills.get(doc.skill)} 重复`);
      else skills.set(doc.skill, where);
    }
    if (isNonEmptyStr(doc.version)) versions.push({ file: `data/capabilities/${f}`, version: doc.version });
  }
  return { skills, versions };
}

function checkSkills(report, capMeta) {
  const dir = path.join(ROOT, 'skills');
  if (!existsSync(dir)) {
    report.error('skills', '目录不存在');
    return;
  }
  const mdFiles = readdirSync(dir).filter((f) => f.endsWith('.md'));
  if (mdFiles.length === 0) report.warn('skills', '目录下没有 *.md（技能注册靠它）');

  const names = new Map(); // frontmatter name -> file
  for (const f of mdFiles) {
    const abs = path.join(dir, f);
    const where = `skills/${f}`;
    const { text, bom, utf8Ok } = readText(abs);
    if (bom) report.error(where, '带 UTF-8 BOM（注册进技能目录会显示乱码，且 frontmatter 解析可能失败）');
    if (!utf8Ok) report.error(where, '不是合法 UTF-8');
    const fm = parseFrontmatter(stripBom(text));
    if (!fm) { report.error(where, '缺少 frontmatter（文件必须以 `---` 开头并闭合）'); continue; }
    if (!isNonEmptyStr(fm.name)) {
      report.error(where, 'frontmatter 缺少 name');
    } else {
      if (!KEBAB.test(fm.name)) report.error(where, `frontmatter name "${fm.name}" 不是 kebab-case`);
      if (names.has(fm.name)) report.error(where, `frontmatter name "${fm.name}" 与 ${names.get(fm.name)} 重复`);
      else names.set(fm.name, where);
      const stem = f.slice(0, -3);
      if (stem !== fm.name) report.warn(where, `文件名 "${stem}" 与 frontmatter name "${fm.name}" 不一致（建议文件名为 \`<name>.md\`）`);
    }
    if (!isNonEmptyStr(fm.description)) {
      report.error(where, 'frontmatter 缺少 description');
    } else if (len(fm.description) > 500) {
      report.error(where, `description 有 ${len(fm.description)} 字符，超过上限 500`);
    }
    if (!isNonEmptyStr(fm.whenToUse)) report.warn(where, 'frontmatter 缺 whenToUse（SPEC §四 要求，会进技能目录做触发判断）');
  }

  // 与能力卡一一对应：能力卡 → 技能 md 缺失是硬错（注册不到、能力卡指向空）；
  // 技能 md → 能力卡缺失只算 warning：skills/ 下还有 1 个"入口技能"不对应任何域能力卡。
  for (const [skill, capFile] of capMeta.skills) {
    if (!names.has(skill)) report.error(capFile, `skill="${skill}" 没有对应的 skills/${skill}.md（技能注册不到，能力卡指向空）`);
  }
  for (const [name, file] of names) {
    if (!capMeta.skills.has(name)) report.warn(file, `技能 "${name}" 没有对应的 data/capabilities/*.json（若这是入口技能则正常）`);
  }
}

// ---------- E. JSON 可解析 + catalog 对账 ----------

function checkJsonParse(report) {
  const dirs = ['data', 'knowledge'].map((d) => path.join(ROOT, d));
  let count = 0;
  for (const dir of dirs) {
    if (!existsSync(dir)) { report.error(rel(dir), '目录不存在'); continue; }
    for (const abs of walk(dir)) {
      if (!abs.toLowerCase().endsWith('.json')) continue;
      count++;
      try {
        JSON.parse(stripBom(readFileSync(abs, 'utf8')));
      } catch (e) {
        report.error(rel(abs), `JSON 解析失败：${e.message}`);
      }
    }
  }
  report.info('data+knowledge', `共校验 ${count} 个 JSON 文件`);
  return count;
}

function checkCatalogFiles(report) {
  if (!existsSync(CATALOG)) {
    report.error('knowledge/catalog.json', '文件不存在');
    return;
  }
  let list;
  try {
    list = JSON.parse(stripBom(readFileSync(CATALOG, 'utf8')));
  } catch (e) {
    report.error('knowledge/catalog.json', `JSON 解析失败：${e.message}`);
    return;
  }
  if (!Array.isArray(list)) {
    report.error('knowledge/catalog.json', `顶层必须是数组，实际是 ${describeType(list)}`);
    return;
  }
  const missing = [];
  let noFile = 0;
  for (const entry of list) {
    if (!entry || !isNonEmptyStr(entry.file)) { noFile++; continue; }
    const abs = path.resolve(CATALOG, '..', entry.file);
    if (!existsSync(abs)) missing.push(entry.file);
  }
  if (noFile) report.warn('knowledge/catalog.json', `${noFile} 条记录没有 file 字段`);
  if (missing.length) {
    report.error('knowledge/catalog.json', `${missing.length}/${list.length} 条 file 指向的技能原文不存在，例如：${missing.slice(0, 5).join('、')}${missing.length > 5 ? ' …' : ''}（research_kb_read 会读空）`);
  }
  report.info('knowledge/catalog.json', `${list.length} 条技能记录，file 缺失 ${missing.length} 条`);
}

// ---------- F. 版本一致性 ----------

function latestChangelogVersion(report) {
  const abs = path.join(ROOT, CHANGELOG);
  if (!existsSync(abs)) { report.error(CHANGELOG, '文件不存在'); return null; }
  const { text, bom } = readText(abs);
  if (bom) report.warn(CHANGELOG, '带 UTF-8 BOM');
  const lines = stripBom(text).split(/\r?\n/);
  for (const line of lines) {
    const m = /^##\s*\[?v?(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\]?/.exec(line.trim());
    if (m) return m[1];
  }
  report.error(CHANGELOG, '找不到 `## x.y.z` 形式的版本条目');
  return null;
}

function checkVersions(report, pkg, capMeta) {
  const pkgVer = pkg && isNonEmptyStr(pkg.version) ? pkg.version : null;
  const clVer = latestChangelogVersion(report);
  if (pkgVer && clVer && pkgVer !== clVer) {
    report.error(CHANGELOG, `最新条目 ${clVer} 与 package.json.version ${pkgVer} 不一致`);
  }
  const { versions } = capMeta;
  for (const { file, version } of versions) {
    if (pkgVer && version !== pkgVer) {
      report.error(file, `version ${version} 与 package.json.version ${pkgVer} 不一致`);
    }
  }
  if (versions.length === 0) report.warn('data/capabilities', '没有任何能力卡版本可供核对');
}

// ---------- F2. data/gates.json（存在则校验结构；schema 由 Lead 维护） ----------

/**
 * data/gates.json 的顶层元信息键：允许字符串（schema 由主控维护，只做轻校验）。
 * 其余顶层键一律视为 section，必须是数组或对象。
 */
const GATES_META_KEYS = new Set(['version', 'updated', 'updatedAt', 'note', 'description', 'title', '$schema', 'name']);

function checkGates(report) {
  const abs = path.join(ROOT, 'data', 'gates.json');
  if (!existsSync(abs)) {
    report.warn('data/gates.json', '不存在（research_gate 的 section=mutex/forbidden/hard 会没有数据）');
    return;
  }
  let doc;
  try {
    doc = JSON.parse(stripBom(readFileSync(abs, 'utf8')));
  } catch (e) {
    report.error('data/gates.json', `JSON 解析失败：${e.message}`);
    return;
  }
  if (!doc || typeof doc !== 'object' || Array.isArray(doc)) {
    report.error('data/gates.json', `顶层必须是对象，实际是 ${describeType(doc)}`);
    return;
  }
  const sections = [];
  for (const key of Object.keys(doc)) {
    const v = doc[key];
    if (GATES_META_KEYS.has(key)) {
      if (v === null || (typeof v !== 'string' && typeof v !== 'number')) {
        report.warn('data/gates.json', `元信息键 "${key}" 建议为字符串，实际是 ${describeType(v)}`);
      }
      continue;
    }
    if (v === null || typeof v !== 'object') {
      report.error('data/gates.json', `section "${key}" 必须是数组或对象，实际是 ${describeType(v)}`);
      continue;
    }
    if (Array.isArray(v) && v.length === 0) {
      report.warn('data/gates.json', `section "${key}" 是空数组`);
      continue;
    }
    sections.push(Array.isArray(v) ? `${key}[${v.length}]` : key);
  }
  report.info('data/gates.json', `section：${sections.join(', ') || '(空)'}`);
}

// ---------- G2. 根目录杂物（不会被 files 白名单带上，但会进 git） ----------

const ROOT_EXPECTED = new Set([
  'package.json', 'cordis.patch.yml', 'README.md', 'CHANGELOG.md', 'LICENSE', 'icon.svg',
  '.gitignore', '.npmignore', '.npmrc', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock',
]);
const ROOT_EXPECTED_DIRS = new Set([
  'lib', 'data', 'skills', 'knowledge', 'references', 'scripts', 'docs',
  '.github', 'node_modules', '.git',
]);

function checkRootFiles(report) {
  const strays = [];
  for (const name of readdirSync(ROOT)) {
    const abs = path.join(ROOT, name);
    const isDir = statSync(abs).isDirectory();
    if (isDir) {
      if (!ROOT_EXPECTED_DIRS.has(name)) report.warn(name + '/', '根目录下的非约定目录（确认是否要发布）');
    } else if (!ROOT_EXPECTED.has(name) && !OPTIONAL_FILES_RE.test(name)) {
      strays.push(name);
    }
  }
  if (strays.length) {
    report.warn('(root)', `非约定文件 ${strays.length} 个：${strays.slice(0, 8).join('、')}${strays.length > 8 ? ' …' : ''}（files 白名单不会带上它们，但会进 git，建议清理）`);
  }
}

// ---------- G. references / docs ----------

function checkReferences(report) {
  const dir = path.join(ROOT, 'references');
  if (!existsSync(dir)) { report.error('references', '目录不存在'); return; }
  const files = readdirSync(dir).filter((f) => statSync(path.join(dir, f)).isFile());
  const numbered = [];
  for (const f of files) {
    const m = /^(\d{1,3})(?:[_\-.]|$)/.exec(f);
    if (!m) { report.warn(`references/${f}`, '文件名没有 N_ 编号前缀（编号连续性无法核对）'); continue; }
    numbered.push({ n: Number(m[1]), f });
  }
  numbered.sort((a, b) => a.n - b.n);
  if (numbered.length === 0) { report.error('references', '没有任何编号文件'); return; }
  const seen = new Map();
  for (const { n, f } of numbered) {
    if (seen.has(n)) report.error(`references/${f}`, `编号 ${n} 重复（另有 references/${seen.get(n)}）`);
    else seen.set(n, f);
  }
  const max = numbered[numbered.length - 1].n;
  for (let i = 1; i <= max; i++) {
    if (!seen.has(i)) report.error('references', `编号不连续：缺 ${String(i).padStart(2, '0')} 号`);
  }
  report.info('references', `${numbered.length} 个编号文件，编号 1–${max}`);
}

function checkDocs(report) {
  const dir = path.join(ROOT, 'docs');
  if (!existsSync(dir)) { report.error('docs', '目录不存在'); return; }
  let n = 0;
  for (const abs of walk(dir)) {
    n++;
    const st = statSync(abs);
    if (st.size === 0) report.error(rel(abs), '空文件');
  }
  if (n === 0) report.error('docs', '目录下没有文件');
  report.info('docs', `${n} 个文件`);
}

// ---------- 统计 ----------

function printStats(report) {
  const skip = new Set(['node_modules', '.git', 'dist', 'coverage']);
  const all = [];
  for (const name of readdirSync(ROOT)) {
    if (skip.has(name)) continue;
    const abs = path.join(ROOT, name);
    const st = statSync(abs);
    if (st.isDirectory()) all.push(...walk(abs, [], skip));
    else all.push(abs);
  }
  let total = 0;
  const byDir = new Map();
  const biggest = [];
  for (const abs of all) {
    const size = statSync(abs).size;
    total += size;
    const r = rel(abs);
    const top = r.includes('/') ? r.split('/')[0] + '/' : '(root)';
    const cur = byDir.get(top) || { files: 0, bytes: 0 };
    cur.files++; cur.bytes += size;
    byDir.set(top, cur);
    biggest.push({ r, size });
  }
  biggest.sort((a, b) => b.size - a.size);

  const mb = (b) => (b / 1024 / 1024).toFixed(2) + ' MB';
  const kb = (b) => (b / 1024).toFixed(1) + ' KB';
  console.log('包体统计：');
  console.log(`  文件数 ${all.length}，总体积 ${mb(total)}`);
  const rows = [...byDir.entries()].sort((a, b) => b[1].bytes - a[1].bytes);
  for (const [d, v] of rows) {
    console.log(`    ${d.padEnd(14)} ${String(v.files).padStart(5)} 个文件  ${mb(v.bytes).padStart(9)}`);
  }
  console.log('  最大的 5 个文件：');
  for (const b of biggest.slice(0, 5)) console.log(`    ${kb(b.size).padStart(9)}  ${b.r}`);
  if (total > 100 * 1024 * 1024) {
    report.warn('package', `总体积 ${mb(total)} 超过 100 MB，npm 装包体验会很差`);
  }
  console.log('');
  return { files: all.length, bytes: total };
}

// ---------- 主流程 ----------

function main() {
  const report = new Report();
  console.log('论衡 · 包体校验  dsh-research-suite');
  console.log(`包根：${ROOT}`);
  console.log('');

  const pkg = checkPackageJson(report);
  checkMain(report, pkg);
  checkFilesWhitelist(report, pkg);
  checkPatch(report, pkg);
  checkForbiddenImports(report);
  const capMeta = collectCapabilityMeta(report);
  checkSkills(report, capMeta);
  checkJsonParse(report);
  checkCatalogFiles(report);
  checkGates(report);
  checkVersions(report, pkg, capMeta);
  checkReferences(report);
  checkDocs(report);
  checkRootFiles(report);
  const stats = printStats(report);

  for (const it of report.items) {
    if (it.level === 'INFO') console.log(`[INFO] ${it.where}: ${it.msg}`);
  }
  const nonInfo = report.items.filter((i) => i.level !== 'INFO');
  if (nonInfo.length) {
    console.log('');
    for (const it of nonInfo) console.log(`[${it.level}] ${it.where}: ${it.msg}`);
  }

  const e = report.errors.length;
  const w = report.warns.length;
  console.log('');
  console.log(`package: ${stats.files} files, ${(stats.bytes / 1024 / 1024).toFixed(2)} MB, ${e} errors, ${w} warnings`);
  console.log(e === 0 ? '结果：通过（exit 0）' : '结果：不通过（exit 1）');
  return e === 0 ? 0 : 1;
}

process.exitCode = main();
