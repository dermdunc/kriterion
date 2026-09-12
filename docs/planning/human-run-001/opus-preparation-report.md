# Human Run 001 — Preparation Report

Public summary. Structure, counts, verdicts and methodology only; no case content, no evidence
claims, no decision-rights entries, no economics figures, and not the synthetic recommendation.
The detailed version is `kriterion-private/human-run-001/preparation-report-detail.md`.

**Read after T2.** This file records observations about the generated page's quality that would
bias section 5 and the Narrative Integrity question in the retrospective if read beforehand.

---

## What this preparation did

A first preparation of Human Run 001 was built, run and frozen against a narrower specification of
the same decision. A materially fuller final specification then arrived, before T0 was recorded.
This preparation reconciled the two: it rebuilt what the new specification superseded, preserved
what was still correct, and archived the frozen artifacts rather than mutating them.

**Archived, not overwritten.** The superseded case pack, its frozen run, its generated page, its
freeze manifest and its case-design record were moved intact into a dated `superseded/` directory,
with an explanatory note. Every content hash was verified before the move and re-verified after it;
all match. The reason is the rule Kriterion enforces on its own users: a canonical decision record is
never mutated in place. A preparation that rewrote its own frozen run, leaving behind a manifest
describing artifacts that no longer existed, would be applying a standard it does not keep.

**No participant data existed to lose, and that was checked rather than assumed.** Every response
placeholder — pre-decision note, completed impact log, human decision, outcome contract,
retrospective — was read and confirmed to contain only its "not yet recorded" stub. The post-T0
evidence file contained its stub and an empty table. The run directory contained no
`human_decision.json` and no `outcome_contract.json`. T0 was never recorded against the superseded
case.

**Preserved unchanged**, because the new specification did not supersede them: the confidentiality
and public/private boundary; the blank participant field in every public file; the refusal to
fabricate any organisation-specific current-state data; content-hash freezing, because the private
directory is deliberately not a git repository; the external evidence base and its provenance rules;
and the cost-only economics model — though that last one was re-checked against the source rather
than inherited.

---

## Case

Case id: `global-platform-engineering`, renamed from `international-platform-engineering`.

Decision, as frozen in the case pack:

> What global platform-engineering operating model should we invest in for the next 12-18 months so
> that distributed engineering teams gain sufficient autonomy and responsiveness without duplicating
> enterprise platforms or fragmenting global standards?

**Why the rename.** "International" is a headquarters-relative term — it only means something if
there is a centre that everything else is international *to*. The superseded framing had exactly
that. The new framing has four peer regions and an operating model in which enterprise-owned
platforms are engineered from all of them at once, so a case id presupposing a centre contradicts
the case's own first section. The rename touched two registry entries in this repository, one test
module, and every document naming the id; a grep for the old id in this repository now returns
nothing. The evidence id space was moved as well, so no evidence reference recorded during this run
can be silently matched against the archived one.

Four alternatives, mapping one-to-one onto the four operating models. `do_nothing` — required by
`DecisionCase`'s own invariant — carries the central model, and two things are recorded rather than
worked around: the central model is not strictly "do nothing", because the specification permits
regional support to be improved within it; and the regional-autonomy model is held as a genuine
alternative rather than a strawman, carrying both supporting and constraining evidence on the same
terms as every other model. The investment dimension reuses Kriterion's `DecisionAction` vocabulary
unchanged.

---

## Evidence

53 items in ledger v1, up from 40. Separation by epistemic class:

| Category | Count | Previously |
|---|---|---|
| `MEASURED` | **0** | 0 |
| `EXTERNAL_REFERENCE` | 15 | 15 |
| `EXPERT_JUDGMENT` | 8 | 5 |
| `INFERENCE` | 4 | 3 |
| `ASSUMPTION` | 8 | 6 |
| `UNKNOWN` | 18 | 11 |
| `FORECAST` | 0 | 0 |

**External evidence** (15 items) all derive from one real, already-public document: a deep-research
whitepaper on international platform engineering in the agentic enterprise, published by the
participant under their own identity in a public repository before this experiment existed. These
items carry `attestation = "REAL"`.

A **provenance ceiling** is now recorded that the first preparation missed: that whitepaper
attributes every claim to a named organisation in prose but contains no URLs, footnotes or
bibliography. It is a second-order source, and no item can be traced to a primary document from the
pack alone. Several items were downgraded in strength on that basis — those resting on a single
organisation's self-report, or carrying the whitepaper's own evidentiary caveat. Coverage was again
checked for one-sidedness: roughly half the external items constrain greater regional authority
rather than supporting it, and two now carry the limit of their own inference inside the claim text.

**Current-state observations: none.** This remains the most important structural fact about the
case, and a fuller specification of the *decision* did not manufacture observations of the
*organisation*. The specification names six current-state categories to look for; each was checked
against the external source before being classified, rather than assumed unavailable. None is
supported. The one worth naming publicly is **timezone coverage**, because it is the category that
most looks like a general industry fact a research source could supply — and it is the one the
source explicitly disowns, self-labelling its own timezone reasoning as inference rather than
measurement and listing the corresponding question among its own open questions. It is an `UNKNOWN`,
and the item records that the check was performed, so the classification cannot later be mistaken
for an oversight.

**Expert judgment** (8 items, up from 5) are the whitepaper's own analytical judgements, which that
document itself labels as inference rather than as source claims. The three added items carry the
pattern library's stated prerequisites and named failure modes, a control-plane maturity ladder, and
a ten-row anti-pattern table — all of which the new specification's framing needs and the old pack
did not carry. The circularity grew with the count: these are the participant's own prior judgements
fed back to them as evidence, which biases toward `T0 ≈ T1`, i.e. against the product hypothesis.

**Assumptions** (8 items), all `LOW`: the six the specification itself names, plus two explicitly
labelled illustrative sizing figures. **Two** now carry `contradicts` pointing at an
external-evidence item, where the first preparation had one, because the research names the
corresponding failure mode of each proposal directly.

**Unknowns** (18 items, up from 11). The increase is not padding: the specification names nine
unknowns explicitly, adds six current-state categories, and requires unpriced amounts to be
preserved as unknowns rather than estimated.

**The seven candidate evidence-request areas are seeded, not authored.** They are not written into
the pack as `EvidenceRequest` objects — those are committee output, and authoring them would
pre-empt what the run measures. Each is present as the corresponding `UNKNOWN`, so the committee can
surface it or fail to. Whether it does is a measurement.

---

## Economics

**What Kriterion could represent honestly: the cost side, and nothing else.**

The specification's economic frame asks for three quantities: the cost of new capability, the cost
of the current model, and the risk of decentralisation. Only the first is priceable.

The cost-only choice was **re-checked against the source rather than inherited**. Every figure in
that source was examined for whether it could legitimately price a benefit-side driver. None can:
each is another organisation's outcome under unstated baseline conditions, a numerator without a
denominator or the reverse. All the quantified ones are outcomes of platform-product and automation
investments, while the source's own *geographic* evidence is precisely the part it marks as
qualitative and non-quantitative. And the source states twice, in its own voice, that external
research cannot establish the magnitude of these effects.

Consequences, all deliberate:

- The result is negative in every scenario, by construction, because only costs are summed.
- **No benefit band is reported at all** — not even the alongside-NPV band Kriterion's Case C
  fixture carries. This case cannot honestly state a band, so the result carries `None`, not `0`.
- The sensitivity ranking has exactly **one** entry, because the cost of the capability is the only
  quantity the case can vary.
- The ask amount is illustrative sizing, explicitly labelled, because `Ask.amount_gbp` is a required
  non-optional float. This pulls against the specification's own instruction to identify the
  *smallest* useful commitment: a required six-figure ask anchors upward, and the case cannot record
  "not yet sized".
- The sizing inputs were **held fixed** at the superseded pack's values rather than re-guessed for
  the broader scope, so that any difference between the two runs is attributable to case content
  rather than to a re-guessed number. The economics output is consequently identical between the two
  runs, which is the correct result and not a sign that nothing changed.

No ROI, NPV or payback figure was fabricated to give the engine more to work with.

---

## Challenge structure

Kriterion's `CommitteeSeat` is a closed five-value enum, and `load_all_charters` loads all five from
a fixed relative path with no per-case selection. The specification names six perspectives, and the
mapping is **worse** than under the previous framing:

| Perspective the specification names | Seat | Fidelity |
|---|---|---|
| CFO | `cfo` | Exact |
| Enterprise CTO / Chief Architect | `cto` | Good |
| Global Platform Leader | — | **No seat** |
| International / Regional CIO | — | **No seat** (cut in V0) |
| Regional Engineering Leader | `business_executive` | Weak proxy |
| Platform Consumer (optional) | — | **No seat** |
| — | `ciso` | Not requested, but fits: delegated control-plane access, entitlement sprawl, JIT privilege |
| — | `cro_compliance` | Not requested, but fits: regional regulatory adaptation, divergence risk |

Two of six well represented, one weakly, three not at all. The sharpest losses: the Global Platform
Leader, which is the sponsor of this case and has no seat at the table judging it; and the Regional
Engineering Leader, whose pressure — *does this actually remove a dependency, or just add another
layer?* — is the one that most directly tests pre-registered falsification condition 5, and has no
faithful carrier. No seat was added; adding one ripples through the charters, the eval harness, the
decision state, the narrative binder and the page.

All five seats participated (5/5 initial, 5/5 revised). What they produced, and how it compares with
the superseded run, is in the private detailed report, because it bears on the quality of what the
participant will read rather than on the preparation.

---

## EvidenceRequests

15 `EvidenceRequest` records persisted, comprising **3 distinct requests repeated verbatim across
all five seats** (previously 10 records, 2 distinct). Quality assessment, applying the
specification's own standard rather than counting them as a success:

| Request shape | Assessment |
|---|---|
| Quantify the cost of the current model and estimate decentralisation risk | **Mixed.** Points at the case's actual economic gap, but bundles two different questions and specifies no method or threshold. |
| Determine whether platform owners would consent to delegated operation | **Best of the three.** Specific, obtainable, and the stated prerequisite of one of the four models. Still no threshold. |
| Establish the optimal size and distribution of the capability | **Weak.** "Establish the optimal" presupposes an optimum is discoverable, and specifies no method, threshold or falsifiable outcome. |

**None of the three specifies a threshold**, so none says what value would flip the decision. They
are recorded as what they are and are **not** rewritten into falsifiable tests for the write-up.

One genuine improvement is worth naming, because it is attributable: the second request is precisely
the hinge the superseded run's committee failed to ask about, and which the first preparation
recorded as a gap. A richer ledger surfaced it. Two other hinges — the upstream contribution
acceptance rate, and which control-plane actions are delegable in fact — were again not asked about,
despite both being in the ledger and both being among the specification's own seven candidate areas.

---

## Product fit

```text
PRODUCT GAP FOUND
```

The one gap that blocked the experiment was fixed during the first preparation and needed no further
change here beyond a mechanical rename. Everything else is recorded and left unfixed, per the
instruction that a recorded limitation may be worth more than code.

### Carried forward — generic cost-only economics

`kriterion.economics.CASE_ECONOMICS_FUNCTIONS` dispatches by case id and both `kriterion run` and
`kriterion econ` exit 1 for an unregistered id. `compute_cost_only_economics` generalises Case C's
cost-only construction with the avoided-loss band made **optional**, so a case that cannot honestly
state even a band carries `None` rather than a fabricated figure or an implied zero. Case C keeps its
own entry point and still requires its band. This preparation changed only the registered case id, in
both registries and the test module that pins them. No case content enters this repository — only the
case id.

### Recorded, not fixed — the five role charters are still coupled to the original fixture

The five `RoleCharter` files name `coding-agent-rollout`'s own evidence in their `required_evidence`,
`standard_challenges` and `failure_modes`. Those expectations are injected into any case the charters
are used on. Contamination was found again in this run's artifacts — content that does not exist in
this case.

One thing improved and one did not. **No contaminated string reaches the generated page this time**,
where one string reached it three times in the superseded run; the page was scanned specifically for
this. But the charters still did no differentiating work: all five seats produced verbatim-identical
initial positions, the same reasons and the same references. **Kriterion's committee still does not
generalise beyond the case it was built for**, and this is the strongest generalisability finding
available before the human has recorded anything. Rewriting the charters would change what every
future run produces on the basis of a single case. Recorded instead.

### Recorded, not fixed — `CaseRealism` cannot express a real decision

`CaseRealism` defines exactly one value, `AUTHORED_FIXTURE`. Confirmed this time by reading the case
pack loader rather than inferring it: `case_realism` is **never parsed from `case.toml` at all**, so
there is no override even in principle. The generated page therefore banners a real decision as an
authored fixture, and asserts in unbound prose that the case and its evidence are authored fixtures.
For this case that statement is false about the evidence.

Not fixed, for the same two reasons as before. The mislabel errs conservative — it understates
realism rather than claiming `REAL` for synthetic material. And fixing it properly means a new enum
value plus conditional unbound prose in the page template, which is template surgery on the only
artifact Narrative Integrity cannot check, undertaken mid-experiment. The evidence table does tell
the truth: those items carry `attestation = "REAL"`, so the page contradicts itself rather than lying
uniformly.

### Recorded, not fixed — a derived economics sentence can outrun its model

`DecisionState.economics_interpretation` selects its wording from the sign of the NPV triple alone.
Under a cost-only model with no benefit term, that produces a valuation claim about a model that
contains no valuation. Narrative Integrity passes it, correctly: the sentence is faithfully derived
from the state. Compounding it, the page never renders the avoided-loss fields at all, so it does not
say that a benefit side exists and is unpriced — the absence is itself absent.

That is the finding, and it remains the most interesting one in this report. **Narrative Integrity
guarantees that the page says what the artifacts say. It does not guarantee that a derived summary
respects the epistemic status of what it is summarising.** Those are different properties, and only
the first is currently enforced.

Not fixed for the same specific reason as before: the only case it affects is this one, so a guarded
fix would be tailoring the instrument to the experiment it is about to be measured on. The impact log
already asks whether anything on the page appeared more conclusive than the evidence justified.
Pre-fixing the best available answer to that question destroys the measurement.

### Recorded, not fixed — three dimensions, one of which Kriterion represents

`DecisionCase.alternatives` is a bare `list[str]` with no per-alternative evidence, cost or
decision-rights profile, so the four operating models are names only and the committee reasons about
the *stage* rather than about which model to adopt. This is **worse** under the new specification
than the old one: the four models differ chiefly in the authority they allocate, which is exactly
what a list of names cannot carry.

Decision rights and physical distribution have no native representation at all and live as blank
private artifacts completed at T0/T1/T2. Whether to add a product-domain model was re-examined when
the decision-rights matrix nearly doubled in size; the answer held. The allocation is a decision
*output*, and the product would gain a schema it cannot validate, cannot economically model and
cannot narratively bind.

---

## Pre-registration

Committed in this directory, blank, before the participant saw any Kriterion analysis of this case:

| Artifact | Contents |
|---|---|
| `README.md` | Experiment scope, public/private split, start sequence |
| `protocol.md` | Research question, T0/T1/T2 across three dimensions, useful outcomes, interpretation rules, **five falsification conditions**, freeze rules, reading order |
| `case-design.md` | Decision, what it replaced, why this case, three dimensions, evidence boundaries, the Model B design problem, economic limits, seven experiment risks |
| `decision-impact-log.md` | The blank instrument: T0 across all three dimensions, sections 1-7, T1 with the explicit stop before section 8, T2 with the anchoring check, trajectory table, human-decision structure, Outcome Contract candidate metrics, the five falsification conditions |
| `opus-preparation-report.md` | This file |

The instrument preserves, unchanged from the first version where the new specification did not
conflict: the `Do not scroll ahead` stop before the synthetic recommendation; the prompt asking
exactly what moved the participant between T0 and T1, naming a specific item rather than "the
analysis"; and the position-trajectory table with its reading guide. The trajectory table now carries
all three dimensions rather than one.

Rebuilt to match the new specification: three dimensions recorded independently at each checkpoint;
T0's operating-model, distribution, decision-rights and investment sections with their reasons,
uncertainties and federation/centralisation triggers; T2's explicit anchoring check at the point of
measurement; the human-decision structure; the Outcome Contract candidate-metric list with a
mandatory baseline column; a "useful outcomes" section fixed in advance so that a null position shift
is not later reported as a disappointment; and **five** falsification conditions in place of two.

Blank decision-rights tables (13 rows) and a blank distribution artifact (4 regions, presence and
ownership kept as separate answers) live privately, because their rows are organisation-specific.
They are blank by design: the allocation is part of the decision, not an input to it, and neither the
case pack nor the generated page asserts or recommends any row.

The participant field is blank, as before.

---

## Frozen versions

| Field | Value |
|---|---|
| Code commit | `69fe023` on `agent/opus/human-run-001-prep`, based on `origin/main` @ `5dac579` |
| Case commit | Not applicable — the private directory is deliberately not a git repository. The freeze is a content-hash manifest with a timestamp, held privately |
| Canonical run | Condition C (full committee, phases 0-8), **seed 1** |
| Evidence ledger | v1, 53 items |
| Generated page | **0 narrative-integrity violations** |
| Superseded bundle | archived intact, all 11 content hashes re-verified after the move and unchanged |

Nothing above is mutated during the experiment. Material evidence arising during the run goes to
`post-t0-evidence.md` in the private directory.

Only one run was made, as before. A second seed was not tried: selecting among runs would be
choosing the instrument after seeing what it says.

---

## Validation

Actually executed:

| Command | Result |
|---|---|
| `pytest` (after the rename) | **356 passed**, unchanged count — the rename is not a behaviour change |
| case-pack load + cross-reference check | 53 items, category counts as tabulated, no dangling `supports`/`contradicts` id |
| `kriterion run <case> --condition C --seed 1` | exit 0, **5/5 initial, 5/5 revised**, no seat abstained |
| `kriterion econ <case>` | exit 0, economics written |
| `kriterion ledger freeze <case>` | 53 items frozen, fingerprint recorded |
| `kriterion decision-page <run> <case>` | exit 0, **0 violations** |
| charter-contamination scan of run artifacts and page | contamination present in artifacts; **none reaching the page** |
| pre-move / post-move hash verification of the superseded bundle | all 11 hashes match the original manifest |
| `kriterion decide` | exit 0 — verified **in a throwaway copy**, then deleted; correctly warned that a funding action needs a contract |
| `kriterion validate-run` (before contract) | exit 1, P0-09 violation raised as designed — same throwaway copy |
| `kriterion contract` | exit 0 — same throwaway copy |
| `kriterion validate-run` (after contract) | clean, no governance violations — same throwaway copy |

Checks against the readiness criteria:

- **Runs through Kriterion.** Yes, unchanged pipeline, case pack outside the repository.
- **Narrative Integrity passes.** Yes, zero violations. `kriterion decision-page` refuses to write a
  failing page, so a written page is the pass.
- **No unsupported claims silently strengthened.** Not fully. The evidence table, assumptions,
  unknowns and sensitivity attribution are faithful. One derived economics sentence outruns its
  model, and one page banner is false for this case. Both are named above; neither is silent.
- **Evidence provenance valid.** Yes, and with a provenance ceiling now recorded that the first
  preparation did not record.
- **Assumptions remain assumptions.** Yes, all `LOW`, two carrying `contradicts` against the
  evidence base.
- **Unknowns remain unknown.** Yes, 18 items, none promoted, none estimated. The six current-state
  categories were each checked against the source before classification, not assumed.
- **EvidenceRequests persist.** Yes, 15 records with `would_change` on each.
- **Superseded artifacts not mutated.** Yes. Archived intact, hashes verified either side of the
  move, with a note recording why and confirming no participant data existed.
- **Blank protocol, blank impact log, five falsification conditions, T0/T1/T2 committed.** Yes, in
  this commit, blank.
- **Case and code frozen.** Yes, see above.
- **Synthetic recommendation hidden until T1.** Procedurally only. It exists in the frozen artifacts
  and on the page from the start; nothing technically prevents scrolling ahead. Stated as a design
  limitation in `protocol.md`, and the reason falsification condition 3 is pre-registered.
- **No `HumanDecision` made during validation.** Confirmed. The canonical run directory contains no
  `human_decision.json` and no `outcome_contract.json`; both commands were exercised on a copy that
  has been deleted.

---

## Human Run readiness

```text
READY
```

Record T0 before viewing any Kriterion decision analysis.
