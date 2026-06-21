# Evidence — designmd-lint run (step 3)

**Date:** 2026-06-21
**Tool:** `tools/designmd-lint/validate.py` (self-contained re-impl of reference/rules + motion extension)
**Subject:** `demo/book-flip/DESIGN.md`

## Command

```
python3 tools/designmd-lint/validate.py demo/book-flip/DESIGN.md
```

## Result — pilot (with motion extension implemented)

```
demo/book-flip/DESIGN.md
  · info    motion-orphaned    [motion.none] Motion token is not referenced by any component.
  → PASS: 0 error(s), 0 warning(s), 1 info
```

The single `info` is expected: `motion.none` is a utility token intentionally
defined for "always suppress motion" use, not referenced by a component in this
pilot. Info severity is non-blocking.

**Before the extension** (hand-validated against the un-extended reference rules
in the prior step): `{motion.flip}` raised a `broken-ref` **error** and
`perspective`/`transition` raised sub-token warnings. Implementing the motion
extension in the validator turns those green — the step-3 proof.

## Cross-check — upstream reference examples (validator fidelity)

```
atmospheric-glass/DESIGN.md  → PASS: 0 error, 4 warning, 0 info
  (4× contrast-ratio: white text on rgba(255,255,255,0.1) glass = 1.00:1)
paws-and-paths/DESIGN.md     → clean
totality-festival/DESIGN.md  → clean
```

Two of three upstream examples validate clean; the third surfaces 4 contrast
warnings on translucent "glass" surfaces. This confirms the validator enforces
real rules (not a rubber stamp) and matches the upstream contrast rule's known
behavior of ignoring alpha + backdrop (see crystallize candidate C5).
