# Mangrove T4 bounded first-pass extraction, 28 October 2026

This is a staging-only recovery pass under ruleset v1.8.0, using the signed standalone `mangrove_restoration__tidal_coastal` scheme. It neither approves evidence nor changes methodology, families, registers, recipes, weights or progress. The earlier forest F4 proposal is superseded. The full corpus is **not** claimed swept.

## Reconciliation

- 184 mangrove EV records; 171 active. Active T4/operational lane: **39**, comprising **12 structural** and **27 operational**. None has `reviewer_ok=true`.
- Those 39 have **zero matched review-log rows and zero matched dashboard decision records** in the files inspected. The wider mangrove scope has historical review records and six dashboard decision matches, all in the effect lane. No repeat-review request is inferred merely from empty/false approval. `pipeline/review/decisions.json` is absent in this worktree; any unsynced decisions elsewhere remain unknown.
- 31 canonical SRC sources linked to mangrove scope/evidence; all 31 PDFs exist in the provided corpus. This does not prove complete source extraction. The 39 lane units belong to 17 sources.
- Existing structural records: three GMA guideline records and nine WOCAT observed-presence records. WOCAT case-site slope, depth, water table, texture and climate are context, not global suitability cutoffs.
- No mangrove T4 CSV was present at the starting snapshot. No mangrove-specific tool source is registered among the 31 sources. A README/tool overview cannot close the missing code/parameter review.
- Exactly **one** SRCH record has mangrove or its legacy family as its explicit scope: T4 grey, 30 September 2026. The larger keyword-matching search collection in `reconciliation.json` includes other scopes' exclusions and effect searches; it must **not** be counted as mangrove's completed four-process protocol. New searches: zero.
- The stocktake has **Blanco-Sacristán et al. (2022), Mangrove distribution and afforestation potential in the Red Sea**, which is absent from SRC and the acquisition queue and has no recognisable named corpus artifact in the provided roots. Its stocktake DOI remains unverified in this pass. The later targeted OneDrive pass located this original PDF; see the addendum below. Do not extract the stocktake summary as source evidence. Whether its MaxEnt community/species distribution model transfers to restoration is unresolved until the paper is read.
- A full filename pass finds **eight** mangrove stocktake papers with no exact title-prefix SRC/queue matches: Blanco-Sacristán 2022, Sahana 2022, Hu 2020, Borges 2017, Aduana-Alcantara 2023, Al-Huqail 2024, Hossain 2003 and Jusoff 2008. `stocktake_reconciliation.json` retains every stocktake field and the exact matching protocol. These are unverified seeds, not additional established source votes. All eight original scoping-library PDFs were subsequently located; see the addendum below.
- The September grey log explicitly deferred Lewis & Brown 2014 because the located copy was third-party hosted. This is an acquisition/domain hold, not proof of paywall or exhaustion of OA recovery.

## Deterministic recovery

Two existing team-accessible sources were indexed with table capability, retrieved using `package_for_extraction_multi(force=True, full_tables=True)`, and opening-title/queue-identity checked:

| Source | Artifact SHA1 | Prior scope | Added staging |
|---|---|---|---|
| GMA 2023 Best practice guidelines | `aedaccc56bef326810eb87bad8fe9d4463c419a1` | T4, legacy mangrove family | Four units |
| WB 2025 Mangroves for Coastal Resilience in Bangladesh | `cd99ab12d31f4106f3f456577c247ad53fa32b50` | T3/T6, legacy mangrove family | One unit |

`artifact_identity.json` records canonical-source reuse explicitly; no duplicate source or independent study vote is created. GMA's registered hash is blank, so the actual hash is retained in this staging manifest. Both queue records have verified titles and publisher acquisition routes, and both SRC rows carry team library paths.

The final `units.json` contains **five** native, page-sliced units: historic mangrove habitat; local-datum elevation envelope; planting when propagules are insufficient after suitable conditions are established; operational stakeholder/legal feasibility; and WB's regional 10 km proximity screen. All are unapproved and non-executable. The proximity unit retains source method lineage to Gijón Mancheño 2021 and World Bank 2024 and does not automatically add an independent vote.

An initially staged inundation-extremes unit was **withdrawn after adversarial review**: its passage measures frequency, whereas the existing ontology variable measures duration. The passage remains in the held source-row inventory; no synonym substitution or claim deletion from an existing register occurred.

## Coverage and remaining holds

`source_row_inventory.csv/json` accounts for 92 selected claim/table/continuation/hold rows. `page_inventory.json` records all 193 PDF pages and marks pages not claim-swept explicitly. `*_structure.json` retains automatic table, figure, section and supplement inventories. Automatic extraction can produce false table blocks from prose and repeated caption references; those are navigation aids, not proof of full row coverage.

GMA Figures 3, 5 and 8 and Table 1 were inspected as rendered pages. Figure 8 retains all members of its five groups: hydroperiod (duration, frequency, level), physicochemical conditions (salinity, pH, redox, sulfides, nutrients), soil conditions (nutrient content, organic matter, texture), topography and target vegetation. These are assessment recommendations, not measured model-use counts, scores or source weights. Table 1 retains all four measurement methods, their scale limitations and cost categories; those cost categories are not MCDA weights. Figure 5's decision branches remain explicit holds rather than flattened masks. GMA printed-page pairs differ from PDF locators because each PDF page contains a spread.

WB §2.1 has four bullets on PDF page 6 and a fifth on page 7; all are inventoried. Intertidal extent, tidal range, wave shelter/freshwater, shoreline dynamics, embankment side and land-use avoidance remain distinct. Appendix equations and effect/design tables are not establishment calibration. Remaining full-paper/appendix row sweeps are explicitly pending.

Key methodological holds:

1. **GMA existing 50% duration claim:** “Most species” is not a universal practice cutoff. Existing `abs_max=50` requires review; preserve qualifier and native duration measure. No missing tail or species envelope is pooled into restoration.
2. **Local tidal envelope:** mean sea level to highest astronomical tide is not a pair of global metre thresholds. The source says “sites that have always been” outside the envelope and marks tidal datums indicative/site-dependent. Figure label “highest high tide” and prose “highest astronomical tide” are both preserved. Local vertical reference, tidal measurements and spatial support are required.
3. **Safeguard:** historical mangrove, undegraded mangrove, mudflat, seagrass, peat/mineral soils and existing land uses need explicit interpretation. Low tree cover does not imply afforestation opportunity. No global exclusion mask was adopted.
4. **Method selection:** planting and EMR remain methods within the approved family. Propagule availability, transport/connectivity and barriers differ by method. No new family or distance proxy resolves them automatically.
5. **Ontology:** frequency, salinity, wave/current exposure, sedimentation rate and shoreline dynamics have no established interchangeable mapping here. `sediment_retention`, wind hazard and duration cannot replace them.
6. **Regional benefit siting:** WB's water-side-of-embankment criterion selects flood-protection benefits; its agriculture/aquaculture/residential screen avoids acquisition. Neither is a universal ecological/legal exclusion. The 10 km screen is a design choice, not a measured survival boundary.

## Support, requirements and review

A complete eligible screened-study membership is not established. Headline denominators **N remain blank**; no quality-weighted support is computed. GMA's `high` and WB's `medium` SRC tiers are source metadata, separate from within-study importance (not reported here) and runtime MCDA weights (not assigned). Repeated GMA passages and cited primaries are not additional votes.

Dataset requirements are inspectable in the inventory: historical/current mangrove and other natural habitat, local reference-site observations, elevation tied to local tidal planes, inundation frequency/duration/level separately, hydrological connectivity and barriers, propagule source/transport, wave/current exposure, salinity, shoreline/sediment dynamics, and operational land-use/tenure context. No blanket SRTM/terrestrial elevation binding or land-cover mask is valid by default. Site-scale measurements and large-scale DEM approaches in GMA Table 1 carry different support; no numeric resolution was invented.

Central orchestrator should ingest only after its gates pass, display the units on existing evidence cards, and retain `intended_use`, `remaining_decision` and source/profile holds there. No parallel approval workflow is proposed.

## Reproduction

From repository root, with the existing environment:

```sh
PYTHONPATH=src .venv/bin/python pipeline/staging/mangrove_t4_20261028/reproduce.py --corpus /path/to/.cache/corpus
PYTHONPATH=src .venv/bin/python pipeline/staging/mangrove_t4_20261028/inventory.py
```

`validate_units` passes for all five final units. This advisory validation does not replace central provenance/context/staging gates. Complete retrospective/progress updates remain central and must describe this bounded partial pass; no learning cursor was advanced.

## Located stocktake addendum

After central orchestration identified the OneDrive stocktake root, all **eight** exact filenames were located (Unicode NFC matching handles the decomposed accent in Blanco-Sacristán). `stocktake_located.json` records full local paths, team-relative paths, SHA1 hashes and original stocktake rows. This resolves artifact location, **not** metadata verification, SRC registration or permission for ecological transfer.

Aduana-Alcantara 2023 was read across all nine pages; PDF pages 3–5 were rendered and inspected. `aduana_inventory.json` retains 24 claim/page rows and native page-sliced excerpts. It directly uses four WLC criteria: elevation and slope from ASTER, average air temperature from Global Solar Atlas, and average precipitation from WorldClim, all reported at 30 arc-seconds. Weights are **assumed equal**, not AHP-derived; the paper explicitly says it did not implement AHP. Four class scores are reported: 1 unsuitable, 2 marginally suitable, 3 moderately suitable, 4 highly suitable. No normalized weights or source-quality tier is inferred.

**Calibration hold:** Table 2 is explicitly referenced but absent from this nine-page artifact, including the rendered page. Table 1 is also referenced but absent; Figure numbering jumps from 1 to 3. No per-variable class boundaries can be recovered from the shown class-score legend. The 8–42°C text is cited short-period tolerance, not an annual-mean membership curve. Elevation is explicitly used as a proxy for inundation; local datum and inundation mapping are unspecified. Water pH, salinity and nutrient availability were **not included** in the model. The map includes agricultural, aquaculture and commercial/residential pixels; that is not an approved land-use safeguard. Metadata and library intake remain central holds; no Aduana EV row was added.

Reproduce artifact lookup and this inventory:

```sh
PYTHONPATH=src .venv/bin/python pipeline/staging/mangrove_t4_20261028/stocktake_locate.py --stocktake-root '/path/to/Zotero_Full_Text_Screening'
```
