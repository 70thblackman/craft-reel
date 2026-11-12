#!/usr/bin/env python3
"""Technical + visual QA on the final file.

    python build/qa.py out/reel.mp4 --n 12

Checks the delivery specs (1080x1920, 30 fps, H.264/yuv420p/BT.709, AAC 48k
stereo, -14 LUFS, TP <= -1) and extracts N evenly spaced native-size frames
plus a contact sheet to build/qa/. Exits non-zero if a hard check fails.
"""
import argparse
import json
import os
import re
import subprocess
import sys

from contact_sheet import sheet

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                        "-show_format", "-show_streams", path],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-2000:])
        sys.exit("ffprobe failed")
    return json.loads(r.stdout)


def loudness(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af",
                        "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    return json.loads(m.group(0)) if m else {}


def fps_of(stream):
    try:
        num, den = stream["r_frame_rate"].split("/")
        return float(num) / float(den)
    except Exception:
        return 0.0


def extract(path, dur, n, outdir):
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        if f.startswith("qa_") and f.endswith(".jpg"):
            os.remove(os.path.join(outdir, f))
    made = []
    for i in range(n):
        t = dur * (i + .5) / n
        name = os.path.join(outdir, f"qa_{i:02d}_{t:07.2f}.jpg")
        r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                            "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", "-q:v", "2", name],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0 and os.path.exists(name):
            made.append(name)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--cues", default="build/cues.json")
    ap.add_argument("--outdir", default="build/qa")
    ap.add_argument("--w", type=int, default=1080)
    ap.add_argument("--h", type=int, default=1920)
    ap.add_argument("--min-mb", type=float, default=1.0)
    args = ap.parse_args()
    os.chdir(ROOT)
    if not os.path.exists(args.video):
        sys.exit(f"missing {args.video}")

    info = probe(args.video)
    fmt = info["format"]
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        sys.exit("no video stream")
    dur = float(fmt["duration"])
    fps = fps_of(v)
    lufs = loudness(args.video)
    size_mb = os.path.getsize(args.video) / 1e6
    expected = None
    if os.path.exists(args.cues):
        expected = float(json.load(open(args.cues, encoding="utf-8"))["duration"])

    rows = []

    def check(name, ok, detail, hard=True):
        rows.append((name, bool(ok), detail, hard))

    check("resolution", v["width"] == args.w and v["height"] == args.h, f"{v['width']}x{v['height']}")
    check("frame rate", abs(fps - 30) < .05, f"{fps:.3f} fps")
    check("codec", v.get("codec_name") == "h264", str(v.get("codec_name")))
    check("pixel format", v.get("pix_fmt") == "yuv420p", str(v.get("pix_fmt")))
    check("color primaries", v.get("color_primaries") == "bt709", str(v.get("color_primaries")), hard=False)
    check("color transfer", v.get("color_transfer") == "bt709", str(v.get("color_transfer")), hard=False)
    if a:
        check("audio codec", a.get("codec_name") == "aac", str(a.get("codec_name")))
        check("audio rate", int(a.get("sample_rate", 0)) == 48000, f"{a.get('sample_rate')} Hz")
        check("audio channels", int(a.get("channels", 0)) == 2, f"{a.get('channels')} ch")
        check("audio bitrate", int(a.get("bit_rate", 0)) >= 128000, f"{int(a.get('bit_rate', 0)) // 1000} kb/s")
    else:
        check("audio stream", False, "missing")
    if lufs:
        i = float(lufs.get("input_i", -99))
        tp = float(lufs.get("input_tp", 0))
        check("loudness", abs(i + 14) <= 1.5, f"{i:.1f} LUFS")
        check("true peak", tp <= -0.8, f"{tp:.1f} dBTP")
    else:
        check("loudness", False, "could not measure")
    if expected:
        check("duration", abs(dur - expected) <= .35, f"{dur:.2f}s / cues {expected:.2f}s")
    else:
        check("duration", True, f"{dur:.2f}s (no cues)")
    check("file size", size_mb >= max(args.min_mb, dur * .04), f"{size_mb:.1f} MB")

    made = extract(args.video, dur, args.n, args.outdir)
    if made:
        sh = os.path.join(args.outdir, "sheet.jpg")
        sheet(args.outdir, sh, 4, 300, True, f"{os.path.basename(args.video)}  {dur:.1f}s  {lufs.get('input_i', '?')} LUFS")
        print("contact sheet:", sh)

    print()
    print(f"{'check':20s} {'result':7s} value")
    for name, ok, detail, hard in rows:
        tag = "PASS" if ok else ("FAIL" if hard else "warn")
        print(f"{name:20s} {tag:7s} {detail}")
    hard_fail = any(not ok and hard for _, ok, _, hard in rows)
    report = {"file": args.video, "duration": dur, "fps": fps, "size_mb": size_mb,
              "loudness": lufs, "checks": [{"name": n, "ok": o, "detail": d, "hard": h}
                                            for n, o, d, h in rows]}
    with open(os.path.join(args.outdir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print("\n" + ("QA PASSED" if not hard_fail else "QA FAILED"))
    sys.exit(1 if hard_fail else 0)


if __name__ == "__main__":
    main()
