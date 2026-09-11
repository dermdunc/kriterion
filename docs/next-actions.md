# Next Actions: Kriterion

Planning is complete. The authoritative plan is [`v0-plan.md`](v0-plan.md); these are the first
tasks from its Weekend Build Plan (§12), in dependency order. Do not re-plan product architecture —
`§15` of the plan contains a ready-to-run build-loop prompt.

## Immediate — Saturday AM (critical path)

- [x] **Get explicit human approval for `pyproject.toml`** — it is a protected path under
      `~/hekton/.rules/git-contract.md:213`. Approved 2026-09-05 via AskUserQuestion.
- [x] **Task 1** — `pyproject.toml` (name `kriterion`, py≥3.11, console script, **zero runtime
      dependencies**), `src/kriterion/` skeleton, pytest wiring.
      *Accept:* `pip install -e . && kriterion --help` — done, verified 2026-09-05 (branch
      `agent/claude/task-1-scaffold`, 2 tests passing).
- [x] **Task 2** — Domain dataclasses (`domain/*.py`): all §4 types, canonical-JSON serialisation,
      sha256 fingerprint helper, `attestation` enforced on every `EvidenceItem`.
      *Accept:* round-trip tests pass; fingerprint stable under key reordering — done 2026-09-05,
      12 tests passing (branch `agent/claude/task-2-domain-model`).
- [x] **Task 3** — Case A pack (`cases/coding-agent-rollout/case.toml`) with full ledger;
      `kriterion ledger freeze`.
      *Accept:* fingerprinted ledger produced; bad category and missing attestation both rejected —
      done 2026-09-05, 26 evidence items across all 7 categories, 23 tests passing total (branch
      `agent/claude/task-3-case-a-ledger`). Phase-6 evidence-injection fixture (the study
      contradicting the 18% uplift assumption, supporting 8-11%) is deliberately NOT in this
      ledger — that's phase-6 input, built with task 10/13, not part of the v1 freeze.
- [x] **Task 4** — ADRs 001–006 already recorded in `docs/decisions.md`; populate
      `.hekton/project.yaml` `architecture.consumes: [hekton-local-llm (provider surface)]`.
      Done 2026-09-05 alongside Task 1 (same branch — both were pure scaffold/metadata, no
      dependency on Task 2/3's code).

## This Week — Saturday PM / Sunday (critical path)

- [x] **Task 5–6** — `economics/engine.py` + golden tests (P0-01, P0-02); staged-funding view.
      Done 2026-09-05: generic engine (npv/payback/peak-funding/tornado) golden-tested on clean
      synthetic fixtures; Case A's own cash-flow model in `economics/case_flows.py` with an
      explicit `benefit-attribution-factor` assumption motivated by `ev-024`. `kriterion econ`
      writes `economics.json`. 36 tests passing total (branch `agent/claude/task-5-6-economics`).
      Staged-funding **rendering** (the ladder view) is task 15's job (report/html.py) — the
      underlying stage budget numbers already exist in `case_flows.py`'s constants.
- [x] **Task 7** — Executor port + `hekton_local.py`, bound to the **source** signature at
      `hekton_llm/ollama_client.py:34` (the interface doc is stale), plus `replay.py`.
      *Accept:* `kriterion doctor` green; smoke completion returns schema-valid JSON — done
      2026-09-05, verified live: `{"ok": true}`. 48 tests passing (branch
      `agent/claude/task-7-executors`). **Carry to task 16:** document the `pip install -e
      ../../platform/hekton-local-llm` dev-setup step in `docs/setup.md` — not a declared
      pyproject.toml dependency, by design. `runtime_provenance`/`model_digests` confirmed
      available but not yet wired into a run manifest — that's task 8/10's job.
- [x] **Task 8** — **Strong Baseline A** + phases 0–4 + Baseline B aggregator. If Baseline A is
      being weakened, stop: that is the experiment. (Task 9 done first — see below — since this
      task's "all five charters' checklists collapsed" needs real charter content to exist.)
      Done 2026-09-05, live-verified twice against real Ollama, not just mocked: 5/5 Baseline B
      members responded validly (modal DEFER 3/5, CFO+CISO dissenting on their real charter
      concerns); Baseline A converged on DEFER with a belief update correctly citing the injected
      `ev-027` study. **Two real bugs found only by running live** — see docs/decisions.md for
      full detail: (1) `OllamaClient.generate()` is stateless, so Baseline A's multi-call context
      had to be explicitly re-sent every call, not assumed carried over — **task 10 must not repeat
      this for phases 5-8**; (2) step 7 had no validation/retry and crashed when the model
      confused the decision vocabulary with the case's alternatives — fixed with
      `parse_revision_response` and a clarified prompt. 71 tests passing (branch
      `agent/claude/task-8-baseline-a-b`). Charter hashes still not yet in a `manifest.json` (no
      manifest file exists yet) — carried to task 10, where the full run manifest gets built.
- [x] **Task 9 of 9–10** — Charters v1 (five TOML files in `charters/`); required-evidence sets
      cross-checked against the live Case A ledger. *Accept:* charter hashes computable and stable
      (`fingerprint()`) — done 2026-09-05, 55 tests passing (branch `agent/claude/task-9-charters`).
      Charter hashes actually **landing in `manifest.json`** is deferred to Task 8/10, where the
      run manifest itself gets built.
- [x] **Task 10 of 9–10** — Phases 5–8 including the deterministic chair and BeliefUpdate
      derivation. *The no-tally-before-phase-8 unit test must pass.* Done 2026-09-05 —
      `tests/protocol/test_no_tally_invariant.py` passes; `kriterion run --condition C` live-verified
      twice end-to-end (5/5 initial, 5/5 revised, zero abstentions, final action DEFER, matching
      both baselines from task 8). Two more real bugs found only by running live — see
      docs/decisions.md: a literal syntax error from a bad patch (caught by `ast.parse` before
      wasting a 7-min run), and phase 7's `blocking_unknowns` initially came back as bare evidence
      ids instead of descriptive text. 90 tests passing (branch `agent/claude/task-10-phases-5-8`).
      Charter hashes / prompt-template hashes still not in a real `manifest.json` — no run-manifest
      file has been built at all yet across tasks 7-10; carried forward again, now genuinely needed
      before task 13's eval harness can cite it.
- [x] **Task 11 of 11–12** — `kriterion decide` / `kriterion contract`. Done 2026-09-05:
      `kriterion validate-run` implements P0-09 for real (funding action without a contract exits
      1, with the exact violation named); `decide` warns immediately rather than leaving the gap
      to be found later; `contract` refuses to run without a prior decision or for a non-funding
      action. 100 tests passing (branch `agent/claude/task-11-decide-contract`).
- [x] **Task 12 of 11–12** — Case C pack (negative NPV by construction). Done 2026-09-05, live
      verified (NPV negative in all 3 scenarios, both baselines run cleanly). Found and fixed a
      real cross-case bug: phase 3 was filtering evidence to `charter.required_evidence`
      (Case-A-specific ids), causing 3/5 members to abstain on Case C — now always shows the full
      ledger. **Carry forward:** charter `concerns`/`standard_challenges` text still has some
      Case-A-specific phrasing ("pilot") that doesn't quite fit Case C — cosmetic, not blocking,
      worth a pass whenever charters are next touched. 109 tests passing
      (branch `agent/claude/task-12-case-c`).
- [x] **Task 13 of 13–16** — Eval harness with all ten P0 fixtures. Done 2026-09-05: 10 pure
      scorers (`evals/scorers.py`), opportunistic harness (`evals/harness.py`,
      `kriterion evals <run-id> --case-id <id>`), `run-export.json` output. Found and fixed a real
      false-positive bug (P0-06 fired on genuine 5-way unanimous convergence, not an actual 4-vs-1
      dissent) via live verification — see docs/decisions.md. 137 tests passing (branch
      `agent/claude/task-13-eval-harness`).
- [x] **Task 14 of 14–16** — `kriterion compare` + `docs/experiment-plan.md` written **before**
      any comparison batch runs (per docs/v0-plan.md §6). Done 2026-09-06: `compare.py` aggregates
      `positions_initial.json`/`positions_revised.json`/`belief_updates.json`/`recommendation.json`/
      `run-export.json` across a seed batch per condition into `ConditionMetrics` (unsupported-claim
      rate, category-inflation/numeric-alteration counts re-derived from the harness's own P0-05/
      P0-03 verdicts rather than rescored, belief-update rationality, dissent non-empty rate, unique
      evidence-refs-per-seat, P0 pass rate), and applies the pre-registered honest-negative criterion
      honestly — reports "not evaluable" (not a silent pass/fail) when fewer than 3 conditions or
      fewer than 2 seeds per condition are present, and flags the perturbation-robustness sub-metric
      as not-yet-computed rather than treating 2-of-2-available as the full 2-of-3 criterion.
      `docs/experiment-plan.md` also fixes the previously-qualitative-only Local LLM quality kill
      criterion 4 with two numeric thresholds (20% `abstained_error` rate; no measurable role-
      diversity difference across all 5 seeds), closing the `INT-2026-09-05-002` disproof_criteria
      #4 gap flagged since task 7. `kriterion run --condition A` also now exposes
      `initial_position` on `BaselineAResult` and writes `positions_initial.json`/
      `belief_updates.json` for Baseline A runs — needed because `compare` couldn't previously find
      Baseline A's own rich intermediate content as a run artifact at all (B/C already had it).
      146 tests passing; live-verified against real `a-s0`/`a-s1`/`b-s0` run data on this machine —
      condition metrics compute correctly and the "need all three conditions" path fires as
      designed (branch `agent/claude/task-13-eval-harness`, same branch as task 13).
      **Not done, carried to task 14b/15/16:** the actual 30+16-run pre-registered grid has not
      been executed (a separate multi-hour activity); token/latency-per-call capture remains
      process-level wall-clock only; role-diversity is the simplified evidence-refs proxy, not the
      fuller n-gram-overlap version — all three are named as known gaps in
      `docs/experiment-plan.md` itself, not silently absorbed.
- [x] **Task 15 of 15–16** — `report/html.py`: five views (the decision, evidence map,
      independent positions + the numbers, what changed minds, decision record), stdlib string
      templating only, self-contained, printable, no JS/server. Done 2026-09-06: every section is
      opportunistic like the eval harness — Baseline B's missing belief updates and missing
      synthesized recommendation render an honest note rather than an empty or broken section.
      Two real gaps closed to make this possible: `load_outcome_contract` added to `decisions.py`
      (only `load_human_decision` existed) and `load_baseline_b_result` added to
      `evals/run_loader.py`, both reusing the existing loader pattern rather than duplicating JSON
      deserialisation. Two judgment calls, stated rather than left implicit (v0-plan.md's own
      wording doesn't fully specify either): the 7-category epistemic taxonomy's grouping into the
      view's 3 display columns (SUPPORTED = MEASURED/EXTERNAL_REFERENCE/EXPERT_JUDGMENT; ASSUMED =
      FORECAST/ASSUMPTION/INFERENCE; UNKNOWN = UNKNOWN); and the staged-funding ladder, sourced as
      display-only figures matching `economics/case_flows.py`'s own Case-A-only constants rather
      than plumbing a new field through the shipped, tested `EconomicsResult`/`Scenario` domain
      types for V0's one staged-funding case. 158 tests passing (12 new). **Live-verified against
      real `a-s0` (Baseline A) and `b-s0` (Baseline B) run data** — found and fixed a real
      formatting bug only visible against real output (negative NPV rendered `£-5,351,240` instead
      of `-£5,351,240`). **Not live-verified: the Treatment C path** (challenges, revised
      positions, multi-member belief updates, chair narrative) — a live seed-0 Case-A run was
      started to exercise it but deferred (killed) mid-run at the human's request; the code path
      is exercised only by synthetic unit tests (`tests/report/test_html.py`), not real model
      output, and should be live-verified before this report is trusted for a real demo. **Not
      done, explicitly deferred, an open question for the human per `docs/v0-plan.md` line 1012**:
      whether a curated Case A demo run gets committed to this public repo (`runs/*/` is
      gitignored except via an explicit `!`-negation task 15 was meant to add) — no run was
      committed this session.
- [x] **Task 16a** — `docs/setup.md`'s two TODOs. Done 2026-09-06: five concrete steps (editable
      install with `dev` extras; the `hekton_llm` dev dependency's separate editable install path,
      carried from task 7 — distribution name `local-llm-lab` vs. import namespace `hekton_llm`
      named explicitly as upstream, not a typo; Ollama + target model pull; `kriterion doctor` as
      the live-chain check, not just an install check; `pytest`, noted as needing no live model
      calls). No code changed; verified accurate against `hekton_local.py` and the real
      `OllamaClient.__init__` default (`http://localhost:11434`) and the real monorepo path.
- [x] **Task 16b** — Started 2026-09-06: `scripts/run-comparison-grid.sh` running
      live against Ollama (the 30-run base grid only — the 16 perturbation-pair runs stay blocked
      on unbuilt P1 machinery, see the script's own header). **Real bug found and fixed mid-batch,
      not after:** `OllamaClient`'s default 120s timeout was too tight for Baseline A's longer
      free-text calls (case_against/premortem) at 14B scale on this hardware — 3/5 seed runs
      (`caseA-condA-s2/s3/s4`) crashed with a raw, uncaught `TimeoutError` traceback instead of a
      diagnosable failure, because `HektonLocalExecutor.complete()` only caught
      `OllamaConnectionError`, not the bare `TimeoutError` the stdlib socket layer raises directly
      on a slow response body (this same gap exists for phase 3/5/7's calls too, not just Baseline
      A's — not retrofitted with retry-then-abstain under time pressure mid-batch, since Baseline A
      must not be weakened per its own ADR; a calmer follow-up should consider it). Fixed: executor
      timeout raised to 300s, `TimeoutError` now caught and converted to a clear `ExecutorError`
      (`src/kriterion/executors/hekton_local.py`) — fixed in Kriterion's own executor layer, not
      `hekton_local_llm`'s `OllamaClient` itself (ADR-001: dependency direction is one-way). Fix
      applies automatically to every run the grid launches from here on (each is a fresh `python
      -m kriterion.cli run` subprocess); it does not retroactively fix the 3 already-failed runs.
      `scripts/retry-failed-grid-runs.sh` re-runs anything marked FAILED in `runs/grid-summary.log`
      and refreshes `kriterion compare` for any case it touches — chained to run automatically once
      the main grid's own "Grid complete" line appears, so the 3 Baseline A failures get retried
      with the fix once the base grid finishes, without competing with it for the one local Ollama
      instance in the meantime.

      **Complete as of 2026-09-06.** All 30 runs clean (25 first-pass + 3 retried after the
      timeout fix + 1 manual retry + 1 re-scored after a second real bug, below). One more real
      bug found and fixed, this time in the eval harness itself: `caseC-condC-s2` reproducibly
      tripped P0-06. Got an independent second opinion via `codex exec -s read-only` before
      touching the harness (see docs/decisions.md for the full exchange) — confirmed this was a
      false positive, not a real dissent-preservation defect: CISO moved `REQUEST_EVIDENCE` ->
      `DISCOVERY`, diverging FURTHER from the majority's `DEFER`, not toward it, and the harness's
      own trigger checked the FINAL 4-vs-1 shape, which structurally can never catch a genuine
      fold (a real fold erases the minority shape by the time you'd check it). Fixed both
      `score_minority_holds` (judges "holding" by conservatism-rank distance now, not literal
      `change_type == no_change`) and the harness trigger (checks the SEEDED phase-3 shape, not
      the revised one). Re-scoring confirmed the diagnosis precisely: at phase 3, CFO's own
      initial position was `REJECT`, not `DEFER` — never a real seeded minority to begin with.
      **Also surfaced, not fixed (separate, tracked below):** `BeliefUpdate.drift_flags` is never
      computed anywhere in `protocol/` despite being a documented harness-written field since
      early in the build; `parse_revision_response` rejects `ch:`-prefixed (challenge-artifact)
      trigger refs even though the plan allows them as meaningful triggers. 162 tests passing (5
      new). **Headline result, unchanged by the fix, on fully corrected data across all 30 runs:**
      `kriterion compare`'s pre-registered honest-negative criterion fired `True` for **both**
      cases — Treatment C beat neither baseline on either available sub-metric. Per
      `docs/experiment-plan.md` this is a successful V0 outcome, still provisional pending the P1
      perturbation batch. **Also worth naming honestly:** across all 10 real Treatment C runs in
      this batch, P0-06's seeded 4-vs-1-minority scenario never occurred naturally even once —
      the fixture is correctly implemented now but this batch doesn't actually exercise it; a
      dedicated synthetic/seeded invocation would be needed to validate it, per the harness's own
      "opportunistic, never fake a tested condition" design note in `evals/harness.py`.
      `runs/compare-caseA/` and `runs/compare-caseC/` hold the final `comparison.json`/`.md`.

## Later

- [x] **`BeliefUpdate.drift_flags` derivation + the `ch:` trigger-ref rejection bug.** Done
      2026-09-06: `protocol/drift.py`'s `derive_drift_flags`, wired into `run_phase7_revised_assessment`
      right after parsing; `ch:` ids now accepted as valid trigger_refs and the phase-7 prompt
      says so explicitly. 175 tests passing (13 new). See docs/decisions.md for the full account,
      including the stated judgment calls (echo's 0.3 n-gram-overlap threshold especially — not
      numerically specified anywhere in the plan). **Not retroactively applied to the
      already-completed 30-run batch** — those `belief_updates.json` files still read
      `drift_flags: []`; recomputing after the fact from each run's own saved artifacts is
      possible but wasn't requested and changes no current `kriterion compare` metric.
- [x] **Live-batch validation of the fixed P0-06 fixture.** Resolved 2026-09-06, better than
      planned: rather than a constructed/synthetic invocation, Treatment D's first live seed
      (`caseA-condD-s0`, below) naturally produced a genuine seeded 4-vs-1 minority (CISO), and
      P0-06 correctly scored it as held. Real live behaviour, not a forced scenario.
- [x] **P1 perturbation-pair evals.** Implemented, run, and complete 2026-09-07: 4 perturbations
      (`framing_flip`, `sponsor_endorsement`, `anchoring`, `evidence_reorder`, `perturbations.py`)
      x 2 conditions (A, C) x seed 0 = 8 pairs, matching the pre-registered "Case A under
      conditions A and C only" design exactly. `kriterion perturbation-diff` added; `kriterion
      compare` extended with an optional `--perturbation-pairs` flag computing a per-condition
      drift rate. 190 tests passing (13 new across this batch's work).

      **Real finding:** `framing_flip` flipped Baseline A's action `DEFER` → `PILOT` — optimistic
      reframing of identical facts changed a funding-adjacent recommendation. Treatment C did not
      drift under the same perturbation. Across all 4: A drifted 1/4, C drifted 0/4 — C wins this
      sub-metric, completing the honest-negative criterion's 3rd sub-metric for the first time.
      **Verdict, all 3 sub-metrics now available (not "provisional on 2 of 3")**: fired `True` — C
      beats A/B on only 1 of the 3 required sub-metrics (perturbation robustness), not the ≥2
      needed. Correction caught on external review before publishing (2026-09-07, full account in
      docs/decisions.md): "fully computed" overstated it — the pre-registered criterion also
      requires beating by a `>2x` seed-stddev margin and a `>2x` inference-cost condition, neither
      of which `compare_conditions` actually checks (bare aggregate comparison only). A stricter
      check can only reduce a "beats" count, never increase it, so the conclusion doesn't change,
      but the "fully computed" claim was retracted. Also disclosed: 2 of the 8 perturbation runs
      (`caseA-condC-s0-framing_flip`, `caseA-condC-s0-sponsor_endorsement`) have `all_green: false`
      — a real P0-05 category-inflation finding in each.

      **A second real prompt bug found and fixed:** `_format_challenges` (`protocol/phases.py`)
      never rendered a challenge's real `id`, only `[type]`. A model that wanted to cite one
      (valid per the earlier `ch:`-trigger fix) had to guess the id format and guessed wrong
      every time, causing a reproducible 5/5 phase-7 abstention under `framing_flip`/C — caught by
      direct reproduction (capturing `RevisionOutcome.raw_attempts`, not guessing), fixed, and
      live-reverified before re-running the official batch entry. Latent but unexercised in every
      prior Condition C run this session, since those models only ever cited bare `ev-` ids — the
      already-committed 30-run grid, Treatment D batch, and demo run are unaffected.
      `runs/compare-caseA-final/` has the complete result. Not yet committed to the repo (open
      question below, matching the demo run's own precedent).
- [x] **Treatment D — heterogeneous per-role models.** Implemented and live-verified 2026-09-06:
      `run_phase5_challenge` gained an optional `executor_by_seat` param (Conditions B/C
      unaffected, confirmed by re-running their existing tests unchanged); `--condition D` wired
      into `kriterion run`; `TREATMENT_D_MODEL_BY_SEAT` assigns 5 distinct model
      families/sizes (see docs/decisions.md for the full rationale and the judgment call it
      required — the plan names the condition but not the assignment). 177 tests passing (1 new).
      **Real finding on the first live seed:** genuine role-level position spread (CISO landed on
      `REQUEST_EVIDENCE` while the other four converged on `DEFER`) — the first time this session
      has seen ANY spread, after all 5 homogeneous Condition C seeds converged uniformly. Also the
      first real, naturally-occurring P0-06 pass this session (not synthetic) — closes the
      "dedicated seeded P0-06 invocation" gap above better than a constructed one would have,
      since it's genuine live behaviour, not a forced scenario.

      **Full 5-seed batch complete, 2026-09-07 — a real, coherent finding, not noise:** CISO
      (`mistral:7b`) held its seeded minority in 2/5 seeds and folded fully into the majority
      `DEFER` in 3/5. Checked whether the folds were legitimate before calling this a finding:
      all three folds are `drift_flags: ['retrofit']` (cites only pre-existing, non-injected,
      non-challenge evidence to justify the change), and neither hold is. Consistent pattern,
      not three coincidences — heterogeneity did not fix dissent-preservation here, it made one
      specific model's unreliability visible and measurable, which is arguably the more useful
      outcome. Separately: `cro_compliance` (`gemma4:12b`) abstained_error at phase 7 in 4/5
      seeds (80%) despite succeeding at phase 3 every time — named as a real data point, though
      the batch-wide abstained_error rate (5/50 calls) stays under kill criterion 4's 20%
      threshold (that criterion is scoped to the standard all-`qwen2.5:14b-instruct` committee,
      not evaluated against this stretch condition). `kriterion compare` with D as a fourth group:
      P0 pass rate 0.94 and belief-update rationality 0.84, both worse than A/B/C's 1.0 — see
      `runs/compare-caseA-with-D/comparison.md`. Full account in docs/decisions.md. **Not yet
      committed to the public repo** — an open question below, matching the original Case A demo
      run's own precedent.
- [ ] P2 judge-scored evals with the blind human calibration sample.
- [ ] Case B (`international-platform-capability`) — deferred from V0; first case added afterwards.
- [ ] Synthetic retrospective as a clearly labelled mock artifact for the demo's closing beat.

## Open questions for the human (see `v0-plan.md` appendix)

- [x] Is the curated Case A demo run committed to the public repo? **Yes, decided 2026-09-06.**
      `runs/caseA-condA-s0/`, `runs/caseA-condB-s0/`, `runs/caseA-condC-s0/` (all three conditions,
      seed 0, for direct comparison) plus `runs/compare-caseA/` are un-gitignored and committed,
      including each run's generated `report.html`. Chosen as the first pre-registered seed
      specifically to avoid any appearance of cherry-picking a better-looking run after seeing
      results. Reviewed for local-machine paths/identifiers before committing — none found.
- [ ] Publication venue and timing if the pre-registered honest-negative criterion fires.
- [ ] Willingness to score the blind calibration sample before learning conditions — if not, drop
      the judged metrics rather than half-doing them.
- [x] Should the Treatment D 5-seed batch be committed to the public repo? **Yes, decided
      2026-09-07.** `runs/caseA-condD-s0..4/` and `runs/compare-caseA-with-D/` are un-gitignored
      and committed, matching the Case A demo run's own precedent. Reviewed for local-machine
      paths/identifiers before committing — none found.
- [x] Should the P1 perturbation batch be committed to the public repo? **Yes, decided
      2026-09-07**, after an independent external review (`codex exec -p review`) caught and this
      session corrected two real reporting issues first (see docs/decisions.md) — overstated
      "fully computed" language, and two undisclosed P0-05 findings. `runs/caseA-cond{A,C}-s0-
      {framing_flip,sponsor_endorsement,anchoring,evidence_reorder}/` and
      `runs/compare-caseA-final/` are un-gitignored and committed. Reviewed for local-machine
      paths/identifiers before committing — none found.

## V1: Decision Instrument (started 2026-09-11)

- [x] **ADR-007 assurance adapter** — `src/kriterion/assurance/adapter.py` (generic
      `AssuranceEvidenceEnvelope` document pair → `EvidenceItem`s, tolerant reader, epistemic
      mapping preserved, hard anti-laundering guards), `kriterion assurance import` CLI, authored
      fixture pair on the Case A pack, 15 adapter tests. Done 2026-09-11 (branch
      `agent/fable/kriterion-decision-instrument`). **Hardened the same day** after an
      adversarial review found four PASS-laundering routes and an uncaught-exception path open:
      `criticalFailures` is now required and typed (an omitted list no longer reads as "none"),
      a gating `fail` under a PASS decision is refused, the decision must be identity-bound to
      the envelope (`capabilityRef`/`envelopeRef`/version), a declared PASS over
      producer-declared-stale evidence reports as STALE, every malformed document shape raises
      `AssuranceImportError` instead of `AttributeError`, duplicate derived ids are refused, and
      `digestsCaptured: false` emits its own explicit UNKNOWN item. 26 adapter tests.
- [x] **Public site leads with the decision journey** — `docs/index.html` rebuilt around the
      coding-agent-rollout case using only committed run artifacts; the V0 research landing page
      preserved at `docs/lab.html` with all caveats intact; README/architecture repositioned
      (instrument first, Lab as the mechanism-evaluation layer). Done 2026-09-11, same branch.
      **Claim-corrected the same day**: a source `fail` was rendering as the invented word
      "PARTIAL", coverage gaps were credited as decision reasons the decision document does not
      contain, an authored fixture was described as an independent measurement, and the page
      called itself "produced end-to-end by the real pipeline". All corrected, and
      `tests/product/test_public_page_coherence.py` now binds every displayed outcome, figure
      and position to its source artifact.
- [x] **Persist evidence requests per run** — `evidence_requests.json` is now written for
      conditions A/B/C/D (empty file when nobody asked, so "no requests" stays distinguishable
      from "run predates the artifact"). Done 2026-09-11.
- [x] **Ledger ingestion path for imported assurance items** — `kriterion assurance import
      --into-case CASE_DIR` freezes imported items with the case pack's own evidence into a new
      fingerprinted ledger version via `freeze()`, and refuses to overwrite an existing frozen
      ledger. Verified end-to-end: import → ledger v2 → `econ` → `report`, with all 12 assurance
      items rendered. Committed V0 demo ledgers untouched. Done 2026-09-11.
- [x] **Render the per-seat evidence requests** — done 2026-09-12 (V1.1). Each seat's card on
      the generated decision page shows what it asked for and its own `would_change`, from
      the stored artifact. `report/html.py` was deliberately NOT changed, so the committed V0
      run reports stay byte-identical frozen research artifacts; the new view lives in the
      decision-page renderer instead. Superseded detail below:
- [x] ~~Render the per-seat evidence requests (original entry)~~ — the artifact now exists but nothing displays
      it. Add an `EvidenceRequest` view to `report/html.py` (deferred once already because a new
      report section changes every committed `report.html`, which are frozen research artifacts
      — do this together with a deliberate regeneration pass), and re-run Case A so the journey
      page can show stored per-seat records instead of derived copy.
- [x] **Generate the public journey page from the pipeline** — done 2026-09-12 (V1.1),
      ADR-011. `kriterion decision-page` renders `docs/index.html` from a `DecisionState`
      projection, with the ADR-012 narrative-integrity check as a publish gate. A test
      asserts the committed page is byte-identical to a fresh render. Superseded detail:
- [x] ~~Generate the public journey page (original entry)~~ — `docs/index.html` is
      hand-maintained. The coherence test is a mechanical stand-in, not a substitute: it catches
      drift from the artifacts, not a missing section or a stale narrative. A small renderer
      reading `runs/caseA-condC-s0/` + `cases/coding-agent-rollout/assurance/` would retire both
      the hand-maintenance and the test.
- [ ] **Import a real producer artifact** — Kriterion has only ever consumed the hand-authored
      JSON facsimile in `cases/coding-agent-rollout/assurance/`. Converting Hekton Assurance's
      real committed `2026-09-07T19-31-41Z` FAIL pair (YAML → JSON, losslessly) and importing it
      is the only thing that proves the contract is real rather than self-consistent. Blocks the
      Assurance-side ADR's "first external consumer" language from being strengthened.
- [ ] **Promote structural economic assumptions** — the 10% discount rate, the full-period
      headcount treatment (1,200 then 5,000, no mid-year ramp) and the stage amounts are named
      constants in `case_flows.py`, excluded from the tornado. The journey page now states this
      explicitly; modelling them as ranged `Assumption` records is the real fix. Note it will
      change `economics.json` output, so it needs a deliberate regeneration pass rather than a
      quiet edit of committed run artifacts.
- [ ] **Human decision + outcome contract demo beat** — needs the accountable human: record a real
      `kriterion decide` (e.g. modify DEFER → DISCOVERY at £50k) and its outcome contract on a
      fresh run, then render section 7 of the journey page from it. Not fabricatable by an agent
      (RISK-0011).
- [ ] **Decision retrospective (expected vs observed)** — domain model carries `OutcomeContract`
      measures/review date; the retrospective comparison object and view remain future work
      (deliberately out of this increment's scope).

## V1.1: Executable Decision Story (2026-09-12)

**Purpose:** ensure the human-facing decision narrative is a faithful projection of the
underlying evidence, economics and decision state. See
`docs/planning/kriterion-v1.1-narrative-integrity/opus-plan-and-report.md`.

- [x] **One decision state, everything else a view** — `src/kriterion/decision_state.py`
      (ADR-011). No second data model; derived values computed once so no template can invent
      one. Absence stays absence: three genuinely different evidence-request states, four
      outcome-contract states, and a refusal rather than an empty render when the ledger
      declares no items.
- [x] **Narrative integrity as an invariant** — `src/kriterion/narrative.py` (ADR-012).
      Binding plus re-derivation, unbound-prose rules, structural attribution rules, and
      `kriterion decision-page` refusing to publish on any violation. 45 regression tests.
- [x] **Generated public decision page** — `src/kriterion/report/decision_page.py`,
      `scripts/build-decision-page.sh`, rendering `runs/caseA-condC-s5`.
- [x] **Controlled refusal on malformed run artifacts** — found by adversarial probing, not
      review: 16 of 16 malformed artifacts escaped as bare tracebacks. All now refuse cleanly
      with the artifact and field named. This is the same defect shape ADR-009 closed in the
      assurance adapter, reproduced in new code.
- [x] **Human lifecycle verified end to end** — `tests/product/test_human_decision_lifecycle.py`
      drives `decide` -> `contract` -> `validate-run` -> `decision-page` over a throwaway copy of
      the canonical run. Found and fixed a real ambiguity: with a synthetic DEFER and a human
      PILOT both recorded, one "capital at risk" figure read as the decision's exposure while
      describing only the machine's suggestion.

### Deferred from V1.1, deliberately

- [ ] **A real human decision on the canonical case.** Still the single most valuable next act,
      still not fabricatable by an agent (RISK-0011). The path is verified and the page states
      the absence honestly; what is missing is the human.
- [ ] **Link evidence requirements to the funding stage they unlock.** Kriterion records what
      each stage costs and what each seat wants, but nothing records which requirement unlocks
      which stage. The page says so rather than inferring a mapping. Needs a real case-pack
      schema for the ladder (still a `case.toml` comment plus constants in `case_flows.py`).
- [ ] **Promote the structural economic assumptions** (discount rate, full-period headcount
      treatment, stage amounts) into ranged `Assumption` records. Unchanged from V1: the page
      now states the ranking's scope explicitly, but modelling them changes `economics.json` and
      needs a deliberate regeneration pass.
- [ ] **Value-of-information.** The chain `Assumption -> range -> sensitivity -> evidence quality
      -> EvidenceRequest` is now fully visible on one page, which is the precondition. Building
      the engine was explicitly out of scope.
- [ ] **Judge whether a derived sentence is *fair*.** The checker proves a statement is computed
      from the record and cannot be hand-edited; it cannot prove the English is a fair summary.
      Named as a limit of the approach, not a bug to fix later.
- [ ] **Case B, additional treatments, retrospective analytics, portfolio views, more committee
      agents, provider expansion, hard cross-repo artifact pinning** — all untouched, as scoped.
