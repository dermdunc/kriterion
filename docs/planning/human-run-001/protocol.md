# Kriterion Human Run 001 — Protocol

**Status: pre-registered.** This file, the blank `decision-impact-log.md`, and `case-design.md`
are committed before the participant records T0 or sees any Kriterion analysis of the Human Run 001
case. The falsification conditions in this file are not to be revised after the result is known.

---

## Research question

> Does Kriterion improve a human's technology-investment judgment?

Concretely, for this run:

> Does Kriterion improve the quality of an accountable human decision about whether, and at what
> scale, to invest in an Internal Developer Platform?

Not "does Kriterion produce a defensible-looking analysis", and **not** "did Kriterion pick the
right investment". The product hypothesis is about the human's reasoning, so the measurement has to
be about the human's reasoning: about evidence, assumptions, uncertainty, economics, adoption
risk, attribution, investment sequencing, and what evidence is required before a larger commitment.

---

## Primary case

**Northstar Software Group — Internal Developer Platform investment.**

Kriterion case id: `northstar-internal-developer-platform`. The case pack is
`cases/northstar-internal-developer-platform/case.toml`, committed in full to this repository.

The decision:

> Should Northstar Software Group invest approximately £3m–£5m over the next 18 months in an
> Internal Developer Platform, or pursue a lower-cost programme of incremental improvements to its
> existing engineering toolchain?

The load-bearing tension underneath it:

> Will reducing developer friction create attributable business value, or primarily move complexity
> and cost from application teams into a new platform organisation?

**Northstar Software Group is fictional.** It is not a real company and not a pseudonym for one.
Every Northstar-specific number in the case is a synthetic scenario input, labelled as one in the
case pack and badged `AUTHORED` on the generated page. The external research the case cites is
real, public and badged `REAL`. `case-design.md` sets out the boundary in full.

This is deliberate. The case is intended to be the first **fully public, fully reproducible**
Agentic Tekton Kriterion use case: a reader can read the case pack, re-run the deterministic parts,
and check every claim the page makes. That is only possible with a case whose underlying evidence
can be published.

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
| Strategy | one of OPTIMISE EXISTING TOOLCHAIN / BUY COMMERCIAL PLATFORM / BUILD THIN INTERNAL PLATFORM / BUILD STRATEGIC IDP / HYBRID-STAGED | `decision-impact-log.md` |
| Investment | capital or operating commitment, duration, stage, team/capacity, scope | `decision-impact-log.md` |
| Evidence gate | what must be demonstrated before the next stage receives funding | `decision-impact-log.md` |
| Confidence | out of 100 | `decision-impact-log.md` |

The three dimensions are separable and a run may move one while the others hold. Collapsing them
into a single label would make that unobservable, which is why the instrument refuses to do it.

The **evidence gate** is a dimension in its own right rather than a footnote on the investment,
because it is the dimension this case is built to stress. A participant can hold their strategy and
their headline number completely still and still have made a materially better decision, by naming
what would have to be true before the next tranche is released. An instrument that recorded only
"which option, how much" could not see that happen.

T1 exists because of one specific confound. A product that generates a recommendation and then
observes that the human agrees with it has measured nothing: the recommendation may have done the
work, or the analysis may have, and a single before/after pair cannot tell those apart. Inserting a
checkpoint between the analysis and the recommendation splits the effect.

**The stop before the recommendation is the experiment.** If the participant reads the synthetic
recommendation before recording T1, the run produces no usable T1 and the primary measurement is
lost.

---

## Reading order, and the redaction the product does not perform

The generated decision page renders thirteen sections. They are read in order, with one stop:

```text
1.  The decision                          }
2.  What we know                          }
3.  What we are assuming                  }
4.  What we do not know                   }  sections 1-8, read in full
5.  The economics                         }  recording impact as you go
6.  Capability assurance                  }
7.  Perspectives                          }
8.  What would change this                }

    ---- STOP.  Record T1 before continuing. ----

9.  Synthetic recommendation              }  record T2 immediately after
10. Human decision                        }
11. Outcome contract                      }
...
```

### Reading-order caveat: section 1 leaks the recommendation

**This is a known product limitation, and it must be handled procedurally before the run starts.**

Section 1, "The decision", was designed under the V1 homepage pattern of leading with the decision.
It therefore places, at the top of the page:

- the synthetic recommendation action;
- its stated confidence band;
- the capital the recommendation would put at risk;
- the dominant economic uncertainty and its NPV swing.

Reading section 1 top-to-bottom therefore reveals the recommendation **before** the reader reaches
the section that is supposed to reveal it. The blind-reveal design this protocol depends on is not
enforced by the product; the product's own front page contradicts it.

**Required handling, for this run and any future run using this page:**

> When presenting section 1, withhold the synthetic recommendation, the stated confidence, the
> capital-at-risk figure and the dominant-uncertainty line. Present the rest of section 1 — the
> decision requested, the amount requested, sponsor, decision owner, deadline and the alternatives
> — in full. Reveal the four withheld lines at the section-8-to-section-9 transition, together with
> the recommendation section itself. Sections 2 to 8 are presented in full, unredacted.

The redaction happens **outside** the product, by whoever is running the session. That is the
limitation, stated plainly: an instrument whose blind-reveal protocol depends on a human
remembering to withhold four lines has not implemented blind reveal. It is recorded here rather
than fixed, because fixing it means changing what the public decision page is for, which is a
separate product decision and not one to make in the middle of pre-registering an experiment.

If the redaction fails and the participant sees the recommendation before recording T1, **the run
produces no T1** and that must be reported, not worked around.

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

* no strategy change, but a substantially better rationale;
* **lower** confidence, because hidden uncertainty became visible;
* a **smaller** initial commitment, because the human decides to buy evidence before buying scale;
* a sharper evidence gate — the same money, released against a named, falsifiable demonstration
  rather than a date;
* identifying that the binding constraint is not toolchain fragmentation at all;
* identifying that adoption, not capability, is what the investment has to buy.

Four of those six are movements Kriterion would register as *less* progress — less confidence, less
money, less resolution, a slower ladder. They are counted as successes here, before the result
exists, so that a result in that direction cannot later be reported as a disappointment.

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

If the position moves between T1 and T2 but the participant cannot name what in sections 1–8
justifies the move, treat it as a **recommendation anchoring** signature. The instrument would then
be moving the human by assertion rather than by analysis, which is worse than having no effect at
all. The T2 section asks this directly rather than leaving it to be inferred later.

### 4 — the process generates more structure without materially improving understanding

Kriterion produces sections, seats, categories, tornado entries and persisted requests whether or
not they carry content. If the participant can point to no place where a structural distinction
changed what they understood, the structure is overhead. Recorded per section via the impact
labels, and the `NOISE` label exists so this condition has somewhere to show up in-session.

### 5 — the investment becomes more elaborate but not more decidable

The failure specific to this decision. A recommendation that adds a stage, a workstream or a
governance forum without naming what evidence releases the next tranche has made the programme
harder to describe and no easier to decide. Check it against the Investment and Evidence-gate
dimensions: if the smallest useful commitment cannot be stated, or if no stage carries a
falsifiable demonstration that would release the next one, this condition has fired.

**No condition is to be revised or reinterpreted after seeing the result.** If one fires, it is
reported as having fired. Conditions 4 and 5 are the two most easily explained away in hindsight,
which is why the instrument requires them to be answered against what was written down rather than
against how the session felt.

---

## What is frozen, and when

Before T0 is recorded:

1. the case pack is complete and committed;
2. `kriterion econ` has run and its output is committed to the run directory;
3. the deliberation run has completed and its artifacts are written and committed;
4. `kriterion decision-page` has generated the page and Narrative Integrity passed with zero
   violations (the command refuses to write a page that fails, so a written page *is* the pass);
5. the exact Kriterion code commit is recorded;
6. the case pack's content freeze is recorded as a content-hash manifest plus timestamp;
7. the run id and seed are recorded.

After T0 is recorded, none of that state is mutated. Material new evidence that appears during the
run is written to a post-T0 evidence note and is explicitly **not** folded back into the frozen
case. Editing the case mid-experiment would silently rewrite what the participant was responding to.

The synthetic recommendation exists in the frozen artifacts from the start. It is not withheld
technically, only procedurally — see the reading-order caveat above. That is a real limitation of
this design.

**What is not committed until the experiment is actually performed:** the participant's T0, T1 and
T2 responses. `decision-impact-log.md` is committed blank, and it stays blank until the run
happens. Committing a blank instrument before the result exists is what makes the pre-registration
checkable; filling it in retrospectively would make every result unfalsifiable.

---

## Instruments

| Instrument | Location |
|---|---|
| Blank impact log | `docs/planning/human-run-001/decision-impact-log.md` (public, committed blank) |
| Case pack | `cases/northstar-internal-developer-platform/case.toml` (public, committed) |
| Frozen run artifacts | `runs/hr001-northstar-condC-s1/` (public, committed) |
| Generated decision page | `docs/human-run-001/decision-page.html` (public, committed) |
| Freeze manifest | `docs/planning/human-run-001/freeze-manifest.md` (public, committed) |
| `HumanDecision` | `kriterion decide`, written to the run directory after the experiment |
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

One thing the fictional case does buy that a real one could not: because Northstar is invented, the
participant has no privileged knowledge of the answer, no organisational stake in the outcome, and
no ability to substitute remembered facts for the case's evidence. The circularity that a real
self-selected case carries — participant as decision-maker, evidence author and product designer at
once — is reduced, though not eliminated, since the participant still authored the scenario.

---

## Relationship to other Kriterion runs

A separate private practitioner run is retained for a real-world operating-model decision where
confidentiality prevents publishing the underlying evidence. Nothing about that decision — the
organisation, the participant, the case content, the position, the recommendation or the evidence —
appears anywhere in this repository, and nothing in this protocol depends on it.
