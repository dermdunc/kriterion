# Experiment Plan: Kriterion V0

Written before any comparison batch runs, per docs/v0-plan.md Section 6's own requirement
("Written into `docs/experiment-plan.md` **before the first batch runs**"). `kriterion compare`
(task 14) reads this document's thresholds; it does not invent them at comparison time.

## Pre-registered honest-negative criterion (headline comparison)

> If condition C does not beat **both** A and B on **≥2 of** {unsupported-claim rate, seeded-trap
> detection, perturbation robustness} by a margin exceeding **2× the observed seed-to-seed standard
> deviation** on that metric, while costing more than 2× A's inference, the finding is written up
> as *"structured multi-agent deliberation did not justify its complexity on these cases."*

This is a **successful** V0 outcome if it fires. The project is an experiment, not a launch
(docs/v0-plan.md Section 6).

## Local LLM quality kill criterion — numeric threshold (fixes a real gap)

`.hekton/intents/INT-2026-09-05-002`'s disproof_criteria #4 requires a threshold "set before the
run, not judged after seeing output." docs/v0-plan.md Section 14's kill criterion 4 only stated
this qualitatively ("schema failures or indistinguishable role outputs across the board") — flagged
as an open gap in this project's own `docs/next-actions.md` since task 7. Fixed here, before any
comparison batch runs:

**Kill criterion 4 fires if, across the full 5-seed batch on either case:**
- the `abstained_error` rate (phase 3 + phase 7 combined) across all 5 committee members exceeds
  **20%** of all independent-assessment/revision calls, OR
- role-diversity (unique evidence items cited per role, pairwise rationale n-gram overlap — Section
  6's own metric) shows **no measurable difference** between any two of the five charters across
  all 5 seeds (i.e. the five roles are statistically indistinguishable, not just similar on one run).

Either condition, independently, is sufficient to fire kill criterion 4. Both are computable from
`run-export.json` outputs already produced by `kriterion evals` (task 13) plus a role-diversity
scorer this plan does not yet require the harness to compute standalone — see "Known gaps" below.

## Run design

**Grid:** 2 cases (`coding-agent-rollout`, `invisible-ai-control-plane`) × 3 conditions (A, B, C) ×
5 seeds = **30 base runs**, plus paired perturbation runs for the four P1 hygiene evals (framing
flip, sponsor endorsement, evidence reorder, anchoring) on Case A under conditions A and C only = 16
further runs. ~46 model-phase runs at 14B scale total (docs/v0-plan.md Section 6).

**Controls:** identical frozen case/ledger/economics fingerprints across conditions within a case;
identical decision vocabulary and JSON schemas (already structurally guaranteed —
`parse_position_response`/`parse_revision_response` reject anything else); identical seeds per
matched run across conditions; temperature 0 (already enforced by every executor call); token
budget recorded and reported per condition.

## Metrics (deterministic, headline — may support a superiority claim)

Computed by `kriterion compare` from `run-export.json` + run artifacts across the seed batch:

- unsupported-claim rate (uncited material claims / material claims) — from P0-05-style scanning
  across all `key_reasons`
- citation-resolution rate — structurally 100% by construction (`parse_position_response` rejects
  any response citing an unknown id before it is ever recorded), reported as a sanity check, not a
  discriminating metric between conditions
- category-inflation count — P0-05's own scorer, summed across the batch
- computed-number-alteration count — P0-03's own scorer, summed across the batch
- belief-update rationality — fraction of `evidence_driven`/`argument_driven` updates with
  non-empty `trigger_refs`, vs `unexplained`
- dissent presence and non-triviality — `strongest_dissent.verbatim` non-empty (structurally
  guaranteed for A and C by `SyntheticRecommendation.__post_init__`) and citing >=1 real evidence id
- tokens, latency, wall-clock per case per condition — **known gap, see below**

## Judge-scored (secondary, never a gate) and human-calibrated

Unchanged from docs/v0-plan.md Section 6: judge is `qwen2.5:14b-instruct`, PROVISIONAL (88%
agreement, 50 examples), also the generator in A/B/C — a documented limitation, not solved locally.
Blind human calibration (>=12 outputs, condition markers stripped, scored before learning which
condition produced each) is the real anchor. **Open question for the project owner, carried from the
original planning-loop fork's own report:** whether they are willing to do this scoring before
seeing conditions. Without it, judged metrics should be dropped from any published claim entirely,
per that report's own recommendation — not half-trusted.

## Known gaps carried into task 14/15, not silently absorbed

- **Token/latency capture is incomplete.** `BaselineACallRecord` (task 8) drops
  `ExecutorResult.elapsed_seconds` when logging each call; phase 3/5/7's `AssessmentOutcome`/
  `RevisionOutcome`/`ChallengeRoundResult` do not record it at all. `kriterion compare`
  (this task) reports wall-clock **at the process level** (start/end time around each `kriterion
  run` invocation) as a substitute — real per-call token/latency instrumentation is a follow-up,
  not built retroactively into already-shipped protocol code as part of this task.
- **Role-diversity metric (unique evidence cited per role, pairwise rationale n-gram overlap) is
  not yet a standalone scorer.** `kriterion compare` computes a simplified proxy (unique
  `evidence_refs` per seat across the batch) sufficient for kill-criterion-4's own threshold above;
  a fuller n-gram-overlap version is deferred to whoever runs the real batch and finds the proxy
  insufficient.
- **The actual 30+16-run batch has not been executed in this build session.** Building and
  live-verifying `kriterion compare` against a small number of real runs (already produced this
  session) is this task's own scope; running the full pre-registered grid is a separate,
  multi-hour activity for whoever picks this project up next, not a precondition for the tool
  existing and working correctly.
