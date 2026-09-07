#!/usr/bin/env bash
# Re-executes any run_id marked FAILED in runs/grid-summary.log (same
# run -> ledger freeze -> econ -> evals chain as run-comparison-grid.sh),
# then re-runs kriterion compare for every case touched by a retried run_id
# so comparison.json/comparison.md reflect the corrected data. Intended to
# run after run-comparison-grid.sh completes, with a fix already applied
# (e.g. the HektonLocalExecutor timeout increase) that the original failures
# needed.
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
SEEDS=(0 1 2 3 4)

if [ ! -f "$SUMMARY" ]; then
  echo "no $SUMMARY found -- nothing to retry"
  exit 0
fi

failed_ids=$(grep "FAILED" "$SUMMARY" | awk '{print $1}')
if [ -z "$failed_ids" ]; then
  echo "no failed runs recorded in $SUMMARY"
  exit 0
fi

retried_cases=()

for run_id in $failed_ids; do
  # run_id shape: <case_key>-cond<condition>-s<seed>
  case_key="${run_id%%-cond*}"
  rest="${run_id#*-cond}"
  condition="${rest:0:1}"
  seed="${rest#?-s}"
  case_dir="${CASE_DIRS[$case_key]}"
  case_id="${CASE_IDS[$case_key]}"

  echo "=== retrying $run_id (case=$case_dir condition=$condition seed=$seed) ==="
  retry_ok=1
  "$PYTHON" -m kriterion.cli run "$case_dir" --condition "$condition" --seed "$seed" \
    --run-id "$run_id" --runs-dir "$RUNS_DIR" || retry_ok=0
  "$PYTHON" -m kriterion.cli ledger freeze "$case_dir" --run-id "$run_id" --runs-dir "$RUNS_DIR" || retry_ok=0
  "$PYTHON" -m kriterion.cli econ "$case_dir" --run-id "$run_id" --runs-dir "$RUNS_DIR" || retry_ok=0
  "$PYTHON" -m kriterion.cli evals "$run_id" --case-id "$case_id" --runs-dir "$RUNS_DIR" || retry_ok=0

  if [ "$retry_ok" -eq 1 ]; then
    # Replace the FAILED line for this run_id with an OK line, don't just append.
    grep -v "^$run_id " "$SUMMARY" > "$SUMMARY.tmp" && mv "$SUMMARY.tmp" "$SUMMARY"
    echo "$run_id OK (retried)" >> "$SUMMARY"
    retried_cases+=("$case_key")
  else
    echo "$run_id FAILED AGAIN on retry (see kriterion output above)"
  fi
done

for case_key in $(printf "%s\n" "${retried_cases[@]}" | sort -u); do
  a_ids=$(printf "${case_key}-condA-s%d," "${SEEDS[@]}"); a_ids="${a_ids%,}"
  b_ids=$(printf "${case_key}-condB-s%d," "${SEEDS[@]}"); b_ids="${b_ids%,}"
  c_ids=$(printf "${case_key}-condC-s%d," "${SEEDS[@]}"); c_ids="${c_ids%,}"
  echo "=== re-running kriterion compare for $case_key ==="
  "$PYTHON" -m kriterion.cli compare \
    --condition-runs "A=$a_ids" --condition-runs "B=$b_ids" --condition-runs "C=$c_ids" \
    --runs-dir "$RUNS_DIR" --out-dir "$RUNS_DIR/compare-$case_key"
done

echo "=== Retry pass complete ==="
