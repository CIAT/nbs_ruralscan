# Discovery log — Water Harvesting & Conservation · in_situ · T4

- Run `water_harvesting_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1 · nbs_id `water_harvesting_conservation`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 442 | 15 | 6 |
| updated_lit | 81 | 15 | 3 |
| grey | 9 | 9 | 4 |
| tool | 2 | 2 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search: ("soil and water conservation" OR "rainwater harvesting" OR "planting pit" OR zai OR "tied ridge") AND (suitability OR siting OR runoff); sort=cited_by_count:desc; per_page=15`
- **updated_lit:** `OpenAlex title.search: ("soil moisture conservation" OR "soil and water conservation" OR "contour bund" OR "contour ridge" OR "planting pit" OR zai OR tassa OR "tied ridge") AND (suitability OR siting OR "site selection" OR runoff), from_publication_date:2015-01-01; sort=cited_by_count:desc`
- **grey:** `WebSearch EN: 'WOCAT soil and water conservation in-situ moisture conservation site selection suitability slope infiltration technology database'; 'FAO ICRISAT in-situ rainwater harvesting suitability manual slope soil runoff zai tied ridges site selection criteria drylands'`
- **tool:** `GitHub API repositories?q=<'rainwater harvesting suitability'|'curve number runoff GIS'|'soil water conservation suitability'|'AHP suitability raster'>&sort=stars; + WebSearch 'GitHub rainwater harvesting suitability GIS MCDA runoff SCS curve number script'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `adham2016_rwh_siting_review` | stock | oa | ok | high | Identification of suitable sites for rainwater harvesting structures in arid and semi-arid regions: A review — Diamond OA (Int Soil & Water Cons Research), 304 cites. Systematic review of biophysical  |
| `wolka2018_swc_ssa_meta` | stock | paywalled | ok | high | Effects of soil and water conservation techniques on crop yield, runoff and soil loss in Sub-Saharan Africa: A review/meta-analysis — 243 cites. In-situ/cross-slope SWC (bunds, tied-ridges) x slope-gr |
| `gismcda_swc_siting_2014` | stock | paywalled | ok | high | GIS-based multi-criteria evaluation to identify potential sites for soil and water conservation techniques — 159 cites. Directly SWC (in-situ family) siting via GIS-MCDA; weighted slope/soil/land-use/ |
| `kahinda2008_sa_rwh_suitability` | stock | paywalled | ok | med | Developing suitability maps for rainwater harvesting in South Africa — 199 cites. Distinguishes in-field (in-situ) RWH suitability from ex-field/storage; soil, slope, rainfall, land-cover criteria. Se |
| `kadam2012_scscn_india_rwh` | stock | paywalled | ok | med | Identifying Potential Rainwater Harvesting Sites of a Semi-arid, Basaltic Region of Western India, Using SCS-CN — 205 cites. SCS-CN runoff estimation + siting, semi-arid India drylands. Strong for run |
| `slope_swc_runoff_2013` | stock | repo | ok | high | Effects of land use, slope gradient, and soil and water conservation structures on runoff and soil loss in semi-arid — 201 cites, green OA (repo copy available). Quantifies slope-gradient x SWC-struct |
| `kordofan2024_insitu_rwh_gis` | updated_lit | oa | ok | high | GIS-Based Site Selection in North Kordofan, Sudan, Using In Situ Rainwater Harvesting Techniques — Gold OA (MDPI Hydrology, 2024). Explicitly in-situ RWH x GIS site selection in Sahelian dryland (Suda |
| `mojo2025_fuzzy_ahp_rwh` | updated_lit | oa | ok | med | Hydrological suitability analysis for rainwater harvesting using GIS-based fuzzy AHP: Mojo watershed, Ethiopia — OA (IWA Water Practice & Technology, 2025). Fuzzy-AHP membership + criterion weights fo |
| `landuse_swc_runoff_2020` | updated_lit | repo | ok | med | Assessing the impacts of different land uses and soil and water conservation interventions on runoff — Hybrid OA, 2020. Runoff response by land-use x SWC intervention -> runoff-generation + land-cover |
| `fao_wh_handbook_runoff_mgmt` | grey | oa | ok | high | FAO Water Harvesting handbook - Ch.1 Rainfall/runoff management techniques (Critchley & Siegert) — FAO OA. Canonical in-situ technique specs + siting rules: slope classes (0-5% very-high suited, tied- |
| `wocat_contour_trench_bund_1480` | grey | oa | ok | high | WOCAT SLM Technology #1480 - Contour Trench cum Bund — WOCAT QCAT structured record: in-situ contour bund/trench with per-technology slope, rainfall, soil-depth/texture applicability ranges = system_c |
| `wocat_swc_channels_uganda_711` | grey | oa | ok | med | WOCAT SLM Technology #711 - Soil and Water Conservation Channels (Uganda) — WOCAT structured in-situ SWC record; slope/water-retention applicability, LMIC (Uganda). Secondary WOCAT record for cross-so |
| `ibraimo2007_rwh_ssa_smallscale` | grey | oa | ok | med | Rainwater Harvesting Technologies for Small Scale Rainfed Agriculture in Arid and Semi-arid Areas (Ibraimo & Munguambe 2007) — OA PDF (WaterNet/Mozambique). Catalogue of in-situ techniques (tied-ridge |
| `gh_c_cn_calculator` | tool | repo | NO | low | C_CN_Calculator (agredo182) - runoff-coefficient / Curve-Number automation toolbox — BLOCKED / NOT included. Topically relevant (CN/runoff-coefficient feeds runoff-generation variable) but git tree at |

## Gaps / next iteration

TOOL process is the weakest lane: no acquirable GitHub repo exposes hardcoded in-situ RWH/SWC siting criteria (C_CN_Calculator commits no source; generic MCDA engines are NbS-agnostic and PICOS-excluded). The genuine hardcoded thresholds for this family live in GIS-MCDA suitability papers, so tool-lane evidence should be sourced from those rather than code. SCOPE-DIRECTION gap: most RWH siting literature optimises for HIGH runoff generation to feed storage structures, which is the OPPOSITE of in-situ logic (place on gentle LOW-runoff inter-stream slopes to hold rain where it falls) - need targeted evidence isolating in-situ placement rules and must screen out ex-situ/storage siting criteria at extraction. Drainage-geomorphology variables for in-situ (stream order, drainage density, proximity-to-channel behaving as an EXCLUSION for in-situ vs an inclusion for storage) and curvature/TWI thresholds are thinly and ambiguously evidenced. Quantitative Sahel zai/tassa slope+rainfall+soil envelopes under-represented in the retrieved set - recommend a targeted CGIAR/ICRISAT/CILSS grey sweep. GitHub unauth rate-limit truncated the tool sweep (retry authenticated to confirm absence). Grey positive-bias discount (WOCAT/FAO) must be applied at synthesis, especially to benefit-framed applicability ranges.
