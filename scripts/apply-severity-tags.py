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
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools.check_context import SEVERITY  # noqa: E402

from nbs_ruralscan.schema_tools.record_publication import edit_records  # noqa: E402
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs  # noqa: E402
from nbs_ruralscan.schema_tools.specialist_records import (  # noqa: E402
    evidence,
    json_field,
    keyed_records,
    rebuild_command,
    write_table,
)

EV = ROOT / "schema" / "registers" / "EV_evidence_register.csv"


def annotate(ev: Path, tags_path: Path) -> None:
    tags = keyed_records(tags_path, array=False)
    for eid, tag in tags.items():
        if (
            not isinstance(tag.get("hazard_severity"), str)
            or tag.get("severity_cue") is not None
            and not isinstance(tag["severity_cue"], str)
        ):
            raise ValueError(f"Malformed severity annotation for {eid}")
    cols, rows = evidence(ev, "context", "relationship", "quote")
    applied = skipped = 0
    problems: list[str] = []
    seen: set[str] = set()
    for r in rows:
        t = tags.get(r["evidence_id"])
        if not t:
            continue
        seen.add(r["evidence_id"])
        ctx = json_field(r, "context")
        sev = t.get("hazard_severity")
        cue = t.get("severity_cue")
        rel = json_field(r, "relationship")
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
    if applied:
        write_table(ev, cols, rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument(
        "tags", type=Path, help="JSON input file; use a path without symlinks"
    )
    ap.add_argument("--root", type=Path, default=ROOT, help="Selected data root")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    root = a.root.resolve()
    ev = root / EV.relative_to(ROOT)
    edit_records(
        [ev],
        lambda files: annotate(files[ev], a.tags),
        inputs=ReviewInputs([a.tags]),
        dry_run=a.dry_run,
    )
    if not a.dry_run:
        print(f"wrote {ev}; now: {rebuild_command(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
