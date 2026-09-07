# Intent-Driven Development in Kriterion — Operating Definition

**Status:** operative from 2026-09-05 (`INT-2026-09-05-001`, this practice's own founding
intent). Adopted `tektograph-1.0`, on the explicit instruction of the project owner
(coderturtle), given during this same session via an `AskUserQuestion` choice among four
options after being told plainly that this decision was factory-governance-level and
unresolved elsewhere.

**Kriterion is the first `factory-output` repo to adopt this practice.** Every prior
adopter (`tektograph`, `regulated-architecture-lab`, `hekton-assurance-lab`,
`hekton-loops-lab`, `hekton-cli-lab`, `egress-broker-lab`) is a `lab` or a standalone
downstream product. There is no factory-output precedent for schema, gate wiring, or
whether a factory-output project should even carry `.hekton/intents/` at all — this
document is that precedent being set, not one being followed.

## Why tektograph-1.0, and why this does not settle the org-wide question

There is a real, unmerged, unadopted proposal in `~/hekton`
(`docs/proposals/intent-schema-consolidation.md`, branch
`agent/claude/intent-schema-consolidation-proposal`) that explicitly reserves this exact
schema choice — and whether one repo may decide it unilaterally — for the project owner,
and deliberately does not pick a winner among its four options (A: standardize
`tektograph-1.0`, B: standardize the nested `1.0` shape as "1.1", C: a decision tree
supporting both, D: a new schema). **This document does not resolve that proposal.** It
records a pragmatic, scoped choice for Kriterion only, made with the fragmentation and
the pending proposal disclosed to the owner before the choice was made.

Counted directly on this machine on 2026-09-05, before choosing:

| Registry | Schema | Live intent count |
|---|---|---|
| `tektograph` | `tektograph-1.0` | 20 |
| `regulated-architecture-lab` | `tektograph-1.0` | 2 |
| `hekton-assurance-lab` | `tektograph-1.0` | 2 |
| `hekton-loops-lab` | `1.0` (nested) | 6 |
| `hekton-cli-lab` | `1.0` (nested) | 1 |
| `egress-broker-lab` | `1.0` (nested) | 1 |
| `intent-assurance-lab` | `1.0` (nested), design-only, parked since 2026-07-11 | 1 |

Both schemas are live, real practice — not one abandoned and one current. The basis for
choosing `tektograph-1.0` for Kriterion specifically: it has a working, ported validator
(`scripts/validate_intents.py`, copied verbatim from `hekton-assurance-lab`, itself ported
from `regulated-architecture-lab`, itself ported from `tektograph` — diff-checked
byte-identical at each hop) and an explicit `history` block giving an append-only audit
trail, which the nested `1.0` shape does not have. No factory-output-specific reason
favored either schema; this was a "pick the one with working tooling" call, made
explicitly, not a claim that `tektograph-1.0` is factory-output's correct answer.

## The registry

**Location:** `.hekton/intents/<intent-id>/intent.yaml`. One directory per intent;
amendments live beside the intent file, never overwrite it. The directory listing is the
index — no separate index file.

**Id format:** `INT-YYYY-MM-DD-NNN`, date = declaration date, NNN = same-day sequence.
Assigned at declaration, never pre-allocated.

**Format**, `tektograph-1.0`:

```yaml
schema_version: "tektograph-1.0"
intent_id: "INT-2026-09-05-NNN"
title: "..."
kind: feature | fix | refactor | experiment | ops | security | decision
status: declared                         # the full 10-status vocabulary
risk_tier: T0 | T1 | T2 | T3
iteration: 0                             # kriterion has no formal iteration concept yet
review_by: YYYY-MM-DD                    # an intent may not float indefinitely unfalsified
owner:
  accountable_human: coderturtle
  responsible_agent: "<agent/branch>"
hypothesis: >                            # one falsifiable claim, plain language
confirmation_criteria:
  - "..."
disproof_criteria:                       # mandatory, never empty, genuinely falsifiable
  - "..."
bindings:
  mission_manifests: []
  adrs: []                               # decisions recorded in docs/decisions.md instead;
                                          # cite by date/row in confirmation evidence
  risks: []                              # RISK-nnnn ids from .hekton/risk-register.yaml
  prs: []                                # PR numbers once they exist
history:
  - {status: declared, date: ..., by: ..., evidence: "..."}
```

`disproof_criteria` is mandatory. An intent whose author cannot state what would disprove
it is not accepted.

## Lifecycle: states, transitions, and who moves them

Adopted verbatim from `tektograph` (via `hekton-assurance-lab`): `declared → critiqued →
accepted → in_progress → technically_confirmed → provisionally_confirmed →
operationally_confirmed`, with side-exits to `disproven`, `superseded`, `abandoned` at any
point after `accepted`.

| Transition | Moved by | Evidence required |
|---|---|---|
| → `declared` | a session (agent drafts, human sees it) | the intent file itself, with non-empty disproof criteria |
| `declared → critiqued` | an adversarial pass: `doubt-driven-development`, an independent review, or the user's own pushback | the critique's findings recorded in `history` (or a note that critique found nothing — also evidence, only if it names what it tried to break) |
| `critiqued → accepted` | **the user, explicitly** — never an agent | user approval recorded in `history`; for T2/T3 this is a named per-intent approval, not bundled with any other sign-off |
| `accepted → in_progress` | the session that picks it up | the kickoff commit |
| `in_progress → technically_confirmed` | session closure | the closure summary + this project's own review with no blocking findings (reuse `.hekton/review-log.yaml`'s `REV-XXXX` mechanism — do not build a parallel gate) |
| `technically_confirmed → provisionally_confirmed` | PR merge (user-approved, per-event) | the merge itself; PR number added to `bindings.prs` |
| `provisionally_confirmed → operationally_confirmed` | a later, real observation | real dogfooding evidence, an end-session report reflecting the change, or a Gremlin run — cited concretely |
| any (post-accepted) → `disproven` | whoever holds the disproving evidence — agent or human; an agent may propose, the record is made immediately, the user is told in the same session | the disproving evidence, cited concretely |
| any (post-accepted) → `superseded` / `abandoned` | the user (T2/T3) or the session with user visibility (T0/T1) | the successor intent id (superseded) or the recorded reason (abandoned) |

Amendments: clarifications and narrowing that change no risk tier, constraint, or
confirmation criterion are recorded directly in `history`; anything material gets an
amendment file beside the intent and, for T2/T3, explicit user approval before work
continues. The original hypothesis text is never edited — only appended to.

**This amendment protocol governs `accepted`-and-later intents only.** Pre-acceptance,
the `declared → critiqued` step's whole purpose is to fix real defects — including in the
hypothesis and criteria text itself — directly in the file. An intent's `declared` history
entry is likewise never rewritten once written, even if its evidence text turns out to be
imprecise — a later entry states the correction and the resulting inconsistency
explicitly, rather than editing the earlier entry to hide that a correction was needed.

## Binding to existing machinery

1. **Risk register.** `bindings.risks` cites `RISK-nnnn` ids from
   `.hekton/risk-register.yaml` when an intent addresses or is constrained by an open risk.
2. **Governance gate.** `.hekton/governance.yaml`'s `required_gates.intent_recorded: true`
   was already true at scaffold time, before this doc existed — this practice is what makes
   that gate mean something concrete rather than an unenforced placeholder.
3. **Review log.** An intent reaching `in_progress` must go through the normal `REV-XXXX`
   review (`.hekton/review-log.yaml`) before `technically_confirmed` — the intent lifecycle
   does not replace or bypass that gate.
4. **Decisions log.** `docs/decisions.md` remains the durable, human-readable record of
   *why*; an intent's `history` records *when it moved and on what evidence*. Both are kept.
5. **Validation.** `scripts/validate_intents.py` (ported verbatim, unmodified, from
   `hekton-assurance-lab`) checks registry mechanics: required fields present,
   `disproof_criteria` non-empty, legal `history` transitions, terminal-status intents cite
   evidence. Advisory posture: reports and exits non-zero on registry-mechanics violations
   only; not wired into `scripts/verify-project.sh` (must stay runnable with no pip
   dependency).
6. **Commit footers.** Every commit already carries the `Agent:` footer via the installed
   `commit-msg` hook (`.rules/git-contract.md`); the registry file's `history` block is the
   authoritative intent-lifecycle record, independent of that.

## Choreography

The `declared → critiqued → accepted` front half has a named, user-level skill,
`~/.claude/skills/intent-choreography`, which scaffolds the file, composes with
`doubt-driven-development` for the critique step, and drafts the acceptance prompt — it
stops at `accepted`; everything after still moves by real evidence, never by the skill.
Non-interactive contexts (CI, `/loop`, scheduled runs) must stop at `critiqued` and say so,
since acceptance requires a live human answer.

## Critique discipline

Two rules, adopted from tektograph's own hard-won incidents:

**Refute-first, not agree-first.** A critic's job is to try to refute a claim, not confirm
it — promotion follows *failure to refute*, not agreement. A critique pass that reports
"looks good, no issues" without naming what it specifically tried to break should be
treated as incomplete, not a clean pass.

**External citations raise questions; they do not outrank this repository's own accepted
facts.** A claim about factory-wide state (schema counts, tool status, another project's
posture) must be independently re-verified at grounding and critique time, not carried
forward from a prior document's text.

## Disproven and abandoned, recorded without shame

A `disproven` intent keeps its full record forever — never renamed, deleted, or quietly
edited into a weaker claim it could pass. The final history entry cites the disproving
evidence and states what was learned. An `abandoned` intent records *why the question
stopped being worth asking* — the one-line reason is mandatory.

## What this deliberately does not build

No intent database, no dashboard, no automation that moves statuses without a
human-visible trace, no retro-registration of sessions before 2026-09-05.
