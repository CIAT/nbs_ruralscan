/* Progress, bibliography and methods are read-only projections of generated data. */
(function () {
  'use strict';
  let data, model, evidence = new Map(), bibliography = [], drawerReturn = null, drawerTab = '', drawerSource = '', registered = new Map();
  const state = { nbs: '', family: '', bibNbs: '', bibType: '', bibSet: '', bibTable: '', bibFamily: '', bibOrigin: '', bibEvidence: '', query: '', page: 0, methodNbs: '', methodTable: '', familyFilter: '', reviewFilter: '', familySort: 'name', familySortDesc: false, overviewView: 'table', chartScale: 'counts', progressTable: 'T4', bibKeys: null, bibScopeLabel: '' };
  // Operational records have independent filters: navigating Progress must not reset them.
  const pipelineState = { nbs: '', family: '', table: '', channel: '', page: 0, sort: 'updated', descending: true };
  const $ = id => document.getElementById(id);
  const esc = v => String(v == null ? '' : v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fmt = v => v == null ? 'Not recorded' : Number(v).toLocaleString('en-GB');
  const label = v => v === 'cross' ? 'General reference sources' : String(v || '').replace(/_/g, ' ').replace(/^./, c => c.toUpperCase());
  const names = { literature: 'Literature', grey: 'Grey literature', tools: 'Tools', unknown: 'Type not recorded', stock: 'Stocktake', updated_lit: 'Literature search', tool: 'Tool search' };
  const list = v => Array.isArray(v) ? v : String(v || '').split(/[|;]/).map(s => s.trim()).filter(Boolean);
  const safeUrl = v => { try { const u = new URL(v); return ['https:', 'http:'].includes(u.protocol) ? u.href : ''; } catch (_) { return ''; } };
  const link = (url, text) => safeUrl(url) ? `<a href="${esc(safeUrl(url))}" target="_blank" rel="noopener noreferrer">${esc(text)}</a>` : esc(text);
  const button = (action, text, value = '', cls = '') => `<button type="button" class="dp-button ${cls}" data-action="${action}" data-value="${esc(value)}">${esc(text)}</button>`;
  function go(tab) { const b = document.querySelector(`.tab-btn[data-tab="${tab}"]`); if (b) b.click(); }
  function options(values, selected, empty) { return `<option value="">${esc(empty)}</option>` + values.map(([v, n]) => `<option value="${esc(v)}"${selected === v ? ' selected' : ''}>${esc(n)}</option>`).join(''); }
  const practiceName = p => p.nbs_id === 'cross' ? 'General reference sources' : p.name;
  const practiceRows = () => model.practices.filter(p=>p.nbs_id!=='cross');
  const progressLabels = {T2a:'T2a · Climate risk',T3:'T3 · Hazard response',T4:'T4 · Suitability',T6:'T6 · Benefits'};
  const progressModel = () => (model.table_views||{})[state.progressTable] || model;
  const progressRows = () => progressModel().project_level ? [{nbs_id:'shared',name:'Shared climate-risk configuration',metrics:progressModel().totals,families:[]}] : (progressModel().practices||[]).filter(p=>p.nbs_id!=='cross');
  const progressTitle = () => progressLabels[state.progressTable] || 'All evidence';
  const feedbackKey = key => state.progressTable&&state.progressTable!=='T4'?'progress:'+state.progressTable+':'+key:key;
  // Each table keeps its own controls; T4 remains the primary view.
  const sectionState = Object.fromEntries(['T4','T2a','T3','T6'].map(t=>[t,{view:'table',scale:'counts',open:false}]));
  const sectionId = (table,id) => table==='T4'?id:id.replace(/^dp-/, 'dp-'+table+'-');
  const sectionNumber = () => viewNumber()+'.'+({T4:1,T2a:2,T3:3,T6:4}[state.progressTable]);
  const outputTitle = () => ({T4:'T4 rules compiled',T2a:'Risk indicators configured',T3:'T3 assessments compiled',T6:'T6 assessments compiled'}[state.progressTable]);
  const outputCount = m => state.progressTable==='T4'?m.t4_structural_relationships:m.compiled_outputs;
  function outputDetails() {
    const p=(progressModel().practices||[]).find(p=>p.nbs_id===state.nbs);
    const r=((p||progressModel()).outputs||[]).find(r=>r.table_id===state.progressTable);
    if(!r||(state.nbs&&progressModel().project_level))return '';
    return `<details class="dp-output-detail" id="dp-output-${esc(r.table_id)}" data-feedback-key="${esc(feedbackKey('output:'+r.table_id+':'+(state.nbs||'all')))}"><summary>Inspect ${esc(r.table_id)} · ${fmt(r.output_count)} ${esc(r.unit)}</summary><p>${fmt(r.evidence_backed_outputs)} of ${fmt(r.output_count)} outputs cite retained extracts. ${fmt(r.contributing_excerpts)} distinct extracts used. Compilation does not certify approval.</p>${button('output-sources','Inspect supporting sources',r.table_id)}<ul>${(r.rows||[]).map(row=>`<li><strong>${esc(row.label||row.id)}</strong>${!state.nbs&&row.nbs_id?' · '+esc(label(row.nbs_id)):''}${row.context_label?'<small>'+esc(row.context_label)+'</small>':''}<small>${fmt((row.evidence_ids||[]).length)} retained extracts linked</small></li>`).join('')}</ul></details>`;
  }
  function additionalPractice(p) {
    if(progressModel().project_level)return '<p>T2a is shared across the project; practice-level allocations are not recorded.</p>'+button('shared-progress','View shared climate-risk progress');
    if(!p)return '<p>No progress records in this scope.</p>';
    const rows=visibleFamilies(p);
    return `${legend()}<div class="dp-scroll"><table class="dp-table dp-summary-table"><caption>Table ${sectionNumber()}. ${esc(practiceName(p))}: ${esc(progressTitle())} by family and evidence scope</caption>${tableHead()}<tbody>${rows.map(familyRow).join('')}</tbody><tfoot><tr><th scope="row">Whole-practice total<small>Deduplicated; family rows overlap.</small></th>${cells(p.metrics)}</tr></tfoot></table></div>`;
  }
  function tableSection(table) {
    state.progressTable=table;state.overviewView=sectionState[table].view;state.chartScale=sectionState[table].scale;
    const p=(progressModel().practices||[]).find(p=>p.nbs_id===state.nbs);
    let content=(state.nbs?(table==='T4'?practiceView(p):additionalPractice(p)):overviewTable())+outputDetails();
    content=content.replace(/data-action="/g,`data-table="${table}" data-action="`);
    if(table!=='T4')content=content.replace(/(id|aria-controls|aria-labelledby)="(dp-[^"]+)"/g,(_,attr,id)=>`${attr}="${sectionId(table,id)}"`).replace(/<h3>.*?<\/h3>/,'');
    const scope=progressModel().scope_note||'';
    return table==='T4'?`<section id="dp-section-T4">${content}</section>`:`<details class="dp-table-section" id="dp-section-${table}"${sectionState[table].open?' open':''}><summary>${sectionNumber()} ${esc(progressTitle())}</summary><div class="dp-table-section-body"><p class="dp-note">${esc(scope)}</p>${content}</div></details>`;
  }

  const viewNumber = () => '2.'+(Math.max(-1,practiceRows().findIndex(p=>p.nbs_id===state.nbs))+2);
  function practices() { return practiceRows().map(p => [p.nbs_id, practiceName(p)]); }
  function mix(m) {
    const kinds = ['literature', 'grey', 'tools', 'unknown'], total = m.known_sources || 0;
    const title = kinds.map(k => `${names[k]}: ${fmt(m.source_mix[k] || 0)}`).join(' · ');
    return `<div class="dp-mix" aria-label="${esc(title)}" title="${esc(title)}"><div class="dp-mix-bar">${kinds.map(k => `<span class="dp-${k}" style="width:${total ? 100 * (m.source_mix[k] || 0) / total : 0}%"></span>`).join('')}</div><span>${kinds.map(k => `<span class="dp-ink-${k}">${fmt(m.source_mix[k] || 0)}</span>`).join(' | ')}</span></div>`;
  }
  function legend() { return '<span class="dp-legend"><span class="dp-ink-literature">Literature</span> | <span class="dp-ink-grey">Grey</span> | <span class="dp-ink-tools">Tools</span> | <span class="dp-ink-unknown">Type not recorded</span></span>'; }
  const percent = (part, total) => total ? `${Number((100 * part / total).toFixed(1))}%` : '—';
  function flow() {
    return `<div class="dp-progress-explanation"><p>The project catalogue contains <strong>${fmt(model.totals.known_sources)} catalogued sources</strong> — published research, grey literature and codebases/tools across all tables and discovery activity. Each table below shows a narrower evidence scope; sources and extracts can support more than one table.</p><p>Automated checks and later review decisions are different steps. Recorded decisions can come from AI or team reviewers. A missing decision does not mean no automated checks occurred, or that every extract needs human review. Human review can focus on questions, exceptions and quality samples.</p><p>A <strong>source</strong> is a publication, report or tool; an <strong>extract</strong> is a saved claim; a <strong>compiled output</strong> is a rule, indicator or assessment. These are different units, not numbers to add together.</p></div>`;
  }
  function column(title, detail) { return `<th scope="col">${title}<small>${detail}</small></th>`; }
  function tableHead(byPractice = false, filters = false, p = null) {
    const sortable=(key,title,detail)=>`<th scope="col">${filters?button('family-sort',title+(state.familySort===key?(state.familySortDesc?' ↓':' ↑'):''),key,'dp-sort'):title}<small>${detail}</small>${filters&&key==='reviewed_excerpts'?`<label class="dp-column-filter">Review status<select id="dp-progress-review">${options([['pending','No later review decision logged'],['unapproved','Unresolved review'],['empty','No extracts']],state.reviewFilter,'All records')}</select></label>`:''}</th>`;
    return `<thead><tr class="dp-stage-head"><th scope="col" rowspan="2">${byPractice?'Practice':'Suitability family'}${filters?`<label class="dp-column-filter">Filter family<select id="dp-progress-family">${familySelectOptions(p)}</select></label>`:''}</th><th scope="colgroup" colspan="1">Collect sources</th><th scope="colgroup" colspan="2">Extract evidence</th><th scope="colgroup" colspan="3">Review decisions</th><th scope="colgroup" colspan="1">Use evidence</th></tr><tr>${sortable('known_sources',state.progressTable?'Sources with '+state.progressTable+' extracts':'Sources catalogued',state.progressTable?'Publications, reports and tools linked to this table':'Publications, reports and tools')}${sortable('extracted_sources','Sources with retained evidence','Sources with at least one non-excluded extract')}${sortable('all_excerpts','Extracts recorded','All saved claims, including excluded claims')}${sortable('reviewed_excerpts','Extracts with a review decision','AI or team decisions; % of all recorded extracts')}${sortable('approved_excerpts','Extracts approved','Count and % of reviewed extracts')}${sortable('dropped_excerpts','Extracts excluded','Saved for audit; not used in synthesis')}${sortable(state.progressTable==='T4'?'t4_structural_relationships':'compiled_outputs',outputTitle(),'Compiled records; may still use evidence awaiting approval')}</tr></thead>`;
  }
  function cells(m) {
    return `<td><b>${fmt(m.known_sources)}</b>${mix(m)}</td><td>${fmt(m.extracted_sources)}</td><td>${fmt(m.all_excerpts)}</td><td title="${fmt(m.reviewed_excerpts)} reviewed out of ${fmt(m.all_excerpts)} recorded extracts">${fmt(m.reviewed_excerpts)} <span class="dp-percent">(${percent(m.reviewed_excerpts,m.all_excerpts)})</span></td><td title="${fmt(m.approved_excerpts)} approved out of ${fmt(m.reviewed_excerpts)} reviewed extracts">${fmt(m.approved_excerpts)} <span class="dp-percent">(${percent(m.approved_excerpts,m.reviewed_excerpts)})</span></td><td>${fmt(m.dropped_excerpts)}</td><td>${fmt(outputCount(m))}</td>`;
  }
  function visibleFamilies(p) { return p.families.filter(f => ((data.family_display_status || {})[f.family_id] || {}).status !== 'out_of_scope' && (f.family_id!=='__unassigned'||['known_sources','all_excerpts','compiled_outputs','t4_structural_relationships'].some(k=>f.metrics[k]>0))); }
  function isEvidenceFamily(f) { return f.navigation_group==='evidence'||(f.scope_kind?f.scope_kind!=='family':f.family_id==='__unassigned'||f.family_id.endsWith('__cross_family')); }
  function namedFamilies(p) { return visibleFamilies(p).filter(f=>!isEvidenceFamily(f)); }
  function familySelectOptions(p) {return '<option value="">All families and evidence groups</option>'+[[false,'Practice families'],[true,'Shared or unassigned evidence']].map(([evidence,title])=>`<optgroup label="${title}">${visibleFamilies(p).filter(f=>isEvidenceFamily(f)===evidence).map(f=>`<option value="${esc(f.family_id)}"${state.familyFilter===f.family_id?' selected':''}>${esc(f.name)}</option>`).join('')}</optgroup>`).join('');}
  function selectedFamilies(p) {
    const rows=visibleFamilies(p).filter(f=>(!state.familyFilter||f.family_id===state.familyFilter)&&(!state.reviewFilter||(state.reviewFilter==='pending'?f.metrics.all_excerpts>f.metrics.reviewed_excerpts:state.reviewFilter==='unapproved'?f.metrics.reviewed_unresolved_excerpts>0:f.metrics.all_excerpts===0)));
    return rows.sort((a,b)=>{const k=state.familySort;const v=k==='name'?a.name.localeCompare(b.name):(a.metrics[k]||0)-(b.metrics[k]||0);return state.familySortDesc?-v:v;});
  }
  function familyRow(f) {
    const scope = (data.family_display_status || {})[f.family_id];
    const broader=isEvidenceFamily(f);
    return `<tr data-feedback-key="${esc(feedbackKey('family:'+f.family_id))}" data-feedback-label="${esc(f.name)}"><th scope="row"><details class="dp-family"><summary>${esc(f.name)}</summary>${scope ? `<p>${esc(scope.label)}. ${esc(scope.reason)}</p>` : ''}${broader?`<p>${esc(f.scope_definition||'A recorded evidence scope, not an additional suitability family. A broad tag does not establish that every claim applies to every family.')}</p>`:''}<ul>${f.subpractices.map(s => `<li>${broader||s.presentation_role==='evidence'?'Evidence routing tag':s.presentation_role==='umbrella'?'Umbrella category':'Variant'}: ${esc(s.name || label(s.subpractice_id))}</li>`).join('')}</ul><p class="dp-note">${broader?'Family applicability must be checked against each claim and its source.':f.subpractices.length?'Counts belong to this family; separate subpractice counts are not recorded.':'No subpractice breakdown recorded.'}</p>${button('scope-bibliography','Inspect these sources',JSON.stringify([state.nbs,f.family_id]))}</details>${broader?'<small class="dp-scope-label">Broader or unassigned evidence scope</small>':''}${scope ? `<small class="dp-scope-label">${esc(scope.label)}</small>` : ''}</th>${cells(f.metrics)}</tr>`;
  }
  function familyTable(p) {
    const chosen=selectedFamilies(p);
    return `<div class="dp-scroll"><table class="dp-table dp-summary-table dp-family-table"><caption>Table ${viewNumber()}.1. ${esc(practiceName(p))}: suitability families and broader evidence scopes</caption>${tableHead(false,true,p)}<tbody>${chosen.map(familyRow).join('')||'<tr><td colspan="8">No families or evidence scopes match the column filters.</td></tr>'}</tbody><tfoot><tr><th scope="row">Whole-practice total<br><small>Includes broader and unassigned evidence; not a sum of family rows.</small></th>${cells(p.metrics)}</tr></tfoot></table></div>`;
  }
  function chartParts(m) {
    return [
      ['approved','Approved',m.approved_excerpts||0],
      ['unresolved','Reviewed · unresolved',m.reviewed_unresolved_excerpts||0],
      ['excluded','Reviewed · excluded',m.reviewed_dropped_excerpts||0],
      ['unreviewed','No later review decision logged',m.unreviewed_excerpts||0]
    ];
  }
  function reviewChart() {
    const rows=progressRows(), max=Math.max(1,...rows.map(p=>p.metrics.all_excerpts||0));
    const percentScale=state.chartScale==='percent', total=progressModel().totals;
    const counts=m=>chartParts(m).map(([key,name,n])=>`<span><i class="dp-chart-key dp-chart-${key}" aria-hidden="true"></i>${fmt(n)} ${esc(name.toLowerCase())}</span>`).join('');
    return `<figure class="dp-review-chart" aria-labelledby="dp-chart-caption"><figcaption id="dp-chart-caption"><strong>Figure ${sectionNumber()}. Evidence collected and review progress · ${esc(progressTitle())}</strong><p>Compare saved extracts and later recorded review decisions, from AI or team reviewers. This chart does not measure all extraction-time automated checks. Each extract appears in one colour only.</p></figcaption><div class="dp-chart-tools"><div class="dp-view-switch" role="group" aria-label="Chart scale"><button id="dp-chart-scale-counts" class="dp-button" data-action="chart-scale" data-value="counts" aria-pressed="${!percentScale}">Number of extracts</button><button id="dp-chart-scale-percent" class="dp-button" data-action="chart-scale" data-value="percent" aria-pressed="${percentScale}">% of recorded extracts</button></div><p class="dp-note">${percentScale?'Every full bar = 100% of that practice’s recorded extracts.':'All practice bars share one count scale: 0–'+fmt(max)+' recorded extracts. Empty space beyond a bar is unused scale, not an evidence status.'}</p></div><div class="dp-chart-legend">${chartParts({}).map(([key,name])=>`<span><i class="dp-chart-key dp-chart-${key}" aria-hidden="true"></i>${esc(name)}</span>`).join('')}</div><div class="dp-chart-axis" aria-hidden="true"><span>0${percentScale?'%':''}</span><span>${percentScale?'50%':fmt(Math.round(max/2))}</span><span>${percentScale?'100%':fmt(max)}</span></div>${rows.map(p=>{
      const m=p.metrics, n=m.all_excerpts||0, parts=chartParts(m), width=percentScale?(n?100:0):100*n/max;
      const description=practiceName(p)+': '+fmt(n)+' recorded extracts. '+parts.map(([,name,value])=>name+': '+fmt(value)).join('; ')+'. '+percent(m.reviewed_excerpts,n)+' reviewed; '+percent(m.approved_excerpts,m.reviewed_excerpts)+' of reviewed extracts approved.';
      return `<section class="dp-chart-row" id="dp-chart-practice-${esc(p.nbs_id)}" data-feedback-key="${esc(feedbackKey('chart-practice:'+p.nbs_id))}"><div class="dp-chart-row-head">${p.nbs_id==='shared'?'<strong>'+esc(practiceName(p))+'</strong>':button('practice',practiceName(p),p.nbs_id,'dp-expand')}<strong>${fmt(n)} extracts</strong></div><p class="dp-chart-context">${fmt(m.known_sources)} sources in scope · ${fmt(m.extracted_sources)} sources with retained evidence · ${fmt(outputCount(m))} ${esc(outputTitle())}</p><div class="dp-chart-track" role="img" aria-label="${esc(description)}"><div class="dp-chart-bar" style="width:${width}%">${parts.map(([key,name,value])=>value?`<span class="dp-chart-${key}" style="width:${100*value/n}%" title="${esc(name)}: ${fmt(value)} (${percent(value,n)} of recorded extracts)"></span>`:'').join('')}</div></div><div class="dp-chart-counts">${counts(m)}</div><p class="dp-chart-rates"><b>${percent(m.reviewed_excerpts,n)} reviewed</b> · ${percent(m.approved_excerpts,m.reviewed_excerpts)} of reviewed extracts approved${n?'':' · No extracts recorded'}</p></section>`;
    }).join('')}<section class="dp-chart-total"><h4>Deduplicated total · ${esc(progressTitle())}</h4><p><strong>${fmt(total.all_excerpts)} extracts recorded</strong> · ${fmt(total.reviewed_excerpts)} reviewed (${percent(total.reviewed_excerpts,total.all_excerpts)}) · ${fmt(total.approved_excerpts)} approved (${percent(total.approved_excerpts,total.reviewed_excerpts)} of reviewed)</p><div class="dp-chart-counts">${counts(total)}</div><p class="dp-note">Practice rows can overlap; this total counts each extract once. Sources and outputs use different units; compiled outputs appear in each practice summary.</p></section><p class="dp-note">“Reviewed” means a later AI or team decision was logged, or explicit approval was recorded. “No later review decision logged” does not mean no automated checks occurred or that human review is required. “Reviewed · excluded” counts exclusions with a logged decision; other excluded claims stay in the no-decision segment. Approval percentages use reviewed extracts; coloured widths use all recorded extracts.</p></figure>`;
  }
  function overviewTable() {
    if(progressModel().project_level && !progressModel().totals.all_excerpts)return `<section><h3>${sectionNumber()} Evidence progress · ${esc(progressTitle())}</h3><div class="dp-orientation"><h4>Shared climate-risk configuration</h4><p>Source collection, extraction and review progress: <strong>not recorded as linked evidence</strong>.</p><p>The configuration has narrative references, but no linked extracts are recorded in this view. This does not mean no research was done. Inspect configured indicators and evidence-link coverage below.</p></div></section>`;
    const general=progressModel().practices.find(p=>p.nbs_id==='cross');
    return `<div class="dp-section-head" id="dp-progress-views"><h3>${sectionNumber()} Evidence progress · ${esc(progressTitle())}</h3><div class="dp-view-switch" role="group" aria-label="Progress presentation"><button id="dp-chart-view-button" class="dp-button" data-action="overview-view" data-value="chart" aria-controls="dp-chart-view" aria-pressed="${state.overviewView==='chart'}">Chart</button><button id="dp-table-view-button" class="dp-button" data-action="overview-view" data-value="table" aria-controls="dp-table-view" aria-pressed="${state.overviewView==='table'}">Table</button></div></div><div id="dp-chart-view"${state.overviewView==='chart'?'':' hidden'}>${reviewChart()}</div><div id="dp-table-view"${state.overviewView==='table'?'':' hidden'}>${legend()}<div class="dp-scroll"><table class="dp-table dp-summary-table"><caption>Table ${sectionNumber()}. Sources, evidence review and use in outputs · ${esc(progressTitle())}</caption>${tableHead(true)}<tbody>${progressRows().map(p=>`<tr class="dp-practice-row" data-feedback-key="${esc(feedbackKey('practice:'+p.nbs_id))}" data-feedback-label="${esc(practiceName(p))}"><th scope="row">${p.nbs_id==='shared'?'<strong>'+esc(practiceName(p))+'</strong>':button('practice',practiceName(p),p.nbs_id,'dp-expand')}<details class="dp-practice-children"><summary>View subpractices</summary><ul>${[...new Set(namedFamilies(p).flatMap(f=>f.subpractices.map(x=>x.name||label(x.subpractice_id))))].map(n=>`<li>${esc(n)}</li>`).join('')||'<li>No subpractices recorded</li>'}</ul></details></th>${cells(p.metrics)}</tr>`).join('')}</tbody><tfoot><tr><th scope="row">Deduplicated scope total</th>${cells(progressModel().totals)}</tr></tfoot></table></div></div><p class="dp-note">Scope totals count each source and extract once. Practice rows can overlap.${general?` Totals include ${fmt(general.metrics.known_sources)} general reference sources that are not a separate practice.`:''} Review percentages use all recorded extracts; approval percentages use reviewed extracts. Review logs include AI and team decisions. Missing decisions do not establish whether automated checks ran or imply that every extract requires human review.</p><p class="dp-note">Search activity is documented in Methods. Its screening counts may repeat a paper across searches, so they are not directly comparable with bibliography source counts. ${button('methods','Inspect search activity')}</p>`;
  }
  function searchEffortCells(m) {
    const s=m.search_metrics;
    return `${['screened','included'].map(k=>`<td class="dp-numbers">${s.complete_counts ? fmt(s['paired_'+k]) : '—'}</td>`).join('')}<td>${fmt(s.complete_counts)} of ${fmt(s.events)}</td>`;
  }
  function searchEffortTable() {
    return `<section class="dp-search-effort" aria-labelledby="dp-search-effort-title"><h3 id="dp-search-effort-title">Search effort · targeted screening</h3><p class="dp-note">We use bounded searches to prioritise relevant, authoritative sources, rather than screen every search-engine hit. Screening assessments and selections below count work logged across searches; the same paper can appear more than once.</p><p class="dp-note"><strong>Search hits are not a screening backlog.</strong> Hit counts overlap and use different counting bases, so they are shown only with individual protocols in Methods. They cannot provide a screening-completion percentage.</p><div class="dp-scroll"><table class="dp-table dp-search-table"><caption>Search activity: candidate assessments, not unique source records</caption><thead><tr><th scope="col">Practice</th>${column('Candidates screened','Assessed for relevance')}${column('Candidates selected','Met the inclusion criteria')}${column('Search records included','Records with all three counts / all logged records')}${column('Search details','Queries, limits and criteria')}</tr></thead><tbody>${practiceRows().map(p=>`<tr><th scope="row">${esc(practiceName(p))}</th>${searchEffortCells(p.metrics)}<td>${button('methods','View protocols',p.nbs_id)}</td></tr>`).join('')}</tbody><tfoot><tr><th scope="row">Recorded totals</th>${searchEffortCells(model.totals)}<td>${button('methods','All protocols')}</td></tr></tfoot></table></div><p class="dp-note">Selections met the search inclusion criteria; they are not counts of unique sources or approved evidence. “Search records included” means records reporting numeric hits, screened and selected counts, out of all logged search events. It measures reporting coverage, not the percentage of research completed; shared runs across tables count once. Other records remain in Methods. “—” means no usable count recorded, not zero work.</p></section>`;
  }
  function countNotes(p=null) {
    const m=p?p.metrics:progressModel().totals, keys=m.source_keys;
    const sources=model.sources.filter(r=>Array.isArray(keys)?keys.includes(r.key):!p||r.nbs_ids.includes(p.nbs_id));
    const registeredIds=new Set((data.registers.SRC_source_register||[]).map(r=>r.source_id));
    const n=sources.filter(r=>[r.source_id,...(r.aliases||[])].some(id=>registeredIds.has(id))).length;
    const scope=progressTitle()+(p?' · '+practiceName(p):' · all practices');
    return `<details class="dp-definitions"><summary>${viewNumber()}.5 Count definitions · ${esc(scope)}</summary><dl><dt>Publications, reports and tools</dt><dd>${fmt(m.known_sources)} catalogued sources linked to ${esc(scope)}: ${fmt(n)} in the source register and ${fmt(sources.length-n)} tracked only in the acquisition queue. This is a table-specific evidence cohort, not the whole project. Across all tables and discovery activity, the project catalogue contains ${fmt(model.totals.known_sources)} known sources. Recorded duplicate links are merged; unlinked duplicates may remain, so these are catalogue counts rather than a verified count of unique publications. Unreconciled stocktake resources are not included in these totals. ${button('known','Inspect sources in this scope',p?p.nbs_id:'')} ${button('project-bibliography','Explore project bibliography')}</dd><dt>Extracts recorded</dt><dd>Every saved evidence claim in the displayed table scope, including excluded claims. Excluded claims remain auditable but do not contribute to synthesis.</dd><dt>Automated checks and later review</dt><dd>Extraction and automated validation precede later Keep, Drop, Query or Reclassify decisions. These later decisions can be made by AI or team reviewers. “Reviewed” counts extracts with a logged decision or explicit approval, once per extract. Automatic flags alone do not count. “No later review decision logged” does not mean no AI checks occurred or that every extract requires a human check. Individual automated-check coverage is not available here; an absent flag is not proof of a completed check.</dd><dt>Reviewed versus approved</dt><dd>Reviewed % = extracts with a recorded decision or explicit approval / all recorded extracts. Approved = currently accepted, non-excluded claims. Approved % = approved / reviewed. A recorded decision can remain unresolved. These counts do not identify who performed an unrecorded check.</dd><dt>Source types</dt><dd>Published literature, grey literature and codebases/tools follow source metadata. “Type not recorded” means missing or conflicting classification. Stocktake describes how a source was found, not its publication type.</dd><dt>Family scope</dt><dd>Named suitability families describe shared constraints. Broader evidence and sources without a recorded family appear in the same table with an explicit scope label; no automatic assignment to a narrower family is made. Sources can support multiple families, so their counts overlap.</dd><dt>Compiled outputs</dt><dd>T4 counts structural suitability rules; T3 counts hazard-response assessments; T6 counts benefit assessments. T2a counts shared climate-risk indicators. Context variants and practice/family roll-ups are separate output records. Evidence can support multiple tables: never add their totals. Compilation does not certify approval.</dd></dl></details>`;
  }
  const pipelineKey = r => 'ledger:'+['nbs_id','family','table','category'].map(k=>encodeURIComponent(r[k]||'')).join(':');
  function pipelineRows() {
    return (data.progress_ledger || []).filter(r=>(!pipelineState.nbs||r.nbs_id===pipelineState.nbs)&&(!pipelineState.family||(pipelineState.family==='__practice'?!r.family:r.family===pipelineState.family))&&(!pipelineState.table||r.table===pipelineState.table)&&(!pipelineState.channel||r.category===pipelineState.channel)).sort((a,b)=>{
      const result=String(a[pipelineState.sort]||'').localeCompare(String(b[pipelineState.sort]||''));
      return pipelineState.descending?-result:result;
    });
  }
  function renderPipelineRecords() {
    const host=$('pipeline-records-app');if(!model||!host)return;
    const all=data.progress_ledger||[], rows=pipelineRows(), size=20;
    pipelineState.page=Math.max(0,Math.min(pipelineState.page,Math.ceil(rows.length/size)-1));
    const choices=(rows,key,display)=>[...new Set(rows.map(r=>r[key]).filter(Boolean))].sort().map(v=>[v,display(v)]);
    const practiceChoices=choices(all,'nbs_id',v=>model.practices.find(p=>p.nbs_id===v)?.name||label(v));
    const familyChoices=choices(all.filter(r=>!pipelineState.nbs||r.nbs_id===pipelineState.nbs),'family',familyLabel);
    const sort=(key,title)=>button('pipeline-sort',title+(pipelineState.sort===key?(pipelineState.descending?' ↓':' ↑'):''),key,'dp-sort');
    const stage=v=>({done:'Complete',in_progress:'In progress · % not recorded',not_started:'Not started',blocked:'Blocked',deferred:'Deferred'}[v]||(v?label(v):'Not recorded'));
    const stages=[['searched','Search'],['screened','Screening'],['extracted','Extraction'],['verified','Verification'],['reviewed','Review']].filter(([key])=>all.some(r=>Object.prototype.hasOwnProperty.call(r,key)));
    host.innerHTML=`<div class="dp-shell" id="dp-ledger" data-feedback-key="id:dp-ledger"><h3>5.3 Pipeline records</h3><p>This operational log records the stages marked by the team or pipeline for each practice, family, table and discovery channel. Only stages stored in this log appear below; extract and review-decision counts remain in Progress. A blank verification stage does not establish that no checks occurred; “in progress” has no percentage denominator.</p><div class="dp-filters"><label>Practice<select id="dp-pipeline-nbs">${options(practiceChoices,pipelineState.nbs,'All practices')}</select></label><label>Family / scope<select id="dp-pipeline-family">${options([['__practice','Whole-practice searches'],...familyChoices],pipelineState.family,'All families and scopes')}</select></label><label>Analytical table<select id="dp-pipeline-table">${options(choices(all,'table',v=>v),pipelineState.table,'All tables')}</select></label><label>Discovery channel<select id="dp-pipeline-channel">${options(choices(all,'category',v=>names[v]||label(v)),pipelineState.channel,'All channels')}</select></label>${button('pipeline-reset','Reset filters')}</div><p class="dp-results" aria-live="polite">${fmt(rows.length)} records · ${rows.length?pipelineState.page*size+1:0}–${Math.min(rows.length,(pipelineState.page+1)*size)} shown</p><div class="dp-scroll"><table class="dp-table dp-monitor-table"><caption>Table 5.3. Recorded pipeline stages</caption><thead><tr><th scope="col">${sort('nbs_id','Practice')}</th><th scope="col">${sort('family','Family / scope')}</th><th scope="col">${sort('table','Table')}</th><th scope="col">${sort('category','Discovery channel')}</th>${stages.map(([key,title])=>`<th scope="col">${sort(key,title)}</th>`).join('')}<th scope="col">${sort('updated','Updated')}</th></tr></thead><tbody>${rows.slice(pipelineState.page*size,(pipelineState.page+1)*size).map(r=>`<tr data-feedback-key="${esc(pipelineKey(r))}" data-feedback-label="${esc([label(r.nbs_id),r.family?familyLabel(r.family):'Whole-practice search',r.table,names[r.category]||label(r.category)].join(' · '))}"><th scope="row">${esc(model.practices.find(p=>p.nbs_id===r.nbs_id)?.name||label(r.nbs_id))}</th><td title="${esc(r.note)}">${esc(r.family?familyLabel(r.family):'Whole-practice search')}</td><td>${esc(r.table)}</td><td>${esc(names[r.category]||label(r.category))}</td>${stages.map(([key])=>`<td><span class="dp-stage ${r[key]==='done'?'dp-stage-done':''}">${esc(stage(r[key]))}</span></td>`).join('')}<td>${esc(r.updated||'—')}</td></tr>`).join('')||`<tr><td colspan="${stages.length+5}">No pipeline records match these filters.</td></tr>`}</tbody></table></div><div class="dp-pagination"><button type="button" class="dp-button" data-action="pipeline-page" data-value="-1"${pipelineState.page===0?' disabled':''}>Previous</button><span>Page ${pipelineState.page+1} / ${Math.max(1,Math.ceil(rows.length/size))}</span><button type="button" class="dp-button" data-action="pipeline-page" data-value="1"${(pipelineState.page+1)*size>=rows.length?' disabled':''}>Next</button></div></div>`;
    ['nbs','family','table','channel'].forEach(key=>{
      $('dp-pipeline-'+key).onchange=e=>{pipelineState[key]=e.target.value;if(key==='nbs')pipelineState.family='';pipelineState.page=0;renderPipelineRecords();$('dp-pipeline-'+key).focus();};
    });
    if(window.DashboardShell)window.DashboardShell.syncSubtabs();
  }
  function practiceView(p) {
    return `<h3>${viewNumber()}.1 T4 · Evidence by suitability family</h3><p class="dp-note">Follow sources through saved extracts, recorded review decisions and compiled suitability rules. Named families and broader evidence scopes share this table. Family rows overlap; the total counts each source and extract once. A missing review decision does not establish whether automated checks ran or imply a human-review backlog.</p>${legend()}${familyTable(p)}`;
  }
  function bindProgressFilters() {
    [['dp-progress-family','familyFilter'],['dp-progress-review','reviewFilter']].forEach(([id,key])=>{
      const node=$(id);if(!node)return;
      node.onchange=e=>{state[key]=e.target.value;renderProgress();$(id).focus();};
    });
  }
  function renderProgress() {
    ['T2a','T3','T6'].forEach(t=>{const el=$('dp-section-'+t);if(el)sectionState[t].open=el.open;});
    state.progressTable='T4';
    const p=(progressModel().practices||[]).find(p=>p.nbs_id===state.nbs);
    const sections=['T4','T2a','T3','T6'].filter(t=>t==='T4'||model.table_views?.[t]).map(tableSection).join('');
    state.progressTable='T4';state.overviewView=sectionState.T4.view;state.chartScale=sectionState.T4.scale;
    $('progress-app').innerHTML=`<div class="dp-shell"><nav class="dp-subtabs shell-subnav" aria-label="Progress views">${button('practice','2.1 Overview','',!p?'is-active':'')}${practiceRows().map((p,i)=>button('practice',`2.${i+2} ${practiceName(p)}`,p.nbs_id,state.nbs===p.nbs_id?'is-active':'')).join('')}</nav><header class="dp-intro"><div class="dp-eyebrow">Rural NbS Scan · ${p?'Practice progress':'Project progress'}</div><h2>${viewNumber()} ${p?esc(practiceName(p)):'Progress overview'}</h2><p>${p?'Follow this practice’s sources and extracted evidence through recorded review decisions to the tables used by the Rural NbS Scan.':'Research effort from source discovery through evidence extraction and checking to the tables that power the Rural NbS Scan.'}</p><div class="dp-actions">${button('bibliography','Explore bibliography',state.nbs)}${button('methods','Read methods',state.nbs)}</div></header>${p?'':flow()}${sections}${countNotes(p)}</div>`;
    bindProgressFilters();
    if(window.DashboardShell)window.DashboardShell.syncSubtabs();
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
    registered=new Map((data.registers.SRC_source_register||[]).map(r=>[r.source_id,r]));
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
  const originNames = {stock:'Stocktake',updated_lit:'Literature search',grey:'Grey-literature search',tool:'Tool search'};
  const tableNames = {T4:'T4 suitability',T3:'T3 hazard response',T6:'T6 benefits',M2b:'M2b risk roles'};
  const roleNames = {structural_suitability:'Suitability',nbs_effect:'Effects',operational_risk:'Operational risk',asset_vulnerability:'Asset vulnerability',climate_risk:'Climate risk'};
  function familyLabel(id) {
    if (!id || id==='__unassigned') return 'Family not recorded';
    if(id.endsWith('__cross_family'))return 'Evidence tagged for all families';
    const f=model.practices.flatMap(p=>p.families).find(f=>f.family_id===id);
    return f ? f.name : 'Recorded scope: '+label(id.split('__').pop());
  }
  function evidenceFamilies(row) { return list(row.suitability_family_id).map(f=>f.includes('__')?f:(row.nbs_id?row.nbs_id+'__'+f:f)); }
  function familyOptions(nbs='') {
    const known=new Map(model.practices.filter(p=>!nbs||p.nbs_id===nbs).flatMap(p=>p.families.map(f=>[f.family_id,[f.family_id,(nbs?'':practiceName(p)+' · ')+familyLabel(f.family_id)]])));
    const registeredFamilies=new Set(model.practices.flatMap(p=>p.families.map(f=>f.family_id)));
    bibliography.filter(s=>!nbs||s.nbs_ids.includes(nbs)).forEach(s=>s.family_ids.forEach(f=>{if(!registeredFamilies.has(f))known.set(f,[f,familyLabel(f)+' (unmapped)']);}));
    if(!nbs&&known.has('__unassigned'))known.set('__unassigned',['__unassigned','Family not recorded (any practice)']);
    return [...known.values()];
  }
  function filteredBibliography() {
    const q=state.query.trim().toLowerCase();
    const scope=model.practices.find(p=>p.nbs_id===state.bibNbs)?.families.find(f=>f.family_id===state.bibFamily);
    const scopes=state.bibNbs?(scope?[scope]:[]):model.practices.flatMap(p=>p.families.filter(f=>f.family_id===state.bibFamily));
    const scopeKeys=scopes.length&&scopes.every(f=>Array.isArray(f.metrics.source_keys))?new Set(scopes.flatMap(f=>f.metrics.source_keys)):null;
    return bibliography.filter(s=>(!state.bibKeys||state.bibKeys.includes(s.key)) && (!state.bibNbs||s.nbs_ids.includes(state.bibNbs)) &&
      (!state.bibFamily||(scopeKeys?scopeKeys.has(s.key):state.bibFamily==='__unassigned'?!s.family_ids.some(id=>model.practices.filter(p=>!state.bibNbs||p.nbs_id===state.bibNbs).some(p=>p.families.some(f=>f.family_id===id&&f.family_id!=='__unassigned'))):s.family_ids.includes(state.bibFamily))) && (!state.bibType||s.type===state.bibType) &&
      (!state.bibOrigin||s.origins.includes(state.bibOrigin)) &&
      (!state.bibSet||(state.bibSet==='legacy'?s.legacy:!s.legacy)) &&
      (!state.bibTable||(s.contributions[state.bibTable]||[]).length) &&
      (!state.bibEvidence||(state.bibEvidence==='retained'?s.evidence_ids.length>0:state.bibEvidence==='pending'?s.evidence_ids.length>s.approved_evidence_ids.length:state.bibEvidence==='approved'?s.approved_evidence_ids.length>0:s.evidence_ids.length===0)) &&
      (!q||[s.citation,s.source_id,s.doi,s.rawPractice,...(s.aliases||[]),...s.nbs_ids,...s.origins,...s.family_ids.map(familyLabel)].join(' ').toLowerCase().includes(q)));
  }
  function extractionSummary(source) {
    const c=source.extraction_counts;
    return c ? `Extracted: T4 ${fmt(c.T4)} · Effects ${fmt(c.effects)} · M2b ${fmt(c.M2b)}`+(c.other?` · Other ${fmt(c.other)}`:'') : 'Extraction categories not linked';
  }
  function contributionButtons(source) {
    if(source.legacy)return '<span class="dp-note">Not linked</span>';
    return '<div class="dp-count-buttons">'+Object.entries(tableNames).map(([t,title])=>{
      const n=(source.contributions[t]||[]).length;
      return n ? button('source-evidence',`${title} · ${fmt(n)}`,JSON.stringify([source.key,t]),'dp-count-button') : `<span class="dp-count-zero">${esc(title)} · 0</span>`;
    }).join('')+'</div>';
  }
  function renderBibliography() {
    if(!model)return;
    const rows=filteredBibliography(),size=30,moreOpen=$('dp-bib-more')&&$('dp-bib-more').open;
    const extraFilters=[state.bibFamily,state.bibType,state.bibOrigin,state.bibEvidence,state.bibSet,state.bibTable].filter(Boolean).length;
    state.page=Math.max(0,Math.min(state.page,Math.ceil(rows.length/size)-1));
    $('bibliography-app').innerHTML=`<div class="dp-shell"><header class="dp-intro dp-bib-intro"><div class="dp-eyebrow">Bibliography · sources & tools</div><h2>Find a source. Explore its evidence.</h2><p>Search publications and resources, then open their details and evidence beside this catalogue.</p></header>
      <div class="dp-filters dp-bib-filters"><label>Search sources<input id="dp-bib-query" type="search" value="${esc(state.query)}" placeholder="Title, author, source ID or family…"></label>
      <label>Practice<select id="dp-bib-nbs">${options(practices(),state.bibNbs,'All practices')}</select></label></div>
      <details class="dp-bib-more" id="dp-bib-more"${moreOpen?' open':''}><summary>More filters${extraFilters?' · '+extraFilters+' active':''}</summary><div class="dp-filters dp-bib-filters dp-bib-more-filters">
      <label>Family<select id="dp-bib-family">${options(familyOptions(state.bibNbs),state.bibFamily,'All families')}</select></label>
      <label>Source type<select id="dp-bib-type">${options(Object.entries(names).filter(([k])=>['literature','grey','tools','unknown'].includes(k)),state.bibType,'All types')}</select></label>
      <label>Discovery origin<select id="dp-bib-origin">${options(Object.entries(originNames),state.bibOrigin,'All origins')}</select></label>
      <label>Evidence status<select id="dp-bib-evidence">${options([['retained','With retained excerpts'],['pending','Excerpts awaiting approval'],['approved','With approved excerpts'],['empty','No retained excerpts']],state.bibEvidence,'All evidence states')}</select></label>
      <label>Records<select id="dp-bib-set">${options([['known','Known source records'],['legacy','Unreconciled legacy resources']],state.bibSet,'All records')}</select></label>
      <label>Used in<select id="dp-bib-table">${options(Object.entries(tableNames),state.bibTable,'Any contribution')}</select></label></div></details>
      <details class="dp-definitions dp-bib-notes"><summary>What this catalogue includes · ${fmt(model.sources.length)} known sources + ${fmt(bibliography.length-model.sources.length)} legacy resources</summary><p>Legacy resources may overlap with known sources and are excluded from progress totals. Family associations include recorded historical work. Unmapped scope tags are shown as recorded, without assigning them to a suitability family.</p><p>Source-level screening decisions, exact discovery-search links and citation-chasing parents are not recorded. Extraction does not establish a screening decision.</p><p>Compiled contributions count distinct retained excerpts cited by T4, T3 or T6. M2b counts operational-risk and asset-vulnerability excerpts, not compiled outputs. Categories overlap; never add the table counts. T6 economics contributions are not shown in this catalogue.</p><p>Approved excerpts are part of retained evidence, not a whole-paper approval. Extraction categories are distinct from compiled contributions.</p></details>
      <div class="dp-bib-toolbar">${state.bibKeys?`<p class="dp-note">Selected progress sources: ${esc(state.bibScopeLabel)}. Reset filters to return to the full bibliography.</p>`:''}<p class="dp-results" aria-live="polite">${fmt(rows.length)} matching records · ${rows.length?state.page*size+1:0}–${Math.min(rows.length,(state.page+1)*size)} shown</p>${button('bib-reset','Reset filters')}</div>
      <div class="dp-scroll"><table class="dp-table dp-bibliography dp-bib-table"><caption class="dp-sr-only">Source catalogue and linked evidence</caption><thead><tr>${['Publication / resource','Type & discovery origin','Practice / recorded scope','Evidence excerpts','Used in · excerpt counts'].map(t=>`<th scope="col">${t}</th>`).join('')}</tr></thead><tbody>${rows.slice(state.page*size,(state.page+1)*size).map(s=>`<tr data-feedback-key="source:${esc(s.key)}" data-feedback-label="${esc(s.citation)}"${drawerSource===s.key?' class="dp-source-selected"':''}><th scope="row">${button('source',s.citation,s.key,'dp-source-title')}<small>${esc(s.source_id||'Legacy resource · identity not reconciled')}</small></th><td>${esc(names[s.type]||names.unknown)}<small>${esc(s.origins.map(o=>originNames[o]||label(o)).join(', ')||'Origin not recorded')}</small></td><td>${esc(s.nbs_ids.map(label).join(', ')||s.rawPractice||'Not assigned')}<small>${s.family_ids.length?esc(s.family_ids.map(familyLabel).join('; ')):'Family not assigned'}</small></td><td>${s.legacy?'Not linked':button('source-evidence',`${fmt(s.evidence_ids.length)} retained`,JSON.stringify([s.key,'']),'dp-count-button')}<small>${s.legacy?'':`${fmt(s.approved_evidence_ids.length)} approved · ${fmt(s.dropped_evidence_ids.length)} quarantined`}</small>${s.legacy?'':`<small>${esc(extractionSummary(s))}</small>`}</td><td>${contributionButtons(s)}</td></tr>`).join('')||'<tr><td colspan="5">No matching records. Reset filters or broaden the search.</td></tr>'}</tbody></table></div>
      <div class="dp-pagination"><button type="button" class="dp-button" data-action="page" data-value="-1"${state.page===0?' disabled':''}>Previous</button><span>Page ${state.page+1} / ${Math.max(1,Math.ceil(rows.length/size))}</span><button type="button" class="dp-button" data-action="page" data-value="1"${(state.page+1)*size>=rows.length?' disabled':''}>Next</button></div></div>`;
    const query=$('dp-bib-query');
    query.addEventListener('input',()=>{state.query=query.value;state.page=0;const pos=query.selectionStart;renderBibliography();const next=$('dp-bib-query');next.focus();next.setSelectionRange(pos,pos);});
    [['nbs','bibNbs'],['family','bibFamily'],['type','bibType'],['origin','bibOrigin'],['evidence','bibEvidence'],['set','bibSet'],['table','bibTable']].forEach(([id,key])=>$('dp-bib-'+id).addEventListener('change',e=>{state[key]=e.target.value;if(key==='bibNbs')state.bibFamily='';state.page=0;renderBibliography();$('dp-bib-'+id).focus();}));
  }
  function sourceRecords(source) {
    const ids=[source.source_id,...(source.aliases||[])];
    return ids.map(id=>registered.get(id)).filter(Boolean);
  }
  function libraryUrl(row) { return row && row.library_path && typeof window.vfSharePointUrl==='function' ? safeUrl(window.vfSharePointUrl(row.library_path)) : ''; }
  function sourceLinks(source) {
    const rows=sourceRecords(source),seen=new Set(),links=[];
    for(const r of rows){const url=libraryUrl(r);if(url&&!seen.has(url)){seen.add(url);links.push(link(url,'Team library'+(rows.length>1?' · '+r.source_id:'' )+' ↗'));}}
    if(safeUrl(source.url)&&!seen.has(safeUrl(source.url)))links.push(link(source.url,'Publisher / website ↗'));
    return links.length?links.join(' '):'<span class="dp-note">No source link recorded.</span>';
  }
  function passageLink(row,source) {
    const raw=registered.get(row.source_id), url=libraryUrl(raw)||safeUrl((raw||{}).url)||safeUrl(source.url);
    if(!url)return '';
    const page=String(row.page||'');
    if(/^\d+$/.test(page)&&Number(page)>0&&(!row.locator_type||row.locator_type==='page')&&/\.pdf(?:$|[?#])/i.test(url)){
      const u=new URL(url);u.hash='page='+page;return link(u.href,`Open PDF · page ${page} ↗`);
    }
    // A file locator is a deep link only with a pinned commit and a complete path/range.
    const loc=String(row.locator||'').match(/^(.+):L(\d+)(?:-L?(\d+))?$/);
    const repo=new URL(url).pathname.split('/').filter(Boolean);
    if(row.locator_type==='file_line'&&loc&&/^[a-f0-9]{7,40}$/i.test(row.commit_sha||'')&&new URL(url).hostname==='github.com'&&repo.length>=2&&!loc[1].split('/').includes('..')){
      return link(`https://github.com/${repo.slice(0,2).join('/')}/blob/${row.commit_sha}/${loc[1].split('/').map(encodeURIComponent).join('/')}#L${loc[2]}${loc[3]?'-L'+loc[3]:''}`,'Open pinned code passage ↗');
    }
    return link(url,'Open source ↗');
  }
  function recordDetails(row) {
    const fields=Object.entries(row).filter(([k,v])=>k!=='quote'&&v!==null&&v!==undefined&&v!=='');
    return `<dl>${fields.map(([k,v])=>`<dt>${esc(label(k))}</dt><dd>${esc(typeof v==='object'?JSON.stringify(v,null,2):v)}</dd>`).join('')}</dl>`;
  }
  function sourceDetails(source) {
    const rows=sourceRecords(source);
    const fields=['citation','doi','url','source_kind','venue_type','method_type','benchmark_tier','study_country','region','study_income_group','farming_system','spatial_scale','access_status','license','retrieved_at','extraction_status','extraction_date','extraction_run_id','extractor'];
    return `<section class="dp-source-meta"><h3>Publication & provenance</h3><dl><dt>Source ID</dt><dd>${esc(source.source_id||'Legacy resource; identity not reconciled')}</dd><dt>Recorded citation</dt><dd>${esc(source.citation)}</dd><dt>Publication DOI</dt><dd>${esc(source.doi||'Not recorded')}</dd><dt>Source type</dt><dd>${esc(names[source.type]||names.unknown)}</dd><dt>Discovery origin</dt><dd>${esc(source.origins.map(o=>originNames[o]||label(o)).join(', ')||'Not recorded')}</dd><dt>Exact search / citation-chasing parent</dt><dd>Not recorded at source level</dd><dt>Screening decision</dt><dd>Not recorded at source level; extraction is not a screening decision.</dd><dt>Practices</dt><dd>${esc(source.nbs_ids.map(label).join(', ')||source.rawPractice||'Not assigned')}</dd><dt>Families / recorded scope</dt><dd>${esc(source.family_ids.map(familyLabel).join('; ')||'Not assigned')}</dd><dt>Acquisition queue</dt><dd>${esc((source.queue_statuses||[]).map(label).join(', ')||'Not recorded')}</dd></dl>
      ${rows.map((r,i)=>`<details${i===0?' open':''}><summary>${i===0&&r.source_id===source.source_id?'Registered source details':'Linked source record'} · ${esc(r.source_id)}</summary>${rows.length>1?'<p class="dp-note">Metadata belongs to this source ID; linked records may differ.</p>':''}<dl>${fields.filter(k=>r[k]!==undefined&&r[k]!==null&&r[k]!=='').map(k=>`<dt>${esc(label(k))}</dt><dd>${esc(Array.isArray(r[k])?r[k].join(', '):r[k])}</dd>`).join('')||'<dd>No additional metadata recorded.</dd>'}</dl></details>`).join('')}
      ${source.raw?`<details><summary>Legacy resource details</summary>${recordDetails(source.raw)}</details>`:''}
      ${(source.tools||[]).map(t=>`<details><summary>${esc(t.name||'Tool details')}</summary>${recordDetails(t)}</details>`).join('')}
      <h3>Evidence contributions</h3>${contributionButtons(source)}<p class="dp-note">T4/T3/T6 count retained excerpts cited by compiled tables. M2b counts risk roles. These counts overlap. T6 economics contributions are not shown.</p></section>`;
  }
  function closeDrawer() {
    const d=$('dp-source-drawer');if(d)d.remove();drawerSource='';
    document.querySelectorAll('.dp-source-selected').forEach(r=>r.classList.remove('dp-source-selected'));
    if(location.hash.startsWith('#source='))history.replaceState(null,'',location.pathname+location.search);
    if(drawerReturn&&drawerReturn.isConnected)drawerReturn.focus();else if($('dp-bib-query'))$('dp-bib-query').focus();
  }
  function openSource(id,table='') {
    if(!model)return;
    const source=bibliography.find(s=>s.key===id||s.source_id===id||(s.aliases||[]).includes(id));
    if(!source)return;
    if(!$('dp-source-drawer'))drawerReturn=document.activeElement;
    drawerSource=source.key;
    const activeTab=document.querySelector('.tab-btn.active');drawerTab=activeTab?activeTab.dataset.tab:'';
    document.querySelectorAll('#bibliography-app tr[data-feedback-key]').forEach(r=>{r.classList.remove('dp-source-selected');if(r.dataset.feedbackKey==='source:'+source.key)r.classList.add('dp-source-selected');});
    const old=$('dp-source-drawer');if(old)old.remove();
    const d=document.createElement('aside');d.id='dp-source-drawer';d.className='dp-drawer dp-source-drawer';d.dataset.feedbackKey='source:'+source.key;d.dataset.feedbackLabel=source.citation;d.setAttribute('role','dialog');d.setAttribute('aria-label','Source details and evidence');d.setAttribute('aria-modal','false');d.tabIndex=-1;
    const ids=[...new Set([...source.evidence_ids,...source.dropped_evidence_ids])];
    const all=ids.map(id=>evidence.get(id)).filter(Boolean);
    let view=all.length||table?'evidence':'details',limit=20;
    const filter={query:'',family:'',role:'',table,review:'',dropped:false};
    const familyIds=[...new Set(all.flatMap(evidenceFamilies))],roles=[...new Set(all.map(r=>r.use_role).filter(Boolean))];
    d.innerHTML=`<div class="dp-drawer-head"><h2>Source & evidence</h2>${button('close','Close ×')}</div><div class="dp-source-summary"><h3>${esc(source.citation)}</h3><div class="dp-record-links">${sourceLinks(source)}</div></div><nav class="dp-source-nav" aria-label="Source views"><button type="button" class="dp-button" id="dp-view-evidence">Evidence (${fmt(source.evidence_ids.length)})</button><button type="button" class="dp-button" id="dp-view-details">Source details</button></nav>
      <section id="dp-source-details" class="dp-source-panel">${sourceDetails(source)}</section>
      <section id="dp-source-evidence" class="dp-source-panel"><div class="dp-evidence-summary"><h3>Evidence excerpts</h3><p>${fmt(source.evidence_ids.length)} retained · ${fmt(source.approved_evidence_ids.length)} approved · ${fmt(source.dropped_evidence_ids.length)} quarantined</p><p class="dp-note">${esc(extractionSummary(source))}. Approval applies to excerpts, not the whole paper.</p></div>
      <div class="dp-filters dp-source-filters"><label>Search excerpts<input type="search" id="dp-excerpt-query" placeholder="Quote, variable or evidence ID…"></label><label>Excerpt family<select id="dp-excerpt-family">${options(familyIds.map(f=>[f,familyLabel(f)]),'','All families')}${all.some(r=>!evidenceFamilies(r).length)?'<option value="__unassigned">Practice-wide / not assigned</option>':''}</select></label><label>Evidence role<select id="dp-excerpt-role">${options(roles.map(r=>[r,roleNames[r]||label(r)]),'','All roles')}</select></label><label>Contribution<select id="dp-excerpt-table">${options(Object.entries(tableNames),table,'All contributions')}</select></label><label>Excerpt review<select id="dp-excerpt-review">${options([['approved','Approved'],['pending','Awaiting approval'],['dropped','Quarantined']],'','All review states')}</select></label></div>
      <label class="dp-toggle"><input id="dp-show-dropped" type="checkbox"> Include quarantined excerpts</label><div class="dp-bib-toolbar"><p id="dp-excerpt-results" class="dp-results" aria-live="polite"></p><button type="button" class="dp-button" id="dp-excerpt-reset">Reset excerpt filters</button></div><div id="dp-drawer-evidence"></div></section>`;
    document.body.appendChild(d);
    function setView(next){view=next;$('dp-source-details').hidden=view!=='details';$('dp-source-evidence').hidden=view!=='evidence';['details','evidence'].forEach(v=>{const b=$('dp-view-'+v);b.setAttribute('aria-pressed',String(view===v));b.className='dp-button'+(view===v?' is-active':'');});}
    function render(){
      const selected=all.filter(r=>{
        const dropped=r.review_state==='dropped',approved=!dropped&&String(r.reviewer_ok)==='true';
        return (!dropped||filter.dropped)&&(!filter.family||(filter.family==='__unassigned'?!evidenceFamilies(r).length:evidenceFamilies(r).includes(filter.family)))&&(!filter.role||r.use_role===filter.role)&&(!filter.table||(source.contributions[filter.table]||[]).includes(r.evidence_id))&&(!filter.review||(filter.review==='dropped'?dropped:filter.review==='approved'?approved:!dropped&&!approved))&&(!filter.query||[r.quote,r.variable,r.effect_indicator,r.evidence_id,r.raw_name,r.taxon].join(' ').toLowerCase().includes(filter.query.toLowerCase().trim()));
      });
      $('dp-excerpt-results').textContent=`${fmt(selected.length)} matching excerpts · ${fmt(Math.min(selected.length,limit))} shown`;
      $('dp-drawer-evidence').innerHTML=selected.slice(0,limit).map(r=>{
        const dropped=r.review_state==='dropped',status=dropped?'Quarantined':String(r.reviewer_ok)==='true'?'Approved':'Awaiting approval';
        const used=Object.entries(tableNames).filter(([t])=>(source.contributions[t]||[]).includes(r.evidence_id)).map(([,n])=>n);
        return `<article class="dp-excerpt" data-vfeid="${esc(r.evidence_id)}" data-feedback-key="evidence:${esc(r.evidence_id)}"><header><strong>${esc(label(r.variable||r.effect_indicator||r.use_role))}</strong><span class="dp-evidence-status">${status}</span></header><small>${esc(r.evidence_id)}</small><p>${esc(label(r.nbs_id))} · ${esc(evidenceFamilies(r).map(familyLabel).join('; ')||'Practice-wide / family not assigned')}<br>${esc(roleNames[r.use_role]||label(r.use_role))}${r.claim_scope?' · '+esc(label(r.claim_scope)):''}${r.taxon?' · '+esc(r.taxon):''}</p><blockquote>${esc(r.quote||'No quote recorded')}</blockquote><div class="dp-record-links"><span>${esc(r.locator||(r.page?'Page '+r.page:'Locator not recorded'))}</span>${passageLink(r,source)}</div><p class="dp-note">${dropped?'Quarantined; excluded from active contributions.':used.length?'Used in: '+esc(used.join(' · ')):'No compiled contribution or M2b risk role recorded.'}</p><details><summary>Full evidence record</summary>${recordDetails(r)}</details></article>`;
      }).join('')||'<p class="dp-empty">No linked excerpts match these filters. Reset excerpt filters to broaden this view.</p>';
      if(selected.length>limit){const b=document.createElement('button');b.type='button';b.className='dp-button';b.textContent=`Show more (${selected.length-limit} remaining)`;b.onclick=()=>{const firstNew=limit;limit+=20;render();const next=document.querySelectorAll('#dp-drawer-evidence .dp-excerpt')[firstNew];if(next){next.tabIndex=-1;next.focus();}};$('dp-drawer-evidence').appendChild(b);}
    }
    ['details','evidence'].forEach(v=>$('dp-view-'+v).onclick=()=>setView(v));
    $('dp-excerpt-query').oninput=e=>{filter.query=e.target.value;limit=20;render();};
    ['family','role','table','review'].forEach(k=>$('dp-excerpt-'+k).onchange=e=>{filter[k]=e.target.value;if(k==='review'&&filter.review==='dropped'){filter.dropped=true;$('dp-show-dropped').checked=true;}limit=20;render();});
    $('dp-show-dropped').onchange=e=>{filter.dropped=e.target.checked;if(!filter.dropped&&filter.review==='dropped'){filter.review='';$('dp-excerpt-review').value='';}limit=20;render();};
    $('dp-excerpt-reset').onclick=()=>{Object.assign(filter,{query:'',family:'',role:'',table:'',review:'',dropped:false});['query','family','role','table','review'].forEach(k=>$('dp-excerpt-'+k).value='');$('dp-show-dropped').checked=false;limit=20;render();};
    setView(view);render();d.focus();history.replaceState(null,'','#source='+encodeURIComponent(source.key));
  }
  function originalProtocols(records) {
    const fieldNames = {search_id:'Search record', n_retrieved:'Reported search hits', n_screened:'Screening assessments', n_included:'Selections', search_date:'Search date', nbs_id:'Practice', suitability_family_id:'Suitability family', run_id:'Search run', ruleset_version:'Method version'};
    return (records || []).map((r,i)=>`<table class="dp-protocol-record"><caption>Original search record ${i+1}</caption><tbody>${Object.entries(r).map(([k,v])=>`<tr><th scope="row">${esc(fieldNames[k] || label(k))}</th><td>${esc(Array.isArray(v)?v.join('; '):v == null || v === '' ? 'Not recorded' : v)}</td></tr>`).join('')}</tbody></table>`).join('') || '<p>No original record available.</p>';
  }
  function renderMethods() {
    if(!model)return;
    const events=model.searches.filter(e=>(!state.methodNbs||e.nbs_id===state.methodNbs)&&(!state.methodTable||e.tables.includes(state.methodTable)));
    $('methods-app').innerHTML=`<div class="dp-shell"><header class="dp-intro"><div class="dp-eyebrow">Methods · reproducible research</div><h2>6.3 Search protocols & counting method</h2><p>Each documented search records its scope, search terms and screening rules. Shared runs across tables appear once; original records remain available inside each protocol. Reported search hits may describe broad query matches or inspected returns. Counting bases differ and queries overlap: these are not unique papers or a screening backlog. Read each protocol’s limits alongside its counts.</p></header><div class="dp-filters"><label>Practice<select id="dp-method-nbs">${options(practices(),state.methodNbs,'All practices')}</select></label><label>Table<select id="dp-method-table">${options(['T4','T3','T6'].map(t=>[t,t]),state.methodTable,'All tables')}</select></label></div><p class="dp-note">${fmt(events.length)} search events. Prose, approximate or conflicting counts are retained as notes, never converted into exact totals.</p>${!state.methodNbs&&!state.methodTable?searchEffortTable():''}${events.map(e=>`<details class="dp-protocol"><summary><strong>${esc(label(e.nbs_id))}</strong> · ${esc(names[e.category]||label(e.category))} · ${esc(e.tables.join(' / '))}<span>${esc(e.search_date || 'Date not recorded')} · ${esc(e.suitability_family_id ? label(e.suitability_family_id.split('__').pop()) : 'Practice-wide')}</span></summary><dl>${['run_id','ruleset_version','search_terms','screening_steps','inclusion_criteria','limits'].map(k=>`<dt>${esc(label(k))}</dt><dd>${esc(e[k] || 'Not recorded')}</dd>`).join('')}<dt>Search records</dt><dd>${esc(e.search_ids.join(', '))}</dd><dt>Reported counts for this search</dt><dd>${['retrieved','screened','included'].map(k=>`${{retrieved:'Reported hits (context only)',screened:'Screening assessments',included:'Selections'}[k]}: ${fmt(e.counts[k])}`).join(' · ')}${e.counts_conflict ? ' · Conflicting counts excluded' : ''}${e.screening_variants > 1 ? ' · Table-specific screening protocols differ; screening totals not combined' : ''}${e.invalid_order ? ' · Invalid sequence excluded' : ''}</dd></dl><details><summary>Original protocol records</summary>${originalProtocols(e.raw_records)}</details></details>`).join('') || '<p>No search protocol recorded for this selection.</p>'}<details class="dp-definitions"><summary>Count definitions and limits</summary><dl>${Object.entries(model.definitions).map(([k,v])=>`<dt>${esc(label(k))}</dt><dd>${esc(v)}</dd>`).join('')}</dl></details></div>`;
    $('dp-method-nbs').onchange=e=>{state.methodNbs=e.target.value;renderMethods();$('dp-method-nbs').focus();};$('dp-method-table').onchange=e=>{state.methodTable=e.target.value;renderMethods();$('dp-method-table').focus();};
  }
  function renderBuild() {
    const b=data.build || {};
    $('dashboard-build').innerHTML=`<span>Dashboard <b>v${esc(b.release || 'unversioned')}</b> · UI ${esc(b.ui_id || '—')} · Data ${esc(b.data_id || '—')}</span><details><summary>Releases</summary><div><p>Counts v${esc(b.count_definition_version || '—')}. Earlier builds are in the project's change history for docs/dashboard_data.json.</p>${(data.dashboard_releases||[]).map(r=>`<p><b>v${esc(r.version)}</b> · ${esc(r.changes)}</p>`).join('')}</div></details>`;
  }
  function dispatch(e) {
    const b=e.target.closest('[data-action]');if(!b||!b.closest('.dp-shell,.dp-drawer'))return;
    const v=b.dataset.value, table=b.dataset.table||'T4';
    if(b.dataset.action.startsWith('pipeline-')){
      if(b.dataset.action==='pipeline-sort'){pipelineState.descending=pipelineState.sort===v?!pipelineState.descending:false;pipelineState.sort=v;pipelineState.page=0;}
      else if(b.dataset.action==='pipeline-page')pipelineState.page+=Number(v);
      else if(b.dataset.action==='pipeline-reset')Object.assign(pipelineState,{nbs:'',family:'',table:'',channel:'',page:0,sort:'updated',descending:true});
      else return;
      renderPipelineRecords();
      if(b.dataset.action==='pipeline-reset')$('dp-pipeline-nbs').focus();
      else if(b.dataset.action==='pipeline-sort')$('pipeline-records-app').querySelector(`[data-action="pipeline-sort"][data-value="${v}"]`)?.focus({preventScroll:true});
      else {$('pipeline-records-app').querySelector(`[data-action="pipeline-page"][data-value="${v}"]:not(:disabled)`)?.focus({preventScroll:true});$('pipeline-records-app').scrollIntoView({block:'start'});}
      return;
    }
    state.progressTable=table;
    switch(b.dataset.action){
      case 'overview-view':sectionState[table].view=v==='table'?'table':'chart';renderProgress();$(sectionId(table,'dp-'+sectionState[table].view+'-view-button')).focus({preventScroll:true});break;
      case 'chart-scale':sectionState[table].scale=v==='percent'?'percent':'counts';renderProgress();$(sectionId(table,'dp-chart-scale-'+sectionState[table].scale)).focus({preventScroll:true});break;
      case 'shared-progress':state.nbs='';renderProgress();$('dp-section-T2a').open=true;$('dp-section-T2a').scrollIntoView({block:'start'});break;
      case 'practice':state.nbs=v;state.family='';state.familyFilter='';state.reviewFilter='';renderProgress();document.querySelector('.dp-subtabs .is-active').focus({preventScroll:true});const destination=table==='T4'?document.querySelector('#progress-app .dp-intro'):$('dp-section-'+table);if(destination){if(table!=='T4')destination.open=true;destination.scrollIntoView({block:'start'});}break;
      case 'known':state.bibKeys=((progressModel().practices||[]).find(p=>p.nbs_id===v)?.metrics||progressModel().totals).source_keys||null;state.bibScopeLabel=progressTitle();state.bibFamily='';state.bibOrigin='';state.bibEvidence='';state.bibNbs=state.bibKeys?'':v||'';state.bibSet='known';state.bibTable='';state.bibType='';state.query='';state.page=0;renderBibliography();go('tab-stocktake');break;
      case 'project-bibliography':Object.assign(state,{bibKeys:null,bibScopeLabel:'',bibNbs:'',bibFamily:'',bibOrigin:'',bibEvidence:'',bibSet:'known',bibTable:'',bibType:'',query:'',page:0});renderBibliography();go('tab-stocktake');break;
      case 'bibliography':state.bibKeys=state.progressTable?((progressModel().practices||[]).find(p=>p.nbs_id===v)?.metrics||progressModel().totals).source_keys:null;state.bibScopeLabel=progressTitle();state.bibFamily='';state.bibOrigin='';state.bibEvidence='';state.bibNbs=state.bibKeys?'':v;state.bibSet='';state.bibTable='';state.bibType='';state.query='';state.page=0;renderBibliography();go('tab-stocktake');break;
      case 'methods':openMethods(v);break;
      case 'family-sort':state.familySortDesc=state.familySort===v?!state.familySortDesc:false;state.familySort=v;renderProgress();break;
      case 'scope-bibliography':{const [nbs,family]=JSON.parse(v);const m=(progressModel().practices||[]).find(p=>p.nbs_id===nbs)?.families.find(f=>f.family_id===family)?.metrics;Object.assign(state,{bibKeys:state.progressTable?(m?.source_keys||[]):null,bibScopeLabel:progressTitle(),bibNbs:state.progressTable?'':nbs,bibFamily:state.progressTable?'':family,bibOrigin:'',bibEvidence:'',bibSet:'known',bibTable:'',bibType:'',query:'',page:0});renderBibliography();go('tab-stocktake');break;}
      case 'output-sources':{const p=practiceRows().find(p=>p.nbs_id===state.nbs);const row=((p?p.outputs:model.outputs)||[]).find(r=>r.table_id===v);if(!row)break;Object.assign(state,{bibKeys:row.source_keys||[],bibScopeLabel:progressLabels[v]+' · used in outputs',bibNbs:'',bibFamily:'',bibOrigin:'',bibEvidence:'',bibSet:'known',bibTable:'',bibType:'',query:'',page:0});renderBibliography();go('tab-stocktake');break;}
      case 'source':openSource(v);break;
      case 'source-evidence':{const [id,table]=JSON.parse(v);openSource(id,table);break;}
      case 'bib-reset':Object.assign(state,{bibKeys:null,bibScopeLabel:'',bibNbs:'',bibFamily:'',bibType:'',bibOrigin:'',bibEvidence:'',bibSet:'',bibTable:'',query:'',page:0});renderBibliography();$('dp-bib-query').focus();break;
      case 'close':closeDrawer();break;
      case 'page':state.page+=Number(v);renderBibliography();$('bibliography-app').scrollIntoView({block:'start'});break;
    }
  }
  // Reveal a saved feedback target without changing evidence or reviewer decisions.
  function revealTarget(key) {
    if(!model || typeof key !== 'string')return false;
    if(key==='id:dp-ledger'||key.startsWith('ledger:')){
      if(key.startsWith('ledger:')){
        const row=(data.progress_ledger||[]).find(r=>pipelineKey(r)===key);
        if(!row)return false;
        Object.assign(pipelineState,{nbs:row.nbs_id||'',family:row.family||'__practice',table:row.table||'',channel:row.category||'',page:0});
      }
      go('tab-qaqc');
      if(window.DashboardShell?.openPipelineRecords)window.DashboardShell.openPipelineRecords();
      renderPipelineRecords();
      $('pipeline-records-app')?.scrollIntoView({block:'start'});
      return !!$('pipeline-records-app');
    }
    if(key.startsWith('source:')) {
      const id=key.slice(7);
      const source=bibliography.find(s=>s.key===id || s.source_id===id || (s.aliases||[]).includes(id));
      if(!source)return false;
      go('tab-stocktake');openSource(source.key);return true;
    }
    let savedTable='T4';
    if(key.startsWith('progress:')){const match=key.match(/^progress:(T2a|T3|T4|T6):(.+)$/);if(!match||!model.table_views?.[match[1]])return false;savedTable=match[1];key=match[2];}
    state.progressTable=savedTable;
    if(key.startsWith('output:')){const [,table,nbs='all']=key.split(':');if(!progressLabels[table])return false;state.nbs=nbs==='all'?'':nbs;if(state.nbs&&!practiceRows().some(p=>p.nbs_id===state.nbs))return false;go('tab-search');renderProgress();const section=$('dp-section-'+table);if(section)section.open=true;const row=$(sectionId(table,'dp-output-'+table));if(!row)return false;row.scrollIntoView({block:'center'});return true;}
    const family=key.startsWith('family:') ? key.slice(7) : '';
    if(key.startsWith('chart-practice:')){const nbs=key.slice(15);if(!practiceRows().some(p=>p.nbs_id===nbs))return false;sectionState[savedTable].view='chart';state.nbs='';go('tab-search');renderProgress();if(savedTable!=='T4')$('dp-section-'+savedTable).open=true;$(sectionId(savedTable,'dp-chart-practice-'+nbs)).scrollIntoView({block:'center'});return true;}
    const practice=key.startsWith('practice:') ? key.slice(9) : '';
    if(practice)sectionState[savedTable].view='table';
    const index=model.practices.findIndex(p=>family ? p.families.some(f=>f.family_id===family) : practice && p.nbs_id===practice);
    if(index<0)return false;
    const target=model.practices[index];
    if(target.nbs_id==='cross')return false;
    if(family && !visibleFamilies(target).some(f=>f.family_id===family))return false;
    state.nbs=family?target.nbs_id:'';state.family=family;state.familyFilter=family||'';state.reviewFilter='';renderProgress();go('tab-search');
    if(savedTable!=='T4')$('dp-section-'+savedTable).open=true;
    return true;
  }
  function openMethods(nbs) {state.methodNbs=nbs && nbs!=='all'?nbs:'';state.methodTable='';renderMethods();go('tab-methods');if(window.DashboardShell?.openMethods)window.DashboardShell.openMethods('search');}
  function printOverview() {
    const oldNbs=state.nbs, active=document.querySelector('.tab-btn.active'), oldTab=active&&active.dataset.tab;
    const oldMarkup=$('progress-app').innerHTML, oldFocus=document.activeElement;
    const oldScroll={x:window.scrollX,y:window.scrollY}, oldHash=location.hash;
    const drawer=$('dp-source-drawer');if(drawer)drawer.remove();
    state.nbs='';renderProgress();['T2a','T3','T6'].forEach(t=>{if($('dp-section-'+t))$('dp-section-'+t).open=true;});go('tab-search');document.body.classList.add('dp-print');
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
    go('tab-stocktake');openSource(id);
  }
  function refresh(next) {data=next;model=data.progress_overview;if(!model)return;evidence=new Map([...(data.registers.EV_evidence_register||[]),...(data._evDropped||[])].map(r=>[r.evidence_id,r]));makeBibliography();renderProgress();renderBibliography();renderMethods();renderPipelineRecords();renderBuild();}
  let initialized=false;
  window.DashboardProgress={
    init(next){refresh(next);if(!initialized){document.addEventListener('click',dispatch);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&$('dp-source-drawer'))closeDrawer();});window.addEventListener('hashchange',openHashSource);initialized=true;}openHashSource();},
    refresh,renderBibliography,renderPipelineRecords,openSource,openMethods,revealTarget,print:printOverview,
    pipelineContext:()=>({nbs:pipelineState.nbs||'all',family:pipelineState.family||'all',table:pipelineState.table||'all',channel:pipelineState.channel||'all'}),
    restoreMethodsContext:scope=>{state.methodNbs=typeof scope.nbs==='string'&&scope.nbs!=='all'?scope.nbs:'';state.methodTable=typeof scope.table==='string'&&scope.table!=='all'?scope.table:'';renderMethods();},
    restorePipelineContext:scope=>{['nbs','family','table','channel'].forEach(k=>{pipelineState[k]=typeof scope[k]==='string'&&scope[k]!=='all'?scope[k]:'';});pipelineState.page=0;renderPipelineRecords();},
    scope:()=>({nbs:state.nbs || 'all',family:state.familyFilter || 'all',table:state.progressTable||'all'}),
    context:tab=>tab==='tab-stocktake'?{nbs:state.bibNbs||'all',family:state.bibFamily||'all',source_type:state.bibType||'all',table:state.bibTable||'all',source:drawerSource,query:state.query}:tab==='tab-methods'?{nbs:state.methodNbs||'all',table:state.methodTable||'all'}:{nbs:state.nbs||'all',family:state.familyFilter||'all',table:state.progressTable||'all'},
    onTab(tab){if($('dp-source-drawer') && tab!==drawerTab)closeDrawer();},
  };
})();
