"""kriterion report: one static HTML file per run (docs/v0-plan.md Section 11).

Five views in demo order: the decision, the evidence map, independent
positions (+ the numbers), what changed minds, the decision record. Stdlib
templating only -- no JS build, no server, printable, self-contained (no
external assets). The debate transcript itself is deliberately not a view:
raw phase artifacts (challenges.json, narrative.txt) stay in the run
directory for the technically curious, per Section 11's own framing that
agent theatre does not get the hero slot.

Every section is opportunistic, matching evals/harness.py's own pattern:
a condition/run that lacks an artifact (Baseline B has no belief updates or
synthesized recommendation; Baseline A has one collapsed position, not five)
renders an honest "not recorded for this run" note rather than a missing or
broken section.
"""

from __future__ import annotations

import html as html_lib
import json
from pathlib import Path

from kriterion.decisions import load_human_decision, load_outcome_contract
from kriterion.domain.case import DecisionCase
from kriterion.domain.committee import BeliefUpdate, CommitteePosition
from kriterion.domain.decision import HumanDecision, OutcomeContract, SyntheticRecommendation
from kriterion.domain.economics import EconomicsResult
from kriterion.domain.enums import ChangeType
from kriterion.domain.evidence import Attestation, EvidenceCategory, EvidenceItem
from kriterion.evals.run_loader import (
    load_baseline_b_result,
    load_belief_update,
    load_economics,
    load_evidence_item,
    load_position,
    load_recommendation,
)
from kriterion.protocol.aggregate import BaselineBResult

# Judgment call, stated rather than left implicit (no such grouping is
# defined anywhere in docs/v0-plan.md): the 7-category epistemic taxonomy
# collapses to the plan's 3 display columns by how directly each category is
# grounded in an observation versus a model/expectation of the world.
EVIDENCE_COLUMNS = [
    ("SUPPORTED", {EvidenceCategory.MEASURED, EvidenceCategory.EXTERNAL_REFERENCE, EvidenceCategory.EXPERT_JUDGMENT}),
    ("ASSUMED", {EvidenceCategory.FORECAST, EvidenceCategory.ASSUMPTION, EvidenceCategory.INFERENCE}),
    ("UNKNOWN", {EvidenceCategory.UNKNOWN}),
]

# V0's only staged_funding ask (docs/v0-plan.md Section 8) -- Case C's ask is
# a plain capital_investment with no stages. Sourced from the same constants
# economics/case_flows.py already defines for Case A's own cash-flow model;
# duplicated here as display-only figures rather than importing Case A's
# private cash-flow constants into a report module every condition/case
# shares, mirroring evals/harness.py's own per-case-id dict pattern
# (GOLDEN_ECONOMICS, REAL_INJECTION_ID).
STAGE_LADDER_GBP = {
    "coding-agent-rollout": [
        ("Discovery", 50_000),
        ("Pilot", 420_000),
        ("Targeted scale", 1_600_000),
    ],
}


def _esc(value: object) -> str:
    return html_lib.escape(str(value))


def _load_json(path: Path):
    return json.loads(path.read_text()) if path.is_file() else None


def _badge(text: str, css_class: str) -> str:
    return f'<span class="badge {css_class}">{_esc(text)}</span>'


def _gbp(amount: float) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}£{abs(amount):,.0f}"


class _RunArtifacts:
    """Everything render_report reads from a run directory, loaded once,
    each field None/[] when the underlying artifact does not exist for this
    condition -- never an error, since which artifacts exist is exactly what
    distinguishes A/B/C from each other."""

    def __init__(self, run_dir: Path):
        ledger_data = _load_json(run_dir / "ledger.frozen.json")
        self.evidence_items: list[EvidenceItem] = (
            [load_evidence_item(item) for item in ledger_data["items"]] if ledger_data else []
        )
        self.evidence_by_id = {item.id: item for item in self.evidence_items}

        econ_data = _load_json(run_dir / "economics.json")
        self.economics: EconomicsResult | None = load_economics(econ_data) if econ_data else None

        initial_data = _load_json(run_dir / "positions_initial.json")
        self.positions_initial: list[CommitteePosition] = [load_position(p) for p in initial_data] if initial_data else []

        revised_data = _load_json(run_dir / "positions_revised.json")
        self.positions_revised: list[CommitteePosition] = [load_position(p) for p in revised_data] if revised_data else []

        updates_data = _load_json(run_dir / "belief_updates.json")
        self.belief_updates: list[BeliefUpdate] = [load_belief_update(u) for u in updates_data] if updates_data else []

        rec_data = _load_json(run_dir / "recommendation.json")
        self.recommendation: SyntheticRecommendation | None = load_recommendation(rec_data) if rec_data else None

        baseline_b_data = _load_json(run_dir / "baseline_b_result.json")
        self.baseline_b: BaselineBResult | None = load_baseline_b_result(baseline_b_data) if baseline_b_data else None

        narrative_path = run_dir / "narrative.txt"
        self.narrative: str | None = narrative_path.read_text().strip() if narrative_path.is_file() else None

        self.human_decision: HumanDecision | None = load_human_decision(run_dir)
        self.outcome_contract: OutcomeContract | None = load_outcome_contract(run_dir)


def _render_decision_view(case: DecisionCase, artifacts: _RunArtifacts) -> str:
    strength_counts: dict[str, int] = {}
    for item in artifacts.evidence_items:
        strength_counts[item.strength.value] = strength_counts.get(item.strength.value, 0) + 1
    strength_summary = (
        ", ".join(f"{count} {label}" for label, count in strength_counts.items())
        if strength_counts else "no evidence ledger recorded for this run"
    )

    top_sensitivity = (
        f"{artifacts.economics.tornado[0].assumption_id} (±{_gbp(artifacts.economics.tornado[0].npv_swing_gbp)} NPV swing)"
        if artifacts.economics and artifacts.economics.tornado else "not computed for this run"
    )

    return f"""
    <section id="decision">
      <h2>1. The decision</h2>
      <p class="ask">{_esc(case.decision_requested)}</p>
      <dl class="facts">
        <dt>Ask</dt><dd>{_esc(case.ask.type)}: {_gbp(case.ask.amount_gbp)} over {_esc(case.ask.duration)}</dd>
        <dt>Deadline</dt><dd>{_esc(case.deadline or "none recorded")}</dd>
        <dt>Sponsor</dt><dd>{_esc(case.sponsor)}</dd>
        <dt>Decision owner</dt><dd>{_esc(case.decision_owner)}</dd>
        <dt>Top sensitivity assumption</dt><dd>{_esc(top_sensitivity)}</dd>
        <dt>Evidence strength (this run's ledger)</dt><dd>{_esc(strength_summary)}</dd>
      </dl>
    </section>
    """


def _render_evidence_view(artifacts: _RunArtifacts) -> str:
    if not artifacts.evidence_items:
        return '<section id="evidence"><h2>2. Evidence map</h2><p class="note">No frozen ledger recorded for this run.</p></section>'

    columns_html = []
    for column_label, categories in EVIDENCE_COLUMNS:
        items = [item for item in artifacts.evidence_items if item.category in categories]
        rows = []
        for item in items:
            contradiction_note = (
                f'<div class="contradicts">contradicts: {_esc(", ".join(item.contradicts))}</div>'
                if item.contradicts else ""
            )
            attestation_class = "attestation-simulated" if item.attestation == Attestation.SIMULATED_THIRD_PARTY else "attestation-authored"
            rows.append(f"""
              <li class="evidence-item{' contradicted' if item.contradicts else ''}" title="{_esc(item.source)} ({_esc(item.period)})">
                <div class="evidence-head">
                  <code>{_esc(item.id)}</code>
                  {_badge(item.category.value, "category")}
                  {_badge(item.attestation.value, attestation_class)}
                </div>
                <div class="evidence-claim">{_esc(item.claim)}</div>
                {contradiction_note}
              </li>
            """)
        columns_html.append(f'<div class="evidence-column"><h3>{_esc(column_label)}</h3><ul>{"".join(rows) or "<li class=\'note\'>none</li>"}</ul></div>')

    return f"""
    <section id="evidence">
      <h2>2. Evidence map</h2>
      <div class="evidence-columns">{"".join(columns_html)}</div>
    </section>
    """


def _render_position_card(position: CommitteePosition) -> str:
    reasons = "".join(
        f'<li>{_esc(reason.text)}'
        + (f' <span class="refs">[{", ".join(reason.evidence_refs)}]</span>' if reason.evidence_refs else " <span class=\"refs unsupported\">[no citation]</span>")
        + "</li>"
        for reason in position.key_reasons
    )
    unknowns = "".join(f"<li>{_esc(u)}</li>" for u in position.blocking_unknowns)
    return f"""
      <div class="position-card">
        <h4>{_esc(position.member.value)}</h4>
        {_badge(position.recommendation.value, "action")}
        {_badge(position.confidence_band.value, "confidence")}
        <ul class="reasons">{reasons or '<li class="note">none stated</li>'}</ul>
        {'<div class="unknowns"><strong>Blocking unknowns:</strong><ul>' + unknowns + '</ul></div>' if unknowns else ''}
      </div>
    """


def _render_numbers(case: DecisionCase, artifacts: _RunArtifacts) -> str:
    econ = artifacts.economics
    if econ is None:
        return '<div class="numbers"><p class="note">No economics recorded for this run.</p></div>'

    tornado_rows = "".join(
        f"<tr><td>{_esc(t.assumption_id)}</td><td>{_gbp(t.npv_swing_gbp)}</td></tr>" for t in econ.tornado
    )
    avoided_loss = ""
    if econ.avoided_loss_low_gbp is not None:
        avoided_loss = f"""
          <div class="avoided-loss">
            <strong>Avoided-loss forecast (never summed into NPV):</strong>
            {_gbp(econ.avoided_loss_low_gbp)} – {_gbp(econ.avoided_loss_high_gbp)}
          </div>
        """
    ladder = STAGE_LADDER_GBP.get(case.id)
    ladder_html = ""
    if ladder:
        stage_rows = "".join(f"<li>{_esc(name)}: {_gbp(amount)}</li>" for name, amount in ladder)
        ladder_html = f'<div class="ladder"><strong>Staged-funding ladder:</strong><ol>{stage_rows}</ol></div>'

    return f"""
    <div class="numbers">
      <table class="npv-table">
        <tr><th>NPV low</th><th>NPV mid</th><th>NPV high</th><th>Payback</th><th>Peak funding</th></tr>
        <tr>
          <td>{_gbp(econ.npv_low_gbp)}</td>
          <td>{_gbp(econ.npv_mid_gbp)}</td>
          <td>{_gbp(econ.npv_high_gbp)}</td>
          <td>{f"{econ.payback_years:.1f}y" if econ.payback_years is not None else "n/a"}</td>
          <td>{_gbp(econ.peak_funding_gbp)}</td>
        </tr>
      </table>
      {avoided_loss}
      <table class="tornado-table">
        <caption>Tornado (assumption swing on NPV, most sensitive first)</caption>
        {tornado_rows}
      </table>
      {ladder_html}
    </div>
    """


def _render_positions_view(case: DecisionCase, artifacts: _RunArtifacts) -> str:
    if artifacts.positions_initial:
        cards_html = f'<div class="position-cards">{"".join(_render_position_card(p) for p in artifacts.positions_initial)}</div>'
    else:
        cards_html = '<p class="note">No independent positions recorded for this run.</p>'

    return f"""
    <section id="positions">
      <h2>3. Independent positions</h2>
      {cards_html}
      {_render_numbers(case, artifacts)}
    </section>
    """


def _render_belief_update(update: BeliefUpdate, revised_by_member: dict) -> str:
    change_class = f"change-{update.change_type.value}"
    if update.change_type == ChangeType.NO_CHANGE:
        revised = revised_by_member.get(update.member)
        held_reason = (
            f"held position: {revised.blocking_unknowns[0]}" if revised and revised.blocking_unknowns
            else "held position"
        )
        body = f'<p class="held">{_esc(held_reason)}</p>'
    else:
        refs = f' <span class="refs">[{", ".join(update.trigger_refs)}]</span>' if update.trigger_refs else ""
        body = f'<p class="transition">{_esc(update.initial_position.value)} → {_esc(update.revised_position.value)}{refs}</p><p class="reason">{_esc(update.stated_reason)}</p>'

    drift = "".join(_badge(f.value, "drift") for f in update.drift_flags)
    return f"""
      <div class="belief-update {change_class}">
        <h4>{_esc(update.member.value)}</h4>
        {_badge(update.change_type.value, "change-type")}
        {drift}
        {body}
      </div>
    """


def _render_changed_minds_view(artifacts: _RunArtifacts) -> str:
    if not artifacts.belief_updates:
        return '<section id="changed-minds"><h2>4. What changed minds</h2><p class="note">No belief updates recorded for this run (no revision phase in this condition).</p></section>'

    revised_by_member = {p.member: p for p in artifacts.positions_revised}
    cards = "".join(_render_belief_update(u, revised_by_member) for u in artifacts.belief_updates)
    return f"""
    <section id="changed-minds" class="hero">
      <h2>4. What changed minds</h2>
      <div class="belief-updates">{cards}</div>
    </section>
    """


def _render_decision_record_view(artifacts: _RunArtifacts) -> str:
    parts = ['<section id="decision-record"><h2>5. Decision record</h2>']

    if artifacts.recommendation is not None:
        rec = artifacts.recommendation
        conditions = "".join(f"<li>{_esc(c)}</li>" for c in rec.conditions)
        stop_conditions = "".join(f"<li>{_esc(c)}</li>" for c in rec.stop_conditions)
        unresolved = "".join(f"<li>{_esc(u)}</li>" for u in rec.unresolved_unknowns)
        dissent_refs = f' <span class="refs">[{", ".join(rec.strongest_dissent.refs)}]</span>' if rec.strongest_dissent.refs else ""
        parts.append(f"""
          <div class="recommendation">
            <div class="not-a-decision-banner">SYNTHETIC RECOMMENDATION · NOT A DECISION</div>
            {_badge(rec.action.value, "action")} {_gbp(rec.amount)} over {_esc(rec.duration)}
            {_badge(rec.confidence_band.value, "confidence")}
            {'<div class="conditions"><strong>Conditions:</strong><ul>' + conditions + '</ul></div>' if conditions else ''}
            {'<div class="stop-conditions"><strong>Stop conditions:</strong><ul>' + stop_conditions + '</ul></div>' if stop_conditions else ''}
            <div class="dissent-box">
              <strong>STRONGEST DISSENT</strong>
              <p>{_esc(rec.strongest_dissent.verbatim)}{dissent_refs}</p>
            </div>
            {'<div class="unresolved"><strong>Unresolved unknowns:</strong><ul>' + unresolved + '</ul></div>' if unresolved else ''}
          </div>
        """)
    elif artifacts.baseline_b is not None:
        b = artifacts.baseline_b
        unknowns = "".join(f"<li>{_esc(u)}</li>" for u in b.unioned_blocking_unknowns)
        minority = "".join(f"<li>{_esc(p.member.value)}: {_esc(p.recommendation.value)}</li>" for p in b.minority_positions)
        parts.append(f"""
          <div class="recommendation">
            <p class="note">Baseline B has no synthesized recommendation: deterministic aggregation only, no chair/narrative step.</p>
            {_badge(b.modal_action.value, "action")} ({b.modal_action_count}/{b.total_positions} members)
            {'<div class="unresolved"><strong>Unioned blocking unknowns:</strong><ul>' + unknowns + '</ul></div>' if unknowns else ''}
            {'<div class="unresolved"><strong>Minority positions:</strong><ul>' + minority + '</ul></div>' if minority else ''}
          </div>
        """)
    else:
        parts.append('<p class="note">No recommendation or aggregation recorded for this run.</p>')

    if artifacts.human_decision is not None:
        d = artifacts.human_decision
        overrides = "".join(f"<li>{_esc(o)}</li>" for o in d.overrides)
        parts.append(f"""
          <div class="human-decision">
            <strong>HUMAN DECISION</strong>
            {_badge(d.action.value, "action")} {_esc(d.disposition)}, owner {_esc(d.owner)}, decided {_esc(d.decided_at)}
            <p>{_esc(d.rationale)}</p>
            {'<div><strong>Overrides:</strong><ul>' + overrides + '</ul></div>' if overrides else ''}
          </div>
        """)
    else:
        parts.append('<div class="human-decision"><strong>HUMAN DECISION</strong><p class="note">No human decision recorded yet for this run.</p></div>')

    if artifacts.outcome_contract is not None:
        c = artifacts.outcome_contract
        measures = "".join(
            f"<li>{_esc(m.name)}: {_esc(m.baseline)} → {_esc(m.target)} (source: {_esc(m.source_ref)})</li>" for m in c.measures
        )
        kill = "".join(f"<li>{_esc(k)}</li>" for k in c.kill_criteria)
        parts.append(f"""
          <div class="outcome-contract">
            <strong>Outcome contract</strong>
            <p>Baseline {_esc(c.baseline_date)} · Review {_esc(c.review_date)} · Owner {_esc(c.owner)}</p>
            <p>Next decision: {_esc(c.next_decision)}</p>
            {'<div><strong>Measures:</strong><ul>' + measures + '</ul></div>' if measures else ''}
            {'<div><strong>Kill criteria:</strong><ul>' + kill + '</ul></div>' if kill else ''}
          </div>
        """)

    parts.append("</section>")
    return "".join(parts)


_STYLE = """
  :root {
    color-scheme: light dark;
    --bg: #ffffff; --fg: #1a1a1a; --muted: #666; --border: #ddd;
    --card-bg: #f7f7f7; --accent: #2a4d8f; --warn-bg: #fff3cd; --warn-fg: #6b5200;
    --dissent-bg: #fdeaea; --dissent-fg: #7a1f1f;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #1a1a1a; --fg: #eee; --muted: #aaa; --border: #444; --card-bg: #262626;
            --accent: #7fa6ff; --warn-bg: #3a3212; --warn-fg: #e8d27a;
            --dissent-bg: #3a1f1f; --dissent-fg: #f0a8a8; }
  }
  body { background: var(--bg); color: var(--fg); font-family: -apple-system, Segoe UI, sans-serif;
         max-width: 900px; margin: 0 auto; padding: 1.5rem; line-height: 1.5; }
  .realism-banner { background: var(--warn-bg); color: var(--warn-fg); text-align: center;
                     padding: 0.5rem; font-weight: bold; letter-spacing: 0.05em; margin-bottom: 1.5rem; }
  section { margin-bottom: 2.5rem; border-top: 1px solid var(--border); padding-top: 1rem; }
  h2 { color: var(--accent); }
  dl.facts dt { font-weight: bold; margin-top: 0.5rem; }
  dl.facts dd { margin-left: 0; color: var(--muted); }
  .badge { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 0.75rem;
           font-size: 0.75rem; margin-right: 0.25rem; background: var(--card-bg); border: 1px solid var(--border); }
  .attestation-simulated { background: var(--warn-bg); color: var(--warn-fg); }
  .evidence-columns { display: flex; gap: 1rem; flex-wrap: wrap; }
  .evidence-column { flex: 1; min-width: 220px; }
  .evidence-column ul { list-style: none; padding: 0; }
  .evidence-item { background: var(--card-bg); border: 1px solid var(--border); border-radius: 0.5rem;
                    padding: 0.5rem; margin-bottom: 0.5rem; }
  .evidence-item.contradicted { border-color: var(--dissent-fg); }
  .evidence-head code { font-size: 0.8rem; }
  .contradicts { color: var(--dissent-fg); font-size: 0.8rem; }
  .position-cards { display: flex; gap: 1rem; flex-wrap: wrap; }
  .position-card { flex: 1; min-width: 200px; background: var(--card-bg); border: 1px solid var(--border);
                    border-radius: 0.5rem; padding: 0.75rem; }
  .refs { color: var(--muted); font-size: 0.8rem; }
  .refs.unsupported { color: var(--dissent-fg); }
  table { border-collapse: collapse; margin: 0.75rem 0; width: 100%; }
  table caption { text-align: left; color: var(--muted); font-size: 0.85rem; }
  table th, table td { border: 1px solid var(--border); padding: 0.35rem 0.6rem; text-align: left; }
  .belief-updates { display: flex; gap: 1rem; flex-wrap: wrap; }
  .belief-update { flex: 1; min-width: 220px; background: var(--card-bg); border: 1px solid var(--border);
                    border-radius: 0.5rem; padding: 0.75rem; }
  .belief-update.change-no_change { border-left: 4px solid var(--accent); }
  .not-a-decision-banner { background: var(--warn-bg); color: var(--warn-fg); font-weight: bold;
                            padding: 0.4rem; text-align: center; margin-bottom: 0.5rem; }
  .dissent-box { background: var(--dissent-bg); color: var(--dissent-fg); border-radius: 0.5rem;
                 padding: 0.75rem; margin-top: 0.75rem; }
  .human-decision { border: 2px solid var(--accent); border-radius: 0.5rem; padding: 0.75rem; margin-top: 1rem; }
  .outcome-contract { background: var(--card-bg); border-radius: 0.5rem; padding: 0.75rem; margin-top: 1rem; }
  .note { color: var(--muted); font-style: italic; }
  @media print { .realism-banner { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
"""


def render_report(case: DecisionCase, run_dir: Path) -> str:
    artifacts = _RunArtifacts(run_dir)

    body = "\n".join([
        _render_decision_view(case, artifacts),
        _render_evidence_view(artifacts),
        _render_positions_view(case, artifacts),
        _render_changed_minds_view(artifacts),
        _render_decision_record_view(artifacts),
    ])

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{_esc(case.title)}: kriterion report</title>
<style>{_STYLE}</style>
</head>
<body>
<div class="realism-banner">{_esc(case.case_realism.value.replace("_", " "))} CASE · SYNTHETIC DATA</div>
<h1>{_esc(case.title)}</h1>
{body}
</body>
</html>
"""
