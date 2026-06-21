# Study20260621

A DESIGN.md reverse-engineering study: recover a live website's visual identity
(and its UI effects) into a structured, linted, exportable `DESIGN.md` design
system, then recreate it from the exports to prove the system transfers. The
pieces compose into **BookHub** — a real flip-gallery book site with
genre-typeset covers, deployed live (below).

See [AGENTS.md](./AGENTS.md) for authoritative context and guidelines.

## Live demos
- **BookHub gallery** — GitHub Pages: https://blossomz37.github.io/Study20260621/ ·
  Railway: https://bookhub-production-cd3a.up.railway.app
- Both auto-deploy on push to `main` (see `.github/workflows/deploy-pages.yml` and
  `deploy-railway.yml`).

## Quick Start
- **Environment**: `source .venv/bin/activate` to enter the Python venv
- **Git**: remote `origin` → https://github.com/blossomz37/Study20260621.git (work on `main`)
- **Pre-push gate**: after cloning, run `git config core.hooksPath .githooks` once (see AGENTS.md)
- **Run the BookHub site**: `python3 -m http.server 8770 --directory demo/books` → open http://localhost:8770/
- **Run the original flip demo**: `python3 -m http.server 8765 --directory demo/book-flip` → open http://localhost:8765/
- **Lint a DESIGN.md**: `python3 tools/designmd-lint/validate.py demo/books/DESIGN.md`
- **Export tokens**: `python3 tools/designmd-export/export.py demo/books/DESIGN.md --out demo/books/dist`
- **Build the titled covers**: `.venv/bin/python tools/cover-typography/compose.py --all --strict`

## Structure
- `docs/` — Durable reference documents (specs, the motion-extension proposal, the crystallize log)
- `tools/` — Reusable tooling: `designmd-lint/` (validator), `designmd-export/`
  (CSS/Tailwind/DTCG exporter), and `cover-typography/` (Pillow compositor that bakes
  genre titling onto covers and gates them on Kindle-ratio + thumbnail legibility)
- `demo/` — Worked demos that double as transfer proofs: `book-flip/` (the flip
  effect), `gradient/` and `glass/` (effect-family modules), and `books/` (**BookHub** —
  the composed site: `DESIGN.md` → exports + per-book cover specs → titled covers + gallery)
- Deploy config (repo root): `Dockerfile` + `Caddyfile` + `railway.json` (Railway),
  `.github/workflows/` (Pages + Railway), `demo/books/index.html` (root→`/site/` redirect)
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
