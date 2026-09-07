"""DecisionCase and Ask (docs/v0-plan.md Section 4 and Section 9's module layout).

Section 9's layout comment names this module "DecisionCase, Alternative, Ask",
but Section 4's own field table gives `alternatives` as a plain list of
identifier strings (e.g. "do_nothing", "limited_pilot") with no separate
`Alternative` fields defined anywhere in the plan — the fixture examples in
Section 8 only ever reference alternatives by bare name. Treating
`alternatives: list[str]` as the real contract and "Alternative" in the
layout comment as referring to that list, not an undefined richer type, since
inventing fields for a type the plan never specifies would be guessing.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from kriterion.domain.base import KriterionRecord
from kriterion.domain.enums import CaseRealism


@dataclass(kw_only=True)
class Ask:
    type: str
    amount_gbp: float
    duration: str


@dataclass(kw_only=True)
class DecisionCase(KriterionRecord):
    title: str
    sponsor: str
    decision_owner: str
    decision_requested: str  # one sentence
    ask: Ask
    alternatives: list[str]
    strategic_objectives: list[str] = field(default_factory=list)
    deadline: str | None = None
    case_realism: CaseRealism = CaseRealism.AUTHORED_FIXTURE
    not_normalisable: bool = False

    def __post_init__(self) -> None:
        if not self.not_normalisable:
            if len(self.alternatives) < 2:
                raise ValueError("DecisionCase.alternatives must have at least 2 entries")
            if "do_nothing" not in self.alternatives:
                raise ValueError("DecisionCase.alternatives must always include 'do_nothing'")
