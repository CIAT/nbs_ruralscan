# Drought-year round 2: discovery report for agroforestry, water harvesting and forest restoration (T3, plus T6 where noted)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `water_synthesis_first_2026-10-06_drought`, ruleset **v1.6.2**, synthesis-first rule (Pete 2026-10-01). Registered by `scripts/register-discovery.py` on 2026-10-06: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `water_synthesis_first_2026-10-06_drought`, ledger per `--ledger`.


- **Date:** 2026-10-06
- **Ruleset in force:** v1.6.x (synthesis-first; OA-recovery; DOI/title round-trip)
- **Agent:** discovery subagent. It wrote to staging only and ran no git commands.
- **Question:** what happens to crop yield, livestock output, income or food security **in drought or dry years** under the practice, compared with a no-practice comparator in the same drought? Secondary: heat-stress-year and flood/cyclone-year effects.
- **Outputs:**
  - `drought_wh_candidates.json` (30)
  - `drought_af_candidates.json` (19)
  - `drought_fr_candidates.json` (13)
  - 61 unique sources in total. Constenla-Villoslada 2022 is deliberately listed for both WH and FR.

## Method
1. **Frame.** The hazard has to be stated by the source: a drought, dry or El Niño year, a rainfall-shock interaction, a stability or downside-risk metric, or at minimum an aridity or low-rainfall stratum. A practice comparator is required.
2. **Source-type triage.** Syntheses (meta-analyses, systematic reviews, stability analyses) come first. Then drought-year primaries and evaluations. Modelled-only sources are kept as fill-only and tiered low.
3. **Relevance.** LMIC sources are preferred. HIC-only items are kept only where an LMIC equivalent was not found, and are tagged by income group so `transfer_class` can down-weight them.
4. **Six-axis credibility.** Applied to the proposed tier. Grey sources carry the positive-bias note.
5. **Saturation stop.** Applied per NbS once new queries returned only known or irrelevant titles.

**De-duplication.** Every hit was checked against all DOIs and normalised citations in:
- `pipeline/acquisition_queue.csv`
- `schema/registers/SRC_source_register.csv`
- every existing `pipeline/staging/discovery/*.json`

Hits already present were dropped silently and are counted below. Examples: Kosmowski 2018 (terraces / 2015 drought), Weston 2015, Haglund 2011, Sendzimir 2011, Lasco 2014, Kuyah 2019, Corbeels 2020, Steward 2018 (CA meta-regression), Kato 2011, Zougmoré 2014 and Hao 2026 (shelterbelt meta). The final 61 were re-checked after Crossref resolution, with zero collisions.

**DOI rule.** Every DOI comes from a Crossref record retrieved by DOI, and `crossref_title` is stored in each candidate. Citations were rebuilt from Crossref. Three items have no trustworthy DOI and are marked `acquire_by_title=true` with a blank `doi`:
- Kaboré & Reij 2004, IFPRI EPTD DP 114
- the Annals of Arid Zone silvopastoral paper (the OpenAlex DOI 10.56093/aaz.v47i1.64902 does not resolve in Crossref)
- the World Bank 2025 Bangladesh mangrove report

**OA recovery.**
1. Unpaywall was checked by DOI for every candidate.
2. For every closed item, OpenAlex alternate locations were checked, and CGSpace items were checked through the DSpace REST API. All 8 CGSpace handles found are "Limited Access".
3. A title/author web search was run per item for the higher-tier items.
4. Nothing is labelled `paywalled`. Closed items carry `oa_status=rg_flag_for_human` and `access_route="institutional (only after human RG check)"`.

## Verbatim queries — channel 1 OpenAlex title search
All of these used `https://api.openalex.org/works?filter=title.search:<QUERY>&per-page=50&sort=cited_by_count:desc`. Counts are shown as **[n_retrieved]**. Up to the top 50 per query were screened.

### Verbatim queries — water_harvesting_conservation (OpenAlex)
- [63] `("conservation agriculture" OR "no-till" OR "zero tillage" OR "minimum tillage") AND (drought OR "dry year" OR "dry years" OR "rainfall variability" OR "yield stability" OR "El Niño")`
- [12] `("tied ridges" OR "tied ridging" OR zai OR "planting pits" OR "stone bunds" OR "half-moon" OR "half moons" OR "contour bunds") AND (drought OR "dry year" OR "dry spell" OR "rainfall" OR "yield stability" OR risk)`
- [147] `("water harvesting" OR "rainwater harvesting" OR "farm pond" OR "farm ponds" OR "check dam" OR "check dams") AND (drought OR "dry year" OR "dry spell" OR "yield stability" OR resilience)`
- [7] `(terrace OR terraces OR terracing) AND (drought OR "dry year" OR "yield stability" OR "rainfall variability")`
- [8] `("spate irrigation" OR "flood-based farming" OR "spate") AND (drought OR yield OR resilience)`
- [19] `("conservation agriculture" OR "no-till" OR "no tillage" OR mulch OR mulching) AND (meta-analysis OR "systematic review" OR "meta-regression") AND (drought OR aridity OR "dry" OR "rainfall" OR stability OR "climate stress")`
- [13] `("conservation agriculture" OR "climate-smart" OR "soil and water conservation") AND ("rainfall shock" OR "rainfall shocks" OR "weather shock" OR "downside risk" OR "production risk" OR "yield variability" OR "crop failure")`
- [5] `("soil and water conservation" OR "soil conservation" OR "water conservation") AND (drought OR "dry year" OR "rainfall variability" OR "low rainfall") AND (yield OR income OR "food security")`
- [ERR, HTTP error, not re-run] `("water harvesting" OR "rainwater harvesting" OR "in-situ" OR "zaï" OR "zai pits" OR "micro-catchment" OR "microcatchment") AND (meta-analysis OR "systematic review" OR synthesis OR review) AND (yield OR productivity)`
- [65] `("sand dam" OR "sand dams" OR "subsurface dam" OR "percolation tank" OR "farm pond" OR "check dam") AND (drought OR "dry season" OR income OR livelihood OR yield)`
- [50] (multilingual ES/FR/PT) `(zaï OR "cordons pierreux" OR "demi-lunes" OR "banquettes" OR "captación de agua" OR "cosecha de agua" OR "captação de água" OR "barraginhas" OR "cisternas" OR "terrazas" OR "labranza cero" OR "plantio direto") AND (sequía OR seca OR sécheresse OR "año seco" OR "année sèche" OR estiagem)`

### Verbatim queries — agroforestry (OpenAlex)
- [86] `(agroforestry OR agroforest OR "trees on farm" OR "farmer managed natural regeneration" OR FMNR OR parkland OR "alley cropping" OR "fertilizer trees" OR Faidherbia OR Gliricidia) AND (drought OR "dry year" OR "dry years" OR "rainfall variability" OR "yield stability" OR "El Niño" OR "climate shock" OR "climate shocks")`
- [7] `(agroforestry OR "tree-based" OR "trees on farms") AND (meta-analysis OR "systematic review") AND (yield OR resilience OR stability OR variability)`
- [28] `(silvopastoral OR silvopasture OR "silvo-pastoral") AND (drought OR "dry season" OR "heat stress" OR "thermal stress" OR "El Niño")`
- [17] `(windbreak OR windbreaks OR shelterbelt OR shelterbelts OR "hedgerow" OR hedgerows) AND (drought OR "dry year" OR "yield" ) AND (meta-analysis OR review OR stability OR drought)`
- [18] `(shade OR shaded OR agroforestry) AND (coffee OR cocoa OR cacao) AND (drought OR "El Niño" OR "heat stress" OR "dry season" OR "dry year")`
- [37] `(trees OR tree OR agroforestry OR forest OR forests) AND ("rainfall shock" OR "rainfall shocks" OR "weather shock" OR "weather shocks" OR "drought shock" OR "consumption smoothing" OR "safety net")` (also used for FR)
- [1] `(cocoa OR cacao OR coffee) AND (shade OR agroforestry OR "full sun") AND (resilien OR "extreme climate" OR drought OR "El Niño") AND (yield OR production OR mortality)`. The truncated `resilien` did not stem, so this was re-run as the next query.
- [41] `(cocoa OR cacao OR coffee) AND (shade OR agroforestry OR "full sun") AND (resilient OR resilience OR "extreme climate" OR drought OR "El Niño")`
- [ERR 429] `("legume trees" OR "fertilizer trees" OR "fertiliser trees" OR "Faidherbia albida" OR "Gliricidia sepium" OR "tree fallow" OR "improved fallow") AND (stability OR "rainfall" OR drought OR variability) AND (maize OR yield)`. Re-run after back-off as the next query.
- [33] `("legume trees" OR "fertilizer trees" OR "fertiliser trees" OR "Faidherbia albida" OR "Gliricidia" OR "improved fallow") AND (stability OR rainfall OR drought OR variability)`
- [2] `(shade OR shelter OR trees OR silvopastoral) AND (cattle OR cows OR sheep OR goats OR livestock) AND ("heat stress") AND (meta-analysis OR "systematic review" OR review)`
- [ERR 429, then re-run: 1] `(windbreak OR windbreaks OR shelterbelt OR shelterbelts) AND (crop OR yield OR yields) AND (meta-analysis OR review OR global)`
- [8] (multilingual ES/FR/PT) `(agroforestería OR agroforesteria OR agrofloresta OR agroflorestal OR agroforesterie OR silvopastoril OR sylvopastoral OR "regeneración natural" OR "régénération naturelle") AND (sequía OR seca OR sécheresse OR "El Niño" OR estiagem)`

### Verbatim queries — forest_restoration (OpenAlex)
- [5] `(reforestation OR afforestation OR "forest restoration" OR "landscape restoration" OR "natural regeneration" OR "exclosure" OR exclosures OR "area closure") AND (drought OR "dry year" OR "dry season" OR "rainfall variability" OR "climate shock" OR resilience) AND (livelihood OR livelihoods OR income OR "food security" OR household OR households)`
- [43] `("community forest" OR "community forestry" OR "community-based forest" OR "forest co-management" OR "participatory forest management" OR "joint forest management" OR "forest user groups") AND (drought OR shock OR shocks OR "rainfall" OR resilience OR "food security")`
- [51] `(mangrove OR mangroves) AND (cyclone OR typhoon OR "storm surge" OR hurricane OR flood) AND (livelihood OR livelihoods OR income OR damage OR losses OR household OR "rice yield" OR agriculture)`
- [0] `(forest OR forests OR "tree cover" OR reforestation) AND (flood OR floods OR flooding) AND (crop OR agriculture OR "agricultural losses" OR "child health" OR income) AND (developing OR "low-income" OR Africa OR Asia OR "Latin America")`
- [2] `(watershed OR catchment) AND (restoration OR reforestation OR afforestation OR "integrated watershed") AND (drought OR "dry season flow" OR "baseflow") AND (impact OR evaluation OR yield OR income)`
- [22] `(forest OR forests OR reforestation OR "tree cover" OR "natural regeneration" OR exclosure OR restoration) AND (drought OR "dry spell" OR "dry season") AND ("crop yield" OR "crop yields" OR "agricultural production" OR "food security" OR livestock OR pastoralists)`
- [11] `(mangrove OR mangroves) AND (cyclone OR typhoon OR "storm surge" OR tsunami) AND (households OR villages OR "economic activity" OR "property" OR deaths OR "storm protection")`
- [6] `("restoration" OR "regreening" OR "re-greening" OR "Great Green Wall" OR "land rehabilitation") AND (drought OR resilience) AND (Sahel OR Ethiopia OR Niger OR "Burkina Faso" OR Kenya) AND (household OR households OR livelihoods OR "food security")`

## Verbatim queries — channel 2 web search (grey / evaluation channel and targeted primaries)
These were run through a general web search engine. Result counts are not meaningful for web search, so each query lists what it yielded.
- `impact evaluation landscape restoration drought 2015 El Niño Tigray yields restored watersheds`: Constenla-Villoslada 2022 (new); Kosmowski 2018 (known)
- `farmer managed natural regeneration drought year food security households Niger evidence yields`: Abasse 2023 Tropenbos (new); Weston 2015 (known)
- `mangroves protect rice agriculture cyclone storm surge household losses Bangladesh empirical`: Akber 2018; Mahmud & Barbier 2016; WB 2025 report
- `3ie impact evaluation soil water conservation drought yields households systematic review "drought"`: nothing new and on-target. No 3ie drought-stratified SWC evaluation found.
- `IFPRI discussion paper sustainable land management drought shock household welfare Ethiopia panel stone bunds rainfall shock`: IFPRI DP 1811 (Kato et al. 2019; excluded, see below)
- `ICRAF working paper agroforestry drought year income food security households comparison non-adopters Kenya Ethiopia`: nothing new with a drought-year contrast
- `conservation agriculture 2015/16 El Niño drought southern Africa maize yields CIMMYT farmers compared conventional`: Setimela 2018
- `silvopastoral systems drought milk production cattle Colombia El Niño 2015 comparison conventional pasture` and `"El Niño" silvopastoral milk production reduction 2.2% conventional 4.9% Colombia study`: Guáqueta-Solórzano 2025 (Land)
- `zaï stone bunds yields dry year Burkina Faso Niger compared untreated fields rainfall deficit`: Kaboré & Reij 2004; Zouré 2025; Sawadogo 2011
- `agroforestry trees drought 2015 2016 Ethiopia Kenya household crop failure food security quasi-experimental trees on farm buffered`: nothing with a measured drought contrast
- `shade trees coffee yield drought year heat stress comparison sun coffee Central America Brazil 2014 drought yields shaded`: Piato 2020 meta (excluded: no hazard stratum)
- `"participatory forest management" Ethiopia shocks coping forest income drought households study`: forest-income studies (excluded, PICOS)
- `exclosures Tigray fodder drought livestock household income resilience study area closure benefits drought year`: Mezgebo 2026 (confirms the drought-stratified yield effect in the abstract)
- `community forest management households rainfall shock consumption smoothing impact evaluation Nepal India Tanzania forest income insurance`: forest-as-insurance studies (excluded, PICOS)
- `"Mangroves for Coastal Resilience in Bangladesh" World Bank Dasgupta report`: WB 2025 PDF URL
- `Kaboré Reij 2004 "The emergence and spreading of an improved traditional soil and water conservation practice in Burkina Faso" EPTD discussion paper 114 pdf`: RePEc / IFPRI URL
- OA-recovery searches, one per item, title plus "pdf". These were run for Pittelkow 2015, Kassie 2015, Setimela 2018, Thierfelder 2026, Barron & Okwach 2005, Fox & Rockström 2003, Constenla-Villoslada 2022, Sileshi 2011, Badola & Hussain 2005, Lasage 2008, Kassie 2008 and Akber 2018. Results are recorded in each candidate's `oa_note`.

## PRISMA-lite counts
| NbS | OpenAlex retrieved (Σ meta.count) | Titles screened (top ≤50 per query) | Already in queue / SRC / staging | Web-search channel queries | Included candidates | Of which syntheses | OA now | Need human RG check |
|---|---|---|---|---|---|---|---|---|
| water_harvesting_conservation | 389 | 264 | 9 | 7 (+ OA recovery) | 30 | 6 (Knapp, Pittelkow ×2, Rusinamhodzi, Tadesse SR, Kaboré & Reij programme review) | 18 | 11 |
| agroforestry | 279 | 243 | 6 | 6 (+ OA recovery) | 19 | 5 (Sileshi ×2 stability analyses, Bayala review, Solorio chapter, Blackshaw review) | 15 | 4 |
| forest_restoration | 140 | 139 | 0 | 6 (+ OA recovery) | 13 | 1 (Meaza meta) | 8 | 5 |

The "OA now" count includes grey URLs and one preprint-only item (Palsaniya). Counts for AF and FR overlap in one shared query (the trees/forests "rainfall shock" query, counted under AF).

## Findings worth knowing before extraction
- **Water harvesting is the best-evidenced lane.** It has genuine drought-year contrasts:
  - Setimela 2018: El Niño 2015/16, CA vs ploughing
  - Michler 2019 and Arslan 2015: CA × rainfall-shock panels
  - Kassie 2008: stone bunds pay only in low-rainfall areas
  - Fox & Rockström 2003 and Barron & Okwach 2005: dry-spell supplemental irrigation from ponds
  - Kaboré & Reij 2004: zaï yields in dry years
  
  It also has stability/aridity syntheses: Knapp 2018, Pittelkow 2015 ×2 and Rusinamhodzi 2011. Note that Pittelkow 2015 (Nature) states that CA "significantly increases rainfed crop productivity in dry climates". This is an aridity-class contrast, not a drought-year one.
- **Agroforestry has counter-evidence that must not be lost.** Abdulai et al. 2018 (GCB) found cocoa agroforestry *less* resilient than full-sun cocoa in the 2015-16 drought (there is a Norgrove comment and reply). Mensah 2023 is a factorial shade × drought experiment. Morel 2024 covers coffee agroforestry yields during a climate shock. Sileshi 2011/2012 provides fertilizer-tree yield-stability analyses.
- **Silvopastoral drought evidence is thin.** The only measured-looking El Niño milk contrast (2.2% vs 4.9% loss) is in Guáqueta-Solórzano 2025 and looks like a secondary citation, so it must be traced to its primary before any unit is emitted. Heat-stress evidence (Blackshaw 1994) includes artificial shade, so tree shade must be separated (PICOS).
- **Windbreaks / linear boundary:** no new LMIC drought-year evidence was found. Hao 2026 (meta) is already queued. This is a gap.
- **Forest restoration drought evidence is genuinely scarce.**
  - The only direct drought-stratified crop-yield contrast is Mezgebo et al. 2026 (exclosures, Tigray). Its abstract says the yield difference is "more pronounced… during drought conditions".
  - Kimwanga 2026 (Malawi co-management × rainfall shocks) is the only CBFM item.
  - Constenla-Villoslada 2022 is the strongest causal design, but it is a bundled SLM programme (SWC plus area closures), so attribution between WH and FR is shared.
  - The rest of the FR list is **cyclone/flood-year** mangrove evidence, the secondary target: Das & Vincent 2009, Das 2011, Badola & Hussain 2005, Akber 2018, Mahmud & Barbier 2016, Hochard 2019, del Valle 2020 and the WB 2025 report. This complements the round-1 physical-protection syntheses (Menéndez 2020, McIvor 2012, which are already queued) with household-loss outcomes.
- **Web-summary figures are not evidence.** The FMNR claim that adopters are "up to 5-fold better off in drought years" appeared in web summaries. It is attributed to the Abasse 2023 review only as a lead and must be traced to a primary before use.
- **Relevance notes are leads only.** The relevance notes and tier rationales describe expected content from titles, abstracts and known study designs. They are not evidence and must not be transcribed into EV. Extraction still goes through the cached PDF.

## Exclusions (with reasons)
- **Off-topic hits from shared vocabulary.**
  - "TILLING" gene-mutant papers and "till 2100" climate projections matched `no-till`/`tillage` title stems.
  - "seca" matched "matéria seca" / "massa seca" (dry matter) and pulled about 40 irrelevant PT/ES no-till agronomy titles.
  - Urban and domestic rainwater harvesting, and Brazilian rooftop *cisternas* (the rooftop family is parked as qualitative_only).
  - Check-dam sediment-yield papers.
  - Lesson for the protocol: qualify `seca` (e.g. `"año seco"`, `"ano seco"`, `estiagem`) and exclude `"matéria seca"` / `"materia seca"`.
- **PICOS: practice not the intervention.** Studies of forest *access or cover* as natural insurance are excluded: World Dev 2023 Malawi weather shock; JDS 2023 forests as natural insurance; Noack-type PEN forest-income studies; Ethiopian PFM forest-income dependence studies; the "dry forest income" drought-coping study. Forest cover ≠ protection/CBFM practice. Kimwanga 2026 was kept because co-management *is* the practice.
- **No hazard stratum.**
  - Piato 2020 (robusta shade meta): yield and quality only.
  - European agroforestry yield meta (Frontiers 2021) and global maize-agroforestry meta (2023): not hazard-stratified, and the latter may already be covered by Dobhal.
  - IFPRI DP 1811 (Kato et al. 2019, SLM water security & poverty): no drought contrast.
  - Ethiopian PSM SWC–food-security preprint (SSRN): no drought contrast.
- **Wrong NbS or non-NbS comparator.** Drought-tolerant maize-only studies, irrigation-method drought studies (China) and the RESTORE livestock-services project (CGSpace, "restoration" of veterinary services).
- **Ecophysiology without a production comparator.** Examples: experimental drought on cacao soil CO2 (Sulawesi), seedling drought physiology (Faidherbia, Gliricidia), shelterbelt tree transpiration (China).
- **Not resolvable or too weak.**
  - "Resilience of the Hani Rice Terraces System to extreme drought" (2013): no DOI, venue unknown, UMIC paddy.
  - "Does Participatory Forest Management Increase Forest Resource Use to Cope with Shocks? Ethiopia" (RePEc): could not be resolved to a verifiable record. Crossref's best match was a different paper (Kahsay 2021).
  - "Drought Resistance of Maize in Gliricidia-Based Cropping Systems" (CGSpace / Harvard Dataverse 2020–21): dataset or record, a PAUSED format.
- **Dataset sources (PAUSED format).** Harvard Dataverse replication data for Sileshi 2011/2012 and Constenla-Villoslada 2022. These are noted in `oa_note` only.

## Needs a human
1. **ResearchGate / author-copy check** for 20 flags marked `rg_flag_for_human`, covering 19 unique sources (Constenla appears in both the WH and FR files). Use institutional access only after this check. The highest-value ones are:
   - Setimela 2018
   - Constenla-Villoslada 2022
   - Kassie 2008 and Kassie 2015
   - Sileshi 2011 and Sileshi 2012
   - Badola & Hussain 2005
   - Barron & Okwach 2005 and Fox & Rockström 2003. Thesis-appended manuscript versions exist on DiVA; a human must decide whether a thesis version is acceptable.
2. **Version decisions.**
   - Palsaniya 2023: the Research Square preprint is OA; the AFS version is closed.
   - Das 2011: a SANDEE working-paper predecessor is on Academia.
   - Kassie 2008: an EfD discussion-paper version exists.
3. **Internal authorship.** Boillat et al. 2019 (ERL) is co-authored by P. Steward. Record this for the independence axis.
4. **Provenance traces before any unit is emitted:**
   - the silvopastoral El Niño milk figures (Guáqueta-Solórzano 2025)
   - the FMNR "5-fold in drought years" claim (Abasse 2023)
5. **Julius 2019 (FTL):** the Crossref author names look mis-parsed. Verify the authors at acquisition. The DOI and title round-trip is fine.
6. **Run `verify_metadata.py verify` after registration** as usual. All DOIs here were round-tripped by this agent, but the central gate is authoritative.
