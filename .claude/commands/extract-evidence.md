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

Hard rules: quote+page mandatory; null when the source is silent (no inference). **PICOS — the NbS
practice must be evidenced IN the source before you tag it.** Only set `nbs_id` / `suitability_family_id`
if the practice (or its sub-practice) is explicitly present in the passage/source — never infer it from a
demo dataset, worked example, file/paper title, or the sweep's current focus. A generic method demoed on
agroforestry is not agroforestry evidence; a coffee case study does not make a generic variable a coffee
claim. If the practice isn't stated, leave it `cross`/agnostic or skip the row. (Same discipline as
`claim_scope`: species ≠ practice.) Tag use_role
(structural_suitability=T4 | climate_risk=T2 | priority_need=T5 | nbs_effect=T6 | dataset=T1);
evidence_type (only literature_relationship/expert carry shape params); claim_basis; claim_scope
(species/crop claims need taxon and must NOT define a practice row). Set lineage_of when a value is
cited from another source. Capture exclusion/failure thresholds too. No silent unit harmonisation.

**Tool / codebase sources (default behaviour):** a tool is a source — interrogate its **actual code/scripts**, not just the README/landing/abstract. Cache the relevant source file(s); extract hardcoded thresholds / default weights / criteria / exclusion rules as EV with `locator_type=file_line` + `commit_sha` + `locator="path:Lstart-Lend"` (the dashboard deep-links to the lines). `claim_basis=expert_assertion` (tool design choice). Ignore species-specific / off-scope files (`claim_scope`). Skip data-driven engines that hardcode nothing.

**Defect catalogue (from QA review — the recurring off-scope/mis-route mistakes; off_scope is still the #1 defect at ~84%):**
- **Enabling-environment ≠ T4 suitability.** `market_access` / `tenure_security` / `extension_governance` / `finance_credit_access` / `labour_availability` are **soft operational constraints** → they belong to **M2b project-risk (Stream B) / scenario levers / M6 next-steps**, NOT the T4 opportunity surface (AGENTS "hard vs soft operational constraints" lock). Don't tag them `use_role=structural_suitability`. If unsure, leave it for review — don't default to T4.
- **Results/output description ≠ a rule.** "regions were classified as suitable", "the map shows priority zones", "potential areas for agroforestry" describe a *produced output*, not a per-pixel suitability criterion. Off-scope.
- **Trend/distribution description ≠ suitability.** "tree cover increased over the past decades", "biomass distribution", global/temporal trends. Off-scope (and tree-cover ≠ agroforestry).
- **Speculation/assumption ≠ evidence.** "we assume", "may still deter", "could potentially", "is a reflection", "hand-wavy assumed causation" — hedged/speculative claims that were not measured or used in the analysis. Skip.
- **Variable-presence vote ≠ usable threshold.** A paper confirming a variable matters (a vote for `n_sources`) is not the same as a usable classification threshold — capture which one it is; don't manufacture a threshold from a mention.
- **Figure-only evidence** — if the value lives in a figure, flag `needs_ocr`/figure-read and ask the human; don't guess.
`check_scope.py` now flags `results_description` / `trend_description` / `speculation` (advisory) in addition to study-site / carbon-biomass / problem-intro.

Reference: methodology/examples/t4_slice_agroforestry_F1_slope.md (the gold standard to reproduce).
