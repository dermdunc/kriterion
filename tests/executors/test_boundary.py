"""Non-negotiable invariant 6 (docs/v0-plan.md Section 15): hekton_llm may
be imported ONLY inside src/kriterion/executors/. This test greps for
violations rather than trusting code review to catch every future addition.
"""

from pathlib import Path

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "kriterion"
ALLOWED_DIR = SRC_ROOT / "executors"


def test_hekton_llm_imported_only_in_executors_package():
    violations = []
    for path in SRC_ROOT.rglob("*.py"):
        if ALLOWED_DIR in path.parents or path.parent == ALLOWED_DIR:
            continue
        text = path.read_text()
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("import hekton_llm") or stripped.startswith("from hekton_llm"):
                violations.append(f"{path.relative_to(SRC_ROOT.parent.parent)}:{lineno}: {stripped}")

    assert not violations, "hekton_llm imported outside kriterion.executors:\n" + "\n".join(
        violations
    )


def test_no_import_or_shared_file_with_hekton_assurance_lab():
    """Section 2's non-negotiable factory-output boundary: zero CODE coupling
    to hekton-assurance-lab, in either direction. ADR-007 (docs/decisions.md,
    2026-09-11) allows consuming assurance evidence as versioned JSON
    *documents* through src/kriterion/assurance/ — a data contract read by a
    tolerant parser, not an import; this test still guarantees no Python edge
    (no import, no repo-path reference) ever exists in either direction."""
    violations = []
    for path in SRC_ROOT.rglob("*.py"):
        text = path.read_text()
        if "hekton_assurance" in text or "hekton-assurance-lab" in text:
            violations.append(str(path.relative_to(SRC_ROOT.parent.parent)))
    assert not violations, "reference to hekton-assurance-lab found in:\n" + "\n".join(violations)
