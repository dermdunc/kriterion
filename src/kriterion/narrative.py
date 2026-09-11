"""Narrative integrity (ADR-012).

    Every material statement presented to a decision-maker must be traceable
    to the underlying decision state, and must not strengthen, soften,
    contradict or invent its meaning.

Kriterion exists to expose decision narratives that overstate their evidence.
Its own V1 review found four of those inside Kriterion: an assurance `fail`
rendered as the invented word "PARTIAL"; a producer decision attributed to
reasoning its decider never performed; an authored fixture described as an
independent measurement; and one figure quoted two different ways in two
places. The computations were right every time. The sentence describing them
was not.

So this is an invariant, not a service. It works in two halves:

**Binding.** `bind()` is the only sanctioned way to put a material value on a
page. It stamps the element with the state path the value came from and the
formatter used. `check()` then re-resolves every path against the authoritative
`DecisionState` and re-formats it, and reports any element whose text is not
exactly what the state says. A renderer therefore cannot write FAIL as PARTIAL,
because the checker recomputes FAIL from the source record.

**Unbound prose.** Binding alone would still allow a hand-written sentence
beside a correct figure. So the checker also extracts every text node that is
*not* inside a bound element and refuses:

  - any currency amount, percentage or large number (numeric fidelity — all
    numbers must be rendered from canonical fields, never retyped in prose);
  - any state-vocabulary token: a `DecisionAction`, `EvidenceCategory`,
    `Strength`/`ConfidenceBand`, or assurance outcome (decision and epistemic
    fidelity — an unbound "PILOT" in prose is exactly how a DEFER becomes a
    pilot recommendation);
  - any softening or promotion word (PARTIAL, mostly, broadly, proven,
    verified, no issue, ...). Bound text is exempt because it is already
    checked against the record character for character: if a source claim says
    "partially", suppressing the source's own word would be its own distortion.

**What this does and does not prove.** It proves every material claim on the
page is a deterministic function of committed artifacts, and that no prose
around those claims restates, softens or invents one. It does *not* prove that
a derived English sentence (e.g. `DecisionState.economics_interpretation`) is a
*fair* summary of the numbers it is computed from — only that it is computed
from them and cannot be edited by hand without the checker noticing. Judging
fairness stays a human job, which is the honest boundary.
"""

from __future__ import annotations

import html as html_lib
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from kriterion.domain.enums import ConfidenceBand, DecisionAction
from kriterion.domain.evidence import EvidenceCategory, Strength

SOURCE_ATTR = "data-kriterion-source"
FORMAT_ATTR = "data-kriterion-format"
ROLE_ATTR = "data-kriterion-role"
ACTOR_ATTR = "data-kriterion-attributed-to"
EVIDENCE_ATTR = "data-evidence-id"


# ---------------------------------------------------------------------------
# Formatters. A binding names one of these; the checker applies the same one.
# There is deliberately no "free text" formatter: every format is a total
# function of the value, so two places quoting the same field cannot disagree.
# ---------------------------------------------------------------------------


def _plain(value: Any) -> str:
    if value is None:
        return "not recorded"
    if isinstance(value, bool):
        return "yes" if value else "no"
    # Every Kriterion enum subclasses `str`, so an isinstance(str) test would
    # match first and `str(value)` would render `EvidenceCategory.MEASURED`
    # instead of `MEASURED`. Enum is checked first, deliberately.
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _gbp(value: Any) -> str:
    amount = float(value)
    sign = "-" if amount < 0 else ""
    return f"{sign}£{abs(amount):,.0f}"


def _gbp_millions(value: Any) -> str:
    amount = float(value)
    sign = "-" if amount < 0 else ""
    return f"{sign}£{abs(amount) / 1_000_000:.2f}m"


def _gbp_thousands(value: Any) -> str:
    amount = float(value)
    sign = "-" if amount < 0 else ""
    return f"{sign}£{abs(amount) / 1_000:,.0f}k"


def _percent(value: Any) -> str:
    return f"{float(value) * 100:g}%"


def _count(value: Any) -> str:
    return str(int(value))


def _years(value: Any) -> str:
    if value is None:
        return "not reached inside the modelled horizon"
    return f"{float(value):.1f} years"


def _list_semi(value: Any) -> str:
    return "; ".join(_plain(v) for v in value)


def _list_dot(value: Any) -> str:
    return " · ".join(_plain(v) for v in value)


def _range_percent(value: Any) -> str:
    lo, hi = value
    return f"{_percent(lo)}–{_percent(hi)}"


def _range_gbp(value: Any) -> str:
    lo, hi = value
    return f"{_gbp(lo)}–{_gbp(hi)}"


def _range_plain(value: Any) -> str:
    lo, hi = value
    return f"{_plain(lo)}–{_plain(hi)}"


def _label(value: Any) -> str:
    """Enum value as a human label: `cro_compliance` -> `CRO COMPLIANCE`.
    A total function of the value, so it cannot smuggle in a new word."""
    return _plain(value).replace("_", " ").upper()


FORMATTERS = {
    "text": _plain,
    "upper": lambda v: _plain(v).upper(),
    "label": _label,
    "gbp": _gbp,
    "gbp_millions": _gbp_millions,
    "gbp_thousands": _gbp_thousands,
    "percent": _percent,
    "count": _count,
    "years": _years,
    "list_semi": _list_semi,
    "list_dot": _list_dot,
    "range_percent": _range_percent,
    "range_gbp": _range_gbp,
    "range_plain": _range_plain,
}


class NarrativeError(ValueError):
    """A binding could not be resolved or formatted at render time."""


# ---------------------------------------------------------------------------
# Path resolution against a DecisionState
# ---------------------------------------------------------------------------

_SEGMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:\[([^\]]+)\])?$")


def _parse_path(path: str) -> list[tuple[str, str | None]]:
    segments: list[tuple[str, str | None]] = []
    for raw in path.split("."):
        match = _SEGMENT_RE.match(raw)
        if match is None:
            raise NarrativeError(f"unparseable state path segment {raw!r} in {path!r}")
        segments.append((match.group(1), match.group(2)))
    return segments


def resolve(state: Any, path: str) -> Any:
    """Walk a dotted state path. Raises NarrativeError rather than returning
    None for a path that does not exist: a silently-None binding would render
    as "not recorded" and quietly turn a typo into an honest-looking absence.
    """
    obj: Any = state
    for name, key in _parse_path(path):
        if isinstance(obj, dict):
            if name not in obj:
                raise NarrativeError(f"{path!r}: no key {name!r}")
            obj = obj[name]
        else:
            if not hasattr(obj, name):
                raise NarrativeError(f"{path!r}: {type(obj).__name__} has no attribute {name!r}")
            obj = getattr(obj, name)
        if key is not None:
            if isinstance(obj, dict):
                if key not in obj:
                    raise NarrativeError(f"{path!r}: no entry {key!r}")
                obj = obj[key]
            elif isinstance(obj, (list, tuple)):
                try:
                    obj = obj[int(key)]
                except (ValueError, IndexError) as exc:
                    raise NarrativeError(f"{path!r}: bad index {key!r}") from exc
            else:
                raise NarrativeError(f"{path!r}: {type(obj).__name__} is not indexable")
    return obj


def render_value(state: Any, path: str, fmt: str) -> str:
    if fmt not in FORMATTERS:
        raise NarrativeError(f"unknown format {fmt!r} for {path!r}")
    try:
        return FORMATTERS[fmt](resolve(state, path))
    except NarrativeError:
        raise
    except Exception as exc:  # a malformed value is a refusal, never a blank
        raise NarrativeError(f"{path!r} could not be formatted as {fmt!r}: {exc}") from exc


def bind(
    state: Any,
    path: str,
    *,
    fmt: str = "text",
    tag: str = "span",
    cls: str | None = None,
    role: str | None = None,
    actor: str | None = None,
    evidence_id: str | None = None,
) -> str:
    """Render one value from the decision state, stamped with its provenance.

    The value is escaped, so a bound element never contains markup — which is
    also what lets the checker treat its inner text as a literal.
    """
    text = render_value(state, path, fmt)
    attrs = [f'{SOURCE_ATTR}="{html_lib.escape(path, quote=True)}"', f'{FORMAT_ATTR}="{fmt}"']
    if cls:
        attrs.append(f'class="{html_lib.escape(cls, quote=True)}"')
    if role:
        attrs.append(f'{ROLE_ATTR}="{html_lib.escape(role, quote=True)}"')
    if actor:
        attrs.append(f'{ACTOR_ATTR}="{html_lib.escape(actor, quote=True)}"')
    if evidence_id:
        attrs.append(f'{EVIDENCE_ATTR}="{html_lib.escape(evidence_id, quote=True)}"')
    return f"<{tag} {' '.join(attrs)}>{html_lib.escape(text)}</{tag}>"


# ---------------------------------------------------------------------------
# The checker
# ---------------------------------------------------------------------------


@dataclass(frozen=True, kw_only=True)
class Violation:
    rule: str
    detail: str

    def __str__(self) -> str:  # pragma: no cover - formatting only
        return f"[{self.rule}] {self.detail}"


_BOUND_RE = re.compile(
    r"<(?P<tag>[A-Za-z][A-Za-z0-9]*)(?P<attrs>[^>]*?\b"
    + SOURCE_ATTR
    + r'="(?P<src>[^"]*)"[^>]*?)>(?P<inner>.*?)</(?P=tag)>',
    re.S,
)
_FORMAT_RE = re.compile(FORMAT_ATTR + r'="([^"]*)"')
_ACTOR_RE = re.compile(ACTOR_ATTR + r'="([^"]*)"')
_ROLE_RE = re.compile(ROLE_ATTR + r'="([^"]*)"')
_STRIP_RE = re.compile(r"<style\b.*?</style>|<script\b.*?</script>|<!--.*?-->", re.S | re.I)
_CARD_RE = re.compile(r'<li\b[^>]*\b' + EVIDENCE_ATTR + r'="([^"]+)"[^>]*>(.*?)</li>', re.S)
_SEAT_RE = re.compile(r'<article\b[^>]*\bdata-seat="([^"]+)"[^>]*>(.*?)</article>', re.S)
_TAG_RE = re.compile(r"<[^>]+>")

# Numbers, currency and percentages must come from canonical fields.
_NUMERIC_RE = re.compile(r"£\s?[\d,.]+|\b\d[\d,]*(?:\.\d+)?\s?%|\b\d[\d,]{3,}\b")

# Attributes whose text a human or a screen reader actually receives. Stripping
# tags hides these from the prose scan, so a claim parked in a `title=` or
# `aria-label=` would be invisible to the checker and perfectly visible to a
# reader. Found by probing the checker rather than by reading it.
_VISIBLE_ATTR_RE = re.compile(
    r'\b(title|alt|aria-label|aria-description|aria-roledescription|placeholder)'
    r'\s*=\s*"([^"]*)"',
    re.I,
)

# CSS can inject text that no HTML text node contains. The style block is
# stripped before the prose scan, so `content:` is the one declaration that
# has to be looked at directly.
_CSS_CONTENT_RE = re.compile(r"content\s*:\s*(['\"])(.*?)\1", re.S)

# The uppercase vocabulary check does not see "the committee recommends a
# pilot". Rather than make every state word case-insensitive (which would
# forbid ordinary English like "pilot cohort"), this targets the actual
# failure: a recommendation verb next to a decision action, in any case.
_ACTION_WORDS = "|".join(
    sorted((a.value.replace("_", "[ _]") for a in DecisionAction), key=len, reverse=True)
)
_RECOMMENDATION_PHRASE_RE = re.compile(
    r"\brecommend(?:s|ed|ing|ation|ations)?\b[^.;]{0,60}?\b(?:" + _ACTION_WORDS + r")\b"
    r"|\b(?:" + _ACTION_WORDS + r")\b[^.;]{0,30}?\bis\s+recommended\b",
    re.I,
)

# State vocabulary. An uppercase occurrence of any of these in prose is a
# claim about the decision state, and claims must be bound.
_VOCABULARY = (
    {a.value for a in DecisionAction}
    | {c.value for c in EvidenceCategory}
    | {s.value for s in Strength}
    | {c.value for c in ConfidenceBand}
    | {"PASS", "FAIL", "FAILED", "INDETERMINATE", "REVIEW_REQUIRED", "STALE", "INCOMPLETE"}
)
_VOCABULARY_RE = re.compile(r"\b(" + "|".join(sorted(_VOCABULARY, key=len, reverse=True)) + r")\b")

# Words that soften a failure or promote an assumption. Banned everywhere in
# the page's own prose, in any case. Each one is a real regression: "PARTIAL"
# shipped in place of a source FAIL, and "proven"/"verified" are how an
# ASSUMPTION stops being an assumption.
_SOFTENING_WORDS = (
    "partial",
    "partially",
    "mostly",
    "broadly",
    "largely",
    "satisfactory",
    "needs attention",
    "minor issue",
    "minor concern",
    "no issue",
    "no issues",
    "not detected",
    "proven",
    "proves",
    "verified",
    "confirmed",
    "compliant",
    "clean bill",
    "on track",
)
_SOFTENING_RE = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in _SOFTENING_WORDS) + r")\b", re.I
)


def _strip_bound(page: str) -> str:
    return _BOUND_RE.sub("  ", page)


def unbound_text(page: str) -> str:
    """Every text node on the page that is NOT inside a bound element."""
    without_bound = _strip_bound(page)
    without_assets = _STRIP_RE.sub(" ", without_bound)
    text = _TAG_RE.sub(" ", without_assets)
    return html_lib.unescape(text)


def _bindings(page: str) -> list[dict[str, Any]]:
    out = []
    for match in _BOUND_RE.finditer(page):
        attrs = match.group("attrs")
        fmt_match = _FORMAT_RE.search(attrs)
        actor_match = _ACTOR_RE.search(attrs)
        role_match = _ROLE_RE.search(attrs)
        out.append(
            {
                "path": html_lib.unescape(match.group("src")),
                "format": fmt_match.group(1) if fmt_match else None,
                "actor": actor_match.group(1) if actor_match else None,
                "role": role_match.group(1) if role_match else None,
                "inner": match.group("inner"),
                "span": match.span(),
            }
        )
    return out


def _regions(page: str) -> dict[str, str]:
    """Top-level `<section data-kriterion-role="...">` blocks, by role.

    Sections are never nested in the decision page, so a non-greedy match to
    the next `</section>` is exact.
    """
    regions: dict[str, str] = {}
    for match in re.finditer(
        r'<section\b[^>]*?' + ROLE_ATTR + r'="([^"]+)"[^>]*?>(.*?)</section>', page, re.S
    ):
        regions.setdefault(match.group(1), "")
        regions[match.group(1)] += match.group(2)
    return regions


def check(state: Any, page: str) -> list[Violation]:
    """Re-derive every material claim on `page` from `state`.

    Returns the violations found. An empty list is the only publishable
    result: `kriterion decision-page` refuses to write a page with any.
    """
    violations: list[Violation] = []
    bindings = _bindings(page)

    if not bindings:
        violations.append(
            Violation(rule="binding.present", detail="the page contains no bound values at all")
        )

    # --- B1/B2/B3: every bound value matches the state, exactly -----------
    for binding in bindings:
        path = binding["path"]
        fmt = binding["format"]
        if fmt is None:
            violations.append(
                Violation(rule="binding.format", detail=f"{path}: binding has no {FORMAT_ATTR}")
            )
            continue
        if "<" in binding["inner"]:
            violations.append(
                Violation(
                    rule="binding.literal",
                    detail=f"{path}: a bound element contains markup, so its text is not a literal",
                )
            )
            continue
        try:
            expected = render_value(state, path, fmt)
        except NarrativeError as exc:
            violations.append(Violation(rule="binding.resolve", detail=str(exc)))
            continue
        actual = html_lib.unescape(binding["inner"])
        if actual != expected:
            violations.append(
                Violation(
                    rule="binding.match",
                    detail=(
                        f"{path}: page shows {actual!r}, but the decision state says "
                        f"{expected!r} (format {fmt})"
                    ),
                )
            )

    # --- N4: attribution fidelity ----------------------------------------
    for binding in bindings:
        actor = binding["actor"]
        if actor is None:
            continue
        expected_prefix = f"seats_by_id[{actor}]"
        if not binding["path"].startswith(expected_prefix):
            violations.append(
                Violation(
                    rule="attribution.fidelity",
                    detail=(
                        f"text attributed to {actor!r} is sourced from {binding['path']!r}, "
                        f"which is not that actor's own record"
                    ),
                )
            )

    # --- N1/N2/N3: unbound prose may carry no claims ----------------------
    # Text a reader receives that is not an HTML text node counts as prose:
    # attribute text (tooltips, screen-reader labels) and CSS-injected content
    # are both stripped before the scan below, so they are folded in here.
    prose = unbound_text(page)
    for attr_match in _VISIBLE_ATTR_RE.finditer(page):
        name, value = attr_match.group(1), html_lib.unescape(attr_match.group(2))
        if value.strip():
            prose += f"\n{value}\n"
    for style_match in re.finditer(r"<style\b.*?</style>", page, re.S | re.I):
        for content_match in _CSS_CONTENT_RE.finditer(style_match.group(0)):
            injected = content_match.group(2)
            if re.search(r"[A-Za-z0-9]", injected):
                violations.append(
                    Violation(
                        rule="numeric.fidelity",
                        detail=(
                            f"the stylesheet injects the text {injected!r} via a `content:` "
                            "declaration — text a reader sees must come from a bound value, not "
                            "from CSS the checker cannot trace"
                        ),
                    )
                )

    for match in _RECOMMENDATION_PHRASE_RE.finditer(prose):
        violations.append(
            Violation(
                rule="decision.fidelity",
                detail=(
                    f"unbound prose reads {match.group(0).strip()!r} — what the model recommended "
                    "must be rendered from recommendation.action, not asserted in a sentence"
                ),
            )
        )

    for match in _NUMERIC_RE.finditer(prose):
        violations.append(
            Violation(
                rule="numeric.fidelity",
                detail=(
                    f"unbound prose contains the figure {match.group(0).strip()!r} — every "
                    "number must be rendered from a canonical field, not retyped"
                ),
            )
        )
    for match in _VOCABULARY_RE.finditer(prose):
        violations.append(
            Violation(
                rule="vocabulary.fidelity",
                detail=(
                    f"unbound prose contains the state token {match.group(0)!r} — a claim about "
                    "the decision state must be bound to the record that makes it"
                ),
            )
        )
    # Bound text is checked against the source record already, so a softening
    # word inside one is the source's own word and suppressing it would be its
    # own distortion. The ban applies to the page's own prose.
    for match in _SOFTENING_RE.finditer(prose):
        violations.append(
            Violation(
                rule="softening",
                detail=(
                    f"the page contains {match.group(0)!r}, which strengthens or softens the "
                    "meaning of a source state"
                ),
            )
        )

    # --- N5: human/AI separation -----------------------------------------
    regions = _regions(page)
    for role in ("synthetic-recommendation", "human-decision"):
        if role not in regions:
            violations.append(
                Violation(
                    rule="separation.regions",
                    detail=f"the page has no <section {ROLE_ATTR}=\"{role}\"> region",
                )
            )
    human_region = regions.get("human-decision", "")
    for binding in _bindings(human_region):
        if binding["path"].startswith("recommendation"):
            violations.append(
                Violation(
                    rule="separation.human_ai",
                    detail=(
                        f"the human-decision region renders {binding['path']!r}: the synthetic "
                        "recommendation and the human decision must never share a field"
                    ),
                )
            )
    if getattr(state, "human_decision", None) is None:
        for binding in _bindings(human_region):
            # A *field of the record*, not a derived status string about its
            # absence: `human_decision.action` is a fabricated decision,
            # `human_decision_status` is the honest statement that none exists.
            if binding["path"] == "human_decision" or binding["path"].startswith("human_decision."):
                violations.append(
                    Violation(
                        rule="separation.human_ai",
                        detail=(
                            "no human decision is recorded, but the human-decision region "
                            f"renders {binding['path']!r}"
                        ),
                    )
                )

    # --- N8: the recommendation headline is the recommendation ------------
    headline = [b for b in bindings if b["role"] == "recommendation-action"]
    if getattr(state, "recommendation", None) is not None:
        if len(headline) != 1:
            violations.append(
                Violation(
                    rule="decision.fidelity",
                    detail=(
                        f"expected exactly one recommendation-action binding, found {len(headline)}"
                    ),
                )
            )
        elif headline[0]["path"] != "recommendation.action":
            violations.append(
                Violation(
                    rule="decision.fidelity",
                    detail=(
                        "the recommendation headline is sourced from "
                        f"{headline[0]['path']!r}, not recommendation.action"
                    ),
                )
            )
    elif headline:
        violations.append(
            Violation(
                rule="decision.fidelity",
                detail="the page shows a recommendation headline but no recommendation is recorded",
            )
        )

    # --- N6/N7: unknowns and imported assurance items cannot be dropped ---
    rendered_ids = set(re.findall(EVIDENCE_ATTR + r'="([^"]+)"', page))
    required: dict[str, str] = {}
    for item in getattr(state, "unknown_evidence", []):
        required[item.id] = "an UNKNOWN ledger item"
    assurance = getattr(state, "assurance", None)
    if assurance is not None:
        for item in assurance.items:
            required[item.id] = "an imported assurance item"
    for item_id, why in sorted(required.items()):
        if item_id not in rendered_ids:
            violations.append(
                Violation(
                    rule="unknown.preservation",
                    detail=f"{item_id} is {why} and does not appear on the page",
                )
            )

    # --- N9a: a card about item X may only render item X --------------------
    # Binding alone does not stop a card labelled `ev-012` from rendering
    # `ev-003`'s category: both would re-derive correctly. The card's own
    # identity has to constrain what may appear inside it.
    for match in _CARD_RE.finditer(page):
        card_id, inner = match.group(1), match.group(2)
        for binding in _bindings(inner):
            if f"[{card_id}]" not in binding["path"]:
                violations.append(
                    Violation(
                        rule="evidence.attribution",
                        detail=(
                            f"the card for {card_id} renders {binding['path']!r}, which is "
                            "another record"
                        ),
                    )
                )

    # --- N4a: a seat's card may only render that seat's own records ---------
    for match in _SEAT_RE.finditer(page):
        seat_id, inner = match.group(1), match.group(2)
        for binding in _bindings(inner):
            path = binding["path"]
            if not path.startswith("seats_by_id["):
                continue  # a page-level derived status, not a claim about this seat
            if not path.startswith(f"seats_by_id[{seat_id}]"):
                violations.append(
                    Violation(
                        rule="attribution.fidelity",
                        detail=(
                            f"the card for seat {seat_id!r} renders {path!r}, which belongs to "
                            "another seat"
                        ),
                    )
                )
            elif binding["actor"] != seat_id:
                violations.append(
                    Violation(
                        rule="attribution.fidelity",
                        detail=(
                            f"the card for seat {seat_id!r} renders {path!r} without attributing "
                            "it to that seat"
                        ),
                    )
                )

    # --- N9: every rendered evidence item shows its own epistemic class ---
    bound_paths = {b["path"] for b in bindings}
    for item_id in sorted(rendered_ids):
        wanted = {
            f"evidence_by_id[{item_id}].category",
            f"assurance.items_by_id[{item_id}].category",
        }
        if not (wanted & bound_paths):
            violations.append(
                Violation(
                    rule="epistemic.fidelity",
                    detail=(
                        f"{item_id} is rendered without a bound epistemic category — an item "
                        "shown without its class can be read as a fact"
                    ),
                )
            )

    return violations


__all__ = [
    "FORMATTERS",
    "NarrativeError",
    "Violation",
    "bind",
    "check",
    "render_value",
    "resolve",
    "unbound_text",
]
