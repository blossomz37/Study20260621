---
version: alpha
name: Aurora Hero (gap proof — intentionally broken gradient)
description: >-
  Same system as DESIGN.md but with a deliberately malformed `gradients` group.
  The UN-extended linter passes this file with zero errors (it cannot see inside
  a gradient) — that silent pass IS the gap. The extended linter must catch the
  invalid type, the out-of-range stop position, and the broken color reference.
colors:
  primary: "#5b21b6"
  on-primary: "#f5f3ff"
  surface: "#0b1020"
  on-surface: "#e8eaf2"
typography:
  display-lg:
    fontFamily: Sora
    fontSize: 56px
    fontWeight: 700
    lineHeight: 1.05
gradients:
  hero:
    type: sweep                              # invalid type  -> gradient-type (warning)
    angle: 135deg
    stops:
      - { color: "{colors.nope}", position: 150% }   # broken ref + bad position -> 2 errors
      - { color: "{colors.primary}", position: 100% }
components:
  hero-banner:
    backgroundImage: "{gradients.hero}"
    textColor: "{colors.on-primary}"
---

# Aurora Hero — gap proof

This file exists only to demonstrate that the pre-extension linter cannot
validate the `gradients` construct. See `workspace/evidence/`.
