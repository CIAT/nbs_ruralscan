---
name: Module Spec
about: Draft or update a module spec sheet (one of M0–M6)
title: "[Module Spec] M<n> <module name>"
labels: ["module-spec", "methodology"]
assignees: []
---

## Module

**ID:** <!-- M0 · M1 · M2 · M3 · M4 · M5 · M6 -->
**Name:** <!-- e.g. Suitability → Opportunity Space -->
**Owner(s):** <!-- e.g. @benson @namita -->
**Status:** <!-- todo · partial · done -->

## Purpose

<!-- One paragraph: what does this module do, what question does it answer for the TTL, where does it sit in the pipeline. -->

## Inputs

| Input | Provenance | Schema table | Notes |
|---|---|---|---|
| <!-- e.g. Suitability variables --> | <!-- e.g. Namita's recipe --> | <!-- T4 --> | |

## Outputs

| Output | Format | Consumer | Notes |
|---|---|---|---|
| <!-- e.g. Continuous suitability raster --> | <!-- GeoTIFF, 1km --> | <!-- M3, M4, wireframe --> | |

## Dependencies

- Upstream modules required before this can run:
- Downstream modules that consume this module's outputs:

## Sub-steps

<!-- 3-8 named steps inside the module. Each step has its own I/O. -->

1. **Step name** — what happens, with which inputs, producing what
2. ...

## Variable Cards consumed

<!-- List variables this module reads, with their cluster representatives if applicable. -->

## Tests / acceptance criteria

- [ ] Reads from schema, never hardcoded
- [ ] Outputs validate against schema
- [ ] Reproducible from clean environment
- [ ] (Module-specific criteria)

## Definition of done

- [ ] Spec written
- [ ] Reviewed by Pete + one team member
- [ ] Implementation issue linked
- [ ] PR raised with spec file
