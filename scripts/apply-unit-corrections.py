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
import sys
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nbs_ruralscan.schema_tools.record_publication import edit_records  # noqa: E402
from nbs_ruralscan.schema_tools.review_inputs import ReviewInputs  # noqa: E402
from nbs_ruralscan.schema_tools.specialist_records import (  # noqa: E402
    REVIEW_COLUMNS,
    append_history,
    evidence,
    json_field,
    keyed_records,
    read_table,
    rebuild_command,
    write_table,
)

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
    rel = json_field(r, "relationship")
    ctx = json_field(r, "context")
    for k, v in change.items():
        if not k or k.endswith("."):
            bad.append(f"empty field name in {k!r}")
            continue
        if k in TOP:
            if k == "lineage_of" and v is None:
                v = ""
            if not isinstance(v, str):
                bad.append(f"expected text in {k}")
                continue
            if k == "claim_basis" and v not in CLAIM_BASES:
                bad.append(f"claim_basis {v!r} not in enum")
                continue
            r[k] = v
        elif k == "context.note_append":
            if not isinstance(v, str):
                bad.append("context.note_append must be text")
                continue
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


def correct(ev: Path, log_path: Path, corrections: Path, reviewer: str) -> None:
    items = keyed_records(corrections, array=True)
    for eid, item in items.items():
        if item.get("why") is not None and not isinstance(item["why"], str):
            raise ValueError(f"Expected a text justification for {eid}")
        if not isinstance(item.get("change"), dict) or not item["change"]:
            raise ValueError(f"Expected nonempty change object for {eid}")
    cols, rows = evidence(ev, "relationship", "context", "claim_basis", "lineage_of")
    history_cols, history = read_table(log_path, REVIEW_COLUMNS)
    today = date.today().isoformat()
    log, seen = [], set()
    changed = False
    prior = {tuple(row[k] for k in REVIEW_COLUMNS if k != "date") for row in history}

    for r in rows:
        c = items.get(r["evidence_id"])
        if not c:
            continue
        seen.add(r["evidence_id"])
        previous = r.copy()
        bad = apply_change(r, c["change"])
        if bad:
            raise ValueError(f"REFUSED {r['evidence_id']}: {', '.join(bad)}")
        entry = {
            "date": today,
            "evidence_id": r["evidence_id"],
            "source_id": r["source_id"],
            "verdict": "unit_correction",
            "decision": "ok",
            "reason": "accepted_correction",
            "note": f"{', '.join(sorted(c['change']))}: {c.get('why', '')}",
            "reviewer": reviewer,
        }
        updated = r != previous
        changed |= updated
        if (
            updated
            or tuple(entry[k] for k in REVIEW_COLUMNS if k != "date") not in prior
        ):
            log.append(entry)
    missing = sorted(set(items) - seen)
    print(f"corrected {len(log)} unit(s); missing {missing}")
    if changed:
        write_table(ev, cols, rows)
    append_history(log_path, history_cols, log)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument(
        "corrections", type=Path, help="JSON input file; use a path without symlinks"
    )
    ap.add_argument("--root", type=Path, default=ROOT, help="Selected data root")
    ap.add_argument("--reviewer", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    if not a.reviewer.startswith("ai_"):
        ap.error("machine-pass reviewer names start with ai_")
    root = a.root.resolve()
    ev, log = (root / path.relative_to(ROOT) for path in (EV, LOG))
    edit_records(
        [ev, log],
        lambda files: correct(files[ev], files[log], a.corrections, a.reviewer),
        inputs=ReviewInputs([a.corrections]),
        dry_run=a.dry_run,
    )
    if not a.dry_run:
        print(f"now: {rebuild_command(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
