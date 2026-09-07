"""Phase 5: structured challenge (docs/v0-plan.md Section 5).

"The challenger is not a sixth persona. Strongest case against is assigned
to the member whose initial position was most favourable, and strongest
case for to the least favourable... Premortem is answered independently by
all five."

Visibility: anonymised positions only — no tally, no authorship, no counts
(kriterion.protocol.anonymize enforces this). Executor calls are stateless
(the task-8 lesson) — every prompt here re-includes full case/ledger/
economics context itself, never relies on carryover.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from kriterion.domain.case import DecisionCase
from kriterion.domain.committee import Challenge, CommitteePosition, RoleCharter
from kriterion.domain.economics import EconomicsResult
from kriterion.domain.enums import ChallengeType, CommitteeSeat
from kriterion.domain.evidence import EvidenceItem
from kriterion.executors.base import Executor
from kriterion.protocol.aggregate import CONSERVATISM_RANK
from kriterion.protocol.anonymize import anonymize_positions
from kriterion.protocol.citations import extract_known_evidence_refs
from kriterion.protocol.prompts import format_case, format_economics, format_evidence


@dataclass(kw_only=True)
class ChallengeRoundResult:
    case_for: Challenge
    case_against: Challenge
    premortems: list[Challenge]


def most_and_least_favourable(
    positions: list[CommitteePosition],
) -> tuple[CommitteePosition, CommitteePosition]:
    """(most_favourable, least_favourable) by conservatism rank — most
    favourable is closest to SCALE, least favourable is closest to STOP."""
    ranked = sorted(positions, key=lambda p: CONSERVATISM_RANK[p.recommendation])
    return ranked[-1], ranked[0]


def _shared_context(case: DecisionCase, ledger_items: list[EvidenceItem], economics: EconomicsResult, anonymized_text: str) -> str:
    return (
        f"{format_case(case)}\n\nEvidence:\n{format_evidence(ledger_items)}\n\n"
        f"{format_economics(economics)}\n\n"
        f"Other committee members' anonymised initial positions (no names, no tally):\n"
        f"{anonymized_text}\n\n"
        "If you cite evidence, use only the real ids listed above — never invent one."
    )


def run_phase5_challenge(
    executor: Executor | None,
    case: DecisionCase,
    ledger_items: list[EvidenceItem],
    economics: EconomicsResult,
    initial_positions: list[CommitteePosition],
    charters_by_seat: dict[CommitteeSeat, RoleCharter],
    *,
    seed: int,
    created_at: str,
    run_id: str,
    executor_by_seat: dict[CommitteeSeat, Executor] | None = None,
) -> ChallengeRoundResult:
    """`executor` is the single shared executor used for every call
    (Conditions B/C: one model for all five seats). Treatment D instead
    passes `executor_by_seat` (a different model per role) -- when given,
    `executor` is ignored entirely and each call uses whichever seat is
    actually speaking (the case_for/case_against author under perspective
    inversion, or the premortem's own member), so "independent contexts"
    means independent MODELS too, not just independent conversation state.
    """

    def _executor_for(seat: CommitteeSeat) -> Executor:
        if executor_by_seat is not None:
            return executor_by_seat[seat]
        assert executor is not None, "either executor or executor_by_seat must be given"
        return executor

    known_ids = {item.id for item in ledger_items}
    _mapping, anonymized_text = anonymize_positions(initial_positions, seed=seed)
    shared = _shared_context(case, ledger_items, economics, anonymized_text)

    most_favourable, least_favourable = most_and_least_favourable(initial_positions)
    least_favourable_charter = charters_by_seat[least_favourable.member]
    most_favourable_charter = charters_by_seat[most_favourable.member]

    # Forced perspective inversion: the member most favourable to funding
    # argues AGAINST it; the member least favourable argues FOR it.
    case_for_prompt = (
        f"{shared}\n\nYou are the {least_favourable.member.value.upper()} "
        f"(objective: {least_favourable_charter.objective}). Your own initial position was "
        f"{least_favourable.recommendation.value} (confidence {least_favourable.confidence_band.value}). "
        f"Regardless of that, write the single strongest, most rigorous case FOR funding this "
        f"proposal. Plain text, 3-5 sentences."
    )
    case_for_result = _executor_for(least_favourable.member).complete(case_for_prompt, fmt=None, seed=seed)
    case_for = Challenge(
        id=f"ch:case_for-{least_favourable.member.value}",
        created_at=created_at,
        type=ChallengeType.CASE_FOR,
        author_role=least_favourable.member,
        content=case_for_result.text,
        evidence_refs=extract_known_evidence_refs(case_for_result.text, known_ids),
    )

    case_against_prompt = (
        f"{shared}\n\nYou are the {most_favourable.member.value.upper()} "
        f"(objective: {most_favourable_charter.objective}). Your own initial position was "
        f"{most_favourable.recommendation.value} (confidence {most_favourable.confidence_band.value}). "
        f"Regardless of that, write the single strongest, most rigorous case AGAINST funding this "
        f"proposal. Plain text, 3-5 sentences."
    )
    case_against_result = _executor_for(most_favourable.member).complete(case_against_prompt, fmt=None, seed=seed)
    case_against = Challenge(
        id=f"ch:case_against-{most_favourable.member.value}",
        created_at=created_at,
        type=ChallengeType.CASE_AGAINST,
        author_role=most_favourable.member,
        content=case_against_result.text,
        evidence_refs=extract_known_evidence_refs(case_against_result.text, known_ids),
    )

    premortems: list[Challenge] = []
    for position in initial_positions:
        charter = charters_by_seat[position.member]
        premortem_prompt = (
            f"{shared}\n\nYou are the {position.member.value.upper()} "
            f"(objective: {charter.objective}; concerns: {'; '.join(charter.concerns)}). "
            f"Premortem: assume this decision was funded and, one year later, it turned out to be "
            f"a mistake. From your own charter's perspective, write the single most plausible "
            f"reason why. Plain text, 2-4 sentences."
        )
        premortem_result = _executor_for(position.member).complete(premortem_prompt, fmt=None, seed=seed)
        premortems.append(
            Challenge(
                id=f"ch:premortem-{position.member.value}",
                created_at=created_at,
                type=ChallengeType.PREMORTEM,
                author_role=position.member,
                content=premortem_result.text,
                evidence_refs=extract_known_evidence_refs(premortem_result.text, known_ids),
            )
        )

    return ChallengeRoundResult(case_for=case_for, case_against=case_against, premortems=premortems)
