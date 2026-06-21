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
| `wocat_slm_db` | platform | SLM tech DB + mapping tool | API token-walled |
| `icraf_spacial` | webgis | dashboards | CIFOR-ICRAF |
| `wri_flr_atlas` | platform | FLR opportunity mapping | forest-restoration scope |
| `iucn_wri_roam` | method_framework | phased MCDA + stakeholder rules | High tier (stocktake-23) |

## Notes / next
- `gh search repos` multi-term queries are unreliable — single strong terms work better; a deeper GitHub pass (R `spatMCDA`-likes, GEE suitability scripts, FAO land-eval implementations) is worth a second iteration.
- WOCAT mechanisation still blocked on the API token.
- Capture model = catalogue rows; where a tool's docs/code state a reusable threshold/default, extract to EV (`locator_type=file_line` + `commit_sha`) and link via `evidence_ids` — none done yet.
- `joshbrew_inat_af` and species-occurrence tools produce species envelopes — keep distinct from practice-level suitability (claim_scope discipline).
