# Routes and bundled limits

This skill is a production guide plus a reusable 2D toolkit. Check available tools; do not promise an unavailable renderer or generation service. Work on generated project copies, keeping installed tools and the original skill intact.

## Bundled HTML/SVG route

Scaffold a fresh project with `scripts/init_reel.py`. Useful for type, vector explainers, data graphics, UI/product images and layered photos. Replace the demo for the approved style.

| Existing default | Required project-local adaptation |
| --- | --- |
| Persian blue poster scenes | New scenes, copy, palette, cover and imagery |
| RTL stage, `Y`, heavy weights | Actual language/direction/fonts and verified readiness |
| `scene` push/whip, automatic cut SFX, vignette | For restraint use `{push:0,tr:'cut',quiet:true,hits:[]}`, disable `.vig::after`; the legacy cut still adds a short colored/tear effect, so suppress `#world` filter and `#fx .tear` if unwanted |
| Word-index demo | Replace all W/WE accesses with actual words or direct times/beats |
| 1080×1920, 30 fps | Coordinate stage CSS, renderer W/H/FPS, engine FPS, mix fps, layout, cover and QA; stock width/fps flags do not exist |
| Image-only partial readiness | Await actual fonts/media; browser footage requires a separate seek adapter |
| Voice/music/SFX mix with visual finish | `--no-finish` for a clean image; different mix/encode for absent stems, footage audio or silence |

Do not require the user to accept defaults to avoid these edits. Check adapted contracts together. Engine-spec.md describes the old implementation; its blue transition accents, camera pushes and word-first recipes are not general creative requirements.

## Narrated work

Use authorized recordings; optionally tighten, transcribe in the selected language, align with an explicit lead, author scenes, export cues, supply/generate suitable sound, render and count frames, mix using the same lead and verify. The synth soundtrack and fast voice edit are optional. No TTS is shipped.

## Silent/music-led work

Use film seconds/beats, render continuous frames, then encode with selected audio or none. For the unchanged 30 fps convention, from the generated project root after creating `out/`:

```sh
ffmpeg -framerate 30 -i build/frames/f_%05d.jpg -c:v libx264 -pix_fmt yuv420p -an -movflags +faststart out/silent.mp4

ffmpeg -framerate 30 -i build/frames/f_%05d.jpg -i audio/music.wav -map 0:v:0 -map 1:a:0 -c:v libx264 -pix_fmt yuv420p -c:a aac -ar 48000 -shortest -movflags +faststart out/music-led.mp4
```

These are encode examples, not loudness-normalized masters. Supply enough music or deliberately pad/trim/fade it; `-shortest` can truncate the film. Adjust frame rate, color and audio targets to the real brief. Validate duration and playback.

## Footage/compositing

Use deterministic browser media integration, predecoded frames or available compositor/FFmpeg edits. Choose one master timeline, media trims, fps conversion and audio owner. See languages-and-assets.md. No browser video-seeking helper is bundled; this integration must be authored and tested per project.

## 3D/character/specialized work

Check for a suitable installed tool before proposing geometry/rigs/tracking/simulation. If unavailable, explain the dependency and offer a feasible 2D/2.5D interpretation only as an option the user can accept. Extruded type is not a general 3D renderer. Use external services only when available, authorized and within budget.

## Verify the chosen route

Inspect metadata with `ffprobe -v error -show_streams -show_format -of json <video>` and compare to the brief. Stock `qa.py` offers width/height overrides but still assumes 30 fps, H.264/AAC, audio and particular loudness/size checks. Use focused checks for silent, other-fps or different-format work rather than declaring those exports passed by an incompatible checker.

Check longest text, source-media crop, moving footage, native-size frames, transitions, repeatable seek, continuous frame sequence, actual duration and full playback. The style studies test two other 2D directions in the old engine; they do not prove every route is implemented.
