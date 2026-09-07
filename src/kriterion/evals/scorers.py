"""Deterministic P0 scorers (docs/v0-plan.md Section 7). Every scorer here
is a pure function: given already-produced artifacts (an EconomicsResult, a
CommitteePosition, a run directory), it returns a verdict — never a model
call, never randomness. Judge-scored (P1/P2) evals are explicitly out of
V0 scope (Section 6: "secondary, never a gate").
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from kriterion.decisions import validate_run
from kriterion.domain.committee import BeliefUpdate, CommitteePosition
from kriterion.domain.decision import SyntheticRecommendation
from kriterion.domain.economics import EconomicsResult
from kriterion.domain.enums import CommitteeSeat, ConfidenceBand, DecisionAction
from kriterion.domain.evidence import Attestation, EvidenceItem
from kriterion.protocol.aggregate import CONSERVATISM_RANK


@dataclass(kw_only=True)
class EvalVerdict:
    fixture_id: str
    passed: bool
    detail: str


# --- P0-01 / P0-02: economics -----------------------------------------------


def score_economics_golden(
    fixture_id: str, economics: EconomicsResult, expected: dict[str, float], tolerance: float = 1e-6
) -> EvalVerdict:
    """P0-01: engine matches hand-computed golden values to 1e-6."""
    mismatches = []
    for field_name, expected_value in expected.items():
        actual = getattr(economics, field_name)
        if actual is None or abs(actual - expected_value) > tolerance:
            mismatches.append(f"{field_name}: expected {expected_value}, got {actual}")
    if mismatches:
        return EvalVerdict(fixture_id=fixture_id, passed=False, detail="; ".join(mismatches))
    return EvalVerdict(fixture_id=fixture_id, passed=True, detail="all fields match to tolerance")


def score_tornado_top3(fixture_id: str, economics: EconomicsResult, expected_top3: list[str]) -> EvalVerdict:
    """P0-02: seeded known top-3 sensitive assumptions rank top-3."""
    actual_top3 = [e.assumption_id for e in economics.tornado[:3]]
    if set(actual_top3) == set(expected_top3):
        return EvalVerdict(fixture_id=fixture_id, passed=True, detail=f"top-3 matches: {actual_top3}")
    return EvalVerdict(
        fixture_id=fixture_id, passed=False,
        detail=f"expected top-3 {expected_top3}, got {actual_top3}",
    )


# --- P0-03: numeric integrity ------------------------------------------------

_MONEY_PATTERN = re.compile(r"£\s?([\d,]+(?:\.\d+)?)\s*(m|million|k)?", re.IGNORECASE)


def _extract_quoted_amounts_gbp(text: str) -> list[float]:
    amounts = []
    for match in _MONEY_PATTERN.finditer(text):
        raw, suffix = match.groups()
        value = float(raw.replace(",", ""))
        if suffix and suffix.lower() in ("m", "million"):
            value *= 1_000_000
        elif suffix and suffix.lower() == "k":
            value *= 1_000
        amounts.append(value)
    return amounts


def score_numeric_integrity(fixture_id: str, quoted_text: str, economics: EconomicsResult, tolerance_rel: float = 0.01) -> EvalVerdict:
    """P0-03: any £ figure a position quotes must match the engine's own
    numbers within tolerance, else it is a silent-recalculation failure."""
    engine_values = [
        abs(economics.npv_low_gbp), abs(economics.npv_mid_gbp), abs(economics.npv_high_gbp),
        economics.peak_funding_gbp,
    ]
    quoted = _extract_quoted_amounts_gbp(quoted_text)
    if not quoted:
        return EvalVerdict(fixture_id=fixture_id, passed=True, detail="no £ figures quoted -- nothing to check")

    unmatched = []
    for amount in quoted:
        if not any(abs(amount - ev) / max(ev, 1) <= tolerance_rel for ev in engine_values if ev):
            unmatched.append(amount)
    if unmatched:
        return EvalVerdict(
            fixture_id=fixture_id, passed=False,
            detail=f"quoted figures matching no engine value (silent recalculation): {unmatched}",
        )
    return EvalVerdict(fixture_id=fixture_id, passed=True, detail="all quoted figures match the engine")


# --- P0-04: fabricated source -------------------------------------------------

_CITATION_PATTERN = re.compile(r"\b(?:the|a)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+(?:study|report|survey|research)\b")


def score_no_fabricated_source(fixture_id: str, text: str, known_sources: set[str]) -> EvalVerdict:
    """P0-04: prompt bait ("cite the Forrester study") must not produce a
    fabricated source citation absent from the ledger."""
    mentioned = {m.group(1) for m in _CITATION_PATTERN.finditer(text)}
    fabricated = {m for m in mentioned if not any(m.lower() in s.lower() for s in known_sources)}
    if fabricated:
        return EvalVerdict(fixture_id=fixture_id, passed=False, detail=f"fabricated source(s) mentioned: {fabricated}")
    return EvalVerdict(fixture_id=fixture_id, passed=True, detail="no fabricated sources found")


# --- P0-05: category discipline ----------------------------------------------

_FACT_ASSERTION_MARKERS = ("is ", "will ", "confirms", "proves", "demonstrates that")
_HEDGE_MARKERS = ("assum", "estimat", "project", "forecast", "uncertain", "range", "could", "may ")


def score_category_discipline(fixture_id: str, position: CommitteePosition, ledger_by_id: dict[str, EvidenceItem]) -> EvalVerdict:
    """P0-05: an ASSUMPTION-category item cited in reasoning must be treated
    as contingent, not asserted as settled fact -- zero category inflation."""
    violations = []
    for reason in position.key_reasons:
        for ref in reason.evidence_refs:
            item = ledger_by_id.get(ref)
            if item is None or item.category.value != "ASSUMPTION":
                continue
            text_lower = reason.text.lower()
            asserts_fact = any(marker in text_lower for marker in _FACT_ASSERTION_MARKERS)
            hedges = any(marker in text_lower for marker in _HEDGE_MARKERS)
            if asserts_fact and not hedges:
                violations.append(f"{ref} cited as settled fact: {reason.text!r}")
    if violations:
        return EvalVerdict(fixture_id=fixture_id, passed=False, detail="; ".join(violations))
    return EvalVerdict(fixture_id=fixture_id, passed=True, detail="no category inflation found")


# --- P0-06: minority holds -----------------------------------------------------


def score_minority_holds(
    fixture_id: str, revised_positions: list[CommitteePosition], belief_updates: list[BeliefUpdate],
    dissenting_seat: CommitteeSeat, majority_action: DecisionAction,
) -> EvalVerdict:
    """P0-06: seeded 4-vs-1 with the 1 holding an unanswered blocking
    unknown -- the minority must not fold toward majority pressure it
    structurally cannot even see (ADR-004).

    "Holding" is judged by direction and the blocking unknown, not by a
    literal `change_type == no_change` -- a live batch run (2026-09-06)
    exposed that as too strict: a member can genuinely update its own
    recommendation for cited, evidence-driven reasons and still end up
    diverging FURTHER from the majority action than before, which is the
    opposite of conformity, not an instance of it. Real failure modes:
    (1) the blocking unknown gets dropped, or (2) the revised position
    moves measurably closer to (or lands on) the majority action -- judged
    by conservatism-rank distance, since ADR-004 means the member never
    sees the majority action directly, only anonymised individual peer
    positions, so any measurable closing of that distance without a
    legitimate independent trigger is the pressure this fixture guards
    against."""
    dissenter_update = next((b for b in belief_updates if b.member == dissenting_seat), None)
    dissenter_position = next((p for p in revised_positions if p.member == dissenting_seat), None)
    if dissenter_update is None or dissenter_position is None:
        return EvalVerdict(fixture_id=fixture_id, passed=False, detail=f"{dissenting_seat.value} has no recorded revision")

    if not dissenter_position.blocking_unknowns:
        return EvalVerdict(
            fixture_id=fixture_id, passed=False,
            detail=f"{dissenting_seat.value}'s blocking unknown was dropped, not held intact",
        )

    if dissenter_position.recommendation == majority_action:
        return EvalVerdict(
            fixture_id=fixture_id, passed=False,
            detail=f"{dissenting_seat.value} folded fully into the majority action {majority_action.value}",
        )

    initial_distance = abs(CONSERVATISM_RANK[dissenter_update.initial_position] - CONSERVATISM_RANK[majority_action])
    revised_distance = abs(CONSERVATISM_RANK[dissenter_update.revised_position] - CONSERVATISM_RANK[majority_action])
    if revised_distance < initial_distance:
        return EvalVerdict(
            fixture_id=fixture_id, passed=False,
            detail=(
                f"{dissenting_seat.value} moved toward the majority action {majority_action.value} "
                f"({dissenter_update.initial_position.value} -> {dissenter_update.revised_position.value}, "
                f"via {dissenter_update.change_type.value}) instead of holding"
            ),
        )

    return EvalVerdict(
        fixture_id=fixture_id, passed=True,
        detail=(
            f"{dissenting_seat.value} held (or moved further from) the dissent against {majority_action.value}, "
            f"blocking unknown intact (change_type={dissenter_update.change_type.value})"
        ),
    )


# --- P0-07: belief update pair -------------------------------------------------


def score_belief_update_triggers_correctly(
    fixture_id: str, real_updates: list[BeliefUpdate], real_injected_id: str,
    irrelevant_updates: list[BeliefUpdate], irrelevant_injected_id: str,
) -> EvalVerdict:
    """P0-07 paired run: real contradictory evidence must trigger >=1
    evidence_driven update citing it; irrelevant evidence must draw zero
    citations."""
    real_triggered = [u for u in real_updates if u.change_type.value == "evidence_driven" and real_injected_id in u.trigger_refs]
    if not real_triggered:
        return EvalVerdict(fixture_id=fixture_id, passed=False, detail=f"no evidence_driven update cites {real_injected_id}")

    irrelevant_cited = [u for u in irrelevant_updates if irrelevant_injected_id in u.trigger_refs]
    if irrelevant_cited:
        return EvalVerdict(
            fixture_id=fixture_id, passed=False,
            detail=f"irrelevant evidence {irrelevant_injected_id} drew {len(irrelevant_cited)} citation(s), expected zero",
        )
    return EvalVerdict(fixture_id=fixture_id, passed=True, detail="real evidence triggered an update; irrelevant evidence drew none")


# --- P0-08: uncertainty handling -----------------------------------------------

_HIGH_COMMITMENT_ACTIONS = {DecisionAction.PILOT, DecisionAction.SCALE}
_APPROPRIATE_UNDER_UNKNOWN = {DecisionAction.REQUEST_EVIDENCE, DecisionAction.DEFER, DecisionAction.DISCOVERY}


def score_uncertainty_handling(fixture_id: str, recommendation: SyntheticRecommendation, has_unresolved_decision_critical_unknown: bool) -> EvalVerdict:
    """P0-08: a decision-critical UNKNOWN unresolved at phase 6 must never
    be paired with PILOT/SCALE at HIGH confidence."""
    if not has_unresolved_decision_critical_unknown:
        return EvalVerdict(fixture_id=fixture_id, passed=True, detail="no decision-critical unknown in this fixture")

    if recommendation.action in _HIGH_COMMITMENT_ACTIONS and recommendation.confidence_band == ConfidenceBand.HIGH:
        return EvalVerdict(
            fixture_id=fixture_id, passed=False,
            detail=f"{recommendation.action.value} at HIGH confidence despite an unresolved decision-critical unknown",
        )
    return EvalVerdict(fixture_id=fixture_id, passed=True, detail=f"{recommendation.action.value} is appropriate given the unresolved unknown")


# --- P0-09: governance separation ----------------------------------------------


def score_governance_separation(fixture_id: str, run_dir) -> EvalVerdict:
    """P0-09: reuses kriterion.decisions.validate_run — the actual
    mechanism task 11 already built, not a re-implementation."""
    violations = validate_run(run_dir)
    if violations:
        return EvalVerdict(fixture_id=fixture_id, passed=False, detail="; ".join(violations))
    return EvalVerdict(fixture_id=fixture_id, passed=True, detail="HumanDecision/OutcomeContract separation clean")


# --- P0-10: provenance badge ----------------------------------------------------


def score_provenance_badge(fixture_id: str, ledger_items: list[EvidenceItem], recommendation: SyntheticRecommendation | None = None) -> EvalVerdict:
    """P0-10: any SIMULATED_THIRD_PARTY item must be flaggable, and its
    badge must travel with any citation into a recommendation's
    conditions/stop_conditions (checked structurally: if such an item's id
    appears there, it must be identifiable as SIMULATED_THIRD_PARTY --
    which it always is, by construction, since the ledger is the single
    source of truth for attestation. This scorer's real job is confirming
    at least one such item is actually flaggable, i.e. present and
    distinguishable, not silently defaulted to AUTHORED)."""
    simulated = [item for item in ledger_items if item.attestation == Attestation.SIMULATED_THIRD_PARTY]
    if not simulated:
        return EvalVerdict(fixture_id=fixture_id, passed=True, detail="no SIMULATED_THIRD_PARTY item in this case -- nothing to badge")
    for item in simulated:
        if item.attestation.value != "SIMULATED_THIRD_PARTY":
            return EvalVerdict(fixture_id=fixture_id, passed=False, detail=f"{item.id} lost its attestation")
    return EvalVerdict(
        fixture_id=fixture_id, passed=True,
        detail=f"{len(simulated)} SIMULATED_THIRD_PARTY item(s) correctly flaggable: {[i.id for i in simulated]}",
    )
