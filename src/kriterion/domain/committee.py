"""RoleCharter, CommitteePosition, EvidenceRequest, Challenge, BeliefUpdate
(docs/v0-plan.md Section 4/5 and Section 9's module layout).

EvidenceRequest isn't named in Section 9's committee.py comment, but Section 4
groups it with the deliberation-protocol types (member/description/
would_change/status) rather than with evidence.py's provenance types
(category/attestation/ledger), so it lives here.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from kriterion.domain.base import KriterionRecord
from kriterion.domain.enums import (
    ChallengeType,
    ChangeType,
    CommitteeSeat,
    ConfidenceBand,
    DecisionAction,
    DriftFlag,
    EvidenceRequestStatus,
    PositionPhase,
)


@dataclass(kw_only=True)
class RoleCharter(KriterionRecord):
    version: str
    seat: CommitteeSeat
    objective: str
    concerns: list[str]
    required_evidence: list[str]
    decision_rights: list[str]
    standard_challenges: list[str]
    failure_modes: list[str]
    forbidden: list[str]


@dataclass(kw_only=True)
class KeyReason:
    text: str
    evidence_refs: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class CommitteePosition(KriterionRecord):
    member: CommitteeSeat
    phase: PositionPhase
    recommendation: DecisionAction
    confidence_band: ConfidenceBand
    key_reasons: list[KeyReason]
    blocking_unknowns: list[str] = field(default_factory=list)
    distrusted_assumption: str | None = None

    def __post_init__(self) -> None:
        if len(self.key_reasons) > 3:
            raise ValueError("CommitteePosition.key_reasons must have at most 3 entries")


@dataclass(kw_only=True)
class EvidenceRequest(KriterionRecord):
    member: CommitteeSeat
    description: str
    would_change: str
    status: EvidenceRequestStatus = EvidenceRequestStatus.UNAVAILABLE


@dataclass(kw_only=True)
class Challenge(KriterionRecord):
    type: ChallengeType
    author_role: CommitteeSeat
    content: str
    evidence_refs: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class BeliefUpdate(KriterionRecord):
    """docs/v0-plan.md Section 5. One per member per run, including no_change."""

    member: CommitteeSeat
    initial_position: DecisionAction
    initial_confidence: ConfidenceBand
    revised_position: DecisionAction
    revised_confidence: ConfidenceBand
    change_type: ChangeType
    trigger_refs: list[str] = field(default_factory=list)
    stated_reason: str = ""
    drift_flags: list[DriftFlag] = field(default_factory=list)  # harness-written only
