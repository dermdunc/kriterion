"""Parses a model's raw JSON text into domain records. Never trusts the
model: every field is validated against the real enum vocabulary and every
evidence_ref is checked against the evidence actually shown to that call
(docs/v0-plan.md's "never invent an id" instruction is enforced here, not
just requested in the prompt).
"""

from __future__ import annotations

import json

from kriterion.domain.committee import BeliefUpdate, CommitteePosition, EvidenceRequest, KeyReason
from kriterion.domain.enums import ChangeType, CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase


class ResponseParsingError(ValueError):
    """The model's response could not be parsed into a valid position —
    triggers the caller's one-retry-then-abstained_error policy."""


def parse_position_response(
    raw_text: str,
    *,
    member: CommitteeSeat,
    phase: PositionPhase,
    known_evidence_ids: set[str],
    created_at: str,
    id_prefix: str,
) -> tuple[CommitteePosition, list[EvidenceRequest]]:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ResponseParsingError(f"response is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ResponseParsingError("response JSON is not an object")

    required = {"recommendation", "confidence_band", "key_reasons"}
    missing = required - data.keys()
    if missing:
        raise ResponseParsingError(f"response is missing required field(s): {missing}")

    try:
        recommendation = DecisionAction(data["recommendation"])
    except ValueError as exc:
        raise ResponseParsingError(f"invalid recommendation '{data['recommendation']}'") from exc

    try:
        confidence_band = ConfidenceBand(data["confidence_band"])
    except ValueError as exc:
        raise ResponseParsingError(f"invalid confidence_band '{data['confidence_band']}'") from exc

    key_reasons_raw = data["key_reasons"]
    if not isinstance(key_reasons_raw, list) or len(key_reasons_raw) > 3:
        raise ResponseParsingError("key_reasons must be a list of at most 3 entries")

    key_reasons: list[KeyReason] = []
    for entry in key_reasons_raw:
        refs = list(entry.get("evidence_refs", []))
        unknown_refs = [r for r in refs if r not in known_evidence_ids]
        if unknown_refs:
            raise ResponseParsingError(f"key_reasons cites unknown evidence id(s): {unknown_refs}")
        key_reasons.append(KeyReason(text=entry.get("text", ""), evidence_refs=refs))

    position = CommitteePosition(
        id=f"{id_prefix}-{member.value}-{phase.value}",
        created_at=created_at,
        member=member,
        phase=phase,
        recommendation=recommendation,
        confidence_band=confidence_band,
        key_reasons=key_reasons,
        blocking_unknowns=list(data.get("blocking_unknowns", [])),
        distrusted_assumption=data.get("distrusted_assumption"),
    )

    requests_raw = data.get("evidence_requests", [])
    evidence_requests = [
        EvidenceRequest(
            id=f"{id_prefix}-{member.value}-req-{i}",
            created_at=created_at,
            member=member,
            description=entry["description"],
            would_change=entry.get("would_change", ""),
        )
        for i, entry in enumerate(requests_raw)
    ]

    return position, evidence_requests


def parse_revision_response(
    raw_text: str,
    *,
    member: CommitteeSeat,
    initial_position: CommitteePosition,
    known_evidence_ids: set[str],
    created_at: str,
    id_prefix: str,
) -> tuple[BeliefUpdate, list[str]]:
    """Returns (belief_update, revised_blocking_unknowns). blocking_unknowns
    is asked for explicitly (defaulting to the initial position's own list
    if the model omits it) so P0-06's "no_change with the blocking unknown
    intact" pattern is actually observable on the revised CommitteePosition,
    not silently dropped.

    Caught live (2026-09-05): a model confused the fixed ten-value
    decision vocabulary with a case's own alternatives list (returned
    "targeted_role_rollout" instead of a DecisionAction), and the caller had
    no retry/validation at all for this response — an unhandled ValueError
    crashed the whole run. This function gives phase 7's revision response
    the same validate-with-a-clear-error discipline phase 3's initial
    response already had, so the caller can apply the same retry policy.
    """
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ResponseParsingError(f"response is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ResponseParsingError("response JSON is not an object")

    required = {"revised_position", "revised_confidence", "change_type"}
    missing = required - data.keys()
    if missing:
        raise ResponseParsingError(f"response is missing required field(s): {missing}")

    try:
        revised_position = DecisionAction(data["revised_position"])
    except ValueError as exc:
        raise ResponseParsingError(
            f"invalid revised_position '{data['revised_position']}' — must be one of the ten "
            f"decision-vocabulary values, not a case alternative"
        ) from exc

    try:
        revised_confidence = ConfidenceBand(data["revised_confidence"])
    except ValueError as exc:
        raise ResponseParsingError(f"invalid revised_confidence '{data['revised_confidence']}'") from exc

    try:
        change_type = ChangeType(data["change_type"])
    except ValueError as exc:
        raise ResponseParsingError(f"invalid change_type '{data['change_type']}'") from exc

    trigger_refs = list(data.get("trigger_refs", []))
    unknown_refs = [r for r in trigger_refs if r not in known_evidence_ids]
    if unknown_refs:
        raise ResponseParsingError(f"trigger_refs cites unknown evidence id(s): {unknown_refs}")

    return BeliefUpdate(
        id=f"{id_prefix}-{member.value}-belief-update",
        created_at=created_at,
        member=member,
        initial_position=initial_position.recommendation,
        initial_confidence=initial_position.confidence_band,
        revised_position=revised_position,
        revised_confidence=revised_confidence,
        change_type=change_type,
        trigger_refs=trigger_refs,
        stated_reason=data.get("stated_reason", ""),
    ), list(data.get("blocking_unknowns", initial_position.blocking_unknowns))
