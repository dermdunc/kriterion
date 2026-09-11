"""The accountable-human path, end to end, through the real CLI.

No committed run has a `human_decision.json` or an `outcome_contract.json`,
deliberately: an agent recording an accountable human's act is the single worst
thing this instrument could do (RISK-0011). The cost of that discipline is that
the renderer's human-decision and outcome-contract branches would otherwise
never execute against real data.

So this test drives the real lifecycle — `kriterion decide`, `kriterion
contract`, `kriterion validate-run`, `kriterion decision-page` — over a
throwaway copy of the canonical run in `tmp_path`, and asserts on what a human
would actually see at each stage. Nothing it writes is ever committed.

It exists because exercising exactly this path found a real defect: with a
synthetic DEFER and a human PILOT both recorded, the page's single "capital at
risk" figure read as the decision's exposure while describing only the
machine's suggestion.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from kriterion.cli import DECISION_PAGE_CREATED_AT
from kriterion.decision_state import load_decision_state
from kriterion.narrative import check
from kriterion.report.decision_page import render_decision_page

REPO_ROOT = Path(__file__).parent.parent.parent
CASE_DIR = REPO_ROOT / "cases" / "coding-agent-rollout"
ASSURANCE_IMPORT = CASE_DIR / "assurance" / "imported.json"
CANONICAL_RUN = REPO_ROOT / "runs" / "caseA-condC-s5"


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "kriterion.cli", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def _region(page: str, role: str) -> str:
    match = re.search(
        r'<section[^>]*data-kriterion-role="' + role + r'"[^>]*>(.*?)</section>', page, re.S
    )
    assert match is not None, f"no {role!r} region on the page"
    return match.group(1)


def _render(run_dir: Path) -> tuple[object, str]:
    state = load_decision_state(
        case_dir=CASE_DIR,
        run_dir=run_dir,
        created_at=DECISION_PAGE_CREATED_AT,
        assurance_import_path=ASSURANCE_IMPORT,
    )
    page = render_decision_page(state)
    assert check(state, page) == [], "the rendered page must satisfy every invariant"
    return state, page


@pytest.fixture
def run_dir(tmp_path) -> Path:
    runs = tmp_path / "runs"
    runs.mkdir()
    target = runs / "lifecycle"
    shutil.copytree(CANONICAL_RUN, target)
    return target


def test_stage_1_undecided_says_so_and_does_not_imply_the_machine_decided(run_dir):
    state, page = _render(run_dir)
    assert state.human_decision is None
    human = _region(page, "human-decision")
    assert "No human decision has been recorded" in human
    assert "kriterion decide" in human  # the page names the actual next act
    contract = _region(page, "outcome-contract")
    assert "no human decision has been recorded" in contract.lower()


def test_stage_2_a_funding_decision_without_a_contract_is_reported_as_a_violation(run_dir):
    decided = _cli(
        "decide", run_dir.name, "--runs-dir", str(run_dir.parent),
        "--action", "PILOT", "--disposition", "modify",
        "--owner", "lifecycle-test", "--rationale", "Test fixture, not a real decision.",
    )
    assert decided.returncode == 0, decided.stderr
    assert "run `kriterion contract`" in decided.stderr  # warned at the point of the act

    validated = _cli("validate-run", run_dir.name, "--runs-dir", str(run_dir.parent))
    assert validated.returncode == 1
    assert "P0-09" in validated.stdout + validated.stderr

    state, page = _render(run_dir)
    assert state.human_decision.action.value == "PILOT"
    assert state.outcome_contract is None
    contract = _region(page, "outcome-contract")
    assert "governance violation" in contract
    human = _region(page, "human-decision")
    assert "kriterion contract" in human


def test_stage_2_the_machine_and_the_human_never_share_a_field(run_dir):
    """The synthetic recommendation is DEFER; the human decision is PILOT.
    Both must be visible, in their own regions, neither restated as the other.
    """
    _cli(
        "decide", run_dir.name, "--runs-dir", str(run_dir.parent),
        "--action", "PILOT", "--disposition", "modify", "--owner", "lifecycle-test",
    )
    state, page = _render(run_dir)
    assert state.recommendation.action.value == "DEFER"
    assert state.human_decision.action.value == "PILOT"

    machine = _region(page, "synthetic-recommendation")
    human = _region(page, "human-decision")
    assert "DEFER" in machine and "PILOT" not in machine
    assert "PILOT" in human
    # The human region may not render any field of the recommendation record.
    assert 'data-kriterion-source="recommendation.' not in human


def test_stage_2_capital_at_risk_is_never_ambiguous_between_the_two_actors(run_dir):
    """The defect this file was written for. `capital_at_risk_gbp` describes
    the machine's suggestion only; with a human funding decision recorded, a
    reader must not be able to read it as the decision's exposure."""
    _cli(
        "decide", run_dir.name, "--runs-dir", str(run_dir.parent),
        "--action", "PILOT", "--disposition", "modify", "--owner", "lifecycle-test",
    )
    state, page = _render(run_dir)
    assert state.capital_at_risk_gbp == 0.0  # DEFER commits nothing
    assert "Capital the machine's suggestion would put at risk" in page
    # And the human's own commitment is stated in its own words, with the
    # honest admission that no amount is recorded on the decision record.
    assert "PILOT authorises funding" in state.human_capital_commitment
    assert "no amount" in state.human_capital_commitment
    assert state.human_capital_commitment in page.replace("&#x27;", "'")


def test_stage_3_a_contracted_decision_validates_and_renders_its_commitments(run_dir):
    _cli(
        "decide", run_dir.name, "--runs-dir", str(run_dir.parent),
        "--action", "PILOT", "--disposition", "modify", "--owner", "lifecycle-test",
    )
    contracted = _cli(
        "contract", run_dir.name, "--runs-dir", str(run_dir.parent),
        "--baseline-date", "2026-09-30", "--review-date", "2027-03-31",
        "--next-decision", "SCALE or STOP at review", "--owner", "lifecycle-test",
        "--measure", "time-to-merge:9.6h:6.0h:ev-002",
        "--kill-criteria", "attribution study shows under 8% attributable uplift",
    )
    assert contracted.returncode == 0, contracted.stderr

    validated = _cli("validate-run", run_dir.name, "--runs-dir", str(run_dir.parent))
    assert validated.returncode == 0, validated.stdout + validated.stderr

    state, page = _render(run_dir)
    assert state.outcome_contract is not None
    contract = _region(page, "outcome-contract")
    assert "2027-03-31" in contract
    assert "time-to-merge" in contract
    assert "ev-002" in contract
    assert "attribution study" in contract
    # Once a contract exists, "what happens next" becomes the review date.
    assert "2027-03-31" in state.next_step
    assert "kriterion decide" not in state.next_step


def test_the_decision_and_the_contract_are_always_separate_files(run_dir):
    """ADR-006 is structural, not stylistic: no code path produces a merged
    artifact, and the page reads two files."""
    _cli(
        "decide", run_dir.name, "--runs-dir", str(run_dir.parent),
        "--action", "DEFER", "--disposition", "accept", "--owner", "lifecycle-test",
    )
    decision = json.loads((run_dir / "human_decision.json").read_text())
    recommendation = json.loads((run_dir / "recommendation.json").read_text())
    assert (run_dir / "recommendation.json").is_file()
    assert set(decision) & set(recommendation) == {
        "action", "created_at", "id", "schema_version"
    }
    assert decision["id"] != recommendation["id"]


def test_a_non_funding_human_decision_requires_no_contract(run_dir):
    _cli(
        "decide", run_dir.name, "--runs-dir", str(run_dir.parent),
        "--action", "DEFER", "--disposition", "accept", "--owner", "lifecycle-test",
    )
    validated = _cli("validate-run", run_dir.name, "--runs-dir", str(run_dir.parent))
    assert validated.returncode == 0
    state, page = _render(run_dir)
    assert "commits no funding" in state.outcome_contract_status
    assert "commits no funding" in state.human_capital_commitment
