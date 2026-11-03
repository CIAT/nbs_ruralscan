# Wireframe revision plan

Updated 29 October 2026. Phase 1 presentation pass implemented locally and browser-checked; not published. Bank acceptance checks remain open except for the bounded demonstrations recorded below. Analytical changes and table integration remain deferred.

## Purpose and scope

Make the wireframe an accessible, interactive explanation of the Rural NbS Scan method. It should help users understand the questions, inputs, evidence and outputs at each step. It is not a finished product design, a commissioned production dashboard or a feasibility assessment. Reproducible implementation remains a separate project deliverable.

Pete's 28 October feedback leads this revision. Laurent/Dinara's earlier feedback remains relevant; simulated agent reviews supply additional checks, not stakeholder authority. Preserve the existing tab order. Hold actual table/backend wiring until the other session resolves the T4–Diego linkage.

Sources:

- [Feedback sheet](https://docs.google.com/spreadsheets/d/1IxovMmYGMS9oddz6fUUd6H4tGDRrsTjtdU1A0zI7vuA/edit): Peter Steward, 28 October; Laurent Frapaise and Dinara Akhmetova, 6 October. References below use P-Setup, P-Opportunity, P-Risk, P-Hotspots, P-Comparison, P-Next and P-General for Pete's sections.
- [Agent review](audits/wireframe_multi_perspective_review_2026-10-28.md): findings V01–V17, including source locations. Perspectives: TTL, Bank reviewer, IFI proposal developer and country implementing partner.
- Bank written follow-ups: `Responses_WBG_NbS_Rural_Scan.docx`, local D591 project folder, `4_Outputs_&_Reporting/4_Reporting/3. Phase 2 reporting/`. This is the locally inspected response document, not a claim about the precise emailed attachment version. It adds the small-vector question, five suggested indicators, agreed hydrology boundary, budget-to-hectares request and explicit risk-trade-off prompt.
- Current method decisions and schema remain authoritative for analytical behaviour. The old wireframe is not evidence of how a rule should work.

## Revision sequence

| Phase | Work | Completion condition |
|---|---|---|
| 1 — Explain and simplify | Scope introduction, section narratives, progressive disclosure, technical configuration access, shared selection labels. | A nontechnical reviewer can identify each screen's question, action, output and limits without opening technical controls. |
| 2 — Repair the illustrated logic | Separate suitability, need, response and investment risk; correct exclusions, uncertainty, economics and fixed-example claims. | Every example is internally consistent and clearly distinguished from a calculated pilot result. |
| 3a — Demonstrate Bank essentials | Pixel/admin and small-AOI examples, hazard overlap, evidence explanations, five-indicator crosswalk, local budget comparison and downloadable example outputs. | Bank-comment acceptance checks below pass in the demonstrator; analytical dependencies are separately identified. |
| 3b — Add supporting concepts | Project/run saving, AI examples and optional user-assumed ROI. | These support the core walkthrough without delaying Bank essentials or implying a live service. |
| 4 — Align and connect | Reconcile with the other session's contracts, then consider generated tables and versioned pilot outputs. | Method owners' input/output meanings, identifiers, scope and provenance agree before connection. |

Phases 1–3 can proceed with labelled, coherent examples. Phase 4 stays deferred. Bank essentials take precedence over optional AI, save/load and ROI expansion; Pete's requests for those concepts remain in scope. No new analytical thresholds or weights should be invented to make the illustration work.

## Screen changes

### Landing and shared controls

- Explain the demonstrator's purpose: a visual companion to the methodology, not the final UI/UX or a ready-to-use investment tool. Name the gap it addresses: rural NbS scoping and prioritisation.
- Give every tab and substantial subsection a short introduction: **What question does this answer? What can I do here? What should I take from it?** Include limits where they affect interpretation.
- Give each displayed variable/result a click- and keyboard-accessible information panel: meaning, unit, source and spatial/temporal grain, calculation or transformation, denominator, interpretation and limitations. Hover can supplement this; an evidence link alone is insufficient.
- Reduce simultaneous information. Use a short sequence or expandable sections, with optional detail, rather than many panels competing at once. Strengthen active-stage shading and keep essential controls visible while scrolling.
- Make the global strip valid for multiple selected NbS. Remove the single-NbS, recipe and risk labels from that strip; show relevant NbS/recipe context beside the local view instead. Retain geographic and display context.
- Illustrate a shared **Map cells / Admin 2 / Admin 3** selector across relevant tabs. Distinguish aggregation/view choice from analysis resolution. State denominator, selected suitability classes and whether statistics are an example. Do not imply district views identify eligible farms.
- Carry consistent NbS and suitability selection into Opportunity Space, Project Risk, Hotspots and Comparison. Hotspot-score selection is a separate control, with its own explanation.
- Add save/load project and analysis concepts. A saved analysis should identify the full parameter set, inputs and versions, selected context, run status and outputs; distinguish rerunning saved settings from reopening an existing result. Exact fields await the shared contract.

Sources: P-General, P-Setup, P-Opportunity, P-Risk, P-Hotspots, P-Comparison; Dinara; V14, V16.

### Setup and technical configuration

- Start with the project challenge and two or three objectives or a preset, then practices and geography. Preserve the useful existing NbS/geography/resolution choices.
- Include a 100-ha example boundary and small exclusion polygon to explain vector display versus raster analysis. Show the analysis-cell grid and loss of detail when cells are too coarse. Do not promise a minimum supported resolution before the runtime contract is verified; explain when finer inputs and local assessment are necessary. An admin-view selector does not solve this problem.
- Use **Mode A only** in the next wireframe. Proposed decision record: Hazard × Exposure keeps the explanation simpler and avoids duplicating vulnerability inputs already used in prioritisation. This is a presentation/method recommendation from Pete's review; before changing any analytical default or retiring Mode B in the method, reconcile the existing locked decision and record the agreed scope of removal. No silent backend change.
- Clearly label Variable Config as optional technical work: “Use this to inspect or customise data and analytical settings.” Explain whether the current user needs it.
- Provide a contextual “Technical configuration for this section” link from each tab. Keep one configuration home under Setup, with clearly separated sections, rather than adding competing top-level tabs.
- Organise configuration around user actions: **inspect/select datasets and local inputs first; inspect/tune analytical rules second**. Separate quantitative response functions, categorical host-system gates, exclusions and operational factors. Do not copy the current mixed suitability panel unchanged.
- Define terms before placing controls: NbS/family suitability; characterisation of selected opportunity; livelihood need; investment risk; hotspot priorities. Shared variables may be reused, but their roles, relevant practices and analytical treatment must remain explicit.
- Remove runtime/cache administration language from the main journey. Review context overlays for removal from the default view until their purpose is clear.

Sources: P-Setup; Laurent; V01, V08, V14. Exact T4 configuration and operational-factor placement depend on the other session.

### Opportunity Space

- Use full class labels: Very high, High, Moderate, Low, Excluded. Separately show unknown/unassessed inputs and out-of-scope areas; low scores must not masquerade as legal exclusions.
- Explain that all fingerprint and problem distributions refer to the selected suitability scope. Move area loss and combined risk-share summaries to the fingerprint/context summary, with explicit denominators, rather than mixing them into individual livelihood-risk rows.
- Split the view into manageable sections: map and footprint; climate-related livelihood need; other needs and NbS response. Explain why those groups differ and how evidence response relates to spatial need.
- Link every displayed constraint or lever back to its configuration and evidence. Do not assume a universal slope cutoff: check the recipe and units, including the percent-versus-degrees ambiguity in the feedback. Do not let road scenarios redefine natural suitability.
- Keep excluded areas inspectable, with reason, source and applicable recipe. Avoid blanket assumptions that protected areas or wetlands prohibit every NbS. Confirmed legal exclusions remain binding; apparent input errors can be referred for local validation.
- Provide an excluded-area/context overlay visible alongside candidate areas, so users can inspect adjacency to wetlands and protected areas. Simplification must not remove this requested context; no distance calculation is promised without a specified method.
- Retain the map; verify zoom/recentre behaviour and demonstrate admin summaries. Simplify or hide context layers without a clear decision purpose.
- Update response symbols to the current T3/T6 design, explain strength separately from confidence, and provide an evidence drill-down concept. Preserve transfer limits and distinguish local need from globally synthesised response.
- Explain Baseline / Future / Difference beside the scenario control: selected climate scenario, horizon, reference period and what changes or remains fixed. Show one worked comparison. Explicitly distinguish climate change from intervention effects: these layers alone cannot estimate benefits of investing now or costs of delay.
- Include one hydrology example: spatial water stress/depletion where defensible data exist → evidence on the selected NbS's possible hydrological response → context and uncertainty → required local study. Keep groundwater recharge, catchment yield and water quality distinct. Show unavailable data honestly. This implements the Bank-agreed scoping response; detailed hydrological modelling remains downstream.

Sources: P-Opportunity; Dinara; V03–V05, V08, V16–V17. Evidence and class definitions can be illustrated now; table wiring waits.

### Project Risk

- State plainly: this screen asks what could damage the intervention or obstruct delivery; Opportunity Space describes where it could fit and what needs occur there.
- Match the NbS and suitability controls used elsewhere. Show suitable area and hazard exposure within each chosen admin unit, plus the selected hazard layer. Explain overlay and denominator.
- Show individual hazards and evidence of NbS vulnerability, including establishment phase. A hazard can be mitigated by an NbS and still damage it; abandon the “complement of mitigation hazards” explanation.
- Demonstrate two hazard layers together with a distinct overlap legend and scope denominator. Co-occurrence is a spatial intersection, not a validated combined-risk score.
- Separate asset hazards from operational/enabling conditions, with links to configuration and evidence. Treat tenure and labour as context requiring verification, not automatic rejection or proven adequacy.
- Remove the unsupported default overall “Moderate risk” verdict. A composite remains an optional concept pending an agreed method; do not replace it with an invented index. Prefer interpretable exposure summaries meanwhile.
- Before claiming alignment, verify the applicable World Bank disaster-risk framework and show which elements are adopted or additional. No claim of an official WB rating or completed safeguards assessment.

Sources: P-Risk; Dinara; V07, V15. Hazard selection, composite method and M2b input/output contract require method-owner resolution.

### Priority Hotspots

- Sequence **choose priorities/preset → inspect map → inspect selected hotspot footprint and admin summary**. Keep custom tuning in technical configuration.
- Put the TTL's need-versus-investment-risk choice here, before confirming a shortlist: retain the need ranking with risk flags, or apply an optional investment-risk filter using explicitly stated criteria. Show a worked before/after example with retained/flagged areas and people within the footprint. Link back to Project Risk evidence; never sum M2b into livelihood need. Until criteria are agreed, label the consequence illustrative rather than inventing a composite threshold.
- Explain hotspot score and provide its own scope selector; show how it intersects the selected suitability scope.
- Keep selected priorities, calculated ranking contributions, descriptors and contextual flags distinct. National gender context cannot create subnational discrimination without appropriate data.
- Explain the gender control at the control itself: with the current national indicator it changes context visibility, not district rankings. Demonstrate that behaviour consistently across views. Any future subnational alternative requires separate data and method review.
- Ensure illustrative rankings and “why here” prose correspond to the example preset. If controls change without recalculation, visibly label the result as an unchanged example; do not call it live.

Sources: P-Hotspots; Laurent; V02, V08–V09.

### NbS Comparison

- Introduce the comparison question and common scope. Carry the shared map/admin view through.
- Explicitly connect opportunity footprint, needs within it and each NbS response profile. Separate evidence strength, confidence and applicability.
- Describe overlap as a candidate for joint assessment, not proof of compatibility or a stronger investment case. Flag possible double-counting of people and benefits.
- Show a five-row crosswalk for the Bank's suggested indicators: percentage of people facing food/nutrition insecurity; hectares of key ecosystems; hectares under enhanced terrestrial/aquatic conservation or management; beneficiaries with enhanced climate resilience; protected terrestrial/aquatic area share. Verify official names and definitions before implementation. For each row show relevant scan evidence, units, and status: context, potential contribution, or project result not estimated. Existing habitat area is not automatically area enhanced; exposed residents are not automatically resilience beneficiaries.
- Place the primary budget box in **NbS Comparison**, as requested by the Bank. Show illustrative affordable hectares by NbS, alongside candidate-area ceilings and editable local cost assumptions: currency/base year, establishment cost, maintenance period/cost and fixed or enabling investments (including roads/electricity when relevant). Show unsupported or missing assumptions explicitly; distinguish literature defaults from user values. Compare both a simple establishment-only case and a fuller cost case. Keep this an arithmetic illustration, not a spatial suitability constraint or an estimate of achieved benefits.

Sources: P-Comparison; Laurent; V09–V10, V13.

### Next Steps and economics

- Make the stopping point unmistakable: **scoping ends here**. Replace the appearance of three equally delivered stages with a concise hand-off: what this scan tells you; what must be established locally before implementation. Link to downstream methods without committing this project to write full feasibility guidance.
- Put local partners and co-production at the centre: refine targeting, validate included and excluded/uncertain areas, assess fit, rights, delivery arrangements and adoption. A promising map does not ensure suitable intervention design or returns.
- Preserve a **Learn about this NbS** section with seminal publications and curated evidence on effects, costs and conditions. Literature economics can be useful without being a local project appraisal; retain context, units and transfer limits.
- Link to the **budget comparison** above, with an optional extended assumption-driven calculator here. Candidate outputs: area/reach, cost per hectare/person and optional illustrative ROI when the user supplies a defined benefit/cost basis. Show time horizon, recurring costs, uptake, denominator and benefit assumptions; do not invent unavailable inputs or equate residents with beneficiaries. Distinguish first income, payback, BCR and ROI. Extended ROI must not delay the simpler Bank budget example.
- Replace existing unexplained BCR, payback and carbon-cost results rather than deleting economics wholesale. Label calculator values as scenarios, not predicted returns. Detailed CBA and validated benefits stay downstream.
- Provide a **copyable and downloadable example scoping brief**, including two or three usable prose paragraphs on opportunity area, risks/admin hotspots and indicative costs/benefits with qualifications. Include objectives, selected scope, evidence, assumptions, uncertainty and commissioning questions. Also provide at least one downloadable example map (PNG) with legend, units, scope, scenario and illustrative-data label. Preview alone does not satisfy the download request. Static assets are sufficient; make example status explicit in both page and downloaded files. Planning layers inform outcome-baseline design; they do not establish attribution.

Sources: P-Next, P-General; Laurent/Dinara; V05–V06, V09, V11–V13, V15–V17.

## AI illustrations

Show three clear entry points, with labelled example interactions:

1. **Make report:** draft results and a methods/assumptions account from the selected analysis. Cite evidence and saved configuration; do not fabricate provenance or results.
2. **Improve inputs for this location:** in technical configuration, ask context questions, accept supporting documents conceptually, and propose locally relevant datasets, variables, weights or relationships. Show proposed changes, sources and human review before adoption. Respect the same evidence and schema process as other inputs.
3. **Ask about this NbS:** answer evidence questions and summarise costs, effects and limitations; expose missing evidence rather than filling gaps with invented values.

AI-assisted discovery of local economic inputs can be illustrated. Live model execution through MCPs remains an exploration, not a promised feature or assumption that a suitable model/service exists. AI cannot convert screening overlap into verified benefits or silently alter rules.

Sources: P-Setup, P-Next, P-General. Extends the agents' narrower explanation/reporting suggestions.

## Reconciliation of feedback

| Tension | Integrated direction |
|---|---|
| Agents suggest removing unsupported economics; Pete wants useful economics and a simple returns calculator. | Remove unexplained project claims; retain contextual evidence and explicitly assumed calculator scenarios, including conditional ROI. |
| Laurent wants priority groups expanded; Pete and Dinara flag overload. | Show the high-level objectives/presets upfront. Put expanded variable detail in optional technical configuration. |
| Existing method offers Mode B; Pete suggests Mode A only. | Plan Mode A-only user journey and record rationale; reconcile the method lock before implementation changes. |
| Agent audit values staged downstream hand-off; Pete questions three stages and extra methods workload. | Keep hand-off and local validation, simplify its display and avoid a new feasibility-method deliverable. |
| Pete suggests technical config per tab; current structure puts it under Setup. | Contextual links into one organised configuration workspace; no duplicate settings or tab-order change. |
| User wants risk interpretation; neither review establishes a defensible composite. | Illustrate hazard-specific/admin summaries now; hold the overall category and calculation pending method agreement. |
| Real tables would improve consistency, but another session owns linkage. | Record intended consumers and data roles; defer connection and schema edits until that work settles. |

All agent findings V01–V17 are incorporated above as accepted or adapted recommendations. V06 economics and the proposed three-stage hand-off are explicitly adapted to Pete's feedback. Analytical portions of V03, V04, V07, V08 and V17 remain dependent on method alignment.

## Bank comment closure matrix

All rows are **open for implementation and demonstration**. “Accepted” describes planned treatment, not completed work. Review owner: this wireframe workstream for presentation; method/runtime owners for the identified analytical dependencies. The Bank feedback source is the sheet unless marked “written follow-up.”

| ID and source request | Disposition and exact screen | Worked example / acceptance check | Dependency or scope boundary |
|---|---|---|---|
| B01 Laurent: challenges upfront; 2–3 priorities | Adapted — Setup, then Hotspots | Select two objectives before choosing NbS; both remain visible in later summary. Detailed weights optional. | Do not move all priority/descriptor variables into structural suitability. Actual weight mapping awaits contract. |
| B02 Dinara: active stages and reduced overload | Accepted — all tabs and Setup substeps | Active tab/subtab visibly shaded; walkthrough presents one manageable decision group at a time. | Expanded technical detail remains available, reconciling Laurent's visibility request. |
| B03 Laurent/Dinara: what variables measure and how calculated | Accepted — information panels throughout | Open example panels for a suitability variable, hazard, priority and response; each explains meaning, units, source/grain, calculation and limits. Apply pattern to every displayed variable/result. | Use current definitions; mark unresolved methods rather than inventing explanations. |
| B04 Laurent: climate toggles and investment timing | Adapted with explicit pushback — Opportunity Space | Baseline/future/difference comparison names scenario and horizon; text says it is not with/without-project analysis. | No avoided-loss or delay-cost estimate from climate layers alone. |
| B05 Dinara: exclusions visible and not universally applicable | Accepted — Opportunity Space and technical configuration | Toggle excluded/context overlay next to candidate areas; inspect reason/source/recipe for protected-area and wetland examples. | Confirm legal versus recipe treatment; preserve local-data challenge route. |
| B06 Dinara: individual and overlapping hazards | Accepted — Project Risk | View each of two hazards, then their overlap; legend distinguishes co-occurrence from overall rating. | No new multi-hazard index. |
| B07 Laurent: gender toggle effect | Accepted — Hotspots and Opportunity Space | Toggle national context; explanation and rankings remain consistent with visibility-only behaviour. | Subnational differentiation requires appropriate inputs. |
| B08 Laurent plus written follow-up: WBG indicators | Accepted selectively — NbS Comparison | All five suggested indicators have a row, source/definition reference and clear context/contribution/not-estimated status. | No claim of achieved project results or full Scorecard coverage. |
| B09 Dinara: local economic inputs | Accepted — NbS Comparison budget panel | Change local unit-cost assumption in a worked scenario; affordable area changes coherently, with cost basis and exclusions visible. | Static paired examples or bounded illustrative arithmetic suffice. No local-price inference without evidence. |
| B10 Written follow-up: budget box and affordable hectares by NbS | Accepted — NbS Comparison | Same budget across two NbS; show hectare range, candidate-area ceiling and establishment-only versus fuller costs. | Budget does not redefine natural suitability. Linear/qualitative practices must not acquire false hectare outputs. |
| B11 Dinara: downloadable outputs | Accepted at demonstrator grade — map and Next Steps | Download labelled example PNG and scoping brief; verify they open and retain scenario/scope/assumptions. | Production export infrastructure deferred; previews alone fail. |
| B12 Laurent/Dinara: prose suitable for project documents | Accepted — Next Steps | Copy two or three example paragraphs covering footprint, risk/admin locations, costs and evidence-supported benefits with limits. | Distinguish literature response from attributable local impact; AI not required to deliver example. |
| B13 Dinara: tool stops at scoping | Accepted — landing and Next Steps | Reviewer can identify delivered output and subsequent partner-led validation; downstream stages not presented as completed modules. | No new feasibility-method deliverable. |
| B14 Written follow-up: 100-ha vectors and rasterisation | Explanation accepted; capability claim deferred — Setup | Small boundary/exclusion over coarse grid demonstrates what is visible versus analytically resolvable; route to finer/local assessment explained. | Runtime team verifies actual supported resolutions and mask semantics. |
| B15 Written follow-up: hydrological inputs and outcomes | Accepted within already agreed scope — Opportunity Space → Next Steps | Water need layer, distinct evidence response, uncertainty and downstream study shown in one example. | No detailed hydrology or interchangeable recharge/yield/quality claims. |
| B16 Written follow-up: where TTL makes risk trade-off | Accepted as visible choice — Hotspots, linked to Project Risk | Need-ranking-with-flags versus optional risk-filter example shows what changes and who/what is excluded. | Filter criteria await method agreement; no unsupported overall risk category. |

Close a row only after recording the actual screen/control and a verified example. A method-dependent row can be marked “visual response demonstrated; analysis pending,” never simply complete. Record any further rejected request with its reason and bounded alternative.

## Handoff to implementation and validation

Maintain a developer note mapping **screen → question → module → input tables/registers → output → example or computed status → unresolved contract**. Keep it outside the TTL journey. Include table versions, provenance and the relationship between the visual front end and reproducible analysis.

Before calling the revision ready:

- Walk through one multi-NbS example with two priorities, selected suitability classes and an admin view. Check consistency across all six tabs.
- Verify scope/selection labels, full class names, sticky controls, map interactions and technical links in the browser; check keyboard access to controls and evidence explanations.
- Check every numerical claim, source link, unit, denominator and example label. No unexplained benefits, automatic investment verdicts or unsupported overall risk rating.
- Check AI and calculator examples against scoping limits; saved-project concepts must account for the full configuration.
- Compare the revised walkthrough against Pete's feedback and the agent IDs, keeping unresolved method questions visible. Do not mark table integration complete from visual consistency alone.
- Run B01–B16 acceptance checks and record outstanding dependencies. Bank-essential examples must exist before optional concepts are treated as the revision's main achievement.

This plan records the full intended revision. Only the bounded Phase 1 presentation work below has been implemented; it does not establish analytical alignment or completion of later phases.


## Phase 1 execution — 29 October 2026

Implemented in `docs/wireframe.html`, with presentation-only `docs/wireframe-guide.css` and `docs/wireframe-guide.js`:

- Setup now opens first. Two or three project objectives remain visible across all sections, explicitly as walkthrough guidance without weight mapping or recalculation.
- Shared introductions explain each section's question, action and scope limits. Landing and Next Steps distinguish the visual demonstrator, reproducible pilot analyses and downstream local feasibility work.
- Setup uses expandable scope and recipe sections. Example navigation replaces the misleading Run analysis action; runtime/cache administration prose is removed from this entry path.
- Optional technical configuration has data-first guidance, contextual suitability/hotspot links and return navigation. Fixed a pre-existing deep-link defect that could leave two panels active. Detailed reorganisation of configuration remains pending.
- Active tabs and subtabs are shaded; main navigation stays visible while scrolling. Global labels describe the example geography/grid/climate without implying one global NbS or recipe. Suitability selectors/readouts use full class names; hotspot selectors distinguish Very low / nil from suitability Excluded.

Validation: browser walkthrough at desktop viewport; two-objective selection, three-objective cap and deselection; keyboard disclosure; example navigation; five downstream section introductions; exactly one active panel; hotspot technical deep-link and return; Setup return; suitability readout update; comparison class labels. Screenshots inspected for Setup, Opportunity Space and technical configuration. No browser console errors observed. Inline/external JavaScript syntax and patch whitespace checked. Screenshot: `.cache/wireframe-review/phase1-setup-2026-10-29.jpg` (local review evidence, not published).

Bank checks: **B01 visual response demonstrated; analytical mapping pending. B02 partial** — active cues and Setup progressive disclosure verified; dense results panels still require later simplification. **B13 partial** — scoping purpose and downstream hand-off introduced; legacy output claims still require the later content audit. B03–B12 and B14–B16 remain open; this pass does not close them.

No analytical rules, schema or runtime wiring changed by this task. Existing method/schema edits in the shared workspace belong to separate work. T4–Diego linkage remains deferred. Later phases, responsive/accessibility audit, full multi-NbS/admin consistency, unsupported legacy risk/economic claims and publication remain outstanding. No subsequent run scheduled.
