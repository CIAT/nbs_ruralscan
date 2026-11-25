"""Scoping companion must not confuse family, hazard and asset-threat evidence."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_provenance_and_roles():
    data = json.loads((ROOT / 'docs/redesign/infrastructure-evidence.json').read_text())
    for row in data['records']:
        if row['table'] == 'T3':
            assert row['risk_role'] in {'livelihood_mitigation', 'both'}
        for eid in row['evidence_ids']:
            evidence = data['evidence'][eid]
            assert evidence['source_id'] in data['sources']
    assert data['input_sha256']


def test_family_selection_and_missing_hazard():
    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js unavailable')
    script = r'''
const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const data=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const mount={dataset:{infrastructureEvidence:'opportunity'},innerHTML:''};
const listeners={};let selectedHazard='flood',onControls;
const ui={state:{practices:['agro_f1']},onControls(fn){onControls=fn;fn();}};
const context={document:{querySelectorAll:()=>[mount]},V1BUI:ui,
 window:{addEventListener:(key,fn)=>listeners[key]=fn},
 localStorage:{getItem:()=>JSON.stringify({hazard:selectedHazard})},
 fetch:()=>Promise.resolve({ok:true,json:()=>Promise.resolve(data)})};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),context);
setImmediate(()=>{
 assert(mount.innerHTML.includes('Confidence: very low'));
 assert(mount.innerHTML.includes('does not describe a physical process'));
 selectedHazard='landslide';listeners['infrastructure-exposure-change']();
 assert(mount.innerHTML.includes('No matching T3 mitigation row'));
 assert(mount.innerHTML.includes('Related T6 evidence'));
 selectedHazard='fire';listeners['infrastructure-exposure-change']();
 assert(!mount.innerHTML.includes('Related T6 evidence'));
 assert(mount.innerHTML.includes('Wider NbS evidence only'));
 ui.state.practices=['anr'];selectedHazard='flood';onControls();
 assert(mount.innerHTML.includes('Assisted natural regeneration'));
 assert(mount.innerHTML.includes('Wider NbS evidence only'));
 assert(!mount.innerHTML.includes('Selected family evidence.'));
 assert(mount.innerHTML.includes('Mitigation ratings are not multipliers'));
});
'''
    subprocess.run([node, '-e', script,
                    str(ROOT / 'docs/redesign/v1b-infrastructure-evidence.js'),
                    str(ROOT / 'docs/redesign/infrastructure-evidence.json')], check=True)
