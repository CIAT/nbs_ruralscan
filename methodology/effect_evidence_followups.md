# Effect-evidence follow-ups — pointers to useful material NOT yet in the registers

**What this is.** Extraction passes regularly meet claims that are useful but cannot be emitted *yet*: no
variable id in `VONT`, no T5 priority to route to, an unquotable text layer, an economics figure with no
denominator, or a role that was deferred at the time. Until now those pointers lived only in the per-batch
extraction reports under `pipeline/staging/` — which is **gitignored**, so they existed on one laptop. This
file is the tracked home for them, so a paper never has to be re-read to recover what was already found.

**What this is NOT.** Nothing here is evidence. No quote, page or number below may be copied into
`EV_*` / a recipe column — every entry must still go through the deterministic pipeline (cached artifact →
`retrieve` → page-stamped `EvidenceUnit` → gates). Entries are *where to look and why*, in the contract's
pointer shape `{source_id, page, claim_kind, outcome_raw, note}`.

**Resolution routes** (how an entry leaves this file): `VONT` id added → re-extract · T5 priority added →
XW route → synthesis picks it up automatically · column-aware PDF ingest / table screengrab (`/api/crop`)
→ re-extract · consumer decision (Namita M5 / Brayden M2b) → XW row.

**Lit-search targeting for T3/T6 (Pete, 2026-10-01).** Effect evidence should be sourced first from
**syntheses — meta-analyses, systematic reviews, evidence gap maps — and from project grey literature
(MEL and impact-assessment studies: WB ICR/IEG, CGIAR MELIA, 3ie, donor IEs)**; primary studies only to
fill cells the syntheses leave empty. The riparian pilot corpus below is mostly single HIC primaries and
shows why: most numbers fall outside the LMIC envelope. Reflect in the method §3 seed-set + the next
contract bump (`SRC.method_type = meta_analysis | systematic_review | mel_report | impact_assessment`).

---

## 1. riparian_buffer — T3/T6 pilot (ruleset v1.6.0, PR #264, 97 units ingested)

Source of these pointers: `pipeline/staging/riparian_effects_{A,B,C}_report.md` (local only), 2026-09-30.

### 1.1 Already in EV but routed nowhere (no T5 target) — decision needed, not re-extraction

| variable (VONT, pending_review) | units | why unmapped | route |
|---|---|---|---|
| `nutrient_removal` | 27 | no T5 water-quality priority (T5 v0.3.0 lock) | Namita/Pete: add a water-quality `priority` row to T5 (or a `descriptor`) → XW row |
| `stream_temperature` | 4 | same | same; could also route as a `component` of a fisheries/aquatic-biodiversity target |

These are riparian's *core* service; the scorecard is blind to it until this is decided.

### 1.2 Mapped to the closest id with `raw_name` set — fine for now, split if the ontology grows

| source_id | page | emitted as | actual outcome (`raw_name`) | suggested id |
|---|---|---|---|---|
| brazil_landuse_loworder_streams_2018 (Mello) | 6 | `nutrient_removal` | dissolved oxygen (r 0.47) | `dissolved_oxygen` |
| brazil_landuse_loworder_streams_2018 | 6 | `nutrient_removal` | fecal coliforms (r −0.47) | `microbial_water_quality` |
| brazil_landuse_loworder_streams_2018 | 6 | `sediment_retention` | organic suspended solids (r −0.55), low confidence | ok |
| brazil_landuse_loworder_streams_2018 | 6 | `nutrient_removal` / `sediment_retention` | **in-stream concentrations**, not removal efficiencies — sign reframed | synthesis/XW: treat as concentration proxies |
| latam_riparian_forest_buffers_2019 (Meli) | 2 | `biodiversity_outcome` | landscape connectivity | `habitat_connectivity` |
| latam_riparian_forest_buffers_2019 | 3 | `biodiversity_outcome` | physical habitat quality / riverbank continuity | proxy, ok |
| global_review_riparian_veg_restoration_2015 (González) | 9 | `biodiversity_outcome` | establishment success / vegetation recovery (frequent failure of planted species) | `establishment_success` |
| site_specific_vs_fixed_width_cost_2016 (Tiwari) | 7, 9 | `project_cost` | **opportunity cost** (forgone forestry NPV, USD/ha, boreal SWE) | T6 `economic_indicator_type` has no `opportunity_cost` member; XW sends `project_cost` → `establishment_cost` / `cost_per_hectare_restored`, neither semantically right |
| managing_buffer_strips_es_review_2020 (Cole) | — | `nutrient_removal` | pesticide / herbicide removal (Lin 2011 glyphosate +, soluble herbicide none) | `pesticide_removal` — VONT `nutrient_removal` is N/P only |
| multispecies_buffer_design_placement_1995 (Schultz); managing_buffer_strips_es_review_2020 | 13, 17, 20; — | `asset_vulnerability` with `variable=flood_hazard` | asset damage outcome (seedlings washed away; stems skinned; plants broken/uprooted) | contract §2.2.8 says use the hazard id; an `asset_damage` outcome id would make these cleaner |

### 1.3 NOT emitted — no VONT id (re-extract once an id exists)

| source_id | page | claim_kind | outcome_raw | note |
|---|---|---|---|---|
| multispecies_buffer_design_placement_1995 (Schultz) | 22 | nbs_effect | atrazine reduced across the MSRBS | needs `pesticide_removal` |
| rip_buffer_width_guidelines_review_2004 (Lee) | 8 | nbs_effect | large woody debris / organic-matter input to streams (McDade 1990: 30 m strip → 85 % of natural input; France 1996: 90 % drop after canopy harvest) | needs `lwd_input` or similar; cited_secondary |
| multispecies_buffer_design_placement_1995 | 1, 14–15 | nbs_effect | woody / grass biomass production (silver maple 8.4 Mg/ha over 4 yr; switchgrass 9.4 Mg/ha) | `carbon_sequestration` would be a silent proxy; mostly species-specific |
| latam_riparian_forest_buffers_2019 (Meli) | 3 | nbs_effect | seasonal stream drying / baseflow loss with riparian loss | needs `baseflow_regulation` / dry-season flow id |
| managing_buffer_strips_es_review_2020 (Cole) | 6 | nbs_effect | **N2O emission under nitrate saturation** (pollutant swapping in saturated buffers) | needs `ghg_emissions`; sign frame is a dis-benefit |
| managing_buffer_strips_es_review_2020 | 4–5 | nbs_effect | liver fluke / biosecurity / livestock shelter; pollination and pest-control services | no ids; out of the listed outcome set |
| managing_buffer_strips_es_review_2020 | 3 | nbs_effect | Wang 2018 narrow stiff-grass strips | dropped only to stay near the ~15/source cap |
| rip_buffer_width_guidelines_review_2004 | — | nbs_effect | Cote & Ferron 2001 null (small mammals) | dropped for the cap; De Groot 2002 carries the same null |
| rip_buffer_width_guidelines_review_2004 | — | — | fish-bearing-status as a width driver (from the T4 sweep, PR #242) | ontology triage (T4-side) |

### 1.4 NOT emitted — unquotable text layer (needs column-aware ingest or a table screengrab)

**grass_barrier_vfs_runoff_effectiveness_2004 (Blanco-Canqui 2004)** — two-column interleave; the paper's
*effectiveness* content is almost entirely here. Edge-of-field filter strips on 16-m plots, simulated rainfall,
Missouri claypan — **not stream-side** (transferability flag).

| page | outcome_raw | what is there |
|---|---|---|
| 1 (abstract) | runoff / sediment / nutrient reduction in first 4 m | 18 % runoff, 92 % sediment, 71 % nutrient |
| 1, 4 | runoff reduction, Fescue-FS vs B-Fescue-FS vs CCF | 11 % and 15 % (p 0.01); **no runoff unit could be emitted** |
| 4 | sediment trapping | 78 % Fescue-FS, 91 % B-Fescue-FS |
| 4–5 | cited Lee 1999: 3-m switchgrass barriers | sediment −69 % (switchgrass), −62 % (fescue) |
| 5 | 4-m strip | sediment −93 % both treatments |
| 5 | cited Gilley 2000: 0.8-m switchgrass barriers | 63 % trapped |
| 5 | 0.7-m Fescue-FS nutrient cuts | org-N 55 %, part-P 36 %, NO3-N 27 %, NH4-N 19 %, PO4-P 37 % |
| 5–6 | B-Fescue-FS nutrient cuts | org-N 67 %, part-P 53 %, NO3-N 68 %, NH4-N 50 %, PO4-P 54 % |
| 6 | 4-m strip nutrient cuts | ~58 % (Fescue-FS), ~71 % (B-Fescue-FS); NH4-N 58/79 %, part-P 68/84 %, PO4-P 62/72 % |
| 6 | cited Eghball 2000: 0.8-m barriers | org-N 57 %, NH4-N 81 %, NO3-N 33 %, part-P 68 % |
| 4 | runoff statements | no runoff difference Fescue-FS vs B-Native-FS; barriers improve infiltration in claypan |
| Table 1 | runoff (mm), sediment (Mg/ha) | header and rows not contiguous |

Other blockers:

| source_id | page | what |
|---|---|---|
| multispecies_buffer_design_placement_1995 | 11–12 | plantings withstood 155 cm rainfall (79 normal), 500-yr flood — page straddle (covered by p.17 unit) |
| multispecies_buffer_design_placement_1995 | 21–22 | nitrate result in body text — page straddle (covered by abstract unit) |
| neotropical_riparian_biodiversity_thresholds_2020 (Dala-Corte) | Table 1 | per-biome threshold rows beyond the first fish block — need whole-page slice |
| site_specific_vs_fixed_width_cost_2016 (Tiwari) | 5, Table 1 | per-scenario cost rows garbled one cell per line — screengrab |
| global_review_riparian_veg_restoration_2015 | 4→5 | Salix/Populus vs Tamarix competition — page straddle; species-specific anyway |
| managing_buffer_strips_es_review_2020 | 9, Fig. 2 | scored −2..+2 synthesis of width × vegetation type × service — figure-only; a `figure_read` pass |

### 1.5 Economics seen but unusable (no buffer-cost denominator)

| source_id | page | figure | why not |
|---|---|---|---|
| multispecies_buffer_design_placement_1995 | 3 | Des Moines >$4 M spent on nitrate filtration, weighing $13.5 M; Welsch 1991 $10–15/month per family of three | downstream treatment cost, not buffer cost |
| multispecies_buffer_design_placement_1995 | 7 | wider row spacing lowers establishment cost | no number |
| grass_barrier_vfs_runoff_effectiveness_2004 | 1 | "less-costly alternative to terraces" | no number; interleaved |
| grass_barrier_vfs_runoff_effectiveness_2004 | 1 | USEPA $44 billion degraded water resources | national total |
| latam_riparian_forest_buffers_2019 | 3 | ">5 km of stream banks in 59 plots", "2.8 ha … 14 farmers" | extents without cost |
| site_specific_vs_fixed_width_cost_2016 | 6 | discount rate | outside quoted spans; no `currency_year` anywhere |

### 1.6 Context caveats worth carrying into synthesis prose (not units)

- Mello 2018 p.7–8: watershed-scale forest mattered more than the 30 m riparian zone — a caveat on riparian-only attribution.
- Cole 2020: Osborne & Kovacic pair compares wooded vs **grass** buffers, not vs no buffer; cited primaries largely non-UK.
- Cole 2020 p.9: carbon 80 t ha⁻¹ yr⁻¹ printed as a rate but framed as storage capacity — implausible as sequestration (low confidence unit in EV).
- Lee 2004: treed buffers *retained after timber harvest* (forestry), tagged `planted` as instructed — transferability flag.
- Tiwari 2016: `climate_zone = boreal`, no T7 boreal AEZ; family fit (`planted`) needs a human call.
- Zhao 2013 is CHN (Liuxihe basin, Guangdong), not CAN — `SRC.study_country` fixed in PR #264; check it stuck.

### 1.7 PICOS exclusions (recorded so nobody re-screens them)

Schultz tile-outlet constructed wetland (nitrate >15 → <3 mg/L, p.1/23 — a *wetland_management* claim, not riparian; **pointer for the wetlands T3/T6 pass**) · Lee: logging / canopy-removal effects with no buffer as intervention (Carlson 1990, Noel 1986, France 1996, Steedman & France 2000), bank cover (Wesche 1987), partial harvest inside buffers · Zhao: NDVI ↔ N-uptake mechanism papers (Hively 2009) · Meli: Conservador das Águas +60 % forest cover, Nascentes >12,000 ha (programme outputs), La Vieja silvopastoral package results (+40 % stocking, −43 % agrochemicals) · González: passive vs active hydro-geomorphic cost-efficiency (dam/levee removal, not buffers) · Dala-Corte: catchment turbidity/nutrient effects (catchment land use, not riparian).

---

## 2. Pointers left by T4-only sweeps of other NbS (from PR bodies; the staging reports are gone)

| nbs_id | source_id | page | claim_kind | outcome_raw | note |
|---|---|---|---|---|---|
| forest_restoration | `reforest_water_yield_drought_risk_2022` | — | nbs_effect | reforestation's effect on water yield (basins screened on water stress >0.2, aridity <0.65, water-yield decline >5 %) | deliberately not extracted in PR #250; whole paper is effect material |
| forest_restoration | ~20 screened-in FR papers | — | nbs_effect | soil-carbon meta-analyses, sediment yield, biomass recovery | PR #250: "yielded nothing" for T4 — i.e. they are T3/T6 corpus; re-screen the FR discovery log for the meta-analyses first |
| wetland_management | most of the 12 screened-in wetland sources | — | nbs_effect | methane flux, nitrate removal, flood attenuation, fire reduction | PR #251: "overwhelmingly about what wetlands do" — the wetland T3/T6 corpus already exists in SRC |
| wetland_management | multispecies_buffer_design_placement_1995 (Schultz) | 1, 23 | nbs_effect | constructed tile-outlet wetland nitrate >15 → <3 mg/L | from the riparian pilot (PICOS exclusion there) |
| agroforestry | 87 T4-net + 105 unlogged (FMNR bundle) archived units | — | nbs_effect / climate_risk | see `schema/registers/_deferred/README.md` | **stay archived** per decision 9 ("if from T4 searches this was junk"); listed only so nobody re-migrates them by accident |

---

## 3. Process gap this file closes (proposal for the next contract bump, v1.6.x)

The v1.6.0 extraction contract (§6) puts deferred pointers, ontology-triage notes, denominator-less economics
and blockers in the **staging report** — which is gitignored. Proposed rule: the orchestrator copies those four
report sections into this file (per NbS section) in the same PR that ingests the units, and `/sweep-retro`
checks the file was touched. No ruleset bump needed to start doing it; the contract line changes at the next bump.
