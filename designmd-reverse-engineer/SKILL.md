---
name: designmd-reverse-engineer
description: >-
  Reverse-engineer a live website (or one specific UI effect/animation on it)
  into a portable DESIGN.md design system, validate it with a linter, export it
  to Tailwind / DTCG / CSS-variables, then recreate the effect FROM the exports
  to prove the recovered system transfers. Use this whenever the user wants to
  capture, recover, copy, clone, or replicate a site's visual identity or a
  specific effect (flip cards, hover animations, glassmorphism, gradients,
  motion) as reusable design tokens — especially when they care about
  consistency across multiple sites, a single source of truth, a DESIGN.md /
  design tokens / Stitch / Google Labs design file, or "make this ours so every
  page uses it." Trigger even if the user just says "I saw this effect on site X,
  recreate it" or "turn this site's look into tokens" — the value of this skill
  over ad-hoc copying is that it produces a linted, exportable, normative spec
  instead of one-off CSS that drifts.
---

# Reverse-engineer a web effect/site into a DESIGN.md system

## Why this workflow exists

Copying CSS off a site gives you one-off styles that drift the moment you reuse
them on a second page or project. This workflow recovers the design as a
**normative DESIGN.md** (typed tokens + rationale) that you can lint, export to
Tailwind/DTCG/CSS-vars, and re-render anywhere — so "the same look" is enforced,
not re-typed. The proof that it worked is recreating the original effect using
*only* the exported tokens.

Use it for a whole site's identity or for one striking effect (a flip card, a
glass panel, a gradient hero, a motion signature).

## The boundary that makes this honest

A visual effect splits into three layers. Keep them in their right home:

- **Values** (colors, type, radius, spacing, durations, easings) → **tokens** in
  DESIGN.md. These are what transfer and what the linter/exporter operate on.
- **Spatial structure** (`perspective`, `transform-style: preserve-3d`,
  `backface-visibility`, absolute-positioned faces) → **component properties** +
  prose. Mechanics, not values.
- **Interaction/behavior** (hover vs tap vs click-to-pin, keyboard handling,
  click-guards, reduced-motion gating) → **prose** (Components + Do's/Don'ts) and
  the recreation code. Event wiring is not a token; don't pretend it is.

Trying to tokenize structure or behavior produces fragile nonsense. Naming this
boundary up front keeps the DESIGN.md clean and the recreation faithful.

## Workflow

### 1. Extract ground truth (don't guess, don't trust a summary)

Pull the *real* CSS/JS, not a prose description and not a WebFetch markdown
flatten (which drops the CSS/JS you need).

```bash
curl -sL -A "Mozilla/5.0" "<url>" -o /tmp/page.html
# find stylesheets/scripts:
grep -oiE '<(link[^>]+href|script[^>]+src)="[^"]+"' /tmp/page.html
# fetch the CSS bundles (e.g. Astro emits /_astro/*.<hash>.css) and grep the rules:
curl -sL "<css-url>" -o /tmp/site.css
grep -oE '\.<class-prefix>[a-z-]*[^{]*\{[^}]*\}' /tmp/site.css
```

Also extract inline `<script type="module">` blocks (use a quick Python regex)
and de-minify the small ones — that's where touch/keyboard/pause behavior lives.
Capture exact values: durations, easings, perspective, radii, colors, the markup
structure, and the interaction model.

Write a short spec of what the effect actually is and how it works, grounded in
the extracted code. (Don't skip this — it's what you'll author tokens from and
what catches "it looks like X but is really Y" illusions.)

### 2. Author the DESIGN.md

Read `references/designmd-format.md` for the schema, token groups, and the fixed
section order. Then write the frontmatter tokens + the prose sections.

- Map the recovered palette/type/radii/spacing to tokens.
- For any **motion** (transitions, animation timing), use the motion extension —
  read `references/motion-extension.md`. Time/easing become `motion` tokens;
  `perspective` becomes a component property; interaction stays prose.
- For any **gradient** background (hero wash, glow, swatch), use the gradients
  extension — read `references/gradient.md`. Stops become a `gradients` token
  (orientation in `$extensions`); the element it paints is a component
  (`backgroundImage`); animating it is a separate `motion` token.
- For **glassmorphism** (frosted panels, translucent cards), use the glass
  extension — read `references/glass.md`. Blur becomes a `blur` token (a
  documented invention — DTCG has no blur type); the drop shadow becomes a native
  DTCG `shadow` token; translucent fill/border are `colors` used with alpha; the
  component declares `backdropBlur`/`borderColor`/`shadow` and a `backdrop` token
  so its contrast is checked against the backdrop, not the fill.
- Define the effect's component(s) under `components:`, referencing primitives
  with `{group.token}` so the indirection survives export.
- Ensure component `backgroundColor`/`textColor` pairs meet WCAG AA (the linter
  checks this).

### 3. Lint until green

```bash
python3 scripts/validate.py path/to/DESIGN.md
```

Exit code 1 means there's an **error** (broken token reference, missing primary,
out-of-order sections, bad motion value). Warnings/info don't fail. Fix errors
and re-run. A clean run means the spec is internally consistent and exportable.

Tip: a *failing* lint on exactly the new construct you added (e.g. a motion
reference an un-extended linter doesn't know) is positive evidence the rest is
correct and the extension is what's needed — worth showing the user.

### 4. Export to standard targets

```bash
python3 scripts/export.py path/to/DESIGN.md --out path/to/dist
```

Produces, from the one source:
- `tokens.css` — CSS custom properties (primitives + resolved component vars,
  with a `prefers-reduced-motion` override baked in).
- `tailwind.config.js` — `theme.extend` (colors, borderRadius, spacing,
  fontFamily/fontSize, transitionDuration/timingFunction/property).
- `tokens.json` — DTCG format (color/typography/dimension/transition types).

### 5. Recreate the effect FROM the exports (the transfer proof)

Build a small demo that consumes **only** the exported tokens — every color,
font, radius, spacing, and timing via `var(--…)` (or Tailwind classes). The only
literals allowed are structural mechanics (per the boundary above). Port the
interaction model from the extracted script.

If the demo looks and behaves right using nothing but the exports, the design
system transferred — that's the whole point. If you had to hard-code a brand
value to make it look right, that value was missing from the tokens; add it and
re-export.

### 6. Capture evidence

Serve the demo and verify both visually and at the computed-style level:

```bash
python3 -m http.server 8765 --directory path/to/demo
```

Screenshot resting + active states. Confirm tokens resolved by reading computed
styles (e.g. the flip's `transition` should compute to your `motion.flip` value;
a component bg should resolve through the `{ref}` chain to the literal color).
Store screenshots + the computed-style check as evidence.

## Gotchas (these bite people)

- **WebFetch won't help** — it returns a markdown summary, not the CSS/JS. Always
  `curl` the raw assets.
- **3D flips**: `perspective` goes on the *outer* element, `preserve-3d` on the
  rotating one; both faces need `backface-visibility: hidden`; the back face must
  be pre-rotated 180° or its text mirrors. `overflow`/`filter` on an intermediate
  ancestor flattens the 3D context in Safari.
- **Touch/keyboard**: `:hover` is unreliable on touch. Gate hover behind
  `@media (hover: hover)` and drive tap/keyboard via a JS-toggled class. If the
  back face has a real link/button, add a click-guard so the flip doesn't swallow
  it, and a click-to-pin so hover users can reach it.
- **Contrast on translucent/glass/gradient surfaces**: the WCAG check would resolve
  an `rgba(...)` background to opaque RGB and ignore the backdrop, so glass
  components used to false-positive. With the glass/gradient extensions, the linter
  detects a translucent/blurred/gradient surface and downgrades the finding to an
  advisory — checking text against the **worst-case (lowest-contrast) stop** of the
  declared `backdrop` (or the gradient itself), not the fill and not the darkest
  stop (which would under-warn light text). Declare a `backdrop` on every glass
  component so that check has something to run against, and heed the advisory:
  keep text over the stops where it stays legible — a non-failing "drops below AA"
  here is a real legibility prompt (see `references/glass.md`).
- **`prefers-reduced-motion`**: honor it. The exporter collapses motion durations
  to 0 under reduced-motion; keep that contract in the recreation.

## Extending to a new effect family

The token format has a fixed vocabulary (colors, typography, rounded, spacing,
components) plus this skill's `motion` extension. You *will* hit effects it can't
yet express — motion was just the first gap; gradients, shadows, blur/glass,
scroll-driven animation, and blend modes are the likely next ones. When that
happens, don't bury the value in prose and move on, and don't invent a bespoke
token shape. Extend deliberately, using the same discipline that produced the
motion extension. The protocol:

1. **Triage by the boundary first.** Decide which layer the new thing lives in —
   values / structure / behavior (see "The boundary that makes this honest").
   Only *values* need a new token type; spatial properties become component
   props; behavior stays prose. Most "I need a new token" urges dissolve here.

2. **Mirror the upstream standard — don't invent.** If it really is a new value
   type, model it on the DTCG token spec, which the format already cites. DTCG has
   types for color, dimension, duration, cubicBezier, shadow, gradient, transition,
   and more. Mirroring them means your extension exports to Tailwind/DTCG/CSS for
   free instead of needing a custom translator.

3. **Scope it narrowly; write down what stays out.** Keep the new type to its
   irreducible values (motion = duration + easing, nothing more) and explicitly
   list what does NOT belong in it. A narrow type stays lintable; a kitchen-sink
   type rots.

4. **Prove the gap with a failing lint.** Author the DESIGN.md with the new
   construct and run `scripts/validate.py` *before* teaching the linter about it.
   One error on exactly the new reference — everything else green — is your
   evidence the extension is genuinely needed and the rest is sound. Don't extend
   on a hunch.

5. **Degrade gracefully.** The extended file must still be consumable by tools
   that don't know your extension: a new token group is an optional top-level key,
   and unknown component props are "accept with warning" per the format's
   unknown-content rules. Never emit a file a standard consumer would reject.

6. **Capture behavioral contracts, not just values.** If the source obeys an
   implicit rule around the effect (reduced-motion gating, touch fallback, a
   backdrop assumption), record it as part of the token's contract so it transfers
   too — the way motion tokens collapse under `prefers-reduced-motion`.

7. **Add a module; don't rewrite the core.** Land the extension as new bundled
   pieces — a `references/<effect-family>.md` digest plus matching rules in
   `scripts/validate.py` (validation) and `scripts/export.py` (the three export
   targets). The workflow (steps 1–6) stays unchanged. This skill grows the same
   way the format does: by adding typed groups, not by editing the spine.

Then propose the extension to the format owner the way motion was: problem →
principles → schema → lint rules → export mapping → backward-compat → open
questions. `references/motion-extension.md` is both the worked example and the
template.

## Bundled resources

- `scripts/validate.py` — DESIGN.md linter (stdlib + PyYAML). Mirrors the upstream
  reference rules and implements the motion extension. Run on every DESIGN.md.
- `scripts/export.py` — DESIGN.md → tokens.css / tailwind.config.js / tokens.json.
- `references/designmd-format.md` — the format schema + section order. Read before
  authoring a DESIGN.md.
- `references/motion-extension.md` — the `motion` token group (durations, easings)
  and the `perspective`/`transition` component props. Read when the effect has any
  animation or transition.
- `references/gradient.md` — the `gradients` token group (stops in DTCG `$value`,
  orientation in `$extensions`) and the `backgroundImage` component prop. Read when
  the effect is a multi-stop gradient background (hero wash, glow, swatch).
- `references/glass.md` — the `blur` group (a documented invention; no DTCG type)
  and native DTCG `shadow` group, the `backdropBlur`/`borderColor`/`shadow`/
  `backdrop` component props, and the C5 contrast fix (translucent/blurred surfaces
  → advisory checked against the declared backdrop's worst-case stop). Read for
  glassmorphism.

## Dependencies

Python 3 with PyYAML (`pip install pyyaml`, or system python3 on macOS already has
it). No build step required.
