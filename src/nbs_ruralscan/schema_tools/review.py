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
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
WORKLIST = ROOT / "pipeline" / "review" / "flag_worklist.csv"
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
        w = csv.DictWriter(f, fieldnames=_WL_FIELDS)
        w.writeheader()
        w.writerows(out)
    print(f"exported {len(out)} flagged units → {WORKLIST.relative_to(ROOT)}")
    print(
        "Fill the 'decision' column (ok | drop) + reviewer, then run: review.py apply"
    )
    return WORKLIST


def apply_decisions(decisions: dict, reviewer: str = "reviewer") -> dict:
    """Apply {evidence_id: 'ok'|'drop'} to the EV register. Returns a summary dict."""
    today = datetime.now(timezone.utc).date().isoformat()
    with EV.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        cols = rd.fieldnames
        rows = list(rd)
    kept, dropped, resolved = [], 0, 0
    for r in rows:
        d = (decisions.get(r["evidence_id"]) or "").strip().lower()
        if d == "drop":
            dropped += 1
            continue
        if d == "ok":
            r["reviewer_ok"] = "true"
            r["attribution"] = _FLAG_RE.sub("", r.get("attribution", "")).strip()
            r["attribution"] = (f"[reviewed {today} by {reviewer}] " + (r["attribution"] or "")).strip()
            resolved += 1
        kept.append(r)
    with EV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(kept)
    return {"ok": resolved, "dropped": dropped, "rows": len(kept)}


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
    reviewer = next((d.get("reviewer") for d in decisions.values() if d.get("reviewer")), "reviewer")
    res = apply_decisions({eid: d["decision"] for eid, d in decisions.items()}, reviewer)
    print(f"applied: {res['ok']} marked reviewed-ok (flag cleared), {res['dropped']} dropped. EV now {res['rows']} rows.")
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
