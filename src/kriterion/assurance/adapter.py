"""AssuranceEvidenceEnvelope → Kriterion EvidenceItem adapter (ADR-007).

The consumed contract
---------------------
An *assurance evidence document pair*, read as plain JSON:

- ``envelope.json`` (required): the canonical-JSON serialisation of an
  assurance ``EvidenceEnvelope`` — ``kind: EvidenceEnvelope``,
  ``envelopeVersion: 0.x``, a ``capability`` block, a ``results[]`` list
  (one entry per eval spec run, each with ``specId``/``method``/``outcome``),
  a **required** ``criticalFailures[]`` list, and an optional structured
  ``fingerprint`` whose ``uncovered[]`` names what the fingerprint does NOT
  track. Hekton Assurance's ``hekton.dev/v0alpha1`` envelope is the
  reference producer, but nothing here imports it: the contract is the
  document shape, and this module is a tolerant reader for *unknown* fields —
  unknown keys are ignored — and a **strict** reader for the fields listed
  below, because guessing at a safety-critical field is how failures get
  laundered.

- ``decision.json`` (optional): the producer's decision over that envelope —
  ``state`` (PASS | FAIL | REVIEW_REQUIRED | STALE | INCOMPLETE), a
  ``capabilityRef`` identifying what it decided about, a ``reasons[]`` list,
  and an optional ``freshness`` block. When absent, the assurance status is
  UNKNOWN and is never treated as PASS.

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
   downgraded to LOW, its claim carries a ``[STALE assurance evidence]``
   marker, and a *declared PASS over stale evidence is reported as STALE,
   never as PASS* — staleness can only ever downgrade a state.
2. A critical failure can never be represented as PASS. Three separate
   routes are closed: (a) ``criticalFailures`` non-empty with a PASS
   decision, (b) ``criticalFailures`` omitted entirely — a missing
   safety-critical field is a refusal, not an implied empty list, and
   (c) a *gating* result whose outcome is ``fail`` under a PASS decision.
3. No decision document ≠ PASS: the summary item says UNKNOWN, explicitly.
4. The decision is identity-bound to the envelope: ``decision.capabilityRef``
   must name the same capability (and, when it declares one, the same
   version) as ``envelope.capability``, and a declared ``envelopeRef`` must
   match the envelope's own ``_envelopeRef`` when it has one. A PASS decision
   about a *different* capability cannot be attached to this envelope.
5. Provenance survives: every derived item's ``source`` names the envelope
   reference and the spec id it came from, and the summary carries the
   producer's own provenance facts (whether artifact digests were captured,
   and the recorded source commit) so an importer cannot silently upgrade an
   undigested envelope into a verified one.
6. Every contract-shape failure — a non-object document, a wrongly typed
   container, a malformed nested field, a duplicate derived id — raises
   ``AssuranceImportError``. The adapter never lets a malformed document
   escape as an uncaught ``AttributeError``/``TypeError``: "unknown" must
   remain distinct from "crashed".
7. Attestation is the caller's explicit statement (AUTHORED fixture vs REAL
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

_KNOWN_STATES = ("PASS", "FAIL", "REVIEW_REQUIRED", "STALE", "INCOMPLETE")


class AssuranceImportError(ValueError):
    """The document pair is malformed, wrongly typed, or internally
    inconsistent in a way that could launder a failure (e.g. PASS over
    critical failures, or a decision about a different capability)."""


@dataclass(kw_only=True)
class AssuranceSummary:
    """What the import concluded, for display next to the derived items."""

    capability_name: str
    capability_version: str
    envelope_ref: str
    generated_at: str
    decision_state: str  # effective: PASS/FAIL/REVIEW_REQUIRED/STALE/INCOMPLETE/UNKNOWN
    declared_decision_state: str  # exactly what the decision document said
    stale: bool
    critical_failure_count: int
    result_count: int
    uncovered_count: int
    reasons: list[str] = field(default_factory=list)
    # Producer provenance, carried through rather than re-asserted.
    digests_captured: bool | None = None
    source_commit: str | None = None


# --------------------------------------------------------------------------
# Shape validation. Every helper below raises AssuranceImportError, never a
# bare AttributeError/TypeError, so `kriterion assurance import` can always
# refuse cleanly instead of producing a traceback.
# --------------------------------------------------------------------------


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AssuranceImportError(
            f"{label} must be a JSON object, got {type(value).__name__}"
        )
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise AssuranceImportError(
            f"{label} must be a JSON list, got {type(value).__name__}"
        )
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AssuranceImportError(f"{label} must be a non-empty string, got {value!r}")
    return value


def _optional_text(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise AssuranceImportError(f"{label} must be a string when present, got {value!r}")
    return value


def load_assurance_documents(envelope_dir: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Read envelope.json (required) and decision.json (optional) from a directory.

    Both are shape-checked to be JSON *objects* here, so a top-level array or
    scalar is a controlled refusal rather than a downstream AttributeError.
    """
    envelope_path = envelope_dir / "envelope.json"
    if not envelope_path.is_file():
        raise AssuranceImportError(f"no envelope.json in {envelope_dir}")
    try:
        envelope = json.loads(envelope_path.read_text())
    except json.JSONDecodeError as exc:
        raise AssuranceImportError(f"envelope.json is not valid JSON: {exc}") from exc
    _require_object(envelope, "envelope.json")

    decision: dict[str, Any] | None = None
    decision_path = envelope_dir / "decision.json"
    if decision_path.is_file():
        try:
            decision = json.loads(decision_path.read_text())
        except json.JSONDecodeError as exc:
            raise AssuranceImportError(f"decision.json is not valid JSON: {exc}") from exc
        _require_object(decision, "decision.json")

    return envelope, decision


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unnamed"


def _clip(text: str) -> str:
    text = " ".join(text.split())
    if len(text) > _MAX_DETAIL_CHARS:
        return text[: _MAX_DETAIL_CHARS - 1] + "…"
    return text


def _validate_envelope(envelope: dict[str, Any]) -> None:
    _require_object(envelope, "envelope document")
    if envelope.get("kind") != "EvidenceEnvelope":
        raise AssuranceImportError(
            f"envelope kind is {envelope.get('kind')!r}, expected 'EvidenceEnvelope'"
        )
    version = envelope.get("envelopeVersion")
    if not isinstance(version, str) or not version.startswith("0."):
        raise AssuranceImportError(
            f"envelopeVersion {version!r} is outside the understood 0.x contract — "
            "refusing to guess what a new major version means"
        )

    capability = _require_object(envelope.get("capability"), "envelope.capability")
    _require_text(capability.get("name"), "envelope.capability.name")

    results = _require_list(envelope.get("results"), "envelope.results")
    for i, result in enumerate(results):
        _require_object(result, f"envelope.results[{i}]")

    # criticalFailures is safety-critical: an absent list is NOT an empty
    # list. Silently defaulting it to [] is exactly how a critical failure
    # becomes a PASS, so refuse rather than assume.
    if "criticalFailures" not in envelope:
        raise AssuranceImportError(
            "envelope does not declare criticalFailures[] — the absence of critical "
            "failures cannot be inferred from a missing field. Refusing to import an "
            "envelope whose critical-failure state is unstated."
        )
    critical_failures = _require_list(envelope.get("criticalFailures"), "envelope.criticalFailures")
    for i, cf in enumerate(critical_failures):
        _require_object(cf, f"envelope.criticalFailures[{i}]")

    if "fingerprint" in envelope and envelope["fingerprint"] is not None:
        fingerprint = _require_object(envelope["fingerprint"], "envelope.fingerprint")
        if "uncovered" in fingerprint and fingerprint["uncovered"] is not None:
            uncovered = _require_list(fingerprint["uncovered"], "envelope.fingerprint.uncovered")
            for i, gap in enumerate(uncovered):
                _require_text(gap, f"envelope.fingerprint.uncovered[{i}]")

    if "provenance" in envelope and envelope["provenance"] is not None:
        _require_object(envelope["provenance"], "envelope.provenance")
    if "sourceState" in envelope and envelope["sourceState"] is not None:
        _require_object(envelope["sourceState"], "envelope.sourceState")


def _validate_decision(decision: dict[str, Any]) -> None:
    _require_object(decision, "decision document")
    if "reasons" in decision and decision["reasons"] is not None:
        reasons = _require_list(decision.get("reasons"), "decision.reasons")
        for i, reason in enumerate(reasons):
            if not isinstance(reason, (dict, str)):
                raise AssuranceImportError(
                    f"decision.reasons[{i}] must be a JSON object or string, "
                    f"got {type(reason).__name__}"
                )
    if "freshness" in decision and decision["freshness"] is not None:
        _require_object(decision["freshness"], "decision.freshness")
    if "capabilityRef" in decision and decision["capabilityRef"] is not None:
        _require_object(decision["capabilityRef"], "decision.capabilityRef")
    _optional_text(decision.get("envelopeRef"), "decision.envelopeRef")


def _bind_identity(envelope: dict[str, Any], decision: dict[str, Any]) -> None:
    """Refuse a decision document that is not about *this* envelope.

    Without this, a PASS decision over some other capability (or an older
    version of the same one) can be paired with any envelope and imported as
    an authoritative verdict.
    """
    capability = envelope["capability"]
    env_name = str(capability.get("name"))
    env_version = capability.get("version")

    cap_ref = decision.get("capabilityRef")
    if cap_ref is None:
        raise AssuranceImportError(
            "decision document has no capabilityRef — it cannot be bound to this "
            f"envelope's capability ({env_name}). Refusing to assume the decision is "
            "about the capability it happens to sit next to."
        )
    ref_name = _require_text(cap_ref.get("name"), "decision.capabilityRef.name")
    if ref_name != env_name:
        raise AssuranceImportError(
            f"decision is about capability {ref_name!r} but the envelope describes "
            f"{env_name!r} — refusing to import a mismatched document pair"
        )
    ref_version = cap_ref.get("version")
    if ref_version is not None and env_version is not None and str(ref_version) != str(env_version):
        raise AssuranceImportError(
            f"decision is about {ref_name} v{ref_version} but the envelope describes "
            f"v{env_version} — refusing to import a version-mismatched document pair"
        )

    env_ref = envelope.get("_envelopeRef")
    dec_ref = decision.get("envelopeRef")
    if isinstance(env_ref, str) and isinstance(dec_ref, str) and env_ref != dec_ref:
        raise AssuranceImportError(
            f"decision.envelopeRef {dec_ref!r} does not match the envelope's own "
            f"_envelopeRef {env_ref!r} — refusing to import a mismatched document pair"
        )


def _declared_state(decision: dict[str, Any] | None) -> str:
    if decision is None:
        return "UNKNOWN"
    state = decision.get("state")
    if state not in _KNOWN_STATES:
        # A state we don't understand must degrade to UNKNOWN, never to PASS.
        return "UNKNOWN"
    return str(state)


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


def _reason_text(reason: Any) -> str:
    if isinstance(reason, dict):
        message = reason.get("message")
        return _clip(str(message)) if message is not None else _clip(json.dumps(reason, sort_keys=True))
    return _clip(str(reason))


def adapt_envelope(
    envelope: dict[str, Any],
    decision: dict[str, Any] | None,
    *,
    attestation: Attestation,
    created_at: str,
) -> tuple[AssuranceSummary, list[EvidenceItem]]:
    """Translate one assurance document pair into Kriterion EvidenceItems.

    Pure: no I/O, no model calls. Raises AssuranceImportError rather than
    importing anything when the pair is malformed, mis-typed, not
    identity-bound, or would launder a critical failure into a PASS.
    """
    _validate_envelope(envelope)
    if decision is not None:
        _validate_decision(decision)
        _bind_identity(envelope, decision)

    capability = envelope["capability"]
    cap_name = str(capability.get("name"))
    cap_version = str(capability.get("version", "?"))
    cap_slug = _slug(cap_name)
    generated_at = str(envelope.get("generatedAt", "?"))
    envelope_ref = str(
        envelope.get("_envelopeRef") or (decision or {}).get("envelopeRef") or generated_at
    )
    critical_failures: list[dict[str, Any]] = envelope["criticalFailures"]
    declared_state = _declared_state(decision)
    stale = _is_stale(decision)

    # --- anti-laundering guards, before anything is derived ----------------
    if critical_failures and declared_state == "PASS":
        raise AssuranceImportError(
            f"decision claims PASS but the envelope records {len(critical_failures)} "
            "critical failure(s) — refusing to import an inconsistent pair that would "
            "represent a critical assurance failure as PASS"
        )

    gating_failures = [
        str(r.get("specId") or f"result-{i}")
        for i, r in enumerate(envelope["results"])
        if r.get("gating") is True and str(r.get("outcome", "")).lower() == "fail"
    ]
    if gating_failures and declared_state == "PASS":
        raise AssuranceImportError(
            "decision claims PASS but the envelope records a FAIL outcome on gating "
            f"spec(s) {', '.join(gating_failures)} — refusing to import an inconsistent "
            "pair that would represent a gating failure as PASS"
        )

    # Staleness can only ever downgrade. A PASS over evidence the producer
    # itself marks stale is reported as STALE, not as PASS.
    effective_state = declared_state
    if stale and declared_state == "PASS":
        effective_state = "STALE"

    provenance = envelope.get("provenance") or {}
    digests_captured = provenance.get("digestsCaptured") if isinstance(provenance, dict) else None
    if not isinstance(digests_captured, bool):
        digests_captured = None
    source_state = envelope.get("sourceState") or {}
    source_commit = source_state.get("commit") if isinstance(source_state, dict) else None
    source_commit = source_commit if isinstance(source_commit, str) else None

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
        spec_id = str(result.get("specId") or f"result-{i}")
        method = str(result.get("method", ""))
        outcome = str(result.get("outcome", "missing"))
        detail_raw = result.get("detail", "")
        detail = _clip(str(detail_raw)) if isinstance(detail_raw, str) else ""

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
    reasons = [_reason_text(r) for r in ((decision or {}).get("reasons") or [])]
    if decision is None:
        decision_claim = (
            f"No assurance decision document was supplied for capability {cap_name} "
            f"v{cap_version}. Assurance status is UNKNOWN and must not be treated as PASS."
        )
        decision_category, decision_strength = EvidenceCategory.UNKNOWN, Strength.LOW
    else:
        decision_claim = (
            f"Assurance decision for capability {cap_name} v{cap_version}: {effective_state}"
            f" (decider {decision.get('deciderVersion', '?')})."
        )
        if effective_state != declared_state:
            decision_claim += (
                f" The producer declared {declared_state}, but its own freshness block "
                "reports this evidence stale; a stale PASS is not a PASS."
            )
        if reasons:
            decision_claim += " Reasons: " + "; ".join(reasons[:3])
        decision_category, decision_strength = EvidenceCategory.INFERENCE, Strength.HIGH
        if effective_state in ("UNKNOWN", "STALE"):
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

    # 5. Provenance: an envelope that captured no artifact digests is not
    #    bound to any real artifact, and that must be visible, not implied.
    if digests_captured is False:
        items.append(
            _make(
                f"asr-{cap_slug}-provenance",
                category=EvidenceCategory.UNKNOWN,
                strength=Strength.LOW,
                claim=(
                    "The assurance producer recorded digestsCaptured=false for this "
                    "envelope: its results are not cryptographically bound to any "
                    "artifact, so what was actually evaluated is unverified."
                ),
                source_detail="provenance.digestsCaptured",
            )
        )

    # Derived ids must be unique — freeze() rejects duplicates, and a silent
    # collision would drop one source result from the record.
    seen: set[str] = set()
    for item in items:
        if item.id in seen:
            raise AssuranceImportError(
                f"the envelope produces a duplicate derived evidence id '{item.id}' "
                "(most likely a repeated specId or coverage gap) — refusing to import "
                "a document that would silently drop one of them"
            )
        seen.add(item.id)

    summary = AssuranceSummary(
        capability_name=cap_name,
        capability_version=cap_version,
        envelope_ref=envelope_ref,
        generated_at=generated_at,
        decision_state=effective_state,
        declared_decision_state=declared_state,
        stale=stale,
        critical_failure_count=len(critical_failures),
        result_count=len(envelope["results"]),
        uncovered_count=len(uncovered),
        reasons=reasons,
        digests_captured=digests_captured,
        source_commit=source_commit,
    )
    return summary, items


__all__ = [
    "AssuranceImportError",
    "AssuranceSummary",
    "STALE_MARKER",
    "adapt_envelope",
    "load_assurance_documents",
]
