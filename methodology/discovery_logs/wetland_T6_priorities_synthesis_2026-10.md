# Wetland management × T6 discovery: `updated_lit`, synthesis-first, English (2026-10-14)

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `wet_t3t6_2026-10-14_lit_t6`, ruleset **v1.6.10**, synthesis-first rule (Pete 2026-10-01). Registered by `scripts/register-discovery.py` on 2026-10-14: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `wet_t3t6_2026-10-14_lit_t6`, ledger per `--ledger`.


> **Run** `wet_t6_lit_2026-10-14` · ruleset **v1.6.10** · process `updated_lit` · language `en` · `nbs_id=wetland_management`.
> **Staging only.** Nothing was registered, queued or ledger-stamped. No `git` command was run. No PDF, snapshot or dataset was downloaded — every field below comes from the OpenAlex record itself.

## Scope

What wetland restoration, rewetting, creation, peatland rewetting, constructed wetlands and coastal marsh restoration **do to the T5 priorities** — water quality and nutrient removal, biodiversity, carbon, rural poverty and household income, production, equity and inclusion — plus the **economics** (cost per hectare, benefit–cost, labour) and **adoption / dis-adoption**.

This is the generic parent search (`suitability_family_id=""`); every candidate is tagged with the FAM families it speaks to. The five wetland families are `wetland_management__restoration_rewetting`, `__creation`, `__peatland`, `__constructed`, `__coastal`. **`__constructed` is `spatial_product_type = qualitative_only`**, so the four candidates tagged to it are parked out of the generated T3/T6 by `synthesise-t3t6.py` and serve the register and Module 6 instead — flagged `qualitative_only_family` so nobody is surprised later.

**Targeting (Pete's standing rule, 2026-10-01):** syntheses first — meta-analyses, systematic reviews, evidence gap maps, quantitative syntheses. **39 of 51** candidates are syntheses. The **11 primaries** were admitted deliberately and each carries the `primary_admitted` flag with the reason stated in its note; they cluster where no synthesis exists at all (measured household outcomes, tropical rewetting adoption, paludiculture cost structures, a measured methane reversal).

**Three weighted gaps**, per the brief:

| gap | what was asked | what this round returns |
|---|---|---|
| tropical / LMIC evidence | our wetland table is almost all temperate, high-income | **36 of 51** candidates cover low or lower-middle income contexts; **19** are LMIC-*focused* (not a global pool that happens to include some), **15** carry the `tropical` flag |
| greenhouse-gas balance with a methane term | some carbon rows have no CH₄ term | **9** candidates report CO₂ and CH₄ together (`full_ghg_balance`), including one meta-analysis dedicated to the methane response alone (`methane_specific`) |
| measured household outcomes | our poverty row rests on a forward reference | **4** candidates measure household income or food security directly; plus paludiculture economics (5) and restoration economics (4) |

## Channel

OpenAlex `/works`, `title_and_abstract.search`, `mailto=p.steward@cgiar.org`, `User-Agent: nbs-ruralscan/1.0`. Retry-with-backoff on 429/503 (six attempts, 5·n-second waits) — **no 429 was hit in this run**. Lens.org and AGRIS were not used: this is the English peer-reviewed lane only; the multilingual, grey/MEL and tool lanes are separate runs.

## Verbatim queries

Each string below is the **exact `filter=` value sent**, copied from the run script (`runall.py`), not a paraphrase. All 15 were re-executed in a single scripted pass so the counts reconcile.

**Q1 — exploratory: wetland/peatland restoration x livelihoods (broad, citation-sorted)**

```
title_and_abstract.search:(wetland OR peatland OR "peat swamp") AND (restoration OR rewetting OR "re-wetting" OR conservation) AND (livelihood OR livelihoods OR "household income" OR poverty OR "food security")
```

`sort=cited_by_count:desc` · `per-page=40` · `mailto=p.steward@cgiar.org` — **total 2003**, retrieved 40.

**Q2 — poverty / household income / food security (tightened)**

```
title_and_abstract.search:(wetland OR peatland OR "peat swamp") AND (restoration OR rewetting OR "re-wetting") AND ("household income" OR livelihood OR poverty OR "food security"),type:review|article
```

`sort=relevance_score:desc` · `per-page=30` · `mailto=p.steward@cgiar.org` — **total 454**, retrieved 30.

**Q3 — paludiculture economics / production**

```
title_and_abstract.search:paludiculture AND (economic OR profitability OR income OR "business model" OR cost OR yield)
```

`sort=relevance_score:desc` · `per-page=30` · `mailto=p.steward@cgiar.org` — **total 173**, retrieved 30.

**Q4 — rewetting greenhouse-gas balance incl. methane**

```
title_and_abstract.search:(peatland OR peat OR wetland) AND (rewetting OR rewetted OR "water table") AND ("greenhouse gas" OR "GHG balance" OR "radiative forcing") AND (methane OR CH4) AND ("meta-analysis" OR synthesis OR review OR global)
```

`sort=relevance_score:desc` · `per-page=30` · `mailto=p.steward@cgiar.org` — **total 288**, retrieved 30.

**Q5 — nutrient / nitrogen / phosphorus removal syntheses**

```
title_and_abstract.search:(wetland OR wetlands) AND (nitrogen OR phosphorus OR nutrient OR nitrate) AND (removal OR retention OR "removal efficiency") AND ("meta-analysis" OR "systematic review" OR "quantitative review" OR synthesis)
```

`sort=relevance_score:desc` · `per-page=30` · `mailto=p.steward@cgiar.org` — **total 199**, retrieved 30.

**Q6 — biodiversity / ecological recovery syntheses**

```
title_and_abstract.search:(wetland OR peatland OR marsh OR "salt marsh") AND (restoration OR restored OR rewetting OR creation) AND (biodiversity OR "species richness" OR "ecological recovery") AND ("meta-analysis" OR "systematic review" OR "evidence synthesis" OR "global review")
```

`sort=relevance_score:desc` · `per-page=30` · `mailto=p.steward@cgiar.org` — **total 105**, retrieved 30.

**Q7 — restoration economics: cost-benefit, cost per hectare, valuation**

```
title_and_abstract.search:(wetland OR peatland OR "salt marsh" OR mangrove) AND (restoration OR rewetting OR creation) AND ("cost-benefit" OR "benefit-cost" OR "cost effectiveness" OR "restoration cost" OR "cost per hectare" OR "economic valuation" OR "return on investment")
```

`sort=relevance_score:desc` · `per-page=35` · `mailto=p.steward@cgiar.org` — **total 441**, retrieved 35.

**Q8 — adoption / dis-adoption: farmer willingness, barriers, incentives**

```
title_and_abstract.search:(wetland OR peatland) AND (restoration OR rewetting OR "water table management") AND (farmer OR farmers OR landowner OR smallholder) AND (adoption OR willingness OR barriers OR acceptance OR participation OR incentive)
```

`sort=relevance_score:desc` · `per-page=35` · `mailto=p.steward@cgiar.org` — **total 235**, retrieved 35.

**Q9 — LMIC gap-fill: African / tropical wetland agriculture, income, food security**

```
title_and_abstract.search:(wetland OR wetlands OR dambo OR fadama OR "inland valley" OR floodplain) AND (Africa OR Uganda OR Zambia OR Ethiopia OR Tanzania OR Malawi OR Rwanda OR Kenya OR Nigeria) AND (agriculture OR cultivation OR "food security" OR livelihood OR income)
```

`sort=relevance_score:desc` · `per-page=35` · `mailto=p.steward@cgiar.org` — **total 3886**, retrieved 35.

**Q10 — ecosystem-service syntheses over wetland restoration**

```
title_and_abstract.search:(wetland OR wetlands OR peatland) AND (restoration OR restored OR rewetting) AND ("ecosystem services" OR "ecosystem service") AND ("meta-analysis" OR "systematic review" OR "global synthesis" OR "evidence map")
```

`sort=relevance_score:desc` · `per-page=30` · `mailto=p.steward@cgiar.org` — **total 57**, retrieved 30.

**Q11 — water regulation: flood, drought, storage syntheses**

```
title_and_abstract.search:(wetland OR wetlands OR floodplain OR peatland) AND (restoration OR restored OR creation OR rewetting) AND (flood OR flooding OR drought OR "low flow" OR "water storage" OR runoff) AND ("meta-analysis" OR "systematic review" OR "evidence review" OR "global review" OR synthesis)
```

`sort=relevance_score:desc` · `per-page=30` · `mailto=p.steward@cgiar.org` — **total 200**, retrieved 30.

**Q12 — carbon / blue carbon syntheses**

```
title_and_abstract.search:(wetland OR wetlands OR marsh OR peatland) AND (restoration OR restored OR rewetting OR creation) AND ("carbon sequestration" OR "carbon stock" OR "soil organic carbon" OR "blue carbon" OR "carbon accumulation") AND ("meta-analysis" OR "systematic review" OR "global synthesis" OR "global review")
```

`sort=relevance_score:desc` · `per-page=30` · `mailto=p.steward@cgiar.org` — **total 66**, retrieved 30.

**Q13 — equity & inclusion: gender, indigenous, tenure, benefit sharing**

```
title_and_abstract.search:(wetland OR peatland OR mangrove OR marsh) AND (restoration OR rewetting OR management) AND (gender OR women OR equity OR indigenous OR "customary tenure" OR "land tenure" OR "benefit sharing" OR "environmental justice")
```

`sort=relevance_score:desc` · `per-page=35` · `mailto=p.steward@cgiar.org` — **total 2602**, retrieved 35.

**Q14 — constructed / treatment wetlands in LMIC settings**

```
title_and_abstract.search:"constructed wetland" AND ("developing countries" OR "low-income" OR tropical OR Africa OR India OR "rural communities" OR "decentralized") AND (cost OR performance OR review OR sustainability)
```

`sort=relevance_score:desc` · `per-page=30` · `mailto=p.steward@cgiar.org` — **total 1211**, retrieved 30.

**Q15 — production: yield, forage, fisheries under rewetting / restoration**

```
title_and_abstract.search:(peatland OR wetland OR "rewetted") AND (rewetting OR restoration OR "raised water table" OR "water table management") AND (yield OR "crop production" OR forage OR grassland OR fisheries OR "fish production" OR productivity)
```

`sort=relevance_score:desc` · `per-page=35` · `mailto=p.steward@cgiar.org` — **total 3682**, retrieved 35.

## PRISMA-lite funnel

| stage | n | note |
|---|---|---|
| queries run | 15 | all logged verbatim above |
| records returned across all queries (sum of per-query totals) | 15 602 | the addressable pool; not screened |
| records **retrieved** (page 1 of each query, 30–40 each) | 485 | retrieval capped per query, as the limits allow |
| **unique** records retrieved | 449 | 36 records were returned by more than one query |
| dropped at **dedup** against `wetland_known_sources.json` (70 rows) | 3 | by DOI; see below |
| **screened** (title + abstract + venue + record type, five-step funnel) | 446 | |
| excluded at screening | 395 | reasons grouped below |
| **included** | **51** | `wet_t6_lit_2026-10-14.json` |

### Dedup

`wetland_known_sources.json` holds 70 rows. Matching every one of the 449 retrieved records by **DOI** and by **normalised-citation prefix** found only **three** already-known records:

| record | matched on | title |
|---|---|---|
| `10.2134/jeq2006.0462` | DOI | Mayer et al. (2007), *Meta-Analysis of Nitrogen Removal in Riparian Buffers* — a riparian source that surfaced in the nutrient query |
| `10.1007/s13157-018-1017-6` | DOI | Dohong et al. (2018), *A Review of Techniques for Effective Tropical Peatland Restoration* |
| `10.1111/1365-2664.13905` | DOI | Mishra et al. (2021), *Degradation of Southeast Asian tropical peatlands…* |

As a second, wider check the 51 included candidates were also matched against the **full** `pipeline/acquisition_queue.csv` and `SRC_source_register.csv` — **zero** `source_id` collisions and **zero** DOI collisions, so nothing here duplicates anything already in the pipeline.

**Three out of 449 is the finding, not a footnote.** The existing wetland corpus is overwhelmingly *suitability and spatial-targeting* literature — site selection, MCDA, potential-wetland mapping, buffer widths. An **effect**-shaped search barely intersects it. Tan et al. (2021) on tropical paludiculture, already registered, did not even surface in the paludiculture query. Treat this round as building the effect corpus close to from scratch, not as topping up an existing one.

### Screening: the five-step funnel

1. **Frame** — does the record speak to a *wetland-management* practice (restore, rewet, create, reconstruct, block drainage, reconnect floodplain, constructed treatment wetland, tidal marsh) and to a *T5 priority, economics or adoption*? Hydrology-only, remote-sensing-method, mapping and suitability papers were framed out — they are T4/T1 material, and T4 extraction is paused.
2. **Source type** — journal articles, reviews and book chapters in peer-reviewed series kept. Conference abstracts (EGU/OpenAgrar), dissertations, dataset records and OpenAlex "additional file" artefacts excluded outright: no stable page-locatable artefact of record. Two SSRN/EarthArXiv preprints were kept *flagged* `preprint` because they fill a weighted gap; neither may set a class until a human confirms a published version.
3. **Relevance / PICOS** — the practice must be **named in the record itself**. This excluded a large block of otherwise attractive records:
   - **Mangrove** papers (Su et al. 2021 *Nature Communications* meta-analysis of ecological and economic outcomes of mangrove restoration; van Zanten et al. 2025 Indonesia spatial CBA; Lovelock & Brown 2019 on tenure; Beck et al. 2022 return on investment). `mangrove_restoration` maps to **`forest_restoration`** in FAM, not `wetland_management`. These are high-value — **hand them to the forest-restoration lane**, do not borrow them here.
   - **Drying–rewetting soil-microbiology** papers (Fierer & Schimel, Barnard et al. and relatives). The word "rewetting" there means a laboratory moisture cycle, not a management intervention.
   - **Wetland *degradation*/urbanisation** papers where no restoration or management action is evaluated.
4. **Six-axis credibility** — evidence strength, methodological transparency, authority and venue, context transferability (LMIC tie-break applied in favour of inclusion), recency offset by seminality, minus an independence discount. Produced the proposed `benchmark_tier`: **High 32 · Medium 18 · Low 1**. Predatory-adjacent and very low-visibility venues were dropped (one, `wet_policy_conservation_household_income_kabale_2022`, was kept at **Low** *only* because measured LIC household-income effects are otherwise unobtainable — it is explicitly marked for hard screening at extraction).
5. **Saturation stop** — reached in the carbon/GHG lane (Q4, Q12 and Q15 kept returning the same core of Zou, Günther, Evans, Wilson, Ojanen) and in the European paludiculture lane. Not reached for LMIC household outcomes, equity, or coastal marsh economics; those were still yielding new material when the retrieval cap bound.

### Why the 395 exclusions, grouped

| reason | rough share | examples |
|---|---|---|
| no wetland-management practice evaluated (mapping, suitability, monitoring, degradation description) | ~40 % | potential-wetland RF mapping, SAR wetland monitoring meta-analyses, urbanisation reviews |
| wrong NbS under PICOS — mangrove / riparian buffer / grassland | ~15 % | Su 2021, Beck 2022, Mayer 2007, Blanco-Canqui 2004 |
| not an artefact of record (conference abstract, dissertation, dataset, supplementary file) | ~15 % | EGU abstracts, OpenAgrar items, five Figshare "Additional file of…" records for Land 2016 |
| "rewetting" in the soil-moisture-cycle sense | ~8 % | Fierer & Schimel 2002, Barnard 2013 |
| constructed-wetland *engineering* with no rural-landscape relevance (substrate chemistry, microplastics, LDH coatings) | ~8 % | zeolite-modified substrate studies, benthic-fauna meta-analyses |
| redundant with a stronger included source | ~8 % | Wei 2016 hurdle model vs Wei 2020; Zhu 2016 vs Wei 2020; De Lauretis 2026 vs Palacios 2026 |
| off-topic noise from the broad LMIC and equity queries (Q9, Q13 are intentionally wide and low-precision) | ~6 % | ecoregion assessments, fisheries governance, coastal-zone handbooks |


## Included candidates (51)

Grouped by the priority they most directly serve. Every row carries the DOI and OpenAlex id exactly as the record gave them.

### Carbon and the full greenhouse-gas balance

| # | Source | Year | Venue | DOI | OpenAlex | OA | Type | Basis | Priorities | Families | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Junyu Zou — *Rewetting global wetlands effectively reduces major greenhouse gas emissions* | 2022 | Nature Geoscience | `10.1038/s41561-022-00989-0` | `W4288447279` | green | meta_analysis | measured | carbon_sequestration_potential | restoration/rewetting · peatland · coastal | High |
| 2 | Anke Beate Günther — *Prompt rewetting of drained peatlands reduces climate warming despite methane emissions* | 2020 | Nature Communications | `10.1038/s41467-020-15499-z` | `W3015108117` | gold | synthesis_modelling | mixed | carbon_sequestration_potential | peatland · restoration/rewetting | High |
| 3 | Lishan Tan — *Conversion of coastal wetlands, riparian wetlands, and peatlands increases greenhouse gas em…* | 2019 | Global Change Biology | `10.1111/gcb.14933` | `W2990852122` | closed → OA recovery | meta_analysis | measured | carbon_sequestration_potential | restoration/rewetting · peatland · coastal | High |
| 4 | Chris Evans — *Overriding water table control on managed peatland greenhouse gas emissions* | 2021 | Nature | `10.1038/s41586-021-03523-1` | `W3155336766` | green | synthesis | measured | carbon_sequestration_potential | peatland · restoration/rewetting | High |
| 5 | Paavo Ojanen — *Rewetting Offers Rapid Climate Benefits for Tropical and Agricultural Peatlands But Not for …* | 2020 | Global Biogeochemical Cycles | `10.1029/2019gb006503` | `W3037793133` | hybrid | synthesis | measured | carbon_sequestration_potential | peatland | High |
| 6 | Earthy Matters Environmental Consultants, Donegal, Ireland — *Greenhouse gas emission factors associated with rewetting of organic soils* | 2016 | Mires and Peat | `10.19189/map.2016.omb.222` | `W2472871865` | diamond | synthesis | measured | carbon_sequestration_potential | peatland · restoration/rewetting | High |
| 7 | Shangqi Xu — *Responses of methane emissions to global wetland restoration and influencing factors* | 2025 | Agricultural and Forest Meteorology | `10.1016/j.agrformet.2025.110459` | `W4407804520` | closed → OA recovery | meta_analysis | measured | carbon_sequestration_potential | restoration/rewetting · creation · peatland | High |
| 8 | Shangqi Xu — *Soil organic carbon changes following wetland restoration: A global meta-analysis* | 2019 | Geoderma | `10.1016/j.geoderma.2019.06.027` | `W4249702774` | closed → OA recovery | meta_analysis | measured | carbon_sequestration_potential | restoration/rewetting · creation | High |
| 9 | Yanan Wu — *Wetland Restoration Is Effective but Insufficient to Compensate for Soil Organic Carbon Loss…* | 2025 | Global Ecology and Biogeography | `10.1111/geb.70063` | `W4410522203` | bronze | meta_analysis | measured | carbon_sequestration_potential | restoration/rewetting · creation · peatland | High |
| 10 | Antonio Camacho — *Carbon stock recovery and greenhouse gas shifts following wetland restoration: a global meta…* | 2025 | — | `10.31223/x53f3z` | `W7117787929` | gold | meta_analysis | measured | carbon_sequestration_potential | restoration/rewetting · creation · peatland · coastal | Medium |
| 11 | David Wilson — *Rewetting of Cutaway Peatlands: Are We Re‐Creating Hot Spots of Methane Emissions?* | 2008 | Restoration Ecology | `10.1111/j.1526-100x.2008.00416.x` | `W1977897828` | closed → OA recovery | primary | measured | carbon_sequestration_potential | peatland | Medium |
| 12 | Pierre Taillardat — *Climate change mitigation potential of wetlands and the cost-effectiveness of their restorat…* | 2020 | Interface Focus | `10.1098/rsfs.2019.0129` | `W3048644195` | bronze | review | mixed | carbon_sequestration_potential | restoration/rewetting · creation · peatland · coastal | High |
| 13 | Nisa Novita — *Natural climate solutions in Indonesia: wetlands are the key to achieve Indonesia’s national…* | 2022 | Environmental Research Letters | `10.1088/1748-9326/ac9e0a` | `W4308023981` | gold | modelling | modelled | carbon_sequestration_potential | peatland · coastal · restoration/rewetting | High |

- **`wet_rewetting_global_ghg_reduction_2022`** — *Why in:* Core carbon cell: rewetting effect on the FULL GHG balance (CO2 + CH4 + N2O), globally pooled — directly addresses the missing methane term in our carbon rows. *Tier:* Global synthesis of paired drained-vs-rewetted sites in Nature Geoscience; CO2, CH4 and N2O together; high citation and transparent data appendix *Flags:* `full_ghg_balance`
- **`wet_prompt_rewetting_climate_warming_2020`** — *Why in:* Answers the methane question explicitly: rewetting reduces warming despite the CH4 pulse, with timing. Flag as part-modelled (strength cap applies if no measured backer in the cell). *Tier:* Nature Communications; couples an emission-factor synthesis with a radiative-forcing model; 450+ citations; the canonical 'does methane cancel the benefit?' answer *Flags:* `full_ghg_balance, modelled_component`
- **`wet_conversion_coastal_riparian_peat_ghg_meta_2019`** — *Why in:* Inverse evidence: what CONVERSION of wetlands costs in GHG terms. Encode with care — it is a degradation contrast, not a restoration contrast. *Tier:* Global meta-analysis in Global Change Biology across coastal, riparian and peat wetlands; CO2, CH4 and N2O *Flags:* `full_ghg_balance, comparator_degradation`
- **`wet_water_table_control_peatland_ghg_2021`** — *Why in:* The water-table depth → emissions response curve. Gives a graded (not binary) rewetting effect, which the T6 carbon cell currently lacks. *Tier:* Nature; pooled flux data across managed peatlands establishing the water-table / emissions response function; 500+ citations *Flags:* `full_ghg_balance, dose_response`
- **`wet_rewetting_tropical_vs_forestry_peat_2020`** — *Why in:* Highest-value carbon source for the tropical/LMIC gap: it states where rewetting pays climate dividends fast (tropical, agricultural) and where it does not (forestry-drained). *Tier:* Global Biogeochemical Cycles; emission-factor synthesis split by peatland type; explicitly separates TROPICAL and agricultural peat from forestry-drained peat *Flags:* `full_ghg_balance, tropical`
- **`wet_rewetting_organic_soils_emission_factors_2016`** — *Why in:* Tier-1 emission factors for rewetted organic soils by climate zone including tropical — a defensible scoping-grade number per hectare. *Tier:* Mires and Peat; the emission-factor synthesis underpinning the IPCC Wetlands Supplement rewetting factors; diamond OA *Flags:* `full_ghg_balance, tropical`
- **`wet_methane_response_global_restoration_2025`** — *Why in:* The single most targeted fix for our missing methane term: methane response to restoration, globally, with moderators. *Tier:* Agricultural and Forest Meteorology; global meta-analysis dedicated to the methane response to wetland restoration and its drivers *Flags:* `methane_specific`
- **`wet_soc_change_restoration_global_meta_2019`** — *Why in:* SOC accrual rates after restoration — the carbon-stock half of the carbon cell. *Tier:* Geoderma; global meta-analysis of soil organic carbon change after wetland restoration *Flags:* `—`
- **`wet_restoration_insufficient_soc_recovery_2025`** — *Why in:* Tempering evidence: restoration recovers SOC but does not fully compensate degradation losses. Prevents an over-stated carbon class. *Tier:* Global Ecology and Biogeography; global meta-analysis quantifying the SOC recovery shortfall relative to degradation losses *Flags:* `maladaptation_signal`
- **`wet_carbon_stock_ghg_shift_restoration_meta_2025`** — *Why in:* Carbon stock and GHG shift in one synthesis. PREPRINT — human must confirm a peer-reviewed version before it sets a class. *Tier:* Global meta-analysis of carbon stock recovery AND GHG shifts after restoration, but an EarthArXiv preprint — not yet peer reviewed *Flags:* `full_ghg_balance, preprint`
- **`wet_cutaway_rewetting_methane_hotspots_2008`** — *Why in:* Primary admitted deliberately: a measured harm finding (CH4 hot spots after rewetting cutaway peat) for the maladaptation list the T6 carbon row must carry. *Tier:* Restoration Ecology; primary field study, but one of the few that reports a methane REVERSAL after rewetting *Flags:* `maladaptation_signal, primary_admitted`
- **`wet_mitigation_potential_cost_effectiveness_2020`** — *Why in:* Cost per tonne CO2e avoided and cost per hectare across wetland types — the economics anchor for the T6 carbon and cost rows. Its cost database is a DATASET (seed list only under the paused dataset rule). *Tier:* Interface Focus (Royal Society); pairs mitigation potential with a compiled restoration-cost database (published separately as a dataset) *Flags:* `economics, cost_per_tco2e`
- **`wet_ncs_indonesia_wetlands_key_2022`** — *Why in:* Tropical/LMIC carbon potential at national scale. MODELLED — strength cap applies unless a measured unit backs it. *Tier:* Environmental Research Letters; national natural-climate-solutions assessment for Indonesia with wetlands as the dominant lever *Flags:* `tropical, modelled_only`

### Water quality and nutrient removal

| # | Source | Year | Venue | DOI | OpenAlex | OA | Type | Basis | Priorities | Families | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Magnus Land — *How effective are created or restored freshwater wetlands for nitrogen and phosphorus remova…* | 2016 | Environmental Evidence | `10.1186/s13750-016-0060-0` | `W2109326402` | gold | systematic_review | measured | water_quality_risk | creation · restoration/rewetting · constructed | High |
| 2 | Emily A. Ury — *Source or sink? Meta-analysis reveals diverging controls of phosphorus retention and release…* | 2023 | Environmental Research Letters | `10.1088/1748-9326/ace6bf` | `W4384008915` | gold | meta_analysis | measured | water_quality_risk | restoration/rewetting · creation · constructed | High |
| 3 | Tiffany L. Messer — *Constructed Wetlands for Water Quality Improvement: A Synthesis on Nutrient Reduction from A…* | 2021 | Transactions of the ASABE | `10.13031/trans.13976` | `W3130500292` | bronze | synthesis | measured | water_quality_risk | constructed · creation | Medium |
| 4 | Dong Qing Zhang — *Application of constructed wetlands for wastewater treatment in developing countries – A rev…* | 2014 | Journal of Environmental Management | `10.1016/j.jenvman.2014.03.015` | `W1991118947` | closed → OA recovery | review | measured | water_quality_risk | constructed | Medium |

- **`wet_created_restored_n_p_removal_cee_sr_2016`** — *Why in:* The headline water-quality source: how effective created/restored wetlands actually are for N and P removal, with the evidence base characterised. *Tier:* Environmental Evidence (CEE-registered systematic review) with a published protocol; the benchmark N and P removal synthesis for created and restored wetlands *Flags:* `cee_systematic_review`
- **`wet_phosphorus_source_or_sink_meta_2023`** — *Why in:* Directional nuance the water-quality row needs: P source-vs-sink behaviour. Carries measured harm findings. *Tier:* Environmental Research Letters; meta-analysis showing restored and constructed wetlands can RELEASE phosphorus as well as retain it *Flags:* `maladaptation_signal`
- **`wet_cw_nutrient_reduction_ag_effluent_synth_2021`** — *Why in:* Agricultural-drainage treatment wetlands: nutrient reduction performance for the farm context the Rural Scan cares about. *Tier:* Transactions of the ASABE; synthesis focused specifically on AGRICULTURAL effluent, which is our use case rather than municipal sewage *Flags:* `qualitative_only_family`
- **`wet_cw_developing_countries_review_2014`** — *Why in:* LMIC gap-fill for constructed wetlands: performance, cost and failure modes outside high-income settings. *Tier:* Journal of Environmental Management; the standard review of constructed wetlands in DEVELOPING countries (2000-2013), 400+ citations *Flags:* `lmic, qualitative_only_family`

### Biodiversity and ecological recovery

| # | Source | Year | Venue | DOI | OpenAlex | OA | Type | Basis | Priorities | Families | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Paula Meli — *Restoration Enhances Wetland Biodiversity and Ecosystem Service Supply, but Results Are Cont…* | 2014 | PLoS ONE | `10.1371/journal.pone.0093507` | `W2073272243` | gold | meta_analysis | measured | biodiversity_priority · water_quality_risk · carbon_sequestration_potential | restoration/rewetting · creation · coastal | High |
| 2 | David Moreno‐Mateos — *Structural and Functional Loss in Restored Wetland Ecosystems* | 2012 | PLoS Biology | `10.1371/journal.pbio.1001247` | `W2041396888` | gold | meta_analysis | measured | biodiversity_priority · carbon_sequestration_potential | restoration/rewetting · creation | High |
| 3 | Lerong Liu — *Effectiveness assessment of China's coastal wetland ecological restoration: A meta-analysis* | 2024 | The Science of The Total Environment | `10.1016/j.scitotenv.2024.173336` | `W4397023993` | closed → OA recovery | meta_analysis | measured | biodiversity_priority · carbon_sequestration_potential | coastal · restoration/rewetting | High |
| 4 | J. Allan — *Meta‐analysis reveals that enhanced practices accelerate vegetation recovery during peatland…* | 2023 | Restoration Ecology | `10.1111/rec.14015` | `W4387397471` | green | meta_analysis | measured | biodiversity_priority | peatland | High |
| 5 | Sally Maxwell — *Restoration and rehabilitation of floodplain wetlands: a systematic, global review of restor…* | 2026 | Restoration Ecology | `10.1111/rec.70458` | `W7163954054` | hybrid | systematic_review | measured | biodiversity_priority · water_quality_risk | restoration/rewetting · creation | High |
| 6 | Maria M. Palacios — *Tidal reinstatement of coastal wetlands: a global review* | 2026 | Restoration Ecology | `10.1111/rec.70347` | `W7128474033` | hybrid | review | measured | biodiversity_priority · carbon_sequestration_potential | coastal | High |

- **`wet_restoration_biodiversity_es_meta_2014`** — *Why in:* Primary biodiversity cell source, and it reports service supply alongside biodiversity so one extraction pass serves several T6 rows. *Tier:* PLoS ONE; the canonical wetland-restoration meta-analysis for biodiversity AND ecosystem-service supply, with explicit context dependence *Flags:* `multi_outcome`
- **`wet_structural_functional_loss_restored_2012`** — *Why in:* Sets the realistic ceiling: restored wetlands sit well below reference condition for decades. Essential so the biodiversity row is not scored as full recovery. *Tier:* PLoS Biology; 621 restored wetlands worldwide; 950+ citations; the reference for incomplete recovery and its time course *Flags:* `recovery_trajectory`
- **`wet_china_coastal_restoration_effectiveness_meta_2024`** — *Why in:* Coastal family evidence from a large non-Western programme; upper-middle income, which widens our transfer envelope. *Tier:* Science of the Total Environment; meta-analysis of China's coastal wetland restoration programme outcomes *Flags:* `—`
- **`wet_peatland_restoration_vegetation_recovery_meta_2023`** — *Why in:* Peatland biodiversity cell, and it separates practice intensities, which maps onto our sub-practice split. *Tier:* Restoration Ecology; meta-analysis comparing enhanced versus passive peatland restoration practices on vegetation recovery *Flags:* `—`
- **`wet_floodplain_restoration_options_outcomes_sr_2026`** — *Why in:* Maps restoration options to outcomes, which is close to the structure of a T6 row and should extract cleanly. *Tier:* Restoration Ecology; global systematic review of floodplain-wetland restoration OPTIONS and their outcomes *Flags:* `—`
- **`wet_tidal_reinstatement_global_review_2026`** — *Why in:* The coastal family is our thinnest; this is a direct global review of the practice. *Tier:* Restoration Ecology; global review of tidal reinstatement outcomes for coastal wetlands *Flags:* `—`

### Water regulation and multi-outcome syntheses

| # | Source | Year | Venue | DOI | OpenAlex | OA | Type | Basis | Priorities | Families | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Arvid Bring — *Effects on groundwater storage of restoring, constructing or draining wetlands in temperate …* | 2022 | Environmental Evidence | `10.1186/s13750-022-00289-5` | `W4311842500` | gold | systematic_review | measured | water_stress | restoration/rewetting · creation | High |
| 2 | Aleksi Räsänen — *After-use of peat extraction sites – A systematic review of biodiversity, climate, hydrologi…* | 2023 | The Science of The Total Environment | `10.1016/j.scitotenv.2023.163583` | `W4366606931` | hybrid | systematic_review | measured | biodiversity_priority · carbon_sequestration_potential · rural_poverty | peatland | High |

- **`wet_groundwater_storage_restoration_cee_sr_2022`** — *Why in:* Water-availability cell. Explicitly temperate/boreal — flag the applicability envelope so it cannot silently set an LMIC class. *Tier:* Environmental Evidence; CEE systematic review with a published protocol on groundwater-storage effects of restoring, constructing or draining wetlands *Flags:* `cee_systematic_review, hic_only`
- **`wet_peat_extraction_afteruse_sr_2023`** — *Why in:* Rare four-domain synthesis including social outcomes — one extraction serves several T6 rows. *Tier:* Science of the Total Environment; systematic review covering biodiversity, climate, hydrological AND social impacts of peat-extraction after-use in one pass *Flags:* `multi_outcome`

### Rural poverty, household income, food security

| # | Source | Year | Venue | DOI | OpenAlex | OA | Type | Basis | Priorities | Families | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Ji Feng — *Wetland restoration, household income, and livelihood structure of farmers* | 2024 | Frontiers in Sustainable Food Systems | `10.3389/fsufs.2024.1256115` | `W4404304807` | gold | primary | measured | rural_poverty · production_gap | restoration/rewetting | Medium |
| 2 | N.L. Nabahungu — *Contribution of wetland agriculture to farmers' livelihood in Rwanda* | 2011 | Ecological Economics | `10.1016/j.ecolecon.2011.07.028` | `W1983987796` | green | primary | measured | rural_poverty · production_gap · agricultural_dependency | restoration/rewetting | High |
| 3 | Nelson Turyahabwe — *Contribution of wetland resources to household food security in Uganda* | 2013 | Agriculture & Food Security | `10.1186/2048-7010-2-5` | `W2118549641` | gold | primary | measured | rural_poverty · production_gap | restoration/rewetting | Medium |
| 4 | Julius Masanyu — *Effects of Wetland Policy on Conservation and Household Incomes in Kabale District, Uganda* | 2022 | Uganda Journal of Agricultural Sciences | `10.4314/ujas.v21i1.2` | `W4312412444` | diamond | primary | measured | rural_poverty | restoration/rewetting | Low |
| 5 | Lisa‐Maria Rebelo — *Wetlands of Sub-Saharan Africa: distribution and contribution of agriculture to livelihoods* | 2009 | Wetlands Ecology and Management | `10.1007/s11273-009-9142-x` | `W2147086132` | closed → OA recovery | review | mixed | rural_poverty · production_gap · agricultural_dependency | restoration/rewetting · creation | High |
| 6 | Massimo Lupascu — *Climate-smart peatland management and the potential for synergies between food security and …* | 2023 | Global Environmental Change | `10.1016/j.gloenvcha.2023.102731` | `W4385609207` | closed → OA recovery | synthesis | mixed | rural_poverty · production_gap · carbon_sequestration_potential | peatland | High |
| 7 | CSIRO Environment, Black Mountain, ACT, Australia — *Facilitating new livelihoods to promote peatland restoration in Indonesia - what are the cha…* | 2024 | Mires and Peat | `10.19189/map.2023.omb.sc.2105613` | `W4415871950` | diamond | review | mixed | rural_poverty · gender_inequity | peatland | Medium |
| 8 | Alan B. Dixon — *Wetland cultivation and hydrological management in eastern Africa: Matching community and hy…* | 2003 | Natural Resources Forum | `10.1111/1477-8947.00047` | `W2134413291` | closed → OA recovery | review | mixed | rural_poverty · production_gap · water_stress | restoration/rewetting | Medium |

- **`wet_restoration_household_income_structure_2024`** — *Why in:* MEASURED household income under restoration — exactly the measurement our poverty row is missing. Primary admitted because no synthesis measures household income. *Tier:* Frontiers in Sustainable Food Systems; household survey quantifying income and livelihood-structure change under a wetland restoration programme *Flags:* `measured_household_outcome, primary_admitted`
- **`wet_agriculture_farmers_livelihood_rwanda_2011`** — *Why in:* Measured LIC household income from wetland use. COMPARATOR WARNING: this is EXISTING wetland use, not restoration — tag context.comparator=existing_wetland (comparator_policy keeps it in the restoration family, out of the roll-up). *Tier:* Ecological Economics; quantified household contribution of wetland agriculture in a low-income country; 85+ citations *Flags:* `measured_household_outcome, comparator_existing_wetland, lmic, primary_admitted`
- **`wet_resources_household_food_security_uganda_2013`** — *Why in:* Measured LIC food-security outcome. Same existing-wetland comparator caveat. *Tier:* Agriculture & Food Security; household survey of wetland contribution to food security in Uganda; gold OA *Flags:* `measured_household_outcome, comparator_existing_wetland, lmic, primary_admitted`
- **`wet_policy_conservation_household_income_kabale_2022`** — *Why in:* Measured household-income effect of wetland conservation policy in a low-income country — one of only four measured household outcomes in this round. LOW tier: verify the sampling and comparison group at extraction before it sets any class. *Tier:* Uganda Journal of Agricultural Sciences (AJOL, diamond OA); small single-district study in a low-visibility venue, admitted only because measured LIC household-income effects of a wetland POLICY are almost unobtainable *Flags:* `measured_household_outcome, lmic, primary_admitted, weak_venue`
- **`wet_ssa_distribution_agriculture_livelihoods_2009`** — *Why in:* The regional framing source for the LMIC gap: who depends on African wetlands and for how much of their income. *Tier:* Wetlands Ecology and Management; IWMI-authored review of sub-Saharan African wetland extent and the livelihood contribution of wetland agriculture; 230+ citations *Flags:* `lmic, comparator_existing_wetland`
- **`wet_climate_smart_peatland_food_security_2023`** — *Why in:* The explicit carbon-versus-food-security trade-off in a tropical LMIC — the heart of the poverty row for peatland rewetting. *Tier:* Global Environmental Change; assesses synergies and trade-offs between peatland climate objectives and FOOD SECURITY in Indonesia *Flags:* `lmic, tropical`
- **`wet_new_livelihoods_peatland_restoration_indonesia_2024`** — *Why in:* What alternative livelihoods actually delivered, and for whom — the dis-adoption and equity side of rewetting at programme scale. *Tier:* Mires and Peat (diamond OA); CSIRO-led assessment of livelihood transitions under Indonesia's peatland restoration programme, including equity of the transition *Flags:* `lmic, tropical, equity`
- **`wet_cultivation_hydrological_mgmt_east_africa_2003`** — *Why in:* The African trade-off framing: cultivating wetlands feeds households but costs hydrological function. Existing-wetland comparator. *Tier:* Natural Resources Forum; 150+ citations; matches community livelihood needs against wetland hydrological function in eastern Africa *Flags:* `lmic, comparator_existing_wetland`

### Paludiculture: production and economics

| # | Source | Year | Venue | DOI | OpenAlex | OA | Type | Basis | Priorities | Families | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Regina Neudert — *Paludiculture - a scoping review of the agricultural, economic and social science literature* | 2026 | Frontiers in Environmental Science | `10.3389/fenvs.2026.1868484` | `W7170143564` | gold | systematic_review | mixed | production_gap · rural_poverty · carbon_sequestration_potential | peatland | High |
| 2 | Ralph J. M. Temmink — *Agriculture on wet peatlands: the sustainability potential of paludiculture* | 2025 | Agricultural Systems | `10.1016/j.agsy.2025.104561` | `W7106097676` | hybrid | review | mixed | production_gap · carbon_sequestration_potential | peatland | High |
| 3 | Saritha Kittie Uda — *Towards better use of Indonesian peatlands with paludiculture and low-drainage food crops* | 2020 | Wetlands Ecology and Management | `10.1007/s11273-020-09728-x` | `W3031201977` | hybrid | review | mixed | production_gap · rural_poverty · carbon_sequestration_potential | peatland | High |
| 4 | Ibnu Budiman — *Progress of paludiculture projects in supporting peatland ecosystem restoration in Indonesia* | 2020 | Global Ecology and Conservation | `10.1016/j.gecco.2020.e01084` | `W3024168701` | gold | review | mixed | production_gap · rural_poverty | peatland | Medium |
| 5 | Sabine Wichmann — *Commercial viability of paludiculture: A comparison of harvesting reeds for biogas productio…* | 2016 | Ecological Engineering | `10.1016/j.ecoleng.2016.03.018` | `W2334369750` | closed → OA recovery | primary | mixed | production_gap · rural_poverty | peatland | Medium |

- **`wet_paludiculture_scoping_review_econ_social_2026`** — *Why in:* The single best economics-and-adoption synthesis for paludiculture. Explicitly in the brief's scope. *Tier:* Frontiers in Environmental Science; scoping review covering the agricultural, ECONOMIC and social-science paludiculture literature — the synthesis our economics row lacks *Flags:* `economics, adoption`
- **`wet_paludiculture_sustainability_potential_2025`** — *Why in:* Production versus GHG trade-off for paludiculture, in a farming-systems journal — maps onto production_gap and carbon in one pass. *Tier:* Agricultural Systems; assessment of whether agriculture on wet peat can be productive and climate-positive at once *Flags:* `economics, full_ghg_balance`
- **`wet_indonesia_paludiculture_low_drainage_crops_2020`** — *Why in:* Tropical paludiculture production AND farm economics — the LMIC counterpart to the European paludiculture literature. *Tier:* Wetlands Ecology and Management; evaluates paludiculture and low-drainage food crops for Indonesian peat, with yields and returns *Flags:* `lmic, tropical, economics`
- **`wet_paludiculture_projects_indonesia_progress_2020`** — *Why in:* Implementation reality including dis-adoption — directly serves the adoption question in the brief. *Tier:* Global Ecology and Conservation; reviews actual paludiculture project experience in Indonesia including why schemes stall *Flags:* `lmic, tropical, adoption`
- **`wet_paludiculture_commercial_viability_reed_2016`** — *Why in:* Explicit paludiculture cost and revenue structure. HIC-only — transfer class must be flagged. *Tier:* Ecological Engineering; costed comparison of three reed-biomass utilisation routes, one of the few full paludiculture cost structures *Flags:* `economics, hic_only, primary_admitted`

### Economics of restoration

| # | Source | Year | Venue | DOI | OpenAlex | OA | Type | Basis | Priorities | Families | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Shokhrukh–Mirzo Jalilov — *Unveiling economic dimensions of peatland restoration in Indonesia: A systematic literature …* | 2025 | Ecosystem Services | `10.1016/j.ecoser.2024.101693` | `W4405969883` | hybrid | systematic_review | mixed | rural_poverty · carbon_sequestration_potential | peatland | High |
| 2 | Jiangjing Wang — *Economic Evaluation and Systematic Review of Salt Marsh Restoration Projects at a Global Sca…* | 2022 | Frontiers in Ecology and Evolution | `10.3389/fevo.2022.865516` | `W4226185727` | gold | systematic_review | mixed | carbon_sequestration_potential · biodiversity_priority | coastal | High |
| 3 | Marije Schaafsma — *Combining focus group discussions and choice experiments for economic valuation of peatland …* | 2017 | Ecosystem Services | `10.1016/j.ecoser.2017.08.012` | `W2760380305` | bronze | primary | measured | rural_poverty · carbon_sequestration_potential | peatland | Medium |
| 4 | Edward B. Barbier — *Economics of Peatlands Conservation, Restoration and Sustainable Management* | 2024 | SSRN Electronic Journal | `10.2139/ssrn.4695533` | `W4391799462` | green | review | mixed | rural_poverty · carbon_sequestration_potential | peatland | Medium |

- **`wet_peatland_restoration_economics_indonesia_slr_2025`** — *Why in:* The economics synthesis for a tropical LMIC — costs, benefits and who bears them. Top pick for the brief's economics ask. *Tier:* Ecosystem Services; systematic literature review of the ECONOMIC dimensions of peatland restoration in Indonesia *Flags:* `lmic, tropical, economics`
- **`wet_salt_marsh_restoration_economic_sr_global_2022`** — *Why in:* Cost per hectare for coastal marsh restoration across projects — ordinal economics for the coastal family. *Tier:* Frontiers in Ecology and Evolution; systematic review plus economic evaluation of salt-marsh restoration projects at global scale, reporting per-hectare costs *Flags:* `economics, cost_per_hectare`
- **`wet_peatland_restoration_valuation_kalimantan_2017`** — *Why in:* Local willingness-to-pay/accept in an LMIC peat landscape; rare because the respondents are the affected households, not distant beneficiaries. *Tier:* Ecosystem Services; choice experiment plus focus groups valuing peatland restoration with LOCAL respondents in Central Kalimantan *Flags:* `lmic, tropical, economics, primary_admitted`
- **`wet_peatlands_economics_conservation_restoration_2024`** — *Why in:* Global peatland economics framing. PREPRINT — human to check for a published version before it sets any class. *Tier:* Barbier & Burgess, an authoritative environmental-economics pairing, BUT currently an SSRN working paper — not peer reviewed *Flags:* `economics, preprint`

### Adoption and dis-adoption

| # | Source | Year | Venue | DOI | OpenAlex | OA | Type | Basis | Priorities | Families | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Caroline Ward — *Smallholder perceptions of land restoration activities: rewetting tropical peatland oil palm…* | 2020 | Regional Environmental Change | `10.1007/s10113-020-01737-z` | `W3115945439` | hybrid | primary | measured | rural_poverty · agricultural_dependency | peatland | High |
| 2 | Xuan Wei — *Poyang lake wetlands restoration in China: An analysis of farmers’ perceptions and willingne…* | 2020 | Journal of Cleaner Production | `10.1016/j.jclepro.2020.125001` | `W3099158246` | closed → OA recovery | primary | measured | rural_poverty · agricultural_dependency | restoration/rewetting | Medium |
| 3 | Morena Merkelbach — *Readiness to transform: Pioneer farmers’ motivations and barriers for adopting paludiculture…* | 2026 | PLOS Sustainability and Transformation | `10.1371/journal.pstr.0000214` | `W7123586139` | gold | primary | measured | rural_poverty | peatland | Medium |

- **`wet_smallholder_perceptions_rewetting_sumatra_2020`** — *Why in:* Why smallholders accept or refuse rewetting, with the income loss named. No synthesis covers tropical rewetting adoption. *Tier:* Regional Environmental Change; smallholder survey on rewetting oil-palm peat in Sumatra — the adoption constraint in the exact LMIC context we target *Flags:* `lmic, tropical, adoption, primary_admitted`
- **`wet_poyang_farmer_willingness_participate_2020`** — *Why in:* Programme-scale adoption determinants and the compensation level that moves them. *Tier:* Journal of Cleaner Production; large farmer survey on willingness to participate in a national wetland restoration programme *Flags:* `adoption, primary_admitted`
- **`wet_paludiculture_pioneer_farmer_barriers_2026`** — *Why in:* Named adoption barriers for paludiculture. HIC-only — transfer class flag required. *Tier:* PLOS Sustainability and Transformation; qualitative study of pioneer paludiculture adopters' motivations and barriers *Flags:* `adoption, hic_only, primary_admitted`

### Equity and inclusion

| # | Source | Year | Venue | DOI | OpenAlex | OA | Type | Basis | Priorities | Families | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Tessa Toumbourou — *Livelihood‐oriented interventions and gender considerations of 25 years of social‐ecological…* | 2026 | Restoration Ecology | `10.1111/rec.70558` | `W7214216640` | hybrid | review | mixed | gender_inequity · rural_poverty · iplc_lands | peatland | High |
| 2 | Ashaluddin Jalil — *The Role of Social Capital of Riau Women Farmer Groups in Building Collective Action for Tro…* | 2021 | Forest and Society | `10.24259/fs.v5i2.12089` | `W3177894780` | gold | primary | measured | gender_inequity · iplc_lands | peatland | Medium |
| 3 | N. Liswanti — *Complexity of land tenure rights in peatland management in Southeast Asia* | 2025 | Center for International Forestry Research (CIFOR) eBooks | `10.17528/cifor-icraf/009358` | `W4408537016` | hybrid | review | mixed | iplc_lands · gender_inequity | peatland | Medium |
| 4 | Michelle L. Pyke — *Wetlands need people: a framework for understanding and promoting Australian indigenous wetl…* | 2018 | Ecology and Society | `10.5751/es-10283-230343` | `W2888611406` | gold | review | mixed | iplc_lands | restoration/rewetting · creation | Medium |

- **`wet_livelihood_gender_25yr_peatland_restoration_2026`** — *Why in:* The strongest equity source found: who gained and who did not over 25 years of tropical peatland restoration, gender explicitly disaggregated. *Tier:* Restoration Ecology; 25-year retrospective on livelihood interventions AND gender outcomes in Central Kalimantan peatland restoration *Flags:* `lmic, tropical, equity`
- **`wet_women_farmer_groups_social_capital_riau_2021`** — *Why in:* Gender and collective action in tropical peat restoration — the gender_inequity row currently has nothing measured. *Tier:* Forest and Society (gold OA); women's farmer-group collective action in Riau peatland restoration *Flags:* `lmic, tropical, equity, primary_admitted`
- **`wet_tenure_rights_peatland_sea_2025`** — *Why in:* Tenure and customary rights as the gate on peatland restoration — feeds the IPLC/FPIC flag and Module 6 rather than a suitability threshold. *Tier:* CIFOR-ICRAF; authoritative LMIC land-tenure analysis for peatland management across Southeast Asia *Flags:* `lmic, tropical, equity, grey_adjacent`
- **`wet_indigenous_wetland_management_framework_2018`** — *Why in:* Only substantive IPLC-framed wetland-management source found. HIC — flag the transfer class; still useful for the FPIC/ESS7 hand-off in Module 6. *Tier:* Ecology and Society (gold OA); framework for Indigenous wetland management grounded in Australian cases *Flags:* `equity, hic_only`

### Tropical peatland restoration, multi-outcome

| # | Source | Year | Venue | DOI | OpenAlex | OA | Type | Basis | Priorities | Families | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Tri Wira Yuwati — *Restoration of Degraded Tropical Peatland in Indonesia: A Review* | 2021 | Land | `10.3390/land10111170` | `W3210737515` | gold | review | mixed | carbon_sequestration_potential · biodiversity_priority · rural_poverty | peatland | High |
| 2 | Dilva Terzano — *Community‐led peatland restoration in Southeast Asia: 5Rs approach* | 2022 | Restoration Ecology | `10.1111/rec.13642` | `W4210462369` | hybrid | review | mixed | rural_poverty · iplc_lands | peatland | Medium |

- **`wet_degraded_tropical_peatland_indonesia_review_2021`** — *Why in:* Tropical multi-outcome review — one read serves carbon, biodiversity and livelihood cells for the peatland family. *Tier:* MDPI Land; comprehensive review of degraded tropical peatland restoration in Indonesia covering technique, outcome and socio-economics *Flags:* `lmic, tropical, multi_outcome`
- **`wet_community_led_peatland_restoration_sea_5rs_2022`** — *Why in:* Community-led delivery model and what made it work or fail — adoption plus equity in one tropical source. *Tier:* Restoration Ecology; synthesises community-led tropical peatland restoration across Southeast Asia (the 5Rs framing) *Flags:* `lmic, tropical, equity, adoption`

## Coverage of the included set

**By T5 priority** (a candidate may serve several): `carbon_sequestration_potential` 27 · `rural_poverty` 22 · `production_gap` 11 · `biodiversity_priority` 9 · `water_quality_risk` 6 · `iplc_lands` 5 · `gender_inequity` 4 · `agricultural_dependency` 4 · `water_stress` 2.

**By family:** `__peatland` 31 · `__restoration_rewetting` 26 · `__creation` 14 · `__coastal` 9 · `__constructed` 4.

**By evidence basis:** measured 31 · mixed 19 · modelled 1. Two candidates carry `modelled_component` or `modelled_only` and are flagged for the Decision 8a modelled-only strength cap.

**Encoding flags carried into extraction** (so the engine's rules are not rediscovered by hand):

- `full_ghg_balance` (8) and `methane_specific` (1) — the CO₂ + CH₄ sources.
- `maladaptation_signal` (3) — measured harm or reversal: phosphorus release from restored wetlands (Ury 2023), methane hot spots after cutaway rewetting (Wilson 2008), incomplete SOC recovery (Wu 2025). Under the 2026-10-07 lock these must appear in `justification.maladaptation`, never be absorbed into agreement.
- `comparator_existing_wetland` (4) — the African wetland-livelihood studies measure what an **existing** wetland delivers, not what restoring one delivers. `schema/lookups/comparator_policy.csv` already carries `wetland_management / existing_wetland → rollup_included=false, home_family=__restoration_rewetting`. Tag `context.comparator=existing_wetland` at extraction or these will inflate the restoration roll-up.
- `comparator_degradation` (1) — Tan 2019 measures the GHG cost of *converting* wetlands; it is a degradation contrast, not a restoration one.
- `hic_only` (4) and `qualitative_only_family` (2) — applicability envelope and family-parking warnings.
- `positive_bias_risk`, `weak_venue`, `preprint` — down-weight markers.
- `primary_admitted` (11) — each states in its note why no synthesis covers the cell.

**Effect locus.** `schema/lookups/effect_locus.csv` stamps `wetland_management` as **`off_site`**: wetland works sit outside cropped land and farmer effects are hydrological and downstream. Every T3 livelihood row generated from this corpus will carry `landscape_scale_only`. Nothing here contradicts that, but the household-income studies (Feng 2024, Nabahungu 2011, Turyahabwe 2013, Masanyu 2022) measure *on-household* income from wetland **use**, which is a different channel from downstream hydrological benefit — do not let them be read as an on-farm production effect.

## Access

DOIs: **51 of 51** candidates carry a DOI **taken from the OpenAlex record itself**. None was stitched together from a search snippet. All must still pass `verify_metadata.py` Crossref round-trip before acquisition; the title remains the trust anchor.

OA: **40 of 51** have a best-OA location recorded in `oa_url` (gold, green, hybrid, bronze, diamond). The other **11** are `oa_status=closed` in OpenAlex and are set to `rg_flag_for_human`, **not** `paywalled`. Per the locked OA-recovery rule, "OpenAlex says closed" is not proof of inaccessibility: Unpaywall-by-DOI **and** a per-source web search (ResearchGate, institutional and agency repositories, author copies) must be run before any institutional request. Neither was run here — this agent downloads nothing. The 11 are:

`wet_conversion_coastal_riparian_peat_ghg_meta_2019` · `wet_methane_response_global_restoration_2025` · `wet_soc_change_restoration_global_meta_2019` · `wet_cutaway_rewetting_methane_hotspots_2008` · `wet_cw_developing_countries_review_2014` · `wet_china_coastal_restoration_effectiveness_meta_2024` · `wet_ssa_distribution_agriculture_livelihoods_2009` · `wet_climate_smart_peatland_food_security_2023` · `wet_cultivation_hydrological_mgmt_east_africa_2003` · `wet_paludiculture_commercial_viability_reed_2016` · `wet_poyang_farmer_willingness_participate_2020`

Two of those — the global methane meta-analysis and the SSA livelihood review — are among the highest-value items in the round, so the OA pass on them is not optional.

## What I could not find — honestly

1. **No measured household-income effect of wetland restoration in a low-income country.** The four measured household outcomes are: one upper-middle-income restoration programme (Feng 2024, China), and three low-income studies (Rwanda, Uganda ×2) that measure **existing wetland use**, not restoration. The counterfactual we actually need — *households before and after a restoration or rewetting intervention, in an LIC* — did not appear in 449 records. The closest is Mendham 2024 and Toumbourou 2026 on Indonesia's programme, which are qualitative or mixed. **The poverty row cannot be made measured from this lane alone.** The MEL/impact-evaluation grey lane (3ie, IFAD IOE, GEF IEO, World Bank ICR/IEG, CIFOR) is the right next net, and that is a different run.
2. **No evidence gap map.** No 3ie, Campbell or CEE evidence gap map on wetland restoration surfaced. Two CEE *systematic reviews* did (Land 2016 on N and P; Bring 2022 on groundwater storage) and both are included.
3. **Economics stays thin and mostly ordinal.** No meta-analysis of restoration cost per hectare exists for wetlands as a class. Taillardat 2020 comes closest and its cost compilation is a **dataset** — under the paused dataset rule it is a discovery seed list only, never a registered source. Wang 2022 gives per-hectare salt-marsh costs. Jalilov 2025 is the only LMIC economics *synthesis*. Nothing at all on **labour requirements**, which the brief asked for: not one record in 449 quantified labour days per hectare for wetland works.
4. **Equity is four sources and three of them are Indonesia.** `gender_inequity` has four candidates, `iplc_lands` five, and the only non-Indonesian IPLC source is Australian (Pyke 2018, high-income). There is no African or Latin American wetland-equity evidence in this set. Gender-disaggregated *outcome* data — as opposed to gender-disaggregated participation — was not found anywhere.
5. **Coastal marsh is nine candidates and no LMIC economics.** Tidal-marsh restoration evidence is Australia, China, Europe and North America. The LMIC coastal literature that exists is overwhelmingly **mangrove**, which is `forest_restoration` under FAM and was excluded on PICOS. If the coastal family needs LMIC evidence, the honest route is a scheme conversation about whether mangrove evidence may inform tidal-marsh rows, not a quiet borrow.
6. **Constructed treatment wetlands in LMICs are a sanitation literature, not an agricultural one.** Q14 returned 1 211 records, almost all municipal or faecal-sludge wastewater. Agricultural-drainage treatment wetlands in LMICs barely exist as a literature. Combined with the family's `qualitative_only` status, this is a reason to keep constructed wetlands out of the generated tables, not a gap to chase.
7. **Production is the weakest priority after equity.** Eleven candidates touch `production_gap` and nearly all are paludiculture biomass in temperate Europe or Indonesian peat crops. There is no synthesis of what restoration or rewetting does to **crop or livestock production on neighbouring land**, which is the channel the off-site effect locus implies.
8. **Queries deliberately not run in this lane.** Fire and haze (a T3 hazard question, and T3 is Brayden's lane plus a separate run), salinity intrusion, and the multilingual Spanish, French, Portuguese and Indonesian forms — the Indonesian-language peatland literature is likely substantial and this English-only lane will have missed it.

## Next steps (for the orchestrator, not done here)

1. `verify_metadata.py verify` over all 51 DOIs — Crossref round-trip, rebuild citations, blank any DOI that fails.
2. OA-recovery pass over the 11 `rg_flag_for_human` rows before anything goes to Namita as institutional.
3. `scripts/register-discovery.py wetland_management --date 2026-10-14 --ruleset v1.6.10 --candidates lit=pipeline/staging/discovery/wet_t6_lit_2026-10-14.json --reports lit=pipeline/staging/discovery/wet_t6_lit_2026-10-14_report.md --log-names lit=wetland_management_T6_synthesis_2026-10.md --ledger updated_lit=done` — note the ledger stamp belongs to whoever runs it, not to this agent.
4. Run the **grey/MEL lane** next. Gap 1 above is the single most valuable thing outstanding and this lane cannot close it.

