# Schema spec — field-level reference (v0.3.0)

> **v0.3.0-G (June 2026)** — doc-only: Table-overview owners refreshed to current roles
> (Brayden = M2/M2b + T1 download + T7 farming_system classifier; Pete = M1/M3/M4 + T4/T5 method
> lead; Namita = Variable Cards + expert elicitation + T6 lit-sourced; MFL team = T6 domain;
> Benson = QA across). T7 prose updated to match. No structural or content change.
>
> **v0.3.0-F (June 2026)** — additive: `iplc_lands` priority row added under T5
> `equity_inclusion` (issue #31). VONT canonical + BIND `iplc_lands__global` → `landmark_iplc_lands`
> shipped. T5 now 16 rows (12 priorities + 4 descriptors). No structural change.
>
> **v0.3.0 (June 2026)** — large methodology batch: T5 ratification, farming-system vocab swap,
> production-gap variable, T6 economic-profile generalisation + cost-effectiveness denominators,
> M2b implementation variables. Companion methodology doc:
> [`../methodology/opportunity_space_T5.md`](../methodology/opportunity_space_T5.md).
>
> **A — T5 (opportunity-space) ratification.**
>
> - `T5.mcda_role` (Required, new enum): `priority` (drives M4 hotspot MCDA, links to T6 effects)
>   vs `descriptor` (carried for narrative/intersection but not in the MCDA). **T6 effect rows
>   link only to `priority` rows.** Resolves the "carry every layer" vs "score only the binding
>   ones" tension.
> - `T5.theme` enum updated: `climate_hazard` · `nbs_response` · `people_production` ·
>   `equity_inclusion` · `context`. **Renamed `equity_gender` → `equity_inclusion`** (broadens to
>   IPLC/marginalisation/GESI, not just gender) and **dropped `infrastructure`** as a top-level
>   theme — infrastructure rows are either descriptors (`theme = context`) or operational levers
>   (M2b Stream B), not opportunity-space pillars.
> - **Repopulated `T5_opportunity_space.*`** with 15 rows: 11 priorities + 4 descriptors
>   (replaces the draft-0 14). Five-lens reasoning: climate-hazard · nbs-response ·
>   people/production · equity/inclusion · context. Variables: `drought_hazard`, `flood_hazard`,
>   `heat_stress_hazard`, `soil_erosion_risk`, `carbon_sequestration_potential`,
>   `biodiversity_priority`, `water_stress`, `rural_poverty`, `production_gap`,
>   `agricultural_dependency`, `gender_inequity` (national flag for now), plus 4 descriptors
>   `rural_population`, `market_access`, `farm_size`, `agricultural_production_value`.
> - **Spatial-grain rule for T5** (documented in `opportunity_space_T5.md`, derived at runtime
>   from `T1.grain_type` + `T1.admin_level` — *not* a new T5 field): a priority that resolves to
>   `admin0` (country) carries a qualified flag, not a hotspot-discriminating layer.
>   `admin1`-or-finer required for MCDA differentiation; `admin0` → flag for hand-off. Mirrors
>   the resolution-trap (§2.4 in T4 method) on the human-system side.
> - **Proximate-over-distal principle**: where two T5 variables capture the same concern at
>   different distances from the outcome (e.g. tree cover vs ecosystem health), prefer the
>   proximate. Distal indicators (literacy → adaptive capacity → resilience) carry compounding
>   uncertainty and are documented as descriptors, not priorities.
> - `biodiversity_priority` ships as `requires_upload` placeholder via BIND — the choice of
>   biodiversity layer (KBA, IBAT, BII, eco-uniqueness, refugia, distance-to-protected) is a
>   deferred review (see seed issue).
>
> **B — Farming-system vocab swap + `production_gap` + BIND examples.**
>
> - **`T7` `farming_system` vocabulary replaced** with a derived EO classification (~6
>   categories): `cropping_rainfed` · `cropping_irrigated` · `mixed_crop_livestock` ·
>   `agro_pastoral` · `pastoral_rangeland` · `tree_perennial`. Derived at scoping grade from
>   GLAD/WorldCereal cropland · GLW livestock density · GMIA irrigation · Hansen/MapSPAM
>   tree-perennial. **BIND-overridable** per country/region. Distinct from `aez`. Dixon
>   farming-systems vocabulary becomes a documented crosswalk only (kept in
>   `schema/registers/FS_DIXON_CROSSWALK.md`). T7 + T3 rows migrated.
> - **`production_gap`** = shortfall vs the *attainable* productivity of the dominant farming
>   system in the pixel — resolved per `farming_system` via BIND: yield-gap (GAEZ/MapSPAM) for
>   cropping; forage/rangeland NPP gap for pastoral; mixed for mixed-system; **livestock side is
>   thinner → `requires_upload`** for many contexts. Several BIND example rows added populating
>   the new `band`/`access_params` fields from v0.2.9.
>
> **C — Suitability/discovery SOP (no schema change this batch).** Add IPLC tenure/rights sources
> to the T4-method seed-set: **LandMark** (LandMark Global Platform of Indigenous & Community
> Lands) + **WWF / ICCA Consortium** (State of IPLC Lands). Already part of the diamond classes
> from v0.2.7; this batch names them explicitly under the M2b tenure stream as well.
>
> **D — T6 economic profile.**
>
> - `T6.economic_indicator_type` extended with **cost-effectiveness denominators**:
>   `cost_per_beneficiary`, `cost_per_hectare_restored`, `cost_per_tco2e_avoided`,
>   `cost_per_farmer_reached`. Mark these as **indicative scoping-grade**, *not* CBA — they
>   feed M5 / M6 framing, not project finance.
> - **`T6.economic_value_range`** generalised from `[low, high]` pairs to a structured object
>   `{ low, high, unit, source_note }`. **`unit` enum-policed:** `usd_per_ha`,
>   `usd_per_ha_yr`, `usd_per_beneficiary`, `usd_per_tco2e`, `usd_per_farmer`. Draft-0 T6 rows
>   migrated to the new shape.
>
> **E — M2b implementation variables.** Updated `methodology/modules/M2b_project_risk.md` with
> the two streams: **A = asset hazard exposure** (T2 hazards × T3 `asset_threat`/`asset_risk_weight`,
> baseline + future, modulated by T0 `establishment_period_years`); **B = operational / enabling
> environment, scenario levers**: accessibility, electrification, tenure (incl. IPLC/customary
> with FPIC / ESS7 safeguard flag; LandMark + WWF/ICCA layers), conflict / fragility (ACLED,
> WB-FCV list), governance/extension, finance/credit, market/value-chain, labour. **Filter,
> never summed** into the priority hotspot; hard exclusions stay as T4 masks; scoping flags,
> feasibility validates. T4 gets new `operational_constraint` rows tagged
> `is_scenario_candidate = true` for the soft Stream-B levers.
>
> Manifest: `T5.mcda_role` + `T5.theme` enum_values updated; `T7.farming_system` vocab governed
> by data (not enum_values — open vocab via T7); `T6.economic_indicator_type` enum extended;
> `T6.economic_value_range.unit` enum_values added.
>
> Bumped to `v0.3.0-structure-frozen`. Companion docs: `opportunity_space_T5.md`,
> `M2b_project_risk.md`.
>
> **v0.2.9 (June 2026)** — focused T1 (Data Registry) reshape to unblock Brayden's data-download
> layer. **Mixed migration** — additive fields + one field re-classification + one rename target;
> all draft-0 T1 rows migrated in lockstep with CSV+JSON.
>
> - **`T1.scenario_type`** → **Conditional** (was Required). Required only if
>   `analytical_module ∈ { climate_hazard, climate_impact }`; omitted for static / non-climate
>   datasets (SoilGrids, SRTM, OSM roads, GADM, etc.). Mirrors the existing `hazard_type`
>   conditional.
> - **`T1.description`** — **new Required**, UI-facing one-line description. Populate from the
>   provider's official metadata/abstract (GEE catalog, dataset landing page) — *not* bespoke
>   prose. Provenance via `citation` + `download_url`.
> - **Spatial-grain model** — replaces the metres-only assumption:
>   - **`T1.grain_type`** — new Required enum `grid` / `admin` / `vector`.
>   - **`T1.spatial_resolution_m`** — Conditional (required iff `grain_type = grid`).
>   - **`T1.admin_level`** — new Conditional enum `admin0` / `admin1` / `admin2` (required iff
>     `grain_type = admin`).
> - **`T1.citation`** — guidance only (no schema change): **APA-7**, sourced verbatim from the
>   provider's recommended citation where given, else resolved from `doi` via Crossref / DataCite.
>   Don't hand-author. Validator stays at `non-empty`; the format expectation is documented in the
>   T1 field row.
> - **`T1.geographic_coverage`** — now a **list of codes**: ISO 3166-1 alpha-3 country codes
>   (uppercase, e.g. `SLE`), plus the keyword **`global`**, plus UN M49 region tokens for broad
>   regional products (e.g. `sub_saharan_africa`, `developing_regions`). Format-policed by the
>   manifest. Draft-0 free-text strings ("Global", "Global (developing regions)") migrated.
> - **`T1.access_params`** — new Optional object: endpoint / collection / asset-key / band-name
>   that a bare `download_url` can't hold. STAC + API datasets land here.
> - **ISO3 alignment** — uppercase ISO3 standardised across the schema: **T7 `admin_country`
>   context_ids** (`sle` → `SLE`), **BIND `scope_id` / `binding_id`** (cocoa rows), so
>   `T1.geographic_coverage`, `T7.admin_country`, and BIND admin-country scopes share one code
>   vocabulary and the FK-policing lines up.
> - **`BIND.band`** — new Optional field (was an explicit gap): a multi-band asset (e.g. WorldClim
>   bioclim's 19 bands, CHELSA bands) needs to resolve to the right layer per variable. Pairs with
>   `T1.access_params` for the parent dataset.
>
> Bumped to `v0.2.9-structure-frozen`. **Unblocks Brayden's T1 → Python download layer.**
>
> **v0.2.8 (June 2026)** — T5 opportunity-space theme ratification. Equity / gender is **its own
> T5 theme** (`equity_gender`), not folded into `people_production` (Pete decision). Pilot
> theme-weight defaults shift from 4 × 0.25 to 5 × 0.20 (TTL-adjustable at M4); update the
> `theme_weights` lookup when populating it. Manifest now enum-polices `T5.theme` with all five
> values. Additive — existing T5 rows valid; no row needs re-tagging this batch (none currently
> use `equity_gender`; the next equity-leaning T5 variable goes there).
>
> **v0.2.7 (June 2026)** — discovery-and-evidence-sourcing SOP (paired with extended
> `T4_generation_method.md` §3). Additive.
>
> - **SRC additions** (all optional) to make the six-axis credibility rubric auditable:
>   - `study_income_group` (enum: `low` / `lower_middle` / `upper_middle` / `high`) — World-Bank
>     income classification of the study's geography. Drives the **LMIC-preference** tie-break in
>     synthesis (prefer evidence from low/lower-middle/upper-middle for WB-investable contexts).
>   - `is_seminal` (boolean) — flag for foundational / highly-cited / influential sources whose
>     authority outweighs recency. Used to reconcile recency vs seminality in the rubric.
>   - `venue_type` (enum: `peer_reviewed_journal` / `institutional_report` / `preprint` / `grey`) —
>     authority & venue axis; coarser than `method_type`, captures the publication channel.
>
> - **Rubric reconciliation:** the existing **C/I/D** rubric (Content · Impact · Data quality) on
>   `benchmark_tier` is one **summary** of the **six-axis** credibility rubric documented in the T4
>   method doc (§3): (1) evidence strength · (2) methodological transparency · (3) authority & venue
>   reputation · (4) context relevance / transferability (LMIC preference) · (5) recency
>   (compensated by `is_seminal`) · (6) seminality / influence — plus an **independence /
>   conflict-of-interest discount** for advocacy sources. The six axes feed `benchmark_tier`; they
>   are not stored separately on every row. (One scheme, two views.)
>
> - **Manifest:** `SRC.study_income_group` policed by enum_values; `is_seminal` + `venue_type`
>   added as optional fields. Manifest bumped to `v0.2.7-structure-frozen`.
>
> Existing rows that lack the new fields stay valid (all optional).
>
> **v0.2.6 (June 2026)** — methodology sharpenings (paired with `T4_generation_method.md` updates).
> Additive.
>
> - **`T4.suitability_dimension` sharpened** with three definitions ordered by what does the limiting:
>   `biophysical_constraint` (natural envelope) · `system_constraint` (existing land-use/farming
>   system — where "constrain by observed distribution" lives) · `operational_constraint`
>   (implementation feasibility / enabling environment — typical scenario levers).
> - **Hard-vs-soft operational decision** documented (resolves the schema ↔ Fig 9 tension): hard
>   exclusions (legal protected areas, water bodies, urban) stay inside the opportunity space as
>   T4 constraints; soft investment-addressable access/institutional factors are treated as
>   scenario levers + an operational-risk filter on the M2b side, not baked into the core
>   opportunity surface.
> - **Manifest enum_values extended** for T4 to police `suitability_dimension` and
>   `relationship_type` (same way `hazard_type` and `scenario_type` are policed).
> - **`SRC.method_type` vocabulary extended** with `adoption_study` and `mel_report` — observed-
>   reality signals that feed `system_constraint` / `operational_constraint` variables and T6
>   conditionality. (See "Evidence-source principle" in the T4 method doc.)
>
> Existing rows that already use the canonical `suitability_dimension` / `relationship_type` /
> `method_type` values remain valid. Draft-0 T4 mislabels (e.g. `land_cover_eligibility` tagged
> `biophysical_constraint`) are fixed in this release.
>
> **v0.2.5 (June 2026)** — additive fields for the **paper-first extraction loop** (T4 method §3 update)
> and Namita's attribution requirement. Additions:
>
> - **EV:** `raw_name` (preserve the paper's surface name pre-harmonisation), `observed_dataset`
>   (which dataset the paper actually used for the variable — audit-grade), `attribution` (free-text
>   citation pointer when the paper attributes a threshold to a non-corpus source — pairs with
>   `lineage_of` which targets corpus sources), `justification_quote` + `justification_page`
>   (the paper's own rationale for the threshold — a *second* quote, often on a different page from
>   the threshold), `selection_justification` + `selection_justification_page` (why the paper
>   selected the variable at all — typically the AHP-weight prose).
> - **SRC:** `vars_extracted[]` (canonical-id list — paper's variable inventory after sweep),
>   `extraction_status` (`pending|in_progress|swept|signed_off`), `extraction_status_by_family`
>   (per-family map for multi-family papers), `extraction_date`, `extraction_run_id`, `extractor`.
> - **SRC.benchmark_tier**: enum extended with `external` (citations not in the screened corpus —
>   e.g. Ahmad 2019 cited by Mushtaq; gets weight 0 in synthesis).
> - **VONT:** `review_status` (`canonical|pending_review|rejected`; default `canonical`), `raised_by`
>   (the `evidence_id` that surfaced the variable when `pending_review`), `raised_date`,
>   `composite_of[]` (FK → VONT — declares this canonical aggregates other canonicals; runtime can
>   decide single-row vs composite synthesis per-family).
>
> **Rule (new):** `VONT.canonical_variable_id` is **immutable** once assigned. Renames happen via
> the `aliases[]` list, never by mutating the id. EV rows depend on it for FK stability.
>
> Backwards compatible — all additions optional. Existing EV/SRC/VONT rows remain valid; sweep
> output backfills these fields opportunistically.
>
> **v0.2.4 (June 2026)** — extended vocabulary policing: the validator now checks **enum membership**
> (`hazard_type`, `scenario_type` across T1/T2/T3) and FK-binds the remaining context fields
> (`SRC.aez`, `SRC.farming_system` → T7; `SRC.nbs_ids` → T0). Closed enums are policed by value, open
> vocabularies by FK. Additive.
>
> **v0.2.3 (June 2026)** — documented **value governance** (inline enums vs FK-governed vocabularies) and made
> `farming_system` (T3) + `farming_systems_applicable` (T0) explicit FKs to **T7** (`context_type =
> farming_system`); registered the previously-unregistered `irrigated_paddy` + `dryland_cereal` farming systems
> in T7; validator now catches farming-system drift. Additive.
>
> **v0.2.2 (June 2026)** — added optional `VONT.context_sensitivity` (`low`/`medium`/`high`): flags
> nationally-derived / sovereignty-sensitive variables (population, poverty, production) so the scoping
> output recommends a country-endorsed source. A **flag for hand-off, not analysis** — scoping flags, the
> feasibility phase validates. Additive.
>
> **v0.2.1 (June 2026)** — added the **BIND — Dataset Binding registry**: context-aware variable→dataset
> resolution (`global` default + country/AEZ/region overrides; `requires_upload` status drives the
> flag-to-upload prompt), and formalised **most-specific-context-wins** precedence for both BIND and
> `T4.context_overrides`. Additive — no existing column changed. See the BIND section below.
>
> **v0.2 (June 2026)** — added `T3.risk_role` + `T3.asset_risk_weight` (the M2 / M2b two-risk split);
> added `T5.theme` + `T5.weight_default` (hotspot grouping & weighting); reconciled `T4.relationship_type`
> to one canonical membership-function set with a wireframe crosswalk; documented NbS-response layers as
> derived (T5 `theme=nbs_response` × T6) and the shared-layer dedup; **added the evidence & configuration layer**
> (Source / Evidence / Variable-Ontology / Subpractice-Family registers) making T3/T4/T6 values traceable, and
> keyed T4 to `suitability_family_id`. **Field trim (June 2026):** evidence-based tables (T2/T3/T4/T6) now carry
> `evidence_ids` (→ EV) instead of free-text `references`; canonical variable name + unit live only in the
> Variable Ontology (analytical tables reference `variable`); derived/duplicated fields removed
> (`T1.nbs_ids_using`, `T5.spatial_resolution_m`, `T5.category`, `T0.last_updated`/`updated_by`); minor merges
> (`T1.limitations`); added `T4.suitability_family_id` (the unit T4 keys to). v0.1 was the original 8-table design.
>
> **Structure frozen (`v0.2-structure-frozen`).** The column set here is machine-mirrored in
> [`structure/columns.json`](structure/columns.json) and enforced by `src/nbs_ruralscan/schema_tools/structure.py`. Change the
> structure only by editing this spec, regenerating the manifest, and raising an issue — never by reshaping data files.

> In-repo Markdown port of `NbS_Schema_Reference_v01_1.docx` (Pete Steward, 7 May 2026).
> Source archived at [`design/NbS_Schema_Reference_v01.docx`](design/NbS_Schema_Reference_v01.docx).
> Entity-relationship diagram: [`design/NbS_ERD_v01.html`](design/NbS_ERD_v01.html) (also published on the Pages site).
> Worked draft-0 examples (Agroforestry · Water Harvesting): CSV + JSON for every table — see [`README.md`](README.md).

This document defines the complete field-level schemas for the eight JSON/tabular structures that form the
analytical backbone of the Rural NbS Scan. They are the authoritative starting point for:

- **Pipeline implementation** — building the data pipeline and MCDA engine. Code always *reads* from these
  files rather than hardcoding values.
- **Methodology team** — populating the tables for each NbS via human-validated research. Pete coordinates T4 (suitability) generation; Namita coordinates expert-opinion elicitation + Variable Cards + T6 scorecards; Brayden owns the M2/M2b risk-side population and the T1 dataset-download layer.
- **Future expansion** — adding an NbS means appending rows, not changing the schema or the code.

All tables link via three foreign keys: `nbs_id` (from T0), `dataset_id` (from T1), `variable_id` (from T5).

### Value governance — where each field's allowed values live

A field's controlled vocabulary sits in one of two places:

- **Inline enums** — closed value sets are listed in the field's description here in `spec.md` (e.g.
  `risk_component`, `relationship_type`, `cluster`, `spatial_product_type`, `context_sensitivity`). The
  description *is* the vocabulary.
- **FK-governed vocabularies** — open / extensible value sets are owned by a table and referenced by foreign
  key: datasets → **T1**, NbS → **T0**, opportunity variables → **T5**, canonical variables → **VONT**,
  suitability families → **FAM**, evidence → **EV** / sources → **SRC**, and **geographic & farming-system
  contexts → T7** (`aez`, `farming_system`, `admin_*`, `hydrobasin`). To extend one of these, add a row to the
  governing table — never invent a value inline.

So **`farming_system` (T3) and `farming_systems_applicable` (T0) are governed by T7** — the rows with
`context_type = farming_system` (FAO/IIASA-sourced) — with `all` as the only allowed wildcard. The structure
validator enforces these FKs; an unregistered value is flagged rather than silently accepted. (Method §2.3 lists
the vocabularies to lock up front.)

## Table overview

| Table | Primary purpose | Owner | QA | Per-NbS? | Location in repo |
|---|---|---|---|---|---|
| **T0** NbS Registry | Master record per NbS, economic archetype, evidence quality | Namita (content) · Pete (oversight) | Benson | yes (`nbs_id`) | `recipes/<nbs_id>/` |
| **T1** Data Registry | Dataset catalog, access routes, citations, limitations | Brayden (download layer) · Namita (lit-sourced rows) | Benson | no | schema root |
| **T2** Climate Risk Formulation | Risk variables, hazard/exposure formula, double-count guard | Brayden (M2 owner) · Namita (lit) | Benson | no | schema root |
| **T3** NbS × Hazard × Farming | Qualitative mitigation-potential matrix · `risk_role` + asset-threat weights for M2b | Brayden (M2/M2b risk side) · Namita (lit) | Benson | yes (`nbs_id`) | `recipes/<nbs_id>/` |
| **T4** Suitability Mappings | Response functions, scenario flags, context overrides | Pete (method lead) · Namita (lit-sourced rows + expert elicitation) · MFL review | Benson | yes (`nbs_id`) | `recipes/<nbs_id>/` |
| **T5** Opportunity Space Vars | TTL-facing priority layers (`mcda_role = priority` \| `descriptor`) | Pete (M4 lead) · Namita (Variable Cards + expert input) | Benson | no | schema root |
| **T6** NbS Scorecard | Likert effects (linked to T5 priorities), economic profile + cost-effectiveness denominators | Namita (lit-sourced) · MFL team (Sarah · Chris · Evert · Hannes — domain content) | Benson | yes (`nbs_id`) | `recipes/<nbs_id>/` |
| **T7** Geographic Context | AEZ / farming-system (EO-derived, 6 classes) / admin context definitions | Brayden (classifier + analytical context) · Pete (vocab review) | Benson | no | schema root |

**Placement rule (draft-0):** tables that carry an `nbs_id` column (T0, T3, T4, T6) live under
`schema/recipes/<nbs_id>/`; cross-NbS tables (T1, T2, T5, T7) live at the schema root. Adding an NbS adds a
new recipe folder and appends rows to the root tables.

---

## T0 — NbS Registry

Master record — all other tables join on `nbs_id`. One row per NbS. **Create this first** for a new NbS
before populating any other table. `economic_archetype` maps to the CrossBoundary (2023) framework.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `nbs_id` | string | Required | Unique identifier (snake_case). Primary key for all joins. | `agroforestry` |
| `nbs_name` | string | Required | Canonical display name. | `Agroforestry` |
| `aliases` | string[] | Optional | Alternative names in use. | `['Tree intercropping','Parkland AF']` |
| `cluster` | enum | Required | `tree_based` \| `soil_water` \| `wetland` \| `pastoral` \| `landscape_scale`. | `tree_based` |
| `description_short` | string | Required | 1–2 sentence plain-language summary. | `Deliberate integration of trees…` |
| `description_technical` | string | Required | Technical description for methodology docs. | `Agroforestry encompasses…` |
| `farming_systems_applicable` | string[] | Required | FK list → T7 (`context_type = farming_system`; FAO/IIASA-sourced), or `all`. | `['mixed_rainfed','irrigated_paddy']` |
| `implementation_scale` | enum | Required | `plot` \| `farm` \| `landscape` \| `watershed`. | `farm` |
| `establishment_period_years` | object | Required | `{ min, max, typical }`. | `{ min: 2, max: 10, typical: 5 }` |
| `economic_archetype` | enum | Required | `high_capital` \| `long_horizon` \| `fragile_gains` \| `quick_returns`. | `long_horizon` |
| `upfront_cost_usd_ha` | object | Optional | `{ low, high, currency, source_note }`. | `{ low: 200, high: 800, … }` |
| `recurrent_cost_level` | enum | Required | `very_low` \| `low` \| `moderate` \| `high` \| `very_high`. | `moderate` |
| `time_to_benefit_years` | object | Required | `{ min, max }`. | `{ min: 5, max: 10 }` |
| `carbon_credit_eligible` | boolean | Required | Typically eligible for carbon finance. | `true` |
| `is_active` | boolean | Required | Included in the current pipeline. | `true` |
| `evidence_quality` | enum | Required | `strong` \| `moderate` \| `limited` \| `emerging`. | `strong` |
| `primary_references` | string[] | Required | Key supporting literature. | `['Mercer 2004','Jose 2009']` |

---

## T1 — Data Registry

Dataset catalog — every dataset used anywhere in the analysis must have a record here. The pipeline looks up
datasets here rather than hardcoding URLs (`download_url` / `gee_asset_id` carry the access pointer). Which NbS
use a dataset is derived on demand from the T2/T4 joins, not stored.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `dataset_id` | string | Required | Unique identifier (snake_case). | `chelsa_precipitation_v21` |
| `dataset_name` | string | Required | Full descriptive name. | `CHELSA Precipitation v2.1` |
| `description` | string | Required *(v0.2.9)* | Short UI-facing one-line description. **Populate from the provider's official metadata/abstract** (GEE catalog, dataset landing page), not bespoke prose. Provenance via `citation` / `download_url`. | `Bias-corrected high-resolution gridded climate (1981-2010, monthly precip @ ~1 km).` |
| `analytical_module` | enum | Required | `climate_hazard` \| `climate_impact` \| `structural_suitability` \| `adaptive_capacity` \| `exposure` \| `opportunity_space` \| `geographic_context`. | `climate_hazard` |
| `hazard_type` | enum | Conditional | Required if `analytical_module = climate_hazard`: `drought` \| `flood` \| `heat_stress` \| `fire` \| `wind_cyclone` \| `waterlogging` \| `frost` \| `multi`. | `drought` |
| `scenario_type` | enum | Conditional *(v0.2.9)* | Required iff `analytical_module ∈ { climate_hazard, climate_impact }`: `baseline` \| `future_ssp126` \| `future_ssp245` \| `future_ssp585` \| `multi_scenario`. Omit for static / non-climate datasets. | `baseline` |
| `time_period` | string | Optional | Reference period or horizon. | `1981–2010` |
| `grain_type` | enum | Required *(v0.2.9)* | Spatial-grain class: `grid` (raster) \| `admin` (administrative unit polygons keyed by `admin_level`) \| `vector` (other vector features — line, point, irregular polygons). Drives whether `spatial_resolution_m` or `admin_level` is the operative grain field. | `grid` |
| `spatial_resolution_m` | integer | Conditional *(v0.2.9)* | Required iff `grain_type = grid`. Native resolution in metres. **Don't fudge** an admin/vector dataset into metres; leave blank and use `admin_level` (admin) or omit (vector). | `1000` |
| `admin_level` | enum | Conditional *(v0.2.9)* | Required iff `grain_type = admin`: `admin0` (country) \| `admin1` (state / province) \| `admin2` (district). | `admin1` |
| `geographic_coverage` | string[] | Required | List of codes. Values: ISO 3166-1 alpha-3 country codes (uppercase, e.g. `SLE`, `KEN`, `BRA`) · the keyword `global` · UN-M49 / project region tokens (`sub_saharan_africa`, `south_asia`, `latin_america`, `southeast_asia`, `developing_regions`). Format-policed by the manifest. | `['global']` · `['SLE']` · `['sub_saharan_africa']` |
| `data_format` | enum | Required | `geotiff` \| `geotiff_cog` \| `geoparquet` \| `netcdf` \| `csv` \| `shapefile` \| `gee_asset`. | `geotiff_cog` |
| `access_type` | enum | Required | `direct_download` \| `gee_asset` \| `api` \| `proprietary_licensed`. | `direct_download` |
| `download_url` | string | Optional | Direct download URL or DOI. | `https://chelsa-climate.org/` |
| `gee_asset_id` | string | Optional | GEE asset path if `access_type = gee_asset`. | `ECMWF/ERA5_LAND/MONTHLY_AGGR` |
| `access_params` | object | Optional *(v0.2.9)* | Endpoint / collection / asset-key parameters that a bare `download_url` can't hold (STAC, generic API). Free-form keys: `endpoint`, `collection`, `asset_key`, `auth_required`, etc. BIND `band` chooses *which layer*; this object captures *how to reach* the parent dataset. | `{ "endpoint":"https://earth-search.aws.element84.com/v1", "collection":"sentinel-2-l2a" }` |
| `license` | string | Required | License (SPDX identifier preferred). | `CC-BY-4.0` |
| `citation` | string | Required | Full bibliographic citation. **APA-7**, sourced verbatim from the provider's recommended citation where given, else resolved from `doi` via Crossref / DataCite. Don't hand-author. Validator: non-empty; `doi` should be present where one exists. | `Karger, D. N., et al. (2017). Climatologies at high resolution for the earth's land surface areas. Scientific Data, 4, 170122.` |
| `doi` | string | Optional | DOI (canonical machine id). | `10.1038/sdata.2017.122` |
| `version` | string | Required | Dataset version used. | `v2.1` |
| `preprocessing_notes` | string | Optional | Resampling, masking, etc. | `Resample to 1km COG, clip to AOI` |
| `limitations` | string | Required | Key caveats + inappropriate uses (merged). | `Coarse resolution; not for site-level design` |

---

## T2 — Climate Risk Formulation

Variables for hazard, exposure, sensitivity and adaptive capacity, plus the composite-index formula.
AR6-consistent: **Risk = Hazard × Exposure × Vulnerability**, where Vulnerability = f(Sensitivity, Adaptive
Capacity). Weights must sum to **1.0 per `scenario_type` group**. `double_count_risk` is the guard against a
variable appearing in both the risk index and the opportunity space — the pipeline checks it before
compositing.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `variable_id` | string | Required | Unique identifier for this risk variable. | `drought_spei12_baseline` |
| `dataset_id` | string | Required | FK → `T1.dataset_id`. | `spei_global_v26` |
| `risk_component` | enum | Required | `hazard` \| `exposure` \| `sensitivity` \| `adaptive_capacity`. | `hazard` |
| `hazard_type` | enum | Conditional | Required if `risk_component = hazard`. `drought` \| `flood` \| `heat_stress` \| `fire` \| `wind_cyclone` \| `waterlogging` \| `frost`. | `drought` |
| `variable` | string | Required | FK → Variable Ontology (canonical name + unit live there). | `spei12` |
| `scenario_type` | enum | Required | `baseline` \| `future_ssp126` \| `future_ssp245` \| `future_ssp585`. | `baseline` |
| `use_in_simplified_mode` | boolean | Required | Include in simplified (climate-index-only) mode. | `true` |
| `use_in_advanced_mode` | boolean | Required | Include in advanced (hazard × exposure) mode. | `true` |
| `double_count_risk` | enum | Required | `risk_only` \| `opportunity_space_only` \| `shared` (shared → pipeline uses `risk_only` by default). | `risk_only` |
| `normalisation_method` | enum | Required | `min_max` \| `percentile_clip` \| `log_transform` \| `none`. | `percentile_clip` |
| `normalisation_params` | object | Optional | e.g. `{ p_low: 2, p_high: 98 }`. | `{ p_low: 2, p_high: 98 }` |
| `weight_default` | float | Required | Default weight in composite index (0–1; per-scenario weights sum to 1). | `0.35` |
| `weight_adjustable` | boolean | Required | Can TTL/analyst adjust this weight? | `true` |
| `directionality` | enum | Required | `positive_risk` \| `negative_risk` (e.g. adaptive capacity = `negative_risk`). | `positive_risk` |
| `evidence_ids` | string[] | Required | FK list → EV (provenance: source · tier · page · quote). | `['ev_spei_vicente10']` |
| `justification` | string | Optional | One-line summary, generated from the evidence units. | `SPEI-12 is standard drought metric…` |

---

## T3 — NbS × Hazard × Farming System

Qualitative matrix of NbS mitigation potential against each climate hazard, per farming-system context. One
row per NbS × hazard × farming_system. Use `all` in `farming_system` where the relationship holds universally.
Negative scores are allowed where an NbS *worsens* a hazard (e.g. dense planting raising fire risk).

**This table carries the two-risk split.** `risk_role` tags each hazard×NbS row as something the NbS
*mitigates* (a livelihood **need** layer feeding M2) or something that *threatens the asset* but the NbS does
**not** mitigate (feeding the **M2b** project disaster-risk screen). The same hazard family can appear in both
roles for different NbS (e.g. flooding is a need driver for wetland creation but an asset threat to a parkland
plot). M2b reads the `asset_threat` rows and their `asset_risk_weight`; M2 reads the mitigation rows.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `record_id` | string | Required | Unique row identifier. | `agro_drought_mixed_rainfed` |
| `nbs_id` | string | Required | FK → `T0.nbs_id`. | `agroforestry` |
| `hazard_type` | enum | Required | `drought` \| `flood` \| `heat_stress` \| `fire` \| `wind_cyclone` \| `waterlogging` \| `frost`. | `drought` |
| `farming_system` | string | Required | FK → T7 (rows with `context_type = farming_system`), or `all` where the relationship holds universally. | `mixed_rainfed` |
| `mitigation_potential` | enum | Required | 7-point: `very_negative` \| `negative` \| `none` \| `low` \| `moderate` \| `high` \| `very_high`. | `moderate` |
| `risk_role` | enum | Required | Which lens this row serves. `livelihood_mitigation` (NbS *mitigates* this hazard → M2 need layer) \| `asset_threat` (hazard *damages the NbS asset* but is not mitigated → M2b project-risk) \| `both`. | `livelihood_mitigation` |
| `asset_risk_weight` | float | Conditional | Required when `risk_role` includes `asset_threat`. Default weight (0–1) of this hazard in the M2b project disaster-risk rating for this NbS; per-NbS `asset_threat` weights sum to 1. Blank for pure `livelihood_mitigation` rows. | `0.40` |
| `mitigation_mechanism` | string | Required | How the NbS mitigates the hazard (1–3 sentences). | `Tree canopy reduces evapotranspiration…` |
| `confidence` | enum | Required | `high` \| `medium` \| `low` \| `expert_opinion`. | `medium` |
| `timescale_of_effect` | enum | Required | `immediate` \| `short_term_1_3yr` \| `medium_term_3_7yr` \| `long_term_7yr_plus`. | `medium_term_3_7yr` |
| `landscape_scale_only` | boolean | Required | Effect only at landscape/catchment scale, not farm scale. | `false` |
| `caveats` | string | Optional | Conditions or exceptions. | `Effect reduced in very arid AEZs` |
| `evidence_ids` | string[] | Required | FK list → EV (provenance). | `['ev_agro_drought_mbow14']` |
| `justification` | string | Optional | One-line summary, generated from the evidence units. | `Meta-analysis of 47 studies shows…` |

---

## T4 — Suitability Variable Mappings

The most complex table. Each row defines how a dataset variable maps to NbS suitability via a named
`relationship_type` (see the Relationship-type reference below).

### `suitability_dimension` — three dimensions, ordered by what's doing the limiting

Defined by *what does the limiting*, ordered from least to most changeable:

1. **`biophysical_constraint`** — the **natural envelope** (climate, terrain, soils): *can the NbS establish
   and persist at all?* Nature-given. Slow to change, hard to engineer. Examples: slope, mean annual
   temperature, soil pH, soil organic carbon, frost-free period, drought index.
2. **`system_constraint`** — the **existing land-use / farming / land-cover system** the NbS must integrate
   with: current land cover, existing tree cover, farming system, host-crop presence, livestock density.
   This is where the **"constrain by observed distribution, not modelled niche"** rule lives (§2.5) —
   prefer the host system's observed extent over a bioclimatic envelope. Changes on land-use timescales
   (years to decades).
3. **`operational_constraint`** — **implementation feasibility / enabling environment**: road access, market
   access, electrification, extension coverage, land tenure, legal/protected exclusions. Often
   investment-addressable → the **what-if scenario levers** (`is_scenario_candidate = true` lives here).

### Hard vs soft operational decision (resolves the schema ↔ Fig 9 tension)

The stocktake's Figure 9 framing routes social/institutional factors into a separate **Project
Operational Risk** stream. The schema needs to be consistent with that, so:

- **Hard exclusions stay inside the opportunity space** as suitability constraints. Examples: legal
  protected areas, water bodies, urban/built-up footprints, formally-designated reserves. These are
  *not* investment-addressable on the timescale of a scoping exercise; they belong in T4 with
  `suitability_dimension = operational_constraint` and `is_scenario_candidate = false`.
- **Soft, investment-addressable access/institutional factors are NOT baked into the core biophysical
  opportunity space.** They appear as **scenario levers** (T4 rows with
  `is_scenario_candidate = true`) and as inputs to a separate **operational-risk / feasibility filter**
  on the M2b side (project-disaster + project-feasibility lens). Examples: road access, market
  access, extension coverage, tenure security. A soft variable applied as a hard mask would
  over-constrain the opportunity space and hide where investment could *create* feasibility.

The practical test: if turning the variable off in a what-if scenario is a *reasonable* policy
question, it's soft → scenario lever + operational-risk filter. If it isn't (you can't legislate away
a water body), it's hard → exclusion in T4.

This reconciliation makes the schema's three-dimension structure consistent with Fig 9's separation:
biophysical + system + hard-operational ≈ opportunity-space surface; soft-operational ≈ scenario
levers + project-operational-risk stream (M2b family).

### Other field guidance

- **Scenario candidate flag:** `is_scenario_candidate = true` **only** for variables a project investment could
  realistically change (road access, electrification, extension coverage). **Never** true for purely physical
  variables (slope, elevation, soil texture).
- **Context overrides:** the pipeline (1) checks `context_overrides` for a matching `context_type` + `context_id`
  from T7, then (2) falls back to the global `relationship_params` if no match.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `mapping_id` | string | Required | Unique row identifier. | `agro_f1_slope_global` |
| `nbs_id` | string | Required | FK → `T0.nbs_id`. | `agroforestry` |
| `suitability_family_id` | string | Required | FK → `FAM.suitability_family_id`. **The unit T4 is keyed to** — suitability is reasoned per family, not per whole NbS. Rolls up to `nbs_id` for display. | `agroforestry__planted_silvoarable` |
| `dataset_id` | string | Required | FK → `T1.dataset_id`. | `srtm_slope_30m` |
| `variable` | string | Required | FK → Variable Ontology (canonical name + unit live there). | `slope` |
| `suitability_dimension` | enum | Required | `biophysical_constraint` \| `system_constraint` \| `operational_constraint`. | `biophysical_constraint` |
| `relationship_type` | enum | Required | Canonical set: `trapezoidal` \| `gaussian` \| `linear_increasing` \| `linear_decreasing` \| `sigmoid` \| `inverted_sigmoid` \| `threshold` \| `ranked_classes` \| `piecewise`. See the reference + wireframe crosswalk below. | `trapezoidal` |
| `relationship_params` | object | Required | Parameters for the relationship (structure depends on type). | `{ opt_low: 0, opt_high: 15, abs_max: 35 }` |
| `uncertainty_pct` | float | Optional | Symmetric ± buffer on limits (%). | `10` |
| `context_overrides` | object[] | Optional | `[{ context_type, context_id, relationship_params }]`. Global default if no match. | `[{ context_type:'aez', context_id:'humid_tropics', … }]` |
| `is_scenario_candidate` | boolean | Required | Can be toggled off in a what-if scenario (investment-influenceable only). | `false` |
| `scenario_label` | string | Conditional | Required if `is_scenario_candidate = true`. | `What if roads were accessible?` |
| `scenario_description` | string | Conditional | Required if `is_scenario_candidate = true`. | `Removes road-access constraint, showing…` |
| `has_future_projection` | boolean | Required | Changes under future climate scenarios (links to T2). | `true` |
| `baseline_dataset_id` | string | Conditional | Baseline `dataset_id` if `has_future_projection = true`. | `chelsa_precip_baseline` |
| `future_dataset_ids` | object | Conditional | `{ ssp126, ssp245, ssp585 }` → dataset_id. | `{ ssp245: 'chelsa_precip_ssp245_2050' }` |
| `weight_default` | float | Required | Default MCDA weight within the suitability index (0–1). | `0.15` |
| `weight_adjustable` | boolean | Required | Can the analyst adjust the weight? | `true` |
| `n_sources` · `corpus_n` | integer | Optional | Numerator (distinct sources with ≥1 evidence unit for this variable) and denominator (papers screened for the family). | `6` · `8` |
| `paper_support_pct` | float | Derived | Literature-prevalence selection signal = `100 · n_sources / corpus_n`. Rolls up to group via the Variable Ontology `group_id` (set-union). Not stored authoritatively — computed from `n_sources`/`corpus_n`. | `75.0` |
| `evidence_ids` | string[] | Required | FK list → EV (provenance behind the thresholds + shape). | `['ev_slope_nair93','ev_slope_zomer14']` |
| `justification` | string | Optional | One-line summary of why this variable and shape, generated from the evidence units. | `Slope >35° prevents machinery access…` |

### Relationship-type reference (`relationship_type` + `relationship_params`)

This is the **one canonical list** of membership/response functions. It supersedes the older
`binary`/`linear_decay`/`*_fuzzy` names and the diagram's "5-function" wording, and it is the set the
`docs/pipeline.html` P1 primitive and the TTL wireframe both map to (crosswalk in the last column).

| Canonical `relationship_type` | Parameters | When to use | TTL wireframe label · internal token |
|---|---|---|---|
| `trapezoidal` | `{ abs_min, opt_low, opt_high, abs_max }` | Optimal plateau with declining shoulders. Most biophysical variables (slope, rainfall). 1.0 within `[opt_low, opt_high]`, → 0 at `abs_min`/`abs_max`. `uncertainty_pct` applies a symmetric ± buffer to the limits. | "Trapezoidal (plateau)" · `trapezoid` |
| `gaussian` | `{ mean, sigma }` | Bell-curve suitability around an optimum (temperature optima). Subsumes the old "bell". | "Gaussian (optimal band)" · `gaussian` |
| `linear_increasing` | `{ unsuitable_min, suitable_max }` | More is better — rises linearly between the bounds. | "Linear — more is better" · `linup` |
| `linear_decreasing` | `{ suitable_max, unsuitable_min }` | Less is better — falls linearly (was `linear_decay`). | "Linear — less is better" · `lindown` |
| `sigmoid` | `{ midpoint, slope }` | Smooth monotonic **increase** (S-curve). | advanced — not in the TTL dropdown |
| `inverted_sigmoid` | `{ midpoint, slope }` | Smooth monotonic **decrease** (S-curve). | advanced — not in the TTL dropdown |
| `threshold` | `{ threshold, above_is_suitable: bool }` | Hard pass/fail (was `binary`); e.g. protected area = exclude. | "Threshold (hard cut)" · `threshold` |
| `ranked_classes` | `{ class_map: { value: score } }` | Categorical input (soil type, land use) → 0–1 scores. | categorical — separate control |
| `piecewise` | `{ points: [[x, y], …] }` | User-defined custom curve. | "Custom (piecewise)" · `custom` |

> `ecocrop` is **not** a base type — it is a multi-dimensional composite (`{ t_min, t_opt_low, t_opt_high, t_max }`
> replicated per dimension) built from `trapezoidal`/`threshold` limits. Document it as a composite where used.
>
> **Surfacing.** The TTL wireframe exposes the continuous subset (trapezoidal · gaussian · linear↑/↓ · threshold ·
> piecewise). `sigmoid`/`inverted_sigmoid` and `ranked_classes` are available to the engine and to technical users
> but are not in the default TTL dropdown. The wireframe keeps its short internal tokens (`trapezoid`, `linup`,
> `lindown`, `custom`); they map to the canonical names per the table above.

---

## T5 — Opportunity Space Variables

Layers characterising the opportunity space that TTLs weight and combine to identify hotspots. They describe
the *characteristics* of the geographic space within the biophysical opportunity space — **not** suitability
constraints. Climate risk enters here via `is_climate_risk_component = true`, but `double_count_risk` in T2
prevents double-counting.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `variable_id` | string | Required | Unique identifier. | `rural_poverty_headcount` |
| `variable` | string | Required | FK → Variable Ontology (canonical name, unit, and `group_id` for theme roll-up live there). | `rural_poverty_headcount` |
| `theme` | enum | Required | Hotspot pillar for grouping + theme-level weighting in M4. `climate_hazard` \| `nbs_response` \| `people_production` \| `infrastructure` \| `equity_gender` (v0.2.8 — equity / gender / GESI is its own theme, not folded into people_production). | `equity_gender` |
| `dataset_id` | string | Required | FK → `T1.dataset_id`. | `worldpop_poverty_2020` |
| `directionality_of_concern` | enum | Required | `high_is_bad` \| `low_is_bad` \| `context_dependent` (sets dashboard colours). | `high_is_bad` |
| `ttl_priority_label` | string | Required | Short label in the weighting interface. | `Poverty` |
| `ttl_priority_description` | string | Required | 1–2 sentence explanation for the TTL. | `Areas with high poverty headcount…` |
| `is_climate_risk_component` | boolean | Required | Also used in T2 (pipeline uses T2 `double_count_risk` to avoid duplication). | `false` |
| `aggregation_method` | enum | Required | `mean` \| `sum` \| `max` \| `majority` \| `area_weighted_mean`. | `mean` |
| `normalisation_method` | enum | Required | `min_max` \| `percentile_clip` \| `log_transform` \| `none`. | `percentile_clip` |
| `weight_default` | float | Required | Default weight of this variable **within its theme** for the hotspot MCDA (0–1; weights within a theme normalise to 1). TTL-adjustable at M4. | `0.25` |
| `has_future_projection` | boolean | Required | Future projection available. | `false` |
| `is_active` | boolean | Required | Include in current prototype. | `true` |
| `evidence_ids` | string[] | Optional | FK list → EV where a literature claim backs inclusion (context layers may be data-only). | `['ev_poverty_wb24']` |

### Theme weights and NbS-response layers

**Theme weights.** Variable weights normalise within a theme; the *theme-level* defaults that set how much each
pillar drives the hotspot index live in a small `theme_weights` lookup at the schema root. With the v0.2.8 split
the pilot defaults are **5 × 0.20** across `climate_hazard` · `nbs_response` · `people_production` · `infrastructure` · `equity_gender` (previously 4 × 0.25; TTL-adjustable at M4). Earlier pilot defaults:
`climate_hazard` 0.30 · `nbs_response` 0.25 · `people_production` 0.30 · `infrastructure` 0.15). All TTL-adjustable
at M4. (A row carrying `weight_default` × its theme weight gives the variable's contribution before user reweighting.)

**NbS-response layers (`theme = nbs_response`).** These are the only T5 variables whose magnitude is
**NbS-specific** — e.g. erosion-reduction potential, water-yield benefit, carbon sequestration, biodiversity
co-benefit. They are **derived, not stored as fixed rasters**: the shared T5 row defines the underlying
need/biophysical layer + direction + `dataset_id`; the per-NbS strength comes from the matching **T6** scorecard
effect, joined on `variable_id` + `nbs_id` (`effect_direction` / `effect_mechanism`). So no extra table is needed —
the T5↔T6 link already carries the NbS-specific modulation. Pure context layers (poverty, market access) have no
T6 row and are identical across NbS.

---

## T6 — NbS Scorecard — Effects and Economic Profile

Per-NbS qualitative effect on each opportunity-space variable, plus economic indicators — the scorecard the
literature team completes. An economist can use `economic_value_range` to construct an indicative cost-benefit
narrative without a full CBA. `economic_archetype_id` points to the CrossBoundary archetype lookup (the
narrative lives there), not a model output.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `record_id` | string | Required | Unique row identifier. | `agro_rural_poverty` |
| `nbs_id` | string | Required | FK → `T0.nbs_id`. | `agroforestry` |
| `variable_id` | string | Required | FK → `T5.variable_id` **or** a hazard_type from T3. | `rural_poverty_headcount` |
| `variable_type` | enum | Required | `opportunity_space_variable` \| `climate_hazard_mitigation` \| `economic_indicator`. | `opportunity_space_variable` |
| `effect_direction` | enum | Required | Likert: `strong_negative` \| `moderate_negative` \| `slight_negative` \| `no_relationship` \| `slight_positive` \| `moderate_positive` \| `strong_positive`. | `moderate_positive` |
| `effect_confidence` | enum | Required | `high` \| `medium` \| `low` \| `expert_opinion`. | `medium` |
| `effect_mechanism` | string | Required | How/why the NbS affects this variable (1–3 sentences). | `Diversified income from timber and fruit…` |
| `conditionality` | string | Optional | Conditions under which the effect holds or reverses. | `Only where tenure security is established` |
| `timescale_of_effect` | enum | Required | `immediate` \| `short_term_1_3yr` \| `medium_term_3_7yr` \| `long_term_7yr_plus`. | `long_term_7yr_plus` |
| `economic_indicator_type` | enum | Conditional | Required if `variable_type = economic_indicator`. `establishment_cost` \| `recurrent_cost` \| `income_potential` \| `cost_reduction` \| `market_access` \| `carbon_revenue` \| `subsidy_dependency` \| `cost_per_beneficiary` \| `cost_per_hectare_restored` \| `cost_per_tco2e_avoided` \| `cost_per_farmer_reached` *(v0.3.0 cost-effectiveness denominators)*. **Indicative, scoping-grade** — not CBA. Feeds M5/M6 framing, not project finance. | `cost_per_hectare_restored` |
| `economic_value_range` | object | Conditional | Generalised in v0.3.0 to `{ low, high, unit, source_note }`. **`unit` enum-policed:** `usd_per_ha` \| `usd_per_ha_yr` \| `usd_per_beneficiary` \| `usd_per_tco2e` \| `usd_per_farmer`. `low` / `high` are numeric in `unit`. `source_note` carries provenance + study context. | `{ low: 200, high: 1200, unit: "usd_per_hectare_restored", source_note: "WB AFR100 PADs 2019-2023, n=12" }` |
| `economic_archetype_id` | string | Optional | FK → CrossBoundary archetype lookup (narrative lives there, not inline). | `agroforestry_long_horizon` |
| `evidence_ids` | string[] | Required | FK list → EV (provenance behind the effect + economic range). | `['ev_agro_income_mercer04']` |
| `justification` | string | Optional | One-line evidence summary, generated from the evidence units. | `Mercer (2004) meta-analysis shows…` |

---

## T7 — Geographic Context

AEZ, farming-system, administrative and hydrological context definitions used to resolve context-specific
overrides in T4. Populated by Brayden (analytical context + EO-derived farming-system classifier — see
`methodology/farming_system_classifier.md`) with Pete reviewing the controlled vocab; Benson QA. Provides
the controlled vocabulary the pipeline looks up by `context_type` + `value_in_dataset` when reading
raster/vector data.

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `context_id` | string | Required | Unique identifier. | `humid_tropics` |
| `context_type` | enum | Required | `aez` \| `farming_system` \| `admin_country` \| `admin_region` \| `hydrobasin`. | `aez` |
| `context_name` | string | Required | Human-readable name. | `Humid tropics` |
| `parent_context_id` | string | Optional | For hierarchical contexts (sub-AEZ within AEZ). | `tropics` |
| `dataset_id` | string | Required | FK → `T1.dataset_id` for the boundary/classification dataset. | `gaez_v4_aez33` |
| `geometry_field` | string | Required | Field in the dataset holding the geometry or raster value. | `aez_code` |
| `value_in_dataset` | string | Required | Value/code identifying this context in the dataset. | `120` |
| `description` | string | Required | Brief description for documentation. | `Humid tropical zone, >1200mm rainfall…` |
| `is_active` | boolean | Required | Currently used for overrides. | `true` |

---

## Evidence & configuration layer (upstream of T0–T7)

Added v0.2. These tables feed the evidence-based analytical tables (**T3, T4, T6**) and are produced by the T4
generation method ([`../methodology/T4_generation_method.md`](../methodology/T4_generation_method.md)). They make
every analytical value traceable: **T4 row → `evidence_id`s → source (tier, page, quote)**. Source tier is stored
once on the Source Register and reached by `source_id` join — never copied onto evidence rows.

### SRC — Source Register

One row per publication/report/tool (formalises the stocktake `NbS_peer_reviewed_benchmarked.csv`).

| Field | Type | Req | Description | Example |
|---|---|---|---|---|
| `source_id` | string | Required | Unique id. | `nath_2021` |
| `citation` · `doi` | string | Required | Bibliographic. | `Nath et al. (2021)…` |
| `benchmark_tier` | enum | Required | `high` \| `medium` \| `low` \| `external`. Summary tier derived from the **six-axis credibility rubric** (T4 method §3): evidence strength · methodological transparency · authority & venue · context relevance/transferability (LMIC preference) · recency (offset by `is_seminal`) · seminality/influence — minus an independence/COI discount. The existing C/I/D rubric is one view of the six axes; both produce the same `benchmark_tier`. `external` = citation-only, not screened — weight 0 in synthesis. **The only place tier is stored.** | `medium` |
| `study_country` · `region` · `coords` | string | Optional | Where the study was done. | `India / E. Himalaya` |
| `aez` · `farming_system` | string | Optional | Study context (→ T7 vocab). | `humid_tropics` |
| `method_type` | enum | Optional | `ahp` \| `critic` \| `entropy` \| `fao_landeval` \| `ecocrop` \| `empirical` \| `expert` \| `adoption_study` \| `mel_report`. Last two are **observed-reality** signals (adoption/dis-adoption studies, MEL/MELIA reports) that feed `system_constraint` / `operational_constraint` variables and T6 conditionality (see T4 method doc, "Evidence-source principle"). | `adoption_study` |
| `study_income_group` | enum | Optional *(v0.2.7)* | World-Bank income classification of the study's geography. `low` / `lower_middle` / `upper_middle` / `high`. Drives the LMIC-preference tie-break in synthesis — evidence from `low`/`lower_middle`/`upper_middle` is preferred for WB-investable contexts. Multi-country studies take the modal income group. | `lower_middle` |
| `is_seminal` | boolean | Optional *(v0.2.7)* | Flag for foundational / highly-cited / influential sources whose authority outweighs simple recency. Used in synthesis to avoid penalising landmark older studies under a recency rule. | `true` |
| `venue_type` | enum | Optional *(v0.2.7)* | Authority & venue axis (coarser than `method_type`): `peer_reviewed_journal` / `institutional_report` (FAO, IPCC, WB, ICRAF, etc.) / `preprint` (bioRxiv, EarthArxiv, SSRN) / `grey` (project reports, blog/web, working papers). | `institutional_report` |
| `spatial_scale` · `analysis_resolution_m` | string/int | Optional | Scale + grid used. | `1000` |
| `nbs_ids` | string[] | Optional | NbS the source addresses. | `['agroforestry']` |
| `vars_extracted` | string[] | Optional *(paper-first sweep)* | Canonical-variable ids the paper-first sweep captured. Derivable via `SELECT DISTINCT variable FROM EV WHERE source_id=...`; persisted for fast lookup + completeness check. FK → VONT. | `['slope','annual_precipitation','soil_ph',...]` |
| `extraction_status` | enum | Optional *(paper-first sweep)* | `pending` \| `in_progress` \| `swept` \| `signed_off`. Default `pending` when absent. | `swept` |
| `extraction_status_by_family` | object | Optional *(paper-first sweep)* | Per-family map for multi-family papers. Keys are `suitability_family_id`, values are the status enum. | `{"agroforestry__planted_silvoarable":"swept"}` |
| `extraction_date` | date | Optional *(paper-first sweep)* | ISO date the sweep completed. | `2026-06-05` |
| `extraction_run_id` | string | Optional *(paper-first sweep)* | Free-form run identifier (git sha, timestamp, ticket id). | `nath_sweep_worked_example` |
| `extractor` | string | Optional *(paper-first sweep)* | Who/what did the extraction. | `claude-opus-4-7` |

### EV — Evidence Register

One row per **atomic claim**. The structured replacement for free-text justifications.

| Field | Type | Req | Description | Example |
|---|---|---|---|---|
| `evidence_id` | string | Required | Unique id. | `ev_slope_nath21` |
| `source_id` | string | Required | FK → SRC. (tier via join.) | `nath_2021` |
| `nbs_id` · `suitability_family_id` | string | Required | What it pertains to. | `agroforestry` · `agroforestry__planted_silvoarable` |
| `variable` | string | Required | FK → Variable Ontology (canonical). | `slope` |
| `relationship` | object | Optional | Extracted thresholds/shape. | `{opt_low:0,opt_high:10,abs_max:44,unit:"deg"}` |
| `context` | object | Optional | AEZ/farming system the claim applies to. | `{aez:"humid_tropics"}` |
| `use_role` | enum | Required | Which table it feeds. `structural_suitability`(T4) \| `climate_risk`(T2) \| `priority_need`(T5) \| `nbs_effect`(T6) \| `dataset`(T1) \| `operational_risk`(M2b Stream-B — soft enabling-environment levers; emitted into the recipe as a flagged `operational_constraint` section, **kept out of the T4 suitability surface**; 2026-06-23). | `structural_suitability` |
| `evidence_type` | enum | Required | `literature_relationship` \| `ml_importance` \| `scoping_candidate` \| `expert`. Only literature/expert carry shape params. | `literature_relationship` |
| `claim_basis` | enum | Required | `primary_measured` \| `modelled` \| `cited_secondary` \| `expert_assertion` \| `table` \| `figure_read`. Claim strength within source. | `table` |
| `claim_scope` | enum | Required | `practice_technology` \| `species_specific` \| `crop_specific`. Species/crop claims must not set practice rows. | `practice_technology` |
| `taxon` | string | Conditional | Required when `claim_scope ≠ practice_technology`. | `Morus alba` |
| `lineage_of` | string | Optional | `evidence_id`/`source_id` this claim is *echoing* (citation cascade) → dedupe to origin. | `harrison_2016` |
| `extraction_confidence` | enum | Required | Transcription fidelity. | `high` |
| `quote` · `page` | string/int | Required | Verbatim + page (provenance). | `"…slope 0 to 5…", p.11` |
| `reviewer_ok` | boolean | Optional | Human-validated. | `false` |
| `raw_name` | string | Optional *(paper-first sweep)* | The paper's surface name **before** harmonisation to the canonical variable. Preserves the mapping audit (`gradient` → `slope`). | `Slope degree` |
| `observed_dataset` | string | Optional *(paper-first sweep)* | Which dataset the paper actually used to operationalise the variable. Free-text or T1 `dataset_id` when catalogued. Feeds resolution-audit decisions. | `SRTM 90m` · `worldclim_v2_bioclim` |
| `attribution` | string | Optional *(Namita's attribution requirement)* | Free-text citation pointer when the paper *attributes* the threshold/variable selection to a source not in our screened corpus. Pairs with `lineage_of` (which targets corpus sources). | `Harrison (2016) — slope >35% cut` |
| `justification_quote` · `justification_page` | string/int | Optional *(Namita's attribution requirement)* | A *second* verbatim quote (different from the threshold quote) capturing the paper's rationale for **why** the threshold was chosen. Often on a different page from the threshold itself. | `"…mechanisation-limited beyond this gradient", p.5` |
| `selection_justification` · `selection_justification_page` | string/int | Optional *(Namita's attribution requirement)* | Quote + page explaining why the paper **selected the variable at all** (typically the AHP-weight prose or criteria-table commentary). Separate from threshold reasoning. | `"slope ranked second-most-important due to erosion + mechanisation interaction", p.6` |

### VONT — Variable Ontology

Canonical variables: harmonisation + data-catalog link + resolution validity.

| Field | Type | Req | Description | Example |
|---|---|---|---|---|
| `canonical_variable_id` | string | Required | Unique id. | `slope` |
| `label` | string | Required | Display name. | `Terrain slope` |
| `aliases` | string[] | Optional | Known surface names **and synonymous variable names** that map to this canonical (so a source's wording resolves here, and near-equivalent variables are linked rather than duplicated — e.g. `distance_to_settlement` carries `distance to market`; `accessibility_travel_time` carries `market_access`). May be empty. | `['terrain slope','gradient','slope %']` |
| `canonical_unit` | string | Required | Canonical unit. | `degrees` |
| `unit_conversions` | object | Optional | Conversions to canonical unit (may be empty). | `{pct→deg:"atan"}` |
| `group_id` | string | Required | → Variable-Group vocab (Topographic, …). | `topographic` |
| `candidate_dataset_ids` | string[] | Required | → T1 datasets that can supply it. | `['srtm_dem_30m','srtm_dem_90m']` |
| `min_meaningful_resolution_m` | integer | Required | Coarsest grid at which the variable stays valid. | `90` |
| `resolution_sensitivity` | enum | Required | `low` \| `medium` \| `high` (derivatives = high). | `high` |
| `derive_then_aggregate` | boolean | Required | Compute native then summarise to grid (slope, TWI…). | `true` |
| `context_sensitivity` | enum | Optional | How generalisable / politically sensitive the variable is. `low` (generalisable physical — slope, climate; global default fine) \| `medium` (context-dependent but apolitical — soils, land cover) \| `high` (nationally-derived / sovereignty-sensitive — population, poverty, production stats; prefer a **country-endorsed** source). A **flag** read by variable cards, the data-gap prompt and the M6 hand-off — it does not change the analysis. | `high` |
| `review_status` | enum | Optional *(paper-first sweep)* | `canonical` \| `pending_review` \| `rejected`. Default `canonical`. `pending_review` rows are queued for Pete/Namita ontology sign-off — EV rows may point at them, but no T4 synthesis until status flips to `canonical`. | `pending_review` |
| `raised_by` | string | Optional *(paper-first sweep)* | The `evidence_id` that surfaced this variable during a sweep. Audit trail for `pending_review` entries. | `ev_cec_nath21` |
| `raised_date` | date | Optional *(paper-first sweep)* | ISO date the entry was raised. | `2026-06-05` |
| `composite_of` | string[] | Optional | If this canonical aggregates other canonicals (e.g. `soil_fertility = [soil_n, soil_p, soil_k, soil_organic_carbon]`), the list of member canonical_variable_ids. FK → VONT. **Decision deferred per-family** — at synthesis time the recipe chooses whether to use the composite or the individual atoms. | `['soil_n','soil_p','soil_k','soil_organic_carbon']` |
| `comment` | string | Optional | Free-text note. Used on `pending_review` rows to flag schema-level decisions (depth stratification, merge vs split, composite vs atomic). Removed or resolved when the row flips to `canonical`. | `Depth-stratified pair with soil_organic_carbon. Decide: separate canonicals vs single canonical with depth context.` |

**Immutability rule (v0.2.5):** `canonical_variable_id` is **permanent** once assigned. Renames happen via `aliases[]`, never by mutating the id — EV rows depend on it for FK stability. Migrations that change the meaning of a canonical require a deprecation/replacement pair, not a rename.

### FAM — Subpractice / Suitability-Family registry

NbS decomposition; the unit T4 is keyed to.

| Field | Type | Req | Description | Example |
|---|---|---|---|---|
| `subpractice_id` · `nbs_id` | string | Required | Variant + parent NbS. | `alley_cropping` · `agroforestry` |
| `name` · `definition` | string | Required | + scope boundaries. | `Alley cropping` |
| `suitability_family_id` | string | Required | The family it belongs to (T4 keys to this). | `agroforestry__planted_silvoarable` |
| `dominant_limiting_factor` | string | Required | Why it's grouped here. | `biophysical envelope + management` |
| `spatial_product_type` | enum | Required | `area_suitability` \| `applicability_zone` \| `zonal_linear` \| `qualitative_only`. | `area_suitability` |
| `grouping_rationale` · `references` | string/[] | Required | Documented + cited (auditable lumping). | `…` |

**T4 change:** rows key to `suitability_family_id` (subpractices roll up to NbS for display). T4 `references`/
`justification` now cite `evidence_id`s.

### BIND — Dataset Binding registry (context-aware data resolution)

*Added v0.2.1.* Binds a **variable → dataset per geographic context**, so a global recipe can be **refined for an
AOI** without forking it. Each variable has a `global` binding (the default); a country/AEZ/region can override it
with a better local dataset. When the better dataset is known but not yet catalogued, the row carries no
`dataset_id` and `status = requires_upload` — the signal the runtime/wireframe uses to **prompt the user to supply
it** (falling back to the global default meanwhile). Relationship *parameters* are refined separately and
compositely via `T4.context_overrides`; BIND chooses *which dataset*, the overrides re-parameterise the *response*.

| Field | Type | Req | Description | Example |
|---|---|---|---|---|
| `binding_id` | string | Required | Unique id. | `cocoa_distribution__sle` |
| `variable` | string | Required | FK → VONT. | `cocoa_distribution` |
| `scope_type` | enum | Required | `global` \| `aez` \| `farming_system` \| `admin_country` \| `admin_region` \| `hydrobasin`. | `admin_country` |
| `scope_id` | string | Conditional | FK → `T7.context_id`. Required unless `scope_type = global`. | `sle` |
| `dataset_id` | string | Optional | FK → `T1.dataset_id`. **Blank** when `status = requires_upload`. | `mapspam_cocoa_2020` |
| `band` | string | Optional *(v0.2.9)* | When the bound dataset is a multi-band / multi-layer asset, this names the specific band/layer to use for the variable. WorldClim bioclim → `BIO1`/`BIO12`; CHELSA → `bio1`/`bio12`; multi-asset GEE collections → the asset key. Pairs with `T1.access_params`. | `BIO12` |
| `preference_rank` | integer | Required | Lower = preferred when several bindings match a pixel's context. | `1` |
| `status` | enum | Required | `catalogued` (in T1, fetchable) \| `community` (community-hosted) \| `requires_upload` (better data known, user must supply). | `requires_upload` |
| `fitness_note` | string | Optional | Why this dataset for this context (resolution, currency, provenance). | `National EO cocoa map, 10 m, 2023` |

**Resolution rule (runtime).** For each variable in an AOI: collect bindings whose `scope` matches the AOI's
contexts (from T7), pick the one with the **most-specific scope**, breaking ties by lowest `preference_rank`.
Precedence: `admin_region` > `admin_country` > `hydrobasin` > `farming_system` > `aez` > `global`. If the winning
binding is `catalogued`/`community` → pull it; if `requires_upload` → use the global default, **flag the user**,
and record the substitution in the run config + resolution audit. The same most-specific-wins precedence now
governs `T4.context_overrides`.

---

### TOOL — Tools / Methods registry

*Added v0.3.2 (clarified v0.3.3).* Catalogues the **tools, codebases, and method frameworks** that implement (or
inform) spatial NbS prioritisation — the output of the dedicated tool/method + codebase discovery channel
(`SRC.source_category = tool`).

**A tool is a source, evidence-reviewed like any other.** Its thresholds, weights, membership functions, and criteria
*are* extractable claims → **EV rows** (provenance via `locator_type = file_line` + `commit_sha` for code, or
`section`/anchor for a method doc), reviewed in QA/QC under the `tool` channel. So a tool also gets a **SRC** row
(`source_category = tool`, `source_kind = website`/codebase). **TOOL is the metadata layer that *extends* SRC for
tools** — *which* variables/weighting/membership/datasets/workflow it uses, plus maturity, licence, C/I/D — it does
**not** replace evidence extraction. Link a tool's EV rows back via `evidence_ids`. A tool's hard-coded parameter is a
design choice, not a literature finding, so its EV rows carry `claim_basis = tool_default` (or `expert_assertion`) —
captured, then weighted accordingly in synthesis.

| Field | Type | Req | Description | Example |
|---|---|---|---|---|
| `tool_id` | string | Required | Unique id (snake_case). | `icraf_spacial_dashboards` |
| `name` | string | Required | Display name. | `CIFOR-ICRAF SPACIAL Dashboards` |
| `tool_type` | enum | Required | `codebase` \| `platform` \| `method_framework` \| `r_package` \| `gee_app` \| `webgis`. | `webgis` |
| `url` | string | Required | Repo or platform URL. | `https://dashboards.icraf.org/` |
| `organisation` | string | Optional | Authoring body. | `CIFOR-ICRAF` |
| `repo_commit` | string | Optional | Commit SHA pin (code provenance, immutable). | `a1b2c3d` |
| `license` | string | Optional | SPDX or stated licence. | `MIT` |
| `language` | enum | Optional | `python` \| `r` \| `gee_js` \| `javascript` \| `other` \| `na`. | `python` |
| `nbs_ids` | string | Optional | Pipe-delimited NbS targeted. | `agroforestry` |
| `spatial_method` | enum | Optional | `mcda_ahp` \| `fuzzy` \| `rule_based` \| `ml` \| `optimization` \| `process_model` \| `other`. | `mcda_ahp` |
| `membership_functions` | string | Optional | Which of the 5 fuzzy primitives it uses. | `sigmoid\|linear` |
| `weighting_scheme` | string | Optional | `ahp` / `critic` / `entropy` / `equal` / `expert` …. | `ahp` |
| `variables_used` | string | Optional | Pipe-delimited → VONT canonicals. | `slope\|annual_precipitation` |
| `datasets_used` | string | Optional | Pipe-delimited → BIND/T1. | `srtm_dem_90m` |
| `workflow_summary` | string | Optional | One-line method/workflow. | `AHP weights × fuzzy membership overlay` |
| `validation` | enum | Optional | `validated` \| `partial` \| `unvalidated` (six-axis evidence strength). | `partial` |
| `benchmark_tier` | enum | Optional | `High` \| `Medium` \| `Low` (C/I/D). | `Medium` |
| `combined_score` | string | Optional | C/I/D combined score. | `2.5` |
| `maturity` | enum | Optional | `active` \| `archived` \| `prototype`. | `active` |
| `source_id` | string | Optional | FK → SRC (cached doc/snapshot backing it). | `icraf_spacial_2024` |
| `evidence_ids` | string | Optional | Pipe-delimited EV rows extracted from it. | `ev_slope_x` |
| `locator` | string | Optional | Where the key method lives (`file:line` / section / anchor). | `src/mcda.R:120` |
| `review_status` | enum | Optional | `canonical` \| `pending_review` \| `rejected`. | `pending_review` |
| `notes` | string | Optional | Free text. | — |

---

## Implementation notes

**File formats.** Each table is a CSV (the **human-editable source of truth**) plus a typed JSON
array-of-objects (one object per row) for machine consumption. **The JSON is generated from the CSV — never
edit it by hand.** Regenerate with `python3 src/nbs_ruralscan/schema_tools/generate.py schema` (CI fails on stale JSON via
`--check`). Conversion is per-cell: a cell that parses as JSON becomes its typed value (numbers, booleans,
`null`, nested `[...]`/`{...}`); otherwise it stays a string; empty cells are dropped. For large tables (T1,
T4), JSONL (one object per line) is an option for streaming.

**Foreign-key validation (fail loudly).** On load, validate: every `dataset_id` in T2/T3/T4/T5/T7 exists in
T1; every `nbs_id` in T0/T3/T4/T6 exists in T0; every `variable_id` in T6 exists in T5 (or is a T3 hazard_type
for `climate_hazard_mitigation` rows). Evidence layer: every `variable` in T2/T4/T5 (and EV) exists in **VONT**;
every `evidence_id` in T2/T3/T4/T5/T6 exists in **EV**; every `source_id` in EV exists in **SRC**; every
`suitability_family_id` in T4 (and EV) exists in **FAM**. A missing target raises an explicit error — never a
silent gap.

**Climate mode switch.** A top-level `climate_mode = 'simplified' | 'advanced'`. Simplified filters T2 rows by
`use_in_simplified_mode = true` and uses only the composite climate index as a single variable; advanced uses
all `use_in_advanced_mode = true` rows and computes hazard × exposure × vulnerability explicitly.

**Scenario / what-if logic.** For each T4 row with `is_scenario_candidate = true`, expose a UI toggle. Toggling
off sets that variable's suitability to 1.0 (constraint removed); the pipeline recomputes the composite
suitability surface and reports the change in opportunity-space extent and density.

**Context-override resolution.** For each pixel: (1) identify AEZ and farming system via T7; (2) for each T4
row, check `context_overrides` for a matching `context_type` + `context_id`; (3) use the override
`relationship_params` if found, else the global params.

**Pilot scope.** Populate T0–T7 for one NbS at a time. The pipeline reads dynamically from the files; adding a
new NbS later requires only adding rows, not code changes.

---

*Ported from `NbS_Schema_Reference_v01_1.docx` — v0.1 Draft, Peter Steward (Team Lead), 7 May 2026.
For queries: P.Steward@cgiar.org*
