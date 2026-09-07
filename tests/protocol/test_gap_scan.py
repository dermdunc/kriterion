from kriterion.domain.committee import CommitteePosition, KeyReason, RoleCharter
from kriterion.domain.enums import CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase
from kriterion.domain.evidence import Attestation, EvidenceCategory, EvidenceItem, Strength
from kriterion.protocol.gap_scan import scan_contradictions_and_gaps


def _evidence(id_, contradicts=None):
    return EvidenceItem(
        id=id_, created_at="2026-09-05T00:00:00Z", category=EvidenceCategory.MEASURED,
        attestation=Attestation.AUTHORED, claim="c", source="s", period="p",
        strength=Strength.HIGH, contradicts=contradicts or [],
    )


def _charter(seat, required_evidence):
    return RoleCharter(
        id=f"charter-{seat.value}", created_at="2026-09-05T00:00:00Z", version="v1", seat=seat,
        objective="o", concerns=["c"], required_evidence=required_evidence,
        decision_rights=["d"], standard_challenges=["s"], failure_modes=["f"], forbidden=["x"],
    )


def _position(seat, cited_refs):
    return CommitteePosition(
        id=f"p-{seat.value}", created_at="2026-09-05T00:00:00Z", member=seat,
        phase=PositionPhase.INITIAL, recommendation=DecisionAction.PILOT,
        confidence_band=ConfidenceBand.MEDIUM,
        key_reasons=[KeyReason(text="r", evidence_refs=cited_refs)],
    )


def test_finds_real_contradictions_between_ledger_items():
    evidence_by_id = {
        "ev-001": _evidence("ev-001", contradicts=["ev-002"]),
        "ev-002": _evidence("ev-002"),
    }
    result = scan_contradictions_and_gaps(evidence_by_id, [], [])
    assert result.contradictions == [("ev-001", "ev-002")]


def test_ignores_contradiction_pointing_to_nonexistent_item():
    evidence_by_id = {"ev-001": _evidence("ev-001", contradicts=["ev-999"])}
    result = scan_contradictions_and_gaps(evidence_by_id, [], [])
    assert result.contradictions == []


def test_finds_gap_when_member_never_cites_own_required_evidence():
    charter = _charter(CommitteeSeat.CISO, required_evidence=["ev-008", "ev-015"])
    position = _position(CommitteeSeat.CISO, cited_refs=["ev-008"])  # never cites ev-015
    result = scan_contradictions_and_gaps({}, [charter], [position])
    assert result.gaps == [("ciso", "ev-015")]


def test_no_gap_when_all_required_evidence_cited():
    charter = _charter(CommitteeSeat.CFO, required_evidence=["ev-016"])
    position = _position(CommitteeSeat.CFO, cited_refs=["ev-016"])
    result = scan_contradictions_and_gaps({}, [charter], [position])
    assert result.gaps == []
