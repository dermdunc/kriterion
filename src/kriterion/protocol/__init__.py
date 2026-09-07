"""Deliberation protocol (docs/v0-plan.md Section 5). Phases 0-8, Baseline A
and Baseline B all live here."""

from kriterion.protocol.aggregate import BaselineBResult, aggregate_baseline_b
from kriterion.protocol.baseline_a import BaselineAResult, run_baseline_a
from kriterion.protocol.chair import ChairResult, synthesize
from kriterion.protocol.challenge import ChallengeRoundResult, run_phase5_challenge
from kriterion.protocol.gap_scan import GapScanResult, scan_contradictions_and_gaps
from kriterion.protocol.phases import (
    AssessmentOutcome,
    RevisionOutcome,
    SealedTally,
    run_phase3_independent_assessment,
    run_phase7_revised_assessment,
    seal_phase4_tally,
)

__all__ = [
    "AssessmentOutcome",
    "BaselineAResult",
    "BaselineBResult",
    "ChairResult",
    "ChallengeRoundResult",
    "GapScanResult",
    "RevisionOutcome",
    "SealedTally",
    "aggregate_baseline_b",
    "run_baseline_a",
    "run_phase3_independent_assessment",
    "run_phase5_challenge",
    "run_phase7_revised_assessment",
    "scan_contradictions_and_gaps",
    "seal_phase4_tally",
    "synthesize",
]
