# NbS Rural Scan — `docs/` folder

This folder hosts the live demonstrator artefacts for the Rural NbS Scan project. GitHub Pages serves the contents at:

**https://ciat.github.io/nbs_ruralscan/**

## What's in here

| File | Description |
|---|---|
| `index.html` | Landing page listing the artefacts |
| `wireframe.html` | TTL tool wireframe v0.7 (interactive mockup) |
| `sle_geo.js` · `sle_map.js` · `priority_detail.js` · `project_risk.js` | JS the wireframe loads (geometry + map/detail/risk logic) |
| `pipeline.html` | Pipeline architecture v0.5 (one-page diagram) |
| `README.md` | This file |

## Editing workflow — Claude Code

The artefacts are single-file HTML pages. All styling and interactivity is inline — no build step, no dependencies. To edit:

### 1. Get set up (once)

```bash
git clone https://github.com/CIAT/nbs_ruralscan.git
cd nbs_ruralscan
```

Open the repo folder in Claude Code (`cd` into it and run `claude`, or use your usual workflow).

### 2. Make changes

Ask Claude Code naturally — it knows HTML/CSS/JS and can read the existing patterns. Examples:

- *"In `docs/wireframe.html`, change the map cells in the Opportunity Space tab to use real Sierra Leone district outlines from this GeoJSON I've added."*
- *"On the Variable Config tab, add a search box that filters the variable list by name."*
- *"On the Priority Hotspots tab, add the planned Project-Risk scope alongside the NbS Suitability Scope and Priority Scope."*
- *"Improve the typography hierarchy across the wireframe — move from default sizes to a more refined scale."*

Claude Code edits files in-place. Test the result by opening the file locally in your browser, or run a tiny local server:

```bash
cd docs
python3 -m http.server 8000
# visit http://localhost:8000
```

### 3. Commit and push

Once the change looks right:

```bash
git add docs/
git commit -m "Improve typography hierarchy in wireframe"
git push
```

GitHub Pages auto-rebuilds within ~2 minutes. Visit the live URL to confirm.

## What to keep stable

Some structural decisions in the artefacts are deliberate and shouldn't drift between edits. If you want to change any of these, propose it in the team channel first:

- **Wireframe tab structure** (v0.7) — Setup → Opportunity Space → Project Risk → Priority Hotspots → NbS Comparison → Next Steps, plus Danger Zone and an internal Dev Notes tab. Setup → Opportunity Space is the primary TTL flow; Variable Config (sub-tab under Setup, with Suitability and Priority/hotspot surfaces), Danger Zone and Dev Notes are technical/internal. *(Tab-set ratification pending.)*
- **Variable Card structure** — six slots: What / Why (NbS-specific) / How to read / What it represents (cluster) / Where it comes from / Response preview (membership curve + raw-vs-transformed maps). Driven by Ani's three principles.
- **Two risk lenses** — risk to rural livelihoods (Opportunity Space) vs risk to the investment (Project Risk tab). Keep them labelled and distinct.
- **T0–T7 colour scheme** — matches the ERD in `2_Technical_&_Data/Claude Outputs/NbS_ERD_v01.html`. Visual consistency across artefacts.
- **Cluster representative + GEE/upload badges** on variable chips — these are the visible expression of Ani's reduce/source principles.
- **Pipeline diagram inheritance attribution** — the top strip of framework primitives all attributed to Benson is structural, not decorative.
- **Sierra Leone / agroforestry mock data** — consistent demo story across all artefacts (matches Dinara's FSRP pilot suggestion).

## What to evolve

- Map rendering quality (the SVG mocks are basic)
- Hover/interaction states (popovers, drill-downs)
- Iconography
- Mobile / responsive variants
- Real data once the agroforestry pilot has run

## Setting up GitHub Pages (one-off, by repo admin)

1. Push this `docs/` folder to the `main` branch.
2. In the repo: Settings → Pages.
3. Source: **Deploy from a branch** · Branch: **main** · Folder: **/docs** · Save.
4. Wait ~2 minutes; the site is live at `https://ciat.github.io/nbs_ruralscan/`.

## Roles

- **Pete** owns artefact direction; reviews PRs that change the structural elements above. Operational lead on M1/M3/M4 outputs once they replace mock data.
- **Benson** reviews pipeline outputs for fitness/resolution as QA/QC; can edit artefacts where his sign-off applies.
- **Namita** owns **M6 content (Implementation Hand-off)**, variable content (Variable Cards, recipe tables) and expert-opinion integration.
- **Brayden** owns dataset-download / analytical-context outputs surfaced on the site (climate risk, hazard indices); can iterate front-end visual polish where needed.
- **MFL team** (Sarah, Chris, Evert, Hannes) are contributors to M6 content (Implementation Hand-off).
