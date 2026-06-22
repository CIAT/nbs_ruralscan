"""Deterministic number-provenance check (cheap first-pass on the [B] defect).

The verbatim guardrail proves the *quote* is real; it does NOT check that the numbers
encoded in an EvidenceUnit's ``relationship`` dict actually come from that quote. The
2026-06 re-extraction found ~34-51% of numeric units had "smuggled" numbers — values
pulled from elsewhere in the paper (discount rates, study counts, table-header units,
cross-row ranges). Two adversarial LLM verify waves caught them by hand.

This module catches the same class deterministically, every build, no model tokens:
every numeric literal in ``relationship`` must also appear in the ``quote``. Misses are
*advisory* (some are legitimately derived — e.g. a %→degree conversion), so this flags
for review rather than failing the build. Use it as a triage filter BEFORE spending an
LLM verify pass, and to stop regressions.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

# capture leading-dot decimals too (".13" as written in papers, not just "0.13")
_NUM = re.compile(r"\d*\.\d+|\d+")


def _nums(text: str) -> set[str]:
    """Numeric tokens, comma-stripped, trailing-zero-normalised (e.g. 1,637,600 / 25.0)."""
    out: set[str] = set()
    for m in _NUM.findall((text or "").replace(",", "")):
        out.add(m)
        if "." in m:
            out.add(m.rstrip("0").rstrip("."))  # 25.0 -> 25
    return out


def _floats(toks: set[str]) -> set[float]:
    """Parseable numeric tokens as floats — so 250.0 ≡ 250.00 ≡ 250 and .13 ≡ 0.13."""
    out: set[float] = set()
    for t in toks:
        try:
            out.add(float(t))
        except ValueError:
            pass
    return out


def _rel_nums(rel: str) -> set[str]:
    """All numeric tokens appearing in a relationship dict (keys are ignored)."""
    try:
        data = json.loads(rel)
    except (json.JSONDecodeError, TypeError):
        return _nums(rel)
    vals = " ".join(str(v) for v in _walk(data))
    return _nums(vals)


def _walk(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)
    else:
        yield obj


def check(schema_root: str | Path) -> list[dict]:
    """Return EV rows whose relationship carries a number absent from the quote."""
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
            if missing:
                flagged.append(
                    {
                        "evidence_id": r["evidence_id"],
                        "source_id": r["source_id"],
                        "variable": r["variable"],
                        "missing_numbers": missing,
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
            f"NUMBER-PROVENANCE OK: all {total_rel} numeric units' numbers trace to their quote."
        )
        return 0
    print(
        f"NUMBER-PROVENANCE: {len(flagged)}/{total_rel} numeric units carry a number "
        f"absent from the quote (review — some may be legitimately derived):"
    )
    for x in flagged:
        print(f"  [{x['evidence_id']}] {x['variable']}: missing {x['missing_numbers']}")
    return 0  # advisory — never fails the build


if __name__ == "__main__":
    raise SystemExit(main())
