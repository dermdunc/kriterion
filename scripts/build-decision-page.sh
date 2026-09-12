#!/usr/bin/env bash
# Rebuild the public decision experience (docs/index.html) from committed state.
#
# There is no hand-editing step. `kriterion decision-page` refuses to write a
# page whose statements do not re-derive from the run's artifacts (ADR-012),
# and tests/product/test_public_page_coherence.py asserts the committed page is
# byte-identical to what this script produces.
#
# Usage: bash scripts/build-decision-page.sh [RUN_ID]
set -euo pipefail

RUN_ID="${1:-caseA-condC-s5}"
CASE_DIR="cases/coding-agent-rollout"
ASSURANCE_DIR="${CASE_DIR}/assurance"

cd "$(dirname "$0")/.."

PY="python"
if [ -x ".venv/bin/python" ]; then PY=".venv/bin/python"; fi

# 1. Re-import the assurance document pair through the ADR-007 adapter. The
#    page renders this payload, never the producer's documents directly.
#    created_at is pinned to the date this fixture was first imported, so the
#    committed payload is reproducible rather than re-stamped on every build.
"$PY" -m kriterion.cli assurance import "$ASSURANCE_DIR" \
    --created-at 2026-09-11T00:00:00Z \
    --out "$ASSURANCE_DIR/imported.json"

# 2. Render the per-run decision record the page links to.
"$PY" -m kriterion.cli report "$RUN_ID" "$CASE_DIR"
cp "runs/$RUN_ID/report.html" docs/reports/decision-record.html

# 3. Render the public decision page, with the integrity check as a gate.
"$PY" -m kriterion.cli decision-page "$RUN_ID" "$CASE_DIR" \
    --assurance-import "$ASSURANCE_DIR/imported.json" \
    --out docs/index.html
