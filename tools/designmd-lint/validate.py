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

It ALSO implements the proposed `motion` token extension
(docs/design-md-motion-extension-proposal.md): a `motion` token group, the
`perspective`/`transition` component sub-tokens, and four motion rules. Running
this validator green on demo/book-flip/DESIGN.md is the step-3 proof that the
extension closes the gap the un-extended reference linter exposed.

Rules implemented (mirroring reference/rules + the motion extension):
  section-order       warning   canonical section order (alias-aware)
  missing-sections    info      spacing/rounded absent while colors present
  missing-primary     error     colors.primary must be defined
  missing-typography  warning   at least one typography token
  broken-ref          error     {a.b} references must resolve; unknown sub-tokens warn
  contrast-ratio      warning   component bg/text pairs >= WCAG AA 4.5:1
  unknown-key         warning   top-level key looks like a typo of a schema key
  motion-format       error     motion.*.duration/delay valid time; easing valid
  motion-orphaned     info      motion tokens referenced by nothing

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
# Base schema keys + the proposed `motion` extension key.
SCHEMA_KEYS = ["version", "name", "description", "colors", "typography",
               "rounded", "spacing", "components", "motion"]
# Base component sub-tokens + the proposed `perspective`/`transition` props.
VALID_COMPONENT_SUB_TOKENS = ["backgroundColor", "textColor", "typography",
                              "rounded", "padding", "size", "height", "width",
                              "perspective", "transition"]
TOKEN_GROUPS = ["colors", "typography", "rounded", "spacing", "motion", "components"]
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
        bg, tx = comp.get("backgroundColor"), comp.get("textColor")
        if bg is None or tx is None:
            continue
        bgv, ok1 = resolve_value(bg, fm)
        txv, ok2 = resolve_value(tx, fm)
        if not (ok1 and ok2):
            continue
        bgc, txc = parse_color(bgv), parse_color(txv)
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


RULES = [rule_section_order, rule_missing_sections, rule_missing_primary,
         rule_missing_typography, rule_broken_ref, rule_contrast,
         rule_unknown_key, rule_motion_format, rule_motion_orphaned]


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
