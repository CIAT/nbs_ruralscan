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
- At this point, the remaining three priority items awaited their individual decisions.

### 4. Groundwater seepage: retain the three source classes

- Mapping under review: `wetland_management__peatland__groundwater_seepage`.
- Evidence: `ev_wet_groundwater_seepage_brouwer26_1`.
- Pete requested more context after a four-band proposal including a zero tail. The subsequent explanation presented three source classes and explicitly recommended leaving values beyond 0.5 mm/day unclassified rather than declaring them unsuitable.
- Pete's exact response to that explanation: "I think your table is fine, next".
- Accepted classification: flux < -0.1 mm/day (upward supply) is high; -0.1 through +0.1 mm/day is moderate; > +0.1 through +0.5 mm/day (downward loss) is marginal. Values > +0.5 mm/day remain unclassified. The earlier proposed zero tail was superseded by the clarified recommendation, not approved.
- Provenance: Brouwer et al. (2026), PDF pp. 2–3, hydrological screening for paludiculture. The latest approved table contains qualitative classes; the source assigns ordinal scores 3/2/1. Do not describe a zero tail as source-derived or silently retain the current abs_max=0.5 semantics.
- Context: rewetting drained former-wetland farmland, as discussed for the preceding criterion; not arbitrary farmland or all wetland restoration. This is vertical groundwater flux, not runoff or canal flow. Input data must measure the same quantity and respect the source's negative-upward sign convention.
- This decision does not approve a combined model, automatic extrapolation, or substitution of a runoff proxy for groundwater seepage.
- Application status: recorded for the scoped T4 correction/compilation step after this review sequence. No analytical tables or evidence approval flags changed by this note.
- At this point, the remaining two priority items awaited their individual decisions.

### 5. Restoration-patch area: remove the hard 1 ha minimum

- Mapping: `wetland_management__restoration_rewetting__restorable_patch_area`.
- Evidence: `ev_wet_site_area_russell97_1`.
- Proposal presented: remove the hard 1 ha minimum while retaining the source-specific conditional restoration-priority guidance. Small patches remain eligible; no replacement minimum is established.
- Pete's exact response: "yes, next".
- Accepted decision: remove the unsupported universal `abs_min=1` suitability cutoff. Retain the evidence record and source's conditional priority rule; do not drop the practice or interpret low priority as zero suitability.
- Provenance: Russell et al. (1997), PDF p. 10. Eligible sites within 90 m are considered first; the subsequent size/proximity screening down-prioritizes patches below 1 ha. Authors explicitly describe the 1 ha threshold as arbitrary, with a flood-attenuation rationale. Preserve the source's separate scrub-cover preservation/restoration branch when describing the complete method.
- This decision does not yet approve a correction to the separate 120 m distance mapping or deployment of the full priority algorithm.
- Application status: recorded for the scoped T4 correction/compilation step after this review sequence. No analytical tables or evidence approval flags changed by this note.
- At this point, restoration distance remained awaiting its individual decision.

### 6. Restoration distance: reviewed connectivity preference

- Mapping under review: `wetland_management__restoration_rewetting__distance_to_waterbody`.
- Evidence: `ev_wet_distance_to_waterbody_russell97_1`.
- Pete proposed "0-90 = 1 / 90-120 = (0.66+0.33)/2 = 0.5? / >120 = <0.5". The response proposed an explicit 0.33 for the final band, explained that 0.495 was rounded to 0.5, and distinguished the adaptation from the source's patch-size-dependent priority rules.
- Pete's exact response: "ok next".
- Accepted stepwise scores for distance in metres: [0,90] -> 1; (90,120] -> 0.5; >120 -> 0.33. Replace the hard 120 m zero-suitability cutoff with this nonzero final band.
- Scope: a reviewed habitat-connectivity preference for eligible riparian wetland restoration sites, measuring distance to existing riparian habitat or open water. It is not the water-delivery criterion used for wetland creation, and it does not establish that a site can support wetland conditions.
- Provenance: Russell et al. (1997), PDF p. 10, supplies the conditional spatial prioritisation framework. The simplified three bands and numeric scores are Pete's reviewed adaptation, not source-validated ecological thresholds. The middle score averages priority levels instead of reproducing the original area/proximity branches; do not attribute that averaging to the paper.
- Do not pool this criterion with Moreno-Mateos water-access distances or other contextually different distance thresholds. Do not silently assume a generic river-distance dataset measures distance to both riparian habitat and open water.
- Application status: all six legacy review decisions are now recorded. Analytical correction/compilation and normal review provenance remain pending; this document does not itself set evidence approval flags or deploy mappings.
- Next stage in the agreed sequence: review the 17 active new T4 claims, with the two quarantined Rao claims handled separately.
