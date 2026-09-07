"""Protocol phases 0-4 (docs/v0-plan.md Section 5's phase table). Phases
5-8 (challenge, injection, revision, synthesis) are task 10's job — this
module only builds what Baseline A/B and Treatment C's early phases share.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from kriterion.domain.case import DecisionCase
from kriterion.domain.committee import BeliefUpdate, Challenge, CommitteePosition, EvidenceRequest, RoleCharter
from kriterion.domain.economics import EconomicsResult
from kriterion.domain.enums import CommitteeSeat, DecisionAction, PositionPhase
from kriterion.domain.evidence import EvidenceItem
from kriterion.executors.base import Executor, ExecutorError
from kriterion.protocol.drift import derive_drift_flags
from kriterion.protocol.parsing import ResponseParsingError, parse_position_response, parse_revision_response
from kriterion.protocol.prompts import (
    PROTOCOL_ID,
    build_phase3_prompt,
    format_case,
    format_economics,
    format_evidence,
)


@dataclass(kw_only=True)
class AssessmentOutcome:
    """Phase 3's real per-member result: either a valid position, or an
    abstained_error after the model failed to produce parseable JSON twice
    (docs/v0-plan.md Section 5's phase-3 failure policy: "invalid JSON -> 1
    retry -> abstained_error"). Not a domain type from Section 4's table —
    this is phase-execution machinery, kept out of domain/ on purpose."""

    member: CommitteeSeat
    status: str  # "ok" | "abstained_error"
    position: CommitteePosition | None = None
    evidence_requests: list[EvidenceRequest] = field(default_factory=list)
    raw_attempts: list[str] = field(default_factory=list)


def run_phase3_independent_assessment(
    executor: Executor,
    charter: RoleCharter,
    case: DecisionCase,
    evidence_by_id: dict,
    economics: EconomicsResult,
    *,
    seed: int,
    created_at: str,
    run_id: str,
) -> AssessmentOutcome:
    """One member's isolated-context initial assessment: full case ledger +
    economics + this charter only — never another member's charter or
    position (phase 3's stated visibility rule, docs/v0-plan.md Section 5:
    "case, ledger, economics, own charter only").

    Caught live testing Case C (2026-09-05): an earlier version filtered the
    shown evidence down to charter.required_evidence, which hardcodes Case
    A's own evidence ids — on a second case with different ids, most
    charters saw zero evidence and abstained. required_evidence is a
    checklist gap_scan.py checks a position against after the fact, never a
    filter on what evidence a member is shown."""
    evidence_items = list(evidence_by_id.values())
    known_ids = set(evidence_by_id.keys())
    prompt = build_phase3_prompt(charter, case, evidence_items, economics)

    raw_attempts: list[str] = []
    for _attempt in range(2):  # 1 try + 1 retry, per Section 5's stated policy
        result = executor.complete(prompt, fmt="json", seed=seed)
        raw_attempts.append(result.text)
        try:
            position, requests = parse_position_response(
                result.text,
                member=charter.seat,
                phase=PositionPhase.INITIAL,
                known_evidence_ids=known_ids,
                created_at=created_at,
                id_prefix=run_id,
            )
            return AssessmentOutcome(
                member=charter.seat,
                status="ok",
                position=position,
                evidence_requests=requests,
                raw_attempts=raw_attempts,
            )
        except ResponseParsingError:
            continue

    return AssessmentOutcome(member=charter.seat, status="abstained_error", raw_attempts=raw_attempts)


@dataclass(kw_only=True)
class SealedTally:
    """Phase 4: the tally is computed and written to disk for the analyst,
    but MUST NEVER be passed into any prompt at any later phase — that is
    ADR-004's ruling in its entirety. Callers must not read this object
    when building a phase 5/7 prompt; nothing in this module does."""

    counts: dict[str, int]
    modal_action: str | None


def seal_phase4_tally(outcomes: list[AssessmentOutcome]) -> SealedTally:
    ok_positions = [o.position for o in outcomes if o.status == "ok" and o.position is not None]
    counts = Counter(p.recommendation.value for p in ok_positions)
    modal_action = counts.most_common(1)[0][0] if counts else None
    return SealedTally(counts=dict(counts), modal_action=modal_action)


@dataclass(kw_only=True)
class RevisionOutcome:
    member: CommitteeSeat
    status: str  # "ok" | "abstained_error"
    revised_position: CommitteePosition | None = None
    belief_update: BeliefUpdate | None = None
    raw_attempts: list[str] = field(default_factory=list)


def _format_challenges(challenges: list[Challenge]) -> str:
    """Shows each challenge's real `id` alongside its content -- caught
    live (2026-09-07, the P1 perturbation batch): omitting it here meant a
    model that wanted to cite a challenge artifact as a trigger_ref had no
    way to know the real id format (`ch:premortem-ciso`), and instead
    guessed an abbreviated one (`ch:premortem`) from the `[type]` tag shown
    -- a well-formed, otherwise-valid response, rejected by
    parse_revision_response's exact-id check every single time. Every
    revised-assessment run this session had used only bare `ev-` ids until
    this batch, so the gap was real but unexercised until a live run
    actually tried to cite one."""
    lines = []
    for ch in challenges:
        lines.append(f"  [{ch.id}] ({ch.type.value}) {ch.content}")
    return "\n".join(lines)


def run_phase7_revised_assessment(
    executor: Executor,
    initial_position: CommitteePosition,
    charter: RoleCharter,
    case: DecisionCase,
    ledger_v2_items: list[EvidenceItem],
    challenges: list[Challenge],
    economics: EconomicsResult,
    *,
    new_evidence_ids: set[str],
    seed: int,
    created_at: str,
    run_id: str,
) -> RevisionOutcome:
    """One member's isolated-context revision (docs/v0-plan.md Section 5,
    phase 7): "own initial position, all challenge artifacts, ledger v2,
    recomputed economics" — no tally, no counts, no authored positions
    (challenges passed here must already be anonymised by the caller if
    they include other members' content; case_for/case_against/premortem
    text itself carries no seat name in this implementation, only its
    `type`, so no separate anonymisation step is needed at this phase).

    `new_evidence_ids` is the phase-6-injected subset of `ledger_v2_items`
    (empty for a run with no injection) -- used only to derive drift_flags
    (docs/v0-plan.md Section 5's "meaningful update" definition), never to
    filter what the model is shown.
    """
    # Challenge artifact ids (ch:-prefixed) are valid trigger_refs per
    # Section 5's own example (`[ev:..., ch:premortem-ciso]`) -- caught live
    # (2026-09-06): they were previously rejected as "unknown evidence ids"
    # because known_ids only ever included the evidence ledger.
    known_ids = {item.id for item in ledger_v2_items} | {c.id for c in challenges}
    prompt = (
        f"{format_case(case)}\n\nEvidence ledger v2 (includes new evidence since your initial "
        f"assessment):\n{format_evidence(ledger_v2_items)}\n\n{format_economics(economics)}\n\n"
        f"Your objective: {charter.objective}\n\n"
        f"Your own initial position: {initial_position.recommendation.value} "
        f"(confidence {initial_position.confidence_band.value}).\n\n"
        f"Challenge artifacts from this round (no authorship shown, no tally):\n"
        f"{_format_challenges(challenges)}\n\n"
        f"Reconsider your position in light of the above.\n\n"
        f"IMPORTANT: revised_position must be one of these exact ten decision-vocabulary "
        f"values — REJECT, DEFER, REQUEST_EVIDENCE, DISCOVERY, FUND_EXPERIMENT, PILOT, SCALE, "
        f"HOLD, REDUCE, STOP — never one of the case's alternatives "
        f"({', '.join(case.alternatives)}).\n\n"
        f"Respond with a single JSON object, no other text:\n"
        "{\n"
        '  "revised_position": "<one of the ten decision-vocabulary values above>",\n'
        '  "revised_confidence": "LOW"|"MEDIUM"|"HIGH",\n'
        '  "change_type": "evidence_driven"|"argument_driven"|"no_change"|"unexplained",\n'
        '  "trigger_refs": ["<the real \'ev-...\' or \'ch:...\' id(s) above that actually changed '
        'your mind -- a challenge artifact id is a valid trigger, not just an evidence id>"],\n'
        '  "stated_reason": "...",\n'
        '  "blocking_unknowns": ["<plain-language description of each still-unresolved concern, '
        "NOT an evidence id -- e.g. 'whether the security review covers regulated-data systems', "
        "not 'ev-008'. Carry forward any concern you have not actually seen resolved.>\"]\n"
        "}"
    )

    raw_attempts: list[str] = []
    for _attempt in range(2):
        result = executor.complete(prompt, fmt="json", seed=seed)
        raw_attempts.append(result.text)
        try:
            belief_update, revised_blocking_unknowns = parse_revision_response(
                result.text,
                member=charter.seat,
                initial_position=initial_position,
                known_evidence_ids=known_ids,
                created_at=created_at,
                id_prefix=run_id,
            )
            belief_update.drift_flags = derive_drift_flags(
                belief_update, new_since_phase3_ids=new_evidence_ids, challenges=challenges
            )
            revised_position = CommitteePosition(
                id=f"{run_id}-{charter.seat.value}-revised",
                created_at=created_at,
                member=charter.seat,
                phase=PositionPhase.REVISED,
                recommendation=belief_update.revised_position,
                confidence_band=belief_update.revised_confidence,
                key_reasons=initial_position.key_reasons,
                blocking_unknowns=revised_blocking_unknowns,
                distrusted_assumption=initial_position.distrusted_assumption,
            )
            return RevisionOutcome(
                member=charter.seat,
                status="ok",
                revised_position=revised_position,
                belief_update=belief_update,
                raw_attempts=raw_attempts,
            )
        except ResponseParsingError:
            continue

    return RevisionOutcome(member=charter.seat, status="abstained_error", raw_attempts=raw_attempts)
