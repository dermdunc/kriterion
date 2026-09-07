"""Executor port + adapters. hekton_llm is imported only within this
package (docs/v0-plan.md Section 9, non-negotiable invariant 6) — see
tests/executors/test_boundary.py for the mechanical check.
"""

from kriterion.executors.base import Executor, ExecutorError, ExecutorResult

__all__ = ["Executor", "ExecutorError", "ExecutorResult"]
