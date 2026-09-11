"""AssuranceEvidenceEnvelope → Kriterion EvidenceItem adapter (ADR-007).

The consumed contract
---------------------
An *assurance evidence document pair*, read as plain JSON:

- ``envelope.json`` (required): the canonical-JSON serialisation of an
  assurance ``EvidenceEnvelope`` — ``kind: EvidenceEnvelope``,
  ``envelopeVersion: 0.x``, a ``capability`` block, a ``results[]`` list
  (one entry per eval spec run, each with ``specId``/``method``/``outcome``),
  an optional ``criticalFailures[]`` list, and an optional structured
  ``fingerprint`` whose ``uncovered[]`` names what the fingerprint does NOT
  track. Hekton Assurance's ``hekton.dev/v0alpha1`` envelope is the
  reference producer, but nothing here imports it: the contract is the
  document shape, and this module is a tolerant reader — unknown fields are
  ignored, only the minimal set below is required.

- ``decision.json`` (optional): the producer's decision over that envelope —
  ``state`` (PASS | FAIL | REVIEW_REQUIRED | STALE | INCOMPLETE), a
  ``reasons[]`` list, and an optional ``freshness`` block. When absent, the
  assurance status is UNKNOWN and is never treated as PASS.

Mapping rules (the epistemic part — deliberately NOT a confidence score)
------------------------------------------------------------------------
- deterministic result        → MEASURED, strength HIGH
- counterfactual result       → MEASURED, strength MEDIUM
- model-judge result          → EXPERT_JUDGMENT, strength LOW (a model's
  judgment is not a measurement; mirrors the producer's own posture that a
  judge may never gate)
- error / indeterminate       → UNKNOWN, strength LOW (not a verdict)
- unrecognised method         → UNKNOWN, strength LOW (we cannot classify
  how it was produced, so we must not claim we can)
- criticalFailures[]          → one MEASURED/HIGH item each, claim prefixed
  ``CRITICAL ASSURANCE FAILURE``
- fingerprint.uncovered[]     → one UNKNOWN/LOW item each (coverage gaps are
  first-class unknowns, not fine print)
- the decision itself         → one INFERENCE item (a deterministic
  derivation over measured results), or UNKNOWN when no decision document
  was supplied

Hard guarantees, enforced here and tested in tests/assurance/:

1. A stale envelope is visibly stale: every derived item's strength is
   downgraded to LOW and its claim carries a ``[STALE assurance evidence]``
   marker.
2. A critical failure can never be represented as PASS: a decision document
   claiming PASS over an envelope with criticalFailures raises
   ``AssuranceImportError`` instead of importing anything.
3. No decision document ≠ PASS: the summary item says UNKNOWN, explicitly.
4. Provenance survives: every derived item's ``source`` names the envelope
   reference and the spec id it came from.
5. Attestation is the caller's explicit statement (AUTHORED fixture vs REAL
   import), never guessed.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kriterion.domain.evidence import Attestation, EvidenceCategory, EvidenceItem, Strength

STALE_MARKER = "[STALE assurance evidence]"
_MAX_DETAIL_CHARS = 240


class AssuranceImportError(ValueError):
    """The document pair is malformed, or internally inconsistent in a way
    that could launder a failure (e.g. PASS over critical failures)."""


@dataclass(kw_only=True)
class AssuranceSummary:
    """What the import concluded, for display next to the derived items."""

    capability_name: str
    capability_version: str
    envelope_ref: str
    generated_at: str
    decision_state: str  # PASS/FAIL/REVIEW_REQUIRED/STALE/INCOMPLETE/UNKNOWN
    stale: bool
    critical_failure_count: int
    result_count: int
    uncovered_count: int
    reasons: list[str] = field(default_factory=list)


def load_assurance_documents(envelope_dir: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Read envelope.json (required) and decision.json (optional) from a directory."""
    envelope_path = envelope_dir / "envelope.json"
    if not envelope_path.is_file():
        raise AssuranceImportError(f"no envelope.json in {envelope_dir}")
    try:
        envelope = json.loads(envelope_path.read_text())
    except json.JSONDecodeError as exc:
        raise AssuranceImportError(f"envelope.json is not valid JSON: {exc}") from exc

    decision: dict[str, Any] | None = None
    decision_path = envelope_dir / "decision.json"
    if decision_path.is_file():
        try:
            decision = json.loads(decision_path.read_text())
        except json.JSONDecodeError as exc:
            raise AssuranceImportError(f"decision.json is not valid JSON: {exc}") from exc

    return envelope, decision


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unnamed"


def _clip(text: str) -> str:
    text = " ".join(text.split())
    if len(text) > _MAX_DETAIL_CHARS:
        return text[: _MAX_DETAIL_CHARS - 1] + "…"
    return text


def _validate_envelope(envelope: dict[str, Any]) -> None:
    if not isinstance(envelope, dict):
        raise AssuranceImportError("envelope document is not a JSON object")
    if envelope.get("kind") != "EvidenceEnvelope":
        raise AssuranceImportError(
            f"envelope kind is {envelope.get('kind')!r}, expected 'EvidenceEnvelope'"
        )
    version = str(envelope.get("envelopeVersion", ""))
    if not version.startswith("0."):
        raise AssuranceImportError(
            f"envelopeVersion {version!r} is outside the understood 0.x contract — "
            "refusing to guess what a new major version means"
        )
    if not isinstance(envelope.get("capability"), dict) or not envelope["capability"].get("name"):
        raise AssuranceImportError("envelope has no capability.name")
    if not isinstance(envelope.get("results"), list):
        raise AssuranceImportError("envelope has no results[] list")


def _decision_state(decision: dict[str, Any] | None) -> str:
    if decision is None:
        return "UNKNOWN"
    state = decision.get("state")
    if state not in ("PASS", "FAIL", "REVIEW_REQUIRED", "STALE", "INCOMPLETE"):
        # A state we don't understand must degrade to UNKNOWN, never to PASS.
        return "UNKNOWN"
    return state


def _is_stale(decision: dict[str, Any] | None) -> bool:
    if decision is None:
        return False
    if decision.get("state") == "STALE":
        return True
    freshness = decision.get("freshness")
    return bool(isinstance(freshness, dict) and freshness.get("stale"))


_METHOD_MAP: dict[str, tuple[EvidenceCategory, Strength]] = {
    "deterministic": (EvidenceCategory.MEASURED, Strength.HIGH),
    "counterfactual": (EvidenceCategory.MEASURED, Strength.MEDIUM),
    "model-judge": (EvidenceCategory.EXPERT_JUDGMENT, Strength.LOW),
}


def adapt_envelope(
    envelope: dict[str, Any],
    decision: dict[str, Any] | None,
    *,
    attestation: Attestation,
    created_at: str,
) -> tuple[AssuranceSummary, list[EvidenceItem]]:
    """Translate one assurance document pair into Kriterion EvidenceItems.

    Pure: no I/O, no model calls. Raises AssuranceImportError rather than
    importing anything when the pair is malformed or would launder a
    critical failure into a PASS.
    """
    _validate_envelope(envelope)

    capability = envelope["capability"]
    cap_name = str(capability.get("name"))
    cap_version = str(capability.get("version", "?"))
    cap_slug = _slug(cap_name)
    generated_at = str(envelope.get("generatedAt", "?"))
    envelope_ref = str(envelope.get("_envelopeRef") or (decision or {}).get("envelopeRef") or generated_at)
    critical_failures = envelope.get("criticalFailures") or []
    state = _decision_state(decision)
    stale = _is_stale(decision)

    if critical_failures and state == "PASS":
        raise AssuranceImportError(
            f"decision claims PASS but the envelope records {len(critical_failures)} "
            "critical failure(s) — refusing to import an inconsistent pair that would "
            "represent a critical assurance failure as PASS"
        )

    source_base = f"Assurance envelope {envelope_ref} (capability {cap_name} v{cap_version})"
    period = generated_at[:10] if generated_at != "?" else "unknown"
    items: list[EvidenceItem] = []

    def _make(
        item_id: str,
        *,
        category: EvidenceCategory,
        strength: Strength,
        claim: str,
        source_detail: str,
    ) -> EvidenceItem:
        if stale:
            strength = Strength.LOW
            claim = f"{STALE_MARKER} {claim}"
        return EvidenceItem(
            id=item_id,
            created_at=created_at,
            category=category,
            attestation=attestation,
            claim=claim,
            source=f"{source_base}, {source_detail}",
            period=period,
            strength=strength,
        )

    # 1. Per-result items.
    for i, result in enumerate(envelope["results"]):
        if not isinstance(result, dict):
            continue
        spec_id = str(result.get("specId") or f"result-{i}")
        method = str(result.get("method", ""))
        outcome = str(result.get("outcome", "missing"))
        detail = _clip(str(result.get("detail", "")))

        if outcome in ("error", "indeterminate", "missing"):
            category, strength = EvidenceCategory.UNKNOWN, Strength.LOW
            claim = (
                f"Assurance check '{spec_id}' did not produce a verdict "
                f"(outcome: {outcome}). Its subject remains unknown, not passed."
            )
        elif method in _METHOD_MAP:
            category, strength = _METHOD_MAP[method]
            claim = f"Assurance {method} check '{spec_id}': {outcome.upper()}."
            if detail:
                claim += f" {detail}"
        else:
            category, strength = EvidenceCategory.UNKNOWN, Strength.LOW
            claim = (
                f"Assurance check '{spec_id}' reported {outcome.upper()} via unrecognised "
                f"method '{method}' — treated as unverified, not as a measurement."
            )

        items.append(
            _make(
                f"asr-{cap_slug}-{_slug(spec_id)}",
                category=category,
                strength=strength,
                claim=claim,
                source_detail=f"spec {spec_id}",
            )
        )

    # 2. Critical failures — always their own explicit items.
    for i, cf in enumerate(critical_failures):
        if not isinstance(cf, dict):
            cf = {}
        condition = cf.get("condition", "unspecified condition")
        spec_id = cf.get("specId", "?")
        claim = (
            f"CRITICAL ASSURANCE FAILURE: {condition} — observed "
            f"{cf.get('observed', '?')}, allowed {cf.get('allowed', '?')} (spec {spec_id})."
        )
        items.append(
            _make(
                f"asr-{cap_slug}-critical-{i + 1}",
                category=EvidenceCategory.MEASURED,
                strength=Strength.HIGH,
                claim=claim,
                source_detail=f"criticalFailures[{i}]",
            )
        )

    # 3. Coverage gaps: what the assurance fingerprint does NOT track.
    fingerprint = envelope.get("fingerprint") or {}
    uncovered = fingerprint.get("uncovered") or [] if isinstance(fingerprint, dict) else []
    for i, gap in enumerate(uncovered):
        items.append(
            _make(
                f"asr-{cap_slug}-uncovered-{_slug(str(gap))}",
                category=EvidenceCategory.UNKNOWN,
                strength=Strength.LOW,
                claim=(
                    f"Assurance coverage gap: '{gap}' is not tracked by the assurance "
                    "fingerprint. A change there would NOT invalidate this evidence, "
                    "so its current state is unknown."
                ),
                source_detail=f"fingerprint.uncovered[{i}]",
            )
        )

    # 4. The decision itself.
    reasons = [
        _clip(str(r.get("message", r)))
        for r in ((decision or {}).get("reasons") or [])
    ]
    if decision is None:
        decision_claim = (
            f"No assurance decision document was supplied for capability {cap_name} "
            f"v{cap_version}. Assurance status is UNKNOWN and must not be treated as PASS."
        )
        decision_category, decision_strength = EvidenceCategory.UNKNOWN, Strength.LOW
    else:
        decision_claim = (
            f"Assurance decision for capability {cap_name} v{cap_version}: {state}"
            f" (decider {decision.get('deciderVersion', '?')})."
        )
        if reasons:
            decision_claim += " Reasons: " + "; ".join(reasons[:3])
        decision_category, decision_strength = EvidenceCategory.INFERENCE, Strength.HIGH
        if state == "UNKNOWN":
            decision_category, decision_strength = EvidenceCategory.UNKNOWN, Strength.LOW

    items.append(
        _make(
            f"asr-{cap_slug}-decision",
            category=decision_category,
            strength=decision_strength,
            claim=decision_claim,
            source_detail="decision document" if decision is not None else "decision document (absent)",
        )
    )

    summary = AssuranceSummary(
        capability_name=cap_name,
        capability_version=cap_version,
        envelope_ref=envelope_ref,
        generated_at=generated_at,
        decision_state=state,
        stale=stale,
        critical_failure_count=len(critical_failures),
        result_count=len(envelope["results"]),
        uncovered_count=len(uncovered),
        reasons=reasons,
    )
    return summary, items


__all__ = [
    "AssuranceImportError",
    "AssuranceSummary",
    "STALE_MARKER",
    "adapt_envelope",
    "load_assurance_documents",
]
