/* Isolated teaching module. Static examples only: no dataset fetch, schema import,
   slope calculation, binding resolution or main-map updates. */
window.WireframeInputs = (() => {
  'use strict';
  const method = 'https://github.com/CIAT/nbs_ruralscan/blob/968eb0b84096d35bdb3f86e9e4a1fb49a1dc446e/methodology/examples/t4_cross_paper_harmonization.md';
  const dem = 'https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30_2024_1';
  const poverty = 'https://datacatalog.worldbank.org/search/dataset/0064796/subnational-poverty-and-inequality-database-spid';
  const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link = (url, label) => `<a href="${url}" target="_blank" rel="noopener">${label}</a>`;
  function rows(items) {
    return `<dl class="input-facts">${items.map(([name,value])=>`<dt>${name}</dt><dd>${value}</dd>`).join('')}</dl>`;
  }
  const sources = {
    suit: {
      catalogue: [
        ['Candidate', 'Copernicus DEM GLO-30, release 2024_1 — catalogue example, not the configured project default.'],
        ['Measured quantity', 'Surface elevation in metres; includes vegetation and buildings. Slope would be a derived input in explicitly declared units.'],
        ['Coverage and scale', 'Global product; nominal 30 m pixels. Check target-area coverage and quality before use.'],
        ['Date and uncertainty', 'A composite surface, not a current terrain survey. Inspect acquisition lineage, height-error and filling masks.'],
        ['Before adoption', 'Check surface versus bare-earth requirements, native projection, derivative scale, missing values and licence. Derive slope before spatial aggregation.'],
        ['Source', link(dem,'Provider catalogue and slope-processing example')]
      ],
      local: [
        ['Candidate', 'Fictional district terrain survey — unreviewed local override proposal. No such file has been supplied.'],
        ['Proposed metadata', 'Bare-earth elevation, metres; nominal 10 m; surveyed in 2025; target districts only. All metadata here are invented for this exercise.'],
        ['Missing proof', 'Producer, survey report, horizontal/vertical datum, accuracy, licence, coverage and country endorsement. Finer pixels alone do not establish better fitness.'],
        ['Outside local coverage', 'Keep the accepted broader input only where definitions and datum are compatible; otherwise show an unresolved gap. Do not silently mix products.'],
        ['Before adoption', 'Validate metadata and data quality, then review a context-specific binding. A dataset replacement does not authorise a new suitability relationship.']
      ]
    },
    priority: {
      catalogue: [
        ['Candidate', 'World Bank Subnational Poverty and Inequality Database (SPID) — catalogue example; country/year availability not checked here.'],
        ['Measured quantity', 'Poverty estimates from household surveys. Choose the poverty line, price basis, population definition and survey year explicitly.'],
        ['Coverage and scale', 'The catalogue describes administrative level 1 estimates. Displaying them on fine pixels does not create within-region detail.'],
        ['Uncertainty', 'Sampling uncertainty, comparable definitions and boundary versions matter. Total-population poverty is not automatically rural poverty.'],
        ['Before adoption', 'Confirm a suitable rural measure and valid geographic variation; treat national-only data as context. No values from SPID are loaded.'],
        ['Source', link(poverty,'World Bank dataset description')]
      ],
      local: [
        ['Candidate', 'Fictional district rural-poverty estimates — unreviewed proposal, not an available national dataset.'],
        ['Proposed metadata', 'Rural population below a stated poverty line, district units, 2025. These attributes are hypothetical.'],
        ['Missing proof', 'National statistical source, survey/model documentation, population denominator, poverty line/PPP basis, uncertainty and official boundary crosswalk.'],
        ['Comparison with catalogue', 'Finer geography and a rural denominator could better match the question, but a different line, year or estimation method may prevent direct comparison.'],
        ['Before adoption', 'Confirm country endorsement and fitness. Review context binding separately from normalisation, correlation handling and weights.']
      ]
    }
  };
  function dataset(surface, choice) {
    const key=surface==='suit'?'suitDataset':'priorityDataset';
    return `<div class="technical-step"><h2>1. Compare candidate inputs</h2>
      <p>Inspect a real catalogue description or a fictional local proposal. This choice changes only the teaching card; it does not select an analytical input.</p>
      <label for="input-example">Inspect candidate
      <select id="input-example" data-input-setting="${key}">
        <option value="catalogue" ${choice==='catalogue'?'selected':''}>Published catalogue example</option>
        <option value="local" ${choice==='local'?'selected':''}>Local override proposal · fictional</option>
      </select></label>
      <div id="input-example-detail">${rows(sources[surface][choice])}</div>
      <details><summary>What would change after review?</summary>
        <div class="table-scroll"><table><thead><tr><th>Decision</th><th>Current teaching example</th><th>Local proposal</th></tr></thead><tbody>
        <tr><td>Dataset and context</td><td>Published catalogue candidate; not adopted</td><td>Named local source, limited geography, reviewed version</td></tr>
        <tr><td>Uncovered locations</td><td>Coverage must be checked</td><td>Explicit compatible fallback or missing-data flag</td></tr>
        <tr><td>Response / weights</td><td>Not connected</td><td>Unchanged unless separately evidenced and approved</td></tr>
        <tr><td>Approval status</td><td>No binding change</td><td>Pending data and method review; no Apply action</td></tr>
        </tbody></table></div>
        <p>The inspected candidate is remembered in saved example settings. It is not a proposed binding approved for the pipeline.</p>
      </details></div>`;
  }
  function treatment(surface) {
    const items=surface==='suit' ? [
      ['Quantitative response','A measured variable such as slope passes through a family- and context-specific response. Units, endpoints and source agreement remain visible.'],
      ['Categorical host-system gate','An observed host crop or land-use class establishes where a practice can fit. A class name is not a continuous score; the accepted class list needs evidence.'],
      ['Confirmed hard exclusion','A verified, applicable legal restriction can mask an area. Neither low suitability nor disagreement between sources creates a legal exclusion.'],
      ['Operational condition','Access, extension and finance inform Project Risk and local follow-up. Investment in these does not change natural or host-system suitability.']
    ] : [
      ['Priority input','A defensible, spatially varying need measure may enter prioritisation after its definition and treatment are agreed.'],
      ['Descriptor / national context','A useful contextual measure need not enter ranking. One national value cannot distinguish districts.'],
      ['Correlation and weight','Thematic grouping and correlation selection prevent repeated information gaining extra influence. No clustering or weighting runs here.'],
      ['Investment-risk choice','A separate shortlist filter or flag follows need prioritisation. It is not an added need score.']
    ];
    return `<div class="technical-step"><h2>2. Separate the analytical decisions</h2>${rows(items)}</div>`;
  }
  function tiles(values, colors, label) {
    return `<figure class="input-preview"><figcaption>${label}</figcaption><div class="input-tiles" role="img" aria-label="${esc(label+': '+values.join(', '))}">${values.map((value,i)=>`<span style="background:${colors[i]}">${esc(value)}</span>`).join('')}</div></figure>`;
  }
  function slopePreview(profile) {
    // Transcribed display examples from method scenarios 07–08; not a recipe or evaluator.
    const raw=['2°','7°','12°','18°','25°','No data'];
    const responses=profile==='a'?['High','Moderate','Moderate','Low','Low','Unknown']:['High','High','Moderate','Moderate','Unsuitable','Unknown'];
    const palette={High:'#c3dfd0',Moderate:'#eee3a9',Low:'#f0cfb0',Unsuitable:'#e1e3e3',Unknown:'#e9d5ed'};
    const path=profile==='a'?'M45 35 H87 V75 H170 V115 H295':'M45 35 H112 V75 H212 V145 H295';
    return `<div class="notice"><b>Hypothetical method example, not a recommendation for the selected practice.</b> Profiles A/B come from ${link(method+'#07-different-slope-cutoffs','worked method scenarios 07–08')}. No field dataset or agreed recipe is loaded.</div>
      <label for="response-example">Compare hypothetical source profiles<select id="response-example" data-input-setting="responseExample"><option value="a" ${profile==='a'?'selected':''}>Source A · hypothetical</option><option value="b" ${profile==='b'?'selected':''}>Source B · hypothetical</option></select></label>
      <div class="input-preview-pair">${tiles(raw,['#edf1f4','#e0e7eb','#cfdce3','#bccfd9','#a8c1ce','#e9d5ed'],'Raw input · six invented cells; slope in degrees')}${tiles(responses,responses.map(x=>palette[x]),'Response classes · same cell positions')}</div>
      <figure class="input-curve"><figcaption>Source ${profile.toUpperCase()}: step response, not a probability curve</figcaption><svg viewBox="0 0 340 190" role="img" aria-label="${profile==='a'?'High below 5 degrees; moderate from 5 to below 15; low from 15 upward':'High below 8 degrees; moderate from 8 through 20; unsuitable above 20'}"><path d="M45 18 V155 H310" fill="none" stroke="#526359"/><path d="${path}" fill="none" stroke="#25613e" stroke-width="3"/><g font-size="10" fill="#18382b"><text x="2" y="39">High</text><text x="2" y="79">Mod.</text><text x="2" y="119">Low</text><text x="2" y="149">Unsuit.</text><text x="43" y="172">0°</text><text x="282" y="172">30°</text><text x="125" y="187">Slope (degrees)</text></g></svg></figure>
      <p>${profile==='a'?'A assigns High below 5°, Moderate from 5° to below 15°, and Low from 15° upward.':'B assigns High below 8°, Moderate from 8° through 20°, and Unsuitable above 20°.'} Boundary inclusivity belongs to the source definition; the diagram alone cannot encode it.</p>
      <p><b>At 25° the sources disagree: Low versus Unsuitable.</b> Preserve that conflict. Do not turn it into a legal mask, or treat source disagreement as a statistical confidence interval. Missing input stays Unknown. Main opportunity maps and totals remain unchanged.</p>`;
  }
  function priorityPreview() {
    return `<p>A national observation may describe the country while providing no district-level contrast. These six invented cells demonstrate the grain issue; they are not poverty observations or normalised scores.</p>
      <div class="input-preview-pair">${tiles(['38%','38%','38%','38%','38%','38%'],Array(6).fill('#cfdce3'),'Raw input · one fictional national value repeated')}${tiles(Array(6).fill('Context'),Array(6).fill('#e6e8df'),'Treatment · no within-country ranking contribution')}</div>
      <p>A suitable subnational rural measure would still need an agreed reference frame, transformation and correlation review. No priority curve is invented to fill that gap. ${link('https://www.worldbank.org/en/data/datatopics/poverty-portal/sae','World Bank guidance on small-area estimation')} explains why survey disaggregation requires care.</p>`;
  }
  function card(surface, profile, practice) {
    const suit=surface==='suit';
    const slots=[
      ['What',suit?'Terrain slope: elevation is an input to a derivative, not slope itself. State degrees or percent explicitly; they are not interchangeable.':'Rural poverty: define the population, poverty line, year and geographic support before interpreting a percentage.'],
      ['Why (NbS-specific)',suit?`Viewing ${esc(practice)}. Terrain response must be relevant to its suitability family and context; the hypothetical profiles below are not approved for this selection.`:'Poverty can describe livelihood need intersecting each practice footprint. It does not establish that the practice reduces poverty, or belong in structural suitability.'],
      ['How to read',suit?'Check raw units, missing cells, source-specific response and applicability before a combined suitability result.':'Check denominator and spatial variation. Repeating a national value on pixels does not add information.'],
      ['What it represents (cluster)',suit?'A terrain constraint. One representative from an agreed correlation cluster enters MCDA; related variables and memberships stay visible.':'A people/production need. Poverty and food insecurity are distinct outcomes; related indicators still require correlation review.'],
      ['Where it comes from','Candidate metadata above are teaching examples. The eventual route is dataset registry → context binding → versioned input, with analytical treatment and EV → SRC evidence tracked separately. No live registers are read.']
    ];
    return `<details class="card" open><summary>Variable card · six-part explanation</summary><div class="card-slots">${slots.map(([title,body])=>`<div><h3>${title}</h3><p>${body}</p></div>`).join('')}<div class="input-response-slot"><h3>Response preview</h3>${suit?slopePreview(profile):priorityPreview()}</div></div></details>`;
  }
  return Object.freeze({render(surface, state, practice) {
    return dataset(surface,state[surface==='suit'?'suitDataset':'priorityDataset'])+treatment(surface)+card(surface,state.responseExample,practice);
  }});
})();
