"""SyntheticRecommendation, HumanDecision, OutcomeContract
(docs/v0-plan.md Section 4 and Section 9's module layout)."""

from __future__ import annotations

from dataclasses import dataclass, field

from kriterion.domain.base import KriterionRecord
from kriterion.domain.enums import ConfidenceBand, DecisionAction


@dataclass(kw_only=True)
class Dissent:
    verbatim: str
    refs: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class SyntheticRecommendation(KriterionRecord):
    action: DecisionAction
    amount: float
    duration: str
    conditions: list[str] = field(default_factory=list)
    stop_conditions: list[str] = field(default_factory=list)
    strongest_dissent: Dissent
    unresolved_unknowns: list[str] = field(default_factory=list)
    confidence_band: ConfidenceBand = ConfidenceBand.MEDIUM

    def __post_init__(self) -> None:
        if not self.strongest_dissent.verbatim.strip():
            raise ValueError(
                "SyntheticRecommendation.strongest_dissent must be non-empty, "
                "even under unanimity (docs/v0-plan.md Section 4)"
            )


@dataclass(kw_only=True)
class HumanDecision(KriterionRecord):
    """Always a separate file from SyntheticRecommendation — never merged (ADR-006)."""

    action: DecisionAction
    disposition: str  # accept | modify | reject
    overrides: list[str] = field(default_factory=list)
    rationale: str = ""
    owner: str = ""
    decided_at: str = ""


@dataclass(kw_only=True)
class Measure:
    name: str
    baseline: str
    target: str
    source_ref: str  # must resolve to a MEASURED or ASSUMPTION EvidenceItem id


@dataclass(kw_only=True)
class OutcomeContract(KriterionRecord):
    baseline_date: str
    measures: list[Measure]
    owner: str
    review_date: str
    next_decision: str
    kill_criteria: list[str] = field(default_factory=list)
