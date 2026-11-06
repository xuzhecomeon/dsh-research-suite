"""Multi-dimensional target-research planner."""

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
DISEASE_TYPES = ("disease", "indication", "condition", "phenotype")


class TargetResearchPlanner:
    scenario = "target-research"
    ontology_packs = (
        "hgnc",
        "uniprot",
        "open-targets",
        "chembl",
        "chebi",
        "mondo",
        "efo",
        "go",
        "reactome",
        "uberon",
        "cell-ontology",
    )
    output_sections = (
        "target_identity_and_scope",
        "human_genetic_evidence",
        "disease_association",
        "mechanism_and_pathways",
        "expression_context",
        "experimental_validation",
        "tractability_and_modality",
        "clinical_translation",
        "safety_liabilities",
        "evidence_gaps",
    )

    def detect(self, question: str, concepts: tuple[Concept, ...]) -> Detection:
        keyword_points, keyword_reasons = keyword_score(
            question,
            (
                r"\b(?:target|druggab|tractab|target validation|target biology)\w*\b",
                r"靶点|成药性|可药性|靶点验证|靶点生物学",
            ),
            points=4,
        )
        concept_points, concept_reasons = concept_type_score(
            concepts, TARGET_TYPES, points=2
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
        targets = concept_terms(request, *TARGET_TYPES)
        diseases = concept_terms(request, *DISEASE_TYPES)
        modalities = concept_terms(request, "modality", "drug_class", "therapeutic_modality")
        tissues = concept_terms(request, "tissue", "cell_type")
        assays = concept_terms(request, "assay", "experimental_assay")
        pathways = concept_terms(request, "pathway", "process", "mechanism")
        anchor = targets or concept_terms(request, "topic")
        if not anchor:
            anchor = (request.question,)

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
                    required_concepts=("target",),
                    notes=notes,
                )
            )

        add(
            "identity_function",
            "Establish target identity, protein function, and nomenclature",
            combine(anchor, ("protein function", "target biology")),
            "target_identity",
            ("uniprot", "pubtator3"),
            family="core",
        )
        requested_focus = (*modalities, *tissues, *assays, *pathways)
        if requested_focus:
            add(
                "requested_focus",
                "Retrieve evidence for the explicitly requested target-research context",
                combine(anchor, diseases, requested_focus),
                "requested_focus",
                ("uniprot", "reactome", "open-targets", "pubtator3"),
                notes=(
                    "Explicit modality, tissue, cell-type, assay, and pathway concepts are retained in a priority lane.",
                ),
            )
        add(
            "human_genetic_support",
            "Find human genetic evidence supporting the target-indication relationship",
            combine(
                anchor,
                diseases,
                ("human genetics", "GWAS", "Mendelian randomization", "loss of function"),
            ),
            "human_genetics",
            ("open-targets", "gwas-catalog", "pubtator3"),
        )
        if diseases:
            add(
                "disease_association",
                "Assess target association with the requested indication",
                combine(anchor, diseases),
                "disease_association",
                ("open-targets", "gwas-catalog"),
            )
        add(
            "mechanism_pathway",
            "Map mechanism, pathway membership, and causal biological context",
            combine(
                anchor,
                diseases,
                pathways or ("mechanism", "pathway", "signaling"),
            ),
            "mechanism_pathway",
            ("reactome", "uniprot", "open-targets"),
            family="mechanism",
        )
        if tissues or budget.depth != "quick":
            add(
                "expression_context",
                "Find tissue, cell-type, and disease-state expression context",
                combine(anchor, tissues, ("expression", "tissue", "single cell")),
                "expression_context",
                ("uniprot", "open-targets"),
            )
        add(
            "experimental_validation",
            "Retrieve genetic and pharmacological perturbation studies",
            combine(
                anchor,
                diseases,
                assays,
                ("CRISPR", "knockout", "knockdown", "inhibition", "target validation"),
            ),
            "experimental_validation",
            ("pubtator3", "open-targets"),
        )
        if budget.depth != "quick":
            add(
                "tractability_structure",
                "Find structural, ligand, assay, and tractability precedents",
                combine(
                    anchor,
                    assays,
                    ("druggability", "tractability", "binding", "structure", "assay"),
                ),
                "tractability",
                ("uniprot", "open-targets"),
            )
            add(
                "modality_precedent",
                "Map therapeutic modalities and pharmacological precedents",
                combine(
                    anchor,
                    modalities or ("small molecule", "antibody", "degrader", "RNA therapy"),
                ),
                "modality",
                ("open-targets", "clinicaltrials", "civic"),
            )
            add(
                "clinical_translation",
                "Find clinical assets and translational evidence",
                combine(anchor, diseases, ("clinical trial", "phase I", "phase II", "phase III")),
                "clinical_translation",
                ("clinicaltrials", "open-targets", "civic"),
            )
        if budget.depth == "deep":
            add(
                "safety_liability",
                "Identify target-mediated safety liabilities and counter-evidence",
                combine(
                    anchor,
                    ("safety", "toxicity", "adverse effect", "on-target toxicity"),
                ),
                "safety_liability",
                ("clinicaltrials", "open-targets", "civic"),
                notes=("Retrieval context is not a causal safety assessment.",),
            )
        return cap_lanes(lanes, budget)
