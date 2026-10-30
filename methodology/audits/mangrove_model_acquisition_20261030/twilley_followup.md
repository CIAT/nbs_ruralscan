# Twilley access follow-up — 2026-10-30

Bounded recovery of `twilley_rivera_monroy_2005_performance`, already queued for
mangrove T4 tool/model methods. No fresh discovery counts or stage advancement.

## Result

No verified PDF acquired. Queue remains pending; DOI and title verification remain
blank. No SRC/EV promotion, extraction, review decision or synthesis. Access remains
unresolved, not paywalled. ResearchGate now provides a specific human-download lead.

## Checks

- FIU current record: https://digitalcommons.fiu.edu/record/15154 — local HTTP 202,
  zero bytes; browser blank. Indexed metadata identifies the intended title.
- OpenAlex exact-title result https://openalex.org/W1534019290 — DOI null;
  locations include the current record, old article URL below, and
  http://digitalscholarship.fiu.edu/record/15154.
- https://digitalcommons.fiu.edu/fce_lter_journal_articles/47/ — web initially
  exposed the title/navigation, then HTTP 403; local retrieval zero bytes.
- https://digitalscholarship.fiu.edu/record/15154 — local retrieval zero bytes.
- https://biblioteca.phorteeducacional.com.br/items/7401279 — local HTTP 502;
  indexed metadata only, not a recovered artifact.
- https://www.researchgate.net/profile/Robert-Twilley/2 — exact paper listed as
  full text available; followed its publication link below. Publication page says
  content uploaded by Robert R Twilley on 18 January 2014. This is an availability
  lead, not proof that the team can download the file.
- https://www.researchgate.net/publication/254593611_Developing_performance_measures_of_mangrove_wetlands_using_simulation_models_of_hydrology_nutrient_biogeochemistry_and_community_dynamics — rendered OCR body and Download full-text PDF link exposed.
  Web-followed download returned HTTP 404 with an extra `/publication/` prefix.
  Removing that prefix to normalize the profile path returned HTTP 403 HTML
  (20,178 bytes), not PDF. No HTML was saved into the PDF corpus.
- Earlier Crossref and Unpaywall checks for candidate `10.2307/25736617` returned
  404 (see acquisition report/metadata audit). Candidate remains outside queue DOI.

Searches covered title/author/year/PDF, FIU/FCE and LSU institutional routes,
ResearchGate/Academia, and old FIU article/47 identifiers. Results containing only
references (including FCE reports) were not treated as copies of the paper.

## Human hand-off

Open the ResearchGate publication link above in a normal signed-in browser and
check **Download full-text PDF**. If available, acquire the original 15-page paper,
Journal of Coastal Research Special Issue 40, printed pages 79–93. Verify its opening
title/authors and use the existing immutable cache/library acquisition workflow.
The existing DOI-less publisher-domain identity gate still needs resolution before
promotion: an author-uploaded mirror is not automatically a publisher-domain copy.
Do not replace that gate with a ResearchGate availability label. If the download
cannot be obtained, check institutional JSTOR access at
https://www.jstor.org/stable/25736617. No author contact was made or requested.

Existing evidence review can continue independently of this source-access hold.
