# NbS Rural Scan

Methodology and demonstrator for spatial prioritisation of Nature-based Solutions in rural, agricultural, and forestry landscapes. Funded by the World Bank (D591). Implemented by Alliance Bioversity International & CIAT.

> ⚠ **Status:** v0 work-in-progress. Mock data only. Not yet a production decision tool.

---

## 👋 Team kickoff — start here

Welcome Benson, Namita, Brayden (and everyone else who lands here). This repo is the shared home for our methodology and workflow going forward. **Please spend ~15 minutes reading this section before picking up any work.**

### What's here

The scaffolding covers the methodology (modules, schema, recipes), the team's working conventions, and a populated project board with the first 15 issues. It's a *spine* you hang your work off — not a replacement for what's already been done.

### Three things to look at, with your feedback in mind

1. **[Pipeline architecture (v0.4)](https://ciat.github.io/nbs_ruralscan/pipeline.html)** — one-page map of the 7 modules + the M2b disaster-risk addendum and the T0–T7 schema. The *framework primitives* layer at the top (canonical membership functions, hybrid weighting, MCDA engine, recipe template) is reusable and read by every module; some run back-end and aren't surfaced in the TTL view.
2. **Module specs — M1 and M2**
   - **[M1 Suitability](./methodology/modules/M1_suitability.md)** — the I/O contract and 8 sub-steps for the suitability → opportunity-space stage, implemented in Python under `src/nbs_ruralscan/`. Function signatures in §13.
   - **[M2 Rural Climate Risk](./methodology/modules/M2_climate_risk.md)** — **Brayden**, pre-scaffolded for you. Mode A vs Mode B, double-count guard with M3/M4, function signatures for `pipeline/climate_risk.py`. Six open methodology questions at the bottom that need your view.
3. **Repo conventions + workflow** — [`CLAUDE.md`](./CLAUDE.md), [`PLAYBOOK.md`](./PLAYBOOK.md), [`CONTRIBUTING.md`](./CONTRIBUTING.md). **Namita** — keen on your take here since you'll coordinate recipe authoring + Variable Cards.

### Ownership (current — June 2026)

> Shifted since the kickoff snapshot. See the [Delivery board](https://github.com/orgs/CIAT/projects/2) for live, issue-level state.

- **Pete** — framework integrity & scope-control · M0 Setup · **M1 Suitability · M3 Opportunity Space · M4 Priority Hotspots** · M6 Implementation Hand-off (lead)
- **Brayden** — M2 Rural Climate Risk · M2b Project Disaster-Risk · **dataset download layer (T1 → Python) and analytical-context construction (T7); server-side preferred (GEE / STAC / large services)**
- **Namita** — **expert-opinion elicitation + pipeline integration** · M5 content · per-NbS recipes · Variable Cards · coordination
- **Benson** — **QA/QC across all modules**: dataset fitness sign-off, output validation, resolution audit
- **MFL team** (Sarah · Chris · Evert · Hannes) — M6 hand-off content, ecosystem-services & domain input

Runtime is **Python via Claude Code** (`src/nbs_ruralscan/`), driven by Brayden / Anastasia / Pete. Native server-side GEE and the GEE App are **dropped** — we pull GEE data into Python and build/stress-test the method through the wireframe.

**Implementation pathway is bifurcated.** Minimum committed deliverable is a Colab notebook worked example per pilot (the WB contract obligation — notebooks, not a polished web app). In parallel, the **Claude-Code-built front/back end** is being explored against the same schema (wireframe = front-end demonstrator; backend reads `schema/registers/` + T0–T7). Both consumers read the same registers — schema stability matters.

### Feedback forum — 1:1 catch-ups

Given staggered availability (Namita out next week; Brayden on leave Monday), the walkthrough happens as three separate 1:1s rather than a group session:

- **Benson — Monday** (calendar invite already sent). 60 min, focused on the framework primitives layer, M1, and the architecture overall.
- **Brayden — when back**. 30–45 min, focused on M2 and the six open methodology questions.
- **Namita — when back**. 45–60 min, focused on recipes, M3/M5, Variable Cards, and the workflow side.

In each: bring questions, pushback, "this is wrong because…" — all welcome.

### Framings worth flagging

- This is **scaffolding**, not a fait accompli.
- The framework primitives draw on prior CIAT MCDA work and are treated as canonical.
- Module specs are I/O contracts you can adjust, not briefs being handed to you.
- The wireframe is being sent for visual polish separately — feedback on flow and content is welcome.

---

## What this is

A scoping and decision-support framework that helps World Bank Task Team Leaders (TTLs) identify where different Nature-based Solutions could be invested in, how extensive the opportunity is, and which TTL priorities (poverty, biodiversity, climate risk, gender equity) intersect that opportunity space. Outputs are reproducible Jupyter/Colab notebooks plus an interactive demonstrator UI.

## Live demonstrator

**https://ciat.github.io/nbs_ruralscan/**

Includes:
- **TTL Tool Wireframe** — interactive mockup of the decision-support tool
- **Pipeline Architecture (v0.4)** — one-page methodology architecture diagram
- **Data Schema (v0.2.9)** — the T0–T7 ERD, field-level spec, evidence/config registers, and draft-0 example tables (structure frozen + machine-validated)

Demonstrators use mock Sierra Leone / agroforestry data.

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
| `docs/` | GitHub Pages — live demonstrators (wireframe · pipeline diagram · schema page + ERD) |
| `methodology/` | Framework + per-NbS recipes + module specs + **`T4_generation_method.md`** (evidence-first suitability generation) + **`families/`** (suitability-family schemes) + `examples/` (worked gold standards) |
| `schema/` | `spec.md` (v0.2.9: T0–T7 + evidence/config registers SRC·EV·VONT·FAM·BIND), `structure/columns.json` (frozen column manifest), ERD, dedup notes, draft-0 example tables (CSV+JSON) for 2 NbS |
| `src/nbs_ruralscan/` | Python method package — doc ingestion, evidence→synthesis→recipe engine, BIND dataset resolver, structure validator (uv · ruff · ty · pytest) |
| `pipeline/` | Pilot Colab notebooks and outputs |
| `reference/` | Stocktake findings, source R scripts, literature references |
| `.claude/` | Project memory and slash commands for Claude Code |
| `.github/` | Issue templates, PR template, project board setup, seed issues |

## Contributing

Detailed walkthrough in [`CONTRIBUTING.md`](./CONTRIBUTING.md). Team workflows in [`PLAYBOOK.md`](./PLAYBOOK.md). Project memory for Claude Code in [`CLAUDE.md`](./CLAUDE.md). Open an issue using one of the templates; raise a PR using the PR template; we review and merge.

## Team

Alliance Bioversity International & CIAT — Climate Action Net Zero. Pete Steward (Team Lead, p.steward@cgiar.org). Full team in [`CLAUDE.md`](./CLAUDE.md#team--roles).

## License

See [LICENSE](./LICENSE).
