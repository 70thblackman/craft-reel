#!/usr/bin/env python3
"""Cut narration takes tight: every pause shrinks to GAP, takes are levelled, then the
whole edit is sped up TEMPO with pitch preserved.

Reads narr/takes.json:
  [{"file": "narr/raw1.m4a", "start": 0.0, "end": null, "gain": 0}, ...]
Writes narr/voice_edit.wav and narr/edl.json (source spans -> edit offsets).
"""
import argparse
import json
import os
import re
import subprocess
import sys


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-3000:])
        sys.exit("ffmpeg failed")
    return r.stderr


def probe_duration(src):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def spans(src, start, end, gap):
    log = run(["ffmpeg", "-hide_banner", "-i", src, "-af", "silencedetect=n=-42dB:d=0.1", "-f", "null", "-"])
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    keep = gap / 2
    cuts = [(s + keep, e - keep) for s, e in zip(st, en) if e - s > gap + .02]
    out, t = [], start
    for a, b in sorted(cuts):
        if b <= start or a >= end:
            continue
        if a > t:
            out.append((t, min(a, end)))
        t = max(t, b)
    if t < end:
        out.append((t, end))
    return [(a, b) for a, b in out if b - a > .02]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--takes", default="narr/takes.json")
    ap.add_argument("--out", default="narr/voice_edit.wav")
    ap.add_argument("--edl", default="narr/edl.json")
    ap.add_argument("--tempo", type=float, default=1.07, help="1.0 = untouched pace")
    ap.add_argument("--gap", type=float, default=.08, help="seconds left of every pause")
    args = ap.parse_args()

    if not os.path.exists(args.takes):
        sys.exit(f"missing {args.takes} — copy assets/starter/narr/takes.example.json and edit it")
    takes = json.load(open(args.takes, encoding="utf-8"))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    segs, parts, labels, off = [], [], [], 0.0
    for k, t in enumerate(takes):
        src = t["file"]
        start = float(t.get("start") or 0)
        end = t.get("end")
        end = float(end) if end else probe_duration(src)
        gain = float(t.get("gain") or 0)
        for a, b in spans(src, start, end, args.gap):
            i = len(labels)
            d = b - a
            parts.append(
                f"[{k}:a]aformat=sample_rates=48000:channel_layouts=mono,"
                f"atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,volume={gain}dB,"
                f"afade=t=in:d=0.008,afade=t=out:st={max(0, d - .01):.3f}:d=0.01[s{i}]")
            labels.append(f"[s{i}]")
            segs.append([k, a, b, off])
            off += d

    if not segs:
        sys.exit("no speech spans found — check takes.json and the -42 dB gate")

    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1,atempo={args.tempo}[o]"
    ins = sum([["-i", t["file"]] for t in takes], [])
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *ins, "-filter_complex", fc,
         "-map", "[o]", "-ac", "1", "-ar", "48000", args.out])

    json.dump({"tempo": args.tempo, "gap": args.gap, "segs": segs,
               "takes": [t["file"] for t in takes]},
              open(args.edl, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(segs)} spans, {off:.2f}s before tempo -> {off / args.tempo:.2f}s after")
    print(f"wrote {args.out} and {args.edl}")


if __name__ == "__main__":
    main()
