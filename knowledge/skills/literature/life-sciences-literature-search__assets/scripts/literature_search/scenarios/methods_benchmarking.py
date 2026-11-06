"""Bioinformatics and life-science methods benchmarking planner."""

from __future__ import annotations

from ..models import Concept, QueryLane, SearchBudget, SearchRequest
from .base import (
    Detection,
    cap_lanes,
    combine,
    concept_terms,
    concept_type_score,
    discovery_sources,
    exact_lookup_lane,
    keyword_score,
    lane,
)


class MethodsBenchmarkingPlanner:
    scenario = "methods-benchmarking"
    ontology_packs = (
        "edam",
        "obi",
        "mesh",
        "go",
        "ncbi-taxonomy",
        "data-accession",
        "efo",
    )
    output_sections = (
        "method_and_task_scope",
        "candidate_method_matrix",
        "dataset_benchmark_matrix",
        "metrics_and_experimental_context",
        "independent_validation",
        "software_and_reproducibility",
        "compute_and_scalability",
        "limitations_and_failure_modes",
        "context_specific_selection",
        "comparability_gaps",
    )

    def detect(self, question: str, concepts: tuple[Concept, ...]) -> Detection:
        keyword_points, keyword_reasons = keyword_score(
            question,
            (
                r"\b(?:benchmark|method comparison|algorithm|bioinformatics|analysis pipeline|computational pipeline|workflow|dataset|metric|accuracy|reproducib|software tool)\b",
                r"方法选型|方法比较|算法|生物信息|工作流|数据集|基准|指标|准确率|复现|软件工具",
            ),
            points=5,
        )
        concept_points, concept_reasons = concept_type_score(
            concepts,
            ("method", "task", "data_modality", "dataset", "benchmark", "metric", "software"),
            points=3,
        )
        return Detection(
            self.scenario,
            keyword_points + concept_points,
            (*keyword_reasons, *concept_reasons),
        )

    def build_lanes(
        self,
        request: SearchRequest,
        budget: SearchBudget,
        available_sources: tuple[str, ...],
    ) -> tuple[QueryLane, ...]:
        methods = concept_terms(request, "method", "algorithm", "software", "tool")
        tasks = concept_terms(request, "task", "analysis_task")
        modalities = concept_terms(request, "data_modality", "data_type", "omics")
        datasets = concept_terms(request, "dataset", "accession")
        benchmarks = concept_terms(request, "benchmark")
        metrics = concept_terms(request, "metric", "evaluation_metric")
        compute_constraints = concept_terms(
            request,
            "compute_constraint",
            "resource_constraint",
            "hardware_constraint",
        )
        organisms = concept_terms(request, "organism", "species")
        anchor = methods or concept_terms(request, "topic") or (request.question,)

        lanes: list[QueryLane] = []
        exact = exact_lookup_lane(self.scenario, request, budget, available_sources)
        if exact:
            lanes.append(exact)

        def add(
            suffix: str,
            purpose: str,
            query: str,
            dimension: str,
            specialized: tuple[str, ...],
            *,
            family: str = "entity_combination",
            notes: tuple[str, ...] = (),
        ) -> None:
            lanes.append(
                lane(
                    id=f"{self.scenario}.{suffix}",
                    scenario=self.scenario,
                    purpose=purpose,
                    query=query,
                    family=family,
                    sources=discovery_sources(available_sources, *specialized),
                    evidence_dimension=dimension,
                    budget=budget,
                    notes=notes,
                )
            )

        add(
            "method_identity",
            "Resolve method names, acronyms, software, and primary publications",
            combine(anchor, tasks, modalities),
            "method_identity",
            ("arxiv", "dblp", "crossref"),
            family="core",
        )
        add(
            "task_modality",
            "Retrieve methods applicable to the requested task and data modality",
            combine(anchor, tasks, modalities, organisms),
            "task_modality_fit",
            ("arxiv", "dblp"),
        )
        if compute_constraints:
            add(
                "requested_compute_constraints",
                "Find methods evaluated under the requested compute or deployment constraints",
                combine(
                    anchor,
                    tasks,
                    modalities,
                    compute_constraints,
                    ("runtime", "memory", "throughput", "scalability"),
                ),
                "compute_scalability",
                ("arxiv", "dblp"),
                notes=(
                    "Compute comparisons are meaningful only under compatible hardware, data scale, and implementation conditions.",
                ),
            )
        add(
            "head_to_head",
            "Find direct comparisons and benchmark studies",
            combine(
                methods or anchor,
                tasks,
                modalities,
                organisms,
                benchmarks or ("benchmark", "comparison", "evaluation"),
            ),
            "head_to_head_comparison",
            ("arxiv", "dblp", "datacite"),
        )
        if datasets:
            add(
                "dataset_accessions",
                "Link exact datasets and accessions to methods and publications",
                combine(datasets, methods, tasks, modalities, organisms),
                "dataset_linkage",
                ("datacite", "openaire", "core"),
                family="exact_identifier",
                notes=("Dataset objects remain separate from publication records.",),
            )
        if metrics:
            add(
                "performance_metrics",
                "Retrieve performance evidence for the requested metrics",
                combine(anchor, tasks, modalities, datasets, metrics, organisms),
                "performance_metrics",
                ("arxiv", "dblp", "datacite"),
                notes=("Metrics are compared only with compatible datasets and evaluation protocols.",),
            )
        if budget.depth != "quick":
            add(
                "independent_validation",
                "Find independent validation and application studies",
                combine(
                    anchor,
                    tasks,
                    modalities,
                    organisms,
                    ("independent validation", "external validation", "replication"),
                ),
                "independent_validation",
                ("arxiv", "dblp", "openaire"),
            )
            add(
                "reproducibility_software",
                "Assess software availability, workflow detail, and reproducibility",
                combine(
                    anchor,
                    tasks,
                    modalities,
                    ("reproducibility", "source code", "workflow", "container"),
                ),
                "reproducibility",
                ("arxiv", "dblp", "datacite", "core"),
            )
            add(
                "limitations_failure_modes",
                "Actively retrieve known limitations and failure modes",
                combine(
                    anchor,
                    tasks,
                    modalities,
                    organisms,
                    ("limitation", "failure mode", "bias", "robustness"),
                ),
                "limitations",
                ("arxiv", "dblp", "openaire"),
            )
        if budget.depth == "deep" and not compute_constraints:
            add(
                "compute_scalability",
                "Find runtime, memory, throughput, and scalability evidence",
                combine(
                    anchor,
                    tasks,
                    modalities,
                    ("runtime", "memory", "scalability", "computational cost"),
                ),
                "compute_scalability",
                ("arxiv", "dblp"),
            )
            add(
                "reviews_taxonomies",
                "Retrieve reviews and method taxonomies for landscape coverage",
                combine(tasks or anchor, modalities, ("review", "survey", "taxonomy")),
                "reviews_taxonomies",
                ("arxiv", "dblp", "openaire"),
                family="publication_type",
            )
        return cap_lanes(lanes, budget)
