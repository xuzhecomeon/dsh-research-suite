"""Public rendering API for evidence bundle v2."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .base import RenderOptions
from .bibliography import export_bibtex, export_csl_json, export_ris, to_csl_json
from .markdown import render_review, render_table


def render(bundle: Mapping[str, Any], options: RenderOptions | None = None) -> str:
    options = options or RenderOptions()
    options.validate()
    if options.format == "table":
        return render_table(bundle, language=options.language, view=options.view)
    if options.format == "review":
        return render_review(
            bundle,
            language=options.language,
            citation_style=options.citation_style,
            view=options.view,
        )
    if options.format == "bibtex":
        return export_bibtex(bundle, include_abstract=options.include_abstract)
    if options.format == "ris":
        return export_ris(bundle, include_abstract=options.include_abstract)
    return export_csl_json(bundle, include_abstract=options.include_abstract)


__all__ = [
    "RenderOptions",
    "export_bibtex",
    "export_csl_json",
    "export_ris",
    "render",
    "render_review",
    "render_table",
    "to_csl_json",
]
