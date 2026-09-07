"""Case A economics integration test. Expected values below are recomputed
independently from case_a_cash_flows' own documented formula (benefit =
active_engineers x fully_loaded_cost x uplift x attribution_factor, minus
staged capex/training/support), not copied from the engine's own output --
this is what "hand-computed" means for a well-defined financial formula
where there is only one correct calculation method.
"""

import json
from pathlib import Path

import pytest

from kriterion.casepack import load_case_pack
from kriterion.domain.serialization import to_dict
from kriterion.economics.case_flows import (
    DISCOVERY_GBP,
    PILOT_GBP,
    TARGETED_SCALE_GBP,
    YEAR_1_ENGINEERS,
    YEAR_2_ENGINEERS,
    compute_economics,
)

CASE_A_DIR = Path(__file__).parent.parent.parent / "cases" / "coding-agent-rollout"
ASK_GBP = 4_200_000
RATE = 0.10


def _hand_computed_base_flows():
    year_1_capex = DISCOVERY_GBP + PILOT_GBP + TARGETED_SCALE_GBP
    year_2_capex = ASK_GBP - year_1_capex
    year_1_training = YEAR_1_ENGINEERS * 340
    year_2_training = (YEAR_2_ENGINEERS - YEAR_1_ENGINEERS) * 340
    benefit_1 = YEAR_1_ENGINEERS * 120_000 * 0.18 * 0.10
    benefit_2 = YEAR_2_ENGINEERS * 120_000 * 0.18 * 0.10
    year_1_net = benefit_1 - year_1_capex - year_1_training
    year_2_net = benefit_2 - year_2_capex - year_2_training - 1_350_000
    return [year_1_net, year_2_net]


def _load_assumptions_by_id():
    _, _, assumptions = load_case_pack(CASE_A_DIR, created_at="2026-09-05T00:00:00Z")
    return {a.id: a for a in assumptions}


def test_base_case_npv_matches_hand_computation():
    flows = _hand_computed_base_flows()
    expected_npv = sum(cf / (1 + RATE) ** (t + 1) for t, cf in enumerate(flows))

    result = compute_economics("coding-agent-rollout", ASK_GBP, _load_assumptions_by_id())

    assert result.npv_mid_gbp == pytest.approx(expected_npv, rel=1e-9)
    assert result.npv_mid_gbp == pytest.approx(5_085_454.545454544, rel=1e-9)


def test_low_scenario_is_worse_than_mid_which_is_worse_than_high():
    result = compute_economics("coding-agent-rollout", ASK_GBP, _load_assumptions_by_id())
    assert result.npv_low_gbp < result.npv_mid_gbp < result.npv_high_gbp
    # By construction (see case_flows.py's pessimistic/optimistic kwargs),
    # the low scenario should be materially negative and the high scenario
    # should dominate the ask by a wide margin -- both hand-verified above
    # module docstring's design reasoning.
    assert result.npv_low_gbp < 0
    assert result.npv_high_gbp > ASK_GBP


def test_tornado_ranks_all_five_assumptions():
    result = compute_economics("coding-agent-rollout", ASK_GBP, _load_assumptions_by_id())
    ranked_ids = [entry.assumption_id for entry in result.tornado]
    assert set(ranked_ids) == {
        "uplift",
        "fully_loaded_cost_gbp",
        "attribution_factor",
        "training_cost_per_engineer_gbp",
        "annual_support_cost_gbp",
    }
    # Sorted descending by |swing| — the first entry must be the single
    # largest swing.
    swings = [abs(e.npv_swing_gbp) for e in result.tornado]
    assert swings == sorted(swings, reverse=True)


def test_economics_result_fingerprint_stable_under_key_reordering():
    from kriterion.domain.serialization import canonical_json

    result = compute_economics("coding-agent-rollout", ASK_GBP, _load_assumptions_by_id())
    d1 = to_dict(result)
    d2 = {k: d1[k] for k in reversed(list(d1.keys()))}
    assert canonical_json(d1) == canonical_json(d2)


def test_economics_result_is_json_serialisable():
    result = compute_economics("coding-agent-rollout", ASK_GBP, _load_assumptions_by_id())
    text = json.dumps(to_dict(result))
    parsed = json.loads(text)
    assert parsed["case_id"] == "coding-agent-rollout"
