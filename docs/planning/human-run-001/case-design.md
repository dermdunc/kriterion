# Kriterion Human Run 001 — Case Design

Public, methodology-only. The case pack's actual content, its decision-rights entries, its
distribution entries and its economics live in `kriterion-private/human-run-001/`, which is not a
git repository. This file describes *how* the case was built and where its epistemic boundaries sit,
not what it says.

Case id: `global-platform-engineering`.

---

## Decision

> What global platform-engineering operating model should we invest in for the next 12-18 months so
> that distributed engineering teams gain sufficient autonomy and responsiveness without duplicating
> enterprise platforms or fragmenting global standards?

---

## What this replaced, and why the case id changed

A narrower first preparation of this case was built, run and frozen before a materially fuller final
specification arrived. That preparation framed the question as a binary between a headquarters-owned
centre and one region, across three operating-model archetypes, with a seven-row decision-rights
matrix. The final specification frames four peer regions across four operating models, adds a
distributed-enterprise model in which enterprise-owned platforms are engineered from several regions
at once, adds an explicit physical-distribution question, and carries a thirteen-row decision-rights
matrix.

Two consequences worth stating in public, because both are methodology rather than content.

**The frozen artifacts were archived, not overwritten.** No participant response had been recorded
against them — every response file was verified still to contain only its "not yet recorded"
placeholder, and the run directory contained no `human_decision.json` — so nothing was lost. They
were nonetheless moved intact, with their hashes re-verified after the move, rather than deleted or
edited in place. Kriterion's own governance rule is that a canonical decision record is never
mutated; a preparation that rewrote its own frozen run while leaving a manifest describing something
that no longer existed would be a project applying a standard to its users that it does not apply to
itself.

**The case was renamed.** "International" is a headquarters-relative term: it only means something
if there is a centre that everything else is international *to*. The new framing has four peer
regions and a model in which enterprise platforms are engineered from all of them, so a case id that
presupposes a centre contradicts the case's own first section. The rename touched two registry
entries in this repository's source, one test module, and every document that names the id. The
evidence id space was moved as well, so that no evidence reference the participant records during
this run can be silently matched against the archived one.

---

## Why this case

**Real.** The question belongs to a real organisation and a real accountable human. It is not a
scenario written to exercise Kriterion.

**Unresolved.** No decision has been taken. The participant holds a research-informed leaning, and
the research itself explicitly declines to settle several of the load-bearing questions for want of
internal evidence.

**Consequential.** It determines funded capability, where engineering capability physically sits,
reporting lines, delegated authority over production control planes, and whether regional divergence
gets encouraged or prevented. It is plausibly irreversible on a 12-18 month horizon: organisations
are harder to unwind than pilots.

**Suitable for Kriterion.** It has genuine external evidence, genuine assumptions, genuinely
unmeasured quantities, and informed parties who would disagree for good reasons. That combination is
what Kriterion claims to instrument. It also stresses Kriterion in a way the fixtures cannot: it has
**no measured internal baseline at all**, which the fixtures always had.

---

## The three decision dimensions

The decision is one question spanning three dimensions, and they are separable. Each is recorded
independently at T0, T1 and T2, so that a run can move one while the others hold.

**1. Operating model.** Which of four models to fund and test next: central platform engineering
(the status quo); distributed enterprise platform engineering (enterprise-owned platforms,
engineering capacity deliberately spread across regions on the same products and backlogs);
federated platform engineering (enterprise retains ownership, regions receive explicit capability
and decision rights); or greater regional platform autonomy. These map onto
`DecisionCase.alternatives`, with `do_nothing` carrying the central model.

Two notes recorded rather than worked around. The central model is not strictly "do nothing" — it
permits regional support to be improved while the organisational model stays centralised, and
Kriterion's required `do_nothing` label understates that. And regional autonomy is held as a genuine
alternative rather than a strawman: it carries both supporting and constraining evidence on the same
terms as every other model, and no item in the pack asserts that it is wrong.

**2. Decision rights.** Thirteen capabilities, each allocated to enterprise, region, joint or
undecided. These allocations are **part of the decision**, not inputs to it, and the case does not
assert them. Kriterion has no native representation for a decision-rights allocation, so this
dimension lives as a case-design artifact alongside the pack, privately, blank. Whether to add a
product-domain model was re-examined when the matrix nearly doubled in size; the answer held. A
thirteen-row allocation is still a decision output, and the product would gain a schema it cannot
validate, cannot economically model and cannot narratively bind.

**2a. Distribution.** A sub-artifact of the same kind, and new. The instrument asks where
platform-engineering capability should physically exist across four regions, *and separately* what
engineers in each region would own. Those are kept apart deliberately: the four operating models are
not distinguished by geography alone, and a position that moves on *where* without moving on *what
those engineers may decide* is the configuration the external evidence names as a failure mode
rather than a change.

**3. Investment.** What capability to fund now, where, at what capacity, for how long, and what it
is allowed to do — with the decision explicitly asked to identify the *smallest* useful commitment
capable of producing the evidence the next decision needs. This dimension reuses Kriterion's existing
`DecisionAction` vocabulary unchanged. No parallel stage system was created.

Kriterion natively represents dimension 3 and, through `alternatives`, the *names* of dimension 1.
It represents neither dimension 2 nor the distribution question. That asymmetry is recorded as a
finding rather than patched, and it is worse under this specification than the previous one: the
four models differ chiefly in the authority they allocate, which is exactly what a bare `list[str]`
of alternative names cannot carry.

---

## Evidence boundaries

The case preserves epistemic status using Kriterion's existing taxonomy
(`MEASURED` / `EXTERNAL_REFERENCE` / `EXPERT_JUDGMENT` / `FORECAST` / `ASSUMPTION` / `INFERENCE` /
`UNKNOWN`), and the boundaries fell as follows.

**Externally sourced.** The external evidence comes from a single real document: a deep-research
whitepaper on international platform engineering in the agentic enterprise, which the participant
published publicly under their own identity before this experiment existed. It cites named public
sources (CNCF, AWS, Microsoft, Google Cloud, ING, Uber, JPMorgan Chase, Goldman Sachs, LinkedIn,
PayPal, Capital One, Spotify, Netflix, Shopify, Meta, Palantir, InnerSource Commons, Team Topologies,
DORA). These items are classified `EXTERNAL_REFERENCE` and carry `attestation = "REAL"` — the first
use in Kriterion of the `Attestation.REAL` value that ADR-003 reserved and V0 never used.

A **provenance ceiling** is now recorded alongside them, which the first preparation did not record
and should have: that whitepaper attributes every claim to a named organisation in prose but
contains no URLs, footnotes or bibliography. It is a second-order source, and no item can be traced
to a primary document from the pack alone. Several items were downgraded in strength on that basis —
specifically those resting on a single organisation's self-report or carrying the whitepaper's own
evidentiary caveat.

**Organisation-specific.** Effectively none, and this is still the single most important fact about
the case. **The case contains zero `MEASURED` items.** A fuller specification of the *decision* did
not manufacture observations of the *organisation*.

The specification names six current-state observation categories to look for. Each was checked
against the external source before being classified, rather than assumed unavailable, and none is
supported by it. The one worth naming is **timezone coverage**, because it is the category that most
looks like a general industry fact a research source could supply. It cannot: the whitepaper's
timezone reasoning is self-labelled as an inference rather than a measured benchmark, its
follow-the-sun references are prescriptive cells in its own design matrix rather than findings about
any organisation, no named source is attached to any timezone claim in it, and it lists the
corresponding question among its *own* open questions requiring internal evidence. It is an
`UNKNOWN`, and the item's claim text records that the check was performed and what it found, so a
later reader cannot mistake the classification for an oversight.

For contrast: Kriterion's canonical fixture opens with seven `MEASURED` telemetry items. The real
case opens with none. Whether an evidence-first instrument remains useful in that condition is itself
a Human Run 001 finding, and arguably a more interesting one than the participant's position shift.

**Assumed.** The six substantive decision assumptions the specification itself names, plus two
explicitly labelled illustrative sizing assumptions. All are `LOW` evidence strength. **Two** are
recorded as *contradicted* by the external evidence base, where the first preparation had one,
because the research names the corresponding failure mode of each proposal directly. Kriterion's
`contradicts` field carries those tensions structurally rather than leaving them in prose — a choice
that paid off measurably in the first run, when every seat independently named the contradicted
assumption as its distrusted one.

One of the six deserves naming as a category: the assumption that central platform teams are
currently a material source of delivery delay. That is the premise the entire decision rests on, it
carries `LOW` strength, and nothing in the case evidences it. If it is false, all four models answer
a question the organisation does not have.

**Unknown.** Eighteen `UNKNOWN` items, up from eleven, covering the quantities the decision would
need and does not have: dependency-attributable delay and its cost; demand commonality across
regions; enterprise capacity consumed by regional support; upstream contribution acceptance rate;
optimal team size and optimal distribution; which control-plane actions are delegable in fact versus
in principle; the economics of distributed versus central engineering; four current-state categories;
whether the binding constraint is capacity, decision rights or prioritisation; whether platform
owners would consent to delegated operation at all; whether agentic execution changes the sizing in
either direction; which platforms cause the most delay; and the appropriate authority boundary.

The increase is not padding. The specification names nine unknowns explicitly, adds six current-state
categories, and requires unpriced amounts to be preserved as unknowns rather than estimated.

**Seeded, not authored.** The specification offers seven candidate evidence-request areas. They are
**not** written into the pack as `EvidenceRequest` objects — those are committee output, and
authoring them would pre-empt the thing the run measures. Each is present in the ledger as the
corresponding `UNKNOWN`, so the committee can surface it or fail to. Whether it does is a
measurement, not a design goal.

**Sanitised.** The whitepaper's own analytical judgements are classified `EXPERT_JUDGMENT` and
attributed to "the research author" rather than to a named individual or employer. No organisation,
team, system, individual or internal document is named anywhere in the pack. The pack itself is not
in a git repository. The public artifacts in this directory name the decision *topic*, which is
already public in the participant's own published research, and nothing more specific.

---

## The Model B question, as a design problem

The specification's distributed-enterprise model states that the change is geography, not platform
ownership. The case had to represent that faithfully without either endorsing or refuting it, and the
way it does so is worth recording as methodology.

The geographic evidence base supports non-headquarters sites *owning globally consumed components*.
It does not demonstrate capacity distributed across regions under unchanged ownership and
prioritisation — and the same evidence base names that exact configuration as a failure mode, twice.
Both halves are in the ledger as separate items, and a distinct `INFERENCE` item states the tension
explicitly: the model is supported as a *location* pattern and constrained on *authority*, so its
benefit case rests on an authority change the model does not itself specify.

That item deliberately stops short of concluding the model is wrong. Whether the organisation wants
to make that authority change is a live question the human answers in the decision-rights matrix,
which is precisely why that matrix is an independent dimension rather than something derived from the
model label.

---

## Economic limitations

This is where the case pushed hardest on the product, and the result is worth stating without
softening.

The specification's economic frame asks for three quantities: the cost of new capability, the cost
of the current model, and the risk of decentralisation. Kriterion could honestly represent **the
first, and nothing else.**

The cost-only choice was **re-checked against the external source rather than inherited** from the
first preparation. Every figure in that source was examined for whether it could legitimately price
any benefit-side driver. None can: each is another organisation's outcome under unstated baseline
conditions — a numerator without a denominator, or a denominator without a numerator. All the
quantified ones are outcomes of platform-product and automation investments, while the source's own
*geographic* evidence is precisely the part it marks as qualitative and non-quantitative. And the
source states twice in its own voice that external research cannot establish the magnitude of these
effects. Building an avoided-loss band from any of them would be a category substitution dressed as
prudence.

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
  absence. This pulls against the specification's own instruction to identify the *smallest* useful
  commitment: a required six-figure ask anchors upward, and the case cannot say "not yet sized".
- The sizing inputs were **held fixed** at the superseded pack's values rather than re-guessed for
  the broader scope. There is no basis for any figure, so changing it would have added motion without
  information and made the two runs incomparable.

No ROI, NPV or payback figure was fabricated to make the engine produce a fuller answer. A reader of
the generated page should come away understanding that the money side of this decision is one-sided,
not that the decision is uneconomic.

---

## Experiment risks

Recorded in advance, none of them eliminated.

**Synthetic recommendation anchoring.** The participant may adopt the recommendation and then
retrofit a rationale from sections 1-7. The T1 checkpoint is the mitigation and it is procedural
only: the recommendation is present in the frozen artifacts and on the generated page from the
start, so nothing technically prevents reading ahead. Pre-registered falsification condition 3 exists
because the mitigation is imperfect.

**Incomplete evidence.** With zero `MEASURED` items, the case may be too thin to move a well-informed
judgment in any direction, which would make a null result uninformative about Kriterion rather than
informative. The compensating value is that the evidence gaps are *themselves* the decision-relevant
content here.

**Weak EvidenceRequests.** `EvidenceRequest`s are produced by the committee during the run, not
authored into the case, so their quality is not under the experimenter's control. Requests without a
threshold, an owner or a falsifiable outcome are to be recorded as weak, not silently upgraded into
falsifiable tests when the results are written up.

**Participant familiarity with the subject.** The participant is highly familiar with the
platform-engineering problem and authored the external research the case draws on. The case's
`EXPERT_JUDGMENT` items are therefore the participant's own prior judgements, fed back to them as
evidence — and there are now more of them than in the first preparation, so the circularity grew.
It biases toward `T0 ≈ T1`, i.e. against the product hypothesis, which makes a movement finding more
credible and a null finding less so.

**Participant familiarity with Kriterion.** The participant designed the instrument, knows what each
section is for, knows the hypothesis, and knows what the T1 checkpoint is testing. Demand
characteristics cannot be excluded.

**Self-dogfooding bias.** The same person is decision-maker, research author, product designer and
experimenter. There is no independent observer. This is the dominant limitation of Human Run 001 and
the reason a later run should use a participant with no involvement in the product.

**Instrument revision before T0.** New to this preparation and worth recording: the case, the
instrument and the protocol were all rebuilt after a first version had been frozen. That happened
before any response was recorded, and the superseded version was archived rather than edited, so
the pre-registration holds. But a specification that can be replaced once can be replaced again, and
the guard against that is procedural: nothing in this directory is revised after T0.

None of these are worked around. Human Run 001 establishes whether the instrument does anything at
all on a real decision. A generalisability study is a different experiment.

---

## Product fit

The case ran through Kriterion's existing pipeline with one generic, case-agnostic addition made
during the first preparation and unchanged here, plus a mechanical case-id rename, and several
limitations that were recorded rather than fixed. The detail, the verdict and the justification for
each choice are in `opus-preparation-report.md`.
