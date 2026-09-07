"""Load a case pack (cases/<id>/case.toml) into domain records.

Case packs are read-only inputs (docs/v0-plan.md Section 9) — this module
never writes to a case.toml, only parses one with stdlib tomllib.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from kriterion.domain.case import Ask, DecisionCase
from kriterion.domain.evidence import Assumption, Attestation, EvidenceCategory, EvidenceItem, Strength

REQUIRED_EVIDENCE_FIELDS = (
    "id",
    "category",
    "attestation",
    "claim",
    "source",
    "period",
    "strength",
)

REQUIRED_ASSUMPTION_FIELDS = ("id", "value", "range", "evidence_strength", "owner")


class CasePackError(ValueError):
    """A case.toml is malformed or fails a required-field / vocabulary check."""


def _load_evidence_item(raw: dict, created_at: str) -> EvidenceItem:
    item_id = raw.get("id", "<unknown id>")
    for field_name in REQUIRED_EVIDENCE_FIELDS:
        if field_name not in raw:
            raise CasePackError(
                f"evidence item '{item_id}' is missing required field '{field_name}'"
            )

    try:
        category = EvidenceCategory(raw["category"])
    except ValueError as exc:
        raise CasePackError(
            f"evidence item '{item_id}' has an invalid category '{raw['category']}' "
            f"(must be one of {[c.value for c in EvidenceCategory]})"
        ) from exc

    try:
        attestation = Attestation(raw["attestation"])
    except ValueError as exc:
        raise CasePackError(
            f"evidence item '{item_id}' has an invalid attestation '{raw['attestation']}' "
            f"(must be one of {[a.value for a in Attestation]})"
        ) from exc

    try:
        strength = Strength(raw["strength"])
    except ValueError as exc:
        raise CasePackError(
            f"evidence item '{item_id}' has an invalid strength '{raw['strength']}' "
            f"(must be one of {[s.value for s in Strength]})"
        ) from exc

    return EvidenceItem(
        id=item_id,
        created_at=created_at,
        category=category,
        attestation=attestation,
        claim=raw["claim"],
        source=raw["source"],
        period=raw["period"],
        strength=strength,
        supports=list(raw.get("supports", [])),
        contradicts=list(raw.get("contradicts", [])),
    )


def _load_assumption(raw: dict, created_at: str) -> Assumption:
    a_id = raw.get("id", "<unknown id>")
    for field_name in REQUIRED_ASSUMPTION_FIELDS:
        if field_name not in raw:
            raise CasePackError(f"assumption '{a_id}' is missing required field '{field_name}'")

    try:
        evidence_strength = Strength(raw["evidence_strength"])
    except ValueError as exc:
        raise CasePackError(
            f"assumption '{a_id}' has an invalid evidence_strength '{raw['evidence_strength']}' "
            f"(must be one of {[s.value for s in Strength]})"
        ) from exc

    range_raw = raw["range"]
    if len(range_raw) != 2:
        raise CasePackError(f"assumption '{a_id}' range must have exactly 2 entries [lo, hi]")

    return Assumption(
        id=a_id,
        created_at=created_at,
        value=raw["value"],
        range=(range_raw[0], range_raw[1]),
        evidence_strength=evidence_strength,
        owner=raw["owner"],
    )


def load_injection(injection_path: Path, *, created_at: str) -> list[EvidenceItem]:
    """Loads a phase-6 evidence-injection fixture (e.g. injection.toml beside
    a case's case.toml) — a list of [[evidence]] items to add to the ledger
    at phase 6, never part of the frozen v1 ledger a case pack loads."""
    if not injection_path.is_file():
        raise CasePackError(f"no injection file found at {injection_path}")

    with injection_path.open("rb") as fh:
        raw = tomllib.load(fh)

    evidence_raw = raw.get("evidence", [])
    if not evidence_raw:
        raise CasePackError(f"{injection_path} has no [[evidence]] items")

    return [_load_evidence_item(entry, created_at=created_at) for entry in evidence_raw]


def load_case_pack(
    case_dir: Path, *, created_at: str
) -> tuple[DecisionCase, list[EvidenceItem], list[Assumption]]:
    """Parse cases/<id>/case.toml. Raises CasePackError on any malformed content."""
    case_file = case_dir / "case.toml"
    if not case_file.is_file():
        raise CasePackError(f"no case.toml found at {case_file}")

    with case_file.open("rb") as fh:
        raw = tomllib.load(fh)

    case_raw = raw.get("case")
    if case_raw is None:
        raise CasePackError(f"{case_file} has no [case] table")

    ask_raw = case_raw.get("ask")
    if ask_raw is None:
        raise CasePackError(f"{case_file}'s [case] table has no [case.ask] sub-table")

    case = DecisionCase(
        id=case_raw["id"],
        created_at=created_at,
        title=case_raw["title"],
        sponsor=case_raw["sponsor"],
        decision_owner=case_raw["decision_owner"],
        decision_requested=case_raw["decision_requested"],
        ask=Ask(
            type=ask_raw["type"],
            amount_gbp=ask_raw["amount_gbp"],
            duration=ask_raw["duration"],
        ),
        alternatives=list(case_raw["alternatives"]),
        strategic_objectives=list(case_raw.get("strategic_objectives", [])),
        deadline=case_raw.get("deadline"),
    )

    evidence_raw = raw.get("evidence", [])
    if not evidence_raw:
        raise CasePackError(f"{case_file} has no [[evidence]] items")

    seen_ids: set[str] = set()
    items: list[EvidenceItem] = []
    for entry in evidence_raw:
        item = _load_evidence_item(entry, created_at=created_at)
        if item.id in seen_ids:
            raise CasePackError(f"duplicate evidence id '{item.id}' in {case_file}")
        seen_ids.add(item.id)
        items.append(item)

    assumptions_raw = raw.get("assumptions", [])
    seen_assumption_ids: set[str] = set()
    assumptions: list[Assumption] = []
    for entry in assumptions_raw:
        assumption = _load_assumption(entry, created_at=created_at)
        if assumption.id in seen_assumption_ids:
            raise CasePackError(f"duplicate assumption id '{assumption.id}' in {case_file}")
        seen_assumption_ids.add(assumption.id)
        assumptions.append(assumption)

    return case, items, assumptions
