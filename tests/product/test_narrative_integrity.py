"""Narrative-integrity regressions (ADR-012).

Every case here is a real failure this project shipped, or a near neighbour of
one. The 2026-09-11 adversarial review of V1 found the computations correct and
the *descriptions* wrong: a source `fail` displayed as the invented word
"PARTIAL", a producer decision credited to reasoning its decider never ran, an
authored fixture called an independent measurement, one cost quoted two ways.

These tests build a decision state directly (no run directory, no case pack) so
each invariant is exercised in isolation, then mutate the rendered page the way
a careless edit or an over-helpful summariser would, and assert the checker
refuses it.
"""

from __future__ import annotations

import pytest

from kriterion.decision_state import AssuranceImport, DecisionState, SeatView
from kriterion.domain.case import Ask, DecisionCase
from kriterion.domain.committee import (
    BeliefUpdate,
    CommitteePosition,
    EvidenceRequest,
    KeyReason,
)
from kriterion.domain.decision import Dissent, SyntheticRecommendation
from kriterion.domain.economics import EconomicsResult, TornadoEntry
from kriterion.domain.enums import (
    ChangeType,
    CommitteeSeat,
    ConfidenceBand,
    DecisionAction,
    EvidenceRequestStatus,
    PositionPhase,
)
from kriterion.domain.evidence import Assumption, Attestation, EvidenceCategory, EvidenceItem, Strength
from kriterion.narrative import check, resolve
from kriterion.report.decision_page import render_decision_page

AT = "2026-01-01T00:00:00Z"


def _item(item_id, category, strength, claim, attestation=Attestation.AUTHORED):
    return EvidenceItem(
        id=item_id,
        created_at=AT,
        category=category,
        attestation=attestation,
        claim=claim,
        source="fixture",
        period="2026-Q1",
        strength=strength,
    )


def _state(**overrides) -> DecisionState:
    """A minimal but complete decision state: one of every shape the page has
    to render, so a mutation test never passes because the section was absent.
    """
    evidence = [
        _item("ev-001", EvidenceCategory.MEASURED, Strength.HIGH, "Pilot acceptance was recorded."),
        _item(
            "ev-002",
            EvidenceCategory.ASSUMPTION,
            Strength.LOW,
            "Benefit attribution is assumed, not established.",
        ),
        _item(
            "ev-003",
            EvidenceCategory.UNKNOWN,
            Strength.LOW,
            "Runtime drift has never been observed either way.",
        ),
    ]
    assumptions = [
        Assumption(
            id="as-benefit-attribution-factor",
            created_at=AT,
            value=0.10,
            range=(0.05, 0.20),
            evidence_strength=Strength.LOW,
            owner="cfo",
        )
    ]
    economics = EconomicsResult(
        id="fixture-economics",
        created_at=AT,
        case_id="fixture-case",
        discount_rate=0.10,
        npv_low_gbp=-5_351_240.0,
        npv_mid_gbp=5_085_455.0,
        npv_high_gbp=38_138_347.0,
        payback_years=None,
        peak_funding_gbp=0.0,
        tornado=[TornadoEntry(assumption_id="attribution_factor", npv_swing_gbp=16_922_975.0)],
    )
    seat = SeatView(
        seat=CommitteeSeat.CFO,
        initial=CommitteePosition(
            id="p-init",
            created_at=AT,
            member=CommitteeSeat.CFO,
            phase=PositionPhase.INITIAL,
            recommendation=DecisionAction.DEFER,
            confidence_band=ConfidenceBand.LOW,
            key_reasons=[KeyReason(text="Attribution is not evidenced.", evidence_refs=["ev-002"])],
            blocking_unknowns=["No agreed attribution methodology."],
        ),
        revised=CommitteePosition(
            id="p-rev",
            created_at=AT,
            member=CommitteeSeat.CFO,
            phase=PositionPhase.REVISED,
            recommendation=DecisionAction.DEFER,
            confidence_band=ConfidenceBand.MEDIUM,
            key_reasons=[KeyReason(text="Attribution is not evidenced.", evidence_refs=["ev-002"])],
            blocking_unknowns=["No agreed attribution methodology."],
        ),
        belief_update=BeliefUpdate(
            id="b-1",
            created_at=AT,
            member=CommitteeSeat.CFO,
            initial_position=DecisionAction.DEFER,
            initial_confidence=ConfidenceBand.LOW,
            revised_position=DecisionAction.DEFER,
            revised_confidence=ConfidenceBand.MEDIUM,
            change_type=ChangeType.NO_CHANGE,
            stated_reason="Nothing arrived that bears on attribution.",
        ),
        evidence_requests=[
            EvidenceRequest(
                id="er-1",
                created_at=AT,
                member=CommitteeSeat.CFO,
                description="A controlled study of attributable productivity improvement.",
                would_change="A controlled study above the stated threshold would move this seat.",
                status=EvidenceRequestStatus.UNAVAILABLE,
            )
        ],
    )
    # Reasoning that mentions a funding action the recommendation did NOT make:
    # the exact shape that turned a DEFER into "the committee recommends a
    # pilot" during the V1 review.
    recommendation = SyntheticRecommendation(
        id="rec-1",
        created_at=AT,
        action=DecisionAction.DEFER,
        amount=4_200_000.0,
        duration="24 months",
        conditions=["A pilot could resolve the attribution uncertainty."],
        strongest_dissent=Dissent(
            verbatim="A pilot could resolve the attribution uncertainty; until then, defer.",
            refs=["ev-002"],
        ),
        unresolved_unknowns=["Attribution methodology."],
    )
    assurance = AssuranceImport(
        summary={
            "capability_name": "fixture-capability",
            "capability_version": "1.0.0",
            "decision_state": "REVIEW_REQUIRED",
            "declared_decision_state": "REVIEW_REQUIRED",
            "stale": False,
            "critical_failure_count": 0,
            "result_count": 2,
            "uncovered_count": 0,
            "digests_captured": False,
            "reasons": ["the injection check did not hold"],
        },
        items=[
            _item(
                "asr-injection",
                EvidenceCategory.MEASURED,
                Strength.MEDIUM,
                "Assurance counterfactual check 'prompt-injection-resilience-001': FAIL.",
            ),
            _item(
                "asr-drift",
                EvidenceCategory.UNKNOWN,
                Strength.LOW,
                "Assurance check 'runtime-drift-001' did not produce a verdict "
                "(outcome: indeterminate). Its subject remains unknown, not passed.",
            ),
        ],
    )
    defaults = dict(
        run_id="fixture-run",
        case=DecisionCase(
            id="fixture-case",
            created_at=AT,
            title="Fixture case",
            sponsor="cto",
            decision_owner="cio",
            decision_requested="Should we fund the fixture?",
            ask=Ask(type="staged_funding", amount_gbp=4_200_000.0, duration="24 months"),
            alternatives=["do_nothing", "limited_pilot"],
            deadline="2026-12-01",
        ),
        assumptions=assumptions,
        evidence=evidence,
        economics=economics,
        seats=[seat],
        recommendation=recommendation,
        human_decision=None,
        outcome_contract=None,
        assurance=assurance,
        ledger_version=1,
        ledger_fingerprint="deadbeef",
        evidence_requests_recorded=True,
    )
    defaults.update(overrides)
    return DecisionState(**defaults)


@pytest.fixture(scope="module")
def state() -> DecisionState:
    return _state()


@pytest.fixture(scope="module")
def page(state) -> str:
    return render_decision_page(state)


def _rules(violations) -> set[str]:
    return {v.rule for v in violations}


def test_the_unmutated_page_is_clean(state, page):
    assert check(state, page) == []


# ---------------------------------------------------------------------------
# State preservation: a FAIL stays a FAIL
# ---------------------------------------------------------------------------


def test_assurance_fail_is_rendered_as_the_source_word(state, page):
    assert "FAIL." in page


@pytest.mark.parametrize(
    "softer", ["PARTIAL", "MOSTLY SATISFIED", "CONCERN", "NEEDS ATTENTION", "MINOR ISSUE"]
)
def test_softening_a_source_fail_is_refused(state, page, softer):
    mutated = page.replace(
        "&#x27;prompt-injection-resilience-001&#x27;: FAIL.",
        f"&#x27;prompt-injection-resilience-001&#x27;: {softer}.",
    )
    assert mutated != page, "the FAIL claim is not on the page in the expected form"
    assert "binding.match" in _rules(check(state, mutated))


def test_a_softening_word_may_not_appear_in_the_pages_own_prose(state, page):
    mutated = page.replace(
        "<h2 id=\"h-assurance\">", "<p>Resilience was mostly satisfactory.</p><h2 id=\"h-assurance\">"
    )
    assert "softening" in _rules(check(state, mutated))


# ---------------------------------------------------------------------------
# Decision fidelity: DEFER does not become PILOT
# ---------------------------------------------------------------------------


def test_the_headline_is_the_recommended_action_not_a_word_from_its_reasoning(state, page):
    """The recommendation's own conditions and dissent both contain the word
    "pilot". The headline must still be the action the model actually chose."""
    assert "A pilot could resolve" in page  # the reasoning really does say it
    action = resolve(state, "recommendation.action")
    assert action is DecisionAction.DEFER
    assert 'data-kriterion-role="recommendation-action"' in page
    headline = page.split('data-kriterion-role="recommendation-action"')[1].split("</span>")[0]
    assert "DEFER" in headline and "PILOT" not in headline


def test_an_unbound_action_claim_in_prose_is_refused(state, page):
    mutated = page.replace(
        "<h2 id=\"h-rec\">", "<p>The committee recommends a PILOT.</p><h2 id=\"h-rec\">"
    )
    assert "vocabulary.fidelity" in _rules(check(state, mutated))


def test_repointing_the_headline_at_another_field_is_refused(state, page):
    mutated = page.replace(
        'data-kriterion-source="recommendation.action" data-kriterion-format="label" '
        'class="headline" data-kriterion-role="recommendation-action"',
        'data-kriterion-source="seats_by_id[cfo].revised.recommendation" '
        'data-kriterion-format="label" class="headline" '
        'data-kriterion-role="recommendation-action"',
        1,
    )
    assert mutated != page
    assert "decision.fidelity" in _rules(check(state, mutated))


# ---------------------------------------------------------------------------
# Epistemic fidelity: an ASSUMPTION is not a measurement
# ---------------------------------------------------------------------------


def test_an_assumption_cannot_be_relabelled_as_measured(state, page):
    card = page.split('data-evidence-id="ev-002"')[1].split("</li>")[0]
    assert "ASSUMPTION" in card
    mutated = page.replace(
        '<span data-kriterion-source="evidence_by_id[ev-002].category" '
        'data-kriterion-format="text" class="badge category">ASSUMPTION</span>',
        '<span data-kriterion-source="evidence_by_id[ev-002].category" '
        'data-kriterion-format="text" class="badge category">MEASURED</span>',
    )
    assert mutated != page
    assert "binding.match" in _rules(check(state, mutated))


def test_a_card_may_not_borrow_another_items_epistemic_class(state, page):
    """Relabelling is caught by re-derivation; *repointing* is not, because
    the other item's class re-derives correctly. The card's own identity has
    to constrain it."""
    card = page.split('<li class="evidence-item" data-evidence-id="ev-002">')[1].split("</li>")[0]
    swapped = card.replace("evidence_by_id[ev-002].category", "evidence_by_id[ev-001].category")
    mutated = page.replace(card, swapped)
    assert mutated != page
    assert "evidence.attribution" in _rules(check(state, mutated))


def test_promotion_words_are_refused_in_prose(state, page):
    mutated = page.replace(
        "<h2 id=\"h-assumed\">", "<p>The attribution figure is proven.</p><h2 id=\"h-assumed\">"
    )
    assert "softening" in _rules(check(state, mutated))


def test_every_rendered_item_shows_its_epistemic_class(state, page):
    mutated = page.replace(
        '<span data-kriterion-source="evidence_by_id[ev-003].category" '
        'data-kriterion-format="text" class="badge category">UNKNOWN</span>',
        "",
    )
    assert mutated != page
    assert "epistemic.fidelity" in _rules(check(state, mutated))


# ---------------------------------------------------------------------------
# Unknown handling: unknown stays unknown
# ---------------------------------------------------------------------------


def test_an_unknown_result_is_rendered_as_unknown(state, page):
    assert "did not produce a verdict" in page
    card = page.split('data-evidence-id="asr-drift"')[1].split("</li>")[0]
    assert "UNKNOWN" in card
    assert "PASS" not in card


@pytest.mark.parametrize("wrong", ["PASS", "NOT DETECTED", "NO ISSUE"])
def test_an_unknown_cannot_be_restated_as_a_pass(state, page, wrong):
    mutated = page.replace(
        '<span data-kriterion-source="evidence_by_id[ev-003].category" '
        'data-kriterion-format="text" class="badge category">UNKNOWN</span>',
        '<span data-kriterion-source="evidence_by_id[ev-003].category" '
        f'data-kriterion-format="text" class="badge category">{wrong}</span>',
    )
    assert mutated != page
    assert "binding.match" in _rules(check(state, mutated))


def test_dropping_an_unknown_item_from_the_page_is_refused(state, page):
    card = page.split('<li class="evidence-item" data-evidence-id="ev-003">')[1].split("</li>")[0]
    mutated = page.replace(
        f'<li class="evidence-item" data-evidence-id="ev-003">{card}</li>', ""
    )
    assert mutated != page
    assert "unknown.preservation" in _rules(check(state, mutated))


def test_dropping_an_imported_assurance_item_is_refused(state, page):
    card = page.split('<li class="evidence-item" data-evidence-id="asr-injection">')[1].split("</li>")[0]
    mutated = page.replace(
        f'<li class="evidence-item" data-evidence-id="asr-injection">{card}</li>', ""
    )
    assert mutated != page
    assert "unknown.preservation" in _rules(check(state, mutated))


# ---------------------------------------------------------------------------
# Numeric fidelity
# ---------------------------------------------------------------------------


def test_the_economics_preserve_sign_currency_and_range_ordering(state, page):
    assert "-£5.35m" in page  # downside keeps its minus sign
    assert "£5.09m" in page
    assert "£38.14m" in page
    low = page.index("-£5.35m")
    mid = page.index("£5.09m")
    high = page.index("£38.14m")
    assert mid < low < high, "the page must present base, downside, upside in that order"
    assert "£16.92m" in page  # the key sensitivity, same figure as the state


@pytest.mark.parametrize("edit", [("£5.09m", "£5.90m"), ("-£5.35m", "£5.35m")])
def test_editing_a_bound_figure_is_refused(state, page, edit):
    mutated = page.replace(*edit, 1)
    assert mutated != page
    assert "binding.match" in _rules(check(state, mutated))


def test_a_number_retyped_into_prose_is_refused(state, page):
    mutated = page.replace(
        "<h2 id=\"h-economics\">", "<p>The base case is about £5.09m.</p><h2 id=\"h-economics\">"
    )
    assert "numeric.fidelity" in _rules(check(state, mutated))


def test_the_same_figure_cannot_be_quoted_two_different_ways(state, page):
    """The V1 review found one cost quoted as two different ranges in two
    places. Formatters are total functions of the value, so two renderings of
    one field are identical by construction; a hand-edited second copy is a
    retyped number and is refused."""
    mutated = page.replace(
        "<h2 id=\"h-change\">", "<p>Buying that evidence costs £50k to £470k.</p><h2 id=\"h-change\">"
    )
    assert "numeric.fidelity" in _rules(check(state, mutated))


# ---------------------------------------------------------------------------
# Attribution fidelity
# ---------------------------------------------------------------------------


def test_a_seat_card_may_not_quote_another_seats_record(state):
    other = SeatView(
        seat=CommitteeSeat.CISO,
        initial=CommitteePosition(
            id="p2",
            created_at=AT,
            member=CommitteeSeat.CISO,
            phase=PositionPhase.INITIAL,
            recommendation=DecisionAction.REQUEST_EVIDENCE,
            confidence_band=ConfidenceBand.HIGH,
            key_reasons=[KeyReason(text="Regulated workloads were never exercised.")],
        ),
    )
    two_seat = _state(seats=[state.seats[0], other])
    page = render_decision_page(two_seat)
    assert check(two_seat, page) == []

    card = page.split('<article class="seat" data-seat="ciso">')[1].split("</article>")[0]
    swapped = card.replace(
        "seats_by_id[ciso].initial.recommendation", "seats_by_id[cfo].revised.recommendation"
    )
    mutated = page.replace(card, swapped)
    assert mutated != page
    assert "attribution.fidelity" in _rules(check(two_seat, mutated))


def test_attributing_a_page_level_statement_to_a_seat_is_refused(state, page):
    mutated = page.replace(
        '<span data-kriterion-source="economics_interpretation" data-kriterion-format="text">',
        '<span data-kriterion-source="economics_interpretation" data-kriterion-format="text" '
        'data-kriterion-attributed-to="cfo">',
    )
    assert mutated != page
    assert "attribution.fidelity" in _rules(check(state, mutated))


# ---------------------------------------------------------------------------
# Human / machine separation
# ---------------------------------------------------------------------------


def test_the_two_decision_regions_are_separate_and_both_present(state, page):
    assert 'data-kriterion-role="synthetic-recommendation"' in page
    assert 'data-kriterion-role="human-decision"' in page


def test_no_human_decision_is_stated_plainly(state, page):
    human = page.split('data-kriterion-role="human-decision"')[1].split("</section>")[0]
    assert "No human decision has been recorded" in human


def test_the_human_region_may_not_render_the_machines_action(state, page):
    mutated = page.replace(
        '<h2 id="h-human">Human decision</h2>',
        '<h2 id="h-human">Human decision</h2>'
        '<span data-kriterion-source="recommendation.action" '
        'data-kriterion-format="label">DEFER</span>',
    )
    assert "separation.human_ai" in _rules(check(state, mutated))


def test_removing_the_human_decision_region_is_refused(state, page):
    mutated = page.replace('data-kriterion-role="human-decision"', 'data-role="human-decision"')
    assert "separation.regions" in _rules(check(state, mutated))


# ---------------------------------------------------------------------------
# Binding hygiene
# ---------------------------------------------------------------------------


def test_a_binding_pointing_at_a_field_that_does_not_exist_is_refused(state, page):
    mutated = page.replace('data-kriterion-source="economics.npv_mid_gbp"',
                           'data-kriterion-source="economics.npv_best_gbp"', 1)
    assert "binding.resolve" in _rules(check(state, mutated))


def test_a_binding_without_a_format_is_refused(state, page):
    mutated = page.replace(
        '<span data-kriterion-source="economics.npv_mid_gbp" data-kriterion-format="gbp_millions"',
        '<span data-kriterion-source="economics.npv_mid_gbp"',
        1,
    )
    assert mutated != page
    assert "binding.format" in _rules(check(state, mutated))


def test_a_page_with_no_bindings_at_all_is_refused(state):
    assert "binding.present" in _rules(check(state, "<html><body>Fund it.</body></html>"))


# ---------------------------------------------------------------------------
# Routes found by attacking the checker rather than by reading it
#
# Each of these passed cleanly on the first implementation. They are the
# reason the checker looks at more than HTML text nodes.
# ---------------------------------------------------------------------------

ANCHOR = '<h2 id="h-economics">The economics</h2>'


def test_a_claim_parked_in_a_title_attribute_is_refused(state, page):
    """Stripping tags hides attribute text from the prose scan, so a claim in
    a tooltip was invisible to the checker and perfectly visible to a reader."""
    mutated = page.replace(
        ANCHOR, '<p title="The committee recommends a PILOT of £420,000.">x</p>' + ANCHOR
    )
    assert _rules(check(state, mutated))


def test_a_claim_parked_in_an_aria_label_is_refused(state, page):
    """A screen-reader label is narrative delivered to a human."""
    mutated = page.replace(ANCHOR, '<p aria-label="Assurance result: PASS">x</p>' + ANCHOR)
    assert "vocabulary.fidelity" in _rules(check(state, mutated))


def test_a_softened_claim_in_alt_text_is_refused(state, page):
    mutated = page.replace(ANCHOR, '<p alt="resilience was mostly fine">x</p>' + ANCHOR)
    assert "softening" in _rules(check(state, mutated))


def test_text_injected_by_css_content_is_refused(state, page):
    """CSS can put words on the page that no HTML text node contains, and the
    style block is stripped before the prose scan."""
    mutated = page.replace(
        "a { color: var(--accent); }",
        'a { color: var(--accent); } .insight::after { content: " Overall: PASS"; }',
    )
    assert mutated != page
    assert _rules(check(state, mutated))


@pytest.mark.parametrize(
    "sentence",
    [
        "On balance the committee recommends a pilot.",
        "The recommendation is to scale next quarter.",
        "Given the spread, a pilot is recommended.",
        "We recommend a limited pilot.",
    ],
)
def test_a_lowercase_recommendation_claim_in_prose_is_refused(state, page, sentence):
    """The uppercase vocabulary rule does not see "recommends a pilot".
    Making every state word case-insensitive would forbid ordinary English
    ("pilot cohort"), so this targets the actual failure shape instead."""
    mutated = page.replace(ANCHOR, f"<p>{sentence}</p>" + ANCHOR)
    assert "decision.fidelity" in _rules(check(state, mutated))


def test_ordinary_english_using_a_state_word_is_still_allowed(state, page):
    """The rule has to bite on claims without banning the language. A sentence
    that merely contains "pilot" is not a recommendation."""
    mutated = page.replace(ANCHOR, "<p>The pilot cohort ran for twelve weeks.</p>" + ANCHOR)
    assert check(state, mutated) == []


def test_the_headline_sensitivity_and_the_table_cannot_name_different_things(state):
    """One fact, one answer. An artifact whose tornado is not stored in
    magnitude order must not produce a headline naming one parameter and a
    table whose own first row names another under a "widest first" caption."""
    from kriterion.domain.economics import EconomicsResult, TornadoEntry

    unsorted_economics = EconomicsResult(
        id="e", created_at=AT, case_id="fixture-case", discount_rate=0.1,
        npv_low_gbp=-1.0, npv_mid_gbp=1.0, npv_high_gbp=2.0,
        payback_years=None, peak_funding_gbp=0.0,
        tornado=[
            TornadoEntry(assumption_id="uplift", npv_swing_gbp=1_000_000.0),
            TornadoEntry(assumption_id="attribution_factor", npv_swing_gbp=16_000_000.0),
        ],
    )
    skewed = _state(economics=unsorted_economics)
    assert skewed.primary_sensitivity_param == skewed.tornado_rows[0]["parameter"]
    assert check(skewed, render_decision_page(skewed)) == []


# ---------------------------------------------------------------------------
# Fixes from reading the finished page as CIO / CFO / CISO / sponsor
# ---------------------------------------------------------------------------


def test_an_unmapped_sensitivity_parameter_is_stated_not_dressed_up(state, page):
    """This fixture's case id has no parameter->assumption map, so the
    dominant sensitivity cannot be resolved to a ranged Assumption record. The
    page must say that plainly rather than implying the swing is backed by a
    declared, owned assumption.

    (The equivalent assertions for a *mapped* case live in
    test_public_page_coherence.py, against the real canonical page. This
    fixture's failure to resolve is a property of the fixture, not a defect.)
    """
    assert state.primary_sensitivity_assumption is None
    decision = page.split('data-kriterion-role="decision"')[1].split("</section>")[0]
    assert "does not declare as a ranged assumption" in decision


def test_the_critical_failure_count_says_what_it_does_not_count(state, page):
    """A CISO reading "critical failures: 0" above a list of a dozen items
    will read it as "every check passed". The envelope behind this page
    records a non-gating failure and a check that returned no verdict."""
    assert "It is not a count of checks that did not pass" in state.assurance_summary_caveat
    assert state.assurance_unknown_count > 0
    assert "assurance_summary_caveat" in page


def test_one_field_may_not_be_quoted_two_different_ways(state, page):
    """The V1 review found one cost quoted as two different ranges. Figures now
    repeat across sections by design, so the formatter has to be checked."""
    mutated = page.replace(
        '<span data-kriterion-source="economics.npv_mid_gbp" data-kriterion-format="gbp_millions"',
        '<span data-kriterion-source="economics.npv_mid_gbp" data-kriterion-format="gbp"',
        1,
    )
    assert mutated != page
    assert "numeric.consistency" in _rules(check(state, mutated))


def test_repeated_figures_on_the_real_page_agree(state, page):
    """The base valuation appears in the decision snapshot and again in the
    economics section. They must be the same characters."""
    import re as _re

    occurrences = _re.findall(
        r'data-kriterion-source="economics\.npv_mid_gbp"[^>]*>([^<]*)<', page
    )
    assert len(occurrences) >= 2, "expected the base valuation to appear more than once"
    assert len(set(occurrences)) == 1, f"the same figure rendered differently: {set(occurrences)}"
