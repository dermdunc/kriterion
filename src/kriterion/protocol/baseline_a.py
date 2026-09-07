"""Strong Baseline A (docs/v0-plan.md Section 6): one model, one continuous
context, performing the SAME cognitive operations as the committee — just
without independent contexts. That is the entire experimental variable; see
§6's own warning: "if you find yourself weakening A, stop — that is the
experiment." This module is not permitted to skip a step to save calls.

Sequence, all in one executor context (Section 6's numbered list):
  1. structured assessment against all five charters' checklists, collapsed
  2. self-generated strongest case for
  3. self-generated strongest case against
  4. premortem
  5. evidence requests (folded into step 1's structured output)
  6. the same phase-6 evidence injection
  7. revised assessment + BeliefUpdate
  8. final output: same schema as the committee's synthesis
     (SyntheticRecommendation-shaped), non-empty dissent mandatory — built
     from step 3's own case-against, since a single continuous voice has no
     other member to dissent from it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from kriterion.domain.case import DecisionCase
from kriterion.domain.committee import BeliefUpdate, CommitteePosition, EvidenceRequest, RoleCharter
from kriterion.domain.decision import Dissent, SyntheticRecommendation
from kriterion.domain.economics import EconomicsResult
from kriterion.domain.enums import CommitteeSeat, PositionPhase
from kriterion.domain.evidence import EvidenceItem
from kriterion.executors.base import Executor
from kriterion.protocol.chair import NARRATIVE_PROMPT_TEMPLATE
from kriterion.protocol.citations import extract_known_evidence_refs
from kriterion.protocol.parsing import ResponseParsingError, parse_position_response, parse_revision_response
from kriterion.protocol.prompts import POSITION_JSON_SCHEMA, format_case, format_economics, format_evidence

COLLAPSED_MEMBER_LABEL = "baseline_a"


def _collapsed_charter_brief(charters: list[RoleCharter]) -> str:
    lines = []
    for charter in charters:
        lines.append(
            f"- {charter.seat.value.upper()}: objective — {charter.objective}; "
            f"concerns — {'; '.join(charter.concerns)}"
        )
    return "\n".join(lines)


@dataclass(kw_only=True)
class BaselineACallRecord:
    step: str
    prompt: str
    response_text: str


@dataclass(kw_only=True)
class BaselineAResult:
    """Not a Section-4 domain type on its own — bundles the final
    SyntheticRecommendation-shaped output with the intermediate belief
    update and the full call transcript, for token-budget reporting
    (Section 6: "its token budget is recorded and reported alongside C's")."""

    recommendation: SyntheticRecommendation
    belief_update: BeliefUpdate
    evidence_requests: list[EvidenceRequest]
    # Caught live running task 14's kriterion compare: neither this nor
    # initial_position was exposed here, so the CLI had nothing to persist
    # for the P0-03/04/05 scorers to scan against a Baseline A run --
    # unlike B/C's positions_initial.json/positions_revised.json, Baseline
    # A's own rich intermediate content (initial assessment, self-generated
    # case for/against, premortem) simply didn't exist as a run artifact at
    # all. Exposed now so cli.py can write it.
    initial_position: CommitteePosition | None = None
    narrative: str = ""
    calls: list[BaselineACallRecord] = field(default_factory=list)


def run_baseline_a(
    executor: Executor,
    charters: list[RoleCharter],
    case: DecisionCase,
    ledger_items: list[EvidenceItem],
    injected_items: list[EvidenceItem],
    economics: EconomicsResult,
    *,
    seed: int,
    created_at: str,
    run_id: str,
) -> BaselineAResult:
    evidence_by_id = {item.id: item for item in ledger_items}
    known_ids = set(evidence_by_id.keys())
    calls: list[BaselineACallRecord] = []

    # Step 1: structured assessment against all five charters, collapsed.
    step1_prompt = (
        "You are a single strong analyst producing an executive investment assessment. "
        "You must address every one of the following stakeholder perspectives yourself, "
        "in one assessment — there is no committee, only you covering all of their concerns:\n"
        f"{_collapsed_charter_brief(charters)}\n\n"
        f"{format_case(case)}\n\n"
        f"Evidence:\n{format_evidence(ledger_items)}\n\n"
        f"{format_economics(economics)}\n\n"
        f"{POSITION_JSON_SCHEMA}"
    )
    initial_position = None
    initial_requests: list[EvidenceRequest] = []
    for _attempt in range(2):
        result = executor.complete(step1_prompt, fmt="json", seed=seed)
        calls.append(BaselineACallRecord(step="1_initial_assessment", prompt=step1_prompt, response_text=result.text))
        try:
            initial_position, initial_requests = parse_position_response(
                result.text,
                member=CommitteeSeat.BASELINE_A,
                phase=PositionPhase.INITIAL,
                known_evidence_ids=known_ids,
                created_at=created_at,
                id_prefix=f"{run_id}-{COLLAPSED_MEMBER_LABEL}",
            )
            break
        except ResponseParsingError:
            continue
    if initial_position is None:
        raise ResponseParsingError("Baseline A step 1 (initial assessment) failed twice — abstained_error")

    # executor.complete() is a single stateless call (Ollama's /api/generate
    # has no chat history) — there is no implicit memory between steps.
    # "One continuous context" for Baseline A therefore means explicitly
    # re-including the case, evidence, and prior-step output in every
    # subsequent prompt, not relying on conversation carryover. Omitting
    # this was a real bug caught by manually inspecting a live run: without
    # real evidence in context, the model fabricated placeholder-style
    # citations ("Evidence ID: E1") instead of citing real ev-* ids.
    shared_context = (
        f"{format_case(case)}\n\nEvidence:\n{format_evidence(ledger_items)}\n\n"
        f"{format_economics(economics)}\n\n"
        f"Your prior assessment: {initial_position.recommendation.value}, "
        f"confidence {initial_position.confidence_band.value}.\n\n"
        "If you cite evidence, use only the real ids listed above (e.g. ev-001) — "
        "never invent a citation format or an id that is not listed."
    )

    # Step 2: self-generated strongest case FOR.
    case_for_prompt = (
        f"{shared_context}\n\nWrite the single strongest, most rigorous case FOR the "
        f"recommendation you are leaning toward. Plain text, 3-5 sentences."
    )
    case_for_result = executor.complete(case_for_prompt, fmt=None, seed=seed)
    calls.append(BaselineACallRecord(step="2_case_for", prompt=case_for_prompt, response_text=case_for_result.text))

    # Step 3: self-generated strongest case AGAINST.
    case_against_prompt = (
        f"{shared_context}\n\nNow write the single strongest, most rigorous case AGAINST your "
        f"own leaning recommendation — steelman the opposing view. Plain text, 3-5 sentences."
    )
    case_against_result = executor.complete(case_against_prompt, fmt=None, seed=seed)
    calls.append(
        BaselineACallRecord(step="3_case_against", prompt=case_against_prompt, response_text=case_against_result.text)
    )

    # Step 4: premortem.
    premortem_prompt = (
        f"{shared_context}\n\nPremortem: assume this decision was made and, one year later, it "
        f"turned out to be a mistake. Write the single most plausible reason why, in plain text, "
        f"2-4 sentences."
    )
    premortem_result = executor.complete(premortem_prompt, fmt=None, seed=seed)
    calls.append(BaselineACallRecord(step="4_premortem", prompt=premortem_prompt, response_text=premortem_result.text))

    # Step 6 (step 5 folded into step 1's evidence_requests): the same
    # phase-6 evidence injection Treatment C gets.
    all_items_after_injection = ledger_items + injected_items
    known_ids_after_injection = known_ids | {item.id for item in injected_items}

    # Step 7: revised assessment + BeliefUpdate. Phase 7's real spec (Section
    # 5) hands the reviser the full ledger v2, not just the delta. Full case
    # + economics re-included too, per the same stateless-executor note above.
    revised_prompt = (
        f"{format_case(case)}\n\n{format_economics(economics)}\n\n"
        f"Your case FOR your leaning recommendation was:\n{case_for_result.text}\n\n"
        f"Your case AGAINST it was:\n{case_against_result.text}\n\n"
        f"Your premortem was:\n{premortem_result.text}\n\n"
        f"New evidence has been added since your initial assessment:\n"
        f"{format_evidence(injected_items)}\n\n"
        f"Full evidence ledger (v2, including the new item above):\n"
        f"{format_evidence(all_items_after_injection)}\n\n"
        f"Reconsider your initial assessment ({initial_position.recommendation.value}, "
        f"confidence {initial_position.confidence_band.value}) in light of this.\n\n"
        f"IMPORTANT: revised_position must be one of these exact ten decision-vocabulary "
        f"values — REJECT, DEFER, REQUEST_EVIDENCE, DISCOVERY, FUND_EXPERIMENT, PILOT, SCALE, "
        f"HOLD, REDUCE, STOP — never one of the case's alternatives "
        f"({', '.join(case.alternatives)}). Those are different vocabularies.\n\n"
        f"Respond with a single JSON object, no other text:\n"
        "{\n"
        '  "revised_position": "<one of the ten decision-vocabulary values above>",\n'
        '  "revised_confidence": "LOW"|"MEDIUM"|"HIGH",\n'
        '  "change_type": "evidence_driven"|"argument_driven"|"no_change"|"unexplained",\n'
        '  "trigger_refs": ["ev-...", ...],\n'
        '  "stated_reason": "...",\n'
        '  "blocking_unknowns": ["<plain-language description of each still-unresolved concern, '
        "NOT an evidence id -- e.g. 'whether the security review covers regulated-data systems', "
        "not 'ev-008'. Carry forward any concern you have not actually seen resolved.>\"]\n"
        "}"
    )

    belief_update = None
    revised_blocking_unknowns = initial_position.blocking_unknowns
    for _attempt in range(2):  # same 1-try + 1-retry policy as phase 3
        revised_result = executor.complete(revised_prompt, fmt="json", seed=seed)
        calls.append(
            BaselineACallRecord(step="7_revised_and_belief_update", prompt=revised_prompt, response_text=revised_result.text)
        )
        try:
            belief_update, revised_blocking_unknowns = parse_revision_response(
                revised_result.text,
                member=CommitteeSeat.BASELINE_A,
                initial_position=initial_position,
                known_evidence_ids=known_ids_after_injection,
                created_at=created_at,
                id_prefix=run_id,
            )
            break
        except ResponseParsingError:
            continue
    if belief_update is None:
        raise ResponseParsingError("Baseline A step 7 (revised assessment) failed twice — abstained_error")

    recommendation = SyntheticRecommendation(
        id=f"{run_id}-{COLLAPSED_MEMBER_LABEL}-recommendation",
        created_at=created_at,
        action=belief_update.revised_position,
        amount=case.ask.amount_gbp,
        duration=case.ask.duration,
        conditions=list(revised_blocking_unknowns),
        stop_conditions=[],
        strongest_dissent=Dissent(
            verbatim=case_against_result.text,
            refs=extract_known_evidence_refs(case_against_result.text, known_ids),
        ),
        unresolved_unknowns=list(revised_blocking_unknowns),
        confidence_band=belief_update.revised_confidence,
    )

    # Step 8 (parity with the committee's chair, Section 5): "Baseline A
    # receives an identical narrative treatment, so it cannot act as an
    # uncontrolled variable between conditions." Same bounded-narrative
    # template as protocol/chair.py's synthesize().
    narrative_prompt = NARRATIVE_PROMPT_TEMPLATE.format(
        decision_requested=case.decision_requested,
        action=recommendation.action.value,
        confidence=recommendation.confidence_band.value,
        conditions="; ".join(recommendation.conditions) or "none",
        dissent=recommendation.strongest_dissent.verbatim,
    )
    narrative_result = executor.complete(narrative_prompt, fmt=None, seed=seed)
    calls.append(BaselineACallRecord(step="8_narrative", prompt=narrative_prompt, response_text=narrative_result.text))

    return BaselineAResult(
        recommendation=recommendation,
        belief_update=belief_update,
        evidence_requests=initial_requests,
        initial_position=initial_position,
        narrative=narrative_result.text,
        calls=calls,
    )
