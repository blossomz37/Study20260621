---
version: alpha
name: BookHub
description: >-
  A warm, literary design system for a flip-gallery book site. Evolves the
  "Shelf & Spine" pilot into the production system behind demo/books/site: the
  same paper-and-ink palette, Fraunces/Inter type, and 0.45s flip, plus a
  cover-typography concern that bakes genre-appropriate titling onto textless
  covers and a Kindle-ratio + thumbnail-legibility QA contract. Reuses the
  motion, gradient, and glass (blur/shadow) extensions; adds NO new token type.
colors:
  primary: "#3a2d28"
  primary-strong: "#241b17"
  on-primary: "#faf6f0"
  secondary: "#9a6a4f"
  on-secondary: "#faf6f0"
  tertiary: "#b8553a"
  on-tertiary: "#faf6f0"
  neutral: "#f7f3ee"
  surface: "#f7f3ee"
  surface-container: "#efe7dd"
  surface-container-high: "#e4d8ca"
  on-surface: "#2a211c"
  on-surface-variant: "#5c5048"
  outline: "#cbbfb2"
  error: "#9a3412"
  on-error: "#faf6f0"
  # --- cover-typography role colors (baked into cover rasters, not site chrome) ---
  cover-ink-light: "#f2f6ff"      # title/author over a dark text zone (Last Word, Signal)
  cover-ink-dark: "#241f1a"       # title/author over a light cream zone (Julian Pike)
  cover-scrim: "rgba(4, 6, 14, 0.86)"   # translucent darkening overlay; alpha => glass
  cover-cream-zone: "#efe6d2"     # the measured cream negative-space backdrop
typography:
  display-lg:
    fontFamily: Fraunces
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.05
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Fraunces
    fontSize: 28px
    fontWeight: 600
    lineHeight: 1.1
  title-md:
    fontFamily: Fraunces
    fontSize: 22px
    fontWeight: 600
    lineHeight: 1.15
  body-md:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.45
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: 0.08em
  label-cta:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 600
    lineHeight: 1
    letterSpacing: 0.02em
  # --- cover-typography ROLES (defaults; each book OVERRIDES the face as instance
  #     data in covers/<slug>/cover-spec.yaml, per the genre->face method below) ---
  cover-title:
    fontFamily: Anton          # default = the modern impact convention; overridden per genre
    fontSize: 220px            # nominal; compose.py auto-fits into the safe zone
    fontWeight: 700
    lineHeight: 1.04
    letterSpacing: 0em
  cover-author:
    fontFamily: Oswald
    fontSize: 58px
    fontWeight: 500
    lineHeight: 1.0
    letterSpacing: 0.12em
rounded:
  sm: 4px
  md: 8px
  cover: 6px
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gallery-gap: 24px
  cover-aspect: "2 / 3"
  cover-safe-inset: 96px        # min margin from cover edge to baked title block
motion:
  flip:
    property: transform
    duration: 450ms
    easing: ease
  none:
    duration: 0ms
    easing: linear
gradients:
  # Backdrops exist ONLY so the linter can check baked title contrast against the
  # text zone's worst-case (lowest-contrast) stop — the glass-module discipline.
  cover-dark-backdrop:
    type: linear
    angle: 180deg
    stops:
      - { color: "#11141c", position: "0%" }
      - { color: "#2b2620", position: "100%" }   # worst case: darkened amber/city glow
  cover-cream-backdrop:
    type: linear
    angle: 180deg
    stops:
      - { color: "#efe6d2", position: "0%" }
      - { color: "#e4d8ca", position: "100%" }   # worst case: deepest cream/paper tone
shadow:
  rest:
    offsetX: 0
    offsetY: 4px
    blur: 16px
    spread: 0
    color: "rgba(42, 33, 28, 0.14)"
  cover-title-glow:
    offsetX: 0
    offsetY: 0
    blur: 36px
    spread: 0
    color: "rgba(0, 0, 0, 0.55)"   # soft dark glow so light titles survive bright art
components:
  book-flip:
    perspective: 800px
    rounded: "{rounded.cover}"
    shadow: "{shadow.rest}"
  book-flip-inner:
    transition: "{motion.flip}"
  book-flip-front:
    backgroundColor: "{colors.surface-container}"
    rounded: "{rounded.cover}"
  book-flip-back-image:
    rounded: "{rounded.cover}"
  book-flip-back-info:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.cover}"
    padding: "{spacing.lg}"
  book-flip-title:
    textColor: "{colors.on-surface}"
    typography: "{typography.title-md}"
  book-flip-meta:
    textColor: "{colors.on-surface-variant}"
    typography: "{typography.label-caps}"
  book-flip-cta:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-cta}"
    rounded: "{rounded.sm}"
    padding: "{spacing.md}"
  book-flip-cta-hover:
    backgroundColor: "{colors.primary-strong}"
  # --- cover text zones: two legibility regimes the three books actually use ---
  cover-dark:
    typography: "{typography.cover-title}"
    textColor: "{colors.cover-ink-light}"
    backgroundColor: "{colors.cover-scrim}"        # translucent => glass advisory path
    backdrop: "{gradients.cover-dark-backdrop}"    # contrast checked vs worst-case stop
    shadow: "{shadow.cover-title-glow}"
    padding: "{spacing.cover-safe-inset}"
  cover-cream:
    typography: "{typography.cover-title}"
    textColor: "{colors.cover-ink-dark}"
    backgroundColor: "{colors.cover-cream-zone}"   # opaque cream => normal AA check
    padding: "{spacing.cover-safe-inset}"
---

# BookHub

## Overview

BookHub is the production design system for a flip-gallery book site. It evolves
the **Shelf & Spine** pilot — keeping its warm, literary, paper-and-ink identity —
and adds the one concern a pilot of token-rendered fake covers didn't have: real
**cover typography**. The gallery shows three real books as interactive flip
cards; each front face is a real cover with genre-appropriate titling baked into
the image, and each back face is an info panel (title, author, blurb, metadata,
buy action) drawn from the book's dossier.

The personality is **warm, literary, and tactile** — paper and ink rather than
glass and neon. Browsing should feel like a thoughtfully curated indie bookshop:
unhurried, legible, quietly premium. The signature gesture is a single
0.45-second flip, used sparingly so it stays special.

Two layers cooperate and must not be confused:

- **Site chrome** — the gallery, cards, info faces, and the flip. Rendered live
  from the exported tokens (`dist/tokens.css`); uses only Fraunces + Inter.
- **Cover typography** — title + author *baked into the cover raster* by
  `tools/cover-typography/compose.py`. The web pages never load the cover fonts
  (zero web-font cost); the design system only governs *how* the baking is done.
  The **method is the system; the three faces are data.**

## Colors

The palette is rooted in warm neutrals — limestone paper and espresso ink — with
a single earthy accent reserved for action.

- **Primary (Espresso #3a2d28):** the buy action and strongest text. Reads as ink.
- **Secondary (Clay #9a6a4f):** supporting accents and series labels.
- **Tertiary (Terracotta #b8553a):** the lone vivid accent, at most once per card.
- **Neutral / Surface (Limestone #f7f3ee):** the gallery background; lets covers
  carry the color.
- **Surface Container (Parchment #efe7dd):** the info back face and the loading
  placeholder behind a cover.
- **On-Surface (Ink #2a211c):** warm near-black for titles and body.
- **On-Surface Variant (Slate-Brown #5c5048):** uppercase metadata, kept secondary.

All foreground/background pairings used by **site-chrome** components meet WCAG AA
(4.5:1 for normal text).

### Cover ink & scrim

Cover text is baked, so its legibility is governed by a **QA contract** (below),
not by live CSS — but its colors are still tokens so the system is one source of
truth:

- **Cover Ink Light (#f2f6ff):** a cool-tinted off-white for titles over dark art
  zones (The Last Word's amber sky, The Signal's night). Pure white clips against
  bright cloud/galaxy patches; the cool tint also rhymes with the art's accents.
- **Cover Ink Dark (#241f1a):** a warm near-black for titles over light cream
  negative space (Julian Pike). Picked from the art (the limo body), so the type
  feels integral, not pasted on.
- **Cover Scrim (rgba(4,6,14,0.86)):** a translucent darkening overlay laid over a
  *bright* text zone so light text clears AA. It is **glass**: its alpha means a
  flat WCAG check against the fill is meaningless, so the `cover-dark` component
  declares a **`backdrop`** and the linter checks the ink against the backdrop's
  **worst-case (lowest-contrast) stop** — the same C5 discipline as the glass
  module. A scrim is applied only where the art demands it (none over clean cream).

## Typography

Two families carry the **site**: **Fraunces** (literary serif) for titles/display
and **Inter** for body and UI labels. Metadata is uppercase Inter with generous
tracking, to read as cataloguing detail.

**Cover typography is a separate, per-genre concern.** The system defines two
**roles** — `cover-title` and `cover-author` — with default faces; each book then
**overrides** the face as instance data in `covers/<slug>/cover-spec.yaml`. The
roles are real tokens; the faces filling them are values.

**The genre → face selection method** (how an override is chosen, grounded in
2024–2026 comps):

1. Name the genre and its current cover convention from **recent (2024–2026) real
   comps**, not memory. Dystopian/techno thrillers → bold condensed/geometric
   UPPERCASE sans as the dominant hook (the "title is 80% of the cover" era).
   Vintage/elegant capers → high-contrast Didone display serif, Title Case.
2. Pick the face **from the curated OFL library first** (33 families); fetch an
   outside OFL face only if the genre genuinely needs one no library face serves.
3. Match the face to *this specific art*: case, weight, and tracking that sit in
   the art's actual text zone (dark sky → light ink + scrim; cream → dark ink).

The three current faces (all in-library, all OFL):

| Book | Genre | Title face | Author face | Treatment |
|---|---|---|---|---|
| The Last Word | post-apoc dystopian thriller | **Anton** | Oswald 500 | UPPERCASE, tight, ice-white + scrim |
| The Signal | YA digital / surveillance thriller | **League Spartan** 800 | Montserrat 500 | UPPERCASE, tracked, near-white + scrim |
| Julian Pike | elegant vintage caper | **Bodoni Moda** (opsz→display) | Marcellus | Title Case, dark ink on cream, no scrim |

## Layout & Spacing

The gallery is a **responsive grid** of cover cards, each a fixed **2:3 portrait**
(`spacing.cover-aspect`) so covers line up regardless of source dimensions. An 8px
base scale governs rhythm; cards flow with a 24px gap (`spacing.gallery-gap`); the
info face uses 24px (`spacing.lg`) internal padding.

For **covers**, `spacing.cover-safe-inset` (96px on the 1600×2560 master) is the
minimum margin from any cover edge to the baked title block — the tool's auto-fit
never lets type cross it.

## Elevation & Depth

Depth is **physical and motion-borne**, not shadow-heavy; the flip itself is the
primary cue.

- **3D context:** each card sets `perspective: 800px`; the inner element uses
  `transform-style: preserve-3d`; both faces use `backface-visibility: hidden`.
- **Rest shadow:** a soft low shadow (`shadow.rest`, `0 4px 16px rgba(42,33,28,
  0.14)`) lifts each cover off the limestone background.
- **Cover title glow:** `shadow.cover-title-glow` is a soft dark outer glow baked
  *behind light cover titles* so individual letters survive over the brightest
  patch of art (a galaxy core, distant city lights). It is a legibility aid, not
  decoration, and is omitted for dark-on-cream titles.

## Shapes

The shape language is **soft-rectangular** — covers are rectangles with a small 6px
radius (`rounded.cover`), the corner softness of a trade paperback.

- **Both flip faces share `rounded.cover`** or the corners tear mid-flip.
- **Buttons** use the tighter 4px `rounded.sm` to read as a control.

## Components

### Book Flip Card

The signature component. Structure: an outer `book-flip` (sets `perspective`,
carries `shadow.rest`), an inner `book-flip-inner` (rotates, carrying the
`{motion.flip}` transition), and two absolutely-positioned faces.

- **Front (`book-flip-front`):** the real baked cover image over a parchment
  placeholder, in a 2:3 box with width/height set so covers don't layout-shift.
- **Back:** either `book-flip-back-image` or `book-flip-back-info` (a parchment
  info panel). The back face is pre-rotated 180° so it reads correctly post-flip.

The flip is **CSS-driven on hover** (gated behind `@media (hover: hover)`), with a
JS-toggled `is-flipped` class for tap and keyboard (Enter/Space); Escape and
click-outside close it.

### Book Info Face

`book-flip-back-info` houses `book-flip-title` (Fraunces), `book-flip-meta`
(uppercase Inter metadata in slate-brown), a blurb in `body-md`, and an optional
`book-flip-cta`. The buy action is a real link living on the back face: the card's
flip handler ignores clicks inside the CTA so the link is never swallowed.

### Cover (baked title zone)

Two components capture the two legibility regimes the three books use. Both
reference the `cover-title` typography role and `cover-safe-inset`; they differ
only in ink and whether a scrim is present.

- **`cover-dark`** — light ink (`cover-ink-light`) over a dark art zone, darkened
  by the translucent `cover-scrim`. Because the scrim is glass, the component
  declares a `backdrop` (`cover-dark-backdrop`); the linter reports the ink's
  contrast against that backdrop's **worst-case stop** as an advisory, and a baked
  `cover-title-glow` reinforces it. Used by The Last Word and The Signal.
- **`cover-cream`** — dark ink (`cover-ink-dark`) over the opaque `cover-cream-zone`,
  no scrim. This is an ordinary opaque pair and is held to full WCAG AA. Used by
  Julian Pike.

The **author byline** sits at the **foot of the cover** (not under the title), in its
own zone, using the `cover-author` role. Because the bottom of cover art is usually
busy — rubble, a desk, a collage — the byline rides its **own gradient band**
(`author_scrim`): a bottom-anchored translucent scrim that doubles as contrast aid and
depth/texture. It is the same scrim primitive as the title's, just bottom-directed and
tuned per art: a **dark** band lifts a light byline over dark foregrounds (Last Word,
Signal); a **cream footer band** lifts a dark byline over a light collage and reads as
an intentional vignette with the art softly showing through (Julian Pike). An optional
hairline **divider rule** above the byline adds a vintage/editorial touch. The per-book
face, ink, zone, scrim, and rule are instance data in `cover-spec.yaml`.

### The QA contract (enforced by compose.py → report.json)

A baked cover is "done" only when its `report.json` passes every gate — the
cover-typography analogue of how motion collapses under reduced-motion:

- **Kindle ratio** 1.600 ± 0.5% (source normalized + upscaled to 1600×2560).
- **Thumbnail legibility:** rendered title cap-height ≥ 14px at a 160px-wide
  thumbnail. *A long literary Didone title (Julian Pike) may lower this floor with
  a recorded rationale when its contrast is far above the minimum — real long-title
  covers make the same trade.*
- **Contrast** ≥ 4.5:1 for title and author over their text zone (worst-case stop,
  after any scrim).
- **≤ 2 title lines** by default (a 5-word title may declare a higher `max_lines`).
- **OFL fonts only**, recorded per face in `tools/cover-typography/fonts.json`.

### Motion

The single `motion.flip` token (`transform 450ms ease`) drives every flip. It is
gated by `prefers-reduced-motion`: when reduced motion is preferred, the effective
duration collapses to 0 (state changes instantly). The exporter bakes that override
into `tokens.css`.

## Do's and Don'ts

- **Do** keep the flip as the system's one signature motion — animate `transform`
  only, at the single `motion.flip` value.
- **Do** maintain the 2:3 cover aspect ratio for every card, and set each cover's
  width/height so it never layout-shifts.
- **Do** apply `rounded.cover` to both faces so corners don't tear during the flip.
- **Do** keep the buy action reachable on the flipped face (don't let the flip
  handler swallow the CTA click).
- **Do** choose a cover title face by the **genre → face method** above, grounded in
  recent real comps, from the OFL library first.
- **Do** put baked light titles only over zones the scrim can carry to AA, and
  measure every cover against the QA contract before shipping it.
- **Do** anchor the author byline at the foot of the cover on its own gradient band —
  use a translucent scrim there for contrast *and* depth (a dark band over dark art, a
  cream footer over a light collage), not just flat text dropped onto busy pixels.
- **Don't** vary flip durations between cards or sites — reference the token.
- **Don't** use the terracotta accent more than once per card.
- **Don't** rely on `:hover` alone — provide tap and keyboard flips.
- **Don't** load cover display fonts on the page — covers are rasters; the chrome
  stays Fraunces + Inter.
- **Don't** put `overflow`, `filter`, or `clip` on an element between the
  perspective context and the faces; it flattens the 3D flip in Safari.
