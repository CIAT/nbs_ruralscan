/* Scripted presentation only. No model, document reading, evidence approval,
   binding writes or analytical execution. Reuses curated source readings. */
window.WireframeAI = (() => {
  'use strict';
  const esc = x => String(x).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function table(headers, rows, label) {
    return `<div class="table-scroll" tabindex="0" role="region" aria-label="${esc(label)}"><table><thead><tr>${headers.map(x=>`<th scope="col">${esc(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(x=>`<td>${esc(x)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  }
  function proposal(surface, state) {
    const suit=surface==='suit';
    const topic=suit?'Terrain input for suitability':'Rural-poverty input for prioritisation';
    const candidate=suit?'Fictional 2025 district terrain survey: 10 m bare-earth elevation in metres.':'Fictional 2025 district rural-poverty estimates: share of rural residents below a declared poverty line.';
    return `<h3>${topic}: proposed change for review</h3><p><b>Scripted draft; not applied.</b> The local candidate is invented. Your notes are recorded verbatim, not interpreted as proof that it exists.</p>
      ${table(['Decision','Before · catalogue teaching example','Proposed change · hypothetical'],[
        ['Dataset',suit?'Copernicus GLO-30 2024_1: nominal 30 m surface elevation, including vegetation/buildings.':'World Bank SPID: Admin 1 estimates; rural denominator and country/year availability need checking.',candidate],
        ['Where to use it','No real dataset is connected to this wireframe.','Only validated target districts; retain a compatible accepted fallback elsewhere or show a gap.'],
        ['What must stay separate',suit?'Family/context-specific slope response is not approved here.':'Transformation, correlation selection and weights are not approved here.',suit?'Derive slope at a meaningful scale before aggregation. Replacing elevation does not approve new thresholds.':'Review poverty line, population denominator, uncertainty and boundary crosswalk before comparing sources. Finer units alone do not justify new weights.']
      ],'Proposed input change')}
      <p><b>Published reference:</b> ${WireframeInputs.reference(surface)}. This supports the catalogue description only; it does not verify the proposed local source.</p>
      <dl class="info-list"><dt>Your context · unverified</dt><dd>${esc(state.localContext||'No local context supplied.')}</dd><dt>Document reference · unread</dt><dd>${esc(state.localReference||'No document reference supplied.')}</dd><dt>File name · content unread</dt><dd>${esc(state.supportingFile||'No file selected.')}</dd></dl>
      <p><b>Review decision now: hold.</b> Obtain the actual source, licence, coverage, date, units and country endorsement. ${suit?'Check datum, accuracy and surface-versus-terrain suitability.':'Check rural population definition, poverty-line/price basis and estimation method.'} A data steward reviews fitness; a method owner separately reviews treatment. Local partners confirm applicability.</p>
      <p>Saving records this unreviewed proposal and your notes in the local settings file. It approves nothing and changes no dataset, threshold, weight or result.</p>`;
  }
  function report(nbs, name, area, residents) {
    const footprint=nbs==='water'?'bund applicability zone':'candidate opportunity footprint';
    return `<h3>AI concept: review claims before drafting</h3><p><b>Scripted example; no model is running.</b> Current selection: ${esc(name)}. A future assistant could assemble scope, evidence and gaps for human review.</p>
      ${table(['Unsupported draft · reject','Safer wording / action','Why'],[
        ['These residents will benefit from the project.',`The synthetic ${footprint} contains ${residents} fictional residents across ${area} nominal ha. Reach, uptake and unique beneficiaries remain unassessed.`,'Counts describe the selected fixture, not an investment result.'],
        ['This practice will improve local water supply.',WireframeEvidence.summary(nbs)+' Local outcome and magnitude require investigation.','Source context and measured outcome must match; no local effect is calculated.'],
        ['The scan proves this investment is viable.','Carry candidate locations, explicit cost assumptions and evidence gaps into local co-production and proportional feasibility studies.','Scoping does not establish feasibility, legal permission or returns.']
      ],'Report claim review')}
      <button data-info="effect-${nbs}">Inspect the source, locator and transfer limits</button>
      <p><b>Drafting packet:</b> the current brief above contains the scope, assumptions, source readings and limits. Copy/download that brief for review. This panel neither alters it nor creates an approved report. No local impact, beneficiary or financial claim should be added without supporting evidence.</p>`;
  }
  function answer(nbs) {
    return WireframeEvidence.ai(nbs)+`<p><b>Supported answer:</b> ${esc(WireframeEvidence.summary(nbs))}</p><button data-info="effect-${nbs}">Inspect supporting passage and context</button><details><summary>Can the assistant rank these practices or fill missing effects?</summary><p>No. The three readings cover different outcomes and designs. No comparable pooled effect or local magnitude is available here. A useful answer names the missing evidence and follow-up study, rather than inventing a score.</p></details><p><b>Human checkpoint:</b> inspect the source locator, confirm practice and country transfer, then review any proposed wording. These are curated readings, not approved EV/T3/T6 rows. A live assistant would need access to reviewed evidence and auditable citations; that integration remains deferred.</p>`;
  }
  return Object.freeze({proposal, report, answer});
})();
