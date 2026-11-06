"""Scenario-aware source capability and routing policy."""

from __future__ import annotations

from dataclasses import dataclass


CORE_SOURCES = ("europepmc", "pubmed", "semantic-scholar", "openalex")


@dataclass(frozen=True)
class SourcePack:
    name: str
    standard: tuple[str, ...]
    deep: tuple[str, ...] = ()
    ontology_packs: tuple[str, ...] = ()

    def sources_for(self, depth: str) -> tuple[str, ...]:
        extras = self.standard if depth in {"standard", "deep"} else self.standard[:1]
        if depth == "deep":
            extras = (*extras, *self.deep)
        return tuple(dict.fromkeys((*CORE_SOURCES, *extras)))


SOURCE_PACKS: dict[str, SourcePack] = {
    "general-basic": SourcePack(
        "general-basic",
        ("pubtator3", "crossref", "reactome"),
        ("uniprot", "datacite", "doaj", "openaire", "arxiv"),
        ("mesh", "go", "ncbi-taxonomy"),
    ),
    "target-research": SourcePack(
        "target-research",
        ("open-targets", "gwas-catalog", "reactome", "uniprot", "pubtator3"),
        ("clinicaltrials", "civic", "crossref"),
        ("hgnc", "mondo", "open-targets", "chembl", "chebi"),
    ),
    "drug-pipeline": SourcePack(
        "drug-pipeline",
        ("clinicaltrials", "open-targets", "pubtator3", "crossref"),
        ("civic", "reactome", "uniprot", "openaire"),
        ("inn", "chembl", "chebi", "mondo"),
    ),
    "drug-safety": SourcePack(
        "drug-safety",
        ("pubtator3", "clinicaltrials", "crossref"),
        ("open-targets", "civic", "openaire"),
        ("inn", "chembl", "chebi", "meddra", "mesh"),
    ),
    "clinical-evidence": SourcePack(
        "clinical-evidence",
        ("clinicaltrials", "pubtator3", "crossref"),
        ("doaj", "openaire"),
        ("mesh", "mondo", "clinical-study-design"),
    ),
    "methods-benchmarking": SourcePack(
        "methods-benchmarking",
        ("arxiv", "dblp", "crossref", "datacite"),
        ("openaire", "core", "doaj"),
        ("mesh", "go", "data-accession"),
    ),
    "genetic-rare": SourcePack(
        "genetic-rare",
        ("pubtator3", "litvar2", "clinvar", "clingen", "gwas-catalog"),
        ("civic", "reactome", "uniprot", "crossref"),
        ("hgnc", "mondo", "hpo", "variant-identifiers"),
    ),
}


SOURCE_ROLES: dict[str, str] = {
    "europepmc": "primary_biomedical_index",
    "pubmed": "primary_biomedical_index",
    "semantic-scholar": "scholarly_index_and_graph",
    "openalex": "broad_scholarly_index",
    "pubtator3": "biomedical_entity_index",
    "open-targets": "target_disease_drug_publication_seed",
    "gwas-catalog": "human_genetics_publication_seed",
    "reactome": "pathway_publication_seed",
    "uniprot": "protein_publication_seed",
    "clinicaltrials": "trial_and_linked_publication_source",
    "civic": "cancer_evidence_publication_seed",
    "litvar2": "variant_publication_seed",
    "clinvar": "clinical_variant_publication_seed",
    "clingen": "gene_variant_curation_publication_seed",
    "crossref": "publisher_metadata_index",
    "datacite": "research_object_index",
    "doaj": "open_access_index",
    "openaire": "open_research_index",
    "core": "open_access_full_text_index",
    "arxiv": "preprint_index",
    "dblp": "computing_index",
}


def source_pack_for(scenario: str) -> SourcePack:
    try:
        return SOURCE_PACKS[scenario]
    except KeyError as error:
        raise ValueError(f"unknown scenario source pack: {scenario}") from error
