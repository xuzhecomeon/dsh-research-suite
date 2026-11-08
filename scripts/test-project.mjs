// scripts/test-project.mjs
// v3.2.0 项目级记忆（lib/project.js）的离线自测：全部用临时目录，不联网、不依赖第三方包、
// 不碰包内任何真实档案。
//
// 为什么这些用例值得单独写：
//   - 档案是「跨会话」状态，一旦被半截写入或静默覆盖，用户丢的是术语表和定稿段落，而且下一次
//     会话才发现，人工很难回溯。所以原子写、损坏恢复、非法输入不落盘三类必须有机械断言。
//   - terms / decisions / sections 是追加语义，去重键写错就会每次会话都把同一条术语再追加一遍，
//     档案越滚越大——这种退化在文本上看不出来，只能用重复 set 复现。
//   - options.project 多项目模式一旦允许 ../ 越界，就会在用户工作区之外写文件，属于必须拦死的一类。
//
// 运行：node scripts/test-project.mjs
// 通过标准：末尾打印 project: N passed, 0 failed，且 exit 0。

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { createProject, findTerm, hashText, SCHEMA_VERSION, ARCHIVE_DIR, ARCHIVE_FILE } from '../lib/project.js';

// ---------------------------------------------------------------------------
// 极简断言与用例登记（与 scripts/test-verify.mjs 同一套口径）
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

function assert(cond, message) {
  if (!cond) throw new Error(message);
}

function eq(actual, expected, label) {
  if (actual !== expected) throw new Error(`${label}: 期望 ${JSON.stringify(expected)}，实际 ${JSON.stringify(actual)}`);
}

function deepEq(actual, expected, label) {
  const a = JSON.stringify(actual);
  const b = JSON.stringify(expected);
  if (a !== b) throw new Error(`${label}: 期望 ${b}，实际 ${a}`);
}

// ---------------------------------------------------------------------------
// 临时工作区
// ---------------------------------------------------------------------------

const roots = [];

function makeRoot() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'dsh-project-'));
  roots.push(dir);
  return dir;
}

function cleanup() {
  for (const dir of roots) {
    try {
      fs.rmSync(dir, { recursive: true, force: true });
    } catch {
      /* 临时目录清理失败不影响判定 */
    }
  }
}

function archiveOf(root, sub) {
  return sub
    ? path.join(root, sub, ARCHIVE_DIR, ARCHIVE_FILE)
    : path.join(root, ARCHIVE_DIR, ARCHIVE_FILE);
}

function writeRaw(file, text) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, text, 'utf8');
}

function listTmp(dir) {
  try {
    return fs.readdirSync(dir).filter((name) => name.endsWith('.tmp'));
  } catch {
    return [];
  }
}

const SAMPLE = {
  project: '热射病大鼠模型',
  targetJournal: '中华急诊医学杂志',
  style: { citation: 'GB/T 7714-2015', superscript: true, language: 'zh', unitStyle: 'SI' },
  terms: [{ zh: '劳力型热射病', en: 'exertional heat stroke', abbr: 'EHS', firstUse: '引言第2段', note: '' }],
  decisions: [{ date: '2026-11-08', what: '讨论部分主张从 demonstrate 降为 show', why: '仅单组细胞实验', by: 'author' }],
};

// ---------------------------------------------------------------------------
// 用例
// ---------------------------------------------------------------------------

function main() {
  console.log('project-memory: lib/project.js');

  // ---------------- get：不存在时不落盘 ----------------
  console.log('\n[get 与不落盘]');

  check('首次 get 返回 exists:false 且不创建目录/文件', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    const r = p.get();
    eq(r.ok, true, 'ok');
    eq(r.exists, false, 'exists');
    eq(r.project, null, 'project');
    assert(!fs.existsSync(path.join(root, ARCHIVE_DIR)), '.dsh-research 目录被意外创建');
    eq(fs.readdirSync(root).length, 0, '工作区应仍是空目录');
  });

  check('首次 set 自动建目录并落盘', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    const r = p.set(SAMPLE);
    eq(r.ok, true, 'ok');
    eq(r.created, true, 'created');
    assert(fs.existsSync(archiveOf(root)), '档案文件未生成');
    eq(fs.existsSync(archiveOf(root) + '.bak'), false, '正常写入不应产生 .bak');
  });

  check('set 之后 get 往返一致', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    p.set(SAMPLE);
    const r = p.get();
    eq(r.ok, true, 'ok');
    eq(r.exists, true, 'exists');
    eq(r.project.project, SAMPLE.project, 'project');
    eq(r.project.targetJournal, SAMPLE.targetJournal, 'targetJournal');
    deepEq(r.project.style, SAMPLE.style, 'style');
    eq(r.project.terms[0].abbr, 'EHS', 'terms[0].abbr');
    eq(r.project.schemaVersion, SCHEMA_VERSION, 'schemaVersion');
    assert(typeof r.project.updatedAt === 'string' && r.project.updatedAt.includes('T'), 'updatedAt 应为 ISO 时间');
  });

  check('get 返回的是副本，改它不影响磁盘档案', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    p.set({ project: '原值' });
    const first = p.get();
    first.project.project = '被调用方改过';
    const second = p.get();
    eq(second.project.project, '原值', '磁盘上的值被外部篡改');
  });

  // ---------------- set：追加与浅合并 ----------------
  console.log('\n[set 合并语义]');

  check('terms 追加去重：同 zh 不重复追加', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    p.set({ terms: [{ zh: '劳力型热射病', en: 'exertional heat stroke' }] });
    p.set({ terms: [{ zh: '劳力型热射病', abbr: 'EHS' }, { zh: '经典热射病', abbr: 'CHS' }] });
    const { project } = p.get();
    eq(project.terms.length, 2, 'terms 条数');
    eq(project.terms[0].zh, '劳力型热射病', 'terms[0].zh');
    eq(project.terms[0].en, 'exertional heat stroke', '旧字段应保留');
    eq(project.terms[0].abbr, 'EHS', '同键更新应补上新字段');
    eq(project.terms[1].zh, '经典热射病', 'terms[1].zh');
  });

  check('同键更新只改该条，不动其它条目', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    p.set({ terms: [{ zh: '甲', note: '旧注' }, { zh: '乙', note: '乙注' }] });
    p.set({ terms: [{ zh: '甲', note: '新注' }] });
    const { project } = p.get();
    eq(project.terms.length, 2, '条数');
    eq(project.terms[0].note, '新注', '甲.note');
    eq(project.terms[1].note, '乙注', '乙.note 不应被牵连');
  });

  check('decisions 按 what 去重、sections 按 name 去重', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    p.set({
      decisions: [{ date: '2026-11-01', what: '限用动物模型结论', why: '无人体数据', by: 'author' }],
      sections: [{ name: '引言', status: 'draft' }],
    });
    p.set({
      decisions: [{ date: '2026-11-08', what: '限用动物模型结论', why: '补充：伦理限制', by: 'author' }],
      sections: [{ name: '引言', status: 'final' }, { name: '讨论', status: 'draft' }],
    });
    const { project } = p.get();
    eq(project.decisions.length, 1, 'decisions 条数');
    eq(project.decisions[0].date, '2026-11-08', '同键应更新 date');
    eq(project.sections.length, 2, 'sections 条数');
    eq(project.sections[0].status, 'final', '引言.status');
  });

  check('sections 传原文自动落 sha256 哈希且不回存正文', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    const text = '热射病（heat stroke）是以核心体温升高与中枢神经系统异常为特征的急症。';
    p.set({ sections: [{ name: '引言', status: 'final', text }] });
    const { project } = p.get();
    eq(project.sections[0].hash, hashText(text), 'hash');
    assert(/^sha256:[0-9a-f]{64}$/.test(project.sections[0].hash), `hash 形态不对：${project.sections[0].hash}`);
    eq('text' in project.sections[0], false, '正文不应入档');
  });

  check('浅合并顶层：再次 set 只给一个字段，其它字段保持', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    p.set({ project: '甲项目', targetJournal: '期刊乙' });
    p.set({ targetJournal: '期刊丙' });
    const { project } = p.get();
    eq(project.project, '甲项目', 'project');
    eq(project.targetJournal, '期刊丙', 'targetJournal');
  });

  // ---------------- set：校验 ----------------
  console.log('\n[set 校验]');

  check('非法类型拒写且磁盘内容不变', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    p.set({ project: '原值' });
    const before = fs.readFileSync(archiveOf(root), 'utf8');
    const r = p.set({ terms: '不是数组' });
    eq(r.ok, false, 'ok');
    eq(r.reason, 'invalid', 'reason');
    assert(Array.isArray(r.issues) && r.issues.length > 0, 'issues 应为非空数组');
    eq(r.issues[0].path, 'terms', 'issues[0].path');
    eq(fs.readFileSync(archiveOf(root), 'utf8'), before, '拒写时文件不应变化');
  });

  check('style 字段类型与未知字段都报 invalid', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    const bad = p.set({ style: { superscript: 'yes' } });
    eq(bad.ok, false, 'ok');
    eq(bad.issues[0].path, 'style.superscript', 'path');
    const unknown = p.set({ style: { doubleSpace: true } });
    eq(unknown.ok, false, 'ok');
    eq(unknown.issues[0].path, 'style.doubleSpace', 'path');
    assert(!fs.existsSync(archiveOf(root)), '非法输入不应建档案');
  });

  check('列表条目缺去重键或带未知字段报 invalid', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    const missing = p.set({ terms: [{ en: 'heat stroke' }] });
    eq(missing.ok, false, 'ok');
    eq(missing.issues[0].path, 'terms[0].zh', 'path');
    const unknown = p.set({ terms: [{ zh: '甲', foo: 'bar' }] });
    eq(unknown.ok, false, 'ok');
    eq(unknown.issues[0].path, 'terms[0].foo', 'path');
  });

  check('decisions 日期必须是 YYYY-MM-DD', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    const r = p.set({ decisions: [{ date: '2026/11/08', what: '某决定' }] });
    eq(r.ok, false, 'ok');
    eq(r.reason, 'invalid', 'reason');
    eq(r.issues[0].path, 'decisions[0].date', 'path');
  });

  // ---------------- 损坏恢复与原子写 ----------------
  console.log('\n[损坏恢复与原子写]');

  check('坏 JSON → corrupt，生成 .bak 且原文件不被覆盖或删除', () => {
    const root = makeRoot();
    const file = archiveOf(root);
    const garbage = '{ "schemaVersion": 1, "terms": [ 坏掉了 ';
    writeRaw(file, garbage);
    const p = createProject({}, { root });
    const r = p.get();
    eq(r.ok, false, 'ok');
    eq(r.reason, 'corrupt', 'reason');
    eq(r.backup, file + '.bak', 'backup 路径');
    eq(fs.readFileSync(file, 'utf8'), garbage, '原文件应保持不动');
    eq(fs.readFileSync(file + '.bak', 'utf8'), garbage, '.bak 应保存坏内容');
  });

  check('坏档时 set 同样拒写（不静默重建）', () => {
    const root = makeRoot();
    const file = archiveOf(root);
    writeRaw(file, 'not json at all');
    const p = createProject({}, { root });
    const r = p.set({ project: '新项目' });
    eq(r.ok, false, 'ok');
    eq(r.reason, 'corrupt', 'reason');
    eq(fs.readFileSync(file, 'utf8'), 'not json at all', '坏档不应被覆盖');
  });

  check('顶层不是对象的 JSON 也算损坏', () => {
    const root = makeRoot();
    const file = archiveOf(root);
    writeRaw(file, '[1, 2, 3]');
    const p = createProject({}, { root });
    eq(p.get().reason, 'corrupt', 'reason');
  });

  check('写盘失败不留半截文件（目标被同名目录占位）', () => {
    const root = makeRoot();
    const file = archiveOf(root);
    fs.mkdirSync(path.join(file, 'marker'), { recursive: true });
    const p = createProject({}, { root });
    const r = p.set({ project: '写不进去' });
    eq(r.ok, false, 'ok');
    eq(r.reason, 'io', 'reason');
    assert(fs.existsSync(path.join(file, 'marker')), '占位目录被破坏');
    eq(listTmp(path.dirname(file)).length, 0, '失败后不应残留 .tmp');
  });

  check('成功写盘后目录里没有 .tmp 残留', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    p.set(SAMPLE);
    p.set({ targetJournal: '另一本期刊' });
    eq(listTmp(path.dirname(archiveOf(root))).length, 0, '残留 .tmp');
    const names = fs.readdirSync(path.dirname(archiveOf(root)));
    eq(names.length, 1, `档案目录应只有 project.json，实际 ${names.join(',')}`);
  });

  // ---------------- diff ----------------
  console.log('\n[diff]');

  check('diff 三态：added / changed / removed 按 JSON 路径给出', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    p.set({
      targetJournal: '中华急诊医学杂志',
      terms: [{ zh: '甲', abbr: 'A1' }, { zh: '乙', abbr: 'B1' }],
    });
    const r = p.diff({
      targetJournal: '中华急诊医学杂志',
      terms: [{ zh: '甲', abbr: 'A2' }, { zh: '丙', abbr: 'C1' }],
    });
    eq(r.ok, true, 'ok');
    deepEq(r.added, ['terms[丙].abbr', 'terms[丙].zh'], 'added');
    deepEq(r.changed, ['terms[甲].abbr'], 'changed');
    deepEq(r.removed, ['terms[乙].abbr', 'terms[乙].zh'], 'removed');
  });

  check('diff 接受档案文件路径，且忽略 updatedAt / schemaVersion 噪声', () => {
    const root = makeRoot();
    const other = path.join(root, 'other.json');
    const p = createProject({}, { root });
    p.set({ project: '甲', terms: [{ zh: '甲' }] });
    writeRaw(other, JSON.stringify({ project: '乙', terms: [{ zh: '甲' }], updatedAt: '2000-01-01T00:00:00.000Z' }));
    const r = p.diff(other);
    eq(r.ok, true, 'ok');
    deepEq(r.changed, ['project'], 'changed');
    deepEq(r.added, [], 'added');
    deepEq(r.removed, [], 'removed');
  });

  check('diff 对不存在的文件与非法 JSON 返回 invalid', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    const r = p.diff(path.join(root, 'nope.json'));
    eq(r.ok, false, 'ok');
    eq(r.reason, 'invalid', 'reason');
  });

  // ---------------- list ----------------
  console.log('\n[list]');

  check('list 枚举 root 自身与一级子项目', () => {
    const root = makeRoot();
    createProject({}, { root }).set({ project: '根项目' });
    createProject({}, { root, project: 'proj-a' }).set({ project: 'A 项目' });
    createProject({}, { root, project: 'proj-b' }).set({ project: 'B 项目' });
    const r = createProject({}, { root }).list();
    eq(r.ok, true, 'ok');
    eq(r.projects.length, 3, `projects 条数：${r.projects.map((x) => x.project).join('|')}`);
    deepEq(r.projects.map((x) => x.project).sort(), ['A 项目', 'B 项目', '根项目'], '项目名集合');
    assert(r.projects.every((x) => fs.existsSync(x.path)), '每个条目都应给出可读 path');
  });

  check('list 跳过坏档，不影响其它项目', () => {
    const root = makeRoot();
    createProject({}, { root }).set({ project: '好项目' });
    writeRaw(archiveOf(root, 'broken'), '{ 坏');
    const r = createProject({}, { root }).list();
    eq(r.projects.length, 1, 'projects 条数');
    eq(r.projects[0].project, '好项目', 'project');
  });

  // ---------------- findTerm ----------------
  console.log('\n[findTerm]');

  const glossary = {
    terms: [
      { zh: '劳力型热射病', en: 'exertional heat stroke', abbr: 'EHS', firstUse: '引言第2段', note: '' },
      { zh: '核心体温', en: 'core temperature', abbr: '', firstUse: '方法第1段', note: '' },
    ],
  };

  check('findTerm 三种写法都能命中并标明命中形式', () => {
    const zhHit = findTerm(glossary, '本文纳入劳力型热射病患者 42 例。');
    eq(zhHit.length, 1, 'zh 命中数');
    eq(zhHit[0].matchedBy, 'zh', 'matchedBy');
    eq(zhHit[0].matchedForm, '劳力型热射病', 'matchedForm');

    const enHit = findTerm(glossary, 'Patients with exertional heat stroke were enrolled.');
    eq(enHit.length, 1, 'en 命中数');
    eq(enHit[0].matchedBy, 'en', 'matchedBy');

    const abbrHit = findTerm(glossary, 'EHS 组 21 例，对照组 21 例。');
    eq(abbrHit.length, 1, 'abbr 命中数');
    eq(abbrHit[0].matchedBy, 'abbr', 'matchedBy');
    eq(abbrHit[0].term.zh, '劳力型热射病', 'term.zh');
  });

  check('findTerm 透传 firstUse 供「已定义于 X 段」提示', () => {
    const hits = findTerm(glossary, '劳力型热射病（EHS）在讨论部分再次出现。');
    eq(hits.length, 1, '同一术语只报一次');
    eq(hits[0].firstUse, '引言第2段', 'firstUse');
    assert(hits[0].firstUse, 'firstUse 不应为空');
  });

  check('findTerm 边界：缩写不在更长单词里命中', () => {
    eq(findTerm(glossary, 'EHSS 是另一个东西。').length, 0, 'EHSS 不应命中 EHS');
    eq(findTerm(glossary, 'SHEHSX').length, 0, '嵌入字母串不应命中');
  });

  check('findTerm 无命中返回空数组，非字符串入参不抛异常', () => {
    deepEq(findTerm(glossary, '这段没有术语。'), [], '无命中');
    deepEq(findTerm(glossary, null), [], 'null');
    deepEq(findTerm(null, '甲'), [], 'project 为空');
  });

  // ---------------- 版本与时间 ----------------
  console.log('\n[版本与时间]');

  check('schemaVersion 自动补齐为 1', () => {
    const root = makeRoot();
    writeRaw(archiveOf(root), JSON.stringify({ project: '旧档案', terms: [] }));
    const r = createProject({}, { root }).get();
    eq(r.ok, true, 'ok');
    eq(r.project.schemaVersion, SCHEMA_VERSION, 'schemaVersion');
  });

  check('updatedAt 每次 set 都推进', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    const first = p.set({ project: '甲' }).project.updatedAt;
    const second = p.set({ targetJournal: '乙' }).project.updatedAt;
    assert(first && second, 'updatedAt 应存在');
    assert(Date.parse(second) > Date.parse(first), `时间未推进：${first} → ${second}`);
  });

  check('同进程连续两次 set 不互相覆盖', () => {
    const root = makeRoot();
    const p = createProject({}, { root });
    p.set({ terms: [{ zh: '第一次' }] });
    p.set({ terms: [{ zh: '第二次' }] });
    const { project } = p.get();
    deepEq(project.terms.map((t) => t.zh), ['第一次', '第二次'], '两次写入都应保留');
  });

  // ---------------- 路径越界 ----------------
  console.log('\n[路径越界]');

  check('options.project 带 ../ 时拒绝读写且不落到 root 之外', () => {
    const root = makeRoot();
    const outsideFile = path.join(path.dirname(root), 'dsh-escape-check', ARCHIVE_DIR, ARCHIVE_FILE);
    const p = createProject({}, { root, project: '../dsh-escape-check' });
    const g = p.get();
    eq(g.ok, false, 'get.ok');
    eq(g.reason, 'outside', 'get.reason');
    const s = p.set({ project: '越界' });
    eq(s.ok, false, 'set.ok');
    eq(s.reason, 'outside', 'set.reason');
    assert(!fs.existsSync(outsideFile), '写到了 root 之外');
  });

  // ---------------- 汇总 ----------------
  console.log(`\nproject: ${passed} passed, ${failed} failed`);
  if (failed > 0) {
    console.log('失败用例：');
    for (const f of failures) console.log(`  - ${f.name}: ${f.message}`);
  }
  cleanup();
  process.exit(failed === 0 ? 0 : 1);
}

try {
  main();
} catch (err) {
  console.error('测试脚本自身崩溃：', err);
  cleanup();
  process.exit(1);
}
