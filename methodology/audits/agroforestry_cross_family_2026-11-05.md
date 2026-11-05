# Agroforestry cross-family source triage — 5 November 2026

## Outcome and limits

The displayed cohort is not 17 independently established sources of evidence for every agroforestry family. It contains broad regional models, several narrower claims, species-selection evidence, companion artifacts, and preserved exclusions. No blanket reassignment to planted silvoarable is justified. The strongest immediate review candidates are the Castle alley-cropping row, Baldwin’s already-recorded F1/F3 applicability, Yadav’s species-model weights, and the Midwest tool’s economic-targeting claim. Haile’s parkland establishment pathway remains unresolved.

This is a bounded, read-only source-scope triage in response to feedback note 4: “can we review these sources in the desktop app to determine what practice they are? if genuinely cross-family?” It is not a new extraction, a complete table/figure sweep, a replication of the models, or a human approval. No SRC/EV/FAM records, pending decisions, review history, synthesis outputs or progress stamps were changed. All historical dropped rows remain in the inventory.

## Snapshot and reconciliation

- Code/register checkout: `598202af26669c300003c78a590624be936ea39a` (feedback worktree).
- Captured dashboard payload: `docs/dashboard_data.json`; embedded source commit `72386b2a548481580ef72c661134d820907a923e`, data ID `94c788c94135`, built `2026-11-05T05:24:31.644422+00:00`. Generated metadata can predate later register/code commits; these identifiers are reported separately.
- Exact selection: `progress_overview.table_views.T4.practices[nbs_id=agroforestry].families[family_id=agroforestry__cross_family].metrics.evidence_ids` and `source_keys`.
- Captured cohort: **17 source keys, 96 EV IDs, 75 retained records and 21 dropped records**. Of the 96, 86 carry `claim_scope=practice_technology` and 10 `species_specific`; all currently carry `use_role=structural_suitability` and family `agroforestry__cross_family`. `reviewer_ok=true` is recorded on 60 rows. These are existing record fields, not approvals granted by this audit.
- Original checkout was used only to read `.cache/corpus` artifacts. Its older generated dashboard contains the other 89 cohort rows but lacks the seven new Ranchi rows; this report therefore pins the current feedback-worktree cohort instead of silently substituting the original dashboard.
- All 17 cached artifacts were available (16 PDF paths and one HTML snapshot). Scope passages, current claim text, current context and review attribution were inspected. Page numbers below are **one-based PDF pages**, not printed journal pages. Original text inspection is distinguished from numerical/image revalidation and from context recorded by earlier reviewers. No new visual table/OCR verification is claimed.

## Rules used

Applied the current [extraction skill](../../.agents/skills/source-command-extract-evidence/SKILL.md) v1.9.4, [T4 review contract](../../.agents/skills/extraction_contracts/T4_review_contract.md), and [defect catalogue](../../.agents/skills/source-command-extract-evidence/references/defects.md): generic agroforestry stays broad unless a source or separately recorded synthesis decision establishes a system; species-selection use is distinct from practice suitability; site context, economic targeting and operational barriers cannot become structural thresholds through retagging. Variable use, direction and numerical calibration are separate assessments.

Family interpretations follow [FAM](../../schema/registers/FAM_family_registry.csv): F1 planted tree/crop systems; F2 regeneration/retention on farmland; F3 trees with grazing; F4 linear-placement logic; F5 shade over an existing perennial crop. The older [family narrative](../families/agroforestry.md) supplies the rationale but includes stale pilot/progress descriptions. Planted versus retained parkland is a consequential distinction. Cross-family is a metadata container, not itself a mapped practice.

## Priority findings

1. **Reconcile one confirmed duplicate identity before changing counts.** `ahmad_2020` and `cgspace_singh_southasia_2020` remain two separate `source_keys` with no merged alias in this cohort. Their DOI, registered SHA1 and cached PDF SHA256 match. The PDF names Ahmad and colleagues; the cgspace citation incorrectly names Singh. The two records hold 10 and 5 cohort EV IDs respectively. Merging the source identities would reduce this cohort’s 17 source records to 16 without deleting any of its 96 EV rows. It would not by itself prove independence of the remaining sources.
2. **Keep publications and companion software linked but distinct as artifacts.** Castle2025 and the Midwest GEE snapshot describe the same study. They must not become two independent votes for a relationship. Same-team/cited-primary methods, repeated variable branches and correction companions likewise require lineage-aware interpretation.
3. **Separate broad scope from universal applicability.** The dashboard scope definition currently says “applying across ALL agroforestry families”. The inspected cohort does not support that wording. Use a broad/undifferentiated or shared-system description, and display explicit `applicable_systems`/species-model scope where already recorded. A family field alone must not imply validated transfer to every family.
4. **Review clear scope/role mismatches first.** Castle’s retained land-cover quotation is specifically alley cropping. Baldwin already records F1/F3. Two active Yadav weights still have generic practice scope despite coming from the tree-species model. The Midwest production-gap claim is an economic-targeting rule. These are concrete per-record questions, not grounds for a bulk edit.
5. **Retain uncertainty and previous exclusions.** Haile parkland is unresolved between planting and retention; generic regional models cannot be forced into a family from title words. None of the 21 dropped rows should be automatically reopened during family cleanup. Species/crop evidence remains retained in its appropriate lane rather than discarded.

## Source-by-source review packet

The following inventory accounts for every selected EV ID exactly once. “Retained” means not currently marked dropped; it does not mean numerically executable, globally transferable, independently replicated or newly approved. Recommendations are proposed review actions only.

### 1. `ahmad_2017`

Ahmad, Firoz; Goparaju, Laxmi (2017). Land Evaluation in terms of Agroforestry Suitability, an Approach to Improve Livelihood and Reduce Poverty: A FAO based Methodology by Geospatial Solution: A case study of Palamu district, Jharkhand, India. Ecological Questions.

**Triage:** Broad regional model; historical exclusions.

**Original-artifact check:** PDF title/method and Table 5 p7; system discussion p12. Text layer has corrupted glyphs; this pass does not revalidate numerical cells.

**Finding:** The model integrates land, soil, climate and topography for Palamu. The discussion proposes agri-silvi-horticulture and planting tree species with crops, but the four cohort claims are regional model criteria rather than four family-specific experiments.

**Recommended follow-up:** Keep all four dropped records and their review history. If a reviewer reopens any, ask whether the specific criterion has conditional F1 relevance; do not infer universal F1–F5 applicability or reactivate the old numerical response. Existing slope-unit, rainfall-transfer and class-encoding objections remain separate.

Artifact: `.cache/corpus/ahmad_2017.pdf` in the original checkout. SHA256: `3febb34b8820d1555844fa9448ce707e3f1e2cb679a32a2c59807d7b3cb35375`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_t4_precip_ahmad17_1` | `annual_precipitation` | `practice_technology` | dropped | PDF p7 |
| `ev_t4_slope_ahmad17_1` | `slope` | `practice_technology` | dropped | PDF p7 |
| `ev_t4_soc_ahmad17_1` | `soil_organic_carbon` | `practice_technology` | dropped | PDF p7 |
| `ev_t4_soilph_ahmad17_1` | `soil_ph` | `practice_technology` | dropped | PDF p7 |

### 2. `ahmad_2018`

Ahmad, Firoz; Uddin, Md Meraj; Goparaju, Laxmi (2018). Assessment of remote sensing and GIS application in identification of land suitability for agroforestry: A case study of Samastipur, Bihar, India. Contemporary Trends in Geoscience.

**Triage:** Genuinely multiple proposed systems; no all-family transfer.

**Original-artifact check:** PDF opening context and p9 system discussion; existing p8 NDVI records and their source-review context inspected.

**Finding:** The paper explicitly discusses agri-horti-silviculture, agrisilviculture, silvopastoral and agrosilvopastoral systems. This supports a broad/multiple-system container, not proof that the NDVI ranking transfers to FMNR, linear-placement practices or shaded-perennial systems.

**Recommended follow-up:** Keep broad regional scope. Retain the two dropped records. Review the two retained NDVI records together as one source-variable relationship and correction companion, not two independent votes. An explicit F1/F3 transfer decision needs the model criterion and system context, not the list of practices alone.

Artifact: `.cache/corpus/ahmad_2018.pdf` in the original checkout. SHA256: `610db8e04a8aaa28cfd4566d7fe2fddc295b3ced49997907cf90a373d9e79e88`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_T4_canopy_ahmad2018_1` | `ndvi` | `practice_technology` | retained; reviewer_ok=true | PDF p8 |
| `ev_T4_landcover_ahmad2018_1` | `land_cover` | `practice_technology` | dropped | PDF p10 |
| `ev_T4_rereview_ahmad_2018_ndvi_1` | `ndvi` | `practice_technology` | retained; reviewer_ok=true | PDF p8 |
| `ev_T4_soilph_ahmad2018_1` | `soil_ph` | `practice_technology` | dropped | PDF p4 |

### 3. `ahmad_2020`

Ahmad, Firoz; Uddin, Md. Meraj; Goparaju, Laxmi; Rizvi, Javed; Biradar, Chandrashekhar (2020). Quantification of the Land Potential for Scaling Agroforestry in South Asia. KN - Journal of Cartography and Geographic Information.

**Triage:** Broad regional model; duplicate source identity.

**Original-artifact check:** PDF pp1,3,6,8, including opening authors, model description, cropland analysis and mixed/homegarden examples. Table 2 image values are not newly revalidated in this pass.

**Finding:** A South Asian generic agroforestry land-evaluation model is followed by tree-cover analysis on cropland and discussion of several local systems. It does not assign each of these ten model-use/direction records to one establishment family.

**Recommended follow-up:** Retain broad regional model scope and existing calibration holds. Reconcile this source with cgspace_singh_southasia_2020 through an audited alias/identity correction; keep every EV ID and review decision. Combine model-use and direction companions by source × variable for interpretation rather than counting two studies.

Artifact: `.cache/corpus/ahmad_2020.pdf` in the original checkout. SHA256: `88139c47184dfebe050a87a384ab216ceeb97636657068969c85d341bd89c153`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_T4_model_use_ahmad2020_annual_precipitation` | `annual_precipitation` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_model_use_ahmad2020_aridity_index` | `aridity_index` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_model_use_ahmad2020_mean_annual_temperature` | `mean_annual_temperature` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_model_use_ahmad2020_ndvi` | `ndvi` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_model_use_ahmad2020_slope` | `slope` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_rereview_ahmad_2020_annual_precipitation_2` | `annual_precipitation` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_rereview_ahmad_2020_aridity_index_3` | `aridity_index` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_rereview_ahmad_2020_mean_annual_temperature_1` | `mean_annual_temperature` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_rereview_ahmad_2020_ndvi_4` | `ndvi` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_rereview_ahmad_2020_slope_5` | `slope` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |

### 4. `baldwin_2022`

Baldwin et al. (2022). Geospatial Analysis and Land Suitability for “FloodWise” Practices: Nature-Based Solutions for Flood Mitigation in Eastern, Rural North Carolina. Land.

**Triage:** Explicit narrower shared applicability: F1 and F3.

**Original-artifact check:** PDF Table 1 p6 and methods pp8–9; cohort recovery quotation p16 and full existing applicability context inspected.

**Finding:** Table 1 defines agroforestry as pine with pasture. Section 2.2.2 also describes trees with row crops and livestock. The land-cover and infrastructure masks apply to that shared mapping exercise. The two newer records already say applicable_systems=[planted_silvoarable,silvopastoral].

**Recommended follow-up:** Surface the existing F1/F3 applicability in review and bibliography. Preserve the cross-family storage container until the shared-claim representation is deliberately resolved; do not copy one claim into every family. The older land-cover row is marked superseded_by the newer row: preserve history and inspect effective duplicate support. Keep local land-cover crosswalk, infrastructure-buffer and parcel-size transfer holds; low-productivity targeting is not a universal suitability boundary.

Artifact: `.cache/corpus/baldwin_2022.pdf` in the original checkout. SHA256: `954c98833988c7e538f2c789b9e4f6a7e7b2e9d5f2202a312c568fd5f9449266`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_T4_landcover_baldwin2022_recovery` | `land_cover` | `practice_technology` | retained; reviewer_ok=true | PDF p16 |
| `ev_operational_risk_built_up_areas_baldwin_2022_full` | `built_up_areas` | `practice_technology` | retained; reviewer_ok=true | PDF p8 |
| `ev_structural_suitability_land_cover_baldwin_2022_full` | `land_cover` | `practice_technology` | retained; reviewer_ok=true | PDF p8 |

### 5. `brandt_2015`

Brandt, Patric; Kvakić, Marko; Butterbach‐Bahl, Klaus; Rufino, Mariana C. (2015). How to target climate-smart agriculture? Concept and application of the consensus-driven decision support framework “targetCSA”. Agricultural Systems.

**Triage:** Off-scope historical claim: climate vulnerability/priority method.

**Original-artifact check:** PDF opening abstract and Table 1 p5.

**Finding:** The quoted rainfall statement describes water availability and agricultural productivity in a climate-vulnerability/CSA targeting framework. It does not establish an agroforestry establishment criterion or a particular agroforestry family.

**Recommended follow-up:** Preserve the dropped row. Do not reclassify it to a family simply because the wider paper mentions agroforestry. A separately authorised methods/priority-lane reuse would need its own purpose and provenance; no new extraction is proposed here.

Artifact: `.cache/corpus/brandt_2015.pdf` in the original checkout. SHA256: `e03143c52086c8d528667f2d61a04bf80d094bbabd18f4b5e18a6b37e8fcdb9c`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_t4_prec_brandt2015_1` | `annual_precipitation` | `practice_technology` | dropped | PDF p5 |

### 6. `castle_2025`

Castle, Sarah; Miller, Daniel C.; Wardropper, Chloe B. (2025). Mapping the social-ecological suitability of agroforestry in the US Midwest. Environmental Research Letters.

**Triage:** Mixed source: explicit F1 claim plus tree-species suitability method.

**Original-artifact check:** PDF opening identity and Table 2 pp7–8; companion snapshot methodology checked.

**Finding:** The land-cover quotation is specifically the Alley cropping row on p8, separate from rows for silvopasture, riparian buffers and windbreaks. The retained drainage and frost-free-period records belong to Indicator 2, tree growth suitability, whose criteria are assessed for selected tree species, rather than a universal agroforestry envelope.

**Recommended follow-up:** First review ev_t4_land_cover_castle2025_1 for F1 assignment (including its explicit nongrazed-forage qualification). Review ev_t4_soil_drain_castle2025_1 and ev_t4_mat_castle2025_1 as species-selection/model-use evidence; inspect Supplementary Table S1 before claiming a taxon-specific response or threshold. Keep all four dropped records. Link the paper and tool as one study lineage while retaining distinct artifacts.

Artifact: `.cache/corpus/castle_2025.pdf` in the original checkout. SHA256: `ffb78fb0dddf32730edd06288132151d7515d86d70b7a1361c42944d99d6dde7`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_t4_ann_precip_castle2025_1` | `annual_precipitation` | `practice_technology` | dropped | PDF p7 |
| `ev_t4_finance_castle2025_1` | `finance_credit_access` | `practice_technology` | dropped | PDF p3 |
| `ev_t4_land_cover_castle2025_1` | `land_cover` | `practice_technology` | retained; reviewer_ok=true | PDF p8 |
| `ev_t4_mat_castle2025_1` | `frost_free_period` | `practice_technology` | retained; reviewer_ok=true | PDF p7 |
| `ev_t4_protected_castle2025_1` | `protected_area_status` | `practice_technology` | dropped | PDF p3 |
| `ev_t4_soil_drain_castle2025_1` | `soil_drainage` | `practice_technology` | retained; reviewer_ok=true | PDF p7 |
| `ev_t4_soil_ph_castle2025_1` | `soil_ph` | `practice_technology` | dropped | PDF p7 |

### 7. `castle_sr_2021`

Castle, S. E. et al. (2021). The impacts of agroforestry on agricultural productivity, ecosystem services, and human well‐being in low‐ and middle‐income countries: A systematic review. Campbell Systematic Reviews.

**Triage:** Off-scope historical claim within a multi-practice review.

**Original-artifact check:** PDF title/abstract, practice descriptions and p29 discussion of Lawry et al. (2014).

**Finding:** The systematic review covers multiple agroforestry systems, but the cohort contains only a secondary statement about tenure interventions and welfare from a wider agricultural review. It is not an establishment suitability response.

**Recommended follow-up:** Preserve the dropped tenure row and cited-primary attribution. Family retagging would not fix the role mismatch. Any future operational-risk/effect reuse requires separately scoped source review; do not promote this claim through the T4 family screen.

Artifact: `.cache/corpus/castle_sr_2021.pdf` in the original checkout. SHA256: `2a6e4b24398e6e4ecb60024decc36adcc5508ff1018292507c1ae6fb2241215e`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_tenure_security_castle21_3` | `tenure_security` | `practice_technology` | dropped | PDF p29 |

### 8. `cgspace_singh_southasia_2020`

Singh et al. (2020). Quantification of the Land Potential for Scaling Agroforestry in South Asia. KN - J. Cartography & Geographic Information 70:71-89.

**Triage:** Duplicate of Ahmad 2020; broad model, two historical exclusions.

**Original-artifact check:** Cached PDF is byte-identical to ahmad_2020; opening page and pp3,6–8 checked through that identical artifact.

**Finding:** The source is Ahmad et al., not Singh et al. Both records have DOI 10.1007/s42489-020-00045-0. The retained rows concern soil-quality class definitions and a cropland analysis mask; the dropped rows describe resulting suitable area/tree-cover distributions.

**Recommended follow-up:** Make the source identity/citation correction first, preserving this acquisition/discovery history and all five EV IDs. Keep the two dropped claims excluded. Do not turn a cropland mask used for tree-cover analysis into a new universal family gate. Keep soil-quality codebook and target-dataset crosswalk holds.

Artifact: `.cache/corpus/cgspace_singh_southasia_2020.pdf` in the original checkout. SHA256: `88139c47184dfebe050a87a384ab216ceeb97636657068969c85d341bd89c153`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `cgspace_singh_southasia_2020__land_cover__01` | `land_cover` | `practice_technology` | retained; reviewer_ok=true | PDF p3 |
| `cgspace_singh_southasia_2020__land_cover__02` | `land_cover` | `practice_technology` | dropped | PDF p6 |
| `cgspace_singh_southasia_2020__soil_texture_hsg__01` | `soil_quality_class` | `practice_technology` | retained; reviewer_ok=true | PDF p3 |
| `cgspace_singh_southasia_2020__soil_texture_hsg__02` | `soil_quality_class` | `practice_technology` | retained; reviewer_ok=true | PDF p3 |
| `cgspace_singh_southasia_2020__tree_canopy_cover__01` | `tree_canopy_cover` | `practice_technology` | dropped | PDF p7 |

### 9. `chuma_2021`

Chuma, Géant Basimine; Cirezi, Nadège Cizungu; Mondo, Jean M.; Mugumaarhahama, Yannick; Ganza, Deckas; Katcho, Karume; Mushagalusa, Gustave Nachigera; Schmitz, Serge (2021). Suitability for agroforestry implementation around Itombwe Natural Reserve (RNI), eastern DR Congo: Application of the Analytical Hierarchy Process (AHP) approach in geographic information system tool. Trees, Forests and People.

**Triage:** Broad regional tree/crop model; no unique family established.

**Original-artifact check:** PDF opening/system passages, methods p3, Table 3/source-system discussion p6 and existing p5 context inspected.

**Finding:** The regional model concerns agroforestry around Itombwe reserve and discusses matching trees to farmers’ main crops and needs. It does not establish one planted-vs-regeneration pathway for all four retained claims. Land cover is currently model-use only; conflict and a richer-looking land-cover extraction are already dropped.

**Recommended follow-up:** Keep the regional/broad container pending an explicit practice description. F1 is a candidate interpretation, not an automatic correction. Preserve altitude/latitude/AEZ, printed aspect-label and class-index holds, and retain the dropped conflict and land-cover rows. Ask system applicability separately from numerical approval.

Artifact: `.cache/corpus/chuma_2021.pdf` in the original checkout. SHA256: `7d30a11e6a21ec96c8ef4076cf405a5fdcb38e11a47ce81400f4596a3d6bb732`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_T4_conflict_fragility_index_chuma21_1` | `conflict_fragility_index` | `practice_technology` | dropped | PDF p6 |
| `ev_T4_elevation_chuma2021_recovery` | `elevation` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_land_cover_chuma21_1` | `land_cover` | `practice_technology` | retained; reviewer_ok=true | PDF p3 |
| `ev_T4_rereview_chuma_2021_aspect_1` | `aspect` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_rereview_chuma_2021_land_cover_3` | `land_cover` | `practice_technology` | dropped | PDF p5 |
| `ev_T4_slope_chuma21_1` | `slope` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |

### 10. `haile_2024`

Haile, Getachew (2024). Land Suitability Evaluation for Agroforestry Using Geospatial Techniques in Genale Sub-basin Oromia, Ethiopia. Agriculture, Forestry and Fisheries.

**Triage:** Insufficient establishment detail: parkland could be F1 or F2.

**Original-artifact check:** PDF title/abstract and p9 validation/parkland description; current p5–8 claim/context fields inspected.

**Finding:** Validation describes parkland agroforestry with named woody species, but the inspected passage does not say whether trees were planted, retained or regenerated. That missing distinction controls the F1/F2 split; the word parkland alone is insufficient.

**Recommended follow-up:** Keep scope unresolved rather than assign all eight records to F1 or F2. Follow the cited field-characterisation source [9] and methods for establishment history, then make a documented group decision. Retain one dropped rainfall record; do not resurrect it as part of family cleanup. Preserve source ranking/transfer and pH/soil-branch calibration holds.

Artifact: `.cache/corpus/haile_2024.pdf` in the original checkout. SHA256: `f9aba0e5ce1dad8d21d9c3922dc81e15de6d92b6a6f352492cc67140abcb9eb0`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_T4_ph_haile2024_1` | `soil_ph` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_T4_precip_haile2024_1` | `annual_precipitation` | `practice_technology` | dropped | PDF p8 |
| `ev_T4_precip_haile2024_2` | `annual_precipitation` | `practice_technology` | retained; reviewer_ok=true | PDF p5 |
| `ev_T4_rereview_haile_2024_elevation_1` | `elevation` | `practice_technology` | retained; reviewer_ok=true | PDF p5 |
| `ev_T4_slope_haile2024_1` | `slope` | `practice_technology` | retained; reviewer_ok=true | PDF p7 |
| `ev_T4_slope_haile2024_2` | `slope` | `practice_technology` | retained; reviewer_ok=true | PDF p7 |
| `ev_T4_soc_haile2024_1` | `soil_organic_carbon` | `practice_technology` | retained; reviewer_ok=true | PDF p5 |
| `ev_T4_soc_haile2024_continuation` | `soil_organic_carbon` | `practice_technology` | retained; reviewer_ok=false | PDF p6 |

### 11. `india_fao_agroforestry_suitability_mapping_2017`

Ahmad et al. (2017). FAO guidelines and geospatial application for agroforestry suitability mapping: case study of Ranchi, Jharkhand state of India. Agroforestry Systems.

**Triage:** Broad regional model with planted tree/crop discussion; family unresolved.

**Original-artifact check:** PDF opening abstract, p8 system discussion; seven current p9/p11 records and their explicit practice_as_described/calibration context inspected.

**Finding:** The Ranchi land-evaluation model discusses agri-silvi-horticulture, tree/crop integration and dryland alternatives, but the inspected material does not uniquely establish a family for every model criterion. These seven records are new, unapproved scoping candidates.

**Recommended follow-up:** Retain broad regional scope and all seven pending review states. Ask whether the relevant land-use proposal supports conditional F1 applicability without treating the paper as validation across all families. Preserve the narrow rainfall range, inequality/OCR, nitrogen-unit and shared-method lineage holds; do not substitute Palamu or same-team papers as independent calibration validation.

Artifact: `.cache/corpus/india_fao_agroforestry_suitability_mapping_2017.pdf` in the original checkout. SHA256: `044eb011675f10b336ae72a62e207408078b31ecf3217ae4e8b4adc2900a98a1`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_af_annual_precipitation_ranchi2017_20261105` | `annual_precipitation` | `practice_technology` | retained; reviewer_ok=false | PDF p11 |
| `ev_af_elevation_ranchi2017_20261105` | `elevation` | `practice_technology` | retained; reviewer_ok=false | PDF p11 |
| `ev_af_ndvi_ranchi2017_20261105` | `ndvi` | `practice_technology` | retained; reviewer_ok=false | PDF p11 |
| `ev_af_slope_ranchi2017_20261105` | `slope` | `practice_technology` | retained; reviewer_ok=false | PDF p11 |
| `ev_af_soil_nitrogen_ranchi2017_20261105` | `soil_nitrogen` | `practice_technology` | retained; reviewer_ok=false | PDF p9 |
| `ev_af_soil_organic_carbon_ranchi2017_20261105` | `soil_organic_carbon` | `practice_technology` | retained; reviewer_ok=false | PDF p11 |
| `ev_af_soil_ph_ranchi2017_20261105` | `soil_ph` | `practice_technology` | retained; reviewer_ok=false | PDF p11 |

### 12. `moisa_2025`

Moisa, Mitiku; Gurmessa, Mengistu; Oljira, Dereje; Dinsa, Misgana Lamessa; Deribew, Kiros; Roba, Zenebe; Tadesse, Tekalign; Gemeda, Dessalegn (2025). Spatial land suitability modeling for livestock production for closing yield gaps in Western parts of Ethiopia. Cogent Food & Agriculture.

**Triage:** Wrong practice historical claim: livestock production.

**Original-artifact check:** PDF title and p2 abstract/method statement.

**Finding:** The model assesses land suitability for cattle, sheep, goats and camels. The cited slope-input sentence does not establish integration of trees with livestock. Livestock suitability alone is not silvopastoral evidence.

**Recommended follow-up:** Leave the already-dropped wrong_practice record excluded and visible in history. Do not move it into F3 based on livestock words or its stocktake folder.

Artifact: `.cache/corpus/moisa_2025.pdf` in the original checkout. SHA256: `ddf033da519ccdac16b89df26b879fe1b8085216572bc38dfd912035e28685d9`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_t4_slope_moisa25_1` | `slope` | `practice_technology` | dropped | PDF p2 |

### 13. `mushtaq_2023`

Mushtaq, Ruyida; Yadav, Rajesh Kumar; Fayaz, Abida; Ahmed, Pervez; Singh, Harmeet (2023). Multi-criteria land suitability assessment for mulberry-based agroforestry using AHP and GIS approach in Anantnag district of the Kashmir valley, India, to achieve sustainable agriculture. Environment, Development and Sustainability.

**Triage:** Seven narrow mulberry records plus one generic secondary statement.

**Original-artifact check:** PDF pp1–2 establish mulberry/sericulture scope; cohort Table 5 p13 and p17 discussion records/context inspected.

**Finding:** Seven records already carry species_specific and Morus spp. The eighth rainfall statement is a generic secondary claim citing Ahmad 2019, and its existing system_applicability_review explicitly retains generic secondary context. Mulberry production does not imply shade trees over an existing perennial crop.

**Recommended follow-up:** Keep the seven narrow rows in the species/crop review lane and out of general practice calibration. Because p2 describes cultivated leaves for silkworms, ask the reviewer whether the project’s crop-vs-species convention requires crop_specific; do not change it silently. Keep the eighth row’s generic secondary status and trace its cited primary before any numerical use. Neither blanket F1 nor F5 assignment is justified by the crop name.

Artifact: `.cache/corpus/mushtaq_2023.pdf` in the original checkout. SHA256: `40906e5fabc5daa3cad4d2797b84a182987c705ca97f57cdc0f79ee8e0589ee6`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_T4_rereview_mushtaq_2023_annual_precipitation_4` | `annual_precipitation` | `species_specific` | retained; reviewer_ok=false | PDF p13 |
| `ev_T4_rereview_mushtaq_2023_land_cover_3` | `land_cover` | `species_specific` | retained; reviewer_ok=false | PDF p13 |
| `ev_T4_rereview_mushtaq_2023_mean_annual_temperature_2` | `mean_annual_temperature` | `species_specific` | retained; reviewer_ok=false | PDF p13 |
| `ev_T4_rereview_mushtaq_2023_slope_1` | `slope` | `species_specific` | retained; reviewer_ok=false | PDF p13 |
| `ev_T4_rereview_mushtaq_2023_soil_drainage_6` | `soil_drainage` | `species_specific` | retained; reviewer_ok=false | PDF p13 |
| `ev_T4_rereview_mushtaq_2023_soil_ph_7` | `soil_ph` | `species_specific` | retained; reviewer_ok=false | PDF p13 |
| `ev_T4_rereview_mushtaq_2023_soil_texture_5` | `soil_texture` | `species_specific` | retained; reviewer_ok=false | PDF p13 |
| `ev_t4_precip_mushtaq2023_2` | `annual_precipitation` | `practice_technology` | retained; reviewer_ok=true | PDF p17 |

### 14. `nath_2021`

Nath, Arun Jyoti; Kumar, Rakesh; Devi, N. Bijayalaxmi; Pebam, Rocky; Giri, Krishna; Sahoo, Uttam Kumar; Bajpai, Raj Kumar; Sahu, Netrananda; Pandey, Rajiv (2021). Agroforestry land suitability analysis in the Eastern Indian Himalayan region. Environmental Challenges.

**Triage:** Broad regional model with mixed validation systems.

**Original-artifact check:** PDF title/abstract, current Table 2 p11 records/context and original Table 5/discussion p19.

**Finding:** Table 5 validation includes homegardens, Piper-betel, fruit-tree, bamboo, Eri-silk and Ananas systems; the discussion also says system choice varies with location and tree species. The regional model is not a separate measured envelope for every named family.

**Recommended follow-up:** Keep a broad/model scope, with the validation mix visible. Do not move all sixteen rows to homegardens just because most validation locations are homegardens, or to F1 because generic crop/trees are discussed. Preserve depth/branch distinctions and source × variable deduplication; use existing reviewer requests when deciding how to summarise soil branches. Units, aridity scale, NDVI overlap and categorical crosswalk holds remain.

Artifact: `.cache/corpus/nath_2021.pdf` in the original checkout. SHA256: `b800444c537664a9f0320e14c2b4e1cf6aa513002a10c51360f7a73c54e3531c`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_T4_rereview_nath_2021_aspect_12` | `aspect` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_elevation_11` | `elevation` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_evapotranspiration_ref_1` | `evapotranspiration_ref` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_soil_available_water_capacity_10` | `soil_available_water_capacity` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_soil_bulk_density_8` | `soil_bulk_density` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_soil_cation_exchange_capacity_3` | `soil_cation_exchange_capacity` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_soil_organic_carbon_subsoil_5` | `soil_organic_carbon_subsoil` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_soil_ph_7` | `soil_ph` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_soil_ph_subsoil_4` | `soil_ph_subsoil` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_soil_ph_subsoil_9` | `soil_ph_subsoil` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_soil_texture_2` | `soil_texture` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_T4_rereview_nath_2021_soil_texture_6` | `soil_texture` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_t4_aridity_nath21_03` | `aridity_index` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_t4_landcov_nath21_01` | `ndvi` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_t4_soildra_nath21_01` | `soil_drainage` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |
| `ev_t4_treecan_nath21_01` | `land_cover` | `practice_technology` | retained; reviewer_ok=true | PDF p11 |

### 15. `saraheb3_af_midwest`

Castle, S.E., Miller, D.C., Wardropper, C. (2025). US Midwest Agroforestry Suitability Mapping — GEE code + Decision Support Tool (accompanying Environ. Res. Lett.).

**Triage:** Companion tool; retained claim is economic targeting, not core suitability.

**Original-artifact check:** Full cached HTML/README snapshot, including Overview and Details of Methodology; corresponding Castle paper Table 2 checked. This pass did not execute or inspect the underlying GEE code.

**Finding:** The retained production_gap quotation describes economic competitiveness of agroforestry against conventional agriculture on marginal land. The snapshot separately describes environmental priority, tree-species suitability, social feasibility and economic viability. This is a purpose/role issue rather than evidence that all families share an establishment limit.

**Recommended follow-up:** Flag ev_production_gap_saraheb3_tool for review against constrained_aoi and wrong_table: preserve the claim as tool-design/economic-priority evidence, not a global opportunity-space limit. Preserve the already-dropped soil-erosion row. Keep the paper/tool lineage linked for independent-support counting. Verify code/version only if a later authorised technical replication is undertaken.

Artifact: `.cache/corpus/saraheb3_af_midwest.html` in the original checkout. SHA256: `24d405d93ca02f490b1048fb795b4aaf322243395640c9e1231c685e43d019aa`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_production_gap_saraheb3_tool` | `production_gap` | `practice_technology` | retained; reviewer_ok=true | section: Details of Methodology |
| `ev_soil_erosion_risk_saraheb3_tool` | `soil_erosion_risk` | `practice_technology` | dropped | section: Details of Methodology |

### 16. `singh_2026`

Singh, R. et al. (2026). Scaling agroforestry land suitability analysis in Odisha, India: a machine learning approach. Frontiers in Remote Sensing.

**Triage:** Broad regional model with several explicit deployment practices.

**Original-artifact check:** PDF opening abstract, methods context p3 and current Table 1 p4 records; system terms checked against original text.

**Finding:** The same regional suitability model is overlaid with land use to propose bund/boundary planting and intercropping, homegardens and block/bulk plantation. These distinct placements are not six separate family-specific responses. F1/F4 distinction depends on whether planting envelope or linear geometry governs the claim; homegardens remain qualitative.

**Recommended follow-up:** Retain the six general model criteria in broad scope, with explicit candidate practices rather than all-family transfer. Do not assign every row to F4 from boundary language or to F1 from intercropping language. Preserve the cited Singh2022 weight lineage and numerical endpoint holds; any family transfer needs a recorded synthesis decision.

Artifact: `.cache/corpus/singh_2026.pdf` in the original checkout. SHA256: `80084dc59dbc30b94a5572b616812c6ca65187263c6293651d17fd451741bb57`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_T4_rereview_singh_2026_annual_precipitation_6` | `annual_precipitation` | `practice_technology` | retained; reviewer_ok=true | PDF p4 |
| `ev_T4_rereview_singh_2026_mean_annual_temperature_5` | `mean_annual_temperature` | `practice_technology` | retained; reviewer_ok=true | PDF p4 |
| `ev_T4_rereview_singh_2026_slope_4` | `slope` | `practice_technology` | retained; reviewer_ok=true | PDF p4 |
| `ev_T4_rereview_singh_2026_soil_drainage_2` | `soil_drainage` | `practice_technology` | retained; reviewer_ok=true | PDF p4 |
| `ev_T4_rereview_singh_2026_soil_ph_3` | `soil_ph` | `practice_technology` | retained; reviewer_ok=true | PDF p4 |
| `ev_T4_rereview_singh_2026_soil_texture_1` | `soil_texture` | `practice_technology` | retained; reviewer_ok=true | PDF p4 |

### 17. `yadav_2024`

Yadav, Neelesh; Rakholia, Shrey; Yosef, Reuven (2024). A Prototype Decision Support System for Tree Selection and Plantation with a Focus on Agroforestry and Ecosystem Services. Forests.

**Triage:** Narrow tree-species selection; two retained weights still generic.

**Original-artifact check:** PDF opening abstract and methods pp5–6; Table2 group context and current p7 records inspected.

**Finding:** The model groups tree species by climate and soil preferences, not by agroforestry practice. Three retained records already carry species_specific, but retained precipitation and SOC importance weights still carry practice_technology. The dropped SOC response was excluded for species_envelope and should remain preserved for a deliberate reclassification review.

**Recommended follow-up:** Review ev_t4_precip_yadav24_5 and ev_t4_soc_yadav24_6 for species-selection model-use scope and linkage to the correct model. Do not treat their weights as practice suitability responses. Any reopening of ev_t4_soc_yadav24_3 must use the normal explicit retag-and-review path; never silently reinstate it during family cleanup. Generic selection methods need no invented single taxon, while group-specific responses must retain their actual source groups. No F1–F5 reassignment resolves this scope issue.

Artifact: `.cache/corpus/yadav_2024.pdf` in the original checkout. SHA256: `bf34f774195ab2df40faf1d92c8f0dacce61638763f26ebe7a7e85f2e91fc61a`.

| Evidence ID | Variable | Current claim scope | Current status | Locator |
|---|---|---|---|---|
| `ev_t4_mat_yadav24_1` | `mean_annual_temperature` | `species_specific` | retained; reviewer_ok=true | PDF p7 |
| `ev_t4_mat_yadav24_4` | `mean_annual_temperature` | `practice_technology` | dropped | PDF p6 |
| `ev_t4_precip_yadav24_2` | `annual_precipitation` | `species_specific` | retained; reviewer_ok=true | PDF p7 |
| `ev_t4_precip_yadav24_5` | `annual_precipitation` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_t4_soc_yadav24_3` | `soil_organic_carbon` | `practice_technology` | dropped | PDF p7 |
| `ev_t4_soc_yadav24_6` | `soil_organic_carbon` | `practice_technology` | retained; reviewer_ok=true | PDF p6 |
| `ev_t4_soildrain_yadav24_9` | `soil_bulk_density` | `species_specific` | retained; reviewer_ok=true | PDF p6 |

## Ordered follow-up and acceptance criteria

1. Open the source packets in the local review dashboard. For the four immediate candidates, show the source page/section, current quote, family/claim scope, role, existing review notes and the proposed interpretation together. Capture a separate scoped decision for each claim or explicitly linked group; do not overwrite earlier approvals or pending decisions.
2. Prepare an auditable source-identity correction for the duplicate South Asia paper. Preserve both discovery/acquisition routes, original source IDs as aliases, all EV IDs and their reviewers. Correct the mistaken citation from the source identity. Regenerate through the normal generator and confirm that known-source counts decrease by exactly one wherever both aliases were counted, with unchanged EV totals/history.
3. Resolve narrow applicability without proliferating duplicate evidence rows: one shared Baldwin claim may support F1 and F3, but it remains one source claim. Castle’s alley-cropping row must not become a universal land-cover gate. Species-model records should remain visible in their own lane, with their source-specific importance weights distinct from executable suitability calibration.
4. Resolve Haile’s planted-versus-retained parkland question through its cited field-characterisation source or an explicit expert synthesis decision. Until then label the missing distinction; do not hide it under “all families”. Other broad models need documented transfer decisions if used for a named family.
5. Recheck downstream support after any accepted changes: no duplicated independent-source votes, no new automatic approval, no global threshold from regional rankings, no accidental reactivation of dropped rows, and no altered pending review decisions. Keep source/EV IDs stable in dashboard deep links and feedback targets.
6. Close this bounded review only when all 17 source groups have a recorded disposition and every proposed mutation has its own review/audit trail. This report completes triage; it does not claim that these subsequent review decisions have been made.

## Verification of this report

Automated inventory check: 17 sections match the captured `source_keys`; 96 distinct EV IDs occur once in the per-source tables; 75 retained plus 21 dropped reconcile to the dashboard cohort. Every listed source has an artifact SHA256. The same-file duplicate was verified byte-for-byte. No new evidence, family metadata or review-state changes were made.
