> Scope: optional original poster preset. These style, language, framing and audio recipes are not universal requirements. Follow SKILL.md and the selected brief for other directions.

# Production playbook

A 60–90 s reel is 2–3 focused days, or one long day if the script and voice are ready. The order matters: voice first, cues second, polish last.

## 0. Preproduction

1. **Brief in one sentence.** Who is it for, what should they believe/do after watching, what is the one stat or turn.
2. **Research the brand.** Palette, logo lockup, type, product language, claims that are safe. Do not invent numbers. Write down sources.
3. **Script for the ear.** 1.8–2.4 words/s. Hook in the first 1.5 s, the turn at 60–70 %, a direct question/CTA at the end. Read it out loud with a timer.
4. **Choose the arc and count scenes.** 60 s → 18–22 scenes; 75 s → 22–26; 90 s → 25–30. Average scene 2.5–4 s. Hook 2–4 s, CTA 3–5 s.
5. **Storyboard on paper.** A thumbnail per scene: background mode, hero prop, headline, number/device, transition. If a scene has no visual idea beyond text, cut it or merge it.
6. **Pick the four backgrounds and the one accent.** Use `scripts/rebrand.py` if the brand is not blue.
7. **Cover idea.** One image, one headline, one stat/sticker. It can reuse a film scene but must be composed for the 3:4 crop.

Get approval on script + storyboard/arc before building. It is much cheaper to change a beat on paper.

## 1. Scaffold

```bash
python "<skill>/scripts/init_reel.py" <project-dir>
cd <project-dir>
npm i
```

Project layout:

```
index.html  cover.html  css/style.css
js/words.js  js/engine.js  js/art.js  js/art2.js  js/scenes.js
narr/  (optional user-supplied fonts/ and img/)
build/  (tighten.py, asr.py, align_words.py, render.mjs, score_synth.py, mix.py, contact_sheet.py, qa.py, rebrand.py)
out/
```

The starter already renders a 12.5 s, 3-scene demo. Render two shots before changing anything; if they fail, fix the toolchain first (Chrome path, puppeteer, fonts).

## 2. Voice

```bash
# edit narr/takes.json
python build/tighten.py
python build/asr.py --engine whisper --input narr/voice_edit.wav --out narr/words.json
python build/align_words.py --words narr/words.json
```

Audition the tightened voice on phone speakers. Fix pronunciation, breaths and pacing now. Update `window.FILM_DURATION` in `index.html` to `voice_end + CTA_tail` (usually +1.0–2.0 s), then build scenes.

## 3. Visual build

Work in passes; do not polish one scene to perfection while the rest are missing.

**Pass A — layout stills.** Write all scenes with text/props in their settled state. Render one still per scene at its midpoint. Make a contact sheet. Fix hierarchy, overlaps, and safe zones at this level.

**Pass B — motion.** Wire `reveal`, `slam`, `drop`, counters, camera shake. Render 3–4 frames around every cut and reveal. Check mid-animation clipping.

**Pass C — sound.** Add `sfx()` cues beside each animated element. Register `hits`. Then export cues and synth the score.

**Pass D — grade.** Captions, kickers, end card, brand lockup, cover. Check the 3:4 crop.

Rules during the build:
- Write scene code in the order the film plays. Name constants (`A`, `big`, `sub`, `tag`) clearly.
- Reuse a single phone position, a single button style, a single card style. Variation comes from content and composition, not new CSS.
- Use the real words in the UI copy. Persian microcopy must be complete, not lorem ipsum.
- Keep the DOM under control: create in `build`, update styles in `update`.
- Every `sfx()` goes at top level, never inside `update`.

## 4. Score and SFX

```bash
node build/render.mjs sfx          # -> build/cues.json
python build/score_synth.py        # -> build/music.wav, build/sfx.wav
```

Listen to the stems before the mix: music alone (does it move?), SFX alone (is every element covered?), voice alone. Adjust `build/score.json` if an act is too busy or too empty. If the film has long holds, add `stops` rather than lowering the whole score.

## 5. Render

```bash
node build/render.mjs shot 2 7.5 18 40 62     # check stills first
node build/render.mjs 0 9999                   # full render, resumable
```

- The renderer skips frames already on disk (size > 2 KB). If a bad frame is cached, delete that file.
- Browser is recycled every 200 frames. A crash leaves completed frames intact; rerun the same range.
- Watch the first 200 frames. Expect ~1.5–3.5 fps on CPU for a full scene; if it drops under ~1.2 fps, cut per-frame DOM/text writes, blur radii or shadow stacks.
- Frame count must be ≥ `round(DURATION * 30)` before mixing.

## 6. Mix and encode

```bash
python build/mix.py --lead 0.10
```

Duration is read from `build/cues.json`; pass the same explicit lead used by align_words.py to avoid adding the first word’s source offset twice. Output `out/reel.mp4`.

## 7. QA

```bash
python build/qa.py out/reel.mp4 --n 12
```

The script extracts 12 native-size frames, builds a contact sheet, measures loudness and checks specs. Open the sheet:

1. **Poster test.** Every cell should look like a designed still.
2. **Safe test.** Headlines, numbers, captions clear of edges and the caption pill.
3. **Mid-animation test.** Render extra shots 0.05/0.1/0.15 s inside each transition; look for clipping and blur artifacts.
4. **Text test.** ZWNJ, Persian digits, RTL punctuation, no duplicate lines between hero/caption, no cut-off final letters.
5. **Sound test.** On phone: voice intelligible, music under it, every hit audible, no late cues.
6. **Cover test.** View at 270 px and inside a 3:4 crop.

Fix, rerender only the affected frame range (delete those frames), remix.

## 8. Deliverables

- `out/reel.mp4` — 1080×1920, 30 fps, H.264/yuv420p/BT.709, AAC 256k 48k stereo, −14 LUFS, TP ≤ −1.
- `out/cover.png` — 1080×1920, key content inside the 3:4 crop.
- The project folder (scenes, words, cues, score plan, mix scripts) so the film can be revised.
- Optional: contact sheet, captions text, a 9:16 still pack.

## Story map templates

| beat | 60 s | 75 s | 90 s | job |
|---|---|---|---|---|
| hook | 0–3.5 | 0–4 | 0–5 | name the pain in one image |
| context | 3.5–15 | 4–18 | 5–22 | show why it happens, keep it human |
| proof / stat | 15–32 | 18–40 | 22–48 | one number + its device |
| turn | 32–42 | 40–52 | 48–62 | the reframe; music drops or stops |
| mechanism | 42–52 | 52–64 | 62–75 | how it works in 3 steps |
| CTA | 52–60 | 64–75 | 75–90 | one question/action |

The exact cuts come from the voice. Treat this as a budget, not a rule.

## Scene budget guide

- 4–12 elements per scene.
- 1 hero prop or 1 phone; not both, unless the phone is the hero.
- 1 number per scene, maximum 2.
- 1 verdict/claim line; supporting text is smaller and shorter.
- 3–5 small props at the edges; they should be partly cropped or out of focus.
- 1 transition idea per cut; do not stack punch + flash + tear.

## Review loop

Watch the export three ways:
1. **Muted**, at arm's length: does the story read without sound?
2. **Sound on**, eyes closed: does the voice land, does the score breathe?
3. **On a phone**, thumb over the bottom third: are captions and CTAs still visible?

Collect notes by timecode + frame. Change the scene, rerender that range, remix. Do not rebuild the whole film for a 0.2 s fix.

## Failure modes

| symptom | likely cause | fix |
|---|---|---|
| scene looks like a slide | one text block, flat background, no prop | add a physical device and 3–5 props; give the type depth |
| text clipped mid-animation | word masks, `.scene` overflow, camera push | mask padding; keep content inside the central 95 % |
| phone screen content escapes | height on wrapper, not `.phone` | set width/height on `.phone` itself |
| orbit/ring hidden behind phone | DOM order | `insertBefore(ring, phone)` |
| receipt rows overlap | row height vs. content length | compute height from rows, test the longest label |
| two lines say the same thing | hero + caption duplicate | caption = speech, hero = verdict |
| broken subtitle sentence | line edited after timing | update words + caption together |
| every cut sounds the same | auto whoosh + manual whoosh | use `quiet: true` or drop the manual cue |
| score starts slow | long pad intro | start on a stab/kick at the hook |
| music stops too early | outro start before the last visual | align outro to the CTA cut |
| render dies mid-run | Chrome crash / memory | rerun the range; reduce DOM/blur if it repeats |
| render command ends early | piping to `head`/`tail` | never pipe the renderer; use `from to` ranges |
| frames are stale | cached > 2 KB | delete the affected `f_XXXXX.jpg` |
| headline clipped at top | top < 90 px or camera push | move down; keep slug zone empty |
| Persian prints as `????` | cp1252 stdout | use UTF-8 files; avoid printing Persian in scripts |
| folder path breaks the build | spaces in the path | quote every path in bash commands |
| loudness off | single-pass loudnorm / skipped mix | two-pass measure + linear apply |
| SFX late | cue placed after the visual | cue at or 10–30 ms before the hit |
| CTA feels weak | last scene is a logo | end on a question/action, logo as a small lockup |
| generic SaaS look | too many pastels, thin type, fades | one accent, deep type, hard cuts, real props |

## Final ship checklist

- [ ] Duration matches the voice; last frame is intentional.
- [ ] 20–28 scenes for 60–90 s; no scene over 6 s without a new beat.
- [ ] Hook in 1.5 s; turn around 60–70 %; CTA with a verb.
- [ ] One accent family; max four backgrounds; brand lockup correct.
- [ ] Every number has a device; every prop does something.
- [ ] Cuts on word starts; no dead frames; camera push everywhere.
- [ ] Every reveal inspected at native size, mid-animation included.
- [ ] Captions synced, no duplicates, correct ZWNJ and Persian digits.
- [ ] SFX on every element; music sections on cuts; hard stop before the biggest reveal.
- [ ] Voice intelligible on phone; mix −14 LUFS, TP ≤ −1.
- [ ] MP4 specs + faststart; cover inside 3:4 crop; project folder saved.
