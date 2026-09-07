"""Phase 8: synthesis (docs/v0-plan.md Section 5).

"The chair is deterministic and procedural. It is a state machine, not a
persona... It makes exactly one model call: a bounded narrative paragraph
over already-structured inputs, template-hashed. Every decision-bearing
field... is computed deterministically from member positions. The
narrative is excluded from every metric, and Baseline A receives an
identical narrative treatment, so it cannot act as an uncontrolled variable
between conditions."

The narrative is NOT a Section-4 SyntheticRecommendation field (that table
has no such field) — it is returned alongside the recommendation, kept out
of every decision-bearing field, exactly as the plan requires.
"""

from __future__ import annotations

from dataclasses import dataclass

from kriterion.domain.case import DecisionCase
from kriterion.domain.committee import Challenge, CommitteePosition
from kriterion.domain.decision import Dissent, SyntheticRecommendation
from kriterion.executors.base import Executor
from kriterion.protocol.aggregate import CONSERVATISM_RANK, aggregate_baseline_b

NARRATIVE_PROMPT_TEMPLATE = (
    "You are the committee chair. Write a single bounded narrative paragraph (3-5 sentences) "
    "summarising this outcome for an executive reader. Do not introduce any new decision, "
    "number, or fact not already given below — this narrative is excluded from every "
    "measured metric; it is presentation only.\n\n"
    "Decision requested: {decision_requested}\n"
    "Final action: {action}\n"
    "Confidence: {confidence}\n"
    "Conditions: {conditions}\n"
    "Strongest dissent: {dissent}"
)


@dataclass(kw_only=True)
class ChairResult:
    recommendation: SyntheticRecommendation
    narrative: str


def synthesize(
    executor: Executor,
    case: DecisionCase,
    revised_positions: list[CommitteePosition],
    case_against_challenge: Challenge,
    *,
    seed: int,
    created_at: str,
    run_id: str,
) -> ChairResult:
    """Deterministic aggregation identical in spirit to Baseline B's, over
    the REVISED positions this time, plus the one bounded narrative call.
    """
    agg = aggregate_baseline_b(revised_positions)

    if agg.minority_positions:
        # Real dissent exists: pick whichever minority position is furthest
        # (by conservatism rank) from the modal action — the most
        # substantively different view, not just the first one found.
        modal_rank = CONSERVATISM_RANK[agg.modal_action]
        strongest = max(agg.minority_positions, key=lambda p: abs(CONSERVATISM_RANK[p.recommendation] - modal_rank))
        reasons = "; ".join(r.text for r in strongest.key_reasons) or "(no stated reasons)"
        dissent = Dissent(
            verbatim=f"{strongest.member.value}: {strongest.recommendation.value} — {reasons}",
            refs=[ref for r in strongest.key_reasons for ref in r.evidence_refs],
        )
    else:
        # Unanimity: the dissent slot must still be non-empty
        # (docs/v0-plan.md Section 4) — falls back to phase 5's own
        # case-against challenge, the forced-inversion counter-argument
        # that exists precisely for this case.
        dissent = Dissent(verbatim=case_against_challenge.content, refs=case_against_challenge.evidence_refs)

    modal_supporters = [p for p in revised_positions if p.recommendation == agg.modal_action]
    # Conservative choice: report the lowest confidence among modal
    # supporters rather than the highest, so the synthesis never overstates
    # agreement strength.
    confidence_band = min(modal_supporters, key=lambda p: p.confidence_band.value).confidence_band

    recommendation = SyntheticRecommendation(
        id=f"{run_id}-synthesis-recommendation",
        created_at=created_at,
        action=agg.modal_action,
        amount=case.ask.amount_gbp,
        duration=case.ask.duration,
        conditions=list(agg.unioned_blocking_unknowns),
        stop_conditions=[],
        strongest_dissent=dissent,
        unresolved_unknowns=list(agg.unioned_blocking_unknowns),
        confidence_band=confidence_band,
    )

    narrative_prompt = NARRATIVE_PROMPT_TEMPLATE.format(
        decision_requested=case.decision_requested,
        action=recommendation.action.value,
        confidence=recommendation.confidence_band.value,
        conditions="; ".join(recommendation.conditions) or "none",
        dissent=dissent.verbatim,
    )
    narrative_result = executor.complete(narrative_prompt, fmt=None, seed=seed)

    return ChairResult(recommendation=recommendation, narrative=narrative_result.text)
