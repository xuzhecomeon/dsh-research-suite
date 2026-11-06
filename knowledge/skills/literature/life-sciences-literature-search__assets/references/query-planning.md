# Query Planning And Execution

Use this reference to inspect or explain how a structured request becomes auditable retrieval lanes and source routes.

## Planning Pipeline

```text
natural-language question
  → typed SearchRequest
  → conservative concept normalization
  → primary and optional secondary scenario planners
  → prioritized QueryLane objects
  → capability-aware SourceRoute objects
  → structured APIs + imported native web
  → paper reconciliation and first-class registry/database objects
  → schema-v2 evidence bundle
```

The planner separates intent, concepts, constraints, and output. It does not create one universal Boolean query, and it does not assume that every source can answer every lane.

## Conservative Normalization

Normalization improves query coverage while keeping the user's term auditable. It may resolve:

| Concept | Resolver or pack | Acceptance rule |
|---|---|---|
| Gene/target | HGNC | Exact ID, symbol, label, or unique exact synonym |
| Disease/indication | OLS4 MONDO | Exact ID, label, or unique exact synonym |
| Phenotype/HPO | OLS4 HPO | Exact ID, label, or unique exact synonym |
| Compound/chemical | OLS4 ChEBI | Exact ID, label, or unique exact synonym |
| Drug/brand/development code | ChEMBL molecule search; optional local INN map | Accepted only when the identity match is exact and provenance is retained |
| GO/pathway, cell type, tissue | OLS4 GO, CL, UBERON | Exact ID, label, or unique exact synonym |
| Biomedical subject heading | MeSH lookup | Exact normalized label match |
| Organism/species | NCBI Taxonomy | Exact scientific/common-name match |
| Study design | Controlled local list | Exact controlled label or synonym |
| Adverse event | Optional licensed local MedDRA map | Exact local-pack match; otherwise literal/MeSH degradation |
| Chinese topic | Optional local CMeSH map | Exact local-pack match; otherwise preserve input |
| Drug class | Optional local ATC map | Exact class label or alias only |
| Method/data modality | Optional local EDAM map | Exact method or data label/alias only |
| Assay | Optional local OBI map | Exact assay label/alias only |
| Therapeutic modality | Optional local modality map | Exact modality label/alias only |
| Sponsor | Optional local sponsor-alias map | Exact organization alias only |
| Stable IDs | Local patterns | HGNC, MONDO, HP, ChEBI, ChEMBL, MeSH, rsID, NCT, GEO, SRA, ArrayExpress |

Every concept retains `input`, normalized ID and label, synonyms, `mapping_status`, resolver, ontology, confidence, expansion policy, and provider provenance. Provider failure, no match, or ambiguity never deletes or replaces the original input. Do not infer equivalence between brands, development codes, salt forms, combination products, transcripts, HGVS forms, or variants.

Use `--include-descendants` only when a broader ontology subtree serves the question. It expands an accepted OLS concept with at most 20 audited child terms; it is never an unbounded default. Use `--mesh-heading` together with `--mesh-subheading` for an intentional qualified PubMed concept, not as a generic synonym shortcut. Repeated headings and subheadings form an audited cross-product of at most three values from each field, so inspect a dry run before using several.

Use `--no-normalize` when terminology services are undesired. A dry run performs no terminology or retrieval calls and reports planned rather than zero counts.

## QueryLane Contract

Each lane has one evidence purpose:

| Field | Meaning |
|---|---|
| `id` | Stable scenario-qualified identifier, such as `target-research.human_genetic_support` |
| `scenario` | Evidence framework that owns the lane |
| `purpose` | Human-readable reason for the query |
| `query` | Bounded expression sent to compatible sources |
| `family` | Ranking and audit family, not a separate vote per cosmetic rewrite |
| `sources` | Exact structured sources allowed for the lane |
| `evidence_dimension` | Output dimension the lane is intended to cover |
| `requested_limit` | Per-lane budget |
| `run_condition` | `always` or `if_dependency_zero` |
| `depends_on` | Earlier lane required by a conditional lane |
| `context_level` | Strict, broad, or other interpretation context |
| `required_concepts` | Concept types expected for meaningful interpretation |
| `notes` | Scientific or operational caveats |

Exact identifier lanes run before topical expansion. Within one scenario, planners order lanes by scientific value. With multiple scenarios, the global planner interleaves their priority order, then truncates to the depth budget while preserving dependencies.

Queries are capped in length and retain exact identifiers. Synonyms are grouped with OR; independent concepts and evidence dimensions use AND. Repeated independent variants, phenotypes, drugs, or datasets should normally receive separate lanes rather than one giant disjunction.

A concept with `role: exclude` is omitted from all positive entity groups and first-class concept objects, then compiled as an explicit `NOT` clause on non-identifier lanes. Inspect this clause in dry-run output because negative retrieval can reduce recall. Use scenario-native comparator fields for PICO/safety comparisons; a generic role label alone does not invent a comparison design.

## Conditional Lanes

Two conditions prevent uncontrolled broadening:

### Per-source zero-result fallback

`if_dependency_zero` is used for a strict-to-broad relationship such as variant + gene + disease → variant + gene. The broad lane runs independently for a source only when that source's strict call:

- completed with `status: ok`;
- reported or returned a known zero;
- did not fail, time out, block, or become inapplicable.

A strict failure is not a zero-result finding. Broad genetic results retain broad context and require disease-text auditing and down-ranking before interpretation.

### Global weak-result fallback

Weakness is evaluated from verified/citation-eligible merged papers, not unverified web candidates. At standard depth with `auto`, the executor may make one Semantic Scholar related-paper request from verified, non-retracted seeds. It does not rerun the same lexical expression under a `related` label. With no eligible seed, the fallback is recorded as skipped and the artifact does not claim semantic coverage.

## Source Routing

Every scenario begins with four scholarly core sources—Europe PMC, PubMed, Semantic Scholar, and OpenAlex—then adds scenario-specific adapters. `quick` receives a small slice of the scenario pack; `standard` receives the standard pack; `deep` adds deep-only sources, subject to global source limits.

Each `SourceRoute` records source role, scenarios, eligible lane IDs, activation reason, and constraint-support level. A source receives only its routed lanes. An explicit `--source` override replaces capability routing and may therefore produce disclosed skips when an adapter cannot execute the requested operation.

An explicit source override also bounds external retrieval providers: Semantic Scholar graph expansion runs only when `semantic-scholar` is selected, OpenCitations and Unpaywall enrichment are disabled under an exact override, and first-class registries run only when their source is selected. Terminology normalization is a separate resolver step; use `--no-normalize` when an exact source-only run must make no resolver calls.

Reactome and the current UniProt adapter are fixed to human data. They are removed for an explicit non-human species request. Other species constraints are native only where supported and otherwise remain query terms plus bounded metadata screening. See [sources.md](sources.md) for the full capability and limitation matrix.

## Execution Order

1. Import any prepared native-web files; each search run remains an independent audit entry.
2. Execute all unconditional structured source routes concurrently, consuming results in deterministic plan order.
3. Normalize source statuses and reconcile candidate papers.
4. Evaluate verified/citation-eligible coverage against the weak-result threshold.
5. For `deep`, or when explicitly enabled, expand verified non-retracted seeds once through Semantic Scholar; add OpenCitations for citation relationships. At standard depth with `auto`, weak non-exact retrieval may perform one seed-based related-paper fallback; if no eligible seed exists, record it as skipped rather than claiming semantic coverage.
6. Outside `quick`, use Unpaywall only to enrich already relevant DOI records when a contact email is configured. Its zero ranking weight cannot create relevance.
7. Fetch ClinicalTrials.gov first-class trial objects for target, pipeline, safety, and clinical scenarios when registry objects are enabled.
8. Build target/drug objects from exact normalized concepts or conservative exact Open Targets matches, and dataset objects from stable accessions or DataCite dataset/collection records; require stable IDs and canonical URLs.
9. Emit the evidence bundle with all planned lanes, routes, constraints, normalization attempts, statuses, ledger, warnings, and typed results.

## Paper Reconciliation And Ranking

Paper records merge by strongest available key: DOI, PMID, PMCID, arXiv ID, then normalized title. Source records, matched queries, scenarios, lanes, and evidence dimensions remain attached after merging.

The default rank is source/query-family-normalized reciprocal-rank fusion plus bounded lexical coverage. Only the best occurrence of a document in a source/family lane contributes; repeated cosmetic queries cannot manufacture votes. Metadata verification and genetic broad-context signals may adjust rank. `newest` and `citations` are explicit alternatives; citation counts remain source-specific and are not a quality score.

The final paper limit does not cap trial, drug, target, or dataset objects. Those have independent typed collections and result sets.

## Native Web As A Separate Lane

The Python process cannot invoke the host Agent's browser or network-search tool. When such a tool is available and allowed, the Agent performs materially different searches, verifies promising bibliographic metadata against canonical pages, and imports a bounded JSON artifact. Web runs preserve provider, query family, rank, target sources, and verification claims.

Web snippets are untrusted discovery text. A web-only record may be a candidate, but `metadata_verified` requires opening a canonical publisher, index, repository, regulator, or registry page. Structured API agreement upgrades bibliographic confirmation. See [web-search-input.md](web-search-input.md).

## Audit States

Every source/lane call is one of:

- `ok`: provider responded successfully, including a genuine zero-result response;
- `error`: an attempted call failed; structured error fields state retryability;
- `skipped`: route was inapplicable, lacked a required credential or seed, or a condition was not met;
- `not_run`: dry-run planning only.

Never convert `null` counts from skipped or not-run routes to zero. Read `retrieval.source_summary` for the overview, `retrieval.source_status` for exact calls, and `retrieval.ledger` for family/lane aggregation.

## Retry And Failure Policy

One failing route never invalidates another. Retry only transient, retryable calls within the configured bound. Do not retry a licensed source without authorization, a deterministic invalid query, or a conditionally skipped lane.

After retrieval, distinguish:

- healthy coverage: priority dimensions have at least one eligible object;
- partial coverage: some routes failed or metadata support is incomplete, but the main decision can still be scoped;
- critical gap: an indispensable lane or canonical source failed or returned only ineligible candidates.

For a critical gap, report it and narrow the conclusion. Do not treat absence from this bounded search as biological absence, no treatment effect, no safety signal, or lack of causality.
