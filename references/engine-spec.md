> Scope: API and implementation of the unchanged legacy starter. Its stylistic defaults are optional; see production-routes.md before adapting language, media, dimensions, fps or audio.

# Engine spec — deterministic frame renderer

Every frame is a pure function of film time `t`. The renderer calls `window.seek(t)` and screenshots the page. If a frame is not reproducible from `t` alone, the pipeline breaks.

## Files and load order

`index.html`:

```html
<script>window.FILM_DURATION = 62.4;</script>
<script src="js/words.js"></script>
<script src="js/engine.js"></script>
<script src="js/art.js"></script>
<script src="js/art2.js"></script>
<script src="js/scenes.js"></script>
```

- `words.js` defines `window.WORDS` before `engine.js` reads it.
- `art.js` / `art2.js` define `ART` before `scenes.js` uses it.
- `DURATION = window.FILM_DURATION`. Scenes may extend to `DURATION + .5`; the renderer captures `round(DURATION * 30)` frames.
- The last scene's `b` should be `DURATION + .5` so the end card is not cut.

## Determinism contract

- `window.seek(t)` must fully redraw the frame from scratch. No CSS animations, no GSAP, no `requestAnimationFrame`, no `Date.now()`, no unseeded `Math.random()`.
- Randomness in layout: `hash(n)` (deterministic). Random-looking motion: sines of `t`.
- Only the active scene's `update` runs. All state must be derivable from `t` (and static data captured at build time).
- `window.ready` waits for all font weights and images; `seek` also awaits `document.fonts.ready`.

## Core API

| helper | contract |
|---|---|
| `scene(a, b, bg, build, opts)` | registers a scene; `build(cam, root)` returns `update(t, p)` |
| `sfx(t, kind, g)` | pushes `[t, kind, g]` into the cue list; call at top level |
| `cap(t, text)` | subtitle shown from `t` until the next caption; `""` hides |
| `mk(html, parent)` / `at(root, html)` | create a DOM node; `at` appends to root |
| `tf(node, o, x, y, s, r, extra)` | opacity/transform; hides at `o <= .002` |
| `line(root, cls, top, size, text, style)` | centered word line, returns `{n, w}` |
| `words(node, text)` | splits into `.wd > span`; `*word` gets `.brand` |
| `reveal(spans, t, w, dur=.2)` | word mask rise; `w` is a number or array of times |
| `pop(spans, t, w, dur=.14)` | blur→sharp scale-in |
| `P(t, a, b)` | clamped progress 0..1 |
| `E.out`, `E.out5`, `E.in`, `E.io`, `E.back`, `E.sine` | easing |
| `slam(t, t0, from, d)` | `{o, s}` for a scale slam |
| `drop(t, t0, d=.32)` | `{o, y, s}` with back bounce |
| `draw(el, p)` | dash-offset stroke for `pathLength="1"` |
| `fa(n)`, `faNum(n)` | Persian digits / grouped digits |
| `hash(n)` | deterministic 0..1 |

`scene` options:

```js
{ push = .05, tr = "whip", hits = [], quiet = false }
```

- `push`: camera scale from 1 → 1+push across the scene (`E.sine`).
- `tr`: `whip | whipL | punch | up | down | flash | cut`.
- `hits`: times (word-anchored) for camera shake, 24 px decaying over .35 s.
- `quiet`: suppress the automatic cut whoosh/hit. Use when the scene is entered on a held beat or you supply a custom cue.

At registration, `scene` automatically adds `sfx(a, "hit"|"whoosh", 1)` for `a > 0` unless `quiet`. Do not add a second whoosh for the same cut.

## Time and words

`WORDS` is `[[word, start, end], ...]` in film seconds.

```js
const W  = (i) => WORDS[i][1];
const WE = (i) => WORDS[i][2];
const S0 = (i) => W(i) - .04;   // scene cut / line start
```

- Cuts: `S0(i)`. Reveals: `W(i) - .05`.
- Impacts: the word that lands the idea, then use the same time in `hits` and `sfx`.
- Type is split per word, so every line has an index budget. Keep narration concise: 2.2–2.8 Persian words per second is dense; 1.8–2.2 is comfortable for explainers.
- When a line has more words than timings, `when(w, i)` reuses the last time. Pass an explicit array when the line runs long.

## Typical update

```js
return (t) => {
  propsIn(ps, t);                                  // enter + idle drift
  reveal(sub.w, t, [W(10), W(11), W(12)]);
  const s = slam(t, W(14) - .02, 1.7);
  tf(big, s.o, 0, 0, s.s);
  const n = Math.round(42 * E.out(P(t, W(11), W(14) + .2)));
  big.textContent = fa(n) + "٪";                    // guarded: only when n changes
};
```

Create DOM once in `build`; update only style/text in `update`. Guard `textContent` writes with a previous-value check when the element is large.

## Animation recipes

**Mask rise.** `reveal(spans, t, times)` — each span translates from 110 % inside `.wd` overflow. Keep `.wd` padding-bottom for descenders; `.pop .wd` removes the mask.

**Hard slam.** `const s = slam(t, t0, 1.7); tf(big, s.o, 0, 0, s.s);` paired with `hits: [t0]` and `sfx(t0, "impact"/"hit")`.

**Prop drop.** Create the prop, then `const d = drop(t, t0); tf(node, d.o, 0, d.y, d.s, -4);`. Add a slight idle drift after landing: `Math.sin(t * .9 + i) * 6`.

**Card cascade.** Rows/cells enter with 4–9 ms stagger and `E.out`; color/light each by `k < n`.

**Count-up.** `E.out(P(t, W(i), W(j)))`; target × eased progress; `fa(Math.round(...))`. The container slams at `W(i) - .02`.

**Draw-on.** For arrows, rings, ticks: `pathLength="1"` in the SVG, `pathLength` CSS dash and `draw(el, P(t, t0, t1))`.

**Typing.** `msg.slice(0, Math.round(msg.length * P(t, t0, t1)))`; blinking caret with `Math.floor(t * 4) % 2`.

**Camera shake.** `hits` are scene-level and applied to the camera. Add at most 1–2 per scene, at the slams.

## Transitions and layering

- The world enters with a blur/offset for .2 s, an accent/white split-shadow and a tear band. This is the house look; use it instead of crossfades.
- Scenes are full-bleed `.scene` with `overflow:hidden`. The camera scales 1→1.05–1.10, so keep critical content inside the central 95 %.
- DOM order is z-order. Backgrounds → props → device → text → overlays. Use `insertBefore` when a ring or shadow must sit under a phone.
- Put static rotations on a wrapper and animate the child, or pass rotation into `tf`; a CSS `transform` on the node will be overwritten by `tf`.
- Animations that move text within a masked line must keep the mask padding; test mid-animation (50 % through the rise), not just the settled frame.

## Captions and SFX

- `cap()` is global, not per scene. The last caption persists into the next scene until replaced. Clear it with `cap(t, "")` or set the next one at the cut.
- Never duplicate a caption with a hero line that says the same words. The caption is the spoken text; the hero is the poster text.
- `sfx()` must be called at top level, once per event. Calling it inside `update` pushes a cue every frame.
- SFX kinds available: `whoosh impact sub hit riser scratch notif cash projector pop pill tick key stamp rise swell scan shutter flip fall wave vhs door`.
- The score learns cuts from `cues.scenes`, so scene `a` values are the musical section boundaries. Keep them on word starts.

## Renderer

`node build/render.mjs`:

- `0 9999` — render a frame range into `build/frames/f_%05d.jpg`; skips existing frames > 2 KB, so rerunning resumes.
- `shot 1.2 3.4` — stills into `build/shots/s_<time>.jpg`.
- `sfx` — writes `build/cues.json` from `window.cues()`.
- `cover` — screenshots `cover.html` to `out/cover.png`.
- 1080×1920, deviceScaleFactor 1, JPEG q94, browser recycled every 200 frames.
- Chrome resolution: `CHROME_PATH` env, then standard Windows/macOS/Linux paths.
- `?render` is appended to the URL. Useful if you want to keep a debug overlay out of captures (`if (!location.search.includes("render"))`).

Frame count: `round(DURATION * 30)`. A 90 s film is 2,700 frames.

## Pitfalls

| symptom | cause | fix |
|---|---|---|
| phone content overflows the bezel | height set on the wrapper, not `.phone` | set width/height on the `.phone` element itself |
| element hidden behind a prop | DOM order | reorder, or `insertBefore` under the target |
| text clipped at the top/bottom | `.wd` mask / `.scene` overflow / camera push | add mask padding; keep inside 95 % center; check the mid-slam frame |
| static rotation jumps | CSS `transform` overwritten by `tf` | rotate a wrapper, animate the child, or pass `r` to `tf` |
| Persian text reversed in SVG | inherited `direction` | keep `direction:ltr` on the SVG; `text-anchor` is physical |
| a whole line animates as one | text not split into words | use `line()` / `words()` and animate spans |
| first frame has fallback type | fonts not loaded | `seek` awaits fonts; render after `window.ready` |
| cut whoosh doubled | manual cue + automatic `scene` cue | use `quiet: true` or drop the manual cue |
| cue fires every frame | `sfx()` inside `update` | move all cues to top level |
| captions linger | global caption state | set `cap(t, "")` or replace at the cut |
| black/blank frames survive a rerender | skipped by size > 2 KB | delete `build/frames/f_XXXXX.jpg` |
| render stops mid-run | Chrome crash | rerun the same range; it resumes |
| slow render | too much DOM / filters per update | fewer nodes, guarded text writes, no layout reads |

## DOM budget

- < 200 nodes per scene is comfortable; a 100-person grid is 100 small SVGs and still fine.
- Avoid per-frame `querySelector`; cache nodes in `build`.
- Avoid writing `innerHTML` every frame. Typewriter text and counters are the exceptions; keep strings short.
- `filter: blur()` on large layers during transitions is expensive but limited to .2 s. Do not leave large blurs on in settled frames.
- Use `textContent`, not `innerHTML`, for counters.
