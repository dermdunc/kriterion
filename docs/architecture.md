# Architecture: Kriterion

## Overview

Kriterion is an **evidence-backed decision instrument** for uncertain technology investments,
built as a standalone Hekton **factory output**. Its identity has two layers:

```text
Kriterion V1   Decision Instrument    the decision journey a CIO/CFO actually reads (docs/index.html)
Kriterion V0   Decision Laboratory    the pre-registered multi-agent experiment, preserved intact (docs/lab.html)
```

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
| `report/` | Single-file static HTML decision record. No server, no JS build |
| `cli.py` | `kriterion new｜ledger｜econ｜run｜decide｜contract｜evals｜compare｜report｜doctor｜assurance` |

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
