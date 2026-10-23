const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('docs/dashboard.html', 'utf8');
const source = html.slice(html.indexOf('function vfRelatedTableHtml'), html.indexOf('// Review the extracted claim'));
const base = {evidence_id:'start',source_id:'paper',nbs_id:'agroforestry',variable:'soil_organic_carbon',suitability_family_id:'shared',claim_scope:'practice_technology',page:5,context:{},relationship:{classes:'low:<0.5, medium:0.5-0.7'},reviewer_ok:true};
const continuation = {...base,evidence_id:'end',page:6,context:{table_continuation_of:'start'},relationship:{classes:'high:0.7-0.75, very_high:>0.75'},reviewer_ok:false};
const rows = [continuation,base];
const ctx=vm.createContext({dashboardData:{registers:{EV_evidence_register:rows}},vfEsc:s=>String(s).replaceAll('<','&lt;'),vfRelHtml:r=>JSON.stringify(r.relationship)});
vm.runInContext(source,ctx);
for (const row of rows) {
 const rendered=ctx.vfRelatedTableHtml(row);
 assert(rendered.includes('low:<0.5')); assert(rendered.includes('very_high:>0.75'));
 assert(rendered.indexOf('Page 5')<rendered.indexOf('Page 6'));
 assert(rendered.includes('awaiting review')); assert(rendered.includes('approved extraction'));
 assert(rendered.includes('only to this record'));
}
for(const field of ['source_id','variable','suitability_family_id','claim_scope','nbs_id']) {
 const before=continuation[field]; continuation[field]='other';
 assert.equal(ctx.vfRelatedTableHtml(continuation),'');
 assert.equal(ctx.vfRelatedTableHtml(base),''); continuation[field]=before;
}
continuation.review_state='dropped'; assert.equal(ctx.vfRelatedTableHtml(base),'');
delete continuation.review_state;
rows.splice(1,1); assert.equal(ctx.vfRelatedTableHtml(continuation),'');
assert(html.includes('+vfRelatedTableHtml(ev)'));
console.log('Table continuations retain page context, scope and separate review decisions.');
