#!/usr/bin/env python3
"""Synthesise an NbS recipe's T4 slice from the evidence register.

Runs `synthesise_family` for every suitability family of one NbS (the t4-synthesise skill,
T4 method section 6) and writes both artefacts the recipe needs:

* `schema/recipes/<nbs_id>/T4_<family>.json` — the enriched per-family rows + provenance
* `schema/recipes/<nbs_id>/T4_suitability_mappings.csv` — the recipe table the dashboard
  and the pipeline read (regenerate its JSON with schema_tools/generate.py afterwards)

Inputs are read from the registers, never hand-passed: tiers from `SRC.benchmark_tier`,
grouping/units/datasets/conversions from `VONT`, grey-discount categories from
`SRC.source_category`, and `corpus_n` from the family's `SRCH` screened-in counts summed
over the four discovery processes.

Usage:
    python3 scripts/synthesise-recipe.py riparian_buffer
    python3 scripts/synthesise-recipe.py riparian_buffer --dry-run
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

from nbs_ruralscan.recipe.evidence import load_units
from nbs_ruralscan.recipe.family import FamilyResult, save_family, synthesise_family

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "schema" / "registers"

# T4 column order, as frozen in schema/structure/columns.json
T4_FIELDS = [
    "mapping_id",
    "nbs_id",
    "dataset_id",
    "suitability_dimension",
    "relationship_type",
    "relationship_params",
    "uncertainty_pct",
    "context_overrides",
    "is_scenario_candidate",
    "scenario_label",
    "scenario_description",
    "has_future_projection",
    "baseline_dataset_id",
    "future_dataset_ids",
    "weight_default",
    "weight_adjustable",
    "justification",
    "variable",
    "suitability_family_id",
    "evidence_ids",
    "n_sources",
    "corpus_n",
    "paper_support_pct",
]


def _rd(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _first_dataset(raw: str | None) -> str:
    """VONT candidate_dataset_ids is a JSON list; T4.dataset_id takes the preferred one."""
    try:
        ids = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return ""
    return ids[0] if ids else ""


def synthesise(nbs_id: str) -> dict[str, FamilyResult]:
    src, vont, srch = (
        _rd(REG / n)
        for n in (
            "SRC_source_register.csv",
            "VONT_variable_ontology.csv",
            "SRCH_search_register.csv",
        )
    )
    tiers = {r["source_id"]: (r["benchmark_tier"] or "medium") for r in src}
    categories = {r["source_id"]: r["source_category"] for r in src}
    group_map = {r["canonical_variable_id"]: r["group_id"] for r in vont}
    canonical_units = {r["canonical_variable_id"]: r["canonical_unit"] for r in vont}
    dataset_ids = {
        r["canonical_variable_id"]: r["candidate_dataset_ids"]
        for r in vont
        if (r["candidate_dataset_ids"] or "[]") != "[]"
    }
    unit_conversions = {
        r["canonical_variable_id"]: json.loads(r["unit_conversions"] or "{}")
        for r in vont
        if (r["unit_conversions"] or "{}") != "{}"
    }

    corpus: dict[str, int] = {}
    for r in srch:
        if r["nbs_id"] == nbs_id and r["suitability_family_id"]:
            corpus[r["suitability_family_id"]] = corpus.get(
                r["suitability_family_id"], 0
            ) + int(r["n_included"] or 0)

    units = [
        u for u in load_units(REG / "EV_evidence_register.json") if u.nbs_id == nbs_id
    ]
    families = sorted(
        {u.suitability_family_id for u in units if u.suitability_family_id}
    )

    out: dict[str, FamilyResult] = {}
    for family in families:
        fam_units = [u for u in units if u.suitability_family_id == family]
        out[family] = synthesise_family(
            fam_units,
            tiers,
            family=family,
            corpus_n=corpus.get(family, len(fam_units)),
            group_map=group_map,
            canonical_units=canonical_units,
            dataset_ids=dataset_ids,
            categories=categories,
            unit_conversions=unit_conversions,
            floor_pct=20.0,
            allow_crop_scope=family.endswith("shaded_perennial_crop"),
        )
    return out


def write_recipe(
    nbs_id: str, results: dict[str, FamilyResult], vont_rows: list[dict[str, str]]
) -> None:
    recipe_dir = ROOT / "schema" / "recipes" / nbs_id
    ds_by_var = {
        r["canonical_variable_id"]: _first_dataset(r["candidate_dataset_ids"])
        for r in vont_rows
    }

    csv_rows: list[dict[str, object]] = []
    for family, res in results.items():
        save_family(res, recipe_dir / f"T4_{family}.json")
        n_rows = len(res.rows) or 1
        for row in res.rows:
            csv_rows.append(
                {
                    "mapping_id": row["mapping_id"],
                    "nbs_id": nbs_id,
                    "dataset_id": ds_by_var.get(row["variable"], ""),
                    "suitability_dimension": row["suitability_dimension"],
                    "relationship_type": row["relationship_type"],
                    "relationship_params": json.dumps(row["relationship_params"]),
                    "uncertainty_pct": row.get("uncertainty_pct", ""),
                    "context_overrides": json.dumps(row.get("context_overrides") or []),
                    "is_scenario_candidate": "false",
                    "scenario_label": "",
                    "scenario_description": "",
                    "has_future_projection": "false",
                    "baseline_dataset_id": "",
                    "future_dataset_ids": "",
                    # equal split across the family's variables until the MCDA weighting pass runs
                    "weight_default": round(1.0 / n_rows, 4),
                    "weight_adjustable": "true",
                    "justification": row.get("justification", ""),
                    "variable": row["variable"],
                    "suitability_family_id": family,
                    "evidence_ids": json.dumps(row.get("evidence_ids") or []),
                    "n_sources": row.get("n_sources", ""),
                    "corpus_n": row.get("corpus_n", ""),
                    "paper_support_pct": row.get("paper_support_pct", ""),
                }
            )

    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=T4_FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(csv_rows)
    (recipe_dir / "T4_suitability_mappings.csv").write_bytes(
        buf.getvalue().encode("utf-8")
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("nbs_id", help="e.g. riparian_buffer")
    ap.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    args = ap.parse_args(argv)

    results = synthesise(args.nbs_id)
    if not results:
        print(f"no evidence units for {args.nbs_id!r}")
        return 1

    for family, res in results.items():
        print(f"\n{family}  corpus_n={res.corpus_n}  rows={len(res.rows)}")
        for row in res.rows:
            print(
                f"  {row['variable']:26s} {json.dumps(row['relationship_params']):44s} "
                f"support={row.get('paper_support_pct', 0)}%  n={row.get('n_sources')}"
            )
        for variable, rep in res.reports.items():
            for ev_id, why in rep.dropped:
                if "unit" in why:
                    print(f"  UNIT-REFUSED {variable}: {ev_id} - {why}")
        for sel in res.selection:
            if sel.decision != "include":
                print(
                    f"  {sel.decision:20s} {sel.variable:26s} {sel.support_pct}%  {sel.note}"
                )

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    write_recipe(args.nbs_id, results, _rd(REG / "VONT_variable_ontology.csv"))
    print(
        f"\nwrote schema/recipes/{args.nbs_id}/T4_*.json + T4_suitability_mappings.csv"
    )
    print("now run: python3 src/nbs_ruralscan/schema_tools/generate.py schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
