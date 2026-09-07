#!/usr/bin/env bash
# Runs the 8 P1 perturbed-run half of docs/v0-plan.md's 16-run perturbation
# grid: 4 perturbations x 2 conditions (A, C), seed 0, Case A. The baseline
# half already exists and is committed (runs/caseA-condA-s0,
# runs/caseA-condC-s0) -- same seed, same case, unperturbed -- so this
# script only needs to produce the perturbed halves and then runs
# kriterion perturbation-diff against the existing baselines.
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON="${PYTHON:-.venv/bin/python}"
RUNS_DIR="${RUNS_DIR:-runs}"
CASE_DIR="cases/coding-agent-rollout"
CASE_ID="coding-agent-rollout"
SUMMARY="$RUNS_DIR/perturbation-summary.log"

PERTURBATIONS=(framing_flip sponsor_endorsement anchoring evidence_reorder)
CONDITIONS=(A C)

: > "$SUMMARY"

for perturbation in "${PERTURBATIONS[@]}"; do
  for condition in "${CONDITIONS[@]}"; do
    run_id="caseA-cond${condition}-s0-${perturbation}"
    baseline_id="caseA-cond${condition}-s0"
    echo "=== $run_id ==="
    run_ok=1
    "$PYTHON" -m kriterion.cli run "$CASE_DIR" --condition "$condition" --seed 0 \
      --run-id "$run_id" --runs-dir "$RUNS_DIR" --perturbation "$perturbation" || run_ok=0
    "$PYTHON" -m kriterion.cli ledger freeze "$CASE_DIR" --run-id "$run_id" --runs-dir "$RUNS_DIR" || run_ok=0
    "$PYTHON" -m kriterion.cli econ "$CASE_DIR" --run-id "$run_id" --runs-dir "$RUNS_DIR" || run_ok=0
    "$PYTHON" -m kriterion.cli evals "$run_id" --case-id "$CASE_ID" --runs-dir "$RUNS_DIR" || run_ok=0

    if [ "$run_ok" -eq 1 ]; then
      echo "$run_id OK" >> "$SUMMARY"
    else
      echo "$run_id FAILED (see kriterion output above)" >> "$SUMMARY"
    fi

    echo "--- perturbation-diff: $baseline_id vs $run_id ---" >> "$SUMMARY"
    "$PYTHON" -m kriterion.cli perturbation-diff "$baseline_id" "$run_id" --runs-dir "$RUNS_DIR" >> "$SUMMARY" 2>&1
  done
done

echo "=== Perturbation batch complete ===" >> "$SUMMARY"
echo "=== Perturbation batch complete ==="
