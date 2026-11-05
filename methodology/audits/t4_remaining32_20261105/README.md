# T4 spatial-targeting screen — 5 November 2026

All 32 previously unread active T4-tagged sources in the bounded triage set now have a source-purpose disposition. This is a **screening closeout**, not a claim that every main paper, supplement, variable or practice has been fully extracted or approved. Work stayed within T4; no effects, economics or operational-risk units were admitted.

| Practice | Sources screened | Spatial targeting or implementation material retained |
|---|---:|---:|
| Agroforestry | 8 | 1 |
| Forest restoration | 7 | 5 |
| Water harvesting | 6 | 5 |
| Wetland management | 11 | 4 |
| Total | 32 | 15 |

Sixteen sources do not pass the practice-level T4 purpose gate; one agroforestry PDF is image-only and remains an adapter/readability hold. The 15 passing sources include conditional design and spatial-priority method referrals: **a pass is not a ready-to-use suitability relationship**. Species, model and design information is retained with its scope, not deleted. Poorter’s cached proof and team-library published version also differ; no evidence from that source was admitted.

## What entered the evidence register

Central intake stored five unapproved `structural_suitability` claims from four newly registered sources. Full-build scope checks then quarantined both Rao claims (`carbon_biomass`); **three new claims remain active and two remain preserved as dropped review holds**:

- Rao/Nair/Ong 1997 (**quarantined, not active**): two conditional hedgerow-intercropping claims for rainfall and soil acidity. Rainfall below 1,000 mm is not a universal exclusion. Soil acidity is coupled to fertility, water and management. The source’s discussion of slopes below 15% is retained as scope, not a new slope cutoff.
- Cloud-forest restoration study: one qualitative preference for passive recovery near mature forest. No distance threshold or fitted distance-response curve.
- WOCAT 4101: one regional upper-treeline boundary for South Caucasus afforestation. The reported 2,300–2,600 m band is not a global or exact elevation exclusion.
- China wetland targeting study: one explicit existing-built-up-land exclusion applied after potential-wetland prediction. Regional, unapproved scoping evidence; no runtime mask activated.

All four SRC records remain `in_progress`. Registration does not close their remaining source accounting. No human approval, executable mapping, family change, consolidation, removal or new discovery was claimed. Cao’s secondary aridity claim stays held until its primary lineage is established. Tidal/salt-marsh and treatment-wetland scope remain parked; spate’s existing parked wording is preserved.

## Useful material retained for focused T4 work

- **Water harvesting:** FAO potential-irrigable-area guidance uses divertible runoff timing/amount and soil water storage; Nooka Ratnam separates erosion-priority mapping from check-dam site assessment; Wolka provides technique-specific slope stability and rainfall-fit guidance. Canonical variable/family/lineage review remains before atomic admission. Boers and Schiettecatte remain conditional crop/design referrals, without invented generic rainfall envelopes. WOCAT 941 fails the capture-structure practice gate.
- **Wetlands:** Goyette’s compatible land-cover availability and spatial allocation are scenario-feasibility candidates; Odgaard’s organic-soil proxy is bounded model-use information, with priority weights kept separately; China’s upstream predictors and final convertible-cover overlay remain explicit model-use/categorical candidates. Potential occurrence is not automatically restoration suitability. Moreno’s treatment-versus-creation scope remains held.
- **Forest:** legal restoration allocation and benefit-priority mapping remain spatial-method referrals; they do not establish ecological suitability. The cloud-forest invasive-dominance clause remains an ontology/scope hold.
- **Agroforestry:** Bayala’s flood/drought passage selects tree traits rather than parkland locations and is retained as a species/trait referral. The unreadable Atlantic-pasture source needs approved readable acquisition/intake before extraction.

These remaining jobs are recorded in source inventories, rather than reopening the 32 sources as generically unread. `source_triage.csv` preserves all 103 original triage records and changes only the 32 screened dispositions. Queue status advances only for the four sources that yielded admitted evidence.

Developer-readiness check also found that approved wetland evidence does not reproduce six existing live recipe rows. `relationship_visibility.json` records the exact keys. This is an unresolved compilation/parity hold; no live recipe was regenerated or declared release-ready. Agroforestry and forest checks did reproduce their audited recipes.

## Rules and independent review

Ruleset v1.9.5 now explicitly requires a page-linked passage showing spatial targeting or spatially usable implementation conditions **before T4 extraction**. A map is not mandatory; generalising siting guidance qualifies. Titles, sampling locations and measured benefits alone do not. Source-purpose passage, suitability claim, numeric calibration and runtime approval remain separate gates. Historical evidence versions are untouched; this batch’s drafts were produced under v1.9.4 plus Pete’s explicit 5 November gate.

Independent review corrected five Odgaard quotation locators (PDF 3; figure weights remain PDF 7), restored useful wetland model-use/scenario constraints, narrowed Bayala to a trait referral, and added Rao’s scope and abbreviation definitions. Central intake then moved a page number out of the relationship payload and placed supporting scope/definitions under supported context fields. The full-build `carbon_biomass` rule disagreed with the narrow Rao implementation-guidance reading. Both records remain quarantined; no automatic reopen, deletion or approval. No gate was weakened.

## Validation and retrospective

- `verify.py`: exact 32-source membership, 176 unique native-page anchors, no mismatches; one explicitly unverified image-only source.
- Deterministic indexes and full-table retrieval built for all four admitted sources. Expanded page-stamped retrieval contains all five admitted quotes; EvidenceUnit validation and central provenance/number/context/VONT/FAM/role gates pass.
- All 6,255 previous EV records and 713 previous SRC records remain field-identical. Totals: 6,260 EV and 717 SRC. Review log and family registry unchanged.
- All five new records remain unapproved; three are active and two quarantined. Numerical mappings remain unchanged. Agroforestry verification is `in_progress` with the quarantine explicitly recorded, not complete.
- Instruction/snapshot and pipeline-hardening checks: 44 passed. Full schema generation/provenance and structure results are recorded in `checks.json`.
- Retrospective: the source-purpose failure was already implicit in the suitability/site-context rules. v1.9.5 makes it an explicit early checkpoint. No global review-feedback cursor advanced. Screening cannot demonstrate improved global defect rates: measured number-provenance 4.7% and verification 0.3% stayed unchanged. The two automatic scope quarantines are a material batch limitation, not evidence of improved extraction quality.

Reproduce the bounded provenance/preservation checks with `PYTHONPATH=src python methodology/audits/t4_remaining32_20261105/verify.py` using the project environment and local corpus. Source-specific reports and prior reviewer findings are retained as audit history; this README and `admission_status.json` record the final central outcome.
