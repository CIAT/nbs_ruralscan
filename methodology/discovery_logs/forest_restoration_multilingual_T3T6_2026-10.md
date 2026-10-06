# Forest restoration × T3/T6: multilingual pass, ES / FR / PT (2026-10-06)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `forest_synthesis_first_2026-10-06_ml`, ruleset **v1.6.2**, synthesis-first rule (Pete 2026-10-01). Registered by `scripts/register-discovery.py` on 2026-10-06: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `forest_synthesis_first_2026-10-06_ml`, ledger per `--ledger`.


- **Scope:** `nbs_id=forest_restoration`, generic parent search, T3 + T6, process `updated_lit` (some `stock`/`grey`), ruleset v1.6.0. Suggested run id: `fr_synthesis_first_ml_2026-10-06`.
- **Source:** OpenAlex `title.search` (accent-sensitive, so accented AND unaccented forms were OR-ed), sorted by citations, top 20–25 rows per query read. Web search was used for OA recovery.
- **Staging only.** Nothing was registered and no git commands were run. Every DOI was Crossref round-tripped. One caveat: the Crossref author metadata for `10.17528/cifor/001872` is garbled ("N. & S."), so its citation was rebuilt from the CIFOR record (Robertson & Wunder 2005), and `verify_metadata.py` should flag it.
- **Synthesis yield is low** in all three languages: few meta-analyses or SRs carry ES/FR/PT titles. Included items are mostly LMIC evaluations, cost studies and chronosequences. Tiers are **Low** by design. They add LMIC context votes and transfer-class coverage (MEX, CRI, BOL, BRA, SEN, MDG), not new consensus.

## Funnel
| stage | n |
|---|---|
| returned (OpenAlex totals, 13 queries) | 1,047 (incl. 469 English-noise hits in M9; see lesson below) |
| screened (titles read) | 236 → ~45 metadata/abstract |
| included | **15** (ES 7 · FR 4 · PT 4) |

## Queries (OpenAlex `filter=title.search:<q>`, verbatim)
| # | lang | query | total |
|---|---|---|---|
| M1 | es | `("restauración forestal" OR "restauracion forestal" OR reforestación OR reforestacion OR "regeneración natural" OR "regeneracion natural" OR "bosque secundario" OR "bosques secundarios") AND (revisión OR revision OR metaanálisis OR "meta-análisis" OR síntesis OR sintesis)` | 3 |
| M2 | es | `("restauración forestal" OR "restauracion forestal" OR reforestación OR reforestacion OR "regeneración natural" OR "regeneracion natural") AND (costos OR costo OR erosión OR erosion OR sequía OR sequia OR inundaciones OR "medios de vida" OR carbono OR biodiversidad)` | 54 |
| M3 | es | `(manglar OR manglares) AND (restauración OR restauracion OR reforestación OR reforestacion OR rehabilitación) AND (supervivencia OR éxito OR exito OR protección OR proteccion OR servicios OR costos)` | 1 |
| M4 | es | `(manglar OR manglares) AND (restauracion OR reforestacion OR rehabilitacion OR recuperacion)` | 3 |
| M5 | es | `("restauración ecológica" OR "restauracion ecologica" OR "restauración pasiva" OR "restauración activa") AND (bosque OR bosques OR tropical)` | 108 |
| M6 | es | `("manejo forestal comunitario" OR "forestería comunitaria" OR "pago por servicios ambientales" OR "pagos por servicios ambientales") AND (impacto OR impactos OR evaluación OR pobreza OR deforestación)` | 48 |
| M7 | fr | `(mangrove OR mangroves) AND (restauration OR reboisement OR reboisements OR "régénération")` | 24 |
| M8 | fr | `("régénération naturelle assistée" OR "regeneration naturelle assistee" OR "mise en défens" OR "mise en defens" OR "foresterie communautaire" OR "gestion communautaire des forêts")` | 123 |
| M9 | fr | `("restauration forestière" OR "restauration forestiere" OR reboisement OR "régénération naturelle" OR "regeneration naturelle" OR "forêts secondaires" OR afforestation) AND (synthèse OR synthese OR revue OR "méta-analyse" OR impacts OR érosion OR erosion OR sécheresse OR revenus OR carbone)` | 469 (**English noise**) |
| M10 | fr | `("restauration forestière" OR "restauration forestiere" OR reboisement OR reboisements OR "régénération naturelle" OR "regeneration naturelle" OR "forêts secondaires") AND (synthèse OR synthese OR revue OR "méta-analyse" OR érosion OR sécheresse OR revenus OR carbone OR coûts OR couts OR biodiversité)` | 28 (clean rerun of M9) |
| M11 | pt | `("restauração florestal" OR "restauracao florestal" OR reflorestamento OR "regeneração natural" OR "regeneracao natural" OR "florestas secundárias" OR "floresta secundária") AND (revisão OR revisao OR "meta-análise" OR síntese OR sintese OR custos OR custo OR erosão OR erosao OR carbono OR biodiversidade OR renda)` | 117 |
| M12 | pt | `(manguezal OR manguezais) AND (restauração OR restauracao OR recuperação OR recuperacao OR reflorestamento)` | 41 |
| M13 | pt | `("pagamento por serviços ambientais" OR "pagamentos por serviços ambientais" OR "manejo florestal comunitário") AND (impacto OR impactos OR avaliação OR renda)` | 28 |

OA-recovery web searches (verbatim): `"Custos de restauração florestal para a bacia do rio Itacaiúnas" ITV pdf` (no copy found); `"Reboisement classique versus régénération assistée" mangroves Sainte-Marie Madagascar Didy` (abstract-level confirmation only, no free copy).

**Lesson (for search_protocol learnings):** do not put cognates that are also English words (`afforestation`, `impacts`, `erosion`) in a French title query. M9 returned 469 English papers, and the rerun without them (M10) was clean. This is the same failure mode as `haies` → "hay" in the agroforestry round.

## Included (15)
ES: barajas_guzman_2013 (mulch cost + drought survival) · keyes_anduaga_1997 (reforestation cost/ha) · hernandez_melchor_2017 (mangrove reforestation survival, Tabasco) · robertson_wunder_2005 (PES Bolivia, CIFOR) · rojas_2011 + padilla_molina_2017 (PES-reforestation income, Costa Rica) · ceballos_2021 (community forestry, Puebla)
FR: badji_2013 (mise en défens chronosequence, Senegal) · didy_2026 (mangrove planting vs assisted regeneration survival, Madagascar) · ramamonjisoa_2012 (economics of community forestry, Madagascar) · inrae_2023 (plantation vs natural regeneration biodiversity, HIC synthesis note)
PT: oliveira_engel_2017 (Atlantic Forest restoration review) · azevedo_2018 (carbon in restoration plantings) · seixas_jabor_2024 (Reflorestar PES economic effects) · nunes_silva_2020 (restoration costs, eastern Amazon; ITV technical report)

## Screened out (main reasons)
| item | reason |
|---|---|
| RNA (régénération naturelle assistée) papers from Niger/Senegal **on farmland** (Aguié resilience 2018; Centre-Sud Niger 2013/2014; RNA vs millet yield 2017; Khatre Sy 2015; RNA SOC 2025) | **PICOS:** farmer-managed regeneration in cropland is the agroforestry `fmnr` family, not FR assisted_regeneration. Route to the agroforestry lane if wanted. Two (IRD 2010, adoption 2020) are already known |
| Mise en défens of steppe rangelands (Naâma, Algeria; Tunisia; Alfa steppe) | rangeland/grass recovery, not forest |
| Maâmora reforestation species drought tolerance (Morocco, 2020 ×2) | species-specific (`claim_scope=species_specific`), not practice |
| Carbon-in-natural-regeneration of *Pinus*, *Cordia*, *Juglans* (ES) | species/stand inventories, not restoration effects |
| Mexican PSA hidrológicos case studies (2015/2017) | hydrological PES for existing forest; weak designs; Campbell SRs cover the cell |
| Restauração de manguezais no Brasil: retrospectiva e perspectivas (UFSC 2012) | appears to be a thesis/TCC repository item; not verified as a publication. Kept as a pointer only |
| Reboisements de mangrove delta du Saloum (2018, no DOI, closed) | no acquirable copy found; pointer only |
| Mangrove "carbone fantôme" Senegal (2026) | journalism/critique, no data |
| Huellas … / Bolsa Floresta econometrics (2024) / Reflorestar forest-cover thesis (UFES 2025) | Bolsa Floresta = avoided deforestation PES, borderline; kept out to stay at 15. Pointer for protection_cbfm if the cell is thin |
| Riparian reforestation vs wave erosion in reservoirs (2021) | riparian_buffer NbS, not FR |

## Needs a human
- **didy_2026** (Cairn, closed) and **nunes_silva_2020** (ITV report, no PDF found): check ResearchGate and itv.org first. The ITV report number is inferred from the DOI.
- **inrae_2023:** read the author list from the HAL PDF at acquisition. It is a France (HIC) synthesis note: direction only, never an LMIC value.
- **keyes_anduaga_1997:** Crossref issued-date is 2016 (OJS back-load), but the journal year is 1997. Make sure `verify_metadata` does not overwrite the year.
