"""One decision state; everything else is a view (ADR-011).

This module assembles the authoritative Kriterion records for a single case +
run into one read-only projection, and derives — deterministically, with no
model call — the handful of summary values a decision-maker needs that are not
themselves stored fields (capital at risk, the dominant sensitivity, whether
the NPV sign flips inside the stated ranges).

It introduces **no second data model**: every field either *is* a domain
record loaded from a committed artifact, or is a pure function of those
records. Nothing here writes anything.

Two rules this module exists to enforce:

1. Derived values are computed here, once, so a renderer can never invent one
   in prose. `narrative.py` re-resolves every rendered claim against this
   object and refuses to publish a page whose text does not match.
2. Absence stays absence. A missing artifact produces `None` plus an explicit
   status string saying *why* it is missing — never a zero, a False, or a
   softened default. `EvidenceRequest`s that were never persisted are
   distinguishable from a run where nobody asked for evidence.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

from kriterion.decisions import FUNDING_ACTIONS, load_human_decision, load_outcome_contract
from kriterion.domain.case import DecisionCase
from kriterion.domain.committee import BeliefUpdate, CommitteePosition, EvidenceRequest
from kriterion.domain.decision import HumanDecision, OutcomeContract, SyntheticRecommendation
from kriterion.domain.economics import EconomicsResult
from kriterion.domain.enums import CommitteeSeat, DecisionAction
from kriterion.domain.evidence import Assumption, EvidenceCategory, EvidenceItem
from kriterion.evals.run_loader import (
    load_belief_update,
    load_economics,
    load_evidence_item,
    load_evidence_request,
    load_position,
    load_recommendation,
)

# How each case's tornado parameter names map back to the case pack's own
# Assumption ids. The tornado stores the engine's keyword-parameter name; the
# assumption record (with its range, owner and evidence strength) is keyed by
# the case-pack id. Without this map a renderer would have to guess, and a
# guess here is exactly how "the dominant assumption" gets misattributed.
_PARAM_TO_ASSUMPTION_ID: dict[str, dict[str, str]] = {}


def _build_param_maps() -> None:
    from kriterion.economics import case_flows

    _PARAM_TO_ASSUMPTION_ID["coding-agent-rollout"] = {
        param: a_id for a_id, param in case_flows.ASSUMPTION_ID_TO_PARAM.items()
    }
    # Case C's economics function overrides exactly one parameter.
    _PARAM_TO_ASSUMPTION_ID["invisible-ai-control-plane"] = {
        "ongoing_annual_cost_gbp": "as-ongoing-annual-cost-gbp",
    }


_build_param_maps()


# The staged-funding ladder's amounts. These are named constants in
# economics/case_flows.py — the same constants the cash-flow model actually
# spends — imported rather than re-typed, so the ladder shown to a human and
# the ladder inside the NPV cannot diverge. Giving the ladder a first-class
# case-pack schema remains named follow-up work (docs/next-actions.md); until
# then this is honestly a code constant, and the page says so.
def _stage_ladder(case_id: str) -> list[dict[str, Any]]:
    from kriterion.economics import case_flows

    if case_id != "coding-agent-rollout":
        return []
    return [
        {"name": "Discovery", "amount_gbp": float(case_flows.DISCOVERY_GBP)},
        {"name": "Pilot", "amount_gbp": float(case_flows.PILOT_GBP)},
        {"name": "Targeted scale", "amount_gbp": float(case_flows.TARGETED_SCALE_GBP)},
    ]


@dataclass(frozen=True, kw_only=True)
class SeatView:
    """Everything one committee seat actually recorded, in one place.

    `evidence_requests` is the seat's own persisted `EvidenceRequest` list.
    An empty list means one of two very different things, which
    `DecisionState.evidence_requests_recorded` disambiguates: either nobody
    asked, or the run predates the artifact.
    """

    seat: CommitteeSeat
    initial: CommitteePosition | None = None
    revised: CommitteePosition | None = None
    belief_update: BeliefUpdate | None = None
    evidence_requests: list[EvidenceRequest] = field(default_factory=list)

    @property
    def current_position(self) -> CommitteePosition | None:
        """The seat's latest recorded position — revised if a revision phase
        ran, otherwise the initial one. Never a blend of the two."""
        return self.revised or self.initial


@dataclass(frozen=True, kw_only=True)
class AssuranceImport:
    """A committed `kriterion assurance import` output, read back as data.

    Deliberately *not* an import of `kriterion.assurance`: this reads the
    Kriterion-side JSON that command already writes, so no module outside the
    adapter package ever learns the producer's document format (ADR-007, and
    the structural test in tests/assurance/).
    """

    summary: dict[str, Any]
    items: list[EvidenceItem]

    @property
    def items_by_id(self) -> dict[str, EvidenceItem]:
        return {item.id: item for item in self.items}


_REQUIRED_SUMMARY_KEYS = (
    "capability_name",
    "capability_version",
    "decision_state",
    "declared_decision_state",
    "stale",
    "critical_failure_count",
    "result_count",
    "uncovered_count",
)


class DecisionStateError(ValueError):
    """A required artifact is missing or malformed. Never silently tolerated:
    a decision page built on a half-loaded state is the failure mode this
    whole module exists to prevent."""


@dataclass(frozen=True, kw_only=True)
class DecisionState:
    run_id: str
    case: DecisionCase
    assumptions: list[Assumption]
    evidence: list[EvidenceItem]
    economics: EconomicsResult | None
    seats: list[SeatView]
    recommendation: SyntheticRecommendation | None
    human_decision: HumanDecision | None
    outcome_contract: OutcomeContract | None
    assurance: AssuranceImport | None
    ledger_version: int | None
    ledger_fingerprint: str | None
    evidence_requests_recorded: bool

    # -- lookups ---------------------------------------------------------

    @cached_property
    def evidence_by_id(self) -> dict[str, EvidenceItem]:
        return {item.id: item for item in self.evidence}

    @cached_property
    def assumptions_by_id(self) -> dict[str, Assumption]:
        return {a.id: a for a in self.assumptions}

    @cached_property
    def seats_by_id(self) -> dict[str, SeatView]:
        return {s.seat.value: s for s in self.seats}

    def evidence_in(self, *categories: EvidenceCategory) -> list[EvidenceItem]:
        wanted = set(categories)
        return [item for item in self.evidence if item.category in wanted]

    # -- derived values, computed once, never re-derived in a template ----

    @cached_property
    def capital_at_risk_gbp(self) -> float:
        """What the synthetic recommendation would actually put at risk.

        A `SyntheticRecommendation` carries an `amount` even when its action
        commits nothing — the synthesiser echoes the ask. Rendering that
        amount as "capital at risk" under a DEFER would be a decision-fidelity
        failure, so the funding-action test (the same set `kriterion
        validate-run` uses) decides it here, once.
        """
        if self.recommendation is None:
            return 0.0
        if self.recommendation.action in FUNDING_ACTIONS:
            return float(self.recommendation.amount)
        return 0.0

    @cached_property
    def capital_at_risk_basis(self) -> str:
        if self.recommendation is None:
            return "No synthetic recommendation was recorded for this run."
        action = self.recommendation.action.value
        if self.recommendation.action in FUNDING_ACTIONS:
            return f"{action} is a funding action, so the recommended amount is capital at risk."
        return (
            f"{action} commits no funding. The recommendation record still carries the full "
            f"ask as its amount field; that is the ask, not a commitment."
        )

    @cached_property
    def human_capital_commitment(self) -> str:
        """What the *human* decision commits, stated separately from what the
        machine suggested.

        Found by exercising the lifecycle: with a synthetic DEFER and a human
        PILOT both recorded, one "capital at risk" figure on the page reads as
        the decision's exposure while actually describing only the machine's
        suggestion. Two actors, two statements.

        `HumanDecision` carries an action but no amount, so the committed sum
        genuinely is not recorded anywhere. Saying so is the honest answer;
        reusing the recommendation's amount would attribute a number to a human
        who never wrote one.
        """
        if self.human_decision is None:
            return "No human decision has been recorded, so nothing is committed."
        action = self.human_decision.action.value
        if self.human_decision.action in FUNDING_ACTIONS:
            return (
                f"{action} authorises funding. The human-decision record carries an action but "
                "no amount, so the committed sum is not recorded on it; what binds this decision "
                "is the outcome contract's measures and review date."
            )
        return f"{action} commits no funding."

    @cached_property
    def primary_sensitivity_param(self) -> str | None:
        if self.economics is None or not self.economics.tornado:
            return None
        return max(self.economics.tornado, key=lambda t: abs(t.npv_swing_gbp)).assumption_id

    @cached_property
    def primary_sensitivity_swing_gbp(self) -> float | None:
        if self.economics is None or not self.economics.tornado:
            return None
        return max(self.economics.tornado, key=lambda t: abs(t.npv_swing_gbp)).npv_swing_gbp

    @cached_property
    def primary_sensitivity_assumption(self) -> Assumption | None:
        param = self.primary_sensitivity_param
        if param is None:
            return None
        a_id = _PARAM_TO_ASSUMPTION_ID.get(self.case.id, {}).get(param)
        if a_id is None:
            return None
        return self.assumptions_by_id.get(a_id)

    @cached_property
    def primary_uncertainty_label(self) -> str:
        """One name for the dominant uncertainty, used everywhere it appears.

        The economics artifact stores the engine's parameter name; the case
        pack stores the assumption id. Quoting one in the headline and the
        other in the interpretation is how the same fact ends up looking like
        two, so the label is resolved once, here.
        """
        assumption = self.primary_sensitivity_assumption
        if assumption is not None:
            return assumption.id
        return self.primary_sensitivity_param or "no ranked assumption"

    @cached_property
    def tornado_rows(self) -> list[dict[str, Any]]:
        """The tornado, joined to the case pack's own assumption records.

        A swing figure without the evidence strength behind it invites the
        reader to treat a well-evidenced parameter and a guess as equally
        solid; they are the same arithmetic and very different decisions.

        Ordered by magnitude here rather than trusting the artifact's stored
        order. The engine already sorts that way, so this is a no-op on real
        data — but an artifact that did not would make the headline dominant
        uncertainty and the table's own first row name different parameters
        while the caption claimed "widest first": one fact, two answers, which
        is the failure this whole increment is about. Found by feeding the
        projection a deliberately unsorted tornado.
        """
        if self.economics is None:
            return []
        rows: list[dict[str, Any]] = []
        ordered = sorted(self.economics.tornado, key=lambda e: abs(e.npv_swing_gbp), reverse=True)
        for entry in ordered:
            a_id = _PARAM_TO_ASSUMPTION_ID.get(self.case.id, {}).get(entry.assumption_id)
            assumption = self.assumptions_by_id.get(a_id) if a_id else None
            rows.append(
                {
                    "parameter": entry.assumption_id,
                    "assumption_id": a_id or "not declared as a ranged assumption",
                    "evidence_strength": (
                        assumption.evidence_strength.value if assumption is not None else "not recorded"
                    ),
                    "owner": assumption.owner if assumption is not None else "not recorded",
                    "swing_gbp": entry.npv_swing_gbp,
                }
            )
        return rows

    @cached_property
    def npv_sign_flips(self) -> bool | None:
        """Whether the stated plausible ranges span value-destroying and
        value-creating outcomes. `None` when no economics were computed —
        not False, which would read as "the sign is stable"."""
        if self.economics is None:
            return None
        return self.economics.npv_low_gbp < 0 < self.economics.npv_high_gbp

    @cached_property
    def economics_interpretation(self) -> str:
        """One sentence, assembled from canonical fields only.

        Binding this string (rather than writing it in the template) means
        `narrative.py` can recompute it and refuse a page whose economics
        sentence has been edited by hand.
        """
        if self.economics is None:
            return "No economics were computed for this run."
        assumption = self.primary_sensitivity_assumption
        name = self.primary_uncertainty_label
        strength = f" ({assumption.evidence_strength.value} evidence)" if assumption is not None else ""
        if self.npv_sign_flips:
            shape = (
                "The sign of the outcome flips inside the stated plausible ranges, so the "
                "case is not yet decidable on the numbers alone."
            )
        elif self.economics.npv_high_gbp <= 0:
            shape = "Every scenario in the stated plausible ranges is value-destroying."
        else:
            shape = "Every scenario in the stated plausible ranges is value-creating."
        return (
            f"{shape} The widest single swing comes from {name}{strength}, which is therefore "
            "the assumption to buy evidence about before buying scale."
        )

    @cached_property
    def dominance_claim_scope(self) -> str:
        """The tornado only ranks what the case pack declared as a ranged
        Assumption. Saying so is not a caveat, it is the claim's actual
        scope — treating 'deterministic' as 'complete' is the exact error
        this instrument exists to expose."""
        n = len(self.economics.tornado) if self.economics is not None else 0
        return (
            f"Ranked over the {n} assumption(s) the case pack declares with an explicit range "
            "and owner. Structural inputs that are code constants rather than ranged Assumption "
            "records are outside this ranking."
        )

    @cached_property
    def stages(self) -> list[dict[str, Any]]:
        return _stage_ladder(self.case.id)

    @cached_property
    def decision_vocabulary(self) -> list[str]:
        return [a.value for a in DecisionAction]

    @cached_property
    def unknown_evidence(self) -> list[EvidenceItem]:
        return self.evidence_in(EvidenceCategory.UNKNOWN)

    @cached_property
    def evidence_count(self) -> int:
        return len(self.evidence)

    @cached_property
    def unknown_count(self) -> int:
        return len(self.unknown_evidence)

    @cached_property
    def seat_count(self) -> int:
        return len(self.seats)

    @cached_property
    def blocking_unknowns_by_seat(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for seat in self.seats:
            position = seat.current_position
            if position is not None and position.blocking_unknowns:
                out[seat.seat.value] = list(position.blocking_unknowns)
        return out

    @cached_property
    def stored_evidence_request_count(self) -> int:
        return sum(len(s.evidence_requests) for s in self.seats)

    @cached_property
    def evidence_request_status(self) -> str:
        """Three genuinely different states, never collapsed into one."""
        if not self.evidence_requests_recorded:
            return (
                "This run predates the evidence_requests.json artifact, so no per-seat "
                "'what would change my mind' record was stored. What each seat left "
                "unresolved is shown instead, from its own recorded position."
            )
        if self.stored_evidence_request_count == 0:
            return (
                "This run recorded the evidence_requests.json artifact and no seat asked "
                "for further evidence. That is a finding, not a gap."
            )
        return (
            f"{self.stored_evidence_request_count} per-seat evidence request(s) were recorded "
            "for this run, each with the condition its author said would change their position."
        )

    @cached_property
    def human_decision_status(self) -> str:
        if self.human_decision is None:
            return (
                "No human decision has been recorded for this case. Kriterion will not "
                "record one on an accountable human's behalf."
            )
        return (
            f"Recorded by {self.human_decision.owner or 'an unnamed owner'} on "
            f"{self.human_decision.decided_at or 'an unrecorded date'}."
        )

    @cached_property
    def outcome_contract_status(self) -> str:
        if self.outcome_contract is not None:
            return "An outcome contract exists for this decision."
        if self.human_decision is None:
            return (
                "No outcome contract exists, because no human decision has been recorded. "
                "A contract is required only once a human commits funding."
            )
        if self.human_decision.action in FUNDING_ACTIONS:
            return (
                "The recorded human decision is a funding action with no outcome contract. "
                "kriterion validate-run reports this as a governance violation (P0-09)."
            )
        return (
            f"The recorded human decision ({self.human_decision.action.value}) commits no "
            "funding, so no outcome contract is required."
        )

    @cached_property
    def stage_ladder_status(self) -> str:
        """Kriterion records what capital each stage would spend, and it
        records what evidence each seat wants. It does **not** record which
        stage a given piece of evidence unlocks. Inventing that mapping for a
        nicer-looking diagram would be exactly the kind of invented structure
        this increment exists to stop, so the gap is stated instead."""
        if not self.stages:
            return "This case declares no staged-funding ladder."
        return (
            "The ladder's amounts are code constants in the cash-flow model, not case-pack "
            "schema, and no record links a named evidence requirement to the stage it would "
            "unlock. Both are stated here rather than filled in by inference."
        )

    @cached_property
    def assurance_unknown_count(self) -> int:
        if self.assurance is None:
            return 0
        return sum(1 for i in self.assurance.items if i.category is EvidenceCategory.UNKNOWN)

    @cached_property
    def assurance_summary_caveat(self) -> str:
        """What the producer's critical-failure count does *not* count.

        Raised by reading the finished page as a CISO: a summary line saying
        zero critical failures, above a list of a dozen items, reads as "every
        check passed". The envelope behind this one records a non-gating
        failure and a check that returned no verdict at all. Softening by
        omission is still softening, so the summary says what it covers.
        """
        if self.assurance is None:
            return "No assurance evidence was imported for this case."
        total = len(self.assurance.items)
        return (
            "The critical-failure count is the producer's own classification, and counts only "
            f"failures it judged critical. It is not a count of checks that did not pass. Of the "
            f"{total} items this import produced, {self.assurance_unknown_count} are recorded as "
            "epistemically unknown, meaning not measured rather than passed. Every item is listed "
            "below with the adapter's own wording; read them rather than the count."
        )

    @cached_property
    def next_step(self) -> str:
        """What actually has to happen next, named as a concrete act by a
        named party. A decision instrument that stops at "here is the
        analysis" leaves the most important field blank."""
        if self.human_decision is None:
            return (
                f"The accountable decision owner for this case ({self.case.decision_owner}) "
                "records a decision against this run with `kriterion decide`, stating whether "
                "they accept, modify or reject the machine's suggestion and why. Until that "
                "happens the run is undecided, and Kriterion reports it as undecided."
            )
        if self.human_decision.action in FUNDING_ACTIONS and self.outcome_contract is None:
            return (
                "The recorded decision commits funding, so `kriterion contract` must record the "
                "outcome contract (measures, baseline, review date, kill criteria) before "
                "`kriterion validate-run` will pass."
            )
        if self.outcome_contract is not None:
            return (
                f"At the review date recorded in the outcome contract ({self.outcome_contract.review_date}), "
                "the recorded measures are compared against what actually happened, and the next "
                f"decision ({self.outcome_contract.next_decision}) is taken on that evidence."
            )
        return (
            "The recorded decision commits no funding. The next step is whatever evidence the "
            "seats above said they still need."
        )

    @cached_property
    def assurance_status(self) -> str:
        if self.assurance is None:
            return "No assurance evidence was imported for this case."
        return (
            "Imported through the ADR-007 adapter after this deliberation ran. The committee "
            "below never saw it: it is not in this run's frozen ledger."
        )

    @cached_property
    def derived(self) -> dict[str, Any]:
        """Every derived value, addressable by `derived.<name>` so the
        narrative checker can resolve exactly what a template rendered."""
        return {
            "capital_at_risk_gbp": self.capital_at_risk_gbp,
            "capital_at_risk_basis": self.capital_at_risk_basis,
            "human_capital_commitment": self.human_capital_commitment,
            "primary_sensitivity_param": self.primary_sensitivity_param,
            "primary_uncertainty_label": self.primary_uncertainty_label,
            "tornado_rows": self.tornado_rows,
            "primary_sensitivity_swing_gbp": self.primary_sensitivity_swing_gbp,
            "economics_interpretation": self.economics_interpretation,
            "dominance_claim_scope": self.dominance_claim_scope,
            "stages": self.stages,
            "stage_ladder_status": self.stage_ladder_status,
            "decision_vocabulary": self.decision_vocabulary,
            "evidence_request_status": self.evidence_request_status,
            "human_decision_status": self.human_decision_status,
            "outcome_contract_status": self.outcome_contract_status,
            "next_step": self.next_step,
            "assurance_status": self.assurance_status,
            "assurance_summary_caveat": self.assurance_summary_caveat,
            "assurance_unknown_count": self.assurance_unknown_count,
            "stored_evidence_request_count": self.stored_evidence_request_count,
            "evidence_count": len(self.evidence),
            "unknown_count": len(self.unknown_evidence),
            "seat_count": len(self.seats),
            "run_id": self.run_id,
        }


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _read_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise DecisionStateError(f"{path} is not valid JSON: {exc}") from exc


def _require_list(value: Any, label: str) -> list[Any]:
    """A run artifact that should be a list and is not must refuse, not be
    iterated. Iterating a dict yields its *keys*, so a positions file written
    as an object feeds bare strings into a loader and surfaces as
    `TypeError: string indices must be integers` — a traceback, not a refusal.
    """
    if not isinstance(value, list):
        raise DecisionStateError(f"{label} must be a JSON list, got {type(value).__name__}")
    return value


def _detail(exc: Exception) -> str:
    return f"missing field {exc}" if isinstance(exc, KeyError) else str(exc)


def _load_each(loader, entries: Any, label: str) -> list[Any]:
    """Deserialise a list of run records, converting every shape failure into
    a `DecisionStateError`.

    This boundary exists because the V1 adversarial review found the assurance
    adapter letting malformed documents escape as bare `AttributeError`, and
    the first adversarial pass over *this* module found the same thing here:
    all eleven malformed-artifact cases tried (a ledger with no `items`, an
    unknown `EvidenceCategory`, a `DecisionAction` of `APPROVE`, an evidence
    request with no `would_change`, a positions file written as an object, ...)
    produced tracebacks rather than controlled refusals. A traceback is not a
    refusal, and "unknown" has to stay distinguishable from "crashed".
    """
    out = []
    for index, entry in enumerate(_require_list(entries, label)):
        try:
            out.append(loader(entry))
        except DecisionStateError:
            raise
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise DecisionStateError(f"{label}[{index}] is malformed: {_detail(exc)}") from exc
    return out


def _guard(thunk, label: str):
    """Same boundary, for the record loaders that read their own file."""
    try:
        return thunk()
    except DecisionStateError:
        raise
    except json.JSONDecodeError as exc:
        raise DecisionStateError(f"{label} is not valid JSON: {exc}") from exc
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise DecisionStateError(f"{label} is malformed: {_detail(exc)}") from exc


def _load_one(loader, data: Any, label: str):
    if not isinstance(data, dict):
        raise DecisionStateError(f"{label} must be a JSON object, got {type(data).__name__}")
    try:
        return loader(data)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise DecisionStateError(f"{label} is malformed: {_detail(exc)}") from exc


def load_assurance_import(path: Path) -> AssuranceImport:
    """Read a committed `kriterion assurance import --out` payload.

    Strict about the fields the page's claims rest on, for the same reason
    the adapter itself is (ADR-009): a missing `decision_state` must be a
    refusal, never a blank that renders as "fine".
    """
    data = _read_json(path)
    if data is None:
        raise DecisionStateError(f"no assurance import payload at {path}")
    if not isinstance(data, dict):
        raise DecisionStateError(f"{path} must contain a JSON object")
    summary = data.get("summary")
    if not isinstance(summary, dict):
        raise DecisionStateError(f"{path} has no 'summary' object")
    missing = [k for k in _REQUIRED_SUMMARY_KEYS if k not in summary]
    if missing:
        raise DecisionStateError(f"{path} summary is missing required field(s): {', '.join(missing)}")
    if "items" not in data:
        raise DecisionStateError(f"{path} has no 'items' list")
    items = _load_each(load_evidence_item, data["items"], f"{path}: items")
    return AssuranceImport(summary=summary, items=items)


def load_decision_state(
    *,
    case_dir: Path,
    run_dir: Path,
    created_at: str,
    assurance_import_path: Path | None = None,
) -> DecisionState:
    """Assemble the decision state for one case + one run.

    `created_at` is supplied by the caller rather than read from the clock so
    that rendering is reproducible: the same artifacts must always produce the
    same page.
    """
    from kriterion.casepack import CasePackError, load_case_pack

    if not run_dir.is_dir():
        raise DecisionStateError(f"run directory not found: {run_dir}")
    try:
        case, _case_items, assumptions = load_case_pack(case_dir, created_at=created_at)
    except CasePackError as exc:
        raise DecisionStateError(str(exc)) from exc

    ledger_data = _read_json(run_dir / "ledger.frozen.json")
    if ledger_data is None:
        raise DecisionStateError(
            f"{run_dir} has no ledger.frozen.json — a decision page without the frozen "
            "evidence it rests on would be a narrative, not a projection"
        )
    if not isinstance(ledger_data, dict) or "items" not in ledger_data:
        raise DecisionStateError(
            f"{run_dir / 'ledger.frozen.json'} declares no items[] — the absence of evidence "
            "cannot be inferred from a missing field, so this is a refusal rather than an "
            "empty ledger"
        )
    evidence = _load_each(load_evidence_item, ledger_data["items"], "ledger.frozen.json: items")

    econ_data = _read_json(run_dir / "economics.json")
    economics = _load_one(load_economics, econ_data, "economics.json") if econ_data else None

    initial = _load_each(
        load_position, _read_json(run_dir / "positions_initial.json") or [], "positions_initial.json"
    )
    revised = _load_each(
        load_position, _read_json(run_dir / "positions_revised.json") or [], "positions_revised.json"
    )
    updates = _load_each(
        load_belief_update, _read_json(run_dir / "belief_updates.json") or [], "belief_updates.json"
    )

    requests_path = run_dir / "evidence_requests.json"
    requests_recorded = requests_path.is_file()
    requests = _load_each(
        load_evidence_request, _read_json(requests_path) or [], "evidence_requests.json"
    )

    initial_by_seat = {p.member: p for p in initial}
    revised_by_seat = {p.member: p for p in revised}
    updates_by_seat = {u.member: u for u in updates}
    requests_by_seat: dict[CommitteeSeat, list[EvidenceRequest]] = {}
    for request in requests:
        requests_by_seat.setdefault(request.member, []).append(request)

    seat_order = [s for s in CommitteeSeat]
    present = set(initial_by_seat) | set(revised_by_seat) | set(updates_by_seat) | set(requests_by_seat)
    seats = [
        SeatView(
            seat=seat,
            initial=initial_by_seat.get(seat),
            revised=revised_by_seat.get(seat),
            belief_update=updates_by_seat.get(seat),
            evidence_requests=requests_by_seat.get(seat, []),
        )
        for seat in seat_order
        if seat in present
    ]

    rec_data = _read_json(run_dir / "recommendation.json")
    recommendation = (
        _load_one(load_recommendation, rec_data, "recommendation.json") if rec_data else None
    )

    assurance = (
        load_assurance_import(assurance_import_path) if assurance_import_path is not None else None
    )

    return DecisionState(
        run_id=run_dir.name,
        case=case,
        assumptions=assumptions,
        evidence=evidence,
        economics=economics,
        seats=seats,
        recommendation=recommendation,
        human_decision=_guard(lambda: load_human_decision(run_dir), "human_decision.json"),
        outcome_contract=_guard(lambda: load_outcome_contract(run_dir), "outcome_contract.json"),
        assurance=assurance,
        ledger_version=ledger_data.get("version"),
        ledger_fingerprint=ledger_data.get("fingerprint"),
        evidence_requests_recorded=requests_recorded,
    )


__all__ = [
    "AssuranceImport",
    "DecisionState",
    "DecisionStateError",
    "SeatView",
    "load_assurance_import",
    "load_decision_state",
]
