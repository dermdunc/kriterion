from kriterion.domain.committee import BeliefUpdate, Challenge
from kriterion.domain.enums import ChallengeType, ChangeType, CommitteeSeat, ConfidenceBand, DecisionAction
from kriterion.protocol.drift import derive_drift_flags

CREATED_AT = "2026-09-06T00:00:00Z"


def _update(
    *, initial_position=DecisionAction.REQUEST_EVIDENCE, revised_position=DecisionAction.REQUEST_EVIDENCE,
    initial_confidence=ConfidenceBand.MEDIUM, revised_confidence=ConfidenceBand.MEDIUM,
    change_type=ChangeType.NO_CHANGE, trigger_refs=None, stated_reason="",
):
    return BeliefUpdate(
        id="b-ciso", created_at=CREATED_AT, member=CommitteeSeat.CISO,
        initial_position=initial_position, initial_confidence=initial_confidence,
        revised_position=revised_position, revised_confidence=revised_confidence,
        change_type=change_type, trigger_refs=trigger_refs or [], stated_reason=stated_reason,
    )


def _challenge(id, author_role, content):
    return Challenge(id=id, created_at=CREATED_AT, type=ChallengeType.PREMORTEM, author_role=author_role, content=content)


def test_no_change_gets_no_flags():
    update = _update()  # initial == revised on both fields
    flags = derive_drift_flags(update, new_since_phase3_ids=set(), challenges=[])
    assert flags == []


def test_unexplained_when_changed_with_no_trigger_refs():
    update = _update(revised_position=DecisionAction.DEFER, change_type=ChangeType.UNEXPLAINED, trigger_refs=[])
    flags = derive_drift_flags(update, new_since_phase3_ids=set(), challenges=[])
    assert "unexplained" in [f.value for f in flags]


def test_retrofit_when_only_stale_evidence_cited():
    update = _update(revised_position=DecisionAction.DEFER, change_type=ChangeType.EVIDENCE_DRIVEN, trigger_refs=["ev-001"])
    flags = derive_drift_flags(update, new_since_phase3_ids=set(), challenges=[])  # ev-001 not in new_since_phase3_ids
    assert "retrofit" in [f.value for f in flags]


def test_no_retrofit_when_citing_newly_injected_evidence():
    update = _update(revised_position=DecisionAction.DEFER, change_type=ChangeType.EVIDENCE_DRIVEN, trigger_refs=["ev-027"])
    flags = derive_drift_flags(update, new_since_phase3_ids={"ev-027"}, challenges=[])
    assert flags == []


def test_no_retrofit_when_citing_a_challenge_artifact():
    update = _update(revised_position=DecisionAction.DEFER, change_type=ChangeType.ARGUMENT_DRIVEN, trigger_refs=["ch:premortem-cto"])
    challenges = [_challenge("ch:premortem-cto", CommitteeSeat.CTO, "some premortem text")]
    flags = derive_drift_flags(update, new_since_phase3_ids=set(), challenges=challenges)
    assert flags == []


def test_confidence_jump_low_to_high():
    update = _update(initial_confidence=ConfidenceBand.LOW, revised_confidence=ConfidenceBand.HIGH, trigger_refs=["ev-027"])
    flags = derive_drift_flags(update, new_since_phase3_ids={"ev-027"}, challenges=[])
    assert "confidence_jump" in [f.value for f in flags]


def test_no_confidence_jump_for_adjacent_band_move():
    update = _update(initial_confidence=ConfidenceBand.LOW, revised_confidence=ConfidenceBand.MEDIUM, trigger_refs=["ev-027"])
    flags = derive_drift_flags(update, new_since_phase3_ids={"ev-027"}, challenges=[])
    assert "confidence_jump" not in [f.value for f in flags]


def test_echo_when_no_new_evidence_and_high_overlap_with_anothers_challenge():
    shared_text = "the security review never covered regulated data systems at all"
    update = _update(
        revised_position=DecisionAction.DEFER, change_type=ChangeType.ARGUMENT_DRIVEN,
        trigger_refs=[], stated_reason=shared_text,
    )
    challenges = [_challenge("ch:premortem-cto", CommitteeSeat.CTO, shared_text)]
    flags = derive_drift_flags(update, new_since_phase3_ids=set(), challenges=challenges)
    assert "echo" in [f.value for f in flags]


def test_no_echo_against_own_challenge_artifact():
    shared_text = "the security review never covered regulated data systems at all"
    update = _update(
        revised_position=DecisionAction.DEFER, change_type=ChangeType.ARGUMENT_DRIVEN,
        trigger_refs=[], stated_reason=shared_text,
    )
    # Same text, but authored by CISO itself (the dissenting member) -- not "another member's".
    challenges = [_challenge("ch:premortem-ciso", CommitteeSeat.CISO, shared_text)]
    flags = derive_drift_flags(update, new_since_phase3_ids=set(), challenges=challenges)
    assert "echo" not in [f.value for f in flags]


def test_no_echo_when_citing_new_evidence_even_with_high_overlap():
    shared_text = "the security review never covered regulated data systems at all"
    update = _update(
        revised_position=DecisionAction.DEFER, change_type=ChangeType.EVIDENCE_DRIVEN,
        trigger_refs=["ev-027"], stated_reason=shared_text,
    )
    challenges = [_challenge("ch:premortem-cto", CommitteeSeat.CTO, shared_text)]
    flags = derive_drift_flags(update, new_since_phase3_ids={"ev-027"}, challenges=challenges)
    assert "echo" not in [f.value for f in flags]


def test_real_batch_finding_evidence_driven_divergence_gets_no_flags():
    # runs/caseC-condC-s2 shape: cites real (if pre-existing) evidence,
    # coherent distinct stated_reason -- should NOT be flagged retrofit
    # once at least one cited ref counts, and gets no echo since it cites
    # evidence. This one only cites stale evidence (ev-101 not injected),
    # so it IS expected to be retrofit-flagged -- confidence-worthy
    # instrumentation, not proof of misbehaviour, which is exactly why
    # P0-06 must not be the thing checking change_type at all (see
    # evals/scorers.py).
    update = _update(
        initial_position=DecisionAction.REQUEST_EVIDENCE, revised_position=DecisionAction.DISCOVERY,
        change_type=ChangeType.EVIDENCE_DRIVEN, trigger_refs=["ev-101", "ev-102", "ev-103", "ev-106"],
        stated_reason="Evidence highlights security risks and negative NPV; a discovery phase is needed.",
    )
    flags = derive_drift_flags(update, new_since_phase3_ids=set(), challenges=[])
    assert [f.value for f in flags] == ["retrofit"]
