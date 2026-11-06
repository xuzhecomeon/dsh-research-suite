#!/usr/bin/env python3
"""Researcher JSON output validator — 机械校验，代码执行，不可跳过。

用法:
  python3 validate_researcher_output.py <researcher_output.json> [--json]

校验三级：
  1. Schema — 必填字段存在
  2. Dedup — dedup.before >= dedup.after
  3. Resilience — query_resilience.succeeded >= ceil(total * 0.5)

退出码: 0=pass, 1=schema_fail, 2=dedup_fail, 3=resilience_warn(soft), 4=json_parse_error
"""

import json, sys, math

REQUIRED_TOP = ["sub_question", "findings", "source_funnel", "dedup", "query_resilience", "key_insight"]
REQUIRED_FINDING = ["finding_id", "claim", "source_url", "source_type", "source_date", "confidence"]
REQUIRED_FUNNEL = ["identified", "screened", "extracted", "included"]
REQUIRED_DEDUP = ["before", "after"]
REQUIRED_RESILIENCE = ["total", "succeeded", "failed", "threshold_met"]
VALID_SOURCE_TYPES = {"official_doc", "academic", "financial_media", "industry_blog", "community"}
VALID_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}


def validate(filepath: str) -> dict:
    errors, warnings = [], []

    # Parse
    try:
        with open(filepath) as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        return {"verdict": "fail", "stage": "json_parse_error", "errors": [str(e)], "warnings": []}

    # Level 1: Schema — top-level fields
    for field in REQUIRED_TOP:
        if field not in data:
            errors.append(f"missing top-level field: {field}")

    # findings array
    findings = data.get("findings", [])
    if not isinstance(findings, list):
        errors.append("findings must be an array")
        findings = []
    elif len(findings) == 0:
        errors.append("findings array is empty")

    for i, f in enumerate(findings):
        for field in REQUIRED_FINDING:
            if field not in f:
                errors.append(f"findings[{i}].{field}: missing")
        st = f.get("source_type", "")
        if st and st not in VALID_SOURCE_TYPES:
            errors.append(f"findings[{i}].source_type='{st}' not in {VALID_SOURCE_TYPES}")
        cf = f.get("confidence", "")
        if cf and cf not in VALID_CONFIDENCE:
            errors.append(f"findings[{i}].confidence='{cf}' not in {VALID_CONFIDENCE}")

    # source_funnel
    funnel = data.get("source_funnel", {})
    for field in REQUIRED_FUNNEL:
        if field not in funnel:
            errors.append(f"source_funnel.{field}: missing")

    # Level 2: Dedup
    dedup = data.get("dedup", {})
    for field in REQUIRED_DEDUP:
        if field not in dedup:
            errors.append(f"dedup.{field}: missing")
    if "before" in dedup and "after" in dedup:
        try:
            if dedup["before"] < dedup["after"]:
                errors.append(f"dedup.before({dedup['before']}) < dedup.after({dedup['after']})")
        except TypeError:
            errors.append("dedup.before/after must be numbers")

    # Level 3: Resilience
    resilience = data.get("query_resilience", {})
    for field in REQUIRED_RESILIENCE:
        if field not in resilience:
            errors.append(f"query_resilience.{field}: missing")
    if "total" in resilience and "succeeded" in resilience:
        try:
            threshold = math.ceil(resilience["total"] * 0.5)
            if resilience["succeeded"] < threshold:
                warnings.append(
                    f"query_resilience: succeeded({resilience['succeeded']}) < threshold({threshold}/{resilience['total']})"
                )
        except TypeError:
            errors.append("query_resilience.total/succeeded must be numbers")

    # Verdict
    if errors:
        return {
            "verdict": "fail",
            "stage": "schema" if any("missing" in e for e in errors) else "dedup",
            "errors": errors,
            "warnings": warnings,
        }
    if warnings:
        return {"verdict": "warn", "stage": "resilience", "errors": [], "warnings": warnings}
    return {"verdict": "pass", "stage": "all_clear", "errors": [], "warnings": []}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_researcher_output.py <researcher_output.json> [--json]", file=sys.stderr)
        sys.exit(4)

    result = validate(sys.argv[1])
    fmt = "--json" in sys.argv

    if fmt:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "✅ PASS" if result["verdict"] == "pass" else ("⚠️ WARN" if result["verdict"] == "warn" else f"❌ FAIL ({result['stage']})")
        print(f"{status}")
        for e in result["errors"]:
            print(f"  ERR: {e}")
        for w in result["warnings"]:
            print(f"  WARN: {w}")

    exit_map = {"pass": 0, "fail": 1, "warn": 3}
    sys.exit(exit_map.get(result["verdict"], 4))
