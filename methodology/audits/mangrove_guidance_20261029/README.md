# Mangrove guidance review — 29 October 2026

This bounded batch reads selected diagnostic and restoration sections of the UNEP Western Indian Ocean guide (2020) and FFEM guide (2024), under extraction ruleset v1.8.0. **Six unapproved qualitative units enter EV: four structural and two operational.** No numerical suitability function, runtime weight, human approval or recipe change is introduced.

This is **not a full review of either book**. The PDFs contain 73 and 71 pages respectively; FFEM PDF pages are two-page spreads. `page_coverage.json` distinguishes 22 UNEP and 23 FFEM pages read from pages merely indexed. Both SRC records remain `in_progress`; queue `extracted` denotes partial extraction. All earlier human decisions remain unchanged. The prior 20/29 selected-artifact review count is not turned into 22 completed sources: two additional candidates are now partially reviewed, seven remain untouched, and separate ITTO reuse and earlier holds remain.

## Admitted evidence

| Source | Variable / destination | Retained meaning |
|---|---|---|
| UNEP PDF28, printed11 | land_cover / T4 qualitative | Avoid planting in non-mangrove seagrass beds, mudflats and sandflats. Native habitat labels retained; no exhaustive raster crosswalk inferred. |
| UNEP PDF29, printed12 | regeneration_potential / T4 qualitative | Consider natural recruitment with propagule supply and stress removal, then evaluate planting if recovery fails. Six-to-twelve months is a reassessment interval, not a suitability cutoff. |
| UNEP PDF36, printed19 | tenure_security / M2b-B, M6 | Clarify ownership and long-term agreements; no tenure index or hard exclusion. |
| UNEP PDF36, printed19 | extension_governance / M2b-B, M6 | Iterative community engagement throughout restoration; not a measured effect size. |
| FFEM PDF25, printed48–49 | soil_texture / T4 qualitative | Sand/silt/clay assessment is recommended for diagnosing restoration failure or success. No preferred texture or fitted response supplied by this passage. |
| FFEM PDF37, printed72–73 | regeneration_potential / T4 qualitative | Healthy adjacent forest and propagule availability favour natural colonisation following hydrological rehabilitation, without obligatory planting. |

The family contains both planting and ecological mangrove restoration. Greater natural regeneration potential reduces the **need for planting**, not the suitability of the whole family. Therefore no scalar increasing/decreasing family curve is asserted; branch-specific directional interpretation is retained in context, with `relationship.direction=unclear` for the combined family. This is not loss of the method-selection relationship. The six records supply no spatial-model importance weights, no fitted model-use votes and no calibrated functions. French anchors retain English translations separately after the substantive native quote.

## Source values and exclusions

`source_value_inventory.json` preserves **44 contiguous native anchors**: all 15 RAM indicators, all eight degradation-response scenarios in FFEM Table 5, 18 species rows from UNEP Tables 5–6, and three method/conflict/classification anchors. `holds_and_followups.json` records additional locators and disposition. Every anchor matches its stated PDF page; key tables and Figure17 were visually checked.

UNEP's nine species rows in each nursery table concern propagule availability, maturity, storage, treatment, sowing depth, shade, germination and out-planting size/age. These remain species-specific implementation information, not landscape establishment envelopes. The seasonal and germination-quality caveats apply. Tables3–4 compare natural/artificial regeneration; Table7's nine failure and nine lesson bullets are independent lists, not nine paired causal estimates. Remaining nursery and ecological sections still require review.

Tidal connection, flood frequency, water depth, inundation duration, salinity, redox and microtopography are distinct. The guides' composite hydroperiod is not automatically percent time flooded. Porewater salinity/pH is not the soil-salinity/soil-pH dataset proxy. Channel dimensions and orientation, planting depth and sampling depth are engineering or measurement choices. They were not converted to ecological thresholds.

FFEM Figure17 (PDF26, printed51) shows salinity classes 3–9, 10–19, 20–45, 46–70 and >71 UPS, plus redox classes >−200, −221 to −290, −291 to −350 and −351 to −500 mV. These are native environmental classifications, not suitability curves. Gaps and endpoint ambiguity remain; no missing classes were completed. The source's 3-cm microrelief and 60–80 UPS example (PDF23) describes a cited vegetation contrast, not global limits. Local reference-site matching remains essential.

## RAM condition assessment: retain, do not miscompile

FFEM explicitly presents RAM as a snapshot of ecosystem condition. It averages 15 ordinal 0–3 indicators across landscape connectivity, trees, substrate, associated biodiversity and social relationships. The protocol was developed for Senegal's Saloum and explicitly requires recalibration elsewhere (PDF30, printed58–59). It can assist restoration diagnosis and monitoring; it does not estimate planting survival or an NbS effect. The Saloum example's 2.44/3 is a condition score, not a validation statistic or suitability probability.

All 15 indicators and their native classes remain in the inventory, including genus-specific porewater salinity bands. Rhizophora's 35–45 g/L and Avicennia's 55–65 g/L are the rubric's highest condition classes, not universal species optima. No blanket mangrove salinity preference was inferred. Protection and sustainable-use indicators intentionally pull in different directions for strict reserves; this is the source's normative socio-ecological design, not a protected-area mask.

Visual inspection confirms unresolved source problems:

- Texture score2 requires **more than 50% mud and more than 50% sand simultaneously**. This is present on the printed page, not introduced by text extraction.
- Recruitment classes overlap at roughly four/five seedlings; mortality classes overlap and do not clearly allocate exactly50%. Canopy/cover and aggregate-score endpoints also need interval conventions before implementation.
- Table5 recommends culverts for road barriers (PDF36, printed71), while adjacent prose advises against culverts and recommends bridges (PDF37, printed73). Neither becomes a universal engineering instruction.
- Topographic scenario wording needs interpretation alongside the prose: raising subsided/eroded sites and lowering accreted ones are corrective actions, not claims that subsidence itself raises terrain.

These conflicts are retained for review; no source correction, new ontology field or schema redesign is made.

## Credibility and lineage

Both are institutional expert guidance, assigned **medium** as a ceiling for these claims. UNEP names regional contributors and technical support, with GEF/WIOSAP and SIDA/MASMA backing; authority and regional practical experience do not provide independent experimental validation. FFEM names chapter authors from research institutions and consultancy/practitioner organisations; its recent publication and transparent diagnostic methods do not repair the printed contradictions. RAM reports personal-communication corroboration at Saloum, not transferable restoration-performance validation. No seminality or conflict-free status is assumed.

Repeated references to Lewis, Bosire, Kairo, Agraz Hernández and related methods must not become independent evidence votes merely because two guides reproduce them. UNEP's hydrological-restoration references remain in attribution. FFEM RAM points to Macera2024 and primary methodology; those are follow-up leads, not newly verified or acquired identities. Mikoko's portal is a discovery lead on PDF23, not a dataset intake. No new discovery search was performed.

## Verification and retrospective

Opening-title checks pass for both artifacts; cached PDFs match the team OneDrive library mirror byte-for-byte. Remote sync was not independently checked. Deterministic indexes were built with table extraction and all-VONT passage retrieval. The index's low-text flags identify front matter/blank pages; no numerical claim relies on them. Machine table fragments are not represented as complete semantic table counts.

Central gates pass for all six units: provenance, numbers, context, role, ontology, family and ruleset. An initially narrow habitat quote was expanded to its complete planting sentence before publication; `prepublication_correction.json` records that correction to this batch's new unapproved record. No pre-existing record was edited. Advisory checks and preservation results accompany this report.

Existing safeguards covered source transcription errors, ordinal condition-versus-suitability scope, compound hydrological variables, proxy substitution, native-language provenance and within-family method choice. No new defect category is claimed. Global sweep metrics are a snapshot, not evidence of improved rates; no global human-feedback cursor advance. Remaining pages and linked sources stay pending.

Validation details: `validation.json`, `batch_checks.json`, `preservation_checks.json`. Full-project type checking exposes pre-existing diagnostics in unchanged audit/test files; the CI-scoped core type check is reported separately. No unrelated code fixes are bundled.

Global number-provenance and verification rates remain 5.7% and 0.1%; no decline or improvement claimed. New-unit scope, species, quote and number checks are empty after the quote-context correction. Full tests: 960 passed with five warnings; structure: zero errors, 3,499 existing/reference-format warnings; T4 coverage: zero errors. Lint, format and CI-scoped type checks pass. Broad type checking reports 149 diagnostics in unchanged files.
