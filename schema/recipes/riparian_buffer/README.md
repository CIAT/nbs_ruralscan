# Riparian buffer recipe

The T0 definition covers planted and natural/restored riparian buffers. Both families use watercourse proximity to describe their linear footprint. The reviewed T4 compilation currently contains zero calibrated mappings for either family. Readers can still use the T3 hazard responses, T6 scorecard and T6E economic profile included with this recipe.

## Why the distance thresholds were withdrawn

The September 2026 synthesis produced two provisional distance-to-waterbody mappings. All six evidence units listed in those mappings still await review. Their original quantities describe different uses of distance.

| Family | Previous provisional rule | Source evidence retained in the register |
| --- | --- | --- |
| Natural/restored | 50–210 m | Zhao used a 210 m study boundary. Dala-Corte estimated a 50 m reserve width per bank for biodiversity protection. De Mello used a 30 m statutory buffer in its study. |
| Planted | Up to 30 m | Schultz described minimum widths for three buffer zones. Tiwari used a 30 m extent for groundwater discharge hotspots. Cole reported widths for controlling different pollutants. |

These sources remain available for assessment. The original synthesis and its decision to express watercourse distance in metres are documented in [PR #249](https://github.com/CIAT/nbs_ruralscan/pull/249). The two [authored distance weights](../../recipe_inputs/t4/riparian_buffer/mapping_settings.csv) apply only when an evidence-based mapping compiles.

## What the review supports

For natural/restored buffers, Witing's 100 m corridor (50 m per bank) defines the area evaluated in the study. Its urban and water exclusions corroborate the shared terrestrial eligibility rules. [Corridor review](../../../methodology/audits/t4_followup_20261106/witing_corridor_decision.md) · [Eligibility review](../../../methodology/audits/t4_followup_20261106/witing_eligibility_decision.md)

For planted buffers, Bentrup and Kellerman used total corridor widths of 80, 100 and 120 m for stream orders 1, 2 and 3 to inventory existing riparian remnants. Both records describe the same planning method. Numeric suitability cutoffs for either family still need evidence and review. [Stream-order and corridor review](../../../methodology/audits/t4_followup_20261106/bentrup_planning_method_decision.md)

Family-level screened-source membership is unknown. The approved compilation therefore reports source counts without prevalence percentages. Its full disposition report can be rebuilt alongside the CSV and family JSON files. [T4 synthesis workflow](../../../.agents/skills/source-command-t4-synthesise/SKILL.md)

## Spatial inputs and effect tables

MERIT Hydro (approximately 90 m) is the default global stream-network binding. A band as narrow as 30 m requires finer local hydrography. The T1 catalogue records dataset limitations and BIND records the available alternatives. [Dataset bindings](../../registers/BIND_dataset_binding.csv)

The effect synthesis report accompanies T3, T6 and T6E. Unresolved water-quality mappings, economic denominators and other findings from the pilot are recorded in the [effect evidence follow-ups](../../../methodology/effect_evidence_followups.md).
