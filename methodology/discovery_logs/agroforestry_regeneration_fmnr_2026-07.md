# Discovery log — Agroforestry × F2 regeneration_farmland (FMNR/ANR/RNA) — T4·T3·T6

**Date:** 2026-07-17.
**Author(s):** Pete Steward (orchestrated) · Claude Code (operator).
**Sub-practice:** `agroforestry__regeneration_farmland` (F2) — Farmer-Managed Natural Regeneration (FMNR), incl. Assisted Natural Regeneration (ANR) and French *régénération naturelle assistée* (RNA). Agroforestry via protecting + managing natural tree/shrub regeneration on farmland/parkland (Sahel re-greening, parkland restoration) — **not** tree planting.
**Run id:** `fmnr_2026-07` · **Ruleset:** v1.2.
**Issue:** #115 (per-sub-practice agroforestry evidence gaps). Fills the F2 gaps T3=0 and T6=0, deepens thin T4 (was 3 rows).
**Seed-set rule:** T4 method §3 bounded, authority-weighted seed-set. Cap ~15–20 sources across the three tables.
**Screening funnel:** five-step (frame · source-type triage · relevance · six-axis credibility → `benchmark_tier` · saturation stop). Grey positive-bias discount applied.

---

## Sources & databases queried

Six discovery lenses (parallel), all title-anchored / authority-weighted, executed 2026-07-17:

1. **OpenAlex REST API — T4 suitability.** `title.search` (display_name) on FMNR/ANR/RNA synonyms (EN/FR) × biophysical & land-condition terms (rainfall, aridity, soil, degradation, parkland, slope), sorted by citations.
2. **OpenAlex — T3 climate-hazard response.** FMNR/ANR/RNA × drought / climate-resilience / regreening-drought-Sahel.
3. **OpenAlex — T6 outcomes + cost.** FMNR/ANR/RNA × yield / adoption / income / tree-density / carbon / biodiversity / cost.
4. **Grey literature (authority orgs).** WebSearch of CRS, WRI, World Agroforestry/ICRAF, FAO, Regreening Africa, ELD/GIZ, World Vision, IUCN for downloadable technical guidance / MEL / economic reports.
5. **WOCAT SLM Technologies database** — FMNR / ANR technology entries (LMIC-grounded establishment conditions + benefits).
6. **Seed backward/forward citation** — canonical FMNR literature (Reij & Garrity 2016, Weston 2015, Binam 2015 & 2017, Chomba 2020, Sendzimir 2011, Haglund 2011, Garrity 2010), confirmed via OpenAlex.

**Multilingual:** title-search included EN (“farmer managed natural regeneration”, “assisted natural regeneration”) + FR (“régénération naturelle assistée”, RNA). Two FR Sahel sources included (ijbcs Mali adoption; ESJ RNA×millet).

---

## PRISMA-lite counts (sweep-level)

| stage | n |
|---|---|
| Retrieved (raw across 6 lenses) | 58 |
| Removed at dedup (cross-lens duplicates) | 22 |
| Unique screened | 36 |
| **Included** | **19** |
| Excluded (venue-authority / saturation / COI / acquire-risk / scope-drift) | 17 |

Per-table included (membership — a source counts under each table it serves): **T4 = 11 · T3 = 9 · T6 = 11.**
By discovery process: updated_lit = 14 · grey = 5.

`crs_fmnr_niger_2025` (already registered) did not re-surface. All 19 carried `fmnr_explicit=true` (no PICOS failures); two borderline species/ecology-framed RNA items were dropped at relevance/saturation.

---

## Included (19) → acquisition outcome

**Cached & indexed (13):** chomba_2020, lohbeck_2020, researchsquare_fmnr_2025 (preprint, Low tier), ijbcs_rna_mali_2020, weston_2015, binam_2017, glce_fmnr_mali_2023, sendzimir_2011, wri_regreening_2015 (grey), fao_anr_2019 (grey), eld_fmnr_2020 (grey), wocat_507_2019 (grey), wocat_1358_2017 (grey).

**Not cached (6) — follow-up pass:**
- Cloudflare-403 (retry): `ijecc_anr_niger_2023`, `esj_rna_millet_2020`.
- Paywalled / no free full-text → **library acquisition** (SharePoint): `kessler_1994` (Elsevier), `ldd_anr_arid_2024` (Wiley), `haglund_2011` (Elsevier-only), `binam_2015` (repo landing, no PDF).

**Acquisition notes:**
- OA PDFs resolved via Unpaywall best-OA-location; several OA hosts (Frontiers, AJOL, unil repository) block the generic tool UA → cached with a browser UA. Follow-up: add a browser-UA fallback to `ingest/acquire.py` (recurring — also hit in the 2026-06 sweep).
- **WOCAT handling rule (new):** the technology web page is a JS SPA shell (near-empty HTML snapshot); acquire the **per-technology PDF export** `wocat.net/en/database/technologies/<id>/pdf/` instead.

---

## Excluded (17) — reasons

Low-tier / predatory venues (Int J Environmental Sciences, Int J Advanced Research, JSIC); saturation-redundant with stronger Sahel anchors; World Vision advocacy manual trio (COI / positive-bias flood-risk on T6); no-DOI grad thesis (acquire-risk); scope-drift (WOCAT area-closure/exclosure → pastoral rangeland; Garrity 2010 evergreen-agriculture/Faidherbia framing); Reij & Garrity 2016 (canonical but closed narrative synthesis, its drivers/scaling signal already carried by Chomba 2020 + Sendzimir 2011 + Lohbeck 2020).

---

## Provenance

- Search protocol: SRCH register rows `agroforestry__{T4,T3,T6}__{updated_lit,grey}__agroforestry__regeneration_farmland__2026-07-17`.
- Ledger: `searched=done` + `screened=done` stamped per (table × category × family) for `fmnr_2026-07`.
- Extraction (deterministic pipeline → staging → central gates) tracked separately; ledger `extracted`/`verified`/`reviewed` advance only as those steps complete.
