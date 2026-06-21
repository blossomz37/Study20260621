---
name: project-workspace-bootstrap
description: Bootstrap a fresh project workspace with a clean order of operations — .gitignore, agent/project docs, workspace structure, filenaming convention, venv, local git init, and remote connection last. Use when starting a new empty repository or project workspace from scratch.
---

# Project Workspace Bootstrap

Scaffold a new project workspace in the correct order. The value of this skill is the **sequence** and the **decisions to confirm** — not just the file contents. Connect a remote *last*, after the local structure is committed.

## When to use
- Starting a brand-new, empty project directory.
- You want consistent workspace hygiene, agent-facing docs, and a filenaming convention before any code exists.

## Order of operations (do not reorder)

1. **`.gitignore` first.** Cover macOS, Linux, Windows system files, `.env`, and the language ecosystem (e.g. Python cache + venv). See `templates/gitignore`.
2. **Agent/project docs.**
   - `AGENTS.md` — authoritative context: project status, workspace structure, filenaming convention, task-completion + evidence requirements, hygiene. See `templates/AGENTS.md`.
   - `CLAUDE.md` — minimal pointer to `AGENTS.md` as authoritative. Nothing more. See `templates/CLAUDE.md`.
   - `README.md` — orientation for any human/agent entering the repo. See `templates/README.md`.
3. **Workspace structure.** Create directories and add `.gitkeep` so empty folders are tracked:
   - `docs/` — durable reference documents.
   - `workspace/plans/` — implementation plans, designs.
   - `workspace/handoffs/` — session-to-session / agent-to-agent handoffs.
   - `workspace/evidence/` — screenshots, test output, logs.
   - `workspace/archive/` — zipped completed task docs.
   - `workspace/scratch/` — ephemeral notes and ideas.
4. **Environment.** Create the language environment if applicable (e.g. `python3 -m venv .venv`). Confirm the stack first if unknown.
5. **Local git.** `git init`, then `git add -A` and an initial commit.
6. **Remote — LAST.** Only after local commits exist. See the remote checklist below.

## Decisions to confirm (don't guess)

- **Workspace shape.** Challenge the user's first instinct if it risks file sprawl or sparse folders. Propose `docs/` (durable) vs `workspace/` (ephemeral) as the core split. Let subfolders emerge from real need.
- **Filenaming convention.** Default: `YYYYMMDD-NN-kebab-case-name.ext` for workspace files (date + daily sequence number + slug). Confirm the user wants enumeration before enforcing it.
- **Stack/venv.** Confirm the language/runtime before creating an environment.
- **Hygiene depth.** For short-lived projects, keep hygiene light. For long-lived ones, add a periodic maintenance checklist to `AGENTS.md`.

## Remote connection checklist

Before pushing, gather:
1. **Remote URL** (HTTPS or SSH).
2. **Is the remote empty?** If not, fetch/merge before pushing — never force-push over existing history without explicit confirmation.
3. **Default branch name** (usually `main`).

Then:
```
git remote add origin <URL>
git branch -M main
git push -u origin main
```
Verify with `git remote -v` and `git log --oneline`.

## Optional: global gitignore (machine-level) — OPT-IN ONLY

A global gitignore makes git skip OS junk files (e.g. macOS `.DS_Store`, Windows `Thumbs.db`) in **every repo on the machine**, even ones that lack a per-project entry.

**This changes git behavior globally, outside the current project. ALWAYS present it as optional and get explicit user consent before configuring it.** Do not set it silently as part of bootstrap.

How to offer it:
1. Ask the user if they want a machine-wide gitignore for OS junk (yes/no). If no, skip entirely.
2. Detect or ask the OS (macOS / Linux / Windows). Apply the matching template below.
3. Note: this is a per-machine setting, not stored in any repo — it won't follow them to a new computer (suggest a dotfiles backup).

Setup (paths differ per OS — `~` resolves to the user's home):
```
git config --global core.excludesfile ~/.gitignore_global
# then write the OS-appropriate patterns into ~/.gitignore_global
```
Verify with `git config --global core.excludesfile` and by printing the file.

OS pattern templates:
- macOS → `templates/gitignore-global-macos`
- Linux → `templates/gitignore-global-linux`
- Windows → `templates/gitignore-global-windows`

The per-project `.gitignore` should still carry its own OS block — redundancy is harmless and keeps the repo self-documenting for collaborators who lack a global config.

## Notes
- Keep this skill portable: no personal paths, names, or org-specific references.
- Templates use placeholders like `<PROJECT_NAME>` and `<YYYYMMDD>` — substitute at bootstrap time.
