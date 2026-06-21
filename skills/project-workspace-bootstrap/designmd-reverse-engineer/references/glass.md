# Proposal: `blur` + `shadow` Token Groups for DESIGN.md (glassmorphism)

**Status:** Draft proposal (extension to the `alpha` DESIGN.md format)
**Date:** 2026-06-21
**Author:** Study20260621 reverse-engineering project
**Motivating case:** Frosted-glass cards floating over the Aurora gradient
(Aurora Glass) — translucent fill + backdrop blur + hairline border + soft
shadow, none of which the current schema can type, plus a long-standing
false-positive contrast warning on every glass surface (the "C5" issue).

---

## 1. Problem

Glassmorphism is four ingredients: a **translucent fill**, a **backdrop blur**, a
**hairline border**, and a **soft drop shadow**. The format can express the fill
and border as `colors` (used with alpha) but has **no type for blur or shadow**.
So a glass system either buries those values in prose or smuggles them into
unvalidated component props.

There is also a correctness bug. The linter's `contrast-ratio` rule resolves a
translucent `rgba(255,255,255,0.10)` fill to opaque white and ignores the
backdrop, so **every** glass surface with light text reports a failing
~1.1:1 contrast — a false positive (the card is perfectly legible over its dark
backdrop). This is the "C5" issue, and it has trained users to ignore contrast
findings, which is worse than not having them.

Concretely (`demo/glass/`): the un-extended linter (a) **passes** a gradient with
a unit-less blur, a non-dimension shadow offset, and a broken shadow color
reference — zero errors — and (b) **fails** the valid glass card with two
false-positive contrast warnings. This proposal closes both.

## 2. Design principles (inherited from the existing spec)

1. **Reuse DTCG where it exists; be honest where it doesn't.**
   - **shadow** → DTCG has a native composite `shadow` `{color, offsetX, offsetY,
     blur, spread}`. Mirror it exactly.
   - **blur / backdrop-filter** → **DTCG has no type.** This is a genuine
     invention point. We add a minimal `blur` dimension group and *document the
     absence* (a `$description` on the group + `$extensions.designmd.role` on each
     token) so a standard consumer is told this is a non-standard local extension,
     never silently misled.
2. **Typed groups + references.** `blur` and `shadow` are new top-level groups;
   components reference them with `{blur.*}` / `{shadow.*}`.
3. **Translucent surfaces use existing `colors`** (with alpha) — no new "alpha
   color" type needed.
4. **Graceful degradation.** New groups are optional top-level keys; the new
   component props fall under "unknown property → accept with warning."

## 3. Proposed schema

```yaml
blur:                          # map<string, Dimension> — INVENTION (no DTCG type)
  glass: 20px
  glass-strong: 40px
shadow:                        # map<string, Shadow> — native DTCG composite
  glass:
    offsetX: 0
    offsetY: 8px
    blur: 32px
    spread: 0
    color: "{colors.glass-shadow}"   # ref or literal CSS color
components:
  glass-card:
    backgroundColor: "{colors.glass-fill}"   # translucent (alpha < 1)
    backdropBlur: "{blur.glass}"             # new prop
    borderColor:  "{colors.glass-border}"    # new prop
    shadow:       "{shadow.glass}"           # new prop
    textColor:    "{colors.on-surface}"
    backdrop:     "{gradients.hero}"         # new prop — the contrast CONTRACT (§5)
```

- **`backdropBlur`** references a `blur` token; a consumer applies it to BOTH
  `backdrop-filter` and `-webkit-backdrop-filter` (Safari).
- **`borderColor`** is the hairline (typically a low-alpha white).
- **`shadow`** references a `shadow` token (or an inline shadow map).
- **`backdrop`** is **not rendered** — it names the gradient/surface the glass
  floats over so the linter can check contrast against the *backdrop*, not the
  fill (the C5 fix).

## 4. What stays OUT (scoping)

- **The backdrop itself.** It's a `gradients` token or page background — composed
  at the component level (Aurora Glass uses `{gradients.hero}`), not part of glass.
- **Noise / grain texture** and the **one-sided "shine" inner border** (top/left
  light-source highlight) — v2.
- **Animation.** Animating the blur is a `motion` token on the element.
- **Multi-shadow arrays.** DTCG allows shadow arrays; deferred until a real
  elevation system needs more than one shadow per token.

## 5. The C5 contrast fix (a designed behavior, not a silenced warning)

`contrast-ratio` is split by surface type:

- **Opaque surface** → unchanged: WCAG AA `>= 4.5:1` or a **warning**.
- **Glass surface** (component declares `backdropBlur`, OR its resolved
  `backgroundColor` has alpha `< 1`) → the fill-based ratio is meaningless, so:
  - If the component declares a `backdrop` token → check `textColor` against the
    backdrop's **worst-case (lowest-contrast) stop** and emit an **info** advisory
    with that ratio (e.g. *"textColor vs the backdrop's worst-case stop is 1.89:1
    (drops below WCAG AA); advisory — blur and translucency shift effective
    contrast."*). The worst-case stop is used deliberately: a gradient backdrop has
    no single color, and checking the *darkest* stop would report the most
    favorable case for light text and under-warn — the opposite of what a safety
    advisory should do.
  - Otherwise → an **info** advisory: *"contrast is not evaluable against the fill
    alone — declare a `backdrop` token or verify against the actual backdrop."*

Never a failing warning for glass, never globally silenced — only downgraded for
genuinely translucent/blurred components. This turns C5 from a false positive into
a contract: glass legibility is verified against what it actually floats over.

## 6. Linting

| Rule | Severity | Behavior |
|---|---|---|
| `blur-format` | error | each `blur.*` is a valid dimension (e.g. `20px`) |
| `shadow-format` | error | `offsetX/offsetY/blur/spread` valid dims; `color` present |
| `shadow-broken-ref` | error | a shadow `color` `{ref}` resolves |
| `contrast-ratio` (glass branch) | info | the C5 advisory above |

Plus `backdropBlur`, `borderColor`, `shadow`, `backdrop` added to the valid
component sub-tokens. Component-level `{blur.*}` / `{shadow.*}` refs are already
covered by the generic `broken-ref` rule.

## 7. Export mapping

**Raw CSS** (`tokens.css`):
```css
:root {
  --blur-glass: 20px;
  --shadow-glass: 0 8px 32px 0 var(--color-glass-shadow);
  --glass-card-bg: var(--color-glass-fill);
  --glass-card-backdrop: blur(var(--blur-glass));   /* -> backdrop-filter + -webkit- */
  --glass-card-border: var(--color-glass-border);
  --glass-card-shadow: var(--shadow-glass);
}
```

**Tailwind** (`tailwind.config.js`):
```js
theme: { extend: {
  backdropBlur: { glass: '20px', 'glass-strong': '40px' },  // class: backdrop-blur-glass
  boxShadow:    { glass: '0 8px 32px 0 var(--color-glass-shadow)' },  // class: shadow-glass
} }
```

**DTCG `tokens.json`** — shadow native, blur documented-invention:
```json
{
  "shadow": { "glass": { "$type": "shadow", "$value": {
    "color": "{colors.glass-shadow}", "offsetX": "0px", "offsetY": "8px",
    "blur": "32px", "spread": "0px" } } },
  "blur": {
    "$description": "Non-standard local extension: DTCG defines no backdrop-filter/blur type...",
    "glass": { "$type": "dimension", "$value": "20px",
               "$extensions": { "designmd": { "role": "backdrop-blur" } } }
  }
}
```

## 8. Backward compatibility

- `blur` and `shadow` are new optional top-level keys; `backdropBlur`,
  `borderColor`, `shadow`, `backdrop` are new accepted component props (older
  consumers: "unknown property → accept with warning"). Absent → behavior
  identical to today.
- The contrast change only *downgrades* findings for translucent/blurred
  components; opaque-surface contrast is unchanged, so no real failure is masked.

## 9. Open questions

1. Should `blur` be proposed upstream to DTCG, or stay a documented local
   extension? (Recommend: propose upstream; keep `$extensions` until adopted.)
2. **Multi-shadow arrays** (DTCG allows them) — support now or when an elevation
   system needs it? (Recommend: later; graduate `shadow` to its own
   `references/shadow.md` module then.)
3. Contrast-vs-backdrop: the advisory uses the **worst-case (lowest-contrast)
   stop** — conservative, because the linter can't know which region of the
   gradient the glass actually overlaps, so it flags the worst a viewport could
   produce. (An earlier draft checked the *darkest* stop, which is the most
   favorable for light text and under-warned — corrected.) A declared solid
   `backdrop` color, or a per-text-region backdrop, would be more precise — add if
   a case needs it.

---

### Appendix — Aurora Glass expressed under this proposal

See `demo/glass/DESIGN.md`: it composes `{gradients.hero}` (Module A) as the
backdrop and adds the `blur` + `shadow` groups and the four glass component props.
The linter passes it with only the C5 advisory (1.89:1 vs the backdrop's
worst-case amber stop — non-failing, but a real prompt to keep text over the
darker stops); the recreation in `demo/glass/index.html` renders the frosted card
from the exported tokens alone — backdrop blur, hairline, and shadow all resolving
through `var(--…)` chains, and a text-shadow scrim keeping the copy legible across
the wash.
