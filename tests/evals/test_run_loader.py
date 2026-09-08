from kriterion.domain.enums import DriftFlag
from kriterion.evals.run_loader import load_belief_update

CREATED_AT = "2026-09-07T00:00:00Z"


def _belief_update_data(drift_flags):
    return {
        "id": "b-cfo", "created_at": CREATED_AT, "member": "cfo",
        "initial_position": "DEFER", "initial_confidence": "MEDIUM",
        "revised_position": "DEFER", "revised_confidence": "MEDIUM",
        "change_type": "evidence_driven", "trigger_refs": [], "stated_reason": "r",
        "drift_flags": drift_flags,
    }


def test_load_belief_update_wraps_drift_flags_as_enum_not_bare_strings():
    """Real bug caught live (2026-09-07) generating a report for a real
    Treatment D run: drift_flags loaded as plain strings, and
    report/html.py's rendering crashed calling .value on a str. Every
    prior report generation happened to only see empty drift_flags lists,
    so the bug was latent until a run with a real flag was rendered."""
    update = load_belief_update(_belief_update_data(["retrofit"]))
    assert update.drift_flags == [DriftFlag.RETROFIT]
    assert update.drift_flags[0].value == "retrofit"  # this line is what crashed before the fix


def test_load_belief_update_handles_empty_drift_flags():
    update = load_belief_update(_belief_update_data([]))
    assert update.drift_flags == []
