"""Unit tests use a fake OllamaClient (no network) so the suite stays fast
and deterministic. test_doctor_live below is the one test that actually
talks to Ollama, per the task's real accept criterion."""

import json

import pytest

from kriterion.executors.base import ExecutorError
from kriterion.executors.hekton_local import HektonLocalExecutor


class _FakeTimedResult:
    def __init__(self, data):
        self.data = data
        self.elapsed_seconds = 0.01


class _FakeOllamaClient:
    base_url = "http://fake:11434"

    def __init__(self, models=("qwen2.5:14b-instruct",), response_text='{"ok": true}'):
        self._models = list(models)
        self._response_text = response_text
        self.last_generate_kwargs = None

    def list_models(self):
        return _FakeTimedResult({"models": [{"name": m} for m in self._models]})

    def generate(self, model, prompt, system=None, fmt=None, options=None):
        self.last_generate_kwargs = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "fmt": fmt,
            "options": options,
        }
        return _FakeTimedResult({"response": self._response_text})


def test_complete_uses_temperature_zero_and_the_given_seed():
    fake = _FakeOllamaClient()
    executor = HektonLocalExecutor(client=fake)

    result = executor.complete("say hi", seed=7)

    assert fake.last_generate_kwargs["options"] == {"temperature": 0, "seed": 7}
    assert fake.last_generate_kwargs["fmt"] == "json"
    assert result.text == '{"ok": true}'
    assert result.model == "qwen2.5:14b-instruct"
    assert result.seed == 7


def test_complete_response_is_schema_valid_json_when_fmt_json():
    fake = _FakeOllamaClient(response_text='{"answer": 42}')
    executor = HektonLocalExecutor(client=fake)
    result = executor.complete("say hi")
    assert json.loads(result.text) == {"answer": 42}


def test_connection_error_raises_executor_error_with_doctor_hint():
    from hekton_llm.ollama_client import OllamaConnectionError

    class _BrokenClient(_FakeOllamaClient):
        def generate(self, *a, **kw):
            raise OllamaConnectionError("boom")

    executor = HektonLocalExecutor(client=_BrokenClient())
    with pytest.raises(ExecutorError, match="kriterion doctor"):
        executor.complete("say hi")


def test_socket_timeout_raises_executor_error_not_a_raw_traceback():
    class _SlowClient(_FakeOllamaClient):
        def generate(self, *a, **kw):
            raise TimeoutError("timed out")

    executor = HektonLocalExecutor(client=_SlowClient())
    with pytest.raises(ExecutorError, match="timed out"):
        executor.complete("say hi")


def test_doctor_reports_not_ok_when_target_model_missing():
    fake = _FakeOllamaClient(models=("some-other-model",))
    executor = HektonLocalExecutor(client=fake)
    status = executor.doctor()
    assert status["ok"] is False
    assert status["target_model_available"] is False


def test_doctor_reports_ok_when_target_model_present():
    fake = _FakeOllamaClient(models=("qwen2.5:14b-instruct", "phi4-mini:latest"))
    executor = HektonLocalExecutor(client=fake)
    status = executor.doctor()
    assert status["ok"] is True


def test_doctor_live():
    """The real accept criterion: kriterion doctor green on this machine."""
    executor = HektonLocalExecutor()
    status = executor.doctor()
    if not status.get("ok") and "reason" in status:
        pytest.skip(f"Ollama not reachable in this environment: {status['reason']}")
    assert status["ok"] is True

    result = executor.complete('Reply with exactly this JSON: {"ok": true}', seed=0)
    parsed = json.loads(result.text)  # must be schema-valid JSON, not just any text
    assert isinstance(parsed, dict)
