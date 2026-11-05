/* Dashboard navigation and orientation. Does not alter evidence or review decisions. */
(function () {
  'use strict';
  var restoringRoute = false;
  function byId(id) { return document.getElementById(id); }
  function open(id) { var button = byId(id); if (button) button.click(); }
  function selectedView(kind, fallback) {
    var button = document.querySelector('[data-' + kind + '-view][aria-pressed="true"]');
    return button ? button.dataset[kind + 'View'] : fallback;
  }
  function syncRoute(tab) {
    if (restoringRoute) return;
    var route = { 'tab-overview': '#overview', 'tab-search': '#progress', 'tab-variables': '#datasets' }[tab];
    if (tab === 'tab-methods') route = '#methods/' + selectedView('method', 'rural');
    if (tab === 'tab-qaqc') route = { queue: window.DashboardPriority ? window.DashboardPriority.route() : '#review-queue', help: '#review-help', pipeline: '#pipeline-records' }[selectedView('review', 'queue')];
    if (tab === 'tab-stocktake') route = location.hash.startsWith('#source=') ? location.hash : '#bibliography';
    if (tab === 'tab-interrogator') route = location.hash.startsWith('#t4/') ? location.hash : selectedView('query', 'relationships') === 'explorer' ? '#evidence-explorer' : '#relationships';
    if (route && location.hash !== route) history.replaceState(null, '', route);
  }
  function setView(kind, view) {
    var selector = '[data-' + kind + '-view]';
    var views = {
      review: { queue: 'review-queue-panel', help: 'review-help-panel', pipeline: 'review-pipeline-panel' },
      query: { relationships: 'relationship-review-root', explorer: 'query-explorer-panel' },
      method: { rural: 'method-rural-panel', evidence: 'method-evidence-panel', search: 'method-search-panel' }
    };
    var panels = views[kind];
    if (!panels || !panels[view]) return;
    Object.keys(panels).forEach(function (key) { var panel = byId(panels[key]); if (panel) panel.hidden = key !== view; });
    document.querySelectorAll(selector).forEach(function (button) { button.setAttribute('aria-pressed', String(button.dataset[kind + 'View'] === view)); });
    var route = kind === 'method' ? '#methods/' + view : kind === 'review' ? { queue: window.DashboardPriority ? window.DashboardPriority.route() : '#review-queue', help: '#review-help', pipeline: '#pipeline-records' }[view] : '';
    if (route && location.hash !== route) history.replaceState(null, '', route);
    if (kind === 'review' && view === 'pipeline' && window.DashboardProgress && typeof window.DashboardProgress.renderPipelineRecords === 'function') window.DashboardProgress.renderPipelineRecords();
    syncSubtabs();
  }
  function openHash() {
    // Opening a main tab must not overwrite the deep link before its subview is restored.
    restoringRoute = true;
    try {
      if (window.DashboardPriority && window.DashboardPriority.openFromHash(location.hash)) return;
      if (location.hash === '#relationships') { open('btn-interrogator'); setView('query', 'relationships'); }
      else if (location.hash === '#evidence-explorer' || location.hash.startsWith('#t4/')) { open('btn-interrogator'); setView('query', 'explorer'); }
      else if (location.hash === '#pipeline-records') { open('btn-qaqc'); setView('review', 'pipeline'); }
      else if (location.hash === '#review-help') { open('btn-qaqc'); setView('review', 'help'); }
      else if (location.hash === '#review-queue') { open('btn-qaqc'); setView('review', 'queue'); }
      else if (location.hash.startsWith('#methods/')) { open('btn-methods'); setView('method', location.hash.slice('#methods/'.length)); }
      else { var tab = { '#overview': 'btn-overview', '#progress': 'btn-search', '#bibliography': 'btn-stocktake', '#datasets': 'btn-variables' }[location.hash]; if (tab) open(tab); }
    } finally { restoringRoute = false; }
  }
  function onTab(tab, updateRoute) {
    var sourceTab = tab === 'tab-stocktake' || tab === 'tab-variables';
    byId('btn-stocktake').classList.toggle('shell-group-active', sourceTab);
    document.querySelectorAll('#tab-stocktake [data-shell-open], #tab-variables [data-shell-open]').forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.shellOpen === (tab === 'tab-variables' ? 'btn-variables' : 'btn-stocktake')));
    });
    // Old deep links and direct calls still use the original tab IDs.
    if (updateRoute !== false) syncRoute(tab);
    syncSubtabs();
    numberContent();
  }
  function measure() {
    var header = document.querySelector('.app-header');
    var active = document.querySelector('.tab-content.active');
    var nav = active && active.querySelector('.shell-subnav:not(.shell-subnav-nested)');
    var mainNav = document.querySelector('.tab-nav');
    var controls = document.querySelector('#query-explorer-panel .sidebar-panel');
    var headerHeight = header && getComputedStyle(header).position === 'sticky' ? header.getBoundingClientRect().height : 0;
    document.documentElement.style.setProperty('--shell-header-height', headerHeight + 'px');
    document.documentElement.style.setProperty('--dp-header-height', headerHeight + 'px');
    document.documentElement.style.setProperty('--dp-main-tabs-height', (mainNav ? mainNav.getBoundingClientRect().height : 0) + 'px');
    document.documentElement.style.setProperty('--shell-subnav-height', (nav ? nav.getBoundingClientRect().height : 0) + 'px');
    document.documentElement.style.setProperty('--shell-controls-height', (controls ? controls.getBoundingClientRect().height : 0) + 'px');
  }
  function syncSubtabs() {
    document.querySelectorAll('.shell-subnav').forEach(function (nav) {
      nav.querySelectorAll('button').forEach(function (button) {
        var selected = button.hasAttribute('data-action') ? button.classList.contains('is-active') : button.getAttribute('aria-selected') === 'true' || button.getAttribute('aria-pressed') === 'true';
        if (!button.hasAttribute('role')) button.setAttribute('aria-pressed', String(selected));
        button.tabIndex = selected ? 0 : -1;
      });
    });
    measure();
  }
  function navigateSubtabs(event) {
    var button = event.target.closest('.shell-subnav button');
    if (!button || button.hasAttribute('data-t4-tab') || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    var nav = button.closest('.shell-subnav'), buttons = Array.from(nav.querySelectorAll('button'));
    var index = buttons.indexOf(button);
    var next = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : buttons.length - 1)) % buttons.length;
    event.preventDefault();
    buttons[next].click();
    // Progress re-renders its navigation; focus the replacement button.
    var current = document.querySelector('.tab-content.active .shell-subnav');
    var target = current && current.querySelectorAll('button')[next];
    if (target) { target.focus({preventScroll: true}); target.scrollIntoView({block: 'nearest', inline: 'nearest'}); }
  }
  function textWithoutNumber(node) {
    var clone = node.cloneNode(true);
    clone.querySelectorAll('.shell-section-number').forEach(function (number) { number.remove(); });
    return clone.textContent.replace(/[▼▶↗]/g, '').replace(/\s+/g, ' ').trim();
  }
  function setNumber(node, number) {
    if (/^(?:(?:Table|Figure)\s+)?\d+(?:\.\d+)*[.\s]/.test(textWithoutNumber(node))) return;
    var label = node.querySelector(':scope > .shell-section-number');
    if (!label) { label = document.createElement('span'); label.className = 'shell-section-number'; node.prepend(label); }
    if (label.textContent !== number + ' ') label.textContent = number + ' ';
  }
  function captionLabel(table) {
    var block = table.closest('section, .card-container, .dp-section, .t4-section, article');
    var title = block && block.querySelector('h2, h3, h4');
    var headings = Array.from(table.querySelectorAll('thead th')).slice(0, 4).map(function (cell) { return cell.textContent.trim(); });
    return title ? textWithoutNumber(title).replace(/^\d+(?:\.\d+)*\s*/, '') : (headings.length ? headings.join(' · ') : 'Evidence records');
  }
  function numberContent() {
    // Progress owns its stage/table numbering. Other legacy and dynamic views share this convention.
    [['tab-interrogator', '3'], ['tab-stocktake', '4.1'], ['tab-variables', '4.2'], ['tab-qaqc', '5'], ['tab-methods', '6']].forEach(function (entry) {
      var root = byId(entry[0]); if (!root) return;
      var h = 0;
      var prefix = entry[0] === 'tab-interrogator' ? '3.2' : entry[1];
      root.querySelectorAll('h2, h3').forEach(function (heading) {
        if (heading.closest('.shell-intro, #vf-cards, #vf-stats, #relationship-review-root') || heading.id === 'family-hero-title' || heading.classList.contains('info-block-title')) return;
        setNumber(heading, heading.closest('#review-queue-panel') ? '5.1' : prefix + '.' + (++h));
      });
      root.querySelectorAll('table').forEach(function (table, index) {
        if (table.closest('#relationship-review-root')) return;
        var caption = table.querySelector(':scope > caption');
        if (caption && !caption.classList.contains('shell-table-caption')) {
          setNumber(caption, 'Table ' + entry[1] + '.' + (index + 1) + '.');
          return;
        }
        if (!caption) { caption = document.createElement('caption'); caption.className = 'shell-table-caption'; table.prepend(caption); }
        var value = 'Table ' + entry[1] + '.' + (index + 1) + '. ' + captionLabel(table);
        if (caption.textContent !== value) caption.textContent = value;
      });
      root.querySelectorAll('.chart-wrapper').forEach(function (chart, index) {
        if (chart.closest('#relationship-review-root')) return;
        var caption = chart.parentElement.querySelector(':scope > .shell-figure-caption');
        if (!caption) { caption = document.createElement('p'); caption.className = 'shell-figure-caption'; chart.after(caption); }
        var title = chart.closest('.card-container');
        var heading = title && title.querySelector('h2, h3');
        var value = 'Figure ' + entry[1] + '.' + (index + 1) + '. ' + (heading ? textWithoutNumber(heading).replace(/^\d+(?:\.\d+)*\s*/, '') : 'Evidence coverage');
        if (caption.textContent !== value) caption.textContent = value;
      });
    });
  }
  function init() {
    document.querySelectorAll('[data-shell-open]').forEach(function (button) { button.addEventListener('click', function () { open(button.dataset.shellOpen); }); });
    document.querySelectorAll('[data-review-view]').forEach(function (button) { button.addEventListener('click', function () { setView('review', button.dataset.reviewView); }); });
    document.querySelectorAll('[data-query-view]').forEach(function (button) { button.addEventListener('click', function () { setView('query', button.dataset.queryView); history.replaceState(null, '', button.dataset.queryView === 'relationships' ? '#relationships' : '#evidence-explorer'); if (button.dataset.queryView === 'explorer' && typeof window.refreshQueryProvenance === 'function') window.refreshQueryProvenance(); }); });
    document.querySelectorAll('[data-method-view]').forEach(function (button) { button.addEventListener('click', function () { setView('method', button.dataset.methodView); }); });
    var guide = byId('review-reference-guide');
    ['vf-howto', 'vf-reason-codes'].forEach(function (id) { var item = byId(id); if (item) guide.appendChild(item); });
    var theme = byId('theme-toggle'), feedback = byId('rv-toggle');
    if (theme && feedback) { var group = document.createElement('div'); group.className = 'shell-utilities'; theme.before(group); group.append(theme, feedback); }
    var controls = document.querySelector('#query-explorer-panel .sidebar-panel');
    if (controls) {
      var oldHelp = controls.querySelector(':scope > div:last-child');
      if (oldHelp && !oldHelp.classList.contains('control-group')) oldHelp.remove();
    }
    document.addEventListener('keydown', navigateSubtabs);
    var pending = false;
    var observer = new MutationObserver(function () {
      if (pending) return;
      pending = true;
      requestAnimationFrame(function () { pending = false; observer.disconnect(); numberContent(); syncSubtabs(); observer.observe(byId('dashboard-content'), { childList: true, subtree: true }); });
    });
    observer.observe(byId('dashboard-content'), { childList: true, subtree: true });
    if (window.ResizeObserver) {
      var resize = new ResizeObserver(measure);
      [document.querySelector('.app-header'), document.querySelector('.tab-nav'), controls].forEach(function (node) { if (node) resize.observe(node); });
      document.querySelectorAll('.shell-subnav').forEach(function (node) { resize.observe(node); });
    }
    window.addEventListener('resize', measure);
    // The default Overview markup is not a navigation choice on first load.
    onTab(document.querySelector('.tab-content.active').id, false);
    window.addEventListener('hashchange', openHash);
    openHash();
  }
  window.DashboardShell = { syncSubtabs: syncSubtabs, onTab: onTab, openFromHash: openHash, showExplorer: function () { open('btn-interrogator'); setView('query', 'explorer'); syncRoute('tab-interrogator'); }, openReviewQueue: function () { open('btn-qaqc'); setView('review', 'queue'); }, openReviewHelp: function () { open('btn-qaqc'); setView('review', 'help'); }, openPipelineRecords: function () { open('btn-qaqc'); setView('review', 'pipeline'); }, openMethods: function (view) { open('btn-methods'); setView('method', view || 'rural'); }, numberContent: numberContent };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
