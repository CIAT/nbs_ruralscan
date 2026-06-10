---
name: "source-command-extract-evidence"
description: "Extract Evidence-Register units for one variable x suitability family from the ingested corpus (T4 method)"
---

# source-command-extract-evidence

Use this skill when the user asks to run the migrated source command `extract-evidence`.

## Command Template

Run the T4 evidence-extraction step (methodology/T4_generation_method.md section 5): turn ingested
source passages into atomic, provenance-bearing Evidence-Register units -- never PDF -> threshold.

Inputs: a canonical variable, a suitability family, optionally a source set (ask if missing).

Workflow:
1. Canonical variable(s) + aliases + min_meaningful_resolution_m from the Variable Ontology; the family
   target spec; tiers from the benchmarked CSV (Source Register).
2. **Dedup check** (saves tokens — skip work already done):
     from nbs_ruralscan.evidence import already_extracted
     # Check for each variable in the set
     existing = already_extracted(sid, variable)
     if existing:
       print(f"SKIP {sid} × {variable} — already extracted: {existing}")
       # skip unless the user explicitly says --force / re-extract
   Report skipped pairs so the user knows what was cached.
3. Ingest + retrieve (deterministic):
     from nbs_ruralscan.ingest import build_index, load_index, save_index
     from nbs_ruralscan.evidence import package_for_extraction, package_for_extraction_multi, EvidenceUnit, validate_units, save_units
     idx = load_index(sid) or build_index(pdf, source_id=sid)

     # Single variable extraction:
     bundle = package_for_extraction(idx, "slope", aliases=["terrain slope","gradient"])
     
     # Paper-first multi-variable extraction (saves context tokens by bundling):
     vars_spec = [
         {"variable": "slope", "aliases": ["gradient"]},
         {"variable": "annual_precipitation", "aliases": ["rainfall"]},
     ]
     bundle = package_for_extraction_multi(idx, vars_spec)
     
   Work ONLY from bundle["passages"] (page-stamped). Flag needs_ocr_pages; never guess.
4. Emit one EvidenceUnit per atomic claim. For multi-variable extraction, extract all variables in the same pass.
5. validate_units(units) must return {} before save_units(units, path).
6. Report units, conflicts, anything pending (OCR / figure-only).

Hard rules: quote+page mandatory; null when the source is silent (no inference). Tag use_role
(structural_suitability=T4 | climate_risk=T2 | priority_need=T5 | nbs_effect=T6 | dataset=T1);
evidence_type (only literature_relationship/expert carry shape params); claim_basis; claim_scope
(species/crop claims need taxon and must NOT define a practice row). Set lineage_of when a value is
cited from another source. Capture exclusion/failure thresholds too. No silent unit harmonisation.

When extracting evidence supporting tables other than T4, consult the specific extraction contracts:
- For T3 (mitigation matrix / M2 / M2b): [.agents/skills/extraction_contracts/T3_contract.md](file:///Users/pstewarda/Documents/rprojects/nbs_ruralscan/.agents/skills/extraction_contracts/T3_contract.md)
- For T5 (opportunity variables / MCDA): [.agents/skills/extraction_contracts/T5_contract.md](file:///Users/pstewarda/Documents/rprojects/nbs_ruralscan/.agents/skills/extraction_contracts/T5_contract.md)
- For T6 (scorecard / cost-effectiveness): [.agents/skills/extraction_contracts/T6_contract.md](file:///Users/pstewarda/Documents/rprojects/nbs_ruralscan/.agents/skills/extraction_contracts/T6_contract.md)

Reference: methodology/examples/t4_slice_agroforestry_F1_slope.md (the gold standard to reproduce).


