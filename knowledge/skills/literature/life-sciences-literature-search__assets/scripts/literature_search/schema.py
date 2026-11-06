"""Validation and shared invariants for evidence bundle schema v2.

The validator is intentionally dependency-free.  It protects the distinctions
that matter for downstream scientific reporting: bibliographic records are not
registry or database entities, access is not the same as inspection, and a
claim cannot cite evidence that is absent from the current retrieval artifact.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


SCHEMA_VERSION = "2.0"
ARTIFACT_TYPE = "life_sciences_evidence_bundle"
OBJECT_COLLECTIONS = {
    "papers": "paper",
    "trials": "trial",
    "drugs": "drug",
    "targets": "target",
    "datasets": "dataset",
}
OBJECT_TYPES = tuple(OBJECT_COLLECTIONS.values())
COLLECTION_FOR_TYPE = {value: key for key, value in OBJECT_COLLECTIONS.items()}

METADATA_STATUSES = ("verified", "partial", "unverified", "missing")
ABSTRACT_STATUSES = ("available", "unavailable", "not_checked")
FULL_TEXT_AVAILABILITY = ("open", "restricted", "unavailable", "unknown")
FULL_TEXT_RETRIEVAL = ("not_attempted", "retrieved", "failed")
FULL_TEXT_INSPECTION = ("not_inspected", "partially_inspected", "inspected")
CONTENT_LEVELS = ("metadata", "abstract", "full_text")
CLAIM_SUPPORT_LEVELS = (*CONTENT_LEVELS, "database")

PAPER_STABLE_IDENTIFIERS = ("doi", "pmid", "pmcid", "arxiv")
MODEL_BASES = ("retrieved_evidence", "model_background", "user_context")
CLAIM_METHODS = ("direct_extract", "model_synthesis", "source_assertion")

RETRIEVAL_STATES = ("performed", "not_performed")
DEPTHS = ("quick", "standard", "deep")
SCENARIOS = (
    "general-basic",
    "target-research",
    "drug-pipeline",
    "drug-safety",
    "clinical-evidence",
    "methods-benchmarking",
    "genetic-rare",
)
DELIVERABLES = ("list", "table", "review", "landscape")
OUTPUT_LANGUAGES = ("zh", "en", "bilingual")
SORT_ORDERS = ("relevance", "newest", "citations")
EXPANSION_MODES = ("auto", "none", "related", "citations", "both")
SOURCE_RUN_STATUSES = ("ok", "error", "skipped", "not_run")

CONSTRAINT_SEQUENCE_FIELDS = (
    "publication_types",
    "excluded_publication_types",
    "authors",
    "venues",
    "languages",
    "species",
    "required_identifiers",
)
CONSTRAINT_BOOLEAN_FIELDS = (
    "open_access",
    "require_abstract",
    "exclude_preprints",
    "include_retracted",
    "has_associated_data",
)
LEDGER_COUNT_FIELDS = (
    "runs",
    "successful",
    "failed",
    "skipped",
    "not_run",
)

FORBIDDEN_FIELDS = {
    "paper": {
        "registry",
        "registry_id",
        "phase",
        "phases",
        "sponsor",
        "interventions",
    },
    "trial": {"publications", "papers", "linked_publication_ids"},
    "drug": {
        "phase",
        "phases",
        "status",
        "sponsor",
        "sponsors",
        "indication",
        "indications",
        "trial_ids",
        "linked_publication_ids",
    },
    "target": {
        "disease",
        "diseases",
        "disease_associations",
        "linked_publication_ids",
    },
    "dataset": {
        "has_associated_data",
        "papers",
        "publication_ids",
        "linked_publication_ids",
    },
}


class SchemaValidationError(ValueError):
    """Raised when an evidence bundle violates one or more v2 invariants."""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid evidence bundle:\n- " + "\n- ".join(self.errors))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def identifier_links(object_: Mapping[str, Any]) -> list[dict[str, str]]:
    """Return canonical identifier links in stable preference order."""

    identifiers = _mapping(object_.get("identifiers"))
    links: list[dict[str, str]] = []
    templates = {
        "doi": "https://doi.org/{value}",
        "pmid": "https://pubmed.ncbi.nlm.nih.gov/{value}/",
        "pmcid": "https://europepmc.org/articles/{value}",
        "arxiv": "https://arxiv.org/abs/{value}",
        "nct": "https://clinicaltrials.gov/study/{value}",
    }
    for scheme in (*PAPER_STABLE_IDENTIFIERS, "nct"):
        value = _clean(identifiers.get(scheme))
        if not value:
            continue
        if scheme == "doi":
            value = value.removeprefix("https://doi.org/").removeprefix("doi:").strip()
        if scheme == "pmcid":
            value = value.upper()
        links.append(
            {
                "scheme": scheme,
                "value": value,
                "url": templates[scheme].format(value=value),
            }
        )
    return links


def citation_eligibility_for(object_: Mapping[str, Any]) -> dict[str, Any]:
    """Compute whether an object may support a traceable report claim.

    Eligibility is deliberately stricter than merely having a URL.  Formal
    bibliography export remains paper-only even though registry/database
    records can be eligible evidence for non-bibliographic facts.
    """

    object_type = _clean(object_.get("type"))
    reasons: list[str] = []
    links = identifier_links(object_)
    preferred = links[0] if links else None
    kind = "candidate_only"

    if object_type == "paper":
        kind = "bibliographic"
        verification = _clean(_mapping(object_.get("verification")).get("level"))
        metadata = _clean(
            _mapping(_mapping(object_.get("content_support")).get("metadata")).get(
                "status"
            )
        )
        if not links:
            reasons.append("missing_stable_identifier")
        if verification == "web_unverified":
            reasons.append("web_metadata_unverified")
        if metadata in {"missing", "unverified"}:
            reasons.append("metadata_not_verified")
    elif object_type == "trial":
        kind = "registry_record"
        registry = _clean(object_.get("registry"))
        registry_id = _clean(object_.get("registry_id"))
        if not registry or not registry_id:
            reasons.append("missing_registry_identifier")
        canonical_url = _clean(_mapping(object_.get("links")).get("canonical"))
        if not canonical_url:
            reasons.append("missing_canonical_url")
        if preferred is None and registry_id:
            preferred = {
                "scheme": registry or "registry",
                "value": registry_id,
                "url": canonical_url,
            }
            links = [preferred]
    elif object_type in {"drug", "target", "dataset"}:
        kind = "database_record"
        identifiers = _mapping(object_.get("identifiers"))
        if not any(_clean(value) for value in identifiers.values()):
            reasons.append("missing_database_identifier")
        canonical_url = _clean(_mapping(object_.get("links")).get("canonical"))
        if not canonical_url:
            reasons.append("missing_canonical_url")
        if preferred is None and identifiers:
            scheme, value = next(
                (
                    (str(key), _clean(raw))
                    for key, raw in identifiers.items()
                    if _clean(raw)
                ),
                ("database", ""),
            )
            if value:
                preferred = {"scheme": scheme, "value": value, "url": canonical_url}
                links = [preferred]
    else:
        reasons.append("unknown_object_type")

    return {
        "eligible": not reasons,
        "kind": kind if not reasons else "candidate_only",
        "preferred_identifier": preferred,
        "links": links,
        "reason_codes": reasons,
    }


def _content_level(content: Mapping[str, Any]) -> str:
    abstract = _mapping(content.get("abstract"))
    full_text = _mapping(content.get("full_text"))
    if (
        full_text.get("retrieval_status") == "retrieved"
        and full_text.get("inspection_status")
        in {"partially_inspected", "inspected"}
    ):
        return "full_text"
    if abstract.get("status") == "available" and _clean(abstract.get("text")):
        return "abstract"
    return "metadata"


def _validate_content_support(
    content: Any, path: str, errors: list[str]
) -> None:
    if not isinstance(content, Mapping):
        errors.append(f"{path} must be an object")
        return
    metadata = _mapping(content.get("metadata"))
    abstract = _mapping(content.get("abstract"))
    full_text = _mapping(content.get("full_text"))
    if metadata.get("status") not in METADATA_STATUSES:
        errors.append(f"{path}.metadata.status is invalid")
    if abstract.get("status") not in ABSTRACT_STATUSES:
        errors.append(f"{path}.abstract.status is invalid")
    if abstract.get("status") == "available" and not _clean(abstract.get("text")):
        errors.append(f"{path}.abstract.text is required when abstract is available")
    if abstract.get("status") != "available" and _clean(abstract.get("text")):
        errors.append(f"{path}.abstract.text requires status=available")
    if full_text.get("availability") not in FULL_TEXT_AVAILABILITY:
        errors.append(f"{path}.full_text.availability is invalid")
    if full_text.get("retrieval_status") not in FULL_TEXT_RETRIEVAL:
        errors.append(f"{path}.full_text.retrieval_status is invalid")
    if full_text.get("inspection_status") not in FULL_TEXT_INSPECTION:
        errors.append(f"{path}.full_text.inspection_status is invalid")
    if (
        full_text.get("inspection_status") != "not_inspected"
        and full_text.get("retrieval_status") != "retrieved"
    ):
        errors.append(f"{path}.full_text inspection requires retrieved content")
    if full_text.get("availability") == "open" and not _clean(full_text.get("url")):
        errors.append(f"{path}.full_text.url is required when availability=open")
    if full_text.get("retrieval_status") == "retrieved" and not (
        _clean(full_text.get("url")) or _sequence(full_text.get("source_refs"))
    ):
        errors.append(f"{path}.full_text retrieved content needs source provenance")
    expected_level = _content_level(content)
    if content.get("highest_inspected") != expected_level:
        errors.append(
            f"{path}.highest_inspected must be {expected_level!r} for its content state"
        )


def _required(value: Any, path: str, errors: list[str]) -> None:
    if not _clean(value):
        errors.append(f"{path} is required")


def _is_array(value: Any) -> bool:
    return isinstance(value, list)


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _validate_string_array(value: Any, path: str, errors: list[str]) -> list[str]:
    if not _is_array(value):
        errors.append(f"{path} must be an array")
        return []
    values: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not _clean(item):
            errors.append(f"{path}[{index}] must be a non-empty string")
            continue
        values.append(_clean(item))
    return values


def _validate_run_and_request(
    bundle: Mapping[str, Any], errors: list[str]
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    run_value = bundle.get("run")
    if not isinstance(run_value, Mapping):
        errors.append("run must be an object")
        run: Mapping[str, Any] = {}
    else:
        run = run_value
        for field in ("id", "tool_version", "created_at"):
            _required(run.get(field), f"run.{field}", errors)
        if run.get("retrieval_state") not in RETRIEVAL_STATES:
            errors.append("run.retrieval_state is invalid")
        if run.get("scenario") not in SCENARIOS:
            errors.append("run.scenario is invalid")
        if run.get("depth") not in DEPTHS:
            errors.append("run.depth is invalid")
        _validate_string_array(run.get("warnings"), "run.warnings", errors)

    request_value = bundle.get("request")
    if not isinstance(request_value, Mapping):
        errors.append("request must be an object")
        request: Mapping[str, Any] = {}
    else:
        request = request_value
        if not isinstance(request.get("question"), str):
            errors.append("request.question must be a string")
        if request.get("depth") not in DEPTHS:
            errors.append("request.depth is invalid")
        primary = request.get("primary_scenario")
        if primary not in SCENARIOS:
            errors.append("request.primary_scenario is invalid")
        scenarios = _validate_string_array(
            request.get("scenarios"), "request.scenarios", errors
        )
        for index, scenario in enumerate(scenarios):
            if scenario not in SCENARIOS:
                errors.append(f"request.scenarios[{index}] is invalid")
        if primary in SCENARIOS and primary not in scenarios:
            errors.append("request.primary_scenario must be present in request.scenarios")

        concepts = request.get("concepts")
        if not _is_array(concepts):
            errors.append("request.concepts must be an array")
        else:
            for index, concept in enumerate(concepts):
                path = f"request.concepts[{index}]"
                if not isinstance(concept, Mapping):
                    errors.append(f"{path} must be an object")
                    continue
                _required(concept.get("type"), f"{path}.type", errors)
                if not isinstance(concept.get("input"), str):
                    errors.append(f"{path}.input must be a string")
                else:
                    _required(concept.get("input"), f"{path}.input", errors)
                for field in ("synonyms", "descendants"):
                    if field in concept:
                        _validate_string_array(
                            concept.get(field), f"{path}.{field}", errors
                        )

        constraints = request.get("constraints")
        if not isinstance(constraints, Mapping):
            errors.append("request.constraints must be an object")
        else:
            for field in ("year_from", "year_to"):
                value = constraints.get(field)
                if value is not None and (
                    not isinstance(value, int) or isinstance(value, bool)
                ):
                    errors.append(f"request.constraints.{field} must be an integer or null")
            year_from = constraints.get("year_from")
            year_to = constraints.get("year_to")
            if (
                isinstance(year_from, int)
                and not isinstance(year_from, bool)
                and isinstance(year_to, int)
                and not isinstance(year_to, bool)
                and year_from > year_to
            ):
                errors.append("request.constraints.year_from must not exceed year_to")
            for field in CONSTRAINT_SEQUENCE_FIELDS:
                _validate_string_array(
                    constraints.get(field), f"request.constraints.{field}", errors
                )
            for field in CONSTRAINT_BOOLEAN_FIELDS:
                if not isinstance(constraints.get(field), bool):
                    errors.append(f"request.constraints.{field} must be a boolean")

        enum_fields = {
            "deliverable": DELIVERABLES,
            "output_language": OUTPUT_LANGUAGES,
            "sort": SORT_ORDERS,
            "expansion": EXPANSION_MODES,
        }
        for field, allowed in enum_fields.items():
            if request.get(field) not in allowed:
                errors.append(f"request.{field} is invalid")
        for field in ("normalize", "include_descendants", "dry_run"):
            if not isinstance(request.get(field), bool):
                errors.append(f"request.{field} must be a boolean")
        for field in ("source_override", "query_variants", "web_result_files"):
            _validate_string_array(request.get(field), f"request.{field}", errors)

    if run and request:
        if run.get("scenario") != request.get("primary_scenario"):
            errors.append("run.scenario must match request.primary_scenario")
        if run.get("depth") != request.get("depth"):
            errors.append("run.depth must match request.depth")
    return run, request


def _validate_ledger_counter(
    value: Any, path: str, errors: list[str]
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{path} must be an object")
        return {}
    for field in LEDGER_COUNT_FIELDS:
        if not _is_nonnegative_int(value.get(field)):
            errors.append(f"{path}.{field} must be a non-negative integer")
    return value


def _validate_plan_and_routes(
    retrieval: Mapping[str, Any],
    request: Mapping[str, Any],
    errors: list[str],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, Mapping[str, Any]]]:
    plan = retrieval.get("plan")
    lane_index: dict[str, Mapping[str, Any]] = {}
    if not _is_array(plan):
        errors.append("retrieval.plan must be an array")
        plan = []
    for index, lane in enumerate(plan):
        path = f"retrieval.plan[{index}]"
        if not isinstance(lane, Mapping):
            errors.append(f"{path} must be an object")
            continue
        lane_id = _clean(lane.get("id"))
        _required(lane_id, f"{path}.id", errors)
        if lane_id in lane_index:
            errors.append(f"duplicate retrieval plan lane id: {lane_id}")
        if lane_id:
            lane_index[lane_id] = lane
        if lane.get("scenario") not in SCENARIOS:
            errors.append(f"{path}.scenario is invalid")
        elif lane.get("scenario") not in _sequence(request.get("scenarios")):
            errors.append(f"{path}.scenario is absent from request.scenarios")
        for field in ("purpose", "query", "family", "evidence_dimension"):
            _required(lane.get(field), f"{path}.{field}", errors)
        sources = _validate_string_array(lane.get("sources"), f"{path}.sources", errors)
        if not sources:
            errors.append(f"{path}.sources must not be empty")
        if not _is_nonnegative_int(lane.get("requested_limit")) or lane.get(
            "requested_limit"
        ) == 0:
            errors.append(f"{path}.requested_limit must be a positive integer")
        _required(lane.get("run_condition"), f"{path}.run_condition", errors)
        for field in ("required_concepts", "notes"):
            if field in lane:
                _validate_string_array(lane.get(field), f"{path}.{field}", errors)

    routes = retrieval.get("routes")
    route_index: dict[str, Mapping[str, Any]] = {}
    if not _is_array(routes):
        errors.append("retrieval.routes must be an array")
        routes = []
    for index, route in enumerate(routes):
        path = f"retrieval.routes[{index}]"
        if not isinstance(route, Mapping):
            errors.append(f"{path} must be an object")
            continue
        source = _clean(route.get("source"))
        _required(source, f"{path}.source", errors)
        if source in route_index:
            errors.append(f"duplicate retrieval route source: {source}")
        if source:
            route_index[source] = route
        _required(route.get("role"), f"{path}.role", errors)
        _required(route.get("activation_reason"), f"{path}.activation_reason", errors)
        route_scenarios = _validate_string_array(
            route.get("scenarios"), f"{path}.scenarios", errors
        )
        for scenario_index, scenario in enumerate(route_scenarios):
            if scenario not in SCENARIOS:
                errors.append(f"{path}.scenarios[{scenario_index}] is invalid")
            elif scenario not in _sequence(request.get("scenarios")):
                errors.append(
                    f"{path}.scenarios[{scenario_index}] is absent from request.scenarios"
                )
        lane_ids = _validate_string_array(
            route.get("lane_ids"), f"{path}.lane_ids", errors
        )
        if "constraint_support" in route and not isinstance(
            route.get("constraint_support"), Mapping
        ):
            errors.append(f"{path}.constraint_support must be an object")
        for lane_id in lane_ids:
            if lane_id not in lane_index:
                errors.append(f"{path}.lane_ids references unknown lane {lane_id!r}")
                continue
            if source not in _sequence(lane_index[lane_id].get("sources")):
                errors.append(
                    f"{path} routes {lane_id!r} to a source absent from the lane"
                )

    for lane_id, lane in lane_index.items():
        for source in _sequence(lane.get("sources")):
            route = route_index.get(str(source))
            if route is None or lane_id not in _sequence(route.get("lane_ids")):
                errors.append(
                    f"retrieval.plan lane {lane_id!r} has no matching route for source {source!r}"
                )
    return lane_index, route_index


def _empty_counter() -> dict[str, int]:
    return {field: 0 for field in LEDGER_COUNT_FIELDS}


def _validate_statuses_and_ledger(
    retrieval: Mapping[str, Any],
    lane_index: Mapping[str, Mapping[str, Any]],
    route_index: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> None:
    statuses = retrieval.get("source_status")
    if not _is_array(statuses):
        errors.append("retrieval.source_status must be an array")
        statuses = []
    status_counts = {status: 0 for status in SOURCE_RUN_STATUSES}
    family_counts: dict[str, dict[str, int]] = {}
    lane_counts: dict[str, dict[str, int]] = {}
    count_field_for_status = {
        "ok": "successful",
        "error": "failed",
        "skipped": "skipped",
        "not_run": "not_run",
    }
    for index, status in enumerate(statuses):
        path = f"retrieval.source_status[{index}]"
        if not isinstance(status, Mapping):
            errors.append(f"{path} must be an object")
            continue
        source = _clean(status.get("source"))
        _required(source, f"{path}.source", errors)
        state = status.get("status")
        if state not in SOURCE_RUN_STATUSES:
            errors.append(f"{path}.status is invalid")
            continue
        status_counts[state] += 1
        family = _clean(status.get("query_family"))
        lane_id = _clean(status.get("query_lane"))
        _required(family, f"{path}.query_family", errors)
        _required(lane_id, f"{path}.query_lane", errors)
        for field in ("requested_limit", "received", "accepted", "reported_total"):
            value = status.get(field)
            if value is not None and not _is_nonnegative_int(value):
                errors.append(f"{path}.{field} must be a non-negative integer or null")
        truncated = status.get("truncated")
        if truncated is not None and not isinstance(truncated, bool):
            errors.append(f"{path}.truncated must be a boolean or null")
        for key, table in ((family, family_counts), (lane_id, lane_counts)):
            if not key:
                continue
            counter = table.setdefault(key, _empty_counter())
            counter["runs"] += 1
            counter[count_field_for_status[state]] += 1
        if lane_id in lane_index:
            lane = lane_index[lane_id]
            if source not in _sequence(lane.get("sources")):
                errors.append(f"{path}.source is not permitted by lane {lane_id!r}")
            route = route_index.get(source)
            if route is None or lane_id not in _sequence(route.get("lane_ids")):
                errors.append(f"{path} has no matching route for lane {lane_id!r}")
        elif _clean(status.get("query_origin")).startswith("scenario:"):
            errors.append(f"{path}.query_lane references unknown planned lane {lane_id!r}")

    ledger = retrieval.get("ledger")
    if not isinstance(ledger, Mapping):
        errors.append("retrieval.ledger must be an object")
        return
    expected_totals = {
        "run_count": len(statuses),
        "successful_runs": status_counts["ok"],
        "failed_runs": status_counts["error"],
        "skipped_runs": status_counts["skipped"],
        "not_run": status_counts["not_run"],
    }
    for field, expected in expected_totals.items():
        if ledger.get(field) != expected:
            errors.append(f"retrieval.ledger.{field} must equal {expected}")
    if ledger.get("details_field") != "source_status":
        errors.append("retrieval.ledger.details_field must be 'source_status'")
    for field, expected_table in (
        ("query_families", family_counts),
        ("query_lanes", lane_counts),
    ):
        actual_table = ledger.get(field)
        if not isinstance(actual_table, Mapping):
            errors.append(f"retrieval.ledger.{field} must be an object")
            continue
        for key in actual_table:
            if key not in expected_table:
                errors.append(
                    f"retrieval.ledger.{field} contains unknown audit key {key!r}"
                )
                _validate_ledger_counter(
                    actual_table.get(key), f"retrieval.ledger.{field}.{key}", errors
                )
        for key, expected in expected_table.items():
            counter = _validate_ledger_counter(
                actual_table.get(key), f"retrieval.ledger.{field}.{key}", errors
            )
            for count_field, expected_count in expected.items():
                if counter and counter.get(count_field) != expected_count:
                    errors.append(
                        f"retrieval.ledger.{field}.{key}.{count_field} "
                        f"must equal {expected_count}"
                    )


def _validate_retrieval(
    bundle: Mapping[str, Any],
    request: Mapping[str, Any],
    errors: list[str],
) -> None:
    retrieval_value = bundle.get("retrieval")
    if not isinstance(retrieval_value, Mapping):
        errors.append("retrieval must be an object")
        return
    lane_index, route_index = _validate_plan_and_routes(
        retrieval_value, request, errors
    )
    _validate_statuses_and_ledger(
        retrieval_value, lane_index, route_index, errors
    )
    source_summary = retrieval_value.get("source_summary")
    if source_summary is not None:
        if not isinstance(source_summary, Mapping):
            errors.append("retrieval.source_summary must be an object")
        else:
            categories = (
                "successful",
                "partial",
                "failed",
                "skipped",
                "not_run",
            )
            summarized: list[str] = []
            for category in categories:
                summarized.extend(
                    _validate_string_array(
                        source_summary.get(category),
                        f"retrieval.source_summary.{category}",
                        errors,
                    )
                )
            if len(summarized) != len(set(summarized)):
                errors.append(
                    "retrieval.source_summary categories must be mutually exclusive"
                )
            status_sources = {
                _clean(value.get("source"))
                for value in _sequence(retrieval_value.get("source_status"))
                if isinstance(value, Mapping) and _clean(value.get("source"))
            }
            if set(summarized) != status_sources:
                errors.append(
                    "retrieval.source_summary must classify every source_status source exactly once"
                )
    bounded = retrieval_value.get("bounded")
    if not isinstance(bounded, Mapping):
        errors.append("retrieval.bounded must be an object")
        return
    if not isinstance(bounded.get("exhaustive"), bool):
        errors.append("retrieval.bounded.exhaustive must be a boolean")
    for field in (
        "per_source_record_cap",
        "per_lane_request_cap",
        "max_calls_per_source",
        "planned_source_operations",
        "final_result_limit",
        "weak_result_threshold",
    ):
        if field in bounded and not _is_nonnegative_int(bounded.get(field)):
            errors.append(f"retrieval.bounded.{field} must be a non-negative integer")
    retrieved_at = bounded.get("retrieved_at")
    if "retrieved_at" in bounded and retrieved_at is not None and not isinstance(
        retrieved_at, str
    ):
        errors.append("retrieval.bounded.retrieved_at must be a string or null")


def _validate_object(
    object_: Any,
    expected_type: str,
    path: str,
    errors: list[str],
) -> None:
    if not isinstance(object_, Mapping):
        errors.append(f"{path} must be an object")
        return
    object_type = _clean(object_.get("type"))
    if object_type != expected_type:
        errors.append(f"{path}.type must be {expected_type!r}")
    object_id = _clean(object_.get("id"))
    _required(object_id, f"{path}.id", errors)
    if object_id and not object_id.startswith(f"{expected_type}:"):
        errors.append(f"{path}.id must start with {expected_type!r} prefix")
    for field in FORBIDDEN_FIELDS.get(expected_type, set()):
        if field in object_:
            errors.append(
                f"{path}.{field} violates the {expected_type} object boundary; use a relation"
            )

    if expected_type == "paper":
        _required(object_.get("title") or object_.get("label"), f"{path}.title", errors)
        if not isinstance(object_.get("identifiers"), Mapping):
            errors.append(f"{path}.identifiers must be an object")
        _validate_content_support(object_.get("content_support"), f"{path}.content_support", errors)
    elif expected_type == "trial":
        _required(object_.get("registry"), f"{path}.registry", errors)
        _required(object_.get("registry_id"), f"{path}.registry_id", errors)
        _required(object_.get("title") or object_.get("label"), f"{path}.title", errors)
    elif expected_type == "drug":
        _required(
            object_.get("preferred_name") or object_.get("label"),
            f"{path}.preferred_name",
            errors,
        )
    elif expected_type == "target":
        _required(
            object_.get("symbol") or object_.get("name") or object_.get("label"),
            f"{path}.name",
            errors,
        )
    elif expected_type == "dataset":
        _required(object_.get("title") or object_.get("label"), f"{path}.title", errors)
        if not (
            _clean(object_.get("accession"))
            or any(_clean(value) for value in _mapping(object_.get("identifiers")).values())
        ):
            errors.append(f"{path} needs an accession or stable database identifier")

    source_refs = object_.get("source_refs")
    if not isinstance(source_refs, Sequence) or isinstance(
        source_refs, (str, bytes, bytearray)
    ):
        errors.append(f"{path}.source_refs must be an array")
    else:
        source_ref_ids: list[str] = []
        for index, source_ref in enumerate(source_refs):
            source_ref_path = f"{path}.source_refs[{index}]"
            if not isinstance(source_ref, Mapping):
                errors.append(f"{source_ref_path} must be an object")
                continue
            source_ref_id = _clean(source_ref.get("id"))
            _required(source_ref_id, f"{source_ref_path}.id", errors)
            _required(source_ref.get("source"), f"{source_ref_path}.source", errors)
            if source_ref_id:
                source_ref_ids.append(source_ref_id)
        if len(source_ref_ids) != len(set(source_ref_ids)):
            errors.append(f"{path}.source_refs contains duplicate ids")

    actual_citation = _mapping(object_.get("citation"))
    expected_citation = citation_eligibility_for(object_)
    if actual_citation.get("eligible") is not expected_citation["eligible"]:
        errors.append(f"{path}.citation.eligible is inconsistent with object metadata")
    if actual_citation.get("kind") != expected_citation["kind"]:
        errors.append(f"{path}.citation.kind is inconsistent with object metadata")


def collect_validation_errors(bundle: Any) -> list[str]:
    """Collect every schema error instead of failing at the first one."""

    errors: list[str] = []
    if not isinstance(bundle, Mapping):
        return ["bundle must be an object"]
    if bundle.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    if bundle.get("artifact_type") != ARTIFACT_TYPE:
        errors.append(f"artifact_type must be {ARTIFACT_TYPE!r}")

    _, request = _validate_run_and_request(bundle, errors)
    _validate_retrieval(bundle, request, errors)

    objects = bundle.get("objects")
    if not isinstance(objects, Mapping):
        errors.append("objects must be an object")
        objects = {}
    object_index: dict[str, Mapping[str, Any]] = {}
    object_types: dict[str, str] = {}
    for collection, object_type in OBJECT_COLLECTIONS.items():
        values = objects.get(collection)
        if not isinstance(values, list):
            errors.append(f"objects.{collection} must be an array")
            continue
        for index, object_ in enumerate(values):
            path = f"objects.{collection}[{index}]"
            _validate_object(object_, object_type, path, errors)
            if not isinstance(object_, Mapping):
                continue
            object_id = _clean(object_.get("id"))
            if not object_id:
                continue
            if object_id in object_index:
                errors.append(f"duplicate object id: {object_id}")
            object_index[object_id] = object_
            object_types[object_id] = object_type

    relation_ids: set[str] = set()
    relations = bundle.get("relations")
    if not isinstance(relations, list):
        errors.append("relations must be an array")
        relations = []
    for index, relation in enumerate(relations):
        path = f"relations[{index}]"
        if not isinstance(relation, Mapping):
            errors.append(f"{path} must be an object")
            continue
        relation_id = _clean(relation.get("id"))
        _required(relation_id, f"{path}.id", errors)
        if relation_id in relation_ids:
            errors.append(f"duplicate relation id: {relation_id}")
        relation_ids.add(relation_id)
        _required(relation.get("predicate"), f"{path}.predicate", errors)
        for field in ("subject_id", "object_id"):
            reference = _clean(relation.get(field))
            _required(reference, f"{path}.{field}", errors)
            if reference and reference not in object_index and not reference.startswith(
                "concept:"
            ):
                errors.append(f"{path}.{field} references unknown object {reference!r}")
        for evidence_index, evidence in enumerate(_sequence(relation.get("evidence_refs"))):
            if not isinstance(evidence, Mapping):
                errors.append(f"{path}.evidence_refs[{evidence_index}] must be an object")
                continue
            object_id = _clean(evidence.get("object_id"))
            if object_id and object_id not in object_index:
                errors.append(
                    f"{path}.evidence_refs[{evidence_index}] references unknown object {object_id!r}"
                )

    result_set_ids: set[str] = set()
    result_sets = bundle.get("result_sets")
    if not isinstance(result_sets, list):
        errors.append("result_sets must be an array")
        result_sets = []
    for index, result_set in enumerate(result_sets):
        path = f"result_sets[{index}]"
        if not isinstance(result_set, Mapping):
            errors.append(f"{path} must be an object")
            continue
        result_set_id = _clean(result_set.get("id"))
        _required(result_set_id, f"{path}.id", errors)
        if result_set_id in result_set_ids:
            errors.append(f"duplicate result set id: {result_set_id}")
        result_set_ids.add(result_set_id)
        object_type = _clean(result_set.get("object_type"))
        if object_type not in OBJECT_TYPES:
            errors.append(f"{path}.object_type is invalid")
        seen_refs: set[str] = set()
        refs = result_set.get("ordered_object_ids")
        if not isinstance(refs, list):
            errors.append(f"{path}.ordered_object_ids must be an array")
            continue
        for reference in refs:
            object_id = _clean(reference)
            if object_id in seen_refs:
                errors.append(f"{path} repeats object {object_id!r}")
            seen_refs.add(object_id)
            if object_id not in object_index:
                errors.append(f"{path} references unknown object {object_id!r}")
            elif object_types[object_id] != object_type:
                errors.append(f"{path} mixes {object_types[object_id]!r} into {object_type!r}")

    synthesis = bundle.get("synthesis")
    if not isinstance(synthesis, Mapping):
        errors.append("synthesis must be an object")
        synthesis = {}
    if synthesis.get("status") not in {"not_generated", "partial", "generated"}:
        errors.append("synthesis.status is invalid")
    claim_ids: set[str] = set()
    claims = synthesis.get("claims")
    if not isinstance(claims, list):
        errors.append("synthesis.claims must be an array")
        claims = []
    for index, claim in enumerate(claims):
        path = f"synthesis.claims[{index}]"
        if not isinstance(claim, Mapping):
            errors.append(f"{path} must be an object")
            continue
        claim_id = _clean(claim.get("id"))
        _required(claim_id, f"{path}.id", errors)
        if claim_id in claim_ids:
            errors.append(f"duplicate claim id: {claim_id}")
        claim_ids.add(claim_id)
        _required(claim.get("kind"), f"{path}.kind", errors)
        text = claim.get("text")
        if not isinstance(text, Mapping) or not any(
            _clean(text.get(language)) for language in ("zh", "en")
        ):
            errors.append(f"{path}.text needs zh and/or en content")
        basis = claim.get("basis")
        if basis not in MODEL_BASES:
            errors.append(f"{path}.basis is invalid")
        if claim.get("method") not in CLAIM_METHODS:
            errors.append(f"{path}.method is invalid")
        support_level = claim.get("support_level")
        if support_level not in CLAIM_SUPPORT_LEVELS:
            errors.append(f"{path}.support_level is invalid")
        evidence_refs = claim.get("evidence")
        if not isinstance(evidence_refs, list):
            errors.append(f"{path}.evidence must be an array")
            evidence_refs = []
        if basis == "retrieved_evidence" and not evidence_refs:
            errors.append(f"{path} retrieved evidence claim needs at least one evidence reference")
        if basis in {"model_background", "user_context"} and evidence_refs:
            errors.append(f"{path} {basis} must not masquerade as retrieved evidence")
        for evidence_index, evidence in enumerate(evidence_refs):
            evidence_path = f"{path}.evidence[{evidence_index}]"
            if not isinstance(evidence, Mapping):
                errors.append(f"{evidence_path} must be an object")
                continue
            object_id = _clean(evidence.get("object_id"))
            if object_id not in object_index:
                errors.append(f"{evidence_path} references unknown object {object_id!r}")
                continue
            object_ = object_index[object_id]
            if not _mapping(object_.get("citation")).get("eligible"):
                errors.append(f"{evidence_path} cites an ineligible candidate object")
            if object_types[object_id] == "paper" and support_level in CONTENT_LEVELS:
                available_level = _content_level(_mapping(object_.get("content_support")))
                if CONTENT_LEVELS.index(available_level) < CONTENT_LEVELS.index(
                    support_level
                ):
                    errors.append(
                        f"{evidence_path} claims {support_level} support but paper only has {available_level}"
                    )
            if support_level == "database" and object_types[object_id] == "paper":
                errors.append(f"{evidence_path} database support cannot cite a paper object")
            if support_level == "full_text":
                locator = _mapping(evidence.get("locator"))
                if not _clean(locator.get("kind")) or not _clean(locator.get("value")):
                    errors.append(f"{evidence_path} full-text support requires a locator")

    sections = synthesis.get("sections")
    if not isinstance(sections, list):
        errors.append("synthesis.sections must be an array")
        sections = []
    for index, section in enumerate(sections):
        if not isinstance(section, Mapping):
            errors.append(f"synthesis.sections[{index}] must be an object")
            continue
        for claim_id in _sequence(section.get("claim_ids")):
            if claim_id not in claim_ids:
                errors.append(
                    f"synthesis.sections[{index}] references unknown claim {claim_id!r}"
                )

    for list_name in ("reading_order", "research_groups"):
        values = synthesis.get(list_name)
        if not isinstance(values, list):
            errors.append(f"synthesis.{list_name} must be an array")
            continue
        for index, value in enumerate(values):
            if not isinstance(value, Mapping):
                errors.append(f"synthesis.{list_name}[{index}] must be an object")
                continue
            refs = value.get("object_ids")
            if refs is None and value.get("object_id") is not None:
                refs = [value.get("object_id")]
            for object_id in _sequence(refs):
                if object_id not in object_index:
                    errors.append(
                        f"synthesis.{list_name}[{index}] references unknown object {object_id!r}"
                    )

    gaps = synthesis.get("gaps")
    if not isinstance(gaps, list):
        errors.append("synthesis.gaps must be an array")
    else:
        for index, gap in enumerate(gaps):
            if isinstance(gap, str) and gap not in claim_ids:
                errors.append(f"synthesis.gaps[{index}] references unknown claim {gap!r}")

    counts = bundle.get("counts")
    if not isinstance(counts, Mapping):
        errors.append("counts must be an object")
    else:
        for collection in OBJECT_COLLECTIONS:
            expected = len(_sequence(objects.get(collection)))
            if counts.get(collection) != expected:
                errors.append(f"counts.{collection} must equal {expected}")
        if counts.get("relations") != len(relations):
            errors.append(f"counts.relations must equal {len(relations)}")
        total_objects = sum(len(_sequence(objects.get(value))) for value in OBJECT_COLLECTIONS)
        if counts.get("total_objects") != total_objects:
            errors.append(f"counts.total_objects must equal {total_objects}")

    return errors


def validate_bundle(bundle: Any) -> None:
    """Raise :class:`SchemaValidationError` when *bundle* is invalid."""

    errors = collect_validation_errors(bundle)
    if errors:
        raise SchemaValidationError(errors)
