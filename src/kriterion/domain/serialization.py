"""Canonical JSON serialisation and sha256 fingerprinting.

Every domain record must fingerprint identically regardless of field-insertion
order (docs/v0-plan.md Section 4: "serialises to canonical JSON with sorted
keys so sha256 fingerprints are stable"). This is the one shared mechanism
every frozen artifact (ledger, case, manifest) depends on for its own
immutability guarantee, so it lives here rather than being reimplemented
per type.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _to_jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    return value


def to_dict(record: Any) -> dict[str, Any]:
    """A dataclass record (or plain dict) as a JSON-safe dict, enums resolved to values."""
    return _to_jsonable(record)


def canonical_json(record: Any) -> str:
    """Deterministic JSON text: sorted keys, no extraneous whitespace, stable across
    key-insertion order and enum identity."""
    return json.dumps(to_dict(record), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def fingerprint(record: Any) -> str:
    """sha256 hex digest of a record's canonical JSON form."""
    return hashlib.sha256(canonical_json(record).encode("utf-8")).hexdigest()
