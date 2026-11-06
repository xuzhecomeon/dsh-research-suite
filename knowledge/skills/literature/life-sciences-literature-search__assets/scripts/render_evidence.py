#!/usr/bin/env python3
"""Render or export an existing schema-v2 life-science evidence bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from literature_search.renderers import RenderOptions, render  # noqa: E402
from literature_search.schema import validate_bundle  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and render a canonical life-science evidence bundle."
    )
    parser.add_argument("artifact", help="Path to schema-v2 JSON, or - for stdin.")
    parser.add_argument(
        "--format",
        choices=("table", "review", "bibtex", "ris", "csl-json"),
        default="table",
    )
    parser.add_argument(
        "--language", choices=("zh", "en", "bilingual"), default="zh"
    )
    parser.add_argument("--view", help="Result-set id or papers/trials/drugs/targets/datasets.")
    parser.add_argument(
        "--citation-style",
        choices=("vancouver", "nature", "ama"),
        default="vancouver",
    )
    parser.add_argument("--include-abstract", action="store_true")
    parser.add_argument(
        "--synthesis",
        help="Optional JSON synthesis object to attach before validation and rendering.",
    )
    parser.add_argument(
        "--save-bundle",
        help="Write the validated bundle, including attached synthesis, as canonical JSON.",
    )
    parser.add_argument("--out", help="Write output to a file instead of stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    bibliography_formats = {"bibtex", "ris", "csl-json"}
    if args.include_abstract and args.format not in bibliography_formats:
        parser.error("--include-abstract requires bibtex, ris, or csl-json format")
    if args.format in bibliography_formats and args.citation_style != "vancouver":
        parser.error("--citation-style applies to table/review output, not bibliography exports")
    try:
        if args.artifact == "-":
            bundle = json.load(sys.stdin)
        else:
            bundle = json.loads(
                Path(args.artifact).expanduser().read_text(encoding="utf-8-sig")
            )
        if args.synthesis:
            synthesis = json.loads(
                Path(args.synthesis).expanduser().read_text(encoding="utf-8-sig")
            )
            if not isinstance(synthesis, dict):
                raise ValueError("--synthesis must contain one JSON object")
            bundle["synthesis"] = synthesis
        validate_bundle(bundle)
        output = render(
            bundle,
            RenderOptions(
                format=args.format,
                language=args.language,
                citation_style=args.citation_style,
                view=args.view,
                include_abstract=args.include_abstract,
            ),
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        parser.exit(2, f"error: {error}\n")
    if args.save_bundle:
        bundle_path = Path(args.save_bundle).expanduser()
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        bundle_path.write_text(
            json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.out:
        destination = Path(args.out).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
