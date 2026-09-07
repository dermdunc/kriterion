import json

import pytest

from kriterion.executors.base import ExecutorError
from kriterion.executors.replay import ReplayExecutor


def _write_recording(tmp_path, calls):
    path = tmp_path / "recording.json"
    path.write_text(json.dumps(calls))
    return path


def test_replays_recorded_calls_in_order(tmp_path):
    path = _write_recording(
        tmp_path,
        [
            {"prompt": "first", "text": "a", "elapsed_seconds": 0.1, "model": "m", "seed": 0},
            {"prompt": "second", "text": "b", "elapsed_seconds": 0.2, "model": "m", "seed": 1},
        ],
    )
    executor = ReplayExecutor(path)
    r1 = executor.complete("first")
    r2 = executor.complete("second")
    assert (r1.text, r2.text) == ("a", "b")


def test_raises_on_prompt_divergence(tmp_path):
    path = _write_recording(
        tmp_path, [{"prompt": "expected", "text": "a", "elapsed_seconds": 0.1, "model": "m", "seed": 0}]
    )
    executor = ReplayExecutor(path)
    with pytest.raises(ExecutorError, match="divergence"):
        executor.complete("different prompt")


def test_raises_when_tape_exhausted(tmp_path):
    path = _write_recording(
        tmp_path, [{"prompt": "only", "text": "a", "elapsed_seconds": 0.1, "model": "m", "seed": 0}]
    )
    executor = ReplayExecutor(path)
    executor.complete("only")
    with pytest.raises(ExecutorError, match="exhausted"):
        executor.complete("only")


def test_raises_when_recording_missing(tmp_path):
    with pytest.raises(ExecutorError, match="no recording found"):
        ReplayExecutor(tmp_path / "missing.json")
