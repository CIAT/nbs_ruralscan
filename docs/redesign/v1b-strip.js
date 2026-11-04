/* v1b-strip.js — thumbnails for the seven-stage method strip (index.html, history.html).
   Needs sle_geo.js, v1b-map.js, v1b-fixture.js. Synthetic example surface only. */
(function () {
  'use strict';
  var M = window.V1BMap, F = window.FIXTURE, VB = '366 22 568 592';
  if (!M || !F || !document.getElementById('th1')) return;
  function thumb(id, key) {
    var s = M.plate(document.getElementById(id), { uid: id, labels: false, scale: false, cities: false, context: false, viewBox: VB });
    M.paintCells(s, F.cells, key); return s;
  }
  var t1 = thumb('th1', function () { return 'low'; });
  t1.querySelector('.m-cells').innerHTML = '<path d="' + M.adm0Path + '" class="k-low"/><path d="' + F.cells.map(function (c) {
    return 'M' + c.x.toFixed(1) + ' ' + c.y.toFixed(1) + 'h' + c.w.toFixed(1) + 'v' + c.h.toFixed(1);
  }).join('') + '" style="fill:none;stroke:var(--paper);stroke-width:2.2"/>';
  var R = F.rollup({});
  thumb('th2', function (c) { return c.suitClass; });
  thumb('th3', function (c) { return !R.sel(c) ? null : c.fireClass === 'high' ? 'fire' : c.fireClass === 'moderate' ? 'fire2' : 'sel'; });
  thumb('th4', function (c) { return !R.sel(c) ? null : R.hot(c) ? 'hot' : 'opp'; });
  document.getElementById('th5').innerHTML =
    '<g style="font:600 6.5px var(--f-body);fill:var(--ink-2)"><rect x="14" y="26" width="64" height="9" class="k-h"/><rect x="14" y="48" width="38" height="9" class="k-h"/>' +
    '<line x1="14" y1="74.5" x2="58" y2="74.5" style="stroke:var(--s3);stroke-width:2.2;stroke-dasharray:5 2.5"/><text x="14" y="22">Area</text><text x="14" y="44">Area</text><text x="14" y="70">Linear</text></g>';
  document.getElementById('th7').innerHTML =
    '<rect x="22" y="14" width="56" height="72" style="fill:var(--surface);stroke:var(--ink-3);stroke-width:.8"/><rect x="28" y="20" width="44" height="30" style="fill:none;stroke:var(--ink-3);stroke-width:.7;stroke-dasharray:2 1.5"/>' +
    '<path d="M34 46c6-10 10-14 16-18c4 6 8 10 14 18" style="fill:none;stroke:var(--s3);stroke-width:1.4"/><g style="stroke:var(--rule);stroke-width:2"><line x1="28" y1="58" x2="70" y2="58" style="stroke:var(--ink-2);stroke-width:2.4"/><line x1="28" y1="66" x2="72" y2="66"/><line x1="28" y1="72" x2="66" y2="72"/><line x1="28" y1="78" x2="60" y2="78"/></g>';
  document.getElementById('th6').innerHTML =
    '<rect x="28" y="16" width="44" height="64" style="fill:var(--surface);stroke:var(--ink-3);stroke-width:.8"/><g style="stroke:var(--rule);stroke-width:2.2"><line x1="35" y1="30" x2="64" y2="30" style="stroke:var(--ink-2);stroke-width:2.6"/>' +
    '<line x1="35" y1="40" x2="65" y2="40"/><line x1="35" y1="47" x2="62" y2="47"/><line x1="35" y1="54" x2="65" y2="54"/><line x1="35" y1="61" x2="47" y2="61"/></g><rect x="52" y="58" width="13" height="13" style="fill:var(--n4);opacity:.85"/><path d="M35 69l3 3 6-6" style="fill:none;stroke:var(--accent);stroke-width:1.6"/>';
})();
