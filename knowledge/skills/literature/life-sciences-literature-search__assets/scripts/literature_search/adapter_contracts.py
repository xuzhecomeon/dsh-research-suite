"""Stable contracts shared by publication adapters and orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SearchOptions:
    per_source: int
    year_from: int | None
    year_to: int | None
    open_access: bool
    publication_types: tuple[str, ...] = ()
    sort: str = "relevance"
    genes: tuple[str, ...] = ()
    diseases: tuple[str, ...] = ()
    concept_genes: tuple[str, ...] = ()
    concept_diseases: tuple[str, ...] = ()
    chemicals: tuple[str, ...] = ()
    go_terms: tuple[str, ...] = ()
    experimental_methods: tuple[str, ...] = ()
    accession_ids: tuple[str, ...] = ()
    accession_types: tuple[str, ...] = ()
    linked_databases: tuple[str, ...] = ()
    has_associated_data: bool = False
    mesh_synonyms: bool = False
    # ``None`` retains the adapter-level per-query behavior. V2 orchestration
    # sets this value and interprets ``per_source`` as a total source budget.
    max_source_calls: int | None = None


@dataclass(frozen=True)
class ResultFilters:
    publication_types: tuple[str, ...] = ()
    excluded_publication_types: tuple[str, ...] = ()
    authors: tuple[str, ...] = ()
    venues: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    required_identifiers: tuple[str, ...] = ()
    require_abstract: bool = False
    exclude_preprints: bool = False
    sort: str = "relevance"
    min_reported_count: int | None = None
    count_entities: tuple[str, ...] = ("proband",)
    count_context_terms: tuple[str, ...] = ()
    require_count_context: bool = False
    strict_count: bool = False
    required_sources: tuple[str, ...] = ()
    include_retracted: bool = False
    has_associated_data: bool = False


@dataclass
class SearchBatch:
    records: list[dict[str, Any]]
    reported_total: int | None
    endpoint: str


class HttpFailure(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status: int | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.retryable = retryable


class SourceFailure(Exception):
    """A source understood the request but could not return a valid batch."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status: int | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.retryable = retryable


class SourceSkipped(Exception):
    def __init__(self, code: str, message: str, *, terminal: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.terminal = terminal
