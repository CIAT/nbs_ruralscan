# GEE App — design owned by Benson

This folder is where the GEE App lives. The App is the visual end of the pilot pipeline — what a non-technical viewer opens to explore the suitability surface, climate risk overlay, and opportunity-space characteristics for a given pilot.

**Design ownership: Benson Kenduiywo.** Constraints below; decisions within constraints are yours.

---

## Why this is your call

You're the team's GEE expert; you know what's buildable in GEE Apps and what isn't. Trying to design the App from outside GEE Apps (in HTML or in a separate mockup) would have us guessing at capability boundaries you already know. Cleaner to let you scope it directly, with the HTML wireframe as a design target and clear constraints below.

## Design target

[The TTL tool wireframe](https://ciat.github.io/nbs_ruralscan/wireframe.html) is the **aspirational** design target. It shows the experience we want a TTL to have. The GEE App is a **scoped** version of it — implementing the parts that GEE Apps can express well, deferring or simplifying the rest.

## Inputs the App consumes

The pilot pipeline (`../mcda_pipeline.py` + the Colab notebook) writes outputs to `../outputs/<pilot_id>/`. The App reads from those — primarily:

- `maps/suitability.tif` and `maps/suitability_class.tif` (from M1)
- `maps/climate_risk_baseline.tif` and `maps/climate_risk_<scenario>.tif` (from M2)
- `tables/fingerprint.csv` (opportunity space summary)
- `tables/scorecard.csv` (T6 Likert effects + economic profile)
- `tables/cluster_log.json` (variable card metadata)
- `run_config.json`

If the GEE App needs additional outputs the pipeline doesn't produce, raise an issue against the M1 / M2 spec — the contract changes together.

## Audience

Three audiences in order of priority:

1. **Internal team + WB technical staff** — for sanity-checking pilot outputs and exploring results during the pilot phase.
2. **Laurent + Dinara** at the WB NbS Solutions team — for the Phase 3 final presentation, alongside the HTML wireframe.
3. **Future TTLs** — if the App moves into operational use post-pilot (out of current scope, but design with this in mind).

## Constraints

### What you must keep

- **Data products consumed must match the pipeline outputs.** Don't introduce new variables or layers that the pipeline doesn't produce. If you need something, raise it against the M1/M2 spec first.
- **Read from schema metadata where possible.** Variable names, descriptions, hosting status, cluster membership — all come from the cluster_log.json + the schema CSVs. Hardcoded labels in the App are an anti-pattern (same rule as the pipeline).
- **Preserve the analytical separation** between suitability (M1), climate risk (M2), and TTL hotspots (M4) — these are distinct surfaces in the wireframe and should remain distinct in the App.
- **Variable cards in the App should carry the six slots** documented in CLAUDE.md (What / Why / How to read / What it represents / Where it comes from / Membership function preview), even if styled simply.

### What you can decide

Within the above:

- Which wireframe tabs to implement vs defer
- Tab navigation pattern (GEE Apps has limited tab support — multi-panel switching, side-by-side, single-page-with-sections all valid)
- Map base layer choice (Google's default vs Esri vs Carto)
- Chart styles (basic Chart widgets vs ee.Chart vs Plotly via HtmlWidget if available)
- Single-pilot vs multi-pilot app structure
- URL parameter handling (deep-linking to a specific pilot / NbS / AOI)
- Whether to embed run configuration vs read it dynamically
- Color ramp choices for the suitability and risk surfaces — match the wireframe's classes if possible, but use whatever renders cleanly in GEE Apps
- How to render the Variable Card content — full panel, hover popover, side panel, etc.

### What stays in the HTML wireframe only

These are likely to be too HTML/CSS-dependent to express well in GEE Apps. Your call whether to attempt them, but the wireframe is the canonical home:

- Stack bars (suitability classes by area; farming systems by share)
- Multi-row scorecard with Likert effect bars
- Side-by-side NbS comparison view with overlap analysis
- Polished economic archetype card

If you find a clean GEE Apps way to render any of these, great — otherwise they stay in the wireframe and we point WB stakeholders at both artefacts.

## Deliverables

1. **App spec doc** at `./spec.md` — your design decisions, scoped feature list, scope mapping against the wireframe, GEE Apps URL structure, dependencies on pipeline outputs. About 1–2 pages. Read by the team and reviewed by Pete before you start building.
2. **GEE App implementation** at `./app.js` (or `./app.py` if you're using GEE Python with `geemap` for embedded use) — the actual App. Deployed to a GEE App URL.
3. **App README** at this file, updated — replaces this brief with operational documentation once the App exists.

## Process

1. **Open an Issue** using the **Module Spec** template (it works for App spec too) — title: `[App Spec] GEE App v0 design`.
2. **Read the wireframe** end-to-end (https://ciat.github.io/nbs_ruralscan/wireframe.html) and the M1 + M2 specs. Build your scoped feature list.
3. **Draft `spec.md`** in this folder. Get Pete's review before building.
4. **Use Claude Code** to scaffold the App. Suggested first prompt:
   > Read `pipeline/gee_app/spec.md` for the design decisions. Build a GEE App in JavaScript (or `geemap` for Python) implementing the scoped feature list. Read pilot outputs from `pipeline/outputs/<pilot_id>/`. Use the schema metadata from cluster_log.json for variable labels. Keep total under 600 lines; produce a deployable file.
5. **Iterate.** Deploy to a GEE App URL; share with the team; refine based on feedback.

## Timeline

- **App spec doc** — within ~1 week of pilot pipeline producing first outputs
- **App v0 deployed** — alongside Phase 3 pilot completion (per proposal Month 6)
- **Demonstrator-ready** — in time for the WB final presentation

## Open questions you'll need to answer in the spec

1. **One App for all pilots, or one App per pilot?** Multi-pilot is more reusable; per-pilot is simpler.
2. **Hosted by whom?** Your CGIAR GEE account, a CIAT account, or via a service account?
3. **GEE compute costs** — at what scale does the App become billable? Worth flagging upfront.
4. **GEE Apps quota / sharing** — does the app URL work for non-GEE-authenticated viewers?
5. **Live recompute vs precomputed** — for the demonstrator, precomputed pilot outputs are fine; for any what-if scenarios in the App, live recompute may be needed (or fall back to a fixed scenario set).
6. **Tab simulation pattern** — GEE Apps doesn't natively support tabs; what's your approach?

These are spec-time decisions. Document them; we can review together before you build.

## Companion artefacts to read

- [TTL Tool Wireframe](https://ciat.github.io/nbs_ruralscan/wireframe.html) — design target
- [`../methodology/modules/M1_suitability.md`](../methodology/modules/M1_suitability.md) — what M1 produces
- [`../methodology/modules/M2_climate_risk.md`](../methodology/modules/M2_climate_risk.md) — what M2 produces
- [`../methodology/recipes/water_harvesting.md`](../methodology/recipes/water_harvesting.md) — your canonical recipe pattern
- [`../CLAUDE.md`](../CLAUDE.md) — project-level memory; what's locked, what's open

## Why this brief is short

The HTML wireframe + the M1 / M2 specs already encode most of the design intent. This brief just hands you ownership of translating that into GEE Apps with clear constraints. The shape of the App and the trade-offs against the wireframe are decisions you're best placed to make.

---

*This file becomes operational documentation once the spec and App exist. Until then, it's the brief for the work.*
