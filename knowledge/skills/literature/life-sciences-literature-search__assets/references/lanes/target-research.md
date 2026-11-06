# Target Research

Use `target-research` to assess a gene or protein as a therapeutic target across human genetics, disease biology, mechanism, experimental validation, tractability, translation, and liabilities.

## Entity Framework

| Role | Concept types | Planning use |
|---|---|---|
| Target identity | `target`, `gene`, `protein` | Required anchor; retain HGNC/UniProt provenance and aliases |
| Disease context | `disease`, `indication`, `condition`, `phenotype` | Scopes association, mechanism, validation, and translation |
| Therapeutic form | `modality`, `drug_class`, `therapeutic_modality` | Separates small molecule, antibody, degrader, RNA, gene, or other precedents |
| Biological context | `tissue`, `cell_type`, `pathway`, `organism` | Locates expression and mechanism |
| Exact anchor | Bibliographic, target, protein, or accession ID | Resolves identity or a known source record |

An indication is strongly recommended. Without it, output a target-biology profile and label disease relevance as unscoped rather than implying universal utility.

## Planned Lanes

| Depth | Lane | Evidence purpose |
|---|---|---|
| Any | `exact_lookup` when applicable | Resolve exact identifiers |
| Any | `identity_function` | Establish nomenclature, protein identity, and baseline function |
| Any | `human_genetic_support` | Retrieve GWAS, Mendelian, MR, loss-of-function, and other human-genetic support |
| Any, when indication supplied | `disease_association` | Assess target–indication association separately from target identity |
| Any | `mechanism_pathway` | Map causal biology, pathways, signaling, and disease mechanism |
| Any with context; standard/deep otherwise | `expression_context` | Examine tissue, cell-type, and disease-state expression |
| Any | `experimental_validation` | Retrieve CRISPR, knockout/knockdown, perturbation, inhibition, and validation studies |
| Standard/deep | `tractability_structure` | Find structures, ligands, assays, binding evidence, and tractability precedents |
| Standard/deep | `modality_precedent` | Compare therapeutic modalities and pharmacological precedent |
| Standard/deep | `clinical_translation` | Find clinical assets and trials connected to target and indication |
| Deep | `safety_liability` | Actively retrieve on-target toxicity, adverse effects, and counter-evidence |

Do not merge human-genetic support, expression correlation, perturbation response, and clinical translation into one “validation” score unless the user explicitly requests a defined scoring method.

## Terminology And Sources

Ontology pack: HGNC, UniProt, Open Targets, ChEMBL, ChEBI, MONDO, EFO, GO, Reactome, UBERON, and Cell Ontology.

Core scholarly sources are supplemented at standard depth by Open Targets, GWAS Catalog, Reactome, UniProt, and PubTator3. Deep depth can add ClinicalTrials.gov, CIViC, and Crossref. Trial records remain first-class objects. For non-human targets, the current Reactome and UniProt adapters are excluded because their routes are fixed to human; use explicit organism concepts and relevant model-organism sources through the native-web lane.

## Output Contract

Structure the target assessment as:

1. target identity and scoped indication;
2. human-genetic evidence;
3. disease association;
4. mechanism and pathways;
5. tissue/cell expression context;
6. experimental validation;
7. tractability and modality precedent;
8. clinical translation and linked trials;
9. safety liabilities and counter-evidence;
10. evidence gaps and source coverage.

Return normalized target objects separately from papers and trials. When a curated or supplied relationship is available, represent target–paper or trial–paper links as relations; do not infer them merely from entity co-occurrence. A database association is not itself a publication conclusion.

## Risks And Stop Conditions

- Confirm symbol identity and species; a short symbol can be ambiguous or historical.
- Association, differential expression, and pathway membership do not independently establish causality.
- Human genetics can support directionality but may be indication-, ancestry-, variant-, or tissue-specific.
- Ligand or structure evidence does not establish clinical tractability; clinical activity does not prove on-target mechanism.
- Target-mediated safety and compound-specific toxicity are different hypotheses.

At quick depth, stop after identity plus the highest-value genetics, mechanism, and validation evidence. At standard depth, require coverage of genetics, biology, experimental validation, tractability/modality, and translation or explicitly mark gaps. At deep depth, also search safety liabilities and counter-evidence. Stop after two focused variants add no eligible evidence or the global budget is exhausted.
