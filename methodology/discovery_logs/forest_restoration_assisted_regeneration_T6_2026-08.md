# Discovery log — Forest Restoration · assisted_regeneration · T6

- Run `forest_restoration_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** discovery + screening only. No extraction.
- **grey + tool = complete.** **stock + updated_lit = IN PROGRESS** — OpenAlex hit its daily budget (HTTP 429, resets midnight UTC); candidates below are provisional (WebSearch/canon fallback), to be finalised with real OpenAlex nets on rerun.

## grey + tool candidates (final)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `wri_2024_anr_24_case_studies` | grey | oa | ok | high | The Role of Assisted Natural Regeneration in Accelerating Forest and Landscape Restoration: Practical Experiences from the Field — WRI 2024 synthesis of 24 ANR case studies (15 Brazil, 9 elsewhere) —  |
| `fao_2019_anr_manual` | grey | oa | ok | high | Restoring forest landscapes through assisted natural regeneration (ANR) — practical manual — FAO 2019 ANR practice manual — practice thresholds (residual seedling/wildling density, protection/weeding  |
| `trilliontrees_wwf_2022_real_cost` | grey | oa | ok | high | Defining the Real Cost of Restoring Forests — Cost-focused grey directly serving T6 cost_per_ha_restored. Natural-regeneration cost ranges (~US$12-3,880/ha) vs active planting (US$105-25,830/ha), trop |
| `wri_brasil_rna_custo_beneficio` | grey | oa | ok | med | A regeneração natural assistida, seus benefícios e seu poder para dar escala à restauração (WRI Brasil) — PT-language LMIC (Brazil) ANR cost-benefit — tie-break value for LMIC context; ANR ~<1/3 cost  |
| `achmadnaufal_reforestation_site_assessor` | tool | repo | NO | low | reforestation-site-assessor (achmadnaufal) — site suitability scoring/MCDA for reforestation — Hardcoded weights (rainfall .20/slope .20/soil_depth .15/forest_proximity .20/road_proximity .10/degradat |

## stock + updated_lit candidates (PROVISIONAL — OpenAlex pending)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `crouzeilles_2017_sciadv_nr_vs_active` | stock | oa | ok | high | Ecological restoration success is higher for natural regeneration than for active restoration in tropical forests — Canonical high-cite global meta-analysis (133 studies, 115 landscapes, 1728 comparis |
| `williams_2024_global_natregen_potential` | updated_lit | oa | ok | high | Global potential for natural regeneration in deforested tropical regions — Spatial regeneration-potential model — directly operationalises the F2 dominant limiter (partial regeneration potential). Nat |
| `anr_dry_tropical_2024_diversity_carbon` | updated_lit | oa | ok | high | Restoring a dry tropical forest through assisted natural regeneration: enhancing tree diversity, structure, and carbon stock — ANR practice explicit. T6 outcomes: species survival rates (M. longifolia |

### Verbatim search terms (as run / attempted)

- **stock:** `OpenAlex title.search=("assisted natural regeneration" OR "managed natural regeneration") AND (restoration OR reforestation) sort=cited_by_count:desc [OpenAlex returned HTTP 402 'Insufficient budget', resets midnight UTC — counts NOT retrievable this run]; FALLBACK WebSearch="'assisted natural regeneration' restoration success survival rate cost per hectare tropical forest" + "natural regeneration versus active restoration cost-effectiveness meta-analysis Crouzeilles Chazdon"`
- **updated_lit:** `OpenAlex title.search=("natural regeneration" OR "secondary forest") AND (cost OR survival OR recovery) from_publication_date:2015-01-01 [OpenAlex HTTP 402 budget block — counts NOT retrievable]; FALLBACK WebSearch same session`
- **grey:** `WebSearch EN: "FAO WRI IUCN assisted natural regeneration guidelines cost restoration outcomes report"; PT/ES: "regeneración natural asistida restauración bosque costos supervivencia regeneração natural assistida floresta"`
- **tool:** `GitHub API repositories?q=natural+regeneration+potential+restoration | forest+restoration+suitability+mapping | restoration+opportunity+earth+engine | restoration+potential | reforestation+suitability | natural+regeneration+mapping (sort=stars); WebSearch "restoration opportunity mapping regeneration potential github suitability model ROAM restoration diagnostic"`

## Gaps / next iteration

OpenAlex was budget-blocked this run (HTTP 402 'Insufficient budget', resets midnight UTC), so stock + updated_lit have NO verified cited_by/total counts — re-run the two boolean queries after the UTC reset to backfill srch.retrieved and catch additional high-cite seminals (e.g. Crouzeilles et al. 2016 Nat Commun 'ecological drivers of forest restoration success'). ANR-specific open-source tooling is a real gap: authoritative restoration tools (IUCN/WRI ROAM, Restoration Diagnostic, WRI Atlas of FLR Opportunities) are methodology PDFs not open code, and GitHub yields only weak-authority generic reforestation scorers with no ANR branch — the Williams et al. 2024 natural-regeneration-potential model may have an associated repo worth a targeted tool follow-up. T6 cost evidence skews to Brazil/Atlantic-Forest and tropical grey lit; sparse on African/Asian ANR cost + on quantitative water/soil outcomes and cost_per_tCO2e for ANR specifically. Grey (WRI/FAO/WWF) needs the standard positive-bias discount on benefit/cost claims. Species-level survival figures (dry-tropical ANR paper) must route to claim_scope=species_specific, not the practice-level T6 surface. All web/PDF candidates still require cached snapshots + EV locators before any extraction.
