"""Deterministic economics (ADR-002). engine.py is generic and pure;
case_flows.py encodes each case's specific business narrative."""

from kriterion.economics.case_flows import (
    compute_case_c_economics,
    compute_cost_only_economics,
    compute_economics,
)
from kriterion.economics.engine import npv, payback_period, peak_funding, tornado_ranking

# Dispatch by case id -- each case's economics function needs different
# assumption ids, so there is no single generic call shape across cases.
#
# international-platform-engineering is the Human Run 001 case (see
# docs/planning/human-run-001/). Its case pack deliberately lives outside this
# repository. It uses the generic cost-only model because every benefit-side
# driver of that decision is an UNKNOWN in its ledger: the cost of the
# capability is the only quantity the case can honestly vary.
CASE_ECONOMICS_FUNCTIONS = {
    "coding-agent-rollout": compute_economics,
    "invisible-ai-control-plane": compute_case_c_economics,
    "international-platform-engineering": compute_cost_only_economics,
}

__all__ = [
    "CASE_ECONOMICS_FUNCTIONS",
    "compute_case_c_economics",
    "compute_cost_only_economics",
    "compute_economics",
    "npv",
    "payback_period",
    "peak_funding",
    "tornado_ranking",
]
