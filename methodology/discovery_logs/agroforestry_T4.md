# Discovery log — Agroforestry × T4 (suitability) — retrospective

**Date(s):** April 2026 – June 2026 (Stocktake) · June 2026 (paper-first F1 sweeps).
**Author(s):** Lolita Müller (Stocktake screening + benchmark scoring) · Pete Steward (paper-first sweeps + this log) · Claude Code (operator).
**Seed-set rule:** T4 method §3 bounded, authority-weighted seed-set (v0.2.6 / v0.2.7 SOP). Cap ~10-20 sources per NbS × table.
**Screening funnel:** five-step (frame · source-type triage · relevance · six-axis credibility · saturation stop). C/I/D rubric used in the Stocktake; six-axis rubric (v0.2.7) reconciles to the same `benchmark_tier`.

> **Retrospective.** This log captures what was done **before** the v0.2.7 PRISMA-lite SOP existed. Numbers are reconstructed from the Stocktake benchmarked CSV + the paper-first sweeps committed to this repo. Forward logs (#27) will follow the SOP from the start.

---

## Sources & databases queried

### Stocktake Review (Apr-Jun 2026, pre-repo)

- **OpenAlex API** (peer-reviewed lit) — see `2_Technical_&_Data/Stocktake Review/Open Alex search/OpenAlex_run.R` + `search_string.xlsx`. Queries built on NbS-practice keywords × spatial-suitability / MCDA / land-evaluation terms.
- **GPT grey-lit pull** — targeted grey-literature scan (project reports, FAO/CGIAR institutional reports) flagged on the same search strings.
- **Manual Zotero screening** — full-text screening folder: `…/Stocktake Review/Manual Screening/Zotero_Full_Text_Screening/Agroforestry/`. 23 PDFs retained (1:1 with the benchmarked CSV's AF practice rows).
- **Benchmark scoring** — C / I / D rubric: Content (variable inventory + thresholds + provenance), Impact (citation count + journal impact factor + citations/year), Data quality (method validation + spatial scale + transparency). Final tier: `Final_Benchmark ∈ {High, Medium, Low}` in `NbS_peer_reviewed_benchmarked.csv` (220 rows total).

### Paper-first sweeps (June 2026, this repo)

- **Frame:** F1 Planted silvoarable agroforestry suitability variables (T4).
- **Corpus:** the 23 AF PDFs from the Stocktake (already discovered + tiered).
- **Method:** paper-first SOP per `T4_generation_method.md` §3 (v0.2.6+) — one PDF visit per paper, all variables + relationships in one pass, harmonise to VONT, tier-weight, synthesise.
- **Tools:** local ingest cache (`src/nbs_ruralscan/ingest/`, vectorless retrieval over page-tagged + table-extracted PDF index, OCR fallback). Cache gitignored (PDFs copyrighted).

### Phase 2: Unified Synthesis & WOCAT Ingestion (June 2026, Issue #24)

- **WOCAT SLM Database (Liniger et al., 2011)** — targeted extraction of biophysical thresholds and baseline establishment costs for the F1 agroforestry family.
- **Scientific Synthesis Papers**:
  - **CGIAR (Simelton et al., 2021)** — agricultural NBS functions mapping to priority themes.
  - **GCA (2022)** — State and Trends agroforestry enabler findings (tenure, finance).
  - **WRI (Collins et al., 2025)** — Sub-Saharan Africa climate-resilience cost-effectiveness.

---

## PRISMA-lite counts

### Stocktake Review pipeline (220 → 23 for AF)

| Stage | Count | Notes |
|---|---:|---|
| OpenAlex returned (raw) | ~30 000+ | NbS-cluster × spatial-method search strings, year ≥ 2000 |
| After dedupe + bibliographic-completeness filter | ~5 000 | Lolita's pipeline (R) |
| After manual title/abstract screen (NbS-spatial relevance) | ~600 | Multi-pass |
| After full-text screen | **220** | Final benchmarked corpus across **all NbS** |
| **Agroforestry subset** | **23** | Practice = "Agroforestry" rows |
| **AF tier breakdown** | 5 High · 13 Medium · 5 Low | Per `Final_Benchmark` column |

### Paper-first F1 sweep (this repo)

| Stage | Count | Notes |
|---|---:|---|
| AF corpus available (Stocktake) | 23 | 5H · 13M · 5L |
| Papers ingested + cache-indexed | 23 | Wotlolan p.10 OCR-flagged |
| Papers **swept paper-first (full var inventory)** | **6** | Nath, Castle, Brandt, Mendonça 2022, Mendonça 2023, Palma |
| Papers contributing variable-first EVs (slope/precip/MAT/pH/SOC) | +9 (overlap +6) | Haile, Ahmad-Goparaju, Mushtaq, Haris, Wotlolan, Seja, Ahmad-2020, Yadav, Ahmad-2018 |
| **Total AF sources with ≥1 EV row in repo** | **18** of 23 | 6 High · 7 Medium · 5 Low |
| **AF EV rows committed** | **81** | Across slope, annual_precipitation, mean_annual_temperature, soil_ph, soil_organic_carbon + each swept paper's full variable inventory |
| **AF papers not yet swept paper-first** | 5 swept-fully + 12 partial = **17 remaining for full sweep** | Tracked as ongoing work; Med/Low tiers |

### Phase 2: Unified Ingestion Counts (Issue #24)

| Stage | Count | Notes |
|---|---:|---|
| Query targeting synthesis sources | 5 | Targeted identification of core WOCAT database reviews and 3 institutional synthesis publications |
| Retained for metadata register extraction | **5** | All 5 papers extracted for biophysical, cost-effectiveness, or enabler evidence |
| Added to SRC Register | **5** | Registered as High-tier synthesis sources |
| Added to EV Register (Agroforestry) | **7** | ev_slope_wocat_liniger11, ev_precip_wocat_liniger11, ev_estcost_wocat_liniger11, ev_priority_simelton21, ev_tenure_gca22, ev_finance_gca22, ev_cost_wri25 |

---

## Inclusions

All 18 AF sources now in `schema/registers/SRC_source_register.json` (`nbs_ids` contains `agroforestry`):

| `source_id` | tier | first author / year | aez · country | paper-first sweep |
|---|---|---|---|:---:|
| `brandt_2015` | High | Brandt 2015 | semi_arid · Kenya | ✓ |
| `castle_2025` | High | Castle 2025 | temperate_europe · USA Midwest | ✓ |
| `mendonca_2022` | High | Mendonça 2022 | humid_tropics · Brazil (São Paulo) | ✓ |
| `mendonca_2023` | High | Mendonça 2023 | humid_tropics · Brazil (São Paulo) | ✓ |
| `palma_2007` | High | Palma 2007 | temperate_europe · Multi (Spain/France/NL) | ✓ |
| `zomer_2014` | High | Zomer 2014 | global · Global | — (variable-first only, slope) |
| `ahmad_2020` | Medium | Ahmad 2020 | sub_humid_tropics · South Asia | — (variable-first) |
| `chuma_2021` | Medium | Chuma 2021 | humid_tropics · DR Congo | — (variable-first) |
| `mushtaq_2023` | Medium | Mushtaq 2023 | highland_tropics · India (Kashmir) | — (variable-first) |
| `nath_2021` | Medium | Nath 2021 | humid_tropics · India (EIHR) | ✓ |
| `nair_1993` | Medium | Nair 1993 | global · Global | — (variable-first only) |
| `wotlolan_2021` | Medium | Wotlolan 2021 | humid_tropics · Fiji (Sigatoka) | — (variable-first) |
| `yadav_2024` | Medium | Yadav 2024 | sub_humid_tropics · India (Punjab) | — (variable-first) |
| `ahmad_2018` | Low | Ahmad 2018 | sub_humid_tropics · India (Samastipur) | — (variable-first) |
| `ahmad_goparaju_2017` | Low | Ahmad & Goparaju 2017 | sub_humid_tropics · India (Palamu) | — (variable-first) |
| `haile_2024` | Low | Haile 2024 | semi_arid · Ethiopia | — (variable-first) |
| `haris_2021` | Low | Haris 2021 | humid_tropics · Indonesia (Maros) | — (variable-first) |
| `seja_2022` | Low | Seja 2022 | sub_humid_tropics · Tanzania (Uluguru) | — (variable-first) |

#### Phase 2 Ingested Synthesis Sources (All High Tier)
| `source_id` | tier | first author / year | aez · country | variables extracted |
|---|---|---|---|---|
| `wocat_liniger_2011` | High | Liniger 2011 | continental · SSA | slope, annual_precipitation, establishment_cost |
| `simelton_2021` | High | Simelton 2021 | global · Global | biodiversity_conservation_priority |
| `gca_2022` | High | GCA 2022 | continental · SSA | tenure_security, finance_credit_access |
| `wri_2025` | High | Collins 2025 | continental · SSA | establishment_cost |

Tier rationale: C/I/D rubric (Lolita) for the Stocktake; six-axis rubric (v0.2.7) confirms the same tiers when re-checked on the High sources (no down-/up-grade triggered).

---

## Exclusions

### Stocktake Review (Apr-Jun 2026)

- **Out-of-NbS-scope** — papers tagged to other clusters (forest conservation, wetlands, water-harvesting, etc.) — not in the AF subset.
- **Out-of-spatial-suitability scope** — agronomy / species-physiology papers without a spatial / MCDA / land-evaluation component.
- **Pure species-suitability papers** ("suitability of *Lansium domesticum*") — screening rule kept the corpus at agroforestry-practice-level, not single-tree.
- **Pre-2000 cutoff** — applied at OpenAlex query stage.
- **Non-English** — current screening pipeline doesn't translate; flagged as a known bias (mostly affects Brazilian + Francophone-Africa lit which is partially represented via English-language outputs).

### Paper-first F1 sweep (June 2026)

- **Family-mismatched papers excluded at sweep time:**
  - `kiziridis_2026` (Med, Mediterranean): silvopastoral → F3 family. Excluded from F1 sweeps; will be picked up when F3 silvopastoral comes into scope.
  - `baldwin_2022` (Med, USA): flood NbS (FloodWise), not silvoarable agroforestry. Excluded from F1; relevant to water-harvesting / flood-mitigation recipes.
  - `singh_2024` (Med, India): remote-sensing/nanotech survey, no spatial-suitability classes. Variable-first EVs only (precip selection signal).
  - `ellis_2000` (Low, USA): FADSS species-DB framing; species-suitability angle conflicts with practice-level T4. Variable-first selection signals only.
- **Species/crop-specific claims** (`claim_scope = species_specific` / `crop_specific`) **dropped at synthesis** (filtered by `synthesise_t4_row`): Mushtaq mulberry (Morus alba), Haris sengon (Falcataria moluccana), Wotlolan multi-crop Pacific. Their **slope** evidence retained (technology-driven); their **climate** evidence routed to species suitability.

---

## Notes

### Judgement calls

- **LMIC preference (six-axis rubric)** applied as a tie-break only — global syntheses (e.g. Zomer 2014) admitted on authority grounds even though they're "global" rather than LMIC-specific.
- **Seminality flag** not yet populated (`SRC.is_seminal`) — would mark Zomer 2014, Nair 1993 as foundational. Backfill task.
- **Independence / COI discount** not triggered for any AF source — none of the 18 sources are advocacy-funded promotional grey lit.
- **Tier tension** documented on slope (`methodology/examples/t4_slice_agroforestry_F1_slope.md`): High-tier sources (Mendonça, Brandt) gave relief rankings, not hard cuts; Low/Med-tier (Nath, Mushtaq, Haris, Seja) gave the crisp numeric thresholds. Synthesised with **High for shape, Low/Med for magnitude**, with the divergence recorded rather than averaged away.

### Saturation stop

- The 23-paper AF corpus was kept whole (not capped at 10-20) because the corpus *is* the v0.2.7 seed-set for AF/T4; no Phase 2 re-discovery has been run yet (issues #20-#26 cover that).
- Saturation reached on the **5 fully-extracted variables** (slope, precip, MAT, pH, SOC) — additional Med/Low-tier papers added context but no new thresholds. Six-axis rubric flagged that the four High-tier papers (Brandt, Castle, Mendonça×2, Palma) **systematically provide selection signals, not shape**; this is the corpus's structural bias (climate-smart targeting + Brazilian relief ranking), not a screening miss.

### Known biases

- **Optimistic-corpus bias** documented in `T4_generation_method.md` §6.1 (where NbS *works* is over-represented; failures are under-published). Conservative synthesis defaults applied.
- **Geographic skew toward South-Asian AHP studies** at Med/Low tier (Indian + Ethiopian context dominates the threshold-bearing papers). High-tier papers cover Brazil, Europe, US Midwest, Kenya.
- **Stocktake `Input_Variables` column is sparse** (3-9 papers per variable) — agroforestry-specific input-variables xlsx sheet is **empty**; the corpus-text-derived candidate-variable register (`schema/registers/CV_candidate_variables_agroforestry_F1.md`) was built post-hoc in this repo to bridge the gap.

### Pending for Phase 2 re-discovery (issues open)

- **#20** T6 bounded-corpus (effectiveness + conditionality).
- **#21** T3 bounded-corpus (hazard mitigation + vulnerability).
- **#22** CSA adoption & barriers ingest.
- **#23** MEL/MELIA seed-set.
- **#24** WOCAT seed-set (SLM technologies DB).
- **#25** Evidence Gap Maps (3ie/Campbell/CEE).
- **#26** WB project evidence (PADs/ICRs/IEG) + TORs tools.

When these land, this log gets a §"Phase 2 amendments" with the additional sources + counts.

---

## Provenance pointers

- Benchmarked CSV (off-repo, OneDrive): `2_Technical_&_Data/Stocktake Review/data/NbS_peer_reviewed_benchmarked.csv`
- AF screening folder (off-repo, OneDrive, copyrighted): `…/Stocktake Review/Manual Screening/Zotero_Full_Text_Screening/Agroforestry/`
- Ingest cache (gitignored, local): `.cache/ingest/`
- This-repo registers:
  - `schema/registers/SRC_source_register.json` — 18 AF entries.
  - `schema/registers/EV_evidence_register.json` — 81 AF EV rows.
  - `schema/registers/CV_candidate_variables_agroforestry_F1.md` — corpus-derived variable prevalence.
  - `schema/registers/CV_lit_review_agroforestry.csv` — Pete's lit-review summary.
- Method: `methodology/T4_generation_method.md` §3 (seed-set rule + screening funnel).
- Worked gold standard: `methodology/examples/t4_slice_agroforestry_F1_slope.md`.

---

## Sign-off

| Step | Sign-off |
|---|---|
| Screening (Stocktake) | Lolita Müller (May 2026) |
| Paper-first sweep (F1 v0.3.0) | Pete Steward (2026-06-06) — operator-level only; QA pass pending |
| Phase 2 Ingestion (Issue #24) | Pete Steward (2026-06-09) — database-first sweep |
| QA / dataset-fitness review | **Benson Kenduiywo (pending)** — flag this log when developmental dataset bindings land. |
