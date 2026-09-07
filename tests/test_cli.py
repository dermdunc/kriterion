import json
import subprocess
import sys
from pathlib import Path

CASE_A_DIR = Path(__file__).parent.parent / "cases" / "coding-agent-rollout"


def test_help_exits_zero():
    result = subprocess.run(
        [sys.executable, "-m", "kriterion.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "kriterion" in result.stdout


def test_version_exits_zero():
    result = subprocess.run(
        [sys.executable, "-m", "kriterion.cli", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "kriterion" in result.stdout


def test_ledger_freeze_end_to_end(tmp_path):
    runs_dir = tmp_path / "runs"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "kriterion.cli",
            "ledger",
            "freeze",
            str(CASE_A_DIR),
            "--run-id",
            "test-run",
            "--runs-dir",
            str(runs_dir),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    ledger_path = runs_dir / "test-run" / "ledger.frozen.json"
    assert ledger_path.is_file()
    data = json.loads(ledger_path.read_text())
    assert "fingerprint" in data and data["fingerprint"]
    assert 25 <= len(data["items"]) <= 30


def test_ledger_freeze_rejects_bad_case_with_clear_error(tmp_path):
    bad_case_dir = tmp_path / "empty-case"
    bad_case_dir.mkdir()
    (bad_case_dir / "case.toml").write_text("[case]\nid = \"x\"\n")

    result = subprocess.run(
        [sys.executable, "-m", "kriterion.cli", "ledger", "freeze", str(bad_case_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "ledger freeze failed" in result.stderr
