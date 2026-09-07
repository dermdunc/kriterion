import json
from pathlib import Path

from kriterion.domain.case import Ask, DecisionCase
from kriterion.report.html import render_report

CREATED_AT = "2026-09-06T00:00:00Z"


def _case(case_id="coding-agent-rollout", **overrides):
    kwargs = dict(
        id=case_id,
        created_at=CREATED_AT,
        title="Enterprise coding-agent rollout",
        sponsor="CTO",
        decision_owner="cio",
        decision_requested="Should we fund a staged rollout?",
        ask=Ask(type="staged_funding", amount_gbp=4_200_000, duration="24 months"),
        alternatives=["do_nothing", "limited_pilot"],
        deadline="2026-12-01",
    )
    kwargs.update(overrides)
    return DecisionCase(**kwargs)


def _evidence(id, category, attestation="AUTHORED", claim="a claim", contradicts=None):
    return {
        "id": id, "created_at": CREATED_AT, "category": category, "attestation": attestation,
        "claim": claim, "source": "src", "period": "2026-Q1", "strength": "HIGH",
        "supports": [], "contradicts": contradicts or [],
    }


def _position(member, refs=("ev-001",), blocking_unknowns=None, recommendation="DEFER"):
    return {
        "id": f"p-{member}", "created_at": CREATED_AT, "member": member, "phase": "initial",
        "recommendation": recommendation, "confidence_band": "MEDIUM",
        "key_reasons": [{"text": "a reason", "evidence_refs": list(refs)}],
        "blocking_unknowns": blocking_unknowns or [],
    }


def test_render_report_with_no_artifacts_renders_all_five_sections(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    html = render_report(_case(), run_dir)
    for heading in ["1. The decision", "2. Evidence map", "3. Independent positions", "4. What changed minds", "5. Decision record"]:
        assert heading in html
    assert "AUTHORED FIXTURE CASE" in html


def test_evidence_columns_group_by_category(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    ledger = {
        "id": "l", "created_at": CREATED_AT,
        "items": [
            _evidence("ev-001", "MEASURED"),
            _evidence("ev-002", "ASSUMPTION"),
            _evidence("ev-003", "UNKNOWN"),
        ],
    }
    (run_dir / "ledger.frozen.json").write_text(json.dumps(ledger))
    html = render_report(_case(), run_dir)

    supported_idx = html.index("SUPPORTED")
    assumed_idx = html.index("ASSUMED")
    unknown_idx = html.index("UNKNOWN")
    ev1_idx = html.index("ev-001")
    ev2_idx = html.index("ev-002")
    ev3_idx = html.index("ev-003")
    assert supported_idx < ev1_idx < assumed_idx
    assert assumed_idx < ev2_idx < unknown_idx
    assert unknown_idx < ev3_idx


def test_contradicting_evidence_item_flagged(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    ledger = {
        "id": "l", "created_at": CREATED_AT,
        "items": [_evidence("ev-001", "MEASURED", contradicts=["ev-002"])],
    }
    (run_dir / "ledger.frozen.json").write_text(json.dumps(ledger))
    html = render_report(_case(), run_dir)
    assert "contradicts: ev-002" in html
    assert "contradicted" in html


def test_position_reason_without_citation_flagged_unsupported(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    (run_dir / "positions_initial.json").write_text(json.dumps([_position("cfo", refs=())]))
    html = render_report(_case(), run_dir)
    assert "no citation" in html


def test_staged_funding_ladder_only_for_coding_agent_rollout(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    econ = {
        "id": "e", "created_at": CREATED_AT, "case_id": "coding-agent-rollout", "discount_rate": 0.1,
        "npv_low_gbp": -1.0, "npv_mid_gbp": 1.0, "npv_high_gbp": 2.0, "payback_years": None,
        "peak_funding_gbp": 0.0, "tornado": [], "avoided_loss_low_gbp": None, "avoided_loss_high_gbp": None,
    }
    (run_dir / "economics.json").write_text(json.dumps(econ))
    html = render_report(_case(), run_dir)
    assert "Staged-funding ladder" in html

    other_run_dir = tmp_path / "run-2"
    other_run_dir.mkdir()
    econ_other = dict(econ, case_id="invisible-ai-control-plane")
    (other_run_dir / "economics.json").write_text(json.dumps(econ_other))
    html_other = render_report(_case(case_id="invisible-ai-control-plane"), other_run_dir)
    assert "Staged-funding ladder" not in html_other


def test_avoided_loss_rendered_beside_not_inside_npv_table(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    econ = {
        "id": "e", "created_at": CREATED_AT, "case_id": "invisible-ai-control-plane", "discount_rate": 0.1,
        "npv_low_gbp": -1.0, "npv_mid_gbp": -1.0, "npv_high_gbp": -1.0, "payback_years": None,
        "peak_funding_gbp": 0.0, "tornado": [], "avoided_loss_low_gbp": 500_000.0, "avoided_loss_high_gbp": 900_000.0,
    }
    (run_dir / "economics.json").write_text(json.dumps(econ))
    html = render_report(_case(case_id="invisible-ai-control-plane"), run_dir)
    assert "Avoided-loss forecast" in html
    npv_table_end = html.index("</table>")
    avoided_loss_idx = html.index("Avoided-loss forecast")
    assert avoided_loss_idx > npv_table_end  # beside, not inside, the NPV table


def test_belief_update_no_change_shows_held_reason_from_revised_blocking_unknown(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    update = {
        "id": "u", "created_at": CREATED_AT, "member": "ciso", "initial_position": "DEFER",
        "initial_confidence": "MEDIUM", "revised_position": "DEFER", "revised_confidence": "MEDIUM",
        "change_type": "no_change", "trigger_refs": [], "stated_reason": "", "drift_flags": [],
    }
    (run_dir / "belief_updates.json").write_text(json.dumps([update]))
    (run_dir / "positions_revised.json").write_text(
        json.dumps([_position("ciso", blocking_unknowns=["unanswered security question"])])
    )
    html = render_report(_case(), run_dir)
    assert "held position: unanswered security question" in html


def test_belief_update_evidence_driven_shows_transition_and_refs(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    update = {
        "id": "u", "created_at": CREATED_AT, "member": "cfo", "initial_position": "PILOT",
        "initial_confidence": "MEDIUM", "revised_position": "DEFER", "revised_confidence": "MEDIUM",
        "change_type": "evidence_driven", "trigger_refs": ["ev-027"], "stated_reason": "the study said so",
        "drift_flags": [],
    }
    (run_dir / "belief_updates.json").write_text(json.dumps([update]))
    html = render_report(_case(), run_dir)
    assert "PILOT" in html and "DEFER" in html
    assert "ev-027" in html
    assert "the study said so" in html


def test_recommendation_renders_dissent_and_not_a_decision_banner(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    rec = {
        "id": "r", "created_at": CREATED_AT, "action": "DEFER", "amount": 4_200_000, "duration": "24 months",
        "conditions": ["a condition"], "stop_conditions": [], "unresolved_unknowns": ["an unknown"],
        "confidence_band": "MEDIUM",
        "strongest_dissent": {"verbatim": "I disagree strongly", "refs": ["ev-001"]},
    }
    (run_dir / "recommendation.json").write_text(json.dumps(rec))
    html = render_report(_case(), run_dir)
    assert "SYNTHETIC RECOMMENDATION — NOT A DECISION" in html
    assert "STRONGEST DISSENT" in html
    assert "I disagree strongly" in html


def test_baseline_b_result_renders_when_no_recommendation(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    b_result = {
        "modal_action": "DEFER", "modal_action_count": 3, "total_positions": 5,
        "unioned_blocking_unknowns": ["thing X"],
        "minority_positions": [_position("ciso", recommendation="REJECT")],
    }
    (run_dir / "baseline_b_result.json").write_text(json.dumps(b_result))
    html = render_report(_case(), run_dir)
    assert "no synthesized recommendation" in html
    assert "ciso: REJECT" in html


def test_human_decision_and_outcome_contract_render(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    decision = {
        "id": "d", "created_at": CREATED_AT, "action": "PILOT", "disposition": "accept",
        "overrides": [], "rationale": "looks fine", "owner": "cio", "decided_at": "2026-09-06",
    }
    (run_dir / "human_decision.json").write_text(json.dumps(decision))
    contract = {
        "id": "c", "created_at": CREATED_AT, "baseline_date": "2026-09-06",
        "measures": [{"name": "uplift", "baseline": "0%", "target": "10%", "source_ref": "ev-001"}],
        "owner": "cio", "review_date": "2026-12-01", "next_decision": "scale or stop",
        "kill_criteria": ["uplift below 5%"],
    }
    (run_dir / "outcome_contract.json").write_text(json.dumps(contract))
    html = render_report(_case(), run_dir)
    assert "HUMAN DECISION" in html
    assert "looks fine" in html
    assert "scale or stop" in html
    assert "uplift below 5%" in html


def test_model_generated_text_is_html_escaped(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    ledger = {
        "id": "l", "created_at": CREATED_AT,
        "items": [_evidence("ev-001", "MEASURED", claim="<script>alert(1)</script> & \"quoted\"")],
    }
    (run_dir / "ledger.frozen.json").write_text(json.dumps(ledger))
    html = render_report(_case(), run_dir)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
