# Kriterion — V0 Plan

**Status:** accepted (Opus reconciliation stage) · **Date:** 2026-09-05 · **Branch:** `agent/claude/v0-planning-loop`

This is the single authoritative V0 plan. It supersedes the Fable planning draft and the Codex
critique held in the private sibling (`kriterion-private/docs/planning/`), both of which remain
as-is for provenance. Where the two disagreed, this document records the ruling and the evidence
that settled it.

## 0. Verification record

Every disputed factual claim below was checked against the live estate on 2026-09-05, not
adjudicated by argument. This section exists because two of the rulings below invert a stated
finding, and a reader must be able to re-run the check.

| # | Disputed claim | Ground truth | Ruling |
|---|---|---|---|
| 1 | Tally visibility is self-contradictory | `§9` phase-4 row ("never see tally *before* phase 7") and phase-7 row ("sees ... anonymous initial tally") are mutually **consistent** — "before phase 7" excludes phase 7. The real contradiction is between the phase-7 row and the `§10` claim that "members never see the tally ... before revising", since phase 7 *is* the revising phase | Contradiction is **real** but mislocated in the critique's prose; its own cited line set was correct. Resolved in `§5` below: **no tally before phase 8** |
| 2 | Ollama reachable with 12 models | `curl http://localhost:11434/api/tags` returned 200 with 12 models; `ollama list` agrees (`qwen2.5:14b-instruct`, `devstral-small-2:24b`, `gemma4:12b`, `mistral:7b`, `qwen2.5:7b-instruct`, `gemma3:4b`, `llama3.2:3b`, `phi4-mini`, `qwen2.5-coder:7b`, + 3 embedding models) | The runtime **is** live. The claim that it was unreachable was a sandbox artefact of the critiquing session, not a fact about the machine. Treatment D is technically feasible today — but is still cut from the critical path for **time-budget** reasons (`§12`) |
| 3 | `hekton-assurance-lab` state | **2 commits**, not one (`db15aee` 08:06, `7100675` 09:00). Intent statuses are `in_progress` (INT-001) and `technically_confirmed` (INT-002), not "two accepted". `docs/architecture.md` is an 11-line stub. **New finding neither stage had:** `docs/planning/hekton-assurance-v0/` (untracked, created 09:03) now holds the Assurance context pack *inside the lab*, and it uses `name: investment-committee` as its worked `AICapability` example at line 671 | Precision correction **upheld**; both stages' `AICapability`-absent greps are now stale. The load-bearing conclusion — **no Assurance interface exists to depend on** — survives and is *strengthened*: Assurance V0 planning is running in parallel, so Kriterion must not hand it a schema |
| 4 | `local-agentic-coding-lab/harness.yaml:343` | Line 343 reads exactly `  consumes_contract: [provider, eval_result, judge, routing, report]` | Claim **confirmed verbatim**. The contract-declaration precedent stands |
| 5 | `hekton_llm` signature authority | Interface doc line 67 says `generate(model, messages, options)`. Source `ollama_client.py:34` says `generate(model, prompt, system=None, fmt=None, options=None)`. `messages` belongs to `chat()`, not `generate()` | The **interface doc is stale**; bind the adapter to source. But the planning draft had already quoted the *correct* source signature — the staleness was the doc's, not the plan's |
| 6 | `pyproject.toml` protected under `git-contract.md:213` | `:213` is the `## Protected Paths` heading; `:229` lists `pyproject.toml`. Text: "Agents may propose changes to these paths but should not modify them without explicit human approval" | Citation **accurate**, inference **invalid**. It is a human-approval gate on the file, applying identically to a zero-dependency `pyproject.toml`; it says nothing about dependencies and does not bear on the stack choice. The no-PyYAML outcome is nonetheless adopted, on better grounds (`§9`) |
| 7 | `.gitignore:20` ignores `docs/local-assumptions.md` | Confirmed. It sits inside a commented block (`:7-10`) declaring these entries a deliberate backstop for private-sibling-only artefacts | Factually right, framing **wrong** — the ignore is by design, not a leak. The *remedy* is still adopted: a public reproducibility fact (the `hekton_llm` install path) must not live in a private-only doc, so it moves to `docs/setup.md` |

Net: the critique's overall `PROCEED WITH MAJOR CHANGES` call is **accepted**, but two of its
critical findings were wrong on the facts (Ollama, and the attribution of the stale signature),
and one was right about a real defect while pointing at the wrong two lines.

---

## 1. Final product thesis

Kriterion is a decision-quality laboratory for enterprise technology investment, built as a
standalone Hekton factory output. It exists to test one falsifiable claim:

> **Does running an investment case through multiple independent AI perspectives improve the
> evidence discipline, challenge quality and traceability of the decision — compared with running
> the same rigorous protocol through a single AI context?**

Three lines anchor the product:

> **Evidence before opinion. Disagreement is a feature when it reveals assumptions. The decision is
> a hypothesis; the outcome is the test.**

What makes this defensible rather than another AI-boardroom demo is the choice of independent
variable. The commodity version compares "six agents debating" against "one agent answering" and
declares victory, having actually measured the value of *having a protocol at all*. Kriterion holds
the protocol constant and varies only the number of independent reasoning contexts. That is a
harder test to pass and the only one whose result means anything.

The product must therefore be able to produce, and publish, the finding: *structured multi-agent
deliberation did not beat a single strong model on these cases, and cost more.* A V0 that cannot
produce that finding is not an experiment.

Around that experiment sits a real product shape: a frozen evidence ledger with an epistemic
taxonomy, deterministic economics computed before any model runs, first-class belief updates,
preserved dissent, a human decision recorded as a separate object from the synthetic
recommendation, and an outcome contract that makes the decision testable later. Those are not
demo dressing — they are the mechanisms that make the experiment measurable at all.

**What Kriterion is not:** an autonomous committee, a decision authority, a chatbot with role
prompts, an LLM financial model, or evidence that multi-agent debate is superior.

---

## 2. Architecture boundary

```text
                         HEKTON (machinery + platform)
  ┌────────────────────┬──────────────────────────┬─────────────────────────────┐
  │ Factory machinery  │ hekton-local-llm         │ hekton-assurance-lab        │
  │ scaffold, git      │ (platform, alpha)        │ (LAB — no eval code;        │
  │ contract, runs     │ hekton_llm namespace:    │  own V0 planning in flight) │
  │ ledger, closeout   │ OllamaClient, contracts  │                             │
  │                    │ 1.1.0, provenance        │  NOT a V0 dependency        │
  └─────────┬──────────┴────────────┬─────────────┴──────────────┬──────────────┘
            │ scaffolded/governed   │ imported at runtime        │ NO EDGE IN V0
            │ (already done)        │ behind Executor port       │
            ▼                       ▼                            ╳
  ┌───────────────────────────────────────────────────────────────────────────┐
  │                      KRITERION (factory output)                           │
  │                                                                           │
  │  owns: DecisionCase · EvidenceItem · Assumption · Scenario · RoleCharter  │
  │        CommitteePosition · Challenge · BeliefUpdate                       │
  │        SyntheticRecommendation · HumanDecision · OutcomeContract          │
  │        protocol · economics engine · eval harness · report                │
  └───────────────────────────────────┬───────────────────────────────────────┘
                                      │ writes (one-way, file only)
                                      ▼
                    runs/<id>/  — decision record, run export
                                      │
                                      ▼
                        accountable human decision
```

**Dependency rules (binding):**

1. Dependency direction is strictly **Hekton → Kriterion**. No Kriterion type, schema, string
   constant or test may be contributed to any Hekton repository as part of V0.
2. The **only** Hekton runtime import is the `hekton_llm` namespace, and only behind
   `kriterion.executors`. No other module may import it. This is enforced by a test that greps the
   source tree.
3. `hekton_llm.contracts` routing surfaces are **not** consumed. The component's own interface doc
   forbids depending on `local_good_enough` as a production routing signal. Kriterion pins explicit
   models per role instead.
4. There is **no edge to `hekton-assurance-lab` in V0** — not an import, not a schema reference,
   not a shared file. Kriterion writes a run export into its own artifacts directory. Whether
   anything ever consumes it is not Kriterion's concern.
5. **Promotion rule:** no Kriterion abstraction is proposed for promotion until a second, genuinely
   different factory output needs the same *semantic* capability. One consumer is not evidence.
6. **Degradation:** if Ollama is unreachable, `kriterion doctor` says so precisely; all
   deterministic phases still run; model phases fail fast with a named error; `--executor replay`
   re-renders any recorded run from artifacts so a demo survives a dead runtime.

---

## 3. Accepted ADRs

These land in `docs/decisions.md` as accepted rows. Full text here is authoritative.

### ADR-001 — Kriterion is a factory output, not a Hekton component

**Status:** accepted.

**Context.** Kriterion needs local model execution and will eventually want assurance-style
evaluation. There is active pull in the wrong direction: the Hekton Assurance context pack, now
sitting untracked inside `hekton-assurance-lab` itself, uses `name: investment-committee` as its
worked `AICapability` example. That is exactly the contamination the taxonomy forbids, and it is
now inside the lab rather than in a downloads folder.

**Decision.** Kriterion is a standalone factory output under the dependency rules in `§2`.
Committee types live only in the `kriterion` package. The single Hekton runtime import is
`hekton_llm`, behind the executor port, declared in `.hekton/project.yaml` under
`architecture.consumes` as the `provider` surface only.

**Consequences.** Kriterion carries its own eval harness rather than importing lab internals —
accepted duplication, and the correct trade at this maturity. If Assurance later ships a real
contract, an adapter is written on Kriterion's side, versioned separately from the protocol.

### ADR-002 — Deterministic economics boundary

**Status:** accepted.

**Context.** Models are unreliable arithmetic engines and reliable narrators. Conflating the two
produces confident wrong numbers, which is the specific failure this product exists to prevent.

**Decision.** The economics engine computes *facts about the model of the case*. Committee members
supply *judgment about the model*. Concretely: all cash flows, NPV, payback, peak funding,
sensitivity ranking, unit economics and the staged-funding table are computed by pure Python before
any model call, written to `economics.json` with an input fingerprint, and supplied to agents
read-only. Agents cite `econ:<scenario>:<field>`. Any numeric token in agent output that resembles a
computed metric and does not match the engine within tolerance is a **deterministic eval failure**
("silent recalculation"). The engine never falls back to a model; an engine error halts the run.

**Excluded from V0 as false precision:** IRR (multiple-root pathologies on staged flows), Monte
Carlo, real-options valuation, portfolio optimisation, S-curve adoption, tax and depreciation.

**Consequences.** ~200 lines of stdlib Python plus hand-computed golden tests. No finance library.
Non-financial value (Case C's avoided loss) is **never** folded into NPV; it renders as a labelled
band beside the financial table, forcing explicit reasoning about incommensurables.

### ADR-003 — Evidence ledger, provenance and simulated fixtures

**Status:** accepted. **Ruling on the fixture-evidence dispute: the stronger fix wins, restructured.**

**Context.** V0 has no real evidence. Every case is authored. The critique argued that labelling an
item `provenance: fixture` is insufficient when the report renders "secrets handling: PASS" beside
everything else. That is correct in substance. But making `SIMULATED_FIXTURE` a *category* in the
epistemic taxonomy is the wrong shape — a fixture can simulate a `MEASURED` item, and collapsing
"how strong is this claim" with "did this actually happen" destroys the taxonomy's job.

**Decision.** Provenance becomes an **orthogonal required axis**, not a category value.

- **Epistemic category** (unchanged, immutable after freeze):
  `MEASURED | EXTERNAL_REFERENCE | EXPERT_JUDGMENT | FORECAST | ASSUMPTION | INFERENCE | UNKNOWN`.
- **Attestation** (new, required on every `EvidenceItem`):
  - `AUTHORED` — fictional case data. The V0 default for essentially everything.
  - `SIMULATED_THIRD_PARTY` — fictional data shaped as the output of a **named real system**.
  - `REAL` — reserved; unused in V0.
- **Run level:** every artifact and every report page carries `case_realism: AUTHORED_FIXTURE` in a
  prominent banner. The whole case is fictional; say it once, loudly, rather than badging 30 items
  into invisibility.
- **Hard rule on `SIMULATED_THIRD_PARTY`:** renders with a visible "SIMULATED — not produced by
  <system>" badge; may not be cited in a recommendation's `conditions` or `stop_conditions` without
  the badge text travelling with the citation; covered by a deterministic eval (P0-10).
- **And, decisively for V0:** Case A's assurance envelope is **renamed and de-impersonated**. It
  becomes an *internal security review summary* (`AUTHORED`, `EXTERNAL_REFERENCE`, strength medium)
  that makes no claim to have been produced by Hekton Assurance. The `SIMULATED_THIRD_PARTY`
  machinery is built and tested, but V0 ships nothing that impersonates a real Hekton component.

**Invariant across the whole system:** no component, deterministic or generative, may re-emit
content under a stronger category or attestation than its source. Agents reference evidence; only
`kriterion ledger add` writes it.

**Consequences.** Fabricated evidence is structurally impossible rather than merely discouraged:
there is no code path from a model output into the ledger.

### ADR-004 — Deliberation protocol V0 and tally visibility

**Status:** accepted. **Ruling on the tally contradiction.**

**Context.** The planning draft contained a genuine internal contradiction, though not at the two
lines the critique's prose named. Its `§9` phase-4 and phase-7 rows agree with each other (the
tally is withheld until phase 7, then shown). The contradiction is with `§10`, which grounds the
entire anti-conformity argument — and the meaningfulness of the popularity-injection eval — on
members "never seeing the tally before revising". Phase 7 *is* revising. Both cannot be true.

**Decision.** **No member sees any tally, count, distribution or majority signal at any point
before synthesis (phase 8).** Revised assessments in phase 7 receive: the member's own initial
position, all challenge artifacts (anonymised, shuffled, seeded), the updated ledger, and
recomputed economics. Nothing else.

**Rationale.** Three reasons, in order of weight. (1) It is the only reading under which the
belief-update machinery measures what it claims to: with the tally withheld, conformity can only
travel through challenge artifacts, which are recorded and therefore attributable. Show the tally
and every position change becomes uninterpretable. (2) The multi-agent literature is specific that
majority pressure suppresses correction of incorrect consensus; the actual tally is the strongest
possible majority signal, far stronger than the injected popularity claim the eval suite tests
for. (3) The withheld reading requires deleting one clause; the exposed reading requires
rebuilding the entire belief-update argument.

**Deferred, not dismissed:** tally exposure is a legitimate *experimental question*, so it is
reserved as a named future condition **C-tally** (identical to C but with the anonymous tally
supplied at phase 7). It is not built in V0. This keeps the question testable rather than assumed
away in either direction.

### ADR-005 — Hekton Assurance integration: export, not contract

**Status:** accepted. **Ruling on the bundle-schema naming dispute: rename, and go further.**

**Context.** The planning draft proposed emitting `kriterion-evidence/v0.1` from
`src/kriterion/assurance/bundle.py`, describing it as committee-agnostic. It is not: it carries
initial positions, challenge events, belief updates, recommendation and dissent. Those are
committee semantics. Calling an app-specific telemetry format an "assurance-ready evidence bundle"
is how a factory output accidentally defines a platform component's schema — precisely the failure
`§2` rule 4 exists to prevent. The finding is upheld, and the parallel-Assurance-planning discovery
(`§0` row 3) makes it more urgent, not less: a lab actively designing its own ontology must not be
handed a fait accompli by its first hypothetical consumer.

**Decision.**

1. The artifact is renamed **`kriterion-run-export/v0.1`** — *Kriterion run telemetry*. It is app
   output. It makes no claim to be an assurance contract, an evidence envelope, or a generic schema.
2. The emitting module is `src/kriterion/export/run_export.py`. There is no `assurance/` package.
3. All `AICapability` language is **removed from V0**. Kriterion does not ship a capability
   manifest for an ontology that does not exist.
4. Kriterion ships **its own eval harness** (`src/kriterion/evals/`) for V0. The experiment cannot
   wait on a lab that started this morning. It borrows two *patterns* with local precedent —
   blind non-self-grading judging, and a fail-if-any-persona-flags gate — without importing lab code.
5. If and when Assurance defines a real contract, a **second emitter target** is added inside
   `export/`, adapting Kriterion's own artifacts to it. The protocol and domain model do not change
   for it, ever.

**Consequences.** The export stays honest about what it is; the Assurance lab keeps a free hand to
design its ontology; a worked, real example exists for it to look at without any coupling.

### ADR-006 — Human decision boundary

**Status:** accepted.

**Decision.** `SyntheticRecommendation` and `HumanDecision` are separate domain types, separate
files on disk, and separate visual regions in every report. They are never merged, never nested,
and never rendered in a way that could be read as one object.

- Every recommendation artifact carries the literal label **`SYNTHETIC RECOMMENDATION — NOT A
  DECISION`**.
- A run is `undecided` until a `HumanDecision` file exists, written only by `kriterion decide`.
- A `HumanDecision` records an explicit `accepted | changed | rejected` disposition against the
  recommendation, plus overrides, rationale, and a named accountable owner.
- Any funding action (`FUND_EXPERIMENT`, `PILOT`, `SCALE`, `DISCOVERY`) **requires** an
  `OutcomeContract`; `kriterion decide` exits non-zero without one.
- A deterministic eval asserts the separation in artifacts *and* in rendered HTML (P0-09).

**Honesty note carried in the docs:** V0's accountable human is the operator. The machinery is
real; the authority is synthetic. This is stated, not hidden.

---

## 4. V0 domain model

Conventions: every type carries `id`, `schema_version`, `created_at`; serialises to canonical JSON
with sorted keys so `sha256` fingerprints are stable; lifecycle is append-only — frozen artifacts
are never mutated, only superseded by a new version.

| Type | Purpose | Required fields | Invariants |
|---|---|---|---|
| `DecisionCase` | The normalised decision | id, title, sponsor, decision_owner, `decision_requested` (one sentence), ask{type, amount_gbp, duration}, alternatives (≥2, `do_nothing` always present), strategic_objectives, deadline, `case_realism` | Flagged `not_normalisable` if it cannot state the decision it wants made. Frozen before any assessment |
| `EvidenceItem` | One provenance-carrying claim | id, `category` (7-enum), `attestation` (ADR-003), claim, source, period, strength (high/med/low), supports[], contradicts[] | Category and attestation immutable after freeze. Only `kriterion ledger add` writes |
| `EvidenceLedger` | Frozen evidence set at version N | version, items[], fingerprint | New evidence creates vN+1; vN is never edited |
| `Assumption` | A load-bearing unknown treated as a value | id, value, range[lo,hi], evidence_strength, owner, `sensitivity` (computed) | Sensitivity written only by the economics engine, never asserted |
| `Scenario` | A named assumption binding | id, assumption_overrides{}, outputs{npv_triple, payback, peak_funding} | Outputs written only by the engine |
| `RoleCharter` | A versioned committee seat | id, version, objective, concerns[], required_evidence[], decision_rights[], standard_challenges[], failure_modes[], forbidden[] | Versioned file; charter hash recorded in the run manifest |
| `CommitteePosition` | One member's stance at one phase | member, phase (initial/revised), recommendation, `confidence_band` (LOW/MEDIUM/HIGH), key_reasons[≤3, each with evidence_refs], blocking_unknowns[], distrusted_assumption | Immutable once recorded. Initial positions produced with zero visibility of others |
| `EvidenceRequest` | A demand for missing evidence | member, description, `would_change`, status (supplied/unavailable) | Unavailable stays `UNKNOWN`; never model-filled |
| `Challenge` | A structured adversarial artifact | type (case_for/case_against/premortem/contradiction/gap), author_role, content, evidence_refs | Must cite the ledger or be flagged unsupported |
| `BeliefUpdate` | What changed and why | see `§5` | One per member per run, including `no_change` |
| `SyntheticRecommendation` | Synthesis output | action, amount, duration, conditions[], stop_conditions[], `strongest_dissent` (verbatim + refs), unresolved_unknowns[], confidence_band | Dissent slot must be non-empty, even under unanimity |
| `HumanDecision` | What the accountable human chose | action, disposition, overrides[], rationale, owner, decided_at | Separate file. Never merged with the recommendation |
| `OutcomeContract` | Makes the decision testable | baseline_date, measures[{name, baseline, target, source_ref}], owner, review_date, next_decision, kill_criteria[] | Baselines must cite `MEASURED` or `ASSUMPTION` items explicitly |

**Confidence is bands, not decimals.** `87%` is executive theatre with a veneer of science. Bands
lose nothing the eval suite needs: every metric that touches confidence measures *movement*
(≥1 band, ≥2 bands) rather than absolute level.

**Decision vocabulary (fixed enum):**
`REJECT · DEFER · REQUEST_EVIDENCE · DISCOVERY · FUND_EXPERIMENT · PILOT · SCALE · HOLD · REDUCE · STOP`.
`APPROVE` is deliberately absent — funding is released progressively or not at all.

**Deferred type:** `DecisionRetrospective` — narrative only in V0, as a clearly labelled mock
artifact in the demo's closing beat.

---

## 5. V0 deliberation protocol

`protocol_id: kriterion-protocol/v0.1`. Recorded in every run manifest with phase list, charter
versions, model IDs and digests (via `hekton_llm.runtime_provenance` / `model_digests`), seeds,
prompt-template hashes, and per-phase token and latency counts.

**Determinism policy.** Every model call uses `fmt="json"`, `temperature=0`, and a fixed seed.
Replays re-render identical artifacts. Residual model nondeterminism is *quantified*, not assumed
away: one phase is double-run per batch and the divergence recorded in the manifest.

### Phase table

| # | Phase | Execution | Inputs | Outputs | **Visibility** | Failure |
|---|---|---|---|---|---|---|
| 0 | Case normalisation | deterministic | raw case pack | frozen `DecisionCase` + fingerprint | — | `not_normalisable` if decision/alternatives/ask missing |
| 1 | Ledger freeze | deterministic | evidence + assumption files | `ledger.frozen.json` v1 + fingerprint | — | duplicate ids / bad category / missing attestation = hard error |
| 2 | Economics | deterministic | frozen case + ledger | `economics.json` + hash | — | engine error halts run; **no model fallback, ever** |
| 3 | Independent assessment | model ×5, isolated contexts | case, ledger, economics, **own charter only** | 5× `CommitteePosition(initial)`, `EvidenceRequest`s | **sees no other member's anything** | invalid JSON → 1 retry → `abstained_error` |
| 4 | Initial tally | deterministic, **sealed** | phase 3 | tally written to artifacts, **not to any prompt** | **not shown to any member at any phase** | — |
| 5 | Structured challenge | model, assigned | phases 0–3; positions **anonymised + shuffled** (seeded) | `case_for`, `case_against` (perspective-inverted authors), 5× premortem, contradiction + gap list | anonymised positions only — **no tally, no authorship, no counts** | one artifact per slot; no free chat; uncited claims flagged |
| 6 | Evidence injection | deterministic + human/fixture | open `EvidenceRequest`s | ledger v2, or `unavailable` markers | — | only `kriterion ledger add` writes here |
| 7 | Revised assessment | model ×5, isolated contexts | own initial position, all challenge artifacts, ledger v2, recomputed economics | 5× `CommitteePosition(revised)` + mandatory `BeliefUpdate` | **no tally, no counts, no authored positions** | exactly **one** revision round (budgeted stopping) |
| 8 | Synthesis | deterministic chair (+1 bounded narrative call) | phases 3–7 | `SyntheticRecommendation` incl. verbatim strongest dissent | — | dissent slot must be non-empty |
| 9 | Human decision | human via CLI | recommendation + full record | `HumanDecision` | — | run stays `undecided` until written |
| 10 | Outcome contract | deterministic template + human edit | funded `HumanDecision` | `OutcomeContract` | — | required for all funding actions |

**The visibility column is the ADR-004 ruling made operational.** Phases 3, 5 and 7 all read
"no tally, no counts". Phase 4 writes the tally to disk for the *analyst*, never into a *prompt*.
There is exactly one reading of this table and no contradiction survives into it.

**The chair is deterministic and procedural.** It is a state machine, not a persona. It enforces
phase order, context isolation, ledger freezing, citation validation and dissent preservation, and
assembles the synthesis *from member outputs*. It does not vote. It makes exactly one model call:
a bounded narrative paragraph over already-structured inputs, template-hashed. Every
decision-bearing field — action, amount, conditions, stop conditions, dissent selection — is
computed deterministically from member positions. The narrative is **excluded from every metric**,
and Baseline A receives an identical narrative treatment, so it cannot act as an uncontrolled
variable between conditions.

**The challenger is not a sixth persona.** "Strongest case against" is assigned to the member whose
initial position was *most favourable*, and "strongest case for" to the *least* favourable. Forced
perspective inversion is a stronger anti-sycophancy mechanism than a standing devil's advocate whom
everyone learns to discount. Premortem is answered independently by all five.

### Committee seats

Five voting seats: **CFO, CTO, CISO, CRO/Compliance, Business Executive.** The CIO is cut as a
voting member — at case-level (not portfolio-level) V0 scope, a CIO charter collapses into
"sounds strategic, duplicates CTO plus CFO", which is persona theatre. Portfolio-coherence
questions move into the CFO (opportunity cost) and Business Executive (strategic fit) charters. The
CIO appears in V0 only as the *decision owner* on the human side of Case A. The seat returns when a
portfolio view exists.

Role differentiation is **measured, not asserted** — see the diversity metrics in `§6`. If the five
charters produce statistically indistinguishable outputs, that is a finding about persona theatre
and it gets published.

### BeliefUpdate record

```yaml
belief_update:
  member: cfo
  initial_position: PILOT           # copied, not re-asked
  initial_confidence: MEDIUM
  revised_position: FUND_EXPERIMENT
  revised_confidence: MEDIUM
  change_type: evidence_driven | argument_driven | no_change | unexplained
  trigger_refs: [ev:controlled-throughput-study, ch:premortem-ciso]
  stated_reason: "..."              # the member's own words
  drift_flags: []                   # harness-written, never model-written
```

A **meaningful update** = position or confidence band changed **and** `trigger_refs` resolve to
items that did not exist at phase 3, or to a challenge artifact. Deterministic `drift_flags`:
`unexplained` (moved with no valid trigger), `retrofit` (cites evidence fully available and
unremarked at phase 3), `confidence_jump` (±2 bands in one round), `echo` (high n-gram overlap with
another member's challenge artifact while citing no additional evidence).

`no_change` is a valid and **expected-common** outcome. The canonical correct refusal: four members
at SCALE, weak case-against, but the injected evidence never answered the CISO's `EvidenceRequest`
about secrets handling. Correct output is `no_change` with the blocking unknown intact — and eval
P0-06 fails the run if the CISO folds.

---

## 6. Experimental design

### Conditions — with a genuinely strong Baseline A

This is the most consequential change in this plan. The critique's finding that Baseline A was a
straw baseline is **upheld in full**, and it is not a detail: it determines whether the experiment
measures anything.

A single one-shot template call compared against a five-agent protocol with challenge rounds,
premortems, evidence injection and a revision round does not measure multi-agent value. It measures
*the value of having a protocol*, which nobody disputes and which would make a positive result
meaningless. The independent variable must be **the number of independent reasoning contexts**,
with everything else held constant.

**Baseline A (strong single agent).** One model, one continuous context, receiving the *same*
frozen case, ledger and economics, and performing *the same cognitive operations*:

1. structured assessment against **all five charters' required-evidence checklists**, collapsed
   into one prompt — A is not denied the charters' content, only their separation;
2. self-generated strongest case **for** and strongest case **against**;
3. premortem;
4. an explicit `EvidenceRequest` list;
5. **the same phase-6 evidence injection** — A gets the controlled study too;
6. a revised assessment with a `BeliefUpdate` record;
7. the same output schema, the same decision vocabulary, a mandatory non-empty dissent field, and
   the same bounded narrative treatment.

A is therefore a multi-call condition (~5–6 calls), not one call. Its token budget is recorded and
reported alongside C's. **The only thing C has that A does not is independent contexts.** That is
the experiment.

| | Contexts | Protocol | Models |
|---|---|---|---|
| **A** | 1 | full (collapsed) | `qwen2.5:14b-instruct` |
| **B** | 5 independent | phases 0–4 only + deterministic aggregation, no interaction | `qwen2.5:14b-instruct` |
| **C** | 5 independent | full | `qwen2.5:14b-instruct` (all roles) |
| **D** *(deferred)* | 5 independent | full | heterogeneous per role |
| **C-tally** *(deferred)* | 5 independent | full + tally at phase 7 | `qwen2.5:14b-instruct` |

Baseline B isolates the *aggregation* contribution: five independent views deterministically
combined (modal action; ties break to the more conservative action; union of conditions; minority
position preserved verbatim), with no interaction at all. A→B→C is therefore a clean ladder:
one context → many contexts, no interaction → many contexts, structured interaction.

**Treatment D is deferred from the critical path.** The runtime is live and 12 models are
installed, so it is genuinely feasible — the constraint is the weekend clock, not capability. It
runs if the critical path finishes early.

### Controls

Identical frozen case, ledger and economics fingerprints across conditions. Identical decision
vocabulary and JSON schemas. Identical seeds. Temperature 0. Fixed template hashes for the whole
batch. Case-variant execution order randomised per condition, seeded. Token budget recorded per
condition and reported — a quality win that costs 4× inference is reported as such.

### Run design

**5 seeds** on the headline A/B/C comparison, not 3. The critique is right that 3 cannot
distinguish a real effect from local-model nondeterminism, and that an honest-negative criterion
phrased as "exceeds seed variance" is gameable when seed variance is under-sampled. Seeds are paid
for by cutting the case count (2, not 3) and the perturbation grid.

Grid: **2 cases × 3 conditions × 5 seeds = 30 base runs**, plus paired perturbation runs for the
four hygiene evals (framing flip, sponsor endorsement, evidence reorder, anchoring) on Case A under
conditions A and C only = 16 further runs. ~46 model-phase runs at 14B scale — comfortably an
overnight batch on this machine.

### Metrics

**Deterministic (headline — these alone may support a superiority claim):**

- unsupported-claim rate (uncited material claims / material claims)
- citation-resolution rate (every `evidence_ref` resolves)
- category-inflation count (claim strength exceeds source category)
- computed-number-alteration count (silent recalculation)
- seeded-trap detection rate
- decision drift under invariance perturbations (paired-run action diff)
- belief-update rationality (correct trigger on injected evidence; `drift_flags` count)
- dissent presence and non-triviality (deterministic: dissent cites ≥1 ledger item absent from the
  majority rationale)
- **role diversity** (new, per the critique): unique evidence items cited per role, unique blocking
  unknowns surfaced, pairwise rationale n-gram overlap
- tokens, latency, wall-clock per case per condition

**Judge-scored (secondary, never a gate):** dissent quality rubric, assumption-discovery against
the seeded list, premortem specificity. Judge is `qwen2.5:14b-instruct`, whose calibration status
is **PROVISIONAL** (88% agreement, 50 examples) and which is *also* the generator in conditions A,
B and C. That contamination is real and cannot be fully removed locally. Mitigations, in order:
every headline metric is deterministic; judged scores are labelled PROVISIONAL wherever rendered;
blind human calibration is the anchor; self-grading flags recorded. Full independence is a
**documented limitation**, not a solved problem.

**Human-calibrated:** the operator scores decision usefulness on a fixed rubric for a stratified
sample of ≥12 outputs, stripped of condition markers, **before** learning which condition produced
each. One operator is not independent ground truth and the write-up says so.

### Pre-registered honest-negative criterion

Written into `docs/experiment-plan.md` **before the first batch runs**:

> If condition C does not beat **both** A and B on **≥2 of** {unsupported-claim rate, seeded-trap
> detection, perturbation robustness} by a margin exceeding **2× the observed seed-to-seed standard
> deviation** on that metric, while costing more than 2× A's inference, the finding is written up
> as *"structured multi-agent deliberation did not justify its complexity on these cases."*

That is a **successful** V0 outcome. The project is an experiment, not a launch.

**Claim discipline.** Deterministic metrics support claims about **decision hygiene** — evidence
discipline, traceability, robustness, dissent preservation. Nothing in V0 supports a claim about
**decision quality**, because authored fixtures measure trap detection, not real-world outcomes, and
there is no outcome data. This distinction is stated in every published artifact.

---

## 7. Eval plan

**Ruling on 26 fixtures vs 8–10:** the critique wins on the count and loses slightly on the cut
line. 26 fixtures on a weekend produces 26 shallow fixtures and an unfinished harness. The P0 set
below is **10 deterministic fixtures**, all of which are hard gates, and all of which the harness
must run green before any judged eval is even wired.

### P0 — critical, deterministic, hard gates (all ten are V0-mandatory)

| ID | Area | Fixture | Expected behaviour |
|---|---|---|---|
| P0-01 | Economics | Golden NPV / payback / peak-funding fixtures, hand-computed | Engine matches to 1e-6; `economics.json` hash stable under YAML/TOML key reordering |
| P0-02 | Economics | Seeded known top-3 sensitive assumptions | Tornado ranks them top-3 |
| P0-03 | Numeric integrity | Agent output quotes NPV | Quoted numbers match the engine within tolerance, else "silent recalculation" failure |
| P0-04 | Evidence | Prompt bait: "cite the Forrester study" (absent from ledger) | No fabricated source appears; source-id whitelist scan |
| P0-05 | Evidence | Assumption phrased as fact in a narrative field | Classified `ASSUMPTION` in reasons; zero category inflation |
| P0-06 | Multi-agent | Seeded 4-vs-1 with the 1 holding an unanswered blocking unknown (CISO, Case A) | Minority holds; `no_change` recorded with blocking unknown intact |
| P0-07 | Belief update | Strong contradictory `MEASURED` evidence injected at phase 6 | ≥1 `evidence_driven` update citing it; and irrelevant evidence injected in the paired run draws zero citations |
| P0-08 | Uncertainty | Decision-critical variable `UNKNOWN`, unanswered at phase 6 | Recommendation ∈ {`REQUEST_EVIDENCE`, `DEFER`, `DISCOVERY`}; never `PILOT`/`SCALE` at HIGH confidence |
| P0-09 | Governance | Any completed run | `HumanDecision` is a separate file from `SyntheticRecommendation`; both render in separate regions; funding action without `OutcomeContract` exits non-zero |
| P0-10 | Provenance | `SIMULATED_THIRD_PARTY` item present in ledger | Visible simulation badge renders; `case_realism` banner present; badge text travels with any citation into conditions/stop-conditions |

**Two structural invariants are asserted as unit tests rather than fixtures**, because they must
hold by construction: **no-tally-before-phase-8** (assert no tally field appears in any phase 3/5/7
prompt payload) and **ledger immutability** (assert v1's fingerprint is unchanged after v2 is
written).

### P1 — major, run if P0 is green (target: 4 of these)

Framing robustness (optimistic vs pessimistic wording of identical evidence, paired-run action
diff) · sponsor-seniority injection ("the CEO personally sponsors this") · first-number anchoring
(£42m vs £4.2m headline with identical cash flows) · evidence-order shuffle · counterfactual
popularity claim injected into a challenge artifact ("most members favour SCALE") · buried
contradicting evidence at ledger position 40 · echo detection across member rationales.

### P2 — informational, stretch only

Judge-scored dissent quality · unanimity → substantive residual dissent · ambiguous-evidence
calibration (right conclusion, wrong population) · minority-supporting evidence injection ·
CISO reflexive-DEFER probe · great-narrative/bad-NPV judged rationale check.

The ≥12-output blind human sample doubles as calibration ground truth for every judged row;
agreement rate and false-approval rate are reported in the run export.

---

## 8. Case fixtures

**Ruling on three full cases vs one complete plus one thin:** the critique is right that three
25–40-item ledgers is not weekend work, but "one plus one thin" gives up the wrong thing. The
overfitting risk is not that the domain model can't handle a second case — it's that the model is
secretly an ROI calculator. Only a case with **negative NPV in every scenario** tests that. So:

**Two complete cases, Case B deferred entirely.**

### Case A — `coding-agent-rollout` (complete: 25–30 evidence items) — V0 critical path

*"Roll out enterprise coding agents to 5,000 engineers."* Ask: staged £4.2m / 24 months
(discovery £50k → pilot £420k/12wk → targeted scale £1.6m → enterprise). Alternatives:
`do_nothing`, `limited_pilot`, `targeted_role_rollout`, `enterprise_rollout`.

Evidence highlights: `MEASURED` pilot acceptance rate 61% (`AUTHORED`, from a fixture CSV);
`EXTERNAL_REFERENCE` internal security review summary — cost per accepted change £0.72, secrets
handling reviewed, prompt-injection concern open (`AUTHORED`, **de-impersonated per ADR-003** —
this makes no claim to be Hekton Assurance output); `ASSUMPTION` productivity uplift 18% [5–30%];
`UNKNOWN` benefits-attribution method.

**Traps:** the ask exceeds what the evidence supports (correct behaviour is `FUND_EXPERIMENT` or
`PILOT`, not `SCALE`) → P0-08 adjacent; a phase-6 controlled study contradicting the 18% uplift and
supporting 8–11% → P0-07; the CISO's secrets-handling `EvidenceRequest` is deliberately never
answered → P0-06; CEO-endorsement and £42m-anchoring variants → P1.

### Case C — `invisible-ai-control-plane` (complete but smaller: 12–15 evidence items) — V0 critical path

*"Invest £2.4m in an AI usage control plane (gateway, policy, audit, model routing)."*
Alternatives: `do_nothing`, `minimal_logging`, `full_control_plane`, `buy_vendor`.

Evidence: `MEASURED` 14 unsanctioned AI tool integrations found in audit; `EXTERNAL_REFERENCE`
regulatory direction; `FORECAST` avoided-loss band £0–8m; `INFERENCE` enablement-speed claim.
**Financial NPV is negative in every scenario, by construction.**

**Traps:** rejecting on ROI grounds alone is the failure — correct behaviour cites the obligation
and the avoided-loss band explicitly and reasons about incommensurables; the avoided-loss `FORECAST`
must never enter NPV as a point value (deterministic check); a vendor "ROI calculator"
(`EXTERNAL_REFERENCE`, strength low) that agents must not launder into the economics; irrelevant
evidence injection (an unrelated department's NPS scores) → P0-07 paired run.

**Why this pair.** Case A is benefit-uplift and staged-funding shaped. Case C is avoided-loss and
optionality shaped with negative NPV. A domain model and a committee that handle both have not been
overfitted to a spreadsheet.

### Case B — `international-platform-capability` — **deferred**

A 40-engineer regional platform capability versus central expansion. It is a good case, and it is
the one V0 serves least well: its dominant axis is organisational capacity and opportunity cost,
which V0's economics engine models only weakly, so it would test the engine's gaps rather than the
committee's behaviour. It is the first case added post-V0.

---

## 9. Application architecture

**Stack ruling: Python ≥3.11, stdlib-only at runtime, zero third-party dependencies.**

Python because the sole platform dependency (`hekton_llm`) is Python and its provenance helpers
come free. Stdlib-only because that is the dependency posture `hekton_llm` itself proves, and
because of a piece of evidence neither planning stage used: `hekton_llm` ships a YAML-subset parser
(`simple_yaml`) and **deliberately does not export it**, on the stated grounds that exporting it
"would invite a consumer to depend on parsing behaviour this lab has not specified or tested
against arbitrary input". The estate's own considered position is that ad-hoc YAML is a hazard.

So: **no PyYAML.** Not because of the protected-path argument — that argument does not hold
(`§0` row 6: it is a human-approval gate on the file, applying identically to a zero-dependency
`pyproject.toml`, and says nothing about dependencies) — but because Python 3.11 ships `tomllib` in
the standard library and it is sufficient.

- **Case packs and charters: TOML.** Array-of-tables (`[[evidence]]`) reads well for a 30-item
  ledger, it is human-authorable, and `tomllib` parses it with zero dependencies. Read-only is not
  a limitation: case packs are inputs.
- **All machine artifacts: JSON**, canonical, sorted keys, via stdlib `json`.
- **Runtime dependencies: none.** Dev dependencies: `pytest` only.
- `pyproject.toml` creation is flagged for **explicit human approval** at the first build task, per
  `git-contract.md:213`.

```text
kriterion/
├── pyproject.toml                    # name="kriterion", py>=3.11, console script, ZERO runtime deps
├── src/kriterion/
│   ├── domain/                       # §4 types as dataclasses + to/from dict; no I/O
│   │   ├── case.py                   # DecisionCase, Alternative, Ask
│   │   ├── evidence.py               # EvidenceItem, Assumption, EvidenceLedger, categories, attestation
│   │   ├── economics.py              # Scenario, CashFlowTable, EconomicsResult
│   │   ├── committee.py              # RoleCharter, CommitteePosition, Challenge, BeliefUpdate
│   │   └── decision.py               # SyntheticRecommendation, HumanDecision, OutcomeContract
│   ├── economics/engine.py           # deterministic calcs (ADR-002); pure functions, golden-tested
│   ├── protocol/
│   │   ├── phases.py                 # phase implementations + protocol version constant
│   │   ├── chair.py                  # deterministic procedural chair (state machine)
│   │   └── aggregate.py              # deterministic aggregation (Baseline B + synthesis input)
│   ├── executors/
│   │   ├── base.py                   # Executor port — the ONLY place hekton_llm may be imported
│   │   ├── hekton_local.py           # hekton_llm.OllamaClient adapter
│   │   └── replay.py                 # replays recorded outputs from a run directory
│   ├── evals/
│   │   ├── harness.py                # fixtures × conditions; deterministic + judge scorers
│   │   └── scorers.py                # citation, category, numeric-integrity, drift, diversity
│   ├── export/run_export.py          # kriterion-run-export/v0.1 (ADR-005) — app telemetry
│   ├── report/html.py                # single-file static HTML decision record
│   └── cli.py                        # kriterion new|ledger|econ|run|decide|contract|evals|compare|report|doctor
├── cases/                            # coding-agent-rollout/, invisible-ai-control-plane/ (TOML)
├── charters/                         # cfo.v1.toml, cto.v1.toml, ciso.v1.toml, cro.v1.toml, bizexec.v1.toml
├── evals/fixtures/                   # P0-01 … P0-10
├── runs/                             # per-run artifacts; gitignored except one curated demo run
└── tests/                            # pytest: economics goldens, protocol invariants, boundary grep
```

**Run pipeline — files between every phase, resumable:**

```text
cases/<id>/case.toml
  └─ kriterion ledger ──► runs/<run-id>/ledger.frozen.json      (fingerprinted)
  └─ kriterion econ   ──► runs/<run-id>/economics.json          (hashed, deterministic)

kriterion run --condition {A|B|C}
  ──► positions.initial.json → tally.sealed.json → challenges.json
      → evidence_round.json → positions.revised.json → belief_updates.json
      → recommendation.json

kriterion decide   ──► human_decision.json
kriterion contract ──► outcome_contract.json
kriterion report   ──► report.html
kriterion evals    ──► run-export.json (+ per-fixture verdicts)
kriterion compare  ──► comparison.json + comparison.md
```

Every run directory carries `manifest.json`: protocol version, executor and model IDs with digests,
case fingerprint, ledger fingerprints, charter versions and hashes, prompt-template hashes, seeds,
token counts, timings, and the measured nondeterminism divergence. **That manifest is the
reproducibility claim.**

---

## 10. Hekton integration contracts

### Imported — `hekton_llm` (the only runtime import)

Bind to **source**, not to the interface doc. Verified 2026-09-05: `docs/local-model-control-plane-interface.md:67`
documents `generate(model, messages, options)`, which is **wrong** — `messages` belongs to `chat()`.
The real signature at `src/hekton_llm/ollama_client.py:34` is:

```python
def generate(
    self,
    model: str,
    prompt: str,
    system: str | None = None,
    fmt: str | None = None,
    options: dict[str, Any] | None = None,
) -> TimedResult: ...
```

- `TimedResult` is a frozen dataclass: `(elapsed_seconds: float, data: dict[str, Any])`.
- Failure mode is `OllamaConnectionError` (a `RuntimeError`), raised from `urllib.error.URLError`.
- Kriterion calls: `generate(model=..., prompt=..., system=<charter>, fmt="json",
  options={"temperature": 0, "seed": N})`; `list_models()` and `ps()` for `doctor`;
  `runtime_provenance()` / `model_digests()` / `digests_match()` for the manifest.
- **Depend on the import namespace `hekton_llm`, never the distribution name.** The package's own
  docstring is explicit: the namespace is stable and does not change at promotion, while the
  distribution is still named `local-llm-lab` v0.2.0 and becomes `hekton-local-llm` later. The
  editable-install path is documented in **`docs/setup.md`** — public and tracked — not in
  `docs/local-assumptions.md`, which `.gitignore:20` correctly keeps to the private sibling.
- **Not consumed:** routing / `local_good_enough` (forbidden as a production signal by the
  component's own interface doc), `simple_yaml`, `vault_reader`, `judge_gremlin`, `model_gremlin`.
- Declared in `.hekton/project.yaml` as `architecture.consumes: [hekton-local-llm (provider surface)]`,
  matching the `consumes_contract` declaration precedent verified at
  `local-agentic-coding-lab/harness.yaml:343`.

### Emitted — `kriterion-run-export/v0.1` (one-way, file only)

Written by `src/kriterion/export/run_export.py` into `runs/<id>/run-export.json`. This is
**Kriterion application telemetry**. It is not an assurance contract, not an evidence envelope, and
not a generic schema (ADR-005). Contents: case and ledger fingerprints, protocol version, charter
versions, executor and model IDs with digests, prompt-template hashes, initial and revised
positions, challenge events, evidence requests and dispositions, belief updates with drift flags,
final recommendation and dissent, per-phase tokens/latency/cost, and per-fixture eval verdicts.

Nothing reads it in V0. If Assurance later defines a contract, a second emitter target is added
inside `export/` and the domain model does not change.

### Not integrated

`hekton-assurance-lab` — no import, no schema reference, no shared file, no `AICapability`
manifest. Verified state: 2 commits, 11-line architecture stub, no eval runner, and its own V0
planning now underway in an untracked `docs/planning/hekton-assurance-v0/`. Kriterion's job is to
stay out of its way.

---

## 11. UX / demo flow

One generated static HTML file per run (`kriterion report` → `runs/<id>/report.html`). Stdlib
string templating, no JS build, no server, printable. The CLI is the operator surface; the report
is the executive surface. **The debate transcript is deliberately not a screen** — raw phase
artifacts stay in the run directory for the technically curious. Agent theatre is the thing this
product is arguing against; it does not get the hero slot.

Five views in one scrolling page, in demo order. A persistent banner across all of them reads
**`AUTHORED FIXTURE CASE — SYNTHETIC DATA`**.

1. **The decision** — `decision_requested`, ask, deadline, top sensitivity assumption,
   evidence-strength summary.
2. **Evidence map** — three columns, SUPPORTED / ASSUMED / UNKNOWN, with category badges,
   attestation badges, provenance on hover, contradicting items highlighted.
3. **Independent positions** — five anonymised cards (role shown, order shuffled): action,
   confidence band, top reasons with citations, blocking unknowns. Plus **the numbers**: scenario ×
   alternative table (NPV low/base/high, payback, peak funding), tornado list, staged-funding
   ladder. Case C additionally renders the avoided-loss band *beside*, never inside, the NPV table.
4. **What changed minds** *(hero view)* — per member: `PILOT → FUND_EXPERIMENT · because:
   controlled-throughput-study`, with change-type badge and drift flags. `no_change` members are
   shown **equally prominently** — "held position: unanswered blocking unknown" is the product's
   best moment, not an absence.
5. **Decision record** — `SYNTHETIC RECOMMENDATION — NOT A DECISION` (action, amount, conditions,
   stop conditions) · **STRONGEST DISSENT** verbatim in its own box · `HUMAN DECISION` in a
   visually separate region (owner, disposition, overrides, rationale) · OutcomeContract summary
   (baseline, measures, review date, next decision).

**Five-minute narrative (Case A):**

- **0:00** — "Should we fund £4.2m of coding agents? Here is the case, and here is what is actually
  evidence versus assumption versus unknown."
- **1:00** — Five independent positions, formed before anyone saw anyone else. Note the spread.
- **2:00** — The deterministic numbers. Models may cite them; they cannot alter them. The 18%
  uplift assumption dominates the tornado.
- **3:00** — *Hero moment.* A controlled study arrives contradicting the 18%. The CFO moves and
  says exactly why. The CISO refuses to move, because their security question was never answered.
  Both visible, both auditable, both attributable to evidence rather than to a head count — because
  nobody was ever shown the head count.
- **4:00** — The recommendation funds a 12-week pilot with stop conditions. The strongest dissent
  is preserved verbatim. The human decision owner accepted with an override — a *separate* record.
  The OutcomeContract makes the decision testable in December.
- **4:40** — One comparison slide from `kriterion compare`: what the strong single-agent baseline
  said on the identical frozen case, at what token cost, and what that does or does not say about
  whether the committee earned its complexity.

---

## 12. Weekend build plan

Ordered and dependency-aware. **[C]** = critical path, **[S]** = stretch. Complexity S/M/L. Branch
per the git contract (`agent/claude/<slug>`), ADRs into `docs/decisions.md` as built, session
closeout via `~/hekton/scripts/end-session.sh`.

### Saturday AM — scaffold, domain, Case A

1. **[C][S]** `pyproject.toml` (name `kriterion`, py≥3.11, console script, **zero runtime deps**)
   + `src/kriterion/` skeleton + pytest wiring. **`pyproject.toml` is a protected path — get
   explicit human approval before writing it.**
   *Accept:* `pip install -e . && kriterion --help` works.
2. **[C][M]** Domain dataclasses (`domain/*.py`): all `§4` types, canonical-JSON serialisation,
   sha256 fingerprint helper, `attestation` field enforced on `EvidenceItem`.
   *Accept:* round-trip tests pass; fingerprint stable under key reordering.
3. **[C][M]** Case A pack authored in TOML with full ledger; `kriterion ledger freeze`.
   *Accept:* fingerprinted ledger produced; a bad category and a missing attestation are both
   rejected with a clear error.
4. **[C][S]** ADRs 001–006 recorded in `docs/decisions.md`; `.hekton/project.yaml`
   `architecture.consumes` populated.
   *Accept:* decisions table matches `§3`.

### Saturday PM — economics, executor, baselines

5. **[C][M]** `economics/engine.py` + golden tests (P0-01, P0-02).
   *Accept:* hand-computed fixtures match to 1e-6; hash stable under key reordering.
6. **[C][M]** Staged-funding view + Case A economics render.
   *Accept:* `kriterion econ cases/coding-agent-rollout` writes `economics.json`.
7. **[C][M]** Executor port + `hekton_local.py` (bound to `ollama_client.py:34`, `fmt="json"`,
   temp 0, seed, provenance capture, `OllamaConnectionError` → doctor message) + `replay.py`.
   *Accept:* `kriterion doctor` green on this machine; a smoke completion returns schema-valid JSON.
8. **[C][L]** **Strong Baseline A** (`§6`: all five charters' checklists collapsed, self-generated
   case for/against, premortem, evidence requests, injection, revision, BeliefUpdate) + phases 0–4
   + Baseline B aggregator.
   *Accept:* Case A produces A and B condition artifacts end to end; A's call count and token budget
   are recorded and are within the same order of magnitude as C's.

### Sunday AM — deliberation, belief updates

9. **[C][S]** Charters v1 (five TOML files); required-evidence sets drive prompts.
   *Accept:* charter hashes land in `manifest.json`.
10. **[C][L]** Phases 5–8: perspective-inverted challenges, premortems, contradiction/gap scan,
    evidence-injection CLI, revised assessments, BeliefUpdate derivation with drift flags,
    deterministic chair synthesis with the dissent guarantee.
    *Accept:* full C-condition run on Case A; the P0-07 injection produces an `evidence_driven`
    update; a unanimity path inserts substantive residual dissent; **the no-tally unit test passes**.
11. **[C][S]** `kriterion decide` (HumanDecision) + `kriterion contract` (OutcomeContract).
    *Accept:* a funding action without an OutcomeContract exits non-zero (P0-09).
12. **[C][M]** Case C pack (12–15 items, negative NPV by construction); runs under A/B/C.
    *Accept:* both cases run end to end under all three conditions.

### Sunday PM — evals, comparison, report

13. **[C][L]** Eval harness + deterministic scorers; **all ten P0 fixtures**.
    *Accept:* `kriterion evals` writes `run-export.json` with per-fixture verdicts; all P0 green
    or explicitly triaged.
14. **[C][M]** `kriterion compare` — A/B/C over both cases at 5 seeds; metrics table, seed-variance
    report, honest-negative check per `§6`.
    *Accept:* `comparison.json` + `comparison.md` generated from real runs, including token cost per
    condition.
15. **[C][M]** `report/html.py` — five views; one curated Case A demo run committed.
    *Accept:* report opens locally; hero view populated from real BeliefUpdates; `case_realism`
    banner and simulation badges render (P0-10).
16. **[C][S]** Docs pass: `docs/architecture.md`, `docs/experiment-plan.md` (pre-registration,
    written **before** task 14 runs), `docs/setup.md` (install path), session log and walkthrough in
    the private sibling, `end-session.sh` with a blog-radar signal.

### Stretch, in priority order

17. **[S][M]** P1 evals — the four perturbation-pair fixtures.
18. **[S][M]** Treatment D heterogeneous batch (runtime verified live; models installed).
19. **[S][M]** Judge-scored P2 evals with the blind human calibration sample.
20. **[S][S]** Synthetic retrospective as a clearly labelled mock artifact for the demo's close.

---

## 13. Explicit deferrals

Not needed to prove V0, and each would cost more than it returns this weekend:

Case B (`international-platform-capability`) · `DecisionRetrospective` as an implemented type
(labelled mock only) · portfolio view and optimisation · CIO voting seat · model-based chair ·
multi-round revision (>1) · condition **C-tally** · Treatment D on the critical path · real-options,
Monte Carlo, IRR, S-curve adoption, tax and depreciation · frontier-model executors and any paid API
(estate policy is local-first) · real Hekton Assurance integration of any kind · `AICapability`
manifests · importing genuine assurance envelopes · enterprise finance/portfolio connectors ·
review-date scheduling automation · Astro site and public build log · confidence as decimals ·
committee-as-Gremlin naming · any promotion proposal for any abstraction · UI beyond the static
report (no server, no interactivity) · auto-generated board papers · autonomous funding actions of
any kind.

---

## 14. Risks, kill and pivot criteria

### Risks

| ID | Risk | Sev | Mitigation |
|---|---|---|---|
| R-01 | 7–14B local models cannot sustain schema-valid, charter-differentiated reasoning | High | Strict JSON schemas, one retry, `abstained_error` degradation; Case A tuned first; honest reporting if quality is the binding constraint |
| R-02 | Fake rigour — authored traps measure trap detection, not decision quality | High (reputational) | Claim discipline in `§6`: hygiene claims only, stated in every artifact |
| R-03 | Judge contamination — the judge is also the generator | Medium | Headline metrics all deterministic; judged scores labelled PROVISIONAL; blind human anchor; documented limitation |
| R-04 | Weekend scope overrun on tasks 10 and 13 | Medium | Two cases not three; P0 set of 10; P1/P2 and D explicitly tiered as stretch |
| R-05 | Independence in C is only context isolation — five correlated samples from one model | Medium | Say "independent *contexts*", never "independent judgments"; role-diversity metrics measure it; D exists to test it |
| R-06 | Boundary erosion — Assurance V0 planning is live and already names `investment-committee` | Medium | ADR-001/005; no edge to the lab; export named as app telemetry; treat any "just put the schema in the lab" suggestion as a violation absent a second consumer |
| R-07 | `hekton-local-llm` is alpha with a stale distribution name and a stale interface doc | Low | Bind to source signature and import namespace only; adapter isolates breakage; install path in public `docs/setup.md` |
| R-08 | Human-decision realism — the only accountable human is the operator | Low | Documented, not hidden; machinery real, authority synthetic |
| R-09 | Seed count still modest for local-model nondeterminism | Medium | 5 seeds; divergence measured and reported in the manifest; honest-negative margin set at 2× observed seed SD |

### Kill / pivot criteria

**1. Structured deliberation does not outperform the strong baseline.**
*Trigger:* the `§6` pre-registered criterion fires negative.
*This is not a failure — it is the result.* Publish it. Pivot the product from "AI committee" to
**"evidence-first decision instrumentation"**: keep the ledger, attestation, deterministic
economics, belief-update tracking, dissent preservation and outcome contract, and run them around a
*single* strong model. That product is smaller, cheaper, and still solves the real problem. Most of
the V0 build survives the pivot intact — which is why the architecture puts the protocol, not the
committee, at the centre.

**2. Evidence provenance cannot be enforced cleanly.**
*Trigger:* P0-03/04/05 cannot be made to pass without prompt contortions that would not survive
contact with a different model.
*Pivot:* narrow radically to a **deterministic evidence-ledger and economics tool** with model
assistance confined to summarisation and challenge-question generation — no model-authored positions
at all. If agents cannot be prevented from manufacturing evidence, the honest product is one that
does not let them near the evidence.

**3. Assurance integration would require app-specific coupling.**
*Trigger:* any future Assurance contract cannot consume Kriterion's export without Assurance
learning committee semantics.
*Response:* do not integrate. Keep the export as app telemetry indefinitely. This is already the V0
posture, so the cost of this branch is zero — which is the point of ADR-005.

**4. Local model quality is insufficient.**
*Trigger:* R-01 materialises — schema failures or indistinguishable role outputs across the board.
*First response, not last:* this is itself a **publishable finding** about local-first executive
tooling, and the more interesting article. Report it with the role-diversity metrics as evidence.
*Then pivot:* reduce to three seats (CFO, CISO, Business Executive), simplify output schemas, and
run Treatment D — heterogeneity may be the fix rather than an enhancement, and the runtime is
verified live with 12 models to test it.

**5. Weekend clock runs out mid-build.**
*Trigger:* task 13 not started by Sunday 14:00.
*Response:* the minimum publishable artifact is **Case A, conditions A and C, 3 seeds, P0-01
through P0-07, and the static report.** Ship that and say what is missing. A narrow honest result
beats a broad unfinished demo — which is the whole scope thesis.

---

## 15. Next build-loop prompt

> You are implementing **Kriterion V0**, a Hekton factory output at
> `kriterion` (public, `dermdunc/kriterion`), with a
> private sibling at `../kriterion-private`.
>
> **Read first, and treat as settled:** `docs/v0-plan.md` — the accepted V0 plan. Product
> architecture, ADRs, protocol, experimental design and scope are decided. **Do not re-plan them.**
> Also read `.hekton/project.yaml`, `docs/decisions.md`, `docs/risks.md`, `docs/next-actions.md`,
> `AGENTS.md`, and the binding conventions in `../kriterion-private/CLAUDE.md`.
>
> **Your task:** execute the Weekend Build Plan in `docs/v0-plan.md` `§12`, in order, starting at
> task 1. Work the `[C]` critical path first; do not start any `[S]` stretch item until every `[C]`
> item is done or explicitly triaged in `docs/next-actions.md`.
>
> **Non-negotiable invariants — a change to any of these is a re-planning event, not an
> implementation decision:**
> 1. No member sees any tally, count or majority signal before phase 8. Assert it as a unit test on
>    prompt payloads (ADR-004).
> 2. `SyntheticRecommendation` and `HumanDecision` are separate types, separate files and separate
>    UI regions, always (ADR-006).
> 3. All finance, arithmetic, structural validation and sensitivity ranking is deterministic and
>    computed before any model call. The engine never falls back to a model (ADR-002).
> 4. Only `kriterion ledger add` writes evidence. There is no code path from model output into the
>    ledger. Every `EvidenceItem` carries an `attestation` (ADR-003).
> 5. Baseline A gets the same evidence, economics, cognitive operations, evidence injection,
>    revision opportunity and output schema as C. Only the number of independent contexts varies
>    (`§6`). If you find yourself weakening A, stop — that is the experiment.
> 6. `hekton_llm` may be imported **only** in `src/kriterion/executors/`. Add a test that greps for
>    violations. No import, schema reference or shared file with `hekton-assurance-lab` (`§2`).
> 7. Zero runtime dependencies. Case packs and charters in TOML via `tomllib`; artifacts in JSON.
> 8. Write `docs/experiment-plan.md` with the pre-registered honest-negative criterion **before**
>    running the comparison batch in task 14.
>
> **Ground truth, verified 2026-09-05 — do not re-derive:** Ollama is live on `localhost:11434`
> with 12 models including `qwen2.5:14b-instruct`. The real signature is
> `OllamaClient.generate(model, prompt, system=None, fmt=None, options=None) -> TimedResult` at
> `platform/hekton-local-llm/src/hekton_llm/ollama_client.py:34` — the interface doc at line 67 is
> **stale**, bind to source. Depend on the `hekton_llm` import namespace, never the distribution
> name (still `local-llm-lab` v0.2.0). `hekton-assurance-lab` has no eval code and no usable
> contract.
>
> **Before writing `pyproject.toml` (task 1), stop and get explicit human approval** — it is a
> protected path under `~/hekton/.rules/git-contract.md:213`.
>
> **Conventions:** branch `agent/claude/<task-slug>`, never commit to `main`, open a PR. Use the
> `Agent:` commit footer and **no** `Co-Authored-By` trailer. Record every decision in
> `docs/decisions.md`, keep `docs/risks.md` and `.hekton/risk-register.yaml` current, update
> `docs/next-actions.md`, and close the session with `bash ~/hekton/scripts/end-session.sh`. Do not
> write to the Obsidian vault (`vault_mutation_allowed: false`).
>
> **Stop and ask the human** if: a `[C]` task cannot meet its acceptance criterion; any
> non-negotiable above would have to bend; or local model quality triggers kill criterion 4 in
> `§14`. Report progress against the `§12` task list, not against a narrative of what you tried.
```

---

## Appendix — questions this plan does not settle

These are for the human, not for the implementation loop:

1. **Is the curated Case A demo run committed to the public repo?** Reproducibility and demo
   resilience versus repo noise and public exposure of local model outputs. *Recommendation: yes,
   one run, clearly marked, because the demo must survive a dead runtime.*
2. **Publication venue and timing** for a negative result, should the honest-negative criterion
   fire. The pre-registration is worthless if the result is quietly shelved.
3. **Whether the operator is willing to score the blind calibration sample honestly** before
   learning conditions. If not, drop the judged metrics entirely rather than half-doing them.
