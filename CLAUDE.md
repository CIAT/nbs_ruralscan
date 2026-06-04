# NbS Rural Scan — Project Memory

> This file is read by Claude Code on every session. Keep it tight — under ~200 lines. Anything longer becomes wallpaper.

## What this project is

The Rural NbS Scan is a World Bank-funded methodology and demonstrator (D591, $200k, 6 months) for spatial prioritisation of Nature-based Solutions in rural, agricultural, and forestry landscapes. It supports World Bank Task Team Leaders (TTLs) in scoping where different NbS could be invested in, what their footprint would be, and what TTL priorities (poverty, biodiversity, climate risk, gender equity) those footprints intersect.

**This is a scoping tool, not a feasibility tool.** It does not do detailed ecosystem service modelling, full cost-benefit analysis, or site-level engineering design. Those are downstream of this scoping work and pointed to in Module 6.

## Deliverables (per proposal)

- **Methodology toolkit** — cross-cutting framework + per-NbS recipes
- **Pilot Implementation Report** — applying methodology to 2 LDC pilots
- **Reproducible Jupyter / Colab notebooks** — the contracted delivery format for pilot analyses

Demonstrator-grade artefacts (not contracted but valuable):
- **TTL tool wireframe** — see `docs/wireframe.html`
- ~~GEE App~~ — **deferred** (native GEE dropped; the wireframe is the demonstrator)
- **Pipeline architecture diagram** — see `docs/pipeline.html`

## Architecture (read this if you do anything in this repo)

### Three layers

- **Framework** — cross-cutting methodology, MCDA engine, standardisation library, schema. NbS-agnostic.
- **Recipe** — per-NbS configuration. One file per NbS. Defines variables, thresholds, weights, subpractice families.
- **Runtime** — reusable Python package (`src/nbs_ruralscan/`) that pulls GEE & other data and computes locally with numpy/rasterio + Colab pilot notebooks. *Native server-side GEE compute and the GEE App are dropped — see Team decision June 2026.*

### Seven modules

| ID | Module | Owner | Schema tables |
|---|---|---|---|
| M0 | Setup & Scope | Pete | T0, T1, T7 |
| M1 | Suitability → Opportunity Space | Benson + Namita | T1, T4, T7 |
| M2 | Rural Climate Risk (risk to **livelihoods**) | Brayden | T1, T2 |
| M2b | Project Disaster Risk Screen (addendum — risk to the **investment**) | Brayden + Pete | T2, T3 |
| M3 | Opportunity Space Characterisation | Namita + Benson | T1, T5 |
| M4 | Priority Hotspots (MCDA) | Benson | T5 |
| M5 | NbS Scorecard & Response | Namita | T3, T6 |
| M6 | Implementation Hand-off | MFL team + Pete + Namita | T0, T6 |

### Schema (the analytical backbone)

The pipeline reads all analytical rules, datasets, response functions, and weights from the T0–T7 schema tables. **Never hardcode analytical rules in code.** The schema is the methodology made machine-readable. Field-level spec: `schema/spec.md` (v0.2.2); ERD: `docs/erd.html`; architecture: `docs/pipeline.html`.

Schema v0.2 adds an **evidence & configuration layer** upstream of T0–T7 — now materialised under `schema/registers/`: Source Register (SRC), Evidence Register (EV), Variable Ontology (VONT), the Subpractice/Suitability-Family registry (FAM), and the **Dataset Binding registry (BIND)** — making every T3/T4/T6 value traceable (`row → evidence_id → source · tier · page · quote`) and every variable's dataset context-resolvable. How these tables are generated from literature is the **T4 generation method**: `methodology/T4_generation_method.md` (with a worked gold standard in `methodology/examples/`).

**Structure is frozen + machine-validated.** The column set of every table lives in `schema/structure/columns.json` (the manifest) and is enforced by `src/nbs_ruralscan/structure.py` (run `python3 src/nbs_ruralscan/structure.py schema`, also in CI). Structure changes go via the manifest + an issue — never reshape data files silently. Content (most `evidence_ids`) is still being populated; the F1×slope chain is the one fully-evidenced example.

## What is locked

These decisions are structural. If you want to change them, raise an issue and tag the team — don't just edit.

- **Wireframe** tabs (v0.6), in order: Setup → Opportunity Space → Project Risk → Priority Hotspots → NbS Comparison → Next Steps, plus Danger Zone and an internal Dev Notes tab. Variable Config now lives as a sub-tab under Setup, with two surfaces (Suitability variables · Priority/hotspot variables). *(Tab-set ratification still pending — see backlog.)*
- **Variable Card** has six slots: What / Why (NbS-specific) / How to read / What it represents (cluster) / Where it comes from / Response preview (membership curve + raw-vs-transformed maps).
- **T0–T7 colour scheme** matches the ERD. Visual consistency across artefacts.
- **Climate risk Mode A** (Hazard × Exposure) is the pilot default. Mode B is full IPCC AR6 — selectable but not default. Vulnerability variables also appear in M3/M4; using them in Mode B + M4 double-counts.
- **Two risk lenses are distinct**: risk to rural **livelihoods** (M2, a *need* layer → hotspots) vs risk to the **investment** (M2b, the WB disaster-screening lens → a feasibility filter/scope). Kept separate; M2b applied as a filter, never summed. See `methodology/modules/M2b_project_risk.md`.
- **Pipeline reads from schema** — analytical rules never hardcoded.
- **Variable selection is 2-stage**: thematic grouping (per recipe) + correlation clustering (per AOI). One representative per cluster enters MCDA. Cluster membership preserved and shown to users.
- **Dataset sourcing is 3-tier**: GEE catalog → community-hosted → upload. Fitness-for-purpose precedes platform. Data is **pulled into Python** for computation (numpy/rasterio) — there is no native server-side GEE pipeline.
- **Suitability is reasoned per *suitability family*, not per whole NbS.** Families group subpractices by their **shared dominant limiting factor** (agroforestry F1 planted silvoarable · F2 regeneration-based · F3 silvopastoral · F4 linear · F5 shaded perennial-crop). T4 keys to `suitability_family_id`. Grouping carries a documented rationale; don't lump by appearance. **Scheme drafted for sign-off in `methodology/families/agroforestry.md`** *(pending Namita + MFL review)*. F5's understorey crop is a **parameter, not a sub-family** (run per crop, max + retain driver).
- **Every family carries a `spatial_product_type`** (`area_suitability` | `applicability_zone` | `zonal_linear` | `qualitative_only`). Linear/point practices are **not** reported as pixel area (over-estimation grows with coarseness). Run coarseness is also bounded **per variable** by `min_meaningful_resolution_m` (slope ≈ 30–90 m); scale-dependent derivatives are **derive-then-aggregate**, never resample-then-derive.
- **Evidence-first / provenance.** Analytical values in T3/T4/T6 trace to evidence units (source · tier · page · quote). Never PDF → threshold in one step. `claim_scope` separates **species/crop-specific** claims from **practice/technology** ones — species envelopes never define a practice row. See `methodology/T4_generation_method.md`.
- **Constrain by observed distribution, not a modelled niche, where data exist.** Where a family is gated by an existing host system (a crop, land use, grazing), use the host's observed distribution/production (MapSPAM, EO maps, ag-stats) as the gating layer; niche/envelope modelling is the fallback. Method §2.5.
- **Context-aware datasets (BIND) + most-specific-context-wins.** A global recipe binds each variable to a default dataset; country/AEZ/region overrides refine it (`requires_upload` flags a better local dataset for the user to supply). Resolver: `src/nbs_ruralscan/binding.py`. Relationship *params* refine in parallel via `T4.context_overrides`.
- **Flag sensitive variables, don't resolve them.** `VONT.context_sensitivity` (`low`/`medium`/`high`) marks nationally-derived / sovereignty-sensitive variables (population, poverty, production) so the scoping output recommends a country-endorsed source. **Scoping flags; feasibility validates** — the tool does not negotiate or validate national data (the scope line). Method §2.6, M6.

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
- `schema/` — `spec.md` (v0.2.2 field-level), T0–T7 tables, `registers/` (SRC·EV·VONT·FAM·BIND), `structure/columns.json` (frozen column manifest), ERD/dedup notes, draft-0 example recipes
- `src/nbs_ruralscan/` — reusable Python implementation: `ingest/` (doc ingestion), `evidence`·`synthesis`·`support`·`recipe` (T4 engine), `binding` (BIND resolver), `structure` (schema validator)
- `tests/` — pytest suite (run via `uv run pytest`)
- `pipeline/` — pilot notebooks and outputs
- `reference/` — stocktake findings, source R script, lit references
- `.claude/commands/` — custom slash commands
- `.github/workflows/ci.yml` — CI: ruff · ty · pytest · schema structure validation
- `.github/ISSUE_TEMPLATE/` — issue templates by type
- `PLAYBOOK.md` — team workflows

## Run / preview / deploy

- **Python environment**: use `uv` from the repo root. Add runtime dependencies with `uv add ...`; add dev tools with `uv add --dev ...`.
- **Python checks**: run `uv run ruff check .`, `uv run ruff format .`, `uv run ty check`, `uv run pytest`, and `python3 src/nbs_ruralscan/structure.py schema` before PRs that touch `src/` or `schema/`. CI (`.github/workflows/ci.yml`) runs the same gates.
- **Preview docs locally**: `cd docs && python3 -m http.server 8000` → http://localhost:8000
- **Run pilot notebook**: open `pipeline/notebooks/<nbs>_<country>.ipynb` in Colab; authenticate GEE
- **Deploy docs**: push to main; GitHub Pages auto-rebuilds from `/docs` within ~2 min
- **Live site**: https://ciat.github.io/nbs_ruralscan/

## Team & roles

- **Pete Steward** (Team Lead) — framework integrity, wireframe direction, scope-control
- **Benson Kenduiywo** (Geospatial Analytics) — **transitioning to QA/QC**: dataset fitness sign-off, output validation, resolution-audit review. *(The framework primitives below remain his inherited work and stay attributed to him.)* Pipeline implementation now proceeds in Python via Claude Code, driven by Brayden / Anastasia / Pete.
- **Namita Joshi** (Coordination + lit) — Variable Cards, recipe content, NbS scorecards (T6), project coordination
- **Brayden Youngberg** (Co-lead — methodology) — M2 climate risk methods; front-end help where capacity allows
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

## Don't

- Don't hardcode analytical rules in pipeline code; read from schema
- Don't merge wireframe edits without preserving the agreed tab structure (see "What is locked") and the six Variable-Card slots
- Don't expand variables into MCDA without correlation reduction
- Don't add an NbS to a cluster without checking it shares the biophysical logic (water harvesting ≠ wetland creation; we caught this once already)
- Don't promise the World Bank a polished web tool — the proposal commits to notebooks; the App and wireframe are demonstrators

## When in doubt

- Read `PLAYBOOK.md` for workflows
- Read the most recent `5_Meetings/` transcript for current discussion state
- Read the closest CLAUDE.md to where you're working (subfolder CLAUDE.md takes precedence)
- Ask in the Teams `NbS Rural Scan Task Force` channel
