"""Recipe engine — build schema *content* (T3/T4/T5/T6 rows) from the literature corpus.

Evidence-first pipeline: ``evidence`` (extract units) -> ``support`` (aggregate
per-paper support) -> ``synthesis`` (synthesise enriched rows) -> ``family``
(assemble + save a suitability family). See ``methodology/T4_generation_method.md``.
"""
