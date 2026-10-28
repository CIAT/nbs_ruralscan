# Tool discovery: forest_restoration

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `forest_restoration_t4_discovery_20261028_tools`, ruleset **v1.8.1**, actual family `forest_restoration__active_planting`. Registered by `scripts/register-discovery.py` on 2026-10-28: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `forest_restoration_t4_discovery_20261028_tools`, ledger per `--ledger`.


Date 2026-10-28; discovery ruleset v1.8.1; family `forest_restoration__active_planting`.

30 distinct bounded screen records; 3 acquisition/review candidates. Inclusion is permission to investigate a source, not approval of evidence or methodology. No extraction, EV, register, recipe or Git changes.

## Actual-code findings

- [Luk-kar/Afforestation-Tracker — repository and inspected implementation (commit fc46b21c2a53)](https://github.com/Luk-kar/Afforestation-Tracker): Actual siting classifier: app/stages/data_categorization.py:36–44 config; 102–111 raster requires slope<15, precipitation>=200 AND moisture>=0.2; 128–133 point uses slope<=15 and rainfall OR moisture. Material inconsistent semantics; annual rainfall aggregation and native nonforest eligibility require audit. Source-design evidence only; no calibrated practice cutoff.
- [worldbank/progreen_suitability — repository and inspected implementation (commit ffed0c2b9079)](https://github.com/worldbank/progreen_suitability): Actual generic classification engine src/pro_green.py:59–95 plus Suitability_Analysis.ipynb application configuration (rainfall, temperature, evapotranspiration, soil and slope). Include application-specific example only; generic engine is not an NbS practice. Confirm aggregation order, units, threshold rationale and validation before extraction; hosting organisation does not establish validation.
- [langoodall/Project-Scotland-Reforestation — repository and inspected implementation (commit 4d3b98e7a52b)](https://github.com/langoodall/Project-Scotland-Reforestation): Actual Scotland Clean.Rmd:465–537 land-cover, national-park, elevation and land-capability scenario masks; 650–720 predictors and Scots pine/oak/birch woodland labels. scotland.py has RF/XGB training and importance. Species/woodland occurrence prediction is not establishment validation. Retain scenario method audit; species model thresholds cannot define general practice. Code elevation mask >650 differs from nearby comment <600; policies require contextual review.

## Holds, provenance and completeness

All included code is pinned to a commit in candidates.json; parameter files and immutable raw URLs are supplied. Copies in this staging directory are read-only screening snapshots, not acquired canonical sources. Later use requires the GitHub ingestion adapter, source metadata validation, and file:line locators. Notebook keyword-hit line numbers in code_screening.json refer to concatenated code cells, not raw .ipynb file lines; do not use them as EV locators. No DOI has been invented or registered.

No repository identity match was found in the current SRC/queue/TOOL search. Afforestation-Tracker and Scotland are known historical discovery leads; GROA is also a known lead but is referred out of active planting. Central deduplication must reconcile companion papers and existing source IDs before registration. The 2007 Scotland farmland queue paper is not this machine-learning repository.

Species models, hypothetical scenario parameters, land-capability residual classes, country legal masks and carbon optimisation must not silently become general planting rules. Dataset-only repositories remain paused under the dataset-intake rule. Generic engines are considered only through an explicit target application. Other screened records and precise exclusion/hold reasons are in screening.json.

This is a bounded first pass, not saturation. French, Spanish and Portuguese functional queries were attempted alongside English; no claim of complete multilingual coverage. GitLab and local-language institutional code catalogues were not systematically searched. Portuguese mangrove API query returned HTTP 403; this is an access limitation, not zero results. Search-engine totals and unseen results are not screened counts; n_retrieved is null. API raw metadata is preserved one directory above, including additional GROA name-collision hits not advanced to the bounded screen.

## Verbatim queries

GitHub repository-search API (per_page=8; metadata in ../forest_api_search.json):

- `afforestation`
- `reforestation suitability`
- `woodland suitability`
- `restauração florestal`
- `reforestacion`
- `GROA`

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

## Central scope hold

Afforestation-Tracker remains a pending method-audit candidate only. Grassland/barren-land eligibility and inconsistent scalar/raster conditions must be resolved before extraction; no ecological or habitat-conversion rule approved.

## Reproducibility files

Final candidates, screening decisions and exact protocol JSON are tracked beside this report under `methodology/discovery_logs/restoration_t4_20261028/tools/forest_restoration/`. Central metadata verification and scope screening precede registration; candidate counts are not evidence counts.
