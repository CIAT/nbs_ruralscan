# Agroforestry — grey-lit discovery (iterative web search, 2026-06)

**Table:** T4 (+ T6 incidental) · **NbS:** agroforestry · **Category:** grey · **Run:** `grey_af_2026-06`

Exploratory, iterative web-search discovery of grey literature (reports, technical briefs, national manuals, tools/methods) — distinct from the OpenAlex peer-reviewed sweep and from the stocktake-23 benchmarked grey set. Goal: surface high-value grey that bubbles up across varied terms, including **tools and methods**.

## Why web search, not an API sweep
- **WOCAT** SLM-technologies DB has a REST API (`qcat.wocat.net/en/api/v2/`) but it is **token-walled (HTTP 401)** — needs an activated WOCAT account + a token request to the secretariat. Parked for later automation; meanwhile specific WOCAT technologies can be human-downloaded.
- **FAO TECA** is a JS SPA with no open JSON API found.
- **CGSpace** (CGIAR DSpace) IS open (`/server/api/discover/...`, 4,455 hits for "agroforestry suitability") — held as the next mechanisable channel.

## Search iterations (EN/ES/FR)
1. agroforestry land suitability spatial targeting decision-support tool/method
2. silvopasture/silvopastoral site suitability GIS mapping manual (tropics)
3. FMNR / parkland suitability targeting (Sahel); restoration opportunity assessment (WRI/ICRAF)
4. cocoa/coffee shade agroforestry zoning suitability; national AF suitability atlas (India/Ethiopia/Kenya); trees-on-farm carbon opportunity maps
5. multilingual: *aptitude agroforesterie cartographie* / *aptitud agroforestería mapeo idoneidad* → surfaced national-manual **threshold** sources (INAB Guatemala, Guinea ZAE) the English pass missed.

## Acquisition outcome
Acquire adapter: `nbs_ruralscan.ingest.acquire` (writes `{sid}.pdf` + `{sid}.meta.json` sidecar to `.cache/corpus`).

| source | status | note |
|---|---|---|
| **inab_landcap_guatemala** | acquired + **extracted** | INAB national land-capability manual (ES); slope×soil-depth → agroforestry classes Aa/Ap/Ss |
| **wri_roam_india** | acquired, **deferred** | ROAM India atlas/methods; poor text layer (garbled), no biophysical thresholds via flat text — needs table parse |
| **crs_fmnr_niger_2025** | acquired, **held** | FMNR scaling brief; only governance/tenure/labor enabling-conditions → no clean VONT canonical (see below). NGO advocacy → positive-bias. |
| icraf_tik_ethiopia | acquire_failed | HTTP 403 (cifor-icraf.org) — manual download needed |
| usda_nac_silvopasture_2025 | acquire_failed | HTTP 403 (fs.usda.gov) — manual download needed |

## Extracted → register
- **INAB Guatemala: 50 EvidenceUnits**, all verbatim-verified (Spanish native quote + bracketed English), 0 number/scope/quote flags. Variables `slope` (%) + `soil_depth_to_bedrock` (cm), `claim_basis=table`, `claim_scope=practice_technology`, across families planted_silvoarable (Aa) · shaded_perennial (Ap) · silvopastoral (Ss), 7 regional matrices. `source_category=grey`, tier=Medium (govt land-capability manual; low advocacy bias but not peer-reviewed).

## Held / flagged
- **CRS FMNR** held: its useful content is operational/enabling-environment (land tenure, governance/extension, labor, rootstock presence) which the current VONT cannot hold without silent proxy-relabelling (`protected_area_status`/`distance_to_road` were force-fit by the extractor — rejected per the no-silent-relabel rule). **PAUSE + define VONT canonicals** (e.g. `land_tenure_security`, `governance_extension_access`, `labor_availability`, `rootstock_presence`) before merging FMNR enabling-condition evidence.
- **Grey-lit positive-bias** (memory `feedback_grey_lit_positive_bias_discount`): grey over-states benefits + is not peer-reviewed → synthesis must discount, especially T6 benefit claims. Not yet implemented in `synthesis.py` — flagged for a spec.
- Tools/methods surfaced (for a tools register, not threshold EV): WOCAT Mapping Tool · Decision-Support Framework · Apps · Carbon Benefits Project; CIFOR-ICRAF SPACIAL dashboards; WRI FLR Opportunity Atlas; ROAM; Guinea ZAE atlas.
