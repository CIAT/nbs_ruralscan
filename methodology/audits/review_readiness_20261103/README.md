# Review readiness and practice coverage — 3 November 2026

Baseline: merged main `bccdfcd088ad` (#540). This is technical triage and a register/ledger stocktake, not new discovery, extraction, calibration or human approval. Reproduce the shared-register audit with `.venv/bin/python methodology/audits/review_readiness_20261103/triage.py`. It excludes ignored local decisions deliberately. Artifacts are point-in-time observations on Pete's machine; they do not establish that another reviewer has SharePoint access or cached files.

## Triage outcome

| Finding | Action / disposition |
|---|---|
| Live review server on port 8766 was serving old detached checkout `190b54ad1fd9` | Checked clean checkout and all 190 saved decisions already applied; backed up decisions; fast-forwarded to merged main; hydrated; restarted on the same port. Health passed; local/remote both `bccdfcd088ad`, `behind=false`; API decision-state hash unchanged. Browser needs hard reload. |
| Port 8765 hosts an unrelated static site | Left untouched. Added alternate-port and safe-refresh notes to reviewer guide. |
| Source access for 4,507 active EV rows | All 635 referenced sources have local artifacts. All 631 populated PDF library paths exist; four remaining sources have URLs and cached snapshots. No missing source identity, absent team link, unreadable PDF or out-of-range numeric page found. Remote permissions and URL reachability were not tested. |
| PDF navigation for 352 records | These have section locators rather than numeric PDF pages, not missing provenance. A PDF preview defaults to page 1. Use the displayed section locator/source link and PDF search; do not mistake the initial page for the cited passage. Breakdown: 19 T4, 29 operational, 175 effect, 129 asset-vulnerability records. Listed in `technical_issues.csv` as navigation limitations, not hard blockers. |
| Source previews | One active T4 full-page render per NbS category: six passed. This tests renderer/file access, not every quote or caption. |
| Human clarification backlog | Baseline: 18 answer-ready record/reviewer pairs, two unresolved human questions. Prepared the missing Namita FMNR reply, giving 19 answer-ready pairs and one remaining human question in this branch. Fourteen additional “needs investigation” entries are automated source-context audit notes, not unanswered human messages. |
| Namita: do not constrain FMNR to 950 mm | Re-read native PDF p4 and existing corrected EV. Added a field-hashed answer explaining observed practice distribution versus establishment limits. Existing EV, approval flag and review decisions unchanged. Reply becomes available after this change reaches the review checkout. |
| Peter: existing wetlands versus created wetlands | `ev_wet_protected_area_status_qiu20_1` remains a substantive scope decision for wetland review. No silent reassignment or approval. |
| Five pre-existing effect-lane follow-ups lack tracker entries | `ev_crop_yield_boil19_2`, `ev_food_security_boil19_1`, `ev_crop_yield_adim16_2`, `ev_crop_yield_arsl15_4`, `ev_crop_yield_arsl15_7`. Baseline follow-up checker already reports these. Retained for the separate T3/T6 session; no effect evidence edited. |

Tests: 13 clarification tests passed; ledger consistency check passed; follow-up checker reports the same five pre-existing effect omissions before/after the new reply, with no new failures. Source availability and numeric page bounds checked across all active evidence; six rendering smoke checks passed. No full provenance revalidation or cross-device access claim.

## What is covered

“Covered” below means **active T4 evidence exists**, not every variable is calibrated or every item human-approved. Counts exclude dropped records and include separately scoped species/crop evidence. A source occurrence is not proof of complete literature coverage. Detailed family counts, scope splits, source-search protocols and literal ledger states are in `practice_coverage.csv`.

| NbS | Practices represented by active T4 evidence | Active T4 records | Remaining work |
|---|---|---:|---|
| Agroforestry | Alley cropping, tree intercropping, planted boundaries/live fences; FMNR, parkland retention, assisted regeneration on farmland; silvopasture/agrosilvopasture; windbreaks/shelterbelts and contour buffers; shaded perennial crops | 182 | Human review of corrections, source-context/curve decisions and family verification. Shaded perennials have only 1 practice-level and 1 crop-level row versus 6 species rows; do not call this strong general-practice coverage. Includes 66 cross-family records. |
| Forest restoration | Reforestation, afforestation, enrichment planting; assisted and passive regeneration/secondary succession; plantation forestry; forest protection/community management | 137 | Priority-method reconciliation closed by #540; verified/calibrated family coverage still incomplete. Plantations have no dedicated family T4 search-protocol row; protection has only a grey family lane. Active planting search/screen states remain in progress. |
| Mangrove restoration | Mangrove restoration and ecological mangrove restoration | 35 | Priority-method/code audit done within declared scope; hydrology, tidal datum, species scope and transferable calibration remain review limits. Family search/verification ledger remains incomplete. |
| Riparian buffers | Planted grass/herbaceous strips, woody buffers, natural regeneration and reforestation | 39 | Four discovery categories searched/screened for both families; verification and human review remain. Zonal-linear products, not blanket pixel-area suitability. Not included in the recent ten-source closeout. |
| Water harvesting/conservation | Contour bunds/ridges, planting pits/Zai, conservation tillage/mulching; semi-circular bunds, eyebrow terraces, runoff strips; macro-catchments, ponds, check/percolation/sand/subsurface dams and small reservoirs; terraces/stone bunds/fanya juu; spate harvesting | 309 | Four main landscape families have searched/screened lanes and verification in progress. Spate has only a grey family lane. Includes 10 rooftop records retained for qualitative guidance, not a landscape suitability layer. Not included in the recent ten-source closeout. |
| Wetland management | Restoration/rewetting, drainage blocking/reflooding, floodplain reconnection; peatland rewetting/paludiculture; wetland creation/reconstruction | 34 | Verification/human review, especially existing versus created wetlands. Creation has 8 records; peatlands 4. Coastal/tidal marsh family has no active T4 evidence or family-specific T4 search row. Not included in the recent ten-source closeout. |

These 736 active structural-suitability records comprise 665 practice-level, 24 crop-specific and 47 species-specific records. Crop/species rows are not automatically eligible for practice-level synthesis. The `approved_t4` column reports the existing `reviewer_ok` field, not an independently reconstructed human-consensus count. Effect-evidence counts are supplied only as read-only context for the other session; they are not T3/T6 completion claims.

## What remains outside a completed landscape T4 surface

- **Real coverage gap:** coastal/tidal marsh wetland restoration (zero active T4 records and no family-specific T4 search protocol).
- **Thin/partially searched families:** shaded perennial agroforestry, plantation forestry, forest protection/community management and spate harvesting. Existing evidence is retained; missing protocol coverage is not proof no source was ever read.
- **Intentionally qualitative:** multistrata homegardens, constructed/treatment wetlands and rooftop/domestic harvesting. They are marked `qualitative_only` in FAM; absence from landscape output is not an automatic discovery task. Cross-family helper records are not extra practices.
- **Across represented practices:** human QA/QC, source-context interpretation, curve/calibration limits, family applicability and final synthesis remain distinct tasks. The ledger was not upgraded from this audit.
- **Cross-track tool referrals:** MapAWD (rice AWD) and Africa Agriculture Adaptation Atlas remain as documented in #540; neither was silently added as a new forest/mangrove task.

No new source-search batch is opened. Proceed with today's review, using the scope and navigation notes above; keep separate T3/T6 work with its existing session.

## Correction: original stocktake scope versus current schema coverage

The six-group coverage table above describes the current schema, **not the complete original stocktake commitment**. Checked against the canonical revised Stocktake Review (scope section and Annex 1), plus `reference/stocktake/peer_reviewed_benchmarked.csv` (220 records). The report explicitly includes ten priority practice headings. The earlier inception longlist is broader still and explicitly says inclusion means screening, not endorsement or prioritisation.

| Original stocktake heading | Stocktake paper rows | Current mapping |
|---|---:|---|
| Agroforestry | 23 | Agroforestry families |
| Agrosilvopastoralism | 5 | Agroforestry silvopastoral family |
| Forest conservation and restoration | 38 | Forest restoration/protection families |
| Reforestation and afforestation | 19 | Forest restoration active planting |
| Community based forest management | 5 | Forest restoration protection/CBFM |
| Water harvesting and conservation | 85 | Water-harvesting families |
| Wetland management | 20 | Wetland families |
| Constructed Wetlands | 8 | Current constructed/treatment family is qualitative-only; original stocktake included it |
| Riparian buffers | 11 | Riparian families |
| Integrated fire management | 6 | No dedicated current FAM/recipe coverage in the six-group inventory; unresolved scope/implementation gap |

Mangroves were split into a separate current group; they were not a separate top-level heading in this benchmark CSV. Fire-hazard screening elsewhere is not equivalent to covering integrated fire management as an intervention. Therefore the original stocktake cannot be described as fully implemented by the current six groups. The original stocktake did review fire-management papers; the gap is subsequent methodology/schema coverage, not absence from that review. Constructed wetlands also require the distinction between original review coverage and the later qualitative-only implementation decision.

Canonical documents checked read-only in the team library on 3 November 2026:
- `4_Outputs_&_Reporting/4_Reporting/2. Stocktake Review/Stocktake Review_with revisions.docx`
- `4_Outputs_&_Reporting/4_Reporting/1. Inception Report/Inception Report_Dec2025.docx`, Table 2 and preceding longlist explanation.
