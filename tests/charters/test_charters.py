from pathlib import Path

import pytest

from kriterion.casepack import load_case_pack
from kriterion.charters import CharterError, load_all_charters, load_charter
from kriterion.domain.enums import CommitteeSeat
from kriterion.domain.serialization import fingerprint

CHARTERS_DIR = Path(__file__).parent.parent.parent / "charters"
CASE_A_DIR = Path(__file__).parent.parent.parent / "cases" / "coding-agent-rollout"


def test_loads_all_five_charters_with_matching_seats():
    charters = load_all_charters(CHARTERS_DIR, created_at="2026-09-05T00:00:00Z")
    assert set(charters.keys()) == {
        CommitteeSeat.CFO,
        CommitteeSeat.CTO,
        CommitteeSeat.CISO,
        CommitteeSeat.CRO_COMPLIANCE,
        CommitteeSeat.BUSINESS_EXECUTIVE,
    }
    for seat, charter in charters.items():
        assert charter.seat == seat
        assert charter.version == "v1"


def test_every_charter_has_nonempty_required_fields():
    charters = load_all_charters(CHARTERS_DIR, created_at="2026-09-05T00:00:00Z")
    for charter in charters.values():
        assert charter.objective.strip()
        assert charter.concerns
        assert charter.required_evidence
        assert charter.decision_rights
        assert charter.standard_challenges
        assert charter.failure_modes
        assert charter.forbidden


def test_required_evidence_ids_exist_in_case_a_ledger():
    """Cross-check: a charter's required_evidence must actually resolve to
    real evidence/assumption ids, or phase 3 would silently inject nothing."""
    charters = load_all_charters(CHARTERS_DIR, created_at="2026-09-05T00:00:00Z")
    _, items, assumptions = load_case_pack(CASE_A_DIR, created_at="2026-09-05T00:00:00Z")
    known_ids = {item.id for item in items} | {a.id for a in assumptions}

    for seat, charter in charters.items():
        unknown = [eid for eid in charter.required_evidence if eid not in known_ids]
        assert not unknown, f"{seat.value} charter references unknown ids: {unknown}"


def test_charter_hash_is_stable():
    charter = load_charter(CHARTERS_DIR / "ciso.v1.toml", created_at="2026-09-05T00:00:00Z")
    h1 = fingerprint(charter)
    h2 = fingerprint(charter)
    assert h1 == h2
    assert len(h1) == 64


def test_ciso_charter_has_the_standing_dissent_right():
    """P0-06 depends on this: the CISO must be allowed to hold a blocking
    unknown open regardless of the other four members."""
    charter = load_charter(CHARTERS_DIR / "ciso.v1.toml", created_at="2026-09-05T00:00:00Z")
    assert any("regardless" in right.lower() for right in charter.decision_rights)


def test_missing_charter_field_raises_clear_error(tmp_path):
    bad = tmp_path / "bad.v1.toml"
    bad.write_text('id = "x"\nversion = "v1"\nseat = "cfo"\n')
    with pytest.raises(CharterError, match="missing required field"):
        load_charter(bad, created_at="2026-09-05T00:00:00Z")


def test_invalid_seat_raises_clear_error(tmp_path):
    bad = tmp_path / "bad.v1.toml"
    bad.write_text(
        """
id = "x"
version = "v1"
seat = "not_a_real_seat"
objective = "o"
concerns = ["c"]
required_evidence = ["ev-1"]
decision_rights = ["d"]
standard_challenges = ["s"]
failure_modes = ["f"]
forbidden = ["x"]
"""
    )
    with pytest.raises(CharterError, match="invalid seat"):
        load_charter(bad, created_at="2026-09-05T00:00:00Z")
