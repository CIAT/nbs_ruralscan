"""World Bank Official Administrative Boundaries (Admin 0 / 1 / 2).

Vector loader. The three source GeoPackages are downloaded once and converted into a
GeoParquet store under ``DATA_DIR/wb_admin_boundaries/`` — partitioned by admin level
(one partition each), Hilbert-sorted so row groups are spatially coherent, with a covering
bbox column for spatial-predicate pushdown, zstd-compressed. ``load`` then reads the
requested level, optionally filtered to a region (ISO3 country code).
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd

from ..core import DATA_DIR, download

_URLS = {
    0: "https://datacatalogfiles.worldbank.org/ddh-published/0038272/2/DR0095370/World%20Bank%20Official%20Boundaries%20%28GeoPackage%29/World%20Bank%20Official%20Boundaries%20-%20Admin%200.gpkg",
    1: "https://datacatalogfiles.worldbank.org/ddh-published/0038272/2/DR0095370/World%20Bank%20Official%20Boundaries%20%28GeoPackage%29/World%20Bank%20Official%20Boundaries%20-%20Admin%201.gpkg",
    2: "https://datacatalogfiles.worldbank.org/ddh-published/0038272/2/DR0095370/World%20Bank%20Official%20Boundaries%20%28GeoPackage%29/World%20Bank%20Official%20Boundaries%20-%20Admin%202.gpkg",
}
_STORE = DATA_DIR / "wb_admin_boundaries"
# WB admin files carry clean ISO3 here (uppercase, the schema convention). NOT WB_A3,
# which deviates for disputed territories (ROM/DRC/TMP) and has NaNs.
_ISO_COL = "ISO_A3"


def _build(level: int) -> Path:
    """Download one level's GeoPackage; convert to sorted, bbox-covered, zstd GeoParquet."""
    out = _STORE / f"admin_level={level}" / "boundaries.parquet"
    if out.exists():
        return out
    gdf = gpd.read_file(download(_URLS[level], name=f"wb_admin{level}.gpkg"))
    gdf = gdf.iloc[gdf.geometry.hilbert_distance().argsort()].reset_index(drop=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(out, compression="zstd", write_covering_bbox=True)
    return out


def load(
    grid=None, level: int = 0, region: str | list[str] | None = None, **kw
) -> gpd.GeoDataFrame:
    gdf = gpd.read_parquet(_build(level))
    if region:
        if _ISO_COL not in gdf.columns:
            raise ValueError(
                f"no {_ISO_COL} in admin{level}; columns: {list(gdf.columns)}"
            )
        wanted = (
            {region.upper()} if isinstance(region, str) else {r.upper() for r in region}
        )
        codes = gdf[_ISO_COL].astype(str).str.upper()
        unknown = wanted - set(codes)
        if unknown:
            raise ValueError(
                f"unknown {_ISO_COL} code(s) in admin{level}: {sorted(unknown)}"
            )
        gdf = gdf[codes.isin(wanted)]
    return gdf
