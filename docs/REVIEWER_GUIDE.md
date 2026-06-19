# QA/QC Reviewer Guide — how to review evidence locally

The public dashboard (`https://ciat.github.io/nbs_ruralscan/dashboard.html`) is **read-only**.
To make review decisions that **stick** (write to the evidence register), you run a small
local server on your machine. It's ~3 commands. You need **write access to the repo**
(ask Pete if you're not sure) and **GitHub + a terminal**.

## One-time setup

1. **Install `uv`** (Python runner) — https://docs.astral.sh/uv/getting-started/installation/
   (macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
2. **Clone the repo:**
   ```
   git clone https://github.com/CIAT/nbs_ruralscan.git
   cd nbs_ruralscan
   ```

## Each review session

1. **Pull the latest** so you're not editing stale data:
   ```
   git pull
   ```
2. **Start the review server** (from the repo root):
   ```
   uv run python3 -m nbs_ruralscan.schema_tools.review_server
   ```
3. **Open** http://localhost:8765/dashboard.html → **QA / QC Flags** tab.
   (You'll see "Live review server connected" — that's how you know edits will save.)
4. **Set your handle** in the header **Reviewer** dropdown (your GitHub handle).
5. **Review** in the **AI-flagged** view:
   - Read the **quote** + **why flagged**; for tables click **📷 show table region**.
   - Pick a **reason** (hover each for its meaning) → click **ok** (keep) or **drop** (remove).
   - Repeat. Your picks are saved as you go (pending).
6. **Apply decisions & rebuild** (sidebar) — writes them to the register, re-runs the gates.
   - **ok** → evidence kept, flag cleared. **drop** → **quarantined** (kept as a record,
     excluded from analysis, fully reversible — not deleted).
   - If two reviewers disagree on a unit, it becomes a **conflict** (stays pending until you agree).
7. **Commit + push** so everyone (and the public site) gets your work:
   ```
   git add -A && git commit -m "qaqc: review <what you did>" && git push
   ```
   The public site rebuilds in ~2 minutes.

## Good to know

- **Views:** *AI-flagged* (open queue) · *AI-passed sample* (spot-check what the AI let through)
  · *2nd opinion* (units one reviewer resolved, awaiting a second) · *My reviewed* (your history,
  re-openable) · **📊 Stats** (header — how well the AI's flags are doing).
- **Filters** (top of cards): by verdict, by your status, or **tables-only**.
- **Source PDFs:** the **SharePoint** link opens the paper (needs your CGIAR login).
- **Reviewer handle = attribution, not a login.** Edits are gated by repo write access, not
  the dropdown — pick your real handle.
- **Nothing is destroyed.** Dropped units are quarantined and can be re-opened; every decision
  is logged in `pipeline/metrics/review_log.csv`.

Questions → Pete, or the Teams `NbS Rural Scan Task Force` channel.
