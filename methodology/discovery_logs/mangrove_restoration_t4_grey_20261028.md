# Grey discovery: mangrove_restoration

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `mangrove_restoration_t4_discovery_20261028_grey`, ruleset **v1.8.1**, actual family `mangrove_restoration__tidal_coastal`. Registered by `scripts/register-discovery.py` on 2026-10-28: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `mangrove_restoration_t4_discovery_20261028_grey`, ledger per `--ledger`.


Date: 2026-10-28. Family: `mangrove_restoration__tidal_coastal`. Table: T4. Ruleset v1.8.1.

Inspected bounded set: 25 unique records; six candidate memberships before central queue deduplication. These counts do not represent total engine hits or full-text reads. Each screening record states its actual inspection depth. Stop reason: candidate and screening cap, not saturation.

## Method and scope

Frame → source type → relevance → six-axis credibility → bounded stop. English, Spanish, French and Portuguese functional searches were combined with targeted agency/repository queries. Tool used: web search/page reader; large PDFs checked in memory with requests/PyMuPDF for opening metadata only. Four supporting identity inspections are retained alongside this report, not acquired artifacts. No EV, register, recipe, approval, or suitability curve changed.

Strength/transparency/authority/transferability/recency/seminality and independence discounts are recorded for each candidate. Medium tiers are proposals for guidance, not evidence of validation. Dates/authors follow opening pages or agency records; all DOI fields blank pending formal verification. New candidates still need central title/identity dedupe, acquisition to the team library, verified metadata, and full extraction inventory.

## Verbatim queries

- `("mangrove restoration" OR "mangrove rehabilitation") (planting OR hydrological) site selection manual guidelines`

- `restauración manglares rehabilitación hidrológica selección sitios manual`

- `restauration mangrove reboisement choix sites hydrologie guide`

- `restauração manguezais plantio seleção áreas hidrologia manual`

- `site.fao.org mangrove rehabilitation site selection manual ITTO`

- `site.worldbank.org mangrove restoration technical guidance hydrology site selection`

- `site.thegef.org mangrove restoration site selection manual`

- `site.cgspace.cgiar.org mangrove restoration guide hydrology`

## Selected sources

- [Site Assessment Guidelines for Mangrove Rehabilitation in Bac Lieu Province, Vietnam](https://www.international-climate-initiative.com/legacy/Dokumente/2019/20190503_Site_Assessment_Manual-Final-Complete.pdf): PDF41 pages; visual/quantitative assessments; local elevation relative to MSL, observed monthly flooding and station transfer caveats. Local datum, seasonal support and frequency/duration distinction critical. Species suitability separate. Website2019 date is not PDF July2014 publication. Access MDB appendix is dataset-adapter hold.

- [Guidelines on Mangrove Ecosystem Restoration for the Western Indian Ocean Region](https://wedocs.unep.org/handle/20.500.11822/33253): PDF73 pages; biophysical assessment, failed planting contexts, restoration pathways and natural regeneration. Planting versus hydrological rehabilitation distinct; species detail separate. GEF-WIOSAP and regional guidance may reuse earlier methods.

- [Manual para la Restauración Ecológica de Manglares del Sistema Arrecifal Mesoamericano y el Gran Caribe](https://marfund.org/es/wp-content/uploads/2021/12/Manual-Restauracion-de-Manglar.pdf): PDF114 pages; forensic site assessment topography/hydrology/soil, printed33–42; hydrological rehabilitation47, topographic rehabilitation54, reforestation59 are separate methods. Source distinguishes water level, duration and frequency. Metadata confirmed from opening pages.

- [Guide méthodologique pour la restauration des mangroves](https://temeum.ofb.fr/sites/default/files/GUIDE-RESTAURATION-MANGROVES-FFEM.pdf): PDF71 spreads; printed pagination differs. Chapter4 passive/active approaches and reforestation, printed65–83; site scenarios around70–71. Hydrological/topographic restoration differentiated. Opening-page recommended citation confirms2024; English later edition is not independent.

- [Atlas dos Manguezais do Brasil](https://www.gov.br/icmbio/pt-br/centrais-de-conteudo/publicacoes/atlas-1/atlas_dos_manguezais_do_brasil.pdf): PDF179 pages; restoration chapter around100–102 discusses local reference hydrology/topography and ecological restoration. Atlas distribution/protection/benefits chapters are not establishment thresholds.

- [National Guidelines for the Restoration of Mangrove Ecosystems of Sri Lanka](https://env.gov.lk/web/images/downloads/biodiversity_division/publications/National_Guidelines_for_the_Restoration_of_Mangrove_Ecosystems_of_Sri_Lanka.pdf): PDF194 pages; institutional description and indexed substantive sections identify restoration site conditions and planting guidance. Opening pages confirm title/year/publisher. Acquisition pass must inventory full methods; separate species-based recommendations from tidal-coastal practice conditions.

## Coverage and holds

FAO/ITTO/CIFOR-ICRAF/CGSpace/WOCAT and World Bank/GEF channels were targeted where listed in the exact queries; not every repository returned a unique eligible record. CGSpace returned no selected direct record. Forest WOCAT query yielded no selected technology record; this is not proof of no relevant records. GEF-supported mangrove manuals surfaced through implementing institutions. AGRIS is a manual browser channel and was not run. Lens/OpenAlex belong the separate literature lane. Stocktake reconciliation and source-code inspection belong separate lanes. These omissions prevent a saturation claim.

Full screening reasons and useful deferred leads are in `screening.json`. A hold is not an exclusion for lack of relevance. No source is labelled paywalled. Failed/oversize fetches are access/identity holds. Translations, precursor manuals and reused underlying models must not generate independent evidence votes.

## Scope controls

Forest: active planting distinct from natural regeneration, agroforestry, production plantations and tree planting on natural nonforest habitat. Mangrove: planting distinct from hydrological/topographic restoration; datum, inundation frequency versus duration, and spatial support require explicit extraction. Species envelopes cannot set practice limits. Priority/benefit maps are M4 referrals; soft tenure/access/finance are operational/M6 referrals.

## Reconciliation

Existing queue reuse is explicit on ITTO2020 (`itto_flr_guidelines_ps24_2020`) for newly targeted active-planting scope; no duplicate source proposed. Existing GMA2023 translation is retained as reuse in mangrove screening, not an additional candidate, because its tidal-coastal scope was already examined. Other identities require final central queue/SRC cross-lane dedupe. Existing acquisition or EV presence never implies full extraction completion.

## Reproducibility files

Final candidates, screening decisions and exact protocol JSON are tracked beside this report under `methodology/discovery_logs/restoration_t4_20261028/grey/mangrove_restoration/`. Central metadata verification and scope screening precede registration; candidate counts are not evidence counts.
