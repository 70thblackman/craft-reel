# Languages, fonts and supplied media

## Language

Select screen, narration and caption languages separately. Preserve supplied copy unless translation is requested. Set page `lang`/direction (`fa`/`rtl`, `en`/`ltr`) and override per block. Isolate embedded Latin names, handles, currency codes and numerals with `<bdi>` or `unicode-bidi:isolate`. Never reverse strings. Use intentional line breaks/hierarchy for bilingual text.

Keep Persian letter spacing zero; check joining, ZWNJ, ی/ک, punctuation and diacritics. English uses its requested numeral convention. The legacy `fa()`/`faNum()` functions explicitly convert digits: call only when appropriate. Preserve numeric source values.

## Fonts

Use the supplied fonts and actual weights. Check Persian/Latin glyph coverage; do not assume every family supports both or all weights from 100 to 950. A static bold file must not be declared as a full variable-font range. Define accurate `@font-face` entries, await loading, then fit the actual text at final size. Check descenders, shadows, long words and caption wrapping.

The old engine waits on family `Y`. If using another name, extend the generated project's `window.ready` to await its real fonts/assets and ensure `seek` awaits them. Readiness is not proof of glyph coverage: inspect rendered samples. Font binaries are not bundled; local system fallback is only a prototype. Follow supplied usage/redistribution terms without assuming missing embedded license metadata means the user lacks rights.

## Inventory and originals

Keep a project-local table: original path, working copy, kind, dimensions/duration, crop/in-out, source audio choice and usage constraints. Preserve originals. Do not commit private client assets to the public skill repository.

- Photos/logos: check resolution/transparency and intended crop; avoid stretching logos.
- SVG: inspect scripts, foreign objects and remote references before inlining; use a safe/rasterized copy if needed.
- Video: use ffprobe for duration, fps, codec, rotation, dimensions and audio. Decide trim/retime/crop/source-audio behavior. Transcode a copy for unsupported codecs.
- Audio: inspect duration, channels, level and intended narration/music/source-audio role.

Use `textContent` for plain text and DOM properties for URLs. Existing `mk`, `line`, `words` and `cap` helpers expect trusted authored markup. Escape user strings before interpolation. Pass file paths as separate process arguments, including paths with spaces/Persian characters/apostrophes.

## Deterministic footage

The starter does not seek video elements. For browser footage, author an async project-local seek adapter: await metadata, map film time to clamped clip time, seek active clips and await the decoded frame before capture. Define freeze/loop/end behavior. Do not use `play()` as the offline render clock. Test forward/backwards/repeated seeks and multiple clip times.

Alternatively, predecode footage frames or use FFmpeg/compositor layers with one known timeline. Plan storage and audio ownership. A paused video poster is not a successful footage test.

## Narration

The ASR helper already accepts language flags:

```sh
python build/asr.py --engine whisper --lang fa --input narr/voice_edit.wav --out narr/words.json
# OR for English:
python build/asr.py --engine whisper --lang en --input narr/voice_edit.wav --out narr/words.json
```

For mixed speech use reviewed manual timings or separate language segments with offsets, checking boundary words. Vosk needs a matching model. ASR is not TTS. The same word/start/end structure works for English and Persian; use matching explicit `--lead` values for alignment and mixing.

Preserve meaningful pauses/breaths for calm or cinematic work; the aggressive old tightening recipe is optional. With no narration, use scene/beat timing. An empty `window.WORDS` is fine only if all authored scenes avoid word indices. Use an appropriate silent/music-led encode instead of fake narration files.
