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


def _compute_ranged_economics(
    *,
    case_id: str,
    ask_amount_gbp: float,
    assumptions_by_id: dict[str, Assumption],
    cash_flows_fn,
    assumption_id_to_param: dict[str, str],
    benefit_side_params: set[str],
) -> EconomicsResult:
    """Shared construction for any case whose cash-flow model is driven
    entirely by ranged case-pack assumptions.

    Builds base/pessimistic/optimistic cash flows from the case pack's own
    assumption ranges (not hardcoded numbers), then calls the generic engine
    for NPV/payback/peak-funding/tornado.

    A parameter not in `benefit_side_params` is treated as cost-side, so its
    high bound is the pessimistic scenario. Every parameter must therefore be
    classified deliberately by the caller; a silent default would put an
    unclassified parameter on the wrong side of the band.
    """
    base_kwargs = {
        param: assumptions_by_id[a_id].value for a_id, param in assumption_id_to_param.items()
    }

    pessimistic_kwargs = {}
    optimistic_kwargs = {}
    for a_id, param in assumption_id_to_param.items():
        lo, hi = assumptions_by_id[a_id].range
        if param in benefit_side_params:
            pessimistic_kwargs[param] = lo
            optimistic_kwargs[param] = hi
        else:
            pessimistic_kwargs[param] = hi  # higher cost = worse
            optimistic_kwargs[param] = lo

    base_flows = cash_flows_fn(ask_amount_gbp=ask_amount_gbp, **base_kwargs)
    low_flows = cash_flows_fn(ask_amount_gbp=ask_amount_gbp, **pessimistic_kwargs)
    high_flows = cash_flows_fn(ask_amount_gbp=ask_amount_gbp, **optimistic_kwargs)

    assumption_ranges = {
        param: assumptions_by_id[a_id].range for a_id, param in assumption_id_to_param.items()
    }

    def flows_fn(**overrides):
        kwargs = dict(base_kwargs)
        kwargs.update(overrides)
        return cash_flows_fn(ask_amount_gbp=ask_amount_gbp, **kwargs)

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


def compute_economics(
    case_id: str, ask_amount_gbp: float, assumptions_by_id: dict[str, Assumption]
) -> EconomicsResult:
    """The single entry point tying case_flows + engine together for Case A."""
    return _compute_ranged_economics(
        case_id=case_id,
        ask_amount_gbp=ask_amount_gbp,
        assumptions_by_id=assumptions_by_id,
        cash_flows_fn=case_a_cash_flows,
        assumption_id_to_param=ASSUMPTION_ID_TO_PARAM,
        benefit_side_params=BENEFIT_SIDE_PARAMS,
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


def compute_cost_only_economics(
    case_id: str, ask_amount_gbp: float, assumptions_by_id: dict[str, Assumption]
) -> EconomicsResult:
    """Cost-only economics for any case whose benefit side cannot be priced.

    Same construction as Case C -- only costs are summed, so NPV is negative in
    every scenario and `payback_years` is always None -- with one difference:
    `as-avoided-loss-band-gbp` is OPTIONAL here.

    That option exists because a real decision can be worse-evidenced than a
    fixture. Case C at least has a risk-modelled avoided-loss band to report
    alongside (never inside) the NPV table. A case whose every benefit driver
    is an UNKNOWN cannot honestly state even a band, and the only faithful
    representation is to carry no benefit figure at all: `avoided_loss_*` stay
    None, and every view must then say the benefit side is unquantified rather
    than render a zero. Inventing a band to fill the field would be exactly the
    fabrication the evidence taxonomy exists to prevent.

    The cash-flow shape is `case_c_cash_flows` -- that function is not in fact
    Case-C-specific, only its name is historical.
    """
    ongoing = assumptions_by_id["as-ongoing-annual-cost-gbp"]
    avoided_loss = assumptions_by_id.get("as-avoided-loss-band-gbp")

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
        avoided_loss_low_gbp=avoided_loss.range[0] if avoided_loss is not None else None,
        avoided_loss_high_gbp=avoided_loss.range[1] if avoided_loss is not None else None,
    )


def compute_case_c_economics(
    case_id: str, ask_amount_gbp: float, assumptions_by_id: dict[str, Assumption]
) -> EconomicsResult:
    """Case C (invisible-ai-control-plane). Cost-only, plus the avoided-loss
    band Case C does declare -- required here rather than optional, because
    Case C's whole point is that rejecting on NPV alone while an avoided-loss
    band sits beside it is the failure mode."""
    if "as-avoided-loss-band-gbp" not in assumptions_by_id:
        raise KeyError(
            "as-avoided-loss-band-gbp is required for Case C's economics "
            "(use compute_cost_only_economics for a case with no benefit band)"
        )
    return compute_cost_only_economics(case_id, ask_amount_gbp, assumptions_by_id)


# --- Staged, adoption-limited platform investment ---------------------------
#
# A third cash-flow shape, for a case that stages capital behind evidence gates
# and whose benefit reaches only the engineers who actually adopt the thing.
# It holds NO case-specific constant: every quantity below arrives from the
# calling case pack's own ranged assumptions. That is deliberate, and it is the
# difference between this and `case_a_cash_flows`, which bakes Case A's
# headcount ramp and stage budgets into module constants. A second case reusing
# Case A's function would silently inherit Case A's 1,200/5,000 engineer ramp
# and its GBP2.07m stage ladder, and the generated page would then state those
# numbers as if they were the case's own.

STAGED_PLATFORM_ASSUMPTION_ID_TO_PARAM = {
    "as-platform-adoption-rate": "adoption_rate",
    "as-benefit-attribution-factor": "benefit_attribution_factor",
    "as-friction-hours-saved-per-engineer": "friction_hours_saved_per_engineer_per_year",
    "as-fully-loaded-hourly-cost-gbp": "fully_loaded_hourly_cost_gbp",
    "as-engineers-reached-year-1": "engineers_reached_year_1",
    "as-engineers-reached-year-2": "engineers_reached_year_2",
    "as-platform-team-annual-cost-gbp": "platform_team_annual_cost_gbp",
    "as-migration-cost-per-engineer-gbp": "migration_cost_per_engineer_gbp",
    "as-precommitted-capital-gbp": "precommitted_capital_gbp",
}

# Higher value = more favourable. `engineers_reached_*` sit here because a
# wider rollout raises benefit faster than it raises migration cost at every
# point in the declared ranges; `precommitted_capital_gbp` is cost-side
# because committing more of the envelope before the first evidence gate
# discounts worse, never better.
STAGED_PLATFORM_BENEFIT_SIDE_PARAMS = {
    "adoption_rate",
    "benefit_attribution_factor",
    "friction_hours_saved_per_engineer_per_year",
    "fully_loaded_hourly_cost_gbp",
    "engineers_reached_year_1",
    "engineers_reached_year_2",
}
STAGED_PLATFORM_COST_SIDE_PARAMS = {
    "platform_team_annual_cost_gbp",
    "migration_cost_per_engineer_gbp",
    "precommitted_capital_gbp",
}


def staged_platform_cash_flows(
    *,
    ask_amount_gbp: float,
    precommitted_capital_gbp: float,
    engineers_reached_year_1: float,
    engineers_reached_year_2: float,
    adoption_rate: float,
    friction_hours_saved_per_engineer_per_year: float,
    fully_loaded_hourly_cost_gbp: float,
    benefit_attribution_factor: float,
    platform_team_annual_cost_gbp: float,
    migration_cost_per_engineer_gbp: float,
) -> list[float]:
    """Two-period (Year 1, Year 2) net cash flow, in GBP, for a staged platform
    investment whose benefit is limited by adoption and by attribution.

    Every parameter is required and keyword-only: there is no default, so a
    case pack that fails to declare an assumption raises rather than silently
    inheriting a number this module invented.

    The benefit chain is deliberately explicit, because each link is a separate
    place the benefit can fail to materialise:

        engineers reached
          x adoption_rate                 -- teams can bypass the platform
          x hours saved per engineer      -- the friction actually removed
          x fully-loaded hourly cost      -- what an engineer-hour costs
          x benefit_attribution_factor    -- the share of saved time that
                                             becomes business value rather
                                             than being absorbed elsewhere

    `benefit_attribution_factor` exists for the same reason Case A's does:
    monetising a productivity saving at full salary equivalence would assert
    that every recovered engineer-hour converts into delivered value, which is
    the "secretly an ROI calculator" failure mode. Here it additionally carries
    the case's own central question, so it is expected to dominate the tornado.

    Simplifications, stated rather than hidden, matching the two existing
    models in this module:
      - Two annual periods, not monthly, and no mid-year ramp: each period's
        reached population is treated as active for the whole period.
      - Capital is split across the two periods by `precommitted_capital_gbp`,
        i.e. how much of the envelope is committed before the first evidence
        gate. Total capital is `ask_amount_gbp` either way, so this parameter
        changes NPV only through discounting. That is the honest result:
        staging buys information, not money.
      - `platform_team_annual_cost_gbp` is charged in year 2 only -- the first
        full year of steady-state run cost after the build period, the same
        treatment `case_a_cash_flows` gives its annual support cost.
      - Migration cost is charged once per newly-reached engineer in the period
        they are reached.
    """
    year_1_capital = min(precommitted_capital_gbp, ask_amount_gbp)
    year_2_capital = ask_amount_gbp - year_1_capital

    def benefit(engineers_reached: float) -> float:
        active = engineers_reached * adoption_rate
        return (
            active
            * friction_hours_saved_per_engineer_per_year
            * fully_loaded_hourly_cost_gbp
            * benefit_attribution_factor
        )

    year_1_migration = engineers_reached_year_1 * migration_cost_per_engineer_gbp
    newly_reached_year_2 = max(engineers_reached_year_2 - engineers_reached_year_1, 0.0)
    year_2_migration = newly_reached_year_2 * migration_cost_per_engineer_gbp

    year_1_net = benefit(engineers_reached_year_1) - year_1_capital - year_1_migration
    year_2_net = (
        benefit(engineers_reached_year_2)
        - year_2_capital
        - year_2_migration
        - platform_team_annual_cost_gbp
    )

    return [year_1_net, year_2_net]


def compute_staged_platform_economics(
    case_id: str, ask_amount_gbp: float, assumptions_by_id: dict[str, Assumption]
) -> EconomicsResult:
    """Economics for a staged, adoption-limited platform investment.

    Unlike `compute_cost_only_economics`, this one does model a benefit side --
    legitimately, because it is only used by a case whose benefit drivers are
    declared as ranged assumptions the case pack owns and labels, not as
    observations it does not have. A case whose benefit drivers are all
    `UNKNOWN` must still use the cost-only model; the two are not
    interchangeable.
    """
    return _compute_ranged_economics(
        case_id=case_id,
        ask_amount_gbp=ask_amount_gbp,
        assumptions_by_id=assumptions_by_id,
        cash_flows_fn=staged_platform_cash_flows,
        assumption_id_to_param=STAGED_PLATFORM_ASSUMPTION_ID_TO_PARAM,
        benefit_side_params=STAGED_PLATFORM_BENEFIT_SIDE_PARAMS,
    )
