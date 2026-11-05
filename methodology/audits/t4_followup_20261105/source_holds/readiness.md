# T4 readiness for 13 November — snapshot 5 November 2026

Snapshot UTC: `2026-11-05T13:26:03.374088+00:00`. Input hashes in `readiness_snapshot.json`. This audit does not advance the ledger or claim completed source extraction, human consensus, calibrated runtime coverage, or full validation. Approved evidence and working mappings are different denominators.

## Current register and mapping counts

Six NbS categories; 28 registered suitability families; 56 subpractice/helper rows. 850 active structural-suitability records; 203 carry `reviewer_ok=true` and 647 do not. These are literal register flags, not independently reconstructed consensus. Scope split: 755 practice_technology, 71 species_specific, 24 crop_specific. Species/crop records do not automatically become practice-level constraints.

| NbS | Active T4 EV | reviewer_ok | Unapproved | T4 CSV rows | Operational rows included | Rows with dataset ID |
|---|---:|---:|---:|---:|---:|---:|
| agroforestry | 217 | 177 | 40 | 26 | 9 | 26 |
| forest_restoration | 142 | 6 | 136 | 0 | 0 | 0 |
| mangrove_restoration | 35 | 0 | 35 | 0 | 0 | 0 |
| riparian_buffer | 45 | 0 | 45 | 2 | 0 | 2 |
| water_harvesting_conservation | 367 | 4 | 363 | 25 | 0 | 23 |
| wetland_management | 44 | 16 | 28 | 4 | 0 | 0 |

Total 57 T4 CSV rows, including 9 operational rows. Presence of a dataset ID does not verify its semantic fit, spatial grain or runtime validity. Forest and mangrove CSVs remain empty despite evidence. Family detail is in `family_readiness.csv`. Its exact FAM-key matches total 848 active /201 approved records; two additional approved agroforestry Baldwin records use literal `cross_family` instead of a registered family ID. They remain included in NbS/global totals and listed in `family_tag_reconciliation.csv`. This audit does not silently reassign them or claim a runtime defect without checking alias handling.

Wetland review application currently leaves four rows: three reviewed scored profiles and one qualitative seepage profile with unknown scores. All four dataset IDs are blank; matching measurements and eligibility masks remain required. Unsupported canal-density and minimum-patch-area hard limits were removed. This is reviewed configuration awaiting binding/validation, not four ready executable spatial layers. Two water-harvesting runoff-catchment mapping rows also have blank dataset IDs: `catchment_area` and `soil_permeability`, making six unbound rows overall. Both riparian mapping rows have dataset IDs; this does not itself certify binding fitness.

## Literal progress ledger

The ledger has 90 T4 rows (category × family/table-level). The saved schema stores searched, screened and verified; it does not store independent extracted/reviewed stage columns. Register counts above must not be substituted for missing completion stamps.

- searched: 79 done, 11 in_progress.
- screened: 82 done, 8 in_progress.
- verified: 59 in_progress, 2 done, 29 not_started.

Only two category/family rows say verified=done; this is not two completed families. Table-level and family-level rows overlap. Historical notes can lag newly applied decisions; `t4_ledger_snapshot.csv` preserves their literal state. No family is certified fully ready by this audit.

## Remaining work, in order

1. Finish central application and verification of the approved six legacy reviews, 17 active claims and two Rao reopenings; preserve reviewer decisions, assumptions and source context. A review flag alone does not authorize an executable curve.
2. Complete native measurements and binding/eligibility work for the four retained wetland rows. Match mean-lowest groundwater depth and signed seepage; distinguish water-supply proximity from habitat-connectivity proximity. Blank datasets are deliberate holds, not silently replaced proxies.
3. Review the remaining global T4 queue by family. The 647 unapproved records in this snapshot extend well beyond the just-reviewed batch; do not represent these as 647 independent studies or 647 numeric rules. Prioritize already calibrated, practice-relevant evidence and known domain clarifications.
4. Keep 32 unresolved bounded source-hold dispositions visible: 28 measurement/ontology, one graded-bund family, one source contradiction, one Goyette supplement and one Atlantic native-adapter hold. Four method/design referrals are resolved for this bounded interpretation, one jessour family remains parked, and Poorter/Cao are closed dispositions. These are not mandatory new-discovery tasks; a reviewable handoff can retain explicit gaps.
5. Reconcile per-family search/verification gaps and compile approved evidence only. Reconcile the two literal `cross_family` tags against canonical-family/alias handling without changing scope. Dedicated T4 search-protocol gaps remain for plantation forestry; forest protection and spate have only a grey family lane. Active planting and mangrove search/screen ledgers remain incomplete. Shaded perennial agroforestry remains thin at practice/crop scope; Amichev species-group evidence cannot fill a generic practice envelope.
6. Produce the handoff status per family: review-ready evidence, reviewed but uncalibrated/unbound, validated runnable rules, explicit evidence/measurement gap, or parked/qualitative. Validate provenance, schema consistency, source coverage, runtime eligibility and spatial-product type; record failures instead of claiming all-practice completion.

## Scope retained for handoff

- Tidal/salt-marsh wetland restoration stays parked; current FAM family `wetland_management__coastal` has no active T4 record. Mangrove restoration is separately active: its 2026-10-19 promotion supersedes inherited PARKED wording in the same FAM rationale.
- Constructed/treatment wetlands and rooftop/household systems remain qualitative/parked; spate/jessour remains parked. Forest protection/community management retains its existing scope hold. No new practices or family reassignment approved by this audit.
- Cross-family helper families are not extra landscape practices; natural/planted riparian families are zonal-linear products, not pixel-area coverage.
- Previous wider audit also identifies Gu/Semmens riparian applicability, water-harvesting storage/recharge/alluvial routing, and source-layout/supplement limits. Those remain pointers for reconciliation, not freshly verified new blockers or authorization to reopen resolved work. No effect/operational extraction or integrated-fire-management scope expansion is opened.

## Bounded-source audit artifacts

`REPORT.md` gives source/page findings; `dispositions.json` and `.csv` contain all 39 entries; `read_manifest.json` identifies exact cached artifacts and pages. Seven PDFs/25 native pages were reread, with eight exact native quote checks. Atlantic received only a native-text availability test. No exhaustive extraction claim follows from these checks.
