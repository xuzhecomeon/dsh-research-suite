# Methods And Benchmarking

Use `methods-benchmarking` to compare life-science or bioinformatics methods across task, modality, datasets, metrics, independent validation, reproducibility, compute cost, robustness, and failure modes.

## Entity Framework

| Role | Concept types | Planning use |
|---|---|---|
| Candidate method | `method`, `algorithm`, `software`, `tool` | Resolves names, versions, acronyms, and primary publications |
| Scientific task | `task`, `analysis_task` | Defines what counts as successful performance |
| Data context | `data_modality`, `data_type`, `omics`, `organism`, `species` | Prevents cross-modality or cross-species overgeneralization |
| Evaluation resource | `dataset`, `accession`, `benchmark` | Links exact datasets and comparison studies |
| Outcome metric | `metric`, `evaluation_metric` | Preserves metric direction, unit, and evaluation protocol |
| Implementation context | `software`, `compute_constraint` | Scopes reproducibility, runtime, memory, and deployability |

Capture method version, reference/annotation version, dataset split, preprocessing, and compute environment when the decision depends on them. These often explain more variance than the method name.

## Planned Lanes

| Depth | Lane | Evidence purpose |
|---|---|---|
| Any | `exact_lookup` when applicable | Resolve DOI, PMID, accession, or software-linked identifiers |
| Any | `method_identity` | Resolve method names, acronyms, software, and primary publications |
| Any | `task_modality` | Find methods applicable to the requested task and data modality |
| Any | `head_to_head` | Retrieve direct comparisons and benchmark studies |
| Any when datasets supplied | `dataset_accessions` | Link exact datasets/accessions to methods and publications |
| Any when metrics supplied | `performance_metrics` | Retrieve performance under requested metrics |
| Standard/deep | `independent_validation` | Find external validation, replication, and real applications |
| Standard/deep | `reproducibility_software` | Assess code, workflow, container, and implementation detail |
| Standard/deep | `limitations_failure_modes` | Actively retrieve limitations, bias, robustness, and failure modes |
| Deep | `compute_scalability` | Retrieve runtime, memory, throughput, and scale evidence |
| Deep | `reviews_taxonomies` | Use reviews and surveys to check landscape coverage |

Dataset records stay in `objects.datasets`; papers that introduce or benchmark them stay in `objects.papers`. Connect them through relations rather than embedding publications inside datasets.

When a data modality or organism is supplied, retain it in head-to-head, metric, dataset-linkage, validation, reproducibility, limitation, and compute lanes. Method names are OR alternatives within the candidate group; task, modality, organism, dataset, metric, and compute context are distinct AND facets. This prevents a `single-cell RNA-seq` benchmark from silently admitting a mass-spectrometry or imaging benchmark merely because both mention batch correction.

## Terminology And Sources

Ontology pack: EDAM, OBI, MeSH, GO, NCBI Taxonomy, data-accession patterns, and EFO.

Core scholarly sources are supplemented at standard depth by arXiv, DBLP, Crossref, and DataCite. Deep depth can add OpenAIRE, CORE, and DOAJ. Repository records such as GEO, SRA, and ArrayExpress can become typed dataset objects when a stable accession resolves; other benchmark repositories and software pages are discoverable through targeted native-web searches.

## Output Contract

Create a comparison organized as:

1. method identities, versions, and scoped task;
2. candidate-method matrix;
3. dataset/benchmark matrix with accessions, populations or organisms, split strategy, and scale where known;
4. metrics and compatible evaluation context;
5. head-to-head and independent validation;
6. software availability and reproducibility;
7. runtime, memory, throughput, and scalability;
8. limitations, biases, robustness, and failure modes;
9. context-specific selection recommendation;
10. comparability and evidence gaps.

Recommend a method only for the scoped task and operating constraints. If no fair comparison exists, say so and provide a validation plan rather than a false winner.

## Risks And Stop Conditions

- Never compare metric values from incompatible datasets, label definitions, splits, prevalence, preprocessing, or evaluation protocols.
- Watch for data leakage, benchmark reuse, hyperparameter advantage, class imbalance, and selective reporting.
- A method's own paper is not independent validation. A preprint may be useful but should remain clearly labeled.
- Source code availability is not reproducibility; version, environment, data access, and executable workflow also matter.
- Runtime claims depend on hardware, implementation, batch size, and data scale.

At quick depth, cover method identity, task fit, and at least one direct comparison. At standard depth, require dataset context, independent validation, reproducibility, and failure modes. At deep depth, add scalability and review-based landscape checks. Stop when candidates are compared on at least one compatible benchmark and every decision criterion has evidence or an explicit gap.
