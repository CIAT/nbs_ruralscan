# NbS Rural Scan

Methodology and demonstrator for spatial prioritisation of Nature-based Solutions in rural, agricultural, and forestry landscapes. Funded by the World Bank (D591). Implemented by Alliance Bioversity International & CIAT.

> ⚠ **Status:** v0 work-in-progress. Mock data only. Not yet a production decision tool.

---

## 👋 Team kickoff — start here

Welcome Benson, Namita, Brayden (and everyone else who lands here). This repo is the shared home for our methodology and workflow going forward. **Please spend ~15 minutes reading this section before picking up any work.**

### What's here

The scaffolding covers the methodology (modules, schema, recipes), the team's working conventions, and a populated project board with the first 15 issues. It's a *spine* you hang your work off — not a replacement for what's already been done.

### Three things to look at, with your feedback in mind

1. **[Pipeline architecture](https://ciat.github.io/nbs_ruralscan/pipeline.html)** — one-page diagram of the 7 modules and the T0–T7 schema. **Benson** — your water-harvesting recipe and v2 plan are the *framework primitives* layer at the top (5 fuzzy MFs, AHP+CRITIC+Entropy, spatMCDA, recipe template). Read on whether the attribution and architecture feel right.
2. **Module specs — M1 and M2**
   - **[M1 Suitability](./methodology/modules/M1_suitability.md)** — Benson, this is the I/O contract and 8 sub-steps for porting `spatMCDA.R` to `pipeline/mcda_pipeline.py`. Check whether the sub-step breakdown matches how you'd structure it. Function signatures in §13.
   - **[M2 Rural Climate Risk](./methodology/modules/M2_climate_risk.md)** — **Brayden**, pre-scaffolded for you. Mode A vs Mode B, double-count guard with M3/M4, function signatures for `pipeline/climate_risk.py`. Six open methodology questions at the bottom that need your view.
3. **Repo conventions + workflow** — [`CLAUDE.md`](./CLAUDE.md), [`PLAYBOOK.md`](./PLAYBOOK.md), [`CONTRIBUTING.md`](./CONTRIBUTING.md). **Namita** — keen on your take here since you'll coordinate recipe authoring + Variable Cards.

### Your assigned work on the [Delivery board](https://github.com/orgs/CIAT/projects/2)

- **Benson:** M1 port (#9), M4 spec (#3), agroforestry recipe (#6), Sierra Leone pilot (#11), GEE App spec (#13)
- **Namita:** M3 spec (#2), M5 spec (#4), forest restoration recipe (#7), riparian buffer recipe (#8)
- **Brayden:** M2 climate risk implementation (#10)

### Feedback forum — 1:1 catch-ups

Given staggered availability (Namita out next week; Brayden on leave Monday), the walkthrough happens as three separate 1:1s rather than a group session:

- **Benson — Monday** (calendar invite already sent). 60 min, focused on the framework primitives layer, M1, and the architecture overall.
- **Brayden — when back**. 30–45 min, focused on M2 and the six open methodology questions.
- **Namita — when back**. 45–60 min, focused on recipes, M3/M5, Variable Cards, and the workflow side.

In each: bring questions, pushback, "this is wrong because…" — all welcome.

### Framings worth flagging

- This is **scaffolding**, not a fait accompli.
- Benson's existing work is the canonical reference for the framework primitives and M1.
- Module specs are I/O contracts you can adjust, not briefs being handed to you.
- The wireframe is being sent for visual polish separately — feedback on flow and content is welcome.

---

## What this is

A scoping and decision-support framework that helps World Bank Task Team Leaders (TTLs) identify where different Nature-based Solutions could be invested in, how extensive the opportunity is, and which TTL priorities (poverty, biodiversity, climate risk, gender equity) intersect that opportunity space. Outputs are reproducible Jupyter/Colab notebooks plus an interactive demonstrator UI.

## Live demonstrator

**https://ciat.github.io/nbs_ruralscan/**

Includes:
- **TTL Tool Wireframe** — interactive mockup of the decision-support tool
- **Pipeline Architecture** — one-page methodology architecture diagram

Both use mock Sierra Leone / agroforestry data.

## Project board

Active work is tracked at the **[NbS Rural Scan — Delivery board](https://github.com/orgs/CIAT/projects/2)**. Five columns (Backlog · This week · In progress · Review · Done); new issues auto-add to Backlog. See [`.github/PROJECT_BOARD_SETUP.md`](./.github/PROJECT_BOARD_SETUP.md) for the setup runbook.

---

## Working in this repo — quick start (≈10 minutes)

The development environment is **VS Code + Claude Code in the integrated terminal**. Claude Code reads `CLAUDE.md` automatically on every session so you're never starting cold.

### One-time setup

```bash
# 1. Tools
brew install gh                                   # GitHub CLI (for issue/PR commands)
curl -fsSL https://claude.com/install.sh | bash   # Claude Code installer
# (Or follow https://docs.claude.com/en/docs/claude-code/setup for your platform)
gh auth login                                     # authenticate GitHub CLI

# 2. Clone and open
git clone https://github.com/CIAT/nbs_ruralscan.git
cd nbs_ruralscan
code .                                            # opens in VS Code
```

In VS Code, the Source Control panel (left sidebar, branch icon — or `⌃ ⇧ G`) shows git status. The integrated terminal (`⌃ \``) is where you'll run Claude Code.

### Your typical loop

In VS Code's integrated terminal, from the repo root:

```bash
git pull                          # sync with main
git checkout -b feat/your-task    # branch
claude                            # start Claude Code in this repo
```

Claude Code now reads `CLAUDE.md` and is grounded in project context. Tell it what you want — for example:

> *"I'm picking up issue #6 (Agroforestry recipe). Read `methodology/recipes/water_harvesting.md` as the template, then scaffold `methodology/recipes/agroforestry.md` with the same eight-section structure. Stop after the master variable table so I can populate the rows."*

Iterate, test, then commit and push via VS Code's Source Control panel or by asking Claude Code to do it for you. Raise the PR via the GitHub UI or `gh pr create`; use the PR template.

### Where to look for what

| You want to… | Read this |
|---|---|
| Understand the system architecture, what's locked, who does what | [`CLAUDE.md`](./CLAUDE.md) |
| Learn the team's workflows and conventions | [`PLAYBOOK.md`](./PLAYBOOK.md) |
| Find a task to pick up | [Issues tab](https://github.com/CIAT/nbs_ruralscan/issues) (or [`.github/SEED_ISSUES.md`](./.github/SEED_ISSUES.md) if you're seeding the backlog) |
| Set up the project board / labels | [`.github/PROJECT_BOARD_SETUP.md`](./.github/PROJECT_BOARD_SETUP.md) and [`.github/setup-labels.sh`](./.github/setup-labels.sh) |
| Author or update a recipe | [`methodology/recipes/water_harvesting.md`](./methodology/recipes/water_harvesting.md) (canonical pattern) + `/new-recipe` slash command |
| Author or update a Variable Card | [`.claude/commands/update-variable-card.md`](./.claude/commands/update-variable-card.md) + the issue template |
| Understand a module's I/O contract | [`methodology/modules/`](./methodology/modules/) |
| Look at the live demonstrators | https://ciat.github.io/nbs_ruralscan/ |

If you're brand new, **read CLAUDE.md and PLAYBOOK.md before your first issue.** Together they're about 15 minutes. They'll save you days of misunderstanding the architecture.

---

## Repo structure

| Folder | Contents |
|---|---|
| `docs/` | GitHub Pages — live demonstrators (wireframe + pipeline diagram) |
| `methodology/` | Cross-cutting framework + per-NbS recipes + module specs |
| `schema/` | T0–T7 schema tables and reference (ERD) |
| `pipeline/` | GEE Python implementation, pilot Colab notebooks, GEE App |
| `reference/` | Stocktake findings, source R scripts, literature references |
| `.claude/` | Project memory and slash commands for Claude Code |
| `.github/` | Issue templates, PR template, project board setup, seed issues |

## Contributing

Detailed walkthrough in [`CONTRIBUTING.md`](./CONTRIBUTING.md). Team workflows in [`PLAYBOOK.md`](./PLAYBOOK.md). Project memory for Claude Code in [`CLAUDE.md`](./CLAUDE.md). Open an issue using one of the templates; raise a PR using the PR template; we review and merge.

## Team

Alliance Bioversity International & CIAT — Climate Action Net Zero. Pete Steward (Team Lead, p.steward@cgiar.org). Full team in [`CLAUDE.md`](./CLAUDE.md#team--roles).

## License

See [LICENSE](./LICENSE).
