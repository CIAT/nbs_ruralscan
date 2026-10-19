# The six conflict-split rulings — answered 19 October 2026

Pete answered the `conflict_rows_to_split` decision (see `DECISIONS_PENDING.md` history and
`2026-10-16_class_eligibility_applied.md` for the lead-up). His words are quoted verbatim;
each ruling records what was implemented and where.

## 1 — Highland / high-rainfall production losses (water harvesting)

> "this speaks to where the practice is suitable, should be not be practiced in areas with
> heavy rainfall as leads to waterlogging, I hope this will come out in the T4 analysis.
> I think it can be withheld from the production, but is an important ceveat to performance
> to log if describing the practice."

**Implemented.** New `context.envelope_misfit` tag on units whose AUTHOR attributes the loss
to excess rainfall / waterlogging: `ev_crop_yield_adim16_2`, `ev_crop_yield_adim16_6`,
`ev_crop_yield_roose93_4`, `ev_crop_yield_roose94_3`, `ev_crop_yield_corb20_7`,
`ev_crop_yield_rusin11_3`, `ev_crop_yield_schmidt12_10`. Tagged units are held out of the T6
production class (`partition_voters`, reason `envelope_misfit`), stay in the row's evidence and
prose as a performance caveat, and still vote in T3 hazard cells (there the failure is the
signal). Each stated rainfall ceiling is logged as a deferred T4 suitability pointer
(`pipeline/staging/t4_deferred_pointers_2026-10-19.md`) — T4 extraction stays paused.

## 2 — Minimum tillage is not in-situ water harvesting

> "I have clearly stated before min till alone is not in-siut water harvesting."

**Implemented.** Rule: intervention = minimum / reduced / no tillage ALONE — no water-capture
element (basin, ripline, pit, bund, tied ridge) and no soil-cover component — is not a
water-harvesting practice. 17 units soft-dropped (`wrong_practice`, restorable, review_log
2026-10-19): the adim16 minimum-tillage arms (4), both Pittelkow no-till meta-analyses
(pittel15 overall/NT-alone/humid = 3; pitt15 all 5 — that paper is no-till-alone throughout,
its source row stays with an empty `vars_extracted`), corb20_5 (tillage-alone null), the
boil19 reduced-tillage arms (2), and the roose 2010 reduced-tillage/direct-seeding pair (2).
**Stays, per D5 (2026-10-06):** conservation tillage that BUILDS capture structure (ripper,
basin tillage, tied ridging), mulching, and CA bundles with residue cover (corb20 bundles,
pittel15_2/5, rusin11, stew18, boil19 ground-cover arms).

## 3 — Forest-restoration water stress: downstream users decide

> "what is more relevant? it is the impacts on downstream users who might benefit (what
> problem might this solve in the opportunity space?). Infiltration does not matter if
> groundwater levels and recharge do not improve as that is what affects discharge for
> agricultural, industrial or muncipal water use."

**Implemented in XW.** `soil_permeability → water_stress` route REMOVED (infiltration is a
mechanism, not the outcome the priority scores; the units stay registered and the prose may
cite the mechanism). `groundwater_recharge_potential` re-routed `water_stress →
catchment_water_yield` (recharge → discharge → downstream users), component 0.7. Variable-level
change: it moves recharge units of every NbS (water harvesting 20, wetland 4, agroforestry 2,
forest restoration 1), consistent with the ruling's framing.

## 4 — Plantations are not forest restoration

> "plantations should be a separate category of forest restoration, as an ecologist I would
> treat them as tree frarming and not forest restoration, we need to make sure plantation is
> aligned with NbS. In general we would expect the restoration of natural forests to improve
> biodiversity strongly (diversity and connectity metrics at different spatial or temporal
> scales). How would a plantation restore anything? it is not represenative of a natural
> baseline we are trying to return to. Planttations could potential provide some
> meta-population connectivity in the lanscape, but still pretty shitty habitat (unless using
> indigenous and diverse plantings to have a multi-use more bio friendly plantation)."

**Scoped as its own change (next PR).** A `forest_restoration__plantation` family split from
`active_planting`, with a unit-level audit (clear cases: farley05 ×6, inrae23 biodiversity ×6,
busch24 plantation arms, busch19_2, lagan09 ×13, keyes97 ×3, iufro18 plantation units, ieg18
smallholder plantations). **Open for Pete + MFL** (`plantation_rollup` in `open_decisions.csv`):
does the plantation family stay inside the forest-restoration roll-up at all, or is it parked
as tree farming whose NbS alignment is unproven — with the "indigenous and diverse plantings"
condition as the possible gate?

## 5 — Boundary-planting drought conflict stays, with a narrative duty

> "ok leave, but we will need a good narrative description of each outcome aggregation
> strongly linked to evidence chain."

**Kept as `conflicting_evidence`.** The standing requirement is recorded in the prose
standard (`recipe/prose.py`): every aggregated outcome carries a narrative that names its
sides and cites the evidence ids that carry them — no class without its chain.

## 6 — Wetland heat: no rural receptor, no claim

> "again what problem in the opportunity space is actually being addressed in-situ for rural
> propulation? are they actually in the wetland? I not getting the logic here."

**Implemented.** New lookup `schema/lookups/xw_route_policy.csv` (per-NbS route exclusions;
routes default to included). `microclimate_buffering → heat_stress` (T3) and `→
heat_stress_hazard` (T6) are OFF for `wetland_management`: the pooled units measure the
wetland's own surface/air temperature against an adjacent alfalfa field — the cooled place is
the wetland itself. The rows disappear rather than claim heat-stress relief; the route returns
if a study shows cooling where people or crops actually are. Agroforestry shade keeps its
route (it cools the crop and the worker in place).
