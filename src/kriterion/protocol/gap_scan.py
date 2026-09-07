"""Deterministic contradiction + gap scan (phase 5's "contradiction + gap
list", docs/v0-plan.md Section 5). Deterministic-before-generative (ADR-002's
spirit extended here): both checks are computable from the ledger and the
initial positions without a model call, so they are not delegated to one.

Contradiction: a pair of evidence items where one's `contradicts` field
names the other, and both genuinely exist in the ledger — not a model's
opinion about what conflicts, a fact already recorded at evidence-authoring
time (kriterion ledger add).

Gap: a charter's own `required_evidence` id that its member's initial
position never actually cited in a key_reason — the member's own charter
said this evidence mattered, and their assessment did not use it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from kriterion.domain.committee import CommitteePosition, RoleCharter
from kriterion.domain.evidence import EvidenceItem


@dataclass(kw_only=True)
class GapScanResult:
    contradictions: list[tuple[str, str]] = field(default_factory=list)  # (item_id, contradicted_id)
    gaps: list[tuple[str, str]] = field(default_factory=list)  # (seat_value, missing_evidence_id)


def scan_contradictions_and_gaps(
    evidence_by_id: dict[str, EvidenceItem],
    charters: list[RoleCharter],
    initial_positions: list[CommitteePosition],
) -> GapScanResult:
    contradictions: list[tuple[str, str]] = []
    for item in evidence_by_id.values():
        for other_id in item.contradicts:
            if other_id in evidence_by_id:
                contradictions.append((item.id, other_id))

    positions_by_member = {p.member: p for p in initial_positions}
    gaps: list[tuple[str, str]] = []
    for charter in charters:
        position = positions_by_member.get(charter.seat)
        if position is None:
            continue
        cited_ids = {ref for reason in position.key_reasons for ref in reason.evidence_refs}
        for required_id in charter.required_evidence:
            if required_id not in cited_ids:
                gaps.append((charter.seat.value, required_id))

    return GapScanResult(contradictions=contradictions, gaps=gaps)
