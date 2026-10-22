# T4 clarification queue

Open `/review/t4-clarifications.html` on the review server; linked from QA/QC.

The API reconciles current per-reviewer decisions with evidence and tracked source corrections. Identical question text, source, reviewer and reason can share a thread. Different questions remain separate even when they concern the same variable. General-practice scope is the default; species/crop requests remain accessible.

- **Answer ready**: every affected record has a matching tracked answer and all correction field fingerprints still match. Reviewer can accept or reply.
- **Needs investigation**: missing answer, incomplete coverage, stale correction, query, disagreement or status mismatch. Team work, not a new review assignment.
- **Needs your judgement**: an explicitly authored, verified follow-up marked `needs_judgement`. Never inferred merely from a missing answer. User records the decision with Reply; team applies the decision separately.
- **Resolved**: explicit acceptance of the current answer version. Any change to the question, affected records or answer invalidates that acceptance. Reopen/reply remains available.

Acceptance closes only the clarification, not the extraction approval or scientific calibration holds. It does not rewrite `reviewer_ok`, historical decisions or T4. Existing tracked `resolved` corrections become answers awaiting confirmation, not presumed human agreement.

Replies are append-only events in gitignored `pipeline/review/clarifications.json`, protected by a write lock and atomic replacement. Export history from the page for backup/handoff. The normal Apply/submit flow does not publish these events. Local history is a first-pass limitation; multi-reviewer shared storage is not implemented.

Initial reconciliation (22 October 2026): 73 active general-practice records produce 77 threads, with 17 answers ready and 60 requiring investigation. No new judgement requests or user acceptances were invented. This is bounded matching against the tracked follow-up register, not a claim that every chat message or untracked document has been reconciled.
