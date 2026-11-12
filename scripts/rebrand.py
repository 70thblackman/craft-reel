#!/usr/bin/env python3
"""Re-map the starter's blue accent family to a new brand colour.

    python build/rebrand.py <project-dir> "#ff5a1f"
    python build/rebrand.py <project-dir> "#7c3aed" --dry

Rewrites hex tokens and rgba() triplets in css/js/html files, leaving the
navy/paper neutrals and the gold signal colour alone. The five-stop family is
derived from one colour so extrusion, links and tints stay coherent.
"""
import argparse
import os
import re
import sys


def parse_hex(s):
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", s):
        sys.exit(f"bad hex colour: {s}")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in c)


def mix(c, target, p):
    return tuple(c[i] + (target[i] - c[i]) * p for i in range(3))


def family(hex_color):
    c = parse_hex(hex_color)
    return {
        "brand": to_hex(c),
        "brand-2": to_hex(mix(c, (0, 0, 0), .16)),
        "brand-3": to_hex(mix(c, (0, 0, 0), .34)),
        "brand-deep": to_hex(mix(c, (0, 0, 0), .55)),
        "sky": to_hex(mix(c, (255, 255, 255), .90)),
        "sky-2": to_hex(mix(c, (255, 255, 255), .62)),
    }


OLD = {
    "#008efa": "brand", "#007dfa": "brand", "#0a6fd8": "brand-2",
    "#0753a8": "brand-3", "#06386f": "brand-deep",
    "#e6f3ff": "sky", "#b9dcff": "sky-2",
}
OLD_RGB = {
    (0, 142, 250): "brand", (0, 125, 250): "brand",
    (10, 111, 216): "brand-2", (7, 83, 168): "brand-3", (6, 56, 111): "brand-deep",
    (230, 243, 255): "sky", (185, 220, 255): "sky-2",
}
SKIP_DIRS = {"node_modules", "build", "out", "samples", "fonts", "img", ".git", "shots", "frames"}


def rewrite(text, fam):
    hits = 0

    def hex_sub(m):
        nonlocal hits
        tok = m.group(0).lower()
        if tok in OLD:
            hits += 1
            return fam[OLD[tok]]
        return m.group(0)

    text = re.sub(r"#[0-9a-fA-F]{6}\b", hex_sub, text)

    def rgb_sub(m):
        nonlocal hits
        triple = tuple(int(x) for x in m.groups())
        if triple in OLD_RGB:
            hits += 1
            c = parse_hex(fam[OLD_RGB[triple]])
            return f"{c[0]},{c[1]},{c[2]}"
        return m.group(0)

    text = re.sub(r"\b(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\b", rgb_sub, text)
    return text, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("color")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    root = os.path.abspath(args.project)
    if not os.path.isdir(root):
        sys.exit(f"not a folder: {root}")
    fam = family(args.color)
    print("accent family:")
    for k, v in fam.items():
        print(f"  {k:12s} {v}")
    lum = sum(parse_hex(fam["brand"])) / 765
    if lum > .72:
        print("note: this accent is light — use navy text on brand fills, keep white ring on light type")

    changed, total = [], 0
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
        for fn in files:
            if not fn.lower().endswith((".css", ".js", ".html", ".mjs")):
                continue
            p = os.path.join(dirpath, fn)
            if os.path.getsize(p) > 800_000:
                continue
            try:
                src = open(p, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            out, hits = rewrite(src, fam)
            if hits:
                changed.append((os.path.relpath(p, root), hits))
                total += hits
                if not args.dry:
                    open(p, "w", encoding="utf-8").write(out)
    for name, hits in changed:
        print(f"  {hits:4d}  {name}")
    print(f"{'would change' if args.dry else 'changed'} {total} tokens in {len(changed)} files")
    if not changed:
        print("nothing matched — already rebranded, or the palette was edited by hand")


if __name__ == "__main__":
    main()
