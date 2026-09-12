# Kriterion Human Run 001 — Protocol

**Status: pre-registered.** This file, the blank `decision-impact-log.md`, and `case-design.md`
were committed before the participant saw any Kriterion analysis of the Human Run 001 case. The
falsification conditions in this file are not to be revised after the result is known.

---

## Research question

> Does Kriterion improve a real accountable human's technology-investment judgment?

Not "does Kriterion produce a defensible-looking analysis". The product hypothesis is about the
human's judgment, so the measurement has to be about the human's judgment.

---

## Primary case

**International Platform Engineering Operating Model.**

Kriterion case id: `international-platform-engineering`. The case pack is private; see
`README.md` for why, and `case-design.md` for what is in it.

The decision:

> What International platform-engineering operating model should be funded for the next 12-18
> months, and what responsibilities, decision rights and enterprise control-plane access should
> International own versus consume from global platform teams?

This replaces an earlier plan to use the `coding-agent-rollout` fixture as the instrument while the
participant held a different decision in mind. That mismatch would have made the run measure
transfer between two unrelated decisions rather than Kriterion's effect on the decision at hand.
For Human Run 001, the Kriterion case, the evidence in sections 1-7, and the decision the human is
actually making are the same decision.

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

Each checkpoint records: preferred operating model, investment/commitment, decision stage from
Kriterion's own `DecisionAction` vocabulary, confidence out of 100, and the reasons.

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

## Pre-registered falsification conditions

These are the conditions under which this run counts as evidence **against** Kriterion's product
hypothesis. They are fixed now, before the result exists.

### Failure condition 1 — analysis theatre

If the final human rationale merely restates the synthetic recommendation without citing any
specific:

* evidence item;
* assumption;
* unknown;
* economic insight;
* challenge;
* EvidenceRequest;

surfaced by Kriterion, then the product may be producing **analysis theatre rather than improved
judgment**. The elaborate machinery in front of the recommendation would, on that evidence, be
decoration.

### Failure condition 2 — recommendation anchoring

If:

```text
T1 → T2 changes materially
```

but the participant cannot identify anything in sections 1-7 that justifies the change, treat this
as a potential **recommendation anchoring** signature. The instrument would then be moving the
human by assertion rather than by analysis, which is a worse outcome than having no effect at all.

**Neither condition is to be revised after seeing the result.** If either fires, it is reported as
having fired.

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

`decision-rights-matrix.md` (private) is completed at the same three checkpoints as the positions
and is safe to open at T0; it is blank by design.

---

## Instruments

| Instrument | Location |
|---|---|
| Blank impact log | `docs/planning/human-run-001/decision-impact-log.md` (public, committed blank) |
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
