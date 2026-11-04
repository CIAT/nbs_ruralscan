# Wireframe review from user and investment perspectives

28 October 2026. Review baseline: `e4347aa1f19e62ca80a490c56529c63897fbfa67`.

**Integrated follow-up:** [Revision plan](../wireframe_revision_plan_2026-10-28.md) reconciles these findings with Pete's submitted feedback. Use that plan for next work; this audit preserves the original agent recommendations, including recommendations subsequently adapted on economics and downstream-stage presentation.

The wireframe communicates the broad scoping sequence well, but several examples imply investment conclusions the method does not establish. The next visual revision should make the illustrated decision logic consistent before connecting actual analytical outputs.

These are simulated agent perspectives, not testimony from TTLs, Laurent, Dinara, GCF or other institutions. They remain proposals pending Pete's review. No dashboard, schema or analytical implementation was changed. T4–Diego linkage and data wiring remain with the other session.

## Review coverage

Three agents independently reviewed the local source:

- **World Bank TTL:** scoping a Sierra Leone rural resilience project, balancing drought resilience and poorer farmers.
- **Bank reviewer:** assessed the interface against Laurent/Dinara concerns already retrieved in this conversation. Findings are agent interpretations, not additional comments from those reviewers.
- **GCF and general IFI proposal developer:** assessed appraisal usefulness, causal claims, beneficiaries, economics and evidence gaps. This is general appraisal judgment, not a fund-specific compliance assessment.

The TTL agent also conducted a separate country-implementation and inclusion pass. The coordinating agent inspected the live Opportunity Space and Setup views, including the rendered Opportunity Space screenshot. This was a limited visual check, not a complete browser or accessibility test. The other reviews were source-based.

Sources below use **W** for [wireframe.html at the review commit](https://github.com/CIAT/nbs_ruralscan/blob/e4347aa1f19e62ca80a490c56529c63897fbfa67/docs/wireframe.html), and **R** for [project_risk.js](https://github.com/CIAT/nbs_ruralscan/blob/e4347aa1f19e62ca80a490c56529c63897fbfa67/docs/project_risk.js). Line numbers refer to that snapshot.

## Recommended presentation changes

P1 means address before the next stakeholder walkthrough. P2 means useful in the same revision where capacity permits. These are reviewer priorities, not approved commitments.

| ID | Priority and screen | Observed issue and evidence | Smallest useful change | Supporting perspectives |
|---|---|---|---|---|
| V01 | P1 Setup | Starts with NbS selection (W 3101–3112); development priorities arrive in Hotspots (4062–4071). | Begin with project problem and two or three objectives. Carry these into the visible summary. Do not imply they already alter weights or calculations. | TTL, Bank |
| V02 | P1 Hotspots | Controls update selections and summaries (W 5926–5945), while “Why Kenema is #1” remains fixed (4288–4298). “Conceptual · live” obscures this distinction (4063). | Label rankings and prose as a fixed example tied to a named preset. Mark results as an unchanged example after edits. Use “Selected priorities” unless actual contribution is calculated. | TTL |
| V03 | P1 Opportunity Space | Roads supposedly make another 12,400 km² viable (W 3329); Next Steps repeats the investment conclusion (5231). | Separate core natural/system opportunity from accessibility within it. Describe current versus improved access; do not show roads creating natural suitability. | TTL, method review |
| V04 | P1 Opportunity Space | Hard exclusions are described as removed rather than scored (W 3335), but every synthetic score below 0.2 becomes “Excluded” (5584). | Distinguish hard exclusion with reason, low suitability, missing input and outside selected scope. Illustrate these states now; defer analytical mapping. | Bank |
| V05 | P1 Opportunity Space and Next Steps | Carbon total 1.9 Mt C/yr and food insecurity “buffers $240M/yr” (W 3569, 3584) imply local attributable effects. | Separate spatial need/exposure from literature response. Replace unsupported totals with bounded evidence statements and validation questions. A mock-data banner alone does not explain the conceptual distinction. | TTL, IFI |
| V06 | P1 Next Steps and Comparison | BCR 1.8–3.2 and payback sit above a “not a CBA” caveat (W 5110–5113); carbon unit costs appear at 5122. | Retain indicative establishment/maintenance costs with units, source context and coverage. Replace unsupported return estimates with “requires project-specific appraisal.” Budget-to-area may be an explicitly assumed illustration, not affordable-benefit estimation. | TTL, Bank, IFI |
| V07 | P1 Project Risk | Hazards threatening an NbS are defined as those it does not mitigate (W 5277, 5360; R 8). | Explain that mitigation potential and damage susceptibility are independent. Include establishment-stage vulnerability. Call this an illustrative investment-risk screen, without implying equivalence to an official WB rating. | TTL, Bank, IFI |
| V08 | P1 Opportunity Space and Hotspots | National gender flag is correctly explained in Hotspots (W 4134), but Opportunity shows a spatial “30% high+ GII” distribution (3579). | Use a consistent national context card. Explain that visibility toggle cannot create within-country differentiation. Keep ranking drivers separate from descriptors. | TTL, Bank, IFI |
| V09 | P2 Hotspots and Next Steps | Population within footprint supports beneficiary language and cost/beneficiary figures (W 4296, 5120). | Say “people living within candidate footprint.” Actual beneficiaries require a delivery model, benefit pathway, disaggregation and overlap checks. | IFI, TTL |
| V10 | P2 Comparison | Spatial overlap is described as the strongest combined investment case or more investable (W 4005, 7093). | Call it a candidate landscape for joint assessment. Identify compatibility, incremental benefits, shared delivery and double-counting checks. | TTL |
| V11 | P2 Next Steps | Baseline layers are presented as allowing attribution (W 5080, 5188). | Describe planning evidence that informs baseline design. Hand off outcome baseline collection, indicators, responsibilities and assessment of contribution/attribution. | IFI |
| V12 | P2 Opportunity Space and Next Steps | “Carbon (eligible)” and suggested credit financing imply assessed eligibility or market viability (W 3603, 7078). | Show financing options to investigate. Distinguish public-good funding rationale from contingent revenues needing rights, measurement, eligibility and transaction-cost assessment. | IFI |
| V13 | P2 Reporting | No consolidated scoping-brief export or explicit WBG indicator crosswalk identified. Existing district narrative offers a useful format (W 4288). | Mock a brief containing objectives, candidate landscapes, evidence, uncertainty and next studies. Distinguish screening proxies from reportable project results. A static example is sufficient. | Bank, IFI |
| V14 | P2 Setup and navigation | Direct entry opens Opportunity Space (W 3050). Setup foregrounds resolution, formulas, clustering and cache-administration details (3173–3244). | Start walkthrough at Setup; lead each stage with its decision. Put implementation details in technical mode/help. Existing active-tab underline and dark step badge already work; improve contrast rather than treating navigation feedback as absent. | Bank, coordinating visual review |

## Country implementation and inclusion

| ID | Priority and evidence | Concern | Smallest useful change |
|---|---|---|---|
| V15 | P1 Project Risk, W 5331–5340 | Customary/community tenure uses a block-styled flag, while labour is declared adequate. This can imply communal rights are a delivery defect and local assumptions already verified. | Use “Local verification required.” Separate tenure context from safeguards applicability. Name community representatives, implementing partner and safeguards specialist as proposed participants in verification. Rights information should not automatically reject a site. |
| V16 | P1 Setup and Hotspots, W 3179–3186, 4293 | Default 5 km and suggested 1 km analysis coexist with a claim about suitability “across most parcels.” | Say “mapped landscape cells.” State that landscape screening does not identify eligible farms or individual holdings. Qualify smallholder information by source grain and coverage. |
| V17 | P2 Opportunity Space and Next Steps, W 3335–3340, 5184–5185 | Blanket masks hide differences between legal exclusions and recipe constraints; local validation focuses on retained hotspots. | Show exclusion reason, source and applicable recipe. Include a local review sample of excluded and uncertain areas to identify input errors. This is not permission to override confirmed legal constraints. |

## Method decisions to resolve before wiring

- **M2b:** hazard selection and aggregation must preserve independent asset susceptibility, mitigation and operational-risk streams. Correcting prose does not validate the calculation.
- **State semantics:** define excluded, unsuitable, unknown and not assessed consistently across recipes and outputs. Do not encode new thresholds in the visual mockup.
- **Priority contract:** distinguish selected objectives, weighted priorities, descriptors and contextual flags. Ranking explanations must correspond to the actual illustrated configuration.
- **Dataset and result contract:** use the current schema and the T4–Diego linkage outcome. This review does not duplicate or supersede that work.
- **Hydrology:** retain scoping-level stress and evidence interpretation. The earlier audit's water-quality/yield/recharge aggregation concern remains a method question, not a licence to change a ratified table here.

## Scope boundaries and useful pushback

Keep detailed hydrology, engineering, validated beneficiary totals, attributable avoided losses, full CBA, credit eligibility, safeguards clearance and fund-specific proposal completion downstream. A visual illustration should clarify how these questions arise, not promise to answer them.

Potential WBG/GCF alignment can be illustrated without declaring compliance or reporting achieved results. Budget-to-hectares examples need cost coverage, exclusions and applicable-area ceilings; they do not establish uptake or benefits. Overlapping footprints do not establish compatible investments.

## AI concept for the next visual revision

This is a coordinating recommendation based on the earlier AI discussion, not a separately tested feature or an explicit Bank chatbot specification.

Use three example actions: **Explain this result**, **Show evidence and transfer limits**, and **Draft a scoping brief**. Example answers should cite the displayed evidence, identify the chosen context and distinguish calculated results from illustrative values. AI may identify missing inputs and suggest questions; it should not manufacture outcomes, approve investment choices or silently change analytical rules. This can remain a static demonstration while the method implementation matures.

## Preserve these strengths

- The six-stage journey and explicit separation of livelihood need from investment risk.
- Disaggregated hazard rows already present in Opportunity Space (W 3499–3542).
- Explicit scoping endpoint and staged pre-feasibility/feasibility hand-off (W 5062–5087).
- Country-endorsed data checks, safeguards hand-off and downstream methods (W 5129, 5201–5222).
- Variable explanations and technical-mode concept: improve consistency rather than exposing every analytical detail by default.

## Combining this with human feedback

Keep this audit separate from the human response collection. Agent findings have not been submitted as stakeholder feedback. After Pete's review, reconcile each finding as accept, adapt, defer or reject; retain the reason and source. Repeated agent findings identify agreement between simulated perspectives, not independent empirical validation.
