"""The assurance vertical slice into Kriterion's system of record.

`kriterion assurance import --into-case` is the only path by which imported
assurance evidence reaches a *frozen ledger version*, and from there the
report renderer. These tests exercise that whole chain end to end with no
model call and no assurance package installed, and assert the two things the
2026-09-11 adversarial review said were unproven:

1. imported assurance items actually land in a frozen ledger vN+1 and are
   rendered into the generated report, carrying their source provenance; and
2. the CLI refuses malformed or laundering document pairs with a controlled
   non-zero exit and a message, never a traceback.
"""

from __future__ import annotations

import json
from pathlib import Path

from kriterion.cli import main

REPO_ROOT = Path(__file__).parent.parent.parent
CASE_DIR = REPO_ROOT / "cases" / "coding-agent-rollout"
FIXTURE_DIR = CASE_DIR / "assurance"


def _import_into_case(tmp_path: Path, envelope_dir: Path = FIXTURE_DIR, run_id: str = "slice") -> int:
    return main(
        [
            "assurance",
            "import",
            str(envelope_dir),
            "--attestation",
            "AUTHORED",
            "--into-case",
            str(CASE_DIR),
            "--run-id",
            run_id,
            "--runs-dir",
            str(tmp_path),
        ]
    )


def test_import_freezes_a_new_ledger_version_and_renders_into_the_report(tmp_path, capsys):
    assert _import_into_case(tmp_path) == 0

    ledger_path = tmp_path / "slice" / "ledger.frozen.json"
    ledger = json.loads(ledger_path.read_text())

    # A new ledger *version*, fingerprinted, never an edit of an existing one.
    assert ledger["version"] == 2
    assert ledger["fingerprint"]

    asr_items = [i for i in ledger["items"] if i["id"].startswith("asr-")]
    case_items = [i for i in ledger["items"] if not i["id"].startswith("asr-")]
    assert case_items, "the case pack's own evidence must still be in the superset ledger"
    assert len(asr_items) == 12

    # Provenance survives into the frozen record.
    for item in asr_items:
        assert "Assurance envelope" in item["source"]
        assert item["attestation"] == "AUTHORED"

    # The source FAIL is a FAIL in the record, not softened.
    pi = next(i for i in asr_items if i["id"].endswith("prompt-injection-resilience-001"))
    assert "FAIL" in pi["claim"]
    assert pi["category"] == "MEASURED"

    # The indeterminate result and the coverage gaps are UNKNOWN, not passes.
    drift = next(i for i in asr_items if i["id"].endswith("runtime-drift-001"))
    assert drift["category"] == "UNKNOWN"
    assert len([i for i in asr_items if "-uncovered-" in i["id"]]) == 3

    # Economics + report render from that frozen ledger with no model call.
    assert main(["econ", str(CASE_DIR), "--run-id", "slice", "--runs-dir", str(tmp_path)]) == 0
    assert main(["report", "slice", str(CASE_DIR), "--runs-dir", str(tmp_path)]) == 0

    report = (tmp_path / "slice" / "report.html").read_text()
    for item in asr_items:
        assert item["id"] in report, f"{item['id']} missing from the generated report"
    assert "FAIL" in report
    assert "Assurance coverage gap" in report


def test_import_refuses_to_overwrite_an_existing_frozen_ledger(tmp_path, capsys):
    assert _import_into_case(tmp_path) == 0
    assert _import_into_case(tmp_path) == 1
    assert "already exists" in capsys.readouterr().err


def test_cli_refuses_malformed_documents_with_a_controlled_error(tmp_path, capsys):
    """Each of these raised an uncaught AttributeError before 2026-09-11."""
    envelope = json.loads((FIXTURE_DIR / "envelope.json").read_text())
    decision = json.loads((FIXTURE_DIR / "decision.json").read_text())

    cases = {
        "decision-is-an-array": (envelope, []),
        "reason-is-an-int": (envelope, {**decision, "reasons": [7]}),
        "missing-critical-failures": (
            {k: v for k, v in envelope.items() if k != "criticalFailures"},
            decision,
        ),
        "mismatched-capability": (
            envelope,
            {**decision, "state": "PASS", "capabilityRef": {"name": "something-else"}},
        ),
    }

    for label, (env, dec) in cases.items():
        doc_dir = tmp_path / label
        doc_dir.mkdir()
        (doc_dir / "envelope.json").write_text(json.dumps(env))
        (doc_dir / "decision.json").write_text(json.dumps(dec))
        rc = main(["assurance", "import", str(doc_dir), "--attestation", "AUTHORED"])
        err = capsys.readouterr().err
        assert rc == 1, f"{label} should exit non-zero"
        assert "assurance import failed" in err, f"{label} produced no controlled message"


def test_report_renders_from_committed_documents_with_no_assurance_producer_installed():
    """Codex check 4, second half: nothing in the render path can reach a
    producer package, because no producer package is importable at all."""
    import importlib.util

    assert importlib.util.find_spec("hekton_assurance") is None
