# designmd-lint

A self-contained DESIGN.md validator (stdlib + PyYAML, no build step).

## Why it exists

The upstream reference linter (`workspace/scratch/.../reference/rules/*.ts`) is
TypeScript that imports modules we never cherry-picked (`model/spec.js`,
`spec-config.js`, `parser/spec.js`), so it **cannot run as-is**. This script
re-implements the *logic* of those rules in dependency-light Python so DESIGN.md
validation is reproducible — and it implements the proposed `motion` token
extension (`docs/design-md-motion-extension-proposal.md`) on top.

## Usage

```bash
python3 tools/designmd-lint/validate.py demo/book-flip/DESIGN.md [more.md ...]
```

Exit code `1` if any **error** finding, else `0`. Warnings and info never fail.

## Rules

| Rule | Severity | Mirrors upstream? |
|---|---|---|
| `section-order` | warning | yes (`section-order.ts`) |
| `missing-sections` | info | yes |
| `missing-primary` | error | yes |
| `missing-typography` | warning | yes |
| `broken-ref` | error | yes (+ extended sub-token list) |
| `contrast-ratio` | warning | yes |
| `unknown-key` | warning | yes (+ `motion` is a known key) |
| `motion-format` | error | **new** — motion extension |
| `motion-orphaned` | info | **new** — motion extension |

## Motion extension support

Implements `docs/design-md-motion-extension-proposal.md`:

- `motion` is a recognized top-level token group; `{motion.x}` references resolve.
- `perspective` and `transition` are accepted component sub-tokens.
- `motion-format` validates `duration`/`delay` (`ms`/`s`) and `easing`
  (keyword or `cubic-bezier()`).

## Fidelity check

Run it against the upstream examples to confirm it enforces real rules:

```bash
REF=workspace/scratch/2026-06-21-01-idea-design.md-reverse-engineering/reference/examples
python3 tools/designmd-lint/validate.py "$REF"/*/DESIGN.md
```

`paws-and-paths` and `totality-festival` validate clean; `atmospheric-glass`
surfaces 4 contrast warnings on translucent glass surfaces (white text on
`rgba(255,255,255,0.1)`), matching the upstream contrast rule's behavior of
ignoring alpha + backdrop.

## Known limitation

The contrast rule (here and upstream) resolves a translucent `rgba(...)`
background to its opaque RGB and ignores the backdrop behind it. Glassmorphism
components will therefore always warn. Treat contrast findings on intentionally
translucent surfaces as advisory.
