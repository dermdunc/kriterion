"""The decision-state projection (ADR-011).

Most of these tests are about *absence*. The projection's job is to make one
authoritative state renderable without ever letting a missing artifact quietly
become a zero, a False, or a reassuring default — which is the failure mode the
adapter hardening (ADR-009) closed on the import side and this closes on the
read side.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent

from kriterion.decision_state import (
    DecisionState,
    DecisionStateError,
    SeatView,
    load_assurance_import,
    load_decision_state,
)
from kriterion.domain.case import Ask, DecisionCase
from kriterion.domain.committee import CommitteePosition, KeyReason
from kriterion.domain.decision import Dissent, HumanDecision, SyntheticRecommendation
from kriterion.domain.economics import EconomicsResult, TornadoEntry
from kriterion.domain.enums import CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase
from kriterion.domain.evidence import Assumption, Attestation, EvidenceCategory, EvidenceItem, Strength
from kriterion.evals.run_loader import load_evidence_request

AT = "2026-01-01T00:00:00Z"


def _case(case_id="coding-agent-rollout"):
    return DecisionCase(
        id=case_id,
        created_at=AT,
        title="Fixture",
        sponsor="cto",
        decision_owner="cio",
        decision_requested="Should we?",
        ask=Ask(type="staged_funding", amount_gbp=4_200_000.0, duration="24 months"),
        alternatives=["do_nothing", "limited_pilot"],
    )


def _recommendation(action: DecisionAction):
    return SyntheticRecommendation(
        id="rec",
        created_at=AT,
        action=action,
        amount=4_200_000.0,
        duration="24 months",
        strongest_dissent=Dissent(verbatim="Not yet."),
    )


def _economics(**kw):
    base = dict(
        id="e",
        created_at=AT,
        case_id="coding-agent-rollout",
        discount_rate=0.10,
        npv_low_gbp=-5_000_000.0,
        npv_mid_gbp=5_000_000.0,
        npv_high_gbp=38_000_000.0,
        payback_years=None,
        peak_funding_gbp=0.0,
        tornado=[
            TornadoEntry(assumption_id="attribution_factor", npv_swing_gbp=16_000_000.0),
            TornadoEntry(assumption_id="uplift", npv_swing_gbp=-17_000_000.0),
        ],
    )
    base.update(kw)
    return EconomicsResult(**base)


def _state(**overrides) -> DecisionState:
    defaults = dict(
        run_id="r",
        case=_case(),
        assumptions=[
            Assumption(
                id="as-benefit-attribution-factor",
                created_at=AT,
                value=0.10,
                range=(0.05, 0.20),
                evidence_strength=Strength.LOW,
                owner="cfo",
            )
        ],
        evidence=[
            EvidenceItem(
                id="ev-001",
                created_at=AT,
                category=EvidenceCategory.UNKNOWN,
                attestation=Attestation.AUTHORED,
                claim="Unknown.",
                source="s",
                period="p",
                strength=Strength.LOW,
            )
        ],
        economics=_economics(),
        seats=[],
        recommendation=_recommendation(DecisionAction.DEFER),
        human_decision=None,
        outcome_contract=None,
        assurance=None,
        ledger_version=1,
        ledger_fingerprint="f",
        evidence_requests_recorded=False,
    )
    defaults.update(overrides)
    return DecisionState(**defaults)


# ---------------------------------------------------------------------------
# Capital at risk
# ---------------------------------------------------------------------------


def test_a_non_funding_action_puts_no_capital_at_risk():
    """The synthesiser echoes the full ask into the recommendation's amount
    field even when the action commits nothing. Presenting that as capital at
    risk would misstate a DEFER as a spend."""
    state = _state()
    assert state.recommendation.amount == 4_200_000.0
    assert state.capital_at_risk_gbp == 0.0
    assert "commits no funding" in state.capital_at_risk_basis


@pytest.mark.parametrize(
    "action", [DecisionAction.PILOT, DecisionAction.SCALE, DecisionAction.FUND_EXPERIMENT, DecisionAction.REDUCE]
)
def test_a_funding_action_does_put_the_recommended_amount_at_risk(action):
    state = _state(recommendation=_recommendation(action))
    assert state.capital_at_risk_gbp == 4_200_000.0
    assert "funding action" in state.capital_at_risk_basis


def test_no_recommendation_means_no_capital_and_says_so():
    state = _state(recommendation=None)
    assert state.capital_at_risk_gbp == 0.0
    assert "No synthetic recommendation" in state.capital_at_risk_basis


# ---------------------------------------------------------------------------
# Sensitivity naming and ordering
# ---------------------------------------------------------------------------


def test_the_dominant_sensitivity_is_ranked_by_magnitude_not_sign():
    state = _state()
    assert state.primary_sensitivity_param == "uplift"  # -17m beats +16m
    assert state.primary_sensitivity_swing_gbp == -17_000_000.0


def test_the_dominant_uncertainty_has_one_name_used_everywhere():
    """The economics artifact stores the engine parameter; the case pack
    stores the assumption id. Quoting one in the headline and the other in the
    interpretation is how one fact looks like two."""
    state = _state(
        economics=_economics(
            tornado=[TornadoEntry(assumption_id="attribution_factor", npv_swing_gbp=16_000_000.0)]
        )
    )
    assert state.primary_uncertainty_label == "as-benefit-attribution-factor"
    assert state.primary_uncertainty_label in state.economics_interpretation


def test_an_unmapped_parameter_falls_back_to_the_parameter_name_not_a_guess():
    state = _state(
        economics=_economics(tornado=[TornadoEntry(assumption_id="mystery_param", npv_swing_gbp=1.0)])
    )
    assert state.primary_uncertainty_label == "mystery_param"
    assert state.tornado_rows[0]["assumption_id"] == "not declared as a ranged assumption"
    assert state.tornado_rows[0]["evidence_strength"] == "not recorded"


def test_the_tornado_rows_carry_the_evidence_strength_behind_each_swing():
    rows = _state().tornado_rows
    attribution = next(r for r in rows if r["parameter"] == "attribution_factor")
    assert attribution["assumption_id"] == "as-benefit-attribution-factor"
    assert attribution["evidence_strength"] == "LOW"
    assert attribution["owner"] == "cfo"


def test_the_tornado_rows_are_ordered_by_magnitude_and_agree_with_the_headline():
    """The fixture's stored tornado has the smaller swing first. Rows are
    ordered by magnitude so the table's "widest first" caption is true, and so
    the headline dominant uncertainty and the first row name one thing."""
    state = _state()
    magnitudes = [abs(r["swing_gbp"]) for r in state.tornado_rows]
    assert magnitudes == sorted(magnitudes, reverse=True)
    assert state.tornado_rows[0]["parameter"] == state.primary_sensitivity_param


# ---------------------------------------------------------------------------
# Absence stays absence
# ---------------------------------------------------------------------------


def test_missing_economics_leaves_the_sign_question_unknown_not_false():
    state = _state(economics=None)
    assert state.npv_sign_flips is None
    assert state.primary_sensitivity_param is None
    assert "No economics" in state.economics_interpretation


def test_no_evidence_request_artifact_is_distinguishable_from_nobody_asking():
    predates = _state(evidence_requests_recorded=False)
    asked_nothing = _state(evidence_requests_recorded=True)
    assert "predates" in predates.evidence_request_status
    assert "no seat asked" in asked_nothing.evidence_request_status
    assert predates.evidence_request_status != asked_nothing.evidence_request_status


def test_the_outcome_contract_status_distinguishes_all_four_real_states():
    none_yet = _state()
    assert "no human decision has been recorded" in none_yet.outcome_contract_status.lower()

    non_funding = _state(
        human_decision=HumanDecision(
            id="h", created_at=AT, action=DecisionAction.DEFER, disposition="accept"
        )
    )
    assert "commits no" in non_funding.outcome_contract_status

    funding_without_contract = _state(
        human_decision=HumanDecision(
            id="h", created_at=AT, action=DecisionAction.PILOT, disposition="modify"
        )
    )
    assert "governance violation" in funding_without_contract.outcome_contract_status


def test_the_next_step_names_the_accountable_party_when_nothing_is_recorded():
    state = _state()
    assert "cio" in state.next_step
    assert "kriterion decide" in state.next_step


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def test_a_run_without_a_frozen_ledger_is_refused_not_rendered_empty(tmp_path):
    run_dir = tmp_path / "runs" / "r"
    run_dir.mkdir(parents=True)
    with pytest.raises(DecisionStateError, match="ledger"):
        load_decision_state(
            case_dir=REPO_ROOT / "cases" / "coding-agent-rollout",
            run_dir=run_dir,
            created_at=AT,
        )


def test_a_missing_case_pack_is_refused(tmp_path):
    run_dir = tmp_path / "runs" / "r"
    run_dir.mkdir(parents=True)
    with pytest.raises(DecisionStateError, match="case.toml"):
        load_decision_state(case_dir=tmp_path / "nope", run_dir=run_dir, created_at=AT)


def test_a_missing_run_directory_is_refused(tmp_path):
    with pytest.raises(DecisionStateError, match="run directory"):
        load_decision_state(case_dir=tmp_path, run_dir=tmp_path / "absent", created_at=AT)


@pytest.mark.parametrize(
    "mutate,expected",
    [
        (lambda d: d.pop("summary"), "summary"),
        (lambda d: d["summary"].pop("decision_state"), "decision_state"),
        (lambda d: d.pop("items"), "items"),
    ],
)
def test_a_malformed_assurance_payload_is_refused_not_half_read(tmp_path, mutate, expected):
    payload = {
        "summary": {
            "capability_name": "c",
            "capability_version": "1",
            "decision_state": "FAIL",
            "declared_decision_state": "FAIL",
            "stale": False,
            "critical_failure_count": 1,
            "result_count": 1,
            "uncovered_count": 0,
        },
        "items": [],
    }
    mutate(payload)
    path = tmp_path / "imported.json"
    path.write_text(json.dumps(payload))
    with pytest.raises(DecisionStateError, match=expected):
        load_assurance_import(path)


def test_an_evidence_request_without_would_change_is_refused():
    """A blank `would_change` renders as "nothing would move this seat",
    which is the strongest possible claim and the least evidenced one."""
    with pytest.raises(KeyError):
        load_evidence_request(
            {"id": "er", "created_at": AT, "member": "cfo", "description": "d"}
        )


def test_seats_appear_in_a_fixed_order_and_only_when_they_recorded_something():
    def position(seat):
        return CommitteePosition(
            id=f"p-{seat.value}",
            created_at=AT,
            member=seat,
            phase=PositionPhase.INITIAL,
            recommendation=DecisionAction.DEFER,
            confidence_band=ConfidenceBand.MEDIUM,
            key_reasons=[KeyReason(text="t")],
        )

    state = _state(
        seats=[
            SeatView(seat=CommitteeSeat.CISO, initial=position(CommitteeSeat.CISO)),
            SeatView(seat=CommitteeSeat.CFO, initial=position(CommitteeSeat.CFO)),
        ]
    )
    assert set(state.seats_by_id) == {"ciso", "cfo"}
    assert state.seats_by_id["cfo"].current_position.member is CommitteeSeat.CFO


def test_current_position_prefers_the_revision_and_never_blends_the_two():
    initial = CommitteePosition(
        id="i", created_at=AT, member=CommitteeSeat.CFO, phase=PositionPhase.INITIAL,
        recommendation=DecisionAction.REJECT, confidence_band=ConfidenceBand.LOW,
        key_reasons=[KeyReason(text="t")],
    )
    revised = CommitteePosition(
        id="r", created_at=AT, member=CommitteeSeat.CFO, phase=PositionPhase.REVISED,
        recommendation=DecisionAction.DEFER, confidence_band=ConfidenceBand.HIGH,
        key_reasons=[KeyReason(text="t")],
    )
    view = SeatView(seat=CommitteeSeat.CFO, initial=initial, revised=revised)
    assert view.current_position is revised
    assert SeatView(seat=CommitteeSeat.CFO, initial=initial).current_position is initial


# ---------------------------------------------------------------------------
# The error boundary: a traceback is not a refusal
# ---------------------------------------------------------------------------

# Found by an adversarial pass over this module rather than by review: every
# one of these produced a bare KeyError/TypeError/ValueError before the
# boundary existed — the same shape the V1 review found in the assurance
# adapter, reproduced here. "Unknown" has to stay distinguishable from
# "crashed", and a user-supplied artifact error must be a controlled refusal.
MALFORMED_ARTIFACTS = {
    "ledger missing items": ("ledger.frozen.json", lambda d: {"version": 1}),
    "ledger items is a dict": ("ledger.frozen.json", lambda d: {**d, "items": {"a": 1}}),
    "ledger is a JSON array": ("ledger.frozen.json", lambda d: [1, 2, 3]),
    "evidence item missing claim": (
        "ledger.frozen.json",
        lambda d: {**d, "items": [{k: v for k, v in d["items"][0].items() if k != "claim"}]},
    ),
    "evidence has an unknown category": (
        "ledger.frozen.json",
        lambda d: {**d, "items": [{**d["items"][0], "category": "TOTALLY_FINE"}]},
    ),
    "positions written as an object": ("positions_initial.json", lambda d: {"cfo": "DEFER"}),
    "position has an action outside the vocabulary": (
        "positions_initial.json",
        lambda d: [{**d[0], "recommendation": "APPROVE"}],
    ),
    "position key_reasons is a string": (
        "positions_initial.json",
        lambda d: [{**d[0], "key_reasons": "none"}],
    ),
    "evidence_requests written as an object": ("evidence_requests.json", lambda d: {"cfo": "x"}),
    "evidence request has no would_change": (
        "evidence_requests.json",
        lambda d: [{k: v for k, v in d[0].items() if k != "would_change"}],
    ),
    "recommendation has no dissent": (
        "recommendation.json",
        lambda d: {k: v for k, v in d.items() if k != "strongest_dissent"},
    ),
    "recommendation written as an array": ("recommendation.json", lambda d: [d]),
    "economics missing a headline figure": (
        "economics.json",
        lambda d: {k: v for k, v in d.items() if k != "npv_mid_gbp"},
    ),
    "economics written as a string": ("economics.json", lambda d: "fine"),
    "belief update has an unknown change type": (
        "belief_updates.json",
        lambda d: [{**d[0], "change_type": "vibes"}],
    ),
    "belief update has an unknown drift flag": (
        "belief_updates.json",
        lambda d: [{**d[0], "drift_flags": ["nope"]}],
    ),
}


@pytest.mark.parametrize("name", sorted(MALFORMED_ARTIFACTS))
def test_a_malformed_run_artifact_is_a_controlled_refusal_never_a_traceback(tmp_path, name):
    import shutil

    filename, mutate = MALFORMED_ARTIFACTS[name]
    run_dir = tmp_path / "run"
    shutil.copytree(REPO_ROOT / "runs" / "caseA-condC-s5", run_dir)
    path = run_dir / filename
    path.write_text(json.dumps(mutate(json.loads(path.read_text()))))

    with pytest.raises(DecisionStateError):
        load_decision_state(
            case_dir=REPO_ROOT / "cases" / "coding-agent-rollout",
            run_dir=run_dir,
            created_at=AT,
        )


def test_malformed_json_is_a_refusal_too(tmp_path):
    import shutil

    run_dir = tmp_path / "run"
    shutil.copytree(REPO_ROOT / "runs" / "caseA-condC-s5", run_dir)
    (run_dir / "economics.json").write_text("{not json")
    with pytest.raises(DecisionStateError, match="not valid JSON"):
        load_decision_state(
            case_dir=REPO_ROOT / "cases" / "coding-agent-rollout",
            run_dir=run_dir,
            created_at=AT,
        )
