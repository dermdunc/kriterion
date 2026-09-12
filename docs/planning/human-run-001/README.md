# Kriterion Human Run 001

Human Run 001 is Kriterion's first **public, fully reproducible** decision experiment.

> Kriterion's first public Human Run asks whether a fictional 2,500-engineer global software
> company should spend millions building an Internal Developer Platform.

Research question:

> Does Kriterion improve a human's technology-investment judgment?

It is **not** asking whether Kriterion picked the right investment. It is asking whether Kriterion
caused an accountable human to reason more explicitly and effectively — about evidence,
assumptions, uncertainty, economics, adoption, attribution, investment sequencing, and what
evidence is required before a larger commitment.

---

## The case

**Northstar Software Group — Internal Developer Platform investment.**

Case id: `northstar-internal-developer-platform`.

> Should Northstar Software Group invest approximately £3m–£5m over the next 18 months in an
> Internal Developer Platform, or pursue a lower-cost programme of incremental improvements to its
> existing engineering toolchain?

The load-bearing tension underneath it:

> Will reducing developer friction create attributable business value, or primarily move complexity
> and cost from application teams into a new platform organisation?

**Northstar Software Group is fictional.** ~2,500 engineers across the United States, Europe and
India, building global digital and software products, running a substantial but fragmented
developer toolchain rather than one coherent platform. Every one of those numbers is a synthetic
scenario input. Northstar is not a real company and is not a pseudonym for one.

The case is deliberately difficult, and difficult in ways that are hard to resolve by analysis:

* platform benefits are hard to attribute;
* the build-versus-buy decision is non-obvious;
* adoption can destroy otherwise attractive economics;
* saved developer time is not automatically business value;
* AI agents may either increase or decrease the strategic value of platform abstractions, and the
  public evidence currently points both ways.

That is a stronger instrument than an artificial "AI committee chooses an investment" demo, because
a reader can disagree with the answer for good reasons.

---

## What is in this directory

| File | Purpose |
|---|---|
| `README.md` | This file. |
| `protocol.md` | The pre-registered design: T0/T1/T2, the three dimensions, reading order, useful outcomes, interpretation rules, five falsification conditions. |
| `case-design.md` | How the case was built, its evidence boundaries, its economics, its challenge-seat gaps, its risks. |
| `decision-impact-log.md` | The blank instrument the participant completes contemporaneously. |
| `freeze-manifest.md` | Identity, content hashes, reproduction commands. Deliberately omits the recommendation, so it is safe to read at T0. |
| `opus-pivot-report.md` | What this preparation produced. **Do not read before T2.** |

The case pack, the frozen run and the generated page live outside this directory:

| Artifact | Location |
|---|---|
| Case pack | `cases/northstar-internal-developer-platform/case.toml` |
| Frozen run artifacts | `runs/hr001-northstar-condC-s1/` |
| Generated decision page | `docs/human-run-001/decision-page.html` |

`protocol.md`, `case-design.md` and the blank `decision-impact-log.md` are committed **before** the
participant records T0. The blank instrument is part of the experimental design; committing it
after the fact would make every result unfalsifiable.

---

## Everything here is public, and that is the point

This case exists because Kriterion needed a first public use case that a reader could check rather
than take on trust. Everything required to reproduce the analysis is committed:

* the case pack, with all 65 evidence items, their epistemic categories, their attestations and
  their cross-references;
* the ranged assumptions the economics spends;
* the frozen evidence ledger and its fingerprint;
* the run artifacts — positions, challenges, belief updates, evidence requests, economics,
  recommendation;
* the generated decision page;
* the freeze manifest, with content hashes and the exact commands.

**What a reader can reproduce exactly:** `kriterion econ`, `kriterion ledger freeze` and
`kriterion decision-page` are deterministic. Re-running them against the committed case pack
reproduces `economics.json`, `ledger.frozen.json` and the page byte-for-byte.

**What a reader cannot reproduce exactly:** `kriterion run` calls a local language model. Re-running
it will produce different positions, challenges and possibly a different recommendation. The hashes
in the freeze manifest are a freeze, not a reproducibility claim about the model.

**What is not committed:** the participant's T0, T1 and T2 responses. Those do not exist yet. They
are committed when the experiment is actually performed, and not before.

---

## Real research, invented company

The case mixes two kinds of claim, and the distinction is rendered on every item of the generated
page rather than explained once in a preamble:

| Attestation badge | Count | Meaning |
|---|---|---|
| `REAL` | 20 | A real, named, public source a reader can go and check — DORA, SPACE, DevEx, Team Topologies, CNCF, InnerSource, NIST, published trials on AI-assisted development. |
| `AUTHORED` | 45 | A synthetic scenario input invented for this experiment. Every Northstar-specific claim. |

Thirteen `AUTHORED` items are categorised `MEASURED`. That is deliberate and it is not a
contradiction: the category describes what kind of claim it is *inside the scenario* — telemetry
rather than opinion — while the attestation says nobody measured anything. `case-design.md`
explains why that is the honest classification, and a test enforces it.

No fictional Northstar number is presented anywhere as an observation of a real organisation.

---

## Starting the run

The order matters, and the stop in the middle of it is the whole experiment:

```text
1.  Read protocol.md, including the reading-order caveat.  Section 1 of the
    generated page states the recommendation, its confidence, the capital at
    risk and the dominant uncertainty at the top.  Those four lines must be
    withheld until step 6.  The product does not do this for you.
2.  Read the case pack.  Record T0: strategy, investment, evidence gate,
    confidence.  Three dimensions, recorded independently.
3.  Read the generated decision page, sections 1-8 only, with the redaction.
4.  Record section-by-section impact as you go.
5.  Record T1, all three dimensions.  Name the specific item that moved you,
    not "the analysis".  STOP before section 9.
6.  Only then read section 9, the synthetic recommendation, revealing the
    four withheld lines at the same time.
7.  Record T2, all three dimensions, BEFORE rereading T0 or T1.  Then the
    anchoring check: name the evidence from sections 1-8 that justified any
    change, or flag possible anchoring.
8.  `kriterion decide` (and `kriterion contract` if it funds anything).
9.  Retrospective, and the five falsification conditions.
```

The case, its run and its page are frozen before step 1. Material evidence that appears during the
run is recorded as post-T0 evidence; the frozen case is never edited mid-experiment.

---

## Participant

One participant, who designed Kriterion and authored the Northstar scenario. That is a serious
limitation and it is recorded as one in `case-design.md`.

The fictional case reduces part of it: the participant has no privileged knowledge of Northstar's
answer, no organisational stake in the outcome, and no remembered internal facts to substitute for
the case's evidence. It does not eliminate it — the participant still chose which facts Northstar
has, and still knows what the T1 checkpoint is testing.

Human Run 001 establishes whether the instrument does anything at all. Generalisability is a later
run's question, with a less project-involved participant.

---

## Relationship to other Kriterion work

A separate private practitioner run is retained for a real-world operating-model decision, where
confidentiality prevents publishing the underlying evidence. Nothing about that decision — the
organisation, the participant, the case content, the position, the recommendation or the evidence —
appears anywhere in this repository, and nothing in Human Run 001 depends on it.

The canonical public Kriterion site stays on the `coding-agent-rollout` fixture. Human Run 001 has
its own page at `docs/human-run-001/decision-page.html`, and whether it becomes the site's front
page is a separate decision that has not been made.
