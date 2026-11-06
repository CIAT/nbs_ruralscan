#!/usr/bin/env python3
"""Generate an NbS recipe's T3 + T6 tables from the evidence register (cell synthesis).

The `/t3t6-synthesise` skill (methodology/T3_T6_generation_method.md §7; contract
`.agents/skills/_versions/v1.6.0/contracts/T3_T6_synthesis_contract.md`). Runs
`recipe.cell_synthesis.synthesise_cell_with_families` for every cell the XW crosswalk routes
evidence to, and writes:

* `schema/recipes/<nbs_id>/T3_nbs_hazard_farming.csv` — mitigation rows (per hazard ×
  farming_system) + asset-threat rows (per hazard), each as global + scope + family rows
* `schema/recipes/<nbs_id>/T6_nbs_scorecard.csv` — effect rows (per T5 priority)
* `schema/recipes/<nbs_id>/T6E_economic_profile.csv` — the cost / economic-indicator rows
  (same columns as T6; Pete 2026-10-23: cost data feeds the economic profile, not the
  scorecard; cost per tCO2e is feasibility-level and not generated)
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
from pathlib import Path

from nbs_ruralscan.recipe import t3t6_build as build
from nbs_ruralscan.recipe.t3t6_build import T3T6BuildInputs

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"
REG = SCHEMA / "registers"
LOOK = SCHEMA / "lookups"
cs = build.cs
T3_FIELDS, T6_FIELDS, T3_HAZARDS = build.T3_FIELDS, build.T6_FIELDS, build.T3_HAZARDS
synthesise = build.synthesise
_summary = build._summary


def crop_scope_policy(nbs_id, *, inputs=None):
    selected = inputs or T3T6BuildInputs.from_root(ROOT, nbs_id)
    return build.crop_scope_policy(nbs_id, path=selected.crop_policy)


def load_inputs(nbs_id, staging, *, inputs=None):
    return build.load_inputs(
        nbs_id, staging, inputs=inputs or T3T6BuildInputs.from_root(ROOT, nbs_id)
    )


def write_recipe(nbs_id, out, *, dry_run, inputs=None, output_dir=None):
    return build.write_recipe(
        nbs_id,
        out,
        dry_run=dry_run,
        inputs=inputs or T3T6BuildInputs.from_root(ROOT, nbs_id),
        output_dir=output_dir
        if output_dir is not None
        else SCHEMA / "recipes" / nbs_id,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("nbs_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--source-root", type=Path, help="Read an independent input snapshot"
    )
    ap.add_argument(
        "--output-dir", type=Path, help="Write the four candidate recipe files here"
    )
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
    source = (args.source_root or ROOT).resolve()
    inputs = T3T6BuildInputs.from_root(source, args.nbs_id)
    if args.source_root and not args.output_dir and not args.dry_run:
        ap.error(
            "--source-root requires --output-dir for writing; use --dry-run for a preview"
        )
    output = (
        args.output_dir
        if args.output_dir is not None
        else source / "schema/recipes" / args.nbs_id
    )
    if args.output_dir:
        resolved = output.resolve()
        for protected in (source, ROOT.resolve()):
            if (
                resolved == protected
                or resolved.is_relative_to(protected)
                or protected.is_relative_to(resolved)
            ):
                ap.error(
                    "--output-dir must be separate from the input snapshot and compiler checkout"
                )
    inp = load_inputs(args.nbs_id, staging, inputs=inputs)
    out = synthesise(args.nbs_id, inp)
    print(_summary(out))
    used = {u.source_id for u in inp["units"]}
    bad = {k: v for k, v in inp["src_country_unresolved"].items() if k in used}
    if bad:
        print(
            f"SRC.study_country tokens not resolved to ISO3 (dropped from envelopes): {bad}"
        )
    for path in write_recipe(
        args.nbs_id, out, dry_run=args.dry_run, inputs=inputs, output_dir=output
    ):
        print("wrote", path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
