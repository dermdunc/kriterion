# Architecture: Kriterion

## Overview

Kriterion is an **evidence-backed decision instrument** for uncertain technology investments,
built as a standalone Hekton **factory output**. Its identity has two layers:

```text
Kriterion V1   Decision Instrument    the decision journey a CIO/CFO actually reads (docs/index.html)
Kriterion V0   Decision Laboratory    the pre-registered multi-agent experiment, preserved intact (docs/lab.html)
```

## Architectural principles

Two principles govern everything Kriterion shows a human. They began as decisions about the
public page (ADR-011, ADR-012) and are **standing principles** as of ADR-013: they bind every
projection Kriterion adds from here on, including reports, CLI output, any future API and any
future demo, not just `docs/index.html`.

### Principle 1: There is one decision state. Everything else is a view.

The authoritative state of a Kriterion decision lives in structured domain state and persisted
artifacts. HTML pages, executive summaries, reports, charts, CLI output, future APIs and demos are
**projections** of that state. They must not become independent narrative stores.

```text
Evidence · Assumptions · Economics · Challenges · EvidenceRequests
SyntheticRecommendation · HumanDecision · OutcomeContract
                          |
                          v
                    DecisionState
                          |
                          v
                     projections
             +------------+------------+
             v            v            v
          website      report         CLI
```

and never:

```text
DecisionState + a separately authored executive narrative + a separately authored website
```

### Principle 2: Narrative is executable output, not commentary.

A human-facing statement about a decision is part of the decision system, and is therefore subject
to the same integrity expectations as a calculation. A narrative statement must not strengthen,
soften or invent evidence; change a decision state; attribute reasoning to the wrong actor; convert
an assumption into a fact or an unknown into an absence of risk; reinterpret deterministic
economics; or collapse a synthetic recommendation and a human decision into one thing.

```text
authoritative state -> narrative projection -> integrity bindings -> validation gate -> publish
```

If integrity validation fails, the build does not publish. That is intended system behaviour, not
an exceptional inconvenience.

### The consequence: publication is a controlled transformation of decision state

Not a third branded principle, but the operational rule the first two imply:

- an invalid run artifact must not become a polished page;
- an untraceable executive claim must not publish;
- a malformed input must fail through a controlled refusal, never a raw traceback;
- presentation code does not get a weaker trust boundary than calculation code.

The last one is the point most easily lost. Every defect of substance found in the V1 review lived
in presentation, not calculation (see [`project-walkthrough.md`](project-walkthrough.md)).

### Where the principles are *enforced*, and where they are only *held*

The distinction matters, because claiming mechanical enforcement that does not exist is itself the
failure mode ADR-010 had to retract:

| Surface | Principle 1 | Principle 2 |
|---|---|---|
| `docs/index.html` (`report/decision_page.py`) | Enforced. Rendered from `DecisionState`; a test asserts the committed page is byte-identical to a fresh render | Enforced. Every material value bound and re-derived; unbound prose scanned; `kriterion decision-page` refuses to write on any violation |
| `runs/*/report.html` (`report/html.py`) | Held by review. Reads the same artifacts, but through its own loaders, not the projection | Not enforced. No bindings, no checker |
| `docs/lab.html` | Held by review. Hand-authored research page; content-checked by test, not generated | Not enforced |
| CLI output | Held by review | Not enforced |
| Future API / demo | Bound by ADR-013 before it is built | Bound by ADR-013 before it is built |

Extending the checker to the other projections is named work in
[`next-actions.md`](next-actions.md), not done work.

## How the projection works

The decision journey is a **projection**, not a second artifact maintained beside the state
(ADR-011). There is one decision state; everything a human reads is a view of it:

```text
    case pack + frozen evidence ledger + assumptions + deterministic economics
  + per-seat positions, belief updates and evidence requests
  + synthetic recommendation + human decision + outcome contract
  + (optional) imported assurance evidence
                                 |
                                 v
                       DecisionState   (one read-only projection;
                                        derived values computed once, here)
                                 |
                                 v
            renderer  ->  narrative-integrity check  ->  refuse or publish
                                 |
                                 v
                      the decision experience a human reads
```

rather than:

```text
              state   +   a hand-authored website describing it
```

The check in the middle is the load-bearing part (ADR-012): every material statement is stamped
with the state path it was rendered from and re-derived from the authoritative record before
publication, and the build refuses to write a page that fails. The Lab keeps its own renderer, so
frozen research output is never rewritten by a change to the instrument's presentation.

### The public experience, end to end

Website content lives **entirely inside this repository**. There is no separate site repo, no
static-site generator and no CI build step:

```text
cases/<id>/ + runs/<run-id>/            committed decision state
        |
        v  bash scripts/build-decision-page.sh <run-id>
        |    1. assurance import  -> cases/<id>/assurance/imported.json
        |    2. kriterion report  -> docs/reports/decision-record.html
        |    3. kriterion decision-page  -> narrative check -> docs/index.html
        v
docs/  (index.html, lab.html, reports/, CNAME)
        |
        v  merge to `main`
        |
GitHub Pages (legacy build, source `main:/docs`)  ->  kriterion.theagentictekton.com
```

Two consequences worth being explicit about:

- **Publication is a git operation, not a build step.** Pages serves `main:/docs` directly, so the
  public site shows whatever `docs/index.html` is on `main`. A regenerated page on an unmerged
  branch has not been published, however correct it is.
- **`infra/github-pages-dns/` is DNS only** (Route53 CNAME + verification TXT, Terraform, applied
  by a human). It carries no content and does not need to change when the page does.

The five-seat AI committee is one challenge mechanism inside the instrument, not the product.
That framing is earned, not asserted: V0's own honest-negative finding (the committee did not
beat both baselines on at least 2 of 3 categories of the pre-registered bare-aggregate check) is
recorded, published, and kept. Mechanically, Kriterion ingests an investment proposal, separates evidence from
assumptions from unknowns, computes the economics deterministically, elicits independent
role-specific assessments, runs structured adversarial challenge, records how positions changed and
why, and produces a synthetic recommendation with preserved dissent — which an accountable human
then accepts, changes or rejects as a separate recorded decision.

The V0 layer exists to test a falsifiable claim: **does running a case through multiple independent AI
contexts improve evidence discipline, challenge quality and traceability, compared with running the
same rigorous protocol through a single strong AI context?** The protocol is held constant across
conditions; only the number of independent contexts varies. V0 must be able to produce, and
publish, the finding that it does not.

**The full plan is [`v0-plan.md`](v0-plan.md)** — product thesis, ADRs, domain model, deliberation
protocol, experimental design, eval plan, case fixtures, build plan and kill criteria.

## Components

| Component | Responsibility |
|---|---|
| `domain/` | `DecisionCase`, `EvidenceItem`, `Assumption`, `Scenario`, `RoleCharter`, `CommitteePosition`, `Challenge`, `BeliefUpdate`, `SyntheticRecommendation`, `HumanDecision`, `OutcomeContract`. Dataclasses, canonical JSON, no I/O |
| `economics/` | Deterministic engine: cash flows, NPV (low/base/high), payback, peak funding, one-way sensitivity, unit economics, staged-funding table. Pure functions, golden-tested. Never falls back to a model |
| `protocol/` | The 11-phase state machine, the **deterministic procedural chair**, and deterministic position aggregation |
| `executors/` | The `Executor` port. **The only place `hekton_llm` may be imported.** Ships an Ollama adapter and a replay adapter |
| `evals/` | Kriterion's own harness — fixtures × conditions, deterministic scorers plus (secondary) judge scorers |
| `export/` | `kriterion-run-export/v0.1` — application telemetry. Not an assurance contract |
| `assurance/` | ADR-007 anti-corruption layer: reads a generic `AssuranceEvidenceEnvelope` document pair (`envelope.json` + optional `decision.json`, 0.x shape) with a tolerant parser and maps it into `EvidenceItem`s, epistemic categories preserved. Never imports assurance code |
| `decision_state.py` | **Principle 1.** `DecisionState`: one read-only projection of a run. Every field either *is* a domain record loaded from a committed artifact or is a pure function of those records; the derived values a decision-maker needs but nobody stores (capital actually at risk, the dominant sensitivity, the economics interpretation, what happens next) are computed here, once, so a checker can re-derive them. Refuses malformed artifacts by name rather than raising a traceback |
| `narrative.py` | **Principle 2.** `bind()` stamps a rendered value with the state path and formatter it came from; `check()` re-resolves every path against the authoritative state and refuses any element whose text is not exactly what the state says. Plus rules over unbound prose (no retyped figures, no unbound state vocabulary, no softening words, no recommendation claims) and structural rules over attribution and human/AI separation |
| `report/` | Two renderers, deliberately not shared. `html.py` is the per-run research record; regenerating a committed V0 `report.html` would rewrite a frozen research artifact, so presentation changes to the instrument must not touch it. `decision_page.py` renders the public decision experience from a `DecisionState`, deterministically (pinned timestamp, no wall clock), which is what lets a test assert the committed page is byte-identical to a fresh render |
| `cli.py` | `kriterion ledger｜econ｜doctor｜run｜decide｜contract｜validate-run｜evals｜compare｜report｜decision-page｜assurance｜perturbation-diff`. `decision-page` runs the narrative-integrity check as a publish gate and exits non-zero without writing on any violation |

**Stack:** Python ≥3.11, **zero runtime dependencies**. Case packs and charters in TOML via stdlib
`tomllib`; all machine artifacts in canonical JSON. `pytest` is the only dev dependency.

## Data Flow

```text
cases/<id>/case.toml
  └─ kriterion ledger ─► runs/<id>/ledger.frozen.json   (fingerprinted, append-only)
  └─ kriterion econ   ─► runs/<id>/economics.json       (hashed; computed BEFORE any model call)

kriterion run --condition {A|B|C}
  ─► positions.initial.json → tally.sealed.json → challenges.json → evidence_round.json
     → positions.revised.json → belief_updates.json → recommendation.json

kriterion decide ─► human_decision.json      kriterion contract ─► outcome_contract.json
kriterion report ─► report.html              kriterion evals ─► run-export.json
                                             kriterion compare ─► comparison.json + .md
```

Every run directory carries `manifest.json` — protocol version, model IDs and digests, case and
ledger fingerprints, charter versions, template hashes, seeds, tokens, timings, and measured
nondeterminism. That manifest is the reproducibility claim.

**Boundary rules.** Dependency direction is strictly Hekton → Kriterion. The only Hekton runtime
import is the `hekton_llm` namespace (provider surface only; routing explicitly excluded), confined
to `executors/`. There is **no code edge to `hekton-assurance-lab`, in either direction** — no
import, no shared file, mechanically enforced by `tests/executors/test_boundary.py`. What ADR-007
adds (V1) is a **data-document edge only**: Kriterion can read a generic assurance envelope +
decision pair as JSON documents through `src/kriterion/assurance/`, the sole module that knows the
format. The producer side (Hekton Assurance's 0.x `EvidenceEnvelope`) carries no Kriterion
concept — no proposals, committees, votes, stages or recommendations — and Kriterion runs
identically when no assurance documents exist: assurance is an optional evidence source, never a
runtime dependency. No Kriterion abstraction is proposed for promotion until a second,
genuinely different factory output needs the same semantic capability.

**Invariants enforced in code, not convention:** no member sees any tally before phase 8; only
`kriterion ledger add` writes evidence (there is no path from model output into the ledger);
`SyntheticRecommendation` and `HumanDecision` are separate files and separate UI regions; every
`EvidenceItem` carries an `attestation` alongside its epistemic category.

## Design Decisions

See [decisions.md](decisions.md) for ADR log.
