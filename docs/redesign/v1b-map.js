/* ============================================================================
   v1b-map.js — plate map engine for the v1b redesign prototypes.

   Projection, grid, point-in-polygon and label code adapted from
   docs/sle_map.js (originals untouched). Boundaries: docs/sle_geo.js
   (geoBoundaries gbOpen v6, CC-BY 4.0). Neighbouring coastlines (Guinea,
   Liberia) are hand-approximated for context only.

   Exposes window.V1BMap  (geometry, grid, plate rendering)
           window.V1BUI   (stage bar, scope line, drawer, segmented, accordions)
   ============================================================================ */
(function () {
  'use strict';
  var GEO = window.SLE_GEO;
  if (!GEO) { console.error('SLE_GEO not loaded'); return; }

  var VB_W = 960, VB_H = 640, DEG = Math.PI / 180;
  // country is fitted into the right of the 3:2 plate; the ocean column on the
  // left carries the title block, inset and legend.
  var FIT = { x0: 372, x1: 928, y0: 30, y1: 606 };

  function mercRaw(lon, lat) { return [lon * DEG, Math.log(Math.tan(Math.PI / 4 + lat * DEG / 2))]; }

  var lonMin = Infinity, lonMax = -Infinity, latMin = Infinity, latMax = -Infinity;
  (function scan(c) {
    if (typeof c[0] === 'number') {
      if (c[0] < lonMin) lonMin = c[0]; if (c[0] > lonMax) lonMax = c[0];
      if (c[1] < latMin) latMin = c[1]; if (c[1] > latMax) latMax = c[1];
    } else c.forEach(scan);
  })(GEO.adm0.coordinates);

  var rTL = mercRaw(lonMin, latMax), rBR = mercRaw(lonMax, latMin);
  var spanX = rBR[0] - rTL[0], spanY = rTL[1] - rBR[1];
  var S = Math.min((FIT.x1 - FIT.x0) / spanX, (FIT.y1 - FIT.y0) / spanY);
  var midRX = (rTL[0] + rBR[0]) / 2, midRY = (rTL[1] + rBR[1]) / 2;
  var TX = (FIT.x0 + FIT.x1) / 2, TY = (FIT.y0 + FIT.y1) / 2;

  function project(lon, lat) {
    var r = mercRaw(lon, lat);
    return [TX + S * (r[0] - midRX), TY - S * (r[1] - midRY)];
  }
  function invert(x, y) {
    var rx = (x - TX) / S + midRX, ry = -(y - TY) / S + midRY;
    return [rx / DEG, (2 * Math.atan(Math.exp(ry)) - Math.PI / 2) / DEG];
  }
  var LAT_C = (latMin + latMax) / 2;
  var KM_PER_DEG_LON = 111.32 * Math.cos(LAT_C * DEG);
  var PX_PER_KM = S * DEG / KM_PER_DEG_LON;   // at the centre latitude
  var CELL_KM = 5, CELL_PX = CELL_KM * PX_PER_KM;
  // km coordinates for noise / distance work (equirectangular at centre lat)
  function toKm(lon, lat) { return [(lon - lonMin) * KM_PER_DEG_LON, (lat - latMin) * 110.6]; }

  /* ---- paths ------------------------------------------------------------ */
  function ringPath(ring) {
    var d = '', i, p;
    for (i = 0; i < ring.length; i++) {
      p = project(ring[i][0], ring[i][1]);
      d += (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1);
    }
    return d + 'Z';
  }
  function geomPath(g) {
    var d = '';
    if (g.type === 'Polygon') g.coordinates.forEach(function (r) { d += ringPath(r); });
    else g.coordinates.forEach(function (p) { p.forEach(function (r) { d += ringPath(r); }); });
    return d;
  }

  /* ---- point in polygon (geographic) with bbox prefilter ---------------- */
  function bboxOf(ring) {
    var b = [Infinity, -Infinity, Infinity, -Infinity];
    ring.forEach(function (p) {
      if (p[0] < b[0]) b[0] = p[0]; if (p[0] > b[1]) b[1] = p[0];
      if (p[1] < b[2]) b[2] = p[1]; if (p[1] > b[3]) b[3] = p[1];
    });
    return b;
  }
  function pipRing(lon, lat, ring) {
    var inside = false, i, j, xi, yi, xj, yj;
    for (i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      xi = ring[i][0]; yi = ring[i][1]; xj = ring[j][0]; yj = ring[j][1];
      if (((yi > lat) !== (yj > lat)) && (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi)) inside = !inside;
    }
    return inside;
  }
  function prepGeom(g) {
    var polys = g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
    return polys.map(function (p) { return { ring: p[0], bb: bboxOf(p[0]) }; });
  }
  function pip(lon, lat, prepped) {
    for (var k = 0; k < prepped.length; k++) {
      var b = prepped[k].bb;
      if (lon < b[0] || lon > b[1] || lat < b[2] || lat > b[3]) continue;
      if (pipRing(lon, lat, prepped[k].ring)) return true;
    }
    return false;
  }

  var ADM0 = prepGeom(GEO.adm0);
  var ADM0_PATH = geomPath(GEO.adm0);

  /* ---- districts: path + pole-of-inaccessibility label point ------------ */
  function segDist(px, py, ax, ay, bx, by) {
    var dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy, t = l2 ? ((px - ax) * dx + (py - ay) * dy) / l2 : 0;
    t = t < 0 ? 0 : t > 1 ? 1 : t;
    var x = ax + t * dx - px, y = ay + t * dy - py;
    return Math.sqrt(x * x + y * y);
  }
  function screenPip(x, y, pts) {
    var inside = false;
    for (var i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      if (((pts[i][1] > y) !== (pts[j][1] > y)) &&
          (x < (pts[j][0] - pts[i][0]) * (y - pts[i][1]) / (pts[j][1] - pts[i][1]) + pts[i][0])) inside = !inside;
    }
    return inside;
  }
  function poleOf(pts) {
    var b = [Infinity, -Infinity, Infinity, -Infinity];
    pts.forEach(function (p) { if (p[0] < b[0]) b[0] = p[0]; if (p[0] > b[1]) b[1] = p[0]; if (p[1] < b[2]) b[2] = p[1]; if (p[1] > b[3]) b[3] = p[1]; });
    function score(x, y) {
      if (!screenPip(x, y, pts)) return -1;
      var m = Infinity;
      for (var i = 0; i < pts.length - 1; i++) { var d = segDist(x, y, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]); if (d < m) m = d; }
      // favour horizontal room: labels are wide
      return m;
    }
    var best = [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2], bs = -1, step = Math.max(b[1] - b[0], b[3] - b[2]) / 28, x, y, s;
    for (x = b[0]; x <= b[1]; x += step) for (y = b[2]; y <= b[3]; y += step) { s = score(x, y); if (s > bs) { bs = s; best = [x, y]; } }
    var c = best.slice(), st = step / 4;
    for (x = c[0] - step; x <= c[0] + step; x += st) for (y = c[1] - step; y <= c[1] + step; y += st) { s = score(x, y); if (s > bs) { bs = s; best = [x, y]; } }
    return { x: best[0], y: best[1], r: bs };
  }
  var DISTRICTS = GEO.adm2.map(function (u) {
    var polys = u.geometry.type === 'Polygon' ? [u.geometry.coordinates] : u.geometry.coordinates;
    var big = null, bigA = -1;
    polys.forEach(function (p) {
      var pts = p[0].map(function (c) { return project(c[0], c[1]); });
      var a = 0; for (var i = 0; i < pts.length - 1; i++) a += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1];
      a = Math.abs(a / 2); if (a > bigA) { bigA = a; big = pts; }
    });
    return { name: u.name, path: geomPath(u.geometry), prep: prepGeom(u.geometry), area: bigA, pole: poleOf(big) };
  });

  /* ---- coast: main-ring arc (Guinea border → Liberia border) + islands --- */
  var rings = GEO.adm0.coordinates.map(function (p) { return p[0]; });
  var mainIdx = 0; rings.forEach(function (r, i) { if (r.length > rings[mainIdx].length) mainIdx = i; });
  var MAIN = rings[mainIdx];
  function nearestIdx(lon, lat) {
    var bi = 0, bd = Infinity;
    MAIN.forEach(function (p, i) { var d = (p[0] - lon) * (p[0] - lon) + (p[1] - lat) * (p[1] - lat); if (d < bd) { bd = d; bi = i; } });
    return bi;
  }
  var iG = nearestIdx(-13.309, 9.0446), iL = nearestIdx(-11.4892, 6.9254);
  var arc = MAIN.slice(Math.min(iG, iL), Math.max(iG, iL) + 1);
  if (iG > iL) arc.reverse();               // arc runs Guinea → Liberia
  var COAST_KM = [];
  (function () {
    var pts = arc.slice();
    rings.forEach(function (r, i) { if (i !== mainIdx) pts = pts.concat(r); });
    var last = null;
    pts.forEach(function (p) {
      var k = toKm(p[0], p[1]);
      if (!last || Math.abs(k[0] - last[0]) + Math.abs(k[1] - last[1]) > 0.8) { COAST_KM.push(k); last = k; }
    });
  })();
  function coastDistKm(lon, lat) {
    var k = toKm(lon, lat), m = Infinity;
    for (var i = 0; i < COAST_KM.length; i++) {
      var dx = COAST_KM[i][0] - k[0], dy = COAST_KM[i][1] - k[1], d = dx * dx + dy * dy;
      if (d < m) m = d;
    }
    return Math.sqrt(m);
  }

  // ocean polygon: Liberia coast (approx) → SLE coast arc reversed → Guinea coast (approx) → far west
  var GUINEA = [[-13.33, 9.10], [-13.45, 9.27], [-13.58, 9.40], [-13.72, 9.47], [-13.66, 9.56], [-13.70, 9.70],
                [-13.84, 9.84], [-14.02, 10.02], [-14.22, 10.22], [-14.5, 10.6], [-14.8, 11.2]];
  var LIBERIA = [[-11.30, 6.80], [-11.05, 6.62], [-10.78, 6.43], [-10.45, 6.22], [-10.0, 5.9]];
  var OCEAN_PATH = (function () {
    var seq = [[-9.5, 5.3]].concat(LIBERIA.slice().reverse())
      .concat(arc.slice().reverse()).concat(GUINEA).concat([[-17.5, 11.5], [-17.5, 5.3]]);
    return ringPath(seq);
  })();
  var NEIGH_COAST_PATH = (function () {
    function line(seq) { var d = ''; seq.forEach(function (c, i) { var p = project(c[0], c[1]); d += (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }); return d; }
    return line([arc[0]].concat(GUINEA)) + line([arc[arc.length - 1]].concat(LIBERIA));
  })();

  /* ---- 5 km grid in screen space (equal cells), tagged to districts ------ */
  var GRID = null;
  function buildGrid() {
    if (GRID) return GRID;
    GRID = [];
    var tl = project(lonMin, latMax), br = project(lonMax, latMin);
    var x0 = tl[0] - CELL_PX, y0 = tl[1] - CELL_PX;
    var nx = Math.ceil((br[0] - x0) / CELL_PX) + 1, ny = Math.ceil((br[1] - y0) / CELL_PX) + 1;
    var offs = [[0.5, 0.5], [0.12, 0.12], [0.88, 0.12], [0.12, 0.88], [0.88, 0.88]];
    for (var j = 0; j < ny; j++) {
      for (var i = 0; i < nx; i++) {
        var x = x0 + i * CELL_PX, y = y0 + j * CELL_PX, hit = -1, k, ll;
        for (k = 0; k < offs.length; k++) {
          ll = invert(x + offs[k][0] * CELL_PX, y + offs[k][1] * CELL_PX);
          if (pip(ll[0], ll[1], ADM0)) { hit = k; break; }
        }
        if (hit < 0) continue;
        var c = invert(x + CELL_PX / 2, y + CELL_PX / 2), adm2 = '';
        for (k = 0; k < offs.length && !adm2; k++) {
          ll = invert(x + offs[k][0] * CELL_PX, y + offs[k][1] * CELL_PX);
          for (var d = 0; d < DISTRICTS.length; d++) if (pip(ll[0], ll[1], DISTRICTS[d].prep)) { adm2 = DISTRICTS[d].name; break; }
        }
        GRID.push({ i: i, j: j, x: x, y: y, w: CELL_PX, h: CELL_PX, lon: c[0], lat: c[1], adm2: adm2 || 'Western Area Rural' });
      }
    }
    return GRID;
  }

  function scaleBarPx(km) { return km * PX_PER_KM; }

  var CITIES = [
    { name: 'Freetown', lon: -13.2317, lat: 8.4844 },
    { name: 'Bo', lon: -11.7383, lat: 7.9647 },
    { name: 'Kenema', lon: -11.1875, lat: 7.8767 }
  ];

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }

  /* ---- plate skeleton -------------------------------------------------- */
  // Label placement overrides: tiny coastal units get a leader into the sea.
  var LEADERS = {
    'Western Area Urban': { tx: 342, ty: 0, anchor: 'end' },
    'Western Area Rural': { tx: 342, ty: 0, anchor: 'end' }
  };
  var NUDGE = { 'Bonthe': [8, -10] };
  var PLACE = { 'Bo': [-12.0, 8.2], 'Kenema': [-10.98, 8.12] };   // keep district names clear of same-name towns

  function plate(svg, opts) {
    opts = opts || {};
    var uid = opts.uid || 'p';
    buildGrid();
    var fr = project(-13.2317, 8.4844);
    var labels = DISTRICTS.map(function (d) {
      var x = d.pole.x, y = d.pole.y, n = NUDGE[d.name] || [0, 0];
      if (PLACE[d.name]) { var pp = project(PLACE[d.name][0], PLACE[d.name][1]); x = pp[0]; y = pp[1]; }
      return { name: d.name, x: x + n[0], y: y + n[1] };
    });
    svg.setAttribute('viewBox', opts.viewBox || ('0 0 ' + VB_W + ' ' + VB_H));
    svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    svg.innerHTML =
      '<defs>' +
        '<pattern id="hatch-' + uid + '" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">' +
          '<rect width="5" height="5" class="pat-paper"/><line x1="0" y1="0" x2="0" y2="5" class="pat-hatch"/></pattern>' +
        '<pattern id="dots-' + uid + '" width="4" height="4" patternUnits="userSpaceOnUse">' +
          '<rect width="4" height="4" class="pat-unknown"/><circle cx="2" cy="2" r=".62" class="pat-dot"/></pattern>' +
        '<pattern id="rm-' + uid + '" width="4" height="4" patternUnits="userSpaceOnUse">' +
          '<rect width="4" height="4" class="pat-paper"/><circle cx="2" cy="2" r=".75" class="pat-rm"/></pattern>' +
        '<clipPath id="clip-' + uid + '"><path d="' + ADM0_PATH + '"/></clipPath>' +
      '</defs>' +
      '<rect class="m-neigh" x="-400" y="-400" width="' + (VB_W + 800) + '" height="' + (VB_H + 800) + '"/>' +
      '<path class="m-ocean" d="' + OCEAN_PATH + '"/>' +
      '<path class="m-ncoast" d="' + NEIGH_COAST_PATH + '"/>' +
      (opts.context === false ? '' :
        '<text class="m-ctx" x="' + project(-10.62, 9.92)[0].toFixed(0) + '" y="' + project(-10.62, 9.92)[1].toFixed(0) + '">Guinea</text>' +
        '<text class="m-ctx" x="' + project(-10.55, 6.95)[0].toFixed(0) + '" y="' + project(-10.55, 6.95)[1].toFixed(0) + '">Liberia</text>' +
        '<text class="m-sea" x="' + project(-13.95, 7.55)[0].toFixed(0) + '" y="' + project(-13.95, 7.55)[1].toFixed(0) + '">Atlantic Ocean</text>') +
      '<path class="m-land" d="' + ADM0_PATH + '"/>' +
      '<g class="m-cells" clip-path="url(#clip-' + uid + ')"></g>' +
      '<g class="m-dfill"></g>' +
      '<g class="m-adm2">' + DISTRICTS.map(function (d) { return '<path d="' + d.path + '"/>'; }).join('') + '</g>' +
      '<path class="m-adm0" d="' + ADM0_PATH + '"/>' +
      '<g class="m-over"></g>' +
      (opts.cities === false ? '' : '<g class="m-cities">' + CITIES.map(function (c) {
        var p = project(c.lon, c.lat);
        return '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="2.6"/>';
      }).join('') + '</g>') +
      '<g class="m-labels"></g>' +
      (opts.scale === false ? '' : scaleNorth()) ;
    svg._labels = labels;
    svg._uid = uid;
    svg._opts = opts;
    if (opts.labels !== false) setLabels(svg, {});
    return svg;
  }

  function scaleNorth() {
    var seg = scaleBarPx(25), x = 926 - seg * 4, y = 612;
    return '<g class="m-scale" transform="translate(' + x.toFixed(1) + ',' + y + ')">' +
      '<rect x="0" y="0" width="' + (seg * 2).toFixed(1) + '" height="3.5" class="sb-a"/>' +
      '<rect x="' + (seg * 2).toFixed(1) + '" y="0" width="' + (seg * 2).toFixed(1) + '" height="3.5" class="sb-b"/>' +
      '<text x="0" y="-5">0</text><text x="' + (seg * 2).toFixed(1) + '" y="-5" text-anchor="middle">50</text>' +
      '<text x="' + (seg * 4).toFixed(1) + '" y="-5" text-anchor="end">100 km</text></g>' +
      '<g class="m-north" transform="translate(912,548)"><path d="M0 -14 L5 4 L0 0 L-5 4 Z"/>' +
      '<text x="0" y="17" text-anchor="middle">N</text></g>';
  }

  // labels: opts.only = [names] to label (others hidden), opts.extra = {name: '62 %'}
  function setLabels(svg, o) {
    o = o || {};
    var g = svg.querySelector('.m-labels'), out = '', fr = project(-13.2317, 8.4844);
    var cityOpt = svg._opts.cities !== false;
    var hideDistricts = svg._opts.labels === 'cities';
    if (!hideDistricts) svg._labels.forEach(function (l) {
      if (o.only && o.only.indexOf(l.name) < 0 && !LEADERS[l.name]) return;
      var extra = o.extra && o.extra[l.name];
      var cls = 'lbl' + (o.emph && o.emph.indexOf(l.name) >= 0 ? ' lbl-em' : '');
      if (LEADERS[l.name]) {
        var ty = l.name === 'Western Area Urban' ? fr[1] - 2 : fr[1] + 22;
        var sx = l.name === 'Western Area Urban' ? fr[0] - 4 : l.x;
        var sy = l.name === 'Western Area Urban' ? fr[1] - 3 : l.y;
        out += '<path class="leader lead-only" d="M' + sx.toFixed(1) + ' ' + sy.toFixed(1) + 'L' + (LEADERS[l.name].tx + 4) + ' ' + (ty - 3) + '"/>';
        out += '<text class="' + cls + ' lead-only" x="' + LEADERS[l.name].tx + '" y="' + ty + '" text-anchor="end">' + esc(l.name) +
          (extra ? '<tspan class="lbl-v" x="' + LEADERS[l.name].tx + '" dy="11">' + esc(extra) + '</tspan>' : '') + '</text>';
      } else {
        out += '<text class="' + cls + '" x="' + l.x.toFixed(1) + '" y="' + l.y.toFixed(1) + '" text-anchor="middle">' + esc(l.name) +
          (extra ? '<tspan class="lbl-v" x="' + l.x.toFixed(1) + '" dy="12">' + esc(extra) + '</tspan>' : '') + '</text>';
      }
    });
    if (cityOpt) CITIES.forEach(function (c) {
      if (c.name === 'Freetown') return;
      var p = project(c.lon, c.lat);
      var left = c.name === 'Kenema';   // keeps clear of the Kailahun district label
      out += '<text class="city" x="' + (p[0] + (left ? -5 : 5)).toFixed(1) + '" y="' + (p[1] + 3.5).toFixed(1) + '"' + (left ? ' text-anchor="end"' : '') + '>' + c.name + '</text>';
    });
    if (cityOpt) out += '<text class="city lead-only" x="' + (fr[0] - 6).toFixed(1) + '" y="' + (fr[1] + 9).toFixed(1) + '" text-anchor="end">Freetown</text>' +
      '<text class="city narrow-only" x="' + (fr[0] + 6).toFixed(1) + '" y="' + (fr[1] - 6).toFixed(1) + '">Freetown</text>';
    g.innerHTML = out;
  }

  // paint cells: keyFn(cell) -> class key or null (paper); classes map key -> css class
  function paintCells(svg, cells, keyFn, opts) {
    opts = opts || {};
    var groups = {}, order = [];
    cells.forEach(function (c) {
      var k = keyFn(c); if (k == null) return;
      if (!groups[k]) { groups[k] = ''; order.push(k); }
      var o = 0.12; // overlap: kills hairline seams
      groups[k] += 'M' + (c.x - o).toFixed(2) + ' ' + (c.y - o).toFixed(2) + 'h' + (c.w + 2 * o).toFixed(2) + 'v' + (c.h + 2 * o).toFixed(2) + 'h' + (-(c.w + 2 * o)).toFixed(2) + 'z';
    });
    var uid = svg._uid, html = '';
    order.forEach(function (k) {
      var fill = '';
      if (k === 'excluded') fill = ' fill="url(#hatch-' + uid + ')"';
      if (k === 'unknown') fill = ' fill="url(#dots-' + uid + ')"';
      if (k === 'gone') fill = ' fill="url(#rm-' + uid + ')"';
      html += '<path class="k-' + k + '"' + fill + ' d="' + groups[k] + '"/>';
    });
    // thin dark outline around excluded areas (dissolved: only edges facing non-excluded cells)
    function outline(test, cls) {
      var ex = {}, d = '';
      cells.forEach(function (c) { if (test(c)) ex[c.i + ',' + c.j] = c; });
      Object.keys(ex).forEach(function (k) {
        var c = ex[k], x0 = c.x.toFixed(2), y0 = c.y.toFixed(2), x1 = (c.x + c.w).toFixed(2), y1 = (c.y + c.h).toFixed(2);
        if (!ex[c.i + ',' + (c.j - 1)]) d += 'M' + x0 + ' ' + y0 + 'H' + x1;
        if (!ex[c.i + ',' + (c.j + 1)]) d += 'M' + x0 + ' ' + y1 + 'H' + x1;
        if (!ex[(c.i - 1) + ',' + c.j]) d += 'M' + x0 + ' ' + y0 + 'V' + y1;
        if (!ex[(c.i + 1) + ',' + c.j]) d += 'M' + x1 + ' ' + y0 + 'V' + y1;
      });
      return '<path class="' + cls + '" d="' + d + '"/>';
    }
    if (groups.excluded) html += outline(function (c) { return keyFn(c) === 'excluded'; }, 'k-outline');
    if (opts.outline) html += outline(opts.outline, 'k-sel-outline');
    svg.querySelector('.m-cells').innerHTML = html;
    svg.querySelector('.m-dfill').innerHTML = '';
  }
  // district choropleth on top of cells: fn(name) -> class key
  function paintDistricts(svg, fn) {
    svg.querySelector('.m-dfill').innerHTML = DISTRICTS.map(function (d) {
      return '<path class="k-' + fn(d.name) + '" d="' + d.path + '"/>';
    }).join('');
  }
  function overlay(svg, html) { svg.querySelector('.m-over').innerHTML = html || ''; }

  window.V1BMap = {
    VB_W: VB_W, VB_H: VB_H, FIT: FIT, CELL_PX: CELL_PX, PX_PER_KM: PX_PER_KM,
    project: project, invert: invert, toKm: toKm, coastDistKm: coastDistKm,
    grid: buildGrid, districts: DISTRICTS, cities: CITIES, adm0Path: ADM0_PATH,
    plate: plate, paintCells: paintCells, paintDistricts: paintDistricts, setLabels: setLabels, overlay: overlay,
    bounds: { lonMin: lonMin, lonMax: lonMax, latMin: latMin, latMax: latMax },
    esc: esc
  };

  /* ======================================================================
     V1BUI — page chrome shared across the prototypes
     ====================================================================== */
  var STAGES = [
    { n: 1, name: 'Setup', href: '01-setup.html' },
    { n: 2, name: 'Explore the practices', href: '02-practices.html' },
    { n: 3, name: 'Opportunity space', href: '03-opportunity.html' },
    { n: 4, name: 'Project risk', href: '04-risk.html' },
    { n: 5, name: 'Priority hotspots', href: '05-hotspots.html' },
    { n: 6, name: 'NbS comparison', href: '06-comparison.html' },
    { n: 7, name: 'Next steps', href: '07-next.html' }
  ];
  /* ---- control bar state (shared across pages, remembered per viewer) ---- */
  var PRACTICES = [
    { id: 'agro_f1', short: 'Planted silvoarable', name: 'planted silvoarable agroforestry' },
    { id: 'riparian', short: 'Riparian buffers', name: 'riparian buffers' },
    { id: 'anr', short: 'Natural regeneration', name: 'assisted natural regeneration' }
  ];
  var CLASSES = [['vh', 'Very high'], ['h', 'High'], ['m', 'Moderate'], ['l', 'Low']];
  var STATE = { practices: ['agro_f1'], classes: { vh: 1, h: 1, m: 0, l: 0 }, view: 'cells', climate: 'base', hot: 'high' };
  try {
    var saved = JSON.parse(window.localStorage.getItem('v1b-controls') || 'null');
    if (saved && saved.classes && saved.practices && saved.practices.length) STATE = Object.assign(STATE, saved);
  } catch (e) { /* storage unavailable: defaults */ }
  if (/[?&]reset=1/.test(window.location.search)) STATE = { practices: ['agro_f1'], classes: { vh: 1, h: 1, m: 0, l: 0 }, view: 'cells', climate: 'base', hot: 'high' };
  (function () {   // URL overrides for review links / screenshots (not saved)
    var q = new URLSearchParams(window.location.search);
    if (/^(cells|adm2|adm3)$/.test(q.get('view') || '')) STATE.view = q.get('view');
    if (/^(base|ssp)$/.test(q.get('climate') || '')) STATE.climate = q.get('climate');
    if (/^(high|vh)$/.test(q.get('hot') || '')) STATE.hot = q.get('hot');
    if (q.get('classes')) { var c = { vh: 0, h: 0, m: 0, l: 0 }; q.get('classes').split(',').forEach(function (k) { if (k in c) c[k] = 1; }); STATE.classes = c; }
  })();
  var LISTENERS = [];
  function save() { try { window.localStorage.setItem('v1b-controls', JSON.stringify(STATE)); } catch (e) { /* ignore */ } }
  function emit() { save(); LISTENERS.forEach(function (fn) { fn(STATE); }); }
  function onControls(fn) { LISTENERS.push(fn); fn(STATE); }
  function setState(part) { Object.assign(STATE, part); renderBar(); emit(); }

  function classWords(st) {
    var on = CLASSES.filter(function (c) { return st.classes[c[0]]; }).map(function (c) { return c[1]; });
    return on.join(' + ') || 'No classes';
  }
  function practiceWords(st) {
    var names = st.practices.map(function (id) { return PRACTICES.filter(function (p) { return p.id === id; })[0].name; });
    return names;
  }
  // one-line scope caption for plates and figure captions
  function scopeText(st, o) {
    st = st || STATE; o = o || {};
    var parts = [];
    var pw = practiceWords(st);
    parts.push(pw[0].charAt(0).toUpperCase() + pw[0].slice(1) + (pw.length > 1 ? ' (map shows this practice; ' + (pw.length - 1) + ' more selected)' : ''));
    if (!o.noClasses) parts.push(classWords(st));
    parts.push('Sierra Leone');
    parts.push(st.view === 'cells' ? '5 km cells' : st.view === 'adm2' ? 'districts (Admin 2)' : 'Admin 3 not in this example — districts shown');
    parts.push(st.climate === 'ssp' ? 'SSP2-4.5, about 2050' : 'baseline 1995–2014');
    return parts.join(' · ');
  }

  function controlBar(opts) {
    opts = opts || {};
    var st = STATE;
    function seg(k, items, multi) {
      return '<div class="seg cb-seg" data-k="' + k + '"' + (multi ? ' data-multi="1"' : '') + ' role="group">' + items.map(function (it) {
        var on = multi ? !!st[k][it[0]] : st[k] === it[0];
        return '<button type="button" data-v="' + it[0] + '" aria-pressed="' + on + '">' + it[1] + '</button>';
      }).join('') + '</div>';
    }
    var chips = st.practices.map(function (id) {
      var p = PRACTICES.filter(function (x) { return x.id === id; })[0];
      return '<span class="cb-chip">' + p.short + (st.practices.length > 1 ? '<button type="button" class="cb-x" data-rm="' + id + '" aria-label="Remove ' + p.short + '">×</button>' : '') + '</span>';
    }).join('');
    var menu = PRACTICES.map(function (p) {
      return '<label><input type="checkbox" data-p="' + p.id + '"' + (st.practices.indexOf(p.id) >= 0 ? ' checked' : '') + '> ' + p.short + '</label>';
    }).join('');
    return '<div class="cb-in">' +
      '<div class="cb-g cb-prac"><span class="cb-l" id="cbl-p">Practice</span><div class="cb-chips" aria-labelledby="cbl-p">' + chips +
        '<button type="button" class="cb-add" aria-expanded="false" aria-haspopup="true">+ Add</button>' +
        '<div class="cb-menu" hidden>' + menu + '</div></div></div>' +
      '<div class="cb-g cb-extent"><span class="cb-l">Opportunity extent · select classes</span>' + seg('classes', CLASSES, true) + '<small>Selected: ' + classWords(st) + '. At least one class; default Very high + High.</small></div>' +
      '<div class="cb-g"><span class="cb-l">View</span>' + seg('view', [['cells', '5 km cells'], ['adm2', 'Admin 2'], ['adm3', 'Admin 3']]) + '</div>' +
      '<div class="cb-g"><span class="cb-l">Climate</span>' + seg('climate', [['base', 'Baseline 1995–2014'], ['ssp', 'SSP2-4.5 ~2050']]) + '</div>' +
      (opts.hotspot ? '<div class="cb-g"><span class="cb-l">Hotspot score</span>' + seg('hot', [['high', 'High+'], ['vh', 'Very high']]) + '</div>' : '') +
      '</div>';
  }
  var BAR_OPTS = {};
  function renderBar() {
    var el = document.getElementById('ctlbar');
    if (el) el.innerHTML = controlBar(BAR_OPTS);
  }
  function wireBar() {
    var el = document.getElementById('ctlbar');
    if (!el) return;
    el.addEventListener('click', function (e) {
      var b = e.target.closest('.cb-seg button');
      if (b) {
        var g = b.parentNode, k = g.getAttribute('data-k'), v = b.getAttribute('data-v');
        if (g.getAttribute('data-multi')) {
          var next = Object.assign({}, STATE.classes); next[v] = next[v] ? 0 : 1;
          if (!CLASSES.some(function (c) { return next[c[0]]; })) return;   // keep at least one class
          STATE.classes = next;
        } else STATE[k] = v;
        renderBar(); emit(); return;
      }
      var rm = e.target.closest('[data-rm]');
      if (rm) { STATE.practices = STATE.practices.filter(function (id) { return id !== rm.getAttribute('data-rm'); }); renderBar(); emit(); return; }
      var add = e.target.closest('.cb-add');
      if (add) { var m = el.querySelector('.cb-menu'); m.hidden = !m.hidden; add.setAttribute('aria-expanded', String(!m.hidden)); }
    });
    el.addEventListener('change', function (e) {
      var cb = e.target.closest('[data-p]'); if (!cb) return;
      var id = cb.getAttribute('data-p'), list = STATE.practices.filter(function (x) { return x !== id; });
      if (cb.checked) list.push(id);
      if (!list.length) { cb.checked = true; return; }
      STATE.practices = PRACTICES.map(function (p) { return p.id; }).filter(function (x) { return list.indexOf(x) >= 0; });
      renderBar(); emit();
    });
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.cb-chips')) { var m = el.querySelector('.cb-menu'); if (m && !m.hidden) { m.hidden = true; } }
    });
  }

  function stageBar(current) {
    var steps = STAGES.map(function (s) {
      var state = current > 0 && s.n < current ? 'done' : s.n === current ? 'now' : 'next';
      var mark = state === 'done' && s.href ? '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 6.3l2.3 2.3 4.7-5"/></svg>' : s.n;
      var inner = '<span class="st-n">' + mark + '</span><span class="st-name">' + s.name + '</span>';
      if (!s.href) return '<li class="st st-' + state + ' st-off" title="Not prototyped in this round">' + inner + '</li>';
      return '<li class="st st-' + state + '"><a href="' + s.href + '"' + (state === 'now' ? ' aria-current="step"' : '') + '>' + inner + '</a></li>';
    }).join('');
    var home = '<li class="st st-home' + (current === 0 ? ' st-now' : '') + '"><a href="index.html"' + (current === 0 ? ' aria-current="page"' : '') + ' title="Home"><span class="st-n st-house"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M1.8 6.2L6 2.4l4.2 3.8M3.2 5.2v4.4h5.6V5.2"/></svg></span><span class="st-name">Home</span></a></li>';
    return '<header class="stagebar"><div class="sb-in">' +
      '<a class="sb-proj" href="index.html" title="Home">Rural NbS Scan<span> · Sierra Leone example</span></a>' +
      '<ol class="stepper" aria-label="Stages">' + home + steps + '</ol>' +
      (current === 0 ? '' : '<a class="btn-ghost tc-link" href="00-config.html">Configuration</a>') +
      '</div></header>' +
      (current === 0 ? '' : '<div class="ctlbar" id="ctlbar" role="region" aria-label="Controls"></div>');
  }

  var JUMP = { practice: '00-config.html?tab=2', classes: '00-config.html?tab=2', geo: '00-config.html?tab=1', grain: '00-config.html?tab=1',
    period: '01-setup.html', priorities: '05-hotspots.html?tab=2', data: '00-config.html?tab=1', rules: '00-config.html?tab=2' };
  function drawer() {
    var sec = [
      ['practice', 'Practice and suitability family', '<p>Agroforestry, family F1 — planted silvoarable (trees in rows within annual cropland). Each family is mapped separately because each is limited by a different factor.</p><label class="fld"><span>Practice</span><select><option>Agroforestry · planted silvoarable</option><option>Agroforestry · regeneration-based</option><option>Riparian buffers</option></select></label>'],
      ['classes', 'Classes carried forward', '<p>Which suitability classes count as the opportunity space for later stages.</p><div class="checks"><label><input type="checkbox" checked> Very high</label><label><input type="checkbox" checked> High</label><label><input type="checkbox"> Moderate</label></div>'],
      ['geo', 'Area of interest', '<p>Sierra Leone, whole country. Districts from geoBoundaries (open licence). Upload a project boundary to narrow the scan.</p>'],
      ['grain', 'Cell size', '<p>5 km cells. Coarser cells run faster but hide small features; slope-based rules are not meaningful above about 90 m and are derived first, then aggregated.</p>'],
      ['period', 'Climate period', '<p>Baseline 1995–2014. Future: SSP2-4.5, around 2050.</p>'],
      ['priorities', 'Priorities', '<p>Priorities choose which need layers are shown in Stage 04. Two example presets:</p><ul class="presets"><li><b>Climate resilience + Livelihoods</b> (selected) — drought exposure, rural poverty, food insecurity</li><li><b>Biodiversity + Water security</b> — habitat intactness, water stress, downstream users</li></ul><p>A preset frames the layers; it does not re-weight them.</p>'],
      ['data', 'Datasets — choosing a source', '<p>Which dataset represents each variable (for example a national soil map instead of a global one). Changing a source does not change any rule.</p>'],
      ['rules', 'Rules — tuning a response', '<p>How a variable is turned into suitability (the response curve and its weight). Rules come from the evidence register; editing them is a separate, logged action.</p>']
    ];
    return '<aside class="drawer" id="drawer" aria-hidden="true" aria-label="Technical configuration">' +
      '<div class="dr-head"><h2>Quick settings</h2><button type="button" class="dr-close" aria-label="Close">Close</button></div>' +
      '<p class="dr-lede">Quick jumps. The full settings live on the <a href="00-config.html">technical configuration page</a>: <b>choosing datasets</b> and <b>tuning rules</b> are two separate jobs.</p>' +
      sec.map(function (s) { return '<section class="dr-sec" id="dr-' + s[0] + '"><h3>' + s[1] + '</h3>' + s[2] + (JUMP[s[0]] ? '<p><a href="' + JUMP[s[0]] + '">Open in technical configuration →</a></p>' : '') + '</section>'; }).join('') +
      '<p class="dr-foot">Prototype — controls are inert.</p></aside><div class="scrim" hidden></div>';
  }

  function openDrawer(key) {
    var d = document.getElementById('drawer'), sc = document.querySelector('.scrim');
    var panel = key === 'panel';
    d.classList.toggle('panel-mode', panel);
    d.querySelector('.dr-head h2').textContent = panel ? 'Evidence details' : 'Quick settings';
    d.setAttribute('aria-label', panel ? 'Evidence details' : 'Technical configuration');
    d.classList.add('open'); d.setAttribute('aria-hidden', 'false'); sc.hidden = false;
    document.querySelectorAll('.dr-sec').forEach(function (s) { s.classList.remove('hl'); });
    var t = document.getElementById('dr-' + key);
    if (t) { t.classList.add('hl'); d.scrollTop = t.offsetTop - 80; }
  }
  function closeDrawer() {
    var d = document.getElementById('drawer'); d.classList.remove('open'); d.setAttribute('aria-hidden', 'true');
    document.querySelector('.scrim').hidden = true;
  }

  var chromeReady = false;
  function chrome(current, opts) {
    var top = document.getElementById('chrome');
    BAR_OPTS = opts || {};
    if (top) top.innerHTML = stageBar(current);
    renderBar();
    if (chromeReady) return;
    chromeReady = true;
    wireBar();
    // sticky offsets: sub-tab strips dock under the stage bar + control bar
    function measure() {
      var h = top ? top.getBoundingClientRect().height : 0;
      if (window.matchMedia('(max-width: 760px)').matches) h = 48;
      document.documentElement.style.setProperty('--chrome-h', Math.round(h) + 'px');
    }
    measure();
    if (window.ResizeObserver && top) new ResizeObserver(measure).observe(top);
    window.addEventListener('resize', measure);
    document.body.insertAdjacentHTML('beforeend', drawer());
    document.addEventListener('click', function (e) {
      var t = e.target.closest('[data-drawer]');
      if (t) { openDrawer(t.getAttribute('data-drawer')); return; }
      if (e.target.closest('.dr-close') || e.target.classList.contains('scrim')) closeDrawer();
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeDrawer(); });
  }

  // segmented control: <div class="seg" data-seg="name"><button data-v="a" aria-pressed="true">…
  function segmented(root, onChange) {
    var btns = root.querySelectorAll('button');
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        btns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        onChange(b.getAttribute('data-v'));
      });
    });
  }

  // drawer panel with arbitrary content (e.g. evidence for a response row)
  function openPanel(title, html) {
    var sec = document.getElementById('dr-panel');
    if (!sec) {
      document.getElementById('drawer').querySelector('.dr-lede').insertAdjacentHTML('afterend', '<section class="dr-sec" id="dr-panel"></section>');
      sec = document.getElementById('dr-panel');
    }
    sec.innerHTML = '<h3>' + title + '</h3>' + html;
    openDrawer('panel');
  }

  // numbered sub-tabs: <div class="subtabs" role="tablist"> buttons aria-controls panels; ?tab=N opens N
  function tabs(root, onOpen) {
    var list = Array.prototype.slice.call(root.querySelectorAll('[role=tab]'));
    function open(n) {
      list.forEach(function (t, i) {
        var on = i === n; t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1;
        var pnl = document.getElementById(t.getAttribute('aria-controls')); if (pnl) pnl.hidden = !on;
        if (on && root.scrollWidth > root.clientWidth) root.scrollLeft = Math.max(0, t.offsetLeft - 16);
      });
      if (onOpen) onOpen(n);
    }
    list.forEach(function (t, i) {
      if (t.tagName === 'A') return;
      t.addEventListener('click', function () { open(i); });
      t.addEventListener('keydown', function (e) {
        var n = e.key === 'ArrowRight' ? (i + 1) % list.length : e.key === 'ArrowLeft' ? (i + list.length - 1) % list.length : -1;
        if (n >= 0 && list[n].tagName !== 'A') { open(n); list[n].focus(); }
      });
    });
    var q = +(new URLSearchParams(window.location.search).get('tab') || 0);
    if (q >= 1 && q <= list.length && list[q - 1].tagName !== 'A') open(q - 1);
    return open;
  }

  window.V1BUI = { chrome: chrome, setState: setState, tabs: tabs, segmented: segmented, openDrawer: openDrawer, openPanel: openPanel,
    onControls: onControls, scopeText: scopeText, classWords: classWords, practices: PRACTICES,
    get state() { return STATE; } };
})();
