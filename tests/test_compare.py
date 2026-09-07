import json
from pathlib import Path

from kriterion.compare import compare_conditions, compute_condition_metrics, compute_perturbation_drift_rate, seed_to_seed_stddev


def _write_run(run_dir: Path, *, positions=None, belief_updates=None, recommendation=None, run_export=None):
    run_dir.mkdir(parents=True)
    if positions is not None:
        (run_dir / "positions_initial.json").write_text(json.dumps(positions))
    if belief_updates is not None:
        (run_dir / "belief_updates.json").write_text(json.dumps(belief_updates))
    if recommendation is not None:
        (run_dir / "recommendation.json").write_text(json.dumps(recommendation))
    if run_export is not None:
        (run_dir / "run-export.json").write_text(json.dumps(run_export))


def _position(seat, refs):
    return {
        "id": f"p-{seat}", "member": seat, "recommendation": "PILOT", "confidence_band": "MEDIUM",
        "key_reasons": [{"text": "r", "evidence_refs": refs}],
    }


def test_unsupported_claim_rate_counts_reasons_with_no_evidence_refs(tmp_path):
    run_dir = tmp_path / "run-1"
    _write_run(run_dir, positions=[_position("cfo", []), _position("cto", ["ev-001"])])
    metrics = compute_condition_metrics("A", [run_dir])
    assert metrics.unsupported_claim_rate == 0.5


def test_belief_update_rationality_counts_grounded_updates(tmp_path):
    run_dir = tmp_path / "run-1"
    updates = [
        {"member": "cfo", "change_type": "evidence_driven", "trigger_refs": ["ev-001"]},
        {"member": "cto", "change_type": "unexplained", "trigger_refs": []},
    ]
    _write_run(run_dir, belief_updates=updates)
    metrics = compute_condition_metrics("C", [run_dir])
    assert metrics.belief_update_rationality == 0.5


def test_belief_update_rationality_none_when_no_updates(tmp_path):
    run_dir = tmp_path / "run-1"
    _write_run(run_dir, positions=[_position("cfo", ["ev-001"])])
    metrics = compute_condition_metrics("B", [run_dir])
    assert metrics.belief_update_rationality is None


def test_dissent_nonempty_rate(tmp_path):
    run_dir = tmp_path / "run-1"
    _write_run(run_dir, recommendation={"strongest_dissent": {"verbatim": "a real dissent"}})
    metrics = compute_condition_metrics("C", [run_dir])
    assert metrics.dissent_nonempty_rate == 1.0


def test_p0_pass_rate_from_run_export(tmp_path):
    run_dir = tmp_path / "run-1"
    run_export = {"fixtures": [{"fixture_id": "P0-01", "passed": True, "detail": "d"}, {"fixture_id": "P0-06", "passed": False, "detail": "d"}]}
    _write_run(run_dir, run_export=run_export)
    metrics = compute_condition_metrics("C", [run_dir])
    assert metrics.p0_pass_rate == 0.5


def test_seed_to_seed_stddev_none_with_fewer_than_two_seeds():
    assert seed_to_seed_stddev([1.0]) is None


def test_seed_to_seed_stddev_computed_with_two_or_more():
    assert seed_to_seed_stddev([1.0, 2.0, 3.0]) is not None


def test_compare_conditions_reports_not_evaluable_with_too_few_seeds(tmp_path):
    a_dir = tmp_path / "a1"
    b_dir = tmp_path / "b1"
    c_dir = tmp_path / "c1"
    _write_run(a_dir, positions=[_position("cfo", ["ev-001"])])
    _write_run(b_dir, positions=[_position("cfo", ["ev-001"])])
    _write_run(c_dir, positions=[_position("cfo", ["ev-001"])])
    result = compare_conditions({"A": [a_dir], "B": [b_dir], "C": [c_dir]})
    assert result.honest_negative_fired is None
    assert "stddev" in result.honest_negative_detail


def test_compare_conditions_reports_missing_condition(tmp_path):
    a_dir = tmp_path / "a1"
    _write_run(a_dir, positions=[_position("cfo", ["ev-001"])])
    result = compare_conditions({"A": [a_dir]})
    assert result.honest_negative_fired is None
    assert "all three conditions" in result.honest_negative_detail


def _write_recommendation_only(run_dir: Path, action):
    run_dir.mkdir(parents=True)
    (run_dir / "recommendation.json").write_text(json.dumps({"action": action, "confidence_band": "MEDIUM"}))


def test_compute_perturbation_drift_rate_none_with_no_pairs():
    assert compute_perturbation_drift_rate([]) is None


def test_compute_perturbation_drift_rate_computes_fraction_drifted(tmp_path):
    base1, pert1 = tmp_path / "base1", tmp_path / "pert1"
    base2, pert2 = tmp_path / "base2", tmp_path / "pert2"
    _write_recommendation_only(base1, "DEFER")
    _write_recommendation_only(pert1, "PILOT")  # drifted
    _write_recommendation_only(base2, "DEFER")
    _write_recommendation_only(pert2, "DEFER")  # not drifted
    rate = compute_perturbation_drift_rate([(base1, pert1), (base2, pert2)])
    assert rate == 0.5


def test_compare_conditions_includes_perturbation_robustness_when_c_more_robust(tmp_path):
    run_export = {"fixtures": [{"fixture_id": "P0-01", "passed": True, "detail": "d"}]}

    def _seed_run(cond, seed):
        d = tmp_path / f"{cond}{seed}"
        _write_run(d, positions=[_position("cfo", ["ev-001"])], run_export=run_export)
        return d

    a_dirs = [_seed_run("a", 0), _seed_run("a", 1)]
    b_dirs = [_seed_run("b", 0), _seed_run("b", 1)]
    c_dirs = [_seed_run("c", 0), _seed_run("c", 1)]

    a_base1, a_pert1 = tmp_path / "a_base1", tmp_path / "a_pert1"
    a_base2, a_pert2 = tmp_path / "a_base2", tmp_path / "a_pert2"
    _write_recommendation_only(a_base1, "DEFER")
    _write_recommendation_only(a_pert1, "PILOT")  # A drifts here
    _write_recommendation_only(a_base2, "DEFER")
    _write_recommendation_only(a_pert2, "DEFER")

    c_base1, c_pert1 = tmp_path / "c_base1", tmp_path / "c_pert1"
    c_base2, c_pert2 = tmp_path / "c_base2", tmp_path / "c_pert2"
    _write_recommendation_only(c_base1, "DEFER")
    _write_recommendation_only(c_pert1, "DEFER")  # C never drifts
    _write_recommendation_only(c_base2, "DEFER")
    _write_recommendation_only(c_pert2, "DEFER")

    result = compare_conditions(
        {"A": a_dirs, "B": b_dirs, "C": c_dirs},
        perturbation_pairs={"A": [(a_base1, a_pert1), (a_base2, a_pert2)], "C": [(c_base1, c_pert1), (c_base2, c_pert2)]},
    )

    assert result.perturbation_drift_rate == {"A": 0.5, "C": 0.0}
    assert "perturbation_robustness" in result.honest_negative_detail
    assert "B not tested by the pre-registered design" in result.honest_negative_detail
