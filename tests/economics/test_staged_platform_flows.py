"""The staged, adoption-limited platform economics model.

This model exists for Human Run 001's `northstar-internal-developer-platform`
case. Its reason to exist rather than reusing Case A's is that it holds no
case-specific constant: `case_a_cash_flows` bakes Case A's 1,200/5,000 engineer
ramp and its GBP2.07m stage ladder into module constants, so a second case
pointed at it would have those numbers rendered onto its page as if they were
its own. The tests below pin that property, not just the arithmetic.
"""

import inspect

import pytest

from kriterion.domain.evidence import Assumption, Strength
from kriterion.economics import CASE_ECONOMICS_FUNCTIONS, compute_staged_platform_economics
from kriterion.economics.case_flows import (
    STAGED_PLATFORM_ASSUMPTION_ID_TO_PARAM,
    STAGED_PLATFORM_BENEFIT_SIDE_PARAMS,
    STAGED_PLATFORM_COST_SIDE_PARAMS,
    staged_platform_cash_flows,
)

NORTHSTAR_CASE_ID = "northstar-internal-developer-platform"
ASK_GBP = 4_000_000.0

_BASE = {
    "as-benefit-attribution-factor": (0.25, (0.05, 0.50)),
    "as-platform-adoption-rate": (0.60, (0.30, 0.85)),
    "as-friction-hours-saved-per-engineer": (90.0, (25.0, 180.0)),
    "as-fully-loaded-hourly-cost-gbp": (55.0, (45.0, 70.0)),
    "as-engineers-reached-year-1": (700.0, (300.0, 1_100.0)),
    "as-engineers-reached-year-2": (1_900.0, (900.0, 2_500.0)),
    "as-platform-team-annual-cost-gbp": (1_800_000.0, (1_200_000.0, 2_800_000.0)),
    "as-migration-cost-per-engineer-gbp": (450.0, (150.0, 900.0)),
    "as-precommitted-capital-gbp": (2_100_000.0, (600_000.0, 4_000_000.0)),
}


def _assumptions() -> dict[str, Assumption]:
    return {
        a_id: Assumption(
            id=a_id,
            created_at="2026-09-12T00:00:00Z",
            value=value,
            range=rng,
            evidence_strength=Strength.LOW,
            owner="cfo",
        )
        for a_id, (value, rng) in _BASE.items()
    }


def _flow_kwargs(**overrides):
    kwargs = {
        param: _BASE[a_id][0] for a_id, param in STAGED_PLATFORM_ASSUMPTION_ID_TO_PARAM.items()
    }
    kwargs.update(overrides)
    return kwargs


# --- the properties that make this model reusable rather than a second Case A ---


def test_every_parameter_is_required_so_no_code_constant_can_leak_into_a_case():
    """No parameter may have a default. A default is a number this module
    invented, and a case pack that forgot to declare an assumption would then
    silently publish it as its own figure."""
    sig = inspect.signature(staged_platform_cash_flows)
    defaulted = [
        name for name, p in sig.parameters.items() if p.default is not inspect.Parameter.empty
    ]
    assert defaulted == []


def test_every_parameter_is_classified_benefit_side_or_cost_side_exactly_once():
    params = set(STAGED_PLATFORM_ASSUMPTION_ID_TO_PARAM.values())
    assert STAGED_PLATFORM_BENEFIT_SIDE_PARAMS | STAGED_PLATFORM_COST_SIDE_PARAMS == params
    assert STAGED_PLATFORM_BENEFIT_SIDE_PARAMS & STAGED_PLATFORM_COST_SIDE_PARAMS == set()


def test_missing_assumption_raises_rather_than_defaulting():
    incomplete = _assumptions()
    del incomplete["as-benefit-attribution-factor"]
    with pytest.raises(KeyError, match="as-benefit-attribution-factor"):
        compute_staged_platform_economics(NORTHSTAR_CASE_ID, ASK_GBP, incomplete)


# --- the benefit chain -------------------------------------------------------


def test_zero_attribution_removes_the_entire_benefit():
    """Saved developer hours that convert to no business value are worth
    nothing in this model. If they were not, the model would be asserting that
    time saved is value created."""
    flows = staged_platform_cash_flows(
        ask_amount_gbp=ASK_GBP, **_flow_kwargs(benefit_attribution_factor=0.0)
    )
    assert all(f < 0 for f in flows)


def test_zero_adoption_removes_the_entire_benefit():
    """A platform nobody uses produces no benefit, however good it is."""
    flows = staged_platform_cash_flows(ask_amount_gbp=ASK_GBP, **_flow_kwargs(adoption_rate=0.0))
    assert all(f < 0 for f in flows)


def test_benefit_is_linear_in_attribution():
    at_10 = staged_platform_cash_flows(
        ask_amount_gbp=ASK_GBP, **_flow_kwargs(benefit_attribution_factor=0.10)
    )
    at_20 = staged_platform_cash_flows(
        ask_amount_gbp=ASK_GBP, **_flow_kwargs(benefit_attribution_factor=0.20)
    )
    at_0 = staged_platform_cash_flows(
        ask_amount_gbp=ASK_GBP, **_flow_kwargs(benefit_attribution_factor=0.0)
    )
    for period in (0, 1):
        assert at_20[period] - at_0[period] == pytest.approx(2 * (at_10[period] - at_0[period]))


# --- staging -----------------------------------------------------------------


def test_staging_changes_timing_not_total_capital():
    """Committing GBP600k before the first gate and GBP4m before it spend the
    same money. Only the discounting differs -- staging buys information, not
    money, and the model must not imply otherwise."""
    early = staged_platform_cash_flows(
        ask_amount_gbp=ASK_GBP, **_flow_kwargs(precommitted_capital_gbp=4_000_000.0)
    )
    late = staged_platform_cash_flows(
        ask_amount_gbp=ASK_GBP, **_flow_kwargs(precommitted_capital_gbp=600_000.0)
    )
    assert sum(early) == pytest.approx(sum(late))


def test_committing_more_capital_before_the_first_gate_is_cost_side():
    from kriterion.economics.engine import npv

    from kriterion.economics.case_flows import DISCOUNT_RATE

    early = npv(
        staged_platform_cash_flows(
            ask_amount_gbp=ASK_GBP, **_flow_kwargs(precommitted_capital_gbp=4_000_000.0)
        ),
        DISCOUNT_RATE,
    )
    late = npv(
        staged_platform_cash_flows(
            ask_amount_gbp=ASK_GBP, **_flow_kwargs(precommitted_capital_gbp=600_000.0)
        ),
        DISCOUNT_RATE,
    )
    assert early < late
    assert "precommitted_capital_gbp" in STAGED_PLATFORM_COST_SIDE_PARAMS


# --- what the case is for ----------------------------------------------------


def test_npv_sign_flips_inside_the_declared_ranges():
    """The decision is genuinely open on the numbers the case declares. A model
    that came out negative (or positive) across the whole range would make the
    case's central question rhetorical."""
    result = compute_staged_platform_economics(NORTHSTAR_CASE_ID, ASK_GBP, _assumptions())
    assert result.npv_low_gbp < 0 < result.npv_high_gbp


def test_attribution_dominates_the_tornado():
    """The case's load-bearing question -- does saved developer time become
    business value -- must be the quantity the valuation is most sensitive to,
    or the economics is not measuring the decision."""
    result = compute_staged_platform_economics(NORTHSTAR_CASE_ID, ASK_GBP, _assumptions())
    assert result.tornado[0].assumption_id == "benefit_attribution_factor"


def test_no_avoided_loss_band_is_reported():
    """This model prices benefits inside the NPV, so there is no separate
    avoided-loss band to report beside it. None here means 'not applicable',
    which is the same absence-not-zero discipline Case A's model follows."""
    result = compute_staged_platform_economics(NORTHSTAR_CASE_ID, ASK_GBP, _assumptions())
    assert result.avoided_loss_low_gbp is None
    assert result.avoided_loss_high_gbp is None


# --- registration ------------------------------------------------------------


def test_northstar_case_is_wired_to_the_staged_platform_model():
    assert CASE_ECONOMICS_FUNCTIONS[NORTHSTAR_CASE_ID] is compute_staged_platform_economics


def test_every_tornado_parameter_resolves_to_the_case_packs_own_assumption():
    """Without a complete map the page names raw engine parameters instead of
    the pack's ranged assumptions, and the dominant-uncertainty line -- the most
    decision-relevant sentence on this case's page -- loses its evidence
    strength and owner."""
    from kriterion.decision_state import _PARAM_TO_ASSUMPTION_ID

    result = compute_staged_platform_economics(NORTHSTAR_CASE_ID, ASK_GBP, _assumptions())
    mapping = _PARAM_TO_ASSUMPTION_ID[NORTHSTAR_CASE_ID]
    assert {e.assumption_id for e in result.tornado} <= set(mapping)
    assert set(mapping.values()) == set(STAGED_PLATFORM_ASSUMPTION_ID_TO_PARAM)
