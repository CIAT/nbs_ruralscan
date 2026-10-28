# Reproduce the restoration T4 first pass

Run from repository root with the project Python environment (`uv run python`, or `.venv/bin/python` with `PYTHONPATH=src`). Hydrate the team corpus first using `docs/HYDRATION.md`. PDFs remain outside Git. Preserve artifact hashes from the source manifests.

## Re-extract the bounded source claims into staging

```sh
PYTHONPATH=src uv run python pipeline/t4_audit/forest_restoration/first_pass_2026-10-28/extract.py
PYTHONPATH=src uv run python pipeline/t4_audit/mangrove_restoration/first_pass_2026-10-28/reproduce.py --corpus .cache/corpus
PYTHONPATH=src uv run python scripts/ingest-effects-staging.py pipeline/staging/forest_t4_20261028/evidence_staging.json pipeline/staging/mangrove_t4_20261028/units.json --dry-run --allow-structural --allow-operational
```

The checked-in staging snapshots record the admitted source reading. Existing IDs are not overwritten. For this snapshot the dry-run is expected to refuse an existing row whose attribution changed during the audited reopen; this is the history-preservation guard, not a request to overwrite it. Compare staged claim fields with the stored snapshot, and use the correction/review path for any intentional change. Do not rerun without `--dry-run` to modify a prior record: corrections require the audited correction/review path. The historical first-pass inventories and review-history searches are snapshots, not current live counts.

## Trial and authoritative compilation

```sh
PYTHONPATH=src uv run python scripts/synthesise-recipe.py forest_restoration --output-dir pipeline/staging/forest-reviewed-trial
PYTHONPATH=src uv run python scripts/synthesise-recipe.py mangrove_restoration --output-dir pipeline/staging/mangrove-reviewed-trial
```

Inspect trial outputs and dispositions. A new reviewed numeric row changes this release's zero-calibration assumption and requires a new audit. Unreviewed diagnostic runs require `--include-unreviewed` and an isolated staging output; their old-style candidate parameters are not approved source profiles or policy. Never copy them to the live recipe.

After reviewing the diff:

```sh
PYTHONPATH=src uv run python scripts/synthesise-recipe.py forest_restoration
PYTHONPATH=src uv run python scripts/synthesise-recipe.py mangrove_restoration
PYTHONPATH=src uv run python scripts/report-restoration-t4-first-pass.py
uv run python src/nbs_ruralscan/schema_tools/generate.py schema
PYTHONPATH=src uv run python scripts/build-t4-dashboard.py
PYTHONPATH=src uv run python scripts/build-t4-dashboard.py --nbs forest_restoration
PYTHONPATH=src uv run python scripts/build-t4-dashboard.py --nbs mangrove_restoration
```

## Developer packages and verification

Choose new, empty output directories. Packages are generated snapshots, not a new review interface.

```sh
PYTHONPATH=src uv run python scripts/build-t4-developer.py --nbs forest_restoration --output handoff/forest-restoration-t4-first-pass-v1
PYTHONPATH=src uv run python scripts/build-t4-developer.py --nbs mangrove_restoration --output handoff/mangrove-restoration-t4-first-pass-v1
PYTHONPATH=src uv run python scripts/build-t4-developer.py --verify handoff/forest-restoration-t4-first-pass-v1
PYTHONPATH=src uv run python scripts/build-t4-developer.py --verify handoff/mangrove-restoration-t4-first-pass-v1
uv run ruff check .
uv run ruff format --check .
uv run ty check src/nbs_ruralscan/schema_tools/structure.py src/nbs_ruralscan/runtime/binding.py
uv run pytest -q
uv run python src/nbs_ruralscan/schema_tools/generate.py schema --check
uv run python src/nbs_ruralscan/schema_tools/structure.py schema
PYTHONPATH=src uv run python -m nbs_ruralscan.schema_tools.t4_coverage
```

No target country, runtime aggregation or weight vector is selected. No spatial execution is implied. Dataset candidates need consumer-side fitness checks; source guidance needs remaining review and transfer decisions.
