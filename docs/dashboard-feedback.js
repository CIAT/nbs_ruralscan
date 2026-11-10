/* ============================================================================
   review-mode.js — client-side review mode for the evidence dashboard.
   A lean port of the review pattern in Pete's ENSO Explorer: comment pins,
   text highlights, region screengrabs, a notes dashboard and exports.
   Everything lives in this viewer's browser (localStorage `nbs_dashboard_feedback`);
   nothing is sent anywhere unless the reviewer opens the GitHub issue link.
   Off by default; switched on from the dashboard header. Feedback never changes QA decisions.
   ============================================================================ */
(function () {
  'use strict';
  var KEY = 'nbs_dashboard_feedback', KEY_ON = 'nbs_dashboard_feedback_on', KEY_NAME = 'nbs_dashboard_feedback_reviewer', KEY_CLEAR_BACKUP = 'nbs_dashboard_feedback_clear_backup';
  var H2C = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
  var ISSUE_URL = 'https://github.com/CIAT/nbs_ruralscan/issues/new';
  var TYPES = ['Question', 'Suggestion', 'Error', 'Praise'], SEV = ['Low', 'Med', 'High'];
  var TARGETS = '[data-feedback-key], [data-vfeid], .evidence-card, #vf-cards > div, tbody tr, .card-container, .stat-card, .tab-content, .app-header';
  var page = (location.pathname.split('/').pop() || 'index.html');
  var mode = null, notes = load(), composer = null, h2cPromise = null;

  function validNote(n) {
    return n && typeof n === 'object' && /^[a-zA-Z0-9_-]+$/.test(n.id || '') &&
      n.page === page && TYPES.indexOf(n.type) >= 0 && SEV.indexOf(n.severity) >= 0 &&
      ['target','text','reviewer','created','tab','anchor','kind','quote','image'].every(function(k) { return typeof n[k] === 'string'; }) &&
      (!n.image || /^data:image\/(png|jpeg);base64,[A-Za-z0-9+/=]+$/.test(n.image));
  }
  function load() { try { var rows = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(rows) ? rows.filter(validNote) : []; } catch (e) { return []; } }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(notes)); } catch (e) { toast('Not saved — browser storage is full or blocked. Export notes or free space and retry.'); return false; } badge(); return true; }
  function isOn() { try { return localStorage.getItem(KEY_ON) === '1'; } catch (e) { return false; } }
  function setOn(v) { try { localStorage.setItem(KEY_ON, v ? '1' : '0'); } catch (e) { /* ignore */ } }
  function reviewer() { try { return localStorage.getItem(KEY_NAME) || window._vfReviewer || ''; } catch (e) { return ''; } }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function uid() { return 'n' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6); }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function pageTitle() { return 'Evidence dashboard'; }
  function tabParam() { var t = document.querySelector('.tab-btn.active'); return t ? t.dataset.tab : ''; }
  function isUI(n) { return !!(n && n.closest && n.closest('[data-rv-ui]')); }
  function clean(t) { return (t || '').replace(/\s+/g, ' ').trim(); }
  function context() {
    var tab = document.querySelector('.tab-btn.active');
    var tabId = tabParam();
    var scope;
    if (tabId === 'tab-qaqc') {
      var pipeline = document.getElementById('review-pipeline-panel');
      scope = pipeline && !pipeline.hidden && window.DashboardProgress && window.DashboardProgress.pipelineContext
        ? window.DashboardProgress.pipelineContext() : Object.assign({}, window._vfScope || {});
      if (!pipeline || pipeline.hidden) {
        scope.reviewPriority = window._vfPriority || 'all';
        scope.priorityEvidence = window._vfPriorityEvidence || '';
        scope.reviewQueue = window._vfSimpleView || 'todo';
      }
    }
    else if (tabId === 'tab-interrogator') scope = {
      nbs: (document.getElementById('select-nbs') || {}).value || 'all',
      family: (document.getElementById('select-family') || {}).value || 'all'
    };
    else if (window.DashboardProgress) scope = window.DashboardProgress.context(tabId);
    else scope = { nbs: 'all', family: 'all' };
    var subview = document.querySelector(tabId === 'tab-methods' ? '[data-method-view][aria-pressed="true"]' : '[data-review-view][aria-pressed="true"]');
    if (subview && (tabId === 'tab-methods' || tabId === 'tab-qaqc')) {
      scope = Object.assign({}, scope, {view: subview.dataset[tabId === 'tab-methods' ? 'methodView' : 'reviewView']});
    }
    return { tab: tab ? clean(tab.textContent) : '', scope: scope,
      build: typeof dashboardData !== 'undefined' && dashboardData ? ((dashboardData.build || {}).data_id || '') : '' };
  }
  function labelFor(e) {
    if (!e) return 'Page';
    if (e.dataset.feedbackLabel) return e.dataset.feedbackLabel;
    if (e.dataset.vfeid) return 'Evidence · ' + e.dataset.vfeid;
    if (e.matches('tr')) {
      var cell = e.querySelector('td, th');
      return clean(cell ? cell.textContent : e.textContent).slice(0, 220);
    }
    var h = e.querySelector('h1, h2, h3, h4, caption');
    return clean((e.id ? '#' + e.id + ' · ' : '') + (h ? h.textContent : e.textContent)).slice(0, 220);
  }
  function targetOf(n) {
    if (!n || n.nodeType !== 1) n = n && n.parentElement;
    if (!n || isUI(n)) return null;
    return n.closest(TARGETS) || document.querySelector('main') || document.body;
  }
  function targetKey(e) {
    if (!e) return '';
    return e.dataset.feedbackKey || (e.dataset.vfeid ? 'evidence:' + e.dataset.vfeid : '') ||
      (e.id ? 'id:' + e.id : ((e.closest('table') || {}).id || '') + ':' + labelFor(e));
  }
  function contextLabel(c) {
    if (!c) return '';
    var scope = c.scope || {};
    return [c.tab, scope.nbs, scope.family, scope.table].filter(function(x) {
      return x && x !== 'all';
    }).join(' · ').replace(/__/g, ' / ').replace(/_/g, ' ');
  }
  function anchorId(e) { var a = e; while (a && !a.id) a = a.parentElement; return a && a.id && !/^rv-/.test(a.id) ? a.id : ''; }
  // Only migrate notes with an explicit stable source identity. Text matches are unsafe.
  function noteTab(n) {
    if (n.targetKey && n.targetKey.indexOf('source:') === 0) return 'tab-stocktake';
    if (n.targetKey && (n.targetKey.indexOf('ledger:') === 0 || n.targetKey === 'id:dp-ledger')) return 'tab-qaqc';
    return n.tab;
  }
  function findTarget(n) {
    var targetTab = noteTab(n);
    if (n.page !== page || (targetTab && targetTab !== tabParam())) return null;
    var cands = document.querySelectorAll(TARGETS);
    for (var i = 0; i < cands.length; i++) if ((n.targetKey ? targetKey(cands[i]) === n.targetKey : labelFor(cands[i]) === n.target) && !isUI(cands[i])) return cands[i];
    return null; // Never attach a stale note to an unrelated parent or another filtered row.
  }

  /* ---------- UI shell ---------- */
  var ui = {};
  function build() {
    var fab = el('div', 'rv-fab'); fab.id = 'rv-fab'; fab.setAttribute('data-rv-ui', ''); fab.setAttribute('data-html2canvas-ignore', '');
    fab.innerHTML =
      btn('comment', 'Comment', '<path d="M4 5h16v11H9l-5 4z"/>') +
      btn('highlight', 'Highlight', '<path d="M4 20h6M14.5 4.5l5 5L10 19H5v-5z"/>', 'rv-desk') +
      btn('grab', 'Screengrab', '<path d="M4 8V4h4M16 4h4v4M20 16v4h-4M8 20H4v-4"/><rect x="8" y="8" width="8" height="8" rx="1"/>', 'rv-desk') +
      btn('notes', 'Notes', '<path d="M6 3h9l4 4v14H6z"/><path d="M9 11h7M9 15h7"/>', '', '<span class="rv-badge" id="rv-badge">0</span>') +
      btn('export', 'Export', '<path d="M12 3v12M7 10l5 5 5-5"/><path d="M4 19h16"/>');
    document.body.appendChild(fab);
    function btn(k, label, path, cls, extra) { return '<button type="button" class="rv-btn ' + (cls || '') + '" data-rv="' + k + '" title="' + label + '"><svg viewBox="0 0 24 24" aria-hidden="true">' + path + '</svg><span>' + label + '</span>' + (extra || '') + '</button>'; }
    var banner = el('div', 'rv-banner'); banner.id = 'rv-banner'; banner.setAttribute('data-rv-ui', ''); banner.setAttribute('data-html2canvas-ignore', ''); banner.hidden = true;
    banner.innerHTML = '<span id="rv-banner-t"></span><button type="button" data-rv="exit">Exit (Esc)</button>';
    document.body.appendChild(banner);
    var layer = el('div', 'rv-layer'); layer.id = 'rv-layer'; layer.setAttribute('data-rv-ui', ''); layer.setAttribute('data-html2canvas-ignore', '');
    document.body.appendChild(layer);
    var tip = el('div', 'rv-tip'); tip.id = 'rv-tip'; tip.setAttribute('data-rv-ui', ''); tip.hidden = true; document.body.appendChild(tip);
    var grab = el('div', 'rv-grab'); grab.id = 'rv-grab'; grab.setAttribute('data-rv-ui', ''); grab.setAttribute('data-html2canvas-ignore', ''); grab.hidden = true;
    grab.innerHTML = '<div class="rv-grab-box" id="rv-grab-box"></div>'; document.body.appendChild(grab);
    var menu = el('div', 'rv-menu'); menu.id = 'rv-menu'; menu.setAttribute('data-rv-ui', ''); menu.hidden = true;
    menu.innerHTML = '<button type="button" data-rv="json">Download notes (JSON)</button><button type="button" data-rv="report">Download report (HTML, with images)</button><button type="button" data-rv="issue">Submit as GitHub issue…</button><label class="rv-imp">Import notes (JSON)<input type="file" accept=".json,application/json" data-rv="import"></label>';
    document.body.appendChild(menu);
    var drawer = el('aside', 'rv-drawer'); drawer.id = 'rv-drawer'; drawer.setAttribute('data-rv-ui', ''); drawer.setAttribute('data-html2canvas-ignore', ''); drawer.setAttribute('aria-label', 'Review notes'); drawer.hidden = true;
    document.body.appendChild(drawer);
    var toastEl = el('div', 'rv-toast'); toastEl.id = 'rv-toast'; toastEl.setAttribute('data-rv-ui', ''); toastEl.hidden = true; document.body.appendChild(toastEl);
    ui = { fab: fab, banner: banner, layer: layer, tip: tip, grab: grab, menu: menu, drawer: drawer, toast: toastEl };
  }
  function toast(t) { if (!ui.toast) return; ui.toast.textContent = t; ui.toast.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(function () { ui.toast.hidden = true; }, 3200); }
  function badge() { var b = document.getElementById('rv-badge'); if (b) { b.textContent = notes.length; b.style.display = notes.length ? '' : 'none'; } }

  /* ---------- toggle in the version bar ---------- */
  function addToggle() {
    var bar = document.querySelector('.header-actions');
    var t = el('button', 'vb-review'); t.type = 'button'; t.id = 'rv-toggle'; t.setAttribute('aria-pressed', 'false'); t.setAttribute('data-rv-ui', '');
    t.title = 'Comment, highlight or capture dashboard feedback';
    t.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 3h12v8H6l-4 3z"/></svg><span>Feedback</span>';
    if (bar) { var ch = bar.querySelector('.vb-changes'); bar.insertBefore(t, ch || null); }
    else { t.classList.add('rv-float-toggle'); document.body.appendChild(t); }
    t.addEventListener('click', function () { enable(!document.body.classList.contains('rv-on')); });
  }
  function enable(on) {
    setOn(on);
    document.body.classList.toggle('rv-on', on);
    var t = document.getElementById('rv-toggle'); if (t) { t.setAttribute('aria-pressed', String(on)); t.querySelector('span').textContent = on ? 'Feedback on' : 'Feedback'; }
    if (on) { pins(); paintHighlights(); toast('Feedback on — notes stay in this browser until exported. QA decisions are separate.'); }
    else { exitModes(); closeComposer(); ui.drawer.hidden = true; ui.menu.hidden = true; ui.tip.hidden = true; if (window.CSS && CSS.highlights) CSS.highlights.delete('rv'); }
  }
  function loadH2C() {
    if (window.html2canvas) return Promise.resolve(window.html2canvas);
    if (h2cPromise) return h2cPromise;
    h2cPromise = new Promise(function (res, rej) { var s = document.createElement('script'); s.src = H2C; s.onload = function () { res(window.html2canvas); }; s.onerror = function () { h2cPromise = null; rej(new Error('html2canvas failed to load')); }; document.head.appendChild(s); });
    return h2cPromise;
  }

  /* ---------- modes ---------- */
  var BANNER = { comment: 'Comment mode: click any figure, table, card or section', highlight: 'Highlight mode: select text to save it as a highlight', grab: 'Screengrab mode: drag a box over any part of the page' };
  function setMode(m) {
    exitModes(true);
    if (!m) return;
    mode = m; document.body.classList.add('rv-mode-' + m);
    ui.banner.hidden = false; document.getElementById('rv-banner-t').textContent = BANNER[m];
    ui.fab.querySelectorAll('[data-rv]').forEach(function (b) { b.classList.toggle('on', b.getAttribute('data-rv') === m); });
    if (m === 'grab') ui.grab.hidden = false;
  }
  function exitModes(keepBanner) {
    if (mode) document.body.classList.remove('rv-mode-' + mode);
    mode = null; if (!keepBanner) ui.banner.hidden = true; else ui.banner.hidden = true;
    ui.grab.hidden = true; document.getElementById('rv-grab-box').style.display = 'none';
    ui.fab.querySelectorAll('.rv-btn').forEach(function (b) { b.classList.remove('on'); });
    var hv = document.querySelector('.rv-hover'); if (hv) hv.classList.remove('rv-hover');
  }

  /* comment-mode hover + click (capture phase so page controls do not fire) */
  document.addEventListener('mouseover', function (e) {
    if (mode !== 'comment' || isUI(e.target)) return;
    var t = targetOf(e.target), hv = document.querySelector('.rv-hover');
    if (hv && hv !== t) hv.classList.remove('rv-hover');
    if (t) t.classList.add('rv-hover');
  }, true);
  document.addEventListener('click', function (e) {
    if (mode !== 'comment' || isUI(e.target)) return;
    e.preventDefault(); e.stopPropagation();
    var t = targetOf(e.target); if (!t) return;
    t.classList.remove('rv-hover');
    openComposer({ target: t });
    exitModes();
  }, true);
  document.addEventListener('mouseup', function (e) {
    if (mode !== 'highlight' || isUI(e.target)) return;
    var sel = window.getSelection(), q = sel ? clean(sel.toString()) : '';
    if (q.length < 2) return;
    var t = targetOf(sel.anchorNode);
    openComposer({ target: t, quote: q.slice(0, 600), kind: 'highlight' });
    exitModes();
  }, true);

  /* screengrab drag */
  (function () {
    var start = null;
    document.addEventListener('mousedown', function (e) {
      if (mode !== 'grab' || e.target !== ui.grab) return;
      e.preventDefault(); start = { x: e.clientX, y: e.clientY };
      var b = document.getElementById('rv-grab-box'); b.style.display = 'block'; b.style.left = start.x + 'px'; b.style.top = start.y + 'px'; b.style.width = b.style.height = '0px';
    });
    document.addEventListener('mousemove', function (e) {
      if (!start) return;
      var b = document.getElementById('rv-grab-box'), x = Math.min(start.x, e.clientX), y = Math.min(start.y, e.clientY);
      b.style.left = x + 'px'; b.style.top = y + 'px'; b.style.width = Math.abs(e.clientX - start.x) + 'px'; b.style.height = Math.abs(e.clientY - start.y) + 'px';
    });
    document.addEventListener('mouseup', function (e) {
      if (!start) return;
      var r = { x: Math.min(start.x, e.clientX), y: Math.min(start.y, e.clientY), w: Math.abs(e.clientX - start.x), h: Math.abs(e.clientY - start.y) };
      start = null;
      if (r.w < 8 || r.h < 8) { document.getElementById('rv-grab-box').style.display = 'none'; return; }
      grabRect(r);
    });
  })();
  function grabRect(r) {
    exitModes();
    var under = document.elementFromPoint(r.x + r.w / 2, r.y + r.h / 2);
    var t = targetOf(under);
    toast('Capturing…');
    return capture(r).then(function (img) { openComposer({ target: t, image: img, kind: 'grab' }); })
      .catch(function () { toast('Screengrab failed (could not load html2canvas). You can still save a note without an image.'); openComposer({ target: t, kind: 'grab' }); });
  }
  /* html2canvas 1.4.1 cannot parse modern colour functions (color-mix → color(srgb …)).
     In the cloned document, resolve every such computed colour to rgb() via a 1px canvas. */
  var COLOR_PROPS = ['color', 'background-color', 'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color', 'outline-color', 'fill', 'stroke', 'text-decoration-color', 'column-rule-color'];
  function toRgb(v, cache, ctx) {
    if (cache[v]) return cache[v];
    ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = '#000'; ctx.fillStyle = v; ctx.fillRect(0, 0, 1, 1);
    var d = ctx.getImageData(0, 0, 1, 1).data;
    return (cache[v] = 'rgba(' + d[0] + ',' + d[1] + ',' + d[2] + ',' + (d[3] / 255).toFixed(3) + ')');
  }
  function flattenColours(doc) {
    var cv = doc.createElement('canvas'); cv.width = cv.height = 1;
    var ctx = cv.getContext('2d', { willReadFrequently: true }), cache = {}, win = doc.defaultView;
    var all = doc.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
      var e = all[i], cs = win.getComputedStyle(e);
      for (var k = 0; k < COLOR_PROPS.length; k++) {
        var v = cs.getPropertyValue(COLOR_PROPS[k]);
        if (v && (v.indexOf('color(') >= 0 || v.indexOf('color-mix') >= 0 || v.indexOf('oklch') >= 0 || v.indexOf('oklab') >= 0)) e.style.setProperty(COLOR_PROPS[k], toRgb(v, cache, ctx), 'important');
      }
      var bi = cs.getPropertyValue('background-image');
      if (bi && bi !== 'none' && /color\(|color-mix|okl/.test(bi)) e.style.setProperty('background-image', 'none', 'important');
      var sh = cs.getPropertyValue('box-shadow');
      if (sh && /color\(|color-mix|okl/.test(sh)) e.style.setProperty('box-shadow', 'none', 'important');
    }
  }
  function capture(r) {
    return loadH2C().then(function (h2c) {
      return h2c(document.body, { useCORS: true, logging: false, scale: 1, x: r.x + window.scrollX, y: r.y + window.scrollY, width: r.w, height: r.h, scrollX: 0, scrollY: 0,
        onclone: flattenColours,
        ignoreElements: function (n) { return n.hasAttribute && (n.hasAttribute('data-html2canvas-ignore') || n.hasAttribute('data-rv-ui')); } });
    }).then(function (canvas) {
      var max = 960, c = canvas;
      if (canvas.width > max || canvas.height > max) {
        var k = Math.min(max / canvas.width, max / canvas.height); c = document.createElement('canvas');
        c.width = Math.round(canvas.width * k); c.height = Math.round(canvas.height * k); c.getContext('2d').drawImage(canvas, 0, 0, c.width, c.height);
      }
      return c.toDataURL('image/jpeg', 0.85);
    });
  }

  /* ---------- composer ---------- */
  function openComposer(o) {
    closeComposer();
    var existing = o.note || null, t = o.target || (existing && findTarget(existing));
    var label = existing ? existing.target : labelFor(t);
    var name = reviewer();
    var c = el('div', 'rv-composer'); c.setAttribute('data-rv-ui', ''); c.setAttribute('data-html2canvas-ignore', ''); c.setAttribute('role', 'dialog'); c.setAttribute('aria-label', 'Review note');
    var type = existing ? existing.type : (o.kind === 'grab' ? 'Error' : 'Suggestion'), sev = existing ? existing.severity : 'Med';
    var quote = existing ? existing.quote : o.quote, image = existing ? existing.image : o.image;
    c.innerHTML =
      '<div class="rv-c-head"><div><span class="rv-c-k">' + (existing ? 'Edit note' : o.kind === 'highlight' ? 'Highlight' : o.kind === 'grab' ? 'Screengrab' : 'Comment') + '</span><div class="rv-c-t">' + esc(label) + '</div></div><button type="button" class="rv-x" data-c="close" aria-label="Close">×</button></div>' +
      (quote ? '<blockquote class="rv-q">' + esc(quote) + '</blockquote>' : '') +
      (image ? '<img class="rv-img" alt="Screengrab" src="' + image + '">' : '') +
      '<div class="rv-c-body"><p class="rv-as">Saved in this browser only. Export or open a GitHub issue to share. This does not submit a QA decision.</p>' +
      (name && !existing ? '<p class="rv-as">As <b>' + esc(name) + '</b> · <button type="button" class="rv-link" data-c="rename">change</button></p><input type="hidden" id="rv-name" value="' + esc(name) + '">'
        : '<label class="rv-f"><span>Your name</span><input type="text" id="rv-name" value="' + esc(existing ? existing.reviewer : name) + '" placeholder="Shown on every note"></label>') +
      '<label class="rv-f"><span>' + (o.kind === 'highlight' ? 'Note (optional)' : 'Comment') + '</span><textarea id="rv-text" rows="4" placeholder="What is unclear, wrong or worth keeping?">' + esc(existing ? existing.text : '') + '</textarea></label>' +
      '<div class="rv-f"><span>Type</span><div class="rv-seg" data-g="type">' + TYPES.map(function (x) { return '<button type="button" data-v="' + x + '" aria-pressed="' + (x === type) + '">' + x + '</button>'; }).join('') + '</div></div>' +
      '<div class="rv-f"><span>Severity</span><div class="rv-seg" data-g="sev">' + SEV.map(function (x) { return '<button type="button" data-v="' + x + '" aria-pressed="' + (x === sev) + '">' + x + '</button>'; }).join('') + '</div></div>' +
      '</div><div class="rv-c-foot"><span class="rv-c-page">' + esc(pageTitle(existing ? existing.page : page)) + '</span><button type="button" class="rv-b2" data-c="close">Cancel</button><button type="button" class="rv-b1" data-c="save">Save note</button></div>';
    document.body.appendChild(c); composer = c;
    // place: next to the target, clamped to the viewport
    var w = Math.min(360, window.innerWidth - 24), x = window.innerWidth - w - 16, y = 80;
    if (t && t.getBoundingClientRect) { var r = t.getBoundingClientRect(); x = Math.min(window.innerWidth - w - 12, Math.max(12, r.right - w - 12)); y = Math.max(70, Math.min(window.innerHeight - 460, r.top + 12)); }
    c.style.width = w + 'px'; c.style.left = x + 'px'; c.style.top = y + 'px';
    c.addEventListener('click', function (e) {
      var b = e.target.closest('[data-c]'), sb = e.target.closest('.rv-seg button');
      if (sb) { sb.parentNode.querySelectorAll('button').forEach(function (z) { z.setAttribute('aria-pressed', z === sb); }); return; }
      if (!b) return;
      var a = b.getAttribute('data-c');
      if (a === 'close') closeComposer();
      if (a === 'rename') { var p = b.closest('.rv-as'); p.outerHTML = '<label class="rv-f"><span>Your name</span><input type="text" id="rv-name" value="' + esc(reviewer()) + '"></label>'; var h = c.querySelector('input[type=hidden]#rv-name'); if (h) h.remove(); }
      if (a === 'save') {
        var nm = clean(c.querySelector('#rv-name').value), txt = c.querySelector('#rv-text').value.trim();
        if (!nm) { c.querySelector('#rv-name').focus(); toast('Add your name once — it is remembered.'); return; }
        if (!txt && o.kind !== 'highlight' && !(existing && existing.kind === 'highlight')) { c.querySelector('#rv-text').focus(); return; }
        try { localStorage.setItem(KEY_NAME, nm); } catch (err) { /* ignore */ }
        var tv = c.querySelector('[data-g=type] [aria-pressed=true]').getAttribute('data-v'), sv = c.querySelector('[data-g=sev] [aria-pressed=true]').getAttribute('data-v');
        if (existing) { existing.text = txt; existing.type = tv; existing.severity = sv; existing.reviewer = nm; existing.edited = new Date().toISOString(); }
        else notes.push({ id: uid(), page: page, pageTitle: document.title, tab: tabParam(), context: context(), targetKey: targetKey(t), target: label, anchor: t ? anchorId(t) : '', kind: o.kind || 'comment',
          quote: quote || '', image: image || '', text: txt, type: tv, severity: sv, reviewer: nm, created: new Date().toISOString() });
        if (!save()) { notes = load(); return; } closeComposer(); pins(); paintHighlights(); if (!ui.drawer.hidden) renderDrawer();
        toast('Note saved (' + notes.length + ' in total).');
      }
    });
    var ta = c.querySelector('#rv-text'); if (ta) setTimeout(function () { (c.querySelector('input#rv-name[type=text]') && !c.querySelector('input#rv-name').value ? c.querySelector('input#rv-name') : ta).focus(); }, 0);
  }
  function closeComposer() { if (composer) { composer.remove(); composer = null; } }

  /* ---------- pins + highlights ---------- */
  function pins() {
    if (!ui.layer) return;
    var mine = notes.filter(function (n) { return n.page === page; }), html = '', seen = {};
    mine.forEach(function (n, i) {
      var t = findTarget(n); if (!t || !t.offsetParent && t !== document.body) return;
      var r = t.getBoundingClientRect(), key = Math.round(r.top) + ',' + Math.round(r.right), off = (seen[key] = (seen[key] || 0) + 1) - 1;
      var fixed = !!t.closest('#chrome');
      var header = document.querySelector('.app-header');
      var ch = header ? header.getBoundingClientRect().bottom : 0;
      if (!fixed && (r.top + 6 < ch || r.bottom < ch + 10)) return;   // tucked under the sticky bars
      var top = r.top + (fixed ? 0 : window.scrollY) + 6, left = r.right + (fixed ? 0 : window.scrollX) - 28 - off * 26;
      html += '<button type="button" class="rv-pin rv-' + n.type.toLowerCase() + (fixed ? ' rv-fixed' : '') + '" data-id="' + n.id + '" style="top:' + top + 'px;left:' + left + 'px">' + (notes.indexOf(n) + 1) + '</button>';
    });
    ui.layer.innerHTML = html;
  }
  var pinRaf = 0;
  window.addEventListener('scroll', function () { if (!document.body.classList.contains('rv-on')) return; cancelAnimationFrame(pinRaf); pinRaf = requestAnimationFrame(pins); }, { passive: true });
  window.addEventListener('resize', function () { if (document.body.classList.contains('rv-on')) pins(); });
  document.addEventListener('click', function (e) { if (document.body.classList.contains('rv-on') && (e.target.closest('.tab-btn, .pill-btn') || e.target.closest('summary'))) setTimeout(pins, 60); });
  document.addEventListener('mouseover', function (e) {
    var p = e.target.closest && e.target.closest('.rv-pin'); if (!p) { if (ui.tip && !ui.tip.hidden && !e.target.closest('.rv-tip')) ui.tip.hidden = true; return; }
    var n = notes.filter(function (x) { return x.id === p.getAttribute('data-id'); })[0]; if (!n) return;
    ui.tip.innerHTML = '<b>' + esc(n.type) + ' · ' + esc(n.severity) + '</b> — ' + esc(n.reviewer) + '<br>' + esc(n.text || (n.quote ? '“' + n.quote + '”' : '')) + (n.image ? '<br><i>with screengrab</i>' : '');
    var r = p.getBoundingClientRect(); ui.tip.hidden = false;
    ui.tip.style.left = Math.max(8, Math.min(window.innerWidth - 300, r.left - 260)) + 'px'; ui.tip.style.top = (r.bottom + 6) + 'px';
  });
  document.addEventListener('click', function (e) {
    var p = e.target.closest && e.target.closest('.rv-pin'); if (!p) return;
    e.preventDefault(); e.stopPropagation();
    var n = notes.filter(function (x) { return x.id === p.getAttribute('data-id'); })[0]; if (n) openComposer({ note: n });
  }, true);
  function paintHighlights() {
    if (!(window.CSS && CSS.highlights && window.Highlight)) return;
    var ranges = [];
    notes.filter(function (n) { return n.page === page && n.kind === 'highlight' && n.quote; }).forEach(function (n) {
      var root = findTarget(n) || document.body, walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT), node, q = n.quote.slice(0, 120);
      while ((node = walker.nextNode())) { var i = node.textContent.indexOf(q.split(' ').slice(0, 6).join(' ')); if (i >= 0) { var rg = document.createRange(); rg.setStart(node, i); rg.setEnd(node, Math.min(node.textContent.length, i + q.length)); ranges.push(rg); break; } }
    });
    var hl = new Highlight(); ranges.forEach(function (rg) { hl.add(rg); }); CSS.highlights.set('rv', hl);
  }

  /* ---------- notes drawer ---------- */
  var filt = { page: page, type: '', sev: '' };
  function renderDrawer() {
    var pages = []; notes.forEach(function (n) { if (pages.indexOf(n.page) < 0) pages.push(n.page); });
    if (filt.page && filt.page !== '*' && pages.indexOf(filt.page) < 0) pages.push(filt.page);
    var list = notes.filter(function (n) { return (filt.page === '*' || n.page === filt.page) && (!filt.type || n.type === filt.type) && (!filt.sev || n.severity === filt.sev); });
    ui.drawer.innerHTML =
      '<div class="rv-d-head"><div><span class="rv-c-k">Review notes</span><h2>' + notes.length + ' note' + (notes.length === 1 ? '' : 's') + ' on the dashboard</h2></div><button type="button" class="rv-x" data-d="close" aria-label="Close">×</button></div>' +
      '<div class="rv-d-filt"><label>Page<select data-f="page"><option value="*">All pages</option>' + pages.map(function (p) { return '<option value="' + esc(p) + '"' + (filt.page === p ? ' selected' : '') + '>' + esc(pageTitle(p)) + '</option>'; }).join('') + '</select></label>' +
      '<label>Type<select data-f="type"><option value="">All</option>' + TYPES.map(function (x) { return '<option' + (filt.type === x ? ' selected' : '') + '>' + x + '</option>'; }).join('') + '</select></label>' +
      '<label>Severity<select data-f="sev"><option value="">All</option>' + SEV.map(function (x) { return '<option' + (filt.sev === x ? ' selected' : '') + '>' + x + '</option>'; }).join('') + '</select></label></div>' +
      '<ol class="rv-list">' + (list.length ? list.map(function (n) {
        return '<li data-id="' + n.id + '"><div class="rv-l-top"><span class="rv-num rv-' + n.type.toLowerCase() + '">' + (notes.indexOf(n) + 1) + '</span><span class="rv-l-t">' + esc(n.target) + '</span></div>' +
          '<div class="rv-l-meta">' + esc(pageTitle(n.page)) + ' · <span class="rv-tag">' + esc(n.type) + '</span><span class="rv-tag rv-sev-' + n.severity.toLowerCase() + '">' + esc(n.severity) + '</span> · ' + esc(n.reviewer) + ' · ' + new Date(n.created).toLocaleString('en-GB', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) + '</div>' +
          (n.context ? '<p class="rv-l-meta">' + esc(contextLabel(n.context)) + '</p>' : '') + (n.quote ? '<blockquote class="rv-q">' + esc(n.quote) + '</blockquote>' : '') + (n.text ? '<p class="rv-l-x">' + esc(n.text) + '</p>' : '') + (n.image ? '<img class="rv-img" alt="Screengrab" src="' + n.image + '">' : '') +
          '<div class="rv-l-act"><button type="button" data-a="jump">Jump to target</button><button type="button" data-a="edit">Edit</button><button type="button" data-a="del">Delete</button></div></li>';
      }).join('') : '<li class="rv-empty">No notes match these filters. Switch on Comment mode and click any figure, table or section.</li>') + '</ol>' +
      '<div class="rv-d-manage"><button type="button" class="rv-b2" data-rv="clear-all"' + (notes.length ? '' : ' disabled') + '>Clear all feedback…</button>' + (clearedNotes().length ? '<button type="button" class="rv-b2" data-rv="restore-cleared">Restore cleared notes</button>' : '') + '</div>' +
      '<div class="rv-d-foot"><button type="button" class="rv-b2" data-rv="json">JSON</button><button type="button" class="rv-b2" data-rv="report">Report (HTML)</button><button type="button" class="rv-b1" data-rv="issue">GitHub issue…</button></div>';
  }
  function clearedNotes() {
    try { var saved = JSON.parse(localStorage.getItem(KEY_CLEAR_BACKUP) || '[]'); return Array.isArray(saved) ? saved.filter(validNote) : []; } catch (e) { return []; }
  }
  function clearAll() {
    notes = load(); // Include notes saved by another dashboard tab.
    if (!notes.length) return;
    if (!window.confirm('Clear all ' + notes.length + ' feedback notes in this browser, including notes hidden by filters? You can restore this batch with Restore cleared notes. This replaces any previous clear-all backup. QA decisions and exported reports are unaffected.')) return;
    try { localStorage.setItem(KEY_CLEAR_BACKUP, JSON.stringify(notes)); }
    catch (e) { toast('Could not save a recovery backup. Nothing cleared. Export notes or free browser storage, then retry.'); return; }
    notes = [];
    if (!save()) { notes = load(); return; }
    renderDrawer(); pins(); paintHighlights();
    toast('Feedback cleared. Restore cleared notes is available in Notes.');
  }
  function restoreCleared() {
    notes = load(); // Preserve newer notes saved by another dashboard tab.
    var saved = clearedNotes();
    if (!saved.length) return;
    var current = new Set(notes.map(function (n) { return n.id; }));
    notes = notes.concat(saved.filter(function (n) { return !current.has(n.id); }));
    if (!save()) { notes = load(); return; }
    try { localStorage.removeItem(KEY_CLEAR_BACKUP); } catch (e) { /* Restoring again is idempotent. */ }
    filt = { page: page, type: '', sev: '' };
    renderDrawer(); pins(); paintHighlights();
    toast('Cleared feedback restored. Newer notes were kept.');
  }
  function openDrawer() { ui.menu.hidden = true; renderDrawer(); ui.drawer.hidden = false; }
  document.addEventListener('change', function (e) {
    var f = e.target.closest('[data-f]'); if (f && isUI(f)) { filt[f.getAttribute('data-f')] = f.value; renderDrawer(); return; }
    var imp = e.target.closest('[data-rv=import]'); if (imp) importFile(imp.files[0]);
  });
  document.addEventListener('click', function (e) {
    if (!isUI(e.target)) { if (ui.menu && !ui.menu.hidden && !e.target.closest('.rv-menu')) ui.menu.hidden = true; return; }
    var a = e.target.closest('[data-a]'), d = e.target.closest('[data-d]'), r = e.target.closest('[data-rv]');
    if (d) { ui.drawer.hidden = true; return; }
    if (a) {
      var id = a.closest('li').getAttribute('data-id'), n = notes.filter(function (x) { return x.id === id; })[0], act = a.getAttribute('data-a');
      if (act === 'del') { if (window.confirm('Delete this note? This cannot be undone.')) { notes = notes.filter(function (x) { return x.id !== id; }); if (!save()) notes = load(); renderDrawer(); pins(); paintHighlights(); } }
      if (act === 'edit') openComposer({ note: n });
      if (act === 'jump') jump(n);
      return;
    }
    if (!r || r.tagName === 'INPUT') return;
    var k = r.getAttribute('data-rv');
    if (k === 'comment' || k === 'highlight' || k === 'grab') { setMode(mode === k ? null : k); if (!mode) ui.banner.hidden = true; return; }
    if (k === 'exit') { exitModes(); return; }
    if (k === 'notes') { if (ui.drawer.hidden) openDrawer(); else ui.drawer.hidden = true; return; }
    if (k === 'export') { ui.menu.hidden = !ui.menu.hidden; return; }
    ui.menu.hidden = true;
    if (k === 'json') download('nbs-dashboard-feedback-notes-' + today() + '.json', JSON.stringify({ kind: 'nbs_dashboard_feedback', exported: new Date().toISOString(), notes: notes }, null, 2), 'application/json');
    if (k === 'report') download('nbs-dashboard-feedback-report-' + today() + '.html', buildReport(), 'text/html');
    if (k === 'issue') issueDialog();
    if (k === 'clear-all') clearAll();
    if (k === 'restore-cleared') restoreCleared();
  });
  function jump(n) {
    var targetTab = noteTab(n);
    if (n.page !== page) { location.href = n.page + (targetTab ? '?tab=' + targetTab : '') + '#rv=' + n.id; return; }
    if (targetTab) { var tb = Array.from(document.querySelectorAll('.tab-btn')).find(function(b) { return b.dataset.tab === targetTab; }); if (tb && !tb.classList.contains('active')) tb.click(); }
    var scope = n.context && n.context.scope || {};
    if (window.DashboardShell) {
      if (targetTab === 'tab-methods') {
        if (window.DashboardProgress && window.DashboardProgress.restoreMethodsContext) window.DashboardProgress.restoreMethodsContext(scope);
        window.DashboardShell.openMethods(scope.view || 'search');
      }
      if (targetTab === 'tab-qaqc' && scope.view === 'help') window.DashboardShell.openReviewHelp();
      if (targetTab === 'tab-qaqc' && scope.view === 'pipeline') {
        if (window.DashboardProgress && window.DashboardProgress.restorePipelineContext) window.DashboardProgress.restorePipelineContext(scope);
        window.DashboardShell.openPipelineRecords();
      }
      if (targetTab === 'tab-qaqc' && scope.view === 'queue') {
        window._vfScope = Object.assign({}, scope);
        window._vfPriority = scope.reviewPriority || 'all';
        window._vfPriorityEvidence = scope.priorityEvidence || '';
        if (scope.priorityEvidence && window.DashboardPriority) {
          window.DashboardPriority.openFromHash('#review-evidence=' + encodeURIComponent(scope.priorityEvidence));
        } else if (typeof vfSimpleQueue === 'function') vfSimpleQueue(scope.reviewQueue || 'todo');
        var queue = document.querySelector('[data-review-view="queue"]'); if (queue) queue.click();
      }
    }
    if (n.targetKey && window.DashboardProgress && window.DashboardProgress.revealTarget) {
      window.DashboardProgress.revealTarget(n.targetKey);
    }
    setTimeout(function () {
      var t = findTarget(n); if (!t) { toast('Target is not visible. Restore the saved practice/filter context shown in the note.'); return; }
      t.scrollIntoView({ behavior: 'smooth', block: 'center' }); t.classList.add('rv-flash'); setTimeout(function () { t.classList.remove('rv-flash'); }, 1600); pins();
    }, 80);
  }
  function today() { return new Date().toISOString().slice(0, 10); }
  function download(name, text, typeStr) {
    var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: typeStr })); a.download = name;
    document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }
  function importFile(f) {
    if (!f) return; if (f.size > 10000000) { toast('Import is too large (maximum 10 MB).'); return; } var rd = new FileReader();
    rd.onload = function () {
      try {
        var o = JSON.parse(rd.result), list = Array.isArray(o) ? o : o.notes, added = 0, updated = 0;
        if (!Array.isArray(list) || list.length > 2000 || !list.every(validNote)) throw new Error('invalid notes');
        list.forEach(function (n) { if (!n || !n.id) return; var i = notes.map(function (x) { return x.id; }).indexOf(n.id); if (i < 0) { notes.push(n); added++; } else { notes[i] = n; updated++; } });
        if (!save()) { notes = load(); return; } pins(); paintHighlights(); if (!ui.drawer.hidden) renderDrawer();
        toast('Imported: ' + added + ' new, ' + updated + ' updated.');
      } catch (e) { toast('That file is not a review-notes export.'); }
    };
    rd.readAsText(f);
  }

  /* ---------- exports ---------- */
  function pageUrl(n) { var u = new URL(n.page, location.href); if (n.tab) u.searchParams.set('tab', n.tab); u.hash = 'rv=' + n.id; return u.href; }
  function buildReport() {
    var by = {}; notes.forEach(function (n) { (by[n.page] = by[n.page] || []).push(n); });
    var css = 'body{margin:0;background:#f7f7f4;color:#1f2a26;font:15px/1.5 "Source Sans 3","Segoe UI",system-ui,sans-serif}main{max-width:900px;margin:0 auto;padding:40px 24px 80px}h1{font:500 32px/1.15 Newsreader,Georgia,serif;margin:0 0 6px}h2{font:500 22px Newsreader,Georgia,serif;margin:36px 0 10px;padding-top:14px;border-top:1px solid #1f2a26}.meta{color:#51605a;font-size:13px}.n{border-top:1px solid #d9ddd9;padding:14px 0 18px}.t{font-weight:600}.tag{display:inline-block;font-size:12px;border:1px solid #d9ddd9;border-radius:3px;padding:0 6px;margin-right:4px;color:#51605a}.High{color:#c4542a;border-color:#c4542a}blockquote{margin:8px 0;padding:6px 12px;border-left:3px solid #0f6e63;background:#fff;color:#51605a}img{display:block;max-width:100%;margin-top:10px;border:1px solid #d9ddd9}a{color:#0f6e63}.num{display:inline-block;min-width:22px;height:22px;border-radius:11px;background:#0f6e63;color:#fff;font-size:12px;text-align:center;line-height:22px;margin-right:8px}';
    var html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dashboard feedback</title><style>' + css + '</style></head><body><main>' +
      '<p class="meta">Rural NbS Scan · evidence dashboard · review report</p><h1>Review notes</h1><p class="meta">' + notes.length + ' notes · exported ' + new Date().toLocaleString('en-GB') + ' · reviewers: ' + esc(uniq(notes.map(function (n) { return n.reviewer; })).join(', ') || '—') + '</p>';
    Object.keys(by).sort().forEach(function (p) {
      html += '<h2>' + esc(pageTitle(p)) + '</h2>';
      by[p].forEach(function (n) {
        html += '<div class="n"><div><span class="num">' + (notes.indexOf(n) + 1) + '</span><span class="t">' + esc(n.target) + '</span></div>' +
          '<div class="meta"><span class="tag">' + esc(n.type) + '</span><span class="tag ' + esc(n.severity) + '">' + esc(n.severity) + '</span> ' + esc(n.reviewer) + ' · ' + new Date(n.created).toLocaleString('en-GB') + ' · <a href="' + esc(pageUrl(n)) + '">open on page</a></div>' +
          (n.context ? '<p class="meta">' + esc(contextLabel(n.context)) + '</p>' : '') + (n.quote ? '<blockquote>' + esc(n.quote) + '</blockquote>' : '') + (n.text ? '<p>' + esc(n.text).replace(/\n/g, '<br>') + '</p>' : '') + (n.image ? '<img alt="Screengrab" src="' + n.image + '">' : '') + '</div>';
      });
    });
    return html + '</main></body></html>';
  }
  function uniq(a) { return a.filter(function (x, i) { return x && a.indexOf(x) === i; }); }
  function issueBody() {
    var lines = ['## Dashboard feedback', '', '**Reviewer(s):** ' + (uniq(notes.map(function (n) { return n.reviewer; })).join(', ') || '—') + ' · **Exported:** ' + today() + ' · **Notes:** ' + notes.length, ''];
    notes.forEach(function (n, i) {
      lines.push('### ' + (i + 1) + '. ' + pageTitle(n.page) + ' · ' + n.target);
      lines.push('- **Type:** ' + n.type + ' · **Severity:** ' + n.severity + ' · **By:** ' + n.reviewer);
      lines.push('- **Page:** ' + pageUrl(n));
      if (n.context) lines.push('- **Context:** ' + JSON.stringify(n.context));
      if (n.quote) lines.push('', '> ' + n.quote.replace(/\n/g, ' '));
      if (n.text) lines.push('', n.text);
      if (n.image) lines.push('', '_Screengrab not included — attach it from the HTML report._');
      lines.push('');
    });
    return lines.join('\n');
  }
  function issueDialog() {
    var who = uniq(notes.map(function (n) { return n.reviewer; })).join(', ') || reviewer() || 'reviewer';
    var title = 'Dashboard feedback — ' + who + ' — ' + today(), body = issueBody();
    var url = ISSUE_URL + '?title=' + encodeURIComponent(title) + '&body=' + encodeURIComponent(body), long = url.length > 8000;
    var d = el('div', 'rv-modal'); d.setAttribute('data-rv-ui', ''); d.setAttribute('role', 'dialog'); d.setAttribute('aria-label', 'Submit as GitHub issue');
    d.innerHTML = '<div class="rv-modal-in"><div class="rv-c-head"><div><span class="rv-c-k">GitHub issue</span><div class="rv-c-t">' + esc(title) + '</div></div><button type="button" class="rv-x" data-m="close" aria-label="Close">×</button></div>' +
      '<div class="rv-c-body"><p>Opens a new issue on <b>CIAT/nbs_ruralscan</b> with all ' + notes.length + ' notes as markdown. You need a GitHub account and must press <b>Submit</b> there yourself.</p>' +
      '<p class="rv-warn">Screengrabs are not included in the issue. Download the HTML report and attach the images to the issue.</p>' +
      (long ? '<p class="rv-warn">The notes are too long for a link (' + url.length.toLocaleString() + ' characters). The body will be copied to your clipboard; paste it into the issue.</p>' : '') +
      '<details><summary>Preview the issue body</summary><pre class="rv-pre">' + esc(body) + '</pre></details></div>' +
      '<div class="rv-c-foot"><button type="button" class="rv-b2" data-m="report">Download report first</button><button type="button" class="rv-b1" data-m="go">' + (long ? 'Copy body and open GitHub' : 'Open GitHub issue') + '</button></div></div>';
    document.body.appendChild(d);
    d.addEventListener('click', function (e) {
      var b = e.target.closest('[data-m]'); if (!b && e.target === d) { d.remove(); return; } if (!b) return;
      var a = b.getAttribute('data-m');
      if (a === 'close') d.remove();
      if (a === 'report') download('nbs-dashboard-feedback-report-' + today() + '.html', buildReport(), 'text/html');
      if (a === 'go') {
        if (long) {
          var done = function () { window.open(ISSUE_URL + '?title=' + encodeURIComponent(title) + '&body=' + encodeURIComponent('_Notes body copied to the clipboard — paste it here._'), '_blank', 'noopener'); toast('Issue body copied to the clipboard.'); d.remove(); };
          if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(body).then(done, function () { toast('Could not copy — use the preview to select the text.'); });
          else { var ta = document.createElement('textarea'); ta.value = body; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); } catch (err) { /* ignore */ } ta.remove(); done(); }
        } else { window.open(url, '_blank', 'noopener'); d.remove(); }
      }
    });
  }

  /* ---------- keyboard ---------- */
  document.addEventListener('keydown', function (e) {
    if (isUI(e.target) || mode) e.stopPropagation();
    if (e.key !== 'Escape' || !document.body.classList.contains('rv-on')) return;
    var m = document.querySelector('.rv-modal'); if (m) { m.remove(); return; }
    if (composer) { closeComposer(); return; }
    if (mode) { exitModes(); return; }
    if (!ui.menu.hidden) { ui.menu.hidden = true; return; }
    if (!ui.drawer.hidden) ui.drawer.hidden = true;
  }, true);

  /* ---------- start ---------- */
  function start() {
    build(); addToggle(); badge();
    var observer = new MutationObserver(function() {
      if (!document.body.classList.contains('rv-on')) return;
      cancelAnimationFrame(pinRaf); pinRaf = requestAnimationFrame(function() { pins(); paintHighlights(); });
    });
    document.querySelectorAll('.tab-content').forEach(function(node) {
      observer.observe(node, {childList: true, subtree: true});
    });
    if (/[?&]review(=|&|$)/.test(location.search)) setOn(true);
    if (isOn()) enable(true);
    var m = /#rv=([\w]+)/.exec(location.hash);
    if (m) { var n = notes.filter(function (x) { return x.id === m[1]; })[0]; if (n) setTimeout(function () { jump(n); }, 400); }
    setTimeout(pins, 300);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();

  // small API (used by the review screenshots and handy from the console)
  window.DashboardFeedback = { enable: enable, openNotes: openDrawer, clearAll: clearAll, restoreCleared: restoreCleared, buildReport: buildReport, issueBody: issueBody,
    openComposerFor: function (sel, opts) { var t = document.querySelector(sel); if (t) openComposer(Object.assign({ target: t }, opts || {})); },
    grab: grabRect, notes: function () { return notes; }, reload: function () { notes = load(); badge(); pins(); paintHighlights(); } };
})();
