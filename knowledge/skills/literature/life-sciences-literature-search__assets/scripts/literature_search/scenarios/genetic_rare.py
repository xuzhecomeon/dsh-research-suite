"""Genetic and rare-disease evidence planner."""

from __future__ import annotations

from ..models import Concept, QueryLane, SearchBudget, SearchRequest
from .base import (
    Detection,
    cap_lanes,
    combine,
    concept_terms,
    concept_type_score,
    concepts_of,
    discovery_sources,
    exact_lookup_lane,
    keyword_score,
    lane,
)


GENE_TYPES = ("gene", "target")
DISEASE_TYPES = ("disease", "rare_disease", "condition", "indication")
PHENOTYPE_TYPES = ("phenotype", "hpo")
VARIANT_TYPES = ("variant", "allele", "hgvs", "rsid")


class GeneticRarePlanner:
    scenario = "genetic-rare"
    ontology_packs = (
        "hgnc",
        "mondo",
        "hpo",
        "sequence-ontology",
        "variant-identifiers",
        "clingen",
        "gencc",
    )
    output_sections = (
        "normalized_genetic_concepts",
        "gene_disease_evidence",
        "variant_case_and_cohort_table",
        "phenotype_gene_relationships",
        "inheritance_and_segregation",
        "functional_mechanism",
        "genotype_phenotype_and_allelic_spectrum",
        "conflicting_evidence",
        "natural_history",
        "classification_boundary_and_gaps",
    )

    def detect(self, question: str, concepts: tuple[Concept, ...]) -> Detection:
        keyword_points, keyword_reasons = keyword_score(
            question,
            (
                r"\b(?:rare disease|Mendelian|variant|mutation|HGVS|phenotype|HPO|segregation|inheritance|proband|case report)\b",
                r"罕见病|遗传病|变异|突变|表型|遗传方式|共分离|先证者|病例|家系",
                r"\b(?:c|g|m|n|p|r)\.[A-Za-z0-9_+*?>=()\[\]-]+",
                r"\brs\d+\b",
            ),
            points=4,
        )
        concept_points, concept_reasons = concept_type_score(
            concepts,
            (*PHENOTYPE_TYPES, *VARIANT_TYPES, "inheritance", "rare_disease"),
            points=3,
        )
        has_genetic_signal = bool(keyword_points or concept_points)
        anchor_points, anchor_reasons = concept_type_score(
            concepts, (*GENE_TYPES, "disease", "condition", "indication"), points=1
        )
        return Detection(
            self.scenario,
            keyword_points + concept_points + (anchor_points if has_genetic_signal else 0),
            (
                *keyword_reasons,
                *concept_reasons,
                *(anchor_reasons if has_genetic_signal else ()),
            ),
        )

    def build_lanes(
        self,
        request: SearchRequest,
        budget: SearchBudget,
        available_sources: tuple[str, ...],
    ) -> tuple[QueryLane, ...]:
        genes = concept_terms(request, *GENE_TYPES)
        diseases = concept_terms(request, *DISEASE_TYPES)
        phenotypes = concept_terms(request, *PHENOTYPE_TYPES)
        inheritance = concept_terms(request, "inheritance", "mode_of_inheritance")
        mechanisms = concept_terms(request, "mechanism", "molecular_mechanism")
        populations = concept_terms(request, "population", "ancestry")
        anchor = (*genes, *diseases) or concept_terms(request, "topic") or (request.question,)

        lanes: list[QueryLane] = []
        exact = exact_lookup_lane(self.scenario, request, budget, available_sources)
        if exact:
            lanes.append(exact)

        lanes.append(
            lane(
                id="genetic-rare.gene_disease_validity",
                scenario=self.scenario,
                purpose="Retrieve gene-disease validity and causal association evidence",
                query=combine(anchor, ("gene disease", "causal", "pathogenic")),
                family="entity_combination",
                sources=discovery_sources(
                    available_sources,
                    "clingen",
                    "open-targets",
                    "gwas-catalog",
                    "pubtator3",
                ),
                evidence_dimension="gene_disease_validity",
                budget=budget,
                required_concepts=("gene", "disease"),
            )
        )

        if phenotypes:
            lanes.append(
                lane(
                    id="genetic-rare.phenotype_bundle",
                    scenario=self.scenario,
                    purpose="Retrieve evidence matching the combined phenotype profile",
                    query=combine(genes, diseases, phenotypes),
                    family="phenotype",
                    sources=discovery_sources(
                        available_sources, "clingen", "pubtator3", "open-targets"
                    ),
                    evidence_dimension="phenotype_bundle",
                    budget=budget,
                    required_concepts=("phenotype",),
                )
            )

        variant_sources = discovery_sources(
            available_sources,
            "litvar2",
            "clinvar",
            "clingen",
            "civic",
            "pubtator3",
        )
        for index, concept in enumerate(concepts_of(request, *VARIANT_TYPES), start=1):
            variant_terms = concept.terms()
            strict_id = f"genetic-rare.variant_strict_{index}"
            lanes.append(
                lane(
                    id=strict_id,
                    scenario=self.scenario,
                    purpose="Retrieve disease-anchored evidence for one independent variant or allele",
                    query=combine(variant_terms, genes, diseases),
                    family="variant",
                    sources=variant_sources,
                    evidence_dimension="variant_disease_evidence",
                    budget=budget,
                    context_level="strict" if diseases else "available_anchor",
                    required_concepts=("variant",),
                    notes=(
                        "Variant forms are equivalent only when that equivalence is user asserted or resolver verified.",
                    ),
                )
            )
            if genes and diseases:
                lanes.append(
                    lane(
                        id=f"genetic-rare.variant_broad_{index}",
                        scenario=self.scenario,
                        purpose="Conditionally broaden a zero-result strict variant search",
                        query=combine(variant_terms, genes),
                        family="variant",
                        sources=variant_sources,
                        evidence_dimension="variant_broad_fallback",
                        budget=budget,
                        run_condition="if_dependency_zero",
                        depends_on=strict_id,
                        context_level="broad_fallback",
                        required_concepts=("variant", "gene"),
                        notes=(
                            "Run per source only after the strict dependency succeeds with zero results.",
                            "Broad results require disease-context auditing and down-ranking.",
                        ),
                    )
                )

        if budget.depth != "quick":
            for index, concept in enumerate(concepts_of(request, *PHENOTYPE_TYPES), start=1):
                lanes.append(
                    lane(
                        id=f"genetic-rare.phenotype_rescue_{index}",
                        scenario=self.scenario,
                        purpose="Recover evidence linked to one phenotype when the full bundle is too strict",
                        query=combine(concept.terms(), genes, diseases),
                        family="phenotype",
                        sources=discovery_sources(available_sources, "clingen", "pubtator3"),
                        evidence_dimension="phenotype_rescue",
                        budget=budget,
                        context_level="broad",
                    )
                )
            lanes.append(
                lane(
                    id="genetic-rare.case_cohort",
                    scenario=self.scenario,
                    purpose="Find case reports, case series, families, and genotype cohorts",
                    query=combine(
                        anchor,
                        phenotypes,
                        populations,
                        ("case report", "case series", "family", "cohort"),
                    ),
                    family="publication_type",
                    sources=discovery_sources(
                        available_sources, "litvar2", "clinvar", "clingen", "pubtator3"
                    ),
                    evidence_dimension="case_cohort",
                    budget=budget,
                )
            )
            lanes.append(
                lane(
                    id="genetic-rare.inheritance_segregation",
                    scenario=self.scenario,
                    purpose="Retrieve inheritance, segregation, de novo, and family evidence",
                    query=combine(
                        anchor,
                        inheritance,
                        ("segregation", "de novo", "inheritance", "pedigree"),
                    ),
                    family="mechanism",
                    sources=discovery_sources(
                        available_sources, "clinvar", "clingen", "pubtator3"
                    ),
                    evidence_dimension="inheritance_segregation",
                    budget=budget,
                )
            )
            lanes.append(
                lane(
                    id="genetic-rare.functional_mechanism",
                    scenario=self.scenario,
                    purpose="Retrieve functional studies and molecular mechanism evidence",
                    query=combine(
                        genes,
                        diseases,
                        mechanisms or ("functional study", "molecular mechanism", "assay"),
                    ),
                    family="mechanism",
                    sources=discovery_sources(
                        available_sources, "reactome", "uniprot", "pubtator3"
                    ),
                    evidence_dimension="functional_mechanism",
                    budget=budget,
                )
            )
        if budget.depth == "deep":
            lanes.append(
                lane(
                    id="genetic-rare.genotype_phenotype",
                    scenario=self.scenario,
                    purpose="Map genotype-phenotype relationships and allelic spectrum",
                    query=combine(
                        genes,
                        diseases,
                        phenotypes,
                        ("genotype phenotype", "allelic spectrum", "variable expressivity"),
                    ),
                    family="phenotype",
                    sources=discovery_sources(
                        available_sources, "litvar2", "clinvar", "clingen", "pubtator3"
                    ),
                    evidence_dimension="genotype_phenotype",
                    budget=budget,
                )
            )
            lanes.append(
                lane(
                    id="genetic-rare.conflicting_evidence",
                    scenario=self.scenario,
                    purpose="Actively retrieve conflicting and refuting genetic evidence",
                    query=combine(
                        anchor,
                        ("conflicting evidence", "refuted", "benign", "uncertain significance"),
                    ),
                    family="entity_combination",
                    sources=discovery_sources(
                        available_sources, "clinvar", "clingen", "pubtator3"
                    ),
                    evidence_dimension="conflicting_evidence",
                    budget=budget,
                    notes=("The search does not perform ACMG/AMP variant classification.",),
                )
            )
        return cap_lanes(lanes, budget)
