"""Scenario-aware life-science literature search package."""

from ._version import PRODUCT_VERSION

__version__ = PRODUCT_VERSION

from .models import (
    Concept,
    Constraints,
    EvidenceObject,
    QueryLane,
    SearchBudget,
    SearchPlan,
    SearchRequest,
    SourceRoute,
)
from .execution import execute_plan, run_search
from .planner import build_plan, plan_search, validate_plan
from .renderers import RenderOptions, render
from .schema import validate_bundle

__all__ = [
    "Concept",
    "Constraints",
    "EvidenceObject",
    "QueryLane",
    "SearchBudget",
    "SearchPlan",
    "SearchRequest",
    "SourceRoute",
    "RenderOptions",
    "build_plan",
    "execute_plan",
    "plan_search",
    "render",
    "run_search",
    "validate_bundle",
    "validate_plan",
]
