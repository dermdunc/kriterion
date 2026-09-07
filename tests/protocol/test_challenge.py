from kriterion.domain.case import Ask, DecisionCase
from kriterion.domain.committee import CommitteePosition, KeyReason, RoleCharter
from kriterion.domain.economics import EconomicsResult
from kriterion.domain.enums import CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase
from kriterion.executors.base import Executor, ExecutorResult
from kriterion.protocol.challenge import most_and_least_favourable, run_phase5_challenge


class _SequentialExecutor(Executor):
    def __init__(self):
        self.call_count = 0

    def complete(self, prompt, *, system=None, fmt="json", seed=0):
        self.call_count += 1
        return ExecutorResult(text=f"Response {self.call_count}, citing ev-001.", elapsed_seconds=0.01, model="fake", seed=seed)


def _position(seat, action):
    return CommitteePosition(
        id=f"p-{seat.value}", created_at="2026-09-05T00:00:00Z", member=seat,
        phase=PositionPhase.INITIAL, recommendation=action, confidence_band=ConfidenceBand.MEDIUM,
        key_reasons=[KeyReason(text="r", evidence_refs=[])],
    )


def test_most_and_least_favourable_by_conservatism():
    positions = [
        _position(CommitteeSeat.CFO, DecisionAction.SCALE),  # most favourable
        _position(CommitteeSeat.CTO, DecisionAction.PILOT),
        _position(CommitteeSeat.CISO, DecisionAction.STOP),  # least favourable
        _position(CommitteeSeat.CRO_COMPLIANCE, DecisionAction.DEFER),
        _position(CommitteeSeat.BUSINESS_EXECUTIVE, DecisionAction.DISCOVERY),
    ]
    most, least = most_and_least_favourable(positions)
    assert most.member == CommitteeSeat.CFO
    assert least.member == CommitteeSeat.CISO


def test_perspective_inversion_assigns_case_for_to_least_favourable():
    positions = [
        _position(CommitteeSeat.CFO, DecisionAction.SCALE),
        _position(CommitteeSeat.CTO, DecisionAction.PILOT),
        _position(CommitteeSeat.CISO, DecisionAction.STOP),
        _position(CommitteeSeat.CRO_COMPLIANCE, DecisionAction.DEFER),
        _position(CommitteeSeat.BUSINESS_EXECUTIVE, DecisionAction.DISCOVERY),
    ]
    charters = {
        seat: RoleCharter(
            id=f"charter-{seat.value}", created_at="2026-09-05T00:00:00Z", version="v1", seat=seat,
            objective="o", concerns=["c"], required_evidence=["ev-001"], decision_rights=["d"],
            standard_challenges=["s"], failure_modes=["f"], forbidden=["x"],
        )
        for seat in [CommitteeSeat.CFO, CommitteeSeat.CTO, CommitteeSeat.CISO, CommitteeSeat.CRO_COMPLIANCE, CommitteeSeat.BUSINESS_EXECUTIVE]
    }
    case = DecisionCase(
        id="case-a", created_at="2026-09-05T00:00:00Z", title="t", sponsor="s", decision_owner="o",
        decision_requested="d", ask=Ask(type="staged_funding", amount_gbp=1, duration="1 month"),
        alternatives=["do_nothing", "pilot"],
    )
    economics = EconomicsResult(
        id="econ", created_at="2026-09-05T00:00:00Z", case_id="case-a", discount_rate=0.1,
        npv_low_gbp=-1.0, npv_mid_gbp=1.0, npv_high_gbp=2.0, payback_years=1.0,
        peak_funding_gbp=0.0, tornado=[],
    )
    executor = _SequentialExecutor()

    result = run_phase5_challenge(
        executor, case, [], economics, positions, charters,
        seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )

    assert result.case_for.author_role == CommitteeSeat.CISO  # least favourable
    assert result.case_against.author_role == CommitteeSeat.CFO  # most favourable
    assert len(result.premortems) == 5
    assert executor.call_count == 2 + 5  # case_for + case_against + one premortem per member


class _TaggedExecutor(Executor):
    """Records its own tag on every call it handles, so a test can verify
    WHICH executor actually served a given prompt (Treatment D: one model
    per seat)."""

    def __init__(self, tag):
        self.tag = tag
        self.calls = 0

    def complete(self, prompt, *, system=None, fmt="json", seed=0):
        self.calls += 1
        return ExecutorResult(text=f"[{self.tag}] response, citing ev-001.", elapsed_seconds=0.01, model=self.tag, seed=seed)


def test_executor_by_seat_routes_each_call_to_that_seats_own_executor():
    positions = [
        _position(CommitteeSeat.CFO, DecisionAction.SCALE),  # most favourable
        _position(CommitteeSeat.CTO, DecisionAction.PILOT),
        _position(CommitteeSeat.CISO, DecisionAction.STOP),  # least favourable
        _position(CommitteeSeat.CRO_COMPLIANCE, DecisionAction.DEFER),
        _position(CommitteeSeat.BUSINESS_EXECUTIVE, DecisionAction.DISCOVERY),
    ]
    seats = [CommitteeSeat.CFO, CommitteeSeat.CTO, CommitteeSeat.CISO, CommitteeSeat.CRO_COMPLIANCE, CommitteeSeat.BUSINESS_EXECUTIVE]
    charters = {
        seat: RoleCharter(
            id=f"charter-{seat.value}", created_at="2026-09-05T00:00:00Z", version="v1", seat=seat,
            objective="o", concerns=["c"], required_evidence=["ev-001"], decision_rights=["d"],
            standard_challenges=["s"], failure_modes=["f"], forbidden=["x"],
        )
        for seat in seats
    }
    case = DecisionCase(
        id="case-a", created_at="2026-09-05T00:00:00Z", title="t", sponsor="s", decision_owner="o",
        decision_requested="d", ask=Ask(type="staged_funding", amount_gbp=1, duration="1 month"),
        alternatives=["do_nothing", "pilot"],
    )
    economics = EconomicsResult(
        id="econ", created_at="2026-09-05T00:00:00Z", case_id="case-a", discount_rate=0.1,
        npv_low_gbp=-1.0, npv_mid_gbp=1.0, npv_high_gbp=2.0, payback_years=1.0,
        peak_funding_gbp=0.0, tornado=[],
    )
    executor_by_seat = {seat: _TaggedExecutor(seat.value) for seat in seats}

    result = run_phase5_challenge(
        None, case, [], economics, positions, charters,
        seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
        executor_by_seat=executor_by_seat,
    )

    assert f"[{CommitteeSeat.CISO.value}]" in result.case_for.content  # least favourable authors case_for
    assert f"[{CommitteeSeat.CFO.value}]" in result.case_against.content  # most favourable authors case_against
    for premortem in result.premortems:
        assert f"[{premortem.author_role.value}]" in premortem.content  # each premortem uses its own member's model
    for seat, executor in executor_by_seat.items():
        assert executor.calls >= 1, f"{seat.value}'s own executor was never used"
