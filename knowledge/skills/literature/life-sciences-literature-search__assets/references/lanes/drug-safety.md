# Drug Safety And Pharmacovigilance

Use `drug-safety` for adverse events, tolerability, organ toxicity, post-marketing signals, special populations, interactions, combination therapy, class effects, and regulatory safety updates.

## Entity Framework

| Role | Concept types | Planning use |
|---|---|---|
| Exposed product | `drug`, `compound`, `chemical`, `intervention`, `drug_class` | Resolves identity, formulation, and class scope |
| Safety outcome | `adverse_event`, `adverse_effect`, `toxicity`, `safety_event` | Keeps each requested event visible and terminology-audited |
| Treatment context | `disease`, `indication`, `condition` | Separates indication-specific dose, regimen, and baseline risk |
| Population | `population`, `age_group`, `special_population` | Scopes pediatrics, older adults, pregnancy, organ impairment, or other groups |
| Co-exposure | `co_medication`, `combination`, `comparator` | Supports interaction and combination-safety lanes |
| Exact anchor | `trial_id`, DOI/PMID, drug or registry ID | Resolves known records before broad safety discovery |

Specify the product, indication, regimen or formulation when material, and named adverse events if the question is not an overall safety profile.

## Planned Lanes

| Depth | Lane | Evidence purpose |
|---|---|---|
| Any | `exact_lookup` when applicable | Resolve known papers, trials, or identifiers |
| Any | `requested_events` or `overall_safety` | Retrieve named events or map the principal reported safety profile |
| Any | `trial_safety` | Find treatment-emergent adverse events and tolerability in trials |
| Standard/deep | `postmarketing_signals` | Retrieve pharmacovigilance, disproportionality, and post-marketing literature |
| Standard/deep | `case_reports` | Find rare or emerging events in case reports and case series |
| Standard/deep | `serious_outcomes` | Retrieve serious and organ-specific outcomes |
| Any when population supplied | `special_populations` | Scope safety evidence to the requested population |
| Any when co-exposure supplied | `interactions_combinations` | Find drug–drug and combination-treatment safety evidence |
| Deep | `class_effect` | Compare requested events across a pharmacological class |
| Deep | `regulatory_updates` | Discover label changes, boxed warnings, and safety communications for canonical verification |

Keep evidence layers separate. Trial adverse-event proportions, spontaneous-report signals, case reports, observational associations, mechanistic studies, and regulator actions answer different questions.

Drug/brand/development-code identity is resolved before planning by the audited terminology layer and, when available, represented as a typed drug object. It is not a publication-search lane: general papers that merely mention the product must not consume the safety evidence budget.

## Terminology And Sources

Ontology pack: WHO INN/local drug map, ChEMBL, ChEBI, PubChem, RxNorm, ATC, MedDRA, and MeSH.

Core sources are supplemented at standard depth by PubTator3, ClinicalTrials.gov, and Crossref. Deep depth can add Open Targets, CIViC, and OpenAIRE. MedDRA expansion requires a caller-provided licensed local pack; without it, retain the literal event plus available MeSH terms and disclose the degradation. Use native web for canonical regulator communications and label pages rather than treating a search snippet as a regulatory fact.

## Output Contract

Build a safety report with:

1. normalized drug/product and adverse-event scope;
2. a safety-signal matrix by event, evidence type, population, comparator, seriousness, and time window;
3. separate trial, observational, pharmacovigilance, case, and mechanistic evidence layers;
4. serious outcomes and temporal pattern where supported;
5. special populations;
6. interactions and combination therapy;
7. class-effect evidence and canonical regulatory updates;
8. consistency, conflicts, reporting bias, and coverage limitations.

Report registry trial facts and linked papers as distinct objects. Do not calculate incidence from spontaneous reports or combine incomparable denominators.

## Risks And Stop Conditions

- A pharmacovigilance signal is hypothesis-generating; it does not establish causality or incidence.
- Case reports support plausibility and rarity discovery, not frequency estimates.
- Trial populations, ascertainment windows, doses, comparators, and event coding may differ.
- Confounding by indication, disease severity, concomitant medication, and stimulated reporting can dominate observational signals.
- Class effects cannot be assumed from one product, and product-specific formulation effects cannot be generalized to a class.

At quick depth, stop after audited identity normalization, requested-event evidence, and trial-safety orientation. At standard depth, require at least trial plus post-marketing/observational layers and rare-event discovery where relevant. At deep depth, add class, special-population, interaction, negative/conflicting, and regulatory coverage. Stop when each requested event has an explicitly stated evidence layer or gap and two focused variants add no verified evidence.
