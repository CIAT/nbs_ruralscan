# Six-practice runtime handoff, 9 November 2026

An independently installed RuralScan runtime read the pinned six-practice release offline. Both readers returned the same 792 analytical rows, authored settings, reports and provenance. This check establishes compatibility for inspection. Spatial execution still uses the existing agroforestry developer package. [Runtime change](https://github.com/RuralScan/runtime/pull/1) · [Verification receipt](m16-runtime-recipe-handoff.json)

## Tested versions

| Component | Pinned value |
|---|---|
| Analytical release SHA-256 | `72a7bddff4778880cbe281117a9fda638a06eb23f624c2e7469d698ae859c507` |
| Producer source revision | `3eab299d33eae3482e0da9312edee5bd98858d04` |
| External runtime revision | [`cbed792537fd0436f8c14a372da02b73114f3189`](https://github.com/RuralScan/runtime/tree/cbed792537fd0436f8c14a372da02b73114f3189) |
| Local release format / analytical schema / T4 readiness contract | `1` / `0.4.0-structure-frozen` / `0.2.0` |
| Existing agroforestry scoring package | `developer-v0.1.5`, source `b356b2af3861bfed6a4c4afc7f25129cca2cdfec` |

The producer revision is the head of PR #636. Its tree and the squash merge at `f75e54c7` are identical. Provenance includes the commit ID, so use the recorded producer revision to reproduce the release ID. A clean compilation of that revision reproduced the 87-file generation, including fingerprints for 102 input files and 51 compiler files. [Producer change](https://github.com/CIAT/nbs_ruralscan/pull/636)

## Repeat the comparison

1. Build or obtain an authorised local copy of the exact generation. When transferring, copy `generations/<release_id>/manifest.json` and its complete sibling `files/` tree under the destination store. The external reader opens the named generation directly. The public runtime package contains the pin and reader. Keep analytical files in the authorised store.
2. In a checkout of the external runtime revision listed above, install a wheel into a separate Python environment. For example, run `python3 -m venv /path/to/runtime-env`, then `/path/to/runtime-env/bin/python -m pip install .` from the runtime checkout. Record the installed interpreter path as `RUNTIME_PYTHON` and the absolute path to that checkout as `RUNTIME_CHECKOUT`. Keep the producer package out of this environment. Set `RECIPE_STORE` to the local store directory.
3. From this repository, run the inspection and compare both readers. The second command runs the external reader in isolation with networking disabled for that process. The resulting JSON can be compared directly to the committed receipt.

```sh
RELEASE_ID=72a7bddff4778880cbe281117a9fda638a06eb23f624c2e7469d698ae859c507
"$RUNTIME_PYTHON" -I -m nbs_runtime.recipe_release --store "$RECIPE_STORE"
uv run python scripts/check-runtime-recipe-handoff.py \
  --store "$RECIPE_STORE" --release-id "$RELEASE_ID" \
  --runtime-python "$RUNTIME_PYTHON" --legacy-upstream "$RUNTIME_CHECKOUT/upstream" \
  > runtime-handoff.json
diff -u methodology/migration/2026-11-05/m16-runtime-recipe-handoff.json runtime-handoff.json
```

To rebuild the original generation, fetch `refs/pull/636/head` in an authorised producer checkout, check out `3eab299d33eae3482e0da9312edee5bd98858d04` in a clean directory, then run `uv run python -m nbs_ruralscan.recipe.publish_release publish --root . --store "$RECIPE_STORE"` there. Use a fresh store for this comparison. Run the handoff script from the checkout that contains it. [Release build and storage guide](../../../docs/RECIPE_RELEASES.md)

## Acceptance results

- Both readers agreed on all 24 typed tables (288 T3, 36 T4, 394 T6 and 74 T6E rows), 25 settings, 12 reports and provenance. The comparison covers row order, JSON scalar types and raw settings bytes. [Counts by practice and comparison digest](m16-runtime-recipe-handoff.json)
- Every practice reported `execution_ready=false`. Forest, mangrove and riparian each loaded a valid empty T4. Water harvesting retained six calibration holds with zero selectable functions, including four that also require matching inputs. The existing agroforestry policy retained its three criterion IDs and function fingerprints. [Release interpretation](m08-recipe-releases.md#first-six-practice-release-9-november-2026)
- A copy containing only the named generation opened successfully, including with a malformed current pointer. On a disposable copy, one altered byte, one absent table, a wrong source revision and a truncated practice list each stopped the read. A newly hashed generation with inconsistent CSV and JSON or an unsupported schema also failed. Restoring the original bytes restored the read.
- In the temporary store, publishing revision `9e8587b6` advanced the current pointer to `987b6c3c4b9e74c2bb1b44632c6f8bd0e140e874b74340f82bb499fd7685aaee`. The installed default still read the original six water-harvesting T4 rows and reproduced the complete receipt. Passing a separate test pin for the newer generation returned eight water-harvesting T4 rows. [Later water-harvesting review](https://github.com/CIAT/nbs_ruralscan/pull/640)
- The previous runtime revision passed all 200 baseline tests. The handoff revision passed 281 tests with geospatial dependencies, its legacy package integrity check and eight installed-package checks. The producer passed 81 release-store, reader and publication tests.

Evidence review can continue on the existing working repository. A later compilation receives its own ID and needs a compatibility comparison before the runtime adopts its pin. Public redistribution, adoption of a newer developer scoring package and end-to-end spatial validation remain separate migration steps.
