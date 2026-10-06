# Discovery search protocol — stepped, logged, auditable

*So that "what searches did we run?" has a clear, queryable answer for every sub-practice.*

## The rule
For **each sub-practice (suitability family) × table (T4)**, run **each of the 4 discovery processes** and **log the protocol** in the `SRCH` register before claiming the search done.

> **T3/T6 deferred (2026-09, ruleset v1.5.0):** T3 and T6 are removed from the extraction exercise — no new T3/T6 searches are run or logged. Their completed search protocols are archived in `schema/registers/_deferred/SRCH_T3_T6_deferred_2026-09.csv`; restore path in `schema/registers/_deferred/README.md`.

### The 4 discovery processes
(= the ledger categories / dashboard audit-matrix columns)

| process | what it is | channel |
|---|---|---|
| **stock** | the benchmarked stocktake corpus (peer-reviewed, C/I/D tiered) | OpenAlex (historical) |
| **updated_lit** | focused peer-reviewed sweep beyond the stocktake | OpenAlex title-search |
| **grey** | reports / manuals / briefs | web search (EN/ES/FR) + CGSpace DSpace API + WOCAT |
| **tool** | tools / methods / codebases | GitHub + platforms |

## What every search logs (the `SRCH` register)
`schema/registers/SRCH_search_register.csv` — one row per (NbS × family × table × process × run):
- **`search_terms`** — the exact query strings used.
- **`screening_steps`** — the 5-step funnel applied: `frame · source_type · relevance · credibility_six_axis · saturation_stop`.
- **`inclusion_criteria`** — the in/out rule (what counts; what's excluded).
- **`limits`** — caps (e.g. `retrieve≤200/query; screen≤50; extract≤15`).
- **`n_retrieved` · `n_screened` · `n_included`** — PRISMA-lite counts.
- **`search_date` · `run_id` · `searched_by`** — provenance.
- **`ruleset_version`** — which instruction set governed it ([RULESET_VERSIONS.md](RULESET_VERSIONS.md)).
- **`discovery_log_ref`** — link to the narrative discovery log.

Log via `schema_tools/search_log.py` (`log_search(...)` / CLI `log`).

### Generic (parent) search vs sub-practice search — they are NOT the same (v1.1)
`suitability_family_id=""` = the **generic / practice-wide parent search** — one broad query over the
NbS and its synonyms (e.g. the stocktake's `("agroforestry" OR "agro-forestry" OR "trees on farms"
OR "tree-based system*" OR "agrosilvopastoral*" OR "silvopastoral*" …) AND climate AND spatial`).
A specific `family` = a **sub-practice-targeted search** with its own added terms (e.g. F1 adds
`"alley cropping" OR "tree intercropping"`). **The union of the per-sub-practice searches ≠ the
generic parent search** — different nets, different recall; you do not *sum* searches. Both are
logged as separate `SRCH` rows and reported separately. A family with no targeted row inherits
*nothing* automatically — it is shown as "covered by the generic net, not targeted" (the dashboard's
amber banner + the matrix dashed ring), never as "done".

### Search-term capture must be VERBATIM (v1.1)
`SRCH.search_terms` records the **exact query string actually run** — copied from the search
configuration / Annex / run script, never a from-memory paraphrase. (A paraphrase silently dropped
the climate block, all practice synonyms, and misfiled `silvopastoral` as a topic — caught
2026-06-29.) If the verbatim string lives in a file (`OpenAlex_run.R`, `search_string.xlsx`, a
stocktake Annex), transcribe it and cite that file in `SRCH.note`.

### Synonym policy (v1.1)
Practice-level (generic) searches use the **full synonym set** for the NbS (all spelling/term
variants OR'd in the practice block). Sub-practice searches keep the parent synonyms **and** add the
family's own vocabulary. Dropping synonyms narrows recall — default is to include them; any omission
is a logged decision.

## How it locks together (one source of truth, layered)
1. **`SRCH`** = the search *protocol* (this record).
2. **Progress ledger** (`progress_ledger.csv`) = the search *status* (`searched` not_started/in_progress/done) per (NbS × table × category × family). **`ledger.check` FAILS the build if `searched=done` has no matching `SRCH` row** — you cannot claim a search without its logged protocol.
3. **Discovery logs** (`methodology/discovery_logs/*.md`) = the narrative companion (PRISMA-lite prose).
4. **`EV.ruleset_version` / `SRCH.ruleset_version`** trace every datum back to the search + the exact instructions that found it.

## Version control of the instructions (reproducibility)
The search/extraction instructions are versioned: [`methodology/RULESET_VERSIONS.md`](RULESET_VERSIONS.md) (semver · date · change) + archived prompt snapshots under [`.agents/skills/_versions/<version>/`](../.agents/skills/_versions/). Bump + snapshot on any change to the screening funnel, defect catalogue, or discovery protocol. A past search is reproducible with the snapshot its `ruleset_version` points to.

### Learnings from the agroforestry synthesis-first round (2026-10-02)
- **Synthesis-first targeting** (Pete 2026-10-01) for T3/T6: meta-analyses · systematic reviews · EGMs · reviews first, then
  MEL / impact-assessment grey literature (ICR/IEG, SPIA/MELIA, 3ie, IFAD IOE, GEF IEO); PADs are ex-ante proposals, never evidence.
- **OpenAlex title search is accent-sensitive** (`agroforestería` 188 hits vs `agroforesteria` 21): run accented AND unaccented forms.
  French `haies` pulls English "hay" noise — qualify it. SciELO's own search and ifad.org bot-block tool fetches (reach SciELO items
  through OpenAlex DOIs; IFAD needs a human browser). Semantic Scholar rate-limits (HTTP 429) — do not rely on it for counts.
- **Web-summary numbers are not evidence**: two widely repeated agroforestry-drought figures could not be traced to any document.
- **Datasets** (ERA) are a format with no handling rule → PAUSE and define a dataset-intake adapter before registering.

## Status (v1.1, 2026-06-29)
The agroforestry `SRCH` rows are the **generic (practice-wide) parent search** at `family=""` — the
June sweeps were not sub-practice-targeted. Their `search_terms` were re-captured **verbatim** from
the stocktake Annex 1 (`reference/stocktake/_local/stocktake_review.txt`), replacing an earlier
paraphrase. **No sub-practice-targeted search (F1…F6) has been run yet** — those are logged per family
when run, and are NOT covered by the generic parent search. Synthesis #114 is gated on the
per-family searches being run + logged.

## Word documents (.docx) — handling rule (2026-10-05, Pete)

A `.docx` is a format the pipeline cannot verify quotes against directly (no stable pages). Rule:
1. **Master = the `.docx`**, uploaded unchanged to the SharePoint library beside its rendering.
2. **Artefact of record = a PDF rendered once** with LibreOffice headless (`soffice --headless --convert-to pdf`);
   record the renderer and version (e.g. `LibreOffice 26.2.4.2`) in `SRC.license`/`note` and the PDF's `artifact_sha1`.
   The rendered PDF is what `.cache/corpus/<source_id>.pdf` holds and what `library_path` points to.
3. **Locator = page of the rendered PDF** (`locator_type = page`), exactly as for a native PDF. Never re-render after
   extraction: a new render can re-flow pages and orphan every page locator. If the master changes, it is a new
   `source_id`.
4. **QA/QC** — `verify_metadata.py verify-titles` must pass on the rendered PDF (DOI-less); the verbatim guardrail runs
   as for any PDF. A published PDF of the same document, when one appears, supersedes the rendering (new SRC row,
   `superseded_by`).
First use: the Alliance working paper *Economic benefits and costs of NbS in LMICs* (Steward et al. 2023) —
`steward_2023_nbs_economics_wp`. Internal authorship is recorded for the independence axis.

### Datasets (.csv / .xlsx / R) — still PAUSED
The economics **meta-dataset** behind that paper (`nbs_data_p3.csv`, ~3,700 rows with the primary study's DOI and an
in-paper table locator per row) and **ERA** are *dataset* sources: no verbatim-page semantics, so no registration until
a dataset-intake adapter is defined (`source_kind = dataset`, snapshot + sha1, `locator_type = table_row`, quote = the
serialised row, `lineage_of` = the row's primary DOI). Until then a dataset is used only as a **discovery seed list**:
its DOIs enter the acquisition queue and the primaries are extracted from their own PDFs.

## OA-recovery — before marking a source `paywalled` (locked, 2026-08)

`blocker="paywalled"` must mean **verified no OA copy found**, NOT "OpenAlex `is_oa=false`" or "one fetch failed". Over-labelling dumps needless institutional-access work on the acquirer (Namita). Before queueing any source for institutional download, exhaust OA recovery:

1. **Unpaywall by DOI** — `https://api.unpaywall.org/v2/<doi>?email=p.steward@cgiar.org`. If `is_oa=true`, take `best_oa_location.url_for_pdf` → this is a **browser/repository** acquire, NOT institutional. (OpenAlex's OA flag lags/misses green OA; Unpaywall is authoritative.)
2. **Web-search each source (REQUIRED — the highest-yield step).** Query distinctive title + first author + year (+ "PDF"/"researchgate"). Accept a **free, directly-downloadable PDF of the SAME paper** (match title/author/year) on ResearchGate/Academia full-text, university/institutional repositories, **agency repos (USDA-ARS, HAL, CGSpace/CIFOR, WUR edepot, gov)**, project/author sites, publisher green/gold OA, SciELO, Semantic Scholar. Reject "Request-PDF" stubs, abstract pages, and different/related papers. *(Evidence: a recovery pass over the 227-source queue found 111 free — ~49% — of which only 23 were in Unpaywall; the other ~88 surfaced only by web-search.)*
3. **Green-OA / preprint / dataset** — check subject/institutional repositories, author postprints, preprints (bioRxiv, EarthArXiv, Research Square) and open **datasets** (Zenodo) even when the article body is closed.
4. **ResearchGate / Academia** — crawler-blocked, so a tool can never confirm/deny a copy. **Never claim "not on ResearchGate"**; instead flag it in the queue note as a **human-checks-RG-first** step.

Only what survives 1–3 is `access_route = institutional`. Anything with a found OA copy → `blocker=OA`, `access_route=browser/repository` + the URL. A helper OA-recovery sweep over the acquisition queue's DOIs is the standard pre-handover step.


## WOCAT technology sheets (handling rule, 2026-10-06)

**Format:** a WOCAT SLM Technologies entry is TWO artefacts under one `source_id` (`wocat_<id>_<year>`): the PDF
export (`.cache/corpus/<sid>.pdf`, SharePoint `library_path`, page locators — the T4 suitability units) and the
adapter transcript (`<sid>.md` rendered from the embedded questionnaire JSON `<sid>.source.json`, section locators —
the T3/T6 effect + asset-vulnerability units). **Acquire:** `python -m nbs_ruralscan.ingest.wocat acquire <sid>…`
(fetches `https://qcat.wocat.net/en/wocat/technologies/view/technologies_<id>/`, writes raw + transcript +
`.meta.json` with sha1s). **Locator semantics:** `locator_type = section`, `locator = <questionnaire_group>/<field>`
(e.g. `impacts_ecological_soil/soil_loss`, `climatological_disaster_coping/drought`); the quote is the transcript line.
**Extraction:** `python -m nbs_ruralscan.ingest.wocat emit --nbs <nbs_id> --out pipeline/staging/<file>.json <sid>…`
— rule-based from the two ratified lookups (`schema/lookups/wocat_impact_map.csv`, `wocat_hazard_map.csv`); the
family is the sheet's T4 family (modal `suitability_family_id` of its EV rows) and the NbS follows that family
through FAM, never the CLI argument (PICOS). **QA/QC:** render determinism + value→direction + coping→hazard are
unit-tested (`tests/test_wocat_adapter.py`); `emit` asserts every quote is a transcript line; the staging gate and
`validate_sources` verify section quotes against the `.md`. A re-acquire that changes the transcript changes the
sha1 in `.meta.json` — re-emit, never hand-edit.

**Costs (QT 4, added 2026-10-06).** The transcript gains a `## costs` section: the sheet's establishment and
maintenance totals (Σ cost per unit × quantity over the costed items, exactly as WOCAT's own export computes them),
placed on a USD-per-hectare or USD-per-structure basis from the sheet's stated calculation base (`area` with its
hectare size, `unit`, or — older sheets — every costed item per ha) and the sheet's **own** exchange rate (never a
cross-sheet price-year normalisation; ordinal economics, Pete 2026-10-05). Sheets with no basis or no rate print
`*_total_as_entered` and emit nothing. Units: `project_cost` (`usd_per_ha` · `usd_per_structure` · `usd_per_ha_yr` ·
`usd_per_structure_yr`) and `economic_return` ordinal units from the QT 4.7 benefits-vs-costs ratings
(`wocat_costbenefit` bands). The adapter's USD totals are cross-checked against the PDF export's printed
"Total costs … in USD" at ingest; a mismatch > 2 % is reported and not ingested.

