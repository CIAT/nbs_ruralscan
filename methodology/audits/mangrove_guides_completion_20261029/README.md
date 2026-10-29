# Mangrove guide continuation — 29 October 2026

This follows `../mangrove_guides_followup_20261029/` under extraction ruleset v1.8.0. It screens **92 additional PDF pages**: MAR 6–24 and 65–114 (69), and Sri Lanka 127–149 (23). Together with the earlier audit, all 114 MAR pages have now received native-text screening. This is **not complete extraction or image digitisation**. Sri Lanka remains partially screened; the full 194-page coverage ledger records remaining pages individually. Both sources remain in progress, and no discovery/SRCH completion is claimed.

## Evidence and correction

Two new, unapproved `operational_risk` units retain Sri Lankan guidance on budgeting pollution remediation (PDF131) and community knowledge/ownership (PDF143). They belong to M2b Stream B / M6, not the structural opportunity surface. The community passage's cost-effectiveness wording is an expert assertion, not a measured effect. No numerical response, runtime weight or new structural threshold is emitted.

The existing **unapproved** habitat unit `ev_mg_habitats_sl21_20261029` now explicitly flags a contradiction: PDF96/132 prohibit planting mudflats, while Table9 on PDF141 proposes grass consolidation followed by mangrove planting on erosion-prone mudflats. The original quote, relationship, role and review state are unchanged. `context_amendment.json` stores the complete before/after row and native counterevidence; `amended_unit.json` represents the current unit. The earlier staging snapshot remains historical and is not the current context. No branch condition is invented to resolve the contradiction. Review is required before any mask or synthesis.

## Coverage and retained holds

`source_inventory.json` retains each newly screened page's native text and explicit disposition. These full-page audit anchors are not evidence quotes or a new dataset. `visual_checks.json` records page-render identities for image checks against the existing cached publisher PDFs.

- MAR Table2.2 (PDF68): hydrology, vegetation, recruitment, fauna, physicochemistry, sediment and landscape indicators, including short/medium/long response periods, are monitoring specifications. Table2.3 (PDF78) has 15 participation, valuation, economic and policy/finance indicators; they are proposed measures, not observed benefits.
- MAR Table3.1 (PDF87) retains ten degradation-cause/country rows and source footnotes. Table3.2 (PDF92–94) retains all country/activity continuations in native page anchors. Project areas, dates and action counts are descriptive; the 100-ha active/passive recommendation is not a minimum suitability area.
- MAR PDF14/17/18 regional degradation totals require scope reconciliation. PDF95's 29/13/1 sources with restoration-area information sum to 43; percentages 68/30/2 describe these reporting sources, not all 112 projects. No graph-digitised dataset is created.
- MAR PDF96–98 costs remain an economic follow-up: captions say per hectare while plot axes label restoration cost. Do not infer denominators from the graph. Monitoring durations and glossary salinity/texture definitions are not ecological suitability envelopes.
- MAR's forest-recovery discussion cites Donath 2003, whose bibliography title concerns alluvial meadows; check citation lineage and transfer before treating this as mangrove calibration.
- Sri Lanka Table7 (PDF133–134) preserves species fruit-collection instructions and the Sonneratia continuation across pages. Table8 (PDF134–137) preserves nursery-site conditions, beds, potting mixtures, seed transfer, watering, shading and species-specific ages. These are nursery operations, not landscape tolerances. Seedling-age guidance must retain its species and hazard context.
- Sri Lanka Figure17 (PDF138) is an image-only species-selection triangle. Visual inspection confirms inundation-depth, soil-texture and salinity axes and 14 species codes. Printed salinity signs and joint-region geometry require source clarification before numeric transcription; no inferred species envelope enters EV. Figure1.3 in MAR likewise does not justify assigning numeric limits to shaded salinity bars.
- Sri Lanka Table9 (PDF141) retains algae, siltation, predation, grazing, erosion, human intervention and waste rows, with the mudflat conflict above. Table10 (PDF143) retains all four community-support activities in the inventory; its unsupported gender-efficiency assertion is not adopted as a finding.
- Embedded invasive-species guide covers (Sri Lanka PDF127) and references are leads, not separately acquired or read publications. MAR's back cover was visually checked; garbled ISBN extraction does not supply evidence.

## Tools, models and codebases

`tool_project_leads.json` preserves five bibliographic leads: an individual-based mangrove restoration model, hydrology/nutrient/community simulation modelling, a restoration-potential map, Global Mangrove Watch and a Deltares coastal project. Initial distinctive-title/name matching found no corresponding SRC, acquisition-queue or TOOL row; broader title/URL reconciliation remains required before admission.

These are **leads, not verified codebases**. Follow-up must establish project identity, repository availability, licence, immutable release/commit, exact file/line locators, model validation and relevance to this scoping workflow. No new DOI, repository URL, duplicate source registration or executed-code claim is invented. Dataset ingestion remains paused. This is reference harvesting from acquired guides, not a completed external discovery search.

## Retrospective and preservation

The ingestion gate passes verbatim-page, numerical-provenance, context, variable, family, role and ruleset checks. Repeating ingestion dry-run finds zero additions. Batch scope/species/quote/direction checks are empty. Preservation checks against 6d3df80 show two added rows, no deletions, and only the audited habitat-context amendment among 5,254 existing evidence rows. Human approvals and review logs remain unchanged.

Global metrics are 5,256 units / 549 sources; number-provenance flags remain 291 (5.7%), verify mismatches remain four (0.1%). This two-unit qualitative batch does not demonstrate global quality improvement. No new automatic flag pattern was introduced; existing context and scope rules govern the contradiction and nursery safeguards. For the next source pass, explicitly cross-check later implementation tables against earlier exclusions before admitting a categorical mask. Historical human-feedback cursor remains untouched. Validation outcomes are recorded in `validation.json`.
