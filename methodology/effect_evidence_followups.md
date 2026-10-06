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

**RESOLVED 2026-10-01 (Pete):** T5 `water_quality_risk` added under `nbs_response` + XW routes (`nutrient_removal` direct · `stream_temperature`, `sediment_retention` component 0.7). The 31 units now feed `riparian_buffer__water_quality_risk` rows. Table kept for the record.

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

### 1.6b QA items raised by the prose-writer review (2026-10-01; `riparian_buffer_prose_report.md`, staging-only)

Engine template defects it found are FIXED in PR #270 (verb frame on risk targets · ISO3-only envelopes · AEZ naming
threshold · cost-row wording). Data items still open for a human:

| item | evidence | call needed |
|---|---|---|
| `ev_biodiversity_outcome_meli19_6` carries `MEX` only as the source default while citing González del Tánago & García de Jalón 2011 (Spain?) | Meli 2019 p3 | if the primary is European, blank `country` → the `income_group-upper_middle` scope row loses an `in_context` vote |
| Lee 2004 units are forest buffers **retained after timber harvest**, tagged `planted` | all `__planted__*` riparian rows | reclassify family (`natural_restored`? or a forestry-retention flag) — already listed in §1.6 |
| `ev_project_cost_tiwari16_2` (forgone-forestry NPV, USD/ha) feeds BOTH `establishment_cost` and `cost_per_hectare_restored` via `project_cost` XW routes | riparian economic rows | an `opportunity_cost` T6 indicator (enum gap, §1.2) or drop the two routes for retention-cost units |
| `ev_carbon_sequestration_cole20_1` — storage capacity printed as t ha⁻¹ yr⁻¹ | Cole 2020 p9 | keep direction-only (engine does); human check of the unit's `metric` |
| `riparian_buffer__asset_threat__flood` = "slightly damaged" rests on one cited mechanism statement; the other unit observed no damage | Cole 2020 (Puijalon/O'Hare) · Schultz 1995 p17 | fine at scoping grade; note for M2b (Brayden) |
| Loss-framed units (meli19_4 flood · dalacorte20_1 biodiversity · mello18_11 bank erosion) count toward agreement after the engine's sign flip | — | by design (contract `framing=loss`); prose conditionality names the framing |

Rows where the quotes give **no mechanism** (prose states only what the quote supports): natural_restored flood rows
(one loss-framed association), `planted__asset_threat__flood` (outcome, not process), both carbon rows, all four
economic rows. Rows resting mainly on `cited_secondary` lineage: all flood rows, asset-threat global/natural_restored,
all biodiversity rows (Lee 2004 / Cole 2020 reviews), carbon rows.

### 1.7 PICOS exclusions (recorded so nobody re-screens them)

Schultz tile-outlet constructed wetland (nitrate >15 → <3 mg/L, p.1/23 — a *wetland_management* claim, not riparian; **pointer for the wetlands T3/T6 pass**) · Lee: logging / canopy-removal effects with no buffer as intervention (Carlson 1990, Noel 1986, France 1996, Steedman & France 2000), bank cover (Wesche 1987), partial harvest inside buffers · Zhao: NDVI ↔ N-uptake mechanism papers (Hively 2009) · Meli: Conservador das Águas +60 % forest cover, Nascentes >12,000 ha (programme outputs), La Vieja silvopastoral package results (+40 % stocking, −43 % agrochemicals) · González: passive vs active hydro-geomorphic cost-efficiency (dam/levee removal, not buffers) · Dala-Corte: catchment turbidity/nutrient effects (catchment land use, not riparian).

---

## 1b. agroforestry — PR6 benchmark run over the 72 migrated units (2026-10-01)

Source: `schema/recipes/agroforestry/T3T6_synthesis_report.json` (tracked) + the PR4 migration notes.

### Unmapped (in EV, no XW route) — consumer decision

| variable | units | sources | route options |
|---|---|---|---|
| `beneficiaries` | 4 | WB FSRP / KCSAP PADs | T6 `cost_per_beneficiary` denominator (needs cost in the same row) or a `people_production` descriptor |
| `climate_shock` | 4 | Quandt 2017, Castle 2021 | generic "resilience to climate shock" — route as `proxy` to T3 `drought` / T6 `drought_hazard`? Namita/Brayden |
| `ecosystem_service` | 2 | Castle 2021 SR | too generic for a T5 target; keep as context |
| `adoption_rate` | 1 | Castle 2021 SR | adoption = observed-reality evidence → T6 `conditionality` text, not an effect |

### Economics seen but failing the §7.7 gates

| source_id | evidence_id | why |
|---|---|---|
| wb_fsrp_2022 | ev_t6_total_cost_fsrp22_1 | no numeric magnitude in quote |
| wb_kcsap_2016 | ev_t6_proj_cost_kcsap16_1 | `usd_million` programme total, no per-unit denominator |
| wb_fsrp_2022 / wb_kcsap_2016 | 8 component-cost lines (collapsed echoes) | programme totals; a `cost_per_beneficiary` row would need beneficiaries × cost from the **same** PAD table — table screengrab + a derived-denominator rule (not yet in contract) |

### Structural findings (why generated ≠ seed)

- **66/72 units have `strength_class = unspecified`** → engine floors every T3 row to `low` and most T6 rows to `slight_*`. Migrated v1.4.2 units carried direction only; a quote-bounded strength pass over the 5 sources (contract §4 BANDS) is the cheapest way to lift this — Castle 2021 (systematic review) and Quandt 2017 carry effect sizes in their quotes.
- **37/72 units (both WB PADs) are tagged `suitability_family_id = planted_silvoarable`** — PAD-level "agroforestry" claims are NbS-level, not F1. Migration default, flag for QA: should be blank (roll-up only) so they stop inflating the F1 family rows.
- Seed hazards with **zero evidence**: `waterlogging`, `heat_stress × cropping_irrigated`, `drought × tree_perennial`, `fire × pastoral_rangeland`, `wind_cyclone × cropping_rainfed` (windbreak) — targets for the synthesis-first search (meta-analyses on windbreak yield effects, shade × heat stress in perennial systems).
- Seed T6 rows with zero evidence: `carbon_sequestration_potential` (seed said strong_positive + carbon_revenue 20–200 USD/ha/yr), `accessibility_travel_time` (market access — seed had it as a T6 effect; by the 2026-06-23 routing it is M2b/next-steps, so the seed row was mis-placed anyway).

### PADs are not effect evidence (Pete, 2026-10-01 → applied 2026-10-02)

The 37 `nbs_effect` units from the two World Bank **Project Appraisal Documents** (`wb_fsrp_2022`, `wb_kcsap_2016`) were
design intent ("Sub-pillar 3.2 *will* support…"), mis-tagged `claim_basis = primary_measured`. A PAD is an ex-ante
investment proposal; it cannot evidence an effect. All 37 are **soft-dropped** (`review_state = dropped`, reason
`speculative_evidence`, note `ex_ante_pad`, reviewer `orchestrator`) — restorable. Agroforestry T3/T6 regenerated without
them: the "ETH, KEN, MDG" context and the two cost rows disappear; the remaining LMIC base is Castle 2021 + Quandt 2017.

| pointer | note |
|---|---|
| **KCSAP ICR** (project approved 2016 → Implementation Completion Report should exist) | the ex-post MEL replacement under the synthesis-first search rule; `method_type = mel_report` |
| FSRP (2022) | too young for an ICR; ISRs only — skip |
| PAD cost tables (programme totals, component budgets) | a possible *cost-expectations* lane (ex-ante budgets), never an effect; needs a per-unit denominator from the same table to be usable |
| `SRC.method_type` enum has no ex-ante value (`empirical` is wrong for a PAD) | add `project_appraisal` at the next spec bump; both SRC rows left as-is until then |
| ledger `agroforestry·T3/T6·grey` table-level rows | `verified` reset to `not_started` (no live grey units); the sub-practice grey rows were already `not_started` |

### QA items raised by the agroforestry prose-writer review (2026-10-02; `agroforestry_prose_report.md`, staging-only)

Engine fixes applied from this review: T6 hazard rows now read "reduces the impact of <hazard>" (the outcome is
livelihood resilience, not a smaller hazard); `transfer_class` share now uses pre-transfer weight with strict
majorities (one Kenyan + one US unit was `in_context` at 0.95 — now `mixed` at 0.5). Metadata fixed: Batcheler units
and SRC lose the wrong `aez = temperate_europe` (US study; T7 has no North-American AEZ — climate_zone `temperate`
kept); Quandt `_3`/`_4` (introduction sentences citing Lin 2007) → `cited_secondary` with lineage. Still open:

| item | evidence | call needed |
|---|---|---|
| `ev_t6_income_timebenefit_castle21_6` (Lower Nyando, 87.5 % after 4 yr) is very likely the same primary as Thorlakson & Neufeldt (`castle21s_3`, `_7`) | Castle p23 | set `lineage_of = Thorlakson & Neufeldt 2012` so `_dedupe_lineage` collapses the double count in `planted_silvoarable__rural_poverty` |
| `castle21_2` (soil-fertility yield), `castle21_6`, `batcheler24_9` are `cited_secondary` with blank `lineage_of` | — | fill lineage from the quotes' citations |
| `ev_crop_yield_castle21s_2` tagged `MOZ` while Castle's text says Nicaragua (Hegde & Bull 2011 is Mozambique — the review mis-states it) | Castle p21 | keep MOZ (true location); note recorded in the unit; prose names no country |
| `ev_economic_return_castle21s_4` (Indonesian social-forestry tenure permits) routed as an agroforestry → `rural_poverty` proxy | Castle p24 | XW/PICOS call: is a tenure-permit programme an agroforestry effect? Lean no |
| Quandt `_1` ("has been proposed…") still `primary_measured` with no citation in the quote; `mixed_crop_livestock` farming-system tag is the SRC default, not in the quotes | Quandt p2 | reviewer call on `_1`; FS tag acceptable as source default |
| `production_gap` "strongly reduces" rests on single-study SMDs (Haggar 3.85, Coulibaly +35 %) while both pooled estimates are ns | Castle | by design (ns units vote at ×0.5, direction only) — but worth stating in the Variable Card |

Rows where the quotes give **no mechanism**: all six flood rows (Quandt conclusion sentence only), Quandt-only drought
rows ("has been proposed"), Batcheler-only drought rows (infiltration listed as a service; drought never named), global
`production_gap` / `rural_poverty` (outcomes only).

### Synthesis-first discovery round 1 — agroforestry T3 + T6 (2026-10-02; probe + 3 agents; 75 candidates queued)

Logs: `methodology/discovery_logs/agroforestry_{T3_synthesis_probe,T6_synthesis,multilingual_T3T6,grey_mel_T3T6}_2026-10.md`.
SRCH: 7 rows (runs `probe_af_t3_2026-10-02`, `probe_af_t6_lit_2026-10-02`, `af_ml_2026-10-02` ×2, `af_grey_mel_2026-10-02` ×2).
Ledger: `updated_lit` T3/T6 = done (EN + ES/FR/PT saturated on OpenAlex/HAL); `grey` T3/T6 = in_progress.

**Coverage after round 1.** T6: carbon · yield · biodiversity · erosion · adoption have meta-analyses; income partial
(Jemaneh 2026 SSA welfare SR-MA); economics only now has per-unit costs (CRS: FMNR Ghana USD 66/hh · 58/ha vs planted
agroforestry Rwanda USD 201/hh · 1,387/ha — two families, so no range yet) plus Current et al. (21 projects, es) and
Brazilian NPV/IRR pools. **No synthesis anywhere** for yield stability, LMIC establishment/recurrent cost, BCR,
`agricultural_dependency`, `iplc_lands`, quantitative gender, water use. T3: drought + heat covered; frost 4 primaries
(incl. a NEGATIVE windbreak effect — cold-air pooling, Quénol & Beltrando 2006); wind China-only MA; flood proxy;
fire HIC; **project grey literature contributes ≈ nothing to T3** (two weak sources) and nothing on asset damage.

| pointer | note |
|---|---|
| **ERA — Evidence for Resilient Agriculture** (Rosenstock et al. 2024; Dataverse doi:10.7910/DVN/C3YBNN v1.0.1; R pkg `EiA2030/ERAg`) | HELD, not queued: CSV/R dataset = a format with no acquisition/locator rule → PAUSE and define a dataset-intake adapter (pin a commit/version; locator = table·row·column). **COI:** Pete + Namita are co-authors → independence-axis note when tiered |
| **Regreening Africa consolidated endline (Aug 2023)** | FOUND via Internet Archive (publisher link 404); 60 pp text layer OK; before–after only (impact comparison dropped); FIES 4.9→4.8 "no substantial change", SOC +0.31 g/kg, tree-product income flat USD 82 PPP/hh; **no drought-conditional outcome** → T6 only. Human: mirror the PDF to SharePoint |
| Untraceable web-summary numbers | "40 % fewer food-insecure months in drought" (attributed to the Regreening endline — NOT in it) and "25 % greater food security during drought in Kenya" (ICRAF news page; probably Thorlakson & Neufeldt 2012) — **never use**; extract only from cached text |
| IFAD (ifad.org 403 bot-check) | human browser download: DECOFOS Mexico impact assessment · IOE Burkina Faso SWC/agroforestry evaluation · "Strengthening agroforestry in rural investments" |
| Caquetá silvopasture DiD brief (Buriticá 2024) | directional only — find the working paper with coefficients |
| ~~IEG Ethiopia SLMP PPAR holds a GPP +14 % drought-buffering number~~ **WRONG — corrected 2026-10-04** | The extraction pass searched all 110 pp of the cached PPAR: **zero** occurrences of "gross primary production" / "GPP". The discovery agent read the sentence in the **GEF SCCE Drylands (2023) vol 1, printed p.32** (which cites IEG) and then asserted it "lives in the PPAR". The PPAR's geospatial work is pixel-level PSM+DiD on EVI/NDVI/LSWI (Table A.7, p.65) with **no drought split**, attributed to the whole SLM package. The claim is therefore **unverified and unusable** until the SCCE Drylands document is itself acquired and cached. **Lesson: a discovery agent's "this number is in document X" is a pointer, never provenance — only the extraction pass, reading the cached artefact, establishes where a number lives.** |
| Adoption syntheses (Stubblefield 2026, Sánchez 2026, Ribeiro 2022, Dias-Filho 2008) | drivers = soft enabling-environment factors → `operational_risk` (M2b / M6), not T6 effect rows; dis-adoption only in Sánchez |
| Mixed-practice syntheses (Basche 2019, Sileshi 2008, Félix 2018, Reed 2017, Haverhals 2016, Zheng 2020) | extract agroforestry rows only (exclude green manures, wood-chip, forest trees, grass hedgerows) |
| Crop-specific syntheses (Niether 2020 cocoa, De Beenhouwer 2013 coffee/cacao, Patil 2025 coffee) | `crop_specific` → shaded_perennial family only via `allow_crop_scope` |
| Title-anchored (DOI-less) items ×15 | WB/IEG/IPCC reports, Montagnini 2015, RIOCCADAPT ch.7, Current et al. (es), Robusti 2017, Dias-Filho 2008 — need `title_verified` after caching; RIOCCADAPT agroforestry section + Ferraz 2024 scope to confirm |
| Citations to repair by hand | Haverhals 2016 (Crossref swaps first/last names — fixed in queue), Ribeiro 2022 (blank first author in Crossref), IPCC chapters (author lists from front matter) |
| Protocol learnings | OpenAlex title search is accent-sensitive (`agroforestería` 188 vs `agroforesteria` 21) — run both forms; FR `haies` pulls English "hay" noise; SciELO/IFAD bot-block tools (reach SciELO via OpenAlex DOIs); Semantic Scholar rate-limits (429) |
| Positive-bias check (grey) | most independent sources (Regreening endline, SPIA Ethiopia) null/modest; implementer briefs (World Vision) most positive → apply the grey/COI discount in synthesis |

### Synthesis-first discovery PROBE, agroforestry × T3 (2026-10-02; 1 agent; log `methodology/discovery_logs/agroforestry_T3_synthesis_probe_2026-10.md`)

20 candidates queued (`pending`, tables T3). Hazard coverage after the probe: **drought 12 · heat_stress 10 · flood 8
(proxy-grade: runoff) · wind_cyclone 6 (windbreak meta-analysis China-only; cyclone damage primaries only) · fire 3
(HIC only) · frost 2 · waterlogging 2**. Asset damage: Watts 2022, van Noordwijk 2021, Colombia CMSCR ICR (new
silvopasture area −45 % in the 2019 drought), McGuigan 2024; nothing for fire/flood damage → `asset_risk_weight`
stays on the equal-weight fallback.

| pointer | note |
|---|---|
| **Regreening Africa consolidated endline report (Aug 2023)** | strong MEL candidate; PDF link 404, not on CGSpace; web summaries attach drought/food-insecurity figures that could not be traced to any document — **do not use those numbers**; acquire the real report via ICRAF/CIFOR-ICRAF library |
| Chausson et al. 2020 (GCB) | publisher PDF blocked at probe time — confirm which hazards its agroforestry slice covers before extraction |
| Ntawuruhunga et al. 2023 | confirm the CGSpace item carries a PDF |
| KCSAP ICR (ICR00006593, 2024) + IEG ICRR | **documents a gap, not an effect**: agroforestry = 395 acres of bundled sub-projects; resilience indicator = adoption of ≥1 practice; the 48.2 % drought-period productivity gain covers five value chains, none agroforestry; ICR Lesson 6 says resilience was not measured. Tier low; useful as T6 `conditionality`/M6 evidence on MEL design, not T3 |
| IPCC AR6 WGII Ch5 | Crossref returns no authors — confirm the author list from the PDF before the SRC row |
| ResearchGate-only candidates (Deniz 2023 · Singh & Lal 2018 · Caramori 1996 · McGuigan 2024) | human must confirm a full-text PDF exists (tool cannot) |
| **T6-relevant syntheses screened out of this T3 probe** | Kuyah et al. 2019 (ecosystem services meta-analysis) · Niether et al. 2020 (cocoa agroforestry meta-analysis) · Reed et al. 2017 (trees for food security) · the **ERA database** (CIAT Evidence for Resilient Agriculture) — first stop for the agroforestry T6 pass |
| Multilingual recall gap | AGROVOC ES/FR/PT synonym queries not run — add before the full search |
| Grey channels not yet worked | CGIAR impact assessments, GEF IEO, IFAD IOE, 3ie repository, WOCAT (adapter still PAUSED) |

**Scale-up estimate (from the probe):** full agroforestry T3 ≈ 25–40 sources; + T6 ≈ 20–35 more; ≈ 45–75 for
T3+T6 before the ~20-per-table cap. `updated_lit` saturated for EN syntheses on drought/heat/wind/fire; `grey` not
saturated.

### Castle 2021 strength pass (2026-10-01, +27 units, 5 superseded)

Castle et al. 2021 (Campbell SR) pools only **two** meta-analyses — crop yield (g 1.16 [−0.35, 2.67], ns) and household
income (g 0.12 [−0.06, 0.30], ns), both all-agroforestry; **no subgroup pooling by intervention type**. Every per-practice
result is a single included study → `cited_secondary` + `lineage_of` (the engine de-dupes to the primary). Family
attribution now carried on 20 units (planted_silvoarable 10 · shaded_perennial 7 [coffee, `crop_specific`, routed out of
practice cells] · silvopastoral 3); `linear_boundary`, `regeneration_farmland`, homegardens have **no isolating result**
in the review. Superseded (soft-dropped, `accepted_correction`, note `superseded_by=`): `ev_t6_yield_p20_castle21_3`,
`ev_t6_yield_meta_castle21_1` (abstract repeat), `ev_t6_income_meta_castle21_4`, `ev_t6_foodsec_dietary_castle21_7`,
`ev_t6_biodiv_esi_castle21_10` (ESI = biodiversity+carbon composite → `ecosystem_service`).

| pointer | page | note |
|---|---|---|
| Thorlakson soil-erosion × tree-biomass correlation (−0.31) | 25→26 | page-break straddle — unquotable; would be the only `erosion_hazard` unit from this review |
| Forest plots (Figs 6–7) per-study effect sizes | — | image-only; `figure_read` pass |
| Forest-cover loss (Sills) | 25 | no VONT id |
| Tree planting density, trees/ha (Pender) | 25 | no VONT id |
| Fuelwood purchases −49 pp, collection time −180 min (Thorlakson) | 26 | no VONT id (existing narrative unit `_12` holds it) |
| Tenure-security perception +26.4 % (Pender) | 24 | no VONT id (and tenure = M2b operational, not T6) |
| Gender-decomposed results | 27 | no VONT id; equity lane |
| Haggar per-certification-scheme yield/income SMDs (Utz, Fairtrade, RA, Organic) | 21–22 | numbers sit in kept quotes; emit as separate units only if per-scheme detail is wanted |
| Hegde & Bull country mis-stated as Nicaragua in the review (is Mozambique) · Coulibaly labelled improved fallows vs Table 4 fertilizer trees | 21 | source errors; units use MOZ / planted_silvoarable |

**Human family check still open:** the 8 kept pre-pass Castle units are all tagged `planted_silvoarable`; `_5`
(income pathway) and `_11` (ecosystem-service baseline) are pooled/narrative → should be `agroforestry__cross_family`.

---

### Prose-writer reviews of the regenerated agroforestry rows (2026-10-05) — engine fixes applied, data items open

Three writers (T3 · T6 + riparian · delta) reviewed 235 rows. **Engine defects they found, all fixed in the same PR:**
unknown context scored as in-context (129 units) · range-only magnitudes read as direction-only · proxy-only cells reaching
`very_high` (heat stress → `moderate`, `proxy_capped`) · hazard-silent units of a multi-hazard variable entering every
hazard cell · T6 hazard cells ignoring `hazard_type` · relative cost ratios and savings pooled into cost LEVEL cells
(the "USD 58–127/ha" range held a Colombia *saving*) · non-income scope rows ignoring the income target (Costa-Rica-only
`tree_perennial` row `in_context`) · one unit per source per cell (Rwanda cost arm and meta-analysis subgroups dropped) ·
engine `evidence_summary` lines failing the account check (`outcome_raw` numbers; `[lo, hi]` read as one number) ·
`claim_basis = primary_measurement` on 86 units (default weight, not counted as primary).

**Still open — data / QA calls (human):**
| item | detail |
|---|---|
| `ev_t3_wind_buffer_quandt17_4` | variable `windbreak_protection` on a quote about deep roots and floods/droughts — likely mis-tagged; lineage corrected to Kandji 2006 / Verchot |
| `ieg20_4` (Ethiopia SLMP stakeholder ratings) | a bundled land-management package result tagged `planted_silvoarable` (9 rows); `claim_basis` should not be primary — stakeholder ratings |
| `faosen24_6` | the English translation adds a soil-temperature sentence absent from the French quote — fix the translation (native text is fine) |
| gender units (Kiptot 2011) | 89 %, 23 %, 47 % are shares of households/participants, yet produce "strongly" classes on `gender_inequity`; the variable's direction semantics are unclear — reviewer call on whether these are effects at all |
| `basche19_1` | "perennials" class pools agroforestry with grasses/forestry — PICOS-weak; already `confidence = low` |
| `vannoordwijk21_2` cites Kuyah 2019 = `kuyah_2019` | lineage text ("Kuyah et al. 2019") cannot match the source_id, so dedupe misses the echo — a surname+year matcher for `lineage_of` ↔ `source_id` is the next engine step |
| `taboada20_3` / `seghieri19_9` in frost rows | now excluded unless `hazard_type = frost` is stated — confirm the extractors' hazard tags |
| flood asset row `watts22` "slightly damaged" vs quote "could significantly increase soil loss" | adjective, no number → weakest class by rule; fine, noted |
| Philpott 2008 hurricane | damage "stemmed from excessive rainfall, rather than wind" and the outcome is landslides — reviewer: `wind_cyclone` or `flood`? |
| Uriarte 2004 (via Philpott): complex vegetation *least* hurricane-resistant | the one asset-side unit contradicting "complexity = protection" — M2b Stream A |
| statement verb vs `magnitude_summary.class` can differ | the statement's class is the weighted modal strength over all quantified units; `magnitude_summary` is one metric/unit group — by design, but the Variable Card should explain it |

**Third review (delta writer, 2026-10-05) — fixed in-engine:** all-ns direction evidence → `no_relationship`; agreement
undefined (`low`) with one independent source; economic cells take an ordinal class from one source. **Confirmed fixed:**
Watts fire null now an asset row; context-less units adjacent; frost rows frost-only; Rwanda arm kept; Colombia saving and
the Steward cost ratio feed `cost_reduction` only; Tiwari units no longer fan into per-beneficiary / per-tCO₂e / recurrent rows.
**Still open (data / design):**
| item | detail |
|---|---|
| riparian envelopes list COL / CHN / MEX that no unit states | by design — SRC `study_country` fallback for units without a country (Meli: Brazil; Colombia; Mexico; Zhao: China) — fine, but the bundle should show the fallback so writers stop flagging it |
| Tiwari opportunity costs → `cost_per_hectare_restored` / `establishment_cost` | needs an `opportunity_cost` indicator (enum gap, §1.2) — XW decision |
| `batcheler24_6` (litter depth ↔ fire spread) counted against fire mitigation | a mechanism correlation, not an agroforestry effect — re-role or drop (QA) |
| Quandt general "agroforestry" units in `planted_silvoarable` rows; `quandt17_3` shade trees; Lee 2004 / Tiwari retained forest in riparian `planted__` | family tags not stated in the source — migration defaults; bulk re-tag to `cross_family` / `natural_restored` is a reviewer call |
| `watts22_14` climate-scenario sensitivity statement counted as a null poverty effect | QA |
| `seghieri19_13` adopter/non-adopter shares stored as a low/high range; `rgaf23_8` 31 % relative rise in a dietary-diversity share drives the rural-poverty magnitude | encoding semantics — reviewer call on whether shares are magnitudes |
| Quandt flood unit = a table caption only | re-slice to include the table rows (screengrab path) |
| statement "slightly" vs `magnitude_summary.class` strong (2 rows) | the two aggregates differ by construction; explain in the Variable Card or pick one — method decision |

## 1c. Agroforestry effect sweep — 4 extractor lanes over the 41 acquired sources (2026-10-04)

**348 units ingested** through the gated staging path (326 `nbs_effect` / `asset_vulnerability` + 22 `operational_risk`):
lane A T3-hazard syntheses 73 · lane B T6 meta-analyses 87 · lane C multilingual es/fr/pt 113 · lane D grey MEL 53 + 22
operational. Agroforestry T3 went 23 → **163 rows**, T6 12 → **71 rows**; 425 units pool into cells. Reports (staging,
gitignored): `pipeline/staging/agroforestry_effects_{A,B,C,D}_report.md`.

### A number that did not survive contact with the PDF
The grey *discovery* agent reported "GPP +14 % in severe-drought project areas vs +3 % elsewhere" as living in the IEG
Ethiopia SLMP PPAR and called it the strongest T3 drought signal of the grey pass. The extraction pass searched all
110 pp: **zero** hits for "gross primary production" or "GPP". The sentence was read in the **GEF SCCE Drylands (2023)
vol 1** (which cites IEG) and then attributed to the PPAR. Corrected in §probe and in the grey discovery log.
**Rule: a discovery agent's "this number is in document X" is a pointer, never provenance.** Only the extraction pass,
reading the cached artefact, establishes where a number lives. Two other widely-repeated agroforestry-drought figures
("40 % fewer food-insecure months", "25 % greater food security in Kenya") were likewise confirmed absent from the
documents they are attributed to.

### Register and engine gaps the sweep exposed (all fixed in this PR — ruleset note v1.6.1)
| gap | effect before | fix |
|---|---|---|
| No band for a response ratio | 19 units incl. RR 9.7 sat at `strength_class = unspecified` | BANDS gains `unit` + `centre`; `absolute`/`response_ratio` bands on \|RR − 1\| against the pct_change thresholds. No new metric, so the contract is unchanged |
| T3 cells ignored a unit's stated hazard | a variable routed to two hazards put every unit in both — the frost cell inherited 12 sources of daytime-shade evidence | units whose `context.hazard_type` differs from the cell are excluded (blank = applies, like `farming_system`). Frost 12 → **4 sources** |
| `_nums` comma-stripped locale decimals | `29,8` → `298`; ~15 % of es/fr/pt magnitudes unusable | decimal comma and thousands dot both read, alongside the plain reading |
| staging gate ≠ central guardrail | all 104 translated multilingual quotes failed the staging gate though `validate_sources` passed them | the gate strips the bracketed translation and compares numbers as floats |
| `operational_risk` had no gated path | 22 units would have needed a forbidden hand-append | `--allow-operational` on the staging ingest |
| `gender_inequity`, `wind_cyclone_hazard`, `waterlogging_hazard`, `livestock_productivity`, `forage_productivity`, soil/water mechanism variables had no XW route | units reached no cell | 10 XW routes added (ratification pending at PR review) |
| `livestock_productivity` / `forage_productivity` missing from VONT | the Colombia silvopasture milk/beef results and the Sahel fodder evidence were dropped rather than mislabelled | both ids added (`pending_review`); the 6 parked units ingested |

### Still open — human calls
| item | detail |
|---|---|
| **Ontology triage** | `tree_mortality` (6 asset units are squeezed into `tree_canopy_cover`), `tree_density`, `pest_disease_incidence` (4 pooled ORs from Patil 2025 unextractable), `infiltration_rate`, `available_phosphorus` (Kuyah RR 1.2 + 7 subgroups and Muchane RR 1.11 dropped), `aggregate_stability`, `livestock_thermal_comfort`, `fuelwood_availability` |
| **Unmapped variables** | `ecosystem_service` 10 · `climate_shock` 7 · `tree_canopy_cover` 5 · `beneficiaries` 4 · `adoption_rate` 2 · `rural_poverty` 2 (a T5 id used as a measured variable — contract forbids; re-tag to `household_income`) · `establishment_cost`/`recurrent_cost` 3 (economic ids used as `ev_variable`) · `landscape_forest_cover` 1 |
| **Economics still cannot fill a T6 cost cell** | the only denominated LMIC costs are CRS (FMNR Ghana USD 66/hh · 58/ha vs planted Rwanda USD 201/hh · 1,387/ha) — one source across two families, so the ≥2-independent-sources gate fails by design. Roe/IPCC give only the USD 100/tCO₂e *screening threshold*, recorded with an explicit "not a measured cost" note |
| **`asset_risk_weight` stays blank** | 5 of 7 hazards have asset-threat rows (no flood- or waterlogging-damage evidence), so M2b keeps the equal-weight fallback |
| **Family calls** | "improved/planted fallow" (IFPRI + lane B, 10 units) provisionally `planted_silvoarable`; cut-and-carry fodder shrubs (2 units) `cross_family`; use `--fix-family` if the team disagrees |
| **Blockers worth a screengrab** | Dobhal p9→10 (the best silvopastoral drought effect size in lane A, lost to a page straddle); Félix rainfall-gradient moderator p9→10; WV2019 p9 Fig 3; CMSCR pp25→26 and Tables A4.16–19; Ferraz Tabela 5 (17 TIR/BCR rows, decimal commas) |
| **Contract gap** | 26 multilingual units carry a deliberately blank `country`: multi-country reviews spanning income bands, where the "modal context" rule has no answer. Consider allowing a country list with a derived band, or an explicit `income_group = mixed` |
| **Content error for QA** | IPCC AR6 WGII Ch5 p72 attributes Abdulai (2018) to coffee in Ghana; the cited study is on cocoa. Recorded at `extraction_confidence = low` with the mis-attribution in `context.note` |
| **A finding that cuts against the grain** | `ev_wind_cyclone_hazard_philpott08_8` (Uriarte 2004): more structurally complex vegetation was *least* resistant to hurricane damage — the only unit contradicting "complexity = protection" on the asset side, sitting opposite 10 units saying complexity lowers landslide risk. Relevant to M2b Stream A |
| **Grey positive-bias check** | the most independent sources (Regreening endline, SPIA Ethiopia, IEG) are null or modest; implementer briefs (World Vision) are the most positive. ~20 % of lane D is null or negative and deliberately kept |

## 1d. Economics — resolving the empty T6 cost cells (Pete "agree go", 2026-10-05)

**Source found:** Pete's OneDrive `1_Projects/Archived/ERA Worldbank Economics` = **Steward, Joshi, Kacha, Ombewa, Mumo,
Muller, Youngberg, Magnan & Rosenstock (2023), *Economic benefits and costs of NbS in LMICs*, Alliance working paper**
(198 studies, ~9,700 economic observations, 12 agricultural NbS) + its meta-dataset (`nbs_data_p3.csv`, 3,744 rows, each
with the primary's DOI and an in-paper table locator; ERA-coded rows resolve via `ERAg::ERA_Bibliography`, column `ERACODE`).

**Three layers applied**
1. **Working paper registered** as `steward_2023_nbs_economics_wp` under the new **.docx rule** (master docx + a once-rendered
   LibreOffice PDF as the artefact of record; `methodology/search_protocol.md` §Word documents). 4 pooled agroforestry units
   from Table 3 (p14), all `ln_response_ratio`, `design = meta_analysis`, all **ns**: gross revenue 0.223 (n=9), cost −0.014
   (n=10), profit 0.164 (n=11), BCR 0.17 (n=8). Internal authorship → tier `medium` (independence discount).
2. **Gate semantics**: a meta-analysis unit now counts its pooled `n` as independent sources (`independent_sources()`), so a
   single synthesis source can clear the ≥2 gate on `magnitude_summary` / `economic_value_range` and lift `evidence_level`.
3. **Meta-dataset as a seed list** (datasets stay PAUSED — no adapter yet): 14 agroforestry economics primaries queued
   (`*_econ`, tables T6, with the dataset's **VALUE LOCATIONS** in the note so the extractor knows which table to read) — 4 from
   `nbs_data_p3.csv` (Bado 2021 Niger · Pérez-Neira 2016 Ecuador · Adhikary 2022 India · Li 2022 China) + 10 ERA codes
   (Bucagu 2013 · Fadl 2013 · Midega 2014 · Aiyelaagbe 2001 · Kormawa 1999 · Maliki 2012 · Onduru 2008 · Reyes 2005 · Snapp 2010 ·
   Tonye 1995). 13/14 DOIs round-trip (Reyes 2005 blanked → title-only). **All 14 are Elsevier/Springer/CUP/SAGE with no
   Unpaywall copy → `pending` for Namita's required web-search OA recovery; NOT labelled paywalled.** Three carry a PICOS
   `SCREEN` flag (Midega legume intercrops, Onduru INM, Snapp PNAS) — emit only if a woody component is explicit.

**For Pete as lead author — the WP's prose disagrees with its own Table 3** (extractor report, verify before any re-release):
agroforestry n = "12" in prose vs 8–11 per outcome in Table 3 and 9 studies / 190 obs / 6 countries in Table S1; total
studies 198 (p8) vs 181 (Summary p3); observations 9,705 vs 7,116 (Table S1); countries 30 vs 34; "ten" NbS (p6) vs "twelve"
(p8) vs 11 listed in Table 2; several prose log-RRs are typos against the table (all-NbS profit "17.5" for 0.176, biochar
profit "16.2", rotation cost "24.4", reduced-tillage cost missing its sign; rotation profit 0.22 vs 0.429; reduced-erosion
profit 0.18 vs 0.207); organic-fertiliser BCR called significant (table p = 0.545). Units were taken from the table.

**Pointers — pooled economics for the other 11 NbS** (Table 3, pp14–15; log-RR, n, p) — a cross-NbS economics layer once
their practices map to our T0 (the "reduced erosion" pool's search string names terraces / contour bunds / zaï / water
harvesting but the results text does not, so no `water_harvesting_conservation` units were emitted):
| NbS | gross revenue | cost | profit | BCR |
|---|---|---|---|---|
| All NbS | 0.162 (137, <0.001) | 0.062 (156, 0.033) | 0.176 (180, <0.001) | 0.019 (137, ns) |
| Reduced erosion | 0.453 (7, 0.143) | 0.183 (7, 0.165) | 0.207 (10, 0.049) | 0.158 (7, 0.241) |
| Residue/mulch | 0.185 (41, 0.028) | −0.017 (51, ns) | 0.222 (64, 0.01) | 0.028 (39, ns) |
| Reduced tillage | 0.03 (49, 0.204) | −0.104 (62, <0.001) | n/c | 0.076 (49, 0.025) |
| Intercropping · Rotation · Cover crops · Organic fert. · Biochar · IPM · Reduced fert./irrig. | see report | | | |
ERA economics codes for the **water-harvesting round**: AN0083, AN0121, DK0008, EO0122, HK0259, JS0241, NJ0007, NN0102, NN0259, NN0305 (+1).

**Two defects the re-synthesis exposed and fixed (same PR):**
- The IPCC AR6 WGIII / Roe 2021 **"USD 100/tCO₂e" is a mitigation-cost screening threshold** (potential available at or below that carbon price), not a measured cost — lane B had said so in the unit note — yet it became the *magnitude* of the per-hectare establishment-cost cell. Both units soft-dropped (`unusable_value`, restorable if a `cost_per_tco2e_avoided` cell wants an upper bound).
- **Economic cells are denominator-specific.** XW routed every `project_cost` unit to every cost cell by variable alone, so a per-tonne or per-beneficiary figure could set a per-hectare value. The engine now admits a unit to a cost cell only if its `unit` matches the cell's denominator (`_ECON_UNITS`); relative metrics (log-RR, % change) pass but can never set a value. With that guard in place `project_cost` is routed to `cost_per_beneficiary`, `cost_per_tco2e_avoided` and `recurrent_cost` too. Result: `cost_per_hectare_restored` now reads **USD 58–127/ha (LMIC, 2 independent sources: CRS Ghana FMNR · Colombia CMSCR)**; `cost_per_beneficiary` USD 66–201/household (CRS, one source across two families — summary only).

**Still open**
| item | detail |
|---|---|
| OA recovery of the 14 primaries | Namita: ResearchGate / repositories / author copies; then extract the dataset-named tables |
| Currency / price-year normalisation | dataset holds NGN, XOF, SDG, MWK, ZAR, ETB… and mixed years; the T6 gate pools only same-unit rows — a USD/ha + price-year rule is needed before local-currency rows can meet (decision 4 said no inflation adjustment; revisit) |
| `gross_revenue` vs profit | both sit under `economic_return`, told apart only by `raw_name`; a VONT `gross_revenue` id or an XW split keeps them from pooling (the WP itself says profit, not revenue, is the farmer-relevant measure) |
| WP cost = variable cost | not an establishment cost; `project_cost` units carry the caveat |
| Dataset-intake adapter | `source_kind = dataset`, snapshot + sha1, `locator_type = table_row`, quote = serialised row, `lineage_of` = row DOI — would let the 3,744 rows (and ERA) enter directly; separate design PR |

## 3. Water harvesting & conservation — synthesis-first round 1 (2026-10-05; 3 agents; 78 candidates queued)

Logs: `methodology/discovery_logs/water_harvesting_{T3T6_synthesis,multilingual_T3T6,grey_mel_T3T6}_2026-10.md`; SRCH runs
`wh_synthesis_first_2026-10-05_{lit,ml,grey}` (7 rows); ledger `updated_lit` T3/T6 done · `grey` in_progress (IFAD 403, WFP
FFA series, Niger half-moon IE, NGO portals not worked) · `stock` T6 done (ERA economics seed). WH had **0 effect units** before.

**Coverage after discovery.** T3: drought 19 syntheses; flood only plot/field runoff (no flood-peak synthesis); heat 1
(Steward 2018 — **Pete first author, COI axis**, conservation-agriculture only); **waterlogging 0** (Vertisol / broad-bed-and-furrow
is grey). Asset vulnerability well covered for the first time: check-dam filling/failure (Lucas-Borja, Frankl), sand-dam failure
(Ritchie; MCC audit of 87 dams: erosion 72 %, leakage 33 %, siltation −10–25 % storage, 3/14 pump wells working), reservoir
sedimentation (Saruchera), terrace collapse (Arnáez, Wei, Roose 2006), pond seepage (Moges), Morocco gabion check dams losing
function; **bund breaching in extreme rainfall: no synthesis**. T6: production_gap 19 · water_stress 14 · soil_erosion_risk 12 ·
rural_poverty 11 · water_quality 5 · carbon 4 (no LMIC soil-carbon-under-bunds synthesis) · gender 0 · spate 1 (Roose 2010 only).
Economics: India watershed treatment cost US$261/ha and US$217/ha (IEG 61065 pp68, 97), zaï ≈300 man-hours/ha (Kaboré & Reij
p15), Rwanda terrace NPV US$285/ha, BCR 1.38 (ICR4539 p50), Joshi 2005 meta-analysis of 311 case studies BCR 2.14 / IRR 22 %
(p6, **needs OCR**); programme ERRs 15–36 % have no denominator. Negative/null evidence kept: Heusch 1995 (Niger diversion
terraces lowered yields, raised erosion), Arabi 2004 (40-yr Algerian ex-post, abandonment), Glendenning (downstream losses),
Malan 2024 (little causal income evidence), Adimassu (yield lost to bund footprint), Ethiopia SLMP (yields fell in treated AND
control; the 20 %/5 % dip on p66 is a CBA assumption, not an observation).

| pointer | note |
|---|---|
| **Uttarakhand II sediment "17 % reduction"** | 71.6→69.3 t/ha/yr is **3.2 %** — the ICR's label is wrong; encode the numbers, never the label |
| 31 % of earthen dams silted within five years, 20 % functioned < 1 yr (IEG 61065 p72) | cited from Kurian et al. 2003 — chase the primary; `cited_secondary` |
| IFAD "+25 % yields" | web snippet, never read in a document — do not use |
| `ieg_ethiopia_slmp_ppar_2020`, `alemu_spia_ethiopia_2024` | already in SRC under agroforestry → add `water_harvesting_conservation` to `nbs_ids` and run a WH extraction pass over the cached PDFs |
| OpenEdition chapters (Roose 2010, 2017; IRD) | served as HTML → cache `.html` snapshots with section locators (existing web rule), or chapter PDFs if OpenEdition serves them — decide before extraction |
| Barraginhas (Brazil) and sand dams | no FAM sub-practice: `runoff_catchment` or `micro_catchment`? — family owner to ratify; sand dams need an id |
| China (Loess Plateau II) | lower-middle income at evaluation, upper-middle now — transfer class from the study period |
| Roose 1994 exists in EN and FR editions | extract one edition only |
| Conservation-agriculture syntheses (Steward 2018, Corbeels 2020, González-Sánchez 2019) | apply ONLY to `water_harvesting__in_situ` (conservation tillage / mulch), never to bunds or pits |
| Fan, Arnáez, Wei, Lucas-Borja | heavily HIC / Chinese evidence → expect `out_of_context` on LMIC rows |
| ERA seed: NJ0007 (no DOI, title-only), EO0122 (candidate DOI, may not be WH at all) | human check |
| Human browser downloads | IFAD IOE Burkina Faso; WFP FFA evaluations; Niger demi-lune impact evaluation; Concern sand-dam brief; MCC-published copy of the sand-dam audit (current copy is an author draft); PeerJ/OUP 403s; ResearchGate-only ×8 (Dile, Rockström, Kato, Glendenning, Arnáez, Adimassu, Bouma, Stavi) + Cárdenas 2022, Arabi 2004, Botoni & Reij 2009 |
| Bias pattern | independent sources (IEG, IFPRI, SPIA, MCC) most sceptical; Bank completion reports most positive — apply the COI discount and cross-check ICRs against IEG's ICRRs |
| Reserve lists | ~25 EN (Pittelkow 2015 ×2, Tarolli 2014, Wolka 2026 adoption/dis-adoption, Ryan 2016 sand dams in drought, Pavelic 2012 floodwater harvesting); Mesoamerican terraces (Bocco 2019) |

## 1e. Water harvesting — round-1 extraction outcome (2026-10-05) and decisions for Pete

Five opus lanes over 37 acquired sources (A: 10 EN syntheses · B1: 7 IEG/IFPRI/ESSP/ILSSI evaluations · B2: 7 WB ICRs ·
C: 7 ES/FR · D: 6 PT). Ingested through the gated staging path: **295 effect/asset units + 80 `operational_risk`**
(run `wh_effect_sweep_2026-10`; SRC rows promoted by `scripts/promote-queue-to-src.py`). First generated WH T3/T6:
`schema/recipes/water_harvesting_conservation/T3T6_BENCHMARK.md`. New: FAM `water_harvesting__cross_family`; XW routes
`agricultural_production_value→production_gap` (proxy), `water_access_deficit→water_stress` (direct) and `→T3 drought`
(component) — all `pete (pending)`.

**Decisions needed**

| item | detail | options |
|---|---|---|
| **Crop-specific yields routed out of practice cells** | Lane A tagged single-crop results `crop_specific` + `taxon` (Zougmoré 4, Kaboré 5, Malan 1) as the lock requires; the drought roll-up is therefore `low` (direction-only pool) although the units show zaï 300–400 kg/ha vs 0 (1990 drought) and stone bunds 2–3× in dry years | add `allow_crop_scope` for WH families (yield on the host crop IS the practice effect; WH does not define a crop system) · or keep routed out and accept the `low` wall |
| **Hazard enum has no sedimentation / intense-rain / landslide value** | 16 `asset_vulnerability` units (A 13 · B1 3) describe siltation, structural erosion, leakage, pump-well breakage, gabion infill, storm damage with no named hazard; 4 lane-C units mapped torrential rain / mass movement to `flood` and flagged. Parked verbatim in `schema/registers/_deferred/wh_asset_pending_2026-10/` | add `sedimentation` (+ `landslide`) to the T3 hazard enum · or a hazard-less `asset_condition` role · or keep `flood` for intense-rain breaching |
| **FAM sub-practice gaps** | sand dams, small communal reservoirs/tanks, subsurface dams, barraginhas (none evidenced), diversion banquettes (never form terraces — lane C) | ids under `runoff_catchment` (sand/subsurface dams, tanks); a `diversion_structures` sub-practice or keep under `terracing`; infiltration trenches `in_situ` vs `micro_catchment` |
| **VONT gaps (not emitted)** | downstream flow reduction (4 sources — the negative externality of upstream harvesting), evaporation loss, microbial / salinity water quality, fish production, asset condition, community participation, maintenance burden, surface-water storage area; `ndvi` (1 unit) has no XW route | add ids before round 2 |
| **Economics without a standard denominator** | per structure, per m³, EUR/acre, EUR/yr, CFA/ha, FRF/ha (Heusch "F 3000/ha" currency unclear), INR/ha (`kar20_5` excluded) | extend `_ECON_UNITS` with `usd_per_structure`, `usd_per_m3`, `labour_days_per_ha`; add currency-year to notes only (ordinal, no normalisation) |
| **Income banded on a cost band** | Venot USD 350/household/yr classed `strong` via the cost band (no income band exists); `usd_npv_per_ha` (Rwanda) is a new unit with no band | add income / NPV bands or leave unbanded |
| **`design` enum** | contract has no `monitoring` design → ICR results-framework values tagged `observational` with a note | add `monitoring` at the next contract bump |
| **Kassie bunds-lower-yields finding** | Schmidt cites it as Kassie et al. 2008, Abate as 2009 — must be resolved before lineage dedupe | check the primary |


**Engine fixes from the WH prose-writer reviews (2026-10-05/06, implemented + tested, pending ratification at PR review)**

| defect | fix |
|---|---|
| `magnitude_summary` pooled magnitudes regardless of direction (a −34 % yield loss was the median of a `strong_positive` production row) | pool only units whose benefit-frame sign = the row's modal sign; opposite/null units counted in `n_excluded_opposite` |
| cost class could rest on a figure `economic_value_range` excluded (Peru 1994 UMIC cost made terracing costs "large" vs the LIC/LMIC band) | income-band gate applied to economic magnitude summaries (`n_excluded_band`) |
| `establishment_cost` and `cost_per_hectare_restored` carried the same four per-ha units → cost counted twice | `establishment_cost` = per-structure / per-system / per-m³ denominators only; per-ha → `cost_per_hectare_restored`, per-household → `cost_per_beneficiary`; BANDS rows added for `usd_per_structure` (1 000 / 10 000) and `usd_per_m3` (5 / 50), LIC/LMIC ×1, UMIC ×2, HIC ×5 — thresholds pending |
| units silently dropped from pooling (`bcr` ≠ `benefit_cost_ratio`; `pct_change` with no unit) | `_UNIT_ALIASES` + default `percent` for `pct_change` |
| bundled-programme results (`evidence_type = scoping_candidate`) voted at full weight; a very_high drought class rested on bundles | `BUNDLED_W = 0.5` |
| farming-system rows emitted with no system-specific unit (rooftop cisterns × irrigated cropping; identical to the all-systems row) | a T3 farming-system row needs ≥1 unit stating that system — agroforestry T3 149→75 rows, riparian 9→6, WH 59→20 |
| asset-threat rows said "slightly damaged" on direction-only evidence | "is damaged by … (strength not quantified in the evidence)" |
| single-source rows printed "weighted sign agreement 0.0" | "sign agreement undefined (single independent source)" |
| medians rounded outside their own range | median/low/high rounded consistently (3 dp) |

Not changed (design, noted for Pete): null / ns units legitimately pull the modal-sign magnitude median to 0 → rank floors at 1 (`low`) even when quantified positives exist (drought roll-up: 3 null units outweigh 4 quantified gains); a meta-analysis counts its `n` studies, so one review's pooled "factor" (n = 105) outranks a multi-source soil-loss pool as the row's magnitude summary.

**Human-QA items from the reviews (Namita's lane; not engine)**

| unit(s) | issue |
|---|---|
| `ev_drought_hazard_arsky20_3`, `_cirilo03_2`, `_cirilo03_3`, `ev_drought_hazard_iegtun13_1` | storage running dry / reduced benefit tagged `asset_vulnerability` (their own notes say "not structural damage") → re-tag `nbs_effect` with the measured direction; they currently create the rooftop + runoff drought asset-threat rows |
| `ev_water_access_deficit_ritc21_3` | capacity limit (67 % of sand dams) coded `none`; its note calls it a negative finding |
| `ev_soil_water_retention_willem21_2` | encodes the positive half of a quote that also says narrow benches / contour-trench terraces had no advantage |
| `ev_flood_hazard_ritc21_1` | dam-size trade-off, not evidence that sand dams worsen floods |
| `ev_food_security_kabo04_1` (negative), `ev_economic_return_heusch95_1` (positive for ≈1 % return), `ev_economic_return_yem12_7` (return reflects the subsidy) | sign / meaning questionable |
| `ev_project_cost_kar20_5`, `ev_project_cost_veno12_1` | tagged `cost_reduction` but encode an absolute cost / a cost spread |
| `ev_runoff_reduction_utk22_4` | +1.5 % runoff kept as null/negative while the same page says most watersheds show less runoff |
| `ev_project_cost_hp17_5` | `usd_per_m3` = per m³ of masonry, not per m³ stored — unit semantics; propose `usd_per_m3_structure` |
| flood cell | bunds/terraces lower peaks vs diversion banquettes raise them (`heusch95_1`, `roose94_3` under terracing) — FAM split would give two clean rows |
| `ev_economic_return_mrt14_4`, `ev_runoff_reduction_roose06_4` | in family rows but not the NbS-wide row — check dedupe/econ filter |
| residue mulch under `in_situ`; a USA unit in the flood asset row's country list | tagging |

**Pointers (verify before use — a lane's "number is in document X" is a pointer, never provenance)**

| pointer | note |
|---|---|
| Joshi 2005 (IWMI RR8 meta-analysis, 311 studies) | body text font-ciphered → `needs_ocr`; only the summary BCR 2.14 / IRR 22 % quotable |
| Venot 2012 tables ciphered; per-ha / per-m³ costs only in figures | queue-note cost figures NOT verified |
| Page-break quotes skipped | Zougmoré 145 000–180 000 FCFA/ha/yr; Castro p17 sentence starts mid-page; four lane-A sentences |
| Tables needing screengrabs | Zougmoré T1–5, Kaboré T1–3, Frankl T3, Saruchera T9–11, Neufeld T8–9, Rwanda farm-model tables p51–52, Yemen T3.3 p46 (garbled text layer) |
| Primaries to chase | DIME Rwanda LWH terracing IE; IFPRI 2014 PSNP public-works IE; TERI 2019 Karnataka impact study; Kurian 2003 (31 % earthen dams silted ≤ 5 yr); full ILSSI assessment behind the Arega 2024 brief (5 pp, no numbers) |
| PICOS refusals (recorded in lane reports, not emitted) | Sujalam Sufalam (canal water, not WH); IWDP wheat/maize (seeds, no control); Morocco net revenue (irrigation + crop packages); Tunisia governorate statistics; Yemen piped/drip component; Karnataka weather-advisory income; Ethiopia food security (80 % cash transfers) |
| Water-quality / health pointers (no VONT id) | faecal coliforms in 70–100 % of cistern samples; no significant diarrhoea difference (quasi-experimental); hospitalisations ns (lane D) |
| Uttarakhand runoff contradiction | p says most watersheds show less runoff AND overall surface runoff +1.5 % → kept as null/negative |
| Casagrande 2022 treatment bundles cistern + cash grant + training | kept as full relationship with the bundle in the note — downgrade candidate |
| ES/FR costs in FRF / CFA (Roose, Heusch) | not encoded (currency unclear) |

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
