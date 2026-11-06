const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('docs/dashboard.html','utf8');
const row=(id,extra={})=>({evidence_id:id,nbs_id:'wetland_management',use_role:'structural_suitability',...extra});
const ev=[row('one'),row('two'),row('ordinary')];
const data={registers:{EV_evidence_register:ev},_evDropped:[],review_priorities:[{batch_id:'wetland',batch_label:'Wetland',priority:'high',evidence_id:'one',reason:'<img onerror="bad">',decision_needed:'Confirm',source_id:'paper',page:3},{batch_id:'wetland',batch_label:'Wetland',priority:'high',evidence_id:'two',context_changed:true}]};
const nodes=new Map();let renders=0,answered=new Set(),lastHash='';
const window={_vfDecisions:{one:'ok'},_vfAllReviews:{one:{Pete:{decision:'ok'}}},_vfScope:{nbs:'agroforestry',family:'wrong',sourceId:'wrong',observations:'hide'},_vfSearch:'wrong',DashboardShell:{openReviewQueue(){}}};
const context=vm.createContext({window,dashboardData:data,document:{getElementById:()=>null,querySelectorAll:()=>[]},history:{replaceState(a,b,h){lastHash=h;}},renderVfWorklist:()=>renders++,vfHasAnswerForReview:id=>answered.has(id),vfClarificationsFor:()=>[],vfNotice:()=>{},_vfR2T:{structural_suitability:'T4'}});
vm.runInContext(html.slice(html.indexOf('function vfSimpleQueue('),html.indexOf('function _vfInScope(')),context);
vm.runInContext(fs.readFileSync('docs/dashboard-priority.js','utf8'),context);
const api=window.DashboardPriority;
const decisions=JSON.stringify([window._vfDecisions,window._vfAllReviews]),original=JSON.stringify(data);
api.set('wetland');
assert.equal(window._vfScope.nbs,'wetland_management');assert.equal(window._vfScope.table,'T4');
assert.equal(window._vfScope.family,'all');assert.equal(window._vfScope.sourceId,'');assert.equal(window._vfScope.observations,'show');assert.equal(window._vfSearch,'');
assert.equal(window._vfSimpleView,'todo');assert.equal(lastHash,'#review-priority=wetland');
assert(api.matches(ev[0]));assert(!api.matches(ev[2]));
assert(api.controls().includes('Wetland (2)'));assert(api.card(ev[0]).includes('&lt;img'));assert(!api.card(ev[0]).includes('<img'));assert(api.card(ev[1]).includes('Evidence changed'));
const unit=(extra={})=>({ev:{...ev[0],_reviewQueue:'first'},me:false,meApplied:false,dropped:false,...extra});
assert(context.vfSimpleMatch(unit(),'todo'));
assert(!context.vfSimpleMatch(unit({me:true,myDec:'ok'}),'todo'));
assert(context.vfSimpleMatch(unit({me:true,myDec:'ok'}),'mine'));
assert(context.vfSimpleMatch(unit({me:true,myDec:'query'}),'waiting'));
assert(!context.vfSimpleMatch(unit({me:true,myDec:'query',meApplied:true,ev:{...ev[0],_reviewQueue:'unresolved'}}),'todo'));
assert(!context.vfSimpleMatch(unit({dropped:true}),'todo'));
assert(!context.vfSimpleMatch(unit({ev:{...ev[0],_reviewQueue:'reviewed'}}),'todo'));
api.openFromHash('#review-evidence=two');assert.equal(lastHash,'#review-evidence=two');assert.equal(window._vfSimpleView,'advanced');assert.equal(window._vfAxStatus,'any');assert(api.matches(ev[1]));assert(!api.matches(ev[0]));
api.set('high');assert(api.matches(ev[0]));assert(!api.matches(ev[2]));
api.set('all');assert(api.matches(ev[2]));
window._vfScope.nbs='agroforestry';api.openFromHash('#review-priority=high');assert.equal(window._vfScope.nbs,'wetland_management');
api.openFromHash('#review-evidence=one');api.leaveFocus();assert.equal(window._vfPriorityEvidence,'');assert.equal(lastHash,'#review-queue');
assert.equal(JSON.stringify([window._vfDecisions,window._vfAllReviews]),decisions);assert.equal(JSON.stringify(data),original);
assert(renders>0);console.log('Priority scopes, links, escaping, queue semantics and no state mutation passed.');

// Web sources carry section locators, never a fabricated PDF page.
const web=row('web');data.registers.EV_evidence_register.push(web);
data.review_priorities.push({batch_id:'web',batch_label:'Web sources',priority:'high',evidence_id:'web',source_id:'manual',page:'',source_locator:'5.3 <img onerror="bad"> > Suitability',reason:'Inspect source section',decision_needed:'Verify recommendation'});
api.set('web');
for (const markup of [api.controls(),api.card(web)]) {
  assert(markup.includes('Source location: 5.3 &lt;img'));
  assert(!markup.includes('<img onerror'));
  assert(!markup.includes('PDF p'));
}
assert(api.card(ev[0]).includes('PDF p3'));
console.log('Section locators displayed and escaped; PDF compatibility preserved.');
