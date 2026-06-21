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
