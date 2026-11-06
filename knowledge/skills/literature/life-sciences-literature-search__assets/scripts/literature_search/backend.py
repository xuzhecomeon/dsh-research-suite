#!/usr/bin/env python3
"""Publication-source HTTP adapters and bounded multi-lane execution.

Scenario planning, typed evidence assembly, reconciliation, rendering, and the
CLI intentionally live in separate modules.  This module is restricted to the
shared publication adapter vocabulary and source-specific API integrations.
"""

from __future__ import annotations

import dataclasses
import html
import json
import os
import re
import socket
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Callable, Iterable

from ._version import USER_AGENT
from .adapter_contracts import (
    HttpFailure,
    SearchBatch,
    SearchOptions,
    SourceFailure,
    SourceSkipped,
)


MAX_RESPONSE_BYTES = 32 * 1024 * 1024
MAX_WEB_RESULTS_BYTES = 4 * 1024 * 1024
MAX_WEB_RESULT_FILES = 5
MAX_WEB_SEARCH_RUNS = 16
MAX_WEB_RESULTS = 250
RRF_K = 60
AGENT_WEB_SOURCE = "agent-web-search"
EXPANSION_STATUS_SOURCE = "semantic-scholar-expansion"
OPENCITATIONS_STATUS_SOURCE = "open-citations-expansion"
UNPAYWALL_STATUS_SOURCE = "unpaywall-enrichment"
QUERY_FAMILIES = (
    "core",
    "exact_identifier",
    "entity_combination",
    "translated_synonym",
    "synonym_expansion",
    "basic_mechanism",
    "organism_model",
    "target_genetics",
    "target_biology",
    "target_tractability",
    "target_translation",
    "pipeline_landscape",
    "trial_registry",
    "drug_safety",
    "clinical_evidence",
    "clinical_design",
    "methods_benchmark",
    "methods_validation",
    "genetic_validity",
    "variant",
    "phenotype",
    "mechanism",
    "publication_type",
    "recency",
    "citation_forward",
    "citation_backward",
    "related",
)
SEMANTIC_SCHOLAR_GRAPH_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper"
SEMANTIC_SCHOLAR_RECOMMENDATIONS_ENDPOINT = (
    "https://api.semanticscholar.org/recommendations/v1/papers/forpaper"
)
OPENCITATIONS_ENDPOINT = "https://opencitations.net/index/coci/api/v1"
UNPAYWALL_ENDPOINT = "https://api.unpaywall.org/v2"
SEMANTIC_SCHOLAR_FIELDS = (
    "paperId",
    "title",
    "authors",
    "year",
    "publicationDate",
    "venue",
    "publicationTypes",
    "abstract",
    "externalIds",
    "url",
    "openAccessPdf",
    "citationCount",
)

ALL_STRUCTURED_SOURCES = (
    "europepmc",
    "pubmed",
    "pubtator3",
    "litvar2",
    "clinvar",
    "clingen",
    "civic",
    "open-targets",
    "gwas-catalog",
    "clinicaltrials",
    "reactome",
    "uniprot",
    "openalex",
    "crossref",
    "datacite",
    "doaj",
    "openaire",
    "core",
    "arxiv",
    "dblp",
    "semantic-scholar",
)

PROFILES: dict[str, tuple[str, ...]] = {
    "general": (
        "openalex",
        "crossref",
        "datacite",
        "doaj",
        "openaire",
        "core",
        "arxiv",
        "dblp",
        "semantic-scholar",
    ),
    "life-sciences": ALL_STRUCTURED_SOURCES,
    "biomedical": ALL_STRUCTURED_SOURCES,
    "life-sciences-core": ("europepmc",),
    "computer-science": ("openalex", "dblp", "arxiv"),
    "preprints": ("arxiv", "europepmc", "openalex"),
    "all": ALL_STRUCTURED_SOURCES,
}

EPMC_LINKED_DATABASE_FIELDS = {
    "chembl": "HAS_CHEMBL",
    "embl": "HAS_EMBL",
    "intact": "HAS_INTACT",
    "interpro": "HAS_INTERPRO",
    "omim": "HAS_OMIM",
    "pdb": "HAS_PDB",
    "pride": "HAS_PRIDE",
    "uniprot": "HAS_UNIPROT",
}

SOURCE_ENDPOINTS = {
    "pubmed": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
    "europepmc": "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
    "pubtator3": "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/search/",
    "litvar2": "https://www.ncbi.nlm.nih.gov/research/litvar2-api/",
    "clinvar": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
    "clingen": "https://erepo.clinicalgenome.org/evrepo/api/summary/classifications",
    "civic": "https://civicdb.org/api/graphql",
    "open-targets": "https://api.platform.opentargets.org/api/v4/graphql",
    "gwas-catalog": "https://www.ebi.ac.uk/gwas/rest/api/v2/",
    "clinicaltrials": "https://clinicaltrials.gov/api/v2/studies",
    "reactome": "https://reactome.org/ContentService/",
    "uniprot": "https://rest.uniprot.org/uniprotkb/search",
    "openalex": "https://api.openalex.org/works",
    "crossref": "https://api.crossref.org/works",
    "datacite": "https://api.datacite.org/dois",
    "doaj": "https://doaj.org/api/search/articles/",
    "openaire": "https://api.openaire.eu/search/publications",
    "core": "https://api.core.ac.uk/v3/search/works",
    "arxiv": "https://export.arxiv.org/api/query",
    "dblp": "https://dblp.org/search/publ/api",
    "semantic-scholar": "https://api.semanticscholar.org/graph/v1/paper/search",
}

SOURCE_ORDER = {name: index for index, name in enumerate(PROFILES["all"])}
SOURCE_ORDER[AGENT_WEB_SOURCE] = len(SOURCE_ORDER)
SOURCE_ORDER["open-citations"] = len(SOURCE_ORDER)
SOURCE_ORDER["unpaywall"] = len(SOURCE_ORDER)
SOURCE_RRF_WEIGHTS = {
    AGENT_WEB_SOURCE: 0.75,
    "pubtator3": 0.9,
    "litvar2": 1.1,
    "clinvar": 1.0,
    "clingen": 1.0,
    "civic": 1.0,
    "open-targets": 0.8,
    "gwas-catalog": 0.9,
    "clinicaltrials": 0.75,
    "reactome": 0.75,
    "uniprot": 0.8,
    "datacite": 0.65,
    "doaj": 0.8,
    "openaire": 0.8,
    "core": 0.8,
    "open-citations": 0.7,
    "unpaywall": 0.0,
}
SOURCE_ROLES = {
    "europepmc": "discovery_index",
    "pubmed": "discovery_index",
    "pubtator3": "entity_aware_discovery",
    "litvar2": "curated_publication_seed",
    "clinvar": "curated_publication_seed",
    "clingen": "curated_publication_seed",
    "civic": "curated_publication_seed",
    "open-targets": "curated_publication_seed",
    "gwas-catalog": "curated_publication_seed",
    "clinicaltrials": "clinical_trial_publication_seed",
    "reactome": "curated_publication_seed",
    "uniprot": "curated_publication_seed",
    "openalex": "discovery_index",
    "crossref": "discovery_index",
    "datacite": "research_object_index",
    "doaj": "open_access_discovery_index",
    "openaire": "open_research_discovery_index",
    "core": "open_access_discovery_index",
    "arxiv": "preprint_index",
    "dblp": "domain_discovery_index",
    "semantic-scholar": "discovery_index",
    "open-citations": "citation_graph_expansion",
    "unpaywall": "open_access_enrichment",
    AGENT_WEB_SOURCE: "native_web_discovery",
}
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
WHITESPACE_RE = re.compile(r"\s+")
HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
DOI_PREFIX_RE = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)
SECRET_PARAM_RE = re.compile(r"(?i)(api[_-]?key|apikey|key|email|mailto)=([^&\s]+)")
QUERY_TOKEN_RE = re.compile(
    r"[A-Za-z0-9][A-Za-z0-9._:+>/-]*|[\u3400-\u4dbf\u4e00-\u9fff]+"
)
ENGLISH_STOPWORDS = {
    "about",
    "after",
    "among",
    "and",
    "article",
    "articles",
    "before",
    "between",
    "find",
    "for",
    "from",
    "into",
    "literature",
    "paper",
    "papers",
    "study",
    "studies",
    "the",
    "their",
    "this",
    "with",
}
COUNT_ENTITY_PATTERNS = {
    "proband": r"(?:probands?|index\s+(?:cases?|patients?))",
    "patient": r"(?:patients?)",
    "family": r"(?:famil(?:y|ies)|kindreds?|pedigrees?)",
    "case": r"(?:cases?)",
    "participant": r"(?:participants?|subjects?|individuals?)",
    "carrier": r"(?:carriers?)",
}
SCIENTIFIC_CONTEXT_RE = re.compile(
    r"(?:\b(?:NM|NP|NC|NG|NR|LRG|ENST|ENSP)_?\d+(?:\.\d+)?\b)"
    r"|(?:\b(?:rs)\d+\b)"
    r"|(?:(?:c|p|g|m|n|r)\.[A-Za-z0-9_+*?>=()\[\]-]+)",
    re.IGNORECASE,
)
VARIANT_RE = re.compile(
    r"(?:\brs\d+\b|\b[A-Z]\d{1,5}[A-Z*]\b|\b(?:VCV|RCV|SCV)\d+(?:\.\d+)?\b|"
    r"\b(?:NM|NP|NC|NG|NR|LRG|ENST|ENSP)_?\d+(?:\.\d+)?(?:\([^)]{2,20}\))?\s*:?[cgmnpr]\.\S+|"
    r"\b[cgmnpr]\.[A-Za-z0-9_+*?>=()\[\]-]+)",
    re.IGNORECASE,
)
RSID_RE = re.compile(r"\brs\d+\b", re.IGNORECASE)
DOI_TEXT_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
PMID_TEXT_RE = re.compile(r"\bPMID\s*[:#]?\s*(\d{1,9})\b", re.IGNORECASE)
PMCID_TEXT_RE = re.compile(r"\bPMC\d+\b", re.IGNORECASE)
GENE_IN_TRANSCRIPT_RE = re.compile(r"\(([A-Z][A-Z0-9-]{1,15})\)")
EXACT_PMID_RE = re.compile(r"^(?:PMID\s*:?\s*)?(\d{1,9})$", re.IGNORECASE)
EXACT_PMCID_RE = re.compile(r"^(?:PMCID\s*:?\s*)?(PMC\d+)$", re.IGNORECASE)
EXACT_ARXIV_RE = re.compile(
    r"^(?:arXiv\s*:?\s*)?(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})v?\d*$",
    re.IGNORECASE,
)


def collapse_ws(value: Any) -> str:
    if value is None:
        return ""
    text = CONTROL_RE.sub("", str(value))
    return WHITESPACE_RE.sub(" ", text).strip()


def clean_text(value: Any) -> str:
    text = html.unescape(collapse_ws(value))
    if HTML_TAG_RE.search(text):
        text = HTML_TAG_RE.sub(" ", text)
    return collapse_ws(html.unescape(text))


def truncate_text(value: str, limit: int) -> str:
    if limit <= 0 or not value:
        return ""
    if len(value) <= limit:
        return value
    shortened = value[: max(1, limit - 1)].rstrip()
    boundary = shortened.rfind(" ")
    if boundary >= max(40, limit // 2):
        shortened = shortened[:boundary]
    return shortened.rstrip(" ,;:") + "..."


def safe_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None and str(value).strip() else None
    except (TypeError, ValueError):
        return None


def optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    normalized = collapse_ws(value).casefold()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    return None


def clean_url(value: Any) -> str | None:
    url = collapse_ws(value)
    if not url:
        return None
    parts = urllib.parse.urlsplit(url)
    if parts.scheme.lower() not in {"http", "https"}:
        return None
    return url


def normalize_doi(value: Any) -> str | None:
    doi = html.unescape(collapse_ws(value)).strip()
    doi = DOI_PREFIX_RE.sub("", doi).strip().lower()
    doi = doi.rstrip(".,;)")
    if not doi.startswith("10.") or "/" not in doi or " " in doi:
        return None
    return doi


def normalize_identifier(value: Any, prefix: str = "") -> str | None:
    identifier = collapse_ws(value)
    if not identifier:
        return None
    if prefix and identifier.lower().startswith(prefix.lower()):
        identifier = identifier[len(prefix) :]
    return identifier.strip() or None


def normalize_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value)).casefold()
    return "".join(character for character in text if character.isalnum())


def extract_year(value: Any) -> int | None:
    if isinstance(value, int):
        return value if 1000 <= value <= 3000 else None
    match = re.search(r"\b(1[5-9]\d{2}|20\d{2}|2100)\b", collapse_ws(value))
    return int(match.group(1)) if match else None


def date_from_parts(parts: Iterable[Any]) -> str | None:
    values = list(parts)
    if not values:
        return None
    year = safe_int(values[0])
    if year is None:
        return None
    if len(values) < 2 or safe_int(values[1]) is None:
        return f"{year:04d}"
    month = safe_int(values[1]) or 1
    if len(values) < 3 or safe_int(values[2]) is None:
        return f"{year:04d}-{month:02d}"
    day = safe_int(values[2]) or 1
    return f"{year:04d}-{month:02d}-{day:02d}"


def infer_query_family(
    query: Any,
    original_query: Any = "",
    position: int = 0,
    explicit: Any = None,
) -> str:
    declared = collapse_ws(explicit).casefold().replace("-", "_")
    if declared in QUERY_FAMILIES:
        return declared

    text = collapse_ws(query)
    original = collapse_ws(original_query) or text
    lowered = text.casefold()
    if (
        EXACT_PMID_RE.fullmatch(text)
        or EXACT_PMCID_RE.fullmatch(text)
        or EXACT_ARXIV_RE.fullmatch(text)
        or normalize_doi(text)
    ):
        return "exact_identifier"
    if re.search(r"\b(cited by|cites|references?|forward citations?)\b", lowered):
        return "citation_forward"
    if re.search(r"\b(similar|related papers?|recommended papers?)\b", lowered):
        return "related"
    if position > 0 and (
        SCIENTIFIC_CONTEXT_RE.search(text) or GENE_IN_TRANSCRIPT_RE.search(text)
    ):
        return "entity_combination"
    original_has_cjk = bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", original))
    query_has_cjk = bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", text))
    if position > 0 and original_has_cjk != query_has_cjk:
        return "translated_synonym"
    if re.search(
        r"\b(case reports?|reviews?|meta-analys(?:is|es)|guidelines?|trials?)\b",
        lowered,
    ):
        return "publication_type"
    if re.search(
        r"\b(recent|latest|newest|since\s+20\d{2}|20\d{2}\s*[-:]\s*20\d{2})\b", lowered
    ):
        return "recency"
    if position == 0:
        return "core"
    return "synonym_expansion"


def sanitize_error(value: Any) -> str:
    message = collapse_ws(value)
    message = SECRET_PARAM_RE.sub(lambda match: f"{match.group(1)}=REDACTED", message)
    return truncate_text(message, 400) or "unknown error"


def endpoint_only(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def build_user_agent() -> str:
    base = USER_AGENT
    email = collapse_ws(os.getenv("LITERATURE_CONTACT_EMAIL"))
    return f"{base} (mailto:{email})" if email else base


class HttpClient:
    def __init__(self, timeout: float, retries: int) -> None:
        self.timeout = timeout
        self.retries = retries
        self.user_agent = build_user_agent()

    def request_bytes(
        self,
        url: str,
        *,
        method: str = "GET",
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        request_headers = {
            "Accept": "application/json, application/xml, text/xml, application/atom+xml",
            "User-Agent": self.user_agent,
        }
        if headers:
            request_headers.update(headers)

        for attempt in range(self.retries + 1):
            request = urllib.request.Request(
                url, data=body, headers=request_headers, method=method
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    length = safe_int(response.headers.get("Content-Length"))
                    if length is not None and length > MAX_RESPONSE_BYTES:
                        raise HttpFailure(
                            "response_too_large",
                            f"response Content-Length {length} exceeds {MAX_RESPONSE_BYTES}",
                        )
                    payload = response.read(MAX_RESPONSE_BYTES + 1)
                    if len(payload) > MAX_RESPONSE_BYTES:
                        raise HttpFailure(
                            "response_too_large",
                            f"response exceeded {MAX_RESPONSE_BYTES} bytes",
                        )
                    return payload
            except urllib.error.HTTPError as error:
                retryable = error.code == 429 or 500 <= error.code <= 599
                if retryable and attempt < self.retries:
                    minimum = 3.0 if "export.arxiv.org" in url else 0.75
                    self._sleep_before_retry(
                        error.headers.get("Retry-After"), attempt, minimum
                    )
                    continue
                reason = collapse_ws(error.reason)
                if not reason and error.code == 429:
                    reason = "Too Many Requests"
                raise HttpFailure(
                    "http_error",
                    f"HTTP {error.code} {reason}".rstrip(),
                    status=error.code,
                    retryable=retryable,
                ) from error
            except (urllib.error.URLError, socket.timeout, TimeoutError) as error:
                if attempt < self.retries:
                    self._sleep_before_retry(None, attempt)
                    continue
                reason = getattr(error, "reason", error)
                raise HttpFailure(
                    "network_error", sanitize_error(reason), retryable=True
                ) from error

        raise HttpFailure("network_error", "request failed", retryable=True)

    def get_bytes(self, url: str, headers: dict[str, str] | None = None) -> bytes:
        return self.request_bytes(url, headers=headers)

    def get_json(self, url: str, headers: dict[str, str] | None = None) -> Any:
        payload = self.get_bytes(url, headers=headers)
        return self._parse_json(payload)

    def post_json(
        self,
        url: str,
        data: Any,
        headers: dict[str, str] | None = None,
    ) -> Any:
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        payload = self.request_bytes(
            url,
            method="POST",
            body=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            headers=request_headers,
        )
        return self._parse_json(payload)

    @staticmethod
    def _parse_json(payload: bytes) -> Any:
        prefix = payload.lstrip()[:256].lower()
        if prefix.startswith(b"<!doctype html") or b"<html" in prefix:
            raise HttpFailure(
                "unexpected_html",
                "API returned an HTML page instead of structured data; the client IP may be blocked or redirected",
                retryable=False,
            )
        try:
            return json.loads(payload.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise HttpFailure("invalid_json", sanitize_error(error)) from error

    @staticmethod
    def _sleep_before_retry(
        retry_after: str | None, attempt: int, minimum: float = 0.75
    ) -> None:
        seconds = min(4.0, minimum * (2**attempt))
        if retry_after:
            try:
                seconds = min(8.0, max(seconds, float(retry_after)))
            except ValueError:
                pass
        time.sleep(seconds)


def make_record(
    source: str,
    source_id: Any,
    query: str,
    rank: int,
    *,
    title: Any,
    authors: Iterable[Any] | None = None,
    year: Any = None,
    publication_date: Any = None,
    venue: Any = None,
    publication_type: Any = None,
    language: Any = None,
    abstract: Any = None,
    identifiers: dict[str, Any] | None = None,
    url: Any = None,
    open_access_url: Any = None,
    citation_count: Any = None,
    source_enrichment: dict[str, Any] | None = None,
    query_family: Any = None,
    is_retracted: Any = None,
    has_correction: Any = None,
    publication_states: Iterable[Any] | None = None,
) -> dict[str, Any]:
    clean_identifiers: dict[str, str] = {}
    for name, value in (identifiers or {}).items():
        normalized = (
            normalize_doi(value) if name == "doi" else normalize_identifier(value)
        )
        if normalized:
            clean_identifiers[name] = normalized

    clean_authors = [clean_text(author) for author in (authors or [])]
    clean_authors = [author for author in clean_authors if author][:100]
    normalized_date = collapse_ws(publication_date) or None
    normalized_year = safe_int(year) or extract_year(normalized_date)
    normalized_citations = safe_int(citation_count)
    normalized_states = list(
        dict.fromkeys(
            clean_text(value).casefold().replace(" ", "_")
            for value in (publication_states or [])
            if clean_text(value)
        )
    )
    if isinstance(language, (list, tuple, set)):
        language = ", ".join(
            collapse_ws(value) for value in language if collapse_ws(value)
        )

    return {
        "source": source,
        "source_id": collapse_ws(source_id),
        "query": query,
        "query_family": infer_query_family(query, query, 0, explicit=query_family),
        "source_rank": rank,
        "title": clean_text(title),
        "authors": clean_authors,
        "year": normalized_year,
        "publication_date": normalized_date,
        "venue": clean_text(venue),
        "publication_type": clean_text(publication_type),
        "language": clean_text(language).lower(),
        "abstract": clean_text(abstract),
        "identifiers": clean_identifiers,
        "url": clean_url(url),
        "open_access_url": clean_url(open_access_url),
        "citation_count": normalized_citations,
        "source_enrichment": source_enrichment or {},
        "is_retracted": optional_bool(is_retracted),
        "has_correction": optional_bool(has_correction),
        "publication_states": normalized_states,
    }


def publication_state_from_types(
    publication_types: Iterable[Any],
) -> tuple[bool | None, bool | None, list[str]]:
    normalized = {
        normalize_metadata_term(value)
        for value in publication_types
        if normalize_metadata_term(value)
    }
    states: list[str] = []
    is_retracted: bool | None = None
    has_correction: bool | None = None
    if "retractedpublication" in normalized:
        is_retracted = True
        states.append("retracted")
    if "retractionofpublication" in normalized or "retraction" in normalized:
        has_correction = True
        states.append("retraction_notice")
    if normalized.intersection(
        {
            "publishederratum",
            "correctedandrepublishedarticle",
            "correction",
            "erratum",
        }
    ):
        has_correction = True
        states.append("correction_notice")
    return is_retracted, has_correction, states


def crossref_publication_state(
    item: dict[str, Any],
) -> tuple[bool | None, bool | None, list[str]]:
    relation = item.get("relation") or {}
    relation_names = (
        {
            normalize_metadata_term(name)
            for name in relation
            if normalize_metadata_term(name)
        }
        if isinstance(relation, dict)
        else set()
    )
    item_type = normalize_metadata_term(item.get("type"))
    update_types = {
        normalize_metadata_term(update.get("type"))
        for update in (item.get("update-to") or [])
        if isinstance(update, dict) and normalize_metadata_term(update.get("type"))
    }
    states: list[str] = []
    is_retracted: bool | None = None
    has_correction: bool | None = None
    if "isretractedby" in relation_names:
        is_retracted = True
        states.append("retracted")
    if (
        item_type == "retraction"
        or "isretractionof" in relation_names
        or "retraction" in update_types
    ):
        has_correction = True
        states.append("retraction_notice")
    correction_relations = {
        "iscorrectedby",
        "iscorrectionof",
        "isupdatedby",
        "updates",
    }
    if (
        relation_names.intersection(correction_relations)
        or item_type in {"correction", "erratum"}
        or update_types.intersection({"correction", "erratum", "update"})
    ):
        has_correction = True
        states.append("correction_notice")
    return is_retracted, has_correction, states


def reconstruct_openalex_abstract(index: Any) -> str:
    if not isinstance(index, dict):
        return ""
    positioned: list[tuple[int, str]] = []
    for word, positions in index.items():
        if not isinstance(positions, list):
            continue
        for position in positions:
            numeric = safe_int(position)
            if numeric is not None:
                positioned.append((numeric, str(word)))
        if len(positioned) > 20_000:
            break
    positioned.sort(key=lambda item: item[0])
    return collapse_ws(" ".join(word for _, word in positioned))


def normalize_english_token(value: str) -> str:
    normalized = value.casefold().strip("._:+>/-")
    if (
        len(normalized) > 4
        and normalized.endswith("s")
        and not any(character.isdigit() for character in normalized)
    ):
        normalized = normalized[:-1]
    return normalized


def query_tokens(query: str) -> list[tuple[str, float, bool]]:
    tokens: list[tuple[str, float, bool]] = []
    seen: set[str] = set()
    for raw in QUERY_TOKEN_RE.findall(unicodedata.normalize("NFKC", query)):
        has_cjk = any("\u3400" <= character <= "\u9fff" for character in raw)
        candidates: list[str]
        if has_cjk:
            candidates = (
                [raw]
                if len(raw) <= 3
                else [raw[index : index + 2] for index in range(len(raw) - 1)]
            )
            candidates = [
                value
                for value in candidates
                if not any(mark in value for mark in "的与和或在")
            ]
        else:
            candidates = [normalize_english_token(raw)]
        for candidate in candidates:
            if (
                len(candidate) < 2
                or candidate in ENGLISH_STOPWORDS
                or candidate in seen
            ):
                continue
            seen.add(candidate)
            identifier_like = not has_cjk and (
                any(character.isdigit() for character in raw)
                or (raw.isupper() and len(raw) >= 3)
                or raw.lower().startswith(("rs", "nm_", "np_", "hp:"))
            )
            tokens.append((candidate, 3.0 if identifier_like else 1.0, has_cjk))
    return tokens


def lexical_coverage(query: str, records: list[dict[str, Any]]) -> float:
    tokens = query_tokens(query)
    if not tokens:
        return 0.0
    content = " ".join(
        [
            *(collapse_ws(record.get("title")) for record in records),
            *(collapse_ws(record.get("abstract")) for record in records),
            *(
                " ".join(
                    str(value) for value in (record.get("identifiers") or {}).values()
                )
                for record in records
            ),
        ]
    )
    normalized_content = unicodedata.normalize("NFKC", content).casefold()
    content_words = {
        normalize_english_token(token)
        for token in QUERY_TOKEN_RE.findall(normalized_content)
    }
    matched = 0.0
    total = 0.0
    for token, weight, has_cjk in tokens:
        total += weight
        if (has_cjk and token in normalized_content) or (
            not has_cjk and token in content_words
        ):
            matched += weight
    return matched / total if total else 0.0


def normalize_metadata_term(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean_text(value)).casefold()
    normalized = "".join(character for character in text if character.isalnum())
    if normalized.endswith("ies"):
        return normalized[:-3] + "y"
    if len(normalized) > 4 and normalized.endswith("s"):
        return normalized[:-1]
    return normalized


def normalize_context_term(value: Any) -> str:
    text = unicodedata.normalize("NFKC", collapse_ws(value)).casefold()
    return re.sub(r"[\s()\[\]]+", "", text)


def extract_context_terms(
    queries: Iterable[str], explicit_terms: Iterable[str] = ()
) -> list[str]:
    terms: list[str] = []
    for query in queries:
        terms.extend(match.group(0) for match in SCIENTIFIC_CONTEXT_RE.finditer(query))
        terms.extend(match.group(1) for match in GENE_IN_TRANSCRIPT_RE.finditer(query))
    terms.extend(explicit_terms)

    expanded: list[str] = []
    for term in terms:
        cleaned = collapse_ws(term)
        if not cleaned:
            continue
        expanded.append(cleaned)
        if re.match(r"^(?:NM|NP|NC|NG|NR|ENST|ENSP)_?\d+\.\d+$", cleaned, re.I):
            expanded.append(cleaned.rsplit(".", 1)[0])
    return list(dict.fromkeys(expanded))


def count_sentences(text: str) -> list[str]:
    normalized = clean_text(text)
    if not normalized:
        return []
    return [
        collapse_ws(sentence)
        for sentence in re.split(r"(?<=[.!?])\s+|\s*[;\n]\s*", normalized)
        if collapse_ws(sentence)
    ]


def extract_count_signals(
    text: str, entities: Iterable[str], context_terms: Iterable[str]
) -> list[dict[str, Any]]:
    normalized_context = [
        (term, normalize_context_term(term))
        for term in context_terms
        if normalize_context_term(term)
    ]
    signals: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    adjectives = r"(?:(?:unrelated|affected|independent|additional|consecutive|sporadic|familial)\s+){0,2}"

    for sentence in count_sentences(text):
        sentence_context = normalize_context_term(sentence)
        matched_context = [
            term
            for term, normalized in normalized_context
            if normalized in sentence_context
        ]
        for entity in entities:
            label = COUNT_ENTITY_PATTERNS[entity]
            patterns = (
                re.compile(
                    rf"(?P<count>[1-9]\d{{0,3}})\s*(?:/|\bof\b)\s*[1-9]\d{{0,3}}\s+{adjectives}(?:{label})\b",
                    re.IGNORECASE,
                ),
                re.compile(
                    rf"\b(?P<count>[1-9]\d{{0,3}})\s+{adjectives}(?:{label})\b",
                    re.IGNORECASE,
                ),
                re.compile(
                    rf"\b(?:n\s*=\s*)?(?P<count>[1-9]\d{{0,3}})\s+{adjectives}(?:{label})\b",
                    re.IGNORECASE,
                ),
                re.compile(
                    rf"\b(?:{label})\s*(?:\(|\[|,|:)?\s*n\s*=\s*(?P<count>[1-9]\d{{0,3}})\s*[)\]]?",
                    re.IGNORECASE,
                ),
            )
            for pattern_index, pattern in enumerate(patterns):
                for match in pattern.finditer(sentence):
                    if pattern_index in {1, 2}:
                        prefix = sentence[max(0, match.start() - 8) : match.start()]
                        if re.search(r"(?:/|\bof\s)$", prefix, re.IGNORECASE):
                            continue
                    count = safe_int(match.group("count"))
                    if count is None or count > 5000:
                        continue
                    key = (entity, count, sentence)
                    if key in seen:
                        continue
                    seen.add(key)
                    signals.append(
                        {
                            "count": count,
                            "entity": entity,
                            "context_matched": bool(matched_context),
                            "matched_context_terms": matched_context,
                            "evidence": truncate_text(sentence, 360),
                        }
                    )
    signals.sort(
        key=lambda signal: (
            not signal["context_matched"],
            -signal["count"],
            signal["entity"],
            signal["evidence"],
        )
    )
    return signals


def screen_reported_count(
    text: str,
    minimum: int,
    entities: Iterable[str],
    context_terms: Iterable[str],
    require_context: bool,
) -> dict[str, Any]:
    entity_list = list(dict.fromkeys(entities))
    context_list = list(dict.fromkeys(context_terms))
    signals = extract_count_signals(text, entity_list, context_list)
    threshold_signals = [signal for signal in signals if signal["count"] >= minimum]
    qualifying = (
        [signal for signal in threshold_signals if signal["context_matched"]]
        if require_context
        else threshold_signals
    )
    if qualifying:
        status = "meets_threshold"
        best_count = max(signal["count"] for signal in qualifying)
    elif threshold_signals:
        status = "threshold_met_without_context"
        best_count = max(signal["count"] for signal in threshold_signals)
    elif signals:
        status = "below_threshold"
        best_count = max(signal["count"] for signal in signals)
    else:
        status = "unknown"
        best_count = None
    return {
        "status": status,
        "minimum": minimum,
        "entities": entity_list,
        "require_variant_context": require_context,
        "context_terms": context_list,
        "best_count": best_count,
        "signals": signals[:8],
        "note": "Automated abstract screening signal; verify the evidence sentence and full text before treating it as a variant-specific proband count.",
    }


def add_date_filter(query: str, options: SearchOptions, field: str) -> str:
    if options.year_from is None and options.year_to is None:
        return query
    start = options.year_from or 1500
    end = options.year_to or datetime.now().year
    return f"({query}) AND {start}:{end}[{field}]"


def europepmc_base_expression(query: str) -> str:
    """Use Europe PMC's identifier fields for exact single-identifier lookups."""
    value = collapse_ws(query)
    pmcid_match = EXACT_PMCID_RE.fullmatch(value)
    if pmcid_match:
        return f"PMCID:{pmcid_match.group(1).upper()}"
    pmid_match = EXACT_PMID_RE.fullmatch(value)
    if pmid_match:
        return f"EXT_ID:{pmid_match.group(1)} AND SRC:MED"
    doi = normalize_doi(value)
    if doi:
        return f"DOI:{json.dumps(doi)}"
    return value


def europepmc_or_clause(field: str, values: Iterable[str]) -> str | None:
    normalized = [collapse_ws(value) for value in values if collapse_ws(value)]
    if not normalized:
        return None
    terms = [f"{field}:{json.dumps(value, ensure_ascii=False)}" for value in normalized]
    return terms[0] if len(terms) == 1 else f"({' OR '.join(terms)})"


def build_europepmc_expression(query: str, options: SearchOptions) -> str:
    expression = europepmc_base_expression(query)
    clauses: list[str] = []
    if options.year_from or options.year_to:
        start = options.year_from or 1500
        end = options.year_to or datetime.now().year
        clauses.append(f"FIRST_PDATE:[{start}-01-01 TO {end}-12-31]")
    if options.open_access:
        clauses.append("OPEN_ACCESS:Y")
    if options.publication_types:
        clause = europepmc_or_clause("PUB_TYPE", options.publication_types)
        if clause:
            clauses.append(clause)
    for field, values in (
        ("GENE_PROTEIN", options.genes),
        ("DISEASE", options.diseases),
        ("CHEM", options.chemicals),
        ("GOTERM", options.go_terms),
        ("EXPERIMENTAL_METHOD", options.experimental_methods),
        ("ACCESSION_ID", options.accession_ids),
        ("ACCESSION_TYPE", options.accession_types),
    ):
        clause = europepmc_or_clause(field, values)
        if clause:
            clauses.append(clause)
    if options.linked_databases:
        linked = [
            f"{EPMC_LINKED_DATABASE_FIELDS[name]}:Y"
            for name in options.linked_databases
        ]
        clauses.append(linked[0] if len(linked) == 1 else f"({' OR '.join(linked)})")
    if options.has_associated_data:
        clauses.append("HAS_DATA:Y")
    return " AND ".join([f"({expression})", *clauses]) if clauses else expression


def search_openalex(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    filters: list[str] = []
    if options.year_from:
        filters.append(f"from_publication_date:{options.year_from}-01-01")
    if options.year_to:
        filters.append(f"to_publication_date:{options.year_to}-12-31")
    elif options.sort == "newest":
        filters.append(f"to_publication_date:{datetime.now().year + 1}-12-31")
    if options.open_access:
        filters.append("is_oa:true")

    params: dict[str, str] = {
        "search": query,
        "per-page": str(options.per_source),
        "select": ",".join(
            (
                "id",
                "doi",
                "title",
                "publication_year",
                "publication_date",
                "type",
                "language",
                "authorships",
                "primary_location",
                "best_oa_location",
                "open_access",
                "is_retracted",
                "cited_by_count",
                "abstract_inverted_index",
                "ids",
            )
        ),
    }
    if filters:
        params["filter"] = ",".join(filters)
    email = collapse_ws(os.getenv("LITERATURE_CONTACT_EMAIL"))
    api_key = collapse_ws(os.getenv("OPENALEX_API_KEY"))
    if email:
        params["mailto"] = email
    if api_key:
        params["api_key"] = api_key

    url = SOURCE_ENDPOINTS["openalex"] + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url)
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise SourceFailure("invalid_response", "OpenAlex response has no results list")
    if data.get("error"):
        raise SourceFailure(
            "api_error", sanitize_error(data.get("message") or data["error"])
        )

    records: list[dict[str, Any]] = []
    for rank, item in enumerate(data["results"], start=1):
        if not isinstance(item, dict):
            continue
        authors = []
        for authorship in item.get("authorships") or []:
            if isinstance(authorship, dict):
                author = authorship.get("author") or {}
                if isinstance(author, dict) and author.get("display_name"):
                    authors.append(author["display_name"])

        primary = item.get("primary_location") or {}
        best_oa = item.get("best_oa_location") or {}
        oa = item.get("open_access") or {}
        ids = item.get("ids") or {}
        source = primary.get("source") or {} if isinstance(primary, dict) else {}
        doi = normalize_doi(item.get("doi"))
        openalex_id = normalize_identifier(item.get("id"), "https://openalex.org/")
        pmid = normalize_identifier(ids.get("pmid"), "https://pubmed.ncbi.nlm.nih.gov/")
        if pmid:
            pmid = pmid.rstrip("/")
        pmcid = normalize_identifier(
            ids.get("pmcid"), "https://www.ncbi.nlm.nih.gov/pmc/articles/"
        )
        if pmcid:
            pmcid = pmcid.rstrip("/")
        landing = primary.get("landing_page_url") if isinstance(primary, dict) else None
        oa_url = None
        if isinstance(best_oa, dict):
            oa_url = best_oa.get("pdf_url") or best_oa.get("landing_page_url")
        if not oa_url and isinstance(oa, dict):
            oa_url = oa.get("oa_url")

        records.append(
            make_record(
                "openalex",
                openalex_id or item.get("id"),
                query,
                rank,
                title=item.get("title") or item.get("display_name"),
                authors=authors,
                year=item.get("publication_year"),
                publication_date=item.get("publication_date"),
                venue=source.get("display_name") if isinstance(source, dict) else None,
                publication_type=item.get("type"),
                language=item.get("language"),
                abstract=reconstruct_openalex_abstract(
                    item.get("abstract_inverted_index")
                ),
                identifiers={
                    "doi": doi,
                    "pmid": pmid,
                    "pmcid": pmcid,
                    "openalex": openalex_id,
                },
                url=(f"https://doi.org/{doi}" if doi else landing or item.get("id")),
                open_access_url=oa_url,
                citation_count=item.get("cited_by_count"),
                is_retracted=item.get("is_retracted"),
                publication_states=("retracted",)
                if item.get("is_retracted") is True
                else (),
            )
        )

    total = safe_int((data.get("meta") or {}).get("count"))
    return SearchBatch(records, total, endpoint_only(url))


def crossref_date(item: dict[str, Any]) -> str | None:
    for key in (
        "published-print",
        "published-online",
        "published",
        "issued",
        "created",
    ):
        value = item.get(key)
        if not isinstance(value, dict):
            continue
        date_parts = value.get("date-parts")
        if (
            isinstance(date_parts, list)
            and date_parts
            and isinstance(date_parts[0], list)
        ):
            parsed = date_from_parts(date_parts[0])
            if parsed:
                return parsed
    return None


def search_crossref(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    exact_doi = normalize_doi(query)
    if exact_doi:
        url = (
            SOURCE_ENDPOINTS["crossref"] + "/" + urllib.parse.quote(exact_doi, safe="")
        )
        data = client.get_json(url)
        message = data.get("message") if isinstance(data, dict) else None
        if not isinstance(message, dict):
            raise SourceFailure(
                "invalid_response", "Crossref exact DOI response is malformed"
            )
        items = [message]
        reported_total = 1
    else:
        items = []
        reported_total = None
    params: dict[str, str] = {
        "query.bibliographic": query,
        "rows": str(options.per_source),
    }
    filters = []
    if options.year_from:
        filters.append(f"from-pub-date:{options.year_from}-01-01")
    if options.year_to:
        filters.append(f"until-pub-date:{options.year_to}-12-31")
    elif options.sort == "newest":
        filters.append(f"until-pub-date:{datetime.now().year + 1}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    email = collapse_ws(os.getenv("LITERATURE_CONTACT_EMAIL"))
    if email:
        params["mailto"] = email

    if not exact_doi:
        url = SOURCE_ENDPOINTS["crossref"] + "?" + urllib.parse.urlencode(params)
        data = client.get_json(url)
        message = data.get("message") if isinstance(data, dict) else None
        if not isinstance(message, dict) or not isinstance(message.get("items"), list):
            raise SourceFailure(
                "invalid_response", "Crossref response has no message.items list"
            )
        items = message["items"]
        reported_total = safe_int(message.get("total-results"))

    records: list[dict[str, Any]] = []
    for rank, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        title_value = item.get("title") or []
        title = (
            title_value[0]
            if isinstance(title_value, list) and title_value
            else None
            if isinstance(title_value, list)
            else title_value
        )
        container = item.get("container-title") or []
        venue = (
            container[0]
            if isinstance(container, list) and container
            else None
            if isinstance(container, list)
            else container
        )
        authors = []
        for author in item.get("author") or []:
            if not isinstance(author, dict):
                continue
            name = author.get("name") or " ".join(
                part for part in (author.get("given"), author.get("family")) if part
            )
            if name:
                authors.append(name)
        doi = normalize_doi(item.get("DOI"))
        publication_date = crossref_date(item)
        is_retracted, has_correction, publication_states = crossref_publication_state(
            item
        )
        records.append(
            make_record(
                "crossref",
                doi or item.get("URL"),
                query,
                rank,
                title=title,
                authors=authors,
                year=extract_year(publication_date),
                publication_date=publication_date,
                venue=venue,
                publication_type=item.get("type"),
                language=item.get("language"),
                abstract=item.get("abstract"),
                identifiers={"doi": doi},
                url=f"https://doi.org/{doi}" if doi else item.get("URL"),
                citation_count=item.get("is-referenced-by-count"),
                is_retracted=is_retracted,
                has_correction=has_correction,
                publication_states=publication_states,
            )
        )
    return SearchBatch(records, reported_total, endpoint_only(url))


def parse_europepmc_response(
    data: Any,
    query: str,
    endpoint: str,
    *,
    source: str = "europepmc",
    origin_enrichment: dict[str, Any] | None = None,
) -> SearchBatch:
    if not isinstance(data, dict):
        raise SourceFailure("invalid_response", "Europe PMC response is not an object")
    if data.get("error") or data.get("errorList"):
        raise SourceFailure(
            "api_error", sanitize_error(data.get("error") or data.get("errorList"))
        )
    result_list = data.get("resultList") or {}
    results = result_list.get("result") if isinstance(result_list, dict) else None
    if results is None:
        results = []
    if not isinstance(results, list):
        raise SourceFailure("invalid_response", "Europe PMC resultList is malformed")

    records: list[dict[str, Any]] = []
    for rank, item in enumerate(results, start=1):
        if not isinstance(item, dict):
            continue
        authors: list[str] = []
        author_list = item.get("authorList") or {}
        for author in (
            author_list.get("author") or [] if isinstance(author_list, dict) else []
        ):
            if isinstance(author, dict):
                name = author.get("fullName") or " ".join(
                    part
                    for part in (author.get("firstName"), author.get("lastName"))
                    if part
                )
                if name:
                    authors.append(name)
        if not authors and item.get("authorString"):
            authors = [part.strip() for part in str(item["authorString"]).split(",")]

        item_source = collapse_ws(item.get("source")) or "MED"
        item_id = normalize_identifier(item.get("id"))
        pmid = normalize_identifier(item.get("pmid"))
        pmcid = normalize_identifier(item.get("pmcid"))
        doi = normalize_doi(item.get("doi"))
        source_id = item_id or pmid or pmcid or doi
        is_oa = str(item.get("isOpenAccess", "")).upper() == "Y"
        oa_url = f"https://europepmc.org/articles/{pmcid}" if pmcid and is_oa else None
        full_text_urls = item.get("fullTextUrlList") or {}
        if not oa_url and isinstance(full_text_urls, dict):
            entries = full_text_urls.get("fullTextUrl") or []
            for entry in entries if isinstance(entries, list) else []:
                if not isinstance(entry, dict):
                    continue
                candidate = clean_url(entry.get("url"))
                availability = collapse_ws(entry.get("availability")).lower()
                if candidate and ("open" in availability or is_oa):
                    oa_url = candidate
                    break
        journal_info = item.get("journalInfo") or {}
        journal = journal_info.get("journal") if isinstance(journal_info, dict) else {}
        venue = item.get("journalTitle")
        if not venue and isinstance(journal, dict):
            venue = journal.get("title") or journal.get("medlineAbbreviation")
        canonical_url = (
            "https://europepmc.org/article/"
            + urllib.parse.quote(item_source, safe="")
            + "/"
            + urllib.parse.quote(source_id or "", safe="")
        )
        publication_types = item.get("pubTypeList") or {}
        publication_type = item.get("pubType")
        if isinstance(publication_types, dict):
            values = publication_types.get("pubType")
            if isinstance(values, list):
                publication_type = ", ".join(str(value) for value in values)
        publication_type_values = (
            values
            if isinstance(publication_types, dict) and isinstance(values, list)
            else [publication_type]
        )
        type_retracted, has_correction, publication_states = (
            publication_state_from_types(publication_type_values)
        )
        source_retracted = optional_bool(item.get("isRetracted"))
        is_retracted = (
            True
            if source_retracted is True or type_retracted is True
            else source_retracted
        )
        if is_retracted is True and "retracted" not in publication_states:
            publication_states.append("retracted")

        cross_references = item.get("dbCrossReferenceList") or {}
        linked_databases = (
            cross_references.get("dbName") if isinstance(cross_references, dict) else []
        )
        if not isinstance(linked_databases, list):
            linked_databases = [linked_databases] if linked_databases else []
        accession_types = item.get("tmAccessionTypeList") or {}
        text_mined_accession_types = (
            accession_types.get("accessionType")
            if isinstance(accession_types, dict)
            else []
        )
        if not isinstance(text_mined_accession_types, list):
            text_mined_accession_types = (
                [text_mined_accession_types] if text_mined_accession_types else []
            )
        source_enrichment = {
            "has_associated_data": str(item.get("hasData", "")).upper() == "Y",
            "has_references": str(item.get("hasReferences", "")).upper() == "Y",
            "has_text_mined_terms": str(item.get("hasTextMinedTerms", "")).upper()
            == "Y",
            "has_database_cross_references": str(
                item.get("hasDbCrossReferences", "")
            ).upper()
            == "Y",
            "linked_databases": [
                clean_text(value) for value in linked_databases if clean_text(value)
            ],
            "text_mined_accession_types": [
                clean_text(value)
                for value in text_mined_accession_types
                if clean_text(value)
            ],
        }
        if origin_enrichment:
            source_enrichment.update(origin_enrichment)
        if source != "europepmc":
            source_enrichment["hydrated_by"] = "europepmc"

        records.append(
            make_record(
                source,
                source_id,
                query,
                rank,
                title=item.get("title"),
                authors=authors,
                year=item.get("pubYear"),
                publication_date=item.get("firstPublicationDate"),
                venue=venue,
                publication_type=publication_type,
                language=item.get("language"),
                abstract=item.get("abstractText"),
                identifiers={"doi": doi, "pmid": pmid, "pmcid": pmcid},
                url=canonical_url,
                open_access_url=oa_url,
                citation_count=item.get("citedByCount"),
                source_enrichment=source_enrichment,
                is_retracted=is_retracted,
                has_correction=has_correction,
                publication_states=publication_states,
            )
        )
    return SearchBatch(records, safe_int(data.get("hitCount")), endpoint)


def search_europepmc(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    expression = build_europepmc_expression(query, options)
    params = {
        "query": expression,
        "format": "json",
        "resultType": "core",
        "pageSize": str(options.per_source),
    }
    if options.mesh_synonyms:
        params["synonym"] = "true"
    url = SOURCE_ENDPOINTS["europepmc"] + "?" + urllib.parse.urlencode(params)
    return parse_europepmc_response(client.get_json(url), query, endpoint_only(url))


GENE_TOKEN_EXCLUSIONS = {
    "ACMG",
    "API",
    "DNA",
    "DOI",
    "FDA",
    "GO",
    "GWAS",
    "HGVS",
    "HPO",
    "MCP",
    "NIH",
    "OA",
    "PCR",
    "PMC",
    "PMCID",
    "PMID",
    "RNA",
    "SNP",
    "WHO",
}


def unique_clean(values: Iterable[Any]) -> list[str]:
    return list(
        dict.fromkeys(collapse_ws(value) for value in values if collapse_ws(value))
    )


def concept_match_key(value: Any) -> str:
    text = unicodedata.normalize("NFKC", collapse_ws(value)).casefold()
    return "".join(character for character in text if character.isalnum())


def variant_terms(query: str, options: SearchOptions) -> list[str]:
    values = [match.group(0).rstrip(".,;)") for match in VARIANT_RE.finditer(query)]
    values.extend(
        value
        for value in options.accession_ids
        if RSID_RE.fullmatch(collapse_ws(value))
        or VARIANT_RE.search(collapse_ws(value))
    )
    return unique_clean(values)


def gene_terms(query: str, options: SearchOptions) -> list[str]:
    values = [*options.genes, *options.concept_genes]
    values.extend(match.group(1) for match in GENE_IN_TRANSCRIPT_RE.finditer(query))
    for token in re.findall(
        r"(?<![A-Za-z0-9-])([A-Z][A-Z0-9-]{1,14})(?![A-Za-z0-9-])", query
    ):
        if re.fullmatch(r"[A-Z]\d{1,5}[A-Z*]", token):
            continue
        if token not in GENE_TOKEN_EXCLUSIONS and not token.startswith(
            ("NM_", "NP_", "NC_", "ENST")
        ):
            values.append(token)
    return unique_clean(values)[:5]


def trial_query_applicable(query: str, options: SearchOptions) -> bool:
    return bool(
        options.chemicals
        or re.search(
            r"\b(?:clinical\s+trial|trial|phase\s+[ivx]+|treatment|therapy|drug|intervention|randomi[sz]ed)\b",
            query,
            re.IGNORECASE,
        )
        or re.search(r"临床试验|治疗|药物|干预", query)
    )


def pathway_query_applicable(query: str, options: SearchOptions) -> bool:
    return bool(
        options.go_terms
        or gene_terms(query, options)
        or re.search(r"\b(?:pathway|signaling|mechanism|interaction)\b", query, re.I)
        or re.search(r"通路|机制|互作", query)
    )


def gwas_query_applicable(query: str, options: SearchOptions) -> bool:
    return bool(
        RSID_RE.search(query)
        or gene_terms(query, options)
        or options.diseases
        or options.concept_diseases
        or re.search(
            r"\b(?:GWAS|genome[- ]wide|association|polygenic|risk\s+score|trait)\b",
            query,
            re.IGNORECASE,
        )
        or re.search(r"全基因组关联|多基因风险|性状", query)
    )


def ncbi_query_params(values: dict[str, Any]) -> dict[str, Any]:
    params = dict(values)
    params["tool"] = "life_sciences_literature_search"
    email = collapse_ws(os.getenv("LITERATURE_CONTACT_EMAIL"))
    api_key = collapse_ws(os.getenv("NCBI_API_KEY"))
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    return params


def recursive_key_values(payload: Any, names: Iterable[str]) -> list[Any]:
    wanted = {re.sub(r"[^a-z0-9]", "", name.casefold()) for name in names}
    values: list[Any] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = re.sub(r"[^a-z0-9]", "", str(key).casefold())
                if normalized in wanted:
                    if isinstance(child, list):
                        values.extend(child)
                    elif not isinstance(child, (dict, tuple, set)):
                        values.append(child)
                visit(child)
        elif isinstance(value, (list, tuple, set)):
            for child in value:
                visit(child)

    visit(payload)
    return values


def extract_publication_identifiers(payload: Any) -> dict[str, list[str]]:
    pmids: list[str] = []
    pmcids: list[str] = []
    dois: list[str] = []
    for value in recursive_key_values(
        payload,
        ("pmid", "pmids", "pubmed_id", "pubmedId", "pubmedIdentifier"),
    ):
        normalized = normalize_identifier(value)
        if normalized and normalized.isdigit() and len(normalized) <= 9:
            pmids.append(normalized)
    for value in recursive_key_values(payload, ("pmcid", "pmcids", "pmc_id")):
        match = PMCID_TEXT_RE.search(collapse_ws(value))
        if match:
            pmcids.append(match.group(0).upper())
    for value in recursive_key_values(
        payload, ("doi", "dois", "digitalObjectIdentifier")
    ):
        normalized = normalize_doi(value)
        if normalized:
            dois.append(normalized)

    def scan(value: Any) -> None:
        if isinstance(value, str):
            pmids.extend(match.group(1) for match in PMID_TEXT_RE.finditer(value))
            pmcids.extend(
                match.group(0).upper() for match in PMCID_TEXT_RE.finditer(value)
            )
            dois.extend(
                doi
                for doi in (
                    normalize_doi(match.group(0))
                    for match in DOI_TEXT_RE.finditer(value)
                )
                if doi
            )
        elif isinstance(value, dict):
            for child in value.values():
                scan(child)
        elif isinstance(value, (list, tuple, set)):
            for child in value:
                scan(child)

    scan(payload)
    return {
        "pmid": unique_clean(pmids),
        "pmcid": unique_clean(pmcids),
        "doi": unique_clean(dois),
    }


def hydrate_publication_identifiers(
    client: HttpClient,
    source: str,
    query: str,
    options: SearchOptions,
    identifiers: dict[str, list[str]],
    origin_endpoint: str,
    *,
    origin_enrichment: dict[str, Any] | None = None,
) -> SearchBatch:
    terms: list[str] = []
    terms.extend(
        f"(EXT_ID:{value} AND SRC:MED)" for value in identifiers.get("pmid", [])
    )
    terms.extend(f"PMCID:{value}" for value in identifiers.get("pmcid", []))
    terms.extend(f'DOI:"{value}"' for value in identifiers.get("doi", []))
    terms = unique_clean(terms)[: options.per_source]
    if not terms:
        return SearchBatch([], 0, origin_endpoint)
    params = {
        "query": " OR ".join(terms),
        "format": "json",
        "resultType": "core",
        "pageSize": str(min(options.per_source, len(terms))),
    }
    url = SOURCE_ENDPOINTS["europepmc"] + "?" + urllib.parse.urlencode(params)
    enrichment = dict(origin_enrichment or {})
    enrichment["seed_identifier_count"] = len(terms)
    return parse_europepmc_response(
        client.get_json(url),
        query,
        origin_endpoint,
        source=source,
        origin_enrichment=enrichment,
    )


def response_total(payload: Any) -> int | None:
    for value in recursive_key_values(
        payload, ("total", "totalCount", "hitCount", "count", "totalElements")
    ):
        parsed = safe_int(value)
        if parsed is not None:
            return parsed
    return None


def element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return collapse_ws("".join(element.itertext()))


def pubmed_publication_date(article: ET.Element) -> str | None:
    article_date = article.find(".//Article/ArticleDate")
    if article_date is not None:
        parsed = date_from_parts(
            (
                element_text(article_date.find("Year")),
                element_text(article_date.find("Month")),
                element_text(article_date.find("Day")),
            )
        )
        if parsed:
            return parsed
    pub_date = article.find(".//JournalIssue/PubDate")
    if pub_date is not None:
        year = element_text(pub_date.find("Year")) or element_text(
            pub_date.find("MedlineDate")
        )
        month_text = element_text(pub_date.find("Month"))
        day = element_text(pub_date.find("Day"))
        month_map = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }
        month = safe_int(month_text) or month_map.get(month_text[:3].lower())
        parsed_year = extract_year(year)
        if parsed_year and month:
            return date_from_parts((parsed_year, month, safe_int(day)))
        if parsed_year:
            return str(parsed_year)
    return None


def parse_pubmed_xml(payload: bytes, query: str) -> list[dict[str, Any]]:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as error:
        raise SourceFailure("invalid_xml", sanitize_error(error)) from error

    records: list[dict[str, Any]] = []
    for rank, article in enumerate(root.findall(".//PubmedArticle"), start=1):
        pmid = normalize_identifier(
            element_text(article.find(".//MedlineCitation/PMID"))
        )
        title = element_text(article.find(".//Article/ArticleTitle"))
        authors = []
        for author in article.findall(".//Article/AuthorList/Author"):
            collective = element_text(author.find("CollectiveName"))
            personal = " ".join(
                part
                for part in (
                    element_text(author.find("ForeName")),
                    element_text(author.find("LastName")),
                )
                if part
            )
            if collective or personal:
                authors.append(collective or personal)

        abstract_parts = []
        for section in article.findall(".//Article/Abstract/AbstractText"):
            value = element_text(section)
            label = collapse_ws(section.attrib.get("Label"))
            if value:
                abstract_parts.append(f"{label}: {value}" if label else value)

        identifiers: dict[str, Any] = {"pmid": pmid}
        for article_id in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
            id_type = collapse_ws(article_id.attrib.get("IdType")).lower()
            value = element_text(article_id)
            if id_type == "doi":
                identifiers["doi"] = normalize_doi(value)
            elif id_type in {"pmc", "pmcid"}:
                identifiers["pmcid"] = value
        doi = identifiers.get("doi")
        pmcid = identifiers.get("pmcid")
        publication_date = pubmed_publication_date(article)
        publication_types = [
            element_text(value)
            for value in article.findall(
                ".//Article/PublicationTypeList/PublicationType"
            )
            if element_text(value)
        ]
        is_retracted, has_correction, publication_states = publication_state_from_types(
            publication_types
        )
        correction_types = {
            collapse_ws(value.attrib.get("RefType")).casefold()
            for value in article.findall(".//CommentsCorrections")
            if collapse_ws(value.attrib.get("RefType"))
        }
        if correction_types.intersection({"retractionin", "retractedandrepublishedin"}):
            is_retracted = True
            if "retracted" not in publication_states:
                publication_states.append("retracted")
        if correction_types.intersection(
            {
                "erratumin",
                "erratumfor",
                "retractionin",
                "retractionof",
                "retractedandrepublishedin",
                "retractedandrepublishedfrom",
                "updatein",
                "updateof",
            }
        ):
            has_correction = True
        if correction_types.intersection(
            {"expressionofconcernin", "expressionofconcernfor"}
        ):
            publication_states.append("expression_of_concern")
        languages = [
            element_text(value)
            for value in article.findall(".//Article/Language")
            if element_text(value)
        ]
        oa_url = (
            f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/" if pmcid else None
        )
        canonical_url = (
            f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            if pmid
            else f"https://doi.org/{doi}"
            if doi
            else None
        )
        records.append(
            make_record(
                "pubmed",
                pmid or doi,
                query,
                rank,
                title=title,
                authors=authors,
                year=extract_year(publication_date),
                publication_date=publication_date,
                venue=element_text(article.find(".//Article/Journal/Title")),
                publication_type=", ".join(publication_types),
                language=", ".join(languages),
                abstract=" ".join(abstract_parts),
                identifiers=identifiers,
                url=canonical_url,
                open_access_url=oa_url,
                is_retracted=is_retracted,
                has_correction=has_correction,
                publication_states=publication_states,
            )
        )
    return records


def ncbi_parameters() -> dict[str, str]:
    params = {"tool": "life-sciences-literature-search"}
    email = collapse_ws(os.getenv("LITERATURE_CONTACT_EMAIL"))
    api_key = collapse_ws(os.getenv("NCBI_API_KEY"))
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    return params


def search_pubmed(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    expression = add_date_filter(query, options, "pdat")
    if options.publication_types:
        type_filter = " OR ".join(
            f"{json.dumps(publication_type)}[pt]"
            for publication_type in options.publication_types
        )
        expression = f"({expression}) AND ({type_filter})"
    search_params = {
        "db": "pubmed",
        "term": expression,
        "retmax": str(options.per_source),
        "retmode": "json",
        "sort": "relevance",
        **ncbi_parameters(),
    }
    search_url = (
        SOURCE_ENDPOINTS["pubmed"]
        + "esearch.fcgi?"
        + urllib.parse.urlencode(search_params)
    )
    data = client.get_json(search_url)
    result = data.get("esearchresult") if isinstance(data, dict) else None
    if not isinstance(result, dict):
        raise SourceFailure("invalid_response", "PubMed ESearch response is malformed")
    if result.get("ERROR") or result.get("errorlist"):
        raise SourceFailure(
            "api_error", sanitize_error(result.get("ERROR") or result.get("errorlist"))
        )
    identifiers = result.get("idlist") or []
    if not isinstance(identifiers, list):
        raise SourceFailure("invalid_response", "PubMed ESearch idlist is malformed")
    if not identifiers:
        return SearchBatch([], safe_int(result.get("count")), endpoint_only(search_url))

    if not os.getenv("NCBI_API_KEY"):
        time.sleep(0.35)
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(str(value) for value in identifiers),
        "retmode": "xml",
        **ncbi_parameters(),
    }
    fetch_url = (
        SOURCE_ENDPOINTS["pubmed"]
        + "efetch.fcgi?"
        + urllib.parse.urlencode(fetch_params)
    )
    records = parse_pubmed_xml(client.get_bytes(fetch_url), query)
    if options.open_access:
        records = [record for record in records if record.get("open_access_url")]
    return SearchBatch(
        records, safe_int(result.get("count")), SOURCE_ENDPOINTS["pubmed"]
    )


def search_arxiv(client: HttpClient, query: str, options: SearchOptions) -> SearchBatch:
    safe_query = query.replace('"', " ")
    params = {
        "search_query": f'all:"{safe_query}"',
        "start": "0",
        "max_results": str(options.per_source),
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = SOURCE_ENDPOINTS["arxiv"] + "?" + urllib.parse.urlencode(params)
    payload = client.get_bytes(url)
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as error:
        raise SourceFailure("invalid_xml", sanitize_error(error)) from error
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
        "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    }
    entries = root.findall("atom:entry", ns)
    if entries and element_text(entries[0].find("atom:title", ns)).lower() == "error":
        raise SourceFailure(
            "api_error",
            element_text(entries[0].find("atom:summary", ns)) or "arXiv error",
        )

    records: list[dict[str, Any]] = []
    for rank, entry in enumerate(entries, start=1):
        raw_id = element_text(entry.find("atom:id", ns))
        arxiv_id = raw_id.rsplit("/", 1)[-1] if raw_id else ""
        arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
        authors = [
            element_text(author.find("atom:name", ns))
            for author in entry.findall("atom:author", ns)
        ]
        alternate_url = raw_id
        pdf_url = None
        for link in entry.findall("atom:link", ns):
            rel = collapse_ws(link.attrib.get("rel"))
            link_type = collapse_ws(link.attrib.get("type"))
            href = link.attrib.get("href")
            if rel == "alternate" and href:
                alternate_url = href
            if (
                link_type == "application/pdf" or link.attrib.get("title") == "pdf"
            ) and href:
                pdf_url = href
        doi = normalize_doi(element_text(entry.find("arxiv:doi", ns)))
        journal_ref = element_text(entry.find("arxiv:journal_ref", ns))
        published = element_text(entry.find("atom:published", ns))
        records.append(
            make_record(
                "arxiv",
                arxiv_id,
                query,
                rank,
                title=element_text(entry.find("atom:title", ns)),
                authors=authors,
                year=extract_year(published),
                publication_date=published[:10] if published else None,
                venue=journal_ref or "arXiv",
                publication_type="preprint",
                abstract=element_text(entry.find("atom:summary", ns)),
                identifiers={"doi": doi, "arxiv": arxiv_id},
                url=(f"https://doi.org/{doi}" if doi else alternate_url),
                open_access_url=pdf_url,
            )
        )
    total = safe_int(element_text(root.find("opensearch:totalResults", ns)))
    return SearchBatch(records, total, endpoint_only(url))


def listify(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def search_dblp(client: HttpClient, query: str, options: SearchOptions) -> SearchBatch:
    params = {"q": query, "h": str(options.per_source), "format": "json"}
    url = SOURCE_ENDPOINTS["dblp"] + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url)
    result = data.get("result") if isinstance(data, dict) else None
    hits = result.get("hits") if isinstance(result, dict) else None
    if not isinstance(hits, dict):
        raise SourceFailure(
            "invalid_response", "DBLP response has no result.hits object"
        )
    hit_list = listify(hits.get("hit"))
    records: list[dict[str, Any]] = []
    for rank, hit in enumerate(hit_list, start=1):
        info = hit.get("info") if isinstance(hit, dict) else None
        if not isinstance(info, dict):
            continue
        authors_block = info.get("authors") or {}
        raw_authors = (
            authors_block.get("author") if isinstance(authors_block, dict) else []
        )
        authors = []
        for author in listify(raw_authors):
            if isinstance(author, dict):
                authors.append(author.get("text") or author.get("@pid") or "")
            else:
                authors.append(author)
        doi = normalize_doi(info.get("doi"))
        source_id = info.get("key") or hit.get("@id")
        ee_values = listify(info.get("ee"))
        external_url = next(
            (clean_url(value) for value in ee_values if clean_url(value)), None
        )
        open_access_url = (
            external_url if collapse_ws(info.get("access")).lower() == "open" else None
        )
        records.append(
            make_record(
                "dblp",
                source_id,
                query,
                rank,
                title=info.get("title"),
                authors=authors,
                year=info.get("year"),
                venue=info.get("venue"),
                publication_type=info.get("type"),
                identifiers={"doi": doi, "dblp": source_id},
                url=(
                    f"https://doi.org/{doi}" if doi else external_url or info.get("url")
                ),
                open_access_url=open_access_url,
            )
        )
    return SearchBatch(records, safe_int(hits.get("@total")), endpoint_only(url))


def semantic_scholar_headers() -> dict[str, str]:
    api_key = collapse_ws(
        os.getenv("SEMANTIC_SCHOLAR_API_KEY") or os.getenv("S2_API_KEY")
    )
    return {"x-api-key": api_key} if api_key else {}


def semantic_scholar_record(
    item: dict[str, Any],
    query: str,
    rank: int,
    *,
    query_family: str = "core",
    source_enrichment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    external = item.get("externalIds") or {}
    oa = item.get("openAccessPdf") or {}
    paper_id = normalize_identifier(item.get("paperId"))
    publication_types = item.get("publicationTypes") or []
    return make_record(
        "semantic-scholar",
        paper_id,
        query,
        rank,
        title=item.get("title"),
        authors=[
            author.get("name")
            for author in item.get("authors") or []
            if isinstance(author, dict)
        ],
        year=item.get("year"),
        publication_date=item.get("publicationDate"),
        venue=item.get("venue"),
        publication_type=", ".join(str(value) for value in publication_types),
        abstract=item.get("abstract"),
        identifiers={
            "doi": external.get("DOI"),
            "pmid": external.get("PubMed"),
            "arxiv": external.get("ArXiv"),
            "semantic_scholar": paper_id,
        },
        url=item.get("url"),
        open_access_url=oa.get("url") if isinstance(oa, dict) else None,
        citation_count=item.get("citationCount"),
        source_enrichment=source_enrichment,
        query_family=query_family,
    )


def search_semantic_scholar(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    params = {
        "query": query,
        "limit": str(options.per_source),
        "fields": ",".join(SEMANTIC_SCHOLAR_FIELDS),
    }
    url = SOURCE_ENDPOINTS["semantic-scholar"] + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url, headers=semantic_scholar_headers())
    if not isinstance(data, dict) or not isinstance(data.get("data"), list):
        message = data.get("message") if isinstance(data, dict) else None
        raise SourceFailure(
            "invalid_response",
            sanitize_error(message or "Semantic Scholar response is malformed"),
        )

    records: list[dict[str, Any]] = []
    for rank, item in enumerate(data["data"], start=1):
        if not isinstance(item, dict):
            continue
        records.append(semantic_scholar_record(item, query, rank))
    return SearchBatch(records, safe_int(data.get("total")), endpoint_only(url))


def semantic_scholar_seed_id(result: dict[str, Any]) -> str | None:
    identifiers = result.get("identifiers") or {}
    candidates = (
        ("semantic_scholar", ""),
        ("doi", "DOI:"),
        ("pmid", "PMID:"),
        ("arxiv", "ARXIV:"),
    )
    for name, prefix in candidates:
        value = collapse_ws(identifiers.get(name))
        if value:
            return prefix + value
    return None


def expansion_directions(mode: str) -> tuple[str, ...]:
    directions: list[str] = []
    if mode in {"citations", "both"}:
        directions.extend(("citation_forward", "citation_backward"))
    if mode in {"related", "both"}:
        directions.append("related")
    return tuple(directions)


def semantic_scholar_expansion_endpoint(direction: str) -> str:
    return (
        SEMANTIC_SCHOLAR_RECOMMENDATIONS_ENDPOINT
        if direction == "related"
        else SEMANTIC_SCHOLAR_GRAPH_ENDPOINT
    )

def fetch_semantic_scholar_expansion(
    client: HttpClient,
    seed: dict[str, Any],
    direction: str,
    limit: int,
    original_query: str,
) -> SearchBatch:
    seed_id = semantic_scholar_seed_id(seed)
    if not seed_id:
        raise SourceFailure(
            "missing_seed_identifier", "seed has no supported identifier"
        )
    encoded_id = urllib.parse.quote(seed_id, safe="")
    params = urllib.parse.urlencode(
        {"fields": ",".join(SEMANTIC_SCHOLAR_FIELDS), "limit": str(limit)}
    )
    if direction == "citation_forward":
        url = f"{SEMANTIC_SCHOLAR_GRAPH_ENDPOINT}/{encoded_id}/citations?{params}"
        item_key = "citingPaper"
        result_key = "data"
    elif direction == "citation_backward":
        url = f"{SEMANTIC_SCHOLAR_GRAPH_ENDPOINT}/{encoded_id}/references?{params}"
        item_key = "citedPaper"
        result_key = "data"
    elif direction == "related":
        url = f"{SEMANTIC_SCHOLAR_RECOMMENDATIONS_ENDPOINT}/{encoded_id}?{params}"
        item_key = None
        result_key = "recommendedPapers"
    else:
        raise SourceFailure("invalid_expansion_direction", direction)

    data = client.get_json(url, headers=semantic_scholar_headers())
    items = data.get(result_key) if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise SourceFailure(
            "invalid_response",
            f"Semantic Scholar {direction} response is malformed",
        )
    records: list[dict[str, Any]] = []
    for rank, wrapper in enumerate(items, start=1):
        item = (
            wrapper.get(item_key) if item_key and isinstance(wrapper, dict) else wrapper
        )
        if not isinstance(item, dict) or not clean_text(item.get("title")):
            continue
        records.append(
            semantic_scholar_record(
                item,
                original_query,
                rank,
                query_family=direction,
                source_enrichment={
                    "discovery": [
                        {
                            "relation": direction,
                            "seed_identifier": seed_id,
                            "seed_title": seed.get("title"),
                        }
                    ]
                },
            )
        )
    return SearchBatch(records, None, endpoint_only(url))


def run_semantic_scholar_expansion(
    seeds: list[dict[str, Any]],
    mode: str,
    per_seed: int,
    original_query: str,
    options: SearchOptions,
    timeout: float,
    retries: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    directions = expansion_directions(mode)
    resolvable = [seed for seed in seeds if semantic_scholar_seed_id(seed)]
    if not resolvable:
        return [], [
            {
                "source": EXPANSION_STATUS_SOURCE,
                "source_role": "citation_graph_expansion",
                "query": original_query,
                "query_family": "related" if mode == "related" else "citation_forward",
                "phase": "expansion",
                "status": "skipped",
                "endpoint": semantic_scholar_expansion_endpoint(
                    directions[0] if directions else "related"
                ),
                "reason": "No ranked seed had a Semantic Scholar, DOI, PMID, or arXiv identifier.",
            }
        ]

    client = HttpClient(timeout, retries)
    records: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    calls = [(seed, direction) for seed in resolvable for direction in directions]
    for index, (seed, direction) in enumerate(calls):
        seed_id = semantic_scholar_seed_id(seed)
        try:
            batch = fetch_semantic_scholar_expansion(
                client, seed, direction, per_seed, original_query
            )
            accepted = [
                record
                for record in batch.records
                if record_passes_filters(record, options)
            ]
            records.extend(accepted)
            statuses.append(
                {
                    "source": EXPANSION_STATUS_SOURCE,
                    "source_role": "citation_graph_expansion",
                    "query": original_query,
                    "query_family": direction,
                    "phase": "expansion",
                    "seed_identifier": seed_id,
                    "seed_title": seed.get("title"),
                    "status": "ok",
                    "endpoint": batch.endpoint,
                    "received": len(batch.records),
                    "accepted": len(accepted),
                    "reported_total": None,
                }
            )
        except (HttpFailure, SourceFailure) as error:
            statuses.append(
                {
                    "source": EXPANSION_STATUS_SOURCE,
                    "source_role": "citation_graph_expansion",
                    "query": original_query,
                    "query_family": direction,
                    "phase": "expansion",
                    "seed_identifier": seed_id,
                    "seed_title": seed.get("title"),
                    "status": "error",
                    "endpoint": semantic_scholar_expansion_endpoint(direction),
                    "error": {
                        "code": error.code,
                        "message": sanitize_error(error.message),
                        "http_status": error.status,
                        "retryable": error.retryable,
                    },
                }
            )
        except Exception as error:  # Defensive boundary around optional expansion.
            statuses.append(
                {
                    "source": EXPANSION_STATUS_SOURCE,
                    "source_role": "citation_graph_expansion",
                    "query": original_query,
                    "query_family": direction,
                    "phase": "expansion",
                    "seed_identifier": seed_id,
                    "seed_title": seed.get("title"),
                    "status": "error",
                    "endpoint": semantic_scholar_expansion_endpoint(direction),
                    "error": {
                        "code": "unexpected_error",
                        "message": sanitize_error(error),
                        "http_status": None,
                        "retryable": False,
                    },
                }
            )
        if index + 1 < len(calls):
            time.sleep(0.4 if semantic_scholar_headers() else 1.0)
    return records, statuses


def open_citations_headers() -> dict[str, str]:
    token = collapse_ws(os.getenv("OPENCITATIONS_ACCESS_TOKEN"))
    return {"authorization": token} if token else {}


def fetch_open_citations_expansion(
    client: HttpClient,
    seed: dict[str, Any],
    direction: str,
    limit: int,
    original_query: str,
    options: SearchOptions,
) -> SearchBatch:
    doi = normalize_doi((seed.get("identifiers") or {}).get("doi"))
    if not doi:
        raise SourceFailure("missing_seed_identifier", "seed has no DOI")
    if direction == "citation_forward":
        relation = "citations"
        identifier_field = "citing"
    elif direction == "citation_backward":
        relation = "references"
        identifier_field = "cited"
    else:
        raise SourceFailure("invalid_expansion_direction", direction)
    url = (
        OPENCITATIONS_ENDPOINT + "/" + relation + "/" + urllib.parse.quote(doi, safe="")
    )
    data = client.get_json(url, headers=open_citations_headers())
    if not isinstance(data, list):
        raise SourceFailure("invalid_response", "OpenCitations response is malformed")
    dois = unique_clean(
        normalized
        for normalized in (
            normalize_doi(item.get(identifier_field))
            for item in data[:limit]
            if isinstance(item, dict)
        )
        if normalized
    )
    batch = hydrate_publication_identifiers(
        client,
        "open-citations",
        original_query,
        options,
        {"pmid": [], "pmcid": [], "doi": dois},
        endpoint_only(url),
        origin_enrichment={
            "discovery": [
                {
                    "relation": direction,
                    "seed_identifier": "DOI:" + doi,
                    "seed_title": seed.get("title"),
                }
            ]
        },
    )
    for record in batch.records:
        record["query_family"] = direction
    batch.reported_total = len(data)
    return batch


def run_open_citations_expansion(
    seeds: list[dict[str, Any]],
    mode: str,
    per_seed: int,
    original_query: str,
    options: SearchOptions,
    timeout: float,
    retries: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    directions = tuple(
        direction
        for direction in expansion_directions(mode)
        if direction in {"citation_forward", "citation_backward"}
    )
    resolvable = [
        seed
        for seed in seeds
        if normalize_doi((seed.get("identifiers") or {}).get("doi"))
    ]
    if not directions:
        return [], []
    if not resolvable:
        return [], [
            {
                "source": OPENCITATIONS_STATUS_SOURCE,
                "source_role": SOURCE_ROLES["open-citations"],
                "query": original_query,
                "query_family": directions[0],
                "phase": "expansion",
                "status": "skipped",
                "endpoint": OPENCITATIONS_ENDPOINT,
                "reason": "No ranked seed had a DOI.",
            }
        ]
    client = HttpClient(timeout, retries)
    records: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    for seed in resolvable:
        for direction in directions:
            doi = normalize_doi((seed.get("identifiers") or {}).get("doi"))
            try:
                batch = fetch_open_citations_expansion(
                    client,
                    seed,
                    direction,
                    per_seed,
                    original_query,
                    options,
                )
                accepted = [
                    record
                    for record in batch.records
                    if record_passes_filters(record, options)
                ]
                records.extend(accepted)
                statuses.append(
                    {
                        "source": OPENCITATIONS_STATUS_SOURCE,
                        "source_role": SOURCE_ROLES["open-citations"],
                        "query": original_query,
                        "query_family": direction,
                        "phase": "expansion",
                        "seed_identifier": "DOI:" + (doi or ""),
                        "seed_title": seed.get("title"),
                        "status": "ok",
                        "endpoint": batch.endpoint,
                        "received": len(batch.records),
                        "accepted": len(accepted),
                        "reported_total": batch.reported_total,
                    }
                )
            except (HttpFailure, SourceFailure) as error:
                statuses.append(
                    {
                        "source": OPENCITATIONS_STATUS_SOURCE,
                        "source_role": SOURCE_ROLES["open-citations"],
                        "query": original_query,
                        "query_family": direction,
                        "phase": "expansion",
                        "seed_identifier": "DOI:" + (doi or ""),
                        "seed_title": seed.get("title"),
                        "status": "error",
                        "endpoint": OPENCITATIONS_ENDPOINT,
                        "error": {
                            "code": error.code,
                            "message": sanitize_error(error.message),
                            "http_status": error.status,
                            "retryable": error.retryable,
                        },
                    }
                )
    return records, statuses


def unpaywall_record(item: dict[str, Any], query: str, rank: int) -> dict[str, Any]:
    best = item.get("best_oa_location") or {}
    authors = [
        " ".join(
            part
            for part in (author.get("given"), author.get("family"))
            if collapse_ws(part)
        )
        for author in item.get("z_authors") or []
        if isinstance(author, dict)
    ]
    oa_url = (
        best.get("url_for_pdf") or best.get("url_for_landing_page") or best.get("url")
        if isinstance(best, dict)
        else None
    )
    doi = normalize_doi(item.get("doi"))
    return make_record(
        "unpaywall",
        doi,
        query,
        rank,
        title=item.get("title"),
        authors=authors,
        year=item.get("year"),
        publication_date=item.get("published_date"),
        venue=item.get("journal_name"),
        publication_type=item.get("genre"),
        identifiers={"doi": doi},
        url=f"https://doi.org/{doi}" if doi else item.get("doi_url"),
        open_access_url=oa_url if item.get("is_oa") else None,
        source_enrichment={
            "oa_status": item.get("oa_status"),
            "best_oa_host_type": best.get("host_type")
            if isinstance(best, dict)
            else None,
            "license": best.get("license") if isinstance(best, dict) else None,
        },
    )


def run_unpaywall_enrichment(
    seeds: list[dict[str, Any]],
    original_query: str,
    options: SearchOptions,
    timeout: float,
    retries: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    email = collapse_ws(os.getenv("LITERATURE_CONTACT_EMAIL"))
    if not email:
        return [], [
            {
                "source": UNPAYWALL_STATUS_SOURCE,
                "source_role": SOURCE_ROLES["unpaywall"],
                "query": original_query,
                "query_family": "core",
                "phase": "enrichment",
                "status": "skipped",
                "endpoint": UNPAYWALL_ENDPOINT,
                "reason": "LITERATURE_CONTACT_EMAIL is required by Unpaywall.",
            }
        ]
    dois = unique_clean(
        doi
        for doi in (
            normalize_doi((seed.get("identifiers") or {}).get("doi")) for seed in seeds
        )
        if doi
    )[: min(10, options.per_source)]
    if not dois:
        return [], [
            {
                "source": UNPAYWALL_STATUS_SOURCE,
                "source_role": SOURCE_ROLES["unpaywall"],
                "query": original_query,
                "query_family": "core",
                "phase": "enrichment",
                "status": "skipped",
                "endpoint": UNPAYWALL_ENDPOINT,
                "reason": "No ranked seed had a DOI.",
            }
        ]
    client = HttpClient(timeout, retries)
    records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for doi in dois:
        url = (
            UNPAYWALL_ENDPOINT
            + "/"
            + urllib.parse.quote(doi, safe="")
            + "?"
            + urllib.parse.urlencode({"email": email})
        )
        try:
            data = client.get_json(url)
            if isinstance(data, dict) and clean_text(data.get("title")):
                records.append(unpaywall_record(data, original_query, len(records) + 1))
        except HttpFailure as error:
            failures.append(
                {
                    "doi": doi,
                    "code": error.code,
                    "http_status": error.status,
                    "retryable": error.retryable,
                }
            )
    status: dict[str, Any] = {
        "source": UNPAYWALL_STATUS_SOURCE,
        "source_role": SOURCE_ROLES["unpaywall"],
        "query": original_query,
        "query_family": "core",
        "phase": "enrichment",
        "status": "ok" if records else "error",
        "endpoint": UNPAYWALL_ENDPOINT,
        "received": len(records),
        "accepted": len(records),
        "reported_total": len(dois),
    }
    if failures:
        status["partial_failures"] = failures
    if not records:
        status["error"] = {
            "code": "all_requests_failed",
            "message": "Unpaywall returned no usable metadata for the selected DOI seeds.",
            "http_status": None,
            "retryable": any(value.get("retryable") for value in failures),
        }
    return records, [status]


def require_graphql_data(payload: Any, source: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SourceFailure("invalid_response", f"{source} response is not an object")
    if payload.get("errors"):
        raise SourceFailure("api_error", sanitize_error(payload["errors"]))
    data = payload.get("data")
    if not isinstance(data, dict):
        raise SourceFailure("invalid_response", f"{source} data is missing")
    return data


def search_pubtator3(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    params = {"text": query, "page": "1"}
    url = SOURCE_ENDPOINTS["pubtator3"] + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url)
    identifiers = extract_publication_identifiers(data)
    batch = hydrate_publication_identifiers(
        client,
        "pubtator3",
        query,
        options,
        identifiers,
        endpoint_only(url),
        origin_enrichment={"entity_query": query},
    )
    batch.reported_total = response_total(data)
    return batch


def litvar_variant_ids(payload: Any) -> list[str]:
    values = recursive_key_values(
        payload, ("variantId", "variant_id", "litvarId", "litvar_id")
    )
    containers: list[Any] = []
    if isinstance(payload, list):
        containers = payload
    elif isinstance(payload, dict):
        for key in ("results", "result", "suggestions", "variants"):
            if isinstance(payload.get(key), list):
                containers.extend(payload[key])
    for item in containers:
        if isinstance(item, dict):
            candidate = collapse_ws(item.get("id"))
            if candidate and re.search(r"(?:rs\d+|litvar|variant|@)", candidate, re.I):
                values.append(candidate)
    return unique_clean(values)[:3]


def search_litvar2(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    terms = variant_terms(query, options)
    if not terms:
        raise SourceSkipped(
            "not_applicable", "LitVar2 requires an rsID or HGVS-like variant"
        )
    identifiers = {"pmid": [], "pmcid": [], "doi": []}
    variant_ids: list[str] = []
    endpoints: list[str] = []
    for term in terms[:3]:
        if RSID_RE.fullmatch(term):
            url = SOURCE_ENDPOINTS["litvar2"] + "sensor/" + urllib.parse.quote(term)
        else:
            params = urllib.parse.urlencode({"query": term})
            url = SOURCE_ENDPOINTS["litvar2"] + "variant/autocomplete/?" + params
        data = client.get_json(url)
        endpoints.append(endpoint_only(url))
        found = extract_publication_identifiers(data)
        for name in identifiers:
            identifiers[name].extend(found[name])
        variant_ids.extend(litvar_variant_ids(data))

    for variant_id in unique_clean(variant_ids)[:3]:
        url = (
            SOURCE_ENDPOINTS["litvar2"]
            + "variant/get/"
            + urllib.parse.quote(variant_id, safe="")
            + "/publications"
        )
        data = client.get_json(url)
        endpoints.append(endpoint_only(url))
        found = extract_publication_identifiers(data)
        for name in identifiers:
            identifiers[name].extend(found[name])
    identifiers = {name: unique_clean(values) for name, values in identifiers.items()}
    endpoint = endpoints[0] if endpoints else SOURCE_ENDPOINTS["litvar2"]
    return hydrate_publication_identifiers(
        client,
        "litvar2",
        query,
        options,
        identifiers,
        endpoint,
        origin_enrichment={
            "matched_variants": terms,
            "resolved_variant_ids": unique_clean(variant_ids),
        },
    )


def search_clinvar(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    terms = variant_terms(query, options)
    if not terms:
        raise SourceSkipped(
            "not_applicable", "ClinVar publication seeding requires a variant"
        )
    search_params = ncbi_query_params(
        {
            "db": "clinvar",
            "term": " OR ".join(f'"{term}"[All Fields]' for term in terms[:3]),
            "retmode": "json",
            "retmax": str(options.per_source),
        }
    )
    search_url = (
        SOURCE_ENDPOINTS["clinvar"]
        + "esearch.fcgi?"
        + urllib.parse.urlencode(search_params)
    )
    search_data = client.get_json(search_url)
    esearch = (
        search_data.get("esearchresult") if isinstance(search_data, dict) else None
    )
    clinvar_ids = esearch.get("idlist") if isinstance(esearch, dict) else None
    if not isinstance(clinvar_ids, list) or not clinvar_ids:
        return SearchBatch(
            [], safe_int((esearch or {}).get("count")), endpoint_only(search_url)
        )
    link_params = ncbi_query_params(
        {
            "dbfrom": "clinvar",
            "db": "pubmed",
            "id": clinvar_ids[: options.per_source],
            "retmode": "json",
        }
    )
    link_url = (
        SOURCE_ENDPOINTS["clinvar"]
        + "elink.fcgi?"
        + urllib.parse.urlencode(link_params, doseq=True)
    )
    link_data = client.get_json(link_url)
    pmids: list[str] = []
    linksets = link_data.get("linksets") if isinstance(link_data, dict) else None
    for linkset in linksets if isinstance(linksets, list) else []:
        for database in (
            linkset.get("linksetdbs") or [] if isinstance(linkset, dict) else []
        ):
            if (
                isinstance(database, dict)
                and collapse_ws(database.get("dbto")).lower() == "pubmed"
            ):
                pmids.extend(
                    collapse_ws(value) for value in database.get("links") or []
                )
    batch = hydrate_publication_identifiers(
        client,
        "clinvar",
        query,
        options,
        {"pmid": unique_clean(pmids), "pmcid": [], "doi": []},
        endpoint_only(link_url),
        origin_enrichment={
            "matched_variants": terms,
            "clinvar_record_count": len(clinvar_ids),
            "citation_coverage_note": "ClinVar citations are submission-driven and may be incomplete.",
        },
    )
    batch.reported_total = safe_int((esearch or {}).get("count"))
    return batch


def search_clingen(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    genes = gene_terms(query, options)
    variants = variant_terms(query, options)
    if not genes and not variants:
        raise SourceSkipped(
            "not_applicable", "ClinGen publication seeding requires a gene or variant"
        )
    column = "gene" if genes else "hgvs"
    value = genes[0] if genes else variants[0]
    params = {
        "columns": column,
        "values": value,
        "matchTypes": "exact" if genes else "contains",
        "pgSize": str(options.per_source),
        "pg": "1",
    }
    url = SOURCE_ENDPOINTS["clingen"] + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url)
    identifiers = extract_publication_identifiers(data)
    batch = hydrate_publication_identifiers(
        client,
        "clingen",
        query,
        options,
        identifiers,
        endpoint_only(url),
        origin_enrichment={"matched_field": column, "matched_value": value},
    )
    batch.reported_total = response_total(data)
    return batch


def civic_authors(value: Any) -> list[str]:
    return [
        collapse_ws(author)
        for author in re.split(r"\s*(?:;|,\s+(?=[A-Z][a-z]+\b))\s*", collapse_ws(value))
        if collapse_ws(author)
    ]


def search_civic(client: HttpClient, query: str, options: SearchOptions) -> SearchBatch:
    genes = gene_terms(query, options)
    variants = variant_terms(query, options)
    if (
        not genes
        and not variants
        and not re.search(r"\b(?:cancer|tumou?r|oncolog)\w*\b", query, re.I)
    ):
        raise SourceSkipped(
            "not_applicable",
            "CIViC publication seeding requires a gene, variant, or cancer query",
        )
    search_term = " ".join(unique_clean([*genes[:1], *variants[:1]])) or query
    graphql = """
      query($q:String!,$n:Int!){
        evidenceItems(molecularProfileName:$q,status:ACCEPTED,first:$n){
          totalCount
          nodes{
            id status evidenceLevel evidenceType evidenceDirection significance
            disease{name}
            molecularProfile{name}
            source{sourceType citationId title journal publicationYear authorString pmcId link openAccess retracted}
          }
        }
      }
    """
    data = require_graphql_data(
        client.post_json(
            SOURCE_ENDPOINTS["civic"],
            {
                "query": graphql,
                "variables": {"q": search_term, "n": options.per_source},
            },
        ),
        "CIViC",
    )
    evidence = data.get("evidenceItems") or {}
    nodes = evidence.get("nodes") if isinstance(evidence, dict) else None
    if not isinstance(nodes, list):
        raise SourceFailure("invalid_response", "CIViC evidenceItems are malformed")
    records: list[dict[str, Any]] = []
    for rank, node in enumerate(nodes, start=1):
        if not isinstance(node, dict) or not isinstance(node.get("source"), dict):
            continue
        source = node["source"]
        source_type = collapse_ws(source.get("sourceType")).upper()
        citation_id = collapse_ws(source.get("citationId"))
        pmid = (
            citation_id if source_type == "PUBMED" and citation_id.isdigit() else None
        )
        doi = normalize_doi(citation_id)
        title = source.get("title")
        if not clean_text(title):
            continue
        disease = node.get("disease") or {}
        profile = node.get("molecularProfile") or {}
        records.append(
            make_record(
                "civic",
                node.get("id") or citation_id,
                query,
                rank,
                title=title,
                authors=civic_authors(source.get("authorString")),
                year=source.get("publicationYear"),
                venue=source.get("journal"),
                publication_type=source_type,
                identifiers={"pmid": pmid, "pmcid": source.get("pmcId"), "doi": doi},
                url=source.get("link"),
                open_access_url=source.get("link")
                if source.get("openAccess")
                else None,
                is_retracted=source.get("retracted"),
                source_enrichment={
                    "evidence_item_id": node.get("id"),
                    "evidence_level": node.get("evidenceLevel"),
                    "evidence_type": node.get("evidenceType"),
                    "evidence_direction": node.get("evidenceDirection"),
                    "significance": node.get("significance"),
                    "disease": disease.get("name")
                    if isinstance(disease, dict)
                    else None,
                    "molecular_profile": profile.get("name")
                    if isinstance(profile, dict)
                    else None,
                },
            )
        )
    return SearchBatch(
        records,
        safe_int(evidence.get("totalCount")) if isinstance(evidence, dict) else None,
        SOURCE_ENDPOINTS["civic"],
    )


def search_open_targets(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    search_graphql = """
      query($q:String!){
        search(queryString:$q,entityNames:["target","disease","drug"],page:{index:0,size:5}){
          total hits{id entity name description score}
        }
      }
    """
    search_data = require_graphql_data(
        client.post_json(
            SOURCE_ENDPOINTS["open-targets"],
            {"query": search_graphql, "variables": {"q": query}},
        ),
        "Open Targets",
    )
    search_result = search_data.get("search") or {}
    hits = search_result.get("hits") if isinstance(search_result, dict) else None
    if not isinstance(hits, list):
        raise SourceFailure(
            "invalid_response", "Open Targets search hits are malformed"
        )
    identifiers = {"pmid": [], "pmcid": [], "doi": []}
    entities: list[dict[str, Any]] = []
    entity_config = {
        "target": ("target", "ensemblId", "approvedSymbol"),
        "disease": ("disease", "efoId", "name"),
        "drug": ("drug", "chemblId", "name"),
    }
    for hit in hits[:3]:
        if not isinstance(hit, dict):
            continue
        entity_type = collapse_ws(hit.get("entity")).lower()
        if entity_type not in entity_config:
            continue
        field, argument, label_field = entity_config[entity_type]
        entity_id = collapse_ws(hit.get("id"))
        if not entity_id:
            continue
        entity_graphql = f"""
          query($id:String!,$start:Int,$end:Int){{
            {field}({argument}:$id){{
              id {label_field}
              literatureOcurrences(startYear:$start,endYear:$end){{
                count rows{{pmid pmcid publicationDate}}
              }}
            }}
          }}
        """
        entity_data = require_graphql_data(
            client.post_json(
                SOURCE_ENDPOINTS["open-targets"],
                {
                    "query": entity_graphql,
                    "variables": {
                        "id": entity_id,
                        "start": options.year_from,
                        "end": options.year_to,
                    },
                },
            ),
            "Open Targets",
        )
        entity = entity_data.get(field)
        if not isinstance(entity, dict):
            continue
        occurrences = entity.get("literatureOcurrences") or {}
        rows = occurrences.get("rows") if isinstance(occurrences, dict) else None
        found = extract_publication_identifiers(rows or [])
        for name in identifiers:
            identifiers[name].extend(found[name])
        entities.append(
            {
                "type": entity_type,
                "id": entity_id,
                "name": hit.get("name") or entity.get(label_field),
                "score": hit.get("score"),
                "literature_count": safe_int(occurrences.get("count"))
                if isinstance(occurrences, dict)
                else None,
            }
        )
        if len(unique_clean(identifiers["pmid"])) >= options.per_source:
            break
    identifiers = {name: unique_clean(values) for name, values in identifiers.items()}
    batch = hydrate_publication_identifiers(
        client,
        "open-targets",
        query,
        options,
        identifiers,
        SOURCE_ENDPOINTS["open-targets"],
        origin_enrichment={"matched_entities": entities},
    )
    batch.reported_total = sum(
        entity.get("literature_count") or 0 for entity in entities
    )
    return batch


def gwas_embedded(payload: Any, key: str) -> list[dict[str, Any]]:
    embedded = payload.get("_embedded") if isinstance(payload, dict) else None
    values = embedded.get(key) if isinstance(embedded, dict) else None
    return [value for value in values or [] if isinstance(value, dict)]


def search_gwas_catalog(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    if not gwas_query_applicable(query, options):
        raise SourceSkipped(
            "not_applicable",
            "GWAS Catalog requires an rsID, gene, trait, or association intent",
        )
    params: dict[str, Any] = {"size": str(options.per_source)}
    path = "studies"
    rsids = unique_clean(match.group(0) for match in RSID_RE.finditer(query))
    genes = gene_terms(query, options)
    if rsids:
        path = "associations"
        params["rs_id"] = rsids[0]
    elif genes:
        params["mapped_gene"] = genes[0]
        params["extended_geneset"] = "false"
    else:
        diseases = options.diseases or options.concept_diseases
        trait = diseases[0] if diseases else query
        params["disease_trait"] = trait
    url = SOURCE_ENDPOINTS["gwas-catalog"] + path + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url)
    identifiers = extract_publication_identifiers(data)
    studies = gwas_embedded(data, "studies")
    associations = gwas_embedded(data, "associations")
    enrichment = {
        "query_path": path,
        "study_accessions": unique_clean(
            item.get("accession_id") for item in [*studies, *associations]
        ),
        "traits": unique_clean(
            item.get("disease_trait") for item in [*studies, *associations]
        ),
    }
    batch = hydrate_publication_identifiers(
        client,
        "gwas-catalog",
        query,
        options,
        identifiers,
        endpoint_only(url),
        origin_enrichment=enrichment,
    )
    page = data.get("page") if isinstance(data, dict) else None
    batch.reported_total = safe_int((page or {}).get("totalElements"))
    return batch


def search_clinical_trials(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    if not trial_query_applicable(query, options):
        raise SourceSkipped(
            "not_applicable",
            "ClinicalTrials.gov publication seeding requires trial or intervention intent",
        )
    params = {
        "query.term": query,
        "pageSize": str(min(options.per_source, 100)),
        "format": "json",
    }
    url = SOURCE_ENDPOINTS["clinicaltrials"] + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url)
    studies = data.get("studies") if isinstance(data, dict) else None
    if not isinstance(studies, list):
        raise SourceFailure(
            "invalid_response", "ClinicalTrials.gov studies are malformed"
        )
    identifiers = extract_publication_identifiers(studies)
    nct_ids: list[str] = []
    for study in studies:
        protocol = study.get("protocolSection") if isinstance(study, dict) else None
        identification = (
            protocol.get("identificationModule") if isinstance(protocol, dict) else None
        )
        if isinstance(identification, dict):
            nct_ids.append(collapse_ws(identification.get("nctId")))
    batch = hydrate_publication_identifiers(
        client,
        "clinicaltrials",
        query,
        options,
        identifiers,
        endpoint_only(url),
        origin_enrichment={"linked_trials": unique_clean(nct_ids)},
    )
    batch.reported_total = safe_int(data.get("totalCount"))
    return batch


def search_reactome(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    if not pathway_query_applicable(query, options):
        raise SourceSkipped(
            "not_applicable",
            "Reactome publication seeding requires a gene or pathway intent",
        )
    search_url = (
        SOURCE_ENDPOINTS["reactome"]
        + "search/query?"
        + urllib.parse.urlencode(
            {"query": query, "species": "Homo sapiens", "cluster": "true"}
        )
    )
    data = client.get_json(search_url)
    entries: list[dict[str, Any]] = []
    groups = data.get("results") if isinstance(data, dict) else None
    if groups is None and isinstance(data, list):
        groups = data
    for group in groups or []:
        if not isinstance(group, dict):
            continue
        candidates = group.get("entries") or group.get("results") or []
        if isinstance(candidates, list):
            entries.extend(item for item in candidates if isinstance(item, dict))
        elif group.get("stId") or group.get("dbId"):
            entries.append(group)
    identifiers = {"pmid": [], "pmcid": [], "doi": []}
    pathways: list[dict[str, Any]] = []
    for entry in entries[:5]:
        stable_id = collapse_ws(entry.get("stId") or entry.get("dbId"))
        if not stable_id:
            continue
        detail_url = (
            SOURCE_ENDPOINTS["reactome"] + "data/query/" + urllib.parse.quote(stable_id)
        )
        detail = client.get_json(detail_url)
        found = extract_publication_identifiers(detail)
        for name in identifiers:
            identifiers[name].extend(found[name])
        pathways.append(
            {
                "id": stable_id,
                "name": entry.get("name")
                or (detail.get("displayName") if isinstance(detail, dict) else None),
                "type": entry.get("type")
                or (detail.get("schemaClass") if isinstance(detail, dict) else None),
            }
        )
    identifiers = {name: unique_clean(values) for name, values in identifiers.items()}
    return hydrate_publication_identifiers(
        client,
        "reactome",
        query,
        options,
        identifiers,
        endpoint_only(search_url),
        origin_enrichment={"matched_pathways": pathways},
    )


def uniprot_reference_authors(citation: dict[str, Any]) -> list[str]:
    authors: list[str] = []
    for author in citation.get("authors") or []:
        if isinstance(author, dict):
            authors.append(collapse_ws(author.get("name")))
        else:
            authors.append(collapse_ws(author))
    return unique_clean(authors)


def search_uniprot(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    genes = gene_terms(query, options)
    if not genes:
        raise SourceSkipped(
            "not_applicable", "UniProt publication seeding requires a gene symbol"
        )
    expression = f"(gene_exact:{genes[0]}) AND (organism_id:9606) AND (reviewed:true)"
    params = {"query": expression, "format": "json", "size": "3"}
    url = SOURCE_ENDPOINTS["uniprot"] + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url)
    entries = data.get("results") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise SourceFailure("invalid_response", "UniProt results are malformed")
    records: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        accession = collapse_ws(entry.get("primaryAccession"))
        protein = entry.get("proteinDescription") or {}
        recommended = (
            protein.get("recommendedName") if isinstance(protein, dict) else None
        )
        protein_name = (
            ((recommended or {}).get("fullName") or {}).get("value")
            if isinstance(recommended, dict)
            else None
        )
        for reference in entry.get("references") or []:
            citation = (
                reference.get("citation") if isinstance(reference, dict) else None
            )
            if not isinstance(citation, dict) or not clean_text(citation.get("title")):
                continue
            identifiers: dict[str, Any] = {}
            for cross_reference in citation.get("citationCrossReferences") or []:
                if not isinstance(cross_reference, dict):
                    continue
                database = collapse_ws(cross_reference.get("database")).lower()
                if database == "pubmed":
                    identifiers["pmid"] = cross_reference.get("id")
                elif database == "doi":
                    identifiers["doi"] = cross_reference.get("id")
            records.append(
                make_record(
                    "uniprot",
                    citation.get("id")
                    or identifiers.get("pmid")
                    or identifiers.get("doi"),
                    query,
                    len(records) + 1,
                    title=citation.get("title"),
                    authors=uniprot_reference_authors(citation),
                    year=citation.get("publicationDate"),
                    publication_date=citation.get("publicationDate"),
                    venue=citation.get("journal"),
                    publication_type=citation.get("citationType"),
                    identifiers=identifiers,
                    url=(
                        f"https://pubmed.ncbi.nlm.nih.gov/{identifiers['pmid']}/"
                        if identifiers.get("pmid")
                        else f"https://doi.org/{normalize_doi(identifiers.get('doi'))}"
                        if normalize_doi(identifiers.get("doi"))
                        else None
                    ),
                    source_enrichment={
                        "uniprot_accession": accession,
                        "protein_name": protein_name,
                    },
                )
            )
            if len(records) >= options.per_source:
                break
        if len(records) >= options.per_source:
            break
    return SearchBatch(records, len(records), endpoint_only(url))


def datacite_text(value: Any) -> str:
    if isinstance(value, dict):
        return clean_text(
            value.get("title") or value.get("description") or value.get("name")
        )
    return clean_text(value)


def search_datacite(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    params = {"query": query, "page[size]": str(options.per_source)}
    url = SOURCE_ENDPOINTS["datacite"] + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url, headers={"Accept": "application/vnd.api+json"})
    items = data.get("data") if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise SourceFailure("invalid_response", "DataCite data is malformed")
    allowed_types = {
        "book",
        "bookchapter",
        "conferencepaper",
        "dissertation",
        "journalarticle",
        "peerreview",
        "preprint",
        "report",
        "text",
        "workingpaper",
    }
    records: list[dict[str, Any]] = []
    for item in items:
        attributes = item.get("attributes") if isinstance(item, dict) else None
        if not isinstance(attributes, dict):
            continue
        types = attributes.get("types") or {}
        resource_type = collapse_ws(
            types.get("resourceTypeGeneral") or types.get("citeproc")
            if isinstance(types, dict)
            else None
        )
        if (
            resource_type
            and normalize_metadata_term(resource_type) not in allowed_types
        ):
            continue
        titles = attributes.get("titles") or []
        title = next(
            (datacite_text(value) for value in titles if datacite_text(value)), ""
        )
        descriptions = attributes.get("descriptions") or []
        abstract = next(
            (
                datacite_text(value)
                for value in descriptions
                if not isinstance(value, dict)
                or collapse_ws(value.get("descriptionType")).lower() == "abstract"
            ),
            "",
        )
        creators = attributes.get("creators") or []
        authors = [
            creator.get("name")
            or " ".join(
                part
                for part in (creator.get("givenName"), creator.get("familyName"))
                if collapse_ws(part)
            )
            for creator in creators
            if isinstance(creator, dict)
        ]
        doi = normalize_doi(attributes.get("doi") or item.get("id"))
        records.append(
            make_record(
                "datacite",
                doi or item.get("id"),
                query,
                len(records) + 1,
                title=title,
                authors=authors,
                year=attributes.get("publicationYear"),
                publication_date=attributes.get("published")
                or attributes.get("created"),
                venue=attributes.get("publisher") or attributes.get("container"),
                publication_type=resource_type,
                language=attributes.get("language"),
                abstract=abstract,
                identifiers={"doi": doi},
                url=f"https://doi.org/{doi}" if doi else attributes.get("url"),
                source_enrichment={"resource_type": resource_type},
            )
        )
    meta = data.get("meta") if isinstance(data, dict) else None
    return SearchBatch(
        records,
        safe_int((meta or {}).get("total")),
        endpoint_only(url),
    )


def search_doaj(client: HttpClient, query: str, options: SearchOptions) -> SearchBatch:
    url = (
        SOURCE_ENDPOINTS["doaj"]
        + urllib.parse.quote(query, safe="")
        + "?"
        + urllib.parse.urlencode({"pageSize": str(options.per_source)})
    )
    data = client.get_json(url)
    items = data.get("results") if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise SourceFailure("invalid_response", "DOAJ results are malformed")
    records: list[dict[str, Any]] = []
    for item in items:
        bibjson = item.get("bibjson") if isinstance(item, dict) else None
        if not isinstance(bibjson, dict):
            continue
        identifiers: dict[str, Any] = {}
        for identifier in bibjson.get("identifier") or []:
            if not isinstance(identifier, dict):
                continue
            kind = collapse_ws(identifier.get("type")).lower()
            if kind == "doi":
                identifiers["doi"] = identifier.get("id")
            elif kind == "pmid":
                identifiers["pmid"] = identifier.get("id")
        links = bibjson.get("link") or []
        fulltext = next(
            (
                clean_url(link.get("url"))
                for link in links
                if isinstance(link, dict)
                and collapse_ws(link.get("type")).lower() == "fulltext"
                and clean_url(link.get("url"))
            ),
            None,
        )
        journal = bibjson.get("journal") or {}
        records.append(
            make_record(
                "doaj",
                item.get("id") or identifiers.get("doi"),
                query,
                len(records) + 1,
                title=bibjson.get("title"),
                authors=[
                    author.get("name")
                    for author in bibjson.get("author") or []
                    if isinstance(author, dict)
                ],
                year=bibjson.get("year"),
                publication_date=date_from_parts(
                    (bibjson.get("year"), bibjson.get("month"))
                ),
                venue=journal.get("title") if isinstance(journal, dict) else None,
                publication_type="journal article",
                language=bibjson.get("language"),
                abstract=bibjson.get("abstract"),
                identifiers=identifiers,
                url=fulltext
                or (
                    f"https://doi.org/{normalize_doi(identifiers.get('doi'))}"
                    if normalize_doi(identifiers.get("doi"))
                    else None
                ),
                open_access_url=fulltext,
            )
        )
    return SearchBatch(records, safe_int(data.get("total")), endpoint_only(url))

def openaire_values(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def openaire_text(value: Any) -> str:
    if isinstance(value, dict):
        return clean_text(value.get("$") or value.get("value") or value.get("name"))
    return clean_text(value)


def search_openaire(
    client: HttpClient, query: str, options: SearchOptions
) -> SearchBatch:
    params = {"format": "json", "keywords": query, "size": str(options.per_source)}
    url = SOURCE_ENDPOINTS["openaire"] + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url)
    response = data.get("response") if isinstance(data, dict) else None
    results = response.get("results") if isinstance(response, dict) else None
    items = results.get("result") if isinstance(results, dict) else None
    items = openaire_values(items)
    records: list[dict[str, Any]] = []
    for wrapper in items:
        metadata = wrapper.get("metadata") if isinstance(wrapper, dict) else None
        entity = metadata.get("oaf:entity") if isinstance(metadata, dict) else None
        result = entity.get("oaf:result") if isinstance(entity, dict) else None
        if not isinstance(result, dict):
            continue
        title = next(
            (
                openaire_text(value)
                for value in openaire_values(result.get("title"))
                if openaire_text(value)
            ),
            "",
        )
        authors = [
            openaire_text(value)
            for value in openaire_values(result.get("creator"))
            if openaire_text(value)
        ]
        identifiers: dict[str, Any] = {}
        for pid in openaire_values(result.get("pid")):
            if not isinstance(pid, dict):
                continue
            kind = collapse_ws(pid.get("@classid")).lower()
            value = pid.get("$")
            if kind == "doi":
                identifiers["doi"] = value
            elif kind in {"pmid", "pubmed"}:
                identifiers["pmid"] = value
            elif kind in {"pmc", "pmcid"}:
                identifiers["pmcid"] = value
        descriptions = [
            openaire_text(value)
            for value in openaire_values(result.get("description"))
            if openaire_text(value)
        ]
        children = result.get("children") or {}
        instances = openaire_values(
            children.get("instance") if isinstance(children, dict) else None
        )
        urls: list[str] = []
        for instance in instances:
            resources = (
                instance.get("webresource") if isinstance(instance, dict) else None
            )
            for resource in openaire_values(resources):
                candidate = (
                    resource.get("url") if isinstance(resource, dict) else resource
                )
                if isinstance(candidate, dict):
                    candidate = candidate.get("$")
                cleaned = clean_url(candidate)
                if cleaned:
                    urls.append(cleaned)
        access_right = openaire_text(result.get("bestaccessright"))
        records.append(
            make_record(
                "openaire",
                identifiers.get("doi")
                or identifiers.get("pmid")
                or (urls[0] if urls else title),
                query,
                len(records) + 1,
                title=title,
                authors=authors,
                year=result.get("dateofacceptance"),
                publication_date=openaire_text(result.get("dateofacceptance")),
                venue=openaire_text(result.get("journal") or result.get("publisher")),
                publication_type=openaire_text(result.get("resulttype")),
                language=openaire_text(result.get("language")),
                abstract=max(descriptions, key=len, default=""),
                identifiers=identifiers,
                url=urls[0] if urls else None,
                open_access_url=urls[0]
                if urls and "open" in access_right.casefold()
                else None,
                source_enrichment={"access_right": access_right},
            )
        )
    header = response.get("header") if isinstance(response, dict) else None
    return SearchBatch(
        records,
        safe_int(openaire_text((header or {}).get("total"))),
        endpoint_only(url),
    )


def search_core(client: HttpClient, query: str, options: SearchOptions) -> SearchBatch:
    api_key = collapse_ws(os.getenv("CORE_API_KEY"))
    if not api_key:
        raise SourceSkipped(
            "missing_api_key",
            "CORE requires CORE_API_KEY; all other sources continue",
            terminal=True,
        )
    params = {"q": query, "limit": str(options.per_source)}
    url = SOURCE_ENDPOINTS["core"] + "?" + urllib.parse.urlencode(params)
    data = client.get_json(url, headers={"Authorization": f"Bearer {api_key}"})
    items = data.get("results") if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise SourceFailure("invalid_response", "CORE results are malformed")
    records: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        authors = [
            author.get("name") if isinstance(author, dict) else author
            for author in item.get("authors") or []
        ]
        journals = item.get("journals") or []
        venue = next(
            (
                journal.get("title")
                for journal in journals
                if isinstance(journal, dict) and journal.get("title")
            ),
            None,
        )
        doi = normalize_doi(item.get("doi"))
        fulltext = clean_url(item.get("downloadUrl") or item.get("fullTextLink"))
        source_urls = item.get("sourceFulltextUrls") or []
        records.append(
            make_record(
                "core",
                item.get("id") or doi,
                query,
                len(records) + 1,
                title=item.get("title"),
                authors=authors,
                year=item.get("yearPublished"),
                publication_date=item.get("publishedDate"),
                venue=venue or item.get("publisher"),
                publication_type=item.get("documentType"),
                language=item.get("language"),
                abstract=item.get("abstract"),
                identifiers={"doi": doi},
                url=f"https://doi.org/{doi}" if doi else next(iter(source_urls), None),
                open_access_url=fulltext,
                citation_count=item.get("citationCount"),
            )
        )
    return SearchBatch(records, safe_int(data.get("totalHits")), endpoint_only(url))


ADAPTERS: dict[str, Callable[[HttpClient, str, SearchOptions], SearchBatch]] = {
    "pubmed": search_pubmed,
    "europepmc": search_europepmc,
    "pubtator3": search_pubtator3,
    "litvar2": search_litvar2,
    "clinvar": search_clinvar,
    "clingen": search_clingen,
    "civic": search_civic,
    "open-targets": search_open_targets,
    "gwas-catalog": search_gwas_catalog,
    "clinicaltrials": search_clinical_trials,
    "reactome": search_reactome,
    "uniprot": search_uniprot,
    "openalex": search_openalex,
    "crossref": search_crossref,
    "datacite": search_datacite,
    "doaj": search_doaj,
    "openaire": search_openaire,
    "core": search_core,
    "arxiv": search_arxiv,
    "dblp": search_dblp,
    "semantic-scholar": search_semantic_scholar,
}


def string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]
    text = clean_text(value)
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def read_web_results_payload(path: str) -> Any:
    try:
        if path == "-":
            payload = sys.stdin.buffer.read(MAX_WEB_RESULTS_BYTES + 1)
        else:
            with open(path, "rb") as handle:
                payload = handle.read(MAX_WEB_RESULTS_BYTES + 1)
    except OSError as error:
        raise SourceFailure("web_results_io_error", sanitize_error(error)) from error
    if len(payload) > MAX_WEB_RESULTS_BYTES:
        raise SourceFailure(
            "web_results_too_large",
            f"web result input exceeds {MAX_WEB_RESULTS_BYTES} bytes",
        )
    try:
        return json.loads(payload.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SourceFailure(
            "invalid_web_results_json", sanitize_error(error)
        ) from error


def normalize_web_searches(payload: Any, fallback_query: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [{"query": fallback_query, "results": payload}]
    if not isinstance(payload, dict):
        raise SourceFailure(
            "invalid_web_results", "web result input must be an object or list"
        )
    if isinstance(payload.get("searches"), list):
        searches = payload["searches"]
    elif isinstance(payload.get("results"), list):
        searches = [payload]
    else:
        raise SourceFailure(
            "invalid_web_results",
            "web result object must contain a searches or results list",
        )
    if any(not isinstance(search, dict) for search in searches):
        raise SourceFailure(
            "invalid_web_results", "each web search run must be an object"
        )
    return searches


def parse_agent_web_search(
    search: dict[str, Any],
    fallback_query: str,
    options: SearchOptions,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    query = collapse_ws(search.get("query")) or fallback_query
    declared_family = search.get("query_family") or search.get("family")
    normalized_family = collapse_ws(declared_family).casefold().replace("-", "_")
    if declared_family is not None and normalized_family not in QUERY_FAMILIES:
        raise SourceFailure(
            "invalid_query_family",
            f"unknown web query family: {collapse_ws(declared_family)}",
        )
    query_family = infer_query_family(
        query,
        fallback_query,
        0 if query == fallback_query else 1,
        explicit=normalized_family,
    )
    provider = truncate_text(
        collapse_ws(search.get("provider")) or "agent-default-network-search", 120
    )
    target_sources = string_list(
        search.get("target_sources")
        or search.get("target_source")
        or search.get("origin_source")
    )
    items = search.get("results")
    if not isinstance(items, list):
        raise SourceFailure(
            "invalid_web_results", "each web search run needs a results list"
        )

    records: list[dict[str, Any]] = []
    for position, item in enumerate(items, start=1):
        if not isinstance(item, dict) or not clean_text(item.get("title")):
            continue
        identifiers_input = item.get("identifiers") or {}
        identifiers: dict[str, Any] = (
            dict(identifiers_input) if isinstance(identifiers_input, dict) else {}
        )
        for name in (
            "doi",
            "pmid",
            "pmcid",
            "arxiv",
            "openalex",
            "dblp",
            "semantic_scholar",
        ):
            if item.get(name) and not identifiers.get(name):
                identifiers[name] = item[name]
        publication_types = string_list(
            item.get("publication_types") or item.get("publication_type")
        )
        languages = string_list(item.get("languages") or item.get("language"))
        rank = safe_int(item.get("rank")) or position
        if rank < 1:
            rank = position
        url = item.get("canonical_url") or item.get("url")
        source_id = (
            item.get("id")
            or identifiers.get("doi")
            or identifiers.get("pmid")
            or url
            or f"web-{normalize_title(item.get('title'))[:80]}"
        )
        record = make_record(
            AGENT_WEB_SOURCE,
            source_id,
            query,
            rank,
            title=item.get("title"),
            authors=string_list(item.get("authors")),
            year=item.get("year"),
            publication_date=item.get("publication_date"),
            venue=item.get("venue"),
            publication_type=", ".join(publication_types),
            language=", ".join(languages),
            # Search-result snippets are discovery context, not publication
            # abstracts.  Keeping the distinction prevents a web snippet from
            # being promoted to abstract-level evidence in schema v2.
            abstract=item.get("abstract"),
            identifiers=identifiers,
            url=url,
            open_access_url=item.get("open_access_url"),
            citation_count=item.get("citation_count"),
            source_enrichment={
                "providers": [provider],
                "target_sources": target_sources,
                "metadata_verified": optional_bool(item.get("metadata_verified"))
                is True,
                "constraints_verified": optional_bool(item.get("constraints_verified"))
                is True,
                "web_snippet": clean_text(item.get("snippet")) or None,
            },
            query_family=query_family,
            is_retracted=item.get("is_retracted"),
            has_correction=item.get("has_correction"),
            publication_states=string_list(item.get("publication_states")),
        )
        if record_passes_filters(record, options):
            records.append(record)

    return records, {
        "source": AGENT_WEB_SOURCE,
        "source_role": SOURCE_ROLES[AGENT_WEB_SOURCE],
        "query": query,
        "query_family": query_family,
        "status": "ok",
        "endpoint": provider,
        "received": len(items),
        "accepted": len(records),
        "reported_total": safe_int(search.get("reported_total")),
    }


def load_agent_web_results(
    paths: Iterable[str], fallback_query: str, options: SearchOptions
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    run_count = 0
    result_count = 0
    for path in paths:
        try:
            searches = normalize_web_searches(
                read_web_results_payload(path), fallback_query
            )
            if run_count + len(searches) > MAX_WEB_SEARCH_RUNS:
                raise SourceFailure(
                    "too_many_web_searches",
                    f"at most {MAX_WEB_SEARCH_RUNS} web search runs are allowed",
                )
            for search in searches:
                items = search.get("results") or []
                if result_count + len(items) > MAX_WEB_RESULTS:
                    raise SourceFailure(
                        "too_many_web_results",
                        f"at most {MAX_WEB_RESULTS} web search results are allowed",
                    )
                parsed, status = parse_agent_web_search(search, fallback_query, options)
                records.extend(parsed)
                statuses.append(status)
                run_count += 1
                result_count += len(items)
        except SourceFailure as error:
            statuses.append(
                {
                    "source": AGENT_WEB_SOURCE,
                    "source_role": SOURCE_ROLES[AGENT_WEB_SOURCE],
                    "query": fallback_query,
                    "query_family": infer_query_family(fallback_query),
                    "status": "error",
                    "endpoint": "agent-default-network-search",
                    "error": {
                        "code": error.code,
                        "message": sanitize_error(error.message),
                        "http_status": error.status,
                        "retryable": error.retryable,
                    },
                }
            )
    return records, statuses


def record_passes_filters(record: dict[str, Any], options: SearchOptions) -> bool:
    year = safe_int(record.get("year"))
    if year is not None and year > datetime.now().year + 1:
        return False
    if options.year_from is not None and (year is None or year < options.year_from):
        return False
    if options.year_to is not None and (year is None or year > options.year_to):
        return False
    if options.open_access and not record.get("open_access_url"):
        return False
    return bool(record.get("title"))


def conditional_query_skip(
    query_entry: dict[str, Any], outcomes: dict[str, dict[str, Any]]
) -> tuple[str, str] | None:
    if query_entry.get("run_condition") != "if_dependency_zero":
        return None
    dependency = collapse_ws(query_entry.get("depends_on"))
    outcome = outcomes.get(dependency)
    if outcome is None:
        return (
            "dependency_missing",
            f"Dependency {dependency or 'unknown'} has no recorded outcome; fallback was not attempted.",
        )
    if outcome.get("status") != "ok":
        return (
            "dependency_not_successful",
            f"Dependency {dependency} did not succeed; fallback was not attempted.",
        )
    reported_total = safe_int(outcome.get("reported_total"))
    received = safe_int(outcome.get("received"))
    if (reported_total is not None and reported_total > 0) or (
        received is not None and received > 0
    ):
        return (
            "dependency_nonzero",
            f"Dependency {dependency} returned results; fallback was not needed.",
        )
    return None


def record_contains_context(record: dict[str, Any], terms: Iterable[Any]) -> bool:
    text = " ".join(
        [collapse_ws(record.get("title")), collapse_ws(record.get("abstract"))]
    )
    normalized = concept_match_key(text)
    words = {word.casefold() for word in QUERY_TOKEN_RE.findall(text)}
    for term in unique_clean(terms):
        key = concept_match_key(term)
        if len(key) >= 4 and key in normalized:
            return True
        if len(key) >= 2 and collapse_ws(term).casefold() in words:
            return True
    return False


def source_status_base(
    source: str,
    query: str,
    query_family: str,
    query_entry: dict[str, Any],
) -> dict[str, Any]:
    return {
        "source": source,
        "source_role": SOURCE_ROLES.get(source),
        "query": query,
        "query_family": query_family,
        "query_lane": collapse_ws(query_entry.get("lane")) or query_family,
        "query_origin": collapse_ws(query_entry.get("origin")) or "unknown",
        "scenario": collapse_ws(query_entry.get("scenario")) or None,
        "evidence_dimension": collapse_ws(query_entry.get("evidence_dimension"))
        or None,
        "query_purpose": collapse_ws(query_entry.get("purpose")) or None,
        "run_condition": query_entry.get("run_condition", "always"),
        "depends_on": query_entry.get("depends_on"),
        "context_level": query_entry.get("context_level"),
        "requested_limit": safe_int(query_entry.get("requested_limit")),
        "endpoint": SOURCE_ENDPOINTS[source],
        "received": None,
        "accepted": None,
        "reported_total": None,
        "truncated": None,
    }


def execute_source(
    source: str,
    query_plan: list[dict[str, Any]] | list[str],
    options: SearchOptions,
    timeout: float,
    retries: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    client = HttpClient(timeout, retries)
    adapter = ADAPTERS[source]
    records: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    outcomes: dict[str, dict[str, Any]] = {}
    bounded_v2 = options.max_source_calls is not None
    remaining_records = options.per_source
    attempted_calls = 0
    original_query = (
        collapse_ws(query_plan[0].get("text"))
        if query_plan and isinstance(query_plan[0], dict)
        else collapse_ws(query_plan[0])
        if query_plan
        else ""
    )
    for index, raw_entry in enumerate(query_plan):
        query_entry = raw_entry if isinstance(raw_entry, dict) else {"text": raw_entry}
        query = collapse_ws(query_entry.get("text"))
        query_family = infer_query_family(
            query, original_query, index, explicit=query_entry.get("family")
        )
        query_lane = collapse_ws(query_entry.get("lane")) or query_family
        status = source_status_base(source, query, query_family, query_entry)
        dependency_skip = conditional_query_skip(query_entry, outcomes)
        if dependency_skip:
            skip_code, reason = dependency_skip
            status.update(status="skipped", skip_code=skip_code, reason=reason)
            statuses.append(status)
            outcomes[query_lane] = status
            continue

        if bounded_v2 and attempted_calls >= (options.max_source_calls or 0):
            status.update(
                status="skipped",
                skip_code="source_call_budget_exhausted",
                reason=(
                    f"The per-source call budget of {options.max_source_calls} "
                    "was exhausted before this lane."
                ),
            )
            statuses.append(status)
            outcomes[query_lane] = status
            continue
        if bounded_v2 and remaining_records <= 0:
            status.update(
                status="skipped",
                skip_code="source_record_budget_exhausted",
                reason=(
                    f"The per-source record budget of {options.per_source} "
                    "was exhausted before this lane."
                ),
            )
            statuses.append(status)
            outcomes[query_lane] = status
            continue

        requested_limit = safe_int(query_entry.get("requested_limit"))
        effective_limit = requested_limit or options.per_source
        if bounded_v2:
            # V2 treats ``per_source`` as a total source budget, not a budget
            # for the first lane.  Divide what remains across the calls that
            # can still be made so later evidence dimensions receive a fair,
            # deterministic slice (for example 5 records / 2 calls -> 3, 2).
            remaining_entries = len(query_plan) - index
            remaining_call_slots = min(
                (options.max_source_calls or 0) - attempted_calls,
                remaining_entries,
            )
            fair_share = (
                remaining_records + remaining_call_slots - 1
            ) // remaining_call_slots
            effective_limit = min(
                effective_limit,
                remaining_records,
                fair_share,
            )
        lane_options = (
            dataclasses.replace(options, per_source=effective_limit)
            if effective_limit != options.per_source
            else options
        )
        status["effective_limit"] = effective_limit
        if source == "arxiv" and index:
            time.sleep(3.0)
        attempted_calls += 1
        try:
            batch = adapter(client, query, lane_options)
            batch_records = batch.records[:effective_limit]
            context_level = collapse_ws(query_entry.get("context_level"))
            disease_terms = query_entry.get("disease_context_terms") or []
            for record in batch_records:
                record["query_family"] = query_family
                record["query_lane"] = query_lane
                record["query_origin"] = query_entry.get("origin")
                record["query_context_level"] = context_level or None
                record["scenario"] = collapse_ws(query_entry.get("scenario")) or None
                record["evidence_dimension"] = (
                    collapse_ws(query_entry.get("evidence_dimension")) or None
                )
                record["query_purpose"] = collapse_ws(query_entry.get("purpose")) or None
                if context_level == "strict":
                    record["variant_context_status"] = "strict_disease_anchored"
                elif context_level in {"broad", "broad_fallback"}:
                    record["variant_context_status"] = (
                        "broad_with_disease_text_match"
                        if record_contains_context(record, disease_terms)
                        else "broad_without_disease_text_match"
                    )
            accepted = [
                record
                for record in batch_records
                if record_passes_filters(record, lane_options)
            ]
            records.extend(accepted)
            if bounded_v2:
                remaining_records -= len(batch_records)
            reported_total = batch.reported_total
            status.update(
                status="ok",
                endpoint=batch.endpoint,
                received=len(batch_records),
                accepted=len(accepted),
                reported_total=reported_total,
                truncated=(reported_total > len(batch_records))
                if reported_total is not None
                else None,
            )
        except SourceSkipped as error:
            status.update(
                status="skipped",
                reason=sanitize_error(error.message),
                skip_code=error.code,
                terminal=error.terminal,
            )
        except HttpFailure as error:
            message = error.message
            if (
                source == "openalex"
                and error.status == 429
                and not os.getenv("OPENALEX_API_KEY")
            ):
                message += "; configure a free OPENALEX_API_KEY to avoid the anonymous shared quota"
            if (
                source == "semantic-scholar"
                and error.status == 429
                and not (
                    os.getenv("SEMANTIC_SCHOLAR_API_KEY") or os.getenv("S2_API_KEY")
                )
            ):
                message += "; configure SEMANTIC_SCHOLAR_API_KEY to avoid the anonymous shared quota"
            status.update(
                status="error",
                error={
                    "code": error.code,
                    "message": sanitize_error(message),
                    "http_status": error.status,
                    "retryable": error.retryable,
                },
            )
        except SourceFailure as error:
            status.update(
                status="error",
                error={
                    "code": error.code,
                    "message": sanitize_error(error.message),
                    "http_status": error.status,
                    "retryable": error.retryable,
                },
            )
        except Exception as error:  # Defensive boundary around third-party payloads.
            status.update(
                status="error",
                error={
                    "code": "unexpected_error",
                    "message": sanitize_error(error),
                    "http_status": None,
                    "retryable": False,
                },
            )
        statuses.append(status)
        outcomes[query_lane] = status
        error_detail = status.get("error") or {}
        terminal_source_unavailable = bool(status.get("terminal")) or (
            status.get("status") == "error"
            and (
                error_detail.get("http_status") in {401, 403, 429}
                or error_detail.get("code") == "unexpected_html"
            )
        )
        if terminal_source_unavailable:
            for remaining_raw in query_plan[index + 1 :]:
                remaining = (
                    remaining_raw
                    if isinstance(remaining_raw, dict)
                    else {"text": remaining_raw}
                )
                remaining_query = collapse_ws(remaining.get("text"))
                remaining_family = infer_query_family(
                    remaining_query,
                    original_query,
                    index + 1,
                    explicit=remaining.get("family"),
                )
                terminal_status = source_status_base(
                    source, remaining_query, remaining_family, remaining
                )
                terminal_status.update(
                    status="skipped",
                    skip_code="source_unavailable",
                    reason="Source is unavailable for all remaining lanes.",
                )
                statuses.append(terminal_status)
            break
    return records, statuses
