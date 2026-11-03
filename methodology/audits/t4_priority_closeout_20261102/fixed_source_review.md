# Fixed ten-source spatial-method review

## Outcome and limits

The ten agreed resources have verified identities, available full texts and the source-linked dispositions below. This closes the **bounded resource-reconciliation batch**, not all T4 extraction, human review, source supplements, code validation or project-wide discovery. No source is marked swept, no analytical rule is generated, and no human decision is changed. Candidate criteria remain accessible here even where a calibrated T4 relationship cannot be justified.

`source_manifest.json` records canonical titles, DOI checks, file hashes and team-library-relative paths. Nine DOIs were checked against Crossref using the repository metadata helper; the DOI-less cocoa report was checked against its publisher PDF's title and imprint. The two recovered grey PDFs were copied into the OneDrive team-library mirror and local corpus cache. Remote SharePoint synchronization was not independently verified. Page numbers below are **1-based native PDF pages in those exact hashed files**, including cover sheets. This is a targeted methods review, not a claim to have extracted every claim on every page.

`criteria_inventory.csv` preserves criterion groups, direction, source values, locators and routing. These are audit records, not schema-ready EV or approved response functions. No absence of calibration is being used to discard a criterion. Where a source mixes establishment, land management, benefit and cost, that mixture is retained explicitly.

## Ten dispositions

### 1. Molin et al. (2018)

**Retain: observed-regrowth targeting method, directional seed-source candidate, and restoration pathway comparison.** Native pp. 3–6, especially Fig. 2 (visually checked).

The Dinamica EGO weights-of-evidence model uses changes from crops/pasture to native forest between 2000 and 2010. Its 12 predictors are soil type, hydrographic network, forest type, rainfall, slope, altitude, population density, rural population density, municipal GDP, roads, urban areas and predominant land use. Predictions combine biophysical potential **and human agency**; the authors explicitly distinguish this from intrinsic regeneration capacity.

Regrowth is associated with proximity to forest remnants and water. The reported 100 m and 200 m associations, and slopes above 10%, are contextual observations, not global limits. Slope contrasts differ among landscape/land-use contexts. Keep distance-to-forest as a decreasing directional candidate for regeneration; do not convert the fitted probability into a universal ecological membership curve.

The authors assign 0–40% model probability to restoration planting, 41–70% to assisted regeneration and 71–100% to unassisted regeneration. Preserve these as source scenario bands, including the intervening gaps in the reported bounds. Pasture fencing, costs and land opportunity costs are implementation/scenario information. External supplements were not reconciled; full predictor transformations and reproducible model implementation are not claimed. Disposition: reviewed method referral with retained T4 candidate, no new EV promotion.

### 2. Crouzeilles et al. (2020)

**Retain: observed natural-regeneration targeting and cost scenarios.** Native pp. 3–6.

MapBiomas 30 m histories identify regrowth after at least five years of crop/pasture use, with at least three years' persistence and five contiguous pixels (0.45 ha). These are observation/classification rules, not minimum viable restoration-patch requirements. Existing forest, urban areas and water are excluded from the restoration domain.

County regression and pixel classification use random forests. The paper reports 80.2% explained county variation and 76.9% pixel accuracy; neither establishes transferability of a global establishment curve. Intermediate forest cover and proximity to remnants support a seed-source mechanism, while the reported 192 m proximity is descriptive, not a cutoff. The >50%/at-least-50% model-potential selections and opportunity-cost bands are scenario choices. The complete predictor/supplement inventory remains unavailable in the nine-page copy reviewed. No full-model or calibration-completeness claim. Disposition: reviewed method referral; supplement limitation retained without opening another literature batch.

### 3. Rajaonarivelo and Williams (2022)

**Retain: Madagascar restoration-priority model with five explicit criteria.** Native pp. 4–11; Tables 4–5 on pp. 10–11 visually checked.

The stated objective combines ecological and socioeconomic benefit. Distance to protected areas **and** forest patches is a compound criterion, not a clean distance-to-seed-source measurement. Four suitability classes and weights are preserved in the inventory. Higher soil loss means higher restoration priority; it must not be translated into better establishment conditions. Road and settlement distances encode disturbance/implementation assumptions. Dense/degraded forest, grassland and agricultural classes are priority categories, not permission to replace native grasslands.

The five weights are 0.25, 0.25, 0.16, 0.17 and 0.17. Soil-loss RUSLE factors and their land-cover/slope coefficients are upstream erosion-model inputs, not independent T4 response functions. Land-cover accuracy (87.1%, kappa 0.85) does not validate restoration success. Disposition: reviewed priority method; compound-variable and ecosystem-history holds prevent generic T4 thresholds.

### 4. Orsi and Geneletti (2010; online 2009)

**Retain: separate need, feasibility and option-ranking stages.** Native pp. 3–6; Fig. 2 on p. 4 visually checked. Canonical print year is 2010; retain the stocktake's 2009 filename as historical provenance.

Need criteria: distances to corridors, forests and protected areas decrease priority with distance; tree-species richness increases priority. Aspect heterogeneity and elevation variability are richness proxies, not elevation suitability limits. Feasibility criteria: distances from agriculture, roads and urban areas increase feasibility; erosion risk decreases it. Equal 0.25 within-group weights are the base scenario, not universal expert weights. Fig. 2 gives curve prototypes without numeric x1/x2 endpoints; do not invent those parameters.

Subsequent option ranking uses edge density, shape, corridor area, conversion cost, erosion-restoration area and poverty. The 15,000–16,500 ha planning target and removal of patches below 5 ha are planning choices. General reforestation is not enough to assign every criterion to one specific restoration family. Disposition: reviewed M4/implementation method with explicit feasibility criteria retained, no forced family mapping.

### 5. Morán-Ordóñez et al. (2022)

**Retain: Costa Rican multi-objective Marxan planning.** Native pp. 12–16 and Appendix S1 pp. 31–33; cost inputs p. 38. This is not the different Langhans record.

Forty-seven frugivorous bird models retained from 62 candidates (AUC >0.7) provide current seed-dispersal and future ecotourism surrogates; with carbon this yields 95 features. Bird habitat suitability is not a direct measurement of tree establishment or dispersal. Appendix S1 uses mean temperature, annual temperature range, annual precipitation, precipitation of the wettest month and forest cover. These are bird-model predictors, not forest-practice envelopes.

Existing forest is locked in; water, bare land and urban land are locked out. Pasture, annual crops and coffee provide restoration scenarios. Forest plantations also appear in the planning outputs; do not flatten this distinction into an eligibility mask. Elevations of 800 m for pasture and 1,000 m for crops/coffee alter opportunity-cost assumptions, not ecological suitability. The manuscript's expression “one record per ha (100 m2)” is internally inconsistent; do not silently use it to define resolution. Disposition: reviewed M4 method; no T3/T6 effects or T4 climate thresholds extracted.

### 6. Valente et al. (2021)

**Retain: water-service restoration-priority model.** Native pp. 4–8, Tables 2–3 and Fig. 3 (map inspected).

Five criteria: distance to springs, soil erodibility, slope, topographic wetness index and land cover. Reported AHP weights are 0.348, 0.208, 0.208, 0.129 and 0.106 (displayed total 1, rounded sum 0.999; CR 0.026). Higher erosion/slope/wetness prioritize service need; they do not demonstrate better establishment.

Standardization prose conflicts with the desired distance-to-spring ordering and the land-cover coding. Preserve the intended rank and flag the formula inconsistency. Observed AOI ranges are not response breakpoints. Road footprints, urban areas and water are masks; distance to roads is a different variable. Cross-tabulation against input layers is not independent success validation. Disposition: reviewed M4 method with explicit standardization hold.

### 7. Blanco-Sacristán et al. (2022)

**Retain: Red Sea mangrove-distribution/afforestation model, with assemblage and ecosystem-history limits.** Native pp. 2–6; Table 1 p. 2 visually checked for layout and all 32 candidate inputs transcribed as groups in the inventory. Final boldface predictor selection is not treated as independently reconciled here.

The workflow combines a 10 m Sentinel-2 CART land-cover classifier with 1 km MaxEnt habitat modelling. NDVI cutoffs (0.2 Sentinel-2, 0.1 Landsat) classify vegetation; they are not establishment limits. The 1.5 m above-sea-level land mask comes from a 30 m surface model in the Red Sea context, not a universal tidal/hydroperiod threshold. MaxEnt >0.5 and Fisher natural breaks select/rank model outputs; resampling to 10 m does not create 10 m environmental information.

The occurrence assemblage is dominated by Avicennia marina and Rhizophora mucronata. The model has no general intervention-success validation or explicit universal safeguard for replacing naturally nonforested intertidal habitat. Soil importance is predictive, not a causal calibrated response. Carbon and mapped-area tables are not T4 thresholds. Disposition: reviewed habitat-model referral, retained for species/assemblage and regional interpretation; no generic mangrove-practice curve.

### 8. Strassburg et al. (2020)

**Retain: PLANGEA global multi-biome prioritisation.** Native pp. 7–10, methods and code-availability statement.

Restoration is to inferred original forest, wetland, grassland, shrubland or arid ecosystems; it is not global tree-planting eligibility. Cropland and cultivated grassland are candidate converted land, with urban and rock/ice excluded. The approximately 4.96 km planning cells support carbon/biodiversity/cost optimization. The 70% remaining-native-vegetation sample rule and weighted 95th-percentile carbon reference are estimation choices, not forest-cover eligibility thresholds. Species elevation/habitat preferences refine biodiversity benefits, not restoration-practice envelopes. Yield-gap closure and cattle-density rules have distinct production/land-classification roles.

Carbon estimates lack explicit recovery time and may overstate near-term gains. Code availability says R code is available **upon request**; no public code archive is verified. Disposition: reviewed M4/M6 method; existing acquired-queue status is not mistaken for unread material, and no author-contact or code-search task is opened.

### 9. Chazdon and Guariguata (2018), CIFOR Occasional Paper 183

**Retain: tools synthesis and direct qualitative seed-source warning.** Recovered institutional copy includes an extra cover: printed page +11 = native PDF page. Title/imprint pp. 1, 4–5; contents pp. 6–7; ecosystem-service tool Table 5 p. 33; spatial-planning chapter pp. 43–54; Table 7 pp. 46–49. Not IUFRO World Series 34.

Table 5 describes SolVES, ARIES, InVEST, TESSA, MIMES, Co$ting Nature and ROOT. These are resource referrals, not claims that their current code was reviewed. Chapter 4 separates feasibility from benefit, describes systematic spatial trade-offs, and includes species-selection tools. Table 7's case studies remain secondary-source summaries; their citations are not automatically new acquisition tasks or independent validations.

Native p. 51 explicitly identifies soil disturbance and poor seed dispersal from remnant forest as reasons natural regeneration may fail. Retain this qualitative direction alongside existing WRI seed-source/disperser evidence; no distance or response curve is supplied. Coarse maps cannot resolve local performance (p. 54). Disposition: reviewed synthesis/referral and qualitative corroboration, no duplicate EV promoted merely to increase source counts.

### 10. Critchley, Sassen and Umunay (2021), UNEP-WCMC/UN-REDD

**Retain: observed cocoa-host mapping, shade-class rules and context-specific legal exclusions.** Native pp. 1–2, 18–24; all 14 Table 2 rules on p. 23 visually checked. Correct publisher report recovered; the stocktake SARE link is not this source.

Existing cocoa anchors the F5 host-system interpretation. Canopy/forest-history classes distinguish full-sun, partial-shade and high-shade cocoa. Remote canopy <30% is a full-sun proxy; it is not an optimum shade recommendation. The paper explains why field full-sun definitions (<10%) and remote canopy can disagree. Cocoa itself can exceed the tree-height threshold. Climate suitability >=20% is an output of a crop model, not a measured temperature/rainfall cutoff or yield fraction.

Expansion on non-cocoa land is limited to specified degraded classified forests under the report's 2021 policy scenario, with <25% canopy. This is not current legal authorization or global permission to convert forests. Protected areas, closed forest, settlements and water have distinct exclusion roles. Missing canopy data filled with zero may confuse absent data with absent canopy. Land-cover resolution is inconsistent (20 m in Table 1 versus 10 m in prose); resampling all data to 30 m does not improve the 1 km climate input.

Distances to closed forest and settlements on p. 24 are biodiversity/service-priority proxies, separate from the cocoa-host gate. Carbon comparisons are not extracted into the separate effect lane. Python/Jupyter/geemap/GEE and QGIS are named, but no repository implementation was verified. Disposition: reviewed F5 host/classification method and policy-specific scenario; do not force composite model outputs into general T4 numeric curves.

## Shared code disposition and stop rule

The seven previously inspected codebases remain **bounded method referrals with their recorded identity/file-line admission and substantive limitations**. This is the single shared closeout decision; it neither grants schema admission nor discards findings. Do not reopen seven repositories or issue seven PRs to inflate EV counts.

The fixed ten-source reconciliation is complete at the targeted-method level. Remaining supplement, calibration, family-mapping, policy and code limits are recorded, not silently converted into completed extraction. No automatic follow-on source search is scheduled. MapAWD and AAAA remain cross-track referrals. Human QA/QC can proceed on existing evidence independently of this documentation batch.
