import json

from kriterion.domain.enums import CommitteeSeat, DecisionAction, PositionPhase
from kriterion.domain.evidence import Attestation, EvidenceCategory, EvidenceItem, Strength
from kriterion.executors.base import Executor, ExecutorResult
from kriterion.protocol.phases import run_phase3_independent_assessment, seal_phase4_tally

VALID_JSON = json.dumps(
    {"recommendation": "PILOT", "confidence_band": "MEDIUM", "key_reasons": [], "evidence_requests": []}
)


class _ScriptedExecutor(Executor):
    """Returns each entry in `responses` in order, one per call."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.call_count = 0
        self.prompts_sent: list[str] = []

    def complete(self, prompt, *, system=None, fmt="json", seed=0):
        self.prompts_sent.append(prompt)
        text = self._responses[self.call_count]
        self.call_count += 1
        return ExecutorResult(text=text, elapsed_seconds=0.01, model="fake", seed=seed)


def _charter():
    from kriterion.domain.committee import RoleCharter

    return RoleCharter(
        id="charter-cfo",
        created_at="2026-09-05T00:00:00Z",
        version="v1",
        seat=CommitteeSeat.CFO,
        objective="o",
        concerns=["c"],
        required_evidence=["ev-001"],
        decision_rights=["d"],
        standard_challenges=["s"],
        failure_modes=["f"],
        forbidden=["x"],
    )


def _case():
    from kriterion.domain.case import Ask, DecisionCase

    return DecisionCase(
        id="case-a",
        created_at="2026-09-05T00:00:00Z",
        title="t",
        sponsor="s",
        decision_owner="o",
        decision_requested="d",
        ask=Ask(type="staged_funding", amount_gbp=1, duration="1 month"),
        alternatives=["do_nothing", "pilot"],
    )


def _economics():
    from kriterion.domain.economics import EconomicsResult

    return EconomicsResult(
        id="econ",
        created_at="2026-09-05T00:00:00Z",
        case_id="case-a",
        discount_rate=0.1,
        npv_low_gbp=-1.0,
        npv_mid_gbp=1.0,
        npv_high_gbp=2.0,
        payback_years=1.0,
        peak_funding_gbp=0.0,
        tornado=[],
    )


def _evidence_by_id():
    return {
        "ev-001": EvidenceItem(
            id="ev-001",
            created_at="2026-09-05T00:00:00Z",
            category=EvidenceCategory.MEASURED,
            attestation=Attestation.AUTHORED,
            claim="c",
            source="s",
            period="p",
            strength=Strength.HIGH,
        )
    }


def test_shows_full_ledger_even_when_charter_required_evidence_does_not_match():
    """Regression test for a real bug caught live on Case C: a charter's
    required_evidence lists ids from the case it was authored against.
    On a different case with different ids, the member must still see the
    full ledger, not zero evidence."""
    charter_with_mismatched_ids = _charter()  # required_evidence=["ev-001"]
    other_case_evidence = {
        "ev-101": EvidenceItem(
            id="ev-101", created_at="2026-09-05T00:00:00Z", category=EvidenceCategory.MEASURED,
            attestation=Attestation.AUTHORED, claim="different case entirely", source="s",
            period="p", strength=Strength.HIGH,
        )
    }
    executor = _ScriptedExecutor([VALID_JSON])
    outcome = run_phase3_independent_assessment(
        executor, charter_with_mismatched_ids, _case(), other_case_evidence, _economics(),
        seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert outcome.status == "ok"
    # The prompt actually sent must contain the other case's evidence claim,
    # proving it wasn't filtered down to the (non-matching) required_evidence.
    assert "different case entirely" in executor.prompts_sent[0]


def test_succeeds_on_first_valid_response():
    executor = _ScriptedExecutor([VALID_JSON])
    outcome = run_phase3_independent_assessment(
        executor, _charter(), _case(), _evidence_by_id(), _economics(),
        seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert outcome.status == "ok"
    assert outcome.position.recommendation == DecisionAction.PILOT
    assert executor.call_count == 1


def test_retries_once_then_succeeds():
    executor = _ScriptedExecutor(["not json", VALID_JSON])
    outcome = run_phase3_independent_assessment(
        executor, _charter(), _case(), _evidence_by_id(), _economics(),
        seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert outcome.status == "ok"
    assert executor.call_count == 2


def test_abstains_after_two_failures():
    executor = _ScriptedExecutor(["not json", "still not json"])
    outcome = run_phase3_independent_assessment(
        executor, _charter(), _case(), _evidence_by_id(), _economics(),
        seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert outcome.status == "abstained_error"
    assert outcome.position is None
    assert executor.call_count == 2
    assert len(outcome.raw_attempts) == 2


def test_seal_phase4_tally_counts_ok_outcomes_only():
    from kriterion.domain.committee import CommitteePosition
    from kriterion.domain.enums import ConfidenceBand
    from kriterion.protocol.phases import AssessmentOutcome

    def pos(seat, action):
        return CommitteePosition(
            id=f"p-{seat.value}", created_at="2026-09-05T00:00:00Z", member=seat,
            phase=PositionPhase.INITIAL, recommendation=action,
            confidence_band=ConfidenceBand.MEDIUM,
            key_reasons=[],
        )

    outcomes = [
        AssessmentOutcome(member=CommitteeSeat.CFO, status="ok", position=pos(CommitteeSeat.CFO, DecisionAction.PILOT)),
        AssessmentOutcome(member=CommitteeSeat.CTO, status="ok", position=pos(CommitteeSeat.CTO, DecisionAction.PILOT)),
        AssessmentOutcome(member=CommitteeSeat.CISO, status="abstained_error"),
    ]
    tally = seal_phase4_tally(outcomes)
    assert tally.counts == {"PILOT": 2}
    assert tally.modal_action == "PILOT"
