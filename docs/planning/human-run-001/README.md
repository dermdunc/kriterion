# Kriterion Human Run 001

Human Run 001 is Kriterion's first **real** decision experiment. Every prior Kriterion run
deliberated an authored fixture. This one instruments a real, unresolved, consequential decision
held by a real accountable human.

Research question:

> Does Kriterion improve the quality of an accountable human decision about how to organise and
> invest in global platform engineering across a distributed enterprise?

It is **not** asking whether Kriterion picked the right operating model. It is asking whether
Kriterion caused the accountable human to reason more explicitly and effectively — about evidence,
assumptions, uncertainty, economics, organisational trade-offs, decision rights, investment
sequencing, and what evidence is required before a larger commitment.

That question cannot be answered by another synthetic engineering loop, which is why this
directory contains an experiment, not a feature.

---

## What is in this directory

| File | Purpose |
|---|---|
| `README.md` | This file: what the experiment is, where its parts live, and how to start it. |
| `protocol.md` | The pre-registered design: T0/T1/T2, the three dimensions, useful outcomes, interpretation rules, five falsification conditions. |
| `case-design.md` | Why this decision, the three dimensions it spans, evidence boundaries, economic limits, experiment risks. |
| `decision-impact-log.md` | The blank instrument the participant completes contemporaneously. |
| `opus-preparation-report.md` | What preparation actually produced, and the product-fit verdict. |

All four of the first files were committed **before** the participant saw any Kriterion analysis
of this case. The blank instrument is part of the experimental design; committing it after the
fact would make every result unfalsifiable.

A narrower first preparation of this case was built, frozen and committed before a materially fuller
final specification arrived. It was rebuilt, and the superseded frozen artifacts were **archived
intact rather than overwritten** — no participant response had been recorded against them, and every
hash was re-verified after the move. `case-design.md` records what changed and why the case id
changed with it. Nothing in this directory is revised after T0.

---

## Public / private split

This repository is public. The decision is a real organisation's real operating-model question.
Those two facts settle the split, and it is not negotiable:

**Public (this directory).** Methodology and protocol only. The decision *topic* is named here,
because the participant has already published their own research on that topic publicly under
their own identity. Nothing here is case-specific evidence content, and nothing here could be
mistaken for a particular organisation's internal specifics.

**Private (`kriterion-private/human-run-001/`, deliberately not a git repository).** The case pack
itself, the decision-rights matrix and the distribution artifact with actual entries, the economics,
the frozen run artifacts, the generated decision page, the archived superseded preparation, and
every completed participant response. None of it is committed anywhere, in this repository or any
other.

The consequence worth stating plainly: **the canonical public Kriterion site stays on the
`coding-agent-rollout` fixture.** Human Run 001 is an experiment, not a public case study, and
publishing its output is a separate decision that has not been made.

---

## Why the case pack is not in `cases/`

Kriterion's CLI takes arbitrary paths for the case directory, the runs directory and every output
(`kriterion run <case_dir> --runs-dir <dir>`, `kriterion decision-page <run_id> <case_dir>
--runs-dir <dir> --out <path>`). So a case can live outside this repository and still run through
the full pipeline unchanged. `cases/` holds the two public fixtures; Human Run 001's pack holds a
real decision and lives privately. No product change was needed to make that work.

One consequence is visible in this repository: `kriterion.economics.CASE_ECONOMICS_FUNCTIONS` and
`kriterion.decision_state._build_param_maps` register the Human Run 001 case id, so the case id
appears in public source even though its content does not. That is intentional and is the only
public trace of the case. It is also why renaming the case meant a source change: the rename is
mechanical, bounded to those two entries plus the test module that pins them, and was carried
through consistently.

---

## Starting the run

The order matters, and the stop in the middle of it is the whole experiment:

```text
1.  Read protocol.md.  Do not open the generated decision page first.
2.  Record T0: operating model, distribution, decision rights, investment,
    confidence.  Three dimensions, recorded independently, across the public
    instrument and the two private blank artifacts.
3.  Read the generated decision page, sections 1-7 only.
4.  Record section-by-section impact as you go.
5.  Record T1, all three dimensions.  Name the specific item that moved you,
    not "the analysis".  STOP before section 8.
6.  Only then read section 8, the synthetic recommendation.
7.  Record T2, all three dimensions, BEFORE rereading T0 or T1.  Then the
    anchoring check: name the evidence from sections 1-7 that justified any
    change, or flag possible anchoring.
8.  `kriterion decide` (and `kriterion contract` if it funds anything).
9.  Retrospective, and the five falsification conditions.
```

The case, its run and its page are frozen before step 1. The freeze manifest lives privately,
alongside the case pack. Material evidence that appears during the run is recorded as **post-T0
evidence**; the frozen case is never edited mid-experiment.

---

## Participant

One participant, who is the author of the external research this case draws on and the designer of
Kriterion itself. That is a serious limitation, it is recorded as one in `case-design.md`, and it
is not something this run attempts to eliminate. Human Run 001 establishes whether the instrument
does anything at all on a real decision. Generalisability is a later run's question, with a less
project-involved participant.
