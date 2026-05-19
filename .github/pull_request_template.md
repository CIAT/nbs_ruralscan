# Pull Request

## Summary

<!-- One paragraph: what does this PR do, and why? -->

## Type of change

- [ ] New NbS recipe
- [ ] Update to existing recipe / Variable Card
- [ ] Module spec sheet
- [ ] Pilot notebook / pilot output
- [ ] Pipeline / GEE Python code
- [ ] Schema (T0–T7) change
- [ ] Wireframe / pipeline diagram edit
- [ ] Documentation / playbook
- [ ] Methodology framework
- [ ] Other (specify):

## Structural checklist

Tick all that apply. **If anything is unchecked, explain in the comments.**

### For all PRs
- [ ] Conventional Commits used in commit messages
- [ ] No analytical rules hardcoded in code — all read from schema (T0–T7)
- [ ] CLAUDE.md updated if a structural decision changed

### For wireframe / docs edits
- [ ] Six-tab structure preserved (Setup · Opportunity Space · NbS Comparison · TTL Hotspots · Variable Config · Danger Zone)
- [ ] Variable Card six-slot structure preserved
- [ ] T0–T7 colour scheme preserved (matches ERD)
- [ ] Cluster + GEE/upload badges on variable chips preserved
- [ ] Sierra Leone / agroforestry mock data preserved (or coordinated update across all artefacts)
- [ ] Tested locally — opens cleanly in browser

### For recipe / Variable Card edits
- [ ] Master variable table follows the six-theme structure (topographic · climatic · soil · LULC · socio-econ · hazard)
- [ ] Variables grouped thematically; correlation clusters identified
- [ ] Dataset hosting status filled (native_gee / community_gee / requires_upload)
- [ ] All Variable Cards have six slots populated
- [ ] References cited

### For pipeline / Colab notebook edits
- [ ] Pipeline reads from schema, never hardcoded
- [ ] Cell markdown documents each step in plain language
- [ ] Hand-off to WB technical team would not require explanation
- [ ] Reproducible — runs from a clean Colab environment

### For schema (T0–T7) changes
- [ ] ERD updated if relationships changed
- [ ] Existing data still validates
- [ ] T0–T7 cross-references checked

## Review

- [ ] One reviewer assigned (content) OR
- [ ] Pete + one reviewer assigned (structural / methodology)
- [ ] Issue linked (e.g. `Closes #42`)

## Notes / context

<!-- Anything reviewers should know that isn't in the diff. References, screenshots, follow-ups, etc. -->
