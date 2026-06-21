---
version: alpha
name: Shelf & Spine
description: >-
  A warm, literary design system for displaying book covers in a gallery that
  flips each cover to reveal the back cover or structured book info. Pilot case
  for the proposed `motion` token extension.
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
motion:
  flip:
    property: transform
    duration: 450ms
    easing: ease
  none:
    duration: 0ms
    easing: linear
components:
  book-flip:
    perspective: 800px
    rounded: "{rounded.cover}"
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
---

# Shelf & Spine

## Overview

Shelf & Spine is a design system for presenting a catalogue of books as an
interactive gallery. Each cover behaves like a physical object: at rest it shows
the front cover; on interaction it flips on its vertical axis to reveal either
the back cover or a structured info panel (title, author, blurb, and a buy
action).

The personality is **warm, literary, and tactile** — paper and ink rather than
glass and neon. It should feel like browsing a thoughtfully curated indie
bookshop: unhurried, legible, and quietly premium. The emotional target is
*invitation* — covers that ask to be picked up. Motion is gentle and physical,
never flashy; a single 0.45-second flip is the system's signature gesture and is
used sparingly so it stays special.

## Colors

The palette is rooted in warm neutrals — limestone paper and espresso ink — with
a single earthy accent reserved for action.

- **Primary (Espresso #3a2d28):** A deep, warm brown used for the buy action and
  the strongest text. Reads as ink, not black.
- **Secondary (Clay #9a6a4f):** A mid warm brown for supporting accents and
  series labels.
- **Tertiary (Terracotta #b8553a):** The lone vivid accent, used for at most one
  highlight per card (e.g. a "New" flag).
- **Neutral / Surface (Limestone #f7f3ee):** The gallery background — a soft warm
  off-white that lets covers, not the chrome, carry the color.
- **Surface Container (Parchment #efe7dd):** A slightly deeper paper tone used
  for the info back face and the placeholder behind a loading cover.
- **On-Surface (Ink #2a211c):** Near-black warm ink for titles and body, chosen
  for maximum legibility against parchment while avoiding pure-black harshness.
- **On-Surface Variant (Slate-Brown #5c5048):** For uppercase metadata
  (author, publisher, year), kept secondary in the hierarchy.

All foreground/background pairings used by components meet WCAG AA (4.5:1 for
normal text).

## Typography

Two families carry the system: **Fraunces** (a literary serif) for titles and
display, and **Inter** for body copy and UI labels.

- **Display & Headlines:** Fraunces Semi-Bold establishes the bookish,
  editorial voice for gallery headings and large book titles.
- **Titles:** Book titles on the info face use Fraunces at 22px so a flipped
  card still reads as "a book," not "a UI panel."
- **Body:** Inter Regular at 15px keeps blurbs comfortable to read in the small
  area of a flipped cover.
- **Labels:** Inter is used for metadata and the buy button. Metadata is strictly
  uppercase with generous letter spacing to read as cataloguing detail.

## Layout & Spacing

The gallery follows a **responsive grid** of cover cards. Each card holds a fixed
**2:3 portrait aspect ratio** (`spacing.cover-aspect`) — the dominant trade
paperback proportion — so covers line up regardless of source image dimensions.

- **Rhythm:** An 8px base scale governs spacing.
- **Grid:** Cards flow in a grid with a 24px gap (`spacing.gallery-gap`);
  card width is fluid (e.g. `min(40vw, 240px)`), height derived from the aspect
  ratio.
- **Info padding:** The flipped info face uses 24px (`spacing.lg`) internal
  padding so text never crowds the rounded corners.

## Elevation & Depth

Depth is **physical and motion-borne**, not shadow-heavy. The flip itself is the
primary depth cue.

- **3D context:** Each card sets `perspective: 800px`; the rotating inner element
  uses `transform-style: preserve-3d`, and both faces use
  `backface-visibility: hidden`.
- **Rest shadow:** A soft, low shadow (`0 4px 16px rgba(42,33,28,0.12)`) lifts
  each cover off the limestone background just enough to read as a discrete
  object.
- **Spine cue:** An optional 1px inner gradient on the left edge of the front
  face suggests a book spine without literal skeuomorphism.

## Shapes

The shape language is **soft-rectangular** — covers are rectangles with a small
6px radius (`rounded.cover`), the corner softness of a real trade paperback.

- **Both faces share the radius.** Front and back must use the identical
  `rounded.cover` or the rounding tears mid-flip.
- **Buttons:** The buy action uses the tighter 4px `rounded.sm` so it reads as a
  control distinct from the cover it sits on.

## Components

### Book Flip Card

The signature component. Structure: an outer `book-flip` (sets `perspective`),
an inner `book-flip-inner` (the element that rotates, carrying the
`{motion.flip}` transition), and two absolutely-positioned faces.

- **Front (`book-flip-front`):** The front cover image over a parchment
  placeholder.
- **Back:** Either `book-flip-back-image` (the back-cover scan) or
  `book-flip-back-info` (a parchment info panel). The back face is pre-rotated
  180° so it reads correctly after the flip.

The flip is **CSS-driven on hover** (gated behind `@media (hover: hover)`), with
a JavaScript-toggled `is-flipped` class providing the same rotation for touch
(tap) and keyboard (Enter/Space) users; Escape and click-outside close it.

### Book Info Face

`book-flip-back-info` houses `book-flip-title` (Fraunces), `book-flip-meta`
(uppercase Inter metadata in slate-brown), a blurb in `body-md`, and an optional
`book-flip-cta`.

### Buy Action

`book-flip-cta` is a solid espresso button with cream label text. Because it is a
real link living on the back face, it must remain reachable when flipped: the
card's flip handler ignores clicks originating inside the CTA so the link is
never swallowed.

### Motion

The single `motion.flip` token (`transform 450ms ease`) drives every flip in the
system. It is gated by `prefers-reduced-motion`: when reduced motion is
preferred, the effective duration collapses to zero (state changes instantly).

## Do's and Don'ts

- **Do** keep the flip as the system's one signature motion — animate `transform`
  only, at the single `motion.flip` value, so every cover flips identically.
- **Do** maintain the 2:3 cover aspect ratio for every card regardless of source
  image size.
- **Do** apply `rounded.cover` to both faces so corners don't tear during the
  flip.
- **Do** keep the buy action reachable on the flipped face (don't let the card's
  flip handler swallow the CTA click).
- **Don't** vary flip durations between cards or sites — reference the token, never
  hard-code a time.
- **Don't** use the terracotta accent more than once per card.
- **Don't** rely on `:hover` alone — provide tap and keyboard flips for touch and
  accessibility.
- **Don't** put `overflow`, `filter`, or `clip` on an element between the
  perspective context and the faces; it can flatten the 3D flip in Safari.
