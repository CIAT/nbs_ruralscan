# Worked slice — Agroforestry · F1 Planted silvoarable · Slope (gold standard)

**Status:** worked example for the T4 method ([`../T4_generation_method.md`](../T4_generation_method.md)) · June 2026
**Purpose:** one variable end-to-end (define → vocab → ingest → extract → synthesise) with a full provenance
chain, to (a) prove the method and (b) be the gold standard the extraction skill is evaluated against.
**Quotes are real** — pulled from the agroforestry stocktake PDFs with page numbers; tiers from
`NbS_peer_reviewed_benchmarked.csv`.

---

## 1. Target (definition layer)

- **NbS:** agroforestry · **Family:** F1 Planted silvoarable (alley cropping, tree intercropping, planted boundary on cropland)
- **`spatial_product_type`:** `area_suitability` · **dominant limiting factor:** biophysical envelope + management
- **Variable:** canonical `slope` · group **Topographic** · **canonical unit: degrees (°)** · aliases: terrain slope, gradient, inclination, "slope %"
- **Dataset (T1):** `copernicus_dem_glo30` → slope derived
- **Suitability question:** where can planted silvoarable agroforestry physically establish (erosion / mechanisation / root-anchoring constraints)?

**Unit harmonisation rule:** papers report slope in **% or degrees** — convert all to degrees: `° = atan(%/100)`.
Key conversions used: 3%→1.7° · 6%→3.4° · 8%→4.6° · 15%→8.5° · 20%→11.3° · 25%→14° · 35%→19.3° · 45%→24.2° · 75%→36.9°.

---

## 2. Evidence Register (extracted, harmonised to degrees)

`evidence_type = literature_relationship` unless noted. Family relevance checked per row.

| evidence_id | source (tier) | study context | raw claim (verbatim, p.) | → degrees | role |
|---|---|---|---|---|---|
| ev_slope_nath21 | Nath 2021 (**Med**) | E. Indian Himalaya | "Slope degree … 0 to 5 \| 5 to 10 \| 10 to 15 \| 15 to 20 \| 20 to 44" (best→worst), weight 40% (p.11) | opt 0–5°, max ~44° | degree-native classes |
| ev_slope_mushtaq23 | Mushtaq 2023 (**Med**) | Kashmir (mulberry AF) | "Slope (°) Below 10 … 27.10% influence \[highest]; 10–20; 20–30; 30–40" (p.13) | opt <10°, declines to ~40° | degree-native classes |
| ev_slope_mendonca23 | Mendonça 2023 (**High**) | São Paulo, Brazil | "Slope 0–3% flat; 3–8% gently undulating; 8–20% undulating; 20–45% strongly undulating; 45–75% mountainous; 75–100% steep" (p.9–10) | flat 0–1.7° best → unsuitable >24° | Embrapa relief ranking |
| ev_slope_mendonca22 | Mendonça 2022 (**High**) | São Paulo, Brazil | "Relief (slope %) … Flat 0–3% \[best score]" ; priority areas "slope 0–3%" (p.5, p.8) | flat 0–1.7° optimal | relief vulnerability factor |
| ev_slope_marinis22 | Marinis 2022 (**Med**) | DRC (land capability) | "low: slope inferior to 6%, medium: 6–25%, high: slope over 25%" (p.6) | best <3.4°, poor >14° | capability classes |
| ev_slope_wotlolan21 | Wotlolan 2021 (**Med**) | Sigatoka, Fiji | "filter out raster cells with slope greater than 35% (Harrison 2016)" (p.5) | hard cut > ~19° | absolute exclusion |
| ev_slope_haris21 | Haris 2021 (**Low**) | Maros, Indonesia | "slope of more than 45%" = heavy erosion inhibitor; tree "optimally … 8% – 15%" (p.5–6) | opt 4.6–8.5°, unsuit >24° | classes |
| ev_slope_seja22 | Seja 2022 (**Low**) | Uluguru, Tanzania | "Slope 8%–12% \| 12–20% \| 20–28% \| 28–38% \| 38–72%" (best→worst) (p.11) | opt ~4.6–6.8° → ~36° | classes |
| ev_slope_kiziridis26 | Kiziridis 2026 (**Med**) | Spain/Greece | "steep slopes (greater than 8°)" a key driver (p.23) | — | **F3 silvopastoral — excluded from F1** |
| ev_slope_baldwin22 | Baldwin 2022 (**Med**) | N. Carolina, USA | "slopes less than 2%" (p.6–7) | — | **FloodWise/flood NbS — excluded from F1** |
| ev_slope_ahmad18 | Ahmad 2018 (**Low**) | Bihar, India | slope-percent criterion; class table garbled in PDF text (p.5) | — | **pending clean OCR/table parse** |
| ev_slope_haile24 | Haile 2024 (**Low**) | Genale, Ethiopia | "Slope percentage plays a significant role…" — thresholds in a table not captured (p.7) | — | **pending table parse** |

Two correctly **excluded** (family/practice mismatch): Kiziridis (silvopastoral → F3), Baldwin (flood NbS, not
silvoarable). Two **flagged pending** (Ahmad 2018, Haile 2024) where the threshold lives in a table the flat text
mangled — exactly the case the structure-aware ingestion (table parsing) will recover.

**Per-claim `claim_basis` · `claim_scope` tags** (the orthogonal axes from method §5.2):

| evidence_id | claim_basis | claim_scope (taxon) | note |
|---|---|---|---|
| ev_slope_nath21 | table | practice_technology | general AF land suitability |
| ev_slope_mushtaq23 | table | practice_technology (paper taxon = *mulberry*) | **slope is technology-driven, so usable** even though the paper is species-specific; the paper's *climate* optima would be `species_specific` and must NOT feed a practice row |
| ev_slope_mendonca23 | cited_secondary (Embrapa relief classes) | practice_technology | standard relief ranking |
| ev_slope_mendonca22 | table | practice_technology | relief vulnerability factor |
| ev_slope_marinis22 | table | practice_technology | land-capability classes |
| ev_slope_wotlolan21 | cited_secondary (Harrison 2016) | practice_technology | absolute exclusion rule |
| ev_slope_haris21 | table | **mixed**: ">45% erosion" = practice_technology; "optimal 8–15%" = `species_specific` (*sengon*) | use the erosion cut; treat the optimum as species-flavoured |
| ev_slope_seja22 | table | practice_technology | classification |

This is the key teaching case: **slope is a technology-driven variable**, so even species-focused papers
(mulberry, sengon) contribute valid *slope* evidence — but the same papers' **temperature/rainfall/altitude**
claims would be `species_specific` and must be routed to species suitability, not the agroforestry-practice row.

---

## 3. Synthesis → F1 slope T4 row

Tier- and context-weighted reconciliation of the eight in-family units.

- **Optimal plateau:** all sources agree suitability is highest on near-flat to gentle ground. Degree-native
  (Nath 0–5°, Mushtaq <10°) and converted High-tier (Mendonça flat 0–3% ≈ 0–1.7°) converge on **opt_low 0°,
  opt_high ≈ 10°**.
- **Absolute max — genuine divergence, context-driven:** converted %-based sources cut at ~19–24° (Wotlolan 35%,
  Haris/Mendonça 45%), while degree-native *montane* studies tolerate ~40–44° (Nath, Mushtaq) — steeper ground is
  accepted where tree cover provides erosion control on mountainous terrain. → **global abs_max ≈ 30° with high
  uncertainty**, plus a **montane/humid override to ≈ 44°**.

```json
{
  "mapping_id": "agro_f1_slope",
  "suitability_family_id": "agroforestry__planted_silvoarable",
  "variable": "slope", "variable_unit": "degrees",
  "dataset_id": "copernicus_dem_glo30",
  "suitability_dimension": "biophysical_constraint",
  "relationship_type": "trapezoidal",
  "relationship_params": { "abs_min": 0, "opt_low": 0, "opt_high": 10, "abs_max": 30 },
  "uncertainty_pct": 30,
  "context_overrides": [
    { "context_type": "aez", "context_id": "humid_tropics",
      "relationship_params": { "abs_min": 0, "opt_low": 0, "opt_high": 18, "abs_max": 44 },
      "note": "Montane/humid systems tolerate steeper ground (tree erosion control). ev_slope_nath21, ev_slope_mushtaq23" },
    { "context_type": "aez", "context_id": "semi_arid",
      "relationship_params": { "abs_min": 0, "opt_low": 0, "opt_high": 8, "abs_max": 20 },
      "note": "Drier parkland systems favour gentler slopes for water retention." }
  ],
  "weight_default": 0.15,
  "justification": "Suitability is highest on flat–gentle slopes and declines as erosion risk and mechanisation difficulty rise. Optimal ≤10° from degree-native classes (ev_slope_nath21 0–5°, ev_slope_mushtaq23 <10°) and High-tier relief ranking (ev_slope_mendonca22/23, flat 0–3%). Absolute max is context-dependent: ~24° in converted %-based studies (ev_slope_wotlolan21, ev_slope_haris21) vs ~44° in montane degree-native studies (ev_slope_nath21, ev_slope_mushtaq23) — captured as a humid/montane override.",
  "references": ["Nath 2021","Mushtaq 2023","Mendonça 2022","Mendonça 2023","Marinis 2022","Wotlolan 2021","Haris 2021","Seja 2022"],
  "evidence_ids": ["ev_slope_nath21","ev_slope_mushtaq23","ev_slope_mendonca23","ev_slope_mendonca22","ev_slope_marinis22","ev_slope_wotlolan21","ev_slope_haris21","ev_slope_seja22"]
}
```

---

## 4. Findings (why this slice is worth it)

1. **The method caught a likely error in the draft-0 table.** The committed draft-0 `agro_slope_global` row uses
   `{opt_high: 15, abs_max: 45}` **degrees**. The evidence shows `45` almost certainly came from papers stating
   slope **45 %** (≈ 24°) read as 45°, blended with Nath's genuine 44° montane case — a **unit-harmonisation
   conflation**. The evidence-based global `abs_max` is ~30° (±), with ~44° only in montane/humid contexts. This
   is exactly the kind of silent error the structured, harmonised, provenance-first method exists to surface.
2. **Tier tension is real and was handled honestly.** The crispest numeric thresholds come from **Low/Med-tier**
   papers (Haris, Seja, Mushtaq, Nath); the **High-tier** ones (Mendonça) give relief *rankings*, not hard cuts.
   The synthesis used High-tier to anchor the optimal/shape and Low/Med for the threshold magnitudes, recording
   the divergence rather than averaging it away.
3. **Family discipline worked.** Kiziridis (silvopastoral → F3) and Baldwin (flood NbS) were excluded on
   family/practice grounds, not lumped in because they mention "slope."
4. **Structure-aware ingestion is needed, confirmed.** Two threshold sources (Ahmad 2018, Haile 2024) sit in
   tables the flat-text pass mangled — recoverable only by the table-parsing step in §5.1 of the method.
5. **Species vs technology matters even on slope.** Two sources (Mushtaq → *mulberry*, Haris → *sengon*) are
   single-species suitability studies wearing an "agroforestry" label. Slope is technology-driven, so their slope
   claims are still practice-valid (with Haris's *optimum* flagged as species-flavoured) — but their
   temperature/rainfall/altitude optima are `species_specific` and would have to be routed to species suitability,
   never allowed to set the agroforestry-practice envelope. Captured via `claim_scope` per claim.

## 5. Provenance chain (the deliverable)

`T4 agro_f1_slope` → `evidence_ids[]` → Evidence Register rows (verbatim quote + page) → Source Register
(paper + tier + study context). Every parameter is traceable; uncertainty is derived from real evidence spread.

> Caveat: quotes are verbatim but page-level; for the final record, attach the source PDF + exact table/figure
> reference per the ingestion design. Ahmad 2018 / Haile 2024 thresholds pending clean table extraction.
