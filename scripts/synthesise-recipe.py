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
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re

from nbs_ruralscan.recipe import t4_build
from nbs_ruralscan.recipe.t4_build import T4BuildInputs

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "schema/registers"
# Preserve the historical script helpers used by existing callers.
_rd = t4_build._rd
_is_synthesised = t4_build._is_synthesised
DESIGN_FIELDS = t4_build.DESIGN_FIELDS
T4_FIELDS = t4_build.T4_FIELDS


def _existing_rows(recipe_dir):
    return t4_build._existing_rows(recipe_dir / "T4_suitability_mappings.csv")


def synthesise(nbs_id, *, inputs=None, approved_only=True, screened_sources=None):
    return t4_build.synthesise(
        nbs_id,
        inputs=inputs or T4BuildInputs.from_root(ROOT, nbs_id),
        approved_only=approved_only,
        screened_sources=screened_sources,
    )


def write_recipe(
    nbs_id,
    results,
    vont_rows,
    *,
    inputs=None,
    output_dir=None,
    supersede_holds_from=None,
):
    inputs = inputs or T4BuildInputs.from_root(ROOT, nbs_id)
    return t4_build.write_recipe(
        nbs_id,
        results,
        vont_rows,
        inputs=inputs,
        output_dir=output_dir or inputs.audited_recipe.parent,
        supersede_holds_from=supersede_holds_from,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("nbs_id", help="e.g. riparian_buffer")
    ap.add_argument(
        "--source-root",
        type=Path,
        default=ROOT,
        help="read a CIAT-layout input snapshot; independent of working directory",
    )
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
    ap.add_argument(
        "--supersede-holds-from",
        metavar="SHA256",
        help="Apply a reviewed hold change against this exact accepted mapping SHA-256, in place",
    )
    args = ap.parse_args(argv)
    if not re.fullmatch(r"[a-z][a-z0-9_]*", args.nbs_id):
        ap.error("Invalid NbS identifier")
    source_root = args.source_root.resolve()
    inputs = T4BuildInputs.from_root(source_root, args.nbs_id)
    if args.include_unreviewed:

        def isolated_path(path):
            resolved = path.resolve()
            return all(
                (root not in resolved.parents and resolved != root)
                or (root / "pipeline/staging").resolve() in resolved.parents
                for root in {
                    ROOT.resolve(),
                    source_root,
                    Path(t4_build.__file__).resolve().parents[3],
                }
            )

        isolated = args.output_dir is not None and isolated_path(args.output_dir)
        if not args.dry_run and not isolated:
            ap.error(
                "--include-unreviewed cannot write authoritative inputs or published docs; use isolated --output-dir or --dry-run"
            )
        if args.report is not None and not isolated_path(args.report):
            ap.error(
                "unreviewed diagnostic reports must stay outside authoritative inputs and published docs"
            )
        if args.report is not None and args.report.exists() and not args.dry_run:
            ap.error(
                "unreviewed report already exists; choose a new diagnostic filename"
            )
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
        args.nbs_id,
        inputs=inputs,
        approved_only=args.approved_only,
        screened_sources=screened_sources,
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

    recipe_dir = args.output_dir or inputs.audited_recipe.parent
    report_path = args.report or recipe_dir / "T4_synthesis_report.json"
    if not args.dry_run:
        reserved = (
            *inputs.paths(),
            recipe_dir / "T4_suitability_mappings.csv",
            *(recipe_dir / f"T4_{family}.json" for family in results),
        )
        if (
            report_path.is_symlink()
            or (report_path.exists() and report_path.stat().st_nlink != 1)
            or report_path.resolve() in {p.resolve() for p in reserved}
        ):
            ap.error(
                "A T4 report cannot use a linked destination or overwrite an input or compiled mapping"
            )
        write_recipe(
            args.nbs_id,
            results,
            _rd(inputs.ontology),
            inputs=inputs,
            output_dir=args.output_dir,
            supersede_holds_from=args.supersede_holds_from,
        )

    if not args.dry_run:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(
                {
                    "status": (
                        "reviewed_compilation_with_explicit_gaps"
                        if args.approved_only
                        else "draft_requires_evidence_and_applicability_review"
                    ),
                    "input_sha256": {
                        str(path.relative_to(source_root)): hashlib.sha256(
                            path.read_bytes()
                        ).hexdigest()
                        for path in [
                            *(source_root / "schema/registers").glob("*.csv"),
                            inputs.crop_scope_policy,
                            inputs.numeric_policy,
                            *inputs.authored_paths(),
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
    print(
        f"\nwrote {args.output_dir or inputs.audited_recipe.parent}/T4_*.json + T4_suitability_mappings.csv"
    )
    if not args.output_dir:
        print("now run: python3 src/nbs_ruralscan/schema_tools/generate.py schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
