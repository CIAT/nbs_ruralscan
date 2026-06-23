# Agroforestry — CGSpace (CGIAR DSpace) discovery (2026-06)

**Channel:** grey/lit · CGSpace open DSpace REST API (`cgspace.cgiar.org/server/api`, no auth). **Run:** `cgspace_af_2026-06`. PRISMA-lite, read-only discovery + screening.

## Why CGSpace
CGIAR's institutional repository — the home of ICRAF/CIFOR/Alliance outputs. Open DSpace API (`/discover/search/objects?query=…`); PDFs via item → bundles → ORIGINAL bitstream → `/content`.

## Queries (4) + screening
- "agroforestry land suitability mapping criteria"; "agroforestry suitability soil slope rainfall classes"; "silvopastoral/silvopasture land suitability"; "land evaluation agroforestry FAO suitability classes S1 S2". ~20 unique items screened.

## Finding — one on-scope study extracted (via OA); the rest paywalled-on-CGSpace / off-scope / wrong-NbS
- **EXTRACTED via OA copy:** *Quantification of Land Potential for Scaling Agroforestry in South Asia* (`10568/113409`) — **metadata-only on CGSpace** (no ORIGINAL bitstream; full text behind the Springer DOI 10.1007/s42489-020-00045-0), BUT OpenAlex/Unpaywall flagged it **hybrid OA, CC-BY** → fetched the Springer OA PDF (`source_id=cgspace_singh_southasia_2020`). **5 EV merged:** HWSD soil class 1-4 suitable / 5-7 not (cited Fischer 2008 + paper-own), FAO-LCCS land-cover class boundary, composite-index result (69% ≥55% suitable), observed tree-cover distribution (AF opportunity signal). `claim_basis` mixes `cited_secondary` (GAEZ/HWSD class defs) + `modelled`/`table`. **Gap:** Table 2 (per-variable weights — slope/precip/temp/soil/land-cover) is a garbled table, not text-extractable (needs OCR/table parse); slope/precip/temp are otherwise only dataset-described (off-scope) so skipped. Lesson: even a "suitability mapping" paper buries its thresholds in a weight table.
- **Off-scope (acquired + screened, then dropped):** *Biophysical characterization: SI-MFS sites, Ethiopia* (`10568/135324`, open PDF) reads as **methods / study-site characterization** ("3. Data and methods… topography of the study site was characterized… slope maps generated using DEM"), not AF suitability *rules*. The slope/rainfall are site descriptors — the off-scope defect (`check_scope` study_site). Not extracted; cache removed.
- **Wrong-NbS / restoration (don't-lump):** FLR Lake Ziway Ethiopia (`132558`), Land Restoration Chad (`117682`), degraded-land prioritization Colombia (`110304`), NbS Dolo Ado (`155265`) — restoration/NbS-broad, AF is one of several land uses.
- **Targeting frameworks → TOOL candidates (not EV):** silvopastoral spatial-targeting reports — N Laos (`10568/169649`), Ghana small-ruminant (`10568/180294`) — are *targeting methods* (like ROAM/ESI-IBSTI), better suited to the TOOL register than threshold-EV.

## Conclusion
**5 EV extracted** (one study, via its OA copy). CGSpace itself mostly hosts metadata-only journal records + reports / restoration-potential / targeting frameworks; few apply explicit AF suitability classes with variable thresholds (query 4: none apply FAO S1–N with cutoffs). Net: low yield for AF thresholds vs the **OpenAlex peer-reviewed** channel — but the CGSpace→OA-copy route works for metadata-only hybrid-OA records. **Next:** (a) Table-2 weights of `113409` need OCR/table parse to recover slope/precip/temp/soil weights; (b) register the silvopastoral targeting reports in the TOOL register if wanted; (c) WOCAT (token-walled) for SLM-tech grey.
