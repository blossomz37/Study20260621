---
version: alpha
name: Aurora Glass (gap proof — intentionally broken blur/shadow)
description: >-
  Same system as DESIGN.md but with a malformed `blur` value and a malformed
  `shadow` token. The linter without the glass rules cannot validate either — it
  passes them with zero errors. The extended linter must catch the bad blur
  dimension, the bad shadow dimension, and the broken shadow color reference.
colors:
  primary: "#5b21b6"
  on-surface: "#eef0fb"
  surface: "#0b1020"
  glass-fill: "rgba(255,255,255,0.10)"
  glass-border: "rgba(255,255,255,0.22)"
typography:
  title-md:
    fontFamily: Sora
    fontSize: 22px
    fontWeight: 600
    lineHeight: 1.2
rounded:
  lg: 20px
spacing:
  lg: 24px
blur:
  glass: 20                       # missing unit -> blur-format (error)
shadow:
  glass:
    offsetX: 0
    offsetY: nope                 # not a dimension -> shadow-format (error)
    blur: 32px
    spread: 0
    color: "{colors.ghost}"       # broken ref  -> shadow-broken-ref (error)
components:
  glass-card:
    backgroundColor: "{colors.glass-fill}"
    backdropBlur: "{blur.glass}"
    borderColor: "{colors.glass-border}"
    shadow: "{shadow.glass}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
---

# Aurora Glass — gap proof

Exists only to demonstrate that the pre-extension linter cannot validate `blur`
or `shadow`. See `workspace/evidence/`.
