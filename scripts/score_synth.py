#!/usr/bin/env python3
"""Original synth score + all SFX from the film cues. numpy only, no samples.

    python build/score_synth.py                  # reads build/cues.json
    python build/score_synth.py --score score.json

cues.json comes from `node build/render.mjs sfx`: scene cuts, transitions and
the inline sfx(t, kind, gain) registry. The score turns its sections on those
cuts, stabs the hard cuts and stops dead before the big reveals.

Optional build/score.json (all keys optional):
{
  "bpm": 96,
  "sections": [{"a": 0, "b": 21.4, "prog": ["Dm","Bb","F","C"], "density": 1}, ...],
  "stops": [[21.1, 21.35], [49.0, 49.2]],
  "outro": {"a": 74.8, "chord": "D"},
  "sfx_mute": ["tick"]
}
Without it the acts, chords, stabs, stops and outro are derived from the cuts.

Writes build/music.wav, build/sfx.wav and build/score_meta.json at 44.1 kHz.
"""
import argparse
import bisect
import json
import math
import os
import wave

import numpy as np

SR = 44100
rng = np.random.default_rng(11)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# root (MIDI), pad voicing, arpeggio figure
CHORDS = {
    "Dm": (38, [62, 65, 69], [62, 69, 74, 69, 65, 69, 74, 69]),
    "Bb": (34, [58, 62, 65], [58, 65, 70, 65, 62, 65, 70, 65]),
    "F":  (41, [57, 60, 65], [57, 65, 69, 65, 60, 65, 69, 65]),
    "C":  (36, [55, 60, 64], [55, 64, 67, 64, 60, 64, 67, 64]),
    "Gm": (31, [55, 58, 62], [55, 62, 67, 62, 58, 62, 67, 62]),
    "A":  (33, [57, 61, 64], [57, 64, 69, 64, 61, 64, 69, 64]),
    "D":  (38, [62, 66, 69], [62, 69, 74, 69, 66, 69, 78, 74]),
}

PROGS = [
    ["Dm", "Bb", "F", "C"],
    ["Bb", "C", "Dm", "A"],
    ["Gm", "Bb", "F", "A"],
]
DENSITY = [1, 2, 2]


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- wavetables
TAB_N = 2048
_ph = np.arange(TAB_N) / TAB_N
SAW = sum(np.sin(2 * np.pi * k * _ph) / k for k in range(1, 9)).astype(np.float32)
SAW /= np.max(np.abs(SAW))
SOFT = sum(np.sin(2 * np.pi * k * _ph) / k ** 2 for k in range(1, 7)).astype(np.float32)
SOFT /= np.max(np.abs(SOFT))


def osc(table, freq, dur, phase=0.0):
    n = max(1, int(round(dur * SR)))
    ph = phase + freq * np.arange(n) / SR
    return table[(ph % 1.0 * TAB_N).astype(np.int32) % TAB_N]


def ta(d):
    return np.arange(max(1, int(round(d * SR)))) / SR


def fit(y, n):
    y = np.asarray(y, np.float32)
    if len(y) >= n:
        return y[:n]
    return np.pad(y, (0, n - len(y)))


def env(n, attack=.01, release=.2, curve=1.0):
    a = max(1, int(attack * SR))
    r = max(1, int(release * SR))
    e = np.ones(n, np.float32)
    a = min(a, n)
    e[:a] = np.linspace(0, 1, a) ** .7
    r = min(r, n)
    e[-r:] *= np.linspace(1, 0, r) ** curve
    return e


def band(x, lo=None, hi=None, order=4):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    f[0] = 1e-3
    H = np.ones_like(f)
    if lo:
        H *= 1 / (1 + (lo / f) ** order)
    if hi:
        H *= 1 / (1 + (f / hi) ** order)
    return np.fft.irfft(X * H, len(x))


def sweep(f0, f1, d, k=5):
    t = ta(d)
    f = f1 + (f0 - f1) * np.exp(-t * k)
    return np.sin(2 * np.pi * np.cumsum(f) / SR), t


# ------------------------------------------------------------------- buses
class Bus:
    def __init__(self, n):
        self.x = np.zeros((n, 2), np.float32)


def add(bus, t, sig, g=1.0, pan=0.0, send=.2, hall=None):
    if g == 0:
        return
    sig = np.asarray(sig, np.float32)
    if sig.ndim == 1:
        sig = np.repeat(sig[:, None], 2, 1)
    i = int(round(t * SR))
    if i >= len(bus.x):
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    n = min(len(sig), len(bus.x) - i)
    if n <= 0:
        return
    seg = sig[:n] * np.array([g * min(1, 1 - pan), g * min(1, 1 + pan)], np.float32)
    bus.x[i:i + n] += seg
    if hall is not None and send:
        hall.x[i:i + n] += seg * send


# ------------------------------------------------------------------ cues
def load_cues(path):
    with open(path, encoding="utf-8") as f:
        c = json.load(f)
    c.setdefault("scenes", [])
    c.setdefault("sfx", [])
    return c


def auto_sections(cues, dur):
    starts = sorted({round(s["a"], 3) for s in cues["scenes"] if s["a"] > .5})
    outro = None
    if starts:
        last = cues["scenes"][-1]
        span = last["b"] - last["a"]
        if 1.4 <= span <= 7.0:
            outro = round(last["a"], 3)

    def snap(target, lo, hi):
        cand = [x for x in starts if lo < x < hi]
        return min(cand, key=lambda x: abs(x - target)) if cand else target

    end = outro if outro else dur - 2.4
    if end < 6:
        return [], {"a": max(0.0, end), "chord": "D"}

    n_acts = 3 if end > 26 else 2
    edges = [0.0]
    for k in range(1, n_acts):
        target = end * k / n_acts
        lo = edges[-1] + 2.0
        hi = end - (n_acts - k) * 2.0
        edges.append(snap(target, lo, hi))
    edges.append(end)
    sections = []
    for k in range(n_acts):
        a, b = edges[k], edges[k + 1]
        if b - a < 1.2:
            continue
        sections.append(dict(a=a, b=b, prog=PROGS[k % len(PROGS)], density=DENSITY[k % len(DENSITY)]))
    return sections, {"a": end, "chord": "D"}


def chord_map(sections, bpm):
    bar = 4 * 60 / bpm
    changes = []
    for s in sections:
        bl = bar
        t = s["a"]
        k = 0
        while t < s["b"] - .03:
            changes.append((round(t, 3), s["prog"][k % len(s["prog"])]))
            t += bl
            k += 1
    return changes


def chord_at(changes, t, fallback="Dm"):
    if not changes:
        return fallback
    i = bisect.bisect_right([c[0] for c in changes], t + 1e-6) - 1
    return changes[max(0, i)][1]


def cutoff_stops(cues, sections, dur):
    cuts = [s["a"] for s in cues["scenes"] if s["a"] > .8]
    strong = []
    for t, kind, g in cues["sfx"]:
        if kind in ("impact", "sub", "stamp", "scratch") and float(g) >= .7:
            strong.append(float(t))
    stops, last = [], -99
    for c in cuts:
        if any(abs(t - c) < .3 or abs(t - c) < 1.2 and t <= c for t in strong) and c - last > 7.0:
            stops.append([round(c - .24, 3), round(c - .03, 3)])
            last = c
    return stops


# ---------------------------------------------------------------- synths
def pad_note(m, dur, g):
    f = midi_hz(m)
    dur = max(.2, dur)
    n = int(round((dur + .9) * SR))
    x = np.zeros(n, np.float32)
    for dt in (-.006, 0.0, .006):
        y = osc(SAW, f * (1 + dt), dur + .9, phase=rng.random())
        x[:min(n, len(y))] += y[:n]
    x /= 3
    lfo = 1 + .045 * np.sin(2 * np.pi * .11 * np.arange(n) / SR + rng.random() * 6)
    e = env(n, attack=.3, release=.9, curve=1.4)
    return np.tanh(x * e * lfo * .8) * g


def pluck(m, dur, vel, bright=.5):
    f = midi_hz(m)
    n = int(max(.08, dur) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for k in range(1, 6):
        if f * k > 15000:
            break
        x += np.sin(2 * np.pi * f * k * t + k * .3) / k ** (1.7 - bright)
    x *= np.exp(-t * (7.5 - 2 * bright))
    x += band(rng.normal(size=n), 2000, 9000) * np.exp(-t * 180) * .18
    return x * vel * .45


def stab(chord, g=1.0):
    root, tones, _ = CHORDS[chord]
    d = .62
    n = int(round(d * SR))
    out = []
    for k, m in enumerate(tones):
        x = fit(osc(SAW, midi_hz(m + 12), d), n) * env(n, .004, .5, 1.6)
        out.append(x * g * (.5 if k else .62))
    x = sum(out) + fit(osc(SAW, midi_hz(root + 12), d), n) * env(n, .004, .45, 1.4) * g * .7
    return np.tanh(x * 1.3) * .8


def kick():
    s, t = sweep(118, 42, .32, 9)
    click = band(rng.normal(size=len(t)), 1800, 9000) * np.exp(-t * 200)
    return (s * np.exp(-t * 10) * .95 + click * .35).astype(np.float32)


KICK = kick()


def clap():
    t = ta(.16)
    n = len(t)
    x = np.zeros(n, np.float32)
    for dt in (0, .009, .019):
        i = int(dt * SR)
        seg = band(rng.normal(size=n - i), 900, 6000) * np.exp(-np.arange(n - i) / (0.018 * SR))
        x[i:] += seg[:n - i] * (1 if dt == 0 else .6)
    return x * .4


def hat(open_=False):
    t = ta(.22 if open_ else .05)
    x = band(rng.normal(size=len(t)), 6500, 15000)
    return x * np.exp(-t * (18 if open_ else 110)) * .5


def snare():
    t = ta(.2)
    noise = band(rng.normal(size=len(t)), 1200, 7000) * np.exp(-t * 24)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * .3
    return (noise + tone) * .55


def boom():
    s, t = sweep(85, 32, .45, 4)
    return s * np.exp(-t * 7) * .9


def tick():
    r = np.random.default_rng(7)
    t = ta(.025)
    return band(r.normal(size=len(t)), 3000, 9000) * np.exp(-t * 400) * .25


def riser(d=.9):
    t = ta(d)
    p = t / t[-1]
    n = rng.normal(size=len(t))
    y = np.zeros(len(t), np.float32)
    for k in range(6):
        c = 300 * 2 ** (k * .7)
        y += band(n, c * .7, c * 1.5) * np.exp(-((p - (.2 + k * .13)) / .28) ** 2)
    f = 90 * 2 ** (p * 3.4)
    y += np.sin(2 * np.pi * np.cumsum(f) / SR) * p ** 2 * .35
    return (y * np.sin(np.pi * p) ** .8 * .8).astype(np.float32)


def swell(d=.5):
    t = ta(d)
    p = t / t[-1]
    return band(rng.normal(size=len(t)), 200, 4500) * np.sin(np.pi * p) ** 2 * .5


# ------------------------------------------------------------------ score
def build_score(cues, cfg):
    dur = float(cfg.get("duration") or cues.get("duration"))
    n = int(round(dur * SR))
    PAD, BASS, DRUM, ARP, FXM, HALL = (Bus(n) for _ in range(6))

    sections = cfg.get("sections")
    outro = cfg.get("outro")
    if not sections:
        sections, auto_outro = auto_sections(cues, dur)
        outro = outro or auto_outro
    outro = dict(outro or {"a": max(0.0, dur - 2.4), "chord": "D"})
    bpm = float(cfg.get("bpm") or 96)
    bar = 4 * 60 / bpm
    changes = chord_map(sections, bpm)
    kick_times = []

    for si, s in enumerate(sections):
        a, b = float(s["a"]), min(float(s["b"]), float(outro["a"]))
        prog = s.get("prog") or PROGS[0]
        dens = int(s.get("density", 1))
        t = a
        k = 0
        while t < b - .04:
            seg = min(bar, b - t)
            ch = prog[k % len(prog)]
            root, tones, arp = CHORDS[ch]
            # pad
            for j, m in enumerate(tones):
                add(PAD, t, pad_note(m, seg * .98, .5 if dens else .36), 1.0, (-.45, 0, .45)[j], .3, HALL)
            add(PAD, t, pad_note(root + 36, seg * .98, .3), 1, .2, .3, HALL)
            # bass ostinato in 8ths, accents on 3+3+2
            step = seg / 8
            sub = 2 if dens >= 2 else 1
            for q in range(8 * sub):
                tt = t + q * step / sub
                acc = (q // sub) in (0, 3, 6) and q % sub == 0
                if q % sub and not acc:
                    continue
                f = midi_hz(root + 12)
                d = max(.06, step / sub * .8)
                nn = int(round(d * SR))
                x = (np.sin(2 * np.pi * f * np.arange(nn) / SR) * np.exp(-np.arange(nn) / (.05 * SR))
                     + .25 * fit(osc(SOFT, f * 2, d), nn) * np.exp(-np.arange(nn) / (.03 * SR)))
                add(BASS, tt, x * (.55 if acc else .32) * (.85 if dens else .55), 1, 0, .05, HALL)
            # drums
            if dens >= 1:
                qs = (0, 1, 2, 3) if dens >= 2 else (0, 2)
                for q in qs:
                    kt = t + q * seg / 4
                    add(DRUM, kt, KICK, .9 if q % 2 == 0 else .62, 0, .05)
                    kick_times.append(kt)
                if dens >= 2 and seg > .6:
                    add(DRUM, t + seg * .25, clap(), .8, -.15, .08, HALL)
                    add(DRUM, t + seg * .75, clap(), .8, .15, .08, HALL)
                for q in range(8 if dens >= 2 else 4):
                    add(DRUM, t + q * seg / (8 if dens >= 2 else 4), hat(False), .38 if q % 2 else .22, .25, .04)
                if dens >= 2:
                    add(DRUM, t + seg * .5, hat(True), .28, -.25, .05)
            else:
                for q in range(4):
                    add(DRUM, t + q * seg / 4, tick(), .3, .2, .02)
            # arpeggio
            if dens >= 1:
                arp_step = seg / 8
                for q, m in enumerate(arp):
                    v = .75 if q in (0, 3, 6) else .5
                    g = (.4 if dens >= 2 else .28) * v
                    add(ARP, t + q * arp_step, pluck(m, arp_step * .85, 1.0), g, -.4, .25, HALL)
                    if dens >= 2:
                        add(ARP, t + q * arp_step, pluck(m + 12, arp_step * .6, 1.0, .8), g * .45, .4, .2, HALL)
            t += seg
            k += 1
        if si > 0 and b - a > 1.0:
            add(FXM, a - min(.9, (b - a) * .25), riser(.8), .5, 0, .2, HALL)

    # stabs, stops and transitions
    cuts = [s["a"] for s in cues["scenes"] if s["a"] > .05]
    cue_by_cut = {}
    for t, kind, g in cues["sfx"]:
        for c in cuts:
            if abs(float(t) - c) < .25:
                prev = cue_by_cut.get(c)
                if prev is None or float(g) > prev[1]:
                    cue_by_cut[c] = (kind, float(g))
    act_starts = [float(s["a"]) for s in sections[1:]]
    stabbed = set()
    for c in cuts:
        kind, g = cue_by_cut.get(c, ("", 0))
        if kind in ("hit", "impact", "sub", "stamp") or any(abs(c - a) < .01 for a in act_starts):
            add(PAD, c - .02, stab(chord_at(changes, c - .02), .9), 1.0, 0, .35, HALL)
            add(DRUM, c - .02, boom(), .75, 0, .25, HALL)
            kick_times.append(c - .02)
            stabbed.add(round(c, 2))
    for a in act_starts:
        if round(a, 2) in stabbed:
            continue
        add(FXM, a - .02, stab(chord_at(changes, a), 1.0), .8, 0, .4, HALL)
        add(DRUM, a - .02, boom(), .9, 0, .2, HALL)
        kick_times.append(a - .02)

    # outro
    o = float(outro["a"])
    och = outro.get("chord", "D")
    if o < dur - .3:
        root, tones, arp = CHORDS[och]
        for j, m in enumerate(tones):
            add(PAD, o, pad_note(m, dur - o + .4, .62), 1, (-.4, 0, .4)[j], .4, HALL)
        add(PAD, o, pad_note(root + 24, dur - o + .4, .45), 1, 0, .3, HALL)
        add(DRUM, o, boom(), .85, 0, .25, HALL)
        kick_times.append(o)
        for q in range(int((dur - o) / .22)):
            m = arp[q % len(arp)] + 12
            add(ARP, o + .12 + q * .22, pluck(m, .5, 1.0, .8), .3 * (1 - q / max(1, (dur - o) / .22)) + .06, (-.3, .3)[q % 2], .35, HALL)
        add(FXM, o, swell(min(1.2, dur - o)), .35, 0, .3, HALL)

    # hard stops last, so nothing sneaks back in
    stops = cfg.get("stops") or cutoff_stops(cues, sections, dur)
    stop_gain = np.ones(n, np.float32)
    for a, b in stops:
        i0, i1 = max(0, int(a * SR)), min(n, int(b * SR))
        f = int(.03 * SR)
        stop_gain[i0:i1] = 0
        stop_gain[max(0, i0 - f):i0] = np.linspace(1, 0, min(f, i0))
        stop_gain[i1:i1 + f] = np.linspace(0, 1, min(f, n - i1))

    # sidechain everything tonal to the kick
    duck = np.ones(n, np.float32)
    for kt in kick_times:
        i = int(kt * SR)
        if i < 0 or i >= n:
            continue
        m = min(int(.28 * SR), n - i)
        env_ = 1 - .5 * np.exp(-np.arange(m) / (.085 * SR))
        duck[i:i + m] = np.minimum(duck[i:i + m], env_)

    tonal = (PAD.x + ARP.x * .95) * duck[:, None] * stop_gain[:, None]
    bass = BASS.x * duck[:, None] * stop_gain[:, None]
    full = tonal + bass + DRUM.x * stop_gain[:, None] + FXM.x * stop_gain[:, None]
    del PAD, BASS, ARP, FXM
    for ch, seed in ((0, 1), (1, 2)):
        full[:, ch] += conv(HALL.x[:, ch], ir(1.9, seed)) * .32
    fade = int(.9 * SR)
    full[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
    full = full[:n]
    full /= np.max(np.abs(full)) + 1e-9
    full *= .88
    return full.astype(np.float32), changes, sections, stops, bpm


def ir(sec, seed):
    r = np.random.default_rng(seed)
    t = np.arange(int(sec * SR)) / SR
    y = band(r.normal(size=len(t)) * np.exp(-t * 6.9 / sec), 200, 7000)
    y = np.concatenate([np.zeros(int(.03 * SR)), y])
    return (y / np.sqrt(np.sum(y ** 2) + 1e-12)).astype(np.float32)


def conv(x, h, blk=1 << 18):
    out = np.zeros(len(x) + len(h), np.float32)
    nf = 1 << int(np.ceil(np.log2(blk + len(h))))
    H = np.fft.rfft(h, nf)
    for s in range(0, len(x), blk):
        seg = x[s:s + blk]
        y = np.fft.irfft(np.fft.rfft(seg, nf) * H, nf)[:len(seg) + len(h)]
        out[s:s + len(y)] += y
    return out[:len(x)]


# ------------------------------------------------------------------- sfx
def s_whoosh(i):
    t = ta(.42)
    p = t / t[-1]
    n = rng.normal(size=len(t))
    y = sum(band(n, 600 * 2 ** (j * .6) * .7, 600 * 2 ** (j * .6) * 1.4) * np.exp(-((p - .3 - j * .06) / .14) ** 2) for j in range(5))
    return y * np.sin(np.pi * p) ** 1.1 * 1.1


def s_impact(i):
    s, t = sweep(130, 38, 1.4, 6)
    return s * np.exp(-t * 2.6) * .9 + band(rng.normal(size=len(t)), 60, 1200) * np.exp(-t * 14) * .8 + band(rng.normal(size=len(t)), 2000, 9000) * np.exp(-t * 60) * .3


def s_sub(i):
    s, t = sweep(70, 30, 1.6, 2.5)
    return s * np.minimum(1, t * 40) * np.exp(-t * 1.8)


def s_hit(i):
    s, t = sweep(160, 70, .5, 12)
    return s * np.exp(-t * 9) * .7 + band(rng.normal(size=len(t)), 250, 4000) * np.exp(-t * 22) * .6


def s_riser(i):
    return riser(1.1) * 1.4


def s_scratch(i):
    t = ta(.38)
    p = t / t[-1]
    fc = 400 + 2600 * np.abs(np.sin(np.pi * p * 2.2)) ** .7
    n = rng.normal(size=len(t))
    y = np.zeros(len(t))
    for c in (500, 900, 1500, 2400, 3200):
        y += band(n, c * .8, c * 1.25) * np.exp(-((fc - c) / 450) ** 2)
    return y * (1 - p) ** .4 * 1.4


def s_notif(i):
    t = ta(.32)
    a = np.sin(2 * np.pi * 1318 * t) * np.exp(-t * 18) * (t < .12)
    b = np.sin(2 * np.pi * 1760 * t) * np.exp(-(t - .1) * 14) * (t >= .1)
    return (a + b) * .4


def s_cash(i):
    t = ta(.8)
    bell = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) * g for f, d, g in ((2093, 5, .3), (2637, 6, .25), (3136, 7, .2), (4186, 9, .12)))
    clk = band(rng.normal(size=len(t)), 1500, 8000) * np.exp(-t * 80)
    return bell * (t > .05) + clk * .8


def s_projector(i):
    t = ta(1.8)
    y = np.zeros(len(t))
    for k in np.arange(0, 1.8, 1 / 18):
        j = int(k * SR)
        seg = band(rng.normal(size=600), 1500, 7000) * np.exp(-np.arange(600) / 60)
        y[j:j + 600] += seg[:len(y) - j] * .5
    return y * np.minimum(1, t * 4) * np.minimum(1, (1.8 - t) * 3) + np.sin(2 * np.pi * 50 * t) * .05


def s_pop(i):
    r = np.random.default_rng(i)
    t = ta(.09)
    return band(r.normal(size=len(t)), 900, 5000) * np.exp(-t * 90) * .6 + np.sin(2 * np.pi * 1300 * t) * np.exp(-t * 70) * .08


def s_pill(i):
    t = ta(.2)
    f = 587 * 2 ** ((i % 6) * 2 / 12)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 24) * .4 + np.sin(4 * np.pi * f * t) * np.exp(-t * 40) * .12 + s_hit(i)[:len(t)] * .3


def s_tick(i):
    r = np.random.default_rng(i)
    t = ta(.03)
    return band(r.normal(size=len(t)), 2500, 9000) * np.exp(-t * 300)


def s_key(i):
    r = np.random.default_rng(i + 99)
    t = ta(.05)
    return (band(r.normal(size=len(t)), 1500, 7000) * np.exp(-t * 200) + band(r.normal(size=len(t)), 150, 900) * np.exp(-t * 120) * .5) * r.uniform(.6, 1)


def s_stamp(i):
    t = ta(.4)
    return np.sin(2 * np.pi * np.cumsum(60 + 90 * np.exp(-t * 35)) / SR) * np.exp(-t * 14) + band(rng.normal(size=len(t)), 200, 2500) * np.exp(-t * 40) * .6


def s_rise(i):
    t = ta(.8)
    p = t / t[-1]
    return band(rng.normal(size=len(t)), 600, 6000) * p ** 2 * np.exp(-((p - .85) / .3) ** 2) * .7


def s_swell(i):
    return swell(1.0) * 1.2


def s_scan(i):
    t = ta(.8)
    p = t / t[-1]
    return band(rng.normal(size=len(t)), 3000, 9000) * (.4 + .6 * np.sin(2 * np.pi * 14 * t) ** 2) * np.sin(np.pi * p) * .4


def s_shutter(i):
    t = ta(.25)
    a = band(rng.normal(size=len(t)), 1500, 8000) * np.exp(-t * 160)
    b = np.roll(band(rng.normal(size=len(t)), 1200, 6000) * np.exp(-t * 120), int(.07 * SR))
    return (a + b * .8) * .9


def s_flip(i):
    r = np.random.default_rng(i + 31)
    t = ta(.18)
    p = t / t[-1]
    return band(r.normal(size=len(t)), 1200, 7000) * np.sin(np.pi * p) ** .5 * np.exp(-p * 3) * .8


def s_fall(i):
    t = ta(1.4)
    p = t / t[-1]
    f = 1600 * np.exp(-p * 1.8)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * p) * .14 + band(rng.normal(size=len(t)), 300, 2000) * np.sin(np.pi * p) ** 2 * .35


def s_wave(i):
    t = ta(2.0)
    p = t / t[-1]
    return band(rng.normal(size=len(t)), 150, 2500) * np.sin(np.pi * p) ** 1.5 * (.6 + .4 * np.sin(2 * np.pi * .7 * t)) * .6


def s_vhs(i):
    t = ta(.6)
    clunk = band(rng.normal(size=len(t)), 100, 1500) * np.exp(-t * 30)
    hum = np.sin(2 * np.pi * 60 * t) * .2 * np.clip(t * 6, 0, 1) * np.exp(-t * 3)
    return clunk + hum + band(rng.normal(size=len(t)), 4000, 9000) * .08 * np.exp(-t * 4)


def s_door(i):
    t = ta(.3)
    return band(rng.normal(size=len(t)), 300, 2000) * np.exp(-t * 25) * .6 + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 18) * .2


SFX = {
    "whoosh": (s_whoosh, .3), "impact": (s_impact, .55), "sub": (s_sub, .5), "hit": (s_hit, .4),
    "riser": (s_riser, .3), "scratch": (s_scratch, .35), "notif": (s_notif, .22), "cash": (s_cash, .3),
    "projector": (s_projector, .25), "pop": (s_pop, .16), "pill": (s_pill, .32), "tick": (s_tick, .07),
    "key": (s_key, .14), "stamp": (s_stamp, .42), "rise": (s_rise, .16), "swell": (s_swell, .14),
    "scan": (s_scan, .08), "shutter": (s_shutter, .32), "flip": (s_flip, .18), "fall": (s_fall, .22),
    "wave": (s_wave, .16), "vhs": (s_vhs, .26), "door": (s_door, .18),
}


def build_sfx(cues, dur, mute):
    n = int(round(dur * SR))
    FX = Bus(n)
    r = np.random.default_rng(23)
    missing = set()
    for i, cue in enumerate(cues["sfx"]):
        t, kind, v = float(cue[0]), cue[1], float(cue[2])
        if kind in mute:
            continue
        if kind not in SFX:
            missing.add(kind)
            fn, g = SFX["pop"]
        else:
            fn, g = SFX[kind]
        y = np.asarray(fn(i), np.float32)
        if y.ndim == 1:
            y = np.repeat(y[:, None], 2, 1)
        i0 = int(round(t * SR))
        if i0 < 0:
            y = y[-i0:]
            i0 = 0
        m = min(len(y), n - i0)
        if m <= 0:
            continue
        pan = float(np.clip(r.normal(0, .2), -.4, .4))
        FX.x[i0:i0 + m] += y[:m] * np.array([g * v * min(1, 1 - pan), g * v * min(1, 1 + pan)], np.float32)
    if missing:
        print("warning: unknown sfx kinds -> pop:", ", ".join(sorted(missing)))
    FX.x /= np.max(np.abs(FX.x)) + 1e-9
    FX.x *= .92
    return FX.x.astype(np.float32)


def write_wav(path, x):
    with wave.open(path, "wb") as wv:
        wv.setnchannels(2)
        wv.setsampwidth(2)
        wv.setframerate(SR)
        wv.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def main():
    os.chdir(ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--cues", default="build/cues.json")
    ap.add_argument("--score", default="build/score.json")
    ap.add_argument("--out-dir", default="build")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--no-sfx", action="store_true")
    args = ap.parse_args()

    cues = load_cues(args.cues)
    cfg = {}
    if os.path.exists(args.score):
        with open(args.score, encoding="utf-8") as f:
            cfg = json.load(f)
        print("score plan:", args.score)
    if args.bpm:
        cfg["bpm"] = args.bpm
    if args.duration:
        cfg["duration"] = args.duration
    if not cfg.get("duration"):
        cfg["duration"] = cues.get("duration")
    dur = float(cfg.get("duration") or 0)
    if dur <= 0:
        raise SystemExit("no duration in cues.json; pass --duration")

    music, changes, sections, stops, bpm = build_score(cues, cfg)
    os.makedirs(args.out_dir, exist_ok=True)
    write_wav(os.path.join(args.out_dir, "music.wav"), music)
    print(f"music.wav  {dur:.1f}s  {bpm:.0f} bpm  {len(sections)} sections  {len(stops)} stops")

    if not args.no_sfx:
        fx = build_sfx(cues, dur, set(cfg.get("sfx_mute", [])))
        write_wav(os.path.join(args.out_dir, "sfx.wav"), fx)
        print(f"sfx.wav    {len(cues['sfx'])} cues")

    meta = {
        "duration": dur, "bpm": bpm, "sections": sections, "stops": stops,
        "changes": changes, "chords": sorted(CHORDS),
        "sfx_count": len(cues["sfx"]),
    }
    with open(os.path.join(args.out_dir, "score_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print("wrote build/score_meta.json")


if __name__ == "__main__":
    main()
