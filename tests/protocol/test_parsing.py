import json

import pytest

from kriterion.domain.committee import CommitteePosition
from kriterion.domain.enums import CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase
from kriterion.protocol.parsing import ResponseParsingError, parse_position_response, parse_revision_response

VALID_RESPONSE = json.dumps(
    {
        "recommendation": "PILOT",
        "confidence_band": "MEDIUM",
        "key_reasons": [{"text": "Pilot data is strong", "evidence_refs": ["ev-001"]}],
        "blocking_unknowns": ["benefits attribution method"],
        "distrusted_assumption": None,
        "evidence_requests": [{"description": "Need scale data", "would_change": "confidence"}],
    }
)


def test_parses_a_valid_response():
    position, requests = parse_position_response(
        VALID_RESPONSE,
        member=CommitteeSeat.CFO,
        phase=PositionPhase.INITIAL,
        known_evidence_ids={"ev-001"},
        created_at="2026-09-05T00:00:00Z",
        id_prefix="run-1",
    )
    assert position.recommendation.value == "PILOT"
    assert position.member == CommitteeSeat.CFO
    assert len(requests) == 1
    assert requests[0].description == "Need scale data"


def test_rejects_non_json():
    with pytest.raises(ResponseParsingError, match="not valid JSON"):
        parse_position_response(
            "not json at all",
            member=CommitteeSeat.CFO,
            phase=PositionPhase.INITIAL,
            known_evidence_ids=set(),
            created_at="2026-09-05T00:00:00Z",
            id_prefix="run-1",
        )


def test_rejects_invalid_recommendation():
    bad = json.dumps({"recommendation": "MAYBE", "confidence_band": "MEDIUM", "key_reasons": []})
    with pytest.raises(ResponseParsingError, match="invalid recommendation"):
        parse_position_response(
            bad,
            member=CommitteeSeat.CFO,
            phase=PositionPhase.INITIAL,
            known_evidence_ids=set(),
            created_at="2026-09-05T00:00:00Z",
            id_prefix="run-1",
        )


def test_rejects_more_than_three_key_reasons():
    bad = json.dumps(
        {
            "recommendation": "PILOT",
            "confidence_band": "MEDIUM",
            "key_reasons": [{"text": str(i), "evidence_refs": []} for i in range(4)],
        }
    )
    with pytest.raises(ResponseParsingError, match="at most 3"):
        parse_position_response(
            bad,
            member=CommitteeSeat.CFO,
            phase=PositionPhase.INITIAL,
            known_evidence_ids=set(),
            created_at="2026-09-05T00:00:00Z",
            id_prefix="run-1",
        )


def test_rejects_invented_evidence_id():
    bad = json.dumps(
        {
            "recommendation": "PILOT",
            "confidence_band": "MEDIUM",
            "key_reasons": [{"text": "x", "evidence_refs": ["ev-does-not-exist"]}],
        }
    )
    with pytest.raises(ResponseParsingError, match="unknown evidence id"):
        parse_position_response(
            bad,
            member=CommitteeSeat.CFO,
            phase=PositionPhase.INITIAL,
            known_evidence_ids={"ev-001"},
            created_at="2026-09-05T00:00:00Z",
            id_prefix="run-1",
        )


def _initial_position(recommendation=DecisionAction.PILOT, blocking_unknowns=None):
    return CommitteePosition(
        id="p-1",
        created_at="2026-09-05T00:00:00Z",
        member=CommitteeSeat.CISO,
        phase=PositionPhase.INITIAL,
        recommendation=recommendation,
        confidence_band=ConfidenceBand.MEDIUM,
        key_reasons=[],
        blocking_unknowns=blocking_unknowns or [],
    )


def test_parse_revision_response_valid():
    raw = json.dumps(
        {
            "revised_position": "DEFER",
            "revised_confidence": "LOW",
            "change_type": "evidence_driven",
            "trigger_refs": ["ev-027"],
            "stated_reason": "New study contradicts the uplift assumption.",
        }
    )
    belief_update, blocking_unknowns = parse_revision_response(
        raw,
        member=CommitteeSeat.CFO,
        initial_position=_initial_position(),
        known_evidence_ids={"ev-027"},
        created_at="2026-09-05T00:00:00Z",
        id_prefix="run-1",
    )
    assert belief_update.revised_position == DecisionAction.DEFER
    assert belief_update.change_type.value == "evidence_driven"
    # blocking_unknowns not supplied by the model -> falls back to the
    # initial position's own list, not silently dropped.
    assert blocking_unknowns == []


def test_parse_revision_response_rejects_case_alternative_as_position():
    """The exact live-caught bug: the model returned a case alternative
    ('targeted_role_rollout') instead of a DecisionAction value."""
    raw = json.dumps(
        {
            "revised_position": "targeted_role_rollout",
            "revised_confidence": "MEDIUM",
            "change_type": "no_change",
        }
    )
    with pytest.raises(ResponseParsingError, match="invalid revised_position"):
        parse_revision_response(
            raw,
            member=CommitteeSeat.CFO,
            initial_position=_initial_position(),
            known_evidence_ids=set(),
            created_at="2026-09-05T00:00:00Z",
            id_prefix="run-1",
        )


def test_parse_revision_response_preserves_blocking_unknown_on_no_change():
    """P0-06's canonical pattern: no_change with the blocking unknown intact."""
    raw = json.dumps(
        {
            "revised_position": "SCALE",
            "revised_confidence": "MEDIUM",
            "change_type": "no_change",
            "blocking_unknowns": ["secrets handling still unanswered"],
        }
    )
    _belief_update, blocking_unknowns = parse_revision_response(
        raw,
        member=CommitteeSeat.CISO,
        initial_position=_initial_position(blocking_unknowns=["secrets handling still unanswered"]),
        known_evidence_ids=set(),
        created_at="2026-09-05T00:00:00Z",
        id_prefix="run-1",
    )
    assert blocking_unknowns == ["secrets handling still unanswered"]


def test_parse_revision_response_rejects_unknown_trigger_ref():
    raw = json.dumps(
        {
            "revised_position": "DEFER",
            "revised_confidence": "LOW",
            "change_type": "evidence_driven",
            "trigger_refs": ["ev-does-not-exist"],
        }
    )
    with pytest.raises(ResponseParsingError, match="unknown evidence id"):
        parse_revision_response(
            raw,
            member=CommitteeSeat.CFO,
            initial_position=_initial_position(),
            known_evidence_ids={"ev-001"},
            created_at="2026-09-05T00:00:00Z",
            id_prefix="run-1",
        )
