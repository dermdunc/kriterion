# Kriterion Human Run 001 — Case Design

Case id: `northstar-internal-developer-platform`.
Case pack: `cases/northstar-internal-developer-platform/case.toml`, committed in full.

This file records *how* the case was built and where its epistemic boundaries sit. Unlike a case
built on a real organisation's decision, this one can also describe *what it says*, because
everything it says is either public research or invented on purpose.

---

## Decision

> Should Northstar Software Group invest approximately £3m–£5m over the next 18 months in an
> Internal Developer Platform, or pursue a lower-cost programme of incremental improvements to its
> existing engineering toolchain?

The more important underlying question, and the one the case is actually built around:

> Will reducing developer friction create attributable business value, or primarily move complexity
> and cost from application teams into a new platform organisation?

---

## Northstar Software Group is fictional

Stated here, in the case pack header, in every scenario evidence item's claim text, in that item's
`source` field, and as an `AUTHORED` attestation badge on the generated page. Five places, because
this is the claim the whole case depends on being unambiguous.

```text
Northstar Software Group          FICTIONAL

Engineers                         ~2,500
Primary engineering regions       United States, Europe, India
Business                          global digital / software products
Current state                     a substantial but fragmented developer
                                  toolchain rather than one coherent
                                  Internal Developer Platform
```

Those numbers are **synthetic scenario inputs**. Northstar is not a real company, is not a
pseudonym for a real company, and no figure attributed to it anywhere in this repository is an
observation of any real organisation.

---

## Why a fictional case

Kriterion's first public human run needed a decision that is genuinely hard, genuinely
consequential, and **publishable in full**. Those three requirements conflict for any real
decision: the cases most worth instrumenting are exactly the ones whose evidence cannot be
published.

A fictional case resolves the conflict in one direction and pays for it in another.

What it buys:

**Full inspectability.** A reader can read the case pack, re-run the deterministic stages
(`econ`, `ledger freeze`, `decision-page`) and reproduce every value exactly, and check every claim
the page makes against the ledger item it cites. No prior Kriterion run has been inspectable end to
end by someone outside the project.

The reproduction is of values, not bytes — those commands stamp a fresh `created_at` on each write,
so the artifacts hash differently even when nothing has changed. That is recorded below as a
product finding rather than smoothed over, because it means the ledger's own fingerprint cannot
answer whether its evidence has been altered.

**A reduced circularity problem.** The participant has no privileged knowledge of Northstar's
answer, no organisational stake in the outcome, and no remembered facts to substitute for the
case's evidence. That is a real improvement over a self-selected real case, though not a cure: the
participant still authored the scenario.

**A decision that is genuinely open.** The economics come out negative in the base case and
strongly positive at the optimistic end of the *same declared ranges*. The sign flips inside the
case's own assumptions. Nothing about the design guarantees an answer.

What it costs:

**It is not a real decision.** Whatever Human Run 001 shows about the instrument's effect on human
reasoning, it shows it on a decision nobody has to live with. That limitation is not reduced by
making the scenario realistic, and it is the dominant threat to the run's external validity.

---

## Candidate strategies

Six alternatives, of which five are substantive. None is designed to win.

| Alternative | What it is |
|---|---|
| `do_nothing` | Continue with no incremental investment. Kriterion requires this alternative; here it is genuinely distinct from Option A, which does invest. |
| `optimise_existing_toolchain` | Option A. Keep the existing CI/CD, cloud tooling, observability, portals, scripts, docs and support teams; invest incrementally in integration, automation and standardisation. |
| `buy_commercial_platform` | Option B. Adopt a commercial platform/portal/control-plane product and integrate existing enterprise tooling underneath it. |
| `build_thin_internal_platform` | Option C. A deliberately constrained platform over existing enterprise tools: golden paths, self-service, service templates, environment provisioning, policy automation, deployment abstractions, discovery. Does not attempt to replace the underlying tools. |
| `build_strategic_idp` | Option D. Developer experience treated as a major internal product: paved roads, self-service control planes, policy-as-code, service lifecycle management, integrated observability, AI-agent interfaces, platform product management. |
| `staged_hybrid` | Fund discovery and an MVP, then let evidence choose between B, C and D at a gate. |

**Option D is deliberately not the obvious winner.** It carries the largest platform-team operating
cost, the most exposure to the adoption assumption, and the over-platforming failure mode that
`ev-405` and `ev-419` both name directly. Option A carries the lowest disruption and the lowest
upfront commitment — and the case contains no costed comparison of it, recorded as `ev-463`, a
known asymmetry in the case's own construction that makes the platform options look better than a
fair comparison might.

---

## Evidence boundaries

The pack has **65 evidence items**, and the boundary that matters most is not the
`EvidenceCategory` — it is the `Attestation`.

| Attestation | Count | What it means here |
|---|---|---|
| `REAL` | 20 | Drawn from a real, named, public source a reader can check. Used **only** on `EXTERNAL_REFERENCE` items. |
| `AUTHORED` | 45 | A synthetic input invented for this experiment. Every Northstar-specific claim. |

ADR-003 made `Attestation` orthogonal to `EvidenceCategory` precisely so that a fixture could
simulate a measurement without claiming one. Human Run 001 is the first case to use both values in
one pack, and it is what lets the case be simultaneously evidence-rich and honest: real research
about platform engineering sitting next to invented facts about Northstar, with the difference
rendered as a badge on every item rather than explained in a preamble a reader might skip.

`tests/test_northstar_pack.py` enforces the boundary: `REAL` may appear only on
`EXTERNAL_REFERENCE`, every other item must be `AUTHORED`, and every `MEASURED` item must carry
`SYNTHETIC SCENARIO INPUT` in its claim text and "fictional" in its source.

### By epistemic category

| Category | Count | What it holds |
|---|---|---|
| `EXTERNAL_REFERENCE` | 20 | Real public research. |
| `MEASURED` | 13 | Northstar's synthetic baseline. **Not real observations** — see below. |
| `UNKNOWN` | 12 | The quantities the decision needs and does not have. |
| `ASSUMPTION` | 8 | The ranged modelling assumptions the economics spends. |
| `EXPERT_JUDGMENT` | 6 | Synthetic internal judgments from Northstar roles. |
| `INFERENCE` | 5 | Derived within the case, each naming what it rests on. |
| `FORECAST` | 1 | Northstar's own forward-looking planning input on agent-originated change. |

**The `MEASURED` note, because it is the one a reader could get wrong.** Thirteen items describe
Northstar telemetry — onboarding time, CI/CD pattern count, provisioning lead time, support volume,
platform headcount, golden-path coverage, lead-time and change-failure comparisons, documentation
sprawl, policy exceptions, idle cloud spend, AI-agent usage. They are categorised `MEASURED`
because that is the kind of claim they are *inside the scenario*: telemetry rather than opinion.
They are attested `AUTHORED` because nobody measured anything. The category describes the claim's
shape; the attestation describes its reality. Both are rendered on the page.

This is the closest honest classification Kriterion's existing vocabulary offers, and it is
adequate — but only because `Attestation` exists. **`CaseRealism` is not adequate**, and that is
recorded as a standing product limitation rather than patched: the enum has exactly one value,
`AUTHORED_FIXTURE`, it is never loaded from `case.toml`, and it is never rendered. A case pack
cannot declare its own realism and a reader cannot see it. Northstar happens to be correctly
labelled by the default, which is luck rather than design.

### The external evidence, and what it is allowed to carry

Twenty `REAL` items, cited by title, author and publishing organisation. The substantive clusters:

- **Delivery measurement.** DORA / *Accelerate*'s four key metrics (`ev-401`), and the 2024 DORA
  finding that AI adoption was associated with *decreased* delivery throughput and stability
  (`ev-402`).
- **Productivity measurement's limits.** The SPACE framework's claim that no single metric validly
  represents developer productivity (`ev-403`), and the DevEx three-dimension model — feedback
  loops, cognitive load, flow state (`ev-404`).
- **Platform as product.** *Team Topologies* on the thinnest viable platform, and on cognitive load
  being relocated rather than eliminated (`ev-405`, `ev-406`); the CNCF Platforms White Paper and
  Platform Engineering Maturity Model (`ev-407`, `ev-408`).
- **AI and engineering, disagreeing with itself.** A controlled experiment showing a substantial
  speed-up on a narrow greenfield task (`ev-411`); a randomised trial finding experienced
  developers *slower* on their own mature repositories while believing they were faster (`ev-412`);
  an enterprise trial reporting a measurable speed-up (`ev-413`). `ev-411` and `ev-412` carry a
  structural `contradicts` link to each other, as do `ev-402` and `ev-413`.
- **Mechanisms.** Paved roads and secure defaults (`ev-416`); policy-as-code and the SSDF
  (`ev-417`); Conway's Law (`ev-418`); InnerSource's finding that acceptance capacity, not
  contributor willingness, is the usual bottleneck (`ev-415`).
- **Cautions.** Practitioner and technology-radar commentary against platforms built without a
  product mindset and against over-abstraction (`ev-419`); Backstage practitioner accounts that the
  portal is the small part of the work (`ev-414`).

Two items are deliberately weak and labelled so in their own `source` field:

- `ev-409`, the analyst prediction that most software engineering organisations will establish
  platform teams. It is an **adoption forecast, not an outcome measurement** — it says platform
  teams will be common, not that they will work. `LOW`.
- `ev-420`, the vendor ROI claim of payback within twelve months on productivity grounds alone.
  Marked `VENDOR EVIDENCE -- included so that it can be challenged, not relied upon`, `LOW`, and
  carrying `contradicts` links to the SPACE item and to the attribution unknown. It is in the pack
  because the CFO seat needs something to push against, following the same pattern as Case C's
  `ev-105`.

### Provenance: what verification actually changed

Every `REAL` item was independently verified against its published source during preparation —
existence, exact title, authors, publisher, year, and the specific figure quoted. This is recorded
because the check **changed the pack**, which is a more useful fact than a claim of diligence:

| Item | What verification caught |
|---|---|
| `ev-416` | **Misattribution.** "Paved road" is Netflix terminology; the Google/O'Reilly security text does not use the phrase. The item now cites Netflix for the paved road and Google for secure-by-default, separately. |
| `ev-402` | **One-sided.** DORA 2024 reports decreased team-level throughput and stability *and* increased individual productivity, satisfaction and code quality. Quoting only the half that suited this case's tension would have misrepresented the source. Both halves are now stated, with the figures. |
| `ev-419` | **One-sided.** The Thoughtworks Radar puts three platform anti-patterns on Hold but has had "Platform engineering product teams" on Adopt since 2021. Citing only the Holds read as a verdict against internal platforms, which is not the source's position. |
| `ev-415` | **Overclaim.** That acceptance capacity is the dominant InnerSource bottleneck is codified pattern experience, not a measured finding. Labelled as such and downgraded to `LOW`. |
| `ev-417` | **Overclaim.** The policy-as-code mechanism is documented; the effect on drift and exception rates is an open evidence gap. The item now says so. |
| `ev-409`–`ev-414` | Exact figures, sample sizes, confidence intervals and status corrections added — including that Backstage is CNCF *Incubating*, not graduated. |

Three of those six were the case's own bias showing: `ev-402`, `ev-419` and `ev-415` had each been
written in the direction that made the case's tension sharper. That is exactly the failure an
evidence-first instrument is supposed to catch in its users, and it was caught here only because
the sources were checked rather than recalled.

**Residual ceilings, not softened.** The pack carries no URLs, so a reader must resolve sources by
name. And `ev-412`'s magnitude is explicitly provisional: METR has reported that a replication on
newer tools did not reproduce a reliable signal, so the durable claim there is the perception gap,
not the 19 per cent. No claim should be read as stronger than the source it names. Vendor-sponsored
survey evidence (`ev-410`), analyst forecast (`ev-409`), vendor marketing (`ev-420`) and pattern
literature (`ev-415`) are all `LOW`.

### Load-bearing assumptions

Eight `ASSUMPTION` items, each mirroring a ranged entry in `[[assumptions]]`. All are synthetic
scenario inputs and say so. Four carry the decision:

**Productivity attribution** (`as-benefit-attribution-factor`, 0.25, ranged 0.05–0.50). What share
of saved developer time becomes business value rather than being absorbed elsewhere. Nothing in the
case evidences any value in that range, and the range's width is the honest statement of that. It
is contradicted by `ev-403` (no single metric represents productivity) and by `ev-436` (Northstar
has no methodology for converting engineering time into a booked benefit). **It ranks first in the
tornado**, which is the case working as intended: the valuation is most sensitive to the question
the decision is actually about.

**Adoption** (`as-platform-adoption-rate`, 0.60, ranged 0.30–0.85). A platform teams bypass creates
no value however good it is. Contradicted by `ev-438` (teams bypass anything slower than what they
already have) and cautioned against by `ev-419`.

**Platform-team operating cost** (`as-platform-team-annual-cost-gbp`, £1.8m/yr, ranged £1.2m–£2.8m).
Engineers, platform product management, operations, support, maintenance and vendor cost. This is
the cost that continues after the capital programme ends and that the £4m ask does not include.
`ev-406` supplies the mechanism: the cognitive load is relocated to this team, not deleted.

**Scope discipline**, carried structurally rather than as a single number:
`as-engineers-reached-year-1` and `-year-2` separate *reach* from *adoption*, and
`as-migration-cost-per-engineer-gbp` prices the effort application teams spend moving, which the
platform's own budget never shows.

### Unknowns

Twelve, covering what the decision needs and does not have: true productivity attribution; the
adoption rate under voluntary use across heterogeneous workloads; business-value conversion;
long-term platform-team cost; developer behavioural response; effect on defect rate; the direction
of the agentic-engineering effect; build-versus-buy total cost of ownership; whether toolchain
fragmentation is the binding constraint at all; opportunity cost; golden-path control
effectiveness; and the benefit horizon the two-period model truncates.

Two deserve naming as categories rather than items:

- **`ev-460`** — whether fragmentation is Northstar's binding constraint at all, rather than
  business prioritisation, architectural coupling or delivery-process overhead. This is the premise
  the entire decision rests on. If it is false, every option answers a question Northstar does not
  have.
- **`ev-463`** — that the incremental option is not costed anywhere in the pack. Recorded as a known
  asymmetry in the case's construction rather than quietly left out.

**Seeded, not authored.** The seven candidate EvidenceRequest areas the case design contemplates —
baseline friction, support demand, delivery comparison, attribution, adoption, control
effectiveness, AI-agent compatibility — are **not** written into the pack as `EvidenceRequest`
objects. Those are committee output, and authoring them would pre-empt the thing the run measures.
Each is present as the corresponding `UNKNOWN`, so the committee can surface it or fail to. Whether
it does is a measurement, not a design goal.

---

## Economics

`kriterion.economics.case_flows.compute_staged_platform_economics`. Every number the model spends
comes from the pack's own ranged assumptions; the module holds no Northstar constant.

The benefit chain is deliberately explicit, because each link is a separate place the benefit can
fail to appear:

```text
engineers reached
  x adoption rate                  teams can bypass the platform
  x hours saved per engineer       the friction actually removed
  x fully-loaded hourly cost       what an engineer-hour costs
  x attribution factor             the share of saved time that becomes
                                   business value rather than being
                                   absorbed elsewhere
```

The last multiplier is the point. Monetising a productivity saving at full salary equivalence would
assert that every recovered engineer-hour converts into delivered value, which is the "secretly an
ROI calculator" failure mode. Two statements the case makes structurally rather than in prose:

```text
developer hours saved   !=   business value
deployment frequency    !=   revenue
```

### Result

| | |
|---|---|
| Ask | £4,000,000 over 18 months (synthetic; midpoint of the £3m–£5m envelope) |
| NPV, pessimistic | **−£6,624,995** |
| NPV, base | **−£4,061,178** |
| NPV, optimistic | **+£11,748,388** |
| Payback | none within the modelled horizon, on base-case flows |
| Peak funding | £4,724,500 |

**The sign flips inside the case's own declared ranges.** That is the single most useful property
of this case's economics: the decision is not resolvable by arithmetic, and a reader who wants a
number to justify a position can find one in either direction without leaving the ranges the case
declares.

### Sensitivity

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

Attribution ranks first. The three quantities nobody has measured — attribution, hours saved,
adoption — occupy the top three places and between them swing the valuation by more than £7m, while
the entire capital ask is £4m.

### Staged investment, and what the model says about it

The staging ladder the case argues for:

```text
£100k  discovery            establish baselines, prove friction is real
   |
£500k  MVP                  3-5 teams, ~150 engineers
   |
   v  evidence gate
£1.5m  targeted rollout     ~1,000 engineers
   |
   v  evidence gate
       enterprise scale
```

All synthetic. It enters the economics as `as-precommitted-capital-gbp` — how much of the £4m
envelope is committed before the first gate — ranged from £600k (discovery and MVP only, everything
else gated) to £4m (the whole envelope approved up front).

The model's answer is worth stating because it is not the flattering one: **staging moves NPV by
£280,992, the smallest swing in the tornado, while attribution moves it by £2,949,136.** Total
capital is identical across the range; only the timing changes. Staging does not save money.

What it buys is the option to stop, and the information on which to exercise it — and the tornado
shows exactly why that matters, because the quantity staging buys information about is the one the
valuation is ten times more sensitive to.

> When uncertainty is high, buy information before buying scale.

The economics supports that principle for a reason the NPV column alone does not show, and a reader
who reads only the NPV column will miss it. Recorded here as something to watch for at T1.

### Modelling limitations, recorded not corrected

- **Two annual periods.** Matching the two existing Kriterion cash-flow models. Platform benefits
  are generally argued to accrue over longer horizons, so the NPV charges the full build cost
  against at most two years of benefit. Recorded in the ledger as `ev-464`.
- **`Ask.amount_gbp` is a single required float.** The £3m–£5m envelope cannot be expressed; £4m is
  the midpoint. The same limitation the staged ladder runs into, and the reason the ladder lives in
  an assumption rather than in the ask.
- **The stage-ladder widget on the generated page is Case-A-only.** `decision_state._stage_ladder`
  returns an empty list for any other case id, so Northstar's ladder is carried by its evidence and
  its assumption rather than by the page's ladder component. Not fixed: giving the ladder a
  first-class case-pack schema is already named follow-up work and is out of scope here.
- **No avoided-loss band.** This model prices benefits inside the NPV, so there is no separate band
  to report beside it, and `avoided_loss_*` are `None` meaning "not applicable" — the same as
  Case A. That is a different `None` from the cost-only model's, which means "cannot honestly be
  stated". The page renders both identically, which is worth watching at section 5.

---

## Challenge perspectives

Kriterion has **five** charter seats. The case design contemplates six perspectives. The mapping,
and the gap, stated before the run:

| Perspective the case wants | Kriterion seat | Present? |
|---|---|---|
| CTO | `cto` | yes |
| CFO | `cfo` | yes |
| CISO / Risk | `ciso`, `cro_compliance` | yes, split across two seats |
| Product / Business Leader | `business_executive` | yes |
| Engineering Leader | — | **no seat** |
| Developer / Platform Consumer | — | **no seat** |

The two missing perspectives are the two closest to the adoption question, which is the case's
third-most-sensitive assumption and its most plausible failure mode. No new agent was created:
adding seats is explicitly out of scope for this pivot, and a seat invented to serve one case is
the coupling this project already has a finding about. The gap is recorded, and `ev-438` carries
the engineering-leader argument into the ledger as evidence so the committee has access to it even
without a seat to voice it.

**Charter coupling, to be observed rather than fixed.** Every charter's `required_evidence` list
names Case A evidence ids (`ev-007`, `ev-014`, `as-training-cost-per-engineer-gbp`, and so on).
Against the Northstar pack those ids do not resolve. The run proceeds — Case C already demonstrates
that — but the effect on differentiated challenge is a standing open question. **Whether the five
seats produce genuinely distinct evidence needs on this case, or converge, is a Human Run 001
observation to record**, not a thing to fix mid-experiment.

---

## Experiment risks

Recorded in advance, none of them eliminated.

**The decision is not real.** The dominant limitation. Whatever the run shows about the
instrument's effect on reasoning, it shows it on a decision nobody has to live with. No amount of
scenario realism changes that.

**The participant authored the scenario.** The circularity is reduced relative to a real
self-selected case — no privileged knowledge of the answer, no stake in the outcome — but not
eliminated. The participant chose which facts Northstar has.

**Synthetic recommendation anchoring.** The participant may adopt the recommendation and then
retrofit a rationale from earlier sections. The T1 checkpoint is the mitigation and it is
procedural only. Pre-registered falsification condition 3 exists because the mitigation is
imperfect.

**The section-1 leak.** The generated page's first section states the recommendation, its
confidence, the capital at risk and the dominant uncertainty at the top, by V1 homepage design.
The blind reveal therefore depends on a human withholding four lines. `protocol.md` specifies the
redaction; if it fails, the run produces no T1 and that must be reported rather than worked around.

**Participant familiarity with Kriterion.** The participant designed the instrument, knows what
each section is for, knows the hypothesis, and knows what T1 is testing. Demand characteristics
cannot be excluded.

**Weak EvidenceRequests.** `EvidenceRequest`s are committee output, not authored into the case, so
their quality is not under the experimenter's control. Requests without a threshold, an owner or a
falsifiable outcome are to be recorded as weak, not silently upgraded when the results are written
up.

**The incremental option is uncosted.** `ev-463`. The case cannot fairly compare Option A against
the platform options, and a position that moves toward a platform may be moving partly because the
alternative was never priced.

---

## Standing product findings, preserved separately

These predate Human Run 001 and are **not** to be hidden by the Northstar case's design. If any
recurs during the run, it is recorded as a recurrence rather than as a new discovery:

- **Charter coupling** — charters name Case A evidence ids; see above.
- **Inconsistent response to contradiction edges** — the `contradicts` field carries tension
  structurally, and seats have not responded to it consistently across runs. This case has eight
  contradiction edges, including two between `REAL` external items.
- **Narrative Integrity versus upstream epistemic correctness** — Narrative Integrity binds the
  page's prose to the decision state. It does not check whether the decision state is right. A page
  can pass with zero violations and still rest on a badly classified ledger.
- **CaseRealism vocabulary limitation** — one enum value, never loaded from the pack, never
  rendered. Described above.
- **The evidence-ledger fingerprint is not a content fingerprint** — new, found during this
  preparation. `econ`, `ledger freeze` and `decision-page` reproduce every value exactly but stamp
  a fresh `created_at` on each write, and the fingerprint is computed over the items including
  those timestamps. It therefore changes on every freeze even when no evidence has changed, so it
  cannot answer the question a frozen ledger's fingerprint exists to answer. `freeze-manifest.md`
  records the measurement and says to compare values rather than bytes.

---

## Product fit

The case required **one** product change: a new generic economics model,
`compute_staged_platform_economics`, plus a shared helper extracted from the existing Case A path
so the two do not duplicate construction. `opus-pivot-report.md` records why it was necessary
rather than opportunistic, and what was deliberately not built.
