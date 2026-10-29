# Forest code review — 29 October 2026

Three queued code projects were reviewed at their acquisition-pinned commits: Luk-kar/Afforestation-Tracker, worldbank/progreen_suitability and langoodall/Project-Scotland-Reforestation. The bounded lane remains forest-restoration active planting / T4, under extraction ruleset v1.8.0. This is a source-code review, not a new discovery search, whole-repository audit, runtime deployment or validation of ecological predictions.

**Result: 22 anchored review records, all 30 ProGreen notebook cells inventoried, zero admitted EV units.** Variable use, source directions and literal parameters are retained in the audit; code-admission and substantive mapping/transfer questions remain open. Missing calibration alone is not the reason for retaining these outside EV. No source-title verification stamp was invented to pass the document identity gate.

## Coverage and provenance

`artifact_checks.json` verifies immutable commit, repository, file path and SHA-1 for ten text artifacts: six previously acquired implementation/configuration files plus three README files and Tracker's data-acquisition implementation acquired through the existing GitHub adapter. Each remains team-accessible at its pinned URL. `claims.json` contains contiguous native code quotes and exact line locators. `progreen_cells.json` preserves every decoded cell, its raw JSON line span, and its disposition; it is an audit, not a replacement native code snapshot.

Reviewed analytical paths include Tracker's complete classifier/configuration/data acquisition; ProGreen's classifier and complete notebook; Scotland's preprocessing, all four scenario masks, final predictor selection, five-model training setup, probability/ensemble filters and external importance/validation-output dependencies. Selected code does not establish coverage of every repository file. Scotland's older `Scotland.Rmd`, dashboard, remote StoryMap/video, external CSV/raster inputs, trained models and rendered figures remain outside this review. No source datasets were ingested.

## Afforestation Tracker

Four inputs actually decide the mask: slope, precipitation, root-zone moisture and land cover. Elevation and SOC are displayed/acquired but are not direct classifier inputs; suggested future species mapping in the README is not implemented species suitability.

The raster path requires slope **<15**, precipitation **>=200**, moisture **>=0.2**, and grassland/bare cover. The point path instead requires slope **<=15** and **either** the rainfall or moisture condition. Three concrete counterexamples in `behavior_probes.json` distinguish the paths. Both preserve decreasing slope and increasing rainfall/moisture logic within this authored screen; no single reconciled response is claimed. Configuration labels slope in degrees, not percent. WorldCover codes 30 and 60 mean grassland and bare/sparse vegetation; these are not evidence that intact native grasslands should be converted.

Precipitation is summed over the configured 2023 period; moisture is averaged over June–October 2020. They are neither contemporaneous observations nor a demonstrated climatological annual envelope. Metadata for exact scaling/depth and scientific calibration remain necessary. The code documents a Sahel planting tool, but establishes neither ecological-restoration eligibility for every selected cell nor empirical survival validation.

## ProGreen

The README describes a rudimentary guide for task teams. Its Kyrgyzstan notebook uses ten analytical inputs plus an administrative mask. All ten table rows, all eleven weights and all eleven WorldCover mappings are preserved in `progreen_cells.json`. Maximum temperature is not mean annual temperature; NDVI anomaly is not tree canopy; 200-cm carbon data cannot be equated to the table's tons/ha without metadata.

Several distinctions matter before any model-use EV admission:

- The table says rainfall >400 mm; code uses a minimum of 50 on raster bands, classifies them, then sums scores. PET is handled similarly. This is not annual precipitation calibration.
- The table's temperature <30 is not enforced; code scales maximum temperature upward with no specified bound. pH minimum 8.3 differs from documentation's 8.4 and uses 200-cm input. The table's “Exclusion Criteria” heading does not consistently explain whether inequalities identify excluded or retained values.
- Elevation scales upward until 2,250 m, then excludes higher cells. Slope is binary at 45, but is derived with `slope_riserun`, not demonstrated degrees. DEM resampling precedes terrain derivation.
- Aspect uses 225/315/360 breaks and claims north is 270; the directional convention requires checking. The generic classifier leaves the last bin unconverted.
- Land-cover code assigns 100 to bare land, herbaceous wetland and mangroves, and 50 to trees/crops, contrary to the summary's forest/desert exclusions. These scores cannot authorise habitat conversion.
- Source weights are NDVI/rainfall/PET/maximum temperature/land cover = 2, pH/carbon/elevation = 1, slope/aspect/admin mask = 0.1. They are arbitrary source settings, not runtime MCDA weights or measured importance. Weighted scores are summed and normalized, then intersected with all nonzero masks; a legitimate zero score is therefore also treated as exclusion.

Inspected numerical function probes confirm three additional implementation problems: in-place range replacement changes NDVI's first two bins to 100 rather than intended 1 and 5; a value at the final NDVI break 250 returns bin index 6; aspect 360 returns bin index 3. A lower bound of zero is ignored by truthiness checks: the carbon example gives raw -10 a score of 100. These results describe this pinned code, not observed ecological responses. Only the inspected pure `re_classify` function was executed with tiny synthetic arrays; no external application or geospatial workflow was run.

The README also lists a human-settlement layer absent as a separate notebook input; maximum temperature and NDVI appear in the notebook instead. No claim that the README and implementation describe identical criterion sets is made.

## Scotland Reforestation

The project classifies three native woodland types from their observed distribution: Scots pine, oak woodland and birch. Oak and birch labels do not identify single verified taxa. Pine labels include both pinewood and regeneration zones. These are potential forest-type predictions, not observed planting-success outcomes; species/system context must survive any eventual EV mapping.

Eight final predictors are rainfall, maximum temperature, sunlight hours, continentality, aspect, slope, an AWC predictor labelled `Soil_Drainage`, and elevation. Minimum temperature is explicitly removed for collinearity. Rainfall is an average of annual totals for 2013–2022; maximum temperature is averaged from the input monthly series, not an annual extreme. Continentality is formed from selected warm/cold months, not mean temperature. AWC is read from field `AWC` and later labelled “Available Water Capacity (mm)”; mapping it to `soil_drainage` would repeat a known proxy defect. Depth and semantics must be established before mapping it to `soil_water_retention`.

The scenarios exclude existing woodland and elevations **>650 m**. A nearby comment says “<600m”; code and comment are preserved separately. Scenarios 1–3 remove national parks; scenario 4 does not. Land-capability exclusions relax from limited/very limited/unsuitable to unsuitable only, with water/built-up excluded. These are local scenario choices, not proof of legal prohibitions or universal forest limits. The initial analysis already restricts the footprint to a pinewood eligibility zone and removes named EUNIS wetland/urban/rock/coastal classes; it cannot estimate an unconstrained global opportunity space.

Training and scenarios are independently standardized, and aspect encoding needs reconciliation between training and prediction. Terrain derives after DEM coarsening. Random stratified splitting and internal cross-validation are implemented, but selected files do not include numeric validation or permutation-importance outputs. The >=0.8 probability and >2/>3 ensemble-vote filters are model display/selection criteria, not establishment probabilities. All these methodological holds precede adoption of any predicted direction or numeric envelope.

## Credibility and admission

All three remain **low, provisional screening candidates**: transparent code improves traceability but does not replace validation. Tracker provides no threshold-study provenance in the inspected files. ProGreen has World Bank/GOST institutional authority and an explicit scoping purpose, but its own description and code conflicts limit evidential strength. Scotland provides a named author, environmental preprocessing and validation procedures, but results and spatial transfer remain unverified here. Sahel, Kyrgyzstan and Scotland contexts are distinct; repository ownership or recency cannot justify global ecological limits. No seminality bonus, independent replication, or absence of conflicts is inferred. Companion files from each repository count as one lineage, not independent votes.

The existing GitHub acquisition adapter supports immutable code snapshots. However, the queue identity gate still requires DOI/title verification, and these three selected code files have no valid document-title stamp. The central page/section ingestion script explicitly rejects `file_line` locators and requests their dedicated adapter. `admission_holds.json` records the actual identity-gate results. The extraction skill requires both verified source identity and the dedicated code route; setting `title_verified=true` merely because a repository hash matches would misstate what was verified. No adapter or schema was changed in this bounded evidence review.

Next intake work must bind canonical repository identity to each pinned companion file, verify exact quoted lines/commit/hash, preserve one lineage, and pass the existing number/scope/ontology gates before admitting model-use records. Missing calibration alone must not discard demonstrated variable use or code directions. Tracker's divergent paths, ProGreen's documented-versus-executed settings, and Scotland's forest-type/AWC/scenario distinctions must remain visible on review cards. None can be promoted directly into executable T4 rules.

## Progress, retrospective and checks

Only three acquisition-queue `blocker` and `note` fields change. Status remains acquired, identity stamps unchanged. SRC, EV, analytical tables, generated files, progress ledger, search register and human decisions remain byte-identical. No extraction, verification or whole-source completion is stamped.

PR #476 merged while this batch began; this branch starts from that merged state. Selected-artifact review accounting reaches **17 of 29 new candidates**, leaving **12 candidates plus separate ITTO reuse**, as well as the explicit admission/semantic holds from reviewed sources. This measures inspected candidates, not extracted or approved evidence.

Existing safeguards cover proxy confusion, source-specific weights, constrained footprints, missing outputs and contradictory calibration. This review also exposed concrete code behavior and an unresolved code-admission workflow. The observations are preserved for intake follow-up; no ruleset change, global feedback-cursor advance or improved corpus error rate is claimed. Because zero units were admitted, this is a source-review closeout rather than an extraction sweep; no empty ingestion or sweep-completion metric is manufactured. Hash/locator checks, small numerical probes, queue/register preservation and relevant ingestion tests are recorded in `validation.json`.
