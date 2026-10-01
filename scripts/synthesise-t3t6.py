#!/usr/bin/env python3
"""Generate an NbS recipe's T3 + T6 tables from the evidence register (cell synthesis).

The `/t3t6-synthesise` skill (methodology/T3_T6_generation_method.md §7; contract
`.agents/skills/_versions/v1.6.0/contracts/T3_T6_synthesis_contract.md`). Runs
`recipe.cell_synthesis.synthesise_cell_with_families` for every cell the XW crosswalk routes
evidence to, and writes:

* `schema/recipes/<nbs_id>/T3_nbs_hazard_farming.csv` — mitigation rows (per hazard ×
  farming_system) + asset-threat rows (per hazard), each as global + scope + family rows
* `schema/recipes/<nbs_id>/T6_nbs_scorecard.csv` — effect rows (per T5 priority) + economic rows
* `schema/recipes/<nbs_id>/T3T6_synthesis_report.json` — the run report (used units, dropped,
  collapsed echoes, unmapped variables, excluded economics, incomplete asset weights)

Inputs are read from the registers, never hand-passed: tiers / categories / study context from
SRC, routes from XW, income groups and the IPCC matrix from `schema/lookups/`. Regenerate the
recipe JSON with `schema_tools/generate.py` afterwards.

Usage:
    python3 scripts/synthesise-t3t6.py riparian_buffer
    python3 scripts/synthesise-t3t6.py riparian_buffer --dry-run
    python3 scripts/synthesise-t3t6.py riparian_buffer --staging pipeline/staging/riparian_effects_A.json ...
        (also pool not-yet-registered staging units — dry-run preview only; the register is the
        source of truth and staging units must go through the central gates first)
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from nbs_ruralscan.recipe import cell_synthesis as cs
from nbs_ruralscan.recipe import prose as P
from nbs_ruralscan.recipe.evidence import EvidenceUnit, load_units

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"
REG = SCHEMA / "registers"
LOOK = SCHEMA / "lookups"

# column orders as frozen in schema/structure/columns.json (v0.4.0) — required + optional + conditional
T3_FIELDS = [
    "record_id",
    "nbs_id",
    "hazard_type",
    "farming_system",
    "mitigation_potential",
    "mitigation_mechanism",
    "confidence",
    "timescale_of_effect",
    "landscape_scale_only",
    "caveats",
    "justification",
    "risk_role",
    "evidence_ids",
    "suitability_family_id",
    "scope_type",
    "scope_id",
    "applicability",
    "family_spread",
    "evidence_level",
    "agreement_level",
    "context_dependent",
    "asset_sensitivity",
    "asset_risk_weight",
]
T6_FIELDS = [
    "record_id",
    "nbs_id",
    "variable_id",
    "variable_type",
    "effect_direction",
    "effect_confidence",
    "effect_mechanism",
    "conditionality",
    "timescale_of_effect",
    "economic_indicator_type",
    "economic_value_range",
    "justification",
    "economic_archetype_id",
    "evidence_ids",
    "suitability_family_id",
    "scope_type",
    "scope_id",
    "applicability",
    "family_spread",
    "magnitude_summary",
    "evidence_level",
    "agreement_level",
    "context_dependent",
]
T3_HAZARDS = cs.T3_HAZARDS


def _rd(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _cell(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def load_inputs(nbs_id: str, staging: list[Path]) -> dict[str, Any]:
    src = _rd(REG / "SRC_source_register.csv")
    tiers = {r["source_id"]: (r["benchmark_tier"] or "medium").lower() for r in src}
    categories = {r["source_id"]: r.get("source_category", "") for r in src}
    # SRC.study_country is free text ("Brazil; Colombia; Mexico", "Global"): normalise to
    # ISO3 here so the envelope never carries a raw name (riparian prose review 2026-10-01)
    name_to_iso3 = {
        r["country_name"]: r["iso3"] for r in _rd(LOOK / "wb_income_groups.csv")
    }
    src_contexts: dict[str, dict[str, Any]] = {}
    unresolved: dict[str, list[str]] = {}
    for r in src:
        codes, bad = cs.normalise_countries(r.get("study_country", ""), name_to_iso3)
        if bad:
            unresolved[r["source_id"]] = bad
        src_contexts[r["source_id"]] = {
            "country": codes,
            "aez": r.get("aez", ""),
            "farming_system": r.get("farming_system", ""),
            "income_group": r.get("study_income_group", ""),
        }
    xw = cs.load_xw(REG / "XW_target_crosswalk.csv")
    income = cs.load_income_lookup(LOOK / "wb_income_groups.csv")
    matrix = cs.load_confidence_matrix(LOOK / "ipcc_confidence_matrix.csv")
    units = [
        u
        for u in load_units(REG / "EV_evidence_register.json")
        if u.nbs_id == nbs_id and u.use_role in cs.EFFECT_ROLES
    ]
    for p in staging:
        units += [
            u
            for u in load_units(p)
            if u.nbs_id == nbs_id and u.use_role in cs.EFFECT_ROLES
        ]
    return {
        "units": units,
        "tiers": tiers,
        "categories": categories,
        "src_contexts": src_contexts,
        "src_country_unresolved": unresolved,
        "xw": xw,
        "income": income,
        "matrix": matrix,
    }


def synthesise(nbs_id: str, inp: dict[str, Any]) -> dict[str, Any]:
    units: list[EvidenceUnit] = inp["units"]
    xw: list[cs.XWRow] = inp["xw"]
    common: dict[str, Any] = {
        "categories": inp["categories"],
        "src_contexts": inp["src_contexts"],
        "income_lookup": inp["income"],
        "matrix": inp["matrix"],
        "xw_rows": xw,
    }
    t3_rows: list[dict[str, Any]] = []
    t6_rows: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "nbs_id": nbs_id,
        "n_units_pooled": len(units),
        "units_by_role": dict(Counter(u.use_role for u in units)),
        "cells": [],
        "dropped": [],
        "collapsed": [],
        "excluded_economics": [],
        "weights_incomplete": [],
        "notes": [],
    }
    live_vars = {u.variable for u in units if u.use_role == "nbs_effect"}
    routed_vars = {x.ev_variable for x in xw}
    report["unmapped_variables"] = sorted(
        {
            v: sum(1 for u in units if u.variable == v and u.use_role == "nbs_effect")
            for v in live_vars - routed_vars
        }.items()
    )

    def _collect(rows, rep, table, key):
        report["cells"].append(
            {
                "table": table,
                "cell": key,
                "rows": len(rows),
                "used": len(rep.used),
                "scope_rows": rep.scope_rows_emitted,
            }
        )
        report["dropped"] += [(table, key, *d) for d in rep.dropped]
        report["collapsed"] += [(table, key, *c) for c in rep.collapsed]
        report["excluded_economics"] += [
            (table, key, *e) for e in rep.excluded_economics
        ]
        report["notes"] += rep.notes

    # ── T6: every XW T6 target (priorities + economic indicators) ──
    for key in sorted({x.target_key for x in xw if x.target_table == "T6"}):
        rows, rep = cs.synthesise_cell_with_families(
            units, inp["tiers"], table="T6", nbs_id=nbs_id, target_key=key, **common
        )
        if rows:
            t6_rows += rows
            _collect(rows, rep, "T6", key)

    # ── T3 mitigation: every XW T3 hazard × the farming systems present (+ all) ──
    fs_present = sorted(
        {str((u.context or {}).get("farming_system") or "all") for u in units} | {"all"}
    )
    for hz in sorted({x.target_key for x in xw if x.target_table == "T3"}):
        for fs in fs_present:
            rows, rep = cs.synthesise_cell_with_families(
                units,
                inp["tiers"],
                table="T3",
                nbs_id=nbs_id,
                target_key=hz,
                farming_system=fs,
                **common,
            )
            if rows:
                t3_rows += rows
                _collect(rows, rep, "T3", f"{hz}__{fs}")

    # ── T3 asset threat: per hazard, from asset_vulnerability units ──
    for hz in T3_HAZARDS:
        rows, rep = cs.synthesise_cell_with_families(
            units,
            inp["tiers"],
            table="T3",
            nbs_id=nbs_id,
            target_key=hz,
            role="asset_vulnerability",
            **common,
        )
        if rows:
            t3_rows += rows
            _collect(rows, rep, "T3", f"asset_threat__{hz}")
    weights = cs.asset_risk_weights(t3_rows, nbs_id)
    if weights is None:
        if any(r.get("risk_role") == "asset_threat" for r in t3_rows):
            report["weights_incomplete"].append(nbs_id)
    else:
        for r in t3_rows:
            if (
                r.get("risk_role") == "asset_threat"
                and not r.get("scope_type")
                and not r.get("suitability_family_id")
            ):
                r["asset_risk_weight"] = weights[r["hazard_type"]]

    report["t3_rows"] = len(t3_rows)
    report["t6_rows"] = len(t6_rows)
    return {"T3": t3_rows, "T6": t6_rows, "report": report}


def write_recipe(nbs_id: str, out: dict[str, Any], *, dry_run: bool) -> list[Path]:
    rdir = SCHEMA / "recipes" / nbs_id
    written: list[Path] = []
    # prose sidecar (contract §5): re-apply AI-written mechanism/conditionality only to rows
    # whose evidence_ids are exactly what the prose was written against; else stays pending
    sidecar = P.load_sidecar(rdir)
    for table, fields, fname in (
        ("T3", T3_FIELDS, "T3_nbs_hazard_farming.csv"),
        ("T6", T6_FIELDS, "T6_nbs_scorecard.csv"),
    ):
        rows = out[table]
        if sidecar:
            applied, stale = P.apply_prose(rows, table, sidecar)
            print(
                f"{table}: prose applied to {applied} row(s); {stale} stale (evidence changed → pending)"
            )
        path = rdir / fname
        if dry_run:
            print(f"[dry-run] {path}: {len(rows)} row(s)")
            continue
        rdir.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(
                f, fieldnames=fields, lineterminator="\n", extrasaction="ignore"
            )
            w.writeheader()
            for r in rows:
                w.writerow({c: _cell(r.get(c)) for c in fields})
        written.append(path)
    rp = rdir / "T3T6_synthesis_report.json"
    if not dry_run:
        rp.write_text(
            json.dumps(out["report"], ensure_ascii=False, indent=2, default=str) + "\n",
            encoding="utf-8",
        )
        written.append(rp)
    return written


def _summary(out: dict[str, Any]) -> str:
    lines = [
        "| table | record_id | class | evidence×agreement→confidence | n | transfer | strength |",
        "|---|---|---|---|---|---|---|",
    ]
    for table in ("T3", "T6"):
        for r in out[table]:
            cls = (
                r.get("effect_direction")
                or r.get("mitigation_potential")
                or r.get("asset_sensitivity")
            )
            conf = r.get("confidence") or r.get("effect_confidence")
            app = r.get("applicability") or {}
            sb = (r.get("justification") or {}).get("strength_basis", "")
            lines.append(
                f"| {table} | {r['record_id']} | {cls} | {r['evidence_level']}×{r['agreement_level']}→{conf} | {r.get('n_sources')} | {app.get('transfer_class')} | {sb} |"
            )
    rep = out["report"]
    lines.append("")
    lines.append(
        f"pooled units {rep['n_units_pooled']} {rep['units_by_role']}; T3 rows {rep['t3_rows']}; T6 rows {rep['t6_rows']}"
    )
    if rep["unmapped_variables"]:
        lines.append(f"unmapped variables: {rep['unmapped_variables']}")
    if rep["excluded_economics"]:
        lines.append(f"excluded economics: {len(rep['excluded_economics'])}")
    if rep["weights_incomplete"]:
        lines.append(
            f"asset_risk_weight blank (incomplete hazard set): {rep['weights_incomplete']}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("nbs_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--staging",
        nargs="*",
        default=[],
        help="extra unit JSON files to pool (preview only)",
    )
    args = ap.parse_args(argv)
    staging = [Path(p) for p in args.staging]
    if staging and not args.dry_run:
        print(
            "--staging is preview-only; add --dry-run (register units must pass the central gates first)"
        )
        return 2
    inp = load_inputs(args.nbs_id, staging)
    out = synthesise(args.nbs_id, inp)
    print(_summary(out))
    used = {u.source_id for u in inp["units"]}
    bad = {k: v for k, v in inp["src_country_unresolved"].items() if k in used}
    if bad:
        print(
            f"SRC.study_country tokens not resolved to ISO3 (dropped from envelopes): {bad}"
        )
    for p in write_recipe(args.nbs_id, out, dry_run=args.dry_run):
        print("wrote", p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
