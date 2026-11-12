> Scope: optional original poster preset. These style, language, framing and audio recipes are not universal requirements. Follow SKILL.md and the selected brief for other directions.

# Narration, score and mix

The voice is the spine. Cuts, type, score sections and sound effects all hang from word timings.

## Narration pipeline

### 1. Takes

`narr/takes.json`:

```json
[
  {"file": "narr/raw1.m4a", "start": 0.0, "end": null, "gain": 0},
  {"file": "narr/raw2.m4a", "start": 1.2, "end": null, "gain": -1.5}
]
```

- Record each paragraph/take separately. Keep the same mic, distance and room.
- `start` / `end`: trim a bad intro/outro before processing; `null` end = file end.
- `gain`: per-take dB correction. Aim for equal perceived loudness before cutting.
- One voice, one room. Do not stitch two mic distances.

### 2. Tighten

```bash
python build/tighten.py --tempo 1.07 --gap .08
```

- Silence gate: −42 dB, minimum silence 0.1 s.
- Every pause is shrunk to `gap` (0.08 s default) by keeping `gap/2` on each side.
- Spans below 0.02 s are dropped; 8 ms fades prevent clicks.
- The whole edit is concatenated and sped up with `atempo` (pitch preserved). 1.04–1.10 is the house range; 1.07 is urgent but natural.
- Output: `narr/voice_edit.wav` (48 kHz mono) and `narr/edl.json`.

Audition the result. If a breath survives, it is usually a low-level noise floor inside a span, not a detected silence. Inspect the gap with level + spectral centroid and either cut it with a manual span or add a short fade. Do not blanket-gate the voice; it will sound lispy.

If the read is too fast after tightening, reduce `--tempo` before cutting scenes. Scene count follows the voice, not the other way round.

### 3. Transcribe and align

```bash
python build/asr.py --engine whisper --model small --input narr/voice_edit.wav --out narr/words.json
python build/align_words.py --words narr/words.json --lead 0.10
```

- ASR must run on the **already-tightened** file, so word times are final.
- `faster-whisper` `small`, language `fa`, word timestamps on, VAD on. Vosk is a fallback.
- `align_words.py` offsets every word by `--lead`, repairs overlaps, enforces 0.05 s minimum, and writes `js/words.js` + `build/film_words.json`.
- `--lead 0.10` means the first voice sample sits at film time 0.10 s. Pass `--lead 0.10` explicitly to `mix.py` as well. Its automatic fallback uses the first word timestamp, which also includes any silence before that word and can add an unwanted delay. Keep the same explicit lead in both commands.

Check:
- count and order match the script; ASR drops or merges short words.
- first word ~lead, last word before the final scene's end.
- no gaps over 0.4 s inside a sentence (unless a dramatic pause is intentional).
- Persian forms normalized (ی/ک, ZWNJ) — ASR may write `می شود`; fix in the script/JS, not in the timing file.

### Writing for the voice

- 1.8–2.2 words/s is comfortable; 2.2–2.8 is urgent. Above that, Persian consonants collide.
- Short sentences. One idea per clause. Read numbers as words in the script, but display Persian digits on screen.
- Put the hook in the first 1.5 s. The first sentence must create a question.
- Leave a 0.3–0.6 s beat before the turn and before the CTA. The score uses those holes.

## Score

Two proven modes. Default to the synth hybrid; switch to sampled orchestral only if the project has a sample library and the time.

### A. Synth hybrid (bundled)

`python build/score_synth.py` reads `build/cues.json` and writes `build/music.wav`, `build/sfx.wav`, `build/score_meta.json` — numpy only, no samples.

- Key: D minor bank (`Dm Bb F C Gm A`) with a D-major lift for the outro.
- Tempo: 96 bpm default. Override in `build/score.json`.
- Sections: acts derived from scene cuts at roughly 1/3 and 2/3, each with a progression and density (pad-only → driving). The final scene becomes the outro.
- Density 0: pads + clock ticks; 1: bass 8ths, kick on 1/3, hats 8ths, arp 8ths; 2: 16th hats, claps, doubled arp, four-on-floor.
- Stabs at hard cuts (hit/impact/sub/stamp cues) and act starts.
- Hard stops (music silent for ~0.22 s) before strong impact cuts, at most every 7 s.
- Risers before act changes; outro pad + bell arpeggio.
- Sidechain ducks pads/bass/arp under the kick; synthetic hall reverb; final −0 dBFS peak ×0.88.

`build/score.json` (optional):

```json
{
  "bpm": 100,
  "sections": [
    {"a": 0.0, "b": 18.2, "prog": ["Dm", "Bb", "F", "C"], "density": 1},
    {"a": 18.2, "b": 48.6, "prog": ["Bb", "C", "Dm", "A"], "density": 2},
    {"a": 48.6, "b": 71.4, "prog": ["Gm", "Bb", "F", "A"], "density": 2}
  ],
  "stops": [[18.0, 18.2], [48.4, 48.6]],
  "outro": {"a": 71.4, "chord": "D"},
  "sfx_mute": ["tick"]
}
```

Section edges should be scene cuts (word starts). Density is a musical decision: keep the hook lighter, lift the proof, peak before the turn, let the CTA ring.

### B. Sampled orchestral

An optional orchestral arrangement can use licensed strings, horn, timpani, bass drum and cymbals: a chord map tied to cut indices, cello ostinato in 3+3+2, violin arpeggios, horn line, timpani/boom stabs, reversed-cymbal risers, hard-stop gates and convolution hall. No samples, sampler.py or orchestral music.py are bundled. Supply your own licensed library and implementation, reusing build/cues.json and the mix. The bundled synth route needs no samples.

### Sound design rules

- The score is support. Leave 300 Hz–3 kHz room for the voice; avoid bright arps under dense narration.
- Music turns a corner on cuts; do not let a chord change land randomly in the middle of a line.
- A hard stop makes the next hit feel twice as big. Place it before the reveal, not after.
- End on a lift (major chord, bell arpeggio), then fade under the end card.
- One musical idea per act. Do not add a new instrument every 4 s.

## SFX

`score_synth.py` synthesizes every kind from the cue list; gains are normalized so no single effect clips. The per-kind table:

| kind | use | nominal gain |
|---|---|---|
| whoosh | cuts, scene entries, swipes | .30 |
| impact | first hook, big reveals | .55 |
| sub | low-end support under impacts | .50 |
| hit | percussive accents, slams | .40 |
| riser | build into a cut | .30 |
| scratch | a stop, a rewind, a joke | .35 |
| stamp | verdicts, approvals, tags | .42 |
| cash | money, payments, savings | .30 |
| notif | phone messages, results | .22 |
| tick | number cascades, timers | .07 |
| pop | small props, chips | .16 |
| pill | list items, cards | .32 |
| key | typing | .14 |
| flip | cards turning, toggles | .18 |
| shutter | camera, before/after | .32 |
| projector | film/reel texture | .25 |
| fall | a prop dropping | .22 |
| vhs | glitch, rewind | .26 |
| scan | scanning a QR/receipt | .08 |
| rise | short bright lift | .16 |
| swell | pad-like swell | .14 |
| wave | slow transitions | .16 |
| door | a closing beat | .18 |

Rules:
- One cue per meaningful element. If it moves and there is no sound, it feels cheap; if everything thunders, nothing does.
- Layer at most two: e.g. `impact` + `tick` cascade, or `stamp` + `sub`. Do not layer `whoosh + impact + riser` on every cut.
- Place cues on word times or 10–30 ms before the visual hit. Late sound reads as a mistake.
- The scene API already adds a whoosh/hit at every cut. Use `quiet: true` or omit manual cut swipes.
- SFX sit under the voice: mix at .8, but individual cues at .5–.9 gain. Numbers and impacts can be louder than props.
- Music stops do not mute SFX. That is what makes the stop work.

## Mix and encode

`python build/mix.py`:

1. VO: high-pass 85 Hz, −2 dB at 250 Hz, +2.5 dB at 3.2 kHz, compressor −22 dB / 3:1 / 8 ms / 120 ms, +3 dB makeup, delayed by the lead, padded/trimmed to the film duration.
2. Music: volume .58, sidechained by the VO (threshold .04, ratio 3, attack 40 ms, release 450 ms).
3. SFX: volume .8, not sidechained.
4. Sum (normalize=0), stereo the voice, 48 kHz.
5. Two-pass `loudnorm I=-14 TP=-1.0 LRA=11`, linear apply.
6. Video: optional `rgbashift` + grain + vignette, BT.709 TV range, x264 CRF 18, high profile, AAC 256k, faststart, `-frames:v duration*30`.

Why two passes: the first measures integrated loudness, true peak, LRA and threshold; the second applies a linear gain, preserving dynamics. A single-pass loudnorm behaves like a limiter and pumps.

Targets: −14 ±1 LUFS integrated, true peak ≤ −1 dBTP, 48 kHz stereo AAC. The −14 target suits Instagram/YouTube/TikTok; do not master to −9.

### Troubleshooting

| symptom | cause | fix |
|---|---|---|
| voice sounds thin | HPF too high / presence boost too strong | 85 Hz, +2.5 dB max at 3 kHz |
| voice pumps under music | sidechain attack too fast / release too short | 40 ms / 450 ms, ratio 3 |
| music overpowers VO | music gain > .65 | .55–.60 |
| SFX mask consonants | cue gain > 1 or too many layers | .7–.9, max two layers |
| mix hits −11 LUFS | loudnorm skipped | run both passes; check the final file |
| true peak over −1 | limiter not applied | lower music/SFX .02, or add `alimiter=limit=0.9` |
| score feels random | chord changes off cuts | align section `a` to `cues.scenes[].a` |
| hard stop kills the groove | too many stops | at most one per 7 s |
| end feels cut | no outro | pad + bell from the CTA cut to the end, fade .9 s |
| voice late/early | lead mismatch | one lead in `align_words.py` and one in `mix.py` |

### Audition checklist

- First 1.5 s: hook audible and music already moving.
- Under the densest line, every consonant is still clear on phone speakers.
- Every visual hit has a sound; no sound arrives more than 50 ms after its element.
- Hard stops are followed by a bigger moment.
- Last 2 s ring out; nothing loops abruptly.
- Measured −14 LUFS, TP ≤ −1, 48 kHz stereo.
