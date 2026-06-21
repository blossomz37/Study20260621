# Evidence — book-flip demo (steps 4–5)

**Date:** 2026-06-21
**Demo:** `demo/book-flip/index.html`
**Consumes:** `demo/book-flip/dist/tokens.css` (generated from `DESIGN.md`)

## The transfer claim

Every color, font, radius, spacing, and timing value in the demo comes from
`dist/tokens.css` via `var(--…)`. Nothing brand-specific is hard-coded in the
HTML/CSS — only structural mechanics (`preserve-3d`, `backface-visibility`,
absolute positioning) are literal, per the motion-extension boundary. If the
demo looks right, the recovered design system transferred.

## Machine-verified token resolution (preview_eval)

```json
{
  "aspect": "2 / 3",                         // <- spacing.cover-aspect
  "ctaBgVar": "#3a2d28",                      // <- {colors.primary} resolved through the chain
  "innerTransition": "transform 0.45s",       // <- motion.flip computed
  "motionFlipVar": "transform 450ms ease",    // <- --motion-flip
  "perspective": "800px",                     // <- components.book-flip.perspective
  "tilesFound": 3,
  "tokensLoaded": true
}
```

The CTA background resolves `--book-flip-cta-bg → var(--color-primary) → #3a2d28`,
proving the component→primitive token indirection survives export into live CSS.

## Visual states (captured in-session via Claude Preview)

1. **Resting** — three fronts: clay (`secondary`), terracotta (`tertiary`),
   espresso (`primary`); Fraunces titles, Inter uppercase labels, 2:3 covers.
2. **Flipped** — book 1 **info mode** (Fraunces title, uppercase parchment meta,
   blurb, espresso "Buy · $14.99" CTA with cream text); book 2 **image mode**
   (back-cover quote + barcode); book 3 left front for contrast.

## Reproduce

```bash
# serve the demo
python3 -m http.server 8765 --directory demo/book-flip
# open http://localhost:8765/  — hover (desktop), tap (touch), or focus+Enter to flip
```

Or via the project's preview config: launch `book-flip-demo`
(`.claude/launch.json`).

## Notes

- Flip interaction ported from the source site's 593-char script + a CTA
  click-guard and desktop click-to-pin (cards with `data-pin`) so the buy link
  stays reachable.
- `prefers-reduced-motion` collapses `--motion-flip` to `0ms` (baked into
  `tokens.css` by the exporter), honoring the motion token contract.
