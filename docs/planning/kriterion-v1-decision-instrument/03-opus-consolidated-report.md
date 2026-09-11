# Kriterion V1 (Decision Instrument) — consolidated loop report

**Loop:** Fable (implement) → Codex (adversarial critique, verdict **RED**) → Opus (resolve)
**Date:** 2026-09-11
**Status at handoff:** all work committed locally on the existing branches. **Nothing pushed,
no PR opened, nothing merged.**

| Repo | Worktree | Branch | Commits ahead of base |
|---|---|---|---|
| kriterion | `factory-output/kriterion--decision-instrument` | `agent/fable/kriterion-decision-instrument` | 10 from `origin/main` `fe1b85b` (3 Fable, 1 Codex-critique, 6 Opus). Local `main` is two merges stale, so `git log main..HEAD` reports 13 — compare against `fe1b85b`, not local `main`. |
| hekton-assurance-lab | `labs/hekton-assurance-lab--consumer-docs` | `agent/fable/assurance-consumer-contract-docs` | 2 (1 Fable, 1 Opus) — docs only, zero code |

**Tests: 239 passing** (193 pre-V1 baseline → 208 after Fable → 239 after Opus).

This file is the authoritative account of the loop. `01-fable-report.md` is the Fable-stage
record (now carrying an errata block and a reconstructed mission of record);
`02-codex-critique.md` is the critique verbatim and is left unedited.

---

## Codex critique resolution

Every claim below was re-verified against the real code before being acted on — in the three
cases Codex said it had executed, by executing them again.

### The seven blocking issues

| # | Issue | Disposition |
|---|---|---|
| 1 | Vertical slice stops before the system of record | **Accepted, split: half fixed, half explicitly relabelled.** The ledger path is now real — `assurance import --into-case` freezes imported items into a fingerprinted ledger vN+1 that flows through `econ` and `report`. The public page is *not* generated, and now says so; every "produced end-to-end" claim is gone. Reasoning below. |
| 2 | Public UI softens a source `fail` to "PARTIAL" | **Accepted and fixed.** Confirmed: `envelope.json` says `"outcome": "fail"`, the page said `PARTIAL`. The page now shows FAIL, qualified as non-gating, and a new coherence test binds every row to its source result. |
| 3 | PASS anti-laundering guarantee incomplete | **Accepted and fixed, and found to be worse than reported.** Re-executed Codex's case and reproduced the PASS-alongside-FAIL result exactly. Fixed all four routes: required/typed `criticalFailures`, gating-fail-under-PASS refusal (a fifth route Codex did not name), envelope↔decision identity binding, and stale-PASS downgrade. |
| 4 | Page fabricates how the decision was reached | **Accepted and fixed.** Confirmed `decision.json` carries two reasons, neither a coverage gap, and that the producer's decider never reads `fingerprint.uncovered`. Coverage gaps are now described separately, and the authored fixture is no longer called an independent measurement. |
| 5 | Load-bearing economic assumptions not all surfaced | **Accepted; claim narrowed rather than assumptions promoted — with a reason.** The dominance claim is now scoped to the five ranged assumptions, and the constants outside the tornado are named explicitly on the page. Promoting them properly would change `economics.json` output, and the committed V0 run artifacts are frozen research data; that needs a deliberate regeneration pass, not a side effect. Named in `next-actions.md`. |
| 6 | "What would change your mind" is copy, not a record | **Accepted and fixed forward; honestly labelled backward.** Codex's phrasing ("no `EvidenceRequest` is instantiated anywhere") is **partly wrong** — the type exists at `domain/committee.py:62` and phase 3 instantiates one per member. Its substance is right: they were discarded, never persisted. Runs now write `evidence_requests.json`. The committed V0 run predates that, so the page's list is labelled *derived* rather than stored. |
| 7 | Malformed JSON escapes the error boundary | **Accepted and fixed.** Re-executed both cases and got the uncaught `AttributeError` Codex reported. Every container and nested field shape is now validated into `AssuranceImportError`. |

### Report-accuracy and claim-discipline findings

| Finding | Disposition |
|---|---|
| "16 adapter tests", actually 15 | **Accepted and fixed** — corrected in both places, errata recorded. (208 = 193 + 15 was correct.) |
| Provenance claim doesn't match what the adapter copies | **Accepted and fixed** — claim corrected, *and* the gap closed: the adapter now reads the producer's `provenance`/`sourceState`, and `digestsCaptured: false` emits its own explicit UNKNOWN item. |
| Mission text missing from `01-fable-report.md` | **Accepted, partially fixable.** A "Mission of record" section was added, explicitly labelled a reconstruction. The verbatim brief was not preserved at Fable stage and cannot be recovered; saying so is the honest fix, not silently presenting a paraphrase as the original. |
| Evidence-buying cost quoted as both £50k–£420k and £50k–£470k | **Accepted and fixed** — £50k–£470k everywhere, with the arithmetic shown, and a test that bans the old figure. |
| Ladder called "case pack input" but is a `case.toml` comment | **Accepted and fixed** — described as a comment plus named constants in `case_flows.py`, which is what it is. |
| "Kriterion runs identically with manual and imported evidence only" | **Accepted and fixed** — replaced with the claim that is actually true and tested (no dependency, no import outside the adapter package, unchanged behaviour with no assurance documents). |
| Assurance ADR overclaims "real second-consumer data point" | **Accepted and fixed** in the Assurance repo. Verified: `evidence/` contains only YAML; Kriterion consumed a hand-authored JSON facsimile. Scoped to schema legibility, barred from counting as adoption evidence until a real artifact round-trips, falsifying test named. |
| Kriterion documentation contract FAIL | **Accepted and fixed** — `docs/session-log.md` created, `docs/project-walkthrough.md` filled in (it had been an empty scaffold since 2026-09-05), ADR-009/010 recorded, `next-actions.md` reconciled. |

### Rejected

| Claim | Why rejected |
|---|---|
| "No `EvidenceRequest` is instantiated or persisted anywhere" (issue 6) | **Half wrong.** `EvidenceRequest` is a real domain type with a `would_change` field, instantiated per member in phase 3 (`protocol/parsing.py` → `phases.py`). Only *persistence* was missing. Acted on the true half. |
| "Arbitrary unrecognised outcomes on recognised methods become MEASURED rather than UNKNOWN" (section 5 caveat) | **Not a defect, deliberately.** A recognised method with an unrecognised outcome yields `"Assurance deterministic check 'x': WEIRDVALUE."` — it reports the producer's own word without interpreting it. Mapping it to UNKNOWN would *lose* information; mapping it to a verdict would invent one. The epistemic class describes how the evidence was produced (the method), which is known. Left as is. |
| "Do not expand the adapter into a generic schema framework" (section 6) | **Agreed, and followed** — no schema framework was added. Recorded here only because the fix direction (strict validation) could be misread as the thing Codex warned against. Validation is hand-written against the actual 0.x contract, roughly 60 lines, no registry or DSL. |

---

## What you found

**Kriterion, before modification, was much closer to a decision instrument than its own framing
suggested.** The complete V1 domain vocabulary already existed as tested dataclasses — seven
epistemic categories with orthogonal attestation, ranged assumptions with owners, an NPV/tornado
economics engine that never calls a model, committee positions, belief updates, a synthetic
recommendation with mandatory non-empty dissent, a `HumanDecision` deliberately kept in a
separate type *and a separate file*, and an `OutcomeContract` whose absence fails validation for
any funding action. The ten-state staged vocabulary with APPROVE deliberately absent was already
there. What was missing was not the model; it was that the public face of the project was the
research experiment, and that nothing connected external assurance evidence to any of it.

It also carried an honest-negative result it had not buried: the pre-registered V0 check found
the five-seat committee did *not* beat a single strong context on evidence discipline. That
result is why the committee is correctly treated as one optional mechanism rather than the
product.

**Hekton Assurance, before modification, needed nothing.** Its envelope + decision documents are
already domain-independent — no investment, committee, stage or allocation concept appears
anywhere in them — and already carry everything Kriterion's evidence model needs: per-spec
method/outcome/detail, a critical-failure list, freshness, coverage gaps and real provenance
with model digests. It had a real committed FAIL against a real non-self-built target, not
rerun to make it go away.

**What the Fable stage then built was directionally right and materially over-claimed.** The
adapter and its guarantees were real and tested; the page describing them was hand-written and
wrong about them in four specific ways. Every defect of substance in this loop lived in the gap
between a hand-authored narrative and the artifacts it claimed to describe.

## Architecture decision

**Kriterion only, for all code. Hekton Assurance docs-only, and even then only to record a fact
about a consumer, never an obligation.**

The reasoning: the thing Kriterion needs from Assurance is a *document shape*, and that shape
already exists and is already domain-independent. Any Kriterion-shaped change to Assurance — a
"consumer" module, an investment-aware field, a stability contract — would import Kriterion's
domain into a repo that has stayed clean of it, in exchange for nothing Kriterion could not get
by reading JSON. So the coupling is one-directional and document-level, mediated by an
anti-corruption adapter that lives entirely inside `src/kriterion/assurance/`.

This was verified, not asserted: a test greps every Kriterion module and fails if anything
outside that package (bar the CLI's lazy, command-local import) imports it, and
`importlib.util.find_spec("hekton_assurance")` returns `None` in the test environment — the
producer package is not merely unused, it is not installed.

The one producer-side implication worth recording is that the consumer keys its
refuse-don't-guess behaviour on `envelopeVersion`, so a shape-breaking change should bump it.
That is a note in Assurance's next-actions, not a promise Assurance has made.

## What changed

### Kriterion (`agent/fable/kriterion-decision-instrument`)

**Fable stage (3 commits):**
- `src/kriterion/assurance/` — the ADR-007 adapter: document pair → `EvidenceItem`s, with the
  epistemic mapping made explicit rather than collapsed into a score (deterministic →
  MEASURED/HIGH, counterfactual → MEASURED/MEDIUM, model-judge → EXPERT_JUDGMENT/LOW,
  error/indeterminate/unrecognised → UNKNOWN/LOW, coverage gaps → UNKNOWN items, the decision
  itself → INFERENCE).
- `kriterion assurance import` CLI; authored fixture pair + README under
  `cases/coding-agent-rollout/assurance/`, labelled as a fixture inside the JSON itself.
- `docs/index.html` rebuilt as a decision journey; the V0 research page preserved
  verbatim-in-substance as `docs/lab.html` with every caveat and the honest-negative headline
  intact; README/architecture repositioned; ADR-007 and ADR-008.

**Opus stage (6 commits — the four below, plus this report and a commit-count correction):**
- `fix(assurance)` — closed four PASS-laundering routes and the uncaught-error boundary.
  Required/typed `criticalFailures`; gating-fail-under-PASS refusal; envelope↔decision identity
  binding on `capabilityRef` name and version plus `envelopeRef`; staleness downgrades a
  declared PASS to STALE with the declared state preserved separately; full container/field
  shape validation, every failure an `AssuranceImportError`; duplicate derived ids refused;
  producer provenance carried, with `digestsCaptured: false` emitting its own UNKNOWN item.
  +15 tests.
- `feat(assurance)` — `assurance import --into-case` freezes imported items with the case
  pack's own evidence into a fingerprinted ledger vN+1 through `freeze()`, refusing to
  overwrite an existing frozen ledger. `evidence_requests.json` now persisted for all four
  conditions. +5 tests.
- `fix(product)` — the page corrections, plus `tests/product/test_public_page_coherence.py`
  (+15 tests) binding every displayed assurance outcome, economics figure, seat position,
  ledger count and ladder amount to its committed source, with five retired overclaim phrases
  banned outright.
- `docs` — README claims corrected; `01-fable-report.md` errata + reconstructed mission of
  record; `docs/session-log.md` created; `docs/project-walkthrough.md` written properly;
  ADR-009 and ADR-010; `next-actions.md` reconciled with what actually shipped.

**Untouched, deliberately:** every frozen run artifact under `runs/`, the committed V0 ledgers,
`infra/**`, `.github/workflows/**`, `pyproject.toml`.

### Hekton Assurance (`agent/fable/assurance-consumer-contract-docs`)

Docs only, both commits, zero code and zero schema change. Fable recorded Kriterion as the
first external document-level consumer. Opus corrected that entry's claim from "a real
second-consumer data point" to what actually happened — the document *shape* was independently
re-read and implemented by someone who did not write it — and barred it from counting as
external-adoption evidence in the pending Retire/Promote Review until a real producer artifact
round-trips, with the falsifying test named in `next-actions.md`.

That correction is not pedantry: this lab's promotion review consumes these entries as evidence
and its recommendation already turns on real-world usage being thin. An inflated entry there is
a corrupted input to a decision awaiting human sign-off.

## Decision journey

Honestly, what a person gets today, in three layers:

**1. What is genuinely generated by the pipeline.** Starting from a case pack, `freeze()`
produces a fingerprinted evidence ledger; `econ` computes NPV/payback/tornado in pure Python
with no model call; `run` executes the committee protocol; `report` renders a per-run HTML
report from whatever artifacts exist. Assurance evidence now enters this path properly:

```
kriterion assurance import cases/coding-agent-rollout/assurance \
    --into-case cases/coding-agent-rollout --run-id my-run
kriterion econ   cases/coding-agent-rollout --run-id my-run
kriterion report my-run cases/coding-agent-rollout
```

That chain was executed. It freezes 26 case items + 12 derived assurance items into ledger v2,
and all 12 appear in the generated report with their source trail — the FAIL as a FAIL, the
indeterminate result as UNKNOWN, the three coverage gaps as named unknowns, and the
undigested-provenance item as its own UNKNOWN.

**2. What is hand-maintained and now says so.** `docs/index.html` — the public journey — is
hand-written HTML. Every figure on it is read from a committed artifact or computed by
deterministic code, but the page itself is narrative, not output. It now states this in its
lede, and `tests/product/test_public_page_coherence.py` mechanically checks each figure against
its source so the story cannot drift silently. That test is a stand-in, not a substitute: it
catches a changed number, not a stale narrative or a missing section.

**3. What does not exist yet, and cannot be faked.** No human has recorded a decision. The
journey renders "not yet recorded" and stops there, because an agent recording an accountable
human's act would be the single worst thing this instrument could do (RISK-0011). Everything
downstream — outcome contract, expected-versus-observed, retrospective — is structurally
enforced in code and empirically empty.

**Why option (b).** Codex's issue 1 offered a choice: wire the page to a renderer, or relabel
it. The mission's own scope discipline prefers the smaller honest proof, and a page renderer
built in the tail of a fix-up pass is exactly the rushed larger thing it warns against. But
"relabel it" alone would have left the substantive complaint — that assurance evidence could not
reach the system of record — unaddressed. So the split: the ledger path, which is the part that
actually matters for integrity, is genuinely built and tested; the marketing page is honestly
labelled and mechanically checked; generating it is named work.

## Assurance boundary

- **Direction:** one way. Kriterion reads documents. Assurance knows nothing of Kriterion.
- **Coupling:** the document shape only — `kind`, `envelopeVersion`, `capability`,
  `results[].{specId,method,outcome,detail,gating}`, `criticalFailures[]`,
  `fingerprint.uncovered[]`, `provenance`, `sourceState`, and
  `decision.{state,capabilityRef,envelopeRef,reasons,freshness,deciderVersion}`.
- **Code dependency:** none, in either direction, enforced by test.
- **Containment:** no Assurance field name appears outside `src/kriterion/assurance/`. The
  adapter emits Kriterion `EvidenceItem`s and nothing else crosses.
- **Strict where it matters, tolerant elsewhere (ADR-009):** unknown fields are ignored; a
  future major `envelopeVersion` is refused rather than guessed; the fields the guarantees rest
  on are required and type-checked.
- **Deliberately uncoupled:** no shared package, no stability contract (`v0alpha1` remains
  "LAB PROOF, NOT A PUBLIC CONTRACT"), no YAML dependency — Kriterion reads JSON and leaves
  conversion to the caller — and no investment/committee/allocation concept in Assurance.

## Validation

**Automated — `pytest`: 239 passed.** 193 pre-V1 baseline, 208 after Fable, 239 after Opus.
The 31 Opus-stage tests target precisely the invariants found broken: omitted and mistyped
`criticalFailures`; gating-fail-under-PASS; envelope↔decision identity binding (wrong
capability, wrong version, absent `capabilityRef`, mismatched `envelopeRef`); stale+PASS
downgrade; every malformed container shape; bare-string reasons; duplicate derived ids;
undigested provenance; the import → ledger v2 → econ → report chain; controlled CLI errors on
four malformed pairs; and 15 page/artifact coherence checks.

**Codex's five falsifying checks (section 10), executed:**

1. *Change a fixture value and see whether the page follows.* **Executed.** Flipping
   `secrets-handling-001` to `fail` does **not** change `docs/index.html` — confirming Codex's
   point that the page is hand-maintained, which is now what the page claims. The suite
   **fails** on that mutation, which is the mechanical guarantee replacing the generated one.
2. *Import the real Assurance `2026-09-07T19-31-41Z` FAIL pair after lossless JSON conversion.*
   **Executed, and it passes.** The real producer artifact — never previously imported by
   anything — yields `decision_state=FAIL`, one explicit `CRITICAL ASSURANCE FAILURE` item for
   `judge-consistency-rule-001`, `digests_captured=true`, `source_commit` preserved, and the
   real `envelopeRef` carried onto every item's source. This is the strongest single result in
   the loop: the contract is real, not merely self-consistent.
3. *Pair that envelope with an unrelated PASS decision, omit `criticalFailures`, set
   `freshness.stale=true`.* **Executed against the real artifact.** Unrelated PASS → refused
   (identity binding). Omitted `criticalFailures` + PASS → refused. Real `criticalFailures` +
   PASS → refused. Stale + PASS → imported as **STALE**, never PASS. No case summarises PASS.
4. *Import → freeze v2 → render, then render again with no Assurance repo.* **Executed**, and
   committed as a test. The second half is trivially satisfied: no producer package is
   installed, so the render path cannot reach one.
5. *Funding decision without an outcome contract must be rejected.* **Covered by pre-existing
   tests** (`test_cli_decide_contract.py`, `test_decisions.py`, 10 passing) and untouched by
   this work. The recommendation/decision separation is enforced by type, file and eval P0-09.

**Not run:** `scripts/verify-project.sh` does not exist on this branch's base — it lives only on
an unmerged infra branch. Disclosed by Fable, re-confirmed here, not silently skipped.
`scripts/check-prereqs.sh` passes.

## Deferred work

All named in `docs/next-actions.md`, not smuggled in:

1. **Generate the public journey page from the pipeline.** Chosen deliberately over a rushed
   renderer. The coherence test is a stand-in that catches drift, not staleness.
2. **Render the persisted per-seat evidence requests.** The artifact now exists; nothing
   displays it. Deferred once already for a specific reason: adding a report section changes
   every committed `report.html`, which are frozen research artifacts, so it needs a deliberate
   regeneration pass.
3. **Promote the structural economic assumptions** (discount rate, headcount timing, stage
   amounts) into ranged `Assumption` records. Narrowing the claim was the acceptable minimum
   and is done; modelling them changes `economics.json` output and needs the same deliberate
   regeneration.
4. **Import a real producer artifact as a committed fixture.** Executed manually this session
   and it passes — but it is not a committed test, because pinning another repo's evidence
   artifact into Kriterion's test suite is a coupling decision worth making explicitly rather
   than as a side effect. Named on both sides.
5. **The human decision + outcome contract beat**, and the decision retrospective. Blocked on
   an accountable human by design.
6. **Case B**; the pre-registered margin and inference-cost sub-conditions of the
   honest-negative criterion, inherited and still disclosed as unimplemented on both pages.

Consciously **not** fixed, with reasons given in *Codex critique resolution* above: the
unrecognised-outcome-on-recognised-method mapping (rejected — not a defect), and the verbatim
mission text (unrecoverable; a labelled reconstruction was substituted).

## Most important remaining product risk

**The instrument has still never been exercised by its accountable human on a decision whose
outcome anyone lived with — and this loop has now demonstrated that the failure mode it most
needs to defend against is its own narrative layer.**

The epistemic machinery is real and, after this pass, considerably harder to fool. But every
defect of substance found here was a *description* problem, not a computation problem: a FAIL
rendered as a softer word, reasoning attributed to a decision model that never produced it, an
authored fixture called an independent measurement, "deterministic" doing rhetorical work that
"complete" had not earned. The economics were correct throughout; the sentence summarising them
was not. That is precisely the compression-on-the-way-to-the-decision-maker failure Kriterion
exists to prevent, reproduced inside Kriterion's own shop window — and it survived a build stage
because nothing tested the prose against the record.

So the open question is sharper than "does the model work". It is: **does an instrument that
keeps uncertainty visible in its artifacts actually keep it visible in the story a human reads
and acts on?** Until a real person records a real decision, returns at a review date, and
compares expected against observed, the core thesis — that explicit evidence, assumptions and
unknowns produce better human *judgment*, not just better-organised analysis — remains an
argument. The coherence test is a hedge against the narrative drifting again. It is not
evidence that the narrative helps.
