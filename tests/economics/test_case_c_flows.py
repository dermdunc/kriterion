"""Case C: NPV must be negative in every scenario, BY CONSTRUCTION -- the
avoided-loss forecast is never summed into it. See docs/v0-plan.md Section 8.
"""

from pathlib import Path

from kriterion.casepack import load_case_pack
from kriterion.economics.case_flows import case_c_cash_flows, compute_case_c_economics

CASE_C_DIR = Path(__file__).parent.parent.parent / "cases" / "invisible-ai-control-plane"
ASK_GBP = 2_400_000


def _assumptions_by_id():
    _, _, assumptions = load_case_pack(CASE_C_DIR, created_at="2026-09-05T00:00:00Z")
    return {a.id: a for a in assumptions}


def test_npv_negative_in_low_mid_and_high_scenarios():
    result = compute_case_c_economics("invisible-ai-control-plane", ASK_GBP, _assumptions_by_id())
    assert result.npv_low_gbp < 0
    assert result.npv_mid_gbp < 0
    assert result.npv_high_gbp < 0


def test_payback_never_occurs():
    result = compute_case_c_economics("invisible-ai-control-plane", ASK_GBP, _assumptions_by_id())
    assert result.payback_years is None


def test_avoided_loss_band_reported_separately_from_npv():
    result = compute_case_c_economics("invisible-ai-control-plane", ASK_GBP, _assumptions_by_id())
    assert result.avoided_loss_low_gbp == 0
    assert result.avoided_loss_high_gbp == 8_000_000
    # The band's magnitude must not have been added into NPV: even the
    # optimistic (least-negative) NPV cannot be less negative than the pure
    # cost basis, i.e. it must not have absorbed any of the 8m avoided-loss
    # upside.
    assert result.npv_high_gbp < -ASK_GBP + 1  # allow only the ongoing-cost variation, not 8m of "benefit"


def test_cash_flows_contain_no_positive_entries():
    flows = case_c_cash_flows(ask_amount_gbp=ASK_GBP)
    assert all(cf <= 0 for cf in flows)


def test_tornado_only_ranks_ongoing_cost_assumption():
    result = compute_case_c_economics("invisible-ai-control-plane", ASK_GBP, _assumptions_by_id())
    assert [e.assumption_id for e in result.tornado] == ["ongoing_annual_cost_gbp"]
