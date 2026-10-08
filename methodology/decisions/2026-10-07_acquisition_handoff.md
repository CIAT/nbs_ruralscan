# Source acquisition hand-off (2026-10-07)

**For:** split 2026-10-08 — **Charity** (`…_handoff_charity.xlsx`, 83 rows: free browser-click copies + ResearchGate / Academia checks) and **Namita** (`…_handoff_namita.xlsx`, 38 rows: institutional journal access). **From:** the NbS Rural Scan evidence pipeline (Pete Steward). Plain-language; no tooling needed beyond a browser and SharePoint.

## What this is

Our evidence tables are built only from sources whose full text we hold. 192 sources that our searches flagged as relevant could not be fetched automatically. Each one needs a human to find and save the PDF. Nothing else: no reading, no judging relevance.

## How to do one row

1. Open `2026-10-07_acquisition_handoff.csv` (same folder). Work top to bottom: priority 1 first.
2. Follow **what_to_do** for the row (the **bucket** says why it was blocked). Try the **url** and the **doi** (`https://doi.org/<doi>`) first.
3. Save the PDF to SharePoint at the path in **save_to_sharepoint**, named exactly as **file_name** (the source id). Same name is what links the file to the register.
4. Put `yes` in **done** (or `no copy found` / `wrong paper` if that is the outcome) and, if you found it somewhere unexpected, note where in **blocker_note**.
5. Send the CSV back (or commit it) when you stop; partial progress is fine.

Two cautions: the **citation is the trust anchor** (a DOI can resolve to the wrong paper; if title and DOI disagree, save the paper matching the title and say so); and please do not retype or "clean" anything in the file.

## What is in the list

Rebuilt after the 2026-10-07 open-access recovery pass (Unpaywall by DOI → automatic re-acquire → three web-search lanes): 71 of the original 192 were fetched automatically; 121 remain.

| bucket | meaning | n |
|---|---|---|
| A_free_click_and_save | A free copy exists at the url but our downloader is blocked: open the url in a browser, save the PDF. | 27 |
| B_researchgate_check | Search ResearchGate / Academia (and Google Scholar) for a free full text; if found, download. Else try institutional access. | 56 |
| C_institutional_access | Automatic + web search found no free copy: download through institutional (university / CGIAR) journal access. | 38 |

By NbS: agroforestry 41, forest_restoration 19, riparian_buffer 1, water_harvesting_conservation 52, wetland_management 8. Priority 1 = free copies that only need a browser click (27); priority 2 = institutional access (38); priority 3 = ResearchGate / Academia checks (56).

## What happens after

The pipeline hydrates its cache from the SharePoint library, verifies each PDF's title against the citation, and only then extracts. Rows marked `no copy found` are retired from the queue as verified-inaccessible.

Technical record: `pipeline/acquisition_queue.csv` (status `pending`), `methodology/search_protocol.md` §OA-recovery.
