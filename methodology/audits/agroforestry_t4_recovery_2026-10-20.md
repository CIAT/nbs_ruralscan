# Agroforestry T4 recovery — 20 October 2026

## Outcome

The scoping-review inventory now reconciles all 23 agroforestry papers to SRC. Five previously missing sources were registered from the shared library; Mendonça 2023's incorrect duplicated DOI was replaced with its title-verified MethodsX DOI. Existing exclusions, including Brandt, remain intact.

- Chuma 2021's **already human-approved** slope record now compiles three numeric classes. The prior compiler did not understand its range-valued fields. Original percentage thresholds are converted to degrees using the existing unit conversion. Regional applicability remains explicit.
- Eight new evidence records are preserved without invented human approval: Haile SOC continuation (two classes), Chuma elevation (five classes), five Ahmad image-table model-use weights, and Baldwin's land-use statement.
- Haile's draft response now joins four classes from two independently cited pages into **one** source profile. Live T4 retains the two previously approved classes until continuation review. Missing-parent, different-source/context/scale and overlapping continuations are rejected.
- Baldwin is quarantined by the existing speculation guardrail. It remains available for review; it sets no live mask.
- Ahmad weights document use and importance within that paper. They neither calibrate response curves nor change runtime weights. Combined soil weight is not divided among individual soil variables. Figure provenance includes page, image and checksum; review status is visible in model-use notes.

## Why review missed these

Review operated on extracted records. It did not establish coverage of the source bibliography or completeness of each table. Chuma passed human review but failed downstream encoding support; Haile's continuation fell outside the extracted page; Ahmad's model table was image-only. A previous reviewer explicitly requested the figures, without a tracked follow-through. The missing SRC papers were invisible to EV-level review.

## Source scope decisions

Mendonça 2022/2023 concern restoration priorities and vulnerability (one SIPA-AFS methodology lineage), Pinto conservation prioritisation, and Ellis species selection. Their absence from generic establishment thresholds is now an explicit disposition, not an unexplained omission. Castle's companion code is not an independent study; species envelopes and environmental-priority weights cannot become practice-level T4 limits. No new general-purpose threshold is inferred from these sources.

## Regression protection

`schema_tools.t4_coverage`, enforced in CI, reconciles the stocktake to SRC/dispositions, checks independently inventoried table class counts, checks approval boundaries against live T4, requires tracking of exact human table/figure/missing-data notes, and verifies figure checksums. The numeric compiler enforces declared class counts and compatible continuation joins. Regression tests exercise missing sources, missing policies, missing follow-ups, incomplete classes, incompatible/overlapping/orphan continuations and live-versus-draft approval boundaries.

These gates protect documented expectations. They do not claim automated detection of every unknown omission in every PDF. Table inventories must be maintained as sources are reviewed. Extraction instructions now require a table/continuation inventory and exact-note follow-through (ruleset v1.6.14, catalogue 31–33).

## Retrospective

Sweep metrics recorded as `agroforestry-t4-recovery-oct20`: register number-provenance rate 5.9%, verification flag rate 0.2%. These are whole-register values, not estimates for this eight-record recovery. None of the eight recovered records has a numeric-provenance flag; cached-source quote verification passed. Baldwin's scope quarantine is retained, not bypassed. The global learnings cursor was not advanced: unrelated review decisions have not been audited in this task. Stock T4 verification status was set to in-progress through the ledger API, reflecting pending human decisions.

## Human decisions remaining

1. Haile: confirm p6 continuation attribution to SOC and the inherited percent unit; approve the two recovered classes if correct.
2. Chuma: confirm elevation class transcription and intended regional/system applicability; no global transfer presumed.
3. Ahmad: confirm five image-read model weights against Table 2. Scaled aridity and response interpolation remain unresolved and do not generate numeric responses.
4. Baldwin: explicit methods p8 supersede the speculative p16 record (which remains dropped). Review NLCD crosswalk and transfer from pine-pasture/row-crop systems.

Review surface: `docs/review/t4-evidence-recovery.html`; original table images and exact evidence IDs included. Pilot execution remains Diego's task.


## Full five-paper extraction follow-through

The earlier source disposition pass was screening, not a completed extraction. This sweep read the main papers and retained 43 claim dispositions in `pipeline/t4_audit/agroforestry/five_source_extraction.json`. It adds 13 EV records, all pending human review:

| Source | New EV | Destination and meaning |
|---|---:|---|
| Baldwin 2022 | 4 | One explicit NLCD host-class candidate; three operational criteria (ownership consolidation, project minimum area, infrastructure conflicts). Low NCCPI and high-value-crop exclusion remain author adoption assumptions, not biological limits. |
| Pinto 2019 | 4 | Two structural candidates (Montado tree-occupied area and urban/industrial exclusions); two operational programme criteria (cattle stocking/protection and minimum area). AEM2 criteria remain programme-specific. |
| Ellis 2000 | 5 | Species-selection dataset/model-use records: rainfall, frost-free period, pH, texture and drainage. No additional practice-level threshold agreement or invented taxon. |
| Mendonça 2022 | 0 | Priority scores, classes and weights extracted into deferred priority-need inventory. Higher slope receives higher vulnerability priority; this cannot become higher establishment suitability. |
| Mendonça 2023 | 0 | Companion SIPA-AFS method, same lineage. No independent suitability calibration. |

Pinto's publisher supplements were acquired and once-rendered; originals and PDFs copied to the shared-library mirror, with hashes and paths retained in the inventory (cloud sync itself not independently verified). S3 is an opportunity-cost matrix, not an eligibility crosswalk. Its AEM2 costs are retained separately. S1 is a MARZONE literature review; S2 documents workflow. Mendonça 2023's supplemental worksheets remain explicitly deferred under the project's paused dataset-intake rule. Main-paper completion does not claim supplementary dataset validation.

Remaining genuine interpretation issues: Pinto's tree-occupied area versus EO canopy cover; transfer of regional programme and FloodWise criteria; Ellis's unitless root-depth example; Mendonça's conflicting <10 versus >10 ha small-fragment wording. These do not create new global biophysical curves. All prior approved evidence stays approved; new records are not silently promoted.

Regression tests now remove a tracked extraction, change its role, remove a covered page, or replace extraction with screening and require failure. Species-selection usage has a separate count. These checks protect documented completeness; they cannot prove no unknown claim remains in an unseen source.

Validation follow-through: full suite reached 462 passed with one UTF-8 guard failure in the new inventory reader; explicit UTF-8 fixed and all 22 affected/encoding tests passed on rerun. No new number-provenance flags (global rate remains 5.9%, rounded; verification rate 0.2%). Catalogue #34–35 and deterministic accounting checks tighten scope/completion requirements despite unchanged rounded global rates. Structure: zero errors; existing advisory warnings remain.
