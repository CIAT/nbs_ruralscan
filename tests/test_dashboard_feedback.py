"""Feedback exports must not turn imported browser notes into executable markup."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_feedback_storage_and_export_boundaries():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for browser-script checks")
    script = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const good = {id:'note1', page:'dashboard.html', type:'Suggestion', severity:'Med',
  target:'Homegardens', text:'<img src=x onerror=alert(1)>', reviewer:'Test',
  created:'2026-11-04T00:00:00Z', tab:'tab-search', anchor:'', kind:'comment',
  quote:'', image:'', context:{tab:'Evidence & Discovery',scope:{nbs:'agroforestry'}}};
function load(notes) {
  const store = {nbs_dashboard_feedback: JSON.stringify(notes)};
  const sandbox = {location:{pathname:'/dashboard.html',href:'http://localhost/dashboard.html'},
    localStorage:{getItem:k=>store[k] || null}, window:{addEventListener(){}},
    document:{readyState:'loading',addEventListener(){},querySelector(){return null;}},
    URL, URLSearchParams, console};
  vm.runInNewContext(source,sandbox);
  return sandbox.window.DashboardFeedback;
}
const api=load([good, {...good,id:'bad" onclick="alert(1)'}, {...good,id:'badimage',
  image:'x" onerror="alert(1)'}, {...good,id:'badpage',page:'javascript:alert(1)'}]);
assert.equal(api.notes().length,1);
assert(api.buildReport().includes('&lt;img src=x onerror=alert(1)&gt;'));
assert(!api.buildReport().includes('<img src=x'));
assert(api.issueBody().includes('agroforestry'));
assert(api.issueBody().includes('tab-search'));
assert.equal(load({not:'an array'}).notes().length,0);
assert(!source.includes("fetch('/api/"));
"""
    result = subprocess.run(
        [node, "-e", script, str(ROOT / "docs/dashboard-feedback.js")],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr


def test_feedback_assets_and_stable_family_targets():
    html = (ROOT / "docs/dashboard.html").read_text()
    assert html.count('src="dashboard-feedback.js?v=1.0.2"') == 1
    assert html.count('href="dashboard-feedback.css?v=1.0.2"') == 1
    progress = (ROOT / "docs/dashboard-progress.js").read_text()
    assert (
        "data-feedback-key=\"${esc(feedbackKey('family:'+f.family_id))}\"" in progress
    )
    assert "data-feedback-key=\"${esc(feedbackKey('practice:'+p.nbs_id))}\"" in progress
    assert 'data-feedback-key="source:${esc(s.key)}"' in progress


def test_clear_all_backup_cancel_and_restore():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for browser-script checks")
    script = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const KEY = 'nbs_dashboard_feedback', BACKUP = KEY + '_clear_backup';
const note = {id:'old', page:'dashboard.html', type:'Suggestion', severity:'Med',
  target:'Overview', text:'Old feedback', reviewer:'Test', created:'2026-11-04T00:00:00Z',
  tab:'tab-search', anchor:'', kind:'comment', quote:'', image:''};
const store = {[KEY]:JSON.stringify([note]), qa_decisions:'untouched'};
let accepted = false, failKey = '', prompts = 0;
function load() {
  const nodes = {};
  function element() { return {style:{},classList:{add(){},contains(){return false;}},
    setAttribute(){},addEventListener(){},querySelector(){return null;},
    querySelectorAll(){return [];},appendChild(n){nodes[n.id]=n;}}; }
  const sandbox = {location:{pathname:'/dashboard.html',href:'http://localhost/dashboard.html'},
    localStorage:{getItem:k=>store[k]||null,removeItem:k=>delete store[k],
      setItem(k,v){if(k===failKey) throw Error('quota'); store[k]=v;}},
    window:{addEventListener(){},confirm(){prompts++;return accepted;}},
    document:{readyState:'complete',body:element(),createElement:element,
      addEventListener(){},querySelector(){return null;},querySelectorAll(){return [];},
      getElementById:k=>nodes[k]||null},
    MutationObserver:class {observe(){}},setTimeout(){},clearTimeout(){},
    URL,URLSearchParams,console};
  vm.runInNewContext(source,sandbox);
  return {api:sandbox.window.DashboardFeedback,nodes};
}
let {api,nodes} = load();
api.openNotes();
assert(nodes['rv-drawer'].innerHTML.includes('data-rv="clear-all"'));
api.clearAll(); // Cancel never writes a backup or clears notes.
assert.equal(JSON.parse(store[KEY]).length,1);
assert.equal(store[BACKUP],undefined);
accepted=true; failKey=BACKUP;
api.clearAll(); // Failed backup prevents deletion.
assert.equal(api.notes().length,1);
assert.equal(JSON.parse(store[KEY]).length,1);
failKey=KEY;
api.clearAll(); // Failed primary write preserves the original notes.
assert.equal(api.notes().length,1);
failKey='';
store[KEY]=JSON.stringify([note,{...note,id:'other_tab'}]);
api.clearAll();
assert.equal(api.notes().length,0);
assert.equal(JSON.parse(store[KEY]).length,0);
assert.equal(JSON.parse(store[BACKUP])[0].id,'old');
assert.equal(JSON.parse(store[BACKUP])[1].id,'other_tab');
assert(nodes['rv-drawer'].innerHTML.includes('Restore cleared notes'));
assert(nodes['rv-drawer'].innerHTML.includes('data-rv="clear-all" disabled'));
const count=prompts; api.clearAll(); assert.equal(prompts,count);
// Reload, then restore alongside newer notes, preserving any edited duplicate ID.
store[KEY]=JSON.stringify([{...note,id:'new',text:'New feedback'},
  {...note,text:'Edited after clearing'}]);
({api,nodes}=load());
failKey=KEY; api.restoreCleared();
assert(store[BACKUP]);
assert.equal(api.notes().length,2);
failKey=''; api.restoreCleared();
assert.equal(api.notes().length,3);
assert.equal(api.notes().find(n=>n.id==='old').text,'Edited after clearing');
assert.equal(store[BACKUP],undefined);
api.restoreCleared(); assert.equal(api.notes().length,3);
// A distinct cleared note survives reload and merges into current notes.
store[BACKUP]=JSON.stringify([{...note,id:'recover'}]);
({api}=load()); api.restoreCleared();
assert.deepEqual(Array.from(api.notes(),n=>n.id),['new','old','other_tab','recover']);
assert.equal(store.qa_decisions,'untouched');
"""
    result = subprocess.run(
        [node, "-e", script, str(ROOT / "docs/dashboard-feedback.js")],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
