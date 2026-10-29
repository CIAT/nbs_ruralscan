/* Curated reading examples, not T3/T6 synthesis or local effect predictions.
   Source passages checked 2026-10-29. No register or runtime data are loaded. */
window.WireframeEvidence = (() => {
  'use strict';
  const examples = {
    agro: {
      name: 'Planted silvoarable agroforestry',
      author: 'Chalupecká et al. (2026)',
      title: 'Early-stage alley cropping: soil moisture and temperature',
      url: 'https://link.springer.com/article/10.1007/s10457-026-01436-4',
      locator: 'Results: “Infiltration characteristics of arable fields and tree alleys”, Table 3; Conclusions.',
      basis: 'Single early-stage field study; Czech temperate silt-loam site, 2023–2024.',
      finding: 'Tree alleys had higher infiltration than adjacent recently harvested arable soil. Soil moisture also depleted faster in some periods.',
      fit: 'Alley cropping matches the planted-tree/arable arrangement. Dense understory versus crusted harvested soil complicates attribution to trees alone. This is not tropical pilot evidence.',
      question: 'Measure seasonal root-zone moisture, infiltration and crop response with a suitable comparator; assess tree–crop water competition.',
      summary: 'Higher infiltration in one field study; moisture depletion also observed.',
      outcome: 'Root-zone soil water; not an aquifer recharge measurement.'
    },
    forest: {
      name: 'Forest restoration · tree establishment',
      author: 'Filoso et al. (2017)',
      title: 'Impacts of forest restoration on water yield: A systematic review',
      url: 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0183210',
      locator: 'Abstract, Results and Discussion; Fig. 3 (direction of water-yield change).',
      basis: 'Systematic review of restoration and other forest-cover expansion interventions; literature searched through 2015.',
      finding: 'Most studies reported lower water yield after forest-cover expansion. Other hydrological benefits do not guarantee increased water supply.',
      fit: 'The review includes afforestation and forestry, not only native restoration. Native-restoration, humid-tropical and long-term evidence was limited; it does not isolate this pilot’s design.',
      question: 'Commission a catchment water balance, seasonal flow baseline and downstream-user assessment; distinguish planting design, previous land cover and establishment period.',
      summary: 'Water yield often decreased in a mixed-intervention review; local direction unresolved.',
      outcome: 'Catchment water yield; distinct from infiltration and water quality.'
    },
    water: {
      name: 'Water harvesting · contour bunds',
      author: 'FAO / Critchley and Siegert (1991)',
      title: 'Water harvesting manual: contour stone bunds',
      url: 'https://www.fao.org/4/u3160e/u3160e07.htm',
      locator: 'Sections 5.7.1 Background, 5.7.2 Technical details, 5.7.4 Maintenance and 5.7.6 Socio-economic factors.',
      basis: 'Practitioner manual; contour stone bunds for crops in dryland West Africa.',
      finding: 'Stone lines slow runoff, encourage infiltration and capture sediment. Heavy runoff can dislodge stones; accumulated sediment requires maintenance.',
      fit: 'A stone-bund subtype example, not evidence for every earth-bund design. Dryland context, stone supply, labour and maintenance must match. No local measured effect size is supplied.',
      question: 'Confirm bund material and purpose, runoff paths, soil infiltration, crop demand and maintenance capacity; check downstream users and safe handling of excess flow.',
      summary: 'Infiltration and sediment-retention rationale from guidance; no local effect estimate.',
      outcome: 'Field runoff and soil-water retention; not a measured groundwater or downstream-flow gain.'
    }
  };
  const esc = x => String(x).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const source = e => `<a href="${e.url}" target="_blank" rel="noopener">${esc(e.author)} — ${esc(e.title)}</a>`;
  const facts = rows => `<dl class="info-list">${rows.map(([k,v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join('')}</dl>`;
  function response(nbs) {
    const e = examples[nbs];
    return `<h3>${esc(e.name)}: what does the source support?</h3><p>${esc(e.finding)}</p>${facts([
      ['Evidence basis', esc(e.basis)], ['Practice and context match', esc(e.fit)],
      ['Effect strength', 'Direction described above; no synthesised strength class or local magnitude assigned.'],
      ['Evidence confidence', 'Study design is shown, not converted into a confidence score. Formal confidence requires the reviewed evidence pool and agreement assessment; local transfer remains unassessed.'],
      ['Source and locator', source(e) + '<br>' + esc(e.locator)],
      ['Review status', 'Published passage checked for this reading example. No approved EV/T3/T6 value is claimed or loaded.']
    ])}<p><b>Scoping question:</b> ${esc(e.question)}</p>`;
  }
  function hydrology(nbs) {
    const e = examples[nbs];
    return `<h3>${esc(e.name)}</h3><ol><li><b>Need:</b> the displayed water-stress share is synthetic. Real targeting needs seasonal, location-appropriate demand/supply evidence.</li><li><b>Outcome to investigate:</b> ${esc(e.outcome)}</li><li><b>Source finding and limitation:</b> ${esc(e.finding)} ${esc(e.fit)} ${source(e)}.</li><li><b>Local study brief:</b> ${esc(e.question)}</li></ol><p><b>Data fitness:</b> no local rainfall, flow, soil-moisture, groundwater or quality observations are connected. Check season, spatial scale, units, baseline and comparator before transfer. No recharge volume or water-quality result is estimated.</p>`;
  }
  function resources(nbs) {
    const e = examples[nbs];
    return `<h3>${esc(e.name)}</h3><ul><li>${source(e)}<br>${esc(e.locator)}<br>${esc(e.basis)}</li><li><a href="scorecard.html" target="_blank" rel="noopener">Current project evidence scorecard</a> — inspect the evolving synthesis and its provenance separately; this example does not load or certify it.</li></ul><p><b>Use the reading to prepare local follow-up:</b> ${esc(e.question)}</p>`;
  }
  function comparison() {
    return '<p>These readings cover different outcomes and evidence designs; they cannot rank the practices against one another.</p><div class="actions">' + Object.entries(examples).map(([key,e]) => `<button data-info="effect-${key}">Inspect ${esc(e.name)} evidence</button>`).join('') + '</div>';
  }
  function brief(nbs) {
    const e = examples[nbs];
    return `EVIDENCE READING — ${e.name}: ${e.finding} ${e.fit} Source: ${e.author}, ${e.url} (${e.locator}). This is a curated reading, not an approved synthesis or local impact prediction; strength and local confidence are not assigned. Follow-up: ${e.question}`;
  }
  function ai(nbs) {
    const e = examples[nbs];
    return `<b>Scripted question — no model running:</b> “Can this source justify a local water-benefit claim?”<p>No local benefit claim is established. ${esc(e.fit)}</p><p>Proposed next step: ${esc(e.question)} ${source(e)}.</p>`;
  }
  return Object.freeze({response, hydrology, resources, comparison, brief, ai, summary: nbs => examples[nbs].summary});
})();
