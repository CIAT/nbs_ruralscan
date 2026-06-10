# gee_app/ — DROPPED (deferred)

**The GEE App is dropped from the current scope (team decision, June 2026).** The standalone
Earth Engine Apps product and a native Earth Engine script pipeline are no longer part of the
delivery — but GEE itself stays central: data and server-side processing are reached through
**xee** (Earth Engine ↔ xarray) inside the Python package.

- Pilots are delivered as **Colab notebooks** backed by the Python package in
  [`../../src/nbs_ruralscan/`](../../src/nbs_ruralscan/) (GEE and other data pulled into Python,
  computed with xarray / rioxarray; GEE processing via xee).
- The **TTL wireframe** ([`../../docs/wireframe.html`](../../docs/wireframe.html)) is the
  visual demonstrator.

This folder is retained only as a historical pointer; the previous design brief is
superseded (see git history). If a GEE App is ever revived, raise an issue first.
