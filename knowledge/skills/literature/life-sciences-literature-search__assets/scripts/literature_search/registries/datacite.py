"""DataCite adapter that keeps datasets as datasets rather than pseudo-papers."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Any

from .._version import USER_AGENT
from ..evidence import make_dataset
from ..models import Concept, SearchRequest


ENDPOINT = "https://api.datacite.org/dois"
MAX_QUERY_CONCEPTS = 8
MAX_ALIASES_PER_CONCEPT = 4
MAX_ALIAS_LENGTH = 160

DATASET_CONCEPT_TYPES = {
    "dataset",
    "accession",
    "method",
    "software",
    "task",
    "data_modality",
    "species",
}


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _bounded_retries(value: int) -> int:
    return max(0, min(int(value), 5))


def _concept_aliases(concept: Concept) -> tuple[str, ...]:
    aliases: list[str] = []
    seen: set[str] = set()
    for raw_value in (concept.input, concept.canonical_label, *concept.synonyms):
        value = _text(raw_value)[:MAX_ALIAS_LENGTH]
        key = value.casefold()
        if value and key not in seen:
            seen.add(key)
            aliases.append(value)
        if len(aliases) == MAX_ALIASES_PER_CONCEPT:
            break
    return tuple(aliases)


def _quoted(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _concept_group(concept: Concept) -> str:
    aliases = _concept_aliases(concept)
    if not aliases:
        return ""
    terms = [_quoted(value) for value in aliases]
    return terms[0] if len(terms) == 1 else f"({' OR '.join(terms)})"


def dataset_query(request: SearchRequest) -> str:
    groups = [
        group
        for concept in request.concepts
        if concept.type.casefold() in DATASET_CONCEPT_TYPES
        and (concept.role or "").casefold() != "exclude"
        and (group := _concept_group(concept))
    ][:MAX_QUERY_CONCEPTS]
    if groups:
        return " AND ".join(groups)
    return _text(request.question)[:500]


def _first_text(values: Any, *keys: str) -> str:
    for item in _list(values):
        if isinstance(item, dict):
            for key in keys:
                text = _text(item.get(key))
                if text:
                    return text
        elif _text(item):
            return _text(item)
    return ""


def _dataset_object(item: Mapping[str, Any]) -> dict[str, Any] | None:
    attributes = item.get("attributes") if isinstance(item, Mapping) else None
    if not isinstance(attributes, Mapping):
        return None
    types = attributes.get("types") or {}
    resource_type = _text(
        types.get("resourceTypeGeneral") if isinstance(types, Mapping) else ""
    )
    if resource_type.casefold() not in {"dataset", "collection"}:
        return None
    doi = _text(attributes.get("doi") or item.get("id")).casefold()
    title = _first_text(attributes.get("titles"), "title")
    if not doi or not title:
        return None
    subjects = [
        _text(value.get("subject"))
        for value in _list(attributes.get("subjects"))
        if isinstance(value, Mapping) and _text(value.get("subject"))
    ]
    rights = [
        {
            "name": _text(value.get("rights")) or None,
            "uri": _text(value.get("rightsUri")) or None,
            "identifier": _text(value.get("rightsIdentifier")) or None,
        }
        for value in _list(attributes.get("rightsList"))
        if isinstance(value, Mapping)
    ]
    creators = [
        _text(value.get("name"))
        or " ".join(
            part
            for part in (
                _text(value.get("givenName")),
                _text(value.get("familyName")),
            )
            if part
        )
        for value in _list(attributes.get("creators"))
        if isinstance(value, Mapping)
    ]
    descriptions = [
        {
            "type": _text(value.get("descriptionType")) or None,
            "text": _text(value.get("description")) or None,
        }
        for value in _list(attributes.get("descriptions"))
        if isinstance(value, Mapping) and _text(value.get("description"))
    ]
    url = f"https://doi.org/{doi}"
    return make_dataset(
        title=title,
        repository=_text(attributes.get("publisher")) or "DataCite",
        accession=doi,
        source="datacite",
        source_id=doi,
        identifiers={"doi": doi},
        object_id=f"dataset:doi:{doi}",
        resource_type=resource_type.casefold(),
        data_types=subjects,
        access={"url": _text(attributes.get("url")) or url, "rights": rights},
        url=url,
        attributes={
            "publication_year": attributes.get("publicationYear"),
            "creators": [value for value in creators if value],
            "descriptions": descriptions,
            "formats": [
                _text(value)
                for value in _list(attributes.get("formats"))
                if _text(value)
            ],
            "sizes": [
                _text(value)
                for value in _list(attributes.get("sizes"))
                if _text(value)
            ],
            "related_identifiers": attributes.get("relatedIdentifiers") or [],
        },
    )


def _get_json(url: str, timeout: float) -> Any:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.api+json",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read(32 * 1024 * 1024).decode("utf-8"))


def fetch_dataset_objects(
    request: SearchRequest,
    *,
    limit: int,
    timeout: float,
    retries: int = 0,
    fetcher: Any = _get_json,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    query = dataset_query(request)
    effective_retries = _bounded_retries(retries)
    status: dict[str, Any] = {
        "source": "datacite-registry",
        "source_role": "research_object_registry",
        "query": query,
        "query_family": "methods_benchmark",
        "query_lane": "registry.datacite_datasets",
        "query_origin": "first_class_registry",
        "scenario": request.primary_scenario,
        "evidence_dimension": "datasets",
        "endpoint": ENDPOINT,
        "status": "not_run" if request.dry_run else "error",
        "received": None,
        "accepted": None,
        "reported_total": None,
        "requested_retries": retries,
        "effective_retries": effective_retries,
        "attempts": 0,
    }
    if request.dry_run:
        status["reason"] = "Dry-run requested; no registry call was made."
        return [], status
    params = urllib.parse.urlencode(
        {
            "query": query,
            "page[size]": str(max(1, min(limit, 100))),
            "resource-type-id": "dataset",
        }
    )
    error: Exception | None = None
    for _ in range(effective_retries + 1):
        status["attempts"] += 1
        try:
            payload = fetcher(f"{ENDPOINT}?{params}", timeout)
            if not isinstance(payload, Mapping):
                raise ValueError("DataCite response is not an object")
            items = payload.get("data")
            if not isinstance(items, list):
                raise ValueError("DataCite response has no data list")
            objects = [
                object_
                for item in items
                if isinstance(item, Mapping)
                and (object_ := _dataset_object(item)) is not None
            ]
            meta = payload.get("meta")
            reported_total = meta.get("total") if isinstance(meta, Mapping) else None
            status.update(
                status="ok",
                received=len(items),
                accepted=len(objects),
                reported_total=reported_total,
            )
            return objects, status
        except Exception as caught:  # Adapter boundary: malformed remote data must not escape.
            error = caught
    assert error is not None
    status["error"] = {
        "code": "registry_request_failed",
        "message": str(error)[:400],
        "retryable": isinstance(error, (OSError, urllib.error.URLError)),
    }
    return [], status
