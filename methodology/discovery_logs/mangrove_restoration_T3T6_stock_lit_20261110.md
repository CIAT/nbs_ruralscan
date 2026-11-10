# mangrove_lit — T3/T6 gap discovery (stock + updated_lit), 2026-11-10

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `mangrove_t3t6_lit_20261110_lit`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-10: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `mangrove_t3t6_lit_20261110_lit`, ledger per `--ledger`.


NbS `mangrove_restoration` (family `mangrove_restoration__tidal_coastal`; generic search, `families: []`). Tables T3, T6 (+T6E costs). Discovery ruleset v1.8.1. Staging only; no PDFs downloaded; no git; no registers touched.

## Counts

| table | process | retrieved | screened | included |
|---|---|---|---|---|
| T3 | updated_lit | 368 | 368 | 20 |
| T6 | updated_lit | 519 | 519 | 21 |
| T3 | stock | 130 | 130 | 17 |
| T6 | stock | 130 | 130 | 10 |

Unique candidates: 60 (22 stock incl. 5 reuse of held sources; 38 updated_lit). OpenAlex: 667 unique records inspected across 25 queries (overlapping per-table pools: T3 368, T6 519). Stock: 130 local rows inspected (cited_originals 58 regex hits, SRC 69 coastal/mangrove rows, queue 3 mangrove-family rows under forest_restoration); stock counts are one shared pool reported against both tables.

## Verbatim queries

Channel: `https://api.openalex.org/works?filter=<filter>&sort=relevance_score:desc&per-page=<n>&mailto=p.steward@cgiar.org`, run 2026-11-10. First page only.

- `t3_wave` (count=138, inspected=25): `title.search:mangrove (wave OR waves) (attenuation OR dissipation OR reduction),publication_year:>2004`
- `t3_surge` (count=168, inspected=30): `title.search:mangrove ("storm surge" OR surge OR flood OR flooding OR "coastal protection" OR "coastal defence" OR "coastal defense"),type:review|article,publication_year:>2009`
- `t3_cyclone_liv` (count=49, inspected=30): `title.search:mangrove (cyclone OR hurricane OR typhoon OR tsunami) (household OR livelihood OR agriculture OR damage OR loss OR income OR mortality),publication_year:>2004`
- `t3_asset_storm` (count=63, inspected=30): `title.search:mangrove (cyclone OR hurricane OR typhoon OR storm) (damage OR mortality OR recovery OR resilience),publication_year:>2009`
- `t3_asset_survival` (count=59, inspected=40): `title.search:mangrove (restoration OR rehabilitation OR planting OR reforestation OR afforestation) (success OR failure OR survival OR outcomes OR lessons),publication_year:>2004`
- `t3_asset_dieback` (count=123, inspected=30): `title.search:mangrove (dieback OR "die-off" OR hypersalinity OR drought OR heatwave OR "sea level" OR burial OR sedimentation) (mortality OR dieback OR vulnerability OR response),publication_year:>2009`
- `t6_fish` (count=132, inspected=40): `title.search:mangrove (fisheries OR fishery OR fish OR crab OR shrimp OR catch) (restoration OR restored OR rehabilitation OR planted OR enhancement OR nursery),publication_year:>2004`
- `t6_silvo` (count=346, inspected=40): `title.search:(silvofishery OR silvofisheries OR "silvo-fishery" OR "integrated mangrove" OR "mangrove-shrimp" OR "mangrove shrimp" OR "mangrove aquaculture" OR "associated mangrove aquaculture"),publication_year:>2004`
- `t6_liv` (count=227, inspected=40): `title.search:mangrove (restoration OR rehabilitation OR reforestation OR planting) (livelihood OR livelihoods OR community OR income OR poverty OR "food security" OR wellbeing OR socioeconomic),publication_year:>2009`
- `t6_carbon` (count=282, inspected=40): `title.search:(restored OR restoration OR planted OR rehabilitated OR reforested) mangrove (carbon OR "blue carbon" OR sequestration OR accumulation OR burial),publication_year:>2009`
- `t6_wq` (count=1109, inspected=30): `title.search:mangrove ("water quality" OR nutrient OR nitrogen OR phosphorus OR effluent OR wastewater OR filtration OR pollutant),publication_year:>2004`
- `t6_salinity` (count=24, inspected=24): `title.search:mangrove (salinity OR saltwater OR "salt water" OR "sea level rise") (intrusion OR agriculture OR crop OR rice OR farm OR groundwater),publication_year:>2004`
- `t6e_cost` (count=146, inspected=40): `title.search:(mangrove OR "coastal restoration" OR "marine coastal restoration") (cost OR costs OR "cost-benefit" OR "cost benefit" OR feasibility OR economics),publication_year:>2009`
- `es_manglar` (count=74, inspected=30): `title.search:(manglar OR manglares) (restauracion OR restauración OR rehabilitacion OR reforestacion OR reforestación OR pesquerias OR pesca OR medios),publication_year:>2004`
- `pt_mangue` (count=128, inspected=30): `title.search:(manguezal OR manguezais OR mangue) (restauração OR recuperação OR reflorestamento OR pesca OR caranguejo),publication_year:>2004`
- `fr_mangrove` (count=508, inspected=30): `title.search:mangrove (restauration OR reboisement OR réhabilitation OR pêche OR riziculture OR "moyens d'existence" OR reforestation),publication_year:>2004`
- `rev_restor` (count=153, inspected=40): `title.search:mangrove (restoration OR rehabilitation OR reforestation OR planting OR afforestation) (review OR "meta-analysis" OR synthesis OR global OR "systematic"),publication_year:>1999`
- `why_fail` (count=4, inspected=4): `title.search:mangrove restoration (fails OR fail OR failure OR "field of dreams" OR "do we know enough" OR "not working" OR pitfalls OR mistakes),publication_year:>1999`
- `mg_agri` (count=20, inspected=20): `title.search:mangrove (rice OR crop OR crops OR agriculture OR agricultural OR farmland OR farm OR farmers) (cyclone OR storm OR flood OR salinity OR protection OR yield OR loss),publication_year:>2004`
- `mg_ecosystem_services_restored` (count=56, inspected=30): `title.search:(restored OR rehabilitated OR planted OR replanted) mangrove ("ecosystem services" OR benefits OR biodiversity OR value OR valuation),publication_year:>2004`
- `mg_shoreline` (count=107, inspected=25): `title.search:mangrove (shoreline OR erosion OR accretion OR sediment) (restoration OR rehabilitation OR "building with nature" OR permeable OR planting),publication_year:>2009`
- `mg_aquaculture_pond_restor` (count=38, inspected=20): `title.search:mangrove (abandoned OR disused) (pond OR ponds OR aquaculture OR shrimp),publication_year:>2004`
- `mg_hydro_restor` (count=12, inspected=12): `title.search:mangrove ("hydrological restoration" OR "hydrologic restoration" OR "ecological mangrove restoration" OR "community based ecological"),publication_year:>2004`
- `mg_temp_heat` (count=31, inspected=15): `title.search:mangrove (temperature OR cooling OR microclimate OR heat) (coastal OR community OR land OR surface),publication_year:>2009`
- `mg_wellbeing` (count=173, inspected=25): `title.search:mangrove ("human wellbeing" OR "human well-being" OR poverty OR "food security" OR nutrition OR "protein") ,publication_year:>2004`

Note: the first run of `fr_mangrove` used a wildcard (`rizicul*`) and returned an API error (0 records); it was re-run without the wildcard (listed above).

Stock reconciliation (no engine): regex `mangrove|manglar|mangue|silvofish|shrimp|blue carbon|coastal|tidal|storm surge|wave` over `pipeline/cited_originals.csv` (reference_text+cited_as or nbs_ids∋mangrove_restoration); regex `fish|aquacult|salin|estuar|delta|blue|coast|sea level|cyclone|hurricane` over SRC citations NOT tagged mangrove; queue rows with family containing `mangrove` under another nbs_id.

## Key stock findings

- `forest_restoration__mangrove_coastal` family still exists in the queue: `didy_2026_mangroves_sainte_marie_reboisement_vs_rna` (pending, mangrove restoration Madagascar, FR) and `mahmud_barbier_2016_defensive_expenditure_bangladesh` (status `extracted`, 0 FR units, explicit note 'pointer for a mangrove lane pp.15-17, Tables A5-A6'). **Mahmud has no SRC row and no EV units** although the queue says extracted — reconcile centrally. Both proposed as reuse for mangrove.
- `rowland_2026` (cyclone impacts on coastal agriculture with coastal-wetland buffering) is held under wetland_management only — it targets exactly the suspicious **flood livelihood = low** mangrove row; reuse proposed (verify mangrove share).
- `cahoon_2006`, `wet_china_coastal_restoration_effectiveness_meta_2024` reusable for mangrove asset_threat / T6.
- 16 cited originals (mostly from gijsman_2021, mcivor_2012, hernandez_melchor_2017) promoted to candidates: wave/surge primaries (Zhang 2012, Horstman 2014, Mazda 1997/2006, Montgomery 2018, Dasgupta), restoration economics (Walton 2006, Adger 1997, Fernández 2007), Bayraktarov 2016 costs (was citation_only), cyclone asset-threat primaries (Radabaugh, Imbert, Macamo, Asbridge), McIvor 2013 NCP report 3, Rodríguez-Rodríguez 2021, Arifanti 2022. `tri_1998`/`quartel_2007` already queued.
- `wb_2022_economics_mangrove_indonesia_technical` already queued for mangrove — updated_lit hit marked duplicate.

## Cell coverage of included candidates

- **T3 flood / wind_cyclone livelihood_mitigation** (row now LOW — likely under-evidenced): Tiggeloven 2026 (restoration, PNAS), Blankespoor 2017, Dasgupta 2019, Zhang 2012, Horstman 2014, Mazda 1997 (planted)/2006, Montgomery 2018 (when attenuation fails), Das & Crépin 2013, Duncan 2014 (rice cropland), Mahmud & Barbier 2016, Rowland 2026. Most are `comparator: existing_habitat` — route accordingly; Tiggeloven and Mazda 1997 are the restoration-explicit ones.
- **T3 asset_threat**: wind_cyclone (Takagi 2023 planted survival, Baring 2024 planted vs natural, Gao 2025 NbS-framed, Krauss 2023, Radabaugh, Imbert, Macamo, Asbridge); flood/waterlogging (Lagomasino 2021 ponding); drought/hypersalinity (Lovelock 2017, Duke 2017); sedimentation/SLR (Woodroffe 2016, McIvor 2013, Cahoon 2006); restoration failure syntheses (Bayraktarov 2016 survival, Primavera 2008, Ellison 2000/2020, Gerona-Daga 2022 SR, Wodehouse 2019, Barnuevo 2017, Rodríguez-Rodríguez 2021, van Bijsterveldt 2020, Didy 2026).
- **T6 food_insecurity**: Carrasquilla-Henao 2017 meta (existing), Das 2017 (planted mangroves → catch), Debrot 2022 (NbS rehab project fisheries), Walton 2006, Duncan 2016, McSherry 2023.
- **T6 production_gap** (shrimp/fish yields next to mangroves): McSherry 2023 review, Lai 2022 (trade-off risk), Nguyen 2022, Bosma 2020 AMA (grey, COI discount).
- **T6 water_quality_risk**: Uddin 2024 review (restoration & trace metals), Nam 2025 (mangrove age in IMS ponds). Thin — Marins 2020 held.
- **T6 water_stress / T3 drought (salinity intrusion)**: Nguyen 2020 only — weak; no restoration study on salinity protection of farm water found in title search.
- **T6 carbon**: Song 2023 meta (restoration-specific), Arifanti 2022, Duncan 2016. **T6E costs**: Goto 2025 (global implementation costs), Bayraktarov 2016, Beck 2022 ROI, van Zanten 2025, Tiggeloven 2026, Fernández 2007, Winterwerp 2020. **T6 rural_poverty**: Sathiyamoorthy 2024, Cormier-Salem 2016 (equity/maladaptation), Prayunita 2026 review, Walton 2006, Adger 1997, Nguyen 2022.
- **heat_stress**: no effect evidence found (titles are urban LST/mapping) — zero-yield, stated not imputed.

## Screening and exclusions

Funnel: frame → source type → practice/system relevance → six-axis credibility (proposed tiers in candidates.json) → cap. Excluded (572): physiology/biochemistry, bioprospecting/medicinal, microbial, mapping/remote-sensing methods without effect outcome, lab hydraulics, ecotourism, crab ethnography, urban LST. 31 holds (cap-reserve, protocol-only, low-authority venues, T4-only content) are in screening.json with reasons; 26 duplicates of SRC/queue/stock. DOI: every included DOI round-tripped against Crossref (title similarity ≥0.86; Arifanti DOI corrected from the cited text 'Forests 13 695' to 10.3390/f13050695 after the first form 404'd). 5 candidates have no DOI (Adger 1997, Fernández 2007, McIvor 2013, Duncan 2014, Bosma 2020) — title is the trust anchor; Duncan 2014 host volume unconfirmed.

Independence flags: Das & Crépin 2013 / Das & Vincent 2009 / Das 2011 share the Odisha 1999 super-cyclone; Beck 2022 / Menéndez 2020 / Torres-Ortega 2019 / Losada 2018 share the IHCantabria model lineage; van Zanten 2025 ↔ World Bank 2022 (queued); Debrot 2022 ↔ Bosma 2020 (Building with Nature Indonesia; implementing-partner COI).

## Channels omitted
- Lens.org (no LENS_TOKEN). AGRIS (manual browser lane). Grey/MEL and tool channels belong to other lanes (`mangrove_grey_tool`). Google Scholar/WoS/Scopus skipped by protocol. Unpaywall/OA recovery not run (discovery only).

## Stop reason
Cap reached (≈20 updated_lit per table; reserves held), not saturation. Remaining gaps: salinity-intrusion / farm-water protection by restored mangroves (water_stress), heat_stress (none), water_quality restoration effects (thin), restoration-specific (not existing-habitat) flood-livelihood evidence.

## Next actions
1. Central: register via `scripts/register-discovery.py` with separate stock / updated_lit protocols and `--reuse-log`; resolve Mahmud queue/SRC inconsistency. 2. OA recovery for paywalled candidates. 3. Targeted follow-up on water_stress (mangrove + salinity + rice/aquaculture, Mekong/Bangladesh/West Africa grey) and restored-vs-intact flood protection.
