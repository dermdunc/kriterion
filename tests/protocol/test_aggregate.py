from kriterion.domain.committee import CommitteePosition
from kriterion.domain.enums import CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase
from kriterion.protocol.aggregate import aggregate_baseline_b


def _position(seat, action, unknowns=None):
    return CommitteePosition(
        id=f"p-{seat.value}",
        created_at="2026-09-05T00:00:00Z",
        member=seat,
        phase=PositionPhase.INITIAL,
        recommendation=action,
        confidence_band=ConfidenceBand.MEDIUM,
        key_reasons=[],
        blocking_unknowns=unknowns or [],
    )


def test_modal_action_wins_outright():
    positions = [
        _position(CommitteeSeat.CFO, DecisionAction.PILOT),
        _position(CommitteeSeat.CTO, DecisionAction.PILOT),
        _position(CommitteeSeat.CISO, DecisionAction.PILOT),
        _position(CommitteeSeat.CRO_COMPLIANCE, DecisionAction.DEFER),
        _position(CommitteeSeat.BUSINESS_EXECUTIVE, DecisionAction.SCALE),
    ]
    result = aggregate_baseline_b(positions)
    assert result.modal_action == DecisionAction.PILOT
    assert result.modal_action_count == 3
    assert len(result.minority_positions) == 2


def test_tie_breaks_to_the_more_conservative_action():
    # 2x PILOT, 2x SCALE, 1x DEFER -> PILOT and SCALE tied at 2; PILOT is
    # more conservative than SCALE per CONSERVATISM_ORDER.
    positions = [
        _position(CommitteeSeat.CFO, DecisionAction.PILOT),
        _position(CommitteeSeat.CTO, DecisionAction.PILOT),
        _position(CommitteeSeat.CISO, DecisionAction.SCALE),
        _position(CommitteeSeat.CRO_COMPLIANCE, DecisionAction.SCALE),
        _position(CommitteeSeat.BUSINESS_EXECUTIVE, DecisionAction.DEFER),
    ]
    result = aggregate_baseline_b(positions)
    assert result.modal_action == DecisionAction.PILOT


def test_unions_blocking_unknowns_without_duplicates():
    positions = [
        _position(CommitteeSeat.CFO, DecisionAction.PILOT, unknowns=["a", "b"]),
        _position(CommitteeSeat.CTO, DecisionAction.PILOT, unknowns=["b", "c"]),
    ]
    result = aggregate_baseline_b(positions)
    assert result.unioned_blocking_unknowns == ["a", "b", "c"]


def test_minority_positions_preserved_verbatim():
    minority = _position(CommitteeSeat.CISO, DecisionAction.DEFER, unknowns=["secrets handling"])
    positions = [
        _position(CommitteeSeat.CFO, DecisionAction.PILOT),
        _position(CommitteeSeat.CTO, DecisionAction.PILOT),
        _position(CommitteeSeat.CRO_COMPLIANCE, DecisionAction.PILOT),
        minority,
    ]
    result = aggregate_baseline_b(positions)
    assert result.minority_positions == [minority]
    assert result.minority_positions[0].blocking_unknowns == ["secrets handling"]
