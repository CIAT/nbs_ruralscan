# Grey discovery: forest_restoration

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `forest_restoration_t4_discovery_20261028_grey`, ruleset **v1.8.1**, actual family `forest_restoration__active_planting`. Registered by `scripts/register-discovery.py` on 2026-10-28: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `forest_restoration_t4_discovery_20261028_grey`, ledger per `--ledger`.


Date: 2026-10-28. Family: `forest_restoration__active_planting`. Table: T4. Ruleset v1.8.1.

Inspected bounded set: 27 unique records; five candidate memberships before central queue deduplication. These counts do not represent total engine hits or full-text reads. Each screening record states its actual inspection depth. Stop reason: candidate and screening cap, not saturation.

## Method and scope

Frame → source type → relevance → six-axis credibility → bounded stop. English, Spanish, French and Portuguese functional searches were combined with targeted agency/repository queries. Tool used: web search/page reader; large PDFs checked in memory with requests/PyMuPDF for opening metadata only. Four supporting identity inspections are retained alongside this report, not acquired artifacts. No EV, register, recipe, approval, or suitability curve changed.

Strength/transparency/authority/transferability/recency/seminality and independence discounts are recorded for each candidate. Medium tiers are proposals for guidance, not evidence of validation. Dates/authors follow opening pages or agency records; all DOI fields blank pending formal verification. New candidates still need central title/identity dedupe, acquisition to the team library, verified metadata, and full extraction inventory.

## Verbatim queries

- `(reforestation OR afforestation OR "forest restoration") planting site selection manual FAO ITTO`

- `restauración forestal reforestación plantación selección sitios manual FAO`

- `restauration forestière reboisement plantation choix site guide`

- `restauração florestal reflorestamento plantio seleção áreas manual`

- `site.cgspace.cgiar.org forest restoration planting site manual`

- `site.cifor-icraf.org restoration planting degraded land manual site`

- `site.itto.int guidelines forest landscape restoration site planting 2020`

- `site.qcat.wocat.net reforestation planting indigenous trees`

## Selected sources

- [Manual de restauración forestal y reconversión productiva](https://biblioteca.semarnat.gob.mx/janium/Documentos/Ciga/libros2018/CD004912.pdf): PDF 108 pages; site selection and eligibility pp9–10, restoration methods and planting. Programme canopy/eligibility screens are not universal ecological limits. Agroforestry/reconversion and soft operations need separate routing.

- [Recomendações técnicas e procedimentos gerais para a restauração florestal de paisagens no estado do Espírito Santo](https://www.cedagro.org.br/arquivos/PUBL_MANUAL_RESTAURA_FLORESTAL_mar22.pdf): PDF 48 pages; full-area planting section distinguishes low regeneration potential from natural regeneration/nucleation. Site-condition comparison table near printed43. Extract only active planting applicability; species recommendations remain separate.

- [A guide to planting native trees for forest restoration in watersheds](https://fiji.wcs.org/Portals/82/WCS%20Forestry%20Restoration%20Doc_English%20Final.pdf): PDF32 pages; site assessment around printed10–11 considers soil, land type, fire and invasive plants; subsequent species/spacing advice must not become whole-practice envelopes. DOI printed in source not emitted without round-trip verification. Bloomberg/Australian Government funding noted.

- [Restauración forestal](https://www.fao.org/sustainable-forest-management-toolbox/modules/forest-restoration/es): Full institutional module inspected: site-level assessment, natural regeneration versus planting, water limitation and objectives. Distinguish this from landscape-priority module and production plantations. Web snapshot with section locators required later.

- [Guidelines for forest landscape restoration in the tropics](https://www.itto.int/direct/topics/topics_pdf_download/topics_id=6511&no=1&disp=inline): PDF142 pages; restoration options and native-tree restoration examples, including Peruvian Amazon. Mixed FLR scope requires active-planting chapter partition. Existing acquired queue source; new targeted family scope, no duplicate source.

- **Scope hold outside registrar candidates:** [Restoration in Action Against Desertification](https://catalogue.unccd.int/1500_Restoration_in_%20Action_%20Against_%20Desertification.pdf): PDF92 pages; field preparation, planting/direct sowing and seasonal calendars. Conditional mixed-system candidate: restrict to explicitly forest/woodland restoration sites; do not infer tree planting on natural grasslands is forest restoration. Species and socioeconomic selection separate. DOI withheld pending verification.

## Coverage and holds

FAO/ITTO/CIFOR-ICRAF/CGSpace/WOCAT and World Bank/GEF channels were targeted where listed in the exact queries; not every repository returned a unique eligible record. CGSpace returned no selected direct record. Forest WOCAT query yielded no selected technology record; this is not proof of no relevant records. GEF-supported mangrove manuals surfaced through implementing institutions. AGRIS is a manual browser channel and was not run. Lens/OpenAlex belong the separate literature lane. Stocktake reconciliation and source-code inspection belong separate lanes. These omissions prevent a saturation claim.

Full screening reasons and useful deferred leads are in `screening.json`. A hold is not an exclusion for lack of relevance. No source is labelled paywalled. Failed/oversize fetches are access/identity holds. Translations, precursor manuals and reused underlying models must not generate independent evidence votes.

## Scope controls

Forest: active planting distinct from natural regeneration, agroforestry, production plantations and tree planting on natural nonforest habitat. Mangrove: planting distinct from hydrological/topographic restoration; datum, inundation frequency versus duration, and spatial support require explicit extraction. Species envelopes cannot set practice limits. Priority/benefit maps are M4 referrals; soft tenure/access/finance are operational/M6 referrals.

## Reconciliation

Existing queue reuse is explicit on ITTO2020 (`itto_flr_guidelines_ps24_2020`) for newly targeted active-planting scope; no duplicate source proposed. Existing GMA2023 translation is retained as reuse in mangrove screening, not an additional candidate, because its tidal-coastal scope was already examined. Other identities require final central queue/SRC cross-lane dedupe. Existing acquisition or EV presence never implies full extraction completion.

## Reproducibility files

Final candidates, screening decisions and exact protocol JSON are tracked beside this report under `methodology/discovery_logs/restoration_t4_20261028/grey/forest_restoration/`. Central metadata verification and scope screening precede registration; candidate counts are not evidence counts.
