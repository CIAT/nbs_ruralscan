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
  // Fictional review data only. No analytical schema rules or pilot results.
  const assets = {
    schools: {label:'Schools',unit:'facilities',assessed:[10,10],missing:2, flood:[0,3],landslide:[1,1],fire:[0,1]},
    health: {label:'Health facilities',unit:'facilities',assessed:[4,4],missing:1,flood:[0,1],landslide:[1,1],fire:[0,0]},
    population: {label:'People in populated areas',unit:'people',assessed:[10000,10000],missing:1500,flood:[500,6000],landslide:[1200,2000],fire:[300,900]}
  };
  const key = 'v2-2-infrastructure-exposure-priority';
  let state = {hazard: 'flood', enabled: false, weight: 20, asset: 'roads'};
  function load() {
    try {
      const saved = JSON.parse(localStorage.getItem(key));
      if (!saved) return;
      if (Object.hasOwn(hazards, saved.hazard)) state.hazard = saved.hazard;
      state.enabled = saved.enabled === true;
      if (['roads','schools','health','population'].includes(saved.asset)) state.asset=saved.asset;
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
    window.dispatchEvent(new CustomEvent("infrastructure-exposure-change"));
    const hazard = hazards[state.hazard];
    const exposed = roads.filter(road => road.hazards.includes(state.hazard));
    if (byId('service-assets')) {
      byId('service-hazard').value = state.hazard;
      byId('service-layer').textContent = hazard[1];
      byId('service-assets').innerHTML = [
        ['Rural roads (km)', sum(exposed), departments.reduce((total, d) => total + d.assessed, 0), 6], ...Object.values(assets).map(a=>[a.label+' ('+a.unit+')',a[state.hazard][0]+a[state.hazard][1],a.assessed[0]+a.assessed[1],a.missing])
      ].map(a => '<tr><th scope="row">' + a[0] + '</th>' + a.slice(1).map(n => '<td>' + n + '</td>').join('') + '</tr>').join('');
      byId('road-sections').innerHTML = exposed.map(r => '<tr><th scope="row">' + r.id + ' · ' + r.name + '</th><td>' + r.id[0] + '</td><td>' + r.km + '</td></tr>').join('');
      byId('road-result').textContent = sum(exposed) + ' km overlap the selected hazard across the two departments.';
      return;
    }
    const weight = state.enabled ? state.weight / 100 : 0;
    const results = departments.map((d,i) => {
      const sections = exposed.filter(r => r.id.startsWith(d.name));
      const km = sum(sections);
      const asset=assets[state.asset];
      const amount=asset?asset[state.hazard][i]:km;
      const assessed=asset?asset.assessed[i]:d.assessed;
      const share=amount/assessed;
      return {...d, km, sections, share, amount, assessed, score: (1 - weight) * d.base + weight * share};
    });
    const enabled = byId('use-services');
    if(!enabled)return;
    byId('service-asset').value=state.asset;
    const label=state.asset==='roads'?'Rural roads':assets[state.asset].label;
    const unit=state.asset==='roads'?'km':assets[state.asset].unit;
    enabled.checked = state.enabled;
    byId('service-weight-control').hidden = !enabled.checked;
    byId('service-weight').value = state.weight;
    byId('service-percent').textContent = state.weight + '%';
    byId('service-context').textContent = hazard[0] + ' · '+label+'. Higher exposed share receives more priority. Comparable inventory coverage is assumed. This is a proposed scoping indicator, not an estimate of protection.';
    byId('road-input').textContent = results.map(d => d.name + ': ' + d.amount + ' exposed of ' + d.assessed + ' assessed '+unit).join(' · ');
    byId('road-ranks').innerHTML = results.map(d => {
      const rank = 1 + results.filter(other => other.score > d.score).length;
      const baseRank = 1 + results.filter(other => other.base > d.base).length;
      return '<tr><th scope="row">' + d.name + '</th><td>' + (state.asset==='roads'?(d.sections.map(r => r.id).join(', ') || 'None'):label) + '</td><td>' + d.amount + ' / ' + d.assessed+' '+unit + '</td><td>' + d.base.toFixed(3) + '</td><td>' + d.score.toFixed(3) + '</td><td>' + baseRank + ' → ' + rank + '</td></tr>';
    }).join('');
    const [a, b] = results;
    let explanation = 'With the priority off, A leads on its base score.';
    if (weight > 0) {
      const outcome = b.score > a.score ? 'B overtakes A' : (b.score === a.score ? 'A and B tie' : 'A still leads');
      explanation = outcome + ' at this weight. Exposure accounts for ' + Math.round(b.share * 100) + '% of B’s assessed '+label.toLowerCase()+' and ' + Math.round(a.share * 100) + '% of A’s.';
    }
    byId('rank-reason').textContent = explanation;
    byId('rank-formula').textContent = 'Selected score = ' + Math.round((1-weight)*100) + '% × base score + ' + Math.round(weight*100) + '% × exposed share of assessed ' + label.toLowerCase() + '. ' + hazard[0] + '.';
  }
  function bind(id, event, field, read) {
    const input = byId(id);
    if (input) input.addEventListener(event, () => update(field, read(input)));
  }
  bind('service-asset','change','asset', el => el.value);
  bind('service-hazard','change','hazard', el => el.value);
  bind('use-services','change','enabled', el => el.checked);
  bind('service-weight','input','weight', el => Number(el.value));
  function refresh() { load(); render(); }
  window.addEventListener('pageshow', refresh);
  window.addEventListener('storage', event => { if (event.key === key) refresh(); });
  refresh();
})();
