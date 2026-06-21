# cover-typography

A deterministic Pillow compositor that bakes genre-appropriate titling onto a
textless book cover and **validates** the result against a Kindle-ratio +
thumbnail-legibility QA contract. Built for the BookHub demo
(`demo/books/`); the design system it serves is `demo/books/DESIGN.md`.

## Why a tool, not hand-placed text

Hand-placing type is unrepeatable and unverifiable. This tool is:

- **Deterministic** — same spec + same fonts → byte-stable output (fixed Lanczos
  resampling, fixed encoder quality, no timestamps). Re-runnable in CI.
- **Self-validating** — "readable at thumbnail" and "Kindle ratio" become
  automated PASS/FAIL gates in `report.json`, not eyeballing.

## Usage

```bash
# one cover
python3 compose.py ../../demo/books/covers/the-last-word/cover-spec.yaml
# every covers/<slug>/cover-spec.yaml under demo/books
python3 compose.py --all
# fail the process if any QA gate fails (CI)
python3 compose.py --all --strict
```

Needs Pillow + PyYAML (the repo `.venv` has them: `.venv/bin/python compose.py …`).

## Inputs

- **Source cover** PNG (the textless art; ~992×1586 here).
- **`cover-spec.yaml`** per book — the *values* (the design boundary's first layer):
  `title` / `title_lines`, `author`, `title_font` / `author_font` (+ `title_axes` /
  `author_axes` to pin variable-font weight/opsz), colors, `safe_zone` (normalized
  box), `scrim` (color + opacity + `hold`/`extent`, or `null`), `stroke`, `shadow`,
  `max_lines`, optional `min_thumb_cap_px`. The byline is anchored at the foot via
  `author_zone` (a normalized box) over its own `author_scrim` (a bottom gradient band
  — dark over dark art, cream footer over a light collage), with an optional
  `author_rule` hairline divider. Omit `author_zone` to tuck the byline under the
  title (back-compat). See the three specs for worked examples.
- **`fonts/`** + **`fonts.json`** — OFL font binaries (git-ignored) and the tracked
  manifest (family + file + axis ranges + Google Fonts URL + license).

## Pipeline (`compose.py`)

1. Normalize the source to **Kindle 1.6:1** and upscale to **1600×2560** (Lanczos).
2. Resolve the font — **for variable fonts, pin the weight/opsz axis explicitly**
   (`set_variation_by_axes`). League Spartan and Montserrat default to `wght=100`
   (hairline); a "bold" pick silently renders thin if you don't. **Auto-fit** the
   title into the safe-zone box (binary search the largest size that fits width +
   stacked height within margins).
3. Apply the legibility treatment: a **scrim** (linear gradient with an optional
   `hold` plateau so a bright zone stays darkened across the whole title band) and
   a text **stroke** + soft **glow**, sized off the fitted cap height.
4. Composite title + author in the safe zone.
5. Export **PNG, JPG (q82), WEBP (q80)**; record each file size.
6. **QA** — downscale to a 160px-wide thumbnail; measure the rendered title
   cap-height and the **worst-case** text-zone contrast (brightest 95th-pct pixel
   for light text, darkest 5th-pct for dark text — the glass module's "worst-case
   stop" discipline). Emit `qa-contact-sheet.png` (full + thumbnail) and
   `report.json`.

## QA gates (`report.json`)

| gate | threshold |
|---|---|
| `ratio_ok` | 1.600 ± 0.5% |
| `thumb_cap_ok` | title cap-height ≥ 14px at a 160px thumbnail (a spec may lower `min_thumb_cap_px` with a recorded rationale — e.g. a long literary Didone whose contrast far exceeds the floor) |
| `contrast_ok` / `author_contrast_ok` | ≥ 4.5:1 (WCAG AA), worst-case stop after scrim |
| `lines_ok` | ≤ `max_lines` (default 2) |

`--strict` exits non-zero if any cover fails.

## Outputs

- `demo/books/covers/<slug>/dist/<slug>.{png,jpg,webp}` — titled covers. The **PNG
  master is git-ignored** (2.7–5.3MB, regenerable here); the web-optimized jpg/webp
  are tracked. The site uses copies in `demo/books/site/assets/`.
- `qa-contact-sheet.png` + `report.json` — tracked evidence.

## Fonts & licensing

All faces are **OFL** Google Fonts (baking onto a commercial cover is permitted).
Binaries live in `fonts/` (git-ignored); `fonts.json` is the reproducible record.
For a genuine genre gap no library face serves, `fetch_fonts.py` pulls one OFL face
and prints its manifest entry — **unused in this build** (The Signal's techno gap
resolved to in-library League Spartan).

## Relationship to the designmd skill

This tool is **new and lives only in this repo** — it is *not* a mirror of the
`designmd-reverse-engineer` skill's `scripts/` (unlike `tools/designmd-lint` and
`tools/designmd-export`). If it proves out, propose it as a skill module later;
do not silently fork the skill.
