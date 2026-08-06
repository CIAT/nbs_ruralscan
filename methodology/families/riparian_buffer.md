# Riparian Buffers — Suitability-Family Scheme (for review)

*Draft for sign-off · August 2026 · sign-off **Pete + MFL** (Sarah · Chris · Evert · Hannes) domain review · QA **Namita**. (Water/hydrology domain reviewer is an open gap since Benson left — flag at validation.)*

> **Why this document exists.** Suitability is reasoned **per suitability family, not per whole NbS** (locked).
> T4 rows key to `suitability_family_id`. Riparian buffers were repeatedly deferred from the agroforestry and
> forest-restoration schemes as **"their own NbS — `zonal_linear`"**; this scheme picks that up.
>
> Grounded in the **16 riparian rows of the benchmarked stocktake** (`reference/stocktake/peer_reviewed_benchmarked.csv`:
> 11 "Riparian buffers" + cross-tagged agroforestry/forest rows; subpractices seen — planted riparian buffers,
> natural riparian vegetation, forested riparian buffers, riparian reforestation, floodplain restoration;
> methods — GIS-MCDA, InVEST nutrient-retention, MARXAN). **`nbs_id = riparian_buffer`.**

## How to review (what we need from Pete + MFL)

1. **Family boundaries** — is the planted-vs-natural/restored split right, with grass-vs-woody as a *parameter*
   (not a family)?
2. **Footprint** — `zonal_linear` (buffer length/km along the stream network, **never pixel area**), agreed?
3. **Scope** — is floodplain/hydro-reconnection in scope here, or a separate wetland/river-restoration NbS?
4. **Answer §6.**

## 1. The grouping principle

Every riparian buffer is gated by the **same placement logic**: proximity to the watercourse network, the
riparian-zone slope/width, and the adjacent land use generating the runoff/sediment/nutrient load it intercepts.
Families split on the **establishment driver** (the same planted-vs-regeneration discipline used in agroforestry
F1/F2 and forest-restoration passive/active) — because that decides the variable set and the suitable extent.

| Archetype | Dominant limiting factor | Footprint |
|---|---|---|
| Planted buffer | watercourse proximity + riparian slope/width + adjacent-land runoff load + planting envelope | line along stream |
| Natural / restored | watercourse proximity + existing riparian condition / regeneration potential + hydro-connectivity | line along stream |
| Floodplain reconnection | hydro-geomorphic connectivity (channel–floodplain), bank/levee state | reach / zone |

## 2. Proposed families

| ID | Family | Subpractices | Dominant limiting factor | `spatial_product_type` | In scope? |
|---|---|---|---|---|---|
| **F1** | Planted riparian buffers | planted grass/herbaceous filter strips, planted woody/forested buffers, live fascines | watercourse proximity + riparian slope/width + adjacent-cropland/pasture runoff load + planting envelope | `zonal_linear` | Yes |
| **F2** | Natural / restored riparian vegetation | protection of existing riparian vegetation, riparian natural regeneration, riparian reforestation | watercourse proximity + existing riparian condition / regeneration potential + hydro-connectivity | `zonal_linear` | Yes |
| *(parked)* | Floodplain / hydro-reconnection | reconnection of sidearms, bank-armour removal, floodplain restoration | channel–floodplain hydro-geomorphic connectivity | `zonal_linear` | Scope Q — river-restoration, own NbS? |

## 3. Family detail

### F1 — Planted riparian buffers · `riparian_buffer__planted`
- **Definition.** Deliberately *established* vegetated strips along watercourses — grass/herbaceous filter strips
  and/or planted woody/forested buffers — to intercept sediment & nutrients, stabilise banks, and shade.
- **Dominant limiting factor.** Watercourse proximity (stream network + order), riparian-zone slope & available
  width, the adjacent land use generating the load (cropland/pasture runoff — a `system_constraint`), and the
  planting envelope for the buffer species.
- **Grass vs woody is a PARAMETER, not a sub-family** (shared placement limiter; run per buffer type, retain which
  drives each reach — the F5-crop / restoration-species pattern).
- **Footprint — `zonal_linear` (critical).** Report candidate **buffer length per stream-km** (or eligible
  stream-km), **never suitable pixel area** — the over-estimate grows with pixel size (same rule as agroforestry
  F4 linear).

### F2 — Natural / restored riparian vegetation · `riparian_buffer__natural_restored`
- **Definition.** Protect or passively/assisted-restore *existing* riparian vegetation along watercourses —
  natural regeneration, riparian reforestation of degraded banks.
- **Why NOT F1.** Limiting factor is the **existing riparian condition / regeneration potential** (residual
  vegetation, seed source, hydro-connectivity), not a planting act — different variable set. *(Same
  planted-vs-regeneration discipline as elsewhere.)*
- **Footprint.** `zonal_linear`.

### Parked / scope question
- **Floodplain / hydro-reconnection — `zonal_linear`.** Reconnecting channel–floodplain hydrology (sidearms,
  bank-armour removal) is a **river-restoration** intervention with a hydro-geomorphic limiting factor — may be a
  separate NbS. **Parked from discovery until sign-off.**

## 4. Edge cases the scheme resolves
- **Grass vs woody buffer** — parameter within F1, not separate families (shared along-stream placement limiter).
- **Riparian vs agroforestry linear (F4)** — riparian is gated by the *watercourse* network (hydrology cluster);
  agroforestry F4 windbreaks/contour buffers are gated by *wind/slope-flow* on farmland. Different networks →
  different NbS (the call the agroforestry scheme already made).
- **Footprint** — always `zonal_linear`; never report suitable pixel area as buffer footprint.

## 5. How this maps to the schema
- Each subpractice → a **FAM row** (`suitability_family_id`, `dominant_limiting_factor`, `spatial_product_type`,
  cited `grouping_rationale`). New NbS → new **T0** registry row (`schema/recipes/riparian_buffer/`).
- **T4 rows key to `suitability_family_id`.** No riparian T4 rows yet; FAM entries are the FK targets.
- First-pass hypothesis, revisable once evidence is in.

## 6. Open questions for sign-off (Pete + MFL)
1. **F1/F2 split** — planted vs natural/restored as separate families, grass-vs-woody as a parameter?
2. **Floodplain reconnection** — in scope here or a separate river-restoration NbS?
3. **Footprint** — confirm `zonal_linear` (buffer length per stream-km), not pixel area.
4. **Stream-network data** — which watercourse layer at scoping grade (HydroSHEDS/HydroRIVERS, national
   hydrography)? BIND-resolved.
5. **LMIC context** — stocktake riparian evidence is temperate-heavy (US/EU/China + some Brazil); flag that LMIC
   transferability needs care; targeted CGIAR/tropical riparian search next iteration.
6. **Naming** — `suitability_family_id`s acceptable for variable cards / TTL displays?

---

## Version history
- **v0.1** (August 2026) — first standalone scheme for sign-off. Grounded in the 16 benchmarked stocktake riparian
  rows + the "riparian = own NbS, zonal_linear" deferral from the agroforestry/forest-restoration schemes. F1–F2
  in-scope; floodplain reconnection parked pending the scope call (§6).
