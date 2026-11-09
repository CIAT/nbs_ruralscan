# Runtime handoff for the 797-row release

The six-practice release contains 288 T3, 41 T4, 394 T6 and 74 T6E rows. It retains all 792 rows from the first handoff and adds five water-harvesting T4 mappings. All 11 water-harvesting mappings require calibration. Eight also require a matching spatial input. All six practices report `execution_ready=false`. [Previous handoff](m16-runtime-recipe-handoff.md) · [Current verification receipt](m16-runtime-797-handoff.json)

| Component | Tested version |
|---|---|
| Analytical release | `ef2b83d14be8e215857a1ce5ae0fa1b4e403ebeefd17a44cf84d4158679a4c86` |
| Producer | `7c74a43dfd71acb604862813e0b44de93c0d6c17`, the reviewed head of [PR #642](https://github.com/CIAT/nbs_ruralscan/pull/642) |
| Runtime | [`d63bf3130c3efc165d4048e4b5349134f7b8422f`](https://github.com/RuralScan/runtime/tree/d63bf3130c3efc165d4048e4b5349134f7b8422f) |
| Existing spatial scoring package | `developer-v0.1.5`, source `b356b2af3861bfed6a4c4afc7f25129cca2cdfec` |

Rebuild from the producer revision above. The release records its source commit, and rebuilding from the later squash merge gives it different provenance. The four audit files and the recipe inputs and tables are identical at the tested revision and at merge `87dd923a`.

## Verify both readers

Point `RECIPE_STORE` to the authorised store, `RUNTIME_CHECKOUT` to the tested runtime checkout, and `RUNTIME_PYTHON` to a separate environment with that runtime installed. Run these commands from the producer repository containing this handoff record. Use the bundled pin for the external reader.

```sh
rid=ef2b83d14be8e215857a1ce5ae0fa1b4e403ebeefd17a44cf84d4158679a4c86
proof=methodology/migration/2026-11-05
"$RUNTIME_PYTHON" -I -m nbs_runtime.recipe_release --store "$RECIPE_STORE"
uv run python scripts/check-runtime-recipe-handoff.py \
  --store "$RECIPE_STORE" --release-id "$rid" --runtime-python "$RUNTIME_PYTHON" \
  --legacy-upstream "$RUNTIME_CHECKOUT/upstream" > runtime-handoff.json
diff -u "$proof/m16-runtime-797-handoff.json" runtime-handoff.json
```

A fresh compilation and the installed local copy produced the same receipt. Both readers matched on 24 typed tables, 25 settings, 12 reports and provenance. All three legacy scoring criteria retained their function fingerprints. The previous release still opens with its saved pin. [Build and storage guide](../../../docs/RECIPE_RELEASES.md)

## Carry the depth audits with the release

Copy `audits/<release_id>/` alongside `generations/<release_id>/` when transferring the authorised handoff. The audit directory contains the in-field and microcatchment soil-depth decision, the terrace-depth decision and their two replay records. Original filenames preserve the links between each decision and its replay. The archive retains reviewer metadata and local replay paths.

To restore the four files in a fresh authorised store, use the following commands from this repository, with `rid` and `RECIPE_STORE` set as above.

```sh
producer=7c74a43dfd71acb604862813e0b44de93c0d6c17
source_dir=methodology/audits/t4_water_block_20261109
archive="$RECIPE_STORE/audits/$rid"
checksums="$(pwd)/methodology/migration/2026-11-05/m16-runtime-797-audits.sha256"
mkdir -p "$archive"
git archive "$producer:$source_dir" soil_depth.md soil_depth_run.json \
  terrace_depth.md terrace_depth_run.json | tar -x -C "$archive"
(cd "$archive" && shasum -a 256 -c "$checksums")
```

The four copied files matched the merged originals byte for byte. The three `result_sha256` values in the replay records matched their complete compiled T4 CSV rows. For each row, hash its UTF-8 JSON representation using the CSV strings, sorted keys and compact separators. The in-field and microcatchment rows each retain two source profiles. Terracing retains three design-specific profiles. Each mapping requires a matching soil-depth input and has zero selectable scoring functions. [Audit checksums](m16-runtime-797-audits.sha256)
