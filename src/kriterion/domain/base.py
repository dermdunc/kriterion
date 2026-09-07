"""Shared record base — not in docs/v0-plan.md Section 9's module list explicitly,
but every domain type needs id/schema_version/created_at (Section 4's stated
universal convention) and putting it in its own module avoids a cross-import
cycle between case.py/evidence.py/committee.py/decision.py."""

from __future__ import annotations

from dataclasses import dataclass

SCHEMA_VERSION = "kriterion/v0.1"


@dataclass(kw_only=True)
class KriterionRecord:
    id: str
    created_at: str  # ISO 8601 — caller-supplied, never wall-clock at construction time
    schema_version: str = SCHEMA_VERSION
