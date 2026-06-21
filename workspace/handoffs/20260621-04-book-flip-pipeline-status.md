# Handoff — Book-cover flip: full pipeline proof

**Date:** 2026-06-21
**Task:** Reverse-engineer the rgdbrandingawards.com cover-flip effect and drive it
through the DESIGN.md pipeline end-to-end (the project's first full proof), with a
proposed `motion` format extension.

## Done (steps 1–6)

| Step | Artifact |
|---|---|
| 0. Reverse-engineer effect | `workspace/plans/20260621-01-book-cover-flip-spec-and-plan.md` (grounded in real CSS + the de-minified 593-char JS) |
| 1. Motion extension proposal | `docs/design-md-motion-extension-proposal.md` (DTCG-aligned `motion` group) |
| 2. Pilot DESIGN.md | `demo/book-flip/DESIGN.md` (Shelf & Spine system) |
| 3. Reproducible linter | `tools/designmd-lint/validate.py` (+ README); pilot **PASS** (0/0, 1 info) |
| 4. Exporter | `tools/designmd-export/export.py` → `demo/book-flip/dist/{tokens.css, tailwind.config.js, tokens.json}` |
| 5. Demo from exports | `demo/book-flip/index.html` (consumes only `dist/tokens.css`) |
| 6. Evidence | `workspace/evidence/20260621-02-designmd-lint-run.md`, `…-03-book-flip-demo.md` |

## Key results

- **The gap is real and now closed:** the un-extended reference linter errors only
  on `{motion.flip}`; implementing the motion extension turns the pilot green.
- **Transfer proven:** demo renders correctly using only exported tokens; computed
  styles confirm `motion.flip → transform 0.45s`, `{colors.primary} → #3a2d28`,
  perspective/aspect resolved.
- **Validator is faithful:** passes 2/3 upstream examples clean, flags 4 real
  contrast warnings on the glass example (see crystallize C5).

## Not done / decisions pending

- **Committed & pushed** to `origin/main` in grouped commits (tooling /
  research+proposal / demo+exports / evidence+handoff / doc-maintenance). The
  pre-push gate (`.githooks`) is active and passed. `demo/**/dist/` is force-tracked
  via a `.gitignore` negation (the generic `dist/` rule would otherwise drop it).
- **Linter is a re-impl**, not the upstream TS linter (which can't run — missing
  imports). If fidelity to upstream matters long-term, consider wiring the real
  package or porting these rules back.
- **Motion extension is a proposal**, not accepted upstream. Open questions in §9
  of the proposal (keyframes? perspective scale? essential-motion flag?).
- **Crystallize candidates** logged in `docs/crystallize-candidates.md` (C1 & C2
  are the strongest — revisit now that the pipeline is end-to-end proven).

## Suggested next steps

1. Decide what to commit (tools + demo + docs are coherent units).
2. Optionally graduate C1 ("live effect → DESIGN.md" workflow) into a skill.
3. Optionally add the `motion` rules to a real runnable linter.
