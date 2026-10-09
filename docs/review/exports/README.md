# Review exports

Drop an exported review CSV here (the **Export CSV** button on
[the review page](../../review.html)) and commit it. The build then:

* writes `docs/review/decisions.json`, so the review page can show what the **other**
  reviewer decided on the same unit, and the build-progress page can report QA progress
  per NbS;
* leaves the evidence register alone — applying decisions is a separate, deliberate step:

```
python3 scripts/apply-review-export.py docs/review/exports/<file>.csv [--dry-run]
python3 src/nbs_ruralscan/schema_tools/generate.py schema
```

File name is whatever the page produced (`review_<batch>_<reviewer>_<date>.csv`); keep one
file per reviewer per export. Re-exporting later is fine — the newest date per
(unit × reviewer) wins.
