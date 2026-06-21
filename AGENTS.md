# Project Agents & Workspace Context

## Project Status
- **Status**: Pending (no remote repo yet)
- **Purpose**: TBD (awaiting specification)
- **Git**: Local init only; remote to be added

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
- **scratch/** — Ephemeral notes, brainstorms, half-formed ideas. Not permanent; see hygiene below.

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
