# Proposal: A `gradients` Token Group for DESIGN.md

**Status:** Draft proposal (extension to the `alpha` DESIGN.md format)
**Date:** 2026-06-21
**Author:** Study20260621 reverse-engineering project
**Motivating case:** A luminous hero banner (Aurora Hero) whose violet→pink→amber
linear wash and radial glow have no home in the current schema.

---

## 1. Problem

The DESIGN.md format defines token groups for `colors`, `typography`, `rounded`,
`spacing`, and `components` (plus this skill's `motion` extension). **There is no
token type for a gradient** — a multi-stop blend with an orientation.

A gradient is a brand signature, not a one-off. Two pages that should share "the
same hero wash" drift the moment each pastes its own `linear-gradient(...)`
string: one ends up `135deg`, the other `140deg`; one stops at `55%`, the other
at `50%`. The format's promise — one normative source that transfers — breaks for
the most visible element on the page.

Worse, the un-extended linter is **blind** to the construct. Given a gradient with
an invalid type, an out-of-range stop position, and a broken color reference, it
reports **zero errors** and only warns that `backgroundImage` is an unrecognized
component property. (See `demo/gradient/DESIGN.broken.md` — the pre-extension
linter passes it; the extended linter fails it with exactly those three findings.)
That silent pass is the gap this proposal closes.

## 2. Design principles (inherited from the existing spec)

1. **Reuse DTCG types.** DTCG standardizes a composite `gradient` type whose
   `$value` is an **array of color stops** `{color, position}`. We mirror it so
   export is a mapping, not a translation.
2. **Honest about what DTCG omits.** DTCG's `gradient` deliberately does **not**
   encode linear vs. radial vs. conic, nor an angle. So orientation goes in
   `$extensions` — the DTCG-blessed escape hatch for non-standard data — never
   smuggled into `$value`.
3. **Typed group + references.** `gradients` is a new top-level group; each stop's
   `color` may be a `{colors.*}` reference, exactly like other tokens.
4. **Graceful degradation.** A consumer that doesn't understand `gradients` falls
   back to the spec's "unknown section/key → preserve, don't error" behavior; a
   component's `backgroundImage` prop is "unknown property → accept with warning."

## 3. Proposed schema

A new top-level group, `gradients`, a `map<string, Gradient>`:

```yaml
gradients:
  hero:
    type: linear            # linear | radial | conic   (default: linear)
    angle: 135deg           # orientation (see below)
    stops:                  # >= 2 stops, in order
      - { color: "{colors.primary}",  position: 0% }
      - { color: "{colors.tertiary}", position: 55% }
      - { color: "{colors.accent}",   position: 100% }
components:
  hero-banner:
    backgroundImage: "{gradients.hero}"   # new component sub-token
```

- **`color`** — a `{colors.*}` reference or a literal CSS color (hex / `rgba()`).
- **`position`** — a percentage (`0%`–`100%`) or a `0`–`1` fraction. Optional per
  stop, but recommended; the exporter scales a bare fraction to a percentage.
- **`angle`** — the orientation, interpreted per `type`:
  - `linear` → a CSS angle (`135deg`); default `180deg`.
  - `radial` → a shape/position phrase (`circle at 28% 18%`); default `circle`.
  - `conic` → a `from <angle> [at <position>]` phrase; default `from 0deg`.

## 4. What stays OUT of `gradients` (scoping)

A gradient is **stops + orientation**, deliberately narrow. Explicitly not part of
this type:

- **Animation.** A moving gradient is a `motion` token applied to the element; the
  gradient defines the *look*, motion the *movement*. Keep them separate.
- **Mesh / multi-layer / image-blended backgrounds.** Layering (e.g. a radial glow
  over a linear wash) is composed at the *component* level by stacking two gradient
  tokens — not by inventing a multi-layer gradient type. (v2 if a real case needs
  it.)
- **The element it paints.** That's a component (`backgroundImage`), not the token.
- **Color-interpolation hints / color space** (`in oklch`). Deferred until a real
  case appears; would live in `$extensions`.

## 5. Linting (how consistency gets enforced)

New rules, parallel to the existing `rules/`:

| Rule | Severity | Behavior |
|---|---|---|
| `gradient-stops` | error | `>= 2` stops; each `position` a valid `%`/`0–1`; each stop has a `color` |
| `gradient-type` | warning | `type` in {linear, radial, conic} |
| `gradient-broken-ref` | error | each stop `color` `{ref}` resolves (extends `broken-ref`) |

Plus a `backgroundImage` entry in the valid component sub-tokens, and a **contrast
advisory**: text over a gradient `backgroundImage` cannot be contrast-checked
against a single color, so the linter emits `info` with the **worst-case
(lowest-contrast) stop** for that text color (e.g. *"worst-case contrast is 1.96:1
(drops below WCAG AA); keep text over the stops where it stays legible"*) rather
than a pass/fail warning. The worst-case stop — not the darkest — is used so the
advisory warns rather than under-reports for light text. This mirrors the
translucent-surface handling used for glass (the C5 pattern).

## 6. Export mapping

`gradients` fans out to the same three targets, all derived from the one token:

**Raw CSS custom properties** (`tokens.css`) — stop refs resolve to color vars:
```css
:root {
  --gradient-hero: linear-gradient(135deg, var(--color-primary) 0%, var(--color-tertiary) 55%, var(--color-accent) 100%);
}
.hero-banner { background-image: var(--gradient-hero); }
```

**Tailwind** (`tailwind.config.js`):
```js
theme: { extend: { backgroundImage: {
  hero: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-tertiary) 55%, var(--color-accent) 100%)',
} } }
// usage: class="bg-hero"
```

**DTCG `tokens.json`** — stops in `$value`, orientation in `$extensions`:
```json
{
  "gradients": {
    "hero": {
      "$type": "gradient",
      "$value": [
        { "color": "{colors.primary}",  "position": "0%" },
        { "color": "{colors.tertiary}", "position": "55%" },
        { "color": "{colors.accent}",   "position": "100%" }
      ],
      "$extensions": { "designmd": { "type": "linear", "angle": "135deg" } }
    }
  }
}
```

Because all three derive from `gradients.hero`, the wash renders identically on
every page that imports the system — the consistency guarantee, now extended to
gradients.

## 7. Backward compatibility

- `gradients` is a new optional top-level key. Existing DESIGN.md files are
  unaffected; if absent, behavior is identical to today.
- `backgroundImage` is a new accepted component property; older consumers fall
  under "unknown component property → accept with warning," so nothing breaks.

## 8. Open questions

1. **Color-interpolation / color space** (`in oklch`, hue interpolation)? Defer to
   `$extensions` when a case needs it.
2. **Conic orientation** representation (`from <angle> at <pos>`) — the current
   single `angle` string covers it, but settle the grammar when a real conic
   appears.
3. **Multi-layer backgrounds** — keep composing at the component level (stack two
   gradient tokens), or eventually introduce a `background` composite? Recommend
   compose-at-component for now.

---

### Appendix — the Aurora Hero expressed under this proposal

```yaml
gradients:
  hero:
    type: linear
    angle: 135deg
    stops:
      - { color: "{colors.primary}",  position: 0% }
      - { color: "{colors.tertiary}", position: 55% }
      - { color: "{colors.accent}",   position: 100% }
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
```

Stops + orientation are a validated, exportable token; the radial glow layers over
the linear wash at the component level; legibility over the wash stays an authored
contract (advisory note). The gap is closed without overreaching.
