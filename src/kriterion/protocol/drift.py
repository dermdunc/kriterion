"""Deterministic BeliefUpdate.drift_flags derivation (docs/v0-plan.md
Section 5): "drift_flags: harness-written, never model-written". A real gap
found live in the 2026-09-06 pre-registered batch -- BeliefUpdate has
carried this field since early in the build, but nothing ever computed it,
leaving every real belief update with drift_flags=[] regardless of what
actually happened. Pure function, no model call, computed once at phase 7
right after parsing the model's own response.

A "meaningful update" (Section 5) = position or confidence changed AND
trigger_refs resolve to items that did not exist at phase 3 (phase-6
injected evidence), or to a challenge artifact (a `ch:`-prefixed id).
Everything below is judged against that one definition.
"""

from __future__ import annotations

from kriterion.domain.committee import BeliefUpdate, Challenge
from kriterion.domain.enums import ConfidenceBand, DriftFlag

_CONFIDENCE_RANK = {ConfidenceBand.LOW: 0, ConfidenceBand.MEDIUM: 1, ConfidenceBand.HIGH: 2}

# "High n-gram overlap" is not further quantified anywhere in the plan --
# a judgment call, stated rather than left implicit: word-trigram Jaccard
# similarity, threshold chosen to catch near-verbatim restatement without
# firing on two people independently making the same short, common point.
ECHO_NGRAM_SIZE = 3
ECHO_OVERLAP_THRESHOLD = 0.3


def _word_ngrams(text: str, n: int) -> set[tuple[str, ...]]:
    words = text.lower().split()
    if len(words) < n:
        return set()
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def _ngram_overlap(a: str, b: str) -> float:
    ngrams_a = _word_ngrams(a, ECHO_NGRAM_SIZE)
    ngrams_b = _word_ngrams(b, ECHO_NGRAM_SIZE)
    if not ngrams_a or not ngrams_b:
        return 0.0
    return len(ngrams_a & ngrams_b) / len(ngrams_a | ngrams_b)


def derive_drift_flags(
    belief_update: BeliefUpdate,
    *,
    new_since_phase3_ids: set[str],
    challenges: list[Challenge],
) -> list[DriftFlag]:
    changed = (
        belief_update.revised_position != belief_update.initial_position
        or belief_update.revised_confidence != belief_update.initial_confidence
    )
    if not changed:
        return []  # no_change (or a no-op restatement) carries no drift risk to flag

    flags: list[DriftFlag] = []
    challenge_ids = {c.id for c in challenges}
    cites_new_evidence = any(ref in new_since_phase3_ids for ref in belief_update.trigger_refs)
    cites_challenge = any(ref in challenge_ids for ref in belief_update.trigger_refs)

    if not belief_update.trigger_refs:
        flags.append(DriftFlag.UNEXPLAINED)
    elif not cites_new_evidence and not cites_challenge:
        # Every cited ref is an evidence id that was already available at
        # phase 3 -- not a fabrication, but not a "meaningful" trigger
        # either per Section 5's own definition.
        flags.append(DriftFlag.RETROFIT)

    confidence_distance = abs(
        _CONFIDENCE_RANK[belief_update.revised_confidence] - _CONFIDENCE_RANK[belief_update.initial_confidence]
    )
    if confidence_distance >= 2:
        flags.append(DriftFlag.CONFIDENCE_JUMP)

    if not cites_new_evidence:
        others_challenges = [c for c in challenges if c.author_role != belief_update.member]
        if any(_ngram_overlap(belief_update.stated_reason, c.content) >= ECHO_OVERLAP_THRESHOLD for c in others_challenges):
            flags.append(DriftFlag.ECHO)

    return flags
