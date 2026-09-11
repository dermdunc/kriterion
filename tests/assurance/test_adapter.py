"""ADR-007 invariants for the assurance-evidence anti-corruption layer.

The mission-level guarantees under test:
- generic assurance evidence maps into Kriterion's own EvidenceItem type;
- epistemic classes are preserved, not flattened into one confidence score;
- unknown fields in the documents do not break the import (tolerant reader);
- stale evidence is visibly stale;
- a critical assurance failure can never be represented as PASS;
- a missing decision document degrades to UNKNOWN, never to PASS;
- provenance (envelope ref + spec id) survives the transformation;
- Kriterion works when assurance is absent (no import path is exercised by
  any other code path — asserted structurally at the bottom).
"""

import json
from pathlib import Path

import pytest

from kriterion.assurance.adapter import (
    STALE_MARKER,
    AssuranceImportError,
    adapt_envelope,
    load_assurance_documents,
)
from kriterion.domain.evidence import Attestation, EvidenceCategory, Strength

CREATED_AT = "2026-09-11T00:00:00Z"


def _envelope(**overrides):
    base = {
        "apiVersion": "hekton.dev/v0alpha1",
        "kind": "EvidenceEnvelope",
        "envelopeVersion": "0.1.0",
        "capability": {"name": "example-capability", "version": "1.0.0"},
        "generatedAt": "2026-09-01T09:00:00Z",
        "results": [
            {
                "specId": "det-check-001",
                "method": "deterministic",
                "gating": True,
                "outcome": "pass",
                "detail": "all clear",
            },
            {
                "specId": "cf-check-001",
                "method": "counterfactual",
                "gating": False,
                "outcome": "fail",
                "detail": "flip rate 0.3 over allowed 0.2",
            },
            {
                "specId": "judge-check-001",
                "method": "model-judge",
                "gating": False,
                "outcome": "pass",
                "detail": "mean score 0.93",
            },
            {
                "specId": "drift-check-001",
                "method": "deterministic",
                "gating": False,
                "outcome": "indeterminate",
                "detail": "cannot measure",
            },
        ],
        "criticalFailures": [],
        "fingerprint": {"components": {}, "uncovered": ["tool-schemas"]},
    }
    base.update(overrides)
    return base


def _decision(**overrides):
    base = {
        "state": "PASS",
        "envelopeRef": "evidence/example/envelope.yaml",
        "reasons": [{"code": "no-blocking-findings", "message": "all gating results passed"}],
        "deciderVersion": "0.0.1",
        "freshness": {"stale": False, "diffCount": 0},
    }
    base.update(overrides)
    return base


def _adapt(envelope, decision, attestation=Attestation.AUTHORED):
    return adapt_envelope(envelope, decision, attestation=attestation, created_at=CREATED_AT)


def _by_id(items):
    return {item.id: item for item in items}


def test_epistemic_classes_survive_the_transformation():
    _, items = _adapt(_envelope(), _decision())
    by_id = _by_id(items)

    det = by_id["asr-example-capability-det-check-001"]
    assert det.category is EvidenceCategory.MEASURED
    assert det.strength is Strength.HIGH

    cf = by_id["asr-example-capability-cf-check-001"]
    assert cf.category is EvidenceCategory.MEASURED
    assert cf.strength is Strength.MEDIUM
    assert "FAIL" in cf.claim

    judge = by_id["asr-example-capability-judge-check-001"]
    assert judge.category is EvidenceCategory.EXPERT_JUDGMENT
    assert judge.strength is Strength.LOW  # an uncalibrated judge is not a measurement

    drift = by_id["asr-example-capability-drift-check-001"]
    assert drift.category is EvidenceCategory.UNKNOWN
    assert "not passed" in drift.claim

    uncovered = by_id["asr-example-capability-uncovered-tool-schemas"]
    assert uncovered.category is EvidenceCategory.UNKNOWN

    decision_item = by_id["asr-example-capability-decision"]
    assert decision_item.category is EvidenceCategory.INFERENCE
    assert "PASS" in decision_item.claim


def test_provenance_and_attestation_are_preserved():
    summary, items = _adapt(_envelope(), _decision(), attestation=Attestation.AUTHORED)
    assert summary.envelope_ref == "evidence/example/envelope.yaml"
    for item in items:
        assert item.attestation is Attestation.AUTHORED
        assert "Assurance envelope evidence/example/envelope.yaml" in item.source
    spec_item = _by_id(items)["asr-example-capability-det-check-001"]
    assert "spec det-check-001" in spec_item.source


def test_unknown_fields_do_not_break_the_import():
    envelope = _envelope()
    envelope["totallyNewTopLevelBlock"] = {"nested": [1, 2, 3]}
    envelope["results"][0]["newResultField"] = "surprise"
    decision = _decision()
    decision["newDecisionField"] = {"a": 1}
    summary, items = _adapt(envelope, decision)
    assert summary.decision_state == "PASS"
    assert len(items) == 4 + 1 + 1  # results + uncovered + decision


def test_stale_evidence_is_visibly_stale_on_every_item():
    decision = _decision(state="STALE", freshness={"stale": True, "diffCount": 1})
    summary, items = _adapt(_envelope(), decision)
    assert summary.stale is True
    assert summary.decision_state == "STALE"
    for item in items:
        assert item.claim.startswith(STALE_MARKER)
        assert item.strength is Strength.LOW


def test_critical_failure_cannot_be_represented_as_pass():
    envelope = _envelope(
        criticalFailures=[
            {"condition": "secrets_leak", "specId": "det-check-001", "observed": 1, "allowed": 0}
        ]
    )
    with pytest.raises(AssuranceImportError, match="critical failure"):
        _adapt(envelope, _decision(state="PASS"))


def test_critical_failures_become_explicit_high_strength_items_under_fail():
    envelope = _envelope(
        criticalFailures=[
            {"condition": "secrets_leak", "specId": "det-check-001", "observed": 1, "allowed": 0}
        ]
    )
    summary, items = _adapt(envelope, _decision(state="FAIL"))
    assert summary.decision_state == "FAIL"
    critical = _by_id(items)["asr-example-capability-critical-1"]
    assert critical.category is EvidenceCategory.MEASURED
    assert critical.strength is Strength.HIGH
    assert critical.claim.startswith("CRITICAL ASSURANCE FAILURE")
    assert "PASS" not in _by_id(items)["asr-example-capability-decision"].claim


def test_missing_decision_document_is_unknown_never_pass():
    summary, items = _adapt(_envelope(), None)
    assert summary.decision_state == "UNKNOWN"
    decision_item = _by_id(items)["asr-example-capability-decision"]
    assert decision_item.category is EvidenceCategory.UNKNOWN
    assert "must not be treated as PASS" in decision_item.claim


def test_unrecognised_decision_state_degrades_to_unknown():
    summary, _ = _adapt(_envelope(), _decision(state="SUPER_PASS"))
    assert summary.decision_state == "UNKNOWN"


def test_unrecognised_result_method_is_unverified_not_measured():
    envelope = _envelope(
        results=[{"specId": "odd-001", "method": "vibes", "outcome": "pass", "detail": ""}]
    )
    _, items = _adapt(envelope, None)
    odd = _by_id(items)["asr-example-capability-odd-001"]
    assert odd.category is EvidenceCategory.UNKNOWN
    assert "unrecognised" in odd.claim


def test_future_major_envelope_version_is_refused_not_guessed():
    with pytest.raises(AssuranceImportError, match="envelopeVersion"):
        _adapt(_envelope(envelopeVersion="1.0.0"), None)


def test_malformed_envelope_is_refused():
    with pytest.raises(AssuranceImportError, match="kind"):
        _adapt({"kind": "SomethingElse"}, None)
    with pytest.raises(AssuranceImportError, match="capability"):
        _adapt(
            {"kind": "EvidenceEnvelope", "envelopeVersion": "0.1.0", "results": []},
            None,
        )


def test_load_assurance_documents_round_trip(tmp_path):
    (tmp_path / "envelope.json").write_text(json.dumps(_envelope()))
    (tmp_path / "decision.json").write_text(json.dumps(_decision()))
    envelope, decision = load_assurance_documents(tmp_path)
    summary, items = _adapt(envelope, decision)
    assert summary.capability_name == "example-capability"
    assert items


def test_load_assurance_documents_without_decision(tmp_path):
    (tmp_path / "envelope.json").write_text(json.dumps(_envelope()))
    envelope, decision = load_assurance_documents(tmp_path)
    assert decision is None
    summary, _ = _adapt(envelope, decision)
    assert summary.decision_state == "UNKNOWN"


def test_committed_fixture_pair_imports_cleanly():
    fixture_dir = Path(__file__).parent.parent.parent / "cases" / "coding-agent-rollout" / "assurance"
    envelope, decision = load_assurance_documents(fixture_dir)
    summary, items = _adapt(envelope, decision)
    assert summary.decision_state == "REVIEW_REQUIRED"
    assert summary.stale is False
    assert summary.critical_failure_count == 0
    # The fixture's own headline: prompt-injection resilience is partial.
    pi = _by_id(items)["asr-enterprise-coding-agent-prompt-injection-resilience-001"]
    assert pi.category is EvidenceCategory.MEASURED
    assert "FAIL" in pi.claim


def test_assurance_is_optional_no_other_kriterion_module_imports_it():
    """Kriterion must remain fully usable with no assurance evidence at all:
    nothing outside src/kriterion/assurance/ (and cli.py's lazy, command-local
    import) may import the adapter."""
    src_root = Path(__file__).parent.parent.parent / "src" / "kriterion"
    violations = []
    for path in src_root.rglob("*.py"):
        if path.parent.name == "assurance":
            continue
        for lineno, line in enumerate(path.read_text().splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("import kriterion.assurance") or stripped.startswith(
                "from kriterion.assurance"
            ):
                if path.name == "cli.py":
                    continue  # lazy import inside the one CLI command is the sanctioned use
                violations.append(f"{path}:{lineno}: {stripped}")
    assert not violations, "kriterion.assurance imported outside its package/cli:\n" + "\n".join(
        violations
    )
