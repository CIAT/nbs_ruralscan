#!/usr/bin/env python3
"""Synthesise an NbS recipe's T4 slice from the evidence register.

Runs `synthesise_family` for every suitability family of one NbS (the t4-synthesise skill,
T4 method section 6) and writes both artefacts the recipe needs:

* `schema/recipes/<nbs_id>/T4_<family>.json` — the enriched per-family rows + provenance
* `schema/recipes/<nbs_id>/T4_suitability_mappings.csv` — the recipe table the dashboard
  and the pipeline read (regenerate its JSON with schema_tools/generate.py afterwards)

Inputs are read from the registers, never hand-passed: tiers from `SRC.benchmark_tier`,
grouping/units/datasets/conversions from `VONT`, grey-discount categories from
`SRC.source_category`. Screened-corpus membership must be supplied explicitly; aggregate
SRCH counts cannot establish a deduplicated denominator.

Usage:
    python3 scripts/synthesise-recipe.py riparian_buffer
    python3 scripts/synthesise-recipe.py riparian_buffer --dry-run
"""

from __future__ import annotations

import argparse
import csv
import io
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from nbs_ruralscan.recipe.evidence import EvidenceUnit
from nbs_ruralscan.schema_tools.generate import _csv_to_rows
from nbs_ruralscan.recipe.family import (
    FamilyResult,
    save_family,
    synthesise_family,
)

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


def synthesise(
    nbs_id: str,
    *,
    approved_only: bool = True,
    screened_sources: dict[str, set[str]] | None = None,
) -> dict[str, FamilyResult]:
    src, vont = (
        _rd(REG / n)
        for n in (
            "SRC_source_register.csv",
            "VONT_variable_ontology.csv",
        )
    )
    tiers = {
        r["source_id"]: (r["benchmark_tier"] or "medium").strip().lower() for r in src
    }
    categories = {r["source_id"]: r["source_category"] for r in src}
    group_map = {r["canonical_variable_id"]: r["group_id"] for r in vont}
    canonical_units = {r["canonical_variable_id"]: r["canonical_unit"] for r in vont}
    dataset_ids = {
        r["canonical_variable_id"]: _first_dataset(r["candidate_dataset_ids"])
        for r in vont
        if (r["candidate_dataset_ids"] or "[]") != "[]"
    }
    unit_conversions = {
        r["canonical_variable_id"]: json.loads(r["unit_conversions"] or "{}")
        for r in vont
        if (r["unit_conversions"] or "{}") != "{}"
    }

    # SRCH stores overlapping search totals, not screened-source membership.
    # Unknown is explicit; never substitute active/extracted sources or included counts.
    screened_sources = screened_sources or {}
    known = {r["source_id"] for r in src}
    for family, source_ids in screened_sources.items():
        if source_ids - known:
            raise ValueError(
                f"Unknown screened source IDs for {family}: {sorted(source_ids - known)}"
            )

    policies = _rd(ROOT / "schema" / "lookups" / "crop_scope_policy.csv")
    units = [
        EvidenceUnit(
            **{
                k: value
                for k, value in row.items()
                if k in EvidenceUnit.__dataclass_fields__
            }
        )
        for row in _csv_to_rows(REG / "EV_evidence_register.csv")
        if row["nbs_id"] == nbs_id
    ]
    families = sorted(
        {u.suitability_family_id for u in units if u.suitability_family_id}
    )

    out: dict[str, FamilyResult] = {}
    for family in families:
        fam_units = [u for u in units if u.suitability_family_id == family]
        policy = next(
            (
                r
                for r in policies
                if r["nbs_id"] == nbs_id and r["suitability_family_id"] == family
            ),
            None,
        )
        if policy is None:
            policy = next(
                (
                    r
                    for r in policies
                    if r["nbs_id"] == nbs_id and not r["suitability_family_id"]
                ),
                {},
            )
        out[family] = synthesise_family(
            fam_units,
            tiers,
            family=family,
            corpus_n=screened_sources.get(family),
            group_map=group_map,
            canonical_units=canonical_units,
            dataset_ids=dataset_ids,
            categories=categories,
            unit_conversions=unit_conversions,
            floor_pct=20.0,
            allow_crop_scope=policy.get("allow_crop_scope", "").lower() == "true",
            approved_only=approved_only,
        )
        out[family].support_basis = (
            "explicit_screened_source_membership"
            if family in screened_sources
            else "unknown_screened_source_membership"
        )
    return out


# Fields a person sets on purpose (model design, not evidence synthesis). A re-run must
# never wipe them: they are carried onto the regenerated row for the same variable.
DESIGN_FIELDS = (
    "is_scenario_candidate",
    "scenario_label",
    "scenario_description",
    "has_future_projection",
    "baseline_dataset_id",
    "future_dataset_ids",
)


def _is_synthesised(row: dict[str, str]) -> bool:
    """A row the engine wrote (as opposed to a hand-set design row: an eligibility
    filter, a hard exclusion mask, an M2b scenario lever)."""
    return (row.get("justification") or "").startswith("Reconciled from")


def _existing_rows(recipe_dir: Path) -> list[dict[str, str]]:
    f = recipe_dir / "T4_suitability_mappings.csv"
    if not f.exists():
        return []
    return list(csv.DictReader(io.StringIO(f.read_bytes().decode("utf-8"), newline="")))


def write_recipe(
    nbs_id: str,
    results: dict[str, FamilyResult],
    vont_rows: list[dict[str, str]],
    *,
    output_dir: Path | None = None,
) -> None:
    source_dir = ROOT / "schema" / "recipes" / nbs_id
    recipe_dir = output_dir or source_dir
    recipe_dir.mkdir(parents=True, exist_ok=True)
    existing = _existing_rows(source_dir)
    design_by_var: dict[tuple[str, str], dict[str, str]] = {}
    for r in existing:
        if any((r.get(k) or "") not in ("", "false") for k in DESIGN_FIELDS):
            design_by_var.setdefault((r["suitability_family_id"], r["variable"]), r)
    ds_by_var = {
        r["canonical_variable_id"]: _first_dataset(r["candidate_dataset_ids"])
        for r in vont_rows
    }

    # Authored, evidence-linked eligibility gates are non-compensatory configuration.
    # Numeric synthesis cannot overwrite a family-specific dataset crosswalk.
    gates = {
        (r["suitability_family_id"], r["variable"]): r
        for r in existing
        if r.get("relationship_type") == "ranked_classes"
        and json.loads(r.get("relationship_params") or "{}").get("mapping_role")
        == "eligibility_gate"
    }
    csv_rows: list[dict[str, object]] = []
    for family, res in results.items():
        save_family(res, recipe_dir / f"T4_{family}.json")
        n_rows = len(res.rows) or 1
        for row in res.rows:
            if (family, row["variable"]) in gates:
                continue
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
            carried = design_by_var.get((family, row["variable"]))
            if carried:
                csv_rows[-1].update({k: carried.get(k, "") for k in DESIGN_FIELDS})

    # keep hand-set design rows the engine does not produce (eligibility filters, hard
    # masks, M2b scenario levers); stale synthesised rows are replaced, never kept
    produced = {(str(r["suitability_family_id"]), str(r["variable"])) for r in csv_rows}
    kept = [
        r
        for r in existing
        if not _is_synthesised(r)
        and (r.get("suitability_family_id", ""), r["variable"]) not in produced
    ]
    for row in kept:
        preserved = {k: row.get(k, "") for k in T4_FIELDS}
        # Retained design/crosswalk rows have no verified screened-source calculation.
        # Do not perpetuate historical search-total percentages across regeneration.
        preserved["corpus_n"] = ""
        preserved["paper_support_pct"] = ""
        csv_rows.append(preserved)

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
    review = ap.add_mutually_exclusive_group()
    review.add_argument(
        "--approved-only",
        action="store_true",
        default=True,
        help="exclude unresolved review records (publication default)",
    )
    review.add_argument(
        "--include-unreviewed",
        action="store_true",
        help="diagnostic draft only; requires isolated --output-dir or --dry-run",
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        help="write isolated trial outputs; preserve live recipe",
    )
    ap.add_argument(
        "--report",
        type=Path,
        help="write complete evidence-disposition and crop-lane report",
    )
    ap.add_argument(
        "--screened-corpus",
        type=Path,
        help="JSON: {families: {family: {source_ids: [...], provenance: ..., complete: true}}}",
    )
    ap.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    args = ap.parse_args(argv)
    if args.include_unreviewed:
        live = (ROOT / "schema" / "recipes" / args.nbs_id).resolve()
        isolated = args.output_dir is not None and args.output_dir.resolve() != live
        if not args.dry_run and not isolated:
            ap.error(
                "--include-unreviewed cannot write the live recipe; use isolated --output-dir or --dry-run"
            )
        if args.report is not None and args.report.resolve().is_relative_to(live):
            ap.error("unreviewed diagnostic reports must stay outside the live recipe")
        args.approved_only = False

    screened_sources = {}
    if args.screened_corpus:
        manifest = json.loads(args.screened_corpus.read_text())
        for family, entry in manifest["families"].items():
            if entry.get("complete") is not True or not entry.get("provenance"):
                raise ValueError(
                    f"Screened corpus must be complete and provenanced: {family}"
                )
            screened_sources[family] = set(entry["source_ids"])
    results = synthesise(
        args.nbs_id, approved_only=args.approved_only, screened_sources=screened_sources
    )
    if not results:
        print(f"no evidence units for {args.nbs_id!r}")
        return 1

    for family, res in results.items():
        print(f"\n{family}  corpus_n={res.corpus_n}  rows={len(res.rows)}")
        print(f"  support basis: {res.support_basis}")
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

    report_path = args.report
    if report_path is None and not args.dry_run:
        report_path = (
            args.output_dir or ROOT / "schema" / "recipes" / args.nbs_id
        ) / "T4_synthesis_report.json"
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(
                {
                    "status": "draft_requires_evidence_and_applicability_review",
                    "input_sha256": {
                        str(path.relative_to(ROOT)): hashlib.sha256(
                            path.read_bytes()
                        ).hexdigest()
                        for path in [
                            *REG.glob("*.csv"),
                            ROOT / "schema/lookups/crop_scope_policy.csv",
                        ]
                    },
                    "screened_corpus_manifest": {
                        "path": str(args.screened_corpus),
                        "sha256": hashlib.sha256(
                            args.screened_corpus.read_bytes()
                        ).hexdigest(),
                    }
                    if args.screened_corpus
                    else None,
                    "review_mode": "approved_only"
                    if args.approved_only
                    else "all_active_draft",
                    "families": {f: asdict(r) for f, r in results.items()},
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
    if args.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    write_recipe(
        args.nbs_id,
        results,
        _rd(REG / "VONT_variable_ontology.csv"),
        output_dir=args.output_dir,
    )
    print(
        f"\nwrote {args.output_dir or ROOT / 'schema' / 'recipes' / args.nbs_id}/T4_*.json + T4_suitability_mappings.csv"
    )
    if not args.output_dir:
        print("now run: python3 src/nbs_ruralscan/schema_tools/generate.py schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
