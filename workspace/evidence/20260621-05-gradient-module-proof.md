# Gradient module — gap proof & transfer proof

**Date:** 2026-06-21
**Module:** `gradients` token group (skill `designmd-reverse-engineer`)
**Files:** `demo/gradient/{DESIGN.md, DESIGN.broken.md, index.html, dist/}`

## 1. Gap proof (the un-extended linter is blind to gradients)

`demo/gradient/DESIGN.broken.md` has a deliberately malformed gradient: an invalid
`type: sweep`, a stop `position: 150%` (out of range), and a stop `color:
{colors.nope}` (broken reference).

**BEFORE** (linter without the gradient rules):

```
demo/gradient/DESIGN.broken.md
  ▲ warning broken-ref  [components.hero-banner.backgroundImage] 'backgroundImage' is not a recognized component sub-token...
  · info    missing-sections [spacing] ...
  · info    missing-sections [rounded] ...
  → PASS: 0 error(s), 1 warning(s), 2 info        exit=0
```

The broken gradient passes with **zero errors** — the linter can only warn that
`backgroundImage` is unrecognized; it never looks inside the gradient. That silent
pass is the gap.

**AFTER** (linter with `gradient-stops` / `gradient-type` / `gradient-broken-ref`):

```
demo/gradient/DESIGN.broken.md
  ✗ error   gradient-stops      [gradients.hero.stops[0].position] '150%' is not a valid stop position (0–100% or a 0–1 fraction).
  ✗ error   gradient-broken-ref [gradients.hero.stops[0]] Reference {colors.nope} does not resolve to any defined token.
  ▲ warning gradient-type       [gradients.hero.type] 'sweep' is not a known gradient type (conic, linear, radial).
  · info    contrast-ratio      [components.hero-banner] textColor sits over a gradient backgroundImage; contrast is not evaluable...
  → FAIL: 2 error(s), 1 warning(s), 3 info         exit=1
```

The same file now fails on exactly the gradient construct. The corrected
`demo/gradient/DESIGN.md` passes clean:

```
demo/gradient/DESIGN.md
  · info    contrast-ratio  [components.hero-banner] textColor sits over a gradient backgroundImage; ...
  → PASS: 0 error(s), 0 warning(s), 1 info         exit=0
```

No regression: `demo/book-flip/DESIGN.md` still passes (1 info, motion-orphaned).

## 2. Export proof (one token → three targets)

`python3 scripts/export.py demo/gradient/DESIGN.md --out demo/gradient/dist`:

- **CSS:** `--gradient-hero: linear-gradient(135deg, var(--color-primary) 0%, var(--color-tertiary) 55%, var(--color-accent) 100%);`
  and `--gradient-glow: radial-gradient(circle at 28% 18%, rgba(37,99,235,0.55) 0%, rgba(37,99,235,0) 70%);`
  — both linear and radial round-trip.
- **Tailwind:** `theme.extend.backgroundImage = { hero: '…', glow: '…' }` → `bg-hero`.
- **DTCG:** `{ "$type": "gradient", "$value": [ {color, position}, … ], "$extensions": { "designmd": { "type": "linear", "angle": "135deg" } } }`.

## 3. Transfer proof (recreate from exports only)

`demo/gradient/index.html` links only `dist/tokens.css`. Computed-style check
(served on :8766) confirms the full reference chain resolved:

```
banner background-image: linear-gradient(135deg, rgb(91,33,182) 0%, rgb(219,39,119) 55%, rgb(245,158,11) 100%)
banner border-radius:    20px   (rounded.lg)
banner padding:          64px   (spacing.xl)
swatch background-image: == banner background-image   (sameToken: true)
```

The banner and the swatch chips paint the **identical** gradient because both
reference `{gradients.hero}` — no drift. The hero wash and radial glow render as
designed (violet→pink→amber with a blue bloom upper-left).

## 4. QA follow-up — light-on-amber at mobile width (fixed)

A review audit found a viewport-dependent legibility issue: at desktop the hero
copy stays over the darker violet/pink end (fine), but on a tall **mobile** banner
the lower sub-text lines reach the light **amber** end (#f59e0b), where near-white
`on-primary` text drops to ≈2:1 — below AA and visibly washing out. This violates
the DESIGN.md's own contract ("keep saturated gradient text on the darker violet
end for legibility").

Fix (`index.html`-only — no token change, no re-export): a `text-shadow: 0 1px 3px
rgba(11,8,24,0.5)` legibility scrim on the headline + sub-text — the same
treatment applied to the glass demo. Verified at mobile (375px): the amber-region
lines separate cleanly with dark glyph edges.

Note: text-shadow is a *perceptual* mitigation, not a measured-ratio fix. The
deeper finding is in the linter — its gradient/glass contrast advisory checks text
against the gradient's **darkest** stop, which is the *most favorable* stop for
light text and so under-warns; a conservative advisory should check the
**worst-case** stop (min contrast across all stops). Flagged for a follow-up to
`scripts/validate.py` (see the session notes / handoff).
