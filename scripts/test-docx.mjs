#!/usr/bin/env node
/**
 * test-docx.mjs —— lib/docx.js 的离线自测（不联网、不需要装 Office）
 *
 * 覆盖三类事实：
 *   1) 正常稿件能生成、审计全过；
 *   2) 七项检查各自真的会在坏样本上报警（不是永远返回 pass 的空壳）；
 *   3) 护栏与边界：引用缺文献表、非 docx、out 越界、3000 字性能、python-docx 可读。
 *
 * 跑法：在包根执行 `node scripts/test-docx.mjs`；可用 DOCX_TEST_DIR 指定样本目录。
 */

import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { performance } from 'node:perf_hooks';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';

const here = path.dirname(fileURLToPath(import.meta.url));
const pkgRoot = path.resolve(here, '..');

const { createDocx } = await import(pathToFileURL(path.join(pkgRoot, 'lib', 'docx.js')).href);

const fixtureDir = process.env.DOCX_TEST_DIR
  ? path.resolve(process.env.DOCX_TEST_DIR)
  : path.resolve(pkgRoot, '..', '..', '2026-11-08_1810', 'fixtures-docx');
fs.mkdirSync(fixtureDir, { recursive: true });
process.chdir(fixtureDir);

const docx = createDocx({ stats: { version: '3.2.0-test' } });

// ---------------------------------------------------------------------------
// 极简 zip 读写（仅用于制造坏样本；生产代码的实现在 lib/docx.js 里）
// ---------------------------------------------------------------------------

const CRC_TABLE = (() => {
  const table = new Int32Array(256);
  for (let n = 0; n < 256; n += 1) {
    let c = n;
    for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c;
  }
  return table;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i += 1) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function zipRead(buf) {
  let eocd = -1;
  for (let i = buf.length - 22; i >= Math.max(0, buf.length - 65557); i -= 1) {
    if (buf.readUInt32LE(i) === 0x06054b50) {
      eocd = i;
      break;
    }
  }
  if (eocd < 0) throw new Error('no EOCD');
  const count = buf.readUInt16LE(eocd + 10);
  let p = buf.readUInt32LE(eocd + 16);
  const entries = new Map();
  for (let i = 0; i < count; i += 1) {
    if (buf.readUInt32LE(p) !== 0x02014b50) throw new Error('bad central header');
    const method = buf.readUInt16LE(p + 10);
    const csize = buf.readUInt32LE(p + 20);
    const nameLen = buf.readUInt16LE(p + 28);
    const extraLen = buf.readUInt16LE(p + 30);
    const commentLen = buf.readUInt16LE(p + 32);
    const localOff = buf.readUInt32LE(p + 42);
    const name = buf.subarray(p + 46, p + 46 + nameLen).toString('utf8');
    const localNameLen = buf.readUInt16LE(localOff + 26);
    const localExtraLen = buf.readUInt16LE(localOff + 28);
    const start = localOff + 30 + localNameLen + localExtraLen;
    const data = buf.subarray(start, start + csize);
    entries.set(name, method === 0 ? Buffer.from(data) : zlib.inflateRawSync(data));
    p += 46 + nameLen + extraLen + commentLen;
  }
  return entries;
}

function zipWrite(entries) {
  const chunks = [];
  const central = [];
  let offset = 0;
  for (const [name, data] of entries) {
    const nameBuf = Buffer.from(name, 'utf8');
    const deflated = zlib.deflateRawSync(data, { level: 9 });
    const useDeflate = deflated.length < data.length;
    const payload = useDeflate ? deflated : data;
    const method = useDeflate ? 8 : 0;
    const crc = crc32(data);

    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(0x0800, 6);
    local.writeUInt16LE(method, 8);
    local.writeUInt16LE(0, 10);
    local.writeUInt16LE(0x0021, 12);
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(payload.length, 18);
    local.writeUInt32LE(data.length, 22);
    local.writeUInt16LE(nameBuf.length, 26);
    local.writeUInt16LE(0, 28);
    chunks.push(local, nameBuf, payload);

    const cd = Buffer.alloc(46);
    cd.writeUInt32LE(0x02014b50, 0);
    cd.writeUInt16LE(20, 4);
    cd.writeUInt16LE(20, 6);
    cd.writeUInt16LE(0x0800, 8);
    cd.writeUInt16LE(method, 10);
    cd.writeUInt16LE(0, 12);
    cd.writeUInt16LE(0x0021, 14);
    cd.writeUInt32LE(crc, 16);
    cd.writeUInt32LE(payload.length, 20);
    cd.writeUInt32LE(data.length, 24);
    cd.writeUInt16LE(nameBuf.length, 28);
    cd.writeUInt16LE(0, 30);
    cd.writeUInt16LE(0, 32);
    cd.writeUInt16LE(0, 34);
    cd.writeUInt16LE(0, 36);
    cd.writeUInt32LE(0, 38);
    cd.writeUInt32LE(offset, 42);
    central.push(cd, nameBuf);

    offset += 30 + nameBuf.length + payload.length;
  }
  const centralBuf = Buffer.concat(central);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(0, 4);
  eocd.writeUInt16LE(0, 6);
  eocd.writeUInt16LE(entries.size, 8);
  eocd.writeUInt16LE(entries.size, 10);
  eocd.writeUInt32LE(centralBuf.length, 12);
  eocd.writeUInt32LE(offset, 16);
  eocd.writeUInt16LE(0, 20);
  return Buffer.concat([...chunks, centralBuf, eocd]);
}

// ---------------------------------------------------------------------------
// 用例工具
// ---------------------------------------------------------------------------

const results = [];
function record(name, pass, detail = '') {
  results.push({ name, pass, detail });
  console.log(`${pass ? 'PASS' : 'FAIL'}  ${name}${detail ? `  — ${detail}` : ''}`);
}

const SAMPLE_MD = `# 研究背景

本研究关注 X 与 Y 的关系[1]，并参考既有工作[2-3]，结论与前人一致。

## 方法

采用前瞻性队列设计，纳入 120 例患者[1,2]，随访 12 个月。

| 指标 | 组 A | 组 B |
| --- | --- | --- |
| 年龄（岁） | 52.1 | 51.3 |
| 有效率（%） | 78.5 | 61.2 |

## 结果

联合治疗组的有效率高于对照组[3]。

# 参考文献

[1] 张三. 某某研究[J]. 中华医学杂志, 2020, 100(1): 1-6.
[2] 李四. 另一项研究[J]. 中华内科杂志, 2021, 60(3): 10-15.
[3] Wang W, et al. A study[J]. N Engl J Med, 2019, 380(1): 1-9.
`;

function buildSample(name, extra = {}) {
  return docx.build({ markdown: SAMPLE_MD, meta: { title: '测试稿件', author: 'tester' }, out: `${name}.docx`, ...extra });
}

function mutate(baseFile, outName, transform) {
  const entries = zipRead(fs.readFileSync(baseFile));
  const xml = entries.get('word/document.xml').toString('utf8');
  entries.set('word/document.xml', Buffer.from(transform(xml), 'utf8'));
  const target = path.join(fixtureDir, outName);
  fs.writeFileSync(target, zipWrite(entries));
  return target;
}

function checkOf(report, id) {
  return (report.checks ?? []).find((c) => c.id === id);
}

function expectFail(name, report, id, needle = '') {
  if (!report) {
    record(name, false, '没有拿到审计报告');
    return;
  }
  // 注意：audit 的 ok=false 可能只是某一项判定失败（这正是我们要测的），
  // 只有「一项检查都没跑成」才是真的没跑起来。
  if (!Array.isArray(report.checks) || report.checks.length === 0) {
    record(name, false, `审计没跑成检查：${report.reason ?? ''} ${report.detail ?? ''}`.trim());
    return;
  }
  const c = checkOf(report, id);
  if (!c) {
    record(name, false, `没有 ${id} 这项检查`);
    return;
  }
  const pass = c.pass === false && String(c.actual).includes(needle);
  record(name, pass, `${id} pass=${c.pass}｜${c.actual}`);
}

// ---------------------------------------------------------------------------
// 用例 1：正常中文论著 → 生成成功且 7 项全过
// ---------------------------------------------------------------------------

const base = buildSample('sample-zh-journal');
const baseAudit = base.ok ? docx.audit({ file: base.path }) : null;
const basePass =
  base.ok &&
  base.profile === 'zh-journal' &&
  base.citations === 4 &&
  base.tables === 1 &&
  base.references === 3 &&
  base.paragraphs >= 6 &&
  base.bytes > 1000 &&
  baseAudit?.ok === true &&
  baseAudit.checks.length === 7 &&
  baseAudit.checks.every((c) => c.pass);
record(
  '1 正常中文论著：build + audit 全过',
  basePass,
  base.ok ? `bytes=${base.bytes} paragraphs=${base.paragraphs} citations=${base.citations} refs=${base.references}｜${baseAudit?.summary}` : JSON.stringify(base),
);

const baseFile = base.ok ? base.path : null;

// ---------------------------------------------------------------------------
// 用例 2～8：七项检查能否真的抓到坏样本
// ---------------------------------------------------------------------------

if (baseFile) {
  const noSuper = mutate(baseFile, 'broken-no-superscript.docx', (xml) => xml.split('<w:vertAlign w:val="superscript"/>').join(''));
  const a2 = docx.audit({ file: noSuper });
  const c2 = checkOf(a2, 'superscript-citations');
  record('2 去掉上标：superscript-citations 报错', c2?.pass === false, c2 ? c2.actual : '缺检查项');

  const extraSup = mutate(
    baseFile,
    'broken-extra-superscript.docx',
    (xml) =>
      xml.replace(
        '</w:p>',
        '<w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:t>整段上标文字</w:t></w:r></w:p>',
      ),
  );
  const a3 = docx.audit({ file: extraSup });
  const c3 = checkOf(a3, 'superscript-citations');
  const extraHit = /上标 run 里非引用文字 (\d+) 个/.exec(c3?.actual ?? '');
  record('3 整段误设上标：报「上标 run 里非引用文字>0」', c3?.pass === false && Number(extraHit?.[1] ?? 0) > 0, c3 ? c3.actual : '缺检查项');

  const badFont = mutate(baseFile, 'broken-font.docx', (xml) => xml.split('w:eastAsia="宋体"').join('w:eastAsia="Calibri"'));
  expectFail('4 字体改 Calibri：fonts 报错', docx.audit({ file: badFont }), 'fonts', '东亚洲字体不符');

  const badSize = mutate(baseFile, 'broken-size.docx', (xml) => xml.split('<w:sz w:val="24"/>').join('<w:sz w:val="16"/>'));
  const a5 = docx.audit({ file: badSize });
  const c5 = checkOf(a5, 'font-size');
  record('5 字号 8pt：font-size 报错', c5?.pass === false, c5 ? c5.actual : '缺检查项');

  const badLine = mutate(baseFile, 'broken-line.docx', (xml) => xml.split('w:line="360"').join('w:line="240"'));
  const a6 = docx.audit({ file: badLine });
  const c6 = checkOf(a6, 'line-spacing');
  record('6 行距单倍：line-spacing 报警（warn）', c6?.pass === false && c6.level === 'warn', c6 ? c6.actual : '缺检查项');

  const badTable = mutate(
    baseFile,
    'broken-table.docx',
    (xml) => xml.replace('</w:tblBorders>', '<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tblBorders>'),
  );
  const a7 = docx.audit({ file: badTable });
  const c7 = checkOf(a7, 'table-borders');
  record('7 表格带竖线：table-borders 报错', c7?.pass === false, c7 ? c7.actual : '缺检查项');

  const badHang = mutate(baseFile, 'broken-hanging.docx', (xml) => xml.split('<w:ind w:left="420" w:hanging="420"/>').join('<w:ind w:left="420"/>'));
  const a8 = docx.audit({ file: badHang });
  const c8 = checkOf(a8, 'hanging-indent');
  record('8 文献表无悬挂缩进：hanging-indent 报警（warn）', c8?.pass === false && c8.level === 'warn', c8 ? c8.actual : '缺检查项');
}

// ---------------------------------------------------------------------------
// 用例 9～10：不是 docx、引用缺文献表
// ---------------------------------------------------------------------------

const junkPath = path.join(fixtureDir, 'not-a-docx.docx');
fs.writeFileSync(junkPath, Buffer.from('这不是 zip，只是一段随机文本，用来验证 not_a_docx。', 'utf8'));
const junkReport = docx.audit({ file: junkPath });
record('9 非 docx 文件：not_a_docx 且不抛异常', junkReport.ok === false && junkReport.reason === 'not_a_docx', junkReport.detail ?? '');

const noRefs = docx.build({ markdown: '# 结果\n\n既往研究提示该关联存在[1]，本文予以验证。\n', out: 'no-refs.docx' });
record(
  '10 有引用编号但无文献表：build 拒绝',
  noRefs.ok === false && noRefs.reason === 'references_missing',
  noRefs.ok ? '竟然生成成功' : `${noRefs.reason}｜${noRefs.detail}`,
);

// ---------------------------------------------------------------------------
// 用例 11：3000 字文档 build + audit 性能
// ---------------------------------------------------------------------------

const para = '本项目围绕队列人群的暴露与结局关系展开分析，逐条核对纳入排除标准并记录随访时间，确保每个统计量都能回溯到原始记录。';
const longMd = `# 引言\n\n${Array.from({ length: 40 }, (_, i) => `${para}（第 ${i + 1} 段，引用见[1]。）`).join('\n\n')}\n\n# 参考文献\n\n[1] 张三. 某某研究[J]. 中华医学杂志, 2020, 100(1): 1-6.\n`;
const perfStart = performance.now();
const big = docx.build({ markdown: longMd, meta: { title: '长稿性能' }, out: 'perf-3000.docx' });
const bigAudit = big.ok ? docx.audit({ file: big.path }) : null;
const perfMs = performance.now() - perfStart;
const charCount = [...longMd].length;
record(
  '11 3000 字文档 build+audit < 3000ms',
  big.ok && bigAudit?.ok === true && perfMs < 3000,
  `字符 ${charCount}｜耗时 ${perfMs.toFixed(0)}ms｜bytes=${big.bytes ?? '-'}`,
);

// ---------------------------------------------------------------------------
// 用例 12：python-docx 能否打开（本机没有就跳过）
// ---------------------------------------------------------------------------

const pythonExe = 'D:\\nodehome\\.dsh\\dsh-runtimes\\dsh-primary-runtime\\dependencies\\python\\python.exe';
if (baseFile && fs.existsSync(pythonExe)) {
  const code = `import docx,sys; d=docx.Document(r"${baseFile}"); print("paragraphs", len(d.paragraphs))`;
  const run = spawnSync(pythonExe, ['-c', code], { encoding: 'utf8', timeout: 60000 });
  const ok = run.status === 0;
  record(
    '12 python-docx 能打开生成的 docx',
    ok,
    ok ? (run.stdout || '').trim() : `跳过/失败：${(run.stderr || run.error?.message || '').trim().slice(0, 160)}`,
  );
} else {
  record('12 python-docx 能打开生成的 docx', true, '本机无内置 python，跳过（记 note）');
}

// ---------------------------------------------------------------------------
// 用例 13：out 越界必须被拒绝
// ---------------------------------------------------------------------------

const outside = docx.build({ markdown: SAMPLE_MD, out: path.resolve(fixtureDir, '..', 'escape.docx') });
record('13 out 越界：out_of_scope', outside.ok === false && outside.reason === 'out_of_scope', outside.detail ?? '');

// ---------------------------------------------------------------------------
// 用例 14～16：其余边界（英文 SCI 档、扩展名、空输入、坏 profile）
// ---------------------------------------------------------------------------

const en = buildSample('sample-en-sci', { profile: 'en-sci' });
const enAudit = en.ok ? docx.audit({ file: en.path, profile: 'en-sci' }) : null;
record('14 en-sci 档：build + audit 全过', en.ok === true && enAudit?.ok === true, en.ok ? enAudit?.summary ?? '' : JSON.stringify(en));

const badExt = docx.build({ markdown: SAMPLE_MD, out: 'wrong.txt' });
const empty = docx.build({ markdown: '   ', out: 'empty.docx' });
const badProfile = docx.build({ markdown: SAMPLE_MD, out: 'x.docx', profile: 'nope' });
record(
  '15 边界：bad_extension / empty_input / bad_profile',
  badExt.reason === 'bad_extension' && empty.reason === 'empty_input' && badProfile.reason === 'bad_profile',
  `${badExt.reason} / ${empty.reason} / ${badProfile.reason}`,
);

const missing = docx.audit({ file: 'does-not-exist.docx' });
record('16 审计不存在文件：not_a_docx', missing.ok === false && missing.reason === 'not_a_docx', missing.detail ?? '');

// ---------------------------------------------------------------------------
// 汇总
// ---------------------------------------------------------------------------

const failed = results.filter((r) => !r.pass);
console.log('');
console.log(`样本目录：${fixtureDir}`);
console.log(`共 ${results.length} 个用例：通过 ${results.length - failed.length}，失败 ${failed.length}`);
if (failed.length > 0) {
  for (const f of failed) console.log(`  FAILED ${f.name} — ${f.detail}`);
  process.exitCode = 1;
} else {
  console.log('结果：全部通过（exit 0）');
}
