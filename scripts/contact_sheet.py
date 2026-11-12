#!/usr/bin/env python3
"""Contact sheet from a folder of frames.

    python build/contact_sheet.py build/shots build/sheet.jpg 5

Sorts by the last number in the filename, lays the stills out in a dark grid
and labels each cell. Use it every few seconds of film: if a cell is boring,
the scene is boring.
"""
import argparse
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

BG = (11, 27, 51)
FG = (185, 220, 255)
PAD = 14
LABEL_H = 30


def sort_key(name):
    nums = re.findall(r"\d+(?:\.\d+)?", os.path.splitext(name)[0])
    return (float(nums[-1]) if nums else 0.0, name)


def font(size):
    for p in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def sheet(folder, out, cols=5, width=270, labels=True, title=None):
    files = sorted((f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))), key=sort_key)
    if not files:
        sys.exit(f"no images in {folder}")
    cols = max(1, min(cols, len(files)))
    rows = (len(files) + cols - 1) // cols
    first = Image.open(os.path.join(folder, files[0]))
    aspect = first.height / first.width
    cell_w, cell_h = width, int(round(width * aspect))
    lab = LABEL_H if labels else 0
    top = 56 if title else PAD
    W = PAD + cols * (cell_w + PAD)
    H = top + rows * (cell_h + lab + PAD)
    canvas = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(canvas)
    f_small, f_title = font(17), font(26)
    if title:
        dr.text((PAD, 16), title, fill=FG, font=f_title)
    for i, name in enumerate(files):
        im = Image.open(os.path.join(folder, name)).convert("RGB")
        im = im.resize((cell_w, cell_h), Image.LANCZOS)
        x = PAD + (i % cols) * (cell_w + PAD)
        y = top + (i // cols) * (cell_h + lab + PAD)
        canvas.paste(im, (x, y))
        if labels:
            dr.text((x + 2, y + cell_h + 6), os.path.splitext(name)[0], fill=FG, font=f_small)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    canvas.save(out, quality=88)
    print(f"{len(files)} stills -> {out}  {W}x{H}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("out", nargs="?", default="build/sheet.jpg")
    ap.add_argument("cols", nargs="?", type=int, default=5)
    ap.add_argument("--width", type=int, default=270)
    ap.add_argument("--title")
    ap.add_argument("--no-labels", action="store_true")
    args = ap.parse_args()
    sheet(args.folder, args.out, args.cols, args.width, not args.no_labels, args.title)


if __name__ == "__main__":
    main()
