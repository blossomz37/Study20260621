#!/usr/bin/env python3
"""
designmd-export — derive standard token targets from a DESIGN.md.

One normative source (DESIGN.md) → three exports that downstream tools consume:
  - tokens.css           CSS custom properties (primitives + resolved component vars)
  - tailwind.config.js   Tailwind theme.extend
  - tokens.json          DTCG (Design Token Community Group) format

Implements the proposed `motion` extension: motion tokens export to
transitionDuration/timingFunction/property (Tailwind), a DTCG `transition`
composite, and a `--motion-*` CSS var (gated by prefers-reduced-motion).

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
              "spacing": "space", "motion": "motion"}.get(group, group)
    return f"var(--{prefix}-{name})"


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
    L.append("")
    L.append("  /* components (resolved from token refs) */")
    for cname, comp in (fm.get("components") or {}).items():
        if not isinstance(comp, dict):
            continue
        for prop, val in comp.items():
            suffix = PROP_SUFFIX.get(prop, prop.lower())
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

    theme = {
        "colors": colors, "borderRadius": rounded, "spacing": spacing,
        "fontFamily": families, "fontSize": fontsize,
        "transitionDuration": dur, "transitionTimingFunction": tf,
        "transitionProperty": tp,
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
