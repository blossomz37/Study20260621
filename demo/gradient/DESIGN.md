---
version: alpha
name: Aurora Hero
description: >-
  A luminous hero-banner design system built on layered CSS gradients — a violet→
  pink→amber linear wash with a soft radial glow on top. Pilot case for the
  proposed `gradients` token group (stops in DTCG `$value`, orientation in
  `$extensions`).
colors:
  primary: "#5b21b6"
  primary-strong: "#4c1d95"
  on-primary: "#f5f3ff"
  secondary: "#2563eb"
  tertiary: "#db2777"
  accent: "#f59e0b"
  surface: "#0b1020"
  surface-container: "#141a2e"
  on-surface: "#e8eaf2"
  on-surface-variant: "#a9b1c7"
  outline: "#2a3350"
typography:
  display-lg:
    fontFamily: Sora
    fontSize: 56px
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: -0.02em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
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
  lg: 32px
  xl: 64px
gradients:
  hero:
    type: linear
    angle: 135deg
    stops:
      - { color: "{colors.primary}",   position: 0% }
      - { color: "{colors.tertiary}",  position: 55% }
      - { color: "{colors.accent}",    position: 100% }
  glow:
    type: radial
    angle: "circle at 28% 18%"
    stops:
      - { color: "rgba(37,99,235,0.55)", position: 0% }
      - { color: "rgba(37,99,235,0)",    position: 70% }
components:
  hero-banner:
    backgroundImage: "{gradients.hero}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.lg}"
    padding: "{spacing.xl}"
  hero-glow:
    backgroundImage: "{gradients.glow}"
  swatch-hero:
    backgroundImage: "{gradients.hero}"
    rounded: "{rounded.md}"
  badge:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.full}"
    padding: "{spacing.sm}"
---

# Aurora Hero

## Overview

Aurora Hero is a design system for a single loud thing: a **gradient hero
banner**. The personality is **luminous, nocturnal, and energetic** — a deep
navy page on which a violet→pink→amber gradient glows like an aurora, lifted by a
soft blue radial bloom in the upper-left. It is the visual opposite of the warm,
papery Shelf & Spine system: where that one is ink on limestone, this one is
light on dark.

The system's signature value is the **gradient itself**. Two sites consuming this
DESIGN.md must render the identical wash — same angle, same stops, same
positions — or the brand drifts. That is exactly what tokenizing the gradient
(rather than copy-pasting a `linear-gradient(...)` string) prevents.

## Colors

The palette is a dark surface plus three saturated gradient anchors and one cool
accent for the glow.

- **Primary (Violet #5b21b6):** The gradient's origin and the brand's core hue.
- **Tertiary (Pink #db2777):** The gradient's midpoint — the heat of the wash.
- **Accent (Amber #f59e0b):** The gradient's far end; the warm horizon.
- **Secondary (Blue #2563eb):** Used only for the radial glow overlay, at low
  alpha, never as a solid fill.
- **Surface (Navy #0b1020):** The page behind the banner; lets the gradient read
  as emitted light.
- **On-Primary (#f5f3ff):** Near-white text that sits on the saturated gradient.

## Typography

- **Display:** Sora Bold at 56px for the hero headline — geometric, modern,
  confident against the wash.
- **Body:** Inter at 18px for the supporting line.
- **Labels:** Inter uppercase with wide tracking for the eyebrow badge.

## Layout

A single centered banner block with generous internal padding
(`spacing.xl` = 64px) so the gradient has room to breathe behind the text. The
radial glow is a same-size overlay layer, not a separate box.

## Elevation & Depth

Depth here is **luminous, not shadow-borne**. The radial glow (`gradients.glow`)
is a translucent blue bloom layered over the linear hero gradient to fake a light
source in the upper-left. Order matters: glow on top of the linear wash, text on
top of both.

## Shapes

Soft-rectangular. The banner uses `rounded.lg` (20px); swatch chips use
`rounded.md` (12px); the eyebrow badge is a full pill (`rounded.full`).

## Components

### Hero Banner

`hero-banner` carries the linear `{gradients.hero}` as its `backgroundImage`, with
`on-primary` text over it. Because the background is a gradient — not a single
color — its text contrast cannot be checked against one background value; the
linter emits an advisory note rather than a pass/fail. Author's responsibility:
keep text over the **darker** (violet) end of the wash, which is where the
headline sits.

### Hero Glow

`hero-glow` is the radial `{gradients.glow}` overlay. It has no text of its own;
it only tints the banner.

### Swatch

`swatch-hero` is a small chip that paints the same `{gradients.hero}` at a smaller
size — proof the one token drives both the banner and the chip identically.

## Do's and Don'ts

- **Do** reference `{gradients.hero}` everywhere the wash appears — never paste a
  literal `linear-gradient(...)` string, or the angle and stops will drift.
- **Do** keep saturated gradient text on the darker violet end for legibility.
- **Do** layer the radial glow *over* the linear wash, never the reverse.
- **Don't** animate the gradient here — a moving gradient is a `motion` token
  applied to the element, kept separate from the gradient's look.
- **Don't** add more than three stops to the hero wash; the three-anchor
  violet→pink→amber identity is the brand.
