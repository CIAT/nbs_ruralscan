#!/usr/bin/env python3
"""Apply hazard-severity tags (ruleset v1.6.3) to EV context.

    python3 scripts/apply-severity-tags.py pipeline/staging/severity/tags.json [--dry-run]

Input: `{evidence_id: {"hazard_severity": value, "severity_cue": cue | null}}`.
Writes `context.hazard_severity` (+ `context.severity_cue` when not unspecified) onto the
matching EV rows. Refuses a tag whose cue is not a verbatim substring of the row's quote /
context.note / relationship.outcome_raw, a tag on a row with no `hazard_type`, or a value
outside the enum — the row is skipped and reported. Only the context column changes
(quote, page, relationship untouched); regenerate JSON afterwards.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools.check_context import SEVERITY  # noqa: E402

EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tags")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    tags = json.loads(Path(a.tags).read_text(encoding="utf-8"))
    with EV.open(newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        cols = list(rdr.fieldnames or [])
        rows = list(rdr)
    applied = skipped = 0
    problems: list[str] = []
    seen: set[str] = set()
    for r in rows:
        t = tags.get(r["evidence_id"])
        if not t:
            continue
        seen.add(r["evidence_id"])
        ctx = json.loads(r["context"] or "{}")
        sev = t.get("hazard_severity")
        cue = t.get("severity_cue")
        rel = json.loads(r["relationship"] or "{}")
        hay = " ".join(
            str(x or "")
            for x in (r.get("quote"), ctx.get("note"), rel.get("outcome_raw"))
        )
        if sev not in SEVERITY:
            problems.append(f"{r['evidence_id']}: bad value {sev!r}")
        elif not ctx.get("hazard_type"):
            problems.append(f"{r['evidence_id']}: no hazard_type")
        elif sev != "unspecified" and (not cue or cue not in hay):
            problems.append(f"{r['evidence_id']}: cue not verbatim {cue!r}")
        else:
            ctx["hazard_severity"] = sev
            if sev == "unspecified":
                ctx.pop("severity_cue", None)
            else:
                ctx["severity_cue"] = cue
            r["context"] = json.dumps(ctx, ensure_ascii=False)
            applied += 1
            continue
        skipped += 1
    missing = set(tags) - seen
    for p in problems:
        print("SKIP", p)
    if missing:
        print(f"{len(missing)} tag(s) with no matching EV row: {sorted(missing)[:5]} …")
    print(f"applied {applied}, skipped {skipped}, {len(rows)} rows read")
    if a.dry_run:
        return 0
    with EV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {EV.relative_to(ROOT)}; now run generate.py schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
