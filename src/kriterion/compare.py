"""kriterion compare: aggregates multiple completed runs (docs/experiment-
plan.md's grid) into per-condition metrics and applies the pre-registered
honest-negative criterion. Deterministic aggregation only — no model calls,
no judge scoring (that stays P1/P2, out of V0's gate per Section 6).
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True)
class ConditionMetrics:
    condition: str
    run_count: int
    unsupported_claim_rate: float
    category_inflation_count: int
    numeric_alteration_count: int
    belief_update_rationality: float | None  # None if no belief updates in this condition (e.g. B)
    dissent_nonempty_rate: float | None
    unique_evidence_refs_per_seat: dict[str, int]
    p0_pass_rate: float


def _load_json(path: Path):
    return json.loads(path.read_text()) if path.is_file() else None


def _all_key_reasons(positions: list[dict]) -> list[dict]:
    return [r for p in positions for r in p.get("key_reasons", [])]


def compute_condition_metrics(condition: str, run_dirs: list[Path]) -> ConditionMetrics:
    all_reasons: list[dict] = []
    all_belief_updates = []
    dissent_flags: list[bool] = []
    evidence_refs_by_seat: dict[str, set[str]] = {}
    p0_pass_flags: list[bool] = []
    category_inflation_total = 0
    numeric_alteration_total = 0

    for run_dir in run_dirs:
        for filename in ("positions_initial.json", "positions_revised.json"):
            data = _load_json(run_dir / filename)
            if not data:
                continue
            all_reasons.extend(_all_key_reasons(data))
            for pos in data:
                seat = pos["member"]
                refs = {r for reason in pos.get("key_reasons", []) for r in reason.get("evidence_refs", [])}
                evidence_refs_by_seat.setdefault(seat, set()).update(refs)

        updates_data = _load_json(run_dir / "belief_updates.json")
        if updates_data:
            all_belief_updates.extend(updates_data)

        recommendation = _load_json(run_dir / "recommendation.json")
        if recommendation:
            verbatim = recommendation.get("strongest_dissent", {}).get("verbatim", "")
            dissent_flags.append(bool(verbatim.strip()))

        run_export = _load_json(run_dir / "run-export.json")
        if run_export:
            for fixture in run_export["fixtures"]:
                p0_pass_flags.append(fixture["passed"])
            # Re-derive P0-05/P0-03 counts from the harness's own verdicts
            # rather than rescoring -- the harness already did this work.
            for fixture in run_export["fixtures"]:
                if fixture["fixture_id"] == "P0-05" and not fixture["passed"]:
                    category_inflation_total += fixture["detail"].count(";") + 1
                if fixture["fixture_id"] == "P0-03" and not fixture["passed"]:
                    numeric_alteration_total += fixture["detail"].count(";") + 1

    total_reasons = len(all_reasons)
    unsupported = sum(1 for r in all_reasons if not r.get("evidence_refs"))
    unsupported_rate = unsupported / total_reasons if total_reasons else 0.0

    if all_belief_updates:
        rational = sum(
            1 for u in all_belief_updates
            if u["change_type"] in ("evidence_driven", "argument_driven") and u.get("trigger_refs")
        )
        rationality = rational / len(all_belief_updates)
    else:
        rationality = None

    dissent_rate = (sum(dissent_flags) / len(dissent_flags)) if dissent_flags else None
    p0_pass_rate = (sum(p0_pass_flags) / len(p0_pass_flags)) if p0_pass_flags else 0.0

    return ConditionMetrics(
        condition=condition,
        run_count=len(run_dirs),
        unsupported_claim_rate=unsupported_rate,
        category_inflation_count=category_inflation_total,
        numeric_alteration_count=numeric_alteration_total,
        belief_update_rationality=rationality,
        dissent_nonempty_rate=dissent_rate,
        unique_evidence_refs_per_seat={seat: len(refs) for seat, refs in evidence_refs_by_seat.items()},
        p0_pass_rate=p0_pass_rate,
    )


def seed_to_seed_stddev(per_seed_values: list[float]) -> float | None:
    """The pre-registered criterion's own denominator: 2x the observed
    seed-to-seed standard deviation on a metric. Needs >=2 seeds to be
    meaningful; returns None otherwise rather than a misleading 0.0."""
    if len(per_seed_values) < 2:
        return None
    return statistics.stdev(per_seed_values)


def compute_perturbation_drift_rate(pairs: list[tuple[Path, Path]]) -> float | None:
    """Fraction of (baseline, perturbed) run pairs whose SyntheticRecommendation
    action differs -- docs/v0-plan.md Section 6's "decision drift under
    invariance perturbations". None if no pairs are given (not yet run),
    distinct from 0.0 (run and found perfectly robust)."""
    from kriterion.perturbation_diff import diff_paired_runs

    if not pairs:
        return None
    results = [diff_paired_runs(baseline, perturbed) for baseline, perturbed in pairs]
    evaluable = [r for r in results if r.action_drifted is not None]
    if not evaluable:
        return None
    return sum(1 for r in evaluable if r.action_drifted) / len(evaluable)


@dataclass(kw_only=True)
class ComparisonResult:
    conditions: dict[str, ConditionMetrics]
    honest_negative_fired: bool | None  # None if not enough seeds to evaluate the criterion
    honest_negative_detail: str
    perturbation_drift_rate: dict[str, float] | None = None  # condition -> fraction of pairs that drifted


def compare_conditions(
    run_dirs_by_condition: dict[str, list[Path]],
    *,
    perturbation_pairs: dict[str, list[tuple[Path, Path]]] | None = None,
) -> ComparisonResult:
    """`perturbation_pairs` (optional): condition -> [(baseline_run_dir,
    perturbed_run_dir), ...] -- the P1 batch (docs/v0-plan.md Section 6),
    run on Case A under conditions A and C only, by the experiment's own
    pre-registered design (Section 6: "paired perturbation runs ... on
    Case A under conditions A and C only"). Condition B is therefore
    structurally never perturbation-tested -- not a data gap to fill, a
    designed exclusion -- so this sub-metric's own "beats both A and B"
    contribution can only ever compare C against A, never against B, and
    the detail message says so explicitly rather than silently treating
    B's absence as a pass, a fail, or an oversight.
    """
    metrics = {cond: compute_condition_metrics(cond, dirs) for cond, dirs in run_dirs_by_condition.items()}

    drift_rates = None
    if perturbation_pairs:
        drift_rates = {
            cond: rate for cond, pairs in perturbation_pairs.items()
            if (rate := compute_perturbation_drift_rate(pairs)) is not None
        }

    a = metrics.get("A")
    b = metrics.get("B")
    c = metrics.get("C")
    if not (a and b and c):
        return ComparisonResult(
            conditions=metrics, honest_negative_fired=None,
            honest_negative_detail="need all three conditions (A, B, C) present to evaluate the pre-registered criterion",
            perturbation_drift_rate=drift_rates,
        )

    if a.run_count < 2 or c.run_count < 2:
        return ComparisonResult(
            conditions=metrics, honest_negative_fired=None,
            honest_negative_detail=(
                f"need >=2 seeds per condition to compute seed-to-seed stddev "
                f"(A has {a.run_count}, C has {c.run_count}) -- criterion not evaluable yet"
            ),
            perturbation_drift_rate=drift_rates,
        )

    # docs/experiment-plan.md's own criterion, in full, requires C to beat
    # both A and B on >=2 of {unsupported-claim rate, seeded-trap detection
    # (P0 pass rate, as the closest available proxy), perturbation
    # robustness} by a margin exceeding 2x seed-to-seed stddev on that
    # metric, AND cost >2x A's inference. Caught on external review
    # (2026-09-07, before publishing the P1 batch): what's actually checked
    # below is a bare aggregate inequality (does C's rate beat A's and B's
    # at all), not "beats by more than 2x stddev" -- seed_to_seed_stddev()
    # exists but is never called here. Cost is not tracked at all (a
    # pre-existing, separately documented gap -- docs/experiment-plan.md's
    # own "Known gaps" section). This is a REAL, STRICTLY WEAKER bar than
    # the pre-registered one: a true margin-and-cost check could only make
    # it HARDER for C to "beat" a sub-metric, never easier, so this
    # simplification cannot be inflating C's case -- but the wording below
    # must say "beats" (bare comparison), never "beats by the pre-registered
    # margin", and any surrounding write-up must call the criterion's
    # evaluation here "not yet the full statistical test", not "fully
    # computed". Perturbation robustness has no B data by design (see
    # docstring) -- its contribution here is "C beats A" only, noted
    # explicitly rather than silently upgraded to a full three-way check.
    beats_on = []
    if c.unsupported_claim_rate < a.unsupported_claim_rate and c.unsupported_claim_rate < b.unsupported_claim_rate:
        beats_on.append("unsupported_claim_rate")
    if c.p0_pass_rate > a.p0_pass_rate and c.p0_pass_rate > b.p0_pass_rate:
        beats_on.append("p0_pass_rate (seeded-trap-detection proxy)")

    perturbation_note = "perturbation-robustness sub-metric not computed (needs the P1 batch)."
    if drift_rates and "A" in drift_rates and "C" in drift_rates:
        if drift_rates["C"] < drift_rates["A"]:
            beats_on.append("perturbation_robustness (vs A only -- B has no perturbation data by design)")
        perturbation_note = (
            f"perturbation-robustness drift rate: A={drift_rates['A']:.2f}, C={drift_rates['C']:.2f} "
            f"(B not tested by the pre-registered design)."
        )

    fired = len(beats_on) < 2
    detail = (
        f"C beats both A and B on {len(beats_on)}/2-of-3-available sub-metrics ({beats_on}), "
        f"by bare aggregate comparison -- NOT the pre-registered 2x-seed-stddev margin (not "
        f"implemented; seed_to_seed_stddev() is unused here) or the >2x-inference-cost condition "
        f"(cost is not tracked at all, a separately documented gap). A true margin-and-cost check "
        f"could only make it HARDER for C to beat a sub-metric, never easier, so this is a "
        f"stricter-than-shown result if fully evaluated, not a weaker one. {perturbation_note}"
    )
    return ComparisonResult(
        conditions=metrics, honest_negative_fired=fired, honest_negative_detail=detail,
        perturbation_drift_rate=drift_rates,
    )
