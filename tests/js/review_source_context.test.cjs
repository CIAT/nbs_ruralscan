const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('docs/dashboard.html', 'utf8');
const source = html.slice(html.indexOf('  function vfToggleCrop'), html.indexOf('  // Client-side rotate'));
const ctx = {
  window: {_reviewApi: true, _cropManifest: new Set(['record'])},
  dashboardData: {registers: {EV_evidence_register: [{evidence_id: 'record', source_id: 'paper', page: 11}]}},
  document: {createElement: () => ({})},
  encodeURIComponent,
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
