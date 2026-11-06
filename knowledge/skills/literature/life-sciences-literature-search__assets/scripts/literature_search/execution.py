"""Execute a v2 search plan and assemble a typed evidence bundle.

This module is the boundary between scenario planning and the legacy HTTP
adapters.  A source receives only the lanes explicitly routed to it; trial and
database records remain first-class evidence objects instead of being forced
through the publication reconciler.
"""

from __future__ import annotations

import concurrent.futures
import dataclasses
import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from . import backend
from .adapter_contracts import ResultFilters, SearchOptions
from .audit import build_search_ledger, normalize_source_status
from .evidence import (
    build_evidence_bundle,
    make_dataset,
    make_drug,
    make_paper,
    make_relation,
    make_target,
)
from .models import Concept, EvidenceObject, SearchPlan, SearchRequest
from .normalizers import normalize_concepts
from .planner import build_plan
from .registries.clinical_trials import fetch_trial_objects
from .registries.datacite import fetch_dataset_objects
from .registries.open_targets import fetch_entity_objects
from .reconciliation import reconcile_records
from .schema import citation_eligibility_for


REGISTRY_SCENARIOS = {
    "target-research",
    "drug-pipeline",
    "drug-safety",
    "clinical-evidence",
}
DATA_ACCESSION_RE = re.compile(
    r"^(?:GSE\d+|E-[A-Z]+-\d+|(?:SRP|SRA|SRR|SRS|SRX|PRJNA|ERP|DRP)\d+)$",
    re.IGNORECASE,
)


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def _unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if value))


def _options(plan: SearchPlan) -> SearchOptions:
    request = plan.request
    constraints = request.constraints
    genes = request.terms_of("gene", "target", "protein")
    diseases = request.terms_of("disease", "condition", "indication")
    accessions = _unique(
        term
        for concept in request.concepts_of("accession", "dataset")
        for term in concept.terms()
        if DATA_ACCESSION_RE.fullmatch(term)
    )
    accession_types = _unique(
        concept.ontology or concept.resolver or concept.type
        for concept in request.concepts_of("accession", "dataset")
    )
    return SearchOptions(
        per_source=plan.budget.per_source,
        year_from=constraints.year_from,
        year_to=constraints.year_to,
        open_access=constraints.open_access,
        publication_types=constraints.publication_types,
        sort="newest" if request.sort == "newest" else "relevance",
        # These concept-only fields activate relevant specialist adapters but
        # do not become an unintended hard AND filter on every publication lane.
        concept_genes=genes,
        concept_diseases=diseases,
        accession_ids=accessions,
        accession_types=accession_types,
        has_associated_data=constraints.has_associated_data,
        mesh_synonyms=True,
        max_source_calls=plan.budget.max_calls_per_source,
    )


def _result_filters(plan: SearchPlan) -> ResultFilters:
    constraints = plan.request.constraints
    return ResultFilters(
        publication_types=constraints.publication_types,
        excluded_publication_types=constraints.excluded_publication_types,
        authors=constraints.authors,
        venues=constraints.venues,
        languages=constraints.languages,
        required_identifiers=constraints.required_identifiers,
        require_abstract=constraints.require_abstract,
        exclude_preprints=constraints.exclude_preprints,
        sort="newest" if plan.request.sort == "newest" else "relevance",
        include_retracted=constraints.include_retracted,
        has_associated_data=constraints.has_associated_data,
    )


def _not_run_status(source: str, lane: Any, reason: str) -> dict[str, Any]:
    status = backend.source_status_base(
        source, lane.query, lane.family, lane.to_backend_dict()
    )
    status.update(status="not_run", reason=reason)
    return normalize_source_status(status)


def _execute_route_group(
    plan: SearchPlan,
    *,
    options: SearchOptions,
    timeout: float,
    retries: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    route_plans: dict[str, list[dict[str, Any]]] = {}
    for route in plan.routes:
        lanes = list(plan.lanes_for_source(route.source))
        if lanes:
            route_plans[route.source] = [lane.to_backend_dict() for lane in lanes]
    if not route_plans:
        return [], []

    records: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(4, len(route_plans))
    ) as executor:
        futures = {
            source: executor.submit(
                backend.execute_source,
                source,
                query_plan,
                options,
                timeout,
                retries,
            )
            for source, query_plan in route_plans.items()
        }
        # Consume in plan order so audit artifacts remain deterministic even
        # though the network operations run concurrently.
        for route in plan.routes:
            future = futures.get(route.source)
            if future is None:
                continue
            source_records, source_statuses = future.result()
            records.extend(source_records)
            statuses.extend(source_statuses)
    return records, [normalize_source_status(value) for value in statuses]


def _sort_by_citations(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(record: Mapping[str, Any]) -> tuple[Any, ...]:
        counts = record.get("citation_counts") or {}
        total = max((int(value) for value in counts.values() if value is not None), default=-1)
        return (-total, -(record.get("year") or 0), -((record.get("score") or {}).get("combined") or 0), _clean(record.get("title")).casefold())

    ordered = sorted(results, key=key)
    for index, record in enumerate(ordered, start=1):
        record["rank"] = index
    return ordered


def _reconcile(
    records: list[dict[str, Any]],
    plan: SearchPlan,
    filters: ResultFilters,
    *,
    snippet_chars: int,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    effective_limit = limit or plan.budget.result_limit
    # Citation sorting needs the full bounded candidate pool before truncation.
    reconciliation_limit = max(effective_limit, len(records)) if plan.request.sort == "citations" else effective_limit
    results = reconcile_records(records, reconciliation_limit, snippet_chars, filters)
    if plan.request.sort == "citations":
        results = _sort_by_citations(results)[:effective_limit]
    return results


def _paper_from_result(result: Mapping[str, Any]) -> dict[str, Any]:
    source_records = result.get("source_records") or []
    source = next(iter(result.get("sources") or ()), "unknown")
    refs = [
        {
            "id": "source:{source}:{source_id}".format(
                source=_clean(item.get("source")) or "unknown",
                source_id=_clean(item.get("source_id"))
                or "query-" + str(index),
            ),
            "source": _clean(item.get("source")) or "unknown",
            "source_id": _clean(item.get("source_id")) or None,
            "url": _clean(item.get("url")) or None,
            "retrieved_at": None,
            "query_run_ids": [
                value
                for value in (
                    _clean(item.get("query_lane")),
                    _clean(item.get("query_family")),
                )
                if value
            ],
        }
        for index, item in enumerate(source_records, start=1)
        if isinstance(item, Mapping)
    ]
    publication_types = result.get("publication_types") or (
        [result.get("publication_type")] if result.get("publication_type") else []
    )
    normalized_types = " ".join(_clean(value).casefold() for value in publication_types)
    design_label = next(
        (
            label
            for needle, label in (
                ("randomized controlled trial", "randomized_controlled_trial"),
                ("randomised controlled trial", "randomized_controlled_trial"),
                ("meta-analysis", "meta_analysis"),
                ("meta analysis", "meta_analysis"),
                ("systematic review", "systematic_review"),
                ("cohort", "cohort_study"),
                ("case-control", "case_control_study"),
                ("case report", "case_report"),
                ("guideline", "guideline"),
                ("preprint", "preprint"),
            )
            if needle in normalized_types
        ),
        None,
    )
    return make_paper(
        title=_clean(result.get("title")),
        source=source,
        source_id=_clean((source_records[0] if source_records else {}).get("source_id")) or None,
        identifiers=result.get("identifiers") or {},
        authors=result.get("authors") or (),
        year=result.get("year"),
        publication_date=result.get("publication_date"),
        venue=result.get("venue"),
        publication_types=publication_types,
        language=next(iter(result.get("languages") or ()), None),
        abstract=result.get("abstract"),
        verification_level=(result.get("verification") or {}).get("level", "web_unverified"),
        url=result.get("url"),
        open_access_url=result.get("open_access_url"),
        citation_counts=result.get("citation_counts") or {},
        evidence_type=design_label or result.get("publication_type"),
        study_design={
            "label": design_label,
            "method": "source_publication_type" if design_label else "not_assessed",
        },
        publication_states=result.get("publication_states") or (),
        is_retracted=result.get("is_retracted"),
        has_correction=result.get("has_correction"),
        source_refs=refs,
        ranking={
            "rank": result.get("rank"),
            "score": result.get("score") or {},
            "lanes": result.get("ranking_lanes") or [],
        },
        attributes={
            "snippet": result.get("snippet"),
            "matched_query_variants": result.get("matched_query_variants") or [],
            "matched_query_families": result.get("matched_query_families") or [],
            "matched_query_lanes": result.get("matched_query_lanes") or [],
            "matched_scenarios": result.get("matched_scenarios") or [],
            "evidence_dimensions": result.get("evidence_dimensions") or [],
            "source_enrichment": result.get("source_enrichment") or {},
            "variant_context": result.get("variant_context"),
        },
    )


def _concept_url(concept: Concept) -> str | None:
    identifier = _clean(concept.canonical_id)
    resolver = _clean(concept.resolver).casefold()
    if not identifier:
        return None
    if resolver == "hgnc" or identifier.upper().startswith("HGNC:"):
        return "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/" + identifier.upper()
    if resolver == "chembl" or identifier.upper().startswith("CHEMBL"):
        return "https://www.ebi.ac.uk/chembl/explore/compound/" + identifier.upper()
    if identifier.upper().startswith("GSE"):
        return "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=" + identifier.upper()
    if identifier.upper().startswith(("SRP", "SRA", "SRR", "SRS", "SRX")):
        return "https://www.ncbi.nlm.nih.gov/sra/?term=" + identifier.upper()
    if identifier.upper().startswith("E-"):
        return "https://www.ebi.ac.uk/biostudies/arrayexpress/studies/" + identifier.upper()
    return None


def _objects_from_concepts(concepts: Iterable[Concept]) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    seen: set[str] = set()
    for concept in concepts:
        if (concept.role or "").casefold() == "exclude":
            continue
        identifier = _clean(concept.canonical_id)
        url = _concept_url(concept)
        if not identifier or not url:
            continue
        label = _clean(concept.canonical_label) or _clean(concept.input)
        resolver = _clean(concept.resolver) or _clean(concept.ontology) or "registry"
        if concept.type in {"gene", "target", "protein"}:
            object_ = make_target(
                name=label,
                symbol=label if concept.type in {"gene", "target"} else None,
                source=resolver,
                source_id=identifier,
                identifiers={"hgnc": identifier},
                aliases=concept.synonyms,
                url=url,
                attributes={"normalization": concept.to_dict()},
            )
        elif concept.type in {"drug", "compound", "chemical", "intervention"} and (
            identifier.upper().startswith("CHEMBL") or resolver.casefold() in {"chembl", "local-inn"}
        ):
            object_ = make_drug(
                preferred_name=label,
                source=resolver,
                source_id=identifier,
                identifiers={"chembl" if identifier.upper().startswith("CHEMBL") else "inn": identifier},
                aliases=concept.synonyms,
                url=url,
                attributes={"normalization": concept.to_dict()},
            )
        elif concept.type in {"dataset", "accession"}:
            repository = (
                "GEO" if identifier.upper().startswith("GSE") else
                "SRA" if identifier.upper().startswith(("SRP", "SRA", "SRR", "SRS", "SRX")) else
                "ArrayExpress"
            )
            object_ = make_dataset(
                title=label,
                repository=repository,
                accession=identifier,
                source=resolver,
                source_id=identifier,
                url=url,
                attributes={"normalization": concept.to_dict()},
            )
        else:
            continue
        if object_["id"] not in seen:
            seen.add(object_["id"])
            objects.append(object_)
    return objects


def _merge_database_objects(
    objects: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge only database views with an auditable identity link.

    A shared label is not an identity assertion: names can collide across
    datasets, drug products, and biological targets.  Two views may merge only
    when they have the same object ID or share an exact stable identifier, and
    every identifier namespace present in both views agrees.
    """

    def identifier_sets(
        values: Iterable[Mapping[str, Any]],
    ) -> dict[str, set[str]]:
        identifiers: dict[str, set[str]] = {}
        for value in values:
            for raw_namespace, raw_identifier in (value.get("identifiers") or {}).items():
                namespace = _clean(raw_namespace).casefold().replace("-", "_")
                identifier = _clean(raw_identifier).casefold()
                if namespace and identifier:
                    identifiers.setdefault(namespace, set()).add(identifier)
        return identifiers

    def compatible(
        left: Iterable[Mapping[str, Any]],
        right: Iterable[Mapping[str, Any]],
    ) -> bool:
        left_ids = identifier_sets(left)
        right_ids = identifier_sets(right)
        return all(
            left_ids[namespace] == right_ids[namespace]
            for namespace in left_ids.keys() & right_ids.keys()
        )

    def identity_link(
        left: Iterable[Mapping[str, Any]],
        right: Iterable[Mapping[str, Any]],
    ) -> bool:
        left_values = list(left)
        right_values = list(right)
        if not left_values or not right_values:
            return False
        if _clean(left_values[0].get("type")) != _clean(right_values[0].get("type")):
            return False
        left_object_ids = {_clean(value.get("id")) for value in left_values}
        right_object_ids = {_clean(value.get("id")) for value in right_values}
        if (left_object_ids & right_object_ids) - {""}:
            return True
        left_identifiers = {
            (namespace, identifier)
            for namespace, identifiers in identifier_sets(left_values).items()
            for identifier in identifiers
        }
        right_identifiers = {
            (namespace, identifier)
            for namespace, identifiers in identifier_sets(right_values).items()
            for identifier in identifiers
        }
        return bool(left_identifiers & right_identifiers)

    groups: list[list[dict[str, Any]]] = [[object_] for object_ in objects]
    changed = True
    while changed:
        changed = False
        for left_index in range(len(groups)):
            for right_index in range(left_index + 1, len(groups)):
                if not identity_link(groups[left_index], groups[right_index]):
                    continue
                if not compatible(groups[left_index], groups[right_index]):
                    continue
                groups[left_index].extend(groups.pop(right_index))
                changed = True
                break
            if changed:
                break

    merged: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    for values in groups:
        preferred = sorted(
            values,
            key=lambda value: (
                0 if _clean(value.get("id")).startswith("target:ensembl:") else 1,
                0 if _clean(value.get("id")).startswith("drug:chembl:") else 1,
                _clean(value.get("id")),
            ),
        )[0]
        result = dict(preferred)
        identifiers: dict[str, Any] = {}
        aliases: list[str] = []
        refs: list[dict[str, Any]] = []
        seen_refs: set[str] = set()
        merged_ids: list[str] = []
        for value in values:
            identifiers.update(value.get("identifiers") or {})
            aliases.extend(value.get("aliases") or [])
            merged_ids.append(_clean(value.get("id")))
            for ref in value.get("source_refs") or []:
                ref_id = _clean(ref.get("id")) if isinstance(ref, Mapping) else ""
                if isinstance(ref, Mapping) and ref_id not in seen_refs:
                    seen_refs.add(ref_id)
                    refs.append(dict(ref))
        result["identifiers"] = identifiers
        if "aliases" in result:
            result["aliases"] = list(dict.fromkeys(value for value in aliases if value))
        result["source_refs"] = refs
        attributes = dict(result.get("attributes") or {})
        attributes["merged_object_ids"] = list(dict.fromkeys(merged_ids))
        shared_identifiers = []
        for namespace, identifiers in identifier_sets(values).items():
            occurrences = sum(
                1
                for value in values
                if namespace
                in {
                    _clean(raw_namespace).casefold().replace("-", "_")
                    for raw_namespace in (value.get("identifiers") or {})
                }
            )
            if occurrences > 1 and len(identifiers) == 1:
                shared_identifiers.append(
                    f"{namespace}:{next(iter(identifiers))}"
                )
        attributes["identity_resolution"] = {
            "method": (
                "stable_identifier_or_object_id" if len(values) > 1 else "not_merged"
            ),
            "shared_identifiers": sorted(shared_identifiers),
            "object_count": len(values),
        }
        original_id = _clean(result.get("id"))
        if original_id in used_ids:
            fingerprint = "|".join(
                [
                    _clean(result.get("type")),
                    *sorted(
                        f"{namespace}:{identifier}"
                        for namespace, values_ in identifier_sets(values).items()
                        for identifier in values_
                    ),
                    *sorted(
                        _clean(ref.get("id"))
                        for ref in refs
                        if isinstance(ref, Mapping)
                    ),
                ]
            )
            suffix = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:12]
            candidate_id = f"{original_id}:conflict-{suffix}"
            sequence = 2
            while candidate_id in used_ids:
                candidate_id = f"{original_id}:conflict-{suffix}-{sequence}"
                sequence += 1
            result["id"] = candidate_id
            attributes["identity_conflict"] = {
                "original_object_id": original_id,
                "resolution": "preserved_as_separate_object",
            }
        result["attributes"] = attributes
        result["citation"] = citation_eligibility_for(result)
        used_ids.add(_clean(result.get("id")))
        merged.append(result)
    return merged


def _entity_key(value: Any) -> str:
    return "".join(character for character in _clean(value).casefold() if character.isalnum())


def _trial_drug_relations(
    trials: Iterable[EvidenceObject], objects: Iterable[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    drug_index: dict[str, str] = {}
    for object_ in objects:
        if object_.get("type") != "drug":
            continue
        values = [
            object_.get("label"),
            object_.get("preferred_name"),
            *(object_.get("aliases") or []),
            *(object_.get("brand_names") or []),
            *(object_.get("development_codes") or []),
        ]
        for value in values:
            if _entity_key(value):
                drug_index[_entity_key(value)] = _clean(object_.get("id"))
    relations: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for trial in trials:
        attributes = trial.attributes
        intervention_names: list[str] = []
        for intervention in attributes.get("interventions") or []:
            if not isinstance(intervention, Mapping):
                continue
            intervention_names.append(_clean(intervention.get("name")))
            intervention_names.extend(
                _clean(value) for value in intervention.get("other_names") or []
            )
        for name in intervention_names:
            drug_id = drug_index.get(_entity_key(name))
            key = (trial.id, drug_id or "")
            if not drug_id or key in seen:
                continue
            seen.add(key)
            relations.append(
                make_relation(
                    subject_id=trial.id,
                    predicate="trial_tests_drug",
                    object_id=drug_id,
                    qualifiers={
                        "intervention_name": name,
                        "conditions": attributes.get("conditions") or [],
                        "phases": attributes.get("phases") or [],
                        "status": attributes.get("overall_status")
                        or attributes.get("status"),
                    },
                    evidence_refs=(
                        {
                            "source_ref": "source:clinicaltrials.gov:"
                            + _clean(attributes.get("registry_id")),
                            "locator": "protocolSection.armsInterventionsModule",
                        },
                    ),
                )
            )
    return relations


def _dataset_paper_relations(
    objects: Iterable[Mapping[str, Any]],
    papers: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Link an explicit DataCite related DOI only when that paper is present."""

    paper_by_doi = {
        doi: _clean(paper.get("id"))
        for paper in papers
        if (doi := backend.normalize_doi((paper.get("identifiers") or {}).get("doi")))
    }
    relations: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for object_ in objects:
        if object_.get("type") != "dataset":
            continue
        related_values = (object_.get("attributes") or {}).get(
            "related_identifiers"
        ) or []
        for index, related in enumerate(related_values):
            if not isinstance(related, Mapping):
                continue
            identifier_type = _clean(
                related.get("relatedIdentifierType")
                or related.get("related_identifier_type")
            ).casefold()
            if identifier_type != "doi":
                continue
            doi = backend.normalize_doi(
                related.get("relatedIdentifier")
                or related.get("related_identifier")
            )
            paper_id = paper_by_doi.get(doi or "")
            if not doi or not paper_id:
                continue
            relation_type = _clean(
                related.get("relationType") or related.get("relation_type")
            )
            predicate = {
                "isdocumentedby": "dataset_described_by_paper",
                "isdescribedby": "dataset_described_by_paper",
                "issupplementto": "dataset_supplements_paper",
            }.get(_entity_key(relation_type), "dataset_related_to_paper")
            key = (_clean(object_.get("id")), predicate, paper_id)
            if key in seen:
                continue
            seen.add(key)
            source_ref = next(
                (
                    _clean(value.get("id"))
                    for value in object_.get("source_refs") or []
                    if isinstance(value, Mapping) and _clean(value.get("id"))
                ),
                None,
            )
            relations.append(
                make_relation(
                    subject_id=key[0],
                    predicate=predicate,
                    object_id=paper_id,
                    qualifiers={
                        "datacite_relation_type": relation_type or None,
                        "related_doi": doi,
                    },
                    evidence_refs=(
                        {
                            "source_ref": source_ref,
                            "locator": f"attributes.related_identifiers[{index}]",
                        },
                    ),
                )
            )
    return relations


def _source_summary(statuses: Iterable[Mapping[str, Any]]) -> dict[str, list[str]]:
    values = list(statuses)
    sources = _unique(_clean(status.get("source")) for status in values)
    buckets: dict[str, list[str]] = {
        "successful": [],
        "partial": [],
        "failed": [],
        "skipped": [],
        "not_run": [],
    }
    for source in sources:
        states = {
            _clean(item.get("status"))
            for item in values
            if _clean(item.get("source")) == source
        }
        if "ok" in states:
            bucket = "partial" if states.intersection({"error", "skipped"}) else "successful"
        elif "error" in states:
            bucket = "failed"
        elif "skipped" in states:
            bucket = "skipped"
        else:
            bucket = "not_run"
        buckets[bucket].append(source)
    return {
        "successful": buckets["successful"],
        "partial": buckets["partial"],
        "failed": buckets["failed"],
        "skipped": buckets["skipped"],
        "not_run": buckets["not_run"],
    }


def _eligible_retrieval_results(
    results: Iterable[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    """Return verified, stable, non-retracted papers usable as coverage/seeds."""

    eligible: list[Mapping[str, Any]] = []
    for result in results:
        if result.get("is_retracted") is True:
            continue
        if (result.get("verification") or {}).get("level") == "web_unverified":
            continue
        paper = _paper_from_result(result)
        if citation_eligibility_for(paper).get("eligible") is True:
            eligible.append(result)
    return eligible


def execute_plan(
    plan: SearchPlan,
    *,
    normalization_audit: Mapping[str, Any] | None = None,
    timeout: float = 20.0,
    retries: int = 2,
    snippet_chars: int = 700,
    include_registry_objects: bool = True,
    enrich_open_access: bool = True,
) -> dict[str, Any]:
    """Execute one validated plan and return a canonical schema-v2 bundle."""

    request = plan.request
    options = _options(plan)
    filters = _result_filters(plan)
    all_records: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    trial_objects: list[EvidenceObject] = []
    dataset_objects: list[dict[str, Any]] = []
    entity_objects: list[dict[str, Any]] = []
    expansion_audit: dict[str, Any] = {
        "requested": request.expansion,
        "planned": plan.budget.expansion,
        "effective": "none",
        "seed_based_related_fallback": False,
        "weak_verified_result_count": None,
        "seed_count": 0,
        "one_round": True,
    }

    if request.dry_run:
        for route in plan.routes:
            for lane in plan.lanes_for_source(route.source):
                statuses.append(
                    _not_run_status(
                        route.source,
                        lane,
                        "Dry-run requested; no network call was made.",
                    )
                )
    else:
        web_records, web_statuses = backend.load_agent_web_results(
            request.web_result_files, request.question, options
        )
        all_records.extend(web_records)
        statuses.extend(
            normalize_source_status(value) for value in web_statuses
        )

        initial_records, initial_statuses = _execute_route_group(
            plan,
            options=options,
            timeout=timeout,
            retries=retries,
        )
        all_records.extend(initial_records)
        statuses.extend(initial_statuses)

        preliminary = _reconcile(
            all_records,
            plan,
            filters,
            snippet_chars=snippet_chars,
        )
        eligible_preliminary = _eligible_retrieval_results(preliminary)
        expansion_audit["weak_verified_result_count"] = len(eligible_preliminary)
        mode = plan.budget.expansion
        exact_lookup = any(lane.family == "exact_identifier" for lane in plan.lanes)
        if (
            mode == "none"
            and request.expansion == "auto"
            and request.depth == "standard"
            and len(eligible_preliminary) < plan.budget.weak_result_threshold
            and not exact_lookup
        ):
            # This is a seed-based related-paper fallback, not an embedding
            # search.  The distinction is retained in the audit artifact.
            mode = "related"
            expansion_audit["seed_based_related_fallback"] = True
        expansion_audit["effective"] = mode
        if (
            mode != "none"
            and request.source_override
            and "semantic-scholar" not in plan.sources
        ):
            expansion_audit["effective"] = "none"
            expansion_audit["skipped_reason"] = (
                "Semantic Scholar graph expansion was not selected by the explicit source override."
            )
            mode = "none"
        if mode != "none":
            seeds = eligible_preliminary[: plan.budget.expansion_seeds]
            expansion_audit["seed_count"] = len(seeds)
            expanded, expansion_statuses = backend.run_semantic_scholar_expansion(
                seeds,
                mode,
                plan.budget.expansion_per_seed,
                request.question,
                options,
                timeout,
                retries,
            )
            all_records.extend(expanded)
            statuses.extend(
                normalize_source_status(value)
                for value in expansion_statuses
            )
            if mode in {"citations", "both"} and not request.source_override:
                expanded, expansion_statuses = backend.run_open_citations_expansion(
                    seeds,
                    mode,
                    plan.budget.expansion_per_seed,
                    request.question,
                    options,
                    timeout,
                    retries,
                )
                all_records.extend(expanded)
                statuses.extend(
                    normalize_source_status(value)
                    for value in expansion_statuses
                )

        if (
            enrich_open_access
            and plan.request.depth != "quick"
            and not request.source_override
        ):
            oa_seeds = _reconcile(
                all_records,
                plan,
                filters,
                snippet_chars=snippet_chars,
                limit=min(10, plan.budget.result_limit),
            )
            enriched, enrichment_statuses = backend.run_unpaywall_enrichment(
                oa_seeds,
                request.question,
                options,
                timeout,
                retries,
            )
            all_records.extend(enriched)
            statuses.extend(
                normalize_source_status(value)
                for value in enrichment_statuses
            )

    registry_needed = (
        include_registry_objects
        and "clinicaltrials" in plan.sources
        and bool(set(request.scenarios).intersection(REGISTRY_SCENARIOS))
    )
    if registry_needed:
        trial_scenarios = [
            value for value in request.scenarios if value in REGISTRY_SCENARIOS
        ]
        trial_objects, trial_status = fetch_trial_objects(
            request,
            limit=min(100, plan.budget.per_source),
            timeout=timeout,
            retries=retries,
        )
        trial_status = dict(trial_status)
        trial_status.setdefault("source_role", trial_status.pop("role", "primary_registry"))
        trial_status.setdefault("query_family", "trial_registry")
        trial_status.setdefault("query_lane", "registry.clinicaltrials")
        trial_status.setdefault("query_origin", "first_class_registry")
        trial_status["scenario"] = trial_scenarios[0]
        trial_status["scenarios"] = trial_scenarios
        trial_status.setdefault("evidence_dimension", "trial_registry")
        statuses.append(normalize_source_status(trial_status))

    dataset_registry_needed = (
        include_registry_objects
        and "datacite" in plan.sources
        and "methods-benchmarking" in request.scenarios
        and (
            request.depth != "quick"
            or bool(request.concepts_of("dataset", "accession"))
        )
    )
    if dataset_registry_needed:
        dataset_objects, dataset_status = fetch_dataset_objects(
            request,
            limit=min(100, plan.budget.per_source),
            timeout=timeout,
            retries=retries,
        )
        dataset_status = dict(dataset_status)
        dataset_status["scenario"] = "methods-benchmarking"
        dataset_status["scenarios"] = ["methods-benchmarking"]
        statuses.append(normalize_source_status(dataset_status))

    entity_registry_needed = (
        include_registry_objects
        and bool({"target-research", "drug-pipeline"}.intersection(request.scenarios))
        and "open-targets" in plan.sources
    )
    if entity_registry_needed:
        entity_scenarios = [
            value
            for value in request.scenarios
            if value in {"target-research", "drug-pipeline"}
        ]
        entity_objects, entity_status = fetch_entity_objects(
            request,
            limit=min(100, plan.budget.per_source),
            timeout=timeout,
            retries=retries,
        )
        entity_status = dict(entity_status)
        entity_status["scenario"] = entity_scenarios[0]
        entity_status["scenarios"] = entity_scenarios
        statuses.append(normalize_source_status(entity_status))

    results = _reconcile(
        all_records,
        plan,
        filters,
        snippet_chars=snippet_chars,
    )
    paper_objects = [_paper_from_result(result) for result in results]
    concept_objects = _objects_from_concepts(request.concepts)
    database_objects = _merge_database_objects(
        [*dataset_objects, *entity_objects, *concept_objects]
    )
    relations = [
        *_trial_drug_relations(trial_objects, database_objects),
        *_dataset_paper_relations(database_objects, paper_objects),
    ]
    normalized_statuses = [
        normalize_source_status(value) for value in statuses
    ]
    source_summary = _source_summary(normalized_statuses)
    retrieved_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    warnings = list(plan.warnings)
    if source_summary["failed"]:
        warnings.append("Failed sources: " + ", ".join(source_summary["failed"]))
    if request.source_override and enrich_open_access and request.depth != "quick":
        warnings.append(
            "Unpaywall enrichment was disabled because the explicit source override bounds all external retrieval providers."
        )
    if request.constraints.species:
        warnings.append(
            "Species constraints are source-native only where supported; other lanes encode the species in the query and remain bounded metadata screening."
        )
    retrieval = {
        "plan": [lane.to_dict() for lane in plan.lanes],
        "routes": [route.to_dict() for route in plan.routes],
        "ontology_packs": list(plan.ontology_packs),
        "budget": plan.budget.to_dict(),
        "normalization": dict(normalization_audit or {}),
        "expansion": expansion_audit,
        "source_status": normalized_statuses,
        "source_summary": source_summary,
        "ledger": build_search_ledger(normalized_statuses),
        "constraints": request.constraints.to_dict(),
        "bounded": {
            "exhaustive": False,
            "per_source_record_cap": plan.budget.per_source,
            "per_lane_request_cap": plan.budget.per_lane,
            "max_calls_per_source": plan.budget.max_calls_per_source,
            "planned_source_operations": sum(
                len(route.lane_ids) for route in plan.routes
            ),
            "final_result_limit": plan.budget.result_limit,
            "weak_result_threshold": plan.budget.weak_result_threshold,
            "retrieved_at": None if request.dry_run else retrieved_at,
            "note": "Source totals overlap and must not be summed; this is bounded evidence discovery.",
        },
    }
    return build_evidence_bundle(
        evidence_objects=[
            *paper_objects,
            *trial_objects,
            *database_objects,
        ],
        request=request,
        plan=plan,
        relations=relations,
        retrieval=retrieval,
        retrieval_state="not_performed" if request.dry_run else "performed",
        warnings=warnings,
    )


def run_search(
    request: SearchRequest,
    *,
    terminology_dir: str | None = None,
    timeout: float = 20.0,
    retries: int = 2,
    snippet_chars: int = 700,
    include_registry_objects: bool = True,
    enrich_open_access: bool = True,
) -> dict[str, Any]:
    """Normalize concepts, plan the scenario, execute it, and build v2 output."""

    concepts = tuple(
        dataclasses.replace(
            concept,
            expansion="exact_synonyms_descendants",
        )
        if request.include_descendants
        and concept.type
        in {
            "disease",
            "condition",
            "indication",
            "phenotype",
            "hpo",
            "compound",
            "chemical",
            "go-term",
            "go_term",
            "pathway",
            "cell-type",
            "cell_type",
            "tissue",
        }
        else concept
        for concept in request.concepts
    )
    normalized, audit = normalize_concepts(
        concepts,
        enabled=request.normalize,
        dry_run=request.dry_run,
        timeout=min(timeout, 8.0),
        terminology_dir=terminology_dir,
    )
    request = dataclasses.replace(request, concepts=normalized)
    plan = build_plan(request)
    return execute_plan(
        plan,
        normalization_audit=audit,
        timeout=timeout,
        retries=retries,
        snippet_chars=snippet_chars,
        include_registry_objects=include_registry_objects,
        enrich_open_access=enrich_open_access,
    )
