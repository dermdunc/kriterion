from kriterion.domain import (
    Ask,
    Attestation,
    CaseRealism,
    DecisionCase,
    EvidenceCategory,
    EvidenceItem,
    Strength,
    canonical_json,
    fingerprint,
    to_dict,
)


def _make_case() -> DecisionCase:
    return DecisionCase(
        id="case-a",
        created_at="2026-09-05T00:00:00Z",
        title="Enterprise coding-agent rollout",
        sponsor="CTO",
        decision_owner="cio",
        decision_requested="Should we fund a 5,000-engineer coding-agent rollout?",
        ask=Ask(type="staged_funding", amount_gbp=2_000_000, duration="12 months"),
        alternatives=["do_nothing", "pilot_500", "full_rollout"],
        case_realism=CaseRealism.AUTHORED_FIXTURE,
    )


def test_fingerprint_stable_under_key_reordering():
    case = _make_case()

    d1 = to_dict(case)
    # Build an equivalent dict with keys inserted in a different order.
    d2 = {k: d1[k] for k in reversed(list(d1.keys()))}

    assert canonical_json(d1) == canonical_json(d2)
    assert fingerprint(d1) == fingerprint(d2)


def test_fingerprint_changes_when_content_changes():
    case_a = _make_case()
    case_b = _make_case()
    case_b.title = "A different title"

    assert fingerprint(case_a) != fingerprint(case_b)


def test_enum_serialises_to_its_value():
    item = EvidenceItem(
        id="ev-1",
        created_at="2026-09-05T00:00:00Z",
        category=EvidenceCategory.MEASURED,
        attestation=Attestation.AUTHORED,
        claim="Pilot acceptance rate 61%",
        source="fixture CSV",
        period="2026-Q2",
        strength=Strength.HIGH,
    )
    d = to_dict(item)
    assert d["category"] == "MEASURED"
    assert d["attestation"] == "AUTHORED"
    assert d["strength"] == "HIGH"


def test_canonical_json_round_trips_through_dict():
    import json

    case = _make_case()
    parsed = json.loads(canonical_json(case))
    assert parsed["title"] == "Enterprise coding-agent rollout"
    assert parsed["ask"]["amount_gbp"] == 2_000_000
