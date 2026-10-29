# Mangrove code review — 29 October 2026

This batch reviews Mini-Buoy, Mangrove Vulnerability Model and DFMFON for the authorised mangrove-restoration tidal/coastal T4 lane, using extraction ruleset v1.8.0. It follows the selected implementations into directly relevant configuration and helper files. **Sixteen pinned text artifacts were checked; 34 native-code findings retained; zero SRC or EV records admitted.** This is a bounded code review, not a whole-repository audit, dataset intake or execution of the coupled models.

`artifact_checks.json` records repository, commit, path, team-openable URL and verified byte hash. `claims.json` contains contiguous quotes with exact line locators, interpretations and scope holds. `behavior_probes.json` and `verify_audit.py` preserve reproducible small-function checks. Positive variable-use evidence and literal directions/parameters remain visible; lack of calibration alone is not treated as absence of evidence.

## Mini-Buoy: measurement and screening

The README explicitly identifies hydrological assessment for mangrove restoration. The selected R application analyses a site and reference deployment, producing eight indicators: monitoring period, mean tide duration, flood frequency, longest inundation-free window, daily inundation duration, median current speed, 75th-percentile current speed and flood-minus-ebb median speed. Reference outputs are the same procedure, not independent evidence.

The complete warning set is retained:

| Input | Implemented condition | Meaning in application |
|---|---|---|
| Mean tide duration | >=1,440 minutes | Does not follow tidal pattern |
| Monitoring period | <=15 days | Deployment should be longer |
| Absolute median–75th-percentile velocity difference | <=0.01 m/s | Below detection limit |
| Mean daily inundation | <100 or >800 minutes/day | Not suitable for mangroves; 100 and 800 included as generally suitable |
| Maximum inundation-free window | <1 day | No window of opportunity detected |
| 75th-percentile velocity | <0.15 m/s | Low current; otherwise high current |

Only the daily-inundation message explicitly labels suitability. “High current” is not itself an exclusion; short deployment and detection-limit warnings concern measurement quality, not ecological limits. The 100–800 band supports a bounded screening relationship in this tool; it does not establish universal limits, a continuous response curve or species-specific tolerances. Its primary calibration and transfer context still require the handbook/paper.

The method assumes a particular accelerometer layout and CSV structure, uses a GMT placeholder, infers sampling interval from two timestamps, takes a 15-minute running median and downsamples. Submergence is median acceleration <=-0.5; current calibration is `1.173 + 1.059*y`. A nine-sample low-tide window separates events, and four 15-minute samples at each tide end are removed from current analysis. These are instrument-processing parameters, not mangrove thresholds.

The code adds 31 minutes at each end despite a comment saying 15 minutes. The reported monitoring period includes this padding. Daily inundation used by the warning comes from thresholded sample counts, not the separately calculated sum of event durations. Deployment timing, short/empty/single-event behavior and calibration uncertainty therefore remain review questions. The R application was not executed; boundary probes evaluate the literal warning expressions only. The repository's handbook PDF is a follow-up, not claimed as acquired or read here.

## Mangrove Vulnerability Model: normalization and species context

The README describes long-term bio-morphodynamic responses to sea-level rise and human pressure. The inspected scenario models natural colonisation; it is not an active-planting trial. Its vegetation factsheet identifies *Avicennia marina* while also saying “Black mangrove”; the naming discrepancy is preserved without inventing a synonym. All 13 general configuration fields, the colonisation timestep and all 14 life-stage fields remain in the quoted factsheet.

The recruitment path requires a configured season, **0 < P < 0.5**, and bed stress below `TauThres=0.2`. The upstream definition is decisive: flooded samples are those with water depth >0.1 m, and **P divides each cell's flooded-sample count by the spatial maximum count**, not the number of observation timesteps. A cell flooded for 20 of 100 samples has P=0.5 if the wettest cell has 40 flooded samples, but P=0.2 if that cell has 100. The same absolute inundation can therefore cross the recruitment boundary as the modeled domain changes. P=0.5 cannot safely become 12 hours/day.

Stress is computed as a 90th percentile of vector magnitude after dry samples are zeroed, despite an older comment mentioning mean stress. Later recruitment uses annual means of stored ecological-step quantities. The stress threshold's units are not printed in the configuration and are not inferred here. The factsheet's 0–0.60 habitat bounds describe a different model component from the recruitment P<0.5 condition; they are not silently reconciled or treated as contradictory measurements.

Other retained settings include waves off, 12 ecological timesteps, a 360-day year, morphological factor 30, initial individuals per cell, grid-cell area and growth/death increments. The sedimentation threshold 0.01 m is explicitly associated with another strategy; the inspected dispatcher selects strategy 1. It is not demonstrated as an active recruitment cutoff. Mortality accumulates annual stress/competition marks <=0.5 and calls a mortality routine at five marks, with no mortality in the first cold-start year. This is simulated persistence, not observed restoration success.

The inspected call chain establishes source variable use and preserves parameter semantics. Full fitness/growth, competition, allocation, mortality-removal and Delft3D internals remain outside this review. The technical PDF and cited studies require their own verified acquisition and source review. No bibliographic DOI was promoted from repository text into the queue.

## DFMFON: species recruitment and implementation behavior

DFMFON couples Delft3D-Flexible Mesh with MesoFON. Its README describes a schematized muddy fluvial–tidal delta inspired by Porong, Indonesia and reports comparisons with observed development. Those reported validation claims were not independently checked here. The selected example uses *Avicennia marina* and the code identifier `Rhizopora_apiculata`; its spelling matters because another function uses `Rhizophora_`.

The configuration's 90-day coupling, morphological factor 90, 10-m raster, 200-m tiles, LLWL -1.1 and initial salinity 35 are scenario/setup choices. Salinity 60 is also a nodata value. None is an ecological optimum or exclusion by itself. The nominal 3/5-day settings are not passed to the helper: the inspected helper hardcodes three/five consecutive daily samples, regards daily maximum depth <=0.01 m as dry, and forces scores to zero where bed level is below zero. That bed datum requires explicit interpretation.

The helper counts successful window starts and divides by all days, including days without a complete trailing window. Five dry days yield scores 0.6 and 0.2; ten dry days yield 0.8 and 0.6. These are window-frequency scores with record-length effects, not validated survival probabilities. A dry cell below zero bed level receives zero under the separate gate. The upstream conversion to daily maxima also depends on timestep/interpolation choices.

Salinity enters seed production through `1/(1+exp(-0.18*(72-salinity)))`, multiplied by crown area and species coefficients 0.03/0.006. It decreases production with increasing salinity in this model; the units, cited calibration and transferability remain unresolved. Dispersal adds residual-current displacement to a random initial location; it supplies no establishment-velocity cutoff. January seasonality, two-year sapling conversion and specified sapling dimensions are model life-history assumptions. The exact 730-day boundary belongs to both the transfer and retained-seedling conditions.

Small probes of the pinned functions confirm material implementation concerns:

- With 30 seedlings, positive scores 0.1, 0.31, 0.51 and 0.71 retain 20, 15, 10 and 30 seedlings. Thus intermediate increases in the named survival score reduce retained counts. The caller separately removes zero-scored rows. Random selection changes identities, not these retained counts.
- The erosion helper triggers on initial-minus-final bed level >=0.06. Its species-removal pattern `Rhizophora_` does not match `Rhizopora_apiculata`, the identifier used by the example. In the two-cell probe, those seedlings survive the intended species deletion.
- The erosion helper appends only qualifying eroding cells. When one cell erodes and another does not, the returned table loses the unaffected cell's seedlings. When neither qualifies, its fallback returns the original table. The probe stubs only spatial cell lookup; the original filtering function executes unchanged.

These are findings about this pinned example, not claims that every release or application behaves identically. Full application execution was not attempted. Runtime versions are recorded (NumPy 2.4.6, pandas 3.0.3); the code also uses legacy pandas APIs elsewhere, so these probes do not establish end-to-end compatibility. MesoFON Java internals, hydrodynamic calibration, external inputs and other example configurations remain unreviewed.

## Admission, credibility and follow-up

All three have verified repository/file hashes, but queue records still lack the required document-title identity stamp. The page/section ingestion gate rejects `file_line` and requires a dedicated code admission route. As in the preceding forest-code review, hash verification is not misrepresented as title verification. `admission_holds.json` records the actual gate responses. No gate, schema or skill was weakened.

Before EV admission, establish canonical repository identity, bind every companion file to its commit and exact lines, preserve one independent lineage per project, and apply the existing number/scope/ontology checks. Suitable candidates include Mini-Buoy's directional screening band and species/model-use records from the two simulations. Minutes/day, spatially normalized hydroperiod and multi-day dry-window frequency must not be mapped as interchangeable quantities. Bed stress, salinity, current and erosion variables need exact ontology matches; coastal salinity is not automatically a soil-salinity proxy, nor bed erosion a catchment erosion-risk index. Preserve species-specific scope and distinguish natural recruitment from a restoration intervention.

Provisional discovery tiers are unchanged. Mini-Buoy has explicit restoration-assessment relevance and transparent processing; its calibration source remains to be reviewed. The two models have identifiable research lineage and detailed implementations, but source-code transparency, institutional association and README validation claims do not demonstrate transferable ecological limits. No seminality, independence or conflict-of-interest bonus is assumed. Companion files are not additional independent studies. Methodological direction and source values remain in the audit while these questions are resolved.

Specific follow-ups are the Mini-Buoy handbook/calibration study; Vulnerability Model's technical PDF, source studies and remaining fitness/allocation helpers; and DFMFON's publication, primary seed-production/propagule calibration, coordinate datum, versioned environment and Java model. Existing corpus must be checked before acquiring these leads. Dataset inputs remain under the paused dataset-intake policy.

## Progress and retrospective

Only the three queue records' notes and blockers change; acquired status and identity stamps remain unchanged. SRC, EV, progress ledger, generated files and human decisions remain intact. No discovery search, extraction, verification or source-completion stage is stamped. Selected-artifact review accounting reaches **20 of 29 new candidates**, leaving **nine candidates plus separate ITTO reuse**, alongside unresolved holds from inspected sources.

This bounded review applies existing safeguards for proxy mismatch, model assumptions, species scope and source-specific calibration. It adds concrete code observations and probes, not a claim of improved corpus-wide error rates. No extraction sweep occurred and no empty sweep metric or learning-cursor advance is fabricated. Hash/locator verification, probes, preservation checks and relevant ingestion tests are recorded in `validation.json`.
