# Evidence Bundle Schema V2

The canonical JSON artifact has `schema_version: "2.0"` and `artifact_type: "life_sciences_evidence_bundle"`. This reference describes the public contract enforced by the dependency-free validator.

## Top Level

| Field | Contents |
|---|---|
| `run` | Run ID, tool version, creation time, retrieval state, primary scenario, depth, and warnings |
| `request` | Structured question, scenarios, concepts, constraints, deliverable, language, sort, expansion, source override, web inputs, and dry-run state |
| `retrieval` | Planned lanes, source routes, ontology packs, budget, normalization audit, source statuses/summary, ledger, constraints, and bounded-search statement |
| `objects` | Typed `papers`, `trials`, `drugs`, `targets`, and `datasets` arrays |
| `relations` | Cross-object relationships and supporting evidence references |
| `result_sets` | Ordered single-type views over object IDs |
| `synthesis` | Evidence claims, sections, reading order, research groups, gaps, and limitations |
| `counts` | Per-collection, relation, and total-object counts verified against the artifact |

Minimal shape:

```json
{
  "schema_version": "2.0",
  "artifact_type": "life_sciences_evidence_bundle",
  "run": {
    "id": "run:...",
    "tool_version": "2.0.0",
    "created_at": "2026-08-21T00:00:00Z",
    "retrieval_state": "performed",
    "scenario": "target-research",
    "depth": "standard",
    "warnings": []
  },
  "request": {},
  "retrieval": {
    "plan": [],
    "routes": [],
    "ontology_packs": [],
    "budget": {},
    "source_status": [],
    "ledger": {},
    "constraints": {},
    "bounded": {"exhaustive": false}
  },
  "objects": {
    "papers": [],
    "trials": [],
    "drugs": [],
    "targets": [],
    "datasets": []
  },
  "relations": [],
  "result_sets": [],
  "synthesis": {
    "status": "not_generated",
    "claims": [],
    "sections": [],
    "reading_order": [],
    "research_groups": [],
    "gaps": [],
    "limitations": []
  },
  "counts": {
    "papers": 0,
    "trials": 0,
    "drugs": 0,
    "targets": 0,
    "datasets": 0,
    "relations": 0,
    "total_objects": 0
  }
}
```

## Run And Retrieval

`run.retrieval_state` is `performed` or `not_performed`. A dry run uses `not_performed`; planned calls are `not_run`, unavailable counts remain `null`, and no terminology, literature, web import, expansion, registry, or OA-enrichment call is made.

`retrieval.plan[]` contains serialized `QueryLane` values:

- `id`, `scenario`, `purpose`, `query`, `family`, and `sources`;
- `evidence_dimension` and `requested_limit`;
- `run_condition`, `depends_on`, and `context_level`;
- `required_concepts` and `notes`.

`retrieval.routes[]` records `source`, role, scenarios, lane IDs, activation reason, and constraint support. `retrieval.source_status[]` is the detailed call ledger; `source_summary` assigns every source to exactly one of `successful`, `partial`, `failed`, `skipped`, or `not_run`. `partial` means that at least one operation succeeded and at least one failed or was skipped. `retrieval.bounded.exhaustive` is always false. Its execution ceilings distinguish `per_source_record_cap`, `per_lane_request_cap`, `max_calls_per_source`, `planned_source_operations`, and the final result limit; a lane may therefore be planned yet explicitly budget-skipped. Table and review renderers surface an unexecuted evidence dimension, zero-result dimension, or budget skip so a populated table cannot hide a coverage gap; the JSON remains the detailed audit.

## Common Object Rules

Every object has:

- `type` and a globally unique ID beginning with `paper:`, `trial:`, `drug:`, `target:`, or `dataset:`;
- a human-readable `label`;
- canonical identifiers and/or links appropriate to its type;
- `source_refs[]` linking back to provider record, source ID, URL, retrieval time, and query-run IDs;
- a computed `citation` block with eligibility, kind, preferred identifier, canonical links, and reason codes;
- type-specific fields and optional `attributes` for source-specific facts.

Objects from different collections cannot share IDs. Fields that represent relationships are forbidden when embedded in the wrong object; use `relations[]`.

## Paper Object

Important fields:

- `title`, `authors[]`, and normalized `identifiers` (`doi`, `pmid`, `pmcid`, `arxiv`, plus other known source IDs);
- `publication`: `year`, `date`, `venue`, `types[]`, `language`, volume, issue, pages/article number, publisher, publication states, retraction and correction flags;
- `study_design`: structured design details when actually assessed;
- `assessment`: evidence type and quality, defaulting to `not_assessed`;
- `links.canonical` and optional `links.open_access`;
- `metrics.citation_counts`, kept by source;
- `verification.level`, such as `structured_confirmed`, `web_metadata_verified`, or `web_unverified`;
- `ranking`: final rank, score components, and contributing source/family lanes;
- `attributes`: snippet, matched variants/families/lanes/scenarios, evidence dimensions, source enrichment, and variant context.

### Content Support

`content_support` is mandatory:

```json
{
  "highest_inspected": "abstract",
  "metadata": {
    "status": "verified",
    "source_refs": ["source:europepmc:123"]
  },
  "abstract": {
    "status": "available",
    "text": "...",
    "language": "en",
    "source_refs": ["source:europepmc:123"]
  },
  "full_text": {
    "availability": "open",
    "retrieval_status": "not_attempted",
    "inspection_status": "not_inspected",
    "url": "https://...",
    "license": null,
    "source_refs": [],
    "locator_hash": null
  }
}
```

Allowed metadata states are `verified`, `partial`, `unverified`, and `missing`. Abstract states are `available`, `unavailable`, and `not_checked`. Full-text availability is `open`, `restricted`, `unavailable`, or `unknown`; retrieval is `not_attempted`, `retrieved`, or `failed`; inspection is `not_inspected`, `partially_inspected`, or `inspected`.

`highest_inspected` is derived: metadata unless a real abstract is available; abstract unless retrieved full text was at least partially inspected. `availability: open` requires a URL but never implies inspection.

## Trial Object

A trial contains:

- `registry`, `registry_id`, `identifiers`, title/label, and canonical registry link;
- current `status`, `phases[]`, `study_type`, structured `design`, and `enrollment`;
- `conditions[]`, `interventions[]`, lead `sponsor`, `collaborators[]`, and `countries[]`;
- `dates` such as start, primary completion, completion, first posted, and last update posted;
- `record_support.level: database`, source references, attributes, and citation eligibility.

Trial facts are as-of registry facts. Trial objects cannot embed papers or publication IDs. Link them with a relation such as `trial_has_publication`.

## Drug Object

A drug contains `preferred_name`, identifiers, aliases, brand names, development codes, modality, optional composition, canonical source link, record support, and attributes.

Phase, status, sponsor, indication, trial IDs, and linked publication IDs are forbidden intrinsic drug fields because they are context-dependent. Represent them with trials, relations, or source-attributed attributes appropriate to the fact.

## Target Object

A target contains name, optional symbol, identifiers, target type, organism, aliases, canonical source link, record support, and attributes.

Disease associations and linked publications are not intrinsic target fields. Keep them as source assertions or relations with evidence.

## Dataset Object

A dataset contains title, repository, accession, identifiers, resource type, data types, modalities, organism, sample count when known, access metadata, canonical source link, record support, and attributes.

Papers and associated-data claims cannot be embedded in a dataset. Use `dataset_described_by_paper` or another explicit relation.

## Relations

Each relation requires:

```json
{
  "id": "relation:...",
  "subject_id": "trial:clinicaltrials.gov:NCT00000000",
  "predicate": "trial_has_publication",
  "object_id": "paper:pmid:12345678",
  "qualifiers": {},
  "evidence_refs": []
}
```

Subject and object must resolve to bundle object IDs or an explicitly external `concept:` reference. Evidence references cannot point to missing objects.

The current execution path creates `trial_has_publication` when a ClinicalTrials.gov-linked PMID resolves to a paper already present in the bundle, and creates `trial_tests_drug` only for an exact normalized intervention/drug-name match. A DataCite dataset may create `dataset_described_by_paper`, `dataset_supplements_paper`, or `dataset_related_to_paper` only when an explicit related DOI resolves to a paper already present in the bundle; the original relation type and locator remain auditable. Drug–paper and target–paper predicates remain valid when explicitly supplied with provenance, but are not inferred from mere co-occurrence.

## Result Sets

A result set has `id`, exactly one `object_type`, an ordered list of object IDs, sort description, and localized label. IDs may not repeat, point to missing objects, or mix types. Default sets are `papers`, `trials`, `drugs`, `targets`, and `datasets` when the respective collection is nonempty.

## Synthesis

`synthesis.status` is `not_generated`, `partial`, or `generated`. The CLI does not manufacture findings from titles; without supplied claims it remains `not_generated`.

Each claim requires:

- unique `id`, `kind`, and localized `text` with `zh` and/or `en`;
- `basis`: `retrieved_evidence`, `model_background`, or `user_context`;
- `method`: `direct_extract`, `model_synthesis`, or `source_assertion`;
- `support_level`: `metadata`, `abstract`, `full_text`, or `database`;
- `evidence[]`, confidence, and limitations.

A retrieved-evidence claim needs at least one eligible object. Model-background and user-context claims cannot masquerade as retrieved evidence. Paper support cannot exceed `content_support.highest_inspected`; full-text support needs a locator with kind and value. Database support cannot cite a paper.

Sections refer to claim IDs. Reading order and research groups refer to existing object IDs. Gaps may be structured objects or valid claim IDs. Renderers ignore unsupported prose rather than deriving findings from result titles.

## Citation Eligibility

For a paper, citation eligibility requires a DOI, PMID, PMCID, or arXiv ID; non-unverified metadata; and a verification state other than `web_unverified`. The preferred identifier order is DOI, PMID, PMCID, arXiv.

For a trial, eligibility requires registry, registry ID, and canonical URL. For a drug, target, or dataset, it requires a stable database identifier and canonical URL. Eligible trials and database objects may support linked factual claims, but formal bibliography exports remain paper-only.

## Validation Invariants

The validator rejects:

- wrong schema/artifact versions, missing typed collections, duplicate IDs, or count mismatches;
- an object in the wrong collection or relationship fields embedded in an object;
- inconsistent citation eligibility;
- invalid content states, abstract text without `available`, inspected full text that was not retrieved, or open content without a URL;
- relations, result sets, claims, sections, reading order, or groups pointing to missing IDs;
- evidence claims without eligible support or claims whose declared support exceeds inspected content.

Validate the canonical JSON before rendering a table, review, or bibliography export.
