# Bac Lieu mangrove site-assessment review — 28 October 2026

## Result and scope

Reviewed Clough (2014), *Site Assessment Guidelines for Mangrove Rehabilitation in Bac Lieu Province, Vietnam*: all 41 PDF pages, including the annexes. Pages 2 and 4 are blank. The tracked inventory accounts for the conceptual diagram, monthly flooding table, drainage diagrams, all 12 species-chart rows, both checklist tables and the database documentation. Relevant graphical claim surfaces on PDF pages 6, 12, 18, 23, 24, 26 and 27 were rendered and inspected. Equipment photographs and software screenshots were not digitised into evidence.

One unapproved structural-suitability unit was admitted for `mangrove_restoration__tidal_coastal`: `ev_mr_elevation_clough14_20261028`. It retains **local non-monotonic elevation guidance**, not an executable response. Source elevation is centimetres above local mean sea level. The green-to-red graphical key establishes direction; its continuous colour transitions do not establish exact optimum endpoints or response scores. “May be unsuitable” above 200 cm and below MSL is not a hard exclusion. This is a mangrove-rehabilitation interpretation, not permission to plant naturally unvegetated intertidal habitats.

Counts: one source-specific variable-use record; one directional record; zero calibrated functions; zero human approvals. No operational-risk claim was admitted from instructions about equipment, monitoring or community awareness. The source remains `in_progress`; acquisition-queue `extracted` denotes partial extraction only. No recipe was changed. This completes a bounded main-paper accounting pass, not the full extraction of held claims or corpus.

## What remains held

- All 60 monthly cells, five elevation columns and lower-band-endpoint convention are retained in `flooding_table.json`. Days flooded per month cannot be converted into percent time flooded without event duration. Local terrain elevation is a tidal proxy with an explicit datum; it must not be transferred as a global DEM cutoff.
- All 12 species-chart rows remain in `species_salinity_inventory.json`. The plotted endpoints are approximate visual readings, not printed numbers. Salinity in parts per thousand is not electrical conductivity. Species-specific local distributions cannot become a practice-wide envelope; no matching canonical salinity variable was found.
- Compaction, surface/subsurface drainage, soil composition, moisture, propagule transport, coastal stability and water-table observations have explicit destinations in `page_claim_inventory.json`. Generic texture is not a USDA/HSG class; snapshot water depth is not mean-lowest groundwater depth. No omitted direction was silently treated as evidence of no relationship.
- Sesuvium's pH statement concerns an indicator plant. It is not a mangrove pH threshold. Species root sensitivity, surface heating, sampling depths and gauge dimensions likewise do not become general establishment bounds.
- Tidebase `.mdb` and associated spreadsheets are documented followups only. They were neither acquired nor run: no dataset-intake adapter exists. Clough (2013), Giesen et al. (2007), and English et al. (1997) remain cited-primary followups; their claims are not counted as new independent evidence here.

## Credibility and adversarial assessment

Medium benchmark tier, institutional report, expert method. The manual is directly relevant to Vietnam and a rural LMIC rehabilitation context. Methods, diagrams and local tidal record years are stated, and experienced project guidance supports practical screening. It is not a peer-reviewed calibration study and provides no independent restoration-performance validation for its elevation colours. Its 2014 vintage and site-specific experience limit current and geographic transfer; seminality is not claimed. Institutional authority is useful but not a substitute for validation, and no independence bonus is assigned to project-derived examples.

Adversarial review retained these internal limitations:

1. Main text gives approximate flooding-frequency accuracy of ±2–3 days/month; the annex gives 3–4 days/month and interannual differences up to 10 days/month. PDF page 41 says river-mouth station tides can differ significantly from exposed coast and that independent verification is unavailable. These are not validated error bounds.
2. Page 23 prints soil water content as `100 × (FWo − DWo)` with no mass denominator. This is dimensionally incomplete; it was neither executed nor silently corrected. Balance-resolution statements also differ between pages 22's equipment and procedure text.
3. Page 30 describes records for 2010–2012; page 34 includes 2013 and predictions for 2011–2014. Dataset version and code cannot be inferred from documentation screenshots.
4. Page 19's top-2–3-m water-table criterion and page 24's 1–1.2-m observation hole describe different protocol statements, not an agreed rooting or feasibility cutoff.
5. Source guidance allows site modification and stresses joint indicators, rainfall, drainage, species choice and monitoring. No single-indicator exclusion or numeric weight was invented.

## Validation and retrospective

Opening-title identity and cache/index hash matched. Deterministic indexing found four tables; all-variable retrieval ran with `force=True` and `full_tables=True`. Central staging accepted the unit's native page quotation, context, numbers, ontology, family, role and ruleset. Separate scope, species, quote-width and number checks found no flags for the new unit. Repeated ingestion dry-run found zero new units.

Preservation checks compare parsed CSV rows to the branch base: all 540 prior sources and 5,211 prior evidence units are unchanged; only the intended acquisition row changed. No human decisions or learning cursor were advanced. Full validation results and global sweep metrics are recorded alongside this audit and in the existing metrics ledger.

Retrospective: known proxy, graphical-endpoint, secondary-lineage, method-versus-calibration and incomplete-coverage rules prevented unsupported additions. No new defect category was established by this bounded pass, so the ruleset stays v1.8.0. Global metrics are not evidence of improved extraction accuracy from one added unit. Remaining candidate workload: 24 of the 29 new candidates lack main-paper review, plus the separate ITTO reuse task; reviewed sources still have explicit holds.
