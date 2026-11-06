"""Builders for the life-science evidence bundle v2.

Retrieval adapters may return heterogeneous scientific records.  This module
turns them into explicit object types, relations, and result sets without
collapsing trials or database entities into pseudo-publications.
"""

from __future__ import annotations

import copy
import hashlib
import re
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from typing import Any

from ._version import PRODUCT_VERSION
from .models import Constraints, EvidenceObject, SearchPlan, SearchRequest
from .schema import (
    ARTIFACT_TYPE,
    COLLECTION_FOR_TYPE,
    OBJECT_COLLECTIONS,
    SCHEMA_VERSION,
    citation_eligibility_for,
    validate_bundle,
)


_DOI_PREFIX_RE = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.I)
_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.I)
_PMCID_RE = re.compile(r"^PMC\d+$", re.I)
_ARXIV_RE = re.compile(r"^(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?$", re.I)


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _unique_strings(values: Iterable[Any]) -> list[str]:
    return list(dict.fromkeys(value for raw in values if (value := _clean(raw))))


def _stable_digest(*values: Any) -> str:
    text = "\x1f".join(_clean(value) for value in values)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _normalize_doi(value: Any) -> str | None:
    doi = _DOI_PREFIX_RE.sub("", _clean(value)).rstrip(".,;)").lower()
    return doi if _DOI_RE.fullmatch(doi) else None


def _normalize_identifiers(values: Mapping[str, Any] | None) -> dict[str, str]:
    identifiers: dict[str, str] = {}
    for raw_name, raw_value in (values or {}).items():
        name = _clean(raw_name).lower().replace("-", "_")
        value = _clean(raw_value)
        if not name or not value:
            continue
        if name == "doi":
            value = _normalize_doi(value) or ""
        elif name == "pmcid":
            value = value.upper()
        elif name in {"pmid", "nct"}:
            value = value.upper() if name == "nct" else value
        if value:
            identifiers[name] = value
    return identifiers


def make_source_ref(
    source: str,
    *,
    source_id: str | None = None,
    url: str | None = None,
    retrieved_at: str | None = None,
    query_run_ids: Iterable[str] = (),
) -> dict[str, Any]:
    """Create an auditable reference to one source record."""

    source = _clean(source)
    source_id = _clean(source_id) or None
    url = _clean(url) or None
    suffix = source_id or _stable_digest(source, url)
    return {
        "id": f"source:{source}:{suffix}",
        "source": source,
        "source_id": source_id,
        "url": url,
        "retrieved_at": _clean(retrieved_at) or None,
        "query_run_ids": _unique_strings(query_run_ids),
    }


def make_content_support(
    *,
    metadata_status: str = "verified",
    metadata_source_refs: Iterable[str] = (),
    abstract_text: str | None = None,
    abstract_language: str | None = None,
    abstract_source_refs: Iterable[str] = (),
    full_text_availability: str = "unknown",
    full_text_retrieval_status: str = "not_attempted",
    full_text_inspection_status: str = "not_inspected",
    full_text_url: str | None = None,
    full_text_license: str | None = None,
    full_text_source_refs: Iterable[str] = (),
    full_text_locator_hash: str | None = None,
) -> dict[str, Any]:
    """Describe content actually available and inspected for one paper.

    An open-access URL changes availability only.  It never upgrades
    ``highest_inspected`` unless full-text content was retrieved and inspected.
    """

    abstract_text = _clean(abstract_text)
    abstract_status = "available" if abstract_text else "unavailable"
    highest = "metadata"
    if abstract_status == "available":
        highest = "abstract"
    if (
        full_text_retrieval_status == "retrieved"
        and full_text_inspection_status in {"partially_inspected", "inspected"}
    ):
        highest = "full_text"
    return {
        "highest_inspected": highest,
        "metadata": {
            "status": metadata_status,
            "source_refs": _unique_strings(metadata_source_refs),
        },
        "abstract": {
            "status": abstract_status,
            "text": abstract_text or None,
            "language": _clean(abstract_language) or None,
            "source_refs": _unique_strings(abstract_source_refs),
        },
        "full_text": {
            "availability": full_text_availability,
            "retrieval_status": full_text_retrieval_status,
            "inspection_status": full_text_inspection_status,
            "url": _clean(full_text_url) or None,
            "license": _clean(full_text_license) or None,
            "source_refs": _unique_strings(full_text_source_refs),
            "locator_hash": _clean(full_text_locator_hash) or None,
        },
    }


def _source_refs(
    source: str,
    source_id: str | None,
    url: str | None,
    source_refs: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    raw_refs = [copy.deepcopy(dict(value)) for value in source_refs]
    if not raw_refs:
        raw_refs.append(make_source_ref(source, source_id=source_id, url=url))

    # A publication can be returned by several lanes from the same source
    # record.  Keep one source record identity and accumulate the query
    # provenance instead of emitting duplicate source-ref IDs.
    refs_by_id: dict[str, dict[str, Any]] = {}
    ordered_ids: list[str] = []
    for index, ref in enumerate(raw_refs, start=1):
        ref_id = _clean(ref.get("id"))
        if not ref_id:
            ref_id = make_source_ref(
                _clean(ref.get("source")) or source,
                source_id=_clean(ref.get("source_id")) or None,
                url=_clean(ref.get("url")) or None,
            )["id"]
            if ref_id in refs_by_id:
                ref_id = f"{ref_id}:record-{index}"
            ref["id"] = ref_id
        ref["query_run_ids"] = _unique_strings(ref.get("query_run_ids") or ())
        existing = refs_by_id.get(ref_id)
        if existing is None:
            refs_by_id[ref_id] = ref
            ordered_ids.append(ref_id)
            continue
        existing["query_run_ids"] = _unique_strings(
            (*existing.get("query_run_ids", ()), *ref.get("query_run_ids", ()))
        )
        for field in ("source", "source_id", "url", "retrieved_at"):
            if not existing.get(field) and ref.get(field):
                existing[field] = ref[field]
    return [refs_by_id[ref_id] for ref_id in ordered_ids]


def _canonical_paper_url(identifiers: Mapping[str, str], fallback: str | None) -> str | None:
    if identifiers.get("doi"):
        return f"https://doi.org/{identifiers['doi']}"
    if identifiers.get("pmid"):
        return f"https://pubmed.ncbi.nlm.nih.gov/{identifiers['pmid']}/"
    if identifiers.get("pmcid"):
        return f"https://europepmc.org/articles/{identifiers['pmcid']}"
    if identifiers.get("arxiv"):
        return f"https://arxiv.org/abs/{identifiers['arxiv']}"
    return _clean(fallback) or None


def paper_object_id(
    *,
    identifiers: Mapping[str, Any] | None,
    source: str,
    source_id: str | None,
    title: str,
) -> str:
    """Derive a stable paper ID from the strongest available identifier."""

    normalized = _normalize_identifiers(identifiers)
    for name in ("doi", "pmid", "pmcid", "arxiv"):
        if normalized.get(name):
            return f"paper:{name}:{normalized[name]}"
    suffix = _clean(source_id) or _stable_digest(source, title)
    return f"paper:{_clean(source) or 'unknown'}:{suffix}"


def _ensure_object_id(object_type: str, object_id: str | None, fallback: str) -> str:
    value = _clean(object_id)
    if not value:
        value = f"{object_type}:{fallback}"
    elif not value.startswith(f"{object_type}:"):
        value = f"{object_type}:{value}"
    return value


def _finalize(object_: dict[str, Any]) -> dict[str, Any]:
    object_["citation"] = citation_eligibility_for(object_)
    return object_


def make_paper(
    *,
    title: str,
    source: str,
    object_id: str | None = None,
    source_id: str | None = None,
    identifiers: Mapping[str, Any] | None = None,
    authors: Iterable[Any] = (),
    year: int | None = None,
    publication_date: str | None = None,
    venue: str | None = None,
    publication_types: Iterable[str] = (),
    language: str | None = None,
    volume: str | None = None,
    issue: str | None = None,
    pages: str | None = None,
    article_number: str | None = None,
    publisher: str | None = None,
    abstract: str | None = None,
    content_support: Mapping[str, Any] | None = None,
    verification_level: str = "structured_confirmed",
    url: str | None = None,
    open_access_url: str | None = None,
    citation_counts: Mapping[str, int] | None = None,
    evidence_type: str | None = None,
    study_design: Mapping[str, Any] | None = None,
    publication_states: Iterable[str] = (),
    is_retracted: bool | None = None,
    has_correction: bool | None = None,
    source_refs: Iterable[Mapping[str, Any]] = (),
    ranking: Mapping[str, Any] | None = None,
    attributes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_ids = _normalize_identifiers(identifiers)
    canonical_url = _canonical_paper_url(normalized_ids, url)
    object_id = _ensure_object_id(
        "paper",
        object_id,
        paper_object_id(
            identifiers=normalized_ids,
            source=source,
            source_id=source_id,
            title=title,
        ).removeprefix("paper:"),
    )
    refs = _source_refs(source, source_id, canonical_url, source_refs)
    if content_support is None:
        content_support = make_content_support(
            metadata_status="verified"
            if verification_level != "web_unverified"
            else "unverified",
            metadata_source_refs=(ref["id"] for ref in refs),
            abstract_text=abstract,
            abstract_source_refs=(ref["id"] for ref in refs) if abstract else (),
            full_text_availability="open" if open_access_url else "unknown",
            full_text_url=open_access_url,
        )
    object_ = {
        "type": "paper",
        "id": object_id,
        "label": _clean(title),
        "title": _clean(title),
        "authors": [copy.deepcopy(value) for value in authors],
        "identifiers": normalized_ids,
        "publication": {
            "year": year,
            "date": _clean(publication_date) or None,
            "venue": _clean(venue) or None,
            "types": _unique_strings(publication_types),
            "language": _clean(language) or None,
            "volume": _clean(volume) or None,
            "issue": _clean(issue) or None,
            "pages": _clean(pages) or None,
            "article_number": _clean(article_number) or None,
            "publisher": _clean(publisher) or None,
            "states": _unique_strings(publication_states),
            "is_retracted": is_retracted,
            "has_correction": has_correction,
        },
        "study_design": copy.deepcopy(dict(study_design or {})),
        "assessment": {
            "evidence_type": _clean(evidence_type) or None,
            "quality": "not_assessed",
        },
        "links": {
            "canonical": canonical_url,
            "open_access": _clean(open_access_url) or None,
        },
        "content_support": copy.deepcopy(dict(content_support)),
        "verification": {"level": verification_level},
        "metrics": {"citation_counts": dict(citation_counts or {})},
        "source_refs": refs,
        "ranking": copy.deepcopy(dict(ranking or {})),
        "attributes": copy.deepcopy(dict(attributes or {})),
    }
    return _finalize(object_)


def _registry_url(registry: str, registry_id: str, fallback: str | None) -> str | None:
    if _clean(fallback):
        return _clean(fallback)
    if registry.casefold() in {"clinicaltrials.gov", "clinicaltrials", "nct"}:
        return f"https://clinicaltrials.gov/study/{registry_id}"
    return None


def make_trial(
    *,
    registry: str,
    registry_id: str,
    title: str,
    source: str = "clinicaltrials",
    object_id: str | None = None,
    source_id: str | None = None,
    status: str | None = None,
    phases: Iterable[str] = (),
    study_type: str | None = None,
    design: Mapping[str, Any] | None = None,
    enrollment: int | None = None,
    conditions: Iterable[Any] = (),
    interventions: Iterable[Any] = (),
    sponsor: Mapping[str, Any] | str | None = None,
    collaborators: Iterable[Mapping[str, Any] | str] = (),
    countries: Iterable[str] = (),
    dates: Mapping[str, Any] | None = None,
    url: str | None = None,
    source_refs: Iterable[Mapping[str, Any]] = (),
    attributes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    registry = _clean(registry)
    registry_id = _clean(registry_id).upper()
    canonical_url = _registry_url(registry, registry_id, url)
    object_id = _ensure_object_id(
        "trial", object_id, f"{registry.casefold()}:{registry_id}"
    )
    refs = _source_refs(source, source_id or registry_id, canonical_url, source_refs)
    identifiers = {"nct": registry_id} if registry_id.startswith("NCT") else {registry.casefold(): registry_id}
    object_ = {
        "type": "trial",
        "id": object_id,
        "label": _clean(title),
        "title": _clean(title),
        "registry": registry,
        "registry_id": registry_id,
        "identifiers": identifiers,
        "status": _clean(status) or None,
        "phases": _unique_strings(phases),
        "study_type": _clean(study_type) or None,
        "design": copy.deepcopy(dict(design or {})),
        "enrollment": enrollment,
        "conditions": [copy.deepcopy(value) for value in conditions],
        "interventions": [copy.deepcopy(value) for value in interventions],
        "sponsor": _organization(sponsor),
        "collaborators": [
            normalized
            for value in collaborators
            if (normalized := _organization(value)) is not None
        ],
        "countries": _unique_strings(countries),
        "dates": copy.deepcopy(dict(dates or {})),
        "links": {"canonical": canonical_url},
        "source_refs": refs,
        "record_support": {"level": "database"},
        "attributes": copy.deepcopy(dict(attributes or {})),
    }
    return _finalize(object_)


def _organization(value: Mapping[str, Any] | str | None) -> dict[str, Any] | str | None:
    if isinstance(value, Mapping):
        organization = {
            "name": _clean(value.get("name")) or None,
            "class": _clean(value.get("class")) or None,
        }
        return organization if organization["name"] else None
    return _clean(value) or None


def _database_object(
    *,
    object_type: str,
    label: str,
    source: str,
    object_id: str | None,
    source_id: str | None,
    identifiers: Mapping[str, Any] | None,
    url: str | None,
    source_refs: Iterable[Mapping[str, Any]],
    fields: Mapping[str, Any],
    attributes: Mapping[str, Any] | None,
) -> dict[str, Any]:
    normalized_ids = _normalize_identifiers(identifiers)
    fallback = (
        next(iter(normalized_ids.values()), None)
        or _clean(source_id)
        or _stable_digest(source, label)
    )
    object_id = _ensure_object_id(object_type, object_id, f"{_clean(source)}:{fallback}")
    refs = _source_refs(source, source_id or fallback, url, source_refs)
    object_ = {
        "type": object_type,
        "id": object_id,
        "label": _clean(label),
        "identifiers": normalized_ids,
        "links": {"canonical": _clean(url) or None},
        "source_refs": refs,
        "record_support": {"level": "database"},
        **copy.deepcopy(dict(fields)),
        "attributes": copy.deepcopy(dict(attributes or {})),
    }
    return _finalize(object_)


def make_drug(
    *,
    preferred_name: str,
    source: str,
    identifiers: Mapping[str, Any],
    object_id: str | None = None,
    source_id: str | None = None,
    aliases: Iterable[str] = (),
    brand_names: Iterable[str] = (),
    development_codes: Iterable[str] = (),
    modality: str | None = None,
    composition: Mapping[str, Any] | None = None,
    url: str | None = None,
    source_refs: Iterable[Mapping[str, Any]] = (),
    attributes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _database_object(
        object_type="drug",
        label=preferred_name,
        source=source,
        object_id=object_id,
        source_id=source_id,
        identifiers=identifiers,
        url=url,
        source_refs=source_refs,
        fields={
            "preferred_name": _clean(preferred_name),
            "aliases": _unique_strings(aliases),
            "brand_names": _unique_strings(brand_names),
            "development_codes": _unique_strings(development_codes),
            "modality": _clean(modality) or None,
            "composition": copy.deepcopy(dict(composition or {})),
        },
        attributes=attributes,
    )


def make_target(
    *,
    name: str,
    source: str,
    identifiers: Mapping[str, Any],
    object_id: str | None = None,
    source_id: str | None = None,
    symbol: str | None = None,
    target_type: str | None = None,
    organism: Mapping[str, Any] | str | None = None,
    aliases: Iterable[str] = (),
    url: str | None = None,
    source_refs: Iterable[Mapping[str, Any]] = (),
    attributes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _database_object(
        object_type="target",
        label=symbol or name,
        source=source,
        object_id=object_id,
        source_id=source_id,
        identifiers=identifiers,
        url=url,
        source_refs=source_refs,
        fields={
            "name": _clean(name),
            "symbol": _clean(symbol) or None,
            "target_type": _clean(target_type) or None,
            "organism": copy.deepcopy(organism),
            "aliases": _unique_strings(aliases),
        },
        attributes=attributes,
    )


def make_dataset(
    *,
    title: str,
    repository: str,
    accession: str,
    source: str,
    identifiers: Mapping[str, Any] | None = None,
    object_id: str | None = None,
    source_id: str | None = None,
    resource_type: str = "dataset",
    data_types: Iterable[str] = (),
    modalities: Iterable[str] = (),
    organism: Mapping[str, Any] | str | None = None,
    sample_count: int | None = None,
    access: Mapping[str, Any] | None = None,
    url: str | None = None,
    source_refs: Iterable[Mapping[str, Any]] = (),
    attributes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    identifiers = dict(identifiers or {})
    identifiers.setdefault(_clean(repository).casefold(), _clean(accession))
    return _database_object(
        object_type="dataset",
        label=title,
        source=source,
        object_id=object_id,
        source_id=source_id or accession,
        identifiers=identifiers,
        url=url,
        source_refs=source_refs,
        fields={
            "title": _clean(title),
            "repository": _clean(repository),
            "accession": _clean(accession),
            "resource_type": _clean(resource_type),
            "data_types": _unique_strings(data_types),
            "modalities": _unique_strings(modalities),
            "organism": copy.deepcopy(organism),
            "sample_count": sample_count,
            "access": copy.deepcopy(dict(access or {})),
        },
        attributes=attributes,
    )


def make_relation(
    *,
    subject_id: str,
    predicate: str,
    object_id: str,
    relation_id: str | None = None,
    qualifiers: Mapping[str, Any] | None = None,
    evidence_refs: Iterable[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    relation_id = _clean(relation_id) or (
        "relation:" + _stable_digest(subject_id, predicate, object_id, qualifiers)
    )
    return {
        "id": relation_id,
        "subject_id": _clean(subject_id),
        "predicate": _clean(predicate),
        "object_id": _clean(object_id),
        "qualifiers": copy.deepcopy(dict(qualifiers or {})),
        "evidence_refs": [copy.deepcopy(dict(value)) for value in evidence_refs],
    }


def make_claim(
    *,
    kind: str,
    text: Mapping[str, str],
    basis: str,
    support_level: str,
    evidence: Iterable[Mapping[str, Any]] = (),
    method: str = "model_synthesis",
    claim_id: str | None = None,
    confidence: str = "not_assessed",
    limitations: Iterable[str] = (),
) -> dict[str, Any]:
    normalized_text = {
        language: _clean(text.get(language)) or None for language in ("zh", "en")
    }
    claim_id = _clean(claim_id) or (
        "claim:" + _stable_digest(kind, normalized_text, basis, support_level)
    )
    return {
        "id": claim_id,
        "kind": _clean(kind),
        "text": normalized_text,
        "basis": basis,
        "method": method,
        "support_level": support_level,
        "evidence": [copy.deepcopy(dict(value)) for value in evidence],
        "confidence": confidence,
        "limitations": _unique_strings(limitations),
    }


def _coerce_model_object(value: EvidenceObject) -> dict[str, Any]:
    attributes = copy.deepcopy(value.attributes)
    common = {
        "source": value.source,
        "object_id": value.id,
        "source_id": attributes.pop("source_id", None),
        "url": value.url,
        "attributes": attributes,
    }
    if value.type == "paper":
        return make_paper(
            title=attributes.pop("title", None) or value.label,
            identifiers=attributes.pop("identifiers", {}),
            authors=attributes.pop("authors", ()),
            year=attributes.pop("year", None),
            publication_date=attributes.pop("publication_date", None),
            venue=attributes.pop("venue", None),
            publication_types=attributes.pop("publication_types", ()),
            abstract=attributes.pop("abstract", None),
            verification_level=attributes.pop(
                "verification_level", "structured_confirmed"
            ),
            **common,
        )
    if value.type == "trial":
        dates = attributes.pop("dates", None)
        if not isinstance(dates, Mapping):
            dates = {
                "start": attributes.pop("start_date", None),
                "primary_completion": attributes.pop(
                    "primary_completion_date", None
                ),
                "completion": attributes.pop("completion_date", None),
                "first_posted": attributes.pop("study_first_post_date", None),
                "last_update_posted": attributes.pop(
                    "last_update_post_date", None
                ),
            }
        return make_trial(
            registry=attributes.pop("registry", "clinicaltrials.gov"),
            registry_id=attributes.pop("registry_id", value.label),
            title=attributes.pop("title", None) or value.label,
            status=attributes.pop("status", None)
            or attributes.pop("overall_status", None),
            phases=attributes.pop("phases", ()),
            study_type=attributes.pop("study_type", None),
            design=attributes.pop("design", {}),
            enrollment=attributes.pop("enrollment", None),
            conditions=attributes.pop("conditions", ()),
            interventions=attributes.pop("interventions", ()),
            sponsor=attributes.pop("sponsor", None)
            or attributes.pop("lead_sponsor", None),
            collaborators=attributes.pop("collaborators", ()),
            countries=attributes.pop("countries", ()),
            dates=dates,
            **common,
        )
    if value.type == "drug":
        return make_drug(
            preferred_name=attributes.pop("preferred_name", None) or value.label,
            identifiers=attributes.pop("identifiers", {}),
            aliases=attributes.pop("aliases", ()),
            modality=attributes.pop("modality", None),
            **common,
        )
    if value.type == "target":
        return make_target(
            name=attributes.pop("name", None) or value.label,
            symbol=attributes.pop("symbol", None),
            identifiers=attributes.pop("identifiers", {}),
            organism=attributes.pop("organism", None),
            **common,
        )
    if value.type == "dataset":
        return make_dataset(
            title=attributes.pop("title", None) or value.label,
            repository=attributes.pop("repository", value.source),
            accession=attributes.pop("accession", value.id),
            identifiers=attributes.pop("identifiers", {}),
            **common,
        )
    raise ValueError(f"unsupported evidence object type: {value.type!r}")


def _coerce_object(value: EvidenceObject | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(value, EvidenceObject):
        return _coerce_model_object(value)
    if not isinstance(value, Mapping):
        raise TypeError("evidence objects must be EvidenceObject or mapping values")
    object_ = copy.deepcopy(dict(value))
    if object_.get("type") not in COLLECTION_FOR_TYPE:
        raise ValueError(f"unsupported evidence object type: {object_.get('type')!r}")
    object_["citation"] = citation_eligibility_for(object_)
    return object_


def _iter_objects(
    values: Iterable[EvidenceObject | Mapping[str, Any]]
    | Mapping[str, Iterable[EvidenceObject | Mapping[str, Any]]],
) -> Iterable[EvidenceObject | Mapping[str, Any]]:
    if isinstance(values, Mapping) and any(key in values for key in OBJECT_COLLECTIONS):
        for collection in OBJECT_COLLECTIONS:
            yield from values.get(collection, ())
        return
    yield from values  # type: ignore[arg-type]


def _request_dict(
    request: SearchRequest | Mapping[str, Any] | None,
    plan: SearchPlan | None,
) -> dict[str, Any]:
    if request is None and plan is not None:
        request = plan.request
    if isinstance(request, SearchRequest):
        result = request.to_dict()
    else:
        result = copy.deepcopy(dict(request or {}))
    primary = _clean(result.get("primary_scenario")) or "general-basic"
    result.setdefault("question", "")
    result.setdefault("depth", "standard")
    result.setdefault("scenarios", [primary])
    result.setdefault("primary_scenario", primary)
    result.setdefault("concepts", [])
    constraints = result.get("constraints")
    if constraints is None:
        result["constraints"] = Constraints().to_dict()
    elif isinstance(constraints, Mapping):
        merged_constraints = Constraints().to_dict()
        merged_constraints.update(copy.deepcopy(dict(constraints)))
        result["constraints"] = merged_constraints
    result.setdefault("deliverable", "table")
    result.setdefault("output_language", "zh")
    result.setdefault("sort", "relevance")
    result.setdefault("expansion", "auto")
    result.setdefault("normalize", True)
    result.setdefault("include_descendants", False)
    result.setdefault("source_override", [])
    result.setdefault("query_variants", [])
    result.setdefault("web_result_files", [])
    result.setdefault("dry_run", False)
    return result


def _empty_ledger_counter() -> dict[str, int]:
    return {
        "runs": 0,
        "successful": 0,
        "failed": 0,
        "skipped": 0,
        "not_run": 0,
    }


def _ledger_for_statuses(statuses: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    values = list(statuses)
    families: dict[str, dict[str, int]] = {}
    lanes: dict[str, dict[str, int]] = {}
    field_for_status = {
        "ok": "successful",
        "error": "failed",
        "skipped": "skipped",
        "not_run": "not_run",
    }
    totals = {field: 0 for field in field_for_status.values()}
    for status in values:
        state = _clean(status.get("status"))
        family = _clean(status.get("query_family"))
        lane = _clean(status.get("query_lane"))
        if state not in field_for_status:
            continue
        count_field = field_for_status[state]
        totals[count_field] += 1
        for key, table in ((family, families), (lane, lanes)):
            if not key:
                continue
            counter = table.setdefault(key, _empty_ledger_counter())
            counter["runs"] += 1
            counter[count_field] += 1
    return {
        "run_count": len(values),
        "successful_runs": totals["successful"],
        "failed_runs": totals["failed"],
        "skipped_runs": totals["skipped"],
        "not_run": totals["not_run"],
        "query_families": families,
        "query_lanes": lanes,
        "details_field": "source_status",
    }


def _retrieval_dict(
    retrieval: Mapping[str, Any] | None,
    plan: SearchPlan | None,
) -> dict[str, Any]:
    result = copy.deepcopy(dict(retrieval or {}))
    if plan is not None:
        result.setdefault("plan", [lane.to_dict() for lane in plan.lanes])
        result.setdefault("routes", [route.to_dict() for route in plan.routes])
        result.setdefault("ontology_packs", list(plan.ontology_packs))
        result.setdefault("budget", plan.budget.to_dict())
    result.setdefault("plan", [])
    result.setdefault("routes", [])
    statuses = result.setdefault("source_status", [])
    if isinstance(statuses, list):
        for status in statuses:
            if not isinstance(status, dict):
                continue
            source = _clean(status.get("source")) or "unknown"
            status.setdefault("query_family", "source_operation")
            status.setdefault("query_lane", f"source_operation.{source}")
            status.setdefault("query_origin", "source_operation")
    result.setdefault(
        "ledger",
        _ledger_for_statuses(
            status for status in statuses if isinstance(status, Mapping)
        )
        if isinstance(statuses, list)
        else _ledger_for_statuses(()),
    )
    result.setdefault("constraints", {})
    result.setdefault("bounded", {"exhaustive": False})
    return result


def _default_result_sets(objects: Mapping[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    result_sets: list[dict[str, Any]] = []
    for collection, object_type in OBJECT_COLLECTIONS.items():
        if not objects[collection]:
            continue
        result_sets.append(
            {
                "id": collection,
                "object_type": object_type,
                "ordered_object_ids": [value["id"] for value in objects[collection]],
                "sort": "provided",
                "label": {"zh": collection, "en": collection},
            }
        )
    return result_sets


def _default_synthesis() -> dict[str, Any]:
    return {
        "status": "not_generated",
        "claims": [],
        "sections": [],
        "reading_order": [],
        "research_groups": [],
        "gaps": [],
        "limitations": [],
    }


def _paper_aliases(paper: Mapping[str, Any]) -> set[str]:
    aliases = {_clean(paper.get("id"))}
    for name, raw_value in (paper.get("identifiers") or {}).items():
        value = _clean(raw_value)
        aliases.update({value, f"{name}:{value}", f"paper:{name}:{value}"})
    return {value.casefold() for value in aliases if value}


def build_evidence_bundle(
    *,
    evidence_objects: Iterable[EvidenceObject | Mapping[str, Any]]
    | Mapping[str, Iterable[EvidenceObject | Mapping[str, Any]]] = (),
    request: SearchRequest | Mapping[str, Any] | None = None,
    plan: SearchPlan | None = None,
    relations: Iterable[Mapping[str, Any]] = (),
    result_sets: Iterable[Mapping[str, Any]] | None = None,
    synthesis: Mapping[str, Any] | None = None,
    retrieval: Mapping[str, Any] | None = None,
    retrieval_state: str = "performed",
    run_id: str | None = None,
    created_at: str | None = None,
    tool_version: str = PRODUCT_VERSION,
    warnings: Iterable[str] = (),
    validate: bool = True,
) -> dict[str, Any]:
    """Assemble and optionally validate a canonical v2 evidence bundle."""

    collections: dict[str, list[dict[str, Any]]] = {
        collection: [] for collection in OBJECT_COLLECTIONS
    }
    model_links: dict[str, tuple[str, ...]] = {}
    for raw in _iter_objects(evidence_objects):
        object_ = _coerce_object(raw)
        collection = COLLECTION_FOR_TYPE[object_["type"]]
        collections[collection].append(object_)
        if isinstance(raw, EvidenceObject) and raw.linked_publication_ids:
            model_links[object_["id"]] = raw.linked_publication_ids

    relation_values = [copy.deepcopy(dict(value)) for value in relations]
    paper_alias_index: dict[str, str] = {}
    for paper in collections["papers"]:
        for alias in _paper_aliases(paper):
            paper_alias_index[alias] = paper["id"]
    unresolved_links: list[str] = []
    predicate_for = {
        "trial": "trial_has_publication",
        "drug": "drug_described_by_paper",
        "target": "target_described_by_paper",
        "dataset": "dataset_described_by_paper",
    }
    object_types = {
        object_["id"]: object_["type"]
        for values in collections.values()
        for object_ in values
    }
    for source_object_id, publication_ids in model_links.items():
        for publication_id in publication_ids:
            target = paper_alias_index.get(_clean(publication_id).casefold())
            if target is None:
                unresolved_links.append(f"{source_object_id} -> {publication_id}")
                continue
            relation_values.append(
                make_relation(
                    subject_id=source_object_id,
                    predicate=predicate_for.get(
                        object_types[source_object_id], "described_by_paper"
                    ),
                    object_id=target,
                )
            )

    request_value = _request_dict(request, plan)
    primary_scenario = _clean(request_value.get("primary_scenario")) or "general-basic"
    depth = _clean(request_value.get("depth")) or "standard"
    created_at = _clean(created_at) or datetime.now(timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )
    warning_values = _unique_strings(
        [
            *warnings,
            *(plan.warnings if plan is not None else ()),
            *(f"unresolved publication link: {value}" for value in unresolved_links),
        ]
    )
    synthesis_value = copy.deepcopy(dict(synthesis or _default_synthesis()))
    for field, default in _default_synthesis().items():
        synthesis_value.setdefault(field, copy.deepcopy(default))
    bundle = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "run": {
            "id": _clean(run_id) or "run:" + _stable_digest(created_at, request_value),
            "tool_version": _clean(tool_version),
            "created_at": created_at,
            "retrieval_state": retrieval_state,
            "scenario": primary_scenario,
            "depth": depth,
            "warnings": warning_values,
        },
        "request": request_value,
        "retrieval": _retrieval_dict(retrieval, plan),
        "objects": collections,
        "relations": relation_values,
        "result_sets": [
            copy.deepcopy(dict(value)) for value in result_sets
        ]
        if result_sets is not None
        else _default_result_sets(collections),
        "synthesis": synthesis_value,
        "counts": {
            **{collection: len(values) for collection, values in collections.items()},
            "relations": len(relation_values),
            "total_objects": sum(len(values) for values in collections.values()),
        },
    }
    if validate:
        validate_bundle(bundle)
    return bundle
