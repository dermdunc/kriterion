"""The cost-only economics model, and the one thing it adds over Case C's:
a case with no benefit band at all must report absence, never zero.

Human Run 001's case (`global-platform-engineering`) is the reason this
exists. Its ledger has no MEASURED items and every benefit-side driver is an
UNKNOWN, so it cannot honestly declare even an avoided-loss band. The case pack
itself lives outside this repository (docs/planning/human-run-001/README.md
explains why), so these tests build the assumption set inline rather than
loading it -- the behaviour under test is the engine's, not that pack's.
"""

import pytest

from kriterion.domain.evidence import Assumption, Strength
from kriterion.economics import CASE_ECONOMICS_FUNCTIONS, compute_cost_only_economics
from kriterion.economics.case_flows import compute_case_c_economics

ASK_GBP = 1_200_000
HUMAN_RUN_001_CASE_ID = "global-platform-engineering"


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
    result = compute_cost_only_economics(HUMAN_RUN_001_CASE_ID, ASK_GBP, _ongoing_only())
    # None, not 0.0: a case that cannot price its benefits is not a case whose
    # benefits are worth nothing, and a renderer must be able to tell them apart.
    assert result.avoided_loss_low_gbp is None
    assert result.avoided_loss_high_gbp is None


def test_npv_negative_in_every_scenario_and_payback_never_occurs():
    result = compute_cost_only_economics(HUMAN_RUN_001_CASE_ID, ASK_GBP, _ongoing_only())
    assert result.npv_low_gbp < 0
    assert result.npv_mid_gbp < 0
    assert result.npv_high_gbp < 0
    assert result.payback_years is None


def test_only_the_cost_assumption_is_ranked():
    """The cost of the capability is the only quantity the Human Run 001 case
    can vary. A one-entry tornado is the honest output, not a degenerate one."""
    result = compute_cost_only_economics(HUMAN_RUN_001_CASE_ID, ASK_GBP, _ongoing_only())
    assert [e.assumption_id for e in result.tornado] == ["ongoing_annual_cost_gbp"]


def test_case_c_still_requires_its_benefit_band():
    """Case C's own guarantee is unchanged: it must not silently degrade into a
    cost-only case if its avoided-loss band goes missing."""
    with pytest.raises(KeyError, match="as-avoided-loss-band-gbp"):
        compute_case_c_economics("invisible-ai-control-plane", ASK_GBP, _ongoing_only())


def test_human_run_001_case_is_wired_to_the_cost_only_model():
    assert CASE_ECONOMICS_FUNCTIONS[HUMAN_RUN_001_CASE_ID] is compute_cost_only_economics


def test_human_run_001_sensitivity_resolves_to_the_case_packs_own_assumption():
    """Without this map entry the page names a raw engine parameter instead of
    the ranged assumption, losing its evidence strength and owner."""
    from kriterion.decision_state import _PARAM_TO_ASSUMPTION_ID

    assert _PARAM_TO_ASSUMPTION_ID[HUMAN_RUN_001_CASE_ID] == {
        "ongoing_annual_cost_gbp": "as-ongoing-annual-cost-gbp",
    }
