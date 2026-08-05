# Discovery log — Forest Restoration · passive_regeneration · T3

- Run `forest_restoration_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** discovery + screening only. No extraction.
- **grey + tool = complete.** **stock + updated_lit = IN PROGRESS** — OpenAlex hit its daily budget (HTTP 429, resets midnight UTC); candidates below are provisional (WebSearch/canon fallback), to be finalised with real OpenAlex nets on rerun.

## grey + tool candidates (final)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `poscrptr_usgs` | tool | repo | ok | high | poscrptR - post-fire conifer regeneration prediction R package/shiny app — Hardcoded model predicts probability of post-fire natural conifer regeneration from precipitation + seed production/source +  |
| `regenmapper_usfs` | tool | other | ok | med | Regenmapper - natural tree regeneration potential DSS for burned areas — 30 m regen-probability maps driven by distance-to-mature-trees (seed source) + hydroclimate + climate suitability layers = NR-v |
| `cifor_nr_potential_flr_es` | grey | oa | ok | med | Claves para entender el potencial de la regeneracion natural para la restauracion de los paisajes forestales (CIFOR) — ES; CIFOR-ICRAF; NR potential for FLR in tropical/LMIC context. Save snapshot + l |
| `humboldt_nr_bosque_seco_es` | grey | oa | ok | med | Regeneracion natural en los bosques secos (Instituto Humboldt, Biodiversidad 2020) — ES; Colombia tropical dry forest — passive NR under drought/disturbance-exclusion; strong LMIC tie-break. |
| `yale_elti_nr_anr_library` | grey | oa | ok | med | Natural and Assisted Natural Regeneration (Yale ELTI Tropical Restoration Library) — Practice guidance distinguishing passive NR from ANR; documents barriers (fire, drought, weed competition, cattle)  |
| `iucn_restoration_drought_risk` | grey | oa | NO | low | Restoring Ecosystems to Reduce Drought Risk and Increase Resilience (IUCN project) — Restoration-as-drought-buffer framing but broad ecosystem restoration; passive-NR practice not explicit → PICOS wea |
| `fao_anr_portal` | grey | oa | NO | low | Assisted Natural Regeneration of forests (FAO) — Authoritative NR guidance but scope is ANR (F2), not passive F1; disturbance-exclusion (fire, grazing) content is relevant background. Do not tag as F1 |

## stock + updated_lit candidates (PROVISIONAL — OpenAlex pending)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `nat_rev_biodiv_nr_drivers` | updated_lit | paywalled | ok | high | Drivers and benefits of natural regeneration in tropical forests — 2025 review; NR practice explicit; synthesises resilience/benefit + barriers to regeneration incl. climate stress. Core T3 anchor for |
| `global_nr_potential_tropics` | updated_lit | oa | ok | high | The global potential for natural regeneration in deforested tropical regions — 30 m spatial NR-potential across tropical countries/biomes; T3 link = regrowth on higher-suitability sites is more resili |
| `mapping_global_forest_regen_iop` | updated_lit | oa | ok | med | Mapping global forest regeneration - an untapped potential to mitigate climate change and biodiversity loss — Global regen mapping; NR practice explicit but framing is mitigation/biodiversity, hazard- |
| `framework_species_nr_fire` | updated_lit | oa | ok | med | The framework species method: harnessing natural regeneration to restore tropical forest ecosystems — Contains explicit fire-resilience selection criterion (fire-prone N. Thailand trial) + drought-dri |
| `spruce_drought_succession` | stock | paywalled | ok | med | Increased sensitivity to drought across successional stages in natural Norway spruce (Picea abies) — Drought response across natural successional stages of unmanaged spruce = regeneration drought vuln |
| `sierra_planting_vs_natural_1978` | stock | paywalled | ok | low | A Comparison of Planting and Natural Succession After a Forest Fire in the Northern Sierra Nevada — Directly contrasts passive post-fire natural succession vs planting (hazard=fire). Old (1978), US te |

### Verbatim search terms (as run / attempted)

- **stock:** `OpenAlex title.search: (natural regeneration OR secondary succession) AND (drought OR fire) ; sort=cited_by_count:desc ; per_page=15`
- **updated_lit:** `OpenAlex title.search: (natural regeneration OR forest regrowth) AND (climate OR resilience) ; sort=cited_by_count:desc ; per_page=10 [budget cap prevented a from_publication_date:2015 date-sorted rerun; recent peer lit instead surfaced via targeted web search]`
- **grey:** `WebSearch EN: 'natural regeneration passive restoration drought mortality fire resilience seedling survival tropical secondary forest' | 'FAO IUCN natural regeneration restoration climate resilience drought fire guidance regeneration potential' ; ES/PT: 'regeneración natural bosque secundario sequía fuego resiliencia restauración pasiva regeneração natural incêndio seca'`
- **tool:** `WebSearch: 'github natural regeneration potential model code repository POSCRPT Regenmapper post-fire conifer regeneration probability' | 'WRI restoration diagnostic ROAM ... natural regeneration criteria github' | 'poscrptR github repository R package source code' ; WebFetch github.com/pderusso/poscrptR (404) + code.usgs.gov gitlab blob (403)`

## Gaps / next iteration

OpenAlex daily budget exhausted after 2 queries (resets midnight UTC) — the planned broader stock booleans and a date-sorted (2015-2026) updated_lit sweep did NOT run; rerun after reset to firm up retrieved counts. Title-only OpenAlex intersection of NR x hazard is noisy (fauna, post-fire weed/deadwood biodiversity, temperate single-genus stands) — genuine T3 signal for passive regeneration lives in tropical-forest-recovery lit + grey/tools, not high-cite title hits. Tool layer is US-temperate post-fire conifer only (poscrptR, Regenmapper); no LMIC/tropical passive-NR hazard-response code tool found — transferability caveat for the pilot. poscrptR code needs a GitLab code adapter to pin file:line of GLM coefficients + probability cutoff (WebFetch 403 blocked inline read); Regenmapper has no open source repo. F1/F2 boundary is pervasive: FAO and ELTI guidance and the framework-species paper are ANR (F2) — pure passive-F1 hazard evidence is sparser and must be segregated at extraction. Hazard coverage is skewed: fire-resilience and drought/desiccation mortality of regeneration are well represented; flood/erosion-control-by-restored-cover and wind are thin — targeted follow-up searches warranted."

---

## stock + updated_lit — FINALISED (OpenAlex online, run `fr_stocklit_finish_2026-08`, 2026-08-05)

Supersedes the provisional section above (OpenAlex was budget-blocked at first pass).

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 257 | 15 | 5 |
| updated_lit | 83 | 15 | 5 |

**Verbatim terms:**
- **stock:** `title.search:("natural regeneration" OR "secondary succession" OR "forest regrowth" OR "second-growth" OR "passive restoration") AND (drought OR fire OR resilience OR mortality OR disturbance)`
- **updated_lit:** `title.search:("natural regeneration" OR "secondary succession" OR "forest regrowth" OR "spontaneous regeneration") AND (drought OR fire OR resilience OR mortality),from_publication_date:2015-01-01`

**Screened-in (stock/lit):**

| source_id | process | access | rel | title / note |
|---|---|---|---|---|
| `tropdry_resilience_meta_2016` | stock | oa | high | Resilience of tropical dry forests – a meta-analysis of changes in species diversity and composition during secondary succession — Meta-analysis (diamond source class) of passive s |
| `drought_resist_succession_tdf_2012` | stock | oa | high | Drought resistance in early and late secondary successional species from a tropical dry forest: the interplay between xylem resistance to embolism, sapwood density and leaf morphol |
| `atlantic_rainforest_recovery_time_2008` | stock | paywalled | med | How long does the Atlantic Rain Forest take to recover after a disturbance? Changes in species composition and ecological features during tropical succession — Passive post-disturb |
| `fire_legacy_amazon_regrowth_2005` | stock | oa | med | Legacy of fire slows carbon accumulation in Amazonian forest regrowth — Fire hazard legacy effect on natural forest regrowth (Amazonia, LMIC). T3 fire-x-regeneration. Carbon-accumu |
| `sec_regrowth_resilience_slashburn_amazon_2005` | stock | paywalled | med | Resilience of secondary forest regrowth after slash-and-burn agriculture in central Amazonia — Passive regrowth resilience after fire/slash-and-burn disturbance (Amazonia, LMIC). T |
| `waterstrategy_succession_tropdry_2015` | updated_lit | oa | high | Exploiting water versus tolerating drought: water-use strategies of trees in a secondary successional tropical dry forest — Drought water-use / tolerance strategies across secondar |
| `postfire_restoration_deadwood_regen_2023` | updated_lit | oa | high | Post-Fire Restoration and Deadwood Management: Microsite Dynamics and Their Impact on Natural Regeneration — Restoration explicit; fire hazard x microsite conditions driving natura |
| `postfire_natregen_bolivia_trends_2023` | updated_lit | oa | high | Post-Fire Natural Regeneration Trends in Bolivia: 2001-2021 — LMIC (Bolivia), spatially-explicit 20-yr trends of post-fire natural regeneration. Fits T3 fire x passive regen with s |
| `fmnr_resilience_welfare_mali_2023` | updated_lit | oa | med | Impact of Farmer-Managed Natural Regeneration on Resilience and Welfare in Mali — LMIC (Mali, drylands). FMNR = low/no-planting natural-regeneration family; resilience outcomes und |
| `soilresp_resilience_drought_dieoff_succession_2016` | updated_lit | oa | med | Strong resilience of soil respiration components to drought-induced die-off resulting in forest secondary succession — Drought-induced die-off triggering secondary succession; ecos |
