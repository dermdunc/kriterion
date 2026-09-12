# Kriterion V1.1 — Executable Decision Story

**Loop:** Opus, solo (no separate adversarial-critique stage; the self-adversarial pass in §9
replaces it)
**Date:** 2026-09-12
**Branch:** `agent/fable/kriterion-v1.1-narrative-integrity` (name inherited from an aborted
earlier attempt, kept deliberately)
**Worktree:** `factory-output/kriterion--v1.1-narrative-integrity`
**Status at handoff:** 5 commits, local, working tree clean. **Nothing pushed, no PR opened,
nothing merged.**
**Tests: 341 passing** (239 at `origin/main` `00fc249`).
**Assurance impact: Kriterion-only.** `hekton-assurance-lab` is untouched — see §7.

| Commit | Scope |
|---|---|
| `2800f29` | `feat(product)` — the decision-state projection and the narrative-integrity invariant |
| `5c35796` | `feat(product)` — the generated public decision page, CLI and build script |
| `7d25660` | `test(product)` — narrative-integrity, projection and human-lifecycle regressions |
| `44881c5` | `docs` — ADR-011/ADR-012, corrected stale claims, the last-metre journal finding |
| `f8a7462` | `fix(product)` — executive-review fixes and the one-field-one-formatting check |

Diff against `origin/main`: 30 files, +7130 / −531. Roughly 2,280 lines of new `src/`, 1,950 of
new tests, 1,480 of committed run artifacts and generated HTML.

---

## Phase 0 — inspection and gap analysis

Everything below was read before any code was written: `AGENTS.md`, `docs/decisions.md` (ADR-001
to ADR-010), `docs/next-actions.md`, `.hekton/project.yaml`, all three V1 planning documents, the
domain model (`domain/*.py`), `casepack.py`, `ledger.py`, `economics/{engine,case_flows}.py`,
`decisions.py`, `report/html.py`, `assurance/adapter.py`, `cli.py`, `evals/run_loader.py`,
`protocol/{phases,parsing}.py`, `docs/index.html`, `docs/lab.html`,
`tests/product/test_public_page_coherence.py`, `tests/executors/test_boundary.py`, the committed
`runs/caseA-condC-s0` artifacts, and the committed assurance fixture pair.

### Already implemented

- The full V1 domain vocabulary as tested dataclasses: seven epistemic categories with an
  orthogonal `attestation` axis, ranged `Assumption`s with owners, `EconomicsResult` with a
  tornado, `CommitteePosition`, `BeliefUpdate` with harness-written `drift_flags`,
  `EvidenceRequest` **with a `would_change` field**, `SyntheticRecommendation` with mandatory
  non-empty dissent, and `HumanDecision` / `OutcomeContract` in separate types and separate files.
- Deterministic economics: NPV / payback / peak funding / tornado in pure Python, no model call.
- The evidence ledger with `freeze()` and canonical-JSON fingerprinting as the single write path.
- The ADR-007/009 assurance adapter, hardened: `criticalFailures` required and typed, gating-fail
  under PASS refused, envelope↔decision identity binding, stale-PASS downgraded to STALE, every
  malformed document shape an `AssuranceImportError`.
- `assurance import --into-case` freezing imported items into a fingerprinted ledger vN+1.
- The complete human lifecycle CLI: `decide`, `contract`, `validate-run` enforcing P0-09.
- `report/html.py` — the generated per-run research record, five opportunistic views.
- `evidence_requests.json` persisted for every condition since 2026-09-11.

### Implemented but not surfaced

- `EvidenceRequest.would_change` — persisted, rendered nowhere. The mission's brief says these
  "are already persisted"; **that is true only for runs made after 2026-09-11**, and no committed
  run had the artifact. This shaped the whole increment (see §5).
- `AssuranceSummary` — computed at import, discarded, so no view could show it.
- The human-decision and outcome-contract CLI path — real, tested in isolation, never exercised
  end to end, and invisible to a reader of the public page.
- `case.alternatives`, `strategic_objectives`, per-seat `distrusted_assumption`, `drift_flags`.

### Hand-maintained / drift-prone

- `docs/index.html`: 369 lines of hand-authored HTML. Every figure on it was checked against an
  artifact by `test_public_page_coherence.py`, which ADR-010 correctly called a stand-in: it
  catches a changed number, not a stale narrative, a missing section, or a softened sentence.
- `STAGE_LADDER_GBP` in `report/html.py`, duplicating `case_flows.py` constants.
- The tornado table, the evidence-buying arithmetic and the assurance conclusions all restated in
  prose beside the values they described.

### Missing

- Any projection layer. Nothing assembled case + ledger + economics + positions + requests +
  recommendation + human decision + contract into one object.
- Any narrative-integrity mechanism. Zero.
- A decision-level "what would move this decision" view.
- An error boundary on reading run artifacts (found later, in §9 — this was worse than it looked).

### Deferred intentionally (unchanged from V1, and still deferred)

Case B; the full value-of-information engine; retrospective analytics; portfolio views;
additional committee agents; an agent-conversation UI; provider expansion; hard cross-repo
artifact pinning; promoting the structural economic assumptions (discount rate, headcount timing,
stage amounts) into ranged `Assumption` records.

---

## 1. Starting state

`origin/main` at `00fc249`, 239 tests. Kriterion had a sound epistemic core and a hand-written
shop window. The V1 loop's own conclusion was that every defect of substance it found lived in
the gap between a hand-authored narrative and the artifacts it claimed to describe: an assurance
`fail` displayed as the invented word "PARTIAL" fourteen lines above a claim that failures cannot
be softened in translation; a producer's `REVIEW_REQUIRED` attributed to three coverage gaps its
decision document does not contain and its decider never reads; an authored fixture called an
independent measurement; one evidence-buying cost quoted as two different ranges in two places.

The computations were correct in every one of those cases.

---

## 2. Architecture choice

**One decision state; everything else is a view.** Two new modules and one new renderer, no new
data model.

```
case pack + frozen ledger + assumptions + deterministic economics
+ per-seat positions, belief updates, evidence requests
+ synthetic recommendation + human decision + outcome contract
+ (optional) imported assurance evidence
                      |
                      v
            DecisionState  (src/kriterion/decision_state.py)
              read-only; derived values computed once, here
                      |
                      v
   render_decision_page  ->  narrative.check()  ->  refuse or publish
                      |
                      v
              docs/index.html
```

- **`decision_state.py`** — every field either *is* a domain record loaded from a committed
  artifact, or is a pure function of those records. The derived values a decision-maker needs but
  nobody stores (capital actually at risk, the dominant sensitivity, the economics interpretation,
  what happens next) are computed once in the projection rather than written in a template,
  precisely so the checker can re-derive them. No new persisted schema; no core domain object was
  modified to serve HTML.
- **`narrative.py`** — `bind()` and `check()` (§4).
- **`report/decision_page.py`** — the renderer.
- **`kriterion decision-page`** — renders, then runs the check as a publish gate. `--check-only`
  verifies a committed page without rewriting it.

Four decisions worth naming, with their reasons:

1. **`report/html.py` is untouched.** The committed V0 run reports are frozen research artifacts;
   a shared renderer would rewrite them. The cost is a second renderer; the alternative was
   regenerating research output as a side effect of a presentation change. The Lab keeps its own
   renderer for the same reason.
2. **The projection does not import `kriterion.assurance`.** `tests/executors/test_boundary.py`
   and the adapter's own structural test forbid it, and they are right to. The page instead reads
   the Kriterion-side JSON that `kriterion assurance import --out` already writes, and a test
   asserts that committed payload is byte-for-byte what the adapter emits from the committed
   envelope. So the assurance section is generated, drift-proof, and the anti-corruption boundary
   is exactly where ADR-007 put it.
3. **Rendering is deterministic** — a pinned timestamp, no wall clock, no iteration over unordered
   sets. That is what lets a test assert the committed page is *byte-identical* to a fresh render,
   which is the check that makes "generated, not hand-maintained" a fact rather than a claim.
   `kriterion assurance import --created-at` was added for the same reason.
4. **No frontend framework, no JavaScript, no external assets.** Semantic HTML, one stylesheet,
   `aria-labelledby` on every section, one `<nav>`, and a strict rule that nothing unknown or
   failing is ever placed behind a `<details>` disclosure.

Recorded as **ADR-011**. ADR-010's arrangement (hand-maintained page + coherence test) is retired.

---

## 3. Implementation

### The projection (`src/kriterion/decision_state.py`, 765 lines)

`DecisionState` plus `SeatView` (one seat's initial position, revised position, belief update and
evidence requests) and `AssuranceImport`. Derived values include `capital_at_risk_gbp` and its
basis, `primary_uncertainty_label`, `tornado_rows` (the tornado joined to the case pack's own
assumption records so a swing figure is never shown without the evidence strength behind it),
`economics_interpretation`, `dominance_claim_scope`, `evidence_request_status`,
`outcome_contract_status`, `human_capital_commitment`, `assurance_summary_caveat` and `next_step`.

Three things this module exists to prevent:

- **Absence staying absent.** `npv_sign_flips` returns `None`, not `False`, when no economics were
  computed. `evidence_request_status` distinguishes three genuinely different states — the run
  predates the artifact / the artifact exists and nobody asked / requests were recorded.
  `outcome_contract_status` distinguishes four. A ledger that declares no `items[]` is a refusal,
  not an empty render.
- **A funding action being inferred.** `capital_at_risk_gbp` is `0.0` unless the recommendation's
  action is in `FUNDING_ACTIONS` — the same set `kriterion validate-run` uses. The canonical case
  recommends DEFER while its recommendation record carries the full £4.2m ask in its `amount`
  field; rendering that as capital at risk would misstate a deferral as a spend.
- **One fact having two names.** The economics artifact stores the engine's parameter
  (`attribution_factor`); the case pack stores the assumption id (`as-benefit-attribution-factor`).
  `primary_uncertainty_label` resolves it once so the headline and the interpretation cannot
  disagree.

### The renderer (`src/kriterion/report/decision_page.py`, 794 lines)

Twelve sections, in the order a decision-maker needs them: the decision → what we know → what we
are assuming → what we do not know → the economics → capability assurance → where the perspectives
agree and disagree → what would change this decision → synthetic recommendation → human decision →
outcome contract → how this page was produced.

### CLI and build

`kriterion decision-page RUN_ID CASE_DIR [--assurance-import P] [--out P] [--check-only]`;
`kriterion assurance import --created-at`; `scripts/build-decision-page.sh`, which is the entire
build and has no hand-editing step. Running it twice produces identical bytes.

### The canonical run (`runs/caseA-condC-s5/`)

The mission assumed `EvidenceRequest`s were already persisted and merely unrendered. They were
persisted only for runs made after 2026-09-11, and **no committed run had the artifact** — so a
per-seat "what would change my mind" view could only ever have been reconstructed copy on the V0
demo runs, which is exactly what V1 was criticised for.

So a fresh Treatment C run was executed live against local Ollama (`qwen2.5:14b-instruct`,
seed 5), producing 10 real per-seat evidence requests with real `would_change` text. Discipline
around it:

- **Seed 5 is outside the pre-registered 0–4 grid and takes no part in any comparison.** It is not
  a replacement for seed 0, and the `.gitignore` entry says so.
- `runs/caseA-condC-s0` is untouched, and a test asserts it still has no `evidence_requests.json`,
  since that historical fact is what the page's status line reports.
- The result independently reproduced seed 0's shape: 5/5 DEFER at both phases, CFO confidence
  LOW→MEDIUM, final action DEFER.

---

## 4. Narrative integrity

Adopted as an invariant (**ADR-012**), not a prompt and not a review habit:

> Every material statement presented to a decision-maker must be traceable to the underlying
> decision state and must not strengthen, soften, contradict or invent its meaning.

`src/kriterion/narrative.py` (724 lines) enforces it in two halves.

**Binding.** `bind()` is the only sanctioned way to put a material value on the page. It stamps
the element with the state path and the formatter used, and escapes the value so the element
contains no markup. `check()` re-resolves every path against the authoritative `DecisionState`,
re-applies the named formatter, and refuses any element whose text is not exactly what the state
says. FAIL cannot be written as PARTIAL because the checker recomputes FAIL from the record. The
committed page carries **509 bindings**.

**Unbound prose.** Binding alone would still allow a hand-written sentence beside a correct
figure, so every text node *outside* a bound element may carry no currency amount, percentage or
large number; no state-vocabulary token (`DecisionAction`, `EvidenceCategory`, `Strength`,
`ConfidenceBand`, assurance outcome); no softening or promotion word; and no recommendation claim.

Rules, by name:

| Rule | What it prevents |
|---|---|
| `binding.match` / `.resolve` / `.format` / `.literal` / `.present` | Any rendered value that is not exactly what the state says, or that points at a field that does not exist |
| `numeric.fidelity` | A figure retyped into prose, or injected via a CSS `content:` declaration |
| `numeric.consistency` | One field rendered with two different formatters — the "quoted two ways" failure |
| `vocabulary.fidelity` | An unbound state token in prose |
| `decision.fidelity` | The recommendation headline sourced from anything but `recommendation.action`; a recommendation claim asserted in a sentence, including lowercase |
| `softening` | PARTIAL / mostly / broadly / proven / verified / no issue / not detected, and 11 more |
| `epistemic.fidelity` | An evidence item rendered without its own bound epistemic class |
| `evidence.attribution` | A card about one item rendering another item's fields |
| `attribution.fidelity` | A seat's card rendering another seat's records, or a page-level statement attributed to a seat |
| `separation.human_ai` / `.regions` | The synthetic recommendation and the human decision sharing a field or a region |
| `unknown.preservation` | Any UNKNOWN ledger item or imported assurance item silently dropped |

`kriterion decision-page` runs the check as a publish gate and exits 1 without writing on any
violation.

### Tests

**49** in `tests/product/test_narrative_integrity.py`, covering every case the mission named —
assurance FAIL softening (parameterised over PARTIAL / MOSTLY SATISFIED / CONCERN / NEEDS
ATTENTION / MINOR ISSUE), recommendation misattribution (the fixture's reasoning deliberately
says "a pilot could resolve the attribution uncertainty" under a DEFER), deterministic economics
preserving sign, currency, range ordering and key sensitivity, assumption promotion, and unknown
handling (parameterised over PASS / NOT DETECTED / NO ISSUE) — plus 41 in
`test_decision_state.py`, 17 in `test_public_page_coherence.py`, 7 in
`test_human_decision_lifecycle.py` and 8 in `test_cli.py`.

Structural tests over brittle snapshots throughout, with one deliberate exception: the
byte-identity test, whose entire purpose is to be exact.

`test_public_page_coherence.py` was rewritten rather than extended. Its figure-by-figure
assertions are **deleted on purpose** — each is now a structural guarantee, and keeping
hand-copied expected values would reintroduce the second source of truth this increment removed.
What it keeps is the byte-identity check, the integrity check, the adapter-payload check, the
retired-overclaim ban (now including "hand-maintained", which became a stale claim), and a check
that Kriterion Lab still carries its A/B/C/D research and its negative result.

---

## 5. Decision experience

The canonical case, beginning to end, as a visitor now reads it.

**The decision.** "Should we fund a staged rollout of an enterprise coding agent to 5,000
engineers?" £4,200,000 over 24 months, staged funding. Sponsor CTO, accountable owner `cio`,
decision sought by 2026-12-01, four named alternatives including `do_nothing`. Then:

- Synthetic recommendation, machine-generated: **DEFER**, confidence MEDIUM.
- Capital the machine's suggestion would put at risk: **£0** — "DEFER commits no funding. The
  recommendation record still carries the full ask as its amount field; that is the ask, not a
  commitment."
- What the accountable human has committed: "No human decision has been recorded, so nothing is
  committed."
- Dominant uncertainty: `as-benefit-attribution-factor`, worth **£16.92m** of swing — with its
  recorded evidence strength **LOW**, base value 10%, plausible range 5%–20%, owner `cfo`.
- Base **£5.09m**, downside **−£5.35m**, upside **£38.14m**, and the derived reading: "The sign of
  the outcome flips inside the stated plausible ranges, so the case is not yet decidable on the
  numbers alone."
- The decision vocabulary, with no approval verb.

**What we know** — 15 items, HIGH strength expanded, the rest behind a disclosure, each with its
epistemic class, strength, attestation, verbatim claim and source. **What we are assuming** — the
five ranged assumptions with base value, range, evidence strength and owner, then the modelled and
inferred items. **What we do not know** — three UNKNOWN items, never collapsed, never behind a
disclosure: no agreed attribution methodology, long-run code quality as the vendor's model
changes, real-world prompt-injection incident rate at scale.

**The economics** — the NPV triple, the 10% discount rate, the interpretation, and the tornado
joined to the assumption records so each swing sits beside the evidence strength and owner behind
it, with the ranking's scope stated: five declared assumptions, structural code constants
excluded.

**Capability assurance** — the imported envelope, stating plainly that it arrived after the
deliberation and is not in this run's frozen ledger, so the committee never saw it. Declared state
and imported state shown separately. The producer's own two reasons, quoted. All 12 derived items
in the adapter's own words, including the prompt-injection **FAIL**, the indeterminate runtime
drift as UNKNOWN, three coverage gaps as named unknowns, and `digestsCaptured: false` as its own
unknown.

**Perspectives** — five seats. All five recorded DEFER; only the CFO's confidence moved
(LOW→MEDIUM). Kriterion reports that as a round in which nothing moved, rather than manufacturing
disagreement. Each card carries the seat's position, its reasons with evidence refs, what it holds
open, the assumption it least trusts, **what it asked for and its own `would_change`**, and how it
moved after challenge with its stated reason.

**What would change this decision** — the decision-level view: 10 recorded per-seat requests, the
recommendation's own unmet conditions and open unknowns, and what each further stage would cost
(£50,000 → £420,000 → £1,600,000) with an explicit statement that no record links a requirement to
the stage it unlocks, so none is inferred.

**Synthetic recommendation** — behind a machine-generated banner, with the strongest preserved
dissent quoted verbatim. **Human decision** — "No human decision has been recorded for this case.
Kriterion will not record one on an accountable human's behalf," then what happens next, naming
`cio` and `kriterion decide`. **Outcome contract** — why none exists. **How this page was
produced** — the run id, ledger version and fingerprint, item counts, and the link to Kriterion
Lab.

All twelve definition-of-done questions are answerable from the page. Question 10 ("what would
justify the next investment stage?") is answered partially and says so: the stage costs and the
recorded requirements are both shown, and the absence of a link between them is stated rather than
filled in.

---

## 6. Human decision readiness

The path is real, verified end to end, and deliberately unexercised on the canonical case.

```
kriterion decide  <run-id> --action PILOT --disposition modify --owner NAME --rationale "..."
kriterion contract <run-id> --baseline-date ... --review-date ... --next-decision ... \
                            --measure name:baseline:target:source_ref --kill-criteria "..."
kriterion validate-run <run-id>
bash scripts/build-decision-page.sh <run-id>
```

`tests/product/test_human_decision_lifecycle.py` drives that sequence through the real CLI over a
throwaway copy of the canonical run, because no committed run has a human decision and the
renderer's human-decision and outcome-contract branches would otherwise never execute against
real data. Verified at each stage: undecided renders honestly and names the next act; a funding
decision without a contract warns at the point of the act, fails `validate-run` with P0-09, and
renders as a governance violation; a contracted decision validates clean and renders its measures,
review date and kill criteria, with "what happens next" becoming the review date.

**No `HumanDecision` was fabricated** (RISK-0011). Nothing the lifecycle test writes is committed.

---

## 7. Assurance impact

```
Kriterion-only
```

`hekton-assurance-lab` is at `325f786` with a clean tree; not one file was touched. The producer
contract was correct, no generic field was missing, and no interoperability bug surfaced. The one
thing the page needed from the adapter — its output — it gets from the Kriterion-side JSON the
existing `assurance import --out` command already writes, so the increment needed no new coupling
in either direction. The `--created-at` flag added for reproducibility is Kriterion-side and does
not change what is imported.

One producer-side note, unchanged from V1 and still only a note: the consumer keys its
refuse-don't-guess behaviour on `envelopeVersion`, so a shape-breaking change should bump it.

The real-producer-artifact fixture remains deliberately unpinned. Making Kriterion's CI depend on
mutable output from another repo is a coupling decision that deserves its own explicit call.

---

## 8. Validation

**`.venv/bin/python -m pytest -q` → 341 passed** (239 at `origin/main`; +102).

| Suite | Tests |
|---|---|
| `tests/product/test_narrative_integrity.py` | 49 |
| `tests/product/test_decision_state.py` | 41 |
| `tests/product/test_public_page_coherence.py` | 17 |
| `tests/product/test_human_decision_lifecycle.py` | 7 |
| `tests/test_cli.py` | 8 (3 new) |

Also executed, beyond the suite:

- `bash scripts/build-decision-page.sh` twice → identical bytes for `docs/index.html` and
  `cases/coding-agent-rollout/assurance/imported.json`. The page renders with **0 violations**.
- A full live Treatment C run against local Ollama (`runs/caseA-condC-s5`), then `ledger freeze`,
  `econ`, `report`, `decision-page`.
- The human lifecycle, by hand, through all three stages before it was made a test.
- **Rule mutation testing.** Disabling each rule in turn — `binding.match`, the prose rules, the
  attribute/CSS scan, the recommendation-phrase rule, the malformed-artifact boundary — makes the
  corresponding tests fail. The tests bite; they do not merely pass.
- `bash scripts/check-prereqs.sh` passes. `scripts/verify-project.sh` still does not exist on this
  base — it lives only on an unmerged infra branch. Disclosed, not silently skipped.

Unchanged and verified unchanged: every committed V0 run artifact, `runs/caseA-condC-s0`,
`report/html.py` and every committed `report.html`, `infra/**`, `.github/workflows/**`,
`pyproject.toml`. No protected path was touched.

---

## 9. Self-adversarial review

This replaces the missing Codex stage. The rule I held myself to: re-read every changed file
trying to refute my own claims, and *execute* the attacks rather than reasoning about them. Four
real defects came out of it, three of them the same bug *shapes* the V1 review found — in code I
had just written while thinking about exactly those shapes.

### Finding 1 — uncaught exceptions on malformed input. 16 of 16 cases escaped as tracebacks.

The worst of the four, and an exact recurrence of V1's issue 7. I fed the projection sixteen
malformed run artifacts. **All sixteen produced bare tracebacks**, not controlled refusals: a
ledger with no `items` (`KeyError`), a ledger whose `items` is an object (`TypeError: string
indices must be integers`), an evidence item missing `claim`, a category of `TOTALLY_FINE`, a
positions file written as an object, a `DecisionAction` of `APPROVE`, an evidence request with no
`would_change`, a recommendation with no dissent, economics missing `npv_mid_gbp`, a
`change_type` of `vibes`, and more.

ADR-009 had already established for the adapter that a traceback is not a refusal and that
*unknown* must stay distinct from *crashed*. I reproduced the defect anyway. Fixed with a real
error boundary (`_require_list`, `_load_each`, `_load_one`, `_guard`) converting every shape
failure into a `DecisionStateError` that names the artifact, the index and the field. Re-ran all
sixteen: **16 controlled refusals, 0 escapes.** All sixteen are now parameterised regression tests,
and disabling the boundary makes 7 of them fail.

That this happened while I was actively thinking about the failure mode is the argument for
mechanical checks over vigilance, and it is recorded in the project journal on those terms.

### Finding 2 — one fact, two answers (the tornado ordering).

The headline dominant uncertainty used `max(abs(swing))`; the tornado table rendered the
artifact's stored order under a caption reading "widest first". The engine happens to sort that
way, so real data agreed. I fed the projection a deliberately unsorted tornado and the headline
said `attribution_factor` while the table's own first row said `uplift` — one fact, two answers,
under a caption asserting the ordering. That is the "inconsistent figures quoted twice" shape.
Fixed by ordering `tornado_rows` by magnitude in the projection, so both derive from one rule.

### Finding 3 — four routes past the checker, found by probing it rather than reading it.

Each passed cleanly on the first implementation:

1. **`title=` attributes** — a claim in a tooltip. Stripping tags hid attribute text from the
   prose scan, so "The committee recommends a PILOT of £420,000" in a tooltip was invisible to the
   checker and perfectly visible to a reader.
2. **`aria-label` / `alt`** — narrative delivered to a screen-reader user, unscanned.
3. **CSS `content:`** — `.insight::after { content: " Overall: PASS"; }` puts words on the page
   that no HTML text node contains, and the style block is stripped before the scan.
4. **Lowercase recommendation claims** — the vocabulary rule is case-sensitive, so "on balance the
   committee recommends a pilot" sailed through. Making every state word case-insensitive would
   forbid ordinary English ("pilot cohort"), so I added a narrow recommendation-phrase rule
   instead and a test asserting ordinary English stays legal.

All four now caught. All four are regression tests. Disabling the new scans fails them.

### Finding 4 — capital at risk, ambiguous between two actors.

Surfaced by *exercising* the human lifecycle rather than reasoning about it. With a synthetic
DEFER and a human PILOT both recorded, the page showed one figure labelled "Capital this would put
at risk: £0". Correct for the machine's suggestion, and read by a human as the decision's
exposure — after a human had authorised a pilot. A misattribution, in the most consequential field
on the page. Fixed: the label now names the actor, and `human_capital_commitment` states the
human's own commitment separately — including the honest admission that `HumanDecision` carries an
action but no amount, so the committed sum genuinely is not recorded anywhere. Reusing the
recommendation's amount would have attributed a number to a human who never wrote one.

### Phase 6 — the executive review, and what it changed

Reading the finished page as CIO, CFO, CISO and sceptical sponsor produced three fixes worth
making. The sharpest was another instance of this increment's own subject:

- **Softening by omission (CISO).** The assurance summary led with "critical failures declared:
  0" above a list of twelve items. The envelope records a non-gating FAIL *and* a check that
  returned no verdict — so that line is literally true and reads as "every check passed". Now
  accompanied by a derived statement of what the producer's count does and does not cover, plus
  how many imported items are epistemically unknown (5 of 12). Derived from Kriterion's own
  evidence categories, so the boundary is untouched.
- **Evidence strength beside the dominant assumption (CFO).** Naming the assumption that swings
  the valuation by four times the ask, without saying how well evidenced it is, invites the reader
  to assume it is solid. It now carries strength, base value, range and owner.
- **The money above the fold (CIO).** The sign-flip finding sat four sections below the decision.
  Base, downside, upside and the interpretation now appear in the decision snapshot. That
  deliberately repeats figures across sections, which is how V1 came to quote one cost two ways —
  so it prompted the `numeric.consistency` rule, making "one field, one formatting" checked rather
  than assumed.

### One false alarm, distinguished from a real bug

A page-shape test failed asserting the dominant assumption's fields were bound in the decision
section. The cause was not a renderer defect: the synthetic test fixture uses case id
`fixture-case`, which has no parameter-to-assumption map, so its dominant sensitivity legitimately
does not resolve to a ranged `Assumption`. The renderer was correctly taking its honest fallback
branch. I moved the mapped assertions to the real canonical page and had the fixture assert the
fallback stays honest ("does not declare as a ranged assumption") — rather than adding a map entry
to make my test pass, which would have deleted the coverage of the unresolvable case.

### Claim-verification pass

Before writing this report I checked its own load-bearing claims against the diff: the test count
(`pytest -q` → 341, and per-file collection), "generated not hand-maintained" (the byte-identity
test is real and fails on a one-character edit), the binding count (**this caught an error**: I had written 520 from memory; counted two ways
it is 509, corrected before this report was committed), the commit list and diffstat, that `runs/caseA-condC-s0` is untouched (`git diff` clean),
and that `hekton-assurance-lab` has a clean tree at `325f786`.

### Limits I am not claiming past

1. **Binding proves derivation, not fairness.** It proves a sentence like
   `economics_interpretation` is computed from the record and cannot be hand-edited without
   detection. It cannot prove the English is a *fair* summary of the numbers. That stays a human
   judgment, and it is the honest boundary of this whole approach.
2. **The checker sees only what it is pointed at.** Findings 1 and 3 are both evidence of that. I
   closed four routes by probing; I do not claim there is no fifth.
3. **The vocabulary rule is case-sensitive** by design, with a narrow phrase rule covering the
   lowercase recommendation claim. Other lowercase softenings could still pass.
4. **One case, one run, one condition.** Nothing here is validated across cases.
5. **Seed 5 is a single run** made with the current code, outside the pre-registered grid. It
   reproduced seed 0's shape, which is reassuring and is not a finding.

---

## 10. Remaining gaps, prioritised

1. **No human has recorded a decision.** The instrument has still never been exercised by its
   accountable human on a decision whose outcome anyone lived with. The path is verified and the
   page states the absence honestly; what is missing is the human.
2. **Nothing links an evidence requirement to the stage it would unlock.** Kriterion records what
   each stage costs and what each seat wants, but not which requirement unlocks which stage. The
   page says so rather than inferring it. Needs a real case-pack schema for the ladder, which is
   still a `case.toml` comment plus constants in `case_flows.py`.
3. **The structural economic assumptions are still code constants** (10% discount rate,
   full-period headcount treatment, stage amounts), excluded from the tornado. The page states the
   ranking's scope explicitly; modelling them changes `economics.json` and needs a deliberate
   regeneration pass.
4. **The model's `would_change` text is often an outcome, not a test.** Real output includes
   "Increase confidence in security and compliance readiness" — not a falsifiable condition. The
   mechanism is real and the content is weak, which is a protocol finding, not a rendering one.
5. **No real producer artifact is a committed fixture.** Deliberate; the coupling decision is
   worth making explicitly.
6. **Value-of-information.** The chain assumption → range → sensitivity → evidence quality →
   `EvidenceRequest` is now visible on one page, which is the precondition. The engine was out of
   scope.
7. **`scripts/verify-project.sh` does not exist** on this base.

---

## 11. Most important next experiment

> What should a real human decision-maker do with Kriterion next to generate information that
> another engineering loop cannot provide?

**Record a real decision on this case, in writing, and then say which part of the page changed
their mind — and produce that answer before seeing the page a second time.**

Concretely: sit the accountable owner in front of `kriterion.theagentictekton.com`, have them run
`kriterion decide` with a rationale in their own words, and capture two things an engineering loop
provably cannot produce.

First, **the disagreement between their rationale and the machine's**. Both are now recorded, in
separate files, in the same vocabulary. Whether a human who has seen explicit unknowns, ranged
assumptions and a named dominant uncertainty reaches a *different* decision than the synthesiser —
and whether their stated reasons cite the things Kriterion surfaced — is the core thesis, and it
is currently an argument. Every loop so far has improved the artifact's honesty; none has produced
one data point on whether that honesty changes human judgment.

Second, **which section they actually used**. This increment made a page that satisfies twelve
questions with 509 traceable bindings, and I have no evidence that a CFO reads more than three of
them. It is entirely possible that the most valuable thing here is the one line saying the sign
flips inside the plausible range, and that most of the rest is completeness serving the builder
rather than the reader. An engineering loop will keep adding faithful sections; only a real reader
can say which ones carry the decision. If the answer is three, the correct next increment is
subtraction — and that is a conclusion no amount of further building can reach.

The experiment has a falsifiable failure mode worth stating in advance: if the human's recorded
rationale turns out to restate the synthetic recommendation in their own words, with no citation
of any unknown or assumption the page surfaced, then Kriterion is producing better-organised
analysis rather than better judgment, and the thesis is in trouble. That is the result most worth
being able to see.
