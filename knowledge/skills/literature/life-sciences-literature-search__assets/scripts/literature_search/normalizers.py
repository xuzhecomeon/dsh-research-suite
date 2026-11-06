"""Auditable, conservative concept normalization.

Only exact identifiers, labels, and synonyms are accepted automatically.  A
provider failure or ambiguous response always preserves the caller's term.
Licensed vocabularies such as MedDRA and organization-specific INN/CMeSH maps
can be supplied as local JSON packs; their absence is an explicit degradation.
"""

from __future__ import annotations

import dataclasses
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional

from ._version import USER_AGENT
from .models import Concept


# Keep this runtime type alias importable on the oldest Python supported by the
# workspace test runner.  PEP 604 annotations elsewhere are postponed by the
# future import, while aliases are evaluated immediately at module import time.
JsonFetcher = Callable[[str, Optional[Dict[str, str]], float], Any]

HGNC_ENDPOINT = "https://rest.genenames.org/search"
OLS_ENDPOINT = "https://www.ebi.ac.uk/ols4/api/search"
OLS_API_ROOT = "https://www.ebi.ac.uk/ols4/api"
MAX_DESCENDANTS = 20
CHEMBL_ENDPOINT = "https://www.ebi.ac.uk/chembl/api/data/molecule/search.json"
MESH_ENDPOINT = "https://id.nlm.nih.gov/mesh/lookup/term"
NCBI_TAXONOMY_ENDPOINT = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

ID_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("hgnc", re.compile(r"^HGNC:\d+$", re.I), "HGNC"),
    ("mondo", re.compile(r"^MONDO:\d+$", re.I), "MONDO"),
    ("hpo", re.compile(r"^HP:\d+$", re.I), "HPO"),
    ("chebi", re.compile(r"^CHEBI:\d+$", re.I), "ChEBI"),
    ("chembl", re.compile(r"^CHEMBL\d+$", re.I), "ChEMBL"),
    ("mesh", re.compile(r"^[CD]\d{6,9}$", re.I), "MeSH"),
    ("rsid", re.compile(r"^rs\d+$", re.I), "dbSNP"),
    ("clinicaltrials", re.compile(r"^NCT\d{8}$", re.I), "ClinicalTrials.gov"),
    ("geo", re.compile(r"^GSE\d+$", re.I), "GEO"),
    ("sra", re.compile(r"^(?:SRP|SRA|SRR|SRS|SRX)\d+$", re.I), "SRA"),
    ("arrayexpress", re.compile(r"^E-[A-Z]+-\d+$", re.I), "ArrayExpress"),
)

OLS_BY_TYPE = {
    "disease": ("mondo", "MONDO"),
    "condition": ("mondo", "MONDO"),
    "indication": ("mondo", "MONDO"),
    "phenotype": ("hp", "HPO"),
    "hpo": ("hp", "HPO"),
    "compound": ("chebi", "ChEBI"),
    "chemical": ("chebi", "ChEBI"),
    "go-term": ("go", "GO"),
    "go_term": ("go", "GO"),
    "pathway": ("go", "GO"),
    "cell-type": ("cl", "Cell Ontology"),
    "cell_type": ("cl", "Cell Ontology"),
    "tissue": ("uberon", "UBERON"),
}

LOCAL_PACK_BY_TYPE = {
    "drug": ("inn", "WHO INN / local drug map"),
    "drug_class": ("atc", "ATC / local drug-class map"),
    "adverse-event": ("meddra", "MedDRA"),
    "adverse_event": ("meddra", "MedDRA"),
    "topic-zh": ("cmesh", "CMeSH"),
    "topic_zh": ("cmesh", "CMeSH"),
    "method": ("edam", "EDAM / local method map"),
    "data_modality": ("edam", "EDAM / local data map"),
    "assay": ("obi", "OBI / local assay map"),
    "modality": ("therapeutic_modality", "Local therapeutic-modality map"),
    "therapeutic_modality": (
        "therapeutic_modality",
        "Local therapeutic-modality map",
    ),
    "sponsor": ("sponsor_aliases", "Local sponsor alias map"),
}

STUDY_DESIGNS = {
    "rct": ("Randomized Controlled Trial", ("randomized controlled trial", "randomised controlled trial")),
    "meta-analysis": ("Meta-Analysis", ("meta analysis", "meta-analysis")),
    "systematic-review": ("Systematic Review", ("systematic review",)),
    "cohort": ("Cohort Study", ("cohort", "cohort study")),
    "case-control": ("Case-Control Study", ("case control", "case-control study")),
    "case-report": ("Case Report", ("case report", "case series")),
    "guideline": ("Guideline", ("clinical guideline", "practice guideline", "consensus")),
}


def _key(value: Any) -> str:
    return "".join(character for character in str(value).casefold() if character.isalnum())


def _unique(values: Iterable[Any], *, limit: int = 12) -> tuple[str, ...]:
    cleaned = []
    seen = set()
    for value in values:
        text = " ".join(str(value or "").split())
        if not text or _key(text) in seen:
            continue
        seen.add(_key(text))
        cleaned.append(text)
        if len(cleaned) >= limit:
            break
    return tuple(cleaned)


def fetch_json(url: str, headers: dict[str, str] | None, timeout: float) -> Any:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, **(headers or {})},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read(8 * 1024 * 1024)
    return json.loads(payload.decode("utf-8"))


def _accepted(
    concept: Concept,
    *,
    canonical_id: str,
    label: str,
    synonyms: Iterable[str],
    resolver: str,
    ontology: str,
    status: str,
    provenance: dict[str, Any],
) -> Concept:
    return dataclasses.replace(
        concept,
        canonical_id=canonical_id or None,
        canonical_label=label or None,
        synonyms=_unique(value for value in synonyms if _key(value) != _key(concept.input)),
        mapping_status=status,
        resolver=resolver,
        ontology=ontology,
        confidence="high",
        provenance=provenance,
    )


def _unresolved(
    concept: Concept,
    status: str,
    resolver: str | None,
    ontology: str | None,
    provenance: dict[str, Any],
) -> Concept:
    return dataclasses.replace(
        concept,
        mapping_status=status,
        resolver=resolver,
        ontology=ontology,
        confidence=None,
        provenance=provenance,
    )


def normalize_exact_identifier(concept: Concept) -> Concept | None:
    value = concept.input.strip()
    for resolver, pattern, ontology in ID_PATTERNS:
        if pattern.fullmatch(value):
            canonical = value.upper() if resolver != "rsid" else value.lower()
            return _accepted(
                concept,
                canonical_id=canonical,
                label=value,
                synonyms=(),
                resolver=resolver,
                ontology=ontology,
                status="exact_id",
                provenance={"method": "identifier_pattern"},
            )
    return None


def _load_local_pack(directory: Path | None, name: str) -> tuple[dict[str, dict[str, Any]], str | None]:
    if directory is None:
        return {}, "terminology directory not configured"
    path = directory / f"{name}.json"
    if not path.exists():
        return {}, f"{path.name} not found"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {}, f"failed to read {path.name}: {error}"
    entries: list[dict[str, Any]]
    if isinstance(payload, list):
        entries = [item for item in payload if isinstance(item, dict)]
    elif isinstance(payload, dict) and isinstance(payload.get("entries"), list):
        entries = [item for item in payload["entries"] if isinstance(item, dict)]
    elif isinstance(payload, dict):
        entries = []
        for term, item in payload.items():
            if isinstance(item, dict):
                entries.append({"term": term, **item})
    else:
        return {}, f"{path.name} has an unsupported JSON shape"
    index: dict[str, dict[str, Any]] = {}
    for item in entries:
        values = [
            item.get("term"),
            item.get("label"),
            item.get("preferred_label"),
            *(item.get("synonyms") or []),
            *(item.get("aliases") or []),
        ]
        for value in values:
            if value:
                index[_key(value)] = item
    return index, None


def _resolve_local(concept: Concept, directory: Path | None) -> Concept | None:
    config = LOCAL_PACK_BY_TYPE.get(concept.type)
    if config is None:
        return None
    pack_name, ontology = config
    index, error = _load_local_pack(directory, pack_name)
    item = index.get(_key(concept.input))
    if item:
        label = item.get("preferred_label") or item.get("label") or concept.input
        match_status = "exact_label" if _key(label) == _key(concept.input) else "exact_synonym"
        return _accepted(
            concept,
            canonical_id=str(item.get("id") or item.get("code") or ""),
            label=str(label),
            synonyms=item.get("synonyms") or item.get("aliases") or (),
            resolver=f"local-{pack_name}",
            ontology=str(item.get("ontology") or ontology),
            status=match_status,
            provenance={"pack": pack_name, "version": item.get("version")},
        )
    return _unresolved(
        concept,
        "unavailable" if error else "no_match",
        f"local-{pack_name}",
        ontology,
        {"degradation": error or "no exact local mapping"},
    )


def _resolve_study_design(concept: Concept) -> Concept | None:
    if concept.type not in {"study-design", "study_design"}:
        return None
    expected = _key(concept.input)
    matches = []
    for identifier, (label, synonyms) in STUDY_DESIGNS.items():
        values = (label, identifier, *synonyms)
        if expected in {_key(value) for value in values}:
            matches.append((identifier, label, synonyms))
    if len(matches) == 1:
        identifier, label, synonyms = matches[0]
        return _accepted(
            concept,
            canonical_id=identifier,
            label=label,
            synonyms=synonyms,
            resolver="built-in-study-design",
            ontology="controlled study-design vocabulary",
            status="exact_label" if expected == _key(label) else "exact_synonym",
            provenance={"method": "controlled_exact_match"},
        )
    return _unresolved(
        concept,
        "ambiguous" if len(matches) > 1 else "no_match",
        "built-in-study-design",
        "controlled study-design vocabulary",
        {"candidate_count": len(matches)},
    )


def _resolve_hgnc(concept: Concept, get: JsonFetcher, timeout: float) -> Concept:
    url = f"{HGNC_ENDPOINT}/{urllib.parse.quote(concept.input)}"
    payload = get(url, {"Accept": "application/json"}, timeout)
    docs = ((payload or {}).get("response") or {}).get("docs") or []
    expected = _key(concept.input)
    matches = []
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        values = [doc.get("symbol"), doc.get("hgnc_id")]
        values.extend(doc.get("prev_symbol") or [])
        values.extend(doc.get("alias_symbol") or [])
        if expected in {_key(value) for value in values if value}:
            matches.append(doc)
    unique = {str(item.get("hgnc_id") or item.get("symbol")): item for item in matches}
    if len(unique) != 1:
        return _unresolved(
            concept,
            "ambiguous" if len(unique) > 1 else "no_match",
            "hgnc",
            "HGNC",
            {"endpoint": HGNC_ENDPOINT, "candidate_count": len(unique)},
        )
    doc = next(iter(unique.values()))
    symbol = str(doc.get("symbol") or concept.input)
    status = "exact_label" if expected == _key(symbol) else "exact_synonym"
    return _accepted(
        concept,
        canonical_id=str(doc.get("hgnc_id") or ""),
        label=symbol,
        synonyms=(*(doc.get("prev_symbol") or []), *(doc.get("alias_symbol") or [])),
        resolver="hgnc",
        ontology="HGNC",
        status=status,
        provenance={"endpoint": HGNC_ENDPOINT},
    )


def _ols_values(doc: dict[str, Any]) -> tuple[str, ...]:
    values: list[Any] = [doc.get("label"), doc.get("obo_id"), doc.get("short_form")]
    for key in ("exact_synonyms", "synonym", "synonyms"):
        raw = doc.get(key) or []
        values.extend(raw if isinstance(raw, list) else [raw])
    return _unique(values, limit=30)


def _resolve_ols(concept: Concept, get: JsonFetcher, timeout: float) -> Concept:
    ontology_slug, ontology_label = OLS_BY_TYPE[concept.type]
    params = urllib.parse.urlencode(
        {
            "q": concept.input,
            "ontology": ontology_slug,
            "rows": "12",
            "queryFields": "label,synonym,obo_id,short_form",
        }
    )
    payload = get(f"{OLS_ENDPOINT}?{params}", None, timeout)
    docs = ((payload or {}).get("response") or {}).get("docs") or []
    expected = _key(concept.input)
    matches = [
        doc
        for doc in docs
        if isinstance(doc, dict)
        and expected in {_key(value) for value in _ols_values(doc)}
    ]
    unique = {
        str(item.get("obo_id") or item.get("iri") or item.get("label")): item
        for item in matches
    }
    if len(unique) != 1:
        return _unresolved(
            concept,
            "ambiguous" if len(unique) > 1 else "no_match",
            "ols4",
            ontology_label,
            {"endpoint": OLS_ENDPOINT, "candidate_count": len(unique)},
        )
    doc = next(iter(unique.values()))
    label = str(doc.get("label") or concept.input)
    status = "exact_label" if expected == _key(label) else "exact_synonym"
    accepted = _accepted(
        concept,
        canonical_id=str(doc.get("obo_id") or doc.get("short_form") or ""),
        label=label,
        synonyms=_ols_values(doc),
        resolver="ols4",
        ontology=ontology_label,
        status=status,
        provenance={"endpoint": OLS_ENDPOINT},
    )
    if concept.expansion not in {"descendants", "exact_synonyms_descendants"}:
        return accepted

    canonical_id = str(doc.get("obo_id") or doc.get("short_form") or "")
    descendant_url = (
        f"{OLS_API_ROOT}/ontologies/{urllib.parse.quote(ontology_slug, safe='')}"
        "/hierarchicalDescendants?"
        + urllib.parse.urlencode(
            {"id": canonical_id, "page": "0", "size": str(MAX_DESCENDANTS)}
        )
    )
    provenance = dict(accepted.provenance)
    provenance["descendant_endpoint"] = descendant_url.split("?", 1)[0]
    provenance["descendant_limit"] = MAX_DESCENDANTS
    try:
        descendant_payload = get(descendant_url, None, timeout)
        embedded = (
            (descendant_payload or {}).get("_embedded")
            if isinstance(descendant_payload, dict)
            else None
        )
        terms = embedded.get("terms") if isinstance(embedded, dict) else None
        descendants = _unique(
            (
                value.get("label")
                for value in (terms or [])
                if isinstance(value, dict) and value.get("label")
            ),
            limit=MAX_DESCENDANTS,
        )
        provenance["descendant_count"] = len(descendants)
        provenance["descendant_ids"] = list(
            _unique(
                (
                    value.get("obo_id") or value.get("short_form")
                    for value in (terms or [])
                    if isinstance(value, dict)
                ),
                limit=MAX_DESCENDANTS,
            )
        )
        return dataclasses.replace(
            accepted,
            descendants=descendants,
            provenance=provenance,
        )
    except (OSError, ValueError, KeyError, urllib.error.URLError) as error:
        provenance["descendant_expansion_error"] = str(error)[:300]
        return dataclasses.replace(accepted, provenance=provenance)


def _resolve_chembl(concept: Concept, get: JsonFetcher, timeout: float) -> Concept:
    params = urllib.parse.urlencode({"q": concept.input, "limit": "10"})
    payload = get(f"{CHEMBL_ENDPOINT}?{params}", {"Accept": "application/json"}, timeout)
    molecules = (payload or {}).get("molecules") or []
    expected = _key(concept.input)
    matches: list[dict[str, Any]] = []
    for molecule in molecules:
        if not isinstance(molecule, dict):
            continue
        synonyms = [
            item.get("molecule_synonym")
            for item in molecule.get("molecule_synonyms") or []
            if isinstance(item, dict)
        ]
        values = [molecule.get("pref_name"), molecule.get("molecule_chembl_id"), *synonyms]
        if expected in {_key(value) for value in values if value}:
            molecule = dict(molecule)
            molecule["_synonyms"] = synonyms
            matches.append(molecule)
    unique = {
        str(item.get("molecule_chembl_id") or item.get("pref_name")): item
        for item in matches
    }
    if len(unique) != 1:
        return _unresolved(
            concept,
            "ambiguous" if len(unique) > 1 else "no_match",
            "chembl",
            "ChEMBL",
            {"endpoint": CHEMBL_ENDPOINT, "candidate_count": len(unique)},
        )
    molecule = next(iter(unique.values()))
    label = str(molecule.get("pref_name") or concept.input)
    status = "exact_label" if expected == _key(label) else "exact_synonym"
    return _accepted(
        concept,
        canonical_id=str(molecule.get("molecule_chembl_id") or ""),
        label=label,
        synonyms=molecule.get("_synonyms") or (),
        resolver="chembl",
        ontology="ChEMBL",
        status=status,
        provenance={"endpoint": CHEMBL_ENDPOINT},
    )


def _resolve_mesh(concept: Concept, get: JsonFetcher, timeout: float) -> Concept:
    params = urllib.parse.urlencode({"label": concept.input, "match": "exact", "limit": "10"})
    payload = get(f"{MESH_ENDPOINT}?{params}", {"Accept": "application/json"}, timeout)
    items = payload if isinstance(payload, list) else []
    expected = _key(concept.input)
    matches = [item for item in items if isinstance(item, dict) and _key(item.get("label")) == expected]
    if len(matches) != 1:
        return _unresolved(
            concept,
            "ambiguous" if len(matches) > 1 else "no_match",
            "mesh-lookup",
            "MeSH",
            {"endpoint": MESH_ENDPOINT, "candidate_count": len(matches)},
        )
    item = matches[0]
    resource = str(item.get("resource") or "")
    return _accepted(
        concept,
        canonical_id=resource.rsplit("/", 1)[-1],
        label=str(item.get("label") or concept.input),
        synonyms=(),
        resolver="mesh-lookup",
        ontology="MeSH",
        status="exact_label",
        provenance={"endpoint": MESH_ENDPOINT, "resource": resource},
    )


def _resolve_taxonomy(concept: Concept, get: JsonFetcher, timeout: float) -> Concept:
    params = urllib.parse.urlencode(
        {"db": "taxonomy", "term": concept.input, "retmode": "json", "retmax": "5"}
    )
    search_url = f"{NCBI_TAXONOMY_ENDPOINT}/esearch.fcgi?{params}"
    payload = get(search_url, None, timeout)
    ids = ((payload or {}).get("esearchresult") or {}).get("idlist") or []
    if len(ids) != 1:
        return _unresolved(
            concept,
            "ambiguous" if len(ids) > 1 else "no_match",
            "ncbi-taxonomy",
            "NCBI Taxonomy",
            {"endpoint": NCBI_TAXONOMY_ENDPOINT, "candidate_count": len(ids)},
        )
    summary_params = urllib.parse.urlencode(
        {"db": "taxonomy", "id": ids[0], "retmode": "json"}
    )
    summary = get(f"{NCBI_TAXONOMY_ENDPOINT}/esummary.fcgi?{summary_params}", None, timeout)
    item = ((summary or {}).get("result") or {}).get(str(ids[0])) or {}
    label = str(item.get("scientificname") or concept.input)
    aliases = [item.get("commonname"), *(item.get("othernames") or [])]
    return _accepted(
        concept,
        canonical_id=str(ids[0]),
        label=label,
        synonyms=aliases,
        resolver="ncbi-taxonomy",
        ontology="NCBI Taxonomy",
        status="exact_label" if _key(label) == _key(concept.input) else "exact_synonym",
        provenance={"endpoint": NCBI_TAXONOMY_ENDPOINT},
    )


def normalize_concept(
    concept: Concept,
    *,
    get: JsonFetcher = fetch_json,
    timeout: float = 8.0,
    terminology_dir: Path | None = None,
) -> Concept:
    identifier = normalize_exact_identifier(concept)
    if identifier is not None:
        return identifier
    local = _resolve_local(concept, terminology_dir)
    if local is not None and local.mapping_status not in {"unavailable", "no_match"}:
        return local
    controlled = _resolve_study_design(concept)
    if controlled is not None:
        return controlled
    try:
        if concept.type in {"gene", "target", "protein"}:
            return _resolve_hgnc(concept, get, timeout)
        if concept.type in OLS_BY_TYPE:
            return _resolve_ols(concept, get, timeout)
        if concept.type == "drug":
            chembl = _resolve_chembl(concept, get, timeout)
            if chembl.mapping_status not in {"no_match", "ambiguous"}:
                return chembl
            return local or chembl
        if concept.type in {
            "topic",
            "medical-subject",
            "medical_subject",
            "mesh_heading",
        }:
            return _resolve_mesh(concept, get, timeout)
        if concept.type in {"species", "organism"}:
            return _resolve_taxonomy(concept, get, timeout)
    except (OSError, ValueError, KeyError, urllib.error.URLError) as error:
        return _unresolved(
            concept,
            "error",
            concept.resolver,
            concept.ontology,
            {"error": str(error)[:300]},
        )
    return local or _unresolved(
        concept,
        "not_applicable",
        None,
        None,
        {"reason": "no configured exact resolver for this concept type"},
    )


def normalize_concepts(
    concepts: Iterable[Concept],
    *,
    enabled: bool,
    dry_run: bool,
    get: JsonFetcher = fetch_json,
    timeout: float = 8.0,
    terminology_dir: str | Path | None = None,
) -> tuple[tuple[Concept, ...], dict[str, Any]]:
    supplied = tuple(concepts)
    if not enabled or dry_run:
        reason = "dry_run" if dry_run else "disabled_by_user"
        preserved = tuple(
            dataclasses.replace(
                concept,
                mapping_status="not_attempted",
                provenance={"reason": reason},
            )
            for concept in supplied
        )
        return preserved, {
            "enabled": enabled,
            "attempted": False,
            "reason": reason,
            "runs": [concept.to_dict() for concept in preserved],
            "degradations": [],
        }
    directory = Path(terminology_dir).expanduser() if terminology_dir else None
    normalized = tuple(
        normalize_concept(
            concept,
            get=get,
            timeout=timeout,
            terminology_dir=directory,
        )
        for concept in supplied
    )
    degradations = [
        {
            "type": concept.type,
            "input": concept.input,
            "status": concept.mapping_status,
            "detail": concept.provenance.get("degradation")
            or concept.provenance.get("error"),
        }
        for concept in normalized
        if concept.mapping_status in {"unavailable", "error", "ambiguous"}
    ]
    return normalized, {
        "enabled": True,
        "attempted": True,
        "reason": None,
        "runs": [concept.to_dict() for concept in normalized],
        "status_counts": {
            status: sum(concept.mapping_status == status for concept in normalized)
            for status in (
                "exact_id",
                "exact_label",
                "exact_synonym",
                "ambiguous",
                "no_match",
                "unavailable",
                "error",
                "not_applicable",
            )
        },
        "degradations": degradations,
    }
