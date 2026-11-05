"""Shared C.5 classification remains consistent across display consumers."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_shared_classification():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js unavailable")
    script = r"""
const assert = require('node:assert/strict'), fs = require('node:fs'), vm = require('node:vm');
let stored = {};
const cells = Array.from({length:10}, (_,i)=>({
  ind:{poverty:i,drought:i}, drought2050:i+3, residents:i+1,
  suitClass:i<5?'vh':'h', suitClass2050:i<3?'vh':'h'
}));
cells.push({ind:{poverty:100,drought:100}, excluded:true});
function boot() {
  const w = {FIXTURE:{cells, rollup:st=>({sel:c=>!!st.classes[st.climate==='ssp'?c.suitClass2050:c.suitClass]})}};
  const ctx = {window:w, localStorage:{getItem:k=>stored[k],setItem:(k,v)=>stored[k]=v}};
  vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),ctx);
  return w.V1BClassification;
}
const st={classes:{vh:1,h:1},climate:'base'}, C=boot();
assert(C.set('poverty',{count:2,method:'threshold',cuts:[60]}));
assert(C.set('drought',{count:5,method:'quantile',cuts:[]}));
const P=C.build('poverty',st), D=C.build('drought',st);
assert.deepEqual(Array.from(P.counts),[6,4]);
assert.equal(P.mapKey(cells[5],'base'),'lhq0');
assert.equal(P.mapKey(cells[6],'base'),'lhq4');
assert.equal(P.high(cells[6],'base'),true);
assert.equal(D.counts.reduce((a,b)=>a+b),10);
assert.equal(D.high(cells[4],'base'),false);
assert.equal(D.high(cells[4],'ssp'),true);
assert.deepEqual(Array.from(C.build('drought',{...st,climate:'ssp'}).cuts),Array.from(D.cuts));
// Per-variable settings survive navigation; invalid edits cannot overwrite valid cuts.
assert.equal(boot().get('poverty').count,2);
assert.equal(boot().get('drought').count,5);
assert(!C.set('poverty',{count:3,method:'threshold',cuts:[80,20]}));
assert(!C.set('poverty',{count:2,method:'threshold',cuts:[NaN]}));
assert.equal(C.get('poverty').count,2);
assert(C.build('poverty',st,{count:3,method:'threshold',cuts:[80,20]}).error);
assert(C.build('poverty',{classes:{},climate:'base'}).error);
const snap=C.snapshot();assert.equal(C.restore({poverty:{count:2,method:'threshold',cuts:[200]}}),false);assert.equal(C.get('poverty').count,2);C.restore({});assert.equal(C.get('poverty').count,3);
C.restore(snap);assert.equal(C.get('poverty').count,2);
// Cross-tab refresh uses storage without resetting other page state.
const other=boot();other.set('poverty',{count:2,method:'threshold',cuts:[80]});
C.refresh();assert.equal(C.get('poverty').cuts[0],80);
// Stale writers preserve independent settings from another tab.
const stale=boot();other.set('poverty',{count:2,method:'threshold',cuts:[70]});
stale.set('drought',{count:2,method:'threshold',cuts:[60]});
assert.equal(boot().get('poverty').cuts[0],70);
const baseSubset=C.build('drought',{classes:{vh:1},climate:'base'},{count:3,method:'quantile',cuts:[]});
const futureSubset=C.build('drought',{classes:{vh:1},climate:'ssp'},{count:3,method:'quantile',cuts:[]});
assert.notEqual(baseSubset.sample.length,futureSubset.sample.length);
assert.deepEqual(Array.from(baseSubset.cuts),Array.from(futureSubset.cuts));
// Direction flips severity, not numeric bin membership or cut points.
const forward=C.build('poverty',st,{count:5,method:'threshold',cuts:[20,40,60,80],direction:'higher_worse'});
const reverse=C.build('poverty',st,{count:5,method:'threshold',cuts:[20,40,60,80],direction:'higher_better'});
assert.equal(forward.names[0],'Best');assert.equal(reverse.names[0],'Worst');
assert.equal(forward.mapKey(cells[0],'base'),'lhq0');assert.equal(reverse.mapKey(cells[0],'base'),'lhq4');
assert.equal(reverse.classify(cells[0],'base'),forward.classify(cells[0],'base'));
assert.equal(reverse.high(cells[0],'base'),true);assert.equal(forward.high(cells[0],'base'),false);
assert.equal(reverse.high(cells[9],'base'),false);
assert.deepEqual(Array.from(reverse.order),[4,3,2,1,0]);
assert(C.set('poverty',{count:2,method:'threshold',cuts:[60],direction:'higher_better'}));
assert.equal(boot().get('poverty').direction,'higher_better');
const directionSnapshot=C.snapshot();C.restore({});C.restore(directionSnapshot);
assert.equal(C.get('poverty').direction,'higher_better');
assert(!C.set('poverty',{count:2,method:'threshold',cuts:[60],direction:'sideways'}));
// Reset only selected variable, including its direction; preserve other tabs' settings.
const resetter=boot();other.set('drought',{count:5,method:'threshold',cuts:[10,30,50,70]});
assert(resetter.reset('poverty'));assert.equal(boot().get('poverty').count,3);
assert.equal(boot().get('poverty').method,'quantile');
assert.equal(boot().get('poverty').direction,'higher_worse');
assert.equal(boot().get('drought').cuts[0],10);
assert(!resetter.reset('unknown'));
// Exact boundaries enter higher class, with no gaps in map class labels.
const E=C.build('poverty',st,{count:2,method:'threshold',cuts:[100/3]});
assert.equal(E.classify(cells[3],'base'),1);
assert.equal(E.counts.reduce((a,b)=>a+b),E.sample.length);
"""
    subprocess.run(
        [node, "-e", script, str(ROOT / "docs/redesign/v1b-classification.js")],
        check=True,
        capture_output=True,
        text=True,
    )
