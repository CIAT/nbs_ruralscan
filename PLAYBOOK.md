# NbS Rural Scan — Team Playbook

How we work. Read once, re-skim when unsure.

## The team and their roles

| Person | Role | Owns |
|---|---|---|
| **Pete Steward** | Team Lead | Framework integrity · wireframe direction · scope-control · WB liaison |
| **Benson Kenduiywo** | Lead — Geospatial Analytics & Data Pipelines | GEE Python pipeline · M1 (Suitability) · pilot implementations |
| **Namita Joshi** | Project Coordination + Literature | Variable Cards · recipe content · NbS scorecards (T6) · coordination |
| **Brayden Youngberg** | Co-lead — Methodology | M2 (Climate Risk) methods · front-end help where capacity allows |
| **Aniruddha Ghosh** | Methodology Advisor | Variable parsimony · transparency · Claude Code patterns |
| **Sarah Jones, Chris Kettle, Evert Thomas, Hannes Gaisberger** | MFL Team | Ecosystem services · M6 hand-off content · agroforestry/forest domain input |
| **Lolita Müller** | Stocktake Lead | Lit review pipelines · stocktake report |
| **Anastasia Wahome** | Geospatial Support | Implementation support across modules |

## How we deliver

Three artefact types coexist; each serves a different audience.

| Artefact | Audience | Owner | Contractual? |
|---|---|---|---|
| **Colab pilot notebook** | WB technical team (Dany), future implementers | Benson | Yes (Phase 3) |
| **GEE App / panel UI** | Demo viewers · basic TTL exploration | Benson | No — natural extension |
| **HTML wireframe** | Laurent · final-presentation audience | Pete + Claude | No — demonstrator |

Pipeline architecture is in [`docs/pipeline.html`](./docs/pipeline.html). The full delivery rationale is in [CLAUDE.md](./CLAUDE.md).

## Standard workflows

### Add a new NbS recipe

1. Open an Issue with the **NbS Recipe** template.
2. In Claude Code, run `/new-recipe <nbs_id>` — scaffolds the folder and starter table.
3. Populate the master variable table (the six-theme structure from the water-harvesting recipe).
4. Fill the Variable Cards (six slots each).
5. Get one MFL-team reviewer (Sarah · Chris · Evert · Hannes — match by domain).
6. Raise a PR using the PR template.

### Update or add a Variable Card

1. Open an Issue with the **Variable Card** template (or comment on an open recipe issue).
2. Edit the recipe's master variable table — the card content lives in those rows.
3. Six required slots: *What · Why (NbS-specific) · How to read · What it represents (cluster) · Where it comes from · Membership function preview.*
4. PR; one review; merge.

### Draft a Module spec sheet

1. Open an Issue with the **Module spec** template.
2. Module spec lives at `methodology/modules/M<n>_<name>.md`.
3. Include: purpose, inputs (with provenance), outputs (with format), dependencies on other modules, schema tables consumed, owner, status.
4. PR; Pete reviews; merge.

### Run a pilot

1. Open an Issue with the **Pilot task** template (country, NbS, AOI).
2. In Claude Code, clone the agroforestry pilot notebook from `pipeline/notebooks/` and adapt.
3. Authenticate GEE; run end-to-end; save outputs to `pipeline/outputs/<pilot_id>/`.
4. Write a one-page summary in the issue; close when validated.

### Push wireframe / pipeline diagram edits

1. Edit `docs/wireframe.html` or `docs/pipeline.html` directly in Claude Code.
2. Preserve the locked structure (six tabs · Variable Card slots · T0–T7 colours — see CLAUDE.md).
3. Test locally: `cd docs && python3 -m http.server 8000`
4. PR using the PR template. The structural checklist must pass.
5. GitHub Pages auto-deploys within ~2 minutes after merge.

## Using Claude Code on this repo

Benson has a Claude Premium seat. We expect Claude Code to be the default development environment.

### What to ask Claude Code

Anything with concrete inputs and outputs. Examples:

- *"Port `reference/R/spatMCDA.R` to GEE Python, preserving the CRITIC + Entropy + AHP weighting logic. Save to `pipeline/mcda_pipeline.py`."*
- *"Scaffold an agroforestry pilot Colab notebook for Sierra Leone, loading the recipe from `methodology/recipes/agroforestry.md`, calling `pipeline/mcda_pipeline.py`, and writing outputs to `pipeline/outputs/agroforestry_sl/`."*
- *"In `docs/wireframe.html`, replace the Sierra Leone SVG outline with district boundaries from the attached GeoJSON, keeping the existing colour scheme."*
- *"Add a Variable Card for `aridity_index` in the agroforestry recipe. Use the same six-slot structure as the slope card."*

### Light-touch accountability

The Premium tool means objections like "this is outside my expertise" or "I don't have time" carry less weight than before. We check on use through:

1. **Weekly share** — paste a Claude Code session transcript or list of commits into the `NbS Rural Scan Task Force` channel.
2. **Fortnightly pair session** — 30 min with Pete or a teammate, working live in Claude Code on something concrete.
3. **GitHub activity** — commits, branches, PRs visible in this repo at a cadence consistent with allocated time.

Not surveillance — shared learning, and visible progress.

## Branch / PR conventions

- Branch naming: `<type>/<short-desc>` — e.g. `feat/agroforestry-recipe`, `fix/variable-card-typography`, `docs/playbook-update`
- Commit messages: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`)
- One logical change per PR; don't bundle wireframe and methodology edits
- All PRs use the PR template
- One reviewer for content PRs (recipes, variable cards); one + Pete for structural PRs (wireframe, schema, CLAUDE.md)

## Scope guardrails

The project commitment is $200k / 6 months / **scoping** — not feasibility, not site-level design, not full ecosystem service modelling, not cost-benefit analysis. When in doubt about whether something is in scope, check the four-tier table in [`docs/pipeline.html`](./docs/pipeline.html#scope-guardrails) (Now / Soon / Later / Out).

## When in doubt

- [CLAUDE.md](./CLAUDE.md) is the source of truth for what's locked
- This Playbook is the source of truth for how we work
- Most recent `5_Meetings/` transcript in the shared SharePoint for current discussion state
- Teams channel: `NbS Rural Scan Task Force`
