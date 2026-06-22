"""Learnings cursor — prove that review-log feedback has actually been incorporated.

The iterative-learning loop is only honest if every human review decision gets READ and
turned into a pipeline adjustment (a defect-catalogue rule + a deterministic check). This
module makes that provable instead of claimed:

* `review_log.csv` grows as humans review (the FEEDBACK).
* `learnings_log.csv` records each retrospective: how many review rows were processed
  (`reviewed_through`), the dominant reason then, the off-scope rate, and the concrete
  adjustment made (rule/check + commit).
* `status()` compares the two. If review decisions outpace the last retrospective, there
  are UNINCORPORATED learnings — surfaced as a build note (like the ledger's coverage
  warnings) so unread feedback can't sit silently.

CLI:
  uv run python3 -m nbs_ruralscan.schema_tools.learnings status
  uv run python3 -m nbs_ruralscan.schema_tools.learnings record \
      --adjustment "check_scope.py + section-scope rule" --commit <sha> --note "..."
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REVIEW_LOG = ROOT / "pipeline" / "metrics" / "review_log.csv"
LEARNINGS_LOG = ROOT / "pipeline" / "metrics" / "learnings_log.csv"
FIELDS = [
    "date",
    "reviewed_through",  # review_log row count incorporated by this retrospective
    "dominant_reason",
    "off_scope_rate_pct",
    "adjustment",
    "commit",
    "note",
]


def _review_rows() -> list[dict]:
    # De-dup to distinct reviews (latest per evidence_id × reviewer). The raw log APPENDS
    # on every apply run, so raw counts over-state reviews ~3x (220 raw → 68 distinct, 2026-06-22).
    from nbs_ruralscan.schema_tools.review import latest_review_rows

    if not REVIEW_LOG.exists():
        return []
    with REVIEW_LOG.open(encoding="utf-8") as f:
        return latest_review_rows(list(csv.DictReader(f)))


def _learnings_rows() -> list[dict]:
    if not LEARNINGS_LOG.exists():
        return []
    with LEARNINGS_LOG.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def status() -> dict:
    rl = _review_rows()
    ll = _learnings_rows()
    reviewed_through = max((int(r.get("reviewed_through") or 0) for r in ll), default=0)
    reasons = Counter(r.get("reason") or "unspecified" for r in rl)
    drops = sum(1 for r in rl if (r.get("decision") or "").lower() == "drop")
    queried = sum(1 for r in rl if (r.get("decision") or "").lower() in ("flag", "query"))
    oks = sum(1 for r in rl if (r.get("decision") or "").lower() == "ok")
    off = reasons.get("off_scope", 0)
    return {
        "distinct_reviews": len(rl),  # distinct (evidence × reviewer), de-duped
        "decisions": {"ok": oks, "drop": drops, "query": queried},
        "reviewed_through": reviewed_through,
        "unprocessed": max(0, len(rl) - reviewed_through),
        "dominant_reason": (reasons.most_common(1)[0][0] if reasons else ""),
        "off_scope_rate_pct_of_drops": (round(100 * off / drops, 1) if drops else None),
    }


def coverage_note() -> str | None:
    s = status()
    if s["unprocessed"] > 0:
        return (
            f"{s['unprocessed']} review decision(s) not yet incorporated into the learning "
            f"loop (dominant reason: {s['dominant_reason']}). Run /sweep-retro → encode the "
            f"defect → learnings.record."
        )
    return None


def record(adjustment: str, commit: str = "", note: str = "") -> dict:
    s = status()
    LEARNINGS_LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LEARNINGS_LOG.exists()
    row = {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "reviewed_through": s["distinct_reviews"],
        "dominant_reason": s["dominant_reason"],
        "off_scope_rate_pct": s["off_scope_rate_pct_of_drops"],
        "adjustment": adjustment,
        "commit": commit,
        "note": note,
    }
    with LEARNINGS_LOG.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)
    return row


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    import sys

    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    pr = sub.add_parser("record")
    pr.add_argument("--adjustment", required=True)
    pr.add_argument("--commit", default="")
    pr.add_argument("--note", default="")
    args = ap.parse_args(argv if argv is not None else sys.argv[1:])

    if args.cmd == "status":
        json.dump(status(), sys.stdout, indent=2)
        print()
    else:
        row = record(args.adjustment, args.commit, args.note)
        print(
            f"recorded learning: reviewed_through={row['reviewed_through']} · {row['adjustment']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
