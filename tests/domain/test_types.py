import pytest

from kriterion.domain import (
    Ask,
    CommitteePosition,
    CommitteeSeat,
    ConfidenceBand,
    DecisionAction,
    DecisionCase,
    Dissent,
    KeyReason,
    PositionPhase,
    SyntheticRecommendation,
)


def test_decision_case_requires_at_least_two_alternatives():
    with pytest.raises(ValueError, match="at least 2"):
        DecisionCase(
            id="c1",
            created_at="2026-09-05T00:00:00Z",
            title="t",
            sponsor="s",
            decision_owner="o",
            decision_requested="d",
            ask=Ask(type="staged_funding", amount_gbp=1, duration="1 month"),
            alternatives=["do_nothing"],
        )


def test_decision_case_requires_do_nothing_alternative():
    with pytest.raises(ValueError, match="do_nothing"):
        DecisionCase(
            id="c1",
            created_at="2026-09-05T00:00:00Z",
            title="t",
            sponsor="s",
            decision_owner="o",
            decision_requested="d",
            ask=Ask(type="staged_funding", amount_gbp=1, duration="1 month"),
            alternatives=["pilot", "full_rollout"],
        )


def test_decision_case_not_normalisable_skips_alternatives_check():
    case = DecisionCase(
        id="c1",
        created_at="2026-09-05T00:00:00Z",
        title="t",
        sponsor="s",
        decision_owner="o",
        decision_requested="d",
        ask=Ask(type="staged_funding", amount_gbp=1, duration="1 month"),
        alternatives=[],
        not_normalisable=True,
    )
    assert case.not_normalisable is True


def test_committee_position_key_reasons_capped_at_three():
    with pytest.raises(ValueError, match="at most 3"):
        CommitteePosition(
            id="p1",
            created_at="2026-09-05T00:00:00Z",
            member=CommitteeSeat.CFO,
            phase=PositionPhase.INITIAL,
            recommendation=DecisionAction.PILOT,
            confidence_band=ConfidenceBand.MEDIUM,
            key_reasons=[KeyReason(text=str(i)) for i in range(4)],
        )


def test_synthetic_recommendation_requires_non_empty_dissent():
    with pytest.raises(ValueError, match="non-empty"):
        SyntheticRecommendation(
            id="r1",
            created_at="2026-09-05T00:00:00Z",
            action=DecisionAction.PILOT,
            amount=1000,
            duration="6 months",
            strongest_dissent=Dissent(verbatim="   "),
        )


def test_synthetic_recommendation_accepts_real_dissent():
    rec = SyntheticRecommendation(
        id="r1",
        created_at="2026-09-05T00:00:00Z",
        action=DecisionAction.PILOT,
        amount=1000,
        duration="6 months",
        strongest_dissent=Dissent(verbatim="CISO: secrets handling unanswered", refs=["ev-1"]),
    )
    assert rec.strongest_dissent.verbatim
