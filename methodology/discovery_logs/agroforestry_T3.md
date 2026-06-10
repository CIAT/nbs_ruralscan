# Discovery log — Agroforestry × T3 (NbS × Hazard × Farming System)

**Date(s):** 2026-06-10
**Author(s):** Pete Steward (Team Lead) · Codex (operator)
**Seed-set rule:** T4 method §3 bounded, authority-weighted seed-set (v0.3.0).

This log records the discovery of the target **corpus feeds** intended to supply evidence for the NbS × Hazard × Farming System table (T3), distinguishing between livelihood mitigation (M2) and asset threat (M2b).

---

## Sources & Databases Queried

### 1. OpenAlex (Scholarly Literature)
*   **Search String**: `agroforestry AND (flood OR landslide OR drought OR erosion OR hazard OR mitigation OR resilience) AND ("systematic review" OR "meta-analysis" OR "evidence gap map")`
*   **Target**: High-level systematic reviews, meta-analyses, and evidence gap maps mapping physical climate hazards and erosion to agroforestry practices.
*   **Date of Search**: 2026-06-10
*   **Results Returned**: **18,080 works**

### 2. CGSpace (CGIAR Research Repository)
*   **Search String**: `site:cgspace.cgiar.org "Evert Thomas" OR "Hannes Gaisberger" OR "Chris Kettle"`
*   **Target**: Technical manuals, working papers, and species vulnerability atlases authored by team members to capture operational limits, seed sourcing, and regional guides.
*   **Date of Search**: 2026-06-10
*   **Results Returned**: Multiple regional guides and technical papers (e.g. Colombian and Peruvian dry forest atlases).

### 3. World Bank Project Portal (Operational Documents)
*   **Target Search**: World Bank Project Appraisal Documents (PADs) and Implementation Completion Reports (ICRs) containing agroforestry designs.
*   **Selected Target Feeds**: KCSAP (Kenya, Project ID `P154784`) and FSRP (Eastern/Southern Africa, Project ID `P178562`).

---

## PRISMA-lite Funnel Counts

| Funnel Stage | Count | Notes / Criteria |
|---|---:|---|
| **Raw Database Returns** | **18,080+** | Total matches from OpenAlex keyword queries. |
| **Synthesis & EGM Filter** | **35** | Filtered for papers with global or regional synthesis scale (excluding primary studies for initial seeds). |
| **Relevance Screen** | **8** | Screened for practice (agroforestry) and target (hazard mitigation/asset risk enabler relationship). |
| **Credibility Screen (Six-Axis)** | **4** | Rated High-tier based on evidence strength, transparency, and authority. |
| **Included in SRC Register** | **4** | Added to `schema/registers/SRC_source_register.json` with `"extraction_status": "pending"`. |

---

## Final Inclusions

The following candidate feeds are registered in the Source Register for extraction:

| `source_id` | Author / Year | Benchmark Tier | Scope / Context | Key Target Variables |
|---|---|---|---|---|
| `miller_egm_2020` | Miller 2020 | High | Global / LMICs | Soil conservation, water quality, carbon sequestration |
| `castle_sr_2021` | Castle 2021 | High | Global / LMICs | Livelihood crop yield impacts, climate risk mitigation |
| `wb_kcsap_2016` | World Bank 2016 | High | National / Kenya | Soil erodibility, local crop resilience enablers |
| `wb_fsrp_2022` | World Bank 2022 | High | Regional / East Africa | Crop-pasture drought enablers, water logging |

---

## Exclusions & Boundaries

*   **Individual Species Suitability Models (e.g., D4R, Treefinder)**: Excluded from general practice-level suitability mapping because a single species' niche does not define practice-level viability. These are deferred to Module 6 for implementation hand-off.
*   **FAO Ecocrop**: Excluded from general suitability/mitigation because physiological crop-niche limits are out-of-scope for general agroforestry practices, except as a parameters lookup for F5 shaded systems understorey crop climate projections.

---

## Next Steps

1. **Document Ingestion**: Index the PDFs for these 4 registered sources into the vectorless parser.
2. **Single-Pass Extraction**: Run the extraction tool on the indexes to capture T3 hazard mitigation variables and write atomic evidence units to `EV_evidence_register.json`.
