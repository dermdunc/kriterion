# Kriterion Human Run 001 — Decision Impact Log

**Status: BLANK BY DESIGN. Committed before T0.**

This is the pre-registered instrument. It is committed empty, and it stays empty until the
experiment is actually performed. Filling it in retrospectively, or revising its questions after
seeing the result, would make every finding unfalsifiable — which is the whole reason it exists as
a committed artifact rather than a notebook.

Complete it **contemporaneously**. Answers written from memory after the session are a different
and much weaker measurement, and should be labelled as such if that is what happens.

---

## Run metadata

**Run:** Human Run 001
**Decision:** £3m–£5m Internal Developer Platform investment over 18 months, or incremental
toolchain improvement
**Kriterion case:** `northstar-internal-developer-platform` (`cases/northstar-internal-developer-platform/case.toml`, committed)
**Scenario:** Northstar Software Group — **FICTIONAL**. Every Northstar figure is a synthetic
scenario input.
**Canonical run:** `hr001-northstar-condC-s1` — condition C, seed 1
**Frozen artifacts:** `runs/hr001-northstar-condC-s1/`
**Generated page:** `docs/human-run-001/decision-page.html`
**Freeze manifest:** `docs/planning/human-run-001/freeze-manifest.md`
**Date:**
**Participant:**
**Status:** `PRE-REGISTERED`. Next action: `RECORD T0`.

---

## Three dimensions, recorded independently

This decision spans strategy, investment and evidence gate. They are separable: a run may move one
while the others hold, and collapsing them into a single label would make that unobservable.

| Dimension | Recorded as |
|---|---|
| **Strategy** | one of `OPTIMISE EXISTING TOOLCHAIN` / `BUY COMMERCIAL PLATFORM` / `BUILD THIN INTERNAL PLATFORM` / `BUILD STRATEGIC IDP` / `HYBRID-STAGED` — or an explicit combination |
| **Investment** | capital or operating commitment, duration, stage, team/capacity, scope |
| **Evidence gate** | what must be demonstrated before the next stage receives funding |
| **Confidence** | out of 100 |

The **evidence gate** is a dimension in its own right, not a footnote on the investment. A
participant can hold their strategy and their headline number completely still and still have made
a materially better decision, by naming what would have to be true before the next tranche is
released.

---

## Before you start

1. Read `protocol.md`, including the **reading-order caveat**. The generated page's section 1
   states the synthetic recommendation, its confidence, the capital at risk and the dominant
   uncertainty at the top, by V1 product design. Those four lines must be withheld until the
   section-8-to-9 transition. The product does not do this for you.
2. Do **not** open `runs/hr001-northstar-condC-s1/recommendation.json`, `narrative.txt` or
   `positions_*.json` before T1. They state or imply the recommendation.
3. Do not read `opus-pivot-report.md` before T2.
4. `freeze-manifest.md` is safe to read at T0: it deliberately omits the recommendation.

---

## Impact labels

Use one per section, in the `Impact:` field:

```text
DECISIVE      changed my position or my stated reason for it
USEFUL        improved my understanding without moving my position
CONFIRMING    matched what I already believed, explicitly
NOISE         added structure without adding understanding
MISSING       the thing I needed from this section was not there
```

`NOISE` exists so that pre-registered falsification condition 4 has somewhere to show up while the
session is running, rather than being reconstructed afterwards. Use it.

---

## Useful outcomes

Fixed in advance. A run in which the position does not move is **not** a failed run.

* no strategy change, but a substantially better rationale;
* **lower** confidence, because hidden uncertainty became visible;
* a **smaller** initial commitment, because you decide to buy evidence before buying scale;
* a sharper evidence gate — same money, released against a named falsifiable demonstration rather
  than a date;
* identifying that the binding constraint is not toolchain fragmentation at all;
* identifying that adoption, not capability, is what the investment has to buy.

---
---

# T0 — human prior

**Complete this BEFORE consuming any Kriterion analysis.** Do not open the generated decision page,
the run artifacts, or the computed economics before this section is finished.

Reading `cases/northstar-internal-developer-platform/case.toml` for the scenario facts is expected
and necessary — you cannot hold a position on a case you have not read. Reading Kriterion's
*analysis* of it is what T0 precedes.

## Strategy

**My preferred strategy today:**



**If it is a combination, what exactly is combined:**



**Why:**



## Investment

**Capital / operating commitment:**

**Duration:**

**Stage (what is being funded right now, not the eventual total):**

**Team / capacity:**

**Scope — which engineers, which workloads:**



## Evidence gate

**What must be demonstrated before the next stage receives funding?**

(Be specific enough that someone else could tell whether it had happened. "Adoption is good" is not
an evidence gate; "sustained voluntary weekly usage above 60% of onboarded teams for two
consecutive months" is.)



**Who would produce that evidence, and by when:**



## Confidence

**Confidence:** ___ / 100

**What that number means here:**



## My three strongest reasons

1.
2.
3.

## My three biggest uncertainties

1.
2.
3.

## What would make me invest more?



## What would make me invest less?



## Evidence required before I would scale further



## T0 summary, in my own words



**The question I most need Kriterion to challenge:**



---
---

# During the Kriterion session

Read `docs/human-run-001/decision-page.html`, sections 1–8, **with the section-1 redaction applied**.
Record impact as you go, not afterwards.

## 1. The decision

**Impact:**

**What, if anything, affected my thinking?**

**Did Kriterion frame the actual decision correctly?**

**Did it hold all three dimensions — strategy, investment, evidence gate — or collapse them?**

**Anything materially missing?**


## 2. What we know

**Impact:**

**Specific evidence that affected my judgment (give the `ev-` id):**

**Did the `REAL` / `AUTHORED` attestation distinction change how I weighted anything?**

**Anything I thought was stronger or weaker than Kriterion represented it?**


## 3. What we are assuming

**Impact:**

**Assumption that mattered most (give the `as-` id):**

**Was this already explicit in my own reasoning?**

**Did its importance change after seeing Kriterion?**


## 4. What we do not know

**Impact:**

**Most important unknown surfaced (give the `ev-` id):**

**Had I explicitly recognised this before the session?**

**Does this unknown prevent a larger commitment?**


## 5. The economics

**Impact:**

**What changed, if anything, in my understanding of the economics?**

**Most decision-sensitive assumption, per the tornado:**

**The NPV sign flips inside the case's own declared ranges. Did that change how I read the result,
or did I anchor on one end of it?**

**Staging moves NPV less than any other parameter in the tornado. Does that change what I think
staging is for?**

**Did this change how much capital I would put at risk now?**


## 6. Machine-checkable evidence about the capability itself

**Impact:**

**Did anything here change my confidence in the analysis, as distinct from the decision?**


## 7. Where the perspectives agree and disagree

**Impact:**

**Challenge that most affected me, and which seat made it:**

**Why?**

**Was it already part of my reasoning?**

**Did the five seats produce genuinely distinct evidence needs, or did they converge?**

(This is a pre-registered observation, not an idle question. Charter coupling is a standing product
finding — see `case-design.md`. Record what actually happened.)

**Two perspectives have no seat: engineering leader and developer / platform consumer. Did their
absence show?**

**Any challenge that was generic or added noise?**


## 8. What would change this decision

**Impact:**

**Kriterion EvidenceRequest that mattered most:**

**Did Kriterion identify evidence I had not independently identified?**

**Any EvidenceRequest too vague to be actionable — no threshold, no owner, no falsifiable outcome?**


---
---

# T1 — after the analysis, before the recommendation

> **STOP. Do not read section 9, and do not open `recommendation.json`.**
>
> If you have already seen the synthetic recommendation, this run produces no usable T1. Record
> that fact here and report it. Do not reconstruct what you "would have" said.

## Strategy

**My preferred strategy now:**

**Why:**

## Investment

**Capital / operating commitment:**

**Duration:**

**Stage:**

**Team / capacity:**

**Scope:**

## Evidence gate

**What must be demonstrated before the next stage receives funding?**

**Who produces it, by when:**

## Confidence

**Confidence:** ___ / 100

## What specifically moved between T0 and T1?

**Dimension that moved (strategy / investment / evidence gate / confidence / none):**

**What moved:**

**The specific item that moved it:**

(Name the evidence id, assumption id, unknown, tornado entry, seat or EvidenceRequest. **"The
analysis" is not an answer** — pre-registered falsification condition 2 is exactly the case where
no specific item can be named.)

**If nothing moved, record that here. A null result is a result:**


---
---

# 9. Synthetic recommendation

Read it now. Reveal the four withheld section-1 lines at the same time.

**Kriterion recommendation:**

**Stated confidence:**

**Immediate reaction, before thinking about it:**

**Impact:**


---
---

# T2 — immediately after the recommendation

**Record this before rereading or editing any earlier answer.** The value of T2 depends entirely on
it being recorded before you reconcile it with what you wrote at T0 and T1.

## Strategy

**My preferred strategy now:**

## Investment

**Capital / operating commitment:**

**Duration:**

**Stage:**

**Team / capacity:**

**Scope:**

## Evidence gate

**What must be demonstrated before the next stage receives funding?**

## Confidence

**Confidence:** ___ / 100

## Did the recommendation change the decision?

**Which dimension(s):**

## What evidence from sections 1–8 justified that change?

(Name specific items.)



**If no specific evidence from sections 1–8 can be named, flag possible recommendation anchoring
here explicitly. That is pre-registered falsification condition 3 firing, and it is reported as
having fired, not explained away:**



---

## Position trajectory

Fill in after T2, from what you already wrote above. **Do not re-decide anything here.**

| | Strategy | Investment | Evidence gate | Confidence |
|---|---|---|---|---|
| T0 | | | | |
| T1 | | | | |
| T2 | | | | |

**Reading this trajectory:** if T0 and T1 differ but T1 and T2 do not (beyond a confidence shift),
the analysis moved the decision independently of the recommendation — the outcome the product
hypothesis predicts. If T0 and T1 are the same and T1 and T2 differ, recommendation anchoring is a
serious alternative explanation and must be reported as one.

---
---

# Human decision

Record with `kriterion decide`, which writes `human_decision.json` separately from
`recommendation.json` and never touches the latter (ADR-006).

**Action (one of the ten decision-vocabulary values):**

**Disposition (accept / modify / reject):**

**Strategy:**

**Investment:**

**Evidence gate:**

**Rationale:**

**Owner:**

**Overrides — what I explicitly rejected from the recommendation, and why:**


---

# Outcome contract

Only if the decision is a funding action. Record with `kriterion contract`.

**Baseline date:**

**Review date:**

**Next decision:**

**Measures (name : baseline : target : source):**

**Kill criteria:**


---

# Retrospective

**Did Kriterion improve this decision? In what specific way?**

**What did it fail to do?**

**Product observations — anything the instrument did that it should not have, or did not do that it
should have:**

| Observation | Section | Severity | Existing finding, or new? |
|---|---|---|---|
| | | | |

**Did the section-1 redaction hold?**

**Did any standing product finding recur (charter coupling, contradiction-edge handling, Narrative
Integrity versus upstream correctness, CaseRealism vocabulary)?**


---

# Falsification check

Answer each against what is written above, not against how the session felt. If a condition fired,
it is reported as having fired.

| # | Condition | Fired? | Evidence |
|---|---|---|---|
| 1 | The final rationale merely copies the synthetic recommendation | | |
| 2 | I cannot identify a specific Kriterion input that affected my reasoning | | |
| 3 | The recommendation changed T1 → T2 without an evidence-based justification | | |
| 4 | The process generated more structure without materially improving understanding | | |
| 5 | The investment became more elaborate but not more decidable | | |

**Overall verdict:**
