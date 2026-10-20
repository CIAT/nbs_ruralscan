# Agroforestry T4 handoff for Diego

Prepared 20 October 2026. Pilot testing belongs to Diego. Haiti is the selected pilot country; no raster run has been performed. This handoff supplies reviewed tables and their dependencies, not a complete M1 runner.

## Start here

**Authoritative table: `schema/recipes/agroforestry/T4_suitability_mappings.csv`**, with generated JSON beside it. Current contents: **17 rows = 1 numeric biophysical rule + 7 categorical host gates + 9 retained operational/design rows**. CSV is the editable source; JSON is generated.

Do not substitute `T4_agroforestry__<family>.json` synthesis intermediates or the historical October 19 tables for this audited live table. They are deliberately omitted from the package. Do not blindly re-run the legacy synthesis command over this reviewed snapshot; reconcile resulting changes against the audit first.

## Tables and dependencies

| File | Purpose |
|---|---|
| T4_suitability_mappings.csv / .json | Reviewed live suitability mappings |
| T1_data_registry.csv / .json | Dataset identifiers, locations, units and limitations |
| BIND_dataset_binding.csv / .json | Context-specific dataset resolution and upload gaps |
| VONT_variable_ontology.csv / .json | Variable definitions and scale/context metadata |
| FAM_family_registry.csv / .json | Families and spatial product types |
| EV_evidence_register.csv / .json | Evidence records, review status and quotations |
| SRC_source_register.csv / .json | Source citations and team library references |
| T7_geographic_context.csv / .json | Geographic context definitions |
| categorical_current_t4.csv | Expanded human-readable class mappings |
| categorical_source_classes.csv | Source-class reconciliation, including unresolved evidence |
| dataset_bindings.csv | Required host inputs and configured datasets |
| README audit + record_reconciliation.csv | Why evidence entered or stayed outside T4 |

Shared registers are copied in full to preserve identifiers and avoid creating divergent, hand-filtered registries. Source PDFs and raster data are not included.

## Current rules to implement

| Family | Current host rule | Remaining input |
|---|---|---|
| Planted silvoarable | WorldCover cropland; grassland only with confirmed ungrazed forage | Optional forage-management mask for grassland branch |
| Regeneration farmland | Cropland; grass/shrub/bare require agricultural/fallow/former-farmland context | `farmland_context` for non-cropland branches |
| Silvopastoral | GPW cultivated OR natural/semi-natural grassland AND local grazing confirmation | `grazing_system_present` |
| Linear/boundary | Cropland OR grassland with field-boundary zone; no extra pasture-confirmation gate | Validated boundary geometry and regional buffer width |
| Shaded perennial | OR across coffee, cocoa and tea host fractions, retaining crop identity | MapSPAM 2020 physical crop area fallback; better commodity maps may override |

Depletion/degradation describe restoration targeting, not universal FMNR eligibility. No severe-depletion cutoff established. FMNR extension to rangelands remains unresolved; do not silently broaden it.

**GPW + GLW4 proposal is not approved as a replacement for local confirmation.** Pete asked why pilot testing was being undertaken and assigned testing to Diego. Keep this as a candidate comparison, not an adopted live rule.

The sole numeric rule is planted-silvoarable slope threshold 19.3 degrees (`above_is_suitable=false`), derived from one regional source's 35% rule. It is not a universal consensus envelope. Old rainfall, pH, canopy and soil-depth numeric rows are not active.

## Runtime contract and known limits

- `runtime/categorical.py:evaluate_family` executes categorical gates only; it is not the whole suitability pipeline. Caller supplies aligned dataset arrays, host masks and required provenance metadata.
- `runtime/host_inputs.py:plan_family_inputs` resolves required host inputs. `ready_to_fetch` means configured, not downloaded or validated. Use context `{"HTI"}` for Haiti; the SLE cocoa override is irrelevant.
- `crop_area_fraction` converts disjoint physical crop areas in hectares to fractions using native pixel area. MapSPAM bands: Arabica 32, Robusta 33, cocoa 34, tea 35. Do not double-count technology totals. Presence probabilities are not area fractions.
- Retain unknown/nodata. Missing masks must not become eligible or excluded by default. GPW codes 1/2 are grassland, 0 is other; WorldCover codes are different.
- Keep source resolution visible. Derive slope before aggregation. Retain crop fractions and crop drivers; do not report whole coarse pixels as crop footprint. Boundary outputs are applicability zones / line lengths, not planted pixel areas.
- Retained protected-area row has `relationship_type=threshold` but text threshold `IUCN_Cat_I_II`. It needs explicit categorical legal-mask handling. It is scoped to planted silvoarable in the current table; do not assume the categorical executor applies it across all families. Resolve intended legal-mask coverage before claiming complete opportunity-space output.
- Eight soft operational scenario rows belong to M2b / implementation guidance, not the structural suitability score. Keep them out of the core opportunity surface.
- No automatic raster download, reprojection, legal-mask adapter or complete end-to-end M1 execution is claimed by this package.

## Minimal categorical use

From an extracted package, with NumPy installed:

```python
from pathlib import Path
from nbs_ruralscan.runtime.host_inputs import plan_family_inputs
from nbs_ruralscan.runtime.categorical import evaluate_family

schema = Path("schema")
plan = plan_family_inputs(schema, "agroforestry", "agroforestry__silvopastoral", {"HTI"})
# Diego supplies aligned arrays and documented local grazing confirmation.
result = evaluate_family(
    schema, "agroforestry", "agroforestry__silvopastoral",
    {"gpw_grassland_class_v1": gpw_classes},
    masks={"grazing_system_present": grazing_confirmation},
)
```

Run with `PYTHONPATH=src`. NumPy is the categorical runtime dependency; pytest is needed for included tests. Existing project environment supports these. Numeric suitability and legal exclusions need separate integration.

## Validation and delivery

Focused categorical / input-plan / UTF-8 checks passed before packaging (30 tests). Structure validation returned zero errors, with existing registry warnings. Package manifest records SHA-256 checksums and source Git commit. Package bytes must match repository files exactly; no analytical values are transformed during packaging.

Build: `python3 scripts/package-t4-handoff.py`. Output: `handoff/agroforestry-t4/agroforestry-t4-diego.zip`. Contents preserve repository-relative paths. This is a local branch snapshot, not a claim that changes have been merged to main. No message or attachment has been sent to Diego.
