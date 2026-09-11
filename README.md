# Kriterion

**Classification:** factory-output
**Lifecycle:** active
**Owner:** hekton
**Promotion target:** `none`

> An evidence-backed decision instrument for uncertain technology investments

## What this is

**Kriterion is an evidence-backed decision instrument for uncertain technology investments.** It
takes a consequential proposal and makes the things a decision actually rests on explicit:
structured evidence kept in seven distinct epistemic categories (measured, external reference,
expert judgment, forecast, assumption, inference, unknown), deterministic economics with named
load-bearing assumptions and sensitivities, structured adversarial challenge with recorded belief
updates, a per-seat `EvidenceRequest.would_change` record of what would change each position,
staged capital allocation instead of a binary approve/reject vocabulary, a synthetic
recommendation that is never the decision, a separately recorded human decision, and an outcome
contract for anything that commits resources. The machine supplies analysis, challenge and
evidence; the human remains accountable for the decision. The live decision journey is at
[kriterion.theagentictekton.com](https://kriterion.theagentictekton.com/).

> **Where that is, and isn't, true yet.** The public page is **generated** from one run's
> committed artifacts (`kriterion decision-page`, ADR-011), not hand-maintained narrative. Every
> material statement on it is stamped with the state path it came from, and the build refuses to
> publish a page whose text does not re-derive from the record (ADR-012); a test asserts the
> committed page is byte-identical to a fresh render. It renders `runs/caseA-condC-s5`, which
> stores real per-seat evidence requests, so "what would change my mind" is each seat's own
> recorded answer rather than reconstructed copy. What that does *not* prove: that a derived
> sentence is a *fair* summary of the numbers it is computed from. That stays a human judgment —
> and no human has yet recorded a decision on this case, which the page says plainly.

Kriterion can also, optionally, import machine-verifiable **assurance evidence** about an AI
capability through a generic document contract (`kriterion assurance import`, ADR-007): an
assurance envelope plus decision document, translated by an anti-corruption adapter into
Kriterion's own evidence domain. The adapter refuses rather than guesses: a critical *or gating*
failure can never import as PASS, an envelope that does not state its `criticalFailures` list at
all is refused rather than assumed clean, the decision must be identity-bound to the envelope it
claims to describe, a producer-declared PASS over stale evidence reports as STALE, a missing
verdict maps to UNKNOWN, and every malformed document shape is a controlled `AssuranceImportError`
rather than a traceback. With `--into-case`, imported items are frozen into a new ledger version
and flow through to the generated report. No assurance system is a runtime dependency; Kriterion
works identically without one.

The mechanics: it ingests an investment proposal, separates evidence from assumptions from
unknowns, computes the economics deterministically, elicits independent role-specific assessments
from a five-seat AI committee (CFO, CTO, CISO, Compliance, Business Executive), runs a structured
adversarial challenge round, records how positions changed and why, and produces a synthetic
recommendation with preserved dissent, which an accountable human then accepts, changes, or
rejects as a separate recorded decision, never merged with the recommendation itself.

## Kriterion Lab: the V0 experiment

The five-seat committee is **one challenge mechanism inside Kriterion, not the product itself**,
and that framing is earned, not asserted: Kriterion Lab is where Kriterion experiments on its own
decision mechanisms. Its V0 experiment tested one falsifiable claim: **does running a case through multiple independent AI
contexts improve evidence discipline, challenge quality, and traceability, compared with running
the same rigorous protocol through a single strong AI context?** The underlying case (evidence,
economics, decision vocabulary, schemas) and seeds are held constant across three conditions; what
varies is the number of independent reasoning contexts, and, for Condition B specifically, whether
any challenge-and-revision step runs at all:

- **Condition A**: one continuous context, all five charters collapsed (the strong baseline).
- **Condition B**: five independent one-shot assessments, deterministically aggregated, no
  revision.
- **Condition C**: the full committee: independent assessment → anonymised structured challenge
  → revision → deterministic synthesis with a preserved dissent.

Everything is fictional (`AUTHORED_FIXTURE` cases, no real company data), and every deterministic
number (NPV, payback, tornado sensitivity) is computed by pure Python before any model call;
models judge the case, they never compute it.

## Status: V0 experiment complete, headline result in; V1 instrument increment underway

The first V1 (decision instrument) increment adds the generic assurance-evidence adapter
(`src/kriterion/assurance/`, ADR-007) with an authored fixture envelope on the Case A pack, and
reworks the public site to lead with the decision journey (`docs/index.html`), with the V0
research preserved intact at `docs/lab.html`. The V0 experiment record below is unchanged.

All ten P0 governance evals pass across the pre-registered 30-run comparison batch (2 cases × 3
conditions × 5 seeds, live against a local 14B model; both authored case packs, a benefit-uplift
staged-funding case and a negative-NPV avoided-loss case, run cleanly under all three conditions).
Two of the later P1 perturbation-pair runs (outside that 30-run batch) did genuinely trip P0-05;
that is not silently excluded here, see [`docs/decisions.md`](docs/decisions.md).

**The comparison tool's bare-aggregate honest-negative check returned `True` on both cases**. On
Case A, the tool counted one of the three categories as a Treatment C win: perturbation robustness
against Baseline A only, because Baseline B was not perturbation-tested by design; on Case C, it
counted zero of the two available categories. Neither case reached the tool's threshold of two
category wins.

These are bare aggregate comparisons, not the full pre-registered margin (>2× seed-to-seed
standard deviation) and inference-cost check; both remain unimplemented, as disclosed in the
[Case A](docs/reports/comparison-case-a.md) and [Case C](docs/reports/comparison-case-c.md)
comparison reports. Adding the missing margin could only reduce Treatment C's category wins, but
the missing cost measurement means the full criterion's verdict remains unevaluated. On the
evidence measured so far, the provisional descriptive finding is: *"structured multi-agent
deliberation did not justify its complexity on these cases."* The experiment plan treats that
finding as a successful V0 outcome, not a failure of the tool, only if the missing >2×
inference-cost condition is also met. See [`docs/decisions.md`](docs/decisions.md) for the full,
warts-and-all account, including two real bugs found and fixed mid-batch and one independent
second opinion sought before changing eval-scoring logic.

A curated demo run (Baseline A, Baseline B, and Treatment C, same case and seed, for direct
comparison) is committed under [`runs/caseA-condA-s0/`](runs/caseA-condA-s0/),
[`runs/caseA-condB-s0/`](runs/caseA-condB-s0/), and [`runs/caseA-condC-s0/`](runs/caseA-condC-s0/);
open any `report.html` in a browser for the executive-facing view, or
[`docs/reports/comparison-case-a.md`](docs/reports/comparison-case-a.md) for the fully-computed
numbers (the demo trio's own [`runs/compare-caseA/comparison.md`](runs/compare-caseA/comparison.md)
predates the P1 perturbation batch and only reflects 2 of the 3 sub-metrics).

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
kriterion assurance import cases/coding-agent-rollout/assurance  # assurance envelope -> evidence items
kriterion assurance import cases/coding-agent-rollout/assurance \
  --into-case cases/coding-agent-rollout --run-id assurance-run   # ...and freeze them into ledger v2
kriterion compare --condition-runs A=... --condition-runs B=... --condition-runs C=...  # aggregate a batch
```

`kriterion --help` and `kriterion <command> --help` document every flag. No runtime dependencies
beyond the standard library and the local `hekton_llm` executor; see `pyproject.toml`.

## Documentation

- [`docs/v0-plan.md`](docs/v0-plan.md): the full V0 design: domain model, protocol phases, eval
  fixtures, experimental design, weekend build plan.
- [`docs/architecture.md`](docs/architecture.md): module layout and data flow.
- [`docs/experiment-plan.md`](docs/experiment-plan.md): the pre-registered comparison criteria,
  written before the batch ran.
- [`docs/decisions.md`](docs/decisions.md): the ADR log: every material design decision and every
  real bug found while building and running this, with the reasoning behind each.
- [`docs/next-actions.md`](docs/next-actions.md): build status task-by-task, and the open
  questions still waiting on a human.
- [`docs/risks.md`](docs/risks.md): the risk register (model quality, judge contamination, scope,
  boundary erosion, and more), each with a stated mitigation.
- [`docs/setup.md`](docs/setup.md) / [`docs/reproducibility.md`](docs/reproducibility.md):
  install and blank-machine rebuild steps.

## Documentation Contract

Agents working here must inspect `.hekton/project.yaml` before structural changes, record
meaningful design decisions in `docs/decisions.md`, and update `docs/next-actions.md` when the work
queue changes.

Vault mutation policy: see `vault_mutation_allowed` in `.hekton/project.yaml` (authoritative;
defaults to false at scaffold time). The repo-local `mind-palace/` folder is only a mirror draft;
do not write to the live vault unless `.hekton/project.yaml` says mutation is allowed and it is
explicitly authorised in-session.
