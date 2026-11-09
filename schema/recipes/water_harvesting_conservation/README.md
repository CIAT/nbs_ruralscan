# Water Harvesting and Conservation

This recipe uses the practice ID `water_harvesting_conservation`. T0 defines the practice and the family register describes the siting context for in-situ measures, micro-catchments, runoff catchments, spate harvesting and terracing. Rooftop harvesting has a qualitative-only designation. [Practice definition](T0_nbs_registry.csv) · [Family register](../../registers/FAM_family_registry.csv)

## Suitability

T4 has five mappings on numerical calibration hold. For runoff catchments these cover contributing area, drainage density, runoff potential and stream order. For terracing the hold covers runoff potential. Four also require a matching spatial input. Each mapping preserves its supporting source evidence and the reasons for its hold. The five rows currently supply **zero executable suitability functions**. [Reviewed T4 mappings](T4_suitability_mappings.csv) · [Authored settings and holds](../../recipe_inputs/t4/water_harvesting_conservation/)

Twenty draft mappings from the earlier recipe await evidence review. Their historical values, source cards and release dispositions are linked individually. For clay content, the two reviewed source corrections preserve the native classes and descriptive mean ranks across studies. A family-level response still requires review. [Mapping crosswalk](../../../methodology/audits/t4_six_practice_release_20261109/water_harvesting.md) · [Clay rank comparison](../../../methodology/audits/t4_water_block_20261109/clay_rank_comparison.csv)

## Other recipe tables

| Table | Contents |
| --- | --- |
| [T3](T3_nbs_hazard_farming.csv) | Hazard responses by family and farming context |
| [T6](T6_nbs_scorecard.csv) | Scorecard effects |
| [T6E](T6E_economic_profile.csv) | Economic profiles |

The effect synthesis report records how the evidence contributed to T3, T6 and T6E. The release reader loads compiled tables, authored settings and readiness reports together by version. [Effect synthesis report](T3T6_synthesis_report.json) · [Release guide](../../../docs/RECIPE_RELEASES.md)

The initial worked example came from the water-harvesting design workbook. Rebuild current evidence-based T4 tables with the recipe compiler and regenerate the typed JSON from the CSV. [Design workbook](../../design/RuralNbS_WaterHarvesting_Tables_T0-T7.xlsx) · [Water-harvesting method](../../../methodology/recipes/water_harvesting.md) · [T4 synthesis instructions](../../../.agents/skills/source-command-t4-synthesise/SKILL.md)
