# Categorical code lists

Reference legends that decode numeric class codes (in EV quotes / `relationship` fields)
into human-readable names — so a reviewer sees "Corn, Soybeans…" not "1, 5". Decoding is
applied **by default** wherever class-coded evidence is shown (resolver:
`src/nbs_ruralscan/runtime/codelist.py`; embedded in `dashboard_data.json`).

One CSV per scheme (`code,label`):
- **`cdl.csv`** — USDA NASS Cropland Data Layer category legend. Source: USDA NASS CDL
  legend (https://www.nass.usda.gov/Research_and_Science/Cropland/sarsfaqs2.php),
  fetched 2026-06-24. Used by the saraheb3 agroforestry tool's CDL crop-eligibility mask.

To add a scheme (e.g. HWSD soil-quality 1–7, FAO LCCS 1–4): drop `<scheme>.csv` here from
an authoritative legend, then map the variable/dataset to it in `codelist.py`.
