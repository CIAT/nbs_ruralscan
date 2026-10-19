# Agroforestry T4 pipeline audit — 19 October 2026

## Conclusion

The thin table reflects both real evidence limitations and pipeline defects. It cannot currently support the claims that only 14 records contain numerical information, that all active records are approved, or that every generated row falls below a defensible 20% support floor. Do not use the current eight generated rows as validated suitability rules.

Audit scope: local working tree at HEAD `a47423c`, including existing uncommitted register changes. Read-only synthesis against current registers; no evidence, recipe, code, or review decisions changed. User supplied the Teams update in chat; the linked Teams message was not accessible through the web tool.

## Reconciled counts

| Stage | Records |
|---|---:|
| Agroforestry structural-suitability EV records | 340 |
| QA-dropped, retained in register | 188 |
| Active structural records | 152 (41 sources) |
| Species/crop excluded by current engine | 27 |
| Remaining practice-level structural records | 125 |
| With parameters current harmoniser can read, before lineage deduplication | 16 |
| With parameters after current deduplication, across emitted rows | 12 |
| Evidence IDs cited by eight generated rows | 23 |
| Generated rows | 8 |
| Preserved design rows | 10 |

Separate operational-risk lane: 99 active records. These are not additional structural T4 evidence.

The 109 practice-level records without engine-readable shape parameters are NOT all qualitative: some contain numerical class tables, explicit thresholds under unsupported keys, categorical gates, weights, or site observations. They require distinct dispositions.

Zero active structural records carry `relationship.type=observed_presence`, the exact discriminator the current exclusion code uses. Thus the update's claimed 23 observed-presence exclusions do not describe the executed gate. Some WOCAT observations instead enter synthesis.

## Findings

### 1. T3/T6 searches inflate T4 support denominators — confirmed code defect

`scripts/synthesise-recipe.py:106–111` sums every table's `n_included` for each family, without `table == T4`.

| Family | Current denominator | Sum of T4-only inclusions |
|---|---:|---:|
| Cross-family | 35 | 7 |
| Planted silvoarable | 34 | 9 |
| Regeneration/FMNR | 38 | 14 |
| Shaded perennial | 41 | 11 |
| Silvopastoral | 40 | 11 |
| Linear/boundary | 43 | 16 |
| Homegardens | 25 | 7 |

T4-only totals are diagnostic, not corrected denominators: overlapping searches, table-level historical searches, screened versus included definitions, and unique source membership still need reconciliation. The fallback `len(fam_units)` counts evidence records rather than papers. Support uses tier weights and inferred weights for unseen sources, so percentages cannot be corrected by a simple count ratio.

The 20% floor only flags selection; it does not delete rows. Low percentages therefore do not explain missing output rows.

### 2. Encoding mismatch makes numerical evidence invisible — confirmed

`recipe/synthesis.py:_harmonise` accepts only `abs_min`, `opt_low`, `opt_high`, `abs_max` plus a small alias list. It ignores examples including:

- `ev_T4_slope_wotlolan2021_1`: `threshold=35`, `direction=exclude_above`.
- `ev_tree_canopy_cover_sprenkle24_1`: threshold 25% canopy, direction below.
- `ev_t4_slope_nath21_01`: explicit class boundaries in degrees under `very_good_max_deg`, `good_min_deg`, etc.
- `ev_T4_slope_ahmad2018_1`: nested slope classes `<5`, `5–15`, `>15` percent.
- `ev_t4_mat_yadav24_1`: temperature ranking intervals differentiated by climate group.
- `ev_t4_soilph_nath21_01`: optimum-class bounds under `very_good_min/max`.

Categorical land-cover and drainage gates also cannot pass this numerical-only synthesis. `family.py:109–113` omits rows with empty params; `save_family` persists only rows, not selection candidates or the detailed reports explaining omissions.

Fix requires typed relationship handling and explicit unresolved dispositions. Do not blanket-map every class boundary or observed range to a hard exclusion: the classes have different semantics and some are unsuitable for generalisation.

### 3. Source deduplication discards different claims — confirmed

`recipe/synthesis.py:343–362` keeps one highest-ranked record per origin source for the whole variable, before evaluating its parameter usability or context. This is broader than removing citation echoes.

Examples:

- Cross-family Haile slope: a narrative mechanism record outranks and removes the numerical class-table record.
- Silvopastoral Kiziridis slope: a null-relationship predictor record retains priority over the scenario grid and the 8-degree finding. Neither scenario grids nor contextual findings should become universal thresholds, but they must remain available for their proper use.
- FMNR Weston rainfall: a site-mean record displaces the range-bearing record.

Reconcile distinct claims/contexts within source and cap source influence; collapse actual echoes, not all records sharing a source. This helper is also imported by T3/T6 synthesis: changing it needs cross-table regression coverage.

### 4. F5 crop exception never matches actual family — confirmed

The runner checks `family.endswith("shaded_perennial_crop")`; actual FAM/EV family is `agroforestry__shaded_perennial`. The policy CSV also contains the stale `_crop` identifier. Seven active F5 crop-specific records are excluded.

An in-memory probe with `allow_crop_scope=True` changes F5 output from one variable to four: slope, temperature, rainfall, soil pH. This establishes a routing defect, not approval of those values. Crop-specific synthesis must preserve the host crop parameter and applicability rather than pooling unlike crops indiscriminately. Land cover still requires categorical support.

### 5. Source support is misrepresented as threshold contribution — confirmed

`rep.used` is populated before harmonisation. Sources with empty harmonised params still enter evidence citations, justification counts and the uncertainty calculation's independent-source count. `n_sources` comes from selection support, which is a different quantity.

| Generated row | Reported supporting sources | Sources supplying readable parameters |
|---|---:|---:|
| Cross-family rainfall | 4 | 2 |
| Cross-family soil pH | 2 | 1 |
| Planted slope | 4 | 1 |
| Planted canopy | 2 | 1 |
| Planted soil depth | 1 | 1 |
| FMNR rainfall | 7 | 4 |
| FMNR slope | 2 | 1 |
| Shaded temperature | 1 | 1 |

These parameter contributors are counted before judging substantive validity. Preserve selection support, but report threshold contributors separately, preferably per parameter. Otherwise one-source rules appear to have corroboration and can evade the thin-evidence uncertainty bump.

### 6. Existing output includes site descriptions as rules — confirmed from stored quotes

- Planted slope: `ev_T4_slope_seja2022_1` quotes five land-mapping-unit slope ranges, 8–72%. Those observed ranges become minimum/maximum suitability. VONT canonical slope unit is degrees: generated 4.6–35.8 is degrees, NOT percent as stated in the update. Removing the minimum alone does not validate the maximum.
- Soil depth ≥90 cm: `ev_soildepth_inab_p92_aa_example` describes one field with >90 cm soil and 22% slope classified as Aa. It does not establish a universal 90 cm minimum.
- FMNR slope 0–2: `EV_wocat_1358_2017_003` quotes the site's flat terrain. Missing observed-presence typing lets it become a limit. The relationship also lacks its percent unit, so synthesis assumes canonical degrees.
- FMNR rainfall: `EV_wri_regreening_2015_001` encodes `abs_min=400` although its quote explicitly says regreening occurs below 400 mm; `EV_researchsquare_fmnr_2025_001` describes a study domain; WOCAT rainfall describes an application site.
- Cross-family rainfall: Haile's quote rates >1200 mm “Very high”, but stored `opt_high=1200` treats the upper edge of the merely “High” class as the optimum ceiling.

These need targeted evidence/relationship review against original artifacts before regeneration. Quotes located in the register were examined; original PDFs were not re-audited in this pass.

### 7. Reviewed does not mean approved — confirmed

Of 152 active structural records, 110 have `reviewer_ok=true`; 42 do not. Five active IDs have no entry in `pipeline/metrics/review_log.csv`. Several false-flag records have human `flag` decisions, including Haile rainfall. Thus some were reviewed but remain unresolved.

Current family synthesis excludes only `review_state=dropped`; it does not require approval. This means the output is not an approved-only compilation. An explicit draft/approved policy and unresolved evidence reporting are needed; do not equate an encountered/reviewed record with acceptance.

### 8. Cross-family evidence is isolated; selection output disappears

The runner groups EV by exact family ID. Cross-family rainfall/pH stay in a standalone family; concrete family synthesis does not inherit them. Dashboard family rendering also filters exact IDs (`docs/dashboard.html:5148`).

`methodology/schema_changes/v0.3.2_cross_family.md` explicitly leaves inheritance versus replication unresolved. This is an unfinished methodological decision, not permission to copy every cross-family rule into every family. Resolving applicability is necessary before interpreting empty family tables.

Homegardens is intentionally `qualitative_only` and currently has no active structural records; it should not be judged against the expectation of a numeric raster suitability table. Linear/boundary evidence includes selection weights, which cannot legitimately generate threshold curves.

## Repair order

1. Add an evidence-disposition audit: dropped, unresolved review, observed case, out-of-scope species/crop, selection-only, unsupported numeric encoding, categorical rule, actual parameter contribution. Preserve candidate and exclusion reports alongside rows.
2. Correct T4-only search selection; reconcile unique screened source membership before publishing support percentages. Correct F5 identifiers/policy lookup and preserve crop-specific applicability.
3. Re-review the site-description rules and contradicted bounds above. Keep all records and review history; use correction/reclassification/quarantine, never deletion.
4. Add typed relationship synthesis and claim-aware lineage handling, with regression tests for the actual failing records. Distinguish variable support from parameter contribution.
5. Resolve cross-family applicability through the existing decision process. Regenerate T4 only once valid inputs and routing are established.
6. Then assess real evidence gaps; do not launch another broad search based on today's missing-row counts.

## Verification and limits

- Executed the current `synthesise()` runner in memory; reproduced eight generated rows and inspected all per-variable reports.
- Counted structural/M2b records from CSV and JSON; both contained 439 agroforestry T4/M2b records.
- Inspected individual relationships and stored quotes; traced parameter extraction through `_harmonise`.
- Ran crop-enabled F5 counterfactual in memory only.
- Existing tests: `.venv/bin/python -m pytest tests/test_synthesis.py tests/test_family_observed_presence.py -q` → **13 passed**. These tests do not detect the real-data defects above.
- Working tree already had unrelated changes. No regeneration, commits, pushes, evidence edits or analytical fixes made by this audit.
