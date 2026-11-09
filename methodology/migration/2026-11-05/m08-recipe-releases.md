# Separate recipe settings and load one complete release

This M07/M08 change follows PR #633. CIAT retains the working registers. Compilation and release checks run against private copies while evidence review continues. No public repository import or external runtime pin update is part of this step.

## Two kinds of files

The T4 compiler previously read weights, gates, scenarios and carried review decisions back from the table it was rebuilding. Each maintained practice now declares its authored files and its optional run policy and effect prose. The compiler can build a candidate without its previous generated mapping CSV. Reconciliation separately requires the audited mapping table and the full approved corpus. Archived snapshots retain their original compilation path. [Authoring instructions](../../../schema/recipe_inputs/t4/README.md)

Every selected practice contributes its T0 definition, declared authored settings, four generated tables, effect synthesis report and T4 readiness report to a local release. The publisher checks source and compiler fingerprints, typed companions, reproduced rows and reports, and the existing run-policy checks. Source settings and generated tables occupy separate directories. One atomic pointer selects the complete generation; readers may keep reading the previous ID. [Commands and reader API](../../../docs/RECIPE_RELEASES.md)

## Rehearsal on the PR #633 baseline

Full-corpus comparisons used the same inputs as commit `470945e0`. The baseline and split T4 compilers agreed on the output of all six practices, including existing refusals. All 35 T4 output files and all six family-result sets matched; the 24 T3/T6/T6E table and report files also reproduced byte for byte. [Comparison hashes](m08-recipe-release-parity.json)

| Practice | Audited T3 rows | Audited T4 rows | Audited T6 rows | Audited T6E rows | Complete local release |
|---|---:|---:|---:|---:|---|
| Agroforestry | 95 | 26 | 112 | 16 | Reconciled |
| Forest restoration | 56 | 0 | 71 | 16 | Reconciled, T4 has no accepted rows |
| Wetland management | 26 | 4 | 64 | 15 | Reconciled |
| Mangrove restoration | 12 | 0 | 14 | 4 | Missing T0 practice identity |
| Riparian buffer | 7 | 2 | 22 | 2 | Reviewed evidence differs from the audited T4 distance-to-waterbody mappings |
| Water harvesting and conservation | 92 | 25 | 111 | 21 | Reviewed evidence differs from multiple audited T4 mappings |

Requesting all six together reports the holds and keeps the current release intact. Explicitly selecting the three reconciled practices produces a 501-row, four-table collection. The counts exclude the T0 definitions, settings and report entries. Continuity tests cover reading an earlier ID through a pointer change, concurrent publishers, interrupted publication, stale source files, unsupported formats and damaged generations.

## First six-practice release, 9 November 2026

The default release now reconciles every registered practice against the same reviewed corpus. The 791 analytical rows include five water-harvesting records retained to document calibration holds.

| Practice | T3 | T4 | T6 | T6E |
|---|---:|---:|---:|---:|
| Agroforestry | 95 | 26 | 112 | 16 |
| Forest restoration | 56 | 0 | 71 | 16 |
| Mangrove restoration | 12 | 0 | 14 | 4 |
| Riparian buffer | 7 | 0 | 22 | 2 |
| Water harvesting and conservation | 92 | 5 | 111 | 21 |
| Wetland management | 26 | 4 | 64 | 15 |
| **Total** | **288** | **35** | **394** | **74** |

Mangrove T0 covers planting and ecological restoration in one tidal-coastal family. Its establishment period, time to a specified benefit and recurrent cost class require local inputs. T6E provides costs with their study context. [Mangrove definition and sources](../../families/mangrove.md)

Neither earlier riparian distance rule had approved numeric support. The six source records remain available for review. For water harvesting, the five held mappings have zero selectable functions, and four also require a matching spatial input. All 49 evidence records behind the 20 earlier draft mappings remain accessible in their review batches. The release preserves the source-specific clay comparison without applying a shared 55% cutoff. [Riparian review](../../../schema/recipes/riparian_buffer/README.md) · [Water-harvesting mapping crosswalk](../../audits/t4_six_practice_release_20261109/water_harvesting.md)

## Next migration step

Define the acceptance and external runtime contract for a pinned analytical release, including provenance, readiness, full-corpus validation and redistribution rights. Preserve the existing runtime pin while that contract is rehearsed.
