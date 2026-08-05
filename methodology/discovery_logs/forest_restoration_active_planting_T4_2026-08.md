# Discovery log — Forest Restoration · active_planting · T4

- Run `forest_restoration_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** discovery + screening only. No extraction.
- **grey + tool = complete.** **stock + updated_lit = IN PROGRESS** — OpenAlex hit its daily budget (HTTP 429, resets midnight UTC); candidates below are provisional (WebSearch/canon fallback), to be finalised with real OpenAlex nets on rerun.

## grey + tool candidates (final)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `roam_iucn_wri_guide_2014` | grey | oa | ok | high | A guide to the Restoration Opportunities Assessment Methodology (ROAM) — OA. Canonical restoration-opportunity methodology (IUCN/WRI); LMIC pilots Ghana/Mexico/Rwanda. Distinguishes intervention types |
| `wri_atlas_flr_opportunity_methodology` | grey | oa | ok | high | Methodology & Data: Atlas of Forest Landscape Restoration Opportunity — OA. Global FLR opportunity classification (wide-scale vs mosaic vs remote) w/ documented masks/thresholds -> T4 system_constrain |
| `iufro_flr_practitioners_guide` | grey | oa | ok | med | Implementing Forest Landscape Restoration: A Practitioner's Guide (EN/ES) — OA, bilingual. Planting/active-restoration practice guidance + site-matching principles. Practitioner grey-lit; discount ben |
| `metodologia_areas_potenciales_restauracion_latam` | grey | oa | ok | med | Metodología de identificación de áreas potenciales locales para restauración y atributos para categorizar el escenario de referencia — OA, Spanish/LatAm LMIC. Local restoration-potential-area identifi |
| `tool_afforestation_tracker_gee` | tool | repo | ok | high | Afforestation-Tracker (Luk-kar) - GEE afforestation suitability, Sahel — Practice EXPLICIT (afforestation/tree planting). CODE-VERIFIED hardcoded planting-envelope thresholds: slope<15 deg, precipitat |
| `tool_groa_forc_db` | tool | repo | ok | low | GROA - Global Reforestation Opportunity Assessment (data+code) — R. Natural-regeneration carbon-accumulation dataset (Cook-Patton/TNC, Nature 2020). Reforestation practice explicit but PASSIVE/natural |
| `tool_scotland_reforestation_ml` | tool | repo | ok | low | Project-Scotland-Reforestation (ML planting-suitability) — EXCLUDED as extractable tool-source. Data-driven RF/XGB predicting planting scenarios; criteria/importances learned at runtime, no hardcoded  |

## stock + updated_lit candidates (PROVISIONAL — OpenAlex pending)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `cdm_afforestation_land_suitability_2008` | stock | paywalled | ok | high | Climate change mitigation: A spatial analysis of global land suitability for clean development mechanism afforestation and reforestation — Practice EXPLICIT (afforestation/reforestation). Global spati |
| `excessive_afforestation_arid_china_2010` | stock | paywalled | ok | med | Excessive reliance on afforestation in China's arid and semi-arid regions: Lessons in ecological restoration — Practice explicit. Do-no-harm / biophysical water-limit constraint: afforestation UNSUITA |
| `portfolio_theory_reforestation_climate_2008` | stock | paywalled | ok | med | Using portfolio theory to guide reforestation and restoration under climate change scenarios — Practice explicit; species/site selection under climate uncertainty -> target-community-as-parameter logi |
| `farmland_afforestation_hotspots_scotland_2007` | stock | paywalled | ok | med | Mapping hotspots of multiple landscape functions: a case study on farmland afforestation in Scotland — Afforestation spatial multi-criteria mapping; temperate but methodologically transferable. Closed |
| `flr_suitability_species_diversity_2024` | updated_lit | oa | ok | high | Suitability assessment for forest landscape restoration based on species diversity conservation — OA. FLR suitability assessment, recent. Confirm active-planting vs mosaic framing on read; suitability |
| `optimizing_afforestation_reforestation_degraded_2024` | updated_lit | paywalled | ok | med | Optimizing afforestation and reforestation strategies to enhance ecosystem services in critically degraded regions — Practice explicit; degraded-land targeting = system_constraint. Paywalled -> acquis |
| `suitable_areas_reforestation_indigenous_gis` | updated_lit | oa | ok | med | Determination of suitable areas for reforestation and afforestation with indigenous species — OA. GIS Boolean site-suitability (slope/aspect/soil pH/texture/EC/OM) for reforestation w/ indigenous spec |
| `geospatial_priority_restoration_slr_2025` | updated_lit | oa | ok | med | Geospatial Technologies-based Priority Forest Restoration Areas Identification: A Systematic Literature Review — OA preprint SLR of RS/GIS/MCA restoration-site criteria -> criteria/dataset catalogue f |

### Verbatim search terms (as run / attempted)

- **stock:** `OpenAlex title.search (curl): (reforestation OR afforestation) AND (suitability OR mapping OR spatial OR restoration) ; sort=cited_by_count:desc; per_page=15; mailto=p.steward@cgiar.org`
- **updated_lit:** `INTENDED (NOT RUN - OpenAlex budget exhausted): OpenAlex title.search: (reforestation OR afforestation OR "forest restoration") AND (suitability OR opportunity OR potential) AND (mapping OR spatial); from_publication_date:2015-01-01; sort=cited_by_count:desc. FALLBACK RUN (WebSearch): reforestation afforestation site suitability spatial mapping species selection restoration 2020..2026`
- **grey:** `WebSearch EN: FAO WRI IUCN restoration opportunity mapping reforestation suitability decision support methodology | WebSearch ES: reforestación restauración forestal aptitud sitio plantación especies mapeo áreas prioritarias FAO metodología`
- **tool:** `WebSearch: github restoration opportunity mapping reforestation suitability model regeneration potential earth engine | gh api search/repositories?q=afforestation+tracker+sahel | gh api search/repositories?q=restoration+opportunity+suitability+afforestation`

## Gaps / next iteration

OpenAlex updated_lit query was NOT executed: per-day API budget hit $0 after the single stock query (resets midnight UTC, retryAfter ~12h). RE-RUN the intended boolean [(reforestation OR afforestation OR \"forest restoration\") AND (suitability OR opportunity OR potential) AND (mapping OR spatial), from_publication_date:2015-01-01] after reset for a real recent total + high-cite recency ranking; current updated_lit candidates are WebSearch fallback only. Grey done EN+ES only - FR and PT NOT separately run (add FAO/CIFOR-ICRAF FR + Portuguese/Brazil Mata Atlantica restoration sources; Brazil is a major active-planting evidence base). WOCAT and Evidence Gap Maps (3ie/CEE) not yet queried for this family. Species/community-as-parameter: single-species SDM papers deliberately excluded (claim_scope=species) - a future species-level layer will need them; not this sweep. GROA belongs to the passive/ANR sibling family, not active_planting - ensure it is picked up there. No DOIs captured (OpenAlex metadata call blocked); acquisition_queue rows carry OpenAlex IDs for Namita-J to resolve. Afforestation-Tracker is the only code-verified tool; WRI restoration-diagnostic / IIASA GLOBIOM restoration modules not located as pinnable public code repos (ROAM/Atlas covered as grey methodology instead).

---

## stock + updated_lit — FINALISED (OpenAlex online, run `fr_stocklit_finish_2026-08`, 2026-08-05)

Supersedes the provisional section above (OpenAlex was budget-blocked at first pass).

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 79 | 30 | 4 |
| updated_lit | 41 | 27 | 5 |

**Verbatim terms:**
- **stock:** `title.search:(reforestation OR afforestation OR "restoration planting") AND (suitability OR prioritization OR "site selection") | sort=cited_by_count:desc`
- **updated_lit:** `title.search:(reforestation OR afforestation OR "restoration planting") AND (suitability OR "restoration opportunity" OR prioritization),from_publication_date:2015-01-01 | sort=cited_by_count:desc`

**Screened-in (stock/lit):**

| source_id | process | access | rel | title / note |
|---|---|---|---|---|
