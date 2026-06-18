"""Deterministic quote-context check (the too-narrow-quote defect).

A verbatim quote can still be useless if it's an isolated table cell — "30-40 pt",
"873.60", "Located in protected area" — with no surrounding sentence or table
caption/header to say what the number means, whether it's a suitability claim, or
whether the scope is species vs practice. 2026-06-18 measurement: ~11% of active units
were <=10 words, and the short tail is where table-garble / smuggled-unit / off-scope /
species-envelope defects hide.

Rule (extract-evidence skill #9): a quote must carry the full threshold SENTENCE plus the
table caption/header that defines the variable & unit — never a bare cell.

This flags active, unreviewed units whose quote is shorter than `MIN_WORDS`. Advisory
(some legitimately-short claims exist), so it flags for review, never fails the build.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
MIN_WORDS = 10


def check(ev_path: str | Path | None = None) -> list[dict]:
    """Return advisory narrow-quote flags: [{evidence_id, words, quote}]."""
    path = Path(ev_path) if ev_path else EV
    flags: list[dict] = []
    if not path.exists():
        return flags
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("review_state") or "") == "dropped":
                continue
            if (r.get("reviewer_ok") or "").lower() == "true":
                continue
            if r.get("use_role") == "dataset":
                continue
            if "[VERIFY-FLAG" in (r.get("attribution") or ""):
                continue
            q = (r.get("quote") or "").split()
            if 0 < len(q) < MIN_WORDS:
                flags.append(
                    {"evidence_id": r["evidence_id"], "words": len(q), "quote": " ".join(q)}
                )
    return flags


def main(argv: list[str] | None = None) -> int:
    flags = check(argv[0] if argv else None)
    if not flags:
        print(f"QUOTE CHECK: no active unreviewed quotes under {MIN_WORDS} words.")
        return 0
    print(f"QUOTE CHECK (advisory): {len(flags)} quote(s) under {MIN_WORDS} words — re-extract with context:")
    for f in sorted(flags, key=lambda x: x["words"]):
        print(f"  {f['words']:2}w  {f['evidence_id']}: {f['quote'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
