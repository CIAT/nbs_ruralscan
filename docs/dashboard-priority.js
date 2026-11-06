/* Review triage only. No register, decision, approval or runtime writes. */
(function () {
  'use strict';
  const esc = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const rows = () => (typeof dashboardData !== 'undefined' && dashboardData && dashboardData.review_priorities) || [];
  const evidence = () => [...(dashboardData.registers.EV_evidence_register || []), ...(dashboardData._evDropped || [])];
  const notes = id => rows().filter(r => r.evidence_id === id);
  const selected = () => window._vfPriority || 'all';
  const batchRoute = id => '#review-priority=' + encodeURIComponent(id);
  const cardRoute = id => '#review-evidence=' + encodeURIComponent(id);
  function sourceLocation(row) {
    return String(row.page || '').trim() ? 'PDF p' + esc(row.page) : 'Source location: ' + esc(row.source_locator);
  }
  function matches(ev) {
    if (window._vfPriorityEvidence && ev.evidence_id !== window._vfPriorityEvidence) return false;
    const value = selected();
    return value === 'all' || notes(ev.evidence_id).some(r => value === 'high' ? r.priority === 'high' : r.batch_id === value);
  }
  function scopeFor(units) {
    const practices = [...new Set(units.map(e => e.nbs_id))];
    const tables = [...new Set(units.map(e => _vfR2T[e.use_role]))];
    window._vfScope = {nbs: practices.length === 1 ? practices[0] : 'all', table: tables.length === 1 ? tables[0] : 'all', family: 'all', source: 'all', access: 'all', claimScope: 'all', observations: 'show', round: 'all', sourceId: '', section: ''};
    window._vfSearch = ''; window._vfMode = 'review';
  }
  function set(value) {
    window._vfPriorityEvidence = '';
    window._vfPriority = value;
    if (value !== 'all') {
      const ids = new Set(rows().filter(r => value === 'high' ? r.priority === 'high' : r.batch_id === value).map(r => r.evidence_id));
      scopeFor(evidence().filter(e => ids.has(e.evidence_id)));
      vfSimpleQueue('todo');
    } else renderVfWorklist();
    history.replaceState(null, '', route());
  }
  function route() {
    return window._vfPriorityEvidence ? cardRoute(window._vfPriorityEvidence) : selected() !== 'all' ? batchRoute(selected()) : '#review-queue';
  }
  function leaveFocus() {
    window._vfPriorityEvidence = '';
    history.replaceState(null, '', route());
  }
  function openFromHash(hash) {
    const match = /^#review-(priority|evidence)=(.*)$/.exec(hash);
    if (!match) return false;
    if (typeof dashboardData === 'undefined' || !dashboardData) return true;
    let value; try { value = decodeURIComponent(match[2]); } catch (_) { return true; }
    const unit = match[1] === 'evidence' && evidence().find(e => e.evidence_id === value);
    if (match[1] === 'priority' && value !== 'high' && !rows().some(r => r.batch_id === value) || match[1] === 'evidence' && !unit) {
      window.DashboardShell.openReviewQueue();
      vfNotice('This review link is not present in the current dashboard build.', true);
      return true;
    }
    window.DashboardShell.openReviewQueue();
    if (unit) {
      scopeFor([unit]);
      window._vfPriority = 'all'; window._vfPriorityEvidence = value;
      vfSimpleQueue('advanced');
      window._vfAxStatus = 'any';
      renderVfWorklist();
      const card = Array.from(document.querySelectorAll('#vf-cards [data-vfeid]')).find(el => el.dataset.vfeid === value);
      if (card) { if (card.tagName === 'DETAILS') card.open = true; card.scrollIntoView({block: 'start'}); }
    } else set(value);
    history.replaceState(null, '', hash);
    return true;
  }
  function controls() {
    const batches = [...new Map(rows().map(r => [r.batch_id, r.batch_label]))];
    if (!batches.length) return '';
    const options = [['all','All priorities'],['high','High priority'],...batches];
    const current = selected();
    const batchRows = rows().filter(r => r.batch_id === current);
    const focused = window._vfPriorityEvidence;
    return '<section class="vf-priority-controls" aria-label="Review priorities" style="margin:10px 0;padding:12px;border:1px solid var(--border-color);border-radius:6px">'
      + '<label>Review priority <select id="vf-priority" onchange="DashboardPriority.set(this.value)">' + options.map(([id,label]) => '<option value="'+esc(id)+'"'+(id===current?' selected':'')+'>'+esc(label)+'</option>').join('')+'</select></label>'
      + '<span style="margin-left:10px">'+batches.map(([id,label]) => '<a href="'+batchRoute(id)+'">'+esc(label)+' ('+new Set(rows().filter(r=>r.batch_id===id).map(r=>r.evidence_id)).size+')</a>').join(' · ')+'</span>'
      + '<p style="margin:8px 0;font-size:12px">Priority identifies what to inspect first. It does not change decisions, extraction approval, source credibility or runtime readiness.</p>'
      + (focused ? '<p>Showing one evidence card, including its existing decision state. <button class="pill-btn" onclick="DashboardPriority.set(\'all\')">Show scoped queue</button></p>' : '')
      + (batchRows.length ? '<p style="font-size:12px">Batch shortcuts reset scope; the current filters above still apply. Use More filters to narrow family, source or evidence scope. Queue tabs follow existing decisions.</p><details><summary>All '+batchRows.length+' batch records · open a native evidence card</summary><ul>'+batchRows.map(r=>'<li><a href="'+cardRoute(r.evidence_id)+'">'+esc(r.evidence_id)+'</a> · '+esc(r.source_id)+' · '+sourceLocation(r)+'</li>').join('')+'</ul></details>' : '')
      + '</section>';
  }
  function badge(ev) {
    const list = notes(ev.evidence_id);
    if (!list.length) return '';
    return '<span style="font-size:11px;border:1px solid var(--accent-amber);color:var(--accent-amber);padding:2px 6px;border-radius:4px">'+(list.some(r=>r.priority==='high')?'High review priority':'Review priority')+'</span>';
  }
  function card(ev) {
    return notes(ev.evidence_id).map(r=>'<section class="vf-priority-note" style="margin:10px 0;padding:12px;border-left:3px solid var(--accent-amber);font-size:12px;line-height:1.6">'
      +'<b>'+esc(r.batch_label)+'</b> · requested by '+esc(r.requested_by)+' · '+esc(r.requested_date)
      +(r.context_changed?'<p><b>Evidence changed since this request.</b> Check these original review questions against the current record.</p>':'')
      +'<p><b>Why prioritized:</b> '+esc(r.reason)+'</p><p><b>Decision needed:</b> '+esc(r.decision_needed)+'</p>'
      +'<details><summary>Request reference and links</summary><p>Source '+esc(r.source_id)+' · '+sourceLocation(r)+'</p><p>Mapping: '+esc(r.mapping_id)+'</p><a href="'+cardRoute(ev.evidence_id)+'">Link to this evidence card</a> · <a href="'+batchRoute(r.batch_id)+'">Open priority batch</a></details>'
      +'<p>Review request only. Keep confirms the extraction; changing a live mapping requires a separate reviewed change.</p></section>').join('');
  }
  window.DashboardPriority = {matches, set, route, leaveFocus, openFromHash, controls, badge, card};
})();
