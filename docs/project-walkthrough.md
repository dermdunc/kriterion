# Kriterion — Plain-English Project Walkthrough

*Last substantially updated 2026-09-11 (V1 decision-instrument increment).*

## What this project is in one paragraph

Kriterion is an instrument for making a consequential technology investment decision with the
uncertainty left visible. You give it a proposal — say, "should we spend £4.2m rolling an AI
coding agent out to 5,000 engineers?" — and instead of returning a score or a
recommendation-shaped answer, it separates what is actually *measured* from what is
*assumed* from what is genuinely *unknown*, computes the economics deterministically so you
can see which assumption the whole business case is resting on, runs the case past several
independent role-chartered AI perspectives and records how and why their positions changed,
and produces a recommendation that is explicitly **not** the decision. A human makes the
decision, separately and on the record, and if they commit money they must also commit to an
outcome contract saying what they expect and when they will check.

## The simple analogy

A blood panel, not a diagnosis. The instrument's job is to produce readings you can act on
and to be honest about which readings it could not take. A panel that quietly prints
"probably fine" for a test that failed to run is worse than useless, so most of the
engineering here is about refusing to do that: unknown must stay distinct from passing, and
both must stay distinct from crashed.

## What problem we are solving

Big technology investment decisions usually fail in one of two ways. Either the analysis is
a spreadsheet whose most load-bearing number is an unexamined guess, or it is a deck whose
confident narrative has laundered away every caveat that would have changed the answer. Both
failures share a mechanism: **the uncertainty gets compressed out on the way to the
decision-maker.** Kriterion's bet is that the compression is the problem, and that an
instrument which structurally refuses to compress — keeping seven distinct epistemic
categories rather than one confidence score, naming unknowns as first-class items, showing
which assumption the NPV actually swings on, preserving dissent verbatim — produces better
human judgment. That bet is not yet proven (see *Current confidence level*).

## What we have built so far

- **Scaffolded** 2026-09-05 — repo and vault control plane created.
- **V0 (research)** — the full domain model (evidence ledger, assumptions, economics,
  committee positions, belief updates, recommendation, human decision, outcome contract),
  a deterministic economics engine, a five-seat AI committee protocol with an anonymised
  challenge round, and a pre-registered experiment testing whether the committee actually
  beats a single strong AI context given the identical protocol. **It did not**, on the
  pre-registered check, on these cases. That honest-negative result is published rather than
  buried, and it is why the committee is now treated as *one optional challenge mechanism*
  rather than as the product.
- **V1 (instrument)** 2026-09-11 — the public site leads with a decision journey rather than
  the experiment (the V0 research page is preserved intact as *Kriterion Lab*); Kriterion can
  import **assurance evidence** about an AI capability from a generic document contract and
  fold it into a frozen ledger version; per-seat "what would change this position" records
  are persisted per run. Built Fable-stage, critiqued adversarially (verdict RED), and
  repaired — see `docs/session-log.md` and
  `docs/planning/kriterion-v1-decision-instrument/`.

## How the pieces fit together

```
case pack (case.toml)
   ├─> evidence items ──freeze()──> ledger.frozen.json  (fingerprinted, never edited;
   └─> assumptions                                       new evidence makes vN+1)
          └─> deterministic economics  (pure Python, no model call, ever)
                 └─> committee protocol (5 independent contexts -> challenge -> revision)
                        └─> synthetic recommendation ──NEVER MERGED WITH──> human decision
                                                                                └─> outcome contract

assurance envelope + decision documents
   └─> anti-corruption adapter ──> EvidenceItems ──> the same freeze() path above
```

Two rules hold that diagram together. **`freeze()` is the only way evidence enters the
record**, so imported assurance evidence gets no privileged side door. And **the
recommendation and the human decision are separate types in separate files**, so no amount of
rendering can quietly turn the machine's output into somebody's accountable act.

## What is deliberately not automated yet

- **The human decision.** An agent must never record one on a human's behalf. The demo run
  renders "not yet recorded" and leaves it there.
- **The public journey page.** `docs/index.html` is hand-maintained narrative, not a rendered
  artifact. The *generated* artifact is the per-run report. Rather than claim otherwise,
  `tests/product/test_public_page_coherence.py` mechanically checks every figure, outcome and
  position on the page against the committed artifact it came from, and bans a list of
  retired overclaims outright.
- **Assurance production.** Kriterion consumes a document shape. It never runs evals, never
  imports an assurance package, and works identically with no assurance evidence at all.
- **Structural economic assumptions.** Headcount timing, the discount rate and the stage
  amounts are named constants, not ranged `Assumption` records, and therefore not in the
  sensitivity analysis. The page says so explicitly rather than letting "deterministic" imply
  "complete".

## How this could connect to the wider Hekton factory

Hekton Assurance is the reference *producer* of the assurance document shape Kriterion
consumes. The two projects are deliberately coupled only at the document level: neither
imports the other, no investment or committee concept appears in Assurance, and no assurance
concept escapes `src/kriterion/assurance/` on the Kriterion side. That boundary is the
interesting part — it is a test of whether an evidence producer and an evidence consumer can
be built independently and still meet usefully in the middle.

## Current confidence level

**Medium on the mechanism, low on the thesis.** The instrument's epistemic guarantees are
real and tested: 239 tests, including the ones added after an adversarial review found three
of them broken in practice. But the central claim — that making evidence, assumptions and
uncertainty explicit produces *better human judgment*, not merely better-organised analysis
— has no evidence behind it yet, because no human has used it on a decision whose outcome
they then lived with. The V0 experiment also failed to show the multi-context committee
beating a single strong context, which is a real result and is treated as one.

## Open questions

- Does the instrument change a real decision-maker's behaviour, or only the artefact quality?
- What is the minimum lifecycle evidence — human decision, outcome contract, observed outcome
  at review date — needed before the journey can honestly be called complete?
- Is the assurance document contract stable enough to consume a *real* producer artifact,
  rather than the hand-authored facsimile currently committed?

## A finding worth keeping: the last metre

Kriterion exists to reveal when a decision narrative overstates its evidence. Building it
produced a clean example of the same failure, inside Kriterion itself.

An adversarial review of the V1 increment found four defects in the public decision page. An
assurance result whose source document said `fail` was displayed as the word "PARTIAL" —
fourteen lines above a claim that the adapter guarantees failures cannot be softened in
translation. A producer's `REVIEW_REQUIRED` was attributed to "three named coverage gaps" that
its decision document does not contain and its decision model never reads. A hand-authored
fixture was described as independently measuring resilience, when no assurance run had
happened. And the cost of buying better evidence was quoted as two different ranges in two
places on the same page.

The striking part is what was *not* wrong. The economics were computed correctly by pure code
throughout. The evidence ledger kept its seven epistemic categories distinct. The adapter
mapped a `fail` to a FAIL. Every artifact was right. The sentences describing the artifacts
were wrong, and nothing tested the prose against the record, so they shipped.

> **In AI-assisted decisions, the dangerous error may not occur in the calculation. It may
> occur in the final metre between evidence and language.**

That is the reasoning behind treating narrative integrity as an invariant with deterministic
checks (ADR-012) rather than as careful writing or a better prompt. It is an engineering and
research finding about where to put the guardrail, not a marketing line, and it is recorded
here rather than repeated through the product.

Two honest qualifications. First, the guardrail proves a statement is *derived from* the
record and cannot be hand-edited without detection; it does not prove the derived sentence is
a *fair* summary. Judging fairness is still a human job. Second, the same failure class showed
up again while building the guardrail: an adversarial pass over the new projection code found
every malformed run artifact escaping as a bare traceback rather than a controlled refusal —
sixteen of sixteen cases — which is the same defect the review had already found once in the
assurance adapter. Knowing about a failure mode is not the same as being immune to it, which
is the argument for mechanical checks over vigilance.

## Next recommended session

Close the loop on a human: record one real `kriterion decide` on a fresh run (even at fixture
scale), attach its outcome contract, and render the journey's decision-record section from
those artifacts instead of from "not yet recorded". That is the one thing no agent can do and
the one thing the product thesis most needs.
