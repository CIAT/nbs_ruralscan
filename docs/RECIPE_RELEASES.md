# Load a complete recipe release

A local recipe release contains T0 and the authored settings for each selected practice, the reconciled T3, T4, T6 and T6E tables in CSV and typed JSON, and the effect synthesis and T4 readiness reports. One release ID identifies all of those files. Use that ID when a calculation or review must be repeatable.

## Build and check

Run these commands in the repository's Python environment. Choose a private local release directory outside the data and compiler checkouts. The example publishes all six registered practices as one release. To publish a subset, repeat `--nbs <practice_id>` for the practices you need. The publisher checks the family registry, settings index and recipe directories agree on that list.

```sh
uv run python -m nbs_ruralscan.recipe.publish_release check --root .
uv run python -m nbs_ruralscan.recipe.publish_release publish --root . \
  --store ../recipe-releases
uv run python -m nbs_ruralscan.recipe.publish_release inspect --store ../recipe-releases
```

The publisher copies the declared inputs, compiles the full practice corpus and checks the output against its audited tables before selecting a release. Stale typed evidence, a missing definition, a changed approved function fingerprint or a table mismatch stops publication of the whole requested set. The command reports practice-specific holds. A header-only table is included with zero rows. The readiness report retains unresolved scientific or implementation decisions.

The [first six-practice release](../methodology/migration/2026-11-05/m08-recipe-releases.md#first-six-practice-release-9-november-2026) lists the table counts and scientific holds by practice. Mangrove establishment time, benefit timing and recurrent cost class need local values before operational use. Water-harvesting rows retain six calibration decisions with no selectable functions.

Each successful publish selects exactly the requested set as the directory's current release. Earlier release IDs remain available. Identical content and provenance yield the same ID. Use separate store directories for collections that need independent current selections.

## Read one version

```python
from pathlib import Path

from nbs_ruralscan.runtime.effect_rows import load_rows
from nbs_ruralscan.runtime.schema_loader import load_recipe_release

release = load_recipe_release(Path("../recipe-releases"))
print(release.release_id, release.practices)
agroforestry = release.table("agroforestry", "T4")
scorecards = load_rows(release, "T6")
settings_csv = release.setting("agroforestry", "T4_run_policy.csv")

# Later, reopen the recorded ID even after a newer publication.
same = load_recipe_release(Path("../recipe-releases"), release.release_id)
```

Opening a release verifies its complete file inventory, hashes, table formats, row identities, authored settings and readiness reports. Keep the returned handle for the duration of a read. The provenance file records the source revision when available, content hashes for the selected source files, and fingerprints of the compiler source. The byte hashes also identify inputs in a data-only checkout.

## Maintain settings

Authored T4 gates, mapping defaults, scenario settings and reviewed holds are maintained in the declared inputs. T0 practice identity, T4 run policy and effect prose have their own files. Generated recipe tables remain available to existing checkout readers. [T4 input layout and editing workflow](../schema/recipe_inputs/t4/README.md)

This release format covers per-practice recipe data for internal review and handoff. Shared T1, T2, T5 and T7 method definitions and the runtime environment have their own versioning and acceptance work. Scientific acceptance, permission to redistribute source material, spatial execution and the external runtime's package pin have separate checks. Store releases on a local filesystem. Concurrent readers and publishers can use the same store. Process interruption can leave a complete unselected generation or temporary staging directory. Repeating the publish checks and reuses matching content.
