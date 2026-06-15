# Discovery Log — Agroforestry × T3 (NbS × Hazard × Farming System)

**Date(s):** 2026-06-15
**Author(s):** Pete Steward (Team Lead) · Codex (operator)
**Seed-set rule:** T4 method §3 bounded, authority-weighted seed-set (v0.3.0) + disjoined synonyms.

This log records the discovery of target candidate feeds intended to supply evidence for the NbS × Hazard × Farming System table (T3), specifically testing the boundaries of the biophysical hazard-mitigation relationships.

---

## Sources & Databases Queried

### 1. OpenAlex (Scholarly Literature)
Disjoined searches in Title Fields (`display_name.search`) incorporating practice synonyms and hazard-mitigation terms across English, Spanish, French, and Portuguese:

*   **Query 1 (Drought / Heat Stress)**:
    - *Filter 1 (Practices)*: `display_name.search:agroforestry|alley-cropping|silvopasture|FMNR|shade-tree|homegarden|sistemas-agroforestales|silvopastoril|agroforesterie`
    - *Filter 2 (Hazards)*: `display_name.search:drought|microclimate|shade|shading|canopy|temperature-buffer|soil-moisture|sequia|microclima|secheresse|microclimat|seca`
    - *Results*: 15 works
*   **Query 2 (Floods / Waterlogging)**:
    - *Filter 1 (Practices)*: `display_name.search:agroforestry|alley-cropping|silvopasture|vegetative-buffer|contour-buffer|sistemas-agroforestales|système-agroforestier|brise-vent`
    - *Filter 2 (Hazards)*: `display_name.search:flood|flooding|runoff|hydrology|hydrological|infiltration|water-retention|waterlogging|inundacion|escurrimiento|infiltracion|inondation|ruissellement|encharcamento`
    - *Results*: 15 works
*   **Query 3 (Wind / Storms)**:
    - *Filter 1 (Practices)*: `display_name.search:agroforestry|windbreak|shelterbelt|live-fence|hedgerow|cortinas-rompevientos|barreras-rompevientos|cercas-vivas|brise-vent|quebra-ventos`
    - *Filter 2 (Hazards)*: `display_name.search:wind|shelter|erosion|protection|storm|cyclone|viento|tormenta|vent|tempete|vento|tempestade`
    - *Results*: 15 works
*   **Query 4 (Erosion / Landslides)**:
    - *Filter 1 (Practices)*: `display_name.search:agroforestry|alley-cropping|vegetative-buffer|contour-buffer|tree-retention|hedgerow|sistemas-agroforestales|système-agroforestier`
    - *Filter 2 (Hazards)*: `display_name.search:erosion|landslide|slope|slopes|root|anchorage|binding|shear-strength|slope-stability|deslizamiento|pendiente|glissement-de-terrain|pente|deslizamento|declividade`
    - *Results*: 15 works
*   **Query 5 (Wildfires / Fire)**:
    - *Filter 1 (Practices)*: `display_name.search:agroforestry|alley-cropping|silvopasture|FMNR|shade-tree|sistemas-agroforestales|silvopastoril|agroforesterie`
    - *Filter 2 (Hazards)*: `display_name.search:fire|wildfire|flammability|fuel-load|incendio|feu|fogo`
    - *Results*: 10 works
*   **Query 6 (Meta-Analysis & Systematic Review Stream)**:
    - *Filter 1 (Practices)*: `display_name.search:agroforestry|alley-cropping|silvopasture|shade-tree`
    - *Filter 2 (Study Types)*: `display_name.search:meta-analysis|systematic-review|evidence-map|review`
    - *Filter 3 (Keywords)*: `display_name.search:adaptation|resilience|mitigation|productivity|benefits`
    - *Results*: 10 additional works (specifically targeting general synthesis papers that miss hazard-specific title indexing)

### 2. Targeted Institutional Database Interrogations
Rather than relying on general web searches, grey literature and tools were discovered by querying structured institutional portals directly:

*   **WOCAT SLM Database (wocat.net)**:
    - *Search Method*: Filtered the Global Database by Technology Group = `Agroforestry` AND Climate Change Adaptation benefits = `Drought / Waterlogging / Wind / Soil Erosion`.
    - *Results*: Identified specific SLM technology records detailing biophysical thresholds, establishing cost ranges, and hazard reduction ratings.
*   **FAO TECA Portal (teca.apps.fao.org)**:
    - *Search Method*: Queried the Technologies and Practices for Small Agricultural Producers portal for `agroforestry hazard mitigation` and `sloping agricultural land technology (SALT)`.
    - *Results*: Retrieved the FAO field practitioner technical guide and farm disaster risk mitigation manuals.
*   **World Bank Documents & Reports (documents.worldbank.org)**:
    - *Search Method*: Searched the project repository for sector = `Agricultural and Rural Development` AND keyword = `agroforestry` AND hazard = `drought / flood`.
    - *Results*: Retrieved Project Appraisal Documents (PADs) and disaster-screening guidelines (PROFOR-DRM).
*   **Center for Agroforestry (centerforagroforestry.org)**:
    - *Search Method*: Searched for `applied agroforestry training manual` and `riparian buffer design`.
    - *Results*: Retrieved the design guides and financial decision-support spreadsheets.

---

## PRISMA-lite Funnel Counts

| Funnel Stage | Count | Notes / Criteria |
|---|---:|---|
| **Returned (raw)** | **80** | Cumulative returns across the 6 disjoined OpenAlex queries (including the new meta-analysis stream). |
| **Topic & Scope Filter** | **50** | Screened out urban forestry, non-agroforestry biology, and general restoration papers. |
| **Relevance Screen** | **30** | Filtered for papers with quantitative or qualitative claims linking practice subtypes to hazard reduction or asset threat thresholds. |
| **Credibility Screen (Six-Axis)** | **20** | Evaluated for evidence strength, methodological transparency, venue, context relevance (LMIC), recency, and seminality. |
| **Included in SRC Register** | **19** | 16 literature publications (including 7 new systematic reviews/meta-analyses), 2 grey literature reports, and 1 database tool. |

---

## Final Inclusions

### 1. Peer-reviewed Literature (OpenAlex)

| `source_id` | Author / Year | Benchmark Tier | Scope / Context | Key Target Variables / Hazards |
|---|---|---|---|---|
| `tscharntke_shade_2011` | Tscharntke et al. 2011 | High | Tropical / Global | Shaded perennial crops (F5), microclimate buffering |
| `quandt_resilience_2017` | Quandt et al. 2017 | High | Kenya (Semi-arid) | Dryland FMNR/F1, livelihood flood & drought resilience |
| `udawatta_runoff_2002` | Udawatta et al. 2002 | High | Global / Arable | Alley cropping (F1) buffer strips, runoff & water logging |
| `anderson_infiltration_2008`| Anderson et al. 2008 | High | Global / Arable | Vegetative buffers (F4), soil water & infiltration |
| `cornelis_windbreak_2004` | Cornelis et al. 2004 | High | Drylands / Global | Windbreaks (F4), wind speed reduction & wind erosion |
| `wei_runoff_2007` | Wei et al. 2007 | High | Sub-humid Tropics | Alley cropping (F1), runoff & soil erosion |
| `damianidis_wildfires_2020` | Damianidis et al. 2020 | High | Med / Global | Silvopasture/Silvoarable (F3/F1), wildfire risk reduction |
| `suyanto_fire_2005` | Suyanto et al. 2005 | Medium | Indonesia (Lampung) | FMNR/F1, land tenure & fire hazard reduction |
| `batcheler_silvopasture_2024`| Batcheler et al. 2024 | Medium | United States / Global | Silvopasture (F3), fuel load & wildfire mitigation |
| `patil_coffee_2025` | Patil et al. 2025 | High | Global | Shaded perennial crops (F5), microclimate buffering & drought hazard |
| `abebaw_adaptation_2025` | Abebaw et al. 2025 | High | Global | Global practices, microclimate, flood, & erosion mitigation |
| `kuyah_ssa_2019` | Kuyah et al. 2019 | High | Sub-Saharan Africa | SSA agroforestry, water regulation & soil erosion risk |
| `niether_cocoa_2020` | Niether et al. 2020 | High | Global | Shaded perennial crops (F5), microclimate buffering & water regulation |
| `baier_maize_2023` | Baier et al. 2023 | High | Global | Alley cropping (F1) / Drylands, grain yield under drought stress |
| `de_beenhouwer_biodiversity_2013` | De Beenhouwer et al. 2013 | High | Global | Shaded perennial crops (F5), microclimate buffering & soil carbon |
| `ngaba_soil_2024` | Ngaba et al. 2024 | High | Global | Global practices, soil carbon & nitrogen dynamics |


### 2. Grey Literature (Reports)

| `source_id` | Author / Year | Benchmark Tier | Scope / Context | Key Target Variables / Hazards |
|---|---|---|---|---|
| `fao_agroforestry_policy_2013`| FAO 2013 | High | Global | DRM policy guidance, climate adaptation |
| `wb_nbs_resilience_2021` | World Bank 2021 | High | Global | nature-based solutions for agricultural resilience |

### 3. Tools and Methodologies

| `source_id` | Author / Year | Benchmark Tier | Scope / Context | Key Target Variables / Hazards |
|---|---|---|---|---|
| `wocat_slm_database` | WOCAT 2026 | High | Global | SLM technologies database, Climate Change Adaptation |

---

## Exclusions & Borderline Edge Cases (Human-in-the-Loop Review)

We identified several borderline cases that require collaborative feedback to define the edges of our task:

### 1. Borderline Exclusions (Proposed for rejection)
*   **Urban Shade Studies (Urban Forestry)**:
    - *Candidate*: Hashem Akbari et al. (2001) — *Cool surfaces and shade trees to reduce energy use and improve air quality in urban areas*. (1819 citations)
    - *Ambiguity*: Focused entirely on urban heat island mitigation and building cooling, rather than agricultural or forestry cropping systems.
    - *Proposal*: **Exclude** from the rural scoping database as it sits outside our rural agricultural mandate.
*   **Poplar Root Disturbance Studies (Pure Forestry)**:
    - *Candidate*: Simon M. Landhäusser et al. (2002) — *Leaf area renewal, root retention and carbohydrate reserves... following above‐ground disturbance*. (138 citations)
    - *Ambiguity*: A pure tree-physiology paper on Populus tremuloides in boreal forestry contexts; lacks any agricultural cropping or hazard-mitigation parameters.
    - *Proposal*: **Exclude** as it is too distal from agricultural agroforestry practices.
*   **Agroforestry Econometric Adoption Drivers**:
    - *Candidate*: K Stubblefield et al. (2026) — *Global agroforestry adoption: A meta-analysis of econometric-based studies*.
    - *Ambiguity*: A very high-quality meta-analysis, but focuses purely on econometric and socio-economic adoption drivers (tenure security, finance, credit access) rather than biophysical hazard-mitigation thresholds.
    - *Proposal*: **Exclude** from the T3 biophysical hazard database, but **Divert** and include in the M2b / T7 registers as a key reference for socio-economic enablers.

### 2. Borderline Inclusions (Proposed for acceptance)
*   **Temperate Biophysical Tolerances**:
    - *Candidate*: Ülo Niinemets & Fernando Valladares (2006) — *TOLERANCE TO SHADE, DROUGHT, AND WATERLOGGING OF TEMPERATE NORTHERN HEMISPHERE TREES AND SHRUBS*. (1204 citations)
    - *Ambiguity*: Extremely rich biophysical parameter datasets, but scoped to temperate, northern hemisphere tree species rather than tropical LMIC crops.
    - *Proposal*: **Include** as a global biophysical baseline reference (Medium/Low tier for LMIC transferability), but override it with tropical specific papers during synthesis when available.
*   **Windbreak Physical Wind Tunnel/Flow Models**:
    - *Candidate*: Dexin Guan et al. (2003) — *A wind-tunnel study of windbreak drag*. (127 citations)
    - *Ambiguity*: Primarily a mechanical physics and wind tunnel study of drag coefficients rather than a field trial of crop yields.
    - *Proposal*: **Include** to supply the physical wind speed reduction thresholds for `agroforestry__linear_boundary` (F4) windbreaks, but tag as `practice_technology` and `claim_basis = figure_read/modelled`.

---

## Sign-off & Audits

| Step / Audit | Date | Sign-off / Rationale |
|---|---|---|
| **Initial Discovery Log** | 2026-06-15 | Pete Steward (Team Lead) · Codex (operator) |
| **Manual Search Audit Cross-Check** | 2026-06-15 | Pete Steward (Team Lead). Cross-checked against 10 Google Scholar meta-analyses (Patil 2025, Abebaw 2025, Kuyah 2019, Stubblefield 2026, Castle 2021, De Beenhouwer 2013, Ngaba 2024, Scordia 2023, Niether 2020, Baier 2023). Confirmed 8/10 are included/screened for T3, 1 is active under T6 (`castle_sr_2021`), and 1 is excluded (`Scordia 2023` - European Mediterranean focus, crop productivity vs biophysical hazard). Documented human-in-the-loop review. |
