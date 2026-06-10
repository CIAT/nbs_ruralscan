# Discovery log — Agroforestry × T3 (NbS × Hazard × Farming System)

**Date(s):** 2026-06-10
**Author(s):** Pete Steward (Team Lead) · Claude Code (operator)
**Seed-set rule:** T4 method §3 bounded, authority-weighted seed-set (v0.2.7 / v0.3.0).

This log records the discovery of the target **corpus feeds** intended to supply evidence for the NbS × Hazard × Farming System table (T3), distinguishing between livelihood mitigation (M2) and asset threat (M2b).

---

## Sources & databases queried

We target high-level synthesis feeds and World Bank operational documents as our initial corpus boundary:

- **Campbell Collaboration / 3ie EGM (Miller et al., 2020)** — "The impacts of agroforestry on agricultural productivity, ecosystem services, and human well‐being in low‐ and middle‐income countries: An evidence and gap map."
- **Campbell Systematic Review (Castle et al., 2021)** — "The impacts of agroforestry on agricultural productivity, ecosystem services, and human well‐being in low‐ and middle‐income countries: A systematic review."
- **World Bank Project Documents (PADs)**:
  - **Kenya Climate Smart Agriculture Project (KCSAP)** (Project ID: `P154784`)
  - **Eastern and Southern Africa Food Systems Resilience Program (FSRP)** (Project ID: `P178562`)

---

## PRISMA-lite counts

| Stage | Count | Notes |
|---|---:|---|
| Query targeting synthesis feeds | 4 | Targeted search for systematic maps/reviews + WB agroforestry PADs |
| After relevance screening | **4** | All 4 feeds meet the practice (agroforestry) and target (hazard mitigation/asset risk) relevance criteria |
| After credibility screening | **4** | Miller 2020, Castle 2021, and the two WB PADs are rated High-tier |
| **Included in SRC Register (Pending)** | **4** | `miller_egm_2020`, `castle_sr_2021`, `wb_kcsap_2016`, `wb_fsrp_2022` |

---

## Inclusions

The following discovered feeds are added to `schema/registers/SRC_source_register.json` with `"extraction_status": "pending"`:

| `source_id` | tier | first author / year | scope / scale | target tables |
|---|---|---|---|---|
| `miller_egm_2020` | High | Miller 2020 | global / LMIC | T3 / T5 / T6 |
| `castle_sr_2021` | High | Castle 2021 | global / LMIC | T3 / T5 / T6 |
| `wb_kcsap_2016` | High | World Bank 2016 | national / Kenya | T3 / T5 / T6 |
| `wb_fsrp_2022` | High | World Bank 2022 | regional / Eastern & Southern Africa | T3 / T5 / T6 |

---

## Exclusions

- **Species-specific database tools (e.g., FAO Ecocrop)**: Excluded from candidate feeds for general practice suitability/mitigation because physiological crop-niche limits are out-of-scope for practice-level targeting.

---

## Notes

- **Next Steps (Pending Ingestion)**: These registered feeds are marked `pending` in the Source Register. Downstream tasks will ingest the documents, retrieve relevant passages by keyword, and extract atomic `EvidenceUnit` rows to map the climate mitigation values to the T3 table.
