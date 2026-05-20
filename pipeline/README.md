# pipeline/

GEE Python implementation of the methodology + pilot Colab notebooks + GEE App.

## Structure

| Path | Contents |
|---|---|
| `mcda_pipeline.py` | Core MCDA engine — port of `../reference/R/spatMCDA.R` to GEE Python. CRITIC + Entropy + AHP weighting; weighted linear combination; classification; ±10% sensitivity. *(to be authored — see Claude Code uplift prompts)* |
| `climate_risk.py` | M2 climate risk implementation — see `../methodology/modules/M2_climate_risk.md`. *(to be authored — Brayden)* |
| `schema_loader.py` | Loads T0–T7 schema rows for a given NbS + AOI; routes to the MCDA engine. *(to be authored)* |
| `data_loaders/` | Per-dataset loaders that fetch from GEE or uploaded assets. *(to be authored)* |
| `notebooks/` | Per-pilot Colab notebooks — one per `<nbs>_<country>.ipynb`. |
| `outputs/` | Pilot outputs — one folder per `<pilot_id>/`. **`.gitignore`'d** (or LFS) for large rasters. |
| `gee_app/` | **GEE App — design owned by Benson** (see [`gee_app/README.md`](./gee_app/README.md)). The visual demonstrator that consumes pilot outputs. |

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
│   ├── opp_space_mask.tif
│   ├── sensitivity.tif
│   ├── climate_risk_baseline.tif        # M2 output
│   ├── climate_risk_<scenario>.tif
│   ├── climate_risk_delta_<scenario>.tif
│   ├── hazards/             # per-hazard surfaces
│   ├── characterisation/    # M3 outputs
│   ├── hotspots.tif         # M4 output
│   └── *.png                # PNG renders for the notebook
├── tables/
│   ├── fingerprint.csv      # opportunity fingerprint
│   ├── scorecard.csv        # T6 effects for this NbS
│   ├── climate_risk_summary.csv
│   ├── resolution_audit.csv
│   ├── weight_log.csv       # M1 weights
│   └── climate_risk_weights.csv  # M2 weights
├── cluster_log.json         # variable card metadata
├── climate_risk_meta.json   # mode + scenario record for M2
└── README.md                # one-page pilot summary
```

The GEE App (`gee_app/`) consumes these outputs to render the visual demonstrator. If the App needs additional outputs the pipeline doesn't produce, raise an issue against the relevant module spec — the contract changes together.

## Three delivery artefacts (recap)

| Artefact | Audience | Owner | Contractual? |
|---|---|---|---|
| Colab pilot notebook | WB technical team (Dany), future implementers | Benson | Yes (Phase 3) |
| GEE App | Demo viewers · WB final presentation | Benson | No — demonstrator |
| HTML wireframe | Design target · WB final presentation | Pete + Claude | No — aspirational design |

Full rationale in the *Delivery Architecture & Claude Code Uplift* note (in the project working folder).

## Starting points for Claude Code

See the **Claude Code uplift note** in the project working folder for five concrete starting prompts. The first three:

1. Port `spatMCDA.R` to `mcda_pipeline.py`
2. Scaffold the agroforestry pilot notebook
3. Build `schema_loader.py` that reads T0–T7 rows for an NbS + AOI

Each is a couple of hours of pair-programming with Claude Code.

For the GEE App specifically, see [`gee_app/README.md`](./gee_app/README.md) — Benson's design brief and process.
