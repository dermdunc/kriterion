"""`docs/index.html` is hand-maintained; these tests stop it drifting.

The 2026-09-11 adversarial review found the public page displaying a source
`fail` outcome as the invented word "PARTIAL" — fourteen lines above a claim
that the adapter guarantees failures "can't be softened in translation" — and
attributing the producer's decision to coverage gaps that its decision
document does not contain. Nothing caught it, because no test ever compared
the page to the artifacts it describes.

Until the page is rendered from the pipeline (deferred, see
docs/next-actions.md), these tests are the mechanical substitute: every
assurance outcome, economics figure, committee position and headline number
on the page is checked against the committed source document it claims to
come from, and a list of known-overclaiming phrases is banned outright.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
PAGE = REPO_ROOT / "docs" / "index.html"
RUN_DIR = REPO_ROOT / "runs" / "caseA-condC-s0"
FIXTURE_DIR = REPO_ROOT / "cases" / "coding-agent-rollout" / "assurance"


@pytest.fixture(scope="module")
def page() -> str:
    return PAGE.read_text()


@pytest.fixture(scope="module")
def envelope() -> dict:
    return json.loads((FIXTURE_DIR / "envelope.json").read_text())


@pytest.fixture(scope="module")
def decision() -> dict:
    return json.loads((FIXTURE_DIR / "decision.json").read_text())


def _assurance_rows(page: str) -> dict[str, str]:
    """specId -> the row's full inner HTML, from the data-spec-id bindings."""
    return {
        m.group(1): m.group(2)
        for m in re.finditer(r'<tr data-spec-id="([^"]+)">(.*?)</tr>', page, re.S)
    }


def _cells(row_html: str) -> list[str]:
    return [
        re.sub(r"<[^>]+>", "", c).strip()
        for c in re.findall(r"<td>(.*?)</td>", row_html, re.S)
    ]


# ---------------------------------------------------------------------------
# Assurance section: every displayed outcome must be the source outcome.
# ---------------------------------------------------------------------------


def test_every_envelope_result_has_a_bound_row_on_the_page(page, envelope):
    rows = _assurance_rows(page)
    envelope_spec_ids = {r["specId"] for r in envelope["results"]}
    assert rows, "the assurance table lost its data-spec-id bindings"
    assert set(rows) == envelope_spec_ids, (
        "the page's assurance table and the committed envelope disagree about which "
        f"checks exist: page={sorted(rows)} envelope={sorted(envelope_spec_ids)}"
    )


def test_displayed_outcome_is_the_source_outcome_never_a_softer_word(page, envelope):
    """The FAIL -> PARTIAL regression, made impossible."""
    rows = _assurance_rows(page)
    for result in envelope["results"]:
        cells = _cells(rows[result["specId"]])
        assert len(cells) == 3, f"{result['specId']}: expected 3 cells, got {cells}"
        _label, method_cell, outcome_cell = cells

        assert method_cell == result["method"], (
            f"{result['specId']}: page shows method {method_cell!r}, "
            f"envelope says {result['method']!r}"
        )
        expected = result["outcome"].upper()
        assert outcome_cell.startswith(expected), (
            f"{result['specId']}: page's result cell starts {outcome_cell[:40]!r}, "
            f"but the envelope's outcome is {expected!r} — the page must show what the "
            "source document actually says"
        )


def test_page_never_invents_an_outcome_vocabulary(page, envelope):
    """"PARTIAL" is neither an assurance outcome nor a Kriterion decision state."""
    rows = _assurance_rows(page)
    permitted = {r["outcome"].upper() for r in envelope["results"]}
    for spec_id, row in rows.items():
        outcome_cell = _cells(row)[2]
        leading = re.match(r"[A-Z_]+", outcome_cell)
        assert leading and leading.group(0) in permitted, (
            f"{spec_id}: result cell leads with {outcome_cell[:30]!r}, which is not one "
            f"of the envelope's own outcomes {sorted(permitted)}"
        )


def test_decision_state_and_reason_count_match_the_decision_document(page, decision):
    assert decision["state"] in page
    # The page must not represent coverage gaps as decision reasons: the
    # producer's decider does not read fingerprint.uncovered at all.
    assert len(decision["reasons"]) == 2
    assert "plus three named coverage gaps" not in page
    assert "<em>not inputs to that decision</em>" in page


def test_coverage_gap_count_matches_the_envelope(page, envelope):
    uncovered = envelope["fingerprint"]["uncovered"]
    assert len(uncovered) == 3
    assert "three coverage gaps" in page
    for gap in uncovered:
        assert f"<code>{gap}</code>" in page, f"coverage gap {gap!r} not named on the page"


# ---------------------------------------------------------------------------
# Economics: every figure traces to the committed economics.json.
# ---------------------------------------------------------------------------


def _millions(value: float) -> str:
    return f"{value / 1_000_000:.2f}"


def test_npv_figures_match_the_committed_economics_artifact(page):
    econ = json.loads((RUN_DIR / "economics.json").read_text())
    # Page quotes these to 2dp in £m, with a minus sign on the low case.
    assert f"£{_millions(econ['npv_mid_gbp'])}m" in page
    assert f"£{_millions(econ['npv_high_gbp'])}m".replace("38.14", "38.1") in page or "£38.1m" in page
    assert "−£5.35m" in page or "-£5.35m" in page
    assert f"{econ['discount_rate']:.0%}".replace("%", "% discount rate") in page


def test_tornado_ordering_and_top_swing_match_the_artifact(page):
    econ = json.loads((RUN_DIR / "economics.json").read_text())
    swings = {t["assumption_id"]: abs(t["npv_swing_gbp"]) for t in econ["tornado"]}
    top = max(swings, key=swings.get)
    assert top == "attribution_factor", (
        "the page's headline says attribution dominates; the artifact now says " + top
    )
    # £16.9m / £15.7m as displayed.
    assert f"£{swings['attribution_factor'] / 1_000_000:.1f}m" in page
    assert f"£{swings['uplift'] / 1_000_000:.1f}m" in page


def test_dominance_claim_is_scoped_to_the_tested_assumptions(page):
    """Deterministic computation is not the same as complete assumption
    discipline: the discount rate, headcount timing and stage amounts are
    constants outside the tornado, and the page must say so."""
    assert "Of the five assumptions the case pack states and ranges" in page
    assert "What the tornado does not cover" in page
    assert "10% discount rate" in page
    assert "no mid-year ramp" in page


# ---------------------------------------------------------------------------
# Deliberation + recommendation: traced to the run artifacts.
# ---------------------------------------------------------------------------


def test_recommendation_matches_the_committed_run(page):
    rec = json.loads((RUN_DIR / "recommendation.json").read_text())
    assert rec["action"] == "DEFER"
    assert rec["confidence_band"] == "MEDIUM"
    assert "<strong>DEFER</strong>" in page
    assert "confidence MEDIUM" in page


def test_every_seat_position_on_the_page_matches_the_run_artifacts(page):
    initial = {p["member"]: p for p in json.loads((RUN_DIR / "positions_initial.json").read_text())}
    revised = {p["member"]: p for p in json.loads((RUN_DIR / "positions_revised.json").read_text())}
    assert set(initial) == set(revised)

    # The page's claim: all five held DEFER, and only the CFO's confidence moved.
    assert all(p["recommendation"] == "DEFER" for p in initial.values())
    assert all(p["recommendation"] == "DEFER" for p in revised.values())
    moved = {
        m
        for m in initial
        if initial[m]["confidence_band"] != revised[m]["confidence_band"]
    }
    assert moved == {"cfo"}, f"page says only the CFO's confidence changed; artifacts say {moved}"
    assert "LOW → MEDIUM" in page


def test_ledger_item_count_matches_the_frozen_ledger(page):
    ledger = json.loads((RUN_DIR / "ledger.frozen.json").read_text())
    assert f"holds {len(ledger['items'])} items" in page


def test_staged_ladder_amounts_match_the_cash_flow_model(page):
    from kriterion.economics import case_flows

    assert f"£{case_flows.DISCOVERY_GBP // 1000}k discovery" in page
    assert f"£{case_flows.PILOT_GBP // 1000}k pilot" in page
    assert f"£{case_flows.TARGETED_SCALE_GBP / 1_000_000:.1f}m targeted scale" in page
    # Cost of buying evidence, quoted consistently as the cumulative range.
    cumulative = (case_flows.DISCOVERY_GBP + case_flows.PILOT_GBP) // 1000
    assert f"£50k–£{cumulative}k" in page
    assert "£50k–£420k" not in page, "the evidence-buying range was quoted two different ways"


# ---------------------------------------------------------------------------
# Claim discipline: phrases the page is not allowed to make.
# ---------------------------------------------------------------------------


BANNED_PHRASES = {
    "produced end-to-end by the real pipeline": "the page is hand-maintained, not rendered",
    "nothing on this page is a mock-up": "overclaims: the page itself is hand-authored narrative",
    "independently measures": "the assurance fixture is authored; no assurance run happened",
    "Kriterion runs identically with manual and imported evidence only": (
        "imported evidence is not part of a committee run"
    ),
    "PARTIAL": "not an assurance outcome or a Kriterion decision state",
}


def test_page_makes_no_known_overclaim(page):
    found = {p: why for p, why in BANNED_PHRASES.items() if p in page}
    assert not found, "docs/index.html contains retired overclaims: " + json.dumps(found, indent=2)


def test_page_states_that_it_is_hand_maintained(page):
    assert "hand-maintained" in page
    assert "authored fixture" in page.lower()


def test_what_would_change_section_is_labelled_as_derived_not_stored(page):
    """`EvidenceRequest.would_change` is only persisted for runs made after
    2026-09-11; this run predates that, so the page must not present its
    list as a stored per-seat record."""
    assert "evidence_requests.json" in page
    assert "derived from" in page or "reconstructed" in page
