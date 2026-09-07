"""kriterion decide / kriterion contract (ADR-006).

HumanDecision and OutcomeContract are always written to separate files from
SyntheticRecommendation — the code path never merges them, and there is no
function in this module that could produce a combined artifact.
"""

from __future__ import annotations

import json
from pathlib import Path

from kriterion.domain.decision import HumanDecision, Measure, OutcomeContract
from kriterion.domain.enums import DecisionAction
from kriterion.domain.serialization import to_dict

# REDUCE is included: it still authorises continued (reduced) funding, so an
# outcome contract's success/guardrail measures remain meaningful. REJECT,
# STOP, HOLD, DEFER, REQUEST_EVIDENCE and DISCOVERY commit no funding and so
# require no contract.
FUNDING_ACTIONS = {DecisionAction.FUND_EXPERIMENT, DecisionAction.PILOT, DecisionAction.SCALE, DecisionAction.REDUCE}


class DecisionError(ValueError):
    pass


def write_human_decision(decision: HumanDecision, out_dir: Path) -> Path:
    out_path = out_dir / "human_decision.json"
    out_path.write_text(json.dumps(to_dict(decision), indent=2, sort_keys=True) + "\n")
    return out_path


def write_outcome_contract(contract: OutcomeContract, out_dir: Path) -> Path:
    out_path = out_dir / "outcome_contract.json"
    out_path.write_text(json.dumps(to_dict(contract), indent=2, sort_keys=True) + "\n")
    return out_path


def load_human_decision(run_dir: Path) -> HumanDecision | None:
    path = run_dir / "human_decision.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text())
    return HumanDecision(
        id=data["id"],
        created_at=data["created_at"],
        action=DecisionAction(data["action"]),
        disposition=data["disposition"],
        overrides=data.get("overrides", []),
        rationale=data.get("rationale", ""),
        owner=data.get("owner", ""),
        decided_at=data.get("decided_at", ""),
    )


def load_outcome_contract(run_dir: Path) -> OutcomeContract | None:
    path = run_dir / "outcome_contract.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text())
    return OutcomeContract(
        id=data["id"],
        created_at=data["created_at"],
        baseline_date=data["baseline_date"],
        measures=[
            Measure(name=m["name"], baseline=m["baseline"], target=m["target"], source_ref=m["source_ref"])
            for m in data.get("measures", [])
        ],
        owner=data["owner"],
        review_date=data["review_date"],
        next_decision=data["next_decision"],
        kill_criteria=data.get("kill_criteria", []),
    )


def validate_run(run_dir: Path) -> list[str]:
    """P0-09 (docs/v0-plan.md Section 7): a funding action without an
    OutcomeContract is a governance violation. Returns a list of violation
    messages — empty means the run is clean. Caller decides the exit code;
    this function performs no I/O side effects beyond reading."""
    violations: list[str] = []
    decision = load_human_decision(run_dir)
    if decision is None:
        return violations  # no decision yet is not itself a violation

    if decision.action in FUNDING_ACTIONS:
        contract_path = run_dir / "outcome_contract.json"
        if not contract_path.is_file():
            violations.append(
                f"HumanDecision action '{decision.action.value}' is a funding action but "
                f"{contract_path} does not exist (P0-09)"
            )
    return violations


def parse_measure_arg(raw: str) -> Measure:
    """CLI syntax: name:baseline:target:source_ref"""
    parts = raw.split(":")
    if len(parts) != 4:
        raise DecisionError(f"--measure must be 'name:baseline:target:source_ref', got: {raw!r}")
    name, baseline, target, source_ref = parts
    return Measure(name=name, baseline=baseline, target=target, source_ref=source_ref)
