# Clinical Evidence

Use `clinical-evidence` for a PICO-oriented synthesis of treatment, diagnostic, prognostic, or biomarker evidence across trials, reviews, observational studies, guidelines, safety, and ongoing research.

## Entity Framework

| PICO+ role | Concept types | Planning use |
|---|---|---|
| Population/problem | `disease`, `condition`, `indication`, `population`, `age_group`, `stage` | Defines clinical eligibility and disease context |
| Intervention | `intervention`, `drug`, `procedure`, `diagnostic_test`, `treatment` | Defines the treatment or test under assessment |
| Comparator | `comparator`, `control` | Preserves the actual counterfactual |
| Outcome | `outcome`, `endpoint` | Separates efficacy, safety, diagnostic, patient-reported, and surrogate outcomes |
| Study design | `study_design` | Scopes RCT, systematic review, cohort, case-control, diagnostic, or guideline evidence |
| Subgroup | `biomarker`, `gene`, `variant`, `target` | Defines biomarker-selected or mechanistic subgroups |
| Exact anchor | `trial_id`, DOI, PMID, PMCID | Resolves a known trial or publication |

If key PICO elements are absent, do not invent them. State the assumed population or outcome and treat unspecified comparator as a coverage gap.

## Planned Lanes

| Depth | Lane | Evidence purpose |
|---|---|---|
| Any | `exact_lookup` when applicable | Resolve known trial/publication identifiers |
| Any | `pico_core` | Retrieve the central population–intervention–comparator–outcome evidence |
| Any | `randomized_trials` | Find randomized and controlled intervention studies |
| Any | `systematic_reviews_meta` | Find systematic reviews and meta-analyses |
| Standard/deep | `observational_real_world` | Retrieve cohort, registry, observational, and real-world evidence |
| Standard/deep | `safety_tolerability` | Retrieve clinical adverse-event and tolerability evidence |
| Standard/deep | `ongoing_trials` | Return current recruiting and ongoing trials as registry objects |
| Any when biomarkers supplied | `biomarker_subgroups` | Assess biomarker-defined or clinically relevant subgroups |
| Deep | `guidelines_consensus` | Discover guideline and consensus candidates requiring canonical verification |
| Deep | `negative_conflicting` | Actively retrieve null, negative, and conflicting evidence |

Search study designs in separate lanes so high-recall registry records, primary studies, and secondary syntheses do not collapse into one undifferentiated rank list.

## Terminology And Sources

Ontology pack: MeSH, optional CMeSH, MONDO, EFO, controlled clinical-study design, PICO terms, WHO INN/local drug map, and ChEMBL.

Core sources are supplemented at standard depth by ClinicalTrials.gov, PubTator3, and Crossref. Deep depth can add DOAJ and OpenAIRE. ClinicalTrials.gov emits first-class trial objects with as-of status; publication adapters emit papers. Use native web for canonical guideline bodies and other trial registries when relevant and authorized.

## Output Contract

Organize the clinical answer as:

1. explicit PICO and eligibility assumptions;
2. evidence hierarchy by design, without treating rank as quality;
3. study table with population, intervention, comparator, outcomes, follow-up, design, and identifiers when inspected;
4. outcomes and effect estimates only from supporting abstract/full text;
5. consistency, conflicts, null/negative evidence, and heterogeneity;
6. biomarkers and subgroups;
7. safety and tolerability;
8. ongoing trials with registry retrieval date;
9. verified guidelines or consensus;
10. evidence gaps and source failures.

Do not infer an effect size, sample size, comparator, endpoint, or risk of bias from title metadata. Registry enrollment and status are database facts, not published outcomes.

## Risks And Stop Conditions

- Different endpoints, estimands, follow-up windows, doses, populations, and comparators may make studies non-comparable.
- Meta-analysis quality depends on included studies and methods; it is not automatically stronger for every question.
- Observational and real-world evidence may be affected by confounding, selection, immortal-time bias, or outcome misclassification.
- Surrogate endpoints and biomarker-defined subgroup results require cautious clinical generalization.
- No retrieved negative study does not mean no negative study exists; publication bias and registry-result gaps matter.

At quick depth, return PICO orientation with primary trials and secondary synthesis. At standard depth, also cover observational evidence, safety, ongoing trials, and requested subgroups. At deep depth, require explicit negative/conflicting and guideline lanes. Stop when each requested PICO element and evidence design is represented or explicitly missing, and additional focused searches yield no verified candidates.
