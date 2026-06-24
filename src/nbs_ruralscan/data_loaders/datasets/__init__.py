"""One module per dataset, named for its ``dataset_id``. Dispatched by ``core.load``.

Each module exposes ``load(grid, ...)`` declaring exactly the kwargs it accepts — no
catch-all ``**kw``, so a typo'd or unknown kwarg fails loud rather than being silently
swallowed. Shared fetch logic for related datasets goes in a ``_``-prefixed helper module
(skipped by dispatch + the contract test).
"""
