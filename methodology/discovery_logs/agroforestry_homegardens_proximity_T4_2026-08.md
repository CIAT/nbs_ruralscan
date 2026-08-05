# Discovery log — Agroforestry · homegardens_proximity · T4

- Run `discovery_crossfam_homegardens_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 775 | 40 | 3 |
| updated_lit | 16 | 16 | 1 |
| grey | 25 | 12 | 3 |
| tool | 6 | 3 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search runs (cited_by_count desc): 'homegardens' (775); 'home gardens agroforestry' (48); 'homegarden diversity' (166); 'homestead agroforestry' (54); '(homegarden OR home garden OR homestead agroforestry OR compound farm) tropical' (487)`
- **updated_lit:** `OpenAlex title.search, from_publication_date:2015-01-01: 'homegarden suitability' (0); 'homegarden distance homestead' (0); 'homegarden spatial distribution mapping' (0); 'homegarden climate' (16); 'homestead agroforestry adoption' (1); 'home garden agroforestry tropical' (2015+) (1)`
- **grey:** `WebSearch EN: 'WOCAT tropical homegarden homestead agroforestry SLM technology suitability'; 'FAO home garden agroforestry establishment requirements climate soil rainfall tropical guidelines'; ES: '"home garden" OR "huerto familiar" agroforestería suitability requisitos climáticos altitud tropical'`
- **tool:** `WebSearch: 'home garden agroforestry spatial suitability mapping GIS GitHub'; GitHub repo inspection of saraheb3/AgroforestrySuitability_GEE`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `kumar_nair_2004_enigma` | stock | paywalled | ok | high | The enigma of tropical homegardens — Seminal review (558 cites). Characterises the humid-tropical distribution and homestead-centred structure of homegardens — directly supports T4 system_constraint ( |
| `fernandes_nair_1986_structure` | stock | paywalled | ok | high | An evaluation of the structure and function of tropical homegardens — Seminal structural typology (465 cites) spanning multiple tropical homegarden systems; defines the biophysical + settlement contex |
| `torquebiau_1992_sustainable` | stock | paywalled | ok | med | Are tropical agroforestry home gardens sustainable? — 204 cites; discusses ecological conditions under which homegardens persist (humid tropics, management intensity). Some biophysical-envelope signal |
| `climate_variability_homegardens_southasia_2018` | updated_lit | oa | ok | med | Climate variability and adaptation of Homegardens in South Asia: case studies from Sri Lanka, Bangladesh... — Multi-country (Sri Lanka/Bangladesh) study describing climatic context and rainfall/temper |
| `wocat_chagga_homegardens_1337` | grey | oa | ok | high | Chagga Homegardens [Tanzania] — WOCAT SLM Technology #1337 — WOCAT structured SLM record for a PICOS-clean tropical multistrata homegarden (Kilimanjaro). land_use=settlements; DB carries climate zone  |
| `wocat_agroforestry_homegardens_slm_pdf` | grey | oa | ok | med | Agroforestry and Home Gardens — Gender and Sustainable Land Management (WOCAT) — WOCAT thematic PDF: notes ~0.5 ha plots, tree-crop-livestock, 'applied close to the homestead as it demands close follo |
| `catie_huerto_familiar_ospina` | grey | oa | ok | med | El huerto familiar: algunas consideraciones para su establecimiento y manejo (CATIE) — Spanish-language CATIE establishment/management manual for Latin American huertos familiares; covers site-selecti |
| `fao_agroforestry_primer` | grey | oa | NO | low | FAO — Agroforestry systems: A primer / SFM Toolbox Agroforestry module — Names generic site-selection factors (climate, soil, drainage, sunlight, precipitation) and cites Javanese homegardens as an ex |
| `saraheb3_agroforestry_suitability_gee` | tool | repo | NO | low | saraheb3/AgroforestrySuitability_GEE (GitHub) — EXCLUDED (PICOS fail). Targets alley cropping/riparian buffers/silvopasture/windbreaks over US temperate land, 9 temperate tree species, county-level so |

## Gaps / next iteration

Structural gap: T4 SUITABILITY evidence for homegardens is genuinely scarce. Title-level OpenAlex queries for 'suitability', 'distance/homestead proximity', and 'spatial distribution mapping' all returned ZERO — the corpus is overwhelmingly OUTCOME literature (agrobiodiversity inventories, carbon stocks, nutrition/food-security, climate-adaptation case studies), not establishment/where-can-it-go rules. (1) BIOPHYSICAL_CONSTRAINT: only a broad, weakly-quantified humid-tropical envelope is documented; no crisp rainfall/temperature/altitude/slope thresholds specific to homegardens found in title screening (WOCAT #1337 structured fields are the best hope for numbers, pending live-page render). This echoes the open F1 climate-vars-redundancy question — for a settlement-gated practice the biophysical envelope may be near-non-binding. (2) SYSTEM_CONSTRAINT is the real driver: proximity to homestead/settlement is definitional (WOCAT 'applied close to the homestead'; Nair reviews), so the gating layer is a settlement/built-up distribution mask (e.g. GHSL/WSF built-up) rather than a climate niche — but NO source quantifies a proximity buffer distance (metres from dwelling); this needs expert elicitation (Namita) or extraction from WOCAT/case-study spatial descriptions. (3) HARD legal exclusions: none surfaced (homegardens on private homestead land rarely intersect protected-area masks) — expected. (4) TOOLS: no homegarden-specific spatial-suitability tool exists; the one agroforestry GEE tool is US-temperate, wrong practice set. (5) Recommend confirming WOCAT #1337 (and sibling homegarden WOCAT records) numeric fields at extraction as the primary quantitative T4 source, and flagging homegardens as a candidate 'applicability_zone' (settlement-proximity) rather than 'area_suitability' spatial_product_type.
