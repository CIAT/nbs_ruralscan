# ANR proximity: review decision and recipe interpretation

6 November 2026. Evidence: `ev_fr_distance_forest_shono07_20261105`; Shono et al. (2007), PDF p. 2 / printed p. 621. Family: `forest_restoration__assisted_regeneration`.

Pete approved keeping the claim qualitative and requested that the final recipe interpret it spatially, suggesting degraded or recently lost forest near remnant patches. This approves qualitative retention and an explicit recipe implementation requirement; no distance cutoff, loss-age window, numerical score, dataset binding or executable eligibility mask is approved.

## Proposed spatial interpretation for the final recipe

1. **Candidate land:** observed degraded forest, former forest with recent loss, or regrowth trajectories consistent with forest restoration. Preserve the class and disturbance date rather than conflating degradation, loss and regrowth. Recent loss is one candidate signal, not a necessary condition for all ANR sites.
2. **Remnant seed sources:** contemporary observed remnant forest patches, with natural forest distinguished from plantations/tree crops where data allow. Calculate distance to the nearest relevant patch edge; keep the continuous distance and patch identity. If the candidate lies within a degraded patch, distinguish on-site remnant trees from adjacent seed-source patches so a zero distance is interpretable.
3. **Regeneration potential:** a separate observed-regrowth or local regeneration check. Shono's ANR guidance requires existing regeneration; forest-loss detection alone does not establish this. Satellite-detected regrowth can support screening but does not establish seedling abundance or species composition. Unknown regeneration remains an explicit verification need rather than automatic suitability or rejection.
4. **Current land use and eligibility:** retain current-use context; recent loss may now be productive agriculture, settlement, plantation or another use. Do not silently treat all forest loss as land available for forest restoration. Apply only separately approved land-use and legal constraints; record unresolved eligibility.
5. **Output before calibration:** a candidate restoration footprint annotated with degradation/loss/regrowth class, time since disturbance, remnant-forest distance and regeneration-evidence status. No 0–1 proximity score, default buffer, automatic exclusion of distant land or composite suitability surface follows from this claim. Display near/far classes only if their boundaries are separately agreed; otherwise retain raw distance.

Distinguish the source claim (nearby remnant forest supports seed supply and continued succession) from this proposed spatial implementation. Supplemental planting remains a possible response when regeneration/seed supply is insufficient. It does not authorize automatic reassignment between ANR and active planting.

## Dataset candidates, not approved bindings

- **JRC Tropical Moist Forests:** a strong candidate within its moist-tropical domain because the 30 m products distinguish disturbance, deforestation and regrowth and supply annual histories. Producer offers Earth Engine access. Check the pinned release, class definitions, recent-event uncertainty and AOI coverage. It does not cover every tropical dry-forest or non-tropical ANR setting. [Producer documentation](https://forobs.jrc.ec.europa.eu/TMF/data), checked 6 November 2026.
- **Hansen Global Forest Change:** broader coverage and a loss-year indicator can supply a disturbance-history layer, but loss is stand-replacement disturbance rather than proof of degradation, regeneration, natural-forest identity or restoration availability. Baseline canopy is year 2000; gain remains 2000–2012 even in the current release. Do not reconstruct present canopy by subtracting binary loss and adding binary gain to percentage canopy. A contemporary forest/remnant layer and current land-use evidence are still needed. [Producer catalog](https://developers.google.com/earth-engine/datasets/catalog/UMD_hansen_global_forest_change_2025_v1_13), checked 6 November 2026.
- **National/local forest-condition and regeneration layers:** prefer these where their dates, classes, resolution and validation fit the target landscape. No suitable local product is selected without a target AOI and metadata review.

These pointers do not ingest a dataset or create new source evidence. Existing T1/BIND entries remain unchanged. Required next recipe decisions: remnant-forest definition; candidate land-use eligibility; recency meaning; treatment of unknown regeneration; any eventual proximity response. User approval of the qualitative claim does not settle those choices.

## Application and verification

Normal review handling applied this approval to the evidence register and appended one review event. Only `reviewer_ok` and attribution changed; all 6,369 records and original source content remain. Isolated approved-only forest synthesis retains Shono as `selection_only` and emits zero numeric mappings. The ANR family section links this final-recipe requirement. Dataset bindings and analytical mappings are unchanged.
