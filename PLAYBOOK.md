# NbS Rural Scan — Team Playbook

How we work. Read once, re-skim when unsure.

## The team and their roles

| Person | Role | Owns |
|---|---|---|
| **Pete Steward** | Team Lead | Framework integrity · wireframe direction · scope-control · WB liaison · **operational lead on M1 (Suitability), M3 (Opp Space Characterisation), M4 (Priority Hotspots)** |
| **Benson Kenduiywo** | QA / QC | Dataset fitness sign-off · output validation · resolution audit · framework primitives (inherited attribution) |
| **Namita Joshi** | Project Coordination + Literature | **Expert-opinion elicitation + pipeline integration** · Variable Cards · recipe content · NbS scorecards (T6) · coordination |
| **Brayden Youngberg** | Co-lead — Methodology | **M2 climate-risk + M2b project-disaster-risk index formulation · dataset download layer (T1 → Python) + analytical-context construction (T7); server-side preferred (GEE / STAC / large services)** |
| **Aniruddha Ghosh** | Methodology Advisor | Variable parsimony · transparency · Claude Code patterns |
| **Sarah Jones, Chris Kettle, Evert Thomas, Hannes Gaisberger** | MFL Team | Ecosystem services · M6 hand-off content · agroforestry/forest domain input |
| **Lolita Müller** | Stocktake Lead | Lit review pipelines · stocktake report |
| **Anastasia Wahome** | Geospatial Support | Implementation support across modules |

## How we deliver

Three artefact types coexist; each serves a different audience.

| Artefact | Audience | Owner | Contractual? |
|---|---|---|---|
| **Colab pilot notebook** | WB technical team (Dany), future implementers | Brayden · Anastasia · Pete (Claude Code) | Yes (Phase 3) — minimum committed pathway |
| **Claude-Code front/back end** | Stretch demonstrator over the same schema | Pete + Claude Code | No — parallel exploration |
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

- *"Port `reference/R/spatMCDA.R` to numpy, preserving the CRITIC + Entropy + AHP weighting logic. Save to `src/nbs_ruralscan/mcda.py`."* (✅ shipped — see `tests/test_mcda.py`)
- *"Scaffold an agroforestry pilot Colab notebook for Sierra Leone, loading the recipe from `methodology/recipes/agroforestry.md`, calling `src/nbs_ruralscan/mcda.py`, and writing outputs to `pipeline/outputs/agroforestry_sl/`."*
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

## Project management on GitHub

We use GitHub as the project's coordination layer. Three building blocks.

### 1. Issues — the unit of work

Every discrete task is an Issue, opened against one of the four templates (`.github/ISSUE_TEMPLATE/`):

- **Recipe** — author or update a per-NbS recipe
- **Variable Card** — author or update a Variable Card
- **Module spec** — draft or revise a module spec (M0–M6) or App spec
- **Pilot task** — apply the methodology to a specific country / NbS

If a task doesn't fit a template, push back: most of the time it's actually one of these in disguise.

### 2. Labels — categorisation

Conventional label set. Apply at least one Type label and at least one Module / NbS label per issue:

- **Type:** `recipe` · `variable-card` · `module-spec` · `pilot` · `bug` · `documentation` · `methodology` · `app`
- **Module:** `M0-setup` · `M1-suitability` · `M2-climate-risk` · `M3-characterisation` · `M4-hotspots` · `M5-scorecard` · `M6-handoff`
- **NbS:** `agroforestry` · `water-harvesting` · `forest-restoration` · `riparian-buffer` *(add as recipes are authored)*
- **Phase:** `phase-2-methodology` · `phase-3-pilot`
- **Status (auxiliary):** `blocked` · `needs-review` · `up-for-grabs`
- **Priority:** `priority-high` · `priority-medium` · `priority-low`

One-time setup via `gh` CLI: `bash .github/setup-labels.sh` (requires GitHub CLI installed and authenticated).

### 3. Milestones — phases

One milestone per project phase, dated:

- **Phase 2 — Methodology Development** (Feb–Apr 2026; closing)
- **Phase 3 — Piloting** (Apr–Jun 2026; current)
- **Phase 3.2 — Final outputs + WB presentation** (Jun 2026)

Assign each issue to the milestone it must close before. Leave the milestone field empty for plumbing work (CLAUDE.md updates, repo bootstrap).

### 4. Project board — the Kanban

One Projects v2 board for the whole consultancy: **NbS Rural Scan — Delivery board**. Create via the repo's *Projects* tab → *New project* → table view, then customise.

Columns:

| Column | Meaning |
|---|---|
| **Backlog** | All open issues, triaged but not yet active |
| **This week** | Committed for the current week |
| **In progress** | Being actively worked on |
| **Review** | PR raised; waiting on review or merge |
| **Done** | Closed |

Recommended views (Projects v2 supports multiple views over the same data):

- **By Module** — group by Module label
- **By Owner** — group by assignee
- **By NbS** — group by NbS label
- **By Phase** — group by milestone

Automation to enable (one-off setup — click-by-click runbook at [`.github/PROJECT_BOARD_SETUP.md`](./.github/PROJECT_BOARD_SETUP.md)):

- New issue → auto-add to Backlog
- Issue assigned / Monday standup → move to This week *(manual)*
- Work starting → move to In Progress *(manual)*
- PR opened or approved → move to Review *(optional auto via "Code review approved" workflow)*
- PR merged / issue closed → move to Done *(auto)*
- Done items older than 14 days → auto-archive *(optional)*

### Conventions

- **Issues are the source of truth for work allocation.** Quick clarifications in Teams are fine; committed work lives as an issue.
- **One issue per logical unit.** Don't bundle "do recipe + update wireframe + write spec" into one. Split.
- **Reference issues in commits and PRs** — `Closes #42` in the PR body closes the issue on merge.
- **Update the issue before closing** — leave a one-line summary of what shipped + a link to the merged PR.

### Seed backlog

`.github/SEED_ISSUES.md` lists the initial ~15 issues to open. Walks through module specs (M0/M3/M4/M5/M6), recipe authoring (agroforestry / forest restoration / riparian buffers), pipeline implementation (`src/nbs_ruralscan/mcda.py` shipped; `src/nbs_ruralscan/climate_risk.py` per M2 spec), pilots, the GEE App spec, and Pages setup. Open them through the web UI one at a time — ~20 min total — and the backlog tells a coherent story when the team first opens it.

### Cadence

- **Weekly Monday standup** (15 min, async on Teams): each person posts which issues they're picking up that week; the "This week" column reflects this.
- **Fortnightly Claude Code pair session** (30 min, scheduled): live work on a concrete issue using Claude Code, with one teammate observing / learning. Per the Claude Code uplift expectation.
- **Module review sessions** (Sessions A–E, scheduled by Pete): one per module; end with the relevant spec sheet signed off.
- **Phase 3 monthly check-in with WB**: scheduled by Pete; surface key issues / pilot progress to Laurent and Dinara.

## When in doubt

- [CLAUDE.md](./CLAUDE.md) is the source of truth for what's locked
- This Playbook is the source of truth for how we work
- Most recent `5_Meetings/` transcript in the shared SharePoint for current discussion state
- Teams channel: `NbS Rural Scan Task Force`
