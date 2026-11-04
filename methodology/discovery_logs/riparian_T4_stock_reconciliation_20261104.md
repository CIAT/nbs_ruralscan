# Riparian T4 stock reconciliation — 2026-11-04

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `riparian_stock_reconciliation_20261104_stock`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-04: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `riparian_stock_reconciliation_20261104_stock`, ledger per `--ledger`.


Discovery skill v1.8.1. Generic parent practice `riparian_buffer`; fixed original stocktake set. All PDFs already team-accessible. Five candidates are for placement-context review, not universal thresholds. See README, screening, criteria and manifest for decisions, source pages and limitations.

## Verbatim queries

Stock inventory:
`NbS_Practice == 'Riparian buffers' in reference/stocktake/peer_reviewed_benchmarked.csv`

Identity lookup for the DOI-less stock record (not a separate grey discovery lane):
`site.fs.usda.gov "Where should buffers go" Bentrup Kellerman`

## Channels and counts

Stock: 11 returned, 11 screened, 5 included. Five referrals and one scope hold retained. Four DOI-bearing included records use Crossref canonical citations; Bentrup uses native title plus USDA record. Ten DOI-bearing identities across the entire fixed set checked; Li's matching English title is on p. 9. Dedupe against SRC and acquisition queue used exact DOI and title-token overlap >0.85; no matches, with manual cross-check of riparian SRC citations. Not an exhaustive alias/entity-resolution claim.

Updated literature: not run. Grey: not run; USDA lookup verifies an existing stock record, not an extra source. Tool companion audit has its own report and protocol; do not sum it into stock counts. No new multilingual search; English texts reviewed except Li, for which only the English abstract is assessed. Chinese methods and all supplements remain outside this pass.

## Stop and next actions

Fixed eleven-paper cap reached. Register five sources for later bounded source intake/placement review. Retain general planning, floodplain and project-proposal referrals without mis-tagging them as buffer suitability. No saturation, extraction, verification-completion or human-review-completion claim. Historical family ledger rows remain unchanged.
