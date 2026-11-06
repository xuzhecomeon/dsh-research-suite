"""Conservative Open Targets entity lookup for first-class target/drug objects."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Any

from .._version import USER_AGENT
from ..evidence import make_drug, make_target
from ..models import Concept, SearchRequest


ENDPOINT = "https://api.platform.opentargets.org/api/v4/graphql"
MAX_QUERY_CONCEPTS = 6
MAX_ALIASES_PER_CONCEPT = 3
MAX_ALIAS_LENGTH = 160

ENTITY_KIND_BY_CONCEPT_TYPE = {
    "target": "target",
    "gene": "target",
    "protein": "target",
    "drug": "drug",
    "compound": "drug",
}

SEARCH_QUERIES = {
    entity_kind: f"""
query SearchEntities($q: String!, $size: Int!) {{
  search(queryString: $q, entityNames: [\"{entity_kind}\"], page: {{index: 0, size: $size}}) {{
    total
    hits {{ id entity name description score }}
  }}
}}
"""
    for entity_kind in ("target", "drug")
}


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _key(value: Any) -> str:
    return "".join(character for character in _text(value).casefold() if character.isalnum())


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


def _lookup_groups(request: SearchRequest) -> tuple[tuple[Concept, str, tuple[str, ...]], ...]:
    groups: list[tuple[Concept, str, tuple[str, ...]]] = []
    for concept in request.concepts:
        if (concept.role or "").casefold() == "exclude":
            continue
        entity_kind = ENTITY_KIND_BY_CONCEPT_TYPE.get(concept.type.casefold())
        aliases = _concept_aliases(concept)
        if entity_kind and aliases:
            groups.append((concept, entity_kind, aliases))
        if len(groups) == MAX_QUERY_CONCEPTS:
            break
    return tuple(groups)


def entity_query(request: SearchRequest) -> tuple[str, tuple[str, ...]]:
    groups = _lookup_groups(request)
    compiled = []
    all_aliases = []
    for _, entity_kind, aliases in groups:
        all_aliases.extend(aliases)
        alternatives = " OR ".join(f'"{value}"' for value in aliases)
        compiled.append(f"{entity_kind}:({alternatives})")
    return " AND ".join(compiled) or _text(request.question)[:500], tuple(all_aliases)


def _post_json(url: str, payload: dict[str, Any], timeout: float) -> Any:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read(16 * 1024 * 1024).decode("utf-8"))


def fetch_entity_objects(
    request: SearchRequest,
    *,
    limit: int = 10,
    timeout: float,
    retries: int = 0,
    fetcher: Any = _post_json,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    groups = _lookup_groups(request)
    query, _ = entity_query(request)
    effective_limit = max(1, min(int(limit), 100))
    effective_retries = _bounded_retries(retries)
    status: dict[str, Any] = {
        "source": "open-targets-registry",
        "source_role": "target_drug_entity_registry",
        "query": query,
        "query_family": "entity_combination",
        "query_lane": "registry.open_targets_entities",
        "query_origin": "first_class_registry",
        "scenario": request.primary_scenario,
        "evidence_dimension": "normalized_entities",
        "endpoint": ENDPOINT,
        "status": "not_run" if request.dry_run else "error",
        "received": None,
        "accepted": None,
        "reported_total": None,
        "requests": [],
        "requested_limit": limit,
        "effective_limit": effective_limit,
        "requested_retries": retries,
        "effective_retries": effective_retries,
        "attempts": 0,
    }
    if request.dry_run:
        status["reason"] = "Dry-run requested; no registry call was made."
        return [], status
    if not groups:
        status.update(
            status="skipped",
            reason="Typed target, gene, protein, drug, or compound concept is required for conservative entity resolution.",
        )
        return [], status
    try:
        objects_by_id: dict[str, dict[str, Any]] = {}
        received = 0
        reported_total = 0
        for concept, entity_kind, aliases in groups:
            expected = {
                _key(value)
                for value in (*aliases, concept.canonical_id)
                if _key(value)
            }
            for alias in aliases:
                error: Exception | None = None
                search: Mapping[str, Any] | None = None
                hits: list[Any] | None = None
                for _ in range(effective_retries + 1):
                    status["attempts"] += 1
                    try:
                        payload = fetcher(
                            ENDPOINT,
                            {
                                "query": SEARCH_QUERIES[entity_kind],
                                "variables": {"q": alias, "size": effective_limit},
                            },
                            timeout,
                        )
                        if not isinstance(payload, Mapping):
                            raise ValueError("Open Targets response is not an object")
                        if payload.get("errors"):
                            raise ValueError("Open Targets GraphQL returned errors")
                        data = payload.get("data")
                        if not isinstance(data, Mapping):
                            raise ValueError("Open Targets response has no data object")
                        search = data.get("search")
                        if not isinstance(search, Mapping):
                            raise ValueError("Open Targets response has no search object")
                        hits = search.get("hits")
                        if not isinstance(hits, list):
                            raise ValueError("Open Targets response has no search hits")
                        error = None
                        break
                    except Exception as caught:  # Adapter boundary: malformed remote data must not escape.
                        error = caught
                if error is not None or search is None or hits is None:
                    raise error or ValueError("Open Targets request failed")
                total = search.get("total")
                received += len(hits)
                if isinstance(total, int):
                    reported_total += total
                status["requests"].append(
                    {
                        "concept_type": concept.type,
                        "concept_role": concept.role,
                        "entity_kind": entity_kind,
                        "alias": alias,
                        "received": len(hits),
                        "reported_total": total,
                    }
                )
                for hit in sorted(
                    (item for item in hits if isinstance(item, Mapping)),
                    key=lambda item: (
                        _text(item.get("entity")).casefold(),
                        _text(item.get("id")).casefold(),
                        _text(item.get("name")).casefold(),
                    ),
                ):
                    entity = _text(hit.get("entity")).casefold()
                    identifier = _text(hit.get("id"))
                    label = _text(hit.get("name"))
                    exact = expected.intersection({_key(identifier), _key(label)})
                    if entity != entity_kind or not identifier or not label or not exact:
                        continue
                    if entity_kind == "target":
                        if not identifier.upper().startswith("ENSG"):
                            continue
                        object_ = make_target(
                            name=label,
                            symbol=label,
                            source="open-targets",
                            source_id=identifier,
                            identifiers={"ensembl": identifier},
                            object_id=f"target:ensembl:{identifier}",
                            url=f"https://platform.opentargets.org/target/{identifier}",
                            attributes={
                                "description": _text(hit.get("description")) or None,
                                "match_score": hit.get("score"),
                            },
                        )
                    else:
                        if not identifier.upper().startswith("CHEMBL"):
                            continue
                        object_ = make_drug(
                            preferred_name=label,
                            source="open-targets",
                            source_id=identifier,
                            identifiers={"chembl": identifier},
                            object_id=f"drug:chembl:{identifier}",
                            url=f"https://platform.opentargets.org/drug/{identifier}",
                            attributes={"match_score": hit.get("score")},
                        )
                    objects_by_id.setdefault(object_["id"], object_)
        objects = sorted(
            objects_by_id.values(),
            key=lambda object_: (str(object_.get("type")), str(object_.get("id"))),
        )
        status.update(
            status="ok",
            received=received,
            accepted=len(objects),
            reported_total=reported_total,
        )
        return objects, status
    except Exception as error:  # Adapter boundary: malformed remote data must not escape.
        status["error"] = {
            "code": "registry_request_failed",
            "message": str(error)[:400],
            "retryable": isinstance(error, (OSError, urllib.error.URLError)),
        }
        return [], status
