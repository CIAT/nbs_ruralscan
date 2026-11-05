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

Remaining active claims: 13 awaiting individual review decisions.
