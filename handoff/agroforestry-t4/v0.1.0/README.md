# Agroforestry T4 v0.1.0

First-pass configuration snapshot for the November 2026 World Bank discussion. Not pilot-validated.

Open [index.html](index.html) for one searchable table, or [T4_review.csv](T4_review.csv) for spreadsheet review. Operational scenarios are hidden by default in the browser view.

| File | Meaning |
|---|---|
| T4_suitability_mappings.csv | Exact authoritative T4 snapshot: 26 mappings |
| T4_review.csv | Human-readable rules, hierarchy, evidence, datasets and status |
| variables.csv | Canonical measurements, aliases, groups, units and meaningful spatial scale |
| datasets.csv | Dataset descriptions, spatial/temporal resolution and limitations |
| dataset_bindings.csv | Existing context-specific preference order and upload requirements |
| host_inputs.csv | Family-specific host masks, dataset bands and dependencies |
| source_relative_importance.csv | Three-study diagnostic; preserve model variants and hierarchy |
| evidence_accounting.csv | Disposition of every current structural/operational record |
| manifest.json | Version, source commit, counts, explicit gaps and file fingerprints |

**Bank-meeting progress:** ten numeric rows across seven variables now accompany seven host gates, with traceable evidence and explicit source/context limitations. Existing legacy handoff described one numeric rule; this release corrects that account. Source-level importance and dataset hierarchy are exposed without claiming validated universal weights.

**Next iteration:** resolve climate recipe/BIND mismatch; legal-mask execution and family coverage; source/context choices for regional numeric functions; priority local host inputs. Broader proxy consolidation requires compatible definitions and depth/time support, then AOI correlation checks. No silent averaging of aridity with rainfall or NDVI with canopy cover.

See [handoff scope and runtime limits](../README.md). A first pass is available now; these limits do not disappear because the release is versioned.
