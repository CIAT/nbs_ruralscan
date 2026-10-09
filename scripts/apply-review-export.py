#!/usr/bin/env python3
"""Apply a review-page export (CSV) to the register through the existing review loop.

    python3 scripts/apply-review-export.py <export.csv> [--dry-run]

CSV columns (as the page exports them): batch, evidence_id, decision (approve|hold|reject),
reason, note, reviewer, date, picos_flags (letters of the PICOS elements the reviewer
flagged; appended to the note as "[PICOS fails: I,C]"). approve → ok · reject → drop (reason code required) ·
hold → flag (stays open, note logged). Goes through `schema_tools.review.apply_decisions`,
so the register, review_log and soft-delete rules are the same as the dashboard's.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools.review import REASON_CODES, apply_decisions  # noqa: E402

MAP = {"approve": "ok", "reject": "drop", "hold": "flag"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("csv")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8")))
    by_reviewer: dict[str, dict] = {}
    bad = []
    for r in rows:
        d = MAP.get((r.get("decision") or "").strip().lower())
        reason = (r.get("reason") or "").strip()
        pic = [x.strip() for x in (r.get("picos_flags") or "").split(";") if x.strip()]
        if not d:
            bad.append(
                (
                    r.get("evidence_id"),
                    "PICOS flags but no decision — re-export after approving / holding / rejecting"
                    if pic
                    else "unknown decision",
                )
            )
            continue
        if d == "drop" and reason not in REASON_CODES:
            bad.append(
                (r.get("evidence_id"), f"reject needs a reason code, got {reason!r}")
            )
            continue
        rev = (r.get("reviewer") or "reviewer").strip() or "reviewer"
        # PICOS element flags ride in the note: review_log has a fixed column set, and a
        # flag is a judgement about the evidence, not a new decision type.
        note = (r.get("note") or "").strip()
        if pic:
            note = (note + " " if note else "") + "[PICOS fails: " + ",".join(pic) + "]"
        by_reviewer.setdefault(rev, {})[r["evidence_id"]] = {
            "decision": d,
            "reason": reason or ("confirmed_pass" if d == "ok" else ""),
            "note": note,
            "reviewer": rev,
        }
    print(
        f"{len(rows)} row(s); decisions: {Counter(MAP.get((r.get('decision') or '').lower(), '?') for r in rows)}; reviewers: {list(by_reviewer)}"
    )
    for eid, why in bad:
        print("  SKIP", eid, why)
    if a.dry_run:
        return 0
    for rev, dec in by_reviewer.items():
        out = apply_decisions(dec, reviewer=rev)
        print(f"  applied for {rev}: {out}")
    print("now: python3 src/nbs_ruralscan/schema_tools/generate.py schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
