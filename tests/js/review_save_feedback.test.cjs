const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('docs/dashboard.html','utf8');
let saved=[],notices=[];
const window={_vfReviewer:'Pete',_reviewApi:true,_vfClarificationFilter:'answer_ready',_vfReconcile:'unresolved'};
const ctx=vm.createContext({window,Promise,localStorage:{setItem:()=>{}},vfNotice:m=>notices.push(m),renderVfWorklist:()=>{},vfRefreshReview:async()=>{},document:{querySelector:()=>null},fetch:async(url,opt)=>{const body=JSON.parse(opt.body);saved.push([url,body]);return {ok:true,json:async()=>({ok:true,reopened:1})};}});
vm.runInContext(html.slice(html.indexOf('function setVfDecision('),html.indexOf('// A per-card DROP')),ctx);
vm.runInContext(html.slice(html.indexOf('async function reopenVf('),html.indexOf('async function challengeVf(')),ctx);
(async()=>{
 ctx.setVfDecision('one','ok');ctx.setVfDecision('two','ok');ctx.setVfDecision('one','ok');await window._vfSaveQueue;
 assert.equal(window._vfAllReviews.one.Pete.decision,'ok');assert.equal(window._vfAllReviews.two.Pete.decision,'ok');
 assert(saved.every(([,body])=>body.decision==='ok'));
 await ctx.reopenVf('one');assert.equal(window._vfClarificationFilter,'all');assert.equal(window._vfReconcile,'all');
 assert(notices.some(m=>m.includes('Record reopened')));
 ctx.fetch=async()=>({ok:false,json:async()=>({error:'disk full'})});ctx.setVfDecision('three','ok');await window._vfSaveQueue;
 assert(!window._vfAllReviews.three);assert(notices.at(-1).includes('NOT saved'));
 assert(!html.slice(html.indexOf('async function reopenVf('),html.indexOf('// Units resolved')).includes('confirm('));
 console.log('Serialized saves, idempotent repeat, visible errors and reopen filter reset passed');
})().catch(e=>{console.error(e);process.exitCode=1;});
