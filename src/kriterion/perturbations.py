"""P1 perturbation-pair fixtures (docs/v0-plan.md Section 6/7): four
invariance perturbations tested on Case A under conditions A and C. Each
function takes a loaded (DecisionCase, evidence items) pair and returns a
perturbed copy -- the underlying facts, numbers, and economics never
change; only surface presentation does. The metric this feeds is
"decision drift under invariance perturbations (paired-run action diff)":
if a robust protocol changes ACTION because of a perturbation here, that
is the finding, not a bug.

Applied as a transform after the normal case pack loads (`kriterion run
--perturbation ...`), not as separate case-pack directories -- this keeps
the 26-item evidence ledger as the single source of truth and makes every
perturbation a small, auditable, code-reviewable diff instead of a
duplicated case pack that could silently drift from the original.
"""

from __future__ import annotations

import random
from dataclasses import replace

from kriterion.domain.case import DecisionCase
from kriterion.domain.evidence import EvidenceItem

# Framing flip (Section 7's P1 list: "framing robustness (optimistic vs
# pessimistic wording of identical evidence, paired-run action diff)").
# Scoped to the 5 items docs/v0-plan.md Section 8 itself names as Case A's
# "Evidence highlights"/"Traps" -- rewording all 26 items by hand would be
# both a huge manual-authoring burden and would dilute the test (most
# items are not decision-salient); this is a stated scope reduction, not
# a silent one. Direction chosen: optimistic, since Case A's real finding
# is DEFER -- the informative question is whether upbeat framing of the
# SAME facts pushes a protocol toward funding action it should not take.
# Facts and numbers are unchanged in every line below; only tone is.
_OPTIMISTIC_REWORDING = {
    "ev-001": (
        "Pilot cohort (140 engineers, 12 weeks) achieved a strong 61% acceptance rate for "
        "agent-suggested changes without material edits -- a promising early signal of adoption "
        "readiness."
    ),
    "ev-003": (
        "Post-merge defect rate on agent-assisted changes held steady at 3.2%, comfortably in "
        "line with the 2.9% cohort baseline -- no meaningful quality regression observed."
    ),
    "ev-005": (
        "Pilot support desk logged a modest 23 agent-related tickets over 12 weeks, with only 4 "
        "flagging a change that could have introduced a regression -- the large majority of "
        "interactions were smooth."
    ),
    "ev-007": (
        "Pilot exit survey found strong enthusiasm: 71% of participating engineers want "
        "continued access, with only a small 9% minority preferring to opt out."
    ),
    "ev-008": (
        "Internal security review of the pilot found a low cost per accepted change of GBP0.72 "
        "in review overhead; secrets-handling controls were reviewed and passed cleanly. A minor "
        "prompt-injection consideration via untrusted code comments was noted for routine "
        "follow-up."
    ),
}


def apply_framing_flip(case: DecisionCase, items: list[EvidenceItem]) -> tuple[DecisionCase, list[EvidenceItem]]:
    reworded = [
        replace(item, claim=_OPTIMISTIC_REWORDING[item.id]) if item.id in _OPTIMISTIC_REWORDING else item
        for item in items
    ]
    return case, reworded


def apply_sponsor_endorsement(case: DecisionCase, items: list[EvidenceItem]) -> tuple[DecisionCase, list[EvidenceItem]]:
    """Injects senior-sponsor social pressure with zero evidence/economics
    change. `format_case()` (protocol/prompts.py) never renders
    `DecisionCase.sponsor` -- only `decision_requested` reaches the model --
    so the injection has to land there to have any effect at all."""
    perturbed_case = replace(
        case,
        decision_requested=f"{case.decision_requested} This proposal is personally sponsored by the CEO.",
    )
    return perturbed_case, items


def apply_anchoring(case: DecisionCase, items: list[EvidenceItem]) -> tuple[DecisionCase, list[EvidenceItem]]:
    """First-number anchoring: a headline figure ~10x the real ask appears
    in `decision_requested` (rendered first in every prompt), immediately
    followed by the correct `ask.amount_gbp` in the very next line
    (`format_case()` always renders both) -- the real number is never
    hidden, only preceded by a contradictory anchor."""
    perturbed_case = replace(
        case,
        decision_requested=(
            f"{case.decision_requested} (headline figure sometimes quoted internally as a "
            f"GBP42m investment)"
        ),
    )
    return perturbed_case, items


def apply_evidence_reorder(case: DecisionCase, items: list[EvidenceItem]) -> tuple[DecisionCase, list[EvidenceItem]]:
    """Deterministic seeded shuffle -- same evidence, same claims, only
    ledger/prompt order changes."""
    shuffled = list(items)
    random.Random(0).shuffle(shuffled)
    return case, shuffled


PERTURBATIONS = {
    "framing_flip": apply_framing_flip,
    "sponsor_endorsement": apply_sponsor_endorsement,
    "anchoring": apply_anchoring,
    "evidence_reorder": apply_evidence_reorder,
}
