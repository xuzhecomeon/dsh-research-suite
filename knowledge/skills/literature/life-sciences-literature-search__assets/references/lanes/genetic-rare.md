# Genetic And Rare-Disease Evidence

Use `genetic-rare` for gene–disease validity, variant and allele evidence, HPO/phenotype matching, inheritance and segregation, cases and cohorts, functional mechanisms, genotype–phenotype relationships, and conflicting evidence.

## Entity Framework

| Role | Concept types | Planning use |
|---|---|---|
| Gene | `gene`, `target` | HGNC-normalized causal or candidate gene anchor |
| Disease | `disease`, `rare_disease`, `condition`, `indication` | MONDO-normalized disease context |
| Phenotype | `phenotype`, `hpo` | HPO ID or free-text clinical feature; bundle and individual rescue use different lanes |
| Variant/allele | `variant`, `allele`, `hgvs`, `rsid` | Each repeated concept is independent unless equivalence is asserted or verified |
| Inheritance | `inheritance`, `mode_of_inheritance` | Scopes segregation, de novo, recessive, dominant, X-linked, or mitochondrial evidence |
| Mechanism | `mechanism`, `molecular_mechanism` | Scopes loss/gain of function, dominant-negative, dosage, splicing, or other mechanisms |
| Population | `population`, `ancestry` | Preserves ancestry, founder, prevalence, or cohort context |

Never put variant forms in one allele group merely because they look similar. Transcript, genome build, reference sequence, coding/protein consequence, and rsID equivalence require user assertion or a dedicated verified normalizer.

## Planned Lanes

| Depth | Lane | Evidence purpose |
|---|---|---|
| Any | `exact_lookup` when applicable | Resolve exact DOI/PMID, HGVS-like, rsID, or stable identifiers |
| Any | `gene_disease_validity` | Retrieve causal association and gene–disease validity evidence |
| Any when phenotypes supplied | `phenotype_bundle` | Match the combined phenotype profile to the gene/disease context |
| Any, one per variant/allele | `variant_strict_n` | Retrieve disease-anchored evidence for one independent variant |
| Any with gene + disease | `variant_broad_n` | Per-source fallback to variant + gene only after the strict source call succeeds with zero results |
| Standard/deep, one per phenotype | `phenotype_rescue_n` | Recover evidence for individual phenotypes when the bundle is too strict |
| Standard/deep | `case_cohort` | Find cases, series, families, and genotype cohorts |
| Standard/deep | `inheritance_segregation` | Retrieve inheritance, co-segregation, de novo, and pedigree evidence |
| Standard/deep | `functional_mechanism` | Retrieve assays and molecular/mechanistic studies |
| Deep | `genotype_phenotype` | Map allelic spectrum, variable expressivity, and genotype–phenotype relationships |
| Deep | `conflicting_evidence` | Actively retrieve refuting, benign, uncertain, and conflicting evidence |

The broad variant lane uses `if_dependency_zero` independently per source. Strict failure, timeout, skip, or nonzero retrieval never triggers broadening. Broad results remain broad context and require disease-text auditing before any disease-specific claim.

## Terminology And Sources

Ontology pack: HGNC, MONDO, HPO, Sequence Ontology, stable variant identifiers, ClinGen, and GenCC terminology.

Core scholarly sources are supplemented at standard depth by PubTator3, LitVar2, ClinVar, ClinGen, and GWAS Catalog. Deep depth can add CIViC, Reactome, UniProt, and Crossref. Curated source assertions seed publications and retain provenance; they do not become paper conclusions. Use targeted native web for HPO, Monarch, Orphanet, model-organism resources, or other relevant repositories when authorized.

## Output Contract

Organize the answer as:

1. normalized genetic concepts and unresolved mappings;
2. gene–disease validity evidence;
3. variant case/cohort table with transcript and allele context when verified;
4. phenotype–gene/disease relationships;
5. inheritance, segregation, de novo, and family evidence;
6. functional mechanism;
7. genotype–phenotype relationship and allelic spectrum;
8. conflicting/refuting evidence;
9. natural-history evidence where available;
10. classification boundary and evidence gaps.

Preserve each matched lane, context level, source record, and normalization attempt. Report a broad-only paper as candidate context, not as confirmed variant–disease evidence.

## Risks And Stop Conditions

- This search does not validate HGVS, establish allele equivalence, or perform ACMG/AMP classification.
- A database classification or gene–disease assertion must remain attributed to that source and its review date/status.
- Disease-text occurrence in metadata is only a context signal, not proof of causality.
- Case counts, segregation, phenotype specificity, functional assay validity, and allelic phase usually require abstract or full-text inspection.
- Phenotypic heterogeneity, reduced penetrance, mosaicism, ancestry, ascertainment, and transcript choice can change interpretation.

At quick depth, cover gene–disease validity and strict variant/phenotype evidence. At standard depth, add individual phenotype rescue, cases/cohorts, inheritance, and function. At deep depth, add allelic spectrum and explicit conflicting evidence. Stop when every independent variant and requested phenotype has a strict result or explicit gap, conditional fallbacks have completed safely, and two focused searches add no eligible evidence.
