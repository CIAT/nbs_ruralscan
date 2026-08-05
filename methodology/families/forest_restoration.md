# Forest Restoration — Suitability-Family Scheme (for review)

*Draft for sign-off · August 2026 · sign-off Pete + domain review MFL (Sarah · Chris · Evert · Hannes), coordination + QA Namita. (Benson left the project Aug 2026; QA/QC → Namita.)*

> **Why this document exists.** Suitability in the Rural NbS Scan is reasoned **per suitability family, not per
> whole NbS** (a locked decision). T4 rows key to `suitability_family_id`. Before we populate T4 for forest
> restoration at scale, the family scheme has to be agreed — get it wrong and the wrong evidence aggregates into
> the wrong surface. This is the reviewable artifact: the proposed families, the rationale for each grouping, and
> the specific calls we need the forest/restoration domain experts to confirm or correct.
>
> Grounded in the **restoration continuum** (passive → assisted → active) canon and in the **62
> forest-restoration rows of the benchmarked stocktake** (`reference/stocktake/peer_reviewed_benchmarked.csv`:
> 38 "Forest conservation and restoration" + 19 "Reforestation and afforestation" + 5 "Community-based forest
> management"). It is a **scoping-grade** grouping — coarse and honest, not a feasibility taxonomy.

## How to review (what we need from you)

1. **Are the family boundaries right?** Does each family group practices that share a *dominant limiting factor*
   (the thing that decides where they're suitable)?
2. **Scope calls** — is **mangrove/coastal** in scope for a *rural agricultural/forestry* scan, or a separate
   coastal NbS? Is **protection / avoided-deforestation** a restoration family here or its own targeting stream?
3. **Answer the numbered open questions** (§6) — the calls we can't make without domain input.

Mark up this file directly, or reply in the Teams `NbS Rural Scan Task Force` channel.

## 1. The grouping principle

A **suitability family** = a set of subpractices that share the **dominant limiting factor** deciding where they
can go. That factor sets the leading variable set, so practices in one family share one coherent evidence base and
one T4 surface.

The canonical trap for restoration is the **restoration continuum**: the *same* degraded site can be restored by
**passive regeneration** (remove the pressure, let it recover), **assisted natural regeneration** (help the
existing regeneration along), or **active planting** (plant, because natural regeneration won't deliver). These
look convergent at the endpoint (forest returns) but are decided by **different limiting factors** — regeneration
potential vs intervention-feasibility vs the planting envelope — so they are **different families**. (Same
discipline as the agroforestry F1/F2 planted-vs-regenerated split.)

| Archetype | Dominant limiting factor | Footprint logic |
|---|---|---|
| Regeneration-potential (passive) | remnant-forest/seed-source proximity · residual woody cover · low disturbance · pressure-removal feasibility | area |
| Regeneration-assisted (ANR) | partial regeneration potential + management/access to intervene | area |
| Planting-envelope (active) | biophysical envelope for target species + high degradation lacking regen potential | area |
| Coastal-hydrology (mangrove) | tidal hydroperiod · salinity · intertidal elevation · sediment | area within coastal zone |
| Standing-stock + threat (protection) | existing forest to protect × degradation pressure × governance | zone within existing forest |

## 2. Proposed forest-restoration families

| ID | Family | Subpractices | Dominant limiting factor | `spatial_product_type` | In scope? |
|---|---|---|---|---|---|
| **F1** | Passive natural regeneration | passive/spontaneous regeneration, secondary succession | regeneration potential (seed-source proximity · residual cover · low disturbance · pressure removal) | `area_suitability` | Yes |
| **F2** | Assisted natural regeneration (ANR) | ANR, liberation thinning, protect-and-manage wildlings | partial regeneration potential + intervention feasibility/access | `area_suitability` | Yes |
| **F3** | Active tree planting | reforestation, afforestation, enrichment planting, active planting | planting envelope for target species/community + degradation too high for natural regen | `area_suitability` | Yes |
| **F4** | Mangrove / coastal restoration | mangrove restoration, ecological mangrove restoration (EMR), mangrove afforestation | coastal hydrology — tidal hydroperiod, salinity, intertidal elevation, sediment | `area_suitability` | **Scope Q — coastal** |
| **F5** | Forest protection & CBFM | avoided degradation/deforestation, community-based forest management | existing standing forest × threat/pressure × governance feasibility | `applicability_zone` | **Scope Q — management** |

## 3. Family detail

### F1 — Passive natural regeneration · `forest_restoration__passive_regeneration`
- **Definition.** Forest recovers by spontaneous regeneration once the degrading pressure is removed; no planting,
  no active management of the regeneration.
- **Dominant limiting factor.** Regeneration potential: proximity to remnant forest / seed sources (the stocktake's
  recurring `distance from remnants` variable), residual woody cover & rootstock, low prior land-use intensity, and
  whether the pressure can be removed (protection feasibility).
- **Leading variables.** Distance to remnant forest/seed source · residual tree/woody cover · degradation intensity
  · prior land-use · slope/erosion · (climate as a coarse gate).
- **Footprint.** `area_suitability` — a suitable pixel ≈ land that will regenerate if released.

### F2 — Assisted natural regeneration (ANR) · `forest_restoration__assisted_regeneration`
- **Definition.** Accelerate natural regeneration by removing barriers — weeding, fire/grazing protection,
  liberation thinning, protecting and releasing existing wildlings/rootstock — still relying on natural propagules,
  not planting.
- **Why NOT F1.** ANR applies where regeneration potential is *partial* and needs help, and it requires
  **intervention feasibility** (access, labour, management) that passive regeneration does not. Different position on
  the degradation gradient, different variable set → its own family. *(Same look as F1, different driver.)*
- **Footprint.** `area_suitability`.

### F3 — Active tree planting · `forest_restoration__active_planting`
- **Definition.** Deliberate establishment by planting — reforestation (formerly forest), afforestation (not
  previously forest), enrichment planting, active planting on degraded land.
- **Dominant limiting factor.** The **planting envelope for the target species/community** (climate/soil/slope) plus
  degradation too severe for natural regeneration to deliver (no seed source / no rootstock).
- **Species/community is a PARAMETER, not a sub-family.** Like agroforestry F5's crop parameter: run per target
  species or restoration community, combine by **max across targets, retaining which drives each pixel**. Per-species
  climate-niche models (MaxEnt/SDM — the dominant stocktake method here) inform the envelope but a single-species
  envelope must not define the whole family.
- **reforestation vs afforestation** = a prior-land-cover *context flag*, not separate families (same planting
  limiting factor). Afforestation of native grassland/peatland carries a **do-no-harm** caveat (don't afforest
  non-forest ecosystems) — flag, not a suitability rule.
- **Footprint.** `area_suitability`.

### F4 — Mangrove / coastal restoration · `forest_restoration__mangrove_coastal`  *(scope question)*
- **Definition.** Restoration of mangroves / coastal forested wetlands (planting or, better, ecological mangrove
  restoration = restore hydrology first, let mangroves return).
- **Dominant limiting factor.** Coastal hydrology — tidal inundation/hydroperiod, salinity, intertidal elevation,
  sediment supply, wave energy. A **distinct biophysical set** from terrestrial restoration → its own family *if*
  in scope.
- **SCOPE QUESTION.** The scan targets **rural agricultural/forestry landscapes**. Mangrove/coastal may be **out of
  scope** (a coastal-NbS concern) — or in scope where coastal communities are part of the rural portfolio. **Parked
  from discovery until sign-off.**

### F5 — Forest protection & CBFM · `forest_restoration__protection_cbfm`  *(scope question)*
- **Definition.** Protecting/maintaining existing forest under threat (avoided degradation/deforestation),
  including community-based forest management.
- **Dominant limiting factor.** Existing standing forest to protect × degradation/deforestation pressure × the
  governance/tenure to enforce protection. The **structural (T4) part** is *existing forest cover × threat*
  (system_constraint); the **governance/tenure part is soft enabling-environment → M2b / Module-6, not T4**
  (per the locked hard-vs-soft routing).
- **Footprint.** `applicability_zone` — applies *within* the existing-forest mask; not new-establishment area.
- **SCOPE QUESTION.** Is avoided-deforestation/protection a *restoration* NbS here, or a separate targeting stream?
  **Parked from discovery until sign-off.**

## 4. Edge cases the scheme deliberately resolves

- **Passive vs ANR** — same appearance (natural regeneration), split by intervention intensity/feasibility along the
  degradation gradient (F1 = release only; F2 = actively assist).
- **FMNR / on-farm regeneration is agroforestry, not forest restoration.** `agroforestry__regeneration_farmland`
  (F2) covers regeneration *on farmland*; `forest_restoration__*` covers regeneration/planting on degraded
  **forest/non-farm** land. Boundary = the land system (farmland vs forest land). **Open question 5.**
- **Riparian buffer restoration** — riparian/streamside is its own NbS (`zonal_linear`), not a forest-restoration
  family (same call the agroforestry scheme makes).
- **Agroforestry-based restoration** — belongs to the agroforestry NbS, not here.

## 5. How this maps to the schema

- Each subpractice is a row in the **FAM register** (`schema/registers/FAM_family_registry`), carrying
  `suitability_family_id`, `dominant_limiting_factor`, `spatial_product_type`, and a cited `grouping_rationale`.
- **T4 rows key to `suitability_family_id`.** No forest-restoration T4 rows yet; FAM entries are the valid FK
  targets, populated as evidence is extracted per family.
- The grouping is a **first-pass hypothesis, revisable once evidence is in** — revisions recorded here.

## 6. Open questions for sign-off

1. **Continuum split (F1/F2/F3)** — agree passive vs assisted vs active planting are separate families (different
   limiting factors / variable sets), even though all end in "forest returns"?
2. **F3 species-as-parameter** — agree active planting runs per target species/community (max + retain driver),
   with single-species SDMs informing but not defining the family?
3. **Mangrove (F4)** — in scope for a rural ag/forestry scan, or a separate coastal NbS? *(Currently parked from
   discovery.)*
4. **Protection/CBFM (F5)** — a restoration family here, or a separate avoided-deforestation targeting stream? Is
   its suitability mappable (existing forest × threat), with governance routed to M2b? *(Parked from discovery.)*
5. **Forest-restoration ↔ agroforestry boundary** — is "on-farm vs forest-land" the right line between
   `agroforestry__regeneration_farmland` and `forest_restoration__passive/assisted`? Any grey zone (e.g. degraded
   fallow)?
6. **Pilot relevance (SLE)** — which families for Sierra Leone (proposed: F1, F2, F3; F4 only if the coastal
   mangrove belt is in the portfolio)?
7. **Naming** — family labels and `suitability_family_id`s acceptable for variable cards / TTL displays?

---

## Version history

- **v0.1** (August 2026) — first standalone scheme for sign-off. Grounded in the restoration continuum + the 62
  benchmarked stocktake forest-restoration rows. F1–F3 proposed in-scope; F4 (mangrove) and F5 (protection/CBFM)
  proposed but **parked from discovery** pending the scope calls in §6.
