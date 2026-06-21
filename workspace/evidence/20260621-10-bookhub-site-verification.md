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

## Cover QA (Slice 3) — `report.json` gates, all PASS

| slug | title px | thumb-cap px | contrast | author | lines | PNG | JPG | WEBP |
|---|---|---|---|---|---|---|---|---|
| the-last-word | 371 | 31.9 | 14.8:1 | 7.3:1 | 2/2 | 4252K | 549K | 338K |
| the-signal | 346 | 22.9 | 18.3:1 | 13.1:1 | 2/2 | 2708K | 296K | 144K |
| julian-pike | 150 | 11.3 | 12.9:1 | 10.1:1 | 3/3 | 5331K | 563K | 272K |

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
