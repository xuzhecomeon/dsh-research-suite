"""Registry and deterministic detector for all supported scenarios."""

from __future__ import annotations

from ..models import Concept, SCENARIOS
from .base import Detection, ScenarioPlanner
from .clinical_evidence import ClinicalEvidencePlanner
from .drug_pipeline import DrugPipelinePlanner
from .drug_safety import DrugSafetyPlanner
from .general_basic import GeneralBasicPlanner
from .genetic_rare import GeneticRarePlanner
from .methods_benchmarking import MethodsBenchmarkingPlanner
from .target_research import TargetResearchPlanner


_PLANNERS: tuple[ScenarioPlanner, ...] = (
    DrugSafetyPlanner(),
    DrugPipelinePlanner(),
    ClinicalEvidencePlanner(),
    MethodsBenchmarkingPlanner(),
    TargetResearchPlanner(),
    GeneticRarePlanner(),
    GeneralBasicPlanner(),
)

PLANNERS: dict[str, ScenarioPlanner] = {
    planner.scenario: planner for planner in _PLANNERS
}

ALIASES = {
    "general": "general-basic",
    "basic": "general-basic",
    "target": "target-research",
    "pipeline": "drug-pipeline",
    "safety": "drug-safety",
    "clinical": "clinical-evidence",
    "methods": "methods-benchmarking",
    "method": "methods-benchmarking",
    "genetic": "genetic-rare",
    "rare": "genetic-rare",
}

_TIE_PRIORITY = {planner.scenario: index for index, planner in enumerate(_PLANNERS)}


def canonical_scenario(value: str) -> str:
    normalized = value.strip().casefold().replace("_", "-")
    normalized = ALIASES.get(normalized, normalized)
    if normalized not in SCENARIOS:
        raise ValueError(
            f"unknown scenario: {value}; choose from {', '.join(SCENARIOS)}"
        )
    return normalized


def planner_for(scenario: str) -> ScenarioPlanner:
    canonical = canonical_scenario(scenario)
    return PLANNERS[canonical]


def detect_scenarios(
    question: str,
    concepts: tuple[Concept, ...] = (),
) -> tuple[Detection, ...]:
    if not question.strip():
        raise ValueError("question must not be empty")
    detections = [planner.detect(question, concepts) for planner in _PLANNERS]
    return tuple(
        sorted(
            detections,
            key=lambda item: (-item.score, _TIE_PRIORITY[item.scenario]),
        )
    )


def detect_primary_scenario(
    question: str,
    concepts: tuple[Concept, ...] = (),
) -> str:
    return detect_scenarios(question, concepts)[0].scenario


def registered_scenarios() -> tuple[str, ...]:
    return tuple(PLANNERS)
