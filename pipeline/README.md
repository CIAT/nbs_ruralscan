# pipeline/

GEE Python implementation of the methodology + pilot Colab notebooks.

## Structure

| Path | Contents |
|---|---|
| `mcda_pipeline.py` | Core MCDA engine — port of `../reference/R/spatMCDA.R` to GEE Python. CRITIC + Entropy + AHP weighting; weighted linear combination; classification; ±10% sensitivity. *(to be authored — see Claude Code uplift prompts)* |
| `schema_loader.py` | Loads T0–T7 schema rows for a given NbS + AOI; routes to the MCDA engine. *(to be authored)* |
| `data_loaders/` | Per-dataset loaders that fetch from GEE or uploaded assets. *(to be authored)* |
| `notebooks/` | Per-pilot Colab notebooks — one per `<nbs>_<country>.ipynb`. |
| `outputs/` | Pilot outputs — one folder per `<pilot_id>/`. **`.gitignore`'d** (or LFS) for large rasters. |

## Conventions

- **Notebooks are the contracted deliverable.** They must be self-contained: authenticate GEE, load recipe from schema, run the pipeline, write outputs, render maps + tables inline.
- **Pipeline reads from schema, never hardcoded.** If a value (variable list, threshold, weight) appears in a Python literal, it belongs in T0–T7 instead.
- **Markdown cells document every step in plain language** so a WB analyst can follow without verbal explanation.
- **Reproducibility** — every run records its config in `outputs/<pilot_id>/run_config.json`: NbS ID, recipe version, schema version, AOI, resolution, date, dataset versions, weights used.

## Output folder structure (per pilot)

```
outputs/<pilot_id>/
├── run_config.json          # full run configuration
├── maps/
│   ├── suitability.tif      # M1 output
│   ├── suitability_class.tif
│   ├── climate_risk.tif     # M2 output
│   ├── characterisation/    # M3 outputs
│   ├── hotspots.tif         # M4 output
│   └── *.png                # PNG renders for the notebook
├── tables/
│   ├── fingerprint.csv      # opportunity fingerprint
│   ├── scorecard.csv        # T6 effects for this NbS
│   ├── resolution_audit.csv # native vs analysis resolution per dataset
│   └── weight_log.csv       # AHP + CRITIC + Entropy reconciliation
└── README.md                # one-page pilot summary
```

## Starting points for Claude Code

See the **Claude Code uplift note** in the project working folder for five concrete starting prompts. The first three:

1. Port `spatMCDA.R` to `mcda_pipeline.py`
2. Scaffold the agroforestry pilot notebook
3. Build `schema_loader.py` that reads T0–T7 rows for an NbS + AOI

Each is a couple of hours of pair-programming with Claude Code.
