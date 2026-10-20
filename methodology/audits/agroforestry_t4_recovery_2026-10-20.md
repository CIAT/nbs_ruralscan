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
4. Baldwin: decide whether the speculative agricultural/open-land statement is admissible for a host rule. Dataset crosswalk and system applicability need review before use.

Review surface: `docs/review/t4-evidence-recovery.html`; original table images and exact evidence IDs included. Pilot execution remains Diego's task.
