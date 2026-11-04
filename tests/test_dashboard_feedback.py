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
    assert html.count('src="dashboard-feedback.js"') == 1
    assert html.count('href="dashboard-feedback.css"') == 1
    assert "tr.dataset.feedbackKey = 'family:' + r.familyId" in html
    assert "gtr.dataset.feedbackKey = 'practice:' + r.nbsId" in html
