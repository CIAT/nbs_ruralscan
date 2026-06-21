# Agroforestry — tools / methods + codebase search (2026-06)

**Channel:** tool (`SRC.source_category = tool`) → lands in the **TOOL_tool_registry** (not EV; a tool's signal is method/variables/weights, not a variable×threshold claim). **Run:** `tool_af_2026-06`.

First pass of the dedicated tool/method + codebase discovery channel (issue #65). Scope: GitHub codebases + tool-platform docs + method frameworks.

## Search
- **GitHub** (`gh search repos`): `agroforestry suitability`, `land-suitability AHP`, `MCDA suitability mapping`, `silvopasture GIS`, `ecocrop suitability`, `fuzzy land evaluation`, `tree planting suitability`. Most multi-term queries returned nothing; `agroforestry suitability` surfaced the live codebases below.
- **Web/platform** (carried from the grey websearch): WOCAT tools, CIFOR-ICRAF SPACIAL, WRI FLR Atlas, ROAM.
- **In-repo:** the inherited `reference/R/spatMCDA.R` reference engine.

## Registered (7, all `review_status=pending_review` except the canonical reference)
| tool_id | type | method | note |
|---|---|---|---|
| `spatmcda_r` | r_package | AHP+CRITIC+entropy × 5 fuzzy membership | **canonical** inherited framework engine |
| `saraheb3_af_midwest` | codebase (GEE) | social-ecological MCDA | accompanies IOP Midwest AF paper; CC0 |
| `joshbrew_inat_af` | codebase (Python) | ML (XGBoost/ExtraTrees) + eta² weighting | iNaturalist/GBIF-driven → species-envelope flavour, not practice |
| `icraf_spacial` | webgis | dashboards | CIFOR-ICRAF; nbs_ids blank (scope unverified) |
| `wri_flr_atlas` | platform | FLR opportunity mapping | forest-restoration scope |
| `iucn_wri_roam` | method_framework | phased MCDA + stakeholder rules | High tier (stocktake-23) |

## Notes / next
- **WOCAT is NOT a tool — it's a grey-lit repository.** Removed from this register; it belongs to the grey-lit channel (search the SLM-technologies DB → each tech = a grey SRC/EV source, like CGSpace). Its companion *Mapping Tool / Decision-Support Framework / Apps* could be separate TOOL entries if specifically catalogued, but the database itself is a source, not a tool. **Repository ≠ tool:** databases/portals (search → grey-lit) vs tools/methods/codebases (compute → TOOL register).
- **GAP — ICRAF/CIFOR methodologies under-found (concern, 2026-06-21).** CIFOR-ICRAF demonstrably publish AF suitability / land-health / restoration-targeting methodologies; this first pass surfaced almost none → a **search-coverage failure, not absence**. Next iteration must hit CGSpace (open DSpace API), `data.worldagroforestry.org`, the ICRAF/CIFOR GitHub orgs, and named ICRAF method docs directly.
- `gh search repos` multi-term queries are unreliable — single strong terms work better; a deeper GitHub pass (R `spatMCDA`-likes, GEE suitability scripts, FAO land-eval implementations) is worth a second iteration.
- Capture model = catalogue rows; where a tool's docs/code state a reusable threshold/default, extract to EV (`locator_type=file_line` + `commit_sha`) and link via `evidence_ids` — none done yet.
- `joshbrew_inat_af` and species-occurrence tools produce species envelopes — keep distinct from practice-level suitability (claim_scope discipline).

## ICRAF / CIFOR / Alliance deeper pass (2026-06-21, after gap flagged)
The first pass missed almost all ICRAF/CIFOR methods — a search-coverage failure. Targeted pass surfaced:
- **Registered now:** `d4r_diversity_restoration` (Diversity for Restoration — our-org DSS: habitat suitability + trait optimisation + seed zones; species-level) + `d4ag_diversity_agroforestry` (sister tool, explicit cacao/coffee AF). D4R is named in the project TORs.
- **Queued candidates (next iteration):**
  - **Global Tree Knowledge Platform (GTKP)** — `cifor-icraf.org/gtkp/` — interlinked DBs, maps, guidelines, **R packages**, DSS. Likely several registrable tools.
  - **SPACIAL Lab** outputs — EO/geoinformatics AF targeting (the team behind `icraf_spacial`); chase their code/methods.
  - **Agroforestry Species Switchboard** (v4, 170k spp) + **GlobalUsefulNativeTrees** (14k spp) — species DBs → repository/species-envelope (grey/repo, not practice tools).
  - **CGSpace** (open DSpace API, ~3,025 hits for the query): method candidates — "Remote Sensing & Climate Data for Targeting Landscape Restoration in Africa", "spatially-explicit threat assessment to target food-tree species (Burkina Faso)", "extrapolation suitability index (ESI) + impact-based spatial targeting index (IBSTI)".
- **Note:** several are species-level (Switchboard, GlobUNT, D4R) → species-envelope, keep distinct from practice-level suitability. ICRAF GitHub org name still unconfirmed (`gh search --owner` failed for guessed names) — find the real org before a code pass.

## Deeper iteration results (2026-06-21)
- **GitHub:** `CIFOR-ICRAF` and `icraf` orgs exist but have **0 public repos** — their code is not on a public GitHub org. So no codebase pass there; their assets are web platforms + CRAN R packages.
- **Registered this iteration:** `biodiversityr` (R. Kindt's CRAN ensemble-SDM/suitability package — species-level, NbS-agnostic) · `esi_ibsti_targeting` (ESI + IBSTI practice/technology-level spatial-targeting method).
- **KEY FINDING — ICRAF spatial tooling is mostly SPECIES-LEVEL** (Roeland Kindt's stack: BiodiversityR ensemble SDM + species DBs). That is **species-envelope, not practice-level NbS suitability** — useful but `claim_scope=species`, must not define practice rows. The genuine *practice/targeting* methods are fewer (ESI/IBSTI, ROAM, RS restoration targeting).
- **Repositories / species DBs (NOT tools — grey/species sources):** TreeGOER (48,129 spp env ranges) · GlobalUsefulNativeTrees (14,014 spp) · EcoregionsTreeFinder · Agroforestry Species Switchboard (v4, 170k spp). Search these as species/grey sources, don't catalogue as tools.
- **CGSpace method candidates (next, ~3,025 hits):** "Remote Sensing & Climate Data for Targeting Landscape Restoration in Africa" (2019) · "A framework for targeting and scaling-out interventions in agricultural systems" (2014) · "Framework for rapid country-level analysis of AFOLU mitigation options" (2020). Acquire + verify before registering.

## Phase B continued (2026-06-21, issue #65)
- **Verified + enriched** `esi_ibsti_targeting` against the real source (Tamene/Coe et al. 2017, hdl 10568/89935): extrapolation-detection → ESI (correlation-aware) → IBSTI; inputs = bioclimatic + on-farm yield-gap; demo = maize+fertilizer (Tanzania) → confirms nbs_ids blank (general ag-tech, not AF).
- **Registered** `rs_targeting_restoration_africa` (Tamene et al. 2019, hdl 10568/106885) — satellite+climate → degradation hotspots → simulate SLM/restoration interventions (AF is one of several) → nbs_ids blank per PICOS.
- **Still queued (insufficient verified detail — don't register from snippets):** "framework for targeting and scaling-out interventions in agricultural systems" (2014) · "rapid country-level AFOLU mitigation options" (2020) · GTKP resource list (403) · saraheb3 GEE code deep-read to fill `variables_used`/`weighting`.
- 11 TOOL rows. CGSpace (open DSpace API) confirmed as the productive grey/method channel — `hdl.handle.net/10568/*` resolvable, acquirable via `ingest.acquire` when EV-grade detail is needed.
- **Still queued:** GTKP resource list (403 on probe — needs another route) · the real practice-suitability code (saraheb3 GEE variants) deep-read.
