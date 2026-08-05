# Discovery log — Forest Restoration · passive_regeneration · T6

- Run `forest_restoration_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** discovery + screening only. No extraction.
- **grey + tool = complete.** **stock + updated_lit = IN PROGRESS** — OpenAlex hit its daily budget (HTTP 429, resets midnight UTC); candidates below are provisional (WebSearch/canon fallback), to be finalised with real OpenAlex nets on rerun.

## grey + tool candidates (final)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `trillion_trees_2022_real_cost` | grey | oa | ok | med | Defining the Real Cost of Restoring Forests — Grey (WWF/Trillion Trees), OA PDF. NR cost range ~US$14-1,400/ha vs active up to $34,000/ha; labour-driven N/S gradient. Indicative scoping cost anchor. G |
| `instituto_escolhas_2023_recuperacao_vegetal` | grey | oa | ok | med | Estrategias de Recuperacao da Vegetacao (Instituto Escolhas, 2023) — Grey, PT, OA PDF, Brazil (LMIC tie-break). Costs by recovery strategy incl regeneracao natural vs plantio. Multilingual quotes must |
| `wri_anr_cost_benefits` | grey | oa | NO | low | What is Assisted Natural Regeneration & How Does it Work? (WRI insight) — WRI web insight. ANR < 1/3 cost of tree planting; Brazil 21.6 Mha ANR saves US$90.6bn (77%). CAVEAT: ANR actively assists = si |
| `leec_seed_dispersal_mapper` | tool | repo | ok | low | LEEClab/seed_dispersal_mapper - phenomenological seed-dispersal / regenerability mapper (GRASS+Python) — Commit pinned (2017-07-17). NR practice explicit (seed dispersal as proxy for natural-regenerat |

## stock + updated_lit candidates (PROVISIONAL — OpenAlex pending)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `crouzeilles_2017_sciadv_success` | stock | oa | ok | high | Ecological restoration success is higher for natural regeneration than for active restoration in tropical forests — Sci Adv 2017, gold OA, 683 cites. Meta-analysis: NR vs active restoration success ac |
| `rozendaal_2019_sciadv_biodiv` | stock | oa | ok | high | Biodiversity recovery of Neotropical secondary forests — Sci Adv 2019, gold OA, 548 cites. Biodiversity recovery trajectories in naturally-regenerating secondary forests (2ndFOR network). T6 biodivers |
| `chazdon_2020_conl_targeted_nr` | stock | oa | ok | high | Achieving cost-effective landscape-scale forest restoration through targeted natural regeneration — Conserv Lett 2020, gold OA, 268 cites. Cost-effectiveness + spatial targeting of NR at landscape sca |
| `crouzeilles_2016_btp_nr_tool` | stock | paywalled | ok | high | Natural regeneration as a tool for large-scale forest restoration in the tropics: prospects and challenges — Biotropica 2016, closed, 694 cites (most-cited hit). Synthesis of NR outcomes/enablers/cost |
| `reid_2018_sciadv_selection_bias` | stock | oa | ok | med | Positive site selection bias in meta-analyses comparing natural regeneration to active forest restoration — Sci Adv 2018, gold OA, 175 cites. Methodological caveat on NR-vs-active outcome comparisons  |
| `williams_beyer_2024_nature_nr_potential` | updated_lit | oa | ok | high | Global potential for natural regeneration in deforested tropical regions — Nature 2024, OA via PMC. Reports NR cost US$12-3,880/ha vs active US$105-25,830/ha, and 23.4 Gt C (21.1-25.7) aboveground ove |
| `bukoski_2024_ncc_cost_effectiveness` | updated_lit | paywalled | ok | high | Cost-effectiveness of natural forest regeneration and plantations for climate mitigation — Nature Climate Change 2024, paywalled. NR vs plantation abatement cost; NR cheaper over ~46% of suitable area |
| `bernal_2018_carbon_removal_rates` | updated_lit | oa | ok | med | Global carbon dioxide removal rates from forest landscape restoration activities — OA (PMC). Natural-regeneration CO2 removal 9.1-18.8 t CO2/ha/yr in first 20yr, contrasted with plantations/agroforest |

### Verbatim search terms (as run / attempted)

- **stock:** `OpenAlex title.search: ("natural regeneration" OR "secondary forest") AND (restoration OR recovery); sort=cited_by_count:desc`
- **updated_lit:** `ATTEMPTED OpenAlex title.search:("passive restoration" OR "forest regrowth" OR "spontaneous regeneration") AND (carbon OR biodiversity OR recovery),from_publication_date:2015-01-01 AND title.search:("secondary forest" OR "natural regeneration") AND ("carbon sequestration" OR "aboveground biomass"),from_publication_date:2015-01-01 [BOTH BLOCKED: OpenAlex budget $0]. FALLBACK WebSearch: 'FAO natural regeneration cost per hectare forest restoration success rates carbon'`
- **grey:** `WebSearch EN: 'FAO natural regeneration cost per hectare forest restoration success rates carbon' | 'WRI World Resources Institute cost of natural regeneration versus active restoration per hectare' ; ES: 'regeneración natural bosque restauración costo por hectárea supervivencia carbono América Latina' ; PT: 'CIFOR ICRAF regeneración natural regeneração natural custo restauração florestal captura carbono'`
- **tool:** `WebSearch: 'github natural regeneration potential mapping model code repository tropical restoration opportunity' | 'WRI restoration diagnostic ROAM restoration opportunities assessment methodology github tool' | '"natural regeneration" potential github repository "seed dispersal" GRASS GIS Crouzeilles OR Chazdon code' ; GitHub API commits+tree for LEEClab/seed_dispersal_mapper`

## Gaps / next iteration

OpenAlex daily budget hit $0 after a SINGLE query, so only the stock process has a real API retrieved count (238); updated_lit true counts are outstanding - RERUN the two verbatim boolean+date OpenAlex queries after midnight-UTC reset to complete that row. Content gaps for F1 passive-regeneration T6: (1) cost_per_ha_restored figures that ISOLATE pure passive NR (most grey/lit lump passive NR with ANR - the ANR sibling scope keeps leaking into cost anchors); (2) survival/success rates conditioned on regeneration-potential drivers (remnant-cover %, seed-source proximity, prior land-use intensity) rather than pooled; (3) African/Asian LMIC outcome+cost evidence (surfaced set is Latin-America-heavy - Rozendaal/Chazdon/Brazil); (4) MEL/adoption evidence for passive-NR schemes (dis-adoption when land re-cleared) - none surfaced. Tool gap: no T6-outcome/cost tool with extractable hardcoded parameters - WRI ROAM/Restoration Diagnostic are handbooks (no code); seed_dispersal_mapper is T4 potential only. A carbon-accumulation-rate dataset/tool (Cook-Patton-style regrowth curves) was NOT verbatim-surfaced this pass and should be sought for cost_per_tCO2e. PICOS watch: exclude single-species SDM and enrichment-planting papers seen in the stock query tail.
