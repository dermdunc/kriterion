"""Baseline B's deterministic aggregation (docs/v0-plan.md Section 6):
"five independent views deterministically combined (modal action; ties
break to the more conservative action; union of conditions; minority
position preserved verbatim), with no interaction at all."

Two interpretation notes, since Section 6's wording doesn't map perfectly
onto Section 4's actual CommitteePosition schema (which has no "conditions"
field): "union of conditions" is read here as the union of blocking_unknowns
across all five positions — the closest existing field to what a funding
condition would actually be built from. "Conservative" tie-breaking uses an
explicit ranking (CONSERVATISM_ORDER below), since the plan states the rule
but not a concrete ordering over the ten-value decision vocabulary.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from kriterion.domain.committee import CommitteePosition
from kriterion.domain.enums import DecisionAction

# Index = conservatism rank, most conservative first. A judgment call, stated
# explicitly rather than left implicit: STOP/REJECT/HOLD/REDUCE withdraw or
# shrink commitment; DEFER/REQUEST_EVIDENCE pause without committing;
# DISCOVERY through SCALE commit increasing capital.
CONSERVATISM_ORDER = [
    DecisionAction.STOP,
    DecisionAction.REJECT,
    DecisionAction.HOLD,
    DecisionAction.REDUCE,
    DecisionAction.DEFER,
    DecisionAction.REQUEST_EVIDENCE,
    DecisionAction.DISCOVERY,
    DecisionAction.FUND_EXPERIMENT,
    DecisionAction.PILOT,
    DecisionAction.SCALE,
]
CONSERVATISM_RANK = {action: i for i, action in enumerate(CONSERVATISM_ORDER)}


@dataclass(kw_only=True)
class BaselineBResult:
    """Not a Section-4 domain type — Baseline B's own aggregate output,
    protocol-execution machinery like AssessmentOutcome."""

    modal_action: DecisionAction
    modal_action_count: int
    total_positions: int
    unioned_blocking_unknowns: list[str]
    minority_positions: list[CommitteePosition]


def aggregate_baseline_b(positions: list[CommitteePosition]) -> BaselineBResult:
    if not positions:
        raise ValueError("cannot aggregate an empty position list")

    counts = Counter(p.recommendation for p in positions)
    max_count = max(counts.values())
    tied_actions = [action for action, count in counts.items() if count == max_count]
    modal_action = min(tied_actions, key=lambda a: CONSERVATISM_RANK[a])

    unioned_blocking_unknowns: list[str] = []
    for p in positions:
        for unknown in p.blocking_unknowns:
            if unknown not in unioned_blocking_unknowns:
                unioned_blocking_unknowns.append(unknown)

    minority_positions = [p for p in positions if p.recommendation != modal_action]

    return BaselineBResult(
        modal_action=modal_action,
        modal_action_count=counts[modal_action],
        total_positions=len(positions),
        unioned_blocking_unknowns=unioned_blocking_unknowns,
        minority_positions=minority_positions,
    )
