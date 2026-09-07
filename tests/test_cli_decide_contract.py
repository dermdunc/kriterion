"""End-to-end CLI test for task 11's real accept criterion: a funding
action without an OutcomeContract exits non-zero (P0-09)."""

import subprocess
import sys
from pathlib import Path


def _run(args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "kriterion.cli", *args], capture_output=True, text=True, cwd=cwd
    )


def test_funding_decision_without_contract_fails_validate_run(tmp_path):
    project_root = Path(__file__).parent.parent
    runs_dir = tmp_path / "runs"
    run_id = "test-run"
    (runs_dir / run_id).mkdir(parents=True)

    decide_result = _run(
        ["decide", run_id, "--action", "SCALE", "--disposition", "accept",
         "--rationale", "r", "--owner", "cio", "--runs-dir", str(runs_dir)],
        cwd=project_root,
    )
    assert decide_result.returncode == 0, decide_result.stderr
    assert "WARNING" in decide_result.stderr  # flagged immediately, not silently missed

    validate_result = _run(["validate-run", run_id, "--runs-dir", str(runs_dir)], cwd=project_root)
    assert validate_result.returncode == 1
    assert "P0-09" in validate_result.stderr


def test_funding_decision_with_contract_passes_validate_run(tmp_path):
    project_root = Path(__file__).parent.parent
    runs_dir = tmp_path / "runs"
    run_id = "test-run"
    (runs_dir / run_id).mkdir(parents=True)

    _run(
        ["decide", run_id, "--action", "SCALE", "--disposition", "accept",
         "--rationale", "r", "--owner", "cio", "--runs-dir", str(runs_dir)],
        cwd=project_root,
    )
    contract_result = _run(
        ["contract", run_id, "--baseline-date", "2026-09-05", "--review-date", "2026-12-05",
         "--next-decision", "review", "--measure", "cycle_time:9.6h:6h:ev-002",
         "--owner", "cio", "--runs-dir", str(runs_dir)],
        cwd=project_root,
    )
    assert contract_result.returncode == 0, contract_result.stderr

    validate_result = _run(["validate-run", run_id, "--runs-dir", str(runs_dir)], cwd=project_root)
    assert validate_result.returncode == 0
    assert "clean" in validate_result.stdout


def test_non_funding_decision_never_needs_a_contract(tmp_path):
    project_root = Path(__file__).parent.parent
    runs_dir = tmp_path / "runs"
    run_id = "test-run"
    (runs_dir / run_id).mkdir(parents=True)

    _run(
        ["decide", run_id, "--action", "DEFER", "--disposition", "reject",
         "--rationale", "r", "--owner", "cio", "--runs-dir", str(runs_dir)],
        cwd=project_root,
    )
    validate_result = _run(["validate-run", run_id, "--runs-dir", str(runs_dir)], cwd=project_root)
    assert validate_result.returncode == 0
