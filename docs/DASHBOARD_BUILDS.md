# Dashboard releases and data builds

The header identifies three things independently:

- **Dashboard version**: human-readable release from `docs/dashboard-releases.csv`.
- **UI build**: content fingerprint of the dashboard HTML, local JavaScript/CSS and release log. Changes to these assets produce a new build.
- **Data build**: content fingerprint of the complete generated dashboard payload, including registers, compiled recipes, queue-derived progress, review history and protocols. Different data produces a different fingerprint.

The build date and source revision identify when and from which checkout the snapshot was generated. The source revision is the input revision, not the later commit that contains the generated file. Rebuilding unchanged inputs preserves the date, revision and build identity.

## Releasing changes

1. Edit source files or CSV registers. Never edit `docs/dashboard_data.json` by hand.
2. For a dashboard release, append a version, date, count-definition version and short change description to `docs/dashboard-releases.csv`. Use a patch for fixes, a minor version for compatible features and a major version for a changed user-facing structure. Increment the count-definition version when counting semantics change.
3. Run `python3 src/nbs_ruralscan/schema_tools/generate.py schema`.
4. Run the project checks. `generate.py schema --check` rejects stale data or UI fingerprints and detects altered payloads even if their stored build IDs were left intact.
5. Commit source changes, release log and generated data together. Reload the dashboard to see the new identity.

The generated file retains the latest 50 build entries. Earlier entries remain in Git history. Routine review submissions regenerate data through the same path; they need no dashboard version bump when only evidence or review data changes. The build history remains inside the already-allowed generated JSON, so review-only submissions retain their existing governance.

## Count interpretation

Progress separates search observations from source records, excerpts and compiled relationships. Source totals reconcile only explicit aliases; they are not a claim that all bibliographic duplicates have been resolved. Stocktake is an origin, redistributed by recorded publication type. Unmatched legacy stocktake/tool resources remain in Bibliography but do not inflate source totals.

A source with an approved excerpt is not necessarily a completely reviewed paper. Per-source screening decisions, exact discovery-search links and citation parents are not captured consistently in current registers; the dashboard displays this gap instead of inferring them. Adding those fields later requires the normal manifest/schema change process and migration, not a dashboard-only guess.

The Progress print action includes the project-wide workflow, distinct grand totals, expanded family/subpractice breakdown and build identity. Browser print-to-PDF can save that view for project reporting.
