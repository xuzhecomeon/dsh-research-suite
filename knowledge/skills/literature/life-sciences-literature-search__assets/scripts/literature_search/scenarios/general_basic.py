"""General life-science discovery planner."""

from __future__ import annotations

from ..models import Concept, QueryLane, SearchBudget, SearchRequest
from .base import (
    Detection,
    cap_lanes,
    combine,
    concept_terms,
    core_sources,
    discovery_sources,
    exact_lookup_lane,
    keyword_score,
    lane,
)


class GeneralBasicPlanner:
    scenario = "general-basic"
    ontology_packs = ("mesh", "go", "ncbi-taxonomy", "mondo", "efo")
    output_sections = (
        "question_scope",
        "ranked_literature",
        "topic_and_evidence_map",
        "reading_order",
        "research_gaps",
        "search_coverage",
    )

    def detect(self, question: str, concepts: tuple[Concept, ...]) -> Detection:
        score, reasons = keyword_score(
            question,
            (
                r"\b(?:literature|papers?|publications?|review|overview)\b",
                r"文献|论文|综述|研究进展|概览",
            ),
            points=1,
        )
        return Detection(self.scenario, max(1, score), reasons or ("fallback",))

    def build_lanes(
        self,
        request: SearchRequest,
        budget: SearchBudget,
        available_sources: tuple[str, ...],
    ) -> tuple[QueryLane, ...]:
        lanes: list[QueryLane] = []
        exact = exact_lookup_lane(self.scenario, request, budget, available_sources)
        if exact:
            lanes.append(exact)

        topic_terms = concept_terms(
            request,
            "topic",
            "disease",
            "indication",
            "gene",
            "target",
            "protein",
            "drug",
            "chemical",
            "process",
            "pathway",
        )
        topic_query = combine(topic_terms) if topic_terms else request.question
        explicit_species_keys = {
            " ".join(value.casefold().split())
            for value in (
                *request.constraints.species,
                *concept_terms(request, "species"),
            )
        }
        model_terms = tuple(
            value
            for value in concept_terms(request, "organism", "model", "model_system")
            if " ".join(value.casefold().split()) not in explicit_species_keys
        )
        lanes.append(
            lane(
                id="general-basic.topic_core",
                scenario=self.scenario,
                purpose="Retrieve the central life-science topic",
                query=topic_query,
                family="core",
                sources=core_sources(available_sources),
                evidence_dimension="topic_core",
                budget=budget,
            )
        )

        # Context axes are separate lanes.  Grouping mechanism, model, tissue,
        # and method as one OR expression produces superficially broad hits
        # and makes it impossible to see which user-requested facet failed.
        facet_specs = (
            (
                "biological_focus",
                "Connect the topic to the requested mechanism or biological question",
                concept_terms(request, "research_aspect", "context", "mechanism", "outcome"),
                ("pubtator3", "reactome", "uniprot"),
            ),
            (
                "method_context",
                "Retrieve studies using the requested experimental or analytical method",
                concept_terms(request, "method", "experimental_method"),
                ("pubtator3", "arxiv"),
            ),
            (
                "model_context",
                "Retrieve evidence in the requested organism or model system",
                model_terms,
                ("pubtator3",),
            ),
            (
                "anatomical_context",
                "Retrieve evidence in the requested tissue, cell type, or population",
                concept_terms(request, "tissue", "cell_type", "population"),
                ("pubtator3", "uniprot"),
            ),
        )
        active_facets: list[tuple[str, ...]] = []
        seen_queries = {" ".join(topic_query.casefold().split())}
        for suffix, purpose, terms, specialized in facet_specs:
            if not terms:
                continue
            query = combine(topic_query, terms)
            query_key = " ".join(query.casefold().split())
            if query_key in seen_queries:
                continue
            seen_queries.add(query_key)
            active_facets.append(terms)
            lanes.append(
                lane(
                    id=f"general-basic.{suffix}",
                    scenario=self.scenario,
                    purpose=purpose,
                    query=query,
                    family="entity_combination",
                    sources=discovery_sources(available_sources, *specialized),
                    evidence_dimension=suffix,
                    budget=budget,
                    required_concepts=("topic", suffix),
                )
            )

        if budget.depth == "deep" and len(active_facets) > 1:
            lanes.append(
                lane(
                    id="general-basic.integrated_context",
                    scenario=self.scenario,
                    purpose="Find studies matching all explicitly requested biological facets",
                    query=combine(topic_query, *active_facets),
                    family="entity_combination",
                    sources=core_sources(available_sources),
                    evidence_dimension="integrated_context",
                    budget=budget,
                    notes=(
                        "This high-precision lane ANDs distinct facets; zero results do not invalidate evidence from the separate facet lanes.",
                    ),
                )
            )

        if request.deliverable in {"review", "landscape"} or budget.depth == "deep":
            lanes.append(
                lane(
                    id="general-basic.secondary_evidence",
                    scenario=self.scenario,
                    purpose="Find reviews and organizing secondary evidence",
                    query=combine(topic_terms, ("review", "systematic review", "overview")),
                    family="publication_type",
                    sources=discovery_sources(available_sources, "doaj", "openaire"),
                    evidence_dimension="secondary_evidence",
                    budget=budget,
                )
            )

        return cap_lanes(lanes, budget)
