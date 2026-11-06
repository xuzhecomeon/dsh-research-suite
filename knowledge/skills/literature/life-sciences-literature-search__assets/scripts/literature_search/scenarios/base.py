"""Shared helpers and protocol for scenario-specific query planners."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Protocol

from ..models import Concept, QueryLane, SearchBudget, SearchRequest


CORE_SOURCES = ("europepmc", "pubmed", "semantic-scholar", "openalex")
EXACT_IDENTIFIER_RE = re.compile(
    r"(?:\b(?:PMID\s*:?\s*\d+|PMC\d+|NCT\d{8}|rs\d+)\b|"
    r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+|"
    r"\b(?:NM|NP|NC|NG|NR|ENST|ENSP)_\d+(?:\.\d+)?(?::[cgmnpr]\.[^\s,;]+)?)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Detection:
    """One auditable scenario-detection score."""

    scenario: str
    score: int
    reasons: tuple[str, ...] = ()


class ScenarioPlanner(Protocol):
    scenario: str
    ontology_packs: tuple[str, ...]
    output_sections: tuple[str, ...]

    def detect(self, question: str, concepts: tuple[Concept, ...]) -> Detection:
        ...

    def build_lanes(
        self,
        request: SearchRequest,
        budget: SearchBudget,
        available_sources: tuple[str, ...],
    ) -> tuple[QueryLane, ...]:
        ...


def unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value.strip() for value in values if value.strip()))


def concepts_of(request: SearchRequest, *types: str) -> tuple[Concept, ...]:
    return request.concepts_of(*types)


def concept_terms(request: SearchRequest, *types: str, limit: int = 12) -> tuple[str, ...]:
    return unique(
        term
        for concept in concepts_of(request, *types)
        for term in concept.terms()
    )[:limit]


def all_concept_terms(request: SearchRequest, limit: int = 16) -> tuple[str, ...]:
    return unique(
        term
        for concept in request.concepts
        if (concept.role or "").casefold() != "exclude"
        for term in concept.terms()
    )[:limit]


def quote_term(value: str) -> str:
    clean = " ".join(value.replace('"', " ").split())
    if not clean:
        return ""
    if re.fullmatch(r"[A-Za-z0-9_.:+>*/-]+", clean):
        return clean
    return f'"{clean}"'


def term_group(values: Iterable[str], limit: int = 8) -> str:
    rendered = unique(quote_term(value) for value in values if value)[:limit]
    if not rendered:
        return ""
    return rendered[0] if len(rendered) == 1 else f"({' OR '.join(rendered)})"


def combine(*groups: Iterable[str] | str) -> str:
    rendered: list[str] = []
    for group in groups:
        value = group if isinstance(group, str) else term_group(group)
        value = value.strip()
        if value:
            rendered.append(value)
    return " AND ".join(rendered)


def bounded_query(query: str, fallback: str, limit: int = 980) -> str:
    clean = " ".join(query.split()) or " ".join(fallback.split())
    if len(clean) <= limit:
        return clean
    return clean[:limit].rsplit(" ", 1)[0]


def select_sources(
    available: tuple[str, ...],
    preferred: Iterable[str],
    *,
    fallback_to_core: bool = True,
) -> tuple[str, ...]:
    allowed = set(available)
    selected = unique(source for source in preferred if source in allowed)
    if selected or not fallback_to_core:
        return selected
    return unique(source for source in CORE_SOURCES if source in allowed) or available


def core_sources(available: tuple[str, ...]) -> tuple[str, ...]:
    selected = select_sources(available, CORE_SOURCES, fallback_to_core=False)
    # An explicit source override may intentionally contain only a resolver or
    # specialist index.  Keep the request executable rather than silently
    # restoring the default core pack.
    return selected or available


def discovery_sources(
    available: tuple[str, ...], *specialized: str
) -> tuple[str, ...]:
    return select_sources(available, (*CORE_SOURCES, *specialized))


def lane(
    *,
    id: str,
    scenario: str,
    purpose: str,
    query: str,
    family: str,
    sources: tuple[str, ...],
    evidence_dimension: str,
    budget: SearchBudget,
    run_condition: str = "always",
    depends_on: str | None = None,
    context_level: str | None = None,
    required_concepts: tuple[str, ...] = (),
    notes: tuple[str, ...] = (),
) -> QueryLane:
    if not sources:
        raise ValueError(f"lane {id} has no applicable source")
    return QueryLane(
        id=id,
        scenario=scenario,
        purpose=purpose,
        query=bounded_query(query, purpose),
        family=family,
        sources=sources,
        evidence_dimension=evidence_dimension,
        requested_limit=budget.per_lane,
        run_condition=run_condition,
        depends_on=depends_on,
        context_level=context_level,
        required_concepts=required_concepts,
        notes=notes,
    )


def exact_lookup_lane(
    scenario: str,
    request: SearchRequest,
    budget: SearchBudget,
    sources: tuple[str, ...],
) -> QueryLane | None:
    matches = unique(EXACT_IDENTIFIER_RE.findall(request.question))
    exact_concepts = concept_terms(
        request,
        "identifier",
        "doi",
        "pmid",
        "pmcid",
        "trial_id",
        "accession",
        limit=6,
    )
    terms = unique((*matches, *exact_concepts))
    if not terms:
        return None
    return lane(
        id=f"{scenario}.exact_lookup",
        scenario=scenario,
        purpose="Resolve exact identifiers before topical expansion",
        query=term_group(terms),
        family="exact_identifier",
        sources=discovery_sources(sources, "crossref", "datacite", "clinicaltrials"),
        evidence_dimension="exact_lookup",
        budget=budget,
        notes=("Exact identifiers are preserved verbatim.",),
    )


def keyword_score(
    text: str,
    patterns: Iterable[str],
    *,
    points: int = 2,
) -> tuple[int, tuple[str, ...]]:
    reasons = unique(
        f"keyword:{match.group(0)}"
        for pattern in patterns
        if (match := re.search(pattern, text, flags=re.IGNORECASE))
    )
    return len(reasons) * points, reasons


def concept_type_score(
    concepts: tuple[Concept, ...],
    types: Iterable[str],
    *,
    points: int = 2,
) -> tuple[int, tuple[str, ...]]:
    wanted = {value.casefold() for value in types}
    found = unique(
        f"concept_type:{concept.type.casefold()}"
        for concept in concepts
        if concept.type.casefold() in wanted
    )
    return len(found) * points, found


def cap_lanes(lanes: Iterable[QueryLane], budget: SearchBudget) -> tuple[QueryLane, ...]:
    """Keep planner priority order while always retaining dependency integrity."""

    selected = list(lanes)[: budget.max_lanes]
    selected_ids = {item.id for item in selected}
    # A conditional lane without its strict dependency is unsafe and useless.
    return tuple(
        item
        for item in selected
        if item.depends_on is None or item.depends_on in selected_ids
    )
