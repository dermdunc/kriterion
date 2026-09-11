# Kriterion V1 (Decision Instrument) — Fable stage report

**Loop:** Fable → Codex → Opus (implementation loop, not planning-only)
**Date:** 2026-09-11
**Branches (both local, unpushed, per the git contract):**

- `kriterion`: `agent/fable/kriterion-decision-instrument`, worktree
  `factory-output/kriterion--decision-instrument`, branched from **`origin/main`**
  (`fe1b85b`, the PR #3 merge) — deliberately not local `main` (`6f90cfc`), which is two
  merges stale, and deliberately not `agent/claude/kriterion-subdomain-infra`, whose
  DNS/infra work is unrelated and unmerged.
- `hekton-assurance-lab`: `agent/fable/assurance-consumer-contract-docs`, worktree
  `labs/hekton-assurance-lab--consumer-docs`, branched from `main` (`06a86a2`).
  **Docs-only** (3 files, 23 insertions, zero code).

---

## Phase 0 — what was actually inspected

Everything below was read directly, not assumed: Kriterion's `AGENTS.md`, `README.md`,
`docs/{decisions,architecture,next-actions}.md`, `docs/index.html`, `.hekton/project.yaml`,
the full `src/kriterion/domain/` package, `ledger.py`, `casepack.py`, `cli.py` (head + full
parser wiring), `economics/` outputs, `tests/executors/test_boundary.py`, the committed demo
run `runs/caseA-condC-s0/` (economics, recommendation, positions initial/revised, belief
updates, frozen ledger), and `cases/coding-agent-rollout/{case,injection}.toml`. On the
Assurance side: `README.md`, `docs/architecture.md`, the full ADR log in `docs/decisions.md`,
`src/hekton_assurance/envelope.py` and `decide.py` in full, and the real committed evidence
pair `evidence/2026-09-07T19-31-41Z/{envelope,decision}.yaml` (the real FAIL).

### Kriterion status summary

**What exists (and is much closer to the mission's target than the mission assumes):**

- The full V1 domain vocabulary already exists as tested dataclasses:
  `DecisionCase`, `EvidenceItem` (7 epistemic categories + orthogonal `attestation`),
  `Assumption` (value/range/strength/owner/engine-written sensitivity), `EconomicsResult`
  (NPV triple, payback, tornado, avoided-loss band kept out of NPV), `CommitteePosition`,
  `EvidenceRequest` (**including `would_change`** — the mission's central UX concept is
  already a domain field), `Challenge`, `BeliefUpdate` (with harness-written drift flags),
  `SyntheticRecommendation` (mandatory non-empty dissent), `HumanDecision` (separate type,
  separate file, ADR-006), `OutcomeContract` (measures/baseline/target/review
  date/kill criteria), and the exact ten-state staged decision vocabulary with APPROVE
  deliberately absent.
- Deterministic economics engine (ADR-002), golden-tested; Case A's real numbers:
  NPV −£5.35m / +£5.09m / +£38.1m @10%, tornado led by attribution factor (≈£16.9m swing)
  then uplift (≈£15.7m).
- Governance enforced in code: no-tally-before-synthesis, ledger single write path,
  funding-without-outcome-contract fails validation, recommendation ≠ decision asserted by
  eval P0-09 and rendered separately.
- A complete, committed, real demo run of the committee condition
  (`caseA-condC-s0`): 5/5 seats DEFER initial and revised, CFO confidence LOW→MEDIUM, all
  five belief updates citing the same two ledger items (ev-015, ev-026), recommendation
  DEFER/MEDIUM with two named unresolved unknowns, **no human decision, deliberately**
  (RISK-0011: an agent must not fabricate the accountable human's act).
- 193 passing tests on `origin/main`; ten P0 governance evals; pre-registered comparison
  with an honest-negative result, corrected twice under external review, with the caveats
  (bare-aggregate only; margin and inference-cost sub-conditions unimplemented) carefully
  preserved in copy.

**What was missing (the real gaps this increment addressed or named):**

1. The public experience led with the research methodology, not a decision
   (`docs/index.html` was entirely about conditions A/B/C/D).
2. No assurance-evidence path of any kind: ADR-005 explicitly scoped V0 to "export, not
   contract", and `tests/executors/test_boundary.py` bans any string reference to
   `hekton_assurance`/`hekton-assurance-lab` in `src/`.
3. `EvidenceRequest.would_change` exists as a type but is never persisted as a per-run
   artifact — "what would change your mind" data lives implicitly in blocking unknowns and
   recommendation conditions.
4. README/architecture positioning led with the laboratory identity.

**What must be preserved (and was):** the honest-negative finding and every one of its
disclosed caveats; the committed V0 run artifacts and frozen ledgers (read, never edited);
the em-dash-free editorial standard (2026-09-08 pass); ADR-001/002/003/004/006 boundaries;
the absence of a fabricated human decision.

### Hekton Assurance status summary

**What exists:** a genuinely built V0 (Slices 1–5, 15/15 acceptance criteria): capability
manifest → deterministically compiled contract → real Inspect-run evidence → an
`EvidenceEnvelope` (results[], structured fingerprint with an explicit `uncovered[]` honesty
list, provenance with model digests, sourceState/dependencyState, retention) → a five-state
`AssuranceDecision` with strict precedence (STALE > FAIL > INCOMPLETE > REVIEW_REQUIRED >
PASS) and an anti-laundering `prior-decision-superseded` rule. Two real capabilities
assured, including a real non-self-built target with a real committed FAIL that was not
rerun to make it go away. Marked `v0alpha1 — LAB PROOF, NOT A PUBLIC CONTRACT`.

**What is reusable for Kriterion:** the envelope + decision **document shape** — it is
domain-independent (no investment/committee concepts anywhere in it) and already carries
everything Kriterion's evidence model needs: per-spec method/outcome/detail,
criticalFailures, freshness, coverage gaps, provenance.

**What is missing there:** nothing this mission needs. Its known debts (bespoke per-capability
run scripts, judge calibration, agent-evidence normalization) are its own tracked work and
irrelevant to a document-level consumer.

**Is a cross-repo change justified?** Code: **no** — the correct consumer posture against a
labeled-unstable producer is a tolerant reader plus fixtures on the consumer side.
Docs: **yes, minimally** — the lab's own documentation contract requires meaningful decisions
to be recorded, and acquiring a first external consumer (plus the one implication: bump
`envelopeVersion` on shape-breaking changes) is such a decision. That is the entire
Assurance-side change: 3 docs files, no code, no schema edits, no new obligations.

---

## Gap analysis (mission-required classification)

| Mission element | Classification | Notes |
|---|---|---|
| DecisionCase/Evidence/Assumption/Unknown/Economics/Challenge/BeliefUpdate/SyntheticRecommendation/HumanDecision/OutcomeContract | **Already exists** | Complete, tested domain model; extended nothing, duplicated nothing |
| Staged vocabulary (no APPROVE), staged funding ladder | **Already exists / exists but hidden** | Vocabulary in `enums.py`; ladder was a case-pack comment + report constant → now surfaced on the journey page |
| "What would change your mind" | **Exists but hidden** | `EvidenceRequest.would_change` is a domain field; per-run persistence missing (named follow-up); journey page surfaces the run's real equivalents (blocking unknowns, recommendation conditions) |
| Load-bearing assumptions view | **Exists but hidden** | Tornado computed since V0; now rendered as the journey's section 3 with an insight sentence |
| Economics-as-insight | **Exists but hidden** | Numbers existed; narrative framing added |
| Recommendation ≠ decision UI | **Already exists** (report.html) / **surfaced** on the journey page, honestly showing "not yet recorded" |
| Assurance envelope contract | **Already exists (producer side)** | Reused as a document shape; explicitly not re-invented |
| Kriterion assurance adapter | **Needed implementation** | Built: `src/kriterion/assurance/` + CLI + fixture + 16 tests |
| Homepage-as-decision | **Needed implementation** | Built: `docs/index.html` journey; old page preserved as `docs/lab.html` |
| README/architecture repositioning | **Needed implementation** | Done, honest-negative intact |
| Assurance evidence into a frozen ledger version | **Future / not V1** (this increment) | `assurance import` emits items; folding into a v2 ledger for a *new* run is the named next slice — committed V0 ledgers are research artifacts and were not touched |
| Human decision + outcome contract demo beat | **Future / blocked on a human** | RISK-0011: not fabricatable by an agent |
| Decision retrospective (expected vs observed) | **Future / not V1** | Domain hooks exist (OutcomeContract measures/review date) |
| Longitudinal outcome data system | **Future / explicitly out of scope** | Per mission's own scope discipline |

---

# Final output (mission-required structure)

## What you found

Kriterion V0 is not a prototype needing rescue; it is a small, rigorously governed system
whose domain model already contains essentially every object the V1 thesis needs, including
the ones the mission asks to check for (`would_change`, outcome contracts, staged
vocabulary, dissent preservation). Its actual deficit was **presentation and one missing
integration**: the public story led with the experiment, and there was no way to consume
assurance evidence. Hekton Assurance V0 is genuinely built and self-honest (real committed
FAILs, an explicit uncovered[] list), with an envelope/decision shape that is already
domain-independent and sufficient — but explicitly labeled as having no stability promise.

## Architecture decision

**Kriterion (code + docs) plus Hekton Assurance (docs only).**

- All executable change is in Kriterion, the consumer, as an anti-corruption layer over a
  *document* contract: `envelope.json` + optional `decision.json`, 0.x shape, tolerant
  reader, refuse-don't-guess on a future major version. No `import hekton_assurance`
  anywhere, mechanically enforced (the pre-existing boundary test still passes unchanged in
  logic; its docstring now names the ADR-007 data-document exception).
- Hekton Assurance received a 3-file docs commit recording its first external consumer and
  the single producer-side implication (bump `envelopeVersion` on shape-breaking changes —
  a field its `envelope.py` already owns). No code, no schema change, no Kriterion concept
  introduced. Rationale for touching it at all: the mission's "document the consumer
  contract" requirement plus that lab's own documentation contract; rationale for touching
  nothing else: `v0alpha1` is labeled "not a public contract", and hardening it into one
  from the consumer side would be exactly the boundary violation ADR-005 exists to prevent.

## What changed

**Kriterion** (`agent/fable/kriterion-decision-instrument`, 2 commits + this report commit):

1. `feat(assurance)` — `src/kriterion/assurance/{__init__,adapter}.py` (pure, no I/O beyond
   document loading; epistemic mapping deterministic→MEASURED/HIGH,
   counterfactual→MEASURED/MEDIUM, model-judge→EXPERT_JUDGMENT/LOW,
   error/indeterminate/unrecognised→UNKNOWN/LOW, uncovered[]→UNKNOWN items,
   decision→INFERENCE; hard guards: stale visibly marks + downgrades every item, PASS over
   criticalFailures raises, absent decision → UNKNOWN never PASS, provenance + caller-stated
   attestation on every item); `kriterion assurance import` CLI (lazy import, default
   attestation AUTHORED); authored fixture pair + README under
   `cases/coding-agent-rollout/assurance/` (fictional capability, placeholder digests,
   `digestsCaptured: false`, fixture note inside the JSON); `tests/assurance/test_adapter.py`
   (16 tests incl. a structural works-when-absent test); boundary-test docstring updated.
2. `feat(product)` — `docs/index.html` rebuilt as the decision journey (details below);
   previous research page preserved as `docs/lab.html` with all caveats and its
   honest-negative headline intact; README repositioned to lead with the instrument thesis;
   `docs/architecture.md` V0/V1 identity + assurance boundary; `docs/decisions.md` ADR-007
   and ADR-008 in full; `docs/next-actions.md` V1 section with shipped items and named
   follow-ups.

**Hekton Assurance** (`agent/fable/assurance-consumer-contract-docs`, 1 commit):
`docs(contract)` — ADR row, next-actions reminder (envelopeVersion bump; optional
canonical-JSON sibling emission, explicitly not required), session-log entry.

## Decision journey (the V1 experience as shipped)

A visitor to the site now lands on: **"Should we fund a staged rollout of an enterprise
coding agent to 5,000 engineers?"** — £4.2m staged ask, with a snapshot answering the
mission's ten questions in order: (1) the decision and its alternatives; (2) measured
pilot facts; (3) explicit owned assumptions with ranges and evidence strengths;
(4) the load-bearing attribution assumption (≈£16.9m NPV swing on LOW evidence) called out
as decision-critical; (5) five seats' positions and their convergence; (6) what would
change the decision, on the record (the run's two evidence requirements + the attribution
methodology for the economics); (7) why £0 is committed (the NPV sign flips inside the
stated plausible range; £50k–£470k of evidence-buying vs ~£43m of spread, on the staged
ladder with evidence gates); (8) the synthetic recommendation (DEFER, MEDIUM, preserved
dissent); (9) the human decision — **honestly absent**, with the ADR-006 explanation that
Kriterion will not fabricate it; (10) what an outcome contract would require before any
funding validates. Section 5 shows the assurance evidence (labeled AUTHORED fixture,
REVIEW_REQUIRED, prompt-injection resilience PARTIAL, runtime drift UNKNOWN) landing
exactly on the committee's biggest recorded unknown. Section 9 links to Kriterion Lab,
framed as "Kriterion experiments on its own decision mechanisms"; the Lab page carries the
entire prior research story unreduced. Every number on the page was hand-verified against
the committed artifacts it links to; no run was re-executed and no artifact edited.

Two honest deviations from the mission's illustrative copy, deliberate: the recommendation
shown is the run's real **DEFER**, not the mission's illustrative "FUND £420k PILOT" (the
mission itself forbids rewriting outcomes to look better); and no CFO belief-flip vignette
is shown because none occurred — the real recorded belief update (CFO confidence LOW→MEDIUM
while holding DEFER; all five seats converging on the same two unknowns) is shown instead.

## Assurance boundary

```text
Hekton Assurance (lab)                        Kriterion (factory output)
  EvidenceEnvelope + AssuranceDecision  ──►   envelope.json + decision.json (documents)
  (v0alpha1, YAML, no stability promise)          │  read by src/kriterion/assurance/ only
                                                  ▼
                                            EvidenceItem records (Kriterion domain)
```

Coupled: the 0.x document *shape* (kind, envelopeVersion, capability,
results[].{specId,method,outcome,detail}, criticalFailures, fingerprint.uncovered,
decision.{state,reasons,freshness}). Deliberately uncoupled: everything else — no Python
import in either direction (mechanically tested on the Kriterion side), no shared files, no
Kriterion concept in Assurance, no Assurance internals (compiler, Inspect, extraction,
fingerprint componentry) known to Kriterion, no runtime dependency (Kriterion runs
identically with zero assurance documents, structurally tested), and no stability promise
extracted from the producer beyond "bump envelopeVersion when the shape breaks."

## Validation

- Kriterion worktree, fresh venv (`pip install -e ".[dev]"` + editable
  `platform/hekton-local-llm` for the executor tests): **208 tests passed**
  (193 baseline on `origin/main`, re-run and confirmed before any change; 15 net new — 16
  adapter tests added, with pre-existing tests unmodified except the boundary-test
  docstring). No test was weakened.
- `scripts/check-prereqs.sh`: pass. **`scripts/verify-project.sh` does not exist on
  `origin/main`** — it lives only on the unmerged `agent/claude/kriterion-subdomain-infra`
  branch, so the AGENTS.md-documented entry point cannot run from this branch; the full
  pytest suite + prereqs were used instead. Flagged here rather than silently skipped.
- CLI smoke: `kriterion assurance import cases/coding-agent-rollout/assurance` → 11 items,
  REVIEW_REQUIRED, 3 coverage gaps; `--out` mode writes valid JSON.
- Cross-check against the reference producer (dev-time only, read-only):
  `hekton_assurance.envelope.validate_envelope()` run against the authored fixture returns
  **zero errors** — the fixture genuinely conforms to the producer's own validator, it is
  not merely shaped "close enough" for Kriterion's tolerant reader.
- Both HTML pages parse cleanly; zero em-dashes in the new audience-facing copy (grep-verified),
  matching the repo's 2026-09-08 editorial standard; the canonical
  "SYNTHETIC RECOMMENDATION · NOT A DECISION" banner wording matches `report/html.py`'s.
- Not validated live: no model runs were executed (none were needed — the journey uses
  committed artifacts, per research-integrity constraint), and the GitHub links on
  `docs/index.html` to `cases/coding-agent-rollout/assurance/` point at `blob/main` and will
  404 until this branch merges (the links to `runs/` and `economics.json` resolve today).

## Deferred work

Named in `docs/next-actions.md` (V1 section), deliberately not smuggled into this increment:
per-run persistence of `EvidenceRequest.would_change` as a real artifact + per-seat view;
folding imported assurance items into a *new* run's frozen ledger v2 (never the committed V0
ledgers); the real human-decision + outcome-contract demo beat (requires the accountable
human, RISK-0011); the decision retrospective (expected vs observed); Case B; and on the
Assurance side, the optional canonical-JSON sibling emission. Also inherited and untouched:
the pre-registered margin and inference-cost sub-conditions of the honest-negative criterion
remain unimplemented, exactly as disclosed on both pages.

## Most important remaining product risk

**The instrument has never been exercised by its accountable human on a decision whose
outcome anyone lived with.** Every journey element downstream of the recommendation — the
human decision, the outcome contract, expected-vs-observed, the retrospective — is
structurally enforced but empirically empty: the demo honestly renders "not yet recorded",
and no committed run has ever completed the lifecycle. Until a real person records a real
(even fixture-scale) decision and returns at a review date, the core thesis — that making
evidence, assumptions and uncertainty explicit produces *better human judgment*, not just
better-organised analysis — remains an argument, not evidence. That is the single most
valuable thing a next increment (or simply the repo owner, with `kriterion decide` and
`kriterion contract`) could produce.
