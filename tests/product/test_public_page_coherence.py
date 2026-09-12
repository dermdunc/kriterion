"""`docs/index.html` is generated; these tests keep it that way.

Before V1.1 this file compared a hand-written page against the artifacts it
described, figure by figure, because nothing else could. That was a stand-in.
The page is now a projection (ADR-011) and every material statement on it is
re-derived from the decision state (ADR-012), so the checks that matter are
different:

  - the committed page is **byte-identical** to what the pipeline emits today,
    which is what makes "generated, not hand-maintained" a fact rather than a
    claim;
  - the narrative-integrity checker passes against it, with no exemptions;
  - the committed assurance-import payload is exactly what the adapter emits
    from the committed envelope, so the assurance section cannot drift either;
  - retired overclaims stay retired;
  - Kriterion Lab is still intact, with its honest-negative result and caveats.

Figure-by-figure assertions are gone on purpose: every one of them is now a
structural guarantee, and keeping hand-copied expected values here would
reintroduce exactly the second source of truth this increment removed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from kriterion.cli import DECISION_PAGE_CREATED_AT
from kriterion.decision_state import load_decision_state
from kriterion.narrative import check
from kriterion.report.decision_page import render_decision_page

REPO_ROOT = Path(__file__).parent.parent.parent
PAGE = REPO_ROOT / "docs" / "index.html"
LAB = REPO_ROOT / "docs" / "lab.html"
CASE_DIR = REPO_ROOT / "cases" / "coding-agent-rollout"
RUN_DIR = REPO_ROOT / "runs" / "caseA-condC-s5"
ASSURANCE_IMPORT = CASE_DIR / "assurance" / "imported.json"


@pytest.fixture(scope="module")
def state():
    return load_decision_state(
        case_dir=CASE_DIR,
        run_dir=RUN_DIR,
        created_at=DECISION_PAGE_CREATED_AT,
        assurance_import_path=ASSURANCE_IMPORT,
    )


@pytest.fixture(scope="module")
def page() -> str:
    return PAGE.read_text()


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------


def test_the_committed_page_is_exactly_what_the_pipeline_emits(state, page):
    """The single check that makes the architecture claim true. If this fails,
    either someone hand-edited the page or the renderer changed and the page
    was not rebuilt:

        kriterion decision-page caseA-condC-s5 cases/coding-agent-rollout \\
            --assurance-import cases/coding-agent-rollout/assurance/imported.json
    """
    assert render_decision_page(state) == page


def test_rendering_is_deterministic(state):
    assert render_decision_page(state) == render_decision_page(state)


def test_the_committed_page_passes_the_narrative_integrity_check(state, page):
    violations = check(state, page)
    assert violations == [], "\n".join(str(v) for v in violations)


def test_the_committed_assurance_import_is_what_the_adapter_actually_emits():
    """The assurance section renders a committed pipeline artifact. Regenerate
    it from the committed envelope and require an exact match, so the section
    cannot drift from the documents it claims to describe:

        kriterion assurance import cases/coding-agent-rollout/assurance \\
            --out cases/coding-agent-rollout/assurance/imported.json
    """
    from kriterion.assurance.adapter import adapt_envelope, load_assurance_documents
    from kriterion.domain.evidence import Attestation
    from kriterion.domain.serialization import to_dict

    committed = json.loads(ASSURANCE_IMPORT.read_text())
    envelope, decision = load_assurance_documents(CASE_DIR / "assurance")
    created_at = committed["items"][0]["created_at"]
    summary, items = adapt_envelope(
        envelope, decision, attestation=Attestation.AUTHORED, created_at=created_at
    )
    assert committed["summary"] == to_dict(summary)
    assert committed["items"] == [to_dict(item) for item in items]


# ---------------------------------------------------------------------------
# Claim discipline
# ---------------------------------------------------------------------------


BANNED_PHRASES = {
    "produced end-to-end by the real pipeline": "overclaim retired in V1",
    "nothing on this page is a mock-up": "overclaim retired in V1",
    "independently measures": "the assurance fixture is authored; no assurance run happened",
    "Kriterion runs identically with manual and imported evidence only": (
        "imported evidence is not part of a committee run"
    ),
    "PARTIAL": "not an assurance outcome or a Kriterion decision state",
    "hand-maintained": "the page is generated now; claiming otherwise is stale",
}


def test_the_page_makes_no_retired_overclaim(page):
    found = {p: why for p, why in BANNED_PHRASES.items() if p in page}
    assert not found, "docs/index.html contains retired claims: " + json.dumps(found, indent=2)


def test_the_page_is_labelled_as_an_authored_fixture(page):
    assert "AUTHORED FIXTURE" in page
    assert "authored fixtures" in page


def test_the_page_states_that_the_assurance_evidence_was_not_before_the_committee(state, page):
    """The imported envelope is not in this run's frozen ledger and the
    deliberation never saw it. Implying otherwise would attribute reasoning to
    a committee that could not have done it."""
    assert "The committee below never saw it" in page
    ledger_ids = set(state.evidence_by_id)
    imported_ids = {item.id for item in state.assurance.items}
    assert not (ledger_ids & imported_ids)


def test_the_title_names_the_case_being_decided(state, page):
    assert f"<title>Kriterion: {state.case.title}</title>" in page


def test_no_human_decision_is_fabricated(state, page):
    assert state.human_decision is None
    assert not (RUN_DIR / "human_decision.json").exists()
    assert "No human decision has been recorded" in page


def test_the_page_tells_the_reader_what_happens_next(state, page):
    assert "kriterion decide" in page
    assert state.case.decision_owner in page


# ---------------------------------------------------------------------------
# The run this page renders
# ---------------------------------------------------------------------------


def test_the_rendered_run_actually_stored_its_evidence_requests(state):
    """The whole reason this page renders seed 5 rather than the pre-registered
    seed 0: the V0 demo runs predate `evidence_requests.json`, so a per-seat
    "what would change my mind" view could only ever have been reconstructed
    copy on those runs."""
    assert state.evidence_requests_recorded
    assert state.stored_evidence_request_count > 0
    assert all(r.would_change.strip() for s in state.seats for r in s.evidence_requests)


def test_the_pre_registered_v0_demo_runs_are_untouched():
    """V1.1 presentation may only read V0 research data. Seed 0's committed
    artifacts must still be there, and must still have no evidence-request
    artifact, since that is the historical fact the page's status line states.
    """
    v0 = REPO_ROOT / "runs" / "caseA-condC-s0"
    assert (v0 / "recommendation.json").is_file()
    assert not (v0 / "evidence_requests.json").exists()


# ---------------------------------------------------------------------------
# The Lab is not collateral damage
# ---------------------------------------------------------------------------


def test_kriterion_lab_still_carries_the_research_and_its_negative_result():
    lab = LAB.read_text()
    for marker in ("Baseline A", "Baseline B", "Treatment C", "Treatment D", "perturbation"):
        assert marker in lab, f"Kriterion Lab lost {marker!r}"
    assert "did not beat" in lab or "honest-negative" in lab


def test_the_public_page_still_points_at_the_lab(page):
    assert 'href="lab.html"' in page


# ---------------------------------------------------------------------------
# Fixes from reading the finished page as CIO / CFO / CISO / sponsor
# ---------------------------------------------------------------------------


def _decision_section(page: str) -> str:
    return page.split('data-kriterion-role="decision"')[1].split("</section>")[0]


def test_the_dominant_assumption_is_shown_with_its_evidence_strength(state, page):
    """A CFO reading that one assumption swings the valuation by more than the
    whole ask, without being told how well evidenced it is, will assume it is
    solid. The strength is the reason for surfacing it at all."""
    decision = _decision_section(page)
    assumption = state.primary_sensitivity_assumption
    assert assumption is not None, "the canonical case must resolve its dominant assumption"
    assert assumption.id in decision
    assert "Recorded evidence strength" in decision
    for field in ("evidence_strength", "range", "value", "owner"):
        assert f'data-kriterion-source="assumptions_by_id[{assumption.id}].{field}"' in decision


def test_the_money_is_visible_before_the_fold(state, page):
    """The most decision-relevant fact - that the sign flips inside the stated
    plausible ranges - must not sit four sections below the decision itself."""
    decision = _decision_section(page)
    for path in ("economics.npv_mid_gbp", "economics.npv_low_gbp", "economics.npv_high_gbp"):
        assert f'data-kriterion-source="{path}"' in decision
    assert "economics_interpretation" in decision
    assert state.npv_sign_flips is True


def test_the_critical_failure_count_says_what_it_does_not_count(state, page):
    """A CISO reading "critical failures: 0" above a list of a dozen items will
    read it as "every check passed". The envelope behind this page records a
    non-gating failure and a check that returned no verdict at all."""
    assert state.assurance.summary["critical_failure_count"] == 0
    assert "It is not a count of checks that did not pass" in state.assurance_summary_caveat
    assert state.assurance_unknown_count > 0
    assert 'data-kriterion-source="assurance_summary_caveat"' in page
