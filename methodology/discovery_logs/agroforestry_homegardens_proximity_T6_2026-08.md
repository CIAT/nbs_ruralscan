# Discovery log — Agroforestry · homegardens_proximity · T6

- Run `discovery_crossfam_homegardens_2026-08` · date 2026-08-05 · by Pete/Claude · ruleset v1.4.1
- **Scope:** targeted discovery + screening only. No extraction (parked pending acquisition).

## PRISMA-lite (4 processes)

| process | retrieved | screened | included |
|---|---|---|---|
| stock | 137 | 24 | 3 |
| updated_lit | 89 | 20 | 4 |
| grey | 26 | 12 | 3 |
| tool | 6 | 6 | 0 |

### Verbatim search terms

- **stock:** `OpenAlex title.search (cited_by desc): "homegarden agroforestry"; "homegarden carbon storage"; "home garden income nutrition"`
- **updated_lit:** `OpenAlex title.search from_publication_date:2015-01-01 (cited_by desc): "homegarden agroforestry" (89); "home garden agroforestry" (36); "home garden agroforestry food security" (4)`
- **grey:** `WebSearch EN: 'WOCAT home garden homestead agroforestry technology tropical yield income'; 'FAO TECA home garden agroforestry food security nutrition income smallholder tropical'; 'World Bank home garden homestead agroforestry cost per beneficiary nutrition income impact evaluation'. ES: 'huerto familiar agroforestal seguridad alimentaria ingresos nutrición trópico WOCAT ICRAF'`
- **tool:** `WebSearch: 'github home garden homestead agroforestry suitability model settlement proximity multistrata mapping'`

## Screened-in candidates

| source_id | process | access | PICOS | rel | title / note |
|---|---|---|---|---|---|
| `kumar_nair_2004_tropical_homegardens` | stock | paywalled | ok | high | Tropical homegardens: a time-tested example of sustainable agroforestry (Kumar & Nair, review) — Seminal review explicitly on tropical homegardens as agroforestry; synthesises production, income share |
| `roshetko_2002_indonesia_homegarden_carbon` | stock | paywalled | ok | high | Carbon stocks in Indonesian homegarden systems: Can smallholder systems be targeted for increased carbon storage? — Carbon-storage outcome + smallholder income framing; Indonesia (in-scope geography). |
| `fernandes_nair_1984_chagga_homegardens` | stock | paywalled | ok | med | The Chagga homegardens: a multistoried agroforestry cropping system on Mt. Kilimanjaro (Tanzania) — Classic descriptive homegarden system paper; production/yield + species structure. More structural t |
| `sharma_2022_homegarden_sdg_review` | updated_lit | oa | ok | high | Homegarden agroforestry systems in achievement of Sustainable Development Goals. A review — Recent review mapping homegarden outcomes to SDGs: food security, income, nutrition, carbon, biodiversity. P |
| `panda_2023_odisha_nutrition_income` | updated_lit | oa | ok | high | Home gardens, household nutrition and income in rural farm households in Odisha, India — Direct empirical nutrition + income outcomes at household level; India (in-scope). Practice explicit. Hybrid OA |
| `linger_2019_ethiopia_adoption_challenges` | updated_lit | oa | ok | high | Opportunities and challenges of adopting home garden agroforestry practices in Ethiopia: A review — Adoption & dis-adoption drivers (observed-reality evidence) + livelihood outcomes. Practice explicit |
| `homegarden_adoption_foodsec_ethiopia_2025` | updated_lit | oa | ok | high | Determinants of adoption of home garden agroforestry practice and its role to food security in Southern Ethiopia — Adoption determinants + food-security outcome, empirical. Practice explicit. Diamond  |
| `wocat_tech_1103_homegarden` | grey | repo | ok | med | WOCAT SLM Technology entry (technologies_1103) — homestead/home-garden agroforestry technology — WOCAT diamond grey class (LMIC-grounded SLM DB); structured benefit/cost + establishment/maintenance da |
| `fao_rap_2006_homegardens_nutrition` | grey | oa | ok | high | FAO RAP Publication 2006/14 — Home gardens: key to improved nutritional well-being — FAO authority; nutrition/food-security outcomes of home gardens in Asia-Pacific tropics. OA PDF — cacheable. Grey d |
| `tesfaye_financial_analysis_homestead_ethiopia` | grey | oa | ok | med | Financial Analysis of Smallholder Woodlot and Homestead Agroforestry Systems... Household Income (Hawassa Zuria, S. Ethiopia) — Scoping-grade financial/income + indicative cost figures for homestead a |
| `homegarden_carbon_storage_2022` | updated_lit | paywalled | ok | med | Homegardens as a modern carbon storage: Assessment of tree diversity and above-ground biomass — Quantified above-ground biomass/carbon outcome. Practice explicit. Paywalled -> queue. Secondary to Rosh |

## Gaps / next iteration

GEOGRAPHY: recent title-searchable literature skews heavily to Ethiopia and India; the canonical high-diversity homegarden geographies named in scope (Indonesia/Java, Kerala, Sri Lanka, West Africa) are underrepresented in recent hits — worth a targeted ES/ID/full-text sweep and Kumar/Nair Kerala corpus. COST: genuinely thin — no scoping-grade cost-per-beneficiary / cost-per-hectare figures found for homegardens specifically; WB project docs (e.g. Chhattisgarh nutrition-agriculture P170645) mention aggregate project cost but not homegarden unit costs; the Longdom financial paper is the only quantified income/cost source and is low-tier. TOOLS: no tool encodes homegarden T6 outcome/cost parameters (all hits are T4 suitability/niche engines) — tool process yields nothing for T6. BIODIVERSITY vs T5: many top-cited homegarden papers are species-diversity descriptors that straddle T6 biodiversity-outcome and T5 descriptor; screening must separate quantified biodiversity OUTCOME (e.g. species richness delta vs alternative land use) from pure floristic inventory. PROXIMITY GATE: outcome literature rarely quantifies how outcomes vary with homestead/settlement proximity (the family's defining suitability gate) — outcomes are reported for the system as a whole, so T6 evidence will not directly validate the proximity driver. ACCESS: three seminal/quantified sources (Roshetko carbon, Chagga, 2022 carbon) are paywalled -> acquisition_queue for Namita-J / CGIAR institutional; prioritise ICRAF-repo check for Roshetko before paid retrieval.
