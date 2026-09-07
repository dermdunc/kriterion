"""Deterministic economics calculations (ADR-002).

Pure functions only: no I/O, no model calls, no fallback on error. Every
function here operates on plain cash-flow numbers so it can be golden-tested
independently of any particular case's business narrative — case-specific
cash-flow construction (headcount ramps, stage budgets, etc.) lives in
kriterion.economics.case_flows, which calls into this module rather than the
reverse.
"""

from __future__ import annotations

from kriterion.domain.economics import TornadoEntry


def npv(cash_flows: list[float], rate: float) -> float:
    """Net present value of cash_flows[0], cash_flows[1], ... discounted
    at `rate` per period, with cash_flows[0] treated as occurring at the end
    of period 1 (there is no separate period-0 upfront outflow — a case's
    own cash_flows list should include period 1 onward only)."""
    return sum(cf / (1.0 + rate) ** (t + 1) for t, cf in enumerate(cash_flows))


def payback_period(cash_flows: list[float]) -> float | None:
    """Fractional period at which cumulative cash flow first reaches zero,
    linearly interpolated within the period it crosses in. None if the
    cumulative flow never reaches zero within the given horizon."""
    cumulative = 0.0
    for t, cf in enumerate(cash_flows):
        prev_cumulative = cumulative
        cumulative += cf
        if cumulative >= 0 and prev_cumulative < 0:
            # Crossed zero during period t+1 (1-indexed for a human-readable "year").
            fraction = -prev_cumulative / cf if cf != 0 else 0.0
            return t + fraction
        if cumulative >= 0 and prev_cumulative >= 0 and t == 0:
            # Already non-negative from period 1 itself.
            return 0.0
    return None


def peak_funding(cash_flows: list[float]) -> float:
    """The largest capital outlay at risk before the case turns cash-flow
    positive: the most negative point of the cumulative cash-flow curve,
    reported as a positive GBP figure (0 if the curve never goes negative)."""
    cumulative = 0.0
    trough = 0.0
    for cf in cash_flows:
        cumulative += cf
        trough = min(trough, cumulative)
    return abs(trough)  # trough is always <= 0 by construction; abs() avoids a -0.0 result


def tornado_ranking(
    base_case_flows_fn,
    assumption_ranges: dict[str, tuple[float, float]],
    rate: float,
) -> list[TornadoEntry]:
    """One-at-a-time sensitivity: for each assumption, hold every other
    assumption at its base value and recompute NPV at that assumption's low
    and high bound. Ranked by descending |swing|.

    `base_case_flows_fn(**overrides) -> list[float]` must accept the same
    keyword names as `assumption_ranges`' keys and return that scenario's
    cash-flow list.
    """
    entries: list[TornadoEntry] = []
    for name, (low, high) in assumption_ranges.items():
        npv_low = npv(base_case_flows_fn(**{name: low}), rate)
        npv_high = npv(base_case_flows_fn(**{name: high}), rate)
        swing = npv_high - npv_low
        entries.append(TornadoEntry(assumption_id=name, npv_swing_gbp=swing))
    entries.sort(key=lambda e: abs(e.npv_swing_gbp), reverse=True)
    return entries
