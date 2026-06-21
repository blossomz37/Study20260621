#!/usr/bin/env python3
"""
designmd-lint — a self-contained DESIGN.md validator.

Why this exists
---------------
The upstream reference linter (workspace/scratch/.../reference/rules/*.ts) is
TypeScript that imports modules we never cherry-picked (model/spec.js,
spec-config.js, parser/spec.js), so it cannot run as-is. This script
re-implements the *logic* of those rules in dependency-light Python (stdlib +
PyYAML) so DESIGN.md validation is reproducible.

It ALSO implements three proposed token extensions: `motion`
(references/motion-extension.md), `gradients` (references/gradient.md), and glass
(`blur` + `shadow`, references/glass.md). Each adds a typed token group plus
matching rules. Running this validator green on a demo DESIGN.md that uses the
extension is the step-3 proof that the extension closes the gap the un-extended
reference linter exposed.

Rules implemented (mirroring reference/rules + the motion/gradient/glass extensions):
  section-order       warning   canonical section order (alias-aware)
  missing-sections    info      spacing/rounded absent while colors present
  missing-primary     error     colors.primary must be defined
  missing-typography  warning   at least one typography token
  broken-ref          error     {a.b} references must resolve; unknown sub-tokens warn
  contrast-ratio      warning   opaque component bg/text pairs >= WCAG AA 4.5:1
                      info      gradient/translucent/blurred surface (C5: advisory,
                                checked vs the declared backdrop's darkest stop)
  unknown-key         warning   top-level key looks like a typo of a schema key
  motion-format       error     motion.*.duration/delay valid time; easing valid
  motion-orphaned     info      motion tokens referenced by nothing
  gradient-stops      error     gradient needs >=2 stops; positions valid (0-100%/0-1)
  gradient-type       warning   gradient type in {linear, radial, conic}
  gradient-broken-ref error     each stop color {ref} must resolve
  blur-format         error     blur.* must be valid dimensions (e.g. 20px)
  shadow-format       error     shadow.* offsets/blur/spread valid dims; color present
  shadow-broken-ref   error     shadow color {ref} must resolve

Exit code: 1 if any ERROR finding, else 0. Warnings/info never fail the build.

Usage:  python3 validate.py path/to/DESIGN.md [more.md ...]
"""

import re
import sys
import math

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required: pip install pyyaml (or use system python3)\n")
    sys.exit(2)

# --- spec constants (mirrors reference spec-config / model) ------------------

CANONICAL_ORDER = [
    "Overview", "Colors", "Typography", "Layout",
    "Elevation & Depth", "Shapes", "Components", "Do's and Don'ts",
]
SECTION_ALIASES = {
    "brand & style": "Overview",
    "layout & spacing": "Layout",
    "elevation": "Elevation & Depth",
    "dos and donts": "Do's and Don'ts",
    "do's and don'ts": "Do's and Don'ts",
}
# Base schema keys + the proposed `motion` / `gradients` / glass (`blur`,
# `shadow`) extension keys.
SCHEMA_KEYS = ["version", "name", "description", "colors", "typography",
               "rounded", "spacing", "components", "motion", "gradients",
               "blur", "shadow"]
# Base component sub-tokens + the `perspective`/`transition` (motion) props, the
# `backgroundImage` (gradients) prop, and the glass props `backdropBlur`,
# `borderColor`, `shadow`, and the `backdrop` contrast contract.
VALID_COMPONENT_SUB_TOKENS = ["backgroundColor", "textColor", "typography",
                              "rounded", "padding", "size", "height", "width",
                              "perspective", "transition", "backgroundImage",
                              "backdropBlur", "borderColor", "shadow", "backdrop"]
TOKEN_GROUPS = ["colors", "typography", "rounded", "spacing", "motion",
                "gradients", "blur", "shadow", "components"]
GRADIENT_TYPES = {"linear", "radial", "conic"}
DIMENSION_RE = re.compile(r"^\d+(\.\d+)?(px|rem|em)$")
SHADOW_DIM_RE = re.compile(r"^-?\d+(\.\d+)?(px|rem|em)$")  # allows negative offsets
WCAG_AA = 4.5
EASING_KEYWORDS = {"linear", "ease", "ease-in", "ease-out", "ease-in-out",
                   "step-start", "step-end"}
DURATION_RE = re.compile(r"^\d+(\.\d+)?(ms|s)$")
CUBIC_BEZIER_RE = re.compile(r"^cubic-bezier\(\s*[-\d.]+\s*,\s*[-\d.]+\s*,"
                             r"\s*[-\d.]+\s*,\s*[-\d.]+\s*\)$")
REF_RE = re.compile(r"^\{(.+)\}$")


# --- parsing -----------------------------------------------------------------

def parse(path):
    text = open(path, encoding="utf-8").read()
    fm = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = yaml.safe_load(text[3:end]) or {}
            body = text[end + 4:]
    sections = re.findall(r"^##\s+(.+?)\s*$", body, re.MULTILINE)
    return fm, sections


def resolve_alias(name):
    key = re.sub(r"[^\w&\s']", "", name).strip().lower()
    return SECTION_ALIASES.get(key, name.strip())


# --- token reference resolution ----------------------------------------------

def lookup(tree, dotted):
    node = tree
    for part in dotted.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None, False
    return node, True


def is_ref(v):
    return isinstance(v, str) and REF_RE.match(v.strip())


def ref_path(v):
    return REF_RE.match(v.strip()).group(1)


def resolve_value(v, tree, hops=8):
    """Follow {ref} chains to a concrete value. Returns (value, ok)."""
    while hops > 0 and is_ref(v):
        node, ok = lookup(tree, ref_path(v))
        if not ok:
            return None, False
        v = node
        hops -= 1
    return v, True


# --- color / WCAG ------------------------------------------------------------

def parse_color(s):
    if not isinstance(s, str):
        return None
    s = s.strip()
    m = re.match(r"^#([0-9a-fA-F]{3,8})$", s)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) >= 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        return None
    m = re.match(r"^rgba?\(([^)]+)\)$", s)
    if m:
        parts = [p.strip() for p in m.group(1).replace("/", ",").split(",")]
        try:
            return tuple(int(float(parts[i])) for i in range(3))
        except (ValueError, IndexError):
            return None
    return None  # named/oklch/etc — skip, like the reference resolveToColor


def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (_lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(c1, c2):
    l1, l2 = luminance(c1), luminance(c2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# --- gradient helpers --------------------------------------------------------

def valid_position(p):
    """A gradient stop position is a percentage (0–100%) or a 0–1 fraction."""
    s = str(p).strip()
    if s.endswith("%"):
        try:
            return 0.0 <= float(s[:-1]) <= 100.0
        except ValueError:
            return False
    try:
        return 0.0 <= float(s) <= 1.0
    except ValueError:
        return False


def valid_shadow_dim(v):
    """Shadow offsets/blur/spread: a dimension, or a bare/explicit zero."""
    s = str(v).strip()
    if s in ("0", "0px", "0rem", "0em"):
        return True
    return bool(SHADOW_DIM_RE.match(s))


# --- glass / translucency helpers --------------------------------------------

def alpha_of(s):
    """Return the alpha channel of a color string (1.0 if opaque or unknown)."""
    if not isinstance(s, str):
        return 1.0
    s = s.strip()
    m = re.match(r"^rgba?\(([^)]+)\)$", s)
    if m:
        parts = [p.strip() for p in m.group(1).replace("/", ",").split(",")]
        if len(parts) >= 4:
            try:
                return float(parts[3])
            except ValueError:
                return 1.0
        return 1.0
    m = re.match(r"^#([0-9a-fA-F]{4}|[0-9a-fA-F]{8})$", s)
    if m:
        h = m.group(1)
        if len(h) == 4:
            h = "".join(c * 2 for c in h)
        return int(h[6:8], 16) / 255.0
    return 1.0


def darkest_stop_color(fm, gradient_path):
    """Resolve a gradient token to the RGB of its darkest (lowest-luminance) stop."""
    node, ok = lookup(fm, gradient_path)
    if not ok or not isinstance(node, dict):
        return None
    darkest, best = None, 2.0
    for st in (node.get("stops") or []):
        if not isinstance(st, dict):
            continue
        cv, _ = resolve_value(st.get("color"), fm)
        c = parse_color(cv)
        if c is not None:
            lum = luminance(c)
            if lum < best:
                best, darkest = lum, c
    return darkest


# --- levenshtein (for unknown-key) -------------------------------------------

def levenshtein(a, b):
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# --- rules -------------------------------------------------------------------

def rule_section_order(fm, sections, F):
    known = [s for s in (resolve_alias(x) for x in sections) if s in CANONICAL_ORDER]
    idx = [CANONICAL_ORDER.index(s) for s in known]
    for i in range(len(idx) - 1):
        if idx[i] > idx[i + 1]:
            F("warning", "section-order", "",
              f"Section '{known[i]}' appears before '{known[i+1]}' (out of order). "
              f"Expected: {', '.join(CANONICAL_ORDER)}")
            break


def rule_missing_sections(fm, sections, F):
    if fm.get("colors"):
        for name, fb in (("spacing", "Layout spacing"), ("rounded", "Corner rounding")):
            if not fm.get(name):
                F("info", "missing-sections", name,
                  f"No '{name}' section. {fb} will fall back to agent defaults.")


def rule_missing_primary(fm, sections, F):
    colors = fm.get("colors") or {}
    if colors and "primary" not in colors:
        F("error", "missing-primary", "colors",
          "No 'primary' color defined. At least the primary palette is required.")


def rule_missing_typography(fm, sections, F):
    if not (fm.get("typography") or {}):
        F("warning", "missing-typography", "typography",
          "No typography tokens defined.")


def rule_broken_ref(fm, sections, F):
    comps = fm.get("components") or {}
    for cname, comp in comps.items():
        if not isinstance(comp, dict):
            continue
        for prop, val in comp.items():
            if prop not in VALID_COMPONENT_SUB_TOKENS:
                F("warning", "broken-ref", f"components.{cname}.{prop}",
                  f"'{prop}' is not a recognized component sub-token. "
                  f"Valid: {', '.join(VALID_COMPONENT_SUB_TOKENS)}.")
            if is_ref(val):
                _, ok = lookup(fm, ref_path(val))
                if not ok:
                    F("error", "broken-ref", f"components.{cname}",
                      f"Reference {{{ref_path(val)}}} does not resolve to any defined token.")


def rule_contrast(fm, sections, F):
    comps = fm.get("components") or {}
    for cname, comp in comps.items():
        if not isinstance(comp, dict):
            continue
        tx = comp.get("textColor")
        bg = comp.get("backgroundImage")
        # Advisory: text over a gradient backgroundImage can't be checked against a
        # single color — note it, don't fail (mirrors the glass C5 pattern).
        if bg and tx and comp.get("backgroundColor") is None:
            F("info", "contrast-ratio", f"components.{cname}",
              "textColor sits over a gradient backgroundImage; contrast is not "
              "evaluable against a single color — verify legibility against the "
              "gradient's darkest stop.")
            continue
        bg = comp.get("backgroundColor")
        if bg is None or tx is None:
            continue
        bgv, ok1 = resolve_value(bg, fm)
        txv, ok2 = resolve_value(tx, fm)
        if not (ok1 and ok2):
            continue
        # C5 fix: a translucent (alpha < 1) or backdrop-blurred surface is glass —
        # its WCAG contrast against the resolved fill is meaningless (it ignores the
        # backdrop). Don't emit a failing warning; downgrade to an advisory and,
        # when the component declares its backdrop, check text vs the backdrop's
        # darkest stop instead.
        is_glass = comp.get("backdropBlur") is not None or alpha_of(bgv) < 1.0
        txc = parse_color(txv)
        if is_glass:
            backdrop = comp.get("backdrop")
            if backdrop is not None and is_ref(backdrop) and txc is not None:
                dark = darkest_stop_color(fm, ref_path(backdrop))
                if dark is not None:
                    r = contrast(dark, txc)
                    verdict = "meets" if r >= WCAG_AA else "is below"
                    F("info", "contrast-ratio", f"components.{cname}",
                      f"translucent/blurred surface over backdrop {backdrop}: "
                      f"textColor vs the backdrop's darkest stop is {r:.2f}:1 "
                      f"({verdict} WCAG AA {WCAG_AA}:1; advisory — blur and "
                      f"translucency shift effective contrast).")
                    continue
            F("info", "contrast-ratio", f"components.{cname}",
              "translucent/blurred surface: contrast is not evaluable against the "
              "fill alone — declare a `backdrop` token or verify against the actual "
              "backdrop.")
            continue
        bgc = parse_color(bgv)
        if not bgc or not txc:
            continue
        r = contrast(bgc, txc)
        if r < WCAG_AA:
            F("warning", "contrast-ratio", f"components.{cname}",
              f"textColor on backgroundColor has contrast {r:.2f}:1, "
              f"below WCAG AA minimum {WCAG_AA}:1.")


def rule_unknown_key(fm, sections, F):
    known = set(SCHEMA_KEYS)
    for key in fm:
        if key in known:
            continue
        best, bestd = None, 99
        for k in SCHEMA_KEYS:
            d = levenshtein(key.lower(), k.lower())
            if d < bestd:
                best, bestd = k, d
        if bestd <= 2:
            F("warning", "unknown-key", key,
              f'Unknown key "{key}" — did you mean "{best}"?')


def rule_motion_format(fm, sections, F):
    motion = fm.get("motion") or {}
    for name, tok in motion.items():
        if not isinstance(tok, dict):
            F("error", "motion-format", f"motion.{name}",
              "Motion token must be a map with at least 'duration'.")
            continue
        for field in ("duration", "delay"):
            if field in tok and not DURATION_RE.match(str(tok[field])):
                F("error", "motion-format", f"motion.{name}.{field}",
                  f"'{tok[field]}' is not a valid duration (expected e.g. 450ms, 0.45s).")
        if "duration" not in tok:
            F("error", "motion-format", f"motion.{name}",
              "Motion token missing required 'duration'.")
        if "easing" in tok:
            e = str(tok["easing"])
            if e not in EASING_KEYWORDS and not CUBIC_BEZIER_RE.match(e):
                F("warning", "motion-format", f"motion.{name}.easing",
                  f"'{e}' is not a known easing keyword or cubic-bezier().")


def rule_motion_orphaned(fm, sections, F):
    motion = fm.get("motion") or {}
    if not motion:
        return
    used = set()
    for comp in (fm.get("components") or {}).values():
        if isinstance(comp, dict):
            for v in comp.values():
                if is_ref(v):
                    p = ref_path(v)
                    if p.startswith("motion."):
                        used.add(p.split(".", 1)[1])
    for name in motion:
        if name not in used:
            F("info", "motion-orphaned", f"motion.{name}",
              "Motion token is not referenced by any component.")


def rule_gradient(fm, sections, F):
    grads = fm.get("gradients") or {}
    for name, g in grads.items():
        if not isinstance(g, dict):
            F("error", "gradient-stops", f"gradients.{name}",
              "Gradient token must be a map with a 'stops' list.")
            continue
        gtype = str(g.get("type", "linear"))
        if gtype not in GRADIENT_TYPES:
            F("warning", "gradient-type", f"gradients.{name}.type",
              f"'{gtype}' is not a known gradient type "
              f"({', '.join(sorted(GRADIENT_TYPES))}).")
        stops = g.get("stops")
        if not isinstance(stops, list) or len(stops) < 2:
            F("error", "gradient-stops", f"gradients.{name}",
              "A gradient needs at least 2 stops.")
            continue
        for i, st in enumerate(stops):
            if not isinstance(st, dict):
                F("error", "gradient-stops", f"gradients.{name}.stops[{i}]",
                  "Each stop must be a map with 'color' (and optional 'position').")
                continue
            pos = st.get("position")
            if pos is not None and not valid_position(pos):
                F("error", "gradient-stops", f"gradients.{name}.stops[{i}].position",
                  f"'{pos}' is not a valid stop position (0–100% or a 0–1 fraction).")
            color = st.get("color")
            if color is None:
                F("error", "gradient-stops", f"gradients.{name}.stops[{i}]",
                  "Stop is missing required 'color'.")
            elif is_ref(color):
                _, ok = lookup(fm, ref_path(color))
                if not ok:
                    F("error", "gradient-broken-ref", f"gradients.{name}.stops[{i}]",
                      f"Reference {{{ref_path(color)}}} does not resolve to any "
                      f"defined token.")


def rule_blur(fm, sections, F):
    blur = fm.get("blur") or {}
    for name, val in blur.items():
        if not DIMENSION_RE.match(str(val)):
            F("error", "blur-format", f"blur.{name}",
              f"'{val}' is not a valid blur dimension (expected e.g. 20px).")


def rule_shadow(fm, sections, F):
    shadow = fm.get("shadow") or {}
    for name, sh in shadow.items():
        if not isinstance(sh, dict):
            F("error", "shadow-format", f"shadow.{name}",
              "Shadow token must be a map (offsetX/offsetY/blur/spread/color).")
            continue
        for field in ("offsetX", "offsetY", "blur", "spread"):
            if field in sh and not valid_shadow_dim(sh[field]):
                F("error", "shadow-format", f"shadow.{name}.{field}",
                  f"'{sh[field]}' is not a valid dimension (expected e.g. 8px, 0).")
        color = sh.get("color")
        if color is None:
            F("error", "shadow-format", f"shadow.{name}",
              "Shadow token is missing required 'color'.")
        elif is_ref(color):
            _, ok = lookup(fm, ref_path(color))
            if not ok:
                F("error", "shadow-broken-ref", f"shadow.{name}",
                  f"Reference {{{ref_path(color)}}} does not resolve to any "
                  f"defined token.")


RULES = [rule_section_order, rule_missing_sections, rule_missing_primary,
         rule_missing_typography, rule_broken_ref, rule_contrast,
         rule_unknown_key, rule_motion_format, rule_motion_orphaned,
         rule_gradient, rule_blur, rule_shadow]


# --- driver ------------------------------------------------------------------

def validate(path):
    findings = []

    def F(sev, rule, p, msg):
        findings.append((sev, rule, p, msg))

    fm, sections = parse(path)
    for r in RULES:
        r(fm, sections, F)
    return findings


def main(argv):
    paths = argv[1:]
    if not paths:
        sys.stderr.write("usage: validate.py DESIGN.md [...]\n")
        return 2
    order = {"error": 0, "warning": 1, "info": 2}
    total_err = 0
    for path in paths:
        findings = validate(path)
        findings.sort(key=lambda f: order.get(f[0], 9))
        errs = sum(1 for f in findings if f[0] == "error")
        warns = sum(1 for f in findings if f[0] == "warning")
        infos = sum(1 for f in findings if f[0] == "info")
        total_err += errs
        print(f"\n{path}")
        if not findings:
            print("  ✓ clean — no findings")
        for sev, rule, p, msg in findings:
            mark = {"error": "✗", "warning": "▲", "info": "·"}[sev]
            loc = f" [{p}]" if p else ""
            print(f"  {mark} {sev:7} {rule:18}{loc} {msg}")
        verdict = "FAIL" if errs else "PASS"
        print(f"  → {verdict}: {errs} error(s), {warns} warning(s), {infos} info")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
