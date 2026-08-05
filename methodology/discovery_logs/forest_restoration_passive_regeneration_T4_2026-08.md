# Discovery log — Forest Restoration · passive_regeneration · T4

- Run `forest_restoration_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** discovery + screening only. No extraction.
- **grey + tool = complete.** **stock + updated_lit = IN PROGRESS** — OpenAlex hit its daily budget (HTTP 429, resets midnight UTC); candidates below are provisional (WebSearch/canon fallback), to be finalised with real OpenAlex nets on rerun.

## grey + tool candidates (final)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `iucn_wri_roam_handbook_2014` | grey | oa | ok | high | A guide to the Restoration Opportunities Assessment Methodology (ROAM) (IUCN & WRI, 2014) — Canonical grey methodology for restoration-opportunity mapping incl. managed/natural regeneration; defines o |
| `fao_flr_mechanism_restoration_opportunities` | grey | oa | ok | med | FAO Forest and Landscape Restoration Mechanism - Assessment of degradation / restoration opportunities — FAO guidance on identifying degraded/deforested land suitable for restoration incl. managed nat |
| `elti_yale_natural_assisted_regeneration` | grey | oa | ok | med | Natural and Assisted Natural Regeneration - Yale ELTI Tropical Restoration Library — Practitioner synthesis of site conditions determining where passive NR vs ANR is appropriate (remnant seed sources, |
| `wri_iucn_atlas_flr_opportunity` | tool | other | ok | high | Atlas of Forest Landscape Restoration Opportunity (WRI/IUCN) - methodology & data — TOOL/product with hardcoded classification thresholds: wide-scale restoration = pop density <10/km2 + former closed  |

## stock + updated_lit candidates (PROVISIONAL — OpenAlex pending)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `williams_2024_global_natreg_potential` | updated_lit | oa | ok | high | Global potential for natural regeneration in deforested tropical regions (Williams et al., Nature 2024) — BEST T4 candidate. Spatially explicit 30m model of natural-regen potential across tropical for |
| `crouzeilles_2020_targeted_natreg` | updated_lit | oa | ok | high | Achieving cost-effective landscape-scale forest restoration through targeted natural regeneration (Crouzeilles et al., Conservation Letters 2020) — Predicts/maps natural-regen potential over 75.5 Mha  |
| `chazdon_guariguata_2016_natreg_flr` | stock | paywalled | ok | high | Natural regeneration as a tool for large-scale forest restoration in the tropics: prospects and challenges (Chazdon & Guariguata, Biotropica 2016) — Seminal synthesis of the conditions/limiters govern |
| `crouzeilles_2017_natreg_vs_active_success` | stock | oa | ok | med | Ecological restoration success is higher for natural regeneration than for active restoration in tropical forests (Crouzeilles et al., Science Advances 2017) — Meta-analysis; primarily effectiveness ( |
| `poorter_2016_biomass_resilience_secondary` | stock | paywalled | ok | med | Biomass resilience of Neotropical secondary forests (Poorter et al., Nature 2016) — Secondary-succession recovery rates driven by water availability/rainfall across 45 Neotropical sites - biophysical  |
| `strassburg_2020_global_priority_restoration` | stock | paywalled | ok | high | Global priority areas for ecosystem restoration (Strassburg et al., Nature 2020) — Multicriteria spatial optimisation (PLANGEA) for restoration priority across biomes - method template for opportunity |
| `cookpatton_2020_regrowth_carbon_map` | updated_lit | paywalled | ok | med | Mapping carbon accumulation potential from global natural forest regrowth (Cook-Patton et al., Nature 2020) — Global 1km natural-regrowth (passive regeneration) rate map from environmental covariates  |
| `brancalion_2019_restoration_hotspots` | updated_lit | oa | ok | high | Global restoration opportunities in tropical rainforest landscapes (Brancalion et al., Science Advances 2019) — Multicriteria restoration-hotspot mapping in tropical rainforests combining benefits+fea |

### Verbatim search terms (as run / attempted)

- **stock:** `OpenAlex title.search=("natural regeneration" OR "passive restoration") AND (forest OR tropical) sort=cited_by_count:desc [BLOCKED - OpenAlex budget $0 until midnight UTC]; fallback WebSearch: 'natural regeneration passive restoration tropical forest suitability spatial prioritization regeneration potential'`
- **updated_lit:** `OpenAlex title.search=("natural regeneration" OR "spontaneous regeneration") AND (potential OR suitability OR predict), from_publication_date:2015-01-01 [BLOCKED - OpenAlex budget $0]; fallback WebSearch: 'Crouzeilles targeted natural regeneration cost-effective landscape restoration mapping regeneration potential' + 'natural regeneration deforested tropical Nature 2024 Williams'`
- **grey:** `WebSearch EN: 'FAO WRI IUCN assisted natural regeneration restoration opportunity mapping guidelines where suitable degraded land'; multilingual ES/FR/PT: 'regeneración natural restauración bosque potencial mapeo áreas prioritarias / régénération naturelle forêt cartographie'`
- **tool:** `WebSearch: 'github natural regeneration potential mapping restoration opportunity suitability model code repository'; 'Strassburg PLANGEA github OR Crouzeilles regeneration potential model code github'; WebFetch github.com/search repositories + WRI Atlas methodology page`

## Gaps / next iteration

BLOCKER: OpenAlex API is hard-rate-limited this session ('Insufficient budget', $0 remaining, resets midnight UTC) - NO true retrieved totals or cited_by ranking obtained for stock/updated_lit. All counts are WebSearch fallbacks. ACTION: rerun the two OpenAlex boolean queries after budget reset (or add funds) to (a) confirm real retrieved totals, (b) surface any high-cite papers missed by WebSearch, (c) recency-rank updated_lit.\n\nTOOL process is thin: no public code repository with hardcoded regeneration-potential weights/thresholds was located/pinnable (GitHub search via WebFetch returned 0 usable results - SPA render limitation, not confirmed-empty). The strongest tool (WRI/IUCN Atlas) exposes thresholds only at doc level, not file:line+commit_sha. Williams et al. 2024 (Nature) and Strassburg PLANGEA analysis code are almost certainly archived on Zenodo/GitHub but were not found this session - needs a direct Zenodo/data-availability lookup + commit pin before any tool-source EV extraction. Recommend a follow-up GitHub/Zenodo pass (query author handles: brookewilliams, hlbeyer, IIS-Brazil, TNC) run with `gh` rather than WebFetch.\n\nFAMILY-BOUNDARY watch for extraction: several sources conflate passive NR with assisted NR (ANR) - Crouzeilles 2020 and ELTI explicitly split them; keep passive-NR (F1) rows distinct from ANR, and route ROAM/Atlas soft success-factors (tenure/finance/governance) to operational_risk/M2b, NOT T4. Cook-Patton 2020 sits near the pure-carbon-accounting exclusion line - retained because it is a spatial regen-potential model, but flag on extraction.\n\nMultilingual grey (ES/FR/PT) surfaced regional priority-mapping studies (Mexico Veracruz, Bolivia) not yet screened in depth - a targeted LMIC grey pass could add 2-3 system_constraint candidates.

---

## stock + updated_lit — FINALISED (OpenAlex online, run `fr_stocklit_finish_2026-08`, 2026-08-05)

Supersedes the provisional section above (OpenAlex was budget-blocked at first pass).

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 197 | 15 | 3 |
| updated_lit | 101 | 15 | 4 |

**Verbatim terms:**
- **stock:** `title.search:("natural regeneration" OR "passive restoration" OR "secondary succession" OR "forest regrowth") AND ("potential" OR "predict" OR "suitability" OR "recovery") | sort=cited_by_count:desc | OpenAlex`
- **updated_lit:** `title.search:("natural regeneration" OR "passive restoration" OR "spontaneous regeneration" OR "second-growth forest") AND ("potential" OR "predict" OR "suitability" OR "spatial") ,from_publication_date:2015-01-01 | sort=cited_by_count:desc | OpenAlex`

**Screened-in (stock/lit):**

| source_id | process | access | rel | title / note |
|---|---|---|---|---|
| `cook_patton_2020_mapping_regrowth_potential` | stock | paywalled | high | Mapping carbon accumulation potential from global natural forest regrowth — Cook-Patton et al. 2020 Nature. Global 1-km map of natural-regrowth potential - directly a regeneration- |
| `meli_2017_landuse_climate_active_passive_recovery` | stock | oa | high | A global review of past land use, climate, and active vs. passive restoration effects on forest recovery — Meli et al. 2017 PLoS ONE (gold OA). Meta-analysis of how prior land use  |
| `cloud_forest_active_vs_passive_pasture_2018` | stock | paywalled | med | Active versus passive restoration: Recovery of cloud forest structure, diversity and soil condition in abandoned pastureland — Ecol. Eng. 2018. LMIC (Neotropical) prior-land-use (a |
| `chazdon_2016_secondgrowth_carbon_latam` | updated_lit | oa | high | Carbon sequestration potential of second-growth forest regeneration in the Latin American tropics — Chazdon et al. 2016 Science Advances (gold OA). Spatially explicit second-growth |
| `williams_2024_global_natregen_potential_deforested` | updated_lit | oa | high | Global potential for natural regeneration in deforested tropical regions — Williams et al. 2024 Nature (hybrid OA). Global map of where natural regeneration is likely to succeed in |
| `crouzeilles_2016_natregen_biodiversity_spatial_planning` | updated_lit | paywalled | high | Natural regeneration and biodiversity: a global meta-analysis and implications for spatial planning — Crouzeilles et al. 2016 Biotropica. Global meta-analysis linking natural-regen |
| `landuse_dynamics_carbon_secondgrowth_2017` | updated_lit | oa | med | Land-use dynamics influence estimates of carbon sequestration potential in tropical second-growth forest — Environ. Res. Lett. 2017 (gold OA). Prior land-use dynamics as a determin |
