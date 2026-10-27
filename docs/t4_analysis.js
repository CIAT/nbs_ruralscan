/* Read-only T4 subtabs in the existing dashboard; no review writes or analytical math. */
(function (root) {
  'use strict';
  const panels = ['evidence', 'studies', 'global', 'rules'];
  const fields = ['evidence_id','source_id','variable','suitability_family_id','relationship','context','reviewer_ok','review_state','use_role','claim_scope','quote','page'];
  function canonical(value) {
    if (Array.isArray(value)) return value.map(canonical);
    if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(k => [k, canonical(value[k])]));
    return value;
  }
  function stateOf(unit) {
    const row = Object.fromEntries(fields.map(k => [k, unit[k] || '']));
    for (const key of ['relationship','context']) {
      if (typeof row[key] === 'string') { try { row[key] = JSON.parse(row[key] || '{}'); } catch (_) { row[key] = {}; } }
    }
    row.reviewer_ok = String(row.reviewer_ok).toLowerCase() === 'true';
    row.page = String(row.page);
    return row;
  }
  function isStale(snapshot, data) {
    const units = [...(data.registers.EV_evidence_register || []), ...(data._evDropped || [])];
    const current = Object.fromEntries(units.filter(u => u.nbs_id === snapshot.nbs && (['structural_suitability','operational_risk'].includes(u.use_role) || snapshot.evidence_state[u.evidence_id])).map(u => [u.evidence_id, stateOf(u)]));
    return JSON.stringify(canonical(current)) !== JSON.stringify(canonical(snapshot.evidence_state));
  }
  function matches(item, scope) {
    if (scope.system && scope.system !== 'all' && item.system && item.system !== scope.system) return false;
    if (scope.lane && scope.lane !== 'all' && item.lane && item.lane !== scope.lane) return false;
    if (scope.variable && item.study && item.variable !== scope.variable) return false;
    return !scope.search || (item.text || '').toLowerCase().includes(scope.search.toLowerCase());
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {stateOf, isStale, matches};
  if (!root.document) return;
  let payload, loading, family = 'all', current = 'global', attached = false, activeNbs, live;
  const el = id => document.getElementById(id);
  function choose(name, hash = true) {
    if (!panels.includes(name)) name = 'global';
    current = name;
    for (const p of panels) {
      el('t4-panel-' + p).hidden = p !== name;
      const button = document.querySelector('[data-t4-tab="' + p + '"]');
      button.setAttribute('aria-selected', String(p === name));
      button.tabIndex = p === name ? 0 : -1;
    }
    if (hash) history.replaceState(null, '', '#t4/' + name);
    filter();
  }
  function filter() {
    const panel = el('t4-panel-' + current);
    const scope = {system: family, search: el('t4-find').value.trim(), lane: panel.querySelector('[data-t4-evidence-lane]')?.value, variable: panel.querySelector('[data-t4-study-variable]')?.value};
    let visible = 0, total = 0;
    for (const row of panel.querySelectorAll('[data-t4-row], [data-t4-study]')) {
      const item = {...row.dataset, study: row.hasAttribute('data-t4-study'), text: row.textContent};
      row.hidden = !matches(item, scope);
      if (!item.importance) { total++; if (!row.hidden) visible++; }
    }
    el('t4-visible').textContent = current === 'rules' ? '' : visible + ' of ' + total + (current === 'studies' ? ' study cards' : ' rows');
  }
  function attach() {
    if (attached) return;
    attached = true;
    const host = el('t4-analysis');
    host.addEventListener('click', event => {
      const tab = event.target.closest('[data-t4-tab]');
      if (tab) return choose(tab.dataset.t4Tab);
      const jump = event.target.closest('[data-t4-jump]');
      if (jump) {
        const select = host.querySelector('[data-t4-study-variable]');
        if ([...select.options].some(o => o.value === jump.dataset.variable)) select.value = jump.dataset.variable;
        choose(jump.dataset.t4Jump);
        host.scrollIntoView({block:'start'});
      }
      const sort = event.target.closest('[data-t4-sort]');
      if (sort) {
        const table = sort.closest('table'), body = table.tBodies[0], col = Number(sort.dataset.t4Sort), asc = sort.dataset.direction !== 'asc';
        table.querySelectorAll('[data-t4-sort]').forEach(b => {delete b.dataset.direction; b.parentElement.removeAttribute('aria-sort');});
        sort.dataset.direction = asc ? 'asc' : 'desc'; sort.parentElement.setAttribute('aria-sort', asc ? 'ascending' : 'descending');
        [...body.rows].sort((a,b) => a.cells[col].textContent.localeCompare(b.cells[col].textContent, undefined, {numeric:true}) * (asc ? 1 : -1)).forEach(r => body.appendChild(r));
      }
    });
    host.addEventListener('keydown', event => {
      const button = event.target.closest('[data-t4-tab]');
      if (!button || !['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
      event.preventDefault();
      const i = panels.indexOf(button.dataset.t4Tab);
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? 3 : (i + (event.key === 'ArrowRight' ? 1 : 3)) % 4;
      choose(panels[next]); host.querySelector('[data-t4-tab="' + panels[next] + '"]').focus();
    });
    host.addEventListener('input', filter); host.addEventListener('change', filter);
  }
  function display() {
    if (!payload || activeNbs !== payload.nbs) return;
    el('t4-analysis').hidden = false; el('t4-legacy').hidden = true;
    el('t4-verbatim-section').hidden = true; el('interrogator-quote-control').hidden = true;
    if (!el('t4-panel-global').children.length) {
      for (const p of panels) el('t4-panel-' + p).innerHTML = payload.panels[p];
    }
    el('t4-snapshot').textContent = 'Work in progress · compiler ' + payload.compiler_version + ' · snapshot ' + payload.snapshot.slice(0,12) + ' · ' + payload.summary.configured_rows + ' configured mappings';
    el('t4-stale').hidden = !isStale(payload, live);
    attach();
    const match = location.hash.match(/^#t4\/(evidence|studies|global|rules)$/);
    choose(match ? match[1] : current, false);
  }
  root.T4Analysis = {
    update(nbs, system, data) {
      activeNbs = nbs; family = system; live = data;
      el('t4-analysis').hidden = true; el('t4-legacy').hidden = false;
      el('t4-verbatim-section').hidden = false; el('interrogator-quote-control').hidden = false;
      if (nbs !== 'agroforestry') return;
      if (payload) return display();
      if (!loading) loading = fetch('t4_analysis.json', {cache:'no-cache'}).then(r => {if (!r.ok) throw Error('T4 analysis snapshot unavailable'); return r.json();}).then(data => {payload = data; display();}).catch(() => {el('t4-analysis-load').textContent = 'T4 analysis snapshot unavailable. Showing existing recipe table.'; loading = null;});
    },
    openFromHash() {
      if (!location.hash.startsWith('#t4/')) return;
      const nbs = el('select-nbs'); nbs.value = 'agroforestry'; nbs.dispatchEvent(new Event('change'));
      el('btn-interrogator').click();
    }
  };
  root.addEventListener('hashchange', () => root.T4Analysis.openFromHash());
})(typeof window === 'undefined' ? globalThis : window);
