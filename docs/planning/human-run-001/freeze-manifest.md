# Kriterion Human Run 001 — Freeze Manifest

**Safe to read at T0.** This manifest deliberately states **no** part of the synthetic
recommendation — not the action, not the confidence band, not the amount, not the dissent. It
records identity, content hashes and reproduction commands only, so that it can be read before the
run without destroying the T1 checkpoint. Run-output observations live in `opus-pivot-report.md`,
which is *not* safe to read before T2.

Everything listed here was produced before T0 and must not be mutated during the experiment.
Material evidence arising during the run is recorded as post-T0 evidence, never folded back into
the case.

---

## Identity

| Field | Value |
|---|---|
| Run | Human Run 001 |
| Decision | £3m–£5m Internal Developer Platform investment over 18 months, or incremental toolchain improvement |
| Scenario | Northstar Software Group — **FICTIONAL** |
| Kriterion case id | `northstar-internal-developer-platform` |
| Case pack | `cases/northstar-internal-developer-platform/case.toml` (committed) |
| Case freeze | the `case.toml` sha256 below, plus this repository's commit |
| Canonical run id | `hr001-northstar-condC-s1` |
| Condition | C (full committee, phases 0–8) |
| Seed | 1 |
| Evidence ledger version | 1 |
| Evidence ledger fingerprint | `bad57982921a5a0a94dd5a86b4601fd243866819b89d6f910667bd0b2941221c` (65 items) — see the reproducibility note below before treating this as a content hash |
| Executor | `HektonLocalExecutor` (local Ollama, `qwen2.5:14b-instruct`) |
| Members responding | 5/5 initial, 5/5 revised |
| Narrative Integrity | **0 violations**; `kriterion decision-page` refuses to write a failing page, so the written page *is* the pass |
| Governance | `kriterion validate-run` reports clean, no violations |
| Generated page | `docs/human-run-001/decision-page.html`, 171,281 bytes on disk (the CLI reports 171,155 — that is the character count of the rendered string; the file is UTF-8 and contains multi-byte characters) |

## Evidence ledger composition

| Category | Count |
|---|---|
| `EXTERNAL_REFERENCE` | 20 |
| `MEASURED` | 13 |
| `UNKNOWN` | 12 |
| `ASSUMPTION` | 8 |
| `EXPERT_JUDGMENT` | 6 |
| `INFERENCE` | 5 |
| `FORECAST` | 1 |
| **Total** | **65** |

| Attestation | Count |
|---|---|
| `AUTHORED` (synthetic scenario input) | 45 |
| `REAL` (public, checkable source) | 20 |

Ids run `ev-401` to `ev-465`. The id space deliberately does not overlap Case A's `ev-0xx` or
Case C's `ev-1xx`, so no evidence reference recorded during this run can be confused with one from
another case.

All 13 `MEASURED` items are attested `AUTHORED`. **The case contains no real measurement of any
real organisation.**

## Economics

| Field | Value |
|---|---|
| Model | `kriterion.economics.case_flows.compute_staged_platform_economics` |
| Ask | £4,000,000 / 18 months (synthetic; midpoint of the £3m–£5m envelope) |
| NPV low / mid / high | −£6,624,995 / −£4,061,178 / **+£11,748,388** |
| Payback | none on base-case flows within the two-period horizon |
| Peak funding | £4,724,500 |
| Avoided-loss band | not applicable — benefits are priced inside the NPV, so there is no separate band |
| Tornado entries | 9, ranked; `as-benefit-attribution-factor` first |

The NPV sign flips inside the case's own declared assumption ranges. That is a property of the
case, not a defect of the model.

---

## Reproduction

```bash
cd <repository root>
K=.venv/bin/python
C=cases/northstar-internal-developer-platform

$K -m kriterion.cli run   $C --condition C --seed 1 \
                          --run-id hr001-northstar-condC-s1 --runs-dir runs
$K -m kriterion.cli econ  $C --run-id hr001-northstar-condC-s1 --runs-dir runs
$K -m kriterion.cli ledger freeze $C --run-id hr001-northstar-condC-s1 --runs-dir runs
$K -m kriterion.cli decision-page hr001-northstar-condC-s1 $C --runs-dir runs \
                          --out docs/human-run-001/decision-page.html
```

`kriterion run` must be invoked with the repository root as the working directory:
`load_all_charters` is called with the literal relative path `charters`, with no flag to override
it.

### What reproduces, and what does not — measured, not assumed

**`kriterion econ`, `ledger freeze` and `decision-page` are deterministic in value but not in
bytes.** This was tested by running each twice against unchanged inputs and diffing the output.

Every decision-relevant value is identical across runs: the NPV triple, peak funding, payback, all
nine tornado entries in the same order, all 65 ledger items with the same categories, attestations
and ordering, and the whole generated page once timestamps and hashes are masked.

What differs is `created_at`, which each command stamps with the wall-clock time of the write.

**Consequence, and it is a product finding rather than a caveat:** because the ledger fingerprint
is computed as `fingerprint(ledger.items)` and each item carries its own freshly stamped
`created_at`, **the fingerprint changes on every freeze even when no evidence has changed.** It is
therefore a freeze identifier, not a content fingerprint, and it cannot be used to detect whether a
ledger's evidence has been altered between two freezes — which is the job a fingerprint on a frozen
evidence ledger would be expected to do. Recorded in `opus-pivot-report.md`; not fixed here,
because changing the identity semantics of a frozen ledger is not a change to make while
pre-registering an experiment.

So: **to verify this case, compare values, not bytes.** The hashes below pin the exact artifacts the
participant responded to. They are a freeze. Re-running the deterministic commands will reproduce
every number and every claim, and will not reproduce these hashes.

**`kriterion run` is not deterministic at all.** It calls a local language model, so re-running it
will not reproduce `positions_*.json`, `challenges.json`, `belief_updates.json`,
`evidence_requests.json`, `narrative.txt` or `recommendation.json` — in value or in bytes.

To verify the page against the committed run without rewriting it:

```bash
$K -m kriterion.cli decision-page hr001-northstar-condC-s1 $C --runs-dir runs \
                    --out docs/human-run-001/decision-page.html --check-only
```

## Integrity check

```bash
shasum -a 256 cases/northstar-internal-developer-platform/case.toml \
              docs/human-run-001/decision-page.html
find runs/hr001-northstar-condC-s1 -type f | sort \
  | while read f; do shasum -a 256 "$f"; done
```

## Content hashes (sha256)

```text
69dbd1f692dcfdbc78c6c2b48686b48174c67c6e90bdde36c165f3fbb64e1f26  cases/northstar-internal-developer-platform/case.toml
570b36fc44ea3b88342ce4a4886a2c583c6634e69d57242022abed73413af3c5  docs/human-run-001/decision-page.html
7a7052a7ad36478900a6591150d3cd7600fd766f268c4ca829b3e1b0e2f74e54  runs/hr001-northstar-condC-s1/belief_updates.json
23fb42dd2cce3e25ad418405f1cc714599d2279e46215d055807fdc16506ee8f  runs/hr001-northstar-condC-s1/challenges.json
a23583c00c4ce2a674ec23d99b8506557a47bb31b1546ab7c26da39b6b9e8f57  runs/hr001-northstar-condC-s1/economics.json
f94adb95b2341553887f974e19787d47d50c8bead62bb92ed9e688987f92ee48  runs/hr001-northstar-condC-s1/evidence_requests.json
88f3d097a564141b9cde18c8329aae82794bbdc6bc3d2c9f4991731a10315294  runs/hr001-northstar-condC-s1/ledger.frozen.json
193478b601a3919b98ffff7181f46f59a20c2e660a41066b55d72f1c5f96454d  runs/hr001-northstar-condC-s1/narrative.txt
d4e4934027b8423a9b534ed21969165a19ee1a57479bf4fa5852576652fba61a  runs/hr001-northstar-condC-s1/positions_initial.json
328dd07556c5097094846dab8c734179f268b219c33921cdfdd42f2f7a0576b6  runs/hr001-northstar-condC-s1/positions_revised.json
685307bea2c44896e8c6bf93e4854a445f7db95058945c1969fa6b787c66f56d  runs/hr001-northstar-condC-s1/recommendation.json
```

`case.toml`, `challenges.json`, `belief_updates.json`, `evidence_requests.json`, `narrative.txt`,
`positions_*.json` and `recommendation.json` are stable — nothing rewrites them.
`ledger.frozen.json`, `economics.json` and the page carry a write-time `created_at` and will hash
differently if regenerated, per the note above.

`recommendation.json` is hashed here but **must not be opened before T1**. Neither must
`narrative.txt` or either `positions_*.json` — they state or imply the recommendation.

## Decision records

No `HumanDecision` and no `OutcomeContract` exist against this run. The run directory contains
neither `human_decision.json` nor `outcome_contract.json`, and will not until the experiment is
performed. `kriterion decide` writes `human_decision.json` as a separate file and never touches
`recommendation.json` (ADR-006).
