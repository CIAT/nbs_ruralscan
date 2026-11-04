# Water-harvesting priority source intake — 4 November 2026

## Result and boundary

Completed formal intake for the five new method candidates from the bounded High-tier stocktake: Adham 2018, Alene 2022, Bera 2023, Jha 2014 and Terêncio 2017. Existing acquisition-queue entries now have `status=acquired`; five new Source Register records have `extraction_status=pending`. No evidence was extracted or approved. No search, extraction or review-completion stage was advanced.

The shared stocktake PDFs were copied unchanged into the standard `library/3_Water_Harvesting/` folder through the OneDrive mirror and into the local corpus. Opening titles and SHA-256 identities were checked against the previous audit; the prior verified Crossref records are retained. `manifest.json` preserves both library paths, full hashes, scope limits and index results. The local searchable indexes cover 70 pages and detect 25 tables, with no OCR-needed pages. Table detection is not semantic validation or complete extraction.

The script's stock-process default classifies sources as grey literature; these five records are explicitly corrected to `source_kind=paper`, retaining `source_category=stock` and `venue_type=peer_reviewed_journal`. Search origin and publication type are different dimensions. No pipeline code was changed.

## Credibility and method metadata

All five retain the audit's provisional medium tier, with its six-axis assessment in `../water_harvesting_priority_20261104/README.md`. Journal publication does not ratify the rules or demonstrate global transfer. Alene, Bera and Jha use AHP; Jha's method is explicit on native PDF pages 6 and 13. Adham and Terêncio are recorded under the broad `expert` method class for source/literature-based scores and planning weights, not as independent experimental validation. Country is recorded from each study; income group is left blank rather than inferred from a current country classification.

## Extraction work left

| Source | Main-paper starting points | Required distinctions and holds |
|---|---|---|
| Adham | pp. 3–5, 7; Table 1 | Inventory all criteria and classes. Keep nonmonotonic runoff scores and absent stream-order 4; storage-dam engineering does not automatically qualify as NbS. |
| Alene | pp. 5–6, 12–13 | Keep pond and check-dam criteria separate. Preserve the malformed slope class literally. Road/town setbacks need operational routing; small functionality samples do not calibrate universal thresholds. |
| Bera | pp. 5–6, 10–15 | Separate surface storage from recharge, degree units from percent slope, demand from establishment, and contradictory geology/landform explanations. Retain cited-primary attribution. |
| Jha | pp. 6–7, 13, 15 | Table 1 structure conditions differ from local weighted potential mapping. Preserve the Jha → Singh lineage: adding Jha does not create an independent replication of Singh's reused criteria. |
| Terêncio | pp. 3–6 | Separate physical opportunity screening from demand/ecological priority and engineering sizing. Protected-area priority is not construction permission; source curve-number scores cannot be pooled with opposite-purpose models. |

These are starting locators, not a complete row-level extraction inventory. The next extraction pass must inspect every relevant table row, continuation, figure and supplement and assign an evidence ID or explicit hold. Use the deterministic retrieval and staging gates, then the extraction retrospective. None of these sources is marked swept, and no family regrouping is authorized by intake.

## Validation

- All five opening-title and promotion gates passed.
- Standard library copies, corpus files and index content hashes match.
- Existing DOI verification retained; acquisition rows also carry verified opening titles.
- All unrelated queue/source rows are unchanged. EV, review log and progress ledger are byte-for-byte unchanged.
- 59 targeted ingestion, metadata and source-validation tests passed (five SWIG deprecation warnings).
- Generator/schema validation results are recorded in `validation.json`.

Human QA/QC of the 47 answer-ready clarification groups can proceed independently. This intake does not decide those reviews or add new evidence cards.
