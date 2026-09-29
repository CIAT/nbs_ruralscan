# Wetland management — T4 extraction sweep (2026-09-29)

Ruleset **v1.5.1**. Run id `wet_t4_sweep_2026-09`. Extractor: Namita-J / Claude.

## Corpus

| | |
|---|---|
| acquired + cached | 25 |
| **extractable** (`doi_verified = true`) | **12** |
| excluded by the DOI gate | 13 — all lack a DOI entirely; 1 had one blanked after failing Crossref |
| read | 12 |
| **yielded evidence** | **3** |

**This is the thinnest corpus of the five NbS, and the reason is structural.** The wetlands
literature that was screened in is overwhelmingly about what wetlands *do* — methane and CO2
flux, nitrate removal, flood attenuation, fire-hotspot reduction, ecosystem-service framing.
That is `nbs_effect` material, deferred since 2026-09-17. Only three papers state where a
wetland intervention *can go*.

## Yield

**6 units**, 5 with a numeric threshold, across 2 of 5 families.

| family | units | T4 rows |
|---|---|---|
| `restoration_rewetting` | 5 | 2 |
| `peatland` | 1 | 1 |
| `creation`, `constructed`, `coastal` | 0 | 0 |

The usable content comes from **Russell et al. (1997)**, a GIS site-selection method: carry
forward only medium and high topographic-wetness classes, require ≥1 ha of contiguous site,
and stay within 120 m of extant riparian vegetation or open water. The paper is honest that
its 1 ha threshold "was arbitrarily defined", and that is recorded in the evidence.

**Sumarga et al. (2026)** supplies the one peatland row, and it is directionally unusual:
rewetting is *targeted at* high canal (drainage) density — peatlands with dams averaged
2.5 km km⁻² against 1.2 km km⁻² for all peatlands. Dense artificial drainage is what makes a
peatland both degraded and restorable, so the variable **selects** the intervention zone
rather than excluding it. A reviewer should confirm that sign before it reaches MCDA.

## Judgement calls

1. **`harrison_seasia_peat_strategies_2021` was not extracted** even though it states a clean
   threshold — water table maintained 40–60 cm below the peat surface. That is the RSPO best
   practice for **oil palm cultivation on peat**, not for rewetting. Tagging it to the
   peatland restoration family would be borrowing the practice from context, which PICOS
   forbids.
2. **Three families have no evidence at all** — `creation`, `constructed` (`qualitative_only`
   anyway) and `coastal`. `creation` is the notable gap: it is a real family with a real
   corpus, just not in what was screened in.
3. Both units from `balancing_2022_floodplain_reconnection` are directional only (low-gradient,
   large drainage-area settings favour floodplain restoration) — no thresholds.

## New `VONT` entries (`pending_review`)

`topographic_wetness_index` · `restorable_patch_area`.

## Not done

Human QA of the 6 units; the 3 first-pass `benchmark_tier` values; the 13 DOI-gated sources;
and a decision on whether `creation` needs its own discovery round rather than more
extraction from this corpus.

## `creation` discovery round (2026-09-29, run `wet_creation_disc_2026-09`)

The August `creation` peer-reviewed search retrieved **5** papers. This broader multilingual
title search (logged in `SRCH`) retrieved **153**; 46 passed the title screen; **15 were
included**.

- **7 acquired** open-access; 6 DOI-verified (the arXiv preprint's DataCite DOI cannot be
  Crossref-verified, so the gate keeps it out of extraction).
- **8 are gold open access but block automated download** (MDPI, Elsevier, T&F). Queued as
  `webfetch_403_bot_block` for a browser download — **not** paywalled. These include the
  strongest restoration-siting papers found (the CONUS restoration indicator, the Ontario
  suitability index, the LiDAR creation-siting paper).

**First-ever evidence for `creation`: 4 units** from Moreno-Mateos et al. 2010 — very suitable
within ~500 m of a frequently flowing stream (calibrated at 450 m, and given the model's
maximum weight), slope as a restrictive construction-cost factor, and irrigated or
low-activity farmland as the most suitable land use.

The other five acquired papers mostly **map where wetlands are** (classifiers, delineation for
avoiding wet ground) rather than where to restore or create them. PICOS keeps them out: the
practice is not evidenced in the source.
