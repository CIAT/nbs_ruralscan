# Discovery and ingestion pipeline audit — 28 October 2026

This maintenance pass audited discovery registration → acquisition → source promotion →
indexing → staged evidence ingestion → review learning and coverage checks. It fixes code
and instruction defects; it is not a new literature search, extraction sweep, reapproval
of the corpus, or pilot run. Baseline: `12da134` on `main`.

The evidence corpus remains the source of truth. No SRC/EV CSV, human decision, pending
review store, generated analytical table or developer package was rewritten. Four existing
follow-up checks were narrowed to their original answer-supporting context keys after a
Git-history comparison proved that only unrelated soil-input annotations had been added.
Their answers and human decisions are unchanged.

## Findings fixed

| Stage | Failure found | Change and regression coverage |
|---|---|---|
| Discovery deduplication | First 70 characters of citation used as identity; long shared author/title prefixes and non-Latin titles could collapse distinct sources. | Compare complete Unicode-normalised citations; DOI matching remains separate. This is conservative deduplication, not bibliographic identity verification. |
| Discovery accounting | Registrar read `table_list` rather than input `tables`, fabricated default ruleset, truncated query text, and counted only newly queued candidates. | Exact table tags, explicit actual ruleset, full query sections, actual search date, counts before queue deduplication; ledger marks only process/table pairs searched. Reject malformed payloads/missing reports before writing. Zero-yield searches use explicit `search_log.log_search` with table/process rather than guessed metadata. |
| Search history | Different runs on the same day overwrote the same SRCH ID. | Run-specific IDs; rerunning the same run/date remains idempotent. Existing IDs are preserved. |
| OA recovery | Registrar promoted an agent's `paywalled` label into a claim of completed Unpaywall plus web-search verification. | Label becomes an OA-recovery hold; no claim of exhaustive search or automatic institutional referral. DOI-based recovery requires a verified DOI. |
| Acquisition | Empty/corrupt caches and mismatched URLs/pins were reused; HTML served with PDF MIME could be saved; retries deleted previous artifacts. | Validate filename-safe IDs, body signature and cache metadata/hash; failed retries preserve previous files; PDF parser validates queue downloads before promotion. Individual writes are atomic. |
| Human downloads | A wanted title anywhere inside another PDF could pass as source identity, including a bibliography entry. Existing cache/library files could be overwritten. | Body-only matches require chapter/reference disambiguation; different existing files are preserved; missing team-library destination remains an intake hold. Opening-page title matching is still a heuristic, not proof of semantic identity. |
| Code sources | A branch name could be recorded as an immutable pin; same owner/file stem could overwrite another repository/path/revision. | Resolve full commit first, use distinct default IDs per repository/path/commit, and refuse conflicting explicit-ID replacement. |
| Source promotion | Acquisition marked a source `swept`, filled extraction metadata, assumed OA/empirical/medium credibility, and silently blanked an unverified DOI. | Promotion starts `pending`; identity/library checks and assessed credibility metadata are required. Preserve known access status and DOI; refuse unverified identity. Validate the batch before appending. |
| PDF indexing | “Process once” still parsed every PDF; a prior no-tables cache could discard a newly built table index. Lossy cache slugs could collide. | Check content hash before parsing; retain table-capability metadata and rebuild legacy/insufficient caches; disambiguate lossy IDs, reject malformed/wrong-source indexes, atomic cache writes. |
| Staging gates | Page zero selected the last PDF page; empty quotes, unregistered/unverified sources, wrong-family NbS assignments and extraction-granted approval could escape basic checks. | Reuse EvidenceUnit validation; require positive integer pages, source identity, artifact hash, family/NbS agreement and explicit role opt-in. Reject unsupported locators rather than treating them as PDF pages. Close cached PDF handles. |
| Idempotency | Changed evidence under an existing ID was silently skipped. | Validate duplicate IDs and compare submitted content before any append, including dry runs. Exact reruns preserve existing review state; corrections need an audited route. |
| Learning loop | Re-reviewing an existing pair never increased the cursor count; an old maximum count defeated a later correction. | Content fingerprints detect changed decisions/reasons/notes; unchanged repeated applies do not inflate learning work. Last cursor wins. Off-scope drop rate uses drops in numerator and denominator. Legacy counts remain explicitly estimates. |
| Review follow-ups | Whole-context hashes reopened answered weight questions when independent soil-method notes were added. | Optional explicit JSON-key checks protect the original answer-supporting content. Changed weights or missing keys still fail. Historical whole-field digests retained. |
| Instructions | Live skill/command still forbade T3/T6; header said v1.6.16 despite later addenda; closest-proxy and shape-only advice contradicted retained directions/classes. | Canonical v1.7.0 skill, detailed reference catalogue, active effect contract and direction addendum; command delegates to skill. Update AGENTS, retrospective and recipe scaffold instructions. Full new instruction snapshot; old snapshots untouched. |
| Test housekeeping | Existing developer-view escaping test injected text into an obsolete field. | Exercise the rendered readiness explanation instead; still verifies escaping and collapsed comparisons. No view behavior changed. |

## Learnings applied from this session

The audit read the latest 30 dated human-review comments in the 20–28 October subset,
plus the recurring issues and accepted decisions in this session. These repeatedly concern
missing table context, unexplained source weights, over-fragmented soil branches, wrong
practice, and secondary findings attributed to the citing paper.

The current contract now explicitly requires:

- Separate variable use, direction, reported classes/values and numeric calibration. A
  weight-only record does not cover a table that also reports suitability direction.
- Inventory complete tables, continuations, figures and supplements; retain missing claims
  as visible holds. Existing EV IDs never establish source completeness.
- Retain source weights, method, parent criterion set, depth/branch, scale and provenance.
  Show multiplication and denominator for derived importance. Relative-to-equal-share
  comparisons require a complete comparable criterion set. Runtime weights remain separate.
- Preserve categorical host classes, scope and source labels. Do not coerce proxies into
  similar variables or invent numerical functions from qualitative direction/map extrema.
- Keep site observations out of suitability calibration; preserve them as context.
- Preserve cited-primary attribution and independent-study counting. A practice mimic or a
  marginal component of a bundled programme does not establish practice evidence.
- Keep unanswered source uncertainty visible; do not require a second answer-approval
  system or silently mark historical human review as superseded.

No claim is made that all historic feedback has been processed. The learning cursor was
**not advanced**: 2,011 distinct reviewer–record pairs versus 961 at the last recorded
retrospective leaves a **1,050-pair legacy count estimate**. This includes agent entries,
not 1,050 new tasks for Pete. Content-level accounting starts at the next fully documented
retrospective; a count alone cannot reconstruct which amended historic notes were read.

## Current register reconciliation

Read-only audit covers **765 acquisition rows, 537 sources and 5,195 evidence rows**.
[Full findings, by source ID](../../pipeline/audits/discovery_ingestion_2026-10-28/register_findings.json).

| Finding | Count | Next action |
|---|---:|---|
| Missing acquisition-queue identity record | 49 sources | Reconcile legacy registrations with their original acquisition and verification artifacts before fresh extraction. Absence of the newer queue record does not prove the original source was wrong. |
| DOI-bearing source lacks current verified flag | 3 sources | Verify `vaast2016_double_dividend`, `cifor_wp270_peatland_restoration_monitoring_management`, `hemes_2018_restored_wetland_surface_cooling_delta` against their acquired documents. No new identity approval inferred here. |
| Acquired but not registered | 120 sources | Triage scope, identity, library access and credibility before promotion. This is a backlog, not proof of missed extraction. |
| `swept`/`signed_off` with no EV | 6 sources | Locate their claim inventories; a documented zero-yield sweep is legitimate. Do not infer either success or failure from row count. |
| Duplicate IDs / evidence with missing SRC / missing PDF library path | 0 | Continue checking on future runs. |

Three apparent citation mismatches were checked: Ahmad 2020, Chuma 2021 and Haile 2024
have identical DOI/title but abbreviated author lists in the queue. Comparison now ignores
that harmless formatting difference; they are not added to the review backlog.

## Verification and limits

Regression tests use local synthetic PDFs, temporary registers and mocked network responses.
They cover happy paths and failed writes; no real download/search or production ingestion was
performed. Validation: **800 tests passed** in the full-suite run; a final 80-test pipeline run
(including two added regression cases) also passed. Lint/format and changed-module plus CI-core typing
passed, schema sync reported zero stale JSON, structure reported zero errors, and T4
coverage reported zero errors. PyMuPDF emitted five deprecation warnings in the test suite.

Untouched baseline reproduced three failing tests: one stale developer-view fixture and two
T4 recovery tests affected by four context digests. Git commit
`790029f760262a08f0b974681bdbe9c30f3686c4` reproduces each old digest; the only later addition
is `soil_input_review`. The maintenance change protects all original context keys rather
than accepting changed answers or weakening weight checks.

The schema generator verifies 3,861 quotes against 530 cached sources and reports no stale
JSON. It also reports advisory flags: five scope signals, 489 narrow quotes, 90 whole-page/
whole-table quotes, 47 magnitude-band disagreements and nine unmapped effect-variable flags.
These categories are not necessarily disjoint, and advisory flags are not confirmed defects.
Structure validation has zero errors but 3,443 warnings across CSV/JSON surfaces; these are
not 3,443 independent new records. Treat them as a separate schema/content triage backlog.

Repository-wide `ty check` also fails on untouched baseline outside this patch; targeted
checks include the changed modules plus CI's core modules. This pass does not rewrite
unrelated analytical code to silence that backlog.

Remaining architectural limits:

1. Register updates across queue, SRCH, ledger, EV and SRC are not one database transaction.
   Preflight catches deterministic batch errors before writes, but disk/process failure can
   still require recovery. Multi-writer locking/transactional storage is future work.
2. This staged-ingestion command verifies page and section artifacts. Code/other locators
   need their dedicated adapters and central verifier. PDF header checks cannot prove identity;
   text gates cannot validate image-only table cells or detect every omitted claim.
3. Historical ruleset versions v1.6.0/v1.6.14 collide and v1.6.17 was an addendum. Preserve
   producing Git commit and lane report alongside those stamps; do not rewrite history.
4. The dashboard's older discovery coverage panel remains T4-focused although QA/QC supports
   effect evidence. It is not a complete T3/T6 discovery inventory; SRCH and ledger remain
   authoritative. No new dashboard was created in this pass.
5. No blanket source corrections, new human-review queue or new full sweep was launched.
   The generated developer bundle and Diego/Brayden's implementation boundary are unchanged.

## Repeatable maintenance commands

From an environment with project dependencies installed:

```bash
PYTHONPATH=src python -m nbs_ruralscan.schema_tools.ingestion_audit --json
PYTHONPATH=src python -m nbs_ruralscan.schema_tools.learnings status
PYTHONPATH=src python scripts/ingest-effects-staging.py <staging.json> --dry-run
python -m pytest -q
ruff check .
ruff format --check .
python src/nbs_ruralscan/schema_tools/generate.py schema --check
python src/nbs_ruralscan/schema_tools/structure.py schema
PYTHONPATH=src python -m nbs_ruralscan.schema_tools.t4_coverage
```

Use `--allow-structural` / `--allow-operational` only for authorised lanes. Source promotion
now requires explicit credibility metadata. `register-discovery.py` requires actual
`--ruleset`, reports and tracked log filenames; use the CLI help rather than older examples
that relied on inferred defaults. `learnings.record` is not part of a read-only audit.
