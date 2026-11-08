/**
 * dsh-research-suite v3.2.0 · lib/docx.js
 *
 * 零依赖 DOCX 生成与审计（只依赖 node:fs / node:path / node:zlib）。
 *
 * 为什么自己拼 OOXML：
 *  - 插件随包分发、离线可用，不能依赖 python-docx / LibreOffice 才能出稿；
 *  - 期刊排版里真正卡人的是 7 个可机械核对的量（上标引用、字体、字号、行距、
 *    首行缩进、三线表、悬挂缩进），它们都能用 w:* 属性确定性表达，不需要
 *    任何模板文件；模板一进仓库就变成"必须拷某个 .dotx"，跨机器必坏。
 *
 * 对外只有两个函数：
 *   createDocx(core) -> { build, audit }
 *   build({ markdown | blocks, profile, meta, out })
 *   audit({ file, profile })
 *
 * 路径约定：out 只能落在 cwd 或 cwd/.dsh-research/ 之下，防止把文件写到
 * 用户没预期的位置；模块内不出现任何绝对路径（路径一律来自参数）。
 */

import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main';

/** 上标引用编号：[1]、[1-3]、[1,2]、[1–3]、[1，2]。 */
const CITE_RE = /\[\d+(?:\s*[-,–，]\s*\d+)*\]/g;

/** 每张表的最大列数，超过就按普通段落输出（避免窄到不可读）。 */
const MAX_TABLE_COLS = 8;

/**
 * 三套内置排版参数。全部以 OOXML 单位书写：
 *  - 页面与边距用 twip（1cm ≈ 566.93twip，1in = 1440twip）；
 *  - 字号用半磅（w:sz，12pt = 24）；
 *  - 行距用 w:line（240 = 单倍，360 = 1.5 倍，480 = 2 倍）。
 */
const PROFILES = {
  'zh-journal': {
    label: '中文期刊论著',
    pageW: 11906, // A4 21cm
    pageH: 16838, // A4 29.7cm
    margin: { top: 1417, bottom: 1417, left: 1701, right: 1134 }, // 2.5 / 2.5 / 3 / 2 cm
    eastAsia: '宋体',
    ascii: 'Times New Roman',
    headingEastAsia: '黑体',
    bodySize: 24, // 小四 12pt
    bodyLine: 360, // 1.5 倍
    firstLineChars: 200, // 2 字符
    headingSize: { 1: 30, 2: 28, 3: 24 }, // 15 / 14 / 12pt
    tableSize: 21, // 10.5pt
    refIndent: { left: 420, hanging: 420 },
    justify: true,
  },
  'en-sci': {
    label: '英文 SCI 稿',
    pageW: 11906,
    pageH: 16838,
    margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 }, // 1in
    eastAsia: 'Times New Roman',
    ascii: 'Times New Roman',
    headingEastAsia: 'Times New Roman',
    bodySize: 24,
    bodyLine: 480, // 双倍行距，审稿惯例
    firstLineChars: 0, // 英文段首不缩进
    headingSize: { 1: 28, 2: 24, 3: 24 },
    tableSize: 20, // 10pt
    refIndent: { left: 720, hanging: 720 },
    justify: true,
  },
  grant: {
    label: '标书',
    pageW: 11906,
    pageH: 16838,
    margin: { top: 1417, bottom: 1417, left: 1701, right: 1417 },
    eastAsia: '宋体',
    ascii: 'Times New Roman',
    headingEastAsia: '黑体',
    bodySize: 24,
    bodyLine: 360,
    firstLineChars: 200,
    headingSize: { 1: 32, 2: 28, 3: 24 }, // 16 / 14 / 12pt
    tableSize: 21,
    refIndent: { left: 420, hanging: 420 },
    justify: true,
  },
};

const DEFAULT_PROFILE = 'zh-journal';

// ---------------------------------------------------------------------------
// 通用小工具
// ---------------------------------------------------------------------------

function esc(text) {
  return String(text ?? '')
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function unesc(text) {
  return String(text ?? '')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, '&');
}

/** CRC32（zip 校验必需）。 */
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
  let c = -1;
  for (let i = 0; i < buf.length; i += 1) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ -1) >>> 0;
}

function dosDateTime(date = new Date()) {
  const time = ((date.getHours() & 0x1f) << 11) | ((date.getMinutes() & 0x3f) << 5) | (Math.floor(date.getSeconds() / 2) & 0x1f);
  const day = (((date.getFullYear() - 1980) & 0x7f) << 9) | (((date.getMonth() + 1) & 0x0f) << 5) | (date.getDate() & 0x1f);
  return { time, day };
}

/**
 * 写 zip：entries = [{ name, data }]。小文件用 deflateRaw，压不小就 store。
 * 只有它自己知道压缩率，所以每项独立决定 method，读侧按中央目录的 method 解。
 */
function zipWrite(entries) {
  const { time, day } = dosDateTime();
  const locals = [];
  const centrals = [];
  let offset = 0;

  for (const entry of entries) {
    const nameBuf = Buffer.from(entry.name, 'utf8');
    const raw = Buffer.isBuffer(entry.data) ? entry.data : Buffer.from(String(entry.data), 'utf8');
    const deflated = zlib.deflateRawSync(raw, { level: 9 });
    const useDeflate = deflated.length < raw.length;
    const body = useDeflate ? deflated : raw;
    const method = useDeflate ? 8 : 0;
    const crc = crc32(raw);

    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(0x0800, 6); // bit 11：文件名按 UTF-8 解释
    local.writeUInt16LE(method, 8);
    local.writeUInt16LE(time, 10);
    local.writeUInt16LE(day, 12);
    local.writeUInt32LE(crc, 14);
    local.writeUInt32LE(body.length, 18);
    local.writeUInt32LE(raw.length, 22);
    local.writeUInt16LE(nameBuf.length, 26);
    local.writeUInt16LE(0, 28);
    locals.push(local, nameBuf, body);

    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(20, 4);
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(0x0800, 8);
    central.writeUInt16LE(method, 10);
    central.writeUInt16LE(time, 12);
    central.writeUInt16LE(day, 14);
    central.writeUInt32LE(crc, 16);
    central.writeUInt32LE(body.length, 20);
    central.writeUInt32LE(raw.length, 24);
    central.writeUInt16LE(nameBuf.length, 28);
    central.writeUInt16LE(0, 30); // extra
    central.writeUInt16LE(0, 32); // comment
    central.writeUInt16LE(0, 34); // disk
    central.writeUInt16LE(0, 36); // internal attr
    central.writeUInt32LE(0, 38); // external attr
    central.writeUInt32LE(offset, 42);
    centrals.push(central, nameBuf);

    offset += local.length + nameBuf.length + body.length;
  }

  const centralBuf = Buffer.concat(centrals);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(0, 4);
  eocd.writeUInt16LE(0, 6);
  eocd.writeUInt16LE(entries.length, 8);
  eocd.writeUInt16LE(entries.length, 10);
  eocd.writeUInt32LE(centralBuf.length, 12);
  eocd.writeUInt32LE(offset, 16);
  eocd.writeUInt16LE(0, 20);

  return Buffer.concat([...locals, centralBuf, eocd]);
}

/** 读 zip：返回 Map<name, Buffer>；结构不认识就抛，由调用方翻成 not_a_docx。 */
function zipRead(buf) {
  let eocd = -1;
  for (let i = buf.length - 22; i >= 0; i -= 1) {
    if (buf.readUInt32LE(i) === 0x06054b50) {
      eocd = i;
      break;
    }
  }
  if (eocd < 0) throw new Error('缺 EOCD，不是 zip 容器');
  const count = buf.readUInt16LE(eocd + 10);
  let off = buf.readUInt32LE(eocd + 16);
  const out = new Map();
  for (let i = 0; i < count; i += 1) {
    if (buf.readUInt32LE(off) !== 0x02014b50) throw new Error('中央目录损坏');
    const method = buf.readUInt16LE(off + 10);
    const compSize = buf.readUInt32LE(off + 20);
    const nameLen = buf.readUInt16LE(off + 28);
    const extraLen = buf.readUInt16LE(off + 30);
    const commentLen = buf.readUInt16LE(off + 32);
    const localOff = buf.readUInt32LE(off + 42);
    const name = buf.toString('utf8', off + 46, off + 46 + nameLen);
    const localNameLen = buf.readUInt16LE(localOff + 26);
    const localExtraLen = buf.readUInt16LE(localOff + 28);
    const dataStart = localOff + 30 + localNameLen + localExtraLen;
    const body = buf.subarray(dataStart, dataStart + compSize);
    out.set(name, method === 8 ? zlib.inflateRawSync(body) : Buffer.from(body));
    off += 46 + nameLen + extraLen + commentLen;
  }
  return out;
}

// ---------------------------------------------------------------------------
// Markdown / blocks -> 内部块模型
// ---------------------------------------------------------------------------

function isCjk(ch) {
  return /[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uff00-\uffef]/.test(ch);
}

function joinLines(prev, line) {
  if (!prev) return line;
  const a = prev.slice(-1);
  const b = line.slice(0, 1);
  return isCjk(a) || isCjk(b) ? prev + line : `${prev} ${line}`;
}

function splitTableRow(line) {
  const trimmed = line.trim().replace(/^\|/, '').replace(/\|$/, '');
  return trimmed.split('|').map((cell) => cell.trim());
}

function isTableSeparator(line) {
  const cells = splitTableRow(line);
  return cells.length > 0 && cells.every((c) => /^:?-{2,}:?$/.test(c));
}

/**
 * 把 Markdown 解析成块。只认论文稿真正会用到的语法：
 * 标题、段落、无序/有序列表、表格、以及「参考文献」之后自动转成悬挂缩进条目。
 * 不做内联 HTML、脚注、引用块嵌套——那些在期刊稿里基本不出现，做了反而脆。
 */
function parseMarkdown(markdown) {
  const lines = String(markdown).replace(/\r\n?/g, '\n').split('\n');
  const blocks = [];
  let inFence = false;
  let inRefs = false;
  let para = '';

  const flushPara = () => {
    const text = para.trim();
    para = '';
    if (!text) return;
    blocks.push(inRefs ? { type: 'ref', text } : { type: 'p', text });
  };

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    if (/^\s*```/.test(line)) {
      inFence = !inFence;
      if (inFence) flushPara();
      continue;
    }
    if (inFence) {
      para = joinLines(para, line);
      continue;
    }
    if (!line.trim()) {
      flushPara();
      continue;
    }
    if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
      flushPara();
      continue;
    }

    const heading = /^(#{1,6})\s+(.+?)\s*#*\s*$/.exec(line);
    if (heading) {
      flushPara();
      const level = Math.min(3, heading[1].length);
      const text = heading[2].trim();
      inRefs = /^(参考文献|References?|REFERENCES)$/i.test(text);
      blocks.push({ type: 'h', level, text, refsHeading: inRefs });
      continue;
    }

    // 参考文献区：一条一行，逐条成段（Markdown 的软换行会把连续几行并成一段，
    // 那样三线表式的悬挂缩进就挂不上去，也无法逐条核对）。
    if (inRefs) {
      const text = line.trim().replace(/^[-*+]\s+/, '');
      if (text) {
        flushPara();
        blocks.push({ type: 'ref', text });
      }
      continue;
    }

    if (line.trim().startsWith('|')) {
      const rows = [];
      let j = i;
      while (j < lines.length && lines[j].trim().startsWith('|')) {
        rows.push(lines[j]);
        j += 1;
      }
      if (rows.length >= 2 && isTableSeparator(rows[1])) {
        flushPara();
        const header = splitTableRow(rows[0]);
        const body = rows.slice(2).map(splitTableRow);
        const tableRows = [header, ...body].filter((r) => r.length > 0);
        if (tableRows[0].length <= MAX_TABLE_COLS) blocks.push({ type: 'table', rows: tableRows });
        else for (const r of tableRows) blocks.push({ type: 'p', text: r.join('；') });
        i = j - 1;
        continue;
      }
    }

    const bullet = /^\s*[-*+]\s+(.*)$/.exec(line);
    if (bullet) {
      flushPara();
      blocks.push(inRefs ? { type: 'ref', text: bullet[1].trim() } : { type: 'bullet', text: bullet[1].trim() });
      continue;
    }

    const ordered = /^\s*(\d+)[.)]\s+(.*)$/.exec(line);
    if (ordered) {
      flushPara();
      blocks.push(inRefs ? { type: 'ref', text: ordered[2].trim() } : { type: 'ol', text: ordered[2].trim(), n: ordered[1] });
      continue;
    }

    const quote = /^>\s?(.*)$/.exec(line);
    para = joinLines(para, quote ? quote[1] : line.trim());
  }
  flushPara();
  return blocks;
}

function blocksFromArray(list) {
  const blocks = [];
  for (const item of list ?? []) {
    if (!item || typeof item !== 'object') continue;
    const type = String(item.type ?? 'p').toLowerCase();
    if (type === 'heading' || type === 'h') {
      const level = Math.min(3, Math.max(1, Number(item.level ?? 1)));
      const text = String(item.text ?? '').trim();
      if (text) blocks.push({ type: 'h', level, text, refsHeading: /^(参考文献|References?)$/i.test(text) });
    } else if (type === 'table') {
      const rows = (item.rows ?? []).map((r) => (Array.isArray(r) ? r.map(String) : String(r).split('|').map((c) => c.trim())));
      if (rows.length) blocks.push({ type: 'table', rows: rows.filter((r) => r.length) });
    } else if (type === 'bullets' || type === 'list') {
      for (const text of item.items ?? []) if (String(text).trim()) blocks.push({ type: 'bullet', text: String(text).trim() });
    } else if (type === 'references') {
      for (const text of item.items ?? []) if (String(text).trim()) blocks.push({ type: 'ref', text: String(text).trim() });
    } else {
      for (const text of String(item.text ?? '').split(/\n{2,}/)) {
        if (text.trim()) blocks.push({ type: 'p', text: text.trim() });
      }
    }
  }
  return blocks;
}

// ---------------------------------------------------------------------------
// 块 -> OOXML
// ---------------------------------------------------------------------------

function rPr(profile, kind, { bold = false, sup = false, size } = {}) {
  const heading = kind === 'h';
  const eastAsia = heading ? profile.headingEastAsia : profile.eastAsia;
  const ascii = heading ? profile.ascii : profile.ascii;
  const sz = size ?? (kind === 'table' ? profile.tableSize : heading ? 24 : profile.bodySize);
  const parts = [
    `<w:rFonts w:ascii="${esc(ascii)}" w:hAnsi="${esc(ascii)}" w:eastAsia="${esc(eastAsia)}" w:cs="${esc(ascii)}"/>`,
    bold || heading ? '<w:b/>' : '',
    `<w:sz w:val="${sz}"/><w:szCs w:val="${sz}"/>`,
    sup ? '<w:vertAlign w:val="superscript"/>' : '',
  ];
  return `<w:rPr>${parts.join('')}</w:rPr>`;
}

function inlineXml(text, profile, kind, { bold = false, size } = {}) {
  const parts = String(text).split(/(\*\*[^*]+\*\*|\*[^*\n]+\*|\[\d+(?:\s*[-,–，]\s*\d+)*\])/g);
  let xml = '';
  for (const raw of parts) {
    if (!raw) continue;
    const runXml = (chunk, opts) =>
      `<w:r>${rPr(profile, kind, { bold, size, ...opts })}<w:t xml:space="preserve">${esc(chunk)}</w:t></w:r>`;
    if (/^\*\*[^*]+\*\*$/.test(raw)) {
      xml += runXml(raw.slice(2, -2), { bold: true });
    } else if (/^\*[^*\n]+\*$/.test(raw)) {
      xml += runXml(raw.slice(1, -1), {});
    } else if (CITE_RE.test(raw)) {
      CITE_RE.lastIndex = 0;
      xml += runXml(raw, { sup: true });
    } else {
      xml += runXml(raw, {});
    }
  }
  return xml;
}

function pPr(profile, kind, { level = 1, align } = {}) {
  const base = [];
  if (kind === 'h') {
    base.push(`<w:pStyle w:val="Heading${level}"/>`, '<w:keepNext/>');
    base.push(`<w:spacing w:before="240" w:after="120" w:line="${profile.bodyLine}" w:lineRule="auto"/>`);
    base.push(`<w:jc w:val="${align ?? 'left'}"/>`);
    return `<w:pPr>${base.join('')}</w:pPr>`;
  }
  if (kind === 'ref') {
    base.push(`<w:spacing w:line="${profile.bodyLine}" w:lineRule="auto" w:before="0" w:after="0"/>`);
    base.push(`<w:ind w:left="${profile.refIndent.left}" w:hanging="${profile.refIndent.hanging}"/>`);
    base.push(`<w:jc w:val="${profile.justify ? 'both' : 'left'}"/>`);
    return `<w:pPr>${base.join('')}</w:pPr>`;
  }
  if (kind === 'table') {
    base.push('<w:spacing w:line="240" w:lineRule="auto" w:before="0" w:after="0"/>');
    base.push('<w:jc w:val="center"/>');
    return `<w:pPr>${base.join('')}</w:pPr>`;
  }
  if (kind === 'bullet') {
    base.push(`<w:spacing w:line="${profile.bodyLine}" w:lineRule="auto" w:before="0" w:after="0"/>`);
    base.push('<w:ind w:left="420" w:hanging="210"/>');
    base.push(`<w:jc w:val="${profile.justify ? 'both' : 'left'}"/>`);
    return `<w:pPr>${base.join('')}</w:pPr>`;
  }
  if (kind === 'ol') {
    base.push(`<w:spacing w:line="${profile.bodyLine}" w:lineRule="auto" w:before="0" w:after="0"/>`);
    base.push('<w:ind w:left="420" w:hanging="210"/>');
    base.push(`<w:jc w:val="${profile.justify ? 'both' : 'left'}"/>`);
    return `<w:pPr>${base.join('')}</w:pPr>`;
  }
  base.push(`<w:spacing w:line="${profile.bodyLine}" w:lineRule="auto" w:before="0" w:after="0"/>`);
  if (profile.firstLineChars) {
    // firstLine 与 firstLineChars 同时给：Word 优先用 chars，其余阅读器用绝对值兜底。
    const firstLine = Math.round(profile.bodySize * 10 * (profile.firstLineChars / 100));
    base.push(`<w:ind w:firstLineChars="${profile.firstLineChars}" w:firstLine="${firstLine}"/>`);
  }
  base.push(`<w:jc w:val="${align ?? (profile.justify ? 'both' : 'left')}"/>`);
  return `<w:pPr>${base.join('')}</w:pPr>`;
}

function paraXml(text, profile, kind, { level = 1, size, bold = false, marker } = {}) {
  const body = inlineXml(text, profile, kind, { bold, size });
  const prefix = marker ? `<w:r>${rPr(profile, kind, { size })}<w:t xml:space="preserve">${esc(marker)}</w:t></w:r>` : '';
  return `<w:p>${pPr(profile, kind, { level })}${prefix}${body}</w:p>`;
}

function tableXml(rows, profile) {
  const cols = Math.max(...rows.map((r) => r.length));
  const contentWidth = profile.pageW - profile.margin.left - profile.margin.right;
  const colWidth = Math.floor(contentWidth / cols);
  const borders = [
    // 子元素顺序按 CT_TblBorders 的 schema 来：top → left → bottom → right → insideH → insideV。
    // 竖线用「白色细线」而不是 w:val="nil"：LibreOffice 把 nil/none 当成「没有直接格式」而继续
    // 继承默认表格样式的网格线（渲染出来是可见竖线），Word/WPS 则会把 nil 当「无边框」。
    // 写成 1 磅白线后两边渲染一致：白底上不可见，且审计按「白色＝不呈现」判定。
    '<w:tblBorders>',
    '<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>',
    '<w:left w:val="single" w:sz="2" w:space="0" w:color="FFFFFF"/>',
    '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>',
    '<w:right w:val="single" w:sz="2" w:space="0" w:color="FFFFFF"/>',
    '<w:insideH w:val="single" w:sz="8" w:space="0" w:color="000000"/>',
    '<w:insideV w:val="single" w:sz="2" w:space="0" w:color="FFFFFF"/>',
    '</w:tblBorders>',
  ].join('');
  const rowsXml = rows
    .map((row, rowIndex) => {
      const cells = [];
      for (let c = 0; c < cols; c += 1) {
        const value = row[c] ?? '';
        const bold = rowIndex === 0;
        cells.push(
          `<w:tc><w:tcPr><w:tcW w:w="${colWidth}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>` +
            `<w:p>${pPr(profile, 'table')}${inlineXml(value, profile, 'table', { bold, size: profile.tableSize })}</w:p>` +
            '</w:tc>',
        );
      }
      const header = rowIndex === 0 ? '<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' : '<w:trPr><w:cantSplit/></w:trPr>';
      return `<w:tr>${header}${cells.join('')}</w:tr>`;
    })
    .join('');
  return (
    '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:jc w:val="center"/>' +
    borders +
    '<w:tblLayout w:type="fixed"/>' +
    '<w:tblCellMar><w:top w:w="57" w:type="dxa"/><w:left w:w="85" w:type="dxa"/>' +
    '<w:bottom w:w="57" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar>' +
    '</w:tblPr>' +
    `<w:tblGrid>${Array.from({ length: cols }, () => `<w:gridCol w:w="${colWidth}"/>`).join('')}</w:tblGrid>` +
    rowsXml +
    '</w:tbl>'
  );
}

function documentXml(blocks, profile) {
  const body = [];
  for (const block of blocks) {
    if (block.type === 'h') {
      const size = profile.headingSize[block.level] ?? profile.headingSize[3];
      body.push(`<w:p>${pPr(profile, 'h', { level: block.level })}${inlineXml(block.text, profile, 'h', { size })}</w:p>`);
    } else if (block.type === 'table') {
      body.push(tableXml(block.rows, profile));
      // 表格后补一个空段，避免连续两表粘在一起时 Word 把网格合并。
      body.push(`<w:p>${pPr(profile, 'p')}</w:p>`);
    } else if (block.type === 'bullet') {
      body.push(paraXml(block.text, profile, 'bullet', { marker: '• ' }));
    } else if (block.type === 'ol') {
      body.push(paraXml(block.text, profile, 'ol', { marker: `${block.n ?? 1}. ` }));
    } else if (block.type === 'ref') {
      body.push(paraXml(block.text, profile, 'ref'));
    } else {
      body.push(paraXml(block.text, profile, 'p'));
    }
  }

  const sect =
    '<w:sectPr>' +
    `<w:pgSz w:w="${profile.pageW}" w:h="${profile.pageH}"/>` +
    `<w:pgMar w:top="${profile.margin.top}" w:right="${profile.margin.right}" ` +
    `w:bottom="${profile.margin.bottom}" w:left="${profile.margin.left}" ` +
    'w:header="851" w:footer="992" w:gutter="0"/>' +
    '<w:cols w:space="425"/>' +
    '<w:docGrid w:type="lines" w:linePitch="312"/>' +
    '</w:sectPr>';

  return (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    `<w:document xmlns:w="${W_NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">` +
    `<w:body>${body.join('')}${sect}</w:body></w:document>`
  );
}

function stylesXml(profile) {
  const heading = (level) => {
    const size = profile.headingSize[level] ?? profile.headingSize[3];
    return (
      `<w:style w:type="paragraph" w:styleId="Heading${level}"><w:name w:val="heading ${level}"/>` +
      '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>' +
      '<w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="120" w:line="360" w:lineRule="auto"/>' +
      `<w:outlineLvl w:val="${level - 1}"/></w:pPr>` +
      `<w:rPr><w:rFonts w:ascii="${esc(profile.ascii)}" w:hAnsi="${esc(profile.ascii)}" ` +
      `w:eastAsia="${esc(profile.headingEastAsia)}"/><w:b/><w:sz w:val="${size}"/><w:szCs w:val="${size}"/></w:rPr>` +
      '</w:style>'
    );
  };
  return (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    `<w:styles xmlns:w="${W_NS}">` +
    '<w:docDefaults><w:rPrDefault><w:rPr>' +
    `<w:rFonts w:ascii="${esc(profile.ascii)}" w:hAnsi="${esc(profile.ascii)}" w:eastAsia="${esc(profile.eastAsia)}" ` +
    `w:cs="${esc(profile.ascii)}"/><w:sz w:val="${profile.bodySize}"/><w:szCs w:val="${profile.bodySize}"/>` +
    '</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>' +
    `<w:spacing w:line="${profile.bodyLine}" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>` +
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>' +
    `<w:pPr><w:spacing w:line="${profile.bodyLine}" w:lineRule="auto"/></w:pPr>` +
    `<w:rPr><w:rFonts w:ascii="${esc(profile.ascii)}" w:hAnsi="${esc(profile.ascii)}" ` +
    `w:eastAsia="${esc(profile.eastAsia)}"/><w:sz w:val="${profile.bodySize}"/></w:rPr></w:style>` +
    heading(1) +
    heading(2) +
    heading(3) +
    '<w:style w:type="table" w:styleId="TableNormal"><w:name w:val="Normal Table"/><w:qFormat/>' +
    '<w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar>' +
    '<w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/>' +
    '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/>' +
    '</w:tblCellMar></w:tblPr></w:style>' +
    '</w:styles>'
  );
}

function contentTypesXml(hasDocProps) {
  return (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' +
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>' +
    '<Default Extension="xml" ContentType="application/xml"/>' +
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>' +
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>' +
    (hasDocProps
      ? '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
      : '') +
    '</Types>'
  );
}

function rootRelsXml(hasDocProps) {
  return (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>' +
    (hasDocProps
      ? '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
      : '') +
    '</Relationships>'
  );
}

function documentRelsXml() {
  return (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' +
    '</Relationships>'
  );
}

function coreXml(meta) {
  const now = new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
  return (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" ' +
    'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" ' +
    'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">' +
    `<dc:title>${esc(meta.title ?? '')}</dc:title>` +
    `<dc:creator>${esc(meta.author ?? '')}</dc:creator>` +
    `<cp:lastModifiedBy>${esc(meta.author ?? '')}</cp:lastModifiedBy>` +
    '<cp:revision>1</cp:revision>' +
    `<dcterms:created xsi:type="dcterms:W3CDTF">${now}</dcterms:created>` +
    `<dcterms:modified xsi:type="dcterms:W3CDTF">${now}</dcterms:modified>` +
    '</cp:coreProperties>'
  );
}

// ---------------------------------------------------------------------------
// 审计：极简 XML 扫描
// ---------------------------------------------------------------------------

function parseRun(inner) {
  const rPrMatch = /<w:rPr>([\s\S]*?)<\/w:rPr>/.exec(inner);
  const rPrInner = rPrMatch ? rPrMatch[1] : '';
  const texts = [];
  const tre = /<w:t(?:\s[^>]*)?>([\s\S]*?)<\/w:t>/g;
  let tm;
  while ((tm = tre.exec(inner))) texts.push(unesc(tm[1]));
  return {
    text: texts.join(''),
    sup: /<w:vertAlign w:val="superscript"/.test(rPrInner),
    ascii: /<w:rFonts[^>]*w:ascii="([^"]*)"/.exec(rPrInner)?.[1] ?? null,
    eastAsia: /<w:rFonts[^>]*w:eastAsia="([^"]*)"/.exec(rPrInner)?.[1] ?? null,
    sz: Number(/<w:sz w:val="(\d+)"/.exec(rPrInner)?.[1] ?? 0),
  };
}

function parseParagraph(inner) {
  const pPrMatch = /<w:pPr>([\s\S]*?)<\/w:pPr>/.exec(inner);
  const pPrInner = pPrMatch ? pPrMatch[1] : '';
  const runs = [];
  const rre = /<w:r(?:\s[^>]*)?>([\s\S]*?)<\/w:r>/g;
  let rm;
  while ((rm = rre.exec(inner))) runs.push(parseRun(rm[1]));
  const spacingMatch = /<w:spacing[^>]*w:line="(\d+)"/.exec(pPrInner);
  const firstLineMatch = /<w:ind[^>]*w:firstLineChars="(\d+)"/.exec(pPrInner);
  const hangingMatch = /<w:ind[^>]*w:hanging="(\d+)"/.exec(pPrInner);
  const leftMatch = /<w:ind[^>]*w:left="(\d+)"/.exec(pPrInner);
  return {
    style: /<w:pStyle w:val="([^"]*)"/.exec(pPrInner)?.[1] ?? '',
    spacingLine: spacingMatch ? Number(spacingMatch[1]) : null,
    firstLineChars: firstLineMatch ? Number(firstLineMatch[1]) : null,
    hanging: hangingMatch ? Number(hangingMatch[1]) : null,
    left: leftMatch ? Number(leftMatch[1]) : null,
    runs,
    text: runs.map((r) => r.text).join(''),
  };
}

function parseParagraphs(xml) {
  const out = [];
  const re = /<w:p(?:\s[^>]*)?>([\s\S]*?)<\/w:p>/g;
  let m;
  while ((m = re.exec(xml))) out.push(parseParagraph(m[1]));
  return out;
}

function parseTables(xml) {
  const out = [];
  const re = /<w:tbl(?:\s[^>]*)?>([\s\S]*?)<\/w:tbl>/g;
  let m;
  while ((m = re.exec(xml))) {
    const borders = /<w:tblBorders>([\s\S]*?)<\/w:tblBorders>/.exec(m[1]);
    const sides = new Map();
    if (borders) {
      const bre = /<w:(top|bottom|insideH|left|right|insideV)\b([^>]*)\/?>/g;
      let bm;
      while ((bm = bre.exec(borders[1]))) {
        const attrs = bm[2] ?? '';
        const val = /w:val="([^"]*)"/.exec(attrs)?.[1] ?? 'single';
        const sz = Number(/w:sz="(\d+)"/.exec(attrs)?.[1] ?? 8);
        const color = (/w:color="([^"]*)"/.exec(attrs)?.[1] ?? '').toUpperCase();
        // 白色边框是「白底上不可见」的写法（见 tableXml 里的说明），判定为不呈现。
        const invisible = val === 'nil' || val === 'none' || sz <= 0 || color === 'FFFFFF' || color === 'WHITE';
        sides.set(bm[1], { val, sz, color, present: !invisible });
      }
    }
    out.push({ hasBorders: Boolean(borders), sides });
  }
  return out;
}

// ---------------------------------------------------------------------------
// createDocx
// ---------------------------------------------------------------------------

export function createDocx(core) {
  const pluginVersion = String(core?.stats?.version ?? '');

  /** 解析并校验输出路径：只能落在 cwd 或 cwd/.dsh-research/ 之下。 */
  function resolveOut(out) {
    const raw = String(out ?? '').trim();
    if (!raw) return { ok: false, reason: 'out_missing', detail: '必须给 out（目标 .docx 路径）' };
    if (!/\.docx$/i.test(raw)) return { ok: false, reason: 'bad_extension', detail: 'out 必须是 .docx 文件' };
    const cwd = process.cwd();
    const abs = path.resolve(cwd, raw);
    const rel = path.relative(cwd, abs);
    const insideCwd = rel !== '' && !rel.startsWith('..') && !path.isAbsolute(rel);
    const dshRoot = path.join(cwd, '.dsh-research');
    const relDsh = path.relative(dshRoot, abs);
    const insideDsh = relDsh !== '' && !relDsh.startsWith('..') && !path.isAbsolute(relDsh);
    if (!insideCwd && !insideDsh) {
      return { ok: false, reason: 'out_of_scope', detail: 'out 必须位于当前工作目录或其 .dsh-research/ 子目录下' };
    }
    return { ok: true, abs, dir: path.dirname(abs) };
  }

  function build(input = {}) {
    const profileName = String(input.profile ?? DEFAULT_PROFILE).trim() || DEFAULT_PROFILE;
    const profile = PROFILES[profileName];
    if (!profile) {
      return {
        ok: false,
        reason: 'bad_profile',
        detail: `不认识的 profile: ${profileName}，可选 ${Object.keys(PROFILES).join(' / ')}`,
      };
    }
    const meta = { title: '', author: '', ...(input.meta ?? {}) };
    const hasMarkdown = typeof input.markdown === 'string' && input.markdown.trim() !== '';
    const hasBlocks = Array.isArray(input.blocks) && input.blocks.length > 0;
    if (!hasMarkdown && !hasBlocks) {
      return { ok: false, reason: 'empty_input', detail: 'markdown 与 blocks 至少给一个，且不能为空' };
    }

    const blocks = hasMarkdown ? parseMarkdown(input.markdown) : blocksFromArray(input.blocks);

    // 文献表：meta.references 补齐到文末，正文有引用但没表就直接拒绝，不静默留空。
    const refs = Array.isArray(meta.references) ? meta.references.map((r) => String(r).trim()).filter(Boolean) : [];
    const hasRefsHeading = blocks.some((b) => b.type === 'h' && b.refsHeading);
    const inlineRefs = blocks.filter((b) => b.type === 'ref').length;
    const bodyCitations = countCitations(blocks);
    if (bodyCitations > 0 && refs.length + inlineRefs === 0) {
      return {
        ok: false,
        reason: 'references_missing',
        detail: `正文有 ${bodyCitations} 处引用编号，但没有文献表（meta.references 为空且正文没有参考文献节）`,
        citations: bodyCitations,
      };
    }
    // markdown 里已经写过「参考文献」节时，meta.references 只当补充来源，不重复追加整表。
    if (refs.length > 0 && !hasRefsHeading) {
      blocks.push({ type: 'h', level: 1, text: '参考文献', refsHeading: true });
      for (const ref of refs) blocks.push({ type: 'ref', text: ref });
    }
    const totalRefs = refs.length + inlineRefs;

    const out = resolveOut(input.out);
    if (!out.ok) return out;

    const tables = blocks.filter((b) => b.type === 'table').length;
    const paragraphs = blocks.filter((b) => b.type === 'p' || b.type === 'ref' || b.type === 'bullet' || b.type === 'ol' || b.type === 'h').length;

    const files = [
      { name: '[Content_Types].xml', data: contentTypesXml(true) },
      { name: '_rels/.rels', data: rootRelsXml(true) },
      { name: 'docProps/core.xml', data: coreXml(meta) },
      { name: 'word/document.xml', data: documentXml(blocks, profile) },
      { name: 'word/styles.xml', data: stylesXml(profile) },
      { name: 'word/_rels/document.xml.rels', data: documentRelsXml() },
    ];
    const buf = zipWrite(files);

    try {
      fs.mkdirSync(out.dir, { recursive: true });
      fs.writeFileSync(out.abs, buf);
    } catch (err) {
      return { ok: false, reason: 'write_failed', detail: `写文件失败: ${err.message}` };
    }

    return {
      ok: true,
      path: out.abs,
      bytes: buf.length,
      paragraphs,
      tables,
      citations: bodyCitations,
      profile: profileName,
      references: totalRefs,
      pluginVersion,
    };
  }

  function countCitations(blocks) {
    let n = 0;
    for (const block of blocks) {
      if (block.type === 'ref' || block.type === 'table') continue;
      CITE_RE.lastIndex = 0;
      const found = String(block.text ?? '').match(CITE_RE);
      if (found) n += found.length;
    }
    return n;
  }

  function audit(input = {}) {
    const file = String(input.file ?? '').trim();
    if (!file) return { ok: false, reason: 'file_missing', detail: '必须给 file（待审 .docx 路径）' };
    const abs = path.resolve(process.cwd(), file);
    let raw;
    try {
      raw = fs.readFileSync(abs);
    } catch (err) {
      return { ok: false, reason: 'not_a_docx', detail: `读不到文件: ${err.message}`, checks: [], summary: '无法读取' };
    }

    let zip;
    try {
      zip = zipRead(raw);
    } catch {
      return { ok: false, reason: 'not_a_docx', detail: '文件不是 zip 容器（docx 是 zip）', checks: [], summary: '不是 docx' };
    }
    const docBuf = zip.get('word/document.xml');
    if (!docBuf) {
      return { ok: false, reason: 'not_a_docx', detail: 'zip 里缺 word/document.xml', checks: [], summary: '不是 docx' };
    }

    const profileName = String(input.profile ?? DEFAULT_PROFILE).trim() || DEFAULT_PROFILE;
    const profile = PROFILES[profileName] ?? PROFILES[DEFAULT_PROFILE];
    const xml = docBuf.toString('utf8');
    const bodyMatch = /<w:body>([\s\S]*)<\/w:body>/.exec(xml);
    const bodyXml = bodyMatch ? bodyMatch[1] : xml;

    // 表格先摘出去，剩下的才是正文段落；否则表格内段落会被算进引用/行距统计。
    const tables = parseTables(bodyXml);
    const restXml = bodyXml.replace(/<w:tbl(?:\s[^>]*)?>[\s\S]*?<\/w:tbl>/g, '');
    const paras = parseParagraphs(restXml);

    const refIdx = paras.findIndex((p) => /^(参考文献|References?)\s*$/i.test(p.text.trim()));
    const bodyParas = refIdx >= 0 ? paras.slice(0, refIdx) : paras;
    const refParas = refIdx >= 0 ? paras.slice(refIdx + 1).filter((p) => p.text.trim()) : [];

    const checks = [];
    const push = (id, expect, actual, pass, level) => checks.push({ id, expect, actual, pass, level });

    // 1) 上标引用
    const cite = analyseCitations(bodyParas);
    push(
      'superscript-citations',
      '正文所有 [n] 引用都在 vertAlign=superscript 的 run 里，且上标 run 不含非引用文字',
      `正文引用 ${cite.total} 处：上标 ${cite.superscript} / 非上标 ${cite.plain}；上标 run 里非引用文字 ${cite.supExtra} 个`,
      cite.total === cite.superscript && cite.supExtra === 0,
      'error',
    );

    // 2) 字体
    const fontRuns = [];
    for (const p of bodyParas) {
      if (/^Heading\d+$/i.test(p.style)) continue;
      for (const r of p.runs) if (r.text.trim()) fontRuns.push(r);
    }
    const eastExpected = profileName === 'en-sci' ? ['Times New Roman'] : ['宋体', 'SimSun'];
    const asciiExpected = profileName === 'en-sci' ? ['Times New Roman', 'Arial'] : ['Times New Roman'];
    const eastBad = fontRuns.filter((r) => !r.eastAsia || !eastExpected.includes(r.eastAsia)).length;
    const asciiBad = fontRuns.filter((r) => !r.ascii || !asciiExpected.includes(r.ascii)).length;
    push(
      'fonts',
      `中文 ${eastExpected.join('/')}，西文 ${asciiExpected.join('/')}`,
      `正文 run ${fontRuns.length} 个：东亚洲字体不符 ${eastBad} 个，西文字体不符 ${asciiBad} 个`,
      fontRuns.length > 0 && eastBad === 0 && asciiBad === 0,
      'error',
    );

    // 3) 字号
    const sizes = [];
    for (const p of bodyParas) {
      if (/^Heading\d+$/i.test(p.style)) continue;
      for (const r of p.runs) if (r.text.trim() && r.sz > 0) sizes.push(r.sz);
    }
    const mode = modeOf(sizes);
    const small = sizes.filter((s) => s < 18).length;
    push(
      'font-size',
      '正文 w:sz ≥ 18（9pt）',
      sizes.length ? `最常用 ${mode} 半磅（${(mode / 2).toFixed(1)}pt），低于 18 半磅的 run ${small} 个` : '没有可读的字号信息',
      sizes.length > 0 && mode >= 18,
      'error',
    );

    // 4) 行距
    const bodyOnly = bodyParas.filter((p) => !/^Heading\d+$/i.test(p.style) && p.text.trim());
    const lines = bodyOnly.map((p) => p.spacingLine).filter((v) => v !== null);
    const lineBad = lines.filter((v) => v < 360).length;
    push(
      'line-spacing',
      '正文 w:spacing w:line ≥ 360（1.5 倍）',
      bodyOnly.length ? `正文段 ${bodyOnly.length} 段，有行距值 ${lines.length} 段，其中低于 360 的 ${lineBad} 段` : '没有正文段',
      bodyOnly.length > 0 && lineBad === 0,
      'warn',
    );

    // 5) 首行缩进（缺省继承算 pass，记在 actual 里）
    const indentParas = bodyOnly.filter((p) => !p.hanging);
    const explicit = indentParas.filter((p) => p.firstLineChars !== null && p.firstLineChars >= 200).length;
    const inherited = indentParas.filter((p) => p.firstLineChars === null).length;
    const indentBad = indentParas.length - explicit - inherited;
    push(
      'first-line-indent',
      '正文段 w:ind w:firstLineChars ≥ 200，或缺省继承',
      `正文段 ${indentParas.length} 段：显式 200 及以上 ${explicit} 段，缺省继承 ${inherited} 段，不足 200 的 ${indentBad} 段`,
      indentParas.length === 0 || indentBad === 0,
      'warn',
    );

    // 6) 三线表
    const threeLine = tables.filter((t) => t.hasBorders && t.sides.get('top')?.present && t.sides.get('bottom')?.present && t.sides.get('insideH')?.present);
    const withVertical = tables.filter((t) => ['left', 'right', 'insideV'].some((s) => t.sides.get(s)?.present));
    push(
      'table-borders',
      '三线表：有 top/bottom/insideH，无 left/right/insideV',
      tables.length ? `表 ${tables.length} 张：三线表 ${threeLine.length} 张，带竖线 ${withVertical.length} 张` : '文档没有表格',
      tables.length === 0 || (threeLine.length === tables.length && withVertical.length === 0),
      'error',
    );

    // 7) 文献表悬挂缩进
    const hangOk = refParas.filter((p) => p.hanging !== null && p.hanging >= 420).length;
    push(
      'hanging-indent',
      '文献表每条 w:ind w:hanging ≥ 420',
      refParas.length ? `文献 ${refParas.length} 条，悬挂缩进 ${hangOk} 条` : '没有文献表（跳过）',
      refParas.length === 0 || hangOk === refParas.length,
      'warn',
    );

    const failed = checks.filter((c) => !c.pass && c.level === 'error');
    const warned = checks.filter((c) => !c.pass && c.level === 'warn');
    const ok = failed.length === 0;
    const summary =
      `${checks.length} 项检查：通过 ${checks.filter((c) => c.pass).length}，失败 ${failed.length}，警告 ${warned.length}；` +
      `引用 ${cite.total} 处（上标 ${cite.superscript} / 非上标 ${cite.plain}），表 ${tables.length} 张，文献 ${refParas.length} 条`;
    return { ok, checks, summary, profile: profileName, file: abs, citations: cite, tables: tables.length };
  }

  return { build, audit };
}

/** 统计正文里的引用上标情况。 */
function analyseCitations(paras) {
  let total = 0;
  let superscript = 0;
  let plain = 0;
  let supExtra = 0;
  for (const p of paras) {
    const text = p.text;
    const covered = new Array(text.length).fill(false);
    CITE_RE.lastIndex = 0;
    let m;
    while ((m = CITE_RE.exec(text))) {
      total += 1;
      const start = m.index;
      const end = start + m[0].length;
      for (let i = start; i < end; i += 1) covered[i] = true;
      // 逐字符判定是否在 superscript run 内：引用可能跨 run 时按"全段上标"才算命中。
      let allSup = true;
      let cursor = 0;
      for (const r of p.runs) {
        const from = cursor;
        const to = cursor + r.text.length;
        cursor = to;
        if (to <= start || from >= end) continue;
        if (!r.sup) allSup = false;
      }
      if (allSup) superscript += 1;
      else plain += 1;
    }
    let cursor = 0;
    for (const r of p.runs) {
      for (let k = 0; k < r.text.length; k += 1) {
        const idx = cursor + k;
        if (r.sup && !covered[idx] && !/\s/.test(r.text[k])) supExtra += 1;
      }
      cursor += r.text.length;
    }
  }
  return {
    total,
    superscript,
    plain,
    supExtra,
    pass: total === superscript && supExtra === 0,
  };
}

function modeOf(values) {
  const counts = new Map();
  for (const v of values) counts.set(v, (counts.get(v) ?? 0) + 1);
  let best = 0;
  let bestCount = -1;
  for (const [value, count] of counts) {
    if (count > bestCount) {
      best = value;
      bestCount = count;
    }
  }
  return best;
}

export default createDocx;
