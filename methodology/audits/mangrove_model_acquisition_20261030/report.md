# Mangrove model-source acquisition — 2026-10-30

## Scope and outcome

Bounded follow-up to the three sources queued in PR #494 for mangrove_restoration,
family mangrove_restoration__tidal_coastal, T4 tool/model methods. Discovery hand-off
v1.8.1 and extraction identity gates v1.9.2. No fresh discovery sweep, extraction,
SRC promotion, human approval, synthesis or search-stage advancement.

Two PDFs acquired and opening titles checked against existing queue citations:

- Rodríguez-Rodríguez et al. (2016): 15 pages; DOI round-trip via verify_metadata.py
  helpers gave title overlap 1.0; citation rebuilt from Crossref. Publisher download
  reset the connection; Semantic Scholar mirror succeeded. Source remains a species
  model candidate, not an admitted generic suitability rule.
- Worthington and Spalding (2018): 36 pages; title coverage 1.0. Ocean Wealth URLs
  timed out locally, although web retrieval exposed the full PDF. Cambridge, a named
  author institution of this report, supplied the PDF. Author/institution repository
  copy of the jointly authored report; no re-rendering or page conversion.

Both files copied immutably into the configured OneDrive SharePoint-library mirror.
Cache/library SHA256 equality checked; see acquisition.json. Cloud synchronization
and another team member's remote access were not independently verified. Queue marks
acquired, not extracted. Canonical SRC and all EV/reviewer records remain unchanged.

Twilley and Rivera-Monroy (2005) remains pending. FIU identifies the intended paper
but direct retrieval was blocked; CEMARIN links the JSTOR record. Search results with
similar text mostly reference the paper rather than provide it. The JSTOR-style DOI
candidate returns Crossref not_found and Unpaywall HTTP 404: retained in audit only,
not emitted into the queue DOI field. No verified full-text artifact acquired.
ResearchGate/Academia require a human availability check; absence is not established.
This is unresolved OA recovery, not a verified paywall or a request to contact authors.

## Retrieval trail

- https://revistas.unal.edu.co/index.php/cal/article/view/55360
- https://revistas.unal.edu.co/index.php/cal/article/download/55360/57948/312858
- https://repositorio.unal.edu.co/handle/unal/61918 (web retrieval unavailable)
- https://pdfs.semanticscholar.org/b6aa/e07cd9b0c822c32f5cc08a7b2e2c09d80852.pdf
- https://oceanwealth.org/wp-content/uploads/2019/02/MANGROVE-TNC-REPORT-FINAL.31.10.LOWSINGLES.pdf
- https://oceanwealth.org/wp-content/uploads/2018/11/MANGROVE-TNC-REPORT-FINAL.31.10.LOWSINGLES.pdf
- https://www.repository.cam.ac.uk/bitstream/handle/1810/292000/MANGROVE-TNC-REPORT-FINAL.31.10.LOWSINGLES.pdf
- https://digitalcommons.fiu.edu/record/15154
- https://www.jstor.org/stable/25736617
- CEMARIN title record linked from web search; abstract and JSTOR link inspected.
- Unpaywall by DOI: Rodríguez HTTP 200, publisher OA, no direct PDF URL;
  Twilley candidate HTTP 404. No verified DOI available for the Worthington report.

## Verbatim queries

- `"Validación y aplicación" "55360" manglar pdf`
- `"Developing performance measures of mangrove wetlands" pdf`
- `"Mangrove Restoration Potential" "2018" report Worthington Spalding`
- `Twilley Rivera Monroy 2005 "performance measures" filetype:pdf`
- `Twilley 2005 "79-93" pdf mangrove ResearchGate`
- `"Developing performance measures of mangrove wetlands" Twilley 2005 PDF ResearchGate repository`
- `"Mangrove Restoration Potential" Worthington Spalding 2018 pdf IUCN`
- `"Validación y aplicación de un modelo de restauración" PDF Rodriguez 2016`
- `"mangrove-tnc-report-final.31.10.lowspreads.pdf"`

Queries recover known sources, not independent included-source counts. No SRCH row
or saturation claim added. Only three pre-existing queue rows changed.

## Next hand-off

Promote the two acquired sources only after source classification and six-axis
credibility review. Read and inventory relevant methods, tables and species scopes
before staging any evidence. Resolve Twilley access separately. The existing ten
mangrove-guide records can remain in human review throughout.
