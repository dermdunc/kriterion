from pathlib import Path

import pytest

from kriterion.casepack import CasePackError, load_case_pack

CASE_A_DIR = Path(__file__).parent.parent / "cases" / "coding-agent-rollout"


def test_loads_case_a_with_25_to_30_evidence_items():
    case, items, _assumptions = load_case_pack(CASE_A_DIR, created_at="2026-09-05T00:00:00Z")
    assert case.id == "coding-agent-rollout"
    assert case.ask.amount_gbp == 4_200_000
    assert "do_nothing" in case.alternatives
    assert 25 <= len(items) <= 30


def test_all_seven_evidence_categories_present():
    _, items, _assumptions = load_case_pack(CASE_A_DIR, created_at="2026-09-05T00:00:00Z")
    categories = {item.category.value for item in items}
    assert categories == {
        "MEASURED",
        "EXTERNAL_REFERENCE",
        "EXPERT_JUDGMENT",
        "FORECAST",
        "ASSUMPTION",
        "INFERENCE",
        "UNKNOWN",
    }


def test_rejects_bad_category(tmp_path):
    case_dir = tmp_path / "bad-case"
    case_dir.mkdir()
    (case_dir / "case.toml").write_text(
        """
[case]
id = "bad-case"
title = "t"
sponsor = "s"
decision_owner = "o"
decision_requested = "d"
alternatives = ["do_nothing", "x"]

[case.ask]
type = "staged_funding"
amount_gbp = 1
duration = "1 month"

[[evidence]]
id = "ev-1"
category = "NOT_A_REAL_CATEGORY"
attestation = "AUTHORED"
claim = "c"
source = "s"
period = "p"
strength = "HIGH"
"""
    )
    with pytest.raises(CasePackError, match="invalid category"):
        load_case_pack(case_dir, created_at="2026-09-05T00:00:00Z")


def test_rejects_missing_attestation(tmp_path):
    case_dir = tmp_path / "bad-case"
    case_dir.mkdir()
    (case_dir / "case.toml").write_text(
        """
[case]
id = "bad-case"
title = "t"
sponsor = "s"
decision_owner = "o"
decision_requested = "d"
alternatives = ["do_nothing", "x"]

[case.ask]
type = "staged_funding"
amount_gbp = 1
duration = "1 month"

[[evidence]]
id = "ev-1"
category = "MEASURED"
claim = "c"
source = "s"
period = "p"
strength = "HIGH"
"""
    )
    with pytest.raises(CasePackError, match="missing required field 'attestation'"):
        load_case_pack(case_dir, created_at="2026-09-05T00:00:00Z")


def test_rejects_duplicate_evidence_id(tmp_path):
    case_dir = tmp_path / "dup-case"
    case_dir.mkdir()
    entry = """
[[evidence]]
id = "ev-1"
category = "MEASURED"
attestation = "AUTHORED"
claim = "c"
source = "s"
period = "p"
strength = "HIGH"
"""
    (case_dir / "case.toml").write_text(
        """
[case]
id = "dup-case"
title = "t"
sponsor = "s"
decision_owner = "o"
decision_requested = "d"
alternatives = ["do_nothing", "x"]

[case.ask]
type = "staged_funding"
amount_gbp = 1
duration = "1 month"
"""
        + entry
        + entry
    )
    with pytest.raises(CasePackError, match="duplicate evidence id"):
        load_case_pack(case_dir, created_at="2026-09-05T00:00:00Z")
