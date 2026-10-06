# Water harvesting & conservation × T3/T6 — multilingual (ES/FR/PT) `updated_lit` discovery pass — 2026-10-05

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `water_synthesis_first_2026-10-05_ml`, ruleset **v1.6.0**, synthesis-first rule (Pete 2026-10-01). Registered by `scripts/register-discovery.py` on 2026-10-05: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `water_synthesis_first_2026-10-05_ml`, ledger per `--ledger`.


> Staging only (`pipeline/staging/discovery/`). Nothing registered, queued, or ledger-stamped. Ruleset **v1.6.0**; run id `wh_ml_t3t6_2026-10-05`. Targeting rule (Pete 2026-10-01): syntheses first (incl. institutional syntheses); primaries only where a hazard/target/family has no synthesis in any language; null/negative findings kept.
> Dedup: `wh_known_sources.json` (175 rows: 68 SRC + 107 queue) by DOI + normalised title — **no included candidate is known**. The archived 2026-08 WH protocol rows (`_deferred/SRCH*`) were all EN OpenAlex/WebSearch with two ES/FR web strings on terraces/zaï; not repeated.
> English and grey/MEL scopes not duplicated. Institutional syntheses in ES/FR/PT (FAO-LAC, IRD, CILSS, IPEA, Embrapa) are included here per brief and **flagged for grey/MEL-agent dedupe**.
> Deliverable: `wh_multilingual_candidates.json` — **19** candidates (es 4 · fr 8 · pt 7).

## Channels
- **OpenAlex** `/works`, `filter=display_name.search:` (title-only, AGENTS.md rule), `per-page=200`, cursor paging, `mailto=p.steward@cgiar.org`. Accented AND unaccented practice blocks run (ES5, FR4, PT5) per the 2026-10 learning. HTTP 429 rate-limiting hit (sibling agents running in parallel) — FR3/FR4 re-run with backoff; ES3 confirmed 0 on retry.
- **HAL** API `api.archives-ouvertes.fr/search` (`title_t:`), rows=200.
- **CGSpace** DSpace 7 discover API (`dsoType=ITEM`, size=40).
- **SciELO** native search not attempted (bot-blocked per 2026-10 learning); SciELO-BR/CL items reached via OpenAlex DOIs (10.1590/*, 10.4067/*) and Unpaywall.
- **Web search** (US engine) for institutional syntheses: 26 strings (listed under each language).
- **Crossref** DOI round-trip + bibliographic title search; **Unpaywall** (`?email=p.steward@cgiar.org`); direct `curl` of OA PDFs into the scratchpad only (title-page check, nothing written to the repo or `.cache/`).

---

## Spanish (es)

### Verbatim OpenAlex queries · count · retrieved
| id | filter (verbatim) | count | retrieved |
|---|---|---|---|
| ES1 | `display_name.search:("cosecha de agua" OR "cosecha de lluvia" OR "captación de agua de lluvia" OR "captación de agua" OR "captación pluvial" OR "conservación de suelos y agua" OR "conservación de suelo y agua" OR "conservación de suelos" OR terrazas OR andenes OR "zanjas de infiltración" OR bordos OR "medias lunas" OR represas OR atajados OR jagüeyes OR qochas OR amunas OR "barreras de piedra" OR "curvas a nivel") AND (sequía OR sequías OR sequia OR inundación OR inundaciones OR inundacion OR escorrentía OR escorrentia OR "estrés hídrico" OR "déficit hídrico" OR "cambio climático" OR "variabilidad climática" OR resiliencia OR adaptación OR heladas)` | 42 | 42 |
| ES2 | `display_name.search:("cosecha de agua" OR "cosecha de lluvia" OR "captación de agua de lluvia" OR "captación de agua" OR "captación pluvial" OR "conservación de suelos y agua" OR "conservación de suelo y agua" OR "conservación de suelos" OR terrazas OR andenes OR "zanjas de infiltración" OR bordos OR "medias lunas" OR represas OR atajados OR jagüeyes OR qochas OR amunas OR "barreras de piedra" OR "curvas a nivel") AND ("meta-análisis" OR metaanálisis OR metaanalisis OR "revisión sistemática" OR "revision sistematica" OR revisión OR revision OR síntesis OR sintesis OR "estado del arte")` | 8 | 8 |
| ES3 | `display_name.search:("cosecha de agua" OR "cosecha de lluvia" OR "captación de agua de lluvia" OR "captación de agua" OR "captación pluvial" OR "conservación de suelos y agua" OR "conservación de suelo y agua" OR "conservación de suelos" OR terrazas OR andenes OR "zanjas de infiltración" OR bordos OR "medias lunas" OR represas OR atajados OR jagüeyes OR qochas OR amunas OR "barreras de piedra" OR "curvas a nivel") AND (rendimiento OR rendimientos OR productividad OR erosión OR "humedad del suelo" OR recarga OR ingresos OR costos OR costo OR rentabilidad OR "beneficio-costo" OR adopción OR adopcion OR "seguridad alimentaria" OR carbono OR "calidad del agua" OR sedimentos OR pobreza) AND ("meta-análisis" OR metaanálisis OR metaanalisis OR "revisión sistemática" OR "revision sistematica" OR revisión OR revision OR síntesis OR sintesis OR "estado del arte")` | 0 | 0 |
| ES4 | `display_name.search:("cosecha de agua" OR "cosecha de lluvia" OR "captación de agua de lluvia" OR "captación de agua" OR "captación pluvial" OR "conservación de suelos y agua" OR "conservación de suelo y agua" OR "conservación de suelos" OR terrazas OR andenes OR "zanjas de infiltración" OR bordos OR "medias lunas" OR represas OR atajados OR jagüeyes OR qochas OR amunas OR "barreras de piedra" OR "curvas a nivel") AND (rendimiento OR rendimientos OR productividad OR erosión OR "humedad del suelo" OR recarga OR ingresos OR costos OR costo OR rentabilidad OR "beneficio-costo" OR adopción OR adopcion OR "seguridad alimentaria" OR carbono OR "calidad del agua" OR sedimentos OR pobreza),language:es` | 116 | 116 |
| ES5 | `display_name.search:("captacion de agua de lluvia" OR "captacion de agua" OR "conservacion de suelos y agua" OR "conservacion de suelo y agua" OR "conservacion de suelos" OR "zanjas de infiltracion" OR jagueyes OR "cosecha de agua") AND (sequía OR sequías OR sequia OR inundación OR inundaciones OR inundacion OR escorrentía OR escorrentia OR "estrés hídrico" OR "déficit hídrico" OR "cambio climático" OR "variabilidad climática" OR resiliencia OR adaptación OR heladas OR "meta-análisis" OR metaanálisis OR metaanalisis OR "revisión sistemática" OR "revision sistematica" OR revisión OR revision OR síntesis OR sintesis OR "estado del arte")` | 12 | 12 |
| ES6 | `display_name.search:("siembra y cosecha de agua" OR "siembra de agua" OR "siembra y cosecha del agua" OR "cosecha de agua de lluvia" OR "reservorios rústicos" OR "reservorios familiares") AND (sequía OR sequia OR impacto OR impactos OR evaluación OR evaluacion OR efectos OR revisión OR revision OR "revisión sistemática" OR rendimiento OR ingresos OR adaptación OR recarga)` | 9 | 9 |

### Web search strings (es, verbatim)
1. `"Captación y almacenamiento de agua de lluvia" opciones técnicas agricultura familiar América Latina FAO 2013 pdf`
2. `andenes terrazas agrícolas Andes revisión rendimiento erosión beneficios recuperación costo`
3. `Forest Trends "¿Qué sabemos?" impactos infraestructura natural agua suelos revisión qochas amunas zanjas Perú`
4. `Locatelli Forest Trends "zanjas de infiltración" ¿Qué sabemos? revisión sistemática informe completo 2020 pdf`
5. `"La siembra y cosecha de agua en Apurímac, Ayacucho y Huancavelica" revisión sistemática proyectos de desarrollo`
6. `Cárdenas Taboada Tafur Leyva "siembra y cosecha de agua" revisión sistemática 114 proyectos Centro de Competencias del Agua pdf`
7. `cosecha de agua Corredor Seco Centroamericano sistematización evaluación impacto reservorios rendimiento sequía FAO`
8. `"Cosechando agua, sembrando resiliencia" FAO sistemas de captación agua lluvia SCALL resultados`
9. `revisión sistemática cosecha de agua de lluvia agricultura América Latina rendimiento meta-análisis`
10. `revisión terrazas zanjas conservación de suelos América Latina efectividad erosión rendimiento adopción síntesis estudios Centroamérica laderas`
11. `Lutz Pagiola Reiche análisis económico institucional proyectos conservación de suelos Centroamérica Caribe español`

### PRISMA-lite (es)
- Retrieved: OpenAlex 187 (170 unique) · CGSpace CG1 3 + CG4 131 (top 40 screened) · HAL4 2 (mixed) · web 11 strings.
- Title screen: ~210 → heavy noise from `represas` (hydropower dams), `bordos` (aquaculture ponds, levees, "a bordo"), `terrazas` (fluvial geology, forest "bosque de terraza", rooftop terraces), `medias lunas` (Red Crescent). ES3 (practice × outcome × synthesis) = **0** — Spanish title-level WH syntheses are almost absent from OpenAlex; they live in grey/institutional series.
- Abstract/full-text screen: **17**.
- **Included: 4** (Locatelli 2020 SR · Willems 2021 SR · Cárdenas 2022 project-SR · FAO 2013 LAC synthesis).

### Screened out / reserve (es)
| record | reason |
|---|---|
| Bocco et al. 2019 *La agricultura en terrazas en la adaptación a la variabilidad climática, Mixteca Alta* (JLAG, 10.1353/lag.2019.0006, green OA) | primary; terracing × drought has EN syntheses/primaries already queued (Chen 2020 MA, Kosmowski 2018) — **reserve (T3, Mesoamerica)** |
| Hinojosa et al. 2003 *Análisis costo-beneficio de las prácticas de conservación de suelos en Cusco y Apurímac* (no DOI) | primary economics; **reserve (T6 economics, Andean terraces)** — acquire if Willems 2021 gives no cost data |
| PROMIC 2007 CBA obras de conservación, Pajcha/Pintu Mayu Bolivia (CGSpace 10568/21923) | primary economics — reserve |
| Ricra et al. 2022 AMUNA recharge, Idesia (10.4067/s0718-34292022000300051, diamond OA) | primary (single site monitoring); recharge covered by Locatelli 2020 — reserve |
| Qochas recharge (Prospectiva Univ. 2021; tesis UCSUR 2022) | primary / thesis |
| Adoption primaries (La Calera 2012/2018; Chile secano 2012; Danlí 1996; Tierra Blanca 1991) | primary; adoption has EN syntheses |
| *Adopción y rentabilidad de la agroforestería y conservación de suelos en El Salvador* (1998) | lineage with Lutz/Pagiola/Reiche (WB Env. Paper 8, EN) — EN sibling |
| FAO 2020 *Cosechando agua, sembrando resiliencia* (ca8353es) | single-site good-practice sheet (El Salvador) — grey/MEL sibling |
| Fog/atmospheric water harvesting reviews (2021, 2024) | out of scope (not a WH family) |
| Urban/household RWH (Guanajuato, Salamanca, Chile tesis) | urban / domestic-urban |
| Gender: *El impacto de la cosecha de agua de lluvia en la calidad de vida de mujeres rurales mejicanas* (Teuken 2024) | low-tier venue, primary — **reserve for gender** (no synthesis found) |
| ~40 carbon/sediment/limnology records hitting `represa`/`terraza` | relevance |

---

## French (fr)

### Verbatim OpenAlex queries · count · retrieved
| id | filter (verbatim) | count | retrieved |
|---|---|---|---|
| FR1 | `display_name.search:("collecte des eaux de pluie" OR "collecte des eaux" OR "récupération des eaux" OR "récupération des eaux de pluie" OR "conservation des eaux et des sols" OR "conservation des sols" OR "défense et restauration des sols" OR "CES/DRS" OR zaï OR "demi-lunes" OR "demi-lune" OR "cordons pierreux" OR diguettes OR banquettes OR terrasses OR "bassins de rétention" OR "retenues collinaires" OR impluvium OR "ouvrages antiérosifs" OR "aménagements antiérosifs" OR "épandage de crues") AND (sécheresse OR sécheresses OR secheresse OR inondation OR inondations OR ruissellement OR "stress hydrique" OR "déficit hydrique" OR "changement climatique" OR "variabilité climatique" OR résilience OR adaptation)` | 29 | 29 |
| FR2 | `display_name.search:("collecte des eaux de pluie" OR "collecte des eaux" OR "récupération des eaux" OR "récupération des eaux de pluie" OR "conservation des eaux et des sols" OR "conservation des sols" OR "défense et restauration des sols" OR "CES/DRS" OR zaï OR "demi-lunes" OR "demi-lune" OR "cordons pierreux" OR diguettes OR banquettes OR terrasses OR "bassins de rétention" OR "retenues collinaires" OR impluvium OR "ouvrages antiérosifs" OR "aménagements antiérosifs" OR "épandage de crues") AND ("méta-analyse" OR "revue systématique" OR revue OR synthèse OR "état des connaissances" OR bilan OR capitalisation)` | 30 | 30 |
| FR3 | `display_name.search:("collecte des eaux de pluie" OR "collecte des eaux" OR "récupération des eaux" OR "récupération des eaux de pluie" OR "conservation des eaux et des sols" OR "conservation des sols" OR "défense et restauration des sols" OR "CES/DRS" OR zaï OR "demi-lunes" OR "demi-lune" OR "cordons pierreux" OR diguettes OR banquettes OR terrasses OR "bassins de rétention" OR "retenues collinaires" OR impluvium OR "ouvrages antiérosifs" OR "aménagements antiérosifs" OR "épandage de crues") AND (rendement OR rendements OR productivité OR érosion OR "humidité du sol" OR recharge OR revenus OR revenu OR coûts OR coût OR rentabilité OR adoption OR "sécurité alimentaire" OR carbone OR pauvreté OR "analyse économique" OR impact OR impacts),language:fr` | 51 | 51 |
| FR4 | `display_name.search:("recuperation des eaux" OR zai OR "demi lunes" OR "amenagements antierosifs" OR "ouvrages antierosifs" OR "bassins de retention" OR "defense et restauration des sols") AND (sécheresse OR sécheresses OR secheresse OR inondation OR inondations OR ruissellement OR "stress hydrique" OR "déficit hydrique" OR "changement climatique" OR "variabilité climatique" OR résilience OR adaptation OR rendement OR rendements OR productivité OR érosion OR "humidité du sol" OR recharge OR revenus OR revenu OR coûts OR coût OR rentabilité OR adoption OR "sécurité alimentaire" OR carbone OR pauvreté OR "analyse économique" OR impact OR impacts OR "méta-analyse" OR "revue systématique" OR revue OR synthèse OR "état des connaissances" OR bilan OR capitalisation)` | 12 | 12 |
| FR5 | `display_name.search:(zaï OR zai OR tassa OR "demi-lunes" OR "cordons pierreux" OR "conservation des eaux et des sols") AND (Sahel OR "Burkina Faso" OR Niger OR Mali OR Sénégal OR Tchad) AND (sécheresse OR rendement OR rendements OR revenus OR adoption OR impact OR impacts OR synthèse OR revue OR bilan)` | 20 | 20 |

### HAL (`title_t:` verbatim; rows=200)
| id | q (verbatim) | numFound |
|---|---|---|
| HAL1 | `title_t:((zaï OR zai OR "demi-lunes" OR "demi-lune" OR "cordons pierreux" OR diguettes OR banquettes OR "conservation des eaux et des sols" OR "récupération des eaux" OR "collecte des eaux de pluie" OR "défense et restauration des sols" OR "gestion conservatoire") AND (sécheresse* OR rendement* OR érosion OR ruissellement OR "humidité du sol" OR adoption OR revenu* OR coût* OR rentabilit* OR impact* OR résilience OR adaptation))` | 11 |
| HAL2 | `title_t:((zaï OR zai OR "demi-lunes" OR "cordons pierreux" OR banquettes OR "conservation des eaux et des sols" OR "récupération des eaux" OR "collecte des eaux de pluie" OR "gestion conservatoire" OR terrasses OR jessour OR "épandage de crues" OR "lacs collinaires") AND ("méta-analyse" OR "revue systématique" OR revue OR synthèse OR bilan OR "état des connaissances" OR capitalisation OR leçons))` | 4 |
| HAL3 | `title_t:((jessour OR meskat OR "épandage de crues" OR "épandage des crues" OR "irrigation de crue" OR "lacs collinaires" OR "retenues collinaires" OR "citernes" OR "impluvium") AND (Tunisie OR Maroc OR Algérie OR Sahel OR Niger OR "Burkina Faso" OR Mali OR Maghreb OR Afrique OR Yémen OR Haïti))` | 14 |
| HAL4 | `title_t:((cosecha OR captación OR "conservación de suelos" OR terrazas OR andenes OR captação OR cisternas OR barraginhas OR terraços) AND (agua OR água OR suelos OR solo))` | 2 |

### Web search strings (fr, verbatim)
1. `Roose zaï demi-lunes cordons pierreux synthèse efficacité rendement Sahel revue IRD`
2. `Roose "gestion conservatoire de l'eau, de la biomasse et de la fertilité des sols" GCES FAO bulletin pédologique 70`
3. `Nyssen "Érosion et conservation des sols en montagne sahélienne" Éthiopie du Nord Sécheresse 2004`
4. `jessour Tunisie synthèse efficacité ruissellement rendement olivier revue aménagements "jessour" pdf`
5. `Roose Sabir Laouina "Gestion durable des eaux et des sols au Maroc" IRD 2010 valorisation techniques traditionnelles`
6. `"Restauration de la productivité des sols tropicaux et méditerranéens" Roose 2017 IRD Éditions zaï demi-lunes`
7. `Botoni Reij "La transformation silencieuse de l'environnement et des systèmes de production au Sahel" CILSS 2009 pdf`
8. `"transformation silencieuse" Botoni Reij 2009 CILSS "gestion des ressources naturelles" pdf download`
9. `"Pour une gestion durable des sols en Afrique subsaharienne" Cahiers Agricultures 2024 revue CES`
10. `synthèse "techniques de conservation des eaux et des sols" Burkina Faso Niger impacts rendements revenus évaluation "demi-lunes" "zaï" capitalisation rapport`
11. `épandage des crues irrigation de crue Maghreb Sahel synthèse "épandage de crues" efficacité rendement revue`
12. `Heusch "Pourquoi la banquette CES diminue les rendements" Bulletin Réseau Erosion`
13. `Roose Kaboré Guenat 1993 "Le zaï" Cahiers ORSTOM Pédologie horizon.documentation.ird.fr pdf`
14. `Arabi Kedaid Bourougaa Asla Roose 2004 "Bilan de l'enquête sur la défense et restauration des sols" Sécheresse pdf horizon IRD`

### PRISMA-lite (fr)
- Retrieved: OpenAlex 142 (121 unique) · HAL 31 · CGSpace CG2 0 + CG5 233 (top 40 screened) · web 14 strings.
- Title screen: ~190 → noise from `terrasses` (archaeology, fluvial, rooftop), `banquettes` (Posidonia seagrass), `bassins de rétention` (urban stormwater), `zai` (Chinese names), `retenues collinaires` in HIC France.
- Abstract/full-text screen: **24**.
- **Included: 8** (Roose 1994 GCES · Roose 2017 IRD vol. · Roose/Sabir/Laouina 2010 Maroc · Roose/Kaboré/Guenat 1993 zaï · Roose 2006 terrasses · Arabi et al. 2004 DRS Algérie · Heusch 1995 [negative] · Botoni & Reij 2009 CILSS).

### Screened out / reserve (fr)
| record | reason |
|---|---|
| Nyssen et al. 2004 *Érosion et conservation des sols en montagne sahélienne : Éthiopie du Nord* (Sécheresse 15(1)) | primary catchment study; EN Nyssen/Tigray work is the EN sibling's — reserve |
| Da 2008 *Impact des techniques CES sur le rendement du sorgho, centre-nord Burkina* (10.4000/com.3512, hybrid OA) | primary; in_situ × production has syntheses (Roose 1993/1994, Botoni 2009) — reserve |
| Bayen et al. 2012 *Effet du zaï amélioré sur la productivité du sorgho* (10.4000/vertigo.11497, gold OA) | primary — reserve |
| Zougmoré et al. *Rôle des nutriments dans le succès des techniques CES* (IRD Horizon fdi:010033564) | primary experiments — reserve |
| Diarra & Riedacker 2017 *Synergies entre récupération des eaux de ruissellement et fertilisations minérales* (DOAJ) | primary comparison zaï vs 200 m³ reservoirs; venue unclear — reserve (runoff_catchment Sahel) |
| Zaï/demi-lune rentabilité primaries (IJBCS 2023; Annales Parakou 2019; ESJ 2022 Ouallam; Tillabéry 2017; JAB 2020 banquettes Niger) | primary; low-tier venues |
| Adoption primaries (Bani 2010; Korsimoro 2024; Nord Burkina 2008) | primary; adoption covered by syntheses |
| Retenues collinaires synthèses (France, HAL 2013) | HIC irrigation reservoirs |
| Banquettes en cascade Tunisie (HSJ 2007, 10.1623/hysj.52.6.1134) · banquettes ruissellement (Rev. Sci. Eau 2005, 10.7202/705534ar) | primary hydrology; terracing covered by Roose 2006/Arabi 2004 — reserve |
| Jessour (Geoconfluences narrative; MDPI Water EN primaries) | EN primaries (sibling); FR narrative not a synthesis; jessour WOCAT 1013 already in SRC |
| Dugué, Andrieu & Bakker 2024 *Pour une gestion durable des sols en Afrique subsaharienne* (10.1051/cagri/2024003) | soil-fertility review, WH marginal |
| CGSpace FR CSA inventories/briefs (Sénégal 2022, AIC Bénin/BF 2024, Ouamega-Nikiema 2019 demi-lunes case) | grey practice catalogues → grey/MEL sibling |
| Morris 2014 (CGSpace, EN review AWM Burkina) · Barry 2008 IWMI · Nguru 2026 SR (10.3390/su18020787) · Dorren & Rey 2004 terracing review (HAL) | **English** — pass to EN sibling (not checked against its list) |

---

## Portuguese (pt)

### Verbatim OpenAlex queries · count · retrieved
| id | filter (verbatim) | count | retrieved |
|---|---|---|---|
| PT1 | `display_name.search:("captação de água de chuva" OR "captação de água da chuva" OR "captação de água" OR "aproveitamento de água de chuva" OR "aproveitamento da água da chuva" OR barraginhas OR terraços OR terraceamento OR "barragens subterrâneas" OR "barragem subterrânea" OR cisternas OR cisterna OR "curvas de nível" OR "conservação do solo e da água" OR "conservação do solo" OR "práticas conservacionistas" OR P1MC OR "Um Milhão de Cisternas" OR "tecnologias sociais hídricas") AND (seca OR secas OR estiagem OR inundação OR inundações OR escoamento OR "déficit hídrico" OR "mudanças climáticas" OR resiliência OR adaptação OR semiárido OR "semi-árido" OR "convivência com o semiárido")` | 237 | 200 |
| PT2 | `display_name.search:("captação de água de chuva" OR "captação de água da chuva" OR "captação de água" OR "aproveitamento de água de chuva" OR "aproveitamento da água da chuva" OR barraginhas OR terraços OR terraceamento OR "barragens subterrâneas" OR "barragem subterrânea" OR cisternas OR cisterna OR "curvas de nível" OR "conservação do solo e da água" OR "conservação do solo" OR "práticas conservacionistas" OR P1MC OR "Um Milhão de Cisternas" OR "tecnologias sociais hídricas") AND ("meta-análise" OR metanálise OR "revisão sistemática" OR revisão OR revisao OR síntese OR "estado da arte" OR "revisão integrativa")` | 6 | 6 |
| PT3 | `display_name.search:("captação de água de chuva" OR "captação de água da chuva" OR "captação de água" OR "aproveitamento de água de chuva" OR "aproveitamento da água da chuva" OR barraginhas OR terraços OR terraceamento OR "barragens subterrâneas" OR "barragem subterrânea" OR cisternas OR cisterna OR "curvas de nível" OR "conservação do solo e da água" OR "conservação do solo" OR "práticas conservacionistas" OR P1MC OR "Um Milhão de Cisternas" OR "tecnologias sociais hídricas") AND (produtividade OR rendimento OR erosão OR "perdas de solo" OR "umidade do solo" OR recarga OR renda OR custos OR custo OR "viabilidade econômica" OR adoção OR "segurança alimentar" OR "segurança hídrica" OR carbono OR "qualidade da água" OR pobreza OR impacto OR impactos OR avaliação) AND ("meta-análise" OR metanálise OR "revisão sistemática" OR revisão OR revisao OR síntese OR "estado da arte" OR "revisão integrativa")` | 2 | 2 |
| PT4 | `display_name.search:("captação de água de chuva" OR "captação de água da chuva" OR "captação de água" OR "aproveitamento de água de chuva" OR "aproveitamento da água da chuva" OR barraginhas OR terraços OR terraceamento OR "barragens subterrâneas" OR "barragem subterrânea" OR cisternas OR cisterna OR "curvas de nível" OR "conservação do solo e da água" OR "conservação do solo" OR "práticas conservacionistas" OR P1MC OR "Um Milhão de Cisternas" OR "tecnologias sociais hídricas") AND (produtividade OR rendimento OR erosão OR "perdas de solo" OR "umidade do solo" OR recarga OR renda OR custos OR custo OR "viabilidade econômica" OR adoção OR "segurança alimentar" OR "segurança hídrica" OR carbono OR "qualidade da água" OR pobreza OR impacto OR impactos OR avaliação),language:pt` | 257 | 200 |
| PT5 | `display_name.search:("captacao de agua de chuva" OR "captacao de agua" OR "aproveitamento de agua de chuva" OR terracos OR "barragens subterraneas" OR "barragem subterranea" OR "conservacao do solo" OR "curvas de nivel") AND (seca OR secas OR estiagem OR inundação OR inundações OR escoamento OR "déficit hídrico" OR "mudanças climáticas" OR resiliência OR adaptação OR semiárido OR "semi-árido" OR "convivência com o semiárido" OR "meta-análise" OR metanálise OR "revisão sistemática" OR revisão OR revisao OR síntese OR "estado da arte" OR "revisão integrativa")` | 1 | 1 |
| PT6 | `display_name.search:("Uma Terra e Duas Águas" OR "P1+2" OR "cisternas de produção" OR "cisterna de produção" OR "segunda água" OR "cisterna calçadão" OR "cisternas calçadão" OR "barreiro trincheira" OR "barragem subterrânea" OR barraginhas) AND (impacto OR impactos OR avaliação OR renda OR produção OR produtividade OR "segurança alimentar" OR seca OR estiagem OR revisão)` | 35 | 35 |

### CGSpace (all languages; verbatim)
| id | query (verbatim; dsoType=ITEM, size=40) | total |
|---|---|---|
| CG1 | `dc.title:("cosecha de agua" OR "captación de agua" OR "conservación de suelos" OR terrazas OR andenes OR "zanjas de infiltración" OR qochas OR atajados) AND dc.title:(revisión OR síntesis OR sequía OR adaptación OR resiliencia OR impacto OR evaluación OR adopción OR "costo-beneficio" OR rendimiento)` | 3 |
| CG2 | `dc.title:(zaï OR "demi-lunes" OR "cordons pierreux" OR "conservation des eaux et des sols" OR "récupération des eaux" OR "collecte des eaux" OR "gestion conservatoire" OR diguettes) AND dc.title:(synthèse OR revue OR sécheresse OR adaptation OR résilience OR impact OR évaluation OR adoption OR rendement OR rentabilité)` | 0 |
| CG3 | `dc.title:("captação de água" OR cisternas OR barraginhas OR "barragens subterrâneas" OR terraços OR "conservação do solo") AND dc.title:(revisão OR síntese OR seca OR adaptação OR impacto OR avaliação OR adoção OR produtividade)` | 0 |
| CG4 | `("cosecha de agua" OR "captación de agua de lluvia" OR "conservación de suelos y agua") AND (revisión OR síntesis OR "meta-análisis" OR "lecciones aprendidas" OR sistematización)` | 131 |
| CG5 | `(zaï OR "demi-lunes" OR "cordons pierreux" OR "conservation des eaux et des sols" OR "récupération des eaux") AND (synthèse OR revue OR "méta-analyse" OR capitalisation OR bilan)` | 233 |
| CG6 | `("captação de água de chuva" OR cisternas OR barraginhas OR "barragens subterrâneas") AND (revisão OR síntese OR avaliação OR impacto)` | 20 |

### Web search strings (pt, verbatim)
1. `Embrapa Semiárido "Potencialidades da água de chuva no Semi-Árido brasileiro" livro pdf`
2. `IPEA "Texto para Discussão 2722" avaliação programa cisternas captação de água de chuva`
3. `MDS Programa Cisternas estudos e avaliações avaliação de impacto segurança alimentar renda produção cisternas segunda água`
4. `Barraginhas Embrapa Milho e Sorgo avaliação recarga produtividade "barraginhas" documento síntese Barros`
5. `"Tecnologias sociais e renda" Programa Cisternas segunda água evidências avaliação impacto`

### PRISMA-lite (pt)
- Retrieved: OpenAlex 538 (384 unique; PT1 and PT4 capped at 200 of 237/257) · CGSpace CG3 0 + CG6 20 · web 5 strings.
- Title screen: ~400 → dominant noise = urban/building RWH sizing, potability case studies, and dozens of single-community P1MC descriptive papers.
- Abstract/full-text screen: **23**.
- **Included: 7** (Castro 2022 IPEA TD 2722 · Brito et al. 2007 Embrapa · Arsky 2020 · Silva 2009 Água-Vida · Casagrande et al. 2022 [primary, gap] · Miranda 2019 Embrapa barraginhas · Cirilo et al. 2003 subsurface dams).

### Screened out / reserve (pt)
| record | reason |
|---|---|
| Silva, Khan, Costa, Amorim & Tabosa 2021 P1+2 PSM, Iguatu-CE (10.38116/ppp57art3, gold OA) | primary quasi-experimental (income ↑, jobs n.s.) — **reserve (T6 rural_poverty)**; Casagrande 2022 national panel preferred |
| Gomes & Heller 2016 P1MC access to water (10.1590/s1413-41522016128417, gold) | qualitative policy analysis — reserve |
| Morais, Paiva & Sousa 2017 *Avaliação do P1MC: eficácia, eficiência e efetividade, RN 2003-2015* (10.18764/2178-2865.v21n1p133-158, gold) | subnational evaluation, overlaps IPEA TD 2722 — reserve |
| Lima et al. 2013 *Barragens subterrâneas no semiárido: análise histórica e metodologias de construção* (Irriga, 10.15809/irriga.2013v18n2p200) | review of construction methods, few outcomes — reserve |
| Cavalcanti et al. 1999 *Avaliação do uso de técnicas de captação de água de chuva no semi-árido* (RBEAA, 10.1590/1807-1929/agriambi.v3n3p403-407) | 179-farmer adoption survey (primary) — reserve (adoption) |
| Borges et al. 2014 *Práticas conservacionistas … umidade do solo … milho, semiárido* (RBCS, 10.1590/s0100-06832014000600021) | primary in_situ — reserve |
| Cistern health impact primaries (diarreia, Rev Bras Saúde Mat Inf 2011; saúde infantil 2015; IPEA SUS study) | health not a T5 priority (water_quality only via Silva 2009) |
| ~60 cistern water-quality / sizing / single-community papers; urban RWH | primary / urban |
| Do P1MC ao Água para Todos (10.4000/ideas.7219) | political science, no outcomes |
| Gender: *A estreita relação entre mulher e água no semiárido: P1MC* (RLAGG 2012) | primary — **reserve for gender** (no synthesis) |
| CGSpace PT: CTA *Capitalização de experiências* Moçambique/Brasil 2018; quintais agroecológicos 2018 | grey case collections → grey sibling |

---

## Draft `SRCH` rows

```
nbs_id=water_harvesting_conservation | suitability_family_id="" | table=T3 | process=updated_lit
search_terms = OpenAlex display_name.search verbatim filters ES1,ES2,ES5,ES6,FR1,FR2,FR4,FR5,PT1,PT2,PT5,PT6 (AGROVOC ES/FR/PT practice block × hazard [sequía/sécheresse/seca · inundación/inondation/inundação · escorrentía/ruissellement/escoamento · estrés/déficit hídrico · cambio climático/changement climatique/mudanças climáticas · resiliencia · adaptación · heladas] or synthesis block; accented + unaccented variants); HAL title_t HAL1–HAL4; CGSpace CG1–CG6; web search (ES 11, FR 14, PT 5 strings, verbatim in discovery log); SciELO native search not run (bot-blocked; reached via OpenAlex DOIs)
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = ES/FR/PT synthesis (SR / review / institutional or programme-evaluation synthesis in a reputable venue) reporting a WH/SWC (any family) effect on a T3 hazard's livelihood impact, or hazard damage to the WH asset (asset_vulnerability: terrace failure, structure overtopping); primaries only where the hazard × family cell has no synthesis in any language; null/negative findings kept; exclude PADs, urban/building RWH, fog harvesting, hydropower/large dams, aquaculture ponds, predatory venues, known sources, translations of EN papers
limits = retrieve<=200/query; screen<=80 (abstract/full-text, shared with T6); include<=25 overall (shared with T6); title-only; multilingual ES/FR/PT
n_retrieved≈1,000 (OpenAlex 867 records [675 unique, shared with T6], HAL 31, CGSpace ≈100 title-screened) | n_screened=64 (shared) | n_included=14 (T3 or T3|T6)
search_date=2026-10-05 | run_id=wh_ml_t3t6_2026-10-05 | searched_by=discovery-agent (multilingual) | ruleset_version=v1.6.0
note = multilingual complement to the EN and grey/MEL WH passes; generic parent search (family=""); do NOT stamp ledger searched=done from this alone
```

```
nbs_id=water_harvesting_conservation | suitability_family_id="" | table=T6 | process=updated_lit
search_terms = OpenAlex display_name.search verbatim filters ES2,ES3,ES4,ES5,ES6,FR2,FR3,FR4,FR5,PT2,PT3,PT4,PT5,PT6 (practice × outcome [rendimiento/rendement/produtividade · erosión/érosion/erosão · humedad del suelo/humidité du sol/umidade do solo · recarga/recharge · ingresos/revenus/renda · costos/coûts/custos · rentabilidad/rentabilité/viabilidade econômica · adopción/adoption/adoção · seguridad alimentaria/sécurité alimentaire/segurança alimentar · carbono/carbone · calidad del agua/qualidade da água · pobreza/pauvreté] [× synthesis markers for ES3/PT3; language:es/fr/pt filter for ES4/FR3/PT4]); HAL HAL1–HAL4; CGSpace CG1–CG6; web search (as T3)
screening_steps = frame · source_type · relevance · credibility_six_axis · saturation_stop
inclusion_criteria = ES/FR/PT synthesis reporting a WH/SWC effect on a T5 priority (production_gap, water_stress, soil_erosion_risk, rural_poverty, carbon, water_quality_risk) or economics/adoption with denominators; primaries only for gap cells (rural_poverty causal income estimate; subsurface dams; signed-negative banquette evidence kept); exclusions as T3
limits = as T3 (shared caps)
n_retrieved≈1,000 (shared) | n_screened=64 (shared) | n_included=19 (T6 or T3|T6)
search_date=2026-10-05 | run_id=wh_ml_t3t6_2026-10-05 | searched_by=discovery-agent (multilingual) | ruleset_version=v1.6.0
note = T3 and T6 rows share one retrieval set; n_included overlaps (14 candidates are T3|T6, 5 T6-only); total unique included = 19
```

---

## Included candidates (19)

### es (4)
| id | citation (short) | tables | hazards | T6 targets | families | tier | OA |
|---|---|---|---|---|---|---|---|
| locatelli_2020_zanjas_es | Locatelli, B.; Homberger, J.-M.; Ochoa-Tocachi, B.F.; Bonnesoeur, V.; Román, F.; Drenkhan, F.; Buytaert, W. (2… | T3|T6 | flood | soil_erosion_risk, water_stress | in_situ, micro_catchment | high | oa_direct |
| willems_2021_andenes_es | Willems, B.; Leyva-Molina, W.-M.; Taboada-Hermoza, R.; Bonnesoeur, V.; Román, F.; Ochoa-Tocachi, B.F.; Buytaer… | T3|T6 | drought, flood | soil_erosion_risk, water_stress, production_gap, economics | terracing | high | oa_direct |
| cardenas_2022_siembra_cosecha_sr_es | Cárdenas, F.; Taboada, R.; Tafur, J.; Leyva, W.M. (2022). La siembra y cosecha de agua en Apurímac, Ayacucho y… | T3|T6 | drought | water_stress, adoption, economics | runoff_catchment, in_situ, micro_catchment | medium | rg_flag_for_human |
| fao_2013_captacion_es | FAO; FIDA; Cooperación Suiza (2013). Captación y almacenamiento de agua de lluvia: opciones técnicas para la a… | T3|T6 | drought | production_gap, water_stress, economics | rooftop, runoff_catchment, in_situ, micro_catchment | medium | oa_direct |

### fr (8)
| id | citation (short) | tables | hazards | T6 targets | families | tier | OA |
|---|---|---|---|---|---|---|---|
| roose_1994_gces_fr | Roose, É. (1994). Introduction à la gestion conservatoire de l'eau, de la biomasse et de la fertilité des sols… | T3|T6 | drought, flood | soil_erosion_risk, production_gap, water_stress, adoption, economics | in_situ, micro_catchment, terracing | high | oa_direct |
| roose_2017_restauration_fr | Roose, É. (éd.) (2017). Restauration de la productivité des sols tropicaux et méditerranéens : contribution à … | T3|T6 | drought, flood | production_gap, soil_erosion_risk, carbon_sequestration_potential, water_stress, economics, adoption | in_situ, micro_catchment, terracing | medium | oa_direct |
| roose_2010_maroc_fr | Roose, É.; Sabir, M.; Laouina, A. (2010). Gestion durable des eaux et des sols au Maroc : valorisation des tec… | T3|T6 | drought, flood | soil_erosion_risk, production_gap, water_stress, adoption | terracing, in_situ, runoff_catchment, spate | medium | oa_direct |
| roose_1993_zai_fr | Roose, É.; Kaboré, V.; Guenat, C. (1993). Le zaï : fonctionnement, limites et amélioration d'une pratique trad… | T3|T6 | drought | production_gap, soil_erosion_risk, water_stress | in_situ | medium | oa_direct |
| roose_2006_terrasses_afrique_fr | Roose, É. (2006). Les terrasses antiérosives en Afrique : typologie, efficacité, limites et améliorations. In:… | T3|T6 | flood, drought | soil_erosion_risk, production_gap, adoption | terracing | medium | oa_direct |
| arabi_2004_drs_algerie_fr | Arabi, M.; Kedaid, O.E.; Bourougaa, L.; Asla, T.; Roose, É. (2004). Bilan de l'enquête sur la défense et resta… | T6 | — | soil_erosion_risk, production_gap, adoption | terracing, runoff_catchment | medium | rg_flag_for_human |
| heusch_1995_banquette_fr | Heusch, B. (1995). Pourquoi la banquette CES diminue les rendements et augmente l'érosion. In: De Noni, G.; Ro… | T6 | — | production_gap, soil_erosion_risk | terracing | low | oa_direct |
| botoni_reij_2009_cilss_fr | Botoni, E.; Reij, C. (2009). La transformation silencieuse de l'environnement et des systèmes de production au… | T3|T6 | drought | production_gap, rural_poverty, water_stress, adoption | in_situ, micro_catchment, terracing | medium | rg_flag_for_human |

### pt (7)
| id | citation (short) | tables | hazards | T6 targets | families | tier | OA |
|---|---|---|---|---|---|---|---|
| castro_2022_ipea_cisternas_pt | Castro, C.N. de (2022). Avaliação do programa nacional de apoio à captação de água de chuva e outras tecnologi… | T3|T6 | drought | water_stress, rural_poverty, production_gap, economics | rooftop, runoff_catchment | medium | oa_direct |
| brito_2007_embrapa_aguachuva_pt | Brito, L.T. de L.; Moura, M.S.B. de; Gama, G.F.B. (eds. técnicos) (2007). Potencialidades da água de chuva no … | T3|T6 | drought | production_gap, water_stress, economics | rooftop, runoff_catchment, in_situ | medium | oa_direct |
| arsky_2020_cisternas_pt | Arsky, I. da C. (2020). Os efeitos do Programa Cisternas no acesso à água no semiárido. Desenvolvimento e Meio… | T3|T6 | drought | water_stress, rural_poverty | rooftop | medium | oa_direct |
| silva_2009_embrapa_aguavida_pt | Silva, A. de S. (coord.) (2009). Avaliação da sustentabilidade do Programa Cisternas do MDS em parceria com a … | T6 | — | water_quality_risk, water_stress, adoption | rooftop | medium | oa_direct |
| casagrande_2022_segunda_agua_pt | Casagrande, D.; Emanuel, L.; Freitas, C.E. de; Lima, A.; Nishimura, F. [author list to confirm] (2022). Tecnol… | T6 | — | rural_poverty, economics | rooftop, runoff_catchment | low | oa_direct |
| miranda_2019_embrapa_barraginhas_pt | Miranda, R.A. de (resp.) (2019). Relatório de avaliação dos impactos de tecnologias geradas pela Embrapa: Mini… | T6 | — | economics, production_gap, soil_erosion_risk, water_stress | runoff_catchment, micro_catchment | low | oa_direct |
| cirilo_2003_barragens_subterraneas_pt | Cirilo, J.A.; Abreu, G.H.F.G. de; Costa, M.R. da; Baltar, A.M.; Azevedo, L.G.T. de (2003). Soluções para o sup… | T3|T6 | drought | water_stress, water_quality_risk, economics | runoff_catchment | low | oa_direct |

---

## DOI round-trip (Crossref) and OA recovery
- **5 included DOIs, all pass** the Crossref title round-trip: td2722 (0.97; Crossref prefixes "TD 2722 -"), dma.v55i0.73378 (1.0), rbrh.v8n4.p5-24 (1.0), books.irdeditions.24108 (1.0, edited-book), books.irdeditions.294 (1.0). Citations rebuilt from Crossref authors/container/vol/issue/pages.
- **DOI failure:** `10.4000/books.irdeditions.600` (seen on the web for Roose, Sabir & Laouina 2010) → Crossref **404** → blanked; the correct DOI `10.4000/books.irdeditions.294` came from a Crossref title search and was then round-trip verified. Treat as recovered: still have a human eyeball it.
- **14 included DOI-less** (Locatelli 2020, Willems 2021, Cárdenas 2022, FAO 2013, Roose 1994, Roose 1993, Roose 2006, Arabi 2004, Heusch 1995, Botoni & Reij 2009, Brito 2007, Silva 2009, Casagrande 2022, Miranda 2019; Crossref title searches returned no matching record): `title_verified=false`, `acquire_by=title` → need `verify_metadata.py verify-titles` after caching. For 10 of them the title page was checked by fetching the OA PDF into the scratchpad (not cached to `.cache/corpus/`).
- Bracketed fields (`[author list to confirm]` on Casagrande 2022) were deliberately not filled from memory.
- **OA breakdown (19): oa_direct 16 · rg_flag_for_human 3 · paywalled 0.** Gold/diamond OA dominates the journal items (UFPR *Desenvolvimento e Meio Ambiente*, ABRH *RBRH*, IPEA TD); institutional repositories: IRD Horizon (Roose ×4, Heusch), OpenEdition IRD Éditions (Roose 2010, 2017), FAO (i3247s), Forest Trends (×2), Embrapa Alice/Infoteca/BS (×3), ANPEC. The 3 `rg_flag_for_human` items (Cárdenas 2022, Arabi 2004, Botoni & Reij 2009) have **no OA copy confirmed by tool** after Unpaywall (where DOI) + ≥2 web searches each, but are NOT labelled paywalled: ResearchGate copies (370716126, 282171205) and CILSS/IRD Horizon need a human check first.

## Flagged for a human
- **Roose 1994 (FAO Bull. Péd. 70):** an EN edition exists (FAO Soils Bulletin 70). Pick one edition with the EN sibling; don't extract both (lineage).
- **Roose 2017 / Roose 2010 (OpenEdition):** chapters are served as HTML (PDF via OpenEdition Freemium). Under the acquisition rule, decide whether to cache chapter PDFs (page locators) or HTML snapshots (section locators) **before** registering anything.
- **Botoni & Reij 2009 vs Botoni, Larwanou & Reij 2010 (agroforestry pass):** same authors, overlapping Sahel case studies → `lineage_of` check at extraction.
- **Arsky 2020** and **Miranda 2019 (Embrapa)**: authors tied to the programme / technology owner → independence/COI discount. Also IPEA TD 2722 cites the MDS evaluations → lineage with Silva 2009 and Arsky 2020.
- **Barraginhas family mapping** (runoff_catchment vs micro_catchment) needs a family-owner decision.
- **Casagrande et al. 2022:** conference paper; check for a later peer-reviewed version; confirm the author list.
- **Cárdenas 2022:** year/ISBN come from a citing source and need checking on the cover.
- **English items found in FR/ES channels** (Morris 2014 IWMI/CGSpace; Barry 2008 IWMI; Nguru 2026 SR 10.3390/su18020787; Dorren & Rey 2004 terracing-erosion review, HAL; Lutz, Pagiola & Reiche 1994 WB Env. Paper 8): hand to the EN sibling (I did not check them against its list).
- **Grey/MEL-agent dedupe:** FAO 2013, Cárdenas 2022, Botoni & Reij 2009, IPEA TD 2722, Silva 2009, Miranda 2019, Brito 2007.
- **Web-summary numbers are not evidence:** search summaries quoted figures (e.g. trench soil-loss %, cistern income %, zaï yields). None are recorded here; extract them only from cached artefacts.

## What the multilingual pass added
- **Sahel zaï / demi-lunes / cordons pierreux (FR):** the francophone evidence base is there, written by the original research team. Roose et al. 1993 is the founding zaï paper, Roose 1994 GCES is the FAO synthesis, the 2017 IRD volume is the most recent, and Botoni & Reij 2009 is the landscape-scale CILSS impact synthesis for LIC Burkina/Niger. Half-moons and stone lines are reviewed only *inside* these volumes; no stand-alone FR demi-lune synthesis was found (only low-tier primaries).
- **Negative and failure evidence (FR):** Heusch 1995 (Niger diversion banquettes: lower yields, more erosion), Arabi et al. 2004 (40-year national ex-post of Algerian DRS banquettes, with abandonment) and Roose 2006 (conditions where African terraces fail: landslide, swelling clays, steep slopes). These give the terracing cells a signed-negative side and the first T3 asset_vulnerability evidence for terraces.
- **Spate family (FR):** Roose, Sabir & Laouina 2010 (Morocco, épandage des crues chapter) is the **only synthesis touching `spate`** in any of the three languages. It is thin, but no longer zero.
- **Brazilian semi-arid cisterns (PT):** a programme-evaluation stack for the `rooftop` family, which had no LMIC programme evidence in the known list: IPEA TD 2722 synthesis, Arsky 2020 (drought-period water access), Silva 2009 (water quality and maintenance, 1,328 households) and Casagrande 2022 (the only causal estimate of income effect for production cisterns). Brito 2007 (Embrapa) adds subsurface dams and in-situ capture; Cirilo 2003 covers subsurface dams.
- **Barraginhas (PT):** the only structured assessment found is Embrapa's 2019 self-assessment of economics, erosion and recharge. Low tier (COI).
- **Andean terraces / trenches / siembra y cosecha (ES):** two systematic reviews from the Forest Trends INSH series, Locatelli 2020 (infiltration trenches; peak-flow attenuation counts toward T3 flood) and Willems 2021 (andenes), plus a project-portfolio SR of 114 Peruvian projects (Cárdenas 2022). FAO 2013 is the LAC rainwater-harvesting synthesis.
- **Not added:** waterlogging (none in any language) and heat_stress (none, as expected for WH). Mesoamerican terraces are only primaries (Bocco 2019, reserve). Corredor Seco reservoirs are only grey good-practice sheets. Gender: only low-tier primaries in ES and PT (reserve). Carbon: no WH synthesis (Roose 2017 touches soil organic matter). Spanish adoption: only primaries.

## Saturation
- **OpenAlex title-only:** saturated for syntheses. ES3 (practice × outcome × synthesis) = 0, and PT3 = 2. The synonym-gap queries ES6 (`siembra de agua`), PT6 (`P1+2`, `segunda água`, `barragem subterrânea`) and FR5 (Sahel country-qualified) returned 9/35/20 records, all primaries, and none changed the include set.
- **HAL:** saturated (31 hits, mostly HIC/urban; HAL2 synthesis = 4, none in scope). **CGSpace:** ES/FR synthesis returns are grey CSA briefs (grey sibling), apart from the Locatelli brief.
- **Not saturated:** SciELO native search (blocked) and IRD Horizon full catalogue (only sampled via web; it is the likeliest source of further FR Sahel/Maghreb SWC reviews). Also not searched: Embrapa Alice/Infoteca native search, Redalyc/Dialnet native, and CILSS/AGRHYMET documentation. A human pass on IRD Horizon + Embrapa Alice would most likely add **+3–6** sources, mostly primaries or narrative reviews.
