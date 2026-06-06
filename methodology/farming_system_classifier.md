# EO-derived farming-system classifier — recipe

**Owner:** Brayden (lead) · Pete (oversight) · Benson (QA / fitness sign-off)
**Status:** v0.3.0 scoping-grade recipe; thresholds documented + tuned per AOI.
**Companion:** `src/nbs_ruralscan/farming_system.py` (classifier code) · `tests/test_farming_system.py` ·
`schema/registers/FS_DIXON_CROSSWALK.md` (Dixon ↔ EO crosswalk).

The schema's six T7 `farming_system` classes are derived from open EO layers at scoping grade.
This doc captures the **decision tree**, **default thresholds**, **per-AOI tuning** (Sierra Leone
pilot below), and **fitness limits**.

---

## Output classes (T7 `farming_system`)

| `context_id` | Definition |
|---|---|
| `cropping_rainfed` | Cropland present + low irrigation + low livestock density. |
| `cropping_irrigated` | Cropland present + irrigation share above threshold. |
| `mixed_crop_livestock` | Cropland present + moderate-to-high livestock density. |
| `agro_pastoral` | Sparse cropland + grazing-dominant land cover + moderate livestock. |
| `pastoral_rangeland` | Non-cropland grassland/shrubland + high livestock density. |
| `tree_perennial` | Tree-perennial dominant (cocoa, coffee, oil palm, rubber, fruit). |

A seventh literal — `other` — is emitted when no rule matches (rare; typically barren / built /
permanent water). Operationally `other` is masked out before the layer enters BIND / T7.

---

## Input layers (T1)

| Role | T1 `dataset_id` | Resolution | Provider |
|---|---|---|---|
| Cropland (primary) | `glad_global_cropland_2019` | 30 m | Potapov et al. 2022 |
| Cropland + irrigation (auxiliary) | `esa_worldcereal_2021` | 10 m | ESA WorldCereal 2021 |
| Livestock density (TLU per km²) | `glw4_livestock_2020` | ~10 km | FAO/ILRI Gridded Livestock of the World v4 |
| Irrigation share (area equipped) | `fao_gmia_v5` | ~10 km | FAO GMIA v5 |
| Tree-perennial mask | `hansen_treecover2000` + `mapspam_cocoa_2020` | 30 m / 10 km | Hansen + MapSPAM (per-crop perennial layers) |

All five live in `schema/T1_data_registry.*` with full metadata. The classifier function takes
**pre-aligned arrays** at the analysis grid; preprocessing (reproject, resample, mask, TLU
computation) is upstream of `classify_arrays`.

---

## Decision tree (priority order — first match wins)

```
if tree_perennial_frac >= thr_tree_perennial_dominant:
    return "tree_perennial"

cropland = cropland_frac >= thr_cropland_present
if cropland and irrigation_frac >= thr_irrigation_share:
    return "cropping_irrigated"
if cropland and livestock_tlu_per_km2 >= thr_livestock_mixed:
    return "mixed_crop_livestock"
if cropland:
    return "cropping_rainfed"

# not cropland
if livestock_tlu_per_km2 >= thr_livestock_pastoral:
    return "pastoral_rangeland"
if livestock_tlu_per_km2 >= thr_livestock_agro:
    return "agro_pastoral"
return "other"
```

**Why this order:** tree-perennial dominance is the most decisive signal (it overrides what would
otherwise be mixed_crop_livestock when livestock + cropland mosaic with the perennial canopy).
Irrigation precedes livestock-mixing because irrigated cropping is operationally distinct (water
+ land+labour) from rainfed-mixed. Pastoral precedes agro_pastoral because high livestock density
without cropland is unambiguous; agro_pastoral is the "moderate + sparse-crop" middle case.

---

## Default thresholds (v0.3.0 scoping-grade)

| Threshold | Default | Rationale |
|---|---:|---|
| `cropland_present` | 0.10 | Pixel is "cropland" when ≥10 % of area is cropland. Conservative — admits mixed-use pixels common in smallholder mosaics. |
| `irrigation_share` | 0.20 | GMIA "area equipped for irrigation" above 20 % flips the pixel to irrigated. Calibrate against WorldCereal irrigation where it agrees. |
| `livestock_mixed_tlu_per_km2` | 5.0 | Ruminant TLU above 5/km² in cropland → mixed system. ILRI mixed-system literature thresholds. |
| `livestock_agro_tlu_per_km2` | 5.0 | Same threshold for non-cropland → agro_pastoral. |
| `livestock_pastoral_tlu_per_km2` | 20.0 | Ruminant TLU above 20/km² (rangeland baselines) → pastoral_rangeland. |
| `tree_perennial_dominant` | 0.50 | Tree-perennial fraction above 50 % → tree_perennial system. |

These are **defensible scoping-grade starting points**. Per-AOI tuning is expected before pilot
deliverable; defaults are *not* validated against ground truth at the global level.

---

## Per-AOI tuning — Sierra Leone (pilot AOI)

Sierra Leone is dominated by smallholder rainfed cropping with significant cocoa/oil-palm
tree-perennial systems in the south-east; limited large irrigation; modest livestock density
(under-counted in Sahelian-derived GLW prior; pastoral systems uncommon). Pilot tuning:

| Threshold | SLE override | Notes |
|---|---:|---|
| `cropland_present` | 0.10 (default) | Default conservative; matches smallholder mosaic. |
| `irrigation_share` | 0.10 | Drop to 0.10 — irrigation in SLE is small-scale lowland (bolilands, mangrove rice) often below GMIA's 20% threshold; cross-check with WorldCereal irrigation. |
| `livestock_mixed_tlu_per_km2` | 3.0 | Lower than default — SLE livestock density is modest; 3 TLU/km² captures the mixed-with-small-stock systems. |
| `livestock_agro_tlu_per_km2` | 3.0 | Match. |
| `livestock_pastoral_tlu_per_km2` | 15.0 | Pure pastoral is rare in SLE; lowered to surface where present. |
| `tree_perennial_dominant` | 0.40 | Slightly lower — cocoa under shade canopy + oil-palm patches register ~40 % perennial fraction in pixels (Hansen + MapSPAM). |

Override the defaults with:

```python
from nbs_ruralscan.farming_system import Thresholds, classify_arrays

sle = Thresholds(
    irrigation_share=0.10,
    livestock_mixed_tlu_per_km2=3.0,
    livestock_agro_tlu_per_km2=3.0,
    livestock_pastoral_tlu_per_km2=15.0,
    tree_perennial_dominant=0.40,
)
out = classify_arrays(cropland, irrigation, livestock_tlu, tree_perennial, thresholds=sle)
```

Document any AOI-specific override in the run config + the discovery log
(`methodology/discovery_logs/`).

---

## BIND integration

The classifier output is **the** authoritative `farming_system` layer for an AOI run, and
populates:

- `T7.farming_system` rows (one per class) via the value-in-dataset = class id mechanism.
- **BIND override**: a `farming_system__<aoi>` row binding the variable to the AOI-specific layer
  (status `community` once stable, `requires_upload` until validated).

For variables whose dataset is **resolved per farming_system** (e.g. `production_gap` — yield gap
for cropping / NPP gap for pastoral / mixed for mixed systems), BIND uses the classifier output
to pick the right dataset per pixel via `most-specific-context-wins`.

---

## Fitness limits

- **Scoping grade only.** This classifier is not validated for site-level decisions; do not use
  for project-finance allocation.
- **GLW is modelled.** Livestock density at high spatial resolution is dasymetric. Uncertainty
  highest in pastoral / mobile-herd contexts; cross-check with ground-truth or sub-national
  statistics before relying on the pastoral_rangeland / agro_pastoral boundary.
- **GMIA is coarse.** 5 arc-min irrigation is a known under-estimate of small-scale irrigation
  (bolilands, paddies, smallholder schemes). WorldCereal irrigation auxiliary recommended.
- **`other` is real, not a bug.** Some pixels are barren/built-up/water and don't fit the
  classifier; mask before the classifier or accept `other`.
- **Updates lag.** GLAD cropland 2019, GLW v4 (~2015 baseline), GMIA v5 (~2013) — none reflect
  post-2020 land-use change. Re-run the classifier when newer inputs land.

---

## Validation (forward)

To validate per-AOI, compare classifier output against:

- Country agricultural census, where available (admin1 statistics on cropping/livestock area).
- LSMS-ISA household surveys (where they cover the AOI).
- Expert review (country team or in-country agronomist).

Drift between EO and census stats > 20 % at admin1 should trigger threshold re-tuning, not
acceptance of the EO surface as ground truth.

---

## See also

- `schema/registers/FS_DIXON_CROSSWALK.md` — Dixon ↔ EO crosswalk reference.
- `methodology/T4_generation_method.md` §2.5 — "Constrain by observed distribution, not modelled
  niche" — same principle applied here.
- `methodology/opportunity_space_T5.md` — `production_gap` uses the classifier output via BIND.
- Tests: `tests/test_farming_system.py`.
