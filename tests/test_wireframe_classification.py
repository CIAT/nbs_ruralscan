"""Concern classes and weighting preview follow the adopted method, without spatial runtime writes."""

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
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
let stored={};
const cells=Array.from({length:10},(_,i)=>({ind:{poverty:i,drought:i},drought2050:i+3,residents:i+1,suitClass:i<5?'vh':'h',suitClass2050:i<3?'vh':'h'}));
cells.push({ind:{poverty:100,drought:100},excluded:true});
function boot(){const w={FIXTURE:{cells,rollup:st=>({sel:c=>!!st.classes[st.climate==='ssp'?c.suitClass2050:c.suitClass]})}};const ctx={window:w,localStorage:{getItem:k=>stored[k],setItem:(k,v)=>stored[k]=v}};vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),ctx);return w.V1BClassification;}
const st={classes:{vh:1,h:1},climate:'base'},C=boot();
const threshold={count:4,method:'threshold',cuts:[0,100/3,200/3],direction:'higher_worse'};
assert(C.set('poverty',threshold));
const P=C.build('poverty',st);
assert.deepEqual(Array.from(P.counts),[1,3,3,3]);
assert.deepEqual(Array.from(P.names),['None','Low','Medium','High']);
assert.equal(P.score(cells[0],'base'),0);
assert.equal(P.score(cells[3],'base'),0.33); // upper bound belongs to lower interval
assert.equal(P.score(cells[6],'base'),0.66);
assert.equal(P.score(cells[9],'base'),1);
assert.equal(P.score({ind:{poverty:null}},'base'),null);
assert.equal(P.mapKey({ind:{poverty:NaN}},'base'),'unknown');
assert(!P.high({ind:{}},'base'));
const reverse=C.build('poverty',st,{...threshold,direction:'higher_better'});
assert.equal(reverse.score(cells[0],'base'),1);assert.equal(reverse.score(cells[9],'base'),0);
assert.deepEqual(Array.from(reverse.cuts),Array.from(P.cuts));
assert(!C.set('poverty',{count:5,method:'quantile',cuts:[]}));
assert(!C.set('poverty',{...threshold,cuts:[70,20,80]}));
assert(!C.set('poverty',{...threshold,cuts:[0,NaN,80]}));
assert.equal(boot().get('poverty').count,4);
const relative={count:3,method:'quantile',cuts:[],direction:'higher_worse'};
const D=C.build('drought',st,relative);
assert.deepEqual(Array.from(D.cuts),[100/3,200/3]); // linear (n-1) interpolation
assert.deepEqual(Array.from(D.names),['Low','Medium','High']);
assert.equal(D.score(cells[0],'base'),0.33); // lowest tercile is never none
assert.equal(D.score(cells[3],'ssp'),0.66);
assert(C.set('drought',{...relative,reference:D.reference}));
const future=C.build('drought',{classes:{vh:1},climate:'ssp'});
assert.deepEqual(Array.from(future.cuts),Array.from(D.cuts));
assert.equal(future.reference.values.length,10); // original full reference stays fixed
assert.equal(future.sample.length,3);
assert(C.build('poverty',{classes:{},climate:'base'}).error);
const bad=JSON.parse(JSON.stringify(D.reference));bad.cuts=[10,90];
assert(!C.set('drought',{...relative,reference:bad}));
const snap=C.snapshot();C.restore({});assert.equal(C.get('poverty').method,'threshold');assert(C.restore(snap));
const stale=boot(),other=boot();other.set('poverty',{...threshold,cuts:[0,40,80]});
stale.set('drought',{...relative,reference:D.reference});assert.equal(boot().get('poverty').cuts[1],40);
assert(C.reset('poverty'));assert.equal(boot().get('poverty').count,4);assert.equal(boot().get('drought').method,'quantile');
// Old five-class preferences are preserved in the old storage key, never reused as new concern rules.
stored['v2-variable-classification']=JSON.stringify({poverty:{count:5,method:'quantile',cuts:[]}});
assert.equal(boot().get('poverty').count,4);assert(stored['v2-variable-classification']);
// Ties cannot be arbitrarily split into three classes.
cells.forEach(c=>{if(!c.excluded)c.ind.poverty=1;});assert(C.build('poverty',st,relative).error);
const context={window:{}};vm.runInNewContext(fs.readFileSync(process.argv[2],'utf8'),context);
const S=context.window.V1BPriorityPreview.score;
let out=S([1,0.33],[2,1],'included');assert.equal(out.status,'scored');assert(Math.abs(out.score-2.33/3)<1e-12);
assert.equal(out.score,out.contributions.reduce((a,b)=>a+b,0));assert.equal(out.denominator,3);
assert.equal(S([null,0.33],[0,1],'included').score,0.33);
assert.equal(S([null,0.33],[1,1],'included').status,'unknown');
assert.equal(S([1,1],[0,0],'included').status,'invalid');
assert.equal(S([1,1],[-1,2],'included').status,'invalid');
assert.equal(S([1,1],[Infinity,2],'included').status,'invalid');
assert.equal(S([1,1],[1,1],'excluded').status,'excluded');
assert.equal(S([1,1],[1,1],'unknown').status,'unknown');
assert.equal(S([1,0],[1,0],'included').score,1);
console.log('Classification and priority preview acceptance checks passed');
"""
    subprocess.run(
        [
            node,
            "-e",
            script,
            str(ROOT / "docs/redesign/v1b-classification.js"),
            str(ROOT / "docs/redesign/v1b-priority-preview.js"),
        ],
        check=True,
    )
