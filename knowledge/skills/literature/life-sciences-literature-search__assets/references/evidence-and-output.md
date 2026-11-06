# Evidence Interpretation And Output

Use this reference after retrieval or when selecting an output format. The central rule is that evidence objects, relationships, and claims remain separate.

## Evidence Object Boundaries

| Object | Represents | Must not absorb |
|---|---|---|
| `paper` | A bibliographic publication or preprint | Trial phase, sponsor, interventions, or registry state |
| `trial` | A canonical clinical-registry record | Embedded paper objects or publication conclusions |
| `drug` | A normalized drug, compound, asset, or product identity | Phase, status, sponsor, indication, or trial IDs |
| `target` | A normalized gene/protein/target identity | Disease associations or publication IDs as intrinsic fields |
| `dataset` | A repository dataset or research object | Papers or associated-data claims as embedded records |

Put cross-object statements in `relations[]`, for example:

- `trial_has_publication`;
- `drug_described_by_paper`;
- `target_described_by_paper`;
- `dataset_described_by_paper`;
- another explicit predicate with subject, object, qualifiers, and evidence references.

This prevents a current registry fact from being mistaken for a paper's historical report, or a database assertion from being presented as a publication conclusion.

The current executor automatically creates `trial_has_publication` only when a registry PMID resolves to a paper already in the bundle, and `trial_tests_drug` only when a trial intervention name exactly matches a normalized drug name. Other predicates above are supported schema vocabulary, not automatically inferred defaults.

## Paper Content Support

Every paper separates three levels:

| Level | What may be stated |
|---|---|
| `metadata` | Title, authors, venue, date, type, identifiers, URLs, indexing and source provenance |
| `abstract` | Findings explicitly present in the retrieved abstract text |
| `full_text` | Findings supported by retrieved and inspected full text, with a locator |

`content_support.highest_inspected` is derived from actual state. An open link sets full-text `availability: open`; it does not change retrieval or inspection status. A snippet placed in `snippet` is not an abstract. Never upgrade support merely because an API labels an item “full text.”

For a full-text claim, record a locator such as section, table, figure, page, paragraph, or stable fragment. For an abstract claim, quote or paraphrase only what the abstract supports. For metadata-only records, write a relevance note, not a study result.

## Citation Eligibility

Eligibility protects traceable reporting:

- A paper needs a stable DOI, PMID, PMCID, or arXiv ID, verified or partial metadata, and must not remain `web_unverified`.
- A trial needs a registry name, registry identifier, and canonical registry URL.
- A drug, target, or dataset needs a stable database identifier and canonical source URL.
- Ineligible candidates stay visible with reason codes but cannot support retrieved-evidence claims.

Only eligible papers enter BibTeX, RIS, or CSL-JSON. Trials and database objects can support registry/database facts through canonical links, but they are not bibliography entries.

## Claims

A synthesis claim contains:

| Field | Rule |
|---|---|
| `kind` | Scenario-relevant role such as `key_finding`, `negative_evidence`, `gap`, or `limitation` |
| `text.zh`, `text.en` | Supply only available language versions; do not silently machine-fill a missing version |
| `basis` | `retrieved_evidence`, `model_background`, or `user_context` |
| `method` | `direct_extract`, `model_synthesis`, or `source_assertion` |
| `support_level` | `metadata`, `abstract`, `full_text`, or `database` |
| `evidence[]` | Eligible object IDs and optional locators |
| `confidence` | Explicit assessment or `not_assessed`; retrieval rank is not confidence |
| `limitations` | Claim-specific uncertainty and scope |

Claims with `basis: retrieved_evidence` require at least one eligible object. Claims based on model background or user context must not carry retrieved-evidence citations. A database-supported claim cannot cite a paper object. A paper claim cannot request a higher support level than the paper's inspected content.

Separate these often-confused assertions:

- “The registry lists the trial as recruiting as of the retrieval date” is a database claim.
- “The trial showed a clinical benefit” requires an eligible result publication or inspected result record.
- “The database links this target to the disease” is a source assertion.
- “Human genetics supports a causal relationship” requires the underlying study or a clearly scoped synthesis of eligible evidence.
- “A safety signal was reported” does not establish incidence or causality.

## Evidence Assessment

The CLI retrieves and ranks; it does not automatically grade study quality. If the user asks for interpretation, assess within compatible evidence designs:

1. Identify the evidence type and population/model.
2. Check whether the outcome, comparator, and analysis match the question.
3. Record sample size and effect estimate only from inspected abstract or full text.
4. Distinguish primary evidence, secondary synthesis, registry facts, and database assertions.
5. Look for independent replication, contradictory findings, negative results, and bias or confounding.
6. Avoid pooling across incompatible diseases, species, interventions, endpoints, datasets, or metrics.
7. State when quality was not assessed because only metadata or abstract text was available.

Scenario references define the dimensions that belong in each evidence matrix; they do not prescribe a universal quality hierarchy.

## Result Sets

`result_sets[]` give a stable ordered view over one object type. A result set cannot mix papers, trials, drugs, targets, and datasets. Default IDs are the plural collection names. Use the typed view appropriate to the question:

- target or general literature: `papers`, with normalized `targets` as supporting objects;
- pipeline or clinical status: `trials`, plus `papers` for published evidence;
- method selection: `papers` and `datasets`;
- normalized landscape: `drugs`, `targets`, or `datasets` alongside relation-aware narrative.

Object count and final-paper limit are independent. A trial-heavy landscape can contain more registry objects than the paper limit.

## Output Formats

| Format | Contents | Safe fallback |
|---|---|---|
| Canonical JSON | Full schema-v2 bundle, audit trail, objects, relations, result sets, synthesis, counts | Always available after a valid run |
| Markdown table | One typed result set with factual columns and canonical links | Shows no-results text for an absent view |
| Markdown review | Only claims already supplied in `synthesis` plus references | If synthesis is absent, explicitly says so and renders factual results |
| BibTeX | Eligible paper bibliography | Omits ineligible candidates and all non-paper objects |
| RIS | Eligible paper bibliography | Same eligibility rule |
| CSL-JSON | Eligible paper bibliography | Same eligibility rule |

Markdown supports `zh`, `en`, and `bilingual`. Bilingual mode shows both stored language versions; it does not translate them. Citation styles accepted for the review bibliography are Vancouver, Nature, and AMA.

Both readable Markdown formats also summarize planned evidence dimensions that never executed successfully, dimensions that executed with zero results, and the number of source operations skipped by the source budget. This compact warning does not replace `retrieval.source_status`; use the canonical JSON to inspect the exact source, lane, error, and skip code.

## Recommended Human-Facing Answer

Lead with the decision-relevant outcome, then make the search auditable:

1. scope, scenario, depth, retrieval date, and key assumptions;
2. concise answer or evidence map, with each substantive statement linked to eligible evidence;
3. scenario-specific matrix separating papers, trials, and database objects;
4. contradictory or negative evidence and unresolved distinctions;
5. evidence gaps, failed/partial sources, and terminology degradation;
6. bounded-search caveat and next action, such as full-text review of pivotal papers.

For a short list, include title, year, venue, stable identifier/link, source coverage, evidence dimension, and a relevance note supported by available content. Do not fabricate “key findings” for metadata-only records.

For a landscape, include an as-of date and clearly separate active, completed, discontinued, unknown, and publication-backed states. For clinical or safety outputs, never turn the absence of retrieved evidence into “no effect” or “no signal.”

## Synthesis Workflow

If the Agent prepares a narrative from the bundle:

1. Select only eligible objects relevant to the requested scenario dimension.
2. Inspect available abstracts or full text before extracting findings.
3. Create narrowly scoped claims and attach exact object references.
4. Keep model background in a visibly separate section.
5. Build sections from the selected scenario's output contract.
6. Add reading order or research groups only when supported by object metadata and explicit reasoning; never infer them from titles alone.
7. Validate the bundle before rendering if synthesis is written back into JSON.

Use `scripts/render_evidence.py <bundle.json> --synthesis <synthesis.json> --save-bundle <validated.json> --format review` to attach a synthesis object, validate the resulting artifact, and render it. The exact field-level contract and validator invariants are documented in [output-schema.md](output-schema.md).
