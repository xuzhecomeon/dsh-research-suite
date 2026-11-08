/**
 * dsh-research-suite v3.2 · litsearch：把「文献检索」从「只给检索式」做到「真能检索 + 字段级核验」
 *
 * 设计立场（与本套件的三条红线一致）：
 *   1) 检索必须可复现：返回的 `query` 是**实际发给 PubMed 的 term**，连同 esearch / esummary 的
 *      完整 URL 一起回给调用方，任何人可以照着复跑一遍拿到同一批 PMID。
 *   2) 绝不伪造结果：网络失败一律 `{ok:false, error}`；**绝不**用空数组冒充「没检索到文献」，
 *      也绝不在 esummary 解析失败时把 count>0 的检索说成 0 条。拿不到就如实说拿不到。
 *   3) 灰区即 FAIL：DOI 核验里题名、作者、卷期页对不上就是 mismatch，不因为「大方向没错」放过。
 *
 * 依赖：零第三方依赖，只用全局 fetch（Node 20+ 自带）；所有网络调用默认 5 秒超时。
 *
 * 两个方法：
 *   - searchPubmed({query, retmax, mindate, maxdate, types, sort}) → PubMed 检索（esearch + esummary）
 *   - compareDoi({doi, expected}) → Crossref 取权威元数据，与稿件里写的字段逐条比对
 */

const DEFAULT_EMAIL = 'dsh-research-suite@users.noreply.github.com';
const TOOL = 'dsh-research-suite';
const EUTILS = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils';
const CROSSREF = 'https://api.crossref.org/works';

const DEFAULT_TIMEOUT_MS = 5000; // 5 秒：NCBI 与 Crossref 都在此量级返回；超时按网络失败处理，不当数据错误
const RATE_PUBLIC_MS = 350; // 无 API key：NCBI 限 3 次/秒
const RATE_KEYED_MS = 100; // 有 API key：NCBI 限 10 次/秒
const MAX_RETMAX = 200; // esummary 单次按 id 列表取，超过 200 条要分批；这里直接封顶
const MAX_AUTHORS = 3; // 题录里只回前 3 位作者（GB/T 7714 与 Vancouver 都够用）

// ---------------------------------------------------------------------------
// 基础工具：错误返回、超时信号、睡眠、串行限速
// ---------------------------------------------------------------------------

function failure(error, extra = {}) {
  return { ok: false, error, ...extra };
}

function isObject(v) {
  return v !== null && typeof v === 'object' && !Array.isArray(v);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** 超时信号：优先用 AbortSignal.timeout（Node 17.3+），老运行时退回 AbortController。 */
function makeTimeoutSignal(ms) {
  const timeout = Number.isFinite(ms) && ms > 0 ? ms : DEFAULT_TIMEOUT_MS;
  if (typeof AbortSignal !== 'undefined' && typeof AbortSignal.timeout === 'function') {
    return { signal: AbortSignal.timeout(timeout), done: () => {} };
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  return { signal: controller.signal, done: () => clearTimeout(timer) };
}

/**
 * 命中/失败的最小判别：只要请求没成功，就返回 {ok:false, error}，绝不退化成「空结果」。
 * error 取值固定为 'network' | 'timeout' | `http_<code>`，调用方不用猜。
 */
async function requestJson(url, { fetchImpl, timeoutMs, headers } = {}) {
  if (typeof fetchImpl !== 'function') return failure('network');
  const { signal, done } = makeTimeoutSignal(timeoutMs);
  try {
    const res = await fetchImpl(url, { signal, headers });
    if (!res || typeof res !== 'object') return failure('network');
    if (!res.ok) return { ok: false, error: `http_${res.status}`, status: res.status };
    const json = await res.json();
    return { ok: true, status: res.status, json };
  } catch (err) {
    // 超时（AbortSignal.timeout 抛 TimeoutError，AbortController 抛 AbortError）与网络错分开报，
    // 因为「等太久」和「没网」对用户的意义不同。
    if (signal?.aborted || err?.name === 'TimeoutError' || err?.name === 'AbortError') return failure('timeout');
    return failure('network');
  } finally {
    done();
  }
}

/**
 * 串行限速队列：NCBI 的调用配额是「每秒几次」，并发打过去会整批 429。
 * 这里保证相邻两次请求的**发起时刻**至少间隔 minIntervalMs。
 */
function createRateLimiter(minIntervalMs) {
  let tail = Promise.resolve();
  let lastAt = 0;
  return function schedule(task) {
    const run = async () => {
      if (lastAt > 0) {
        const wait = lastAt + minIntervalMs - Date.now();
        if (wait > 0) await sleep(wait);
      }
      lastAt = Date.now();
      return task();
    };
    const p = tail.then(run, run);
    tail = p.then(
      () => {},
      () => {},
    );
    return p;
  };
}

// ---------------------------------------------------------------------------
// 文本归一化：题名、作者、卷期页各有各的「看起来不一样但其实是同一件事」
// ---------------------------------------------------------------------------

function hasCjk(value) {
  return typeof value === 'string' && /[\u3400-\u9fff]/.test(value);
}

function stripHtml(value) {
  return String(value ?? '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/&[a-zA-Z]+;|&#\d+;/g, ' ');
}

function collapse(value) {
  return String(value ?? '').replace(/\s+/g, ' ').trim();
}

/** 去变音符号（Müller → Muller），否则作者姓比对会被重音符号判成两个人。 */
function foldAccents(value) {
  return String(value ?? '')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '');
}

/** 题名归一化：去 HTML、去副标题（冒号之后）、小写、去变音、只留字母数字。 */
function normalizeTitle(value) {
  let t = stripHtml(value);
  t = t.split(/[:：]/)[0]; // 副标题常被作者漏写或改写，只比主标题
  t = foldAccents(t).toLowerCase();
  t = t.replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  return t;
}

/**
 * 题名切词：拉丁文按词，中日韩按**单字**。
 * 中文题名没有空格，按词切会得到一整个 token，Jaccard 只能算出 0/1，起不到「近似」的作用。
 */
function titleTokens(value) {
  const norm = normalizeTitle(value);
  if (!norm) return new Set();
  if (hasCjk(norm)) return new Set(Array.from(norm.replace(/\s+/g, '')));
  return new Set(norm.split(' ').filter(Boolean));
}

function jaccard(a, b) {
  if (!a.size && !b.size) return 1;
  if (!a.size || !b.size) return 0;
  let inter = 0;
  for (const x of a) if (b.has(x)) inter += 1;
  return inter / (a.size + b.size - inter);
}

/** 作者名归一化：去变音、小写、去掉空格与连字符（van der Berg ≈ Vanderberg 不保险，但比不归一一律 mismatch 好）。 */
function normalizeName(value) {
  return foldAccents(value)
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '');
}

/** 卷/期/页码归一化：去空格、各种破折号统一成 '-'、去掉首尾标点。 */
function normalizeNumberish(value) {
  return String(value ?? '')
    .trim()
    .replace(/\s+/g, '')
    .replace(/[–—−～~]/g, '-')
    .replace(/^[-,;:]+|[-,;:.]+$/g, '')
    .toLowerCase();
}

function firstString(value) {
  return Array.isArray(value) && value.length ? String(value[0] ?? '') : value ? String(value) : '';
}

function normalizeDoi(input) {
  return String(input ?? '')
    .trim()
    .replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, '')
    .replace(/^doi:\s*/i, '')
    .replace(/[.,;)\]]+$/, '')
    .trim()
    .toLowerCase();
}

const DOI_RE = /^10\.\d{4,9}\/\S+$/;

// ---------------------------------------------------------------------------
// PubMed 字段解析
// ---------------------------------------------------------------------------

function yearOf(value) {
  const m = String(value ?? '').match(/\b(1[89]\d{2}|20\d{2})\b/);
  return m ? Number(m[1]) : null;
}

function doiOfRecord(rec) {
  const ids = Array.isArray(rec?.articleids) ? rec.articleids : [];
  for (const item of ids) {
    if (String(item?.idtype ?? '').toLowerCase() === 'doi' && item?.value) return normalizeDoi(item.value);
  }
  const loc = String(rec?.elocationid ?? '');
  const m = loc.match(/^doi:\s*(.+)$/i);
  return m ? normalizeDoi(m[1]) : null;
}

function pubTypeOf(rec) {
  const list = Array.isArray(rec?.pubtype) ? rec.pubtype : rec?.pubtype ? [rec.pubtype] : [];
  const clean = list.map((x) => collapse(x)).filter(Boolean);
  return clean.length ? clean[0] : null;
}

function itemsFromSummary(summary, uids) {
  const result = isObject(summary?.result) ? summary.result : {};
  const items = [];
  for (const uid of uids) {
    const rec = result[String(uid)];
    if (!isObject(rec)) continue;
    const authors = (Array.isArray(rec.authors) ? rec.authors : [])
      .map((a) => collapse(a?.name))
      .filter(Boolean)
      .slice(0, MAX_AUTHORS);
    // year 取「刊期年」（题录引用的出版年），epubYear 另记「在线优先年」。
    // PubMed 的 [pdat] 日期限定对优先出版记录用的是 epub 日期，而 esummary 的 pubdate 是最终刊期年，
    // 两者会差一年（实测 mindate/maxdate=2024..2025 能返回 pubdate=2026 的记录）。不把这件事摊开，
    // 用户会以为日期限定失效了。
    const year = yearOf(rec.pubdate) ?? yearOf(rec.epubdate);
    const epubYear = yearOf(rec.epubdate);
    items.push({
      pmid: String(rec.uid ?? uid),
      title: stripHtml(collapse(rec.title)).replace(/\s+/g, ' ').replace(/\.$/, ''),
      journal: collapse(rec.fulljournalname) || collapse(rec.source) || '',
      year,
      epubYear: epubYear && epubYear !== year ? epubYear : null,
      authors,
      doi: doiOfRecord(rec),
      type: pubTypeOf(rec),
      abstractUrl: `https://pubmed.ncbi.nlm.nih.gov/${uid}/`,
    });
  }
  return items;
}

// ---------------------------------------------------------------------------
// 工厂
// ---------------------------------------------------------------------------

/**
 * @param {object} core 插件 core（可只用其 stats.version 组装 User-Agent；允许为空对象）
 * @param {object} options
 *   - email：NCBI / Crossref 礼貌池联系邮箱（缺省用仓库占位邮箱）
 *   - apiKey：NCBI API key（有则限速 10 次/秒）
 *   - timeoutMs：单次网络超时，默认 5000
 *   - fetchImpl：注入 fetch 实现（测试用；默认 globalThis.fetch）
 *   - rateLimitMs：覆盖默认限速间隔（测试或已知配额的场景用）
 */
export function createLitSearch(core, options = {}) {
  const version = collapse(core?.stats?.version) || collapse(options.version) || '3.2.0';
  const email = collapse(options.email) || DEFAULT_EMAIL;
  const apiKey = collapse(options.apiKey);
  const timeoutMs = Number.isFinite(options.timeoutMs) && options.timeoutMs > 0 ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
  const fetchImpl = typeof options.fetchImpl === 'function' ? options.fetchImpl : globalThis.fetch;
  const rateLimitMs =
    Number.isFinite(options.rateLimitMs) && options.rateLimitMs >= 0
      ? options.rateLimitMs
      : apiKey
        ? RATE_KEYED_MS
        : RATE_PUBLIC_MS;
  const schedule = createRateLimiter(rateLimitMs);

  const headers = {
    'User-Agent': `${TOOL}/${version} (mailto:${email})`,
    Accept: 'application/json',
  };

  /**
   * PubMed 检索。字段标签原样透传（`[tiab]` / `[mh]` / `[pt]` / `[dp]` …），
   * 不做任何「自动扩词」——扩词是检索策略该由人决定，工具只负责如实执行与记录。
   *
   * types 一律落成 `[pt]` 项并 `AND` 进 term（如 `review` → `review[pt]`）。
   * 不走 esearch 的 `filter` 参数：2026-11 实测 `filter=review` 会被 NCBI 拒为
   * `Invalid filter key: review`（filter 名单用的是另一套内部 key），而 `review[pt]` 稳定可用。
   */
  async function searchPubmed(args = {}) {
    const rawQuery = String(args.query ?? '');
    const term = rawQuery.replace(/\s+/g, ' ').trim();
    if (!term) return failure('invalid_query', { query: '' });

    const retmax = clampInt(args.retmax, 20, 1, MAX_RETMAX);
    const sort = mapSort(args.sort);
    const dates = {};
    const mindate = cleanDate(args.mindate);
    const maxdate = cleanDate(args.maxdate);
    if (mindate) dates.mindate = mindate;
    if (maxdate) dates.maxdate = maxdate;

    const pubtypes = normalizeTypes(args.types);
    const finalTerm = pubtypes.length ? `(${term}) AND (${pubtypes.map((t) => `${t}[pt]`).join(' OR ')})` : term;

    const esearch = new URL(`${EUTILS}/esearch.fcgi`);
    esearch.searchParams.set('db', 'pubmed');
    esearch.searchParams.set('term', finalTerm);
    esearch.searchParams.set('retmax', String(retmax));
    esearch.searchParams.set('retmode', 'json');
    esearch.searchParams.set('sort', sort);
    esearch.searchParams.set('tool', TOOL);
    esearch.searchParams.set('email', email);
    if (apiKey) esearch.searchParams.set('api_key', apiKey);
    if (mindate || maxdate) {
      esearch.searchParams.set('datetype', 'pdat'); // 按出版日期限定；reldate 语义不同，不混用
      if (mindate) esearch.searchParams.set('mindate', mindate);
      if (maxdate) esearch.searchParams.set('maxdate', maxdate);
    }

    const searchRes = await schedule(() =>
      requestJson(esearch.toString(), { fetchImpl, timeoutMs, headers }),
    );
    if (!searchRes.ok) {
      return failure(searchRes.error, { query: finalTerm, esearchUrl: esearch.toString(), status: searchRes.status ?? null });
    }
    const esearchResult = searchRes.json?.esearchresult;
    if (!isObject(esearchResult)) {
      return failure('pubmed_bad_response', { query: finalTerm, esearchUrl: esearch.toString() });
    }
    if (esearchResult.ERROR) {
      return failure('pubmed_error', {
        query: finalTerm,
        esearchUrl: esearch.toString(),
        message: collapse(esearchResult.ERROR),
      });
    }

    const count = Number(esearchResult.count ?? 0);
    const uids = Array.isArray(esearchResult.idlist) ? esearchResult.idlist.map(String) : [];
    const base = {
      ok: true,
      query: finalTerm,
      count: Number.isFinite(count) ? count : 0,
      retmax,
      sort,
      types: pubtypes,
      dates,
      esearchUrl: esearch.toString(),
      esummaryUrl: null,
      items: [],
    };
    if (!uids.length) return base; // count=0 是「真的没命中」，与失败返回的 ok:false 是两件事

    const esummary = new URL(`${EUTILS}/esummary.fcgi`);
    esummary.searchParams.set('db', 'pubmed');
    esummary.searchParams.set('id', uids.join(','));
    esummary.searchParams.set('retmode', 'json');
    esummary.searchParams.set('tool', TOOL);
    esummary.searchParams.set('email', email);
    if (apiKey) esummary.searchParams.set('api_key', apiKey);

    const summaryRes = await schedule(() =>
      requestJson(esummary.toString(), { fetchImpl, timeoutMs, headers }),
    );
    if (!summaryRes.ok) {
      return failure(summaryRes.error, {
        query: finalTerm,
        count: base.count,
        esearchUrl: base.esearchUrl,
        esummaryUrl: esummary.toString(),
        status: summaryRes.status ?? null,
      });
    }

    const items = itemsFromSummary(summaryRes.json, uids);
    if (!items.length) {
      // 有 id 却解析不出条目：绝不能回「0 条」，那是把解析失败伪装成检索结论
      return failure('summary_parse', {
        query: finalTerm,
        count: base.count,
        esearchUrl: base.esearchUrl,
        esummaryUrl: esummary.toString(),
      });
    }
    return { ...base, esummaryUrl: esummary.toString(), items };
  }

  /**
   * DOI 字段级核验：先确认 DOI 能解析（最便宜的一步），再逐字段对账。
   * 返回的 fields 每项都是 `{field, expected, actual, match}`，match ∈ exact|fuzzy|mismatch|missing，
   * 让人一眼看出「错在哪一栏」，而不是笼统的「引用有问题」。
   */
  async function compareDoi(args = {}) {
    const doi = normalizeDoi(args.doi);
    if (!DOI_RE.test(doi)) return failure('invalid_doi', { doi: String(args.doi ?? '') });
    const expected = isObject(args.expected) ? args.expected : {};

    const url = new URL(`${CROSSREF}/${encodeURIComponent(doi)}`);
    url.searchParams.set('mailto', email);
    const res = await requestJson(url.toString(), { fetchImpl, timeoutMs, headers });

    if (!res.ok) {
      if (res.status === 404) {
        // 中文期刊多数不进 Crossref：查不到不等于「这条引用是假的」，必须降级成「无法核实」
        if (looksChinese(expected)) {
          return {
            ok: true,
            doi,
            source: 'crossref',
            status: 'unverifiable',
            hint: '中文期刊多不在 Crossref，请人工核对原文',
            fields: [],
            crossref: null,
          };
        }
        return { ok: true, doi, source: 'crossref', status: 'not_found', fields: [], crossref: null };
      }
      return { ok: false, doi, source: 'crossref', status: 'unverifiable', error: res.error };
    }

    const message = res.json?.message;
    if (!isObject(message)) return failure('crossref_bad_response', { doi, source: 'crossref', status: 'unverifiable' });

    const crossref = {
      doi: normalizeDoi(message.DOI) || doi,
      type: message.type ? String(message.type) : null,
      title: stripHtml(collapse(firstString(message.title))),
      journal: collapse(firstString(message['container-title'])),
      year: crossrefYear(message),
      volume: message.volume ? String(message.volume) : null,
      issue: message.issue ? String(message.issue) : null,
      // 电子刊（Nature/Cell 系、PLOS、BMC）用 article-number 代替页码，Crossref 的 page 为空；
      // 不回落成 null，否则每条这类文献都会被判成「页码缺失」。
      pages: message.page ? String(message.page) : message['article-number'] ? String(message['article-number']) : null,
      pageKind: message.page ? 'page' : message['article-number'] ? 'article-number' : null,
      authors: crossrefAuthors(message),
    };

    const fields = [];
    const push = (field, exp, act, match, warn) => {
      const row = { field, expected: exp ?? null, actual: act ?? null, match };
      if (warn) row.warn = warn;
      fields.push(row);
    };

    if (expected.title) {
      const sim = jaccard(titleTokens(expected.title), titleTokens(crossref.title));
      const match = sim >= 0.9 ? 'exact' : sim >= 0.75 ? 'fuzzy' : 'mismatch';
      push('title', expected.title, crossref.title, match);
    }
    if (Array.isArray(expected.authors) && expected.authors.length) {
      const expFamilies = expected.authors.map(normalizeName).filter(Boolean);
      const actualFamilies = messageAuthorFamilies(message);
      const all = new Set([...actualFamilies, ...crossref.authors.map(normalizeName)]);
      const firstOk = expFamilies.length ? all.has(expFamilies[0]) : true;
      const missing = expFamilies.filter((f) => !all.has(f));
      let match;
      let warn;
      if (!firstOk) match = 'mismatch'; // 首作者被换掉是最严重的一类错误，不给模糊空间
      else if (missing.length) match = 'fuzzy';
      else match = 'exact';
      if (firstOk && Math.abs(expFamilies.length - actualFamilies.length) > 1) warn = 'author_count';
      push('authors', expFamilies.length === 1 ? expFamilies[0] : expected.authors, crossref.authors, match, warn);
    }
    if (expected.year !== undefined && expected.year !== null && String(expected.year).trim() !== '') {
      const expYear = Number(String(expected.year).trim());
      const actYear = crossref.year;
      let match;
      if (!Number.isFinite(expYear) || actYear === null) match = 'missing';
      else if (expYear === actYear) match = 'exact';
      else if (Math.abs(expYear - actYear) <= 1) match = 'fuzzy'; // 在线优先出版与正式卷期常差一年
      else match = 'mismatch';
      push('year', String(expected.year).trim(), actYear, match);
    }
    for (const key of ['journal', 'volume', 'issue', 'pages']) {
      const exp = expected[key];
      if (exp === undefined || exp === null || String(exp).trim() === '') continue;
      const act = crossref[key];
      const expNorm = key === 'journal' ? normalizeTitle(exp) : normalizeNumberish(exp);
      const actNorm = act === null ? '' : key === 'journal' ? normalizeTitle(act) : normalizeNumberish(act);
      let match;
      if (!actNorm) match = 'missing';
      else if (expNorm === actNorm) match = 'exact';
      else if (key === 'journal' && jaccard(titleTokens(exp), titleTokens(act)) >= 0.5) match = 'fuzzy'; // 刊名缩写差异
      else match = 'mismatch';
      push(key, String(exp).trim(), act, match);
    }

    const status = fields.some((f) => f.match === 'mismatch') ? 'mismatch' : 'verified';
    return { ok: true, doi, source: 'crossref', status, fields, crossref };
  }

  return { version, email, searchPubmed, compareDoi };
}

// ---------------------------------------------------------------------------
// 参数整理小函数（放外面，便于单独测）
// ---------------------------------------------------------------------------

function clampInt(value, fallback, min, max) {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.min(max, Math.max(min, Math.trunc(n)));
}

/** PubMed sort 只认 relevance / pub_date 两档；别的值原样透传，让 PubMed 自己报错而不是悄悄换排序。 */
function mapSort(value) {
  const s = String(value ?? 'relevance').trim().toLowerCase();
  if (!s || s === 'relevance' || s === 'relevance_date') return 'relevance';
  if (s === 'pub_date' || s === 'pubdate' || s === 'date') return 'pub_date';
  return s;
}

/** mindate/maxdate：接受 2020、2020-05、2020-05/01、2020/05/01 → PubMed 的 YYYY/MM/DD */
function cleanDate(value) {
  const raw = String(value ?? '').trim();
  if (!raw) return '';
  const m = raw.match(/^(\d{4})(?:[-/](\d{1,2}))?(?:[-/](\d{1,2}))?$/);
  if (!m) return '';
  const parts = [m[1]];
  if (m[2]) parts.push(String(Number(m[2])).padStart(2, '0'));
  if (m[3]) parts.push(String(Number(m[3])).padStart(2, '0'));
  return parts.join('/');
}

/**
 * types 一律归一成「出版类型词」，由调用方再拼 `[pt]`。
 * 带字段标签的（`review[pt]`、`Review`）都先剥掉标签，避免拼出 `review[pt][pt]` 这种废词。
 */
function normalizeTypes(value) {
  const list = Array.isArray(value) ? value : value === undefined || value === null ? [] : [value];
  const out = [];
  for (const raw of list) {
    const t = collapse(raw)
      .replace(/^["']|["']$/g, '')
      .replace(/\[[^\]]+\]$/, '')
      .trim();
    if (t && !out.includes(t)) out.push(t);
  }
  return out;
}

function looksChinese(expected) {
  return [expected.title, expected.journal, ...(Array.isArray(expected.authors) ? expected.authors : [])].some(hasCjk);
}

function crossrefYear(message) {
  const parts =
    message?.issued?.['date-parts']?.[0] ??
    message?.['published-print']?.['date-parts']?.[0] ??
    message?.['published-online']?.['date-parts']?.[0] ??
    message?.published?.['date-parts']?.[0] ??
    null;
  if (!Array.isArray(parts) || !Number.isFinite(Number(parts[0]))) return null;
  return Number(parts[0]);
}

function crossrefAuthors(message) {
  const list = Array.isArray(message?.author) ? message.author : [];
  return list
    .map((a) => collapse([a?.given, a?.family].filter(Boolean).join(' ')))
    .filter(Boolean);
}

function messageAuthorFamilies(message) {
  const list = Array.isArray(message?.author) ? message.author : [];
  return list.map((a) => normalizeName(a?.family ?? '')).filter(Boolean);
}
