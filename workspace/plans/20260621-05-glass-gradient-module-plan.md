# Module Implementation Plan — `glass.md` & `gradient.md`

**Date:** 2026-06-21
**For:** the `designmd-reverse-engineer` skill (`~/.myagents/skills/designmd-reverse-engineer/`)
**Why:** First real exercise of the skill's "Extending to a new effect family"
protocol. Gradient and glass are the next two gaps the token format can't yet
express (after `motion`). Each becomes a self-contained module: a
`references/<family>.md` digest + matching rules in `scripts/validate.py` and
`scripts/export.py`, proven by a demo recreated from exports.

Repo for tooling/demos: `~/Github/Study20260621/`. Skill is external; re-zip to
`.manual-distributed/` after changes.

---

## Guiding protocol (from SKILL.md — apply to each module)

1. Triage by the values / structure / behavior boundary.
2. Mirror the upstream standard (DTCG), don't invent.
3. Scope narrowly; write down what stays out.
4. Prove the gap with a failing lint *before* teaching the linter.
5. Degrade gracefully (optional top-level key; unknown props "accept with warning").
6. Capture behavioral contracts, not just values.
7. Add a module; don't rewrite the core workflow.

## Shared module anatomy (every effect-family module delivers)

- `references/<family>.md` — the schema digest + worked example + open questions.
- `scripts/validate.py` — format/ref/semantic rules for the new token group.
- `scripts/export.py` — CSS-vars + Tailwind + DTCG mappings for the new tokens.
- A demo under `~/Github/Study20260621/demo/<family>/` — DESIGN.md → exports →
  recreation consuming only the exports.
- SKILL.md "Bundled resources" updated to list the new reference file.
- A short proposal note (problem → schema → lint → export → compat → open Qs),
  using `references/motion-extension.md` as the template.

---

## Module A — `gradient` (do this FIRST)

Rationale for going first: cleanest DTCG fit, no structural layer, minimal
sub-gaps. It re-proves the protocol on something low-risk before glass forces the
hard questions.

### 1. Triage
- **Values** → new `gradients` token group (stops + orientation). This is the
  whole module.
- **Structure** → none.
- **Behavior** → none for a static gradient. An *animated* gradient is just a
  `motion` token applied to the element; gradient defines the look, motion the
  movement. Keep them separate.

### 2. DTCG fit (mirror, don't invent)
DTCG defines a `gradient` composite type whose `$value` is an array of color
stops `{ color, position }`. It deliberately does **not** encode linear/radial or
angle. So: put **stops in `$value`** (native DTCG) and **orientation in
`$extensions`** (the DTCG-blessed escape hatch for non-standard data). This is a
clean, honest application of "mirror the standard."

### 3. Proposed schema
```yaml
gradients:
  hero:
    type: linear            # linear | radial | conic
    angle: 135deg           # linear: angle; radial/conic: position keyword(s)
    stops:
      - { color: "{colors.primary}",  position: 0% }
      - { color: "{colors.tertiary}", position: 100% }
components:
  hero-banner:
    backgroundImage: "{gradients.hero}"   # new component sub-token
```
- `color` accepts a `{colors.*}` ref or a literal CSS color.
- `position` is a percentage (0–100%) or 0–1.

### 4. What stays OUT (scope)
- Animation (→ `motion`).
- Mesh / multi-layer / image-blended backgrounds (v2 if ever).
- The element the gradient is applied to (that's a component).

### 5. Lint rules (add to validate.py)
- `gradient-stops` (error): ≥2 stops; each `position` a valid %/0–1.
- `gradient-type` (warning): `type` in {linear, radial, conic}.
- `gradient-broken-ref` (error): each stop `color` ref resolves (extends
  existing broken-ref).
- Add `backgroundImage` to `VALID_COMPONENT_SUB_TOKENS`.
- Contrast note: text over a gradient can't be contrast-checked against a single
  bg — emit advisory info, don't fail (see glass C5 handling for the pattern).

### 6. Export mapping (add to export.py)
- **CSS:** `--gradient-hero: linear-gradient(135deg, var(--color-primary) 0%, var(--color-tertiary) 100%);`
- **Tailwind:** `theme.extend.backgroundImage = { hero: 'linear-gradient(...)' }` → `bg-hero`.
- **DTCG:** `{ "$type": "gradient", "$value": [ {color, position}, ... ], "$extensions": { "designmd": { "type": "linear", "angle": "135deg" } } }`.

### 7. Demo
`demo/gradient/` — a hero banner (and a couple of swatch chips) whose background
is `var(--gradient-*)` only. Prove a `radial` and a `linear` both round-trip.

### Open questions
- Color-interpolation hint / color space (`in oklch`)? Defer.
- Conic angle/position representation — settle when a real conic case appears.

---

## Module B — `glass` (do this SECOND)

Glass is harder and that's the point: it forces the sub-gaps the protocol is meant
to surface honestly. Glassmorphism = translucent background + `backdrop-filter:
blur` + hairline border + soft shadow.

### 1. Triage
- **Values** → a **`blur`** group (new; no DTCG equivalent) + a **`shadow`** group
  (new, but native DTCG type) + translucent surface/border colors (existing
  `colors`, used with alpha).
- **Structure** → none beyond normal layout.
- **Behavior / contract** → glass sits over a backdrop; its legibility depends on
  what's behind it. This is the C5 issue and must be encoded as a validation
  contract, not faked.

### 2. DTCG fit
- **shadow** → native DTCG `shadow` composite (`{color, offsetX, offsetY, blur,
  spread}`). Mirror directly.
- **blur / backdrop-filter** → **no DTCG type exists.** This is a genuine
  invention point: add a minimal `blur` group (dimension values) and document the
  absence + put any extra metadata in `$extensions`. Honest "what we had to
  invent."

### 3. Proposed schema
```yaml
blur:
  glass: 20px
  glass-strong: 40px
shadow:
  glass: { offsetX: 0, offsetY: 8px, blur: 32px, spread: 0, color: "rgba(0,0,0,0.10)" }
components:
  glass-card:
    backgroundColor: "rgba(255,255,255,0.10)"
    backdropBlur: "{blur.glass}"        # new component sub-token
    borderColor:  "rgba(255,255,255,0.20)"   # new component sub-token
    shadow:       "{shadow.glass}"      # new component sub-token
```

### 4. What stays OUT (scope)
- The backdrop itself (a `gradients` token or page background — composes with
  Module A).
- Noise/grain texture; the "shine" top/left-only inner border (v2).
- Animation (→ motion).

### 5. Lint rules (add to validate.py) — including the C5 fix
- `blur-format` (error): `blur.*` valid dimensions.
- `shadow-format` (error): offsets/blur/spread valid dimensions; `color` valid.
- `shadow-broken-ref` / `blur-broken-ref` (error): refs resolve.
- Add `backdropBlur`, `borderColor`, `shadow` to `VALID_COMPONENT_SUB_TOKENS`.
- **Fix C5:** in `contrast-ratio`, when a component declares `backdropBlur` OR a
  translucent `backgroundColor` (alpha < 1), do **not** emit a failing warning —
  downgrade to `info`: "contrast not evaluable on a translucent/blurred surface;
  verify against the declared backdrop." Optionally support an explicit
  `backdrop: "{gradients.hero}"` component prop and check contrast against the
  gradient's darkest stop. This turns C5 from a known false-positive into a
  designed behavior.

### 6. Export mapping (add to export.py)
- **CSS:**
  `--glass-card-bg: rgba(255,255,255,0.10);`
  `--glass-card-backdrop: blur(20px);` (also emit `-webkit-backdrop-filter`)
  `--glass-card-border: rgba(255,255,255,0.20);`
  `--glass-card-shadow: 0 8px 32px 0 rgba(0,0,0,0.10);`
- **Tailwind:** `backdropBlur: { glass: '20px' }`, `boxShadow: { glass: '...' }`.
- **DTCG:** shadow → native `shadow` type; blur → custom group with `$extensions`
  note that no standard type exists.

### 7. Demo
`demo/glass/` — a glass card over a gradient backdrop (reuse Module A) to show the
two modules composing. Prove the card renders from exports only and that the
linter no longer false-positives on its contrast.

### Open questions
- Should `blur` be proposed upstream to DTCG, or stay a documented local extension?
- Multi-shadow arrays (DTCG allows shadow arrays) — support now or later?
- Contrast-vs-backdrop: darkest-stop heuristic vs. a declared backdrop token.

---

## Sequencing & dependencies

```
gradient  (independent, clean DTCG fit) ──► glass (composes gradient as backdrop;
                                                    needs new blur + shadow groups;
                                                    fixes C5 contrast handling)
```

- Build, prove, and commit **gradient** fully before starting glass.
- Glass bundles a **minimal `shadow` group**. If shadow grows (elevation system),
  graduate it to its own `references/shadow.md` module later — note it, don't
  pre-build it.

## Acceptance criteria (per module)

1. A DESIGN.md using the new tokens **fails** the current linter on exactly the
   new construct (the gap proof), then **passes** once rules are added.
2. `export.py` produces correct CSS-vars, Tailwind, and DTCG for the new tokens.
3. A demo recreates the effect consuming **only** the exports.
4. `references/<family>.md` written; SKILL.md Bundled resources updated.
5. Skill re-zipped to `.manual-distributed/` (clean, no system files).
6. Cross-check: the upstream `atmospheric-glass` example (glass) lints sensibly
   under the new contrast handling.

## Risks

- **DTCG gaps** (gradient orientation, blur) → use `$extensions`, document
  clearly; don't silently diverge.
- **Scope creep** in glass (shadows, shine, texture) → hold the line via §4.
- **Contrast change** could mask real failures → only downgrade for translucent/
  blurred components, never globally.

---

## Pursue goal prompt (start the next session with this)

> Continue developing the `designmd-reverse-engineer` skill by implementing the
> **`gradient`** effect-family module first, then **`glass`**, following the
> "Extending to a new effect family" protocol in the skill's SKILL.md and the plan
> at `~/Github/Study20260621/workspace/plans/20260621-05-glass-gradient-module-plan.md`.
>
> Skill: `~/.myagents/skills/designmd-reverse-engineer/`. Repo (tooling + demos):
> `~/Github/Study20260621/`.
>
> For **gradient**: author `references/gradient.md`; add a `gradients` token group
> (stops in DTCG `$value`, orientation in `$extensions`) with lint rules to
> `scripts/validate.py` and export mappings (CSS-vars, Tailwind `backgroundImage`,
> DTCG `gradient`) to `scripts/export.py`; prove the gap by linting a new DESIGN.md
> that fails only on the gradient construct, then passes after the rules land;
> build `demo/gradient/` (a hero banner recreated from exports only); update
> SKILL.md Bundled resources; re-zip the skill to `.manual-distributed/`. Mirror
> DTCG, scope narrowly (no animation, no mesh), keep the file degradable.
>
> Then do **glass** the same way: it needs a new `blur` group (no DTCG type —
> document the invention) and a minimal `shadow` group (native DTCG type); add
> `backdropBlur`/`borderColor`/`shadow` component sub-tokens; and **fix the C5
> contrast false-positive** by downgrading contrast checks on translucent/blurred
> components to advisory (verify against a declared/derived backdrop). Build
> `demo/glass/` composing the gradient module as the backdrop.
>
> Commit in sensible groups and push (the repo's pre-push gate at `.githooks`
> blocks home paths/secrets — keep paths relative). Acceptance criteria and the
> full schema/lint/export sketches are in the plan file above.
