# v1.6.9 addendum — `context.practice_as_described` (extraction contract §2.3)

**Ratified:** Pete, 2026-10-12 (review theme 2, `methodology/decisions/2026-10-12_review_themes.md`).
**Applies to:** every `nbs_effect` and `asset_vulnerability` unit extracted under v1.6.9 or later.
Units under v1.6.0–v1.6.8 stay valid and are **not** re-stamped or retro-filled.

## Why

Whole classes of wrong tags got through review because the practice test was inferred from our
own tag instead of read from the paper: supplemental irrigation counted as water harvesting,
a plantation counted as forest restoration, protected areas counted as restoration, a farm pond
whose water was used for irrigation counted as water harvesting. Pete asked for the fix directly:

> "it would be good if the extract could capture the description of the NbS in question from the evidence."

## The field

| Key | Value | Fill from |
|---|---|---|
| `practice_as_described` | free text, the SOURCE's own words for what was done | the paper's methods / intervention description, not our vocabulary |

Rules:

1. **The source's words, not ours.** "planting basins dug in the dry season and filled with
   manure", not "in-situ water harvesting". Quote-like, one sentence; a verbatim fragment is
   ideal but it is not held to the verbatim gate (it is a description, not a claim).
2. **Write what was actually done to the land**, including anything applied alongside the
   practice (fertiliser, irrigation, improved seed) — that is exactly what the reviewer needs
   to judge whether the thing measured is the NbS.
3. **If the source never describes the intervention**, say so in the field
   (`"not described beyond the label 'conservation agriculture'"`) rather than leaving it blank —
   a blank reads as an extraction omission.
4. It is **context**, so it goes in the `context` object, never in `relationship`.

## Checks

`check_context.py` adds `missing_practice_description` (advisory), raised only when the unit's
`ruleset_version` is **v1.6.9 or later** — no retrospective sweep over the existing register.
The review page prints the field under the practice line, and in the PICOS **I** row, with a
standing prompt to judge the practice from the quote when it is absent.
