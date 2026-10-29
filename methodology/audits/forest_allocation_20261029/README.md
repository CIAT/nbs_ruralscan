# Three-source forest allocation review — 29 October 2026

Reviewed Chen et al. (2021), Nurda et al. (2020) and Poccard-Chapuis et al. (2021) together under extraction ruleset v1.8.0. The authorised family remains `forest_restoration__active_planting`, with operational-risk evidence considered separately. All 54 main-paper pages are accounted for. **No source or evidence records were added:** none of these papers separates active ecological planting sufficiently to justify admission to this family. The papers remain acquired, with explicit pre-registration holds rather than false completion stamps.

| Source | Pages | Main-paper inventory | Disposition |
|---|---:|---|---|
| Chen — Three Gorges FLR | 9 | 5 tables, 4 figures; six criteria with full classes and weights | Mixed FLR activities; restoration techniques deferred by authors; aspect conflicts unresolved |
| Nurda — Indonesian forest extension | 21 | 10 tables, 8 figures; five criteria with full classes and expert weights | Production/conservation zoning includes palm oil; ambiguous settlements measure and class gaps |
| Poccard-Chapuis — Amazon landscape restoration | 24 | 9 tables, 6 figures; four mapping inputs, five landforms, full service rankings and ordered rules | Agricultural allocation and secondary regrowth; no active-planting establishment calibration |

The deterministic indexes were rebuilt and all-VONT retrieval packages generated. `artifact_checks.json` records PDF hashes, verified metadata/opening-title matches, page coverage and rendered-page hashes. `page_claim_inventory.json` covers every page, table, continuation and figure with a disposition; it does not claim that every numeric result has become evidence. Key analytical tables and map legends were visually checked. No named supplement was observed in these PDFs; no publisher-side supplement search or supplemental completeness is claimed.

## Retained criteria and defects

`chen_criteria.json` preserves all six weights (0.21/0.23/0.15/0.16/0.12/0.13), every suitability interval, six aspect score positions, eleven soil-type rows, land-use masks and both result tables. The 175-m threshold refers to the local reservoir waterline. Slope classes are justified partly by operational feasibility. Soil organic matter is not soil organic carbon; soil types are not silently mapped to USDA texture classes.

Chen's prose says more light improves vegetation growth, but the table gives shaded aspects the highest score. Two partly sunny bearing ranges overlap. Table 2 places score 80 in suitability level 1 while the equations put it in the moderate interval; soil-type class boundaries also overlap without endpoint closure. All versions remain visible. Reported slope shares use the total recoverable area denominator, not the within-class denominator suggested by some prose. None of these numbers becomes an executable response function.

`nurda_criteria.json` preserves every class, direction, area, 25 expert weights, five printed averages, five percentage weights and final zone allocations. Settlements are unitless in the table, with an unexplained 214–264 gap; the map ranges from 264 to 418. The river table jumps from 13–21 m to >29 m, whereas its map shows 21–29 m as the final class. Metres are explicitly printed for river and road distances; they were not repaired to kilometres. Average weights total 0.716 while percentage weights total 100; the apparent normalization was not substituted for the source. LULC's printed average exceeds settlements despite the prose ranking settlements first.

Nurda's classification accuracy assesses land cover, not establishment success. Calibration references include landslide mapping, surface irrigation and island development; their validity for ecological restoration has not been established. Road access would belong to operational risk if practice applicability were established. Urban land classified S3 is not a hard exclusion. The paper's references to wood and palm oil production prevent treating its entire criterion set as ecological restoration evidence.

`poccard_criteria.json` preserves four soil categories, five slope classes, the 10-m ravine buffer, 10-m HAND parameter, 900-pixel/81-ha flow accumulation setting, all five ordered classification rules, and all fifteen forest-service ranks. These describe landscape units and service priorities. They do not establish survival limits. The 8–10% mechanisation slope limit concerns agriculture; HAND height is not measured groundwater depth or flood tolerance. Euterpe oleracea, cocoa, palms and Brachiaria humidicola remain explicit crop/species pointers, not generic forest envelopes.

Poccard-Chapuis's Table 9 prints overlapping road-distance headings and a first-column total inconsistent with its component rows. Those values are preserved, not repaired. Several change percentages elsewhere use a later-area denominator. The source itself warns that canopy bias and a 90-m DEM resampled to 30 m limit farm-level use. Its illustrated restoration plan is not independent validation of planting success.

## Credibility and applicability

All three are peer-reviewed and regionally relevant, with transparent main-paper methods. None supplies independent validation of active-planting suitability. Chen's expert-informed model is local to a Chinese reservoir landscape; unreported expert agreement is not measured performance. Nurda validates LULC but combines distinct forest purposes; unclear classes and borrowed calibration constrain reuse. Poccard-Chapuis draws on substantial farmer knowledge and landscape observations in Brazil, but describes agricultural intensification and regeneration rather than an active-planting treatment.

Provisional discovery-tier judgements remain unchanged; no SRC tier was assigned. Recency does not overcome practice mismatch. No seminality or independence bonus is assumed. Chen discloses research funding; Nurda reports no external funding; Poccard-Chapuis reports ANR and CGIAR support. The papers report no conflicts of interest. Country-specific land systems and reservoir/terrain conditions require transfer review before any LIC/LMIC application.

## Followups and progress

`followups.json` states the three concrete practice questions and cited-primary leads. Brancalion et al. (2016), comparing passive and active restoration in Brazil, is a potentially useful followup; check existing corpus before acquisition. Wang's restoration thesis and the Brazilian mapping/landscape studies remain citation seeds. HAND, TerraHidro, TOPODATA and DINAMICA references are method/code leads only: no repository was inspected, version-pinned or registered in this batch. No DOI was copied from a bibliography into the acquisition queue.

Only the three queue rows' `blocker` and `note` fields changed. Existing status, acquisition location and verified identity fields are preserved. All 542 SRC records and 5,214 EV records remain unchanged; `preservation.json` checks this against the branch base. No search, extraction, verification or human-review completion was stamped. No analytical schema, generated JSON, recipe, human decision or global learning cursor changed.

Main-paper accounting now covers 11 of the 29 new discovery candidates. **18 candidates plus the separate ITTO reuse task remain**, alongside unresolved holds and supplements from reviewed sources. This count describes review coverage, not extracted or approved sources.

## Retrospective

This review exercised existing safeguards for wrong practice, residual-land allocation, source-specific weighting, proxy equivalence and conflicting tables. Zero admitted units is the supported result, not a missing extraction quota. No new defect category or ruleset change is claimed. Global metrics remain a corpus snapshot; this bounded source review cannot demonstrate improved corpus-wide error rates. Schema/coverage, preservation and test results are recorded in `validation.json`. Central evidence ingestion and quote/numeric gating are not invoked with an empty batch; existing records were not re-evaluated or reapproved.
