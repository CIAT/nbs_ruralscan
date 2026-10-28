# Forest planting and mangrove T4 discovery — 28 October 2026

Three agents ran separate literature/stocktake, grey-literature and tools/project lanes,
followed by cross-lane review and central registration under discovery ruleset v1.8.1.
This is a bounded discovery round, not an extraction sweep or a saturation claim.

| Target family | Recorded screening decisions across lanes | Candidate memberships | New acquisition rows | Canonical-source reuse tasks |
|---|---:|---:|---:|---:|
| Forest active planting | 83 | 14 | 13 | 1 |
| Mangrove tidal/coastal | 79 | 16 | 16 | 0 |

Screening totals sum lane records; they are not globally deduplicated search-engine
returns or full-text reads. Literature screened 26 records per family; grey screened
27 forest/25 mangrove; tools screened 30 forest/28 mangrove. Eight SRCH rows record
stock, updated_lit, grey and tool separately for each exact family. Unknown returned
totals remain blank. Grey returned totals describe only the inventoried bounded set.

All 11 candidate literature DOIs passed `schema_tools.verify_metadata.verify()` on an
isolated discovery-only queue slice, with authoritative Crossref citation rebuilding.
The saved metadata audit records the result. Only those new queue rows received stamps;
all pre-existing acquisition rows remain unchanged. DOI-less candidates still require
artifact/title verification during acquisition. The existing ITTO 2020 manual has a
separate pending scope-review task in `../forest_restoration_t4_reuse_20261028.json`;
its acquired status and source identity were preserved.

## Useful leads and controls

- Forest: CONAFOR, CEDAGRO and WCS Fiji field manuals; planting and enrichment studies;
  ProGreen application configuration and transparent reforestation code. Broad landscape
  allocation studies, species models and policy masks remain scope-review candidates.
- Mangrove: Bac Lieu site assessment, WIO, Sri Lanka, MAR/Caribbean, FFEM and Brazilian
  guidance; hydrological classification/flow-path studies; Mini-Buoy, LEAF, DFMFON and
  MangroveVulnerabilityModel code. Preserve tidal datum, time denominator, species,
  establishment stage, geographic calibration and paper/code lineage.
- Afforestation-Tracker has conflicting point/raster logic and native-nonforest eligibility
  questions. It is queued for method audit only; no thresholds or habitat masks approved.
- Nigeria soil tool moved from the agent shortlist to hold because inspected code did not
  establish mangrove application. DFMFON's explicit example species are preserved.
- Species models, priority maps, soft operational factors and mixed dryland restoration
  remain named referrals/holds. Discovery inclusion is not practice-level T4 eligibility.

## Reproducibility and remaining coverage

Each lane/family directory contains final candidates, screening decisions, protocols
and its source report. Registrar-produced narrative copies are linked directly from
SRCH. Supporting Crossref/OpenAlex responses and grey opening-page identity inspections
are retained in the lane directories. Code candidates carry full commits and file URLs;
local code snapshots were screening caches, not acquired evidence artifacts.

Search used EN/ES/FR/PT web queries, local stocktake reconciliation, OpenAlex title
search, citation follow-up and GitHub/code inspection. Lens was unavailable without
its token; AGRIS manual search and GitLab remain unrun. A Portuguese mangrove GitHub
query was rate-limited. Caps stopped the round; they do not demonstrate saturation.

The current family-level searched/screened stages are `in_progress` for this unfinished
coverage pass, including reopening forest discovery for the new round. Historical SRCH
rows remain unchanged. Existing extracted/reviewed states and EV/SRC/T4 content were
not modified. Pending sources now need acquisition, artifact identity checks and
source-complete scope/lineage review before extraction. The 29 pending acquisition
rows are unassigned; no work was silently assigned to another team member.

Independent review checked lane counts, known identities and code claims. Registrar
review found and fixed citation-format deduplication and changed-protocol overwrite
risks, with regression coverage. No human approval or scientific validation is implied.
