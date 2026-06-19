"""Progress ledger — orchestrator-owned, register-enforced, per (NbS × table × category).

Tracks, for each (nbs_id × table[T4/T3/T6] × source-category[stock/updated_lit/grey/tool]),
the AUTHORED process stages: searched · screened · verified. These cannot be derived from
data (a search either happened or didn't), so the pipeline STEP that runs them stamps the
ledger via `mark()`. Extraction (E) and review (R) ARE facts, derived live from the
register per (family × table × category) — they are not stored here.

`check()` reconciles ledger claims against the register and is wired into generate.py + CI:
it FAILS the build on an invalid status, or `verified=done` for a cell with zero evidence
(you can't have verified nothing). It also reports (non-fatal) cells that hold evidence
from a category whose search isn't `done` — i.e. ad-hoc / incomplete search coverage.

Status values: not_started · in_progress · done.

CLI:
  uv run python3 -m nbs_ruralscan.schema_tools.ledger show
  uv run python3 -m nbs_ruralscan.schema_tools.ledger check
  uv run python3 -m nbs_ruralscan.schema_tools.ledger mark --nbs agroforestry --table T4 \
      --category stock --stage searched --status done --run-id stocktake_2026-06
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "pipeline" / "progress_ledger.csv"

STAGES = ["searched", "screened", "verified"]  # authored (cannot be derived)
TABLES = ["T4", "T3", "T6"]
CATEGORIES = ["stock", "updated_lit", "grey", "tool"]
_ROLE = {"T4": "structural_suitability", "T3": "climate_risk", "T6": "nbs_effect"}
_ROLE_INV = {v: k for k, v in _ROLE.items()}
STATUSES = {"not_started", "in_progress", "done"}
FIELDS = (
    ["nbs_id", "table", "category"] + STAGES + ["last_run_id", "updated", "by", "note"]
)


def _rows() -> list[dict]:
    if not LEDGER.exists():
        return []
    with LEDGER.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write(rows: list[dict]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def _category_map(schema_root: Path) -> dict[str, str]:
    """source_id -> source_category (stock/updated_lit/grey/tool), explicit from SRC."""
    src = Path(schema_root) / "registers" / "SRC_source_register.csv"
    out: dict[str, str] = {}
    if src.exists():
        with src.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                out[r["source_id"]] = r.get("source_category", "") or "stock"
    return out


def derive_facts(schema_root: str | Path) -> dict[tuple, dict]:
    """Per (nbs_id, table, category): ev count + reviewed count, from the register.

    (Family is folded out here — the gate works at NbS×table×category; the dashboard
    derives the per-family cell facts itself.)
    """
    schema_root = Path(schema_root)
    cat = _category_map(schema_root)
    ev_csv = schema_root / "registers" / "EV_evidence_register.csv"
    facts: dict[tuple, dict] = {}
    if not ev_csv.exists():
        return facts
    with ev_csv.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("review_state") or "") == "dropped":
                continue  # soft-deleted — not active evidence
            tbl = _ROLE_INV.get(r.get("use_role", ""))
            if not tbl:
                continue
            key = (r.get("nbs_id", ""), tbl, cat.get(r.get("source_id", ""), "stock"))
            d = facts.setdefault(key, {"ev": 0, "reviewed": 0})
            d["ev"] += 1
            if r.get("reviewer_ok") in (True, "true", "True"):
                d["reviewed"] += 1
    return facts


def check(schema_root: str | Path) -> list[str]:
    """Hard reconciliation (build-failing). Returns list of violations (empty = OK)."""
    facts = derive_facts(schema_root)
    rows = {(r["nbs_id"], r["table"], r["category"]): r for r in _rows()}
    errs: list[str] = []
    for (nbs, tbl, c), r in rows.items():
        if tbl not in TABLES:
            errs.append(f"[{nbs}·{tbl}·{c}] invalid table '{tbl}'")
        if c not in CATEGORIES:
            errs.append(f"[{nbs}·{tbl}·{c}] invalid category '{c}'")
        for s in STAGES:
            if (r.get(s) or "not_started") not in STATUSES:
                errs.append(f"[{nbs}·{tbl}·{c}] stage '{s}'='{r.get(s)}' invalid")
        if (r.get("verified") or "not_started") == "done":
            if facts.get((nbs, tbl, c), {}).get("ev", 0) == 0:
                errs.append(
                    f"[{nbs}·{tbl}·{c}] verified=done but 0 evidence units — nothing to verify"
                )
    return errs


def coverage_warnings(schema_root: str | Path) -> list[str]:
    """Non-fatal: cells holding evidence from a category whose search isn't 'done'."""
    facts = derive_facts(schema_root)
    rows = {(r["nbs_id"], r["table"], r["category"]): r for r in _rows()}
    out = []
    for key, fct in facts.items():
        if fct["ev"] > 0:
            r = rows.get(key)
            if not r or (r.get("searched") or "not_started") != "done":
                out.append(
                    f"[{key[0]}·{key[1]}·{key[2]}] {fct['ev']} evidence units but search "
                    f"!= done — ad-hoc/incomplete search coverage"
                )
    return out


def mark(
    nbs: str,
    table: str,
    category: str,
    stage: str,
    status: str,
    *,
    run_id: str = "",
    by: str = "orchestrator",
    note: str = "",
) -> None:
    if table not in TABLES:
        raise ValueError(f"table must be one of {TABLES}")
    if category not in CATEGORIES:
        raise ValueError(f"category must be one of {CATEGORIES}")
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}")
    if status not in STATUSES:
        raise ValueError(f"status must be one of {sorted(STATUSES)}")
    rows = _rows()
    row = next(
        (
            r
            for r in rows
            if r["nbs_id"] == nbs and r["table"] == table and r["category"] == category
        ),
        None,
    )
    if row is None:
        row = {k: "" for k in FIELDS}
        row.update(
            nbs_id=nbs,
            table=table,
            category=category,
            **{s: "not_started" for s in STAGES},
        )
        rows.append(row)
    row[stage] = status
    row["last_run_id"] = run_id or row.get("last_run_id", "")
    row["by"] = by
    row["updated"] = datetime.now(timezone.utc).date().isoformat()
    if note:
        row["note"] = note
    _write(rows)


def _show() -> None:
    rows = _rows()
    if not rows:
        print("progress ledger is empty.")
        return
    tick = {"done": "✓", "in_progress": "~", "not_started": "·"}
    print(f"{'nbs·table·category':40}  " + " ".join(f"{s[:4]}" for s in STAGES))
    for r in sorted(rows, key=lambda x: (x["nbs_id"], x["table"], x["category"])):
        key = f"{r['nbs_id']}·{r['table']}·{r['category']}"
        print(
            f"{key:40}  "
            + "    ".join(tick.get(r.get(s) or "not_started", "?") for s in STAGES)
        )


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    pc = sub.add_parser("check")
    pc.add_argument("schema_root", nargs="?", default="schema")
    pm = sub.add_parser("mark")
    pm.add_argument("--nbs", required=True)
    pm.add_argument("--table", required=True)
    pm.add_argument("--category", required=True)
    pm.add_argument("--stage", required=True)
    pm.add_argument("--status", required=True)
    pm.add_argument("--run-id", default="")
    pm.add_argument("--by", default="orchestrator")
    pm.add_argument("--note", default="")
    args = ap.parse_args(argv)

    if args.cmd == "show":
        _show()
        return 0
    if args.cmd == "mark":
        mark(
            args.nbs,
            args.table,
            args.category,
            args.stage,
            args.status,
            run_id=args.run_id,
            by=args.by,
            note=args.note,
        )
        print(
            f"marked {args.nbs}·{args.table}·{args.category} {args.stage}={args.status}"
        )
        return 0
    errs = check(args.schema_root)
    warns = coverage_warnings(args.schema_root)
    if errs:
        print(f"LEDGER CHECK FAILED: {len(errs)} violation(s):", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("LEDGER OK: claims reconcile with the register.")
    if warns:
        print(
            f"  ({len(warns)} coverage note(s) — evidence in not-fully-searched categories):"
        )
        for w in warns:
            print(f"    · {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
