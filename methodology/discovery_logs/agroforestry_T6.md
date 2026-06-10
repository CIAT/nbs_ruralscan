# Discovery log — Agroforestry × T6 (NbS Scorecard)

**Date(s):** 2026-06-10
**Author(s):** Pete Steward (Team Lead) · Codex (operator)
**Seed-set rule:** T4 method §3 bounded, authority-weighted seed-set (v0.3.0).

This log records the discovery of the target **corpus feeds** intended to supply evidence for the NbS Scorecard table (T6), covering qualitative benefits/trade-offs, cost indicators, and cost-effectiveness ratios.

---

## Sources & Databases Queried

### 1. OpenAlex (Scholarly Literature)
*   **Search String**: `agroforestry AND (cost OR benefit OR revenue OR income OR profitability OR investment OR "cost-effectiveness" OR "cost-benefit") AND ("systematic review" OR "meta-analysis" OR "evidence gap map" OR "economic evaluation")`
*   **Target**: Systematic reviews, meta-analyses, and economic evaluations mapping costs, revenue, benefits, and adoption economics to agroforestry practices.
*   **Date of Search**: 2026-06-10
*   **Results Returned**: **19,261 works**

### 2. CGSpace (CGIAR Research Repository)
*   **Search String**: `site:cgspace.cgiar.org "Evert Thomas" OR "Hannes Gaisberger" OR "Chris Kettle"`
*   **Target**: Technical manuals, feasibility briefs, and scaling reports authored by team members focusing on seed supply networks, nursery costs, and livelihood feasibility enablers.
*   **Date of Search**: 2026-06-10
*   **Results Returned**: Multiple regional guides and technical papers (e.g. Colombian and Peruvian dry forest atlases).

### 3. Institutional Cost-Effectiveness Reports
*   **Selected Target Feed**: WRI Growing Resilience (Collins et al., 2025) on Sub-Saharan Africa climate-resilience cost-effectiveness. (Already registered and active in the repository as `wri_2025`).

---

## PRISMA-lite Funnel Counts

| Funnel Stage | Count | Notes / Criteria |
|---|---:|---|
| **Raw Database Returns** | **19,261+** | Total matches from OpenAlex keyword queries. |
| **Synthesis & EGM Filter** | **42** | Filtered for systematic maps, reviews, or economic meta-evaluations. |
| **Relevance Screen** | **9** | Screened for practice (agroforestry) and target (scorecard effects, cost indicators). |
| **Credibility Screen (Six-Axis)** | **5** | Rated High-tier based on evidence strength, transparency, and authority. |
| **Included in SRC Register** | **4** | Added to `schema/registers/SRC_source_register.json` with `"extraction_status": "pending"` (excludes `wri_2025` which is already active). |

---

## Final Inclusions

The following candidate feeds are registered in the Source Register for extraction:

| `source_id` | Author / Year | Benchmark Tier | Scope / Context | Key Target Variables |
|---|---|---|---|---|
| `miller_egm_2020` | Miller 2020 | High | Global / LMICs | Crop-pasture yields, net farm returns |
| `castle_sr_2021` | Castle 2021 | High | Global / LMICs | Yield trade-offs, labor demand, economic benefits |
| `wb_kcsap_2016` | World Bank 2016 | High | National / Kenya | Establishment costs, cost per farmer |
| `wb_fsrp_2022` | World Bank 2022 | High | Regional / East Africa | Livelihood enablers, benefit-cost indicators |
| `wri_2025` | Collins 2025 | High | Sub-Saharan Africa | Cost-effectiveness, cost per beneficiary |

---

## Exclusions & Boundaries

*   **Species-Specific Economic Database Tools (e.g., FAO Ecocrop)**: Excluded because crop physiological requirements do not inform practice-level economic costs or general scorecard benefits.
*   **Advocacy Project Literature**: Standard grey lit from promotional NGOs is excluded to avoid low-transparency or biased cost estimates (Conflict of Interest discount applied).

---

## Next Steps

1. **Document Ingestion**: Index the PDFs for the registered pending sources into the vectorless parser.
2. **Single-Pass Extraction**: Run the extraction tool on the indexes to capture T6 economic scorecard variables and write atomic evidence units to `EV_evidence_register.json`.
