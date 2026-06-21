#!/usr/bin/env python3
"""
designmd-export — derive standard token targets from a DESIGN.md.

One normative source (DESIGN.md) → three exports that downstream tools consume:
  - tokens.css           CSS custom properties (primitives + resolved component vars)
  - tailwind.config.js   Tailwind theme.extend
  - tokens.json          DTCG (Design Token Community Group) format

Implements two proposed extensions:
  - `motion`    -> transitionDuration/timingFunction/property (Tailwind), a DTCG
                  `transition` composite, and a `--motion-*` CSS var (gated by
                  prefers-reduced-motion).
  - `gradients` -> a `--gradient-*` CSS var (built into a CSS gradient string),
                  Tailwind `backgroundImage`, and a DTCG `gradient` composite
                  (stops in `$value`, orientation in `$extensions.designmd`).
  - glass       -> `--blur-*` and `--shadow-*` CSS vars; component `--*-backdrop`
                  (a `blur(...)` value) and `--*-shadow`; Tailwind `backdropBlur` +
                  `boxShadow`; DTCG native `shadow` composite and a custom `blur`
                  group ($extensions-documented, since DTCG has no blur type).

Usage:  python3 export.py demo/book-flip/DESIGN.md --out demo/book-flip/dist
"""

import argparse
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required\n"); sys.exit(2)

REF_RE = re.compile(r"^\{(.+)\}$")
EASING_BEZIER = {
    "linear": [0.0, 0.0, 1.0, 1.0],
    "ease": [0.25, 0.1, 0.25, 1.0],
    "ease-in": [0.42, 0.0, 1.0, 1.0],
    "ease-out": [0.0, 0.0, 0.58, 1.0],
    "ease-in-out": [0.42, 0.0, 0.58, 1.0],
}
# component property name -> short CSS-var suffix
PROP_SUFFIX = {
    "backgroundColor": "bg", "textColor": "fg", "typography": "font",
    "rounded": "radius", "padding": "pad", "perspective": "perspective",
    "transition": "transition", "size": "size", "height": "height", "width": "width",
    "backgroundImage": "bg-image", "backdropBlur": "backdrop", "borderColor": "border",
    "shadow": "shadow", "backdrop": "backdrop-image",
}


def parse_fm(path):
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    return yaml.safe_load(text[3:end]) or {}


def is_ref(v):
    return isinstance(v, str) and REF_RE.match(v.strip())


def ref_to_var(v):
    """'{colors.primary}' -> 'var(--color-primary)', etc."""
    path = REF_RE.match(v.strip()).group(1)
    group, _, name = path.partition(".")
    prefix = {"colors": "color", "typography": "type", "rounded": "rounded",
              "spacing": "space", "motion": "motion", "gradients": "gradient",
              "blur": "blur", "shadow": "shadow"}.get(group, group)
    return f"var(--{prefix}-{name})"


def shadow_dim(v):
    """Shadow offset/blur/spread -> CSS length. Bare 0 stays '0'; bare N -> 'Npx'."""
    s = str(v).strip()
    if s in ("0", "0px", "0rem", "0em"):
        return "0"
    if re.match(r"^-?\d+(\.\d+)?$", s):
        return s + "px"
    return s


def _dtcg_dim(v):
    """DTCG dimension string: a bare number gets 'px'; '0' becomes '0px'."""
    s = str(v).strip()
    if re.match(r"^-?\d+(\.\d+)?$", s):
        return s + "px"
    return s


def shadow_css(sh):
    """A shadow token map -> a CSS box-shadow string. Color ref -> var()."""
    color = sh.get("color", "#000")
    col = ref_to_var(color) if is_ref(color) else color
    return (f"{shadow_dim(sh.get('offsetX', 0))} {shadow_dim(sh.get('offsetY', 0))} "
            f"{shadow_dim(sh.get('blur', 0))} {shadow_dim(sh.get('spread', 0))} {col}")


def css_position(pos):
    """Stop position -> a CSS-legal length/percentage.

    The validator accepts a percentage ('0%'..'100%') or a 0–1 fraction; CSS
    gradients require a percentage or length, so a bare fraction is scaled.
    """
    s = str(pos).strip()
    if s.endswith("%") or re.search(r"(px|em|rem)$", s):
        return s
    try:
        f = float(s)
    except ValueError:
        return s
    return f"{f * 100:g}%" if 0.0 <= f <= 1.0 else f"{f:g}%"


def gradient_css(g):
    """A gradient token -> a CSS gradient string. Stop color refs become var()."""
    gtype = g.get("type", "linear")
    parts = []
    for st in (g.get("stops") or []):
        color = st.get("color", "")
        col = ref_to_var(color) if is_ref(color) else color
        pos = st.get("position")
        parts.append(f"{col} {css_position(pos)}" if pos is not None else str(col))
    stops = ", ".join(parts)
    orient = g.get("angle")
    if gtype == "radial":
        return f"radial-gradient({orient or 'circle'}, {stops})"
    if gtype == "conic":
        return f"conic-gradient({orient or 'from 0deg'}, {stops})"
    return f"linear-gradient({orient or '180deg'}, {stops})"


def font_shorthand(t):
    """typography token -> CSS `font` shorthand (letterSpacing handled separately)."""
    weight = t.get("fontWeight", 400)
    size = t.get("fontSize", "16px")
    lh = t.get("lineHeight", "1.4")
    fam = t.get("fontFamily", "sans-serif")
    return f"{weight} {size}/{lh} {fam}"


# --- CSS export --------------------------------------------------------------

def export_css(fm):
    L = [":root {"]
    for name, val in (fm.get("colors") or {}).items():
        L.append(f"  --color-{name}: {val};")
    for name, t in (fm.get("typography") or {}).items():
        L.append(f"  --type-{name}: {font_shorthand(t)};")
        if "letterSpacing" in t:
            L.append(f"  --type-{name}-tracking: {t['letterSpacing']};")
    for name, val in (fm.get("rounded") or {}).items():
        L.append(f"  --rounded-{name}: {val};")
    for name, val in (fm.get("spacing") or {}).items():
        var = "cover-aspect" if name == "cover-aspect" else name
        L.append(f"  --space-{var}: {val};")
    for name, m in (fm.get("motion") or {}).items():
        prop = m.get("property", "all")
        L.append(f"  --motion-{name}: {prop} {m.get('duration','0ms')} {m.get('easing','ease')};")
    for name, g in (fm.get("gradients") or {}).items():
        L.append(f"  --gradient-{name}: {gradient_css(g)};")
    for name, val in (fm.get("blur") or {}).items():
        L.append(f"  --blur-{name}: {val};")
    for name, sh in (fm.get("shadow") or {}).items():
        L.append(f"  --shadow-{name}: {shadow_css(sh)};")
    L.append("")
    L.append("  /* components (resolved from token refs) */")
    for cname, comp in (fm.get("components") or {}).items():
        if not isinstance(comp, dict):
            continue
        for prop, val in comp.items():
            suffix = PROP_SUFFIX.get(prop, prop.lower())
            if prop == "backdropBlur":
                # wrap the blur dimension in blur(); apply to backdrop-filter AND
                # -webkit-backdrop-filter at the call site (Safari).
                dim = ref_to_var(val) if is_ref(val) else val
                css = f"blur({dim})"
            elif prop == "shadow":
                css = ref_to_var(val) if is_ref(val) else shadow_css(val)
            else:
                css = ref_to_var(val) if is_ref(val) else val
            L.append(f"  --{cname}-{suffix}: {css};")
    L.append("}")
    L.append("")
    L.append("/* honor the motion token contract: reduced motion collapses duration */")
    L.append("@media (prefers-reduced-motion: reduce) {")
    L.append("  :root {")
    for name, m in (fm.get("motion") or {}).items():
        prop = m.get("property", "all")
        L.append(f"    --motion-{name}: {prop} 0ms linear;")
    L.append("  }")
    L.append("}")
    return "\n".join(L) + "\n"


# --- Tailwind export ---------------------------------------------------------

def export_tailwind(fm):
    colors = fm.get("colors") or {}
    rounded = fm.get("rounded") or {}
    spacing = {k: v for k, v in (fm.get("spacing") or {}).items() if k != "cover-aspect"}
    typ = fm.get("typography") or {}
    motion = fm.get("motion") or {}

    families, fontsize = {}, {}
    for name, t in typ.items():
        fam = t.get("fontFamily")
        if fam:
            families[fam.lower().replace(" ", "-")] = [fam, "serif" if "serif" in fam.lower() else "sans-serif"]
        opts = {"lineHeight": str(t.get("lineHeight", "")), "fontWeight": str(t.get("fontWeight", ""))}
        if t.get("letterSpacing"):
            opts["letterSpacing"] = t["letterSpacing"]
        fontsize[name] = [t.get("fontSize", "16px"), {k: v for k, v in opts.items() if v}]

    dur = {n: m.get("duration", "0ms") for n, m in motion.items()}
    tf = {n: m.get("easing", "ease") for n, m in motion.items()}
    tp = {n: m["property"] for n, m in motion.items() if m.get("property")}
    bgimg = {n: gradient_css(g) for n, g in (fm.get("gradients") or {}).items()}
    backdrop_blur = {n: str(v) for n, v in (fm.get("blur") or {}).items()}
    box_shadow = {n: shadow_css(sh) for n, sh in (fm.get("shadow") or {}).items()}

    theme = {
        "colors": colors, "borderRadius": rounded, "spacing": spacing,
        "fontFamily": families, "fontSize": fontsize,
        "transitionDuration": dur, "transitionTimingFunction": tf,
        "transitionProperty": tp, "backgroundImage": bgimg,
        "backdropBlur": backdrop_blur, "boxShadow": box_shadow,
    }
    body = json.dumps({"theme": {"extend": theme}}, indent=2)
    return ("// Generated from DESIGN.md by tools/designmd-export — do not edit by hand.\n"
            "/** @type {import('tailwindcss').Config} */\n"
            f"module.exports = {body};\n")


# --- DTCG export -------------------------------------------------------------

def export_dtcg(fm):
    out = {}
    if fm.get("name"):
        out["$description"] = fm.get("description", fm["name"])
    if fm.get("colors"):
        out["colors"] = {n: {"$type": "color", "$value": v} for n, v in fm["colors"].items()}
    if fm.get("typography"):
        out["typography"] = {}
        for n, t in fm["typography"].items():
            v = {"fontFamily": t.get("fontFamily"), "fontSize": t.get("fontSize"),
                 "fontWeight": int(t["fontWeight"]) if str(t.get("fontWeight", "")).isdigit() else t.get("fontWeight"),
                 "lineHeight": t.get("lineHeight")}
            if t.get("letterSpacing"):
                v["letterSpacing"] = t["letterSpacing"]
            out["typography"][n] = {"$type": "typography", "$value": {k: x for k, x in v.items() if x is not None}}
    if fm.get("rounded"):
        out["rounded"] = {n: {"$type": "dimension", "$value": str(v)} for n, v in fm["rounded"].items()}
    if fm.get("spacing"):
        out["spacing"] = {}
        for n, v in fm["spacing"].items():
            entry = {"$value": str(v)}
            if re.match(r"^\d", str(v)) and re.search(r"(px|rem|em)$", str(v)):
                entry["$type"] = "dimension"
            out["spacing"][n] = entry
    if fm.get("motion"):
        out["motion"] = {}
        for n, m in fm["motion"].items():
            bez = EASING_BEZIER.get(m.get("easing", "ease"), EASING_BEZIER["ease"])
            out["motion"][n] = {"$type": "transition", "$value": {
                "duration": {"$type": "duration", "$value": m.get("duration", "0ms")},
                "timingFunction": {"$type": "cubicBezier", "$value": bez},
                "delay": {"$type": "duration", "$value": m.get("delay", "0ms")},
            }}
    if fm.get("gradients"):
        # DTCG defines a `gradient` composite whose $value is an array of color
        # stops {color, position}; it does NOT standardize linear/radial or angle,
        # so orientation goes in $extensions (the DTCG-blessed escape hatch).
        out["gradients"] = {}
        for n, g in fm["gradients"].items():
            stops = []
            for st in (g.get("stops") or []):
                stop = {"color": st.get("color")}
                if st.get("position") is not None:
                    stop["position"] = st["position"]
                stops.append(stop)
            ext = {"type": g.get("type", "linear")}
            if g.get("angle") is not None:
                ext["angle"] = g["angle"]
            out["gradients"][n] = {
                "$type": "gradient",
                "$value": stops,
                "$extensions": {"designmd": ext},
            }
    if fm.get("shadow"):
        # DTCG has a native `shadow` composite: {color, offsetX, offsetY, blur, spread}.
        out["shadow"] = {}
        for n, sh in fm["shadow"].items():
            out["shadow"][n] = {"$type": "shadow", "$value": {
                "color": sh.get("color"),
                "offsetX": _dtcg_dim(sh.get("offsetX", 0)),
                "offsetY": _dtcg_dim(sh.get("offsetY", 0)),
                "blur": _dtcg_dim(sh.get("blur", 0)),
                "spread": _dtcg_dim(sh.get("spread", 0)),
            }}
    if fm.get("blur"):
        # INVENTION POINT: DTCG has no backdrop-filter / blur type. We carry blur as
        # a minimal dimension group and flag the absence in $extensions so a
        # standard consumer is told this is a non-standard local extension.
        out["blur"] = {
            "$description": ("Non-standard local extension: DTCG defines no "
                             "backdrop-filter/blur type. Values are dimensions "
                             "consumed as `backdrop-filter: blur(<value>)`."),
        }
        for n, v in fm["blur"].items():
            out["blur"][n] = {
                "$type": "dimension", "$value": str(v),
                "$extensions": {"designmd": {"role": "backdrop-blur"}},
            }
    if fm.get("components"):
        out["components"] = {}
        for cn, comp in fm["components"].items():
            if isinstance(comp, dict):
                out["components"][cn] = {p: {"$value": v} for p, v in comp.items()}
    return json.dumps(out, indent=2) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv[1:])
    fm = parse_fm(a.design)
    os.makedirs(a.out, exist_ok=True)
    files = {
        "tokens.css": export_css(fm),
        "tailwind.config.js": export_tailwind(fm),
        "tokens.json": export_dtcg(fm),
    }
    for name, content in files.items():
        path = os.path.join(a.out, name)
        open(path, "w", encoding="utf-8").write(content)
        print(f"  wrote {path} ({len(content)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
