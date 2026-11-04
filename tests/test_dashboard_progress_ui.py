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
  const metrics={known_sources:1,source_mix:{literature:1},extracted_sources:1,reviewed_sources:1,active_excerpts:1,approved_excerpts:1,all_excerpts:2,dropped_excerpts:1,t4_structural_relationships:1,t4_operational_relationships:0,t4_evidence_backed_relationships:1,t4_relationships:1,t4_contributing_sources:1,search_metrics};
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
assert(t.nodes.get('progress-app').innerHTML.includes('Cross-practice resources'));
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
assert(html.includes('0 | 0 | 0 | 0'));
t.api.openSource('canonical');
assert(t.nodes.get('dp-source-drawer').innerHTML.includes('Extracted: T4 0 · Effects 1 · M2b 0'));
""")


def test_feedback_targets_reveal_hidden_families_and_filtered_sources():
    run_js(r"""
const t=setup();
t.tabs['tab-methods'].click();
assert.equal(t.api.revealTarget('family:agroforestry__f1'),true);
assert.equal(t.activeTab,'tab-search');
assert.equal(t.nodes.get('dp-families-0').hidden,false);
assert.equal(t.api.scope().nbs,'all');
assert.equal(t.api.revealTarget('practice:cross'),true);
assert.equal(t.api.revealTarget('family:not-a-family'),false);
const query=t.nodes.get('dp-bib-query');query.value='no matching source';query.trigger('input');
assert.equal(t.api.revealTarget('source:canonical'),true);
assert.equal(t.activeTab,'tab-stocktake');
assert.equal(t.nodes.get('dp-source-drawer').dataset.feedbackKey,'source:canonical');
assert.equal(t.nodes.get('dp-source-drawer').dataset.feedbackLabel,t.fixture.progress_overview.sources[0].citation);
""")
