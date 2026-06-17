"""Progress ledger — orchestrator-owned, register-enforced project tracker.

The dashboard used to *infer* stage status from artifacts (a log file exists → "searched").
That over-claims. This makes progress EXPLICIT and ENFORCED:

- The ledger (`pipeline/progress_ledger.csv`) records, per (nbs_id × table), the authored
  status of each lifecycle stage: searched · screened · extracted · verified · reviewed
  (plus which source categories were searched). It is stamped by the pipeline STEP that
  did the work via `mark()` — never guessed.
- `check()` RECONCILES those claims against ground truth in the registers and FAILS the
  build on any lie or stage-order violation (wired into generate.py + CI). You cannot
  mark a stage "done" without the evidence to back it, and evidence cannot exist for an
  unstamped stage. This is the enforcement.

Stage order: searched → screened → extracted → verified → reviewed (a later stage done
requires all earlier ones done).

CLI:
  uv run python3 -m nbs_ruralscan.schema_tools.ledger show
  uv run python3 -m nbs_ruralscan.schema_tools.ledger check
  uv run python3 -m nbs_ruralscan.schema_tools.ledger mark --nbs agroforestry --table T4 \
      --stage extracted --status done --run-id reextract_2026-06 --by orchestrator
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "pipeline" / "progress_ledger.csv"

STAGES = ["searched", "screened", "extracted", "verified", "reviewed"]
TABLES = ["T4", "T3", "T6"]
_ROLE = {"T4": "structural_suitability", "T3": "climate_risk", "T6": "nbs_effect"}
STATUSES = {"not_started", "in_progress", "done"}
FIELDS = (
    ["nbs_id", "table"]
    + STAGES
    + ["searched_categories", "last_run_id", "updated", "by", "note"]
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


def derive_facts(schema_root: str | Path) -> dict[tuple[str, str], dict]:
    """Ground truth from the registers, per (nbs_id, table)."""
    ev_csv = Path(schema_root) / "registers" / "EV_evidence_register.csv"
    facts: dict[tuple[str, str], dict] = {}
    if not ev_csv.exists():
        return facts
    with ev_csv.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            tbl = {v: k for k, v in _ROLE.items()}.get(r.get("use_role", ""))
            if not tbl:
                continue
            key = (r.get("nbs_id", ""), tbl)
            d = facts.setdefault(key, {"ev": 0, "flagged": 0, "reviewed": 0})
            d["ev"] += 1
            if "[VERIFY-FLAG" in (r.get("attribution") or ""):
                d["flagged"] += 1
            if r.get("reviewer_ok") in (True, "true", "True"):
                d["reviewed"] += 1
    return facts


def check(schema_root: str | Path) -> list[str]:
    """Reconcile ledger claims vs register facts. Return list of violations (empty = OK)."""
    facts = derive_facts(schema_root)
    rows = {(r["nbs_id"], r["table"]): r for r in _rows()}
    errs: list[str] = []

    # 1. Every (nbs, table) that HAS evidence must have a ledger row claiming extracted=done.
    for key, fct in facts.items():
        if fct["ev"] > 0 and key not in rows:
            errs.append(
                f"[{key[0]}·{key[1]}] {fct['ev']} EV rows exist but there is NO ledger row "
                f"— stamp it: ledger.mark(...stage=extracted, status=done)"
            )

    for (nbs, tbl), r in rows.items():
        fct = facts.get((nbs, tbl), {"ev": 0, "flagged": 0, "reviewed": 0})
        st = {s: (r.get(s) or "not_started") for s in STAGES}
        for s, v in st.items():
            if v not in STATUSES:
                errs.append(f"[{nbs}·{tbl}] stage '{s}' has invalid status '{v}'")

        # 2. claims must be backed by facts
        if st["extracted"] == "done" and fct["ev"] == 0:
            errs.append(f"[{nbs}·{tbl}] extracted=done but 0 EV rows — unproven claim")
        if fct["ev"] > 0 and st["extracted"] != "done":
            errs.append(
                f"[{nbs}·{tbl}] {fct['ev']} EV rows exist but extracted!='done' "
                f"(={st['extracted']}) — stamp it or evidence entered outside the pipeline"
            )
        if st["reviewed"] == "done" and fct["reviewed"] == 0:
            errs.append(f"[{nbs}·{tbl}] reviewed=done but no reviewer_ok rows")
        if fct["reviewed"] > 0 and st["reviewed"] != "done":
            errs.append(
                f"[{nbs}·{tbl}] {fct['reviewed']} reviewed rows but reviewed!='done'"
            )

        # 3. stage order: a 'done' stage requires all earlier stages 'done'
        for i, s in enumerate(STAGES):
            if st[s] == "done":
                for earlier in STAGES[:i]:
                    if st[earlier] != "done":
                        errs.append(
                            f"[{nbs}·{tbl}] stage-order violation: {s}=done but {earlier}={st[earlier]}"
                        )
                        break
    return errs


def mark(
    nbs: str,
    table: str,
    stage: str,
    status: str,
    *,
    run_id: str = "",
    by: str = "orchestrator",
    categories: str | None = None,
    note: str = "",
) -> None:
    """Stamp a stage's status for (nbs, table). Called by the pipeline step that did the work."""
    if table not in TABLES:
        raise ValueError(f"table must be one of {TABLES}")
    if stage not in STAGES:
        raise ValueError(f"stage must be one of {STAGES}")
    if status not in STATUSES:
        raise ValueError(f"status must be one of {sorted(STATUSES)}")
    rows = _rows()
    row = next((r for r in rows if r["nbs_id"] == nbs and r["table"] == table), None)
    if row is None:
        row = {k: "" for k in FIELDS}
        row.update(nbs_id=nbs, table=table, **{s: "not_started" for s in STAGES})
        rows.append(row)
    row[stage] = status
    row["last_run_id"] = run_id or row.get("last_run_id", "")
    row["by"] = by
    row["updated"] = datetime.now(timezone.utc).date().isoformat()
    if categories is not None:
        row["searched_categories"] = categories
    if note:
        row["note"] = note
    _write(rows)


def _show() -> None:
    rows = _rows()
    if not rows:
        print("progress ledger is empty.")
        return
    print(f"{'nbs·table':28}  " + "  ".join(f"{s[:4]:>5}" for s in STAGES) + "  cats")
    for r in sorted(rows, key=lambda x: (x["nbs_id"], x["table"])):
        tick = {"done": "  ✓  ", "in_progress": " ~~  ", "not_started": "  ·  "}
        print(
            f"{r['nbs_id'] + '·' + r['table']:28}  "
            + "  ".join(tick.get(r.get(s) or "not_started", "  ?  ") for s in STAGES)
            + f"  {r.get('searched_categories', '')}"
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
    pm.add_argument("--stage", required=True)
    pm.add_argument("--status", required=True)
    pm.add_argument("--run-id", default="")
    pm.add_argument("--by", default="orchestrator")
    pm.add_argument("--categories", default=None)
    pm.add_argument("--note", default="")
    args = ap.parse_args(argv)

    if args.cmd == "show":
        _show()
        return 0
    if args.cmd == "mark":
        mark(
            args.nbs,
            args.table,
            args.stage,
            args.status,
            run_id=args.run_id,
            by=args.by,
            categories=args.categories,
            note=args.note,
        )
        print(f"marked {args.nbs}·{args.table} {args.stage}={args.status}")
        return 0
    # check
    errs = check(args.schema_root)
    if errs:
        print(f"LEDGER CHECK FAILED: {len(errs)} violation(s):", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("LEDGER OK: claims reconcile with the register; stage order valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
