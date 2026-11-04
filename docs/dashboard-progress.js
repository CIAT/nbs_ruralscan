/* Progress, bibliography and methods are read-only projections of generated data. */
(function () {
  'use strict';
  let data, model, evidence = new Map(), bibliography = [], drawerReturn = null, drawerTab = '', drawerSource = '', registered = new Map();
  const state = { nbs: '', family: '', bibNbs: '', bibType: '', bibSet: '', bibTable: '', bibFamily: '', bibOrigin: '', bibEvidence: '', query: '', page: 0, methodNbs: '', methodTable: '', familyFilter: '', reviewFilter: '', ledgerTable: '', ledgerChannel: '', ledgerPage: 0, familySort: 'name', familySortDesc: false, ledgerSort: 'updated', ledgerSortDesc: true, overviewView: 'chart', chartScale: 'counts', progressTable: '', bibKeys: null, bibScopeLabel: '' };
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
  const feedbackKey = key => state.progressTable?'progress:'+state.progressTable+':'+key:key;
  function tableSelector() {
    return `<section class="dp-table-selector"><label for="dp-progress-table">Analytical purpose</label><select id="dp-progress-table">${options(Object.entries(progressLabels),state.progressTable,'All evidence · unique project totals')}</select><p class="dp-note" aria-live="polite">${esc(progressModel().scope_note || 'All recorded evidence, counted once. Table-specific views overlap; never add their totals.')}</p></section>`;
  }
  function analyticalOutputs(p) {
    const rows=(p?p.outputs:model.outputs)||[];
    if(!rows.length)return '';
    return `<section class="dp-outputs"><h3>${p?viewNumber()+'.4':'2.1.3'} Analytical outputs</h3><p class="dp-note">Compare outputs across all analytical purposes. The evidence selector above does not filter this comparison.</p><div class="dp-scroll"><table class="dp-table"><caption>Table ${p?viewNumber()+'.4':'2.1.2'}. What the evidence has produced${p?' · '+esc(practiceName(p)):''}</caption><thead><tr><th scope="col">Analytical purpose</th><th scope="col">Outputs recorded</th><th scope="col">With linked evidence</th><th scope="col">Sources used</th><th scope="col">Extracts used</th></tr></thead><tbody>${rows.map(r=>`<tr id="dp-output-${esc(r.table_id)}" data-feedback-key="${esc(feedbackKey('output:'+r.table_id+':'+(state.nbs||'all')))}"><th scope="row">${esc(progressLabels[r.table_id]||r.label)}</th><td>${fmt(r.output_count)} ${esc(r.unit)}</td><td>${fmt(r.evidence_backed_outputs)} of ${fmt(r.output_count)}</td><td>${r.source_keys?.length?button('output-sources',fmt(r.contributing_sources),r.table_id):fmt(r.contributing_sources)}</td><td>${fmt(r.contributing_excerpts)}</td></tr>`).join('')}</tbody></table></div><p class="dp-note">No grand total: output types differ and supporting sources and extracts can overlap.</p><details class="dp-output-detail"><summary>How to read these output counts</summary><p class="dp-note">Configured indicators and compiled assessments are different outputs. “With linked evidence” means at least one retained extract is cited, not that the output is approved. Assessment counts include practice roll-ups, families and context variants, not distinct hazards or benefits. T6 covers benefits; economics (T6E) is separate. Shared T2a configuration is reported at project level.</p></details>${rows.map(r=>`<details class="dp-output-detail"><summary>Inspect ${esc(r.table_id)} · ${fmt(r.output_count)} ${esc(r.unit)}</summary>${r.rows?.length?`<ul>${r.rows.map(row=>`<li><strong>${esc(row.label||row.id)}</strong>${row.nbs_id?' · '+esc(label(row.nbs_id)):''}${row.context_label?'<small>'+esc(row.context_label)+'</small>':''}<small>${fmt((row.evidence_ids||[]).length)} retained extracts linked</small>${(row.source_keys||[]).map(key=>button('source',(model.sources.find(s=>s.key===key)||{}).citation||key,key)).join(' ')}</li>`).join('')}</ul>`:'<p>No output records in this scope.</p>'}</details>`).join('')}</section>`;
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
    return `<section class="dp-orientation" aria-label="Purpose of progress reporting"><h3>2.1.1 What this progress report tells you</h3><p>The Rural NbS Scan turns published research and technical guidance into a method for identifying promising locations for nature-based solutions. This page shows how much evidence has been collected, assessed and translated into that method.</p><p>Use the chart or table to compare practices and identify review work still needed. <strong>A source</strong> is a publication, report or tool. <strong>An extract</strong> is one recorded claim from a source. <strong>An output</strong> is a climate-risk indicator, hazard-response assessment, suitability rule or benefit assessment. These are different units; they cannot be added together.</p><p>Review means a decision was recorded, including a request for clarification or exclusion. Approval means the extract is currently accepted. Compiled outputs may still rely on evidence awaiting approval; progress is not a claim that the method is ready for site-level design.</p></section>`;
  }
  function column(title, detail) { return `<th scope="col">${title}<small>${detail}</small></th>`; }
  function tableHead(byPractice = false, filters = false, p = null) {
    const sortable=(key,title,detail)=>`<th scope="col">${filters?button('family-sort',title+(state.familySort===key?(state.familySortDesc?' ↓':' ↑'):''),key,'dp-sort'):title}<small>${detail}</small>${filters&&key==='reviewed_excerpts'?`<label class="dp-column-filter">Review status<select id="dp-progress-review">${options([['pending','Not yet reviewed'],['unapproved','Unresolved review'],['empty','No extracts']],state.reviewFilter,'All records')}</select></label>`:''}</th>`;
    return `<thead><tr class="dp-stage-head"><th scope="col" rowspan="2">${byPractice?'Practice':'Suitability family'}${filters?`<label class="dp-column-filter">Filter family<select id="dp-progress-family">${familySelectOptions(p)}</select></label>`:''}</th><th scope="colgroup" colspan="1">Collect sources</th><th scope="colgroup" colspan="2">Extract evidence</th><th scope="colgroup" colspan="3">Review evidence</th><th scope="colgroup" colspan="1">Use evidence</th></tr><tr>${sortable('known_sources',state.progressTable?'Sources with tracked extracts':'Sources catalogued',state.progressTable?'Sources linked to this evidence scope':'Publications, reports and tools')}${sortable('extracted_sources','Sources with evidence','Sources with at least one non-excluded extract')}${sortable('all_excerpts','Extracts recorded','All saved claims, including excluded claims')}${sortable('reviewed_excerpts','Extracts reviewed','Count and % of all recorded extracts')}${sortable('approved_excerpts','Extracts approved','Count and % of reviewed extracts')}${sortable('dropped_excerpts','Extracts excluded','Saved for audit; not used in synthesis')}${sortable('contributing_excerpts','Extracts used in outputs','Distinct retained claims cited by selected outputs')}</tr></thead>`;
  }
  function cells(m) {
    return `<td><b>${fmt(m.known_sources)}</b>${mix(m)}</td><td>${fmt(m.extracted_sources)}</td><td>${fmt(m.all_excerpts)}</td><td title="${fmt(m.reviewed_excerpts)} reviewed out of ${fmt(m.all_excerpts)} recorded extracts">${fmt(m.reviewed_excerpts)} <span class="dp-percent">(${percent(m.reviewed_excerpts,m.all_excerpts)})</span></td><td title="${fmt(m.approved_excerpts)} approved out of ${fmt(m.reviewed_excerpts)} reviewed extracts">${fmt(m.approved_excerpts)} <span class="dp-percent">(${percent(m.approved_excerpts,m.reviewed_excerpts)})</span></td><td>${fmt(m.dropped_excerpts)}</td><td>${fmt(m.contributing_excerpts)}</td>`;
  }
  function visibleFamilies(p) { return p.families.filter(f => ((data.family_display_status || {})[f.family_id] || {}).status !== 'out_of_scope'); }
  function isEvidenceFamily(f) { return f.navigation_group==='evidence'||(f.scope_kind?f.scope_kind!=='family':f.family_id==='__unassigned'||f.family_id.endsWith('__cross_family')); }
  function namedFamilies(p) { return visibleFamilies(p).filter(f=>!isEvidenceFamily(f)); }
  function familySelectOptions(p) {return '<option value="">All families and evidence groups</option>'+[[false,'Practice families'],[true,'Shared or unassigned evidence']].map(([evidence,title])=>`<optgroup label="${title}">${visibleFamilies(p).filter(f=>isEvidenceFamily(f)===evidence).map(f=>`<option value="${esc(f.family_id)}"${state.familyFilter===f.family_id?' selected':''}>${esc(f.name)}</option>`).join('')}</optgroup>`).join('');}
  function selectedFamilies(p) {
    const rows=visibleFamilies(p).filter(f=>(!state.familyFilter||f.family_id===state.familyFilter)&&(!state.reviewFilter||(state.reviewFilter==='pending'?f.metrics.all_excerpts>f.metrics.reviewed_excerpts:state.reviewFilter==='unapproved'?f.metrics.reviewed_unresolved_excerpts>0:f.metrics.all_excerpts===0)));
    return rows.sort((a,b)=>{const k=state.familySort;const v=k==='name'?a.name.localeCompare(b.name):(a.metrics[k]||0)-(b.metrics[k]||0);return state.familySortDesc?-v:v;});
  }
  function familyRow(f) {
    const scope = (data.family_display_status || {})[f.family_id];
    return `<tr data-feedback-key="${esc(feedbackKey('family:'+f.family_id))}" data-feedback-label="${esc(f.name)}"><th scope="row"><details class="dp-family"><summary>${esc(f.name)}</summary>${scope ? `<p>${esc(scope.label)}. ${esc(scope.reason)}</p>` : ''}<ul>${f.subpractices.map(s => `<li>${isEvidenceFamily(f)||s.presentation_role==='evidence'?'Evidence routing tag':s.presentation_role==='umbrella'?'Umbrella category':'Variant'}: ${esc(s.name || label(s.subpractice_id))}</li>`).join('')}</ul><p class="dp-note">${f.subpractices.length ? 'Counts belong to this family; separate subpractice counts are not recorded.' : 'Evidence grouping; no subpractice breakdown recorded.'}</p></details>${scope ? `<small class="dp-scope-label">${esc(scope.label)}</small>` : ''}</th>${cells(f.metrics)}</tr>`;
  }
  function familyTable(p) {
    const chosen=selectedFamilies(p), other=chosen.filter(isEvidenceFamily);
    const named=chosen.filter(f=>!isEvidenceFamily(f));
    return `<div class="dp-scroll"><table class="dp-table dp-summary-table dp-family-table"><caption>Table ${viewNumber()}.1. ${esc(practiceName(p))}: evidence by named suitability family</caption>${tableHead(false,true,p)}<tbody>${named.map(familyRow).join('')||'<tr><td colspan="8">No families match the column filters.</td></tr>'}</tbody><tfoot><tr><th scope="row">Whole-practice total<br><small>Includes broader and unassigned scope records; not a sum of family rows.</small></th>${cells(p.metrics)}</tr></tfoot></table></div>${other.length?`<details class="dp-scope-notes" id="dp-scope-notes"><summary>${viewNumber()}.2 Shared or unassigned evidence</summary><p>These are scope records, not additional practices. Family totals overlap; do not add the rows. Evidence tagged as applying across all families does not establish that every claim applies to every family. Sources without a recorded family remain unassigned.</p><div class="dp-scroll"><table class="dp-table dp-summary-table dp-evidence-family-table"><caption>Table ${viewNumber()}.2. ${esc(practiceName(p))}: shared or unassigned evidence</caption>${tableHead()}<tbody>${other.map(familyRow).join('')}</tbody></table></div>${other.map(f=>`<p>${esc(f.name)}: ${esc(f.scope_definition||'No single named family is recorded; this is not evidence that the source applies to every family.')} ${button('scope-bibliography','Inspect these sources',JSON.stringify([p.nbs_id,f.family_id]))}</p>`).join('')}</details>`:''}`;
  }
  function chartParts(m) {
    return [
      ['approved','Approved',m.approved_excerpts||0],
      ['unresolved','Reviewed · unresolved',m.reviewed_unresolved_excerpts||0],
      ['excluded','Reviewed · excluded',m.reviewed_dropped_excerpts||0],
      ['unreviewed','No assessment recorded',m.unreviewed_excerpts||0]
    ];
  }
  function reviewChart() {
    const rows=progressRows(), max=Math.max(1,...rows.map(p=>p.metrics.all_excerpts||0));
    const percentScale=state.chartScale==='percent', total=progressModel().totals;
    const counts=m=>chartParts(m).map(([key,name,n])=>`<span><i class="dp-chart-key dp-chart-${key}" aria-hidden="true"></i>${fmt(n)} ${esc(name.toLowerCase())}</span>`).join('');
    return `<figure class="dp-review-chart" aria-labelledby="dp-chart-caption"><figcaption id="dp-chart-caption"><strong>Figure 2.1.1. Evidence collected and review progress · ${esc(progressTitle())}</strong><p>Compare the amount of evidence recorded, then see how much has a recorded assessment. Switch to percentages to compare review coverage. Each extract appears in one colour only.</p></figcaption><div class="dp-chart-tools"><div class="dp-view-switch" role="group" aria-label="Chart scale"><button id="dp-chart-scale-counts" class="dp-button" data-action="chart-scale" data-value="counts" aria-pressed="${!percentScale}">Number of extracts</button><button id="dp-chart-scale-percent" class="dp-button" data-action="chart-scale" data-value="percent" aria-pressed="${percentScale}">% of recorded extracts</button></div><p class="dp-note">${percentScale?'Every full bar = 100% of that practice’s recorded extracts.':'All practice bars share one count scale: 0–'+fmt(max)+' recorded extracts.'}</p></div><div class="dp-chart-legend">${chartParts({}).map(([key,name])=>`<span><i class="dp-chart-key dp-chart-${key}" aria-hidden="true"></i>${esc(name)}</span>`).join('')}</div><div class="dp-chart-axis" aria-hidden="true"><span>0${percentScale?'%':''}</span><span>${percentScale?'50%':fmt(Math.round(max/2))}</span><span>${percentScale?'100%':fmt(max)}</span></div>${rows.map(p=>{
      const m=p.metrics, n=m.all_excerpts||0, parts=chartParts(m), width=percentScale?(n?100:0):100*n/max;
      const description=practiceName(p)+': '+fmt(n)+' recorded extracts. '+parts.map(([,name,value])=>name+': '+fmt(value)).join('; ')+'. '+percent(m.reviewed_excerpts,n)+' reviewed; '+percent(m.approved_excerpts,m.reviewed_excerpts)+' of reviewed extracts approved.';
      return `<section class="dp-chart-row" id="dp-chart-practice-${esc(p.nbs_id)}" data-feedback-key="${esc(feedbackKey('chart-practice:'+p.nbs_id))}"><div class="dp-chart-row-head">${p.nbs_id==='shared'?'<strong>'+esc(practiceName(p))+'</strong>':button('practice',practiceName(p),p.nbs_id,'dp-expand')}<strong>${fmt(n)} extracts</strong></div><p class="dp-chart-context">${fmt(m.known_sources)} sources in scope · ${fmt(m.extracted_sources)} sources with retained evidence · ${fmt(m.contributing_excerpts)} extracts used in outputs</p><div class="dp-chart-track" role="img" aria-label="${esc(description)}"><div class="dp-chart-bar" style="width:${width}%">${parts.map(([key,name,value])=>value?`<span class="dp-chart-${key}" style="width:${100*value/n}%" title="${esc(name)}: ${fmt(value)} (${percent(value,n)} of recorded extracts)"></span>`:'').join('')}</div></div><div class="dp-chart-counts">${counts(m)}</div><p class="dp-chart-rates"><b>${percent(m.reviewed_excerpts,n)} reviewed</b> · ${percent(m.approved_excerpts,m.reviewed_excerpts)} of reviewed extracts approved${n?'':' · No extracts recorded'}</p></section>`;
    }).join('')}<section class="dp-chart-total"><h4>Deduplicated total · ${esc(progressTitle())}</h4><p><strong>${fmt(total.all_excerpts)} extracts recorded</strong> · ${fmt(total.reviewed_excerpts)} reviewed (${percent(total.reviewed_excerpts,total.all_excerpts)}) · ${fmt(total.approved_excerpts)} approved (${percent(total.approved_excerpts,total.reviewed_excerpts)} of reviewed)</p><div class="dp-chart-counts">${counts(total)}</div><p class="dp-note">Practice rows can overlap; this total counts each extract once. Sources and outputs use different units; output coverage is reported separately below.</p></section><p class="dp-note">“Reviewed” includes recorded automated and team assessments; it does not certify human review. “Reviewed · excluded” counts only exclusions with an assessment record. Excluded claims without one remain in “No assessment recorded”. Approval percentages beside bars use reviewed extracts; coloured widths always use recorded extracts.</p></figure>`;
  }
  function overviewTable() {
    if(progressModel().project_level && !progressModel().totals.all_excerpts)return `<section><h3>2.1.2 Evidence progress · ${esc(progressTitle())}</h3><div class="dp-orientation"><h4>Shared climate-risk configuration</h4><p>Source collection, extraction and review progress: <strong>not recorded as linked evidence</strong>.</p><p>The configuration has narrative references, but no linked extracts are recorded in this view. This does not mean no research was done. Inspect configured indicators and evidence-link coverage below.</p></div></section>`;
    const general=progressModel().practices.find(p=>p.nbs_id==='cross');
    return `<div class="dp-section-head" id="dp-progress-views"><h3>2.1.2 Evidence progress · ${esc(progressTitle())}</h3><div class="dp-view-switch" role="group" aria-label="Progress presentation"><button id="dp-chart-view-button" class="dp-button" data-action="overview-view" data-value="chart" aria-controls="dp-chart-view" aria-pressed="${state.overviewView==='chart'}">Chart</button><button id="dp-table-view-button" class="dp-button" data-action="overview-view" data-value="table" aria-controls="dp-table-view" aria-pressed="${state.overviewView==='table'}">Table</button></div></div><div id="dp-chart-view"${state.overviewView==='chart'?'':' hidden'}>${reviewChart()}</div><div id="dp-table-view"${state.overviewView==='table'?'':' hidden'}>${legend()}<div class="dp-scroll"><table class="dp-table dp-summary-table"><caption>Table 2.1.1. Sources, evidence review and use in outputs · ${esc(progressTitle())}</caption>${tableHead(true)}<tbody>${progressRows().map(p=>`<tr class="dp-practice-row" data-feedback-key="${esc(feedbackKey('practice:'+p.nbs_id))}" data-feedback-label="${esc(practiceName(p))}"><th scope="row">${p.nbs_id==='shared'?'<strong>'+esc(practiceName(p))+'</strong>':button('practice',practiceName(p),p.nbs_id,'dp-expand')}<details class="dp-practice-children"><summary>View subpractices</summary><ul>${[...new Set(namedFamilies(p).flatMap(f=>f.subpractices.map(x=>x.name||label(x.subpractice_id))))].map(n=>`<li>${esc(n)}</li>`).join('')||'<li>No subpractices recorded</li>'}</ul></details></th>${cells(p.metrics)}</tr>`).join('')}</tbody><tfoot><tr><th scope="row">Deduplicated scope total</th>${cells(progressModel().totals)}</tr></tfoot></table></div></div><p class="dp-note">Scope totals count each source and extract once. Practice rows can overlap.${general?` Totals include ${fmt(general.metrics.known_sources)} general reference sources that are not a separate practice.`:''} Review percentages use all recorded extracts; approval percentages use reviewed extracts. Review logs include team and automated decisions; these counts do not claim that a human checked every extract.</p><p class="dp-note">Search activity is documented in Methods. Its screening counts may repeat a paper across searches, so they are not directly comparable with bibliography source counts. ${button('methods','Inspect search activity')}</p>`;
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
    return `<details class="dp-definitions"><summary>${viewNumber()}.${p?'5':'4'} Count definitions · ${p?esc(practiceName(p)):'whole project'}</summary><dl><dt>Sources catalogued</dt><dd>${fmt(m.known_sources)} source records in this scope: ${fmt(n)} registered + ${fmt(sources.length-n)} queue-only records. Explicit duplicate links are merged. Stocktake entries without a source ID are excluded. ${button('known','Inspect sources in this scope',p?p.nbs_id:'')}</dd><dt>Extracts recorded</dt><dd>Every saved evidence claim in this scope, including excluded claims. Excluded claims remain auditable but do not contribute to synthesis.</dd><dt>Reviewed versus approved</dt><dd>Reviewed = at least one recorded assessment (keep, exclude, query or reclassify), or an explicit approval in the register. Repeated decisions on one extract count once. Automatic flags alone do not count. Reviewed % = reviewed / all recorded. Approved = currently accepted, non-excluded claims. Approved % = approved / reviewed. A review can remain unresolved. Logged assessments include automated and team decisions.</dd><dt>Source types</dt><dd>Literature, grey literature and tools follow source metadata. “Type not recorded” means missing or conflicting classification. Stocktake describes discovery origin, not publication type.</dd><dt>Family scope</dt><dd>Named suitability families describe shared constraints. Practice-level evidence tags and sources without a family are shown separately. Neither is automatically assigned to a narrower family. Sources can support multiple families, so their counts overlap.</dd><dt>Extracts used in outputs</dt><dd>Distinct retained claims cited by the selected analytical outputs. The all-evidence view deduplicates across T2a, T3, T4 and T6. An extract may support more than one output or table. Compilation does not certify approval.</dd></dl></details>`;
  }
  function ledgerRows(p) {
    const hidden = new Set(p.families.filter(f=>!visibleFamilies(p).includes(f)).map(f=>f.family_id));
    return (data.progress_ledger || []).filter(r => r.nbs_id===p.nbs_id && !hidden.has(r.family) && (!state.familyFilter || (state.familyFilter==='__unassigned' ? !r.family : r.family===state.familyFilter)) && (!state.ledgerTable || r.table===state.ledgerTable) && (!state.ledgerChannel || r.category===state.ledgerChannel)).sort((a,b)=>{const result=String(a[state.ledgerSort]||'').localeCompare(String(b[state.ledgerSort]||''));return state.ledgerSortDesc?-result:result;});
  }
  function ledger(p) {
    const rows=ledgerRows(p),size=20;state.ledgerPage=Math.max(0,Math.min(state.ledgerPage,Math.ceil(rows.length/size)-1));
    const sort=(key,title)=>button('ledger-sort',title+(state.ledgerSort===key?(state.ledgerSortDesc?' ↓':' ↑'):''),key,'dp-sort');
    const stage=v=>({done:'Complete',in_progress:'In progress · % not recorded',not_started:'Not started',blocked:'Blocked',deferred:'Deferred'}[v]||(v?label(v):'Not recorded'));
    return `<details class="dp-stage-summary" id="dp-ledger"><summary>${viewNumber()}.3 Pipeline step records</summary><p class="dp-note">This log records whether a search or extraction step was marked complete. It does not count individual claims checked. A blank verification entry does not establish that no checks occurred. The log has no completion denominator: an “in progress” percentage cannot be calculated. Use Table ${viewNumber()}.1 for recorded review counts.</p><p class="dp-results">${fmt(rows.length)} records · ${rows.length?state.ledgerPage*size+1:0}–${Math.min(rows.length,(state.ledgerPage+1)*size)} shown</p><div class="dp-scroll"><table class="dp-table dp-monitor-table"><caption>Table ${viewNumber()}.3. ${esc(practiceName(p))}: recorded pipeline stages</caption><thead><tr><th scope="col">${sort('family','Family / scope')}</th><th scope="col">${sort('table','Analytical table')}<label class="dp-column-filter">Filter table<select id="dp-ledger-table">${options(['T4','T3','T6'].map(t=>[t,t]),state.ledgerTable,'All tables')}</select></label></th><th scope="col">${sort('category','Discovery channel')}<label class="dp-column-filter">Filter channel<select id="dp-ledger-channel">${options(['stock','updated_lit','grey','tool'].map(k=>[k,names[k]]),state.ledgerChannel,'All channels')}</select></label></th><th scope="col">${sort('searched','Search stage')}</th><th scope="col">${sort('screened','Screening stage')}</th><th scope="col">${sort('verified','Verification stage')}</th><th scope="col">${sort('updated','Updated')}</th></tr></thead><tbody>${rows.slice(state.ledgerPage*size,(state.ledgerPage+1)*size).map(r=>`<tr><td title="${esc(r.note)}">${esc(r.family?familyLabel(r.family):'Whole-practice search')}</td><td>${esc(r.table)}</td><td>${esc(names[r.category]||label(r.category))}</td>${['searched','screened','verified'].map(k=>`<td><span class="dp-stage ${r[k]==='done'?'dp-stage-done':''}">${esc(stage(r[k]))}</span></td>`).join('')}<td>${esc(r.updated||'—')}</td></tr>`).join('')||'<tr><td colspan="7">No pipeline records match these column filters.</td></tr>'}</tbody></table></div><div class="dp-pagination">${button('ledger-page','Previous',-1)}<span>Page ${state.ledgerPage+1} / ${Math.max(1,Math.ceil(rows.length/size))}</span>${button('ledger-page','Next',1)}</div></details>`;
  }
  function practiceView(p) {
    return `<h3>${viewNumber()}.1 Evidence by suitability family</h3><p class="dp-note">Families group subpractices with shared suitability constraints. Compare extracted, reviewed and approved evidence here; filter and sort using the column headings. The whole-practice total includes broader or unassigned records explained below, and may differ from the sum of family rows.</p>${legend()}${familyTable(p)}${ledger(p)}`;
  }
  function bindProgressFilters() {
    [['dp-progress-family','familyFilter'],['dp-progress-review','reviewFilter'],['dp-ledger-table','ledgerTable'],['dp-ledger-channel','ledgerChannel']].forEach(([id,key])=>{
      const node=$(id);if(!node)return;
      node.onchange=e=>{const open=$('dp-ledger') && $('dp-ledger').open;state[key]=e.target.value;state.ledgerPage=0;renderProgress();if(open && $('dp-ledger'))$('dp-ledger').open=true;$(id).focus();};
    });
  }
  function renderProgress() {
    const p=(progressModel().practices||[]).find(p=>p.nbs_id===state.nbs) || practiceRows().find(p=>p.nbs_id===state.nbs);
    $('progress-app').innerHTML=`<div class="dp-shell"><nav class="dp-subtabs shell-subnav" aria-label="Progress views">${button('practice','2.1 Overview','',!p?'is-active':'')}${practiceRows().map((p,i)=>button('practice',`2.${i+2} ${practiceName(p)}`,p.nbs_id,state.nbs===p.nbs_id?'is-active':'')).join('')}</nav><header class="dp-intro"><div class="dp-eyebrow">Rural NbS Scan · ${p?'Practice progress':'Project progress'}</div><h2>${viewNumber()} ${p?esc(practiceName(p)):'Progress overview'}</h2><p>${p?'Inspect evidence collection, recorded review decisions and current approvals for this practice.':'Research effort behind the landscape scoping methodology, from discovery to traceable evidence.'}</p><div class="dp-actions">${button('bibliography','Explore bibliography',state.nbs)}${button('methods','Read methods',state.nbs)}</div></header>${p?'':flow()}${tableSelector()}${p?(progressModel().project_level?'<p class="dp-note">T2a is shared across the project; practice-level allocations are not recorded.</p>'+button('practice','View shared climate-risk progress',''):practiceView(p)+analyticalOutputs(practiceRows().find(row=>row.nbs_id===state.nbs))):overviewTable()+analyticalOutputs()}${p&&progressModel().project_level?'':countNotes(p)}</div>`;
    bindProgressFilters();
    $('dp-progress-table').onchange=e=>{state.progressTable=e.target.value;if(progressModel().project_level)state.nbs='';state.familyFilter='';state.reviewFilter='';state.familySort='name';renderProgress();$('dp-progress-table').focus({preventScroll:true});};
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
    $('methods-app').innerHTML=`<div class="dp-shell"><header class="dp-intro"><div class="dp-eyebrow">Methods · reproducible research</div><h2>Search protocols & counting method</h2><p>Each documented search records its scope, search terms and screening rules. Shared runs across tables appear once; original records remain available inside each protocol. Reported search hits may describe broad query matches or inspected returns. Counting bases differ and queries overlap: these are not unique papers or a screening backlog. Read each protocol’s limits alongside its counts.</p></header><div class="dp-filters"><label>Practice<select id="dp-method-nbs">${options(practices(),state.methodNbs,'All practices')}</select></label><label>Table<select id="dp-method-table">${options(['T4','T3','T6'].map(t=>[t,t]),state.methodTable,'All tables')}</select></label></div><p class="dp-note">${fmt(events.length)} search events. Prose, approximate or conflicting counts are retained as notes, never converted into exact totals.</p>${!state.methodNbs&&!state.methodTable?searchEffortTable():''}${events.map(e=>`<details class="dp-protocol"><summary><strong>${esc(label(e.nbs_id))}</strong> · ${esc(names[e.category]||label(e.category))} · ${esc(e.tables.join(' / '))}<span>${esc(e.search_date || 'Date not recorded')} · ${esc(e.suitability_family_id ? label(e.suitability_family_id.split('__').pop()) : 'Practice-wide')}</span></summary><dl>${['run_id','ruleset_version','search_terms','screening_steps','inclusion_criteria','limits'].map(k=>`<dt>${esc(label(k))}</dt><dd>${esc(e[k] || 'Not recorded')}</dd>`).join('')}<dt>Search records</dt><dd>${esc(e.search_ids.join(', '))}</dd><dt>Reported counts for this search</dt><dd>${['retrieved','screened','included'].map(k=>`${{retrieved:'Reported hits (context only)',screened:'Screening assessments',included:'Selections'}[k]}: ${fmt(e.counts[k])}`).join(' · ')}${e.counts_conflict ? ' · Conflicting counts excluded' : ''}${e.screening_variants > 1 ? ' · Table-specific screening protocols differ; screening totals not combined' : ''}${e.invalid_order ? ' · Invalid sequence excluded' : ''}</dd></dl><details><summary>Original protocol records</summary>${originalProtocols(e.raw_records)}</details></details>`).join('') || '<p>No search protocol recorded for this selection.</p>'}<details class="dp-definitions"><summary>Count definitions and limits</summary><dl>${Object.entries(model.definitions).map(([k,v])=>`<dt>${esc(label(k))}</dt><dd>${esc(v)}</dd>`).join('')}</dl></details></div>`;
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
      case 'overview-view':state.overviewView=v==='table'?'table':'chart';renderProgress();$('dp-'+state.overviewView+'-view-button').focus({preventScroll:true});break;
      case 'chart-scale':state.chartScale=v==='percent'?'percent':'counts';renderProgress();$('dp-chart-scale-'+state.chartScale).focus({preventScroll:true});break;
      case 'practice':state.nbs=v;state.family='';state.familyFilter='';state.reviewFilter='';state.ledgerTable='';state.ledgerChannel='';state.ledgerPage=0;renderProgress();document.querySelector('.dp-subtabs .is-active').focus({preventScroll:true});const intro=document.querySelector('#progress-app .dp-intro');if(intro)intro.scrollIntoView({block:'start'});break;
      case 'ledger-sort':state.ledgerSortDesc=state.ledgerSort===v?!state.ledgerSortDesc:false;state.ledgerSort=v;state.ledgerPage=0;renderProgress();$('dp-ledger').open=true;break;
      case 'ledger-page':state.ledgerPage+=Number(v);renderProgress();$('dp-ledger').open=true;$('dp-ledger').scrollIntoView({block:'start'});break;
      case 'known':state.bibKeys=((progressModel().practices||[]).find(p=>p.nbs_id===v)?.metrics||progressModel().totals).source_keys||null;state.bibScopeLabel=progressTitle();state.bibFamily='';state.bibOrigin='';state.bibEvidence='';state.bibNbs=state.bibKeys?'':v||'';state.bibSet='known';state.bibTable='';state.bibType='';state.query='';state.page=0;renderBibliography();go('tab-stocktake');break;
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
    if(key.startsWith('source:')) {
      const id=key.slice(7);
      const source=bibliography.find(s=>s.key===id || s.source_id===id || (s.aliases||[]).includes(id));
      if(!source)return false;
      go('tab-stocktake');openSource(source.key);return true;
    }
    let savedTable='';
    if(key.startsWith('progress:')){const match=key.match(/^progress:(T2a|T3|T4|T6):(.+)$/);if(!match||!model.table_views?.[match[1]])return false;savedTable=match[1];key=match[2];}
    state.progressTable=savedTable;
    if(key.startsWith('output:')){const [,table,nbs='all']=key.split(':');if(!progressLabels[table])return false;state.nbs=nbs==='all'?'':nbs;if(state.nbs&&!practiceRows().some(p=>p.nbs_id===state.nbs))return false;go('tab-search');renderProgress();const row=$('dp-output-'+table);if(!row)return false;row.scrollIntoView({block:'center'});return true;}
    const family=key.startsWith('family:') ? key.slice(7) : '';
    if(key.startsWith('chart-practice:')){const nbs=key.slice(15);if(!practiceRows().some(p=>p.nbs_id===nbs))return false;state.overviewView='chart';state.nbs='';go('tab-search');renderProgress();$('dp-chart-practice-'+nbs).scrollIntoView({block:'center'});return true;}
    const practice=key.startsWith('practice:') ? key.slice(9) : '';
    if(practice)state.overviewView='table';
    const index=model.practices.findIndex(p=>family ? p.families.some(f=>f.family_id===family) : practice && p.nbs_id===practice);
    if(index<0)return false;
    const target=model.practices[index];
    if(target.nbs_id==='cross')return false;
    if(family && !visibleFamilies(target).some(f=>f.family_id===family))return false;
    const named=family&&namedFamilies(target).some(f=>f.family_id===family);
    state.nbs=family?target.nbs_id:'';state.family=family;state.familyFilter=family||'';state.reviewFilter='';state.ledgerPage=0;renderProgress();go('tab-search');
    if(family&&!named&&$('dp-scope-notes'))$('dp-scope-notes').open=true;
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
    $('dp-progress-table').onchange=e=>{state.progressTable=e.target.value;if(progressModel().project_level)state.nbs='';state.familyFilter='';state.reviewFilter='';state.familySort='name';renderProgress();$('dp-progress-table').focus({preventScroll:true});};
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
  function refresh(next) {data=next;model=data.progress_overview;if(!model)return;evidence=new Map([...(data.registers.EV_evidence_register||[]),...(data._evDropped||[])].map(r=>[r.evidence_id,r]));makeBibliography();renderProgress();renderBibliography();renderMethods();renderBuild();}
  let initialized=false;
  window.DashboardProgress={
    init(next){refresh(next);if(!initialized){document.addEventListener('click',dispatch);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&$('dp-source-drawer'))closeDrawer();});window.addEventListener('hashchange',openHashSource);initialized=true;}openHashSource();},
    refresh,renderBibliography,openSource,openMethods,revealTarget,print:printOverview,
    scope:()=>({nbs:state.nbs || 'all',family:state.familyFilter || 'all',table:state.progressTable||'all'}),
    context:tab=>tab==='tab-stocktake'?{nbs:state.bibNbs||'all',family:state.bibFamily||'all',source_type:state.bibType||'all',table:state.bibTable||'all',source:drawerSource,query:state.query}:tab==='tab-methods'?{nbs:state.methodNbs||'all',table:state.methodTable||'all'}:{nbs:state.nbs||'all',family:state.familyFilter||'all',table:state.progressTable||'all'},
    onTab(tab){if($('dp-source-drawer') && tab!==drawerTab)closeDrawer();},
  };
})();
