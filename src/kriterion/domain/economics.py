"""Scenario, CashFlowTable, EconomicsResult (docs/v0-plan.md Section 4 and
Section 9's module layout). CashFlowTable/EconomicsResult were deferred at
task 2 pending task 5-6 actually needing their shape; defined now.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from kriterion.domain.base import KriterionRecord


@dataclass(kw_only=True)
class ScenarioOutputs:
    """Written only by the economics engine (task 5-6), never asserted elsewhere."""

    npv_triple: tuple[float, float, float] | None = None  # (low, mid, high)
    payback: float | None = None
    peak_funding: float | None = None


@dataclass(kw_only=True)
class Scenario(KriterionRecord):
    assumption_overrides: dict[str, float] = field(default_factory=dict)
    outputs: ScenarioOutputs = field(default_factory=ScenarioOutputs)


@dataclass(kw_only=True)
class CashFlowTable:
    """Net cash flow per period (period 0, 1, 2, ...), in GBP. Pure data —
    how periods map to calendar time is the caller's concern, not this
    table's."""

    periods: list[float]


@dataclass(kw_only=True)
class TornadoEntry:
    assumption_id: str
    npv_swing_gbp: float  # abs(NPV at assumption's high) - abs... see engine.tornado_ranking


@dataclass(kw_only=True)
class EconomicsResult(KriterionRecord):
    """Output of economics/engine.py for one case + one assumption set.
    ADR-002: written only by the engine, never asserted by a model."""

    case_id: str
    discount_rate: float
    npv_low_gbp: float
    npv_mid_gbp: float
    npv_high_gbp: float
    payback_years: float | None
    peak_funding_gbp: float
    tornado: list[TornadoEntry]
    # Case C only: an avoided-loss FORECAST band, reported ALONGSIDE the NPV
    # table but never summed into it (docs/v0-plan.md Section 8's trap: "the
    # avoided-loss FORECAST must never enter NPV as a point value"). None
    # for cases with no such non-financial-value band (e.g. Case A).
    avoided_loss_low_gbp: float | None = None
    avoided_loss_high_gbp: float | None = None
