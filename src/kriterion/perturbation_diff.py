"""Paired-run action diff (docs/v0-plan.md Section 6: "decision drift
under invariance perturbations, paired-run action diff"). Compares a
baseline run's SyntheticRecommendation against a perturbed run's -- pure
data comparison, no model call. If a P1 perturbation changes the ACTION,
that is the finding (decision drift), not a defect in this tool.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True)
class PerturbationDiffResult:
    baseline_run: str
    perturbed_run: str
    baseline_action: str | None
    perturbed_action: str | None
    action_drifted: bool | None  # None if either run has no recommendation.json yet
    baseline_confidence: str | None
    perturbed_confidence: str | None


def _load_recommendation(run_dir: Path) -> dict | None:
    path = run_dir / "recommendation.json"
    return json.loads(path.read_text()) if path.is_file() else None


def diff_paired_runs(baseline_run_dir: Path, perturbed_run_dir: Path) -> PerturbationDiffResult:
    baseline = _load_recommendation(baseline_run_dir)
    perturbed = _load_recommendation(perturbed_run_dir)
    baseline_action = baseline["action"] if baseline else None
    perturbed_action = perturbed["action"] if perturbed else None
    drifted = (baseline_action != perturbed_action) if (baseline and perturbed) else None
    return PerturbationDiffResult(
        baseline_run=baseline_run_dir.name,
        perturbed_run=perturbed_run_dir.name,
        baseline_action=baseline_action,
        perturbed_action=perturbed_action,
        action_drifted=drifted,
        baseline_confidence=baseline["confidence_band"] if baseline else None,
        perturbed_confidence=perturbed["confidence_band"] if perturbed else None,
    )
