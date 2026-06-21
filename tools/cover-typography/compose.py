#!/usr/bin/env python3
"""
compose.py — deterministic cover-typography compositor.

Bakes genre-appropriate titling onto a textless book cover and validates the
result against a Kindle-ratio + thumbnail-legibility QA contract.

  spec (cover-spec.yaml) + font manifest (fonts.json) + source PNG
      -> titled cover .png/.jpg/.webp
      -> qa-contact-sheet.png (full + 160px thumbnail)
      -> report.json (ratio, file sizes, thumbnail cap-height, text contrast, PASS/FAIL)

Design boundary (mirrors the designmd skill):
  * VALUES  (font, size, weight, tracking, color, scrim, safe-inset) come from the spec.
  * STRUCTURE (1.6:1 canvas, safe-zone box, auto-fit, upscale) is mechanics, here.
  * The QA CONTRACT (ratio, >=N px cap-height at 160px, >=4.5:1 contrast, <=max lines,
    OFL fonts) is enforced by the report.json gate below.

Deterministic: same spec + same fonts -> byte-stable output (no timestamps, fixed
resampling, fixed encoder quality).

Usage:
  python3 compose.py path/to/cover-spec.yaml [--strict]
  python3 compose.py --all          # every covers/<slug>/cover-spec.yaml under demo/books
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "fonts.json"
FONTS_DIR = HERE / "fonts"

# Kindle master canvas + QA thresholds (the contract).
KINDLE_W, KINDLE_H = 1600, 2560
TARGET_RATIO = KINDLE_H / KINDLE_W            # 1.6
RATIO_TOL = 0.005                              # +-0.5%
THUMB_W = 160                                  # thumbnail-legibility test width
MIN_THUMB_CAP_PX = 14.0                        # title cap-height floor at thumbnail
MIN_CONTRAST = 4.5                             # WCAG AA normal text
JPG_QUALITY = 82
WEBP_QUALITY = 80


# ---------- color / contrast (WCAG 2.x) ----------

def _hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore


def _rel_lum(rgb) -> float:
    def chan(c):
        c /= 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb[:3]
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def _contrast(l1: float, l2: float) -> float:
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ---------- font resolution (pins variable axes — the silent failure mode) ----------

def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text())["fonts"]


def resolve_font(manifest: dict, key: str, size: int, axes: dict | None) -> ImageFont.FreeTypeFont:
    if key not in manifest:
        raise SystemExit(f"font '{key}' not in fonts.json")
    entry = manifest[key]
    path = FONTS_DIR / entry["file"]
    if not path.exists():
        raise SystemExit(f"font file missing: {path} (run fetch_fonts.py or copy from the library)")
    font = ImageFont.truetype(str(path), size)
    if entry.get("variable") and axes:
        # Pillow renders the axis DEFAULT unless we set it; League Spartan/Montserrat
        # default to wght=100 (hairline). Pin every axis the spec names.
        order = [a.encode() for a in ("wght", "opsz", "wdth", "slnt", "ital") if a in axes]
        try:
            font.set_variation_by_axes([float(axes[a.decode()]) for a in order])
        except Exception:
            # fall back to named-instance lookup if axis-by-value is unsupported
            pass
    return font


# ---------- text geometry ----------

def _line_size(font, text):
    l, t, r, b = font.getbbox(text)
    return r - l, b - t


def cap_height(font) -> float:
    """Ink height of a capital letter at this font size."""
    l, t, r, b = font.getbbox("H")
    return b - t


def fit_title(manifest, key, axes, lines, box_w, box_h, line_spacing, max_px):
    """Largest integer font size where the widest line fits box_w and the stacked
    block (n lines * (cap + spacing)) fits box_h. Binary search -> deterministic."""
    lo, hi, best = 8, int(max_px), 8
    while lo <= hi:
        mid = (lo + hi) // 2
        font = resolve_font(manifest, key, mid, axes)
        widest = max(_line_size(font, ln)[0] for ln in lines)
        line_h = cap_height(font) * line_spacing
        block_h = line_h * len(lines)
        if widest <= box_w and block_h <= box_h:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    return best


# ---------- scrim ----------

def apply_scrim(img: Image.Image, scrim: dict | None) -> Image.Image:
    if not scrim:
        return img
    color = _hex_rgb(scrim["color"])
    peak = float(scrim["opacity"])
    direction = scrim.get("direction", "top")
    extent = float(scrim.get("extent", 0.3))     # fraction of H where the scrim reaches 0
    hold = float(scrim.get("hold", 0.0))         # fraction held at full peak before fading
    W, H = img.size
    span = max(1, int(H * extent))
    hold_px = int(H * hold)
    fade = max(1, span - hold_px)
    grad = Image.new("L", (1, H), 0)
    px = grad.load()
    for y in range(H):
        if direction == "top":
            d = y
        elif direction == "bottom":
            d = H - 1 - y
        else:
            d = span
        if d <= hold_px:
            t = 1.0                               # plateau: full strength across the text band
        elif d < span:
            t = 1.0 - (d - hold_px) / fade        # then linear fade to 0
        else:
            t = 0.0
        px[0, y] = int(max(0.0, min(1.0, t)) * peak * 255)
    alpha = grad.resize((W, H))
    overlay = Image.new("RGBA", (W, H), color + (0,))
    overlay.putalpha(alpha)
    return Image.alpha_composite(img.convert("RGBA"), overlay)


# ---------- text drawing (shadow/glow + stroke for legibility) ----------

def draw_block(base: Image.Image, lines, font, color, cx, top_y, line_spacing,
               stroke=None, shadow=None) -> tuple[int, int, int, int]:
    """Draw centered, stacked lines. Returns the ink bbox (l,t,r,b) of the whole block."""
    W, H = base.size
    line_h = cap_height(font) * line_spacing
    rgb = _hex_rgb(color)

    # soft shadow / outer glow on its own layer, then composited under the text
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        scol = _hex_rgb(shadow["color"]) + (int(float(shadow.get("opacity", 0.5)) * 255),)
        off = int(shadow.get("offset", 0))
        for i, ln in enumerate(lines):
            w, _ = _line_size(font, ln)
            x = cx - w // 2 + off
            y = int(top_y + i * line_h) + off
            sd.text((x, y), ln, font=font, fill=scol)
        sh = sh.filter(ImageFilter.GaussianBlur(float(shadow.get("blur", 6))))
        base.alpha_composite(sh)

    draw = ImageDraw.Draw(base)
    sw = int(stroke["width"]) if stroke else 0
    sfill = _hex_rgb(stroke["color"]) if stroke else None
    xs, ys, xe, ye = W, H, 0, 0
    for i, ln in enumerate(lines):
        w, _ = _line_size(font, ln)
        x = cx - w // 2
        y = int(top_y + i * line_h)
        draw.text((x, y), ln, font=font, fill=rgb,
                  stroke_width=sw, stroke_fill=sfill)
        l, t, r, b = draw.textbbox((x, y), ln, font=font, stroke_width=sw)
        xs, ys, xe, ye = min(xs, l), min(ys, t), max(xe, r), max(ye, b)
    return xs, ys, xe, ye


# ---------- QA: worst-case zone contrast ----------

def zone_worst_contrast(bg: Image.Image, box, text_color, light_text: bool) -> float:
    """Contrast of text vs the least-favorable luminance inside the text bbox of the
    scrimmed background. Light text -> brightest 95th-pct pixel; dark text -> darkest
    5th-pct. Mirrors the glass module's 'worst-case stop' discipline."""
    l, t, r, b = [int(v) for v in box]
    crop = bg.convert("RGB").crop((l, t, r, b))
    px = list(crop.getdata())
    if not px:
        return 0.0
    lums = sorted(_rel_lum(p) for p in px)
    n = len(lums)
    zone_l = lums[int(0.95 * (n - 1))] if light_text else lums[int(0.05 * (n - 1))]
    return _contrast(_rel_lum(_hex_rgb(text_color)), zone_l)


# ---------- main compose ----------

def compose(spec_path: Path, strict: bool = False) -> dict:
    spec = yaml.safe_load(spec_path.read_text())
    manifest = load_manifest()
    spec_dir = spec_path.parent
    out_dir = spec_dir / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = spec["slug"]

    # 1. load + normalize to Kindle 1.6:1, upscale to 1600x2560 (Lanczos, deterministic)
    src_path = (spec_dir / spec["source"]).resolve()
    src = Image.open(src_path).convert("RGB")
    src_ratio = src.height / src.width
    img = src.resize((KINDLE_W, KINDLE_H), Image.LANCZOS).convert("RGBA")
    upscale_factor = KINDLE_W / src.width

    # 2. scrim over the text zone
    scrimmed = apply_scrim(img, spec.get("scrim"))
    bg_for_contrast = scrimmed.copy()       # measure contrast against bg only (pre-text)

    # 3. resolve safe-zone box (normalized -> px)
    sz = spec["safe_zone"]
    box_x = int(sz["x"] * KINDLE_W)
    box_y = int(sz["y"] * KINDLE_H)
    box_w = int(sz["w"] * KINDLE_W)
    box_h = int(sz["h"] * KINDLE_H)
    cx = box_x + box_w // 2

    # 4. auto-fit + draw title
    title_lines = spec["title_lines"]
    line_spacing = float(spec.get("line_spacing", 1.18))
    max_px = spec.get("title_max_px", box_h)
    t_axes = spec.get("title_axes")
    size = fit_title(manifest, spec["title_font"], t_axes, title_lines,
                     box_w, box_h, line_spacing, max_px)
    tfont = resolve_font(manifest, spec["title_font"], size, t_axes)
    light_text = _rel_lum(_hex_rgb(spec["text_color"])) > 0.5

    # scale px-relative treatments off the fitted cap height
    cap = cap_height(tfont)
    stroke = None
    if spec.get("stroke"):
        stroke = {"width": max(1, round(cap * float(spec["stroke"]["width"]))),
                  "color": spec["stroke"]["color"]}
    shadow = None
    if spec.get("shadow"):
        s = spec["shadow"]
        shadow = {"blur": round(cap * float(s["blur"])), "color": s["color"],
                  "opacity": s.get("opacity", 0.5), "offset": round(cap * float(s.get("offset", 0)))}

    block_h = cap * line_spacing * len(title_lines)
    title_top = box_y + max(0, (box_h - block_h) * float(spec.get("v_align", 0.0)))
    canvas = scrimmed
    tbox = draw_block(canvas, title_lines, tfont, spec["text_color"], cx, int(title_top),
                      line_spacing, stroke=stroke, shadow=shadow)

    # 5. author line below the title block
    author = spec.get("author")
    abox = None
    if author:
        a_axes = spec.get("author_axes")
        a_size = max(10, round(size * float(spec.get("author_scale", 0.32))))
        afont = resolve_font(manifest, spec["author_font"], a_size, a_axes)
        # letter-tracking via spacing string (Pillow has no tracking; insert thin spaces)
        track = int(spec.get("author_tracking", 0))
        atext = (" " * track).join(list(author)) if track else author
        a_gap = int(float(spec.get("author_gap", 0.02)) * KINDLE_H)
        a_y = tbox[3] + a_gap
        acolor = spec.get("author_color", spec["text_color"])
        a_stroke = {"width": max(1, round(cap_height(afont) * float(spec["stroke"]["width"]))),
                    "color": spec["stroke"]["color"]} if spec.get("stroke") else None
        abox = draw_block(canvas, [atext], afont, acolor, cx, a_y, 1.0, stroke=a_stroke,
                          shadow=shadow)

    final = canvas.convert("RGB")

    # 6. export PNG / JPG / WEBP + sizes
    paths = {
        "png": out_dir / f"{slug}.png",
        "jpg": out_dir / f"{slug}.jpg",
        "webp": out_dir / f"{slug}.webp",
    }
    final.save(paths["png"], "PNG", optimize=True)
    final.save(paths["jpg"], "JPEG", quality=JPG_QUALITY, optimize=True, progressive=True)
    final.save(paths["webp"], "WEBP", quality=WEBP_QUALITY, method=6)
    sizes = {k: p.stat().st_size for k, p in paths.items()}

    # 7. QA — thumbnail cap-height + worst-case contrast
    thumb_h = round(THUMB_W * TARGET_RATIO)
    thumb = final.resize((THUMB_W, thumb_h), Image.LANCZOS)
    thumb_cap_px = cap * (THUMB_W / KINDLE_W)
    contrast = zone_worst_contrast(bg_for_contrast, tbox, spec["text_color"], light_text)
    author_contrast = (zone_worst_contrast(bg_for_contrast, abox,
                       spec.get("author_color", spec["text_color"]), light_text)
                       if abox else None)
    ratio = KINDLE_H / KINDLE_W
    max_lines = int(spec.get("max_lines", 2))
    # The cap-height floor is genre-aware: a long literary Didone title legitimately
    # runs smaller than an impact sans, and very high contrast compensates for size.
    # Default 14; a spec may lower it ONLY with a recorded rationale (see spec comment).
    min_thumb_cap = float(spec.get("min_thumb_cap_px", MIN_THUMB_CAP_PX))

    gates = {
        "ratio_ok": abs(ratio - TARGET_RATIO) <= RATIO_TOL,
        "thumb_cap_ok": thumb_cap_px >= min_thumb_cap,
        "contrast_ok": contrast >= MIN_CONTRAST,
        "author_contrast_ok": (author_contrast is None or author_contrast >= MIN_CONTRAST),
        "lines_ok": len(title_lines) <= max_lines,
    }
    passed = all(gates.values())

    # 8. QA contact sheet (full + 160px thumbnail side by side)
    pad, label_h = 24, 28
    cs_w = KINDLE_W // 4 + THUMB_W + pad * 3
    cs_h = max(KINDLE_H // 4, thumb_h) + pad * 2 + label_h
    sheet = Image.new("RGB", (cs_w, cs_h), (244, 240, 234))
    sd = ImageDraw.Draw(sheet)
    full_small = final.resize((KINDLE_W // 4, KINDLE_H // 4), Image.LANCZOS)
    sheet.paste(full_small, (pad, pad + label_h))
    sheet.paste(thumb, (pad * 2 + KINDLE_W // 4, pad + label_h))
    try:
        lab = ImageFont.truetype(str(FONTS_DIR / "Marcellus-Regular.ttf"), 18)
    except Exception:
        lab = ImageFont.load_default()
    verdict = "PASS" if passed else "FAIL"
    sd.text((pad, pad), f"{slug}  full 1600x2560", font=lab, fill=(40, 33, 28))
    sd.text((pad * 2 + KINDLE_W // 4, pad), f"thumbnail 160px  [{verdict}]", font=lab,
            fill=(20, 110, 40) if passed else (150, 30, 20))
    sheet_path = out_dir / "qa-contact-sheet.png"
    sheet.save(sheet_path, "PNG")

    report = {
        "slug": slug,
        "title": spec["title"],
        "author": author,
        "fonts": {
            "title": {"key": spec["title_font"], "axes": t_axes,
                      "license": manifest[spec["title_font"]]["license"]},
            "author": ({"key": spec.get("author_font"), "axes": spec.get("author_axes"),
                        "license": manifest[spec["author_font"]]["license"]} if author else None),
        },
        "dimensions": {"width": KINDLE_W, "height": KINDLE_H,
                       "source": [src.width, src.height], "upscale_factor": round(upscale_factor, 3)},
        "ratio": round(ratio, 4),
        "source_ratio": round(src_ratio, 4),
        "title_font_px": size,
        "title_lines": title_lines,
        "thumbnail_cap_height_px": round(thumb_cap_px, 2),
        "text_contrast": round(contrast, 2),
        "author_contrast": (round(author_contrast, 2) if author_contrast is not None else None),
        "file_sizes_bytes": sizes,
        "file_sizes_kb": {k: round(v / 1024, 1) for k, v in sizes.items()},
        "gates": gates,
        "thresholds": {"ratio": TARGET_RATIO, "ratio_tol": RATIO_TOL,
                       "min_thumb_cap_px": min_thumb_cap, "min_contrast": MIN_CONTRAST,
                       "max_lines": max_lines},
        "result": verdict,
        "outputs": {k: str(p.relative_to(spec_dir.parent.parent.parent)) for k, p in paths.items()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")

    flag = "✓" if passed else "✗"
    print(f"[{flag} {verdict}] {slug}: title {size}px, thumb-cap {thumb_cap_px:.1f}px, "
          f"contrast {contrast:.1f}:1"
          + (f" (author {author_contrast:.1f}:1)" if author_contrast else "")
          + f", lines {len(title_lines)}/{max_lines} | "
          + "  ".join(f"{k}:{round(v/1024)}KB" for k, v in sizes.items()))
    if strict and not passed:
        failed = [k for k, v in gates.items() if not v]
        raise SystemExit(f"QA FAILED for {slug}: {failed}")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("spec", nargs="?", help="path to a cover-spec.yaml")
    ap.add_argument("--all", action="store_true", help="compose every covers/<slug>/cover-spec.yaml")
    ap.add_argument("--strict", action="store_true", help="exit non-zero if any QA gate fails")
    args = ap.parse_args()

    if args.all:
        root = HERE.parent.parent / "demo" / "books" / "covers"
        specs = sorted(root.glob("*/cover-spec.yaml"))
        if not specs:
            raise SystemExit(f"no specs under {root}")
        reports = [compose(p, strict=args.strict) for p in specs]
        n_pass = sum(r["result"] == "PASS" for r in reports)
        print(f"\n{n_pass}/{len(reports)} covers PASS")
        sys.exit(0 if n_pass == len(reports) else 1)
    elif args.spec:
        compose(Path(args.spec), strict=args.strict)
    else:
        ap.error("provide a spec path or --all")


if __name__ == "__main__":
    main()
