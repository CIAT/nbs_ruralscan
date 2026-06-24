"""VERIFY-FLAG review loop — turn the read-only worklist into logged decisions.

A static dashboard can't write the register, so human review happens here:

  1. export → pipeline/review/flag_worklist.csv  (one row per flagged EV unit, with the
     full quote, the parsed verdict + reason, and EMPTY decision/reviewer/note columns).
  2. A human fills `decision` for each row in a spreadsheet:
       ok    = evidence stands (auto-correction accepted, or flag was a false positive)
               → sets reviewer_ok=true and clears the [VERIFY-FLAG ...] marker
       drop  = remove the unit from the register
       (leave blank = undecided; left flagged)
  3. apply → reads the filled CSV, mutates EV_evidence_register.csv accordingly, then you
     regenerate + can mark the ledger `reviewed` stage done for fully-reviewed tables.

Verdict meanings (from the adversarial relationship-verify):
  mismatch    = a number/label in the relationship contradicted/misread the quote (it was
                auto-corrected to the quote-faithful subset).
  unsupported = the relationship asserted a number the quote did not contain (it was
                stripped). Reviewer confirms the strip/correction or drops the unit.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
WORKLIST = ROOT / "pipeline" / "review" / "flag_worklist.csv"
LOG = ROOT / "pipeline" / "metrics" / "review_log.csv"
REASON_CODES = [
    "smuggled_number",
    "cross_row_stitch",
    "wrong_variable",
    "wrong_practice",
    "species_envelope",
    "table_garble",
    "off_scope",
    "quote_too_narrow",
    "relationship_missed",
    "insufficient_context",
    "uninterpretable_weight",
    "speculative_evidence",
    "wrong_table",
    "constrained_aoi",
    "false_flag",
    "accepted_correction",
    "confirmed_pass",
    "missed_error",
    "other",
]
_FLAG_RE = re.compile(r"\[VERIFY-FLAG\s+(\w+):\s*(.*?)\]\s*", re.S)
_WL_FIELDS = [
    "evidence_id",
    "source_id",
    "variable",
    "use_role",
    "verdict",
    "flag_reason",
    "quote",
    "relationship",
    "decision",
    "reviewer",
    "note",
]


def _flag(attr: str) -> tuple[str, str] | None:
    m = _FLAG_RE.search(attr or "")
    return (m.group(1), m.group(2).strip()) if m else None


def export() -> Path:
    """Write a review worklist of every currently-flagged EV unit."""
    with EV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        fl = _flag(r.get("attribution", ""))
        if not fl:
            continue
        out.append(
            {
                "evidence_id": r["evidence_id"],
                "source_id": r["source_id"],
                "variable": r["variable"],
                "use_role": r["use_role"],
                "verdict": fl[0],
                "flag_reason": fl[1],
                "quote": r.get("quote", ""),
                "relationship": r.get("relationship", ""),
                "decision": "",
                "reviewer": "",
                "note": "",
            }
        )
    WORKLIST.parent.mkdir(parents=True, exist_ok=True)
    with WORKLIST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=_WL_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    print(f"exported {len(out)} flagged units → {WORKLIST.relative_to(ROOT)}")
    print(
        "Fill the 'decision' column (ok | drop) + reviewer, then run: review.py apply"
    )
    return WORKLIST


def _verdict_of(attr: str) -> str:
    m = _FLAG_RE.search(attr or "")
    return m.group(1) if m else ""


def latest_review_rows(rows: list[dict] | None = None) -> list[dict]:
    """De-dup the review log to one row per (evidence_id, reviewer) — the LATEST.

    ``apply_decisions`` APPENDS a row on every run, so the raw log over-counts a
    re-applied decision many times (220 raw rows vs 68 distinct reviews, 2026-06-22).
    Metrics (learnings, qaqc_stats, sweep_metrics) must count distinct reviews, not
    appended rows. File order is chronological, so the last write wins.
    """
    if rows is None:
        rows = []
        if LOG.exists():
            with LOG.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
    latest: dict[tuple[str, str], dict] = {}
    for r in rows:
        latest[(r.get("evidence_id", ""), (r.get("reviewer") or "").strip())] = r
    return list(latest.values())


def apply_decisions(decisions: dict, reviewer: str = "reviewer") -> dict:
    """Apply decisions to EV. Each value is 'ok'|'drop' OR {'decision','reason'}.

    Logs every decision (with reason code) to pipeline/metrics/review_log.csv so the
    sweep retrospective can tally failure patterns and feed them back into the spec/checks.
    """
    today = datetime.now(timezone.utc).date().isoformat()

    def _norm(v):
        if isinstance(v, dict):
            return (
                str(v.get("decision", "")).strip().lower(),
                (v.get("reason") or "").strip(),
                (v.get("note") or "").strip(),
                (v.get("reviewer") or "").strip(),
            )
        return (str(v or "").strip().lower(), "", "", "")

    with EV.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        cols = list(rd.fieldnames or [])
        rows = list(rd)
    kept, dropped, resolved, queried = [], 0, 0, 0
    reasons: Counter = Counter()
    logrows = []
    for r in rows:
        dec, reason, note, rev = _norm(decisions.get(r["evidence_id"]))
        who = rev or reviewer
        if not dec:
            kept.append(r)
            continue
        verdict = _verdict_of(r.get("attribution", ""))
        logrows.append(
            [
                today,
                r["evidence_id"],
                r.get("source_id", ""),
                verdict,
                dec,
                reason,
                note,
                who,
            ]
        )
        reasons[reason or "unspecified"] += 1
        if dec == "drop":
            # soft-delete: keep the row as a record, mark dropped (excluded from
            # synthesis/support/counts; reversible via reopen_units).
            r["review_state"] = "dropped"
            r["attribution"] = _FLAG_RE.sub("", r.get("attribution", "")).strip()
            tag = (
                f"[dropped {today} by {who}"
                + (f"; reason:{reason}" if reason else "")
                + (f"; note:{note}" if note else "")
                + "]"
            )
            r["attribution"] = (tag + " " + (r["attribution"] or "")).strip()
            dropped += 1
            kept.append(r)
            continue
        if dec in ("flag", "query"):
            # tentatively accepted + open question for further review: stays ACTIVE
            # (included, like ok) but reviewer_ok is NOT set — it's unresolved. The verify
            # flag (if any) is kept so the record stays in the queue for resolution; the
            # query + note (the question) are stamped + logged.
            r["review_state"] = ""
            tag = (
                f"[query {today} by {who}"
                + (f"; reason:{reason}" if reason else "")
                + (f"; note:{note}" if note else "")
                + "]"
            )
            r["attribution"] = (tag + " " + (r.get("attribution") or "")).strip()
            queried += 1
            kept.append(r)
            continue
        if dec == "ok":
            r["reviewer_ok"] = "true"
            r["review_state"] = ""  # active (un-drops if it was previously dropped)
            r["attribution"] = _FLAG_RE.sub("", r.get("attribution", "")).strip()
            tag = (
                f"[reviewed {today} by {who}"
                + (f"; reason:{reason}" if reason else "")
                + (f"; note:{note}" if note else "")
                + "]"
            )
            r["attribution"] = (tag + " " + (r["attribution"] or "")).strip()
            resolved += 1
        kept.append(r)
    with EV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(kept)
    if logrows:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        new_file = not LOG.exists()
        with LOG.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(
                    [
                        "date",
                        "evidence_id",
                        "source_id",
                        "verdict",
                        "decision",
                        "reason",
                        "note",
                        "reviewer",
                    ]
                )
            w.writerows(logrows)
    return {
        "ok": resolved,
        "dropped": dropped,
        "queried": queried,
        "rows": len(kept),
        "reasons": dict(reasons),
    }


def reopen_units(evidence_ids: list[str], reviewer: str = "reviewer") -> dict:
    """Revert an ok-reviewed EV row back to flagged (clears reviewer_ok, restores the
    [VERIFY-FLAG verdict: reason] from the review_log) so it re-enters the worklist.

    Only ok-reviewed units (still in EV) can be reopened; dropped units are gone and
    must be re-extracted. Logs a 'reopen' action for audit.
    """
    today = datetime.now(timezone.utc).date().isoformat()
    # latest logged verdict+reason per evidence_id (for restoring the flag text)
    last: dict[str, tuple[str, str]] = {}
    if LOG.exists():
        with LOG.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                last[row["evidence_id"]] = (
                    row.get("verdict", ""),
                    row.get("reason", ""),
                )
    with EV.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        cols = list(rd.fieldnames or [])
        rows = list(rd)
    targets = set(evidence_ids)
    reopened, logrows = 0, []
    for r in rows:
        if r["evidence_id"] not in targets:
            continue
        was_ok = (r.get("reviewer_ok") or "").lower() == "true"
        was_dropped = (r.get("review_state") or "") == "dropped"
        if not (was_ok or was_dropped):
            continue
        verdict, reason = last.get(
            r["evidence_id"], ("mismatch", "re-opened for review")
        )
        r["reviewer_ok"] = "false"
        r["review_state"] = ""  # un-drop / un-keep -> active + flagged again
        # strip any prior [reviewed ...] / [dropped ...] tag, prepend a fresh VERIFY-FLAG
        attr = re.sub(
            r"\[(reviewed|dropped)[^\]]*\]\s*", "", r.get("attribution", "")
        ).strip()
        r["attribution"] = (f"[VERIFY-FLAG {verdict}: {reason}] " + attr).strip()
        reopened += 1
        logrows.append(
            [
                today,
                r["evidence_id"],
                r.get("source_id", ""),
                verdict,
                "reopen",
                "",
                "",
                reviewer,
            ]
        )
    with EV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    if logrows:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        new_file = not LOG.exists()
        with LOG.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(
                    [
                        "date",
                        "evidence_id",
                        "source_id",
                        "verdict",
                        "decision",
                        "reason",
                        "note",
                        "reviewer",
                    ]
                )
            w.writerows(logrows)
    return {"reopened": reopened}


def apply() -> None:
    """Apply decisions from the filled worklist back into the EV register."""
    if not WORKLIST.exists():
        print("no worklist found — run `review.py export` first.")
        return
    with WORKLIST.open(newline="", encoding="utf-8") as f:
        decisions = {
            d["evidence_id"]: d
            for d in csv.DictReader(f)
            if (d.get("decision") or "").strip()
        }
    if not decisions:
        print("no decisions filled in the worklist — nothing to apply.")
        return
    reviewer = (
        next(
            (d.get("reviewer") for d in decisions.values() if d.get("reviewer")),
            "reviewer",
        )
        or "reviewer"
    )
    res = apply_decisions(
        {
            eid: {
                "decision": d["decision"],
                "reason": d.get("reason", ""),
                "note": d.get("note", ""),
            }
            for eid, d in decisions.items()
        },
        reviewer,
    )
    print(
        f"applied: {res['ok']} marked reviewed-ok (flag cleared), {res['dropped']} dropped. EV now {res['rows']} rows."
    )
    print(
        "Next: `generate.py schema` to rebuild + re-gate, then `ledger.py mark ... "
        "--stage reviewed --status done` for fully-reviewed tables."
    )


def main(argv: list[str] | None = None) -> int:
    import sys

    cmd = (argv or sys.argv[1:] or ["export"])[0]
    if cmd == "export":
        export()
    elif cmd == "apply":
        apply()
    else:
        print("usage: review.py [export|apply]", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
