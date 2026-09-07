"""hekton_llm.OllamaClient adapter — the only concrete, live executor in V0.

Bound to the source signature (verified 2026-09-05, not the interface doc,
which is stale): OllamaClient.generate(model, prompt, system=None, fmt=None,
options=None) -> TimedResult, at
platform/hekton-local-llm/src/hekton_llm/ollama_client.py:34. Depend on the
hekton_llm import namespace only, never the distribution name (still
local-llm-lab v0.2.0).
"""

from __future__ import annotations

from hekton_llm.ollama_client import OllamaClient, OllamaConnectionError

from kriterion.domain.enums import CommitteeSeat
from kriterion.executors.base import Executor, ExecutorError, ExecutorResult

DEFAULT_MODEL = "qwen2.5:14b-instruct"

# Treatment D (docs/v0-plan.md Section 6, deferred from the critical path,
# "runs if the critical path finishes early" -- it did): "5 independent,
# full [protocol], heterogeneous per role" is the entire spec given: which
# model goes to which seat is not specified anywhere. A judgment call,
# stated rather than left implicit: five distinct model families/sizes
# from the 9 real generation models installed on this machine (verified via
# `ollama list`, not the plan's own possibly-stale names), chosen for
# maximum heterogeneity, not because any model is meaningfully better
# suited to a given role -- no such fine-tuned model exists in this set, so
# claiming otherwise would be dishonest. CFO keeps the baseline default
# (Qwen 14B) specifically as an anchor back to Conditions A/B/C.
TREATMENT_D_MODEL_BY_SEAT: dict[CommitteeSeat, str] = {
    CommitteeSeat.CFO: "qwen2.5:14b-instruct",
    CommitteeSeat.CTO: "devstral-small-2:24b",
    CommitteeSeat.CISO: "mistral:7b",
    CommitteeSeat.CRO_COMPLIANCE: "gemma4:12b",
    CommitteeSeat.BUSINESS_EXECUTIVE: "llama3.2:3b",
}

# OllamaClient's own default (120s) proved too tight live: 3/5 seeds of a
# real Baseline A batch run hit a raw TimeoutError on a long free-text
# case_against/premortem generation at 14B scale on this hardware (see
# docs/decisions.md). Applied here, not in OllamaClient itself -- that's
# platform code (ADR-001: Hekton -> Kriterion only, never the reverse).
DEFAULT_TIMEOUT_SECONDS = 300


class HektonLocalExecutor(Executor):
    def __init__(self, model: str = DEFAULT_MODEL, client: OllamaClient | None = None) -> None:
        self.model = model
        self._client = client or OllamaClient(timeout=DEFAULT_TIMEOUT_SECONDS)

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        fmt: str | None = "json",
        seed: int | None = 0,
    ) -> ExecutorResult:
        options: dict = {"temperature": 0}
        if seed is not None:
            options["seed"] = seed

        try:
            result = self._client.generate(self.model, prompt, system=system, fmt=fmt, options=options)
        except OllamaConnectionError as exc:
            raise ExecutorError(
                f"cannot reach Ollama at {self._client.base_url} — run `kriterion doctor` "
                "for diagnosis"
            ) from exc
        except TimeoutError as exc:
            # Raised directly by the stdlib socket layer on a slow response body
            # (not wrapped in OllamaConnectionError -- that only covers connect
            # failures), so it must be caught here too or it crashes the run with
            # a raw traceback instead of a diagnosable error.
            raise ExecutorError(
                f"Ollama request to {self._client.base_url} timed out after "
                f"{getattr(self._client, 'timeout', '?')}s -- the model may be under heavy load "
                "for this prompt length on this hardware"
            ) from exc

        return ExecutorResult(
            text=result.data.get("response", ""),
            elapsed_seconds=result.elapsed_seconds,
            model=self.model,
            seed=seed,
        )

    def doctor(self) -> dict:
        """Connectivity + model-availability check for `kriterion doctor`."""
        try:
            models_result = self._client.list_models()
        except OllamaConnectionError as exc:
            return {"ok": False, "reason": str(exc)}

        available = [m["name"] for m in models_result.data.get("models", [])]
        return {
            "ok": self.model in available,
            "base_url": self._client.base_url,
            "target_model": self.model,
            "target_model_available": self.model in available,
            "available_models": available,
        }
