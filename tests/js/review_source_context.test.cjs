const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('docs/dashboard.html', 'utf8');
const source = html.slice(html.indexOf('  function vfSourcePages'), html.indexOf('  // Client-side rotate'));
const ctx = {
  window: {_reviewApi: true, _cropManifest: new Set(['record'])},
  dashboardData: {registers: {EV_evidence_register: [{evidence_id: 'record', source_id: 'paper', page: 11}]}},
  document: {createElement: () => ({})},
  encodeURIComponent,
  vfClarificationsFor:()=>[], vfEsc:s=>s,
};
vm.createContext(ctx); vm.runInContext(source, ctx);
function render() {
  const box = {style: {display: 'none'}, dataset: {}, prepend: node => {box.link = node;}};
  ctx.vfToggleCrop('record', {nextElementSibling: box});
  return box;
}
const live = render();
assert(live.innerHTML.includes('/api/crop?eid=record&full=1'));
assert(!live.innerHTML.includes('crops/record.jpg'));
assert(live.innerHTML.includes('open full page'));
assert.equal(live.link.href, '/api/pdf?sid=paper#page=11');
ctx.window._reviewApi = false;
const offline = render();
assert(offline.innerHTML.includes('crops/record.jpg'));
assert(offline.innerHTML.includes('open crop'));
assert(!offline.innerHTML.includes('open full'));
console.log('Review source context: live full page and offline crop passed');
const fallbackSource = html.slice(html.indexOf('  function vfCropOnErr'), html.indexOf('  // Task 3: click a card'));
vm.runInContext(fallbackSource, ctx);
let warning;
const image = {dataset: {}, before: node => {warning = node.textContent;}};
ctx.vfCropOnErr('record', image);
assert.equal(image.src, 'crops/record.jpg');
assert(warning.includes('caption may be incomplete'));

ctx.vfClarificationsFor=()=>[{answers:[{source_check:{pdf_pages:[4,8],page_labels:{4:'Table 1 — suitability relationships',8:'Table 2 — variable weights'}}}]}];
const pages=ctx.vfSourcePages({evidence_id:'record',page:4,context:JSON.stringify({model_use:{page:'4,8'}})});
assert.deepEqual(Array.from(pages,p=>p.page),[4,8]);
assert(pages[1].label.includes('Table 2'));
let img={src:'',style:{},removeAttribute:()=>{}};
let link={href:'/api/pdf?sid=paper#page=4',getAttribute:()=>'/api/pdf?sid=paper#page=4'};
let box={dataset:{rot:'90'},querySelector:()=>img,querySelectorAll:s=>s==='a'?[link]:[]};
ctx.vfSelectSourcePage('record',8,{closest:()=>box});
assert.equal(img.src,'/api/crop?eid=record&full=1&page=8');
assert(link.href.endsWith('#page=8'));assert.equal(box.dataset.rot,'0');
ctx.vfClarificationsFor=()=>[];
ctx.window._vfClarifications=[{source:'chuma',answers:[{source_check:{pdf_pages:[5,6],page_labels:{5:'Table 2 — AHP variable weights',6:'Table 3 — suitability classes'}}}]}];
const chuma=ctx.vfSourcePages({evidence_id:'other-card',source_id:'chuma',page:6,context:{}});
assert.deepEqual(Array.from(chuma,p=>p.page),[5,6]);
assert(chuma[0].label.includes('Table 2'));
assert.equal(ctx.vfSourcePages({evidence_id:'unrelated',source_id:'elsewhere',page:2}).length,1);
