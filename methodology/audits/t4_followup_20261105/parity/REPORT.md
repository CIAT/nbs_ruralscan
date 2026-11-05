# Wetland recipe parity diagnosis

Six mismatches reproduced. Approved-only compiler emits zero wetland mappings; all six live keys cite reviewer_ok=false evidence. None of those six evidence IDs has an applied review-log entry. Four source records say swept, a legacy extraction-completion label which is not human evidence approval. No evidence approval was inferred from source tier or source status.

## Why blind regeneration or blanket approval is unsafe

Replacing the live recipe with the approved-only trial would remove all six rows. Including unreviewed evidence produces eight diagnostic rows, introducing additional keys and retaining several unsupported legacy numeric interpretations. Neither trial is a deployable repair. Two distance variables are suppressed by the compiler because pooled bounds contradict each other; four of the six live keys still compile diagnostically despite semantic problems in their numeric evidence.

## Exact key-by-key findings

### wetland_management__creation__distance_to_waterbody

Evidence `ev_wet_distance_to_waterbody_morenomateos10_1`; source `wet_optimal_location_created_mediterranean_2010`, PDF6. Approved trial: `unresolved_review`. Unreviewed diagnostic: `inconsistent_bound_order`.

Source PDF6 distinguishes approximate500m very-suitable distance from water delivery cost/pumping; no outer zero-suitability tail. Diagnostic pooling conflicts with Uuemaa125m outer bound, while source companion450m is a calibration variant.

**Proposed decision:** Keep scoped direction and native approximate class; review450vs500 within source and separate Uuemaa system before pooling. Decide whether cost-driven distance belongs structural siting or operational guidance; do not silently create missing tail.

### wetland_management__peatland__drainage_density

Evidence `ev_wet_drainage_density_sumarga26_1`; source `tropical_peatland_restoration_reduces_fire_2026`, PDF5. Approved trial: `unresolved_review`. Unreviewed diagnostic: `parameter_contributor`.

Source PDF5 reports1.2km/km2 as observed mean of all peatlands, not minimum restoration suitability.2.5km/km2 is mean treated canal-dam area and1.5near wells. Dense drainage plus prior fire activity describes actual targeting, not an ecological exclusion. Existing scs_cn_runoff_composite binding is a runoff proxy, not an observed canal-density layer.

**Proposed decision:** Retain observed targeting direction and literal means; propose removal of unsupported abs_min only through review. No numeric runtime threshold supported here. Request observed canal dataset binding if retained as targeting variable.

### wetland_management__peatland__water_table_depth

Evidence `ev_wet_water_table_depth_brouwer26_1`; source `page_nl_paludiculture_crop_suitability_model`, PDF3. Approved trial: `unresolved_review`. Unreviewed diagnostic: `parameter_contributor`.

PDF3 Table1 is paludiculture hydrological screening: mean lowest groundwater level classes0–30high,30–80moderate,80–160marginal.160 is endpoint of marginal class, not demonstrated zero; source multiplies three discrete scores and selects product>=8. Generic trapezoidal fall-to-zero is not that method.

**Proposed decision:** Retain native ordinal classes, direction and Netherlands paludiculture scope. Human decision: applicability to generic peatland rewetting versus paludiculture-only model referral; if a runtime class model is desired, approve scores, tails and combined rule separately. Do not approve current abs_max semantics by approving quote.

### wetland_management__peatland__groundwater_seepage

Evidence `ev_wet_groundwater_seepage_brouwer26_1`; source `page_nl_paludiculture_crop_suitability_model`, PDF3. Approved trial: `unresolved_review`. Unreviewed diagnostic: `parameter_contributor`.

PDF3 Table1: upward<-0.1mm/d high, -0.1to0.1neutral moderate,0.1to0.5downward marginal.0.5 is marginal-class endpoint, not stated zero. Source discrete product model differs from live trapezoid.

**Proposed decision:** Same paludiculture applicability decision as water table. Preserve signed seepage and ordinal classes; require explicit tail/score semantics and appropriate binding before execution.

### wetland_management__restoration_rewetting__restorable_patch_area

Evidence `ev_wet_site_area_russell97_1`; source `gis_riparian_siting_russell_1997`, PDF10. Approved trial: `unresolved_review`. Unreviewed diagnostic: `parameter_contributor`.

PDF10 applies1ha sieve only after separating high-priority sites within90m; remaining<1ha areas receive low priority.1ha explicitly arbitrary, rationale flood attenuation. Universal abs_min loses conditional rule and converts low priority to exclusion.

**Proposed decision:** Retain source conditional restoration-priority method; ask whether remove this live structural cutoff while preserving evidence and source priorities. Any new minimum ecological area requires separate evidence/approval.

### wetland_management__restoration_rewetting__distance_to_waterbody

Evidence `ev_wet_distance_to_waterbody_russell97_1`; source `gis_riparian_siting_russell_1997`, PDF10. Approved trial: `unresolved_review`. Unreviewed diagnostic: `inconsistent_bound_order`.

PDF10 says>120m is low-priority restoration, not unsuitable;90m defines first high-priority branch. Current abs_max120 turns priority into exclusion. Diagnostic pooling also combines Medland250/500 and Qiu300 values with different contexts.

**Proposed decision:** Retain full90m/120m priority branching and observed target definition; decide removal from structural runtime, preserve method referral. Do not pool these priority/feasibility contexts into a single distance envelope.

## Precise decision package

Recommended: keep the parity hold and evidence records; approve neither a blanket rebuild nor blanket approval of six numeric claims. Pete can approve a scoped repair plan to retire the unsupported structural mappings while preserving their source information: drainage mean as targeting observation, Russell branches as priority method, Brouwer as bounded paludiculture class model, Moreno as context-specific water-access guidance. Paludiculture applicability and water-delivery-cost routing are explicit scope choices. Subsequent EV corrections need normal review before compiler regeneration. This report makes no removal, reclassification or approval.

Shared metadata limits: live paper_support_pct values6.8/11.4/16.1 and corpus_n24/14/9 are historical; current compiler has unknown screened membership and leaves support denominator unknown. Do not transfer the historical weighted percentages into current raw n/N reporting. Source quality is not MCDA weight. Existing equal/default weights are not newly endorsed.

## Diagnostic pooling IDs

- Creation distance: ev_wet_distance_to_waterbody_morenomateos10_1 (500m), ev_wet_distance_to_waterbody_morenomateos10_2 (450m companion), ev_wet_distance_to_waterbody_uuemaa18_1 (125m maximum). Combining optimum450/500 with maximum125 yields inconsistent bounds.
- Restoration distance: ev_wet_distance_to_waterbody_russell97_1 (120m priority), ev_wet_distance_to_waterbody_medland20_1 (250m rank), ev_wet_distance_to_waterbody_medland20_2 (500m), ev_wet_distance_to_waterbody_qiu20_1 (300m priority). Pooling endpoints loses context and yields inconsistent bounds.

## Reproduction and constraints

Reviewed trial: trial/ and trial-report.json. Unreviewed diagnostic only: unreviewed-diagnostic/ and unreviewed-report.json. Targeted native page text retained beside diagnosis.json; review_history.json is empty. FAM IDs unchanged. No live CSV/JSON, approval, FAM, git or runtime edits. Compiler input hashes retained in reports; no new discovery or extraction. This diagnosis is not a full re-extraction of the four legacy papers.
