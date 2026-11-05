# New T4 claim review decisions — 5 November 2026

Sequential human review of the 17 active new claims from `t4_remaining32_20261105`
and `t4_followup_20261105`. The two quarantined Rao claims are separate. These
notes preserve decisions for subsequent scoped application; they do not themselves
change registers, approval flags, review-server decisions, mappings or family definitions.

## 1. Passive forest regeneration: proximity to mature forest

- Evidence: `ev_fr_distance_cloud2018_t4_20261105`.
- Source: Trujillo-Miranda et al. (2018), `cloud_forest_active_vs_passive_pasture_2018`, PDF p. 8 (printed p. 57), conclusions.
- Proposal presented: retain qualitative siting evidence for passive forest regeneration; proximity to mature forest favours that strategy. Do not infer a numerical distance curve, transferable cutoff or exclusion of distant sites.
- Pete's exact response: "agree, next".
- Accepted decision: keep on that qualitative basis, scoped to the source's abandoned-pasture/cloud-forest context in Veracruz, Mexico. The source explicitly distinguishes zones adjacent to mature forest from zones far from propagule sources and/or dominated by invasive species when discussing passive versus active restoration.
- Limitation preserved: this is an author recommendation from a 21-year comparison, not a fitted distance-response model or guarantee of complete passive recovery. Later interventions may still be needed. Do not classify study-site distances as suitability thresholds.
- Application status: human decision recorded; central review application and compilation pending. No executable numeric mapping approved.

## 2. Active forest planting: regional upper treeline

- Evidence: `ev_fr_elevation_wocat4101_t4_20261105`.
- Source: WOCAT (2018), `wocat_4101_2018`, PDF p. 1, high-altitude afforestation for erosion control in Armenia.
- Proposal presented: keep as regional contextual evidence only. Distinguish the reported South Caucasus upper treeline band of 2,300–2,600 m from the project's planting locations at 1,900–2,300 m; neither establishes a universal elevation cutoff.
- Pete's exact response: "ok".
- Accepted decision: retain the regional natural-forest-boundary evidence for contextual siting review. No global elevation threshold, numerical suitability curve, or inference that naturally treeless grasslands should become forest is approved.
- Limitation preserved: this is a regional expert statement without an exact local calibration. The nonnumeric lower treeline description (steppe and semi-desert ecosystems) must not be converted into an invented lower elevation threshold.
- Application status: human decision recorded; central review application and compilation pending. No executable numeric mapping approved.

## 3. Built-up land: shared exclusion, with wetland-source corroboration

- Evidence: `ev_wet_land_cover_xiangchina2023_20261105`.
- Source: Xiang et al. (2023), `wet_potential_distribution_china_ml_2023`, PDF pp. 17–18, section 4.3.
- Proposal presented: keep evidence supporting exclusion of existing built-up land from wetland-restoration candidates; retain the China/model context and distinguish built-up land from other human-used land such as cropland.
- Pete's exact response: "yes, but this is obvious rule that applies to nearly anything in rural scan\\".
- Accepted decision: keep the evidence as corroboration of a shared Rural Scan built-up-footprint exclusion, not as a distinctive wetland-specific suitability driver or an additional weighted score for this practice.
- The methodological hard-exclusion policy already includes urban/built-up footprints (`methodology/T4_generation_method.md`, section 2.7). During application, check shared-mask handling and avoid duplicate masking/weighting. A common policy statement is not proof that every runtime consumer already implements it.
- Preserve source provenance: this publication demonstrates the exclusion in China's wetland-restoration overlay; it is not evidence for every NbS independently. Do not copy the claim into all families as independent source support, treat all anthropogenic land as excluded, or silently convert every mixed/coarse land-cover cell to a built-up footprint.
- Application status: human decision recorded; central review application and shared-mask consistency check pending. No schema, global runtime mask or family definitions changed by this note.

## 4. Level soil bunds: rainfall preference

- Evidence: `ev_wh_levelbund_rain_wolka18_followup_20261105`.
- Source: Wolka et al. (2018), `wolka2018_swc_ssa_meta`, PDF p. 3 (printed p. 69), Table 1.
- Proposal presented: retain mean annual rainfall <1,400 mm as a preference for level soil bunds only, not a hard exclusion at or above 1,400 mm or a condition for every water-harvesting practice.
- Pete's exact response: "yes,  next".
- Accepted decision: keep that scoped implementation preference. Level soil bunds retain rainwater along contours; graded bunds discharge excess water and remain a separate scope issue. No numerical suitability curve, optimum lower bound, or zero-suitability tail is approved.
- Provenance: secondary review guidance with a grouped reference list; do not count the cited works as independently verified evidence votes or assign the condition to a particular primary without verification.
- Application status: human decision recorded; central review application and compilation pending. No executable numeric mapping approved.

## 5. Soil-bund slope: conditional evidence with unknown lower bound

- Evidence: `ev_wh_bund_slope_wolka18_followup_20261105`.
- Source: Wolka et al. (2018), `wolka2018_swc_ssa_meta`, PDF p. 3, Table 1: level/graded soil bunds fit well-drained soils deeper than 0.5 m, with a slope of up to 30%.
- Pete's clarification: "lower range is also uncertain it says slopes not flats too".
- Required interpretation: the source gives no explicit lower slope bound. Do not convert "up to 30%" into an approved 0–30% interval or infer that flat land is suitable. Conversely, the wording does not establish that flat land is unsuitable. Preserve the lower bound as unknown, the reported upper applicability value as 30%, and the soil conditions; suitability above 30% also remains unspecified.
- Do not invent a positive minimum slope or infer a numerical response curve. This clarification does not approve graded-bund routing or an executable mapping.
- After the revised interpretation was presented with lower bound unknown, soil conditions retained and no complete suitability curve, Pete's exact decision was: "yes, next".
- Accepted decision: keep the conditional evidence with both the lower-bound uncertainty and unspecified suitability above 30% explicit. Retain the current level-soil-bund scope rather than applying this condition to all water-harvesting practices.
- Application status: human decision recorded; central review application and compilation pending. No executable numeric mapping approved.

## 6. Fanya juu: slope-related embankment stability

- Evidence: `ev_wh_fanyajuu_slope_wolka18_followup_20261105`.
- Source: Wolka et al. (2018), `wolka2018_swc_ssa_meta`, PDF p. 9 (printed p. 75), discussion; practice description in Table 1, PDF p. 3.
- Proposal presented: retain a qualitative physical implementation constraint for Fanya juu: increasing steepness can reduce embankment stability. No slope cutoff, lower bound or numerical response curve; do not infer flat land is optimal or generalize to every terrace type.
- Pete's exact response: "ok next".
- Accepted decision: keep that qualitative constraint, scoped to Fanya juu in the source's Sub-Saharan African agricultural context. The source also mentions soil bunds, but this evidence unit remains scoped to Fanya juu rather than approving new family assignments.
- Provenance: author synthesis links reduced stability and greater occupation of cultivable land on steep slopes to crop-yield patterns. This review accepts the physical implementation condition only; it does not extract or approve crop-yield effects in the T4 lane.
- Application status: human decision recorded; central review application and compilation pending. No executable numeric mapping approved.

## 7. Tied ridges: qualitative gentle-slope condition

- Evidence: `ev_wh_tiedridge_slope_wolka18_followup_20261105`.
- Source: Wolka et al. (2018), `wolka2018_swc_ssa_meta`, PDF p. 3 (printed p. 69), Table 1.
- Proposal presented: keep the qualitative implementation condition that tied ridges are effective on gently sloping land. No numerical definition of gentle, lower slope bound, flat-land suitability, maximum slope or numerical curve is established. Construction dimensions are not landscape suitability thresholds.
- Pete's exact response: "ok next".
- Accepted decision: keep on that qualitative basis, restricted to tied ridges forming enclosed rainwater-retaining micro-basins; do not generalize to open ridges, tillage alone or all in-situ water-harvesting practices.
- Provenance: secondary review guidance with grouped citations, not independently verified votes from each cited primary.
- Application status: human decision recorded; central review application and compilation pending. No executable numeric mapping approved.

## 8. Wetland expansion: source-specific compatible land cover

- Evidence: `ev_wet_goyette_compatible_cover_20261105`.
- Source: Goyette et al., `watershed_restoration_targets_hydro_2022`, PDF pp. 5–6 (printed pp. 369–370), restoration scenarios in the St. Charles watershed, Quebec.
- Proposal presented: retain the model's forest, agriculture, open-land and bare-soil list as contextual spatial-allocation/scenario evidence only; do not turn those classes into universal restoration permissions, especially forest conversion. Impervious surfaces were omitted for socio-economic practicality, not established ecological impossibility.
- Pete's exact response: "fine, next".
- Accepted decision: keep that source-specific scenario evidence and the requirement for enough available compatible area within hydrological units. No universal class scores, global land-cover gate, pixel-level proof of former wetland history or permission to convert forest is approved.
- Application status: human decision recorded; central review application and compilation pending. No executable mapping approved.

## 9–15. China potential-wetland model: inputs and Figure 8 importance

- Source: Xiang et al. (2023), `wet_potential_distribution_china_ml_2023`. Table 1 / methods, PDF pp. 6–8; Figure 8, p. 16; restoration overlay, pp. 17–18.
- Seven evidence IDs and their retained Figure 8 relative importance values:
  - `ev_wet_xiang_apre_modeluse_20261105`: annual precipitation, 3.81%.
  - `ev_wet_xiang_amt_modeluse_20261105`: mean annual temperature, 4.20%.
  - `ev_wet_xiang_clay_modeluse_20261105`: clay content, 2.66%.
  - `ev_wet_xiang_ndvi_modeluse_20261105`: NDVI, 3.58%.
  - `ev_wet_xiang_dem_modeluse_20261105`: elevation, 5.05%.
  - `ev_wet_xiang_slope_modeluse_20261105`: slope, 3.43%.
  - `ev_wet_xiang_asp_modeluse_20261105`: aspect, 1.05%.
- Pete asked whether Figure 8 had been considered. A register check confirmed its values, method and denominator were already retained in each record's context; the review summary had understated this numerical evidence.
- Revised proposal presented: keep model use plus numerical importance and its method/denominator. These are relative mean-decrease-accuracy importance values across all 30 predictors, not percentages renormalized over these seven. They can inform variable selection and weighting discussions but do not supply standalone suitability directions, thresholds or response functions.
- Pete's exact response to the revised proposal: "ok good next".
- Accepted decision: keep all seven on that basis, preserving the China potential-wetland model and downstream restoration-targeting context. One study supplies seven variable records, not seven independent studies. Figure 8 values remain source-specific predictive importance; adoption as Rural Scan weights would require a separate modelling decision, which was not requested or approved here.
- Application status: human decisions recorded; central review application and compilation pending. No executable numeric suitability functions or runtime weights approved.

## 16. China restoration overlay: cropland, grassland and woodland

- Evidence: `ev_wet_xiang_convertible_cover_20261105`.
- Source: Xiang et al. (2023), `wet_potential_distribution_china_ml_2023`, PDF p. 18, section 4.3.
- Proposal presented: retain the source's intersection of modelled potential wetlands with current cropland, grassland and woodland as a spatial-targeting approach. No universal conversion permissions, class scores or assumption that every predicted site was historically wetland; retain the authors' woodland conservation trade-off.
- Pete's exact response: "fine, next".
- Accepted decision: keep that source-specific restoration-target overlay evidence. Land-cover membership alone is not a suitability condition: the source also requires predicted potential wetland location and its preceding built-up exclusion.
- Preserve independence: this is another component of the same Xiang study, not an additional independent source or a duplicate vote for the already reviewed built-up exclusion.
- Application status: human decision recorded; central review application and compilation pending. No global land-cover mask, numeric scores or authorization to convert other habitats approved.

## 17. Active afforestation: severe water-deficit constraint

- Evidence: `ev_fr_aridity_cao2011_t4_20261105`.
- Source: Cao et al. (2011), `excessive_afforestation_arid_china_2010`, PDF p. 5 (printed p. 244).
- Proposal presented: retain qualitative dry-region afforestation siting guidance where precipitation is much lower than potential evapotranspiration. No quantified meaning of "much lower", numerical rainfall/aridity cutoff, blanket dryland exclusion or globally monotonic wetter-is-better response.
- Pete's exact response: "ok next".
- Accepted decision: keep the qualitative constraint for active afforestation in the source's arid/semi-arid northern-China context, preserving the need to match vegetation restoration to available water.
- Provenance: secondary attribution to Cao et al. (2010), Nature correspondence, preserved. Do not count the cited finding twice or present it as an independently measured threshold from the 2011 review.
- Application status: human decision recorded; central review application and compilation pending. No executable numeric mapping approved.

All 17 active new claims now have recorded review decisions.

## Quarantined Rao claims: approve contextual reopening

- Evidence: `ev_af_annual_precipitation_rao97_targeting_20261105` and `ev_af_soil_ph_rao97_targeting_20261105`.
- Source: Rao, Nair and Ong (1997), `nair1997_biophys_interactions`, PDF pp. 15–16 (printed pp. 17–18), conclusions on hedgerow intercropping.
- Proposal presented: reopen both as contextual T4 implementation evidence for planted hedgerows alongside annual crops only. Retain rainfall–soil–management interactions; no independent rainfall/pH curve or blanket agroforestry exclusion.
- Pete's exact response: "ok next".
- Accepted decision: reopen and keep on that limited basis. Rainfall <1,000 mm/year is a conditional water-competition concern, not an absolute minimum; acid/infertile soils interact with amendments and long-term management, with no numerical pH threshold. Preserve management exceptions and the source discussion's scope; do not transform crop-yield or biomass values into T4 thresholds.
- The prior automated `off_scope:carbon_biomass` quarantine remains part of the history. Apply the authorized reopen through the normal review mechanism; do not erase the prior reason or broadly disable scope screening.
- Application status: decision recorded; central review application pending. No executable numeric mappings approved.

## Application update — 5 November 2026

The decisions above have now been applied through normal evidence review handling. See `methodology/audits/t4_followup_20261105/REVIEW_APPLICATION.md` for corrected claims, scoped compiled profiles, preserved evidence and outstanding dataset/eligibility holds. Earlier pending-status entries remain historical records of the review sequence.
