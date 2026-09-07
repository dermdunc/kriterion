#!/usr/bin/env bash
# Executes docs/experiment-plan.md's pre-registered base grid: 2 cases x 3
# conditions x 5 seeds = 30 runs, live against Ollama via hekton-local-llm.
# Per run: kriterion run -> ledger freeze -> econ -> evals, so every run
# directory ends up with everything kriterion compare and kriterion report
# need. Continues past a single run's failure (recorded in the summary)
# rather than aborting the whole grid -- a real live-model batch this size
# is expected to hit an occasional abstained_error, per docs/decisions.md's
# own account of prior single-run live behaviour.
#
# NOT included here: the 16 perturbation-pair runs (framing flip, sponsor
# endorsement, evidence reorder, anchoring) docs/experiment-plan.md also
# names -- that P1 fixture-perturbation machinery does not exist yet
# (docs/next-actions.md "Later" section), so those runs are not executable
# and are not silently skipped-and-forgotten; kriterion compare's own
# honest-negative check already reports perturbation-robustness as
# not-yet-computed for exactly this reason.
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON="${PYTHON:-.venv/bin/python}"
RUNS_DIR="${RUNS_DIR:-runs}"
SUMMARY="$RUNS_DIR/grid-summary.log"

declare -A CASE_DIRS=(
  [caseA]="cases/coding-agent-rollout"
  [caseC]="cases/invisible-ai-control-plane"
)
declare -A CASE_IDS=(
  [caseA]="coding-agent-rollout"
  [caseC]="invisible-ai-control-plane"
)
CONDITIONS=(A B C)
SEEDS=(0 1 2 3 4)

mkdir -p "$RUNS_DIR"
: > "$SUMMARY"

total=0
failed=0

for case_key in caseA caseC; do
  case_dir="${CASE_DIRS[$case_key]}"
  case_id="${CASE_IDS[$case_key]}"
  for condition in "${CONDITIONS[@]}"; do
    for seed in "${SEEDS[@]}"; do
      run_id="${case_key}-cond${condition}-s${seed}"
      total=$((total + 1))
      echo "=== [$total/30] $run_id ==="

      run_ok=1
      "$PYTHON" -m kriterion.cli run "$case_dir" --condition "$condition" --seed "$seed" \
        --run-id "$run_id" --runs-dir "$RUNS_DIR" || run_ok=0

      "$PYTHON" -m kriterion.cli ledger freeze "$case_dir" --run-id "$run_id" --runs-dir "$RUNS_DIR" || run_ok=0
      "$PYTHON" -m kriterion.cli econ "$case_dir" --run-id "$run_id" --runs-dir "$RUNS_DIR" || run_ok=0
      "$PYTHON" -m kriterion.cli evals "$run_id" --case-id "$case_id" --runs-dir "$RUNS_DIR" || run_ok=0

      if [ "$run_ok" -eq 1 ]; then
        echo "$run_id OK" >> "$SUMMARY"
      else
        echo "$run_id FAILED (see kriterion output above)" >> "$SUMMARY"
        failed=$((failed + 1))
      fi
    done
  done
done

echo "=== Grid complete: $((total - failed))/$total runs OK, $failed failed ==="
echo "=== Grid complete: $((total - failed))/$total runs OK, $failed failed ===" >> "$SUMMARY"

# kriterion compare per case, across all 5 seeds x 3 conditions.
for case_key in caseA caseC; do
  a_ids=$(printf "${case_key}-condA-s%d," "${SEEDS[@]}"); a_ids="${a_ids%,}"
  b_ids=$(printf "${case_key}-condB-s%d," "${SEEDS[@]}"); b_ids="${b_ids%,}"
  c_ids=$(printf "${case_key}-condC-s%d," "${SEEDS[@]}"); c_ids="${c_ids%,}"
  "$PYTHON" -m kriterion.cli compare \
    --condition-runs "A=$a_ids" --condition-runs "B=$b_ids" --condition-runs "C=$c_ids" \
    --runs-dir "$RUNS_DIR" --out-dir "$RUNS_DIR/compare-$case_key"
done
