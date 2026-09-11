## 1. Verdict

`RED` — this is not an end-to-end V1 vertical slice. It is an isolated document adapter plus a manually curated homepage that is not driven by the adapter, ledger, or report pipeline. The homepage also contradicts the fixture by rendering an Assurance `fail` as `PARTIAL` while claiming translation cannot soften failures.

Opus should not patch only the copy. It must settle the actual V1 integration boundary and make one artifact flow through import → frozen ledger → decision record.

## 2. Blocking issues

### 1. The claimed vertical slice stops before Kriterion’s system of record

Evidence:

- `src/kriterion/cli.py:622-667` only serializes imported items to stdout or an arbitrary file.
- It never calls `freeze()`, creates a new ledger version, attaches evidence to a run, or invokes the report renderer.
- `docs/next-actions.md:323-325` explicitly admits ledger ingestion remains future work.
- `docs/index.html` is entirely hand-authored HTML; no build or rendering path connects it to the imported items.
- The Fable report nevertheless calls this “one complete decision journey, produced end-to-end by the real pipeline” at `docs/index.html:74-77`.

Consequence: Assurance evidence cannot affect a deliberation, frozen evidence record, recommendation, or generated decision report. Staleness and UNKNOWN handling are only properties of an isolated JSON conversion, not of the shipped UI.

Required change: implement one real fresh-run path that imports Assurance items, freezes them into ledger vN+1, runs or renders from that ledger, and verifies that the displayed Assurance state comes from those artifacts.

### 2. The public UI softens a source `fail` while claiming failures cannot be softened

Evidence:

- `cases/coding-agent-rollout/assurance/envelope.json:97-105` records `prompt-injection-resilience-001` with `"outcome": "fail"`.
- The adapter would render that as `FAIL`: `src/kriterion/assurance/adapter.py:241-245`.
- The homepage instead displays `PARTIAL`: `docs/index.html:190`.
- `PARTIAL` is not an Assurance outcome or decision state.
- Fourteen lines later, the page claims the adapter guarantees the evidence “can't be softened in translation”: `docs/index.html:200-204`.

Consequence: the showcase demonstrates the exact semantic laundering it claims to prevent. Because the page is disconnected from the adapter, tests cannot catch the contradiction.

Required change: render `FAIL`, qualifying it as non-gating if useful, and generate the table from adapter output or test every displayed field against the source documents.

### 3. The PASS anti-laundering guarantee is incomplete

Evidence:

- `criticalFailures` is silently defaulted to `[]` at `src/kriterion/assurance/adapter.py:189`.
- The PASS guard at `:193-198` only checks that denormalized list.
- A deterministic, gating result with `outcome: fail`, an omitted `criticalFailures` field, and a PASS decision is accepted. I executed that case against the branch: the returned summary was `PASS`, alongside an item saying `FAIL`.
- The adapter does not bind the decision to the envelope. It never compares `decision.capabilityRef`, `decision.envelopeRef`, or version with the supplied envelope (`:183-191`).
- A PASS decision from another capability/envelope is therefore accepted.
- A freshness block can say stale while state remains PASS; the summary remains `decision_state="PASS"` (`:190-191`, `:333-343`), although item claims receive a stale prefix.

Consequence: malformed, incomplete, or mismatched document pairs can produce an authoritative-looking PASS summary. The advertised “hard guarantee” is only true for one well-formed representation.

Required change: require and type-check safety-critical fields, bind decision and envelope identities, reject inconsistent freshness/state combinations, and degrade incomplete integrity information to UNKNOWN or refusal.

### 4. The page fabricates how the Assurance decision was reached

Evidence:

- `docs/index.html:195-197` says REVIEW_REQUIRED is caused by the prompt-injection result “plus three named coverage gaps.”
- `decision.json:12-22` contains only two reasons: counterfactual failure and runtime-drift indeterminacy.
- The producer’s decider does not examine `fingerprint.uncovered`: `hekton-assurance-lab/src/hekton_assurance/decide.py:129-170`.
- `docs/index.html:200-202` says the envelope “independently measures” partial resilience, while the fixture says no Assurance run occurred at `envelope.json:2` and `README.md:3-5`.

Consequence: the UI invents both causal decision logic and independent measurement.

Required change: describe coverage gaps separately from the decision reasons, and call the result an authored demonstration claim, not an independent measurement.

### 5. The economics are deterministic, but not all load-bearing assumptions are surfaced

Evidence:

- The economics are correctly calculated in Python.
- However, `case_flows.py:8-11` assumes each stage’s headcount is active for a full annual period.
- `case_flows.py:30-38` hard-codes an unevidenced 10% discount rate, headcounts, and stage amounts.
- These inputs are not `Assumption` records and are excluded from the tornado.
- `docs/index.html:150-154` concludes that attribution and uplift dominate the business case, but that conclusion only applies to the five selected sensitivities.

Consequence: deterministic computation is being confused with complete assumption discipline. The full-year 1,200/5,000-engineer timing assumption could materially change the result but is absent from the decision view.

Required change: model material timing, headcount, discount-rate, and stage assumptions explicitly or qualify the dominance claim as limited to the five parameters tested.

### 6. “What would change your mind” is claimed as a record but remains reconstructed copy

Evidence:

- `README.md:17` advertises an explicit “what would change this position” record.
- No `EvidenceRequest` is instantiated or persisted anywhere.
- `docs/next-actions.md:319-322` and the Fable report at `:67-69` admit the page reconstructs it from blocking unknowns and recommendation conditions.

Consequence: the central decision-instrument affordance is not auditable per seat and cannot be traced to an actual `EvidenceRequest.would_change`.

Required change: persist `EvidenceRequest` artifacts or revise all product claims to say the page currently summarizes proxy fields.

### 7. Malformed JSON can escape the documented error boundary

Evidence:

- `load_assurance_documents()` accepts any valid JSON value: `adapter.py:91-109`.
- `_decision_state()` immediately assumes a mapping: `:142-149`.
- Reason handling assumes every reason is a mapping: `:302-305`.
- The CLI catches only `AssuranceImportError`: `cli.py:632-642`.
- I verified that a decision array and a string reason both raise uncaught `AttributeError`.

Consequence: user-supplied document errors produce tracebacks instead of a controlled refusal, contradicting the “refuse, don’t guess” posture.

Required change: validate container and nested field types and convert every contract-shape failure into `AssuranceImportError`.

## 3. Architecture boundary verdict

- Assurance domain independence: **PASS.** Its diff is exactly three documentation files and 23 insertions. No investment proposal, committee, stage, allocation, vote, or recommendation type entered Assurance code or schema.
- Zero code dependency: **PASS.** Kriterion does not import `hekton_assurance`; Assurance does not import Kriterion.
- Kriterion type translation: **PASS.** Assurance field names are confined to `src/kriterion/assurance/`, and the adapter emits Kriterion `EvidenceItem` objects.
- Dependable anti-corruption boundary: **FAIL.** The envelope and decision are not identity-bound or adequately shape-validated, and the actual UI bypasses the adapter.

The architecture separation is sound; the integrity enforcement at that separation is not.

## 4. Fabrication/claim-discipline findings

The fixture is generally labelled well: the homepage banner, fixture README, both JSON files, Assurance section, and footer all say it is authored/synthetic. No human decision was fabricated.

Material unsupported claims remain:

- “Produced end-to-end by the real pipeline” and “nothing … is a mock-up” at `docs/index.html:74-77`: false for the hand-written Assurance fixture and hand-written homepage.
- `FAIL` displayed as `PARTIAL` at `docs/index.html:190`.
- Coverage gaps represented as decision reasons at `docs/index.html:195-197`.
- Authored claims described as independently measured at `docs/index.html:200-202`.
- “Kriterion runs identically with manual and imported evidence only” at `docs/index.html:207-209`: imported evidence is not part of a run at all.
- “Explicit what-would-change record” at `README.md:17`: no record is persisted.
- Evidence-buying cost is inconsistent: `£50k–£420k` at `docs/index.html:172`, but `£50k–£470k` at `:285` and in the Fable report. The latter appears to add discovery and pilot, while the former treats them as a range.
- `docs/index.html:283` calls the ladder structured “case pack input,” but `case.toml:23-26` contains it only as a comment; executable values live in `case_flows.py`.
- Assurance’s new ADR calls Kriterion a “real second-consumer data point,” but Kriterion consumes a hand-authored JSON facsimile. The producer emits YAML, and no real producer artifact was imported.

The remaining displayed case facts, NPV values, tornado values, committee positions, confidence transition, and recommendation match the committed artifacts.

Report mismatches:

- The report repeatedly claims 16 adapter tests (`01-fable-report.md:117,171,233-235`). There are 15 test functions/node IDs. The total 208 is consistent with 193 + 15.
- The report says imported Assurance provenance survives, but the adapter does not preserve the producer’s `provenance` block. It copies an unverified `decision.envelopeRef` string and spec ID.
- The promised original mission is not present in `01-fable-report.md`; the 276-line file begins directly with Fable’s report. That prevents full mission-fidelity verification from the prescribed source.

## 5. Invariant violations found

- Seven epistemic classes: **upheld in the domain** at `domain/evidence.py:12-21`; method mapping is explicit at `adapter.py:161-165`. Caveat: arbitrary unrecognised outcomes on recognised methods become MEASURED rather than UNKNOWN.
- Synthetic recommendation versus human decision: **upheld** in the model at `domain/decision.py:18-46` and visibly separated at `docs/index.html:87-90,243-264`.
- Critical failure cannot become PASS: **fails under incomplete/mismatched input**. The explicit non-empty-list case is protected, but missing `criticalFailures` and unbound decision documents are not.
- Unknown versus failing evidence: **upheld in adapter items** at `adapter.py:235-251`; **violated in the showcase**, where `fail` becomes `PARTIAL`.
- Stale evidence visibly stale: **partially upheld**. Items get a marker and LOW strength at `adapter.py:212-214`, but a stale freshness block can retain a PASS summary, and no generated UI exercises the marker.
- Assurance entirely absent: **upheld in code structure**. The import is command-local at `cli.py:622-628`, and no producer package is required. The test proves only static import placement, not a complete absent-install execution.
- Economics computed without an LLM: **upheld**. The calculations are deterministic, although some important assumptions remain hidden constants.
- Human decision not fabricated: **upheld**.

## 6. Scope overreach

No generic portfolio platform, workflow engine, GRC system, observability product, Assurance rewrite, chat UI, or longitudinal analytics platform was introduced.

What should be deleted or deferred:

- Remove or downgrade Assurance’s “real second-consumer data point” language until Kriterion consumes an actual producer artifact.
- Remove the manually duplicated Assurance conclusions from the homepage unless they are generated or mechanically checked.
- Do not expand the adapter into a generic schema framework; strict support for the actual 0.x document contract is enough.

Research integrity otherwise passes. Relative to the real branch base `fe1b85b`, `docs/lab.html` preserves the V0 page’s substantive findings, caveats, report links, and seeds; only Lab framing and cross-links changed. Fable did not edit frozen runs. The extra report-file changes visible in `main...HEAD` came from the two upstream editorial commits because local `main` is stale, not from Fable’s three commits.

## 7. Missing but essential

- A real import → frozen-ledger-version → report path.
- A generated or mechanically source-checked public decision journey.
- Import compatibility testing against a real committed Assurance envelope/decision, not only a consumer-authored facsimile.
- Envelope/decision identity binding and strict safety-field validation.
- Persisted per-seat `EvidenceRequest.would_change` artifacts.
- Explicit economics records for material ramp/timing and discount-rate assumptions.
- A human decision/outcome-contract exercise before claiming a complete decision lifecycle. It need not be fabricated, but the absence must constrain the product claim.
- The original mission text in the Fable-stage audit file.

## 8. Test validity concerns

Meaningful tests:

- Epistemic method mapping.
- Explicit stale-item marking.
- Non-empty `criticalFailures` plus PASS refusal.
- Missing decision → UNKNOWN.
- Unknown method and future-major behavior.
- Basic JSON loading.
- Basic committed-fixture smoke test.

Weak or superficial coverage:

- `test_assurance_is_optional_no_other_kriterion_module_imports_it` only greps import syntax and explicitly exempts the CLI. It does not run Kriterion without Assurance documents or without the producer installed.
- The “tolerant reader” test adds one irrelevant field; it does not test malformed known fields.
- The fixture test checks only the summary and one prompt-injection item.
- No test covers omitted/malformed `criticalFailures`, mismatched envelope/decision, incompatible capability refs, stale/PASS inconsistency, invalid reason types, duplicate generated IDs, or arbitrary result outcomes.
- No CLI test asserts controlled errors.
- No test compares `docs/index.html` with the fixture, economics, recommendation, or belief-update artifacts. Consequently, `FAIL → PARTIAL` passes the suite.
- No test imports a real Assurance-produced artifact.
- The claimed 16 tests are actually 15.

## 9. House-convention compliance

- Branch naming: **PASS** — both use `agent/fable/<slug>`.
- Worktrees/cleanliness: **PASS** — both worktrees were clean.
- Conventional Commits: **PASS** — `feat(assurance)`, `feat(product)`, `docs(planning)`, and `docs(contract)`.
- Attribution: **PASS** — Fable commits have `Agent: - fable`; no `Co-Authored-By`.
- Push/upstream: **PASS as far as Git state can establish** — neither branch has upstream configuration or a local remote-tracking counterpart. Git cannot prove a push was never attempted.
- Push/PR/merge: **no evidence of any** in the Fable commit ranges.
- Protected paths: **PASS** — none touched.
- Secrets or `.env`: **PASS** — no secret-like files or credentials were added; placeholder digests are clearly labelled.
- Scope control: **PARTIAL** — implementation stayed within the named repos, but Assurance documentation records a stronger consumer relationship than actually exists.
- Kriterion documentation contract: **FAIL** — the material session did not update `docs/session-log.md`, `docs/project-walkthrough.md`, a dated walkthrough, or report mind-palace/taxonomy status as required by `CODEX.md`.
- Verification entry point: **adequately disclosed** — `verify-project.sh` is absent on the chosen base, and Fable said so.

## 10. Five checks that would falsify “this is a real decision instrument, not just a relabeled research demo”

1. Change an Assurance fixture outcome, recommendation, or economics value and run the documented build commands. If `docs/index.html` does not change automatically, the public “instrument” is a hand-maintained story.
2. Import the real Assurance `2026-09-07T19-31-41Z` FAIL pair after lossless JSON conversion. Require a FAIL summary, an explicit critical item, and preserved source identity.
3. Pair that envelope with an unrelated PASS decision, omit `criticalFailures`, and set `freshness.stale=true`. Every case must refuse or become UNKNOWN/STALE, never summarize PASS.
4. Start a fresh Kriterion run, import Assurance evidence, freeze ledger v2, render the report, and confirm FAIL/UNKNOWN/stale items appear with provenance. Then remove the Assurance repository and repeat rendering from committed documents.
5. Record a funded human decision without an outcome contract and verify rejection; add a valid contract and verify the generated report keeps recommendation, human decision, and later observed outcome separate.

## 11. Required Opus decisions

1. Decide whether V1 requires a true ledger-to-report vertical slice. If not, rename this explicitly as an adapter and static journey prototype.
2. Define the supported contract precisely: JSON versus producer YAML, required fields, valid outcomes, identity binding, and inconsistent-pair behavior.
3. Decide whether the Assurance-side “first external consumer” ADR remains, is downgraded, or waits for a real producer artifact test.
4. Make generated artifacts the homepage’s source of truth, or introduce exhaustive coherence tests for the static page.
5. Restore the source `FAIL` outcome and separate it from its non-gating consequence.
6. Decide whether uncovered fingerprint fields affect the Assurance decision. Do not claim they did unless the decision model says so.
7. Promote timing, headcount ramp, and discount rate into explicit assumptions or narrow the economic-dominance claim.
8. Persist `EvidenceRequest.would_change` or remove the claim that it is already an explicit record.
9. Decide the minimum accountable-human lifecycle evidence required before calling the journey “complete.”
10. Correct the Fable report’s test count, provenance claim, end-to-end claim, and missing mission record before handoff.