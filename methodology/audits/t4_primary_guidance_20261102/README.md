# T4 primary-guidance recovery — 2 November 2026

This bounded follow-up resolves the three primary-document leads left by the [ITTO audit](../itto_tool_resolution_20261102/README.md). It stages evidence sources for review; it does not extract EV, change T4 functions, approve evidence, or work in the other session's T3/T6 lane.

| Lead | Result | Next gate |
|---|---|---|
| WRI Restoration Diagnostic | Primary 2015 English PDF recovered, 96 native pages. Table 7 has ecological establishment questions. | Full-source reading; separate ecological questions from seed procurement, markets, tenure and other operational conditions; assign families. |
| IUFRO “Spotlight” | Spotlight 35 is a newsletter pointing to the **stoplight** method in World Series 34. Both primary PDFs recovered. | Chapter 6 is a planning/communication referral, not a T4 curve. Remaining report chapters are not fully screened. |
| DENR Technical Bulletin 27 | Official migrated index links the 15-page public scan. Title and 1 July 2019 stamp visually checked on page 1. | OCR/text identity gate, full reading and mapping review; retain original scan unchanged. |

## What the primary pages establish

**WRI:** native pages 30–32 explain the case-based method and its causal limitations. Pages 34–35 list factors; pages 48–50 (printed 44–46) separate ecological conditions from markets and policy. The ecological questions cover physical conditions, interfering vegetation/animals and regeneration sources. They do not provide numeric thresholds. Seed sources include both in-situ biological potential and supplied planting material: do not merge these into one structural T4 variable. Market access, tenure, finance and extension remain operational-risk/Module 6 referrals. General diagnostic scores cannot become fuzzy membership values. Full 96-page extraction reading remains outstanding.

**IUFRO:** native pages 54–60 (printed 51–57) explain the stoplight method and Tables 6.1–6.5. The same colors have different meanings across implementation status, stakeholder priority, consensus, alternative desirability and benefits. These are not validated ecological suitability classes. Spotlight 35 and World Series 34 represent one publication lineage. Native page 51 has a species/provenance mapping lead; retain for species-specific follow-up, not a practice-wide climate envelope. This targeted chapter review does not establish that the rest of the 75-page report lacks T4 evidence.

**DENR:** native/printed page 2, section D, names suitable areas, including degraded/open forest lands and particular restoration objectives. Protected-area examples are jurisdiction-specific restoration contexts, not permission to override project legal masks. Page 3, section F.I.1.3, specifies an ideal 600–700 vigorous wildlings/ha, height 15–200 cm, relatively well spread. Its note routes areas below 600 toward reforestation and above 700 toward enrichment planting. These distinct treatment routes preclude simply translating this passage to a monotonically increasing ANR suitability curve. WOCAT Approach 1971 uses closely matching language; the recovered bulletin is not independent empirical validation. No numeric EV or curve was added here.

## Acquisition and identity

- WRI: [publisher page](https://www.wri.org/research/restoration-diagnostic) → public download form → [primary PDF](https://files.wri.org/d8/s3fs-public/WRI_Restoration_Diagnostic_1.pdf). The form exposes a direct download without submitting an email. No DOI supplied by the English publisher record; secondary ResearchGate identifiers and the Portuguese translation DOI were not assigned to it.
- IUFRO: [Spotlight 35](https://www.iufro.org/media/fileadmin/publications/spotlights/spotlight35-forest-landscape-restoration.pdf) → [World Series 34](https://www.iufro.org/media/fileadmin/publications/world-series/ws34.pdf). Referral artifacts are retained in the team library with hashes, not registered as duplicate T4 votes.
- DENR: old `forestry.denr.gov.ph` paths failed; root redirected to `fmb.denr.gov.ph`. The new homepage links [Technical Bulletins](https://fmb.denr.gov.ph/fmb_web/?page_id=2553), which links [the public PDF](https://drive.google.com/file/d/1EW8lPh-OqzkswWnCvXoFN861iQYPmSe8/view). Drive connector metadata confirmed the PDF identity, followed by public original-byte download. All 15 pages lack a text layer. The title/date were visually checked, but automated title verification and extraction remain blocked pending OCR. This is not a paywall. No scanned document was silently passed through the text identity gate.

`snapshot_manifest.json` records original PDF hashes and explicit screened-page coverage. `acquisition.json` records cache/library locations and final queue state. Copies in the local OneDrive-backed SharePoint library are published without replacing different existing files; remote sync is not independently verified.

## Scope, counts and omissions

Generic tool protocol: three distinct primary works inspected (WRI guide, IUFRO newsletter, IUFRO report), one included. ANR grey protocol: one distinct primary work inspected (DENR bulletin), one included with an OCR hold. Landing pages and PDF endpoints are not extra records. Counts describe this selected recovery set, not all search-engine results.

Stock reconciliation checked existing SRC, acquisition queue and prior ITTO/ROAM-WOCAT logs. No matching canonical source rows existed for these new candidate identities. Existing SRCH/ledger history was retained, with no new whole-family completion stamp. Fresh stock and updated-literature sweeps were not run. English exact-title web searches and direct publisher links were used; no multilingual expansion, OpenAlex, Lens, AGRIS or code-host sweep. This is a fixed three-lead recovery stop, not saturation.

The WRI XLSX assessment workbook remains a dataset-intake hold. Its 16 companion case PDFs and translations remain seeds, not acquired or counted independent studies. The IUFRO 2017 practitioner handbook surfaced incidentally but lies outside this batch. No author contact occurred.

## Next substantive batch

1. Prepare page-preserving OCR for DENR, validate against the scan, and complete all 15 pages under the extraction skill. Resolve how the local density/treatment guidance maps to ANR variables before proposing any numeric use.
2. Complete WRI's 96-page source review, including tables/appendices; extract only eligible, family-resolved qualitative criteria with the required independent verification and retrospective.
3. Review the remaining IUFRO ecological-method chapters only if the T4 gap inventory warrants it. The stoplight identity hold is closed; no further tool-identity search is needed.

Validation results are recorded in `validation.json`.
