# Five-source water-harvesting T4 extraction — 4 November 2026

## Result

Added 53 unapproved evidence units from the five priority papers prepared in the previous intake. This is a bounded T4 pass, not new discovery or completion of all water-harvesting extraction. Existing EV rows and human review decisions are unchanged. All five sources remain `in_progress`; queue `extracted` means they now have evidence, not that all outstanding work is complete.

| Source | New units | Main retained content |
|---|---:|---|
| Adham 2018 | 5 | All five Table 1 criteria and classes, local rankings and source inconsistencies |
| Alene 2022 | 13 | Five ranked criteria with weights; four joint siting criteria for each of pond/check dam |
| Bera 2023 | 16 | Mapped Table 3 criteria, TWI continuation, structure-specific siting prose and citations |
| Jha 2014 | 15 | Four structures × three criteria; three complete weighted potential-index criteria |
| Terêncio 2017 | 4 | Rainfall, curve number, clay content and slope ranks; planning-stage limits retained |

There are 27 units with a supported non-`unclear` direction and 26 categorical or conditional units without a single scalar direction. These are **unit counts, not independent-study votes**: TWI continuation and structure variants must not inflate agreement; Jha and Singh share a source lineage. No executable membership curves, global exclusions or runtime weights were created. Raw classes, units and source weights remain available for review.

## Source fidelity and remaining holds

- **Adham:** nonmonotonic runoff scores, missing stream-order 4, clay-unit ambiguity and cited slope caution versus graded classes remain explicit.
- **Alene:** the printed slope class is `8-May`; p4's >8% caution conflicts with graded classes and the check-dam <15% criterion. Table 7's `Stream order` header does not match its drainage-density row. Small functionality samples include structures in restricted zones.
- **Bera:** slope is degrees; surface storage and recharge cannot share one permeability direction. Curvature, lineament density and geomorphology remain ontology holds. Groundwater depth is alternative-supply demand. Gully-plug applicability needs a family decision. Referenced supplementary site tables S1–S6 were not acquired; validation-site audit remains pending.
- **Jha:** fine versus light soils, structure-specific slopes/orders and the local 50-m stream buffer remain distinct. Bera's cited percolation orders differ from Jha's; Singh adapts Jha rather than independently corroborating it.
- **Terêncio:** mixed planning model includes engineered dams. Soil profile depth is not assumed to mean depth to bedrock. Demand and ecological priorities stay outside T4 extraction. Generic all-one weights and irrigation-project weights are different stages, explicitly explained on p7; no global runtime weight follows.

Drainage density increases suitability in Alene/Bera but decreases it in Jha. Terêncio's curve-number scores decrease with CN. Runoff depth, runoff coefficient and curve number share a broad ontology ID but retain their native measurement and model context; they must not be pooled or treated as interchangeable calibrations.

`criterion_inventory.json` accounts for 68 claim/criterion groups: 53 staged units and 15 explicit holds/deferred groups. Each holds its native quote and page. `table_coverage.json` accounts for criterion tables, input-method tables, map outputs, validation, engineering and supplements. It is not a claim that every figure or supplement has been independently revalidated.

## Review question

For each card: retain the source-specific variable use, reported classes and supported direction with its stated limits, or query/drop with a reason? A Keep decision does not by itself authorize transfer to all structures or a numeric runtime curve. Table headers are preserved as native supporting quotes; short rows include a contiguous header-bearing passage. No quote was stitched across pages.

## Pipeline and validation

The deterministic PDF indexes from intake were used with `package_for_extraction_multi(full_tables=True)`. Quotes were sliced from cached native page text. Main tables with layout-dependent interpretation were visually checked. Units passed `validate_units`, staging dry-run, and gated ingestion with explicit structural-suitability authorization under v1.9.2. `manifest.json` records PDF and retrieval-package hashes. The local, gitignored staging file is `pipeline/staging/wh_five_t4_20261104.json`; its hash is recorded in validation. The committed EV register contains the admitted units.

Batch number, scope, species and quote checks have zero flags; T4 coverage has zero errors. Generator verified 4,578 corpus quotes against 670 cached sources (1,490 baseline exemptions). Prior corpus advisories remain; they are not defects introduced by these units. All 1,020 tests pass (five SWIG warnings). Structure validation has zero errors: 3,863 baseline warnings plus ten standard pipe-delimited SRC-variable reference advisories; each variable passes the VONT gate. Native PDF trailing whitespace is preserved in verbatim EV quotes. Results are recorded in `validation.json`.

The progress ledger remains `verified=in_progress` for runoff-catchment stock T4. No human approval, family regrouping, T3/T6 extraction or synthesis was performed.
