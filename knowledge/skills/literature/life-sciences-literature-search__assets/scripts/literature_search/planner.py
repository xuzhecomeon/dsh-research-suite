"""Scenario detection, plan assembly, source routing, and plan validation."""

from __future__ import annotations

import dataclasses
from collections import defaultdict
from typing import Iterable

from .budgets import budget_for
from .models import (
    DELIVERABLES,
    DEPTHS,
    OUTPUT_LANGUAGES,
    SCENARIOS,
    QueryLane,
    SearchBudget,
    SearchPlan,
    SearchRequest,
    SourceRoute,
)
from .scenarios import (
    Detection,
    canonical_scenario,
    detect_primary_scenario,
    detect_scenarios,
    planner_for,
)
from .scenarios.base import combine, term_group
from .source_packs import SOURCE_ROLES, source_pack_for


AUTO_SCENARIOS = {"", "auto"}
CORE_SOURCES = ("europepmc", "pubmed", "semantic-scholar", "openalex")
HUMAN_ONLY_BACKEND_SOURCES = {"reactome", "uniprot"}
HUMAN_SPECIES_MARKERS = (
    "human",
    "humans",
    "homo sapiens",
    "ncbitaxon:9606",
    "taxon:9606",
    "9606",
    "人类",
)


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if value))


def _resolved_request(request: SearchRequest) -> SearchRequest:
    if not request.question.strip():
        raise ValueError("question must not be empty")
    explicit: list[str] = []
    for scenario in request.scenarios:
        if scenario.strip().casefold() in AUTO_SCENARIOS:
            continue
        explicit.append(canonical_scenario(scenario))
    primary_raw = request.primary_scenario.strip().casefold()
    if primary_raw in AUTO_SCENARIOS:
        primary = explicit[0] if explicit else detect_primary_scenario(
            request.question, request.concepts
        )
    else:
        primary = canonical_scenario(primary_raw)
    scenarios = _unique((primary, *explicit))
    return dataclasses.replace(
        request,
        question=" ".join(request.question.split()),
        scenarios=scenarios,
        primary_scenario=primary,
    )


def _validate_request(request: SearchRequest) -> None:
    errors: list[str] = []
    if request.depth not in DEPTHS:
        errors.append(f"unknown depth: {request.depth}")
    if request.primary_scenario not in SCENARIOS:
        errors.append(f"unknown primary scenario: {request.primary_scenario}")
    unknown_scenarios = [value for value in request.scenarios if value not in SCENARIOS]
    if unknown_scenarios:
        errors.append(f"unknown scenarios: {', '.join(unknown_scenarios)}")
    if request.primary_scenario not in request.scenarios:
        errors.append("primary_scenario must be present in scenarios")
    if request.deliverable not in DELIVERABLES:
        errors.append(f"unknown deliverable: {request.deliverable}")
    if request.output_language not in OUTPUT_LANGUAGES:
        errors.append(f"unknown output language: {request.output_language}")
    if request.sort not in {"relevance", "newest", "citations"}:
        errors.append(f"unknown sort mode: {request.sort}")
    if request.expansion not in {"auto", "none", "related", "citations", "both"}:
        errors.append(f"unknown expansion mode: {request.expansion}")
    if request.constraints.year_from and request.constraints.year_to:
        if request.constraints.year_from > request.constraints.year_to:
            errors.append("year_from must not exceed year_to")
    if errors:
        raise ValueError("invalid search request: " + "; ".join(errors))


def _is_explicit_nonhuman_request(request: SearchRequest) -> bool:
    species = tuple(
        " ".join(value.casefold().replace("_", " ").split())
        for value in request.constraints.species
        if value.strip()
    )
    if not species:
        return False
    return not any(
        marker in value
        for value in species
        for marker in HUMAN_SPECIES_MARKERS
    )


def _select_sources(request: SearchRequest, budget: SearchBudget) -> tuple[str, ...]:
    if request.source_override:
        sources = _unique(value.strip().casefold() for value in request.source_override)
        unknown = [source for source in sources if source not in SOURCE_ROLES]
        if unknown:
            raise ValueError(f"unknown source override: {', '.join(unknown)}")
        if len(sources) > budget.max_sources:
            raise ValueError(
                f"source override contains {len(sources)} sources but {request.depth} "
                f"allows at most {budget.max_sources}"
            )
        incompatible = HUMAN_ONLY_BACKEND_SOURCES.intersection(sources)
        if incompatible and _is_explicit_nonhuman_request(request):
            raise ValueError(
                "source override is incompatible with the explicit non-human species "
                f"constraint because the current backend is human-only for: {', '.join(sorted(incompatible))}"
            )
        return sources

    ordered: list[str] = []
    for scenario in request.scenarios:
        ordered.extend(source_pack_for(scenario).sources_for(request.depth))
    selected = _unique(ordered)
    if _is_explicit_nonhuman_request(request):
        selected = tuple(
            source for source in selected if source not in HUMAN_ONLY_BACKEND_SOURCES
        )
    return selected[: budget.max_sources]


def _scenario_lane_groups(
    request: SearchRequest,
    budget: SearchBudget,
    sources: tuple[str, ...],
) -> tuple[tuple[QueryLane, ...], ...]:
    groups: list[tuple[QueryLane, ...]] = []
    for scenario in request.scenarios:
        built = planner_for(scenario).build_lanes(request, budget, sources)
        if request.source_override:
            # Explicit override is an expert instruction.  Apply its exact
            # source set to every generated lane and let adapters disclose
            # unsupported operations in the execution ledger.
            built = tuple(dataclasses.replace(item, sources=sources) for item in built)
        groups.append(built)
    if request.query_variants:
        variant_sources = tuple(source for source in CORE_SOURCES if source in sources)
        if not variant_sources:
            variant_sources = sources
        variants = tuple(
            QueryLane(
                id=f"shared.query_variant_{index}",
                scenario=request.primary_scenario,
                purpose="Run a user-curated translated or synonym query without changing its asserted meaning",
                query=" ".join(value.split()),
                family="translated_synonym",
                sources=variant_sources,
                evidence_dimension="translated_or_synonym_recall",
                requested_limit=budget.per_lane,
                notes=("The query variant is user/agent supplied and retained verbatim in the audit.",),
            )
            for index, value in enumerate(request.query_variants, start=1)
            if value.strip()
        )
        if variants:
            # Explicit variants are part of the primary scenario.  Place them
            # directly after its highest-priority lane so quick searches do not
            # silently discard a requested translation.
            primary = groups[0]
            groups[0] = (*primary[:1], *variants, *primary[1:])
    mesh_headings = request.terms_of("mesh_heading")
    mesh_subheadings = request.terms_of("mesh_subheading")
    if mesh_headings and mesh_subheadings and "pubmed" in sources:
        qualified = tuple(
            QueryLane(
                id=f"shared.mesh_qualified_{index}",
                scenario=request.primary_scenario,
                purpose="Run an explicit PubMed MeSH heading/subheading combination",
                query=f'"{heading}/{subheading}"[MeSH Terms]',
                family="entity_combination",
                sources=("pubmed",),
                evidence_dimension="mesh_qualified_query",
                requested_limit=budget.per_lane,
                required_concepts=("mesh_heading", "mesh_subheading"),
                notes=("The heading/subheading combination is explicit and source-native to PubMed.",),
            )
            for index, (heading, subheading) in enumerate(
                (
                    (heading, subheading)
                    for heading in mesh_headings[:3]
                    for subheading in mesh_subheadings[:3]
                ),
                start=1,
            )
        )
        primary = groups[0]
        groups[0] = (*primary[:1], *qualified, *primary[1:])
    species_terms = _unique(
        (*request.constraints.species, *request.terms_of("species", "organism"))
    )
    if species_terms:
        constrained_groups: list[tuple[QueryLane, ...]] = []
        for group in groups:
            constrained: list[QueryLane] = []
            for item in group:
                query_key = item.query.casefold()
                already_encoded = any(
                    term.casefold() in query_key for term in species_terms
                )
                if item.family == "exact_identifier" or already_encoded:
                    constrained.append(item)
                    continue
                constrained.append(
                    dataclasses.replace(
                        item,
                        query=combine(item.query, species_terms),
                        required_concepts=_unique(
                            (*item.required_concepts, "species")
                        ),
                    )
                )
            constrained_groups.append(tuple(constrained))
        groups = constrained_groups
    excluded_terms = _unique(
        term
        for concept in request.excluded_concepts()
        for term in concept.terms()
    )
    if excluded_terms:
        negative_clause = f"NOT {term_group(excluded_terms)}"
        groups = [
            tuple(
                item
                if item.family == "exact_identifier"
                else dataclasses.replace(
                    item,
                    query=combine(item.query, negative_clause),
                    required_concepts=_unique(
                        (*item.required_concepts, "exclusion")
                    ),
                )
                for item in group
            )
            for group in groups
        ]
    return tuple(groups)


def _allocate_lanes(
    groups: tuple[tuple[QueryLane, ...], ...], budget: SearchBudget
) -> tuple[QueryLane, ...]:
    if not groups:
        return ()
    candidates: list[QueryLane] = []
    if len(groups) == 1:
        candidates.extend(groups[0])
    else:
        # Give every explicitly requested scenario a lane before filling the
        # remaining budget in planner priority order.
        max_group = max((len(group) for group in groups), default=0)
        for index in range(max_group):
            for group in groups:
                if index < len(group):
                    candidates.append(group[index])

    selected: list[QueryLane] = []
    seen_ids: set[str] = set()
    seen_exact: set[tuple[str, str]] = set()
    for item in candidates:
        if item.id in seen_ids:
            continue
        if item.evidence_dimension == "exact_lookup":
            key = (item.query.casefold(), item.family)
            if key in seen_exact:
                continue
            seen_exact.add(key)
        selected.append(item)
        seen_ids.add(item.id)
        if len(selected) == budget.max_lanes:
            break

    selected_ids = {item.id for item in selected}
    return tuple(
        item
        for item in selected
        if item.depends_on is None or item.depends_on in selected_ids
    )


def _constraint_support(source: str, request: SearchRequest) -> dict[str, str]:
    support: dict[str, str] = {}
    constraints = request.constraints
    if constraints.year_from is not None or constraints.year_to is not None:
        support["year"] = "source_pushdown_or_bounded_post_filter"
    if constraints.publication_types or constraints.excluded_publication_types:
        support["publication_type"] = "source_pushdown_or_bounded_post_filter"
    if constraints.species:
        support["species"] = (
            "native_or_indexed" if source in {"europepmc", "pubmed", "pubtator3"}
            else "metadata_incomplete_post_filter"
        )
    if constraints.open_access:
        support["open_access"] = "source_metadata_and_post_filter"
    if constraints.require_abstract:
        support["abstract"] = "bounded_post_filter_metadata_incomplete"
    return support


def _build_routes(
    request: SearchRequest,
    lanes: tuple[QueryLane, ...],
    sources: tuple[str, ...],
) -> tuple[SourceRoute, ...]:
    routes: list[SourceRoute] = []
    for source in sources:
        source_lanes = tuple(item for item in lanes if source in item.sources)
        if not source_lanes:
            continue
        scenarios = _unique(item.scenario for item in source_lanes)
        routes.append(
            SourceRoute(
                source=source,
                role=SOURCE_ROLES[source],
                scenarios=scenarios,
                lane_ids=tuple(item.id for item in source_lanes),
                activation_reason=(
                    f"Selected for {', '.join(scenarios)} evidence dimensions: "
                    + ", ".join(_unique(item.evidence_dimension for item in source_lanes))
                ),
                constraint_support=_constraint_support(source, request),
            )
        )
    return tuple(routes)


def _ontology_packs(request: SearchRequest) -> tuple[str, ...]:
    values: list[str] = []
    for scenario in request.scenarios:
        values.extend(source_pack_for(scenario).ontology_packs)
        values.extend(planner_for(scenario).ontology_packs)
    return _unique(values)


def _output_sections(request: SearchRequest) -> tuple[str, ...]:
    return _unique(
        section
        for scenario in request.scenarios
        for section in planner_for(scenario).output_sections
    )


def _warnings(
    request: SearchRequest,
    budget: SearchBudget,
    lane_groups: tuple[tuple[QueryLane, ...], ...],
    lanes: tuple[QueryLane, ...],
    ontology_packs: tuple[str, ...],
) -> tuple[str, ...]:
    warnings: list[str] = [
        "This is bounded evidence discovery, not an exhaustive systematic review.",
        "Database and registry assertions remain distinct from publication conclusions.",
    ]
    planned = sum(len(group) for group in lane_groups)
    if planned > len(lanes):
        warnings.append(
            f"The {request.depth} budget retained {len(lanes)} of {planned} generated lanes."
        )
    elif any(len(group) >= budget.max_lanes for group in lane_groups):
        warnings.append(
            f"The {request.depth} budget retained the planner's first {len(lanes)} priority lanes at its lane cap."
        )
    if request.source_override:
        warnings.append(
            "An explicit source override replaced scenario capability routing; unsupported routes may be skipped."
        )
    if _is_explicit_nonhuman_request(request):
        warnings.append(
            "Reactome and UniProt routes were excluded because their current adapters are fixed to Homo sapiens."
        )
    if "meddra" in ontology_packs:
        warnings.append(
            "MedDRA expansion is available only when a licensed terminology pack is configured; otherwise retain literal/MeSH fallback terms."
        )
    if "inn" in ontology_packs:
        warnings.append(
            "WHO INN, brand, and development-code mappings require provenance and must not be inferred as equivalents."
        )
    if request.depth == "quick" and budget.expansion == "none":
        warnings.append("Quick depth omits citation-graph expansion by design.")
    return _unique(warnings)


def validate_plan(plan: SearchPlan) -> None:
    """Reject unsafe, internally inconsistent, or over-budget plans."""

    errors: list[str] = []
    lane_ids = [item.id for item in plan.lanes]
    lane_id_set = set(lane_ids)
    if not plan.lanes:
        errors.append("plan contains no query lanes")
    if len(lane_ids) != len(lane_id_set):
        errors.append("query lane ids must be unique")
    if len(plan.lanes) > plan.budget.max_lanes:
        errors.append("query lane count exceeds budget")
    if len(plan.routes) > plan.budget.max_sources:
        errors.append("source route count exceeds budget")
    if len(plan.sources) != len(set(plan.sources)):
        errors.append("source routes must be unique by source")

    positions = {lane_id: index for index, lane_id in enumerate(lane_ids)}
    for item in plan.lanes:
        if item.scenario not in plan.request.scenarios:
            errors.append(f"lane {item.id} belongs to an unrequested scenario")
        if not item.query.strip():
            errors.append(f"lane {item.id} has an empty query")
        if not item.sources:
            errors.append(f"lane {item.id} has no sources")
        if len(item.sources) != len(set(item.sources)):
            errors.append(f"lane {item.id} has duplicate sources")
        if not 1 <= item.requested_limit <= 50:
            errors.append(f"lane {item.id} has invalid requested_limit")
        if item.depends_on:
            if item.depends_on not in lane_id_set:
                errors.append(f"lane {item.id} has a missing dependency")
            elif item.depends_on == item.id:
                errors.append(f"lane {item.id} depends on itself")
            elif positions[item.depends_on] >= positions[item.id]:
                errors.append(f"lane {item.id} dependency must precede it")
            if item.run_condition == "always":
                errors.append(f"lane {item.id} has a dependency but no run condition")

    routed: dict[str, set[str]] = defaultdict(set)
    for route in plan.routes:
        if route.source not in SOURCE_ROLES:
            errors.append(f"route uses unknown source {route.source}")
        if not route.lane_ids:
            errors.append(f"route {route.source} has no lanes")
        unknown = [lane_id for lane_id in route.lane_ids if lane_id not in lane_id_set]
        if unknown:
            errors.append(
                f"route {route.source} references unknown lanes: {', '.join(unknown)}"
            )
        for lane_id in route.lane_ids:
            routed[lane_id].add(route.source)

    for item in plan.lanes:
        expected = set(item.sources)
        actual = routed.get(item.id, set())
        if actual != expected:
            errors.append(
                f"lane {item.id} route mismatch: expected {sorted(expected)}, got {sorted(actual)}"
            )

    if not plan.ontology_packs:
        errors.append("plan contains no ontology packs")
    if not plan.output_sections:
        errors.append("plan contains no output sections")
    if errors:
        raise ValueError("invalid search plan: " + "; ".join(errors))


def build_plan(
    request: SearchRequest,
    *,
    budget: SearchBudget | None = None,
) -> SearchPlan:
    resolved = _resolved_request(request)
    _validate_request(resolved)
    effective_budget = budget or budget_for(
        resolved.depth,
        expansion=None if resolved.expansion == "auto" else resolved.expansion,
    )
    if effective_budget.depth != resolved.depth:
        raise ValueError("budget depth must match request depth")
    sources = _select_sources(resolved, effective_budget)
    lane_groups = _scenario_lane_groups(resolved, effective_budget, sources)
    lanes = _allocate_lanes(lane_groups, effective_budget)
    routes = _build_routes(resolved, lanes, sources)
    ontologies = _ontology_packs(resolved)
    plan = SearchPlan(
        request=resolved,
        budget=effective_budget,
        lanes=lanes,
        routes=routes,
        ontology_packs=ontologies,
        output_sections=_output_sections(resolved),
        warnings=_warnings(
            resolved, effective_budget, lane_groups, lanes, ontologies
        ),
    )
    validate_plan(plan)
    return plan


plan_search = build_plan


__all__ = [
    "Detection",
    "build_plan",
    "detect_primary_scenario",
    "detect_scenarios",
    "plan_search",
    "validate_plan",
]
