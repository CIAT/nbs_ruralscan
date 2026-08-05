# Discovery log — Agroforestry · cross_family · T4

- Run `discovery_crossfam_homegardens_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 991 | 15 | 2 |
| updated_lit | 933 | 27 | 2 |
| grey | 16 | 16 | 2 |
| tool | 2 | 2 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: agroforestry AND (suitability OR biophysical OR mapping OR land) ; sort=cited_by_count:desc ; per_page=15`
- **updated_lit:** `OpenAlex title.search: agroforestry AND (suitability OR adoption OR mapping OR potential) , from_publication_date:2015-01-01 ; sort=cited_by_count:desc ; per_page=15 (companion determinants query: agroforestry AND (constraint OR determinant OR driver OR barrier), 202 hits)`
- **grey:** `WebSearch EN: "agroforestry suitability mapping biophysical criteria WOCAT FAO where trees on farms grow climate soil terrain" ; WebSearch EN: "WOCAT agroforestry technology land suitability slope rainfall requirements ICRAF suitability where agroforestry can be established"`
- **tool:** `WebSearch EN: "agroforestry suitability GIS multi-criteria GitHub tool Earth Engine land suitability model repository" ; GitHub API repo inspection saraheb3/AgroforestrySuitability_GEE`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `zomer2016_treecover_agland` | stock | oa | ok | high | Global Tree Cover and Biomass Carbon on Agricultural Land: the contribution of agroforestry to global and national carbon budgets — Cross-family observed-distribution / system_constraint anchor: quant |
| `nair1997_biophys_interactions` | stock | paywalled | ok | high | Biophysical interactions in tropical agroforestry systems — Seminal cross-family biophysical_constraint reference: light/water/nutrient/temperature interactions defining the general envelope for tree- |
| `dollinger2023_af_soil_adaptation` | updated_lit | oa | ok | high | Agroforestry potential for adaptation to climate change: A soil-based perspective — Cross-family biophysical_constraint (soil): general soil conditions/thresholds under which agroforestry establishes  |
| `sanou2019_socioecol_niche` | updated_lit | oa | ok | med | Socio-Ecological Niche and Factors Affecting Agroforestry Practice Adoption in Different Agroecologies of Southern Ethiopia — MIXED: agroecology-niche component = system_constraint (in-scope, LMIC Eth |
| `icraf_jharkhand_af_suitability` | grey | repo | ok | med | GIS-based assessment of land-agroforestry potentiality of Jharkhand State, India (CIFOR-ICRAF) — ICRAF grey, LMIC India (context tie-break up). Cross-family biophysical suitability criteria: slope, ra |
| `fao_land_eval_af_suitability` | grey | other | ok | med | FAO Framework for Land Evaluation guidelines applied to agroforestry suitability mapping (nutrient retention / rooting conditions / erosion hazard limiting-factor classes) — Methodological grey anchor |
| `af_suitability_gee_midwest_tool` | tool | repo | ok | med | AgroforestrySuitability_GEE - Agroforestry Suitability Decision Support Tool (US Midwest) — CODE evidence (not README). In-scope cross-family T4 params: env-priority criterion weights hardcoded per pr |

## Gaps / next iteration

SCOPE-DOMINANT GAP: the recent-lit corpus for cross-family agroforestry is heavily ADOPTION-DRIVER oriented (extension, credit, tenure, labour, market access) = soft enabling-env, which is OUT of T4 (routes to operational_risk / M2b per the 2026-06-23 re-ratification). Genuine practice-agnostic BIOPHYSICAL-envelope evidence is comparatively thin at cross-family level because most rigorous suitability thresholds are stated per sub-practice or per species (F1-F5), not for 'agroforestry in general' -> expect cross_family T4 to be a small common layer (broad bioclimatic/tree-cover envelope + FAO land-evaluation limiting-factor framing) with most specifics deferred to family-level sweeps. WOCAT SLM technology database did not surface a clean cross-family agroforestry suitability sheet in the grey search (its content is technology-specific) -> a targeted WOCAT API/DB query is a recommended follow-up. HARD legal exclusions (protected areas, water bodies, urban) were not specifically sourced here (generic, likely handled at framework/mask level, not cross-family evidence). No good OA seminal biophysical source beyond Nair1997 (paywalled) -> acquisition dependency.
