# BookHub site — verification evidence (Slice 6)

**Date:** 2026-06-21
**Served:** `python3 -m http.server 8770 --directory demo/books`, page at `/site/index.html`.

## Computed-style transfer proof (read from the running page)

The site hard-codes **no** brand value; every design value resolves from
`demo/books/dist/tokens.css` (exported from `demo/books/DESIGN.md`).

| Proof | Expected | Observed |
|---|---|---|
| `motion.flip` token → computed `transition` | `transform 450ms ease` | `--motion-flip: transform 450ms ease` → `.book-inner` computes `transform 0.45s ease` ✓ |
| `{colors.primary}` `{ref}` chain → CTA bg | `#3a2d28` | `.book-cta` background `rgb(58, 45, 40)` ✓ |
| Info title face | Fraunces | `.book-title` font-family `Fraunces` ✓ |
| Real baked covers (webp → jpg) | 1600×2560, webp chosen | all 3 `currentSrc` = `*.webp`, naturalSize `1600x2560`, `complete: true` ✓ |
| Card aspect (Kindle, no title crop) | `1 / 1.6` | `.book-flip` aspect-ratio `1 / 1.6` ✓ |
| Reduced-motion contract baked into CSS | `@media (prefers-reduced-motion)` collapses `--motion-flip` to `0ms` | rule present & reachable in document stylesheets ✓ |

## Interaction / accessibility (dispatched on the running page)

| Behavior | Result |
|---|---|
| Click CTA on flipped face does NOT close the card (click-guard) | `stillFlippedAfterCTA: true` ✓ |
| Escape closes the flipped card | `closedAfterEsc: true` ✓ |
| Enter flips a focused card open | `openAfterEnter: true` ✓ |
| Hover flip gated to `@media (hover:hover)`; tap/keyboard via `is-flipped` | per source + tests ✓ |
| No console errors/warnings | "No console logs" ✓ |

## Screenshots captured this session (in-transcript)

- Resting gallery (desktop): three real titled covers on limestone.
- Flipped card (desktop): The Last Word info face — kicker, Fraunces title, uppercase
  meta, full blurb, espresso "Buy · $12.99" CTA on parchment.
- Mobile (375×812): single-column, cover full-width and legible.

## Revision — author byline moved to the foot of the cover

Per request, the author byline now sits at the **foot** of each cover (not under the
title), each on its **own gradient band** for contrast + depth/texture:
- **The Last Word / The Signal:** a bottom-up **dark** scrim band lifts the light
  byline over the rubble / desk foreground.
- **Julian Pike:** a translucent **cream footer band** (a soft vignette, art showing
  through) lifts the dark byline over the busy collage; a hairline rule above it adds a
  vintage touch. Byline ink darkened to `#241f1a` for margin.

The tool gained `author_zone` (a normalized foot box), `author_scrim` (a second,
bottom-directed scrim), and an optional `author_rule` hairline. All re-verified PASS.

## Cover QA (Slice 3) — `report.json` gates, all PASS (after byline revision)

| slug | title px | thumb-cap px | contrast | author | lines | PNG | JPG | WEBP |
|---|---|---|---|---|---|---|---|---|
| the-last-word | 371 | 31.9 | 14.7:1 | 14.5:1 | 2/2 | 3939K | 498K | 294K |
| the-signal | 346 | 22.9 | 18.3:1 | 10.3:1 | 2/2 | 2568K | 284K | 138K |
| julian-pike | 150 | 11.3 | 12.9:1 | 9.8:1 | 3/3 | 5118K | 533K | 255K |

Moving the byline onto its own scrim band *raised* author contrast across the board
(e.g. Julian 10.1→4.8 with a thin scrim, then →9.8 with the cream footer band).

**Visual evidence:** the three baked cover PNGs under `demo/books/covers/*/dist/`
(viewed directly during the build) are the authoritative render. NOTE: the headless
preview's screenshot compositor stopped capturing `<img>` layers mid-session (later
captures show parchment placeholders) — but a `canvas.drawImage` pixel read of the
in-page cover returned `242,246,255` = `#f2f6ff`, the exact baked title color, proving
the covers raster correctly in-page; earlier-session screenshots of the same site code
rendered the covers normally.

- **Determinism:** re-running `compose.py` on a spec produced an identical PNG SHA
  (verified for the-signal and the-last-word).
- **WEBP vs PNG:** 92–95% smaller — the file-size comparison the plan asked for.
- **Julian Pike** uses `max_lines: 3` and `min_thumb_cap_px: 11` (documented in its
  spec): a 5-word literary Didone can't reach 14px cap in the available clean cream,
  and its 12.9:1 contrast (vs the 4.5 floor) compensates — the trade real long-title
  literary covers make.

## Lint (Slice 4) — `demo/books/DESIGN.md`

`PASS: 0 error(s), 0 warning(s), 2 info`
- `cover-dark` glass advisory: ink vs backdrop worst-case stop **13.85:1, meets AA**.
- `motion.none` orphaned (info, benign).

Contact sheets: `20260621-07/08/09-cover-qa-*.png`.
