# Opportunity-space (T5) — ratified scheme, v0.3.0

**Owner:** Pete (operational, M3) · Namita (content) · Benson (QA/QC)
**Status:** ratified June 2026 (v0.3.0). Replaces draft-0 T5 set. Companion: `schema/spec.md` T5 section.
**Aligned to:** the WB TORs language on "where TTL priorities intersect the opportunity space" + the
v0.6 wireframe Opportunity Space tab.

---

## What T5 is

T5 = the **opportunity-space**: the variable set the TTL weights in M4 to identify *where* the NbS
opportunity *should* be invested in (within whatever is biophysically suitable from M1). T5 is the
"why this pixel, not that one" layer.

T4 = where the NbS *can* establish (biophysical / system / operational constraints).
T5 = where it *should*, given TTL priorities.
T6 = what the NbS *does* once placed (effects + economics) — T6 conditionality joins via T5
priority rows.

---

## The five-lens scheme (v0.3.0)

Five themes, ordered by what they answer:

| Theme | What it answers | Examples |
|---|---|---|
| **`climate_hazard`** | Where is the climate exposure highest? | drought · flood · heat-stress |
| **`nbs_response`** | Where would the NbS *do* the most? | soil erosion risk · carbon sequestration potential · biodiversity priority |
| **`people_production`** | Where are the people and the productive systems? | water stress · rural poverty · production gap · agricultural dependency |
| **`equity_inclusion`** | Whose disadvantage are we addressing? | gender inequity (national flag) — IPLC/marginalisation layers requires_upload |
| **`context`** | What's the descriptive backdrop (not in MCDA)? | rural population · market access · farm size · ag-production value |

Rename: **`equity_gender` → `equity_inclusion`** (broadens to IPLC, marginalisation, GESI).
Dropped: **`infrastructure`** as a top-level theme — infrastructure is either a descriptor (market
access) or an operational lever (M2b Stream B), not an opportunity-space pillar.

---

## `mcda_role` — priority vs descriptor

A T5 row carries `mcda_role` (Required, v0.3.0):

- **`priority`** — drives the M4 MCDA hotspot; reweightable in the wireframe; T6 effect rows
  attach here.
- **`descriptor`** — carried for narrative, intersection, hand-off, but **not in the MCDA**.
  Examples: rural population (how many people live in the hotspot) · market access (descriptive
  context) · farm size · agricultural production value.

This resolves the "carry every layer" vs "score only the binding ones" tension. Descriptors fix
the surfacing problem (show me context) without inflating the MCDA dimensionality.

**T6 effect rows link only to `priority` rows.** The "what does the NbS do" question doesn't
apply to descriptors.

---

## The 15 ratified rows

### Priorities (11)

| variable_id | theme | concern direction | notes |
|---|---|---|---|
| `drought_hazard` | climate_hazard | higher → more concern | SPEI-based; future-projection ready |
| `flood_hazard` | climate_hazard | higher → more concern | layer choice deferred (FATHOM / JRC / WRI Aqueduct) |
| `heat_stress_hazard` | climate_hazard | higher → more concern | extreme-heat-day count or WBGT |
| `soil_erosion_risk` | nbs_response | higher → more concern | RUSLE-class |
| `carbon_sequestration_potential` | nbs_response | higher → more concern | FAO GSOCseq-style additional-C |
| `biodiversity_priority` | nbs_response | higher → more concern | **placeholder / requires_upload** — layer choice deferred |
| `water_stress` | people_production | higher → more concern | composite (Aqueduct or ET-deficit) |
| `rural_poverty` | people_production | higher → more concern | WB PIP subnational |
| `production_gap` | people_production | higher → more concern | per-farming-system metric via BIND (yield gap / NPP gap / mixed) |
| `agricultural_dependency` | people_production | higher → more concern | share of livelihoods in ag |
| `gender_inequity` | equity_inclusion | higher → more concern | national flag; subnational requires_upload |

### Descriptors (4, `theme=context`)

| variable_id | what it provides |
|---|---|
| `rural_population` | how many people live in the hotspot |
| `market_access` | accessibility — travel time to large markets |
| `farm_size` | mean farm size / smallholder share — agrarian-structure context |
| `agricultural_production_value` | MapSPAM-style value layer — what's economically at stake |

### Held out / requires_upload / deferred

- **`biodiversity_priority`** — ships as BIND `requires_upload`. Layer choice (KBA · IBAT · BII ·
  refugia · distance-to-protected) is a deferred review (seed issue).
- **Marginalisation** (race/ethnicity/IPLC subnational) — unpopulated placeholder under
  `equity_inclusion`. LandMark + WWF/ICCA layers feed M2b tenure stream and the future T5
  marginalisation row when ratified.

---

## Spatial-grain rule (derived from T1.grain_type + T1.admin_level)

**Differentiation requires ≥ admin1 (state/province)** or grid. A T5 priority that resolves to an
`admin0` (country-level) dataset for a given AOI carries a **qualified flag** — it surfaces in
the hand-off + scorecard but is **not used to discriminate hotspots within a country**. The rule
is computed at runtime from `T1.grain_type` (`grid` / `admin` / `vector`) + `T1.admin_level`
(`admin0` / `admin1` / `admin2`) on the bound dataset.

No new T5 field needed — the grain story already lives in T1 (v0.2.9 reshape). T5 just reads it.

Examples:
- `gender_inequity` bound to a national-flag dataset (GII) → `admin0` → flag, not hotspot driver
  *within Sierra Leone*; surfaces as a national-level qualifier.
- `rural_poverty` bound to PIP `admin1` (or `admin2` where available) → MCDA-eligible.
- `drought_hazard` bound to SPEI grid → MCDA-eligible.

Mirrors the resolution-trap (§2.4 in T4 method) on the human-system side.

---

## Proximate-over-distal principle

Where two T5 variables capture the same concern at different distances from the outcome, **prefer
the proximate**. Distal indicators carry compounding uncertainty:

- **Tree cover** > **ecosystem health** > **biodiversity outcome** — prefer the proximate
  observable.
- **Yield gap** > **literacy rate** > **adaptive capacity** > **resilience** — proximate
  proximity.
- **Heat-stress days** > **temperature anomaly** > **climate change index** — proximate first.

Distal indicators that survive are documented as **descriptors**, not priorities.

This sharpens the variable count and forces selection to defensible signals.

---

## How T5 connects to the rest

```
T1 (datasets)
  │ via BIND (variable→dataset, context-resolved)
  ▼
T5 (priorities + descriptors)
  │ priorities → M4 hotspot MCDA
  │ priorities → T6 effect rows
  ▼
T6 (NbS effects on T5 priorities)
```

Joins:
- `T5.variable` → `VONT.canonical_variable_id`
- `T5.dataset_id` → `T1.dataset_id`
- `T6.variable_id` → `T5.variable_id` **where `T5.mcda_role = priority`** (or `T3.hazard_type`
  for hazard-mitigation rows)

---

## Seed issues for follow-up

1. **Biodiversity-layer ratification** — choose `biodiversity_priority`'s bound dataset (KBA /
   IBAT / BII / eco-uniqueness / refugia / distance-to-protected). Currently `requires_upload`.
2. **Marginalisation row** — when WWF/ICCA + LandMark integration matures, add a
   `marginalisation` or `iplc_lands` priority under `equity_inclusion`.
3. **`flood_hazard` layer choice** — FATHOM vs JRC vs WRI Aqueduct vs basin-routing model.
4. **Production-gap binding rollout** — per-farming-system BIND examples beyond the rainfed
   cropping example.
5. **Gender-inequity subnational disaggregation** — currently a national flag; subnational
   layer when available.

---

## What did NOT make it (and why)

- **Infrastructure as a top-level theme** — infrastructure is descriptive context
  (`market_access` descriptor) or operational lever (M2b Stream B). Not an opportunity-space
  pillar of its own.
- **`tree_cover_gap`** (was a draft-0 priority) — proximate-over-distal: superseded by
  `carbon_sequestration_potential` (more proximate to the NbS-response signal) or
  `biodiversity_priority` (proximate to the biodiversity claim). Kept as a candidate descriptor
  for tropical-forest-restoration recipes.
- **`runoff_potential_index`** — M3/M4 internal calculation, not a T5 row.
- **`food_security_risk`** (draft-0) — too distal; subsumed by `production_gap` +
  `rural_poverty`.
- **`groundwater_recharge_potential`** — water-harvesting recipe-specific; lives in T6 effect
  rows for the WH recipe, not in T5.

---

*Companion: `schema/spec.md` T5 section · v0.3.0 changelog · `M2b_project_risk.md` Stream-B for the
operational levers; T4 method §3 for the seed-set rule + screening funnel.*
