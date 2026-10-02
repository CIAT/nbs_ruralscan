#!/usr/bin/env python3
"""Prose writer tooling for generated T3/T6 rows (synthesis contract §5).

    python3 scripts/write-prose.py bundle <nbs_id>            # rows needing prose + their used units
    python3 scripts/write-prose.py check  <nbs_id> <prose.json>   # validate, write nothing
    python3 scripts/write-prose.py merge  <nbs_id> <prose.json> [--writer opus]

`bundle` writes `pipeline/staging/prose/<nbs_id>_bundle.json` — for every row whose prose is
pending or stale: the engine's statement/levels/envelope and, for each used unit, the verbatim
quote, page, outcome_raw, relationship, context, claim_basis, source citation. That bundle is
the ONLY input the prose writer may draw on.

`<prose.json>` is `{record_id: {"mechanism": str, "conditionality": str,
"evidence_summary": [str] | null, "agreement_note": str | null}}`. `merge` runs
`check_account` on the would-be rows, refuses on any flag, otherwise records the prose in
`schema/recipes/<nbs_id>/T3T6_prose.json` (keyed to the rows' current `evidence_ids`), applies
it to the CSVs and regenerates their JSON. Re-running `synthesise-t3t6.py` re-applies the
sidecar automatically while the evidence set is unchanged.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from nbs_ruralscan.recipe import prose as P
from nbs_ruralscan.schema_tools.generate import _csv_to_rows

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"
REG = SCHEMA / "registers"
TABLES = (("T3", "T3_nbs_hazard_farming"), ("T6", "T6_nbs_scorecard"))
_JSON_COLS = {
    "justification",
    "applicability",
    "evidence_ids",
    "economic_value_range",
    "magnitude_summary",
}


def _rd(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _rows(nbs_id: str, stem: str) -> tuple[list[dict[str, Any]], list[str]]:
    path = SCHEMA / "recipes" / nbs_id / f"{stem}.csv"
    raw = _rd(path)
    cols = list(raw[0].keys()) if raw else []
    rows: list[dict[str, Any]] = []
    for r in raw:
        d: dict[str, Any] = dict(r)
        for c in _JSON_COLS:
            if c in d and d[c]:
                try:
                    d[c] = json.loads(d[c])
                except json.JSONDecodeError:
                    pass
        rows.append(d)
    return rows, cols


def _cell(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _write_rows(
    nbs_id: str, stem: str, rows: list[dict[str, Any]], cols: list[str]
) -> None:
    rdir = SCHEMA / "recipes" / nbs_id
    path = rdir / f"{stem}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=cols, lineterminator="\n", extrasaction="ignore"
        )
        w.writeheader()
        for r in rows:
            w.writerow({c: _cell(r.get(c)) for c in cols})
    (rdir / f"{stem}.json").write_text(
        json.dumps(_csv_to_rows(path), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _needs_prose(row: dict[str, Any], sidecar: dict[str, dict[str, Any]]) -> bool:
    entry = sidecar.get(row["record_id"])
    if entry and sorted(entry.get("evidence_ids") or []) == P._ids(row):
        return False
    acc = row.get("justification") or {}
    return bool(acc.get("prose_pending", True))


def bundle(nbs_id: str) -> Path:
    ev = {r["evidence_id"]: r for r in _rd(REG / "EV_evidence_register.csv")}
    src = {r["source_id"]: r for r in _rd(REG / "SRC_source_register.csv")}
    sidecar = P.load_sidecar(SCHEMA / "recipes" / nbs_id)
    out: list[dict[str, Any]] = []
    for table, stem in TABLES:
        rows, _ = _rows(nbs_id, stem)
        for r in rows:
            if not _needs_prose(r, sidecar):
                continue
            acc = r.get("justification") or {}
            units = []
            for eid in P._ids(r):
                u = ev.get(eid)
                if not u:
                    continue
                rel = u.get("relationship") or ""
                ctx = u.get("context") or ""
                units.append(
                    {
                        "evidence_id": eid,
                        "source_id": u["source_id"],
                        "citation": src.get(u["source_id"], {}).get("citation", ""),
                        "benchmark_tier": src.get(u["source_id"], {}).get(
                            "benchmark_tier", ""
                        ),
                        "page": u.get("page"),
                        "quote": u.get("quote"),
                        "variable": u.get("variable"),
                        "raw_name": u.get("raw_name"),
                        "claim_basis": u.get("claim_basis"),
                        "claim_scope": u.get("claim_scope"),
                        "lineage_of": u.get("lineage_of"),
                        "relationship": json.loads(rel) if rel else {},
                        "context": json.loads(ctx) if ctx else {},
                    }
                )
            out.append(
                {
                    "table": table,
                    "record_id": r["record_id"],
                    "nbs_id": r["nbs_id"],
                    "target": r.get("hazard_type") or r.get("variable_id"),
                    "farming_system": r.get("farming_system"),
                    "scope": {"type": r.get("scope_type"), "id": r.get("scope_id")},
                    "suitability_family_id": r.get("suitability_family_id"),
                    "risk_role": r.get("risk_role"),
                    "class": r.get("mitigation_potential")
                    or r.get("effect_direction")
                    or r.get("asset_sensitivity"),
                    "confidence": r.get("confidence") or r.get("effect_confidence"),
                    "evidence_level": r.get("evidence_level"),
                    "agreement_level": r.get("agreement_level"),
                    "statement": acc.get("statement"),
                    "strength_basis": acc.get("strength_basis"),
                    "engine_evidence_summary": acc.get("evidence_summary"),
                    "engine_agreement_note": acc.get("agreement_note"),
                    "proxies": acc.get("proxies"),
                    "applicability": r.get("applicability"),
                    "economic_value_range": r.get("economic_value_range"),
                    "magnitude_summary": r.get("magnitude_summary"),
                    "units": units,
                }
            )
    dest = ROOT / "pipeline" / "staging" / "prose" / f"{nbs_id}_bundle.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"{len(out)} row(s) need prose → {dest.relative_to(ROOT)}")
    return dest


def _load_prose(path: Path) -> dict[str, dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def check(nbs_id: str, prose_path: Path) -> int:
    prose = _load_prose(prose_path)
    total_flags: list[dict[str, Any]] = []
    seen: set[str] = set()
    for table, stem in TABLES:
        rows, _ = _rows(nbs_id, stem)
        ids = {r["record_id"] for r in rows}
        sub = {k: v for k, v in prose.items() if k in ids}
        seen |= set(sub)
        total_flags += P.check_prose(rows, table, sub)
    for k in set(prose) - seen:
        total_flags.append({"signal": "unknown_record", "record_id": k, "detail": ""})
    if not total_flags:
        print(f"PROSE CHECK: {len(prose)} row(s) clean.")
        return 0
    print(f"PROSE CHECK: {len(total_flags)} flag(s):")
    for f in total_flags[:80]:
        print(f"  [{f['signal']}] {f['record_id']}: {f['detail']}")
    return 1


def merge(nbs_id: str, prose_path: Path, writer: str) -> int:
    if check(nbs_id, prose_path) != 0:
        print("nothing written")
        return 1
    prose = _load_prose(prose_path)
    rdir = SCHEMA / "recipes" / nbs_id
    n = 0
    for table, stem in TABLES:
        rows, cols = _rows(nbs_id, stem)
        ids = {r["record_id"] for r in rows}
        sub = {k: v for k, v in prose.items() if k in ids}
        if not sub:
            continue
        applied, flags = P.merge_prose(rdir, rows, table, sub, writer=writer)
        if flags:
            print("merge refused:", flags[:5])
            return 1
        _write_rows(nbs_id, stem, rows, cols)
        n += applied
    print(
        f"merged prose onto {n} row(s); sidecar {P.sidecar_path(rdir).relative_to(ROOT)}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bundle")
    b.add_argument("nbs_id")
    c = sub.add_parser("check")
    c.add_argument("nbs_id")
    c.add_argument("prose")
    m = sub.add_parser("merge")
    m.add_argument("nbs_id")
    m.add_argument("prose")
    m.add_argument("--writer", default="opus")
    a = ap.parse_args(argv)
    if a.cmd == "bundle":
        bundle(a.nbs_id)
        return 0
    if a.cmd == "check":
        return check(a.nbs_id, Path(a.prose))
    return merge(a.nbs_id, Path(a.prose), a.writer)


if __name__ == "__main__":
    raise SystemExit(main())
