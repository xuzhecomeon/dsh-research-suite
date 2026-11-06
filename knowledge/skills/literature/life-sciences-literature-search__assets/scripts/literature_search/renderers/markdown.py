"""Markdown table and review renderers for validated evidence bundles."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..schema import validate_bundle
from .base import localized_text, message, object_index, select_result_set
from .bibliography import format_reference


TABLE_HEADERS: dict[str, dict[str, tuple[str, ...]]] = {
    "paper": {
        "zh": ("排名", "标题", "年份", "期刊", "证据类型", "关键发现", "支持层级", "引用"),
        "en": ("Rank", "Title", "Year", "Venue", "Evidence type", "Key finding", "Support", "Citation"),
    },
    "trial": {
        "zh": ("排名", "试验", "分期", "状态", "适应症", "申办方", "入组数", "注册号"),
        "en": ("Rank", "Trial", "Phase", "Status", "Conditions", "Sponsor", "Enrollment", "Registry"),
    },
    "drug": {
        "zh": ("排名", "药物", "模态", "别名/研发代号", "稳定标识", "来源链接"),
        "en": ("Rank", "Drug", "Modality", "Aliases/development codes", "Stable ID", "Source"),
    },
    "target": {
        "zh": ("排名", "靶点", "名称", "类型", "物种", "稳定标识", "来源链接"),
        "en": ("Rank", "Target", "Name", "Type", "Organism", "Stable ID", "Source"),
    },
    "dataset": {
        "zh": ("排名", "数据集", "数据库", "数据类型", "样本数", "访问方式", "稳定标识"),
        "en": ("Rank", "Dataset", "Repository", "Data type", "Samples", "Access", "Stable ID"),
    },
}


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _escape(value: Any, *, table: bool = False) -> str:
    text = (
        _clean(value)
        .replace("\\", "\\\\")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("|", "\\|")
    )
    if table:
        text = text.replace("\n", "<br>")
    return text


def _language_headers(object_type: str, language: str) -> tuple[str, ...]:
    headers = TABLE_HEADERS[object_type]
    if language == "bilingual":
        return tuple(
            f"{zh}<br>{en}" for zh, en in zip(headers["zh"], headers["en"])
        )
    return headers[language]


def _markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend(
        "| "
        + " | ".join(
            _clean(value).replace("|", "\\|").replace("\n", "<br>")
            for value in row
        )
        + " |"
        for row in rows
    )
    return "\n".join(lines)


def _canonical_link(object_: Mapping[str, Any], label: str | None = None) -> str:
    url = _clean((object_.get("links") or {}).get("canonical"))
    label = _clean(label) or _clean(object_.get("label")) or _clean(object_.get("id"))
    return f"[{_escape(label)}]({url})" if url else _escape(label)


def _identifier_text(object_: Mapping[str, Any]) -> str:
    preferred = (object_.get("citation") or {}).get("preferred_identifier") or {}
    if preferred.get("value"):
        return f"{str(preferred.get('scheme')).upper()}: {preferred['value']}"
    identifiers = object_.get("identifiers") or {}
    return ", ".join(f"{name.upper()}: {value}" for name, value in identifiers.items())


def _citation_links(object_: Mapping[str, Any]) -> str:
    links = (object_.get("citation") or {}).get("links") or []
    if not links:
        return _canonical_link(object_, "candidate")
    return " · ".join(
        f"[{str(link['scheme']).upper()}]({link['url']})" for link in links[:2]
    )


def _claims_for_object(bundle: Mapping[str, Any], object_id: str, kind: str) -> list[Mapping[str, Any]]:
    return [
        claim
        for claim in (bundle.get("synthesis") or {}).get("claims") or []
        if claim.get("kind") == kind
        and any(
            evidence.get("object_id") == object_id
            for evidence in claim.get("evidence") or []
            if isinstance(evidence, Mapping)
        )
    ]


def _paper_rows(
    bundle: Mapping[str, Any], objects: Sequence[Mapping[str, Any]], language: str
) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for rank, paper in enumerate(objects, start=1):
        publication = paper.get("publication") or {}
        assessment = paper.get("assessment") or {}
        claims = _claims_for_object(bundle, paper["id"], "key_finding")
        finding = (
            localized_text(claims[0].get("text"), language, inline=True)
            if claims
            else message("not_assessed", language)
        )
        support = claims[0].get("support_level") if claims else (
            (paper.get("content_support") or {}).get("highest_inspected")
        )
        evidence_type = assessment.get("evidence_type") or next(
            iter(publication.get("types") or []), None
        )
        rows.append(
            [
                rank,
                _canonical_link(paper, _clean(paper.get("title"))),
                publication.get("year") or "—",
                publication.get("venue") or "—",
                evidence_type or message("not_assessed", language),
                finding,
                support or "metadata",
                _citation_links(paper),
            ]
        )
    return rows


def _trial_rows(objects: Sequence[Mapping[str, Any]]) -> list[list[Any]]:
    rows = []
    for rank, trial in enumerate(objects, start=1):
        conditions = [
            value.get("label") or value.get("name") if isinstance(value, Mapping) else value
            for value in trial.get("conditions") or []
        ]
        sponsor = trial.get("sponsor")
        if isinstance(sponsor, Mapping):
            sponsor = sponsor.get("name")
        rows.append(
            [
                rank,
                _canonical_link(trial, _clean(trial.get("title"))),
                ", ".join(trial.get("phases") or []) or "—",
                trial.get("status") or "—",
                ", ".join(_clean(value) for value in conditions if _clean(value)) or "—",
                sponsor or "—",
                trial.get("enrollment") if trial.get("enrollment") is not None else "—",
                _citation_links(trial),
            ]
        )
    return rows


def _drug_rows(objects: Sequence[Mapping[str, Any]]) -> list[list[Any]]:
    return [
        [
            rank,
            _canonical_link(object_, _clean(object_.get("preferred_name"))),
            object_.get("modality") or "—",
            ", ".join(
                [
                    *(object_.get("aliases") or []),
                    *(object_.get("development_codes") or []),
                ]
            )
            or "—",
            _identifier_text(object_) or "—",
            _canonical_link(object_, "source"),
        ]
        for rank, object_ in enumerate(objects, start=1)
    ]


def _organism_text(value: Any) -> str:
    if isinstance(value, Mapping):
        return _clean(value.get("label") or value.get("name") or value.get("taxon_id"))
    return _clean(value)


def _target_rows(objects: Sequence[Mapping[str, Any]]) -> list[list[Any]]:
    return [
        [
            rank,
            _canonical_link(object_, _clean(object_.get("symbol") or object_.get("label"))),
            object_.get("name") or "—",
            object_.get("target_type") or "—",
            _organism_text(object_.get("organism")) or "—",
            _identifier_text(object_) or "—",
            _canonical_link(object_, "source"),
        ]
        for rank, object_ in enumerate(objects, start=1)
    ]


def _dataset_rows(objects: Sequence[Mapping[str, Any]]) -> list[list[Any]]:
    rows = []
    for rank, object_ in enumerate(objects, start=1):
        access = object_.get("access") or {}
        access_text = access.get("type") or access.get("status") or access.get("license")
        rows.append(
            [
                rank,
                _canonical_link(object_, _clean(object_.get("title"))),
                object_.get("repository") or "—",
                ", ".join(object_.get("data_types") or []) or "—",
                object_.get("sample_count") if object_.get("sample_count") is not None else "—",
                access_text or "—",
                _identifier_text(object_) or object_.get("accession") or "—",
            ]
        )
    return rows


ROW_BUILDERS = {
    "paper": _paper_rows,
    "trial": lambda _bundle, values, _language: _trial_rows(values),
    "drug": lambda _bundle, values, _language: _drug_rows(values),
    "target": lambda _bundle, values, _language: _target_rows(values),
    "dataset": lambda _bundle, values, _language: _dataset_rows(values),
}


def _failed_sources(bundle: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    for status in (bundle.get("retrieval") or {}).get("source_status") or []:
        if status.get("status") in {"error", "failed"}:
            failures.append(_clean(status.get("source")))
    return list(dict.fromkeys(value for value in failures if value))


def _retrieval_coverage_notes(
    bundle: Mapping[str, Any], language: str
) -> list[str]:
    """Summarize evidence dimensions that the readable output did not cover.

    The canonical JSON remains the detailed audit artifact.  This compact
    summary prevents a populated result table from hiding a failed or
    budget-skipped scenario lane.
    """

    run = bundle.get("run") or {}
    if run.get("retrieval_state") != "performed":
        return [message("retrieval_not_performed", language)]

    retrieval = bundle.get("retrieval") or {}
    plan = retrieval.get("plan") or []
    statuses = [
        value
        for value in retrieval.get("source_status") or []
        if isinstance(value, Mapping)
    ]
    statuses_by_lane: dict[str, list[Mapping[str, Any]]] = {}
    for status in statuses:
        lane_id = _clean(status.get("query_lane"))
        if lane_id:
            statuses_by_lane.setdefault(lane_id, []).append(status)

    lane_descriptors: list[tuple[str, str]] = []
    for value in plan:
        if not isinstance(value, Mapping):
            continue
        lane_id = _clean(value.get("id") or value.get("lane"))
        if lane_id:
            lane_descriptors.append(
                (lane_id, _clean(value.get("evidence_dimension")) or lane_id)
            )
    if not lane_descriptors:
        lane_descriptors = [
            (
                lane_id,
                next(
                    (
                        _clean(value.get("evidence_dimension"))
                        for value in lane_statuses
                        if _clean(value.get("evidence_dimension"))
                    ),
                    lane_id,
                ),
            )
            for lane_id, lane_statuses in statuses_by_lane.items()
        ]

    gaps: list[str] = []
    zero_results: list[str] = []
    for lane_id, dimension in lane_descriptors:
        lane_statuses = statuses_by_lane.get(lane_id, [])
        successful = [value for value in lane_statuses if value.get("status") == "ok"]
        if not successful:
            reason_codes = list(
                dict.fromkeys(
                    _clean(value.get("skip_code")) or _clean(value.get("status"))
                    for value in lane_statuses
                    if _clean(value.get("skip_code")) or _clean(value.get("status"))
                )
            )
            reason = ", ".join(reason_codes) or "no_source_status"
            gaps.append(f"{dimension} [{reason}]")
            continue
        accepted = [value.get("accepted") for value in successful]
        if accepted and all(value == 0 for value in accepted):
            zero_results.append(dimension)

    budget_skips = sum(
        1
        for value in statuses
        if _clean(value.get("skip_code"))
        in {"source_call_budget_exhausted", "source_record_budget_exhausted"}
    )
    notes: list[str] = []
    if gaps:
        notes.append(
            f"{message('coverage_gaps', language)}: " + "; ".join(dict.fromkeys(gaps))
        )
    if zero_results:
        notes.append(
            f"{message('zero_result_dimensions', language)}: "
            + ", ".join(dict.fromkeys(zero_results))
        )
    if budget_skips:
        notes.append(
            f"{message('budget_limited_operations', language)}: {budget_skips} "
            f"({message('audit_detail', language)})"
        )
    return notes


def render_table(
    bundle: Mapping[str, Any],
    *,
    language: str = "zh",
    view: str | None = None,
    include_heading: bool = True,
) -> str:
    """Render one typed result set as a Markdown table."""

    validate_bundle(bundle)
    if language not in {"zh", "en", "bilingual"}:
        raise ValueError(f"unsupported output language: {language}")
    result_set = select_result_set(bundle, view)
    question = _clean((bundle.get("request") or {}).get("question"))
    lines: list[str] = []
    if include_heading:
        lines.extend(
            [
                f"# {message('search_results', language)}",
                "",
                f"{message('query', language)}: {_escape(question) or '—'}",
                f"{message('scope', language)}: {message('bounded', language)}",
            ]
        )
        failures = _failed_sources(bundle)
        if failures:
            lines.append(f"{message('source_failures', language)}: {', '.join(failures)}")
        lines.extend(_retrieval_coverage_notes(bundle, language))
        lines.append("")
    if result_set is None:
        lines.append(message("no_results", language))
        return "\n".join(lines).rstrip() + "\n"
    object_type = result_set["object_type"]
    index = object_index(bundle)
    objects = [index[object_id] for object_id in result_set["ordered_object_ids"]]
    if not objects:
        lines.append(message("no_results", language))
    else:
        rows = ROW_BUILDERS[object_type](bundle, objects, language)
        lines.append(_markdown_table(_language_headers(object_type, language), rows))
    return "\n".join(lines).rstrip() + "\n"


def _paper_numbering(bundle: Mapping[str, Any]) -> tuple[dict[str, int], list[Mapping[str, Any]]]:
    papers = [
        paper
        for paper in bundle["objects"]["papers"]
        if (paper.get("citation") or {}).get("eligible")
    ]
    return ({paper["id"]: index for index, paper in enumerate(papers, start=1)}, papers)


def _claim_citations(
    claim: Mapping[str, Any],
    index: Mapping[str, Mapping[str, Any]],
    paper_numbers: Mapping[str, int],
) -> str:
    citations: list[str] = []
    for evidence in claim.get("evidence") or []:
        object_id = evidence.get("object_id")
        object_ = index.get(object_id)
        if not object_:
            continue
        url = _clean((object_.get("links") or {}).get("canonical"))
        if object_.get("type") == "paper" and object_id in paper_numbers:
            label = str(paper_numbers[object_id])
        else:
            preferred = (object_.get("citation") or {}).get("preferred_identifier") or {}
            label = _clean(preferred.get("value")) or _clean(object_.get("label"))
        marker = f"[{_escape(label)}]({url})" if url else f"[{_escape(label)}]"
        if marker not in citations:
            citations.append(marker)
    return " ".join(citations)


def _render_claim(
    claim: Mapping[str, Any],
    *,
    language: str,
    index: Mapping[str, Mapping[str, Any]],
    paper_numbers: Mapping[str, int],
) -> str:
    text = localized_text(claim.get("text"), language)
    text = "<br><br>".join(_escape(part) for part in text.split("\n\n"))
    citations = _claim_citations(claim, index, paper_numbers)
    support = _clean(claim.get("support_level"))
    suffix = " ".join(value for value in (citations, f"({support})" if support else "") if value)
    return f"- {text}" + (f" {suffix}" if suffix else "")


def _section_title(section: Mapping[str, Any], language: str) -> str:
    title = localized_text(section.get("title"), language, inline=True)
    if title:
        return title
    kind = _clean(section.get("kind")).replace("_", " ")
    return kind.title() or message("review", language)


def _localized_reason(value: Mapping[str, Any], language: str) -> str:
    return localized_text(value.get("reason") or value.get("note"), language)


def render_review(
    bundle: Mapping[str, Any],
    *,
    language: str = "zh",
    citation_style: str = "vancouver",
    view: str | None = None,
) -> str:
    """Render only synthesis already present in the bundle.

    The renderer never derives key findings, research groups, reading order, or
    gaps from titles.  Missing synthesis is stated plainly and accompanied by a
    factual retrieval table.
    """

    validate_bundle(bundle)
    if language not in {"zh", "en", "bilingual"}:
        raise ValueError(f"unsupported output language: {language}")
    if citation_style not in {"vancouver", "nature", "ama"}:
        raise ValueError(f"unsupported citation style: {citation_style}")
    synthesis = bundle["synthesis"]
    index = object_index(bundle)
    paper_numbers, papers = _paper_numbering(bundle)
    question = _clean((bundle.get("request") or {}).get("question"))
    lines = [
        f"# {message('review', language)}",
        "",
        f"{message('query', language)}: {_escape(question) or '—'}",
        f"{message('scope', language)}: {message('bounded', language)}",
        "",
    ]
    failures = _failed_sources(bundle)
    if failures:
        lines.extend(
            [
                f"> {message('source_failures', language)}: {', '.join(failures)}",
                "",
            ]
        )
    coverage_notes = _retrieval_coverage_notes(bundle, language)
    if coverage_notes:
        lines.extend([*(f"> {value}" for value in coverage_notes), ""])
    if synthesis.get("status") == "not_generated":
        lines.extend(
            [
                f"> {message('synthesis_not_generated', language)}",
                "",
                render_table(
                    bundle,
                    language=language,
                    view=view,
                    include_heading=False,
                ).rstrip(),
                "",
            ]
        )
    else:
        claims_by_id = {claim["id"]: claim for claim in synthesis.get("claims") or []}
        retrieved_claims = {
            claim_id: claim
            for claim_id, claim in claims_by_id.items()
            if claim.get("basis") == "retrieved_evidence"
        }
        for section in synthesis.get("sections") or []:
            section_claims = [
                retrieved_claims[claim_id]
                for claim_id in section.get("claim_ids") or []
                if claim_id in retrieved_claims
            ]
            if not section_claims:
                continue
            lines.extend([f"## {_escape(_section_title(section, language))}", ""])
            lines.extend(
                _render_claim(
                    claim,
                    language=language,
                    index=index,
                    paper_numbers=paper_numbers,
                )
                for claim in section_claims
            )
            lines.append("")

        background = [
            claim
            for claim in claims_by_id.values()
            if claim.get("basis") == "model_background"
        ]
        if background:
            lines.extend([f"## {message('model_background', language)}", ""])
            lines.extend(
                _render_claim(
                    claim,
                    language=language,
                    index=index,
                    paper_numbers=paper_numbers,
                )
                for claim in background
            )
            lines.append("")

        lines.extend([f"## {message('reading_order', language)}", ""])
        reading_order = synthesis.get("reading_order") or []
        if reading_order:
            for rank, item in enumerate(reading_order, start=1):
                object_ = index.get(item.get("object_id"))
                if not object_:
                    continue
                reason = _localized_reason(item, language)
                lines.append(
                    f"{rank}. {_canonical_link(object_)}"
                    + (f" — {_escape(reason)}" if reason else "")
                )
        else:
            lines.append(message("not_provided", language))
        lines.append("")

        lines.extend([f"## {message('research_groups', language)}", ""])
        groups = synthesis.get("research_groups") or []
        if groups:
            for group in groups:
                label = localized_text(group.get("name") or group.get("label"), language)
                note = localized_text(group.get("note"), language)
                refs = [index[value] for value in group.get("object_ids") or [] if value in index]
                links = ", ".join(_canonical_link(value) for value in refs)
                lines.append(
                    f"- {_escape(label) or '—'}"
                    + (f": {_escape(note)}" if note else "")
                    + (f" ({links})" if links else "")
                )
        else:
            lines.append(message("not_provided", language))
        lines.append("")

        lines.extend([f"## {message('research_gaps', language)}", ""])
        gaps = synthesis.get("gaps") or []
        if gaps:
            for gap in gaps:
                claim = claims_by_id.get(gap) if isinstance(gap, str) else gap
                if isinstance(claim, Mapping):
                    lines.append(
                        _render_claim(
                            claim,
                            language=language,
                            index=index,
                            paper_numbers=paper_numbers,
                        )
                    )
        else:
            lines.append(message("not_provided", language))
        lines.append("")

    limitations = synthesis.get("limitations") or []
    if limitations:
        lines.extend([f"## {message('limitations', language)}", ""])
        lines.extend(f"- {_escape(localized_text(value, language))}" for value in limitations)
        lines.append("")

    if papers:
        lines.extend([f"## {message('references', language)}", ""])
        lines.extend(
            f"{paper_numbers[paper['id']]}. {format_reference(paper, citation_style)}"
            for paper in papers
        )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
