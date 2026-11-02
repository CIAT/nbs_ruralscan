# IUFRO World Series 34: independent T4 adversarial review

Date: 2026-11-02. Ruleset: v1.9.2; T4 review contract v1.6.16.
Source: `pipeline/staging/t4_primary_guidance_20261102/iufro_ws34.pdf` and its native-page text JSON.
Scope: native pages 30–52 inclusive (printed 27–49), Chapters 4 and 5. All 23 pages read. Table images inspected at native 33, 34, 43, 45, 46, 47, 48 and 52. These include every continuation of Tables 4.1 and 5.2. Parent owns whole-source coverage and admission decisions. No staged EV payload was supplied for this review; this is a source-level omissions/scope review, not validation of subsequently authored units.

## Verdict

No executable T4 response function occurs in these chapters. No practice-level suitability calculation or fitted model is demonstrated here. The ecological guidance does support directional mechanisms, but exact-variable mapping, practice isolation and attribution must precede admission. Do not claim that zero immediately admissible units means no evidence was found.

Strongest potentially new material is native 37, section 4.3.1: competing vegetation can prevent natural regeneration and reduce planted-seedling survival; grazing animals can impede restoration. Both warrant raw-property inventories with negative directions. No exact competition-pressure or herbivory-pressure VONT mapping was found in the current ontology. Do not map them to NDVI, livestock presence, or a generic grazing-system gate. They are holds, not silent exclusions. Existing `regeneration_potential` is not a synonym for vegetation competition or herbivory pressure.

Native 37 seed-source paragraph mixes natural and artificial regeneration, nurseries, ANR enrichment and agroforestry. Unlike WRI's explicitly passive Box 5, it is not a clean additional passive-regeneration card. Table 4.1's ecological rows explicitly cite IUCN and WRI (2014); they cannot count as independent replication of the WRI/ROAM guidance family.

## Three independent assessments

| Passage | Variable use | Direction | Calibration / scope disposition |
|---|---|---|---|
| Native 30–31, Fig. 4.1 | Reported global restoration opportunity typology based on human density; source Minnemeyer 2011 / Laestadius 2012 | Different opportunity types, not a continuous suitability response | Preserve density/radius values and lineage; global prioritisation/typology, not family-specific biophysical threshold |
| Native 34, Table 4.1 ecological row 1; native 37 opening | Soil, water, climate and wildfire named as conditions to match restoration methods to | Unclear for each named variable; no measured soil/water/climate variable specified | Raw bundle hold. Do not manufacture pH, annual rain, mean annual temperature, soil drainage, or increasing/decreasing curves |
| Native 34, ecological row 2; native 37 competition paragraph | Competing vegetation/invasive plants and grazing animals identified as impediments | Increasing competing vegetation/herbivory impedes regeneration; negative direction retained in inventory | Metric/VONT hold. No abundance, cover, grazing intensity, or exclusion threshold. Broader restoration sentence does not isolate ANR from planting |
| Native 34, ecological row 3; native 37 seed paragraph | Native seeds/seedlings/source populations needed by several natural and artificial methods | Availability favourable; not quantitatively monotonic in any specified metric | Shared lineage; mixed natural supply and purchased/produced planting inputs. Do not default to passive or ANR |
| Native 48, Table 5.2 regeneration barriers; native 50–51 text | Herbivory, dispersal barriers, genetically diverse germplasm relevant to adaptation | Barriers impede some species' regeneration/migration; diverse seed sources enable adaptation | Species/genetic and adaptation scope, no practice-wide calibrated envelope; preserve primary references and qualitative directions |
| Native 51, suitability maps / seed transfer | Species selection/deployment under climatic envelopes | No individual species response supplied | Species-selection/tool referral; not use of a practice-level T4 model |
| Native 50, mangrove restoration | Sediment balance, altered dams/shore structures, space for landward recession | No simple monotonic sediment/salinity rule; removing migration obstruction can enable accommodation | Mangrove hydrological/geomorphic restoration pointer, family and exact metric unresolved; no new FR card |

Counts for these chapters: 0 demonstrated practice-level suitability models; 0 executable calibrated T4 functions; multiple supported qualitative mechanisms retained above. These are not independent-source counts or runtime weights.

## Material findings and exact source anchors

### 1. Keep WRI lineage explicit

Native 33–34 Table 4.1 names IUCN and WRI (2014) against all three ecological enabling conditions. Native 30 also directs readers to the Rapid Restoration Diagnostic Tool. Its attribution is not Hanson et al. (2015) automatically: retain the actual 2014 reference and shared institutional/source lineage pending bibliographic resolution. Funding acknowledgement also mentions WRI, but funding alone would not prove duplicate evidence. The copied/attributed criterion rows do establish a lineage concern. Preserve canonical-source reuse rather than adding independent support votes.

### 2. Preserve new negative ecological directions without false proxies

Native 37:

> Competing vegetation, especially invasive species, may prevent natural regeneration to restore large areas and reduce survival of planted seedlings (Stanturf et al., 2014a).

This is a limiting-factor claim, not only a background mention. Two recipients are named: natural regeneration and planted-seedling establishment. A family-resolved record could be possible after an exact competition-pressure variable exists and the distinction between untreated pressure and planned removal is recorded. No need to lose the direction merely because no curve exists. With current VONT, hold the raw claim. Attribute Stanturf et al. (2014a), not an independent IUFRO trial. The following Ghana/Chromolaena passage illustrates the mechanism; it does not establish a universal species envelope or grass-cover cutoff.

Same page:

> Grazing animals, both domestic and wild, can impede restoration if they are not excluded by fencing or active herding.

Record the conditional barrier and remedy. This is not proof that all landscapes with livestock are unsuitable, not stocking-density calibration, and not an unconditional legal exclusion. The remedy is management/Module 6; the untreated ecological pressure can be a T4 hypothesis only with matching metric/family semantics.

### 3. ANR enrichment is outside the project's ANR definition

Native 37 says ANR, including FMNR, benefits from enrichment with locally absent species. Current FAM defines assisted regeneration as relying on natural propagules, without planting; enrichment belongs to active planting. Do not tag the source's whole ANR paragraph to `forest_restoration__assisted_regeneration`. Nor map FMNR's living-rootstock variable to ordinary forest seed supply. Preserve the source's broader terminology as a scope caveat.

### 4. Numeric values are opportunity classes or scheduling, not thresholds

Native 30–31: remote restoration described using density <1 person/km² within a 500 km radius; wide-scale <10 people/km² with potential for closed forest; mosaic 10–100 people/km². Native 31 prose says remote forests more than 500 km from settlements. Retain both formulations; do not silently harmonise their spatial operators. They are cited global mapping categories, not passive/ANR/planting suitability functions.

Native 39: planting window one or two months; financing may be needed a year or more beforehand; Box 4.2 discusses breeding for more than 50 priority species. These are operational planning examples, not environmental class boundaries. Native 40's 200-year Danish recovery history is not required establishment duration.

### 5. Species deployment is not a general forest-restoration envelope

Native 50–51 discusses some species' herbivory/migration barriers and suitable climate-adapted provenances. The needed species suitability maps (Kindt et al. 2014/2015), breeding traits, seed zones and assisted migration remain species/genetic selection referrals. No named species × climate numeric response is supplied. Retain those referrals; do not create a practice-wide temperature, rainfall, drought or salinity curve from them.

### 6. Natural ecosystems and degraded forests require precise safeguards

Native 31 distinguishes native grasslands, which may not need trees, and states native forests should not be converted to commercial plantations. Native 35/44 warns against calling secondary forests degraded to permit oil-palm conversion. These are meaningful land-cover/safeguard statements, not universal bans on restoring all existing forest or all land labelled grassland. EO class mapping, baseline ecosystem identity and proposed treatment remain necessary. A plantation-conversion prohibition is not an ANR exclusion.

## Table coverage and disposition

Table 4.1, native 33–34: read both pages, including unreferenced entries. Multifunctional ecological rows (resilience, integrity, self-sustaining, ecosystem services) are restoration objectives. Economic rows concern financial/public benefits. Social rows concern histories, expectations, cultural communities and international commitments. Legal and supportive-policy rows address tenure, restoration requirements, forest-clearing restrictions, policy alignment, sectoral/infrastructure adaptation and enforcement. Preserve hard-legal versus soft-institutional distinctions; these are not quantified T4 masks. Ecological enabling triplet is accounted for above. Economic enabling rows concern competing demands/value chains. Social rows concern empowerment/benefit access. Institutional rows include coordination, maladaptation avoidance, risk policies, adaptive governance, know-how, transfer, administration and infrastructure; several carry no individual citation. Financial rows concern incentives, accessibility of funds and viability. All non-ecological rows are M2b/M6 or effect/goal referrals, not authorised new T4 units.

Table 5.1, native 43: all activity rows inspected. Carbon sequestration groups (area, biomass, soil), fossil-fuel/material substitution, burning efficiency and land-use emission controls describe mechanisms/actions. Recolonisation, farmer-assisted regeneration, agroforestry and afforestation remain separate methods. Spatial codes S/T/L/N mean species/stand/landscape/national, not suitability scores. No variable weighting/calibration exists here.

Table 5.2, native 45–48: all four pages inspected. Forest-area and carbon-stock sections include governance, protection, grazing/fire controls, logging, harvesting, soils, stand structure/composition, natural processes, diversity, planting material and markets. Biodiversity/hydrology sections include seed dispersers/herbivores, invasive removal, species-range edges, mixed planting, catchments/ridges, dams, hydroperiod, stream shade/buffers, erosion controls, mangrove salinity/sediment and shore structures. Rural-economy rows are outcome/implementation aims. Vulnerability/regeneration-barrier rows cover thinning, pests, coastal adjustments, adapted provenances, herbivory, connectivity, seed diversity, transfer zones and germplasm. Final rows address assisted population/range migration and refugia. I/A columns classify incremental/anticipatory adaptation, not measured success or suitability. Duplicated activities across objectives are not independent evidence. No row provides a practice-wide calibrated curve. The chapter text's native-50 reference to Table 5.3 for resistance/resilience appears inconsistent with table contents; actual corresponding activities are in 5.2. Preserve actual locator rather than repeat mistaken cross-reference.

Table 5.3, native 52: eight activity rows cover spontaneous assemblages, policy allowing non-native/transgenic trees, long-distance migration, synthetic/designer species, rewilding, replacement with non-native functions, neo-native ecosystems and novel assemblages. These are transformational adaptation options, not evidence authorising them as baseline-restoring NbS or T4 suitability criteria. Keep external/scope referrals, no threshold extraction.

Figure 4.1 native 31 is an opportunity-area bar chart, not response curves. Chapter photos (native 32, 35, 37, 39, 44, 49, 50) illustrate practices or sites, not numeric suitability legends. Box 4.1 native 36 is Ghana tenure/rights context; Box 4.2 native 39 is reproductive-material supply/breeding infrastructure.

## Admission recommendation

Do not add a duplicate WRI seed-source vote. Retain raw competing-vegetation and herbivory directions with exact mapping holds, shared-lineage ecological guidance, mixed ANR/enrichment scope, safeguards and species-tool referrals. No threshold activation, human approval or source-complete status follows from this review. If parent stages any new unit, recheck its exact quote, attribution, family and raw-to-canonical mapping against these findings before central admission.

## Additional conclusion check: native 65 / printed 62

Read at parent request. The conclusion explicitly warns that low-cost/non-intensive natural regeneration may fail without seed sources within effective dispersal range or with uncontrolled grazing. This strengthens the directional interpretation: available effective seed supply supports regeneration, while uncontrolled grazing hinders it. It provides no distance, density, pressure threshold or numeric score. Natural regeneration is not resolved between passive and assisted families; do not infer passive merely from “low-cost, non-intensive.” The conclusion is this report's synthesis of preceding discussion, not another independent study. Retain a `regeneration_potential` directional candidate with family and source-independence holds; retain uncontrolled grazing as a separate raw-property hold. Audit-only closure is appropriate pending these resolutions. No new EV is recommended solely from this paragraph.

Companion `table_rows.json` inventories each feature/activity row with native/printed locator and disposition. Repeated activities under different objectives are retained as separate source rows, never counted as separate independent claims.
