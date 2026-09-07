"""Loads charters/<seat>.v1.toml into RoleCharter records.

Charters are read-only inputs, same posture as case packs (kriterion.casepack).
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from kriterion.domain.committee import RoleCharter
from kriterion.domain.enums import CommitteeSeat

REQUIRED_CHARTER_FIELDS = (
    "id",
    "version",
    "seat",
    "objective",
    "concerns",
    "required_evidence",
    "decision_rights",
    "standard_challenges",
    "failure_modes",
    "forbidden",
)

# Section 9's tree lists these five filenames explicitly.
CHARTER_FILENAMES = {
    CommitteeSeat.CFO: "cfo.v1.toml",
    CommitteeSeat.CTO: "cto.v1.toml",
    CommitteeSeat.CISO: "ciso.v1.toml",
    CommitteeSeat.CRO_COMPLIANCE: "cro.v1.toml",
    CommitteeSeat.BUSINESS_EXECUTIVE: "bizexec.v1.toml",
}


class CharterError(ValueError):
    """A charter TOML file is malformed or fails a required-field check."""


def load_charter(path: Path, *, created_at: str) -> RoleCharter:
    if not path.is_file():
        raise CharterError(f"no charter file found at {path}")

    with path.open("rb") as fh:
        raw = tomllib.load(fh)

    for field_name in REQUIRED_CHARTER_FIELDS:
        if field_name not in raw:
            raise CharterError(f"{path} is missing required field '{field_name}'")

    try:
        seat = CommitteeSeat(raw["seat"])
    except ValueError as exc:
        raise CharterError(
            f"{path} has an invalid seat '{raw['seat']}' "
            f"(must be one of {[s.value for s in CommitteeSeat]})"
        ) from exc

    return RoleCharter(
        id=raw["id"],
        created_at=created_at,
        version=raw["version"],
        seat=seat,
        objective=raw["objective"],
        concerns=list(raw["concerns"]),
        required_evidence=list(raw["required_evidence"]),
        decision_rights=list(raw["decision_rights"]),
        standard_challenges=list(raw["standard_challenges"]),
        failure_modes=list(raw["failure_modes"]),
        forbidden=list(raw["forbidden"]),
    )


def load_all_charters(charters_dir: Path, *, created_at: str) -> dict[CommitteeSeat, RoleCharter]:
    """Loads all five v1 charters. Raises CharterError if any is missing or malformed."""
    return {
        seat: load_charter(charters_dir / filename, created_at=created_at)
        for seat, filename in CHARTER_FILENAMES.items()
    }
