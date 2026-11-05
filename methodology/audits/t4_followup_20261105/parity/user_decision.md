Pete, 5 November 2026: prioritize these six mappings for human review and request a dashboard priority filter/control. Temporary mapping removal was not approved. Live mappings and all evidence remain unchanged. The proposed empty mapping CSV is an unapplied diagnostic proposal, not the selected repair.

## Sequential review — 5 November 2026

### 1. Wetland creation: distance to water

- Mapping: `wetland_management__creation__distance_to_waterbody`.
- Evidence: `ev_wet_distance_to_waterbody_morenomateos10_1`.
- Pete's exact decision: "0-500m optimum = ok" followed by "next".
- Accepted decision: retain the mapping with an optimum interval of 0–500 m. The proposed removal was not approved.
- Provenance: Moreno-Mateos et al. (2010), PDF p. 6, describes approximately 500 m as very suitable; p. 8 gives 450 m as the calibrated low-implementation-cost distance in the same study. The explicit 0–500 m optimum is Pete's review decision, not a newly discovered independent source result.
- This decision does not specify an outer zero-suitability distance or approve pooling with the separate Uuemaa 125 m rule. Those remain unspecified.
- Application status: recorded for the scoped T4 correction/compilation step after this review sequence. No evidence approval flags, review-server decisions or analytical tables changed by this note.
- At this point, the remaining five priority items awaited their individual decisions.

### 2. Drained peatland restoration: artificial canal density

- Mapping: `wetland_management__peatland__drainage_density`.
- Evidence: `ev_wet_drainage_density_sumarga26_1` (source citation: Salmayenti et al., 2026; legacy evidence ID retained).
- Proposal presented: remove the unsupported 1.2 km/km² minimum while retaining observed targeting evidence; the reported 1.2, 2.5 and 1.5 km/km² values are group means, not suitability thresholds. Any numeric mapping requires calibration and actual canal-density data rather than the current runoff proxy.
- Pete's exact response: "hmm ok, but very niche and restricted to peat land restoration practice only not wetland restoration in general."
- Accepted decision: remove the unsupported numeric minimum; retain evidence only for restoration of artificially drained peatlands, under `wetland_management__peatland`. Do not inherit or pool this claim into general wetland creation/restoration, or treat natural drainage density as interchangeable with artificial canal density.
- Preserve the source's combined targeting context: denser artificial drainage and prior high fire-hotspot density. This does not establish a universally increasing suitability curve or a new numerical cutoff.
- Application status: recorded for the scoped T4 correction/compilation step after this review sequence. No analytical tables or evidence approval flags changed by this note.
- At this point, the remaining four priority items awaited their individual decisions.

### 3. Rewetting former-wetland farmland: mean lowest groundwater depth

- Mapping under review: `wetland_management__peatland__water_table_depth`.
- Evidence: `ev_wet_water_table_depth_brouwer26_1`.
- Pete proposed: "0-30 = high 1 / 30-80 = moderate 0.66 / 80-160 = marginal 0.33 / >160 = 0 suitability" and considered farmland rewetting more generalizable than peatland canal density.
- The response clarified applicability to drained former-wetland farmland, rather than arbitrary farmland; the mean lowest groundwater level is the average for the three lowest-water months, not an annual mean or single measurement. Pete then said "next", accepting advancement after that clarification.
- Accepted stepwise rule (depth below ground in cm): [0,30] -> 1; (30,80] -> 0.66; (80,160] -> 0.33; >160 -> 0. Negative depths / surface inundation are unspecified and must not be silently assigned a class.
- Provenance: the first three depth classes and ordinal scores 3/2/1 come from Brouwer et al. (2026), PDF pp. 2–3. The 1/0.66/0.33 normalization and >160 cm zero score are the reviewed scoping adaptation; the zero tail is Pete's screening assumption, not a source-established ecological limit.
- Source scope is hydrological screening for paludiculture. Applying this criterion to rewetting drained former-wetland farmland is the reviewed adaptation, not new evidence of general restoration validity. Preserve that distinction in provenance and context; do not silently rewrite family definitions or apply it to all farmland.
- This decision concerns the water-depth criterion only. It does not approve seepage scores, soil water capacity scores, the source's multiplicative combined rule or an overall suitability threshold.
- Application status: recorded for the scoped T4 correction/compilation step after this review sequence. No analytical tables or evidence approval flags changed by this note.
- Remaining three priority items: awaiting their individual decisions.
