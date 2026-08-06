# Discovery log — Riparian Buffers · planted · T6

- Run `riparian_buffer_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.1 · nbs_id `riparian_buffer`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 46 | 46 | 4 |
| updated_lit | 39 | 39 | 3 |
| grey | 34 | 34 | 4 |
| tool | 8 | 8 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search (cited_by_count desc): 'riparian buffer nitrogen phosphorus'; 'riparian buffer sediment removal efficiency'; 'vegetative filter strip water quality'; 'riparian buffer meta-analysis nitrogen removal'; 'riparian buffer effectiveness agricultural'; 'riparian buffer carbon sequestration'; 'vegetative filter strip sediment trapping efficiency'; 'cost riparian buffer conservation program'`
- **updated_lit:** `OpenAlex title.search + from_publication_date:2015-01-01 (cited_by_count desc): 'riparian buffer water quality'; plus recency filter applied to the stock strings above`
- **grey:** `WebSearch (EN): 'USDA NRCS riparian forest buffer conservation practice standard 391 cost nutrient removal'; 'FAO riparian buffer zone guidelines nutrient sediment water quality agriculture'; 'WOCAT riparian buffer strip SLM technology water quality erosion'; 'EU CAP GAEC buffer strip along watercourses width requirement 2023 nitrates directive'`
- **tool:** `WebSearch + GitHub API: 'InVEST nutrient delivery ratio riparian buffer retention model GitHub natcap'; 'GitHub riparian buffer siting suitability GIS MCDA stream network python tool'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `mayer_2007_n_removal_meta` | stock | paywalled | ok | high | Meta-Analysis of Nitrogen Removal in Riparian Buffers — Seminal (621 cites) quantitative synthesis of N-removal vs buffer width/vegetation/subsurface-vs-surface flow. Core T6 nutrient-removal-efficien |
| `dosskey_grass_shrub_2007` | stock | paywalled | ok | high | Grass-Shrub Riparian Buffer Removal of Sediment, Phosphorus, and Nitrogen From Simulated Runoff — Planted grass-shrub buffer; measured sediment/P/N trapping efficiencies. Grass-vs-woody parameter evid |
| `stutter_eu_rivers_np_2013` | stock | oa | ok | high | Reduction of nitrogen and phosphorus loads to European rivers by riparian buffer zones — OA. Basin-scale N & P load reduction by riparian buffers; both nutrients + EU policy context. Directly fetchabl |
| `desosa_tropical_agri_buffers_2018` | updated_lit | oa | ok | high | Riparian buffers in tropical agriculture: Scientific support, effectiveness and directions — LMIC/TROPICAL tie-break winner (150 cites). Synthesises buffer effectiveness for WQ/sediment/biodiversity i |
| `wu_buffer_length_v_width_2021` | updated_lit | repo | ok | med | Riparian buffer length is more influential than width on river water quality — Recent design-parameter evidence (length vs width) informing buffer geometry for WQ gain. Green OA repo copy; no direct P |
| `valera_buffer_capacity_anthropogenic_2019` | updated_lit | oa | ok | med | The Buffer Capacity of Riparian Vegetation to Control Water Quality in Anthropogenic Catchments — OA (MDPI). WQ control by riparian vegetation across land-use gradient; supports buffer WQ-gain outcome |
| `fortier_poplar_buffer_carbon_2010` | stock | paywalled | ok | med | Nutrient accumulation and carbon sequestration in 6-year-old hybrid poplars in multiclonal riparian buffers — Carbon + nutrient-accumulation outcome for planted woody buffers. Covers the carbon T6 out |
| `usda_nrcs_cps391_riparian_forest_buffer` | grey | oa | ok | high | USDA-NRCS Conservation Practice Standard 391 - Riparian Forest Buffer (+ Overview & cost job sheet) — Authoritative practice standard: up-to-90% nitrate removal (non-tile-drained), forested>grassed fo |
| `fao_sfm_tb11_conservation_riparian_buffer` | grey | oa | ok | med | FAO SFM Toolbox TB11 - Use of conservation riparian buffer to preserve water quality — FAO technical brief: design + maintenance for WQ; cites ~20 m buffer removing ~91-100% N (73-study meta). Interna |
| `wocat_6204_vegetative_riparian_buffers` | grey | oa | ok | high | WOCAT SLM Technology #6204 - Vegetative riparian buffers — WOCAT diamond source: standardised SLM tech record (establishment/maintenance costs, benefits, LMIC-grounded). Directly maps to T6 cost + ben |
| `eu_cap_gaec4_buffer_strips` | grey | oa | ok | med | EU CAP 2023-27 GAEC 4 buffer strips along watercourses (+ cross-compliance Std 5.2 effectiveness) — Policy/adoption + design-width rule: 3 m (slope <=12%) / 5 m (>12%), no PPP/fertiliser. Adoption-pro |
| `invest_ndr_natcap` | tool | oa | NO | low | InVEST Nutrient Delivery Ratio (NDR) model - natcap/invest — Nutrient-retention engine; riparian buffer is a biophysical-TABLE parameterisation, NOT a hardcoded buffer-width branch. picos_ok=false pen |

## Gaps / next iteration

COVERAGE: Strong temperate T6 nutrient/sediment-removal evidence (Mayer meta = anchor; grass-vs-woody parameter well served) + one high-value tropical synthesis (de Sosa 2018) satisfying the LMIC tie-break. Cost served mainly at grey-lit grade (NRCS 391 job-sheet, WOCAT cost fields, EU CAP); no peer-reviewed cost-per-km / cost-per-unit-pollutant-removed source surfaced (only W2511507407 floodplain-cost, not screened in). GAPS: (1) LMIC quantitative removal-efficiency + $/km data remain thin - tropical/Brazil/Africa title searches returned 0; recommend a next-round full-text or Portuguese/Spanish body search (Brazil Forest Code APP riparian, Uruguay Santa Lucia surfaced via WOCAT). (2) Biodiversity/habitat T6 outcome under-sampled in this sweep (WQ-dominant); a targeted 'riparian buffer bird/macroinvertebrate biodiversity' pass advised. (3) Carbon covered only by temperate hybrid-poplar studies (Ontario/Quebec) - no tropical buffer-carbon. (4) Nitrous-oxide pollution-swapping (W2890954121, saturated buffers) noted as a disbenefit worth capturing in T6. TOOL: no dedicated buffer-siting GIS-MCDA repo exists; InVEST NDR needs a code-dive to confirm whether any buffer param is hardcoded (likely table-driven -> no extractable claim). SATURATION: stock N/P/sediment reached saturation (~top-cite results recurring across query variants); updated_lit and grey stopped at cap, not exhaustion.
