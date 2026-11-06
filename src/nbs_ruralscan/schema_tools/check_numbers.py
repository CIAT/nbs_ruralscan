"""Deterministic number-provenance check (cheap first-pass on the [B] defect).

The verbatim guardrail proves the *quote* is real; it does NOT check that the numbers
encoded in an EvidenceUnit's ``relationship`` dict actually come from that quote. The
2026-06 re-extraction found ~34-51% of numeric units had "smuggled" numbers — values
pulled from elsewhere in the paper (discount rates, study counts, table-header units,
cross-row ranges). Two adversarial LLM verify waves caught them by hand.

This module catches the same class deterministically, every build, no model tokens:
every numeric literal in ``relationship`` must also appear in the ``quote``. Misses are
*advisory* (some are legitimately derived — e.g. a %→degree conversion), so this flags
for review rather than failing the build. Explicit closed observed-class summaries
also receive a separate consistency check. Use these as triage before source review;
passing either check does not establish scientific plausibility or suitability.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from decimal import Decimal
from pathlib import Path

# capture leading-dot decimals too (".13" as written in papers, not just "0.13")
_NUM = re.compile(r"\d*\.\d+|\d+")
# thousands grouped with a space (SI style, used by WOCAT/FAO: "1 001 - 1 500 mm"),
# incl. no-break / thin / narrow no-break spaces, and \x0f — a control character some PDF
# fonts emit as their narrow-space glyph (Wichmann 2021 prints "€ 127\x0f862"; caught
# 2026-10-16 when the figure could not be cited from its own quote)
_SPACED_THOUSANDS = re.compile(
    r"(?<![\d.])\d{1,3}(?:[ \u00a0\u2009\u202f\x0f]\d{3})+(?:\.\d+)?(?![\d.])"
)


#: locale DECIMAL COMMA (es/fr/pt): "29,8" = 29.8. A thousands group is 3 digits
#: ("1,637,600"), so requiring 1-2 digits not followed by another digit excludes it.
_DECIMAL_COMMA = re.compile(r"(?<![\d.])\d+,\d{1,2}(?![\d,])")
#: locale THOUSANDS DOT (pt/es): "5.047" = 5047. Genuinely ambiguous with a 3-decimal
#: value, so BOTH readings are emitted - this is a containment check, and offering the
#: alternative reading can only let a correctly-transcribed number match.
_THOUSANDS_DOT = re.compile(r"(?<![\d,])\d{1,3}(?:\.\d{3})+(?![\d.])")
_NUMBER_WORDS = {
    "half": "0.5",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "twelve": "12",
    "fifteen": "15",
    "twenty": "20",
    "doubl(?:ed?|es|ing)|twice|twofold": "2",
    "tripl(?:ed?|es|ing)|threefold|thrice": "3",
    "fourfold|quadrupl(?:ed?|es|ing)": "4",
    "fivefold": "5",
    "halv(?:ed|es|ing)": "0.5",
    "tenfold": "10",
}


def _nums(text: str) -> set[str]:
    """Union of the readings of the text as printed and of its normalised form.

    Normalisation only ever ADDS readings (2026-10-21 retro): NFKC folds typographic
    ligatures ("ﬁve" -> "five") and a thousands group split across a line break
    ("25,\n000") is rejoined, but the as-printed tokens are kept, so no unit that
    matched before can stop matching.
    """
    raw = text or ""
    norm = re.sub(
        r"(\d),\s*\n\s*(\d{3})\b", r"\1,\2", unicodedata.normalize("NFKC", raw)
    )
    out = _nums_one(raw)
    if norm != raw:
        out |= _nums_one(norm)
    # "four and one-half (times)" = 4.5 — Bishop & Stevens 1964 (2026-10-21 retro)
    for word, val in _NUMBER_WORDS.items():
        if val.isdigit() and re.search(
            rf"\b(?:{word})\s+and\s+(?:one-|a\s+)half\b", norm, flags=re.IGNORECASE
        ):
            out.add(f"{val}.5")
    return out


def _nums_one(text: str) -> set[str]:
    """Numeric tokens, comma-stripped, trailing-zero-normalised (e.g. 1,637,600 / 25.0).

    Space-grouped thousands ("1 001") are ALSO added joined ("1001"), so a relationship
    value written as 1001 matches a quote that prints it SI-style (2026-09: every WOCAT
    rainfall class tripped this). The split tokens are kept too, so nothing is lost.

    Locale forms are added too (2026-10, multilingual sweep): a decimal comma ("29,8")
    yields "29.8" and a thousands dot ("5.047") yields "5047", alongside the plain
    comma-stripped reading. Without this every es/fr/pt magnitude failed provenance.
    """
    raw = text or ""
    pre: set[str] = set()
    # spelled-out multipliers (v1.6.2, 2026-10-06): "two to three times", "doubled" —
    # a stated ratio is provenance whether printed as digits or words
    for word, val in _NUMBER_WORDS.items():
        if re.search(rf"\b{word}\b", raw, flags=re.IGNORECASE):
            pre.add(val)
    for m in _DECIMAL_COMMA.findall(raw):
        d = m.replace(",", ".")
        pre.add(d)
        pre.add(d.rstrip("0").rstrip("."))
    for m in _THOUSANDS_DOT.findall(raw):
        pre.add(m.replace(".", ""))
    text = raw.replace(",", "")
    out: set[str] = set()
    for m in _NUM.findall(text):
        out.add(m)
        if "." in m:
            out.add(m.rstrip("0").rstrip("."))  # 25.0 -> 25
    for m in _SPACED_THOUSANDS.findall(text):
        joined = re.sub(
            r"[ \u00a0\u2009\u202f\x0f]", "", m
        )  # keep a decimal part: "3 945.60"
        out.add(joined)
        if "." in joined:
            out.add(joined.rstrip("0").rstrip("."))
    return out | pre


def _floats(toks: set[str]) -> set[float]:
    """Parseable numeric tokens as floats — so 250.0 ≡ 250.00 ≡ 250 and .13 ≡ 0.13."""
    out: set[float] = set()
    for t in toks:
        try:
            out.add(float(t))
        except ValueError:
            pass
    return out


#: Provenance tokens that are never claims (retro 2026-10-07; 1,122 WOCAT false positives):
#: the WOCAT adapter's questionnaire references ("WOCAT QT 6.3", "WOCAT 6.1.flood_impacts",
#: "on the −3…+3 scale"), ISO run dates, and evidence-id references in process notes.
_PROVENANCE = re.compile(
    r"WOCAT\s+(?:QT\s*)?\d(?:\.\d)?(?:\.[a-z_]+)?(?:\s*:)?"
    r"|WOCAT\s+[a-z_]+\.[a-z_]+"
    r"|\bQT\s*\d(?:\.\d)?\b"
    r"|on the [−-]3…\+3 scale"
    r"|\b\d{4}-\d{2}-\d{2}\b"
    r"|\b[eE][vV]_[A-Za-z0-9_]+"
)


def _strip_provenance(text: str) -> str:
    return _PROVENANCE.sub(" ", text)


def _rel_nums(rel: str) -> set[str]:
    """All numeric tokens appearing in a relationship dict (keys are ignored); adapter
    provenance, ISO dates and evidence-id references are not numbers (``_PROVENANCE``)."""
    try:
        data = json.loads(rel)
    except (json.JSONDecodeError, TypeError):
        return _nums_one(_strip_provenance(rel))
    # " ; " not " ": adjacent values (observed_min 251, observed_max 500) must never fuse
    # into a space-grouped "thousands" number on the relationship side
    vals = " ; ".join(_strip_provenance(str(v)) for v in _walk(data))
    # claims are read as written: normalisation widens only the QUOTE side, so it can
    # only ever make a unit pass, never demand a number its quote lacks
    return _nums_one(vals)


def _walk(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)
    else:
        yield obj


def observed_range_mismatches(relationship: dict) -> list[dict]:
    """Check compatibility with explicit closed observed classes in the same unit.

    Quote-token containment deliberately accepts alternative numeric readings. It
    cannot catch a summary of 1 mm when the class itself prints 1 000 mm. This
    separate check uses only unambiguous closed classes; open ends, prose labels,
    mixed units and locale-ambiguous punctuation remain for source review.
    Measured extrema may lie within the outer selected bins: they need not equal
    bin edges. Every selected bin must remain compatible with the extrema. Class
    envelopes never imply support across gaps or suitability limits. Nothing is
    converted, corrected or approved here.
    """
    if not isinstance(relationship, dict):
        return []
    if relationship.get("type") != "observed_presence":
        return []
    invalid = []
    for field in ("observed_min", "observed_max"):
        if field not in relationship:
            continue
        stored = relationship[field]
        if type(stored) not in (int, float) or not Decimal(str(stored)).is_finite():
            invalid.append(
                {
                    "field": field,
                    "stored": stored,
                    "problem": "present observed summary must be a finite number; "
                    "omit an unknown summary instead",
                }
            )
    if invalid:
        return invalid
    if (
        "observed_min" in relationship
        and "observed_max" in relationship
        and relationship["observed_min"] > relationship["observed_max"]
    ):
        # Continue to class checks when possible, so a truncated maximum still
        # receives its source-class diagnostic. Fall back to the ordering issue
        # if the classes cannot be interpreted without guessing.
        invalid = [
            {
                "field": "observed_max",
                "stored": relationship["observed_max"],
                "problem": "observed maximum is below observed minimum",
            }
        ]
    classes = relationship.get("observed_classes")
    unit = relationship.get("unit")
    if (
        not isinstance(classes, list)
        or not classes
        or not isinstance(unit, str)
        or not unit.strip()
    ):
        return invalid
    bounds = []
    for label in classes:
        if not isinstance(label, str):
            return invalid
        label = unicodedata.normalize("NFKC", label)
        if "," in label or _THOUSANDS_DOT.search(label):
            return invalid  # do not choose a locale-dependent interpretation
        label = _SPACED_THOUSANDS.sub(
            lambda m: re.sub(r"[ \u00a0\u2009\u202f\x0f]", "", m[0]), label
        )
        match = re.fullmatch(
            r"\s*(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)"
            r"\s*([A-Za-z%][A-Za-z0-9/% ^.-]*)\s*",
            label,
        )
        if not match or match[3].strip() != unit.strip():
            return invalid
        low, high = Decimal(match[1]), Decimal(match[2])
        if low > high:
            return invalid
        bounds.append((low, high))
    envelope = {
        "observed_min": min(low for low, _ in bounds),
        "observed_max": max(high for _, high in bounds),
    }
    compatible = {
        "observed_min": (
            min(low for low, _ in bounds),
            min(high for _, high in bounds),
        ),
        "observed_max": (
            max(low for low, _ in bounds),
            max(high for _, high in bounds),
        ),
    }
    out = []
    for field, expected in envelope.items():
        if field not in relationship:
            continue
        stored = relationship[field]
        value = Decimal(str(stored))
        low, high = compatible[field]
        if not low <= value <= high:
            out.append(
                {"field": field, "stored": stored, "class_envelope": float(expected)}
            )
    return out or invalid


def check(schema_root: str | Path) -> list[dict]:
    """Return missing-number or observed-class-summary findings for review."""
    ev = Path(schema_root) / "registers" / "EV_evidence_register.csv"
    if not ev.exists():
        return []
    flagged: list[dict] = []
    with ev.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rel = (r.get("relationship") or "").strip()
            if not rel:
                continue
            q = _nums(r.get("quote", ""))
            qf = _floats(q)
            # a relationship number is "missing" only if neither its string nor its float
            # value appears in the quote — suppresses pure decimal-formatting false positives
            # (250.0 vs 250.00, .13 vs 0.13) while still flagging real conversions/expansions.
            missing = sorted(
                n for n in _rel_nums(rel) if n not in q and not (_floats({n}) & qf)
            )
            try:
                summary = observed_range_mismatches(json.loads(rel))
            except (json.JSONDecodeError, TypeError):
                summary = []
            if missing or summary:
                flagged.append(
                    {
                        "evidence_id": r["evidence_id"],
                        "source_id": r["source_id"],
                        "variable": r["variable"],
                        "missing_numbers": missing,
                        **({"observed_range_mismatches": summary} if summary else {}),
                    }
                )
    return flagged


def main() -> int:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("schema")
    flagged = check(root)
    total_rel = sum(
        1
        for r in csv.DictReader(
            (root / "registers" / "EV_evidence_register.csv").open(encoding="utf-8")
        )
        if (r.get("relationship") or "").strip()
    )
    if not flagged:
        print(
            f"NUMBER-PROVENANCE OK: {total_rel} relationships have no missing-number "
            "or explicit observed-class-summary finding."
        )
        return 0
    print(
        f"NUMBER-PROVENANCE: {len(flagged)}/{total_rel} relationships have missing "
        "numbers or inconsistent observed summaries (review; no automatic correction):"
    )
    for x in flagged:
        print(f"  [{x['evidence_id']}] {x['variable']}: missing {x['missing_numbers']}")
        for issue in x.get("observed_range_mismatches", []):
            detail = issue.get("problem") or (
                f"literal class envelope={issue['class_envelope']}"
            )
            print(f"    {issue['field']}={issue['stored']}; {detail}")
    return 0  # advisory — never fails the build


if __name__ == "__main__":
    raise SystemExit(main())
