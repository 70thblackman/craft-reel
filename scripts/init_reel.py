#!/usr/bin/env python3
"""Scaffold a new reel project from the craft-reel starter.

    python init_reel.py <project-dir> [--force]

Copies the starter (engine, art, demo scenes, CSS backgrounds) and the
pipeline scripts into <project-dir>/build, then writes package.json.
"""
import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STARTER = os.path.join(ROOT, "assets", "starter")
SCRIPTS = HERE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--force", action="store_true", help="copy into a non-empty folder")
    args = ap.parse_args()
    target = os.path.abspath(args.target)
    if os.path.abspath(target) in (os.path.abspath(ROOT),):
        sys.exit("refusing to scaffold over the skill folder")
    if os.path.isdir(target) and os.listdir(target) and not args.force:
        sys.exit(f"target is not empty: {target} (use --force)")

    shutil.copytree(STARTER, target, dirs_exist_ok=True)
    os.makedirs(os.path.join(target, "build"), exist_ok=True)
    copied = 0
    for name in os.listdir(SCRIPTS):
        if not name.endswith((".py", ".mjs")) or name == "init_reel.py":
            continue
        shutil.copy2(os.path.join(SCRIPTS, name), os.path.join(target, "build", name))
        copied += 1

    pkg = {
        "name": os.path.basename(target).lower().replace(" ", "-"),
        "private": True,
        "type": "commonjs",
        "scripts": {
            "sfx": "node build/render.mjs sfx",
            "render": "node build/render.mjs",
            "cover": "node build/render.mjs cover",
        },
        "dependencies": {"puppeteer-core": "^24.0.0"},
    }
    with open(os.path.join(target, "package.json"), "w", encoding="utf-8") as f:
        json.dump(pkg, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"scaffolded {target}")
    print(f"  starter: engine.js, art.js, art2.js, scenes.js, words.js, css, CSS backgrounds, cover.html")
    print(f"  build/: {copied} pipeline scripts")
    print("next:")
    print(f"  cd \"{target}\" && npm i")
    print("  edit js/scenes.js + window.FILM_DURATION in index.html")
    print("  node build/render.mjs shot 0 2 5 8    # quick look")
    print("  python build/contact_sheet.py build/shots build/sheet.jpg")


if __name__ == "__main__":
    main()
