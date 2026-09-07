from pathlib import Path

import pytest

from kriterion.casepack import load_case_pack
from kriterion.ledger import freeze, write_frozen_ledger

CASE_A_DIR = Path(__file__).parent.parent / "cases" / "coding-agent-rollout"


def _load_items():
    _, items, _assumptions = load_case_pack(CASE_A_DIR, created_at="2026-09-05T00:00:00Z")
    return items


def test_freeze_produces_a_fingerprinted_ledger():
    items = _load_items()
    ledger = freeze(items, ledger_id="case-a-ledger", created_at="2026-09-05T00:00:00Z")
    assert ledger.fingerprint is not None
    assert len(ledger.fingerprint) == 64  # sha256 hex
    assert ledger.version == 1
    assert len(ledger.items) == len(items)


def test_freeze_fingerprint_is_deterministic():
    items = _load_items()
    ledger_1 = freeze(items, ledger_id="case-a-ledger", created_at="2026-09-05T00:00:00Z")
    ledger_2 = freeze(items, ledger_id="case-a-ledger", created_at="2026-09-05T00:00:00Z")
    assert ledger_1.fingerprint == ledger_2.fingerprint


def test_freeze_rejects_duplicate_ids():
    items = _load_items()
    with pytest.raises(ValueError, match="duplicate evidence id"):
        freeze(items + [items[0]], ledger_id="case-a-ledger", created_at="2026-09-05T00:00:00Z")


def test_write_frozen_ledger_creates_valid_json(tmp_path):
    import json

    items = _load_items()
    ledger = freeze(items, ledger_id="case-a-ledger", created_at="2026-09-05T00:00:00Z")
    out_path = tmp_path / "runs" / "run-1" / "ledger.frozen.json"
    write_frozen_ledger(ledger, out_path)

    assert out_path.is_file()
    data = json.loads(out_path.read_text())
    assert data["fingerprint"] == ledger.fingerprint
    assert len(data["items"]) == len(items)
