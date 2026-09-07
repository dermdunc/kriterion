import json
from pathlib import Path

from kriterion.perturbation_diff import diff_paired_runs


def _write_recommendation(run_dir: Path, action, confidence="MEDIUM"):
    run_dir.mkdir(parents=True)
    (run_dir / "recommendation.json").write_text(json.dumps({"action": action, "confidence_band": confidence}))


def test_no_drift_when_actions_match(tmp_path):
    baseline = tmp_path / "baseline"
    perturbed = tmp_path / "perturbed"
    _write_recommendation(baseline, "DEFER")
    _write_recommendation(perturbed, "DEFER")

    result = diff_paired_runs(baseline, perturbed)

    assert result.action_drifted is False
    assert result.baseline_action == result.perturbed_action == "DEFER"


def test_drift_when_actions_differ(tmp_path):
    baseline = tmp_path / "baseline"
    perturbed = tmp_path / "perturbed"
    _write_recommendation(baseline, "DEFER")
    _write_recommendation(perturbed, "PILOT")

    result = diff_paired_runs(baseline, perturbed)

    assert result.action_drifted is True
    assert result.baseline_action == "DEFER"
    assert result.perturbed_action == "PILOT"


def test_none_when_a_run_has_no_recommendation(tmp_path):
    baseline = tmp_path / "baseline"
    perturbed = tmp_path / "perturbed"
    _write_recommendation(baseline, "DEFER")
    perturbed.mkdir(parents=True)  # no recommendation.json -- e.g. every member abstained

    result = diff_paired_runs(baseline, perturbed)

    assert result.action_drifted is None
    assert result.perturbed_action is None
