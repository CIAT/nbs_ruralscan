# T4 source follow-up and priority review — 5 November 2026

This bounded follow-up continues the 32-source spatial-purpose screen. It adds **14 active, unapproved T4 evidence units from four sources**, with no new executable mapping, human approval, practice reassignment or removal. The full build retained all 14. Eight existing sources received targeted follow-up: four water-harvesting sources, three wetland sources and the Cao forest-restoration source. This is not a new discovery sweep or a claim of complete all-practice extraction.

## Retained evidence

| Lane | New claims | What is retained | What is not established |
|---|---:|---|---|
| Water harvesting | 4 | Wolka Table 1 rainfall preference and slope fit; Fanya juu stability direction; tied-ridge gentle-slope condition | Universal cutoffs, fitted curves, graded-drainage family applicability |
| Wetlands | 9 | Goyette compatible-cover scenario; seven China model inputs and one restoration-cover overlay | Independent restoration suitability directions, global conversion permissions, runtime weights |
| Forest restoration | 1 | Cao's qualitative afforestation water-balance limitation, with exact external primary attribution | A numerical aridity threshold or independent primary field calibration |

Only two new records carry explicit, bounded directions: Fanya juu stability versus slope and Cao's movement away from severe precipitation-to-demand deficit. The other records retain conditions or model use without inventing a monotonic response. All 14 have compiler disposition `unresolved_review`, with zero live mapping links. The seven China predictor records expose an upstream potential-occurrence model used in the source's restoration workflow; they are not validated restoration response functions.

Three acquired sources were registered through the central identity gate. All four touched sources remain `in_progress`. China's existing low benchmark tier is preserved; no follow-up suggestion silently overwrites it. The three new sources are medium-tier reviews/model evidence with explicit regional and independence limits. The only change to a previous SRC record is China's extracted-variable list. All 6,260 previous EV rows remain field-identical; totals are 6,274 EV and 720 SRC.

## Six wetland mappings: prioritized review, not removal

Trial synthesis reproduced the mismatch: all six live wetland mapping rows cite unapproved evidence, with substantive numeric or contextual problems. Examples include an observed canal-density mean treated as a minimum, paludiculture marginal classes treated as zero-suitability endpoints, and restoration priority rules treated as exclusions. Blanket approval or regeneration would not resolve those problems.

Pete's response was to **prioritize these for review and request a dashboard priority filter/control**. He did not approve temporary removal. Every live mapping, FAM entry, evidence record and review decision remains unchanged. `parity/priority_review_batch.json` provides six exact evidence IDs, mapping/source/page links, reasons and decision questions. `parity/REPORT.md` contains the diagnosis. The empty proposed mapping CSV is an unapplied diagnostic proposal, not the selected repair.

The dashboard chat received the explicit implementation request and six-record handoff. Dashboard UI work is owned by that chat; priority metadata must not act as a Keep/Drop decision, source-quality score or runtime authorization.

## Remaining precise holds

- Wolka's generic soil depth is not proven depth to bedrock. Its literal condition is retained in the ontology hold. Graded drainage and contradictory drainage wording remain separate from level-bund capture.
- Nooka Ratnam names soil properties, runoff quantity and velocity without sufficient measurement semantics for existing canonical variables. Erosion-priority weights remain methodological context.
- Boers remains a crop/soil/design-conditional microcatchment referral. Schiettecatte's jessr/jessour lies in the parked spate definition; its queue tag cannot reassign or unpark it.
- Odgaard's organic-soil proxy is not soil organic carbon. Goyette's allocation composite and 23 China variable/measurement issues remain explicitly inventoried.
- The earlier image-only agroforestry and Poorter artifact-version holds are unchanged. Both earlier Rao claims remain quarantined; no automatic reopening occurred. Tidal/salt-marsh and treatment-wetland scope remain parked.

Cao's previous missing-primary-register hold was too strict. The schema permits an exact external citation in `attribution`; `lineage_of` is reserved for corpus evidence/source IDs. The referenced correspondence was identified through the publisher and title/DOI verification, but is not counted as an independent empirical study. This resolves attribution for the secondary claim without inventing a corpus ID or requiring a numeric response.

## Validation and retrospective

Central source promotion and intake gates pass: native quotations, numeric provenance, context, VONT, FAM, role and ruleset. Deterministic indexes and retrieval packages were built; the final 14 `EvidenceUnit` objects were validated and saved before intake. Independent reviewers corrected overly broad table quotes, a soil-depth proxy, unsupported context keys and invalid author-year strings in `lineage_of` before admission.

`verify.py` confirms 33 native claim/support anchors, all previous EV records unchanged, only China's expected SRC variable update, three expected queue updates, and byte-identical live T4 mappings, FAM and review log. Full generation verifies 4,775 quotes against 711 cached sources, with 1,499 baseline exemptions and no new quarantine. Post-intake full test suite: 1,074 passed. Repository-wide lint and format checks pass; generated JSON has zero stale files; T4 coverage has zero errors. Structure check: zero errors, 3,983 advisory warnings. Seven short China row quotes carry separate native caption/header anchors; short-quote advisories are not treated as proof of missing context.

Metrics are recorded once under `t4_followup_20261105`: number-provenance flags remain 291, verification mismatches 16, displayed rates 4.7% and 0.3%. No improvement is claimed from this bounded pass. Existing defect classes explain the pre-intake repairs; no global learning cursor advanced. For the next bounded pass, central context validation and row/header quote checks must happen before independent semantic review, and external citation strings must be checked against the corpus-ID meaning of `lineage_of` before staging. This is a targeted enforcement of existing rules, not a new scientific eligibility rule or historical restamping.

Reproduce with `PYTHONPATH=src python methodology/audits/t4_followup_20261105/verify.py` in the project environment with the local corpus. Lane reports retain staging-time status; this README, `admitted_units.json`, `validation.json` and `relationship_visibility.json` record the final central outcome.
