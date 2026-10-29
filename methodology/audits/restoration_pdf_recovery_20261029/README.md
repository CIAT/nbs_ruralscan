# Restoration PDF recovery — 29 October 2026

## Result

Retried the three pending identities from the 28 October acquisition batch. **No new PDF was recovered.** All three remain pending, access status unknown. No source was labelled paywalled, promoted to SRC, extracted, or stamped reviewed. Acquisition remains 26/29 candidates; the subsequent review count remains 20/29. No library or corpus files were written.

## Verified routes and outcomes

| Source | Direct retrieval | Browser retrieval | Next useful action |
|---|---|---|---|
| Ioki 2025 | Wiley pdfdirect returned HTTP 403, HTML rather than PDF | Publisher record loaded; its Download PDF link timed out after 40 seconds without a saved path | Manual publisher download; preserve Supplement S1 master DOCX and once-rendered PDF if acquired. Author/repository or ResearchGate follow-up remains possible, not an asserted absence. |
| CONAFOR 2015 | Official SEMARNAT connection reset | Same exact PDF failed with ERR_CONNECTION_RESET | Retry official host from another connection or obtain exact 2015 edition from team holdings; do not substitute 2023 manual or programme regulations. |
| Sidik 2025 | Twente PDF returned HTTP 403, HTML rather than PDF | Repository record loaded; final-version PDF download timed out after 45 seconds without a saved path | Manual retrieval of the repository final version; metadata visibility does not establish possession of the PDF. |

Machine-readable retrieval receipts are in `receipts.json`. These are tooling/host failures, not proof of a paywall. Earlier Unpaywall findings remain in `../restoration_acquisition_20261028/unpaywall_recovery.json`; they were not rerun here.

## Exact links

- [Ioki publisher](https://onlinelibrary.wiley.com/doi/10.1111/rec.70113); [observed Download PDF link](https://onlinelibrary.wiley.com/doi/pdf/10.1111/rec.70113).
- [Ioki Supplement S1](https://onlinelibrary.wiley.com/action/downloadSupplement?doi=10.1111%2Frec.70113&file=rec70113-sup-0001-Supinfo.docx): publisher Supporting Information panel identifies a 1.8 MB DOCX, including species-specific growth-response Table S1. Link inspected; supplement not downloaded or read.
- [CONAFOR exact 2015 PDF](https://biblioteca.semarnat.gob.mx/janium/Documentos/Ciga/libros2018/CD004912.pdf).
- [Sidik repository record](https://research.utwente.nl/en/publications/hydrological-suitability-for-mangrove-species-in-restored-mangrov/); [observed final-version PDF](https://research.utwente.nl/files/514860335/1-s2.0-S0304377025000087-main.pdf), listed as 5.93 MB with Taverne licence.

## Focused recovery search

Web searches run on 29 October 2026:

- `"Navigating effective tropical forest restoration" pdf Ioki`
- `"Manual de restauración forestal y reconversión productiva" pdf 2015`
- `"Hydrological suitability for mangrove species in restored mangroves" pdf`

Results reconfirmed Wiley, SEMARNAT and Twente/ScienceDirect routes. A Scribd transcription and FAO-hosted programme regulations were not substituted for the official CONAFOR artifact. No broad discovery search or new source identity was registered. Search results and abstracts were not used as extractable evidence.

## Validation

Only the three existing acquisition-queue blocker/note fields changed. Status, access classification, identity stamps, DOI, family, table and assignments remain unchanged. No progress stage advanced. Queue row identity and untouched-row checks passed; generated-file consistency checked separately.
