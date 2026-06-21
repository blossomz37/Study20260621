# Handoff — BookHub flip-gallery site + cover-typography tool (COMPLETE)

**Date:** 2026-06-21
**Plan:** `workspace/plans/20260621-06-bookhub-site-and-cover-typography-plan.md`
**Author of demo books:** A. May Zing
**Status:** All 6 slices done; acceptance criteria met; evidence captured.

## What was built

A real static **flip-gallery site** presenting three real books with real
**baked covers**, plus a deterministic **cover-typography tool** and a
representative **`DESIGN.md`** that makes "add a fourth book / make another page"
a recipe, not a redesign.

```
demo/books/
  DESIGN.md                 # BookHub system — evolves Shelf & Spine + cover concern (lints green)
  dist/                     # exported tokens.css / tailwind.config.js / tokens.json
  data/books.json           # per-book site copy (from dossiers) + provenance
  covers/<slug>/cover-spec.yaml  # per-book titling spec (instance data)
  covers/<slug>/dist/       # titled cover.{png,jpg,webp} + qa-contact-sheet.png + report.json
  site/index.html           # the gallery (consumes ../dist/tokens.css only for design values)
  site/assets/              # web-optimized covers (webp + jpg)
tools/cover-typography/      # compose.py, fonts.json, fetch_fonts.py, README, fonts/ (git-ignored)
```

## Slice-by-slice

1. **Book copy → `data/books.json`** — 3 subagents, one per dossier. All blurbs
   ≤ 50 words, spoiler-safe, voice-matched, no invented proper nouns (supervised
   against QC gates; provenance recorded per book in the JSON).
2. **Genre font research** — 3 subagents, grounded in 2024–2026 comps:
   - The Last Word (dystopian) → **Anton** + Oswald (comps: *Hum* '24, *The Dream
     Hotel* '25, *You Weren't Meant to Be Human* '25).
   - The Signal → **techno-font gap RESOLVED in favor of the library: League
     Spartan** + Montserrat; **no OFL fetch** (comps: *Culpability* '25, *Watching
     From Within* '25, *Darkly* '24 show the lane is bold uppercase *sans*, not mono).
   - Julian Pike (caper) → **Bodoni Moda** + Marcellus (comps: Osman *Impossible
     Fortune* '25, *We Solve Murders* '24, Sutanto *Vera Wong* '24–25).
3. **Cover tool** — `tools/cover-typography/compose.py`. Deterministic, pins
   variable-font axes, auto-fits, scrim (with `hold` plateau), worst-case contrast
   gate. **3/3 covers PASS**; byte-stable re-runs; WEBP 92–95% smaller than PNG.
4. **`demo/books/DESIGN.md`** — adds `cover-title`/`cover-author` type roles +
   per-book override method, `cover-scrim`/`cover-ink-*` colors, `cover-safe-inset`
   spacing, `cover-title-glow` shadow, and `cover-dark`/`cover-cream` components
   (scrim reuses the glass worst-case-contrast discipline). **No new token type.**
   Lints **green** (0 errors / 0 warnings); exports cleanly; overrides round-trip.
5. **Site** — `site/index.html` renders cards from `books.json`, real covers via
   `<picture>` (webp→jpg, width/height set → no CLS), all design values via
   `var(--…)` from `dist/tokens.css`. Hover/tap/keyboard/Escape + CTA click-guard +
   reduced-motion all work.
6. **Verify + evidence** — see `workspace/evidence/20260621-10-bookhub-site-verification.md`
   (computed-style transfer proof, interaction tests, QA table) and contact sheets
   `20260621-07/08/09-cover-qa-*.png`.

## Decisions / deviations (all documented in-place)

- **The Signal genre:** the dossier is a **YA digital/social-media thriller**, not
  the "surveillance/techno thriller" the plan assumed. Copy follows the dossier
  (authoritative); the cover art (camera + screen wall) reconciles as a
  documentary-filmmaker premise; font choice (League Spartan) holds for that genre.
  Flagged in `books.json` provenance.
- **Julian Pike titling:** `max_lines: 3` and `min_thumb_cap_px: 11` (a 5-word
  literary Didone can't hit 14px cap in the clean cream; its 12.9:1 contrast
  compensates). Rationale recorded in its `cover-spec.yaml` and the tool README.
- **Tracking:** large PNG masters are git-ignored (regenerable via `compose.py
  --all`); web jpg/webp, contact sheets, reports, and exports are tracked. Font
  binaries git-ignored; `fonts.json` is the reproducible record.

## How to reproduce / extend

```bash
.venv/bin/python tools/cover-typography/compose.py --all --strict   # rebuild + gate covers
.venv/bin/python tools/designmd-lint/validate.py demo/books/DESIGN.md
.venv/bin/python tools/designmd-export/export.py demo/books/DESIGN.md --out demo/books/dist
python3 -m http.server 8770 --directory demo/books   # then open /site/index.html
```

**Add a fourth book:** drop the source PNG in `demo/books/`, pick a title face by
the genre→face method in `DESIGN.md` (library-first), write a `cover-spec.yaml`,
run `compose.py`, copy the webp/jpg into `site/assets/`, add a `books.json` entry.
No redesign required.

## Open items (none blocking)

- Imprint ("Parchment Press") and prices ($12.99/$14.99) are placeholders — no
  dossier specifies them. Swap real values before any real publish.
- Source art is 992w; the 1.6× upscale to 1600w is fine for web, marginal for
  print. Regenerate sources at ≥1600w for true print masters.
- GitHub Pages: serve from `demo/books/` as the site root (it references
  `../dist/tokens.css` and `../data/books.json`). Not yet deployed.
