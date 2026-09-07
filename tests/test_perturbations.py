from pathlib import Path

from kriterion.casepack import load_case_pack
from kriterion.perturbations import (
    PERTURBATIONS,
    apply_anchoring,
    apply_evidence_reorder,
    apply_framing_flip,
    apply_sponsor_endorsement,
)

CASE_A_DIR = Path(__file__).parent.parent / "cases" / "coding-agent-rollout"
CREATED_AT = "2026-09-07T00:00:00Z"

# Numbers that must survive framing_flip's rewording verbatim -- the whole
# point is identical facts, different tone.
_MUST_SURVIVE = {
    "ev-001": ["61%"],
    "ev-003": ["3.2%", "2.9%"],
    "ev-005": ["23", "4"],
    "ev-007": ["71%", "9%"],
    "ev-008": ["GBP0.72"],
}


def _load_case_a():
    return load_case_pack(CASE_A_DIR, created_at=CREATED_AT)


def test_framing_flip_preserves_numbers_but_changes_wording():
    case, items, _assumptions = _load_case_a()
    original_by_id = {item.id: item.claim for item in items}

    perturbed_case, perturbed_items = apply_framing_flip(case, items)

    assert perturbed_case is case  # framing flip touches evidence only
    perturbed_by_id = {item.id: item.claim for item in perturbed_items}
    for item_id, numbers in _MUST_SURVIVE.items():
        assert perturbed_by_id[item_id] != original_by_id[item_id]  # wording actually changed
        for number in numbers:
            assert number in perturbed_by_id[item_id]  # facts did not


def test_framing_flip_leaves_unreworded_items_untouched():
    case, items, _assumptions = _load_case_a()
    _perturbed_case, perturbed_items = apply_framing_flip(case, items)
    perturbed_by_id = {item.id: item.claim for item in perturbed_items}
    original_by_id = {item.id: item.claim for item in items}
    untouched_ids = set(original_by_id) - set(_MUST_SURVIVE)
    assert untouched_ids  # sanity: most of the 26 items are NOT reworded
    for item_id in untouched_ids:
        assert perturbed_by_id[item_id] == original_by_id[item_id]


def test_sponsor_endorsement_injects_ceo_language_only():
    case, items, _assumptions = _load_case_a()
    perturbed_case, perturbed_items = apply_sponsor_endorsement(case, items)

    assert "CEO" in perturbed_case.decision_requested
    assert case.decision_requested in perturbed_case.decision_requested  # additive, not replaced
    assert perturbed_case.ask.amount_gbp == case.ask.amount_gbp
    assert perturbed_items is items  # no evidence change at all


def test_anchoring_injects_wrong_headline_but_keeps_real_ask():
    case, items, _assumptions = _load_case_a()
    perturbed_case, perturbed_items = apply_anchoring(case, items)

    assert "42m" in perturbed_case.decision_requested
    assert perturbed_case.ask.amount_gbp == 4_200_000  # the REAL ask, untouched
    assert perturbed_items is items


def test_evidence_reorder_same_items_different_order():
    case, items, _assumptions = _load_case_a()
    _perturbed_case, reordered = apply_evidence_reorder(case, items)

    assert {i.id for i in reordered} == {i.id for i in items}
    assert [i.id for i in reordered] != [i.id for i in items]  # 26 items: shuffle certain to differ
    # claims themselves are untouched, only order changed
    original_by_id = {i.id: i.claim for i in items}
    for item in reordered:
        assert item.claim == original_by_id[item.id]


def test_evidence_reorder_is_deterministic():
    case, items, _assumptions = _load_case_a()
    _c1, order1 = apply_evidence_reorder(case, items)
    _c2, order2 = apply_evidence_reorder(case, items)
    assert [i.id for i in order1] == [i.id for i in order2]


def test_all_four_perturbations_registered():
    assert set(PERTURBATIONS) == {"framing_flip", "sponsor_endorsement", "anchoring", "evidence_reorder"}
