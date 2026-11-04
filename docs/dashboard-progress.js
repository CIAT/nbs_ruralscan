/* Progress, bibliography and methods are read-only projections of generated data. */
(function () {
  'use strict';
  let data, model, evidence = new Map(), bibliography = [], drawerReturn = null, drawerTab = '';
  const state = { nbs: '', family: '', bibNbs: '', bibType: '', bibSet: '', bibTable: '', query: '', page: 0, methodNbs: '', methodTable: '', familyFilter: '', reviewFilter: '', ledgerTable: '', ledgerChannel: '', ledgerPage: 0 };
  const $ = id => document.getElementById(id);
  const esc = v => String(v == null ? '' : v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = v => v == null ? 'Not recorded' : Number(v).toLocaleString('en-GB');
  const label = v => v === 'cross' ? 'Cross-practice resources' : String(v || '').replace(/_/g, ' ').replace(/^./, c => c.toUpperCase());
  const names = { literature: 'Literature', grey: 'Grey literature', tools: 'Tools', unknown: 'Type not recorded', stock: 'Stocktake', updated_lit: 'Literature search', tool: 'Tool search' };
  const list = v => Array.isArray(v) ? v : String(v || '').split(/[|;]/).map(s => s.trim()).filter(Boolean);
  const safeUrl = v => { try { const u = new URL(v); return ['https:', 'http:'].includes(u.protocol) ? u.href : ''; } catch (_) { return ''; } };
  const link = (url, text) => safeUrl(url) ? `<a href="${esc(safeUrl(url))}" target="_blank" rel="noopener noreferrer">${esc(text)}</a>` : esc(text);
  const button = (action, text, value = '', cls = '') => `<button type="button" class="dp-button ${cls}" data-action="${action}" data-value="${esc(value)}">${esc(text)}</button>`;
  function go(tab) { const b = document.querySelector(`.tab-btn[data-tab="${tab}"]`); if (b) b.click(); }
  function options(values, selected, empty) { return `<option value="">${esc(empty)}</option>` + values.map(([v, n]) => `<option value="${esc(v)}"${selected === v ? ' selected' : ''}>${esc(n)}</option>`).join(''); }
  const practiceName = p => p.nbs_id === 'cross' ? 'Cross-practice resources' : p.name;
  function practices() { return model.practices.map(p => [p.nbs_id, practiceName(p)]); }
  function mix(m) {
    const kinds = ['literature', 'grey', 'tools', 'unknown'], total = m.known_sources || 0;
    const title = kinds.map(k => `${names[k]}: ${fmt(m.source_mix[k] || 0)}`).join(' · ');
    return `<div class="dp-mix" aria-label="${esc(title)}" title="${esc(title)}"><div class="dp-mix-bar">${kinds.map(k => `<span class="dp-${k}" style="width:${total ? 100 * (m.source_mix[k] || 0) / total : 0}%"></span>`).join('')}</div><span>${kinds.map(k => `<span class="dp-ink-${k}">${fmt(m.source_mix[k] || 0)}</span>`).join(' | ')}</span></div>`;
  }
  function legend() { return '<span class="dp-legend"><span class="dp-ink-literature">Literature</span> | <span class="dp-ink-grey">Grey</span> | <span class="dp-ink-tools">Tools</span> | <span class="dp-ink-unknown">Type not recorded</span></span>'; }
  const percent = (part, total) => total ? `${Number((100 * part / total).toFixed(1))}%` : '—';
  function step(n, title) { return `<li><strong>${fmt(n)}</strong><span>${title}</span></li>`; }
  function flow(m) {
    return `<section class="dp-workflow dp-totals" aria-label="Project evidence totals"><h3>Find sources → extract evidence → review claims → build relationships</h3><ol class="dp-flow">${step(m.known_sources, 'Known source records')}${step(m.extracted_sources, 'Sources with excerpts')}${step(m.active_excerpts, 'Retained excerpts')}${step(m.t4_structural_relationships, 'T4 suitability relationships')}</ol></section>`;
  }
  function tableHead(discovery = false) {
    return `<thead><tr><th scope="col">${discovery ? 'Practice' : 'Suitability family'}</th><th scope="col" title="Source Register and acquisition queue, with explicit duplicate aliases merged">Known sources</th>${discovery ? '<th scope="col" title="Result appearances returned; the same paper can appear more than once">Results found</th><th scope="col" title="Result appearances assessed for relevance, including those later rejected">Results screened</th><th scope="col" title="Screened result appearances that met inclusion criteria">Passed screening</th>' : ''}<th scope="col">Sources with excerpts</th><th scope="col" title="Sources with at least one approved excerpt; not whole-paper reviews">Sources with approved excerpts</th><th scope="col">Retained excerpts</th><th scope="col" title="Human-approved retained excerpts; percentage of retained excerpts">Approved excerpts</th><th scope="col" title="Compiled structural suitability relationships; soft operational records excluded">T4 relationships</th></tr></thead>`;
  }
  function cells(m, discovery = false) {
    const s = m.search_metrics;
    return `<td><b>${fmt(m.known_sources)}</b>${mix(m)}</td>${discovery ? ['retrieved','screened','included'].map(k=>`<td class="dp-numbers">${s.complete_counts ? fmt(s['paired_'+k]) : '—'}</td>`).join('') : ''}<td>${fmt(m.extracted_sources)}</td><td>${fmt(m.reviewed_sources)}</td><td>${fmt(m.active_excerpts)}</td><td title="${fmt(m.approved_excerpts)} of ${fmt(m.active_excerpts)} retained excerpts approved">${fmt(m.approved_excerpts)} <span class="dp-percent">(${percent(m.approved_excerpts,m.active_excerpts)})</span></td><td>${fmt(m.t4_structural_relationships)}</td>`;
  }
  function visibleFamilies(p) { return p.families.filter(f => ((data.family_display_status || {})[f.family_id] || {}).status !== 'out_of_scope'); }
  function selectedFamilies(p) { return visibleFamilies(p).filter(f => (!state.familyFilter || f.family_id===state.familyFilter) && (!state.reviewFilter || (state.reviewFilter==='pending' ? f.metrics.active_excerpts>f.metrics.approved_excerpts : f.metrics.active_excerpts===0))); }
  function familyRow(f) {
    const scope = (data.family_display_status || {})[f.family_id];
    return `<tr data-feedback-key="family:${esc(f.family_id)}" data-feedback-label="${esc(f.name)}"><th scope="row"><details class="dp-family"><summary>${esc(f.name)}</summary>${scope ? `<p>${esc(scope.label)}. ${esc(scope.reason)}</p>` : ''}<ul>${f.subpractices.map(s => `<li>${esc(s.name || label(s.subpractice_id))}</li>`).join('')}</ul><p class="dp-note">${f.subpractices.length ? 'Counts belong to this family; separate subpractice counts are not recorded.' : 'Evidence grouping; no subpractice breakdown recorded.'}</p></details>${scope ? `<small class="dp-scope-label">${esc(scope.label)}</small>` : ''}</th>${cells(f.metrics)}</tr>`;
  }
  function familyTable(p) { return `<div class="dp-scroll"><table class="dp-table dp-summary-table dp-family-table"><caption>${esc(practiceName(p))} · family progress</caption>${tableHead()}<tbody>${selectedFamilies(p).map(familyRow).join('') || '<tr><td colspan="7">No families match these filters.</td></tr>'}</tbody></table></div>`; }
  function overviewTable() {
    return `<div class="dp-section-head"><h3>Progress by practice</h3>${legend()}</div><p class="dp-note">Discovery columns use only records reporting all three stages: found, screened (assessed), and passed (met inclusion criteria). Results can repeat papers; known sources are catalogue records. Partial discovery records remain in Methods.</p><div class="dp-scroll"><table class="dp-table dp-summary-table"><caption class="dp-sr-only">Project effort by practice</caption>${tableHead(true)}<tbody>${model.practices.map(p => `<tr class="dp-practice-row" data-feedback-key="practice:${esc(p.nbs_id)}" data-feedback-label="${esc(practiceName(p))}"><th scope="row">${button('practice',practiceName(p),p.nbs_id,'dp-expand')}</th>${cells(p.metrics,true)}</tr>`).join('')}</tbody><tfoot><tr><th scope="row">Grand total</th>${cells(model.totals,true)}</tr></tfoot></table></div><p class="dp-note">Sources and excerpts can support several practices. Grand totals count each record once; do not add practice rows. “—” means no usable count recorded.</p>`;
  }
  function countNotes() {
    const registeredIds=new Set((data.registers.SRC_source_register || []).map(r=>r.source_id));
    const registered=model.sources.filter(r=>[r.source_id,...(r.aliases || [])].some(id=>registeredIds.has(id))).length;
    return `<details class="dp-definitions"><summary>Where do the totals come from?</summary><dl><dt>Known source records</dt><dd>${fmt(model.totals.known_sources)} = ${fmt(registered)} registered sources + ${fmt(model.sources.length-registered)} queue-only source records, after merging explicit duplicate links. Stocktake entries without a source ID are not included. ${button('known','Inspect counted sources')}</dd><dt>Results versus sources</dt><dd>One paper can appear in several discovery results. Results found, screened and passed are reported observations, not unique papers. Screened includes rejected results; passed screening means selected as relevant. Selected results are not linked individually to catalogue records, so these columns cannot form one source-level funnel.</dd><dt>Missing counts</dt><dd>All three discovery columns use the same complete, ordered records. Incomplete and conflicting records are excluded from this summary, not treated as zero. Methods retains all reported counts and original protocols. The summary is therefore a subset of recorded discovery effort.</dd><dt>Source types</dt><dd>Literature, grey literature and tools use recorded metadata. “Type not recorded” covers missing or conflicting classifications. Stocktake is an origin, not a publication type.</dd><dt>Extraction and approval</dt><dd>Retained excerpts are extracted evidence still in use. Approved excerpts have human reviewer approval; the percentage uses retained excerpts as its denominator. A source with an approved excerpt is not necessarily fully reviewed.</dd><dt>Scope and history</dt><dd>Totals describe recorded research effort, including historical work. Out-of-scope families are hidden from practice monitoring; their evidence remains in the register. Dropped excerpts do not count as retained.</dd><dt>T4 relationships</dt><dd>Compiled structural suitability relationships, including hard masks. Soft operational records are tracked separately. Compilation does not mean every supporting excerpt has human approval.</dd></dl></details>`;
  }
  function ledgerRows(p) {
    const hidden = new Set(p.families.filter(f=>!visibleFamilies(p).includes(f)).map(f=>f.family_id));
    return (data.progress_ledger || []).filter(r => r.nbs_id===p.nbs_id && !hidden.has(r.family) && (!state.familyFilter || (state.familyFilter==='__unassigned' ? !r.family : r.family===state.familyFilter)) && (!state.ledgerTable || r.table===state.ledgerTable) && (!state.ledgerChannel || r.category===state.ledgerChannel));
  }
  function ledger(p) {
    const rows=ledgerRows(p), size=20;
    state.ledgerPage=Math.max(0,Math.min(state.ledgerPage,Math.ceil(rows.length/size)-1));
    const stage = v => ({done:'Complete',in_progress:'In progress',not_started:'Not started',blocked:'Blocked',deferred:'Deferred'}[v] || (v ? label(v) : 'Not recorded'));
    return `<details class="dp-stage-summary" id="dp-ledger"><summary>Pipeline activity log</summary><p class="dp-note">Search and screening record completed process steps. Evidence checks cover source and extraction verification; human approval is shown in the family table above. Blank ledger stages mean not recorded, not zero evidence.</p><div class="dp-filters"><label>Analytical table<select id="dp-ledger-table">${options(['T4','T3','T6'].map(t=>[t,t]),state.ledgerTable,'All tables')}</select></label><label>Discovery channel<select id="dp-ledger-channel">${options(['stock','updated_lit','grey','tool'].map(k=>[k,names[k]]),state.ledgerChannel,'All channels')}</select></label></div><p class="dp-results" aria-live="polite">${fmt(rows.length)} records · ${rows.length ? state.ledgerPage*size+1 : 0}–${Math.min(rows.length,(state.ledgerPage+1)*size)} shown</p><div class="dp-scroll"><table class="dp-table dp-monitor-table"><thead><tr>${['Family / scope','Table','Channel','Search run','Screening run','Evidence checks','Updated'].map(t=>`<th scope="col">${t}</th>`).join('')}</tr></thead><tbody>${rows.slice(state.ledgerPage*size,(state.ledgerPage+1)*size).map(r=>`<tr><td title="${esc(r.note)}">${esc(r.family ? label(r.family.split('__').pop()) : 'Practice-wide')}</td><td>${esc(r.table)}</td><td>${esc(names[r.category] || label(r.category))}</td>${['searched','screened','verified'].map(k=>`<td><span class="dp-stage ${r[k]==='done'?'dp-stage-done':''}">${esc(stage(r[k]))}</span></td>`).join('')}<td>${esc(r.updated || '—')}</td></tr>`).join('') || '<tr><td colspan="7">No activity records match these filters.</td></tr>'}</tbody></table></div><div class="dp-pagination">${button('ledger-page','Previous',-1)}<span>Page ${state.ledgerPage+1} / ${Math.max(1,Math.ceil(rows.length/size))}</span>${button('ledger-page','Next',1)}</div></details>`;
  }
  function practiceView(p) {
    return `<div class="dp-section-head dp-monitor-head"><h3>Family progress</h3><div class="dp-filters"><label>Family<select id="dp-progress-family">${options(visibleFamilies(p).map(f=>[f.family_id,f.name]),state.familyFilter,'All families')}</select></label><label>Show<select id="dp-progress-review">${options([['pending','Awaiting human approval'],['empty','No retained evidence']],state.reviewFilter,'All progress')}</select></label></div></div><p class="dp-note">Approval is shown as a count and percentage of retained excerpts. Expand a family name for its subpractices.</p>${legend()}${familyTable(p)}${ledger(p)}`;
  }
  function bindProgressFilters() {
    [['dp-progress-family','familyFilter'],['dp-progress-review','reviewFilter'],['dp-ledger-table','ledgerTable'],['dp-ledger-channel','ledgerChannel']].forEach(([id,key])=>{
      const node=$(id);if(!node)return;
      node.onchange=e=>{const open=$('dp-ledger') && $('dp-ledger').open;state[key]=e.target.value;state.ledgerPage=0;renderProgress();if(open && $('dp-ledger'))$('dp-ledger').open=true;$(id).focus();};
    });
  }
  function renderProgress() {
    const p=model.practices.find(p=>p.nbs_id===state.nbs);
    $('progress-app').innerHTML=`<div class="dp-shell"><nav class="dp-subtabs" aria-label="Progress views">${button('practice','Overview','',!p?'is-active':'')}${model.practices.map(p=>button('practice',practiceName(p),p.nbs_id,state.nbs===p.nbs_id?'is-active':'')).join('')}</nav><header class="dp-intro"><div class="dp-eyebrow">Rural NbS Scan · ${p?'Practice progress':'Project progress'}</div><h2>${p?esc(practiceName(p)):'Evidence behind the Rural NbS Scan'}</h2><p>${p?'Track evidence extraction and human approval by family.':'Research effort behind the landscape scoping methodology, from discovery to traceable evidence.'}</p><div class="dp-actions">${button('bibliography','Explore bibliography',state.nbs)}${button('methods','Read methods',state.nbs)}</div></header>${p?practiceView(p):flow(model.totals)+overviewTable()}${countNotes()}</div>`;
    bindProgressFilters();
  }
  function legacyPractices(raw) {
    const normalize = value => String(value || '').trim().toLowerCase().replace(/_/g,' ').replace(/\s+/g,' ');
    const wanted = normalize(raw);
    const known = model.practices.find(p => wanted && [p.nbs_id,p.name].some(value=>normalize(value)===wanted));
    if(known)return [known.nbs_id];
    const explicit = {'water harvesting and conservation':'water_harvesting_conservation','riparian buffers':'riparian_buffer'};
    const mapped = explicit[wanted];
    return mapped && model.practices.some(p=>p.nbs_id===mapped) ? [mapped] : [];
  }
  function makeBibliography() {
    bibliography = model.sources.map(s => ({...s, legacy:false}));
    const keys = new Set(model.sources.flatMap(s => [s.source_id,...s.aliases]));
    Object.entries(data.stocktake || {}).forEach(([kind, rows]) => {
      if (!Array.isArray(rows)) return;
      rows.forEach((r,i) => {
        if (r.source_id && keys.has(r.source_id)) return;
        bibliography.push({key:`legacy:${kind}:${i}`,source_id:'',citation:r.oa_title || r.title || r.name || 'Untitled stocktake resource', type:kind==='peer_reviewed'?'literature':kind.includes('tool')?'tools':'grey',url:r.url || r.URL || '',doi:r.doi_extracted || '',origins:['stock'],nbs_ids:legacyPractices(r.NbS_Practice),family_ids:[],rawPractice:r.NbS_Practice || '',raw:r,legacy:true,evidence_ids:[],approved_evidence_ids:[],dropped_evidence_ids:[],contributions:{}});
      });
    });
    (data.registers.TOOL_tool_registry || []).forEach(r => {
      if (r.source_id && keys.has(r.source_id)) return;
      bibliography.push({key:`tool:${r.tool_id}`,source_id:'',citation:r.name,type:'tools',url:r.url,origins:['tool'],nbs_ids:list(r.nbs_id || r.nbs_ids),family_ids:[],raw:r,legacy:true,evidence_ids:[],approved_evidence_ids:[],dropped_evidence_ids:[],contributions:{}});
    });
  }
  function filteredBibliography() {
    const q = state.query.toLowerCase();
    return bibliography.filter(s => (!state.bibNbs || s.nbs_ids.includes(state.bibNbs)) && (!state.bibType || s.type===state.bibType) && (!state.bibSet || (state.bibSet==='legacy' ? s.legacy : !s.legacy)) && (!state.bibTable || (s.contributions[state.bibTable] || []).length) && (!q || [s.citation,s.source_id,s.doi,s.rawPractice,...s.nbs_ids,...s.origins].join(' ').toLowerCase().includes(q)));
  }
  function extractionSummary(source) {
    const counts=source.extraction_counts;
    if(!counts)return 'Extract categories not recorded';
    return `Extracted: T4 ${fmt(counts.T4)} · Effects ${fmt(counts.effects)} · M2b ${fmt(counts.M2b)}`+(counts.other ? ` · Other ${fmt(counts.other)}` : '');
  }
  function renderBibliography() {
    if (!model) return;
    const rows = filteredBibliography(), size=40;
    state.page=Math.max(0,Math.min(state.page,Math.ceil(rows.length/size)-1));
    $('bibliography-app').innerHTML = `<div class="dp-shell"><header class="dp-intro"><div class="dp-eyebrow">One catalogue · sources & tools</div><h2>Bibliography</h2><p>Publication details, recorded origins and evidence contributions. Open a source to read its excerpts alongside the catalogue.</p></header><div class="dp-filters"><label>Search<input id="dp-bib-query" type="search" value="${esc(state.query)}" placeholder="Title, author, source ID…"></label><label>Practice<select id="dp-bib-nbs">${options(practices(),state.bibNbs,'All practices')}</select></label><label>Source type<select id="dp-bib-type">${options(Object.entries(names).filter(([k])=>['literature','grey','tools','unknown'].includes(k)),state.bibType,'All types')}</select></label><label>Records<select id="dp-bib-set">${options([['known','Known source records'],['legacy','Unreconciled legacy resources']],state.bibSet,'All records')}</select></label><label>Contribution<select id="dp-bib-table">${options(['T4','T3','M2b','T6'].map(t=>[t,t]),state.bibTable,'Any contribution')}</select></label></div><p class="dp-note">${fmt(model.sources.length)} known source records + ${fmt(bibliography.length-model.sources.length)} unreconciled legacy resources. Legacy entries may overlap and are excluded from progress totals. Screening decisions, exact discovery-search links and citation parents are not recorded per source. Extraction categories are separate: T4 suitability, effects, and M2b risk. Effects are not assigned to T3 versus T6 until synthesis. Compiled contributions count retained excerpts cited by T4/T3/T6; M2b counts risk-role excerpts. Table contributions overlap; approved excerpts are included in retained counts.</p><div class="dp-results" aria-live="polite">${fmt(rows.length)} matching records · ${rows.length ? state.page*size+1 : 0}–${Math.min(rows.length,(state.page+1)*size)} shown</div><div class="dp-scroll"><table class="dp-table dp-bibliography"><thead><tr><th>Publication / resource</th><th>Type / origin</th><th>Practices</th><th>Screening / extraction</th><th>Compiled contributions<br><small>T4 | T3 | M2b* | T6</small></th></tr></thead><tbody>${rows.slice(state.page*size,(state.page+1)*size).map(s => `<tr data-feedback-key="source:${esc(s.key)}" data-feedback-label="${esc(s.citation)}"><th scope="row">${button('source',s.citation,s.key,'dp-source-title')}<small>${esc(s.source_id || 'Legacy resource · identity not reconciled')}</small>${s.url ? link(s.url,'Open source ↗') : ''}${s.doi ? `<small>DOI: ${esc(s.doi)}</small>` : ''}</th><td>${esc(names[s.type])}<small>${s.origins.map(o=>esc(names[o] || label(o))).join(', ') || 'Origin not recorded'}</small></td><td>${esc(s.nbs_ids.map(label).join(', ') || s.rawPractice || 'Not assigned')}</td><td>Screening: not recorded<small>${s.legacy ? 'Extraction: not linked' : `${fmt(s.evidence_ids.length)} retained · ${fmt(s.approved_evidence_ids.length)} approved excerpts`}</small>${s.legacy ? '' : `<small>${esc(extractionSummary(s))}</small>`}</td><td class="dp-numbers">${['T4','T3','M2b','T6'].map(t=>s.legacy?'—':fmt((s.contributions[t]||[]).length)).join(' | ')}</td></tr>`).join('') || '<tr><td colspan="5">No matching records. Clear a filter to broaden the list.</td></tr>'}</tbody></table></div><div class="dp-pagination">${button('page','Previous',-1)}<span>Page ${state.page+1} / ${Math.max(1,Math.ceil(rows.length/size))}</span>${button('page','Next',1)}</div></div>`;
    const query=$('dp-bib-query');
    query.addEventListener('input',()=>{state.query=query.value;state.page=0;const pos=query.selectionStart;renderBibliography();const next=$('dp-bib-query');next.focus();next.setSelectionRange(pos,pos);});
    [['nbs','bibNbs'],['type','bibType'],['set','bibSet'],['table','bibTable']].forEach(([id,key])=>$('dp-bib-'+id).addEventListener('change',e=>{state[key]=e.target.value;state.page=0;renderBibliography();$('dp-bib-'+id).focus();}));
  }
  function closeDrawer() { const d=$('dp-source-drawer');if(d)d.remove();if(location.hash.startsWith('#source='))history.replaceState(null,'',location.pathname+location.search);if(drawerReturn && drawerReturn.isConnected)drawerReturn.focus(); }
  function openSource(id) {
    if(!model)return;
    const source=bibliography.find(s=>s.key===id || s.source_id===id || (s.aliases||[]).includes(id));
    if(!source)return;
    if(!$('dp-source-drawer'))drawerReturn=document.activeElement;
    const activeTab=document.querySelector('.tab-btn.active');
    drawerTab=activeTab ? activeTab.dataset.tab : '';
    const old=$('dp-source-drawer');if(old)old.remove();
    const d=document.createElement('aside');d.id='dp-source-drawer';d.className='dp-drawer';d.dataset.feedbackKey='source:'+source.key;d.dataset.feedbackLabel=source.citation;d.setAttribute('role','dialog');d.setAttribute('aria-label','Source details and evidence');d.setAttribute('aria-modal','false');d.tabIndex=-1;
    const ids=[...source.evidence_ids,...source.dropped_evidence_ids];
    d.innerHTML=`<div class="dp-drawer-head"><h2>Source & evidence</h2>${button('close','Close ×')}</div><h3>${esc(source.citation)}</h3><p>${link(source.url,'Open source ↗')}</p><dl><dt>Source ID</dt><dd>${esc(source.source_id || 'Legacy resource; identity not reconciled')}</dd><dt>Publication DOI</dt><dd>${esc(source.doi || 'Not recorded')}</dd><dt>Origin</dt><dd>${esc(source.origins.map(o=>names[o]||label(o)).join(', ') || 'Not recorded')}</dd><dt>Discovered by search / citation parent</dt><dd>Not recorded at source level</dd><dt>Screening decision</dt><dd>Not recorded at source level</dd><dt>Practices / families</dt><dd>${esc(source.nbs_ids.map(label).join(', ') || source.rawPractice || 'Not assigned')}<br>${esc(source.family_ids.map(f=>label(f.split('__').pop())).join(', '))}</dd><dt>Recorded extraction / queue status</dt><dd>${esc([...(source.extraction_status||[]),...(source.queue_statuses||[])].map(label).join(', ') || 'Not recorded')}</dd></dl>${source.raw ? `<details><summary>Legacy resource / tool details</summary><dl>${Object.entries(source.raw).filter(([,v])=>v).map(([k,v])=>`<dt>${esc(label(k))}</dt><dd>${esc(v)}</dd>`).join('')}</dl></details>`:''}${(source.tools||[]).map(t=>`<details><summary>${esc(t.name)}</summary><p>${esc(t.workflow_summary)}</p><p>${esc(t.spatial_method)} · ${esc(t.validation)}</p></details>`).join('')}<h3>Evidence excerpts</h3><p>${esc(extractionSummary(source))}</p><p class="dp-note">Extraction categories are mutually exclusive. Effects can later contribute to T3, T6, or both through synthesis.</p><p class="dp-note">${fmt(source.evidence_ids.length)} retained · ${fmt(source.approved_evidence_ids.length)} approved · ${fmt(source.dropped_evidence_ids.length)} quarantined. Approved excerpts are a subset of retained excerpts. Approval applies to excerpts, not the whole paper.</p><label class="dp-toggle"><input id="dp-show-dropped" type="checkbox"> Include quarantined excerpts</label><div id="dp-drawer-evidence"></div>`;
    document.body.appendChild(d);
    let limit=25;
    const render=()=>{const show=$('dp-show-dropped').checked;const selected=ids.map(id=>evidence.get(id)).filter(r=>r&&(show||r.review_state!=='dropped'));
      $('dp-drawer-evidence').innerHTML=selected.slice(0,limit).map(r=>`<article class="dp-excerpt" data-vfeid="${esc(r.evidence_id)}" data-feedback-key="evidence:${esc(r.evidence_id)}"><strong>${esc(label(r.variable || r.effect_indicator || r.use_role))}</strong><small>${esc(r.evidence_id)} · ${esc(r.review_state==='dropped'?'Quarantined':String(r.reviewer_ok)==='true'?'Approved':'Awaiting review')}</small><blockquote>${esc(r.quote || 'No quote recorded')}</blockquote><p>${esc(label(r.nbs_id))} · ${esc(label((r.suitability_family_id||'').split('__').pop()))}<br>${esc(label(r.use_role))} · ${esc(r.locator || (r.page ? 'Page '+r.page : 'Locator not recorded'))}</p></article>`).join('') || '<p>No linked excerpts in this view.</p>';
      if(selected.length>limit){const b=document.createElement('button');b.type='button';b.className='dp-button';b.textContent=`Show more (${selected.length-limit} remaining)`;b.onclick=()=>{limit+=25;render();};$('dp-drawer-evidence').appendChild(b);}
    };
    $('dp-show-dropped').onchange=render;render();d.focus();history.replaceState(null,'','#source='+encodeURIComponent(source.key));
  }
  function originalProtocols(records) {
    const fieldNames = {search_id:'Search record', n_retrieved:'Search hits', n_screened:'Hits screened', n_included:'Hits selected', search_date:'Search date', nbs_id:'Practice', suitability_family_id:'Suitability family', run_id:'Search run', ruleset_version:'Method version'};
    return (records || []).map((r,i)=>`<table class="dp-protocol-record"><caption>Original search record ${i+1}</caption><tbody>${Object.entries(r).map(([k,v])=>`<tr><th scope="row">${esc(fieldNames[k] || label(k))}</th><td>${esc(Array.isArray(v)?v.join('; '):v == null || v === '' ? 'Not recorded' : v)}</td></tr>`).join('')}</tbody></table>`).join('') || '<p>No original record available.</p>';
  }
  function renderMethods() {
    if(!model)return;
    const events=model.searches.filter(e=>(!state.methodNbs||e.nbs_id===state.methodNbs)&&(!state.methodTable||e.tables.includes(state.methodTable)));
    $('methods-app').innerHTML=`<div class="dp-shell"><header class="dp-intro"><div class="dp-eyebrow">Methods · reproducible research</div><h2>Search protocols & counting method</h2><p>Each documented search records its scope, search terms and screening rules. Shared runs across tables appear once; original records remain available inside each protocol.</p></header><div class="dp-filters"><label>Practice<select id="dp-method-nbs">${options(practices(),state.methodNbs,'All practices')}</select></label><label>Table<select id="dp-method-table">${options(['T4','T3','T6'].map(t=>[t,t]),state.methodTable,'All tables')}</select></label></div><p class="dp-note">${fmt(events.length)} search events. Prose, approximate or conflicting counts are retained as notes, never converted into exact totals.</p>${events.map(e=>`<details class="dp-protocol"><summary><strong>${esc(label(e.nbs_id))}</strong> · ${esc(names[e.category]||label(e.category))} · ${esc(e.tables.join(' / '))}<span>${esc(e.search_date || 'Date not recorded')} · ${esc(e.suitability_family_id ? label(e.suitability_family_id.split('__').pop()) : 'Practice-wide')}</span></summary><dl>${['run_id','ruleset_version','search_terms','screening_steps','inclusion_criteria','limits'].map(k=>`<dt>${esc(label(k))}</dt><dd>${esc(e[k] || 'Not recorded')}</dd>`).join('')}<dt>Search records</dt><dd>${esc(e.search_ids.join(', '))}</dd><dt>Numeric counts used</dt><dd>${['retrieved','screened','included'].map(k=>`${label(k)}: ${fmt(e.counts[k])}`).join(' · ')}${e.counts_conflict ? ' · Conflicting counts excluded' : ''}${e.screening_variants > 1 ? ' · Table-specific screening protocols differ; screening totals not combined' : ''}${e.invalid_order ? ' · Invalid sequence excluded' : ''}</dd></dl><details><summary>Original protocol records</summary>${originalProtocols(e.raw_records)}</details></details>`).join('') || '<p>No search protocol recorded for this selection.</p>'}<details class="dp-definitions"><summary>Count definitions and limits</summary><dl>${Object.entries(model.definitions).map(([k,v])=>`<dt>${esc(label(k))}</dt><dd>${esc(v)}</dd>`).join('')}</dl></details></div>`;
    $('dp-method-nbs').onchange=e=>{state.methodNbs=e.target.value;renderMethods();$('dp-method-nbs').focus();};$('dp-method-table').onchange=e=>{state.methodTable=e.target.value;renderMethods();$('dp-method-table').focus();};
  }
  function renderBuild() {
    const b=data.build || {};
    $('dashboard-build').innerHTML=`<span>Dashboard <b>v${esc(b.release || 'unversioned')}</b> · UI ${esc(b.ui_id || '—')} · Data ${esc(b.data_id || '—')}</span><details><summary>Build ${esc((b.built_at || data.timestamp || '').slice(0,16).replace('T',' '))} · history</summary><div><p>Counts v${esc(b.count_definition_version || '—')} · Source revision ${esc((b.source_commit || '').slice(0,12))}</p>${(data.dashboard_releases||[]).map(r=>`<p><b>v${esc(r.version)}</b> · ${esc(r.changes)}</p>`).join('')}<ul>${(b.history||[]).slice().reverse().map(h=>`<li>${esc(h.built_at)} · v${esc(h.release)} · UI ${esc(h.ui_id)} · Data ${esc(h.data_id)}</li>`).join('')}</ul><small>Latest 50 builds retained here; older builds remain in project history.</small></div></details>`;
  }
  function dispatch(e) {
    const b=e.target.closest('[data-action]');if(!b||!b.closest('.dp-shell,.dp-drawer'))return;
    const v=b.dataset.value;
    switch(b.dataset.action){
      case 'practice':state.nbs=v;state.family='';state.familyFilter='';state.reviewFilter='';state.ledgerTable='';state.ledgerChannel='';state.ledgerPage=0;renderProgress();document.querySelector('.dp-subtabs .is-active').focus({preventScroll:true});const intro=document.querySelector('#progress-app .dp-intro');if(intro)intro.scrollIntoView({block:'start'});break;
      case 'ledger-page':state.ledgerPage+=Number(v);renderProgress();$('dp-ledger').open=true;$('dp-ledger').scrollIntoView({block:'start'});break;
      case 'known':state.bibNbs='';state.bibSet='known';state.bibTable='';state.bibType='';state.query='';state.page=0;renderBibliography();go('tab-stocktake');break;
      case 'bibliography':state.bibNbs=v;state.bibSet='';state.bibTable='';state.bibType='';state.query='';state.page=0;renderBibliography();go('tab-stocktake');break;
      case 'methods':openMethods(v);break;
      case 'source':openSource(v);break;
      case 'close':closeDrawer();break;
      case 'page':state.page+=Number(v);renderBibliography();$('bibliography-app').scrollIntoView({block:'start'});break;
    }
  }
  // Reveal a saved feedback target without changing evidence or reviewer decisions.
  function revealTarget(key) {
    if(!model || typeof key !== 'string')return false;
    if(key.startsWith('source:')) {
      const id=key.slice(7);
      const source=bibliography.find(s=>s.key===id || s.source_id===id || (s.aliases||[]).includes(id));
      if(!source)return false;
      go('tab-stocktake');openSource(source.key);return true;
    }
    const family=key.startsWith('family:') ? key.slice(7) : '';
    const practice=key.startsWith('practice:') ? key.slice(9) : '';
    const index=model.practices.findIndex(p=>family ? p.families.some(f=>f.family_id===family) : practice && p.nbs_id===practice);
    if(index<0)return false;
    const target=model.practices[index];
    if(family && !visibleFamilies(target).some(f=>f.family_id===family))return false;
    state.nbs=family?target.nbs_id:'';state.family=family;state.familyFilter=family;state.reviewFilter='';state.ledgerPage=0;renderProgress();go('tab-search');
    return true;
  }
  function openMethods(nbs) {state.methodNbs=nbs && nbs!=='all'?nbs:'';state.methodTable='';renderMethods();go('tab-methods');}
  function printOverview() {
    const oldNbs=state.nbs, active=document.querySelector('.tab-btn.active'), oldTab=active&&active.dataset.tab;
    const oldMarkup=$('progress-app').innerHTML, oldFocus=document.activeElement;
    const oldScroll={x:window.scrollX,y:window.scrollY}, oldHash=location.hash;
    const drawer=$('dp-source-drawer');if(drawer)drawer.remove();
    state.nbs='';renderProgress();go('tab-search');document.body.classList.add('dp-print');
    let restored=false;
    const restore=()=>{
      if(restored)return;restored=true;
      document.body.classList.remove('dp-print');state.nbs=oldNbs;$('progress-app').innerHTML=oldMarkup;
      bindProgressFilters();
      if(oldTab)go(oldTab);
      if(drawer)document.body.appendChild(drawer);
      history.replaceState(null,'',location.pathname+location.search+oldHash);
      if(oldFocus && oldFocus.isConnected)oldFocus.focus({preventScroll:true});
      window.scrollTo(oldScroll.x,oldScroll.y);
      window.removeEventListener('afterprint',restore);
    };
    window.addEventListener('afterprint',restore);
    try { window.print(); } catch(error) { restore(); throw error; }
  }
  function openHashSource() {
    if(!location.hash.startsWith('#source='))return;
    let id;
    try {id=decodeURIComponent(location.hash.slice(8));} catch(_) {return;}
    openSource(id);
  }
  function refresh(next) {data=next;model=data.progress_overview;if(!model)return;evidence=new Map([...(data.registers.EV_evidence_register||[]),...(data._evDropped||[])].map(r=>[r.evidence_id,r]));makeBibliography();renderProgress();renderBibliography();renderMethods();renderBuild();}
  function trackStickyOffsets() {
    if(!window.ResizeObserver)return;
    const header=document.querySelector('.app-header'), tabs=document.querySelector('.tab-nav');
    const update=()=>{document.documentElement.style.setProperty('--dp-header-height',`${header?header.getBoundingClientRect().height:0}px`);document.documentElement.style.setProperty('--dp-main-tabs-height',`${tabs?tabs.getBoundingClientRect().height:0}px`);};
    const observer=new window.ResizeObserver(update);if(header)observer.observe(header);if(tabs)observer.observe(tabs);update();
  }
  let initialized=false;
  window.DashboardProgress={
    init(next){refresh(next);if(!initialized){trackStickyOffsets();document.addEventListener('click',dispatch);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&$('dp-source-drawer'))closeDrawer();});window.addEventListener('hashchange',openHashSource);initialized=true;}openHashSource();},
    refresh,renderBibliography,openSource,openMethods,revealTarget,print:printOverview,
    scope:()=>({nbs:state.nbs || 'all',family:state.familyFilter || 'all'}),
    context:tab=>tab==='tab-stocktake'?{nbs:state.bibNbs||'all',source_type:state.bibType||'all',query:state.query}:tab==='tab-methods'?{nbs:state.methodNbs||'all',table:state.methodTable||'all'}:{nbs:state.nbs||'all',family:state.familyFilter||'all'},
    onTab(tab){if($('dp-source-drawer') && tab!==drawerTab)closeDrawer();},
  };
})();
