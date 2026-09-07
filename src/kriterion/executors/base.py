"""The Executor port. Deliberately imports nothing from hekton_llm — see
docs/v0-plan.md Section 9's non-negotiable invariant 6: hekton_llm is
imported only inside kriterion.executors' concrete adapters
(hekton_local.py), never here and never outside this package.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass


class ExecutorError(RuntimeError):
    """Raised when an executor cannot produce a completion at all — a
    connectivity failure, an exhausted replay tape, etc. Distinct from the
    model returning a bad-but-present completion, which callers handle
    themselves (retry-then-abstained_error, per docs/v0-plan.md Section 5)."""


@dataclass(kw_only=True)
class ExecutorResult:
    text: str
    elapsed_seconds: float
    model: str
    seed: int | None


class Executor(abc.ABC):
    """Every deliberation-protocol phase calls an Executor, never a
    provider client directly — this is what lets Baseline A, the committee,
    and eval replay all share one call shape."""

    @abc.abstractmethod
    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        fmt: str | None = "json",
        seed: int | None = 0,
    ) -> ExecutorResult:
        """Determinism policy (docs/v0-plan.md Section 5): implementations
        must use fmt="json", temperature=0, and the given fixed seed."""
