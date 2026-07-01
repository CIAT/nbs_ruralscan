"""One module per dataset, named for its ``dataset_id``. Dispatched by ``core.load``.

Each module exposes ``load(target, ...)`` declaring exactly the kwargs it accepts — no
catch-all ``**kw``, so a typo'd or unknown kwarg fails loud rather than being silently
swallowed. The ``target`` is an ``AOI`` (native bbox/polygon extract — the default) or an
``odc.geo.GeoBox`` (also reproject onto an MCDA grid); ``read_raster``/``ee_to_xarray``/
``to_target`` handle both, so a loader is usually one line and mode-agnostic. Shared fetch
logic for related datasets goes in a ``_``-prefixed helper module (skipped by dispatch +
the contract test).

Resampling method is the loader's responsibility, not the grid's — pass ``resampling=`` to
``read_raster`` / ``ee_to_xarray`` / ``to_target`` to match the data's measurement type. It
applies only in the GeoBox (reproject) case. The default (``bilinear``) suits continuous
data; **categorical** loaders (land cover, AEZ, masks) MUST override (``nearest`` / ``mode``)
and **fractional** cover with ``average`` — bilinear-interpolating class codes is meaningless.
"""
