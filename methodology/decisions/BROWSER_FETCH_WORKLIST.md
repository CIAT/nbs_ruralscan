# Browser fetch worklist — for the desktop Claude session

**Who this is for:** a Claude session with a real browser, working alongside the pipeline
session. **Do not run git. Do not edit any file in the repository.** Your entire job is
downloading PDFs into the right OneDrive folders and reporting what you got.

## The job, per row of the table below

1. Open the URL in the browser. Every one of these is CONFIRMED free to read — a license or
   open-access check was already done. If a page asks for money or a login, something is
   wrong: skip it and note it, do not pay and do not log into anything.
2. Save the PDF as `<source_id>.pdf` (exactly the id in column one) into the folder in
   column three. The folders are under:
   `~/Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects/D591_Rural-Scan_NBS/2_Technical_&_Data/library/`
3. Open the saved file and check page 1 against the citation in column four: same title,
   same authors. A mismatch means the wrong file — note it and move on.
4. Keep a running list: source_id → done / skipped(reason) / mismatch(what page 1 says).
   At the end, save that list as `FETCH_REPORT_<date>.md` in the library root folder above.

When the files are in OneDrive, the pipeline session hydrates its cache from there and
marks the queue — you do not touch the queue.

## One extra task, two minutes

Go to the 3ie Development Evidence Portal (developmentevidence.3ieimpact.org), search for
wetland / peatland restoration impact evaluations and evidence gap maps. We believe there
are none; the portal blocks automated tools so nobody has confirmed it by eye. Write what
you find (or that you found nothing) into the same report file.

## The table

| source_id | url | folder | citation to verify |
|---|---|---|---|
| `homegarden_carbon_storage_2022` | https://doi.org/10.1016/j.ufug.2022.127671 | 1_Agroforestry | Lowe et al. (2022). Homegardens as a modern carbon storage: Assessment of tree diversity and above-ground biom |
| `begum_2025` | https://doi.org/10.1079/junoreports.2025.0004 | 1_Agroforestry | Begum et al. (2025). Mapping evidence on agroforestry’s role in biodiversity and climate change mitigation and |
| `baker_2025` | https://doi.org/10.1016/j.agsy.2024.104240 | 1_Agroforestry | Baker et al. (2025). Effect of silvopasture, paddock trees and linear agroforestry systems on agricultural pro |
| `fan_2023` | https://www.sciencedirect.com/science/article/pii/S0016706123003208 | 3_Water_Harvesting | Fan et al. (2023). The effectiveness of mulching practices on water erosion control: A global meta-analysis. G |
| `zhang_2026` | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5158446 | 3_Water_Harvesting | Zhang et al. (2026). Spatiotemporal effects of soil and water conservation measures on soil organic carbon enh |
| `ruzzante_2021` | https://www.sciencedirect.com/science/article/pii/S0305750X2100214X | 3_Water_Harvesting | Ruzzante et al. (2021). Adoption of agricultural technology in the developing world: A meta-analysis of the em |
| `moges_2011` | https://research.wur.nl/en/publications/review-and-quantitative-assessment-of-ex-situ-household-rainwater | 3_Water_Harvesting | Moges et al. (2011). Review and quantitative assessment of ex situ household rainwater harvesting systems in E |
| `era_an0083_sime_2015` | https://core.ac.uk/download/82197736.pdf | 3_Water_Harvesting | Sime et al. (2015). Agronomic and economic response of tillage and water conservation management in maize, cen |
| `arslan_2015_csa_zambia` | https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/1477-9552.12107 | 3_Water_Harvesting | Arslan et al. (2015). Climate Smart Agriculture? Assessing the Adaptation Implications in Zambia. Journal of A |
| `bruelle_2014_ca_upland_rice_variability` | http://agritrop.cirad.fr/575595/1/document_575595.pdf | 3_Water_Harvesting | BRUELLE et al. (2014). SHORT- TO MID-TERM IMPACT OF CONSERVATION AGRICULTURE ON YIELD VARIABILITY OF UPLAND RI |
| `mashavakure_2025_ca_el_nino_zimbabwe` | https://jpt.ub.ac.id/index.php/jpt/article/download/10713/351 | 3_Water_Harvesting | Mashavakure et al. (2025). Soil, Crop Yield, and Economic Benefits of Conservation Agriculture-Based Cropping  |
| `tadesse_2023_csa_production_risk_review` | https://www.sciencedirect.com/science/article/pii/S266615432300162X | 3_Water_Harvesting | Tadesse et al. (2023). Impact of adoption of climate smart agricultural practices to minimize production risk  |
| `uwizeyimana_2018_water_conservation_rwanda` | https://www.sciencedirect.com/science/article/pii/S209563391730299X/pdf | 3_Water_Harvesting | Uwizeyimana et al. (2018). Effect of water conservation measures on soil moisture and maize yield under drough |
| `zoure_2025_traditional_practices_burkina` | https://onlinelibrary.wiley.com/doi/pdf/10.1155/aess/8855588 | 3_Water_Harvesting | Zouré et al. (2025). On the Performance of Traditional Agroecological Practices in Mitigating the Effects of C |
| `sawadogo_2011_swc_burkina` | https://www.tandfonline.com/doi/pdf/10.3763/ijas.2010.0552 | 3_Water_Harvesting | Sawadogo (2011). Using soil and water conservation techniques to rehabilitate degraded lands in northwestern B |
| `bagheri_2025` | https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/jfr3.70112 | 5_Wetlands_Constructed | Bagheri‐Gavkosh et al. (2025). Hydrological Analysis and Impacts of Natural Flood Management Strategies: A Sys |
| `earl_2023` | https://www.sciencedirect.com/science/article/pii/S004896972301392X/pdfft | 5_Wetlands_Constructed | Earl et al. (2023). A critical review of Natural Flood Management application and spatial prioritisation appro |
| `rowland_2026` | https://besjournals.onlinelibrary.wiley.com/doi/pdfdirect/10.1111/1365-2664.70335 | 5_Wetlands_Constructed | Rowland et al. (2026). Identifying predictors of tropical cyclone impacts on coastal agriculture to assess coa |
| `silliman_2019` | https://research.rug.nl/files/118507594/1_s2.0_S0960982219305500_main.pdf | 5_Wetlands_Constructed | Silliman et al. (2019). Field Experiments and Meta-analysis Reveal Wetland Vegetation as a Crucial Element in  |
| `verhoeven_2009` | https://academic.oup.com/aob/article-pdf/105/1/155/16998009/mcp172.pdf | 5_Wetlands_Constructed | Verhoeven et al. (2009). Agricultural use of wetlands: opportunities and limitations. Annals of Botany. |
| `maxwell_2026` | https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/rec.70458 | 5_Wetlands_Constructed | Maxwell et al. (2026). Restoration and rehabilitation of floodplain wetlands: a systematic, global review of r |
| `wet_restoration_insufficient_soc_recovery_2025` | https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/geb.70063 | 5_Wetlands_Constructed | Wu et al. (2025). Wetland Restoration Is Effective but Insufficient to Compensate for Soil Organic Carbon Loss |
| `wet_mitigation_potential_cost_effectiveness_2020` | https://pmc.ncbi.nlm.nih.gov/articles/PMC7435041/pdf/rsfs20190129.pdf | 5_Wetlands_Constructed | Taillardat et al. (2020). Climate change mitigation potential of wetlands and the cost-effectiveness of their  |
| `wet_ncs_indonesia_wetlands_key_2022` | https://iopscience.iop.org/article/10.1088/1748-9326/ac9e0a/pdf | 5_Wetlands_Constructed | Novita et al. (2022). Natural climate solutions in Indonesia: wetlands are the key to achieve Indonesia’s nati |
| `wet_phosphorus_source_or_sink_meta_2023` | https://iopscience.iop.org/article/10.1088/1748-9326/ace6bf/pdf | 5_Wetlands_Constructed | Ury et al. (2023). Source or sink? Meta-analysis reveals diverging controls of phosphorus retention and releas |
| `wet_paludiculture_projects_indonesia_progress_2020` | https://www.sciencedirect.com/science/article/pii/S2351989419306109/pdf | 5_Wetlands_Constructed | Budiman et al. (2020). Progress of paludiculture projects in supporting peatland ecosystem restoration in Indo |
| `wet_peatland_restoration_economics_indonesia_slr_2025` | https://www.sciencedirect.com/science/article/pii/S2212041624001001 | 5_Wetlands_Constructed | Jalilov et al. (2025). Unveiling economic dimensions of peatland restoration in Indonesia: A systematic litera |
| `wet_peatland_restoration_valuation_kalimantan_2017` | https://research.vu.nl/files/278174690/Combining_focus_group_discussions_and_choice_experiments_for_economic_valuation_of_peatland_restoration.pdf | 5_Wetlands_Constructed | Schaafsma et al. (2017). Combining focus group discussions and choice experiments for economic valuation of pe |
| `wet_community_led_peatland_restoration_sea_5rs_2022` | https://iris.uniroma1.it/bitstream/11573/1622661/1/Terzano_Community%E2%80%90led%20peatland_2022.pdf | 5_Wetlands_Constructed | Terzano et al. (2022). Community‐led peatland restoration in Southeast Asia: <scp>5Rs</scp> approach. Restorat |
| `dongting_eco_compensation_wetland_recovery_2010` | https://www.geogsci.com/EN/PDF/10.1007/s11442-010-0389-1 | 5_Wetlands_Constructed | Xiong et al. (2010). Eco-compensation effects of the wetland recovery in Dongting Lake area. Journal of Geogra |
| `german_peatland_rewetting_economic_assessment_2026` | https://www.tandfonline.com/doi/pdf/10.1080/21606544.2026.2616676?needAccess=true | 5_Wetlands_Constructed | Meyer-Jürshof et al. (2026). From dry to wet: economic assessments of peatland rewetting scenarios in German a |
| `rural_cooling_potential_adaptation_measures_2024` | https://www.sciencedirect.com/science/article/pii/S0301479724015810/pdfft | 5_Wetlands_Constructed | Zimmermann et al. (2024). Assessing the cooling potential of climate change adaptation measures in rural areas |
| `satellite_wetland_induced_local_cooling_2025` | https://www.sciencedirect.com/science/article/pii/S2666017225000987/pdfft | 5_Wetlands_Constructed | Gao et al. (2025). Satellite observation reveals wetland-induced local cooling moderated by regional climate g |
