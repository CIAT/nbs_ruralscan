# Forest restoration — T4 extraction sweep (2026-09-29)

Ruleset **v1.5.1**. Run id `fr_t4_sweep_2026-09`. Extractor: Namita-J / Claude.
Companion to the `SRCH` protocol rows (discovery was logged earlier); this log covers the
**extraction** pass over the already-screened corpus.

## Corpus

| | |
|---|---|
| acquired + cached (library PDFs) | 41 |
| **extractable** (`doi_verified = true`) | **32** |
| excluded by the DOI gate | 9 — all have no DOI at all, none has a mis-stitched one |
| read | 32 |
| **yielded evidence** | **12** |

The 20 papers that yielded nothing were consistently outcome or ecology studies — soil-carbon
meta-analyses, sediment yield, species seed biology, biomass recovery curves, survival trials.
That is `nbs_effect` material, deferred since 2026-09-17, so it was not extracted and was not
relabelled into a live role. Roughly **one third of the FR corpus is T4-useful**.

## Yield

**30 units** — 22 `structural_suitability`, 8 `operational_risk`. **14 (46%) carry a numeric
threshold**, across 15 distinct variables.

| family | units | synthesised T4 rows |
|---|---|---|
| `passive_regeneration` | 16 | 4 |
| `active_planting` | 11 | 5 |
| `assisted_regeneration` | 3 | 0 |

The headline row is `distance_to_forest` for passive regeneration: **6 independent sources**,
60.5% paper support — the best-evidenced T4 row in the register. It also carries **±60%
uncertainty**, because the sources disagree by scale rather than in direction: Chazdon &
Guariguata give 100 m (remnant patches) and 200 m (large remnants), Shive 150 m (post-fire
seed kernel), Williams 300 m, Bukoski and Barros both 5 km (landscape screens). The weighted
median resolves to 5 km with the spread carried honestly. Worth a reviewer's eye on whether
the local-scale and landscape-scale claims belong in one row.

Three sources independently give a canopy-cover ceiling for the opportunity space — 25%
(Cook-Patton), 30% (Zomer), 30% (Busch, the UNFCCC definition).

## Judgement calls a reviewer should check

1. **`reforest_water_yield_drought_risk_2022` was NOT extracted.** It screens basins on water
   stress index > 0.2, **aridity index < 0.65** (matching Zomer's threshold from the opposite
   direction) and water-yield decline > 5%. The mechanism is reforestation's downstream effect
   on water yield — `nbs_effect`, deferred — so extracting it would have meant relabelling
   deferred material into a live role. Recover it when T3/T6 return.
2. **One unit auto-quarantined, believed a false positive.**
   `ev_fr_distance_to_forest_williams24_1` (98.1% of high-potential cells within 300 m of a
   forest edge) trips `off_scope:study_site` because the sentence contains "across the study
   region". Every span carrying the 300 m figure contains that phrase, so it cannot be
   re-sliced clear. **Flagged for re-open in the QA queue.** Williams still contributes its
   directional claim (`…williams24_2`), which is active.
3. **Two Barros units were auto-quarantined and fixed, not overridden.** Their quotes opened
   with "forest cover increased in the landscape", which reads as `trend_description`. The
   rule sentence follows it, so the quotes were re-sliced to start at "To generate the
   regeneration potential in the IRB…" — both numbers retained, signal cleared, rows active.
4. **`distance_to_plantation` synthesises a row with no support figure.** It is
   `operational_risk`, and support is measured over structural-suitability candidates only —
   expected behaviour, not a bug.
5. **`assisted_regeneration` produced no T4 row** from 3 units: all three are qualitative
   (road access, labour, a land-cover mask). The family has no threshold evidence yet.

## New `VONT` entries (both `pending_review`)

`distance_to_plantation` · `population_density`.

## Not done

Human QA of the 30 units; sign-off on the 12 first-pass `benchmark_tier` values; the
`/sweep-retro` retrospective; the 9 DOI-gated sources.

## Deep pass (2026-09-29, run `deep_pass_2026-09`) — **+5 units, 30 → 35**

Full-variable re-read of all 32 sources with whole tables. **Much smaller gain than water
harvesting**, and the reason is the corpus rather than the method: the first pass had already
caught the T4 content, and the remainder is outcome ecology. The estimate of +10-15 was too
high.

New: a **75% slope ceiling for planting** (Oliveira 2026 — a paper the first pass wrongly
wrote off as results-description), a protected-area hard mask (Zomer 2008), local forest
density within 1 km as a positive driver of natural regeneration (Williams 2024), and two
enabling-environment units from Chazdon & Guariguata — a **legal clearing threshold** (in Pará,
regrowth under 10 m²/ha basal area may be legally cleared, so passive regeneration is at risk
until it crosses it) and the need to compensate regeneration stewards.

`landscape_forest_cover` is a new `VONT` variable, deliberately separate from
`tree_canopy_cover`: on-site canopy must be LOW (<25-30%) for land to be restorable, while
surrounding forest being HIGH is good. One variable would carry opposite signs.


## DOI-unblocked pass (2026-09-29)

PR #253 recovered DOIs printed on 21 cached library PDFs (Crossref round-trip, confirmed at PR
review; Nyamadzawo 2013 was rejected in review because the library file is the wrong paper,
and one FR row was a duplicate of Zomer 2008). The remaining sources were re-read with
full-table bundles. Most are effect or impact studies (T3/T6 material, deferred), so they
yield no T4 rule.

- **del Campo et al. 2021 — 1 unit, `active_planting`, species_specific (*Pinus pinaster*)**:
  survival improves only where soil depth is above 30–35 cm. Routed out of the practice
  surface by `claim_scope` and kept for the species layer.
- **Fahrudin et al. 2024 — 1 unit, `active_planting`**: planting targets are defined as
  non-forested or low-forest-cover land (a land-cover inclusion rule).
- Screened, no T4 rule: Cao 2010 (the only criterion is a programme-eligibility rule), the
  IUFRO climate-adaptive guidelines (727 pages — forest *definitions*, nursery and species
  guidance; no practice-level siting threshold), the 2007 Scottish farmland hotspots (benefit
  weights, not suitability), the 2021 large-seedling meta-analysis, the 2023 planting-methods
  study, and the 2008 portfolio-theory study.
