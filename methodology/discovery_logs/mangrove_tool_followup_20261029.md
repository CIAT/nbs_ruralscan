# Mangrove tool lead follow-up — 29 October 2026

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `mangrove_tool_followup_20261029_tool`, ruleset **v1.8.1**, actual family `mangrove_restoration__tidal_coastal`. Registered by `scripts/register-discovery.py` on 2026-10-29: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `mangrove_tool_followup_20261029_tool`, ledger per `--ledger`.


Discovery ruleset v1.8.1; mangrove_restoration / mangrove_restoration__tidal_coastal / T4 / tool. Five guide references and two code companions screened. Three method sources included for acquisition review; four project/code records retained as referrals or holds. Search-engine totals unknown; no saturation claim. Stock, updated_lit and grey lanes were not rerun.

## Verbatim queries
- "Global Mangrove Watch" github code
- "Validation and application" "individual based restoration model" mangrove
- "Mangrove restoration potential" github Worthington Spalding
- "mangrove coasts under threat" Deltares model
- "Developing performance measures" "mangrove" Twilley 2005 model
- "Worthington" "2018" "restoration" "github"
- "FORMAN" mangrove model code GitHub
- "Validación y aplicación" "55360"
- "Mangrove restoration potential" "2018" Worthington Spalding map
- "FORMAN" "mangrove" "github.com"
- "Validación y aplicación" site:revistas.unal.edu.co 55360

## Channels and limits

Web search in English and Spanish; primary publisher, institutional, project and GitHub pages. Public GitHub API used for commits, tree listings and selected files after connected repository search for globalmangrovewatch/gmw_planetary_computer_s2_alerts returned no match. No GitLab, French/Portuguese, OpenAlex, Lens or AGRIS searches. Incidental results were not counted as screened candidates. Seven selected records, not approximate engine hits, define the screening denominator.

## Decisions

FORMAN: publisher abstract describes species-specific calibration against monitoring; code availability remains unresolved. Twilley/Rivera-Monroy: institutional record identifies simulation/performance methods; direct access returned 403, not evidence of a paywall. Worthington/Spalding: primary report establishes an expert-derived restoration method; original scoring implementation remains unverified. Full acquisition, title/DOI checks and applicability review precede extraction.

GMW alerts code is Apache-2.0 and tied to a public analysis paper. Inspected notebook loads Sentinel-2 via STAC, applies existing-extent masks and calculates NDVI. This verifies code availability and purpose, not reproduced validation or T4 thresholds. GMW Atlas is MIT-licensed (root and inspected data subdirectory); inspected notebooks read OVERALL_SRE and multiply for display. They do not establish the original score derivation. Software licences do not automatically licence upstream datasets. No notebook was executed and no credentials or upstream data were fetched.

Deltares project page links Delft3D FM and coastal engineering publications. It does not establish a project-specific, reusable mangrove suitability codebase. Keep M6 referral. The later Global Coastal Wetlands Lab restoration entry is a successor lead; do not conflate it with the 2018 report. Incidental soil-carbon and conservation-priority repositories were outside this bounded inspection.

## Credibility and lineage

Strength: FORMAN reports calibration; transfer beyond its taxa/sites unverified. Other included methods require full validation review. Transparency: papers/report accessible or located, original model code unresolved. Authority: journal/institutional primary records. Context: Colombian mangroves, Florida modelling and global historical restoration potential differ. Recency: historical methods retained for lineage, not presumed current. Seminality: no citation-count claim. Independence: guide citations and companion platform code are not independent evidence votes; institutional advocacy warrants caution. Proposed tiers medium pending full review.

## Stop and next actions

Stopped after resolving identities and code availability for the bounded seed set. Acquire three method sources with team access, verify identities, then inspect model variables, relationships and scope. Public code referrals require their own adapter and immutable locators before any EV admission. Dataset ingestion remains paused. No source is labelled paywalled, no author contacted, no suitability rule or human approval changed.

## Primary links

- FORMAN: https://revistas.unal.edu.co/index.php/cal/article/view/55360
- Twilley/Rivera-Monroy: https://digitalcommons.fiu.edu/record/15154
- Restoration method: https://oceanwealth.org/wp-content/uploads/2019/02/MANGROVE-TNC-REPORT-FINAL.31.10.LOWSINGLES.pdf
- GMW validation/code linkage: https://www.mdpi.com/2072-4292/15/8/2050
- Deltares: https://www.deltares.nl/en/expertise/projects/mangrove-coasts-under-threat
- Successor-data lead: https://www.globalcoastalwetlands.com/data

Exact commits, selected file hashes and notebook-cell inspection are in repository_checks.json. This is discovery inspection, not registered code evidence.
