#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Biomed Literature Pipeline — 全生物医学领域文献调研流水线
适用于任意临床/基础医学专业与研究方向，英文（SCI）+ 中文（核心期刊）双轨检索。

子命令:
  search    检索（英文: Europe PMC 多路径；中文: OpenAlex + 核心期刊白名单过滤）
  download  下载全文（多通道: EPMC-render / S2 / Unpaywall / OpenAlex / 网页全文转PDF）
  rename    PDF 按论文标题重命名
  excel     生成 Excel 清单（含语种/来源库/获取方式）
  stats     输出库结构统计（供撰写前沿报告）
  guide     生成中文库检索式（CNKI / 万方 / SinoMed）与导出步骤
  import    导入中文库导出的文件（CNKI / RefWorks / EndNote RIS / CSV）

用法: python pipeline.py <子命令> --out <目录> [选项]
依赖: requests, openpyxl；网页通道需 bs4 + lxml + pymupdf（缺失时自动降级并提示）
"""
import argparse, collections, csv, io, json, os, re, sys, time
import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
      "Accept-Language": "zh-CN,zh;q=0.9,en-US;en;q=0.8"}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OPENALEX = "https://api.openalex.org/works"
MAILTO = "lit.pipeline@example.org"
MIN_FULLTEXT = 8000
HERE = os.path.dirname(os.path.abspath(__file__))
CN_WHITELIST_FILE = os.path.join(HERE, "..", "references", "cn_journals.json")

try:
    from bs4 import BeautifulSoup
    _HAS_BS4 = True
except Exception:
    _HAS_BS4 = False
try:
    import pymupdf
    _HAS_PDF = True
except Exception:
    try:
        import fitz as pymupdf
        _HAS_PDF = True
    except Exception:
        _HAS_PDF = False

# ============================ 通用配置（非专业限定） ============================
# 检索噪声：这些出现在标题里的内容与"研究前沿"无关，一律剔除（跨学科通用）
TITLE_NOISE = [
    "retraction", "retracted", "erratum", "corrigendum", "correction to",
    "author correction", "editor's note", "withdrawn", "expression of concern",
    "comment on", "reply to", "response to reviewer", "letter to the editor",
]
# 通用停用词（用于从主题式自动派生相关性关键词）
STOP = set("""and or of the in on for with to a an by from as at is are be study studies
clinical research analysis review systematic meta effect effects role impact outcomes
patients patient trial randomized randomised cohort case control versus vs among between
during after before using use used results conclusion background methods objective""".split())

# ============================ 中文核心期刊白名单 ============================
def load_cn_whitelist():
    try:
        d = json.load(open(CN_WHITELIST_FILE, encoding="utf-8"))
        return set(d.get("journals", [])), d.get("by_category", {})
    except Exception:
        return set(), {}

CN_CORE, CN_BY_CAT = load_cn_whitelist()
try:
    _CNW = json.load(open(CN_WHITELIST_FILE, encoding="utf-8"))
    CN_ALT = set(_CNW.get("alt_names", []))
    CN_ISSN = set(_CNW.get("issns", []))
except Exception:
    CN_ALT, CN_ISSN = set(), set()

def _norm_cn(s):
    return re.sub(r"[\s\.·・\-—_（）()\[\]【】:：,，;；]+", "", (s or "")).lower()

_CN_CORE_NORM = {_norm_cn(x) for x in CN_CORE}
_CN_ALT_NORM = {_norm_cn(x) for x in CN_ALT}

def is_cn_core(journal, issn=""):
    """判断期刊是否属于中文核心（中华系列 / CSCD / 北大核心）
    支持：中文刊名、罗马化/拼音别名、ISSN"""
    if issn and issn in CN_ISSN:
        return True
    if not journal:
        return False
    j = journal.strip()
    jn = _norm_cn(j)
    if not jn:
        return False
    if jn in _CN_CORE_NORM or jn in _CN_ALT_NORM:
        return True
    for c in _CN_CORE_NORM:
        if len(c) >= 5 and (c in jn or jn in c):
            return True
    for a in _CN_ALT_NORM:
        if len(a) >= 8 and (a in jn or jn in a):
            return True
    # 中文刊罗马化的通用特征
    low = j.lower()
    if low.startswith(("zhonghua ", "zhongguo ", "beijing da xue", "sichuan da xue",
                       "nan fang yi ke", "zhong nan da xue", "di san jun yi", "di er jun yi")):
        return True
    if re.match(r"^(chinese|china)\s+(journal|medical|critical)", low):
        return True
    return False

# ============================ 工具函数 ============================
def epmc(query, page_size=25, sort="CITED desc", retries=5):
    """Europe PMC 检索（含指数退避重试，应对 429/5xx 限流）"""
    last = None
    for a in range(retries):
        try:
            r = requests.get(EPMC, params={"query": query, "format": "json", "pageSize": page_size,
                                           "resultType": "core", "sort": sort},
                             headers={"User-Agent": UA["User-Agent"]}, timeout=45)
            if r.status_code == 200 and r.text.strip():
                try:
                    return r.json().get("resultList", {}).get("result", [])
                except Exception:
                    pass
            last = r.status_code
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(min(4 * (a + 1), 20)); continue
            return []
        except Exception:
            time.sleep(min(3 * (a + 1), 15))
    if last:
        print(f"    [!] Europe PMC 暂时不可用（HTTP {last}），本轮该检索跳过")
    return []

def openalex_search(query, per_page=25, y0=2021, sort="cited_by_count:desc", language=None, retries=3):
    """OpenAlex 检索（支持中文关键词）。language='zh' 时限制语种。含退避重试。"""
    flt = f"from_publication_date:{y0}-01-01"
    if language:
        flt += f",language:{language}"
    for a in range(retries):
        try:
            r = requests.get(OPENALEX, params={"search": query, "per-page": per_page,
                                               "filter": flt, "sort": sort, "mailto": MAILTO},
                             headers={"User-Agent": UA["User-Agent"]}, timeout=45)
            if r.status_code == 200 and r.text.strip():
                return r.json().get("results", [])
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(min(3 * (a + 1), 12)); continue
            return []
        except Exception:
            time.sleep(2 * (a + 1))
    return []

def _clean_journal(j):
    """中文刊在 MEDLINE 中形如 'Zhongguo gu shang = China journal of ...'，取前半段更简洁"""
    j = (j or "").strip()
    if " = " in j:
        j = j.split(" = ")[0].strip()
    return j

def norm_en(rec):
    return {"pmid": rec.get("pmid", ""), "pmcid": rec.get("pmcid", ""), "doi": rec.get("doi", ""),
            "title": (rec.get("title") or "").strip().rstrip("."),
            "journal": _clean_journal(rec.get("journalInfo", {}).get("journal", {}).get("title") or rec.get("journalTitle") or ""),
            "year": str(rec.get("pubYear") or ""), "authors": rec.get("authorString", ""),
            "cited": int(rec.get("citedByCount") or 0), "is_oa": rec.get("isOpenAccess", "N"),
            "has_pdf": rec.get("hasPDF", "N"), "in_epmc": rec.get("inEPMC", "N"),
            "pubtypes": "; ".join((rec.get("pubTypeList", {}) or {}).get("pubType", [])) if isinstance(rec.get("pubTypeList", {}), dict) else "",
            "abstract": (rec.get("abstractText") or "")[:1500], "source": rec.get("source", ""),
            "lang": ("zh" if (rec.get("language") or "").lower() in ("chi", "zho", "zh") else "en"),
            "source_db": "Europe PMC"}

def norm_oa(w):
    """OpenAlex work -> 统一记录"""
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    inv = w.get("abstract_inverted_index") or {}
    abstract = ""
    if inv:
        pos = {}
        for word, idxs in inv.items():
            for i in idxs:
                pos[i] = word
        abstract = " ".join(pos[k] for k in sorted(pos))[:1500]
    authors = "; ".join(a.get("author", {}).get("display_name", "") for a in (w.get("authorships") or [])[:8])
    doi = (w.get("doi") or "").replace("https://doi.org/", "")
    oa = w.get("open_access") or {}
    return {"pmid": (w.get("ids") or {}).get("pmid", "").replace("https://pubmed.ncbi.nlm.nih.gov/", "").rstrip("/"),
            "pmcid": (w.get("ids") or {}).get("pmcid", "").replace("https://www.ncbi.nlm.nih.gov/pmc/articles/", "").rstrip("/"),
            "doi": doi, "title": (w.get("title") or w.get("display_name") or "").strip().rstrip("."),
            "journal": src.get("display_name") or "", "year": str(w.get("publication_year") or ""),
            "authors": authors, "cited": int(w.get("cited_by_count") or 0),
            "is_oa": "Y" if oa.get("is_oa") else "N", "has_pdf": "N", "in_epmc": "N",
            "pubtypes": (w.get("type") or ""), "abstract": abstract, "source": "OpenAlex",
            "lang": w.get("language") or "", "source_db": "OpenAlex",
            "issn": (src.get("issn") or [None])[0] or ""}

def key_of(r):
    if r.get("doi"):
        return r["doi"].lower()
    if r.get("pmid"):
        return "pmid:" + str(r["pmid"])
    if r.get("title"):
        return "t:" + r["title"].lower()[:80]
    return None

def safe_name(s, n=150):
    s = re.sub(r'[\\/:*?"<>|\r\n\t]+', " ", s or "")
    return (re.sub(r"\s+", " ", s).strip().strip(".")[:n].strip() or "untitled")

def load_corpus(out):
    fp = os.path.join(out, "corpus_raw.json")
    if not os.path.exists(fp):
        sys.exit(f"[错误] 找不到 {fp}，请先运行 search")
    return json.load(open(fp, encoding="utf-8"))

def save_corpus(out, data):
    json.dump(data, open(os.path.join(out, "corpus_raw.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

# ---------- 主题解析与相关性关键词自动派生 ----------
def parse_topics(args):
    """返回 {主题名: 检索表达式} 与 主题名列表"""
    if args.topics:
        raw = json.load(open(args.topics, encoding="utf-8"))
        # 支持 {"topics": {...}} 或直接 {...}
        topics = raw.get("topics", raw) if isinstance(raw, dict) else raw
        topics = {k: v for k, v in topics.items() if isinstance(v, str)}
        return topics
    if args.topic:
        return {"__topic__": args.topic}
    return {}

def has_chinese(s):
    return bool(re.search(r"[\u4e00-\u9fff]", s or ""))

def derive_keywords(topics):
    """从主题表达式自动派生相关性关键词（不依赖任何专业硬编码词表）。
    - 引号内的英文短语**整体保留**（如 "acute kidney injury"），保证匹配精度
    - 引号外未被覆盖的裸词再作补充
    - 中文主题按连接词切分为语义单元
    """
    kws = set()
    for name, q in topics.items():
        if name != "__topic__":
            kws.add(name.lower())
        phrases = re.findall(r'"([^"]+)"', q)
        for ph in phrases:
            kws.add(ph if has_chinese(ph) else ph.lower().strip())
        # 引号外的裸词（排除已被短语覆盖的）
        rest = re.sub(r'"[^"]*"', " ", q)
        covered = set()
        for ph in phrases:
            covered |= set(re.split(r"[\s\-]+", ph.lower()))
        for w in re.findall(r"[a-zA-Z][a-zA-Z\-]{3,}", rest.lower()):
            if w not in STOP and w not in covered:
                kws.add(w)
        # 中文主题（无引号）：按连接词切分
        if has_chinese(q) and '"' not in q:
            for seg in re.split(r"[与和及、,，/;；\s]+|OR|AND", q):
                seg = seg.strip()
                if has_chinese(seg) and len(seg) >= 2:
                    kws.add(seg)
    return sorted(kws, key=len, reverse=True)

def _cn_grams(kw):
    """中文关键词的匹配碎片：全串 + 2~4 字子串"""
    out = {kw}
    for n in (4, 3, 2):
        for i in range(0, max(0, len(kw) - n + 1)):
            out.add(kw[i:i + n])
    return out

def _en_hit(kw, text_lower):
    """英文关键词匹配：整短语命中，或（多词时）各词均出现（顺序无关）"""
    if kw in text_lower:
        return True
    parts = [p for p in re.split(r"[\s\-]+", kw) if len(p) >= 3]
    if len(parts) >= 2:
        return all(p in text_lower for p in parts)
    return False

def make_keep_epmc_cn(en_kws):
    """Europe PMC 中文语种通道专用过滤：核心词（前 2 个）优先。
    规则：标题命中核心词 → 收；或标题命中 ≥2 个关键词 → 收；否则丢弃。
    这样可滤掉"高召回"分支带入的偏题文献（如仅含 bleeding 的中药/消化科论文）。"""
    core = en_kws[:2]

    def keep(r):
        t = (r.get("title") or "").strip()
        if not t:
            return False
        tl = t.lower()
        if any(n in tl for n in TITLE_NOISE):
            return False
        hits_all = sum(1 for k in en_kws if _en_hit(k, tl))
        hits_core = sum(1 for k in core if _en_hit(k, tl))
        return hits_core >= 1 or hits_all >= 2
    return keep

def make_keep(keywords, lang="both"):
    en_kw = [k for k in keywords if not has_chinese(k)]
    cn_kw = [k for k in keywords if has_chinese(k)]
    cn_frags = set()
    for k in cn_kw:
        cn_frags |= _cn_grams(k)
    cn_frags_strong = {x for x in cn_frags if len(x) >= 3}

    def keep(r):
        t = (r.get("title") or "").strip()
        if not t:
            return False
        tl = t.lower()
        if any(n in tl for n in TITLE_NOISE):
            return False
        if lang == "cn_only" and not has_chinese(t):
            return False
        if lang == "en_only" and has_chinese(t):
            return False
        # 标题命中即可
        if any(_en_hit(k, tl) for k in en_kw):
            return True
        if cn_frags and any(f in t for f in cn_frags):
            return True
        # 标题未中 → 摘要兜底（命中 ≥2 个关键词，降低漏检）
        ab = (r.get("abstract") or "")
        if not ab:
            return False
        abl = ab.lower()
        hits = sum(1 for k in en_kw if _en_hit(k, abl)) + sum(1 for f in cn_frags_strong if f in ab)
        return hits >= 2
    return keep

# ============================ search ============================
def cmd_search(args):
    out = args.out
    os.makedirs(out, exist_ok=True)
    topics = parse_topics(args)
    if not topics:
        sys.exit("[错误] 请用 --topic \"方向/关键词\" 指定检索方向，或用 --topics 传入 JSON 主题表")
    keywords = derive_keywords(topics)
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(";") if k.strip()] + keywords
    keep = make_keep(keywords, args.lang)
    y0, y1 = args.years.split("-")
    yr = f"[{y0} TO {y1}]"

    print(f"[i] 检索方向: {list(topics.keys())}")
    print(f"[i] 相关性关键词（自动派生 {len(keywords)} 个）: {', '.join(keywords[:14])}{' ...' if len(keywords) > 14 else ''}")
    print(f"[i] 语种模式: {args.lang} | 时间: {yr}\n")

    corpus, dropped = {}, 0

    def add(recs, tag, normfn=norm_en, keepfn=None):
        nonlocal dropped
        kf = keepfn or keep
        n = 0
        for raw in recs:
            x = normfn(raw)
            if not x["title"]:
                continue
            if not kf(x):
                dropped += 1; continue
            k = key_of(x)
            if not k:
                continue
            if k not in corpus:
                x["areas"] = [tag]; corpus[k] = x; n += 1
            elif tag not in corpus[k]["areas"]:
                corpus[k]["areas"].append(tag)
        return n

    total_steps = 0
    for _ in topics:
        total_steps += 2
    total_steps += len(getattr(args, "journals_list", []) or [])
    step = 0

    # ---- 英文轨道 ----
    en_topics = {a: q for a, q in topics.items() if not has_chinese(q)}
    if en_topics and args.lang in ("both", "en", "en_only"):
        if len(en_topics) < len(topics):
            print(f"[i] 英文轨道跳过 {len(topics)-len(en_topics)} 个纯中文主题（这些走中文轨道）\n")
        print(f"路径A: 主题 × 高被引（Europe PMC）{yr}")
        for a, q in en_topics.items():
            step += 1
            expr = q if re.search(r"\b(AND|OR|NOT)\b|SRC:|JOURNAL:", q) else f'("{q}")' if " " in q else q
            n = add(epmc(f'({expr}) AND (SRC:MED) AND (PUB_YEAR:{yr})', args.per_page), a)
            print(f"  [{step}/{total_steps}] {a[:34]:36s} +{n:>3d} 累计{len(corpus):>4d}"); time.sleep(0.35)

        steps_years = f"[{max(int(y0), int(y1)-2)} TO {y1}]"
        print(f"\n路径B: 近三年加厚 {steps_years}")
        for a, q in en_topics.items():
            step += 1
            expr = q if re.search(r"\b(AND|OR|NOT)\b|SRC:|JOURNAL:", q) else f'("{q}")' if " " in q else q
            n = add(epmc(f'({expr}) AND (SRC:MED) AND (PUB_YEAR:{steps_years})', max(15, args.per_page - 5)), "[近期] " + a)
            print(f"  [{step}/{total_steps}] {a[:34]:36s} +{n:>3d} 累计{len(corpus):>4d}"); time.sleep(0.3)

        if args.journals_list:
            dom = " OR ".join(f'"{k}"' for k in keywords[:12] if not has_chinese(k)) or "\"study\""
            print(f"\n路径C: 指定期刊 × 主题约束 {yr}")
            for j in args.journals_list:
                step += 1
                n = add(epmc(f'(JOURNAL:"{j}") AND ({dom}) AND (SRC:MED) AND (PUB_YEAR:{yr})', max(15, args.per_page - 5)), "[期刊] " + j)
                print(f"  [{step}/{total_steps}] {j[:40]:42s} +{n:>3d} 累计{len(corpus):>4d}"); time.sleep(0.35)
    elif not en_topics and args.lang in ("en", "en_only"):
        print("[!] 英文轨道：未提供英文主题（当前主题均为中文）。如需英文文献，请同时给出英文关键词。")

    # ---- 中文轨道 ----
    if args.lang in ("both", "cn", "cn_only"):
        cn_terms = [t for t in topics.values() if has_chinese(t)] or \
                   ([t for t in topics.keys() if t != "__topic__" and has_chinese(t)])
        cn_terms = [re.sub(r"[（）()\"]", "", t) for t in cn_terms]
        en_kws = [k for k in keywords if not has_chinese(k)]
        keep_any = make_keep(keywords, "both")     # 不按语种过滤（用于中文刊的英文题录）
        keep_epmc = make_keep_epmc_cn(en_kws)      # 中文通道专用（核心词优先）
        got_epmc = got_oa = 0

        # D1: Europe PMC 中文语种通道 —— 覆盖中华系列 / CSCD / 北大核心的中文文献（附 PMID/PMCID）
        # 按主题分别构建检索式（避免多主题关键词相互污染）
        plan = []
        for tname, tq in topics.items():
            kws_t = [k for k in derive_keywords({tname: tq}) if not has_chinese(k)]
            if tname == "__topic__" and args.keywords:
                kws_t = [k.strip() for k in args.keywords.split(";") if k.strip()] + kws_t
            kws_t = list(dict.fromkeys(kws_t))
            if kws_t:
                plan.append((tname, kws_t))
        if plan:
            print(f"\n路径D1(主): 中文核心刊文献（Europe PMC LANG:chi，题录为英文翻译）{yr}")
            all_merged, seen_ids = [], set()
            for tname, kws_t in plan:
                if args.cn_query and len(plan) == 1:
                    queries = [("自定义", args.cn_query)]
                elif len(kws_t) >= 2:
                    # 高精度：核心词 AND (其余同义/相关词 OR)。实测精度显著优于纯 OR，
                    # 纯 OR 会带入大量仅共享泛词的偏题文献（如"bleeding"/"care"）
                    queries = [("高精度", f'("{kws_t[0]}") AND (' + " OR ".join(f'"{k}"' for k in kws_t[1:8]) + ")")]
                else:
                    queries = [("单主题", f'"{kws_t[0]}"')]
                got_t = 0
                for kind, qd in queries:
                    recs = epmc(f'({qd}) AND (LANG:"chi") AND (SRC:MED) AND (PUB_YEAR:{yr})',
                                max(args.per_page, 30), sort="CITED desc")
                    print(f"  「{str(tname)[:16]}」[{kind}] {qd[:74]} → {len(recs)}")
                    for r in recs:
                        rid = r.get("pmid") or r.get("doi") or r.get("title")
                        if rid and rid not in seen_ids:
                            seen_ids.add(rid); all_merged.append((r, tname, kws_t))
            got_epmc = 0
            for r, tname, kws_t in all_merged:
                x = norm_en(r)
                if not x["title"] or not make_keep_epmc_cn(kws_t)(x):
                    dropped += 1; continue
                k = key_of(x)
                if not k: continue
                tag = ("[中文·EPMC] " + str(tname)) if tname != "__topic__" else "[中文·EPMC]"
                if k not in corpus:
                    x["areas"] = [tag]; corpus[k] = x; got_epmc += 1
                elif tag not in corpus[k]["areas"]:
                    corpus[k]["areas"].append(tag)
            print(f"  合并去重 {len(all_merged)} 篇 → 入库 +{got_epmc}（累计 {len(corpus)}）")
            jc = collections.Counter(_clean_journal(
                (r.get("journalInfo", {}) or {}).get("journal", {}).get("title") or r.get("journalTitle") or "?")
                for r, _, _ in all_merged)
            for j, c in jc.most_common(6):
                print(f"      {c:>3d}  {str(j)[:62]}")

        # D2: OpenAlex 中文检索 + 核心刊白名单
        if cn_terms:
            print(f"\n路径D2(补): 中文文献（OpenAlex + 核心刊白名单）")
            all_hits = core_hits = 0
            for t in cn_terms[:12]:
                raw = openalex_search(t, args.per_page, int(y0))
                all_hits += len(raw)
                if args.cn_all:
                    sel = raw
                else:
                    sel = []
                    for w in raw:
                        src = (w.get("primary_location") or {}).get("source") or {}
                        if is_cn_core(src.get("display_name"), (src.get("issn") or [""])[0]):
                            sel.append(w)
                core_hits += len(sel)
                n = add(sel, "[中文·OA] " + t, norm_oa)
                got_oa += n
                print(f"    「{t[:18]}」命中{len(raw):>3d} → 核心刊{len(sel):>3d} 入库+{n:>2d} 累计{len(corpus):>4d}")
                time.sleep(0.3)
            print(f"    [i] OpenAlex 中文文献总量 {all_hits}，其中核心刊 {core_hits}")

        if not en_kws:
            print("\n[!] 中文主通道需要**英文关键词**（中文刊在 Europe PMC 的题录是英文翻译）——"
                  "请同时给出该方向的英文关键词（--keywords，或在 --topics 中给出英文检索式）。")
        print(f"    [i] 中文轨道小结: EPMC 中文核心刊 +{got_epmc}，OpenAlex +{got_oa}。"
              f" CNKI/万方/SinoMed 的完整中文核心文献，请用 `guide` 生成检索式、导出后用 `import` 入库。")

    if not corpus:
        print("\n[!] 未检索到任何文献。请检查主题关键词，或放宽 --lang。")
        return

    save_corpus(out, {"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
                      "topic": arg_echo(args), "years": args.years,
                      "keywords": keywords, "total": len(corpus), "filtered_out": dropped,
                      "records": list(corpus.values())})
    oa = sum(1 for r in corpus.values() if r["is_oa"] == "Y")
    cn = sum(1 for r in corpus.values() if has_chinese(r["title"]))
    print(f"\n{'='*64}\n入库 {len(corpus)} 篇（剔除无关 {dropped}）| OA {oa} | 中文标题 {cn}\n输出: {out}/corpus_raw.json")

def arg_echo(args):
    if getattr(args, "topics", ""):
        return f"topics:{args.topics}"
    return getattr(args, "topic", "")

# ============================ download ============================
def _is_pdf(c): return c[:5] == b"%PDF-" and len(c) > 15000

def _fetch(url, referer=None, timeout=30):
    h = dict(UA)
    if referer: h["Referer"] = referer
    try:
        r = requests.get(url, headers=h, timeout=timeout, allow_redirects=True)
        if r.status_code == 200 and _is_pdf(r.content):
            return r.content
    except Exception:
        pass
    return None

def _oa_pdf_urls(rec):
    doi = rec.get("doi", "")
    urls = []
    if not doi: return urls
    try:
        r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf",
                         headers={"User-Agent": UA["User-Agent"]}, timeout=25)
        if r.status_code == 200:
            u = (r.json().get("openAccessPdf") or {}).get("url")
            if u: urls.append(("s2", u))
        elif r.status_code == 429:
            time.sleep(2)
    except Exception: pass
    try:
        r = requests.get(f"https://api.unpaywall.org/v2/{doi}?email={MAILTO}",
                         headers={"User-Agent": UA["User-Agent"]}, timeout=25)
        if r.status_code == 200:
            d = r.json()
            for loc in ([d.get("best_oa_location")] + (d.get("oa_locations") or [])):
                if loc and loc.get("url_for_pdf"): urls.append(("unpaywall", loc["url_for_pdf"]))
    except Exception: pass
    try:
        r = requests.get(f"https://api.openalex.org/works/doi:{doi}?mailto={MAILTO}",
                         headers={"User-Agent": UA["User-Agent"]}, timeout=25)
        if r.status_code == 200:
            d = r.json()
            for loc in ([d.get("best_oa_location")] + (d.get("locations") or [])):
                if loc and loc.get("pdf_url"): urls.append(("openalex", loc["pdf_url"]))
    except Exception: pass
    seen, out = set(), []
    for src, u in urls:
        if u and u not in seen:
            seen.add(u); out.append((src, u))
    return out

HTML_HOSTS_OK = ["frontiersin.org", "biomedcentral.com", "bmj.com", "jamanetwork.com",
                 "nature.com", "sciencedirect.com", "springer", "wiley", "onlinelibrary",
                 "academic.oup.com", "journals.lww.com", "ahajournals.org", "thoracic.org",
                 "atsjournals.org", "springeropen.com", "plos.org", "mdpi.com", "karger.com",
                 "thieme", "tandfonline", "sagepub", "liebertpub", "elsevier", "cell.com",
                 "europepmc.org", "ncbi.nlm.nih.gov"]

def _extract_fulltext(html_text):
    if not _HAS_BS4: return []
    soup = BeautifulSoup(html_text, "lxml")
    for t in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript", "iframe", "button"]):
        t.decompose()
    cands = ["article", "div.article-body", "div.article__body", "div.fulltext", "div.full-text",
             "section.body", "div#bodymatter", "div.body", "main", "div#content", "div.content",
             "div.article-content", "div#article-content", "div.c-article-body"]
    node = None
    for sel in cands:
        for n in soup.select(sel):
            if len(n.get_text(" ", strip=True)) > MIN_FULLTEXT:
                node = n; break
        if node: break
    if node is None and soup.body and len(soup.body.get_text(" ", strip=True)) > MIN_FULLTEXT:
        node = soup.body
    if node is None: return []
    paras = []
    for el in node.find_all(["h1", "h2", "h3", "h4", "p", "li"], recursive=True):
        t = el.get_text(" ", strip=True)
        if len(t) < 25: continue
        if any(k in t.lower() for k in ("cookie", "subscribe", "sign in", "advertisement",
                                        "download pdf", "privacy policy", "terms of use",
                                        "all rights reserved", "we use cookies")):
            continue
        paras.append((el.name.upper() if el.name.startswith("h") else "P", t))
    return paras if sum(len(t) for _, t in paras) >= MIN_FULLTEXT else []

def _paras_to_pdf(paras, rec, pdf_dir):
    if not _HAS_PDF or not paras: return None
    import html as htmlmod
    esc = lambda s: htmlmod.escape(s)
    parts = [f"<h1>{esc(rec['title'])}</h1>",
             f"<p><i>{esc((rec.get('authors') or '')[:300])}<br/>{esc(rec.get('journal',''))} · {rec.get('year','')} · DOI: {esc(rec.get('doi',''))}</i></p><hr/>"]
    for tag, t in paras:
        if tag == "P":
            parts.append(f"<p>{esc(t)}</p>")
        else:
            lv = min(int(tag[1]), 3)
            parts.append(f"<h{lv}>{esc(t)}</h{lv}>")
    parts.append(f"<hr/><p><i>来源：网页版全文自动归档 · {time.strftime('%Y-%m-%d')}</i></p>")
    html_doc = "<html><body>" + "".join(parts) + "</body></html>"
    base = safe_name(rec["title"]); fn = base + ".pdf"; i = 2
    while os.path.exists(os.path.join(pdf_dir, fn)):
        fn = f"{base}_{i}.pdf"; i += 1
    fp = os.path.join(pdf_dir, fn)
    try:
        story = pymupdf.Story(html=html_doc)
        writer = pymupdf.DocumentWriter(fp)
        mediabox = pymupdf.paper_rect("a4"); where = mediabox + (45, 45, -45, -45)
        more, guard = 1, 0
        while more and guard < 400:
            dev = writer.begin_page(mediabox)
            more, _ = story.place(where)
            story.draw(dev); writer.end_page(); guard += 1
        writer.close()
        if os.path.exists(fp) and os.path.getsize(fp) > 20000: return fp
        os.remove(fp)
    except Exception:
        pass
    return None

def _try_html_fulltext(rec, pdf_dir):
    doi = rec.get("doi", "")
    if not doi or not _HAS_BS4 or not _HAS_PDF: return None
    try:
        r = requests.get(f"https://doi.org/{doi}", headers=UA, timeout=35, allow_redirects=True)
    except Exception:
        return None
    if r.status_code != 200 or "html" not in r.headers.get("Content-Type", "").lower(): return None
    host = re.sub(r"^https?://([^/]+).*$", r"\1", r.url)
    if not any(h in host for h in HTML_HOSTS_OK): return None
    paras = _extract_fulltext(r.text)
    return _paras_to_pdf(paras, rec, pdf_dir) if paras else None

def cmd_download(args):
    out = args.out; pdf_dir = os.path.join(out, "pdf"); os.makedirs(pdf_dir, exist_ok=True)
    recs = load_corpus(out)["records"]
    rfp = os.path.join(out, "download_results.json")
    prev = json.load(open(rfp, encoding="utf-8")) if os.path.exists(rfp) else {}
    todo = [r for r in recs if not prev.get(key_of(r) or "", {}).get("ok")]
    limit = getattr(args, "limit", 0)
    if limit: todo = todo[:limit]; print(f"[测试模式] 仅处理前 {limit} 篇")
    warn = ""
    if not _HAS_BS4: warn += " (bs4 缺失→网页通道关闭)"
    if not _HAS_PDF: warn += " (pymupdf 缺失→网页通道关闭)"
    cn = sum(1 for r in todo if has_chinese(r.get("title", "")))
    print(f"待下载 {len(todo)} 篇（其中中文标题 {cn} 篇，多需机构订阅）| 通道: EPMC-render / OA直链 / 网页全文转PDF{warn}")

    def save(content, rec):
        base = safe_name(rec["title"]); fn = base + ".pdf"; i = 2
        while os.path.exists(os.path.join(pdf_dir, fn)):
            fn = f"{base}_{i}.pdf"; i += 1
        fp = os.path.join(pdf_dir, fn); open(fp, "wb").write(content); return fp

    def one(rec):
        pmid, pmcid = rec.get("pmid", ""), rec.get("pmcid", "")
        if pmcid:
            c = _fetch(f"https://europepmc.org/articles/{pmcid}?pdf=render",
                       referer=f"https://europepmc.org/article/MED/{pmid}" if pmid else None)
            if c: return {"ok": True, "file": save(c, rec), "via": "EPMC-render"}
        for src, u in _oa_pdf_urls(rec)[:6]:
            c = _fetch(u, referer=f"https://doi.org/{rec.get('doi','')}")
            if c: return {"ok": True, "file": save(c, rec), "via": f"OA:{src}"}
        fp = _try_html_fulltext(rec, pdf_dir)
        if fp: return {"ok": True, "file": fp, "via": "WebHTML->PDF"}
        return {"ok": False, "via": "", "reason": "no-oa-fulltext"}

    from concurrent.futures import ThreadPoolExecutor, as_completed
    todo.sort(key=lambda r: (0 if r.get("in_epmc") == "Y" else 1, 0 if r.get("pmcid") else 1, -r.get("cited", 0)))
    res, done, okn = {}, 0, 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(one, r): r for r in todo}
        for fu in as_completed(futs):
            r = futs[fu]; k = key_of(r) or r["title"]
            try: res[k] = fu.result()
            except Exception as e: res[k] = {"ok": False, "reason": f"err:{type(e).__name__}"}
            done += 1
            if res[k].get("ok"):
                okn += 1
                print(f"  [{done}/{len(todo)}] OK via {res[k].get('via'):20s} | {r['title'][:58]}")
            elif done % 50 == 0:
                print(f"  ...进度 {done}/{len(todo)} 新增成功 {okn}")
    prev.update(res)
    json.dump(prev, open(rfp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n下载完成: 本轮新增 {okn}；累计成功 {sum(1 for v in prev.values() if v.get('ok'))}/{len(recs)} → {pdf_dir}")

def cmd_rename(args):
    out = args.out; pdf = os.path.join(out, "pdf")
    rfp = os.path.join(out, "download_results.json")
    if not os.path.exists(rfp): sys.exit("[错误] 找不到 download_results.json")
    dl = json.load(open(rfp, encoding="utf-8"))
    corpus = {key_of(r): r for r in load_corpus(out)["records"] if key_of(r)}
    used, n = set(), 0
    for k, d in dl.items():
        if not d.get("ok") or not d.get("file") or not os.path.exists(d["file"]): continue
        rec = corpus.get(k)
        title = safe_name(rec["title"]) if rec else os.path.splitext(os.path.basename(d["file"]))[0]
        name = title + ".pdf"; i = 2
        while name.lower() in used or (os.path.exists(os.path.join(pdf, name)) and os.path.join(pdf, name) != d["file"]):
            name = f"{title}_{i}.pdf"; i += 1
        used.add(name.lower())
        new = os.path.join(pdf, name)
        if os.path.abspath(d["file"]) != os.path.abspath(new):
            try: os.replace(d["file"], new); n += 1
            except Exception: continue
        d["file"] = new
    json.dump(dl, open(rfp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"重命名 {n} 个；PDF 总数 {len([f for f in os.listdir(pdf) if f.lower().endswith('.pdf')]) if os.path.isdir(pdf) else 0}")

def cmd_excel(args):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    out = args.out; meta = load_corpus(out); corpus = meta["records"]
    rfp = os.path.join(out, "download_results.json")
    dl = json.load(open(rfp, encoding="utf-8")) if os.path.exists(rfp) else {}
    rows = []
    for i, r in enumerate(corpus, 1):
        k = key_of(r); d = dl.get(k, {}); ok = bool(d.get("ok"))
        link = ("https://doi.org/" + r["doi"]) if r.get("doi") else (("https://pubmed.ncbi.nlm.nih.gov/" + str(r["pmid"]) + "/") if r.get("pmid") else r.get("url", ""))
        areas = [a for a in r.get("areas", []) if not a.startswith("[")] or r.get("areas", [])
        pt = (r.get("pubtypes") or "").lower()
        typ = ("综述" if "review" in pt else "RCT" if "randomized" in pt or "randomised" in pt else "指南/共识"
               if ("guideline" in pt or "consensus" in pt) else "Meta分析" if "meta-analysis" in pt else "研究")
        rows.append({"序号": i, "标题": r["title"],
                     "语种": "中文" if (r.get("lang") == "zh" or has_chinese(r.get("title", ""))) else "英文",
                     "期刊": r["journal"], "年份": r["year"], "类型": typ, "被引": r.get("cited", 0),
                     "DOI": r.get("doi", ""), "PMID": r.get("pmid", ""), "PMCID": r.get("pmcid", ""),
                     "学科主题": " / ".join(areas[:2]), "OA": r.get("is_oa", ""),
                     "来源库": r.get("source_db", ""), "期刊等级": ("中文核心" if is_cn_core(r.get("journal")) else ""),
                     "全文链接": link, "下载状态": "已下载" if ok else "待下载",
                     "获取方式": d.get("via", "") if ok else "",
                     "本地文件": os.path.basename(d.get("file", "")) if ok else ""})
    rows.sort(key=lambda x: (0 if x["下载状态"] == "已下载" else 1, -x["被引"]))
    W = {"序号": 6, "标题": 80, "语种": 7, "期刊": 34, "年份": 7, "类型": 10, "被引": 8, "DOI": 33,
         "PMID": 11, "PMCID": 14, "学科主题": 26, "OA": 6, "来源库": 14, "期刊等级": 10,
         "全文链接": 40, "下载状态": 10, "获取方式": 16, "本地文件": 44}
    HF = PatternFill("solid", fgColor="1F4E79"); HFONT = Font(bold=True, color="FFFFFF", size=10)
    TH = Side(style="thin", color="BFBFBF"); BD = Border(left=TH, right=TH, top=TH, bottom=TH)
    def sheet(ws, data):
        cols = list(W.keys()); ws.append(cols)
        for c in range(1, len(cols) + 1):
            cell = ws.cell(1, c); cell.fill = HF; cell.font = HFONT; cell.border = BD
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ws.column_dimensions[get_column_letter(c)].width = W[cols[c - 1]]
        for row in data: ws.append([row[c] for c in cols])
        for r in range(2, ws.max_row + 1):
            for c in range(1, len(cols) + 1):
                cell = ws.cell(r, c); cell.font = Font(size=10); cell.border = BD
                cell.alignment = Alignment(vertical="top", wrap_text=(cols[c - 1] in ("标题", "学科主题", "期刊")))
        ws.freeze_panes = "A2"; ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{ws.max_row}"
    wb = Workbook(); ws1 = wb.active; ws1.title = "全部文献库"; sheet(ws1, rows)
    failed = [r for r in rows if r["下载状态"] != "已下载"]
    sheet(wb.create_sheet("待自行下载"), failed)
    cnrows = [r for r in rows if r["语种"] == "中文"]
    sheet(wb.create_sheet("中文文献"), cnrows)
    ws3 = wb.create_sheet("说明")
    yrs = meta.get("years", args.years)
    for r in [["文献库说明"], [""], ["检索方向", str(meta.get("topic", ""))],
              ["检索来源", "英文: Europe PMC（PubMed 收录）/ 中文: OpenAlex + 核心期刊白名单 + 手工导入"],
              ["时间范围", yrs], ["文献总量", len(rows)],
              ["其中中文", len(cnrows)], ["已下载全文", len(rows) - len(failed)], ["待自行下载", len(failed)],
              ["获取通道", "EPMC-render / Semantic Scholar / Unpaywall / OpenAlex / 网页全文转PDF"],
              [""], ["说明", "「待自行下载」多为订阅制文献（含多数中文核心刊），附 DOI/链接，可通过机构订阅、知网/万方或文献传递获取。"],
              ["中文核心刊界定", "《中文核心期刊要目总览》2023年版医药卫生类 + 中华医学会系列期刊"],
              ["生成时间", time.strftime("%Y-%m-%d %H:%M")]]:
        ws3.append(r)
    ws3.column_dimensions["A"].width = 16; ws3.column_dimensions["B"].width = 100
    ws3["A1"].font = Font(bold=True, size=13)
    fp = os.path.join(out, "文献库清单.xlsx"); wb.save(fp)
    print(f"Excel: {fp} (全部 {len(rows)} / 中文 {len(cnrows)} / 已下载 {len(rows)-len(failed)} / 待下载 {len(failed)})")

def cmd_stats(args):
    out = args.out; corpus = load_corpus(out)["records"]
    yc = collections.Counter(r["year"] for r in corpus)
    jc = collections.Counter(r["journal"] for r in corpus if r["journal"])
    ac = collections.Counter()
    for r in corpus:
        for a in r.get("areas", []):
            if not a.startswith("["): ac[a] += 1
    cn = sum(1 for r in corpus if has_chinese(r.get("title", "")))
    print(f"总量 {len(corpus)} | 中文标题 {cn} | 年度 {dict(sorted(yc.items()))}")
    print("\n期刊 Top 20:"); [print(f"  {c:>4d} {j}") for j, c in jc.most_common(20)]
    print("\n子领域覆盖:"); [print(f"  {c:>4d} {a}") for a, c in ac.most_common()]
    print("\n高被引 Top 25:")
    for i, r in enumerate(sorted(corpus, key=lambda x: -x.get("cited", 0))[:25], 1):
        print(f"  {i:>2d}. [{r['cited']:>5d}] {r['journal'][:34]:36s} {r['year']} | {r['title'][:92]}")

# ============================ guide（中文库检索式） ============================
CN_DBS = {
    "CNKI 知网": {
        "url": "https://kns.cnki.net/kns8s/AdvSearch",
        "steps": ["打开知网高级检索 → 选择「学术期刊」库",
                  "在「主题」或「篇关摘」字段粘贴下方检索式（支持 AND/OR/NOT）",
                  "来源类别勾选：北大核心 / CSSCI / CSCD / AMI",
                  "按「被引」排序，导出：勾选文献 → 导出与分析 → 导出文献 → 选「参考文献」或「Excel」/「Refworks」"],
        "tip": "知网导出格式：TXT(参考文献) / Excel / RefWorks / EndNote 均可被 import 解析"},
    "万方数据": {
        "url": "https://s.wanfangdata.com.cn/paper",
        "steps": ["进入万方「学术期刊」检索",
                  "粘贴检索式到高级检索框",
                  "左侧「期刊收录」勾选：北大核心 / CSCD / 统计源",
                  "按被引排序 → 导出 → 选「NoteExpress/EndNote/RefWorks/Excel」"],
        "tip": "万方导出 Zotero/EndNote 格式最稳妥"},
    "SinoMed 中国生物医学文献服务系统": {
        "url": "https://www.sinomed.ac.cn/",
        "steps": ["机构 IP 或登录后进入「高级检索」/「基本检索」",
                  "粘贴中文主题词（SinoMed 支持主题词+副主题词）",
                  "限定：核心期刊 / 中华医学会系列 / 出版年",
                  "导出：勾选 → 输出 → 选「题录」或「参考文献」格式"],
        "tip": "SinoMed 是中文医学最权威的检索源，需机构账号"},
}

def cmd_guide(args):
    out = args.out; os.makedirs(out, exist_ok=True)
    meta = None
    if os.path.exists(os.path.join(out, "corpus_raw.json")):
        try: meta = load_corpus(out)
        except Exception: meta = None
    topics = parse_topics(args) if (args.topic or args.topics) else {}
    if not topics and meta:
        topics = {"from_corpus": str(meta.get("topic", ""))}
    kws = derive_keywords(topics) if topics else []
    cn_kw = [k for k in kws if has_chinese(k)] or [k for k in kws[:6]]

    lines = []
    lines.append("# 中文文献检索指引（CNKI / 万方 / SinoMed）\n")
    lines.append("> OpenAlex 对中文核心刊覆盖有限，**中文核心文献建议用下面的检索式在中文库中检索后导出，再用 `import` 命令合并进文献库**。\n")
    if cn_kw:
        expr = " OR ".join(cn_kw[:8])
        lines.append(f"## 本次主题关键词\n\n{ ' / '.join(cn_kw[:12]) }\n")
        lines.append(f"## 通用检索式（可直接粘贴）\n\n```\n主题 = ({expr})\n```\n")
    for db, d in CN_DBS.items():
        lines.append(f"## {db}\n\n- 入口：{d['url']}")
        for i, s in enumerate(d["steps"], 1):
            lines.append(f"- 步骤{i}：{s}")
        lines.append(f"- 💡 {d['tip']}\n")
    lines.append("## 导出后如何入库\n")
    lines.append("```bash\npython pipeline.py import --out <工作目录> --file <导出的文件>\n```")
    lines.append("支持格式：知网 TXT/Excel、RefWorks、EndNote RIS、纯 CSV（需含标题列）。\n")
    lines.append("## 中文核心期刊界定\n")
    lines.append(f"内置白名单 **{len(CN_CORE)} 本**：《中文核心期刊要目总览》2023年版 医药卫生类 + 中华医学会系列期刊。")
    lines.append("白名单文件：`references/cn_journals.json`（可按学科增删）。\n")

    fp = os.path.join(out, "中文文献检索指引.md")
    open(fp, "w", encoding="utf-8").write("\n".join(lines))
    print(f"已生成: {fp}\n")
    print("\n".join(lines[:40]))

# ============================ import（导入中文库导出文件） ============================
def _parse_refworks(txt):
    recs, cur = [], {}
    for line in txt.splitlines():
        line = line.strip()
        if not line: continue
        m = re.match(r"^([A-Z][A-Z0-9])\s*-\s*(.*)$", line)
        if not m: continue
        tag, val = m.group(1), m.group(2).strip()
        if tag in ("RT", "SR") and cur.get("title") and tag == "RT":
            recs.append(cur); cur = {}
        if tag == "TI": cur["title"] = val
        elif tag == "T1" and not cur.get("title"): cur["title"] = val
        elif tag == "JO": cur["journal"] = val
        elif tag == "JF" and not cur.get("journal"): cur["journal"] = val
        elif tag == "PY": cur["year"] = re.sub(r"[^0-9]", "", val)[:4]
        elif tag == "AU": cur.setdefault("authors", []).append(val)
        elif tag == "DO": cur["doi"] = val
        elif tag == "AB": cur["abstract"] = val[:1500]
        elif tag == "UR": cur["url"] = val
    if cur.get("title"): recs.append(cur)
    return recs

def _parse_ris(txt):
    recs, cur = [], {}
    for line in txt.splitlines():
        line = line.rstrip()
        m = re.match(r"^([A-Z][A-Z0-9])\s{2}-\s?(.*)$", line)
        if not m: continue
        tag, val = m.group(1), m.group(2).strip()
        if tag == "TY":
            if cur.get("title"): recs.append(cur)
            cur = {}
        elif tag == "TI": cur["title"] = val
        elif tag == "T1" and not cur.get("title"): cur["title"] = val
        elif tag == "JO": cur["journal"] = val
        elif tag == "JF" and not cur.get("journal"): cur["journal"] = val
        elif tag == "PY": cur["year"] = re.sub(r"[^0-9]", "", val)[:4]
        elif tag == "AU": cur.setdefault("authors", []).append(val)
        elif tag == "DO": cur["doi"] = val
        elif tag == "AB": cur["abstract"] = val[:1500]
        elif tag == "UR": cur["url"] = val
    if cur.get("title"): recs.append(cur)
    return recs

def _parse_cnki_txt(txt):
    """知网「参考文献」导出格式：每条形如
    [1]作者.题名[J].刊名,年,卷(期):页码.
    或 题名 单独成行。尽量宽松解析。
    """
    recs = []
    blocks = re.split(r"\n(?=\[\d+\])", txt)
    for b in blocks:
        b = b.strip()
        if not b: continue
        b = re.sub(r"^\[\d+\]\s*", "", b)
        m = re.search(r"([^\.。]+?)\[J\]\s*[\.。]?\s*([^,，\.。]+)[,，]\s*(\d{4})", b)
        if m:
            authors, journal, year = m.group(1).strip(), m.group(2).strip(), m.group(3)
            title = b.split("[J]")[0].split(".", 1)[-1] if "[J]" in b else b[:120]
            title = re.sub(r"^[^\.。]*[\.。]", "", b.split("[J]")[0]).strip()
            recs.append({"title": title or b[:100], "journal": journal, "year": year, "authors": [authors]})
    return recs

def _parse_csv_any(fp):
    recs = []
    for enc in ("utf-8-sig", "gbk", "utf-8"):
        try:
            with open(fp, encoding=enc, newline="") as f:
                rd = list(csv.DictReader(f))
            if rd: break
        except Exception:
            rd = []
    else:
        return []
    def pick(row, *names):
        for k in row:
            if any(n in k for n in names):
                return (row[k] or "").strip()
        return ""
    for row in rd:
        t = pick(row, "题名", "标题", "篇名", "Title", "title", "题录")
        if not t: continue
        recs.append({"title": t, "journal": pick(row, "刊名", "期刊", "来源", "Journal", "journal"),
                     "year": re.sub(r"[^0-9]", "", pick(row, "年", "Year", "year"))[:4],
                     "authors": [pick(row, "作者", "Author", "author")],
                     "doi": pick(row, "DOI", "doi"), "cited": 0,
                     "abstract": pick(row, "摘要", "Abstract", "abstract")[:1500]})
    return recs

def cmd_import(args):
    out = args.out; fp = args.file
    if not os.path.exists(fp):
        sys.exit(f"[错误] 文件不存在: {fp}")
    raw = open(fp, encoding="utf-8", errors="ignore").read()
    if not raw.strip():
        try: raw = open(fp, encoding="gbk", errors="ignore").read()
        except Exception: pass
    name = os.path.basename(fp).lower()
    recs = []
    if fp.lower().endswith((".xlsx", ".xls")):
        try:
            from openpyxl import load_workbook
            wb = load_workbook(fp, read_only=True); ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            if rows:
                hdr = [str(x or "") for x in rows[0]]
                idx = {}
                for i, h in enumerate(hdr):
                    for key, pat in (("title", ("题名", "标题", "篇名", "Title")), ("journal", ("刊名", "期刊", "来源", "Journal")),
                                     ("year", ("年", "Year")), ("authors", ("作者", "Author")), ("doi", ("DOI", "doi")),
                                     ("cited", ("被引", "引证", "Cited")), ("abstract", ("摘要", "Abstract"))):
                        if key not in idx and any(p in h for p in pat):
                            idx[key] = i
                for r in rows[1:]:
                    t = str(r[idx["title"]] or "").strip() if "title" in idx else ""
                    if not t: continue
                    recs.append({"title": t,
                                 "journal": str(r[idx["journal"]] or "").strip() if "journal" in idx else "",
                                 "year": re.sub(r"[^0-9]", "", str(r[idx["year"]] or ""))[:4] if "year" in idx else "",
                                 "authors": [str(r[idx["authors"]] or "")] if "authors" in idx else [],
                                 "doi": str(r[idx["doi"]] or "").strip() if "doi" in idx else "",
                                 "cited": int(re.sub(r"[^0-9]", "", str(r[idx["cited"]] or "0")) or 0) if "cited" in idx else 0,
                                 "abstract": str(r[idx["abstract"]] or "")[:1500] if "abstract" in idx else ""})
        except Exception as e:
            sys.exit(f"[错误] Excel 解析失败: {e}")
    elif fp.lower().endswith(".ris") or re.search(r"^TY\s{2}-", raw, re.M):
        recs = _parse_ris(raw)
    elif re.search(r"^RT\s*-\s*(JOUR|Journal)", raw, re.M | re.I):
        recs = _parse_refworks(raw)
    elif "题名" in raw or "刊名" in raw or "作者" in raw:
        recs = _parse_csv_any(fp) or _parse_cnki_txt(raw)
    else:
        recs = _parse_cnki_txt(raw) or _parse_csv_any(fp)

    if not recs:
        sys.exit("[错误] 未能从该文件解析出文献记录。支持：知网 TXT/Excel、RefWorks、EndNote RIS、CSV。")

    os.makedirs(out, exist_ok=True)
    cfp = os.path.join(out, "corpus_raw.json")
    if os.path.exists(cfp):
        data = load_corpus(out)
        corpus = {key_of(r): r for r in data["records"] if key_of(r)}
    else:
        data = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "topic": "import", "years": "", "keywords": []}
        corpus = {}
    added = 0
    for r in recs:
        t = (r.get("title") or "").strip().rstrip(".")
        if not t: continue
        x = {"pmid": "", "pmcid": "", "doi": (r.get("doi") or "").strip(),
             "title": t, "journal": (r.get("journal") or "").strip(),
             "year": str(r.get("year") or ""), "authors": "; ".join(r.get("authors") or []) if isinstance(r.get("authors"), list) else str(r.get("authors") or ""),
             "cited": int(r.get("cited") or 0), "is_oa": "N", "has_pdf": "N", "in_epmc": "N",
             "pubtypes": "", "abstract": r.get("abstract") or "", "source": "import",
             "lang": "zh" if has_chinese(t) else "en", "source_db": args.db or "手工导入",
             "url": r.get("url", ""), "areas": ["[导入] " + (args.db or "中文库")]}
        k = key_of(x)
        if k and k not in corpus:
            corpus[k] = x; added += 1
    data["records"] = list(corpus.values()); data["total"] = len(corpus)
    save_corpus(out, data)
    print(f"导入完成: 解析 {len(recs)} 条，新增 {added} 条，库内合计 {len(corpus)} 篇 → {cfp}")

def main():
    p = argparse.ArgumentParser(description="Biomed Literature Pipeline — 全生物医学文献调研流水线")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="检索文献（英文 Europe PMC / 中文 OpenAlex）")
    s.add_argument("--out", required=True)
    s.add_argument("--topic", default="", help="检索方向：中文或英文关键词，或布尔表达式")
    s.add_argument("--topics", default="", help="JSON 主题表 {主题名: 检索式}")
    s.add_argument("--keywords", default="", help="追加相关性关键词，分号分隔")
    s.add_argument("--years", default="2021-2026")
    s.add_argument("--lang", default="both", choices=["both", "en", "en_only", "cn", "cn_only"],
                   help="语种范围；en/cn=允许对方语种混入, en_only/cn_only=严格过滤")
    s.add_argument("--journals", default="", help="指定期刊列表（分号分隔），做定向期刊检索")
    s.add_argument("--per-page", dest="per_page", type=int, default=25, help="每个主题/路径的单次抓取量")
    s.add_argument("--cn-query", dest="cn_query", default="",
                   help="中文轨道使用的英文检索式（中文刊在 Europe PMC 的题录为英文）；缺省则由英文关键词自动组合")
    s.add_argument("--cn-all", dest="cn_all", action="store_true", help="中文轨道不过滤核心刊（默认只保留核心刊）")
    s.set_defaults(func=cmd_search)

    d = sub.add_parser("download", help="下载全文")
    d.add_argument("--out", required=True)
    d.add_argument("--workers", type=int, default=3); d.add_argument("--limit", type=int, default=0)
    d.set_defaults(func=cmd_download)

    r = sub.add_parser("rename", help="按标题重命名 PDF"); r.add_argument("--out", required=True); r.set_defaults(func=cmd_rename)

    e = sub.add_parser("excel", help="生成 Excel 清单")
    e.add_argument("--out", required=True); e.add_argument("--years", default=""); e.set_defaults(func=cmd_excel)

    t = sub.add_parser("stats", help="库结构统计"); t.add_argument("--out", required=True); t.set_defaults(func=cmd_stats)

    g = sub.add_parser("guide", help="生成中文库检索指引（CNKI/万方/SinoMed）")
    g.add_argument("--out", required=True); g.add_argument("--topic", default=""); g.add_argument("--topics", default="")
    g.set_defaults(func=cmd_guide)

    m = sub.add_parser("import", help="导入中文库导出文件")
    m.add_argument("--out", required=True); m.add_argument("--file", required=True)
    m.add_argument("--db", default="", help="来源库名，如 CNKI / 万方 / SinoMed")
    m.set_defaults(func=cmd_import)

    args = p.parse_args()
    # 解析 --journals 为列表
    if hasattr(args, "journals"):
        args.journals_list = [x.strip() for x in args.journals.split(";") if x.strip()]
    args.func(args)

if __name__ == "__main__":
    main()
