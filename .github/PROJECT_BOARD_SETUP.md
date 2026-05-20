# Projects v2 board — one-off setup runbook

Click-by-click guide to setting up the **NbS Rural Scan — Delivery** project board on GitHub. ~15 minutes end-to-end. Done once.

> The GitHub Projects v2 UI shifts occasionally. If a label or menu position has moved, the underlying concept stays the same — search the page for the named element.

---

## Step 1 — Create the project

1. Open the repo: https://github.com/CIAT/nbs_ruralscan
2. Click the **Projects** tab in the repo's top nav (between *Pull requests* and *Wiki*).
3. Click the green **New project** button (top right).
4. Choose the **Board** template.
5. Project name: `NbS Rural Scan — Delivery`
6. Description: `Coordination board for the World Bank D591 NbS Rural Scan consultancy. Issues, PRs, and pilot tasks.`
7. Click **Create project**.

You should now see an empty board with three default columns: **Todo**, **In Progress**, **Done**.

---

## Step 2 — Customise the Status column (5 columns instead of 3)

The Status field is what drives the columns. We want five values: **Backlog · This week · In progress · Review · Done**.

### Method A — via the board view (faster)

1. In the new project, click the **+ Add column** button to the right of *Done*.
2. Type **Review** → press Enter.
3. Click **+ Add column** again, type **This week** → Enter.
4. Click on the **Todo** column header → small dropdown → **Edit** → rename to **Backlog**.
5. Now drag columns into the desired order (left-to-right): **Backlog → This week → In Progress → Review → Done**.
   - Drag from the column header.

### Method B — via Settings (more robust)

1. Click the **…** (kebab) menu at the top right of the project → **Settings**.
2. In the left sidebar, click **Custom fields** (or *Fields*).
3. Click **Status** (the default single-select field).
4. You see three options: Todo · In Progress · Done.
5. Rename **Todo** → **Backlog**.
6. Click **+ Add option** → name it **This week** → save.
7. Click **+ Add option** → name it **Review** → save.
8. Drag options into the order: **Backlog → This week → In Progress → Review → Done**.
9. Click **Save**.

Either method gives you the right five-column board.

---

## Step 3 — Add a few useful custom fields (optional but recommended)

In **Settings → Custom fields**, click **+ New field**:

1. **Owner** — type: *Single select*. Options: Pete · Benson · Namita · Brayden · Sarah · Chris · Evert · Hannes · Ani · Lolita · Anastasia. *(Why a custom field on top of GitHub's built-in assignee? Because Projects v2 doesn't visualise GitHub assignees in board column headers as cleanly. Optional — can skip if you prefer to use plain assignees.)*
2. **Module** — type: *Single select*. Options: M0 · M1 · M2 · M3 · M4 · M5 · M6 · cross-cutting.
3. **NbS** — type: *Single select*. Options: agroforestry · water-harvesting · forest-restoration · riparian-buffer · other.
4. **Estimate (days)** — type: *Number*. Optional, useful for sprint planning later.

Each new field auto-appears in the board view and can be added to any item.

---

## Step 4 — Add useful views

A view is a saved arrangement (filter + grouping + columns). Multiple views read the same data — they're just different lenses.

In the project, look at the bottom of the page — there's a tab strip showing the current view (probably called *Board*). Click **+ New view** next to it.

Add these views:

### View: "By Module"
- Type: **Board**
- Group by: **Module** custom field
- Name: `By Module`
- Now each column is a module (M0–M6) so you can see how each module's work stands.

### View: "By Owner"
- Type: **Board**
- Group by: **Owner** custom field (or **Assignees** if you skipped Step 3)
- Name: `By Owner`
- Shows the workload per person at a glance.

### View: "By NbS"
- Type: **Board**
- Group by: **NbS** custom field
- Name: `By NbS`
- Tracks recipe progress per NbS.

### View: "By Phase" (uses Milestones)
- Type: **Table**
- Group by: **Milestone**
- Name: `By Phase`
- Tabular layout reads better for milestone tracking than a board.

### View: "All open" (the master)
- Type: **Table** or **Board**
- Filter: `is:open`
- Sort by: Updated (descending)
- Name: `Open`
- The default "what's everything not done" view.

You now have 5 views over the same set of items.

---

## Step 5 — Set up workflow automation

Workflows live at: **Project Settings** (gear icon top right of the project, or *…* menu → Settings) → **Workflows** (left sidebar).

You'll see ~6 built-in workflows, all initially disabled.

Enable these four:

### Workflow A: Auto-add new issues to this project

1. Click **Auto-add to project**.
2. Toggle the workflow **On** (top-right switch).
3. Set the filter: `repo:CIAT/nbs_ruralscan is:issue`
   - This auto-adds new issues from the repo. Excludes PRs — we add those manually when they link to an issue, or via a separate filter if desired.
4. Click **Save**.

> Optional second auto-add for PRs: repeat with filter `repo:CIAT/nbs_ruralscan is:pr`. Recommended — keeps PRs visible alongside the issues they close. Up to you.

### Workflow B: Set initial status to Backlog

1. Click **Item added to project**.
2. Toggle **On**.
3. Set: When → *Item is added* · Set → **Status = Backlog**.
4. Click **Save**.

Combined with Workflow A: every new issue lands in Backlog automatically.

### Workflow C: Auto-move to Done when issue is closed

1. Click **Item closed**.
2. Toggle **On**.
3. Set: When → *Item is closed* · Set → **Status = Done**.
4. Click **Save**.

### Workflow D: Auto-move to Done when PR is merged

1. Click **Pull request merged**.
2. Toggle **On**.
3. Set: When → *Pull request is merged* · Set → **Status = Done**.
4. Click **Save**.

This catches the case where a PR's closure of an issue (via `Closes #42`) should mark the project item as done.

### Workflow E (optional): Code review approved → Status = Review

If you want PRs to auto-move to Review when approved (rather than when opened):

1. Click **Code review approved**.
2. Toggle **On**.
3. Set: When → *Pull request review is approved* · Set → **Status = Review**.
4. Click **Save**.

---

## Step 6 — Manual transitions (what's not automated)

A few transitions remain manual — that's by design. The team uses them:

| Transition | How |
|---|---|
| **Backlog → This week** | At Monday standup, drag the item into *This week* column |
| **This week → In Progress** | When you start work, drag to *In Progress* |
| **In Progress → Review** | Drag manually when you raise the PR (or set up Workflow E above to auto-do this on PR approval) |
| **Done → archived** | After a week or so, archive done items via *…* → *Archive*; or set up **Auto-archive items** workflow below |

### Workflow F (optional): Auto-archive done items after 14 days

1. Click **Auto-archive items**.
2. Toggle **On**.
3. Set: filter → `status:Done updated:<@today-14d`
4. Save.

Keeps the board tidy without manual archiving.

---

## Step 7 — Add the project to the repo README (optional)

Anyone landing on the repo home should know the board exists. Update the repo `README.md` to include a project link:

```markdown
## Project board

Active work is tracked at the [Delivery board](https://github.com/orgs/CIAT/projects/<board-id>).
```

(Get the board ID from the URL after creating it — it's an integer in the path.)

---

## Step 8 — Verify it works

End-to-end smoke test:

1. Open a new test issue via any template (e.g. "Test issue, please close").
2. Check the project board → it should appear in the **Backlog** column automatically.
3. Close the issue.
4. Refresh → the item should move to **Done**.
5. If that round-trip works, automation is correctly wired. Delete the test issue.

---

## Done

You now have:

- A 5-column Kanban board reflecting the team's workflow
- Three custom fields (Owner / Module / NbS) plus optional Estimate
- Five views (Board · By Module · By Owner · By NbS · By Phase · Open)
- Four-to-six automation workflows running the board state

Total setup time: ~15–20 minutes.

After this, open the seed issues from `SEED_ISSUES.md` and they'll populate the board automatically.
