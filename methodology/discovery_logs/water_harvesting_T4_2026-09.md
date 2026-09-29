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

## Deep pass (2026-09-29, run `deep_pass_2026-09`) — **+32 units, 25 → 57**

A second, full-variable pass over all 35 extractable sources, with bundles regenerated using
`full_tables=True` (PR #252). The first pass lost most of its yield to two things, both now
measured: **18% of passages arrived as `[table truncated]`**, and 28 of the 35 papers had been
screened with a regex rather than read. Siting evidence in this literature lives in tables.

New sources: Karimi 2019 (full AHP criteria table — invisible in the first pass), Vema/Singh
2019 (fuzzy **membership-function parameters**, directly usable trapezoids), Al-Abadi 2017,
Mahmoud 2021 (check-dam weights and stream-order scores), de Winnaar 2007, and an adoption
study giving bund adoption determinants (extension, credit, farm size → `operational_risk`).
Re-reads of Kahinda 2008 and Singh 2017 recovered their ranking tables, split by **in-field
versus ex-field RWH** — which want opposite things: in-field peaks at 200-400 mm and 15-35%
clay, ex-field at 600-800 mm and 35-55% clay.

`runoff_catchment` now reconciles **slope across 6 sources (58% support)** and runoff potential
across 5 (50%).

**Two findings for review.** (1) Drainage density runs in **opposite directions** across
sources: low is best for RWH potential (Karimi, Singh) but high is best for check dams
(Mahmoud 2021 — high density means more runoff). Both are in `runoff_catchment`. (2) That
family mixes **storage** structures (farm ponds, check dams — want low permeability) with
**recharge** structures (percolation tanks — want high permeability). Vema 2019 states both;
only the storage requirement was extracted, because encoding opposite requirements in one
family would make the synthesised median meaningless. **Recommend splitting the family.**

One earlier unit was re-tagged: Krois 2014's % clay had been recorded as `soil_texture` (a
class variable); it is now `clay_content`, a new `VONT` variable.


## DOI-unblocked pass (2026-09-29)

PR #253 recovered DOIs printed on 21 cached library PDFs (Crossref round-trip, confirmed at PR
review; Nyamadzawo 2013 was rejected in review because the library file is the wrong paper,
and one FR row was a duplicate of Zomer 2008). The remaining sources were re-read with
full-table bundles. Most are effect or impact studies (T3/T6 material, deferred), so they
yield no T4 rule.

- **Kiboi et al. 2017 — 1 unit, `in_situ`**: tied ridging performs best on coarser semi-arid
  soils; on clay it can induce waterlogging and then erosion (citing FAO 1993).
- Screened, no T4 rule: the 2018 study of terraces mitigating the 2015 Ethiopian drought
  (effect only). Nyamadzawo 2013 is back in `pending`: the library PDF is the wrong paper, so
  it needs re-acquisition by title.
