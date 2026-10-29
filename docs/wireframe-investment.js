/* Read-only economic context and Bank indicator definitions.
   No analytical rules, cost defaults or reporting results are set here. */
window.WireframeInvestment = (() => {
  'use strict';
  const methods = 'https://wbgscorecardcdn.worldbank.org/scorecard-methodology/2026/data/methodologynotes_20261009060021023.zip';
  const faoForest = 'https://www.fao.org/sustainable-forest-management-toolbox/modules/forest-restoration/';
  const faoBunds = 'https://www.fao.org/4/u3160e/u3160e07.htm';
  const esc = x => String(x).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link = (url, text) => `<a href="${url}" target="_blank" rel="noopener">${esc(text)}</a>`;
  const facts = rows => `<dl class="info-list">${rows.map(([k,v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join('')}</dl>`;
  const indicators = {
    food: {
      contribution: 'Frame food-security need and identify a suitable local baseline.',
      label: 'Food and nutrition insecurity', type: 'Vision + client context', unit: '% of population',
      meaning: 'People in households experiencing moderate or severe food insecurity because resources constrain food access. This is not a count of people whose food security improved.',
      calculation: 'Estimated affected population / total population × 100. FAO FIES or compatible survey measures; country estimates use three-year averages. A percentage of flagged map cells is a different measure.',
      data: 'FAO survey-based estimates. Do not spread a national value across cells to infer local variation or project beneficiaries.',
      status: 'No population-based estimate loaded; the wireframe only shows synthetic food-need flags.',
      note: '7.1.[CONTEXT-VISION]_Food and Nutrition_Insecurity.pdf; pp. 1 and 4; version 2, 3 September 2026.'
    },
    ecosystems: {
      contribution: 'Locate candidate interventions relative to existing ecosystems once appropriate layers are agreed.',
      label: 'Key ecosystem extent', type: 'Vision', unit: 'Hectares',
      meaning: 'Extent of forests, grasslands, shrublands, mangroves and corals. Extent is not ecosystem condition, improvement or a project result.',
      calculation: 'Areas collated by country using World Bank official boundaries; no percentage denominator. A local overlay must specify the same ecosystem definitions, dates and overlap handling.',
      data: 'The note maps forest/shrubland/grassland to ESA WorldCover (10 m), mangroves to Global Mangrove Watch with WorldCover fallback, and corals to Allen Coral Atlas Reef Habitat v2.0 (5 m). These are reference mappings, not configured input bindings.',
      status: 'No ecosystem dataset loaded. Synthetic biodiversity-pressure flags and opportunity hectares are not ecosystem extent.',
      note: '[VISION]_Key Ecosystems.pdf; pp. 1, 3–4; version 1, 5 June 2024.'
    },
    conservation: {
      contribution: 'Shortlist candidate areas and specify the nature improvements to test.',
      label: 'Enhanced conservation / management', type: 'WBG result', unit: 'Hectares; corporate totals may use millions',
      meaning: 'Terrestrial and aquatic areas improved through WBG-supported protection, conservation, restoration or sustainable management, with documented nature benefits.',
      calculation: 'Count qualifying area with evidence of improvement or eligible progress proxies, a baseline and attribution to supported activities. No percentage denominator. Address spatial overlap before aggregation.',
      data: 'Project records plus monitoring, surveys or earth observation; the method requires evidence of nature benefits. A land-cover map alone cannot establish enhancement.',
      status: 'Not estimated. Candidate hectares are not enhanced hectares; habitat conversion and project biodiversity offsets are not qualifying results.',
      note: '5.3.[RESULTS]_Terrestrial and Aquatic Areas.pdf; Definition, Inclusion Criteria and Method of Calculation.'
    },
    resilience: {
      contribution: 'Identify exposed communities and develop an intervention-to-resilience pathway.',
      label: 'Enhanced climate resilience', type: 'WBG result', unit: 'People; corporate totals may use millions',
      meaning: 'Beneficiaries whose resilience to climate risks is enhanced through qualifying project support. Exposure alone does not demonstrate benefit.',
      calculation: 'Identify direct beneficiaries of high-intensity support linked to climate vulnerability and resilience outcomes, following the retrieved note. No percentage denominator. Deduplicate people across interventions.',
      data: 'Project activity, reach and outcome evidence; qualifying beneficiaries may differ from residents or total participants. Review the applicable reporting guidance with the TTL.',
      status: 'Not estimated. Neither synthetic residents nor the optional assumed participant count is a verified resilience result.',
      note: '5.2.[RESULTS]_Resilience to Climate Risks.pdf; Definition, Inclusion Criteria and Method of Calculation; version 1, 17 October 2024.'
    },
    protected: {
      contribution: 'Flag conservation context and prompt activity-specific permission checks.',
      label: 'Protected terrestrial / aquatic share', type: 'Client context', unit: '% of surface area',
      meaning: 'Country coverage by protected areas and other effective area-based conservation measures (OECMs). This is an official context indicator, not a standalone WBG project-results measure.',
      calculation: 'Protected-area/OECM coverage on land (including inland waters) and in territorial waters / total land (including inland waters) and territorial-water area × 100. Match geography and remove overlapping designations; retain terrestrial/inland-water and coastal/marine breakdowns.',
      data: 'Retrieved note uses Protected Planet WDPA + WD-OECM pending GBF indicator 3.1. It notes that the WDI protected-area series excludes OECMs. Check the actual release and coverage before use.',
      status: 'Not calculated. The purple context marks are fictional. Protected overlap / candidate opportunity would be a different local diagnostic, not this national indicator.',
      note: '5.3.[CONTEXT]_Terrestrial and Aquatic Areas.pdf; pp. 1–4, calculation p. 3; version 1, 28 March 2024.'
    }
  };
  function crosswalk() {
    return '<p><b>Three context/vision measures; two project-results measures.</b> None is calculated by this wireframe. Definitions checked against the Bank’s methodology download dated 9 October 2026.</p><div class="table-scroll"><table><thead><tr><th>Suggested indicator</th><th>Role / unit</th><th>What this scan can support</th><th>Inspect</th></tr></thead><tbody>' + Object.entries(indicators).map(([k,e]) => `<tr><td>${esc(e.label)}</td><td>${esc(e.type)}<br>${esc(e.unit)}</td><td>${esc(e.contribution)}<br><small>${esc(e.status)}</small></td><td><button data-info="bank-${k}">Definition: ${esc(e.label)}</button></td></tr>`).join('') + '</tbody></table></div><p>' + link(methods,'Bank methodology pack (ZIP, 9 October 2026)') + ' · ' + link('https://scorecard.worldbank.org/en/scorecard','Current official indicator listing') + '</p>';
  }
  function indicator(key) {
    const e = indicators[key]; if (!e) return null;
    return [e.label, facts([
      ['Role and unit',esc(e.type+' · '+e.unit)], ['Meaning',esc(e.meaning)],
      ['Calculation and denominator',esc(e.calculation)], ['Source mapping',esc(e.data)],
      ['Wireframe status',esc(e.status)], ['Source and locator',link(methods,'Official methodology pack (ZIP)')+'<br>'+esc(e.note)]
    ]) + (key==='protected'?'<div class="notice"><b>Two denominators, two questions — invented arithmetic:</b><p>A country with 200 protected/OECM hectares out of 1,000 total hectares has 20% coverage. A 100-ha candidate footprint overlapping 30 protected hectares has 30% overlap. Neither number measures conservation improvement or establishes whether an activity is permitted.</p></div>':'')];
  }
  const costs = {
    agro: {
      name: 'Planted silvoarable agroforestry', value: 'AGFORWARD model case: €753.28/ha tree establishment; €51.40/ha/year average tree maintenance. One case, not a cost range.',
      context: 'Bedfordshire, England: poplar with arable crops, 156 trees per system hectare; a 30-year model with cropping for 14 years. Report updated October 2017. Sterling costs were reported in euros at £1 = €1.389; no common price year for the tree costs is established here. This is not a Sierra Leone quotation.',
      coverage: 'Table 11 covers the tree component; crop costs are separate in Table 10. Establishment includes itemised plants, protection, mulch, ground preparation and labour. The table also lists weeding, pruning, harvest and administration. Its maintenance figure is an annual average, not a year-by-year spending schedule.',
      limits: 'The planted-tree/cropland arrangement matches this example; species, design, wages and context do not transfer automatically. Obtain dated local quantities, quotes and a maintenance schedule. Do not add itemised components to their totals or treat the annual average as a verified first-five-year budget. Calculator defaults stay invented; no currency conversion or source-to-budget transfer runs.',
      url: 'https://agforward.eu/documents/Deliverable%206.18%20Modelling%20the%20economics%20of%20agroforestry%202.pdf#page=30', source: 'García de Jalón et al. (2017), AGFORWARD Deliverable 6.18', locator: '§§4.3.1–4.3.3, pp. 27–29: case, model and price basis; Table 11, p. 30, Silvoarable column. Model assumptions, not an approved T6E synthesis.'
    },
    forest: {
      name: 'Forest restoration · tree planting', value: 'FAO indicative range: US$1,000–3,000 per hectare for planting plus three years of maintenance and monitoring.',
      context: 'General restoration guidance for full replanting. It does not specify a common price year or a Sierra Leone cost basis; it is not a current local quotation or a statistical confidence interval.',
      coverage: 'Includes seedling production and materials/labour for planting, maintenance and monitoring over three years. The passage does not establish a complete local land, opportunity-cost, safeguards or financing budget.',
      limits: 'Do not enter this combined total as establishment cost and add the same maintenance again. Separate cost components, align the horizon and obtain local prices before using the calculator.',
      url: faoForest, source: 'FAO Sustainable Forest Management Toolbox', locator: 'Forest restoration, section 3: “Establish realistic time schedules and plan for financial requirements”.'
    },
    water: {
      name: 'Water harvesting · contour stone bunds', value: 'FAO layout example: 50 person-days/ha with stones in-field versus 75 with local wheelbarrow transport.',
      context: 'Historical dryland guidance (1991), Table 24: small stone bunds, 0.05 m² cross-section, 20 m spacing, 25 m³ stone/ha. These are the source’s assumptions, not selected design rules.',
      coverage: 'Labour quantities for that layout, not currency costs. Local wages, stone purchase/transport, supervision, repairs and maintenance need separate estimates.',
      limits: 'The source’s hectare refers to a specified treated-field layout. Applicability-zone hectares cannot supply installed bund length or treated area. No automatic conversion or hectare-return calculation is enabled.',
      url: faoBunds, source: 'FAO / Critchley and Siegert (1991)', locator: 'Water harvesting manual, §5.7.2, Table 24 and its productivity note.'
    }
  };
  function costContext(nbs) {
    const e = costs[nbs];
    return `<h3>${esc(e.name)}</h3><p><b>${esc(e.value)}</b></p>${facts([
      ['Context and price basis',esc(e.context)], ['Cost coverage',esc(e.coverage)], ['Before local use',esc(e.limits)],
      ['Source and locator',link(e.url,e.source)+'<br>'+esc(e.locator)]
    ])}<p>Curated reading only; no approved T6E value loaded. Changing the viewed practice does not apply this reading to your budget inputs.</p>`;
  }
  function brief(nbs) {
    const e = costs[nbs];
    return `ECONOMIC CONTEXT — ${e.name}: ${e.value} ${e.context} ${e.limits} Source: ${e.source}, ${e.url} (${e.locator}). This reading has not populated the calculator. BANK ALIGNMENT — food insecurity, key ecosystems and protected/OECM coverage describe context or vision; enhanced conservation hectares and resilience beneficiaries require qualifying project evidence. No official indicator value is estimated here. Confirm baselines, units, boundaries, overlaps and reporting eligibility with the TTL. Definitions: ${methods}`;
  }
  return Object.freeze({crosswalk, indicator, costContext, brief});
})();
