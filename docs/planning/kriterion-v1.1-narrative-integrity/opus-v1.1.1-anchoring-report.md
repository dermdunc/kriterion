# Kriterion V1.1.1 — Anchoring the Architecture, Aligning the Public Story

**Loop:** Opus, solo. No separate adversarial-critique stage, so §Self-adversarial review below
replaces it.
**Date:** 2026-09-12
**Branch:** `agent/fable/kriterion-v1.1-narrative-integrity` (name inherited, kept deliberately)
**Worktree:** `factory-output/kriterion--v1.1-narrative-integrity`
**Base:** continues directly on top of unmerged V1.1 work at `f2f54f9`. `origin/main` is at
`00fc249`.
**Status at handoff:** 4 commits, local, working tree clean. **Nothing pushed, no PR opened,
nothing merged.**
**Tests: 350 passing** (341 at `f2f54f9`, the V1.1 tip, verified before any change).
**Assurance impact: Kriterion-only.** `hekton-assurance-lab` is at `325f786` with a clean tree;
not one file was touched.

| Commit | Scope |
|---|---|
| `cb8f405` | `docs(architecture)` — the two principles anchored as standing, ADR-013, enforcement-scope table, deployment path |
| `37ea133` | `feat(product)` — "How Kriterion earns trust", the assurance boundary in product terms, 9 tests |
| `814e1d7` | `docs` — stale counts corrected, five last-metre defect classes kept, demo backlogged |
| (this file) | `docs(planning)` — the V1.1.1 report |

Diff against the V1.1 tip: 8 files, +529 / −27 of code and documentation, plus this report
(9 files, +1050 / −27 in total). No protected path touched (checked mechanically
against `.github/**`, `infra/**`, `terraform/**`, `.env*`, `*.pem`, `*.key`, `rules/**`,
`.rules/**`, `package.json`, `pyproject.toml`).

---

## Phase 0 — inspection, and the one thing the mission was right to warn about

Read before anything was written: the V1 consolidated report, the V1.1 plan-and-report,
`docs/decisions.md` (ADR-001 to ADR-012, numbering confirmed by grep rather than assumed),
`docs/next-actions.md`, `AGENTS.md`, `.hekton/project.yaml`, `README.md`, `docs/architecture.md`,
`docs/project-walkthrough.md`, `docs/index.html`, `docs/lab.html`,
`src/kriterion/report/decision_page.py`, `src/kriterion/decision_state.py`,
`src/kriterion/narrative.py`, `tests/product/test_public_page_coherence.py`, the build script, the
Pages configuration, and the live site itself.

### The public site and the V1.1 branch are not aligned, and could not be

This is the single most consequential finding of the pass, and the mission's instruction not to
assume alignment was correct.

Verified against the GitHub Pages API (`gh api repos/dermdunc/kriterion/pages`):

```json
"build_type": "legacy", "source": {"branch": "main", "path": "/docs"},
"cname": "kriterion.theagentictekton.com", "https_enforced": true
```

There is no Actions workflow in the repository at all (`.github/workflows/` does not exist). Pages
serves `main:/docs` directly. V1.1 is unmerged. Therefore:

- `curl https://kriterion.theagentictekton.com/` returns HTTP 200 and **the pre-V1.1
  hand-maintained page**: 23,052 bytes, **0** `data-kriterion-source` bindings, and the string
  `hand-maintained` present once.
- The generated page on this branch is 126,714 bytes with **509** bindings.

So every V1-era claim the mission asked to remove is still live **on the site** and already absent
**from this branch**. Regenerating a page is not publishing it. **Publication is a git operation
here, not a build step**, and no agent should perform it. This is now recorded in
`docs/architecture.md` and as the top blocking item in `docs/next-actions.md`.

Website changes live **entirely inside Kriterion**. There is no second repository, no static-site
generator and no deployment layer for content. `infra/github-pages-dns/` is DNS only (Route53 CNAME
plus a verification TXT, Terraform, human-applied); `dig` confirms the CNAME resolves to
`dermdunc.github.io` and the challenge TXT exists at
`_github-pages-challenge-dermdunc.theagentictekton.com`. It carries no content and does not change
when the page does.

### Verifying V1.1's own numbers rather than copying them

The mission said not to trust the prior report's counts. Each load-bearing figure was recounted
from the repository:

| Claim | V1.1 report | Independently verified | Method |
|---|---|---|---|
| Total tests at branch tip | 341 | **341** | `pytest -q`, before any edit |
| Traceable bindings on the page | 509 | **509** | count of `data-kriterion-source=` |
| Narrative-integrity tests | 49 | **49** | `pytest --collect-only` on the file |
| `test_decision_state.py` | 41 | **41** | collection |
| `test_public_page_coherence.py` | 17 | **17** | collection |
| Malformed-artifact cases refused | 16 | **16** | parsed the `MALFORMED_ARTIFACTS` dict keys |
| Byte-identical regeneration | yes | **yes** | ran the build twice, `diff -q` clean |
| Page renders with 0 violations | yes | **yes** | build output, and `check()` called directly |
| `hekton-assurance-lab` untouched at `325f786` | yes | **yes** | `git rev-parse`, clean status |
| `runs/caseA-condC-s0` untouched | yes | **yes** | `git status` on the path, empty |

All ten held. One count elsewhere did **not**: `docs/next-actions.md` stated "45 regression tests"
for narrative integrity where collection says **49**. Corrected, with the correction itself
recorded in the entry — this is the same defect class as V1.1's own 520-versus-509 slip, in the
same increment's paperwork, which is evidence for the discipline rather than against it.

---

## Architecture

### Where the two principles were anchored

**`docs/architecture.md`, in a new "Architectural principles" section**, is the durable home. It
names Principle 1 (*there is one decision state; everything else is a view*) and Principle 2
(*narrative is executable output, not commentary*) with the projection diagram, the enumerated list
of what a narrative statement must not do, and the fail-closed pipeline. The derived consequence —
*publication is a controlled transformation of decision state* — is recorded with its four
operational rules but **deliberately not promoted to a third branded principle**, per the mission's
own instruction.

**ADR-013** was added, and the judgment about *why* matters:

- ADR-011 already owns the decision behind Principle 1; ADR-012 already owns Principle 2. Writing
  new ADRs restating them would be exactly the documentation ceremony the mission warned against,
  so that was not done.
- What ADR-013 adds is genuinely new: it changes their **scope**. Both were argued and implemented
  as decisions about `docs/index.html`. ADR-013 makes them standing and general, binding every
  projection Kriterion adds — reports, CLI output, a future API, a future demo — because each new
  surface is a fresh chance to re-create the V1 defect of a second narrative store.
- ADR-013 also fixes the **canonical-versus-sandbox boundary**, which no existing ADR owned and
  which the demo question requires an answer to before anything is built. That boundary follows
  logically from the generalisation (if every surface is a view of one decision state, a surface
  that lets a visitor change inputs must be a view of a *different, explicitly counterfactual*
  state), which is why one ADR is the coherent unit rather than two.

### The honesty addition: where the principles are enforced versus merely held

Anchoring a principle invites overclaiming that it is enforced everywhere. Architecture.md now
carries a per-surface table stating plainly that **only the generated decision page is mechanically
checked**:

| Surface | Principle 1 | Principle 2 |
|---|---|---|
| `docs/index.html` | Enforced (projection + byte-identity test) | Enforced (bindings, prose scan, publish gate) |
| `runs/*/report.html` | Held by review | **Not enforced** |
| `docs/lab.html` | Held by review | **Not enforced** |
| CLI output | Held by review | **Not enforced** |
| Future API / demo | Bound by ADR-013 before it is built | Bound by ADR-013 before it is built |

Claiming otherwise would repeat precisely the overclaim ADR-010 had to retract.

### Also corrected in architecture.md

The Components table predated V1.1 and did not mention `decision_state.py`, `narrative.py` or the
deliberate two-renderer split. All three added. The CLI command list was stale and wrong: it
advertised a `new` command that does not exist and omitted `validate-run`, `decision-page` and
`perturbation-diff`. Corrected against `kriterion --help` rather than from memory.

### The adversarial findings, preserved as engineering evidence

`docs/project-walkthrough.md` already carried the last-metre finding and its headline, written by
V1.1. It kept only one of the five defect classes. It now keeps all five, each verified against the
code before being written:

1. **Malformed input escaping as a traceback rather than a refusal** — 16 of 16 cases; verified as
   16 parameterised regression tests.
2. **One fact with two answers** — the tornado headline used widest-swing while the table rendered
   stored order under a "widest first" caption; verified fixed by ordering in
   `decision_state.tornado_rows`, whose docstring records the probe that found it.
3. **Text escaping validation through an alternate rendering path** — `title=`, `aria-label`, CSS
   `content:`, and a lowercase recommendation claim; verified as four real regression tests.
4. **A correct figure attributed to the wrong actor** — "capital at risk" under a synthetic
   deferral plus a human pilot.
5. **A count written from memory instead of calculated** — the 520-versus-509 binding slip.

The lesson is stated once, in the journal, and not repeated through the product: *in AI-assisted
decisions, the dangerous error may not occur in the calculation; it may occur in the final metre
between evidence and language.*

---

## Site

All site changes were made **in the generator** (`src/kriterion/report/decision_page.py`) and the
page regenerated through `scripts/build-decision-page.sh`. `docs/index.html` was never hand-edited;
the byte-identity test proves it.

**Added: "How Kriterion earns trust"**, a concise section in product language placed after the
decision experience and before provenance, with a nav entry. Four commitments — one decision state;
narrative is output, not commentary; fail closed; a human remains accountable — plus a short "Where
Kriterion sits" placing Kriterion in the Agentic Tekton ecosystem (Hekton factory produces and
evolves it; Hekton Assurance is one optional evidence producer) while stating that none of it is
needed to read the page. Mechanics are linked, not inlined.

One design decision worth naming: **`_section_trust()` takes no `DecisionState`**, and the signature
is the point. Every statement in it is about how the instrument behaves, not about this decision, so
it cannot read one; binding a claim about the system to a field of this decision would be a false
provenance. It therefore adds **zero** bindings, which is why the count is still 509.

**Changed: the assurance section now states the boundary in product terms.** It previously described
the adapter but never said the thing a reader most needs. It now opens "Kriterion did not produce
this evidence and does not claim to", names Hekton Assurance as the reference producer of the
document contract, says the instrument works the same way when no such documents exist, and labels
these particular documents as authored fixtures rather than the output of a real assurance run. The
`Hekton Assurance → generic evidence → anti-corruption adapter → Kriterion decision evidence` chain
is intact and unchanged in code; only its description improved.

**Changed: the Lab is framed as supporting research.** The provenance section now says Kriterion
experiments on its own decision mechanisms rather than assuming fashionable agent architectures
improve decision quality, and that the Lab is supporting evidence about how the instrument evolves,
not the product. `docs/lab.html` is untouched and intact.

**Fixed: two em-dashes** that V1.1's renderer had silently reintroduced into Kriterion's own copy,
regressing the 2026-09-08 editorial pass, plus one in `README.md`. The four em-dashes that remain on
the page are all inside **bound** values quoting the assurance producer's own fixture text — source
data, not our prose to edit — verified by counting em-dashes in `unbound_text(page)`, which is 0.
This is now a test rather than a habit.

### What was deliberately *not* changed on the site

The homepage information architecture was reviewed against the mission's ten-point hierarchy and
already satisfied it. Decision first (the ask, amount, synthetic recommendation, whether a human
decision exists, the dominant uncertainty, and the NPV triple with the sign-flip reading, all in the
first section); known / assumed / unknown as three separate sections with epistemic class and
attestation per item; the dominant assumption shown with its evidence strength, range and owner
beside a swing worth four times the ask; deterministic economics kept distinct from interpretation;
the assurance boundary; perspectives without making synthetic executives the hero; per-seat "what
would change your mind" from real persisted `EvidenceRequest.would_change`; recommendation strictly
separate from human decision; an honest empty outcome contract; and the Lab as research. Inventing
work here to look productive would have been the wrong call.

Two specific mission suggestions were considered and declined, with reasons:

- **"STILL REQUIRED BEFORE SCALE"** per seat, and an aggregated **"WHAT WOULD MOVE THIS DECISION?"**
  across seats. Both imply a relationship between a requirement and the stage it unlocks. The
  authoritative state does not record that relationship — `stage_ladder_status` on the page says so
  explicitly. Rendering either would be the inference ADR-013 forbids. Recorded internally as
  backlog instead of faked in the product, exactly as the mission instructed.
- **Repositioning the lead.** The page already leads with "An evidence-backed decision instrument
  for uncertain technology investments" and the decision itself. Verified by offset: the decision
  question appears at character 1,046 of body text and the first seat card at 4,848. The only early
  mention of "committee" is in the authored-fixture provenance banner, which is a disclosure, not
  positioning.

---

## Stale narrative removed

Four V1-era claims the mission named. All four are **verbatim present on the live site** and
**absent from this branch**, confirmed by grep on both:

| Claim (live site wording) | Live | This branch |
|---|---|---|
| "it is **hand-maintained narrative**, not a rendered output" | present | absent |
| "a test in `tests/product/` mechanically checks the..." (coherence test as drift stand-in) | present | absent |
| "until 2026-09-11 the run never wrote them to disk" (`EvidenceRequest`s not persisted) | present | absent |
| "derived from **what the run did persist**" (reconstructed "what would change the decision") | present | absent |

They were absent because V1.1 replaced the page wholesale, not because this pass removed them. What
this pass added is **durability**: five more phrases are now in `BANNED_PHRASES` in
`tests/product/test_public_page_coherence.py` (`hand-authored`, `not a rendered output`,
`mechanically checks`, `never wrote them to disk`, `what the run did persist`), joining the six
already there. Each was taken verbatim from the page currently live. Every one was accurate when
written, which is what makes them the most dangerous kind of stale copy: they read as candour.

The page's positive statement of the current state, in product language, is in the provenance
section and the new trust section: it is generated from committed decision state, every value
carries the state path it came from, and a build that cannot re-derive a statement refuses to
publish.

Also corrected outside the page: the `45 → 49` test count in `docs/next-actions.md`; the retired
"hand-maintained" entry in the same file, which was struck through only in its title so the body
still read as a present-tense claim, now explicitly marked historical; and `README.md`'s status
section, which described only the first V1 increment.

---

## Generated-state validation

How the site proves it represents authoritative state, in the order the proofs bite:

1. **Byte identity.** `tests/product/test_public_page_coherence.py::test_the_committed_page_is_exactly_what_the_pipeline_emits`
   asserts `render_decision_page(state) == docs/index.html`. Ran the build twice and diffed: byte
   identical. This is what makes "generated, not hand-maintained" a fact. A one-character hand-edit
   fails it.
2. **Re-derivation of every material claim.** 509 bound elements, each stamped with its state path
   and formatter; `check()` re-resolves each path against the authoritative `DecisionState`,
   re-applies the formatter, and rejects any mismatch. Called directly against the committed page:
   **0 violations**.
3. **Fail-closed publication.** `kriterion decision-page` runs the check as a gate and exits without
   writing on any violation, covered by
   `test_decision_page_refuses_to_write_a_page_that_fails_the_integrity_check`.
4. **Unbound prose is policed too.** No retyped figures, no unbound state vocabulary, no softening
   words, no recommendation claims, and the scan covers `title`/`aria-label`/`alt` attributes and
   CSS `content:` declarations.
5. **The assurance payload cannot drift.** A test regenerates `imported.json` from the committed
   envelope through the adapter and requires an exact match, so the assurance section is generated
   without the projection importing `kriterion.assurance` — the ADR-007 boundary stays where it is,
   still mechanically enforced by `tests/executors/test_boundary.py`.
6. **Determinism.** Pinned timestamp, no wall clock, no iteration over unordered sets, which is what
   makes proof 1 possible at all.
7. **New in this pass: advertised promises are tied to their mechanisms.** The trust section makes
   four claims in product language. A page can assert "fail closed" long after the gate has rotted,
   so the section is not merely rendered, it is bound to the behaviour it advertises: one test
   asserts the checker actually rejects a tampered statement; another asserts the human-accountability
   claim matches `state.human_decision is None`; another asserts the section carries **no** binding
   and renders identically for a different state, so it cannot smuggle a decision claim in.

### The honest limit of proof 7, and of the whole approach

Binding proves a statement is *derived from* the record and cannot be hand-edited without detection.
It does not prove the derived English is a *fair* summary. That stays a human judgment and is the
boundary of this entire architecture — unchanged from V1.1, restated because it is easy to lose.

The trust section is itself the sharpest instance: it is **hand-authored prose that the checker
cannot re-derive**, because there is nothing in decision state to derive it from. Its claims are
kept honest by tests, which is a weaker guarantee than binding and is stated as such rather than
blurred. A reader deserves to know which of the two they are relying on.

---

## Demo recommendation

```text
BACKLOG
```

Sequenced explicitly **after Human Run 001**, recorded as a defined backlog item in
`docs/next-actions.md` with its user goal, candidate interactions, what it must demonstrate, what it
must not become, and its architectural boundary; the boundary itself is recorded in **ADR-013**.

**Reasoning, from investigation rather than default.** A demo would genuinely help comprehension:
the generated page is twelve sections, and a visitor must read a great deal before the mechanism
lands. That is a real problem and the mission's framing of it is right. Three things put it behind
Human Run 001:

1. **It is addition on top of surface area whose value is unmeasured.** V1.1's own closing argument
   is that nobody knows which of the twelve sections a real CFO actually uses, and that the correct
   next increment may be *subtraction*. Building interactive scaffolding around sections a real
   reader ignores would make that discovery more expensive, not cheaper.
2. **It is not trivial after inspection**, which is the mission's own test for building it now. The
   page is deliberately zero-JavaScript, zero-dependency, zero-external-asset (verified: `grep -c
   "<script"` returns 0 for both public pages). ADR-013's constraint that economics must be
   recomputed through the existing deterministic engine rules out a JavaScript NPV — that would be
   precisely the second source of truth Principle 1 forbids — leaving a precomputed scenario grid or
   a server-side call. Either is a real scenario engine, not an afternoon's work.
3. **It is agent-buildable, and that is the argument against doing it now.** The single most
   valuable act available to this project cannot be done by an agent at all. A demo is exactly the
   kind of satisfying, tractable work that would quietly displace it.

**The architectural question the mission asked to resolve, resolved (ADR-013).** A canonical run is
an immutable historical record of what specific models said on a specific date under a specific
protocol; the instrument's entire value rests on that staying true. So: **a canonical run is
read-only to every projection, and exploratory interaction must operate on explicitly labelled
counterfactual state that is never written back.** Concretely, any such surface must (a) start from a
copied fixture, never a mutable handle on committed artifacts; (b) label scenario-derived figures as
scenario figures wherever they appear; (c) recompute economics through the existing deterministic
engine, not a reimplementation; (d) keep the narrative-integrity discipline, because a scenario
sentence overstates as easily as a canonical one; and (e) never write a sandbox human decision
anywhere the canonical case can read it, because ADR-006's separation is not suspended for a demo.

---

## Human Run readiness

**Nothing in the code prevents Human Run 001.** The lifecycle is real and verified end to end:
`kriterion decide` → `kriterion contract` → `kriterion validate-run` → `decision-page`, driven
through the real CLI by `tests/product/test_human_decision_lifecycle.py` (7 tests) over a throwaway
copy of the canonical run. The page states the absence of a human decision honestly and names both
the accountable owner and the command. No `HumanDecision` has been fabricated (RISK-0011);
`runs/caseA-condC-s5/human_decision.json` does not exist, asserted by test.

Five things stand between here and a run worth learning from. Only the first is blocking:

1. **Blocking: the page the human would read is not published.** If the experiment is "sit the
   accountable owner in front of `kriterion.theagentictekton.com`", they would currently read the
   pre-V1.1 hand-maintained page — without per-seat evidence requests, without the trust section,
   and stating that the page is hand-maintained. **Merging this branch is a prerequisite for the
   experiment, not just for tidiness.** A human must do it.
2. **No capture mechanism for the experiment's second question.** `kriterion decide` records
   `--action`, `--disposition`, `--rationale`, `--owner`, `--override` (verified from `--help`).
   Nothing records *which section changed their mind*, which is half of what V1.1 named as the
   experiment's value. This does not need to be built — a paper form or a note file is enough — but
   it needs to be decided **before** the session, because it cannot be reconstructed afterwards, and
   the answer must be captured before the owner reads the page a second time.
3. **The canonical run is seed 5**, outside the pre-registered 0–4 grid and taking no part in any
   comparison. Correct for the product and disclosed on the page; the human should know that the
   page they are reading is not a grid run.
4. **The `would_change` text is often an outcome, not a falsifiable test.** Real model output
   includes "Increase confidence in security and compliance readiness". The mechanism is real and
   the content is weak. This is a protocol finding, and it may limit how useful the "what would
   change your mind" section is to a real reader — which is itself a result worth observing rather
   than fixing first.
5. **`scripts/verify-project.sh` does not exist** on this base (confirmed by `ls`); it lives only on
   an unmerged infra branch. Disclosed, not silently skipped.

The experiment's falsifiable failure mode, unchanged from V1.1 and worth stating in advance: if the
human's recorded rationale restates the synthetic recommendation in their own words without citing
any unknown or assumption the page surfaced, then Kriterion is producing better-organised analysis
rather than better judgment.

---

## Validation

**`.venv/bin/python -m pytest -q` → 350 passed** (341 at the V1.1 tip `f2f54f9`, verified before any
change; +9).

| Suite | Tests |
|---|---|
| `tests/product/test_narrative_integrity.py` | 49 |
| `tests/product/test_decision_state.py` | 41 |
| `tests/product/test_public_page_coherence.py` | **26** (17 before; +9 this pass) |
| `tests/product/test_human_decision_lifecycle.py` | 7 |
| `tests/assurance/test_adapter.py` | 26 |
| `tests/assurance/test_ledger_slice.py` | 4 |
| `tests/executors/test_boundary.py` | 2 |
| `tests/report/test_html.py` | 12 |
| `tests/test_cli.py` | 8 |

Executed beyond the suite, against the mission's own validation list:

- **Public page regeneration**: `bash scripts/build-decision-page.sh` run three times across the
  pass. Final output 126,714 bytes, **0 violations**.
- **Byte-identical output**: built twice into separate copies and `diff -q` clean. The invariant
  still applies and still holds.
- **Narrative-integrity bindings**: **509**, counted by attribute; unchanged, as expected, because
  the new section binds nothing by design. `check()` called directly on the committed page: 0
  violations.
- **Malformed input rejection**: 16 parameterised cases, verified by parsing the parameterisation
  rather than trusting the docstring.
- **Kriterion Lab**: intact and untouched; its research-and-negative-result test passes.
- **`EvidenceRequest` rendering**: per-seat `would_change` present from the stored artifact, with the
  test asserting every rendered request has non-empty `would_change`.
- **Synthetic/human separation**: enforced by `separation.human_ai` rules and region tests; no human
  decision fabricated.
- **Assurance adapter**: 26 tests pass; the committed payload still matches what the adapter emits
  from the committed envelope; `test_boundary.py` still forbids the import edge.
- **Deployment build**: there is none, and that is the finding. Pages builds `main:/docs` itself;
  no workflow exists. Verified against the Pages API and by `dig` on both DNS records.
- **Mutation testing of the new tests.** Every new phrase and structure assertion was fed a page
  mutated to reintroduce exactly what it forbids: dropping a trust commitment, binding a decision
  field inside the trust section, re-adding an em-dash to Kriterion's own copy, re-adding
  "hand-authored", re-adding "what the run did persist", dropping the ecosystem placement, and
  claiming Kriterion produced the assurance evidence. **7 of 7 caught.** The tests bite; they do not
  merely pass.

Unchanged and verified unchanged: `runs/caseA-condC-s0` and all committed V0 demo runs (`git status`
on the paths, empty), `report/html.py`, every committed `report.html`, `docs/lab.html`,
`infra/**`, `pyproject.toml`. `hekton-assurance-lab` at `325f786`, clean tree, zero files touched.

---

## Self-adversarial review

This replaces the missing critique stage. Findings against my own work, in the order they were
found.

**1. I nearly shipped an overclaim in my own new copy.** The trust section's first draft said the
page, the per-run decision record and the command line "are all views of that record". Per the
enforcement table I had just written two files earlier, `report/html.py` reads the same artifacts
through its *own* loaders, not the projection, and is not under the checker. The sentence was
defensible on one reading and false on the more natural one — which is the exact shape of defect
this increment exists to prevent, committed by the person writing the section about preventing it.
Rewritten to say that every view reads the record rather than keeping its own copy of the story, and
that **this page is the view where that is checked mechanically**. The fifth entry in the journal's
defect classes applies to me, not just to V1.1.

**2. Anchoring a principle invites claiming it is enforced everywhere.** My first draft of
architecture.md asserted the principles "bind every projection" with no statement of coverage. That
is how ADR-010's overclaim happened. Added the per-surface enforcement table and the explicit note
that extending the checker is named work, not done work.

**3. A new unbound section is new unbound surface area.** The trust section is, structurally, the
thing Principle 1 warns about: hand-authored narrative on the page. I decided it is legitimate —
it describes the instrument, not the decision, and unbound explanatory prose is a sanctioned
category that the prose rules still police — but that "legitimate" is a judgment, so I made it
checkable instead of merely asserted: a test proves it carries no binding, another proves it renders
identically for a different state, and three more tie its promises to the mechanisms behind them.
`_section_trust()` takes no state so the property is visible in the signature. I am not claiming
this is as strong as binding, and the report says so above.

**4. Found while grepping, not while reading: the editorial standard had silently regressed.** The
2026-09-08 ADR records a hand-done pass removing every em-dash from audience-facing copy. V1.1's
renderer reintroduced two into Kriterion's own copy and one into `README.md`. A hand-done standard
with no test regressed within one increment. Fixed, and made a test scoped to unbound text so
verbatim producer fixture data stays exempt by construction rather than by remembering to.

**5. The mission asked for a section I declined to build, twice.** Aggregating evidence requests and
a per-seat "still required before scale" both need a requirement-to-stage relationship that the
authoritative state does not record. The mission's own instruction covers this ("if stage linkage
remains backlog work, say so internally rather than faking it in the product"), and following the
suggestion literally would have contradicted the ADR I was writing in the same pass.

### The finding I am naming but did not fix

**`docs/lab.html` is now the remaining hand-authored narrative store on the public site**, and it
carries hand-typed research figures. Three, specifically: the single-context baseline drifted on
"1 of 4" perturbations and the committee on "0 of 4"; Case C's comparison is "provisional, 2 of 3";
and "three of five seeds folded". I checked the first two against the artifact rather than assuming:
`runs/compare-caseA-final/comparison.json` records `perturbation_drift_rate {"A": 0.25, "C": 0.0}`,
which agrees. So the figures are **currently correct, and nothing mechanically keeps them correct.**

That is precisely the ADR-010 arrangement the decision page has now outgrown, still standing one
file over. I did not fix it: the Lab is research output, generating it means a renderer over
`comparison.json` plus per-seed artifacts, and this is a consolidation increment whose scope guard I
would be breaking. It is named in `docs/next-actions.md` and in the enforcement table, and it is the
strongest candidate for the next application of Principle 1.

### Limits I am not claiming past

1. **Binding proves derivation, not fairness.** Unchanged, and the boundary of the whole approach.
2. **The trust section's claims rest on tests, not bindings.** Weaker, and stated rather than
   blurred.
3. **The checker sees only what it is pointed at.** V1.1 closed four routes by probing; I added no
   new routes and found no fifth, which is not the same as there being none.
4. **One case, one run, one condition.** Nothing here is validated across cases.
5. **I did not read the rendered page in a browser.** I read the generated HTML, extracted its text
   in document order, and checked structure and ordering mechanically. Visual hierarchy, mobile
   layout and whether a reader's eye lands where the section order intends are unverified.
6. **"The site now tells the truth" is true of this branch, not of the live site**, and will remain
   untrue of the live site until a human merges. That is the most important limit on this report.

---

## Next step

**Merge this branch to `main`.**

One action, and it is deliberately the smallest one. It is the only thing that converts every claim
in this report from true-in-the-repository to true-on-the-website, it is the prerequisite for Human
Run 001 to be run against the page this work produced rather than the page it replaced, and it is
the one step an agent must not take. Everything else — Human Run 001 itself, projecting the Lab's
figures, the demo — is correctly sequenced behind it.
