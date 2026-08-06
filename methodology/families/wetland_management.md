# Wetland Management & Restoration — Suitability-Family Scheme (for review)

*Draft for sign-off · August 2026 · sign-off **Pete + MFL** (Sarah · Chris · Evert · Hannes) domain review · QA **Namita**. (Water/hydrology + wetland-ecology domain reviewer is an open gap since Benson left — flag at validation.)*

> **Why this document exists.** Suitability is reasoned **per suitability family, not per whole NbS** (locked).
> T4 rows key to `suitability_family_id`. Wetland management is the 2nd-richest Water & Wetland NbS in the
> stocktake. This scheme is the reviewable artifact before T4 is populated.
>
> Grounded in the **30 wetland-relevant benchmarked stocktake rows** (`reference/stocktake/peer_reviewed_benchmarked.csv`:
> 20 "Wetland management" + 8 "Constructed Wetlands" + cross-tagged; subpractices seen — wetland restoration,
> wetland creation/reconstruction, peatland restoration, paludiculture (wet meadow/pasture/reed), floodplain
> reconnection, tidal marsh, constructed/treatment wetlands; methods — GIS-MCDA / SMCE / AHP suitability overlays).
> **`nbs_id = wetland_management`.**

## How to review (what we need from Pete + MFL)
1. **Family boundaries** — restore-rewet vs create vs peatland/paludiculture — the right T4 split?
2. **Scope** — are **constructed/treatment wetlands** (point-source / ag-drainage treatment) in scope for a
   *rural landscape* scan, or a separate WASH/engineering concern? Are **coastal** wetlands (tidal marsh) in scope
   or out (same coastal call as forest-restoration mangroves)?
3. **Answer §6.**

## 1. The grouping principle
Every wetland intervention is gated by **hydrology** — water table, inundation regime, drainage history, water
availability. Families split on the **intervention driver** (restore an existing/degraded wetland vs create a new
one vs peat-specific rewetting), because that sets the variable set and the suitable extent.

| Archetype | Dominant limiting factor | Footprint |
|---|---|---|
| Restoration / rewetting | former/degraded wetland extent + hydrology (water table, drainage history, hydro-connectivity) | area |
| Creation | water availability + low-lying/depression terrain + soil + currently-not-wetland | area |
| Peatland / paludiculture | **peat soil presence** + drainage state + water table | area |
| Constructed / treatment | point-source / ag-drainage load + engineered siting | zone / site |

## 2. Proposed families
| ID | Family | Subpractices | Dominant limiting factor | `spatial_product_type` | In scope? |
|---|---|---|---|---|---|
| **F1** | Wetland restoration / rewetting | wetland restoration, rewetting, drainage-blocking, floodplain-wetland reconnection | former/degraded wetland extent + hydrology (water table · drainage history · connectivity) | `area_suitability` | Yes |
| **F2** | Wetland creation | wetland creation, wetland reconstruction | water availability + low-lying/depression terrain + soil permeability + currently-not-wetland | `area_suitability` | Yes |
| **F3** | Peatland restoration / paludiculture | peatland rewetting, paludiculture (wet meadow/pasture, reed) | peat soil presence + drainage state + water table | `area_suitability` | Yes |
| *(parked)* | Constructed / treatment wetlands | HSSF-CW, surface-flow treatment wetlands | point-source / ag-drainage load + engineered siting (area, slope, inflow) | `qualitative_only` | Scope Q — treatment/engineering |
| *(parked)* | Coastal wetlands | tidal marsh, mangrove (see forest-restoration F4) | coastal hydrology — tidal, salinity, elevation | `area_suitability` | Scope Q — coastal |

## 3. Family detail
### F1 — Wetland restoration / rewetting · `wetland_management__restoration_rewetting`
- **Definition.** Restore a degraded/drained wetland to functioning by restoring its hydrology (block drainage,
  re-flood, reconnect the floodplain).
- **Dominant limiting factor.** The **former/degraded wetland extent** (where a wetland was or is degrading),
  water table & inundation regime, drainage history, and hydro-connectivity to the water source.
- **Footprint.** `area_suitability`. **Note:** floodplain-wetland reconnection overlaps riparian_buffer's parked
  floodplain family — keep the split on whether the target is the *wetland body* (here) vs the *streamside strip*
  (riparian). Open question 4.

### F2 — Wetland creation · `wetland_management__creation`
- **Definition.** Create/reconstruct a wetland where one is not currently present (e.g. a farm/landscape wetland
  for water storage, habitat, nutrient interception).
- **Why NOT F1.** Gated by **water availability + low-lying/depression terrain + soil permeability** on
  *non-wetland* land — a siting problem, not a restore-what-was problem. Different variable set.
- **Footprint.** `area_suitability`.

### F3 — Peatland restoration / paludiculture · `wetland_management__peatland`
- **Definition.** Rewet drained peatlands and/or farm them wet (paludiculture — wet meadow/pasture, reed).
- **Why its own family.** Gated by **peat soil presence** (a specific soil layer) + drainage state + water table
  — a distinct variable set (peat depth/extent, subsidence, carbon), and a distinct high-value carbon case.
- **LMIC relevance.** Tropical peat (SE Asia, Congo Basin) is a major rural carbon/land-use case.
- **Footprint.** `area_suitability`.

### Parked / scope questions
- **Constructed / treatment wetlands — `qualitative_only`.** Engineered wetlands for point-source / ag-drainage
  treatment are a siting/engineering problem (peri-urban / point-source), not a landscape suitability surface.
  **Scope Q** — in scope for the rural scan, or out?
- **Coastal wetlands (tidal marsh) — `area_suitability`.** Coastal-hydrology gated; same coastal scope call as
  forest-restoration mangroves (F4 there). **Parked from discovery until sign-off.**

## 4. Edge cases the scheme resolves
- **Restore vs create** — split on whether a wetland was/is there (F1, restore hydrology) vs siting a new one on
  non-wetland land (F2). Different limiting variable (degraded-extent vs terrain/water-availability).
- **Peatland is not just "a wetland on peat"** — the peat soil layer + subsidence + carbon make it a distinct
  variable set → its own family (F3), not an F1 context.
- **Floodplain reconnection** appears here (F1, the wetland body) and as a parked riparian family (the streamside
  strip) — keep the split by target; reconcile at sign-off (Q4).

## 5. How this maps to the schema
- Each subpractice → a **FAM row**. New NbS → new **T0** (`schema/recipes/wetland_management/`).
- **T4 rows key to `suitability_family_id`.** No wetland T4 rows yet; FAM entries are the FK targets.
- First-pass hypothesis, revisable once evidence is in.

## 6. Open questions for sign-off (Pete + MFL)
1. **F1/F2/F3 split** — restore-rewet vs create vs peatland/paludiculture as separate families?
2. **Constructed/treatment wetlands** — in scope for the rural scan or out (engineering/WASH)?
3. **Coastal wetlands (tidal marsh)** — in scope, or out (coastal, as with FR mangroves)?
4. **Floodplain reconnection** — wetland-body (here) vs riparian-strip (riparian_buffer) boundary — agree the split?
5. **Hydrology data** — which water-table / inundation / wetland-extent layers at scoping grade (e.g. Global
   Surface Water, GIEMS, HydroSHEDS, peatland maps)? BIND-resolved.
6. **Naming** — `suitability_family_id`s acceptable for variable cards / TTL displays?

---
## Version history
- **v0.1** (August 2026) — first standalone scheme for sign-off. Grounded in the 30 benchmarked stocktake
  wetland rows. F1–F3 in-scope; constructed/treatment + coastal parked pending scope calls (§6).
