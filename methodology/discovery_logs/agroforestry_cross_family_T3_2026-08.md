# Discovery log — Agroforestry · cross_family · T3

- Run `discovery_crossfam_homegardens_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 250 | 24 | 4 |
| updated_lit | 7 | 7 | 3 |
| grey | 16 | 10 | 4 |
| tool | 9 | 3 | 1 |

### Verbatim search terms

- **stock:** `OpenAlex title.search (cited_by desc): "agroforestry climate change adaptation"; "agroforestry microclimate"; "agroforestry drought resilience"; "trees on farms climate adaptation"; "agroforestry ecosystem services resilience"`
- **updated_lit:** `OpenAlex title.search + from_publication_date:2015-01-01 (cited_by desc): "agroforestry climate resilience adaptation"; "agroforestry drought heat buffering"`
- **grey:** `WebSearch EN: "agroforestry climate resilience buffering drought heat WOCAT FAO TECA technical guidance"; ES: "agroforestería resiliencia climática sequía sombra árboles manual técnico ICRAF World Bank"`
- **tool:** `WebSearch: "agroforestry suitability climate resilience model GitHub google earth engine script weights thresholds"; GitHub API repo tree + raw grep on saraheb3/AgroforestrySuitability_GEE`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `quandt_2017_kenya_flood_drought` | stock | oa | ok | high | The role of agroforestry in building livelihood resilience to floods and drought in semiarid Kenya — Ecology & Society, 163 cites, OA, LMIC (Kenya drylands). Directly cross-family T3: how AF buffers b |
| `verchot_2007_adapt_mitigation_af` | stock | paywalled | ok | high | Climate change: linking adaptation and mitigation through agroforestry — Mitig Adapt Strateg Glob Change, 784 cites, seminal (is_seminal). Cross-family framing of AF adaptation incl. microclimate/wate |
| `lin_2007_microclimate_extremes` | stock | paywalled | ok | high | Agroforestry management as an adaptive strategy against potential microclimate extremes — Agric & Forest Meteorology, 453 cites. Core T3 mechanism paper: shade/canopy buffering of temperature + moistu |
| `mbow_2013_cosust_mitig_adapt` | stock | oa | ok | med | Achieving mitigation and adaptation to climate change through sustainable agroforestry practices — COSUST, 725 cites, OA. Broad cross-family review; adaptation/resilience content is general but includ |
| `quandt_2023_cosust_adapt_gaps` | updated_lit | oa | ok | high | Climate change adaptation through agroforestry: opportunities and gaps — COSUST 2023, 186 cites, OA. Recent cross-family synthesis of AF hazard-adaptation evidence + gaps. Strong updated-lit anchor. |
| `af_drylands_adapt_resilience_2023` | updated_lit | oa | ok | high | Agroforestry practices for climate change adaptation and livelihood resilience in drylands — 2023, OA, drylands (drought/heat hazard context), LMIC tie-break. Cross-family. |
| `intercropping_af_adaptation_2022` | updated_lit | oa | ok | med | The deployment of intercropping and agroforestry as adaptation to climate change — Crop & Environment 2022, 133 cites, OA. AF-as-adaptation general; watch intercropping-only claims (not AF) at extract |
| `fao_af_extreme_weather_riskreduction` | grey | oa | ok | high | Global assessment of production benefits and risk reduction in agroforestry during extreme weather events under climate change scenarios — FAO. Directly T3: production risk-reduction during extreme we |
| `fao_practitioners_field_guide_af_resilience` | grey | oa | ok | med | Practitioner's field guide: agroforestry for climate resilience — FAO field guide, cross-family design/management for climate resilience. Grey guidance = expert_assertion basis; discount. |
| `cifor_icraf_agroforestry_primer` | grey | oa | ok | med | Agroforestry: a primer — design and management principles (CIFOR-ICRAF) — CIFOR-ICRAF primer (EN + ES editions). Cross-family; contains microclimate/moisture-buffering + windbreak general statements.  |
| `saraheb3_agroforestry_suitability_gee` | tool | repo | ok | low | AgroforestrySuitability_GEE — GEE MCDA agroforestry suitability tool (US Midwest) — commit af338e8251c6bde4fa46caccf4e92124f80d7623 (2025-01-15). Practice explicit (agroforestry MCDA, real code branch |

## Gaps / next iteration

Title-only OpenAlex search is weak for T3 mechanism papers (many buffering studies name the crop/system, not "agroforestry", in the title; "drought heat buffering" returned 0). A full-text/abstract sweep (OpenAlex abstract or Scopus) would recover more, and much cross-family hazard-buffering evidence is embedded in crop-specific studies that must be PICOS-screened at the row level (coffee/cocoa shade = F5, not cross_family). Grey lit is FAO/ICRAF-heavy and positive-biased -> apply COI/grey discount, especially to benefit-magnitude claims. Only one code-bearing agroforestry tool exists and it is US-Midwest T4-suitability with negligible genuine T3 content; no LMIC hazard-response tool found. Two strongest high-cite anchors (Verchot 2007, Lin 2007) are paywalled and queued for Namita-J. Wind/erosion-hazard buffering (windbreak function) is under-represented at cross_family level here because most wind evidence is windbreak-family-specific.
