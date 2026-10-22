const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('docs/dashboard.html', 'utf8');
const source = html.slice(html.indexOf('var _sec=function'), html.indexOf('// ---- sidebar presets'));
const list = html.slice(html.indexOf('var _list=_uni.filter'), html.indexOf('// stable seeded order'));
const units = [
  {ev:{evidence_id:'active'},origin:'passed',me:false,other:false,dropped:false},
  {ev:{evidence_id:'automatic-quarantine'},origin:'passed',me:false,other:false,dropped:true},
  {ev:{evidence_id:'human-drop'},origin:'flagged',me:true,other:true,myDec:'drop',dropped:true},
];
const window = {_vfSimpleView:"advanced",_vfAxOrigin:'any',_vfAxMe:'any',_vfAxOther:'any',_vfMyCall:'all',_vfVerdictFilter:'all'};
const ctx = vm.createContext({vfSimpleMatch:()=>true,window,_uni:units,_store:{},_vfTabular:()=>true});
vm.runInContext(source,ctx);
function ids(){vm.runInContext(list,ctx);return Array.from(ctx._list,u=>u.ev.evidence_id);}
assert.deepEqual(ids(),['active']); // Missing status defaults to active, including no-human-review quarantine.
for(const [status,expected] of [['active',1],['dropped',2],['any',3]]){
 window._vfAxStatus=status;
 assert.equal(ids().length,expected);
 assert.equal(ctx._axN('status',status),expected);
 for(const [axis,key,options] of [['origin','_vfAxOrigin',['any','flagged','passed']],['me','_vfAxMe',['any','no','yes']],['other','_vfAxOther',['any','no','yes']]]){
  for(const value of options){const count=ctx._axN(axis,value);const old=window[key];window[key]=value;assert.equal(ids().length,count);window[key]=old;}
 }
}
window._vfAxStatus='active';window._vfAxMe='no';
assert.deepEqual(ids(),['active']);
window._vfAxStatus='dropped';
assert.deepEqual(ids(),['automatic-quarantine']);
window._vfAxMe='yes';window._vfMyCall='drop';
assert.deepEqual(ids(),['human-drop']);
// A reopened row returns to the active queue without touching stored decisions.
units[1].dropped=false;window._vfAxStatus='active';window._vfAxMe='no';window._vfMyCall='all';
assert.deepEqual(ids(),['active','automatic-quarantine']);
assert(html.includes("window._vfAxStatus='active'; window._vfAxOrigin='any';"));
assert(html.includes("['dropped','Dropped history']"));
console.log('Review status: default exclusion, history, axis counts and reopen passed');
window._vfAxMe='any';window._vfAxOrigin='any';window._vfAxStatus='dropped';
units[2].verdict='mismatch';
assert.equal(ctx._axN('verdict','mismatch'),1);
window._vfVerdictFilter='mismatch';assert.deepEqual(ids(),['human-drop']);
window._vfAxStatus='active';assert.equal(ctx._axN('verdict','mismatch'),0);
window._vfVerdictFilter='all';
// Round inventory includes dropped history and scopes its counts by the selected status.
const rounds=html.slice(html.indexOf('var _rdN=function'),html.indexOf('var _rdCur='));
window._vfScope={round:'round2'};
window._vfPreScope=[{review_state:'',round:'round1'},{review_state:'dropped',round:'round2'}];
ctx._vfInScope=()=>true;ctx._vfRoundKey=e=>e.round;
vm.runInContext(rounds,ctx);
assert.equal(ctx._rdN('all'),1);assert.equal(ctx._rdN('round2'),0);
window._vfAxStatus='dropped';assert.equal(ctx._rdN('all'),1);assert.equal(ctx._rdN('round2'),1);
assert.equal(window._vfScope.round,'round2');
