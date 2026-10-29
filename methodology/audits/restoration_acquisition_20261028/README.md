# Restoration candidate acquisition — 28 October 2026

This round follows discovery PR #467. Of its 29 new candidate identities, **26 now have
acquired artifacts**: 18 PDFs (915 pages), one FAO HTML page, and selected code files
from seven repositories. Three PDF downloads remain pending. Acquisition does not
establish scientific suitability, source-complete extraction, or approval.

## Verified acquisition

- The PDF acquisition script ran on isolated slices containing only these candidates.
  Eleven PDFs succeeded initially. OA recovery and existing team stocktake copies supplied
  seven more. All 18 passed opening-title identity checks; each cached PDF matches its
  copy in the team SharePoint library's local OneDrive mirror byte-for-byte.
- Forest PDFs use `library/2_ForestRestoration/`; standalone mangrove PDFs use the new
  `library/6_MangroveRestoration/` folder. The manifest and queue retain complete library
  paths. Local mirror persistence was verified; remote OneDrive sync completion was not
  independently verified.
- Nine acquired papers retain the DOI verification from discovery. Nine DOI-less PDFs
  and the FAO HTML snapshot passed the existing title verifier (10 checks, no failures).
  Mahdavi's DOI resolver reached the correct CJES publisher page, but Crossref returned
  `not_found`; acquisition therefore remains title-verified with DOI blank. The publisher's
  own `citation_pdf_url` supplied the 18-page paper.
- `ingest.github.acquire_file` fetched 13 selected files from seven repositories at their
  full immutable commits. The code manifest records each path, source ID, hash and cache
  location; canonical queue URLs now point to the primary pinned file. Companion files
  retain separate adapter IDs. These are selected-file acquisitions, not whole-repository
  archives or independent evidence votes.
- Code rows remain explicitly blocked from source admission/extraction pending identity,
  locator, lineage and practice/species scope checks. No PDF-style `title_verified` stamp
  was invented for code. FAO also requires its source/section-locator admission step.
- Existing ITTO 2020 PDF passed an opening-title recheck. Its acquired queue state and
  pending active-planting scope-review task were preserved.

The manifest contains hashes, page/text-layer counts, artifact paths, URLs and remaining
blockers. No pre-existing source outside the 29 discovery candidates was changed. SRC,
EV, recipes, search protocols, progress stages and human review decisions were not changed.

## Remaining downloads

| Candidate | Finding | Next action |
|---|---|---|
| Ioki 2025 enrichment planting | Unpaywall identifies the Wiley open PDF; direct and pdfdirect routes failed through tooling. Publisher lists Supplement S1, including species-response Table S1. | Retrieve publisher PDF in browser; obtain linked DOCX supplement and preserve master plus once-rendered PDF under the existing document rule. Manual ResearchGate/author-repository check remains available; no claim of absence there. |
| CONAFOR 2015 manual | Official SEMARNAT PDF URL repeatedly timed out. Search also surfaced a newer 2023 manual and programme regulations, which are different sources. | Retry the exact 2015 PDF in browser. Do not substitute another edition or regulations under this ID. |
| Sidik 2025 abandoned ponds | Unpaywall has no PDF location, but University of Twente lists a public final-version PDF under its Taverne route. Both direct download and a download-query retry returned 403. | Retrieve the repository PDF in browser. This is an access-tool blocker, not evidence of a paywall. |

No source was labelled paywalled or assigned to another team member. Useful browser routes:
[Ioki publisher PDF](https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/rec.70113),
[CONAFOR 2015 manual](https://biblioteca.semarnat.gob.mx/janium/Documentos/Ciga/libros2018/CD004912.pdf),
[Sidik repository record](https://research.utwente.nl/en/publications/hydrological-suitability-for-mangrove-species-in-restored-mangrov/).

## Recovery trail and hand-off

`recovery_attempts.json`, `recovery_second.json`, `mahdavi_recovery.json` and
`unpaywall_recovery.json` retain outcomes. `web_search_recovery.md` records exact web
queries and the source routes they revealed. `source_manifest.json` is the final state;
earlier failed-attempt records remain historical.

Notable recoveries: Chen and Hossain were already in the team's stocktake; Griffith supplied
Villarreal-Rosas; PLOS supplied Pérez-Ceballos; Mangrove Action Project supplied Lewis;
Diálogo Florestal supplied CEDAGRO after the original host's expired certificate failed.
All recovered documents passed the same identity gate before library copying.

Next extraction must inventory tables, continuations, figures, cited lineages and supplements;
retain species-specific and broad-restoration scope holds from discovery. No new EV units,
source-quality approvals, source-complete claims or suitability values are produced here.
Validation: source/hash/title and untouched-row checks, schema regeneration and CI.
