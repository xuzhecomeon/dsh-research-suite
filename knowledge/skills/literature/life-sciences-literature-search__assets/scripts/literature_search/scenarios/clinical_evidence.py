"""PICO-oriented clinical-evidence planner."""

from __future__ import annotations

from ..models import Concept, QueryLane, SearchBudget, SearchRequest
from .base import (
    Detection,
    cap_lanes,
    combine,
    concept_terms,
    concept_type_score,
    discovery_sources,
    exact_lookup_lane,
    keyword_score,
    lane,
)


class ClinicalEvidencePlanner:
    scenario = "clinical-evidence"
    ontology_packs = (
        "mesh",
        "cmesh",
        "mondo",
        "efo",
        "clinical-study-design",
        "pico",
        "inn",
        "chembl",
    )
    output_sections = (
        "structured_pico",
        "evidence_hierarchy",
        "study_table",
        "outcomes_and_effects",
        "consistency_conflicts_negative_evidence",
        "subgroups_and_biomarkers",
        "safety_and_tolerability",
        "ongoing_trials",
        "guidelines_and_consensus",
        "evidence_gaps",
    )

    def detect(self, question: str, concepts: tuple[Concept, ...]) -> Detection:
        keyword_points, keyword_reasons = keyword_score(
            question,
            (
                r"\b(?:clinical evidence|randomi[sz]ed|RCT|meta-analysis|systematic review|cohort|real-world|guideline|PICO|treatment outcome)\b",
                r"临床证据|随机对照|荟萃分析|系统综述|队列|真实世界|指南|疗效|循证",
            ),
            points=7,
        )
        concept_points, concept_reasons = concept_type_score(
            concepts,
            (
                "population",
                "intervention",
                "comparator",
                "outcome",
                "study_design",
                "biomarker",
            ),
            points=2,
        )
        return Detection(
            self.scenario,
            keyword_points + concept_points,
            (*keyword_reasons, *concept_reasons),
        )

    def build_lanes(
        self,
        request: SearchRequest,
        budget: SearchBudget,
        available_sources: tuple[str, ...],
    ) -> tuple[QueryLane, ...]:
        conditions = concept_terms(request, "disease", "condition", "indication")
        populations = concept_terms(request, "population", "age_group", "stage")
        interventions = concept_terms(
            request, "intervention", "drug", "procedure", "diagnostic_test", "treatment"
        )
        comparators = concept_terms(request, "comparator", "control")
        outcomes = concept_terms(request, "outcome", "endpoint")
        biomarkers = concept_terms(request, "biomarker", "gene", "variant", "target")
        designs = concept_terms(request, "study_design")
        population_anchor = (*conditions, *populations) or concept_terms(request, "topic")
        intervention_anchor = interventions or biomarkers
        if not population_anchor:
            population_anchor = (request.question,)

        lanes: list[QueryLane] = []
        exact = exact_lookup_lane(self.scenario, request, budget, available_sources)
        if exact:
            lanes.append(exact)

        def add(
            suffix: str,
            purpose: str,
            query: str,
            dimension: str,
            specialized: tuple[str, ...] = (),
            *,
            family: str = "entity_combination",
            notes: tuple[str, ...] = (),
        ) -> None:
            lanes.append(
                lane(
                    id=f"{self.scenario}.{suffix}",
                    scenario=self.scenario,
                    purpose=purpose,
                    query=query,
                    family=family,
                    sources=discovery_sources(available_sources, *specialized),
                    evidence_dimension=dimension,
                    budget=budget,
                    notes=notes,
                )
            )

        add(
            "pico_core",
            "Retrieve the central population-intervention clinical evidence",
            combine(population_anchor, intervention_anchor, comparators, outcomes),
            "pico_core",
            ("pubtator3", "clinicaltrials"),
            family="core",
        )
        add(
            "randomized_trials",
            "Retrieve randomized and controlled intervention studies",
            combine(
                population_anchor,
                intervention_anchor,
                designs or ("randomized controlled trial", "controlled clinical trial"),
            ),
            "randomized_trials",
            ("clinicaltrials", "pubtator3"),
            family="publication_type",
        )
        add(
            "systematic_reviews_meta",
            "Retrieve systematic reviews and meta-analyses",
            combine(
                population_anchor,
                intervention_anchor,
                ("systematic review", "meta-analysis"),
            ),
            "systematic_reviews_meta",
            ("crossref", "doaj", "openaire"),
            family="publication_type",
        )
        if budget.depth != "quick":
            add(
                "observational_real_world",
                "Retrieve cohort, observational, and real-world evidence",
                combine(
                    population_anchor,
                    intervention_anchor,
                    ("cohort", "observational", "real-world evidence", "registry"),
                ),
                "observational_real_world",
                ("pubtator3", "openaire"),
                family="publication_type",
            )
            add(
                "safety_tolerability",
                "Retrieve clinical safety and tolerability evidence",
                combine(
                    population_anchor,
                    intervention_anchor,
                    ("safety", "tolerability", "adverse event"),
                ),
                "safety_tolerability",
                ("clinicaltrials", "pubtator3"),
            )
            add(
                "ongoing_trials",
                "Find ongoing and recruiting clinical trials",
                combine(population_anchor, intervention_anchor, ("recruiting", "clinical trial")),
                "ongoing_trials",
                ("clinicaltrials",),
                notes=("Trial status is reported as an as-of registry fact.",),
            )
        if biomarkers:
            add(
                "biomarker_subgroups",
                "Assess biomarker-defined and clinically relevant subgroups",
                combine(population_anchor, intervention_anchor, biomarkers, outcomes),
                "biomarker_subgroups",
                ("pubtator3", "clinicaltrials"),
            )
        if budget.depth == "deep":
            add(
                "guidelines_consensus",
                "Discover guidelines, recommendations, and expert consensus",
                combine(population_anchor, intervention_anchor, ("guideline", "consensus", "recommendation")),
                "guidelines_consensus",
                ("crossref", "openaire"),
                family="publication_type",
                notes=("Canonical guideline verification is required before synthesis.",),
            )
            add(
                "negative_conflicting",
                "Actively retrieve negative, null, and conflicting evidence",
                combine(
                    population_anchor,
                    intervention_anchor,
                    ("negative trial", "no significant", "null result", "conflicting evidence"),
                ),
                "negative_conflicting",
                ("clinicaltrials", "openaire"),
                notes=("Absence of retrieved evidence is never interpreted as no effect.",),
            )
        return cap_lanes(lanes, budget)
