# NbS Rural Scan — Team Playbook

How we work. Read once, re-skim when unsure.

## The team and their roles

| Person | Role | Owns |
|---|---|---|
| **Pete Steward** | Team Lead | Framework integrity · wireframe direction · scope-control · WB liaison · **operational lead on M1 (Suitability), M3 (Opp Space Characterisation), M4 (Priority Hotspots)** · recipe/spec authoring |
| **Benson Kenduiywo** | QA / QC | Dataset fitness sign-off · output validation · resolution audit · framework primitives (inherited attribution) |
| **Namita Joshi** | Project Coordination + Literature | **Task H focus ([expert-opinion elicitation & integration protocol](file:///Users/pstewarda/Documents/rprojects/nbs_ruralscan/methodology/expert_opinion_protocol.md))** · expert-opinion elicitation · project coordination |
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

Pipeline architecture is in [`docs/pipeline.html`](./docs/pipeline.html). The full delivery rationale is in [AGENTS.md](./AGENTS.md).

## Standard workflows

### Add a new NbS recipe

1. Open an Issue with the **NbS Recipe** template.
2. In Claude Code, run `/new-recipe <nbs_id>` — scaffolds the folder and starter table.
3. Populate the master variable table (the six-theme structure from the water-harvesting recipe).
4. Fill the Variable Cards (six slots each).
5. Get one MFL-team reviewer (Sarah · Chris · Evert · Hannes — match by domain).
6. Raise a PR using the PR template.

### Perform literature & tools discovery

1. Open an Issue with the **Data Discovery & Ingestion** template.
2. Formulate organization-neutral, functional search queries for the target table (avoiding hardcoded organization names in the query text).
3. Conduct both general web/repository searches (e.g., using Google, GitHub, or meta-directories like the Nature-Positive Agrifood Systems Toolkit) to discover standalone tools, repositories, and methods, and targeted institutional queries (such as WOCAT Global Database, FAO TECA, World Bank project documents, and Center for Agroforestry databases) for official reports and databases.
4. Screen and select candidates using the **six-axis credibility rubric** (methodological transparency, evidence type, context AEZ/LMIC relevance, recency, influence).
5. Compile the screening results in the PRISMA-lite discovery log under `methodology/discovery_logs/<nbs_id>_<table>.md`.
6. Add the approved candidates to `SRC_source_register.csv` and log detailed evidence extraction quotes in `EV_evidence_register.csv`.
7. Link the evidence IDs to the recipe table (e.g. `T3_nbs_hazard_farming.csv` or `T4_suitability_rules.csv`).
8. Run `python3 src/nbs_ruralscan/schema_tools/generate.py schema` to rebuild the JSON files and update the dashboard logs view.
9. Verify using `python3 src/nbs_ruralscan/schema_tools/check_alignment.py` and run tests (`uv run pytest`).
10. Raise a PR using the PR template.

### Review flagged evidence (QA/QC → main)

1. Start the local review server: `uv run python3 -m nbs_ruralscan.schema_tools.review_server` → http://localhost:8765/dashboard.html → **QA/QC** tab. (One-time per clone: `bash scripts/setup-repo.sh`; be logged in — `gh auth status`.)
2. Set your reviewer handle. Work the **AI-flagged** queue: **ok** (keep) or **drop** (remove) + a reason code.
3. Click **✓ Apply & submit to main** — one click: writes your decisions to the register + `review_log`, regenerates JSON, then branches off latest `main`, opens a PR, and **auto-merges on green CI**. You get a popup with the PR link. (Headless equivalent: `bash scripts/submit-review.sh <handle> --auto`.)
4. **Consensus:** a flag is applied only when the reviewers who decided it agree; a disagreement stays a pending conflict. Applied decisions are re-openable/challengeable.
5. **Auto-merge governance:** `main` is protected (CI `checks` + 1 approval). Review-only PRs (files ⊆ registers/`review_log`/`docs/*.json`, title `qaqc:*`) from allowlisted reviewers (`Namita-J`, `peetmate`) get the bot's approval + auto-merge; **anything else needs a human review.** Extend the allowlist in `.github/workflows/auto-merge-review.yml`.
6. Run it **once per review session** (batches all agreed decisions into one PR) — not per flag.

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
2. Preserve the locked structure (six tabs · Variable Card slots · T0–T7 colours — see AGENTS.md).
3. Test locally: `cd docs && python3 -m http.server 8000`
4. PR using the PR template. The structural checklist must pass.
5. GitHub Pages auto-deploys within ~2 minutes after merge.

## Using Claude Code on this repo

Benson has a Claude Premium seat. We expect Claude Code to be the default development environment.

### What to ask Claude Code

Anything with concrete inputs and outputs. Examples:

- *"Port `reference/R/spatMCDA.R` to numpy, preserving the CRITIC + Entropy + AHP weighting logic. Save to `src/nbs_ruralscan/runtime/mcda.py`."* (✅ shipped — see `tests/test_mcda.py`)
- *"Scaffold an agroforestry pilot Colab notebook for Sierra Leone, loading the recipe from `methodology/recipes/agroforestry.md`, calling `src/nbs_ruralscan/runtime/mcda.py`, and writing outputs to `pipeline/outputs/agroforestry_sl/`."*
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
- One reviewer for content PRs (recipes, variable cards); one + Pete for structural PRs (wireframe, schema, AGENTS.md)

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

Assign each issue to the milestone it must close before. Leave the milestone field empty for plumbing work (AGENTS.md updates, repo bootstrap).

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

`.github/SEED_ISSUES.md` lists the initial ~15 issues to open. Walks through module specs (M0/M3/M4/M5/M6), recipe authoring (agroforestry / forest restoration / riparian buffers), pipeline implementation (`src/nbs_ruralscan/runtime/mcda.py` shipped; `src/nbs_ruralscan/runtime/climate_risk.py` per M2 spec), pilots, the GEE App spec, and Pages setup. Open them through the web UI one at a time — ~20 min total — and the backlog tells a coherent story when the team first opens it.

### Cadence

- **Weekly Monday standup** (15 min, async on Teams): each person posts which issues they're picking up that week; the "This week" column reflects this.
- **Fortnightly Claude Code pair session** (30 min, scheduled): live work on a concrete issue using Claude Code, with one teammate observing / learning. Per the Claude Code uplift expectation.
- **Module review sessions** (Sessions A–E, scheduled by Pete): one per module; end with the relevant spec sheet signed off.
- **Phase 3 monthly check-in with WB**: scheduled by Pete; surface key issues / pilot progress to Laurent and Dinara.

## When in doubt

- [AGENTS.md](./AGENTS.md) is the source of truth for what's locked
- This Playbook is the source of truth for how we work
- Most recent `5_Meetings/` transcript in the shared SharePoint for current discussion state
- Teams channel: `NbS Rural Scan Task Force`
