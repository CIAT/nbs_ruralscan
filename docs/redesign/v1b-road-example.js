/* Authored Haiti review fixture. Roads and distances are fictional. */
(function () {
  'use strict';
  const hazards = {
    flood: ['River flood', '1-in-100-year river inundation', 3, 1],
    landslide: ['Landslide', 'High modelled landslide hazard', 2, 2],
    fire: ['Wildfire', 'Historical detected burn footprint', 1, 0]
  };
  const departments = [{name: 'A', base: 0.72, assessed: 50}, {name: 'B', base: 0.65, assessed: 50}];
  // Each row is one distinct road section.
  const roads = [
    {id: 'A1', name: 'Market crossing', km: 2, hazards: ['flood']},
    {id: 'A2', name: 'Valley road', km: 6, hazards: ['flood', 'landslide']},
    {id: 'B1', name: 'School access road', km: 5, hazards: ['flood', 'fire']},
    {id: 'B2', name: 'Clinic crossing', km: 3, hazards: ['flood']},
    {id: 'B3', name: 'Ridge approach', km: 2, hazards: ['flood', 'fire']},
    {id: 'B4', name: 'Hillside road', km: 6, hazards: ['landslide']}
  ];
  const key = 'v2-road-exposure-priority';
  let state = {hazard: 'flood', enabled: false, weight: 20};
  function load() {
    try {
      const saved = JSON.parse(localStorage.getItem(key));
      if (!saved) return;
      if (Object.hasOwn(hazards, saved.hazard)) state.hazard = saved.hazard;
      state.enabled = saved.enabled === true;
      if (Number.isInteger(saved.weight) && saved.weight >= 0 && saved.weight <= 50) state.weight = saved.weight;
    } catch (_) { /* Keep defaults when browser storage is unavailable. */ }
  }
  function update(field, value) {
    load();
    state[field] = value;
    try { localStorage.setItem(key, JSON.stringify(state)); } catch (_) {}
    render();
  }
  const byId = id => document.getElementById(id);
  const sum = rows => rows.reduce((total, road) => total + road.km, 0);
  function render() {
    const hazard = hazards[state.hazard];
    const exposed = roads.filter(road => road.hazards.includes(state.hazard));
    if (byId('service-assets')) {
      byId('service-hazard').value = state.hazard;
      byId('service-layer').textContent = hazard[1];
      byId('service-assets').innerHTML = [
        ['Rural roads (km)', sum(exposed), departments.reduce((total, d) => total + d.assessed, 0), 6], ['Schools', hazard[2], 20, 2], ['Health facilities', hazard[3], 8, 1]
      ].map(a => '<tr><th scope="row">' + a[0] + '</th>' + a.slice(1).map(n => '<td>' + n + '</td>').join('') + '</tr>').join('');
      byId('road-sections').innerHTML = exposed.map(r => '<tr><th scope="row">' + r.id + ' · ' + r.name + '</th><td>' + r.id[0] + '</td><td>' + r.km + '</td></tr>').join('');
      byId('road-result').textContent = sum(exposed) + ' km overlap the selected hazard across the two departments.';
      return;
    }
    const weight = state.enabled ? state.weight / 100 : 0;
    const results = departments.map(d => {
      const sections = exposed.filter(r => r.id.startsWith(d.name));
      const km = sum(sections);
      const share = km / d.assessed;
      return {...d, km, sections, share, score: (1 - weight) * d.base + weight * share};
    });
    const enabled = byId('use-services');
    enabled.checked = state.enabled;
    byId('service-weight-control').hidden = !enabled.checked;
    byId('service-weight').value = state.weight;
    byId('service-percent').textContent = state.weight + '%';
    byId('service-context').textContent = hazard[0] + '. Give more priority to departments where a larger share of assessed rural roads overlaps the hazard. The example assumes comparable inventory coverage.';
    byId('road-input').textContent = results.map(d => d.name + ': ' + d.km + ' exposed of ' + d.assessed + ' assessed km').join(' · ');
    byId('road-ranks').innerHTML = results.map(d => {
      const rank = 1 + results.filter(other => other.score > d.score).length;
      const baseRank = 1 + results.filter(other => other.base > d.base).length;
      return '<tr><th scope="row">' + d.name + '</th><td>' + (d.sections.map(r => r.id).join(', ') || 'None') + '</td><td>' + d.km + ' / ' + d.assessed + '</td><td>' + d.base.toFixed(3) + '</td><td>' + d.score.toFixed(3) + '</td><td>' + baseRank + ' → ' + rank + '</td></tr>';
    }).join('');
    const [a, b] = results;
    let explanation = 'With the priority off, A leads on its base score.';
    if (weight > 0) {
      const outcome = b.score > a.score ? 'B overtakes A' : (b.score === a.score ? 'A and B tie' : 'A still leads');
      explanation = outcome + ' at this weight. Exposed sections account for ' + Math.round(b.share * 100) + '% of B’s assessed road length and ' + Math.round(a.share * 100) + '% of A’s.';
    }
    byId('rank-reason').textContent = explanation;
    byId('rank-formula').textContent = 'Selected score = ' + Math.round((1-weight)*100) + '% × base score + ' + Math.round(weight*100) + '% × exposed share of assessed road length. ' + hazard[0] + '.';
  }
  function bind(id, event, field, read) {
    const input = byId(id);
    if (input) input.addEventListener(event, () => update(field, read(input)));
  }
  bind('service-hazard','change','hazard', el => el.value);
  bind('use-services','change','enabled', el => el.checked);
  bind('service-weight','input','weight', el => Number(el.value));
  function refresh() { load(); render(); }
  window.addEventListener('pageshow', refresh);
  window.addEventListener('storage', event => { if (event.key === key) refresh(); });
  refresh();
})();
