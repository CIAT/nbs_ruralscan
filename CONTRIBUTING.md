# Contributing to NbS Rural Scan

Welcome. This document is the detailed onboarding for working in this repo — for first-time contributors and as a refresher for the existing team. Read [`CLAUDE.md`](./CLAUDE.md) and [`PLAYBOOK.md`](./PLAYBOOK.md) first if you haven't; they set the architectural and team context. This file is about *how to actually get hands on the work*.

---

## Tools you'll use

| Tool | Why | How to install |
|---|---|---|
| **VS Code** | Editor + Source Control panel + integrated terminal | https://code.visualstudio.com |
| **Claude Code** | Pair programmer in your terminal; reads project memory automatically | `curl -fsSL https://claude.com/install.sh \| bash` (or see https://docs.claude.com/en/docs/claude-code/setup) |
| **GitHub CLI (`gh`)** | Commits, PRs, issues from the terminal — used by `setup-labels.sh` | `brew install gh` then `gh auth login` |
| **Python 3** | Pipeline code; local Pages preview server | Usually installed on macOS by default; `brew install python` otherwise |
| **Google Earth Engine** | Underlying analytics platform (pipeline work only) | https://earthengine.google.com — request access via your CGIAR email |

Confirm everything is installed:

```bash
code --version
claude --version
gh --version
python3 --version
git --version
```

## VS Code: the suggested setup

A few VS Code conventions used across the team:

- **Use the integrated terminal** (`⌃ \``) — that's where you'll run Claude Code. Keeps your editor and terminal in one window.
- **Source Control panel** (`⌃ ⇧ G`) — visual git status, stage / commit / push without leaving the editor.
- **GitLens extension** (optional but recommended) — inline blame, file history, PR view.
- **GitHub Pull Requests and Issues extension** (recommended) — manage issues / PRs without leaving VS Code.
- **Markdown All in One extension** — table editing and preview for the many `.md` files in this repo.

Open the repo with: `cd nbs_ruralscan && code .`

## Claude Code: how we use it on this repo

**Claude Code reads `CLAUDE.md` on every session.** That file encodes the project architecture, what's locked vs open, the seven modules, the team, the conventions. You don't need to brief Claude Code on the project — just open it in the repo and tell it what you want to do.

The team has Claude Premium seats. We expect Claude Code to be the default development environment — not a side tool. The Claude Code uplift expectations are documented in [`PLAYBOOK.md`](./PLAYBOOK.md#using-claude-code-on-this-repo).

### Slash commands

We have two custom slash commands in `.claude/commands/`:

- `/new-recipe <nbs_id>` — scaffolds a new NbS recipe with the standard structure
- `/update-variable-card <variable> <nbs_id>` — authors or updates a Variable Card

### Tool permissions

`.claude/settings.json` sets project-level permissions. Reads are auto-allowed; writes and `git push` prompt for confirmation. Adjust to your comfort if you find the prompts intrusive — but err conservative when working with the schema or the methodology folder.

### Concrete starting prompts

Five focused prompts that map to project deliverables are in the **Claude Code Uplift note** (in the project working folder — ask Pete for a copy). Each is a couple of hours of pair-programming that produces a tangible artefact:

1. ~~Port `reference/R/spatMCDA.R` to `pipeline/mcda_pipeline.py`~~ ✅ shipped at `src/nbs_ruralscan/mcda.py` (see `tests/test_mcda.py`)
2. Scaffold the agroforestry pilot Colab notebook (calls `src/nbs_ruralscan/mcda.py`)
3. Extend the Water Harvesting master variable table into Variable Cards
4. ~~Build the v0 GEE App~~ deferred (GEE App dropped; the wireframe is the demonstrator)
5. Run correlation reduction on input variables

---

## Your first contribution — walkthrough

A worked example from issue → committed PR. Assumes you've completed the one-time setup in the [README quick start](./README.md#working-in-this-repo--quick-start-10-minutes).

### Step 1 — Find a task

Go to [Issues](https://github.com/CIAT/nbs_ruralscan/issues). Find an issue with the `up-for-grabs` label (or one explicitly assigned to you).

If you can't find one, ask in the `NbS Rural Scan Task Force` Teams channel.

### Step 2 — Claim the issue

In the issue, click **Assign yourself** (right sidebar). Comment: "Picking this up — aiming to have it ready by [date]." Move the issue card on the project board from **Backlog** to **This week**.

### Step 3 — Branch

In VS Code's integrated terminal, from the repo root:

```bash
git checkout main
git pull
git checkout -b feat/short-description-of-task
```

Branch naming convention: `<type>/<short-desc>` — types are `feat`, `fix`, `docs`, `chore`, `refactor`.

### Step 4 — Run Claude Code

```bash
claude
```

Tell it what you're doing and reference the issue:

> *"I'm picking up issue #N: [issue title]. The acceptance criteria are X, Y, Z. Read the relevant context files (CLAUDE.md is already loaded; also look at [specific file]) and propose an approach before writing anything."*

Iterate until you have a working artefact. Test it (run the notebook, preview the docs page, validate the schema row — whatever applies).

### Step 5 — Stage and commit

Either via Claude Code (which will ask for confirmation on git commands per the settings) or via VS Code's Source Control panel.

Commit message format (Conventional Commits):

```
<type>: <short description>

<longer body if needed — what changed, why, references>

Closes #N
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`.

The `Closes #N` line auto-closes the issue when the PR merges and triggers the project board automation to move it to Done.

### Step 6 — Push and raise PR

```bash
git push -u origin feat/short-description-of-task
gh pr create --fill --base main
```

Or use VS Code's UI: in the Source Control panel, click "..." → "Push" → then "Create Pull Request" if the GitHub Pull Requests extension is installed.

The PR will auto-populate from the PR template. Fill out the **Structural checklist** — this catches drift on locked decisions. If anything's unchecked, explain in the comments.

### Step 7 — Review

Request at least one reviewer (your assignee is in the issue). For structural changes (wireframe, schema, CLAUDE.md), request Pete + one other reviewer.

When the PR is approved and merged, the issue closes automatically, the project board moves it to Done.

### Step 8 — Update the issue

Before the issue auto-closes, leave a final comment summarising what shipped and linking to the merged PR. Future readers (including future-you) will thank you.

---

## Working on specific kinds of tasks

### Authoring or updating a recipe (`methodology/recipes/<nbs_id>.md`)

1. Open the existing canonical pattern: [`methodology/recipes/water_harvesting.md`](./methodology/recipes/water_harvesting.md). It has eight sections; your recipe follows the same structure.
2. Use `/new-recipe <nbs_id>` in Claude Code to scaffold the file.
3. Populate the master variable table (§2.2 in the canonical pattern) — six themes (topographic / hydrological / soil / climatic / LULC / socio-econ + hazard), with the standard columns.
4. Author Variable Cards in the recipe markdown (six slots each: What / Why / How to read / What it represents / Where it comes from / Membership function preview).
5. Pull schema rows into `schema/recipes/<nbs_id>/`.
6. Get an MFL-team reviewer (Sarah, Chris, Evert, or Hannes — pick by domain).
7. PR using the PR template. The recipe-related boxes in the structural checklist must pass.

### Updating the wireframe or pipeline diagram (`docs/`)

The structural decisions are locked — see [`docs/README.md`](./docs/README.md). Common locks:

- Six tabs in the wireframe, in their order
- Variable Card six slots
- T0–T7 colour scheme
- Sierra Leone / agroforestry mock data consistency

Edit `docs/wireframe.html` or `docs/pipeline.html` directly in Claude Code. Test locally:

```bash
cd docs
python3 -m http.server 8000
# open http://localhost:8000 in browser
```

PR with the PR template's wireframe-edit checklist ticked.

### Working on pipeline code (`pipeline/`)

The methodology is data-driven — analytical rules read from the schema (T0–T7), never hardcoded. If you find yourself writing a threshold, weight, or variable name as a Python literal in `pipeline/`, stop and put it in the schema instead.

Pilot notebooks (`pipeline/notebooks/`) follow the structure in [`pipeline/notebooks/README.md`](./pipeline/notebooks/README.md) — header → setup → configuration → ingestion → reduction → M1 → M2 → M3 → M4 → M5 → outputs → summary. Plain-language markdown between cells so a WB analyst can follow without verbal explanation.

To pull GEE-hosted data, ensure you have Earth Engine API access (request via your CGIAR email if you don't). The package reaches GEE data and server-side processing through **xee** (Earth Engine ↔ xarray), so you'll need to be authenticated to Earth Engine when a run touches GEE-hosted layers.

### The GEE App is dropped

The standalone GEE App is no longer in scope (team decision, June 2026) — see [`pipeline/gee_app/README.md`](./pipeline/gee_app/README.md). GEE itself stays central via xee; the **wireframe** (`docs/wireframe.html`) is the visual demonstrator. If a GEE App is ever revived, raise an issue first.

---

## Cadence

Mirrored from PLAYBOOK so it's findable here:

- **Weekly Monday standup** (15 min, async on Teams): post the issues you're picking up that week.
- **Fortnightly Claude Code pair session** (30 min, scheduled): live work on a concrete issue with one teammate observing.
- **Module review sessions** (A–E, scheduled by Pete): one per module, end with the spec sheet signed off.
- **Phase 3 monthly check-in with WB**: Pete coordinates; surface key issues / pilot progress to Laurent and Dinara.

---

## Questions and stuck-points

- Code questions → ask Claude Code first. It knows the project conventions.
- Workflow questions → check `PLAYBOOK.md`.
- Architecture questions → check `CLAUDE.md` (for the locked decisions) and the module specs (`methodology/modules/`).
- Domain questions (does this NbS work in X context?) → ask the relevant MFL team member.
- Anything urgent → `NbS Rural Scan Task Force` Teams channel.
- Anything that should be remembered for future Claude Code sessions → update `CLAUDE.md` (small) or `PLAYBOOK.md` (larger).

Welcome aboard.
