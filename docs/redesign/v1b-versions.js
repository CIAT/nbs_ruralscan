/* v1b-versions.js — slim version bar shared by every atlas (v2) page.
   v0 = ../wireframe-v0.html (original) · v1 = ../wireframe.html (draft) · v2 = these pages. */
(function () {
  'use strict';
  var html =
    '<div class="vbar" role="region" aria-label="Mock-up versions"><div class="vb-in">' +
      '<label for="v1b-version">Version</label>' +
      '<select id="v1b-version" aria-describedby="v1b-version-note">' +
        '<option value="../wireframe-v0.html">v0 · Original</option>' +
        '<option value="../wireframe.html">v1 · Draft</option>' +
        '<option value="index.html" selected>v2 · Atlas</option>' +
      '</select>' +
      '<span id="v1b-version-note">v2 · atlas redesign · example data</span>' +
      '<details class="vb-changes"><summary>What changed? · v1 → v2</summary><ul>' +
        '<li>One question and one dominant plate per stage.</li>' +
        '<li>A visible control bar for practice, classes, view and climate.</li>' +
        '<li>Depth staged in numbered sub-tabs instead of stacked panels.</li>' +
        '<li>A coherent synthetic surface instead of tiled example values.</li>' +
        '<li>Numbered figures, tables and sections.</li>' +
        '<li>This version selector, shared by all three versions.</li>' +
      '</ul></details>' +
    '</div></div>';
  document.body.insertAdjacentHTML('afterbegin', html);
  var sel = document.getElementById('v1b-version');
  sel.addEventListener('change', function () {
    if (sel.value !== 'index.html') window.location.assign(new URL(sel.value, window.location.href).href);
    else if (!/\/redesign\/(index\.html)?$/.test(window.location.pathname)) window.location.assign(new URL('index.html', window.location.href).href);
  });
  window.addEventListener('pageshow', function () { sel.value = 'index.html'; });
})();
