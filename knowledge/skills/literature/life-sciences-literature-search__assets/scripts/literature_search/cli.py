"""Command-line interface for scenario-aware life-science evidence retrieval."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from . import __version__
from .execution import run_search
from .models import Concept, Constraints, SearchRequest
from .renderers import RenderOptions, render
from .scenarios import canonical_scenario


SCENARIO_COMMANDS = {
    "auto": "auto",
    "general": "general-basic",
    "target": "target-research",
    "pipeline": "drug-pipeline",
    "safety": "drug-safety",
    "clinical": "clinical-evidence",
    "methods": "methods-benchmarking",
    "genetic": "genetic-rare",
}

SCENARIO_ARGUMENTS: dict[str, tuple[tuple[str, str], ...]] = {
    "auto": (),
    "general": (
        ("topic", "topic"),
        ("context", "context"),
        ("research-aspect", "research_aspect"),
        ("model", "model_system"),
        ("tissue", "tissue"),
        ("cell-type", "cell_type"),
        ("pathway", "pathway"),
        ("method", "method"),
        ("accession", "accession"),
    ),
    "target": (
        ("target", "target"),
        ("indication", "indication"),
        ("modality", "modality"),
        ("tissue", "tissue"),
        ("cell-type", "cell_type"),
        ("assay", "assay"),
        ("pathway", "pathway"),
    ),
    "pipeline": (
        ("target", "target"),
        ("drug", "drug"),
        ("asset", "asset"),
        ("indication", "indication"),
        ("sponsor", "sponsor"),
        ("modality", "modality"),
        ("phase", "trial_phase"),
        ("status", "trial_status"),
        ("trial-id", "trial_id"),
    ),
    "safety": (
        ("drug", "drug"),
        ("adverse-event", "adverse_event"),
        ("drug-class", "drug_class"),
        ("indication", "indication"),
        ("population", "population"),
        ("comparator", "comparator"),
        ("co-medication", "co_medication"),
    ),
    "clinical": (
        ("condition", "condition"),
        ("population", "population"),
        ("intervention", "intervention"),
        ("drug", "drug"),
        ("comparator", "comparator"),
        ("outcome", "outcome"),
        ("study-design", "study_design"),
        ("biomarker", "biomarker"),
    ),
    "methods": (
        ("method", "method"),
        ("software", "software"),
        ("tool", "tool"),
        ("task", "task"),
        ("data-modality", "data_modality"),
        ("dataset", "dataset"),
        ("benchmark", "benchmark"),
        ("metric", "metric"),
        ("compute-constraint", "compute_constraint"),
    ),
    "genetic": (
        ("gene", "gene"),
        ("disease", "disease"),
        ("hpo", "hpo"),
        ("phenotype", "phenotype"),
        ("variant", "variant"),
        ("allele", "allele"),
        ("inheritance", "inheritance"),
        ("mechanism", "mechanism"),
        ("population", "population"),
    ),
}


def _repeat(parser: argparse.ArgumentParser, name: str, help_text: str) -> None:
    parser.add_argument(f"--{name}", action="append", default=[], help=help_text)


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("question", help="Natural-language research question.")
    parser.add_argument(
        "--depth",
        choices=("quick", "standard", "deep"),
        default="standard",
        help="Retrieval budget and expansion depth (default: standard).",
    )
    _repeat(
        parser,
        "also",
        "Add a secondary scenario: general, target, pipeline, safety, clinical, methods, or genetic.",
    )
    _repeat(parser, "concept", "Add a typed concept as TYPE=VALUE; repeat as needed.")
    _repeat(parser, "query-variant", "Add a curated synonym or translated query variant.")
    _repeat(parser, "source", "Override capability routing with an exact source name or comma list.")
    _repeat(parser, "web-results", "Import a bounded JSON file from agent-run native web search.")
    parser.add_argument("--year-from", type=int)
    parser.add_argument("--year-to", type=int)
    _repeat(parser, "publication-type", "Required publication type (OR within field).")
    _repeat(parser, "exclude-publication-type", "Excluded publication type.")
    _repeat(parser, "author", "Required author match in the bounded candidate set.")
    _repeat(parser, "venue", "Required journal or venue match.")
    _repeat(parser, "language", "Required publication language.")
    _repeat(parser, "species", "Species or taxon constraint; also becomes a typed query concept.")
    _repeat(parser, "mesh-heading", "Explicit MeSH heading for a PubMed qualified query.")
    _repeat(parser, "mesh-subheading", "Explicit MeSH subheading paired with --mesh-heading.")
    _repeat(
        parser,
        "require-identifier",
        "Require an identifier type such as doi, pmid, pmcid, or arxiv.",
    )
    parser.add_argument("--open-access", action="store_true")
    parser.add_argument("--require-abstract", action="store_true")
    parser.add_argument("--exclude-preprints", action="store_true")
    parser.add_argument("--include-retracted", action="store_true")
    parser.add_argument("--has-associated-data", action="store_true")
    parser.add_argument(
        "--sort",
        choices=("relevance", "newest", "citations"),
        default="relevance",
    )
    parser.add_argument(
        "--expansion",
        choices=("auto", "none", "related", "citations", "both"),
        default="auto",
        help="One bounded citation/related-work round; auto follows depth.",
    )
    parser.add_argument(
        "--deliverable",
        choices=("list", "table", "review", "landscape"),
        help="Planning deliverable; inferred from --format when omitted.",
    )
    parser.add_argument(
        "--output-language",
        choices=("zh", "en", "bilingual"),
        default="zh",
    )
    parser.add_argument(
        "--format",
        choices=("json", "table", "review", "bibtex", "ris", "csl-json"),
        default="json",
    )
    parser.add_argument(
        "--view",
        choices=("papers", "trials", "drugs", "targets", "datasets"),
        help="Typed result set rendered by table/review output.",
    )
    parser.add_argument(
        "--citation-style",
        choices=("vancouver", "nature", "ama"),
        default="vancouver",
    )
    parser.add_argument("--include-abstract-in-export", action="store_true")
    parser.add_argument(
        "--terminology-dir",
        help="Directory containing optional licensed or organization-local terminology JSON packs.",
    )
    parser.add_argument("--no-normalize", action="store_true")
    parser.add_argument(
        "--include-descendants",
        action="store_true",
        help="Expand accepted OLS concepts with at most 20 hierarchical descendants.",
    )
    parser.add_argument("--no-registry-objects", action="store_true")
    parser.add_argument("--no-oa-enrichment", action="store_true")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--snippet-chars", type=int, default=700)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out", help="Write the requested rendering to this path.")
    parser.add_argument(
        "--audit-out",
        help="Write canonical schema-v2 JSON even when another format is rendered.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plan and execute auditable life-science evidence searches across "
            "basic science, targets, pipelines, safety, clinical evidence, methods, and genetics."
        )
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    descriptions = {
        "auto": "Detect the primary scenario from the question and typed concepts.",
        "general": "General/basic-science mechanisms, models, organisms, pathways, and methods.",
        "target": "Target genetics, biology, tractability, modality, and translational competition.",
        "pipeline": "Drug/asset pipeline and trial competitive intelligence.",
        "safety": "Drug safety and pharmacovigilance evidence.",
        "clinical": "PICO-oriented clinical evidence and study hierarchy.",
        "methods": "Methods, datasets, benchmarks, metrics, and compute trade-offs.",
        "genetic": "Genetic and rare-disease variant/phenotype evidence.",
    }
    for command in SCENARIO_COMMANDS:
        child = subparsers.add_parser(command, help=descriptions[command])
        _add_common_arguments(child)
        for flag, destination in SCENARIO_ARGUMENTS[command]:
            child.add_argument(
                f"--{flag}",
                dest=destination,
                action="append",
                default=[],
                help=f"Structured {destination.replace('_', ' ')} concept; repeat as needed.",
            )
    return parser


def _parse_concept(value: str, parser: argparse.ArgumentParser) -> Concept:
    if "=" not in value:
        parser.error(f"--concept expects TYPE=VALUE, got {value!r}")
    concept_type, concept_value = value.split("=", 1)
    concept_type = concept_type.strip().casefold().replace("-", "_")
    concept_value = concept_value.strip()
    if not concept_type or not concept_value:
        parser.error(f"--concept expects non-empty TYPE=VALUE, got {value!r}")
    return Concept(concept_type, concept_value)


def _flatten_csv(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            item.strip()
            for value in values
            for item in value.split(",")
            if item.strip()
        )
    )


def request_from_args(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> SearchRequest:
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not 0 <= args.retries <= 5:
        parser.error("--retries must be between 0 and 5")
    if not 100 <= args.snippet_chars <= 5000:
        parser.error("--snippet-chars must be between 100 and 5000")
    for name in ("year_from", "year_to"):
        value = getattr(args, name)
        if value is not None and not 1600 <= value <= 2100:
            parser.error(f"--{name.replace('_', '-')} must be between 1600 and 2100")
    if args.year_from and args.year_to and args.year_from > args.year_to:
        parser.error("--year-from must not exceed --year-to")
    bibliography_formats = {"bibtex", "ris", "csl-json"}
    if args.format in bibliography_formats and args.view not in {None, "papers"}:
        parser.error("bibliography exports accept only --view papers")
    if args.format in bibliography_formats and args.citation_style != "vancouver":
        parser.error("--citation-style applies to table/review output, not bibliography exports")
    if args.include_abstract_in_export and args.format not in bibliography_formats:
        parser.error("--include-abstract-in-export requires bibtex, ris, or csl-json format")

    concepts = [_parse_concept(value, parser) for value in args.concept]
    for _, concept_type in SCENARIO_ARGUMENTS[args.command]:
        for value in getattr(args, concept_type):
            concepts.append(Concept(concept_type, value))
    for value in args.species:
        concepts.append(Concept("species", value, role="constraint"))
    for value in args.mesh_heading:
        concepts.append(Concept("mesh_heading", value))
    for value in args.mesh_subheading:
        concepts.append(Concept("mesh_subheading", value))
    if bool(args.mesh_heading) != bool(args.mesh_subheading):
        parser.error("--mesh-heading and --mesh-subheading must be supplied together")

    primary = SCENARIO_COMMANDS[args.command]
    try:
        secondary = tuple(canonical_scenario(value) for value in args.also)
    except ValueError as error:
        parser.error(str(error))
    constraints = Constraints(
        year_from=args.year_from,
        year_to=args.year_to,
        publication_types=tuple(args.publication_type),
        excluded_publication_types=tuple(args.exclude_publication_type),
        authors=tuple(args.author),
        venues=tuple(args.venue),
        languages=tuple(args.language),
        species=tuple(args.species),
        required_identifiers=tuple(
            value.casefold() for value in args.require_identifier
        ),
        open_access=args.open_access,
        require_abstract=args.require_abstract,
        exclude_preprints=args.exclude_preprints,
        include_retracted=args.include_retracted,
        has_associated_data=args.has_associated_data,
    )
    inferred_deliverable = {
        "review": "review",
        "bibtex": "list",
        "ris": "list",
        "csl-json": "list",
    }.get(args.format, "table")
    return SearchRequest(
        question=args.question,
        depth=args.depth,
        scenarios=(primary, *secondary),
        primary_scenario=primary,
        concepts=tuple(concepts),
        constraints=constraints,
        deliverable=args.deliverable or inferred_deliverable,
        output_language=args.output_language,
        sort=args.sort,
        expansion=args.expansion,
        normalize=not args.no_normalize,
        include_descendants=args.include_descendants,
        source_override=_flatten_csv(args.source),
        query_variants=tuple(args.query_variant),
        web_result_files=tuple(args.web_results),
        dry_run=args.dry_run,
    )


def _serialize(bundle: dict[str, Any], args: argparse.Namespace) -> str:
    if args.format == "json":
        return json.dumps(bundle, ensure_ascii=False, indent=2) + "\n"
    return render(
        bundle,
        RenderOptions(
            format=args.format,
            language=args.output_language,
            citation_style=args.citation_style,
            view=args.view,
            include_abstract=args.include_abstract_in_export,
        ),
    )


def _write(path: str, value: str) -> None:
    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(value, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    request = request_from_args(args, parser)
    try:
        bundle = run_search(
            request,
            terminology_dir=args.terminology_dir,
            timeout=args.timeout,
            retries=args.retries,
            snippet_chars=args.snippet_chars,
            include_registry_objects=not args.no_registry_objects,
            enrich_open_access=not args.no_oa_enrichment,
        )
        rendered = _serialize(bundle, args)
    except (OSError, TypeError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")

    if args.out:
        _write(args.out, rendered)
    else:
        sys.stdout.write(rendered)
    if args.audit_out:
        _write(
            args.audit_out,
            json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
        )

    summary = (bundle.get("retrieval") or {}).get("source_summary") or {}
    if request.dry_run:
        return 0
    return 0 if summary.get("successful") or summary.get("partial") else 3


if __name__ == "__main__":
    raise SystemExit(main())
