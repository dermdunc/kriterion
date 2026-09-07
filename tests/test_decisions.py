import json

import pytest

from kriterion.decisions import (
    DecisionError,
    parse_measure_arg,
    validate_run,
    write_human_decision,
    write_outcome_contract,
)
from kriterion.domain.decision import HumanDecision, Measure, OutcomeContract
from kriterion.domain.enums import DecisionAction


def _decision(action):
    return HumanDecision(
        id="run-1-human-decision",
        created_at="2026-09-05T00:00:00Z",
        action=action,
        disposition="accept",
        rationale="r",
        owner="cio",
        decided_at="2026-09-05T00:00:00Z",
    )


def test_write_human_decision_creates_a_separate_file(tmp_path):
    out_path = write_human_decision(_decision(DecisionAction.PILOT), tmp_path)
    assert out_path.name == "human_decision.json"
    assert out_path.is_file()
    data = json.loads(out_path.read_text())
    assert data["action"] == "PILOT"
    # ADR-006: never merged with a recommendation.
    assert not (tmp_path / "recommendation.json").exists()


def test_validate_run_clean_when_no_decision_yet(tmp_path):
    assert validate_run(tmp_path) == []


def test_validate_run_flags_funding_action_without_contract(tmp_path):
    write_human_decision(_decision(DecisionAction.SCALE), tmp_path)
    violations = validate_run(tmp_path)
    assert len(violations) == 1
    assert "P0-09" in violations[0]


def test_validate_run_clean_when_funding_action_has_contract(tmp_path):
    write_human_decision(_decision(DecisionAction.SCALE), tmp_path)
    contract = OutcomeContract(
        id="run-1-outcome-contract", created_at="2026-09-05T00:00:00Z",
        baseline_date="2026-09-05", measures=[Measure(name="m", baseline="b", target="t", source_ref="ev-001")],
        owner="cio", review_date="2026-12-05", next_decision="review",
    )
    write_outcome_contract(contract, tmp_path)
    assert validate_run(tmp_path) == []


def test_validate_run_clean_for_non_funding_action_without_contract(tmp_path):
    write_human_decision(_decision(DecisionAction.DEFER), tmp_path)
    assert validate_run(tmp_path) == []


def test_parse_measure_arg_valid():
    measure = parse_measure_arg("cycle_time:9.6h:6h:ev-002")
    assert measure == Measure(name="cycle_time", baseline="9.6h", target="6h", source_ref="ev-002")


def test_parse_measure_arg_rejects_wrong_field_count():
    with pytest.raises(DecisionError, match="name:baseline:target:source_ref"):
        parse_measure_arg("cycle_time:9.6h")
