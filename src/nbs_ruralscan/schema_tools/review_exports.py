"""Committed review-page exports → the shared decision view.

The evidence-review page (`docs/review.html`) keeps a reviewer's decisions in their own
browser until they press Export. Dropping that CSV into `docs/review/exports/` makes it
shared: this module reads every export, reduces them to the latest decision per
(evidence_id × reviewer), and writes `docs/review/decisions.json` so that

* the review page can show what the OTHER reviewer already decided (second opinion), and
* `table_progress` can report QA progress per NbS on the build-progress page.

Applying those decisions to the register is a separate, deliberate step
(`scripts/apply-review-export.py`); this module never touches evidence.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
EXPORTS = ROOT / "docs" / "review" / "exports"
BATCH_DIR = ROOT / "docs" / "review"
DEST = BATCH_DIR / "decisions.json"
DECISIONS = ("approve", "hold", "reject")


def collect(exports_dir: Path | None = None) -> dict[str, dict[str, dict[str, Any]]]:
    """`{batch: {evidence_id: {reviewer: {decision, reason, note, date, picos_flags}}}}`.

    Latest date wins per (evidence_id × reviewer); malformed rows are skipped silently —
    an export is a hand-moved file, not a gate.
    """
    out: dict[str, dict[str, dict[str, Any]]] = {}
    d = exports_dir or EXPORTS
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.csv")):
        try:
            rows = list(csv.DictReader(f.open(encoding="utf-8-sig")))
        except OSError:
            continue
        for r in rows:
            eid = (r.get("evidence_id") or "").strip()
            batch = (r.get("batch") or "").strip()
            rev = (r.get("reviewer") or "").strip()
            dec = (r.get("decision") or "").strip().lower()
            if not (eid and batch and rev):
                continue
            if dec and dec not in DECISIONS:
                continue
            rec = {
                "decision": dec,
                "reason": (r.get("reason") or "").strip(),
                "note": (r.get("note") or "").strip(),
                "date": (r.get("date") or "").strip(),
                "picos_flags": [
                    x.strip()
                    for x in (r.get("picos_flags") or "").split(";")
                    if x.strip()
                ],
                "file": f.name,
            }
            prev = out.setdefault(batch, {}).setdefault(eid, {}).get(rev)
            if prev and (prev.get("date") or "") > (rec["date"] or ""):
                continue
            out[batch][eid][rev] = rec
    return out


def _batch_units(batch_dir: Path | None = None) -> dict[str, list[dict[str, str]]]:
    """`{batch: [{evidence_id, nbs_id, use_role}]}` from the committed batch files."""
    d = batch_dir or BATCH_DIR
    out: dict[str, list[dict[str, str]]] = {}
    for f in sorted(d.glob("*.json")):
        if f.name in ("index.json", "decisions.json"):
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        bid = ((data.get("batch") or {}).get("id")) or f.stem
        out[bid] = [
            {
                "evidence_id": u["evidence_id"],
                "nbs_id": u.get("nbs_id", ""),
                "use_role": u.get("use_role", ""),
            }
            for u in data.get("units") or []
        ]
    return out


def summary(
    exports_dir: Path | None = None, batch_dir: Path | None = None
) -> dict[str, Any]:
    """QA progress per batch and per NbS: units in review, how many decided, by whom,
    the decision split, PICOS flags, and units where reviewers disagree."""
    dec = collect(exports_dir)
    units = _batch_units(batch_dir)
    by_batch: dict[str, Any] = {}
    by_nbs: dict[str, dict[str, Any]] = {}
    for bid, us in units.items():
        d = dec.get(bid, {})
        reviewers = sorted({r for v in d.values() for r in v})
        b = {
            "units": len(us),
            "decided": 0,
            "reviewers": reviewers,
            "by_decision": {k: 0 for k in DECISIONS},
            "picos_flagged": 0,
            "disagreements": [],
        }
        for u in us:
            n = by_nbs.setdefault(
                u["nbs_id"],
                {
                    "units": 0,
                    "decided": 0,
                    "by_decision": {k: 0 for k in DECISIONS},
                    "picos_flagged": 0,
                    "batches": [],
                },
            )
            n["units"] += 1
            if bid not in n["batches"]:
                n["batches"].append(bid)
            calls = d.get(u["evidence_id"]) or {}
            made = {r: v["decision"] for r, v in calls.items() if v.get("decision")}
            if made:
                b["decided"] += 1
                n["decided"] += 1
                for v in made.values():
                    b["by_decision"][v] = b["by_decision"].get(v, 0) + 1
                    n["by_decision"][v] = n["by_decision"].get(v, 0) + 1
                if len(set(made.values())) > 1:
                    b["disagreements"].append(
                        {"evidence_id": u["evidence_id"], "calls": made}
                    )
            if any(v.get("picos_flags") for v in calls.values()):
                b["picos_flagged"] += 1
                n["picos_flagged"] += 1
        by_batch[bid] = b
    return {"batches": by_batch, "nbs": by_nbs}


def write_decisions(check: bool = False, dest: Path | None = None) -> list[Path]:
    """(Re)write `docs/review/decisions.json`; `[]` when the content is unchanged."""
    dest = Path(dest) if dest else DEST
    payload = {"decisions": collect(), "summary": summary()}
    try:
        current = json.loads(dest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        current = None
    if (
        isinstance(current, dict)
        and current.get("decisions") == payload["decisions"]
        and current.get("summary") == payload["summary"]
    ):
        return []
    out = {"built": datetime.now(timezone.utc).isoformat(), **payload}
    if not check:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            json.dumps(out, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return [dest]
