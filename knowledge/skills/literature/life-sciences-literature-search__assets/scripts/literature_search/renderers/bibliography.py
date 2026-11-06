"""Deterministic CSL-JSON, BibTeX, RIS, and inline reference rendering."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

from ..schema import validate_bundle


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _papers(
    bundle_or_papers: Mapping[str, Any] | Iterable[Mapping[str, Any]],
    *,
    eligible_only: bool = True,
) -> list[Mapping[str, Any]]:
    if isinstance(bundle_or_papers, Mapping) and "objects" in bundle_or_papers:
        validate_bundle(bundle_or_papers)
        values = list(bundle_or_papers["objects"]["papers"])
    else:
        values = list(bundle_or_papers)  # type: ignore[arg-type]
    if eligible_only:
        values = [paper for paper in values if (paper.get("citation") or {}).get("eligible")]
    return values


def _authors(paper: Mapping[str, Any]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for author in paper.get("authors") or []:
        if isinstance(author, Mapping):
            family = _clean(author.get("family") or author.get("family_name"))
            given = _clean(author.get("given") or author.get("given_name"))
            literal = _clean(author.get("literal") or author.get("name"))
            item = {key: value for key, value in {"family": family, "given": given}.items() if value}
            if not item and literal:
                item = {"literal": literal}
        else:
            item = {"literal": _clean(author)}
        if any(item.values()):
            result.append(item)
    return result


def _date_parts(paper: Mapping[str, Any]) -> list[list[int]] | None:
    publication = paper.get("publication") or {}
    raw = _clean(publication.get("date"))
    values: list[int] = []
    if raw:
        match = re.match(r"^(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?", raw)
        if match:
            values = [int(value) for value in match.groups() if value]
    if not values and publication.get("year"):
        values = [int(publication["year"])]
    return [values] if values else None


def _csl_type(paper: Mapping[str, Any]) -> str:
    types = " ".join((paper.get("publication") or {}).get("types") or []).casefold()
    if "conference" in types or "proceedings" in types:
        return "paper-conference"
    if "book chapter" in types or "bookchapter" in types:
        return "chapter"
    if "book" in types:
        return "book"
    if "thesis" in types or "dissertation" in types:
        return "thesis"
    if "report" in types:
        return "report"
    return "article-journal"


def paper_to_csl(paper: Mapping[str, Any], *, include_abstract: bool = False) -> dict[str, Any]:
    publication = paper.get("publication") or {}
    identifiers = paper.get("identifiers") or {}
    links = paper.get("links") or {}
    item: dict[str, Any] = {
        "id": paper["id"],
        "type": _csl_type(paper),
        "title": _clean(paper.get("title")),
        "author": _authors(paper),
        "container-title": _clean(publication.get("venue")) or None,
        "publisher": _clean(publication.get("publisher")) or None,
        "volume": _clean(publication.get("volume")) or None,
        "issue": _clean(publication.get("issue")) or None,
        "page": _clean(publication.get("pages") or publication.get("article_number")) or None,
        "issued": {"date-parts": _date_parts(paper)} if _date_parts(paper) else None,
        "DOI": _clean(identifiers.get("doi")) or None,
        "PMID": _clean(identifiers.get("pmid")) or None,
        "PMCID": _clean(identifiers.get("pmcid")) or None,
        "URL": _clean(links.get("canonical")) or None,
        "language": _clean(publication.get("language")) or None,
    }
    if include_abstract:
        abstract = (paper.get("content_support") or {}).get("abstract") or {}
        if abstract.get("status") == "available":
            item["abstract"] = _clean(abstract.get("text"))
    return {key: value for key, value in item.items() if value not in (None, [], "")}


def to_csl_json(
    bundle_or_papers: Mapping[str, Any] | Iterable[Mapping[str, Any]],
    *,
    include_abstract: bool = False,
    eligible_only: bool = True,
) -> list[dict[str, Any]]:
    return [
        paper_to_csl(paper, include_abstract=include_abstract)
        for paper in _papers(bundle_or_papers, eligible_only=eligible_only)
    ]


def export_csl_json(
    bundle_or_papers: Mapping[str, Any] | Iterable[Mapping[str, Any]],
    *,
    include_abstract: bool = False,
    eligible_only: bool = True,
) -> str:
    return json.dumps(
        to_csl_json(
            bundle_or_papers,
            include_abstract=include_abstract,
            eligible_only=eligible_only,
        ),
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def _ascii_slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return "".join(re.findall(r"[A-Za-z0-9]+", normalized))


def _first_author_key(paper: Mapping[str, Any]) -> str:
    authors = _authors(paper)
    if not authors:
        return ""
    author = authors[0]
    if author.get("family"):
        return _ascii_slug(author["family"])
    literal = _ascii_slug(author.get("literal", ""))
    return literal.split()[-1] if literal else ""


def _citekey_base(paper: Mapping[str, Any]) -> str:
    publication = paper.get("publication") or {}
    author = _first_author_key(paper)
    year = str(publication.get("year") or "nd")
    title_words = re.findall(r"[A-Za-z0-9]+", _clean(paper.get("title")))[:3]
    title = "".join(word.capitalize() for word in title_words)
    base = f"{author}{year}{title}" if author or title else ""
    if not base:
        identifiers = paper.get("identifiers") or {}
        stable = next(
            (_clean(identifiers.get(name)) for name in ("pmid", "doi", "pmcid", "arxiv") if identifiers.get(name)),
            _clean(paper.get("id")),
        )
        base = "paper" + _ascii_slug(stable)
    return base[:72] or "paper"


def citekeys(papers: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for paper in papers:
        groups[_citekey_base(paper)].append(paper)
    result: dict[str, str] = {}
    for base, values in groups.items():
        ordered = sorted(values, key=lambda value: _clean(value.get("id")))
        for index, paper in enumerate(ordered):
            suffix = "" if len(ordered) == 1 else chr(ord("a") + index)
            result[paper["id"]] = base + suffix
    return result


_BIB_ESCAPE = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "%": r"\%",
    "&": r"\&",
    "_": r"\_",
    "#": r"\#",
    "$": r"\$",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _bib_escape(value: Any) -> str:
    return "".join(_BIB_ESCAPE.get(character, character) for character in _clean(value))


def _bib_type(csl_type: str) -> str:
    return {
        "article-journal": "article",
        "paper-conference": "inproceedings",
        "chapter": "incollection",
        "book": "book",
        "thesis": "phdthesis",
        "report": "techreport",
    }.get(csl_type, "misc")


def _bib_author(author: Mapping[str, str]) -> str:
    if author.get("family") and author.get("given"):
        return f"{_bib_escape(author['family'])}, {_bib_escape(author['given'])}"
    if author.get("family"):
        return _bib_escape(author["family"])
    return "{{" + _bib_escape(author.get("literal", "")) + "}}"


def export_bibtex(
    bundle_or_papers: Mapping[str, Any] | Iterable[Mapping[str, Any]],
    *,
    include_abstract: bool = False,
    eligible_only: bool = True,
) -> str:
    papers = _papers(bundle_or_papers, eligible_only=eligible_only)
    keys = citekeys(papers)
    entries: list[str] = []
    for paper in papers:
        csl = paper_to_csl(paper, include_abstract=include_abstract)
        fields: list[tuple[str, Any]] = [
            ("title", csl.get("title")),
            ("author", " and ".join(_bib_author(author) for author in csl.get("author", []))),
            ("journal", csl.get("container-title") if csl["type"] == "article-journal" else None),
            ("booktitle", csl.get("container-title") if csl["type"] == "paper-conference" else None),
            ("publisher", csl.get("publisher")),
            ("year", ((csl.get("issued") or {}).get("date-parts") or [[None]])[0][0]),
            ("volume", csl.get("volume")),
            ("number", csl.get("issue")),
            ("pages", csl.get("page")),
            ("doi", csl.get("DOI")),
            ("pmid", csl.get("PMID")),
            ("pmcid", csl.get("PMCID")),
            ("url", csl.get("URL")),
            ("language", csl.get("language")),
            ("abstract", csl.get("abstract")),
        ]
        rendered = [f"@{_bib_type(csl['type'])}{{{keys[paper['id']]},"]
        present = [(name, value) for name, value in fields if value not in (None, "")]
        for index, (name, value) in enumerate(present):
            comma = "," if index < len(present) - 1 else ""
            escaped = value if name == "author" else _bib_escape(value)
            rendered.append(f"  {name} = {{{escaped}}}{comma}")
        rendered.append("}")
        entries.append("\n".join(rendered))
    return "\n\n".join(entries) + ("\n" if entries else "")


def _ris_type(csl_type: str) -> str:
    return {
        "article-journal": "JOUR",
        "paper-conference": "CPAPER",
        "chapter": "CHAP",
        "book": "BOOK",
        "thesis": "THES",
        "report": "RPRT",
    }.get(csl_type, "GEN")


def _ris_author(author: Mapping[str, str]) -> str:
    if author.get("family") and author.get("given"):
        return f"{author['family']}, {author['given']}"
    return author.get("family") or author.get("literal", "")


def export_ris(
    bundle_or_papers: Mapping[str, Any] | Iterable[Mapping[str, Any]],
    *,
    include_abstract: bool = False,
    eligible_only: bool = True,
) -> str:
    records: list[str] = []
    for paper in _papers(bundle_or_papers, eligible_only=eligible_only):
        csl = paper_to_csl(paper, include_abstract=include_abstract)
        lines = [f"TY  - {_ris_type(csl['type'])}", f"TI  - {csl['title']}"]
        lines.extend(f"AU  - {_ris_author(author)}" for author in csl.get("author", []))
        date_parts = ((csl.get("issued") or {}).get("date-parts") or [[]])[0]
        if date_parts:
            lines.append(f"PY  - {date_parts[0]}")
            lines.append("DA  - " + "/".join(str(value) for value in date_parts))
        pages = _clean(csl.get("page"))
        page_match = re.match(r"^(.+?)[-–](.+)$", pages)
        start_page = page_match.group(1) if page_match else pages
        end_page = page_match.group(2) if page_match else None
        tags = (
            ("JO", csl.get("container-title")),
            ("PB", csl.get("publisher")),
            ("VL", csl.get("volume")),
            ("IS", csl.get("issue")),
            ("SP", start_page),
            ("EP", end_page),
            ("DO", csl.get("DOI")),
            ("AN", f"PMID:{csl['PMID']}" if csl.get("PMID") else None),
            ("UR", csl.get("URL")),
            ("LA", csl.get("language")),
            ("AB", csl.get("abstract")),
        )
        lines.extend(f"{tag}  - {_clean(value)}" for tag, value in tags if value)
        lines.append("ER  -")
        records.append("\r\n".join(lines))
    return "\r\n\r\n".join(records) + ("\r\n" if records else "")


def _author_summary(paper: Mapping[str, Any], limit: int = 6) -> str:
    authors = _authors(paper)
    names = [
        author.get("literal")
        or " ".join(value for value in (author.get("given"), author.get("family")) if value)
        for author in authors[:limit]
    ]
    suffix = ", et al." if len(authors) > limit else ""
    return ", ".join(names) + suffix


def format_reference(paper: Mapping[str, Any], style: str = "vancouver") -> str:
    publication = paper.get("publication") or {}
    identifiers = paper.get("identifiers") or {}
    authors = _author_summary(paper) or "Authors unavailable"
    title = _clean(paper.get("title"))
    venue = _clean(publication.get("venue"))
    year = _clean(publication.get("year"))
    volume = _clean(publication.get("volume"))
    issue = _clean(publication.get("issue"))
    pages = _clean(publication.get("pages") or publication.get("article_number"))
    volume_part = volume + (f"({issue})" if issue else "")
    if pages:
        volume_part += f":{pages}" if volume_part else pages
    if style == "nature":
        result = f"{authors}. {title}. {venue} {volume_part} ({year})."
    else:
        result = f"{authors}. {title}. {venue}. {year}"
        if volume_part:
            result += f";{volume_part}"
        result += "."
    if identifiers.get("doi"):
        result += f" doi:{identifiers['doi']}."
    elif identifiers.get("pmid"):
        result += f" PMID:{identifiers['pmid']}."
    return _clean(result)
