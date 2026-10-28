# T4 support reporting: study counts first

**Approved by Pete Steward, 28 October 2026**, in this pipeline review:
“Approve: study counts first; quality weighting separate.”

## Convention

- Headline support is `n_sources / corpus_n`, expressed as n/N and, when N is known
  and positive, a percentage. Each canonical screened source counts once per variable;
  group support uses the union across member variables.
- Quality-weighted support is a separate diagnostic. It requires explicit screened
  membership and known quality tiers for that complete membership. An integer count
  alone cannot establish its denominator; do not impute unseen studies as medium quality.
- Missing denominator means unknown, not zero. Counts describe the declared eligible
  cohort, not all available literature or a systematic-review prevalence claim.
- The low-support decision flag uses the headline percentage. It remains advisory,
  never an automatic exclusion.
- Harmonisation source-quality weights, relative importance within a source model,
  and runtime MCDA weights retain their distinct existing meanings and policies.

## Compatibility and provenance

The existing CSV field `paper_support_pct` carries the headline percentage for new
compilation. No CSV columns are added. The synthesis report exposes the separate
`quality_weighted_pct` diagnostic. Historical files and evidence stamps are not rewritten;
rebuild affected recipes through normal review rather than silently patching old results.

The support API receives source IDs, not bibliographic metadata. Reconcile DOI aliases
and canonical source identity in the screened membership before claiming distinct studies.
Do not treat record counts, citation copies or soil-depth branches as extra studies.
Developer variable-inclusion estimates already use a separately defined DOI-deduplicated
model-use cohort; keep that denominator visible rather than substituting it for screened N.
