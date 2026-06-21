# Handoff — BookHub byline revision + GitHub Pages & Railway deployments

**Date:** 2026-06-21
**Continues:** `workspace/handoffs/20260621-06-bookhub-site-and-cover-typography-complete.md`
(the original 6-slice build). This handoff covers the follow-on work: the
author-byline redesign and getting the site live on two hosts with auto-deploy.

## Live URLs

| Host | URL | Auto-deploy on push to `main` |
|---|---|---|
| GitHub Pages | https://blossomz37.github.io/Study20260621/ | ✅ |
| Railway | https://bookhub-production-cd3a.up.railway.app | ✅ (via `RAILWAY_TOKEN` secret) |

Both serve `demo/books/` (root redirects to `/site/`). Both verified 200 across
`/`, `/site/`, `/dist/tokens.css`, `/data/books.json`, and the cover assets — with
correct MIME including `image/webp`.

## 1. Author byline moved to the foot of each cover

The byline was decoupled from the title and given its **own gradient band** for
contrast + depth (not just text on busy pixels):

- **The Last Word / The Signal** — bottom-up **dark** scrim band lifts the light
  byline over the rubble / desk foreground.
- **Julian Pike** — a translucent **cream footer band** (a soft vignette, art
  showing through) + a hairline rule lifts the dark byline over the busy collage.
  Byline contrast went 4.8:1 → **9.8:1** after switching from a thin scrim to the
  footer band; ink darkened to `#241f1a`.

Tool changes (`tools/cover-typography/compose.py`): new spec keys `author_zone`
(normalized foot box), `author_scrim` (second, bottom-directed scrim), and
`author_rule` (optional hairline). Author contrast is now measured in the byline's
own light/dark regime. Omitting `author_zone` falls back to the old under-title
placement. All 3 covers still PASS `--strict`; `DESIGN.md` + README updated.

> Note: the headless preview's screenshot compositor stopped capturing `<img>`
> layers mid-session (later site screenshots show parchment placeholders). Confirmed
> a tooling artifact, not a site bug: a `canvas.drawImage` pixel-read of the in-page
> cover returned `242,246,255` (`#f2f6ff`, the baked title ink), and the deployed
> sites render the covers normally. The authoritative visual is the cover PNGs under
> `demo/books/covers/*/dist/`.

## 2. GitHub Pages

"Deploy from Branch" can only serve repo root or `/docs`, but the site lives in
`demo/books/`. Solution: **Pages via GitHub Actions**.

- `.github/workflows/deploy-pages.yml` — uploads **only `demo/books/`** as the site
  root; `demo/books/index.html` redirects `/` → `/site/`.
- Enabled Pages with `build_type: workflow` via `gh api`. Deploy ran green.
- The first push-triggered run failed because it ran *before* Pages was enabled —
  harmless, superseded by the dispatch run.

## 3. Railway

Railway runs containers, so the site is served by a tiny Caddy image.

- `Dockerfile` (Caddy:2-alpine, copies `demo/books` → `/srv`), `Caddyfile`
  (`:{$PORT}`, gzip, correct MIME), `railway.json` (pins the Dockerfile builder).
- **Smoke-tested the exact image locally** (started Docker Desktop, `docker build` +
  `run`) before committing — all paths 200, `image/webp` correct.
- Deployed via CLI after the user ran `railway login`: `railway link` →
  `railway add --service bookhub` → `railway up`.
- First `railway up` **timed out on the upload** (whole-repo payload too big). Added
  `.railwayignore` to slim the upload to the build inputs; retry succeeded.
- Generated the public domain with `railway domain`.

Project: `test-design-md` (id `6f1d5274-af66-48b4-9d62-28ed9721af68`), env
`production`, service `bookhub`.

## 4. Railway auto-deploy (GitHub Actions)

Native Railway↔GitHub needs the Railway GitHub App OAuth (browser-only), so instead:

- `.github/workflows/deploy-railway.yml` — runs `railway up --service bookhub --ci`
  on push (paths: `demo/books/**` + build config), using a **project token** in the
  GitHub secret `RAILWAY_TOKEN`.
- First token was rejected ("Invalid RAILWAY_TOKEN") because it was an **account
  token**; the CLI's `RAILWAY_TOKEN` wants a **project** token (Project → Settings →
  Tokens). After re-creating it as a project token, the run went **green** and the
  site redeployed.

Token-type reference:
| Railway token source | CLI env var |
|---|---|
| Project → Settings → Tokens (project token) ✅ | `RAILWAY_TOKEN` |
| Account → Tokens (account/team token) | `RAILWAY_API_TOKEN` |

## How to update either site

Normal loop: edit a `covers/<slug>/cover-spec.yaml` → `.venv/bin/python
tools/cover-typography/compose.py --all` → copy the new `webp`/`jpg` into
`demo/books/site/assets/` → commit → push. Both Pages and Railway redeploy on push.
Manual triggers: the **Actions** tab, or `gh workflow run deploy-pages.yml` /
`gh workflow run deploy-railway.yml`.

## Open / non-blocking

- Both workflows log a **Node 20 deprecation** warning (GitHub auto-runs them on
  Node 24 — harmless). Bump action versions whenever convenient.
- Imprint ("Parchment Press") and prices ($12.99/$14.99) are still placeholders.
- Source art is 992w (1.6× upscale to 1600w — fine for web, marginal for print).
- Railway deploy is CLI/Actions-based, not the native GitHub App integration (which
  would add PR preview environments if ever wanted).

## Key files added this session

- `tools/cover-typography/compose.py` (byline-at-foot support), README, specs
- `.github/workflows/deploy-pages.yml`, `.github/workflows/deploy-railway.yml`
- `demo/books/index.html` (redirect), `Dockerfile`, `Caddyfile`, `railway.json`,
  `.railwayignore`, `.dockerignore`
- Evidence: `workspace/evidence/20260621-10-bookhub-site-verification.md`
