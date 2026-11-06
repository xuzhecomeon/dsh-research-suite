"""Normalize source-operation audit entries and summarize their ledger."""

from __future__ import annotations

from typing import Any

from .backend import SOURCE_ROLES, collapse_ws, infer_query_family


def normalize_source_status(status: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(status)
    family = infer_query_family(
        normalized.get("query"), explicit=normalized.get("query_family")
    )
    normalized.setdefault("source_role", SOURCE_ROLES.get(normalized.get("source")))
    normalized["query_family"] = family
    normalized.setdefault("query_lane", family)
    normalized.setdefault("query_origin", "source_operation")
    normalized.setdefault("scenario", None)
    normalized.setdefault("evidence_dimension", None)
    normalized.setdefault("query_purpose", None)
    normalized.setdefault("run_condition", "always")
    normalized.setdefault("depends_on", None)
    normalized.setdefault("context_level", None)
    normalized.setdefault("requested_limit", None)
    normalized.setdefault("effective_limit", None)
    normalized.setdefault("endpoint", None)
    normalized.setdefault("received", None)
    normalized.setdefault("accepted", None)
    normalized.setdefault("reported_total", None)
    normalized.setdefault("truncated", None)
    return normalized


def build_search_ledger(statuses: list[dict[str, Any]]) -> dict[str, Any]:
    families: dict[str, dict[str, int]] = {}
    lanes: dict[str, dict[str, int]] = {}
    for status in statuses:
        family = infer_query_family(
            status.get("query"), explicit=status.get("query_family")
        )
        counts = families.setdefault(family, _empty_counts())
        lane = collapse_ws(status.get("query_lane")) or family
        lane_counts = lanes.setdefault(lane, _empty_counts())
        counts["runs"] += 1
        lane_counts["runs"] += 1
        bucket = {
            "ok": "successful",
            "error": "failed",
            "skipped": "skipped",
            "not_run": "not_run",
        }.get(status.get("status"))
        if bucket:
            counts[bucket] += 1
            lane_counts[bucket] += 1
    return {
        "run_count": len(statuses),
        "successful_runs": sum(status.get("status") == "ok" for status in statuses),
        "failed_runs": sum(status.get("status") == "error" for status in statuses),
        "skipped_runs": sum(
            status.get("status") == "skipped" for status in statuses
        ),
        "not_run": sum(status.get("status") == "not_run" for status in statuses),
        "query_families": families,
        "query_lanes": lanes,
        "details_field": "source_status",
    }


def _empty_counts() -> dict[str, int]:
    return {"runs": 0, "successful": 0, "failed": 0, "skipped": 0, "not_run": 0}
