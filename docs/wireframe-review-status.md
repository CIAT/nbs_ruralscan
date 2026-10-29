# v1 feedback implementation record

29 October 2026. This record covers the revised **v1 draft**, not the preserved v0. It records implementation, not stakeholder approval. Overall assessment: **3/5 towards the full feedback set**. The walkthrough and bounded examples are substantially stronger; the evidence-led response/configuration surfaces remain incomplete.

Scores: 1 = barely addressed; 2 = partial explanation; 3 = usable illustration with material gaps; 4 = demonstrated with bounded limitations; 5 = requested demonstrator behaviour fully checked and reviewed. Scores assess the visual method illustration, not analytical readiness. No real schema tables or runtime outputs are connected.

## Prioritised action table

Multiple actions can remain on one row. “Demonstrated” means browser-checked at example grade; it does not mean an approved method, real dataset or stakeholder sign-off.

| Request / priority | Progress /5 | Actions implemented in v1 | Remaining actions, in priority order |
|---|---:|---|---|
| Background, project aims and tool purpose — P1 | 4 | Landing explains rural NbS, investment-scoping gap, intended users, project deliverables and the wireframe's purpose before objectives. | **P1:** Pete checks whether the explanation answers a first-time reader's questions. |
| Explain each stage and simplify — P1 | 4 | Six original stages retained; each has a question, introduction and numbered/disclosed sections. Active stage and shared controls remain visible. | **P1:** First-time TTL walkthrough; tighten remaining long tables and repeated caveats based on actual confusion. |
| Objectives before interventions — P1 | 4 | Two editable objective presets; selected objectives carry into hotspots and brief. Custom combinations explicitly have no illustrated ranking. | **P1:** Agree the intended objective-to-variable relationship; demonstrate contributions once agreed. |
| Optional data-first configuration — P1 | 3 | Contextual returnable workspace under Setup, data inspection before analytical treatment, two variable surfaces and six card slots. | **P1:** Add concrete dataset-selection and local-override examples; show categorical gates separately from quantitative responses. **Dependency:** response curves/raw-transformed maps await agreed contract. |
| Correct suitability and operational factors — P0 | 4 | Roads/access support do not alter opportunity; operational questions stay with Project Risk and hand-off. No universal slope threshold. | **P1:** Method owners verify the screen-to-method wording, including hard masks and context overrides. |
| Shared selection and full labels — P1 | 4 | One state for viewed practice, suitability classes, climate and geographic view; hotspot classes remain separate. Three practices compared under common scope. | **P1:** Broader multi-practice selection/geography configuration remains outside this single-country example; avoid presenting three fixtures as full recipe support. |
| Excluded, unknown and context areas — P0/P1 | 3 | Separate classes; context overlay; explanation rejects universal protected-area/wetland bans. | **P1:** Add one sourced, recipe-specific legal exclusion with an inspectable reason and local challenge route. Current spatial marks are synthetic. |
| Map cells, Admin 2/3 and 100-ha example — P1 | 4 | Shared views, denominators, zoom/recentre, administration summaries and coarse-grid illustration. Admin 3 is explicitly invented quadrants. | **Dependency:** Official Admin 3 data and actual raster/mask semantics/resolution verification. No real small-AOI capability claimed. |
| Need versus response; evidence explanations — P1 | 3 | Need, response strength and confidence separated. Information panels explain units/denominators and missing data. One EV→SRC→page example with transfer caveat. | **P1:** Provide verified practice-matched response and confidence examples; expand information panels to every real input after alignment. **P1:** Confirm the cited unit's review status before using it as approved evidence. |
| Climate comparison and timing — P1 | 4 | Baseline/future/difference fixture, named periods/scenario, explicit baseline denominator in difference mode. No intervention counterfactual or delay-cost claim. | **Dependency:** Actual output contract and future hazard/vulnerability treatment. Hazard flags stay fixed in this example. |
| Hydrology — P1 | 3 | Worked path from water need to possible response, uncertainty and commissioning questions; recharge/yield/quality distinguished. | **P1:** Add a verified, selected-practice hydrological effect example and associated data fitness statement. Detailed water-balance modelling remains downstream. |
| Individual hazards and overlap — P0/P1 | 4 | Fire, flood and intersection views with consistent scope/admin summaries. Unsupported overall risk rating and complement-of-mitigation logic removed. | **P1:** Add authoritative asset/establishment-vulnerability example. Do not infer vulnerability from an intervention's mitigation effect. |
| Risk trade-off at shortlist — P1 | 4 | Keep-with-flags versus defer-overlap scenario; before/after area and residents visible; structural opportunity unchanged. | **Dependency:** Agree actual filter criteria; intersection is explicitly an illustrative choice, not an endorsed exclusion rule. |
| Gender and equity — P1 | 4 | Context-only toggle; counts/rankings unchanged; local rights and equity remain in hand-off. | **P1:** Link an appropriate national context source. Subnational differentiation requires separate data/method agreement. |
| Comparison and double counting — P0/P1 | 3 | Common-scope footprint/need table, pairwise agroforestry–restoration overlap, residents not beneficiaries; no compatibility verdict. Linear bund view reports applicability zone only. | **P1:** Practice-specific response/confidence comparison; expand overlap to any supported practice combination. |
| Five Bank indicators — P1 | 3 | Five-row crosswalk with official reference links and context/contribution/not-estimated status. | **P1:** Resolve protected terrestrial/aquatic share's official status, definition and denominator; verify ecosystem dataset mapping. No achieved results claimed. |
| Local budget and affordable hectares — P0/P1 | 4 | Editable currency/year, establishment, maintenance and fixed costs; same budget across two area practices, ceilings, two cost cases; linear bunds excluded from hectare returns. | **P1:** Add reviewed contextual cost evidence/ranges; current defaults are explicitly invented. No production economics or currency conversion promised. |
| Unsupported economics and benefits — P0 | 4 | Removed asserted BCR/payback/carbon-cost/local benefit results. Optional return/reach require user assumptions; residents never substituted. | **P1:** Clarify uptake, timing and transfer for any future literature example. Detailed CBA remains downstream. |
| Downloadable map and prose — P1 | 4 | PNG with colour legend, scope, scenario and provenance; three-paragraph brief with Admin 2 locations, assumptions and limits; copy/download work. | **P1:** Add verified response/evidence prose once approved. Cross-browser/mobile export checks remain. |
| Local co-production and stopping point — P1 | 4 | Clear scoping end; partner validation, rights, adoption, feasibility and monitoring questions. | **P1:** Curate practice-specific downstream resources; avoid creating a new feasibility deliverable. |
| Learn about this NbS — P1 | 2 | Two contextual agroforestry references and evidence workspace link; transfer limitations explicit. | **P1:** Expand to curated, practice-specific effects, economic context and conditions for forest restoration and water harvesting; references should track viewed practice. |
| AI concepts — P2 | 3 | Scripted report/input/evidence interactions; proposals require review; file references stay local/unread; no live model. | **P2:** Improve examples using approved evidence and a concrete proposed change diff. Live service is not required or promised. |
| Save/load project and result — P2 | 4 | Versioned local JSON stores controls, assumptions, fixture identity/provenance and result snapshot; matching-version restoration demonstrated. | **Dependency:** Actual run manifest/version/output contract. No pipeline execution or real analysis archive claimed. |
| Front/back-end alignment — deferred | 2 | Dev Notes map each screen to modules, tables, intended outputs and missing contracts. | **Dependency:** Wait for T4–Diego work, review identifiers/units/product type/masks/transformations and provenance, then decide whether to connect read-only tables. |

## Bank acceptance checks

These retain the B01–B16 identifiers from the revision plan. No row is labelled fully closed pending stakeholder review.

| Check | Status in this draft | Remaining boundary |
|---|---|---|
| B01 Objectives upfront | Visual behaviour demonstrated | Actual variable/weight mapping pending. |
| B02 Active stages / overload | Main journey demonstrated | Full TTL usability check and dense admin-table simplification. |
| B03 Meaning / calculation / source | Partial | Explanation patterns exist; real response previews and per-input coverage incomplete. |
| B04 Climate / timing | Visual behaviour demonstrated | No avoided-loss or cost-of-delay inference. |
| B05 Exclusions / adjacency | Partial | Overlay demonstrated; recipe-specific legal evidence pending. |
| B06 Individual / overlapping hazards | Visual behaviour demonstrated | Synthetic flags, not severity/probability or overall risk. |
| B07 Gender toggle | Behaviour demonstrated in hotspots | No actual gender dataset; national context cannot rank districts. |
| B08 Five indicators | Partial | Fifth indicator's definition/status and ecosystem mapping unresolved. |
| B09 Local economics | Arithmetic demonstrated | Local evidence and prices unvalidated. |
| B10 Budget across NbS | Arithmetic demonstrated | Two area practices only; bund zones are not installed hectares. |
| B11 Downloads | PNG and text opened and checked | Production exports and broader browser matrix not claimed. |
| B12 Project-document prose | Partial | Scope, Admin 2 locations, hazards and costs included; approved effects prose pending. |
| B13 Scoping boundary | Visual response demonstrated | Local validation remains downstream. |
| B14 Small vectors / rasterisation | Concept demonstrated | Actual supported resolution/masking remains with runtime owners. |
| B15 Hydrology | Partial | Need-to-study pathway shown; selected-practice response evidence pending. |
| B16 Risk choice | Before/after example demonstrated | Filter criterion is an illustration awaiting method agreement. |

## Validation evidence

Browser checks against local v1 on 29 October 2026:

- Shared practice/class/climate controls update opportunity, risk, shortlist, comparison and brief. Empty suitability scope shows zero area and unavailable percentages, not NaN.
- Default climate/livelihoods shortlist: 1,970,000 nominal ha / 137,230 fictional residents. Optional overlap deferral: 1,022,500 ha / 81,890 residents; opportunity remains 2,967,500 ha. Gender toggle leaves these values unchanged.
- Biodiversity/water preset gives a different retained example footprint. Future water-harvesting view explicitly says applicability zone, not treated area. Admin 3 table explicitly says schematic quadrants.
- USD 1m, USD 100k fixed, five maintenance years: agroforestry 2,000 ha establishment-only versus 1,384.6 ha fuller cost; restoration 1,000 versus 720 ha. Raising agroforestry establishment cost to 1,000 gives 1,000 versus 782.6 ha. Fixed cost above budget gives zero fuller-case area; zero unit cost rejects the calculation.
- Local result download reopened after reload, restoring water-harvesting/future/biodiversity-water/risk-filter/gender-hidden settings. Example state/provenance inspected in JSON. No pipeline ran.
- PNG opened with coloured legend, unclipped coastal labels, selected scope/scenario and synthetic-data notice. Text brief opened with assumptions, retained Admin 2 footprints and provenance. Copy action succeeded.
- Information dialog closes with Escape. Contextual technical workspace returns to originating stage. Version selector returns to preserved v0 and revised v1.
- JavaScript syntax, local asset/link targets, duplicate HTML IDs and whitespace checks pass. No browser console errors during revised-v1 interaction checks.

Not yet checked: exhaustive accessibility audit, mobile/cross-browser matrix, every AI/invalid-import path, stakeholder comprehension, actual analytical correctness. No schema/backend changes were made. v0 body and pinned behaviour remain unchanged except shared release notes.
