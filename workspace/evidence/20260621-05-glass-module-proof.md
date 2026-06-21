# Glass module — gap proof, C5 fix & composition proof

**Date:** 2026-06-21
**Module:** `blur` + `shadow` token groups + the C5 contrast fix (skill
`designmd-reverse-engineer`)
**Files:** `demo/glass/{DESIGN.md, DESIGN.broken.md, index.html, dist/}`

## 1. Two gaps proven (un-extended linter)

### a. Blind to blur/shadow
`demo/glass/DESIGN.broken.md` has `blur.glass: 20` (no unit), `shadow.glass.offsetY:
nope` (not a dimension), and `shadow.glass.color: {colors.ghost}` (broken ref).

**BEFORE** (no glass rules) → `PASS: 0 error(s)` — the linter cannot see inside
`blur`/`shadow`. **AFTER** →
```
✗ error  blur-format       [blur.glass] '20' is not a valid blur dimension (expected e.g. 20px).
✗ error  shadow-format     [shadow.glass.offsetY] 'nope' is not a valid dimension (expected e.g. 8px, 0).
✗ error  shadow-broken-ref [shadow.glass] Reference {colors.ghost} does not resolve to any defined token.
→ FAIL: 3 error(s)        exit=1
```

### b. C5 contrast false-positive
`demo/glass/DESIGN.md` glass-card = `rgba(255,255,255,0.10)` fill + near-white
text. **BEFORE** the linter resolved the fill to opaque white and reported a
failing ratio against white text:
```
▲ warning contrast-ratio [components.glass-card]  textColor on backgroundColor has contrast 1.14:1, below WCAG AA minimum 4.5:1.
▲ warning contrast-ratio [components.glass-badge]  ... 1.14:1 ...
```
That is a false positive — the card is legible over the dark backdrop.

**AFTER** (C5 fix) the linter detects the translucent/blurred surface, declines to
fail it, and checks text against the declared `backdrop: {gradients.hero}` token's
**worst-case (lowest-contrast) stop**:
```
· info contrast-ratio [components.glass-card]  translucent/blurred surface over backdrop {gradients.hero}: textColor vs the backdrop's worst-case (lowest-contrast) stop is 1.89:1 (drops below WCAG AA 4.5:1; advisory — blur and translucency shift effective contrast).
· info contrast-ratio [components.glass-badge] ... 1.89:1 (drops below WCAG AA ...) ...
→ PASS: 0 error(s), 0 warning(s), 2 info        exit=1→0
```

The downgrade only applies to translucent/blurred components; opaque-surface
contrast is unchanged, so no real failure is masked. (The advisory uses the
worst-case stop, not the darkest — see §7; an earlier draft reported 7.91:1 vs the
darkest violet stop, which under-warned for light text.)

## 2. Cross-check: upstream `atmospheric-glass` lints sensibly (acceptance #6)

`reference/examples/atmospheric-glass/DESIGN.md` (translucent cards, white text)
previously produced 4 false-positive contrast warnings. Under the C5 fix all four
downgrade to advisory info and the file passes clean:
```
· info contrast-ratio [components.glass-card-standard] translucent/blurred surface: contrast is not evaluable against the fill alone — declare a `backdrop` token or verify against the actual backdrop.
· info ... glass-card-elevated / button-ghost / input-field ...
→ PASS: 0 error(s), 0 warning(s), 4 info
```

## 3. Export proof (one source → three targets)

`scripts/export.py demo/glass/DESIGN.md`:

- **CSS:** `--blur-glass: 20px;`, `--shadow-glass: 0 8px 32px 0 var(--color-glass-shadow);`,
  and component `--glass-card-backdrop: blur(var(--blur-glass));`,
  `--glass-card-shadow: var(--shadow-glass);`.
- **Tailwind:** `backdropBlur: { glass: '20px', 'glass-strong': '40px' }`,
  `boxShadow: { glass: '0 8px 32px 0 var(--color-glass-shadow)' }`.
- **DTCG:** native `shadow` composite `{ "$type": "shadow", "$value": {color,
  offsetX, offsetY, blur, spread} }`; **blur** as a custom group with a
  `$description` documenting that DTCG has no blur type and per-token
  `$extensions.designmd.role: backdrop-blur` (honest invention).

## 4. Composition + transfer proof (recreate from exports only)

`demo/glass/index.html` links only `dist/tokens.css`. The page backdrop is
`var(--gradient-hero)` — the **same** `{gradients.hero}` token from Module A — and
the card frosts sharp token-colored orbs behind it. Computed-style check (served
on :8767) confirms the full chains resolved:

```
card backdrop-filter: blur(20px)                          (blur.glass)
card background:       rgba(255, 255, 255, 0.1)            (colors.glass-fill)
card box-shadow:       rgba(8,10,25,0.45) 0 8px 32px 0     (shadow.glass -> color ref)
card border-top:       1px rgba(255, 255, 255, 0.22)       (colors.glass-border)
card border-radius:    20px                                (rounded.lg)
body background-image: linear-gradient(135deg, rgb(91,33,182) ...)  (gradients.hero)
```

No console errors. The two modules compose: glass adds blur + shadow on top of the
gradient module's backdrop, and the frosted card renders from the exported tokens
alone.

## 5. No regression

Full sweep via `tools/`: book-flip / gradient / glass all PASS; both `.broken.md`
gap files FAIL as designed. `tools/` exporter output is byte-identical to the
committed `dist/`.

## 6. QA follow-up — white-on-white in the demo (fixed)

A review caught a legibility bug in `index.html` (not the tooling): the decorative
`orb--b` was filled with `var(--color-on-primary)` (#f5f3ff, near-white) and sat
directly behind the card's near-white body text — frosted through the 10%-white
fill it produced a ~1:1 white-on-white band. This violated the DESIGN.md's own
"keep glass text on the darker end of the backdrop" rule. The linter has a
*structural* limitation here: its C5 advisory can only reason about the declared
`backdrop: {gradients.hero}` token, not a decorative non-token orb composited
behind the glass (`references/glass.md` open Q #3). Separately, at the time of this
review the advisory also reported a falsely-reassuring `7.91:1` because it used the
*darkest* stop — corrected in §7 to the worst-case stop.

Fixes (both `index.html`-only — no token change, no re-export):
- **Recolor** `orb--b` from `--color-on-primary` to `--color-tertiary` (#db2777,
  saturated pink) so the frosted patch behind the text stays mid-dark.
- **Legibility scrim:** `text-shadow: 0 1px 3px rgba(8,10,25,0.55)` on the card
  text — the treatment the DESIGN.md and upstream atmospheric-glass both prescribe.

Verified on :8767: body text legible across the full card; `orb--b` computes to
`rgb(219,39,119)`; no console errors. Lint/exports unchanged (demo-only edit).

## 7. Linter heuristic correction — worst-case stop, not darkest

The white-on-white review surfaced a deeper, correctly-attributed bug in the
*linter* (not the demo): the C5 / gradient advisory checked text against the
backdrop's **darkest** stop. For light text the darkest stop is the *most
favorable* one, so the advisory under-warned — it reported `7.91:1 (meets AA)` for
the glass card even though the same light text over the gradient's amber end is
only ~1.9:1.

Fix (`scripts/validate.py`, mirrored to `tools/`): `darkest_stop_color` →
`worst_stop_contrast(fm, gradient_path, txc)`, which returns the **minimum**
contrast across all stops for the given text color. Both advisory branches (glass
`backdrop`, and text over a gradient `backgroundImage`) now report that worst case.
Conservative on purpose: the linter can't know which region of the gradient the
element overlaps, so it flags the worst a viewport could produce.

Result after the fix (all still non-failing `info`, exit 0):
- glass-card / glass-badge: `1.89:1 (drops below WCAG AA)` vs the worst-case amber stop.
- gradient hero-banner: `1.96:1 (drops below WCAG AA)` — the advisory now catches
  exactly the light-on-amber legibility issue found in the gradient demo at mobile.
- atmospheric-glass: unchanged (no `backdrop` declared → generic "declare a
  backdrop" advisory); still passes clean.

Docs synced to match: `references/glass.md` (§5, open Q #3, appendix),
`references/gradient.md` (§5 advisory), `SKILL.md` (gotcha + glass pointer), and
the `validate.py` docstring. Skill re-zipped.
