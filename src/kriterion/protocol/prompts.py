"""Prompt template construction. Every function here is a pure string
builder — same inputs always produce the same prompt text, so a
prompt-template hash (docs/v0-plan.md Section 5's manifest requirement) is
meaningful. No model calls, no I/O, no randomness live here.
"""

from __future__ import annotations

from kriterion.domain.case import DecisionCase
from kriterion.domain.committee import RoleCharter
from kriterion.domain.economics import EconomicsResult
from kriterion.domain.evidence import EvidenceItem

PROTOCOL_ID = "kriterion-protocol/v0.1"

POSITION_JSON_SCHEMA = """Respond with a single JSON object, no other text, matching exactly:
{
  "recommendation": one of "REJECT","DEFER","REQUEST_EVIDENCE","DISCOVERY","FUND_EXPERIMENT","PILOT","SCALE","HOLD","REDUCE","STOP",
  "confidence_band": one of "LOW","MEDIUM","HIGH",
  "key_reasons": [ {"text": "...", "evidence_refs": ["ev-001", ...]}, ... up to 3 entries ],
  "blocking_unknowns": ["...", ...],
  "distrusted_assumption": "..." or null,
  "evidence_requests": [ {"description": "...", "would_change": "..."}, ... ]
}
Every evidence_refs id must be one already cited in the evidence provided to you below — never invent an id."""


def format_case(case: DecisionCase) -> str:
    return (
        f"Decision requested: {case.decision_requested}\n"
        f"Ask: {case.ask.type}, GBP{case.ask.amount_gbp:,.0f}, {case.ask.duration}\n"
        f"Alternatives: {', '.join(case.alternatives)}\n"
        f"Strategic objectives: {', '.join(case.strategic_objectives) or 'none stated'}"
    )


def format_economics(economics: EconomicsResult) -> str:
    return (
        f"Deterministic economics (do not recompute or alter these numbers):\n"
        f"  NPV low/mid/high: GBP{economics.npv_low_gbp:,.0f} / "
        f"GBP{economics.npv_mid_gbp:,.0f} / GBP{economics.npv_high_gbp:,.0f}\n"
        f"  Payback (years): {economics.payback_years}\n"
        f"  Peak funding at risk: GBP{economics.peak_funding_gbp:,.0f}"
    )


def format_evidence(items: list[EvidenceItem]) -> str:
    lines = []
    for item in items:
        lines.append(
            f"  [{item.id}] ({item.category.value}, {item.attestation.value}, "
            f"strength {item.strength.value}): {item.claim} (source: {item.source})"
        )
    return "\n".join(lines) if lines else "  (none)"


def build_phase3_prompt(
    charter: RoleCharter,
    case: DecisionCase,
    evidence_items: list[EvidenceItem],
    economics: EconomicsResult,
) -> str:
    """Independent assessment (phase 3). Full case evidence + this charter's
    own concerns/objective — never another member's charter or position
    (docs/v0-plan.md Section 5's visibility rule). `evidence_items` is the
    full case ledger; `charter.required_evidence` is a checklist gap_scan.py
    checks the resulting position against, not a filter on what is shown
    here — see phases.py's run_phase3_independent_assessment docstring for
    why (a filtered version broke on a second case with different ids)."""
    return (
        f"You are the {charter.seat.value.upper()} on an executive investment committee. "
        f"You see only your own charter and the case's frozen evidence and economics — "
        f"no other committee member's views exist yet.\n\n"
        f"Your objective: {charter.objective}\n"
        f"Your concerns: {'; '.join(charter.concerns)}\n"
        f"Your standard challenges: {'; '.join(charter.standard_challenges)}\n"
        f"You are forbidden from: {'; '.join(charter.forbidden)}\n\n"
        f"{format_case(case)}\n\n"
        f"Evidence:\n{format_evidence(evidence_items)}\n\n"
        f"{format_economics(economics)}\n\n"
        f"Give your independent initial assessment. If a concern in your charter is not "
        f"addressed by the evidence above, raise it as an evidence_requests entry rather than "
        f"assuming an answer.\n\n{POSITION_JSON_SCHEMA}"
    )
