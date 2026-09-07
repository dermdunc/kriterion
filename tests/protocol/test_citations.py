from kriterion.protocol.citations import extract_known_evidence_refs


def test_extracts_known_refs_deduplicated_and_ordered():
    text = "See evidence [ev-024] and also [ev-013], plus ev-024 again."
    result = extract_known_evidence_refs(text, known_ids={"ev-024", "ev-013"})
    assert result == ["ev-024", "ev-013"]


def test_ignores_unknown_ids():
    text = "Citing ev-999 which does not exist, and ev-001 which does."
    result = extract_known_evidence_refs(text, known_ids={"ev-001"})
    assert result == ["ev-001"]


def test_returns_empty_list_when_nothing_cited():
    assert extract_known_evidence_refs("No citations here.", known_ids={"ev-001"}) == []
