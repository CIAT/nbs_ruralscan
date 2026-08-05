# Discovery log — Forest Restoration · assisted_regeneration · T4

- Run `forest_restoration_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** discovery + screening only. No extraction.
- **grey + tool = complete.** **stock + updated_lit = IN PROGRESS** — OpenAlex hit its daily budget (HTTP 429, resets midnight UTC); candidates below are provisional (WebSearch/canon fallback), to be finalised with real OpenAlex nets on rerun.

## grey + tool candidates (final)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `fao_anr_manual_philippines` | grey | oa | ok | high | Advancing Assisted Natural Regeneration (ANR) / ANR Approach to Forest Restoration (FAO SFM Toolbox + Philippines manual) — FAO ANR manual/guidelines: explicit site-selection criteria for ANR (high na |
| `cifor_icraf_natregen_potential_flr` | grey | oa | ok | high | Keys to understanding the potential of natural regeneration for forest landscape restoration / Natural regeneration on abandoned land as a restoration strategy (CIFOR-ICRAF, Chazdon et al.) — CIFOR-IC |
| `wri_flr_atlas_roam_methodology` | grey | oa | ok | med | Atlas of Forest Landscape Restoration Opportunities + Restoration Opportunities Assessment Methodology (ROAM), WRI/IUCN — Grey methodology: potential tree cover (climate/soils/ecoregions) minus actual |
| `wri_brasil_rna_mata_atlantica` | grey | oa | ok | med | Estudos mostram potencial da Regeneração Natural Assistida na Amazônia e Mata Atlântica (WRI Brasil) + Pacto pela Restauração da Mata Atlântica — PT/LMIC. Reports mapping of natural-regen potential ov |
| `replant_alfa_gee_r` | tool | oa | ok | med | RePlant Alfa: Integrating Google Earth Engine and R Coding to Support the Identification of Priority Areas for Ecological Restoration — MDPI Land 2023, OA. GEE+R semiautomatic restoration-prioritisati |
| `wri_flr_atlas_tool` | tool | oa | ok | med | WRI Atlas of Forest Landscape Restoration Opportunities (interactive GEE/Blue-Raster app) — Interactive tool with hardcoded criteria: >=10% potential canopy threshold + population-density class breaks |
| `usfs_regenmapper` | tool | oa | ok | low | Regenmapper / REGEN MAPPER: web tool predicting post-fire conifer regeneration & prioritising reforestation (USFS) — Predicts natural regen potential from distance-to-live-seed-source + hydroclimate = |

## stock + updated_lit candidates (PROVISIONAL — OpenAlex pending)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `williams_2024_global_natregen_potential` | updated_lit | oa | ok | high | Global potential for natural regeneration in deforested tropical regions — Nature 2024 (W4403921242, 90 cites, OA). Maps 215 Mha regen potential across deforested tropics from spatial predictors -> th |
| `drivers_benefits_natregen_tropical_2025` | updated_lit | oa | ok | high | Drivers and benefits of natural regeneration in tropical forests — 2025 review (W4409638709, OA). Synthesises the spatial/biophysical drivers that determine WHERE natural regen delivers = direct T4 re |
| `sahel_fmnr_drivers_2020` | updated_lit | oa | ok | med | Drivers of farmer-managed natural regeneration in the Sahel. Lessons for restoration — 2020 (W3086938851, 76 cites, OA). Managed/assisted natural regen, LMIC (Sahel) -> regen-potential + system_constr |
| `crouzeilles_2016_natregen_biodiversity_meta` | stock | paywalled | ok | high | Natural regeneration and biodiversity: a global meta-analysis and implications for spatial planning — Biotropica 2016 (W2554309037, 75 cites). Global meta-analysis explicitly framed for spatial planni |
| `anr_automating_tropical_2016` | stock | paywalled | ok | med | The potential for automating assisted natural regeneration of tropical forest ecosystems — Biotropica 2016 (W2554814657, 49 cites). ANR practice explicit; discusses spatial targeting/identification of |
| `landscape_regen_after_disturbance_2018` | stock | paywalled | ok | med | From the stand scale to the landscape scale: predicting the spatial patterns of forest regeneration after disturbance — Ecol Appl 2018 (W2806045623, 110 cites). Spatial prediction of regen (distance-t |

### Verbatim search terms (as run / attempted)

- **stock:** `OpenAlex title.search sort=cited_by_count:desc per_page=12 mailto ; Q1=("assisted natural regeneration" OR "natural regeneration") AND (potential OR suitability OR mapping OR spatial) ; Q2=("natural regeneration" OR "forest regeneration") AND (predict OR drivers OR probability OR likelihood)`
- **updated_lit:** `OpenAlex filter=from_publication_date:2015-01-01,title.search:... sort=cited_by_count:desc ; Q3=("assisted natural regeneration" OR "managed natural regeneration") AND (restoration OR degraded OR tropical) ; Q4=("restoration potential" OR "regeneration potential" OR "restoration opportunity") AND (map OR mapping OR spatial OR suitability)`
- **grey:** `WebSearch EN: 'FAO assisted natural regeneration guidelines suitability where ANR appropriate site selection restoration' ; 'WRI restoration opportunities atlas assessment methodology natural regeneration potential mapping suitability' ; 'World Bank forest restoration natural regeneration where suitable degraded land spatial prioritization diagnostic tool' ; ES: 'regeneración natural asistida restauración bosque potencial dónde aplicar criterios sitio CIFOR' ; PT: 'regeneração natural assistida restauração floresta potencial mapeamento aptidão Brasil Pacto Mata Atlântica'`
- **tool:** `WebSearch: 'natural regeneration potential mapping GitHub Google Earth Engine restoration suitability model code seed source distance remnant forest' ; 'RePlant Alfa Google Earth Engine restoration priority areas GitHub code repository weights criteria' ; 'Regenmapper natural regeneration potential distance seed source model code repository' ; GitHub API repositories q=natural+regeneration+potential+restoration / restoration+priority+earth+engine / assisted+natural+regeneration (sort=stars)`

## Gaps / next iteration

SEARCH-COVERAGE GAPS: (1) OpenAlex dedicated recent (Q3/Q4 date-filtered) + planned ES/FR/PT title-only runs were BLOCKED by HTTP 429 (daily budget exhausted, resets midnight UTC; WebFetch fallback also 429). updated_lit candidates were harvested from the recency subset of the successful stock Q1/Q2 runs - re-run Q3/Q4 and add PT/ES title booleans (e.g. 'regeneracao natural' AND (potencial OR restauracao)) next window to confirm totals and catch the Brazil literature. (2) The Brazil natural-regen-potential prediction paper behind WRI-Brasil/Pacto (75.5 Mha modelled; likely Crouzeilles/Molin ~2019-2020) is not yet pinned to a DOI - targeted OpenAlex/Scholar pull needed; strong LMIC T4 regen-potential source. TOOL-LANE GAP: no interrogable public source repo located for ANY named tool (RePlant Alfa, WRI FLR Atlas, USFS Regenmapper) - GitHub API returned 0 relevant repos. Per the tools-are-sources rule, EV extraction (commit sha + file:line of weights/thresholds/masks) is BLOCKED until a repo/commit is located; screened-in as candidates only. WRI Atlas has quotable hardcoded criteria (>=10% canopy, pop-density class breaks) but from methodology docs, not code. SCOPE FLAGS: sahel_fmnr_drivers mixes T4 regen-potential with soft enabling-env drivers (tenure/governance) -> extract ONLY biophysical/system_constraint as structural_suitability; route soft factors to use_role=operational_risk/M2b. Regenmapper is US temperate post-fire (low LMIC transferability). Williams_2024 Nature likely ships a global regen-potential raster + driver model = candidate T4 BIND dataset AND a tool-lane artifact - inspect its data-availability/Zenodo next.

---

## stock + updated_lit — FINALISED (OpenAlex online, run `fr_stocklit_finish_2026-08`, 2026-08-05)

Supersedes the provisional section above (OpenAlex was budget-blocked at first pass).

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 258 | 30 | 6 |
| updated_lit | 214 | 30 | 5 |

**Verbatim terms:**
- **stock:** `title.search:("assisted natural regeneration" OR "natural regeneration") AND (restoration OR degraded)  [+ complementary run: ("forest restoration" OR "forest landscape restoration") AND (regeneration OR suitability OR prioritization)]  sort=cited_by_count:desc`
- **updated_lit:** `title.search:("assisted natural regeneration" OR "natural regeneration") AND (restoration OR degraded OR potential),from_publication_date:2015-01-01  [+ complementary run: ("forest restoration" OR reforestation) AND (suitability OR prioritization OR "seed source" OR "remnant forest"),from_publication_date:2015-01-01]  sort=cited_by_count:desc`

**Screened-in (stock/lit):**

| source_id | process | access | rel | title / note |
|---|---|---|---|---|
| `gonzalez_targeted_anr_2020` | stock | oa | high | Achieving cost-effective landscape-scale forest restoration through targeted natural regeneration — Gold OA. Core T4: spatially targets WHERE natural regeneration is the cost-effec |
| `vieira_principles_nat_regen_dry_forest_2006` | stock | repo | high | Principles of Natural Regeneration of Tropical Dry Forests for Restoration — Green OA (seminal, 518 cites). Conditions/limiting factors governing natural regen success (seed source |
| `shono_anr_degraded_tropical_2007` | stock | paywalled | high | Application of Assisted Natural Regeneration to Restore Degraded Tropical Forestlands — Seminal ANR practice paper (295 cites). ANR barrier-removal + site conditions where ANR viab |
| `chazdon_natregen_tool_flr_2016` | stock | paywalled | high | Natural regeneration as a tool for large-scale forest restoration in the tropics: prospects and challenges — Top-cited (694) seminal anchor. Frames biophysical/landscape conditions |
| `orsi_mcda_prioritize_restoration_2017` | stock | oa | high | Multicriteria decision analysis for prioritizing areas for forest restoration — Diamond OA. MCDA prioritization = T4 method-side; criteria include regeneration/connectivity/degrada |
| `holl_stimulating_natregen_degraded_2013` | stock | paywalled | med | Stimulating Natural Regeneration of Tropical Forest on Degraded Land: Approaches, Outcomes, and Information Gaps — Degradation-gradient threshold: when natural regen stalls -> acti |
| `crouzeilles_global_natregen_potential_tropics_2024` | updated_lit | oa | high | Global potential for natural regeneration in deforested tropical regions — Hybrid OA, 2024, 90 cites. THE regeneration-potential mapping paper: spatial predictors of where natural  |
| `chomba_fmnr_opportunities_constraints_ssa_2020` | updated_lit | oa | high | Opportunities and Constraints for Using Farmer Managed Natural Regeneration for Land Restoration in Sub-Saharan Africa — Gold OA, LMIC (SSA). FMNR = ANR variant; biophysical opport |
| `barros_mcda_prioritize_restoration_amazon_2022` | updated_lit | paywalled | high | Multicriteria approach to prioritize forest restoration areas for biodiversity conservation in the eastern Amazon — LMIC (Amazon) MCDA prioritization; criteria layers relevant to T |
| `elliott_automating_anr_tropical_2016` | updated_lit | paywalled | med | The potential for automating assisted natural regeneration of tropical forest ecosystems — ANR practice explicit; more method/remote-sensing than suitability thresholds. Medium T4  |
