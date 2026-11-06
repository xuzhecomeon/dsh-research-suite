"""Drug-pipeline and competitive-intelligence planner."""

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


TARGET_TYPES = ("target", "gene", "protein")
DISEASE_TYPES = ("disease", "indication", "condition")
ASSET_TYPES = ("drug", "compound", "asset", "intervention", "chemical")


class DrugPipelinePlanner:
    scenario = "drug-pipeline"
    ontology_packs = (
        "inn",
        "chembl",
        "chebi",
        "pubchem",
        "hgnc",
        "uniprot",
        "mondo",
        "efo",
        "therapeutic-modality",
        "clinical-trial-terms",
        "sponsor-aliases",
    )
    output_sections = (
        "as_of_and_scope",
        "normalized_assets",
        "competitive_landscape",
        "trial_registry",
        "asset_trial_publication_links",
        "discontinued_and_negative_programs",
        "pivotal_publications",
        "coverage_and_freshness",
    )

    def detect(self, question: str, concepts: tuple[Concept, ...]) -> Detection:
        keyword_points, keyword_reasons = keyword_score(
            question,
            (
                r"\b(?:drug pipeline|development pipeline|competitive landscape|competitor|asset|sponsor|first[- ]in[- ]human|phase [123iIvV]+)\b",
                r"管线|竞品|竞争格局|申办方|研发项目|临床阶段|在研|已终止",
            ),
            points=5,
        )
        weak_points, weak_reasons = keyword_score(
            question, (r"\bpipeline\b",), points=2
        )
        concept_points, concept_reasons = concept_type_score(
            concepts,
            (*ASSET_TYPES, "sponsor", "trial_phase", "trial_status", "modality"),
            points=2,
        )
        has_target = any(
            concept.type.casefold() in set(TARGET_TYPES) for concept in concepts
        )
        contextual_bonus = 2 if weak_points and has_target else 0
        return Detection(
            self.scenario,
            keyword_points + weak_points + concept_points + contextual_bonus,
            (*keyword_reasons, *weak_reasons, *concept_reasons),
        )

    def build_lanes(
        self,
        request: SearchRequest,
        budget: SearchBudget,
        available_sources: tuple[str, ...],
    ) -> tuple[QueryLane, ...]:
        targets = concept_terms(request, *TARGET_TYPES)
        diseases = concept_terms(request, *DISEASE_TYPES)
        assets = concept_terms(request, *ASSET_TYPES)
        sponsors = concept_terms(request, "sponsor", "company", "organization")
        modalities = concept_terms(request, "modality", "therapeutic_modality", "drug_class")
        phases = concept_terms(request, "trial_phase", "phase")
        statuses = concept_terms(request, "trial_status", "status")
        trial_ids = concept_terms(request, "trial_id", "nct_id", "registry_id")
        anchor = (*targets, *assets, *trial_ids) or concept_terms(request, "topic") or (request.question,)
        lanes: list[QueryLane] = []
        exact = exact_lookup_lane(self.scenario, request, budget, available_sources)
        if exact:
            lanes.append(exact)

        def add(
            suffix: str,
            purpose: str,
            query: str,
            dimension: str,
            specialized: tuple[str, ...],
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
            "asset_identity",
            "Resolve INN, brand, development-code, target, and modality identity",
            combine(anchor, ("drug", "compound", "therapeutic")),
            "asset_identity",
            ("open-targets", "pubtator3"),
            family="core",
            notes=("Brand names, INNs, and development codes remain provenance-tagged.",),
        )
        add(
            "target_indication_assets",
            "Discover assets for the target-indication combination",
            combine(targets or anchor, diseases, assets),
            "competitive_assets",
            ("clinicaltrials", "open-targets", "civic"),
        )
        if statuses:
            add(
                "requested_trials",
                "Retrieve trials matching the requested phase and registry status",
                combine(anchor, diseases, trial_ids, phases, statuses, ("clinical trial",)),
                "requested_trials",
                ("clinicaltrials",),
                notes=(
                    "Trial phase and status are preserved as explicit registry-query terms.",
                    "Trial registry facts must be emitted as evidence objects, not papers.",
                ),
            )
        else:
            add(
                "active_trials",
                "Retrieve recruiting and active interventional trials",
                combine(
                    anchor,
                    diseases,
                    trial_ids,
                    phases,
                    ("clinical trial", "recruiting", "active"),
                ),
                "active_trials",
                ("clinicaltrials",),
                notes=("Trial registry facts must be emitted as evidence objects, not papers.",),
            )
        if modalities:
            add(
                "modality_competitors",
                "Compare assets within the requested therapeutic modality",
                combine(targets or anchor, diseases, modalities),
                "modality_competition",
                ("clinicaltrials", "open-targets", "civic"),
            )
        if sponsors:
            add(
                "sponsor_asset",
                "Resolve sponsor-to-asset and sponsor-to-trial relationships",
                combine(sponsors, assets or targets, diseases),
                "sponsor_landscape",
                ("clinicaltrials", "crossref", "openaire"),
            )
        if budget.depth != "quick":
            normalized_statuses = " ".join(statuses).casefold()
            if not statuses or any(
                marker in normalized_statuses
                for marker in ("complete", "result", "published")
            ):
                add(
                    "completed_trials",
                    "Retrieve completed trials and available study results",
                    combine(
                        anchor,
                        diseases,
                        trial_ids,
                        phases,
                        statuses or ("completed",),
                        ("results", "clinical trial"),
                    ),
                    "completed_trials",
                    ("clinicaltrials",),
                )
            add(
                "trial_results_publications",
                "Link registered trials to peer-reviewed results publications",
                combine(
                    anchor,
                    diseases,
                    trial_ids,
                    phases,
                    statuses,
                    ("trial results", "randomized", "phase"),
                ),
                "trial_publications",
                ("clinicaltrials", "crossref"),
            )
            if not statuses or any(
                marker in normalized_statuses
                for marker in ("terminat", "withdraw", "suspend", "discontinu", "fail")
            ):
                add(
                    "discontinued_programs",
                    "Find terminated, withdrawn, suspended, or negative programs",
                    combine(
                        anchor,
                        diseases,
                        trial_ids,
                        phases,
                        statuses
                        or ("terminated", "withdrawn", "suspended", "failed"),
                        ("negative trial",),
                    ),
                    "discontinued_negative",
                    ("clinicaltrials", "open-targets", "openaire"),
                )
        if budget.depth == "deep":
            add(
                "pivotal_evidence",
                "Retrieve pivotal, first-in-human, and late-stage evidence",
                combine(
                    anchor,
                    diseases,
                    trial_ids,
                    phases or ("phase II", "phase III"),
                    statuses,
                    ("first in human", "pivotal"),
                ),
                "pivotal_evidence",
                ("clinicaltrials", "crossref", "civic"),
            )
            add(
                "regulatory_milestones",
                "Discover regulatory milestones with source-specific provenance",
                combine(anchor, diseases, ("approval", "breakthrough therapy", "orphan drug")),
                "regulatory_milestones",
                ("openaire", "crossref"),
                notes=("Regulatory claims require canonical regulator or sponsor verification.",),
            )
        return cap_lanes(lanes, budget)
