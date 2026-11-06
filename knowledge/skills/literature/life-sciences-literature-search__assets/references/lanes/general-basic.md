# General And Basic Life-Science Search

Use `general-basic` for a biological topic, mechanism, organism, pathway, or introductory evidence map when a more specialized decision framework would add little value.

## Entity Framework

| Role | Concept types | Planning use |
|---|---|---|
| Central topic | `topic`, `disease`, `indication`, `gene`, `target`, `protein`, `drug`, `chemical`, `process`, `pathway` | Defines the core discovery expression |
| Biological focus | `research_aspect`, `context`, `mechanism`, `outcome` | Creates a mechanism/question lane |
| Method | `method`, `experimental_method` | Creates a method-specific lane |
| Model | `organism`, `species`, `model`, `model_system` | Creates an organism/model lane; hard species constraints also enter every non-ID query |
| Anatomical context | `tissue`, `cell_type`, `population` | Creates a tissue/cell/population lane |
| Exact anchor | `identifier`, `doi`, `pmid`, `pmcid`, `accession` | Resolves a known record before topic discovery |

If no typed topic is available, the planner uses the cleaned question as the central topic. Keep species, model system, tissue, and disease context distinct when they change interpretation.

## Planned Lanes

| Priority | Lane | Activation | Evidence purpose |
|---:|---|---|---|
| 0 | `exact_lookup` | An exact scientific or bibliographic ID is present | Resolve the known object without synonym broadening |
| 1 | `topic_core` | Always | Retrieve the central life-science topic from core scholarly indexes |
| 2 | `biological_focus` | A research aspect, mechanism, generic context, or outcome is present | Connect the topic to the requested biological question |
| 3 | `method_context` | A method is present | Retrieve studies using that method, without OR-mixing it with the biological focus |
| 4 | `model_context` | An organism or model system is present | Retrieve model-specific evidence |
| 5 | `anatomical_context` | Tissue, cell type, or population is present | Retrieve anatomical/context-specific evidence |
| 6 | `integrated_context` | Deep search with at least two context axes | High-precision AND of the explicitly separate facets |
| 7 | `secondary_evidence` | Deliverable is review/landscape or depth is deep | Find reviews and organizing secondary evidence |

Terms within one concept group are alternatives; distinct scientific facets are ANDed or searched in separate audited lanes. This prevents a request such as `autophagy × lysosome dynamics × zebrafish × live-cell imaging` from collapsing into a broad `(mechanism OR model OR method)` expression.
If a model-system term exactly duplicates the hard species constraint, the planner keeps the species in every non-ID lane and omits the redundant model lane. A distinct model context such as `larval zebrafish`, `organoid`, or a disease model remains a separate lane.
After these lexical lanes, standard `auto` may run one Semantic Scholar related-paper request only when verified results remain weak and an eligible seed exists. This is an execution fallback, not a duplicate lexical lane; without a seed it is recorded as skipped.

## Terminology And Sources

Ontology pack: MeSH, GO, NCBI Taxonomy, MONDO, and EFO.

Core sources are Europe PMC, PubMed, Semantic Scholar, and OpenAlex. The scenario adds PubTator3, Crossref, and Reactome at standard depth; deep depth can add UniProt, DataCite, DOAJ, OpenAIRE, and arXiv. Non-human requests exclude human-fixed Reactome/UniProt adapters and should use explicit organism terms plus appropriate native-web repository routes.

## Output Contract

Organize the answer as:

1. question and scope;
2. ranked literature;
3. topic-and-evidence map by context or evidence type;
4. suggested reading order when justified;
5. research gaps;
6. search coverage and degraded routes.

This scenario normally returns a paper-first result set. Dataset, target, or other objects appear only when a normalized stable identifier supports them.

## Risks And Stop Conditions

- A broad topic can produce high lexical recall but low decision value. Add one meaningful context rather than many generic synonyms.
- Reviews organize a field but do not replace primary evidence for a specific result.
- Cross-species findings require explicit species labels and should not be generalized to humans without translational evidence.
- A related-paper fallback is broad discovery, not stronger evidence.

Stop when the central topic and each user-requested context have eligible coverage, two focused variants add no verified candidates, or the depth budget is exhausted. Escalate to a specialized scenario if the user actually needs a target assessment, pipeline, safety matrix, PICO synthesis, method comparison, or genetic evidence framework.
