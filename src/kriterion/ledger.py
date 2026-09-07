"""Ledger freeze: turns a case pack's evidence items into a fingerprinted,
append-only EvidenceLedger version (docs/v0-plan.md Section 5, phase 1).

"Only kriterion ledger add writes evidence" (ADR-003) — this module is that
single write path. A frozen ledger version is never edited; new evidence
creates vN+1, produced by calling freeze() again with the superset of items.
"""

from __future__ import annotations

import json
from pathlib import Path

from kriterion.domain.evidence import EvidenceItem, EvidenceLedger
from kriterion.domain.serialization import fingerprint, to_dict


def freeze(items: list[EvidenceItem], *, ledger_id: str, created_at: str, version: int = 1) -> EvidenceLedger:
    """Freeze a list of evidence items into a fingerprinted ledger version.

    Raises ValueError on a duplicate item id — the same check load_case_pack
    already does for a single case.toml, repeated here because freeze() is
    the actual ADR-003 write path and must not trust its caller.
    """
    seen_ids: set[str] = set()
    for item in items:
        if item.id in seen_ids:
            raise ValueError(f"duplicate evidence id '{item.id}' — cannot freeze")
        seen_ids.add(item.id)

    ledger = EvidenceLedger(
        id=ledger_id,
        created_at=created_at,
        version=version,
        items=items,
    )
    ledger.fingerprint = fingerprint(ledger.items)
    return ledger


def write_frozen_ledger(ledger: EvidenceLedger, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(to_dict(ledger), indent=2, sort_keys=True) + "\n")
