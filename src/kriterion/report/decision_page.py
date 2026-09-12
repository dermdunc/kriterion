"""The public decision experience, rendered from the decision state (ADR-011).

`docs/index.html` used to be hand-authored narrative checked against the
artifacts by a separate test. This module replaces that arrangement: the page
is now a projection of `DecisionState`, every material value is placed through
`narrative.bind()`, and `narrative.check()` refuses to publish a page whose
text does not re-derive from the record.

Design constraints, in priority order:

1. **Faithful before pretty.** Nothing on this page may be written by hand if
   it can be rendered from a field. Section prose is deliberately free of
   numbers and state vocabulary; the checker enforces that.
2. **Absence is content.** A missing artifact produces an explicit statement
   of what is missing and why, never a blank or a plausible default.
3. **Nothing that is unknown or failing is hidden behind a disclosure.**
   Strong supporting evidence may collapse; unknowns and assurance results
   never do.
4. Semantic HTML, one stylesheet, no JavaScript, no external assets — the same
   constraints `report/html.py` already works under.

`report/html.py` (the per-run research record) is untouched: the committed V0
run reports are frozen research artifacts and a shared renderer would rewrite
them.
"""

from __future__ import annotations

import html as html_lib

from kriterion.decision_state import DecisionState
from kriterion.domain.evidence import EvidenceCategory, Strength
from kriterion.narrative import bind

# The three display groups. Grounded-in-an-observation versus
# modelled/expected versus unknown — the same collapse `report/html.py`
# already uses, kept identical so the two views cannot imply different
# epistemics for the same item.
KNOWN_CATEGORIES = (
    EvidenceCategory.MEASURED,
    EvidenceCategory.EXTERNAL_REFERENCE,
    EvidenceCategory.EXPERT_JUDGMENT,
)
ASSUMED_CATEGORIES = (
    EvidenceCategory.FORECAST,
    EvidenceCategory.ASSUMPTION,
    EvidenceCategory.INFERENCE,
)

_STRENGTH_ORDER = {Strength.HIGH: 0, Strength.MEDIUM: 1, Strength.LOW: 2}


def _esc(value: object) -> str:
    return html_lib.escape(str(value))


def _assumption_format(assumption_id: str) -> tuple[str, str]:
    """(value format, range format) for one assumption id.

    Cash amounts are suffixed `-gbp` by convention in every case pack; the
    rest are fractions. Stated here rather than inferred from magnitude,
    because guessing units from a number is how a rate becomes a currency.
    """
    if assumption_id.endswith("-gbp"):
        return "gbp", "range_gbp"
    return "percent", "range_percent"


def _evidence_card(state: DecisionState, item, *, root: str) -> str:
    path = f"{root}[{item.id}]"
    contradicts = ""
    if item.contradicts:
        contradicts = (
            '<p class="contradicts">Recorded as contradicting '
            + bind(state, f"{path}.contradicts", fmt="list_semi")
            + "</p>"
        )
    return f"""
      <li class="evidence-item" data-evidence-id="{_esc(item.id)}">
        <p class="evidence-head">
          {bind(state, f"{path}.id", tag="code")}
          {bind(state, f"{path}.category", cls="badge category")}
          {bind(state, f"{path}.strength", cls="badge strength")}
          {bind(state, f"{path}.attestation", cls="badge attestation")}
        </p>
        <p class="claim">{bind(state, f"{path}.claim")}</p>
        <p class="source">{bind(state, f"{path}.source")} · {bind(state, f"{path}.period")}</p>
        {contradicts}
      </li>
    """


def _evidence_list(state: DecisionState, items, *, root: str, collapse_below: Strength | None) -> str:
    ordered = sorted(items, key=lambda i: (_STRENGTH_ORDER[i.strength], i.id))
    if collapse_below is None:
        cards = "".join(_evidence_card(state, i, root=root) for i in ordered)
        return f'<ul class="evidence-list">{cards}</ul>'

    threshold = _STRENGTH_ORDER[collapse_below]
    lead = [i for i in ordered if _STRENGTH_ORDER[i.strength] <= threshold]
    rest = [i for i in ordered if _STRENGTH_ORDER[i.strength] > threshold]
    html = f'<ul class="evidence-list">{"".join(_evidence_card(state, i, root=root) for i in lead)}</ul>'
    if rest:
        html += (
            "<details><summary>Remaining items in this group, of lower recorded evidence "
            "strength</summary>"
            f'<ul class="evidence-list">{"".join(_evidence_card(state, i, root=root) for i in rest)}</ul>'
            "</details>"
        )
    return html


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------


def _primary_uncertainty_detail(state: DecisionState) -> str:
    """The dominant assumption's own evidence strength and plausible range.

    Raised by reading the finished page as a CFO: naming the assumption that
    swings the valuation by more than the ask, without saying how well
    evidenced it is, leaves the reader to assume it is solid. The strength is
    the whole point of surfacing it.
    """
    assumption = state.primary_sensitivity_assumption
    if assumption is None:
        return (
            "Engine parameter "
            + bind(state, "primary_sensitivity_param")
            + ", which the case pack does not declare as a ranged assumption"
        )
    path = f"assumptions_by_id[{assumption.id}]"
    value_fmt, range_fmt = _assumption_format(assumption.id)
    return (
        "Recorded evidence strength "
        + bind(state, f"{path}.evidence_strength", fmt="label")
        + ", base value "
        + bind(state, f"{path}.value", fmt=value_fmt)
        + " across a plausible range of "
        + bind(state, f"{path}.range", fmt=range_fmt)
        + ", owned by "
        + bind(state, f"{path}.owner")
        + ". Engine parameter "
        + bind(state, "primary_sensitivity_param")
        + "."
    )


def _headline_economics(state: DecisionState) -> str:
    """Base, downside and upside at the top of the page.

    Raised by reading the finished page as a CIO: the single most
    decision-relevant fact - that the sign flips inside the stated ranges -
    sat four sections below the fold. Same fields, same formatters as the
    economics section, so the two cannot disagree.
    """
    if state.economics is None:
        return ""
    return f"""
        <dl class="snapshot">
          <dt>Base valuation</dt>
          <dd>{bind(state, "economics.npv_mid_gbp", fmt="gbp_millions", cls="headline")}</dd>
          <dt>Downside, every assumption at its pessimistic end</dt>
          <dd>{bind(state, "economics.npv_low_gbp", fmt="gbp_millions", cls="headline")}</dd>
          <dt>Upside, every assumption at its optimistic end</dt>
          <dd>{bind(state, "economics.npv_high_gbp", fmt="gbp_millions", cls="headline")}</dd>
          <dt>What that shape means</dt>
          <dd>{bind(state, "economics_interpretation")}</dd>
        </dl>
        """


def _section_decision(state: DecisionState) -> str:
    if state.recommendation is None:
        rec_block = (
            '<p class="note">No synthetic recommendation was recorded for this run.</p>'
        )
    else:
        rec_block = f"""
        <dl class="snapshot">
          <dt>Synthetic recommendation, machine-generated</dt>
          <dd>{bind(state, "recommendation.action", fmt="label", cls="headline", role="recommendation-action")}</dd>
          <dt>Stated confidence</dt>
          <dd>{bind(state, "recommendation.confidence_band", fmt="label")}</dd>
          <dt>Capital the machine's suggestion would put at risk</dt>
          <dd>{bind(state, "capital_at_risk_gbp", fmt="gbp", cls="headline")}
              <span class="basis">{bind(state, "capital_at_risk_basis")}</span></dd>
          <dt>What the accountable human has committed</dt>
          <dd><span class="basis">{bind(state, "human_capital_commitment")}</span></dd>
          <dt>Dominant uncertainty</dt>
          <dd>{bind(state, "primary_uncertainty_label")}, worth
              {bind(state, "primary_sensitivity_swing_gbp", fmt="gbp_millions")} of swing on the
              base valuation
              <span class="basis">{_primary_uncertainty_detail(state)}</span></dd>
        </dl>
        {_headline_economics(state)}
        """
    return f"""
    <section data-kriterion-role="decision" id="decision" aria-labelledby="h-decision">
      <h2 id="h-decision">The decision</h2>
      <p class="ask">{bind(state, "case.decision_requested", cls="lede")}</p>
      <dl class="snapshot">
        <dt>Amount requested</dt>
        <dd>{bind(state, "case.ask.amount_gbp", fmt="gbp", cls="headline")}
            over {bind(state, "case.ask.duration")}
            ({bind(state, "case.ask.type", fmt="label")})</dd>
        <dt>Sponsor</dt><dd>{bind(state, "case.sponsor")}</dd>
        <dt>Accountable decision owner</dt><dd>{bind(state, "case.decision_owner")}</dd>
        <dt>Decision date sought</dt><dd>{bind(state, "case.deadline")}</dd>
        <dt>Alternatives on the table</dt><dd>{bind(state, "case.alternatives", fmt="list_semi")}</dd>
      </dl>
      {rec_block}
      <p class="note">Kriterion's decision vocabulary has no approval verb, by design:
        {bind(state, "decision_vocabulary", fmt="list_dot", cls="vocab")}</p>
    </section>
    """


def _section_known(state: DecisionState) -> str:
    items = state.evidence_in(*KNOWN_CATEGORIES)
    return f"""
    <section data-kriterion-role="what-we-know" id="known" aria-labelledby="h-known">
      <h2 id="h-known">What we know</h2>
      <p>Every item carries its own epistemic class, its recorded strength, and whether it is an
         observation or an authored fixture. Kriterion never collapses those into one score.</p>
      {_evidence_list(state, items, root="evidence_by_id", collapse_below=Strength.HIGH)}
    </section>
    """


def _section_assumed(state: DecisionState) -> str:
    rows = []
    for assumption in state.assumptions:
        value_fmt, range_fmt = _assumption_format(assumption.id)
        path = f"assumptions_by_id[{assumption.id}]"
        rows.append(
            f"<tr><td>{bind(state, f"{path}.id", tag="code")}</td>"
            f"<td>{bind(state, f'{path}.value', fmt=value_fmt)}</td>"
            f"<td>{bind(state, f'{path}.range', fmt=range_fmt)}</td>"
            f"<td>{bind(state, f'{path}.evidence_strength', fmt='label')}</td>"
            f"<td>{bind(state, f'{path}.owner')}</td></tr>"
        )
    items = state.evidence_in(*ASSUMED_CATEGORIES)
    return f"""
    <section data-kriterion-role="what-we-assume" id="assumed" aria-labelledby="h-assumed">
      <h2 id="h-assumed">What we are assuming</h2>
      <p>Each of these carries an owner and a plausible range, so the economics below can be
         swung across the range rather than quoted as a single confident figure.</p>
      <table>
        <caption>Ranged assumptions declared by the case pack</caption>
        <thead><tr><th>Identifier</th><th>Base value</th><th>Plausible range</th>
          <th>Evidence strength</th><th>Owner</th></tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
      <h3>Modelled and inferred evidence</h3>
      {_evidence_list(state, items, root="evidence_by_id", collapse_below=Strength.MEDIUM)}
    </section>
    """


def _section_unknown(state: DecisionState) -> str:
    return f"""
    <section data-kriterion-role="what-we-do-not-know" id="unknown" aria-labelledby="h-unknown">
      <h2 id="h-unknown">What we do not know</h2>
      <p>These stay open. Nothing here is rendered as a zero, an absence of risk, or a low score,
         and nothing here is collapsed behind a disclosure.</p>
      {_evidence_list(state, state.unknown_evidence, root="evidence_by_id", collapse_below=None)}
    </section>
    """


def _section_economics(state: DecisionState) -> str:
    if state.economics is None:
        body = '<p class="note">No economics were computed for this run.</p>'
    else:
        rows = []
        for index in range(len(state.tornado_rows)):
            row = f"tornado_rows[{index}]"
            rows.append(
                f"<tr><td>{bind(state, f'{row}.assumption_id')}</td>"
                f"<td>{bind(state, f'{row}.parameter')}</td>"
                f"<td>{bind(state, f'{row}.evidence_strength', fmt='label')}</td>"
                f"<td>{bind(state, f'{row}.owner')}</td>"
                f"<td>{bind(state, f'{row}.swing_gbp', fmt='gbp_millions')}</td></tr>"
            )
        body = f"""
        <dl class="snapshot">
          <dt>Base valuation</dt>
          <dd>{bind(state, "economics.npv_mid_gbp", fmt="gbp_millions", cls="headline")}</dd>
          <dt>Downside, every assumption at its pessimistic end</dt>
          <dd>{bind(state, "economics.npv_low_gbp", fmt="gbp_millions", cls="headline")}</dd>
          <dt>Upside, every assumption at its optimistic end</dt>
          <dd>{bind(state, "economics.npv_high_gbp", fmt="gbp_millions", cls="headline")}</dd>
          <dt>Discount rate applied</dt>
          <dd>{bind(state, "economics.discount_rate", fmt="percent")}</dd>
        </dl>
        <p class="insight">{bind(state, "economics_interpretation")}</p>
        <table>
          <caption>One-way sensitivity: the swing on the base valuation between each assumption's
            stated low and high bound, widest first. A negative sign means a higher value of that
            parameter lowers the valuation, so the magnitude is what ranks it.</caption>
          <thead><tr><th>Case-pack assumption</th><th>Engine parameter</th>
            <th>Evidence strength</th><th>Owner</th><th>Swing</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
        <p class="caveat">{bind(state, "dominance_claim_scope")}</p>
        """
    return f"""
    <section data-kriterion-role="economics" id="economics" aria-labelledby="h-economics">
      <h2 id="h-economics">The economics</h2>
      <p>Every figure here is computed by pure code before any model is called, and no model may
         overwrite one. A model may explain these numbers; it may not produce them.</p>
      {body}
    </section>
    """


def _section_assurance(state: DecisionState) -> str:
    if state.assurance is None:
        body = f'<p class="note">{bind(state, "assurance_status")}</p>'
    else:
        reasons = ""
        if state.assurance.summary.get("reasons"):
            entries = "".join(
                f"<li>{bind(state, f'assurance.summary.reasons[{i}]')}</li>"
                for i in range(len(state.assurance.summary["reasons"]))
            )
            reasons = f"<h3>Reasons the producer recorded for that state</h3><ul>{entries}</ul>"
        body = f"""
        <p class="note">{bind(state, "assurance_status")}</p>
        <dl class="snapshot">
          <dt>Capability assessed</dt>
          <dd>{bind(state, "assurance.summary.capability_name")}
              {bind(state, "assurance.summary.capability_version")}</dd>
          <dt>State the producer declared</dt>
          <dd>{bind(state, "assurance.summary.declared_decision_state", fmt="label", cls="headline")}</dd>
          <dt>State Kriterion imported it as</dt>
          <dd>{bind(state, "assurance.summary.decision_state", fmt="label", cls="headline")}</dd>
          <dt>Critical failures declared by the producer</dt>
          <dd>{bind(state, "assurance.summary.critical_failure_count", fmt="count")}
              <span class="basis">{bind(state, "assurance_summary_caveat")}</span></dd>
          <dt>Checks in the envelope</dt>
          <dd>{bind(state, "assurance.summary.result_count", fmt="count")}</dd>
          <dt>Areas the assurance fingerprint does not track</dt>
          <dd>{bind(state, "assurance.summary.uncovered_count", fmt="count")}</dd>
          <dt>Artifact digests captured by the producer</dt>
          <dd>{bind(state, "assurance.summary.digests_captured")}</dd>
        </dl>
        {reasons}
        <h3>Every item this import produced</h3>
        {_evidence_list(state, state.assurance.items, root="assurance.items_by_id", collapse_below=None)}
        """
    return f"""
    <section data-kriterion-role="assurance" id="assurance" aria-labelledby="h-assurance">
      <h2 id="h-assurance">Machine-checkable evidence about the capability itself</h2>
      <p>An external assurance system's own documents, translated into Kriterion evidence by an
         adapter that is allowed to lose detail but never to upgrade a result. Each claim below is
         the adapter's output, quoted.</p>
      {body}
    </section>
    """


def _seat_card(state: DecisionState, seat) -> str:
    seat_id = seat.seat.value
    path = f"seats_by_id[{seat_id}]"
    position_path = f"{path}.revised" if seat.revised is not None else f"{path}.initial"
    position = seat.current_position

    if position is None:
        return (
            f'<article class="seat" data-seat="{_esc(seat_id)}"><h3>'
            + bind(state, f"{path}.seat", fmt="label", actor=seat_id)
            + '</h3><p class="note">This seat recorded no position for this run.</p></article>'
        )

    reasons = "".join(
        f"<li>{bind(state, f'{position_path}.key_reasons[{i}].text', actor=seat_id)}"
        + (
            f' <span class="refs">{bind(state, f"{position_path}.key_reasons[{i}].evidence_refs", fmt="list_semi", actor=seat_id)}</span>'
            if position.key_reasons[i].evidence_refs
            else ' <span class="refs unsupported">no evidence cited</span>'
        )
        + "</li>"
        for i in range(len(position.key_reasons))
    )
    unknowns = "".join(
        f"<li>{bind(state, f'{position_path}.blocking_unknowns[{i}]', actor=seat_id)}</li>"
        for i in range(len(position.blocking_unknowns))
    )
    distrusted = (
        f'<p><span class="field">Assumption this seat least trusts</span> '
        + bind(state, f"{position_path}.distrusted_assumption", actor=seat_id)
        + "</p>"
        if position.distrusted_assumption
        else ""
    )

    if seat.belief_update is None:
        movement = '<p class="note">No revision phase ran for this seat.</p>'
    else:
        movement = f"""
        <p><span class="field">After the challenge round</span>
          {bind(state, f"{path}.belief_update.initial_position", fmt="label", actor=seat_id)}
          &rarr;
          {bind(state, f"{path}.belief_update.revised_position", fmt="label", actor=seat_id)},
          confidence
          {bind(state, f"{path}.belief_update.initial_confidence", fmt="label", actor=seat_id)}
          &rarr;
          {bind(state, f"{path}.belief_update.revised_confidence", fmt="label", actor=seat_id)}
          ({bind(state, f"{path}.belief_update.change_type", fmt="label", actor=seat_id)})</p>
        <p class="stated-reason">{bind(state, f"{path}.belief_update.stated_reason", actor=seat_id)}</p>
        """

    if seat.evidence_requests:
        requests = "".join(
            f"<li><p class=\"asked\">{bind(state, f'{path}.evidence_requests[{i}].description', actor=seat_id)}</p>"
            f"<p class=\"would-change\"><span class=\"field\">Would change this seat's position if</span> "
            f"{bind(state, f'{path}.evidence_requests[{i}].would_change', actor=seat_id)}</p>"
            f"<p class=\"status\"><span class=\"field\">Has that evidence arrived?</span> "
            f"{bind(state, f'{path}.evidence_requests[{i}].status', fmt='label', actor=seat_id)}</p></li>"
            for i in range(len(seat.evidence_requests))
        )
        requests_block = f'<h4>What this seat asked for</h4><ul class="requests">{requests}</ul>'
    else:
        requests_block = (
            '<h4>What this seat asked for</h4><p class="note">'
            + bind(state, "evidence_request_status")
            + "</p>"
        )

    return f"""
      <article class="seat" data-seat="{_esc(seat_id)}">
        <h3>{bind(state, f"{path}.seat", fmt="label", actor=seat_id)}</h3>
        <p class="position">
          <span class="field">Current position</span>
          {bind(state, f"{position_path}.recommendation", fmt="label", cls="headline", actor=seat_id)}
          <span class="field">Confidence</span>
          {bind(state, f"{position_path}.confidence_band", fmt="label", actor=seat_id)}
        </p>
        <h4>Why</h4>
        <ul class="reasons">{reasons or '<li class="note">No reasons recorded.</li>'}</ul>
        <h4>What this seat holds open</h4>
        <ul class="unknowns">{unknowns or '<li class="note">Nothing recorded as blocking.</li>'}</ul>
        {distrusted}
        {requests_block}
        {movement}
      </article>
    """


def _section_perspectives(state: DecisionState) -> str:
    if not state.seats:
        body = '<p class="note">No independent positions were recorded for this run.</p>'
    else:
        body = '<div class="seats">' + "".join(_seat_card(state, s) for s in state.seats) + "</div>"
    return f"""
    <section data-kriterion-role="perspectives" id="perspectives" aria-labelledby="h-perspectives">
      <h2 id="h-perspectives">Where the perspectives agree and disagree</h2>
      <p>Five role-chartered seats assessed the case independently, then faced an anonymised
         challenge round and revised. No seat is shown a tally before synthesis, so agreement
         cannot be manufactured by visible consensus. Kriterion does not invent disagreement
         either: a round in which nothing moves is reported as a round in which nothing moved.</p>
      {body}
    </section>
    """


def _section_what_would_change(state: DecisionState) -> str:
    blocks = [f'<p class="note">{bind(state, "evidence_request_status")}</p>']

    if state.recommendation is not None and state.recommendation.conditions:
        entries = "".join(
            f"<li>{bind(state, f'recommendation.conditions[{i}]')}</li>"
            for i in range(len(state.recommendation.conditions))
        )
        blocks.append(
            "<h3>Conditions the synthetic recommendation records as unmet</h3>"
            f"<ul>{entries}</ul>"
        )
    if state.recommendation is not None and state.recommendation.unresolved_unknowns:
        entries = "".join(
            f"<li>{bind(state, f'recommendation.unresolved_unknowns[{i}]')}</li>"
            for i in range(len(state.recommendation.unresolved_unknowns))
        )
        blocks.append("<h3>Unknowns it records as still open</h3>" f"<ul>{entries}</ul>")

    if state.stages:
        rungs = "".join(
            f"<li>{bind(state, f'stages[{i}].name')}: "
            f"{bind(state, f'stages[{i}].amount_gbp', fmt='gbp')}</li>"
            for i in range(len(state.stages))
        )
        blocks.append(
            "<h3>What each further stage would cost</h3>"
            f'<ol class="ladder">{rungs}</ol>'
            f'<p class="caveat">{bind(state, "stage_ladder_status")}</p>'
        )

    return f"""
    <section data-kriterion-role="what-would-change" id="what-would-change"
             aria-labelledby="h-change">
      <h2 id="h-change">What would change this decision</h2>
      <p>Per-seat answers sit with each seat above. This is the decision-level view: what the
         synthesised recommendation itself records as outstanding, and what buying the next
         tranche of evidence would cost.</p>
      {"".join(blocks)}
    </section>
    """


def _section_recommendation(state: DecisionState) -> str:
    if state.recommendation is None:
        body = '<p class="note">No synthetic recommendation was recorded for this run.</p>'
    else:
        refs = (
            f' <span class="refs">{bind(state, "recommendation.strongest_dissent.refs", fmt="list_semi")}</span>'
            if state.recommendation.strongest_dissent.refs
            else ""
        )
        stop = ""
        if state.recommendation.stop_conditions:
            entries = "".join(
                f"<li>{bind(state, f'recommendation.stop_conditions[{i}]')}</li>"
                for i in range(len(state.recommendation.stop_conditions))
            )
            stop = f"<h3>Stop conditions</h3><ul>{entries}</ul>"
        body = f"""
        <dl class="snapshot">
          <dt>Action</dt>
          <dd>{bind(state, "recommendation.action", fmt="label", cls="headline")}</dd>
          <dt>Amount named in the recommendation record</dt>
          <dd>{bind(state, "recommendation.amount", fmt="gbp")} over
              {bind(state, "recommendation.duration")}</dd>
          <dt>Capital actually at risk under this action</dt>
          <dd>{bind(state, "capital_at_risk_gbp", fmt="gbp")} &mdash;
              {bind(state, "capital_at_risk_basis")}</dd>
        </dl>
        <blockquote class="dissent">
          <h3>Strongest preserved dissent, quoted</h3>
          <p>{bind(state, "recommendation.strongest_dissent.verbatim")}{refs}</p>
        </blockquote>
        {stop}
        """
    return f"""
    <section data-kriterion-role="synthetic-recommendation" id="recommendation"
             aria-labelledby="h-rec">
      <h2 id="h-rec">Synthetic recommendation</h2>
      <p class="machine-banner">Machine-generated. This is not a decision, and Kriterion never
         treats it as one.</p>
      {body}
    </section>
    """


def _section_human_decision(state: DecisionState) -> str:
    if state.human_decision is None:
        body = f'<p class="empty-state">{bind(state, "human_decision_status")}</p>'
    else:
        overrides = ""
        if state.human_decision.overrides:
            entries = "".join(
                f"<li>{bind(state, f'human_decision.overrides[{i}]')}</li>"
                for i in range(len(state.human_decision.overrides))
            )
            overrides = f"<h3>Overrides</h3><ul>{entries}</ul>"
        body = f"""
        <dl class="snapshot">
          <dt>Action taken</dt>
          <dd>{bind(state, "human_decision.action", fmt="label", cls="headline")}</dd>
          <dt>Disposition toward the machine's suggestion</dt>
          <dd>{bind(state, "human_decision.disposition", fmt="label")}</dd>
          <dt>Accountable owner</dt><dd>{bind(state, "human_decision.owner")}</dd>
          <dt>Recorded on</dt><dd>{bind(state, "human_decision.decided_at")}</dd>
          <dt>What this commits</dt>
          <dd>{bind(state, "human_capital_commitment")}</dd>
        </dl>
        <p class="rationale">{bind(state, "human_decision.rationale")}</p>
        {overrides}
        """
    return f"""
    <section data-kriterion-role="human-decision" id="human-decision" aria-labelledby="h-human">
      <h2 id="h-human">Human decision</h2>
      <p>Kept structurally separate from the machine's suggestion, in a different record type and
         a different file. An agent may not write this one.</p>
      {body}
      <h3>What happens next</h3>
      <p class="next-step">{bind(state, "next_step")}</p>
    </section>
    """


def _section_outcome_contract(state: DecisionState) -> str:
    if state.outcome_contract is None:
        body = f'<p class="empty-state">{bind(state, "outcome_contract_status")}</p>'
    else:
        measures = "".join(
            f"<li>{bind(state, f'outcome_contract.measures[{i}].name')}: "
            f"{bind(state, f'outcome_contract.measures[{i}].baseline')} &rarr; "
            f"{bind(state, f'outcome_contract.measures[{i}].target')} "
            f"({bind(state, f"outcome_contract.measures[{i}].source_ref", tag="code")})</li>"
            for i, m in enumerate(state.outcome_contract.measures)
        )
        kill = "".join(
            f"<li>{bind(state, f'outcome_contract.kill_criteria[{i}]')}</li>"
            for i in range(len(state.outcome_contract.kill_criteria))
        )
        body = f"""
        <dl class="snapshot">
          <dt>Baseline date</dt><dd>{bind(state, "outcome_contract.baseline_date")}</dd>
          <dt>Review date</dt><dd>{bind(state, "outcome_contract.review_date")}</dd>
          <dt>Owner</dt><dd>{bind(state, "outcome_contract.owner")}</dd>
          <dt>Next decision due</dt><dd>{bind(state, "outcome_contract.next_decision")}</dd>
        </dl>
        <h3>Measures</h3><ul>{measures}</ul>
        {"<h3>Kill criteria</h3><ul>" + kill + "</ul>" if kill else ""}
        """
    return f"""
    <section data-kriterion-role="outcome-contract" id="outcome-contract"
             aria-labelledby="h-contract">
      <h2 id="h-contract">Outcome contract</h2>
      <p>What a funded decision commits to measuring, by when, and what would end it. Kriterion
         refuses to validate a funded run without one.</p>
      {body}
    </section>
    """


def _section_provenance(state: DecisionState) -> str:
    return f"""
    <section data-kriterion-role="provenance" id="provenance" aria-labelledby="h-provenance">
      <h2 id="h-provenance">How this page was produced</h2>
      <p>This page is generated. It is a projection of one run's committed artifacts, and every
         value on it carries the state path it was rendered from; a build that cannot re-derive a
         statement from the record refuses to publish.</p>
      <dl class="snapshot">
        <dt>Run rendered</dt><dd>{bind(state, "run_id", tag="code")}</dd>
        <dt>Case</dt><dd>{bind(state, "case.id", tag="code")}</dd>
        <dt>Frozen ledger version</dt><dd>{bind(state, "ledger_version", fmt="count")}</dd>
        <dt>Ledger fingerprint</dt><dd>{bind(state, "ledger_fingerprint", tag="code")}</dd>
        <dt>Evidence items in this ledger</dt><dd>{bind(state, "evidence_count", fmt="count")}</dd>
        <dt>Items recorded as unknown</dt><dd>{bind(state, "unknown_count", fmt="count")}</dd>
        <dt>Case realism</dt><dd>{bind(state, "case.case_realism", fmt="label")}</dd>
      </dl>
      <p>The research behind the instrument, including a pre-registered result that did not go the
         way its authors expected, is preserved separately in
         <a href="lab.html">Kriterion Lab</a>. The per-run decision record for this run is
         <a href="reports/decision-record.html">also rendered</a>, and the source is
         <a href="https://github.com/dermdunc/kriterion">on GitHub</a>.</p>
    </section>
    """


_STYLE = """
  :root {
    color-scheme: light dark;
    --bg: #fff; --fg: #1a1a1a; --muted: #5a5a5a; --border: #dcdcdc;
    --card: #f6f6f6; --accent: #2a4d8f; --warn-bg: #fff3cd; --warn-fg: #5f4a00;
    --alert-bg: #fdeaea; --alert-fg: #7a1f1f;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #161616; --fg: #ededed; --muted: #a8a8a8; --border: #3a3a3a;
            --card: #212121; --accent: #8fb0ff; --warn-bg: #3a3212; --warn-fg: #e8d27a;
            --alert-bg: #3a1f1f; --alert-fg: #f0a8a8; }
  }
  * { box-sizing: border-box; }
  body { background: var(--bg); color: var(--fg); line-height: 1.6;
         font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
         max-width: 56rem; margin: 0 auto; padding: 2rem 1.25rem 5rem; }
  h1 { margin-bottom: 0.2rem; }
  .tagline { color: var(--muted); font-size: 1.1rem; margin-top: 0; }
  .banner { background: var(--warn-bg); color: var(--warn-fg); padding: 0.6rem 1rem;
            border-radius: 0.4rem; font-weight: 600; margin-bottom: 2rem; }
  nav ol { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 0.75rem;
           font-size: 0.9rem; }
  section { border-top: 1px solid var(--border); margin-top: 2.75rem; padding-top: 1.25rem; }
  h2 { color: var(--accent); margin-top: 0.5rem; }
  h3 { margin-bottom: 0.3rem; font-size: 1.05rem; }
  h4 { margin-bottom: 0.2rem; font-size: 0.85rem; text-transform: uppercase;
       letter-spacing: 0.06em; color: var(--muted); }
  .lede { font-size: 1.15rem; font-weight: 600; }
  .snapshot { background: var(--card); border: 1px solid var(--border); border-radius: 0.5rem;
              padding: 1rem 1.25rem; margin: 1.25rem 0; }
  .snapshot dt { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em;
                 color: var(--muted); margin-top: 0.8rem; }
  .snapshot dt:first-child { margin-top: 0; }
  .snapshot dd { margin: 0.15rem 0 0; }
  .headline { font-size: 1.2rem; font-weight: 700; }
  .basis { display: block; color: var(--muted); font-size: 0.9rem; }
  .badge { display: inline-block; font-size: 0.7rem; letter-spacing: 0.05em; padding: 0.1rem 0.5rem;
           border: 1px solid var(--border); border-radius: 0.8rem; background: var(--bg);
           margin-right: 0.25rem; }
  .evidence-list { list-style: none; padding: 0; }
  .evidence-item { background: var(--card); border: 1px solid var(--border);
                   border-radius: 0.5rem; padding: 0.75rem 1rem; margin-bottom: 0.6rem; }
  .evidence-item p { margin: 0.25rem 0; }
  .evidence-head code { font-size: 0.8rem; color: var(--muted); }
  .source, .refs, .status, .caveat, .note { color: var(--muted); font-size: 0.88rem; }
  .contradicts { color: var(--alert-fg); font-size: 0.88rem; }
  .refs.unsupported { color: var(--alert-fg); }
  table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
  caption { text-align: left; color: var(--muted); font-size: 0.88rem; padding-bottom: 0.4rem; }
  th, td { border: 1px solid var(--border); padding: 0.4rem 0.65rem; text-align: left;
           vertical-align: top; }
  th { background: var(--card); }
  .insight { background: var(--card); border-left: 4px solid var(--accent);
             padding: 0.85rem 1rem; margin: 1rem 0; }
  .seats { display: grid; gap: 1rem; }
  .seat { border: 1px solid var(--border); border-radius: 0.5rem; padding: 1rem 1.25rem; }
  .seat .field { display: inline-block; font-size: 0.72rem; text-transform: uppercase;
                 letter-spacing: 0.05em; color: var(--muted); margin-right: 0.35rem; }
  .requests { list-style: none; padding: 0; }
  .requests li { border-left: 3px solid var(--accent); padding-left: 0.8rem; margin-bottom: 0.8rem; }
  .would-change { font-weight: 600; }
  .machine-banner { background: var(--warn-bg); color: var(--warn-fg); padding: 0.5rem 1rem;
                    border-radius: 0.4rem; font-weight: 600; }
  .dissent { background: var(--alert-bg); color: var(--alert-fg); border-radius: 0.5rem;
             padding: 0.85rem 1.1rem; margin: 1rem 0; border-left: 4px solid currentColor; }
  .empty-state { border: 2px dashed var(--border); border-radius: 0.5rem; padding: 1rem 1.25rem; }
  .ladder { padding-left: 1.2rem; }
  details summary { cursor: pointer; color: var(--accent); margin: 0.5rem 0; }
  footer { margin-top: 3rem; border-top: 1px solid var(--border); padding-top: 1.25rem;
           color: var(--muted); font-size: 0.9rem; }
  a { color: var(--accent); }
"""


def render_decision_page(state: DecisionState) -> str:
    """Render the public decision experience. Pure: same state, same bytes."""
    sections = [
        _section_decision(state),
        _section_known(state),
        _section_assumed(state),
        _section_unknown(state),
        _section_economics(state),
        _section_assurance(state),
        _section_perspectives(state),
        _section_what_would_change(state),
        _section_recommendation(state),
        _section_human_decision(state),
        _section_outcome_contract(state),
        _section_provenance(state),
    ]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kriterion: {_esc(state.case.title)}</title>
<meta name="description" content="An evidence-backed decision instrument for uncertain technology investments.">
<style>{_STYLE}</style>
</head>
<body>
<p class="banner">{bind(state, "case.case_realism", fmt="label")} &mdash; this case, its evidence
  and its assurance documents are authored fixtures. The committee text is real local-model
  output and the arithmetic is real.</p>

<h1>Kriterion</h1>
<p class="tagline">An evidence-backed decision instrument for uncertain technology investments.</p>
<p>Kriterion makes what a decision actually rests on explicit: what is known, what is assumed,
   what remains unknown, which assumption dominates the money, where informed perspectives
   disagree, what evidence would move them, and how much capital the current uncertainty
   justifies. The machine supplies analysis and challenge. A human remains accountable for the
   decision.</p>

<nav aria-label="Sections">
  <ol>
    <li><a href="#decision">The decision</a></li>
    <li><a href="#known">What we know</a></li>
    <li><a href="#assumed">What we are assuming</a></li>
    <li><a href="#unknown">What we do not know</a></li>
    <li><a href="#economics">The economics</a></li>
    <li><a href="#assurance">Capability assurance</a></li>
    <li><a href="#perspectives">Perspectives</a></li>
    <li><a href="#what-would-change">What would change this</a></li>
    <li><a href="#recommendation">Synthetic recommendation</a></li>
    <li><a href="#human-decision">Human decision</a></li>
    <li><a href="#outcome-contract">Outcome contract</a></li>
    <li><a href="#provenance">How this was produced</a></li>
  </ol>
</nav>
{"".join(sections)}
<footer>
  <p>Kriterion is a Hekton factory-output project. Deterministic figures are computed by code;
     the narrative around them is generated from the same records and mechanically re-derived
     before publication.</p>
</footer>
</body>
</html>
"""


__all__ = ["render_decision_page"]
