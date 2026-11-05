# Pietsch and Mabit (2012): complete bounded T4/operational review

Date: 2026-11-05. Ruleset v1.9.4; T4 contract and defect catalogue applied. Source ID remains `dahlke_2012_terrace_soils_yemen_suitability` despite misleading historic prefix. No register, queue, ledger, review decision or git edits.

**Result: zero eligible T4 units; zero eligible operational-risk units; zero executable functions.** All 13 PDF pages read; four tables and six figures accounted; all six figures visually inspected from rendered pages. No supplementary file cited in main paper; this does not claim external supplement acquisition. `units.json` intentionally empty. No human approval granted.

## Identity and availability

Opening title and DOI match queue. Actual authors are D. Pietsch and L. Mabit, not Dahlke; queue citation's “et al.” is imprecise. Queue already says `doi_verified=true`; no new Crossref verification claimed. Team OneDrive/SharePoint mirror exists and SHA-256 equals cached artifact. DOI/title/source-ID scans of SRC and EV found no canonical duplicate. See `identity.json`; metadata suggestion preserves source identity. New SRC promotion is unnecessary for zero-unit closure.

Deterministic index built: 13 pages, nine machine table detections, no OCR pages. These nine machine regions are **four publication tables**, not nine independent tables. Retrieval package generated for soil depth, texture, pH, salinity, slope, rainfall and labour; full-paper reading governs completeness.

## Scope and main-paper accounting

108 anchored disposition entries, including whole-table header/footnote records, eight Table 1 comparative rows, four Table 2 depth groups, 40 Table 3 horizon rows, 23 Table 4 geochemical observations, six figures, and 23 narrative/section items. Counts include overlapping table-level and row-level records; they are **not 108 independent scientific claims**. Every quote is a contiguous exact substring of its recorded page. Page text and rendered figures retained; `dispositions.json` retains numeric source values, missing cells, units and cited lineage without turning them into analytical parameters.

- Table 1 (PDF3 / printed50): eight historical comparative terrace-site rows; all relief, elevation, rainfall/erosivity, erodibility, soil, nutrient, crop and irrigation columns preserved. Not establishment criteria.
- Table 2 (PDF6 / printed53): four depth groups, four radioisotopes, measurement errors and detection limits. Scientific-method quality context.
- Table 3 (PDF7 / printed54): Jid-Cs two horizons; Ir16 one dating row; Ir15 four; Ir02 fourteen; Ir01 nineteen. All 40 rows retained, including unlabeled depth continuations. Measured physical/chemical/radiometric profiles of existing terraces, not pre-establishment suitability thresholds.
- Table 4 (PDF9 / printed56): nineteen Ir01 and four Jid-Cs geochemical observations. Weathering reconstruction; no criterion weights, suitability scores or class gates.
- Figures 1–3: location map, terrace cross-section and sampled-profile map. Figure 4: elevations/stratigraphy/dates. Figure 5: observed grain-size depth profiles. Figure 6: radionuclide activity by depth. No suitability legend.

## Critical exclusions and retained pointers

Paper evaluates whether **soil already accumulated behind terrace walls supports crop agriculture** and how these old terraces degrade. It does not establish where new terraces can be built. Conclusion's pH 8.4, salts <0.2%, CaCO3 <4%, loamy texture, rainfall 600–800 mm/year and k-factor 0.3–0.5 therefore cannot enter terracing T4. Neither observed slopes 1–30° / >30° nor deposited profile thickness 42 to >640 cm is a construction envelope. No general practice-use/direction vote manufactured from study measurements.

PDF10–11 discusses nutrient availability, pH and salinity for “most/all crops”, often using Landon (1993). These are generic agricultural-soil evaluations, not identified crop-taxon calibration or terrace-establishment rules. Pav and Kav were not directly measured in this study; potential inferred from total oxides remains explicit. Native text's Ir02/Ir01 wording and reported unit inconsistencies are retained, not silently corrected.

PDF1 migration → abandonment statement is cited-secondary (Steffen 1981; Vogel 1988). It does not explicitly identify seasonal labour availability as cause, so no labour/credit/tenure proxy unit. PDF5 lack of wall maintenance → erosion is practice-specific Module 6 detail; no supported canonical socioeconomic factor. PDF2 runoff/infiltration/storm and PDF5/10/11 erosion observations retained as **future effect/asset-risk review pointers**, not extracted in this T4/operational lane. Cited Vogel/Fassbender lineages retained for any later authorized evaluation.

Accumulation 4 m / 2000 years versus 2 m / 200 years compares different terrace positions, histories and geomorphic processes. No terrace-versus-control effect can be inferred. Modern radioisotopic erosion rates are explicitly future work; baseline is not effect.

## Validation and closure

Build script checks every disposition quote against page text before writing. Team/cache hash matches; opening title/DOI match; no existing SRC/EV duplicate; all pages and tables accounted. No units means unit validation/ingestion gates are not applicable; central orchestrator should review semantic accounting before updating queue note. Keep `acquired` with explicit completed no-T4 review note; do not stamp `extracted=done` without EV. No source promotion to `swept`, no review approval and no learning-cursor advance.

Retrospective: prevented recurring site-context-as-threshold defect (#16) despite suitability in paper title. Also retained baseline-versus-effect (#28), proxy mismatch (#4), causal operational factor (#50), and full main-paper accounting (#34). No novel defect discovered; parent owns sweep metrics and any ledger/retrospective updates.
