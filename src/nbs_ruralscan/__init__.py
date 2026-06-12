"""Reusable Python package for the NbS Rural Scan pipeline.

Subpackages group code by what it acts on:

- ``schema_tools`` — build/validate/snapshot the machine-readable schema
  (``structure``, ``generate``, ``freeze``).
- ``recipe``       — build schema *content* from the literature corpus
  (``evidence`` -> ``support`` -> ``synthesis`` -> ``family``).
- ``runtime``      — execute the method on data (``mcda``, ``binding``,
  ``farming_system``; ``schema_loader``/``outputs`` to be authored).
- ``ingest``       — structure-aware document ingestion feeding ``recipe``.
- ``data_loaders`` — Earth Engine / geospatial dataset loaders.

``models`` holds shared type/dataclass definitions used across subpackages.
"""
