"""Search-protocol register (SRCH) — the auditable record of every discovery search.

The progress ledger says *whether* a search ran (status); this records *what the search
was* — terms · inclusion criteria · limits · PRISMA counts · date · run · ruleset_version —
per (NbS × sub-practice × table × discovery-process). So "what searches did we do for FMNR
T3?" is answered with the exact protocol, reproducibly, not from memory or evidence presence.

The 4 discovery processes (= ledger categories / audit-matrix columns): stock · updated_lit
(OpenAlex) · grey (web/CGSpace) · tool. Each sub-practice × table runs all 4.

`ledger.check` requires a SRCH row before it will accept `searched=done` (no claimed search
without its logged protocol). `ruleset_version` pins the search/extract instructions in
force (see methodology/RULESET_VERSIONS.md + .agents/skills/_versions/).

CLI:
  uv run python3 -m nbs_ruralscan.schema_tools.search_log show
  uv run python3 -m nbs_ruralscan.schema_tools.search_log log --nbs agroforestry --table T3 \
      --category grey --family agroforestry__regeneration_farmland \
      --terms "FMNR parkland suitability Sahel" --limits "screen<=50" --ruleset v1.0 --run-id fmnr_2026
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRCH = ROOT / "schema" / "registers" / "SRCH_search_register.csv"
CATEGORIES = ["stock", "updated_lit", "grey", "tool"]
TABLES = ["T3", "T4", "T6"]
FIELDS = [
    "search_id",
    "nbs_id",
    "suitability_family_id",
    "table",
    "category",
    "search_terms",
    "screening_steps",
    "inclusion_criteria",
    "limits",
    "n_retrieved",
    "n_screened",
    "n_included",
    "search_date",
    "run_id",
    "searched_by",
    "ruleset_version",
    "discovery_log_ref",
    "note",
]


def rows(path: str | Path = SRCH) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def has_search(
    nbs: str, table: str, category: str, family: str = "", path: str | Path = SRCH
) -> bool:
    """True if a logged search covers this cell. A table-level (family='') row covers all
    families; a family-specific row covers that family."""
    for r in rows(path):
        if (
            r.get("nbs_id") == nbs
            and r.get("table") == table
            and r.get("category") == category
        ):
            rf = r.get("suitability_family_id", "") or ""
            if rf == "" or rf == family:
                return True
    return False


def log_search(
    *,
    nbs: str,
    table: str,
    category: str,
    search_terms: str,
    ruleset_version: str,
    family: str = "",
    screening_steps: str = "",
    inclusion_criteria: str = "",
    limits: str = "",
    n_retrieved: str = "",
    n_screened: str = "",
    n_included: str = "",
    run_id: str = "",
    searched_by: str = "orchestrator",
    discovery_log_ref: str = "",
    note: str = "",
    path: str | Path = SRCH,
) -> dict:
    """Append a search-protocol row. Validates table/category + required fields."""
    if table not in TABLES:
        raise ValueError(f"table must be one of {TABLES}")
    if category not in CATEGORIES:
        raise ValueError(f"category must be one of {CATEGORIES}")
    if not search_terms.strip():
        raise ValueError("search_terms is required (what was actually searched)")
    if not ruleset_version.strip():
        raise ValueError("ruleset_version is required (which instructions governed it)")
    date = datetime.now(timezone.utc).date().isoformat()
    fam_tag = family or "all"
    sid = f"{nbs}__{table}__{category}__{fam_tag}__{date}"
    row = {
        "search_id": sid,
        "nbs_id": nbs,
        "suitability_family_id": family,
        "table": table,
        "category": category,
        "search_terms": search_terms,
        "screening_steps": screening_steps,
        "inclusion_criteria": inclusion_criteria,
        "limits": limits,
        "n_retrieved": n_retrieved,
        "n_screened": n_screened,
        "n_included": n_included,
        "search_date": date,
        "run_id": run_id,
        "searched_by": searched_by,
        "ruleset_version": ruleset_version,
        "discovery_log_ref": discovery_log_ref,
        "note": note,
    }
    existing = rows(path)
    existing = [r for r in existing if r.get("search_id") != sid]  # upsert by id
    existing.append(row)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in existing:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    return row


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    pl = sub.add_parser("log")
    pl.add_argument("--nbs", required=True)
    pl.add_argument("--table", required=True)
    pl.add_argument("--category", required=True)
    pl.add_argument("--terms", required=True)
    pl.add_argument("--ruleset", required=True)
    pl.add_argument("--family", default="")
    pl.add_argument("--screening-steps", default="")
    pl.add_argument("--inclusion", default="")
    pl.add_argument("--limits", default="")
    pl.add_argument("--retrieved", default="")
    pl.add_argument("--screened", default="")
    pl.add_argument("--included", default="")
    pl.add_argument("--run-id", default="")
    pl.add_argument("--by", default="orchestrator")
    pl.add_argument("--log-ref", default="")
    pl.add_argument("--note", default="")
    args = ap.parse_args(argv)

    if args.cmd == "show":
        for r in rows():
            fam = r.get("suitability_family_id") or "all"
            print(
                f"{r['nbs_id']}·{r['table']}·{r['category']}·{fam:30}  "
                f"n={r.get('n_included') or '?'}  {r.get('search_date')}  {r['search_id']}"
            )
        return 0
    r = log_search(
        nbs=args.nbs,
        table=args.table,
        category=args.category,
        search_terms=args.terms,
        ruleset_version=args.ruleset,
        family=args.family,
        screening_steps=args.screening_steps,
        inclusion_criteria=args.inclusion,
        limits=args.limits,
        n_retrieved=args.retrieved,
        n_screened=args.screened,
        n_included=args.included,
        run_id=args.run_id,
        searched_by=args.by,
        discovery_log_ref=args.log_ref,
        note=args.note,
    )
    print(f"logged search {r['search_id']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
