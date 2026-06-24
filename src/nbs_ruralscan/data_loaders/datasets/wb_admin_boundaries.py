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
# ISO3 country code (uppercase) — the schema convention (spec.md). The WB admin-0 file
# carries it as `ISO_A3` (clean ISO3); NOT `WB_A3`, which deviates (ROM/DRC/TMP, NaNs).
_ISO_COLS = ("ISO_A3", "ISO3", "iso3", "ISO3166_1_Alpha_3")


def _partition(level: int) -> Path:
    return _STORE / f"admin_level={level}" / "boundaries.parquet"


def _build(level: int) -> Path:
    """Download one level's GeoPackage and convert to sorted, bbox-covered, zstd GeoParquet."""
    out = _partition(level)
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
        col = next((c for c in _ISO_COLS if c in gdf.columns), None)
        if col is None:
            raise ValueError(
                f"no ISO3 column in admin{level}; columns: {list(gdf.columns)}"
            )
        wanted = {region} if isinstance(region, str) else set(region)
        wanted = {r.upper() for r in wanted}
        unknown = wanted - set(gdf[col].astype(str).str.upper())
        if unknown:
            raise ValueError(
                f"unknown {col} code(s) in admin{level}: {sorted(unknown)}"
            )
        gdf = gdf[gdf[col].astype(str).str.upper().isin(wanted)]
    return gdf
