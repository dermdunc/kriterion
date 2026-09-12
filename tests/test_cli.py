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


def test_evidence_requests_are_persisted_as_a_run_artifact(tmp_path):
    """"What would change this seat's mind" must be an artifact, not copy.

    Phase 3 parses an EvidenceRequest (with its `would_change`) out of every
    member's assessment; before 2026-09-11 the CLI discarded them, so nothing
    on disk recorded them. The file is written even when empty, so "nobody
    asked for evidence" stays distinguishable from "this run predates the
    artifact".
    """
    import json as _json

    from kriterion.cli import _write_evidence_requests
    from kriterion.domain.committee import EvidenceRequest
    from kriterion.domain.enums import CommitteeSeat, EvidenceRequestStatus

    request = EvidenceRequest(
        id="er-001",
        created_at="2026-09-11T00:00:00Z",
        member=CommitteeSeat.CISO,
        description="Security-review coverage of regulated-data systems",
        would_change="Would move CISO from DEFER to PILOT if coverage is demonstrated",
        status=EvidenceRequestStatus.UNAVAILABLE,
    )

    _write_evidence_requests(tmp_path, [request])
    written = _json.loads((tmp_path / "evidence_requests.json").read_text())
    assert len(written) == 1
    assert written[0]["would_change"].startswith("Would move CISO")
    assert written[0]["member"] == "ciso"
    assert written[0]["status"] == EvidenceRequestStatus.UNAVAILABLE.value

    _write_evidence_requests(tmp_path, [])
    assert _json.loads((tmp_path / "evidence_requests.json").read_text()) == []


def test_decision_page_refuses_to_write_a_page_that_fails_the_integrity_check(tmp_path):
    """`kriterion decision-page --check-only` must exit non-zero, and must not
    overwrite the file, when the page on disk no longer re-derives from the
    run. A build step that publishes anyway is not an invariant."""
    repo_root = Path(__file__).parent.parent
    page = tmp_path / "index.html"
    page.write_text((repo_root / "docs" / "index.html").read_text().replace("£5.09m", "£9.05m", 1))
    before = page.read_text()

    result = subprocess.run(
        [
            sys.executable, "-m", "kriterion.cli", "decision-page", "caseA-condC-s5",
            str(CASE_A_DIR), "--assurance-import",
            str(CASE_A_DIR / "assurance" / "imported.json"),
            "--out", str(page), "--check-only",
        ],
        capture_output=True, text=True, cwd=repo_root,
    )
    assert result.returncode == 1
    assert "narrative-integrity violation" in result.stderr
    assert "binding.match" in result.stderr
    assert page.read_text() == before, "a refused check must not rewrite the page"


def test_decision_page_check_only_passes_against_the_committed_page():
    repo_root = Path(__file__).parent.parent
    result = subprocess.run(
        [
            sys.executable, "-m", "kriterion.cli", "decision-page", "caseA-condC-s5",
            str(CASE_A_DIR), "--assurance-import",
            str(CASE_A_DIR / "assurance" / "imported.json"),
            "--out", "docs/index.html", "--check-only",
        ],
        capture_output=True, text=True, cwd=repo_root,
    )
    assert result.returncode == 0, result.stderr
    assert "is faithful to" in result.stdout


def test_decision_page_refuses_a_run_it_cannot_load(tmp_path):
    repo_root = Path(__file__).parent.parent
    result = subprocess.run(
        [
            sys.executable, "-m", "kriterion.cli", "decision-page", "no-such-run",
            str(CASE_A_DIR), "--out", str(tmp_path / "out.html"),
        ],
        capture_output=True, text=True, cwd=repo_root,
    )
    assert result.returncode == 1
    assert "run directory not found" in result.stderr
    assert not (tmp_path / "out.html").exists()
