"""Deterministic economics (ADR-002). engine.py is generic and pure;
case_flows.py encodes each case's specific business narrative."""

from kriterion.economics.case_flows import compute_case_c_economics, compute_economics
from kriterion.economics.engine import npv, payback_period, peak_funding, tornado_ranking

# Dispatch by case id -- each case's economics function needs different
# assumption ids, so there is no single generic call shape across cases.
CASE_ECONOMICS_FUNCTIONS = {
    "coding-agent-rollout": compute_economics,
    "invisible-ai-control-plane": compute_case_c_economics,
}

__all__ = [
    "CASE_ECONOMICS_FUNCTIONS",
    "compute_case_c_economics",
    "compute_economics",
    "npv",
    "payback_period",
    "peak_funding",
    "tornado_ranking",
]
