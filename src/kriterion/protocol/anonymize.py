"""Seeded anonymisation + shuffling of positions for phase 5/7's visibility
rule: "anonymised positions only — no tally, no authorship, no counts"
(docs/v0-plan.md Section 5). The mapping is internal only — Challenge and
CommitteePosition records still carry their real author_role/member; only
the TEXT shown to other members in a prompt hides identity.
"""

from __future__ import annotations

import random

from kriterion.domain.committee import CommitteePosition
from kriterion.domain.enums import CommitteeSeat

LABELS = ["Member A", "Member B", "Member C", "Member D", "Member E"]


def anonymize_positions(
    positions: list[CommitteePosition], *, seed: int
) -> tuple[dict[CommitteeSeat, str], str]:
    """Returns (seat -> anonymous label mapping, formatted text) with the
    5 positions shuffled deterministically by `seed`. No tally/count of any
    kind is included in the formatted text — each position is listed
    individually, never aggregated."""
    rng = random.Random(seed)
    shuffled = list(positions)
    rng.shuffle(shuffled)

    mapping = {p.member: label for p, label in zip(shuffled, LABELS)}

    lines = []
    for position in shuffled:
        label = mapping[position.member]
        reasons = "; ".join(r.text for r in position.key_reasons)
        lines.append(
            f"{label}: recommends {position.recommendation.value} "
            f"(confidence {position.confidence_band.value}). Reasons: {reasons}"
        )
    return mapping, "\n".join(lines)
