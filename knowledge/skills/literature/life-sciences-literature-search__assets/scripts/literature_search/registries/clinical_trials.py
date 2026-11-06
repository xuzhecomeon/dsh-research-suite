"""ClinicalTrials.gov v2 adapter returning trial objects, not fake papers."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Any

from .._version import USER_AGENT
from ..models import Concept, EvidenceObject, SearchRequest


ENDPOINT = "https://clinicaltrials.gov/api/v2/studies"
MAX_QUERY_CONCEPTS = 8
MAX_ALIASES_PER_CONCEPT = 4
MAX_ALIAS_LENGTH = 160

TRIAL_CONCEPT_TYPES = {
    "trial_id",
    "trial-id",
    "target",
    "gene",
    "drug",
    "intervention",
    "disease",
    "indication",
    "adverse_event",
    "adverse-event",
    "sponsor",
    "biomarker",
    "trial_phase",
    "phase",
    "trial_status",
    "status",
}


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bounded_retries(value: int) -> int:
    return max(0, min(int(value), 5))


def _names(values: Any) -> list[str]:
    return [
        name
        for item in _list(values)
        if isinstance(item, dict)
        for name in [_text(item.get("name"))]
        if name
    ]


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


def trial_query(request: SearchRequest) -> str:
    groups = [
        group
        for concept in request.concepts
        if concept.type.casefold() in TRIAL_CONCEPT_TYPES
        and (concept.role or "").casefold() != "exclude"
        and (group := _concept_group(concept))
    ][:MAX_QUERY_CONCEPTS]
    if groups:
        return " AND ".join(groups)
    return _text(request.question)[:500]


def _trial_object(study: Mapping[str, Any]) -> EvidenceObject | None:
    protocol = study.get("protocolSection") if isinstance(study, Mapping) else None
    if not isinstance(protocol, Mapping):
        return None
    identification = _mapping(protocol.get("identificationModule"))
    status = _mapping(protocol.get("statusModule"))
    design = _mapping(protocol.get("designModule"))
    sponsor = _mapping(protocol.get("sponsorCollaboratorsModule"))
    conditions = _mapping(protocol.get("conditionsModule"))
    arms = _mapping(protocol.get("armsInterventionsModule"))
    locations = _mapping(protocol.get("contactsLocationsModule")).get("locations") or []
    description = _mapping(protocol.get("descriptionModule"))
    references = _mapping(protocol.get("referencesModule"))
    nct_id = _text(identification.get("nctId"))
    if not nct_id:
        return None
    interventions = []
    for item in _list(arms.get("interventions")):
        if not isinstance(item, Mapping):
            continue
        interventions.append(
            {
                "type": _text(item.get("type")),
                "name": _text(item.get("name")),
                "other_names": [_text(value) for value in _list(item.get("otherNames")) if _text(value)],
                "description": _text(item.get("description")) or None,
            }
        )
    lead_sponsor = _mapping(sponsor.get("leadSponsor"))
    collaborators = sponsor.get("collaborators") or []
    countries = sorted(
        {
            _text(item.get("country"))
            for item in _list(locations)
            if isinstance(item, Mapping) and _text(item.get("country"))
        }
    )
    publication_ids = []
    publication_refs = []
    for item in [*_list(references.get("references")), *_list(references.get("seeAlsoLinks"))]:
        if not isinstance(item, Mapping):
            continue
        pmid = _text(item.get("pmid"))
        if pmid:
            publication_ids.append(f"paper:pmid:{pmid}")
        publication_refs.append(
            {
                "pmid": pmid or None,
                "type": _text(item.get("type")) or None,
                "citation": _text(item.get("citation")) or None,
                "url": _text(item.get("url")) or None,
            }
        )
    attributes = {
        "registry": "ClinicalTrials.gov",
        "registry_id": nct_id,
        "brief_title": _text(identification.get("briefTitle")) or None,
        "official_title": _text(identification.get("officialTitle")) or None,
        "acronym": _text(identification.get("acronym")) or None,
        "overall_status": _text(status.get("overallStatus")) or None,
        "why_stopped": _text(status.get("whyStopped")) or None,
        "study_type": _text(design.get("studyType")) or None,
        "phases": [_text(value) for value in _list(design.get("phases")) if _text(value)],
        "enrollment": _mapping(design.get("enrollmentInfo")).get("count"),
        "enrollment_type": _text(_mapping(design.get("enrollmentInfo")).get("type")) or None,
        "conditions": [_text(value) for value in _list(conditions.get("conditions")) if _text(value)],
        "keywords": [_text(value) for value in _list(conditions.get("keywords")) if _text(value)],
        "interventions": interventions,
        "lead_sponsor": {
            "name": _text(lead_sponsor.get("name")) or None,
            "class": _text(lead_sponsor.get("class")) or None,
        },
        "collaborators": [
            {"name": _text(item.get("name")), "class": _text(item.get("class")) or None}
            for item in _list(collaborators)
            if isinstance(item, Mapping) and _text(item.get("name"))
        ],
        "countries": countries,
        "start_date": _text(_mapping(status.get("startDateStruct")).get("date")) or None,
        "primary_completion_date": _text(_mapping(status.get("primaryCompletionDateStruct")).get("date")) or None,
        "completion_date": _text(_mapping(status.get("completionDateStruct")).get("date")) or None,
        "study_first_post_date": _text(_mapping(status.get("studyFirstPostDateStruct")).get("date")) or None,
        "last_update_post_date": _text(_mapping(status.get("studyLastUpdatePostDateStruct")).get("date")) or None,
        "brief_summary": _text(description.get("briefSummary")) or None,
        "publication_references": publication_refs,
    }
    label = attributes["official_title"] or attributes["brief_title"] or nct_id
    return EvidenceObject(
        type="trial",
        id=f"trial:clinicaltrials.gov:{nct_id}",
        label=str(label),
        source="clinicaltrials.gov",
        url=f"https://clinicaltrials.gov/study/{nct_id}",
        attributes=attributes,
        linked_publication_ids=tuple(dict.fromkeys(publication_ids)),
        support_level="database",
    )


def _get_json(url: str, timeout: float) -> Any:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read(32 * 1024 * 1024).decode("utf-8"))


def fetch_trial_objects(
    request: SearchRequest,
    *,
    limit: int,
    timeout: float,
    retries: int = 0,
    fetcher: Any = _get_json,
) -> tuple[list[EvidenceObject], dict[str, Any]]:
    query = trial_query(request)
    effective_retries = _bounded_retries(retries)
    status: dict[str, Any] = {
        "source": "clinicaltrials-registry",
        "role": "primary_registry",
        "query": query,
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
            "query.term": query,
            "pageSize": str(max(1, min(limit, 100))),
            "countTotal": "true",
            "format": "json",
        }
    )
    error: Exception | None = None
    for _ in range(effective_retries + 1):
        status["attempts"] += 1
        try:
            payload = fetcher(f"{ENDPOINT}?{params}", timeout)
            if not isinstance(payload, Mapping):
                raise ValueError("ClinicalTrials.gov response is not an object")
            studies = payload.get("studies")
            if not isinstance(studies, list):
                raise ValueError("ClinicalTrials.gov response has no studies list")
            objects = [
                item
                for study in studies
                if isinstance(study, Mapping)
                and (item := _trial_object(study)) is not None
            ]
            status.update(
                status="ok",
                received=len(studies),
                accepted=len(objects),
                reported_total=payload.get("totalCount"),
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
