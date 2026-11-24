"""Manuscript text extraction and consistency audit.

--extract: pdf (Flate streams + text operators), docx, xlsx, md/txt -> plain text.
           A PDF without a text layer is reported, never guessed.
--audit:   emits candidate signals only (numbers, figure/table numbering,
           citation order, sample size, terminology variants). The model decides
           what each signal means; the script never writes a verdict.
--diff:    checks a polished draft against its source and lists added numbers
           and added entities, supporting the "meaning unchanged" rule.
"""

import argparse
import re
import sys
import zipfile
import zlib
from pathlib import Path
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _shared as S  # noqa: E402

STAT_KEYS = ("OR", "HR", "RR", "AUC", "C-INDEX", "P", "SE", "MD", "SMD", "I2")
TERM_VARIANTS = [
    ("脓毒症", "脓毒血症"),
    ("随机对照试验", "随机对照实验"),
    ("心肌梗死", "心肌梗塞"),
    ("并发症", "合并症"),
    ("生存率", "存活率"),
    ("灵敏度", "敏感性"),
    ("特异度", "特异性"),
    ("质量调整生命年", "质量校正生命年"),
]


# ---------------------------------------------------------------- extraction


def extract_pdf(path):
    """Return (text, meta). Uses Flate streams plus text-showing operators."""
    data = Path(path).read_bytes()
    if b"/Encrypt" in data[:4000]:
        return None, {"reason": "PDF is encrypted", "fix": "decrypt or paste the text manually"}
    chunks = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        raw = m.group(1)
        text = None
        try:
            text = zlib.decompress(raw)
        except zlib.error:
            try:
                text = zlib.decompressobj().decompress(raw)
            except zlib.error:
                text = None
        if text is None:
            continue
        if b"Tj" in text or b"TJ" in text:
            chunks.append(text)
    if not chunks:
        return None, {
            "reason": "no decompressible text stream found",
            "fix": "the PDF has no text layer; paste the body text or use an external PDF tool",
        }
    out = []
    for blob in chunks:
        out.append(_decode_pdf_text(blob.decode("latin-1", "replace")))
    text = "\n".join(x for x in out if x.strip())
    if not text.strip():
        return None, {
            "reason": "text layer present but no glyphs could be decoded",
            "fix": "paste the body text, or convert the PDF with an external tool",
        }
    return text, {"streams": len(chunks)}


def _decode_pdf_text(s):
    pieces = []
    for m in re.finditer(r"\((?:\\.|[^\\()])*\)\s*Tj|\[(?:[^\[\]]*)\]\s*TJ", s):
        frag = m.group(0)
        for lit in re.finditer(r"\((?:\\.|[^\\()])*\)", frag):
            body = lit.group(0)[1:-1]
            body = re.sub(r"\\([()\\])", r"\1", body)
            body = re.sub(r"\\([0-7]{1,3})", lambda mm: chr(int(mm.group(1), 8)), body)
            pieces.append(body)
        if frag.endswith("Tj"):
            pieces.append(" ")
    return "".join(pieces)


def extract_docx(path):
    with zipfile.ZipFile(path) as zf:
        if "word/document.xml" not in zf.namelist():
            return None, {"reason": "no word/document.xml part", "fix": "file is not a valid docx"}
        root = ET.fromstring(zf.read("word/document.xml"))
    paras = []
    for node in root.iter():
        if node.tag.split("}")[-1] != "p":
            continue
        text = "".join(t.text or "" for t in node.iter() if t.tag.split("}")[-1] == "t")
        paras.append(text)
    return "\n".join(paras), {"paragraphs": len(paras)}


def extract_xlsx(path):
    cols, rows = S.read_table(path)
    lines = [" | ".join(cols)]
    for r in rows:
        lines.append(" | ".join(str(r.get(c, "")) for c in cols))
    return "\n".join(lines), {"rows": len(rows)}


def extract(path):
    p = Path(path)
    if not p.exists():
        S.fail("input not found: " + str(p), S.EXIT_INPUT)
    suf = p.suffix.lower()
    if suf == ".pdf":
        return extract_pdf(p)
    if suf == ".docx":
        return extract_docx(p)
    if suf in (".xlsx", ".xlsm"):
        return extract_xlsx(p)
    if suf in (".md", ".txt", ".csv"):
        return p.read_text(encoding="utf-8", errors="replace"), {"chars": p.stat().st_size}
    return None, {"reason": "unsupported extension " + suf, "fix": "convert to docx, pdf, xlsx, md or txt"}


# ---------------------------------------------------------------- audit rules


def norm(text):
    return (text or "").replace("\u3000", " ").replace("\xa0", " ")


def find_stat_pairs(text):
    hits = []
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(k) for k in STAT_KEYS) + r")\s*[=:：]\s*(-?\d+(?:\.\d+)?)",
        re.I,
    )
    for m in pattern.finditer(text):
        line = text[: m.start()].count("\n") + 1
        hits.append({"key": m.group(1).upper(), "value": float(m.group(2)), "raw": m.group(0), "line": line})
    return hits


def signal_numbers(text):
    hits = find_stat_pairs(text)
    grouped = {}
    for h in hits:
        grouped.setdefault(h["key"], []).append(h)
    out = []
    for key, items in grouped.items():
        values = sorted({i["value"] for i in items})
        if len(values) < 2:
            continue
        span = max(values) - min(values)
        decimals = min(
            len(str(i["value"]).split(".")[1]) if "." in str(i["value"]) else 0 for i in items
        )
        rounding_only = span <= 0.5 * (10 ** -decimals) + 1e-12
        out.append(
            {
                "kind": "number-conflict",
                "key": key,
                "values": values,
                "lines": [i["line"] for i in items],
                "raw": [i["raw"] for i in items],
                "confidence": "low" if rounding_only else "high",
                "note": "differences within the last reported digit may be rounding only"
                if rounding_only
                else "the same statistic is reported with different values",
            }
        )
    return out


def signal_numbering(text):
    caps = {}
    for m in re.finditer(r"(?m)^\s*(图|表)\s*([0-9]{1,2})\b", text):
        caps.setdefault(m.group(1), set()).add(int(m.group(2)))
    refs = {}
    for m in re.finditer(r"(图|表)\s*([0-9]{1,2})\b", text):
        refs.setdefault(m.group(1), set()).add(int(m.group(2)))
    out = []
    for kind, seen in refs.items():
        known = caps.get(kind, set())
        dangling = sorted(v for v in seen if known and v not in known)
        if known:
            gaps = sorted(set(range(1, max(known) + 1)) - known)
        else:
            gaps = []
        if dangling:
            out.append(
                {
                    "kind": "dangling-" + ("figure" if kind == "图" else "table"),
                    "values": dangling,
                    "note": "referenced in the body but no matching caption line was found",
                    "confidence": "high",
                }
            )
        if gaps:
            out.append(
                {
                    "kind": "numbering-gap-" + ("figure" if kind == "图" else "table"),
                    "values": gaps,
                    "note": "caption numbers skip a value",
                    "confidence": "high",
                }
            )
    return out


def signal_citations(text):
    order = []
    max_n = 0
    for m in re.finditer(r"\[([0-9,\-\s]{1,40})\]", text):
        body = m.group(1)
        for part in body.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, _, b = part.partition("-")
                if a.strip().isdigit() and b.strip().isdigit():
                    for v in range(int(a), int(b) + 1):
                        order.append(v)
                        max_n = max(max_n, v)
            elif part.isdigit():
                order.append(int(part))
                max_n = max(max_n, int(part))
    out = []
    if not order:
        return out
    first_seen = []
    for v in order:
        if v not in first_seen:
            first_seen.append(v)
    inversions = [
        (first_seen[i], first_seen[i + 1])
        for i in range(len(first_seen) - 1)
        if first_seen[i + 1] < first_seen[i]
    ]
    if inversions:
        out.append(
            {
                "kind": "citation-order",
                "values": inversions[:5],
                "note": "reference numbers do not increase in order of first appearance",
                "confidence": "high",
            }
        )
    gaps = sorted(set(range(1, max_n + 1)) - set(order))
    if gaps:
        out.append(
            {
                "kind": "citation-gap",
                "values": gaps[:10],
                "note": "some numbers are never cited in the body",
                "confidence": "medium",
            }
        )
    return out


SAMPLE_PATTERNS = (
    r"n\s*=\s*([0-9]{1,6})",
    r"共\s*([0-9]{1,6})\s*例",
    r"纳入\s*([0-9]{1,6})\s*例",
    r"([0-9]{1,6})\s*例(?:患者|受试者|病例)",
)


def signal_sample_size(text):
    found = {}
    for pat in SAMPLE_PATTERNS:
        for m in re.finditer(pat, text):
            v = int(m.group(1))
            line = text[: m.start()].count("\n") + 1
            found.setdefault(v, []).append(line)
    out = []
    if len(found) > 1:
        out.append(
            {
                "kind": "sample-size-conflict",
                "values": sorted(found.keys()),
                "lines": {str(k): v for k, v in found.items()},
                "note": "different sample sizes appear in the text; some may legitimately refer to subgroups",
                "confidence": "medium",
            }
        )
    return out


def signal_terms(text):
    out = []
    for a, b in TERM_VARIANTS:
        if a in text and b in text:
            out.append(
                {
                    "kind": "term-variant",
                    "values": [a, b],
                    "note": "two names for one concept; fix one and use it throughout",
                    "confidence": "high",
                }
            )
    expansions = {}
    for m in re.finditer(r"（([^）]{2,40})[，,]\s*([A-Za-z][A-Za-z0-9\-]{1,9})）", text):
        expansions.setdefault(m.group(2).upper(), set()).add(m.group(1))
    for abbr, names in expansions.items():
        if len(names) > 1:
            out.append(
                {
                    "kind": "abbreviation-conflict",
                    "values": [abbr] + sorted(names),
                    "note": "one abbreviation is expanded in two different ways",
                    "confidence": "high",
                }
            )
    return out


def audit(text):
    signals = []
    for fn in (signal_numbers, signal_numbering, signal_citations, signal_sample_size, signal_terms):
        signals.extend(fn(text))
    return signals


def diff_texts(source, revised):
    """Added numbers and added latin entities, for the meaning-unchanged check."""
    def numbers(t):
        return set(re.findall(r"(?<![A-Za-z0-9])[0-9]+(?:\.[0-9]+)?", t))

    def entities(t):
        return set(re.findall(r"\b[A-Z][A-Za-z\-]{2,}\b", t))

    added_nums = sorted(numbers(revised) - numbers(source))
    added_ents = sorted(entities(revised) - entities(source))
    removed_nums = sorted(numbers(source) - numbers(revised))
    return {
        "added_numbers": added_nums,
        "removed_numbers": removed_nums,
        "added_entities": added_ents,
        "note": "every added number or entity must be traceable to the source; otherwise revert it",
    }


def to_markdown(signals, meta):
    lines = [
        "# 稿件体检（候选信号）",
        "",
        "> 本表只列**候选信号**，不下结论。每条需人工复核后再决定是否处理；",
        "> 信号可能由舍入、亚组、排版等原因造成。",
        "",
        "| # | 类别 | 取值 | 位置 | 置信 | 说明 |",
        "|---|---|---|---|---|---|",
    ]
    for i, s in enumerate(signals, 1):
        lines.append(
            "| {} | {} | {} | {} | {} | {} |".format(
                i,
                s.get("kind", ""),
                s.get("values", ""),
                s.get("lines", ""),
                s.get("confidence", ""),
                s.get("note", ""),
            )
        )
    if not signals:
        lines.append("| - | 未发现候选信号 | - | - | - | 仍需人工通读 |")
    lines.append("")
    lines.append("检测项：数字一致性、图表编号、引文顺序、样本量一致性、术语变体。")
    lines.append("未执行项：图像复用与拼接检测（需图像工具）、逐条引文真伪核验（需联网）。")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- selftest


CLEAN = """资料与方法
本研究为回顾性队列研究，纳入 40 例脓毒症患者（sepsis, SEP）。
统计采用 logistic 回归，OR=1.82，P=0.031。见表 1 与图 1。
结果
40 例患者中 12 例死亡，占 30.0%。
"""

DIRTY = """资料与方法
本研究纳入 40 例脓毒症患者，另设 46 例脓毒血症患者作对照。
统计采用 logistic 回归，OR=1.82，P=0.031，见表 3 与图 1。
结果
共 46 例患者中 12 例死亡，OR=1.79。
表 1 基线特征
图 1 生存曲线
讨论
既往研究[3]与本研究一致，另见[1]与[2]。
"""


def selftest(argv):
    tmp = S.tmpdir()
    checks = []
    clean_signals = audit(CLEAN)
    checks.append(S.check("clean_text_no_signal", not clean_signals, str([s["kind"] for s in clean_signals])))
    dirty = audit(DIRTY)
    kinds = {s["kind"] for s in dirty}
    checks.append(S.check("detects_number_conflict", "number-conflict" in kinds, str(sorted(kinds))))
    checks.append(S.check("detects_dangling_table", "dangling-table" in kinds, str(sorted(kinds))))
    checks.append(S.check("detects_sample_conflict", "sample-size-conflict" in kinds, str(sorted(kinds))))
    checks.append(S.check("detects_term_variant", "term-variant" in kinds, str(sorted(kinds))))
    checks.append(S.check("detects_citation_order", "citation-order" in kinds, str(sorted(kinds))))
    md = to_markdown(dirty, {})
    checks.append(S.check("markdown_disclaimer", "不下结论" in md and "未执行项" in md, "disclaimer present"))
    d = diff_texts(CLEAN, CLEAN + "新增 OR=2.10，另加 7 例。")
    checks.append(S.check("diff_added_numbers", "2.10" in d["added_numbers"] and "7" in d["added_numbers"], str(d["added_numbers"])))
    d2 = diff_texts(CLEAN, CLEAN)
    checks.append(S.check("diff_identical_empty", not d2["added_numbers"] and not d2["added_entities"], "empty"))
    txt = tmp / "draft.md"
    txt.write_text(DIRTY, encoding="utf-8")
    text, meta = extract(txt)
    checks.append(S.check("extract_md", "logistic" in text and meta.get("chars"), "chars"))
    docx_path = _make_docx(tmp / "draft.docx", ["资料与方法", "OR=1.82", "见表 3"])
    text2, meta2 = extract(docx_path)
    checks.append(S.check("extract_docx", "OR=1.82" in text2 and meta2.get("paragraphs") >= 3, str(meta2)))
    bad = tmp / "bad.pdf"
    bad.write_bytes(b"%PDF-1.4\n1 0 obj<<>>stream\nnot-compressed-data\nendstream\nendobj\n%%EOF")
    text3, meta3 = extract_pdf(bad)
    checks.append(S.check("pdf_without_text_layer_reported", text3 is None and "reason" in meta3, meta3.get("reason", "")[:60]))
    out = tmp / "audit"
    S.write_json(out / "audit.json", {"signals": dirty})
    (out / "audit.md").write_text(to_markdown(dirty, {}), encoding="utf-8")
    first = (out / "audit.json").read_bytes()
    S.write_json(out / "audit.json", {"signals": dirty})
    checks.append(S.check("audit_json_idempotent", first == (out / "audit.json").read_bytes(), "byte identical"))
    failed = [c for c in checks if c["status"] != "pass"]
    for c in checks:
        print("  [{}] {} {}".format(c["status"], c["name"], c["reason"]))
    S.log_run("manuscript_audit.py", argv, checks, [], log_path=tmp / "logs" / "run.jsonl")
    print("selftest: {} checks, {} failed".format(len(checks), len(failed)))
    return S.EXIT_OK if not failed else S.EXIT_ASSERT


def _make_docx(path, paragraphs):
    import office_writer as OW

    return OW.write_docx(
        path, {"kind": "docx", "blocks": [{"type": "p", "text": t} for t in paragraphs]}
    )


def fixtures(argv):
    tmp = S.tmpdir()
    checks = []
    p = tmp / "shuffled.md"
    p.write_text("讨论[5]与[2]一致，另见[1]。\n", encoding="utf-8")
    sig = audit(p.read_text(encoding="utf-8"))
    kinds = {s["kind"] for s in sig}
    checks.append(S.check("shuffled_citations_detected", "citation-order" in kinds, str(sorted(kinds))))
    p2 = tmp / "gap.md"
    p2.write_text("正文见图 1 与图 3。\n图 1 曲线\n图 2 箱线\n", encoding="utf-8")
    sig2 = audit(p2.read_text(encoding="utf-8"))
    kinds2 = {s["kind"] for s in sig2}
    checks.append(S.check("caption_gap_or_dangling", bool(kinds2 & {"numbering-gap-figure", "dangling-figure"}), str(sorted(kinds2))))
    code = 0
    try:
        extract(tmp / "absent.pdf")
    except SystemExit as exc:
        code = int(exc.code or 0)
    checks.append(S.check("missing_file_exit2", code == S.EXIT_INPUT, "exit " + str(code)))
    weird = tmp / "weird.bin"
    weird.write_bytes(b"\x00\x01\x02")
    text, meta = extract(weird)
    checks.append(S.check("unsupported_reported", text is None and "reason" in meta, meta.get("reason", "")))
    empty = tmp / "empty.md"
    empty.write_text("", encoding="utf-8")
    checks.append(S.check("empty_text_no_signal", audit("") == [], "0 signals"))
    failed = [c for c in checks if c["status"] != "pass"]
    for c in checks:
        print("  [{}] {} {}".format(c["status"], c["name"], c["reason"]))
    S.log_run("manuscript_audit.py", argv, checks, [], log_path=tmp / "logs" / "run.jsonl")
    print("fixtures: {} checks, {} failed".format(len(checks), len(failed)))
    return S.EXIT_OK if not failed else S.EXIT_ASSERT


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(
        description="manuscript extraction and consistency audit; every finding is a candidate signal, not a verdict.",
        epilog="""\
usage:
  --extract draft.docx   -> audit/<stem>.txt          (docx / xlsx / pdf / md / txt)
  --audit   draft.docx   -> audit/audit.json + audit/audit.md
  --diff    old.md new.md -> audit/diff.json          (added numbers and entities)

Signals: number-conflict, dangling-figure, dangling-table, numbering-gap-*,
         citation-order, citation-gap, sample-size-conflict, term-variant,
         abbreviation-conflict.
Not executed here: image reuse / splicing detection (needs image tooling),
                   per-reference authenticity (needs network).
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--extract")
    ap.add_argument("--audit")
    ap.add_argument("--diff", nargs=2, metavar=("SOURCE", "REVISED"))
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--log")
    ns = ap.parse_args(argv)

    info = S.probe()
    if ns.probe:
        print(S.probe_line(info))
        return S.EXIT_OK
    if ns.selftest:
        return selftest(argv)
    if ns.fixtures:
        return fixtures(argv)

    if ns.extract:
        text, meta = extract(ns.extract)
        if text is None:
            print("未提取到文本层：{}".format(meta.get("reason", "")))
            print("补救：① 直接粘贴正文；② 若已安装外部 PDF 工具技能则改用之。本脚本不做 OCR、不猜测内容。")
            S.log_run(
                "manuscript_audit.py",
                argv,
                [S.skip("extract", meta.get("reason", "no text layer"))],
                [],
                degraded=[{"cap": "pdf-text", "reason": meta.get("reason", ""), "fix": meta.get("fix", "")}],
                log_path=ns.log,
            )
            return S.EXIT_DEPENDENCY
        out = S.out_dir(ns.out)
        target = out / "audit" / (Path(ns.extract).stem + ".txt")
        S.ensure(target)
        target.write_text(text, encoding="utf-8")
        S.log_run("manuscript_audit.py", argv, [S.check("extract", True, str(meta))], [target], log_path=ns.log)
        print("wrote {} ({} chars)".format(target, len(text)))
        return S.EXIT_OK

    if ns.audit:
        text, meta = extract(ns.audit)
        if text is None:
            print("未提取到文本层：{}".format(meta.get("reason", "")))
            return S.EXIT_DEPENDENCY
        signals = audit(text)
        out = S.out_dir(ns.out)
        S.write_json(out / "audit" / "audit.json", {"signals": signals, "source_meta": meta})
        md = to_markdown(signals, meta)
        S.ensure(out / "audit" / "audit.md")
        (out / "audit" / "audit.md").write_text(md, encoding="utf-8")
        S.log_run(
            "manuscript_audit.py",
            argv,
            [S.check("audit", True, "{} signal(s)".format(len(signals)))],
            [out / "audit" / "audit.json", out / "audit" / "audit.md"],
            log_path=ns.log,
        )
        print("wrote audit/audit.json and audit/audit.md ({} candidate signal(s))".format(len(signals)))
        for s in signals:
            print("  - {}: {}".format(s.get("kind"), s.get("values")))
        return S.EXIT_OK

    if ns.diff:
        src, _meta = extract(ns.diff[0])
        rev, _meta2 = extract(ns.diff[1])
        if src is None or rev is None:
            print("diff needs two readable texts")
            return S.EXIT_DEPENDENCY
        payload = diff_texts(src, rev)
        out = S.out_dir(ns.out)
        S.write_json(out / "audit" / "diff.json", payload)
        print("added numbers: {}".format(payload["added_numbers"][:20]))
        print("added entities: {}".format(payload["added_entities"][:20]))
        S.log_run("manuscript_audit.py", argv, [S.check("diff", True, "")], [out / "audit" / "diff.json"], log_path=ns.log)
        return S.EXIT_OK

    S.fail("one of --extract / --audit / --diff is required", S.EXIT_INPUT)
    return S.EXIT_INPUT


if __name__ == "__main__":
    sys.exit(main())
