#!/usr/bin/env python3
"""
fetch_fonts.py — fetch ONE OFL gap font that the curated library doesn't cover.

This build did NOT need it: the only anticipated gap (a techno/mono face for
"The Signal") resolved in favor of the in-library League Spartan, so the
fetch budget stayed unspent. Keep this for the rule in the plan: a font OUTSIDE
the 33-family library may be used ONLY when a genre genuinely needs one no library
face serves, and ONLY if it is OFL — then it comes in through here, the binary is
git-ignored, and `fonts.json` records family + URL + license for reproducibility.

It resolves the variable/static TTF from the Google Fonts css2 API (which serves
OFL faces), downloads it into fonts/, and prints the fonts.json entry to add.

Usage:
  python3 fetch_fonts.py "Family Name" [--weight 700] [--key family-key]
Example:
  python3 fetch_fonts.py "Space Mono" --key space-mono
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS_DIR = HERE / "fonts"
UA = "Mozilla/5.0 (compatible; cover-typography/1.0)"


def css2_url(family: str, weight: int) -> str:
    fam = family.replace(" ", "+")
    return f"https://fonts.googleapis.com/css2?family={fam}:wght@{weight}&display=swap"


def fetch(url: str, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read() if binary else r.read().decode("utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("family")
    ap.add_argument("--weight", type=int, default=700)
    ap.add_argument("--key", help="fonts.json key (default: kebab of family)")
    a = ap.parse_args()
    key = a.key or re.sub(r"[^a-z0-9]+", "-", a.family.lower()).strip("-")

    print(f"resolving {a.family} @ {a.weight} via Google Fonts css2 …")
    css = fetch(css2_url(a.family, a.weight))
    m = re.search(r"url\((https://[^)]+\.(?:ttf|woff2?))\)", css)
    if not m:
        sys.exit("no font file URL found — check the family name (must be on Google Fonts / OFL).")
    font_url = m.group(1)
    ext = font_url.rsplit(".", 1)[-1]
    out = FONTS_DIR / f"{key}.{ext}"
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"downloading {font_url}")
    out.write_bytes(fetch(font_url, binary=True))
    print(f"  saved {out} ({out.stat().st_size} bytes)")

    entry = {
        key: {
            "family": a.family,
            "file": out.name,
            "variable": ext == "ttf" and "[" in out.name,
            "axes": {"wght": [a.weight, a.weight]},
            "url": f"https://fonts.google.com/specimen/{a.family.replace(' ', '+')}",
            "license": "OFL-1.1",
        }
    }
    print("\nAdd this to fonts.json -> \"fonts\":")
    print(json.dumps(entry, indent=2))
    print("\nNote: Google Fonts are OFL; record the license above. The binary is "
          "git-ignored — fonts.json is the tracked record.")


if __name__ == "__main__":
    main()
