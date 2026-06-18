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
     from nbs_ruralscan.recipe.evidence import already_extracted
     # Check for each variable in the set
     existing = already_extracted(sid, variable)
     if existing:
       print(f"SKIP {sid} × {variable} — already extracted: {existing}")
       # skip unless the user explicitly says --force / re-extract
   Report skipped pairs so the user knows what was cached.
3. Ingest + retrieve (deterministic):
     from nbs_ruralscan.ingest import build_index, load_index, save_index
     from nbs_ruralscan.recipe.evidence import package_for_extraction, package_for_extraction_multi, EvidenceUnit, validate_units, save_units
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

## Common extraction defects (2026-06 learnings — avoid these)

Quote-verbatim does NOT mean the structured fields are faithful. Two adversarial verify
waves found ~34-51% of numeric units defective. Recurring patterns to avoid:

1. **Smuggled numbers** — every value in `relationship` MUST appear in the SAME quote.
   Do not import discount rates, time horizons, study counts (n), I² heterogeneity,
   table-header units, or cross-row range endpoints from elsewhere in the paper.
   (Deterministically caught by `schema_tools/check_numbers.py`.)
2. **Lowest-rank-class misread as exclusion** — in AHP/land-suitability tables, the
   bottom class (score 1 / "Low") is NOT a hard `abs_min`/`abs_max`. Only encode an
   absolute limit when the text says excluded/unsuitable, not merely low-scoring.
3. **Unit-from-quote-only** — if the quoted cell shows "873.60" with the unit in a
   header row not in the quote, do not assert `unit`. Quote the header too, or omit unit.
4. **Proxy ≠ canonical variable** — SOM≠soil_organic_carbon, NDVI≠tree_canopy_cover,
   soil-moisture≠soil_drainage, frost-free-period / LST ≠ mean_annual_temperature. If the
   paper measures a proxy, say so in `raw_name` and pick the closest canonical id with
   `extraction_confidence` lowered — never silently relabel.
5. **Contiguous single-passage quotes only** — never stitch text across passages/pages
   (fails the page-level guardrail).
6. **Family**: general cross-cutting envelope claims → `agroforestry__cross_family`, not a
   default to F1. Family-specific only when the paper's system is that family.
7. **cited_secondary REQUIRES `attribution`** (whose finding) — synthesis de-dups on it.
8. **Section-scope: a T4 quote must be a SUITABILITY claim** (2026-06-18 — 86% of QA drops
   were `off_scope`). Do NOT extract a `structural_suitability` value from a section that is
   not suitability reasoning: study-site / characteristics tables, methods / study-area
   descriptions, carbon·CO2·biomass accounting, or generic intros / problem statements. A
   verbatim number near a variable name is not a threshold if the section isn't analysing
   suitability. (Carbon/biomass IS valid for T6 effects and fuel/biomass for T3 hazard —
   the rule is T4-only.) Record `claim_basis` + `selection_justification`; if you can't say
   why it's a suitability claim, don't extract it. Deterministically triaged by
   `schema_tools/check_scope.py`. **Source-scope:** also confirm the paper is about the NbS
   *practice* — a reforestation / forest-restoration / carbon-only paper is not agroforestry
   suitability; scope-flag it at screening rather than mapping its rows to a family.

The trustworthy gates are CENTRAL: the verbatim+page guardrail (`validate_sources.py`),
`check_numbers.py`, `check_scope.py`, and the adversarial relationship-verify. A subagent's
own self-check is advisory — do not rely on it. After a sweep, the learning loop is only
honest if feedback is incorporated: `learnings.py` tracks `review_log` vs adjustments and
the build flags unprocessed review decisions (run `/sweep-retro` → encode → `learnings.record`).
