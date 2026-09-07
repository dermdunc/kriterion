from kriterion.domain.case import Ask, DecisionCase
from kriterion.domain.committee import Challenge, CommitteePosition, KeyReason
from kriterion.domain.enums import ChallengeType, CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase
from kriterion.executors.base import Executor, ExecutorResult
from kriterion.protocol.chair import synthesize


class _FixedExecutor(Executor):
    def __init__(self, text="A brief narrative paragraph."):
        self._text = text
        self.last_prompt = None

    def complete(self, prompt, *, system=None, fmt="json", seed=0):
        self.last_prompt = prompt
        return ExecutorResult(text=self._text, elapsed_seconds=0.01, model="fake", seed=seed)


def _position(seat, action, unknowns=None):
    return CommitteePosition(
        id=f"p-{seat.value}", created_at="2026-09-05T00:00:00Z", member=seat,
        phase=PositionPhase.REVISED, recommendation=action, confidence_band=ConfidenceBand.MEDIUM,
        key_reasons=[KeyReason(text="reason", evidence_refs=[])], blocking_unknowns=unknowns or [],
    )


def _case():
    return DecisionCase(
        id="case-a", created_at="2026-09-05T00:00:00Z", title="t", sponsor="s", decision_owner="o",
        decision_requested="d", ask=Ask(type="staged_funding", amount_gbp=1, duration="1 month"),
        alternatives=["do_nothing", "pilot"],
    )


def _fallback_case_against():
    return Challenge(
        id="ch:case_against-cfo", created_at="2026-09-05T00:00:00Z", type=ChallengeType.CASE_AGAINST,
        author_role=CommitteeSeat.CFO, content="Fallback dissent under unanimity.", evidence_refs=[],
    )


def test_dissent_is_a_real_minority_position_when_one_exists():
    positions = [
        _position(CommitteeSeat.CFO, DecisionAction.PILOT),
        _position(CommitteeSeat.CTO, DecisionAction.PILOT),
        _position(CommitteeSeat.CRO_COMPLIANCE, DecisionAction.PILOT),
        _position(CommitteeSeat.CISO, DecisionAction.STOP, unknowns=["secrets handling"]),
        _position(CommitteeSeat.BUSINESS_EXECUTIVE, DecisionAction.PILOT),
    ]
    executor = _FixedExecutor()
    result = synthesize(
        executor, _case(), positions, _fallback_case_against(),
        seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert result.recommendation.action == DecisionAction.PILOT
    assert "ciso" in result.recommendation.strongest_dissent.verbatim.lower()
    assert result.recommendation.strongest_dissent.verbatim.strip()


def test_dissent_falls_back_to_case_against_under_unanimity():
    positions = [_position(seat, DecisionAction.PILOT) for seat in CommitteeSeat if seat != CommitteeSeat.BASELINE_A]
    executor = _FixedExecutor()
    result = synthesize(
        executor, _case(), positions, _fallback_case_against(),
        seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert result.recommendation.strongest_dissent.verbatim == "Fallback dissent under unanimity."
    assert result.recommendation.strongest_dissent.verbatim.strip()  # still non-empty


def test_narrative_is_captured_but_not_part_of_the_recommendation_object():
    positions = [_position(seat, DecisionAction.PILOT) for seat in CommitteeSeat if seat != CommitteeSeat.BASELINE_A]
    executor = _FixedExecutor(text="Executive summary paragraph.")
    result = synthesize(
        executor, _case(), positions, _fallback_case_against(),
        seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert result.narrative == "Executive summary paragraph."
    assert not hasattr(result.recommendation, "narrative")


def test_conditions_are_the_union_of_blocking_unknowns():
    positions = [
        _position(CommitteeSeat.CFO, DecisionAction.PILOT, unknowns=["a"]),
        _position(CommitteeSeat.CTO, DecisionAction.PILOT, unknowns=["b"]),
        _position(CommitteeSeat.CISO, DecisionAction.PILOT, unknowns=["a"]),
        _position(CommitteeSeat.CRO_COMPLIANCE, DecisionAction.PILOT),
        _position(CommitteeSeat.BUSINESS_EXECUTIVE, DecisionAction.PILOT),
    ]
    executor = _FixedExecutor()
    result = synthesize(
        executor, _case(), positions, _fallback_case_against(),
        seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert result.recommendation.conditions == ["a", "b"]
