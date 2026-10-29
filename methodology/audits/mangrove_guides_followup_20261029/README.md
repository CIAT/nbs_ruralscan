# MAR and Sri Lanka mangrove guides — selected sections, 29 October 2026

This bounded T4 recovery pass reviews site selection, diagnosis and restoration decision paths in the acquired MAR/Greater Caribbean manual (2021) and Sri Lankan national guidelines (2021), under extraction ruleset v1.8.0. **83 selected section pages were text-screened; eight new unapproved units were admitted: four structural and four operational.** This is partial extraction, not completion of either book.

The two publisher PDFs match their team-library copies and pass opening-title identity checks. Deterministic indexes cover all 308 PDF pages. MAR's index reports zero tables despite visible Table 2.1; manual image inspection and inventory preserve that table. Sri Lanka Figure 13 has an image-only decision tree: its labels were visually inventoried, not passed off as text-verified EV. Opening pages, MAR Figures 2.3/2.14/2.21 and Table 2.1, and Sri Lanka Figure 13 were visually checked. Other selected pages were text-screened; photographs and diagrams are not claimed as independently measured or digitised.

## New evidence

| Source | Variable | Role | Claim retained |
|---|---|---|---|
| MAR PDF44 | regeneration_potential | structural_suitability | Nearby conserved mangrove supplies seeds/propagules for natural regeneration; no distance cutoff |
| MAR PDF27 | tenure_security | operational_risk | Legal security supports persistence of restoration and benefits |
| MAR PDF27 | finance_credit_access | operational_risk | Funding certainty/amount relates to access, area and degradation; no financial score |
| MAR PDF25 | extension_governance | operational_risk | Local/indigenous participation and knowledge from planning through monitoring |
| Sri Lanka PDF96 | land_cover | structural_suitability | Avoid replacing other coastal habitats and planting lagoon/estuarine shores; class mapping and broad shore wording require review |
| Sri Lanka PDF124 | land_cover | structural_suitability | Branch B.3: no brackish inflow and thriving replacement vegetation; do not select merely because mangroves existed historically |
| Sri Lanka PDF97 | regeneration_potential | structural_suitability | Prefer protected natural colonisation where feasible; assess shared citation lineage |
| Sri Lanka PDF85 | tenure_security | operational_risk | Establish ownership across protected, government/institutional and private land |

None documents use in a fitted spatial suitability model. None supplies a new continuous response, numerical cutoff, score or runtime weight. Structural relationships remain categorical or conditional; “unclear” scalar direction does not erase their explicit applicability recommendations. Better recruitment changes the choice between planting and regeneration, not the suitability of the whole family. No source-derived national legal mask or human approval is created.

## Retained directions, values and mapping holds

`source_inventory.json` retains contiguous native page anchors and dispositions for every selected page, including raw values. These full-page audit anchors are not EV quotes or an approved dataset. `figure_table_inventory.json` inventories all 13 MAR site-selection criteria, the example table's columns/targets and both decision trees.

- MAR separates inundation depth (monthly mean metres), frequency (days per month) and duration (hours per month). These are not interchangeable. Relative microtopography, salinity, redox and sediment properties cannot be silently mapped to generic elevation, rainfall, drainage or SOC.
- MAR Table 2.1's 36 hectares, salinity-to-50% objective and six/eighteen-month targets are illustrative project goals, not observed effects or suitability thresholds. Reference/degraded bulk-density illustrations on PDF43 remain condition examples.
- Channel widths/depths, wall slopes, maintenance intervals and constructed-platform dimensions are engineering guidance. MAR PDF60 specifically recommends platform placement at inundation level >0.4–0.5 msnm and interstitial salinity <80 ups. The ambiguous threshold range, vertical datum, platform scope and salinity mapping remain visible holds; these values are not discarded or converted into a whole-family envelope.
- Sri Lanka's silt/sand and acidic-soil warnings retain supported qualitative relationships. Water versus soil pH, unreported soil depth and USDA texture mapping remain unresolved; no numerical pH cutoff is invented. Species-specific light/anoxia differences on PDF49 remain a separate species/primary-reference follow-up, not a pooled mangrove curve.
- Sri Lanka B.2 says to retain established vegetation while repairing partially connected former ponds. B.3 says not to restore thriving replacement habitats without brackish inflow. Their branch conditions matter; the rules are not collapsed into one land-cover mask. Invasive monostands enter a separate assessment/removal pathway.
- MAR recommends dry-season channel work; Sri Lanka recommends aligning channel cutting with rain in the stated restoration branches. These remain regional implementation guidance, not an averaged universal season. Sri Lanka's in-situ spoil islands are not assumed equivalent to MAR's obstructive spoil piled along banks.
- Generic field-site accessibility is not travel time to a market. Worker safety, expected community benefits, science opportunities and project goals retain implementation/mapping dispositions rather than forced VONT substitutions.

## Lineage, coverage and follow-up

Sri Lanka explicitly adopts UNEP2020 figures and reproduces guidance from a 2018 tropical-wetlands guide. MAR cites Lewis2005 and other primaries. `lineage_and_holds.json` records canonical reuse and unverified bibliographic leads. Neither repeated passages nor two guide records count as independent experimental votes. No new external search, DOI or acquisition is claimed.

`page_coverage.json` records all 308 pages. Forty MAR and 43 Sri Lanka section pages are screened; opening/title/contents inspection is separate. Remaining pages—including species appendices, later monitoring, pollution, nursery and case material—need further semantic screening. Both SRC records remain `in_progress`. Queue status `extracted` means some units were admitted, with explicit partial-coverage notes; it does not mean swept. Family verification remains `in_progress`; search/SRCH stages and human decisions are unchanged.

Selected-artifact review has now touched 26 of the bounded 29 candidates. The three acquisition blockers remain untouched by this batch; ITTO reuse, code admission, Atlas lineage and other prior holds remain open. This is candidate-review coverage, not completed extraction.

## Adversarial review and retrospective

The review checked variable use, scalar direction, numeric calibration, practice/species scope and table/diagram omissions separately. Native quotes, source identity, FAM/VONT, context, number provenance and ruleset gates pass. Scope, species, quote and direction checks return no new-unit flags. Central ingestion grants no human approval. Repeated ingestion is checked for zero duplicates.

Existing defect rules cover the encountered hazards: missing image text/table detection, engineered dimensions mistaken for ecological thresholds, proxy substitution, branch collapse and duplicate lineage. This pass reinforces those safeguards through explicit row/branch inventories rather than claiming a new defect or changing the frozen schema. Global number-provenance and verification rates remain 5.7% and 0.1%; unchanged historical flags do not demonstrate improvement from a small qualitative batch. The global human-feedback learning cursor is not advanced. Metrics and verification details are retained in companion JSON files.
