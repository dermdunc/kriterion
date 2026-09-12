# Kriterion Human Run 001 — Case Design

Public, methodology-only. The case pack's actual content, its decision-rights entries and its
economics live in `kriterion-private/human-run-001/`, which is not a git repository. This file
describes *how* the case was built and where its epistemic boundaries sit, not what it says.

Case id: `international-platform-engineering`.

---

## Decision

> What International platform-engineering operating model should be funded for the next 12-18
> months, and what responsibilities, decision rights and enterprise control-plane access should
> International own versus consume from global platform teams?

---

## Why this case

**Real.** The question belongs to a real organisation and a real accountable human. It is not a
scenario written to exercise Kriterion.

**Unresolved.** No decision has been taken. The participant holds a research-informed leaning, and
the research itself explicitly declines to settle several of the load-bearing questions for want of
internal evidence.

**Consequential.** It determines funded capability, reporting lines, delegated authority over
production control planes, and whether regional divergence gets encouraged or prevented. It is
plausibly irreversible on a 12-18 month horizon: organisations are harder to unwind than pilots.

**Suitable for Kriterion.** It has genuine external evidence, genuine assumptions, genuinely
unmeasured quantities, and informed parties who would disagree for good reasons. That combination
is what Kriterion claims to instrument. It also stresses Kriterion in a way the fixtures cannot:
it has **no measured internal baseline at all**, which the fixtures always had.

---

## The three decision dimensions

The decision is one question spanning three dimensions, and they are separable:

**1. Operating model.** Which of four archetypes to move toward: enterprise-led (status quo),
international enablement (coordination, little execution authority), federated hybrid (enterprise
owns platforms, International receives delegated authority and contribution rights), or regional
autonomy (International owns regional platform capability). These are mapped onto
`DecisionCase.alternatives`, with `do_nothing` carrying its real meaning here: the status quo *is*
enterprise-led, so the required `do_nothing` alternative is a substantive option rather than a
placeholder.

**2. Decision rights.** Which responsibilities sit with Enterprise, with International, or jointly,
across capabilities such as core platform architecture, global standards, International demand
prioritisation, regional configuration, control-plane access, upstream contribution and regional
exceptions. These allocations are **part of the decision**, not inputs to it, and the case does not
assert them as facts. Kriterion has no native representation for a decision-rights allocation, so
this dimension lives as a case-design artifact alongside the pack, privately. No product-domain
model was added for it; see "Product fit" below.

**3. Investment.** What dedicated capability to fund now, and what evidence would justify more
autonomy or a larger capability later. This dimension reuses Kriterion's existing `DecisionAction`
vocabulary unchanged (`REQUEST_EVIDENCE`, `DISCOVERY`, `FUND_EXPERIMENT`, `PILOT`, `SCALE`, `HOLD`,
`REDUCE`, `STOP`, `DEFER`, `REJECT`). No parallel stage system was created.

Kriterion natively represents dimension 3 and, through `alternatives`, dimension 1. Dimension 2 it
does not represent. That asymmetry is recorded as a finding rather than patched.

---

## Evidence boundaries

The case preserves epistemic status using Kriterion's existing taxonomy
(`MEASURED` / `EXTERNAL_REFERENCE` / `EXPERT_JUDGMENT` / `FORECAST` / `ASSUMPTION` / `INFERENCE` /
`UNKNOWN`), and the boundaries fell as follows.

**Externally sourced.** The external evidence comes from a single real document: a deep-research
whitepaper on international platform engineering in the agentic enterprise, which the participant
published publicly under their own identity before this experiment existed. It cites named public
sources (CNCF, AWS, Microsoft, Google Cloud, ING, Uber, JPMorgan Chase, Goldman Sachs, LinkedIn,
PayPal, Capital One, Spotify, Netflix, Shopify, Meta, Palantir, Atlassian, InnerSource Commons, Team
Topologies, DORA). These items are classified `EXTERNAL_REFERENCE` and carry
`attestation = "REAL"` — the first use in Kriterion of the `Attestation.REAL` value that ADR-003
reserved and V0 never used. Labelling real, citable research as `AUTHORED` would have understated
its provenance.

**Organisation-specific.** Effectively none, and this is the single most important fact about the
case. **The case contains zero `MEASURED` items.** No ticket-volume data, no lead-time or
waiting-time baseline, no cost data, no headcount or org-chart data was available to it. Every
place where a current-state observation would be required — current central-team dependency,
regional prioritisation friction, present International engineering capacity — is recorded as an
explicit `UNKNOWN`. None of it was estimated, inferred from plausibility, or promoted into a
stronger class to make the case look complete.

For contrast: Kriterion's canonical fixture opens with seven `MEASURED` telemetry items. The real
case opens with none. Whether an evidence-first instrument remains useful in that condition is
itself a Human Run 001 finding, and arguably a more interesting one than the participant's position
shift.

**Assumed.** Four substantive decision assumptions (regional demand commonality; that a dedicated
capability reduces drag rather than adding a queue; that upstream contribution prevents forks at the
local acceptance rate; that delegated authority materially reduces lead time), plus two explicitly
labelled illustrative sizing assumptions. All are `LOW` evidence strength. One of them is recorded
as *contradicted* by the external evidence base, because the research names the corresponding
failure mode directly; Kriterion's `contradicts` field carries that rather than prose burying it.

**Unknown.** Eleven `UNKNOWN` items, covering: delay attributable to platform dependencies; cost of
delay; proportion of common regional demand; upstream acceptance rate; which control-plane actions
are delegable in fact versus delegable in principle; whether the binding constraint is capacity,
decision rights or prioritisation; present International engineering capacity; appropriate authority
boundaries; whether agentic execution changes the sizing; which platforms cause the most delay; and
whether enterprise platform owners would consent to delegated operation at all.

**Sanitised.** The whitepaper's own analytical judgements are classified `EXPERT_JUDGMENT` and
attributed to "the research author" rather than to a named individual or employer. No organisation,
team, system, individual or internal document is named anywhere in the pack. The pack itself is not
in a git repository. The public artifacts in this directory name the decision *topic*, which is
already public in the participant's own published research, and nothing more specific.

---

## Economic limitations

This is where the case pushed hardest on the product, and the result is worth stating without
softening.

Kriterion could honestly represent **the cost side only**. The decision's economic drivers are
incremental capability cost on one side and, on the other, cost of delay, central-queue dependency,
duplicated regional effort, enterprise support demand, fork/divergence cost, initiatives unblocked,
reuse contributed upstream and time-to-market improvement. Every single benefit-side driver in that
list is an `UNKNOWN` in this case's ledger. None of them was given a number.

The consequences, all of them deliberate:

- The economics result is **negative in every scenario, by construction**, because only costs are
  summed. This is the same construction Kriterion's Case C fixture uses.
- **No benefit band is reported at all.** Case C at least has a risk-modelled avoided-loss band to
  report alongside (never inside) the NPV table. This case cannot honestly state even a band, so the
  result carries `None`, not `0`. Absence had to stay absence.
- The sensitivity analysis ranks **exactly one** assumption, because the cost of the capability is
  the only quantity the case can vary. A one-entry tornado is the honest output here, not a
  degenerate one.
- The ask amount is **illustrative sizing, explicitly labelled**, because `Ask.amount_gbp` is a
  required non-optional float. A case whose ask has genuinely not been sized cannot record that
  absence in Kriterion's current domain model. A labelled illustrative figure was preferred to a
  false zero, and the choice is itself recorded as a product observation.

No ROI, NPV or payback figure was fabricated to make the engine produce a fuller answer. A reader
of the generated page should come away understanding that the money side of this decision is
one-sided, not that the decision is uneconomic.

---

## Experiment risks

Recorded in advance, none of them eliminated.

**Synthetic recommendation anchoring.** The participant may adopt the recommendation and then
retrofit a rationale from sections 1-7. The T1 checkpoint is the mitigation and it is procedural
only: the recommendation is present in the frozen artifacts and on the generated page from the
start, so nothing technically prevents reading ahead. Pre-registered failure condition 2 exists
because the mitigation is imperfect.

**Incomplete evidence.** With zero `MEASURED` items, the case may be too thin to move a
well-informed judgment in any direction, which would make a null result uninformative about
Kriterion rather than informative. The compensating value is that the evidence gaps are *themselves*
the decision-relevant content here.

**Weak EvidenceRequests.** `EvidenceRequest`s are produced by the committee during the run, not
authored into the case, so their quality is not under the experimenter's control. Requests such as
"increase confidence in readiness" are weak: unfalsifiable, no threshold, no owner. They are to be
recorded as weak, not silently upgraded into falsifiable tests when the results are written up.

**Participant familiarity with the subject.** The participant is highly familiar with the
platform-engineering problem and authored the external research the case draws on. The case's
`EXPERT_JUDGMENT` items are therefore the participant's own prior judgements, fed back to them as
evidence. That circularity is real. It biases toward `T0 ≈ T1`, i.e. against the product
hypothesis, which makes a movement finding more credible and a null finding less so.

**Participant familiarity with Kriterion.** The participant designed the instrument, knows what
each section is for, knows the hypothesis, and knows what the T1 checkpoint is testing. Demand
characteristics cannot be excluded.

**Self-dogfooding bias.** The same person is decision-maker, research author, product designer and
experimenter. There is no independent observer. This is the dominant limitation of Human Run 001 and
the reason a later run should use a participant with no involvement in the product.

None of these are worked around. Human Run 001 establishes whether the instrument does anything at
all on a real decision. A generalisability study is a different experiment.

---

## Product fit

The case ran through Kriterion's existing pipeline with one generic, case-agnostic addition, and
three limitations that were recorded rather than fixed. The detail, the verdict and the
justification for each choice are in `opus-preparation-report.md`.
