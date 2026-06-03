/* ============================================================================
   sle_map.js — cartographic thematic-map engine for the Rural NbS Scan tool.

   Renders an authentic Sierra Leone basemap from real administrative
   boundaries (geoBoundaries gbOpen v6, CC-BY 4.0; see sle_geo.js) using a
   self-contained Mercator projection + SVG path generator. No external libs,
   no runtime network fetches.

   Country-agnostic by design: the engine never hard-codes level words. The
   data module carries the local level name (meta.adm2_level_name) which the
   host shows only as a muted secondary annotation.

   Exposes window.SLEMap:
     .init(configs)                  build projection + grid + basemaps
     .GRID                           [{lon,lat,x,y,w,h,gi,gj,adm2}]
     .gSuit(lon,lat,scenario)        mock suitability surface 0..1
     .gPrio(lon,lat)                 mock priority surface 0..1
     .scenario                       'baseline' | 'ssp' | 'delta'
     .project(lon,lat) -> [x,y]
   ============================================================================ */
(function () {
  'use strict';

  var GEO = window.SLE_GEO;
  if (!GEO) { console.error('SLE_GEO not loaded'); return; }

  var VB_W = 600, VB_H = 400;          // viewBox of every map svg
  var PAD = 24;                        // inset for projection fit
  var DEG = Math.PI / 180;

  /* ---- Mercator projection, fitted to the ADM0 bounds --------------------- */
  function mercRaw(lon, lat) {
    return [lon * DEG, Math.log(Math.tan(Math.PI / 4 + (lat * DEG) / 2))];
  }

  // geographic + raw bounds over ADM0
  var lonMin = Infinity, lonMax = -Infinity, latMin = Infinity, latMax = -Infinity;
  (function scan(coords) {
    if (typeof coords[0] === 'number') {
      if (coords[0] < lonMin) lonMin = coords[0];
      if (coords[0] > lonMax) lonMax = coords[0];
      if (coords[1] < latMin) latMin = coords[1];
      if (coords[1] > latMax) latMax = coords[1];
    } else { coords.forEach(scan); }
  })(GEO.adm0.coordinates);

  var rawTL = mercRaw(lonMin, latMax), rawBR = mercRaw(lonMax, latMin);
  var rawMinX = rawTL[0], rawMaxX = rawBR[0];
  var rawMinY = rawBR[1], rawMaxY = rawTL[1];
  var spanX = rawMaxX - rawMinX, spanY = rawMaxY - rawMinY;
  var S = Math.min((VB_W - 2 * PAD) / spanX, (VB_H - 2 * PAD) / spanY);
  var midRX = (rawMinX + rawMaxX) / 2, midRY = (rawMinY + rawMaxY) / 2;
  var TX = VB_W / 2, TY = VB_H / 2;

  function project(lon, lat) {
    var r = mercRaw(lon, lat);
    return [TX + S * (r[0] - midRX), TY - S * (r[1] - midRY)];
  }

  /* ---- SVG path generation ----------------------------------------------- */
  function ringToPath(ring) {
    var d = '', i, p;
    for (i = 0; i < ring.length; i++) {
      p = project(ring[i][0], ring[i][1]);
      d += (i === 0 ? 'M' : 'L') + p[0].toFixed(1) + ' ' + p[1].toFixed(1);
    }
    return d + 'Z';
  }
  function geomToPath(geom) {
    var d = '';
    if (geom.type === 'Polygon') {
      geom.coordinates.forEach(function (r) { d += ringToPath(r); });
    } else { // MultiPolygon
      geom.coordinates.forEach(function (poly) {
        poly.forEach(function (r) { d += ringToPath(r); });
      });
    }
    return d;
  }

  /* ---- point-in-polygon (geographic) ------------------------------------- */
  function pipRing(lon, lat, ring) {
    var inside = false, i, j, xi, yi, xj, yj;
    for (i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      xi = ring[i][0]; yi = ring[i][1]; xj = ring[j][0]; yj = ring[j][1];
      if (((yi > lat) !== (yj > lat)) &&
          (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi)) inside = !inside;
    }
    return inside;
  }
  function pipGeom(lon, lat, geom) {
    if (geom.type === 'Polygon') return pipRing(lon, lat, geom.coordinates[0]);
    for (var k = 0; k < geom.coordinates.length; k++) {
      if (pipRing(lon, lat, geom.coordinates[k][0])) return true;
    }
    return false;
  }

  /* ---- per-unit bbox + largest-polygon centroid (screen space) ----------- */
  function geomBBox(geom) {
    var b = { lonMin: Infinity, lonMax: -Infinity, latMin: Infinity, latMax: -Infinity };
    (function s(c) {
      if (typeof c[0] === 'number') {
        if (c[0] < b.lonMin) b.lonMin = c[0]; if (c[0] > b.lonMax) b.lonMax = c[0];
        if (c[1] < b.latMin) b.latMin = c[1]; if (c[1] > b.latMax) b.latMax = c[1];
      } else c.forEach(s);
    })(geom.coordinates);
    return b;
  }
  function ringArea(pts) { // screen-space signed area
    var a = 0;
    for (var i = 0; i < pts.length - 1; i++) a += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1];
    return a / 2;
  }
  function ringCentroid(pts) {
    var a = 0, cx = 0, cy = 0, i, x0, y0, x1, y1, f;
    for (i = 0; i < pts.length - 1; i++) {
      x0 = pts[i][0]; y0 = pts[i][1]; x1 = pts[i + 1][0]; y1 = pts[i + 1][1];
      f = x0 * y1 - x1 * y0; a += f; cx += (x0 + x1) * f; cy += (y0 + y1) * f;
    }
    a *= 0.5;
    if (Math.abs(a) < 1e-6) {
      var sx = 0, sy = 0; pts.forEach(function (p) { sx += p[0]; sy += p[1]; });
      return [sx / pts.length, sy / pts.length];
    }
    return [cx / (6 * a), cy / (6 * a)];
  }
  // largest exterior ring of a unit, projected, + its centroid
  function unitLabelPoint(geom) {
    var rings = [];
    if (geom.type === 'Polygon') rings.push(geom.coordinates[0]);
    else geom.coordinates.forEach(function (poly) { rings.push(poly[0]); });
    var best = null, bestA = -1;
    rings.forEach(function (ring) {
      var proj = ring.map(function (c) { return project(c[0], c[1]); });
      var a = Math.abs(ringArea(proj));
      if (a > bestA) { bestA = a; best = proj; }
    });
    return { c: ringCentroid(best), area: bestA };
  }

  /* ---- mock data surfaces (geographic) ----------------------------------- */
  function frac(x) { var n = Math.sin(x) * 43758.5453; return n - Math.floor(n); }
  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

  // Suitability: peaks in the SE interior hill country (Bo/Kenema/Kailahun),
  // declines to the dry north and the urban/coastal west.
  function gSuit(lon, lat, scenario) {
    var dx = (lon - (-11.0)) / 1.6;
    var dy = (lat - 8.0) / 1.30;
    var s = 1 - Math.sqrt(dx * dx + dy * dy) * 0.95;
    s += (frac(lon * 91.7 + lat * 47.3) - 0.5) * 0.18;
    if (lat > 9.2) s -= 0.22;                       // drier northern fringe
    if (scenario === 'ssp') {
      // Mid-century SSP2-4.5: a SMOOTH climate-stress field (no hard steps).
      // Suitability erodes in the hot, drying north & far north-east, with
      // modest gains on the cooler, wetter south-eastern uplands.
      var north  = clamp01((lat - 8.0) / 1.6);                       // 0 south -> 1 far north
      var seHill = clamp01((lon + 11.6) / 1.2) * clamp01((8.6 - lat) / 1.2); // east & south
      var delta = -0.04 - 0.10 * north + 0.16 * seHill;
      delta += (frac(lon * 71.3 + lat * 19.7) - 0.5) * 0.035;        // gentle texture
      s += delta;
    }
    return clamp01(s);
  }
  // Priority (need/impact): peaks toward the eastern hotspot belt.
  function gPrio(lon, lat) {
    var dx = (lon - (-10.85)) / 1.35;
    var dy = (lat - 8.05) / 1.25;
    var s = 1 - Math.sqrt(dx * dx + dy * dy) * 0.92;
    s += (frac(lon * 53.1 + lat * 17.9) - 0.5) * 0.22;
    return clamp01(s);
  }
  // Mock RAW slope surface (degrees, 0..40): steeper toward the eastern uplands
  // and far north-east; gentle along the coast and major valleys.
  function gSlope(lon, lat) {
    var east = clamp01((lon + 12.7) / 2.3);                 // 0 west -> 1 east
    var hill = clamp01((lon + 11.4) / 1.4) * clamp01((8.9 - lat) / 1.6); // SE upland
    var ne   = clamp01((lat - 8.6) / 1.1) * clamp01((lon + 11.6) / 1.4); // far NE
    var d = 3 + 24 * east * 0.5 + 22 * hill + 16 * ne;
    d += (frac(lon * 33.7 + lat * 21.3) - 0.5) * 9;          // texture
    return Math.max(0, Math.min(40, d));
  }

  /* ---- build the 5 km grid (clipped to ADM0, tagged to ADM2) ------------- */
  var GRID = [];
  function buildGrid() {
    var STEP = 0.05;                                // ~5.5 km
    var units = GEO.adm2.map(function (u) { return { name: u.name, geom: u.geometry, bb: geomBBox(u.geometry) }; });
    var gj = 0;
    for (var lat = latMax; lat >= latMin; lat -= STEP, gj++) {
      var gi = 0;
      for (var lon = lonMin; lon <= lonMax; lon += STEP, gi++) {
        if (!pipGeom(lon, lat, GEO.adm0)) continue;
        // assign ADM2
        var adm2 = '';
        for (var u = 0; u < units.length; u++) {
          var b = units[u].bb;
          if (lon < b.lonMin || lon > b.lonMax || lat < b.latMin || lat > b.latMax) continue;
          if (pipGeom(lon, lat, units[u].geom)) { adm2 = units[u].name; break; }
        }
        var nw = project(lon - STEP / 2, lat + STEP / 2);
        var se = project(lon + STEP / 2, lat - STEP / 2);
        GRID.push({
          lon: lon, lat: lat, gi: gi, gj: gj,
          x: +nw[0].toFixed(1), y: +nw[1].toFixed(1),
          w: +(se[0] - nw[0] + 0.4).toFixed(1), h: +(se[1] - nw[1] + 0.4).toFixed(1),
          adm2: adm2
        });
      }
    }
  }

  /* ---- decorations: scale bar (honest) ----------------------------------- */
  function scaleBarPx(km) {
    var latC = (latMin + latMax) / 2;
    var p1 = project(lonMin, latC), p2 = project(lonMax, latC);
    var kmSpan = (lonMax - lonMin) * 111.32 * Math.cos(latC * DEG);
    var pxSpan = Math.abs(p2[0] - p1[0]);
    return km * (pxSpan / kmSpan);
  }

  /* ---- cities ------------------------------------------------------------ */
  var CITIES = [
    { name: 'Freetown', lon: -13.2317, lat: 8.4844, anchor: 'start', dx: 8, dy: -7 },
    { name: 'Bo',       lon: -11.7383, lat: 7.9647, anchor: 'start', dx: 7, dy: 4 },
    { name: 'Kenema',   lon: -11.1875, lat: 7.8767, anchor: 'start', dx: 7, dy: 12 }
  ];

  /* ---- small SVG helpers ------------------------------------------------- */
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }

  /* ---- build static base layers into one svg ----------------------------- */
  function buildBase(svg, opts) {
    opts = opts || {};
    var uid = opts.uid || 'm';
    var adm0Path = geomToPath(GEO.adm0);

    // graticule (faint, integer degrees)
    var grat = '';
    var L, T;
    for (L = Math.ceil(lonMin); L <= Math.floor(lonMax); L++) {
      T = project(L, latMax); var Bp = project(L, latMin);
      grat += '<line x1="' + T[0].toFixed(1) + '" y1="' + T[1].toFixed(1) +
              '" x2="' + Bp[0].toFixed(1) + '" y2="' + Bp[1].toFixed(1) + '"/>';
    }
    for (L = Math.ceil(latMin); L <= Math.floor(latMax); L++) {
      var Lp = project(lonMin, L), Rp = project(lonMax, L);
      grat += '<line x1="' + Lp[0].toFixed(1) + '" y1="' + Lp[1].toFixed(1) +
              '" x2="' + Rp[0].toFixed(1) + '" y2="' + Rp[1].toFixed(1) + '"/>';
    }

    // ADM2 fills + borders
    var fills = '', borders = '';
    GEO.adm2.forEach(function (u) {
      var p = geomToPath(u.geometry);
      fills += '<path d="' + p + '"/>';
      borders += '<path d="' + p + '"/>';
    });

    // ADM2 labels (centroid; tiny units get a leader line out to sea)
    var pts = GEO.adm2.map(function (u) {
      var lp = unitLabelPoint(u.geometry);
      return { name: u.name, x: lp.c[0], y: lp.c[1], area: lp.area };
    });
    pts.sort(function (a, b) { return b.area - a.area; });
    var labels = '';
    var leaderTargets = { 'Western Area Urban': { x: 70, y: 250 }, 'Western Area Rural': { x: 70, y: 272 } };
    pts.forEach(function (p) {
      if (leaderTargets[p.name]) {
        var t = leaderTargets[p.name];
        labels += '<line x1="' + p.x.toFixed(1) + '" y1="' + p.y.toFixed(1) +
                  '" x2="' + (t.x + 2) + '" y2="' + (t.y - 3) + '" class="sle-leader"/>' +
                  '<text x="' + t.x + '" y="' + t.y + '" text-anchor="end" class="sle-adm2-lbl">' + esc(p.name) + '</text>';
      } else {
        labels += '<text x="' + p.x.toFixed(1) + '" y="' + p.y.toFixed(1) + '" class="sle-adm2-lbl">' + esc(p.name) + '</text>';
      }
    });

    // cities
    var cityG = '';
    CITIES.forEach(function (c) {
      var p = project(c.lon, c.lat);
      cityG += '<circle cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="3.6" class="sle-city-dot"/>' +
               '<text x="' + (p[0] + c.dx).toFixed(1) + '" y="' + (p[1] + c.dy).toFixed(1) +
               '" text-anchor="' + c.anchor + '" class="sle-city-lbl">' + esc(c.name) + '</text>';
    });

    // scale bar (bottom-right sea)
    var bx = 470, by = 372, seg = scaleBarPx(50);
    var scaleG =
      '<g transform="translate(' + bx + ',' + by + ')" class="sle-scale">' +
        '<rect x="0" y="0" width="' + seg.toFixed(1) + '" height="4" class="sle-scale-fill"/>' +
        '<rect x="' + seg.toFixed(1) + '" y="0" width="' + seg.toFixed(1) + '" height="4" class="sle-scale-empty"/>' +
        '<text x="0" y="14">0</text>' +
        '<text x="' + seg.toFixed(1) + '" y="14" text-anchor="middle">50</text>' +
        '<text x="' + (seg * 2).toFixed(1) + '" y="14" text-anchor="middle">100 km</text>' +
      '</g>';

    // north arrow (right sea, upper)
    var northG =
      '<g transform="translate(548,150)" class="sle-north">' +
        '<circle cx="0" cy="6" r="13"/>' +
        '<path d="M0 -4 L 5 14 L 0 9 L -5 14 Z" class="sle-north-needle"/>' +
        '<text x="0" y="31" text-anchor="middle">N</text>' +
      '</g>';

    svg.innerHTML =
      '<title>' + esc(opts.title || 'Sierra Leone thematic map') + '</title>' +
      '<desc>' + esc(opts.desc || '') + '</desc>' +
      '<defs>' +
        '<pattern id="sea-' + uid + '" width="7" height="7" patternUnits="userSpaceOnUse">' +
          '<rect width="7" height="7" fill="#dce7ec"/>' +
          '<line x1="0" y1="7" x2="7" y2="0" stroke="#cdd9de" stroke-width=".55"/>' +
        '</pattern>' +
        '<clipPath id="clip-' + uid + '"><path d="' + adm0Path + '"/></clipPath>' +
      '</defs>' +
      '<rect x="0" y="0" width="' + VB_W + '" height="' + VB_H + '" fill="url(#sea-' + uid + ')"/>' +
      (opts.minimal ? '' : '<g class="sle-grat">' + grat + '</g>') +
      '<g class="sle-adm2-fill">' + fills + '</g>' +
      '<g id="' + opts.cellsId + '" clip-path="url(#clip-' + uid + ')"></g>' +
      (opts.oppOutline ? '<path id="' + opts.oppOutline + '" clip-path="url(#clip-' + uid + ')" class="sle-opp-outline" d=""></path>' : '') +
      '<g class="sle-adm2-border" clip-path="url(#clip-' + uid + ')">' + borders + '</g>' +
      '<path class="sle-adm0" d="' + adm0Path + '"/>' +
      (opts.minimal ? '' :
        '<g class="sle-labels">' + labels + '</g>' +
        '<g class="sle-cities">' + cityG + '</g>' +
        scaleG + northG);
  }

  /* ---- public init ------------------------------------------------------- */
  var _scenario = 'baseline';
  function init(configs) {
    if (!GRID.length) buildGrid();
    configs.forEach(function (cfg) {
      var svg = document.getElementById(cfg.svgId);
      if (svg) buildBase(svg, cfg);
    });
  }

  /* ---- fill a cells group with arbitrary per-cell colours ---------------- */
  // colorFn(cell) -> colour string, or { color, title } object.
  function fill(cellsId, colorFn) {
    if (!GRID.length) buildGrid();
    var g = document.getElementById(cellsId);
    if (!g) return;
    var rows = GRID.map(function (c) {
      var r = colorFn(c);
      var color = (r && r.color) ? r.color : r;
      var title = (r && r.title) ? '<title>' + esc(r.title) + '</title>' : '';
      return '<rect class="raster-cell" x="' + c.x + '" y="' + c.y + '" width="' + c.w +
        '" height="' + c.h + '" fill="' + color + '">' + title + '</rect>';
    });
    g.innerHTML = rows.join('');
  }

  window.SLEMap = {
    init: init,
    fill: fill,
    project: project,
    gSuit: gSuit,
    gPrio: gPrio,
    gSlope: gSlope,
    get GRID() { return GRID; },
    get scenario() { return _scenario; },
    set scenario(v) { _scenario = v; },
    get meta() { return GEO.meta; }
  };
})();
