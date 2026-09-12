# Human Run 001 — Preparation Report

Public summary. Structure, counts, verdicts and methodology only; no case content, no evidence
claims, no decision-rights entries, no economics figures, and not the synthetic recommendation.
The detailed version is `kriterion-private/human-run-001/preparation-report-detail.md`.

**Read after T2.** This file records observations about the generated page's quality that would
bias section 5 and the Narrative Integrity question in the retrospective if read beforehand.

---

## Case

Case id: `international-platform-engineering`.

Decision, as frozen in the case pack:

> What International platform-engineering operating model should be funded for the next 12-18
> months, and what responsibilities, decision rights and enterprise control-plane access should
> International own versus consume from global platform teams?

The pack lives outside this repository, at
`kriterion-private/human-run-001/case/international-platform-engineering/case.toml`. Naming follows
the existing `cases/` convention (subject, kebab-case, no run prefix); a `human-run-001-` prefix was
rejected because the case outlives the run.

Four alternatives, mapping one-to-one onto the four operating-model archetypes in the decision
brief. `do_nothing` — required by `DecisionCase`'s own invariant — carries real content here,
because the status quo genuinely is the enterprise-led archetype. The investment dimension reuses
Kriterion's existing `DecisionAction` vocabulary unchanged; no parallel stage system was created.

---

## Evidence

40 items in ledger v1. Separation by epistemic class:

| Category | Count |
|---|---|
| `MEASURED` | **0** |
| `EXTERNAL_REFERENCE` | 15 |
| `EXPERT_JUDGMENT` | 5 |
| `INFERENCE` | 3 |
| `ASSUMPTION` | 6 |
| `UNKNOWN` | 11 |
| `FORECAST` | 0 |

**External evidence** (15 items) all derive from one real, already-public document: a
deep-research whitepaper on international platform engineering in the agentic enterprise, published
by the participant under their own identity in a public repository before this experiment existed.
It cites named public sources across cloud providers, banks, technology companies and published
frameworks. These items carry `attestation = "REAL"` — the first use in Kriterion of the value
ADR-003 reserved and V0 never used. Labelling real, citable research `AUTHORED` would have
understated it. Coverage was checked for one-sidedness: roughly half the external items constrain
greater regional authority rather than supporting it, and one carries the limit of its own inference
inside its claim text, stating what the cited evidence does *not* establish.

**Current-state observations: none.** This is the most important structural fact about the case.
No internal baseline existed — no ticket-volume, lead-time, waiting-time, cost, headcount or
org-chart data. Every place where a current-state observation would have been required is recorded
as an explicit `UNKNOWN`. Nothing was estimated from plausibility and nothing was promoted into a
stronger class to make the case look complete. For contrast, Kriterion's canonical fixture opens
with seven `MEASURED` telemetry items.

**Expert judgment** (5 items) are the whitepaper's own analytical judgements, which that document
itself labels as inference rather than as source claims. Each item's `source` field flags that the
author is the participant. That circularity biases toward `T0 ≈ T1`, i.e. against the product
hypothesis, which makes a movement finding more credible and a null finding less informative.

**Assumptions** (6 items), all `LOW` evidence strength: four substantive decision assumptions and
two explicitly labelled illustrative sizing figures. One substantive assumption carries
`contradicts` pointing at an external-evidence item, because the research names the corresponding
failure mode of that exact proposal directly. Kriterion's `contradicts` field carried the tension
structurally rather than leaving it in prose, and the committee picked it up: all five seats
independently named that assumption as their distrusted one.

**Unknowns** (11 items) cover the quantities the decision would need and does not have, including
which of three candidate binding constraints actually binds — a distinction that implies three
different answers and which nothing in the case resolves.

---

## Economics

**What Kriterion could represent honestly: the cost side, and nothing else.**

The decision's benefit-side drivers are cost of delay, central-queue dependency, duplicated
regional effort, enterprise support demand, fork/divergence cost, initiatives unblocked, reuse
contributed upstream and time-to-market improvement. Every one of them is an `UNKNOWN` in this
ledger. None was given a number.

Consequences, all deliberate:

- The result is negative in every scenario, by construction, because only costs are summed.
- **No benefit band is reported at all** — not even the alongside-NPV band Kriterion's Case C
  fixture carries. This case cannot honestly state a band, so the result carries `None`, not `0`.
  Absence had to stay absence, and making that possible was the one product change this preparation
  made.
- The sensitivity ranking has exactly **one** entry, because the cost of the capability is the only
  quantity the case can vary. A one-entry tornado is the honest output here.
- The ask amount is illustrative sizing, explicitly labelled, because `Ask.amount_gbp` is a
  required non-optional float. A case whose ask has genuinely not been sized cannot record that
  absence. A labelled illustrative figure was preferred to a false zero.

No ROI, NPV or payback figure was fabricated to give the engine more to work with.

---

## Challenge structure

Kriterion's `CommitteeSeat` is a closed five-value enum: `cfo`, `cto`, `ciso`, `cro_compliance`,
`business_executive`. CIO was explicitly cut as a voting seat in V0. The perspectives this decision
actually needs map only partially onto it:

| Perspective the decision needs | Seat | Fidelity |
|---|---|---|
| CFO | `cfo` | Exact |
| Enterprise CTO / Architecture | `cto` | Good |
| Enterprise Platform Leader | — | **No seat** |
| International CIO | — | **No seat** (cut in V0) |
| Regional Technology Leader | `business_executive` | Weak proxy |
| — | `ciso` | Not requested, but fits: delegated control-plane access, entitlement sprawl, JIT privilege |
| — | `cro_compliance` | Not requested, but fits: regional regulatory adaptation, divergence risk |

The missing Enterprise Platform Leader is the sharpest loss: global coherence, platform ownership,
avoiding duplication and upstream contribution is arguably the most important challenge to this
decision, and there is no seat that can carry it. No seat was added — adding one ripples through
the charters, the eval harness, the decision state, the narrative binder and the page.

All five seats participated (5/5 initial, 5/5 revised). Two observations about what they produced
are recorded in the private detailed report, because they bear on the quality of what the
participant will read rather than on the preparation.

---

## EvidenceRequests

10 `EvidenceRequest` records persisted, comprising **2 distinct requests repeated verbatim across
all five seats**. Quality assessment, applying the brief's own standard rather than counting them
as a success:

| Request shape | `would_change` | Assessment |
|---|---|---|
| Measure the cost of delay per delayed initiative, to quantify economic benefit | `NPV` | **Adequate.** Names a specific quantity, names what it would move, and is obtainable in principle. No threshold, so it does not say what value would flip the decision. |
| Determine whether the binding constraint is capacity, decision rights or prioritisation | Operating model and funding requirements | **Weak.** Points at the right question, but specifies no method, no threshold and no falsifiable outcome. "Conduct an analysis to determine" is close to the brief's own example of a vague request. |

Neither request specifies a threshold, and neither is owned by a seat in any meaningful sense given
that all five produced the same two. Both are recorded here as what they are. They are **not**
rewritten into falsifiable tests for the write-up; converting a vague request into a crisp one after
the fact is exactly the epistemic laundering the evidence taxonomy exists to prevent.

Zero-threshold requests against a case with zero `MEASURED` items is a coherent result, not a
contradiction: the committee correctly identified that the missing quantities are missing, and could
not say how much of them would be enough.

---

## Product fit

```text
PRODUCT GAP FOUND
```

Four gaps. **One was fixed, because Human Run 001 could not otherwise run at all. Three were
recorded and left unfixed**, per the brief's instruction that a recorded limitation may be worth
more than code.

### Fixed — economics dispatch (hard blocker)

`kriterion.economics.CASE_ECONOMICS_FUNCTIONS` dispatches by case id, and both `kriterion run` and
`kriterion econ` exit 1 for an unregistered id. Without an entry there is no run, no page, no
sections 1-7 and no experiment. Confirmed empirically before changing anything:

```text
kriterion: econ failed: no cash-flow model wired for case
           'international-platform-engineering' yet
```

The change is generic, not case-shaped: `compute_cost_only_economics` generalises Case C's
cost-only construction with the avoided-loss band made **optional**, so a case that cannot honestly
state even a band carries `None` rather than a fabricated figure or an implied zero. Case C keeps
its own entry point and still requires its band. The Human Run 001 case id is registered, and its
single sensitivity parameter is mapped in `decision_state` so the page names the case pack's own
ranged assumption rather than a raw engine parameter. No case content enters this repository — only
the case id.

### Recorded, not fixed — the five role charters are coupled to the original fixture

The five `RoleCharter` files name `coding-agent-rollout`'s own evidence in their
`required_evidence`, `standard_challenges` and `failure_modes` (a pilot security review, regulated
customer data, an untyped legacy codebase). Those expectations are injected into any case the
charters are used on, and they surfaced in this run's artifacts as content that does not exist in
this case. One such string reaches the generated page. Detail and exact locations are in the private
report.

This is the sharpest generalisability finding available: **Kriterion's committee does not yet
generalise beyond the case it was built for.** Rewriting the charters would have been a
significant product change, and would have changed what every future run produces, on the basis of
a single case. Recorded instead.

### Recorded, not fixed — `CaseRealism` cannot express a real decision

`CaseRealism` defines exactly one value, `AUTHORED_FIXTURE`, and `DecisionCase.case_realism`
defaults to it with no case-pack override. The generated decision page therefore banners a real
decision as an authored fixture, and asserts in unbound prose that the case and its evidence are
authored fixtures. For this case that statement is false about the evidence, which is real, cited,
public research.

Not fixed, for two reasons. The mislabel errs conservative — it understates realism rather than
claiming `REAL` for synthetic material, which is the direction that would matter. And fixing it
properly means a new enum value plus conditional unbound prose in the page template, which is
template surgery on the only artifact Narrative Integrity cannot check, undertaken mid-experiment.
The evidence table does tell the truth: those items carry `attestation = "REAL"`, so the page
contradicts itself rather than lying uniformly.

### Recorded, not fixed — a derived economics sentence can outrun its model

`DecisionState.economics_interpretation` selects its wording from the sign of the NPV triple alone.
Under a cost-only model with no benefit term, that produces a valuation claim about a model that
contains no valuation. Narrative Integrity passes it, correctly: the sentence is faithfully derived
from the state.

That is the finding, and it is the most interesting one in this report. **Narrative Integrity
guarantees that the page says what the artifacts say. It does not guarantee that a derived summary
respects the epistemic status of what it is summarising.** Those are different properties, and only
the first is currently enforced.

Not fixed for a specific reason: the only case it affects is this one, so a guarded fix would be
tailoring the instrument to the experiment it is about to be measured on. The impact log already
asks whether anything on the page appeared more conclusive than the evidence justified. Pre-fixing
the best available answer to that question, or pre-announcing it, would destroy the measurement.

---

## Pre-registration

Committed in this directory, blank, before the participant saw any Kriterion analysis of this case:

| Artifact | Contents |
|---|---|
| `README.md` | Experiment scope, public/private split, start sequence |
| `protocol.md` | Research question, T0/T1/T2 design, interpretation rules, **both falsification conditions**, freeze rules, reading order |
| `case-design.md` | Decision, why this case, three dimensions, evidence boundaries, economic limits, six experiment risks |
| `decision-impact-log.md` | The blank instrument: T0, sections 1-7, T1, the explicit stop before section 8, T2, trajectory table, falsification check |
| `opus-preparation-report.md` | This file |

The instrument preserves, unchanged: the `Do not scroll ahead` stop before the synthetic
recommendation; the prompt asking exactly what moved the participant between T0 and T1, naming a
specific section rather than "the evidence"; and the final position-trajectory table with its
reading guide. Its header now records the real case id, the code commit, the case content freeze and
the canonical run id and seed.

Blank decision-rights tables for T0/T1/T2 live privately, because their rows are organisation
specific. They are blank by design: the allocation is part of the decision, not an input to it,
and neither the case pack nor the generated page asserts or recommends any row.

---

## Frozen versions

| Field | Value |
|---|---|
| Code commit | `677d668adf285633ee113681ceb233256100f6ad` on `agent/opus/human-run-001-prep`, based on `origin/main` @ `5dac579` |
| Case commit | Not applicable — the private directory is deliberately not a git repository. The freeze is a content-hash manifest: `case.toml` sha256 `200aaa9fbf98221a00605191f5bfd50c32dd1eff5002fb85fe98bb1a7bd5bed1`, frozen 2026-09-12T10:03Z, with hashes for every run artifact in `kriterion-private/human-run-001/freeze-manifest.md` |
| Canonical run | `hr001-intl-platform-condC-s1` — condition C (full committee, phases 0-8), **seed 1** |
| Evidence ledger | v1, fingerprint `421019302391da70b8912d3ba8f3cc9364a01d1aded96a3d6711833ee55b5443`, 40 items |
| Generated page | 126,739 bytes, **0 narrative-integrity violations** |

Nothing above is mutated during the experiment. Material evidence arising during the run goes to
`post-t0-evidence.md` in the private directory.

Only one run was made. A second seed was not tried: selecting among runs would be choosing the
instrument after seeing what it says.

---

## Validation

Actually executed:

| Command | Result |
|---|---|
| `pytest` (before any change) | 350 passed |
| `pytest` (after) | **356 passed**, 6 new in `tests/economics/test_cost_only_flows.py` |
| `kriterion econ <case>` (pre-change) | exit 1, `no cash-flow model wired` — the blocker, confirmed |
| `kriterion econ <case>` (post-change) | exit 0, economics written |
| `kriterion ledger freeze <case>` | 40 items frozen, fingerprint recorded |
| `kriterion run <case> --condition C --seed 1` | exit 0, **5/5 initial, 5/5 revised**, no seat abstained |
| `kriterion decision-page <run> <case>` | exit 0, 126,739 bytes, **0 violations** |
| `kriterion decide` | exit 0 — verified **in a throwaway copy** of the run directory, then discarded |
| `kriterion contract` | exit 0 — same throwaway copy, funding action accepted with a measure and a kill criterion |
| `kriterion validate-run` | clean, no governance violations — same throwaway copy |

Checks against the readiness criteria:

- **Runs through Kriterion.** Yes, unchanged pipeline, case pack outside the repository.
- **Narrative Integrity passes.** Yes, zero violations. `kriterion decision-page` refuses to write
  a failing page, so a written page is the pass.
- **No unsupported claims silently strengthened.** Not fully. The evidence table, assumptions,
  unknowns and sensitivity attribution are faithful. One derived economics sentence outruns its
  model, and one page banner is false for this case. Both are named above; neither is silent.
- **Evidence provenance valid.** Yes. Every item names its source document and section; external
  items carry `attestation = "REAL"`.
- **Assumptions remain assumptions.** Yes, all six `LOW`, one carrying `contradicts` against the
  evidence base.
- **Unknowns remain unknown.** Yes, 11 items, none promoted, none estimated.
- **EvidenceRequests persist.** Yes, 10 records with `would_change` on each, written to
  `evidence_requests.json`.
- **Blank protocol, blank impact log, falsification conditions, T0/T1/T2 committed.** Yes, in this
  commit, blank.
- **Case and code frozen.** Yes, see above.
- **Synthetic recommendation hidden until T1.** Procedurally only. It exists in the frozen
  artifacts and on the page from the start; nothing technically prevents scrolling ahead. Stated as
  a design limitation in `protocol.md`, and the reason failure condition 2 is pre-registered.
- **No `HumanDecision` made during validation.** Confirmed. The canonical run directory contains no
  `human_decision.json` and no `outcome_contract.json`; both commands were exercised on a copy that
  has been deleted.

---

## Human Run readiness

```text
READY
```

Record T0 before viewing any Kriterion decision analysis.
