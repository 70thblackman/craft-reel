> Scope: optional original poster preset. These style, language, framing and audio recipes are not universal requirements. Follow SKILL.md and the selected brief for other directions.

# Design language — the poster grammar

The film is a sequence of composed posters that move, not slides that fade. Every scene must survive a paused screenshot at native size.

## Canvas and safe zones

1080 × 1920, 30 fps. Margins 80 px on both sides; nothing meaningful outside x 60–1020.

| zone | y | use |
|---|---|---|
| slug | 0–170 | kicker, brand lockup, scene index; keep the top 90 px quiet |
| hero | 200–1100 | headline, stat number, hero prop, phone |
| proof | 1100–1450 | device, cards, supporting sentence, tag |
| CTA / caption | 1450–1700 | action line, caption pill sits at 1530 |
| bottom | 1700–1920 | keep 180 px clear; thumbnails and platform UI cover it |

The cover must work in the 3:4 profile crop: y 240–1680, x 0–1080.

Test composition at 270 px wide. If the hierarchy disappears, it is too subtle.

## Palette

One accent and its family, plus navy/paper neutrals, one gold, one signal red. Never let two accents compete.

Starter variables in `assets/starter/css/style.css`:

```
--brand #008efa   --brand-2 #0a6fd8   --brand-3 #0753a8   --brand-deep #06386f
--navy #0b1b33    --ink #101828       --muted #667085     --paper #f3f5f8
--sky #e6f3ff     --sky-2 #b9dcff     --gold #ffc23d      --signal #ff4d4d
```

Use `scripts/rebrand.py` to shift the whole accent family at once. Do not hand-pick a second blue.

## Background modes

Pick four and give them a narrative arc:

| class | look | when |
|---|---|---|
| `bg-grid` | graph-paper daylight, thin accent lines | proof, numbers, calm clarity |
| `bg-paper` | CSS paper-colored background; optional licensed texture | documents, receipts, editorial asides |
| `bg-desk` | radial accent light + grain | hook, hero props, emotional beats |
| `bg-navy` | deep night gradient | the turn, doubt, night-time worry |
| `bg-brand` | flat accent | CTA and brand statements only |

A proven arc: desk hook → grid proof → navy turn → brand CTA. Another: grid → paper → desk → brand. Use `bg-brand` once, at the end.

Each scene gets `.vig` (vignette) and often `.grain` on the background element; the grade in `mix.py` adds the rest.

## Type

Use one properly licensed Persian family under the CSS alias `Y`, with 6+ weights where available. The public starter uses local system fonts and simulated weights for preview only. No font binaries are included; configure a licensed family before final layout QA. Persian line-height 1.45, letter-spacing 0. Latin kickers may use `.lat` and letter-spacing.

| role | size | weight | notes |
|---|---|---|---|
| kicker / slug | 36–46 | 700–800 | often accent, `.lat` or letterspaced Persian |
| subline | 56–72 | 300–500 | light against a heavy hero |
| hero word | 140–260 | 900–950 | one line, 3–6 words max |
| stat number | 240–380 | 950 | digits + `٪`, count-up |
| tag / stamp | 48–64 | 800–950 | white pill, rotated sticker |
| caption pill | 38 | 700 | bottom, max 900 px wide |

Rules:

- Display type is physical. Use `ext(side, depth, ring, ringW)`; the default starter look is a white face with a deep accent side on dark, or an accent face with a white ring on light. A display line without depth must be a deliberate sticker instead.
- Never mix a thin display face with a heavy one in the same line.
- Persian digits via `fa()` / `faNum()`. ZWNJ in `می‌شود`, `به‌خاطر`, `نمی‌شود`.
- Split words with `line(root, cls, top, size, text)` so each gets a `.wd` mask; animate the spans.
- The hero and the caption must not say the same thing. The caption carries the spoken sentence; the hero carries the turn.

`ext` signature:

```js
ext(side = "#0753a8", depth = 14, ring = "", ringW = 0, cast = "rgba(0,20,60,.45)")
```

Build a big style once per film:

```js
const BIG = (size, light = false) => light
  ? `font-weight:950;font-size:${size}px;line-height:1.2;color:#008efa;${ext("#06386f", Math.round(size/16), "#fff", Math.max(6, size/30))}`
  : `font-weight:950;font-size:${size}px;line-height:1.2;color:#fff;${ext("#06386f", Math.round(size/16))}`;
```

## Composition recipes

Each scene needs 4–12 elements: one hero, one supporting device, 2–4 props, one text hierarchy. Empty margins are fine; empty scenes are not.

**1. Hook on the desk.** Hero prop (wallet, envelope, grocery bag, phone) at 300–550 px, two short lines below, 3–5 small props scattered with `±14°` rotations. One prop may drop or open.

**2. The number and the crowd.** Stat number top, human sentence below, a physical device behind/under it. For percentages, the 100-person grid is the strongest device: each person lights in accent as the count rises. Alternative: donut `ART.donut`, pie with a pulled slice, receipt stack, order cards.

**3. Phone proof.** One phone position reused for every phone scene (`PH`). Screen content is real DOM inside `.phone .scr`: mini cards, toggles, a progress bar, payment-plan rows. Tags/callouts pinned around it with connectors. Never put a phone in a different place per scene.

**4. Contrast.** Split frame or two objects: one accent, one navy/grey. A cross (`ART.cross`) over the rejected option, a check (`ART.check`) on the accepted one. Use red only here.

**5. Mechanism.** Three steps left-to-right or top-to-bottom, connected by dotted arrows; each step is an icon chip + one word + one micro-line. Build the arrow with an SVG path and `draw()`.

**6. Quote / comment.** White comment bubble with a name handle, a big quote mark, one accent word. Useful for social proof without fake logos.

**7. Receipts and cards.** Use `ART.receipt(w, rows)` for installments, fees and comparisons. The rows are data; animate each row in with a 40 ms stagger.

**8. CTA.** Brand background, enormous line (200–260 px), one input/comment box that types a message, one arrow. No props crowd the CTA.

The last scene is 3–5 s of one clear action: comment, swipe, save, answer. Do not end on a logo alone.

## Props

Hand-drawn SVG only (`js/art.js`, `js/art2.js`), never stock icons.

- Thick rounded strokes (4–7 px), 2–3 tones of the accent, one gold, one signal red.
- 300–600 px for heroes, 60–180 px for scatter. Rotate ±3–14°. Shadows via `.shd` (midground) or `.sh` (small).
- Out-of-focus edge props: `filter: blur(7px)`, low detail, placed partly off-canvas.
- A prop must be doing something: opened, dropped, checked, circled, counted. Static decoration only at the edges.
- Build new props as SVG functions with `viewBox`, `pathLength="1"` on strokes you want to draw on, and a class (`flap`, `arc`, `row`, `k`) for the parts you animate.
- Give every prop a physical anchor on the canvas (a desk line, a card edge, a phone). Floating props read as stickers.

## Motion grammar

Everything is a function of film time. No transitions over 0.45 s.

| move | duration | use |
|---|---|---|
| mask rise (`reveal`) | 0.18–0.22 | every line of type, word by word |
| pop blur→sharp | 0.14 | short punch words, labels |
| slam | 0.12 | numbers, verdicts, one per scene |
| drop with back bounce | 0.30–0.36 | props, cards, phones |
| counter | 0.6–1.2 | numbers, one easing `E.out` |
| draw-on stroke | 0.3–0.8 | arrows, circles, checkmarks |
| typing | 0.4–0.7 | comment box, search, CTA input |
| hit shake | 0.35 | impacts; 24 px, decaying, camera only |
| camera push | scene-length | 3–10 % every scene, `E.sine` |

Stagger words 60–90 ms. Stagger rows/cells 4–9 ms for cascades. Nothing should start moving after the narration has finished the phrase.

Words start on `W(i) - .05`; cuts land on `W(i) - .04`. Sound follows the same clock.

## Transitions

| tr | motion | use |
|---|---|---|
| `whip` | 760 px horizontal + 16 px blur | default between ideas |
| `whipL` | same, other direction | alternating rhythm |
| `punch` | scale 1.28→1 + blur | stat reveals, hard claims |
| `up` / `down` | 900 px vertical | escalation / falling back |
| `flash` | white flash + cut | one or two maximum per film |
| `cut` | hard, no blur | deadpan jokes, abrupt verdicts |

All transitions include an accent/white split-shadow and a tracking tear. Do not add slow crossfades or dissolve transitions.

## Numbers as devices

Never show a number without a body:

- **Percent:** 100-person grid, ring/donut, pie with pulled slice, or a giant `٪` with the figure extruded.
- **Money:** receipt, price tags, order cards, wallet with notes.
- **People:** person grid or avatar cluster; light them in accent, leave the rest grey.
- **Time:** calendar with crossed days, clock, countdown chips.
- **Comparison:** two receipts, two phones, a scale (`ART.scale`), before/after cards.

Count-up rule: `n = Math.round(target * E.out(P(t, W(i), W(i) + 0.9)))`, display `fa(n)`. Slam the container at `W(i) - .02`. Pair with `sfx` ticks at 90 ms or a single cash/stamp.

## Captions

`cap(t, text)` shows from t until the next caption. Keep one line, max 900 px, 38 px. The caption is the spoken subtitle, not a second headline. Empty string hides the pill. Verify no duplicate with the hero line.

## Cover

One idea, readable at 270 px.

- Deep/spotlight background, 3–6 props, one big headline (2 lines max), one sticker subline, one stat, brand lockup, footer.
- Keep everything inside y 240–1680. The bottom 240 px of a 9:16 cover is cut by profile grids.
- Headline stack: 130–170 px lines, depth 12–14; sticker 54 px white strip rotated −2°, no wider than 920 px.
- The stat lives opposite the hero prop, not on top of it.
- No collage of 5 ideas. No tiny text.

## Do / don't

| do | don't |
|---|---|
| one hero prop + 3–8 supporting elements | a lone line of text on a flat background |
| one accent + deep family | five pastel colors |
| extruded or sticker display type | flat 40 px body type as a headline |
| word-anchored reveals | eyeballed animation delays |
| 3–5 scene backgrounds across the film | a new gradient every scene |
| props that get used | floating decoration |
| camera push + hit shake | static frames |
| 4–12 elements per scene | 20 props burying the message |
| captions in the safe zone | text under platform UI |
| correct ZWNJ and Persian digits | Latin digits in Persian copy |
