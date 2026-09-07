"""ADR-004's ruling, made mechanically checkable: "No member sees any
tally, count, distribution or majority signal at any point before synthesis
(phase 8)." Structural checks, not behavioural ones — phase 5 and phase 7's
own source must never reference the sealed tally at all, and the anonymised
position text they build must never include a count.
"""

from pathlib import Path

PROTOCOL_DIR = Path(__file__).parent.parent.parent / "src" / "kriterion" / "protocol"


def test_challenge_module_never_references_the_sealed_tally():
    # The word "tally" legitimately appears in this module's own docstring
    # explaining the invariant it enforces — the mechanical guarantee is
    # that the actual SealedTally type/constructor is never imported or
    # called here, not that the word never appears in a comment.
    text = (PROTOCOL_DIR / "challenge.py").read_text()
    assert "SealedTally" not in text
    assert "seal_phase4_tally" not in text


def test_phases_module_phase7_function_never_references_sealed_tally():
    text = (PROTOCOL_DIR / "phases.py").read_text()
    # SealedTally/seal_phase4_tally are DEFINED in this file (phase 4) but
    # must never appear inside run_phase7_revised_assessment's own body.
    phase7_start = text.index("def run_phase7_revised_assessment")
    phase7_body = text[phase7_start:]
    assert "SealedTally" not in phase7_body
    assert "sealed_tally" not in phase7_body.lower()


def test_anonymized_position_text_lists_each_position_without_a_count():
    from kriterion.domain.committee import CommitteePosition, KeyReason
    from kriterion.domain.enums import CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase
    from kriterion.protocol.anonymize import anonymize_positions

    positions = [
        CommitteePosition(
            id=f"p-{seat.value}", created_at="2026-09-05T00:00:00Z", member=seat,
            phase=PositionPhase.INITIAL, recommendation=DecisionAction.PILOT,
            confidence_band=ConfidenceBand.MEDIUM,
            key_reasons=[KeyReason(text="reason", evidence_refs=[])],
        )
        for seat in [CommitteeSeat.CFO, CommitteeSeat.CTO, CommitteeSeat.CISO]
    ]
    mapping, text = anonymize_positions(positions, seed=0)

    # No real seat name leaks into the anonymised text.
    for seat in mapping:
        assert seat.value not in text.lower()
    # No aggregate count/tally phrase appears — each position stands alone.
    for forbidden in ["3 of", "count:", "tally", "majority", "unanimous"]:
        assert forbidden not in text.lower()
