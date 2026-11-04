"""Exercise the dashboard's read-only UI behavior without browser dependencies."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = r"""
const fs=require('fs'), vm=require('vm'), assert=require('assert');
const script=fs.readFileSync(process.argv[1],'utf8');
function setup() {
  const nodes=new Map(), handlers={}, events={}, tabs={};
  let activeTab='tab-search';
  const location={hash:'',pathname:'/dashboard.html',search:''};
  const document={activeElement:null};
  class Node {
    constructor(id=''){this.id=id;this.dataset={};this.listeners={};this.children=[];this.attrs={};this.isConnected=true;this.checked=false;this.value='';this.selectionStart=0;this._html='';this.classes=new Set();this.classList={add:x=>this.classes.add(x),remove:x=>this.classes.delete(x),contains:x=>this.classes.has(x)};if(id)nodes.set(id,this);}
    set innerHTML(html){this._html=html;for(const m of html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g)){const n=new Node(m[1]);const val=m[0].match(/\bvalue="([^"]*)"/);if(val)n.value=val[1];}}
    get innerHTML(){return this._html;}
    setAttribute(k,v){this.attrs[k]=v;}
    addEventListener(k,f){this.listeners[k]=f;}
    trigger(k){const f=this.listeners[k]||this['on'+k];if(f)f({target:this});}
    appendChild(n){this.children.push(n);n.isConnected=true;if(n.id)nodes.set(n.id,n);}
    remove(){this.isConnected=false;if(nodes.get(this.id)===this)nodes.delete(this.id);}
    focus(){document.activeElement=this;}
    scrollIntoView(){}
    setSelectionRange(){}
    querySelector(){return null;}
  }
  document.body=new Node('body');
  document.getElementById=id=>nodes.get(id)||null;
  document.createElement=()=>new Node();
  document.addEventListener=(k,f)=>handlers[k]=f;
  document.querySelector=selector=>{
    if(selector==='.tab-btn.active')return tabs[activeTab];
    const m=selector.match(/data-tab="([^"]+)"/);if(m)return tabs[m[1]];
    if(selector==='.dp-subtabs .is-active')return nodes.get('progress-app');
    return null;
  };
  document.querySelectorAll=()=>[];
  const window={scrollX:7,scrollY:321,scrollTo(x,y){this.scrollX=x;this.scrollY=y;},addEventListener(k,f){events[k]=f;},removeEventListener(k){delete events[k];},print(){assert(document.body.classList.contains('dp-print'));assert.equal(activeTab,'tab-search');if(events.afterprint)events.afterprint();}};
  const history={replaceState(_,__,url){location.hash=url.includes('#')?url.slice(url.indexOf('#')):'';}};
  for(const id of ['progress-app','bibliography-app','methods-app','dashboard-build'])new Node(id);
  for(const id of ['tab-search','tab-stocktake','tab-methods','tab-interrogator']){const n=new Node();n.dataset.tab=id;n.click=()=>{activeTab=id;window.DashboardProgress.onTab(id);};tabs[id]=n;}
  const search_metrics={events:0,retrieved:null,screened:null,included:null,complete_counts:0,screened_pct:null,coverage:Object.fromEntries(['retrieved','screened','included'].map(k=>[k,{recorded:0}]))};
  const metrics={known_sources:1,source_mix:{literature:1},extracted_sources:1,reviewed_sources:1,active_excerpts:1,approved_excerpts:1,all_excerpts:2,reviewed_excerpts:2,reviewed_unresolved_excerpts:0,dropped_excerpts:1,t4_structural_relationships:1,t4_operational_relationships:0,t4_evidence_backed_relationships:1,t4_relationships:1,t4_contributing_sources:1,search_metrics};
  const source={key:'canonical',source_id:'canonical',aliases:['alias'],citation:'First publication <img src=x onerror=alert(1)>',url:'javascript:alert(1)',doi:'',origins:['stock'],nbs_ids:['agroforestry'],family_ids:['agroforestry__f1'],evidence_ids:['ev1'],approved_evidence_ids:['ev1'],dropped_evidence_ids:['ev2'],contributions:{T4:['ev1']},extraction_counts:{T4:1,effects:0,M2b:0,other:0},type:'literature'};
  const fixture={timestamp:'2026-11-04',registers:{EV_evidence_register:[{evidence_id:'ev1',quote:'<script>alert(1)</script>',reviewer_ok:true,nbs_id:'agroforestry'}],TOOL_tool_registry:[]},_evDropped:[{evidence_id:'ev2',quote:'Quarantined claim',review_state:'dropped'}],stocktake:{peer_reviewed:[{oa_title:'Legacy agroforestry',NbS_Practice:'Agroforestry'},{oa_title:'Broad forest scope',NbS_Practice:'Forest conservation and restoration'}]},progress_ledger:[],progress_overview:{sources:[source],practices:[{nbs_id:'agroforestry',name:'Agroforestry',metrics,families:[{family_id:'agroforestry__f1',name:'Planted systems',metrics,subpractices:[]}]},{nbs_id:'cross',name:'Cross',metrics,families:[]}],totals:metrics,definitions:{counts:'Not additive'},searches:[{nbs_id:'agroforestry',category:'stock',tables:['T4'],search_ids:['s1'],counts:{retrieved:2,screened:1,included:1},raw_records:[{n_retrieved:'2',search_terms:'<img src=x onerror=alert(1)>'}]}]}};
  vm.runInNewContext(script,{window,document,location,history,URL,console,URIError});
  window.DashboardProgress.init(fixture);
  return {api:window.DashboardProgress,window,document,nodes,handlers,events,tabs,location,fixture,get activeTab(){return activeTab;}};
}
"""


def run_js(body):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for UI behavior checks")
    result = subprocess.run(
        [node, "-e", HARNESS + body, str(ROOT / "docs/dashboard-progress.js")],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr


def test_bibliography_escapes_content_and_preserves_explicit_practice_filters():
    run_js(r"""
const t=setup();
assert(!t.nodes.get('progress-app').innerHTML.includes('Cross-practice resources'));
assert(!t.nodes.get('progress-app').innerHTML.includes('data-value="cross"'));
assert(t.nodes.get('progress-app').innerHTML.includes('general reference sources'));
assert(!t.nodes.get('bibliography-app').innerHTML.includes('<img'));
assert(!t.nodes.get('bibliography-app').innerHTML.includes('href="javascript:'));
assert(t.nodes.get('methods-app').innerHTML.includes('Original search record 1'));
assert(!t.nodes.get('methods-app').innerHTML.includes('<pre>'));
assert(!t.nodes.get('methods-app').innerHTML.includes('<img'));
let select=t.nodes.get('dp-bib-nbs');select.value='agroforestry';select.trigger('change');
let html=t.nodes.get('bibliography-app').innerHTML;
assert(html.includes('Legacy agroforestry'));assert(!html.includes('Broad forest scope'));
select=t.nodes.get('dp-bib-table');select.value='T4';select.trigger('change');
html=t.nodes.get('bibliography-app').innerHTML;
assert(html.includes('First publication'));assert(!html.includes('Legacy agroforestry'));
const query=t.nodes.get('dp-bib-query');query.value='no match <svg onload=alert(1)>';query.trigger('input');
html=t.nodes.get('bibliography-app').innerHTML;
assert(html.includes('No matching records'));assert(!html.includes('<svg'));
""")


def test_alias_source_drawer_escape_quarantine_and_same_tab_navigation():
    run_js(r"""
const t=setup();t.tabs['tab-interrogator'].click();
const previous=t.nodes.get('dp-bib-query');previous.focus();
t.api.openSource('alias');
assert.equal(t.location.hash,'#source=canonical');
assert(t.nodes.get('dp-source-drawer'));
assert(!t.nodes.get('dp-source-drawer').innerHTML.includes('<img'));
assert(!t.nodes.get('dp-drawer-evidence').innerHTML.includes('<script>'));
assert(!t.nodes.get('dp-drawer-evidence').innerHTML.includes('Quarantined claim'));
const toggle=t.nodes.get('dp-show-dropped');toggle.checked=true;toggle.trigger('change');
assert(t.nodes.get('dp-drawer-evidence').innerHTML.includes('Quarantined claim'));
t.api.onTab('tab-interrogator');assert(t.nodes.get('dp-source-drawer'));
t.handlers.keydown({key:'Escape'});
assert(!t.nodes.get('dp-source-drawer'));assert.equal(t.document.activeElement,previous);
assert.equal(t.location.hash,'');
t.location.hash='#source=alias';t.events.hashchange();
assert(t.nodes.get('dp-source-drawer'));assert.equal(t.location.hash,'#source=canonical');
assert.equal(t.activeTab,'tab-stocktake');
t.tabs['tab-methods'].click();assert(!t.nodes.get('dp-source-drawer'));
t.location.hash='#source=%E0%A4%A';assert.doesNotThrow(()=>t.events.hashchange());
""")


def test_print_restores_active_tab_drawer_hash_scroll_and_overview_markup():
    run_js(r"""
const t=setup();t.tabs['tab-interrogator'].click();t.api.openSource('canonical');
const oldDrawer=t.nodes.get('dp-source-drawer'), oldMarkup=t.nodes.get('progress-app').innerHTML;
t.api.print();
assert.equal(t.activeTab,'tab-interrogator');
assert.equal(t.nodes.get('dp-source-drawer'),oldDrawer);
assert.equal(t.location.hash,'#source=canonical');
assert.equal(t.nodes.get('progress-app').innerHTML,oldMarkup);
assert.equal(t.window.scrollX,7);assert.equal(t.window.scrollY,321);
assert(!t.document.body.classList.contains('dp-print'));
assert(!t.events.afterprint);
""")


def test_print_hides_dashboard_controls_and_feedback():
    css = (ROOT / "docs/dashboard-progress.css").read_text()
    assert "body.dp-print .tab-nav" in css
    assert "body.dp-print [data-rv-ui]" in css
    assert "body.dp-print .header-actions>*:not(#dashboard-build)" in css
    assert "var(--text-main" not in css


def test_uncited_effect_excerpts_remain_visible_as_extraction_work():
    run_js(r"""
const t=setup();
t.fixture.progress_overview.sources[0].contributions={};
t.fixture.progress_overview.sources[0].extraction_counts={T4:0,effects:1,M2b:0,other:0};
t.api.refresh(t.fixture);
const html=t.nodes.get('bibliography-app').innerHTML;
assert(html.includes('Extracted: T4 0 · Effects 1 · M2b 0'));
assert(html.includes('Compiled contributions'));
for(const title of ['T4 suitability','T3 hazard response','T6 benefits','M2b risk roles'])assert(html.includes(title+' · 0'));
assert(!html.includes('data-action="source-evidence" data-value="[&quot;canonical&quot;,&quot;T4&quot;]'));
t.api.openSource('canonical');
assert(t.nodes.get('dp-source-drawer').innerHTML.includes('Extracted: T4 0 · Effects 1 · M2b 0'));
""")


def test_feedback_targets_reveal_hidden_families_and_filtered_sources():
    run_js(r"""
const t=setup();
t.tabs['tab-methods'].click();
assert.equal(t.api.revealTarget('family:agroforestry__f1'),true);
assert.equal(t.activeTab,'tab-search');
assert(t.nodes.get('progress-app').innerHTML.includes('Planted systems'));
assert.equal(t.api.scope().nbs,'agroforestry');
assert.equal(t.api.scope().family,'agroforestry__f1');
assert.equal(t.api.revealTarget('practice:cross'),false);
assert.equal(t.api.revealTarget('family:not-a-family'),false);
const query=t.nodes.get('dp-bib-query');query.value='no matching source';query.trigger('input');
assert.equal(t.api.revealTarget('source:canonical'),true);
assert.equal(t.activeTab,'tab-stocktake');
assert.equal(t.nodes.get('dp-source-drawer').dataset.feedbackKey,'source:canonical');
assert.equal(t.nodes.get('dp-source-drawer').dataset.feedbackLabel,t.fixture.progress_overview.sources[0].citation);
""")


def test_progress_overview_separates_count_units_and_keeps_families_in_practice_views():
    run_js(r"""
const t=setup();
let html=t.nodes.get('progress-app').innerHTML;
assert(!html.includes('Results found'));assert(!html.includes('Results screened'));
assert(!html.includes('Candidates screened'));assert(!html.includes('Candidates selected'));
assert(html.includes('Extracts reviewed'));assert(html.includes('Extracts approved'));
assert(html.includes('View subpractices'));assert(!html.includes('dp-flow'));
assert(t.nodes.get('methods-app').innerHTML.includes('Candidates screened'));
const sourceTable=html.split('<table class="dp-table dp-summary-table">')[1].split('</table>')[0];
assert(!sourceTable.includes('Screening'));assert(sourceTable.includes('Sources catalogued'));
assert(!html.includes('Planted systems'));assert(!html.includes('dp-family-group'));
assert(!html.includes('searches fully counted'));assert(!html.includes('Search hits selected'));
assert(html.includes('Type not recorded'));assert(!html.includes('Tools | ?'));
assert(t.api.revealTarget('family:agroforestry__f1'));
html=t.nodes.get('progress-app').innerHTML;
assert(!html.includes('dp-flow'));assert(html.includes('100%'));assert(html.includes('dp-progress-family'));
assert(html.includes('Verification stage'));assert(!html.includes('<th>Extracted</th>'));
""")


def test_family_filters_hide_out_of_scope_without_losing_historical_totals():
    run_js(r"""
const t=setup(), p=t.fixture.progress_overview.practices[0];
p.families.push({family_id:'agroforestry__out',name:'Out of scope family',metrics:p.metrics,subpractices:[]});
p.families.push({family_id:'agroforestry__pending',name:'Needs review family',metrics:{...p.metrics,approved_excerpts:0,reviewed_excerpts:0},subpractices:[]});
t.fixture.family_display_status={'agroforestry__out':{status:'out_of_scope'}};
t.api.refresh(t.fixture);t.api.revealTarget('family:agroforestry__f1');
let family=t.nodes.get('dp-progress-family');family.value='';family.trigger('change');
let html=t.nodes.get('progress-app').innerHTML;
assert(!html.includes('Out of scope family'));assert(html.includes('Needs review family'));
assert.equal(t.api.revealTarget('family:agroforestry__out'),false);
const filter=t.nodes.get('dp-progress-review');filter.value='pending';filter.trigger('change');
html=t.nodes.get('progress-app').innerHTML;
assert(!html.includes('data-feedback-label="Planted systems"'));
assert(html.includes('data-feedback-label="Needs review family"'));
assert.equal(t.fixture.progress_overview.totals.known_sources,1);
""")


def test_activity_log_filters_and_paginates_real_ledger_stages():
    run_js(r"""
const t=setup();
t.fixture.progress_ledger=Array.from({length:45},(_,i)=>({nbs_id:'agroforestry',family:'agroforestry__f1',table:i<30?'T4':'T6',category:'stock',searched:'done',screened:'in_progress',verified:'done',updated:'2026-11-04'}));
t.api.refresh(t.fixture);t.api.revealTarget('family:agroforestry__f1');
let html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('45 records · 1–20 shown'));assert(html.includes('Page 1 / 3'));
assert.equal((html.match(/<td>T4<\/td>/g)||[]).length,20);
let select=t.nodes.get('dp-ledger-table');t.nodes.get('dp-ledger').open=true;select.value='T6';select.trigger('change');
html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('15 records · 1–15 shown'));assert.equal(t.nodes.get('dp-ledger').open,true);
assert(!html.includes('<td>T4</td>'));assert(html.includes('Verification stage'));
""")


def test_methods_uses_matched_discovery_counts_only():
    run_js(r"""
const t=setup(), m=t.fixture.progress_overview.totals;
m.search_metrics={...m.search_metrics,retrieved:41,screened:93,included:26,complete_counts:0,paired_retrieved:0,paired_screened:0,paired_included:0};
t.api.refresh(t.fixture);
let html=t.nodes.get('methods-app').innerHTML;
assert(!html.includes('>41</td>'));assert(!html.includes('>93</td>'));assert(!html.includes('>26</td>'));
m.search_metrics={...m.search_metrics,events:3,complete_counts:1,paired_retrieved:100,paired_screened:20,paired_included:10};
t.api.refresh(t.fixture);html=t.nodes.get('methods-app').innerHTML;
assert(!html.includes('>100</td>'));assert(html.includes('>20</td>'));assert(html.includes('>10</td>'));
assert(!html.includes('20%'));assert(html.includes('1 of 3'));
t.api.openMethods('agroforestry');
assert.equal(t.activeTab,'tab-methods');
html=t.nodes.get('methods-app').innerHTML;
assert(html.includes('Reported hits (context only): 2'));
assert(html.includes('Screening assessments: 1'));
assert(html.includes('not unique papers or a screening backlog'));
""")


def test_source_metadata_aliases_access_and_missing_screening():
    run_js(r"""
const t=setup();
t.window.vfSharePointUrl=p=>'https://library.example/'+p;
t.fixture.registers.SRC_source_register=[
  {source_id:'canonical',citation:'Canonical citation',library_path:'source.pdf',method_type:'review',study_country:'Niger',doi:'canonical-doi'},
  {source_id:'alias',citation:'Alias citation',library_path:'alias.pdf',method_type:'modelling',doi:'alias-doi'}];
t.api.refresh(t.fixture);t.api.openSource('alias');
const html=t.nodes.get('dp-source-drawer').innerHTML;
assert(html.includes('https://library.example/source.pdf'));
assert(html.includes('https://library.example/alias.pdf'));
assert(html.includes('Canonical citation'));assert(html.includes('Alias citation'));
assert(html.includes('canonical-doi'));assert(html.includes('alias-doi'));
assert(html.includes('Metadata belongs to this source ID'));
assert(html.includes('Not recorded at source level; extraction is not a screening decision.'));
assert(!html.includes('href="javascript:'));
assert.equal(t.nodes.get('dp-source-details').hidden,true);
t.nodes.get('dp-view-details').onclick();
assert.equal(t.nodes.get('dp-source-details').hidden,false);
assert.equal(t.nodes.get('dp-source-evidence').hidden,true);
assert.equal(t.nodes.get('dp-view-details').attrs['aria-pressed'],'true');
""")


def test_evidence_filter_intersections_quarantine_and_reset():
    run_js(r"""
const t=setup(),s=t.fixture.progress_overview.sources[0];
s.evidence_ids=['ev1','ev3','ev4'];s.approved_evidence_ids=['ev1'];
s.contributions={T4:['ev1'],T3:['ev3'],T6:['ev3','ev4'],M2b:['ev4']};
t.fixture.registers.EV_evidence_register=[
 {evidence_id:'ev1',source_id:'canonical',variable:'slope',quote:'Suitability quote',use_role:'structural_suitability',reviewer_ok:true,nbs_id:'agroforestry',suitability_family_id:'f1'},
 {evidence_id:'ev3',source_id:'canonical',variable:'yield',quote:'Yield benefit',use_role:'nbs_effect',reviewer_ok:false,nbs_id:'agroforestry',suitability_family_id:'agroforestry__f1'},
 {evidence_id:'ev4',source_id:'canonical',variable:'tenure',quote:'Tenure risk',use_role:'operational_risk',reviewer_ok:false,nbs_id:'agroforestry',suitability_family_id:'agroforestry__f2'}];
t.fixture._evDropped=[{evidence_id:'ev2',source_id:'canonical',quote:'Dropped despite old approval',review_state:'dropped',reviewer_ok:true}];
t.api.refresh(t.fixture);t.api.openSource('canonical','T6');
function select(k,value){const el=t.nodes.get('dp-excerpt-'+k);el.value=value;el.trigger('change');}
function html(){return t.nodes.get('dp-drawer-evidence').innerHTML;}
assert(html().includes('Yield benefit'));assert(html().includes('Tenure risk'));assert(!html().includes('Suitability quote'));
select('family','agroforestry__f1');assert(html().includes('Yield benefit'));assert(!html().includes('Tenure risk'));
select('role','structural_suitability');assert(html().includes('No linked excerpts'));
t.nodes.get('dp-excerpt-reset').onclick();
assert(html().includes('Suitability quote'));assert(!html().includes('Dropped despite'));
select('review','approved');assert(html().includes('Suitability quote'));assert(!html().includes('Yield benefit'));
select('review','dropped');assert(html().includes('Dropped despite'));assert(!html().includes('Suitability quote'));assert(!html().includes('dp-evidence-status">Approved'));
assert.equal(t.nodes.get('dp-show-dropped').checked,true);
const toggle=t.nodes.get('dp-show-dropped');toggle.checked=false;toggle.trigger('change');
assert.equal(t.nodes.get('dp-excerpt-review').value,'');
assert(html().includes('Suitability quote'));assert(!html().includes('Dropped despite'));
t.nodes.get('dp-excerpt-reset').onclick();
const query=t.nodes.get('dp-excerpt-query');query.value='ev3';query.trigger('input');
assert(html().includes('Yield benefit'));assert(!html().includes('Tenure risk'));
t.api.openSource('canonical');assert(html().includes('Tenure risk')); // New source opening resets filters.
""")


def test_bibliography_combines_filters_and_resets_family_on_practice_change():
    run_js(r"""
const t=setup();
function select(k,value){const el=t.nodes.get('dp-bib-'+k);el.value=value;el.trigger('change');}
function html(){return t.nodes.get('bibliography-app').innerHTML;}
select('family','agroforestry__f1');assert(html().includes('First publication'));assert(!html().includes('Legacy agroforestry'));
select('evidence','pending');assert(html().includes('No matching records'));
select('evidence','approved');assert(html().includes('First publication'));
select('origin','grey');assert(html().includes('No matching records'));
select('origin','stock');assert(html().includes('First publication'));
select('nbs','cross');assert(html().includes('No matching records'));
select('nbs','agroforestry');select('evidence','');
assert(html().includes('Legacy agroforestry')); // Practice change cleared family filter.
const target={dataset:{action:'bib-reset'},closest:()=>target};
t.handlers.click({target});
assert(html().includes('Broad forest scope'));
assert.equal(t.document.activeElement,t.nodes.get('dp-bib-query'));
""")


def test_passage_links_do_not_invent_section_anchors_or_unpinned_code():
    run_js(r"""
const t=setup(),s=t.fixture.progress_overview.sources[0];
t.window.vfSharePointUrl=p=>'https://library.example/'+p;
t.fixture.registers.SRC_source_register=[{source_id:'canonical',library_path:'source.pdf'}];
const ev=t.fixture.registers.EV_evidence_register[0];
Object.assign(ev,{source_id:'canonical',page:12,locator_type:'page',context:{note:'<img src=x onerror=alert(1)>'}});
t.api.refresh(t.fixture);t.api.openSource('canonical');
let html=t.nodes.get('dp-drawer-evidence').innerHTML;
assert(html.includes('https://library.example/source.pdf#page=12'));
assert(html.includes('Full evidence record'));assert(!html.includes('<img'));
t.fixture.registers.SRC_source_register=[{source_id:'canonical',url:'https://example.org/report'}];
Object.assign(ev,{page:12,locator_type:'section',locator:'Results'});
t.api.refresh(t.fixture);t.api.openSource('canonical');html=t.nodes.get('dp-drawer-evidence').innerHTML;
assert(html.includes('href="https://example.org/report"'));assert(!html.includes('#Results'));assert(!html.includes('#page=12'));
t.fixture.registers.SRC_source_register=[{source_id:'canonical',url:'https://github.com/team/project'}];
Object.assign(ev,{locator_type:'file_line',locator:'src/rules.py:L4-L8',commit_sha:'abcdef1234567'});
t.api.refresh(t.fixture);t.api.openSource('canonical');html=t.nodes.get('dp-drawer-evidence').innerHTML;
assert(html.includes('https://github.com/team/project/blob/abcdef1234567/src/rules.py#L4-L8'));
ev.commit_sha='';t.api.refresh(t.fixture);t.api.openSource('canonical');html=t.nodes.get('dp-drawer-evidence').innerHTML;
assert(!html.includes('/blob/'));assert(!html.includes('Open pinned code'));
""")


def test_empty_legacy_source_opens_details_and_contribution_buttons_use_exact_subset():
    run_js(r"""
const t=setup();t.api.openSource('legacy:peer_reviewed:0');
assert.equal(t.nodes.get('dp-source-details').hidden,false);
assert(t.nodes.get('dp-source-drawer').innerHTML.includes('No source link recorded.'));
const target={dataset:{action:'source-evidence',value:JSON.stringify(['canonical','T3'])},closest:()=>target};
t.handlers.click({target});
assert.equal(t.nodes.get('dp-source-evidence').hidden,false);
assert(t.nodes.get('dp-drawer-evidence').innerHTML.includes('No linked excerpts'));
""")


def test_unmapped_recorded_scopes_remain_filterable_without_invented_family_links():
    run_js(r"""
const t=setup();t.fixture.progress_overview.sources[0].family_ids=['unmapped_subpractice'];
t.api.refresh(t.fixture);
let html=t.nodes.get('bibliography-app').innerHTML;
assert(html.includes('Recorded scope: Unmapped subpractice (unmapped)'));
const family=t.nodes.get('dp-bib-family');family.value='unmapped_subpractice';family.trigger('change');
html=t.nodes.get('bibliography-app').innerHTML;
assert(html.includes('First publication'));assert(!html.includes('Legacy agroforestry'));
assert(!html.includes('data-feedback-key="family:agroforestry__unmapped_subpractice"'));
""")


def test_stage_headers_keep_review_and_approval_denominators_distinct():
    run_js(r"""
const t=setup(), m=t.fixture.progress_overview.totals;
Object.assign(m,{known_sources:25,extracted_sources:7,all_excerpts:30,active_excerpts:23,reviewed_excerpts:20,approved_excerpts:5,dropped_excerpts:7,t4_structural_relationships:99,contributing_excerpts:11});
t.api.refresh(t.fixture);
const html=t.nodes.get('progress-app').innerHTML;
const table=html.split('<table class="dp-table dp-summary-table">')[1].split('</table>')[0];
assert(table.includes('</td><td>7</td><td>30</td><td title="20 reviewed out of 30 recorded extracts">20'));
assert(table.includes('(66.7%)'));assert(table.includes('5 approved out of 20 reviewed extracts'));assert(table.includes('(25%)'));
assert(table.includes('</td><td>7</td><td>11</td>'));
assert(table.indexOf('Extracts reviewed') < table.indexOf('Extracts approved'));
assert(html.includes('A source</strong> is a publication'));
assert(!html.includes('Claims still in use'));assert(!html.includes('dp-flow'));
""")


def test_family_scope_notes_and_count_definitions_follow_selected_practice():
    run_js(r"""
const t=setup(),p=t.fixture.progress_overview.practices[0];
p.metrics={...p.metrics,known_sources:1};
t.fixture.progress_overview.totals={...p.metrics,known_sources:99};
p.families.push({family_id:'agroforestry__cross_family',name:'Cross family',scope_kind:'all_families',scope_definition:'Tagged for all families; not a subpractice.',metrics:p.metrics,subpractices:[]});
p.families.push({family_id:'__unassigned',name:'Family not recorded',scope_kind:'unassigned',metrics:{...p.metrics,all_excerpts:0},subpractices:[]});
t.api.refresh(t.fixture);t.api.revealTarget('family:agroforestry__cross_family');
const html=t.nodes.get('progress-app').innerHTML;
assert(t.nodes.get('dp-scope-notes').open);
assert(html.includes('Evidence tagged as applying across all families'));
assert(html.includes('Sources without a recorded family'));
assert(!html.split('dp-family-table')[1].split('<tbody>')[1].split('</tbody>')[0].includes('>Cross family<'));
assert(html.includes('1 source records in this scope'));assert(!html.includes('99 source records in this scope'));
assert(html.includes('dp-column-filter'));assert(html.includes('data-action="family-sort"'));
assert(html.includes('percentage cannot be calculated'));
""")


def test_count_drilldowns_match_authoritative_scope_and_show_selected_family():
    run_js(r"""
const t=setup(),p=t.fixture.progress_overview.practices[0];
p.families.push({family_id:'__unassigned',name:'Family not recorded',scope_kind:'unassigned',metrics:{...p.metrics,source_keys:['canonical']},subpractices:[]});
t.api.refresh(t.fixture);
let target={dataset:{action:'scope-bibliography',value:JSON.stringify(['agroforestry','__unassigned'])},closest:()=>target};
t.handlers.click({target});
let html=t.nodes.get('bibliography-app').innerHTML;
assert(html.includes('value="__unassigned" selected>Family not recorded'));
assert(html.includes('First publication'));assert(!html.includes('Legacy agroforestry'));
target={dataset:{action:'known',value:'agroforestry'},closest:()=>target};t.handlers.click({target});
html=t.nodes.get('bibliography-app').innerHTML;
assert(html.includes('value="agroforestry" selected'));
assert(html.includes('First publication'));assert(!html.includes('Legacy agroforestry'));assert(!html.includes('Broad forest scope'));
""")


def test_global_unassigned_filter_unions_each_practice_scope():
    run_js(r"""
const t=setup(),p=t.fixture.progress_overview.practices[0];
p.families.push({family_id:'__unassigned',name:'Family not recorded',metrics:{...p.metrics,source_keys:['canonical']},subpractices:[]});
t.api.refresh(t.fixture);
const selector=t.nodes.get('dp-bib-family');selector.value='__unassigned';selector.trigger('change');
const html=t.nodes.get('bibliography-app').innerHTML;
assert(html.includes('value="__unassigned" selected>Family not recorded (any practice)'));
assert(html.includes('First publication'));assert(!html.includes('Legacy agroforestry'));
""")


def test_progress_subtabs_and_content_share_stable_section_numbers():
    run_js(r"""
const t=setup();
let html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('class="dp-subtabs shell-subnav"'));
assert(html.includes('2.1 Overview'));assert(html.includes('2.2 Agroforestry'));
assert(html.includes('<h2>2.1 Progress overview</h2>'));
const target={dataset:{action:'practice',value:'agroforestry'},closest:()=>target};
t.handlers.click({target});
html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('<h2>2.2 Agroforestry</h2>'));
assert(html.includes('2.2.1 Evidence by suitability family'));
assert(html.includes('Table 2.2.1. Agroforestry'));
""")


def test_chart_outcomes_partition_recorded_extracts_and_keep_denominators_explicit():
    run_js(r"""
const t=setup(), m=t.fixture.progress_overview.practices[0].metrics;
Object.assign(m,{all_excerpts:30,reviewed_excerpts:20,approved_excerpts:5,reviewed_unresolved_excerpts:8,reviewed_dropped_excerpts:7,unreviewed_excerpts:10,dropped_excerpts:9});
t.api.refresh(t.fixture);
let html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('id="dp-chart-view">'));
assert(html.includes('id="dp-table-view" hidden'));
assert(html.includes('Approved: 5; Reviewed · unresolved: 8; Reviewed · excluded: 7; No assessment recorded: 10'));
assert(html.includes('66.7% reviewed; 25% of reviewed extracts approved'));
assert(html.includes('7 reviewed · excluded'));assert(!html.includes('9 reviewed · excluded'));
assert(html.includes('All practice bars share one count scale: 0–30 recorded extracts'));
assert(html.includes('Deduplicated total · All evidence'));
const click=(action,value)=>{const target={dataset:{action,value},closest:()=>target};t.handlers.click({target});};
click('chart-scale','percent');
html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('Every full bar = 100%'));
assert.equal(t.document.activeElement.id,'dp-chart-scale-percent');
click('overview-view','table');html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('id="dp-chart-view" hidden'));assert(html.includes('id="dp-table-view">'));
assert.equal(t.document.activeElement.id,'dp-table-view-button');
click('overview-view','chart');
assert(t.api.revealTarget('chart-practice:agroforestry'));
assert(!t.api.revealTarget('chart-practice:missing'));
Object.assign(m,{all_excerpts:0,reviewed_excerpts:0,approved_excerpts:0,reviewed_unresolved_excerpts:0,reviewed_dropped_excerpts:0,unreviewed_excerpts:0});
t.api.refresh(t.fixture);html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('No extracts recorded'));assert(!html.includes('width:NaN'));assert(!html.includes('Infinity'));
""")


def test_analytical_purpose_updates_metrics_and_exact_source_drilldown():
    run_js(r"""
const t=setup(), model=t.fixture.progress_overview;
const base=model.practices[0];
const metric={...base.metrics,known_sources:1,all_excerpts:10,reviewed_excerpts:4,approved_excerpts:2,reviewed_unresolved_excerpts:1,reviewed_dropped_excerpts:1,unreviewed_excerpts:6,contributing_excerpts:3,source_keys:['canonical']};
const output={table_id:'T3',label:'Hazard response',unit:'assessments',output_count:2,evidence_backed_outputs:1,contributing_sources:1,contributing_excerpts:3,source_keys:['canonical'],rows:[{id:'one',label:'Drought <img>',evidence_ids:['ev1'],source_keys:['canonical']}]};
model.outputs=[output];base.outputs=[output];
model.table_views={T3:{totals:metric,scope_note:'Routed inputs can overlap.',practices:[{...base,metrics:metric,families:base.families.map(f=>({...f,metrics:metric}))}]},T2a:{totals:{...metric,all_excerpts:0,reviewed_excerpts:0,approved_excerpts:0,reviewed_unresolved_excerpts:0,reviewed_dropped_excerpts:0,unreviewed_excerpts:0},scope_note:'Shared configuration; zero tracked extracts does not mean no research.',project_level:true,practices:[]}};
t.api.refresh(t.fixture);
const choose=v=>{const n=t.nodes.get('dp-progress-table');n.value=v;n.trigger('change');};
const click=(action,value)=>{const target={dataset:{action,value},closest:()=>target};t.handlers.click({target});};
choose('T3');let html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('Evidence progress · T3 · Hazard response'));
assert(html.includes('4 reviewed out of 10 recorded extracts'));assert(html.includes('(40%)'));assert(html.includes('(50%)'));
assert(html.includes('3 extracts used in outputs'));assert(html.includes('Routed inputs can overlap.'));
assert(html.includes('Drought &lt;img&gt;'));assert(!html.includes('Drought <img>'));
model.sources[0].nbs_ids=['riparian_buffer'];
click('bibliography','agroforestry');assert(t.nodes.get('bibliography-app').innerHTML.includes('1 matching records'));
click('known','agroforestry');assert(t.nodes.get('bibliography-app').innerHTML.includes('1 matching records'));
assert(!t.nodes.get('bibliography-app').innerHTML.includes('Legacy agroforestry'));
click('bib-reset','');assert(t.nodes.get('bibliography-app').innerHTML.includes('Legacy agroforestry'));
click('output-sources','T3');assert(t.nodes.get('bibliography-app').innerHTML.includes('1 matching records'));
click('practice','agroforestry');html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('4 reviewed out of 10 recorded extracts'));
choose('T2a');html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('Shared climate-risk configuration'));assert(html.includes('zero tracked extracts does not mean no research'));
assert(!html.includes('id="dp-chart-practice-agroforestry"'));assert(!html.includes('width:NaN'));
click('practice','agroforestry');html=t.nodes.get('progress-app').innerHTML;assert(html.includes('practice-level allocations are not recorded'));assert(!html.includes('Count definitions'));
assert(t.api.revealTarget('progress:T3:chart-practice:agroforestry'));assert.equal(t.api.scope().table,'T3');
assert(t.nodes.get('progress-app').innerHTML.includes('4 reviewed out of 10 recorded extracts'));
assert(t.api.revealTarget('progress:T3:output:T3:all'));assert.equal(t.api.scope().table,'T3');
assert(!t.api.revealTarget('progress:BAD:output:T3:all'));
choose('');html=t.nodes.get('progress-app').innerHTML;
assert(html.includes('Evidence progress · All evidence'));
assert(html.includes('id="dp-chart-practice-agroforestry"'));
""")


def test_evidence_groups_and_umbrella_labels_do_not_become_practice_options():
    run_js(r"""
const t=setup(), p=t.fixture.progress_overview.practices[0];
p.families[0].subpractices=[{name:'Broad umbrella',presentation_role:'umbrella'},{name:'Specific <variant>',presentation_role:'variant'}];
p.families.push({family_id:'agroforestry__cross_family',name:'Shared claims',navigation_group:'evidence',metrics:p.metrics,subpractices:[{name:'Routing tag',presentation_role:'evidence'}]});
p.families.push({family_id:'__unassigned',name:'Unassigned claims',navigation_group:'evidence',metrics:p.metrics,subpractices:[]});
t.api.refresh(t.fixture);t.api.revealTarget('family:agroforestry__f1');
let select=t.nodes.get('dp-progress-family');select.value='';select.trigger('change');
let html=t.nodes.get('progress-app').innerHTML;
const table=html.match(/<table class="dp-table dp-summary-table dp-family-table">[\s\S]*?<\/table>/)[0];
const rows=table.split('<tbody>')[1].split('</tbody>')[0];
assert(rows.includes('Planted systems'));assert(!rows.includes('Shared claims'));assert(!rows.includes('Unassigned claims'));
assert(table.includes('Umbrella category: Broad umbrella'));assert(table.includes('Variant: Specific &lt;variant&gt;'));
const evidence=html.match(/<table class="dp-table dp-summary-table dp-evidence-family-table">[\s\S]*?<\/table>/)[0];
assert(evidence.includes('Shared claims'));assert(evidence.includes('Unassigned claims'));assert(!evidence.includes('Planted systems'));
assert(t.api.revealTarget('family:agroforestry__cross_family'));
assert.equal(t.api.scope().family,'agroforestry__cross_family');
html=t.nodes.get('progress-app').innerHTML;assert(html.includes('data-feedback-key="family:agroforestry__cross_family"'));
assert.equal(t.fixture.progress_overview.totals.known_sources,1);
""")
