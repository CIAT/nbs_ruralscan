---
description: Extract Evidence-Register units for one variable x suitability family from the ingested corpus (T4 method)
---

Run the T4 evidence-extraction step (methodology/T4_generation_method.md section 5): turn ingested
source passages into atomic, provenance-bearing Evidence-Register units -- never PDF -> threshold.

Inputs: a canonical variable, a suitability family, optionally a source set (ask if missing).

Workflow:
1. Canonical variable + aliases + min_meaningful_resolution_m from the Variable Ontology; the family
   target spec; tiers from the benchmarked CSV (Source Register).
2. Ingest + retrieve (deterministic):
     from nbs_ruralscan.ingest import build_index, load_index, save_index
     from nbs_ruralscan.recipe.evidence import package_for_extraction, EvidenceUnit, validate_units, save_units
     idx = load_index(sid) or build_index(pdf, source_id=sid)
     bundle = package_for_extraction(idx, "slope", aliases=["terrain slope","gradient","slope %"])
   Work ONLY from bundle["passages"] (page-stamped). Flag needs_ocr_pages; never guess.
3. Emit one EvidenceUnit per atomic claim.
4. validate_units(units) must return {} before save_units(units, path).
5. Report units, conflicts, anything pending (OCR / figure-only).

Hard rules: quote+page mandatory; null when the source is silent (no inference). Tag use_role
(structural_suitability=T4 | climate_risk=T2 | priority_need=T5 | nbs_effect=T6 | dataset=T1);
evidence_type (only literature_relationship/expert carry shape params); claim_basis; claim_scope
(species/crop claims need taxon and must NOT define a practice row). Set lineage_of when a value is
cited from another source. Capture exclusion/failure thresholds too. No silent unit harmonisation.

Reference: methodology/examples/t4_slice_agroforestry_F1_slope.md (the gold standard to reproduce).
