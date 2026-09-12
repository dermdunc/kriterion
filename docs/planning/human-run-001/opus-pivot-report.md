# Human Run 001 — Pivot and Preparation Report

**Do not read before T2.** This file does not state the synthetic recommendation, but it records
specific observations about the generated page and the run's outputs, which would bias sections 5
and 7 and the Narrative Integrity question in the retrospective.

---

## Pivot

Human Run 001 has been re-registered on a new case.

The previously prepared case was too closely related to a real organisational operating-model
decision to serve as Agentic Tekton's first *public* Kriterion use case. Rather than publish a
sanitised shell of it or abandon it, the two experiments were separated:

| | Retained privately | Human Run 001 |
|---|---|---|
| Case | a real technology operating-model decision | `northstar-internal-developer-platform` |
| Reality | real, accountable, confidential | fictional, explicitly synthetic |
| Location | a private workspace, never committed anywhere | this repository, in full |
| Reproducible by a reader | no | yes |
| State | paused after its first checkpoint | prepared, not yet started |

**What moved out of this repository:** the previous case's preparation report. It documented a
private case and is preserved unmodified in the private workspace.

**What stayed:** all generic methodology — T0/T1/T2, the anchoring checks, the impact labels, the
five falsification conditions, the requirement to record contemporaneous impact, HumanDecision
separation, the OutcomeContract concept, the freeze-before-T0 discipline, the interpretation rules
and the useful-outcomes list. Those were never case-specific, and they were rewritten for Northstar
rather than replaced.

**What was removed as case-specific coupling:** the private case's id was registered in two places
in this repository's source, plus a test module that pinned them. All removed. The private case had
been the only public trace of itself; there is now none.

**Nothing was pushed before the pivot.** The branch has never existed on the remote, and there is
no PR and no merge. Re-registering the public experiment is therefore not a retrospective revision
of a published pre-registration — which matters, because a pre-registration that can be quietly
rewritten after publication is not one.

### Privacy verification

A leak scan was run over every tracked and untracked file in the repository, excluding `.git` and
`.venv`, for the private case id, its superseded id, its run ids, and every operating-model term
specific to it. **Zero hits.** The only surviving mentions of the private workspace are
pre-existing generic references to the sibling directory in `.gitignore`, `.hekton/`, and
`docs/v0-plan.md`, none of which names a case, a decision, a participant or any content.

This repository acknowledges the private run only at the level `protocol.md` and `README.md` state
it: that a separate private practitioner run is retained for a real-world decision where
confidentiality prevents publishing the underlying evidence. Privacy beats narrative completeness,
and even that acknowledgement is optional.

---

## Human Run 001

| | |
|---|---|
| Case id | `northstar-internal-developer-platform` |
| Decision | Should Northstar Software Group invest approximately £3m–£5m over 18 months in an Internal Developer Platform, or pursue a lower-cost programme of incremental toolchain improvements? |
| Underlying tension | Will reducing developer friction create attributable business value, or primarily move complexity and cost from application teams into a new platform organisation? |
| Scenario | Northstar Software Group — **fictional**. ~2,500 engineers; United States, Europe, India; global digital and software products; a fragmented toolchain rather than one coherent platform. All synthetic. |
| Strategies | `do_nothing`, `optimise_existing_toolchain`, `buy_commercial_platform`, `build_thin_internal_platform`, `build_strategic_idp`, `staged_hybrid` |
| Ask | £4,000,000 / 18 months (synthetic; midpoint of the £3m–£5m envelope) |
| NPV low / mid / high | −£6,624,995 / −£4,061,178 / **+£11,748,388** |
| Run | `hr001-northstar-condC-s1`, condition C, seed 1 |

### Evidence

65 items. The boundary that carries the publish claim is the **attestation**, not the category.

| Attestation | Count |
|---|---|
| `REAL` — a public source a reader can check | 20 |
| `AUTHORED` — synthetic scenario input | 45 |

| Category | Count | Attestation |
|---|---|---|
| `EXTERNAL_REFERENCE` | 20 | all `REAL` |
| `MEASURED` | 13 | all `AUTHORED` |
| `UNKNOWN` | 12 | all `AUTHORED` |
| `ASSUMPTION` | 8 | all `AUTHORED` |
| `EXPERT_JUDGMENT` | 6 | all `AUTHORED` |
| `INFERENCE` | 5 | all `AUTHORED` |
| `FORECAST` | 1 | `AUTHORED` |

Distinguishing what the mission asked to be distinguished:

- **Public reference: 20.** DORA and *Accelerate*, SPACE, DevEx, *Team Topologies* (twice), the
  CNCF Platforms White Paper and Maturity Model, InnerSource Commons, *Building Secure and Reliable
  Systems*, Open Policy Agent and NIST SP 800-218, Conway, Backstage practitioner accounts,
  technology-radar cautions, and four items on AI-assisted engineering that disagree with each
  other. Two are deliberately weak and labelled in their own `source` field: an analyst adoption
  forecast (`ev-409`) and a vendor ROI claim (`ev-420`, `VENDOR EVIDENCE — included so that it can
  be challenged, not relied upon`).
- **Synthetic scenario data: 13 `MEASURED` + 6 `EXPERT_JUDGMENT` + 1 `FORECAST` = 20.** Every one
  carries `SYNTHETIC SCENARIO INPUT` or `SYNTHETIC SCENARIO FORECAST` in its claim text and
  "fictional" in its source.
- **Assumptions: 8**, each mirroring a ranged `[[assumptions]]` entry.
- **Inference: 5**, each naming the items it derives from.
- **Unknown: 12.**

**No fictional Northstar number is presented as an observation of a real organisation.** The 13
`MEASURED` items are categorised that way because that is the kind of claim they are inside the
scenario — telemetry rather than opinion — and attested `AUTHORED` because nobody measured
anything. ADR-003 made the two axes orthogonal so this is expressible; the page renders the badge
on every item; and `tests/test_northstar_pack.py` enforces it rather than leaving it to be trusted.

### Citation verification changed the pack, and three of the changes were this case's own bias

Every `REAL` item was independently verified against its published source. Six items were wrong or
overclaimed, and the corrections are worth reporting rather than quietly absorbed:

- **`ev-416` was misattributed.** "Paved road" is Netflix terminology; the Google/O'Reilly security
  text does not use the phrase at all. A confident, plausible, wrong citation — the exact failure
  mode of writing evidence from recall.
- **`ev-402` quoted only half of DORA 2024.** The report finds decreased team-level throughput
  (−1.5%) and stability (−7.2%) per 25-point increase in AI adoption *and* increased individual
  productivity, job satisfaction and code quality. The original item stated only the negative half.
- **`ev-419` quoted only the Thoughtworks Holds.** Three platform anti-patterns are on Hold, but
  "Platform engineering product teams" has been on Adopt since 2021. As written it read as a
  verdict against internal platforms, which is not the source's position.
- **`ev-415` overclaimed** InnerSource acceptance capacity as a measured bottleneck; it is codified
  pattern experience. Downgraded to `LOW`.
- **`ev-417` overclaimed** policy-as-code's effect; the mechanism is documented, the effect on drift
  and exception rates is an open evidence gap.
- **`ev-414`** claimed CNCF status loosely; Backstage is Incubating, not graduated.

The first three matter most, and they matter in a specific way: **each had been written in the
direction that made the case's central tension sharper.** A case about whether platform benefits
are attributable had, unprompted, acquired evidence shaded toward "they are not". That is the bias
an evidence-first instrument exists to catch in its users, appearing in the instrument's own case
pack, and it was caught only because the sources were checked rather than recalled. It is recorded
in `case-design.md` as a property of the case, and the case pack header lists every correction so a
reader can audit the audit.

Residual ceilings, not softened: the pack carries no URLs, and `ev-412`'s 19% magnitude is
provisional — METR has reported a replication on newer tools that did not reproduce a reliable
signal, so the durable claim there is the perception gap, not the number.

### Economics

All figures synthetic and labelled. The benefit chain is explicit because each link is a separate
place the benefit can fail:

```text
engineers reached x adoption x hours saved x hourly cost x attribution
```

| Rank | Assumption | NPV swing |
|---|---|---|
| 1 | `as-benefit-attribution-factor` | £2,949,136 |
| 2 | `as-friction-hours-saved-per-engineer` | £2,821,705 |
| 3 | `as-platform-adoption-rate` | £1,501,875 |
| 4 | `as-platform-team-annual-cost-gbp` | −£1,322,314 |
| 5 | `as-migration-cost-per-engineer-gbp` | −£1,221,074 |
| 6 | `as-fully-loaded-hourly-cost-gbp` | £744,731 |
| 7 | `as-engineers-reached-year-1` | £510,248 |
| 8 | `as-engineers-reached-year-2` | £386,777 |
| 9 | `as-precommitted-capital-gbp` | −£280,992 |

Two properties worth naming:

**The NPV sign flips inside the case's own declared ranges.** A reader who wants a number to
justify either position can find one without leaving the assumptions the case declares. The
decision is not resolvable by arithmetic, which is the point.

**Staging ranks last.** `as-precommitted-capital-gbp` — how much of the envelope is committed
before the first evidence gate — moves NPV by £280,992, while attribution moves it by £2,949,136.
Total capital is identical across the range; only timing changes. **Staging does not save money.**
What it buys is the option to stop and the information on which to exercise it, and the tornado
shows why that is worth having: the quantity staging buys information about is the one the
valuation is ten times more sensitive to. A reader who reads only the NPV column will miss this.

### Challenge perspectives

Five Kriterion seats against six perspectives the case wanted:

| Perspective | Seat |
|---|---|
| CTO | `cto` |
| CFO | `cfo` |
| CISO / Risk | `ciso` + `cro_compliance` |
| Product / Business Leader | `business_executive` |
| Engineering Leader | **none** |
| Developer / Platform Consumer | **none** |

No seat was created. The two missing perspectives are the two closest to the adoption question, and
`ev-438` carries the engineering-leader argument into the ledger as evidence so the committee can
reach it without a seat to voice it.

---

## Product changes

**One generic change was required.** Not `NO PRODUCT CHANGE REQUIRED`, and the justification
matters because the constraint was to change nothing that was not necessary.

`kriterion.economics.case_flows.compute_staged_platform_economics`, plus a shared
`_compute_ranged_economics` helper extracted from the existing Case A path.

**Why the experiment could not proceed honestly without it.** Neither existing model could carry
this case:

- `compute_economics` (Case A) has the right *shape* — a productivity benefit with an attribution
  factor — but bakes Case A's 1,200/5,000 engineer ramp and its £2.07m stage ladder into module
  constants. Pointing Northstar at it would have rendered Case A's headcount and Case A's ladder
  onto Northstar's page as if they were Northstar's own: a 5,000-engineer benefit for a
  2,500-engineer company. That is an objectively false representation, which the constraint
  explicitly names as grounds for a change.
- `compute_cost_only_economics` is honest only for a case whose benefit drivers are all `UNKNOWN`.
  Northstar's are ranged assumptions the pack owns and labels as synthetic, so they can honestly be
  varied. Using the cost-only model would have removed attribution and adoption from the NPV
  entirely, leaving a one-entry tornado — and the case's central question, the one the whole
  decision turns on, would have been invisible to the economics.

**How it was kept generic.** The new cash-flow function holds **no case-specific constant**. Every
parameter is required and keyword-only with no default, so a case pack that omits an assumption
raises rather than silently publishing a number the module invented. A test pins that property.

**Tested.** 377 tests pass, up from 356. Case A's golden economics tests are unchanged and still
pass, which is what proves the shared-helper extraction is behaviour-preserving. The new tests pin
properties rather than arithmetic: no defaults; every parameter classified benefit- or cost-side
exactly once; zero attribution and zero adoption each remove the entire benefit; staging changes
timing not total capital; the NPV sign flips inside the declared ranges; attribution ranks first.

**Deliberately not built.** `/demo`, value-of-information, stage-linked EvidenceRequests, Case B,
portfolio features, new agents, UI redesign, charter architecture changes, a first-class
case-pack schema for the staged-funding ladder, and any fix to the section-1 leak below.

---

## Limitations recorded rather than fixed

- **Section 1 leaks the recommendation.** The generated page's first section states the
  recommendation, its confidence, the capital at risk and the dominant uncertainty at the top, by
  V1 homepage design. Reading it top-to-bottom reveals the recommendation before the section that
  is supposed to. `protocol.md` specifies the required redaction as a numbered reading-order
  caveat. The redaction happens outside the product, which means the blind reveal is not
  implemented — it is performed. If it fails, the run produces no T1 and that must be reported.
- **`Ask.amount_gbp` is a single required float.** The £3m–£5m envelope cannot be expressed.
- **The stage-ladder widget is Case-A-only.** `_stage_ladder` returns an empty list for any other
  case id, so Northstar's ladder is carried by its evidence and its assumption instead.
- **`CaseRealism` has one value, is never loaded from the pack, and is never rendered.** Northstar
  is correctly labelled `AUTHORED_FIXTURE` by the default, which is luck rather than design.
- **Two `None` values render identically.** `avoided_loss_*` is `None` here meaning "not
  applicable" (benefits are priced inside the NPV) and `None` in the cost-only model meaning
  "cannot honestly be stated". Worth watching at section 5.
- **The incremental option is uncosted** (`ev-463`), so the case cannot fairly compare it.

## Standing findings, observed in this run

Recorded before T0 so they are not discovered afterwards. These are **recurrences**, not new:

- **Charter coupling, now measurable.** Five differently chartered seats produced **10
  `EvidenceRequest` records containing 2 distinct requests** — against a case with 12 `UNKNOWN`
  items and seven candidate request areas seeded into the ledger. `case-design.md` pre-registers
  this as a section-7 observation rather than presenting the seats as differentiated.
- **`stop_conditions` is empty**, and `conditions` (7) matches `unresolved_unknowns` (7) in count.
  A recommendation that names conditions but no stop conditions tells a funder what to check and
  never what would make them stop.
- **Belief updates skew argument-driven** — 4 of 5, with 1 evidence-driven and no drift flags.
- **`strongest_dissent` cites specific items** (`ev-460`, `ev-455`, `ev-454`, `ev-453`, `ev-463`).
  This continues to work.
- **Narrative Integrity versus upstream correctness.** The page wrote with 0 violations. That binds
  the prose to the decision state; it says nothing about whether the decision state is right.

---

## Reproducibility

What a public reader can do that they could not before:

* read the complete case pack — 65 evidence items with categories, attestations, sources, strengths
  and cross-references, and 9 ranged assumptions;
* re-run `kriterion econ`, `kriterion ledger freeze` and `kriterion decision-page` and get every
  **value** reproduced exactly;
* check every claim the page makes against the ledger item it cites;
* check the 20 `REAL` sources against the published work they name;
* read the frozen run artifacts and the generated page.

**New product finding: the deterministic commands are deterministic in value, not in bytes — and
the evidence-ledger fingerprint is not a content fingerprint.**

This was measured rather than assumed. Each of `econ`, `ledger freeze` and `decision-page` was run
twice against unchanged inputs and the outputs diffed. Every decision-relevant value is identical:
the NPV triple, peak funding, payback, all nine tornado entries in the same order, all 65 ledger
items with the same categories, attestations and ordering, and the entire page once timestamps and
hashes are masked. The only difference is `created_at`, stamped with the wall-clock time of each
write.

The consequence is the part that matters. `ledger.fingerprint` is computed as
`fingerprint(ledger.items)`, and each item carries its own freshly stamped `created_at`, so **the
fingerprint changes on every freeze even when no evidence has changed.** A fingerprint on a frozen
evidence ledger would be expected to answer "has this evidence been altered since it was frozen?"
It cannot: it answers "was this frozen at a different moment?", which is a question nobody asked.

Severity: it does not affect this run — the committed artifacts are the ones the participant
responds to, and their hashes pin them. It does affect the reproducibility claim the project can
honestly make, which is why `README.md` and `freeze-manifest.md` were corrected to say
**compare values, not bytes** rather than claiming byte-identical reproduction.

Not fixed. Changing the identity semantics of a frozen ledger is a real product decision — it
implies separating content identity from freeze identity, and probably that item `created_at`
should come from the case pack rather than the freeze — and it is not a change to make while
pre-registering an experiment. Recorded as follow-up work.

What a reader cannot do at all: reproduce `kriterion run`. It calls a local language model, so the
positions, challenges, belief updates, evidence requests and recommendation are a **freeze, not a
reproducibility claim about the model**.

---

## Freeze

| | |
|---|---|
| Case pack sha256 | `69dbd1f692dcfdbc78c6c2b48686b48174c67c6e90bdde36c165f3fbb64e1f26` |
| Evidence ledger fingerprint | `bad57982921a5a0a94dd5a86b4601fd243866819b89d6f910667bd0b2941221c` (65 items, version 1) — a freeze identifier, not a content fingerprint; see above |
| Generated page sha256 | `570b36fc44ea3b88342ce4a4886a2c583c6634e69d57242022abed73413af3c5` |
| Run id | `hr001-northstar-condC-s1` (condition C, seed 1) |
| Commits | `3f3c499` economics, `22f03a9` case pack and frozen run, `27e2fdd` pre-registration |

Full per-file hashes, reproduction commands and the integrity check are in `freeze-manifest.md`.

---

## Validation

* **377 tests pass**, up from 356. No skips, no failures.
* **Narrative Integrity: 0 violations.** `kriterion decision-page` refuses to write a failing page,
  so the written page is the pass.
* **`kriterion validate-run`: clean**, no governance violations.
* **Committee: 5/5 initial, 5/5 revised.**
* **Privacy: leak scan returns zero hits** for every private-case term.
* **No `HumanDecision` and no `OutcomeContract` exist.** The run directory contains neither, and
  will not until the experiment is performed.
* **The blank instrument is committed blank.**

---

## Readiness

```text
HUMAN RUN 001 READY
```

## Next step

> Record Northstar T0 before reviewing Kriterion sections 1–8.

Apply the section-1 redaction from `protocol.md` when the page is opened.
