# Farming-system vocabulary — Dixon → EO-derived crosswalk (v0.3.0)

The T7 `farming_system` vocabulary was swapped at v0.3.0 from a Dixon-flavoured 9-class
typology to a 6-class **EO-derived** scheme. Dixon now serves as a crosswalk reference only.

## EO-derived classes (T7, v0.3.0+)

Derived at scoping grade from current EO layers:

| EO class (T7 `context_id`) | Derivation (scoping-grade recipe) |
|---|---|
| `cropping_rainfed` | Cropland (GLAD/WorldCereal/ESA WorldCover) + GMIA irrigation < threshold + GLW livestock density low + Hansen tree-cover low. |
| `cropping_irrigated` | Cropland + GMIA irrigation share above threshold. |
| `mixed_crop_livestock` | Cropland co-located with moderate-to-high livestock density (GLW). |
| `agro_pastoral` | Sparse cropland + grazing land-cover + livestock-dominant economy (Sahelian / dryland mosaics). |
| `pastoral_rangeland` | Grassland/shrubland-dominant + high livestock density + minimal cropland. |
| `tree_perennial` | Tree-perennial dominance (cocoa, coffee, oil palm, rubber, fruit) — Hansen tree cover + MapSPAM perennial mask. |

**BIND-overridable** per country/region. The recipe is documented and reproducible; not a
schema enum (open vocab via T7).

## Dixon → EO crosswalk

| Dixon-style label (pre-v0.3.0) | EO class |
|---|---|
| `mixed_rainfed` | `cropping_rainfed` |
| `agro_pastoral_millet_sorghum` | `agro_pastoral` |
| `highland_mixed` | `mixed_crop_livestock` |
| `pastoral` | `pastoral_rangeland` |
| `tree_crop` | `tree_perennial` |
| `irrigated_paddy` | `cropping_irrigated` |
| `dryland_cereal` | `cropping_rainfed` |
| `maize_mixed` | `mixed_crop_livestock` |
| `root_crop` | `cropping_rainfed` |

(Some Dixon classes collapse; the EO scheme is coarser by design — scoping-grade.)

## Why the swap

- **Operationally derived.** EO classes are computable from open layers (no closed-vocab gate
  between AOI definition and farming-system assignment).
- **Distinct from `aez`.** `aez` is bioclimatic; `farming_system` is land-system. The new EO
  scheme makes the distinction non-overlapping.
- **`production_gap` binding-friendly.** BIND resolves `production_gap` per farming_system →
  yield-gap (cropping) · NPP-gap (rangeland) · mixed (mixed systems). Six classes is enough
  resolution at scoping grade.

## Open follow-ups

- **Thresholds.** Pilot AOIs (Sierra Leone, second NbS) will fix the thresholds (e.g. "high
  livestock density" cutoff in GLW units).
- **Dixon → EO mapping per existing project.** Where prior CGIAR/CCAFS work used Dixon, the
  above table is the bridge.
