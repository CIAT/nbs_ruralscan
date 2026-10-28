# Forest T4 bounded recovery — 28 October 2026

This is staging for central validation and review, not a completed corpus sweep, human approval, family-transfer decision or runnable global afforestation envelope. Ruleset v1.8.0 was read with the T4 review contract, defect catalogue, current FAM, crop-scope and roll-up policies. The current active-planting family includes reforestation, afforestation and enrichment planting. Plantation evidence stays in its separate family and excluded from forest-restoration roll-up.

## Reconciled baseline

`summary.json` and `evidence_accounting.csv` are regenerated from current CSVs. Before this batch: 211 forest structural/operational records, of which 210 active: active planting 71, passive regeneration 62, assisted regeneration 17, protection/CBFM 37, plantation 17, cross-family 6. Active roles: 110 structural and 100 operational. No active `reviewer_ok=true` values. The live `review_log.csv` has no matching decisions for these 211 IDs. Both available local `pipeline/review/decisions.json` files were inspected, with no matching IDs; their paths/hashes and matching entries are recorded. This establishes the checked history only, not a claim that no reviewer ever saw these papers or blanket request to repeat review.

`source_inventory.csv` reconciles 71 identities from existing forest T4 queue scope plus sources carrying structural/operational EV, including source metadata, exact family associations, cached artifacts, provenance and review history. Duplicate queue aliases retain canonical IDs and artifact locations; they are not extra studies. The truly uncached nonduplicate source is `fr_nucleation_seedling_planting_2024`, still pending. No DOI check failed for these queue identities. Canonical aliases include Chazdon, Cook-Patton and Crouzeilles; reuse must stay scoped to the applicable family rather than be counted again.

`search_protocol_existing.csv` and `queue_existing.csv` preserve current T4 searches and queue scope. Historical active-planting discovery explicitly finished stock/updated literature in an appended section, following an earlier budget-limited provisional section. Therefore the provisional section cannot alone establish an unsearched gap. Historical counts are not a complete screened membership list and do not supply a defensible current support denominator.

`stocktake_reconciliation.csv` records all 51 terrestrial rows labelled reforestation/afforestation or forest conservation/restoration after excluding explicit mangrove rows. Only three match current SRC/queue by exact DOI; 48 need title/canonical identity reconciliation, applicability screening or intake. This is not proof of missing papers or 48 eligible planting studies. It includes species models, natural regeneration, restoration priorities and other out-of-scope practices. Stocktake DOI strings are labelled **unverified seed metadata**, not emitted as verified source identities.

Highest-relevance remaining candidates to inspect first are:

- Rajaonarivelo and Williams (2022), *Remote Sensing-Based Land Suitability Analysis for Forest Restoration in Madagascar* — stocktake DOI candidate `10.3390/f13101727`.
- Poccard-Chapuis et al. (2021), *Mapping Land Suitability to Guide Landscape Restoration in the Amazon* — `10.3390/land10040368`.
- Chen et al. (2021), *Evaluating suitability of land for forest landscape restoration: A case study of Three Gorges Reservoir* — `10.1016/j.ecolind.2021.107765`.

All three PDFs were subsequently located in the team OneDrive **Stocktake Review/Manual Screening/Zotero_Full_Text_Screening/Forest conservation and restoration** directory. Opening pages carry matching titles and the candidate DOIs; exact paths, SHA256 hashes and opening text are in `stocktake_priority_artifacts.json`. They are existing team assets requiring central metadata verification/intake, not new discovery. Across the 51 stocktake rows, 44 exact-filename PDFs were located; seven require alternate-filename/content reconciliation. Their titles do not prove active planting applicability, numeric suitability calibration or quality.

## Three-source recovery

`extract.py` builds fresh table-capable indexes over the cached Zomer 2008, Oliveira 2026 and Fahrudin 2024 PDFs, verifies metadata and opening-title identity, packages page-stamped passages with full tables, slices native quotes and validates/stages EvidenceUnits. `artifact_manifest.json` records hashes and library locations. `inspected_source_inventory.json` contains 61 interpreted items; `machine_table_row_inventory.json` contains 372 text-layout rows and `caption_inventory.json` all detected captions. Machine table rows are not equivalent to verified source rows or complete manual visual review.

Three new units are staged:

1. Zomer p3 categorical continuation omitted from existing p2 land-cover unit: tundra, irrigated/intensive agriculture, forested/recently deforested categories. Preserved as historical CDM-specific exclusions, with no approved global mask.
2. Oliveira p4 allocation domain: agricultural and non-vegetated classes. Regional optimizer scope only; no permission to convert native non-forest ecosystems.
3. Zomer p5 land/tree tenure as an explicitly omitted enabling condition. Operational/M6 only; no model-use vote, numeric cutoff or T4 weight.

All have `reviewer_ok=false`, `practice_as_described` and scope/transfer holds. Central dry-run passed with explicit structural and operational roles. No extraction agent wrote registers or approvals.

Important holds:

- Zomer's 2007–2012 CDM screen requires no forest at the start of 1990, implemented with a 1991 land-cover proxy. It includes industrial plantations, agroforestry, ANR and planted reforestation, while excluding enrichment. Existing 30% canopy, 0.65 aridity and 3500 m elevation values are not universally transferable to the full active-planting family. The aridity text alternates `<0.65` exclusion and `>0.65` suitability; equality remains undefined.
- Zomer growing-season mean temperature below 6.5°C cannot be relabelled mean annual temperature. The rendered glyph and appropriate ontology variable require review. Protected areas are excluded in the source map; that is not evidence that restoration in every protected area is illegal.
- Oliveira p8 says slopes above 75% are generally unsuitable for planting, citing Santos 2018, then explicitly includes those areas in its restoration strategy. The existing unconditional `abs_max=75` is misleading. Preserve the cited planting-difficulty statement and contradictory allocation context. Supplementary sections 2/3 and Figs S1/S2/S3 remain uninspected holds.
- Fahrudin's 21 Table 1 input rows are accounted for by their actual role: target-domain inputs, ES priorities, wildfire model, environmental pressure and planning comparison. Equal weights belong to ES priority components; Gini importance belongs to wildfire susceptibility. Neither is a T4 weight vector. Soil-water depth units/data labels disagree between prose, table and reference; no silent repair. The 12-subdistrict Table 2 areas are model outputs. Graphic-only precision and complete visual second-read remain pending.
- WOCAT `observed_presence` claims remain contextual evidence. They cannot supply cutoffs. Busch observed reforestation associations likewise require their occurrence/selection context; this pass does not convert them into physiological envelopes.

## Tools and scope

Historical discovery/SRCH names Afforestation-Tracker (Luk-kar), GROA and Project-Scotland-Reforestation. No current forest SRC/TOOL registration or immutable cached parameter files were found for those identities. The log claims earlier code inspection for Afforestation-Tracker, but the current deterministic pipeline cannot substantiate its reported thresholds. Acquire pinned source code through the GitHub adapter, register canonical identity and inspect actual parameter blocks before any EV emission. GROA remains a passive-regeneration candidate; the historical Scotland exclusion is recorded as data-driven rather than a hardcoded rule source. No README-derived parameters were emitted. Existing forest WOCAT PDFs are PDF case sources, not pinned model code.

## Support, weights and decisions

No new support denominator is asserted. Raw `n/N` headlines require the complete eligible screened membership list, with separate variable-use, direction and calibration counts. Quality-weighted support stays blank until screened membership and all tiers are known. Source-quality weights, source ES/Gini importance and runtime MCDA weights remain separate. No new scoring convention, aggregation, transfer pool, global forest mask or family split is proposed as approved.

The necessary methodological questions are limited to (1) admissible historical-CDM transfer scope, including enrichment and native non-forest safeguards; (2) whether any new growing-season temperature variable/profile should be introduced; and (3) treatment of Oliveira's conditional planting difficulty versus actual allocation. Clear false hard-ceiling behavior should remain held while these questions are answered on the same evidence cards. Other missing-source/supplement work is acquisition/completeness work, not a methodological approval request.

## Reproduce

Run from repository root:

```sh
uv run python pipeline/staging/forest_t4_20261028/reconcile.py
uv run python pipeline/staging/forest_t4_20261028/extract.py
uv run python pipeline/staging/forest_t4_20261028/finish_inventory.py
uv run python pipeline/staging/forest_t4_20261028/stocktake_paths.py
uv run python scripts/ingest-effects-staging.py pipeline/staging/forest_t4_20261028/evidence_staging.json --dry-run --allow-structural --allow-operational
```

The script currently accepts original cache locations recorded in source manifest; keep the PDFs byte-identical or adapt `CACHE` explicitly before rerunning. No search, extraction-complete or review-complete stage was stamped. Central orchestration owns retrospective and append. Feedback cursors were not advanced.
