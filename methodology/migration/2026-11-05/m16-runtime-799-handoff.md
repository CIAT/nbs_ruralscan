# Runtime handoff for the 799-row release

The six-practice release contains 288 T3, 43 T4, 394 T6 and 74 T6E rows. All 798 previous rows retained their values and order. The added T4 row covers annual rainfall for terrace siting. [Previous handoff](m16-runtime-798-handoff.md) · [Offline verification receipt](m16-runtime-799-handoff.json)

| Component | Tested version |
|---|---|
| Analytical release | `0964c9577fda9ba6226c1f33ead0e42d5c0b1500941f3202099850f1a649ae6a` |
| Producer | [`2023cb82c94a93120600a7feb17d8cd1e12ce54f`](https://github.com/CIAT/nbs_ruralscan/commit/2023cb82c94a93120600a7feb17d8cd1e12ce54f), the head tested from [PR #645](https://github.com/CIAT/nbs_ruralscan/pull/645) |
| Runtime | [`94a7c6568cf986359fc73f9d01a4d1ebb386776d`](https://github.com/RuralScan/runtime/tree/94a7c6568cf986359fc73f9d01a4d1ebb386776d) |
| Spatial scoring package | `developer-v0.1.5`, source `b356b2af3861bfed6a4c4afc7f25129cca2cdfec` |

Rebuild from the recorded producer commit. Its identity is part of the release ID. The evidence correction and the additional review-log event originate in #645. The migration receipt records the exact version tested.

## Verification after merge

The wheel built from [runtime main at e690d4e](https://github.com/RuralScan/runtime/commit/e690d4e413d925c28c273945a5268ddbfb2d67cc) reproduced the committed 799-row receipt byte for byte. The producer-side check passed on both main revisions below. Both readers agreed on 62 values across six practices. All nine archive checksums passed. Replaying the rainfall correction on its recorded base reproduced the evidence and review-log CSVs at `887189ce`.

| CIAT main revision | Clean build in a separate store |
|---|---|
| [887189ce](https://github.com/CIAT/nbs_ruralscan/commit/887189ce4238427486816cc3e83674ec9bfc2dfd), after #645 and #650 | 799 rows. Of 87 members, 86 were byte-identical to the pin. Only the producer revision in `provenance.json` changed. All 102 input and 51 compiler hashes matched. Rebuild ID `f197afee6b51c7fb4ae0569d49049a70c4ec994eb356969896910dff210448fa`. |
| [c10e14b3](https://github.com/CIAT/nbs_ruralscan/commit/c10e14b311383bfe94d6ff8abceab3c5019e26b1), after #653 | 801 rows. Water-harvesting T4 grew from 13 to 15 rows. Six members changed across its settings, readiness report, T4 table pair and release provenance. Rebuild ID `0347a72f50dc55e97b432ea028cb892c292b168ea1b5068c9b4755d53b33e018`. |

The runtime default selects the 799-row release by ID. To reproduce either main build, check out its exact revision and publish to an empty scratch store using the [release build guide](../../../docs/RECIPE_RELEASES.md). The [scoring publisher check](m16-scoring-package-publishers.md) exercises the same recipe pin against both copies of the scoring package.

## Terrace rainfall

WOCAT reports forward-sloping benches in places receiving 200–600 mm/year. This observed use range supplies the single source counted for the annual mapping. The Ronquillo watershed model uses mean October–April rainfall. Its study-specific classes and 0.04 criterion weight remain contextual. The FAO profile describes contour stone lines for crop water harvesting. All three profiles retain their evidence IDs and locators. The annual precipitation layer is available, but the terrace row has no approved common curve or selectable scoring function. All 13 water-harvesting T4 rows require calibration, eight also need matching spatial inputs, and all six practices report `execution_ready=false`. [Decision](https://github.com/CIAT/nbs_ruralscan/blob/2023cb82c94a93120600a7feb17d8cd1e12ce54f/methodology/audits/t4_water_block_20261109/terrace_rainfall.md) · [Run record](https://github.com/CIAT/nbs_ruralscan/blob/2023cb82c94a93120600a7feb17d8cd1e12ce54f/methodology/audits/t4_water_block_20261109/terrace_rainfall_run.json)

The archived correction changes only `relationship` and `context` on `ev_wh_annual_precipitation_krois14_1`. Its scalar annual limits are cleared. Its identity, quotation, locator and review state are preserved. Applying the correction to the recorded input revision in an isolated Git index reproduced the producer's exact evidence-register CSV and review-log CSV, including one appended `unit_correction` event. All three evidence fingerprints and the compiled rainfall row fingerprint matched the run record.

## Verify both readers

Set `RECIPE_STORE` to the authorised store, `RUNTIME_PYTHON` to a separate environment with the recorded runtime installed, and `RUNTIME_CHECKOUT` to its checkout. From the repository containing this handoff record, run:

```sh
rid=0964c9577fda9ba6226c1f33ead0e42d5c0b1500941f3202099850f1a649ae6a
proof=methodology/migration/2026-11-05
"$RUNTIME_PYTHON" -I -m nbs_runtime.recipe_release --store "$RECIPE_STORE"
uv run python scripts/check-runtime-recipe-handoff.py \
  --store "$RECIPE_STORE" --release-id "$rid" --runtime-python "$RUNTIME_PYTHON" \
  --legacy-upstream "$RUNTIME_CHECKOUT/upstream" > runtime-handoff.json
diff -u "$proof/m16-runtime-799-handoff.json" runtime-handoff.json
```

The clean build and the local install produced identical receipts across all 24 typed tables, 25 settings, 12 reports and provenance. All three legacy scoring criteria matched their fingerprints. The runtime opened the 798-row release with its saved pin and rejected a transfer mixing the previous water-harvesting table with this generation. [Release build guide](../../../docs/RECIPE_RELEASES.md)

## Transfer the audit records

Copy `audits/<release_id>/` alongside `generations/<release_id>/` in the authorised store. The archive contains the six depth and slope files, the terrace-rainfall decision and run record, and `terrace_rainfall_evidence.patch`. The patch carries the original and corrected register row and its review-log event. These nine files are checked separately from the 87 generation members. [Audit checksums](m16-runtime-799-audits.sha256)

To restore the archive to a fresh store, use the pinned Git objects. Fetch `refs/pull/645/head` if the producer revision is missing. Run from the repository root with `RECIPE_STORE` and `rid` set as above.

```sh
producer=2023cb82c94a93120600a7feb17d8cd1e12ce54f
base=e00cd34d9cb218b9a5d6cd911aa9633dfff51928
source_dir=methodology/audits/t4_water_block_20261109
archive="$RECIPE_STORE/audits/$rid"
checksums="$(pwd)/methodology/migration/2026-11-05/m16-runtime-799-audits.sha256"
mkdir -p "$archive"
git archive "$producer:$source_dir" soil_depth.md soil_depth_run.json \
  terrace_depth.md terrace_depth_run.json terrace_slope.md terrace_slope_run.json \
  terrace_rainfall.md terrace_rainfall_run.json | tar -x -C "$archive"
git diff --no-ext-diff --no-textconv --no-renames --full-index --color=never \
  --diff-algorithm=myers --unified=0 --src-prefix=a/ --dst-prefix=b/ \
  "$base" "$producer" -- pipeline/metrics/review_log.csv schema/registers/EV_evidence_register.csv \
  > "$archive/terrace_rainfall_evidence.patch"
(cd "$archive" && shasum -a 256 -c "$checksums")
```
