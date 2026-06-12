# NbS Rural Scan — Project Memory

> **This is the canonical agent guide** (the cross-tool `AGENTS.md` standard). It is read directly by coding agents, and Claude Code loads it via `CLAUDE.md` → `@AGENTS.md`. **Edit this file, not `CLAUDE.md`.** Keep it tight — under ~200 lines. Anything longer becomes wallpaper.

## What this project is

The Rural NbS Scan is a World Bank-funded methodology and demonstrator (D591, $200k, 6 months) for spatial prioritisation of Nature-based Solutions in rural, agricultural, and forestry landscapes. It supports World Bank Task Team Leaders (TTLs) in scoping where different NbS could be invested in, what their footprint would be, and what TTL priorities (poverty, biodiversity, climate risk, gender equity) those footprints intersect.

**This is a scoping tool, not a feasibility tool.** It does not do detailed ecosystem service modelling, full cost-benefit analysis, or site-level engineering design. Those are downstream of this scoping work and pointed to in Module 6.

## Deliverables (per proposal)

- **Methodology toolkit** — cross-cutting framework + per-NbS recipes
- **Pilot Implementation Report** — applying methodology to 2 LDC pilots
- **Reproducible Jupyter / Colab notebooks** — the contracted delivery format for pilot analyses

Demonstrator-grade artefacts (not contracted but valuable):
- **TTL tool wireframe** — see `docs/wireframe.html`
- ~~GEE App~~ — **deferred** (standalone GEE App dropped; GEE stays central via xee; the wireframe is the demonstrator)
- **Pipeline architecture diagram** — see `docs/pipeline.html`

## Architecture (read this if you do anything in this repo)

### Three layers

- **Framework** — cross-cutting methodology, MCDA engine, standardisation library, schema. NbS-agnostic.
- **Recipe** — per-NbS configuration. One file per NbS. Defines variables, thresholds, weights, subpractice families.
- **Runtime** — reusable Python package (`src/nbs_ruralscan/`) that pulls GEE & other data and computes with xarray, rioxarray, and xee + Colab pilot notebooks. *the GEE App is dropped — see Team decision June 2026.*

### Seven modules

| ID | Module | Owner | Schema tables |
|---|---|---|---|
| M0 | Setup & Scope | Pete | T0, T1, T7 |
| M1 | Suitability → Opportunity Space | Pete (Benson QA) | T1, T4, T7 |
| M2 | Rural Climate Risk (risk to **livelihoods**) | Brayden | T1, T2 |
| M2b | Project Disaster Risk Screen (addendum — risk to the **investment**) | Brayden | T2, T3 |
| M3 | Opportunity Space Characterisation | Pete (Namita content) | T1, T5 |
| M4 | Priority Hotspots (MCDA) | Pete (Benson QA) | T5 |
| M5 | NbS Scorecard & Response | Namita | T3, T6 |
| M6 | Implementation Hand-off | Namita (lead) + MFL team + Pete | T0, T6 |

### Schema (the analytical backbone)

The pipeline reads all analytical rules, datasets, response functions, and weights from the T0–T7 schema tables. **Never hardcode analytical rules in code.** The schema is the methodology made machine-readable. Field-level spec: `schema/spec.md` (v0.3.0); ERD: `docs/erd.html`; architecture: `docs/pipeline.html`.

Schema v0.2 adds an **evidence & configuration layer** upstream of T0–T7 — now materialised under `schema/registers/`: Source Register (SRC), Evidence Register (EV), Variable Ontology (VONT), the Subpractice/Suitability-Family registry (FAM), and the **Dataset Binding registry (BIND)** — making every T3/T4/T6 value traceable (`row → evidence_id → source · tier · page · quote`) and every variable's dataset context-resolvable. How these tables are generated from literature is the **T4 generation method**: `methodology/T4_generation_method.md` (with a worked gold standard in `methodology/examples/`).

**Structure is frozen + machine-validated.** The column set of every table lives in `schema/structure/columns.json` (the manifest) and is enforced by `src/nbs_ruralscan/schema_tools/structure.py` (run `python3 src/nbs_ruralscan/schema_tools/structure.py schema`, also in CI). Structure changes go via the manifest + an issue — never reshape data files silently. Content (most `evidence_ids`) is still being populated; the F1×slope chain is the one fully-evidenced example.

**CSV is the source of truth; JSON is generated.** Each schema table is a CSV (edit this) plus a typed JSON the code reads. **Never edit the JSON by hand** — run `python3 src/nbs_ruralscan/schema_tools/generate.py schema` after editing any CSV (CI fails on stale JSON). Generator: `src/nbs_ruralscan/schema_tools/generate.py`.

## What is locked

These decisions are structural. If you want to change them, raise an issue and tag the team — don't just edit.

- **Wireframe** tabs (v0.7), in order: Setup → Opportunity Space → Project Risk → Priority Hotspots → NbS Comparison → Next Steps, plus Danger Zone and an internal Dev Notes tab. Variable Config lives as a sub-tab under Setup, with two surfaces (Suitability variables · Priority/hotspot variables). *(Tab-set ratification still pending — see backlog.)*
- **Variable Card** has six slots: What / Why (NbS-specific) / How to read / What it represents (cluster) / Where it comes from / Response preview (membership curve + raw-vs-transformed maps).
- **T0–T7 colour scheme** matches the ERD. Visual consistency across artefacts.
- **Climate risk Mode A** (Hazard × Exposure) is the pilot default. Mode B is full IPCC AR6 — selectable but not default. Vulnerability variables also appear in M3/M4; using them in Mode B + M4 double-counts.
- **Two risk lenses are distinct**: risk to rural **livelihoods** (M2, a *need* layer → hotspots) vs risk to the **investment** (M2b, the WB disaster-screening lens → a feasibility filter/scope). Kept separate; M2b applied as a filter, never summed. See `methodology/modules/M2b_project_risk.md`.
- **Pipeline reads from schema** — analytical rules never hardcoded.
- **Variable selection is 2-stage**: thematic grouping (per recipe) + correlation clustering (per AOI). One representative per cluster enters MCDA. Cluster membership preserved and shown to users.
- **Dataset sourcing is 3-tier**: GEE catalog → community-hosted → upload. Fitness-for-purpose precedes platform. Data is **pulled into Python** for computation (xarray, rioxarray); GEE data and its server-side processing are reached through **xee** (Earth Engine ↔ xarray) rather than a native Earth Engine app or script. **Within the tiers, prefer server-side hosting (GEE catalog → community GEE → other large STAC/AWS-Open-Data services) over flat-file download** so resample/crop/mosaic happens server-side before transfer and the download functions stay simple and consistent. Where a fitness-equivalent GEE-hosted version exists, take it.
- **Suitability is reasoned per *suitability family*, not per whole NbS.** Families group subpractices by their **shared dominant limiting factor** (agroforestry F1 planted silvoarable · F2 regeneration-based · F3 silvopastoral · F4 linear · F5 shaded perennial-crop). T4 keys to `suitability_family_id`. Grouping carries a documented rationale; don't lump by appearance. **Scheme drafted for sign-off in `methodology/families/agroforestry.md`** *(pending Namita + MFL review)*. F5's understorey crop is a **parameter, not a sub-family** (run per crop, max + retain driver).
- **Every family carries a `spatial_product_type`** (`area_suitability` | `applicability_zone` | `zonal_linear` | `qualitative_only`). Linear/point practices are **not** reported as pixel area (over-estimation grows with coarseness). Run coarseness is also bounded **per variable** by `min_meaningful_resolution_m` (slope ≈ 30–90 m); scale-dependent derivatives are **derive-then-aggregate**, never resample-then-derive.
- **Evidence-first / provenance.** Analytical values in T3/T4/T6 trace to evidence units (source · tier · page · quote). Never PDF → threshold in one step. `claim_scope` separates **species/crop-specific** claims from **practice/technology** ones — species envelopes never define a practice row. See `methodology/T4_generation_method.md`.
- **Constrain by observed distribution, not a modelled niche, where data exist.** Where a family is gated by an existing host system (a crop, land use, grazing), use the host's observed distribution/production (MapSPAM, EO maps, ag-stats) as the gating layer; niche/envelope modelling is the fallback. Method §2.5.
- **Context-aware datasets (BIND) + most-specific-context-wins.** A global recipe binds each variable to a default dataset; country/AEZ/region overrides refine it (`requires_upload` flags a better local dataset for the user to supply). Resolver: `src/nbs_ruralscan/runtime/binding.py`. Relationship *params* refine in parallel via `T4.context_overrides`.
- **Flag sensitive variables, don't resolve them.** `VONT.context_sensitivity` (`low`/`medium`/`high`) marks nationally-derived / sovereignty-sensitive variables (population, poverty, production) so the scoping output recommends a country-endorsed source. **Scoping flags; feasibility validates** — the tool does not negotiate or validate national data (the scope line). Method §2.6, M6.
- **Implementation pathway is bifurcated.** Minimum commitment is the **Colab notebook** worked example per pilot (the contract deliverable). In parallel, the **Claude-Code-built front/back end** is explored against the same schema (wireframe = front-end demonstrator; backend reads SRC/EV/VONT/FAM/BIND + T0–T7). Both consumers read the same registers — schema stability matters more now (two consumers, not one).
- **`suitability_dimension` — three dimensions, ordered by what does the limiting** (v0.3.0 sharpening): `biophysical_constraint` = natural envelope (climate · terrain · soils — can the NbS establish at all); `system_constraint` = existing land-use / farming / land-cover system the NbS must integrate with (where "constrain by observed distribution" lives); `operational_constraint` = implementation feasibility / enabling environment (road & market access, extension, tenure, legal/protected exclusions — typically the scenario levers). Field-level definitions in `schema/spec.md`; method-side framing in `methodology/T4_generation_method.md` §2.7.
- **Hard vs soft operational constraints** (resolves the schema ↔ stocktake Fig 9 tension): **hard exclusions** (legal protected areas, water bodies, urban footprints) stay inside the opportunity space as T4 constraints (`is_scenario_candidate = false`); **soft, investment-addressable** factors (road access, market access, extension, tenure) are **scenario levers** + inputs to an **operational-risk filter on the M2b side** — not baked into the core opportunity surface. Reconciles biophysical + system + hard-operational ≈ opportunity space; soft-operational ≈ scenario levers + project-risk stream.
- **Bounded, authority-weighted discovery seed-set per NbS** (T4 method §3): WB rural-NbS catalogue · GEF / NBS Invest · IPCC · FAO · WRI · major meta-analyses · MEL/MELIA reports · CSA adoption & barriers dataset. Don't sweep 100k abstracts. Tie selection to `SRC.benchmark_tier`. **Corpus differs per table** — sequence T6/T3 discovery after T4. Read each paper once: extract T3/T4/T5/T6 variables in a single pass.
- **Adoption / dis-adoption + MEL/MELIA are observed-reality evidence**, not a separate stream (v0.3.0). They extend "constrain by observed distribution" to the human-system side and feed `system_constraint` / `operational_constraint` T4 variables + T6 conditionality. Ingest via the per-paper sweep with `SRC.method_type = adoption_study` / `mel_report` (added in v0.3.0).
- **Screening SOP + six-axis credibility rubric** (v0.3.0, T4 method §3): five-step funnel (frame → source-type triage → relevance → six-axis credibility → saturation stop, cap ~10–20 sources per NbS × table). Diamond source classes — **WOCAT** (SLM technologies DB, LMIC-grounded), **Evidence Gap Maps** (3ie/Campbell/CEE), **WB project evidence** (PADs, ICRs, IEG) + TORs-named tools (D4R, AAAA, MapAWD), **ICRAF/TECA** practice DBs (excluding crop-specific Ecocrop models for general practices). Six axes: evidence strength (validated models/performance metrics upweighted; unvalidated caps at Med/Low) · methodological transparency · authority & venue (`venue_type`) · context/transferability (`study_income_group`, LMIC tie-break) · recency (offset by `is_seminal`) · seminality — minus an independence/COI discount. The C/I/D rubric is one summary view of the six. Both produce `benchmark_tier`.
- **Reproducible discovery log** (v0.2.7) — per NbS × table, PRISMA-lite markdown under `methodology/discovery_logs/<nbs>_<table>.md`: date, search strings, sources queried, counts at each funnel stage (returned → screened → included). Not a schema register at this phase — narrative audit trail.
- **T5 ratification (v0.3.0)** — 5 themes: `climate_hazard` · `nbs_response` · `people_production` · `equity_inclusion` · `context` (renamed from `equity_gender`; dropped `infrastructure`). `T5.mcda_role` = `priority` | `descriptor`; **T6 effect rows link only to `priority` rows**. 16 rows: 12 priorities + 4 descriptors (added `iplc_lands` under `equity_inclusion`). Spatial-grain rule (≥admin1 for MCDA differentiation; admin0 → qualified flag) derived from `T1.grain_type` + `T1.admin_level`. Proximate-over-distal principle. Companion: `methodology/opportunity_space_T5.md`.
- **Farming-system vocab is EO-derived (v0.3.0)** — 6 T7 classes: `cropping_rainfed` · `cropping_irrigated` · `mixed_crop_livestock` · `agro_pastoral` · `pastoral_rangeland` · `tree_perennial`. Derived at scoping grade from GLAD/WorldCereal · GLW · GMIA · Hansen/MapSPAM. BIND-overridable. Distinct from `aez`. Dixon farming-systems vocabulary = crosswalk only (`schema/registers/FS_DIXON_CROSSWALK.md`).
- **`production_gap`** = shortfall vs attainable productivity of the dominant farming system; metric resolved per farming_system via BIND (yield gap / NPP gap / mixed). Livestock side often `requires_upload`.
- **T6 cost-effectiveness (v0.3.0)** — `economic_indicator_type` extended with `cost_per_beneficiary` · `cost_per_hectare_restored` · `cost_per_tco2e_avoided` · `cost_per_farmer_reached` (indicative, scoping-grade, **not CBA**). `economic_value_range` generalised to `{low, high, unit, source_note}` with `unit` enum-policed.
- **M2b is two-stream (v0.3.0)** — Stream A = asset hazard exposure (T2 × T3 `asset_threat`/`asset_risk_weight`, baseline + future, modulated by T0 `establishment_period_years`). Stream B = operational / enabling environment scenario levers (accessibility · electrification · **tenure incl. IPLC + FPIC/ESS7 safeguard flag** · conflict / fragility (ACLED, WB-FCV) · governance/extension · finance/credit · market/value-chain · labour). **Filter / flag, never summed.** Hard exclusions stay T4 masks. See `methodology/modules/M2b_project_risk.md` §12.

## Inheritance from Benson's existing work

The framework primitives below come from Benson's water-harvesting recipe and v2 methodology plan. Treat them as canonical. Cite their origin in diagrams and docs.

| Primitive | Origin |
|---|---|
| 5 fuzzy membership functions (sigmoid, linear, Gaussian, bell, inverted sigmoid) | v2 plan §4 |
| Hybrid AHP + CRITIC + Entropy weighting (α-reconciled) | v2 plan §7 |
| Reference MCDA implementation | `reference/R/spatMCDA.R` |
| Recipe template column structure | water-harvesting recipe §2.2 |
| Subpractice family pattern | water-harvesting recipe §1 |

## File map

- `docs/` — GitHub Pages site (wireframe, pipeline diagram, index, schema page + ERD)
- `methodology/` — framework + per-NbS recipes + module specs + **`T4_generation_method.md`** (evidence-first suitability generation) + **`families/`** (suitability-family schemes) + `examples/` (worked gold standards)
- `schema/` — `spec.md` (v0.3.0 field-level), T0–T7 tables, `registers/` (SRC·EV·VONT·FAM·BIND), `structure/columns.json` (frozen column manifest), ERD/dedup notes, draft-0 example recipes
- `src/nbs_ruralscan/` — reusable Python implementation, grouped by what code acts on: `schema_tools/` (`structure` validator · `generate` CSV→JSON · `freeze` snapshots), `recipe/` (the evidence engine: `evidence`→`support`→`synthesis`→`family`), `runtime/` (`mcda` · `binding` resolver · `farming_system`; `schema_loader`/`outputs` to be authored), `ingest/` (doc ingestion), `data_loaders/` (geospatial loaders), `models` (shared types). Subpackage map in `__init__.py`.
- `tests/` — pytest suite (run via `uv run pytest`)
- `pipeline/` — pilot notebooks and outputs
- `reference/` — stocktake findings, source R script, lit references
- `.claude/commands/` — custom slash commands
- `.github/workflows/ci.yml` — CI: ruff · ty · pytest · schema structure validation
- `.github/ISSUE_TEMPLATE/` — issue templates by type
- `PLAYBOOK.md` — team workflows

## Run / preview / deploy

- **Python environment**: use `uv` from the repo root. Add runtime dependencies with `uv add ...`; add dev tools with `uv add --dev ...`.
- **Edited a schema CSV?** Regenerate its JSON: `python3 src/nbs_ruralscan/schema_tools/generate.py schema` (CSV is source of truth; CI fails on stale JSON).
- **Python checks**: run `uv run ruff check .`, `uv run ruff format .`, `uv run ty check`, `uv run pytest`, `python3 src/nbs_ruralscan/schema_tools/generate.py schema --check`, and `python3 src/nbs_ruralscan/schema_tools/structure.py schema` before PRs that touch `src/` or `schema/`. CI (`.github/workflows/ci.yml`) runs the same gates.
- **Preview docs locally**: `cd docs && python3 -m http.server 8000` → http://localhost:8000
- **Run pilot notebook**: open `pipeline/notebooks/<nbs>_<country>.ipynb` in Colab; authenticate GEE
- **Deploy docs**: push to main; GitHub Pages auto-rebuilds from `/docs` within ~2 min
- **Live site**: https://ciat.github.io/nbs_ruralscan/

## Team & roles

- **Pete Steward** (Team Lead) — framework integrity, wireframe direction, scope-control; **operational lead on M1 (suitability), M3 (opportunity-space characterisation), M4 (hotspotting/MCDA)**. Leads recipe/spec authoring.
- **Benson Kenduiywo** (Geospatial Analytics) — **QA/QC**: dataset fitness sign-off, output validation, resolution-audit review. *(The framework primitives below remain his inherited work and stay attributed to him.)* Pipeline implementation now proceeds in Python via Claude Code, driven by Brayden / Anastasia / Pete.
- **Namita Joshi** (Coordination + lit) — **Task H focus ([expert-opinion elicitation & integration protocol](file:///Users/pstewarda/Documents/rprojects/nbs_ruralscan/methodology/expert_opinion_protocol.md))**, lead on **M6 (Implementation Hand-off)**, project coordination.
- **Brayden Youngberg** (Co-lead — methodology) — **M2 climate-risk + M2b project-disaster-risk index formulation; dataset download layer from T1 + analytical-context construction from T7** (server-side preferred — GEE / STAC / large services).
- **Aniruddha Ghosh** — variable parsimony + transparency principles; Claude Code patterns
- **Sarah Jones, Chris Kettle, Evert Thomas, Hannes Gaisberger** (MFL team) — ecosystem services, M6 implementation hand-off content, agroforestry & forest restoration domain input
- **Lolita Müller** — stocktake methods, literature pipelines
- **Anastasia Wahome** — geospatial implementation support

## Style & conventions

- Use Conventional Commits where possible (`feat:`, `fix:`, `docs:`, `chore:`)
- One PR per logical change; don't bundle wireframe edits with methodology edits
- Variables, dataset IDs: `snake_case`
- NbS IDs: `snake_case` (e.g. `agroforestry`, `water_harvesting`)
- Files: kebab-case for `docs/` artefacts (`wireframe.html`, `pipeline.html`); snake_case for code
- Per-NbS recipe filenames: `methodology/recipes/<nbs_id>.md`
- **Replication for Synthesis**: Do not skip extracting similar thresholds across papers to avoid "redundant entries." The synthesis engine counts the number of unique sources (`n_sources`) to calculate consensus weights and median bounds. Every distinct literature threshold must have its own `EvidenceUnit` in `EV_evidence_register.json`.
- **Source-Evidence Variable Agreement**: The `vars_extracted` list for each paper in `SRC_source_register.json` must exactly match the variables that have actual evidence rows in `EV_evidence_register.json` (excluding baseline map/mask layers). Run the discrepancy script to align them.
- **Full-Variable Sweeps**: When sweeping a source, extract all suitability parameters, enablers, and costs mapping to any variable in the target recipe (including `soil_texture`, `soil_drainage`, `distance_to_road`, and `tree_canopy_cover`), not just the core five biophysical variables.
- If using/directly importing a python module, check that it is included in `pyproject.toml` and use `uv add <module_name>` if missing.

## Don't

- Don't hardcode analytical rules in pipeline code; read from schema
- Don't merge wireframe edits without preserving the agreed tab structure (see "What is locked") and the six Variable-Card slots
- Don't expand variables into MCDA without correlation reduction
- Don't add an NbS to a cluster without checking it shares the biophysical logic (water harvesting ≠ wetland creation; we caught this once already)
- Don't promise the World Bank a polished web tool — the proposal commits to notebooks; the App and wireframe are demonstrators
- Don't pick a flat-file dataset when a fitness-equivalent GEE-hosted (or other server-side) version exists — server-side resample/crop is the default.
- Don't break the EvidenceUnit shape when adding expert-evidence capture — expert claims must land in the same EV rows as literature, via `evidence_type=expert`; only patch the schema if EV literally cannot represent something Namita needs.
- Don't let `SRC.vars_extracted` diverge from actual `EV_evidence_register.json` variable listings.
- Don't skip secondary suitability variables (like soil texture/drainage or distance to road) when they are quantified in paper texts.

## When in doubt

- Read `PLAYBOOK.md` for workflows
- Read the most recent `5_Meetings/` transcript for current discussion state
- Read the closest AGENTS.md/CLAUDE.md to where you're working (subfolder memory takes precedence)
- Ask in the Teams `NbS Rural Scan Task Force` channel
