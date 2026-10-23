#!/usr/bin/env python3
"""Apply verified field corrections to EV units, each logged to review_log.

    python3 scripts/apply-unit-corrections.py <corrections.json> --reviewer ai_<pass> [--dry-run]

Input: `[{evidence_id, change: {...}, why}]`. Allowed keys in `change`:
`claim_basis`, `lineage_of`, `relationship.<key>`, `context.<key>` (an empty string
removes the key) and `context.note_append` (appended to `context.note`). Quote, page,
variable and claim text are never touched; anything else in `change` is refused. Drops are
NOT applied here — they are review decisions and go through `apply-review-export.py`.
The reviewer name must start with `ai_` for machine passes (the T4 follow-up tracker
exempts those).
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"
LOG = ROOT / "pipeline" / "metrics" / "review_log.csv"
TOP = {"claim_basis", "lineage_of"}
CLAIM_BASES = {
    "primary_measured",
    "table",
    "figure_read",
    "modelled",
    "expert_assertion",
    "cited_secondary",
}


def apply_change(r: dict, change: dict) -> list[str]:
    """Mutate one EV row; return refusals."""
    bad: list[str] = []
    rel = json.loads(r.get("relationship") or "{}")
    ctx = json.loads(r.get("context") or "{}")
    for k, v in change.items():
        if k in TOP:
            if k == "claim_basis" and v not in CLAIM_BASES:
                bad.append(f"claim_basis {v!r} not in enum")
                continue
            r[k] = v
        elif k == "context.note_append":
            prev = str(ctx.get("note") or "")
            if v not in prev:
                ctx["note"] = (prev + " | " if prev else "") + v
        elif k.startswith("context."):
            kk = k.split(".", 1)[1]
            if v in ("", None):
                ctx.pop(kk, None)
            else:
                ctx[kk] = v
        elif k.startswith("relationship."):
            rel[k.split(".", 1)[1]] = v
        else:
            bad.append(f"field {k!r} not allowed")
    r["relationship"] = json.dumps(rel, ensure_ascii=False)
    r["context"] = json.dumps(ctx, ensure_ascii=False)
    return bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("corrections")
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if not a.reviewer.startswith("ai_"):
        ap.error("machine-pass reviewer names start with ai_")
    items = {
        c["evidence_id"]: c
        for c in json.loads(Path(a.corrections).read_text(encoding="utf-8"))
    }
    with EV.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        cols = list(rd.fieldnames or [])
        rows = list(rd)
    today = date.today().isoformat()
    log, seen = [], set()
    for r in rows:
        c = items.get(r["evidence_id"])
        if not c:
            continue
        seen.add(r["evidence_id"])
        bad = apply_change(r, c["change"])
        for b in bad:
            print("REFUSED", r["evidence_id"], b)
        log.append(
            {
                "date": today,
                "evidence_id": r["evidence_id"],
                "source_id": r["source_id"],
                "verdict": "unit_correction",
                "decision": "ok",
                "reason": "accepted_correction",
                "note": f"{', '.join(sorted(c['change']))}: {c.get('why', '')}",
                "reviewer": a.reviewer,
            }
        )
    missing = sorted(set(items) - seen)
    print(f"corrected {len(log)} unit(s); missing {missing}")
    if a.dry_run:
        return 0
    with EV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with LOG.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(log[0]), lineterminator="\n")
        w.writerows(log)
    print("now: python3 src/nbs_ruralscan/schema_tools/generate.py schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
