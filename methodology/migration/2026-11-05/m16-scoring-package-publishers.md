# Scoring package publisher verification

The runtime can fetch `developer-v0.1.5` from either of the two GitHub locations below. Both served identical bytes for all seven package files. CIAT remains the source for the scoring package. The RuralScan copy verifies that a consumer can switch origins and preserve prior results. [Runtime change](https://github.com/RuralScan/runtime/pull/2) · [Verified implementation](https://github.com/RuralScan/runtime/tree/d41f10f419820e63bc2e1c7a4d009314455d27e2)

| Publisher | Package root | Tested commit |
|---|---|---|
| CIAT/nbs_ruralscan | `handoff/` | [b356b2af](https://github.com/CIAT/nbs_ruralscan/tree/b356b2af3861bfed6a4c4afc7f25129cca2cdfec/handoff/agroforestry-t4/developer-v0.1.5) |
| RuralScan/runtime | `upstream/` | [e690d4e4](https://github.com/RuralScan/runtime/tree/e690d4e413d925c28c273945a5268ddbfb2d67cc/upstream/agroforestry-t4/developer-v0.1.5) |

## Reproduce the switch

Run from the verified runtime checkout with its test dependencies installed. Use a fresh scratch directory for the local store.

```sh
store=$(mktemp -d)
package=agroforestry-t4/developer-v0.1.5
python scripts/sync_upstream.py --package "$package" --upstream "$store" \
  --ref b356b2af3861bfed6a4c4afc7f25129cca2cdfec
python scripts/sync_upstream.py --check --upstream "$store"
python scripts/sync_upstream.py --repo RuralScan/runtime --source-root upstream \
  --package "$package" --upstream "$store" --ref e690d4e413d925c28c273945a5268ddbfb2d67cc
python scripts/sync_upstream.py --check --upstream "$store"
```

The selected publisher and commit changed in the scratch store. The seven file hashes stayed identical. Separate clean runtime checkouts using each downloaded package passed 65 tests each across conformance, policy, planning and raster behavior. These included all 40 response and host-gate examples and six policy examples. The complete runtime suite passed 292 tests.

An independently installed runtime wheel also passed the [799-row recipe handoff](m16-runtime-799-handoff.md#verify-both-readers) with each store supplied to `--legacy-upstream`. Both receipts contained the same six practices, 62 compared values, digest `8f2289813460e078dadd04a78d00687e251ea2e79f71a7409087577fa861f840` and three matched scoring criteria. Only the scoring publisher commit recorded in the receipt differed.

The runtime tests also cover interrupted downloads, incomplete manifests, an unsupported contract, duplicate rule identifiers and changed bytes under an installed version. The next M16 step is to give public runtime and notebook identifiers neutral names with compatibility for existing callers. The upgrade to scoring package v0.1.7 has its own M17 review.
