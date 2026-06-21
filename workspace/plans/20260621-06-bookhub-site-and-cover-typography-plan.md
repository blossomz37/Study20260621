# Plan — BookHub flip-gallery site + cover-typography tool + representative DESIGN.md

**Date:** 2026-06-21
**Status:** Planning (approved scope; build not started)
**Author of demo books:** A. May Zing
**Owner:** Carlo
**Supersedes nothing; extends:** `demo/book-flip/` (Shelf & Spine proof), `tools/`, the
`designmd-reverse-engineer` skill.

---

## 1. Objective & end-state

Put the three proven pieces (flip card, gradient, glass) together into **one real
static website** that presents three real books as an interactive flip gallery, and
produce a **representative `DESIGN.md`** that lets Carlo replicate this design on any
future page. Alongside it, build a **cover-typography tool** that bakes
genre-appropriate titling onto the three textless covers and validates them against
Kindle ratio + thumbnail legibility.

**Definition of done (acceptance criteria):**

1. Three titled covers exist as `PNG + JPG + WEBP` at Kindle ratio (1600×2560, 1.6:1),
   each with title + "A. May Zing", each passing an automated thumbnail-legibility gate,
   with a file-size report comparing the three formats.
2. A `cover-typography` tool (Python/Pillow) reproduces those covers from a per-book
   spec + a font manifest — deterministic, re-runnable, documented.
3. A static site (`demo/books/site/`) renders the gallery: real covers on the front,
   info panels (title/author/blurb/meta/CTA) on the flip, consuming **only** exported
   tokens for design values. Hover + tap + keyboard + reduced-motion all work.
4. `demo/books/DESIGN.md` lints green, exports cleanly, and documents the system well
   enough that "add a fourth book / make another page" is a recipe, not a redesign.
5. Evidence captured per AGENTS.md (screenshots resting/flipped/mobile/thumbnail,
   computed-style checks, lint/export logs, file-size table) and a handoff written.

---

## 2. What already exists (recap, so we build *with* it)

- **Proven pipeline:** extract → author `DESIGN.md` → `tools/designmd-lint` → `tools/designmd-export` → recreate-from-exports → evidence. Documented in `~/.myagents/skills/designmd-reverse-engineer/SKILL.md`.
- **Shelf & Spine** (`demo/book-flip/DESIGN.md` + `index.html`): the flip system as
  tokens — warm literary palette, Fraunces/Inter, `motion.flip` (transform 450ms ease),
  2:3 card, perspective/preserve-3d/backface mechanics, hover+tap+keyboard+reduced-motion,
  CTA click-guard. **This is the spine we extend.** Its covers are token-rendered fakes;
  the new site swaps in real baked covers.
- **Three covers** (`demo/books/`), already ~1.6:1 (992×1586):
  - `the-last-word-openai-l1.png` — post-apocalyptic dystopian thriller (ruined city, glowing forbidden book). Dossier: `BOOKHUB/The Last Word/Plans/`.
  - `the-signal-openai-s1.png` — contemporary techno/surveillance thriller-mystery (night, monitor wall, coastal city, camera). Dossier: `BOOKHUB/The Signal/Dossier/Story_Dossier_Worksheet.md`, `the_signal_output.json`.
  - `julian-pike-openai-d1.png` — "later-in-life alt-history caper" / witty crime-mystery (cream collage, vintage limo, photos, romance silhouette). Dossier: `BOOKHUB/The Tasteful Kidnapping of Julian Pike/story-dossier-yaml-format/`.
- **Tools:** `designmd-lint/validate.py`, `designmd-export/export.py` (mirror the skill's
  `scripts/`; change both when changing either). Need PyYAML (in `.venv`). **New:** Pillow
  for the cover tool.
- **Pre-downloaded font library** (Carlo's, to copy in): `…/carlo-v-santiago.com/workspace-carlo/kindle-cover-specs/font-library/google-fonts`
  — **33 families / 44 files**, curated for Kindle covers, skewed to literary display/serif/
  script/blackletter. **Mostly variable fonts** (`Oswald[wght]`, `Fraunces[opsz,wght]`, …).
  Genre coverage vs our three books:
  - Last Word (dystopian thriller) → **Anton** / Oswald / Bebas Neue (bold condensed impact).
  - Julian Pike (vintage caper) → **Playfair Display** / Bodoni Moda / Cormorant / Marcellus.
  - The Signal (techno thriller) → **gap:** no mono/techno-geometric face; closest is
    League Spartan / Montserrat. The *only* candidate font fetch in the build (Slice 2 decides).
  - No `LICENSE` files present; all OFL Google Fonts (license recorded per face in `fonts.json`).

---

## 3. Decisions locked (from intake Q&A)

| Fork | Decision |
|---|---|
| Cover text | **Baked into the image** via Pillow. Emit **PNG + JPG + WEBP**; report file sizes for load-time comparison. |
| Title fonts | **Per-genre faces**, each appropriate to genre & reader expectation. Back research with **recent (2024–2026)** real comps + sample images where knowledge is thin. Sources must be recent publications. |
| Back face | **Info panel** (title, author, blurb, metadata, buy CTA) from real dossier content. |
| Delivery | **Self-contained static HTML site** (like existing demos), GitHub-Pages-deployable. |

**Reconciling per-genre fonts with a *replicable* DESIGN.md:** the system defines a
`cover-title` / `cover-author` typography **role** (defaults + the selection *method* as
prose), and each book carries a **per-book override** as instance data. The DESIGN.md
captures the methodology + slots; the three faces are values that fill the slots. This
keeps it a real design system, not three one-offs. (Boundary triage in §6.)

---

## 4. Architecture — where things live

```
demo/books/
  *.png                         # original textless source covers (unchanged)
  DESIGN.md                     # ← THE representative artifact (evolves Shelf & Spine)
  dist/                         # exported tokens (tokens.css/json, tailwind.config.js)
  covers/
    <slug>/cover-spec.yaml      # per-book titling spec (title, author, font, scrim, safe-zone)
    <slug>/dist/                # titled cover.{png,jpg,webp} + qa-contact-sheet.png + report.json
  data/books.json               # per-book site content (title, author, kicker, blurb, meta, cta, cover paths)
  site/
    index.html                  # the gallery (consumes ../dist/tokens.css only for design values)
    assets/                     # web-optimized titled covers (webp primary, jpg fallback)
tools/
  cover-typography/
    compose.py                  # Pillow compositor: spec + fonts → titled covers + QA + report
    fonts/                      # copied from Carlo's kindle-cover-specs library (git-ignored binaries)
    fonts.json                  # manifest: family, file, weight-axis value, Google Fonts URL, OFL license
    fetch_fonts.py              # ONLY for a gap font not already in fonts/ (e.g. a techno face)
    README.md
workspace/
  evidence/20260621-NN-*.png    # screenshots + contact sheets
  handoffs/20260621-NN-*.md     # completion handoff
```

`.gitignore` additions: `tools/cover-typography/.fonts-cache/` (OFL binaries, fetched
on demand). Titled cover outputs *are* deliverables → force-track `demo/books/covers/**/dist/`
and `demo/books/site/assets/` the same way `demo/**/dist/` is already negated.

---

## 5. The slices (with subagent + QC + evidence per slice)

Six slices. 1–2 fan out to subagents and can run **in parallel** at the start; 3–6 are
mostly mine (integration-heavy) with targeted delegation.

### Slice 1 — Book content extraction → `data/books.json`  *(subagents, parallel ×3)*
- **Goal:** real per-book site copy from the dossiers.
- **Work:** one subagent per book reads that book's dossier/summary and returns:
  kicker (genre tag), back-cover **blurb** (≤ ~50 words, hook not synopsis, spoiler-safe),
  metadata line (author = A. May Zing · imprint · 2026), CTA label/price, and a one-line
  genre statement to feed Slice 2.
- **QC gates (mine):** blurb ≤ 50 words; on-voice vs dossier's style directives; no
  spoilers past the inciting hook; factually consistent with the dossier; no invented
  proper nouns. Reject + re-run any miss; I spot-read the dossier to verify.
- **Evidence:** `data/books.json` + a short provenance note (which dossier fields used).

### Slice 2 — Genre cover-typography research  *(subagents, parallel ×3)*
- **Goal:** for each genre, a defensible **Google Font** title face + treatment, grounded
  in 2024–2026 comps.
- **Work:** one research subagent per genre (dystopian thriller / techno-thriller-mystery /
  alt-history caper) returns: 2–3 recent real titles with cover-type observations, a
  recommended title + author face **chosen first from the existing 33-family library**
  (see §2), case/tracking/weight, and a color+scrim direction that suits *that specific
  illustration's* text zone. A font **outside** the library may be proposed **only** if the
  genre genuinely needs it (anticipated: The Signal's techno face) — then it must be OFL and
  go through `fetch_fonts.py`. Pull sample images where knowledge is thin; **cite sources,
  2024–2026 only.**
- **QC gates (mine):** pick is in the library *or* a justified OFL fetch; recommendation
  matches genre convention *and* the actual art (dark sky zones for Last Word/Signal; cream
  negative-space top for Julian Pike); sources are recent and real (I spot-check 1–2).
  Reject hand-wavy or dated picks, and reject an out-of-library pick when an in-library face
  would serve (don't fetch for novelty).
- **Evidence:** a research note per book in `workspace/scratch/` + the chosen face → fills
  each `covers/<slug>/cover-spec.yaml`.

### Slice 3 — Cover-typography tool  *(mine; optional scaffold delegation)*
- **Goal:** deterministic Pillow tool that bakes titling + validates.
- **Work:** see §7 for full design. Build `compose.py`, `fonts.json`, `fetch_fonts.py`,
  README. Encode the battle-tested rules (safe margins, ≤2 title lines, auto-fit,
  scrim/stroke for contrast, thumbnail cap-height gate, upscale to 1600×2560). Emit
  PNG+JPG+WEBP, a QA contact sheet (full + 160px thumbnail), and a `report.json`
  (dimensions, ratio, per-format file size, thumbnail cap-height px, text-zone contrast).
- **QC gates (mine):** re-run is byte-stable; all three covers PASS the legibility gate;
  ratio == 1.6 ±0.5%; report file-size table present.
- **Evidence:** three `covers/<slug>/dist/` sets + contact sheets in `workspace/evidence/`
  + the file-size comparison table.

### Slice 4 — Representative `DESIGN.md`  *(mine)*
- **Goal:** evolve Shelf & Spine into the production system at `demo/books/DESIGN.md`.
- **Work:** keep palette/flip/motion/gallery/info-face. **Add** the cover-typography
  concern: `cover-title`/`cover-author` type roles + per-book override tokens, a `scrim`
  color (translucent, alpha) reusing the glass module's worst-case-contrast discipline,
  `cover-safe-inset` spacing, and a `cover` component declaring title/author/scrim/safe
  props. Prose: the genre→face **selection method**, the Kindle-ratio + thumbnail-legibility
  **QA contract**, and Do's/Don'ts. **Boundary triage first (§6): confirm no new token
  *type* is needed** — reuse typography + colors(+alpha) + spacing + DTCG shadow.
- **QC gates (mine):** `validate.py` exits 0; every component bg/text pair meets AA (or is
  a declared advisory with a backdrop); `export.py` produces all three targets; the
  per-book override pattern round-trips through export.
- **Evidence:** lint log (green), `demo/books/dist/` exports.

### Slice 5 — The static site  *(mine)*
- **Goal:** the gallery, "putting it all together."
- **Work:** `site/index.html` — header/hero with site identity, responsive grid of flip
  cards. Front = real titled cover (`<picture>`: webp → jpg fallback, `loading="lazy"`,
  width/height set, 2:3 box). Back = info panel from `books.json`. Design values come
  **only** from `dist/tokens.css` (`var(--…)`); literals limited to structural mechanics.
  Port the proven flip script (hover gated to `@media (hover:hover)`, JS `is-flipped` for
  tap/keyboard, Escape + click-outside close, CTA click-guard). Honor `prefers-reduced-motion`.
- **QC gates (mine):** no hard-coded brand values; keyboard reachable; CTA clickable on
  flip; covers don't layout-shift (CLS); reduced-motion collapses the flip.
- **Evidence:** in Slice 6.

### Slice 6 — Verify, evidence, handoff  *(mine)*
- **Work:** serve (`python3 -m http.server`), screenshot resting / flipped / mobile /
  reduced-motion; verify computed `transition` resolves to `motion.flip`; verify a
  component bg resolves through the `{ref}` chain to the literal color; confirm covers at
  thumbnail size stay legible in-page. Write the handoff + (optional) "replicate to a new
  page" recipe as the final replication-kit proof.
- **Evidence:** screenshots + computed-style dump in `workspace/evidence/`; handoff in
  `workspace/handoffs/`.

---

## 6. Boundary triage for cover typography (keep the DESIGN.md honest)

Per the skill's "boundary that makes this honest," classify before tokenizing:

- **Values → tokens:** title/author font, size, weight, tracking, case → `typography`;
  text color + translucent scrim → `colors` (with alpha); safe-zone inset → `spacing`;
  any drop-shadow behind text → DTCG `shadow` (already supported by the glass module).
  **→ No new token *type* is required.** (If research surfaces a genuinely new value —
  e.g. a text *stroke* distinct from shadow — only then extend, via the skill's 7-step
  "new effect family" protocol and a failing-lint proof. Expected: not needed.)
- **Structure → component props / the tool:** Kindle 1.6:1 canvas, safe-zone box,
  auto-fit line-breaking, upscale resampling. Mechanics, not values.
- **Behavior/QA contract → prose + the tool:** "title must clear ≥X px cap-height at a
  160px thumbnail," "text contrast ≥4.5:1 over its zone after scrim," "≤2 title lines,"
  "OFL fonts only." Recorded as the cover token's contract (the way motion collapses
  under reduced-motion), enforced by `compose.py`'s `report.json` gate.

This is the teaching payload: the *method* is the system; the three faces are data.

---

## 7. Cover-typography tool design (`tools/cover-typography/`)

**Why a tool, not hand-placed text:** deterministic, re-runnable, and it *validates* —
the "readable at thumbnail" and "Kindle ratio" requirements become automated gates, not
eyeballing.

**Inputs**
- Source cover PNG (992×1586).
- `cover-spec.yaml` per book: `title`, `author`, `title_font`/`author_font` (→ `fonts.json`),
  `case`, `tracking`, `align`, `text_color`, `scrim` (color+alpha+direction or none),
  `safe_zone` (normalized box, e.g. top third for Last Word/Signal, top-center for Julian
  Pike), optional `shadow`/`stroke`.
- `fonts/` (copied from Carlo's library) + `fonts.json` manifest. `fetch_fonts.py` only for a
  gap font (the techno face); binaries git-ignored, manifest tracked for reproducibility.

**Pipeline (`compose.py`)**
1. Load source; **normalize to Kindle 1.6:1** → upscale to **1600×2560** (Lanczos). *(Caveat: source is 992w; 1.6× upscale is fine for web, marginal for print — flagged in report.)*
2. Resolve font — **for variable fonts, set the weight axis explicitly** via
   `ImageFont.set_variation_by_axes`/`set_variation_by_name` (otherwise Pillow renders the
   default weight and a "bold" pick silently comes out regular). **Auto-fit** the title into
   the safe-zone box (shrink until ≤2 lines fit with margins).
3. Apply legibility treatment: scrim gradient and/or text shadow/stroke sized to guarantee contrast over that zone.
4. Composite title + author in the safe zone.
5. Export **PNG, JPG (q≈82), WEBP (q≈80)**; record each file size.
6. **QA:** downscale to a 160px-wide thumbnail; measure rendered title cap-height (px) and
   text-zone contrast; **PASS/FAIL** against thresholds. Emit `qa-contact-sheet.png`
   (full + thumbnail side by side) and `report.json`.

**Gates (in `report.json`)**: `ratio≈1.600`; `thumbnail_cap_height_px ≥ ~16`;
`text_contrast ≥ 4.5`; `lines ≤ 2`; file-size table (png/jpg/webp).

**Licensing note:** Google Fonts are OFL — baking onto a commercial cover is permitted;
record license per font in `fonts.json`.

---

## 8. Subagent supervision & QC (the standing rules for this build)

- **Fan-out:** Slice 1 (×3 blurbs) and Slice 2 (×3 research) launch concurrently — 6 agents,
  independent, all read-only against BOOKHUB + web.
- **I supervise every return.** No subagent output ships unreviewed. Each slice above lists
  explicit, checkable QC gates; a miss = re-task that agent with the specific defect, not a
  silent fix. I spot-verify against primary sources (dossiers; cited cover pages).
- **Build stays with me** (tool, DESIGN.md, site) — too integration-coupled to delegate
  blind. I may delegate *scaffolding* (e.g. a first `compose.py` draft) but I run, read, and
  own the result.
- **Evidence is mandatory** per AGENTS.md before any slice is called done.

---

## 9. Risks & open items

- **Upscale quality:** 992→1600 px width is a 1.6× enlargement; acceptable on screen,
  flagged for print. If Carlo wants true print masters, regenerate sources at ≥1600w.
- **Text-zone fit:** Julian Pike's cream collage has busy edges; the safe zone is the
  top-center cream — scrim may be unnecessary there but contrast must still be measured
  (dark text on cream). Last Word/Signal have dark skies → light text, light scrim.
- **Per-genre font load:** non-issue for the site (rasterized into covers = 0 web-font
  cost); the *site chrome* keeps Fraunces+Inter only.
- **`tools/` ↔ skill mirror:** the cover tool is **new** and lives only in this repo for
  now (not a skill mirror). If it proves out, propose it as a skill module later — do **not**
  silently fork the designmd skill.
- **Techno-face gap:** the library has no mono/geometric-techno face for The Signal. Mitigation:
  try League Spartan/Montserrat first; fetch one OFL face only if research shows it's needed.
- **Variable fonts:** 44 files are mostly variable; `compose.py` must pin the weight axis
  (see §7-2) — a silent failure mode if missed. Build a tiny render smoke-test per font.
- **Font tracking policy:** copy the library into `tools/cover-typography/fonts/` for work,
  but **git-ignore the binaries** (AGENTS: no large binaries tracked) and rely on `fonts.json`
  (family + Google Fonts URL + license) for reproducibility.
- **Open:** site imprint name + price/CTA per book (placeholder "Parchment Press · 2026 ·
  Buy $14.99" unless Carlo specifies); whether to deploy to GitHub Pages now or just build.

## 10. Sequence / dependency graph

```
        ┌─ Slice 1 (blurbs ×3) ─────────────┐
start ──┤                                    ├─→ Slice 4 (DESIGN.md) ─→ export ─┐
        └─ Slice 2 (font research ×3) ─→ Slice 3 (cover tool → titled covers) ──┴─→ Slice 5 (site) ─→ Slice 6 (verify+handoff)
```

Slices 1 & 2 parallel at start. Slice 3 needs Slice 2's fonts. Slice 4 can proceed in
parallel with 3 (it needs the *role* design, not the rendered covers). Slice 5 needs 3
(covers) + 4 (exported tokens) + 1 (copy). Slice 6 closes out.
