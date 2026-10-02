# Agroforestry × T3/T6 — multilingual (ES/FR/PT) `updated_lit` discovery pass — 2026-10-02

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `af_ml_2026-10-02`, ruleset **v1.6.0**, synthesis-first rule (Pete 2026-10-01). SRCH rows carry the same run_id; candidates → `pipeline/acquisition_queue.csv` (status `pending`). 20 queued (es 9 · fr 4 · pt 7).


> Staging only (`pipeline/staging/discovery/`). Nothing registered, queued, or ledger-stamped. Ruleset **v1.6.0**; run id `ml_af_t3t6_2026-10-02`. Targeting rule (Pete 2026-10-01): syntheses first; primaries only for hazard/target cells with no synthesis in any language; PADs excluded.
> Dedup: `agroforestry_known_sources.json` (134 rows: 52 SRC + 82 queue, incl. the T3 probe) by DOI + normalised title — **no included candidate is known**. English probe/T6-sibling and grey/MEL agent scopes not duplicated (FAO/CATIE/Embrapa institutional *syntheses* included here are flagged for grey-agent dedupe).
> Deliverable: `agroforestry_multilingual_candidates.json` (**20** candidates: es 9 · fr 4 · pt 7).

## Channels
- **OpenAlex** `/works`, `display_name.search` (title-only, per AGENTS.md rule), `per-page=200`, cursor paging, `mailto=p.steward@cgiar.org`. Note: OpenAlex title search is **accent-sensitive** (`agroforestería` 188 vs `agroforesteria` 21) — unaccented variants added in ES5/ES6. FR `haies` matches EN "hay" (stemming) → ~40 livestock-feed noise records screened out by title.
- **HAL** API `api.archives-ouvertes.fr/search` (`title_t:`), rows=200.
- **CGSpace** DSpace 7 discover API (`dsoType=ITEM`, size=40).
- **SciELO** `search.scielo.org`: **BLOCKED** (Bunny-shield JS challenge, no API response) — 0 results; SciELO content was reached indirectly via OpenAlex (10.1590/*, 10.4067/* DOIs) and web search. **Redalyc / Dialnet**: no usable API; reached via web search + OpenAlex (Dialnet/Redalyc appear as OpenAlex sources).
- **Web search** (US engine) for institutional syntheses (CATIE, CIPAV, EMBRAPA/IAPAR, CIRAD/IRD, RIOCCADAPT) and gap hazards.
- **Crossref** (DOI round-trip + bibliographic search), **Unpaywall** (`?email=p.steward@cgiar.org`).

---

## Spanish (es)

### Verbatim queries (OpenAlex `filter=`) · count · retrieved
| id | filter (verbatim) | count | retrieved |
|---|---|---|---|
| ES1 | `display_name.search:(agroforestería OR agroforestal OR agroforestales OR silvopastoril OR silvopastoriles OR agrosilvopastoril OR "cercas vivas" OR rompevientos OR "cortinas rompevientos" OR "barreras vivas" OR "café bajo sombra" OR "árboles en fincas" OR "árboles dispersos" OR "árboles en potreros") AND (sequía OR sequías OR inundación OR inundaciones OR "estrés térmico" OR "estrés calórico" OR "confort térmico" OR heladas OR huracán OR huracanes OR incendio OR incendios OR "eventos extremos" OR "variabilidad climática" OR "cambio climático" OR resiliencia OR adaptación OR microclima)` | 96 | 96 |
| ES2 | `display_name.search:(agroforestería OR agroforestal OR agroforestales OR silvopastoril OR silvopastoriles OR agrosilvopastoril OR "cercas vivas" OR rompevientos OR "cortinas rompevientos" OR "barreras vivas" OR "café bajo sombra" OR "árboles en fincas" OR "árboles dispersos" OR "árboles en potreros") AND ("meta-análisis" OR metaanálisis OR "revisión sistemática" OR revisión OR síntesis OR "estado del arte" OR "estado del conocimiento")` | 27 | 27 |
| ES3 | `display_name.search:(agroforestería OR agroforestal OR agroforestales OR silvopastoril OR silvopastoriles OR agrosilvopastoril OR "cercas vivas" OR rompevientos OR "cortinas rompevientos" OR "barreras vivas" OR "café bajo sombra" OR "árboles en fincas" OR "árboles dispersos" OR "árboles en potreros") AND (rendimiento OR productividad OR ingresos OR "seguridad alimentaria" OR carbono OR erosión OR biodiversidad OR costos OR rentabilidad OR "análisis económico" OR adopción OR "servicios ecosistémicos" OR "calidad del agua" OR pobreza OR género OR mujeres) AND ("meta-análisis" OR metaanálisis OR "revisión sistemática" OR revisión OR síntesis OR "estado del arte" OR "estado del conocimiento")` | 4 | 4 |
| ES4 | `display_name.search:(agroforestería OR agroforestal OR agroforestales OR silvopastoril OR silvopastoriles OR agrosilvopastoril OR "cercas vivas" OR rompevientos OR "cortinas rompevientos" OR "barreras vivas" OR "café bajo sombra" OR "árboles en fincas" OR "árboles dispersos" OR "árboles en potreros") AND (rendimiento OR productividad OR ingresos OR "seguridad alimentaria" OR carbono OR erosión OR biodiversidad OR costos OR rentabilidad OR "análisis económico" OR adopción OR "servicios ecosistémicos" OR "calidad del agua" OR pobreza OR género OR mujeres),language:es` | 413 | 200 |
| ES5 | `display_name.search:(agroforesteria OR agroforestales OR silvopastoriles OR "cercas vivas") AND (metaanalisis OR "meta-analisis" OR "revision sistematica" OR revision OR sintesis)` | 1 | 1 |
| ES6 | `display_name.search:(agroforestería OR agroforesteria OR agroforestal OR agroforestales OR silvopastoril OR silvopastoriles OR "cercas vivas" OR rompevientos OR "café bajo sombra" OR "árboles dispersos") AND (heladas OR helada OR huracán OR huracan OR huracanes OR ciclón OR inundación OR inundaciones OR anegamiento OR incendio OR incendios OR fuego OR sequía OR sequia OR sequías OR "El Niño" OR "estrés hídrico" OR "estrés térmico" OR "estrés calórico")` | 20 | 20 |

### PRISMA-lite (es)
- Retrieved 348 (OpenAlex) → ~300 unique · CGSpace CG1 (3) + CG4 (272; top 40 screened) + CG7 (615, mixed-language; top 40) · web search 7 queries.
- Title screen: all unique; kept syntheses + hazard-titled records.
- Abstract/full-text screen: **28**.
- **Included: 9** (Villarreyna 2020 · Montagnini et al. 2015 CATIE · RIOCCADAPT Ch7 2020 · Current et al. (es ed.) · Murgueitio 2013 · Navas 2010 · Cisneros 2024 · Morantes-Toloza 2018 · Saucedo-Uriarte 2023).

### Screened out (es)
| record | reason |
|---|---|
| Meta-Análisis de Cacao en Agroforestería vs. Monocultivos (BORIS Bern, 2020, no DOI) | duplicate — Spanish version of Niether et al. 2020 ERL MA (10.1088/1748-9326/abb053, an EN T6 candidate in the probe reserve) → acquire the EN original (EN sibling) |
| Murgueitio et al. 2015 Rev. Cubana Cienc. Agríc. "Los SSPi en América Latina…" | lineage (CIPAV, same as Murgueitio 2013 + Montagnini 2015 ch.) — **reserve** |
| Buitrago-Guillen 2018 Bol. Cient. Museo (10.17151/bccm.2018.22.1.2) | overlap/credibility (narrative, superseded by Cisneros 2024) — reserve |
| Guananga 2026 SSP bienestar y producción, revisión sistemática (10.61347/ei.v5iesp.2.341) | credibility (new low-tier venue) — reserve |
| SSP en ganadería bovina… estrés calórico, revisión (2023, repositorio) | thesis/credibility |
| Almacén de COS en SAF de café: revisión (Terra Latinoam. 2025, 10.28940/terra.v43i.2195) | **DOI failure (Crossref 404)** + carbon well covered in EN — reserve, acquire by title |
| IMPACTO SAF seguridad alimentaria y CC: revisión (2024, 10.37885/240717238) | credibility (Editora Científica Digital book chapter) |
| Agroforestería urbana SR 2023; avifauna certificaciones SR 2020; cacao/bioagresores reviews | relevance (urban / biodiversity of certification / pests) |
| Guzmán-Castillo 2024 EARN impact evaluation café/cacao Peru (10.7201/earn.2024.01.05) | primary; production has syntheses — **reserve (T6, quasi-exp LMIC)** |
| Agroforestería familiar inundable, Loreto (IIAP 2019) | primary (flood-adapted floodplain AF, Peru) — **reserve for flood** (no synthesis on flood impact under AF) |
| Estrategias de los árboles… tolerancia a la sequía en SSP (2013, NORA) | relevance (tree physiology chapter) — reserve for asset_vulnerability(drought) |
| Limitaciones en la adopción de SSP en Latinoamérica (2006, Redalyc) | could not resolve authors/DOI within cap — reserve (T6 adoption) |
| Harvey et al. 2003 Contribución de las cercas vivas… (Agrofor. Américas) | overlap with Morantes-Toloza 2018 — reserve |
| FAO 2021 Cómo abordar la silvicultura y agroforestería en los PNA (10.4060/cb1203es) | guidance, no outcome data |
| CIFOR 2014 Monte Alen brief; CGSpace CSA briefs/MRV/PSA reports | grey/MEL scope (grey agent) or no outcome data |
| ~40 carbon-stock primaries (ES4) | primary; carbon covered by EN syntheses |
| Barreras vivas nopal/agave contra incendios (2024) | outreach, not AF |

---

## French (fr)

### Verbatim queries (OpenAlex) · count · retrieved
| id | filter (verbatim) | count | retrieved |
|---|---|---|---|
| FR1 | `display_name.search:(agroforesterie OR agroforestier OR agroforestiers OR agroforestière OR agroforestières OR sylvopastoral OR sylvopastoraux OR agrosylvopastoral OR haies OR "brise-vent" OR "parcs agroforestiers" OR "parc agroforestier" OR "régénération naturelle assistée" OR "arbres hors forêt") AND (sécheresse OR sécheresses OR inondation OR inondations OR "stress thermique" OR canicule OR gel OR cyclone OR cyclones OR feu OR feux OR incendie OR incendies OR "variabilité climatique" OR "changement climatique" OR résilience OR adaptation OR microclimat)` | 72 | 72 |
| FR2 | `display_name.search:(agroforesterie OR agroforestier OR agroforestiers OR agroforestière OR agroforestières OR sylvopastoral OR sylvopastoraux OR agrosylvopastoral OR haies OR "brise-vent" OR "parcs agroforestiers" OR "parc agroforestier" OR "régénération naturelle assistée" OR "arbres hors forêt") AND ("méta-analyse" OR métaanalyse OR "revue systématique" OR revue OR synthèse OR "état des connaissances" OR "état de l'art")` | 17 | 17 |
| FR3 | `display_name.search:(agroforesterie OR agroforestier OR agroforestiers OR agroforestière OR agroforestières OR sylvopastoral OR sylvopastoraux OR agrosylvopastoral OR haies OR "brise-vent" OR "parcs agroforestiers" OR "parc agroforestier" OR "régénération naturelle assistée" OR "arbres hors forêt") AND (rendement OR rendements OR productivité OR revenus OR revenu OR "sécurité alimentaire" OR carbone OR érosion OR biodiversité OR coûts OR rentabilité OR "analyse économique" OR adoption OR "services écosystémiques" OR "qualité de l'eau" OR pauvreté OR genre OR femmes),language:fr` | 127 | 127 |
| FR4 | `display_name.search:(agroforesterie OR agroforestier OR agroforestiers OR agroforestière OR agroforestières OR sylvopastoral OR sylvopastoraux OR "brise-vent" OR "parcs agroforestiers" OR "parc agroforestier" OR "régénération naturelle assistée" OR "Faidherbia albida") AND (sécheresse OR sécheresses OR gel OR gelées OR cyclone OR cyclones OR inondation OR inondations OR feu OR feux OR incendie OR incendies OR "stress hydrique" OR "stress thermique" OR "déficit hydrique")` | 9 | 9 |
| FR5 | `display_name.search:("parcs agroforestiers" OR "parc agroforestier" OR "régénération naturelle assistée" OR "Faidherbia albida" OR "arbres hors forêt" OR "systèmes agroforestiers") AND ("sécurité alimentaire" OR rendement OR rendements OR revenus OR pauvreté OR résilience OR vulnérabilité OR femmes OR genre)` | 24 | 24 |

**HAL** (`title_t:` verbatim; rows=200):
| id | q | numFound |
|---|---|---|
| HAL1 | `title_t:((agroforesterie OR agroforestier* OR sylvopastora* OR "brise-vent" OR "parcs agroforestiers" OR "régénération naturelle assistée") AND (sécheresse* OR inondation* OR "stress thermique" OR gel OR cyclone* OR feu* OR incendie* OR résilience OR adaptation))` | 23 |
| HAL2 | `title_t:((agroforesterie OR agroforestier* OR sylvopastora* OR "parcs agroforestiers") AND ("méta-analyse" OR "revue systématique" OR revue OR synthèse OR "état des connaissances"))` | 6 |
| HAL3 | `title_t:((agroforestry OR agroforesterie OR silvopastoral) AND (meta-analysis OR "systematic review" OR review)) AND language_s:(fr OR es OR pt)` | 0 |

**CGSpace** (verbatim `query`, size=40):
| id | query | total |
|---|---|---|
| CG1 | `dc.title:(agroforestería OR agroforestales OR silvopastoriles OR silvopastoril) AND dc.title:(revisión OR síntesis OR "meta-análisis" OR sequía OR adaptación OR resiliencia)` | 3 |
| CG2 | `dc.title:(agroforesterie OR agroforestiers OR "parcs agroforestiers" OR "régénération naturelle") AND dc.title:(synthèse OR revue OR sécheresse OR adaptation OR résilience)` | 4 |
| CG3 | `dc.title:(agroflorestais OR silvipastoris OR agrofloresta) AND dc.title:(revisão OR síntese OR seca OR adaptação OR resiliência)` | 0 |
| CG4 | `(agroforestería OR silvopastoriles) AND (revisión OR "meta-análisis" OR síntesis)` | 272 |
| CG5 | `(agroforesterie OR "parcs agroforestiers" OR "régénération naturelle assistée") AND (synthèse OR revue OR "méta-analyse")` | 249 |
| CG6 | `(agroflorestais OR silvipastoris) AND (revisão OR "meta-análise" OR síntese)` | 3 |
| CG7 | `(agroforestería OR silvopastoriles OR agroforesterie OR agroflorestais) AND (sequía OR sécheresse OR seca OR huracán OR cyclone OR inundación OR inondation)` | 615 |

### PRISMA-lite (fr)
- Retrieved 249 (OpenAlex) + 29 (HAL) + 44 (CGSpace FR) → ~230 unique (after removing ~40 "hay" noise).
- Abstract/full-text screen: **18**.
- **Included: 4** (Seghieri & Harmand 2019 Quae · Botoni, Larwanou & Reij 2010 IRD · FAO 2024 Sénégal · Quénol & Beltrando 2006).

### Screened out (fr)
| record | reason |
|---|---|
| Lawali et al. 2018 RNA outil d'adaptation, Aguié Niger (10.4314/ijbcs.v12i1.6) | primary; drought×F2 has syntheses (EN Sendzimir/Weston/Binam known + Botoni 2010) — **reserve** |
| Mariel, Penot & Danthu 2021 Madagascar (10.4000/economierurale.9104) | relevance — resilience to **price** shocks, not climate hazard |
| FAO 2022 Pratiques agroforestières à haut potentiel… Sénégal (10.4060/cc1230fr) | practice catalogue, superseded by FAO 2024 bilan — reserve |
| Effets des brise-vent en zones tempérée et tropicale : revue… Afrique sèche (1983) | unacquirable (no source/DOI; Crossref no match) — **reserve, human search** (seminal Sahel windbreak review) |
| ENSO-driven vulnerability of Neotropical coffee/cacao AF (thèse 2025, HAL/theses.fr) | thesis; asset/livelihood drought — **reserve, high priority** (check for a review chapter) |
| Gestion durable des SAF en Afrique de l'Ouest : état des connaissances (2026, 10.59384/recopays.tg.v5i2.170) | credibility (new low-tier venue) — reserve |
| La dynamique des parcs agroforestiers soudano-sahéliens comme stratégie d'adaptation (HAL 2016) | not verified within cap — reserve |
| Amassaghrou 2021 olive AF Maroc (10.1051/cagri/2020041) | primary (T6 productivity) |
| Pratiques agroforestières et résilience climatique, Djougou Bénin 2024 | credibility (low-tier venue, case study) |
| Brise-vent, pare-feu et sylviculture (1990); sylvopastoral fire-prevention (1995); EU-FIRESMART (2011) | HIC Mediterranean fire, primaries; Damianidis 2021 (EN, probe) already covers |
| Régulation des bioagresseurs… revue (Quae 2019) | relevance (pests, not a T5 target) — inside Seghieri volume anyway |
| Karité / Faidherbia / néré parkland carbon & yield primaries | primary; covered by Bayala 2015 (known) |

---

## Portuguese (pt)

### Verbatim queries (OpenAlex) · count · retrieved
| id | filter (verbatim) | count | retrieved |
|---|---|---|---|
| PT1 | `display_name.search:(agrofloresta OR agroflorestas OR agroflorestal OR agroflorestais OR silvipastoril OR silvipastoris OR silvopastoril OR silvopastoris OR agrossilvipastoril OR "quebra-ventos" OR "quebra-vento" OR "cercas vivas" OR "café sombreado" OR "café arborizado" OR "árvores em pastagens" OR "integração lavoura-pecuária-floresta" OR ILPF) AND (seca OR secas OR estiagem OR inundação OR inundações OR "estresse térmico" OR "estresse calórico" OR "conforto térmico" OR geada OR geadas OR ciclone OR incêndio OR incêndios OR fogo OR "variabilidade climática" OR "mudanças climáticas" OR resiliência OR adaptação OR microclima)` | 96 | 96 |
| PT2 | `display_name.search:(agrofloresta OR agroflorestas OR agroflorestal OR agroflorestais OR silvipastoril OR silvipastoris OR silvopastoril OR silvopastoris OR agrossilvipastoril OR "quebra-ventos" OR "quebra-vento" OR "cercas vivas" OR "café sombreado" OR "café arborizado" OR "árvores em pastagens" OR "integração lavoura-pecuária-floresta" OR ILPF) AND ("meta-análise" OR metanálise OR "revisão sistemática" OR revisão OR síntese OR "estado da arte")` | 45 | 45 |
| PT3 | `display_name.search:(agrofloresta OR agroflorestas OR agroflorestal OR agroflorestais OR silvipastoril OR silvipastoris OR silvopastoril OR silvopastoris OR agrossilvipastoril OR "quebra-ventos" OR "quebra-vento" OR "cercas vivas" OR "café sombreado" OR "café arborizado" OR "árvores em pastagens" OR "integração lavoura-pecuária-floresta" OR ILPF) AND (produtividade OR rendimento OR renda OR "segurança alimentar" OR carbono OR erosão OR biodiversidade OR custos OR rentabilidade OR "análise econômica" OR "viabilidade econômica" OR adoção OR "serviços ecossistêmicos" OR "qualidade da água" OR pobreza OR gênero OR mulheres) AND ("meta-análise" OR metanálise OR "revisão sistemática" OR revisão OR síntese OR "estado da arte")` | 7 | 7 |
| PT4 | `display_name.search:(agrofloresta OR agroflorestas OR agroflorestal OR agroflorestais OR silvipastoril OR silvipastoris OR silvopastoril OR silvopastoris OR agrossilvipastoril OR "quebra-ventos" OR "quebra-vento" OR "cercas vivas" OR "café sombreado" OR "café arborizado" OR "árvores em pastagens" OR "integração lavoura-pecuária-floresta" OR ILPF) AND (produtividade OR rendimento OR renda OR "segurança alimentar" OR carbono OR erosão OR biodiversidade OR custos OR rentabilidade OR "análise econômica" OR "viabilidade econômica" OR adoção OR "serviços ecossistêmicos" OR "qualidade da água" OR pobreza OR gênero OR mulheres),language:pt` | 466 | 200 |
| PT5 | `display_name.search:(agrofloresta OR agroflorestas OR agroflorestal OR agroflorestais OR silvipastoril OR silvipastoris OR agrossilvipastoril OR "quebra-ventos" OR "quebra-vento" OR "café sombreado" OR "café arborizado" OR "integração lavoura-pecuária-floresta") AND (seca OR secas OR estiagem OR geada OR geadas OR ciclone OR inundação OR alagamento OR encharcamento OR incêndio OR incêndios OR fogo OR "estresse hídrico" OR "déficit hídrico" OR "estresse térmico" OR "estresse calórico")` | 34 | 34 |
| PT6 | `display_name.search:(agroflorestais OR silvipastoris OR "integração lavoura-pecuária-floresta" OR ILPF) AND ("meta-análise" OR metanálise OR "revisão sistemática" OR "revisão integrativa" OR "revisão de escopo")` | 9 | 9 |

CGSpace PT: CG3 (0), CG6 (3) — see table above.

### PRISMA-lite (pt)
- Retrieved 391 (OpenAlex) → ~340 unique + 3 CGSpace + 3 web queries.
- Abstract/full-text screen: **18**.
- **Included: 7** (Souza et al. 2011 · Robusti et al. 2017 · Ribeiro 2022 SR+MA · Santos et al. 2025 · Dos Santos & Triches 2023 · Ferraz et al. 2024 · Dias-Filho & Ferreira 2008).

### Screened out (pt)
| record | reason |
|---|---|
| Schembergue et al. 2017 RESR (10.1590/1234-56781806-94790550101) | primary (municipal PSM; vulnerability index not hazard-specific) — **reserve** (strong; cited 49) |
| Bento et al. 2020 SSP no Brasil: revisão sistemática (10.33448/rsd-v9i10.9016) | credibility (RSD = questionable venue) — reserve |
| Produção de leite em SSP: revisão (RSD 2021); PubVet 2019; Nucleus Animalium 2012 | credibility (low-tier) |
| Feltrin Puttini 2025 SciELO preprint, financiamento SAF (10.1590/scielopreprints.13486) | scope → M2b operational_risk (finance), not T6 |
| Conforto térmico de búfalas em SSP (PAB 2011, 10.1590/s0100-204x2011001000033) + ~15 ILPF thermal-comfort primaries | primary; heat_stress has syntheses — reserve |
| Fire-in-AF primaries (bracatinga, Pará 2006–2020) | primary, soil/seedbank effects not hazard outcome |
| ~30 SAF financial-viability case studies (Pará, Amazonas, Paraná) | primary — pooled via Ferraz 2024 instead |
| Quintais agroflorestais & segurança alimentar case studies | primary (F6 homegardens food security) — reserve |
| Gênero e SAF Igarapé-Açu (2008); Mulheres e agroflorestas no Cerrado (2017) | primary — **reserve for gender_inequity** (no synthesis found in any language) |

---

## Draft `SRCH` rows

```
nbs_id=agroforestry | suitability_family_id="" | table=T3 | process=updated_lit
search_terms = OpenAlex display_name.search verbatim filters ES1,ES2,ES5,ES6,FR1,FR2,FR4,FR5,PT1,PT2,PT5,PT6 (see tables; AGROVOC ES/FR/PT practice × hazard / synthesis blocks); HAL title_t HAL1–HAL3; CGSpace CG1–CG3, CG4–CG7; web search (7 hazard/institution strings, listed in report); SciELO search attempted — blocked (bot shield), 0 results
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = ES/FR/PT synthesis (MA / SR / integrative or narrative review in a reputable venue / institutional assessment or synthesis volume) reporting an agroforestry (any family) effect on a T3 hazard's livelihood impact, or hazard damage to the AF asset; primaries only where the hazard has no synthesis in any language (frost); exclude PADs, predatory/low-tier venues, urban AF, pure physiology, species-only envelopes, known sources, translations of EN papers already covered
limits = retrieve<=200/query; screen<=80 (abstract/full-text, shared with T6); include<=25 overall (shared with T6); title-only; multilingual ES/FR/PT
n_retrieved≈1,150 (OpenAlex 988 [865 unique, shared with T6], HAL 29, CGSpace ≈130 screened by title) | n_screened=64 (shared) | n_included=14 (T3 or T3|T6)
search_date=2026-10-02 | run_id=ml_af_t3t6_2026-10-02 | searched_by=discovery-agent (multilingual) | ruleset_version=v1.6.0
note = multilingual complement to probe_af_t3_2026-10-02 (EN); generic parent search; do NOT stamp ledger searched=done from this alone
```

```
nbs_id=agroforestry | suitability_family_id="" | table=T6 | process=updated_lit
search_terms = OpenAlex display_name.search verbatim filters ES2,ES3,ES4,ES5,FR2,FR3,FR5,PT2,PT3,PT4,PT6 (practice × outcome [rendimiento/rendement/produtividade · ingresos/revenus/renda · seguridad alimentaria/sécurité alimentaire/segurança alimentar · carbono/carbone · erosión/érosion/erosão · biodiversidad/biodiversité/biodiversidade · costos/coûts/custos · adopción/adoption/adoção · pobreza/pauvreté · género/genre/gênero · mujeres/femmes/mulheres] [× synthesis markers for ES3/PT3; language:es/fr/pt filter for ES4/FR3/PT4]); HAL HAL2–HAL3; CGSpace CG4–CG6; web search (EMBRAPA/CATIE/Murgueitio/MA strings)
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = ES/FR/PT synthesis reporting an agroforestry effect on a T5 priority (production_gap, rural_poverty, soil_erosion_risk, carbon, biodiversity, water_stress, gender) or economics/adoption with denominators; primaries excluded (every T6 target hit had a synthesis except gender_inequity → reserve); exclude PADs, predatory venues, translations, known sources
limits = as T3 (shared caps)
n_retrieved≈1,150 (shared) | n_screened=64 (shared) | n_included=15 (T6 or T3|T6)
search_date=2026-10-02 | run_id=ml_af_t3t6_2026-10-02 | searched_by=discovery-agent (multilingual) | ruleset_version=v1.6.0
note = T3 and T6 rows share one retrieval set; n_included counts overlap (9 candidates are T3|T6); total unique included = 20
```

---

## Included candidates (20)

### es (9)
| id | citation | tables | hazards | T6 targets | tier | OA |
|---|---|---|---|---|---|---|
| villarreyna_2020_es | Villarreyna, Rogelio; Avelino, Jacques (2020). Adaptación basada en ecosistemas: efecto de los árboles de sombra sobre servicios ecosistémic | T3|T6 | heat_stress, drought | production_gap, soil_erosion_risk, carbon_sequestration_potential, water_stress | medium | oa_direct |
| montagnini_2015_catie_es | Montagnini, F.; Somarriba, E.; Murgueitio, E.; Fassola, H.; Eibl, B. (eds.) (2015). Sistemas agroforestales. Funciones productivas, socioeco | T3|T6 | drought, heat_stress | production_gap, rural_poverty, carbon_sequestration_potential, biodiversity_priority, soil_erosion_risk, economics, adoption | medium | oa_direct |
| taboada_2020_rioccadapt_es | Taboada, M.A. et al. (2020). Capítulo 7. Sector Agropecuario. En: Moreno, J.M. et al. (eds.), Adaptación frente a los riesgos del cambio cli | T3 | drought, flood, heat_stress, frost | production_gap | medium | oa_repository |
| current_1995_es | Current, D.; Lutz, E.; Scherr, S.J. ([year to confirm]). Adopción agrícola y beneficios económicos de la agroforestería: experiencias en Amé | T6 | — | economics, adoption, rural_poverty | medium | oa_repository |
| murgueitio_2013_es | Murgueitio R, Enrique; Chará, Julián D; Solarte, Antonio J et al. (2013). Agroforestería Pecuaria y Sistemas Silvopastoriles Intensivos (SSP | T3|T6 | heat_stress, drought | production_gap, carbon_sequestration_potential, biodiversity_priority | low | oa_direct |
| navas_2010_es | Navas Panadero, Alexander (2010). Importancia de los sistemas silvopastoriles en la reducción del estrés calórico en sistemas de producción  | T3 | heat_stress | production_gap | low | oa_direct |
| cisneros_2024_es | Cisneros-Saguilán, Pedro; Hernández-Salinas, Gregorio; Hernández, Manuel Hernández (2024). Sistemas silvopastoriles, una alternativa para at | T3 | heat_stress, drought | production_gap | low | oa_direct |
| morantes_2018_es | Morantes-Toloza, Javier Leonardo; Renjifo, Luis Miguel (2018). Cercas vivas en sistemas de producción tropicales:  una revisión mundial de l | T3|T6 | wind_cyclone | production_gap, biodiversity_priority, adoption | medium | oa_direct |
| saucedo_2023_es | Saucedo-Uriarte, José Américo; Diaz-Quevedo, Clavel; Milla Pino, Manuel Emilio et al. (2023). Sustentabilidad productiva de la instalación d | T6 | — | production_gap, economics, soil_erosion_risk | medium | oa_direct |

### fr (4)
| id | citation | tables | hazards | T6 targets | tier | OA |
|---|---|---|---|---|---|---|
| seghieri_2019_fr | Seghieri, Josiane; Harmand, Jean-Michel (2019). Agroforesterie et services écosystémiques en zone tropicale. éditions Quae. https://doi.org/ | T3|T6 | drought, heat_stress | production_gap, carbon_sequestration_potential, biodiversity_priority, soil_erosion_risk, water_stress, rural_poverty | medium | oa_repository |
| botoni_2010_fr | Botoni, Edwige; Larwanou, Mahamane; Reij, Chris (2010). La régénération naturelle assistée (RNA) : une opportunité pour reverdir le Sahel et | T3|T6 | drought | production_gap, rural_poverty, agricultural_dependency | medium | oa_repository |
| fao_2024_senegal_fr | FAO (2024). Bilan et analyse des interventions et expérimentations agroforestières au regard de leur potentiel à contribuer à l'adaption aux | T3|T6 | drought, wind_cyclone, heat_stress | production_gap, soil_erosion_risk, rural_poverty | medium | oa_direct |
| quenol_2006_fr | Quenol, Herve; Beltrando, Gerard (2006). Impact des haies brise-vent sur le gel printanier en arboriculture. Climatologie, 3, 9-23. https:// | T3 | frost | — | low | oa_direct |

### pt (7)
| id | citation | tables | hazards | T6 targets | tier | OA |
|---|---|---|---|---|---|---|
| souza_2011_pt | Souza, Velci Queiróz de; Caron, Braulio Otomar; Schmidt, Denise et al. (2011). Resistência de espécies arbóreas submetidas a extremos climát | T3 | frost | — | low | oa_direct |
| robusti_2017_pt | Robusti, E.A.; Zapparoli, I.D.; Santoro, P.H. (2017). Café arborizado no Estado do Paraná, Brasil: indicadores financeiros e interferências  | T3|T6 | frost | economics | low | oa_direct |
| ribeiro_2022_pt | Ribeiro, Julio Cesar Pereira (None). Aspectos determinantes para adoção de sistemas agroflorestais no brasil: revisão sistemática e metanáli | T6 | — | adoption, economics | medium | oa_repository |
| santos_2025_pt | Santos, Wagner Martins dos; Costa de Sousa Martins, Lady Daiane; Costa, Claudenilde de Jesus Pinheiro et al. (2025). Sistemas Agroflorestais | T3|T6 | drought | economics, water_stress, soil_erosion_risk, carbon_sequestration_potential | low | oa_direct |
| dossantos_2023_pt | Dos Santos, Fernanda; Triches, Rozane Marcia (2023). Diferenças de produtividade entre sistemas convencionais e agroflorestais de culturas a | T6 | — | production_gap | low | oa_direct |
| ferraz_2024_pt | Ferraz, Ibirá Ferro; Souza, Mayara Andrade; Sant'Anna, Selenobaldo Axelinaldo Cabral de et al. (2024). Viabilidade financeira e econômica de | T6 | — | economics | low | oa_direct |
| diasfilho_2008_pt | Dias-Filho, M.B.; Ferreira, J. (2008). Barreiras à adoção de sistemas silvipastoris no Brasil. Embrapa (Documentos series; number to confirm | T6 | — | adoption | low | oa_repository |

---

## DOI round-trip (Crossref) and OA recovery
- **15 included DOIs: all pass** the Crossref title round-trip (ratio 1.0 vs OpenAlex title); citations rebuilt from Crossref authors/container/vol/issue/pages.
- **5 included DOI-less** (Montagnini 2015 CATIE · RIOCCADAPT Ch7 · Current et al. es-ed. · Robusti 2017 Agroalimentaria · Dias-Filho & Ferreira 2008 Embrapa): `title_verified=false`, `acquire_by=title` — need `verify_metadata.py verify-titles` after caching. Bracketed `[… to confirm]` fields in these citations were deliberately NOT filled from memory.
- **DOI failure:** `10.28940/terra.v43i.2195` (Almacén de COS en SAF de café, Terra Latinoamericana 2025) → Crossref 404 → blanked; reserve only.
- **Crossref data defect:** `10.47328/ufvbbt.2023.024` (Ribeiro, UFV) — first author blank in Crossref; rebuild from thesis cover.
- **Related EN DOI recorded (not this pass's scope):** Current, Lutz & Scherr 1995 → `10.1596/0-8213-3428-x` (Crossref title match).
- **OA breakdown (20): oa_direct 14 · oa_repository 6 · rg_flag_for_human 0 · paywalled 0.** Gold/diamond OA dominates (LatAm/francophone journals: Agron. Mesoam., Rev. Biol. Trop., RCCP, Rev. Med. Vet., Idesia/SciELO-CL, RCTA/AGROSAVIA, Ciência Rural/SciELO-BR, RBGF, Faz Ciência, OELV, Climatologie, AJOL). Repository: HAL (Seghieri), OpenEdition (Botoni), UFV LOCUS (Ribeiro), CGSpace (RIOCCADAPT), CATIE Orton (Current), Embrapa Infoteca (Dias-Filho). FAO cc9818fr: Unpaywall says `closed` but FAO publishes free (doi → fao.org/documents/card/fr/c/cc9818fr) → oa_direct.

## Flagged for a human
- **RIOCCADAPT Ch7:** confirm an agroforestry/silvopastoral slice exists and the author list/publisher (no Crossref record).
- **Montagnini 2015 / Current (es):** confirm series/edition details from the PDF/record; prefer EN Current 1995 WB edition if the EN sibling also queues it (dedupe).
- **Ribeiro 2022:** author list. **Ferraz 2024:** confirm the review is agroforestry-specific (abstract drifts to family farming generally).
- **Robusti 2017:** frost-mortality and NPV figures were seen only in a tool summary of the Redalyc HTML — NOT evidence; extract from the cached text through the pipeline.
- **"Effets des brise-vent… Afrique sèche" (1983)** — seminal Sahel windbreak review, no locator found; library search.
- **SciELO** search interface bot-blocked — a human run of `search.scielo.org` with the ES/PT strings is the one channel not executed.
- **Grey-agent dedupe:** FAO 2024 Sénégal, Montagnini (CATIE), RIOCCADAPT, Dias-Filho (Embrapa), Current (CATIE/WB).

## What the multilingual pass added
- **Frost (was 1 primary):** +3 — Quénol & Beltrando 2006 (windbreaks *worsen* spring frost via cold-air pooling — a signed negative F4 effect), Souza 2011 (asset_vulnerability: AF tree frost damage, S Brazil), Robusti 2017 (shaded vs open coffee mortality after the 2013 frost + per-ha economics). Still no synthesis → expect low/very-low confidence, but no longer single-source.
- **Heat stress × silvopasture (LatAm tropical cattle):** Navas 2010, Cisneros 2024, Murgueitio 2013 — Spanish syntheses on tropical breeds absent from EN SR (Deniz 2023 is temperate-dairy-heavy).
- **Francophone Sahel:** FAO 2024 Senegal synthesis of AF adaptation interventions; Botoni/Larwanou/Reij 2010 FMNR vulnerability synthesis (LIC). Lineage with Reij/Sendzimir.
- **LatAm institutional syntheses:** CATIE/CIPAV 2015 volume; RIOCCADAPT (Ibero-American IPCC analogue); Villarreyna 2020 (CATIE/CIRAD EbA coffee).
- **T6 economics/adoption (was the thinnest T6 cell):** Current et al. (21-project cost-benefit + adoption, Central America/Caribbean), Ribeiro SR+MA on adoption (Brazil, the only adoption MA in any of 3 languages), Ferraz 2024 (Brazilian NPV/IRR pool), Dias-Filho 2008 (SPS barriers → M2b).
- **F4 live fences:** Morantes-Toloza 2018 global review — first synthesis touching `planted_boundary_cropland`.
- **Semi-arid Brazil (Caatinga)** as a dryland analogue: Santos 2025.
- **Not added:** cyclone/hurricane (only Holt-Giménez-type primaries; Haiti/Caribbean FR search gave grey only), LMIC fire (only HIC Mediterranean + Pará soil primaries), waterlogging (none), flood impact under AF (only the Loreto floodplain primary, reserve), gender_inequity (only primaries, reserve).

## Saturation
- **OpenAlex title-only:** saturated. Supplementary gap queries (ES5/ES6/FR4/FR5/PT5/PT6) returned 1–34 records, >80% already seen; ES5 (unaccented synthesis markers) returned 1.
- **HAL / CGSpace:** HAL saturated (HAL3 = 0; HAL1/2 overlap OpenAlex). CGSpace FR/ES returns are almost all grey CSA briefs → grey-agent territory.
- **Not saturated:** SciELO native search (blocked), Redalyc/Dialnet native search (no API), and the institutional repositories (CATIE Orton, Embrapa Alice/Infoteca, CIRAD Agritrop full-text) were only sampled via web search. Expected yield from a human SciELO/Embrapa pass: +3–6 sources, mostly primaries/low-tier reviews.
