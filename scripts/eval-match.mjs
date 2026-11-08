#!/usr/bin/env node
/**
 * 识别层评估：拿 data/golden/cases.json 里的真人原话跑一遍匹配，报四个指标。
 * 这是 v3.1 对「没有 golden set、没有对照评估」这条批评的正面回答：
 * 识别规则（data/match-rules.json）改完必须跑它，数字不许变差。
 *
 * 用法：
 *   node scripts/eval-match.mjs            # 只报数字，exit 0
 *   node scripts/eval-match.mjs --strict   # 低于阈值 exit 1（CI 用）
 *   node scripts/eval-match.mjs -v         # 逐条打印
 */
import { readFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createCore } from '../lib/core.js'

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const verbose = process.argv.includes('-v') || process.argv.includes('--verbose')
const strict = process.argv.includes('--strict')

const core = createCore(root)
const golden = JSON.parse(readFileSync(path.join(root, 'data', 'golden', 'cases.json'), 'utf8'))

const rows = []
for (const c of golden.cases) {
  const r = core.matchCapabilities(c.utterance, { limit: 3 })
  const expectNo = Boolean(c.expect?.noTakeover)
  const decisionOk = expectNo ? r.takeover === false : r.takeover === true
  let domainOk = null
  let cap1 = null
  let cap3 = null
  if (!expectNo) {
    const accepted = new Set([c.expect?.cap, ...(c.expect?.alts ?? [])].filter(Boolean))
    domainOk = r.domain === c.expect?.domain
    const top1 = r.matches[0]?.cap?.id ?? null
    cap1 = top1 ? accepted.has(top1) : false
    cap3 = r.matches.some((m) => accepted.has(m.cap.id))
  }
  rows.push({ id: c.id, utterance: c.utterance, expectNo, decisionOk, domainOk, cap1, cap3, r, expect: c.expect })
}

const taken = rows.filter((x) => !x.expectNo)
const refused = rows.filter((x) => x.expectNo)
const sum = (arr, f) => arr.filter(f).length
const pct = (n, d) => (d ? `${((n / d) * 100).toFixed(1)}%` : '—')

const decisionOk = sum(rows, (x) => x.decisionOk)
const domainOk = sum(taken, (x) => x.domainOk)
const cap1Ok = sum(taken, (x) => x.cap1)
const cap3Ok = sum(taken, (x) => x.cap3)
const falseTakeover = sum(refused, (x) => x.r.takeover)
const missed = sum(taken, (x) => !x.r.takeover)

console.log('')
console.log('== 识别层评估（data/golden/cases.json）==')
console.log(`用例总数            ${rows.length}（科研 ${taken.length} / 非科研 ${refused.length}）`)
console.log(`接管判定正确        ${decisionOk}/${rows.length}  ${pct(decisionOk, rows.length)}`)
console.log(`  误接管（该拒却接） ${falseTakeover}/${refused.length}`)
console.log(`  漏接管（该接却拒） ${missed}/${taken.length}`)
console.log(`域 top1 正确        ${domainOk}/${taken.length}  ${pct(domainOk, taken.length)}`)
console.log(`能力卡 top1 正确    ${cap1Ok}/${taken.length}  ${pct(cap1Ok, taken.length)}`)
console.log(`能力卡 top3 命中    ${cap3Ok}/${taken.length}  ${pct(cap3Ok, taken.length)}`)

if (verbose) {
  console.log('')
  for (const x of rows) {
    const mark = x.decisionOk && (x.expectNo || x.domainOk) ? 'ok  ' : 'FAIL'
    const got = x.r.takeover
      ? `${x.r.matches[0]?.cap?.id ?? '?'}(${x.r.score}/${x.r.confidence})`
      : `未接管(${x.r.reason})`
    console.log(`${mark} ${x.id} ${x.utterance}  →  ${got}`)
  }
}

const bad = rows.filter((x) => !x.decisionOk || (!x.expectNo && (!x.domainOk || !x.cap1)))
if (bad.length) {
  console.log('')
  console.log('-- 需要关注的用例 --')
  for (const x of bad) {
    const want = x.expectNo ? '不接管' : `${x.expect.domain}/${x.expect.cap}`
    const got = x.r.takeover ? x.r.matches.map((m) => m.cap.id).join(' > ') : `未接管：${x.r.reason}`
    console.log(`  ${x.id} 期望 ${want}｜实际 ${got}｜${x.utterance}`)
  }
}

const gates = { decision: 0.9, domain: 0.8, cap1: 0.65, cap3: 0.85 }
const failGates = []
if (decisionOk / rows.length < gates.decision) failGates.push(`接管判定 ${pct(decisionOk, rows.length)} < ${gates.decision * 100}%`)
if (domainOk / taken.length < gates.domain) failGates.push(`域 top1 ${pct(domainOk, taken.length)} < ${gates.domain * 100}%`)
if (cap1Ok / taken.length < gates.cap1) failGates.push(`卡 top1 ${pct(cap1Ok, taken.length)} < ${gates.cap1 * 100}%`)
if (cap3Ok / taken.length < gates.cap3) failGates.push(`卡 top3 ${pct(cap3Ok, taken.length)} < ${gates.cap3 * 100}%`)

if (failGates.length) {
  console.log('')
  console.log(`未达门槛：${failGates.join('；')}`)
  if (strict) process.exit(1)
} else {
  console.log('')
  console.log('四项指标均达门槛（strict 模式下 exit 0）')
}
