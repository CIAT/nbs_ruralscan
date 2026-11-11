# wetland_stock_tool — wetland_management T3/T6, processes `stock` + `tool` (2026-11-10)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `wetland_t3t6_gaps_20261110_stock_tool`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-10: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `wetland_t3t6_gaps_20261110_stock_tool`, ledger per `--ledger`.


Run `t3t6_gaps_2026-11-10/wetland_stock_tool` · discovery ruleset v1.8.1 · generic (family="") · staging only, no git, no PDFs downloaded.

## Counts (bounded inspected set)

| table | process | retrieved | screened | included |
|---|---|---|---|---|
| T3 | stock | 238 | 238 | 10 |
| T6 | stock | 238 | 238 | 21 |
| T3 | tool | 31 | 16 | 1 |
| T6 | tool | 31 | 16 | 5 |

28 unique candidates (22 stock, 6 tool); 6 are `reuse_source_id` (registered sources never extracted for T3/T6). All new DOIs round-tripped via Crossref (title match); grey items carry no DOI and are acquired by title.

## Verbatim queries

#### stock
- `SRC_source_register.csv: nbs_ids/source_id contains "wetland" AND no non-dropped EV unit with use_role in {nbs_effect, asset_vulnerability} (19 rows)`
- `acquisition_queue.csv: rows mentioning wetland with status in {pending, acquired} (37 rows)`
- `cited_originals.csv: nbs_ids contains wetland_management AND status in {reference_found, citation_only} (97 rows)`
- `methodology/discovery_logs/wetland_management_*_T3|T6_2026-08.md screened-in tables (85 entries) title-matched against SRC + queue citations`
- `Crossref /works?query.bibliographic=<exact title> for identity + DOI round-trip of each new candidate`

#### tool
- `GitHub API GET /repos/natcap/invest/commits/main ; /git/trees/main?recursive=1 (paths containing ndr|sdr|coastal|seasonal|annual|carbon|flood)`
- `GitHub API GET /repos/natcap/invest.users-guide/git/trees/main?recursive=1 (coastal_vuln|ndr|annual_water|seasonal_water)`
- `grep -i "wetland|marsh|rank|eff_n|eff_p|crit_len|lulc_veg|kc" over fetched source files`
- `GitHub API GET /repos/swat-model/swatplus/git/trees/<sha>?recursive=1 (paths containing wet|res_sed|res_nut|res_hyd)`
- `GitHub API GET /search/repositories?q=swat2012+in:name,description&per_page=10 ; ?q=SWAT+rev681+OR+"SWAT+rev+681"&per_page=5 ; ?q=swatplus+source+fortran&per_page=5`
- `GitHub API GET /repos/swat-model/swat2012/git/trees/<sha>?recursive=1 (readpnd|wetlan|pothole|pond.f)`
- `WebSearch: "WET-RehabEvaluate guidelines monitoring evaluating wetland rehabilitation projects Water Research Commission TT 342/09"`
- `WebSearch: "WET-EcoServices version 2 Water Research Commission TT 834/20 wetland ecosystem services assessment tool"`
- `WebSearch: "IPCC 2013 Supplement to the 2006 Guidelines Wetlands chapter 3 rewetted organic soils emission factors PDF"`
- `WebSearch: "Restauración de humedales altoandinos mediante rehidratación del paisaje enfoque de bajo costo"`

## Channels used / omitted
- Used: local registers (SRC, queue, cited_originals, Aug-2026 discovery logs), Crossref API, GitHub REST API (unauthenticated), raw.githubusercontent file reads, WebSearch (4 queries, 1 Spanish).
- Omitted: Lens.org (no LENS_TOKEN), AGRIS (manual lane), OpenAlex (not needed for stock/tool), French/Portuguese tool queries, SWAT 2012 I/O documentation PDF (typical wetland settling values; not opened), CUBHIC PDF (WebFetch exceeded 10 MB).

## Key findings
- **Stock:** 6 registered sources hold effect content but were swept only for T4/operational_risk (Goyette 2022 → catchment_water_yield/water_stress; Salmayenti 2026 + Yuwati 2021 → T3 fire; Mendham 2024 → food_insecurity; Canning 2022 → biodiversity; Earl 2023 → zero units). 16 Aug-2026 screened-in or cited-original sources were never queued, incl. LMIC cost studies (Hansson 2018, Puspitaloka 2021, Tan 2022) and the Waza-Logone floodplain re-flooding case (Loth 2004 IUCN; Scholte 2000) — the best lead for the empty T6 food_insecurity row.
- **Queue blockers matter more than discovery:** Rebelo 2009 (SSA wetlands, agriculture, livelihoods) and Dixon 2003 (East Africa wetland cultivation) are the strongest food_insecurity sources and sit `pending` as unobtainable → recommend CGIAR document delivery.
- **Tools:** effect parameters are rarely hardcoded. InVEST Coastal Vulnerability hardcodes the habitat-rank aggregation (coastal_vulnerability.py L2699-2724) and the UG default table ranks marsh = 2 → only tool lead for T3 wind_cyclone (coastal family). InVEST Annual Water Yield hardcodes a wetland AET rule (lulc_veg=0 → AET=min(Kc·ET0,P)) → direction-only lead for catchment_water_yield. NDR wetland retention 0.6–0.8 / >0.8 is guidance, not code. SWAT2012 and SWAT+ hardcode no wetland effect parameter (nutrient settling user-set; only wetevcoeff=0.6, chlaw/secciw=1, weir c=1.84/k=2.6). IPCC 2013 Wetlands Supplement Tier-1 EFs and GEST (Couwenberg 2011) are the canonical carbon parameter sources (carbon not a gap). WET-EcoServices v2 (Kotze 2020) scores water supply/streamflow/food — mostly existing_habitat comparator; its Excel tool falls under the XLSX pause.
- **Pins:** natcap/invest @ f02f5e20d2d3f46f69f4a6785d032659e2cf318d; natcap/invest.users-guide @ 56d86f2532189967cd0960fcc10a505b856f370c; swat-model/swat2012 @ ee2edded7473aad85690ab61ff56f4a15ac29051; swat-model/swatplus @ 6f515368525e7d84089ae0f9d33f4c9115de5679.

## Gaps not closed
- T3 waterlogging and T3 extreme_rainfall asset_threat: no stock or tool source found. A targeted lit search is needed (e.g. rewetting → waterlogging of adjoining farmland; storm damage to restored wetland structures/dikes).
- T3 wind_cyclone: only a coastal tool rule (InVEST CV); no inland evidence.

## Holds
CUBHIC (Forest Trends 2020, Andean bofedal water-benefit calculator — strong LMIC water_yield lead; needs human open for authors + coefficients); WET-RehabEvaluate (identity unresolved); FAO EX-ACT (XLSX paused); SWAT 2012 I/O docs; IFAD 2021 SMPEI MTR + SEAPeat Quoi 2015 (grey livelihood leads, identity unresolved); Ghermandi 2008; Singh 2022 Ramganga; sago economics cited originals.

## Stop reason
Stock: pool exhausted (all 238 reconciled records screened). Tool: saturation for the named model families (InVEST, SWAT/SWAT+, IPCC/GEST, WET-suite) — further tools are either XLSX (paused), constructed-wetland only (qualitative_only family), or encode no effect parameter.

## Next actions
1. Registrar with `--reuse-log` for the 6 reuse rows; queue the 16 new stock + 6 tool candidates.
2. Acquire LMIC priorities first: Loth 2004 (IUCN OA), Scholte 2000, Tan 2022 (OA), Puspitaloka 2021 (OA), Hansson 2018.
3. Tool code extraction via `nbs_ruralscan.ingest.github natcap/invest f02f5e2…` (coastal_vulnerability + annual_water_yield) — claim_basis=expert_assertion.
4. Human: open CUBHIC PDF; CGIAR delivery request for Rebelo 2009 and Dixon 2003.
