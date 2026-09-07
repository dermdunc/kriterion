"""Case A (coding-agent-rollout) cash-flow construction.

This is deliberately separate from engine.py: engine.py is generic and
golden-tested against clean synthetic numbers; this module encodes Case A's
own business narrative (stage budgets, headcount ramp, benefit model) using
named, documented constants, and is the only place that narrative lives.

V0 simplifications, stated rather than hidden:
  - Two annual periods (matching the ask's 24-month duration), not monthly.
  - Each period's headcount is treated as active for the full period — no
    mid-year ramp/interpolation.
  - Benefit = active_engineers x fully_loaded_cost x uplift x
    attribution_factor. The attribution_factor exists specifically because
    ev-024 in the case pack states no agreed benefits-attribution
    methodology exists; naive full-salary-equivalent monetisation of a
    productivity percentage would be exactly the "secretly an ROI
    calculator" failure mode docs/v0-plan.md Section 8 warns against.
  - Training cost is charged once per newly-onboarded engineer in the year
    they onboard, additional to the staged capital ask (the ask funds the
    programme/tooling; onboarding labour cost is a separate assumption,
    ev-020).
"""

from __future__ import annotations

from kriterion.domain.economics import EconomicsResult
from kriterion.domain.evidence import Assumption
from kriterion.economics.engine import npv, payback_period, peak_funding, tornado_ranking

DISCOUNT_RATE = 0.10  # Not evidenced in the case pack -- a standard corporate hurdle-rate default.

YEAR_1_ENGINEERS = 1_200  # targeted_role_rollout stage headcount, matching ev-017's forecast.
YEAR_2_ENGINEERS = 5_000  # enterprise_rollout stage headcount, matching the ask's stated target.

# Staged ask, docs/v0-plan.md Section 8: discovery -> pilot -> targeted_scale -> enterprise.
DISCOVERY_GBP = 50_000
PILOT_GBP = 420_000
TARGETED_SCALE_GBP = 1_600_000


def case_a_cash_flows(
    *,
    ask_amount_gbp: float,
    uplift: float = 0.18,
    fully_loaded_cost_gbp: float = 120_000,
    attribution_factor: float = 0.10,
    training_cost_per_engineer_gbp: float = 340,
    annual_support_cost_gbp: float = 1_350_000,
) -> list[float]:
    """Two-period (Year 1, Year 2) net cash flow for Case A, in GBP.

    Keyword-only so kriterion.economics.engine.tornado_ranking can call this
    with a single overridden assumption at a time while every other
    parameter keeps its base-case default.
    """
    year_1_capex = DISCOVERY_GBP + PILOT_GBP + TARGETED_SCALE_GBP
    year_2_capex = ask_amount_gbp - year_1_capex

    year_1_training = YEAR_1_ENGINEERS * training_cost_per_engineer_gbp
    year_2_training = (YEAR_2_ENGINEERS - YEAR_1_ENGINEERS) * training_cost_per_engineer_gbp

    def benefit(active_engineers: int) -> float:
        return active_engineers * fully_loaded_cost_gbp * uplift * attribution_factor

    year_1_net = benefit(YEAR_1_ENGINEERS) - year_1_capex - year_1_training
    year_2_net = (
        benefit(YEAR_2_ENGINEERS) - year_2_capex - year_2_training - annual_support_cost_gbp
    )

    return [year_1_net, year_2_net]


# Maps case.toml assumption ids to case_a_cash_flows' keyword parameter names.
ASSUMPTION_ID_TO_PARAM = {
    "as-productivity-uplift": "uplift",
    "as-fully-loaded-cost-gbp": "fully_loaded_cost_gbp",
    "as-benefit-attribution-factor": "attribution_factor",
    "as-training-cost-per-engineer-gbp": "training_cost_per_engineer_gbp",
    "as-annual-support-cost-gbp": "annual_support_cost_gbp",
}

# Whether a higher value of the parameter makes the case MORE favourable
# (benefit-side) or LESS favourable (cost-side) -- used to build the
# pessimistic/optimistic npv_triple bounds. Every parameter in
# ASSUMPTION_ID_TO_PARAM's values must appear in exactly one of these sets.
BENEFIT_SIDE_PARAMS = {"uplift", "fully_loaded_cost_gbp", "attribution_factor"}
COST_SIDE_PARAMS = {"training_cost_per_engineer_gbp", "annual_support_cost_gbp"}


def compute_economics(
    case_id: str, ask_amount_gbp: float, assumptions_by_id: dict[str, Assumption]
) -> EconomicsResult:
    """The single entry point tying case_flows + engine together for Case A.

    Builds base/pessimistic/optimistic cash flows from the case pack's own
    assumption ranges (not hardcoded numbers), then calls the generic engine
    for NPV/payback/peak-funding/tornado.
    """
    base_kwargs = {
        param: assumptions_by_id[a_id].value for a_id, param in ASSUMPTION_ID_TO_PARAM.items()
    }

    pessimistic_kwargs = {}
    optimistic_kwargs = {}
    for a_id, param in ASSUMPTION_ID_TO_PARAM.items():
        lo, hi = assumptions_by_id[a_id].range
        if param in BENEFIT_SIDE_PARAMS:
            pessimistic_kwargs[param] = lo
            optimistic_kwargs[param] = hi
        else:
            pessimistic_kwargs[param] = hi  # higher cost = worse
            optimistic_kwargs[param] = lo

    base_flows = case_a_cash_flows(ask_amount_gbp=ask_amount_gbp, **base_kwargs)
    low_flows = case_a_cash_flows(ask_amount_gbp=ask_amount_gbp, **pessimistic_kwargs)
    high_flows = case_a_cash_flows(ask_amount_gbp=ask_amount_gbp, **optimistic_kwargs)

    assumption_ranges = {
        param: assumptions_by_id[a_id].range for a_id, param in ASSUMPTION_ID_TO_PARAM.items()
    }

    def flows_fn(**overrides):
        kwargs = dict(base_kwargs)
        kwargs.update(overrides)
        return case_a_cash_flows(ask_amount_gbp=ask_amount_gbp, **kwargs)

    return EconomicsResult(
        id=f"{case_id}-economics",
        created_at=assumptions_by_id[next(iter(assumptions_by_id))].created_at,
        case_id=case_id,
        discount_rate=DISCOUNT_RATE,
        npv_low_gbp=npv(low_flows, DISCOUNT_RATE),
        npv_mid_gbp=npv(base_flows, DISCOUNT_RATE),
        npv_high_gbp=npv(high_flows, DISCOUNT_RATE),
        payback_years=payback_period(base_flows),
        peak_funding_gbp=peak_funding(base_flows),
        tornado=tornado_ranking(flows_fn, assumption_ranges, DISCOUNT_RATE),
    )


def case_c_cash_flows(*, ask_amount_gbp: float, ongoing_annual_cost_gbp: float = 480_000) -> list[float]:
    """Case C (invisible-ai-control-plane): NPV is negative in every
    scenario BY CONSTRUCTION. Only costs are summed here -- the avoided-loss
    FORECAST (as-avoided-loss-band-gbp) is deliberately never added as a
    benefit inflow, matching docs/v0-plan.md Section 8's trap: "the
    avoided-loss FORECAST must never enter NPV as a point value." It is
    reported separately by compute_case_c_economics, alongside the NPV
    table, never inside it.

    Two annual periods, matching the 18-month ask rounded to a 2-year
    evaluation horizon (year 1: full build cost; year 2: first year of
    ongoing run cost) -- the same V0 simplification Case A uses.
    """
    year_1 = -ask_amount_gbp
    year_2 = -ongoing_annual_cost_gbp
    return [year_1, year_2]


def compute_case_c_economics(
    case_id: str, ask_amount_gbp: float, assumptions_by_id: dict[str, Assumption]
) -> EconomicsResult:
    ongoing = assumptions_by_id["as-ongoing-annual-cost-gbp"]
    avoided_loss = assumptions_by_id["as-avoided-loss-band-gbp"]

    base_flows = case_c_cash_flows(ask_amount_gbp=ask_amount_gbp, ongoing_annual_cost_gbp=ongoing.value)
    low_cost, high_cost = ongoing.range
    # Pessimistic scenario = higher ongoing cost (cost-side: higher is worse).
    pessimistic_flows = case_c_cash_flows(ask_amount_gbp=ask_amount_gbp, ongoing_annual_cost_gbp=high_cost)
    optimistic_flows = case_c_cash_flows(ask_amount_gbp=ask_amount_gbp, ongoing_annual_cost_gbp=low_cost)

    def flows_fn(**overrides):
        kwargs = {"ongoing_annual_cost_gbp": ongoing.value}
        kwargs.update(overrides)
        return case_c_cash_flows(ask_amount_gbp=ask_amount_gbp, **kwargs)

    tornado = tornado_ranking(flows_fn, {"ongoing_annual_cost_gbp": (low_cost, high_cost)}, DISCOUNT_RATE)

    return EconomicsResult(
        id=f"{case_id}-economics",
        created_at=ongoing.created_at,
        case_id=case_id,
        discount_rate=DISCOUNT_RATE,
        npv_low_gbp=npv(pessimistic_flows, DISCOUNT_RATE),
        npv_mid_gbp=npv(base_flows, DISCOUNT_RATE),
        npv_high_gbp=npv(optimistic_flows, DISCOUNT_RATE),
        payback_years=payback_period(base_flows),  # always None -- no positive inflow, ever
        peak_funding_gbp=peak_funding(base_flows),
        tornado=tornado,
        avoided_loss_low_gbp=avoided_loss.range[0],
        avoided_loss_high_gbp=avoided_loss.range[1],
    )
