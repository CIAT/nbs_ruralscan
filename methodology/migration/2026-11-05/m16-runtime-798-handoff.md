# Runtime handoff for the 798-row release

The six-practice release contains 288 T3, 42 T4, 394 T6 and 74 T6E rows. All 797 previous rows retained their values and order. The only addition is the water-harvesting terrace-slope mapping. [Previous handoff](m16-runtime-797-handoff.md) · [Verification receipt](m16-runtime-798-handoff.json)

| Component | Tested version |
|---|---|
| Analytical release | `d336eba5cf9b79ee1b5d5db7a28ee589c87841656ea621548576b3e667dc8332` |
| Producer | `10e1e463973ba873b7017a7a33015c942dd0915d`, the final reviewed head of [PR #643](https://github.com/CIAT/nbs_ruralscan/pull/643) |
| Runtime | [`bebce6010d2abfb6520d2d05f703ab8f756b775f`](https://github.com/RuralScan/runtime/tree/bebce6010d2abfb6520d2d05f703ab8f756b775f) |
| Spatial scoring package | `developer-v0.1.5`, source `b356b2af3861bfed6a4c4afc7f25129cca2cdfec` |

Rebuild from the recorded producer commit. Its file tree matches the squash merge at `5cbb1775`. The source commit is part of the release ID.

## Readiness

The terrace-slope mapping retains five profiles in the units reported by each source. Four support terrace siting. The contour stone-line profile remains available as contextual evidence and is excluded from terrace scoring and the support count. The slope dataset `srtm_dem_30m` is available. Calibration is held, with zero selectable functions. All 12 water-harvesting T4 rows require calibration, including eight that also need a matching spatial input. All six practices report `execution_ready=false`. [Terrace-slope decision](../../audits/t4_water_block_20261109/terrace_slope.md) · [Run record](../../audits/t4_water_block_20261109/terrace_slope_run.json)

## Verify both readers

Set `RECIPE_STORE` to the authorised store, `RUNTIME_PYTHON` to a separate environment with the recorded runtime installed, and `RUNTIME_CHECKOUT` to its checkout. From the repository containing this handoff record, run the installed reader with its bundled pin and compare its complete output with the producer.

```sh
rid=d336eba5cf9b79ee1b5d5db7a28ee589c87841656ea621548576b3e667dc8332
proof=methodology/migration/2026-11-05
"$RUNTIME_PYTHON" -I -m nbs_runtime.recipe_release --store "$RECIPE_STORE"
uv run python scripts/check-runtime-recipe-handoff.py \
  --store "$RECIPE_STORE" --release-id "$rid" --runtime-python "$RUNTIME_PYTHON" \
  --legacy-upstream "$RUNTIME_CHECKOUT/upstream" > runtime-handoff.json
diff -u "$proof/m16-runtime-798-handoff.json" runtime-handoff.json
```

The clean build and the installed local copy produced the same receipt. The offline comparison covered all 24 typed tables, 25 settings, 12 reports and provenance. All three legacy scoring criteria matched their function fingerprints. The previous pin still opened the 797-row release. Substituting its water-harvesting T4 table into the new generation caused the reader to reject the transfer. [Release build guide](../../../docs/RECIPE_RELEASES.md)

## Transfer the audit records

Copy `audits/<release_id>/` alongside `generations/<release_id>/` in the authorised handoff. The audit directory contains the soil-depth, terrace-depth and terrace-slope decisions with their three replay records. All six originals matched the merged source files byte for byte. All four row fingerprints in the replay records matched the corresponding compiled T4 CSV rows.

To restore the six files in a fresh authorised store, use the following commands from this repository with `rid` and `RECIPE_STORE` set as above.

```sh
producer=10e1e463973ba873b7017a7a33015c942dd0915d
source_dir=methodology/audits/t4_water_block_20261109
archive="$RECIPE_STORE/audits/$rid"
checksums="$(pwd)/methodology/migration/2026-11-05/m16-runtime-798-audits.sha256"
mkdir -p "$archive"
git archive "$producer:$source_dir" soil_depth.md soil_depth_run.json \
  terrace_depth.md terrace_depth_run.json terrace_slope.md terrace_slope_run.json \
  | tar -x -C "$archive"
(cd "$archive" && shasum -a 256 -c "$checksums")
```
