/* Read-only teaching examples. Source text and interpretation stay separate.
   This module never masks cells, assigns a risk score or writes evidence tables. */
window.WireframeSafety = (() => {
  'use strict';
  const law='https://faolex.fao.org/docs/pdf/sie41659.pdf#page=11';
  const forest='https://www.fao.org/sustainable-forest-management-toolbox/modules/forest-restoration/';
  const link=(url,label)=>`<a href="${url}" target="_blank" rel="noopener">${label}</a>`;
  const esc=text=>String(text).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function facts(items){return `<dl class="info-list">${items.map(([key,value])=>`<dt>${key}</dt><dd>${value}</dd>`).join('')}</dl>`;}
  const activity={
    agro:'For planted silvoarable agroforestry, ask whether the design clears new land for cultivation or adds trees to an existing field. The practice label alone cannot answer that.',
    forest:'For tree-based forest restoration, inspect site preparation and any tree cutting. Restoration intent does not itself establish permission or a prohibition.',
    water:'For contour bunds, inspect the actual earthworks, vegetation removal and land-use change. This clearing example alone does not resolve permissions for a bund design.'
  };
  function exclusion(nbs,name){
    return `<h3>Sourced example: activity and permission matter</h3>
      <p><b>Viewing ${esc(name)}.</b> ${activity[nbs]}</p>
      ${facts([
        ['Documented provision',`${link(law,'Sierra Leone Wildlife Conservation Act 1972, section 20; printed p. 8 / PDF p. 11')}. In the interval between a section 11 notice and the constituting order/proclamation, section 20 restricts new clearing for cultivation on the notified land. Section 20(2) provides an exception for written permission from a Wildlife Conservation Officer.`],
        ['Illustrated activity','A proposed new cultivated plot inside a hypothetical notified area. No real parcel, notice or permission has been supplied.'],
        ['What must match','Activity; notified boundary; relevant dates and designation stage; applicable law and amendments; authorisation and its conditions. A generic protected-area polygon supplies only part of this information.'],
        ['Current status','Source provision inspected; current consolidated law, local applicability and permission status NOT verified. This is a legal-screening teaching example, not a determination for Sierra Leone parcels.'],
        ['Effect on this map','None. Existing excluded cells and purple context marks remain synthetic. They are not mapped applications of this Act.']
      ])}
      <div class="table-scroll"><table><thead><tr><th>Review finding</th><th>Scoping treatment</th></tr></thead><tbody>
      <tr><td>Applicable prohibition and absence of authorisation confirmed by competent review</td><td>Record the reason, activity, boundary, date and authority; apply only the confirmed restriction.</td></tr>
      <tr><td>Designation, activity, permission or current legal basis unresolved</td><td>Flag for clarification. Do not infer either eligibility or a confirmed legal exclusion.</td></tr>
      <tr><td>Written authorisation is presented</td><td>Verify validity, coverage and conditions with the responsible authority. It does not automatically clear every other constraint.</td></tr>
      </tbody></table></div>
      <details><summary>Challenge a boundary or applicability error</summary><p>Prepare the location and boundary version, proposed activity, disputed reason, source section, relevant dates and any authorisation reference. Ask the competent authority and local rights holders to review the discrepancy. Keep the original restriction and review history until an authorised correction is recorded.</p><p>This wireframe cannot submit a challenge or lift an exclusion. The follow-up question is included in Next Steps and the downloadable brief.</p></details>`;
  }
  function vulnerability(nbs,hazard,name){
    const relevance=nbs==='forest'
      ? 'Direct practice context: the source discusses planted-forest maintenance. Species, planting age, site and management still need local assessment.'
      : nbs==='agro'
        ? 'Transfer question: planted agroforestry trees share an establishment stage, but this forest-restoration guidance does not establish a silvoarable loss rate or risk class.'
        : 'Not matched to this asset: guidance for planted trees does not establish the vulnerability of contour bunds. A structure-specific source and design assessment are still needed.';
    const layer=hazard==='fire'?'Fire layer selected. The map supplies only a synthetic exposure flag.':hazard==='flood'?'Flood layer selected. The source below concerns fire and cannot establish flood vulnerability.':'Overlap view selected. The source below addresses fire only, not flood susceptibility or a combined-risk category.';
    return `<div class="safety-example"><h3>Worked evidence example: fire during tree establishment</h3><p><b>Viewing ${esc(name)}.</b> ${layer}</p>
      ${facts([
        ['Source and locator',`${link(forest,'FAO Sustainable Forest Management Toolbox — Forest restoration')}, “Monitor and maintain forest management”, Table 3 and the following prescribed-burns paragraph. Inspected 29 October 2026.`],
        ['What the guidance supports','FAO includes dry-season fire prevention and survival/replanting checks in planted-forest maintenance. Its discussion of prescribed fire depends on trees being large enough to resist it.'],
        ['Interpretation for scoping','Establishment and later growth stages require different questions about exposure and protection. This is a qualitative screening rationale, not a measured damage function.'],
        ['Applicability to the selected practice',relevance],
        ['What it does not establish','No local mortality probability, severity threshold, safe planting age, benefit estimate or overall risk category is supplied. Protection measures are not evidence that risk has been eliminated.'],
        ['Evidence status','Published practitioner guidance, checked for this illustration. No new EV/T3 entry or project approval is claimed; formal evidence review and local transfer checks remain separate.']
      ])}
      <details><summary>What should local investigation establish?</summary><ul>
      <li>Planting or construction dates, species/materials, establishment stage and exposed assets.</li>
      <li>Hazard timing, intensity and duration; relevant observations and uncertainty.</li>
      <li>Protection and maintenance responsibilities, feasibility, costs and monitoring of survival or damage.</li>
      <li>Practice-matched evidence before choosing design changes, deferral or risk acceptance.</li></ul></details>
      <p><b>No numerical inference:</b> an NbS response to a hazard cannot be inverted into its susceptibility. Main opportunity and shortlist totals remain unchanged by reading this example.</p></div>`;
  }
  function handoff(nbs){
    const asset=nbs==='water'?'Obtain contour-bund-specific evidence on structure, establishment and damage; planted-tree fire guidance does not apply to the structure.':'Assess planting stage, species, fire exposure and feasible protection; FAO planted-forest guidance supplies qualitative questions, not a local loss rate.';
    return `LEGAL FOLLOW-UP: Confirm current law, notified boundary, designation dates, proposed activity and any written permission before applying an activity-specific exclusion. The section 20 illustration is not a parcel determination (${law}). ASSET FOLLOW-UP: ${asset} Source/contrast: ${forest} No restriction, risk score or analytical table has been changed.`;
  }
  return Object.freeze({exclusion,vulnerability,handoff});
})();
