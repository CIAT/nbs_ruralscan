# Candidate-Variable Register — Agroforestry F1 Planted silvoarable

**Status:** draft, June 2026. Discovery artefact (method §3). Not yet team-reviewed.

**Source signals:** (1) 23-paper corpus text scan; (2) Stocktake `Input_Variables` column
  (sparse, curated); (3) inherited draft-0 T4 list. Scoping-report agroforestry input is
  **MISSING** — `SpatialPrioritization_lit_review_input variables.xlsx` Agroforestry sheet is empty;
  scoping plan docx (`Spatial_Methodological_Plan_NbS Scoping_v2.docx`) not yet parsed for AF specifics.
  ML-importance: not run.

## Why this exists

Pete (2026-06-04): 'Where does the F1 variable list come from?' The answer was: not from
any audited triangulation. Draft-0 was authored ad-hoc and the team has been extracting
evidence *against that fixed list* rather than letting the corpus + scoping report inform it.
This register is the corrective — explicit, provenance-tracked candidate list with prevalence.

## Corpus-text prevalence (23 agroforestry papers, vectorless scan of tables + early body)

| Canonical variable | Papers / 23 | % | In draft-0 T4? |
|---|---:|---:|---|
| `annual_precipitation` | 23 | 100% | ✓ |
| `land_cover` | 23 | 100% | ✓ |
| `soil_erosion` | 18 | 78% |  |
| `slope` | 16 | 70% | ✓ |
| `poverty` | 16 | 70% |  |
| `elevation` | 15 | 65% |  |
| `soil_drainage` | 12 | 52% | ✓ |
| `soil_organic_carbon` | 11 | 48% | ✓ |
| `protected_areas` | 11 | 48% | ✓ |
| `soil_ph` | 10 | 43% | ✓ |
| `mean_annual_temperature` | 9 | 39% | ✓ |
| `tree_canopy_cover` | 9 | 39% | ✓ |
| `soil_texture` | 8 | 35% |  |
| `soil_n` | 7 | 30% |  |
| `soil_depth` | 6 | 26% |  |
| `ndvi` | 6 | 26% |  |
| `climate_type_koppen` | 6 | 26% |  |
| `tenure` | 5 | 22% |  |
| `soil_k` | 4 | 17% |  |
| `tmin` | 4 | 17% |  |
| `soil_moisture` | 4 | 17% |  |
| `aspect` | 4 | 17% |  |
| `soil_p` | 3 | 13% |  |
| `wetness_factor` | 3 | 13% |  |
| `aridity_index` | 3 | 13% | ✓ |
| `tmax` | 3 | 13% |  |
| `distance_river` | 2 | 9% |  |
| `evapotranspiration` | 2 | 9% |  |
| `distance_market` | 2 | 9% |  |
| `soil_cec` | 2 | 9% |  |
| `population_density` | 2 | 9% |  |
| `soil_bulk_density` | 2 | 9% |  |
| `literacy` | 1 | 4% |  |
| `distance_road` | 1 | 4% | ✓ |
| `temp_seasonality` | 1 | 4% |  |
| `soil_awc` | 1 | 4% |  |

## Gaps and tensions to resolve

### High-prevalence variables NOT in draft-0 (corpus says yes, draft-0 says no)
- **`elevation`** — 65% of corpus (Ahmad×3, Castle, Chuma, Haile, Marinis, Mendonça, Mushtaq,
  Nath, Seja, Singh, Wotlolan, Baldwin, Kiziridis). Stronger support than MAT. Likely a real omission.
- **`soil_erosion`** — 78%. Caveat: usually treated as the *dependent* variable (RUSLE output) rather
  than an input, so prevalence may be inflated. Decide: input or output?
- **`soil_texture`** — 35% (Mushtaq, Castle, Ellis, Haris, Kiziridis, Nath, Singh, Yadav).
- **`soil_depth`** — 26% (Mushtaq, Castle, Haris, Marinis, Palma, Ahmad_gop). Frequent in
  South-Asian AHP studies.
- **`soil_n / p / k`** — 30% / 13% / 17%. Together a 'nutrient availability' composite that
  several papers (Ahmad_gop, Ahmad18, Haile, Nath, Singh) use as a fertility layer.
- **`tenure`** — 22%. Inherent socio-economic variable underrepresented in draft-0.

### Draft-0 variables with weak corpus support
- **`aridity_index`** — 22%. Niche (Brandt, Chuma, Mushtaq, Nath, Ahmad20). Justifiable if
  scoping report calls for it; otherwise weak.
- **`mean_annual_temperature`** — 39%. Already flagged in MAT extraction note: only 1 source
  states a quantified F1 envelope. Consider dropping pending climate-vars-redundancy decision.
- **`distance_to_road`** — corpus signal very low (the term matches in only 1 paper here).
  Likely scoping-report-driven (scenario variable for investment-influenceable infrastructure).
  Keep, but flag the provenance gap.

### Likely false positives in the prevalence scan
- `poverty` (69%) — token matches 'poverty reduction' in NbS intros; not always a variable.
- `protected_areas` (48%) — could be intro/legal context, not always an exclusion layer.
- `soil_erosion` (78%) — input vs output ambiguity (see above).

## Per-paper variable touches

*(See `/tmp/var_audit.txt` for full per-paper listing — not committed to repo. Move to
`schema/registers/CV_per_paper_agroforestry_F1.csv` if we want it durable.)*

## Proposed next step

Before extracting more T4 rows, decide the F1 variable list by triangulating:
1. **Endorse, add, or drop** per the corpus-prevalence table above (Namita + Pete).
2. **Parse `Spatial_Methodological_Plan_NbS Scoping_v2.docx`** for AF-specific variable mentions;
   capture in a `scoping_candidate` block.
3. **Fill in the empty Agroforestry sheet** of `SpatialPrioritization_lit_review_input variables.xlsx`
   from the now-extracted EV register (the missing other half of the triangulation).
4. **Defer ML-importance** to Phase 2 (Brayden's pilot).
5. Re-run the extraction loop only on the endorsed list.

*This register is not yet in the structure manifest — promotes to a formal table only if the
candidate-variable layer becomes part of the schema (would key into VONT).*
