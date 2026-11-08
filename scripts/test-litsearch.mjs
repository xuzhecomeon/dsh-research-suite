#!/usr/bin/env node
/**
 * scripts/test-litsearch.mjs —— lib/litsearch.js 的离线测试
 *
 * 原则：**测试不联网**。所有网络调用都走注入的假 fetch，返回固定的 PubMed / Crossref JSON，
 * 这样「超时」「429」「404」「网络断开」这些最容易被写错的分支才能稳定复现。
 * 联网的真实 smoke（若本机有网）在测试末尾单独跑，失败不判 FAIL，只在报告里如实记录。
 *
 * 跑法：node scripts/test-litsearch.mjs
 */

import { createLitSearch } from '../lib/litsearch.js';

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

// ---------------------------------------------------------------------------
// 假 fetch 的零件
// ---------------------------------------------------------------------------

function jsonResponse(body, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    async json() {
      return body;
    },
  };
}

function routeFetch(routes) {
  const calls = [];
  const impl = async (url, opts = {}) => {
    calls.push({ url: String(url), at: Date.now() });
    const hit = routes.find((r) => (typeof r.match === 'string' ? String(url).includes(r.match) : r.match.test(String(url))));
    if (!hit) return jsonResponse({}, 599); // 未编排的 URL 直接报错，避免测试悄悄依赖真实网络
    return typeof hit.reply === 'function' ? hit.reply(String(url), opts) : hit.reply;
  };
  impl.calls = calls;
  return impl;
}

const DOI = '10.1038/s41572-021-00264-3';

function crossrefBody(patch = {}) {
  return {
    status: 'ok',
    message: {
      DOI,
      type: 'journal-article',
      title: ['Trauma-induced coagulopathy'],
      'container-title': ['Nature Reviews Disease Primers'],
      issued: { 'date-parts': [[2021, 5, 1]] },
      volume: '7',
      issue: '1',
      page: '30',
      author: [
        { given: 'Ernest E', family: 'Moore' },
        { given: 'Hunter B', family: 'Moore' },
        { given: 'Matthew D', family: 'Neal' },
      ],
      ...patch,
    },
  };
}

const EXPECTED = {
  title: 'Trauma-induced coagulopathy',
  authors: ['Moore', 'Moore', 'Neal'],
  journal: 'Nature Reviews Disease Primers',
  year: 2021,
  volume: 7,
  issue: 1,
  pages: '30',
};

function fieldRow(result, field) {
  return (result.fields ?? []).find((f) => f.field === field);
}

function pubmedEsearch({ count = '2', ids = ['111', '222'] } = {}) {
  return jsonResponse({ esearchresult: { count, retmax: String(ids.length), idlist: ids } });
}

function pubmedEsummary(uids = ['111', '222']) {
  const result = { uids };
  for (const uid of uids) {
    result[uid] = {
      uid,
      title: 'Heat stroke in rats: a systematic review',
      fulljournalname: 'Journal of Thermal Biology',
      pubdate: '2023 Mar',
      // 第 2 条演示「在线优先年 ≠ 刊期年」：pdat 日期限定按 epub 日期算，esummary 的 pubdate 是刊期年
      epubdate: uid === '222' ? '2022 Nov' : undefined,
      authors: [
        { name: 'Zhang San' },
        { name: 'Li Si' },
        { name: 'Wang Wu' },
        { name: 'Zhao Liu' },
      ],
      articleids: [{ idtype: 'doi', value: '10.1016/j.jtherbio.2023.103450' }],
      pubtype: ['Journal Article', 'Review'],
      elocationid: 'doi: 10.1016/j.jtherbio.2023.103450',
    };
  }
  return jsonResponse({ result });
}

// ---------------------------------------------------------------------------
// 用例
// ---------------------------------------------------------------------------

async function main() {
  const base = 'https://eutils.ncbi.nlm.nih.gov';
  const crossrefHost = 'https://api.crossref.org';

  // ---------------- searchPubmed ----------------
  console.log('\n[searchPubmed]');

  await checkAsync('搜索正常返回：count/items/字段齐全，且 query 是实际发出的 term', async () => {
    const fetchImpl = routeFetch([
      { match: 'esearch.fcgi', reply: pubmedEsearch() },
      { match: 'esummary.fcgi', reply: pubmedEsummary() },
    ]);
    const lit = createLitSearch({}, { fetchImpl, email: 't@example.org' });
    const res = await lit.searchPubmed({ query: 'heat stroke[tiab] AND rat', retmax: 5 });
    assert(res.ok === true, `应成功：${JSON.stringify(res)}`);
    eq(res.count, 2, 'count');
    eq(res.items.length, 2, 'items.length');
    eq(res.query, 'heat stroke[tiab] AND rat', 'query');
    eq(res.retmax, 5, 'retmax');
    const item = res.items[0];
    eq(item.pmid, '111', 'pmid');
    eq(item.journal, 'Journal of Thermal Biology', 'journal');
    eq(item.year, 2023, 'year');
    eq(item.doi, '10.1016/j.jtherbio.2023.103450', 'doi');
    eq(item.type, 'Journal Article', 'type');
    eq(item.authors.length, 3, '只保留前 3 位作者');
    eq(item.abstractUrl, 'https://pubmed.ncbi.nlm.nih.gov/111/', 'abstractUrl');
    assert(!item.abstract, '不应为了拼摘要再抓 efetch');
    eq(item.epubYear, null, '无 epub 日期时 epubYear 为 null');
    eq(res.items[1].year, 2023, '刊期年');
    eq(res.items[1].epubYear, 2022, '在线优先年单独回报（否则用户以为日期限定失效）');
  });

  await checkAsync('请求携带 tool / email，检索 URL 可照抄复跑', async () => {
    const fetchImpl = routeFetch([
      { match: 'esearch.fcgi', reply: pubmedEsearch({ count: '0', ids: [] }) },
    ]);
    const lit = createLitSearch({}, { fetchImpl, email: 't@example.org' });
    const res = await lit.searchPubmed({ query: 'foo' });
    const url = new URL(res.esearchUrl);
    eq(url.searchParams.get('tool'), 'dsh-research-suite', 'tool');
    eq(url.searchParams.get('email'), 't@example.org', 'email');
    eq(url.searchParams.get('db'), 'pubmed', 'db');
    eq(url.searchParams.get('retmode'), 'json', 'retmode');
  });

  await checkAsync('count=0 返回 ok:true + 空 items（真没命中，与失败区分开）', async () => {
    const fetchImpl = routeFetch([{ match: 'esearch.fcgi', reply: pubmedEsearch({ count: '0', ids: [] }) }]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.searchPubmed({ query: 'no such thing' });
    assert(res.ok === true, 'count=0 不算失败');
    eq(res.count, 0, 'count');
    eq(res.items.length, 0, 'items');
  });

  await checkAsync('搜索超时 → {ok:false, error:timeout}', async () => {
    // 真 fetch 会占住 socket 保持事件循环；假 fetch 必须自己挂一个 ref 着的定时器，
    // 否则 AbortSignal.timeout 的定时器是 unref 的，事件循环一空 Node 就直接以 0 退出。
    const hang = (url, opts = {}) =>
      new Promise((_, reject) => {
        const keep = setTimeout(() => {}, 60000);
        const onAbort = () => {
          clearTimeout(keep);
          reject(Object.assign(new Error('aborted'), { name: 'TimeoutError' }));
        };
        if (opts.signal?.aborted) onAbort();
        else opts.signal?.addEventListener?.('abort', onAbort);
      });
    const lit = createLitSearch({}, { fetchImpl: hang, timeoutMs: 30 });
    const res = await lit.searchPubmed({ query: 'slow' });
    eq(res.ok, false, 'ok');
    eq(res.error, 'timeout', 'error');
  });

  await checkAsync('搜索 429 → {ok:false, error:http_429}', async () => {
    const fetchImpl = routeFetch([{ match: 'esearch.fcgi', reply: jsonResponse({}, 429) }]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.searchPubmed({ query: 'rate limited' });
    eq(res.ok, false, 'ok');
    eq(res.error, 'http_429', 'error');
    eq(res.status, 429, 'status');
  });

  await checkAsync('空检索词 → invalid_query（不发请求）', async () => {
    let called = 0;
    const fetchImpl = async () => {
      called += 1;
      return jsonResponse({});
    };
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.searchPubmed({ query: '   ' });
    eq(res.ok, false, 'ok');
    eq(res.error, 'invalid_query', 'error');
    eq(called, 0, '不应发出请求');
  });

  await checkAsync('有 id 但 esummary 解析不出条目 → summary_parse（不许回 0 条）', async () => {
    const fetchImpl = routeFetch([
      { match: 'esearch.fcgi', reply: pubmedEsearch({ count: '2', ids: ['111', '222'] }) },
      { match: 'esummary.fcgi', reply: jsonResponse({ result: { uids: ['111', '222'] } }) },
    ]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.searchPubmed({ query: 'parse fail' });
    eq(res.ok, false, 'ok');
    eq(res.error, 'summary_parse', 'error');
    eq(res.count, 2, 'count 仍要如实回报');
  });

  await checkAsync('types 一律落成 [pt] 项（filter 参数被 NCBI 拒，不能用）', async () => {
    const fetchImpl = routeFetch([
      { match: 'esearch.fcgi', reply: pubmedEsearch({ count: '0', ids: [] }) },
    ]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.searchPubmed({ query: 'x', types: ['review', 'clinical trial[pt]'] });
    const url = new URL(res.esearchUrl);
    const term = decodeURIComponent(url.searchParams.get('term'));
    assert(term.includes('review[pt]'), `term 应含 review[pt]：${term}`);
    assert(term.includes('clinical trial[pt]'), `term 应含 clinical trial[pt]：${term}`);
    assert(term.includes(' OR '), `多个出版类型应 OR：${term}`);
    eq(url.searchParams.get('filter'), null, '不得走 filter 参数');
    eq(res.types.join('|'), 'review|clinical trial', '结果里回报归一后的出版类型');
  });

  await checkAsync('日期限定走 datetype=pdat，并归一成 YYYY/MM/DD', async () => {
    const fetchImpl = routeFetch([{ match: 'esearch.fcgi', reply: pubmedEsearch({ count: '0', ids: [] }) }]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.searchPubmed({ query: 'x', mindate: '2020-05', maxdate: '2024' });
    const url = new URL(res.esearchUrl);
    eq(url.searchParams.get('datetype'), 'pdat', 'datetype');
    eq(url.searchParams.get('mindate'), '2020/05', 'mindate');
    eq(url.searchParams.get('maxdate'), '2024', 'maxdate');
  });

  await checkAsync('限速队列：相邻两次请求间隔 ≥ 300ms（不并发打 NCBI）', async () => {
    const fetchImpl = routeFetch([{ match: 'esearch.fcgi', reply: pubmedEsearch({ count: '0', ids: [] }) }]);
    const lit = createLitSearch({}, { fetchImpl });
    await lit.searchPubmed({ query: 'a' });
    await lit.searchPubmed({ query: 'b' });
    await lit.searchPubmed({ query: 'c' });
    const times = fetchImpl.calls.map((c) => c.at);
    eq(times.length, 3, '调用次数');
    const gaps = [times[1] - times[0], times[2] - times[1]];
    assert(gaps.every((g) => g >= 300), `间隔应 ≥300ms，实际 ${gaps.join(' / ')}`);
  });

  // ---------------- compareDoi ----------------
  console.log('\n[compareDoi]');

  await checkAsync('字段完全一致 → verified，四类字段全 exact', async () => {
    const fetchImpl = routeFetch([{ match: crossrefHost, reply: jsonResponse(crossrefBody()) }]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.compareDoi({ doi: DOI, expected: EXPECTED });
    assert(res.ok === true, `应成功：${JSON.stringify(res)}`);
    eq(res.status, 'verified', 'status');
    eq(res.fields.length, 7, `字段数：${res.fields.map((f) => f.field).join(',')}`);
    for (const f of res.fields) eq(f.match, 'exact', `${f.field} 应 exact（实际 ${f.match}）`);
    eq(res.crossref.year, 2021, 'crossref.year');
    eq(res.crossref.authors.length, 3, 'crossref.authors');
  });

  await checkAsync('首作者抄错 → mismatch（不给模糊空间）', async () => {
    const fetchImpl = routeFetch([{ match: crossrefHost, reply: jsonResponse(crossrefBody()) }]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.compareDoi({ doi: DOI, expected: { ...EXPECTED, authors: ['Smith', 'Moore'] } });
    eq(res.status, 'mismatch', 'status');
    eq(fieldRow(res, 'authors').match, 'mismatch', 'authors.match');
  });

  await checkAsync('卷期页错 → mismatch 且精确指到 volume/pages', async () => {
    const fetchImpl = routeFetch([{ match: crossrefHost, reply: jsonResponse(crossrefBody()) }]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.compareDoi({ doi: DOI, expected: { ...EXPECTED, volume: 8, pages: '31-40' } });
    eq(res.status, 'mismatch', 'status');
    eq(fieldRow(res, 'volume').match, 'mismatch', 'volume');
    eq(fieldRow(res, 'pages').match, 'mismatch', 'pages');
    eq(fieldRow(res, 'issue').match, 'exact', 'issue 不受牵连');
  });

  await checkAsync('题名近似（多一个词）→ fuzzy，不误判成 mismatch', async () => {
    const fetchImpl = routeFetch([{ match: crossrefHost, reply: jsonResponse(crossrefBody()) }]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.compareDoi({ doi: DOI, expected: { ...EXPECTED, title: 'Trauma-induced coagulopathy revisited' } });
    eq(fieldRow(res, 'title').match, 'fuzzy', 'title.match');
    eq(res.status, 'verified', '只有 fuzzy 时不算 mismatch');
  });

  await checkAsync('年份差 1（在线优先出版）→ fuzzy，仍 verified', async () => {
    const fetchImpl = routeFetch([{ match: crossrefHost, reply: jsonResponse(crossrefBody()) }]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.compareDoi({ doi: DOI, expected: { ...EXPECTED, year: 2022 } });
    eq(fieldRow(res, 'year').match, 'fuzzy', 'year.match');
    eq(res.status, 'verified', 'status');
  });

  await checkAsync('字段缺失记 missing（不算 mismatch）', async () => {
    const fetchImpl = routeFetch([
      { match: crossrefHost, reply: jsonResponse(crossrefBody({ volume: undefined, issue: undefined, page: undefined })) },
    ]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.compareDoi({ doi: DOI, expected: EXPECTED });
    eq(fieldRow(res, 'volume').match, 'missing', 'volume');
    eq(fieldRow(res, 'pages').match, 'missing', 'pages');
    eq(res.status, 'verified', 'missing 不升级成 mismatch');
  });

  await checkAsync('电子刊只有 article-number 时按页码比对（不误判页码缺失）', async () => {
    const fetchImpl = routeFetch([
      { match: crossrefHost, reply: jsonResponse(crossrefBody({ page: undefined, 'article-number': '30' })) },
    ]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.compareDoi({ doi: DOI, expected: EXPECTED });
    eq(fieldRow(res, 'pages').match, 'exact', 'pages');
    eq(res.crossref.pageKind, 'article-number', 'pageKind');
    eq(res.crossref.pages, '30', 'crossref.pages');
  });

  await checkAsync('DOI 不存在（404）→ status:not_found', async () => {
    const fetchImpl = routeFetch([{ match: crossrefHost, reply: jsonResponse({}, 404) }]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.compareDoi({ doi: '10.9999/does-not-exist', expected: { title: 'Ghost paper' } });
    eq(res.ok, true, 'ok');
    eq(res.status, 'not_found', 'status');
    eq(res.crossref, null, 'crossref');
  });

  await checkAsync('网络错 → {ok:false, status:unverifiable, error:network}', async () => {
    const boom = async () => {
      throw new Error('ECONNREFUSED');
    };
    const lit = createLitSearch({}, { fetchImpl: boom });
    const res = await lit.compareDoi({ doi: DOI, expected: EXPECTED });
    eq(res.ok, false, 'ok');
    eq(res.status, 'unverifiable', 'status');
    eq(res.error, 'network', 'error');
  });

  await checkAsync('中文条目查不到 → unverifiable + 中文期刊提示（不报 not_found）', async () => {
    const fetchImpl = routeFetch([{ match: crossrefHost, reply: jsonResponse({}, 404) }]);
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.compareDoi({ doi: '10.3969/j.issn.1000-0000.2021.01.001', expected: { title: '创伤性凝血病的诊治进展' } });
    eq(res.status, 'unverifiable', 'status');
    assert(String(res.hint ?? '').includes('中文期刊'), `hint 应说明中文期刊：${JSON.stringify(res.hint)}`);
  });

  await checkAsync('DOI 格式非法 → invalid_doi（不发请求）', async () => {
    let called = 0;
    const fetchImpl = async () => {
      called += 1;
      return jsonResponse({});
    };
    const lit = createLitSearch({}, { fetchImpl });
    const res = await lit.compareDoi({ doi: 'not-a-doi' });
    eq(res.error, 'invalid_doi', 'error');
    eq(called, 0, '不应发出请求');
  });

  await checkAsync('Crossref 请求带 mailto（礼貌池）', async () => {
    const fetchImpl = routeFetch([{ match: crossrefHost, reply: jsonResponse(crossrefBody()) }]);
    const lit = createLitSearch({}, { fetchImpl, email: 't@example.org' });
    await lit.compareDoi({ doi: DOI, expected: EXPECTED });
    const url = new URL(fetchImpl.calls[0].url);
    eq(url.searchParams.get('mailto'), 't@example.org', 'mailto');
  });

  // ---------------- 联网 smoke（可选） ----------------
  console.log('\n[smoke]');
  let smoke = 'skipped（未联网或联网失败）';
  if (typeof globalThis.fetch === 'function' && process.env.LITSEARCH_SMOKE !== '0') {
    const live = createLitSearch({}, { timeoutMs: 8000 });
    try {
      const search = await live.searchPubmed({ query: 'heat stroke[tiab] AND rat', retmax: 5 });
      if (search.ok && search.items.length) {
        smoke = `OK：${search.count} 命中，首条 PMID ${search.items[0].pmid}《${search.items[0].title}》`;
      } else {
        smoke = `联网检索未成功（${JSON.stringify({ ok: search.ok, error: search.error })}），本次以上全部为离线测试`;
      }
    } catch (err) {
      smoke = `联网检索抛错（${String(err?.message ?? err)}），本次以上全部为离线测试`;
    }
    console.log(`  • ${smoke}`);
    try {
      const check = await live.compareDoi({
        doi: '10.1038/s41572-021-00264-3',
        expected: { title: 'Trauma-induced coagulopathy', year: 2021, volume: 7, pages: '30' },
      });
      console.log(`  • compareDoi ${check.ok ? check.status : check.error}`);
    } catch (err) {
      console.log(`  • compareDoi 抛错 ${String(err?.message ?? err)}`);
    }
  } else {
    console.log('  • 跳过联网 smoke（LITSEARCH_SMOKE=0 或无 fetch）');
  }

  // ---------------- 汇总 ----------------
  console.log(`\nlitsearch: ${passed} passed, ${failed} failed`);
  if (failed > 0) {
    console.log('失败用例：');
    for (const f of failures) console.log(`  - ${f.name}: ${f.message}`);
  }
  console.log(`smoke: ${smoke}`);
  process.exit(failed === 0 ? 0 : 1);
}

main().catch((err) => {
  console.error('测试脚本自身崩溃：', err);
  process.exit(1);
});
