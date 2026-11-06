"""Drug-safety and pharmacovigilance literature planner."""

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


DRUG_TYPES = ("drug", "compound", "chemical", "intervention", "drug_class")
AE_TYPES = ("adverse_event", "adverse_effect", "toxicity", "safety_event")


class DrugSafetyPlanner:
    scenario = "drug-safety"
    ontology_packs = (
        "inn",
        "chembl",
        "chebi",
        "pubchem",
        "rxnorm",
        "atc",
        "meddra",
        "mesh",
    )
    output_sections = (
        "normalized_drug_and_events",
        "safety_signal_matrix",
        "evidence_type_layers",
        "seriousness_and_timeline",
        "special_populations",
        "interactions_and_combinations",
        "regulatory_updates",
        "consistency_and_conflicts",
        "coverage_limitations",
    )

    def detect(self, question: str, concepts: tuple[Concept, ...]) -> Detection:
        keyword_points, keyword_reasons = keyword_score(
            question,
            (
                r"\b(?:drug safety|safety profile|adverse event|adverse effect|safety signal|pharmacovigilance|toxicity|tolerability|post[- ]marketing)\b",
                r"不良反应|不良事件|安全信号|药物警戒|毒性|耐受性|上市后",
            ),
            points=6,
        )
        weak_points, weak_reasons = keyword_score(
            question, (r"\bsafety\b", r"安全性"), points=2
        )
        event_points, event_reasons = concept_type_score(
            concepts, AE_TYPES, points=4
        )
        has_drug = any(concept.type.casefold() in set(DRUG_TYPES) for concept in concepts)
        drug_context_bonus = 1 if has_drug and (keyword_points or weak_points or event_points) else 0
        return Detection(
            self.scenario,
            keyword_points + weak_points + event_points + drug_context_bonus,
            (*keyword_reasons, *weak_reasons, *event_reasons),
        )

    def build_lanes(
        self,
        request: SearchRequest,
        budget: SearchBudget,
        available_sources: tuple[str, ...],
    ) -> tuple[QueryLane, ...]:
        drugs = concept_terms(request, *DRUG_TYPES)
        events = concept_terms(request, *AE_TYPES)
        diseases = concept_terms(request, "disease", "indication", "condition")
        populations = concept_terms(request, "population", "age_group", "special_population")
        combinations = concept_terms(request, "co_medication", "combination", "comparator")
        anchor = drugs or concept_terms(request, "topic") or (request.question,)
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
                    required_concepts=("drug",),
                    notes=notes,
                )
            )

        add(
            "requested_events" if events else "overall_safety",
            "Retrieve evidence for requested adverse events" if events else "Map the principal reported safety profile",
            combine(
                anchor,
                diseases,
                events or ("adverse event", "adverse effect", "toxicity", "safety"),
            ),
            "requested_adverse_events" if events else "overall_safety",
            ("pubtator3", "clinicaltrials", "civic"),
            family="core",
        )
        add(
            "trial_safety",
            "Find treatment-emergent adverse events and trial tolerability results",
            combine(anchor, diseases, events, ("clinical trial", "tolerability", "safety")),
            "trial_safety",
            ("clinicaltrials", "pubtator3"),
        )
        if budget.depth != "quick":
            add(
                "postmarketing_signals",
                "Retrieve post-marketing and pharmacovigilance signal literature",
                combine(
                    anchor,
                    events,
                    ("pharmacovigilance", "postmarketing", "disproportionality", "safety signal"),
                ),
                "postmarketing_signals",
                ("pubtator3", "openaire"),
                notes=("A signal report is not proof of causality or incidence.",),
            )
            add(
                "case_reports",
                "Find case reports and case series for rare or emerging events",
                combine(anchor, events, ("case report", "case series")),
                "case_reports",
                ("pubtator3", "doaj"),
                family="publication_type",
            )
            add(
                "serious_outcomes",
                "Retrieve serious and organ-specific adverse outcomes",
                combine(
                    anchor,
                    events,
                    ("serious adverse event", "hospitalization", "death", "organ toxicity"),
                ),
                "serious_outcomes",
                ("clinicaltrials", "pubtator3"),
            )
        if populations:
            add(
                "special_populations",
                "Assess safety in the requested special populations",
                combine(anchor, events, populations),
                "special_populations",
                ("clinicaltrials", "pubtator3"),
            )
        if combinations:
            add(
                "interactions_combinations",
                "Find interaction and combination-treatment safety evidence",
                combine(anchor, combinations, events, ("interaction", "combination safety")),
                "interactions",
                ("clinicaltrials", "pubtator3"),
            )
        if budget.depth == "deep":
            add(
                "class_effect",
                "Compare requested events across the pharmacological class",
                combine(
                    concept_terms(request, "drug_class") or anchor,
                    events,
                    ("class effect", "adverse event"),
                ),
                "class_effect",
                ("open-targets", "pubtator3"),
            )
            add(
                "regulatory_updates",
                "Discover canonical regulatory safety communications",
                combine(anchor, events, ("safety communication", "boxed warning", "label update")),
                "regulatory_updates",
                ("openaire", "crossref"),
                notes=("Regulatory facts require canonical regulator-page verification.",),
            )
        return cap_lanes(lanes, budget)
