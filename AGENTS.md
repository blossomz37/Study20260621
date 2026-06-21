# Project Agents & Workspace Context

## Project Status
- **Status**: Active (early/nascent)
- **Purpose**: DESIGN.md reverse-engineering study/demo — reverse-engineer a live website's visual identity into a structured `DESIGN.md` (the Google Labs/Stitch format: YAML design tokens + markdown rationale), validate it with the official linter, export to Tailwind/DTCG, then recreate a mini-UI to prove the recovered design system transfers. Educational/demo framing.
- **Git**: GitHub remote at `origin` → https://github.com/blossomz37/Study20260621.git; work on `main`.
- **First pipeline proof (complete)**: the rgdbrandingawards.com cover-flip effect was reverse-engineered end-to-end — spec → `DESIGN.md` → lint → export → recreate-from-exports. Reusable tooling lives in `tools/` (linter + exporter); the worked demo and its generated exports in `demo/book-flip/`; a proposed `motion` format extension in `docs/design-md-motion-extension-proposal.md`. The whole workflow is captured as the external `designmd-reverse-engineer` skill (Carlo's global skills home; packaged copy in `.manual-distributed/`). Summary: `workspace/handoffs/20260621-04-book-flip-pipeline-status.md`.
- **Effect-family modules (complete)**: two further token groups were added to the skill via its "Extending to a new effect family" protocol — `gradients` (`demo/gradient/`, `references/gradient.md`) and glass = `blur` + native-DTCG `shadow` plus the C5 translucent-contrast fix (`demo/glass/`, `references/glass.md`). Each was proven gap→lint→export→recreate. Summary: `workspace/handoffs/20260621-05-glass-gradient-modules-complete.md`.
- **`tools/` ↔ skill sync**: `tools/designmd-lint/validate.py` and `tools/designmd-export/export.py` are mirrors of the skill's bundled `scripts/`. When changing one, change both (the skill source is external at `~/.myagents/skills/designmd-reverse-engineer/`). Linter/exporter need `pyyaml` (installed in `.venv`).
- **Upstream reference material**: `workspace/scratch/2026-06-21-01-idea-design.md-reverse-engineering/reference/` — cherry-picked spec, lint rules, worked examples. See `reference/SOURCE.md` for provenance (Apache-2.0, attributed).

## Workspace Structure

**Shared workspace across multiple sessions.** Handoffs are internal documentation — assume agents/users may not have prior context.

### docs/
Durable reference documents (project specs, architecture, guidelines, decision logs). Grows slowly; intended for retention.

### workspace/
Ephemeral work and handoffs. Subfolders:

- **plans/** — Implementation plans, designs, PRDs. Migrate completed plans to archive/ or delete.
- **handoffs/** — Agent-to-agent or session-to-session handoffs. Format: clear summary of work done, what's next, any blockers. Include timestamps and task IDs.
- **evidence/** — Screenshots, test output, diffs, logs. Name by task ID for traceability. Link from handoffs.
- **archive/** — Zipped completed task documentation. Zip structure: `TASK-ID_YYYY-MM-DD.zip` containing relevant plans/handoffs/evidence.
- **scratch/** — Ephemeral notes, brainstorms, half-formed ideas. Not permanent; see hygiene below. **Reference-material convention:** downloaded repo zips are cherry-pick sources only — they are git-ignored (`scratch/**/*.zip`) and stay local. Extract just the needed files into a `reference/` subfolder (tracked) and record provenance in `reference/SOURCE.md`.

### tools/
Reusable, dependency-light project tooling (stdlib + PyYAML; not ephemeral).
`designmd-lint/` validates a `DESIGN.md`; `designmd-export/` exports it to CSS
custom properties, a Tailwind config, and DTCG `tokens.json`. Both are also
bundled into the `designmd-reverse-engineer` skill.

### demo/
Worked demonstrations that double as transfer proofs. `book-flip/` holds a
`DESIGN.md`, its generated `dist/` exports, and an `index.html` that recreates
the cover-flip effect consuming only those exports.

> **Tracking note:** the global `.gitignore` has a generic `dist/` rule (Python
> build cruft). `demo/**/dist/` is force-tracked via a negation because those
> exports are part of the demo, not build artifacts.

## Filenaming Convention

All workspace files follow this format: `YYYYMMDD-NN-kebab-case-name.ext`

- `YYYYMMDD` — today's date (20260621)
- `NN` — sequence number (01, 02, 03…) — resets daily
- `kebab-case-name` — descriptive slug
- `.ext` — appropriate extension (.md for most, .zip for archive, .png for screenshots)

**Examples:**
- `20260621-01-project-kickoff.md` (handoff or plan)
- `20260621-02-implementation-plan.md` (plan)
- `20260621-03-before-screenshot.png` (evidence)
- `20260621-04-task-completion.md` (handoff)
- `20260621-tasks.zip` (archive — no sequence number)

## Task Completion Requirements

**All completed tasks require evidence:**
- **Code changes**: Commit with clear message
- **UI/UX changes**: Screenshots (before/after preferred) — store in `workspace/evidence/` with naming convention
- **Refactors**: Test output or diff review
- **Research/analysis**: Linked sources or artifact in workspace/evidence/ or workspace/plans/

**Handoff format:**
- When passing work between agents or sessions, place summary in `workspace/handoffs/` with naming convention
- Include: what was done, what's next, any blockers or decisions pending
- Link to evidence files with full paths

## Pre-push Safety Gate

This repo has a pre-push hook (`.githooks/pre-push`) that blocks pushes containing home paths, secrets, tracked `.env`, or `.claude/settings.local.json`.

**After cloning, enable it once:**
```
git config core.hooksPath .githooks
```
This setting is local and not carried by the clone. Bypass a known-safe push with `git push --no-verify`.

## Workspace Hygiene & Maintenance

**Prevent sprawl:**

1. **Scratch folder** — Ephemeral by design. Monthly cleanup: delete stale notes or migrate valuable ideas to docs/.
2. **Plans folder** — After a task completes, archive the plan (zip it into workspace/archive/) or delete. Don't accumulate abandoned plans.
3. **Handoffs folder** — Name clearly: `TASK-ID_PHASE.md` with timestamp. After task archive, can be deleted or kept if precedent-setting.
4. **Evidence folder** — Link evidence from handoffs with full paths. After 30 days, check for orphaned files (not referenced in any handoff) and delete.
5. **Archive folder** — Zipped files only. Label: `TASK-ID_YYYY-MM-DD.zip`. This folder should grow slowly and stay organized.

**General:**
- Keep .gitignore current (add patterns as needed)
- Commit after logical units; document task completion in workspace/handoffs/
- Document decisions in AGENTS.md as they emerge
- No large binaries in tracked directories (only in archive/ as zips)
- When in doubt, ask: "Does this belong in docs/ (permanent) or workspace/ (temporary)?"
