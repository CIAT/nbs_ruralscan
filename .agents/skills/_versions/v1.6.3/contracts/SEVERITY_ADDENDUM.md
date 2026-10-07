# v1.6.3 addendum — hazard severity (2026-10-07)

Applies on top of `T3_T6_extraction_contract.md` §2.2.7–8 (hazard units). Units stamped `ruleset_version = v1.6.3`; units under v1.6.0–v1.6.2 stay valid and are back-tagged in place (the tag is context, not a claim).

**Why.** T3 answered "does the practice reduce the impact of drought?" with one class, whatever the drought. Pete (2026-10-07): water harvesting "can mitigate drought a bit, but it is not irrigation — it is not going to help you with late-onset or extreme drought." The table now records which hazard intensities the evidence actually covers, and the synthesis discounts a cell only for failures the source itself places at the severe end.

## `context.hazard_severity` — every unit with `context.hazard_type`

The **author's own characterisation** of the hazard event / season under which the unit's outcome was observed. Never inferred from rainfall numbers, country, or what the reader thinks a drought "must" have been.

| value | set when the source says… | examples of cue words |
|---|---|---|
| `extreme` | the event was extreme / a record / catastrophic; a season with complete failure or no rain; a stated return period ≥ 1-in-20 | extreme, record, catastrophic, rainless year, no rain, complete crop failure, worst in N years |
| `severe` | severe; the driest year of a series; prolonged or consecutive drought years; a major event; stores ran dry | severe, driest year, prolonged, consecutive / successive drought years, major flood, dried up |
| `moderate` | a drought / dry / below-average / low-rainfall year or season, or a flood event, with no stronger qualifier | drought year, dry year, low-rainfall year, below-average rainfall, a flood |
| `mild` | a dry spell, a short or minor deficit, erratic / irregular rain, a late or delayed onset | dry spell, short drought, minor, slight, erratic rainfall, late onset |
| `unspecified` | the hazard is named but its intensity is not characterised: practitioner ratings (WOCAT), general statements ("reduces drought impacts"), model averages over many years, reviews that pool events | — |

**`context.severity_cue`** — the verbatim words (a substring of the unit's `quote`, or of `context.note` / `relationship.outcome_raw` where those were sliced from the same page) that justify any value other than `unspecified`. Required for `mild` … `extreme`; `check_context` fails a tag whose cue is not found verbatim.

Rules:
1. Severity is about the **hazard event**, not the outcome. "Crop failure" alone is an outcome; it is `extreme` only when the source ties it to the season ("failed completely in the drought season" → extreme; "yields fell" → no tag from that).
2. A hazard named `extreme_rainfall` is a hazard type, not a severity cue; tag its intensity from the event wording like any other.
3. One severity per unit. A source reporting several seasons gives one unit per season (contract §2.2.7), each with its own severity.
4. When in doubt, `unspecified`. A wrong `severe` discounts a cell; a wrong `unspecified` only loses coverage information.
5. Does not apply to T6 (`variable_type != climate_hazard_mitigation`) or to units without `hazard_type`.

## Synthesis (cell_synthesis, Decision 7)

* The hazard-intensity discount (Decision 6) counts measured same-hazard failures tagged `moderate` · `severe` · `extreme` · `unspecified`; failures tagged `mild` are excluded (a practice that cannot buffer a dry spell is a different, rarer finding and is left to agreement).
* Every T3 livelihood row's account carries `severity_coverage`: weight of gains and of failures per severity value. The statement says when **no measured gain exists at `severe` / `extreme`** while failures do — the honest reading of "helps a bit, not in an extreme drought".
