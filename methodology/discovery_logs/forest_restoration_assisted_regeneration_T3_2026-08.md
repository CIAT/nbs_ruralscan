# Discovery log — Forest Restoration · assisted_regeneration · T3

- Run `forest_restoration_discovery_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** discovery + screening only. No extraction.
- **grey + tool = complete.** **stock + updated_lit = IN PROGRESS** — OpenAlex hit its daily budget (HTTP 429, resets midnight UTC); candidates below are provisional (WebSearch/canon fallback), to be finalised with real OpenAlex nets on rerun.

## grey + tool candidates (final)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `fao_sfm_anr_case_degraded` | grey | oa | ok | high | FAO SFM Toolbox: Application of assisted natural regeneration to restore degraded tropical forestlands — FAO grey case describing ANR method incl. fire/grazing suppression, firebreaks, fencing. Snapsh |
| `wri_what_is_anr_insight` | grey | oa | ok | med | What is Assisted Natural Regeneration & How Does it Work? (WRI insight) — WRI definitional grey: firebreaks, clearing dry debris (fire), fencing (grazing) as barrier removal. Qualitative T3 (hazard-as |
| `iucn_es_restauracion_paisaje_tecnicas` | grey | oa | ok | med | Restauración funcional del paisaje rural: manual de técnicas (IUCN, ES) — Spanish-language FLR techniques manual (IUCN) incl. regeneración natural asistida + fire management. Multilingual grey; verbat |
| `elti_bloomfield_es_principios_restauracion` | grey | oa | ok | med | Principios para la restauración de bosques tropicales / RNA (ELTI, Bloomfield, ES) — ELTI/Yale Spanish training material on regeneración natural asistida incl. fire (fuego) as a recurrent disturbance  |
| `williams_2024_natregen_potential_model` | tool | repo | ok | med | Global potential for natural regeneration in deforested tropical regions (30m regeneration-potential model) — Spatial regeneration-POTENTIAL random-forest model (30m) = the F2 dominant-limiter gate. T |
| `iucn_wri_roam_methodology` | tool | oa | ok | low | Restoration Opportunities Assessment Methodology (ROAM) guide (IUCN/WRI) — Methodology/diagnostic (not code). Frames restoration-opportunity criteria incl. degradation/disturbance; ANR is one interven |

## stock + updated_lit candidates (PROVISIONAL — OpenAlex pending)

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `shono_2007_anr_degraded_forestlands` | stock | paywalled | ok | high | Application of Assisted Natural Regeneration to Restore Degraded Tropical Forestlands — Seminal high-cite ANR practice paper (Shono, Cadaweng, Durst). ANR EXPLICIT: suppressing fire, grazing and loggi |
| `elliott_framework_species_method` | stock | oa | ok | high | The framework species method: harnessing natural regeneration to restore tropical forest ecosystems — Framework-species = explicit family vocab (accelerating natural regeneration, not plantation). Cov |
| `frontiers_2022_assisted_functional_recovery` | stock | oa | ok | med | Assisted restoration interventions drive functional recovery of tropical wet forest tree communities — Compares assisted vs unassisted regeneration; recruitment/survival outcomes of interventions. Pra |
| `frontiers_2024_anr_bibliometric_synthesis` | updated_lit | oa | ok | high | Bibliometric and literature synthesis on assisted natural regeneration: an evidence base for forest and landscape restoration in the tropics — Recent OA synthesis of ANR evidence base incl. barrier ty |
| `naturerev_2025_drivers_natural_regeneration` | updated_lit | paywalled | ok | high | Drivers and benefits of natural regeneration in tropical forests — Recent review of regeneration drivers incl. climate/drought and disturbance. Regeneration-potential = the family's dominant limiter.  |
| `dry_forest_anr_diversity_carbon_2024` | updated_lit | oa | ok | high | Restoring a dry tropical forest through assisted natural regeneration: enhancing tree diversity, structure, and carbon stock — ANR in a DRY tropical forest -> directly the drought/seasonality hazard c |
| `restoration_interventions_recruitment_2022` | updated_lit | oa | ok | med | Restoration interventions mediate tropical tree recruitment dynamics over time — Intervention effect on recruitment/survival over time (Costa Rica; natural regen vs applied nucleation vs plantation, ~ |

### Verbatim search terms (as run / attempted)

- **stock:** `OpenAlex title.search boolean (ran via curl): (assisted natural regeneration OR assisted regeneration) AND (drought OR fire OR survival OR mortality) — sort=cited_by_count:desc; SUPPLEMENTED by WebSearch: "assisted natural regeneration tropical forest drought seedling survival mortality restoration"`
- **updated_lit:** `WebSearch: "natural regeneration tropical forest recovery climate drought resprouting resilience meta-analysis 2022 2023"; "assisted natural regeneration fire resilience grazing protection restoration tropics review" (intended OpenAlex recent filter from_publication_date:2015 blocked by same budget cap)`
- **grey:** `WebSearch EN+ES: "FAO regeneración natural asistida restauración sequía fuego bosque tropical guía"; "assisted natural regeneration fire resilience grazing protection restoration tropics review" (FAO/WRI/IUCN/SER/ELTI/CIFOR-ICRAF/WOCAT targeted)`
- **tool:** `WebSearch: "WRI restoration opportunity mapping GitHub regeneration potential suitability model repository"; "github.com natural regeneration potential tropical model code Williams 2024 restoration repository"; WebFetch code/data-availability of Williams et al. 2024 (PMC11618091)`

## Gaps / next iteration

OpenAlex curl was IP-budget-exhausted ('Insufficient budget, resets midnight UTC', ~12h) after a single query that returned 0 for the strict title.search boolean — so BOTH stock (high-cite) and updated_lit (recent) OpenAlex passes are UNVERIFIED for real retrieved/cited_by totals; re-run the logged booleans after reset to confirm counts and pull any high-cite items WebSearch missed. Multilingual grey is EN+ES only: no PT (Brazil Atlantic Forest ANR literature is substantial) and no FR (Sahel/francophone Africa) grey retrieved this pass. WOCAT SLM technologies DB (a locked diamond source) was not directly queried. Tool process is genuinely thin: no public commit-pinnable regeneration-potential code repo exists (Williams model code is on-request; ROAM/Restoration Diagnostic are methodologies, not code) — so file:line tool evidencing for this family is currently not possible. T3 content skew: most ANR sources treat fire and grazing QUALITATIVELY as regeneration barriers (hazard-to-restoration) rather than giving quantified drought survival/mortality or fire-resilience thresholds — expect many qualitative_only T3 rows, and watch claim_scope (dry-forest drought/resprouting and framework-species tolerance evidence is often species_specific, must be KEPT+tagged, not read as practice-level). Restoration-as-hazard-buffer direction (restored cover reducing flood/erosion/heat) is under-represented in the ANR-specific corpus and may need a separate cross-family/forest-cover search.
