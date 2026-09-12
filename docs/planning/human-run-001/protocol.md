# Kriterion Human Run 001 — Protocol

**Status: pre-registered.** This file, the blank `decision-impact-log.md`, and `case-design.md`
were committed before the participant saw any Kriterion analysis of the Human Run 001 case. The
falsification conditions in this file are not to be revised after the result is known.

---

## Research question

> Does Kriterion improve the quality of an accountable human decision about how to organise and
> invest in global platform engineering across a distributed enterprise?

Not "does Kriterion produce a defensible-looking analysis", and **not** "did Kriterion pick the
right operating model". The product hypothesis is about the human's reasoning, so the measurement
has to be about the human's reasoning: about evidence, assumptions, uncertainty, economics,
organisational trade-offs, decision rights, investment sequencing, and what evidence is required
before a larger commitment.

---

## Primary case

**Global Platform Engineering in a Distributed Engineering Organisation.**

Kriterion case id: `global-platform-engineering`. The case pack is private; see `README.md` for
why, and `case-design.md` for what is in it.

The decision:

> What global platform-engineering operating model should we invest in for the next 12-18 months so
> that distributed engineering teams gain sufficient autonomy and responsiveness without duplicating
> enterprise platforms or fragmenting global standards?

This replaces an earlier plan to use the `coding-agent-rollout` fixture as the instrument while the
participant held a different decision in mind. That mismatch would have made the run measure
transfer between two unrelated decisions rather than Kriterion's effect on the decision at hand.
For Human Run 001, the Kriterion case, the evidence in sections 1-7, and the decision the human is
actually making are the same decision.

A narrower first preparation of this case, framed as International-versus-Enterprise across three
operating models with a seven-row decision-rights matrix, was superseded by the final specification
before T0 was recorded. It was archived intact rather than overwritten; `case-design.md` records
the reasoning and the case-id change.

---

## Design: T0 / T1 / T2

Three position checkpoints, recorded in that order, each before the participant has seen the next
thing:

```text
T0    human prior, before opening Kriterion at all

T1    human position after evidence, assumptions, unknowns, economics,
      challenge perspectives and EvidenceRequests
      but BEFORE viewing the synthetic recommendation

T2    human position after viewing the synthetic recommendation
```

**Each checkpoint records three dimensions independently**, plus confidence:

| Dimension | Recorded as | Where |
|---|---|---|
| Operating model | one of CENTRAL / DISTRIBUTED ENTERPRISE / FEDERATED / REGIONAL AUTONOMY / HYBRID-OTHER | `decision-impact-log.md` |
| Distribution | where platform-engineering capability should physically exist, per region, and what those engineers own | private `distribution.md` |
| Decision rights | 13 rows, each ENTERPRISE / REGION / JOINT / UNDECIDED | private `decision-rights-matrix.md` |
| Investment | capability, region, capacity, duration, mandate, and a decision stage | `decision-impact-log.md` |
| Confidence | out of 100 | `decision-impact-log.md` |

The three dimensions are separable and a run may move one while the others hold. Collapsing them
into a single label would make that unobservable, which is why the instrument refuses to do it.

Distribution is recorded as a distinct dimension because the four operating models are not
distinguished by geography alone: distributed-enterprise and federated models can place engineers in
the same places while allocating authority completely differently. A position on *where* the
engineers are is not a position on *what they may decide*.

T1 exists because of one specific confound. A product that generates a recommendation and then
observes that the human agrees with it has measured nothing: the recommendation may have done the
work, or the analysis may have, and a single before/after pair cannot tell those apart. Inserting a
checkpoint between the analysis and the recommendation splits the effect.

**The stop before section 8 is the experiment.** If the participant reads the synthetic
recommendation before recording T1, the run produces no usable T1 and the primary measurement is
lost. The instrument says `Do not scroll ahead` for that reason.

---

## Interpretation

If:

```text
T0 != T1  and  T1 ≈ T2
```

then the decision analysis may have influenced judgment independently of the recommendation. This
is the outcome the product hypothesis predicts.

If:

```text
T0 ≈ T1  and  T1 != T2
```

then recommendation anchoring should be treated as a serious alternative explanation. The analysis
did not move the position; the stated conclusion did.

Neither pattern proves causality. One participant, one case, no control condition, and a
participant who knows the hypothesis. What the split does produce is a useful observational
distinction that a single before/after measurement cannot produce at all.

Two further patterns worth naming in advance:

- `T0 ≈ T1 ≈ T2` — the instrument did nothing to the decision. That is a legitimate and reportable
  result, not a failed run. The retrospective should still capture whether Kriterion changed the
  *rationale* or the *next action* without changing the position.
- `T0 != T1 != T2` in the same direction — analysis and recommendation both moved it, and this
  design cannot separate their contributions. Report it as unresolved rather than claiming the
  analysis did the work.

---

## Useful outcomes

Fixed in advance so that the success criteria are not inferred from whatever happens. A run in
which the position does not move is **not** a failed run. All of these are useful outcomes:

* no decision change, but a substantially better rationale;
* **lower** confidence, because hidden uncertainty became visible;
* a **smaller** initial investment, because the human decides to buy evidence first;
* a different allocation of decision rights;
* identifying that the bottleneck is authority rather than engineering capacity;
* identifying that distributed engineering is more important than initially believed.

Three of those six are movements Kriterion would register as *less* progress — less confidence, less
money, less resolution. They are counted as successes here, before the result exists, so that a
result in that direction cannot later be reported as a disappointment.

---

## Pre-registered falsification conditions

These are the conditions under which this run counts as evidence **against** Kriterion's product
hypothesis. They are fixed now, before the result exists.

Kriterion has failed to demonstrate useful decision impact if:

### 1 — the final rationale merely copies the synthetic recommendation

If the recorded rationale restates what Kriterion recommended without citing any specific evidence
item, assumption, unknown, economic insight, challenge or EvidenceRequest that the session
surfaced, then the machinery in front of the recommendation was decoration. This is **analysis
theatre**.

### 2 — the human cannot identify a specific Kriterion input that affected reasoning

Distinct from condition 1, and it fires independently of whether the recommendation was followed.
A participant who overrules the recommendation but still cannot name one input that changed how
they reasoned has been given structure without content. "The analysis" is not an answer; the
instrument says so at the point of asking.

### 3 — the recommendation changes T1 → T2 without an evidence-based justification

If the position moves between T1 and T2 but the participant cannot name what in sections 1-7
justifies the move, treat it as a **recommendation anchoring** signature. The instrument would then
be moving the human by assertion rather than by analysis, which is worse than having no effect at
all. The T2 section asks this directly rather than leaving it to be inferred later.

### 4 — the process generates more structure without materially improving understanding

Kriterion produces sections, seats, categories, tornado entries and persisted requests whether or
not they carry content. If the participant can point to no place where a structural distinction
changed what they understood, the structure is overhead. Recorded per section via the impact
labels, and the `NOISE` label exists so this condition has somewhere to show up in-session.

### 5 — the operating model becomes more complicated but not more actionable

The failure specific to this decision. A recommendation that adds a coordination layer, a
consultation step or a joint-ownership row without removing a dependency has made the organisation
harder to describe and no faster to work in. Check it against the Investment and Conditions
sections of the human decision: if the smallest useful commitment cannot be stated, or if no
enumerated dependency is removed by it, this condition has fired.

**No condition is to be revised or reinterpreted after seeing the result.** If one fires, it is
reported as having fired. Conditions 4 and 5 are the two most easily explained away in hindsight,
which is why the instrument requires them to be answered against what was written down rather than
against how the session felt.

---

## What is frozen, and when

Before T0 is recorded:

1. the case pack is complete;
2. `kriterion econ` has run and its output is committed to the private run directory;
3. the deliberation run has completed and its artifacts are written;
4. `kriterion decision-page` has generated the page and Narrative Integrity passed with zero
   violations (the command refuses to write a page that fails, so a written page *is* the pass);
5. the exact Kriterion code commit is recorded;
6. the case pack's content freeze is recorded (the private directory is not a git repository, so
   the case "commit" is a content-hash manifest plus timestamp, not a SHA);
7. the run id and seed are recorded.

After T0 is recorded, none of that state is mutated. Material new evidence that appears during the
run is written to `post-t0-evidence.md` in the private run directory and is explicitly **not**
folded back into the frozen case. Editing the case mid-experiment would silently rewrite what the
participant was responding to.

The synthetic recommendation exists in the frozen artifacts from the start. It is not withheld
technically, only procedurally. That is a real limitation of this design and is recorded in
`case-design.md`.

---

## Reading order, and what not to read

Do not read these before T2:

- `opus-preparation-report.md` (this directory). It does not state the synthetic recommendation, but
  it does record specific observations about the generated page's quality, which would bias section 5
  and the Narrative Integrity question in the retrospective.
- `freeze-manifest.md` and `preparation-report-detail.md` (private). Both state the synthetic
  recommendation outright, so reading either destroys the T1 checkpoint.

`decision-rights-matrix.md` and `distribution.md` (both private) are completed at the same three
checkpoints as the positions and are safe to open at T0; both are blank by design.

The superseded first preparation is archived privately under `superseded/`. Its freeze manifest and
run artifacts state a synthetic recommendation for a case the participant will never be shown, and
the two cases share most of their evidence base, so that directory is also not to be opened before
T2.

---

## Instruments

| Instrument | Location |
|---|---|
| Blank impact log | `docs/planning/human-run-001/decision-impact-log.md` (public, committed blank) |
| Blank decision-rights matrix (13 rows × T0/T1/T2) | private, never committed |
| Blank distribution artifact (4 regions × T0/T1/T2) | private, never committed |
| Completed impact log | private run directory, never committed |
| Generated decision page | private run directory, never committed |
| `HumanDecision` | `kriterion decide`, written to the private run directory |
| `OutcomeContract` | `kriterion contract`, only if the decision is a funding action |

`kriterion decide` writes `human_decision.json` as a separate file from `recommendation.json` and
never touches the latter (ADR-006). The human's decision and the machine's recommendation stay
distinguishable in the artifacts, which is what makes "FOLLOWED / MODIFIED / OVERRULED" a
checkable claim rather than a recollection.

---

## What this is not

This is not a controlled scientific study. There is no control condition, no blinding, n=1, and the
participant knows the hypothesis and designed the instrument. It is a structured product
experiment with a pre-registered stopping rule and pre-registered failure conditions, which is
enough to make a negative result survivable and a positive result honestly qualified.
