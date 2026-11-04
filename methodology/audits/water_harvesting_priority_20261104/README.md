# Water-harvesting High-tier stocktake reconciliation — 4 November 2026

The fixed **11 High-tier records** have been checked against primary PDF methods and current intake: **five new method candidates, two canonical-source reuses, two holds and two referrals**. The original pool has 85 records (11 High, 52 Medium, 22 Low); the remaining 74 were not screened here. This closes a bounded priority-stocktake pass, not the literature or every family.

All 11 PDFs exist in the shared stocktake library. The manifest records Crossref citations, opening-title checks, library paths and SHA256 hashes. Filenames are not authoritative: the Kumar filename resolves to Rai et al.; de Mendonça is a 2025 issue with a 2024 DOI/stocktake label. Singh and Vema retain their historical canonical IDs despite misleading names; their queue aliases are not new papers.

## Decision boundary

Retain runoff-catchment **applicability zones**, distinguishing surface storage from groundwater recharge and each structure's conditions. Sources support opposite permeability directions for storage and recharge, not one pooled curve. No family split, analytical threshold, evidence approval or T3/T6 change is made.

The 36 groups in criteria.csv are an audit inventory, **not EV units**. existing_evidence_review.json references ten existing unapproved EV rows. These are **review referrals, not machine-enforced synthesis blocks**. Existing EV and review decisions remain unchanged. Vema's problematic numeric interpretations remain unresolved until the evidence workflow reviews/corrects them; this audit does not fix those rows.

## Source decisions

| Source | Decision | Finding and transfer limit |
|---|---|---|
| Rai 2018 | M2/M3 referral | Basin morphometry and LULC change; p. 14 classification accuracy is not harvesting-structure validation. |
| Adham 2018 | New candidate | Storage-dam siting, pp. 3–5, 7. Table 1 has nonmonotonic runoff scores and no stream-order 4 class. Engineering sizing belongs in M6; not every dam qualifies as NbS. |
| Alene 2022 | New candidate | Pond/check-dam conditions, pp. 5–6. Printed slope class is literally “8-May”. Validation includes two failed ponds and ten functional structures; some functional structures occupy restricted zones (pp. 12–13). |
| Bera 2023 | New candidate | Structure placements, pp. 13–14; slope is degrees, not percent. Groundwater depth expresses alternative-supply demand (p. 12). Storage/infiltration explanations conflict for some geology/landform classes (pp. 10–11). |
| Hassan 2025 | Hold | Generic RWH map leaves technology unresolved. Table 5 labels groundwater depth m.a.s.l.; local restrictions and score conventions need clarification. Code available by request (p. 21), not verified public code. |
| Jha 2014 | New primary-method candidate | Table 1 p. 7 distinguishes ponds, ground/stream percolation and check dams. Based on past studies and regional experience; potential-index weights are local (p. 13). |
| de Mendonça 2025 | M4/agroforestry referral | PES watershed restoration targeting, not harvesting-structure establishment. |
| Singh 2017 | Canonical reuse | Seven EV rows under mahmoud_2016_mcda_gis_wh_recharge. Table 6 cites Jha. Table 3 is native p. 3 and Table 6 p. 6: existing page numbers are correct. |
| Terêncio 2017 | New candidate | Ex-field storage allocation, pp. 3–6, includes potentially engineered dams. Separate supply-demand, ecological priorities and engineering sizing. Protected-area priority is not construction permission. |
| Vema 2019 | Canonical reuse | Three EV rows under singh_2019_fuzzy_wh_structure_rainfed. Input memberships feed joint rules; endpoints are not standalone absolute suitability limits. |
| Zheng 2023 | Hold | Printed slope classes include negative slope and 0–76.915 degrees while prose favors gentle slopes. Rank/label conflicts and inconsistent totals remain. Table 5 contains coordinates, not siting criteria. |

## Human-review priorities

1. **Vema joint logic.** Table 2 p. 4 defines low-slope [0,0,5,10] and low-permeability [0,0,12,48] cm/day input trapezoids. Twenty-seven joint rules generate structure outputs. Existing abs_max=10 and abs_max=48 interpretations must not be approved as unconditional limits. High-runoff CN is also an input, not an independent necessity: an illustrated medium-runoff rule yields high storage suitability. Four example rules are printed; the full executable rule set was not verified. Review all three EV rows together.
2. **Jha → Singh lineage.** Review four Table-6 EV rows for conditional slope, soil, cover and stream order; review three Table-3 rows separately as local index components. Singh adds wasteland to ground-percolation cover where Jha names degraded forest. Preserve differences and avoid independent-vote inflation.
3. **Storage versus recharge.** Low permeability favors storage, while recharge favors permeability. Bera's valley-fill explanation is mixed. Establish purpose before pooling directions.
4. **Numeric integrity.** Preserve Alene's malformed class, Adham's missing class, Hassan's groundwater-unit ambiguity and Zheng's printed inconsistencies. Do not invent corrections.
5. **Evidence roles.** Groundwater scarcity, population, wildfire priority, access and town proximity are demand/operational context unless a justified hard exclusion exists. AHP consistency is not ecological calibration.
6. **Geometry and validation.** Vema p. 8 restricts check dams to drainage lines even where raster suitability is widespread. Existing-site agreement, small functionality samples, sensitivity and local ROC scores are not universal performance calibration.

## Credibility

Inherited High labels are preserved. Candidates receive a **provisional Medium methods tier**; existing SRC tiers are not overwritten.

- Strength: explicit spatial methods, mainly existing-location agreement and sensitivity. Alene's functionality sample is small and imperfectly separated. Bera reports AUC 0.874 against 52 existing check dams, not validation of every proposed structure.
- Transparency: primary structure tables and fuzzy memberships are inspectable; incomplete rules, malformed classes and generic scope limit reproduction.
- Authority: journal publication does not make a threshold an engineering standard or ratified rule.
- Transferability: retained cases span Iraq, Ethiopia, India and Portugal. Localize soils, runoff, drainage extraction, scale and demand; Portugal does not establish LMIC validation.
- Recency/seminality: Jha is a traceable precursor to Singh; no formal seminality premium inferred. Newer held papers remain held.
- Independence/COI: shared rules and author-led model checks are not independent replications. No unverified COI clearance or causal-effect claim is made.

## Codebase check

[AMERTA](https://github.com/sitasatu/AMERTA) was inspected at commit 7b0be43778dd7732601893b004778c4e5d576a65. Actual scoring implementation, TWI preprocessing and README were read; file paths/hashes are in tool_audit.json. Weights are fixed at 0.30 rainfall + 0.30 TWI + 0.20 land cover + 0.20 soil; missing scores become zero. TWI cuts are 0/5/10/15; the documented default score conflicts with the function at TWI=0. No scientific validation or threshold provenance was established in inspected files.

This is an implementation referral, not approved T4 evidence. No code was executed or copied into runtime. README and header license versions differ and need reconciliation before reuse. HydroHarvest was excluded at search-result screening for rooftop focus. Vema's paper was located, but complete public code/rules were not verified; this does not prove absence.

## Coverage and next gate

Stock: 11 retrieved/screened, seven candidates before dedupe (five new + two reuse). Tools: 17 returned links, three selected targets screened, one repository inspected, zero T4 candidates. Fresh literature and grey channels were not searched. English queries only; multilingual, GitLab, wider repositories and supplements remain outside the cap. Incidental literature results were not promoted.

Registered actual generic protocols without overwriting historical family status. New sources remain pending formal intake despite existing shared PDFs. Next gate: targeted human review and evidence-first extraction, not another unrestricted search.

AMERTA hardcoded parameters are genuine design-choice claims, not measured findings. Retain their pinned locations for later expert_assertion extraction after retention-pond/NbS scope and file-level intake review; lack of validation alone does not erase a tool claim. This discovery audit does not perform that extraction.

Repository acquisition was also run through nbs_ruralscan.ingest.github on the analysis and preanalysis subdirectories (five source files; empty package initializers and PNG assets excluded). Its heuristic returned zero parameter matches despite the manually verified scoring expressions. Zero scanner hits must not be reported as no analytical rules.
