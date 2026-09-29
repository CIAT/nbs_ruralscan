# Water harvesting & conservation — T4 extraction sweep (2026-09-29)

Ruleset **v1.5.1**. Run id `wh_t4_sweep_2026-09`. Extractor: Namita-J / Claude.

## Corpus

| | |
|---|---|
| acquired + cached | 39 |
| **extractable** (`doi_verified = true`) | **35** |
| excluded by the DOI gate | 4 |
| read | 35 (7 read in full after a threshold-signal scan across all 35) |
| **yielded evidence** | **7** |

## Yield — the best of the three sweeps

**25 units, 18 of them (72%) carrying a numeric threshold** — the highest numeric yield of any
sweep so far (forest restoration 46%, riparian ~14%). The reason is the corpus: water
harvesting has a mature GIS/MCDA siting literature, and those papers publish **explicit
per-structure specification tables** rather than narrative findings.

| family | units | T4 rows |
|---|---|---|
| `runoff_catchment` | 14 | 5 |
| `terracing` | 8 | 3 |
| `in_situ` | 2 | 2 |
| `micro_catchment` | 1 | 0 |
| `rooftop`, `spate` | 0 | 0 |

Highlights:

- **Kadam et al. (2012)** and **Singh et al. (2017, after Jha)** both publish per-structure
  criteria — slope, catchment area, stream order, soil texture, land cover for farm ponds,
  check dams, percolation tanks and gully plugs. They agree on the shape (storage structures
  need gentle slopes, gully plugs sit on the steep runoff-generating ground) and differ on the
  numbers, which is exactly what the weighted median is for.
- **Krois & Schulte (2014)** gives the only evidence that separates **terraces from bunds** on
  the same axis: terraces optimal at 18–30°, bunds optimal below 2–5°. The same variable runs
  in opposite directions for two families of the same NbS.
- **Kahinda et al. (2008)** bounds the practice on both sides: RWH is not worth implementing
  below 100 mm/year or above 1000 mm/year, within an aridity (rainfall:PET) window of
  0.05–0.65.

## The unit guard earned its place

Three units were **refused** by the conversion guard added in the riparian work, and the
refusals are informative rather than noise:

1. `soil_depth_to_bedrock` — Krois states depth in **m** against a canonical **cm**. This is a
   real conversion, so `m->cm` was declared in `VONT` and the row now reconciles both sources
   (`abs_min` 15 cm from Chen, `opt_low` 100 cm from Krois).
2. `catchment_area` — Boers (1986) expresses the micro-catchment constraint as a **transport
   distance** (<100 m from runoff area to infiltration basin), not an area. Refused, and
   rightly: it is a different quantity wearing the same variable name. **Reviewers to decide**
   whether micro-catchment needs its own distance variable.
3. `soil_texture` — Krois gives **% clay**, the canonical unit is a texture **class**. Also a
   semantic clash, not a rescale. `soil_texture_hsg` already exists; a `clay_content` variable
   may be the right answer.

Note also that slope evidence arrives in **both percent and degrees**; the engine's existing
percent↔degree conversion handled it (Kadam's 2–20% becomes 1.1–11.3°), which is why the
`runoff_catchment` slope row reconciles three sources.

## Not done

Human QA of the 25 units; the 7 first-pass `benchmark_tier` values; the 4 DOI-gated sources;
`rooftop` and `spate` have no evidence (`rooftop` is `qualitative_only`, `spate` is a genuine
gap). 28 of the 35 read sources yielded nothing — mostly agronomic trials and meta-analyses
of yield or runoff *effect*, which is deferred material.
