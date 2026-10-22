#!/usr/bin/env python3
"""Log a ROW-review export (generated T3/T6 rows) to pipeline/metrics/row_review_log.csv.

    python3 scripts/apply-row-review-export.py <export.csv> [--log path] [--dry-run]

CSV columns (as review.html exports a "rows" batch): batch, record_id, nbs_id, table,
decision (approve|hold|reject), reason, note, reviewer, date. Rows are GENERATED, so a
decision is a review record, not an edit: nothing in the registers or recipes changes.
Each decision is appended to the log; holds and rejects are the orchestrator's to-do list
(fix the evidence, routing or prose, then regenerate). Re-applying the same export does not
duplicate lines (dedup on record_id + reviewer + date + decision).
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "pipeline" / "metrics" / "row_review_log.csv"
LOG_COLS = [
    "date",
    "record_id",
    "nbs_id",
    "table",
    "decision",
    "reason",
    "note",
    "reviewer",
]
DECISIONS = {"approve", "hold", "reject"}
ROW_REASONS = {
    "wrong_class",
    "wrong_confidence",
    "prose_misleading",
    "evidence_misrouted",
    "should_be_split",
    "other",
}


def _key(r: dict) -> tuple:
    return (
        r.get("record_id", ""),
        r.get("reviewer", ""),
        r.get("date", ""),
        r.get("decision", ""),
    )


def apply_export(export: Path, log: Path = LOG, dry_run: bool = False) -> dict:
    with export.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    existing: set[tuple] = set()
    if log.exists():
        with log.open(newline="", encoding="utf-8") as f:
            existing = {_key(r) for r in csv.DictReader(f)}
    good, bad = [], []
    for r in rows:
        rec = {k: (r.get(k) or "").strip() for k in LOG_COLS}
        rec["decision"] = rec["decision"].lower()
        if not rec["record_id"]:
            bad.append(("?", "no record_id"))
            continue
        if rec["decision"] not in DECISIONS:
            bad.append((rec["record_id"], f"unknown decision {rec['decision']!r}"))
            continue
        if rec["decision"] == "reject" and rec["reason"] not in ROW_REASONS:
            bad.append(
                (
                    rec["record_id"],
                    f"reject needs a row reason code, got {rec['reason']!r}",
                )
            )
            continue
        if rec["decision"] != "reject":
            rec["reason"] = ""
        rec["reviewer"] = rec["reviewer"] or "reviewer"
        if _key(rec) in existing:
            continue
        existing.add(_key(rec))
        good.append(rec)
    if good and not dry_run:
        log.parent.mkdir(parents=True, exist_ok=True)
        new = not log.exists()
        with log.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=LOG_COLS)
            if new:
                w.writeheader()
            w.writerows(good)
    return {
        "read": len(rows),
        "appended": 0 if dry_run else len(good),
        "would_append": len(good),
        "skipped": bad,
        "decisions": Counter(r["decision"] for r in good),
        "todo": [r for r in good if r["decision"] in ("hold", "reject")],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("csv")
    ap.add_argument("--log", default=str(LOG))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    out = apply_export(Path(a.csv), Path(a.log), a.dry_run)
    print(
        f"{out['read']} row(s) read; {'would append' if a.dry_run else 'appended'} "
        f"{out['would_append']}; decisions: {dict(out['decisions'])}"
    )
    for rid, why in out["skipped"]:
        print("  SKIP", rid, why)
    for r in out["todo"]:
        print(
            f"  TODO {r['decision']:6} {r['record_id']} {r['reason']} {r['note']}".rstrip()
        )
    return 1 if out["skipped"] and not out["would_append"] else 0


if __name__ == "__main__":
    sys.exit(main())
