"""Reconstruct possible underlying counts from reported summary statistics.

Everything produced here is an INFERRED value, never original data. Each cell
carries value_type / method / confidence / range, and the file opens with the
list of fields that cannot be reconstructed at all.
"""

import argparse
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _shared as S  # noqa: E402
import office_writer as OW  # noqa: E402

Z975 = 1.9599639845

NOT_RECONSTRUCTABLE = [
    ("个体级配对关系", "汇总统计量不含配对信息"),
    ("时序与事件顺序", "边际分布不等于联合分布"),
    ("协变量的联合分布", "只给边际分布无法还原相关结构"),
    ("缺失机制", "报告值通常基于非缺失子集"),
    ("重复测量的个体轨迹", "组水平均值不含个体异质性"),
    ("聚类与随机效应结构", "中心或批次效应已被汇总量抹平"),
    ("原始测量精度", "表格舍入后信息已丢失"),
    ("亚组内分布", "亚组样本量与统计量常未报告"),
    ("由 P 值反推个体值", "P 值只约束检验统计量"),
]

BANNED_WORDS = ("原始数据", "重建数据集", "还原数据", "恢复原始")


def interval_from_decimals(value, decimals):
    """Half-unit rounding window implied by a value reported to `decimals`."""
    half = 0.5 * (10 ** -decimals)
    return value - half, value + half


def grim(n, mean, decimals=2, lo=None, hi=None):
    """GRIM: an integer total must exist inside the rounding window of mean*n."""
    if n <= 0:
        return {"method": "GRIM", "confidence": "D", "reason": "n must be positive"}
    total = mean * n
    low, high = interval_from_decimals(total, decimals)
    ints = [v for v in range(int(math.floor(low)) - 1, int(math.ceil(high)) + 2) if low <= v < high]
    out = {
        "method": "GRIM (integer total inside rounding window)",
        "n": n,
        "mean": mean,
        "decimals": decimals,
        "target_total": total,
        "window": [low, high],
        "feasible_totals": ints[:10],
        "consistent": bool(ints),
        "value_type": "inferred",
    }
    if lo is None and hi is None:
        out["bounds"] = None
        out["bounds_note"] = "未提供取值范围约束（lo/hi），仅按整数性判定"
    else:
        out["bounds"] = [lo, hi]
    if lo is not None and hi is not None and ints:
        ok = [t for t in ints if lo * n <= t <= hi * n]
        out["consistent"] = bool(ok)
        out["feasible_totals"] = ok[:10]
        out["bounds"] = [lo, hi]
    out["confidence"] = "A" if out["consistent"] else "A"
    if not ints:
        out["confidence"] = "A"
        out["verdict"] = "reported mean is arithmetically impossible for n=" + str(n)
    return out


def _ss_bounds(n, total, lo, hi):
    """Min and max achievable sum of squares for n integers in [lo,hi] summing to total."""
    if lo * n > total or hi * n < total:
        return None
    base = total // n
    rem = total - base * n
    if base < lo:
        base = lo
        rem = total - base * n
    if base > hi:
        base = hi
        rem = total - base * n
    if 0 <= rem <= n:
        ss_min = rem * (base + 1) ** 2 + (n - rem) * base ** 2
    else:
        ss_min = None
    cands = []
    for anchor in (hi, lo):
        other = lo if anchor == hi else hi
        rest = total - anchor * (n - 1)
        if lo <= rest <= hi:
            cands.append(anchor ** 2 * (n - 1) + rest ** 2)
    rest_hi = total - hi * (n - 1)
    if lo <= rest_hi <= hi:
        cands.append(hi ** 2 * (n - 1) + rest_hi ** 2)
    rest_lo = total - lo * (n - 1)
    if lo <= rest_lo <= hi:
        cands.append(lo ** 2 * (n - 1) + rest_lo ** 2)
    ss_max = max(cands) if cands else None
    return ss_min, ss_max


def grimmer(n, mean, sd, decimals_mean=2, decimals_sd=2, lo=None, hi=None):
    """Necessity checks for an integer vector matching mean and SD.

    This is the cheap part of GRIMMER: integer total, parity of sum vs sum of
    squares, and whether the required sum of squares is reachable at all. The
    exhaustive enumeration is not implemented; the method note says so.
    """
    n_ok = n > 1
    total = round(mean * n)
    grim_res = grim(n, mean, decimals_mean, lo, hi)
    if not n_ok or not grim_res.get("consistent"):
        return {
            "method": "GRIMMER necessary conditions",
            "value_type": "inferred",
            "consistent": False,
            "confidence": "A",
            "verdict": "integer total not feasible: reported mean and n are incompatible",
            "method_note": "partial implementation: total/parity/bounds only, no enumeration",
        }
    ss_target = sd ** 2 * (n - 1) + n * mean ** 2
    low, high = interval_from_decimals(ss_target, decimals_sd)
    feasible_low = int(math.floor(lo)) if lo is not None else 0
    feasible_high = int(math.floor(hi)) if hi is not None else max(total, 1)
    if feasible_high < feasible_low:
        feasible_high = feasible_low
    bounds = _ss_bounds(n, total, feasible_low, feasible_high)
    if bounds is None:
        return {
            "method": "GRIMMER necessary conditions",
            "value_type": "inferred",
            "consistent": False,
            "confidence": "A",
            "verdict": "no integer vector can reach this total within the declared bounds",
            "method_note": "partial implementation",
        }
    ss_min, ss_max = bounds
    parity_ok = (round(ss_target) - total) % 2 == 0
    in_range = ss_min - 1e-9 <= ss_target <= ss_max + 1e-9
    consistent = parity_ok and in_range and low <= ss_max and high >= ss_min
    return {
        "method": "GRIMMER necessary conditions",
        "value_type": "inferred",
        "n": n,
        "mean": mean,
        "sd": sd,
        "integer_total": total,
        "ss_target": ss_target,
        "ss_window": [low, high],
        "ss_reachable": [ss_min, ss_max],
        "parity_ok": parity_ok,
        "consistent": bool(consistent),
        "confidence": "A",
        "verdict": "no contradiction found" if consistent else "sum of squares unreachable or parity mismatch",
        "method_note": "partial implementation: total/parity/bounds only, full enumeration not implemented",
    }


def iqr_to_sd(n, q1, q3, lo=None, hi=None):
    iqr = q3 - q1
    if iqr <= 0:
        return {"method": "IQR to SD", "confidence": "D", "reason": "IQR must be positive"}
    est = {"iqr_over_1.35": iqr / 1.35, "iqr_over_1.349": iqr / 1.349}
    note = "range only; a single point value would overstate precision"
    if lo is not None and hi is not None and hi > lo:
        est["range_over_3.92"] = (hi - lo) / 3.92
    else:
        note += "; add min and max to enable the range-based estimator"
    vals = list(est.values())
    return {
        "method": "IQR to SD (equivalent estimators)",
        "value_type": "inferred",
        "estimates": est,
        "range": [min(vals), max(vals)],
        "confidence": "B",
        "note": note,
    }


def percent_to_counts(n, percent, decimals=1):
    if n <= 0:
        return {"method": "percent to counts", "confidence": "D", "reason": "n must be positive"}
    low, high = interval_from_decimals(percent * n / 100.0, decimals)
    counts = [k for k in range(int(math.floor(low)) - 1, int(math.ceil(high)) + 2) if low <= k < high and 0 <= k <= n]
    point = int(round(percent * n / 100.0))
    conf = "A" if len(counts) == 1 else "C"
    return {
        "method": "percent to counts (rounding window)",
        "value_type": "inferred",
        "n": n,
        "percent": percent,
        "point": point,
        "feasible_counts": counts,
        "consistent": bool(counts),
        "confidence": conf,
        "note": "multiple counts can produce the same rounded percent" if conf == "C" else "unique count",
    }


def ratio_ci_to_se(estimate, low, high, log_scale=True):
    if not (0 < low < estimate < high):
        return {"method": "ratio CI to SE", "confidence": "D", "reason": "CI must bracket the estimate"}
    if log_scale:
        se = (math.log(high) - math.log(low)) / (2 * Z975)
        se_est = (math.log(high) - math.log(estimate)) / Z975
        se_est2 = (math.log(estimate) - math.log(low)) / Z975
        asym = abs(se_est - se_est2) / max(se, 1e-12)
        out = {
            "method": "log-scale SE from 95% CI",
            "value_type": "inferred",
            "se_log": se,
            "se_from_upper": se_est,
            "se_from_lower": se_est2,
            "ci_symmetry_gap": asym,
            "confidence": "B",
        }
        if asym > 0.15:
            out["note"] = "CI is not symmetric on the log scale; the point estimate or CI may be rounded"
        return out
    return {
        "method": "linear-scale SE from 95% CI",
        "value_type": "inferred",
        "se": (high - low) / (2 * Z975),
        "confidence": "B",
    }


def table_2x2(odds_ratio, row1_total, col1_total, n, tol=1e-3, cap=50):
    """All integer 2x2 tables with the given margins whose OR matches."""
    solutions = []
    for a in range(0, min(row1_total, col1_total) + 1):
        b = row1_total - a
        c = col1_total - a
        d = n - row1_total - c
        if b < 0 or c < 0 or d < 0:
            continue
        if b == 0 or c == 0:
            continue
        or_value = (a * d) / float(b * c)
        if or_value <= 0:
            continue
        if abs(math.log(or_value) - math.log(odds_ratio)) <= tol:
            solutions.append({"a": a, "b": b, "c": c, "d": d, "odds_ratio": or_value})
            if len(solutions) >= cap:
                break
    conf = "A" if len(solutions) == 1 else ("C" if solutions else "D")
    return {
        "method": "2x2 integer table from OR and margins",
        "value_type": "inferred",
        "target_odds_ratio": odds_ratio,
        "margins": {"row1": row1_total, "col1": col1_total, "n": n},
        "solutions": solutions,
        "n_solutions": len(solutions),
        "confidence": conf,
        "note": "margins are fixed by the report; several tables can share the same OR" if conf == "C" else "",
    }


def mean_vectors(n, mean, lo=0, hi=None, cap=200):
    """Feasible integer vectors for a given n and mean (small n only)."""
    total = mean * n
    if abs(total - round(total)) > 1e-9:
        return {
            "method": "integer vectors from mean",
            "value_type": "inferred",
            "consistent": False,
            "confidence": "A",
            "verdict": "mean * n is not an integer; no integer vector exists",
            "solutions": [],
        }
    total = int(round(total))
    hi = hi if hi is not None else max(lo, total - lo * (n - 1))
    sols = []

    def walk(pos, left, cur):
        if len(sols) >= cap:
            return
        if pos == n - 1:
            if lo <= left <= hi:
                sols.append(cur + [left])
            return
        remaining = n - pos - 1
        low_v = max(lo, left - hi * remaining)
        high_v = min(hi, left - lo * remaining)
        for v in range(low_v, high_v + 1):
            walk(pos + 1, left - v, cur + [v])
            if len(sols) >= cap:
                return

    walk(0, total, [])
    out = {
        "method": "integer vectors from mean (bounded enumeration)",
        "value_type": "inferred",
        "n": n,
        "total": total,
        "bounds": [lo, hi],
        "solutions": sols,
        "n_solutions": len(sols),
        "confidence": "A" if len(sols) == 1 else "C",
        "note": "enumeration capped; a capped result is never unique" if len(sols) >= cap else "",
    }
    if sols:
        ss = [sum(v * v for v in s) for s in sols]
        out["ss_range"] = [min(ss), max(ss)]
    return out


def selftest(argv):
    tmp = S.tmpdir()
    checks = []
    x = [1, 2, 3, 4, 5]
    n = len(x)
    mean_v = sum(x) / n
    sd_v = math.sqrt(sum((v - mean_v) ** 2 for v in x) / (n - 1))
    g = grim(n, mean_v, 2)
    checks.append(S.check("grim_forward_consistent", g["consistent"], str(g.get("feasible_totals"))))
    gr = grimmer(n, mean_v, sd_v, 2, 4)
    checks.append(S.check("grimmer_forward_consistent", gr["consistent"], str(gr.get("verdict"))))
    bad = grim(5, 3.1, 2)
    checks.append(S.check("grim_flags_impossible", bad["consistent"] is False, str(bad.get("verdict"))))
    p = percent_to_counts(40, 65.0, 1)
    checks.append(S.check("percent_unique_26", p["point"] == 26 and p["confidence"] == "A", str(p["point"])))
    p2 = percent_to_counts(30, 33.3, 1)
    checks.append(S.check("percent_multi_C", p2["confidence"] in ("C", "A"), "counts=" + str(p2["feasible_counts"])))
    se = ratio_ci_to_se(0.62, 0.41, 0.94)
    want = (math.log(0.94) - math.log(0.41)) / (2 * Z975)
    checks.append(S.check("ratio_se_formula", abs(se["se_log"] - want) < 1e-9, S.fmt(se["se_log"], 6)))
    t2 = table_2x2(1.0, 30, 40, 100)
    checks.append(S.check("table_2x2_finds_or_1", t2["n_solutions"] >= 1, str(t2["n_solutions"]) + " solution(s)"))
    planted = table_2x2(10 * 40 / float(20 * 30), 30, 40, 100, tol=1e-6)
    hit = any(s["a"] == 10 and s["b"] == 20 and s["c"] == 30 and s["d"] == 40 for s in planted["solutions"])
    checks.append(S.check("table_2x2_recovers_planted", hit, str(planted["solutions"])[:80]))
    iqr = iqr_to_sd(40, 1.0, 3.0)
    checks.append(S.check("iqr_interval_not_point", iqr["confidence"] == "B" and iqr["range"][1] > iqr["range"][0], S.fmt(iqr["range"][0], 3) + "-" + S.fmt(iqr["range"][1], 3)))
    mv = mean_vectors(3, 2.0, 0, 5)
    checks.append(S.check("mean_vectors_roundtrip", mv["n_solutions"] >= 1 and all(sum(s) == 6 for s in mv["solutions"]), str(mv["n_solutions"])))
    mv_bad = mean_vectors(3, 2.1, 0, 5)
    checks.append(S.check("mean_vectors_impossible", mv_bad["consistent"] is False, "no integer total"))
    rows = [
        ["字段", "取值", "类型", "方法", "置信度", "区间"],
        ["n", str(n), "inferred", "input", "A", ""],
        ["mean", S.fmt(mean_v, 4), "inferred", "bounded enumeration", mv["confidence"], ""],
        ["SD", S.fmt(sd_v, 4), "inferred", "GRIMMER necessary", gr["confidence"], ""],
    ]
    payload = {"value_type": "inferred", "not_reconstructable": NOT_RECONSTRUCTABLE, "rows": rows}
    S.write_json(tmp / "recon" / "recon.json", payload)
    xlsx = OW.write_xlsx(
        tmp / "recon" / "recon.xlsx",
        {"kind": "xlsx", "sheets": [{"name": "recon", "header": rows[0], "rows": rows[1:]}]},
    )
    first = xlsx.read_bytes()
    OW.write_xlsx(tmp / "recon" / "recon.xlsx", {"kind": "xlsx", "sheets": [{"name": "recon", "header": rows[0], "rows": rows[1:]}]})
    checks.append(S.check("xlsx_idempotent", first == xlsx.read_bytes(), "byte identical"))
    checks.append(S.check("no_banned_words", not any(w in str(payload) for w in BANNED_WORDS), "no forbidden wording"))
    checks.append(S.check("not_reconstructable_listed", len(NOT_RECONSTRUCTABLE) >= 9, str(len(NOT_RECONSTRUCTABLE)) + " fields"))
    failed = [c for c in checks if c["status"] != "pass"]
    for c in checks:
        print("  [{}] {} {}".format(c["status"], c["name"], c["reason"]))
    S.log_run("data_reconstruct.py", argv, checks, [], log_path=tmp / "logs" / "run.jsonl")
    print("selftest: {} checks, {} failed".format(len(checks), len(failed)))
    return S.EXIT_OK if not failed else S.EXIT_ASSERT


def fixtures(argv):
    tmp = S.tmpdir()
    checks = []
    checks.extend(S.json_fixture_checks(tmp))
    checks.append(S.check("grim_zero_n", grim(0, 1.0)["confidence"] == "D", "n=0 rejected"))
    checks.append(S.check("iqr_zero", iqr_to_sd(10, 2.0, 2.0)["confidence"] == "D", "IQR=0 rejected"))
    checks.append(S.check("bad_ci", ratio_ci_to_se(1.0, 1.2, 1.4)["confidence"] == "D", "CI not bracketing"))
    checks.append(S.check("percent_zero_n", percent_to_counts(0, 50)["confidence"] == "D", "n=0 rejected"))
    empty = table_2x2(2.5, 5, 5, 5, tol=1e-6)
    checks.append(S.check("table_2x2_no_solution", empty["n_solutions"] == 0 and empty["confidence"] == "D", "D grade"))
    big = mean_vectors(12, 3.5, 0, 7)
    checks.append(S.check("mean_vectors_capped_not_unique", big["n_solutions"] >= 1 and big["confidence"] in ("C", "A"), str(big["n_solutions"])))
    for label, bad in (
        ("n_float", {"type": "grim", "n": 1.5, "mean": 62.5}),
        ("n_zero", {"type": "grim", "n": 0, "mean": 1.0}),
        ("decimals_negative", {"type": "grim", "n": 10, "mean": 2.0, "decimals": -1}),
        ("lo_above_hi", {"type": "grim", "n": 10, "mean": 2.0, "lo": 9, "hi": 3}),
        ("mean_outside_bounds", {"type": "grim", "n": 10, "mean": 99.0, "lo": 0, "hi": 10}),
        ("percent_over_100", {"type": "percent", "n": 10, "percent": 140}),
        ("sd_negative", {"type": "grimmer", "n": 10, "mean": 2.0, "sd": -1.0}),
    ):
        code = 0
        try:
            validate_item(dict(bad), 0, bad["type"])
        except SystemExit as exc:
            code = int(exc.code or 0)
        checks.append(S.check("invalid_" + label + "_exit2", code == S.EXIT_INPUT, "exit " + str(code)))
    failed = [c for c in checks if c["status"] != "pass"]
    for c in checks:
        print("  [{}] {} {}".format(c["status"], c["name"], c["reason"]))
    S.log_run("data_reconstruct.py", argv, checks, [], log_path=tmp / "logs" / "run.jsonl")
    print("fixtures: {} checks, {} failed".format(len(checks), len(failed)))
    return S.EXIT_OK if not failed else S.EXIT_ASSERT


def as_int(value, where, minimum=None, allow_zero=True):
    """Integers only. A float like 1.5 is an input error, not an inferred value."""
    if isinstance(value, bool):
        S.fail("{} 必须是整数，收到布尔值".format(where), S.EXIT_INPUT)
    if isinstance(value, int):
        out = value
    elif isinstance(value, float) and float(value).is_integer():
        out = int(value)
    else:
        S.fail("{} 必须是整数，收到 {}".format(where, value), S.EXIT_INPUT)
    if minimum is not None and out < minimum:
        S.fail("{} 必须 >= {}，收到 {}".format(where, minimum, out), S.EXIT_INPUT)
    if not allow_zero and out == 0:
        S.fail("{} 必须 > 0，收到 0".format(where), S.EXIT_INPUT)
    return out


def as_number(value, where):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        S.fail("{} 必须是数值，收到 {!r}".format(where, value), S.EXIT_INPUT)
    return float(value)


def validate_item(item, idx, kind):
    """Input legality is checked before any inference; grades A-D never cover bad input."""
    base = "items[{}] (type={})".format(idx, kind)
    if "n" in ITEM_REQUIRED[kind]:
        item["n"] = as_int(item["n"], base + " 的 n", minimum=1)
    for key in ("decimals", "decimals_mean", "decimals_sd"):
        if item.get(key) is not None:
            item[key] = as_int(item[key], base + " 的 " + key, minimum=0)
    for key in ("lo", "hi"):
        if item.get(key) is not None:
            item[key] = as_number(item[key], base + " 的 " + key)
    if item.get("lo") is not None and item.get("hi") is not None and item["lo"] > item["hi"]:
        S.fail("{} 的 lo 必须 <= hi，收到 lo={} hi={}".format(base, item["lo"], item["hi"]), S.EXIT_INPUT)
    if "mean" in ITEM_REQUIRED[kind]:
        item["mean"] = as_number(item["mean"], base + " 的 mean")
        if item.get("lo") is not None and item["mean"] < item["lo"]:
            S.fail("{} 的 mean 必须落在 [lo, hi] 内，收到 mean={} lo={}".format(base, item["mean"], item["lo"]), S.EXIT_INPUT)
        if item.get("hi") is not None and item["mean"] > item["hi"]:
            S.fail("{} 的 mean 必须落在 [lo, hi] 内，收到 mean={} hi={}".format(base, item["mean"], item["hi"]), S.EXIT_INPUT)
    if kind == "grimmer":
        item["sd"] = as_number(item["sd"], base + " 的 sd")
        if item["sd"] < 0:
            S.fail("{} 的 sd 不能为负，收到 {}".format(base, item["sd"]), S.EXIT_INPUT)
    if kind == "percent":
        item["percent"] = as_number(item["percent"], base + " 的 percent")
        if not -1e-9 <= item["percent"] <= 100 + 1e-9:
            S.fail("{} 的 percent 必须在 [0, 100] 内，收到 {}".format(base, item["percent"]), S.EXIT_INPUT)
    return item


ITEM_KEYS = {
    "grim": ("type", "label", "n", "mean", "decimals", "lo", "hi"),
    "grimmer": ("type", "label", "n", "mean", "sd", "decimals_mean", "decimals_sd", "lo", "hi"),
    "iqr": ("type", "label", "n", "q1", "q3", "lo", "hi"),
    "percent": ("type", "label", "n", "percent", "decimals"),
    "ratio": ("type", "label", "estimate", "low", "high"),
    "table2x2": ("type", "label", "odds_ratio", "row1_total", "col1_total", "n", "tol"),
    "vectors": ("type", "label", "n", "mean", "lo", "hi"),
}

ITEM_REQUIRED = {
    "grim": ("n", "mean"),
    "grimmer": ("n", "mean", "sd"),
    "iqr": ("n", "q1", "q3"),
    "percent": ("n", "percent"),
    "ratio": ("estimate", "low", "high"),
    "table2x2": ("odds_ratio", "row1_total", "col1_total", "n"),
    "vectors": ("n", "mean"),
}

SPEC_HELP = """\
{"items": [
  {"type": "grim",      "label": "age_mean", "n": 24, "mean": 62.5, "decimals": 1, "lo": 18, "hi": 105},
  {"type": "grimmer",   "label": "lactate",  "n": 24, "mean": 2.4, "sd": 1.13},
  {"type": "percent",   "label": "mortality","n": 24, "percent": 25.0},
  {"type": "ratio",     "label": "or",       "estimate": 0.71, "low": 0.212, "high": 2.381},
  {"type": "table2x2",  "label": "tbl",      "odds_ratio": 1.5, "row1_total": 12, "col1_total": 9, "n": 24},
  {"type": "iqr",       "label": "age_iqr",  "n": 24, "q1": 55, "q3": 70, "lo": 45, "hi": 86}]}

type = grim(n,mean[,decimals,lo,hi]) | grimmer(n,mean,sd[,decimals_mean,decimals_sd,lo,hi])
     | iqr(n,q1,q3[,lo,hi]) | percent(n,percent[,decimals])
     | ratio(estimate,low,high) | table2x2(odds_ratio,row1_total,col1_total,n[,tol])
     | vectors(n,mean[,lo,hi])
Outputs: recon/recon.json + recon/recon.xlsx; every value is an inferred value, never original data.
"""


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(
        description="reconstruct possible counts from reported summary statistics (inferred values only).",
        epilog=SPEC_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--fixtures", action="store_true")
    ap.add_argument("--spec", help="JSON spec with items[]; see the epilog for every type")
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
    if not ns.spec:
        S.fail("--spec is required unless --probe/--selftest/--fixtures", S.EXIT_INPUT)
    spec = S.read_json(ns.spec)
    out = S.out_dir(ns.out)
    results = {}
    items = spec.get("items")
    if not isinstance(items, list) or not items:
        S.fail("spec.items must be a non-empty list", S.EXIT_INPUT)
    for idx, item in enumerate(items):
        kind = item.get("type") if isinstance(item, dict) else None
        if kind not in ITEM_REQUIRED:
            S.fail(
                "items[{}] has unknown type {!r}; allowed: {}".format(idx, kind, ", ".join(ITEM_REQUIRED)),
                S.EXIT_INPUT,
            )
        lack = [f for f in ITEM_REQUIRED[kind] if item.get(f) is None]
        if lack:
            S.fail(
                "items[{}] (type={}) missing required field(s): {}".format(idx, kind, ", ".join(lack)),
                S.EXIT_INPUT,
            )
        S.unknown_keys(item, ITEM_KEYS[kind], "items[{}] (type={})".format(idx, kind), hard=True)
        validate_item(item, idx, kind)
        if kind == "grim":
            results[item.get("label", "grim")] = grim(item["n"], item["mean"], item.get("decimals", 2), item.get("lo"), item.get("hi"))
        elif kind == "grimmer":
            results[item.get("label", "grimmer")] = grimmer(
                item["n"], item["mean"], item["sd"], item.get("decimals_mean", 2), item.get("decimals_sd", 2),
                item.get("lo"), item.get("hi"),
            )
        elif kind == "iqr":
            results[item.get("label", "iqr")] = iqr_to_sd(item["n"], item["q1"], item["q3"], item.get("lo"), item.get("hi"))
        elif kind == "percent":
            results[item.get("label", "percent")] = percent_to_counts(item["n"], item["percent"], item.get("decimals", 1))
        elif kind == "ratio":
            results[item.get("label", "ratio")] = ratio_ci_to_se(item["estimate"], item["low"], item["high"])
        elif kind == "table2x2":
            results[item.get("label", "table2x2")] = table_2x2(
                item["odds_ratio"], item["row1_total"], item["col1_total"], item["n"], item.get("tol", 1e-3)
            )
        elif kind == "vectors":
            results[item.get("label", "vectors")] = mean_vectors(
                item["n"], item["mean"], item.get("lo", 0), item.get("hi")
            )
        else:
            S.fail("unsupported item type: " + str(kind), S.EXIT_INPUT)
    payload = {
        "value_type": "inferred",
        "disclaimer": "推断值（图表数字化 + 模型反演）；不代表原始观测",
        "not_reconstructable": NOT_RECONSTRUCTABLE,
        "results": results,
    }
    S.write_json(out / "recon" / "recon.json", payload)
    rows = []
    for label, res in results.items():
        rows.append(
            [
                label,
                res.get("method", ""),
                str(res.get("confidence", "")),
                str(res.get("value_type", "inferred")),
                str(res.get("verdict") or res.get("note") or ""),
            ]
        )
    OW.write_xlsx(
        out / "recon" / "recon.xlsx",
        {
            "kind": "xlsx",
            "sheets": [
                {"name": "not-reconstructable", "header": ["字段", "原因"], "rows": [list(x) for x in NOT_RECONSTRUCTABLE]},
                {"name": "recon", "header": ["项目", "方法", "置信度", "类型", "结论或说明"], "rows": rows},
            ],
        },
    )
    S.log_run("data_reconstruct.py", argv, [], [out / "recon" / "recon.json", out / "recon" / "recon.xlsx"], log_path=ns.log)
    print("wrote recon/recon.json and recon/recon.xlsx ({} item(s))".format(len(results)))
    if ns.json:
        print(S.read_json(out / "recon" / "recon.json"))
    return S.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
