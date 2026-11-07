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

## Filing papers someone downloaded by hand (ResearchGate, institutional access)

Save each PDF in `~/Downloads` as `<source_id>.pdf` (the ID from `pipeline/acquisition_queue.csv`), then run:

```
uv run python3 scripts/intake-downloads.py --dry-run   # check what would be filed
uv run python3 scripts/intake-downloads.py             # file them
uv run python3 src/nbs_ruralscan/schema_tools/verify_metadata.py verify   # stamp DOI rows
```

Each file must show the citation's title on its opening pages. A body-only match is held
for manual chapter/reference identity review; a mismatch is refused and left in Downloads. Accepted files are copied to
`.cache/corpus/` and to the SharePoint library folder (via the OneDrive mirror), the queue row is
marked `acquired`, and the download moves to `~/Downloads/nbs_ingested/`. Nothing is downloaded
by the script: ResearchGate and publisher downloads stay human clicks (their terms forbid
automated downloading).

**Code / web sources in the queue.** `--queue` also snapshots acquired queue rows that have a `url`
but no library PDF (e.g. a tool's commit-pinned GitHub file: `/blob/` → raw `.txt`, anything else →
`.html`), the same way the SRC pass does. For a full tool interrogation across many repository
files use `python -m nbs_ruralscan.ingest.github <owner/repo> <commit> --subdir …`.

## Independent paths and recoverable publication

The existing commands and defaults remain available. To use records and storage outside
the compiler checkout, select their locations explicitly:

```bash
python3 scripts/hydrate-corpus.py --root /data/evidence \
  --corpus-dir /data/corpus --library-root /team/library-parent \
  --archive-dir /data/reviewed-archives --queue --dry-run

python3 scripts/intake-downloads.py --root /data/evidence \
  --corpus-dir /data/corpus --library-root /team/library-parent \
  --dir /data/downloads --dry-run
```

`--root` selects the existing record layout: `schema/registers/SRC_source_register.csv`
and `pipeline/acquisition_queue.csv`. Hydration defaults its archive search to
`methodology/audits/*/<source_id>.md` under that root. Manual intake also accepts
`--queue-path` for a queue outside that layout. The library root is the folder **before**
the relative path recorded in `library_path` or `target_library_path`; it is independent
of the corpus directory. Do not select overlapping storage roots.

Hydration prepares missing files privately, then publishes the selected batch with
recovery for caught errors. Existing cached snapshots retain their original bytes.
WOCAT missing-transcript repair still refreshes its source/transcript/provenance bundle;
tracked approach transcripts with the recorded hash remain the preferred offline source.
Hydration preserves source bytes and routing; it does not newly verify source identity or
stamp acquisition/extraction progress. `--nbs` retains its existing scope: it filters only
the queue pass and matches the entire `nbs_id` cell, while the SRC pass remains unfiltered.

Hydration `--dry-run` still downloads and validates privately; it publishes no corpus files.
Manual-intake `--dry-run` checks local downloads only. Normal intake publishes cache,
library and archive copies before updating the queue. Downloads are removed only after
successful publication, unless `--keep` is supplied. If cleanup fails or a download changes,
the command reports **CLEANUP PENDING**, returns a failure status and preserves the changed
original; the published queue/copies remain valid. Reconcile the reported files before retrying.

GitHub interrogation and WOCAT acquisition accept `--corpus-dir`. Each GitHub text/provenance
pair and each WOCAT source/transcript/provenance bundle is published together. The multi-source
commands still progress source by source; they are not one transaction across the entire repository
or source list. Review previews use the same recoverable publication mechanism for missing
code/PDF files and serialize hydration within their server process.

Use stable inputs and one writer for a selected corpus. A reported `PublicationRecoveryError`
means recovery was incomplete: retain the named recovery directory, stop writes to those paths,
and reconcile the retained and current files before retrying. These operations handle caught
errors; they do not guarantee recovery after power loss, lock other processes, provide a
simultaneous multi-file reader snapshot or confirm remote OneDrive/SharePoint synchronization.
