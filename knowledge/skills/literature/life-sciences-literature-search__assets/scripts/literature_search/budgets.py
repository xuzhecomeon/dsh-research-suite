"""Configurable search-depth budgets."""

from __future__ import annotations

import dataclasses

from .models import SearchBudget


DEFAULT_BUDGETS: dict[str, SearchBudget] = {
    "quick": SearchBudget(
        depth="quick",
        per_source=8,
        per_lane=6,
        max_calls_per_source=4,
        result_limit=8,
        max_lanes=4,
        max_sources=6,
        web_search_min=0,
        web_search_max=2,
        expansion="none",
        expansion_seeds=0,
        expansion_per_seed=0,
        weak_result_threshold=3,
    ),
    "standard": SearchBudget(
        depth="standard",
        per_source=15,
        per_lane=12,
        max_calls_per_source=8,
        result_limit=20,
        max_lanes=14,
        max_sources=12,
        web_search_min=2,
        web_search_max=6,
        expansion="none",
        expansion_seeds=3,
        expansion_per_seed=10,
        weak_result_threshold=5,
    ),
    "deep": SearchBudget(
        depth="deep",
        per_source=30,
        per_lane=20,
        max_calls_per_source=16,
        result_limit=40,
        max_lanes=32,
        max_sources=21,
        web_search_min=6,
        web_search_max=12,
        expansion="both",
        expansion_seeds=5,
        expansion_per_seed=20,
        weak_result_threshold=8,
    ),
}


def budget_for(
    depth: str,
    *,
    per_source: int | None = None,
    per_lane: int | None = None,
    result_limit: int | None = None,
    expansion: str | None = None,
) -> SearchBudget:
    try:
        budget = DEFAULT_BUDGETS[depth]
    except KeyError as error:
        raise ValueError(f"unknown search depth: {depth}") from error
    updates = {
        key: value
        for key, value in {
            "per_source": per_source,
            "per_lane": per_lane,
            "result_limit": result_limit,
            "expansion": expansion,
        }.items()
        if value is not None
    }
    return dataclasses.replace(budget, **updates)
