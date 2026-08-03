# Handover — working with Claude Code on NbS Rural Scan

> **For Namita.** Everything you need to run Claude Code on this repo from your own
> (Windows) machine and pick up your lanes. Written 2026-08-03. If a step fights you,
> ping Pete on the `NbS Rural Scan Task Force` Teams channel — don't burn an afternoon.

This is the *getting-started + current-state* map. The deeper references stay where they
are: [`AGENTS.md`](./AGENTS.md) (what's locked / architecture — Claude Code reads it
automatically), [`PLAYBOOK.md`](./PLAYBOOK.md) (how we work), [`CONTRIBUTING.md`](./CONTRIBUTING.md)
(first-PR walkthrough), [`docs/REVIEWER_GUIDE.md`](./docs/REVIEWER_GUIDE.md) (QA review).

---

## 1. What this project is (60-second version)

A World Bank–funded **scoping** methodology + demonstrator (D591) that helps TTLs see
*where* different Nature-based Solutions could be invested, *how big* the opportunity is,
and *which priorities* (poverty, biodiversity, climate risk, gender) it intersects. **Not**
feasibility, not site design, not CBA — those are downstream (Module 6).

The analytical backbone is the **T0–T7 schema + evidence registers** (SRC · EV · VONT ·
FAM · BIND). Analytical rules are never hardcoded — they live in the schema, read by the
Python package (`src/nbs_ruralscan/`). Evidence is **traceable**: every value → an evidence
unit → source · page · verbatim quote.

## 2. Your lanes (Namita)

| Lane | Where it lives | Current state |
|---|---|---|
| **QA/QC evidence review** | dashboard QA tab + local `review_server.py` — you're an allowlisted reviewer (`Namita-J`), so your PRs auto-merge on green CI | Live. This is the fastest way to start. See §6. |
| **Expert-opinion elicitation & integration (Task H)** | [`methodology/expert_opinion_protocol.md`](./methodology/expert_opinion_protocol.md) | Protocol drafted. Expert claims flow through the **same** EV pipeline as literature (`evidence_type=expert`) — don't invent a parallel store. |
| **Recipes + Variable Cards** | `methodology/recipes/` · `/new-recipe`, `/update-variable-card` slash commands | Agroforestry is the worked NbS; water-harvesting is the canonical template. |
| **M6 Implementation Hand-off (lead)** | `methodology/modules/M6_*` + MFL team | Yours to drive. |

## 3. Current repo state (2026-08-03)

- Branch **`main`** is the trunk; HEAD `c76fbd8`. `main` is **protected** (CI + 1 approval).
- **Ruleset version `v1.4.1`** (2026-07-20) — the frozen search/extraction instructions
  ([`methodology/RULESET_VERSIONS.md`](./methodology/RULESET_VERSIONS.md)). Every evidence
  row pins to a ruleset version so past sweeps stay reproducible.
- Evidence so far: **~3,100 EV rows across ~52 sources**, agroforestry only. T4 (suitability)
  synthesised for families **F2 (FMNR / regeneration)**, **F3 (silvopastoral)**, and
  **cross-family**; F1 (planted silvoarable) is the fully-evidenced example.
- **Species/crop lane** is live — per-taxon claims are tagged (`claim_scope` + `taxon`) and
  **kept out of the practice-level MCDA but retained** for a future species layer. The file
  you had open, `docs/crops/manifest.json`, is the generated index behind that lane.
- Open PR: **#122 `feat/dataloaders`** (Brayden, geospatial loaders) — not yours.
- One-click **"Apply & submit to main"** QA flow is live for allowlisted reviewers.

## 4. One-time setup on your machine (Windows)

You need five tools. Install once, then you never think about them again.

| Tool | What for | Install |
|---|---|---|
| **Git for Windows** | git + **Git-Bash** (the `bash` the submit flow needs) | https://git-scm.com/download/win — accept defaults |
| **VS Code** | editor + integrated terminal (where Claude Code runs) | https://code.visualstudio.com |
| **Claude Code** | the pair programmer | `irm https://claude.ai/install.ps1 \| iex` in PowerShell, or see https://docs.claude.com/en/docs/claude-code/setup |
| **GitHub CLI (`gh`)** | PRs / issues / auth | `winget install GitHub.cli` then `gh auth login` |
| **uv** | Python runner (runs the review server, tests, generators) | `irm https://astral.sh/uv/install.ps1 \| iex` |

Then clone and run the one-time repo setup:

```bash
git clone https://github.com/CIAT/nbs_ruralscan.git
cd nbs_ruralscan
bash scripts/setup-repo.sh        # registers the JSON merge driver + sets autocrlf=false
```

`setup-repo.sh` is **required on Windows** — it pins `core.autocrlf false` so the CSV
registers keep LF line endings (otherwise you get spurious diffs), and it registers the
`regen` merge driver so generated JSON auto-rebuilds instead of throwing merge conflicts.

Confirm everything is there:

```bash
git --version && gh --version && claude --version && uv --version
```

### Windows gotchas (read these — they've each cost someone a day)

- **Run the QA submit + scripts from Git-Bash**, not PowerShell/CMD. The one-click
  "Apply & submit to main" auto-locates Git-Bash; if it can't find it, open **Git Bash**
  and run `bash scripts/submit-review.sh Namita-J --auto` yourself.
- **OneDrive "cloud-only" files.** The evidence PDFs live in SharePoint/OneDrive as
  *placeholders not on disk* by default, so the review server can't read them and source
  crops show *"crop unavailable"*. Fix: right-click the library folder →
  **"Always keep on this device"**. This is the #1 source of confusion.
- **`NBS_LIBRARY_ROOT`** — if your OneDrive folder name/path differs from the default, point
  the tools at it: `NBS_LIBRARY_ROOT="C:/Users/<you>/OneDrive - .../1_Projects" ...`.

## 5. How to actually work with Claude Code

Claude Code reads [`AGENTS.md`](./AGENTS.md) on **every** session — it starts grounded in
the architecture, what's locked, the team, the conventions. You never brief it cold.

Your loop, in VS Code's integrated terminal from the repo root:

```bash
git checkout main && git pull          # sync
git checkout -b <type>/<short-desc>    # branch — feat/ fix/ docs/ chore/
claude                                 # start Claude Code here
```

Tell it what you want in plain language and reference the issue. Good first prompts for
your lanes:

- *"Read `methodology/expert_opinion_protocol.md`. I'm running an elicitation with 3 MFL
  experts on agroforestry suitability thresholds. Draft the capture template that lands
  their claims as `evidence_type=expert` EV rows through the normal pipeline — don't create
  a separate store."*
- *"Read `methodology/recipes/water_harvesting.md` as the canonical template, then scaffold
  `methodology/recipes/<nbs>.md` with the same eight-section structure. Stop after the
  master variable table so I can populate rows."*
- *"Add a Variable Card for `<variable>` in the agroforestry recipe — same six-slot
  structure as the slope card."* (or `/update-variable-card <variable> agroforestry`)

**Rules Claude Code already enforces (don't fight them):** never hand-author evidence (it
must come through the deterministic pipeline over a cached source), never hardcode
analytical rules (they go in the schema), extraction subagents write only to
`pipeline/staging/` and never run git. All of this is in `AGENTS.md`.

## 6. Your fastest first win — QA evidence review

This uses your reviewer allowlisting and produces a merged contribution the same day.

```bash
git pull                                                     # (see the red "new version — pull" banner? do this)
python3 scripts/hydrate-corpus.py                            # copy PDFs/web snapshots into the local cache (needed for the guardrail)
uv run python3 -m nbs_ruralscan.schema_tools.review_server   # starts http://localhost:8765
```

Open http://localhost:8765/dashboard.html → **QA/QC** tab → set your handle to `Namita-J`.
Work the **AI-flagged** queue: **ok** (keep) or **drop** (needs a coded reason —
`off_scope`, `wrong_practice`, `wrong_table`, `unusable_value`, `table_error`). For
species/crop rows use **🧬 reclassify**, not drop — it retags and keeps them.

Then click **✓ Apply & submit to main** — one button: writes your decisions, regenerates
JSON, branches off latest `main`, opens a `qaqc:` PR, and **auto-merges on green CI**
(because you're allowlisted). Run it **once per session**, not per flag.

Full detail (including the OneDrive source-crop steps): [`docs/REVIEWER_GUIDE.md`](./docs/REVIEWER_GUIDE.md).

## 7. Before any PR that touches `src/` or `schema/`

```bash
uv run ruff check . && uv run ruff format .
uv run ty check
uv run pytest
python3 src/nbs_ruralscan/schema_tools/generate.py schema --check   # CSV is source of truth; JSON is generated
python3 src/nbs_ruralscan/schema_tools/structure.py schema          # frozen column manifest
```

CI runs the same gates. Edited a schema CSV? Regenerate its JSON (`generate.py schema`, no
`--check`) and commit both — CI fails on stale JSON.

## 8. Where to go next

| You want to… | Read |
|---|---|
| Understand what's locked / the architecture | [`AGENTS.md`](./AGENTS.md) |
| Learn the team workflows | [`PLAYBOOK.md`](./PLAYBOOK.md) |
| Do your first PR end-to-end | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
| Review evidence | [`docs/REVIEWER_GUIDE.md`](./docs/REVIEWER_GUIDE.md) |
| See the live demonstrators | https://ciat.github.io/nbs_ruralscan/ |
| Find a task | [Issues](https://github.com/CIAT/nbs_ruralscan/issues) · [Delivery board](https://github.com/orgs/CIAT/projects/2) |

Welcome to the driver's seat. Ask Claude Code first for anything code-shaped — it knows the
conventions. Ask Pete for anything scope-shaped.
