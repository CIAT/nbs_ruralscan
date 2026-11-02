/* ============================================================================
   SYNTHETIC EXAMPLE SURFACE — no thresholds, weights or evidence; not derived
   from any schema table (T0–T7) or register. Display fixture for the v1b
   redesign prototypes only.

   Method: seeded value noise (integer-hash lattice + smoothstep interpolation),
   three octaves (wavelengths 90 / 40 / 18 km, amplitudes 1 / .5 / .25), plus
   smooth macro gradients per theme. Exclusions and the unknown gap are
   coherent shapes (discs, a coastal band, noisy blobs). Deterministic from
   SEED 20261031. Requires sle_geo.js + v1b-map.js.

   window.FIXTURE = { cells[], districts{}, totals, practices[], ... }
   cells[i] = {lon,lat,x,y,w,h,adm2,suit,suitClass,suit2050,suitClass2050,
               need,needClass,fire,fireClass,flood,floodClass,slope,
               excluded: 'urban'|'wetland'|'protected'|null, unknown}
   ============================================================================ */
(function () {
  'use strict';
  var M = window.V1BMap;
  var SEED = 20261031;
  var HA_PER_CELL = 2500;            // nominal: 5 km x 5 km

  function hash(ix, iy, s) {
    var h = Math.imul(ix, 374761393) ^ Math.imul(iy, 668265263) ^ Math.imul(s, 0x27d4eb2d);
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  }
  function vnoise(x, y, s) {
    var ix = Math.floor(x), iy = Math.floor(y), fx = x - ix, fy = y - iy;
    var u = fx * fx * (3 - 2 * fx), v = fy * fy * (3 - 2 * fy);
    var a = hash(ix, iy, s), b = hash(ix + 1, iy, s), c = hash(ix, iy + 1, s), d = hash(ix + 1, iy + 1, s);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }
  var OCT = [[90, 1], [40, 0.7], [18, 0.45]];
  function fbm(X, Y, s) {
    var t = 0, n = 0;
    for (var k = 0; k < OCT.length; k++) {
      t += OCT[k][1] * vnoise(X / OCT[k][0] + 17.3 * k, Y / OCT[k][0] - 9.1 * k, s + 131 * k);
      n += OCT[k][1];
    }
    return t / n;                     // ~0..1, centred near .5
  }
  function c01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function kmDist(lon1, lat1, lon2, lat2) {
    var a = M.toKm(lon1, lat1), b = M.toKm(lon2, lat2);
    return Math.sqrt((a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]));
  }
  // distance to a polyline in km
  function lineDist(lon, lat, pts) {
    var p = M.toKm(lon, lat), m = Infinity;
    for (var i = 0; i < pts.length - 1; i++) {
      var a = M.toKm(pts[i][0], pts[i][1]), b = M.toKm(pts[i + 1][0], pts[i + 1][1]);
      var dx = b[0] - a[0], dy = b[1] - a[1], l2 = dx * dx + dy * dy;
      var t = c01(((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2);
      var x = a[0] + t * dx - p[0], y = a[1] + t * dy - p[1], d = Math.sqrt(x * x + y * y);
      if (d < m) m = d;
    }
    return m;
  }

  var RIVER = [[-12.35, 7.30], [-12.05, 7.62], [-11.85, 7.86], [-11.55, 8.12], [-11.35, 8.45], [-11.05, 8.80], [-10.85, 9.20]];
  var URBAN = [{ lon: -13.2317, lat: 8.4844, r: 11 }, { lon: -11.7383, lat: 7.9647, r: 9 }, { lon: -11.1875, lat: 7.8767, r: 8 }];
  var PROTECTED = [{ lon: -11.12, lat: 9.17, r: 16 }, { lon: -10.86, lat: 7.62, r: 15 }];
  var GAP = { lon: -12.05, lat: 9.52, a: 44, b: 27, rot: -0.45 };

  var cells = M.grid().map(function (g) {
    var lon = g.lon, lat = g.lat, K = M.toKm(lon, lat), X = K[0], Y = K[1];
    var dc = M.coastDistKm(lon, lat);
    var se = c01((lon + 12.5) / 1.9) * c01((9.1 - lat) / 1.7);
    var ne = c01((lat - 8.6) / 1.1) * c01((lon + 11.7) / 1.2);
    var north = c01((lat - 8.75) / 1.1);
    var east = c01((lon + 12.9) / 2.5);
    var n1 = fbm(X, Y, SEED + 11), n2 = fbm(X, Y, SEED + 7), n3 = fbm(X, Y, SEED + 13), n4 = fbm(X, Y, SEED + 19), n5 = fbm(X, Y, SEED + 23);

    var suit = 2.6 * (n1 - 0.5) + 0.16 * se - 0.14 * north - 0.16 * Math.exp(-dc / 9) + 0.05 * ne;
    var drift = -0.13 * c01((lat - 8.2) / 1.4) + 0.16 * se - 0.03 + 0.20 * (fbm(X, Y, SEED + 29) - 0.5);
    var need = 1.5 * (n2 - 0.5) + 0.32 * east + 0.24 * north;
    var fire = 1.5 * (n3 - 0.5) + 0.38 * north + 0.22 * east - 0.2 * Math.exp(-dc / 20);
    var flood = 1.3 * (n4 - 0.5) + 0.42 * Math.exp(-dc / 16) + 0.40 * Math.exp(-Math.pow(lineDist(lon, lat, RIVER) / 11, 2));
    var slope = Math.max(0, 4 + 34 * (0.6 * se + 0.7 * ne) + 18 * (n5 - 0.5));
    // livelihood hazards (exposure of people; Stage 02 sub-tab 2.3)
    var n6 = fbm(X, Y, SEED + 31), n7 = fbm(X, Y, SEED + 37), n8 = fbm(X, Y, SEED + 41);
    var drought = 1.4 * (n6 - 0.5) + 0.40 * north + 0.12 * east;
    var heat = 1.2 * (n7 - 0.5) + 0.30 * north + 0.18 * c01(dc / 60);
    var erosion = 1.2 * (n8 - 0.5) + 0.012 * slope;

    var excluded = null, i;
    for (i = 0; i < URBAN.length; i++) if (kmDist(lon, lat, URBAN[i].lon, URBAN[i].lat) < URBAN[i].r + 3 * (n5 - 0.5)) excluded = 'urban';
    if (!excluded && lat < 8.15 && lon > -13.05 && dc < 6 + 7 * (n4 - 0.5)) excluded = 'wetland';
    if (!excluded) for (i = 0; i < PROTECTED.length; i++) if (kmDist(lon, lat, PROTECTED[i].lon, PROTECTED[i].lat) < PROTECTED[i].r * (0.75 + 0.6 * n2)) excluded = 'protected';
    var unknown = false;
    if (!excluded) {
      var gx = X - M.toKm(GAP.lon, GAP.lat)[0], gy = Y - M.toKm(GAP.lon, GAP.lat)[1];
      var rx = gx * Math.cos(GAP.rot) - gy * Math.sin(GAP.rot), ry = gx * Math.sin(GAP.rot) + gy * Math.cos(GAP.rot);
      unknown = (rx * rx) / (GAP.a * GAP.a) + (ry * ry) / (GAP.b * GAP.b) < 0.75 + 0.7 * (n3 - 0.5) * 2;
    }
    return { lon: lon, lat: lat, x: g.x, y: g.y, w: g.w, h: g.h, i: g.i, j: g.j, adm2: g.adm2,
      suit: suit, suit2050: suit + drift, need: need, fire: fire, flood: flood, slope: +slope.toFixed(1),
      drought: drought, drought2050: drought + 0.10 + 0.10 * north, heat: heat, heat2050: heat + 0.16 + 0.06 * north,
      erosion: erosion, erosion2050: erosion + 0.04, flood2050: flood + 0.06 + 0.06 * Math.exp(-dc / 16),
      excluded: excluded, unknown: unknown };
  });

  // quantile classes: top 15 % very high, 25 % high, 30 % moderate, 30 % low
  function breaks(vals) {
    var s = vals.slice().sort(function (a, b) { return a - b; });
    function q(p) { return s[Math.min(s.length - 1, Math.floor(p * s.length))]; }
    return [q(0.30), q(0.60), q(0.85)];
  }
  function cls(v, b) { return v >= b[2] ? 'vh' : v >= b[1] ? 'h' : v >= b[0] ? 'm' : 'l'; }
  var eligible = cells.filter(function (c) { return !c.excluded && !c.unknown; });
  var sb = breaks(eligible.map(function (c) { return c.suit; }));
  var nb = breaks(cells.map(function (c) { return c.need; }));
  function tercile(key) {
    var s = cells.map(function (c) { return c[key]; }).sort(function (a, b) { return a - b; });
    return [s[Math.floor(0.5 * s.length)], s[Math.floor(0.75 * s.length)]];
  }
  var fb = tercile('fire'), lb = tercile('flood');
  var LH = { drought: tercile('drought'), flood: lb, erosion: tercile('erosion'), heat: tercile('heat') };
  function hcls(v, b) { return v >= b[1] ? 'high' : v >= b[0] ? 'moderate' : 'low'; }
  cells.forEach(function (c) {
    var ok = !c.excluded && !c.unknown;
    c.suitClass = c.excluded ? 'excluded' : c.unknown ? 'unknown' : cls(c.suit, sb);
    c.suitClass2050 = ok ? cls(c.suit2050, sb) : c.suitClass;   // same envelope breaks: the envelope moves
    c.needClass = cls(c.need, nb);
    c.fireClass = c.fire >= fb[1] ? 'high' : c.fire >= fb[0] ? 'moderate' : 'low';
    c.floodClass = c.flood >= lb[1] ? 'high' : c.flood >= lb[0] ? 'moderate' : 'low';
    c.lh = {}; c.lh2050 = {};
    Object.keys(LH).forEach(function (k) { c.lh[k] = hcls(c[k], LH[k]); c.lh2050[k] = hcls(c[k + '2050'], LH[k]); });
    var top = function (k) { return k === 'vh' || k === 'h'; };
    c.selected = ok && top(c.suitClass);
    c.change = !ok ? c.suitClass : top(c.suitClass) && top(c.suitClass2050) ? 'stay' :
      top(c.suitClass2050) ? 'gain' : top(c.suitClass) ? 'loss' : 'below';
  });

  // authored residents per district (example integers, not census figures)
  var RESIDENTS = { 'Bo': 575000, 'Bombali': 606000, 'Bonthe': 200000, 'Kailahun': 526000, 'Kambia': 345000,
    'Kenema': 610000, 'Koinadugu': 409000, 'Kono': 506000, 'Moyamba': 318000, 'Port Loko': 615000,
    'Pujehun': 346000, 'Tonkolili': 531000, 'Western Area Rural': 444000, 'Western Area Urban': 1055000 };

  var districts = {};
  M.districts.forEach(function (d) {
    districts[d.name] = { name: d.name, cells: 0, vh: 0, h: 0, m: 0, l: 0, excluded: 0, unknown: 0,
      selected: 0, selected2050: 0, needHigh: 0, overlap: 0, fireHigh: 0, floodHigh: 0, bothHigh: 0, anyHigh: 0,
      residents: RESIDENTS[d.name] || 0, hotspotResidents: 0 };
  });
  cells.forEach(function (c) {
    var d = districts[c.adm2]; if (!d) return;
    d.cells++; d[c.suitClass]++;
    if (c.selected) d.selected++;
    if (c.change === 'stay' || c.change === 'gain') d.selected2050++;
    var nh = c.needClass === 'vh' || c.needClass === 'h';
    if (nh) d.needHigh++;
    if (nh && c.selected) d.overlap++;
    c.hotspot = !!(nh && c.selected);
    if (c.selected) {
      var fh = c.fireClass === 'high', wh = c.floodClass === 'high';
      if (fh) d.fireHigh++; if (wh) d.floodHigh++; if (fh && wh) d.bothHigh++; if (fh || wh) d.anyHigh++;
    }
  });
  // residents spread evenly over a district's cells (example only)
  cells.forEach(function (c) {
    var d = districts[c.adm2]; if (!d || !d.cells) return;
    c.residents = d.residents / d.cells;
    if (c.hotspot) d.hotspotResidents += c.residents;
  });
  Object.keys(districts).forEach(function (k) {
    var d = districts[k];
    d.shareVHH = d.cells ? (d.vh + d.h) / d.cells : 0;
    d.share2050 = d.cells ? d.selected2050 / d.cells : 0;
    d.shareHotspot = d.selected ? d.overlap / d.selected : 0;
    d.shareFire = d.selected ? d.fireHigh / d.selected : 0;
    d.shareFlood = d.selected ? d.floodHigh / d.selected : 0;
    d.shareBoth = d.selected ? d.bothHigh / d.selected : 0;
    d.shareAny = d.selected ? d.anyHigh / d.selected : 0;
  });

  var T = { cells: cells.length, vh: 0, h: 0, m: 0, l: 0, excluded: 0, unknown: 0, urban: 0, wetland: 0, protected: 0,
    selected: 0, gain: 0, loss: 0, stay: 0, overlap: 0, fireHigh: 0, floodHigh: 0, both: 0, anyHigh: 0, hotspotResidents: 0 };
  cells.forEach(function (c) {
    T[c.suitClass]++;
    if (c.excluded) T[c.excluded]++;
    if (c.selected) T.selected++;
    if (c.change === 'gain' || c.change === 'loss' || c.change === 'stay') T[c.change]++;
    if (c.selected && (c.needClass === 'vh' || c.needClass === 'h')) T.overlap++;
    if (c.selected && c.fireClass === 'high') T.fireHigh++;
    if (c.selected && c.floodClass === 'high') T.floodHigh++;
    if (c.selected && c.fireClass === 'high' && c.floodClass === 'high') T.both++;
    if (c.selected && (c.fireClass === 'high' || c.floodClass === 'high')) T.anyHigh++;
    if (c.hotspot) T.hotspotResidents += c.residents;
  });

  // example practices for the comparison screen (authored, scoping grade)
  var practices = [
    { id: 'agro_f1', name: 'Planted silvoarable agroforestry', family: 'Trees in rows within annual cropland',
      footprintType: 'area', footprintHa: T.selected * HA_PER_CELL, overlapNeed: T.overlap / Math.max(1, T.selected),
      addresses: [
        { problem: 'Drought', strength: 2, word: 'moderate benefit', conf: 'medium confidence' },
        { problem: 'Soil erosion', strength: 3, word: 'strong benefit', conf: 'high confidence' },
        { problem: 'Rural income', strength: 2, word: 'moderate benefit', conf: 'low confidence' },
        { problem: 'Heat stress', strength: 1, word: 'weak benefit', conf: 'low confidence' }],
      cost: { low: 420, high: 1150, maint: 90, unit: 'ha', source: 'Grey literature and project documents' } },
    { id: 'riparian', name: 'Riparian buffers', family: 'Vegetated strips along streams',
      footprintType: 'linear', footprintKm: 3860, footprintHaEq: 3860 * 3, overlapNeed: 0.41,
      addresses: [
        { problem: 'Flooding', strength: 2, word: 'moderate benefit', conf: 'medium confidence' },
        { problem: 'Water quality', strength: 3, word: 'strong benefit', conf: 'high confidence' },
        { problem: 'Soil erosion', strength: 2, word: 'moderate benefit', conf: 'medium confidence' },
        { problem: 'Rural income', strength: 0, word: 'no clear effect', conf: 'low confidence' }],
      cost: { low: 1400, high: 3900, maint: 250, unit: 'km', source: 'Peer-reviewed studies, mixed regions' } },
    { id: 'anr', name: 'Assisted natural regeneration', family: 'Protecting and managing regrowth on fallow land',
      footprintType: 'area', footprintHa: 512500, overlapNeed: 0.33,
      addresses: [
        { problem: 'Soil erosion', strength: 2, word: 'moderate benefit', conf: 'medium confidence' },
        { problem: 'Drought', strength: 1, word: 'weak benefit', conf: 'low confidence' },
        { problem: 'Biodiversity loss', strength: 3, word: 'strong benefit', conf: 'medium confidence' },
        { problem: 'Rural income', strength: 1, word: 'weak benefit', conf: 'low confidence' }],
      cost: { low: 90, high: 380, maint: 25, unit: 'ha', source: 'Practitioner records (WOCAT-type)' } }
  ];

  /* Roll-ups for any control-bar state: classes {vh,h,m,l}, climate base|ssp,
     hot 'high' (need High or Very high) | 'vh' (Very high only). Counts only. */
  function rollup(st) {
    st = st || {};
    var cl = st.classes || { vh: 1, h: 1 }, ssp = st.climate === 'ssp', vhOnly = st.hot === 'vh';
    function sel(c) { var k = ssp ? c.suitClass2050 : c.suitClass; return !!cl[k]; }
    function hot(c) { return sel(c) && (vhOnly ? c.needClass === 'vh' : (c.needClass === 'vh' || c.needClass === 'h')); }
    var R = { sel: sel, hot: hot, totals: { cells: cells.length, selected: 0, overlap: 0, fireHigh: 0, floodHigh: 0, both: 0, anyHigh: 0, residentsSel: 0, hotspotResidents: 0 }, districts: {} };
    Object.keys(districts).forEach(function (k) { R.districts[k] = { name: k, cells: districts[k].cells, residents: districts[k].residents, selected: 0, overlap: 0, fireHigh: 0, floodHigh: 0, bothHigh: 0, anyHigh: 0, residentsSel: 0, hotspotResidents: 0 }; });
    cells.forEach(function (c) {
      if (!sel(c)) return;
      var d = R.districts[c.adm2], t = R.totals, fh = c.fireClass === 'high', wh = c.floodClass === 'high', h = hot(c);
      [t, d].forEach(function (o) {
        if (!o) return;
        o.selected++; o.residentsSel += c.residents;
        if (h) { o.overlap++; o.hotspotResidents += c.residents; }
        if (fh) o.fireHigh++; if (wh) o.floodHigh++;
        if (fh && wh) { if (o === t) o.both++; else o.bothHigh++; }
        if (fh || wh) o.anyHigh++;
      });
    });
    Object.keys(R.districts).forEach(function (k) {
      var d = R.districts[k], s = d.selected || 0;
      d.share = d.cells ? s / d.cells : 0;
      d.shareHotspot = s ? d.overlap / s : 0; d.shareFire = s ? d.fireHigh / s : 0; d.shareFlood = s ? d.floodHigh / s : 0;
      d.shareBoth = s ? d.bothHigh / s : 0; d.shareAny = s ? d.anyHigh / s : 0;
    });
    return R;
  }

  window.FIXTURE = Object.freeze({
    seed: SEED, haPerCell: HA_PER_CELL, cells: cells, districts: districts, totals: T,
    practices: practices, inset: { lon: -11.86, lat: 7.86, km: 20 }, rollup: rollup
  });
})();
