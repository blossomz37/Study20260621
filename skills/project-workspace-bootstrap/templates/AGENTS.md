# Project Agents & Workspace Context

## Project Status
- **Status**: <Pending | Active>
- **Purpose**: <TBD>
- **Git**: <Local only | Remote: URL>

## Filenaming Convention

All workspace files follow: `YYYYMMDD-NN-kebab-case-name.ext`

- `YYYYMMDD` — date created
- `NN` — sequence number (01, 02…) — resets daily
- `kebab-case-name` — descriptive slug
- `.ext` — appropriate extension

**Examples:** `20260101-01-implementation-plan.md`, `20260101-02-before-screenshot.png`

## Workspace Structure

**Shared workspace across multiple sessions.** Handoffs are internal documentation — assume agents/users may not have prior context.

### docs/
Durable reference documents (specs, architecture, guidelines, decision logs).

### workspace/
Ephemeral work and handoffs:
- **plans/** — implementation plans, designs.
- **handoffs/** — session/agent handoffs: what was done, what's next, blockers.
- **evidence/** — screenshots, test output, diffs, logs. Name by task; link from handoffs.
- **archive/** — zipped completed task docs (`TASK-ID_YYYY-MM-DD.zip`).
- **scratch/** — ephemeral ideas; clean periodically.

## Task Completion Requirements

**All completed tasks require evidence:**
- **Code changes**: commit with clear message.
- **UI/UX changes**: screenshots (before/after preferred) in `workspace/evidence/`.
- **Refactors**: test output or diff review.
- **Research/analysis**: linked sources or artifact in `workspace/`.

**Handoff format:** place a summary in `workspace/handoffs/`; include what was done, what's next, blockers, and links to evidence.

## Workspace Hygiene
- Keep `.gitignore` current.
- Commit after logical units; document completion in `workspace/handoffs/`.
- No large binaries in tracked dirs (only zipped in `archive/`).
- When in doubt: does this belong in `docs/` (permanent) or `workspace/` (temporary)?
