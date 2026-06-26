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
- **Acquisition & cataloguing (locked).** Evidence the AI discovers must be acquirable by the whole team, not only on the discoverer's laptop. **PDFs** → upload to the SharePoint library (`…/2_Technical_&_Data/library/<NbS>/`) and set `SRC.library_path` (the QA/QC dashboard builds the team-openable SharePoint link from it); also cache `.cache/corpus/<sid>.pdf` for the guardrail. **Websites / GitHub** → set `SRC.url` + save a snapshot (`.txt`/`.html`/`.md`) in `.cache/corpus/`, and give every EV row a **locator** (`locator_type` + `locator` = *where on the page*: section / anchor / selector / `file:line`). **A format with no handling rule → PAUSE**: define the acquire adapter + locator semantics + a QA/QC rule before registering anything from it — don't improvise. `validate_sources.py` audits all three (missing `library_path` / `url` / locator = non-fatal notes; an unknown `.cache/corpus` extension = hard fail).
- **Constrain by observed distribution, not a modelled niche, where data exist.** Where a family is gated by an existing host system (a crop, land use, grazing), use the host's observed distribution/production (MapSPAM, EO maps, ag-stats) as the gating layer; niche/envelope modelling is the fallback. Method §2.5.
- **Context-aware datasets (BIND) + most-specific-context-wins.** A global recipe binds each variable to a default dataset; country/AEZ/region overrides refine it (`requires_upload` flags a better local dataset for the user to supply). Resolver: `src/nbs_ruralscan/runtime/binding.py`. Relationship *params* refine in parallel via `T4.context_overrides`.
- **Flag sensitive variables, don't resolve them.** `VONT.context_sensitivity` (`low`/`medium`/`high`) marks nationally-derived / sovereignty-sensitive variables (population, poverty, production) so the scoping output recommends a country-endorsed source. **Scoping flags; feasibility validates** — the tool does not negotiate or validate national data (the scope line). Method §2.6, M6.
- **Implementation pathway is bifurcated.** Minimum commitment is the **Colab notebook** worked example per pilot (the contract deliverable). In parallel, the **Claude-Code-built front/back end** is explored against the same schema (wireframe = front-end demonstrator; backend reads SRC/EV/VONT/FAM/BIND + T0–T7). Both consumers read the same registers — schema stability matters more now (two consumers, not one).
- **`suitability_dimension` — three dimensions, ordered by what does the limiting** (v0.3.0 sharpening): `biophysical_constraint` = natural envelope (climate · terrain · soils — can the NbS establish at all); `system_constraint` = existing land-use / farming / land-cover system the NbS must integrate with (where "constrain by observed distribution" lives); `operational_constraint` = implementation feasibility / enabling environment (road & market access, extension, tenure, legal/protected exclusions — typically the scenario levers). Field-level definitions in `schema/spec.md`; method-side framing in `methodology/T4_generation_method.md` §2.7.
- **Hard vs soft operational constraints** (resolves the schema ↔ stocktake Fig 9 tension): **hard exclusions** (legal protected areas, water bodies, urban footprints) stay inside the opportunity space as T4 constraints (`is_scenario_candidate = false`); **soft, investment-addressable** factors (road access, market access, extension, tenure) are **scenario levers** + inputs to an **operational-risk filter on the M2b side** — not baked into the core opportunity surface. Reconciles biophysical + system + hard-operational ≈ opportunity space; soft-operational ≈ scenario levers + project-risk stream.
- **Enabling-environment variables — re-ratified routing (2026-06-23, SUPERSEDES 2026-06-22).** `distance_to_road` · `accessibility_travel_time`/`market_access` · `market_value_chain` · `tenure_security` · `extension_governance` · `finance_credit_access` · `labour_availability` (+ FMNR `rootstock_presence`, governance) are **soft, investment-addressable** factors → they do **NOT** belong in **T4 structural suitability**. Route them to the **M2b Stream-B operational-risk filter** + **Module-6 next-steps / implementation guidance**. **Their evidence MUST NOT be extracted as `use_role = structural_suitability`** — that is the `wrong_table` QA defect. **Only hard exclusions** (legal protected areas, water bodies, urban footprints) stay in T4, as masks (`is_scenario_candidate = false`). The recurring reviewer question *"is this T4 or T3?"* → **soft enabling-env = T3/M2b/next-steps; T4 only for hard legal masks.** *Why the reversal:* the 2026-06-22 "T4 `operational_constraint` scenario lever" routing **contradicted the older 'Hard vs soft operational constraints' lock above** (soft = "not baked into the core opportunity surface") and drove ~13 QA flags on 2026-06-23 (reviewers repeatedly asking "is this T4 or T3?"). This re-ratification aligns the two. **M2b home implemented (2026-06-23):** soft enabling-env evidence carries **`use_role = operational_risk`** (new enum member). `synthesise_family` still emits these as recipe rows (flagged `suitability_dimension = operational_constraint`) but `family.py` keeps them **out of the T4 MCDA support/selection surface** — so they're catalogued + traceable without setting the suitability base. 48 enabling-env EV rows retagged on 2026-06-23. Extract these as `use_role = operational_risk` (NOT `structural_suitability`); `wrong_table` flags strays. *(The agroforestry T4-recipe scenario rows still live in `T4_suitability_mappings.csv`, flagged operational_constraint — a future split into a dedicated M2b table remains optional.)*
- **Bounded, authority-weighted discovery seed-set per NbS** (T4 method §3): WB rural-NbS catalogue · GEF / NBS Invest · IPCC · FAO · WRI · major meta-analyses · MEL/MELIA reports · CSA adoption & barriers dataset. Don't sweep 100k abstracts. Tie selection to `SRC.benchmark_tier`. **Corpus differs per table** — sequence T6/T3 discovery after T4. Read each paper once: extract T3/T4/T5/T6 variables in a single pass.
- **Adoption / dis-adoption + MEL/MELIA are observed-reality evidence**, not a separate stream (v0.3.0). They extend "constrain by observed distribution" to the human-system side and feed `system_constraint` / `operational_constraint` T4 variables + T6 conditionality. Ingest via the per-paper sweep with `SRC.method_type = adoption_study` / `mel_report` (added in v0.3.0).
- **Screening SOP + six-axis credibility rubric** (v0.3.0, T4 method §3): five-step funnel (frame → source-type triage → relevance → six-axis credibility → saturation stop, cap ~10–20 sources per NbS × table). Diamond source classes — **WOCAT** (SLM technologies DB, LMIC-grounded), **Evidence Gap Maps** (3ie/Campbell/CEE), **WB project evidence** (PADs, ICRs, IEG) + TORs-named tools (D4R, AAAA, MapAWD), **ICRAF/TECA** practice DBs (excluding crop-specific Ecocrop models for general practices). Six axes: evidence strength (validated models/performance metrics upweighted; unvalidated caps at Med/Low) · methodological transparency · authority & venue (`venue_type`) · context/transferability (`study_income_group`, LMIC tie-break) · recency (offset by `is_seminal`) · seminality — minus an independence/COI discount. The C/I/D rubric is one summary view of the six. Both produce `benchmark_tier`.
- **Iterative-learning loop (locked process).** After EVERY extraction sweep run the retrospective (`methodology/extraction_retrospective.md`, slash `/sweep-retro`): measure with `schema_tools/sweep_metrics.py` (ledger `pipeline/metrics/sweep_log.csv`), then encode each new defect into the extract-evidence skill's catalogue + a deterministic check (`check_numbers.py` for smuggled numbers; `check_scope.py` for off-scope T4 extraction — the dominant 2026-06-18 defect: suitability vars pulled from site-descriptor/methods/carbon-biomass sections; `check_quote.py` for too-narrow quotes — isolated table cells lacking the threshold sentence + header). `numberprov_rate_pct`, `verify_rate_pct`, and the `off_scope` rate must trend DOWN sweep-over-sweep; if not, tighten the spec. **Incorporation is tracked, not claimed:** `schema_tools/learnings.py` holds a cursor (`pipeline/metrics/learnings_log.csv`) of how many `review_log` decisions have been turned into adjustments; `generate.py` prints a build note for any unprocessed review feedback until `learnings.record` advances it. This is how the pipeline gets measurably better each round.
- **QA/QC review system (locked).** Human review of flagged evidence happens in the dashboard QA/QC tab + a local `schema_tools/review_server.py` (`:8765`, run `uv run python3 -m nbs_ruralscan.schema_tools.review_server`). Modes: **AI-flagged** (open queue, nobody reviewed) · **AI-passed sample** (spot-check false negatives) · **2nd opinion** (resolved by one reviewer, needs another, per-reviewer) · **My reviewed** (applied history) · **Stats** (AI confusion matrix from `review_log.csv`). Decisions key `(evidence_id × reviewer)` in `pipeline/review/decisions.json`; **Apply** = consensus (agree→write register + `review_log`; disagree→conflict pending). Applied decisions are **viewable, re-openable, and challengeable** (a 2nd reviewer's disagreement auto-reopens a conflict). Reason codes incl. `wrong_practice` (mapped to wrong NbS) and `species_envelope` (per-species row ≠ practice rule). Tabular quotes get an on-demand **table screengrab** (`/api/crop`, page-region render from the cached PDF). Full map: memory `project_qaqc_review_system.md`.
- **Soft-delete / quarantine (locked).** A QA `drop` is **never a hard delete** — it sets EV `review_state=dropped`: the row stays as a restorable record, excluded from synthesis (`synthesise_family`), the progress ledger, and dashboard counts (`_segregateDropped`). Reversible via `review.reopen_units` / the dashboard re-open. `ruleset_version` stamps which extraction ruleset a unit was (re-)evaluated under, so re-evals are auditable. Hard-deleting evidence is forbidden; recover any historic hard-delete from git as a `review_state=dropped` row (as done 2026-06-18).
- **Progress ledger (locked, orchestrator-owned + register-enforced).** Project progress lives in `pipeline/progress_ledger.csv`, per (NbS × table × category **× family**), with the lifecycle stages searched · screened · extracted · verified · reviewed (+ `searched_categories` for stock/lit/grey/tools). It is **stamped by the pipeline STEP that did the work** — `schema_tools/ledger.py mark(...)` — never inferred from artifact presence and never hand-claimed. **`family` granularity (2026-06-25):** empty `family` = table-level / all-families search (default); a specific `suitability_family_id` logs a **sub-practice-targeted** search status as source of truth — so "have we searched for FMNR T3?" is answered from the ledger, never inferred from whether evidence happens to exist (**absence of evidence ≠ search not done**). `mark(..., family=...)`; `derive_facts`/`check` reconcile per-family (family='' aggregates). `ledger.check` runs inside `generate.py` + CI and **fails the build** if a claim doesn't reconcile with the register (no `extracted=done` without EV rows; no EV rows for an unstamped stage; `reviewed=done` needs `reviewer_ok`; stage order enforced). After each sweep, the orchestrator updates the ledger as part of the retrospective. The dashboard READS the ledger for stage status (it must not re-infer). You cannot claim progress you can't prove.
- **Reproducible discovery log** (v0.2.7) — per NbS × table, PRISMA-lite markdown under `methodology/discovery_logs/<nbs>_<table>.md`: date, search strings, sources queried, counts at each funnel stage (returned → screened → included). Narrative companion to the structured SRCH register below.
- **Search-protocol register + ruleset versioning (locked, 2026-06-26).** Every discovery search is logged in the **`SRCH` register** (`schema/registers/SRCH_search_register.csv`, manifest-frozen) — one row per **(NbS × sub-practice × table × discovery-process)**: `search_terms` · `screening_steps` (5-step funnel) · `inclusion_criteria` · `limits` · PRISMA counts · `search_date` · `run_id` · **`ruleset_version`**. The **4 discovery processes** = `stock · updated_lit · grey · tool`; each sub-practice × table runs all 4. Log via `schema_tools/search_log.py`. **`ledger.check` FAILS the build if `searched=done` has no matching SRCH row** — no claimed search without its logged protocol (the ledger holds *status*, SRCH holds the *protocol*). The search/extraction **instructions are version-controlled**: `methodology/RULESET_VERSIONS.md` (semver · date · change) + archived prompt snapshots under `.agents/skills/_versions/<version>/`; `SRCH.ruleset_version` + `EV.ruleset_version` pin to it, so any past search is reproducible with its exact instructions. System doc: `methodology/search_protocol.md`. **Existing agroforestry searches backfilled at `family=""` (table-level)** — going forward, log per sub-practice.
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
- **Title-only Multilingual Search**: Formulate disjoined search strings targeting title-only fields (e.g., `display_name.search` in OpenAlex) using AGROVOC synonyms in English, Spanish, French, and Portuguese to avoid full-text search noise.
- **Human-in-the-Loop Triage**: Always validate borderline inclusions/exclusions with a human-in-the-loop review before registration to align on study boundaries (e.g., rejecting urban shade/pure forestry, accepting temperate baselines).
- **Living Database Model**: Maintain the decoupled SRC ➔ EV ➔ Synthesis pipeline. Adding more evidence later is append-only (new source rows, new evidence rows); the synthesis engine dynamically recalculates consensus weights and median bounds.
- **Multilingual Quotes**: Verbatim quotes from non-English sources must be saved in their native language followed by bracketed English translation: `"[Native Text] (English: [Translated Text])"`.
- If using/directly importing a python module, check that it is included in `pyproject.toml` and use `uv add <module_name>` if missing.

## Don't

- Don't use browser subagents or make browser tool calls to verify, interrogate, or toggle controls on local web servers or websites (which consumes 1000+ credits). Instead, just capture a single screenshot if needed, or ask the user to test and verify UI changes manually.
- Don't hardcode analytical rules in pipeline code; read from schema
- Don't merge wireframe edits without preserving the agreed tab structure (see "What is locked") and the six Variable-Card slots
- Don't expand variables into MCDA without correlation reduction
- Don't add an NbS to a cluster without checking it shares the biophysical logic (water harvesting ≠ wetland creation; we caught this once already)
- Don't promise the World Bank a polished web tool — the proposal commits to notebooks; the App and wireframe are demonstrators
- Don't pick a flat-file dataset when a fitness-equivalent GEE-hosted (or other server-side) version exists — server-side resample/crop is the default.
- Don't break the EvidenceUnit shape when adding expert-evidence capture — expert claims must land in the same EV rows as literature, via `evidence_type=expert`; only patch the schema if EV literally cannot represent something Namita needs.
- Don't let `SRC.vars_extracted` diverge from actual `EV_evidence_register.json` variable listings.
- Don't skip secondary suitability variables (like soil texture/drainage or distance to road) when they are quantified in paper texts.
- **Don't hand-author evidence. Ever.** No quote, page, or EvidenceUnit may be typed from memory, an abstract, a search-result snippet, or model knowledge. Every EV row MUST come through the deterministic pipeline (`build_index` → `retrieve`/`package_for_extraction` → emit `EvidenceUnit` from the page-stamped passages → `validate_units` → `save_units`) over a **cached source artifact** in `.cache/corpus/` (PDF, or a saved `.txt`/`.html`/`.md` snapshot for web sources). Appending straight to `EV_*.csv`/`.json` or a recipe `evidence_ids` column is forbidden — that is exactly how the 2026-06 contamination happened (see `schema/registers/_quarantine/`). The guardrail `schema_tools/validate_sources.py` runs inside `generate.py` + CI and fails the build on any quote not found verbatim on its cited page; don't weaken or bypass it. If a source can't be cached (paywalled, dead URL), it can't be registered — leave it out.
- Don't cite a URL/website as evidence without a saved snapshot AND the specific page/section the quote came from. A bare domain link is not provenance.
- Don't register AI-discovered evidence the team can't open: a **PDF** must be uploaded to the SharePoint library with `SRC.library_path` set; a **web/github** source must have `SRC.url` + a cached snapshot + an EV `locator`. Hit a format with no handling rule → **stop and define the rule** (adapter + locator + QA/QC check), don't shoehorn it into an existing one.
- **Tools are sources — interrogate the actual code/docs, by default.** A tool/method/codebase is **evidence-reviewed like any other source**: its hardcoded thresholds, default weights, criteria, and exclusion rules are **EV claims** → extract them (`source_category=tool` SRC row + `TOOL` metadata row + EV rows, linked via `evidence_ids`). **Do not register/evidence a tool from its README, landing page, or abstract alone** — that shallow pass misses the real content (caught 2026-06-21: a README gave only prose criteria while the GEE scripts hardcode per-practice weights). **Default = dig into the repository's source files** (analysis scripts, app code, parameter blocks). Provenance is **file-level**: `locator_type=file_line` + `commit_sha` (immutable pin) + `locator="path:Lstart-Lend"`, so the dashboard deep-links to exact lines. **Ignore off-scope/species-specific files** (per-species tree-growth scripts are species envelopes, not practice rules — `claim_scope`). A tool's hardcoded parameter is a design choice, not a measured finding → `claim_basis=expert_assertion`, weighted down in synthesis. Skip only genuinely data-driven engines that hardcode nothing (`spatMCDA.R` computes weights at runtime → no extractable claim). **Automated:** `ingest/github.py` (`python -m nbs_ruralscan.ingest.github <owner/repo> <commit> --subdir …`) acquires repo files at a pinned commit (commit-stamped `.cache/corpus` + `.meta.json`; ignore-list skips species scripts) and **scans for candidate parameter lines** (weights/thresholds/masks/buffers/reclassify) with `file:line` — only the variable→family **emission** is judged by hand, then the central guardrail verifies. Don't hand-`gh api`+grep tool repos any more.
- **PICOS — the NbS practice must be EVIDENCED in the source, never inferred.** The Intervention (the NbS practice/sub-practice) has to appear explicitly in the literature text or tool/repo description before you tag `nbs_id` / `suitability_family_id` / `TOOL.nbs_ids`. A **demo dataset, worked example, file title, or the sweep's current focus is NOT evidence of association**: a generic MCDA engine that ships an agroforestry example is not an agroforestry tool (`reference/R/spatMCDA.R` is NbS-agnostic — caught 2026-06-21); a paper whose *method* is generic but *case study* is coffee does not make every variable a coffee/agroforestry claim. If the practice isn't stated in the source, leave the NbS field **blank / `cross` / agnostic** — don't borrow it from context. This is the same discipline as `claim_scope` (species ≠ practice) and `wrong_practice` (mapped to wrong NbS), applied to the *source→practice* link itself. Basic PICOS: Population/Intervention must be in the source.
- **Verbatim ≠ faithful.** A real quote does not make the encoded `relationship` numbers or the `variable` label right. ~34-51% of numeric units in the 2026-06 sweep had smuggled/misread numbers. Every number in `relationship` must appear in its quote (`schema_tools/check_numbers.py` flags violations); never read an AHP "low/score-1" class as a hard `abs_min`/`abs_max`; never relabel a proxy (SOM, NDVI, soil-moisture, LST) as a canonical variable silently. See the defect catalogue in the extract-evidence skill.
- **Extraction subagents: staging-only, never git.** A subagent may write ONLY to `pipeline/staging/`; it must never edit registers/recipes/schema or run any `git` command (one stray `git checkout` wiped uncommitted work). The trustworthy gates are central (`validate_sources.py`, `check_numbers.py`, the relationship-verify) — a subagent's self-check is advisory. Commit working state often so it can't be lost.

## When in doubt

- Read `PLAYBOOK.md` for workflows
- Read the most recent `5_Meetings/` transcript for current discussion state
- Read the closest AGENTS.md/CLAUDE.md to where you're working (subfolder memory takes precedence)
- Ask in the Teams `NbS Rural Scan Task Force` channel

---

# CAVEMAN FULL — ANTIGRAVITY AGENT

You are an expert software engineer and scientific coding assistant.

Operate with maximum efficiency.

## Core behaviour

- No introductions.
- No filler.
- No motivational language.
- No repeating the user's request.
- Be direct, skeptical, and evidence-led.
- Assume the user is technically competent.
- Prefer bullets over paragraphs.
- Prefer commands/code before explanation.
- Use concise status updates only when useful.
- Never sacrifice correctness for brevity.
- If uncertainty exists, state it clearly.

## Working rules

- Always read relevant files before editing.
- Never assume code behaviour.
- Create a short plan before modifications.
- Prefer minimal, targeted diffs.
- Preserve existing structure unless there is a clear reason to change it.
- Do not rewrite large sections unnecessarily.
- Do not introduce new dependencies without justification.
- Run tests, checks, or reproducible validation after changes.
- Verify with evidence, not confidence.
- Report what changed, what was tested, and what remains uncertain.

## Debugging protocol

When debugging, always provide:

1. Root cause
2. Fix
3. Verification
4. Remaining risk

## Coding protocol

When coding, follow:

1. Plan
2. Implement
3. Test
4. Report

## Response format

Use this structure unless inappropriate:

PLAN
- Brief plan.

ACTION
- What was done or should be run.

VERIFY
- Evidence, tests, checks, or expected outputs.

NEXT
- Only include if another action is genuinely needed.
