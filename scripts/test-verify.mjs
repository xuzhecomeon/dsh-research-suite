// scripts/test-verify.mjs
// v3.1 执行与核验层的自测：自造 fixtures，不联网、不依赖任何第三方包。
//
// 为什么自造二进制 fixtures：
//   - 真实投稿件（PNG/DOCX/PDF）不能放进仓库（体积 + 版权），而「能不能打开」的判定
//     恰恰依赖文件头/zip 目录/页面对象这些字节级事实，所以这里按格式规范手写最小样本。
//   - 坏样本（缺 word/document.xml 的 docx、96dpi 的 png、无文本层的 pdf）必须能稳定复现，
//     否则「检查器抓不抓得住问题」这件事无法验证。
//
// 运行：node scripts/test-verify.mjs
// 通过标准：末尾打印 verify: N passed, 0 failed 且 exit 0。

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import zlib from 'node:zlib';
import { createVerify } from '../lib/verify.js';

const FIXTURES = path.join(
  'D:',
  'workbuddy',
  '2026-11-04-20-37-51',
  '2026-11-05_0000',
  'analysis',
  'fixtures-v31',
);

// ---------------------------------------------------------------------------
// 最小 zip 写入器（store 模式）：只为造 docx/xlsx 样本，避免引入 archiver 之类依赖
// ---------------------------------------------------------------------------

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i += 1) {
    c ^= buf[i];
    for (let k = 0; k < 8; k += 1) c = (c >>> 1) ^ (0xedb88320 & -(c & 1));
  }
  return (c ^ 0xffffffff) >>> 0;
}

function zipStore(entries) {
  const locals = [];
  const centrals = [];
  let offset = 0;
  for (const entry of entries) {
    const name = Buffer.from(entry.name, 'utf8');
    const data = entry.data;
    const crc = crc32(data);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4); // version needed
    local.writeUInt16LE(0, 6); // flags
    local.writeUInt16LE(0, 8); // method 0 = store
    local.writeUInt16LE(0, 10); // mod time
    local.writeUInt16LE(0, 12); // mod date
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(data.length, 18);
    local.writeUInt32LE(data.length, 22);
    local.writeUInt16LE(name.length, 26);
    local.writeUInt16LE(0, 28);
    const localRecord = Buffer.concat([local, name, data]);
    locals.push(localRecord);

    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(20, 4); // version made by
    central.writeUInt16LE(20, 6); // version needed
    central.writeUInt16LE(0, 8); // flags
    central.writeUInt16LE(0, 10); // method
    central.writeUInt16LE(0, 12);
    central.writeUInt16LE(0, 14);
    central.writeUInt32LE(crc, 16);
    central.writeUInt32LE(data.length, 20);
    central.writeUInt32LE(data.length, 24);
    central.writeUInt16LE(name.length, 28);
    central.writeUInt16LE(0, 30); // extra
    central.writeUInt16LE(0, 32); // comment
    central.writeUInt16LE(0, 34); // disk
    central.writeUInt16LE(0, 36); // internal attrs
    central.writeUInt32LE(0, 38); // external attrs
    central.writeUInt32LE(offset, 42);
    centrals.push(Buffer.concat([central, name]));

    offset += localRecord.length;
  }
  const cd = Buffer.concat(centrals);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(0, 4);
  eocd.writeUInt16LE(0, 6);
  eocd.writeUInt16LE(entries.length, 8);
  eocd.writeUInt16LE(entries.length, 10);
  eocd.writeUInt32LE(cd.length, 12);
  eocd.writeUInt32LE(offset, 16);
  eocd.writeUInt16LE(0, 20);
  return Buffer.concat([...locals, cd, eocd]);
}

// ---------------------------------------------------------------------------
// 最小 PNG 写入器：1×1 RGB，可选 pHYs（每米像素）控制 DPI
// ---------------------------------------------------------------------------

function pngChunk(type, data) {
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length, 0);
  const body = Buffer.concat([Buffer.from(type, 'latin1'), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(body), 0);
  return Buffer.concat([length, body, crc]);
}

function makePng({ dpi = null } = {}) {
  const signature = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(1, 0); // width
  ihdr.writeUInt32BE(1, 4); // height
  ihdr[8] = 8; // bit depth
  ihdr[9] = 2; // color type RGB
  const chunks = [pngChunk('IHDR', ihdr)];
  if (dpi) {
    const ppm = Math.round(dpi / 0.0254);
    const phys = Buffer.alloc(9);
    phys.writeUInt32BE(ppm, 0);
    phys.writeUInt32BE(ppm, 4);
    phys[8] = 1; // unit = meter
    chunks.push(pngChunk('pHYs', phys));
  }
  // 一行像素：filter byte 0 + RGB(255,255,255)，deflate 后即合法 IDAT
  chunks.push(pngChunk('IDAT', zlib.deflateSync(Buffer.from([0x00, 0xff, 0xff, 0xff]))));
  chunks.push(pngChunk('IEND', Buffer.alloc(0)));
  return Buffer.concat([signature, ...chunks]);
}

// ---------------------------------------------------------------------------
// fixtures 落盘
// ---------------------------------------------------------------------------

function writeFixtures() {
  fs.rmSync(FIXTURES, { recursive: true, force: true });
  fs.mkdirSync(FIXTURES, { recursive: true });

  const write = (name, content) => {
    const full = path.join(FIXTURES, name);
    fs.mkdirSync(path.dirname(full), { recursive: true });
    fs.writeFileSync(full, content);
    return full;
  };

  // 一份「哪条闸门都过不去」的 CSV：缺失率、常量列、重复 ID、不可能值、重复行、EPV 不足
  const badCsv = [
    'id,age,sex,count,rate,outcome,pred1,pred2,pred3,pred4,sparse,moderate,const',
    '1,45,M,3,20.5,1,0.1,0.2,0.3,0.4,x,1,C',
    '1,52,F,2,30.0,0,0.2,0.1,0.4,0.3,,2,C',
    '3,200,M,-1,150.0,0,0.5,0.6,0.7,0.8,x,,C',
    '4,,F,1,10.0,,0.3,0.2,0.1,0.5,,,C',
    '5,61,M,4,40.0,0,0.4,0.3,0.2,0.1,,3,C',
    '5,61,M,4,40.0,0,0.4,0.3,0.2,0.1,,3,C',
    '7,33,F,2,25.0,0,0.6,0.7,0.8,0.9,,,C',
    '8,47,M,3,35.0,0,0.7,0.6,0.9,0.8,,,C',
    '9,29,F,,,0,0.8,0.9,0.1,0.2,,1,C',
    '',
  ].join('\n');
  write('bad-data.csv', Buffer.from(badCsv, 'utf8'));

  write('good.csv', Buffer.from('a,b\n1,2\n3,4\n', 'utf8'));

  // TSV：验证分隔符探测不是「永远逗号」
  write('data.tsv', Buffer.from('a\tb\n1\t2\n3\t4\n', 'utf8'));

  // 21 个文本水平：应触发「疑似把分类变量当连续变量」的提示
  const manyLevels = ['id,label'];
  for (let i = 1; i <= 21; i += 1) manyLevels.push(`${i},L${i}`);
  write('many-levels.csv', Buffer.from(`${manyLevels.join('\n')}\n`, 'utf8'));

  // PNG：96dpi（投稿不可用）、300dpi（合格）、无 pHYs（无法判定）
  write('png-96.png', makePng({ dpi: 96 }));
  write('png-300.png', makePng({ dpi: 300 }));
  write('png-nophys.png', makePng());

  // 正常 DOCX：document.xml 有 2 段正文 + 1 个表格（表格里还有 1 段）
  const documentXml = Buffer.from(
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
      + '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
      + '<w:p><w:r><w:t>First paragraph</w:t></w:r></w:p>'
      + '<w:p><w:r><w:t>Second paragraph</w:t></w:r></w:p>'
      + '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Cell</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
      + '</w:body></w:document>',
    'utf8',
  );
  const contentTypes = Buffer.from(
    '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/></Types>',
    'utf8',
  );
  write('docx-good.docx', zipStore([
    { name: '[Content_Types].xml', data: contentTypes },
    { name: 'word/document.xml', data: documentXml },
  ]));

  // 坏 DOCX：zip 合法，但没有 word/document.xml（Word 打开会报「文件已损坏」）
  write('docx-bad.docx', zipStore([
    { name: '[Content_Types].xml', data: contentTypes },
    { name: 'word/styles.xml', data: Buffer.from('<w:styles/>', 'utf8') },
  ]));

  // 正常 XLSX：workbook 声明 1 个 sheet，磁盘上也有 1 个 worksheet
  const workbookXml = Buffer.from(
    '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Sheet1" sheetId="1"/></sheets></workbook>',
    'utf8',
  );
  write('xlsx-good.xlsx', zipStore([
    { name: '[Content_Types].xml', data: contentTypes },
    { name: 'xl/workbook.xml', data: workbookXml },
    { name: 'xl/worksheets/sheet1.xml', data: Buffer.from('<worksheet/>', 'utf8') },
  ]));

  // 有文本层的 PDF（/Type /Page + 字体资源 + BT/Tj）
  const pdfText = [
    '%PDF-1.4',
    '1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj',
    '2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj',
    '3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj',
    '4 0 obj << /Length 44 >> stream',
    'BT /F1 24 Tf 72 700 Td (Hello PDF) Tj ET',
    'endstream endobj',
    '5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj',
    'trailer << /Root 1 0 R >>',
    '%%EOF',
    '',
  ].join('\n');
  write('pdf-good.pdf', Buffer.from(pdfText, 'latin1'));

  // 纯图片 PDF：没有 /Font 也没有 Tj，应提示「没有文本层」
  const pdfScan = [
    '%PDF-1.4',
    '1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj',
    '2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj',
    '3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R >> endobj',
    '4 0 obj << /Length 37 >> stream',
    'q 100 0 0 100 0 0 cm /Im0 Do Q',
    'endstream endobj',
    'trailer << /Root 1 0 R >>',
    '%%EOF',
    '',
  ].join('\n');
  write('pdf-scan.pdf', Buffer.from(pdfScan, 'latin1'));

  write('note.md', Buffer.from('# 标题\n\n这是正文，用来验证字数统计。\n', 'utf8'));
  write('plain.txt', Buffer.from('unsupported', 'utf8'));
}

// ---------------------------------------------------------------------------
// 极简断言与用例登记
// ---------------------------------------------------------------------------

let passed = 0;
let failed = 0;
const failures = [];

function check(name, fn) {
  try {
    fn();
    passed += 1;
    console.log(`  ok   ${name}`);
  } catch (err) {
    failed += 1;
    failures.push({ name, message: String(err?.message ?? err) });
    console.log(`  FAIL ${name}`);
    console.log(`       ${String(err?.message ?? err)}`);
  }
}

async function checkAsync(name, fn) {
  try {
    await fn();
    passed += 1;
    console.log(`  ok   ${name}`);
  } catch (err) {
    failed += 1;
    failures.push({ name, message: String(err?.message ?? err) });
    console.log(`  FAIL ${name}`);
    console.log(`       ${String(err?.message ?? err)}`);
  }
}

function assert(cond, message) {
  if (!cond) throw new Error(message);
}

function eq(actual, expected, label) {
  if (actual !== expected) throw new Error(`${label}: 期望 ${JSON.stringify(expected)}，实际 ${JSON.stringify(actual)}`);
}

function rules(result) {
  return new Set((result.findings ?? []).map((f) => f.rule));
}

function levels(result) {
  return (result.findings ?? []).map((f) => f.level);
}

const F = (name) => path.join(FIXTURES, name);

// ---------------------------------------------------------------------------
// 用例
// ---------------------------------------------------------------------------

async function main() {
  writeFixtures();

  const verify = createVerify({}, {});
  const verifyNoRuntime = createVerify({}, { runtimes: { r: [path.join(FIXTURES, 'no-such-Rscript.exe')] } });
  // runScript 的 workdir 必须落在 process.cwd() 或系统临时目录内；测试从包根启动，
  // fixtures 不在 cwd 下，所以执行目录放临时区（既符合安全闸，也不在仓库里留垃圾）。
  const runDir = path.join(os.tmpdir(), 'dsh-verify-v31-run');
  fs.rmSync(runDir, { recursive: true, force: true });
  fs.mkdirSync(runDir, { recursive: true });

  console.log(`fixtures: ${FIXTURES}`);
  console.log(`version: ${verify.version}`);
  eq(verify.version, '3.1.0', 'version');

  // ---------------- runScript ----------------
  console.log('\n[runScript]');

  const rOk = await verify.runScript({ kind: 'r', workdir: runDir, code: 'cat("hello-from-r\\n")\nwriteLines("done", "out.txt")' });
  await checkAsync('R 脚本能跑起来并报告 stdout', () => {
    assert(rOk.ok === true, `期望 ok=true，实际 ${JSON.stringify(rOk).slice(0, 300)}`);
    eq(rOk.exitCode, 0, 'exitCode');
    eq(rOk.kind, 'r', 'kind');
    assert(String(rOk.stdout).includes('hello-from-r'), `stdout 未包含标记：${rOk.stdout}`);
    assert(/\.R$/.test(String(rOk.script)), `脚本扩展名应为 .R：${rOk.script}`);
    assert(Array.isArray(rOk.files), 'files 必须是数组');
  });
  check('R 脚本执行后列出新增文件', () => {
    assert(rOk.files.some((f) => f.path === 'out.txt'), `files 里没有 out.txt：${JSON.stringify(rOk.files)}`);
    assert(rOk.files.every((f) => typeof f.bytes === 'number' && typeof f.mtime === 'string'), 'files 元素须含 bytes/mtime');
  });
  check('runScript 返回 command/durationMs', () => {
    assert(typeof rOk.command === 'string' && rOk.command.length > 0, 'command 为空');
    assert(Number.isFinite(rOk.durationMs) && rOk.durationMs >= 0, 'durationMs 非法');
  });

  const pyOk = await verify.runScript({ kind: 'python', workdir: runDir, code: 'print("hello-from-py")' });
  await checkAsync('Python 脚本能跑起来', () => {
    assert(pyOk.ok === true, `期望 ok=true，实际 ${JSON.stringify(pyOk).slice(0, 300)}`);
    assert(String(pyOk.stdout).includes('hello-from-py'), `stdout 未包含标记：${pyOk.stdout}`);
    assert(/\.py$/.test(String(pyOk.script)), `脚本扩展名应为 .py：${pyOk.script}`);
  });

  const blocked = await verify.runScript({ kind: 'r', workdir: runDir, code: 'install.packages("ggplot2")' });
  await checkAsync('安装包的代码被安全闸拦下', () => {
    eq(blocked.ok, false, 'ok');
    eq(blocked.blocked, true, 'blocked');
    eq(blocked.reason, 'dangerous_code', 'reason');
    assert(String(blocked.hint).includes('install.packages'), `hint 未说明命中规则：${blocked.hint}`);
  });

  const outside = await verify.runScript({ kind: 'r', workdir: 'C:\\Windows', code: 'cat("x")' });
  await checkAsync('workdir 越界被拦下', () => {
    eq(outside.ok, false, 'ok');
    eq(outside.blocked, true, 'blocked');
    eq(outside.reason, 'workdir_outside', 'reason');
  });

  const missingRuntime = await verifyNoRuntime.runScript({ kind: 'r', workdir: runDir, code: 'cat("x")' });
  await checkAsync('解释器缺失时返回 runtime_missing 而不是抛异常', () => {
    eq(missingRuntime.ok, false, 'ok');
    eq(missingRuntime.error, 'runtime_missing', 'error');
    assert(Array.isArray(missingRuntime.tried) && missingRuntime.tried.length >= 1, 'tried 必须列出探测过的路径');
    assert(String(missingRuntime.tried[0]).includes('no-such-Rscript.exe'), `tried 内容不对：${JSON.stringify(missingRuntime.tried)}`);
  });

  const timedOut = await verify.runScript({ kind: 'r', workdir: runDir, code: 'Sys.sleep(3)', timeoutMs: 1000 });
  await checkAsync('超时被标记 timedOut 且不挂死', () => {
    eq(timedOut.ok, false, 'ok');
    eq(timedOut.timedOut, true, 'timedOut');
    assert(Number(timedOut.durationMs) < 5000, `耗时过长：${timedOut.durationMs}ms`);
  });

  const badKind = await verify.runScript({ kind: 'julia', workdir: runDir, code: 'x' });
  await checkAsync('未知 kind 返回 bad_kind', () => {
    eq(badKind.ok, false, 'ok');
    eq(badKind.error, 'bad_kind', 'error');
  });

  // ---------------- checkData ----------------
  console.log('\n[checkData]');

  const bad = await verify.checkData({ file: F('bad-data.csv'), outcome: 'outcome', predictors: ['pred1', 'pred2', 'pred3', 'pred4'] });
  await checkAsync('坏数据能读到行列结构', () => {
    eq(bad.rows, 9, 'rows');
    eq(bad.cols, 13, 'cols');
    eq(bad.delimiter, ',', 'delimiter');
    eq(bad.columns.length, 13, 'columns.length');
  });
  check('坏数据命中缺失率规则（>50% 为 error，>20% 为 warn）', () => {
    const missing = bad.findings.filter((f) => f.rule === 'missing_rate');
    assert(missing.some((f) => f.level === 'error' && f.detail.includes('sparse')), `缺少 sparse 的 error：${JSON.stringify(missing)}`);
    assert(missing.some((f) => f.level === 'warn' && f.detail.includes('moderate')), `缺少 moderate 的 warn：${JSON.stringify(missing)}`);
  });
  check('坏数据命中常量列 / 重复 ID / 不可能值 / 重复行', () => {
    const r = rules(bad);
    for (const rule of ['constant_column', 'id_duplicate', 'impossible_age', 'negative_count', 'percent_range', 'duplicate_rows']) {
      assert(r.has(rule), `缺少规则 ${rule}，实际：${[...r].join(',')}`);
    }
  });
  check('EPV 不足判 error 且数值正确', () => {
    eq(bad.epv.events, 1, 'events');
    eq(bad.epv.predictors, 4, 'predictors');
    eq(bad.epv.epv, 0.25, 'epv');
    eq(bad.epv.ok, false, 'epv.ok');
    assert(rules(bad).has('epv_low'), '缺少 epv_low');
    assert(levels(bad).includes('error'), '至少应有一条 error');
  });

  const good = await verify.checkData({ file: F('good.csv') });
  await checkAsync('干净数据不误报', () => {
    eq(good.rows, 2, 'rows');
    eq(good.findings.length, 0, `不应有 findings：${JSON.stringify(good.findings)}`);
  });

  const tsv = await verify.checkData({ file: F('data.tsv') });
  await checkAsync('TSV 分隔符能被识别', () => {
    eq(tsv.delimiter, '\t', 'delimiter');
    eq(tsv.rows, 2, 'rows');
  });

  const many = await verify.checkData({ file: F('many-levels.csv') });
  await checkAsync('文本水平 >20 提示疑似误当连续变量', () => {
    assert(rules(many).has('too_many_levels'), `规则缺失：${[...rules(many)].join(',')}`);
    assert(!levels(many).includes('error'), '该样本不应有 error');
  });

  const notFound = await verify.checkData({ file: F('no-such.csv') });
  await checkAsync('数据文件不存在返回 not_found', () => {
    assert(rules(notFound).has('not_found'), '缺少 not_found');
    eq(notFound.findings[0].level, 'error', 'level');
  });

  const epvMissing = await verify.checkData({ file: F('good.csv'), outcome: 'nope', predictors: [] });
  await checkAsync('outcome 列不存在时跳过 EPV 并给出提示', () => {
    assert(rules(epvMissing).has('epv_outcome_missing'), `规则缺失：${[...rules(epvMissing)].join(',')}`);
  });

  // ---------------- checkOutputs ----------------
  console.log('\n[checkOutputs]');

  const out = await verify.checkOutputs({
    files: [
      F('png-96.png'),
      F('png-300.png'),
      F('png-nophys.png'),
      F('docx-good.docx'),
      F('docx-bad.docx'),
      F('xlsx-good.xlsx'),
      F('pdf-good.pdf'),
      F('pdf-scan.pdf'),
      F('good.csv'),
      F('note.md'),
      F('plain.txt'),
      F('no-such.png'),
    ],
  });
  const byName = new Map(out.results.map((r) => [path.basename(r.file), r]));

  await checkAsync('汇总计数与结果条数一致', () => {
    eq(out.results.length, 12, 'results.length');
    eq(out.summary.files, 12, 'summary.files');
    eq(typeof out.summary.error, 'number', 'summary.error 类型');
    eq(typeof out.summary.warn, 'number', 'summary.warn 类型');
  });

  check('96dpi PNG 判为不可用（error）', () => {
    const r = byName.get('png-96.png');
    eq(r.ok, true, 'png 本身能解析');
    const hit = r.findings.find((f) => f.rule === 'png_dpi_low');
    assert(hit, '缺少 png_dpi_low');
    eq(hit.level, 'error', '96dpi 应为 error');
  });
  check('300dpi PNG 通过且 dpi 正确', () => {
    const r = byName.get('png-300.png');
    eq(r.ok, true, 'ok');
    eq(r.facts.dpi, 300, 'dpi');
    eq(r.findings.length, 0, `不应有 findings：${JSON.stringify(r.findings)}`);
  });
  check('无 pHYs PNG 提示无法判定 DPI（warn）', () => {
    const r = byName.get('png-nophys.png');
    const hit = r.findings.find((f) => f.rule === 'png_no_dpi');
    assert(hit, '缺少 png_no_dpi');
    eq(hit.level, 'warn', 'level');
  });
  check('正常 DOCX 能数出段落与表格', () => {
    const r = byName.get('docx-good.docx');
    eq(r.ok, true, 'ok');
    assert(r.facts.paragraphs >= 3, `段落数应 >=3，实际 ${r.facts.paragraphs}`);
    eq(r.facts.tables, 1, 'tables');
  });
  check('假 DOCX 缺 document.xml 判 error', () => {
    const r = byName.get('docx-bad.docx');
    eq(r.ok, false, 'ok');
    assert(rules(r).has('docx_missing_document'), `规则缺失：${[...rules(r)].join(',')}`);
  });
  check('正常 XLSX 能数出 sheet', () => {
    const r = byName.get('xlsx-good.xlsx');
    eq(r.ok, true, 'ok');
    assert(r.facts.sheets >= 1, `sheets=${r.facts.sheets}`);
  });
  check('正常 PDF 有页数与文本层', () => {
    const r = byName.get('pdf-good.pdf');
    eq(r.ok, true, 'ok');
    assert(r.facts.pages >= 1, `pages=${r.facts.pages}`);
    eq(r.facts.hasText, true, 'hasText');
    eq(r.findings.length, 0, `不应有 findings：${JSON.stringify(r.findings)}`);
  });
  check('扫描件 PDF 提示无文本层（warn）', () => {
    const r = byName.get('pdf-scan.pdf');
    eq(r.ok, true, 'ok');
    assert(rules(r).has('pdf_no_text'), `规则缺失：${[...rules(r)].join(',')}`);
    eq(r.findings.find((f) => f.rule === 'pdf_no_text').level, 'warn', 'level');
  });
  check('CSV 能数出行列', () => {
    const r = byName.get('good.csv');
    eq(r.ok, true, 'ok');
    eq(r.facts.rows, 2, 'rows');
  });
  check('Markdown 能统计字数', () => {
    const r = byName.get('note.md');
    eq(r.ok, true, 'ok');
    assert(r.facts.chars > 0, `chars=${r.facts.chars}`);
  });
  check('不支持的扩展名与缺失文件都判 error', () => {
    assert(rules(byName.get('plain.txt')).has('unsupported_type'), '缺少 unsupported_type');
    assert(rules(byName.get('no-such.png')).has('not_found'), '缺少 not_found');
  });

  // ---------------- checkDois ----------------
  console.log('\n[checkDois]');

  const offline = createVerify({}, { fetchImpl: async () => { throw new TypeError('fetch failed'); } });
  const offlineRes = await offline.checkDois({ dois: ['https://doi.org/10.1000/XYZ'] });
  await checkAsync('无网络时返回 network 且不抛异常', () => {
    eq(Array.isArray(offlineRes), true, '返回数组');
    eq(offlineRes.length, 1, 'length');
    eq(offlineRes[0].ok, false, 'ok');
    eq(offlineRes[0].error, 'network', 'error');
    eq(offlineRes[0].doi, '10.1000/xyz', 'doi 归一化（去前缀 + 小写）');
  });

  const seen = [];
  const fakeOk = createVerify({}, {
    fetchImpl: async (url, init) => {
      seen.push({ url, userAgent: init?.headers?.['User-Agent'] });
      return {
        ok: true,
        status: 200,
        json: async () => ({
          message: {
            title: ['A Great Paper'],
            'container-title': ['Journal of Tests'],
            issued: { 'date-parts': [[2020, 5, 1]] },
            type: 'journal-article',
            author: [{ given: 'Alice', family: 'Zhang' }],
          },
        }),
      };
    },
  });
  const okRes = await fakeOk.checkDois({ dois: ['https://doi.org/10.1000/XYZ'] });
  await checkAsync('CrossRef 返回被解析成 title/year/authors', () => {
    eq(okRes[0].ok, true, 'ok');
    eq(okRes[0].status, 200, 'status');
    eq(okRes[0].title, 'A Great Paper', 'title');
    eq(okRes[0].container, 'Journal of Tests', 'container');
    eq(okRes[0].year, 2020, 'year');
    eq(okRes[0].type, 'journal-article', 'type');
    eq(okRes[0].authors[0], 'Alice Zhang', 'authors');
    assert(seen[0].url.includes('api.crossref.org/works/10.1000%2Fxyz'), `URL 编码不对：${seen[0].url}`);
    assert(String(seen[0].userAgent).startsWith('dsh-research-suite/'), `UA 不对：${seen[0].userAgent}`);
  });

  const fake404 = createVerify({}, { fetchImpl: async () => ({ ok: false, status: 404, json: async () => ({}) }) });
  const notFoundRes = await fake404.checkDois({ dois: ['10.9999/nope'] });
  await checkAsync('DOI 不存在返回 not_found', () => {
    eq(notFoundRes[0].ok, false, 'ok');
    eq(notFoundRes[0].error, 'not_found', 'error');
  });

  const invalid = await fakeOk.checkDois({ dois: ['   '] });
  await checkAsync('空 DOI 返回 invalid_doi', () => {
    eq(invalid[0].error, 'invalid_doi', 'error');
  });

  // ---------------- auditRefs ----------------
  console.log('\n[auditRefs]');

  const refsText = [
    '正文首次引用[1]，再次引用[2]与[5-6]，同一编号重复[1]，编号 3、4 缺失。',
    '正文里同一 DOI 出现两次：10.1000/ABC 与 10.1000/abc。',
    '',
    '## 参考文献',
    '[1] 张三. 某研究. 中华医学杂志. 2020. doi:10.1000/a',
    '[2] 李四. 某研究二. 2021.',
    '[3] 王五. 某研究三. 2099. doi:10.1000/b',
    '[4] 赵六. 某研究四. 2020. doi:10.1000/a',
    '',
  ].join('\n');
  const refs = await verify.auditRefs({ text: refsText });
  await checkAsync('引用编号统计正确', () => {
    eq(refs.cites.length, 5, 'cites');
    eq(refs.uniqueCites, 4, 'uniqueCites');
    eq(refs.dois.includes('10.1000/abc'), true, 'dois 应归一化后包含 10.1000/abc');
  });
  check('八条引用对账规则全部命中', () => {
    const r = rules(refs);
    for (const rule of ['cite_gap', 'cite_duplicate', 'cite_count_mismatch', 'entry_missing_doi', 'entry_future_year', 'duplicate_doi', 'repeated_doi', 'cite_beyond_entries']) {
      assert(r.has(rule), `缺少规则 ${rule}，实际：${[...r].join(',')}`);
    }
  });
  check('年份/编号类问题是 error，重复类问题是 warn', () => {
    const lv = Object.fromEntries(refs.findings.map((f) => [f.rule, f.level]));
    eq(lv.cite_count_mismatch, 'error', 'cite_count_mismatch');
    eq(lv.entry_future_year, 'error', 'entry_future_year');
    eq(lv.duplicate_doi, 'error', 'duplicate_doi');
    eq(lv.cite_gap, 'warn', 'cite_gap');
    eq(lv.entry_missing_doi, 'warn', 'entry_missing_doi');
  });

  const cleanRefs = await verify.auditRefs({
    text: [
      '方法见文献[1]，另见[2]。',
      '',
      '## 参考文献',
      '[1] 张三. 某研究. 2020. doi:10.1000/x1',
      '[2] 李四. 某研究二. 2021. doi:10.1000/x2',
      '',
    ].join('\n'),
  });
  await checkAsync('干净引用不误报', () => {
    eq(cleanRefs.findings.length, 0, `不应有 findings：${JSON.stringify(cleanRefs.findings)}`);
    eq(cleanRefs.uniqueCites, 2, 'uniqueCites');
  });

  const empty = await verify.auditRefs({ text: '   ' });
  await checkAsync('空文本返回 empty_text', () => {
    assert(rules(empty).has('empty_text'), `规则缺失：${[...rules(empty)].join(',')}`);
  });

  // ---------------- 汇总 ----------------
  console.log(`\nverify: ${passed} passed, ${failed} failed`);
  if (failed > 0) {
    console.log('失败用例：');
    for (const f of failures) console.log(`  - ${f.name}: ${f.message}`);
  }
  process.exit(failed === 0 ? 0 : 1);
}

main().catch((err) => {
  console.error('测试脚本自身崩溃：', err);
  process.exit(1);
});
