# Water Harvesting & Conservation — NbS Recipe

*Canonical recipe pattern. Module: Water & Wetland Systems · Practice: Water Harvesting and Conservation.*

*Originally authored by Benson Kenduiywo (May 2026). Treated as the template for all other recipes.*

> **Companion documents:**
> - Methodological framework: [`../framework.md`](../framework.md)
> - Schema rows: `schema/recipes/water_harvesting/` *(to be populated)*
> - Source docx (canonical original): `2_Technical_&_Data/Methodology/Claude/Spatial_Methodological_Plan_Water_Harvesting_NbS.docx`

---


## 1. Context and Scope


This methodological plan operationalises the generic Methodological Plan for Geospatial Scoping of Nature-based Solutions (NbS) for the Water Harvesting and Conservation (WH&C) practice within the Water & Wetland Systems cluster. It is intended to support early-stage scoping analyses that identify, screen and prioritise areas where WH&C interventions may be biophysically suitable, climate-relevant and operationally feasible. It is not a feasibility or engineering design tool.

Water Harvesting and Conservation comprises a heterogeneous set of NbS subpractices that capture, store, infiltrate and conserve runoff at the plot, field, micro-catchment and watershed scales. Our stocktake review identified the following recurring subpractices across 85 reviewed studies: in-situ rainwater harvesting (contour bunds, contour ridges, tied ridging, mulching, conservation tillage, planting pits, micro-basins, Negarim, Zai pits); micro-catchment systems (semi-circular bunds, eyebrow terraces, runoff strips); ex-situ structures (farm ponds, percolation tanks, check dams, gully plugs, nala bunds, earthen dams, recharge dams); terracing systems (bench terraces, contour stone terraces, stone bunds, fanya juu, gradoni); and rooftop or domestic harvesting (cisterns, reservoirs).

Across these subpractices, three convergent suitability questions recur: (i) where does sufficient runoff generate to make harvesting hydrologically meaningful, (ii) where can the runoff be physically captured, stored or infiltrated given terrain, soil and land-cover conditions, and (iii) where is the intervention strategically desirable given demand, infrastructure access, climate risk and socio-economic context. The methodology proposed here translates these questions into a structured set of input variables, fuzzy-standardised criteria and an MCDA aggregation that begins with expert weights and is optimised through objective weighting (CRITIC and Entropy).


### 1.1 Position within the generic methodological framework


This module follows the eleven-phase logic of the generic plan (Phases 0–11). It customises Phases 2 (input data inventory and variable selection), 3 (criteria definition and suitability logic), 4 (spatial pre-processing and standardisation), 6 (climate and disaster risk profiling), 7 (criteria weighting) and 8 (spatial MCDA integration) to the specific decision logic of WH&C. Phases 0, 1, 5, 9, 10 and 11 are inherited from the generic plan and require only practice-specific parameter setting.


## 2. Recommended Input Variables for Suitability Analysis


The variable set proposed below is derived from a structured synthesis of 85 peer-reviewed studies supplemented with the recommendations of the generic methodological plan. Variables are organised into six thematic categories, distinguishing core variables (used in the majority of reviewed studies and considered minimum-data requirements) from optional variables (recommended where data and context permit).


### 2.1 Variable categories


Topographic and morphometric variables — slope, elevation, aspect, curvature, Topographic Wetness Index (TWI). These govern overland-flow generation, ponding potential and the structural feasibility of water-harvesting structures. The TWI is computed as:

TWI=ln⁡atanβ
Where:

		a= upslope contributing area per unit contour length

		β= slope angle in radians

High TWI values indicate:

		water accumulation zones

		wetter soils

		potential runoff concentration areas

		suitable locations for:

		infiltration trenches

		water pans

		check dams

		recharge structures

		riparian restoration

Hydrological variables — runoff depth/coefficient, drainage density, stream order, flow accumulation, distance to streams. These define where harvestable runoff converges and the hierarchical position within the drainage network.

Soil and lithology variables — soil texture, hydrologic soil group (HSG), soil depth, soil permeability, lithology, lineament density. These determine infiltration capacity, structural integrity for impoundment and groundwater-recharge potential.

Climatic variables — annual rainfall, rainfall intensity/erosivity, potential evapotranspiration (PET), aridity index. These define the supply side of the water balance.

Land cover and ecological variables — land use/land cover (LULC), NDVI/vegetation cover, soil moisture index. These act as both suitability criteria and exclusion masks (e.g. settlements, water bodies, protected areas).

Socio-economic, infrastructure and risk variables — population density, distance to settlements, distance to roads, agricultural land, flood/drought hazard, climate-change projections. These determine demand, accessibility, feasibility and exposure.


### 2.2 Master variable table


Table 1 presents the master set of input variables recommended for WH&C suitability analysis. For each variable the table specifies its definition and purpose, its relevance to WH&C, its expected influence on suitability (positive, negative or non-monotonic), the recommended fuzzy-membership normalisation, and the suggested spatial data source or proxy dataset.


**Table 1. Master input-variable table for Water Harvesting and Conservation NbS suitability analysis. Variables synthesised from 85 stocktake studies and aligned with the generic methodological plan.**


Input variable

Definition / purpose

Relevance to WH&C NbS

Expected influence on suitability

Recommended normalisation (fuzzy membership)

Suggested spatial data source / proxy dataset

Slope (gradient, %)

Rate of elevation change derived from a DEM; typically expressed in degrees or percent.

Controls overland flow velocity, sediment transport, and the structural feasibility of impoundment, terracing and bund construction. Gentle slopes favour ex-situ structures (ponds, check dams) while moderate slopes favour terracing.

Negative (non-monotonic): low–moderate slopes optimal; very flat areas drain poorly; steep slopes are unsuitable.

Decreasing sigmoid (or generalised bell-shaped centred on 1–8% for ponds; 5–25% for terraces).

SRTM 30 m, ASTER GDEM 30 m, ALOS PALSAR 12.5 m, Copernicus GLO-30.

Elevation (DEM)

Height above mean sea level used both directly and as the base layer for derived terrain variables.

Provides the basis for delineating sub-catchments, deriving slope, aspect, curvature, flow direction and stream order. Elevation thresholds may also exclude unsuitable upland or coastal areas.

Context-dependent (typically used as derived input rather than direct criterion).

Min–max linear normalisation; or used as constraint mask for elevation-bounded subpractices.

SRTM 30 m, ASTER GDEM 30 m, ALOS PALSAR 12.5 m, Copernicus GLO-30.

Aspect

Compass direction of slope face derived from the DEM.

Influences solar exposure, evaporation losses from open ponds and vegetation regeneration on terraces. North-facing aspects in the Northern Hemisphere typically reduce evaporation.

Non-monotonic (hemisphere-dependent).

Reclassified categorical fuzzy membership; or generalised bell on preferred azimuth.

Derived from any DEM (SRTM, ASTER, ALOS).

Curvature

Second derivative of the elevation surface; profile and plan curvature indicate concavity/convexity.

Concave areas (negative curvature) accumulate water and sediment, favouring percolation tanks and farm ponds; convex areas shed water.

Negative curvature → positive influence on suitability for storage structures.

Decreasing sigmoid on signed curvature (concave → high suitability).

Derived from DEM in ArcGIS / QGIS / GRASS r.slope.aspect.

Topographic Wetness Index (TWI)

ln(a/tan β), where a is upslope contributing area and β is local slope; indicates soil-moisture potential.

Identifies hydrologically convergent zones suitable for ponding, percolation and ephemeral wetland formation.

Positive.

Increasing sigmoid.

Derived from DEM via SAGA, GRASS, or WhiteboxTools.

Runoff depth / Surface runoff

Depth of overland runoff per unit area, typically estimated using SCS-CN, SWAT, or rainfall-runoff regression.

The principal supply-side variable: areas with high runoff generation are prioritised for ex-situ harvesting; low-runoff areas may favour in-situ moisture conservation.

Positive (monotonic).

Increasing sigmoid or linear (after outlier capping at 95th percentile).

SCS-CN method (USDA-NRCS) using LULC + HSG + rainfall; SWAT model outputs; CHIRPS-driven runoff models.

Curve Number (CN)

Empirical SCS-CN coefficient (30–100) summarising land cover and hydrologic soil group response to rainfall.

Direct proxy for runoff potential; high CN indicates impervious or poorly-draining surfaces that generate harvestable runoff.

Positive for ex-situ structures; negative for recharge-oriented subpractices.

Increasing sigmoid (ex-situ); decreasing sigmoid (recharge).

USDA-NRCS National Engineering Handbook; derived from HWSD + LULC layers.

Drainage density

Total length of streams per unit area (km/km²); typically derived from DEM-extracted drainage network.

Indicates the efficiency of runoff drainage. Moderate-to-high drainage density supports check dams and percolation tanks; very high density may indicate erosional landscapes.

Positive (non-monotonic at extremes).

Generalised bell-shaped (peak at moderate density) or increasing sigmoid.

Derived from DEM (Strahler/Horton extraction) using ArcHydro, SAGA, or GRASS.

Stream order (Strahler)

Hierarchical classification of streams in a network (1st-, 2nd-order, …).

Different subpractices align with different orders: gully plugs and contour bunds on 1st–2nd order; check dams on 2nd–3rd; farm ponds on 3rd–4th; small dams on 4th–5th.

Subpractice-specific (non-monotonic).

Reclassified categorical or generalised bell-shaped on preferred order.

Derived from DEM using D8 flow algorithm and Strahler ordering.

Flow accumulation

Number of upslope cells draining into each cell.

Identifies channel-like convergence points and potential dam/pond sites along drainage lines.

Positive at moderate values; very high values indicate large rivers (typically excluded).

Generalised bell-shaped or capped increasing sigmoid.

Derived from DEM (D8 or D-infinity); ArcHydro, SAGA, GRASS r.watershed.

Distance to streams / drainage proximity

Euclidean distance from each pixel to the nearest mapped stream.

Sites for ex-situ structures are typically located along or close to drainage lines; in-situ practices are placed on inter-stream slopes.

Negative for ex-situ (closer is better); positive for in-situ.

Decreasing sigmoid (ex-situ) or increasing sigmoid (in-situ).

Euclidean distance on DEM-derived stream network.

Lineament density

Density of linear geological features (fractures, faults) per unit area.

Proxy for groundwater-recharge potential; high lineament density supports artificial recharge subpractices and percolation tanks.

Positive.

Increasing sigmoid.

Derived from Landsat/Sentinel imagery (edge-enhancement); national geological surveys.

Annual rainfall

Mean annual precipitation (mm/yr) over a multi-decadal climatology.

Sets the upper bound of harvestable water; semi-arid regions (250–800 mm) are typical priority zones for WH&C investment.

Positive (monotonic up to a saturation threshold beyond which other practices dominate).

Increasing sigmoid with upper plateau, or generalised bell-shaped (peak in semi-arid range).

CHIRPS 5 km, WorldClim v2 1 km, ERA5-Land 9 km, TRMM 3B43, national meteorological gauge networks.

Rainfall intensity / erosivity (R-factor)

Energy and intensity of rainfall events; RUSLE R-factor or extreme-rainfall indices.

High intensity events generate the largest harvestable runoff but also drive erosion and structure failure; informs design return periods.

Positive for runoff generation; negative for structural risk.

Generalised bell-shaped (moderate intensity favoured) or sigmoid-paired surfaces.

GloREDa global R-factor; CHIRPS-based intensity indices; national daily rainfall records.

Potential Evapotranspiration (PET)

Reference evapotranspiration as estimated by Penman–Monteith, Hargreaves, or remote-sensed proxies.

Determines storage losses from open-water structures (ponds, dams) and irrigation demand satisfied by harvesting.

Negative (high PET reduces structure performance).

Decreasing sigmoid.

MOD16 (500 m), TerraClimate (4 km), CGIAR-CSI Global Aridity dataset.

Aridity index (P/PET)

Ratio of annual precipitation to potential evapotranspiration; UNEP classification.

Identifies water-scarce areas where WH&C delivers the highest marginal benefit; semi-arid (0.2–0.5) is the typical priority band.

Generalised bell-shaped (peak at semi-arid).

Generalised bell-shaped membership.

CGIAR-CSI Global-Aridity v3, TerraClimate.

Soil texture

USDA textural class (sand, silt, clay percentages).

Governs infiltration vs. runoff partitioning and the structural integrity of earthen impoundments. Loamy and clay-loam soils favour pond floors; sandy soils favour recharge.

Subpractice-specific (categorical).

Reclassified categorical fuzzy membership per subpractice.

SoilGrids 250 m, HWSD v2, FAO DSMW, ISRIC AfSIS, national soil surveys.

Hydrologic Soil Group (HSG)

USDA HSG classification (A–D) based on infiltration capacity.

Direct input to SCS-CN runoff estimation and a primary determinant of pond bed sealing and recharge potential. HSG C/D favours runoff harvesting; A/B favours recharge.

Categorical (subpractice-specific).

Reclassified categorical (A=0.2, B=0.4, C=0.8, D=1.0 for runoff harvesting; reverse for recharge).

Derived from SoilGrids/HWSD using USDA-NRCS lookup; FAO HSG global maps.

Soil depth

Depth to bedrock or to a restricting horizon.

Deeper soils support larger storage volumes for in-situ practices and structural anchoring of bunds and terraces. Very shallow soils (<25 cm) constrain construction.

Positive (monotonic up to ~150 cm, then plateau).

Increasing sigmoid.

SoilGrids 250 m (bdod, bdricm), national soil surveys.

Soil permeability / saturated hydraulic conductivity (Ksat)

Rate at which water moves through saturated soil (cm/hr).

Critical control on infiltration losses from ponds (lower is better) and recharge potential (higher is better). Often estimated via pedo-transfer functions (Saxton & Rawls).

Subpractice-specific.

Decreasing sigmoid (ponds) or increasing sigmoid (recharge).

SoilGrids-derived (clay/sand/OC) via Saxton–Rawls PTF.

Soil clay content

Percentage clay in the topsoil/subsoil layer.

High clay content reduces seepage losses from ponds and check dams; very high clay may impede recharge and root development.

Generalised bell-shaped (~25–45% optimal for ponds).

Generalised bell-shaped membership.

SoilGrids 250 m clay content layer.

Soil organic carbon / soil moisture index

Topsoil organic carbon stock or remotely sensed surface moisture.

Indicator of soil health and antecedent moisture status; affects infiltration and conservation potential.

Positive.

Increasing sigmoid.

SoilGrids 250 m SOC; SMAP/SMOS soil moisture; Sentinel-1 backscatter-based moisture proxies.

Land Use / Land Cover (LULC)

Categorical map of dominant land cover (e.g. cropland, grassland, bare, forest, settlement, water).

Used both as a suitability criterion (croplands and rangelands prioritised) and as an exclusion mask (water bodies, settlements, dense forest excluded).

Categorical (subpractice-specific).

Reclassified categorical fuzzy membership; Boolean exclusion for water/built-up.

ESA WorldCover 10 m, Esri Land Cover 10 m, Copernicus GLC 100 m, MODIS MCD12Q1, national LULC.

NDVI / Vegetation cover

Normalised Difference Vegetation Index from optical remote sensing.

Proxy for runoff–infiltration partitioning (high NDVI promotes infiltration) and for identifying degraded areas where WH&C delivers high uplift.

Non-monotonic: very low NDVI = degraded (high priority); very high NDVI = forest (often excluded).

Generalised bell-shaped (peak at sparse-to-moderate cover).

MODIS MOD13Q1, Sentinel-2 NDVI composites, Landsat-8/9 NDVI.

Lithology / geology

Bedrock type and weathering characteristics from geological maps.

Determines structural stability for dams and reservoirs and the recharge potential of underlying aquifers.

Categorical (subpractice-specific).

Reclassified categorical fuzzy membership.

USGS World Geological Map, OneGeology, national geological surveys.

Distance to roads

Euclidean distance to the nearest road or accessibility-weighted travel time.

Influences cost of construction, material transport and maintenance access. Areas closer to roads are more feasible for ex-situ structures.

Negative (closer is better).

Decreasing sigmoid.

OpenStreetMap, GRIP global roads, national road network shapefiles.

Distance to settlements

Euclidean distance to nearest village or built-up area.

Captures both demand (proximity raises usefulness) and constraint (very close may compete with built infrastructure).

Generalised bell-shaped (moderate distance optimal).

Generalised bell-shaped membership.

GHSL Settlement Layer, WorldPop, OSM places, national census.

Population density

Number of inhabitants per km².

Indicator of demand for harvested water and labour availability for construction; very high density may indicate urban areas where WH&C is excluded.

Generalised bell-shaped.

Generalised bell-shaped (rural-peri-urban peak).

WorldPop 100 m, GHS-POP 100 m, LandScan 1 km.

Agricultural land / cropland intensity

Cropland extent or cropping intensity (cropping frequency per year).

WH&C delivers the highest agronomic uplift on cultivated lands; cropland masks define the addressable footprint.

Positive.

Increasing sigmoid; or used as Boolean inclusion mask.

GFSAD 30 m cropland; ESA WorldCereal; national cropland maps.

Flood hazard / susceptibility

Probabilistic flood-extent maps or flood-susceptibility indices.

Identifies zones where structures are at risk of failure or where WH&C delivers a co-benefit by attenuating flood peaks.

Dual interpretation: positive (intervention need) but negative (structural risk above design return period).

Generalised bell-shaped or paired sigmoid surfaces.

JRC GHFP global flood hazard, FATHOM, Aqueduct Floods, national flood-zone maps.

Drought hazard / SPEI

Standardised Precipitation-Evapotranspiration Index or drought-frequency index.

Identifies areas of greatest WH&C need; high drought frequency raises priority for in-situ moisture conservation.

Positive (monotonic).

Increasing sigmoid.

SPEIbase v2.9 0.5°, EM-DAT drought events, CHIRPS-based SPI/SPEI.

Climate-change projection (rainfall change)

Projected change in mean annual rainfall and rainfall variability under representative scenarios (e.g. SSP2-4.5, SSP5-8.5).

Future-proofs siting decisions; areas with stable or increasing reliability are preferred. Used either as overlay or weighted criterion (per generic plan Phase 6).

Context-dependent.

Sigmoid on robust ensemble change signals; or scenario overlay.

CMIP6 ensembles (NEX-GDDP-CMIP6 25 km), CORDEX regional projections, World Bank Climate Change Knowledge Portal.


## 3. Variable Descriptions and Rationale


This section elaborates the rationale for each variable category and clarifies how it links to the underlying biophysical and decision logic of WH&C. Variable selection is grounded in three observations from the stocktake review: (i) WH&C is the single most data-intensive NbS category, with 82 of 85 reviewed studies relying on elevation/terrain layers, 81 on soil/geology, 77 on hydrology and 77 on LULC; (ii) the prevailing analytical paradigm is MCDA combined with SCS-CN runoff modelling; and (iii) the most scalable studies rely on transparent, globally-available raster inputs.


### 3.1 Topographic and morphometric variables


Topographic variables anchor the structural feasibility of WH&C. Slope is the single most consistently used variable in the reviewed literature, appearing in essentially every spatial analysis. Slope governs runoff velocity, sediment delivery, and the practical limits of bund, terrace and pond construction. Most reviewed studies adopt thresholds in the 0–5% range for ex-situ ponds, 5–15% for check dams and 15–30% for terracing. Aspect, curvature and TWI provide finer-grained discrimination of micro-topographic ponding and shading conditions. Elevation itself is rarely a direct criterion but is the foundational layer from which the others are derived.


### 3.2 Hydrological variables


Hydrological variables operationalise the runoff supply and its routing. Runoff depth — typically estimated using the SCS Curve Number method with land-cover, hydrologic soil group and rainfall inputs — appears in approximately two-thirds of stocktake studies and is the most influential single criterion in nearly all weighted MCDA frameworks. Drainage density, stream order and flow accumulation translate the runoff signal into a network position, supporting the matching of subpractice type to network hierarchy. Distance to streams and lineament density refine the placement of structures within sub-catchments and identify groundwater-recharge potential.


### 3.3 Soil and lithology variables


Soil variables determine the partition between runoff and infiltration and the structural integrity of earthen structures. Soil texture and hydrologic soil group together explain most of the variability in runoff response and are essential inputs to the SCS-CN model. Soil depth and clay content govern the storage and sealing properties of pond beds, while permeability and lithology determine recharge potential. Where field measurements are unavailable, SoilGrids-derived properties combined with the Saxton–Rawls pedo-transfer functions provide a consistent global dataset.


### 3.4 Climatic variables


Climatic variables define the supply side of the water balance. Annual rainfall determines the upper bound of harvestable water, and the most cost-effective WH&C investments are typically concentrated in the 250–800 mm/yr semi-arid band, where harvesting fills a meaningful gap relative to potential evapotranspiration. Rainfall intensity informs design return periods and erosion risk. PET and aridity index frame the demand side and the relative scarcity context, with the aridity-index bell-curve identifying the priority semi-arid zone.


### 3.5 Land cover and ecological variables


LULC provides both a suitability surface and a Boolean exclusion mask. Croplands and rangelands are typically prioritised, while water bodies, settlements, dense forests, glaciers and protected areas are excluded. NDVI complements LULC by providing a continuous measure of vegetation cover that helps identify degraded areas with high WH&C uplift potential.


### 3.6 Socio-economic, infrastructure and risk variables


Socio-economic and infrastructure variables capture demand, accessibility and feasibility. Distance to roads is a near-universal criterion in the stocktake literature, used as a proxy for construction and maintenance cost. Distance to settlements and population density capture demand. Climate hazard variables (flood, drought, climate-change rainfall projections) anchor the climate-risk profiling described in Phase 6 of the generic plan and ensure that prioritisation accounts for both current need and future robustness.


## 4. Potential Data Sources and Spatial Data Types


Table 2 summarises the recommended global and regional datasets, with their spatial resolution, temporal coverage and data type. Where multiple datasets exist for the same variable, preference is given to those that are: (i) globally consistent, (ii) regularly updated, (iii) openly licensed, and (iv) demonstrated as scalable in the stocktake review.


**Table 2. Recommended global and regional spatial datasets for WH&C suitability analysis.**


Variable / theme

Recommended dataset

Native resolution

Data type

Source / GEE Asset ID

Elevation, slope, aspect, curvature, TWI

SRTM v3

30 m

Raster

‘USGS/SRTMGL1_003’

Rainfall (annual, daily)

CHIRPS v2.0

5 km / daily, monthly

Raster timeseries

"UCSB-CHG/CHIRPS/PENTAD"

Rainfall + temperature + ET

TerraClimate

4.6 km / monthly 1958–present

Raster timeseries

“IDAHO_EPSCOR/TERRACLIMATE”

aridity index (precipitation/PET)

Compute from TerraClimate

30 arc-sec

Raster

'IDAHO_EPSCOR/TERRACLIMATE'

LULC

Generate from Dynamic World

10 m / 2020, 2021

Raster (categorical)

"GOOGLE/DYNAMICWORLD/V1"

NDVI

NOAA

5566 m

Raster timeseries

"NOAA/CDR/VIIRS/NDVI/V1")

Soil properties (texture, OC, depth, clay, sand)

ISRIC SoilGrids 2.0

250 m

Raster (continuous)

"ISRIC/SoilGrids250m/v2_0"

Drainage network, stream order

HydroSheds

90 m

Vector / raster

Drainage direction:  'WWF/HydroSHEDS/03DIR

Flow accumulation: 'WWF/HydroSHEDS/15ACC'

Global rivers (reference)

HydroSHEDS / HydroRIVERS

15 arc-sec/500 m

Vector

"WWF/HydroSHEDS/v1/FreeFlowingRivers"

Population

WorldPop

100 m / annual

Raster

'WorldPop/GP/100m/pop'

Settlements / built-up

Extract from Dynamic world

10 m / multi-year

Raster

"GOOGLE/DYNAMICWORLD/V1"

Roads

OpenStreetMap (OSM) + GRIP4

Vector (variable)

Vector linestring

“projects/sat-io/open-datasets/GRIP4/Africa”

Cropland

Extract from Dynamic world

30 m / 10 m

Raster (categorical)

"GOOGLE/DYNAMICWORLD/V1"

Flood hazard

JRC Global Human Flood Plains; FATHOM

30 m–90 m

Raster

JRC; commercial (FATHOM)

Drought (PDSI)

Terraclimate

4638.3 m 1958–

Raster timeseries

"IDAHO_EPSCOR/TERRACLIMATE"

Climate projections

NEX-GDDP-CMIP6

25 km / daily 1950–2100

Raster timeseries

"NASA/GDDP-CMIP6"


## 5. Normalisation Using Fuzzy Membership Functions


All criteria must be standardised to a common 0–1 scale before aggregation, in line with Phase 4 of the generic methodological plan. The choice of fuzzy-membership function should reflect the relationship between the variable and WH&C suitability. Five families of functions are used in this module, drawn directly from the generic plan, and are summarised below.


### 5.1 Recommended membership functions


Increasing sigmoid — used for variables where suitability rises with the variable value and saturates at high values. Examples: runoff depth, drainage density, rainfall (up to a saturation), TWI, soil depth, lineament density, drought hazard, distance to streams (in-situ), agricultural land. Parameter c sets the inflection point and a controls the steepness.

Decreasing sigmoid — used where suitability falls with increasing variable value. Examples: slope (above an optimum), distance to roads, distance to streams (ex-situ), PET, soil permeability for ponds. Implemented as the complement of the increasing sigmoid.

Generalised bell-shaped — used where suitability peaks at an intermediate value and declines on both sides. Examples: aspect, curvature, drainage density (extreme cases), rainfall intensity, aridity index, soil clay content, distance to settlements, population density, NDVI, flow accumulation.

Linear (min–max) — used when no clear non-linear threshold is defensible or where data are already pre-classified. Suitable as a simple default for elevation when used directly.

Reclassified categorical — used for categorical variables (LULC, HSG, soil texture, lithology) where each class is assigned a fuzzy membership value derived from expert consensus or stocktake-evidence priors.


### 5.2 Practice-specific normalisation guidance


Where a variable's relationship to suitability differs across subpractices (e.g. soil permeability, distance to streams, hydrologic soil group), the fuzzy parameters should be set per-subpractice. The recommended approach is to maintain a master parameter table (Table 1) that lists default fuzzy parameters for each variable–subpractice combination and to allow the parameters to be overridden by TTL expert input during Phase 1 problem framing.


### 5.3 Sigmoid parameterisation example


Using the sigmoid function S(x) = 1 / (1 + exp(−a(x − c))), recommended starting parameters for runoff depth (per stocktake review) are c = 50 mm (inflection at the median runoff depth in dryland WH&C studies) and a = 0.05 (gentle transition). For slope, a decreasing sigmoid with c = 8% and a = −0.4 captures the consensus suitability decline above the gentle-slope threshold for ex-situ structures. These defaults should be calibrated to the study area distribution during Phase 4.


## 6. Weighting Approaches for the MCDA


Following Phase 7 of the generic plan, the WH&C module adopts a hybrid expert-then-objective weighting strategy. Subjective weighting (AHP-derived expert weights) is used to structure the decision problem, document the rationale and elicit Task Team Leader (TTL) preferences. Objective weighting (CRITIC and Entropy) is then applied to optimise weights against the empirical information content and contrast of the input rasters in the study area. This combination preserves a defensible decision logic while reducing the sensitivity of the results to expert subjectivity.


### 6.1 Step 1 — Expert-based starting weights (AHP)


AHP pairwise comparisons are conducted across the criteria hierarchy (Goal → criteria → sub-criteria → indicators). Recommended top-level criteria for WH&C are (a) runoff supply, (b) physical feasibility, (c) demand and accessibility, and (d) climate risk. Pairwise judgments are elicited from TTLs and technical specialists using the standard 1–9 Saaty scale. The consistency ratio (CR) is calculated and required to be below 0.10; if CR ≥ 0.10, the elicitation is repeated. AHP weights serve as the prior weight vector w_AHP.


### 6.2 Step 2 — Objective weighting


Two objective methods are recommended, applied independently and reconciled via averaging or scenario analysis.


#### 6.2.1 CRITIC (Criteria Importance Through Intercriteria Correlation)


CRITIC weights reward criteria with high contrast (information content) and low redundancy (low correlation with other criteria). For each criterion j, the CRITIC weight is computed as:

C_j = σ_j × Σ_k (1 − r_jk)  where σ_j is the standard deviation of the standardised criterion j and r_jk is the Pearson correlation between criteria j and k. Weights are then normalised: w_CRITIC_j = C_j / Σ_j C_j.

CRITIC is recommended where input layers are partially correlated (a common occurrence in WH&C, where slope, drainage density and TWI all derive from the same DEM). It penalises this redundancy automatically and is therefore a useful corrective to naïve expert weighting.


#### 6.2.2 Entropy weighting


Entropy weighting assigns higher weights to criteria whose values vary more across the study area. The Shannon-entropy weight for criterion j is:

E_j = −(1/ln n) × Σ_i p_ij × ln(p_ij)  where p_ij = x_ij / Σ_i x_ij and n is the number of pixels. The entropy-derived weight is w_Entropy_j = (1 − E_j) / Σ_j (1 − E_j).

Entropy is recommended where the analyst seeks a fully data-driven weight set that requires no expert input. It is well-suited to WH&C analyses across heterogeneous landscapes where the most discriminating criteria are not known a priori.


### 6.3 Step 3 — Weight reconciliation


The recommended default is to compute a hybrid weight as a convex combination of expert and objective weights:

w_final = α × w_AHP + (1 − α) × w_objective  where α ∈ [0, 1] is set by TTL preference. A default of α = 0.4 is recommended (60% objective, 40% expert), with sensitivity tested over α ∈ {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} during Phase 9.

Alternative reconciliation strategies include: (i) running CRITIC and Entropy in parallel and reporting both surfaces, (ii) using AHP only as a structuring tool while reporting only the objective-weighted surface, or (iii) using the AHP weights as priors in a constrained optimisation that maximises an information-theoretic objective.


### 6.4 Documentation and reproducibility


All weight derivations must be documented in a weight-derivation log, including: pairwise comparison matrices, consistency ratios, standardisation parameters used in CRITIC and Entropy, correlation matrices, and the final weight table for each scenario. The log is a required output of Phase 7 and underpins the sensitivity analysis in Phase 9.


## 7. Suitability Analysis Considerations, Assumptions and Constraints


### 7.1 Aggregation rule


The default aggregation rule is the weighted linear combination (WLC) used in Phase 8 of the generic plan: S_i = Σ_j w_j × x_ij, where x_ij is the fuzzy-standardised value of criterion j at pixel i and w_j is the final weight. WLC is computationally efficient, transparent and compatible with the SpatMCDA R workflow. Where strong limiting factors are identified during the structural-suitability phase (e.g. slope > 30%, water bodies, dense forest, settlements, protected areas), a rule-of-minimum aggregation is applied as a Boolean filter prior to WLC.


### 7.2 Subpractice-specific suitability surfaces


Because WH&C encompasses a diverse range of subpractices with different biophysical envelopes, the recommended approach is to compute multiple suitability surfaces — one per subpractice family (in-situ, micro-catchment, ex-situ structures, terraces) — rather than a single aggregate surface. The subpractice families share a core set of variables but differ in normalisation parameters and weighting. A composite map can then be derived by taking the maximum across subpractices, or by retaining the per-subpractice surfaces as parallel decision layers.


### 7.3 Structural exclusion masks


Prior to MCDA aggregation, a set of structural exclusion masks is applied. Recommended exclusions are: water bodies (lakes, rivers, reservoirs); built-up and settled areas; protected areas (WDPA strictly protected categories I-IV unless explicitly co-managed); dense closed-canopy forest (NDVI > 0.7 and tree cover > 60%); glaciers and snow; slopes > 30% (subpractice-dependent); soil depth < 25 cm (for structures requiring excavation); and known geohazard zones.


### 7.4 Climate risk integration


In line with Phase 6 of the generic plan, climate risk is treated either (a) as an additional criterion within the MCDA, weighted alongside the other criteria, or (b) as a separate overlay applied post-aggregation. The recommended default for WH&C is a hybrid: drought hazard is included as a positive criterion within the MCDA (high drought = high need), while flood hazard above a 50-year return period is applied as a constraint masking out high-risk pixels for ex-situ structures.


### 7.5 Key assumptions


The fuzzy-membership functions in Table 1 represent stocktake-evidence consensus and may require local recalibration where empirical data are available.

Globally available datasets at 100 m–1 km resolution are sufficient for scoping; sub-100 m analysis is rarely robust given input-data uncertainty and is reserved for feasibility-stage work.

The SCS-CN runoff estimation assumes infiltration and storage processes are adequately represented by the lookup tables, which is a known limitation in tropical and karstic environments.

Input layers reflect a multi-year climatology; intra-annual variability and event-scale dynamics are not represented in the suitability surface and require process-based supplementary models.

Land tenure, customary rights and governance constraints are not represented in core variables and should be addressed during the validation phase (Phase 11).


### 7.6 Constraints and limitations


Many globally available soil and hydrology layers carry substantial uncertainty (especially HWSD-derived HSG and SoilGrids depth-to-bedrock); uncertainty propagation should be examined in the Phase 9 sensitivity analysis.

Stream-network extraction from coarse DEMs (≥ 30 m) underestimates first-order tributaries and may bias drainage density downward. Use of higher-resolution DEMs (e.g. ALOS PALSAR 12.5 m) is encouraged where available.

LULC products differ in their treatment of mosaic landscapes; cross-validation between two LULC products is recommended for studies in heterogeneous agricultural areas.

CRITIC and Entropy weights are dependent on the spatial extent and may shift if the analytical extent is changed; this should be reported transparently.

The framework is a scoping tool. It does not replace site-specific hydrological modelling, geotechnical assessment, or community consultation, all of which remain essential for project design.


## 8. Indicative Workflow Summary


The following sequence operationalises the WH&C suitability analysis. It mirrors Phases 0–11 of the generic methodological plan and identifies the practice-specific configurations introduced by this module.


**Table 3. Indicative phase-by-phase workflow for the Water Harvesting and Conservation NbS module.**


Phase

Activity

WH&C-specific configuration

Outputs

0

Module definition

Confirm WH&C subpractice typology (in-situ, micro-catchment, ex-situ, terraces, rooftop) and select active subpractices for the analysis.

WH&C subpractice list, decision register

1

Problem framing

Define geography (basin, country, ecological zone), priority subpractice(s), decision-support purpose (national scoping vs basin prioritisation).

Problem-framing note, study-area boundary

2

Variable selection

Apply Table 1 master variable list; mark core vs optional based on data availability.

Selected variable list, data-source register (Table 2)

3

Suitability logic

Define decision rules and fuzzy-membership parameters per subpractice (Table 1).

Suitability logic matrix, fuzzy-parameter table

4

Pre-processing

Reproject to common CRS (equal-area for area-weighted analyses, e.g. EPSG:6933); resample to target resolution (recommended 100 m or 250 m for national scoping); apply fuzzy normalisation.

Standardised raster stack (0–1)

5

Structural suitability

Apply exclusion masks (Section 7.3) and rule-of-minimum across structural variables (slope, soil depth, LULC).

Structural suitability map, exclusion mask

6

Climate risk profiling

Compute drought-hazard layer (SPEI), flood-hazard mask (50-yr return period); integrate per Section 7.4.

Climate risk surfaces, hazard masks

7

Weighting

Apply hybrid AHP→CRITIC/Entropy weighting (Section 6).

Weight matrix, weight-derivation log

8

MCDA integration

Compute weighted-linear-combination suitability surface per subpractice; produce composite max-across-subpractice surface.

Subpractice suitability rasters, composite surface

9

Sensitivity analysis

Vary α (expert↔objective), perturb fuzzy parameters by ±20%, vary exclusion-mask thresholds.

Sensitivity plots, uncertainty maps

10

Classification

Translate continuous suitability to actionable classes (very high, high, moderate, low) using natural breaks or quantiles; identify hotspots.

Priority classes, hotspot maps

11

Validation

Expert review with TTLs; comparison with known WH&C interventions where available.

Validation note, revised maps


## 9. Closing Notes


This methodological plan is intended as a living document. The default variables, fuzzy parameters, weights and exclusion masks proposed here represent the consensus of the WH&C stocktake evidence base. They should be reviewed and adapted for each application based on (i) decision context defined in Phase 1, (ii) data availability, (iii) TTL expert input, and (iv) feedback from Phase 11 validation. Documentation of all parameter choices in the weight-derivation log and the suitability-logic matrix is essential to ensure the transparency and reproducibility on which the scalability of the framework depends.



---

## Version history

- **v0.1** (May 2026) — initial port of Benson's canonical recipe into the repo. Source: `Spatial_Methodological_Plan_Water_Harvesting_NbS.docx`. Some structural cleanup; analytical content unchanged.
