# Dashboard feedback round 2 — 4 November 2026

Input: Pete's 12-note HTML report, exported 14:44:18, plus earlier request to remove search-run counts from Progress.

## Review and implementation sequence

1. **Count meaning (notes 1, 4, 5, 6).** Separate discovery result appearances from catalogue records. Give found, screened and passed distinct columns. Explain the catalogue total as registered plus queue-only canonical records. Replace `?` with `Type not recorded`; missing queue metadata cannot be inferred safely. Never calculate screening percentages across unmatched cohorts.
2. **Overview hierarchy and readability (notes 2, 3, 7, 8, 9, 10).** Keep one compact practice table and four headline totals. Remove per-number footnotes and search-run counts; put definitions in a disclosure and protocols in Methods. Keep navigation sticky. Put family/subpractice detail only in practice tabs; remove repeated practice headline figures. Printed report is the overview.
3. **Monitoring accuracy and usability (notes 11, 12).** Hide explicitly out-of-scope families from active monitoring; preserve historical records and totals. Replace unsupported ledger extraction/review columns with real family evidence and human-approval counts. Add family and review-backlog filters. Keep three authored ledger stages in a collapsed, filtered, paginated activity log.
4. **Validation.** Adversarial count review; behavior checks for filters, scope exclusions, feedback navigation and print restoration; visual checks for sticky navigation, compact tables and disclosures. Rebuild generated dashboard data and version the release.

## Adversarial findings incorporated

- 853 known sources = 673 registered + 180 queue-only canonical source records. Raw union has 877 IDs; explicit alias merges remove 24. Counts are snapshot-specific, so UI derives the breakdown.
- All 180 unclassified records, including Agroforestry's 41, are queue-only. Queue has no authoritative source type fields; preserve unknown classification.
- Agroforestry's 11,812 found / 1,083 screened / 260 included aggregate different reporting coverage. They are not unique-source funnel stages. Overview now uses a matched complete cohort for all three discovery columns; partial counts stay in Methods. Count-definition version 2 records this presentation change.
- Ledger only stores searched, screened and verified. Previous UI's extracted/reviewed columns read nonexistent fields. Extraction and approval now use evidence metrics instead.
- Verification is source/extraction checking; human approval is `reviewer_ok`. Only human approval has an excerpt numerator and denominator suitable for display.
- Hide only explicit `out_of_scope` status. Preserve plantation's `separate_comparison` status and historical evidence.
- Closed family disclosure content must remain hidden in both browser rendering and screenshot capture.

No analytical rules, evidence decisions or source metadata are modified.

## Validation results

- Full suite: 1,025 tests passed; targeted dashboard suite: 35 passed.
- Lint, formatting, type check, schema structure and T4 evidence coverage passed.
- Full dashboard DOM integration passed, including QA tab startup, bibliography, evidence drawer and saved-feedback family navigation.
- Browser: sticky tabs, compact family table, scope exclusions, family filter and expanded subpractice layout verified. Final checks moved to the desktop app's built-in browser at Pete's request; personal Chrome is no longer used.
- Reviewer found no remaining blockers after fixes. Print restores practice state/filter handlers under automated tests; visual print preview not confirmed.
