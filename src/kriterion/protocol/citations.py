"""Shared free-text citation extraction. Used wherever a model produces
prose (case for/against, premortem) rather than structured JSON, so
citation-resolution metrics (docs/v0-plan.md Section 6) have real
structured data even from free-text steps.
"""

from __future__ import annotations

import re


def extract_known_evidence_refs(text: str, known_ids: set[str]) -> list[str]:
    """Pulls real evidence ids actually cited in free text (e.g. "evidence
    [ev-024]") into a structured list, deduplicated, order-preserved.
    Anything not in known_ids is silently dropped, not an error — free text
    isn't validated the way JSON responses are."""
    found = re.findall(r"\bev-\d+\b", text)
    seen: list[str] = []
    for ref in found:
        if ref in known_ids and ref not in seen:
            seen.append(ref)
    return seen
