---
name: "source-command-t4-synthesise"
description: "Compile reviewed suitability evidence into T4 CSV and traceable developer outputs for a declared NbS."
---

# T4 synthesis

Read `AGENTS.md`, `methodology/T4_generation_method.md` and
`.agents/skills/extraction_contracts/T4_review_contract.md`. Use the current FAM IDs,
not labels or a family inferred from the task name. Preserve independent species/crop,
operational, observed-presence and unresolved-applicability lanes.

## Reproducible workflow

1. Confirm the authorised NbS and target families against FAM. Start from the existing
   evidence corpus and source-table inventory. Missing evidence is an explicit gap;
   this synthesis command does not authorise a new discovery/extraction sweep.
2. Use the registered compiler, which reads CSV registers, crop-scope policy, numeric
   compilation policy, source tiers, units and conversions:

   ```sh
   PYTHONPATH=src python scripts/synthesise-recipe.py <nbs_id> --dry-run
   PYTHONPATH=src python scripts/synthesise-recipe.py <nbs_id> \
     --output-dir <isolated-trial-directory> --report <trial-report.json>
   ```

   Reviewed evidence is the default. Unreviewed diagnostics require
   `--include-unreviewed` with an isolated output directory or `--dry-run`.
   They never become a published recipe or human approval.
3. Inspect the complete disposition report: omitted/unassigned variables, crop lanes,
   unsupported units, conflicting class boundaries, lineage and calibration holds.
   Preserve categorical gates and deliberate design fields. Do not infer a numeric
   curve from direction, map extrema, observations or an importance weight.
4. Review differences against the current recipe. Resolve genuine ambiguities with
   Pete before changing applicability, pooled functions, missing tails, masks or weights.
   Compilation is not policy approval. Preserve existing approved mappings and record
   any superseding decision explicitly.
5. Only after that review, regenerate the live CSV through the compiler and run:

   ```sh
   PYTHONPATH=src python scripts/synthesise-recipe.py <nbs_id>
   python src/nbs_ruralscan/schema_tools/generate.py schema
   python src/nbs_ruralscan/schema_tools/structure.py schema
   PYTHONPATH=src python -m nbs_ruralscan.schema_tools.t4_coverage
   ```

   CSV is authoritative. Never use a standalone `save_family()` JSON output to bypass
   the CSV/compiler path or edit generated analytical JSON by hand.
6. Export a new developer package only after the audited recipe reproduces:

   ```sh
   PYTHONPATH=src python scripts/build-t4-developer.py --nbs <nbs_id> --output <new-package-directory>
   ```

   Target country (`--country`) and study-country filters (`--evidence-country`) have
   different meanings. Neither approves ecological transfer. No recipe inherits
   agroforestry's selected functions, weights, masks or handoff instructions.

## Counts and decisions

Report variable use, direction and calibrated response contributions separately,
with source/lineage deduplication and review status. A screened-corpus denominator
requires explicit complete membership with provenance (`--screened-corpus`); never
substitute overlapping SRCH counts or only extracted sources. Unknown stays unknown.
Pete approved raw n/N as the headline on 2026-10-28: `paper_support_pct` now follows
that convention. The report shows `quality_weighted_pct` separately only when complete
screened membership and quality tiers are known. Do not infer unseen source weights.
Historical exports may use the old weighted percentage; label their version. See
`methodology/decisions/2026-10-28_t4_support_reporting.md`. Source importance, source-quality
weights and runtime MCDA weights remain distinct.

Crop admission comes from `schema/lookups/crop_scope_policy.csv`; never hardcode an
F5 suffix or extend crop permission to species envelopes. The low-support floor is
advisory, not an automatic exclusion. All compiled values retain evidence provenance.
