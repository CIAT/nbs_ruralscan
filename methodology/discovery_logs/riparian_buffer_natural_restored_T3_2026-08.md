# Discovery log — Riparian Buffers · natural_restored · T3

- Run `riparian_buffer_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.1 · nbs_id `riparian_buffer`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 305 | 40 | 4 |
| updated_lit | 90 | 30 | 5 |
| grey | 13 | 13 | 3 |
| tool | 52 | 15 | 2 |

### Verbatim search terms

- **stock:** `OpenAlex title.search (cited_by_count desc): "riparian restoration stream"; "riparian vegetation erosion"; "riparian buffer water quality"; "riparian buffer sediment"`
- **updated_lit:** `OpenAlex title.search from_publication_date:2015-01-01 (cited_by_count desc): "riparian buffer tropical"; "riparian restoration sediment"; "riparian revegetation"; "riparian buffer flood"; "riparian restoration Brazil"`
- **grey:** `WebSearch EN: "riparian buffer restoration natural regeneration guidance flood erosion USDA NRCS FAO". WebSearch ES: "restauración vegetación ribereña regeneración natural erosión inundación guía técnica"`
- **tool:** `GitHub search/repositories (stars desc): "riparian restoration"; "riparian buffer"; "InVEST natcap invest". WebSearch: "InVEST nutrient delivery ratio riparian buffer siting GIS MCDA restoration prioritization github"`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `osborne_kovacic_buffer_wq_restoration_1993` | stock | paywalled | ok | high | Riparian vegetated buffer strips in water-quality restoration and stream management — Seminal (950 cites), is_seminal. Frames buffer-strip restoration + stream management; sediment/nutrient/WQ T3. Tem |
| `riparian_restoration_effectiveness_wq_2012` | stock | oa | ok | high | The Effectiveness of Riparian 'Restoration' on Water Quality—A Case Study of Lowland Streams — Bronze OA. Restoration-focused (F2), measures WQ/sediment T3 outcomes of restored riparian buffers. Tempe |
| `restoration_age_nutrient_retention_2014` | stock | paywalled | ok | high | Influence of Restoration Age and Riparian Vegetation on Reach-Scale Nutrient Retention — Restoration-age gradient = regeneration/recovery trajectory (core F2 limiter: regeneration potential over time) |
| `riparian_bankerosion_sao_francisco_brazil_2005` | stock | oa | ok | med | Riparian vegetation affected by bank erosion in the Lower Sao Francisco River, Northeastern Brazil — Gold OA, Brazil (LMIC tie-break). Existing riparian veg condition vs bank erosion = F2 limiter + ba |
| `riparian_buffers_tropical_agriculture_review_2018` | updated_lit | oa | ok | high | Riparian buffers in tropical agriculture: scientific support, effectiveness and directions for future research — Hybrid OA. Review, tropical/LMIC agriculture context (directly offsets temperate stockt |
| `sediment_yield_riparian_vegetation_recovery_2021` | updated_lit | oa | ok | high | Reduction of sediment yield by riparian vegetation recovery at distinct levels of soil erosion — Gold OA. Vegetation RECOVERY (passive/natural restoration = F2 core) quantified against sediment yield  |
| `restoration_conservation_sediment_retention_2023` | updated_lit | oa | ok | high | Effects of Restoration and Conservation of Riparian Vegetation on Sediment Retention — Gold OA. Restoration + conservation of existing riparian veg (F2), sediment-retention T3. Recent. |
| `riparian_buffer_natural_flood_management_2020` | updated_lit | repo | ok | high | Riparian buffer strips and their effectiveness as a natural flood management measure — Green/repo OA (Heriot-Watt). Flood attenuation / peak-flow T3 — the flood mechanism under-covered elsewhere. NFM  |
| `riparian_forest_soil_bioengineering_brazil_2014` | updated_lit | oa | ok | med | Installation of a Riparian Forest by Means of Soil Bioengineering Techniques—Monitoring Results — Diamond OA, Brazil (LMIC). Riparian forest re-establishment for bank stabilization (bank-erosion/sedim |
| `nrcs_cps391_riparian_forest_buffer_std` | grey | oa | ok | high | USDA-NRCS Conservation Practice Standard 391 — Riparian Forest Buffer — Authoritative standard. Explicitly permits natural regeneration in lieu of planting (F2). Covers all 4 T3 mechanisms: 40-90% sed |
| `revive_mx_guia_restauracion_riparia` | grey | oa | ok | high | Guia Tecnica para la Restauracion Riparia (REVIVE MX) — Spanish, Mexico (LMIC, multilingual coverage). Natural-regeneration riparian restoration; bank-erosion reduction + flood-frequency/severity miti |
| `iowa_dnr_riparian_buffering_guide3` | grey | oa | ok | med | River Restoration Toolbox Practice Guide 3 — Riparian Buffering (Iowa DNR) — Restoration-toolbox practice guide; buffer establishment incl. natural regeneration, erosion/bank + sediment T3. Temperate  |
| `costarica_river_reforestation_invest_tool` | tool | repo | ok | high | kelley-langhans/CostaRica-river-reforestation (InVEST riparian buffer scenario + NDR/SDR) — Confirmed real code branch: generates forest riparian-buffer RESTORATION scenarios (F2) with hardcoded 10m w |
| `forested_buffers_toolbox_arcpy` | tool | repo | NO | med | ahalota/ForestedBuffersToolbox (arcpy forested riparian buffer delineation) — arcpy toolbox delineating forested riparian buffers from an input stream. Delineation/siting, not restoration-specific; bu |

## Gaps / next iteration

Coverage strong for sediment/bank-erosion and WQ T3 mechanisms; THERMAL/drought buffering (shade, baseflow) and FLOOD peak-flow attenuation are thin — 'riparian buffer thermal temperature stream' and 'riparian buffer peak flow' both returned OpenAlex COUNT=0 on title.search; only NRCS (shade) and the 2020 Heriot-Watt NFM paper (flood) touch them. Recommend a full-text/abstract-search pass for thermal refugia + baseflow. LMIC/tropical improved via targeted searches (2018 tropical review, Brazil x3, Costa Rica tool) but Africa/Asia riparian restoration essentially absent (one Nigeria pesticide paper, off-T3) — stocktake temperate skew only partly corrected. Grey lit: FAO/WOCAT/IWMI/CGIAR returned nothing riparian-specific; FR/PT grey rounds not run (EN+ES saturated guidance layer). Tools: only one confirmed hardcoded-rule repo (CostaRica InVEST); no GEE riparian-siting MCDA or stream-network suitability tool with inspectable buffer-width thresholds surfaced — a dedicated GEE/STAC tool search may be warranted. 'natural regeneration' as an exact title term is near-empty (COUNT=1) — the F2 concept lives under 'revegetation'/'recovery'/'passive restoration' vocabulary, which is where hits concentrated.
