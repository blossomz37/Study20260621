# Proposal: A `motion` Token Group for DESIGN.md

**Status:** Draft proposal (extension to the `alpha` DESIGN.md format)
**Date:** 2026-06-21
**Author:** Study20260621 reverse-engineering project
**Motivating case:** A book-cover flip component (reverse-engineered from rgdbrandingawards.com) whose timing, easing, and 3D perspective have no home in the current schema.

---

## 1. Problem

The current DESIGN.md format (`reference/spec.md`) defines five token groups: `colors`, `typography`, `rounded`, `spacing`, and `components`. **There is no token type for motion** — durations, easings, delays, or transitions.

This is fine for static design systems, but it breaks the project's core promise — *one normative source of truth that transfers consistently across sites* — the moment a design system includes animation. Concretely, for the book-flip:

- The flip duration (`0.45s`) and easing (`ease`) currently can only live as prose or as un-typed custom component properties.
- Two sites consuming the "same" system can drift to `0.4s` vs `0.5s` because nothing normative pins the value.
- The linter can't check motion values (no type to validate against), so motion silently escapes the consistency guarantees that `colors`/`typography` enjoy.

The spec's own escape hatch — "unknown component property → accept with warning" — means motion *works*, but as an unvalidated, un-exported afterthought. That's the gap this proposal closes.

## 2. Design principles (inherited from the existing spec)

The spec states it is "inspired by the [Design Token JSON spec]" and adopts "typed token groups" plus the `{path.to.token}` reference syntax. This proposal stays inside those rules:

1. **Reuse DTCG types.** The DTCG 2025 format already standardizes `duration`, `cubicBezier`, and a composite `transition` type. We mirror them so export is a mapping, not a translation.
2. **Typed group + references.** `motion` is a new top-level typed group; components reference its primitives with `{motion.<name>}`, exactly like `{rounded.md}` today.
3. **Primitive references for component fields; composite allowed in `components`.** Same rule the spec already applies to `{typography.label-md}`.
4. **Graceful degradation.** A consumer that doesn't understand `motion` should fall back to the existing "unknown section/key → preserve, don't error" behavior.

## 3. Proposed schema

A new top-level group, `motion`, that is a `map<string, Motion>`:

```yaml
motion:
  <token-name>:
    duration: <Duration>          # required
    easing:   <Easing>            # optional, default "ease"
    delay:    <Duration>          # optional, default 0
```

**Duration** — a string with a time unit: `ms` or `s` (e.g. `450ms`, `0.45s`). Maps to DTCG `duration`.

**Easing** — either a CSS easing keyword (`ease`, `linear`, `ease-in-out`, `step-end`, …) or a `cubic-bezier(x1, y1, x2, y2)` string. Maps to DTCG `cubicBezier` (keywords expand to their canonical bezier on export).

### Optional: a `transition` convenience composite

For ergonomics, a `motion` token may instead be expressed as a composite that names the property it animates — aligning with DTCG's composite `transition` type:

```yaml
motion:
  flip:
    property: transform           # CSS property (or "all")
    duration: 450ms
    easing: ease
    delay: 0ms
```

This is sugar; `property` is optional and defaults to `all`. Tools that only understand the primitive form can ignore `property`.

### Component reference

Components reference motion tokens through a new accepted component property, `transition`:

```yaml
components:
  book-flip-inner:
    transition: "{motion.flip}"   # resolves to transform 450ms ease 0ms
    perspective: 800px            # see §5
```

## 4. Reduced-motion semantics (normative)

Motion tokens carry an implicit contract that mirrors how the source site (and good practice) behaves:

- A consumer **must** treat every `motion` token as gated by `prefers-reduced-motion`. When the user prefers reduced motion, the effective `duration` and `delay` collapse to `0` (the transition still "happens" instantly; layout/state is unchanged).
- This makes reduced-motion a property of the *system*, not of each hand-written component — which is the whole point of tokenizing it.

A design system may additionally define an explicit override token:

```yaml
motion:
  none:
    duration: 0ms
    easing: linear
```

…and reference `{motion.none}` where motion must always be suppressed.

## 5. What stays OUT of `motion` (scoping)

Motion is **time + easing**, deliberately narrow. Two related concerns are explicitly *not* motion tokens:

- **`perspective` / 3D context** (e.g. `800px`, `transform-style: preserve-3d`, `backface-visibility`). These are *spatial* properties of a component, not motion. They belong as **component properties** (proposed addition to the accepted component-property list: `perspective: <Dimension>`). The flip's two-face `preserve-3d` structure remains a *prose* concern in the Components section — it's structure, not a value.
- **Interaction model** (hover-preview vs. click-to-pin, click-guards, Escape-to-close, touch gating). This is *behavior*, not a token, and stays in the Components + Do's/Don'ts prose. No token format should try to encode event wiring.

This boundary keeps `motion` validatable and exportable while honestly admitting that some of an effect is irreducibly prose + code.

## 6. Linting (how consistency gets enforced)

New rules, parallel to the existing `rules/`:

| Rule | Behavior | Parallels |
|---|---|---|
| `motion-duration-format` | `duration`/`delay` must be valid `ms`/`s` time strings | `contrast-ratio` (value validation) |
| `motion-easing-format` | `easing` must be a known keyword or valid `cubic-bezier()` | — |
| `motion-broken-ref` | `{motion.x}` references must resolve | extends existing `broken-ref` |
| `motion-orphaned` | warn on `motion` tokens referenced by nothing | extends existing `orphaned-tokens` |

With these, a `book-flip-inner` that references `{motion.flip}` is validated end-to-end, exactly as a button referencing `{colors.primary}` is today.

## 7. Export mapping

The payoff — `motion` fans out to the same targets the project already exports to:

**Tailwind** (`tailwind.config.js`):
```js
theme: {
  transitionDuration:       { flip: '450ms' },
  transitionTimingFunction: { flip: 'ease' },
  transitionProperty:       { flip: 'transform' },
}
// usage: class="transition-flip duration-flip ease-flip"
```

**DTCG `tokens.json`:**
```json
{
  "motion": {
    "flip": {
      "$type": "transition",
      "$value": {
        "duration":      { "$type": "duration",   "$value": "450ms" },
        "timingFunction":{ "$type": "cubicBezier", "$value": [0.25, 0.1, 0.25, 1] },
        "delay":         { "$type": "duration",   "$value": "0ms" }
      }
    }
  }
}
```

**Raw CSS custom properties:**
```css
:root { --motion-flip: transform 450ms ease 0ms; }
.book-flip-inner { transition: var(--motion-flip); }
```

Because all three derive from the one `motion.flip` token, the flip animates identically on every site that imports the system. That is the consistency guarantee the project exists to demonstrate — now extended to motion.

## 8. Backward compatibility

- `motion` is a new optional top-level key. Existing DESIGN.md files are unaffected.
- A `transition` component property is a new accepted property; older consumers fall under the spec's "unknown component property → accept with warning" rule, so nothing breaks.
- If `motion` is absent, behavior is identical to today.

## 9. Open questions

1. Should `motion` support keyframe/multi-step animations (DTCG has no standard composite for these yet), or stay transition-only? **Recommendation:** transition-only for `alpha`; revisit if a case needs keyframes.
2. Should `perspective` be a `spacing`-style scale or a free component property? **Recommendation:** free component `Dimension` property — it's rarely scaled.
3. Is `prefers-reduced-motion` collapse-to-zero the right universal default, or should some motion be "essential" and exempt? **Recommendation:** default collapse-to-zero; allow an explicit `essential: true` flag on a motion token later if needed.

---

### Appendix — the book-flip expressed under this proposal

```yaml
motion:
  flip:
    property: transform
    duration: 450ms
    easing: ease
components:
  book-flip:
    perspective: 800px
  book-flip-inner:
    transition: "{motion.flip}"
  book-flip-back-info:
    backgroundColor: "{colors.surface-container}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
  book-flip-cta:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.cover}"
```

Everything time/easing-related is now a validated, exportable token. Everything spatial is a typed component property. Everything behavioral stays in prose. The gap is closed without overreaching.
