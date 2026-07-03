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

## Seeing the source (📷 show source region)

Each flagged card can show you **where in the paper** the claim came from. What it takes
to see it depends on whether the source is **open-access** or **restricted (copyright)** —
the card tells you which with a badge, top-right:

| Badge | Meaning | What you need to do |
|---|---|---|
| 🟢 **OA** | Open-access source | **Nothing.** The highlighted crop is pre-rendered and ships with the dashboard — it just appears, on the public site and locally. |
| 🟡 **RESTRICTED** | Copyrighted (non-open-access) | The crop is **never** published (we're not allowed to). To see it you need the PDF **on your own machine** — see below. |

### Restricted sources — you need the file locally

We cannot put copyrighted papers on the public site, so their crops are **only** viewable
by team members with access to the file. If a restricted card shows **"crop unavailable"**,
it means the PDF isn't on your machine yet. Two ways to fix it:

**A — Sync the library offline in OneDrive (recommended, once).**
The team library lives in SharePoint / OneDrive:
`Alliance-ClimateActionNetZero → ClimateActionNetZero → 1_Projects → D591_Rural-Scan_NBS → 2_Technical_&_Data`
— both the `library/` **and** `Stocktake Review/` folders.

> ⚠️ **This is the step everyone misses.** By default OneDrive lists folders as
> **cloud-only placeholders that are not actually on disk** — so the review server can't
> read them and crops show *"crop unavailable"*. In the **OneDrive** app (or Finder/File
> Explorer), **right-click the folder → "Always keep on this device"**. That downloads the
> real files. This has been the #1 source of confusion.

Then start the local review server and crops render automatically (it copies each PDF into
the cache on first use). If your OneDrive folder name differs from the default, point the
server at it:
```
NBS_LIBRARY_ROOT="<...>/1_Projects" uv run python3 -m nbs_ruralscan.schema_tools.review_server
```
To pre-copy every registered PDF into the cache in one pass:
```
python3 scripts/hydrate-corpus.py
```

**B — Just click the SharePoint link on the card.**
Don't want to sync, or a file won't render? The card has an **"open … in SharePoint ↗"**
link — it opens the paper (or the highlighted crop) in your browser. Needs your **CGIAR
login**. If it won't open, you don't have library access yet → ask **Pete or Namita** to
share it.

**Can't see the source at all?** You can still review from the **verbatim quote** on the
card — that's the exact text the claim was extracted from. Use the SharePoint link only
when you need the surrounding context (e.g. a table's column headers).

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
