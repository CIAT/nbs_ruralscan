# v1 feedback implementation record

29 October 2026. This record covers the revised **v1 draft**, not the preserved v0. It records implementation, not stakeholder approval. Overall assessment: **3/5 towards the full feedback set**. The walkthrough and bounded examples are substantially stronger; practice-specific readings now illustrate response and transfer limits. Reviewed synthesis, locally matched costs, supporting AI examples and stakeholder usability review remain incomplete.

Scores: 1 = barely addressed; 2 = partial explanation; 3 = usable illustration with material gaps; 4 = demonstrated with bounded limitations; 5 = requested demonstrator behaviour fully checked and reviewed. Scores assess the visual method illustration, not analytical readiness. No real schema tables or runtime outputs are connected.

## Modular delivery queue

Each module gets a bounded diff, browser checks and its own PR. Earlier modules remain usable without later modules. This queue does not authorise or claim live analytical integration.

| Order | Module | Status | Completion boundary |
|---|---|---|---|
| 1 | Dataset inspection and response teaching examples | Merged in PR #496 | Two dataset surfaces, local proposal comparison, six-slot cards, raw/response illustration, compatible save/load. Actual bindings remain deferred. |
| 2 | Safety-critical evidence examples | Merged in PR #497 | Source-linked activity/permission example and establishment-risk guidance; applicability checks explicit, with no mapped legal determination or numerical vulnerability claim. |
| 3 | Practice-specific effects and resources | Merged in PR #498 | Matched response/confidence examples, hydrology and learning resources for each demonstrated practice; follow review state. |
| 4 | Economic context and Bank indicators | Merged in PR #499; matched agroforestry cost gap remains | Contextual cost evidence; remaining indicator definitions and denominators; qualified brief prose. |
| 5 | Usability and consistency | Implemented; bounded browser checks passed | Dense admin summaries, multi-practice overlaps, mobile/keyboard and remaining export/import edge cases. Pete/TTL comprehension review stays separate. |
| 6 | Supporting AI examples | Next | Concrete evidence-backed proposal diff; no live service commitment. |
| Hold | Real table/runtime alignment | Deferred | T4–Diego contract settled and checked before any connection. |

### Module 1: dataset inspection and response examples

- Added a separate presentation module, `wireframe-inputs.js`, reached only through the existing optional technical workspace.
- Published catalogue examples: Copernicus GLO-30 2024_1 for elevation/derived slope and World Bank SPID for poverty. Provider descriptions checked on 29 October 2026. Neither is claimed as the configured project binding; country/AOI access and fitness are unverified.
- Fictional local alternatives expose year, units, coverage, grain, missing provenance, endorsement and compatibility checks. The before/after review table distinguishes a dataset/context proposal from analytical rules; no Apply control or live input change exists.
- Four treatment types are separate: quantitative response, categorical host-system gate, confirmed legal mask and operational condition. Priority input, national context, correlation/weights and investment-risk choice are separately explained.
- Six Variable Card slots retained. Slope raw/response tiles and step profiles reuse **hypothetical** scenarios 07–08 of the existing method example. No new analytical threshold is adopted. Missing cells remain Unknown; Low versus Unsuitable disagreement never creates a legal mask. Priority preview demonstrates why repeating a national value cannot rank districts.
- Browser checks: both local candidate cards, source A/B response change, all six slots, unchanged opportunity total (2,967,500 nominal ha), priority context-only preview, new settings round-trip and old-result compatibility. No console errors. Syntax and whitespace checks pass. Actual family-specific curves, context bindings and evidence approval remain pending.

### Module 2: exclusion applicability and establishment risk

- Added a separate read-only `wireframe-safety.js` module. No classification, mask, risk criterion, schema or evidence register changes.
- Opportunity Space has an **Activity-specific exclusion example** dialog: [Sierra Leone Wildlife Conservation Act 1972, section 20, printed p. 8 / PDF p. 11](https://faolex.fao.org/docs/pdf/sie41659.pdf#page=11). The published provision was inspected, including its designation interval and written-permission exception. The example is conditional on the proposed activity, not a blanket protected-area ban. **Current consolidated law, parcel applicability and permission status remain unverified.** No real area is declared legally excluded by this example.
- Dialog separates confirmed restriction, unresolved applicability and presented authorisation, then gives a concrete local challenge route. Practice-specific prompts distinguish new cultivation, restoration site preparation and bund works.
- Project Risk adds [FAO forest-restoration guidance](https://www.fao.org/sustainable-forest-management-toolbox/modules/forest-restoration/), locator: “Monitor and maintain forest management”, Table 3 and following prescribed-burns paragraph. Source support, our scoping interpretation, practice transfer and unavailable numerical inference are separate. This is practitioner guidance, not a newly approved EV/T3 record.
- Fire guidance is identified as a direct planted-forest context, an agroforestry transfer question, and unmatched to bund structures. Selecting Flood or overlap explicitly exposes the hazard mismatch. It supplies no local loss rate, safe establishment age or overall risk score.
- Legal and asset questions follow the selected practice into Next Steps and the downloaded brief, retaining source links and unverified status.
- Browser checks: legal dialog/Escape, unchanged default opportunity (2,967,500 nominal ha), forest/fire context, water-harvesting/flood mismatch, dynamic hand-off and downloaded brief contents. Screenshot inspected; no console errors. JavaScript syntax, local targets/duplicate IDs and whitespace checks pass.

### Module 3: practice-specific effects, hydrology and resources

- Added read-only `wireframe-evidence.js`. Response dialogs, hydrology, comparison, learning links, scripted answer and downloaded brief use one curated example per selected practice. No schema, evidence-register or analytical changes.
- Primary passages checked on 29 October 2026: [Chalupecká et al. (2026)](https://link.springer.com/article/10.1007/s10457-026-01436-4), infiltration Results/Table 3 and Conclusions; [Filoso et al. (2017)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0183210), Abstract/Results/Discussion and Fig. 3; [FAO / Critchley and Siegert (1991)](https://www.fao.org/4/u3160e/u3160e07.htm), §§5.7.1–5.7.2, 5.7.4 and 5.7.6.
- Source fit is bounded: temperate alley cropping with an understory/soil-surface contrast; mixed forest-cover interventions rather than an isolated native-restoration effect; dryland stone bunds rather than every contour-bund design. These are curated reading examples, not extracted or newly approved EV/T3/T6 records.
- Evidence design is not a confidence score. No strength class, local benefit magnitude, new threshold or ranking is authored. The three source outcomes cannot be compared as a common performance metric. Formal pooled confidence and local transfer remain pending.
- Browser checks: all three hydrology examples and selected learning references; response dialog/Escape; cross-practice comparison dialog without changing selected practice; scripted-answer context; downloaded bund brief preserves source/locator/subtype/transfer limits. Default opportunity remains 2,967,500 nominal ha. Screenshot inspected; no console errors. JavaScript syntax, local targets/duplicate IDs and whitespace checks pass.

### Module 4: economic context and Bank indicators

- Added read-only `wireframe-investment.js`; no budget formulas/defaults, analytical rules, schema or backend changes. Published readings remain separate from editable assumptions and follow the viewed practice into learning resources and the downloaded brief.
- Bank definitions checked in the [official methodology pack dated 9 October 2026](https://wbgscorecardcdn.worldbank.org/scorecard-methodology/2026/data/methodologynotes_20261009060021023.zip), reached through the current Scorecard Data/Methods menu. Individual notes retain their own revision dates: food insecurity v2 September 2026; key ecosystems June 2024; protected-area context March 2024; resilience October 2024. The pack date is not asserted as every note’s revision date.
- Protected-area/OECM coverage is confirmed as **client context**. Its denominator includes land/inland waters and territorial waters; selected-opportunity overlap is a different local diagnostic. A 20% versus 30% invented arithmetic example demonstrates the difference. Ecosystem reference mapping names WorldCover, Global Mangrove Watch and Allen Coral Atlas without configuring bindings. The three context/vision measures and two project-results measures retain distinct meanings; no result is estimated.
- Cost passages inspected: [FAO forest-restoration toolbox](https://www.fao.org/sustainable-forest-management-toolbox/modules/forest-restoration/), section 3 financial requirements; [FAO water-harvesting manual](https://www.fao.org/4/u3160e/u3160e07.htm), §5.7.2 Table 24 and its note. Source price/horizon/layout limits are explicit. Combined planting/maintenance cost is not entered as establishment-only; historical labour quantities are not current currency prices or a conversion from applicability-zone hectares.
- **Open:** no matched monetary range for planted silvoarable agroforestry was verified. The UI identifies the gap and required local quantities/quotes; unrelated FMNR/cocoa costs are not substituted. These are curated readings, not approved T6E records. Local costing remains a dependency for every practice.
- Validation: all five dialogs and Escape; three practice cost panels; changing currency/year leaves source units intact; default affordable areas unchanged (agroforestry 2,000 / 1,384.6 ha; restoration 1,000 / 720 ha). Downloaded bund brief retains layout/denominator caveats, source and Bank limits. Screenshot inspected, no console errors; JavaScript syntax, HTML IDs/assets and whitespace checks pass.

### Module 5: usability and consistency

- Added `wireframe-usability.js` for presentation helpers. Administrative summaries show five units first, with the remaining units in an expandable table; expansion survives shared-control changes. Comparison includes bund applicability zones and all three practice pairs, plus a union that counts each fixture cell/resident once. Pairwise overlaps are explicitly non-additive and do not establish compatibility or installed area.
- Narrow screens retain readable table columns inside keyboard-focusable horizontal scroll regions. Touch controls and long-text wrapping improved. Desktop and 390 × 844 checks passed; no page-wide horizontal overflow after correcting crushed mobile columns.
- Saved results expose their original brief as unverified plain text, separate from the current rebuilt display. Settings-only imports and reset clear the archive. Invalid imports do not replace current settings; export validates control ranges. Earlier settings files without optional dataset fields still load.
- Validation: Admin 2 shows 5/14 units, schematic Admin 3 shows 5/53; keyboard disclosure and stage navigation work. All three pairs checked in baseline/future and empty scope; an independent three-cell example verifies triple-overlap deduplication. Default opportunity remains 2,967,500 nominal ha.
- Downloaded result reopened; archived markup displays literally, never as HTML. Invalid JSON, wrong fixture, missing brief, array settings and out-of-range maintenance years rejected; existing controls preserved. Invalid save rejected; legacy settings accepted. Mobile PNG exported and opened with scope, legend and provenance intact. Screenshots inspected; no console errors. Syntax, HTML IDs/assets and whitespace checked.
- **Still open:** full accessibility/cross-browser matrix, concurrent-load stress testing and Pete/TTL comprehension. No real analytical correctness, practice compatibility or runtime archive is claimed.

## Prioritised action table

Multiple actions can remain on one row. “Demonstrated” means browser-checked at example grade; it does not mean an approved method, real dataset or stakeholder sign-off.

| Request / priority | Progress /5 | Actions implemented in v1 | Remaining actions, in priority order |
|---|---:|---|---|
| Background, project aims and tool purpose — P1 | 4 | Landing explains rural NbS, investment-scoping gap, intended users, project deliverables and the wireframe's purpose before objectives. | **P1:** Pete checks whether the explanation answers a first-time reader's questions. |
| Explain each stage and simplify — P1 | 4 | Six original stages retained; each has a question, introduction and numbered/disclosed sections. Active stage and shared controls remain visible. | Module 5 compacts admin tables and checks narrow-screen/keyboard behaviour. **P1:** First-time TTL walkthrough; tighten remaining content based on actual confusion. |
| Objectives before interventions — P1 | 4 | Two editable objective presets; selected objectives carry into hotspots and brief. Custom combinations explicitly have no illustrated ranking. | **P1:** Agree the intended objective-to-variable relationship; demonstrate contributions once agreed. |
| Optional data-first configuration — P1 | 4 | Module 1 adds concrete catalogue/local candidate comparisons, proposal review differences, distinct treatment types and raw/response teaching previews within the two six-slot surfaces. | **P1:** Pete checks explanatory usefulness. **Dependency:** Actual family-specific response, local dataset validation and bindings await agreed contract; current curves are existing hypothetical method examples. |
| Correct suitability and operational factors — P0 | 4 | Roads/access support do not alter opportunity; operational questions stay with Project Risk and hand-off. No universal slope threshold. | **P1:** Method owners verify the screen-to-method wording, including hard masks and context overrides. |
| Shared selection and full labels — P1 | 4 | One state for viewed practice, suitability classes, climate and geographic view; hotspot classes remain separate. Three practices compared under common scope. | **P1:** Broader multi-practice selection/geography configuration remains outside this single-country example; avoid presenting three fixtures as full recipe support. |
| Excluded, unknown and context areas — P0/P1 | 4 | Module 2 adds a sourced activity-specific restriction, permission exception, applicability checklist and local challenge route alongside synthetic exclusion/context classes. | **Dependency:** Confirm current legal framework, actual activity, boundary and authorisation before any real mask. No parcel or recipe legality is ratified here. |
| Map cells, Admin 2/3 and 100-ha example — P1 | 4 | Shared views, denominators, zoom/recentre, administration summaries and coarse-grid illustration. Admin 3 is explicitly invented quadrants. | **Dependency:** Official Admin 3 data and actual raster/mask semantics/resolution verification. No real small-AOI capability claimed. |
| Need versus response; evidence explanations — P1 | 4 | Three source-linked readings distinguish effect direction, evidence design, source context, strength and confidence. The earlier unmatched FMNR example is replaced. | **Dependency:** Approved pooled T3/T6 strength and confidence remain separate; these readings are not approved evidence rows. Expand per-input coverage after alignment. |
| Climate comparison and timing — P1 | 4 | Baseline/future/difference fixture, named periods/scenario, explicit baseline denominator in difference mode. No intervention counterfactual or delay-cost claim. | **Dependency:** Actual output contract and future hazard/vulnerability treatment. Hazard flags stay fixed in this example. |
| Hydrology — P1 | 4 | Selected-practice readings show soil-water competition, catchment-yield trade-offs and stone-bund maintenance; local data fitness and study questions explicit. | **Dependency:** Local transfer and wider practice-family evidence review. No water-balance model or local hydrological prediction. |
| Individual hazards and overlap — P0/P1 | 4 | Fire, flood and intersection views with consistent scope/admin summaries. Unsupported overall risk rating and complement-of-mitigation logic removed. | Module 2 supplies an authoritative qualitative planted-tree/fire example with explicit transfer limits. **Dependency:** Practice/site-specific hazard severity, vulnerability and design evidence; no damage function or composite risk score. |
| Risk trade-off at shortlist — P1 | 4 | Keep-with-flags versus defer-overlap scenario; before/after area and residents visible; structural opportunity unchanged. | **Dependency:** Agree actual filter criteria; intersection is explicitly an illustrative choice, not an endorsed exclusion rule. |
| Gender and equity — P1 | 4 | Context-only toggle; counts/rankings unchanged; local rights and equity remain in hand-off. | **P1:** Link an appropriate national context source. Subnational differentiation requires separate data/method agreement. |
| Comparison and double counting — P0/P1 | 4 | Common-scope footprint/need table, all three pairwise overlaps and a deduplicated union, residents not beneficiaries; no compatibility verdict. Linear bund view reports applicability zone only. | Module 3 adds side-by-side source findings and individual evidence dialogs; incomparable outcomes cannot rank practices. Module 5 covers all supported combinations, including empty scope. **Dependency:** Reviewed common-outcome synthesis and local compatibility assessment. |
| Five Bank indicators — P1 | 4 | Five definition dialogs identify role, unit, denominator, source mapping, scan contribution and reporting limits. Protected/OECM share confirmed as client context; ecosystem reference datasets identified. | **Dependency:** Agree actual data releases/bindings, local baselines and reporting eligibility with the TTL. No official indicator is calculated. |
| Local budget and affordable hectares — P0/P1 | 4 | Editable currency/year, establishment, maintenance and fixed costs; same budget across two area practices, ceilings, two cost cases; linear bunds excluded from hectare returns. | Module 4 adds a sourced FAO planting-cost range and stone-bund labour comparison, separate from invented defaults. **P1:** Matched planted-silvoarable monetary evidence remains open. **Dependency:** Local quotes, price year, cost coverage and T6E review before reuse. |
| Unsupported economics and benefits — P0 | 4 | Removed asserted BCR/payback/carbon-cost/local benefit results. Optional return/reach require user assumptions; residents never substituted. | Module 4 identifies cost coverage, combined versus annual costs, price-year gaps, uptake and benefit timing; readings do not populate the calculator. Detailed CBA remains downstream. |
| Downloadable map and prose — P1 | 4 | PNG with colour legend, scope, scenario and provenance; three-paragraph brief with Admin 2 locations, assumptions and limits; copy/download work. | Module 3 adds a sourced, qualified reading paragraph to the brief, checked in download. Module 5 checks mobile PNG export. Approved synthesis and broader cross-browser export checks remain. |
| Local co-production and stopping point — P1 | 4 | Clear scoping end; partner validation, rights, adoption, feasibility and monitoring questions. | Module 3 adds practice-specific reading and local study prompts. **P1:** Local partners assess usefulness; no new feasibility deliverable. |
| Learn about this NbS — P1 | 3 | Readings, locators, context limits and follow-up questions now track all three practices; unrelated cocoa/FMNR defaults removed. | Module 4 adds selected-practice economic context and local costing prompts. **P1:** Matched planted-silvoarable cost evidence. **Dependency:** Team review of transfer and formal evidence status. |
| AI concepts — P2 | 3 | Scripted report/input/evidence interactions; proposals require review; file references stay local/unread; no live model. | **P2:** Improve examples using approved evidence and a concrete proposed change diff. Live service is not required or promised. |
| Save/load project and result — P2 | 4 | Versioned local JSON stores controls, assumptions, fixture identity/provenance and result snapshot; matching-version restoration demonstrated. Module 5 retains the original brief separately, rejects malformed/out-of-range imports and checks older settings compatibility. | **Dependency:** Actual run manifest/version/output contract. No pipeline execution or real analysis archive claimed. |
| Front/back-end alignment — deferred | 2 | Dev Notes map each screen to modules, tables, intended outputs and missing contracts. | **Dependency:** Wait for T4–Diego work, review identifiers/units/product type/masks/transformations and provenance, then decide whether to connect read-only tables. |

## Bank acceptance checks

These retain the B01–B16 identifiers from the revision plan. No row is labelled fully closed pending stakeholder review.

| Check | Status in this draft | Remaining boundary |
|---|---|---|
| B01 Objectives upfront | Visual behaviour demonstrated | Actual variable/weight mapping pending. |
| B02 Active stages / overload | Main journey demonstrated | Admin summaries compacted; full TTL usability check remains. |
| B03 Meaning / calculation / source | Partial; Module 1 demonstration expanded | Concrete input metadata and hypothetical raw/response previews shown. Real family-specific profiles and per-input evidence coverage remain incomplete. |
| B04 Climate / timing | Visual behaviour demonstrated | No avoided-loss or cost-of-delay inference. |
| B05 Exclusions / adjacency | Conditional legal example demonstrated | Activity, designation interval and permission are inspectable; current legal applicability and real boundary remain unverified. |
| B06 Individual / overlapping hazards | Visual behaviour plus sourced establishment example | FAO planted-forest/fire guidance supports qualitative follow-up only. Other hazards/assets and local vulnerability remain unresolved. |
| B07 Gender toggle | Behaviour demonstrated in hotspots | No actual gender dataset; national context cannot rank districts. |
| B08 Five indicators | Definitions and reference mapping demonstrated | All five have source notes, units and counting boundaries; actual input versions and reporting eligibility remain for owners. |
| B09 Local economics | Arithmetic plus sourced cost context | FAO planting range and bund labour quantities inspected; planted-silvoarable monetary evidence and all local prices remain unvalidated. |
| B10 Budget across NbS | Arithmetic demonstrated | Two area practices only; bund zones are not installed hectares. |
| B11 Downloads | PNG/text checked; mobile PNG and saved-brief recovery checked | Production exports and broader browser matrix not claimed. |
| B12 Project-document prose | Source reading added | Brief includes practice-specific findings, citations and transfer limits; approved local effects remain pending. |
| B13 Scoping boundary | Visual response demonstrated | Local validation remains downstream. |
| B14 Small vectors / rasterisation | Concept demonstrated | Actual supported resolution/masking remains with runtime owners. |
| B15 Hydrology | Selected-practice reading examples demonstrated | Three different outcomes, source contexts and study questions; local effect estimates and formal confidence remain unassigned. |
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

Not yet checked: exhaustive accessibility audit, broader mobile/cross-browser matrix, every AI/concurrent-import path, stakeholder comprehension, actual analytical correctness. No schema/backend changes were made. v0 body and pinned behaviour remain unchanged except shared release notes.
