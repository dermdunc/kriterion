"""Replays previously-recorded executor outputs from a run directory —
lets protocol/eval code run against a fixed, already-observed transcript
without live Ollama (CI, regression tests, deterministic re-scoring).

Recording format: a JSON list of {"prompt", "text", "elapsed_seconds",
"model", "seed"} objects, in call order, written by whatever produced the
original run (HektonLocalExecutor does not write this itself in V0 — a
recorder wrapper is a natural task-8/task-10 addition once real protocol
runs exist to record).
"""

from __future__ import annotations

import json
from pathlib import Path

from kriterion.executors.base import Executor, ExecutorError, ExecutorResult


class ReplayExecutor(Executor):
    def __init__(self, recording_path: Path) -> None:
        if not recording_path.is_file():
            raise ExecutorError(f"no recording found at {recording_path}")
        self._calls: list[dict] = json.loads(recording_path.read_text())
        self._index = 0

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        fmt: str | None = "json",
        seed: int | None = 0,
    ) -> ExecutorResult:
        if self._index >= len(self._calls):
            raise ExecutorError(
                f"replay tape exhausted after {self._index} calls — the caller made more "
                "completions than were recorded"
            )
        entry = self._calls[self._index]
        if entry["prompt"] != prompt:
            raise ExecutorError(
                f"replay divergence at call {self._index}: recorded prompt does not match "
                "the prompt requested now — the protocol/prompt logic has drifted since "
                "this recording was made"
            )
        self._index += 1
        return ExecutorResult(
            text=entry["text"],
            elapsed_seconds=entry["elapsed_seconds"],
            model=entry["model"],
            seed=entry.get("seed"),
        )
