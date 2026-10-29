/* ============================================================================
   priority_detail.js — raw-vs-transformed map view for the Priority / hotspot
   variable detail (Variable Config → Priority / hotspot variables).

   Priority is a NEED score, not a fitness score: there are no membership
   curves. Instead each variable is NORMALISED (fixed threshold · min–max ·
   percentile · z-score) within a chosen REFERENCE FRAME (AOI · sub-national ·
   global · fixed baseline), with a DISTRIBUTION view showing the breakpoints
   and a stated provenance / reference frame.

   All rules read from the PVARS schema below (mock T5); nothing about the
   scoring is hardcoded in the render path. NbS-agnostic — NbS enters only later
   as a T6 Likert weight at the hotspot stage (out of scope here).
   ============================================================================ */
(function () {
  'use strict';
  if (!window.SLEMap) { console.warn('priority_detail: SLEMap missing'); return; }

  var cl = function (v) { return v < 0 ? 0 : v > 1 ? 1 : v; };
  function frac(x) { var n = Math.sin(x) * 43758.5453; return n - Math.floor(n); }

  // ---- colour ramps -------------------------------------------------------
  function lerp(a, b, t) {
    var pa = [parseInt(a.slice(1, 3), 16), parseInt(a.slice(3, 5), 16), parseInt(a.slice(5, 7), 16)];
    var pb = [parseInt(b.slice(1, 3), 16), parseInt(b.slice(3, 5), 16), parseInt(b.slice(5, 7), 16)];
    var c = pa.map(function (v, i) { return Math.round(v + (pb[i] - v) * t); });
    return 'rgb(' + c[0] + ',' + c[1] + ',' + c[2] + ')';
  }
  function ramp(stops, t) {
    t = cl(t);
    var seg = (stops.length - 1) * t, i = Math.min(stops.length - 2, Math.floor(seg));
    return lerp(stops[i], stops[i + 1], seg - i);
  }
  var RAW_STOPS = ['#eef3f6', '#9fc1d6', '#4f8aae', '#1d4a66'];      // neutral data ramp
  var PRI_STOPS = ['#efe9dd', '#f8cdb0', '#ef7d52', '#c5391a', '#7a1505']; // need ramp (T-hot)
  function rawColor(t) { return ramp(RAW_STOPS, t); }
  function priColor(p) { return ramp(PRI_STOPS, p); }

  // ---- schema (mock) ------------------------------------------------------
  // dir: 'hi' = higher raw → higher priority; 'lo' = lower raw → higher priority
  // fixed: ascending bands by upper bound `max` (last = Infinity)
  var INF = Infinity;
  // kind: 'priority' = weighted need score · 'descriptor' = context filter, never weighted
  // sens: nationally-sensitive variable → carries a "confirm country-endorsed source" flag
  var PVARS = [
    { key: 'spei', name: 'Drought hazard', theme: 'Climate hazard', kind: 'priority', unit: 'SPEI · index', fkey: 'north',
      range: [-2.4, 1.0], dir: 'lo', method: 'percentile',
      fixed: [{ lab: 'Extreme', max: -2 }, { lab: 'Severe', max: -1.5 }, { lab: 'Moderate', max: -1 }, { lab: 'Mild', max: -0.5 }, { lab: 'None / wet', max: INF }],
      prov: 'SPEI drought classes', invField: true,
      what: 'Standardised Precipitation–Evapotranspiration Index — a normalised measure of dry vs wet conditions. More negative = drier.',
      source: '<b>SPEI global</b> · 1 km · monthly · CSIC · CC-BY 4.0', grain: 'SPEI global · 1 km', tier: 'Tier 1 · peer-reviewed',
      quote: '“Drought is the dominant climate stressor on rainfed systems in the interior.” — Recipe note · Climate hazard (p. 6)' },
    { key: 'flood', name: 'Flood hazard', theme: 'Climate hazard', kind: 'priority', unit: 'hazard · 0–1', fkey: 'south',
      range: [0, 1], dir: 'hi', method: 'fixed',
      fixed: [{ lab: 'Low', max: 0.33 }, { lab: 'Moderate', max: 0.66 }, { lab: 'High', max: INF }],
      prov: 'flood return-period classes',
      what: 'Modelled flood hazard from return-period inundation depth, normalised 0–1. Concentrated on low-lying southern plains and river margins.',
      source: '<b>Fathom / JRC</b> · 90 m · global · research licence', grain: 'Fathom / JRC · 90 m', tier: 'Tier 2 · global model' },
    { key: 'heat', name: 'Heat-stress hazard', theme: 'Climate hazard', kind: 'priority', unit: '°C anomaly', fkey: 'north',
      range: [0.4, 3.4], dir: 'hi', method: 'percentile',
      fixed: [{ lab: 'Slight', max: 1.2 }, { lab: 'Moderate', max: 2.0 }, { lab: 'High', max: 2.8 }, { lab: 'Extreme', max: INF }],
      prov: 'WBGT anomaly classes',
      what: 'Projected wet-bulb temperature anomaly under SSP2-4.5, °C above baseline. Highest in the drier interior north.',
      source: '<b>CHIRTS / CMIP6</b> · 5 km · derived', grain: 'CHIRTS / CMIP6 · 5 km', tier: 'Tier 2 · derived' },
    { key: 'wstress', name: 'Water stress', theme: 'Climate hazard', kind: 'priority', unit: 'index · 0–1', fkey: 'north',
      range: [0.05, 0.95], dir: 'hi', method: 'percentile',
      fixed: [{ lab: 'Low', max: 0.33 }, { lab: 'Moderate', max: 0.55 }, { lab: 'High', max: 0.75 }, { lab: 'Severe', max: INF }],
      prov: 'water-stress index classes',
      what: 'Ratio of water demand to renewable supply, 0–1. Higher = more stressed; peaks in the drier interior north.',
      source: '<b>WRI Aqueduct</b> · sub-basin · derived', grain: 'WRI Aqueduct · sub-basin', tier: 'Tier 2 · global model' },
    { key: 'erosion', name: 'Soil-erosion risk', theme: 'NbS response (environment)', kind: 'priority', unit: 't/ha/yr', fkey: 'se',
      range: [0, 28], dir: 'hi', method: 'minmax',
      fixed: [{ lab: 'Low', max: 6 }, { lab: 'Moderate', max: 14 }, { lab: 'High', max: 22 }, { lab: 'Very high', max: INF }],
      prov: 'RUSLE soil-loss bands',
      what: 'Modelled soil loss the NbS could reduce (RUSLE), t/ha/yr. Highest on the steep south-eastern uplands.',
      source: '<b>RUSLE (derived)</b> · 1 km · from slope, soil & cover', grain: 'RUSLE derived · 1 km', tier: 'Tier 2 · derived' },
    { key: 'carbon', name: 'Carbon-sequestration potential', theme: 'NbS response (environment)', kind: 'priority', unit: 'tCO₂/ha/yr', fkey: 'se',
      range: [0.3, 7.5], dir: 'hi', method: 'minmax',
      fixed: [{ lab: 'Low', max: 2 }, { lab: 'Moderate', max: 4 }, { lab: 'High', max: INF }],
      prov: 'IPCC tier-1 accumulation rates',
      what: 'Indicative above-ground carbon accumulation an NbS could deliver, tCO₂/ha/yr.',
      source: '<b>IPCC tier-1</b> · agro-ecological zone lookup', grain: 'IPCC tier-1 · zone lookup', tier: 'Tier 1 · IPCC' },
    { key: 'biodiv', name: 'Biodiversity priority', theme: 'NbS response (environment)', kind: 'priority', unit: 'index · 0–1', fkey: 'east',
      range: [0.05, 0.95], dir: 'hi', method: 'percentile',
      fixed: [{ lab: 'Low', max: 0.33 }, { lab: 'Moderate', max: 0.66 }, { lab: 'High', max: INF }],
      prov: 'KBA / intactness composite',
      what: 'Composite of proximity to Key Biodiversity Areas and habitat intactness, 0–1. Peaks toward the eastern Gola forests.',
      source: '<b>KBA + intactness</b> · composite', grain: 'KBA + intactness · composite', tier: 'Tier 2 · composite' },
    { key: 'poverty', name: 'Rural poverty', theme: 'People & production', kind: 'priority', unit: '% below line', fkey: 'north',
      range: [16, 84], dir: 'hi', method: 'percentile', sens: true,
      fixed: [{ lab: '<20%', max: 20 }, { lab: '20–40%', max: 40 }, { lab: '40–60%', max: 60 }, { lab: '60–80%', max: 80 }, { lab: '≥80%', max: INF }],
      prov: 'national poverty assessment',
      what: 'Share of population below the national poverty line, %. Higher = greater need.',
      source: '<b>SL Integrated Household Survey</b> · ADM2', grain: 'SL IHS · ADM2', tier: 'Tier 1 · national survey',
      endorse: 'Poverty figures are nationally sensitive — confirm the Stats SL country-endorsed release before publishing.',
      upload: 'A more recent district poverty surface from the 2024 survey round may exist locally — upload to replace the 2018 default.' },
    { key: 'prodgap', name: 'Production gap', theme: 'People & production', kind: 'priority', unit: '% below potential', fkey: 'ne',
      range: [5, 70], dir: 'hi', method: 'percentile',
      fixed: [{ lab: 'Small', max: 20 }, { lab: 'Moderate', max: 40 }, { lab: 'Large', max: 55 }, { lab: 'Very large', max: INF }],
      prov: 'yield-gap bands',
      what: 'Shortfall of actual vs attainable yield, %. A larger gap = more headroom for an NbS to lift production.',
      source: '<b>GYGA / FAO</b> · agro-zone (derived)', grain: 'GYGA / FAO · agro-zone', tier: 'Tier 2 · derived' },
    { key: 'agdep', name: 'Agricultural dependency', theme: 'People & production', kind: 'priority', unit: '% livelihoods', fkey: 'townrural',
      range: [20, 92], dir: 'hi', method: 'percentile',
      fixed: [{ lab: 'Low', max: 35 }, { lab: 'Moderate', max: 55 }, { lab: 'High', max: 75 }, { lab: 'Very high', max: INF }],
      prov: 'census livelihood shares',
      what: 'Share of livelihoods dependent on agriculture, %. Higher = more exposed to land-productivity change.',
      source: '<b>Agricultural census</b> · ADM2', grain: 'Ag census · ADM2', tier: 'Tier 1 · national census' },
    { key: 'rpop', name: 'Rural population', theme: 'Descriptors (context)', kind: 'descriptor', unit: 'persons/km²', fkey: 'townrural',
      range: [4, 380], dir: 'hi', method: 'percentile', sens: true,
      fixed: [{ lab: 'Sparse', max: 40 }, { lab: 'Moderate', max: 120 }, { lab: 'Dense', max: 250 }, { lab: 'Very dense', max: INF }],
      prov: 'WorldPop density bands',
      what: 'Rural population density, persons/km². A descriptor of who is present — used as a filter, not weighted into the score.',
      source: '<b>WorldPop</b> · 100 m · 2020 · CC-BY 4.0', grain: 'WorldPop · 100 m', tier: 'Tier 1 · modelled census',
      endorse: 'Population counts are nationally sensitive — confirm the country-endorsed census / WorldPop release.' },
    { key: 'smallhold', name: 'Farm size / smallholder', theme: 'Descriptors (context)', kind: 'descriptor', unit: 'farms/km²', fkey: 'townrural',
      range: [2, 58], dir: 'hi', method: 'minmax',
      fixed: [{ lab: 'Low', max: 12 }, { lab: 'Moderate', max: 30 }, { lab: 'High', max: INF }],
      prov: 'agricultural census bands',
      what: 'Smallholder farm density, farms/km² — a descriptor of the farming structure, used as a filter.',
      source: '<b>Agricultural census</b> · ADM2 (derived)', grain: 'Ag census · ADM2', tier: 'Tier 2 · derived' },
    { key: 'market', name: 'Market access', theme: 'Descriptors (context)', kind: 'descriptor', unit: 'hours to market', fkey: 'remote',
      range: [0.3, 7.5], dir: 'hi', method: 'percentile',
      fixed: [{ lab: '<1 h', max: 1 }, { lab: '1–3 h', max: 3 }, { lab: '3–5 h', max: 5 }, { lab: '≥5 h', max: INF }],
      prov: 'travel-time surface classes',
      what: 'Travel time to the nearest market town, hours — a descriptor of remoteness, used as a filter / mask.',
      source: '<b>Malaria Atlas / Weiss et al.</b> · 1 km · global', grain: 'Weiss et al. · 1 km', tier: 'Tier 1 · peer-reviewed' },
    { key: 'prodval', name: 'Agricultural production value', theme: 'Descriptors (context)', kind: 'descriptor', unit: '$/km²/yr', fkey: 'se',
      range: [5, 260], dir: 'hi', method: 'percentile', sens: true,
      fixed: [{ lab: 'Low', max: 40 }, { lab: 'Moderate', max: 110 }, { lab: 'High', max: 180 }, { lab: 'Very high', max: INF }],
      prov: 'gridded ag-GDP bands',
      what: 'Value of agricultural output per km², $/yr — context for what is at stake, used as a filter, not a need score.',
      source: '<b>Spatial ag-GDP</b> · 10 km (derived)', grain: 'Spatial ag-GDP · 10 km', tier: 'Tier 3 · indicative',
      endorse: 'Production value is nationally sensitive — confirm the country-endorsed agricultural-statistics source.' }
  ];

  var REGION = { Kenema: 1, Kailahun: 1, Kono: 1 };   // mock "Eastern region" subset
  var FRAME_LABEL = { aoi: 'this country (AOI)', region: 'the Eastern region', global: 'the global dataset', fixed: 'a fixed baseline' };
  var METHOD_NOTE = {
    fixed: 'Classify against fixed, externally-defined thresholds — comparable across places & time.',
    minmax: 'Rescale the lowest value to 0 and the highest to 1 within the reference frame.',
    percentile: 'Rank each cell against the reference population — robust to outliers.',
    zscore: 'Standardise by mean & standard deviation of the reference frame.'
  };

  // ---- raw surface --------------------------------------------------------
  function fieldFactor(pv, lon, lat) {
    var f;
    switch (pv.fkey) {
      case 'north': f = cl((lat - 7.2) / 2.6); break;
      case 'east': f = cl((lon + 13.0) / 2.5); break;
      case 'se': f = cl((lon + 11.6) / 1.4) * cl((8.8 - lat) / 1.6); break;
      case 'south': f = cl((8.6 - lat) / 1.7); break;
      case 'ne': f = cl((lat - 8.4) / 1.4) * cl((lon + 11.6) / 1.4); break;
      case 'remote': f = cl(Math.sqrt((lon + 13.23) * (lon + 13.23) + (lat - 8.48) * (lat - 8.48)) / 2.8); break;
      case 'townrural': {
        var towns = [[-11.74, 7.96], [-12.04, 8.88], [-11.19, 7.88], [-10.97, 8.64]], g = 0;
        towns.forEach(function (t) { var d2 = (lon - t[0]) * (lon - t[0]) + (lat - t[1]) * (lat - t[1]); g = Math.max(g, Math.exp(-d2 / (2 * 0.33 * 0.33))); });
        f = cl(0.12 + 0.88 * g); break;
      }
      default: f = 0.5;
    }
    // some variables are "worse where the field is high" inverted into raw value space
    if (pv.invField) f = 1 - f;
    var n1 = 30 + pv.key.length * 7, n2 = 15 + pv.key.length * 3;
    f += (frac(lon * n1 + lat * n2) - 0.5) * 0.20;
    return cl(f);
  }
  function rawVal(pv, c) {
    var v = pv.range[0] + (pv.range[1] - pv.range[0]) * fieldFactor(pv, c.lon, c.lat);
    return pv.round ? Math.round(v) : v;
  }

  // ---- reference population ----------------------------------------------
  function population(pv, frame) {
    var grid = SLEMap.GRID, vals = [];
    if (frame === 'region') {
      grid.forEach(function (c) { if (REGION[c.adm2]) vals.push(rawVal(pv, c)); });
      if (vals.length < 8) grid.forEach(function (c) { vals.push(rawVal(pv, c)); }); // fallback
    } else if (frame === 'fixed') {
      var lo = pv.range[0], hi = pv.range[1];
      for (var i = 0; i <= 200; i++) vals.push(lo + (hi - lo) * (i / 200));
    } else { // aoi or global → start from AOI
      grid.forEach(function (c) { vals.push(rawVal(pv, c)); });
      if (frame === 'global') {
        var mn = Math.min.apply(null, vals), mx = Math.max.apply(null, vals), r = (mx - mn) || 1, extra = [];
        for (var j = 0; j <= 240; j++) extra.push(mn - 0.6 * r + (1.5 * r + 0.9 * r) * (j / 240));
        vals = vals.concat(extra);
      }
    }
    vals.sort(function (a, b) { return a - b; });
    return vals;
  }
  function quantile(sorted, q) {
    var idx = (sorted.length - 1) * q, lo = Math.floor(idx), hi = Math.ceil(idx);
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
  }
  function stats(sorted) {
    var n = sorted.length, mean = 0; sorted.forEach(function (v) { mean += v; }); mean /= n;
    var sd = 0; sorted.forEach(function (v) { sd += (v - mean) * (v - mean); }); sd = Math.sqrt(sd / n) || 1;
    return { min: sorted[0], max: sorted[n - 1], mean: mean, std: sd };
  }

  // ---- state + normalisation ---------------------------------------------
  var active = PVARS[0];
  var ctl = {};   // {method, dir, frame, clip}
  function resetCtl(pv) { ctl = { method: pv.method, dir: pv.dir, frame: 'aoi', clip: 2 }; }

  function bandIndex(pv, x) {
    for (var i = 0; i < pv.fixed.length; i++) if (x <= pv.fixed[i].max) return i;
    return pv.fixed.length - 1;
  }
  function score(pv, x, pop, st) {
    var s;
    if (ctl.method === 'fixed') {
      var n = pv.fixed.length;
      s = bandIndex(pv, x) / (n - 1);
      return cl(ctl.dir === 'lo' ? 1 - s : s);
    }
    // winsorise tails
    var lo = quantile(pop, ctl.clip / 100), hi = quantile(pop, 1 - ctl.clip / 100);
    var xc = Math.max(lo, Math.min(hi, x));
    if (ctl.method === 'minmax') {
      s = (xc - lo) / ((hi - lo) || 1);
    } else if (ctl.method === 'percentile') {
      var c = 0; for (var i = 0; i < pop.length; i++) if (pop[i] <= x) c++; s = c / pop.length;
    } else { // zscore
      s = ((x - st.mean) / st.std + 2.5) / 5;
    }
    s = cl(s);
    return ctl.dir === 'lo' ? 1 - s : s;
  }

  // ---- map rendering ------------------------------------------------------
  var pop, st;
  function recompute() { pop = population(active, ctl.method === 'fixed' ? 'aoi' : ctl.frame); st = stats(pop); }
  function renderMaps() {
    var lo = active.range[0], hi = active.range[1], span = (hi - lo) || 1;
    SLEMap.fill('pd-rawmap-cells', function (c) {
      var v = rawVal(active, c);
      return { color: rawColor((v - lo) / span), title: active.name + ': ' + fmt(v) + ' ' + (active.round ? '' : active.unit.split('·')[0].trim()) + ' · ' + (c.adm2 || '—') };
    });
    SLEMap.fill('pd-transmap-cells', function (c) {
      var p = score(active, rawVal(active, c), pop, st);
      return { color: priColor(p), title: 'priority ' + p.toFixed(2) };
    });
  }
  function fmt(v) { return Math.abs(v) >= 10 ? Math.round(v) : (Math.round(v * 100) / 100); }

  // ---- distribution histogram --------------------------------------------
  function renderHist() {
    var svg = document.getElementById('pd-hist'); if (!svg) return;
    var X0 = 40, X1 = 444, Y0 = 120, Y1 = 16;
    var dmin = pop[0], dmax = pop[pop.length - 1], dr = (dmax - dmin) || 1;
    var toX = function (v) { return X0 + ((v - dmin) / dr) * (X1 - X0); };
    var NB = 20, bins = new Array(NB).fill(0);
    pop.forEach(function (v) { var b = Math.min(NB - 1, Math.floor(((v - dmin) / dr) * NB)); bins[b]++; });
    var maxC = Math.max.apply(null, bins) || 1;
    var bw = (X1 - X0) / NB, html = '';
    // bars coloured by their transformed priority (ties hist to the transform)
    for (var i = 0; i < NB; i++) {
      var center = dmin + (i + 0.5) / NB * dr;
      var h = (bins[i] / maxC) * (Y0 - Y1 - 4);
      var p = score(active, center, pop, st);
      html += '<rect class="hb" x="' + (X0 + i * bw + 0.6).toFixed(1) + '" y="' + (Y0 - h).toFixed(1) +
        '" width="' + (bw - 1.2).toFixed(1) + '" height="' + h.toFixed(1) + '" fill="' + priColor(p) + '"/>';
    }
    // axis
    html += '<line class="axis" x1="' + X0 + '" y1="' + Y0 + '" x2="' + X1 + '" y2="' + Y0 + '"/>';
    // breakpoints
    var brks = [], labs = [];
    if (ctl.method === 'fixed') {
      active.fixed.forEach(function (b) { if (b.max !== INF && b.max > dmin && b.max < dmax) { brks.push(b.max); labs.push(active.round ? String(b.max) : fmt(b.max)); } });
    } else {
      [0.2, 0.4, 0.6, 0.8].forEach(function (q) { var v = quantile(pop, q); brks.push(v); labs.push('Q' + Math.round(q * 100)); });
    }
    brks.forEach(function (v, k) {
      var x = toX(v);
      html += '<line class="brk" x1="' + x.toFixed(1) + '" y1="' + Y1 + '" x2="' + x.toFixed(1) + '" y2="' + Y0 + '"/>';
      html += '<text class="brk-lab" x="' + (x + 2).toFixed(1) + '" y="' + (Y1 + 8) + '">' + labs[k] + '</text>';
    });
    // x labels
    html += '<text class="axlab" x="' + X0 + '" y="' + (Y0 + 12) + '">' + fmt(dmin) + '</text>';
    html += '<text class="axlab" x="' + X1 + '" y="' + (Y0 + 12) + '" text-anchor="end">' + fmt(dmax) + '</text>';
    html += '<text class="axlab" x="' + ((X0 + X1) / 2) + '" y="' + (Y0 + 12) + '" text-anchor="middle">' + active.unit + '</text>';
    // direction arrow (toward higher priority)
    var ay = Y1 + 4, toHi = (ctl.dir === 'hi');
    var ax1 = toHi ? X1 - 92 : X0 + 92, ax2 = toHi ? X1 - 6 : X0 + 6;
    html += '<line x1="' + ax1 + '" y1="' + ay + '" x2="' + ax2 + '" y2="' + ay + '" stroke="' + 'var(--hot-h)' + '" stroke-width="1.4"/>';
    var tipX = ax2, dir = toHi ? 1 : -1;
    html += '<path class="dirarrow" d="M' + tipX + ' ' + ay + ' l' + (-6 * dir) + ' -3 l0 6 z"/>';
    html += '<text class="dirlab" x="' + ((ax1 + ax2) / 2) + '" y="' + (ay - 4) + '" text-anchor="middle">higher priority</text>';
    svg.innerHTML = html;
  }

  // ---- absolute context ---------------------------------------------------
  function renderAbs() {
    var el = document.getElementById('pd-abs'); if (!el) return;
    // AOI median raw value + its fixed band
    var aoi = population(active, 'aoi'), med = quantile(aoi, 0.5);
    var bi = bandIndex(active, med);
    var strip = active.fixed.map(function (b, i) {
      return '<span class="pdb' + (i === bi ? ' here' : '') + '" style="background:' + ramp(PRI_STOPS, active.dir === 'lo' ? 1 - i / (active.fixed.length - 1) : i / (active.fixed.length - 1)) + '">' + b.lab + '</span>';
    }).join('');
    el.innerHTML =
      '<div class="pd-abs-read">AOI median: <b>' + fmt(med) + ' ' + active.unit.replace('·', '·') + '</b> → fixed band: <b>' + active.fixed[bi].lab + '</b></div>' +
      '<div class="pd-bandstrip">' + strip + '</div>' +
      '<div class="pd-abs-read" style="color:var(--mute); font-size:10.5px;">The relative score above is contrast <em>within</em> the reference frame — this fixed band is the absolute severity, so a high relative score in a low-severity country isn\'t read as a crisis.</div>';
  }

  // ---- text / provenance --------------------------------------------------
  function plainSummary() {
    var dirWord = ctl.dir === 'hi' ? 'Higher' : 'Lower';
    var phrase = dirWord + ' = more need';
    if (ctl.method === 'fixed') return phrase + '; classified by fixed thresholds (' + active.prov + ').';
    var verb = ctl.method === 'percentile' ? 'ranked' : ctl.method === 'zscore' ? 'z-scored' : 'scaled';
    return phrase + '; ' + verb + ' within ' + FRAME_LABEL[ctl.frame] + '.';
  }
  function provLine() {
    return ctl.method === 'fixed' ? 'Values from: ' + active.prov : 'Ranked within: ' + FRAME_LABEL[ctl.frame];
  }

  // ---- full detail render -------------------------------------------------
  function renderDetail() {
    recompute();
    var byId = function (id) { return document.getElementById(id); };
    byId('pd-theme').textContent = active.theme;
    byId('pd-name-bc').textContent = active.name;
    byId('pd-title').textContent = active.name;
    var kindPill = active.kind === 'descriptor'
      ? '<span class="pill blue"><svg class="ic-xs" aria-hidden="true"><use href="#i-eye"/></svg>DESCRIPTOR · CONTEXT</span>'
      : '<span class="pill blue"><svg class="ic-xs" aria-hidden="true"><use href="#i-target"/></svg>PRIORITY · NEED SCORE</span>';
    var sensPill = active.sens ? '<span class="pill amber"><svg class="ic-xs" aria-hidden="true"><use href="#i-lock"/></svg>NATIONALLY SENSITIVE</span>' : '';
    byId('pd-pills').innerHTML =
      '<span class="pill gray">' + active.theme.toUpperCase() + '</span>' + kindPill + sensPill +
      '<span class="pill green">NbS-AGNOSTIC</span>';
    byId('pd-what').textContent = active.what;
    var chips = '<div class="prov-chips">' +
      '<span class="prov-chip"><span class="pk">dataset</span>' + (active.grain || '—') + '</span>' +
      '<span class="prov-chip tier"><span class="pk">evidence</span>' + (active.tier || 'Tier 2') + '</span>' +
      '<span class="prov-chip' + (active.sens ? ' sens' : '') + '"><span class="pk">sensitivity</span>' + (active.sens ? 'nationally sensitive' : 'public') + '</span>' +
      '</div>';
    var endorse = active.sens ? '<div class="dsrc-flag endorsed"><svg aria-hidden="true"><use href="#i-alert"/></svg><div><b>Confirm a country-endorsed source.</b> ' + active.endorse + '</div></div>' : '';
    var upload = active.upload ? '<div class="dsrc-flag upload"><svg aria-hidden="true"><use href="#i-download"/></svg><div><b>A better local dataset may exist.</b> ' + active.upload + '</div></div>' : '';
    var quote = active.quote ? '<div class="prov-quote">' + active.quote + '</div>' : '';
    byId('pd-source').innerHTML = '<div class="source-block"><div class="src-line">' + active.source + '</div>' + chips + endorse + upload + quote + '</div>';
    byId('pd-raw-unit').textContent = active.unit;
    byId('pd-raw-lo').textContent = fmt(active.range[0]);
    byId('pd-raw-hi').textContent = fmt(active.range[1]);
    var rawBar = byId('pd-raw-bar'); if (rawBar) rawBar.style.background = 'linear-gradient(90deg,' + RAW_STOPS.join(',') + ')';
    // controls reflect state
    byId('pd-method').value = ctl.method;
    byId('pd-dir').value = ctl.dir;
    byId('pd-frame').value = ctl.frame;
    byId('pd-clip').value = ctl.clip; byId('pd-clip-val').textContent = '±' + ctl.clip + '%';
    byId('pd-method-note').textContent = METHOD_NOTE[ctl.method];
    byId('pd-dir-note').textContent = active.dir === 'lo' ? 'schema default: lower → higher' : 'schema default: higher → higher';
    byId('pd-frame-row').style.display = ctl.method === 'fixed' ? 'none' : '';
    byId('pd-dist-sub').textContent = ctl.method === 'fixed' ? 'lookup breakpoints' : 'quantile cuts';
    var plain = plainSummary();
    byId('pd-norm-plain').textContent = plain;
    byId('pd-prov').textContent = provLine();
    byId('pd-trans-cap').innerHTML = 'Right: priority score — ' +
      (ctl.method === 'fixed' ? 'fixed thresholds (' + active.prov + ')' : 'ranked within ' + FRAME_LABEL[ctl.frame]) +
      '. Both clipped to the AOI.';
    renderMaps();
    renderHist();
    renderAbs();
  }

  // ---- variable list ------------------------------------------------------
  function buildList() {
    var list = document.getElementById('pri-var-list'); if (!list) return;
    var themes = [];
    PVARS.forEach(function (p) { if (themes.indexOf(p.theme) < 0) themes.push(p.theme); });
    var html = '';
    themes.forEach(function (t) {
      var members = PVARS.filter(function (p) { return p.theme === t; });
      html += '<div class="vg">' + t + ' · ' + members.length + '</div>';
      members.forEach(function (p) {
        html += '<div class="var-item" role="option" data-key="' + p.key + '"' + (p === active ? ' aria-current="true"' : '') + '><span>' + p.name + '</span></div>';
      });
    });
    list.innerHTML = html;
    list.addEventListener('click', function (e) {
      var it = e.target.closest('.var-item[data-key]'); if (!it) return;
      var pv = PVARS.filter(function (p) { return p.key === it.dataset.key; })[0];
      if (!pv) return;
      active = pv; resetCtl(pv);
      list.querySelectorAll('.var-item').forEach(function (x) { x.removeAttribute('aria-current'); });
      it.setAttribute('aria-current', 'true');
      renderDetail();
    });
  }

  // ---- control wiring -----------------------------------------------------
  function wire() {
    var m = document.getElementById('pd-method'); m && m.addEventListener('change', function () { ctl.method = m.value; renderDetail(); });
    var d = document.getElementById('pd-dir'); d && d.addEventListener('change', function () { ctl.dir = d.value; renderDetail(); });
    var f = document.getElementById('pd-frame'); f && f.addEventListener('change', function () { ctl.frame = f.value; renderDetail(); });
    var cp = document.getElementById('pd-clip'); cp && cp.addEventListener('input', function () { ctl.clip = Number(cp.value); document.getElementById('pd-clip-val').textContent = '±' + cp.value + '%'; renderDetail(); });
  }

  // ---- view toggle (overview ↔ detail) -----------------------------------
  function wireViewToggle() {
    var tg = document.getElementById('pri-viewtoggle'); if (!tg) return;
    tg.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-pview]'); if (!b) return;
      tg.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      var detail = b.dataset.pview === 'detail';
      var ov = document.getElementById('pri-overview-view'), dv = document.getElementById('pri-detail-view');
      if (ov) ov.hidden = detail; if (dv) dv.hidden = !detail;
      if (detail) renderDetail();
    });
  }

  // ---- init ---------------------------------------------------------------
  SLEMap.init([
    { svgId: 'pd-rawmap', uid: 'pdr', cellsId: 'pd-rawmap-cells', minimal: true, title: 'Raw priority variable — Sierra Leone (mock)', desc: 'Raw variable surface, clipped to the AOI.' },
    { svgId: 'pd-transmap', uid: 'pdt', cellsId: 'pd-transmap-cells', minimal: true, title: 'Transformed priority surface — Sierra Leone (mock)', desc: 'Variable normalised to a 0–1 priority score, clipped to the AOI.' }
  ]);
  resetCtl(active);
  buildList();
  wire();
  wireViewToggle();
  renderDetail();
})();
