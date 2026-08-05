# Water Harvesting & Conservation — Suitability-Family Scheme (for review)

*Draft for sign-off · August 2026 · domain owner **Benson** (this is his canonical recipe), QA Benson, coordination Namita.*

> **Why this document exists.** Suitability is reasoned **per suitability family, not per whole NbS**
> (locked). T4 rows key to `suitability_family_id`. Water Harvesting is the **most evidenced NbS in the
> stocktake (85 studies)** and Benson's canonical recipe — so the family scheme must be agreed before T4 is
> populated at scale. This is the reviewable artifact.
>
> Grounded directly in **`methodology/recipes/water_harvesting.md`** (§1–§2, which already frames in-situ vs
> ex-situ vs terracing vs micro-catchment and the subpractice-specific membership functions) and the **85
> benchmarked stocktake rows** (`reference/stocktake/peer_reviewed_benchmarked.csv`; dominant subpractices:
> check dams, farm ponds, percolation tanks, bench terraces, contour ridges, runoff strips, gully plugs).
> **`nbs_id = water_harvesting_conservation`.**

## How to review (what we need from you, Benson)

1. **Are the family boundaries right?** The recipe already separates in-situ / micro-catchment / ex-situ /
   terracing by the water-balance question they answer — is that the right T4 family split?
2. **Footprint types** — ex-situ storage structures (check dams, ponds) and their placement on drainage lines:
   `applicability_zone` (site density, not pixel area), agreed?
3. **Answer §6 open questions.**

## 1. The grouping principle

The recipe (§2) states the three convergent suitability questions: **(i) where is runoff generated**,
**(ii) where can it be captured/stored/infiltrated** given terrain·soil·land-cover, **(iii) where is it
strategically desirable**. Families are grouped by **which of these the dominant limiting factor answers** — the
same water-balance logic the recipe already uses to switch membership functions per subpractice (e.g. increasing
sigmoid on runoff for ex-situ, decreasing for recharge; ponds favour 1–8 % slope, terraces 5–25 %).

| Archetype | Dominant limiting factor | Footprint |
|---|---|---|
| In-situ moisture conservation | on-field water balance — rainfall deficit + soil infiltration/depth, gentle slope, placed on inter-stream slopes | area |
| Micro-catchment | short-slope runoff:cropped-area ratio + slope/soil | area |
| Ex-situ / macro-catchment storage | runoff generation + **drainage-line geomorphology** (stream order, drainage density, proximity to channel, clay/storage) | zone along drainage (site density) |
| Terracing / slope SWC | **slope** (defining) + soil depth for construction | area |

## 2. Proposed families

| ID | Family | Subpractices | Dominant limiting factor | `spatial_product_type` | In scope? |
|---|---|---|---|---|---|
| **F1** | In-situ moisture conservation | contour bunds/ridges, tied ridging, mulching, conservation tillage, planting pits, Zai, Negarim micro-basins | on-field water balance (rainfall deficit + infiltration/soil depth), gentle slope | `area_suitability` | Yes |
| **F2** | Micro-catchment harvesting | semi-circular bunds, eyebrow terraces, runoff strips | short-slope runoff:cropped-area ratio + slope/soil | `area_suitability` | Yes |
| **F3** | Ex-situ / macro-catchment storage | farm ponds, check dams, percolation tanks, gully plugs, nala bunds, small earthen/recharge dams | runoff generation + drainage-line geomorphology (stream order · drainage density · channel proximity · clay/storage) | `applicability_zone` | Yes |
| **F4** | Terracing / slope SWC | bench terraces, stone bunds, fanya juu, gradoni, contour stone terraces | slope (defining) + soil depth | `area_suitability` | Yes |
| *(parked)* | Rooftop / domestic harvesting | cisterns, reservoirs, rooftop catchment | settlement/building presence (sub-pixel) | `qualitative_only` | Scope Q — settlement, not rural landscape |
| *(parked)* | Floodwater / spate harvesting | spate irrigation, water spreading, jessour | ephemeral channel / wadi presence + sediment | `zonal_linear` | Scope Q — thin in stocktake |

## 3. Family detail

### F1 — In-situ moisture conservation · `water_harvesting__in_situ`
- **Definition.** Capture and hold rain *where it falls* on the field — no external catchment or storage
  structure. Contour bunds/ridges, tied ridging, mulching, conservation tillage, planting pits, Zai, Negarim.
- **Dominant limiting factor.** On-field water balance: rainfall deficit (aridity), soil infiltration &
  water-holding capacity, soil depth, gentle-to-moderate slope. Placed on **inter-stream slopes** (recipe §
  "in-situ practices are placed on inter-stream slopes"; membership on runoff is *decreasing* — low-runoff
  areas favour in-situ moisture conservation).
- **Footprint.** `area_suitability`.

### F2 — Micro-catchment harvesting · `water_harvesting__micro_catchment`
- **Definition.** Short-slope-length systems where a small bare catchment feeds an adjacent cropped basin —
  semi-circular bunds, eyebrow terraces, runoff strips.
- **Dominant limiting factor.** The local runoff-to-cropped-area ratio at short slope lengths, plus slope/soil.
  Intermediate between purely in-situ (F1) and structural storage (F3) → its own family.
- **Footprint.** `area_suitability`.

### F3 — Ex-situ / macro-catchment storage · `water_harvesting__runoff_catchment`  *(family already in FAM)*
- **Definition.** Collect runoff from a catchment *larger* than the storage/benefiting area into a structure —
  farm ponds, check dams, percolation tanks, gully plugs, nala bunds, small earthen/recharge dams.
- **Dominant limiting factor.** Runoff generation (increasing membership) **and drainage-line geomorphology** —
  stream order (gully plugs 1st–2nd, check dams 2nd–3rd, farm ponds 3rd–4th, small dams 4th–5th; recipe §),
  drainage density, proximity to drainage line, soil clay for seepage control / storage volume.
- **Footprint — `applicability_zone` (critical).** Structures are sited **on/near drainage lines**, not spread
  over pixels. Report **candidate siting density** (e.g. suitable structure sites per km² of drainage), never
  suitable pixel *area* — the over-estimate grows with pixel size (same rule as agroforestry F4 linear).

### F4 — Terracing / slope SWC · `water_harvesting__terracing`
- **Definition.** Reshape the slope to intercept and hold runoff — bench terraces, stone bunds, fanya juu,
  gradoni, contour stone terraces.
- **Dominant limiting factor.** **Slope** is the defining variable (recipe: bell-shaped 5–25 % for terraces vs
  1–8 % for ponds) plus soil depth for construction. A distinct slope-driven envelope from F1/F3.
- **Footprint.** `area_suitability`.

### Parked / scope questions
- **Rooftop / domestic harvesting — `qualitative_only`.** Settlement/building-driven, sub-pixel; not a
  rural-landscape suitability surface. Scorecard/M6 note. **Scope Q.**
- **Floodwater / spate harvesting — `zonal_linear`.** Ephemeral-channel/wadi gated; thin in the stocktake.
  **Scope Q** — own family or fold into F3? Parked from discovery pending sign-off.

## 4. Edge cases the scheme resolves
- **In-situ vs micro-catchment** — both on-field, split by whether a distinct runoff-donor catchment exists
  (F2) or not (F1); the recipe's runoff membership flips sign between them.
- **Ex-situ storage footprint** — never pixel area; drainage-line siting density (F3 `applicability_zone`).
- **Terracing vs micro-catchment eyebrow terraces** — eyebrow/runoff-strip terraces are micro-catchment (F2,
  runoff-ratio driven); bench/bund terraces are slope-reshaping (F4, slope driven). Open question 3.

## 5. How this maps to the schema
- Each subpractice → a **FAM row** (`suitability_family_id`, `dominant_limiting_factor`, `spatial_product_type`,
  cited `grouping_rationale`). `runoff_catchment` already exists; F1/F2/F4 added.
- **T4 rows key to `suitability_family_id`.** No WH T4 rows yet; FAM entries are the FK targets.
- First-pass hypothesis, revisable once evidence is in.

## 6. Open questions for sign-off (Benson)
1. **Four-family split** (in-situ / micro-catchment / ex-situ / terracing) — right T4 boundaries, matching the
   recipe's per-subpractice membership logic?
2. **F3 footprint** — agree ex-situ storage is `applicability_zone` (drainage-line siting density, not pixel
   area)?
3. **Eyebrow/runoff-strip terraces** — F2 (micro-catchment) not F4 (terracing)? Confirm the boundary.
4. **Rooftop harvesting** — keep `qualitative_only` (out of the mapped rural surface)?
5. **Spate/floodwater** — own family or folded into F3? In scope for the pilots?
6. **Naming** — `suitability_family_id`s acceptable for variable cards / TTL displays?

---

## Version history
- **v0.1** (August 2026) — first standalone scheme for sign-off. Grounded in Benson's water-harvesting recipe
  (§1–§2) + the 85 benchmarked stocktake rows. F1–F4 proposed in-scope; rooftop + spate parked from discovery
  pending scope calls (§6).
