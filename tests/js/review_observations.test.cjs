const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('docs/dashboard.html','utf8');
const window={_vfScope:{nbs:'agroforestry',table:'T4'}};
const ctx=vm.createContext({window,_vfR2T:{structural_suitability:'T4',operational_risk:'T4',nbs_effect:'T3/T6'}});
vm.runInContext(html.slice(html.indexOf('function vfIsSiteObservation('),html.indexOf('// Gap rows carry')),ctx);
const row=relationship=>({nbs_id:'agroforestry',use_role:'structural_suitability',relationship});
for(const relationship of [{type:'observed_presence'},{type:'site_context'},{observed_slope_pct:[3,5]},{site_mean:950,note:'case_study_site_context'},JSON.stringify({type:'observed_presence'})]){
 const ev=row(relationship);assert(ctx.vfIsSiteObservation(ev));assert(!ctx._vfInScope(ev));
 window._vfScope.observations='show';assert(ctx._vfInScope(ev));
 window._vfScope.observations='only';assert(ctx._vfInScope(ev));
 window._vfScope.observations='hide';
}
for(const relationship of [{design:'observational',metric:'pct_change'},{type:'source_ordinal_classes'},{shape:'sigmoidal',observed_min:0},{type:'model_use_only'},'{malformed']){
 assert(ctx._vfInScope(row(relationship)));
 window._vfScope.observations='only';assert(!ctx._vfInScope(row(relationship)));window._vfScope.observations='hide';
}
assert(ctx._vfInScope({...row({design:'observational',direction:'negative'}),use_role:'operational_risk'}));
console.log('Site observations hidden by default; include/only work; relationship and operational evidence retained');
