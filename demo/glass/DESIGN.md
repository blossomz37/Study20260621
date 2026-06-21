---
version: alpha
name: Aurora Glass
description: >-
  Frosted-glass cards floating over the Aurora gradient backdrop. Composes the
  `gradients` module (Module A) as the backdrop and adds two new value groups:
  `blur` (no DTCG type — a documented local invention) and `shadow` (native DTCG
  composite). Pilot case for the glass effect family and the C5 contrast fix.
colors:
  primary: "#5b21b6"
  primary-strong: "#4c1d95"
  on-primary: "#f5f3ff"
  secondary: "#2563eb"
  tertiary: "#db2777"
  accent: "#f59e0b"
  surface: "#0b1020"
  on-surface: "#eef0fb"
  on-surface-variant: "#c7cbe0"
  glass-fill: "rgba(255,255,255,0.10)"
  glass-fill-strong: "rgba(255,255,255,0.16)"
  glass-border: "rgba(255,255,255,0.22)"
  glass-shadow: "rgba(8,10,25,0.45)"
typography:
  display-lg:
    fontFamily: Sora
    fontSize: 44px
    fontWeight: 700
    lineHeight: 1.08
    letterSpacing: -0.02em
  title-md:
    fontFamily: Sora
    fontSize: 22px
    fontWeight: 600
    lineHeight: 1.2
  body-lg:
    fontFamily: Inter
    fontSize: 17px
    fontWeight: 400
    lineHeight: 1.6
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: 0.12em
rounded:
  md: 12px
  lg: 20px
  full: 9999px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
  xl: 64px
gradients:
  hero:
    type: linear
    angle: 135deg
    stops:
      - { color: "{colors.primary}",  position: 0% }
      - { color: "{colors.tertiary}", position: 55% }
      - { color: "{colors.accent}",   position: 100% }
blur:
  glass: 20px
  glass-strong: 40px
shadow:
  glass:
    offsetX: 0
    offsetY: 8px
    blur: 32px
    spread: 0
    color: "{colors.glass-shadow}"
components:
  glass-card:
    backgroundColor: "{colors.glass-fill}"
    backdropBlur: "{blur.glass}"
    borderColor: "{colors.glass-border}"
    shadow: "{shadow.glass}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
    backdrop: "{gradients.hero}"
  glass-card-title:
    textColor: "{colors.on-surface}"
    typography: "{typography.title-md}"
  glass-badge:
    backgroundColor: "{colors.glass-fill-strong}"
    backdropBlur: "{blur.glass-strong}"
    borderColor: "{colors.glass-border}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.full}"
    padding: "{spacing.sm}"
    backdrop: "{gradients.hero}"
---

# Aurora Glass

## Overview

Aurora Glass is a frosted-glass card system that floats over the **Aurora
gradient** (the Module A backdrop). The personality is **luminous, layered, and
tactile** — panels of frosted glass catching the violet→pink→amber light beneath
them. It is the composition proof: the gradient module supplies the backdrop, and
this module adds only what glass needs on top of it — translucency, blur, a
hairline border, and a soft shadow.

Glassmorphism is four ingredients: a **translucent fill**, a **backdrop blur**, a
**hairline border**, and a **soft drop shadow**. This system tokenizes each so
"the same glass" renders identically everywhere — and encodes the one contract
glass can't escape: *its legibility depends on what's behind it.*

## Colors

Aurora Glass shares the Aurora palette and adds four glass-specific values:

- **Glass Fill (`rgba(255,255,255,0.10)`):** The translucent white surface. At 10%
  opacity it tints whatever shows through rather than hiding it.
- **Glass Fill Strong (`rgba(255,255,255,0.16)`):** A denser fill for smaller chips
  (the badge) that need a touch more presence.
- **Glass Border (`rgba(255,255,255,0.22)`):** The hairline top/edge highlight that
  reads as the lit rim of a glass panel.
- **Glass Shadow (`rgba(8,10,25,0.45)`):** A cool, deep shadow that lifts the card
  off the gradient.
- **On-Surface (`#eef0fb`):** Near-white text. **Note:** measured against the glass
  fill alone this is white-on-white — but the card always sits over the *darker*
  end of the Aurora backdrop, where it is comfortably legible. That backdrop
  dependency is declared on the component (`backdrop: {gradients.hero}`) so the
  linter checks contrast against the backdrop's darkest stop, not the fill.

## Typography

- **Display:** Sora Bold for the page headline.
- **Titles:** Sora Semi-Bold for card titles.
- **Body:** Inter for card copy.
- **Labels:** Inter uppercase, wide tracking, for the glass badge.

## Layout

Cards sit centered over a full-bleed Aurora backdrop with generous internal
padding (`spacing.lg`). The backdrop is the same `{gradients.hero}` token the
gradient demo uses — one source, two demos.

## Elevation & Depth

Depth here is **glass over light**. The stack, back to front: the Aurora gradient
backdrop → the translucent card fill → the backdrop blur (`{blur.glass}`) frosting
what shows through → the hairline border → the soft drop shadow
(`{shadow.glass}`) grounding the card. The blur is what makes it read as *glass*
rather than a flat translucent rectangle.

`blur` is a genuine invention point: **DTCG has no backdrop-filter / blur type.**
It is carried here as a minimal dimension group and documented as a local
extension (see `references/glass.md`), with the gap noted in the DTCG export's
`$extensions`.

## Shapes

Soft-rectangular. Cards use `rounded.lg` (20px); the badge is a full pill
(`rounded.full`).

## Components

### Glass Card

`glass-card` is the signature component: a `{colors.glass-fill}` surface with
`backdropBlur: {blur.glass}`, a `{colors.glass-border}` hairline, a
`{shadow.glass}` drop shadow, and `on-surface` text. It declares
`backdrop: {gradients.hero}` — not a rendered property but a **contract**: it tells
the linter (and the reader) what this glass floats over, so text contrast is
verified against the backdrop's darkest stop rather than the translucent fill.

A consumer must apply the blur to **both** `backdrop-filter` and
`-webkit-backdrop-filter` (Safari), and should provide a slightly more opaque
fallback fill where `backdrop-filter` is unsupported, so the text never strands on
bare gradient.

### Glass Badge

`glass-badge` is a denser, more-blurred pill (`{blur.glass-strong}`,
`{colors.glass-fill-strong}`) for an eyebrow label on the card.

## Do's and Don'ts

- **Do** apply `backdropBlur` to both `backdrop-filter` and `-webkit-backdrop-filter`.
- **Do** declare each glass component's `backdrop` so its contrast is checked
  against what it actually floats over, not its translucent fill.
- **Do** keep glass text on the darker end of the backdrop where it's legible.
- **Do** compose the backdrop from the `gradients` module — never bake a literal
  gradient into the glass system.
- **Don't** treat the glass-fill contrast warning as a failure — translucent and
  blurred surfaces are advisory by design (the C5 rule).
- **Don't** animate the blur or add noise/grain or a one-sided "shine" inner border
  here — those are out of scope (motion / v2).
- **Don't** stack an `overflow`/`filter` ancestor that would clip the backdrop blur.
