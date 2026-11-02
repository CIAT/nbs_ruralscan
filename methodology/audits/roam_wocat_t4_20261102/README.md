# ROAM full review and WOCAT ANR intake — T4

2 November 2026. Extraction ruleset v1.9.2; T4 contract v1.6.16. Bounded follow-up to the ITTO tool batch, not a new discovery sweep. No T3/T6 extraction or human approval.

## Outcome

- **WOCAT Approach 1971:** acquired from the primary publisher, exact title and approach/version identity verified, registered, and two pending T4 units ingested for assisted regeneration: degraded-land host classes and existing regeneration potential. Both have `relationship.direction=unclear`: no monotonic response is asserted. No numeric function, score or weight was created.
- **ROAM:** all 64 native PDF pages (printed spreads), 28 numbered tables plus Appendix A1, and 22 figures screened. Deterministic index refreshed: 41 detected table objects, no OCR-page flags, 39 page-stamped retrieval passages with full-table retrieval. Nine key spreads visually checked. No new ROAM EV: candidate claims remain explicitly scoped/mapped holds or priority/process referrals. Existing canonical queue identity is reused; no duplicate SRC or acquisition.
- **133 ROAM candidate/criterion rows** retained in the source-value inventory. Complete page and table/figure inventories accompany it. This is full-document screening, not a claim that every economic or operational value has been extracted.

## Claims and limits

`ev_fr_landcover_wocat_anr1971_20261102` records degraded grassland and shrub vegetation in a forest-rehabilitation context, not permission to replace native non-forest ecosystems. No EO class crosswalk supplied.

`ev_fr_regen_wocat_anr1971_20261102` records assessment of existing wildlings under the broad categorical `regeneration_potential` concept. The site's ideal **600–700 vigorous wildlings/ha, 15–200 cm high, relatively well spread** remain literal source values. Density, height and spatial spread lack exact canonical mappings. The broad category is itself a review question; it is not a substitute calibrated density variable. `rootstock_presence` is FMNR-specific and was not used. Source does not say that values outside these ideal ranges are unsuitable.

WOCAT's Danao, Bohol project (2006–2009) is the same case as ITTO2020 case study 4. Count one underlying case, not independent corroboration. The only prior ITTO EV in this recovery work is a separate international native-habitat safeguard, not a duplicate Danao measurement; no misleading EV-to-EV lineage pointer was invented. Identity/case lineage is recorded in both new cards and this audit.

ROAM distinctions retained:

- Table 2: heavy degradation **and** absent seed sources may require planting. Natural regeneration is not split into passive versus assisted here; no universal seed-distance threshold inferred.
- Tables 5–6 and 16: restoration need, priorities and weights are not establishment suitability. All nine Table 16 classes retain original priority, group weight and assessment score. Only two example criterion groups are shown; there is no complete-model weight denominator.
- Box 5 / Table 10 / Figure 22: protective-forest allocation and inconsistent slope labels. Box 5 says >55% and 20 m buffers; Table 10 prints “steep (55%)” and “very steep (20%–55%)”; Figure 22 instead labels very steep >55% and steep 20%–55%. Preserve conflict. Do not repair the table into an executable curve.
- Table 11: wet climate/rich soil are explicitly favourable for fuelwood growth, but not measured precipitation or SOC, and production plantations are distinct from restoration. Keep the directional wording as a mapping/scope hold, not discard it for missing cutoffs.
- Table 13: 1,000/40,000 ha are polygon delineation minima. Coastal mangrove polygons have no minimum. These are not minimum viable patch sizes. The 75% rule mixes ecological unsuitability and unavailability.
- Table 21: compound ecological readiness factors are retained. Its unusual printed legend is **yellow=in place, green=partly in place, red=not in place**; colours are not suitability scores.
- Figure 22 is illustrative; printed page 115 explicitly requires consultation and consent before on-ground assignments.

## Acquisition and handling rule

ROAM opening title matched its citation. Cached PDF bytes equal the existing team library artifact. `identity_manifest.json` records hashes and locators.

WOCAT approaches require a separate adapter from technologies. `ingest/wocat_approach.py` retrieves the published primary page, requires `/api/database/approaches/<id>/`, matching record and selected-version approach IDs, publication status and English title/description. It writes raw questionnaire and metadata sidecars plus a deterministic Markdown narrative. No effect ratings or claims are inferred.

**Locator semantics:** `locator_type=section`; locator is the source questionnaire field heading, here `description (selected_version 1972)`. Quotes preserve native text with whitespace normalization only. Nested narrative paths retain field names/indexes. Linked technologies and administrative/media/contact records are excluded from the transcript and are not treated as approach claims. Raw questionnaire remains the acquisition sidecar. The archived Markdown in this audit is the team-openable quote artifact; SRC also links the live primary page.

**QA/QC rule:** verify source title, record type, version, transcript hash, exact section containment, native quote and original page context before extraction. Existing technology adapter cannot accept this source ID. Hydration first restores the archived narrative when its hash matches SRC. Otherwise it regenerates the narrative and compares its hash with SRC before writing; changed publisher content fails rather than replacing evidence. If the publisher version changes, restore this archived Markdown to `.cache/corpus/wocat_anr_approach_1971.md`, or perform an explicit source-version review. This is a narrative web adapter, not permission for dataset intake.

## Six-axis credibility

WOCAT: medium. Explicit practical criteria but no validation sample/performance model; transparent field-visit/interview basis with no systematic documentation; institutional practice database, not a peer-reviewed experiment; Philippines case is relevant but country/site transfer is unresolved; documented 2016/version 2017; useful established ANR practice rather than evidence of quantified seminality. Promotional success statements and ITTO overlap prevent treating this as independent validation. Method `expert`, venue `grey`.

ROAM: authoritative IUCN/WRI methodological guidance, but expressly a road-test edition with country examples. Authority supports method interpretation, not universal transfer of national priorities. No additional source-support vote created.

## Holds and next steps

1. Human review of the two ANR cards, especially broad regeneration-potential mapping and degraded-forest history.
2. Exact wildling density/height/spread ontology mappings need an explicit schema decision before numeric extraction. Preserve joint ideal-site qualifiers.
3. ROAM conditional regeneration/planting guidance needs a declared family interpretation. Plantation growth factors need exact variables and appropriate production scope.
4. Resolve Rwanda slope-label conflict against country-primary methods if those allocation rules are needed; current handbook cannot settle it.
5. WOCAT functional-structure image is an operational diagram, not inspected for T4; explicitly held. Related technologies, DENR primary guidance, and ROAM's cited underlying country reports were not newly acquired or swept.

Source status remains `in_progress` where claims/mappings are held. No search completion, reviewer approval, global feedback-cursor advancement or new synthesis is claimed.
