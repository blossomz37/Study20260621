# Book-Cover Flip — Spec & Implementation Plan

**Date:** 2026-06-21
**Source effect:** JUDGES grid on https://rgdbrandingawards.com/ (Astro site)
**Goal:** A reusable book-cover component that flips on interaction to reveal the back cover *or* a structured info panel (blurb, author, buy link).
**Provenance:** Mechanism reverse-engineered from live DOM/CSS/JS. Exact rules quoted below were pulled from `/_astro/index.B5QMzA5h.css` and the page's inline module scripts on 2026-06-21. RGD's code is © RGD — we reimplement the *technique* (a standard CSS flip card), not their assets, copy, or brand styling.

---

## 1. How the source effect actually works (ground truth)

The RGD judge tile is a **textbook CSS 3D flip card**. Verbatim mechanism from their CSS (de-scoped from their `[data-astro-cid-…]` attributes):

```css
.judge-tile  { width:184px; height:184px; position:relative; cursor:pointer; perspective:800px; }
.judge-inner { width:100%; height:100%; position:relative; transform-style:preserve-3d; }
.judge-front,
.judge-back  { position:absolute; inset:0; overflow:hidden;
               backface-visibility:hidden; -webkit-backface-visibility:hidden; }
.judge-front { background:#cccbc6; }              /* placeholder behind photo */
.judge-back  { transform:rotateY(180deg); }       /* pre-rotated so it reads correctly after flip */

/* transition ONLY when motion is allowed */
@media (prefers-reduced-motion: no-preference) {
  .judge-inner { transition: transform .45s ease; }
}
/* otherwise */
.judge-inner { transition: none; }

/* hover flip — gated so touch devices don't sticky-hover */
@media (hover: hover) {
  .judge-tile:not(.judge-tile--accent):hover .judge-inner { transform: rotateY(180deg); }
}
/* JS-driven flip (touch tap / keyboard) */
.judge-tile.is-flipped .judge-inner { transform: rotateY(180deg); }
```

**The whole flip is pure CSS.** Their only flip JavaScript is one 593-character module (de-minified, unchanged logic):

```js
(() => {
  const isTouch = window.matchMedia("(hover: none)").matches;
  const tiles = [...document.querySelectorAll(".judge-tile:not(.judge-tile--accent)")];
  const closeAll = () => tiles.forEach(t => t.classList.remove("is-flipped"));

  tiles.forEach(tile => {
    if (isTouch) tile.addEventListener("click", () => {
      const open = tile.classList.contains("is-flipped");
      closeAll(); if (!open) tile.classList.add("is-flipped");
    });
    tile.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        const open = tile.classList.contains("is-flipped");
        closeAll(); if (!open) tile.classList.add("is-flipped");
      }
      if (e.key === "Escape") closeAll();
    });
  });
  document.addEventListener("click", e => { if (!e.target.closest(".judge-tile")) closeAll(); });
})();
```

That script does exactly three things: (1) tap-to-flip on `(hover: none)` devices, (2) Enter/Space to flip + Escape to close for keyboard users, (3) click-outside closes any open tile. It never computes the animation — it only toggles `.is-flipped`.

**Markup pattern** (one tile, attributes trimmed):

```html
<div class="judge-tile judge-tile--square judge-tile--magenta"
     role="button" tabindex="0"
     aria-label="Léo Breton-Allaire, Caserne, Montréal, QC">
  <div class="judge-inner">
    <div class="judge-front">
      <img class="judge-photo" src="…webp" alt loading="lazy" decoding="async">
    </div>
    <div class="judge-back" aria-hidden="true">
      <p class="judge-name">Léo Breton-Allaire</p>
      <div class="judge-meta"><p>Caserne</p><p>Montréal, QC</p></div>
    </div>
  </div>
</div>
```

Key accessibility decisions they made: tile is `role="button" tabindex="0"` with a full `aria-label` describing the back-face content; the back face itself is `aria-hidden="true"` (so the info is announced once, via the label, not duplicated). Hover is gated behind `@media (hover: hover)`; transitions behind `prefers-reduced-motion`.

**Brand flourishes we will NOT copy** (RGD-specific, not relevant to book covers):
- Mixed tile shapes: `--square`, `--circle` (`border-radius:999px`), and single-rounded-corner variants (`border-radius:0 245px 0 0`, etc.), each with per-shape back-face padding/alignment.
- Brand back-face colors: magenta `#e32961`/white, pink `#ffb1de`/`#270273`, orange `#ffa600`/`#270273`, blue `#4cadf3`/`#270273`.
- `--accent` tiles: decorative color blocks with `cursor:default` and no back face.
- A site-wide pause toggle (`body[data-animations-paused]`) and Konami easter egg — out of scope, but the pause pattern is noted in §6 as an optional add-on.

---

## 2. What changes for book covers

| Dimension | RGD judge tile | Book-cover flip |
|---|---|---|
| Aspect ratio | 1:1 square, 184px | **Portrait ~2:3** (e.g. 1600×2400). Use `aspect-ratio: 2 / 3`, fluid width. |
| Front face | Portrait photo on `#cccbc6` | **Front cover image** |
| Back face | Name + studio + city | **Mode A:** back-cover image. **Mode B:** info panel (blurb, author, price, CTA). **Mode C:** both (image with overlaid/below text). |
| Shape | Mixed brand shapes | Single rectangle, optional small `border-radius` + book-spine shadow |
| Trigger | Hover (desktop), tap (touch) | Same, **plus** a recommended explicit click/tap default so covers feel like buttons, not hover toys |
| Interactivity on back | None (static text) | Back may contain a **real link/button** ("Buy", "Read more") → needs care so the link is reachable and the flip doesn't swallow the click |

The single most important structural difference: **a book back-cover or info panel often contains an interactive element (a buy link).** The RGD back face is inert. That changes the interaction model — see §4.

---

## 3. Component API (proposed)

Framework-agnostic core (works as a plain custom element, an Astro component, or a React/Svelte wrapper). One book = one instance.

```
BookFlip props:
  front:        { src, alt }                         // required — front cover image
  backMode:     "image" | "info" | "image+info"      // default "info"
  back:         { src, alt }                          // when backMode includes "image"
  info:         {                                     // when backMode includes "info"
    title, author, blurb,
    meta?: [ "Genre", "Series #2", "Published 2026" ],
    cta?:  { label: "Buy on Amazon", href }           // optional real link
  }
  trigger:      "hover" | "click" | "both"           // default "both" (hover on desktop, tap on touch)
  flipAxis:     "y" | "x"                             // default "y"
  flipDirection:"left" | "right"                      // default "left" (rotateY 180 vs -180)
  size:         CSS width (e.g. "240px" | "min(40vw,300px)")  // height derived from aspect-ratio
```

A multi-cover grid is just a flex/grid wrapper of `BookFlip` instances — no shared state needed beyond the close-others behavior (lifted to one document-level listener, as RGD does).

---

## 4. Interaction model decision (the one real fork)

Because a book back face can hold a **CTA link**, "hover to flip" alone is fragile: a user hovers, the back appears, they move the mouse to click "Buy", and on a grid the cursor may cross another cover. Recommended model:

- **Desktop:** hover *previews* the flip (matches the source's delight factor), **but** also support an explicit click that "pins" the flip (`is-flipped`) so the back stays open while the user reaches the CTA. Hover-only covers with no CTA can stay hover-only.
- **Touch:** tap flips (`is-flipped`); the CTA is then a normal tap. First tap flips, second tap on the CTA follows the link. (Exactly the RGD touch model + a real link on the back.)
- **Keyboard:** the tile is `role="button" tabindex="0"`; Enter/Space flips; when flipped, the CTA is a normal focusable `<a>` in tab order; Escape closes.
- **Click-swallowing guard:** if `trigger` includes click, the tile's own click handler must ignore clicks that originate inside the CTA (`if (e.target.closest('a,button')) return;`) so the buy link isn't intercepted.

**Recommendation:** default `trigger: "both"` and, whenever `info.cta` is present, force a *click-to-pin* in addition to hover. Surface this as the documented default; no need to ask per-instance.

---

## 5. Accessibility & correctness requirements (carry over from source + book-specific)

1. `transform-style: preserve-3d` on `.inner`; `perspective` on the **outer** tile only.
2. Both faces `backface-visibility: hidden` (+ `-webkit-` prefix for Safari).
3. Back face pre-rotated 180° so text isn't mirrored.
4. Matching `border-radius`/`overflow:hidden` on **both** faces or rounded corners break mid-flip.
5. Gate hover behind `@media (hover: hover)`; gate the transition behind `@media (prefers-reduced-motion: no-preference)` (fall back to `transition: none`).
6. Tile: `role="button"`, `tabindex="0"`, and a descriptive `aria-label`. If the back is purely a duplicate image of info already in the label, mark it `aria-hidden`. **But** if the back contains the *only* copy of the blurb or a CTA link, do **not** `aria-hidden` it — instead manage focus/visibility so it's reachable when flipped (this diverges from RGD, whose back is inert).
7. Don't trap: `Escape` closes; click-outside closes.
8. Performance: animate `transform` only (the source uses `transform .45s ease`); avoid `overflow`/`filter` on intermediate ancestors that can flatten `preserve-3d` in Safari. Lazy-load cover images (`loading="lazy" decoding="async"`), as RGD does.
9. Provide a real `<img alt>` for both faces in image modes; the info-mode back is real text (good for SEO/readers).

---

## 6. Optional production-parity add-ons (defer unless asked)

- **Pause toggle:** RGD wires a button that toggles `body[data-animations-paused]` and dispatches `rgd:animations-paused` / `…-resumed` events; CSS kills the transition when the attribute is present. Easy to port if a "reduce motion" UI control is wanted beyond the OS setting.
- **Flip-on-scroll / staggered intro** for a grid (IntersectionObserver) — RGD uses this pattern elsewhere on the page.
- **3D depth polish:** subtle spine shadow, a slight `box-shadow` that intensifies mid-flip, or a paper-edge gradient to sell "this is a physical book."

---

## 7. Implementation plan (phased)

**Phase 0 — Scaffold & evidence baseline**
- Create `workspace/` demo dir or a standalone `demo/` page. Decide host: a single static `index.html` (zero-build, matches "demo piece") vs. an Astro/Vite component. *Recommendation: start with one static HTML/CSS/JS file* — the effect needs no build, and it's the cleanest teaching artifact. Promote to a component only if it goes into a real site.
- Capture a "before"/reference screenshot of the RGD effect for the evidence folder (per AGENTS.md task-completion rules).

**Phase 1 — Pure-CSS flip (desktop hover), one cover**
- Build the `.book-flip` → `.book-inner` → `.book-front`/`.book-back` structure with `aspect-ratio: 2/3`.
- Front = cover image; back = info panel (Mode B) as the default to prove the harder layout.
- Verify: hover flips, back reads correctly (not mirrored), rounded corners hold, reduced-motion disables transition.

**Phase 2 — JS interaction layer (~20–30 lines)**
- Port the 593-char RGD script: `(hover:none)` tap toggle, Enter/Space/Escape, click-outside-closes, close-others.
- Add the CTA click guard (`closest('a,button')`).
- Add `click-to-pin` on desktop when a CTA is present.

**Phase 3 — Modes & theming**
- Implement `backMode` (image / info / image+info) and `flipAxis`/`flipDirection`.
- Tokenize colors/spacing/radius as CSS custom properties so a book's palette can theme the info back.
- Multi-cover grid demo (3–6 books) to validate close-others and layout.

**Phase 4 — Accessibility & QA**
- Keyboard-only walkthrough; screen-reader pass on label vs. back-face content; reduced-motion; Safari `preserve-3d` check; mobile tap + CTA tap.
- Screenshots (front, mid-flip, back, mobile) → `workspace/evidence/` with naming convention.

**Phase 5 — Package**
- Extract into a reusable component (custom element `<book-flip>` is the most portable; or an Astro/React wrapper). Document the API from §3. Optional: publish as a small snippet for FFA course labs / a vibecoding starter.

---

## 8. Risks / gotchas (from the source analysis, confirmed)

- Forgetting `preserve-3d` → flat flip / back never shows.
- Missing `backface-visibility:hidden` → mirrored image bleeds through.
- Back not pre-rotated 180° → mirrored text.
- `overflow:hidden`/`filter` on an ancestor → Safari flattens the 3D context.
- Touch `:hover` stickiness → must gate hover behind `@media (hover:hover)` and drive touch via the `.is-flipped` class (the whole reason RGD ships JS).
- **Book-specific:** the CTA-on-back interaction — without the click guard and click-to-pin, hover users can't reach the buy link. This is the part the RGD pattern does *not* solve for you.

---

## 9. Deliverables checklist

- [ ] `demo/index.html` (single-file flip demo) — Phases 1–3
- [ ] Reusable `<book-flip>` component + README API — Phase 5
- [ ] Evidence screenshots (front / mid-flip / back / mobile) in `workspace/evidence/`
- [ ] Short handoff in `workspace/handoffs/` linking evidence

---

### Appendix A — Reference values pulled from the live site (for fidelity, not reuse)
- Flip transition: `transform .45s ease`
- Perspective: `800px`
- Tile size (source): `184px` square, grid `repeat(5,184px)` gap `50px`
- Back-face brand colors: magenta `#e32961`/`#fff`; pink `#ffb1de`/`#270273`; orange `#ffa600`/`#270273`; blue `#4cadf3`/`#270273`; front placeholder `#cccbc6`
- Corner radius for rounded variants: `245px`; circle: `999px`
- Source stack: Astro (scoped `data-astro-cid-*`), images served as `.webp`, fonts `.woff/.woff2`
