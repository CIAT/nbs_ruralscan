"""Progress ledger — orchestrator-owned, register-enforced, per (NbS × table × category × family).

Tracks, for each (nbs_id × table[T4/T3/T6] × source-category[stock/updated_lit/grey/tool]
× suitability_family), the AUTHORED process stages: searched · screened · verified. These
cannot be derived from data (a search either happened or didn't, and **absence of evidence
is NOT proof a search was run** — it may be searched-and-empty), so the pipeline STEP that
runs them stamps the ledger via `mark()`. Extraction (E) and review (R) ARE facts, derived
live from the register — they are not stored here.

`family` granularity (2026-06-25): an empty `family` = the table-level / all-families search
(the default — a bounded seed-set sweep reads papers spanning families). A specific
`family` (e.g. `agroforestry__regeneration_farmland`) records a SUB-PRACTICE-targeted search
status as source of truth — so "have we searched for FMNR T3?" is answerable from the
ledger, never inferred from whether evidence happens to exist. Existing rows keep `family=""`.

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
    ["nbs_id", "table", "category", "family"]
    + STAGES
    + ["last_run_id", "updated", "by", "note"]
)


def _rows() -> list[dict]:
    if not LEDGER.exists():
        return []
    with LEDGER.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write(rows: list[dict]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
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
    """Per (nbs_id, table, category, family): ev count + reviewed count, from the register.

    `family` is the EV's `suitability_family_id`. Aggregate (all-families) facts for a
    `(nbs, table, category)` are obtained with `facts_for(..., family="")` which sums over
    families — matching a `family=""` ledger row.
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
            key = (
                r.get("nbs_id", ""),
                tbl,
                cat.get(r.get("source_id", ""), "stock"),
                r.get("suitability_family_id", ""),
            )
            d = facts.setdefault(key, {"ev": 0, "reviewed": 0})
            d["ev"] += 1
            if r.get("reviewer_ok") in (True, "true", "True"):
                d["reviewed"] += 1
    return facts


def facts_for(
    facts: dict[tuple, dict], nbs: str, tbl: str, c: str, family: str
) -> dict:
    """Resolve facts for a ledger cell: a specific family, or (family=='') the sum over all."""
    if family:
        return facts.get((nbs, tbl, c, family), {"ev": 0, "reviewed": 0})
    agg = {"ev": 0, "reviewed": 0}
    for (n, t, cc, _fam), d in facts.items():
        if n == nbs and t == tbl and cc == c:
            agg["ev"] += d["ev"]
            agg["reviewed"] += d["reviewed"]
    return agg


def check(schema_root: str | Path) -> list[str]:
    """Hard reconciliation (build-failing). Returns list of violations (empty = OK)."""
    from nbs_ruralscan.schema_tools.search_log import has_search

    srch = Path(schema_root) / "registers" / "SRCH_search_register.csv"
    facts = derive_facts(schema_root)
    errs: list[str] = []
    for r in _rows():
        nbs, tbl, c, fam = (
            r["nbs_id"],
            r["table"],
            r["category"],
            r.get("family", "") or "",
        )
        lbl = f"{nbs}·{tbl}·{c}" + (f"·{fam}" if fam else "")
        # a claimed search must have a logged protocol in SRCH (no search without a record)
        if (r.get("searched") or "not_started") == "done" and not has_search(
            nbs, tbl, c, fam, path=srch
        ):
            errs.append(
                f"[{lbl}] searched=done but no SRCH search-protocol row — log the search "
                "(terms/criteria/limits) via search_log before claiming it"
            )
        if tbl not in TABLES:
            errs.append(f"[{lbl}] invalid table '{tbl}'")
        if c not in CATEGORIES:
            errs.append(f"[{lbl}] invalid category '{c}'")
        for s in STAGES:
            if (r.get(s) or "not_started") not in STATUSES:
                errs.append(f"[{lbl}] stage '{s}'='{r.get(s)}' invalid")
        if (r.get("verified") or "not_started") == "done":
            if facts_for(facts, nbs, tbl, c, fam).get("ev", 0) == 0:
                errs.append(
                    f"[{lbl}] verified=done but 0 evidence units — nothing to verify"
                )
    return errs


def coverage_warnings(schema_root: str | Path) -> list[str]:
    """Non-fatal: cells holding evidence from a category whose search isn't 'done'.

    Checks at table level (family='' ledger rows) — a family-specific 'done' also counts."""
    facts = derive_facts(schema_root)
    rows = list(_rows())

    def _searched_done(nbs: str, tbl: str, c: str, fam: str) -> bool:
        for r in rows:
            if r["nbs_id"] == nbs and r["table"] == tbl and r["category"] == c:
                rf = r.get("family", "") or ""
                if (rf == "" or rf == fam) and (r.get("searched") or "") == "done":
                    return True
        return False

    out = []
    for (nbs, tbl, c, fam), fct in facts.items():
        if fct["ev"] > 0 and not _searched_done(nbs, tbl, c, fam):
            out.append(
                f"[{nbs}·{tbl}·{c}" + (f"·{fam}" if fam else "") + f"] {fct['ev']} "
                "evidence units but search != done — ad-hoc/incomplete search coverage"
            )
    return out


def mark(
    nbs: str,
    table: str,
    category: str,
    stage: str,
    status: str,
    *,
    family: str = "",
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
            if r["nbs_id"] == nbs
            and r["table"] == table
            and r["category"] == category
            and (r.get("family", "") or "") == family
        ),
        None,
    )
    if row is None:
        row = {k: "" for k in FIELDS}
        row.update(
            nbs_id=nbs,
            table=table,
            category=category,
            family=family,
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
    print(f"{'nbs·table·category·family':48}  " + " ".join(f"{s[:4]}" for s in STAGES))
    for r in sorted(
        rows,
        key=lambda x: (
            x["nbs_id"],
            x["table"],
            x["category"],
            x.get("family", "") or "",
        ),
    ):
        fam = r.get("family", "") or ""
        key = f"{r['nbs_id']}·{r['table']}·{r['category']}" + (f"·{fam}" if fam else "")
        print(
            f"{key:48}  "
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
    pm.add_argument(
        "--family",
        default="",
        help="suitability_family_id; empty = table-level/all-families",
    )
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
            family=args.family,
            run_id=args.run_id,
            by=args.by,
            note=args.note,
        )
        _k = f"{args.nbs}·{args.table}·{args.category}" + (
            f"·{args.family}" if args.family else ""
        )
        print(f"marked {_k} {args.stage}={args.status}")
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
