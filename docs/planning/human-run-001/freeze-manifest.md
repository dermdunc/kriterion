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
| Evidence ledger fingerprint | `254c00ee4d1edc6c9a0362560ff8d8d5df2f56bf6fec113f686124a82b87b623` (65 items) |
| Executor | `HektonLocalExecutor` (local Ollama, `qwen2.5:14b-instruct`) |
| Members responding | 5/5 initial, 5/5 revised |
| Narrative Integrity | **0 violations**; `kriterion decision-page` refuses to write a failing page, so the written page *is* the pass |
| Governance | `kriterion validate-run` reports clean, no violations |
| Generated page | `docs/human-run-001/decision-page.html`, 168,268 bytes on disk (the CLI reports 168,142 — that is the character count of the rendered string; the file is UTF-8 and contains multi-byte characters) |

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

**What reproduces exactly.** `kriterion econ`, `kriterion ledger freeze` and
`kriterion decision-page` are deterministic. Re-running them against the committed case pack and
the committed run artifacts reproduces `economics.json`, `ledger.frozen.json` and the page
byte-for-byte, and their hashes below are a reproducibility claim.

**What does not.** `kriterion run` calls a local language model, so re-running it will not
reproduce `positions_*.json`, `challenges.json`, `belief_updates.json`, `evidence_requests.json`,
`narrative.txt` or `recommendation.json` byte-for-byte. Their hashes below are a freeze, not a
reproducibility claim about the model.

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
b34472ca751986646a6347eb45d016b40f192c0d0636f9541c41a2df6244fc83  cases/northstar-internal-developer-platform/case.toml
9be5e9cd59d44c42891ecf4c1144da60336483786725099f39506775fe8d3b88  docs/human-run-001/decision-page.html
c92fc131973cb84baf7fc555f50182cf196ca99b7d647f3e3277d5dae6a0cf1f  runs/hr001-northstar-condC-s1/belief_updates.json
7084179f942b6cc5295787fe20fd7a7be8d566912bf0223d0a354c9f871d60ec  runs/hr001-northstar-condC-s1/challenges.json
790f5ae328b0dca15ed8195a42d60ebcff3935f511eebc3ec685c31d457ec838  runs/hr001-northstar-condC-s1/economics.json
2405e14d65010de5d4f682ce87eb819ee32a1cc6d0c3ada7216c73eb067ce063  runs/hr001-northstar-condC-s1/evidence_requests.json
7b491e42e99e3a7fd9fa68964102fcabf8ae131d198b9169f58f6b5772400985  runs/hr001-northstar-condC-s1/ledger.frozen.json
193478b601a3919b98ffff7181f46f59a20c2e660a41066b55d72f1c5f96454d  runs/hr001-northstar-condC-s1/narrative.txt
c7a5d2c9c85073da5d08cf7be0fb9881f531619074a894f301ce5fc9b4f76c92  runs/hr001-northstar-condC-s1/positions_initial.json
818a05a66631d8ce967725e77b1299fbd701552a43e0e730b2952bb0931f0f5e  runs/hr001-northstar-condC-s1/positions_revised.json
954942441646a31f240574abfbd046f30268cf442000a7a7927cfd7694a96b85  runs/hr001-northstar-condC-s1/recommendation.json
```

`recommendation.json` is hashed here but **must not be opened before T1**. Neither must
`narrative.txt` or either `positions_*.json` — they state or imply the recommendation.

## Decision records

No `HumanDecision` and no `OutcomeContract` exist against this run. The run directory contains
neither `human_decision.json` nor `outcome_contract.json`, and will not until the experiment is
performed. `kriterion decide` writes `human_decision.json` as a separate file and never touches
`recommendation.json` (ADR-006).
