# Optional original poster preset

Read this only when the user selects the original Persian dimensional-poster direction. Its artistic rules are scoped to this preset, never to all motion graphics. User choices override preset preferences. Use ../SKILL.md for the general workflow.

# Craft Reel — Persian vertical brand films

A poster-led visual grammar for Persian vertical brand films. The grammar is fixed; the idea must be new for every film. Never clone the reference frame-for-frame.

## The taste bar (non-negotiables)

- A hook inside 1.5 s, a turn at ~60–70 %, and a direct question/CTA at the end. No intro logos, no "سلام، من…".
- 20–28 scenes for 60–90 s. Every scene is a composed poster: 4–12 supporting elements, not one lonely line of text.
- One Persian type family in 6+ weights. Display type has physical depth (extruded side + cast shadow) or a sticker treatment; nothing in between.
- One accent color plus a neutral family. Four background modes max. Never two accent hues competing.
- Kinetic words anchored to narration word indices (`W(i)`), not eyeballed seconds.
- Every number gets a visual device: 100-person grid, donut, pie with pulled slice, receipt, order cards, counter.
- Camera push on every scene, hit-shake on impacts, transitions with blur/tear/split. No dead frames, no slow crossfades.
- Score sections turn on cuts; hard stop before reveals; SFX on every meaningful element. If a thing moves and makes no sound, it feels cheap.
- Correct RTL, Persian digits, safe zones, zero clipping at any animation frame (test mid-animation, not just the end).
- QA with native-size frames and contact sheets; deliver MP4 + cover + project folder.

## Public package setup

Read [README.md](../README.md) for dependencies, installation, font setup and limitations. Treat demo statistics as fictional. Obtain narration from the user or an authorized voice service; no TTS client or voice is bundled. Only render trusted local scene code.

## Pipeline (fast path)

```bash
# 0. scaffold a new project
python "<skill>/scripts/init_reel.py" <project-dir>

# 1. narration: config narr/takes.json, then tighten and align
python build/tighten.py                     # -> narr/voice_edit.wav, narr/edl.json
python build/asr.py --engine whisper --input narr/voice_edit.wav --out narr/words.json
python build/align_words.py --words narr/words.json   # -> js/words.js, build/film_words.json

# 2. build scenes in js/scenes.js; register sfx() beside the animation code
# 3. export cues and render the score
node build/render.mjs sfx                   # -> build/cues.json
python build/score_synth.py                 # -> build/music.wav, build/sfx.wav

# 4. render frames (resumable, 30 fps JPEG)
node build/render.mjs 0 9999

# 5. QA while iterating
node build/render.mjs shot 2.0 5.5 9.1
python build/contact_sheet.py build/shots build/sheet.jpg 5

# 6. mix + encode + final QA + cover
python build/mix.py --lead 0.10             # match align_words.py --lead explicitly
python build/qa.py out/reel.mp4 --n 12
node build/render.mjs cover                 # -> out/cover.png
```

## Architecture contract

- **Everything is a pure function of film time.** `window.seek(t)` must fully redraw a frame from scratch. No GSAP-style retained timelines, no `Date.now()`, no unseeded `Math.random()` in the frame path (use `hash(n)`).
- **Words drive cuts.** `js/words.js` holds `[[word, start, end], …]` in film seconds. `W(i)` = word start, `WE(i)` = end, cuts land at `W(i) - .04`.
- **Scene API.** `scene(a, b, bg, build, {tr, hits, push})`; `build(cam, root)` returns `update(t, p)`. Only the active scene updates.
- **SFX registry.** Declare cues inline with `sfx(t, kind, gain)` next to the animation they support; export them from the page. Never hand-write cue lists twice.
- **One source of time.** Score, SFX, captions and scene cuts all derive from the same cue export.
- **Render contract.** 1080×1920, 30 fps, deterministic JPEG frames, resumable, browser recycled every ~200 frames.

Full API and pitfalls: [references/engine-spec.md](engine-spec.md).

## Art direction in brief

- **Background modes:** `bg-grid` (graph-paper daylight), `bg-paper` (photo paper), `bg-desk` (radial brand gradient + grain), `bg-navy` (night), `bg-brand` (flat accent). Pick an arc, e.g. grid → navy turn → brand CTA.
- **Type:** one properly licensed Persian family, with multiple weights mapped to `Y`. The public starter uses system fonts until you configure one. White face + deep accent side on dark; accent face + white ring on light. Persian line-height 1.45; letter-spacing 0; digits via `fa()`/`faNum()`.
- **Props:** hand-drawn SVG only (coins, wallet, calendar, scale, receipt, calculator, envelope, cart, groceries, luxury goods, phone UI). Thick rounded strokes, soft drop shadows, 2–3 tones of the accent, one warm gold.
- **Stats:** count up with easing, slam the number, pair it with a physical device, put the human sentence underneath.
- **Motion:** mask-rise and pop words; drop props with bounce; camera push 3–10 %; 24 px hit shake decaying over .35 s; whip/punch/flash/cut transitions; draw-on SVG strokes.
- **Composition:** 80 px side margins, top slug zone 0–170, hero zone 200–1100, proof zone 1100–1450, CTA/subtitle zone 1450–1700, keep 180 px clear at the bottom. Cover keeps everything inside the 3:4 profile crop (y 240–1680).

Full system, scene templates, do/don't: [references/design-language.md](design-language.md).

## Audio in brief

- **VO:** cut pauses to 0.06–0.10 s, tempo 1.04–1.10 with pitch preserved, 8 ms fades, per-take gain matching, no breaths. If breaths survive, inspect every gap with level + spectral centroid before cutting.
- **Score:** two proven modes — sampled orchestral (VSCO strings/brass/timpani; expensive, editorial) or synth hybrid (pads/bass/kick/hats; dark, urgent). Both build sections on scene boundaries and hard-stop before reveals.
- **SFX:** whoosh, impact, sub, hit, riser, scratch, stamp, cash, tick, pop, pill, flip, key, notif, shutter, projector, fall, vhs, swell. Quiet but present; never louder than the VO.
- **Mix:** VO cleaned (HPF 85, presence EQ, gentle compression), music ducked 45–55 % under voice, SFX at .7–.85, two-pass `loudnorm I=-14 TP=-1`, AAC 256k, H.264 CRF 18, TV-range BT.709, light grain/chroma/vignette finish.

Full recipes: [references/narration-and-score.md](narration-and-score.md).

## QA gates

1. **Contact sheet** every ~3 s. If any cell is boring, fix the scene.
2. **Native-size check** of every reveal: headline, stat, CTA, phone screen, caption pill. Look for clipping, overlaps, and text touching the safe zone.
3. **Mid-animation sweep:** 3–4 frames inside each transition, not just the settled state.
4. **Text sweep:** RTL punctuation, ZWNJ (`می‌شود`, `به‌خاطر`), Persian digits, no duplicated lines between hero and caption.
5. **Sound sync:** every visual hit has a cue; no cue before its element.
6. **Specs:** duration, 1080×1920, 30 fps, −14 LUFS, true peak ≤ −1 dBTP, phone playback.
7. **Cover:** readable at grid-thumbnail size, inside 3:4 crop, one idea.

Failure modes and fixes: [references/production-playbook.md](production-playbook.md).

## Resources

- `assets/starter/` — working project: deterministic engine, art library, three demo scenes, CSS backgrounds, cover. Font binaries and unverified raster textures are excluded from the public package; see README.md.
- `scripts/init_reel.py` — copy starter + pipeline into a new folder.
- `scripts/render.mjs` — frame renderer, shot mode, cue export.
- `scripts/tighten.py`, `scripts/asr.py`, `scripts/align_words.py` — narration to word timings.
- `scripts/score_synth.py` — original score + all SFX from `cues.json` (numpy only).
- `scripts/mix.py` — VO/music/SFX mix, loudnorm, final encode.
- `scripts/contact_sheet.py`, `scripts/qa.py` — visual and technical QA.
- `scripts/rebrand.py` — remap the accent color family in a copied starter.
- `references/design-language.md`, `engine-spec.md`, `narration-and-score.md`, `production-playbook.md`.

## House rules

- A reel is a sequence of posters, not slides with fades.
- One accent, many weights, deep type.
- Props carry the joke; numbers carry the argument.
- Sound designs the cut.
- If it looks like a generic SaaS explainer, start over.
- New film, new concept. Reuse the grammar, never the gags.
