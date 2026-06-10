# Discovery log — Agroforestry × T6 (NbS Scorecard)

**Date(s):** 2026-06-10
**Author(s):** Pete Steward (Team Lead) · Claude Code (operator)
**Seed-set rule:** T4 method §3 Bounded, authority-weighted seed-set (v0.2.7 / v0.3.0).

This log records the discovery of the target **corpus feeds** intended to supply evidence for the NbS Scorecard table (T6), covering qualitative benefits/trade-offs, cost indicators, and cost-effectiveness ratios.

---

## Sources & databases queried

We target high-level synthesis feeds, cost-effectiveness reports, and World Bank project documents:

- **Campbell Collaboration / 3ie EGM (Miller et al., 2020)** — "The impacts of agroforestry on agricultural productivity, ecosystem services, and human well‐being in low‐ and middle‐income countries: An evidence and gap map."
- **Campbell Systematic Review (Castle et al., 2021)** — "The impacts of agroforestry on agricultural productivity, ecosystem services, and human well‐being in low‐ and middle‐income countries: A systematic review."
- **World Bank Project Documents (PADs)**:
  - **Kenya Climate Smart Agriculture Project (KCSAP)** (Project ID: `P154784`)
  - **Eastern and Southern Africa Food Systems Resilience Program (FSRP)** (Project ID: `P178562`)
- **Institutional Cost-Effectiveness Reports**:
  - **WRI Growing Resilience (Collins et al., 2025)** — Sub-Saharan Africa climate-resilience cost-effectiveness.

---

## PRISMA-lite counts

| Stage | Count | Notes |
|---|---:|---|
| Query targeting synthesis feeds | 5 | Search for systematic maps, cost-effectiveness reports, and WB PADs |
| After relevance screening | **5** | All 5 feeds meet the practice (agroforestry) and target (cost-effectiveness/economic scorecard) relevance criteria |
| After credibility screening | **5** | All 5 sources are rated High-tier |
| **Included in SRC Register (Pending/Active)** | **5** | Active: `wri_2025` (Collins 2025). Pending: `miller_egm_2020`, `castle_sr_2021`, `wb_kcsap_2016`, `wb_fsrp_2022`. |

---

## Inclusions

The following discovered feeds are added to `schema/registers/SRC_source_register.json` with `"extraction_status": "pending"`:

| `source_id` | tier | first author / year | scope / scale | target tables |
|---|---|---|---|---|
| `miller_egm_2020` | High | Miller 2020 | global / LMIC | T3 / T5 / T6 |
| `castle_sr_2021` | High | Castle 2021 | global / LMIC | T3 / T5 / T6 |
| `wb_kcsap_2016` | High | World Bank 2016 | national / Kenya | T3 / T5 / T6 |
| `wb_fsrp_2022` | High | World Bank 2022 | regional / Eastern & Southern Africa | T3 / T5 / T6 |

*(Note: `wri_2025` is already active and swept in the repository).*

---

## Exclusions

- **Species-specific database tools (e.g., FAO Ecocrop)**: Excluded because physiological crop/tree parameters do not inform practice-level economic costs or general scorecard benefits.

---

## Notes

- **Next Steps (Pending Ingestion)**: These registered feeds are marked `pending` in the Source Register. Downstream tasks will ingest the documents, retrieve relevant passages by keyword, and extract atomic `EvidenceUnit` rows (Likert effects, cost indicators like `establishment_cost`, and cost-effectiveness denominators).
