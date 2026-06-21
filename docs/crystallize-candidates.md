# Crystallize Candidates

Running log of reusable patterns/learnings from this project that may be worth
formalizing later as a **rule**, **skill**, **workflow**, or **memory**. Not yet
crystallized — captured here so they aren't lost. Review periodically and graduate
the strong ones.

> Convention: `Cn` id, a one-line hook, what it is, why it's reusable, and a
> proposed home (rule / skill / workflow / reference).

---

## C1 — "Live effect → DESIGN.md" reverse-engineering workflow
**Hook:** Recover a web effect as portable design tokens, not copied CSS.
**What:** A repeatable pipeline proven on the book-cover flip:
`inspect live site → extract REAL css/js (curl + grep/python) → write spec →
author DESIGN.md tokens → lint → export to Tailwind/DTCG → recreate from exports`.
The component-level version mirrors the whole-site project goal.
**Why reusable:** Any "I saw this effect on site X, make it ours, consistently"
request follows the same steps. Turns one-off copying into a validated, portable
system.
**Proposed home:** workflow (or skill `reverse-engineer-web-effect`).

## C2 — DTCG-aligned format extensions
**Hook:** When a token format lacks a type, extend it by mirroring DTCG types.
**What:** The DESIGN.md `motion` extension (`docs/design-md-motion-extension-proposal.md`)
aligns to DTCG `duration`/`cubicBezier`/`transition` rather than inventing shapes,
so it stays lintable and exportable.
**Why reusable:** The same move applies to any future gap (e.g. `gradient`,
`shadow`, `border` token groups). "Align extensions to the upstream standard's
types" is a durable principle.
**Proposed home:** rule/reference note ("extend formats toward their cited standard").

## C3 — Use the un-extended linter as evidence of a gap
**Hook:** A failing lint on exactly the new construct *proves* the extension is needed.
**What:** Hand-running the reference rules surfaced one `broken-ref` error
(`{motion.flip}`) and sub-token warnings — everything else passed. That single
failure is positive evidence: the file is correct except for the precise thing
the proposal adds.
**Why reusable:** A clean way to justify a format/spec change — show the current
tooling failing only on the new construct.
**Proposed home:** reference/method note.

## C4 — Re-implement an un-runnable cherry-picked linter, then cross-check
**Hook:** Cherry-picked rule files often can't run (missing imports) — reimplement + verify.
**What:** The reference `rules/*.ts` import `model/spec.js` etc. that weren't
extracted. Rather than reconstruct the whole package, we re-implemented the rule
*logic* in dep-light Python (`tools/designmd-lint/`) and **cross-checked against
the upstream example files** (2/3 clean, 1 with expected warnings) to prove the
re-impl is faithful, not a rubber stamp.
**Why reusable:** General tactic whenever you depend on a slice of someone else's
tooling: reimplement minimally, then validate against their own fixtures.
**Proposed home:** rule ("when porting partial tooling, validate against the
source's fixtures").

## C5 — Contrast rule false-positives on translucent/glass surfaces
**Hook:** WCAG contrast checks ignore alpha + backdrop → glassmorphism always warns.
**What:** Both the upstream `contrast-ratio` rule and our re-impl resolve
`rgba(255,255,255,0.1)` to opaque white and ignore what's behind it, so glass
components report ~1:1. Not a bug to "fix" by muting — a real limitation to
document; contrast on intentionally translucent surfaces is advisory.
**Why reusable:** Anyone reverse-engineering modern (glass/blur) UIs into DESIGN.md
will hit this. Worth a standing caveat.
**Proposed home:** reference note (and a candidate spec improvement: contrast
against a declared backdrop token).

## C6 — Extracting real source from Astro/static sites
**Hook:** Get ground-truth CSS/JS, not a WebFetch markdown summary.
**What:** `curl` the page, then pull `/_astro/*.<hash>.css` bundles and inline
`<script type="module">` blocks; de-minify the small ones. WebFetch flattens to
markdown and loses the CSS/JS you actually need to reverse-engineer.
**Why reusable:** Standard first move for any "reverse-engineer this site" task.
**Proposed home:** skill step / workflow note.

---

### Status
Pipeline proven end-to-end (book-cover flip), so several candidates have graduated:

- **C1** → crystallized as the `designmd-reverse-engineer` skill (Carlo's global
  skills home; packaged in `.manual-distributed/`).
- **C2 + C3** → folded into that skill's "Extending to a new effect family"
  protocol (mirror DTCG, scope narrowly, prove the gap with a failing lint).
- **C6** → captured as step 1 of the skill workflow ("extract ground truth").

Still open as reference notes / future work:

- **C4** (re-implement partial tooling, validate against the source's fixtures) —
  applied here; worth a standing rule.
- **C5** (contrast false-positive on translucent/glass surfaces) — documented in
  the skill + linter README; candidate spec improvement is contrast against a
  declared backdrop token.
- **C2 (next gaps)** — gradient / shadow / glass / scroll-driven token groups are
  the obvious next extensions to exercise the protocol.
