# Reference Material — Source & Attribution

The files in this `reference/` directory are **extracted, unmodified, for study and
demo purposes** from the upstream open-source project:

- **Project:** DESIGN.md (Google Labs / Stitch)
- **Repository:** https://github.com/google-labs-code/design.md
- **Snapshot:** `main` branch, downloaded 2026-06-21 (zip commit `2a19f5d`)
- **License:** Apache License 2.0 — see [`LICENSE`](./LICENSE)

These are **not** original work in this repo. They are cherry-picked from a full
clone (kept locally as a git-ignored zip) so this project can be developed offline
against the real spec, lint rules, and worked examples.

## What was extracted

| Path | Upstream path | Purpose |
|:-----|:--------------|:--------|
| `spec.md` | `docs/spec.md` | Full DESIGN.md format specification (alpha) |
| `rules/` | `packages/cli/src/linter/linter/rules/` | The lint rules (+ tests) our reverse-engineered DESIGN.md is validated against |
| `examples/atmospheric-glass/` | `examples/atmospheric-glass/` | Worked round-trip: DESIGN.md → design_tokens.json → tailwind.config.js |
| `examples/paws-and-paths/` | `examples/paws-and-paths/` | (same) |
| `examples/totality-festival/` | `examples/totality-festival/` | (same) |

## Attribution & redistribution

Apache-2.0 source files retain their original copyright headers
(`Copyright 2026 Google LLC`). The upstream `LICENSE` is included here per the
license's redistribution terms. No upstream files in this directory have been
modified; any changes for this project live outside `reference/`.
