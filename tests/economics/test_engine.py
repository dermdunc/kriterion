"""P0-01/P0-02 golden tests for the generic engine (docs/v0-plan.md Section
7's eval matrix). Uses clean, trivially hand-verifiable numbers -- Case A's
own business-narrative numbers are checked separately in
tests/economics/test_case_flows.py, since pinning a multi-million-pound
figure here would make this test's own correctness harder to eyeball.
"""

from kriterion.economics.engine import npv, payback_period, peak_funding, tornado_ranking


def test_npv_matches_hand_computation():
    # -1000 upfront (period 1), then 400/period for periods 2 and 3, at 10%.
    # NPV = -1000/1.1 + 400/1.1^2 + 400/1.1^3
    cash_flows = [-1000.0, 400.0, 400.0]
    expected = -1000 / 1.1 + 400 / 1.1**2 + 400 / 1.1**3
    assert abs(npv(cash_flows, 0.10) - expected) < 1e-6


def test_npv_zero_rate_is_plain_sum():
    assert npv([100.0, 200.0, 300.0], 0.0) == 600.0


def test_payback_period_interpolates_within_crossing_period():
    # Cumulative after each period: -1000, -600, -200, +200 -> still
    # negative after 3 periods, crosses zero during period 4 (index 3),
    # 200/400 = 0.5 of the way through it -> payback = 3.5
    cash_flows = [-1000.0, 400.0, 400.0, 400.0]
    assert payback_period(cash_flows) == 3.5


def test_payback_period_none_if_never_recovered():
    assert payback_period([-1000.0, 100.0, 100.0]) is None


def test_payback_period_zero_if_first_period_already_nonnegative():
    assert payback_period([100.0, 100.0]) == 0.0


def test_peak_funding_is_the_deepest_trough():
    # Cumulative: -1000, -1400, -1000, -400, 200 -> trough is -1400 at period 2
    cash_flows = [-1000.0, -400.0, 400.0, 600.0, 600.0]
    assert peak_funding(cash_flows) == 1400.0


def test_peak_funding_zero_if_never_negative():
    assert peak_funding([100.0, 100.0]) == 0.0


def test_tornado_ranking_orders_by_absolute_npv_swing():
    # Three assumptions with deliberately different, known swing magnitudes:
    # 'big' should swing NPV the most, 'small' the least.
    def flows_fn(big=1.0, medium=1.0, small=1.0):
        return [100.0 * big + 10.0 * medium + 1.0 * small]

    ranking = tornado_ranking(
        flows_fn,
        {"big": (0.0, 100.0), "medium": (0.0, 100.0), "small": (0.0, 100.0)},
        rate=0.0,
    )
    assert [entry.assumption_id for entry in ranking] == ["big", "medium", "small"]
    # big: flows_fn(big=0)=0+10+1=11 vs flows_fn(big=100)=10000+10+1=10011 -> swing 10000
    assert ranking[0].npv_swing_gbp == 10_000.0
