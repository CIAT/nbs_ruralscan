# pipeline/

Per-pilot Colab notebooks and their outputs. **The reusable method code lives in
[`../src/nbs_ruralscan/`](../src/nbs_ruralscan/)** — schema loader, data loaders,
document ingestion, and the evidence → synthesis → recipe engine. A pilot notebook is
a thin driver that imports that package, runs one NbS × AOI, writes outputs, and
renders maps + tables inline. **Notebooks are the contracted deliverable.**

> **Architecture note (June 2026).** The standalone **GEE App is dropped**. The method runs
> as a Python package that pulls GEE (and other) data and computes with **xarray / rioxarray**;
> GEE data and server-side processing are reached through **xee** (Earth Engine ↔ xarray)
> rather than a native Earth Engine app or script. The engine moved from `pipeline/` to
> `src/nbs_ruralscan/`; and the **TTL wireframe** (`docs/wireframe.html`) is the visual
> demonstrator. See `../CLAUDE.md` and `../methodology/T4_generation_method.md`.

## Structure

| Path | Contents |
|---|---|
| `notebooks/` | Per-pilot Colab notebooks — one `<nbs>_<iso3>.ipynb`. The contracted deliverable. |
| `outputs/` | Pilot outputs — one folder per `<pilot_id>/`. Large rasters gitignored (or LFS). |

The engine the notebooks call lives in `../src/nbs_ruralscan/`: `schema_loader` (T0–T7
rows for an NbS + AOI), `data_loaders/`, `ingest/` (vectorless doc ingestion),
`evidence` · `synthesis` · `support` · `recipe` (the T4 generation engine), `outputs`.

## Conventions

- **Notebooks are self-contained:** load the recipe from the schema (`schema_loader`), pull data into Python, run the method, write outputs, render maps + tables inline.
- **Reads from schema, never hardcoded.** If a variable list, threshold or weight appears as a Python literal, it belongs in T0–T7 instead.
- **Markdown cells document every step in plain language** so a WB analyst can follow without verbal explanation.
- **Reproducibility** — every run records its config in `outputs/<pilot_id>/run_config.json`: NbS ID, recipe version, schema version, AOI, resolution, date, dataset versions, weights used. (Also freeze the ingestion cache + Source/Evidence registers for the run.)

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

## Delivery artefacts (recap)

| Artefact | Audience | Owner | Contractual? |
|---|---|---|---|
| Colab pilot notebook | WB technical team, future implementers | Brayden · Anastasia · Pete (Claude Code) | **Yes** (Phase 3) |
| TTL wireframe (`docs/wireframe.html`) | demo viewers · WB final presentation | Pete + Claude | No — demonstrator |

*(The GEE App is dropped — see `gee_app/README.md`. Benson is now QA/QC: dataset fitness sign-off, output validation, resolution audit.)*

## Starting points

> **Pilot build is gated (June 2026).** The agroforestry Sierra Leone pilot is **deferred pending World Bank
> use-case definition** (which decisions the TTLs want the tool to inform, AOI granularity, which what-if
> scenarios, which families). Don't start the runtime build until the use-cases are agreed — revisit **early
> July 2026**. The steps below are the build plan for *when it's unblocked*.

1. Wire the **M1 suitability raster pipeline** in `src/nbs_ruralscan/` against the T4 recipe rows (the evidence → recipe engine already produces them).
2. Build the per-dataset **`data_loaders/`** (GEE-catalog + uploaded assets → local arrays). For each variable,
   resolve *which* dataset to use with `nbs_ruralscan.binding.resolve_binding(variable, aoi_contexts)` (BIND
   registry — global default + per-AOI override) before loading, and surface any `needs_upload` prompts to the user.
3. Scaffold the **agroforestry pilot notebook** (`notebooks/agroforestry_sle.ipynb`) as a thin driver over the package.
