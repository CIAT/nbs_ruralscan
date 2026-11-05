# Wetland T4 review priority handoff

Pete requested priority human review of six claims supporting live wetland mappings on 2026-11-05. No approval or removal was authorised.

The accompanying JSON preserves the source task’s handoff verbatim (SHA256 17c391c135e61ede83452baac53a0d746691690e861cce15e7c384177cf24ae1). The dashboard annotation source is `pipeline/review_priorities.csv`; it does not add columns to frozen evidence registers. Each request pins evidence semantics with an SHA256 fingerprint. Changed evidence receives a visible context warning, without blocking continued review.

Priority is triage metadata, independent of Keep/Drop/Query, extraction approval, source credibility and runtime readiness. Current review state determines the queue; priority never reopens, approves, drops or regenerates anything. Requested mapping decisions need the normal review and separate implementation process.

In Evidence review, select a priority batch to reset scope to its records. To review, Waiting for answers and My reviewed retain their existing meanings. The batch index also links directly to every native card, including settled or dropped history, without reopening records.

To add a batch, append CSV rows with a unique batch ID and existing evidence IDs, source/page, priority (`high` or `normal`), requester/date, reason, decision needed and `evidence_fingerprint` from `schema_tools.review_notes`. Regenerate the dashboard payload; do not hand-edit its JSON. Retire completed requests through a reviewed CSV change, not an inferred approval flag.
