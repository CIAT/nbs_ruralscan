/* v1b-versions.js — slim version bar shared by every v2 page.
   v0 = ../wireframe-v0.html (original) · v1 = ../wireframe.html (draft) · v2 = these pages. */
(function () {
  'use strict';
  var html =
    '<div class="vbar" role="region" aria-label="Mock-up versions"><div class="vb-in">' +
      '<label for="v1b-version">Version</label>' +
      '<select id="v1b-version" aria-describedby="v1b-version-note">' +
        '<option value="../wireframe-v0.html">v0 · Original</option>' +
        '<option value="../wireframe.html">v1 · Draft</option>' +
        '<option value="index.html" selected>v2 · Scoping tool</option>' +
      '</select>' +
      '<span id="v1b-version-note">v2 · NbS spatial opportunity scoping tool · example data</span>' +
      '<button type="button" class="vb-theme" id="v1b-theme" aria-pressed="false"><svg viewBox="0 0 16 16" aria-hidden="true"><path class="ic-moon" d="M11.5 10.6A5 5 0 0 1 5.4 4.5a5 5 0 1 0 6.1 6.1z"/><g class="ic-sun"><circle cx="8" cy="8" r="2.8"/><path d="M8 1.5v1.6M8 12.9v1.6M1.5 8h1.6M12.9 8h1.6M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M3.4 12.6l1.1-1.1M11.5 4.5l1.1-1.1"/></g></svg><span>Dark theme</span></button>' +
      '<details class="vb-changes"><summary>What changed? · v1 → v2</summary><ul>' +
        '<li>One question and one dominant plate per stage.</li>' +
        '<li>A visible control bar for practice, classes, view and climate.</li>' +
        '<li>Depth staged in numbered sub-tabs instead of stacked panels.</li>' +
        '<li>A coherent synthetic surface instead of tiled example values.</li>' +
        '<li>Numbered figures, tables and sections.</li>' +
        '<li>A new stage, Explore the practices, and a full technical configuration page.</li>' +
        '<li>A light and dark theme, and this version selector, shared by all three versions.</li>' +
      '</ul></details>' +
    '</div></div>';
  document.body.insertAdjacentHTML('afterbegin', html);
  var sel = document.getElementById('v1b-version');
  sel.addEventListener('change', function () {
    if (sel.value !== 'index.html') window.location.assign(new URL(sel.value, window.location.href).href);
    else if (!/\/redesign\/(index\.html)?$/.test(window.location.pathname)) window.location.assign(new URL('index.html', window.location.href).href);
  });
  window.addEventListener('pageshow', function () { sel.value = 'index.html'; });
  // theme toggle: light by default, remembered per viewer; the inline <head> script applies it before paint
  var btn = document.getElementById('v1b-theme');
  function show() {
    var dark = document.documentElement.getAttribute('data-theme') === 'dark';
    btn.setAttribute('aria-pressed', String(dark));
    btn.querySelector('span').textContent = dark ? 'Light theme' : 'Dark theme';
    btn.classList.toggle('is-dark', dark);
  }
  btn.addEventListener('click', function () {
    var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { window.localStorage.setItem('v1b-theme', next); } catch (e) { /* ignore */ }
    show();
  });
  show();
})();
