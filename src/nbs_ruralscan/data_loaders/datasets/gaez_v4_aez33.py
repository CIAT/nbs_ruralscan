"""FAO-IIASA GAEZ v4 33-class Agro-Ecological Zones (T1: gaez_v4_aez33).

Single global COG of nominal AEZ class codes (1–33; 0 = nodata) at ~10 km (5 arc-min),
EPSG:4326. Streamed via GDAL /vsicurl/ — it's tiled + overviewed, so only the AOI tiles
transfer (and it's ~1 MB regardless), no download/persist needed. Classes are nominal,
so resample with ``nearest`` (never bilinear — interpolating class codes is meaningless).

Returns raw codes; decode names via the ``gaez_aez33`` codelist
(``schema/codelists/gaez_aez33.csv``, routed by ``dataset_id`` in ``runtime/codelist.py``).
"""

from __future__ import annotations

from ..core import AOI, GeoBox, read_raster

_URL = "https://s3.eu-west-1.amazonaws.com/data.gaezdev.aws.fao.org/LR/aez/aez_v9v2red_5m_CRUTS32_Hist_8110_100_avg.tif"


def load(target: AOI | GeoBox):
    return read_raster(_URL, target, resampling="nearest")  # categorical AEZ classes
