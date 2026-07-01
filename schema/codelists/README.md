# Categorical code lists

Reference legends that decode numeric class codes (in EV quotes / `relationship` fields)
into human-readable names — so a reviewer sees "Corn, Soybeans…" not "1, 5". Decoding is
applied **by default** wherever class-coded evidence is shown (resolver:
`src/nbs_ruralscan/runtime/codelist.py`; embedded in `dashboard_data.json`).

One CSV per scheme (`code,label`):
- **`cdl.csv`** — USDA NASS Cropland Data Layer category legend. Source: USDA NASS CDL
  legend (https://www.nass.usda.gov/Research_and_Science/Cropland/sarsfaqs2.php),
  fetched 2026-06-24. Used by the saraheb3 agroforestry tool's CDL crop-eligibility mask.
- **`gaez_aez33.csv`** — GAEZ v4 33-class Agro-Ecological Zones legend (codes 1–33;
  0=nodata). Source: FAO GAEZ4 symbology `AEZ_33classes.clr`. Decodes the `gaez_v4_aez33`
  dataset raster (loader streams the class-coded COG; classes are nominal).

To add a scheme (e.g. HWSD soil-quality 1–7, FAO LCCS 1–4): drop `<scheme>.csv` here from
an authoritative legend, then map the variable/dataset to it in `codelist.py`.
- **`hwsd_soil_quality.csv`** — GAEZ Harmonized World Soil Database soil-suitability/quality 7-class scheme (Fischer et al. 2008, *GAEZ Assessment for Agriculture*). Classes 1–4 = soil-limitation degrees (% of growth potential); 5 = non-soil, 6 = permafrost, 7 = water. Sources: GAEZ v3.0/2008 model documentation (gaez.iiasa.ac.at; classes 1–4 growth-potential ranges) + the cached `cgspace_singh_southasia_2020` source (5/6/7 definitions, Fischer 2008). Used by the South-Asia AF suitability rows (`soil_texture_hsg`, classes_suitable 1–4).
