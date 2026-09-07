"""Integration tests for the eval harness against constructed run
directories -- not live model output, but real file-shaped fixtures
matching exactly what cli.py's _cmd_run/_cmd_econ/_cmd_ledger_freeze write."""

import json
from pathlib import Path

from kriterion.casepack import load_case_pack
from kriterion.domain.serialization import to_dict
from kriterion.economics.case_flows import compute_economics
from kriterion.evals.harness import run_eval_harness, write_run_export
from kriterion.ledger import freeze, write_frozen_ledger

CASE_A_DIR = Path(__file__).parent.parent.parent / "cases" / "coding-agent-rollout"


def _build_case_a_run(run_dir: Path) -> None:
    """A run directory with real economics + ledger, but no positions --
    the shape of a run that only got as far as `kriterion econ`."""
    case, items, assumptions = load_case_pack(CASE_A_DIR, created_at="2026-09-05T00:00:00Z")
    assumptions_by_id = {a.id: a for a in assumptions}
    economics = compute_economics(case.id, case.ask.amount_gbp, assumptions_by_id)
    run_dir.mkdir(parents=True)
    (run_dir / "economics.json").write_text(json.dumps(to_dict(economics), indent=2, sort_keys=True))
    ledger = freeze(items, ledger_id="case-a-ledger", created_at="2026-09-05T00:00:00Z")
    write_frozen_ledger(ledger, run_dir / "ledger.frozen.json")


def test_harness_runs_all_ten_fixtures_and_produces_verdicts(tmp_path):
    run_dir = tmp_path / "run-1"
    _build_case_a_run(run_dir)

    verdicts = run_eval_harness(run_dir, "coding-agent-rollout")
    fixture_ids = {v.fixture_id for v in verdicts}
    assert fixture_ids == {f"P0-{i:02d}" for i in range(1, 11)}


def test_harness_p0_01_and_p0_02_pass_on_real_case_a_economics(tmp_path):
    run_dir = tmp_path / "run-1"
    _build_case_a_run(run_dir)
    verdicts = {v.fixture_id: v for v in run_eval_harness(run_dir, "coding-agent-rollout")}
    assert verdicts["P0-01"].passed
    assert verdicts["P0-02"].passed


def test_harness_p0_09_flags_missing_contract_after_funding_decision(tmp_path):
    from kriterion.decisions import write_human_decision
    from kriterion.domain.decision import HumanDecision
    from kriterion.domain.enums import DecisionAction

    run_dir = tmp_path / "run-1"
    _build_case_a_run(run_dir)
    write_human_decision(
        HumanDecision(id="d1", created_at="2026-09-05T00:00:00Z", action=DecisionAction.SCALE, disposition="accept", owner="cio"),
        run_dir,
    )
    verdicts = {v.fixture_id: v for v in run_eval_harness(run_dir, "coding-agent-rollout")}
    assert not verdicts["P0-09"].passed


def test_harness_reports_not_applicable_for_missing_data_rather_than_crashing(tmp_path):
    run_dir = tmp_path / "empty-run"
    run_dir.mkdir()
    verdicts = run_eval_harness(run_dir, "coding-agent-rollout")
    assert len(verdicts) == 10
    # An empty run should be reported honestly, not silently all-green
    # without qualification -- every non-P0-09 verdict should say why.
    for v in verdicts:
        if v.fixture_id != "P0-09":
            assert "not_applicable" in v.detail


def test_p0_06_not_applicable_on_genuine_unanimous_convergence(tmp_path):
    """Regression test for a real bug caught live on Case A: a run where
    all 5 members (including CISO) genuinely converged on the same action
    must be reported not_applicable for P0-06, not scored as a failure --
    it isn't the seeded 4-vs-1 dissent scenario the fixture describes."""
    run_dir = tmp_path / "run-1"
    _build_case_a_run(run_dir)

    def _positions(phase):
        return [
            {
                "id": f"p-{seat}-{phase}", "created_at": "2026-09-05T00:00:00Z", "member": seat,
                "phase": phase, "recommendation": "DEFER", "confidence_band": "MEDIUM",
                "key_reasons": [], "blocking_unknowns": ["shared open question"],
            }
            for seat in ["cfo", "cto", "ciso", "cro_compliance", "business_executive"]
        ]

    belief_updates = [
        {
            "id": "b-ciso", "created_at": "2026-09-05T00:00:00Z", "member": "ciso",
            "initial_position": "DEFER", "initial_confidence": "MEDIUM",
            "revised_position": "DEFER", "revised_confidence": "MEDIUM",
            "change_type": "evidence_driven", "trigger_refs": [], "stated_reason": "r",
        }
    ]
    # Genuine 5-0 convergence at BOTH phase 3 (initial) and phase 7 (revised)
    # -- eligibility is judged on the initial/seeded shape now, so the
    # initial positions must show the same real unanimity for this
    # regression to still exercise the scenario it names.
    (run_dir / "positions_initial.json").write_text(json.dumps(_positions("initial")))
    (run_dir / "positions_revised.json").write_text(json.dumps(_positions("revised")))
    (run_dir / "belief_updates.json").write_text(json.dumps(belief_updates))

    verdicts = {v.fixture_id: v for v in run_eval_harness(run_dir, "coding-agent-rollout")}
    assert verdicts["P0-06"].passed
    assert "not_applicable" in verdicts["P0-06"].detail


def test_p0_06_passes_when_ciso_diverges_further_via_real_evidence(tmp_path):
    """Regression test for a real bug caught live in the 2026-09-06
    pre-registered batch (runs/caseC-condC-s2): CISO was the seeded 4-vs-1
    minority, updated its OWN recommendation for cited evidentiary reasons,
    and ended up diverging FURTHER from the majority action than before --
    the opposite of folding to conformity pressure. The old scorer flagged
    this as a P0-06 failure just because change_type wasn't literally
    no_change; it must pass."""
    run_dir = tmp_path / "run-1"
    _build_case_a_run(run_dir)

    def _majority_and_ciso(phase, ciso_action, ciso_unknowns):
        positions = [
            {
                "id": f"p-{seat}-{phase}", "created_at": "2026-09-05T00:00:00Z", "member": seat,
                "phase": phase, "recommendation": "DEFER", "confidence_band": "MEDIUM",
                "key_reasons": [], "blocking_unknowns": ["shared open question"],
            }
            for seat in ["cfo", "cto", "cro_compliance", "business_executive"]
        ]
        positions.append({
            "id": f"p-ciso-{phase}", "created_at": "2026-09-05T00:00:00Z", "member": "ciso",
            "phase": phase, "recommendation": ciso_action, "confidence_band": "MEDIUM",
            "key_reasons": [], "blocking_unknowns": ciso_unknowns,
        })
        return positions

    belief_updates = [
        {
            "id": "b-ciso", "created_at": "2026-09-05T00:00:00Z", "member": "ciso",
            "initial_position": "REQUEST_EVIDENCE", "initial_confidence": "MEDIUM",
            "revised_position": "DISCOVERY", "revised_confidence": "MEDIUM",
            "change_type": "evidence_driven", "trigger_refs": ["ev-001"], "stated_reason": "r",
        }
    ]
    (run_dir / "positions_initial.json").write_text(
        json.dumps(_majority_and_ciso("initial", "REQUEST_EVIDENCE", ["unanswered concern"]))
    )
    (run_dir / "positions_revised.json").write_text(
        json.dumps(_majority_and_ciso("revised", "DISCOVERY", ["unanswered concern"]))
    )
    (run_dir / "belief_updates.json").write_text(json.dumps(belief_updates))

    verdicts = {v.fixture_id: v for v in run_eval_harness(run_dir, "coding-agent-rollout")}
    assert verdicts["P0-06"].passed
    assert "not_applicable" not in verdicts["P0-06"].detail


def test_write_run_export_creates_valid_json(tmp_path):
    run_dir = tmp_path / "run-1"
    _build_case_a_run(run_dir)
    out_path = write_run_export(run_dir, "coding-agent-rollout")
    assert out_path.is_file()
    data = json.loads(out_path.read_text())
    assert data["case_id"] == "coding-agent-rollout"
    assert len(data["fixtures"]) == 10
    assert isinstance(data["all_green"], bool)
