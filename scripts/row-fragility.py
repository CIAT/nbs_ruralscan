#!/usr/bin/env python3
"""Leave-one-out fragility of generated T3/T6 roll-up rows (review triage).

    python3 scripts/row-fragility.py <nbs_id> [--out pipeline/metrics/row_fragility_<nbs>.csv]

For every NbS-level roll-up row, each evidence unit in the row is removed in turn and the
row's cell is re-synthesised with exactly the production engine and policies
(`synthesise-t3t6.py`). A unit is PIVOTAL when its removal changes the row's class (or
removes the row). The output ranks rows by how few units hold their class up — the rows a
human reviewer should read first. Read-only: writes the CSV only, never the recipes.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "synth_t3t6", ROOT / "scripts" / "synthesise-t3t6.py"
)
assert _spec and _spec.loader
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
cs = S.cs


def _label(row: dict[str, Any] | None) -> str:
    if row is None:
        return "row gone"
    acc = row.get("justification") or {}
    if isinstance(acc, dict) and acc.get("data_deficient"):
        return "data_deficient"
    for k in ("effect_direction", "mitigation_potential", "asset_sensitivity"):
        v = row.get(k)
        if v:
            return str(v)
    return ""


def _cell_runner(nbs_id: str, inp: dict[str, Any]):
    xw = cs.filter_xw(inp["xw"], nbs_id, S.XW_ROUTE_POLICY)
    common = {
        "categories": inp["categories"],
        "src_contexts": inp["src_contexts"],
        "income_lookup": inp["income"],
        "matrix": inp["matrix"],
        "xw_rows": xw,
        "allow_crop_scope": S.crop_scope_policy(nbs_id),
    }

    def run(units, table: str, key: str, fs: str | None, role: str | None):
        kw: dict[str, Any] = dict(
            table=table,
            nbs_id=nbs_id,
            comparator_policy=S.COMPARATOR_POLICY,
            family_rollup_policy=S.FAMILY_ROLLUP_POLICY,
            target_key=key,
            **common,
        )
        if fs is not None:
            kw["farming_system"] = fs
        if role is not None:
            kw["role"] = role
        rows, _ = cs.synthesise_cell_with_families(units, inp["tiers"], **kw)
        return rows

    return run


def _cell_of(row: dict[str, Any]) -> tuple[str, str, str | None, str | None]:
    """(table, target_key, farming_system, role) that regenerates this row."""
    if row.get("variable_id"):
        return "T6", row["variable_id"], None, None
    if row.get("risk_role") == "asset_threat":
        return "T3", row["hazard_type"], None, "asset_vulnerability"
    return "T3", row["hazard_type"], row.get("farming_system") or "all", None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("nbs_id")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    inp = S.load_inputs(a.nbs_id, [])
    run = _cell_runner(a.nbs_id, inp)
    units = inp["units"]
    out_rows: list[dict[str, Any]] = []
    for stem in ("T3_nbs_hazard_farming", "T6_nbs_scorecard"):
        path = S.SCHEMA / "recipes" / a.nbs_id / f"{stem}.csv"
        with path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("suitability_family_id") or r.get("scope_type"):
                    continue  # NbS-level roll-up rows only
                r = dict(r)
                for k in ("justification", "evidence_ids"):
                    try:
                        r[k] = (
                            json.loads(r[k])
                            if r.get(k)
                            else ({} if k == "justification" else [])
                        )
                    except json.JSONDecodeError:
                        pass
                table, key, fs, role = _cell_of(r)
                base = _label(r)
                ids = list(r.get("evidence_ids") or [])
                pivots: list[tuple[str, str]] = []
                for eid in ids:
                    sub = [u for u in units if u.evidence_id != eid]
                    rows = run(sub, table, key, fs, role)
                    same = next(
                        (x for x in rows if x["record_id"] == r["record_id"]), None
                    )
                    lab = _label(same)
                    if lab != base:
                        pivots.append((eid, lab))
                out_rows.append(
                    {
                        "record_id": r["record_id"],
                        "class": base,
                        "n_units": len(ids),
                        "n_pivotal": len(pivots),
                        "pivotal_units": "; ".join(
                            f"{e} -> {lab}" for e, lab in pivots[:8]
                        ),
                    }
                )
    out = Path(a.out or ROOT / "pipeline" / "metrics" / f"row_fragility_{a.nbs_id}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    out_rows.sort(key=lambda x: (-x["n_pivotal"], x["record_id"]))
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    print(f"{len(out_rows)} roll-up rows -> {out}")
    for x in out_rows[:12]:
        print(
            f"  {x['n_pivotal']:3d} pivotal / {x['n_units']:3d}  {x['class']:22s} {x['record_id']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
