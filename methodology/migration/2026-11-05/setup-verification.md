# Organization and runtime copy verification

Completed 5 November 2026, following Pete's confirmation of account defaults and action-time approval to accept GitHub's terms.

| Item | Verified result |
|---|---|
| Organization | [RuralScan](https://github.com/RuralScan), display name Rural Scan |
| Plan | GitHub Free, confirmed through authenticated organization metadata |
| Initial owner | peetmate; active organization admin/owner membership |
| Contact | P.Steward@cgiar.org, as approved in setup |
| Default repository permission | Read; no additional members or teams invited |
| Source | [dagudelo30/nbs-ruralscan-runtime](https://github.com/dagudelo30/nbs-ruralscan-runtime) |
| Destination | [RuralScan/runtime](https://github.com/RuralScan/runtime), public |
| Copy mode | GitHub fork; parent metadata points to Diego's source repository |
| Source and destination HEAD | `78fba87d88a6f1d1a308e06632fb7fec76032696` |
| Advertised branch refs | Both have `refs/heads/main` at that same commit |
| Advertised tag refs | None on either repository at verification |
| Runtime changes | None. Identical commit preserves the tree, history and contributor attribution. |
| Existing integration | CIAT package pin, Python package/import names and external data-host references preserved |
| Original repositories | No changes to either Diego repository |

The GitHub page visibly identifies the destination as public and forked from Diego. Independent authenticated metadata and Git remote-ref checks confirm the same result. The original runtime's latest inspected CI passed; no new runtime implementation or new fork workflow run is claimed. Matching commits preserve its tested baseline and pinned files.

This is an unchanged staging copy, not a declaration that Diego has moved his daily work or that all migration gates passed. Next governance work: agree canonical runtime work location with Diego; establish owner recovery and appropriately scoped maintainer access; configure repository review protections; record external deployment/secret/issue metadata; resolve the missing runtime reuse license before a reusable release or World Bank handover. Do not infer permission to grant new access from this verification record.

The older `dagudelo30/nbs-ruralscan` repository remains separate and has only been assessed. Method and evidence repositories have not yet been populated; their curated migration follows the [execution plan](README.md) and [task board](execution-board.csv).
