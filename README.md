# Study20260621

A DESIGN.md reverse-engineering study: recover a live website's visual identity
(and its UI effects) into a structured, linted, exportable `DESIGN.md` design
system, then recreate it from the exports to prove the system transfers.

See [AGENTS.md](./AGENTS.md) for authoritative context and guidelines.

## Quick Start
- **Environment**: `source .venv/bin/activate` to enter the Python venv
- **Git**: remote `origin` → https://github.com/blossomz37/Study20260621.git (work on `main`)
- **Pre-push gate**: after cloning, run `git config core.hooksPath .githooks` once (see AGENTS.md)
- **Run the demo**: `python3 -m http.server 8765 --directory demo/book-flip` → open http://localhost:8765/
- **Lint a DESIGN.md**: `python3 tools/designmd-lint/validate.py demo/book-flip/DESIGN.md`
- **Export tokens**: `python3 tools/designmd-export/export.py demo/book-flip/DESIGN.md --out demo/book-flip/dist`

## Structure
- `docs/` — Durable reference documents (specs, the motion-extension proposal, the crystallize log)
- `tools/` — Reusable tooling: `designmd-lint/` (validator) and `designmd-export/` (CSS/Tailwind/DTCG exporter)
- `demo/` — Worked demos that double as transfer proofs: `book-flip/` (DESIGN.md → exports → recreated effect)
- `workspace/` — Shared work across sessions
  - `plans/` — Implementation plans and designs
  - `handoffs/` — Agent/session handoffs with task summaries
  - `evidence/` — Screenshots, test output, logs
  - `archive/` — Zipped completed task documentation
  - `scratch/` — Ephemeral ideas (monthly cleanup)
- `CLAUDE.md` / `AGENTS.md` — project instructions and authoritative context
- `.venv/` — Python virtual environment

> The reusable workflow proven here is captured as the `designmd-reverse-engineer`
> skill (in Carlo's global skills home; packaged copy in the git-ignored
> `.manual-distributed/`).
