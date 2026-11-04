# Amichev2020 shelterbelt suitability: complete main-paper T4 inventory

All31 main-paper pages read; source matches queued title, authors, journal/year, DOI and31-page extent. No existing SRC/EV identity found, nor extraction in current audits or shared/main staging. Acquired queue row is DOI-verified and points to team-library copy. Native opening title checked. Source remains unregistered; no writes beyond this staging directory.

## Result and limits

24 unapproved source-direction/model-use units: eight existing canonical variables, each represented separately for deciduous, coniferous and shrub shelterbelt groups. All use existing `agroforestry__linear_boundary`, `species_specific` and explicit pooled-group taxon lists from Table2. These are three modeled species-group populations, not three independently validated studies or individual-species response estimates. Zero practice-general units; zero executable curves; no claim that F4 extraction/approval is complete.

Mapped variables: mean annual temperature, annual precipitation, clay fraction, available water capacity, pH, bulk density, elevation, distance to water. Source-native soil depths retained. Opposing species-group signs preserved. `criteria_inventory.json` accounts for **all50** input rows and all150 group sign/loading/rank cells, includingnominal class IDs, source distributions and rounded-zero weights. No source range interpreted as a suitability cutoff. All50-member criterion set retained, while source-specific percent loadings remain separate from runtime weights.

Table quotes use three separately anchored excerpts: native selected row as `quote`, full Table3 caption/header atPDF18 as `justification_quote`, and rank/sign/membership semantics atPDF21 as `selection_justification`. No stitched quotation or duplicated whole-table quote. Context identifies column order and exact group; central compatibility of these anchored table contexts remains for review.

## Complete objects and page coverage

|Pages|Object|Disposition|
|1–3|Identity, abstract, introduction, scope, study region|Title matches. Planted shelterbelts for agricultural landscapes; site coordinates/area are context, not suitability limits. Secondary introductory benefits not effect extraction.|
|4–8|Table1, all50 input rows in four categories|Complete input inventory. Climate21, management13, soils14, topography2; no input mention omitted. Detailed source definitions delegated to OnlineResource1/S1–S4, currently unavailable locally.|
|4|Figure1, shelterbelt length/age/carbon/census maps|Observed-distribution and carbon-stock proxy construction, not suitable/unsuitable thresholds.|
|9–10|Methods,299 census subdivisions, PCA/PCR|Predictor averages and carbon totals; standardized inputs. Carbon proxy combines age×length×species/soil-zone addition rates. PCA/PCR correlations do not prove independent establishment causation.|
|11|Table2,31 soil-zone/cluster rows, six species and grouped rates|Full table retained in page11.txt. Growth/carbon proxy inputs and species-group definitions. No T4 numeric threshold; no effect units or duplicate independent support from companion studies. Mixed group is not a separate modeled suitability map.|
|12–13|Figure2 and fuzzy/weighted overlay methods|All50 layers used. Positive reported loading selects fuzzy-large, negative selects fuzzy-small; source weights are percent of total loadings. Midpoint/spread absent. Reclassification to five output suitability levels not an input-variable response.|
|13–15|PCA/PCR results,Figure3|Components explain source predictor variation; source regression significance identifies components, not each individual variable effect. No component weight assigned wholesale to variables.|
|16|Figure4, first six PC stacked loadings|Method illustration:72% explained variation; not complete50-variable source weighting alone. Table3 full output supersedes visual approximation; no bar digitisation.|
|17–21|Narrative and Table3,all50 rows and six footnotes|All input distributions, signs, loading percentages,ranks retained in criteria_inventory.json. Eight canonical variables×three groups staged; remaining rows held with exact ontology, categorical or scale reason, not discarded.|
|21|Footnotes:9crop classes,6hardiness zones,6capability classes,3drainage classes,5erosion classes,4texture classes|All native footnotes retained in page21.txt. Codes are not continuous ecological values. No class ordering converted to a hard mask.|
|22|Figure5, three maps plus evaluation and area charts|Model output and internal inventory evaluation; no new independent study. Caption's above-average0.4–0.8 overlaps average0.4–0.6: retain as source inconsistency, do not repair silently.|
|23–24|Table4,5soil zones×5suitability classes plus totals×3species groups×with/without/total area|All rows retained in native pages; mapped land-area outputs, not pixel footprint of planted linear shelters. Never count reported area as actual shelterbelt area.|
|25–26|Suitability evaluation/discussion|Same inventory binned by suitability, not out-of-sample validation. Low-suitability deciduous class excluded in parts of Gray/DarkGray; reported area discrepancies retained.|
|27–29|Species-zone recommendations,transfer discussion,conclusions|Regional group selection, not universal family thresholds. Willow short-rotation coppice transfer suggestion is separate practice/cultivar scope. Climate/drought discussion contains secondary effects, deferred outside this T4 batch.|
|30–31|Funding,COI,references,affiliations|AAFC funding,authors declare noCOI. Companion Amichev2015/2016/2017/Piwowar2017/Sealey2019 are lineage inputs, not sources newly acquired/read or independent validation.|

## Holds requiring source/method work

1. **Supplement Online Resource1** explicitly named onp1/p4, including TablesS1–S4; no matching supplement found alongside main PDF or in cache/OneDrive filename inventory. Not web-recovered in this bounded pass. Do not claim source complete or that supplement lacks parameters.
2. **Algorithm wording:** p10 claims signed sums of squared eigenvectors; negatives are mathematically inconsistent. Source Table3 signs are explicit and p13/p21 explains directional meaning, so retain reported directions; cannot reconstruct signed weights or publish exact algorithm without clarification.
3. **Calibration:** main table min/max are observed predictor ranges across census subdivisions. No fuzzy midpoint/spread; no defaults invented. Rounded zero loadings retain signed source label with precision warning.
4. **Species scope:** all maps and loadings are group-specific, often opposite. Lists are source groups, not separate single-species units. No pooling into generic shelterbelt suitability.
5. **Nominal classes:** crop/capability/texture and drainage codes need semantic mapping; class numbers are not physical gradients. Full footnotes retained.
6. **Proxy mismatch:** SOC stock vs concentration; exploitable soil depth vs bedrock; aridity formula unverified; seasonal/extreme measures vs annual mean; soil fractions vs USDA classes. Every affected row has explicit inventory hold.
7. **Validation/transfer:** carbon proxy and same-inventory evaluation, geographic Canada/high-income scope and management confounding limit transfer. No validation metric or correlation is a runtime suitability score.

## Review and next action

Prepare.py equivalent is `build.py`: deterministic index with tables, source-row slices,24 EvidenceUnit objects, native anchors,50-row inventory, local validation and duplicate check. Source intake metadata and six-axis rationale in source_metadata.json. Orchestrator handles source registration/promotion, central gates, independent review and retrospective. No source stage or human review completion stamped. Further work is supplement retrieval/mapping decisions, not rediscovery of the main article.

Validation follow-up: deterministic number/context/direction/quote/species/scope/BANDS checks pass with zero flags. Table2 group membership and Table3 all four pages visually checked (PDF11,18–21). Independent inventory reviewer found no blocking defect in24units/50criteria; see sibling inventory/AMICHEV_REVIEW.md. Human review and source-registration gate remain separate.
