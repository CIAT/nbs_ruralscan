/* Authored Haiti review fixture. Distances and catchment links are fictional. */
(function () {
  'use strict';
  const hazards = {
    flood: ['River flood', '1-in-100-year river inundation', 3, 1],
    landslide: ['Landslide', 'High modelled landslide hazard', 2, 2],
    fire: ['Wildfire', 'Historical detected burn footprint', 1, 0]
  };
  const departments = [{name: 'A', base: 0.72}, {name: 'B', base: 0.65}];
  // Each row is one distinct road section. A reach identifies the watercourse at its crossing.
  const roads = [
    {id: 'A1', name: 'Market crossing', km: 2, reach: 'North Fork', hazards: ['flood']},
    {id: 'A2', name: 'Valley road', km: 6, reach: 'West Fork', hazards: ['flood', 'landslide']},
    {id: 'B1', name: 'School access road', km: 5, reach: 'East Fork', hazards: ['flood', 'fire']},
    {id: 'B2', name: 'Clinic crossing', km: 3, reach: 'East Fork', hazards: ['flood']},
    {id: 'B3', name: 'Ridge approach', km: 2, reach: null, hazards: ['flood', 'fire']},
    {id: 'B4', name: 'Hillside road', km: 6, reach: null, hazards: ['landslide']}
  ];
  const upstreamBuffers = new Set(['North Fork', 'East Fork']);
  const key = 'v2-road-priority';
  let state = {hazard: 'flood', practice: 'buffer', enabled: false, weight: 20};
  function load() {
    try {
      const saved = JSON.parse(localStorage.getItem(key));
      if (!saved) return;
      if (Object.hasOwn(hazards, saved.hazard)) state.hazard = saved.hazard;
      if (['buffer', 'trees'].includes(saved.practice)) state.practice = saved.practice;
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
    const supported = state.hazard === 'flood' && state.practice === 'buffer';
    const practice = state.practice === 'buffer' ? 'Natural or restored riparian buffer' : 'Planted silvoarable agroforestry';
    const exposed = roads.filter(road => road.hazards.includes(state.hazard));
    const candidates = exposed.filter(road => supported && upstreamBuffers.has(road.reach));
    const reason = supported ? 'Riparian vegetation may slow flow. The example assumes comparable road coverage and a distinct service priority after checking overlap with livelihood risk.'
      : 'This example has no supported road-protection pathway for this practice and hazard. Exposure remains visible and the base ranking applies.';
    function pathway(road) {
      if (!supported) return 'Exposure only · practice effect unresolved';
      if (!road.reach) return 'Exposure only · drainage connection unknown';
      if (!upstreamBuffers.has(road.reach)) return 'Exposure only · no upstream buffer on ' + road.reach;
      return 'Candidate · buffer upstream on ' + road.reach + ' drains to this crossing';
    }
    if (byId('service-assets')) {
      byId('service-hazard').value = state.hazard;
      byId('service-practice').value = state.practice;
      byId('service-layer').textContent = hazard[1];
      byId('service-assets').innerHTML = [
        ['Rural roads (km)', sum(exposed), 100, 6], ['Schools', hazard[2], 20, 2], ['Health facilities', hazard[3], 8, 1]
      ].map(a => '<tr><th scope="row">' + a[0] + '</th>' + a.slice(1).map(n => '<td>' + n + '</td>').join('') + '</tr>').join('');
      byId('road-sections').innerHTML = exposed.map(r => '<tr><th scope="row">' + r.id + ' · ' + r.name + '</th><td>' + r.id[0] + '</td><td>' + r.km + '</td><td>' + pathway(r) + '</td></tr>').join('');
      byId('road-result').textContent = sum(candidates) + ' of ' + sum(exposed) + ' exposed km have a supported pathway in this example. ' + reason;
      return;
    }
    const weight = supported && state.enabled ? state.weight / 100 : 0;
    const results = departments.map(d => {
      const km = sum(exposed.filter(r => r.id.startsWith(d.name)));
      const linked = candidates.filter(r => r.id.startsWith(d.name));
      const share = km ? sum(linked) / km : 0;
      return {...d, km, linked, share, score: (1 - weight) * d.base + weight * share};
    });
    const enabled = byId('use-services');
    enabled.disabled = !supported;
    enabled.checked = supported && state.enabled;
    byId('service-weight-control').hidden = !enabled.checked;
    byId('service-weight').value = state.weight;
    byId('service-percent').textContent = state.weight + '%';
    byId('service-context').textContent = practice + ' · ' + hazard[0] + '. ' + reason;
    byId('road-input').textContent = results.map(d => d.name + ': ' + sum(d.linked) + ' of ' + d.km + ' exposed km').join(' · ');
    byId('road-ranks').innerHTML = results.map(d => {
      const rank = 1 + results.filter(other => other.score > d.score).length;
      const baseRank = 1 + results.filter(other => other.base > d.base).length;
      return '<tr><th scope="row">' + d.name + '</th><td>' + (d.linked.map(r => r.id).join(', ') || 'None') + '</td><td>' + sum(d.linked) + ' / ' + d.km + '</td><td>' + d.base.toFixed(3) + '</td><td>' + d.score.toFixed(3) + '</td><td>' + baseRank + ' → ' + rank + '</td></tr>';
    }).join('');
    const [a, b] = results;
    let explanation = 'With the priority off, A leads on its base score.';
    if (!supported) explanation = 'No supported pathway has been identified for this combination. Both departments keep their base ranks.';
    else if (weight > 0) {
      const outcome = b.score > a.score ? 'B overtakes A' : (b.score === a.score ? 'A and B tie' : 'A still leads');
      explanation = outcome + ' at this weight. Candidate sections account for ' + Math.round(b.share * 100) + '% of B’s exposed road length and ' + Math.round(a.share * 100) + '% of A’s.';
    }
    byId('rank-reason').textContent = explanation;
    byId('rank-formula').textContent = 'Selected score = ' + Math.round((1-weight)*100) + '% × base score + ' + Math.round(weight*100) + '% × candidate share of exposed road length. ' + practice + ' · ' + hazard[0] + '.';
  }
  function bind(id, event, field, read) {
    const input = byId(id);
    if (input) input.addEventListener(event, () => update(field, read(input)));
  }
  bind('service-hazard','change','hazard', el => el.value);
  bind('service-practice','change','practice', el => el.value);
  bind('use-services','change','enabled', el => el.checked);
  bind('service-weight','input','weight', el => Number(el.value));
  function refresh() { load(); render(); }
  window.addEventListener('pageshow', refresh);
  window.addEventListener('storage', event => { if (event.key === key) refresh(); });
  refresh();
})();
