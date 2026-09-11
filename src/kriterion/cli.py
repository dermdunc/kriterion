"""Kriterion command-line entry point."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from kriterion import __version__
from kriterion.casepack import CasePackError, load_case_pack
from kriterion.charters import CharterError, load_all_charters
from kriterion.decisions import (
    FUNDING_ACTIONS,
    DecisionError,
    load_human_decision,
    parse_measure_arg,
    validate_run,
    write_human_decision,
    write_outcome_contract,
)
from kriterion.domain.decision import HumanDecision, OutcomeContract
from kriterion.domain.enums import DecisionAction
from kriterion.domain.serialization import to_dict
from kriterion.economics import CASE_ECONOMICS_FUNCTIONS
from kriterion.ledger import freeze, write_frozen_ledger


def _cmd_doctor(_args: argparse.Namespace) -> int:
    from kriterion.executors.hekton_local import HektonLocalExecutor

    executor = HektonLocalExecutor()
    status = executor.doctor()

    if not status.get("ok"):
        print("kriterion doctor: NOT READY", file=sys.stderr)
        if "reason" in status:
            print(f"  cannot reach Ollama: {status['reason']}", file=sys.stderr)
        else:
            print(
                f"  target model '{status['target_model']}' not found among "
                f"{status['available_models']}",
                file=sys.stderr,
            )
        return 1

    print("kriterion doctor: READY")
    print(f"  Ollama reachable at {status['base_url']}")
    print(f"  target model '{status['target_model']}' available")

    smoke = executor.complete('Reply with exactly this JSON: {"ok": true}', fmt="json", seed=0)
    print(f"  smoke completion ({smoke.elapsed_seconds:.2f}s): {smoke.text!r}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    from kriterion.casepack import load_injection
    from kriterion.domain.serialization import to_dict
    from kriterion.executors.hekton_local import HektonLocalExecutor
    from kriterion.protocol import (
        aggregate_baseline_b,
        run_baseline_a,
        run_phase3_independent_assessment,
        run_phase5_challenge,
        run_phase7_revised_assessment,
        synthesize,
    )

    case_dir = Path(args.case_dir)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        case, items, _assumptions = load_case_pack(case_dir, created_at=created_at)
        assumptions_by_id = {a.id: a for a in _assumptions}
        charters = load_all_charters(Path("charters"), created_at=created_at)
    except (CasePackError, CharterError) as exc:
        print(f"kriterion: run failed: {exc}", file=sys.stderr)
        return 1

    if args.perturbation:
        from kriterion.perturbations import PERTURBATIONS

        case, items = PERTURBATIONS[args.perturbation](case, items)
        print(f"kriterion: applied perturbation '{args.perturbation}' (docs/v0-plan.md Section 7, P1)")

    econ_fn = CASE_ECONOMICS_FUNCTIONS.get(case.id)
    if econ_fn is None:
        print(f"kriterion: run failed: no cash-flow model wired for case '{case.id}' yet", file=sys.stderr)
        return 1

    evidence_by_id = {item.id: item for item in items}
    economics = econ_fn(case.id, case.ask.amount_gbp, assumptions_by_id)
    executor = HektonLocalExecutor()

    run_id = args.run_id or f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir = Path(args.runs_dir) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.condition == "A":
        injection_path = case_dir / "injection.toml"
        injected = load_injection(injection_path, created_at=created_at) if injection_path.is_file() else []
        result = run_baseline_a(
            executor, list(charters.values()), case, items, injected, economics,
            seed=args.seed, created_at=created_at, run_id=run_id,
        )
        (out_dir / "recommendation.json").write_text(
            json.dumps(to_dict(result.recommendation), indent=2, sort_keys=True) + "\n"
        )
        (out_dir / "belief_update.json").write_text(
            json.dumps(to_dict(result.belief_update), indent=2, sort_keys=True) + "\n"
        )
        (out_dir / "belief_updates.json").write_text(
            json.dumps([to_dict(result.belief_update)], indent=2, sort_keys=True) + "\n"
        )
        if result.initial_position is not None:
            (out_dir / "positions_initial.json").write_text(
                json.dumps([to_dict(result.initial_position)], indent=2, sort_keys=True) + "\n"
            )
        print(f"kriterion: Baseline A complete -> {out_dir} ({len(result.calls)} model calls)")
        print(f"kriterion: final action = {result.recommendation.action.value}")
        return 0

    if args.condition == "B":
        outcomes = [
            run_phase3_independent_assessment(
                executor, charter, case, evidence_by_id, economics,
                seed=args.seed, created_at=created_at, run_id=run_id,
            )
            for charter in charters.values()
        ]
        ok_positions = [o.position for o in outcomes if o.status == "ok" and o.position is not None]
        abstained = [o.member.value for o in outcomes if o.status == "abstained_error"]
        if not ok_positions:
            print("kriterion: run failed: every Baseline B member abstained_error", file=sys.stderr)
            return 1
        result = aggregate_baseline_b(ok_positions)
        (out_dir / "positions_initial.json").write_text(
            json.dumps([to_dict(p) for p in ok_positions], indent=2, sort_keys=True) + "\n"
        )
        (out_dir / "baseline_b_result.json").write_text(
            json.dumps(to_dict(result), indent=2, sort_keys=True) + "\n"
        )
        print(f"kriterion: Baseline B complete -> {out_dir} ({len(ok_positions)}/5 members responded)")
        print(f"kriterion: modal action = {result.modal_action.value} ({result.modal_action_count}/{result.total_positions})")
        if abstained:
            print(f"kriterion: abstained_error members: {abstained}", file=sys.stderr)
        return 0

    if args.condition == "D":
        from kriterion.executors.hekton_local import TREATMENT_D_MODEL_BY_SEAT

        # A different model per seat, per charter -- everything else about
        # this branch is Condition C's own protocol, verbatim. The chair's
        # one bounded narrative call still uses the shared baseline default
        # (`executor` above): the chair is not a sixth persona, and keeping
        # its treatment identical across B/C/D is deliberate (docs/v0-plan.md
        # Section 5's own fairness requirement, extended here).
        executor_by_seat = {seat: HektonLocalExecutor(model=model) for seat, model in TREATMENT_D_MODEL_BY_SEAT.items()}

        phase3_outcomes_d = [
            run_phase3_independent_assessment(
                executor_by_seat[charter.seat], charter, case, evidence_by_id, economics,
                seed=args.seed, created_at=created_at, run_id=run_id,
            )
            for charter in charters.values()
        ]
        initial_positions = [o.position for o in phase3_outcomes_d if o.status == "ok" and o.position is not None]
        abstained_phase3 = [o.member.value for o in phase3_outcomes_d if o.status == "abstained_error"]
        if len(initial_positions) < 2:
            print(
                f"kriterion: run failed: only {len(initial_positions)}/5 members produced a valid "
                f"initial position (abstained: {abstained_phase3}) -- cannot run challenge/revision",
                file=sys.stderr,
            )
            return 1

        charters_by_seat = {c.seat: c for c in charters.values()}
        challenge_result = run_phase5_challenge(
            None, case, items, economics, initial_positions, charters_by_seat,
            seed=args.seed, created_at=created_at, run_id=run_id,
            executor_by_seat=executor_by_seat,
        )
        all_challenges = [challenge_result.case_for, challenge_result.case_against] + challenge_result.premortems

        injection_path = case_dir / "injection.toml"
        injected = load_injection(injection_path, created_at=created_at) if injection_path.is_file() else []
        ledger_v2_items = items + injected
        new_evidence_ids = {item.id for item in injected}

        revision_outcomes = [
            run_phase7_revised_assessment(
                executor_by_seat[position.member], position, charters_by_seat[position.member], case, ledger_v2_items,
                all_challenges, economics, new_evidence_ids=new_evidence_ids,
                seed=args.seed, created_at=created_at, run_id=run_id,
            )
            for position in initial_positions
        ]
        revised_positions = [o.revised_position for o in revision_outcomes if o.status == "ok" and o.revised_position is not None]
        belief_updates = [o.belief_update for o in revision_outcomes if o.status == "ok" and o.belief_update is not None]
        abstained_phase7 = [o.member.value for o in revision_outcomes if o.status == "abstained_error"]
        if not revised_positions:
            print("kriterion: run failed: every member abstained_error at phase 7", file=sys.stderr)
            return 1

        chair_result = synthesize(
            executor, case, revised_positions, challenge_result.case_against,
            seed=args.seed, created_at=created_at, run_id=run_id,
        )

        (out_dir / "positions_initial.json").write_text(
            json.dumps([to_dict(p) for p in initial_positions], indent=2, sort_keys=True) + "\n"
        )
        (out_dir / "challenges.json").write_text(
            json.dumps([to_dict(c) for c in all_challenges], indent=2, sort_keys=True) + "\n"
        )
        (out_dir / "positions_revised.json").write_text(
            json.dumps([to_dict(p) for p in revised_positions], indent=2, sort_keys=True) + "\n"
        )
        (out_dir / "belief_updates.json").write_text(
            json.dumps([to_dict(b) for b in belief_updates], indent=2, sort_keys=True) + "\n"
        )
        (out_dir / "recommendation.json").write_text(
            json.dumps(to_dict(chair_result.recommendation), indent=2, sort_keys=True) + "\n"
        )
        (out_dir / "narrative.txt").write_text(chair_result.narrative + "\n")

        print(f"kriterion: Treatment D complete -> {out_dir}")
        print(f"kriterion: {len(initial_positions)}/5 initial, {len(revised_positions)}/5 revised")
        if abstained_phase3:
            print(f"kriterion: phase 3 abstained_error: {abstained_phase3}", file=sys.stderr)
        if abstained_phase7:
            print(f"kriterion: phase 7 abstained_error: {abstained_phase7}", file=sys.stderr)
        print(f"kriterion: final action = {chair_result.recommendation.action.value}")
        return 0

    # Condition C: the full committee, phases 0-8.
    phase3_outcomes = [
        run_phase3_independent_assessment(
            executor, charter, case, evidence_by_id, economics,
            seed=args.seed, created_at=created_at, run_id=run_id,
        )
        for charter in charters.values()
    ]
    initial_positions = [o.position for o in phase3_outcomes if o.status == "ok" and o.position is not None]
    abstained_phase3 = [o.member.value for o in phase3_outcomes if o.status == "abstained_error"]
    if len(initial_positions) < 2:
        print(
            f"kriterion: run failed: only {len(initial_positions)}/5 members produced a valid "
            f"initial position (abstained: {abstained_phase3}) -- cannot run challenge/revision",
            file=sys.stderr,
        )
        return 1

    charters_by_seat = {c.seat: c for c in charters.values()}
    challenge_result = run_phase5_challenge(
        executor, case, items, economics, initial_positions, charters_by_seat,
        seed=args.seed, created_at=created_at, run_id=run_id,
    )
    all_challenges = [challenge_result.case_for, challenge_result.case_against] + challenge_result.premortems

    injection_path = case_dir / "injection.toml"
    injected = load_injection(injection_path, created_at=created_at) if injection_path.is_file() else []
    ledger_v2_items = items + injected
    new_evidence_ids = {item.id for item in injected}

    revision_outcomes = [
        run_phase7_revised_assessment(
            executor, position, charters_by_seat[position.member], case, ledger_v2_items,
            all_challenges, economics, new_evidence_ids=new_evidence_ids,
            seed=args.seed, created_at=created_at, run_id=run_id,
        )
        for position in initial_positions
    ]
    revised_positions = [o.revised_position for o in revision_outcomes if o.status == "ok" and o.revised_position is not None]
    belief_updates = [o.belief_update for o in revision_outcomes if o.status == "ok" and o.belief_update is not None]
    abstained_phase7 = [o.member.value for o in revision_outcomes if o.status == "abstained_error"]
    if not revised_positions:
        print("kriterion: run failed: every member abstained_error at phase 7", file=sys.stderr)
        return 1

    chair_result = synthesize(
        executor, case, revised_positions, challenge_result.case_against,
        seed=args.seed, created_at=created_at, run_id=run_id,
    )

    (out_dir / "positions_initial.json").write_text(
        json.dumps([to_dict(p) for p in initial_positions], indent=2, sort_keys=True) + "\n"
    )
    (out_dir / "challenges.json").write_text(
        json.dumps([to_dict(c) for c in all_challenges], indent=2, sort_keys=True) + "\n"
    )
    (out_dir / "positions_revised.json").write_text(
        json.dumps([to_dict(p) for p in revised_positions], indent=2, sort_keys=True) + "\n"
    )
    (out_dir / "belief_updates.json").write_text(
        json.dumps([to_dict(b) for b in belief_updates], indent=2, sort_keys=True) + "\n"
    )
    (out_dir / "recommendation.json").write_text(
        json.dumps(to_dict(chair_result.recommendation), indent=2, sort_keys=True) + "\n"
    )
    (out_dir / "narrative.txt").write_text(chair_result.narrative + "\n")

    print(f"kriterion: Treatment C complete -> {out_dir}")
    print(f"kriterion: {len(initial_positions)}/5 initial, {len(revised_positions)}/5 revised")
    if abstained_phase3:
        print(f"kriterion: phase 3 abstained_error: {abstained_phase3}", file=sys.stderr)
    if abstained_phase7:
        print(f"kriterion: phase 7 abstained_error: {abstained_phase7}", file=sys.stderr)
    print(f"kriterion: final action = {chair_result.recommendation.action.value}")
    return 0


def _cmd_ledger_freeze(args: argparse.Namespace) -> int:
    case_dir = Path(args.case_dir)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        case, items, _assumptions = load_case_pack(case_dir, created_at=created_at)
    except CasePackError as exc:
        print(f"kriterion: ledger freeze failed: {exc}", file=sys.stderr)
        return 1

    run_id = args.run_id or f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    ledger = freeze(items, ledger_id=f"{case.id}-ledger", created_at=created_at)

    out_path = Path(args.runs_dir) / run_id / "ledger.frozen.json"
    write_frozen_ledger(ledger, out_path)

    print(f"kriterion: froze {len(items)} evidence items -> {out_path}")
    print(f"kriterion: ledger fingerprint {ledger.fingerprint}")
    return 0


def _cmd_econ(args: argparse.Namespace) -> int:
    case_dir = Path(args.case_dir)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        case, _items, assumptions = load_case_pack(case_dir, created_at=created_at)
    except CasePackError as exc:
        print(f"kriterion: econ failed: {exc}", file=sys.stderr)
        return 1

    econ_fn = CASE_ECONOMICS_FUNCTIONS.get(case.id)
    if econ_fn is None:
        print(f"kriterion: econ failed: no cash-flow model wired for case '{case.id}' yet", file=sys.stderr)
        return 1

    assumptions_by_id = {a.id: a for a in assumptions}
    result = econ_fn(case.id, case.ask.amount_gbp, assumptions_by_id)

    run_id = args.run_id or f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    out_path = Path(args.runs_dir) / run_id / "economics.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(to_dict(result), indent=2, sort_keys=True) + "\n")

    print(f"kriterion: wrote economics -> {out_path}")
    print(
        f"kriterion: NPV low/mid/high = "
        f"£{result.npv_low_gbp:,.0f} / £{result.npv_mid_gbp:,.0f} / £{result.npv_high_gbp:,.0f}"
    )
    return 0


def _cmd_decide(args: argparse.Namespace) -> int:
    """ADR-006: HumanDecision is always a separate file from
    SyntheticRecommendation — this command never touches recommendation.json."""
    run_dir = Path(args.runs_dir) / args.run_id
    if not run_dir.is_dir():
        print(f"kriterion: decide failed: no run directory at {run_dir}", file=sys.stderr)
        return 1

    try:
        action = DecisionAction(args.action)
    except ValueError:
        print(
            f"kriterion: decide failed: invalid action '{args.action}' "
            f"(must be one of {[a.value for a in DecisionAction]})",
            file=sys.stderr,
        )
        return 1

    decided_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    decision = HumanDecision(
        id=f"{args.run_id}-human-decision",
        created_at=decided_at,
        action=action,
        disposition=args.disposition,
        overrides=args.override or [],
        rationale=args.rationale,
        owner=args.owner,
        decided_at=decided_at,
    )
    out_path = write_human_decision(decision, run_dir)
    print(f"kriterion: wrote human decision -> {out_path}")

    violations = validate_run(run_dir)
    if violations:
        for v in violations:
            print(f"kriterion: WARNING: {v}", file=sys.stderr)
        print(
            "kriterion: this is a funding action — run `kriterion contract` before this "
            "decision is considered complete",
            file=sys.stderr,
        )
    return 0


def _cmd_contract(args: argparse.Namespace) -> int:
    run_dir = Path(args.runs_dir) / args.run_id
    if not run_dir.is_dir():
        print(f"kriterion: contract failed: no run directory at {run_dir}", file=sys.stderr)
        return 1

    decision_path = run_dir / "human_decision.json"
    if not decision_path.is_file():
        print(
            f"kriterion: contract failed: no human_decision.json in {run_dir} — run "
            "`kriterion decide` first",
            file=sys.stderr,
        )
        return 1

    decision = load_human_decision(run_dir)
    if decision.action not in FUNDING_ACTIONS:
        print(
            f"kriterion: contract failed: HumanDecision action '{decision.action.value}' is not "
            f"a funding action ({[a.value for a in FUNDING_ACTIONS]}) — no contract needed",
            file=sys.stderr,
        )
        return 1

    try:
        measures = [parse_measure_arg(m) for m in (args.measure or [])]
    except DecisionError as exc:
        print(f"kriterion: contract failed: {exc}", file=sys.stderr)
        return 1
    if not measures:
        print("kriterion: contract failed: at least one --measure is required", file=sys.stderr)
        return 1

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    contract = OutcomeContract(
        id=f"{args.run_id}-outcome-contract",
        created_at=created_at,
        baseline_date=args.baseline_date,
        measures=measures,
        owner=args.owner,
        review_date=args.review_date,
        next_decision=args.next_decision,
        kill_criteria=args.kill_criteria or [],
    )
    out_path = write_outcome_contract(contract, run_dir)
    print(f"kriterion: wrote outcome contract -> {out_path}")
    return 0


def _cmd_validate_run(args: argparse.Namespace) -> int:
    """P0-09: a funding action without an OutcomeContract exits non-zero."""
    run_dir = Path(args.runs_dir) / args.run_id
    if not run_dir.is_dir():
        print(f"kriterion: validate-run failed: no run directory at {run_dir}", file=sys.stderr)
        return 1

    violations = validate_run(run_dir)
    if violations:
        for v in violations:
            print(f"kriterion: VIOLATION: {v}", file=sys.stderr)
        return 1

    print(f"kriterion: {run_dir} is clean (no governance violations)")
    return 0


def _cmd_evals(args: argparse.Namespace) -> int:
    from kriterion.evals import write_run_export

    run_dir = Path(args.runs_dir) / args.run_id
    if not run_dir.is_dir():
        print(f"kriterion: evals failed: no run directory at {run_dir}", file=sys.stderr)
        return 1

    out_path = write_run_export(run_dir, args.case_id)
    data = json.loads(out_path.read_text())
    for fixture in data["fixtures"]:
        status = "PASS" if fixture["passed"] else "FAIL"
        print(f"kriterion: [{status}] {fixture['fixture_id']}: {fixture['detail']}")
    print(f"kriterion: wrote {out_path}")
    print(f"kriterion: all_green = {data['all_green']}")
    return 0 if data["all_green"] else 1


def _cmd_compare(args: argparse.Namespace) -> int:
    from dataclasses import asdict

    from kriterion.compare import compare_conditions

    runs_dir = Path(args.runs_dir)
    run_dirs_by_condition: dict[str, list[Path]] = {}
    for entry in args.condition_runs or []:
        if "=" not in entry:
            print(f"kriterion: compare failed: --condition-runs must be COND=run1,run2, got {entry!r}", file=sys.stderr)
            return 1
        condition, ids_raw = entry.split("=", 1)
        run_dirs_by_condition[condition] = [runs_dir / rid for rid in ids_raw.split(",") if rid]

    missing = [str(d) for dirs in run_dirs_by_condition.values() for d in dirs if not d.is_dir()]
    if missing:
        print(f"kriterion: compare failed: run directories not found: {missing}", file=sys.stderr)
        return 1

    perturbation_pairs: dict[str, list[tuple[Path, Path]]] = {}
    for entry in args.perturbation_pairs or []:
        if "=" not in entry:
            print(f"kriterion: compare failed: --perturbation-pairs must be COND=base1:pert1,base2:pert2, got {entry!r}", file=sys.stderr)
            return 1
        condition, pairs_raw = entry.split("=", 1)
        pairs: list[tuple[Path, Path]] = []
        for pair in pairs_raw.split(","):
            if not pair:
                continue
            if ":" not in pair:
                print(f"kriterion: compare failed: perturbation pair must be baseline:perturbed, got {pair!r}", file=sys.stderr)
                return 1
            baseline_id, perturbed_id = pair.split(":", 1)
            pairs.append((runs_dir / baseline_id, runs_dir / perturbed_id))
        perturbation_pairs[condition] = pairs

    missing_pairs = [str(d) for pairs in perturbation_pairs.values() for pair in pairs for d in pair if not d.is_dir()]
    if missing_pairs:
        print(f"kriterion: compare failed: perturbation run directories not found: {missing_pairs}", file=sys.stderr)
        return 1

    result = compare_conditions(run_dirs_by_condition, perturbation_pairs=perturbation_pairs or None)

    out_dir = Path(args.out_dir) if args.out_dir else runs_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "comparison.json"
    json_path.write_text(
        json.dumps(
            {
                "conditions": {c: asdict(m) for c, m in result.conditions.items()},
                "honest_negative_fired": result.honest_negative_fired,
                "honest_negative_detail": result.honest_negative_detail,
                "perturbation_drift_rate": result.perturbation_drift_rate,
            },
            indent=2, sort_keys=True,
        )
        + "\n"
    )

    md_lines = ["# Kriterion Comparison\n"]
    for cond, m in sorted(result.conditions.items()):
        md_lines.append(f"## Condition {cond} ({m.run_count} run(s))\n")
        md_lines.append(f"- Unsupported-claim rate: {m.unsupported_claim_rate:.3f}")
        md_lines.append(f"- Category-inflation count: {m.category_inflation_count}")
        md_lines.append(f"- Numeric-alteration count: {m.numeric_alteration_count}")
        md_lines.append(f"- Belief-update rationality: {m.belief_update_rationality}")
        md_lines.append(f"- Dissent non-empty rate: {m.dissent_nonempty_rate}")
        md_lines.append(f"- P0 pass rate: {m.p0_pass_rate:.3f}\n")
    if result.perturbation_drift_rate:
        md_lines.append("## Perturbation-robustness drift rate (P1 batch)\n")
        for cond, rate in sorted(result.perturbation_drift_rate.items()):
            md_lines.append(f"- Condition {cond}: {rate:.2f}")
        md_lines.append("")
    md_lines.append(f"## Pre-registered honest-negative criterion (docs/experiment-plan.md)\n")
    md_lines.append(f"**Fired:** {result.honest_negative_fired}\n\n{result.honest_negative_detail}\n")
    md_path = out_dir / "comparison.md"
    md_path.write_text("\n".join(md_lines) + "\n")

    print(f"kriterion: wrote {json_path} and {md_path}")
    print(f"kriterion: honest_negative_fired = {result.honest_negative_fired}")
    print(f"kriterion: {result.honest_negative_detail}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    from kriterion.report.html import render_report

    run_dir = Path(args.runs_dir) / args.run_id
    if not run_dir.is_dir():
        print(f"kriterion: report failed: run directory not found: {run_dir}", file=sys.stderr)
        return 1

    case_dir = Path(args.case_dir)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        case, _items, _assumptions = load_case_pack(case_dir, created_at=created_at)
    except CasePackError as exc:
        print(f"kriterion: report failed: {exc}", file=sys.stderr)
        return 1

    html = render_report(case, run_dir)
    out_path = Path(args.out) if args.out else run_dir / "report.html"
    out_path.write_text(html)

    print(f"kriterion: wrote {out_path}")
    return 0


def _cmd_perturbation_diff(args: argparse.Namespace) -> int:
    from kriterion.perturbation_diff import diff_paired_runs

    runs_dir = Path(args.runs_dir)
    baseline_dir = runs_dir / args.baseline_run_id
    perturbed_dir = runs_dir / args.perturbed_run_id
    for d in (baseline_dir, perturbed_dir):
        if not d.is_dir():
            print(f"kriterion: perturbation-diff failed: run directory not found: {d}", file=sys.stderr)
            return 1

    result = diff_paired_runs(baseline_dir, perturbed_dir)

    print(f"kriterion: baseline ({result.baseline_run}): {result.baseline_action} ({result.baseline_confidence})")
    print(f"kriterion: perturbed ({result.perturbed_run}): {result.perturbed_action} ({result.perturbed_confidence})")
    if result.action_drifted is None:
        print("kriterion: action_drifted = unknown (one or both runs have no recommendation.json)", file=sys.stderr)
        return 1
    print(f"kriterion: action_drifted = {result.action_drifted}")
    return 0


def _cmd_assurance_import(args: argparse.Namespace) -> int:
    from kriterion.assurance.adapter import (
        AssuranceImportError,
        adapt_envelope,
        load_assurance_documents,
    )
    from kriterion.domain.evidence import Attestation

    envelope_dir = Path(args.envelope_dir)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        envelope, decision = load_assurance_documents(envelope_dir)
        summary, items = adapt_envelope(
            envelope,
            decision,
            attestation=Attestation(args.attestation),
            created_at=created_at,
        )
    except AssuranceImportError as exc:
        print(f"kriterion: assurance import failed: {exc}", file=sys.stderr)
        return 1

    payload = {
        "schema_version": "kriterion/v0.1",
        "summary": to_dict(summary),
        "items": [to_dict(item) for item in items],
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        print(f"kriterion: wrote {out_path}")
    else:
        print(text, end="")

    print(
        f"kriterion: capability {summary.capability_name} v{summary.capability_version}: "
        f"decision {summary.decision_state}"
        + (" (STALE)" if summary.stale else "")
        + f", {len(items)} evidence item(s) derived "
        f"({summary.critical_failure_count} critical failure(s), "
        f"{summary.uncovered_count} coverage gap(s))",
        file=sys.stderr,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kriterion",
        description="Evidence-first executive decision instrumentation.",
    )
    parser.add_argument("--version", action="version", version=f"kriterion {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    ledger_parser = subparsers.add_parser("ledger", help="Evidence ledger operations")
    ledger_subparsers = ledger_parser.add_subparsers(dest="ledger_command", required=True)

    freeze_parser = ledger_subparsers.add_parser(
        "freeze", help="Freeze a case pack's evidence into a fingerprinted ledger version"
    )
    freeze_parser.add_argument("case_dir", help="Path to a case pack directory (contains case.toml)")
    freeze_parser.add_argument("--run-id", default=None, help="Run directory name under runs/")
    freeze_parser.add_argument("--runs-dir", default="runs", help="Root directory for run artifacts")
    freeze_parser.set_defaults(func=_cmd_ledger_freeze)

    econ_parser = subparsers.add_parser("econ", help="Compute deterministic economics for a case")
    econ_parser.add_argument("case_dir", help="Path to a case pack directory (contains case.toml)")
    econ_parser.add_argument("--run-id", default=None, help="Run directory name under runs/")
    econ_parser.add_argument("--runs-dir", default="runs", help="Root directory for run artifacts")
    econ_parser.set_defaults(func=_cmd_econ)

    doctor_parser = subparsers.add_parser(
        "doctor", help="Check the local executor (Ollama) is reachable and ready"
    )
    doctor_parser.set_defaults(func=_cmd_doctor)

    run_parser = subparsers.add_parser("run", help="Run a deliberation condition against a case")
    run_parser.add_argument("case_dir", help="Path to a case pack directory (contains case.toml)")
    run_parser.add_argument("--condition", choices=["A", "B", "C", "D"], required=True)
    run_parser.add_argument("--seed", type=int, default=0)
    run_parser.add_argument("--run-id", default=None, help="Run directory name under runs/")
    run_parser.add_argument("--runs-dir", default="runs", help="Root directory for run artifacts")
    run_parser.add_argument(
        "--perturbation", default=None,
        choices=["framing_flip", "sponsor_endorsement", "anchoring", "evidence_reorder"],
        help="Apply a P1 invariance perturbation (docs/v0-plan.md Section 7) before running",
    )
    run_parser.set_defaults(func=_cmd_run)

    decide_parser = subparsers.add_parser("decide", help="Record the human decision for a run")
    decide_parser.add_argument("run_id")
    decide_parser.add_argument("--action", required=True, help="One of the ten decision-vocabulary values")
    decide_parser.add_argument("--disposition", required=True, choices=["accept", "modify", "reject"])
    decide_parser.add_argument("--rationale", default="")
    decide_parser.add_argument("--owner", default="")
    decide_parser.add_argument("--override", action="append", default=[])
    decide_parser.add_argument("--runs-dir", default="runs")
    decide_parser.set_defaults(func=_cmd_decide)

    contract_parser = subparsers.add_parser("contract", help="Write an outcome contract for a funded run")
    contract_parser.add_argument("run_id")
    contract_parser.add_argument("--baseline-date", required=True)
    contract_parser.add_argument("--review-date", required=True)
    contract_parser.add_argument("--next-decision", required=True)
    contract_parser.add_argument(
        "--measure", action="append", help="name:baseline:target:source_ref (repeatable)"
    )
    contract_parser.add_argument("--kill-criteria", action="append", default=[])
    contract_parser.add_argument("--owner", default="")
    contract_parser.add_argument("--runs-dir", default="runs")
    contract_parser.set_defaults(func=_cmd_contract)

    validate_parser = subparsers.add_parser(
        "validate-run", help="Check a run for governance violations (P0-09)"
    )
    validate_parser.add_argument("run_id")
    validate_parser.add_argument("--runs-dir", default="runs")
    validate_parser.set_defaults(func=_cmd_validate_run)

    evals_parser = subparsers.add_parser("evals", help="Run the P0 eval harness against a completed run")
    evals_parser.add_argument("run_id")
    evals_parser.add_argument("--case-id", required=True, help="Case id, for golden-fixture lookup")
    evals_parser.add_argument("--runs-dir", default="runs")
    evals_parser.set_defaults(func=_cmd_evals)

    compare_parser = subparsers.add_parser(
        "compare", help="Aggregate multiple runs into per-condition metrics (docs/experiment-plan.md)"
    )
    compare_parser.add_argument(
        "--condition-runs", action="append",
        help="COND=run1,run2,... (repeatable, e.g. --condition-runs A=run-a1,run-a2)",
    )
    compare_parser.add_argument("--runs-dir", default="runs")
    compare_parser.add_argument("--out-dir", default=None, help="Defaults to --runs-dir")
    compare_parser.add_argument(
        "--perturbation-pairs", action="append",
        help="COND=baseline1:perturbed1,baseline2:perturbed2,... (repeatable, e.g. A=caseA-condA-s0:caseA-condA-s0-anchoring)",
    )
    compare_parser.set_defaults(func=_cmd_compare)

    report_parser = subparsers.add_parser(
        "report", help="Render a run into a single static HTML file (docs/v0-plan.md Section 11)"
    )
    report_parser.add_argument("run_id", help="Run directory name under --runs-dir")
    report_parser.add_argument("case_dir", help="Path to the case pack directory this run used (contains case.toml)")
    report_parser.add_argument("--runs-dir", default="runs", help="Root directory for run artifacts")
    report_parser.add_argument("--out", default=None, help="Defaults to <run-dir>/report.html")
    report_parser.set_defaults(func=_cmd_report)

    assurance_parser = subparsers.add_parser(
        "assurance", help="Generic assurance-evidence document operations (ADR-007)"
    )
    assurance_subparsers = assurance_parser.add_subparsers(dest="assurance_command", required=True)
    assurance_import_parser = assurance_subparsers.add_parser(
        "import",
        help="Translate an assurance envelope.json (+ optional decision.json) into Kriterion evidence items",
    )
    assurance_import_parser.add_argument(
        "envelope_dir", help="Directory containing envelope.json and optionally decision.json"
    )
    assurance_import_parser.add_argument(
        "--attestation",
        choices=["AUTHORED", "SIMULATED_THIRD_PARTY", "REAL"],
        default="AUTHORED",
        help="Provenance of the documents (ADR-003). Defaults to AUTHORED — never claims REAL silently.",
    )
    assurance_import_parser.add_argument(
        "--out", default=None, help="Write the derived items JSON here instead of stdout"
    )
    assurance_import_parser.set_defaults(func=_cmd_assurance_import)

    pdiff_parser = subparsers.add_parser(
        "perturbation-diff", help="Compare a baseline and perturbed run's action (docs/v0-plan.md Section 6, P1)"
    )
    pdiff_parser.add_argument("baseline_run_id")
    pdiff_parser.add_argument("perturbed_run_id")
    pdiff_parser.add_argument("--runs-dir", default="runs", help="Root directory for run artifacts")
    pdiff_parser.set_defaults(func=_cmd_perturbation_diff)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        return args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
