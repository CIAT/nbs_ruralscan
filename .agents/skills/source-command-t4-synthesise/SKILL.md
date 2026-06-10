---
name: "source-command-t4-synthesise"
description: "Synthesise a suitability family's evidence units into enriched T4 rows + a selection table (T4 method section 6)"
---

# source-command-t4-synthesise

Use this skill when the user asks to run the migrated source command `t4-synthesise`.

## Command Template

Run T4 synthesis for one suitability family (methodology/T4_generation_method.md section 6). Ask for the
family if missing; run /extract-evidence first if units do not exist.

Workflow:
1. Gather: the family's evidence units; tiers {source_id: high|medium|low} from the Source Register
   (looked up, never read off the unit); from the Variable Ontology group_map, canonical_units,
   dataset_ids; corpus_n (papers screened); optional ml_important.
2. Run the engine (do not re-judge thresholds by hand):
     from nbs_ruralscan.recipe import synthesise_family, save_family
     res = synthesise_family(units, tiers, family=family, corpus_n=corpus_n, group_map=group_map,
         canonical_units=canonical_units, dataset_ids=dataset_ids, ml_important=ml_important,
         floor_pct=20.0, allow_crop_scope=family.endswith("shaded_perennial_crop"))
     save_family(res, "schema/recipes/<nbs_id>/T4_<family>.json")
3. Report: T4 rows (params, uncertainty_pct, paper_support_pct, overrides); the selection table --
   surface every review_low_support / include_ml_override for a recorded decision; group-level support
   (hierarchy roll-up) + coverage gaps; per-variable dropped/collapsed.

Rules: do not hand-edit thresholds (fix the evidence unit and re-run). Soft floor, not a hard cut.
Species/crop claims never set a practice row (except F5). Uncertainty only widens. Every row cites
its evidence_ids.

Reference: methodology/examples/t4_slice_agroforestry_F1_slope.md.
