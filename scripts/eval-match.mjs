#!/usr/bin/env node
/**
 * eval-match.mjs —— 识别层评估（v3.2.0）
 *
 * 读 data/golden/dev.json（调参集）或 data/golden/test.json（盲测集，已冻结），
 * 逐条调用 lib/core.js 的 matchCapabilities()，输出混淆矩阵 + 分类别指标。
 *
 * 用法
 *   node scripts/eval-match.mjs                  # 默认 --set test，只报数
 *   node scripts/eval-match.mjs --set dev        # 调参集（永不受 --strict 影响）
 *   node scripts/eval-match.mjs --set test --strict   # 门槛不过 exit 1（CI 用）
 *   node scripts/eval-match.mjs --json           # 机器可读（CI 解析）
 *   node scripts/eval-match.mjs -v               # 逐条打印判定明细
 *
 * 指标口径（与 docs/EVAL.md 一致）
 *   接管判定准确率 = (期望接管的科研诉求被接管 + 期望不接管的非科研诉求未被接管) / 全部
 *   误接管率       = 非科研诉求被接管的条数 / 非科研诉求条数（越低越好，门槛 ≤0.03）
 *   科研诉求召回   = 科研诉求被接管的条数 / 科研诉求条数
 *   卡 top1        = 候选第一位命中期望卡（cap 或 alts）的科研诉求占比
 *   卡 top3        = 候选前三位含期望卡的科研诉求占比
 *
 * 说明：top1/top3 在 candidates（恒有前三个候选）上计算，因此即使接管判定失败也能看出
 * 「排序对不对」；这比只在 matches 上算更能区分「漏接管」与「排序错」两类失败。
 */
import { readFileSync, existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createCore } from '../lib/core.js'

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const argv = process.argv.slice(2)
const has = (f) => argv.includes(f)
const arg = (f, d) => {
  const i = argv.indexOf(f)
  return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : d
}

const SET = arg('--set', 'test')
const WANT_JSON = has('--json')
const VERBOSE = has('-v') || has('--verbose')
// dev 集只报数：调参集一旦参与门禁，就会变成「对着门槛调题」，盲测集随之失效。
const STRICT = has('--strict') && SET !== 'dev'
const STRICT_IGNORED = has('--strict') && SET === 'dev'

if (!['dev', 'test'].includes(SET)) {
  console.error(`--set 只接受 dev 或 test，收到 ${JSON.stringify(SET)}`)
  process.exit(2)
}

const setPath = path.join(root, 'data', 'golden', `${SET}.json`)
if (!existsSync(setPath)) {
  console.error(`找不到 ${path.relative(root, setPath)}`)
  process.exit(2)
}
const golden = JSON.parse(readFileSync(setPath, 'utf8'))
const cases = golden.cases || []

const core = createCore(root)

const THRESHONDS = {
  accuracy: 0.92,
  falseTakeover: 0.03,
  recall: 0.90,
  top1: 0.80,
  top3: 0.95,
}

const rows = []
for (const c of cases) {
  const expectNo = Boolean(c.expect && c.expect.noTakeover === true)
  const want = new Set([c.expect && c.expect.cap, ...((c.expect && c.expect.alts) || [])].filter(Boolean))
  let r
  try {
    r = core.matchCapabilities(c.utterance, { limit: 3 })
  } catch (e) {
    r = { takeover: false, candidates: [], matches: [], domain: null, score: 0, reason: `MATCH ERROR: ${e.message}` }
  }
  const take = r.takeover === true
  const cands = (r.candidates || []).map((x) => x.cap && x.cap.id).filter(Boolean)
  const got = (r.matches || []).map((x) => x.cap && x.cap.id).filter(Boolean)
  const decisionOk = expectNo ? !take : take
  const top1 = expectNo ? null : want.has(cands[0])
  const top3 = expectNo ? null : cands.slice(0, 3).some((id) => want.has(id))
  const domainOk = expectNo ? null : r.domain === c.expect.domain
  rows.push({
    id: c.id,
    utterance: c.utterance,
    category: c.category || '(未分类)',
    source: c.source,
    expectNo,
    want: [...want],
    expectDomain: c.expect && c.expect.domain,
    take,
    got,
    cands,
    domain: r.domain,
    score: r.score,
    confidence: r.confidence,
    reason: r.reason,
    decisionOk,
    domainOk,
    top1,
    top3,
  })
}

const pos = rows.filter((r) => !r.expectNo)
const neg = rows.filter((r) => r.expectNo)
const tp = pos.filter((r) => r.take).length
const fn = pos.length - tp
const fp = neg.filter((r) => r.take).length
const tn = neg.length - fp

const metrics = {
  total: rows.length,
  positives: pos.length,
  negatives: neg.length,
  accuracy: rows.length ? (tp + tn) / rows.length : 0,
  falseTakeover: neg.length ? fp / neg.length : 0,
  recall: pos.length ? tp / pos.length : 0,
  top1: pos.length ? pos.filter((r) => r.top1).length / pos.length : 0,
  top3: pos.length ? pos.filter((r) => r.top3).length / pos.length : 0,
  domain: pos.length ? pos.filter((r) => r.domainOk).length / pos.length : 0,
  // 接管成功的正例里，卡排第一/前三的比例（衡量「接对了但排错」）
  top1WhenTaken: tp ? pos.filter((r) => r.take && r.top1).length / tp : 0,
  top3WhenTaken: tp ? pos.filter((r) => r.take && r.top3).length / tp : 0,
}

// ── 分类别统计 ─────────────────────────────────────────────────────────
const cats = [...new Set(rows.map((r) => r.category))].sort()
const perCategory = cats.map((cat) => {
  const rs = rows.filter((r) => r.category === cat)
  const p = rs.filter((r) => !r.expectNo)
  const n = rs.filter((r) => r.expectNo)
  const pt = p.filter((r) => r.take).length
  const nf = n.filter((r) => r.take).length
  const fails = rs
    .filter((r) => !r.decisionOk || (!r.expectNo && !r.top3))
    .slice(0, 3)
    .map((r) => ({
      id: r.id,
      utterance: r.utterance,
      expect: r.expectNo ? 'noTakeover' : `${r.expectDomain}/${r.want[0]}`,
      actual: r.take ? `${r.domain || '?'}/${(r.got[0] || r.cands[0] || '?')}` : 'noTakeover',
      fail: failType(r),
    }))
  return {
    category: cat,
    n: rs.length,
    positives: p.length,
    negatives: n.length,
    recall: p.length ? pt / p.length : null,
    falseTakeover: n.length ? nf / n.length : null,
    top1: p.length ? p.filter((r) => r.top1).length / p.length : null,
    top3: p.length ? p.filter((r) => r.top3).length / p.length : null,
    decisionAccuracy: rs.length ? rs.filter((r) => r.decisionOk).length / rs.length : null,
    fails,
  }
})

function failType(r) {
  if (r.expectNo) return r.take ? '误接管' : 'ok'
  if (!r.take) return '漏接管'
  if (r.domain !== r.expectDomain) return '域错'
  if (!r.top3) return '卡错'
  if (!r.top1) return '卡错（前三内）'
  return 'ok'
}

// 全部失败条目（供 docs/EVAL.md 附录直接抄）
const failures = rows
  .filter((r) => !r.decisionOk || (!r.expectNo && !r.top3))
  .map((r) => ({
    id: r.id,
    category: r.category,
    utterance: r.utterance,
    expect: r.expectNo ? '不接管' : `${r.expectDomain} / ${r.want[0]}${r.want.length > 1 ? '（含 alts）' : ''}`,
    actual: r.take ? `${r.domain || '?'} / ${(r.got[0] || r.cands[0] || '?')}` : '不接管',
    candidates: r.cands.slice(0, 3),
    score: r.score,
    confidence: r.confidence,
    reason: r.reason,
    fail: failType(r),
  }))

// ── 门槛差多少 ─────────────────────────────────────────────────────────
const shortfalls = []
const check = (key, val, thr, dir) => {
  const pass = dir === 'max' ? val <= thr : val >= thr
  if (!pass) shortfalls.push({ metric: key, value: +val.toFixed(4), threshold: thr, delta: +(val - thr).toFixed(4) })
}
const errors = []
const out = {
  set: SET,
  generatedAt: new Date().toISOString(),
  note: golden.note || null,
  strict: STRICT,
  thresholds: THRESHONDS,
  metrics: Object.fromEntries(Object.entries(metrics).map(([k, v]) => [k, typeof v === 'number' ? +v.toFixed(4) : v])),
  confusion: {
    positives: { taken: tp, notTaken: fn },
    negatives: { taken: fp, notTaken: tn },
  },
  perCategory,
  failures,
  shortfalls,
}

if (STRICT) {
  check('accuracy', metrics.accuracy, THRESHONDS.accuracy, 'min')
  check('falseTakeover', metrics.falseTakeover, THRESHONDS.falseTakeover, 'max')
  check('recall', metrics.recall, THRESHONDS.recall, 'min')
  check('top1', metrics.top1, THRESHONDS.top1, 'min')
  check('top3', metrics.top3, THRESHONDS.top3, 'min')
  if (shortfalls.length) {
    errors.push(`--strict 未达标 ${shortfalls.length} 项：` + shortfalls.map((s) => `${s.metric}=${s.value}（门槛${s.threshold >= 0 && s.threshold < 1 ? s.threshold : s.threshold}，差 ${(s.delta > 0 ? '+' : '') + s.delta}）`).join('；'))
  }
}
out.shortfalls = shortfalls
out.errors = errors

// ── 输出 ───────────────────────────────────────────────────────────────
if (WANT_JSON) {
  console.log(JSON.stringify(out, null, 2))
} else {
  const pct = (x) => (x === null || x === undefined ? '—' : (x * 100).toFixed(1) + '%')
  console.log(`识别层评估：${SET}.json（${cases.length} 条：科研诉求 ${pos.length} / 非科研诉求 ${neg.length}）`)
  if (golden.note) console.log(`  ${golden.note}`)
  if (STRICT_IGNORED) console.log('  注意：--set dev 是调参集，--strict 已按设计忽略（只在 test 上判定门槛）')

  console.log('\n混淆矩阵（接管判定）')
  console.log('                     实际接管   实际不接管   合计')
  console.log(`  期望接管(科研诉求)   ${String(tp).padStart(6)}     ${String(fn).padStart(8)}   ${String(pos.length).padStart(5)}`)
  console.log(`  期望不接管(非科研)   ${String(fp).padStart(6)}     ${String(tn).padStart(8)}   ${String(neg.length).padStart(5)}`)

  console.log('\n总指标')
  const line = (name, val, thr) => console.log(`  ${name}${thr ? '（门槛 ' + thr + '）' : ''}：${val}`)
  line('接管判定准确率', pct(metrics.accuracy), THRESHONDS.accuracy)
  line('误接管率', pct(metrics.falseTakeover), '≤' + THRESHONDS.falseTakeover)
  line('科研诉求召回', pct(metrics.recall), THRESHONDS.recall)
  line('卡 top1', pct(metrics.top1), THRESHONDS.top1)
  line('卡 top3', pct(metrics.top3), THRESHONDS.top3)
  console.log(`  （辅助）域正确率：${pct(metrics.domain)}；接管成功时的 top1：${pct(metrics.top1WhenTaken)}、top3：${pct(metrics.top3WhenTaken)}`)

  console.log('\n分类别')
  const head = ['类别', 'n', '科研', '非科研', '召回', '误接管', 'top1', 'top3', '判定准']
  console.log('  ' + [head[0].padEnd(8), ...head.slice(1).map((h) => h.padStart(7))].join(''))
  for (const c of perCategory) {
    console.log('  ' + [
      c.category.padEnd(8),
      String(c.n).padStart(7),
      String(c.positives).padStart(7),
      String(c.negatives).padStart(7),
      pct(c.recall).padStart(7),
      pct(c.falseTakeover).padStart(7),
      pct(c.top1).padStart(7),
      pct(c.top3).padStart(7),
      pct(c.decisionAccuracy).padStart(7),
    ].join(''))
  }

  if (failures.length) {
    console.log(`\n失败条目（${failures.length} 条，按失败类型）`)
    for (const f of failures) {
      console.log(`  [${f.fail}] ${f.id}「${f.utterance}」`)
      console.log(`        期望 ${f.expect} ｜ 实际 ${f.actual} ｜ 候选 ${f.candidates.join(' > ') || '—'} ｜ score=${f.score} conf=${f.confidence || '—'}`)
    }
  } else {
    console.log('\n失败条目：0 条')
  }

  if (VERBOSE) {
    console.log('\n逐条明细')
    for (const r of rows) {
      console.log(`  ${r.id} ${r.decisionOk ? 'OK ' : 'BAD'} take=${r.take} dom=${r.domain || '—'} want=${r.expectNo ? 'noTakeover' : r.want.join('|')} cands=${r.cands.join('>') || '—'} score=${r.score}`)
    }
  }

  if (STRICT) {
    if (shortfalls.length) {
      console.log('\n--strict 未达标（不调门槛、不挑数据，如实失败）：')
      for (const s of shortfalls) console.log(`  ${s.metric}：${s.value} vs 门槛 ${s.threshold}（实际差 ${s.delta > 0 ? '+' : ''}${s.delta}）`)
    } else {
      console.log('\n--strict：五项门槛全部达标')
    }
  }
}

process.exit(STRICT && shortfalls.length ? 1 : 0)
