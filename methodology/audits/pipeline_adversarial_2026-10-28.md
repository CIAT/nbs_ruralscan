# Adversarial pipeline review before forest and mangrove T4

28 October 2026. Base: `8405f2d4bd32266b2d202042fa172c257c571d6f` (merged PR #463).
Scope: adversarial code/protocol checks, not a literature search, extraction sweep or
new human review. Three independent agents tested acquisition/discovery, provenance
and staging, and T4 synthesis; the parent reviewed cross-NbS handoff and integration.
Agents then cross-reviewed each other's fixes. All attacks used isolated test fixtures.

## Assessment

The previous hardening addressed normal failure paths but left demonstrable bypasses.
This review adds deterministic failures for those cases, preserves existing source
artifacts and approvals, and removes accidental agroforestry inheritance. The tested
workflow is stronger; this is not certification of every legacy claim or every entrypoint.

No production queue, source/evidence register, review decision or analytical CSV was
changed. Existing agroforestry compilation still reproduces its audited recipe. Ruleset
v1.8.0 snapshots the strengthened extraction contract and the corrected synthesis workflow.

## Findings and fixes

| Boundary | Reproduced failure | Fix / regression evidence |
|---|---|---|
| Download → source | Readable unrelated PDF could inherit verified DOI metadata | Check opening title before publishing a new cache artifact, at promotion and staged ingestion; wrong first URL cannot poison cache or prevent trying the next URL |
| Library publication | Acquisition could overwrite a different existing team PDF; subdirectory could escape library | Immutable exclusive atomic copy, exact path containment, existing bytes preserved |
| Human intake | Corrupt input could abort remaining files; archive collision or failed queue persistence could lose original download | Isolate per-file errors, preserve differing archives, remove original only after queue persistence |
| Artifact provenance | Different artifact kinds shared a sidecar; GitHub path `?`/`#` could interfere with the commit-pinned URL | Refuse cross-kind sidecar collision; escape literal paths and reject binary content through text adapter |
| Discovery coverage | Known identity in a new NbS/table/family, including two lanes in one batch, could lose its new work through dedupe | Explicit pre-write reuse hold instead of silent discard; retained candidate/report identifies required reconciliation |
| Registered scope | Pipe-delimited NbS memberships were skipped or narrowed during acquisition/promotion | Exact token membership; preserve all already-declared scopes; hold an existing SRC missing those scopes |
| Search history | Duplicate lane/log names or conflicting report overwrite could erase provenance | Preflight complete batch and preserve historical logs; conflicting DOI/title, unknown NbS fail |
| Quote provenance | Translation-only quote normalised to an empty native substring and passed | Native anchor required independently; supplementary rationale/selection quotes checked on their own pages |
| Payload types | Nested NaN/infinity, numeric IDs, duplicate JSON keys and Boolean numeric values bypassed permissive parsing | Strict staging types/portable JSON; finite numeric checks through synthesis/harmonisation; malformed payload fails before append |
| Register append | Bad later row could partly append a batch; duplicate existing IDs could shadow records | Render and validate full batch before atomic EV publication; reject duplicate identities |
| Synthesis scope | Public row API could compile dropped records or relabel another variable/family; selected coffee could include cocoa | Exact family/variable/crop membership and dropped-record gates in public APIs |
| Units and response geometry | `native`/`mixed` canonical labels allowed unlike source units to pool; rounded conversion merged nearby piecewise knots | Refuse cross-scale pooling without conversion; preserve distinct piecewise coordinates; invalid bounds, overflow and intervals fail |
| Source independence | Lineage cycles or source-level pointers to mixed origins depended on input order | Explicit cycle/ambiguity failure; no arbitrary origin vote |
| Support denominator | Invalid denominator types or fewer screened sources than observed sources could produce misleading support | Validate cohort size/type; unknown stays unknown; approved reporting change below |
| Draft publication | Unreviewed output could be written into another live recipe or root file; explicit dry-run report still wrote | Only external or staging diagnostic destinations, no existing report overwrite; true no-write dry run |
| Developer handoff | Other NbS packages copied agroforestry instructions and decisions | Recipe-specific documents or neutral templates, with local-link tests and pinned document hashes |
| Package verification | Empty/incomplete manifest or omitted analytical hash entries could claim successful verification | Require complete contract outputs and analytical inputs; reject unlisted payload files and changed hashes |
| Active guidance | Old synthesis command hardcoded an F5 name and direct JSON output; forest document still parked mangrove | Delegate to current CSV compiler/policies; document signed standalone mangrove routing and preserve historical decisions |

The new tests are in `tests/test_adversarial_ingestion.py`, `test_adversarial_gates.py`,
`test_adversarial_t4.py` and `test_adversarial_handoff.py`. They test refusal paths and
valid recovery, not only implementation-shaped assertions. Examples include wrong first
PDF followed by correct PDF, failed atomic publication preserving EV bytes, source-order
permutations, crop separation, close slope breakpoints and package manifest omissions.

## Approved reporting decision

Pete approved on 28 October 2026: **“Approve: study counts first; quality weighting separate.”**
See [decision and exact interpretation](../decisions/2026-10-28_t4_support_reporting.md).
Headline `paper_support_pct` is raw n/N over the declared screened cohort. Quality-weighted
support is a separate diagnostic, only calculable with complete explicit membership and
known source tiers. An integer N does not authorise inventing medium quality for unseen
sources. Unknown denominators remain blank. This does not change quality weighting of
compatible response functions, source-relative importance or runtime MCDA weights.

Source IDs must represent the intended canonical studies; the support API cannot infer
DOI equivalence from IDs alone. Existing developer inclusion calculations use their own
DOI-deduplicated cohort. Those two denominators must remain labelled, not conflated.

## Validation

- Full test suite: **944 passed**, including the approved support-convention change;
  only five existing PyMuPDF/SWIG warnings. The four new adversarial test files cover
  acquisition, staging, synthesis and developer handoff; support tests additionally
  cover raw counts, complete quality cohorts and unknown denominators.
- Ruff lint and format checks pass. Type checks pass for all changed Python production
  files plus the CI core targets. This is not a claim that unrelated repository-wide
  type debt has disappeared.
- Schema generation check: **0 stale JSON files**. Structure: **0 errors**, 3,443 existing
  warnings across CSV/JSON surfaces. T4 coverage: **0 errors**.
- Existing advisory findings remain visible: 5 scope flags, 489 narrow-quote flags,
  90 whole-page/table quotes, 47 band disagreements and 9 unmapped effect variables.
- No learning cursor or progress stage advanced: no full retrospective/extraction sweep
  was performed. The prior 1,050 unprocessed-feedback estimate remains, not 1,050 new
  requests to Pete.

Commands (use the project Python environment):

```sh
PYTHONPATH=src pytest -q
ruff check .
ruff format --check .
python src/nbs_ruralscan/schema_tools/generate.py schema --check
python src/nbs_ruralscan/schema_tools/structure.py schema
PYTHONPATH=src python -m nbs_ruralscan.schema_tools.t4_coverage
```

## Remaining limits and explicit holds

1. **Source reuse is visible but not automated across new scopes.** The existing queue
   cannot fully represent completion per source × NbS × table × family. Registering
   a known source for a newly requested scope now stops with its canonical IDs and
   retained discovery inputs. A tracked reuse workflow must be designed before those
   holds can be cleared; do not create duplicate papers or silently widen SRC scope.
2. **Non-page locator validation remains adapter-dependent.** Generic section staging
   verifies quote containment in the snapshot, not that it appears under the claimed
   heading. WOCAT group/field locators and generic web headings are not interchangeable.
   Use only a source adapter that verifies the actual anchor or hold the claim for
   adapter work. No new claim of exact-section validation is made here.
3. **Document identity is a conservative heuristic.** Opening-title word coverage can
   hold scans/chapters and does not establish scientific fidelity. Manual identity
   resolution needs an auditable artifact binding, not an unverified bypass flag.
4. **Atomic files are not a multi-register transaction.** EV append and SRC resync, and
   discovery queue/SRCH/ledger updates, are still separate operations. Use one central
   writer in an isolated worktree; coordinate review submission before refresh. A future
   transaction/locking mechanism is needed for arbitrary concurrent writers or whole-job
   crash recovery. Exclusive artifact copy also requires hard-link support on its filesystem.
5. **Legacy content was not re-reviewed.** Prior audit's 52 source identity holds,
   six zero-EV completion checks and 120 acquired/unregistered sources still require
   reconciliation. CI without the local corpus cannot verify every source quote.
6. **Ecological policy stays explicit.** No new native-ecosystem afforestation mask,
   species-to-practice transfer, mangrove method split, regional transfer or MCDA vector
   was authorised by this software review. Bring actual proposals to Pete before applying.

## Next-NbS readiness

Read-only baseline on this revision:

| Scope | T4 + operational EV total | Active | Active `reviewer_ok=true` | Sources across these records |
|---|---:|---:|---:|---:|
| All forest restoration families | 211 | 210 | 0 | 53 |
| Mangrove restoration | 39 | 39 | 0 | 17 |

These flags do not prove that no reviewer ever considered a record: reconcile decision
history first. They are not a request to re-review every extract. Forest has a legacy T4
CSV needing current compiler/review reconciliation; mangrove has no T4 CSV yet.
Reforestation/afforestation remain active planting within forest restoration; production
plantations stay separate under the existing roll-up exclusion. Mangrove has its own
approved tidal/coastal family. Neither recipe may inherit agroforestry defaults.

The [new-session prompt](../../handoff/T4_FOREST_MANGROVE_SESSION_PROMPT.md) starts with
this reconciliation, prioritises active planting and mangrove, retains genuine holds,
and ends with a tested developer table through GitHub. Pilot testing stays with Diego
and Brayden.
