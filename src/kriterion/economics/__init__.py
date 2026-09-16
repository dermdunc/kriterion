"""Deterministic economics (ADR-002). engine.py is generic and pure;
case_flows.py encodes each case's specific business narrative."""

from kriterion.economics.case_flows import (
    compute_case_c_economics,
    compute_cost_only_economics,
    compute_economics,
    compute_staged_platform_economics,
)
from kriterion.economics.engine import npv, payback_period, peak_funding, tornado_ranking

# Dispatch by case id -- each case's economics function needs different
# assumption ids, so there is no single generic call shape across cases.
#
# northstar-internal-developer-platform is the Human Run 001 case (see
# docs/planning/human-run-001/). It uses the staged-platform model because its
# benefit drivers -- adoption, hours saved per engineer, and the share of saved
# time that converts to business value -- are declared as ranged assumptions the
# case pack owns and labels as synthetic scenario inputs, so they can honestly
# be varied. That is precisely the condition compute_cost_only_economics exists
# for the absence of: a case whose benefit drivers are all UNKNOWN must use the
# cost-only model instead, and the two are not interchangeable.
CASE_ECONOMICS_FUNCTIONS = {
    "coding-agent-rollout": compute_economics,
    "invisible-ai-control-plane": compute_case_c_economics,
    "northstar-internal-developer-platform": compute_staged_platform_economics,
}

__all__ = [
    "CASE_ECONOMICS_FUNCTIONS",
    "compute_case_c_economics",
    "compute_cost_only_economics",
    "compute_economics",
    "compute_staged_platform_economics",
    "npv",
    "payback_period",
    "peak_funding",
    "tornado_ranking",
]
