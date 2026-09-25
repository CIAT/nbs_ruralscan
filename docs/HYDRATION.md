# Corpus hydration — getting the source PDFs onto your machine

`.cache/corpus/` holds the source artifacts (PDFs, web/code snapshots) that every
evidence operation is checked against. It is **gitignored** — copyright, and
`githubusercontent.com` attachment URLs are public — so a fresh clone has none of it and
you hydrate it yourself from the SharePoint library.

You need it for two different jobs:

| Job | What must be cached | Command |
|---|---|---|
| **QA/QC review** (Apply's provenance guardrail verifies every quote against the cached artifact) | the sources already in `SRC` | `python3 scripts/hydrate-corpus.py` |
| **An extraction sweep** (the sources you are about to read) | the acquisition queue's `acquired` rows — **these have no `SRC` row yet** | `python3 scripts/hydrate-corpus.py --queue` |

The second case is the one that trips people up: a source being swept is **pre-`SRC`** — its
`SRC` row is written at the central merge, *after* extraction — so the default (SRC-driven)
pass cannot see it. Use `--queue`.

## One-time: point at the library

The script copies from your local OneDrive mirror of the SharePoint library. It defaults to
the Mac mount; set `NBS_LIBRARY_ROOT` if yours differs. It must point at the folder that
**contains** `D591_Rural-Scan_NBS/` (i.e. `.../1_Projects`), because the queue's
`target_library_path` is relative to that.

```bash
# macOS (default — usually no need to set it)
export NBS_LIBRARY_ROOT="$HOME/Library/CloudStorage/OneDrive-CGIAR/ClimateActionNetZero/1_Projects"

# Windows (Git Bash) — note the SharePoint-synced folder name
export NBS_LIBRARY_ROOT="$USERPROFILE/OneDrive - CGIAR/Alliance - ClimateActionNetZero - Documents/ClimateActionNetZero/1_Projects"
```

Check it resolves before you run anything: `ls "$NBS_LIBRARY_ROOT/D591_Rural-Scan_NBS/2_Technical_&_Data/library"`
should list `1_Agroforestry` … `5_Wetlands_Constructed`.

**OneDrive Files On-Demand**: a file that shows in Explorer but is cloud-only still copies
fine (OneDrive downloads it on read) — but it is slow on a cold cache, and it fails silently
if you are offline. If you get a long `MISSING` list, open the library folder in Explorer/Finder
and make sure it has finished syncing.

## Hydrating for a sweep

Per NbS (recommended — you see exactly what the sweep will have):

```bash
python3 scripts/hydrate-corpus.py --queue --nbs forest_restoration
python3 scripts/hydrate-corpus.py --queue --nbs wetland_management
python3 scripts/hydrate-corpus.py --queue --nbs water_harvesting_conservation
```

Or all of them: `python3 scripts/hydrate-corpus.py --queue`.

**How many files to expect.** The three queued sweeps are **up to 104 PDFs on a cold cache**
— forest restoration 40, wetlands 25, water harvesting 39 — and **fewer if you have hydrated
before**, since anything already in `.cache/corpus/` is skipped. A machine that has been
through the agroforestry and riparian rounds will copy far fewer than 104; a clean clone
copies all of them. `already cached` is a normal, healthy line — not a failure.

## Reading the output

```
acquisition queue (forest_restoration)
queue PDF copied    : 12
queue already cached: 28
SKIP spruce_drought_succession - not acquired (OA (websearch:academia/med))
SKIP reforestation_drought_west_africa_2017 - not acquired (paywalled (closed, Springer))
```

- **`copied` / `already cached`** — ready to sweep.
- **`SKIP … not acquired`** — the row is still `status=pending` in
  `pipeline/acquisition_queue.csv`: nobody has put the PDF in the library yet, so there is
  nothing to copy. Expected, not an error.
- **`MISSING from library`** — the row says `acquired` but the file is not at
  `target_library_path`. That *is* a problem: either your `NBS_LIBRARY_ROOT` is wrong, the
  filename in the library does not match `<source_id>.pdf` exactly, or OneDrive has not
  synced it.

### The 18 pending rows — don't block on them

Across the three queued sweeps there are **18 rows still `pending`** (forest restoration 7,
water harvesting 6, wetlands 5): **5 are OA** and recoverable by browser/repository download
under the full OA-recovery rules (`methodology/search_protocol.md` §OA-recovery), **13 need
CGIAR institutional access** and sit with Pete.

**Sweeps run on what is cached.** The register is append-only, so stragglers join a later
pass — a pending row never justifies holding a sweep. Log the search and its PRISMA counts in
`SRCH` as usual; the sources that arrive later are extracted on top.

## The order of operations (pre-`SRC` sources)

```
acquire (PDF → SharePoint library, status=acquired)
  → hydrate (--queue, into .cache/corpus/)
    → extract (staging-only agents; quotes sliced from the cached PDF)
      → central merge: SRC row created from the verified queue metadata, EV rows written,
        gates run (validate_sources · check_numbers · check_scope · ledger.check)
```

The `SRC` row is **not** created before extraction. This is the order `PLAYBOOK.md`
("Acquisition queue") now states; earlier wording had the `SRC` row before hydration, which
is impossible for a source that has never been swept.

Two hard rules that bite here:

- **Extraction refuses any source with `doi_verified != true`** — such rows are acquired and
  extracted **by title**. Hydration itself doesn't check this; the extraction contract does.
- **Quotes are sliced from `page.get_text()`, never retyped** (ruleset v1.5.1 #18). If the
  PDF isn't cached, there is nothing to slice from — which is the whole point of this step.

Never commit a PDF. `.cache/corpus/` stays gitignored.

## Related

- `docs/REVIEWER_GUIDE.md` — the review-side setup (SRC hydration + the review server)
- `PLAYBOOK.md` → *Acquisition queue* and *Review flagged evidence*
- `methodology/search_protocol.md` → §OA-recovery
