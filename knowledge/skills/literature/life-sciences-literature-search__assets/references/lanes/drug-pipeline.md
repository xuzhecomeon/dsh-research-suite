# Drug Pipeline And Competitive Landscape

Use `drug-pipeline` for an as-of landscape of therapeutic assets, sponsors, modalities, clinical phases, active and discontinued programs, trials, and linked publications.

## Entity Framework

| Role | Concept types | Planning use |
|---|---|---|
| Target | `target`, `gene`, `protein` | Defines the biological program |
| Indication | `disease`, `indication`, `condition` | Prevents assets in unrelated diseases from being conflated |
| Asset | `drug`, `compound`, `asset`, `intervention`, `chemical` | Retains INN, brand, development code, salt/form, and combination provenance |
| Organization | `sponsor`, `company`, `organization` | Links sponsors to assets and trials without making sponsor intrinsic to the drug |
| Modality | `modality`, `therapeutic_modality`, `drug_class` | Supports modality-specific competition |
| Trial state | `trial_id`, `trial_phase`, `trial_status` | Exact registry resolution and scoped status filtering |

A useful landscape normally needs target or asset plus indication. Record the retrieval date because registry status, ownership, and development state change.

## Planned Lanes

| Depth | Lane | Evidence purpose |
|---|---|---|
| Any | `exact_lookup` when applicable | Resolve NCT, DOI, PMID, asset, or other stable identifiers |
| Any | `asset_identity` | Resolve INN, brand, development code, target, and modality identity |
| Any | `target_indication_assets` | Discover assets for the scoped target–indication combination |
| Any | `active_trials` | Retrieve recruiting and other active interventional trials |
| Any when modality supplied | `modality_competitors` | Compare competitors within the requested therapeutic modality |
| Any when sponsor supplied | `sponsor_asset` | Resolve sponsor–asset and sponsor–trial relationships |
| Standard/deep | `completed_trials` | Find completed trials and available registry results |
| Standard/deep | `trial_results_publications` | Link registered trials to peer-reviewed results publications |
| Standard/deep | `discontinued_programs` | Actively search terminated, withdrawn, suspended, failed, and negative programs |
| Deep | `pivotal_evidence` | Retrieve first-in-human, pivotal, and late-stage evidence |
| Deep | `regulatory_milestones` | Discover approval and designation candidates requiring canonical verification |

ClinicalTrials.gov is queried both as a publication-seed adapter and as a first-class registry source. Registry objects belong in `objects.trials`; linked result papers belong in `objects.papers` with explicit relations.

## Terminology And Sources

Ontology pack: WHO INN/local drug map, ChEMBL, ChEBI, PubChem, HGNC, UniProt, MONDO, EFO, therapeutic-modality terms, clinical-trial terms, and sponsor aliases.

Core sources are supplemented at standard depth by ClinicalTrials.gov, Open Targets, PubTator3, and Crossref. Deep depth can add CIViC, Reactome, UniProt, and OpenAIRE. Use the native-web lane for regulator and sponsor pages, other registries, and current ownership statements; verify them on canonical pages before treating them as facts.

## Output Contract

Produce an as-of landscape with:

1. scope, retrieval date, target, indication, and inclusion rules;
2. normalized assets and unresolved aliases;
3. competitive landscape by asset, modality, sponsor, indication, and development state;
4. typed trial registry table with NCT, phase, status, sponsor, enrollment, dates, countries, interventions, and conditions when available;
5. explicit asset–trial–publication links;
6. discontinued, withdrawn, negative, and unknown programs;
7. pivotal publications and regulatory candidates;
8. freshness, failed routes, and coverage limitations.

Do not store phase, indication, sponsor, or trial status as intrinsic drug fields. These are context-dependent relations or registry facts.

## Risks And Stop Conditions

- INNs, brands, codes, salts, formulations, combination products, and renamed assets are not automatically equivalent.
- Registry status is point-in-time and may lag sponsor announcements; sponsor announcements may be selective.
- “Completed” does not mean results are published. “Terminated” does not by itself state why.
- Absence from ClinicalTrials.gov does not prove absence worldwide.
- Regulatory approval, designation, ownership, and discontinuation claims require canonical regulator, registry, or sponsor verification.

At quick depth, stop after identity plus active-trial orientation. At standard depth, require active, completed, publication-linked, and discontinued/negative dimensions or mark each gap. At deep depth, add pivotal and regulatory verification. Stop when asset aliases are reconciled, new focused routes add no verified asset/trial, and all requested status classes are covered or explicitly unresolved.
