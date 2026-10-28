---
name: "source-command-extract-evidence"
description: "Extract and verify source-provenanced evidence for an authorised T4 suitability, T3/T6 effect, or operational-risk lane."
version: "v1.7.0"
---

# Evidence extraction

Current ruleset: **v1.7.0**. Stamp new units with the version actually used; never restamp
historical evidence. Version log: `methodology/RULESET_VERSIONS.md`. This skill is the
canonical extraction instruction; `.claude/commands/extract-evidence.md` delegates here.

## Establish scope

Use the user's authorised NbS, families, sources and live roles. Do not expand into a new
search or full corpus sweep without task scope. Read `AGENTS.md`, the source register and
relevant methodology before extracting:

| Claim | Evidence role | Contract / consumer |
|---|---|---|
| Establishment suitability, host system, hard exclusion | `structural_suitability` | T4; `../extraction_contracts/T4_review_contract.md` |
| NbS changes an outcome | `nbs_effect` | `../extraction_contracts/T3_T6_extraction_contract.md`; XW routes to T3/T6/T6E |
| Hazard damages the NbS asset | `asset_vulnerability` | Same effect contract; T3 asset threat / M2b A |
| Soft access, tenure, finance, labour or other enabling factor | `operational_risk` | M2b B / M6; separate from core suitability |

T3/T6 were reactivated on 2026-09-30: the September blanket deferral is obsolete.
The 2026-10-12 T4 pause applies within effect lanes unless explicitly authorised otherwise.
Legacy `climate_risk`/`priority_need` roles are not substitutes for current effect claims.
Dataset intake remains paused without an approved adapter; a discovery seed is not evidence.

Read [defect catalogue](references/defects.md) and the applicable contract. For effects,
also read `../extraction_contracts/DIRECTION_ADDENDUM.md`. T4 suitability direction and
change in an outcome variable are different meanings; do not interchange their vocabularies.

## Source and coverage checks

1. Resolve canonical variable and aliases from VONT and practice applicability from FAM.
   A generic agroforestry source stays cross-family unless its system is established by the
   paper or a separately recorded synthesis decision; never default it to planted silvoarable.
2. Confirm the team's source is available: PDF library path and cache, or registered URL and
   snapshot/code adapter. Require verified DOI, or no DOI plus verified title. Check identity
   against the acquired artifact; a resolvable DOI alone cannot establish PDF identity.
3. Inventory relevant pages, tables, continuations, figures and supplements. Record each claim's
   disposition and EV IDs or explicit hold/exclusion. Check existing units for missing variable
   use, direction, values, classes and weights. `already_extracted()` returns record IDs, not a
   completeness verdict. Species/crop-specific evidence is retained in its own scope.
4. Build or refresh the deterministic index (`python -m nbs_ruralscan.ingest.build <pdf_dir>`).
   This checks artifact hash and table capability. Retrieve page-stamped passages using
   `package_for_extraction_multi`; inspect the source table and its continuation, not only
   search hits. Flag OCR/image-only blockers with exact locators. Never infer an absent row.

## Extract and validate

- One atomic claim per `EvidenceUnit`; preserve original names, units, class labels and scope.
- Slice verbatim quotes from the source. Include readable caption/header/row context with
  anchored supporting excerpts. No stitched quotes, invented cutoffs or cross-paper inference.
- Separate variable use, direction, numeric calibration and importance. Weight-only extraction
  is incomplete if the same table also reports direction or classes. Do not turn raw map
  extrema, site observations, source rank scores or importance weights into suitability curves.
- Preserve cited-primary attribution and lineage. Count independent studies, not duplicate
  records, depth branches or repository copies. Keep source importance separate from runtime
  MCDA weights; record enough of the original criterion set to explain relative importance.
- Validate `EvidenceUnit` objects with `validate_units`, then save staging only. New extraction
  never grants `reviewer_ok` or overwrites a reviewed record. A changed existing ID requires an
  audited correction. Retain ambiguities and source conflicts visibly; do not manufacture agreement.
- Orchestrator runs `scripts/ingest-effects-staging.py ... --dry-run` for supported page/section
  units, with explicit `--allow-structural` / `--allow-operational` when authorised. Code locators
  use their dedicated adapter and central source verifier; unsupported formats stay blocked.
  Repeat without `--dry-run` only after all gates pass. XW-unmapped outcomes remain catalogued
  and visibly unmapped; they must not be silently renamed to force a consumer.

## Close the work

Run central provenance, number, context, scope, species, direction, coverage and schema checks.
Adversarial review checks omissions as well as incorrect additions. Quote matching cannot prove
semantic fidelity. Report sources read, claims accounted for, pending holds, new units and tests.

Run `methodology/extraction_retrospective.md` after a sweep. Advance learning/progress records
only for work actually completed. Human review and synthesis approval remain separate from
extraction. No new sweep is implied by a ruleset maintenance task.
