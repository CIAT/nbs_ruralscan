/* Live T4 relationships: presentation only; no decisions or analytical defaults. */
(function () {
  'use strict';
  let data={}, payload={}, root, bound=false;
  const state={practice:'agroforestry',variable:'',query:'',family:'',scope:'practice_technology',review:'',limit:25};
  const $=id=>document.getElementById(id);
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const nice=value=>String(value||'Unassigned').split('__').pop()==='cross_family'?'Broad family scope; applicability unconfirmed':String(value||'Unassigned').split('__').pop().replace(/_/g,' ');
  const obj=value=>typeof value==='string'?JSON.parse(value||'{}'):(value||{});
  const approved=row=>String(row.reviewer_ok).toLowerCase()==='true';
  const entry=()=>payload.practices?.[state.practice]||{};
  const records=()=>entry().catalogue?.records||[];
  const options=(values,current,all)=>`${all?`<option value="">${esc(all)}</option>`:''}${values.map(([key,label])=>`<option value="${esc(key)}"${key===current?' selected':''}>${esc(label)}</option>`).join('')}`;
  const select=(id,label,values,current,all)=>`<label>${label}<select id="${id}">${options(values,current,all)}</select></label>`;
  const list=values=>[...new Set(values.filter(Boolean))].sort().map(v=>[v,nice(v)]);
  const source=id=>`<button type="button" class="dr-link" data-dr-source="${esc(id)}">${esc(id)}</button>`;
  function use(value) {return value&&value.N?`<strong>${value.n} of ${value.N} studies</strong><small>${value.percent}% of recorded model-use cohort</small>`:'Not documented';}
  function selectedClaims() {
    const q=state.query.toLowerCase();
    return records().filter(r=>(!state.variable||r.variable===state.variable)&&(!state.family||r.suitability_family_id===state.family)&&(!state.scope||r.claim_scope===state.scope)&&(!state.review||(state.review==='approved')===approved(r))&&(!q||[r.variable,r.source_id,r.quote,r.evidence_id,r.source_direction].join(' ').toLowerCase().includes(q)));
  }
  function aggregateRows() {
    const rows=entry().aggregate?.rows||[], q=state.query.toLowerCase();
    return rows.filter(r=>(!state.variable||r.variable===state.variable)&&(!q||[r.variable,r.group,...r.claim_sources].join(' ').toLowerCase().includes(q)));
  }
  function weights(row) {
    if(!row.weight_summary.length)return 'No reconstructed weight model';
    return row.weight_summary.map(w=>`<p><strong>${w.median_relative_to_equal.toFixed(2)}× equal-share benchmark</strong><small>${esc(nice(w.scope))} · ${w.reporting_sources} reporting sources</small><small>Range ${w.relative_range.map(v=>v.toFixed(2)).join('–')}×; median whole-model share ${(100*w.median_source_share).toFixed(1)}%</small></p>`).join('')+`<details><summary>Original study weights</summary>${row.study_weights.map(w=>`<p>${source(w.source_id)} · ${esc(w.model_id)}<br>${(w.share*100).toFixed(2)}% whole-model share; ${w.relative_to_equal.toFixed(2)}×<small>${esc(nice(w.scope))}</small><pre>${esc(JSON.stringify({original_weights:w.native_weight_paths,provenance:w.provenance},null,2))}</pre></p>`).join('')}</details>`;
  }
  function aggregateTable() {
    const e=entry();
    if(!e.aggregate)return `<div class="dr-notice"><p>${esc(e.aggregate_note||'No aggregate is available for this practice.')}</p>${e.rebuild_detail?`<details><summary>Why aggregation is unavailable</summary><p>${esc(e.rebuild_detail)}</p></details>`:''}</div>`;
    const rows=aggregateRows();
    return `<p class="dr-note">${rows.length} variables. Practice-wide, general-practice evidence. Family, scope and approval filters below apply to source claims only. Study use includes unreviewed records; missing use means unknown.</p><div class="dr-table-scroll"><table class="dr-table"><caption>Table 3.1.1. Variable use, source importance and relationship support</caption><thead><tr><th>Variable / group</th><th>Group used in studies</th><th>Variable used in studies</th><th>Reported importance</th><th>Direction reported by sources</th><th>Sources supporting numeric functions</th></tr></thead><tbody>${rows.map(r=>`<tr><th scope="row"><button type="button" class="dr-link" data-dr-variable="${esc(r.variable)}">${esc(nice(r.variable))}</button><small>${esc(nice(r.group))}</small></th><td>${use(r.group_use)}${r.mapped_group_weights.length?`<details><summary>Mapped group shares</summary>${r.mapped_group_weights.map(w=>`<p>${esc(w.model_id)}: ${(w.share*100).toFixed(1)}%${w.unmapped_model_variables.length?' (partial)':''}<small>${esc(nice(w.scope))}</small></p>`).join('')}<small>Sum of mapped variables only; not the study’s declared group weight.</small></details>`:''}</td><td>${use(r.variable_use)}</td><td>${weights(r)}</td><td>${r.direction_by_family.map(d=>`<p><strong>${esc(nice(d.direction))}</strong><small>${esc(nice(d.family))} · ${d.sources.length} sources</small>${d.sources.map(source).join(', ')}</p>`).join('')||'No explicit direction encoded'}</td><td>${r.function_support.filter(f=>f.sources.length).map(f=>`<p><strong>${f.sources.length} sources</strong><small>${esc(nice(f.family))}</small><button class="dr-link" type="button" data-dr-rule="${esc(f.mapping_id)}">View numeric function</button></p>`).join('')||'No supported numeric function compiled'}<button class="dr-link" type="button" data-dr-variable="${esc(r.variable)}">Inspect ${r.evidence_ids.length} source claims</button></td></tr>`).join('')||'<tr><td colspan="6">No variables match this search.</td></tr>'}</tbody></table></div>`;
  }
  function relationshipKind(r) {
    if(r.linked_mapping_ids.length)return 'Linked to a compiled rule';
    if(r.has_source_classes)return 'Reported classes / gate; no compiled link';
    if(r.has_stated_direction||r.source_shape)return 'Reported direction / shape; no compiled link';
    return 'Qualitative or selection evidence; no compiled link';
  }
  function claimCard(r) {
    return `<article tabindex="-1" class="dr-claim" id="dr-claim-${esc(r.evidence_id)}"><h4>${esc(nice(r.variable))} · ${source(r.source_id)}</h4><p>${esc(nice(r.suitability_family_id))} · ${esc(nice(r.claim_scope))}</p><div class="dr-status"><span>${esc(relationshipKind(r))}</span><span>${approved(r)?'Approval recorded':'Approval not recorded'}</span></div><p>Direction: <strong>${esc(nice(r.source_direction||'not_encoded'))}</strong> · Shape: ${esc(nice(r.source_shape||'not_encoded'))}</p><blockquote>${esc(r.quote||'Quote not recorded')}</blockquote><p class="dr-note">${esc(r.citation||r.source_id)} · Page ${esc(r.page||'not recorded')}${r.locator?` · ${esc(r.locator_type)}: ${esc(r.locator)}`:''}</p><details><summary>Reported relationship, context and full evidence record</summary><dl><dt>Evidence ID</dt><dd>${esc(r.evidence_id)}</dd><dt>Compiler assessment</dt><dd>${esc(nice(r.compilation_disposition==='not_accounted'?'not_available':r.compilation_disposition))}</dd><dt>Reported relationship</dt><dd><pre>${esc(JSON.stringify(obj(r.relationship),null,2))}</pre></dd><dt>Context</dt><dd><pre>${esc(JSON.stringify(obj(r.context),null,2))}</pre></dd>${r.justification_quote?`<dt>Supporting quote · page ${esc(r.justification_page)}</dt><dd>${esc(r.justification_quote)}</dd>`:''}${r.lineage_of?`<dt>Source lineage</dt><dd>${esc(r.lineage_of)}</dd>`:''}</dl></details>${r.linked_mapping_ids.map(id=>`<button class="dr-link" type="button" data-dr-rule="${esc(id)}">Inspect rule ${esc(id)}</button>`).join(' ')}</article>`;
  }
  function renderResults() {
    $('dr-rule-detail').innerHTML='';
    $('dr-aggregate').innerHTML=aggregateTable();
    const rows=selectedClaims();
    $('dr-count').textContent=`${rows.length.toLocaleString()} source claims match · ${rows.filter(approved).length.toLocaleString()} with approval recorded. Claims are not independent studies.`;
    $('dr-claims').innerHTML=rows.slice(0,state.limit).map(claimCard).join('')||'<p>No source claims match. Clear filters to widen this view.</p>';
    $('dr-more').hidden=rows.length<=state.limit;
  }
  function render() {
    if(!root)return;
    root.innerHTML=`<div class="dr-shell"><h2>3.1 Relationships across sources</h2><p>See which variables studies use, what relationships sources report, and which evidence supports compiled suitability functions. Select a variable to inspect its source claims below.</p><div class="dr-filters">${select('dr-practice','Practice',list(Object.keys(payload.practices||{})),state.practice)}${select('dr-variable','Variable',list(records().map(r=>r.variable)),state.variable,'All variables')}<label>Find variable, source or claim<input type="search" id="dr-search" value="${esc(state.query)}" placeholder="Search relationships"></label><button type="button" id="dr-reset">Clear filters</button></div><details class="dr-method"><summary>3.1.1 How to read study use, weights and functions</summary><p>Study-use counts include only papers with explicitly verified model-use records. Their denominator is that recorded cohort, not every paper in the library. Missing use is unknown. A paper counts once within each group or variable.</p><p>Importance describes reconstructed source-model weights: 1× is the equal-share benchmark. Alternative models are first summarized within each reporting source, then across sources in the same scope. Regional models and FMNR practitioner models stay separate. Missing weights are unknown; partial mapped group shares are not renormalized.</p><p>Direction counts use explicit fields only. Source classes and qualitative wording remain visible below. Current approval reflects the register flag and may include automated approvals; it does not certify human assessment. Numeric function support, current approval and target applicability are separate: no table here grants runtime weights or transfer approval.</p><p>Latest aggregate presentation: ${esc(payload.presentation_version||'unavailable')}; current dashboard registers supply the evidence. Historical handoff packages remain archived snapshots.</p></details><div id="dr-aggregate"></div><div id="dr-rule-detail"></div><h3 id="dr-source-heading" tabindex="-1">3.1.2 Source claims and review status</h3><p class="dr-note">Approval reflects the current register flag, including automated approvals. It does not certify human assessment.</p><div class="dr-filters">${select('dr-family','Source family',list(records().map(r=>r.suitability_family_id)),state.family,'All recorded families')}${select('dr-scope','Claim scope',[['practice_technology','General practice'],['species_specific','Species-specific'],['crop_specific','Crop-specific']],state.scope,'All scopes')}${select('dr-review','Current approval',[['approved','Approval recorded'],['unapproved','Approval not recorded']],state.review,'All review states')}</div><p id="dr-count" class="dr-note" aria-live="polite"></p><div id="dr-claims"></div><button type="button" id="dr-more">Show 25 more claims</button></div>`;
    renderResults();
  }
  function readableRule(rule) {
    const params=obj(rule.relationship_params), profiles=params.profiles||[];
    if(!profiles.length)return `<dl class="dr-rule-summary">${Object.entries(params).filter(([,v])=>v===null||typeof v!=='object').map(([key,value])=>`<dt>${esc(nice(key))}</dt><dd>${esc(value===null?'Unknown':value)}</dd>`).join('')}</dl>`;
    return profiles.map((profile,index)=>`<section class="dr-profile"><h4>${source(profile.source_id)} · ${esc(profile.unit||'Unit not recorded')}</h4><p>${esc(profile.applicability_note||'Target applicability requires review.')}</p><div class="dr-table-scroll"><table class="dr-table dr-intervals"><caption>Table 3.1.2.${index+1}. Recorded intervals · ${esc(profile.source_id)}</caption><thead><tr><th>Input interval</th><th>Source class</th><th>Compiled score</th><th>Score basis</th></tr></thead><tbody>${(profile.intervals||[]).map(band=>`<tr><td>${esc(band.lower===null||band.lower===undefined?'Below':(band.lower_inclusive?'≥ ':'> ')+band.lower)} ${band.upper===null||band.upper===undefined?'— no upper boundary':esc((band.upper_inclusive?'≤ ':'< ')+band.upper)}</td><td>${esc(band.label||'Not labelled')}</td><td>${esc(band.score===null||band.score===undefined?'Unknown':band.score)}</td><td>${esc(nice(band.score_basis||'not_recorded'))}</td></tr>`).join('')}</tbody></table></div><p class="dr-note">Outside reported intervals and unresolved boundaries remain unknown. Scores are stored compilation conventions, not measured probabilities.</p></section>`).join('');
  }
  function openPlots(id) {
    const rule=(data.recipes?.[state.practice]?.T4_suitability_mappings||[]).find(r=>r.mapping_id===id);
    if(!rule||!window.T4Analysis||!window.DashboardShell)return;
    const practice=state.practice, family=rule.suitability_family_id, host=$('t4-analysis');
    if(!host)return;
    let observer, timer;
    const selectPlots=()=>{
      if(host.hidden)return false;
      const variable=host.querySelector('[data-t4-study-variable]');
      if(!variable||![...variable.options].some(o=>o.value===rule.variable))return false;
      observer?.disconnect();if(timer)window.clearTimeout(timer);
      variable.value=rule.variable;
      const find=$('t4-find');if(find)find.value='';
      $('t4-tab-studies').click();
      variable.dispatchEvent(new Event('change',{bubbles:true}));
      host.scrollIntoView({block:'start'});variable.focus({preventScroll:true});
      return true;
    };
    window.DashboardShell.showExplorer();
    const practiceSelect=$('select-nbs');practiceSelect.value=practice;practiceSelect.dispatchEvent(new Event('change'));
    const familySelect=$('select-family');
    if([...familySelect.options].some(o=>o.value===family)){familySelect.value=family;familySelect.dispatchEvent(new Event('change'));}
    window.T4Analysis.update(practice,family,data);
    if(!selectPlots()&&window.MutationObserver){
      observer=new window.MutationObserver(selectPlots);observer.observe(host,{childList:true,subtree:true,attributes:true});
      timer=window.setTimeout(()=>observer.disconnect(),10000);
    }
  }
  function showRule(id) {
    const rule=(data.recipes?.[state.practice]?.T4_suitability_mappings||[]).find(r=>r.mapping_id===id);
    const target=$('dr-rule-detail');
    target.innerHTML=rule?`<section class="dr-rule" tabindex="-1"><h3>3.1.3 Compiled rule: ${esc(nice(rule.variable))}</h3><p>${esc(nice(rule.suitability_family_id))} · ${esc(nice(rule.relationship_type))}</p><p>${esc(rule.justification||'Inspect source context and explicit function selection before applying this rule.')}</p>${readableRule(rule)}${['agroforestry','forest_restoration','mangrove_restoration'].includes(state.practice)?`<button class="dr-plot-button" type="button" data-dr-plots="${esc(id)}">Compare source plots in Evidence explorer</button><p class="dr-note">Opens this variable and family using existing source plots. Check the snapshot warning before interpreting a curve.</p>`:''}<details><summary>Full function parameters and evidence links</summary><pre>${esc(JSON.stringify(obj(rule.relationship_params),null,2))}</pre><p>${esc(JSON.stringify(rule.evidence_ids||[]))}</p></details><p>Compiled does not mean approved for every location or family.</p></section>`:'<p>Rule is not present in the current recipe.</p>';
    target.scrollIntoView({block:'start'});target.querySelector('section')?.focus({preventScroll:true});
  }
  function change(event) {
    const ids={'dr-practice':'practice','dr-variable':'variable','dr-family':'family','dr-scope':'scope','dr-review':'review'};
    const key=ids[event.target.id];if(!key)return;
    state[key]=event.target.value;state.limit=25;
    if(key==='practice'){state.variable='';state.family='';state.query='';render();$(event.target.id)?.focus();}else renderResults();
  }
  function click(event) {
    const button=event.target.closest('button');if(!button)return;
    if(button.dataset.drSource){window.DashboardProgress?.openSource(button.dataset.drSource);return;}
    if(button.dataset.drRule){showRule(button.dataset.drRule);return;}
    if(button.dataset.drPlots){openPlots(button.dataset.drPlots);return;}
    if(button.dataset.drVariable){state.variable=button.dataset.drVariable;state.query='';state.scope='practice_technology';state.family='';state.review='';state.limit=25;render();$('dr-source-heading').scrollIntoView({block:'start'});$('dr-source-heading').focus({preventScroll:true});return;}
    if(button.id==='dr-reset'){Object.assign(state,{variable:'',query:'',family:'',scope:'practice_technology',review:'',limit:25});render();$('dr-search').focus();}
    if(button.id==='dr-more'){const next=selectedClaims()[state.limit];state.limit+=25;renderResults();if(next)$('dr-claim-'+next.evidence_id)?.focus();}
  }
  function refresh(next) {data=next;payload=data.relationships||{};root=$('relationship-review-root');if(!payload.practices?.[state.practice])state.practice=Object.keys(payload.practices||{})[0]||'';render();}
  window.DashboardRelationships={init(next){refresh(next);if(root&&!bound){root.addEventListener('change',change);root.addEventListener('click',click);root.addEventListener('input',e=>{if(e.target.id==='dr-search'){state.query=e.target.value;state.limit=25;renderResults();}});bound=true;}},refresh};
})();
