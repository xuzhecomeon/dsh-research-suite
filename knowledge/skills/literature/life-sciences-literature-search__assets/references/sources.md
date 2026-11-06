# Sources, Terminology, And Configuration

This file is the single source-of-truth for v2 source capabilities. The CLI is a client-side federated retrieval tool: it calls public APIs, imports optional Agent web discoveries, and does not depend on GenDia, MCP, a local database, telemetry, or third-party Python packages.

## Capability-Aware Routing

All scenarios start with four scholarly core sources:

| Source | Role | Principal value |
|---|---|---|
| Europe PMC | Primary biomedical index and metadata hydrator | PubMed-origin records, abstracts, PMID/PMCID/DOI, types, citation metadata, associated-data and full-text links |
| PubMed E-utilities | Independent NLM discovery and metadata | MeSH/NLM coverage and independent PubMed retrieval |
| Semantic Scholar | Broad scholarly index and graph | Discovery plus one-round citation, reference, and related-paper expansion |
| OpenAlex | Broad scholarly index | Cross-disciplinary discovery, concepts, citation metadata, and open locations |

The selected scenario adds sources by evidence capability. Quick depth receives the first scenario source in the standard pack; standard receives the full standard pack; deep adds the deep pack, all subject to the global source limit.

| Scenario | Quick extra | Standard pack | Deep additions |
|---|---|---|---|
| `general-basic` | PubTator3 | PubTator3, Crossref, Reactome | UniProt, DataCite, DOAJ, OpenAIRE, arXiv |
| `target-research` | Open Targets | Open Targets, GWAS Catalog, Reactome, UniProt, PubTator3 | ClinicalTrials.gov, CIViC, Crossref |
| `drug-pipeline` | ClinicalTrials.gov | ClinicalTrials.gov, Open Targets, PubTator3, Crossref | CIViC, Reactome, UniProt, OpenAIRE |
| `drug-safety` | PubTator3 | PubTator3, ClinicalTrials.gov, Crossref | Open Targets, CIViC, OpenAIRE |
| `clinical-evidence` | ClinicalTrials.gov | ClinicalTrials.gov, PubTator3, Crossref | DOAJ, OpenAIRE |
| `methods-benchmarking` | arXiv | arXiv, DBLP, Crossref, DataCite | OpenAIRE, CORE, DOAJ |
| `genetic-rare` | PubTator3 | PubTator3, LitVar2, ClinVar, ClinGen, GWAS Catalog | CIViC, Reactome, UniProt, Crossref |

Each query lane contains its exact allowed sources. A selected source is called only for lanes routed to it. An explicit source override replaces scenario routing; use it only when the user names an index or deliberately accepts narrower coverage.

## Structured Source Roles

| Source | Adapter role | Activation or limitation |
|---|---|---|
| PubTator3 | Entity-aware biomedical discovery | Useful for gene, disease, chemical, variant, and safety entity contexts; NCBI access can be limited on shared IPs |
| LitVar2 | Variant-to-publication seed | Runs for rsID/HGVS-like variant concepts; returns linked publications, not variant objects as papers |
| ClinVar | Clinical-variant publication seed | Runs for variant concepts; submitter and review context remains attributed to ClinVar |
| ClinGen | Gene/variant curation publication seed | Runs for relevant gene or variant lanes; public ERepo availability may vary |
| CIViC | Cancer evidence publication seed | Runs for cancer-relevant gene, variant, target, drug, or translation lanes |
| Open Targets | Target/drug entity lookup and publication seed | Exact typed target/drug matches can become first-class objects; association and publication-seed assertions retain source provenance |
| GWAS Catalog | Human-genetics publication seed | Supports target genetics, gene/disease/trait, rsID, and genetic-validity lanes |
| ClinicalTrials.gov | Trial registry and publication seed | Returns first-class trial objects for registry-enabled scenarios and linked paper seeds separately |
| Reactome | Pathway-to-publication seed | Supports mechanism/pathway lanes; current adapter is fixed to Homo sapiens |
| UniProt | Protein-to-publication seed | Supports identity, function, mechanism, and tractability; current adapter prefers reviewed human entries |
| Crossref | Publisher/DOI metadata index | Useful for identity, secondary evidence, guidelines, trial publications, and current publisher metadata |
| DataCite | Research-object index and dataset registry | Useful for methods, datasets, software, and accessions; matching dataset records become first-class dataset objects rather than pseudo-papers |
| DOAJ | Open-access journal discovery | Journal-article coverage only; OA status is not evidence quality |
| OpenAIRE | Open-research discovery | Useful for reports, negative/discontinued programs, methods, and open research; metadata varies by provider |
| CORE | Open-access discovery | Requires `CORE_API_KEY`; otherwise skipped |
| arXiv | Preprint discovery | Important for computational methods; clearly distinguish preprints from peer-reviewed evidence |
| DBLP | Computing index | Useful for bioinformatics and methods; limited coverage outside computing |

bioRxiv and medRxiv preprints are discovered through Europe PMC, broad indexes, or targeted native web; there is no dedicated first-class keyword adapter. ChEMBL normalization resolves conservative molecule identity only and does not automatically infer target, activity, or modality relationships.

Specialized adapters may extract PMID, PMCID, or DOI seeds and hydrate them through Europe PMC. Their database records do not become publications. Source-specific context is retained as enrichment or first-class typed objects.

## Expansion And Enrichment

| Service | Phase | Behavior |
|---|---|---|
| Semantic Scholar graph/recommendations | Optional; automatic at deep depth and as a weak-result standard fallback | One bounded round from verified, non-retracted seeds; standard fallback is related-only and is skipped without a seed |
| OpenCitations COCI | Citation expansion | Independently supplements DOI-based forward and backward citation edges |
| Unpaywall | OA enrichment outside quick depth | Adds open locations to already relevant DOI records when a contact email exists; zero ranking weight |
| Agent native web | Independent discovery input | Adds verified or candidate records from the host's browser/search tool through `--web-results` |

Expansion never recurses. Unpaywall cannot create topical relevance. Search-engine estimates and source totals overlap and must not be added.

## Terminology And Object Resolvers

Terminology services plan queries; they are not literature sources:

| Resolver | Concepts | Notes |
|---|---|---|
| HGNC REST | Gene and target | Exact approved ID/symbol/label or unique exact synonym only |
| EBI OLS4 | MONDO, HPO, ChEBI, GO, Cell Ontology, UBERON | Exact match only; ambiguous/fuzzy results preserve user input |
| ChEMBL | Drug and compound | Supports exact molecule name, brand, and development-code candidates with provenance |
| MeSH lookup | Biomedical headings | Exact normalized label matching |
| NCBI Taxonomy | Organism/species | Exact scientific/common-name matching |
| Controlled study-design list | RCT, meta-analysis, cohort, case-control, case report, guideline | Local deterministic mapping |
| Local `inn.json` | INN/brand/development-code map | Optional caller-provided provenance-aware map |
| Local `meddra.json` | Adverse events | Optional licensed pack; no bundled MedDRA content |
| Local `cmesh.json` | Chinese biomedical terms | Optional caller-provided map |
| Local `atc.json` | Drug class | Optional ATC/local drug-class map |
| Local `edam.json` | Method and data modality | Optional EDAM/local methods map |
| Local `obi.json` | Assay | Optional OBI/local assay map |
| Local `therapeutic_modality.json` | Therapeutic modality | Optional modality vocabulary |
| Local `sponsor_aliases.json` | Sponsor organization | Optional sponsor alias map |

Each local file may be an entry array, `{ "entries": [...] }`, or a mapping keyed by input term. An entry can contain `term`, `label`/`preferred_label`, `id`/`code`, `synonyms`/`aliases`, `ontology`, and `version`. Example:

```json
{
  "entries": [
    {
      "term": "T-DXd",
      "preferred_label": "trastuzumab deruxtecan",
      "id": "local:drug:tdxd",
      "aliases": ["DS-8201"],
      "ontology": "organization drug map",
      "version": "2026-08"
    }
  ]
}
```

The resolver indexes only exact normalized terms, labels, synonyms, and aliases. Keep pack version and authoritative provenance in each entry; the CLI does not validate the scientific authority or licensing of caller-provided files.

Exact patterns recognize HGNC, MONDO, HPO, ChEBI, ChEMBL, MeSH, rsID, NCT, GEO, SRA, and ArrayExpress identifiers without a network call. Missing, ambiguous, failed, or disabled normalization remains explicit and never erases the original term.

Target and drug objects can come from an exact normalized concept or conservative exact Open Targets entity lookup with a stable identifier and canonical URL. Dataset objects can come from normalized GEO/SRA/ArrayExpress concepts or direct DataCite dataset retrieval. ClinicalTrials.gov objects are fetched directly for target, pipeline, safety, and clinical scenarios unless registry objects are disabled.

## Species Behavior

Species is a typed concept and/or constraint, not a hidden keyword. Europe PMC, PubMed, and PubTator3 can provide native or indexed species support for some records. Other sources often have incomplete species metadata, so species may be encoded in a lane and disclosed as bounded screening.

An explicit non-human request removes Reactome and UniProt because their current adapters are human-fixed. Use NCBI Taxonomy normalization and targeted model-organism resources in the native-web lane. Never generalize a non-human result to human biology without separate translational evidence.

## Native Web And Long-Tail Routing

Use native web selectively for canonical objects, current status, terminology, and linked publications that structured adapters do not cover:

| Domain | Useful canonical routes | Extract |
|---|---|---|
| Gene/transcript/protein | NCBI Gene, Ensembl, UniProt, InterPro, Human Protein Atlas | Stable IDs, aliases, species, linked primary references |
| Human variation | dbSNP, LitVar2, ClinVar, gnomAD, Ensembl Variation | HGVS/rsID/VCV/RCV context and linked publications |
| Rare disease/phenotype | HPO, Monarch, Orphanet, GARD, ClinGen | Stable disease/phenotype terms and curated references |
| Drugs/chemistry | ChEMBL, PubChem, Open Targets | Compound identity, target, assay, and linked publications |
| Trials/regulation | ClinicalTrials.gov, WHO ICTRP, FDA, EMA and national regulators | Registry ID, status, intervention, canonical safety or regulatory statements |
| Pharmacogenomics | ClinPGx/PharmGKB, CPIC | Gene–drug relationships and guideline references |
| Pathways/interactions | Reactome, WikiPathways, STRING | Stable pathway/interaction IDs and publications |
| Expression/epigenomics | GEO, SRA, ENA, Expression Atlas, GTEx, ENCODE | Dataset accessions and associated publications |
| Single-cell/spatial | CELLxGENE, Human Cell Atlas, Single Cell Expression Atlas | Collection IDs, tissue/cell context, and publications |
| Proteomics/metabolomics | PRIDE, ProteomeXchange, MetaboLights, Metabolomics Workbench | Project/study accession and publication |
| Model organisms | Alliance of Genome Resources and organism-specific databases | Ortholog/phenotype context and primary references |
| Software/benchmarks | Project repository, archival release, Zenodo, benchmark repository | Version, license, dataset, protocol, and primary paper |
| Access/citation graph | DOI.org, Unpaywall, OpenCitations, Semantic Scholar | Canonical DOI, OA location, and citation relationships |

Set `target_sources` on imported web runs. Database assertions remain attributed source facts or expansion clues. See [web-search-input.md](web-search-input.md) for the exact import contract.

## Authentication

All optional configuration is local:

```bash
export LITERATURE_CONTACT_EMAIL='research@example.org'
export OPENALEX_API_KEY='...'
export NCBI_API_KEY='...'
export SEMANTIC_SCHOLAR_API_KEY='...'
export CORE_API_KEY='...'
export OPENCITATIONS_ACCESS_TOKEN='...'
```

`LITERATURE_CONTACT_EMAIL` identifies the caller to polite API pools and is required for Unpaywall. OpenAlex, NCBI, Semantic Scholar, and OpenCitations can operate without a key but may have lower quotas. CORE requires its key. Credentials and contact email are never emitted and are redacted from errors.

## Failure And Licensing Boundaries

Each route reports `ok`, `error`, `skipped`, or `not_run`, endpoint, counts, and structured retryability where available. A successful zero-result response is `ok`; a timeout is not zero. One failure never discards another source's records.

Do not scrape or automate COSMIC, OncoKB, KEGG, CNKI, Wanfang, VIP, SinoMed, or another licensed/institution-bound source without explicit authorized access. Do not bypass authentication, robots rules, quotas, regional controls, or controlled-access governance. MedDRA and other licensed vocabularies must be caller-supplied local packs with appropriate rights.

## Primary Documentation

- [Europe PMC REST](https://europepmc.org/RestfulWebService)
- [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api)
- [Open Targets GraphQL](https://platform-docs.opentargets.org/data-access/graphql-api)
- [GWAS Catalog API](https://www.ebi.ac.uk/gwas/rest/api/v2/docs)
- [Reactome Content Service](https://reactome.org/dev/content-service)
- [UniProt REST](https://www.uniprot.org/help/api_queries)
- [OpenAlex API](https://developers.openalex.org/api-reference/introduction)
- [Crossref REST](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
- [DataCite API](https://support.datacite.org/docs/api)
- [Semantic Scholar API](https://www.semanticscholar.org/product/api)
- [OpenCitations COCI](https://opencitations.net/index/coci/api/v1)
- [Unpaywall API](https://unpaywall.org/products/api)
- [HGNC REST](https://www.genenames.org/help/rest/)
- [EBI OLS4](https://www.ebi.ac.uk/ols4/help)
