#!/usr/bin/env python3
"""Mix voice + score + SFX and encode the rendered frames.

    python build/mix.py                      # duration from build/cues.json
    python build/mix.py --duration 86.33 --lead .10
    python build/mix.py --no-finish --crf 20

Inputs: narr/voice_edit.wav, build/music.wav, build/sfx.wav, build/frames/f_*.jpg
Output: out/reel.mp4 — 1080x1920, 30 fps, BT.709, -14 LUFS, AAC 256k.
The voice is cleaned, the score is sidechained under it, both peak-normalized
tracks are summed, and loudnorm runs twice (measure, then linear apply).
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30


def ff(args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-y", *args],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-4000:])
        sys.exit("ffmpeg failed")
    return r.stderr


def ffprobe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                        "-show_format", "-show_streams", path],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-2000:])
        sys.exit(f"ffprobe failed: {path}")
    return json.loads(r.stdout)


def film_duration(cues_path, frames_dir, cli):
    if cli:
        return float(cli)
    if os.path.exists(cues_path):
        return float(json.load(open(cues_path, encoding="utf-8"))["duration"])
    n = len([f for f in os.listdir(frames_dir) if f.startswith("f_") and f.endswith(".jpg")])
    if n:
        return n / FPS
    sys.exit("cannot determine duration: render frames or pass --duration")


def lead_time(cli):
    if cli is not None:
        return float(cli)
    if os.path.exists("build/film_words.json"):
        words = json.load(open("build/film_words.json", encoding="utf-8"))
        if words:
            return float(words[0][1])
    return .10


def measure_loudness(path):
    st = ff(["-i", path, "-af", "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json",
             "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", st, re.S)
    if not m:
        sys.exit("could not read loudnorm measurements")
    return json.loads(m.group(0))


def main():
    os.chdir(ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float)
    ap.add_argument("--lead", type=float, help="film seconds of the first voice sample")
    ap.add_argument("--voice", default="narr/voice_edit.wav")
    ap.add_argument("--music", default="build/music.wav")
    ap.add_argument("--sfx", default="build/sfx.wav")
    ap.add_argument("--frames", default="build/frames")
    ap.add_argument("--cues", default="build/cues.json")
    ap.add_argument("--out", default="out/reel.mp4")
    ap.add_argument("--music-gain", type=float, default=.58)
    ap.add_argument("--sfx-gain", type=float, default=.8)
    ap.add_argument("--lead-in", type=float, default=0.0,
                    help="extra delay before the first voice sample")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--no-finish", action="store_true", help="skip grain / chroma / vignette")
    args = ap.parse_args()

    for p in (args.voice, args.music, args.sfx):
        if not os.path.exists(p):
            sys.exit(f"missing {p} — run tighten.py / score_synth.py first")
    frames = sorted(f for f in os.listdir(args.frames) if f.startswith("f_") and f.endswith(".jpg")) if os.path.isdir(args.frames) else []
    if not frames:
        sys.exit(f"no frames in {args.frames} — run node build/render.mjs")

    dur = film_duration(args.cues, args.frames, args.duration)
    lead = lead_time(args.lead) + args.lead_in
    need = int(round(dur * FPS))
    if len(frames) < need:
        sys.exit(f"{len(frames)} frames, need {need} for {dur:.2f}s; run node build/render.mjs")

    mix = (
        f"[0:a]aformat=sample_fmts=fltp:channel_layouts=mono,highpass=f=85,"
        f"equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=2.5,"
        f"acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=3,"
        f"adelay={int(lead * 1000)},apad,atrim=0:{dur:.3f},asplit=2[v][sc];"
        f"[1:a]volume={args.music_gain}[m];"
        f"[m][sc]sidechaincompress=threshold=0.04:ratio=3:attack=40:release=450[md];"
        f"[2:a]volume={args.sfx_gain}[fx];"
        f"[v]pan=stereo|c0=c0|c1=c0[vs];"
        f"[vs][md][fx]amix=inputs=3:normalize=0:duration=first,atrim=0:{dur:.3f}"
    )
    os.makedirs("build", exist_ok=True)
    ff(["-i", args.voice, "-i", args.music, "-i", args.sfx,
        "-filter_complex", mix + "[o]", "-map", "[o]", "-ar", "48000", "build/mix.wav"])
    m = measure_loudness("build/mix.wav")
    ln = (f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
          f"offset={m['target_offset']}:linear=true")
    ff(["-i", "build/mix.wav", "-af", ln, "-ar", "48000", "build/mix_norm.wav"])
    print(f"mix: lead {lead:.2f}s, music {args.music_gain}, sfx {args.sfx_gain}, "
          f"input {m['input_i']} LUFS -> -14 LUFS")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    finish = ("rgbashift=rh=-1:bh=1,"
              "noise=c0s=5:c0f=t+u:c1s=2:c1f=t+u:c2s=2:c2f=t+u,"
              "vignette=angle=PI/6:mode=forward,")
    vf = ("" if args.no_finish else finish) + \
        "scale=out_range=tv:out_color_matrix=bt709:in_range=pc,format=yuv420p"
    ff(["-framerate", str(FPS), "-i", os.path.join(args.frames, "f_%05d.jpg"),
        "-i", "build/mix_norm.wav", "-vf", vf, "-frames:v", str(need),
        "-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf),
        "-maxrate", "14M", "-bufsize", "28M", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709",
        "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", args.out])

    info = ffprobe(args.out)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    size = os.path.getsize(args.out) / 1e6
    print(f"wrote {args.out}  {float(info['format']['duration']):.2f}s  {size:.1f} MB  "
          f"{v['width']}x{v['height']} {v['codec_name']} {v['r_frame_rate']}"
          + (f"  {a['codec_name']} {int(a.get('bit_rate', 0)) // 1000}k" if a else ""))


if __name__ == "__main__":
    main()
