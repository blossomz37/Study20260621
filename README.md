# Study20260621

Project workspace (pending remote setup).

See [AGENTS.md](./AGENTS.md) for workspace context and guidelines.

## Quick Start
- **Environment**: `source .venv/bin/activate` to enter the Python venv
- **Git**: Initialized locally; remote to be added
- **Workspace**: See [AGENTS.md](./AGENTS.md) for folder structure and hygiene policies

## Structure
- `docs/` — Durable reference documents (specs, architecture, guidelines)
- `workspace/` — Shared work across sessions
  - `plans/` — Implementation plans and designs
  - `handoffs/` — Agent/session handoffs with task summaries
  - `evidence/` — Screenshots, test output, logs
  - `archive/` — Zipped completed task documentation
  - `scratch/` — Ephemeral ideas (monthly cleanup)
- `.gitignore` — excludes OS files, .env, and Python cache
- `CLAUDE.md` — project-level instructions (points to AGENTS.md)
- `AGENTS.md` — authoritative context, hygiene, task completion standards
- `.venv/` — Python virtual environment
