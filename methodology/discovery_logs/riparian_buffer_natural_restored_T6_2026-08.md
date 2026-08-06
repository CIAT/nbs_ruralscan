# Discovery log — Riparian Buffers · natural_restored · T6

- Run `riparian_buffer_discovery_2026-08` · date 2026-08-06 · by Pete/Claude · ruleset v1.4.1 · nbs_id `riparian_buffer`
- **Scope:** discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 81 | 40 | 4 |
| updated_lit | 28 | 30 | 5 |
| grey | 24 | 16 | 4 |
| tool | 16 | 8 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search (curl, sort=cited_by_count:desc): "riparian buffer water quality"; "riparian buffer nitrogen"; "riparian buffer sediment"; "riparian vegetation nutrient retention"`
- **updated_lit:** `OpenAlex title.search (curl, from_publication_date filter, sort=cited_by_count:desc): "riparian buffer water quality" from 2018; "riparian restoration biodiversity" from 2015; "riparian buffer carbon sequestration"; "riparian buffer cost effectiveness"; "riparian buffer tropical water quality"`
- **grey:** `WebSearch EN: 'USDA NRCS riparian forest buffer conservation practice standard nitrogen sediment removal cost per acre CRP'; 'FAO riparian buffer restoration water quality guidance nutrient removal tropical'; 'WOCAT riparian vegetation restoration natural regeneration streambank technology'`
- **tool:** `WebSearch: 'InVEST nutrient delivery ratio riparian buffer retention model github natural capital'; 'github riparian buffer siting prioritization GIS MCDA stream network suitability tool'. Verify: WebFetch natcap/invest ndr.py for hardcoded buffer params`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `osborne_kovacic_1993_buffer_wq_restoration` | stock | paywalled | ok | high | Riparian vegetated buffer strips in water-quality restoration and stream management — Seminal (is_seminal) synthesis of buffer WQ-restoration function incl. natural/restored vegetated strips - anchors |
| `mayer_2007_meta_n_removal_buffers` | stock | paywalled | ok | high | Meta-Analysis of Nitrogen Removal in Riparian Buffers — Quantitative meta-analysis of N removal efficiency vs buffer width/vegetation across many sites incl. forest/natural buffers - highest-value T6  |
| `sabater_2003_n_removal_euro_gradient` | stock | oa | ok | high | Nitrogen Removal by Riparian Buffers along a European Climatic Gradient: Patterns and Factors of Variation — Multi-site N-removal efficiency of existing riparian buffers across a climatic gradient (tr |
| `newbold_2000_buffer_restoration_connecticut_wq` | stock | paywalled | ok | high | Water Quality Changes from Riparian Buffer Restoration in Connecticut — Directly restored-buffer T6: WQ change attributable to riparian buffer RESTORATION (not planting-act-specific) - core PICOS fit  |
| `buffer_length_costa_rica_2021_wq` | updated_lit | oa | ok | high | Riparian buffer length is more influential than width on river water quality: a case study in southern [Costa Rica/Colombia] — LMIC/tropical Latin-America anchor (tie-break priority given temperate-he |
| `reforestation_ecosystem_services_costa_rica_2022` | updated_lit | paywalled | ok | high | Modeling multiple ecosystem services and beneficiaries of riparian reforestation in Costa Rica — Tropical LMIC riparian reforestation (restored family) with multi-ES + beneficiary outcomes (T6 people/ |
| `cost_effectiveness_riparian_forest_buffers_2025` | updated_lit | oa | ok | high | Cost-effectiveness of riparian forest buffers in farmland for water quality improvement — Direct T6 COST dimension (cost per unit WQ improvement) - the scarcest T6 axis. Only cost-titled hit in OpenAl |
| `ontario_carbon_riparian_buffer_types_2022` | updated_lit | oa | ok | med | Diverse temperate riparian buffer types promote system-level carbon sequestration in southern Ontario — T6 CARBON outcome for restored/natural buffer vegetation. Diamond OA. Temperate (transferability |
| `restoring_riparian_habitats_biodiversity_livelihoods_2025` | updated_lit | oa | ok | med | Restoring riparian habitats for benefits to biodiversity and human livelihoods: a systematic map protocol — T6 biodiversity + human-livelihoods outcomes of riparian RESTORATION; systematic-map = evide |
| `fao_sfm_toolbox_tb11_riparian_buffer_wq` | grey | oa | ok | high | FAO SFM Toolbox TB11 - Use of conservation riparian buffer to preserve water quality — FAO authority; design/maintenance guidance + qualitative sediment/nutrient/pesticide removal + biodiversity co-be |
| `nrcs_cps_391_riparian_forest_buffer` | grey | oa | ok | high | USDA-NRCS Conservation Practice Standard 391 - Riparian Forest Buffer — Quantified practice-standard values (up to 90% sediment filtered; ~21 lb N/ac/yr retained; 3-zone design, Zone-1 min 15 ft). Pra |
| `fsa_crp_cp22_riparian_forest_buffer_program` | grey | oa | ok | med | USDA-FSA CRP CP22 Riparian Forest Buffer (program sheet) — ADOPTION/program evidence (CRP buffer enrolment, payments) -> T6 cost/adoption + conditionality. method_type=adoption_study. PDF -> library. |
| `epa_2005_buffer_width_n_removal` | grey | oa | ok | high | Riparian Buffer Width, Vegetative Cover, and Nitrogen Removal Effectiveness (EPA/USDA-FS synthesis) — Synthesis of N-removal efficiency vs width & vegetative cover across studies - quantitative T6 nut |
| `invest_ndr_natcap` | tool | repo | NO | low | InVEST Nutrient Delivery Ratio (NDR) model - natcap/invest — CODE-LEVEL INTERROGATED: eff_n/eff_p, crit_len_n/crit_len_p all read from user biophysical table; NO hardcoded riparian retention/width in  |

## Gaps / next iteration

LMIC/tropical evidence is thin and temperate-dominated (US Chesapeake, European gradient, Ontario). Only two tropical anchors surfaced (Costa Rica/Colombia buffer-length 2021; Costa Rica reforestation-ES 2022) plus one FAO/agris tropical-watershed record; Africa & Asia rural riparian restoration essentially absent from title.search. (1) No ES/FR/PT grey hits surfaced (WebSearch is US/EN-biased) - direct WOCAT SLM portal, CGIAR/IWMI, and Latin-America/Brazil (APP/Codigo Florestal riparian) queries remain OPEN and should be run for LMIC adoption + cost evidence. (2) T6 COST axis is critically sparse - only ONE cost-effectiveness paper in all of OpenAlex title.search; cost-per-km / cost-per-kg-pollutant-removed will lean on grey (NRCS/CRP payment rates, restoration cost databases) with positive-bias discount. (3) TOOL process yielded NO extractable claim: InVEST NDR is data-driven (verified in ndr.py); other siting/MCDA tools (Riparian Restoration DSS, ArcGIS dashboards, riparianbuffers.com) are proprietary web apps with no pinnable commit+file:line - a github repo hardcoding riparian-buffer siting weights/widths was not found. (4) OpenAlex title.search AND-semantics are strict (multi-term restoration+nutrient+sediment queries returned 0) - a full-text/abstract concept search or OpenAlex concept-ID filter would recover restoration-framed studies the title-only pass missed. (5) Natural-regeneration vs active-reforestation split within this family is not separable from titles alone - screen at extraction to keep passive/natural-regen distinct from planting-act (that belongs to a planted riparian sub-family, not F2).
