# NbS Rural Scan

Methodology and demonstrator for spatial prioritisation of Nature-based Solutions in rural, agricultural, and forestry landscapes. Funded by the World Bank (D591). Implemented by Alliance Bioversity International & CIAT.

> ⚠ **Status:** v0 work-in-progress. Mock data only. Not yet a production decision tool.

## What this is

A scoping and decision-support framework that helps World Bank Task Team Leaders (TTLs) identify where different Nature-based Solutions could be invested in, how extensive the opportunity is, and which TTL priorities (poverty, biodiversity, climate risk, gender equity) intersect that opportunity space. Outputs are reproducible Jupyter/Colab notebooks plus an interactive demonstrator UI.

## Live demonstrator

**https://ciat.github.io/nbs_ruralscan/**

Includes:
- **TTL Tool Wireframe** — interactive mockup of the decision-support tool
- **Pipeline Architecture** — one-page methodology architecture diagram

Both use mock Sierra Leone / agroforestry data.

## Repo structure

| Folder | Contents |
|---|---|
| `docs/` | GitHub Pages — live demonstrators |
| `methodology/` | Cross-cutting framework + per-NbS recipes |
| `schema/` | T0–T7 schema tables and reference (ERD) |
| `pipeline/` | GEE Python implementation + pilot Colab notebooks |
| `reference/` | Stocktake findings, source R scripts, literature references |
| `.claude/` | Project memory and slash commands for Claude Code |
| `.github/` | Issue templates and PR template |

## Contributing

Workflow is documented in [PLAYBOOK.md](./PLAYBOOK.md). Project memory for Claude Code lives in [CLAUDE.md](./CLAUDE.md). Open an issue using one of the templates; raise a PR using the PR template; we review and merge.

## Team

Alliance Bioversity International & CIAT — Climate Action Net Zero. Pete Steward (Team Lead, p.steward@cgiar.org). Full team in [CLAUDE.md](./CLAUDE.md#team--roles).

## License

See [LICENSE](./LICENSE).
