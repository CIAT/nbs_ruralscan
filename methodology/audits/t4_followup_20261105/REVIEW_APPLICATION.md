# T4 review application — 5 November 2026

Pete's sequential chat decisions are applied through the normal evidence review API: 25 approvals (19 new/reopened claims and six corrected legacy claims), plus two Rao reopen events. All 6,343 evidence records remain; only the 25 authorized records change. No practice definitions, family assignments, evidence quotes or source page locators change.

## Wetland mapping publication

Six numeric compilation policies replace the six reviewed legacy mappings:

| Mapping | Published result | Remaining requirement |
|---|---|---|
| Creation water distance | 0–500 m = 1; outside unknown | Frequently flowing water-supply distance; site eligibility |
| Peatland artificial canal density | Unsupported numeric minimum removed; targeting evidence retained | Canal-specific measurement and calibration |
| Former-wetland farmland water depth | 0–30 cm = 1; >30–80 = .66; >80–160 = .33; >160 = 0; negative unknown | Mean lowest groundwater depth and eligible land mask |
| Groundwater seepage | Three qualitative classes; source ranks 3/2/1; all runtime scores unknown | Matching signed groundwater flux; normalized scores not approved |
| Restoration patch area | Universal 1 ha exclusion removed; conditional priority evidence retained | No replacement cutoff approved |
| Restoration habitat distance | 0–90 m = 1; >90–120 = .5; >120 = .33; negative unknown | Distance to riparian habitat OR open water and eligible site mask |

Numeric scores are explicitly reviewed scoping adaptations, not newly asserted source findings. Original source relationships are retained in each profile. Fingerprints bind the approved source claim and effective source/evidence context; stale approvals fail compilation. Explicit profile selection is mandatory; profiles are not pooled. Context metadata does not itself enforce a spatial eligibility mask.

All four retained mapping dataset IDs are blank. Existing generic river-distance assignments do not demonstrate the reviewed measurements; groundwater inputs have no matching binding. These mappings are reviewable specifications, not ready-to-run spatial products. The source's complete paludiculture product model is not approved. Neither farmland rewetting nor artificial canal evidence silently changes family definitions.

The 19 new claims remain evidence of variable use, direction or conditional targeting. Their approvals do not establish numeric calibration, automatic transfer, runtime weights or new hard masks. Figure 8 relative importance remains source-model importance with the original 30-predictor denominator.

## Reproduction and scope

Run the registered compiler with an isolated output directory:

```
PYTHONPATH=src python scripts/synthesise-recipe.py wetland_management --output-dir <trial-directory> --report <trial-report.json>
```

The trial produces exactly the four retained reviewed profiles. Publication changes only the six authorized mapping IDs. Dataset holds are explicit schema policy: the registered compiler keeps dataset IDs blank and records the matching-input requirement in CSV and family JSON. Full wetland CSV byte-reproduces from the isolated trial; no post-compilation edits are required. Original and final rows plus exact runtime boundary probes are in `parity/compilation_application.json`. Rao reopening also changes two agroforestry support counts from 2 to 3 sources (rainfall and soil pH). Isolated compilation confirms no curve, weight, evidence-ID list or other field changes in those rows; see `rao_support_count_application.json`. Other recipe rows are unchanged.

Generate analytical JSON only through `src/nbs_ruralscan/schema_tools/generate.py schema`. Evidence application exports, original/corrected records and decision authority are preserved in the companion audit files. Earlier notes describing application as pending are historical snapshots; this report records the subsequent application.

Validation results and remaining source/pipeline gaps are recorded alongside this report after checks finish. This review is not a new extraction sweep and does not claim completion of unsearched or unverified ledger stages.

## Bounded feedback learning

This pass addresses the 25 explicit decisions, not the entire historical feedback backlog. Deterministic regression tests now reject stale/unsigned reviewed interval adaptations, accidental shared closed boundaries, invented unknown-tail scores, and automatic fallback datasets despite explicit matching-input holds. Model importance remains distinct from suitability scoring; source-specific conditional priorities and group means do not become universal exclusions. No new extraction sweep or global learning-cursor advance is claimed. The global generator reminder about unincorporated historical feedback remains visible.

Release accounting also appends the two reopened Rao records with their compiler-derived non-numeric dispositions. Historical reconciliation rows remain unchanged; no unaccounted live evidence is hidden.

## Validation — 5 November 2026

- Registered wetland compilation: isolated/live CSV byte equality; exact boundary probes pass for all four profiles, including negative/unknown domains and explicit selection.
- Full local suite: 1,151 passed; one release-accounting failure identified missing Rao reconciliation entries. After appending those two entries, all 58 release/numeric/interval/binding regression tests pass.
- Ruff lint/format and core type checks pass. Structure validation: zero errors (4,007 existing advisory warnings). T4 coverage: zero errors. Standard generator succeeds; JSON synchronization test passes in the full suite.
- Preservation: 6,343 evidence IDs retained; exactly 25 authorized records changed, with quotes/pages/source IDs/families unchanged; 27 review events appended without changing earlier events.
- Wetland developer package builds and verifies input/output hashes. It reports four blocked configured mappings and six reference-only operational records; no raster run is claimed. Package created at `/tmp/nbs-t4-wetland-reviewed-20261105` for local inspection; reproducible with `scripts/build-t4-developer.py --nbs wetland_management --output <external-directory>`.
- Twelve missing local cache artifacts were hydrated from the existing shared checkout before successful provenance validation. No provenance gate was bypassed. Pre-existing whitespace in verbatim multiline evidence quotes remains preserved.
