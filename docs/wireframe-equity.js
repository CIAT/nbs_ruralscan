/* Static country reading, checked against the published PDF on 2026-10-29.
   Not a schema binding, district layer, equity score or runtime input. */
window.WireframeEquity = (() => {
  'use strict';
  const url='https://www.statistics.sl/images/StatisticsSL/Documents/DHS2018/SIERRA_LEONE_2019_DHS_REPORT.pdf';
  const source=`<a href="${url}#page=324" target="_blank" rel="noopener">Stats SL / ICF, Sierra Leone DHS 2019, Table 15.7.1</a> and <a href="${url}#page=325" target="_blank" rel="noopener">Table 15.7.2</a> (printed pp. 286–287).`;
  function panel() {
    return `<h3>Sierra Leone · national context, 2019</h3><p>Published survey estimates for women and men aged 15–49, including urban and rural residents. Historical context, not current conditions in the selected footprint.</p>
      <div class="table-scroll" tabindex="0" role="region" aria-label="National gender context; scroll horizontally if needed"><table><thead><tr><th scope="col">Reported measure</th><th scope="col">Women, age 15–49</th><th scope="col">Men, age 15–49</th></tr></thead><tbody>
      <tr><td>Have and use an account in a bank or other financial institution</td><td>5.8%</td><td>13.0%</td></tr>
      <tr><td>Own a mobile phone</td><td>42.6%</td><td>64.3%</td></tr></tbody></table></div>
      <p><small>Source: ${source} Denominator: the respective female or male population aged 15–49; these are not shares of farmers or project beneficiaries.</small></p>
      <p><b>Planning question:</b> could digital outreach or account-based payments miss intended participants? Check locally; these figures do not measure credit access, phone control or NbS adoption.</p><button data-info="equity">Interpretation and local equity checks</button>`;
  }
  function detail() {
    return panel().replace('<button data-info="equity">Interpretation and local equity checks</button>','')+
      `<h3>How to use this reading</h3><p>Use it to ask about participation and delivery arrangements. Do not multiply these percentages by fictional residents, assign them to map cells or use them to rank districts.</p><p>The publication also reports rural/urban and district breakdowns. They are not connected here; definitions, sampling uncertainty, boundary compatibility and present-day relevance would need review before any spatial use. No claim is made that 2019 is the latest available source.</p>
      <h3>Questions for local partners</h3><ul><li>Who can use the proposed outreach and payment channels? Offer workable alternatives and check who controls access.</li><li>Who holds land-use rights, supplies labour, makes decisions and controls benefits? Check tenure, participation and safeguards separately; these two measures do not answer those questions.</li><li>How will participation and outcomes be tracked by sex, age and relevant excluded groups, with locally agreed definitions?</li></ul><p><b>Method boundary:</b> national context informs co-production and implementation questions. It changes no suitability, hotspot rank, risk filter, area or resident count. Hiding the card does not remove equity from the hand-off.</p>`;
  }
  function brief(visible) {
    return 'GENDER CONTEXT — '+(visible?'Sierra Leone DHS 2019 reports that 5.8% of women and 13.0% of men aged 15–49 have and use an account in a bank or other financial institution; 42.6% and 64.3%, respectively, own a mobile phone. These national estimates include urban and rural residents; they are not current local observations or beneficiary shares. ':'National context card hidden; equity follow-up remains required. ')+
      'Source: Stats SL / ICF, Sierra Leone DHS 2019, Tables 15.7.1–15.7.2, printed pp. 286–287, '+url+'#page=324 . Planning questions: check outreach/payment access, land-use rights, labour, decision-making and benefit control with local partners. No spatial gender layer or ranking adjustment is connected.';
  }
  return Object.freeze({panel,detail,brief});
})();
