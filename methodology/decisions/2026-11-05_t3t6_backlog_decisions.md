# T3/T6 backlog — open decisions (5 November 2026)

The T3/T6 extraction backlog is done (PRs #532–#594). These are the questions the extraction rounds left for you. Each has a recommendation. **To answer, reply with the item code and a letter or "yes/no"**, for example `A1: B, A2: yes, C3: as recommended`. "As recommended" for a whole section is fine.

Items you have already settled (Verchot net-CO2e, library swaps for Taufik and the arid-India paper) are left out.

## A. Rules that change many rows (highest impact)

**A1. Does a gain in a dry season make a practice a drought defence?**
Water-harvesting micro-catchments jumped to *high* drought mitigation, mainly on Botoni & Reij's 2007 Burkina season (demi-lunes +112% in a season with 14–23-day dry spells). The same source has a failure under extreme drought (Batodi: nothing harvested at 200–250 mm). Your earlier ruling was that a gain in a rainfall-deficit year is not, by itself, a drought defence.
- **A:** keep as computed (the intensity discount already handles severe failures).
- **B:** cap micro-catchment drought at *moderate* until there is measured evidence across more than one season.
- *Recommendation: B.*

**A2. Is "p = .05" significant?**
Kosmowski 2018 (terraces in the 2015 drought) prints p = .05. Your 5% rule (#51) says 0.05 ≤ P < 0.10 is not significant. Read literally, 4 units become non-significant and the terracing drought row weakens.
- *Recommendation: apply the rule literally (not significant); it is the rule we gave every other lane.*

**A3. Two-arm ratios and range midpoints set "strong".**
Bogie 2018 (shrubs ~10× millet yield in drought) and Vaast 2014 come out *strong* from a ratio between two trial arms. A range like 4–56% (silt clogging) is classed by its midpoint. Rahn 2014's carbon difference (41 vs 16 t C/ha, one plot per farm, no statistics) is also *strong*.
- *Recommendation: keep ratios between two measured arms (that is real evidence); cap single-plot, no-statistics contrasts like Rahn at moderate; for ranges use the lower bound, not the midpoint.*

**A4. Is an implied counterfactual acceptable for recharge?**
Massuel 2014 (percolation tank) and Dashora 2017 (check dams) estimate recharge without measuring a no-structure case; the counterfactual is "the runoff would have left".
- *Recommendation: accept for recharge (it is physically implied) but keep them at low confidence.*

**A5. Several units from one study or analysis.**
Ehui 1990 gives five return units from one simulation. Botoni's 2007 summary (+30–100%) overlaps its own per-technique rows from the same season.
- *Recommendation: collapse Ehui to one unit; drop the Botoni summary unit and keep the per-technique rows.*

**A6. Bundled interventions.**
Pauw 2008 (sand dams) codes crop and income gains as the dam's effect, but dam households also used terraces and small-scale irrigation from dam water.
- *Recommendation: mark them `bundled` (weight 0.6), consistent with the 12 October ruling.*

## B. Single units

| Code | Unit(s) | Question | Recommendation |
|---|---|---|---|
| B1 | Ward 2020 canal blocks | Negative (9.7% of farmers report lower yields) or none (61% noticed no impact)? | **none** |
| B2 | `ipccar6ch5_2` | Cites two papers for "shade cools coffee"; neither says so | **drop** |
| B3 | `mello18_9`, `vannoordwijk21_7`, `patil25_8`, `ribeiro22_1` | The cited source does not contain the claim (they also cite others) | **remove that source from their lineage; keep the units** |
| B4 | Castle 2021 ×7 (dropped) | Certified vs non-certified farms, not agroforestry | **confirm drop** |
| B5 | Haggar 2017 diversity units | Authors say "it is less obvious why" diversity lowers yield | **keep at low confidence** |
| B6 | Ram 2011 carbon | Trees were felled and sold | **drop** (harvested uptake, #39) |
| B7 | MWE 2016 benefit-cost ratios | Ex-ante model, assumed benefits | **keep as modelled** (the modelled-only cap applies) |
| B8 | Roshetko 2002 | Measured and projected carbon comparison from one source | **keep measured only** |
| B9 | Silvopastoral heat → high | Rests partly on a second-hand IPCC claim | **cap at moderate** until a primary is added |
| B10 | Krauss 2009 salt-marsh unit | Filed under wetlands from a mangrove paper | **keep** (the finding is about marsh) |
| B11 | Botoni & Reij figures | `cited_secondary` (national reports) or primary? | **keep cited_secondary** (avoids double counting later) |
| B12 | Binam 2015 | Two tables disagree (P<10% vs P<5%) | **not significant** (the % table, as coded) |

## C. Scope and families

| Code | Question | Recommendation |
|---|---|---|
| C1 | **Losada 2018** (9 modelled flood units held): lift the DOI hold? It overlaps Menéndez 2020 (same model, revised numbers). | **drop**; Menéndez is the published version |
| C2 | **Yang 2019** hedgerows on construction spoil heaps (no crop) | **out** |
| C3 | **Onduru 2008** off-farm Tithonia green manure as "tree biomass transfer" | **out** (no trees in the system) |
| C4 | Live fences in pasture (silvopastoral) vs windbreaks in pasture (linear_boundary) | **both linear_boundary** (it is the boundary planting that matters) |
| C5 | Chen 2019: level ditches → in-situ, fish-scale pits → micro-catchment, though the authors call all six "terracing" | **keep the split** (follows our families) |
| C6 | Merkelbach paludiculture barriers: peatland or restoration_rewetting? | **peatland** |
| C7 | Add a `managed_forest` comparator (Orefice's thinned woodlot is tagged "unmanaged") | **yes** |
| C8 | Somanathan, Jauhiainen and Krauss compare existing forest/peat/mangrove management, not restoration — keep them out of restoration roll-ups? | **yes** (tag existing_forest / existing_wetland where missing) |
| C9 | Gross fishery value per ha of standing mangrove (~10 units) — accept a zero-catch counterfactual? | **no** (levels, #28) |

## D. Vocabulary gaps (variables or routes to add)

Each blocks evidence we have already read:
- `water_table_depth`: needs a direction-sense row and a route (peat canal blocks, biodrainage).
- `establishment_survival`: needs a route (micro-catchment and planting survival).
- `ecosystem_service`: route dung-beetle processes to biodiversity?
- New variables: fish catch / fisheries production; social capital; tree density; air quality (PM10 behind windbreaks); crop labour demand.
- Gender in living-fence adoption: M2b operational stream or Module 6 guidance only?

*Recommendation: add `water_table_depth` and `establishment_survival` routes now (most evidence waiting), fish catch as a variable; defer the rest; gender → Module 6 guidance.*

## E. Different versions of a source

| Code | Source | What is free | Recommendation |
|---|---|---|---|
| E1 | Pinoargote 2016 | the author's thesis (same study) | **accept** |
| E2 | Dixon 2015 | a conference abstract only | **reject** (too thin) |
| E3 | Franzel 2002 | the whole ICRAF book; the chapter is inside | **accept** (cite the chapter pages) |
| E4 | Oweis 1997 | the 2012 second edition | **reject** unless the cited figures are unchanged |
