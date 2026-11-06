# Intent, Request Structure, And Search Depth

Use this reference before planning when a natural-language request must be turned into a `SearchRequest`. The aim is to preserve the user's scientific decision, not merely extract keywords.

## Request Model

Every request has six independent axes:

| Axis | Question to answer | v2 field |
|---|---|---|
| Scientific question | What decision or understanding should the evidence support? | `question` |
| Search depth | How much recall, dimensional coverage, and cost is justified? | `depth` |
| Evidence framework | Which domain structure makes the evidence comparable? | `primary_scenario`, `scenarios` |
| Typed entities | Which things and relationships must remain independently visible? | `concepts[]` |
| Hard constraints | Which metadata properties must a returned paper satisfy? | `constraints` |
| Deliverable | Does the user need records, a matrix, a narrative, or a landscape? | `deliverable`, `output_language`, renderer format |

Do not replace a missing scientific decision with a generic “find all papers” objective. Ask a focused question only when the answer changes the scenario, required concepts, hard filters, or acceptable evidence type. Otherwise make a conservative assumption and disclose it.

## Recognize The Retrieval Intent

These intents can occur within any scenario:

| Intent | Planning behavior |
|---|---|
| Exact lookup | Preserve DOI, PMID, PMCID, NCT, HGVS, rsID, ontology ID, or dataset accession; run exact lane before expansion |
| Entity relationship | Keep each entity typed and build relationship-specific conjunctions, such as target × indication or drug × event |
| Topic discovery | Use a compact central topic plus a small number of context or evidence-type lanes |
| Evidence comparison | Split evidence dimensions and negative/counter-evidence into separate lanes; do not rank everything by one keyword score |
| Landscape | Include identity resolution, active and inactive entities, relationships, freshness, and known coverage gaps |
| Citation neighborhood | Retrieve verified seeds first, then use exactly one bounded citation/related-paper expansion round |
| Metadata screening | Express year, type, author, venue, language, identifiers, access, preprint, and retraction requirements as constraints |
| Content screening | Treat outcomes, sample sizes, effect estimates, subgroup results, and mechanistic findings as abstract/full-text extraction, not metadata filters |

## Typed Concepts

A concept retains both the user's input and any audited normalization:

```json
{
  "type": "target",
  "input": "PCSK9",
  "role": "primary",
  "canonical_id": "HGNC:20001",
  "canonical_label": "PCSK9",
  "synonyms": [],
  "descendants": [],
  "mapping_status": "exact_label",
  "resolver": "hgnc",
  "ontology": "HGNC",
  "confidence": "high",
  "expansion": "exact_and_synonyms",
  "provenance": {}
}
```

Use concept types that express domain meaning. Common types include:

- biology: `topic`, `process`, `pathway`, `organism`, `species`, `tissue`, `cell_type`;
- targets: `target`, `gene`, `protein`, `indication`, `modality`;
- drugs: `drug`, `compound`, `chemical`, `drug_class`, `asset`, `sponsor`, `adverse_event`, `co_medication`;
- clinical: `condition`, `population`, `intervention`, `comparator`, `outcome`, `endpoint`, `study_design`, `biomarker`;
- methods: `method`, `algorithm`, `software`, `task`, `data_modality`, `dataset`, `accession`, `benchmark`, `metric`;
- genetics: `gene`, `disease`, `rare_disease`, `variant`, `allele`, `hgvs`, `rsid`, `phenotype`, `hpo`, `inheritance`, `mechanism`;
- identifiers: `identifier`, `doi`, `pmid`, `pmcid`, `trial_id`, `accession`.

Repeated concepts are independent by default. Never treat two drug names, variant forms, disease labels, or dataset IDs as equivalent unless the user or a trusted resolver supplies that relationship. Put roles in `role` instead of encoding them in the value. `exclude` is compiled as an audited negative clause and is never allowed into a positive term group or result object. For query frameworks that distinguish arms, prefer the scenario-native `comparator` concept/CLI flag; `primary` and `comparator` role labels remain available for downstream synthesis but do not replace the typed PICO fields.

## Hard Constraints

Use constraints only for user requirements, not as speculative precision improvements:

| Constraint | Semantics |
|---|---|
| `year_from`, `year_to` | Inclusive range; source pushdown where available, bounded post-filter otherwise |
| `publication_types` | OR within the include list; do not infer an indexed type from colloquial wording |
| `excluded_publication_types` | Exclude explicit type matches after bounded retrieval |
| `authors`, `venues`, `languages` | OR within one field, AND across fields; metadata may be incomplete |
| `species` | Source-native where supported; elsewhere encoded in query and reported as partial support |
| `required_identifiers` | Require stable identifiers such as DOI, PMID, PMCID, or arXiv ID |
| `open_access` | Require a known open location; this can reduce recall |
| `require_abstract` | Require returned abstract metadata; this is not full-text availability |
| `exclude_preprints` | Remove explicit preprints, not records whose status is simply unknown |
| `include_retracted` | Default false; enable only for retraction or research-integrity questions |
| `has_associated_data` | Use indexed data linkage where supported; missing indexing is not evidence of no data |

Repeated values within a constraint use OR semantics; different constraint fields combine with AND semantics. Keep ranking preferences (`relevance`, `newest`, `citations`) separate from eligibility constraints.

## Depth Budgets

The defaults are deterministic and global across all selected scenarios:

| Budget | `quick` | `standard` | `deep` |
|---|---:|---:|---:|
| Per source | 8 | 15 | 30 |
| Per lane | 6 | 12 | 20 |
| Maximum calls per source | 4 | 8 | 16 |
| Final paper limit | 8 | 20 | 40 |
| Maximum lanes | 4 | 14 | 32 |
| Maximum structured sources | 6 | 12 | 21 |
| Native-web run guidance | 0–2 | 2–6 | 6–12 |
| Automatic expansion | none | one seed-based related fallback only if results remain weak | citations + related |
| Expansion seeds | 0 | 3 | 5 |
| Per seed/relationship | 0 | 10 | 20 |
| Weak-result rescue threshold | 3 | 5 | 8 |

`Per source` is a total retrieved-record cap for the structured source, not a cap repeated for every lane. `Per lane` is the maximum request size before the remaining source quota is applied. At execution time, the remaining source records are divided deterministically across the remaining callable lanes, so an early identity or orientation lane cannot consume the entire budget before a critical evidence lane runs. Calls beyond the per-source call cap are retained in the plan but recorded as budget-skipped in the execution ledger.

Select depth by decision value:

- Choose `quick` for exact IDs, confirmation of a known paper, a narrow current-status check, or an initial vocabulary probe.
- Choose `standard` for a research brief, evidence table, initial target assessment, drug safety summary, PICO search, or methods comparison.
- Choose `deep` for a competitive landscape, comprehensive target assessment, multiple adverse-event layers, explicit contradictory/negative evidence, a broad methods benchmark, or genetic evidence with multiple variants and phenotypes.

Do not choose `deep` merely because the topic is important. A narrow high-stakes exact lookup may be quick but still requires careful verification. Conversely, a low-stakes landscape may need deep recall.

## Scenario Selection

Automatic detection uses both the question and concept types. Strong intent terms and structured entities outweigh generic words such as “research” or “literature.” If several detectors score similarly:

1. Prefer the framework implied by the requested deliverable: pipeline table, safety matrix, PICO table, benchmark, or gene/variant evidence.
2. Prefer the object whose status is being compared: targets → `target-research`; assets/trials → `drug-pipeline`; adverse events → `drug-safety`.
3. Use `general-basic` only when no specialized framework improves interpretation.

Use multiple scenarios sparingly. Examples that justify it include target assessment plus pipeline translation, or clinical efficacy plus drug safety. The planner interleaves each scenario's priority lanes so every selected scenario gets representation before filling the shared budget.

## Deliverable And Language

`list` and `table` are appropriate when retrieval facts are enough. `review` requires evidence-grounded claims and must state when synthesis was not generated. `landscape` requires typed non-paper objects, relations, an as-of date, and explicit inactive/negative or missing dimensions where the scenario calls for them.

Choose `zh`, `en`, or `bilingual`. Keep scientific identifiers unchanged. Translate narrative only when translation is available; a renderer must label a missing language rather than silently inventing it.

## Retry And Stop Policy

After the planned lanes run:

1. Inspect whether required evidence dimensions succeeded, not only the final result count.
2. If verified merged results are below the depth threshold, execute only the predeclared rescue lane. At standard depth, a non-exact request may then use one seed-based related-paper fallback; without an eligible seed it is explicitly skipped.
3. Make at most one further focused retry when a recoverable source failure or an overly narrow nonessential term clearly explains the gap.
4. Stop when two materially different query variants add no verified candidate, the depth budget is exhausted, or required dimensions are adequately represented.
5. Report critical missing dimensions, unavailable licensed terminology, source failures, and uncertain mappings. Do not compensate by strengthening the conclusion.

For the mechanics behind normalization, lane dependencies, routes, and ranking, continue with [query-planning.md](query-planning.md).
