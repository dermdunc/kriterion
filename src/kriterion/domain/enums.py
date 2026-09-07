"""Cross-cutting enums shared by case.py/committee.py/decision.py.

EvidenceCategory/Attestation/Strength live in evidence.py instead, per
docs/v0-plan.md Section 9's module comment for that file.
"""

from enum import Enum


class ConfidenceBand(str, Enum):
    """Bands, not decimals — see docs/v0-plan.md Section 4."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CaseRealism(str, Enum):
    AUTHORED_FIXTURE = "AUTHORED_FIXTURE"  # the only value used in V0 — every case is fictional


class DecisionAction(str, Enum):
    """The fixed decision vocabulary. APPROVE is deliberately absent."""

    REJECT = "REJECT"
    DEFER = "DEFER"
    REQUEST_EVIDENCE = "REQUEST_EVIDENCE"
    DISCOVERY = "DISCOVERY"
    FUND_EXPERIMENT = "FUND_EXPERIMENT"
    PILOT = "PILOT"
    SCALE = "SCALE"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    STOP = "STOP"


class PositionPhase(str, Enum):
    INITIAL = "initial"
    REVISED = "revised"


class EvidenceRequestStatus(str, Enum):
    SUPPLIED = "supplied"
    UNAVAILABLE = "unavailable"


class ChallengeType(str, Enum):
    CASE_FOR = "case_for"
    CASE_AGAINST = "case_against"
    PREMORTEM = "premortem"
    CONTRADICTION = "contradiction"
    GAP = "gap"


class ChangeType(str, Enum):
    """docs/v0-plan.md Section 5, BeliefUpdate.change_type."""

    EVIDENCE_DRIVEN = "evidence_driven"
    ARGUMENT_DRIVEN = "argument_driven"
    NO_CHANGE = "no_change"
    UNEXPLAINED = "unexplained"


class DriftFlag(str, Enum):
    """Harness-written only, never model-written (docs/v0-plan.md Section 5)."""

    UNEXPLAINED = "unexplained"
    RETROFIT = "retrofit"
    CONFIDENCE_JUMP = "confidence_jump"
    ECHO = "echo"


class CommitteeSeat(str, Enum):
    """Five voting seats (docs/v0-plan.md Section 5) — CIO is cut as a voting member in V0."""

    CFO = "cfo"
    CTO = "cto"
    CISO = "ciso"
    CRO_COMPLIANCE = "cro_compliance"
    BUSINESS_EXECUTIVE = "business_executive"
    # Not a real seat: Baseline A (Section 6) is one continuous single-agent
    # context covering all five charters collapsed, so its CommitteePosition/
    # BeliefUpdate records need SOME CommitteeSeat value to satisfy the
    # domain type. Using this rather than an arbitrary real seat keeps it
    # honestly distinguishable in any report/eval that groups by member.
    BASELINE_A = "baseline_a"
