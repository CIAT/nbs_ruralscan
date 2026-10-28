---
name: source-command-discover-sources
description: Discover and screen additional literature, grey literature and code/project sources for an authorised NbS family and analytical table, producing auditable candidate files before acquisition and extraction.
metadata:
  ruleset_version: v1.8.1
---

# Bounded source discovery

Use for new searches or coverage-gap audits, not as a substitute for reading acquired sources.
Read `AGENTS.md`, `methodology/search_protocol.md` and the screening rubric in
`methodology/T4_generation_method.md` §3. Discovery ruleset: **v1.8.1**. Extraction remains
under its own current skill; never restamp existing records.

## Scope and coverage

Specify NbS, family, table and purpose before searching. Reconcile SRC, acquisition queue,
SRCH, progress ledger, discovery logs and stocktake inventory. Existing EV is not proof that
a search or paper is complete. Generic searches and family-targeted searches remain separate.
Run or explicitly account for four processes: `stock`, `updated_lit`, `grey`, `tool`.
T4 establishment suitability, restoration priority, species matching, observed distribution,
soft operational feasibility and T3/T6 effects are different lanes. Keep useful adjacent work
as a named referral, not a falsely tagged T4 source. Borderline inclusions stay review holds.

## Search and screen

- Stock: reconcile the original screened pool, titles, local artifacts and missed intake.
- Literature: reuse OpenAlex title-search machinery; Lens CLI is `scripts/discover-sources.py
  lens ... --tables T4` (requires LENS_TOKEN). For other tables set the actual tag explicitly.
  Use reviews and seminal methods as seeds, then primary studies for uncovered criteria.
- Grey: organization-neutral functional searches plus targeted repository checks; include
  agency manuals, practice databases and project evaluations. AGRIS is a manual browser lane;
  its CLI writes a template, not search results. Do not fabricate a completed channel.
- Tools/projects: search GitHub/GitLab, project and academic platforms. Inspect actual methods,
  scripts and parameter files before claiming rules exist. Pin repository identity/commit and
  file paths when available. A README, project name or demo dataset is not practice evidence.
  Code extraction later uses `nbs_ruralscan.ingest.github`, not hand-authored EV.
- Use English, Spanish, French and Portuguese variants appropriate to the practice. Record
  omitted language/channel coverage. Preserve parent practice synonyms plus family vocabulary;
  no extra climate block that accidentally excludes establishment-suitability methods.
- Follow references from strong seeds to original methods and later applications. Distinguish
  new independent studies from reused methods, reviews, translations and companion reports.
- Apply frame → source type → practice/system relevance → six-axis credibility → saturation.
  Assess strength, transparency, authority, transferability, recency and seminality, with an
  independence/COI discount. Proposed tiers need reasons; unknowns remain unknown.
- Bound the run explicitly. A cap or unavailable channel is not evidence of saturation. Report
  why work stopped and what remains. Record observed returned/screened records, not an engine's
  approximate hit total. Screening snippets identifies candidates, not verified source claims.

## Agent contract

When delegation is authorised, split literature/stocktake, grey and tools into independent
lanes. Each agent writes **only `pipeline/staging/`**, never registers, recipes or Git. It reads
this skill and receives explicit family/table/search limits. The orchestrator reconciles lane
outputs; an independent review checks omissions, weak exclusions, duplicates and role errors.
No source acquisition permission implies permission to contact authors or project maintainers.

For each NbS/family, produce:

1. `candidates.json`: list compatible with `scripts/register-discovery.py`. Required fields:
   `candidate_id`, `citation`, `url`, `process`, `tables`, `families`, `relevance_note`.
   Add language, method subtype, proposed tier+rationale, source lineage and existing-source
   IDs where known (`reuse_source_id` plus `reuse_reason` for canonical-source reuse). DOI candidates must be publisher/metadata-grounded; mark verification state.
   Never invent authors/year/DOI. Missing identity stays a hold outside registrar candidates.
2. `report.md`: exact query strings under `## Verbatim queries`, dates, channels actually used,
   screening decisions and exclusions, credible omissions, stop reason and next actions.
3. `protocols.json`: list of objects, one per actual table/process, containing `table`,
   `category`, `search_terms` (exact queries), `inclusion_criteria`, `limits`, `n_retrieved`,
   `n_screened`, `n_included`. Counts describe this bounded inspected set; unknown counts are
   null. Included count equals that table/process's candidate membership before queue dedupe.
   Keep zero-yield searches explicit. Do not combine stock reconciliation with fresh literature
   counts. Keep generic and targeted protocols in separate registration calls.
4. `screening.json`: inspected record identity/URL, include/exclude/hold/reuse disposition,
   reason and evidence of relevance. Count unique records consistently within each process.

## Central closeout

Validate candidate scope and metadata; dedupe DOI/title/report identity against SRC and queue.
Retain new-scope work for known sources through registrar reuse tracking, without duplicate votes.
Use the registrar with actual family, searched-by identity and explicit per-lane protocols;
pass `--reuse-log <new-run-name>.json` to retain canonical IDs and pending scope-review tasks.
Inspect its output before claiming stages. Zero-candidate lanes use explicit zero-yield protocols with the same registrar. Mark only actual work in the ledger.
Do not overwrite historical search rows, extraction status or review decisions.

Then verify DOI/title, acquire/cache team-accessible artifacts, and hand eligible sources to
`../source-command-extract-evidence/SKILL.md`. Pending acquisition is not extracted evidence;
no source discovered in this round silently changes suitability functions or approvals.
For a missing artifact, follow the full OA-recovery protocol before any paywall classification.
