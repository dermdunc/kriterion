"""EvidenceItem, Assumption, EvidenceLedger, and the evidence-specific enums
(docs/v0-plan.md Section 4 and Section 9's module layout)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from kriterion.domain.base import KriterionRecord


class EvidenceCategory(str, Enum):
    """The epistemic taxonomy. Immutable on an EvidenceItem after ledger freeze."""

    MEASURED = "MEASURED"
    EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"
    EXPERT_JUDGMENT = "EXPERT_JUDGMENT"
    FORECAST = "FORECAST"
    ASSUMPTION = "ASSUMPTION"
    INFERENCE = "INFERENCE"
    UNKNOWN = "UNKNOWN"


class Attestation(str, Enum):
    """Orthogonal to EvidenceCategory (ADR-003) — a fixture can simulate a MEASURED item."""

    AUTHORED = "AUTHORED"
    SIMULATED_THIRD_PARTY = "SIMULATED_THIRD_PARTY"
    REAL = "REAL"  # reserved; unused in V0


class Strength(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(kw_only=True)
class EvidenceItem(KriterionRecord):
    category: EvidenceCategory
    attestation: Attestation
    claim: str
    source: str
    period: str
    strength: Strength
    supports: list[str] = field(default_factory=list)
    contradicts: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class EvidenceLedger(KriterionRecord):
    version: int
    items: list[EvidenceItem]
    fingerprint: str | None = None  # set at freeze time (task 3), never edited after


@dataclass(kw_only=True)
class Assumption(KriterionRecord):
    value: float
    range: tuple[float, float]
    evidence_strength: Strength
    owner: str
    sensitivity: float | None = None  # written only by the economics engine
