# Discovery log — Riparian Buffers · planted · T4

- Run `riparian_buffer_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.1 · nbs_id `riparian_buffer`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 388 | 15 | 4 |
| updated_lit | 54 | 15 | 4 |
| grey | 16 | 16 | 4 |
| tool | 8 | 8 | 0 |

### Verbatim search terms

- **stock:** `title.search:("riparian buffer" OR "buffer strip" OR "filter strip" OR "vegetated buffer" OR "riparian planting") AND (suitability OR siting OR placement OR width OR slope OR runoff) | sort=cited_by_count:desc`
- **updated_lit:** `title.search:("riparian buffer" OR "buffer strip" OR "filter strip") AND (siting OR placement OR suitability OR targeting OR width),from_publication_date:2015-01-01 | sort=cited_by_count:desc`
- **grey:** `EN: riparian buffer siting suitability GIS width guidance USDA NRCS FAO cropland runoff | ES: franja riberena vegetada zona buffer largura | FR: bande enherbee riveraine largeur | PT: mata ciliar largura (WebSearch)`
- **tool:** `InVEST NDR riparian buffer siting natcap; GitHub riparian buffer placement optimization slope flow-accumulation python; GIS-MCDA stream-network suitability (WebSearch + api.github.com)`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `rip_buffer_width_guidelines_review_2004` | stock | paywalled | ok | high | Quantitative review of riparian buffer width guidelines from Canada and the United States — Seminal (cited 376). Synthesises published buffer-WIDTH guidelines by function -> core T4 riparian-width env |
| `multispecies_buffer_design_placement_1995` | stock | paywalled | ok | high | Design and placement of a multi-species riparian buffer strip system — Directly F1 PLANTED multi-species buffer; design + PLACEMENT (zonal, stream-adjacent). Explicit practice. Paywalled -> queue. |
| `grass_barrier_vfs_runoff_effectiveness_2004` | stock | paywalled | ok | high | Grass Barrier and Vegetative Filter Strip Effectiveness in Reducing Runoff, Sediment, Nitrogen, and Phosphorus Loss — Grass filter-strip (grass-vs-woody parameter) vs adjacent-land runoff load (system |
| `buffer_width_extent_vegetation_review_1999` | stock | oa | ok | high | A review of the scientific literature on riparian buffer width, extent and vegetation — Free PDF on Missouri DNR site (no DOI). Width/extent/vegetation synthesis -> T4 width + planting envelope. Cache |
| `costa_rica_buffer_length_vs_width_2021` | updated_lit | oa | ok | high | Riparian buffer length is more influential than width on river water quality: a case study in southern Costa Rica — TROPICAL/LMIC tie-break keep (stocktake is temperate-heavy). Supports zonal_linear f |
| `site_specific_vs_fixed_width_cost_2016` | updated_lit | paywalled | ok | high | Cost of riparian buffer zones: a comparison of hydrologically adapted site-specific riparian buffers with traditional fixed widths — Variable/precision buffer SITING driven by hydrology vs fixed width |
| `effective_width_sediment_anfis_swat_2020` | updated_lit | paywalled | ok | med | Assessment of the effective width of riparian buffer strips to reduce suspended sediment in an agricultural landscape using ANFIS and SWAT models — Effective-width in AGRICULTURAL landscape (adjacent- |
| `optimal_width_nutrient_removal_chaohu_2018` | updated_lit | oa | ok | med | The optimal width and mechanism of riparian buffers for storm water nutrient removal in the Chinese eutrophic Lake Chaohu watershed — Agricultural lake watershed (China, LMIC-adjacent). Optimal-width  |
| `nrcs_cps_391_riparian_forest_buffer` | grey | oa | ok | high | USDA-NRCS Conservation Practice Standard 391 - Riparian Forest Buffer — Authoritative design standard: 3-zone widths (Zone1 >=15ft trees, Zone2 >=20ft, Zone3 grass filter where cropland sheet-flow), 5 |
| `epa_riparian_buffer_width_n_removal_2005` | grey | oa | ok | med | Riparian Buffer Width, Vegetative Cover, and Nitrogen Removal Effectiveness (EPA review) — Grey review of width x vegetation cover x N-removal. Grey-lit positive-bias discount applies to effectiveness |
| `fao_sti_franja_riberena` | grey | oa | ok | med | FAO STI Portal - Franja riberena (riparian strip innovation) — ES/LMIC framing: strips typically 10 m wide x 1 km along watercourses, native trees/shrubs/deep-rooted grasses; fixed vs variable/precisi |
| `franja_riberena_humedales_review` | grey | other | ok | low | Las franjas de vegetacion riberena y su funcion de amortiguamiento (conservacion de humedales) — Spanish-language riparian-buffer function review. LMIC-language coverage but conservation/wetland frami |
| `invest_ndr_natcap` | tool | repo | NO | low | InVEST Nutrient Delivery Ratio (NDR) model - natcap/invest — PICOS-FAIL as buffer-siting tool: NDR computes nutrient delivery via LULC retention params + DEM/flow; no buffer-siting/width/stream-proxim |
| `comola_landuse_optimizer` | tool | repo | NO | low | CoMOLA - Constrained Multi-objective Optimization of Land use Allocation — PICOS-FAIL: NbS-agnostic land-use optimizer (NSGA-II). Riparian reforestation is an external case-study application, not a ha |

## Gaps / next iteration

CORPUS SKEW: literature is temperate-heavy (US/Canada/EU) and dominated by width x effectiveness studies rather than spatial SITING/targeting. Only 2 LMIC/tropical hits surfaced (Costa Rica length-vs-width; China Lake Chaohu) - actively tie-break-kept; deeper tropical/LMIC search (Latin America 'mata ciliar'/'franja riberena', Sub-Saharan, SE Asia) still thin and needs a dedicated multilingual sweep. TOOL GAP: no purpose-built riparian-buffer-siting tool found with hardcoded buffer-width/riparian-slope/stream-order/proximity rules as a real code branch - InVEST NDR (nutrient delivery, not siting) and CoMOLA (NbS-agnostic optimizer) both PICOS-fail; the practice-specific parameterisation lives in guidance docs (NRCS-391) not code. GREY GAP: WOCAT/IWMI/CGIAR riparian-buffer-siting entries not surfaced by queries - worth a direct WOCAT SLM-database + IWMI query. FOOTPRINT: sources confirm zonal_linear framing (buffer length per stream-km; Costa Rica shows length>width) - good alignment, but explicit stream-network/stream-order gating thresholds are sparse in what was retrieved. F2 (existing riparian condition / regeneration potential) barely represented in this planted-focused pass - run a separate F2/regen search before treating riparian_buffer T4 as saturated.
