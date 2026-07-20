---
name: "source-command-extract-evidence"
description: "Extract Evidence-Register units for one variable x suitability family from the ingested corpus (T4 method)"
version: "v1.4.1"
---

<!-- ruleset version v1.4.1 — log: methodology/RULESET_VERSIONS.md · snapshots: .agents/skills/_versions/.
     Bump + snapshot on any change to the screening funnel, defect catalogue, or discovery protocol.
     Stamp the version on SRCH.ruleset_version + EV.ruleset_version. -->


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
9. **Quote context — never an isolated cell** (2026-06-18 — ~11% of units were <=10 words).
   The quote must carry the full threshold SENTENCE plus the table caption/header that
   defines the variable & unit. A bare cell ("30-40 pt", "873.60", "5.1-8.5") can't prove
   it's a suitability claim, what the number means, or species-vs-practice scope — and is
   where table-garble / smuggled-unit / species-envelope defects hide. If the value is a
   per-species table row, it's a species envelope (`claim_scope=species`), not a practice
   row. Triaged by `schema_tools/check_quote.py`.
10. **Soft enabling-environment ≠ T4 structural suitability → `wrong_table`** (2026-06-23,
    RE-RATIFIED, reverses 2026-06-22). `market_access`/`accessibility_travel_time` ·
    `market_value_chain` · `tenure_security` · `extension_governance` ·
    `finance_credit_access` · `labour_availability` · `distance_to_road` are **soft,
    investment-addressable** factors → they belong to the **M2b Stream-B operational-risk
    filter + Module-6 next-steps, NOT T4**. Do NOT emit them as `use_role=structural_suitability`.
    Only HARD legal masks (protected areas, water bodies, urban) stay in T4. (~13 such rows
    flagged in 2026-06-23 QA.) Extract with **`use_role=operational_risk`** (the M2b enum
    member, 2026-06-23) — synthesised into a flagged `operational_constraint` recipe section,
    kept OUT of the T4 suitability surface (var_support/selection use structural only).
11. **Wrong practice ≠ agroforestry → `wrong_practice`** (PICOS, deterministically caught by
    `schema_tools/check_picos.py`). Reforestation, afforestation, pure forestry/plantation,
    "climate-smart agriculture"/CSA umbrella, generic forest restoration are NOT agroforestry.
    The practice must be EVIDENCED in the source — don't borrow the AF tag from the sweep's
    focus, a demo dataset, or a file title. No AF/silvo signal in the source → blank `nbs_id`.
12. **Capture the relationship — don't drop the curve → `relationship_missed`** (2026-06-23).
    When a source gives a suitability *relationship* (membership curve, monotonic decline with
    distance, "very high = fine texture, high = fine-to-coarse", a min/opt/max band), that
    directionality IS the evidence — encode it in `relationship`. Capturing the variable name
    but losing the curve is a BIG miss (singh26: distance/precip/MAT/slope/soil-texture/
    soil-drainage relationships all dropped). Read the membership/classification logic.
13. **Speculation ≠ evidence → `speculative_evidence`** ("may still deter", "could
    potentially", "we assume", "is a reflection", hand-wavy assumed causation — not measured
    or used in the analysis). **Values that give no usable rule → `unusable_value`**
    (2026-07, was `uninterpretable_weight`): a bare "5" is uninterpretable ("5 out of what?") —
    the quote/`attribution` must carry the scale (e.g. "0–10", "region-specific HUC default") and
    what is weighted; land_cover with no class list (which classes in/out) is likewise
    unreviewable (deterministically flagged by `check_scope.py` `land_cover_no_classes`). **No caption/context, or a
    failed table screengrab → `insufficient_context`**: flag for the human, don't guess.
14. **Constrained-AOI framing → `constrained_aoi`** (2026-06-24, general principle). A source
    that scopes the NbS onto a *subset* of land **understates where the NbS is actually
    feasible** and misrepresents the opportunity-space extent. Classic case: **land-capability
    / land-use-capacity classifications** (USDA-LCC-style, e.g. INAB Guatemala) that assign
    agroforestry as a **residual / "marginal land"** bucket — what's left after prime
    agriculture and protection forest. Agroforestry is *also* feasible on good land, so the
    source's thresholds describe "where it was *allocated*", not "where it *can go*". This is a
    FRAMING bias of an otherwise on-topic source (distinct from `off_scope`, which is the wrong
    section, and `wrong_practice`, which is the wrong NbS). **Down-weight; NEVER use such a
    source to set the AOI / opportunity-space extent or a global threshold** — at most a
    qualitative, region-flagged vote (`claim_basis=expert_assertion`). Watch for it in any
    land-allocation / capability / zoning scheme.
15. **Species-specific evidence → TAG + KEEP, never drop → `species_envelope`** (2026-07). A
    per-species / per-cultivar claim is real evidence — it is NOT deleted, it is **routed**. Set
    **`claim_scope=species_specific`** (or `crop_specific`) **+ a `taxon`** (e.g. `Faidherbia
    albida`); `synthesis.py` then keeps it OUT of the practice-level T4 suitability surface but
    RETAINS it in the register for a future species-level layer. **crop vs species (2026-07):
    `crop_specific` = a CULTIVATED cash/food crop** (coffee, cocoa, mulberry, banana, citrus,
    groundnut, cereals, cultivated food trees e.g. breadfruit/Tahitian-chestnut/tropical-almond);
    **`species_specific` = a tree grown for timber/service/fodder OR a wild-harvested tree even
    if it fruits** (baobab/Adansonia, sandalwood/Santalum, Faidherbia, merbau). The
    product + cultivation decide, NOT tree-vs-not. The defect is the **mis-tag**:
    leaving a species claim as `claim_scope=practice_technology`, so it leaks into practice
    suitability (12 of 29 July `species_envelope` drops were this). **The article title /
    citation (and abstract, where available) is itself a signal** — a source titled for one
    species is likely species-specific throughout; scope-flag it at screening. On QA, the fix
    for such a row is to **retag (claim_scope + taxon) and KEEP — reviewers must not drop it.**
    Deterministically triaged by `schema_tools/check_species.py` (quote/citation names a taxon
    but claim_scope=practice_technology).
16. **A single study's SITE CONTEXT is not a suitability RULE → `site_context`** (2026-07; the
    #1 recurring reviewer complaint — sharpens #8 from "wrong section" to "wrong *kind of
    claim*"). A `structural_suitability` unit must encode a **rule that GENERALISES** — a
    threshold / range / gradient / requirement / comparison across suitable-vs-unsuitable land
    ("FMNR needs living stumps"; "grows better on sandier soils"; "suitable 250–600 mm"). A
    lone report of the STUDY'S OWN LOCATION is **n=1 context** — it answers *"where did you
    work?"*, not *"where does the practice work?"* — and must NOT be extracted as suitability.
    The tell: "the study area is 900 mm / 28 °C / Lixisol / 30 trees·ha⁻¹", a figure caption
    ("Extended Figure 1: counts for croplands >300 mm"), or a region descriptor ("the Sahel
    covers 320 000 km²… arid ecosystems, 200–600 mm"). **A range or a number in the sentence
    does NOT make it a rule** — a context sentence routinely states the region's rainfall
    band; the FRAMING (study/figure/region) is what disqualifies it. **"Constrain by observed
    distribution" does NOT license this**: that principle is a *run-time DATASET-gating layer*
    (mask by a MapSPAM / EO host-distribution map, chosen via BIND), **not** a licence to
    encode one paper's site measurement as a T4 threshold. If a value is only a single-site
    observation, drop it (or, if it is a genuine outcome, route it to T6). Deterministically
    triaged by `schema_tools/check_scope.py` `site_context` (frame/occurrence − criterion −
    generalisation; tuned to 6/6 of the 2026-07 FMNR site-context drops, 0 rule false-positives).
17. **Relationship shape params MUST use the canonical keys** `abs_min`·`opt_low`·`opt_high`·
    `abs_max` (+ `unit`) — never free-form (`range_min`, `precip_mm_low`, `optimum_low_mm`,
    `sahelian_zone_min`, `low_density_per_ha`…). The T4 synthesiser reads only the canonical
    keys, so a real range under a free-form key is **silently invisible** — the family emits 0
    T4 rows despite genuine consensus (2026-07 FMNR: a rainfall envelope agreed across 7
    sources was lost this way). A range/optimum → `{"abs_min":…, "opt_low":…, "opt_high":…,
    "abs_max":…, "unit":"…"}`; a single floor/ceiling → the one bound; a categorical class is
    not a shape param (leave it descriptive). `recipe.synthesis.normalize_shape_keys` maps the
    common aliases as a safety net, but emit canonical directly.

The trustworthy gates are CENTRAL: the verbatim+page guardrail (`validate_sources.py`),
`check_numbers.py`, `check_scope.py`, `check_quote.py`, `check_picos.py` (wrong-practice),
`check_species.py` (species mis-tag), `quarantine.py` (auto-soft-deletes off-scope +
wrong-practice on build, reversible), and the adversarial relationship-verify. A subagent's
own self-check is advisory — do not rely on it. After a sweep, the learning loop is only
honest if feedback is incorporated: `learnings.py` tracks `review_log` vs adjustments and
the build flags unprocessed review decisions (run `/sweep-retro` → encode → `learnings.record`).
