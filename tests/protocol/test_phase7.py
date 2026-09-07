import json

from kriterion.domain.committee import Challenge, CommitteePosition, KeyReason, RoleCharter
from kriterion.domain.economics import EconomicsResult
from kriterion.domain.case import Ask, DecisionCase
from kriterion.domain.enums import ChallengeType, CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase
from kriterion.executors.base import Executor, ExecutorResult
from kriterion.protocol.phases import run_phase7_revised_assessment

VALID_REVISION = json.dumps(
    {
        "revised_position": "DEFER",
        "revised_confidence": "LOW",
        "change_type": "evidence_driven",
        "trigger_refs": ["ev-027"],
        "stated_reason": "New study changes things.",
        "blocking_unknowns": ["still unresolved"],
    }
)


class _ScriptedExecutor(Executor):
    def __init__(self, responses):
        self._responses = list(responses)
        self.call_count = 0
        self.prompts = []

    def complete(self, prompt, *, system=None, fmt="json", seed=0):
        self.prompts.append(prompt)
        text = self._responses[self.call_count]
        self.call_count += 1
        return ExecutorResult(text=text, elapsed_seconds=0.01, model="fake", seed=seed)


def _initial_position():
    return CommitteePosition(
        id="p-cfo", created_at="2026-09-05T00:00:00Z", member=CommitteeSeat.CFO,
        phase=PositionPhase.INITIAL, recommendation=DecisionAction.PILOT,
        confidence_band=ConfidenceBand.MEDIUM, key_reasons=[KeyReason(text="r", evidence_refs=[])],
    )


def _charter():
    return RoleCharter(
        id="charter-cfo", created_at="2026-09-05T00:00:00Z", version="v1", seat=CommitteeSeat.CFO,
        objective="o", concerns=["c"], required_evidence=["ev-027"], decision_rights=["d"],
        standard_challenges=["s"], failure_modes=["f"], forbidden=["x"],
    )


def _case():
    return DecisionCase(
        id="case-a", created_at="2026-09-05T00:00:00Z", title="t", sponsor="s", decision_owner="o",
        decision_requested="d", ask=Ask(type="staged_funding", amount_gbp=1, duration="1 month"),
        alternatives=["do_nothing", "pilot"],
    )


def _ledger_item():
    from kriterion.domain.evidence import Attestation, EvidenceCategory, EvidenceItem, Strength

    return EvidenceItem(
        id="ev-027", created_at="2026-09-05T00:00:00Z", category=EvidenceCategory.MEASURED,
        attestation=Attestation.AUTHORED, claim="c", source="s", period="p", strength=Strength.HIGH,
    )


def _economics():
    return EconomicsResult(
        id="econ", created_at="2026-09-05T00:00:00Z", case_id="case-a", discount_rate=0.1,
        npv_low_gbp=-1.0, npv_mid_gbp=1.0, npv_high_gbp=2.0, payback_years=1.0,
        peak_funding_gbp=0.0, tornado=[],
    )


def _challenge():
    return Challenge(
        id="ch:premortem-cto", created_at="2026-09-05T00:00:00Z", type=ChallengeType.PREMORTEM,
        author_role=CommitteeSeat.CTO, content="Some premortem text.", evidence_refs=[],
    )


def test_phase7_succeeds_and_carries_forward_blocking_unknowns():
    executor = _ScriptedExecutor([VALID_REVISION])
    outcome = run_phase7_revised_assessment(
        executor, _initial_position(), _charter(), _case(), [_ledger_item()], [_challenge()], _economics(),
        new_evidence_ids=set(), seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert outcome.status == "ok"
    assert outcome.revised_position.recommendation == DecisionAction.DEFER
    assert outcome.revised_position.blocking_unknowns == ["still unresolved"]
    assert outcome.belief_update.change_type.value == "evidence_driven"


def test_phase7_prompt_shows_the_real_challenge_id_not_just_its_type():
    """Real bug caught live in the 2026-09-07 P1 perturbation batch: the
    prompt told the model a ch: id was a valid trigger (the fix above) but
    never showed the REAL id string, only "[premortem] <content>" -- a
    model that wanted to cite it had to guess, and guessed the abbreviated
    "ch:premortem" (no member suffix), which parse_revision_response then
    rejected as an unknown id every single time, well-formed JSON and all.
    """
    executor = _ScriptedExecutor([VALID_REVISION])
    run_phase7_revised_assessment(
        executor, _initial_position(), _charter(), _case(), [_ledger_item()], [_challenge()], _economics(),
        new_evidence_ids=set(), seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert "ch:premortem-cto" in executor.prompts[0]


def test_phase7_accepts_a_challenge_artifact_as_a_trigger_ref():
    """Real bug caught live in the 2026-09-06 pre-registered batch: a
    ch:-prefixed challenge artifact id is a valid trigger_ref per
    docs/v0-plan.md Section 5's own example, but was previously rejected
    as an unknown evidence id -- known_ids only ever included the ledger."""
    revision = json.dumps({
        "revised_position": "DEFER", "revised_confidence": "LOW", "change_type": "argument_driven",
        "trigger_refs": ["ch:premortem-cto"], "stated_reason": "The premortem changed my mind.",
        "blocking_unknowns": [],
    })
    executor = _ScriptedExecutor([revision])
    outcome = run_phase7_revised_assessment(
        executor, _initial_position(), _charter(), _case(), [_ledger_item()], [_challenge()], _economics(),
        new_evidence_ids=set(), seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert outcome.status == "ok"
    assert outcome.belief_update.trigger_refs == ["ch:premortem-cto"]


def test_phase7_populates_drift_flags_via_derivation_not_left_default_empty():
    """runs/caseC-condC-s2 exposed that BeliefUpdate.drift_flags was never
    computed anywhere despite the field existing -- citing only stale
    (non-injected, non-challenge) evidence should get retrofit-flagged."""
    executor = _ScriptedExecutor([VALID_REVISION])  # cites ev-027, not in new_evidence_ids
    outcome = run_phase7_revised_assessment(
        executor, _initial_position(), _charter(), _case(), [_ledger_item()], [_challenge()], _economics(),
        new_evidence_ids=set(), seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert outcome.status == "ok"
    assert "retrofit" in [f.value for f in outcome.belief_update.drift_flags]


def test_phase7_abstains_after_two_failures():
    executor = _ScriptedExecutor(["not json", "still not json"])
    outcome = run_phase7_revised_assessment(
        executor, _initial_position(), _charter(), _case(), [_ledger_item()], [_challenge()], _economics(),
        new_evidence_ids=set(), seed=0, created_at="2026-09-05T00:00:00Z", run_id="run-1",
    )
    assert outcome.status == "abstained_error"
    assert outcome.revised_position is None
