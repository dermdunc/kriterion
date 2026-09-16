"""The cost-only economics model, and the one thing it adds over Case C's:
a case with no benefit band at all must report absence, never zero.

This model exists for a case whose ledger has no MEASURED items and whose every
benefit-side driver is an UNKNOWN, so it cannot honestly declare even an
avoided-loss band. It is deliberately NOT wired to any case id in
`CASE_ECONOMICS_FUNCTIONS` right now: it is reachable through
`compute_case_c_economics`, and available to any future case pack in that
condition. These tests therefore build the assumption set inline and use a
placeholder case id -- the behaviour under test is the engine's, not any
particular pack's.
"""

import pytest

from kriterion.domain.evidence import Assumption, Strength
from kriterion.economics import CASE_ECONOMICS_FUNCTIONS, compute_cost_only_economics
from kriterion.economics.case_flows import compute_case_c_economics

ASK_GBP = 1_200_000
UNPRICED_BENEFIT_CASE_ID = "any-case-whose-benefits-cannot-be-priced"


def _ongoing_only() -> dict[str, Assumption]:
    return {
        "as-ongoing-annual-cost-gbp": Assumption(
            id="as-ongoing-annual-cost-gbp",
            created_at="2026-09-12T00:00:00Z",
            value=840_000,
            range=(560_000, 1_120_000),
            evidence_strength=Strength.LOW,
            owner="cfo",
        )
    }


def test_missing_benefit_band_reports_absence_not_zero():
    result = compute_cost_only_economics(UNPRICED_BENEFIT_CASE_ID, ASK_GBP, _ongoing_only())
    # None, not 0.0: a case that cannot price its benefits is not a case whose
    # benefits are worth nothing, and a renderer must be able to tell them apart.
    assert result.avoided_loss_low_gbp is None
    assert result.avoided_loss_high_gbp is None


def test_npv_negative_in_every_scenario_and_payback_never_occurs():
    result = compute_cost_only_economics(UNPRICED_BENEFIT_CASE_ID, ASK_GBP, _ongoing_only())
    assert result.npv_low_gbp < 0
    assert result.npv_mid_gbp < 0
    assert result.npv_high_gbp < 0
    assert result.payback_years is None


def test_only_the_cost_assumption_is_ranked():
    """The cost of the capability is the only quantity such a case can vary.
    A one-entry tornado is the honest output here, not a degenerate one."""
    result = compute_cost_only_economics(UNPRICED_BENEFIT_CASE_ID, ASK_GBP, _ongoing_only())
    assert [e.assumption_id for e in result.tornado] == ["ongoing_annual_cost_gbp"]


def test_case_c_still_requires_its_benefit_band():
    """Case C's own guarantee is unchanged: it must not silently degrade into a
    cost-only case if its avoided-loss band goes missing."""
    with pytest.raises(KeyError, match="as-avoided-loss-band-gbp"):
        compute_case_c_economics("invisible-ai-control-plane", ASK_GBP, _ongoing_only())


def test_cost_only_model_is_not_wired_to_a_case_id():
    """Guard against a future case being pointed at the cost-only model by
    habit. A case that CAN price a benefit side must not use this one, because
    reporting `avoided_loss_*` as None would then be a false absence rather
    than an honest one."""
    assert compute_cost_only_economics not in CASE_ECONOMICS_FUNCTIONS.values()
