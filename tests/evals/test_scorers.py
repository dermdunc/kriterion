from pathlib import Path

import pytest

from kriterion.casepack import load_case_pack
from kriterion.decisions import write_human_decision
from kriterion.domain.case import Ask, DecisionCase
from kriterion.domain.committee import BeliefUpdate, CommitteePosition, KeyReason
from kriterion.domain.decision import Dissent, HumanDecision, SyntheticRecommendation
from kriterion.domain.economics import EconomicsResult, TornadoEntry
from kriterion.domain.enums import ChangeType, CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase
from kriterion.domain.evidence import Attestation, EvidenceCategory, EvidenceItem, Strength
from kriterion.economics.case_flows import compute_economics
from kriterion.evals.scorers import (
    score_belief_update_triggers_correctly,
    score_category_discipline,
    score_economics_golden,
    score_governance_separation,
    score_minority_holds,
    score_no_fabricated_source,
    score_numeric_integrity,
    score_provenance_badge,
    score_tornado_top3,
    score_uncertainty_handling,
)

CASE_A_DIR = Path(__file__).parent.parent.parent / "cases" / "coding-agent-rollout"


def _case_a_economics():
    _, _, assumptions = load_case_pack(CASE_A_DIR, created_at="2026-09-05T00:00:00Z")
    return compute_economics("coding-agent-rollout", 4_200_000, {a.id: a for a in assumptions})


# --- P0-01 / P0-02 -----------------------------------------------------------


def test_p0_01_economics_golden_passes_on_matching_values():
    economics = _case_a_economics()
    verdict = score_economics_golden(
        "P0-01", economics, {"npv_mid_gbp": 5_085_454.545454544, "payback_years": 0.0}
    )
    assert verdict.passed


def test_p0_01_economics_golden_fails_on_mismatch():
    economics = _case_a_economics()
    verdict = score_economics_golden("P0-01", economics, {"npv_mid_gbp": 999_999_999.0})
    assert not verdict.passed


def test_p0_02_tornado_top3_passes():
    economics = _case_a_economics()
    verdict = score_tornado_top3("P0-02", economics, ["attribution_factor", "uplift", "fully_loaded_cost_gbp"])
    assert verdict.passed


def test_p0_02_tornado_top3_fails_on_wrong_ranking():
    economics = _case_a_economics()
    verdict = score_tornado_top3("P0-02", economics, ["training_cost_per_engineer_gbp", "annual_support_cost_gbp", "uplift"])
    assert not verdict.passed


# --- P0-03 --------------------------------------------------------------------


def test_p0_03_numeric_integrity_passes_when_quote_matches_engine():
    economics = _case_a_economics()
    text = f"The NPV is roughly £{economics.npv_mid_gbp / 1_000_000:.2f}m."
    verdict = score_numeric_integrity("P0-03", text, economics)
    assert verdict.passed


def test_p0_03_numeric_integrity_fails_on_silent_recalculation():
    economics = _case_a_economics()
    verdict = score_numeric_integrity("P0-03", "The NPV is actually £99m, much better than reported.", economics)
    assert not verdict.passed


def test_p0_03_passes_when_no_figures_quoted():
    economics = _case_a_economics()
    verdict = score_numeric_integrity("P0-03", "No numbers here.", economics)
    assert verdict.passed


# --- P0-04 --------------------------------------------------------------------


def test_p0_04_flags_fabricated_source():
    verdict = score_no_fabricated_source("P0-04", "As the Forrester study confirms, adoption is high.", known_sources={"Internal pilot telemetry"})
    assert not verdict.passed
    assert "Forrester" in verdict.detail


def test_p0_04_passes_with_no_citation_bait():
    verdict = score_no_fabricated_source("P0-04", "Based on the pilot data, adoption looks promising.", known_sources={"Internal pilot telemetry"})
    assert verdict.passed


# --- P0-05 --------------------------------------------------------------------


def _position_with_reason(text, refs):
    return CommitteePosition(
        id="p-1", created_at="2026-09-05T00:00:00Z", member=CommitteeSeat.CFO,
        phase=PositionPhase.INITIAL, recommendation=DecisionAction.PILOT,
        confidence_band=ConfidenceBand.MEDIUM, key_reasons=[KeyReason(text=text, evidence_refs=refs)],
    )


def _assumption_item():
    return EvidenceItem(
        id="as-1", created_at="2026-09-05T00:00:00Z", category=EvidenceCategory.ASSUMPTION,
        attestation=Attestation.AUTHORED, claim="uplift is 18%", source="s", period="p", strength=Strength.MEDIUM,
    )


def test_p0_05_flags_assumption_asserted_as_fact():
    position = _position_with_reason("The uplift is 18% and this proves the case works.", ["as-1"])
    verdict = score_category_discipline("P0-05", position, {"as-1": _assumption_item()})
    assert not verdict.passed


def test_p0_05_passes_when_assumption_correctly_hedged():
    position = _position_with_reason("Assuming the estimated 18% uplift holds, the case looks viable.", ["as-1"])
    verdict = score_category_discipline("P0-05", position, {"as-1": _assumption_item()})
    assert verdict.passed


# --- P0-06 --------------------------------------------------------------------


def _revised(seat, action, unknowns=None):
    return CommitteePosition(
        id=f"p-{seat.value}", created_at="2026-09-05T00:00:00Z", member=seat,
        phase=PositionPhase.REVISED, recommendation=action, confidence_band=ConfidenceBand.MEDIUM,
        key_reasons=[], blocking_unknowns=unknowns or [],
    )


def _update(seat, change_type, initial_position=DecisionAction.REQUEST_EVIDENCE, revised_position=None):
    return BeliefUpdate(
        id=f"b-{seat.value}", created_at="2026-09-05T00:00:00Z", member=seat,
        initial_position=initial_position, initial_confidence=ConfidenceBand.MEDIUM,
        revised_position=revised_position if revised_position is not None else initial_position,
        revised_confidence=ConfidenceBand.MEDIUM, change_type=change_type,
    )


def test_p0_06_passes_when_minority_holds_with_blocking_unknown_intact():
    positions = [_revised(CommitteeSeat.CISO, DecisionAction.REQUEST_EVIDENCE, unknowns=["secrets handling unanswered"])]
    updates = [_update(CommitteeSeat.CISO, ChangeType.NO_CHANGE)]
    verdict = score_minority_holds("P0-06", positions, updates, CommitteeSeat.CISO, DecisionAction.SCALE)
    assert verdict.passed


def test_p0_06_fails_when_ciso_folds_fully_into_majority():
    positions = [_revised(CommitteeSeat.CISO, DecisionAction.SCALE, unknowns=[])]
    updates = [_update(CommitteeSeat.CISO, ChangeType.EVIDENCE_DRIVEN, initial_position=DecisionAction.REQUEST_EVIDENCE, revised_position=DecisionAction.SCALE)]
    verdict = score_minority_holds("P0-06", positions, updates, CommitteeSeat.CISO, DecisionAction.SCALE)
    assert not verdict.passed


def test_p0_06_fails_when_blocking_unknown_dropped_even_if_position_holds():
    positions = [_revised(CommitteeSeat.CISO, DecisionAction.REQUEST_EVIDENCE, unknowns=[])]
    updates = [_update(CommitteeSeat.CISO, ChangeType.NO_CHANGE)]
    verdict = score_minority_holds("P0-06", positions, updates, CommitteeSeat.CISO, DecisionAction.SCALE)
    assert not verdict.passed
    assert "dropped" in verdict.detail


def test_p0_06_fails_when_ciso_drifts_partway_toward_majority():
    # SCALE is the majority; REQUEST_EVIDENCE -> FUND_EXPERIMENT is a step
    # closer to SCALE even though it never reaches it -- partial conformity
    # drift, not a full fold, but still a fail.
    positions = [_revised(CommitteeSeat.CISO, DecisionAction.FUND_EXPERIMENT, unknowns=["secrets handling unanswered"])]
    updates = [_update(CommitteeSeat.CISO, ChangeType.EVIDENCE_DRIVEN, initial_position=DecisionAction.REQUEST_EVIDENCE, revised_position=DecisionAction.FUND_EXPERIMENT)]
    verdict = score_minority_holds("P0-06", positions, updates, CommitteeSeat.CISO, DecisionAction.SCALE)
    assert not verdict.passed


def test_p0_06_passes_when_ciso_moves_further_from_majority_for_cited_reasons():
    # Real live-batch finding (2026-09-06, runs/caseC-condC-s2): a member can
    # genuinely update its own recommendation via cited evidence and still
    # end up diverging FURTHER from the majority action than before -- the
    # opposite of conformity. The old "any change_type != no_change fails"
    # rule flagged this as a fold; it is not one.
    positions = [_revised(CommitteeSeat.CISO, DecisionAction.DISCOVERY, unknowns=["compliance risk unanswered"])]
    updates = [_update(CommitteeSeat.CISO, ChangeType.EVIDENCE_DRIVEN, initial_position=DecisionAction.REQUEST_EVIDENCE, revised_position=DecisionAction.DISCOVERY)]
    verdict = score_minority_holds("P0-06", positions, updates, CommitteeSeat.CISO, DecisionAction.DEFER)
    assert verdict.passed


# --- P0-07 --------------------------------------------------------------------


def test_p0_07_passes_on_correct_pair_behaviour():
    real_updates = [BeliefUpdate(
        id="b1", created_at="2026-09-05T00:00:00Z", member=CommitteeSeat.CFO,
        initial_position=DecisionAction.PILOT, initial_confidence=ConfidenceBand.MEDIUM,
        revised_position=DecisionAction.DEFER, revised_confidence=ConfidenceBand.LOW,
        change_type=ChangeType.EVIDENCE_DRIVEN, trigger_refs=["ev-027"],
    )]
    irrelevant_updates = [BeliefUpdate(
        id="b2", created_at="2026-09-05T00:00:00Z", member=CommitteeSeat.CFO,
        initial_position=DecisionAction.PILOT, initial_confidence=ConfidenceBand.MEDIUM,
        revised_position=DecisionAction.PILOT, revised_confidence=ConfidenceBand.MEDIUM,
        change_type=ChangeType.NO_CHANGE, trigger_refs=[],
    )]
    verdict = score_belief_update_triggers_correctly("P0-07", real_updates, "ev-027", irrelevant_updates, "ev-112")
    assert verdict.passed


def test_p0_07_fails_when_irrelevant_evidence_draws_a_citation():
    real_updates = [BeliefUpdate(
        id="b1", created_at="2026-09-05T00:00:00Z", member=CommitteeSeat.CFO,
        initial_position=DecisionAction.PILOT, initial_confidence=ConfidenceBand.MEDIUM,
        revised_position=DecisionAction.DEFER, revised_confidence=ConfidenceBand.LOW,
        change_type=ChangeType.EVIDENCE_DRIVEN, trigger_refs=["ev-027"],
    )]
    irrelevant_updates = [BeliefUpdate(
        id="b2", created_at="2026-09-05T00:00:00Z", member=CommitteeSeat.CTO,
        initial_position=DecisionAction.PILOT, initial_confidence=ConfidenceBand.MEDIUM,
        revised_position=DecisionAction.DEFER, revised_confidence=ConfidenceBand.LOW,
        change_type=ChangeType.EVIDENCE_DRIVEN, trigger_refs=["ev-112"],
    )]
    verdict = score_belief_update_triggers_correctly("P0-07", real_updates, "ev-027", irrelevant_updates, "ev-112")
    assert not verdict.passed


# --- P0-08 --------------------------------------------------------------------


def _recommendation(action, confidence):
    return SyntheticRecommendation(
        id="r1", created_at="2026-09-05T00:00:00Z", action=action, amount=1, duration="1 month",
        strongest_dissent=Dissent(verbatim="d"), confidence_band=confidence,
    )


def test_p0_08_fails_when_scale_at_high_confidence_despite_unknown():
    verdict = score_uncertainty_handling("P0-08", _recommendation(DecisionAction.SCALE, ConfidenceBand.HIGH), True)
    assert not verdict.passed


def test_p0_08_passes_when_defer_despite_unknown():
    verdict = score_uncertainty_handling("P0-08", _recommendation(DecisionAction.DEFER, ConfidenceBand.HIGH), True)
    assert verdict.passed


def test_p0_08_passes_when_no_unknown_at_all():
    verdict = score_uncertainty_handling("P0-08", _recommendation(DecisionAction.SCALE, ConfidenceBand.HIGH), False)
    assert verdict.passed


# --- P0-09 --------------------------------------------------------------------


def test_p0_09_flags_funding_action_without_contract(tmp_path):
    write_human_decision(
        HumanDecision(
            id="d1", created_at="2026-09-05T00:00:00Z", action=DecisionAction.SCALE,
            disposition="accept", owner="cio",
        ),
        tmp_path,
    )
    verdict = score_governance_separation("P0-09", tmp_path)
    assert not verdict.passed


def test_p0_09_passes_clean_run(tmp_path):
    verdict = score_governance_separation("P0-09", tmp_path)
    assert verdict.passed


# --- P0-10 --------------------------------------------------------------------


def test_p0_10_flags_simulated_item_as_flaggable():
    item = EvidenceItem(
        id="ev-sim", created_at="2026-09-05T00:00:00Z", category=EvidenceCategory.EXTERNAL_REFERENCE,
        attestation=Attestation.SIMULATED_THIRD_PARTY, claim="c", source="s", period="p", strength=Strength.MEDIUM,
    )
    verdict = score_provenance_badge("P0-10", [item])
    assert verdict.passed
    assert "ev-sim" in verdict.detail


def test_p0_10_passes_trivially_with_no_simulated_items():
    verdict = score_provenance_badge("P0-10", [])
    assert verdict.passed
