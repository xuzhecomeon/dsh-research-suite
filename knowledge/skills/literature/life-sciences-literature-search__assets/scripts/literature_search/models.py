"""Shared request, planning, and evidence contracts.

The contracts deliberately keep research intent, domain scenario, retrieval
budget, and output format independent.  Scenario modules may add detail but
must not invent their own incompatible result shape.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Iterable


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
SUPPORT_LEVELS = ("metadata", "abstract", "full_text", "database")


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value.strip() for value in values if value.strip()))


@dataclass(frozen=True)
class Concept:
    """One user-supplied scientific concept and its audited normalization."""

    type: str
    input: str
    role: str | None = None
    canonical_id: str | None = None
    canonical_label: str | None = None
    synonyms: tuple[str, ...] = ()
    descendants: tuple[str, ...] = ()
    mapping_status: str = "not_attempted"
    resolver: str | None = None
    ontology: str | None = None
    confidence: str | None = None
    expansion: str = "exact_and_synonyms"
    provenance: dict[str, Any] = field(default_factory=dict)

    def terms(self) -> tuple[str, ...]:
        descendants = (
            self.descendants
            if self.expansion in {"descendants", "exact_synonyms_descendants"}
            else ()
        )
        return _unique(
            value
            for value in (
                self.input,
                self.canonical_label,
                *self.synonyms,
                *descendants,
            )
            if value
        )

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)


@dataclass(frozen=True)
class Constraints:
    year_from: int | None = None
    year_to: int | None = None
    publication_types: tuple[str, ...] = ()
    excluded_publication_types: tuple[str, ...] = ()
    authors: tuple[str, ...] = ()
    venues: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    species: tuple[str, ...] = ()
    required_identifiers: tuple[str, ...] = ()
    open_access: bool = False
    require_abstract: bool = False
    exclude_preprints: bool = False
    include_retracted: bool = False
    has_associated_data: bool = False

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)


@dataclass(frozen=True)
class SearchBudget:
    depth: str
    per_source: int
    per_lane: int
    max_calls_per_source: int
    result_limit: int
    max_lanes: int
    max_sources: int
    web_search_min: int
    web_search_max: int
    expansion: str
    expansion_seeds: int
    expansion_per_seed: int
    weak_result_threshold: int

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)


@dataclass(frozen=True)
class SearchRequest:
    question: str
    depth: str
    scenarios: tuple[str, ...]
    primary_scenario: str
    concepts: tuple[Concept, ...]
    constraints: Constraints
    deliverable: str = "table"
    output_language: str = "zh"
    sort: str = "relevance"
    expansion: str = "auto"
    normalize: bool = True
    include_descendants: bool = False
    source_override: tuple[str, ...] = ()
    query_variants: tuple[str, ...] = ()
    web_result_files: tuple[str, ...] = ()
    dry_run: bool = False

    def concepts_of(self, *types: str) -> tuple[Concept, ...]:
        wanted = {value.casefold() for value in types}
        return tuple(
            concept
            for concept in self.concepts
            if concept.type.casefold() in wanted
            and (concept.role or "").casefold() != "exclude"
        )

    def excluded_concepts(self) -> tuple[Concept, ...]:
        return tuple(
            concept
            for concept in self.concepts
            if (concept.role or "").casefold() == "exclude"
        )

    def terms_of(self, *types: str) -> tuple[str, ...]:
        return _unique(
            term for concept in self.concepts_of(*types) for term in concept.terms()
        )

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)


@dataclass(frozen=True)
class QueryLane:
    id: str
    scenario: str
    purpose: str
    query: str
    family: str
    sources: tuple[str, ...]
    evidence_dimension: str
    requested_limit: int
    run_condition: str = "always"
    depends_on: str | None = None
    context_level: str | None = None
    required_concepts: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_backend_dict(self) -> dict[str, Any]:
        return {
            "text": self.query,
            "family": self.family,
            "lane": self.id,
            "origin": f"scenario:{self.scenario}",
            "purpose": self.purpose,
            "scenario": self.scenario,
            "evidence_dimension": self.evidence_dimension,
            "run_condition": self.run_condition,
            "depends_on": self.depends_on,
            "context_level": self.context_level,
            "requested_limit": self.requested_limit,
            "required_concepts": list(self.required_concepts),
            "notes": list(self.notes),
        }

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)


@dataclass(frozen=True)
class SourceRoute:
    source: str
    role: str
    scenarios: tuple[str, ...]
    lane_ids: tuple[str, ...]
    activation_reason: str
    constraint_support: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)


@dataclass(frozen=True)
class SearchPlan:
    request: SearchRequest
    budget: SearchBudget
    lanes: tuple[QueryLane, ...]
    routes: tuple[SourceRoute, ...]
    ontology_packs: tuple[str, ...]
    output_sections: tuple[str, ...]
    warnings: tuple[str, ...] = ()

    @property
    def sources(self) -> tuple[str, ...]:
        return tuple(route.source for route in self.routes)

    def lanes_for_source(self, source: str) -> tuple[QueryLane, ...]:
        route = next((item for item in self.routes if item.source == source), None)
        if route is None:
            return ()
        allowed = set(route.lane_ids)
        return tuple(lane for lane in self.lanes if lane.id in allowed)

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)


@dataclass(frozen=True)
class EvidenceObject:
    type: str
    id: str
    label: str
    source: str
    url: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    linked_publication_ids: tuple[str, ...] = ()
    support_level: str = "database"

    def to_dict(self) -> dict[str, Any]:
        return dataclass_to_dict(self)


def dataclass_to_dict(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {
            field_.name: dataclass_to_dict(getattr(value, field_.name))
            for field_ in dataclasses.fields(value)
        }
    if isinstance(value, tuple):
        return [dataclass_to_dict(item) for item in value]
    if isinstance(value, list):
        return [dataclass_to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: dataclass_to_dict(item) for key, item in value.items()}
    return value
