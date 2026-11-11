# mangrove_grey_tool — T3/T6 gap round, 2026-11-10

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `mangrove_t3t6_gaps_20261110_grey_tool`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-10: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `mangrove_t3t6_gaps_20261110_grey_tool`, ledger per `--ledger`.


Lane `mangrove_grey_tool`; NbS `mangrove_restoration`, family `mangrove_restoration__tidal_coastal`; tables T3 + T6; processes `grey` + `tool`. Discovery ruleset v1.8.1. Builds on `mangrove_five_refs_20261030` and `mangrove_tool_followup_20261029` (not repeated: Losada, Spalding, Hutchison, McIvor, GMW code, Deltares, FORMAN).

## Counts (unique records inspected, not engine hits)
| table | process | retrieved | screened | included |
|---|---|---|---|---|
| T3 | grey | 58 | 58 | 11 |
| T6 | grey | 58 | 58 | 12 |
| T3 | tool | 15 | 15 | 1 |
| T6 | tool | 15 | 15 | 3 |

17 candidates (14 grey incl. 3 reuse, 3 tool). Reuse: `wocat_578_2016`, `wocat_4300_2019`, `wocat_1442_2011` (registered T4-only; WOCAT §6 impacts + cost tables feed T3/T6).

## Channels used
Web search (EN, FR, ES, PT); World Bank Documents API (`search.worldbank.org/api/v3/wds`); GCF, GEF-IEO, IISD, IPCC, SEAFDEC, RePEc landing pages; GitHub API (natcap/invest @ f02f5e20d2d3, natcap/invest.users-guide @ 56d86f253218); Zenodo API; Crossref for DOI round-trip.
Two publisher PDFs were read via fetch text (IISD SAVi Annex B; IPCC WS Ch4 tables) for tool-parameter inspection only — nothing cached in `.cache/corpus` or the library.

## Omitted / blocked
- Lens (no token), AGRIS (manual lane), OpenAlex (not needed for grey/tool; literature lane covers it).
- Blocked, not bypassed: preventionweb (403), FAO OKR EX-ACT guidelines (403), UFSC repository (security challenge), nature.com (auth redirect), qcat.wocat.net search (login).
- No ADB PCR located (Sindh press account only); no IFAD/TNC mangrove MEL with outcome data surfaced.

## Tool inspection
- **IISD SAVi Casamance (2026, preliminary)** — Annex B hardcodes: reforestation 350 000 CFA/ha; maintenance 20 000 CFA/ha/yr; sequestration 14.6 tCO2/ha/yr young, 33 mature; low-efficacy flood-damage reduction 2.5%; fisheries 5 707 210 kg/yr x 1 325 CFA/kg. Model assumptions → expert_assertion.
- **IPCC 2013 Wetlands Supplement Ch4** — Table 4.4 AGB growth mangroves (t d.m./ha/yr: trop. wet 9.9, trop. dry 3.3, subtropical 18.1), Table 4.5 R, Table 4.12 EF_RE mangrove ≈1.62 t C/ha/yr removal at re-establishment.
- **InVEST Coastal Blue Carbon** — code hardcodes no mangrove rate (accumulation = user CSV); UG Table 1 (`coastal_blue_carbon.rst` L322-339) has mangrove disturbance-loss defaults (biomass half-life 15 yr, 75% immediate release; soil loss 30/50/66%; CH4 0.4 t CO2/ha/yr). Existing-habitat comparator, low tier.
- Excluded: InVEST Coastal Vulnerability (rank + protection distance user inputs; UG says model does not quantify habitat role); SWAN-CWV (existing-vegetation physics); GMW code (already inspected); MOW coastal protection (= Losada/Menéndez, already queued).
- Held: Worthington et al. 2024 restoration-potential dataset (Zenodo 10.5281/zenodo.11283186 — fisheries uplift for 37 species + 40-yr carbon; R scripts inside 1.16 GB zip, not inspected); FAO EX-ACT coastal (403); Verra VM0033 and CDM AR-AM0014 (default tables not confirmed).

## Screening notes
- PICOS: every include names mangrove planting/rehabilitation/restoration. `comparator: existing_habitat` flagged on Beck & Lange 2016, WB Philippines 2017, SOWM 2024, InVEST CBC.
- Negative/mixed evidence deliberately kept (WB ICR6719 Unsatisfactory; Aceh lessons; Primavera 10-20% survival) to counter grey positive bias.
- DOI: only 10.1596/37605, 10.1596/23775, 10.1596/27666 emitted, each Crossref title-matched; all others blank (title-only).
- Holds (identity or content unverified): BwN Demak final report, WeForest MANCO survival study, Muniz 2024 crab thesis, Rovai Brazil review, MFF small-grant reports, GEF 3821/4083 TEs, SNV MAM / IKI 2022 evaluation, PTFCF/ZSL training manual, Thi Nai CBA, ADB Sindh PCR. Details in screening.json.

## Gap coverage
- food_insecurity (fisheries): SOWM 2024, SAVi, WB Indonesia economics, WOCAT 1442; Worthington dataset held.
- water_quality_risk: no grey/tool source found with restoration-attributable water-quality outcomes (silvofishery effluent studies are primary literature → literature lane).
- production_gap: weak — Demak AMA and MAM organic-shrimp evaluations both held (final reports not located).
- flood livelihood protection: FP013, Beck & Lange, WB Philippines, WOCAT 578/4300.
- asset threats: WB ICR6719, Wibisono 2006, Wibisono & Sualia 2008, Primavera 2014, WOCAT.
- costs per ha: SAVi, Ferrer 2011 EEPSEA, WB Indonesia, ICR6719, WOCAT.

## Stop reason
Bounded cap reached on grey (11-12 per table) and tool lane exhausted its named targets. New queries were mostly returning press, programme pages and already-registered reports. That is near-saturation for openly reachable grey sources, not full saturation: holds, blocked repositories and the unread Worthington scripts are still open.

## Next actions
Verify titles at acquisition; open FP013 and ICR6719 results tables; chase the BwN Demak final report, the WeForest survival study and the IKI MAM evaluation (production_gap); run a code-intake step on the Worthington Zenodo scripts; inspect the VM0033 v2.1 default tables.

## Verbatim queries
#### grey
- `Mangroves for Coastal Resilience M4CR Indonesia World Bank implementation status results mangrove rehabilitation hectares survival`
- `GEF terminal evaluation mangrove restoration project livelihoods fisheries survival rate report`
- `Building with Nature Demak final report Wetlands International mangrove restoration outcomes aquaculture income`
- `Mangrove Capital Africa results report Wetlands International mangrove restoration livelihoods`
- `Vietnam coastal resources for sustainable development project ICR mangrove World Bank implementation completion report`
- `State of the World's Mangroves 2024 Global Mangrove Alliance restoration fisheries benefits`
- `GCF FP013 Vietnam coastal resilience mangrove terminal evaluation UNDP mangrove survival rate`
- `Mangroves for the Future IUCN final evaluation report mangrove restoration livelihood outcomes`
- `Forest Sector Modernization and Coastal Resilience Enhancement Project Vietnam implementation completion report mangrove planted survival`
- `Mikoko Pamoja Plan Vivo annual report mangrove planting community benefits survival`
- `mangrove restoration project evaluation cost per hectare grey literature World Bank "cost per hectare" mangrove planting Asia evaluation report`
- `Coastal Wetlands Protection and Development Project Vietnam implementation completion report mangrove Mekong`
- `"Forest Sector Modernization and Coastal Resilience Enhancement" "Implementation Completion and Results Report" ICR6719`
- `EEPSEA fishpond reversion mangrove Philippines cost natural regeneration active planting research report`
- `WOCAT mangrove planting technology database site:wocat.net mangrove`
- `Blue Ventures mangrove restoration Madagascar Tahiry Honko evaluation fisheries mud crab income report`
- `FAO mangrove rehabilitation evaluation report tsunami Aceh mangrove replanting survival lessons learned`
- `ADB evaluation mangrove rehabilitation coastal project completion report mangrove survival planted hectares`
- `Wibisono Suryadiputra 2006 "Study of lessons learned from mangrove/coastal ecosystem restoration efforts in Aceh since the tsunami" Wetlands International pdf`
- `évaluation finale projet restauration mangrove Sénégal Guinée reboisement taux de survie rapport`
- `evaluación final proyecto restauración de manglares informe pesca medios de vida sobrevivencia`
- `relatório avaliação restauração de manguezal projeto resultados pesca caranguejo sobrevivência mudas`
- `Mangroves and Markets MAM project SNV IUCN Ca Mau final evaluation organic shrimp mangrove income results report`
- `Beck Lange 2016 "Managing Coasts with Natural Solutions" World Bank WAVES guidelines mangroves coral reefs`
- `mangrove restoration water quality improvement shrimp pond effluent nutrient removal project report silvofishery evaluation FAO`
- `Green Coast project assessment of lessons learnt Wetlands International 2008 Aceh Nias mangrove rehabilitation survival livelihoods`
- `qcat.wocat.net mangrove technology rehabilitation planting Rhizophora Avicennia SLM`
- `WB Documents API qterm: Forest Sector Modernization and Coastal Resilience Enhancement | Economics of Large-scale Mangrove | P157127 Implementation Completion | ICR6719 | Mangroves for Coastal Resilience Implementation Status | mangrove Implementation Completion and Results Report`
#### tool
- `gh api repos/natcap/invest (commit f02f5e20d2d3) code search 'mangrove'; tree grep coastal_vulnerability|blue_carbon`
- `gh api repos/natcap/invest.users-guide (commit 56d86f253218) source/en/coastal_blue_carbon.rst, coastal_vulnerability.rst`
- `zu Ermgassen mangrove fisheries enhancement global model fish density per hectare juvenile fish invertebrates 2020`
- `Global Mangrove Watch restoration potential benefits fisheries carbon "restoration" widget methodology github globalmangrovewatch`
- `FAO EX-ACT coastal wetlands mangrove module default emission factors restoration tCO2 per hectare guidelines`
- `CDM AR-AM0014 afforestation reforestation degraded mangrove habitats methodology default parameters`
- `2013 Supplement to the 2006 IPCC Guidelines Wetlands Chapter 4 Coastal Wetlands Table 4.5 annual aboveground biomass growth mangroves default`
- `Verra VM0033 tidal wetland seagrass restoration methodology default values mangrove biomass carbon accumulation rate`
- `mangrove wave attenuation model tool coastal protection calculator per metre mangrove width parameter open source`
- `Zenodo API records/11283186 (Worthington et al. restoration potential dataset) file listing`
- `IISD SAVi Casamance report (surfaced by FR grey query) — Annex B parameter scan`
