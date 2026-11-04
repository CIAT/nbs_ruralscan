# Bounded water-harvesting priority stocktake audit

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `wh_high_stocktake_20261104_stock`, ruleset **v1.8.1**, actual family `generic`. Registered by `scripts/register-discovery.py` on 2026-11-04: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `wh_high_stocktake_20261104_stock`, ledger per `--ledger`.


Date: 2026-11-04. Ruleset v1.8.1. Baseline fdad1d2. Parent water_harvesting_conservation; T4; generic reconciliation, not completed per-family searches.

## Verbatim queries

`NbS_Practice == 'Water harvesting and conservation' and Final_Benchmark == 'High' in reference/stocktake/peer_reviewed_benchmarked.csv`

Fixed set: 11 retrieved, 11 primary-text screened, seven retained before dedupe (five new, two canonical reuse), two held, two referred. Reconciliation: DOI equality or title-token overlap >0.85 against SRC and queue; not exhaustive alias matching. Crossref title/DOI and opening-PDF title checks passed for all 11. Shared paths/hashes retained.

Funnel: bounded T4 runoff-catchment frame excluding rooftop; journal-PDF source type; explicit placement relevance with storage/recharge and demand/engineering distinctions; six-axis credibility in README; stop at fixed High-tier cap, not saturation. Remaining 52 Medium and 22 Low records not screened.

Native renders checked: Adham p4, Alene p5, Jha p7, Singh p6, Vema p4, Zheng p4. Manifest lists targeted pages read; no exhaustive page, supplement or citation-chain extraction claimed. Criteria inventory and ten existing EV review referrals accompany screening decisions. Existing analytical rules and decisions unchanged. Tool channel logged separately; updated_lit and grey not run.
