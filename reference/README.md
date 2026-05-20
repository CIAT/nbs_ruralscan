# reference/

Source material that informed the framework and recipes — kept here for citation and reproducibility, not for active editing.

## Structure

| Path | Contents |
|---|---|
| `R/spatMCDA.R` | Original R MCDA prototype by Benson Kenduiywo. The reference implementation that the GEE Python pipeline (`pipeline/mcda_pipeline.py`) ports. |
| `stocktake/` | Stocktake review findings — extracted patterns from the 85 reviewed studies. Pointers to the canonical docx on OneDrive. |

## Conventions

- **Don't modify files here in flight.** If a reference asset needs updating (e.g. a fix in `spatMCDA.R`), modify it, log the change in a comment header, and reference the change in the relevant `pipeline/` module that consumes it.
- **Canonical source materials** (the Stocktake Review docx, the inception report, meeting transcripts) live on OneDrive at `D591_Rural-Scan_NBS/`. This folder mirrors what we need locally for reproducibility.
