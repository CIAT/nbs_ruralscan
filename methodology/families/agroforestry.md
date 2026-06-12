# Agroforestry — Suitability-Family Scheme (for review)

*Draft for sign-off · June 2026 · owner Namita, domain review MFL (Sarah · Chris · Evert · Hannes).*

> **Why this document exists.** Suitability in the Rural NbS Scan is reasoned **per suitability family, not per
> whole NbS** (a locked decision). T4 rows key to `suitability_family_id`. Before we populate T4 for agroforestry
> at scale, the family scheme has to be agreed — get it wrong and the wrong evidence aggregates into the wrong
> surface. This is the reviewable artifact: the proposed families, the rationale for each grouping, and the
> specific calls we need the agroforestry domain experts to confirm or correct.
>
> It formalises the first-pass hypothesis embedded in
> [`../T4_generation_method.md`](../T4_generation_method.md) §2.1 into a standalone, signable scheme. It is a
> **scoping-grade** grouping — coarse and honest, not a feasibility taxonomy.

## How to review (what we need from you)

1. **Are the family boundaries right?** Does each family group practices that share a *dominant limiting factor*
   (the thing that decides where they're suitable), or have we mis-merged on appearance?
2. **Is anything missing or mis-placed** from the agroforestry practices relevant to World Bank rural/agricultural
   landscapes — especially for the Sierra Leone pilot?
3. **Answer the numbered open questions** at the end (§6) — these are the calls we can't make without domain input.

Mark up this file directly, or reply in the Teams `NbS Rural Scan Task Force` channel.

## 1. The grouping principle

A **suitability family** = a set of subpractices that share the **dominant limiting factor** deciding where they
can go. That factor sets the *leading variable and the whole variable set*, so practices in one family can be
reasoned about with one coherent evidence base and one T4 surface.

We deliberately **do not group by visual structure or by tree species.** The canonical trap: *scattered trees on
cropland* can arise by **planting** (limited by the biophysical envelope + management) or by **assisted natural
regeneration / retention** (limited by remnant rootstock, seedbank, seed-source proximity, tenure). Same picture
on the ground — different limiting factor, different variables, different suitable area. They must be **different
families**. (This is the same discipline `AGENTS.md` enforces elsewhere: "water harvesting ≠ wetland creation.")

Four limiting-factor archetypes underlie the scheme:

| Archetype | Dominant limiting factor | Footprint logic |
|---|---|---|
| Biophysical-envelope, planted | climate / soil / slope envelope + management access | area |
| Regeneration-potential | remnant rootstock · seedbank · seed-source proximity · tenure | area |
| Placement / geometry | linear-feature logic — wind exposure *or* slope/flow lines | line within a candidate zone |
| Proximity / intensive | settlement & water proximity (sub-pixel) | qualitative |

## 2. Proposed agroforestry families

| ID | Family | Subpractices | Dominant limiting factor | `spatial_product_type` | SLE-pilot relevance |
|---|---|---|---|---|---|
| **F1** | Planted silvoarable | alley cropping, tree intercropping, planted boundary on cropland | arable biophysical envelope + management access | `area_suitability` | High |
| **F2** | Regeneration-based on farmland | FMNR, parkland *retention*, ANR-on-farm | regeneration potential (rootstock · seedbank · seed-source · tenure) | `area_suitability` | High |
| **F3** | Silvopastoral | planted/managed silvopasture, agrosilvopasture | envelope **+** grazing context + forage/livestock variables | `area_suitability` | Medium |
| **F4** | Linear / boundary plantings | windbreaks, shelterbelts, contour & vegetative buffers | wind exposure / slope-flow lines + boundary geometry | `applicability_zone` | Medium |
| **F5** | Shaded perennial-crop systems | shade trees over a perennial cash crop (crop = **parameter**: coffee · cocoa · tea · cardamom · pepper · …) | the host crop's **observed distribution** (where it is grown) + shade-as-adaptation | `area_suitability` | High (cocoa) |
| *(parked)* | Homegardens | multistrata homegardens | settlement & water proximity (sub-pixel) | `qualitative_only` | Low — scorecard only |
| *(separate NbS)* | Riparian buffers | riparian/streamside planting | hydrology / watercourse proximity | `zonal_linear` | n/a — own NbS |

## 3. Family detail

### F1 — Planted silvoarable · `agroforestry__planted_silvoarable`

- **Definition.** Deliberately *planted* woody perennials integrated with annual cropping on cultivable land.
- **Subpractices.** Alley cropping, tree intercropping, planted boundary/live-fence on cropland.
- **Dominant limiting factor.** The arable biophysical envelope (slope, rainfall, temperature, soil pH/depth/SOC)
  plus management/market access — establishment is a deliberate act on farmed land.
- **Leading variables.** Slope · annual precipitation · mean annual temperature · soil pH · soil organic carbon;
  operational: land-cover eligibility, distance to road, protected-area exclusion.
- **Footprint.** `area_suitability` — a suitable pixel ≈ plantable land.
- **This is the worked family** (the F1 × slope gold standard). Slope envelope from the evidence: optimum ≤ ~10°,
  unsuitable > ~30° (machinery/erosion), with montane/semi-arid context overrides.

### F2 — Regeneration-based on farmland · `agroforestry__regeneration_farmland`

- **Definition.** Tree cover *re-established by managing natural regeneration*, not planting — FMNR, parkland
  retention, assisted natural regeneration on farmland.
- **Why it is NOT F1.** The limiting factor is **regeneration potential** — living rootstock / stumps, seedbank,
  seed-source proximity, and tenure security that lets a farmer protect regrowth — not the planting envelope. The
  variable set is different (woody-cover baseline & change, distance to seed source, land-tenure proxies), so it
  cannot be a context override of F1; it is its own family. *Same appearance as planted parkland, different driver.*
- **Footprint.** `area_suitability` (where regeneration can be induced).
- **Note.** Very relevant to Sahelian/West-African parkland and degraded-farmland contexts.

### F3 — Silvopastoral · `agroforestry__silvopastoral`

- **Definition.** Trees deliberately integrated with grazing/livestock systems.
- **Why its own family.** It needs **additional** variables — forage/grazing context, stocking/grazing pressure,
  livestock presence — that F1 doesn't carry. Overrides only re-parameterise existing variables, so silvopasture
  can't be a "cropland → grazing" override of F1; it is a distinct family.
- **Footprint.** `area_suitability`.

### F4 — Linear / boundary plantings · `agroforestry__linear_boundary`

- **Definition.** Trees/shrubs in lines for a placement function — windbreaks, shelterbelts, contour & vegetative
  buffers.
- **Dominant limiting factor.** Linear-feature geometry: wind exposure (windbreaks) or slope/flow lines (contour
  buffers), plus where field boundaries exist.
- **Footprint — `applicability_zone` (critical).** The intervention is a **line within** a candidate area, not the
  area itself. **Never report suitable pixel *area* as footprint** — report candidate length/density (e.g.
  erodible field-boundary km per km²). The over-estimate from area-reporting grows with pixel size.

### F5 — Shaded perennial-crop systems · `agroforestry__shaded_perennial`

- **Definition.** Shade trees over a perennial cash crop. The intervention is shading an *existing* perennial
  crop, so applicability follows where that crop is grown.
- **Why its own family.** Suitability is gated by the **understorey crop's** bioclimatic envelope (coffee → cool
  highlands; cocoa → lowland humid tropics) — a crop-specific variable set distinct from generic silvoarable,
  a crop-specific gate distinct from F1 — so its own family.
- **The crop is a parameter, not a sub-family.** One family; run it once per candidate crop and combine by
  **max across crops, retaining which crop drives each pixel** (the cluster-membership pattern). The surface reads
  "shaded-perennial suitable — cocoa-driven here, coffee-driven there." We **do not** blend crops into one
  envelope (averaging disjoint ranges yields a surface suitable for neither).
- **Constrain by observed distribution, not a modelled niche.** Because we shade *existing* crops, the
  applicability mask is the crop's **observed distribution / production** (e.g. MapSPAM, GAEZ harvested-area, EO
  commodity maps, national ag-stats) — graded by fractional crop area or production where available, not just
  binary presence. Observed distribution already integrates the real climate/soil/market/tenure reasons the crop
  sits where it does. Bioclimatic-envelope (`ecocrop`-style) modelling is the **fallback only where distribution
  data are absent**. *Which* distribution dataset is used is context-resolved via the **BIND registry**
  (`schema/spec.md`): a global default (e.g. MapSPAM), overridable per country — e.g. for the SLE pilot a national
  cocoa map is used if catalogued, else the user is flagged to upload it.
- **Shade-as-adaptation, reframed.** Rather than extending beyond the distribution, **prioritise the
  climate-stressed edge *within* it** — where shade adds the most resilience.
- **Footprint.** `area_suitability` — but the area is defined by crop presence, and bounded by the resolution of
  the crop layer (a coarse distribution dataset constrains coarsely).
- **Relevance.** Cocoa-relevant for the Sierra Leone pilot.

### Parked / out of scope

- **Homegardens — `qualitative_only`.** Multistrata homegardens are sub-pixel and settlement-proximity-driven; a
  raster surface misleads. Handle via the NbS scorecard + an M6 note, not a mapped suitability surface.
- **Riparian buffers — separate NbS (`zonal_linear`).** Suitability is defined *along watercourses*, a different
  spatial logic (the wetland/hydrology cluster), so it lives as its own NbS, not an agroforestry family.

## 4. Edge cases the scheme deliberately resolves

- **Planted parkland vs retained parkland.** A planted Faidherbia parkland is **F1**; a retained/FMNR parkland is
  **F2**. The subpractice label "parkland" alone is ambiguous — keyed by *establishment driver*, not look. *(This
  corrects the draft-0 register, which had parkland under F1.)*
- **Silvopasture as an F1 override?** No — it needs extra variables (see F3).
- **Shaded coffee as an F1 override?** No — crop-gated, and gated by the crop's *observed distribution* (see F5).
- **A family per crop?** No — one F5 family with the crop as a parameter (run per crop, max + retain driver),
  the same way F1 isn't split by tree species.

## 5. How this maps to the schema

- Each subpractice is a row in the **FAM register** (`schema/registers/FAM_family_registry`), carrying
  `suitability_family_id`, `dominant_limiting_factor`, `spatial_product_type`, and a cited `grouping_rationale`.
- **T4 rows key to `suitability_family_id`.** Today only **F1** is populated (the slope slice + draft-0 envelope
  rows); F2–F5 have FAM entries (valid FK targets) but no T4 rows yet — they are populated as evidence is
  extracted per family.
- The grouping is a **first-pass hypothesis, revisable once evidence is in.** Revisions are recorded here so the
  change is auditable.

## 6. Open questions for sign-off

1. **F1/F2 split** — do you agree planted vs regeneration-based should be separate families (different variable
   sets), even though they can look identical on the ground?
2. **F5 crops + distribution data** — we've settled on one family with the crop as a parameter, constrained by
   the crop's *observed distribution* (not a modelled niche). (a) Which crops matter for the WB rural portfolio?
   (b) Which distribution / production datasets do you trust per crop (MapSPAM, GAEZ harvested-area, EO cocoa
   maps, national ag-stats…)? (c) Is observed-distribution constraint the right framing for the pilots, or do you
   want modelled potential anywhere?
3. **F3 silvopastoral** — is it in scope for the pilots, and what forage/grazing datasets would you trust at
   scoping grade?
4. **Homegardens** — agree to keep as `qualitative_only` (scorecard, not mapped)?
5. **Sierra Leone pilot** — confirm the priority families for SLE (proposed: F1, F2, F5-cocoa). Anything else?
6. **Naming** — are the family labels and `suitability_family_id`s acceptable for the variable cards and TTL-facing
   displays?

---

## Version history

- **v0.1** (June 2026) — first standalone scheme for sign-off, lifted from `T4_generation_method.md` §2.1;
  corrected parkland retention F1→F2; added SLE-pilot relevance and review questions.
