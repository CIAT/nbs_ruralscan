/* ============================================================================
   project_risk.js — Project Risk tab (WB Climate & Disaster Risk Screening lens).

   ASSET RISK: where disasters could damage or destroy the NbS investment itself
   — distinct from risk to rural livelihoods (a need measure, on Opportunity
   Space). Per-NbS, because different assets are vulnerable to different hazards.

   Rating = Σ(hazardᵢ × weightᵢ) × exposure, classified Low → Very High,
   mirroring the WB "Overall Risk Rating". Hazards are the complement of the
   NbS mitigation set (mock T3); exposure = NbS asset + roads / power.
   Indicative spatial screen only — not the full project-level screening.
   ============================================================================ */
(function () {
  'use strict';
  if (!window.SLEMap) { console.warn('project_risk: SLEMap missing'); return; }

  var cl = function (v) { return v < 0 ? 0 : v > 1 ? 1 : v; };
  function frac(x) { var n = Math.sin(x) * 43758.5453; return n - Math.floor(n); }

  // ---- geographic primitives --------------------------------------------
  function north(lat) { return cl((lat - 7.4) / 2.4); }
  function south(lat) { return cl((8.6 - lat) / 1.7); }
  function east(lon) { return cl((lon + 13.0) / 2.5); }
  function slope01(lon, lat) { return cl(SLEMap.gSlope(lon, lat) / 40); }
  function coast(lon, lat) {           // western + southern seaboard
    return cl(Math.max(cl((-12.3 - lon) / 0.9), cl((7.55 - lat) / 0.6)));
  }
  function towns(lon, lat) {           // proximity to major towns (infra proxy)
    var T = [[-13.23, 8.48], [-11.74, 7.96], [-12.04, 8.88], [-11.19, 7.88], [-10.97, 8.64]], g = 0;
    T.forEach(function (t) { var d2 = (lon - t[0]) * (lon - t[0]) + (lat - t[1]) * (lat - t[1]); g = Math.max(g, Math.exp(-d2 / (2 * 0.34 * 0.34))); });
    return cl(g);
  }

  // ---- hazard catalogue (mock T3 — complement of the mitigation set) -----
  var HAZARDS = {
    surge:     { label: 'Cyclone / storm surge', note: 'coastal storm damage to the asset',
                 field: function (lo, la) { return cl(coast(lo, la) * 0.95 + (frac(lo * 21 + la * 13) - 0.5) * 0.12); } },
    fire:      { label: 'Extreme fire', note: 'dry-season burns destroy young plantings',
                 field: function (lo, la) { return cl(0.18 + 0.72 * north(la) - 0.18 * south(la) + (frac(lo * 41 + la * 27) - 0.5) * 0.18); } },
    flood:     { label: 'Destructive flood', note: 'riverine washout of the asset',
                 field: function (lo, la) { return cl(0.12 + 0.62 * south(la) + 0.34 * (1 - slope01(lo, la)) * Math.abs(Math.sin(lo * 6.1 + la * 3.7)) + (frac(lo * 33 + la * 19) - 0.5) * 0.12); } },
    landslide: { label: 'Landslide', note: 'mass movement on steep, wet ground',
                 field: function (lo, la) { return cl(slope01(lo, la) * 0.82 + 0.28 * east(lo) - 0.1 + (frac(lo * 51 + la * 17) - 0.5) * 0.14); } }
  };

  var EXPOSURE_TEXT = { surge: 'coastal asset + infra', fire: 'asset extent', flood: 'asset + roads', landslide: 'asset + roads' };

  // ---- per-NbS config (weights = complement of what the NbS mitigates) ---
  var PR_NBS = {
    agro:   { name: 'Agroforestry',       weights: { fire: 0.40, flood: 0.35, landslide: 0.25 },
              asset: function (lo, la) { return cl(0.18 + 0.82 * SLEMap.gSuit(lo, la, 'baseline')); } },
    forest: { name: 'Forest restoration', weights: { fire: 0.50, landslide: 0.30, flood: 0.20 },
              asset: function (lo, la) { return cl(0.18 + 0.82 * east(lo) * cl((la - 7.4) / 2.2)); } },
    water:  { name: 'Water harvesting',   weights: { flood: 0.55, landslide: 0.25, surge: 0.20 },
              asset: function (lo, la) { return cl(0.18 + 0.82 * north(la) * (1 - slope01(lo, la))); } }
  };

  // ---- rating -------------------------------------------------------------
  function hazardScore(nbs, lo, la) {
    var w = PR_NBS[nbs].weights, s = 0;
    for (var k in w) s += w[k] * HAZARDS[k].field(lo, la);
    return cl(s);
  }
  function exposure(nbs, lo, la) {
    return cl(0.32 + 0.42 * PR_NBS[nbs].asset(lo, la) + 0.26 * towns(lo, la));
  }
  function risk(nbs, lo, la) {
    return cl(hazardScore(nbs, lo, la) * (0.45 + 0.55 * exposure(nbs, lo, la)));
  }
  function classify(r) {
    if (r >= 0.60) return { k: 'VH', name: 'Very high', color: 'var(--pr-vh)' };
    if (r >= 0.44) return { k: 'H',  name: 'High',      color: 'var(--pr-h)' };
    if (r >= 0.28) return { k: 'M',  name: 'Moderate',  color: 'var(--pr-m)' };
    return            { k: 'L',  name: 'Low',       color: 'var(--pr-l)' };
  }
  var CLASS_ORDER = ['VH', 'H', 'M', 'L'];
  var CLASS_COLOR = { VH: 'var(--pr-vh)', H: 'var(--pr-h)', M: 'var(--pr-m)', L: 'var(--pr-l)' };
  var CLASS_NAME = { VH: 'Very high', H: 'High', M: 'Moderate', L: 'Low' };
  var OUTSIDE_COLOR = '#c9c6bc';   // neutral "outside opportunity space"

  // Opportunity-space footprint: VH+H suitability (suit >= 0.60), matching the
  // Opportunity Space map. Asset risk only applies where the NbS would be
  // invested, so the rating is confined to this footprint.
  function inOpp(lo, la) { return SLEMap.gSuit(lo, la, 'baseline') >= 0.60; }

  // ---- state + render -----------------------------------------------------
  var active = 'agro';

  function renderMap() {
    SLEMap.fill('pr-map-cells', function (c) {
      if (!inOpp(c.lon, c.lat)) return { color: OUTSIDE_COLOR, title: 'Outside opportunity space · ' + (c.adm2 || '—') };
      var r = risk(active, c.lon, c.lat), cls = classify(r);
      return { color: cls.color, title: cls.name + ' risk · ' + (c.adm2 || '—') + ' · ' + r.toFixed(2) };
    });
    var lab = document.getElementById('pr-map-layer');
    if (lab) lab.textContent = 'Project-risk rating · ' + PR_NBS[active].name;
  }

  function aggregate() {
    // area-weighted over the OPPORTUNITY-SPACE footprint only
    var grid = SLEMap.GRID, sum = 0, n = 0, counts = { VH: 0, H: 0, M: 0, L: 0 }, byUnit = {};
    grid.forEach(function (c) {
      if (!inOpp(c.lon, c.lat)) return;
      var r = risk(active, c.lon, c.lat); sum += r; n++;
      counts[classify(r).k]++;
      var u = c.adm2 || '—'; if (!byUnit[u]) byUnit[u] = { sum: 0, n: 0 }; byUnit[u].sum += r; byUnit[u].n++;
    });
    var units = Object.keys(byUnit).filter(function (u) { return u !== '—' && byUnit[u].n >= 3; })
      .map(function (u) { return { name: u, mean: byUnit[u].sum / byUnit[u].n }; })
      .sort(function (a, b) { return b.mean - a.mean; });
    return { mean: n ? sum / n : 0, counts: counts, n: n || 1, units: units };
  }

  function renderSummary() {
    var a = aggregate();
    var overall = classify(a.mean);
    var badge = document.getElementById('pr-rating-badge');
    if (badge) { badge.textContent = overall.name.toUpperCase(); badge.setAttribute('data-r', overall.k); }
    var shares = document.getElementById('pr-rating-shares');
    if (shares) {
      shares.innerHTML = CLASS_ORDER.map(function (k) {
        var pct = (a.counts[k] / a.n) * 100;
        return pct < 0.5 ? '' : '<span style="flex:' + pct.toFixed(1) + '; background:' + CLASS_COLOR[k] + '" title="' + CLASS_NAME[k] + ': ' + pct.toFixed(0) + '%"></span>';
      }).join('');
    }
    // ranked units (top 6)
    var rl = document.getElementById('pr-ranklist');
    if (rl) {
      rl.innerHTML = a.units.slice(0, 6).map(function (u, i) {
        var cls = classify(u.mean);
        return '<div class="pr-rankrow"><span class="rk-n">' + String(i + 1).padStart(2, '0') + '</span>' +
          '<span class="rk-nm">' + u.name + '</span>' +
          '<span class="rk-badge" data-r="' + cls.k + '">' + cls.name + '</span></div>';
      }).join('');
    }
  }

  function renderHazards() {
    var wrap = document.getElementById('pr-hazlist');
    if (!wrap) return;
    var w = PR_NBS[active].weights, grid = SLEMap.GRID;
    var keys = Object.keys(w).sort(function (a, b) { return w[b] - w[a]; });
    var opp = grid.filter(function (c) { return inOpp(c.lon, c.lat); });
    var n = opp.length || 1;
    wrap.innerHTML = keys.map(function (k) {
      var hi = 0;
      opp.forEach(function (c) { if (HAZARDS[k].field(c.lon, c.lat) >= 0.5) hi++; });
      var pct = (hi / n) * 100;
      return '<div class="pr-haz"><div class="ph-head">' +
        '<span class="ph-nm">' + HAZARDS[k].label + '<span class="ph-w">w ' + Math.round(w[k] * 100) + '%</span></span>' +
        '<span class="ph-hi">' + pct.toFixed(0) + '% high+</span></div>' +
        '<div class="ph-bar"><span style="width:' + pct.toFixed(0) + '%"></span></div>' +
        '<div class="ph-note">' + HAZARDS[k].note + '</div></div>';
    }).join('');
  }

  function renderWeightsTable() {
    var tb = document.querySelector('#pr-weights-table tbody');
    if (!tb) return;
    var w = PR_NBS[active].weights;
    var keys = Object.keys(w).sort(function (a, b) { return w[b] - w[a]; });
    tb.innerHTML = keys.map(function (k) {
      return '<tr><td>' + HAZARDS[k].label + '</td><td style="text-align:right;">' + Math.round(w[k] * 100) + '%</td><td class="unit">' + EXPOSURE_TEXT[k] + '</td></tr>';
    }).join('');
  }

  function renderAll() { renderMap(); renderSummary(); renderHazards(); renderWeightsTable(); }

  // ---- wiring -------------------------------------------------------------
  var list = document.getElementById('pr-nbslist');
  list && list.addEventListener('click', function (e) {
    var btn = e.target.closest('.ns-nbs'); if (!btn) return;
    list.querySelectorAll('.ns-nbs').forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
    active = btn.dataset.ns; renderAll();
  });

  // sync the Project Risk NbS to the global NbS where possible
  window.setProjectRiskNbs = function (k) {
    if (!PR_NBS[k] || !list) return;
    var btn = list.querySelector('.ns-nbs[data-ns="' + k + '"]');
    if (btn) { list.querySelectorAll('.ns-nbs').forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); }); active = k; renderAll(); }
  };

  // ---- init ---------------------------------------------------------------
  SLEMap.init([
    { svgId: 'pr-map', uid: 'prk', cellsId: 'pr-map-cells',
      title: 'Project-risk rating — Sierra Leone (mock)',
      desc: 'Overall project-risk rating (Low to Very High) for the selected NbS asset, clipped to the national boundary (ADM0) over ADM2 units. Exposure = NbS asset + roads / power.' }
  ]);
  renderAll();
})();
