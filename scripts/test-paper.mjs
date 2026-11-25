// scripts/test-paper.mjs
// v3.4.0 论文工坊（lib/paper.js）的离线自测：全部用临时目录，不联网、不编译 LaTeX、
// 不碰包内任何真实稿件。
//
// 为什么这些用例值得单独写：
//   - 状态机一旦把阶段写错或把门禁状态搞混，用户会在「以为已经到投稿」的地方丢一整天；
//   - 账本判读与审稿判分是机械底线，错判一次就会把无证据的主张放进正文；
//   - lint 的越界检查必须拦死，否则一次手滑就能把工作区外的文件读进来。
//
// 运行：node scripts/test-paper.mjs
// 通过标准：末尾打印 paper: N passed, 0 failed，且 exit 0。

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import { createPaper, STAGES, GATES } from '../lib/paper.js';

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

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

const ROOT = fs.mkdtempSync(path.join(os.tmpdir(), 'dsh-paper-test-'));
const cleanup = () => {
  try {
    fs.rmSync(ROOT, { recursive: true, force: true });
  } catch {
    /* 忽略清理失败 */
  }
};

function fresh() {
  fs.rmSync(path.join(ROOT, '.dsh-research'), { recursive: true, force: true });
  return createPaper({ root: ROOT });
}

function write(rel, text) {
  const file = path.join(ROOT, rel);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, text, 'utf8');
  return file;
}

function stateOf() {
  return JSON.parse(fs.readFileSync(path.join(ROOT, '.dsh-research', 'paper', 'state.json'), 'utf8'));
}

function main() {
  console.log(`paper 工坊自测（临时目录 ${ROOT}）`);

  // ---------------- 状态机 ----------------
  check("状态机：init、status 与重复 init", () => {
    const p = fresh();
    const out = p.runAction('status');
    assert(out.includes('尚未初始化'), '未初始化时应提示 init');

    const init = p.runAction('init', { title: '测试稿', venue: 'NeurIPS' });
    assert(init.includes('已初始化'), 'init 应成功');
    const st = stateOf();
    assert(st.stage === 'intake', `初始阶段应为 intake，实际 ${st.stage}`);
    assert(st.title === '测试稿' && st.venue === 'NeurIPS', 'init 应写入标题与 venue');
    for (const g of GATES) assert(st.gates[g] === 'pending', `门禁 ${g} 初始应为 pending`);
    for (const s of STAGES) assert(typeof s === 'string' && s, '阶段表不应为空');

    const again = p.runAction('init', { title: '覆盖试试' });
    assert(again.includes('已存在'), '重复 init 应拒绝覆盖');
    assert(stateOf().title === '测试稿', '重复 init 不应改标题');
  });

  // ---------------- 阶段推进与门禁 ----------------
  check("阶段推进、门禁记录与回退", () => {
    const p = fresh();
    p.runAction('init', {});
    const bad = p.runAction('stage', { stage: 'nope' });
    assert(bad.includes('阶段无效'), '非法阶段应被拒绝');

    const plan = p.runAction('stage', { stage: 'plan' });
    assert(plan.includes('阶段已设为：plan'), '应能进入 plan');
    assert(stateOf().stage === 'plan', '状态文件应记录 plan');

    const draft = p.runAction('stage', { stage: 'draft' });
    assert(draft.includes('⚠'), '缺 claims/figures 门禁时应告警');
    assert(draft.includes('claims'), '告警应点名 claims');

    p.runAction('gate', { gate: 'claims', result: 'passed' });
    assert(stateOf().gates.claims === 'passed', 'claims 门禁应记为 passed');

    const badGate = p.runAction('gate', { gate: 'nope', result: 'passed' });
    assert(badGate.includes('门禁名无效'), '非法门禁应被拒绝');
    const badResult = p.runAction('gate', { gate: 'claims', result: 'maybe' });
    assert(badResult.includes('门禁状态无效'), '非法门禁状态应被拒绝');

    p.runAction('gate', { gate: 'figures', result: 'passed' });
    const okDraft = p.runAction('stage', { stage: 'draft' });
    assert(okDraft.includes('阶段已设为：draft'), '两门禁齐后可进 draft');
    assert(!okDraft.includes('⚠'), '门禁齐后不应再告警');
    assert(stateOf().gates.claims === 'passed', '门禁状态不应被阶段推进清掉');

    const back = p.runAction('stage', { stage: 'intake' });
    assert(back.includes('回退'), '回退阶段应提示');
    assert(stateOf().history.length >= 3, 'history 应记录阶段变更');
  });

  // ---------------- 主张账本 ----------------
  check("主张账本：四档判定与阻断项", () => {
    const p = fresh();
    p.runAction('init', {});
    assert(p.runAction('ledger').includes('没找到'), '无账本时应给出友好提示');

    write('paper/plan/CLAIM_LEDGER.json', JSON.stringify({
      claims: [
        { id: 'C1', claim: '方法在三个基准上超过基线', status: 'verified', evidence: 'tab:main' },
        { id: 'C2', claim: '训练成本降低 40%', status: 'no-evidence' },
        { id: 'C3', claim: '所有数据集都有效', status: 'contradicted', evidence: 'app:dataset' },
        { id: 'C4', claim: '在长文本上略好', status: 'partial' },
      ],
    }));
    const out = p.runAction('ledger');
    assert(out.includes('verified 1'), `应统计 verified，实际输出：${out.slice(0, 120)}`);
    assert(out.includes('no-evidence 1') && out.includes('contradicted 1'), '应统计两类阻断状态');
    assert(out.includes('结论：FAIL'), '有阻断项应判 FAIL');
    assert(out.includes('C2') && out.includes('C3'), '应点名阻断条目');
    assert(stateOf().artifacts.claims, '应把账本路径写进 artifacts');

    write('paper/plan/CLAIM_LEDGER.json', JSON.stringify([
      { claim: '主张一', verdict: 'yes', evidence: 'tab:1' },
      { claim: '主张二', verdict: 'partial' },
    ]));
    const warn = p.runAction('ledger');
    assert(warn.includes('结论：WARN'), '只有 partial 时应判 WARN');
    assert(warn.includes('需要弱化表述'), 'partial 应给出降调清单');

    write('paper/plan/CLAIM_LEDGER.json', '{ not json');
    assert(p.runAction('ledger').includes('不是合法 JSON'), '坏账本应给出解析错误');
  });

  // ---------------- 机械核验 ----------------
  check("机械核验：占位符、引用键、空章节、环境配对、越界", () => {
    const p = fresh();
    p.runAction('init', {});
    write('sections/clean.tex', '\\section{Introduction}\nWe study the problem and report results.~\cite{vaswani2017}\n');
    write('paper/plan/refs.bib', '@inproceedings{vaswani2017, title={Attention}}\n');
    const clean = p.runAction('lint', { path: 'sections', bib: 'paper/plan/refs.bib' });
    assert(clean.includes('结论：PASS'), `干净稿应 PASS，实际：${clean.slice(0, 160)}`);

    write('sections/bad.tex', [
      '\\section{Introduction}',
      'We propose a TODO approach with SOTA results~\\cite{missing2024}.',
      '\\section{Empty}',
      '\\section{Method}',
      '\\begin{figure}',
    ].join('\n'));
    const badOut = p.runAction('lint', { path: 'sections/bad.tex', bib: 'paper/plan/refs.bib' });
    assert(badOut.includes('TODO_MARKER'), '应命中占位符');
    assert(badOut.includes('CITE_UNKNOWN'), '应命中未解析引用键');
    assert(badOut.includes('EMPTY_SECTION'), '应命中空章节');
    assert(badOut.includes('ENV_MISMATCH'), '应命中环境不配对');
    assert(badOut.includes('PRIORITY_WORD'), '应提示绝对化措辞');
    assert(badOut.includes('结论：FAIL'), '有错误应判 FAIL');

    const escape = p.runAction('lint', { path: '../../package.json' });
    assert(escape.includes('越界'), '越界路径必须拒绝');
  });

  // ---------------- 审稿判分 ----------------
  check("审稿判分：阈值、阻断项与报告格式", () => {
    const p = fresh();
    p.runAction('init', {});
    assert(p.runAction('review').includes('没找到'), '无审稿报告时应提示');

    // Markdown 不认，必须是 JSON
    write('paper/review/REVIEW_REPORT.json', '# 审稿意见\n总分 7\n');
    assert(p.runAction('review').includes('不是合法 JSON'), 'Markdown 报告应被拒绝');

    write('paper/review/REVIEW_REPORT.json', JSON.stringify({
      round: 1,
      scores: { soundness: 5, novelty: 4, clarity: 6, evidence: 4, repro: 5 },
      verdict: 'revise',
      blocking: [{ id: 'B1', problem: '主结果缺消融', fix: '补三组消融' }],
    }));
    const fail = p.runAction('review');
    assert(fail.includes('结论：FAIL'), '低分加阻断项应 FAIL');
    assert(fail.includes('主结果缺消融'), '应列出阻断项');
    assert(stateOf().gates.review === 'failed', 'FAIL 应把 review 门禁记为 failed');

    write('paper/review/REVIEW_REPORT.json', JSON.stringify({
      round: 2,
      overall: 6.2,
      verdict: 'almost',
      blocking: [],
      non_blocking: ['补一句 limitation'],
    }));
    const pass = p.runAction('review');
    assert(pass.includes('结论：PASS'), '达标应 PASS');
    assert(stateOf().gates.review === 'passed', 'PASS 应把 review 门禁记为 passed');
    assert(stateOf().artifacts.review, '应把报告路径写进 artifacts');

    write('paper/review/REVIEW_REPORT.json', JSON.stringify({ overall: 11, verdict: 'ready', blocking: [] }));
    assert(p.runAction('review').includes('越界'), '总分越界应被拒绝');

    write('paper/review/REVIEW_REPORT.json', JSON.stringify({ scores: { a: 6 }, verdict: 'ready', blocking: [] }));
    assert(p.runAction('review').includes('PASS'), '无 overall 时用五维均值判分');
  });

  // ---------------- 下一步建议 ----------------
  check("下一步建议", () => {
    const p = fresh();
    p.runAction('init', {});
    p.runAction('stage', { stage: 'review' });
    assert(p.runAction('next').includes('research_paper action=review'), 'review 阶段应指向判分动作');
    p.runAction('stage', { stage: 'submission' });
    assert(p.runAction('next').includes('还没到投稿'), '门禁未过时不应鼓励投稿');
  });

  console.log(`\npaper: ${passed} passed, ${failed} failed`);
  if (failed > 0) {
    console.log('失败用例：');
    for (const f of failures) console.log(`  - ${f.name}: ${f.message}`);
  }
}

try {
  main();
} catch (err) {
  console.error('测试脚本自身崩溃：', err);
  failed += 1;
} finally {
  cleanup();
}
process.exit(failed === 0 ? 0 : 1);
