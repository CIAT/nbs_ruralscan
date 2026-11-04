# Semmens and Witing: bounded T4 recovery inventory

Date: 2026-11-04. Ruleset: v1.9.4. Main-paper reading and source-specific claim accounting only. No human approval; no quantitative response functions. Retrieval packages were consulted, followed by native full-page text and rendered images. Page numbers below are PDF pages, not journal pagination. Original PDFs remain unchanged.

## Result and limits

- Witing: two staged units, for the source's fixed riparian modelling corridor and urban/water exclusions. Both are unreviewed scoping candidates for `riparian_buffer__natural_restored`. Width is 100 m total / 50 m each side; it is not an ecological maximum. No direction of increasing/decreasing establishment suitability is supported.
- Semmens: zero staged EV units; four anchored holds preserve width, stream order, agricultural land-cover mask, and milkweed soil establishment evidence. Family assignment is unresolved because the source combines restoration of natural vegetation and a management range, not one explicit planting/regeneration pathway. Holds are not dropped evidence or human questions prematurely answered.
- Read-only intake manifest confirms original PDF hashes and opening-title matches. Queue DOI verification was checked by the build script. Native page slices are reproducible; no quote retyping or concatenation.
- Main-paper accounting is complete for this bounded T4 pass. Source-wide extraction is not complete: supplements and effect/priority claims remain deferred. Central provenance and scope admission results are recorded in the parent audit directory.

## Semmens page inventory (14 pages)

| PDF page | Content | Disposition |
|---|---|---|
| 1 | Title, abstract, monarch/milkweed conservation framing | Identity and practice context. Abstract benefit estimates not extracted. |
| 2 | Introduction, marginal land, ecosystem services, Minnesota regulation | No new suitability rule. Minnesota 50 feet / 15.24 m is cited jurisdictional policy (MNBWSR 2019), not a universal buffer minimum; defer primary policy verification. Marginal land argument is allocation/value framing, not establishment exclusion. |
| 3 | Study area; scenario development; CDL intersection; milkweed densities | Four claim groups: width/order/land-cover holds (held_claims.json); milkweed density scenarios deferred to species/effect lane. Study crop shares are site context. |
| 4 | Figure 1; milkweed soils; surface-flow filtering | Soil texture/drainage claim held species-specific. Figure 1 depicts scenario footprints, not suitability scores. Channelized-vs-lateral overland-flow filtering is a service delivery condition, deferred to effects/M6; no structural soil rule inferred. |
| 5 | Figure 2; Table 1; headwater and tile-drainage adjustment | Sediment-service contributing-area accounting, not exclusion of headwaters from ecological establishment. All Table 1 state rows retained in deferred_tables.json. |
| 6 | Tables 2–3; erosion/trapping and valuation | Service calculations only. Soil type/slope/land use influence trapping performance, not establishment thresholds. All table rows deferred. |
| 7 | Tables 4–5; pollination distance model | Species flight distances and pollination-service decay, not riparian establishment suitability; all table rows deferred. |
| 8 | Soybean benefits; crop costs; Table 6 milkweed scenario output | Species-specific outcomes, economic assumptions and modeled benefits. Supplementary Table 1 referenced for crop values. No T4 calibration. |
| 9 | Tables 7–11 and results/discussion | Modeled sediment, pollination, conversion areas and monetary trade-offs; all rows deferred. |
| 10 | Discussion of species presence, pesticides, uncertainty, ephemeral streams | Species occurrence is not establishment calibration. Pesticide/landowner management remain M6 pointers. Explicit omission of ephemeral streams is data-resolution limitation, not ecological exclusion. |
| 11 | Conclusion, data and supplement pointers; references begin | No new independent claim. ScienceBase release DOI and publisher supplementary-material anchor recorded below. |
| 12–14 | References and publication end matter | Lineage only; no direct evidence extracted from reference titles. Bowles reference identifies a species-specific primary; do not generalize its content from this secondary paper. |

### Semmens main-paper table accounting

All table rows are preserved as native page text in `deferred_tables.json`, with no table reassembly or ingestion. These are explicit out-of-lane deferrals, not claims that their effect extraction is complete.

| Table/page | Every row accounted for | Destination |
|---|---|---|
| T1/p5 | Michigan, Wisconsin, Minnesota, Iowa, Illinois, Indiana, Ohio, total; crop hectares/headwater percentages/areas | Sediment-service model contributing-area context |
| T2/p6 | Iowa, Illinois, Ohio, Indiana, Minnesota, Michigan, Wisconsin; subsurface drainage area/share | Sediment-service model context; Sugg 2007 lineage |
| T3/p6 | AI Mitigation 5/10/20 m; Yuan 0–3/4–6/>6 m; Hawes forested/vegetated/combined; Dillaha 4.6/9.1 m; Dickey/Vanderholm 91–262 m; Young 24 m | Width/composition-dependent trapping effects; primary references required; not suitability cutoffs |
| T4/p7 | Twelve bee groups/species and average flight distance; all source ranges and derived averages | Species pollination mechanism; no establishment function |
| T5/p7 | All fourteen distance bands, 90 to 2400 m; pollinator-dependent crop and soybean values | Pollination economic distance decay, not suitability |
| T6/p8 | 30 m, variable width, 100 m; habitat area and all three milkweed density scenarios | Species-specific modeled restoration outcomes |
| T7/p9 | MN, IA, IL, IN, OH, MI, WI, total | Modeled sediment baseline, not intervention effect alone |
| T8/p9 | All three buffer scenarios, sediment retained and water-quality value | T3/T6/T6E deferred |
| T9/p9 | All three scenarios, pollinator-dependent crops/soybeans/total | T6/T6E deferred |
| T10/p9 | All three scenarios, converted hectares/gross/net annual crop value | Economic opportunity cost; not suitability |
| T11/p9 | All three scenarios, water quality/pollination/lost crop cost/ratio | Economic comparison; omits establishment costs; not feasibility CBA |

Semmens held soil evidence explicitly says well-drained, fine-textured glacial soils enhance establishment/growth of milkweed. Preserve both qualitative preferred conditions, `claim_scope=species_specific`, taxon only as source-stated milkweed/Asclepias spp. The paper explicitly did **not** use soil composition in its model. Bowles 2015 concerns Mead's milkweed according to the bibliography; primary transfer remains unresolved. No genus-wide numeric curve or general buffer constraint.

## Witing page inventory (16 pages)

| PDF page | Content | Disposition |
|---|---|---|
| 1 | Title, abstract | Identity, catchment-scale optimization context; no abstract extraction. |
| 2 | Introduction and abstract continuation | Prior studies/effect rationale; not new establishment claims. |
| 3 | Study objectives/site and Figure 1 | Site conditions and land-use map, not suitability. |
| 4 | Sampling design and ecological/EPT/diatom/carbon objectives | Outcome variables and sampling context, deferred T3/T6/M4. |
| 5 | Agricultural production objective, corridor geometry, Figure 2 | `ev_riparian_distance_witing22_design_20261104`; other metrics are objectives, not suitability. 300-m segment length is modelling support. |
| 6 | Predictor sets and model selection; management measures | `ev_riparian_landcover_witing22_exclusions_20261104`. Reforestation increments 20/40/60/80/100% are scenarios. DeFor20% explicitly excluded from NbS evidence. |
| 7 | Measure map construction, optimization and initial results | Existing patches expanded; absent patches generated along river: allocation algorithm, not regeneration prerequisite. Four objective functions/Pareto rankings and frequencies are priority method, deferred M4. |
| 8 | Table 1; model evaluation and trade-offs | Every predictor row inventoried below; effects on outcomes, not suitability direction. |
| 9 | Figures 3–4 | Pareto trade-offs and management-option dominance; legends are outcome/frequency scales, not suitability ratings. |
| 10 | Results and Figure 5 | Forest-cover changes and regional priorities; urban restriction consistent with p6 unit, no duplicate independent evidence. |
| 11 | Discussion of trade-offs and spatial planning | M4 and M6; no universal establishment preference inferred. |
| 12 | Limitations and recommendations | Fixed width simplification explicitly challenged; 100 m only upper modelling boundary, potentially larger relevant width. Width >50 m discussion is speculative dimensioning of modeled performance, not calibrated minimum. |
| 13 | Conclusions, data release, references start | Stakeholder/policy feasibility next steps. Data release requires separate intake. |
| 14–15 | References | Lineage, no new extracted claims. |
| 16 | References, support notice and citation | Referenced supplements unresolved; source not declared swept. |

### Witing Table 1 (p8): all eleven predictor rows

Arrows describe response-variable effects, not establishment suitability. Interaction tags and units retained in native page text (`deferred_tables.json`) and checked on rendered p8. Entire table routes to effect/priority method inventory, not T4 EV.

1. Local forest & shrub share [%]: EPT up (*1,*2), carbon processing/permanence up, diatom diversity up (*4,*5).
2. Local pasture & grassland [%]: carbon processing/permanence down; agricultural production up.
3. Local arable land [%]: carbon processing/permanence down (*3); agricultural production up.
4. Upstream riparian forest & shrub [%]: EPT up (*1).
5. Upstream distance between 100-m forest blocks [m]: carbon processing/permanence down (*3), diatom diversity down (*5). Do not rename this silently to nearest forest distance.
6. Upstream catchment urban-industrial [%]: EPT down.
7. Local elevation mean [m]: diatom diversity down.
8. Local elevation gradient [m]: EPT up; not degree/percent slope.
9. Local biophysical food-production suitability [%]: agricultural production up; not tree establishment suitability.
10. Upstream catchment size [m, as printed]: diatom diversity up (*4). Source unit suspect; no silent square-unit correction.
11. Upstream elevation gradient [m]: EPT up (*2).

Table model evaluation row retained: R2/adjusted R2/P values describe fit, not criterion weights. No source importance weights assigned. Five matched interaction pairs must remain coupled in any future effect-model reading.

## Supplements and datasets: explicit holds

- Semmens p8 Supplementary Table 1: crop yield/price data; p11 publisher anchor `https://www.frontiersin.org/articles/10.3389/fenvs.2019.00126/full#supplementary-material`. Not acquired here; format not verified. Economic data outside this T4 batch. Do not ingest until approved format/adapter established.
- Semmens p9/p11 ScienceBase data release `10.5066/P9DV375U`: state-specific costs/benefits and geospatial outputs; no companion data ingest.
- Witing p4 S1–S3: field-sampling protocols; p5 S1 cotton-strip assay and S4 spatial delineation; p6 S5–S7 explanatory-variable definitions and S8 selection/preparation; p7 S9 map translation and S10 optimization; p7–8 S11 model details and S12 convergence; p8 Figure S13 Pareto display; p9 S14 mapped-scenario target values. Main-paper pointers preserved; supplementary content not inspected, format not verified in this agent task.
- Witing p13/p16 data release `10.5281/zenodo.6412402`; known mixed dataset ZIP intake remains paused. No data files acquired, expanded or registered.

## Visual and omission checks

Rendered and visually inspected Semmens pp3,4,6,7,9 and Witing pp5,6,8,9,10. Images remain in local gitignored staging; source/page references and render hashes are recorded in the parent audit directory. Checked both-column text continuity, table headers, row/column relationships and legends. Witing Table 1 has outcome arrows, never suitability colours. Semmens Figure 1 only maps buffer scenarios; does not resolve variable-width side convention. Witing Figure 2 supports total corridor units; Figure 4 colours denote measure dominance, Figure 5 forest shares/change.

Independent omission pass compared full native text, all 11 Semmens tables and Witing Table 1 against the retrieval package. Automated index table counts are not coverage denominators (Semmens manifest says 5, but paper has 11; Witing says 2, paper has one numbered table). Four Semmens held claim groups preserve claims that cannot yet receive a family. No source-specific weights, missing calibrated direction, or ecological cutoffs were silently inferred. No reviewed IDs overwritten, no JSON/register generation performed by this agent.
