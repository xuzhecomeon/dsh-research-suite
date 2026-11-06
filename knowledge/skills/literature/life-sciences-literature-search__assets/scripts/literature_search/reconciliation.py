"""Publication identity resolution, evidence merging, ranking, and filtering.

The source adapters deliberately emit a small common record vocabulary.  This
module owns the separate, source-agnostic step which turns those records into
deduplicated publication candidates.  Keeping it independent prevents source
transport changes from silently changing evidence-merging policy.
"""

from __future__ import annotations

import re
from typing import Any, Iterable

from .adapter_contracts import ResultFilters
from .backend import (
    AGENT_WEB_SOURCE,
    RRF_K,
    SOURCE_ORDER,
    SOURCE_ROLES,
    SOURCE_RRF_WEIGHTS,
    clean_text,
    collapse_ws,
    infer_query_family,
    lexical_coverage,
    normalize_metadata_term,
    normalize_title,
    optional_bool,
    safe_int,
    screen_reported_count,
    truncate_text,
)


def record_aliases(record: dict[str, Any]) -> set[str]:
    """Return stable identifiers and a normalized-title fallback."""
    aliases: set[str] = set()
    identifiers = record.get("identifiers") or {}
    for name in ("doi", "pmid", "pmcid", "arxiv"):
        value = collapse_ws(identifiers.get(name)).casefold()
        if value:
            aliases.add(f"{name}:{value}")
    title = normalize_title(record.get("title"))
    if len(title) >= 8:
        aliases.add(f"title:{title}")
    return aliases


def strong_identifier_conflict(
    record: dict[str, Any], group: list[dict[str, Any]]
) -> bool:
    incoming = record.get("identifiers") or {}
    for name in ("doi", "pmid", "pmcid", "arxiv"):
        value = collapse_ws(incoming.get(name)).casefold()
        if not value:
            continue
        existing = {
            collapse_ws((candidate.get("identifiers") or {}).get(name)).casefold()
            for candidate in group
            if (candidate.get("identifiers") or {}).get(name)
        }
        if existing and value not in existing:
            return True
    return False


def group_records(records: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Group records without allowing a title match to override conflicting IDs."""
    groups: dict[int, list[dict[str, Any]]] = {}
    group_aliases: dict[int, set[str]] = {}
    alias_to_group: dict[str, int] = {}
    next_group = 0

    for record in records:
        aliases = record_aliases(record)
        matched: set[int] = set()
        for alias in aliases:
            group_id = alias_to_group.get(alias)
            if group_id is None:
                continue
            if alias.startswith("title:") and strong_identifier_conflict(
                record, groups[group_id]
            ):
                continue
            matched.add(group_id)

        if not matched:
            group_id = next_group
            next_group += 1
            groups[group_id] = [record]
            group_aliases[group_id] = set(aliases)
        else:
            group_id = min(matched)
            groups[group_id].append(record)
            group_aliases[group_id].update(aliases)
            for other_id in sorted(matched - {group_id}):
                groups[group_id].extend(groups.pop(other_id))
                group_aliases[group_id].update(group_aliases.pop(other_id))
        for alias in group_aliases[group_id]:
            alias_to_group[alias] = group_id

    return list(groups.values())


def _choose_text(records: list[dict[str, Any]], field: str) -> str:
    candidates = [
        collapse_ws(record.get(field)) for record in records if record.get(field)
    ]
    return max(candidates, key=lambda value: (len(value), value), default="")


def _collect_metadata_values(
    records: list[dict[str, Any]], field: str
) -> list[str]:
    values: list[str] = []
    for record in records:
        raw = collapse_ws(record.get(field))
        if raw:
            values.extend(clean_text(value) for value in re.split(r"[,;]", raw))
    return list(dict.fromkeys(value for value in values if value))


def _merge_source_enrichment(
    records: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for record in records:
        source = collapse_ws(record.get("source"))
        enrichment = record.get("source_enrichment") or {}
        if not source or not isinstance(enrichment, dict) or not enrichment:
            continue
        target = merged.setdefault(source, {})
        for name, value in enrichment.items():
            if isinstance(value, bool):
                target[name] = bool(target.get(name)) or value
            elif isinstance(value, list):
                existing = target.setdefault(name, [])
                if isinstance(existing, list):
                    existing.extend(item for item in value if item not in existing)
            elif value is not None and name not in target:
                target[name] = value
    return merged


def _ranking_family_counts(
    records: Iterable[dict[str, Any]],
) -> dict[str, int]:
    families_by_source: dict[str, set[str]] = {}
    for record in records:
        source = collapse_ws(record.get("source"))
        if source:
            family = infer_query_family(
                record.get("query"), explicit=record.get("query_family")
            )
            families_by_source.setdefault(source, set()).add(family)
    return {source: len(families) for source, families in families_by_source.items()}


def _merged_optional_bool(
    records: Iterable[dict[str, Any]], field: str
) -> bool | None:
    values = [optional_bool(record.get(field)) for record in records]
    if True in values:
        return True
    if False in values:
        return False
    return None


def _verification_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    structured_sources = sorted(
        {
            record["source"]
            for record in records
            if record.get("source")
            and record["source"] != AGENT_WEB_SOURCE
            and SOURCE_ROLES.get(record["source"]) != "open_access_enrichment"
        },
        key=lambda value: SOURCE_ORDER.get(value, 999),
    )
    web_enrichments = [
        record.get("source_enrichment") or {}
        for record in records
        if record.get("source") == AGENT_WEB_SOURCE
    ]
    web_metadata_verified = any(
        enrichment.get("metadata_verified") is True
        for enrichment in web_enrichments
        if isinstance(enrichment, dict)
    )
    web_constraints_verified = any(
        enrichment.get("constraints_verified") is True
        for enrichment in web_enrichments
        if isinstance(enrichment, dict)
    )
    if structured_sources:
        level, multiplier = "structured_confirmed", 1.0
    elif web_metadata_verified:
        level, multiplier = "web_metadata_verified", 0.82
    else:
        level, multiplier = "web_unverified", 0.58
    return {
        "level": level,
        "metadata_verified": bool(structured_sources) or web_metadata_verified,
        "structured_sources": structured_sources,
        "web_metadata_verified": web_metadata_verified,
        "web_constraints_verified": web_constraints_verified,
        "ranking_multiplier": multiplier,
    }


def _variant_context_summary(
    records: Iterable[dict[str, Any]],
) -> dict[str, Any] | None:
    statuses = {
        collapse_ws(record.get("variant_context_status"))
        for record in records
        if collapse_ws(record.get("variant_context_status"))
    }
    if not statuses:
        return None
    if "strict_disease_anchored" in statuses:
        status = "strict_disease_anchored"
        multiplier = 1.0
        note = "Retrieved by a variant lane anchored to both gene and disease."
    elif "broad_with_disease_text_match" in statuses:
        status = "broad_with_disease_text_match"
        multiplier = 0.9
        note = "Broad variant fallback matched disease text, but context still needs review."
    else:
        status = "broad_without_disease_text_match"
        multiplier = 0.72
        note = "Broad fallback found the variant/gene without supplied disease text; manually verify disease relevance."
    return {"status": status, "ranking_multiplier": multiplier, "note": note}


def _merge_record_group(
    group: list[dict[str, Any]],
    snippet_chars: int,
    family_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    ordered = sorted(
        group,
        key=lambda record: (
            SOURCE_ORDER.get(record["source"], 999),
            safe_int(record.get("source_rank")) or 9999,
        ),
    )
    identifiers: dict[str, str] = {}
    for record in ordered:
        for name, value in (record.get("identifiers") or {}).items():
            if value and name not in identifiers:
                identifiers[name] = value

    authors = max(
        (record.get("authors") or [] for record in ordered),
        key=lambda values: (len(values), sum(len(value) for value in values)),
        default=[],
    )
    years = [safe_int(record.get("year")) for record in ordered]
    year = max((value for value in years if value is not None), default=None)
    dates = [collapse_ws(record.get("publication_date")) for record in ordered]
    publication_date = max((value for value in dates if value), default=None)
    publication_type = next(
        (
            collapse_ws(record.get("publication_type"))
            for record in ordered
            if record.get("publication_type")
            and "preprint" not in collapse_ws(record.get("publication_type")).lower()
        ),
        _choose_text(ordered, "publication_type"),
    )
    publication_types = _collect_metadata_values(ordered, "publication_type")
    languages = _collect_metadata_values(ordered, "language")
    abstract = _choose_text(ordered, "abstract")

    source_records: list[dict[str, Any]] = []
    seen_source_records: set[tuple[str, str, str, str]] = set()
    best_lane_ranks: dict[tuple[str, str], int] = {}
    citation_counts: dict[str, int] = {}
    for record in ordered:
        query_family = infer_query_family(
            record.get("query"), explicit=record.get("query_family")
        )
        source_key = (
            record["source"],
            collapse_ws(record.get("source_id")),
            record["query"],
            query_family,
        )
        if source_key not in seen_source_records:
            seen_source_records.add(source_key)
            rank = safe_int(record.get("source_rank")) or 9999
            lane_key = (record["source"], query_family)
            best_lane_ranks[lane_key] = min(rank, best_lane_ranks.get(lane_key, rank))
            source_records.append(
                {
                    "source": record["source"],
                    "source_id": collapse_ws(record.get("source_id")) or None,
                    "source_rank": rank,
                    "query": record["query"],
                    "query_family": query_family,
                    "query_lane": collapse_ws(record.get("query_lane")) or query_family,
                    "query_origin": collapse_ws(record.get("query_origin")) or None,
                    "scenario": collapse_ws(record.get("scenario")) or None,
                    "evidence_dimension": collapse_ws(record.get("evidence_dimension")) or None,
                    "query_purpose": collapse_ws(record.get("query_purpose")) or None,
                    "context_level": collapse_ws(record.get("query_context_level")) or None,
                    "url": record.get("url"),
                }
            )
        count = safe_int(record.get("citation_count"))
        if count is not None:
            citation_counts[record["source"]] = max(
                count, citation_counts.get(record["source"], 0)
            )

    active_family_counts = family_counts or _ranking_family_counts(ordered)
    rrf = 0.0
    ranking_lanes: list[dict[str, Any]] = []
    for (source, family), rank in sorted(
        best_lane_ranks.items(),
        key=lambda item: (SOURCE_ORDER.get(item[0][0], 999), item[0][1]),
    ):
        source_family_count = max(1, active_family_counts.get(source, 1))
        normalized_weight = SOURCE_RRF_WEIGHTS.get(source, 1.0) / source_family_count
        contribution = normalized_weight / (RRF_K + rank)
        rrf += contribution
        ranking_lanes.append(
            {
                "source": source,
                "query_family": family,
                "best_rank": rank,
                "normalized_weight": round(normalized_weight, 8),
                "rrf_contribution": round(contribution, 8),
            }
        )

    sources = sorted({record["source"] for record in ordered}, key=SOURCE_ORDER.get)
    query_variants = list(dict.fromkeys(record["query"] for record in ordered))
    query_families = list(
        dict.fromkeys(
            infer_query_family(record.get("query"), explicit=record.get("query_family"))
            for record in ordered
        )
    )
    coverage = max(
        (lexical_coverage(query, ordered) for query in query_variants), default=0.0
    )
    verification = _verification_summary(ordered)
    variant_context = _variant_context_summary(ordered)
    context_multiplier = (
        variant_context["ranking_multiplier"] if variant_context is not None else 1.0
    )
    pre_verification_score = rrf + (0.025 * coverage)
    combined_score = (
        pre_verification_score
        * verification["ranking_multiplier"]
        * context_multiplier
    )
    oa_url = next(
        (record.get("open_access_url") for record in ordered if record.get("open_access_url")),
        None,
    )
    doi = identifiers.get("doi")
    pmid = identifiers.get("pmid")
    pmcid = identifiers.get("pmcid")
    arxiv_id = identifiers.get("arxiv")
    canonical_url = (
        f"https://doi.org/{doi}"
        if doi
        else f"https://europepmc.org/article/MED/{pmid}"
        if pmid
        else f"https://europepmc.org/articles/{pmcid}"
        if pmcid
        else f"https://arxiv.org/abs/{arxiv_id}"
        if arxiv_id
        else next((record.get("url") for record in ordered if record.get("url")), None)
    )
    is_retracted = _merged_optional_bool(ordered, "is_retracted")
    has_correction = _merged_optional_bool(ordered, "has_correction")
    publication_states = list(
        dict.fromkeys(
            state
            for record in ordered
            for state in (record.get("publication_states") or [])
            if state
        )
    )
    if is_retracted is True and "retracted" not in publication_states:
        publication_states.append("retracted")

    return {
        "title": _choose_text(ordered, "title"),
        "authors": authors,
        "year": year,
        "publication_date": publication_date,
        "venue": _choose_text(ordered, "venue"),
        "publication_type": publication_type,
        "publication_types": publication_types,
        "languages": languages,
        "abstract": abstract or None,
        "snippet": truncate_text(abstract, snippet_chars),
        "_abstract": abstract,
        "identifiers": identifiers,
        "url": canonical_url,
        "open_access_url": oa_url,
        "open_access": bool(oa_url),
        "citation_counts": citation_counts,
        "is_retracted": is_retracted,
        "has_correction": has_correction,
        "publication_states": publication_states,
        "sources": sources,
        "matched_query_variants": query_variants,
        "matched_query_families": query_families,
        "matched_query_lanes": list(
            dict.fromkeys(
                collapse_ws(record.get("query_lane"))
                or infer_query_family(record.get("query"), explicit=record.get("query_family"))
                for record in ordered
            )
        ),
        "matched_scenarios": list(
            dict.fromkeys(
                collapse_ws(record.get("scenario"))
                for record in ordered
                if collapse_ws(record.get("scenario"))
            )
        ),
        "evidence_dimensions": list(
            dict.fromkeys(
                collapse_ws(record.get("evidence_dimension"))
                for record in ordered
                if collapse_ws(record.get("evidence_dimension"))
            )
        ),
        "source_records": source_records,
        "source_enrichment": _merge_source_enrichment(ordered),
        "verification": verification,
        "variant_context": variant_context,
        "ranking_lanes": ranking_lanes,
        "score": {
            "combined": round(combined_score, 8),
            "rrf": round(rrf, 8),
            "pre_verification": round(pre_verification_score, 8),
            "variant_context_multiplier": context_multiplier,
            "lexical_coverage": round(coverage, 6),
            "source_matches": len(sources),
            "query_matches": len(query_variants),
            "family_matches": len(query_families),
        },
    }


def _metadata_matches_any(actual: Iterable[str], requested: Iterable[str]) -> bool:
    actual_terms = [normalize_metadata_term(value) for value in actual]
    requested_terms = [normalize_metadata_term(value) for value in requested]
    return any(
        requested_term
        and actual_term
        and (
            requested_term == actual_term
            or requested_term in actual_term
            or actual_term in requested_term
        )
        for requested_term in requested_terms
        for actual_term in actual_terms
    )


def _is_explicit_preprint(record: dict[str, Any]) -> bool:
    publication_types = record.get("publication_types") or []
    normalized_types = {normalize_metadata_term(value) for value in publication_types}
    identifiers = record.get("identifiers") or {}
    venue = normalize_metadata_term(record.get("venue"))
    return bool(
        normalized_types.intersection({"preprint", "postedcontent"})
        or identifiers.get("arxiv")
        or venue in {"arxiv", "corr"}
    )


def _result_matches_filters(record: dict[str, Any], filters: ResultFilters) -> bool:
    sources = set(record.get("sources") or [])
    if any(source not in sources for source in filters.required_sources):
        return False
    publication_types = record.get("publication_types") or []
    if filters.publication_types and not _metadata_matches_any(
        publication_types, filters.publication_types
    ):
        return False
    if filters.excluded_publication_types and _metadata_matches_any(
        publication_types, filters.excluded_publication_types
    ):
        return False
    if filters.authors and not _metadata_matches_any(
        record.get("authors") or [], filters.authors
    ):
        return False
    if filters.venues and not _metadata_matches_any(
        [record.get("venue") or ""], filters.venues
    ):
        return False
    if filters.languages and not _metadata_matches_any(
        record.get("languages") or [], filters.languages
    ):
        return False
    identifiers = record.get("identifiers") or {}
    if any(not identifiers.get(name) for name in filters.required_identifiers):
        return False
    if filters.require_abstract and not record.get("_abstract"):
        return False
    if filters.exclude_preprints and _is_explicit_preprint(record):
        return False
    if not filters.include_retracted and record.get("is_retracted") is True:
        return False
    if filters.has_associated_data:
        enrichments = record.get("source_enrichment") or {}
        if not any(
            isinstance(value, dict) and value.get("has_associated_data") is True
            for value in enrichments.values()
        ):
            return False
    if filters.strict_count:
        screening = record.get("reported_count_screening") or {}
        if screening.get("status") != "meets_threshold":
            return False
    return True


def _count_screen_priority(record: dict[str, Any]) -> int:
    status = (record.get("reported_count_screening") or {}).get("status")
    return {
        "meets_threshold": 0,
        "threshold_met_without_context": 1,
        "below_threshold": 2,
        "unknown": 3,
    }.get(status, 0)


def reconcile_records(
    records: list[dict[str, Any]],
    limit: int,
    snippet_chars: int,
    result_filters: ResultFilters | None = None,
) -> list[dict[str, Any]]:
    """Merge, filter, rank, and bound adapter records."""
    filters = result_filters or ResultFilters()
    family_counts = _ranking_family_counts(records)
    merged = [
        _merge_record_group(group, snippet_chars, family_counts)
        for group in group_records(records)
    ]
    if filters.min_reported_count is not None:
        for record in merged:
            record["reported_count_screening"] = screen_reported_count(
                record.get("_abstract") or "",
                filters.min_reported_count,
                filters.count_entities,
                filters.count_context_terms,
                filters.require_count_context,
            )
    merged = [record for record in merged if _result_matches_filters(record, filters)]

    def sort_key(record: dict[str, Any]) -> tuple[Any, ...]:
        screening_priority = _count_screen_priority(record)
        if filters.sort == "newest":
            return (
                screening_priority,
                -(record.get("year") or 0),
                -record["score"]["combined"],
                -record["score"]["source_matches"],
                -record["score"]["family_matches"],
                normalize_title(record.get("title")),
            )
        return (
            screening_priority,
            -record["score"]["combined"],
            -record["score"]["source_matches"],
            -record["score"]["family_matches"],
            -record["score"]["rrf"],
            -(record.get("year") or 0),
            normalize_title(record.get("title")),
        )

    merged.sort(key=sort_key)
    results = merged[:limit]
    for rank, record in enumerate(results, start=1):
        record["rank"] = rank
        record.pop("_abstract", None)
    return results
