"""Deserialises run-artifact JSON (written by cli.py's to_dict(...) calls)
back into domain records, so the eval harness works with real typed objects
instead of raw dicts. One place for this, not reimplemented per scorer call
site.
"""

from __future__ import annotations

from kriterion.domain.committee import BeliefUpdate, CommitteePosition, KeyReason
from kriterion.domain.decision import Dissent, SyntheticRecommendation
from kriterion.domain.economics import EconomicsResult, TornadoEntry
from kriterion.domain.enums import ChangeType, CommitteeSeat, ConfidenceBand, DecisionAction, PositionPhase
from kriterion.domain.evidence import Attestation, EvidenceCategory, EvidenceItem, Strength
from kriterion.protocol.aggregate import BaselineBResult


def load_economics(data: dict) -> EconomicsResult:
    return EconomicsResult(
        id=data["id"], created_at=data["created_at"], case_id=data["case_id"],
        discount_rate=data["discount_rate"], npv_low_gbp=data["npv_low_gbp"],
        npv_mid_gbp=data["npv_mid_gbp"], npv_high_gbp=data["npv_high_gbp"],
        payback_years=data["payback_years"], peak_funding_gbp=data["peak_funding_gbp"],
        tornado=[TornadoEntry(assumption_id=t["assumption_id"], npv_swing_gbp=t["npv_swing_gbp"]) for t in data["tornado"]],
        avoided_loss_low_gbp=data.get("avoided_loss_low_gbp"),
        avoided_loss_high_gbp=data.get("avoided_loss_high_gbp"),
    )


def load_evidence_item(data: dict) -> EvidenceItem:
    return EvidenceItem(
        id=data["id"], created_at=data["created_at"], category=EvidenceCategory(data["category"]),
        attestation=Attestation(data["attestation"]), claim=data["claim"], source=data["source"],
        period=data["period"], strength=Strength(data["strength"]),
        supports=data.get("supports", []), contradicts=data.get("contradicts", []),
    )


def load_position(data: dict) -> CommitteePosition:
    return CommitteePosition(
        id=data["id"], created_at=data["created_at"], member=CommitteeSeat(data["member"]),
        phase=PositionPhase(data["phase"]), recommendation=DecisionAction(data["recommendation"]),
        confidence_band=ConfidenceBand(data["confidence_band"]),
        key_reasons=[KeyReason(text=r["text"], evidence_refs=r["evidence_refs"]) for r in data.get("key_reasons", [])],
        blocking_unknowns=data.get("blocking_unknowns", []),
        distrusted_assumption=data.get("distrusted_assumption"),
    )


def load_belief_update(data: dict) -> BeliefUpdate:
    return BeliefUpdate(
        id=data["id"], created_at=data["created_at"], member=CommitteeSeat(data["member"]),
        initial_position=DecisionAction(data["initial_position"]), initial_confidence=ConfidenceBand(data["initial_confidence"]),
        revised_position=DecisionAction(data["revised_position"]), revised_confidence=ConfidenceBand(data["revised_confidence"]),
        change_type=ChangeType(data["change_type"]), trigger_refs=data.get("trigger_refs", []),
        stated_reason=data.get("stated_reason", ""), drift_flags=data.get("drift_flags", []),
    )


def load_recommendation(data: dict) -> SyntheticRecommendation:
    return SyntheticRecommendation(
        id=data["id"], created_at=data["created_at"], action=DecisionAction(data["action"]),
        amount=data["amount"], duration=data["duration"], conditions=data.get("conditions", []),
        stop_conditions=data.get("stop_conditions", []),
        strongest_dissent=Dissent(
            verbatim=data["strongest_dissent"]["verbatim"], refs=data["strongest_dissent"].get("refs", [])
        ),
        unresolved_unknowns=data.get("unresolved_unknowns", []),
        confidence_band=ConfidenceBand(data["confidence_band"]),
    )


def load_baseline_b_result(data: dict) -> BaselineBResult:
    return BaselineBResult(
        modal_action=DecisionAction(data["modal_action"]),
        modal_action_count=data["modal_action_count"],
        total_positions=data["total_positions"],
        unioned_blocking_unknowns=data.get("unioned_blocking_unknowns", []),
        minority_positions=[load_position(p) for p in data.get("minority_positions", [])],
    )
