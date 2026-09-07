# Kriterion

**Classification:** factory-output
**Lifecycle:** active
**Owner:** hekton
**Promotion target:** `none`

> An evidence-backed decision system for uncertain technology investments

## What this is

Kriterion is a decision-quality laboratory for enterprise technology investment. It ingests an
investment proposal, separates evidence from assumptions from unknowns, computes the economics
deterministically, elicits independent role-specific assessments from a five-seat AI committee
(CFO, CTO, CISO, Compliance, Business Executive), runs a structured adversarial challenge round,
records how positions changed and why, and produces a synthetic recommendation with preserved
dissent — which an accountable human then accepts, changes, or rejects as a separate recorded
decision, never merged with the recommendation itself.

It exists to test one falsifiable claim: **does running a case through multiple independent AI
contexts improve evidence discipline, challenge quality, and traceability, compared with running
the same rigorous protocol through a single strong AI context?** The protocol (evidence, economics,
schemas, challenge structure) is held constant across three conditions; only the number of
independent reasoning contexts varies:

- **Condition A** — one continuous context, all five charters collapsed (the strong baseline).
- **Condition B** — five independent one-shot assessments, deterministically aggregated, no
  revision.
- **Condition C** — the full committee: independent assessment → anonymised structured challenge
  → revision → deterministic synthesis with a preserved dissent.

Everything is fictional (`AUTHORED_FIXTURE` cases, no real company data), and every deterministic
number (NPV, payback, tornado sensitivity) is computed by pure Python before any model call —
models judge the case, they never compute it.

## Status: V0 complete, headline result in

All ten P0 governance evals pass, both authored case packs (a benefit-uplift staged-funding case
and a negative-NPV avoided-loss case) run cleanly under all three conditions, and the pre-registered
30-run comparison batch (2 cases × 3 conditions × 5 seeds, live against a local 14B model) has run.

**The pre-registered honest-negative criterion fired `True` on both cases**: Treatment C did not
beat either baseline by the required margin on the available sub-metrics. Per
[`docs/experiment-plan.md`](docs/experiment-plan.md), that is itself a valid, successful V0
outcome — *"structured multi-agent deliberation did not justify its complexity on these
cases"* — not a failure of the tool. See [`docs/decisions.md`](docs/decisions.md) for the full,
warts-and-all account, including two real bugs found and fixed mid-batch and one independent
second opinion sought before changing eval-scoring logic.

A curated demo run (Baseline A, Baseline B, and Treatment C, same case and seed, for direct
comparison) is committed under [`runs/caseA-condA-s0/`](runs/caseA-condA-s0/),
[`runs/caseA-condB-s0/`](runs/caseA-condB-s0/), and [`runs/caseA-condC-s0/`](runs/caseA-condC-s0/) —
open any `report.html` in a browser for the executive-facing view, or
[`runs/compare-caseA/comparison.md`](runs/compare-caseA/comparison.md) for the numbers.

## Quick start

Full setup (including the local-LLM dependency and Ollama) is in [`docs/setup.md`](docs/setup.md).
Once installed:

```bash
kriterion doctor                                    # confirm Ollama + model are reachable
kriterion run cases/coding-agent-rollout \
  --condition C --seed 0 --run-id my-run             # run a deliberation
kriterion econ cases/coding-agent-rollout --run-id my-run
kriterion ledger freeze cases/coding-agent-rollout --run-id my-run
kriterion evals my-run --case-id coding-agent-rollout   # P0 governance checks -> run-export.json
kriterion report my-run cases/coding-agent-rollout      # -> my-run/report.html
kriterion compare --condition-runs A=... --condition-runs B=... --condition-runs C=...  # aggregate a batch
```

`kriterion --help` and `kriterion <command> --help` document every flag. No runtime dependencies
beyond the standard library and the local `hekton_llm` executor — see `pyproject.toml`.

## Documentation

- [`docs/v0-plan.md`](docs/v0-plan.md) — the full V0 design: domain model, protocol phases, eval
  fixtures, experimental design, weekend build plan.
- [`docs/architecture.md`](docs/architecture.md) — module layout and data flow.
- [`docs/experiment-plan.md`](docs/experiment-plan.md) — the pre-registered comparison criteria,
  written before the batch ran.
- [`docs/decisions.md`](docs/decisions.md) — the ADR log: every material design decision and every
  real bug found while building and running this, with the reasoning behind each.
- [`docs/next-actions.md`](docs/next-actions.md) — build status task-by-task, and the open
  questions still waiting on a human.
- [`docs/risks.md`](docs/risks.md) — the risk register (model quality, judge contamination, scope,
  boundary erosion, and more), each with a stated mitigation.
- [`docs/setup.md`](docs/setup.md) / [`docs/reproducibility.md`](docs/reproducibility.md) —
  install and blank-machine rebuild steps.

## Documentation Contract

Agents working here must inspect `.hekton/project.yaml` before structural changes, record
meaningful design decisions in `docs/decisions.md`, and update `docs/next-actions.md` when the work
queue changes.

Vault mutation policy: see `vault_mutation_allowed` in `.hekton/project.yaml` (authoritative;
defaults to false at scaffold time). The repo-local `mind-palace/` folder is only a mirror draft;
do not write to the live vault unless `.hekton/project.yaml` says mutation is allowed and it is
explicitly authorised in-session.
