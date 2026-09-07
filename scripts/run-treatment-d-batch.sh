#!/usr/bin/env bash
# Runs Treatment D (heterogeneous per-seat models, see
# executors/hekton_local.py's TREATMENT_D_MODEL_BY_SEAT) across the same
# 5 pre-registered seeds as the base grid, Case A only. Same per-run chain
# as scripts/run-comparison-grid.sh: run -> ledger freeze -> econ -> evals.
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON="${PYTHON:-.venv/bin/python}"
RUNS_DIR="${RUNS_DIR:-runs}"
CASE_DIR="cases/coding-agent-rollout"
CASE_ID="coding-agent-rollout"
SUMMARY="$RUNS_DIR/treatment-d-summary.log"

: > "$SUMMARY"

for seed in 1 2 3 4; do
  run_id="caseA-condD-s${seed}"
  echo "=== $run_id ==="
  run_ok=1
  "$PYTHON" -m kriterion.cli run "$CASE_DIR" --condition D --seed "$seed" --run-id "$run_id" --runs-dir "$RUNS_DIR" || run_ok=0
  "$PYTHON" -m kriterion.cli ledger freeze "$CASE_DIR" --run-id "$run_id" --runs-dir "$RUNS_DIR" || run_ok=0
  "$PYTHON" -m kriterion.cli econ "$CASE_DIR" --run-id "$run_id" --runs-dir "$RUNS_DIR" || run_ok=0
  "$PYTHON" -m kriterion.cli evals "$run_id" --case-id "$CASE_ID" --runs-dir "$RUNS_DIR" || run_ok=0
  if [ "$run_ok" -eq 1 ]; then
    echo "$run_id OK" >> "$SUMMARY"
  else
    echo "$run_id FAILED (see kriterion output above)" >> "$SUMMARY"
  fi
done

echo "=== Treatment D batch complete ===" >> "$SUMMARY"
echo "=== Treatment D batch complete ==="
