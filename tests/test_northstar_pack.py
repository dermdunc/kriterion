"""Human Run 001's case pack: northstar-internal-developer-platform.

Northstar Software Group is fictional, and the whole point of this case is that
it is publishable in full precisely because it is. These tests pin the
properties that make that claim checkable rather than asserted, so a later edit
cannot quietly turn a synthetic scenario number into something a reader would
take for an observation of a real company.
"""

from collections import Counter
from pathlib import Path

from kriterion.casepack import load_case_pack
from kriterion.domain.evidence import Attestation, EvidenceCategory

NORTHSTAR_DIR = Path(__file__).resolve().parents[1] / "cases" / "northstar-internal-developer-platform"
CREATED_AT = "2026-09-12T00:00:00Z"


def _pack():
    return load_case_pack(NORTHSTAR_DIR, created_at=CREATED_AT)


def test_pack_loads_and_is_the_expected_case():
    case, _, _ = _pack()
    assert case.id == "northstar-internal-developer-platform"
    assert case.ask.amount_gbp == 4_000_000
    assert case.ask.duration == "18 months"
    assert "do_nothing" in case.alternatives
    # The four candidate strategies plus do_nothing plus the staged/hybrid path.
    assert len(case.alternatives) == 6


def test_every_northstar_specific_item_is_attested_authored():
    """The load-bearing privacy/honesty property of this case. `REAL` is
    permitted only on EXTERNAL_REFERENCE items, which cite public work a reader
    can check. Everything else -- including the MEASURED-category scenario
    telemetry -- must be AUTHORED, so the page's attestation badge tells a
    reader which claims are invented."""
    _, items, _ = _pack()
    for item in items:
        if item.attestation is Attestation.REAL:
            assert item.category is EvidenceCategory.EXTERNAL_REFERENCE, item.id
        else:
            assert item.attestation is Attestation.AUTHORED, item.id


def test_no_measured_item_claims_to_be_a_real_observation():
    """`MEASURED` here describes the kind of claim inside the fictional
    scenario, never that anyone measured anything. ADR-003 makes category and
    attestation orthogonal so this is expressible; this test makes it enforced."""
    _, items, _ = _pack()
    measured = [i for i in items if i.category is EvidenceCategory.MEASURED]
    assert measured, "the scenario baseline should exist"
    for item in measured:
        assert item.attestation is Attestation.AUTHORED, item.id
        assert "SYNTHETIC SCENARIO INPUT" in item.claim, item.id
        assert "fictional" in item.source.lower(), item.id


def test_every_epistemic_category_is_represented():
    """A case that is evidence-rich in only one category would not exercise the
    taxonomy the instrument exists to preserve."""
    _, items, _ = _pack()
    counts = Counter(i.category for i in items)
    for category in EvidenceCategory:
        assert counts[category] > 0, f"no {category.value} items"


def test_unknowns_cover_the_questions_the_decision_turns_on():
    _, items, _ = _pack()
    unknown_claims = " ".join(
        i.claim.lower() for i in items if i.category is EvidenceCategory.UNKNOWN
    )
    for topic in ("attribution", "adoption", "opportunity cost", "operating cost"):
        assert topic in unknown_claims, topic


def test_cross_references_resolve():
    """`supports` / `contradicts` are the structural carriers of this case's
    tensions. A dangling reference would silently drop one."""
    _, items, _ = _pack()
    ids = {i.id for i in items}
    for item in items:
        for ref in list(item.supports) + list(item.contradicts):
            assert ref in ids, f"{item.id} references unknown {ref}"


def test_the_ai_evidence_genuinely_disagrees_with_itself():
    """The case must not quietly settle the AI question in either direction.
    At least one pair of REAL external items must contradict each other."""
    _, items, _ = _pack()
    by_id = {i.id: i for i in items}
    real_conflicts = [
        (i.id, ref)
        for i in items
        if i.attestation is Attestation.REAL
        for ref in i.contradicts
        if by_id[ref].attestation is Attestation.REAL
    ]
    assert real_conflicts


def test_every_declared_assumption_has_a_matching_assumption_evidence_item():
    """An assumption that moves the economics but never appears in the ledger
    is invisible to the committee and to the page."""
    _, items, assumptions = _pack()
    assumption_claims = " ".join(
        i.claim for i in items if i.category is EvidenceCategory.ASSUMPTION
    )
    for assumption in assumptions:
        assert assumption.id in assumption_claims, assumption.id


def test_every_assumption_declares_a_real_range():
    _, _, assumptions = _pack()
    assert assumptions
    for a in assumptions:
        lo, hi = a.range
        assert lo < hi, a.id
        assert lo <= a.value <= hi, a.id
