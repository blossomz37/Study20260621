# Claude's assessment of https://rgdbrandingawards.com/



I dug into the live DOM and CSS of the JUDGES grid. Here's the full breakdown.

## What the animation actually is

When you hover a judge, the tile does a **3D card flip on the Y axis**. The front face is the portrait photo; the back face rotates into view showing the judge's name, studio, and city on a colored background. It's not a fade or a crossfade and, despite appearances, the shape does **not** morph from circle to square. Each tile has a fixed shape (some are circles, some squares, some have a single rounded corner), and the front and back share that same shape. The illusion of "circle becoming a square card" you noticed is really just adjacent tiles having different fixed shapes, plus the colored back face reading as a different object than the gray photo.

The mechanism is the textbook flip-card recipe:

- An outer `.judge-tile` sets `perspective: 800px` (the 3D vanishing point) and `cursor: pointer`.
- An inner `.judge-inner` is the thing that rotates. It has `transform-style: preserve-3d` so its children live in real 3D space, and `transition: transform 0.45s`.
- Two absolutely-positioned, overlapping faces (`.judge-front` and `.judge-back`), both with `backface-visibility: hidden`. The back is pre-rotated with `transform: rotateY(180deg)` so it sits facing away until the flip.
- On hover, a single rule (`:hover .judge-inner { transform: rotateY(180deg); }`) spins the inner container 180°. The front rotates away, the back rotates forward.

A couple of nice touches in their implementation: the hover rule is wrapped in `@media (hover: hover)` so touch devices don't trigger it on tap, and there's a parallel `.is-flipped` class that does the same rotation — meaning they drive flips via JavaScript too (likely for keyboard/click on touch). They also respect `@media (prefers-reduced-motion)` (transition only applies when motion is allowed) and have a global `body[data-animations-paused]` switch — that's the pause button in the bottom-right corner of the page that kills the transition entirely.

## Terms to know to reverse-engineer it

The vocabulary you'd search for: CSS 3D transforms, `perspective` and `perspective-origin`, `transform-style: preserve-3d`, `backface-visibility: hidden`, `rotateY()`, and "CSS flip card / card flip." Supporting concepts: the stacking of two `position: absolute; inset: 0` faces, `transition` timing/easing, the `@media (hover: hover)` and `(pointer)` media queries for touch handling, and `prefers-reduced-motion` for accessibility.

## Were they clever / outside the box?

The flip itself is a well-known pattern, so it's a conventional technique done cleanly rather than a novel trick. Where they showed taste rather than raw novelty: they applied the flip across a **mosaic grid of mixed shapes** (circles, squares, and tiles with a single 245px rounded corner like `border-radius: 0 245px 0 0`) and mixed brand colors (magenta, pink, orange, blue), with a few non-interactive `--accent` tiles sprinkled in (`cursor: default`, no back face) purely as decorative color blocks. That variety is what makes a plain flip feel like a designed system. The genuinely thoughtful, "above and beyond" parts are the accessibility/control layer: a site-wide animation pause toggle, reduced-motion support, and the dual hover-class + `.is-flipped`-class approach so it works for pointer, touch, and programmatic triggers — not just `:hover`.

## Gotchas and blockers if you build this yourself

The classic ones that bite people:

The most common failure is forgetting `transform-style: preserve-3d` on the rotating element (or putting `perspective` in the wrong place), which makes the card flip "flat" with no depth or makes the back face never appear. Similarly, omitting `backface-visibility: hidden` means you'll see a mirror-reversed photo bleeding through during and after the flip.

Watch the rotation axes: the back face must be **pre-rotated 180°** so that when the parent rotates 180°, the back ends up at 0° (facing you) and reads correctly — otherwise your text comes out mirror-imaged. Keep `overflow: hidden` and matching `border-radius` on *both* faces or the rounded/circular clipping breaks mid-flip.

Touch devices are a real blocker: `:hover` on mobile is sticky and unreliable, which is exactly why this site added a JS-driven `.is-flipped` class and gated the hover rule behind `@media (hover: hover)`. Plan a tap/focus interaction from the start.

Other practical traps: `preserve-3d` is famously fragile when you nest more transforms or add `overflow` on intermediate ancestors (Safari in particular will flatten it); a parent with `overflow: hidden` or certain `filter`/`clip` properties can collapse the 3D context. Accessibility-wise, you should honor `prefers-reduced-motion` and make sure the back-face content is reachable/announced properly (note they marked the back `aria-hidden="true"`, so if the info matters for screen readers you'd want a non-visual equivalent). Finally, flipping many tiles at once can cause repaint jank, so promoting layers and keeping transitions to `transform` (which they do — 0.45s on `transform` only) matters for smoothness.

---

Short answer: **the core flip is 100% HTML/CSS and needs no JavaScript. But to match what this site actually ships, you need a small amount of scripting for three things — touch support, keyboard support, and the pause/reduced-motion controls.**

Here's what I confirmed by inspecting their code.

The flip animation itself is pure CSS. The whole effect runs off one hover rule (`:hover .judge-inner { transform: rotateY(180deg) }`) plus the `perspective`, `preserve-3d`, and `backface-visibility` setup. On a desktop with a mouse, no JS touches the animation at all. So if your only requirement is "portrait flips to an info card on hover," HTML and CSS fully accomplish it.

What their JavaScript adds is everything *around* the hover. I found exactly one small script (593 characters) responsible for the flip interactivity, and it does three specific things:

It handles **touch devices**. The script checks `matchMedia` for a *coarse* pointer (i.e. a finger, no real hover) and, on those devices, listens for `click` and toggles an `.is-flipped` class to flip the card on tap. This exists because the CSS hover rule is deliberately gated behind `@media (hover: hover)`, so it does nothing on phones. Without this script, your cards would be un-flippable on mobile.

It handles **keyboard accessibility**. It listens for key events so a keyboard user can focus a tile and flip it, rather than the effect being mouse-only.

Separately, a few other inline scripts manage the global **pause-animations toggle** (that button in the corner sets `body[data-animations-paused]`) and wire up `prefers-reduced-motion`. The CSS already respects both, but the scripts are what flip the switches and persist the choice.

So it comes down to your scope:

If you just want the desktop hover flip as a portfolio/demo piece, write it in plain HTML/CSS and you're done — genuinely no scripting required. If you want production parity with this site (works on phones via tap, works with a keyboard, and has an animation pause control), you need roughly 15–30 lines of JavaScript: a `matchMedia('(pointer: coarse)')` check, a click/keydown listener that toggles an `.is-flipped` class, and optionally the pause toggle. The CSS already provides the `.is-flipped` hook to make that JS trivial — the script only ever toggles a class; it never computes or drives the animation itself.

