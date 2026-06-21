# DESIGN.md format — authoring reference

Concise summary of the DESIGN.md format for authoring. The normative spec is the
Google Labs / Stitch "DESIGN.md Format" (Apache-2.0); this is a working digest,
not a replacement. When a detail isn't here, prefer the upstream spec.

## Shape

A DESIGN.md is **YAML frontmatter (machine-readable tokens)** + **markdown body
(human-readable rationale)**. Tokens are normative; prose gives application
context. Prose may use descriptive color names ("Espresso") that map to
systematic token names (`primary`).

```
---
<yaml token frontmatter>
---
<markdown sections>
```

## Token groups (frontmatter)

```yaml
version: alpha          # optional
name: <string>          # required
description: <string>   # optional
colors:                 # map<string, Color>  — at least `primary` required
  primary: "#1A1C1E"
typography:             # map<string, Typography>
  body-md: { fontFamily: Inter, fontSize: 16px, fontWeight: 400, lineHeight: 1.5 }
rounded:                # map<string, Dimension>   (corner radii)
  md: 8px
spacing:                # map<string, Dimension|number|string>
  md: 16px
components:             # map<string, map<string,string>>
  button-primary:
    backgroundColor: "{colors.primary}"   # {ref} resolves to another token
    rounded: "{rounded.md}"
```

- **Color**: any valid CSS color (hex recommended). Converted to sRGB for contrast.
- **Typography fields**: fontFamily, fontSize (Dimension), fontWeight (number),
  lineHeight (Dimension|number), letterSpacing, fontFeature, fontVariation.
- **Dimension**: number + unit (`px`/`em`/`rem`).
- **Token references**: `{group.token}` — must resolve to a primitive, except in
  `components` where references to composites (e.g. `{typography.body-md}`) are OK.
- **Valid component sub-tokens**: backgroundColor, textColor, typography, rounded,
  padding, size, height, width. (This skill's motion extension adds
  `perspective` and `transition` — see references/motion-extension.md.)
- **Component variants** use related keys: `button-primary`, `button-primary-hover`.

## Sections (markdown body) — fixed order

Use `##` headings, in this order (omit any that don't apply, never reorder):

1. **Overview** (alias: "Brand & Style") — personality, audience, emotional target.
2. **Colors** — palette roles + rationale.
3. **Typography** — families, hierarchy, treatment.
4. **Layout** (alias: "Layout & Spacing") — grid/spacing strategy.
5. **Elevation & Depth** (alias: "Elevation") — how hierarchy is conveyed.
6. **Shapes** — corner/shape language.
7. **Components** — per-component style guidance.
8. **Do's and Don'ts** — guardrails.

An optional `#` H1 title is allowed and not parsed as a section.

## Common token names (non-normative)

- Colors: primary, secondary, tertiary, neutral, surface, on-surface, error
- Typography: headline-lg/md, body-lg/md/sm, label-lg/md/sm
- Rounded: none, sm, md, lg, xl, full

## Consumer behavior for unknown content

| Scenario | Behavior |
|---|---|
| Unknown section heading | Preserve, don't error |
| Unknown color/typography token name | Accept if value valid |
| Unknown spacing value (e.g. "2 / 3") | Accept; store as string |
| Unknown component property | Accept **with warning** |
| Duplicate section heading | **Error** — reject the file |

This "accept with warning" rule is what lets the motion extension's
`perspective`/`transition` props work even before the format formally adopts them.

## Exports

The same tokens convert cleanly to Tailwind theme config, DTCG `tokens.json`, and
CSS custom properties. `scripts/export.py` does all three. Keeping one normative
DESIGN.md and exporting is what guarantees identical results across sites.
