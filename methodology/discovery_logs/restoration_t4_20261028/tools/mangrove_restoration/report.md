# Tool discovery: mangrove_restoration

Date 2026-10-28; discovery ruleset v1.8.1; family `mangrove_restoration__tidal_coastal`.

28 distinct bounded screen records; 5 acquisition/review candidates. Inclusion is permission to investigate a source, not approval of evidence or methodology. No extraction, EV, register, recipe or Git changes.

## Actual-code findings

- [thorstenbalke/Mini-Buoy — repository and inspected implementation (commit 01c86d95bc7d)](https://github.com/thorstenbalke/Mini-Buoy): Actual R shiny app mangrove restoration GITHUB.R:334–390 tidal inundation, windows and velocity statistics; 420–428 daily inundation warnings (<100 or >800 minutes/day). HESS 25:1229 (2021) technical method inspected. Keep instrument/reference-site design, measurement calibration and regional context; daily minutes are not instantaneous percent or universally validated boundaries.
- [xiedanghan/MangroveVulnerabilityModel — repository and inspected implementation (commit edf2d2229c60)](https://github.com/xiedanghan/MangroveVulnerabilityModel): Actual ColonisationStrategy_dh.m:26–35 recruitment-window and bed-stress logic; general_input.m:37–47 stress, sediment and mortality scenario parameters. Process simulation candidate for establishment mechanisms; scenario settings are not observed global thresholds. Retain timestep, sediment regime, local calibration and paper/code shared lineage.
- [smbeselly/DFMFON — repository and inspected implementation (commit 11fed6bf1eca)](https://github.com/smbeselly/DFMFON): Actual example 02_DFMFON_run.py:154 inundation window (days), 451/521 salinity output and median, 598–610 recruitment logic; coupled Delft3D/FON example. Inspect species, model version, hydrodynamics, timestep and validation before use. Mechanistic/local parameter context, not universal suitability thresholds.
- [DunlopT/LEAF — repository and inspected implementation (commit 91a8b9c3e377)](https://github.com/DunlopT/LEAF): Actual LEAF_main_v.2.1.py:221 onward recruitment/establishment, tidal datum, inundation-free periods, burial/erosion and mortality with LEAF_inputs_v.2.1.json. Avicennia marina model context: species-specific parameters retained for mechanistic/planning review, not general practice envelope. Verify stage, timestep, datum and NSW calibration transfer.
- [tnyqu/nigeria-feasibility-analysis — repository and inspected implementation (commit 1a3c35a54d51)](https://github.com/tnyqu/nigeria-feasibility-analysis): Actual scripts/soil/run_soil_analysis.py implements OpenLandMap soil-depth suitability scores and aggregation; reported 0–5 tool rubric and surface weighting require provenance/calibration. Include as transparent local tool assumptions, not established ecological boundaries or approval of weighting.

## Holds, provenance and completeness

All included code is pinned to a commit in candidates.json; parameter files and immutable raw URLs are supplied. Copies in this staging directory are read-only screening snapshots, not acquired canonical sources. Later use requires the GitHub ingestion adapter, source metadata validation, and file:line locators. Notebook keyword-hit line numbers in code_screening.json refer to concatenated code cells, not raw .ipynb file lines; do not use them as EV locators. No DOI has been invented or registered.

No repository identity match was found in the current SRC/queue/TOOL search. Afforestation-Tracker and Scotland are known historical discovery leads; GROA is also a known lead but is referred out of active planting. Central deduplication must reconcile companion papers and existing source IDs before registration. The 2007 Scotland farmland queue paper is not this machine-learning repository.

Species models, hypothetical scenario parameters, land-capability residual classes, country legal masks and carbon optimisation must not silently become general planting rules. Dataset-only repositories remain paused under the dataset-intake rule. Generic engines are considered only through an explicit target application. Other screened records and precise exclusion/hold reasons are in screening.json.

This is a bounded first pass, not saturation. French, Spanish and Portuguese functional queries were attempted alongside English; no claim of complete multilingual coverage. GitLab and local-language institutional code catalogues were not systematically searched. Portuguese mangrove API query returned HTTP 403; this is an access limitation, not zero results. Search-engine totals and unseen results are not screened counts; n_retrieved is null. API raw metadata is preserved one directory above, including additional GROA name-collision hits not advanced to the bounded screen.

## Verbatim queries

GitHub repository-search API (per_page=8; metadata in ../mangrove_api_search.json):

- `mangrove restoration`
- `mangrove model`
- `mangrove suitability`
- `mangrove hydrology`
- `restauracao manguezal`

Web queries (shared forest/mangrove discovery session; only matching identities enter this scope’s counts):

- `github reforestation afforestation suitability spatial planting code`
- `github mangrove restoration suitability hydrology model code`
- `"Afforestation-Tracker" github`
- `"GROA" restoration opportunity assessment code`
- `github mangrove restoration model suitability`
- `github reforestation suitability Scotland woodland`
- `"GROA" "restoration"`
- `github restauracao florestal aptidao reforestacion idoneidad`
- `github "mangrove" "pyMANGA"`
- `github mangrove restoration "suitability" hydrology`
- `github "restauration" "mangrove"`
- `github "reforestación" "aptitud"`
- `"Project-Scotland-Reforestation" github`
- `github restauration forestière aptitude plantation outil`
- `github restauración manglares hidrología idoneidad`
- `Mangrove Restoration Potential Map technical methodology tool`
- `"Scotland" "Reforestation" "github.com"`
- `"restauration forestière" "outil" "aptitude"`
- `"Mini-Buoy" "github" mangrove`
- `"mangrove" "restauração" "ferramenta"`

## Technical-method follow-up

Mini-Buoy companion method: https://hess.copernicus.org/articles/25/1229/2021/index.html (technical text inspected). Potential successor `Ale0430/MiniBuoy-App` surfaced via https://cailadd90.github.io/MiniBuoyHandbook/chapters/analysis.html; not code-screened, not counted or included. Reconcile version lineage before extraction. TNC map report is a separate grey-lane referral; neither its full implementation nor dataset generation was audited here.

## Central screening correction

Final registrar inclusion is four repositories. Nigeria soil-scoring tool moved to hold: inspected code does not establish mangrove-specific application. Original agent shortlist had five; screened count remains 28. DFMFON example species are Avicennia_marina and Rhizopora_apiculata (source spelling); parameters remain species-specific.

## Reproducibility files

Final candidates, screening decisions and exact protocol JSON are tracked beside this report under `methodology/discovery_logs/restoration_t4_20261028/tools/mangrove_restoration/`. Central metadata verification and scope screening precede registration; candidate counts are not evidence counts.
