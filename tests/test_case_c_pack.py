from pathlib import Path

from kriterion.casepack import load_case_pack, load_injection

CASE_C_DIR = Path(__file__).parent.parent / "cases" / "invisible-ai-control-plane"


def test_loads_case_c_with_12_to_15_evidence_items():
    case, items, assumptions = load_case_pack(CASE_C_DIR, created_at="2026-09-05T00:00:00Z")
    assert case.id == "invisible-ai-control-plane"
    assert case.ask.amount_gbp == 2_400_000
    assert "do_nothing" in case.alternatives
    assert "buy_vendor" in case.alternatives
    assert 12 <= len(items) <= 15
    assert len(assumptions) == 2


def test_all_seven_categories_present_in_case_c():
    _, items, _ = load_case_pack(CASE_C_DIR, created_at="2026-09-05T00:00:00Z")
    categories = {item.category.value for item in items}
    assert categories == {
        "MEASURED", "EXTERNAL_REFERENCE", "EXPERT_JUDGMENT", "FORECAST",
        "ASSUMPTION", "INFERENCE", "UNKNOWN",
    }


def test_injection_fixture_is_the_irrelevant_nps_item():
    injected = load_injection(CASE_C_DIR / "injection.toml", created_at="2026-09-05T00:00:00Z")
    assert len(injected) == 1
    assert injected[0].id == "ev-112"
    assert "NPS" in injected[0].claim or "Net Promoter" in injected[0].claim
