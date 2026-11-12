# Craft Reel

**A portable AI skill for making motion graphics from your idea, style references, language and media.**

Use Craft Reel with a coding agent to plan and author a film in the requested direction: minimal, kinetic typography, vector explainer, data story, product/UI, collage, footage-led edits or another feasible style. Supply your own fonts, logos, photos, video and audio. Persian, English and mixed layouts are first-class brief choices. Output format, pacing and sound follow your project rather than a mandatory vertical Persian template.

The skill is model-independent: Codex, Claude Code, Antigravity, Qwen Code and environments powered by DeepSeek or other models can use its instructions if they can read files, write code and run the needed tools. A chat-only model cannot render a video by itself. Cross-agent end-to-end testing is pending.

## What v0.2 adds

- A general brief → direction → route → production → QA workflow in `SKILL.md`.
- Style-reference analysis and scoped direction families, without compulsory extrusion, one accent, narration or a CTA.
- Persian/English/mixed typography and supplied-font/media guidance.
- Explicit route selection for 2D, footage and specialized work, including tools the agent must supply or author.
- Two runnable [contrasting style studies](examples/README.md), a brief template and portable prompts.
- The original toolkit and Persian poster starter, preserved as an optional direction. All ten existing scripts and all original starter files are byte-for-byte unchanged from the v0.1 public package.

### What is actually bundled

The supplied engine renders authored HTML/SVG 2D scenes. Its existing tools default to 1080×1920/30 fps and a narrated three-stem mix. The new general skill instructs the agent how to adapt **generated project copies** or select a different available pipeline. It does not introduce universal format flags, an automatic style-transfer model, TTS, a browser video-seeking adapter, a 3D renderer or a character rig. Those routes need suitable project code/tools and testing; do not read style guidance as proof every route is preimplemented.

The original 12.5-second, three-scene demo and its 42% figure are fictional templates. Font binaries, unverified raster textures, voices and orchestral samples are not bundled. See [asset notes](THIRD_PARTY_NOTICES.md).

## Choose your project

Provide a description or reference, screen/narration/caption languages, fonts/media, duration, format and sound preference. The agent should inspect supplied assets, propose a storyboard/style frames, and check tools before committing to a renderer. See [the brief](examples/brief-template.md), [style guide](references/style-selection.md), [language/media guide](references/languages-and-assets.md) and [routes](references/production-routes.md).

## Install in your coding assistant

Keep the folder intact: copying only `SKILL.md` loses the engine, scripts and references. For a project-scoped installation, copy this entire repository into the appropriate directory:

| Host | Project location | Personal location | Use |
| --- | --- | --- | --- |
| Codex | `.agents/skills/craft-reel/` | `~/.agents/skills/craft-reel/` | Mention `$craft-reel` |
| Claude Code | `.claude/skills/craft-reel/` | `~/.claude/skills/craft-reel/` | Invoke `/craft-reel` |
| Google Antigravity | `.agents/skills/craft-reel/` | `~/.gemini/config/skills/craft-reel/` | Ask it to use Craft Reel |
| Qwen Code | `.qwen/skills/craft-reel/` | `~/.qwen/skills/craft-reel/` | Ask it to use Craft Reel |
| Other agents, including DeepSeek/Qwen-powered environments | Any readable folder, such as `tools/craft-reel/` | Host-specific | Give the agent the path to `SKILL.md` |

`~` means your user directory. Older host versions may use different locations. Avoid installing duplicate copies with the same skill name. These are documented discovery conventions, not a claim of successful testing in every host.

From your project root, choose one installation location:

```sh
# Codex / Antigravity project installation
git clone https://github.com/70thblackman/craft-reel.git .agents/skills/craft-reel

# OR Claude Code project installation
git clone https://github.com/70thblackman/craft-reel.git .claude/skills/craft-reel

# OR Qwen Code project installation
git clone https://github.com/70thblackman/craft-reel.git .qwen/skills/craft-reel
```

To install from a downloaded ZIP, extract it and copy its `craft-reel` folder to one of these locations. Refresh skills or restart your host if it does not appear.

### Universal prompt

```text
Read tools/craft-reel/SKILL.md and follow it. Make a 20-second minimal
motion-graphics video with English/Persian text, my supplied fonts and photos,
in 16:9. Use the attached style reference, restrained transitions and music
without narration. Keep my original files unchanged. Check available tools,
propose the storyboard and style frames, then build after approval.
```

Replace the path with your installed folder. Hosts without native skills can use this explicit-file approach when they have file/execution access, or a human runs the commands.

## Local toolchain

Installing the skill does not install its rendering dependencies.

| Requirement | Purpose |
| --- | --- |
| Python 3.10+ | Pipeline scripts; use a virtual environment |
| Node.js 20+ and npm | Renderer and `puppeteer-core` dependency |
| Google Chrome or Chromium | Headless frame capture; browser not downloaded by `puppeteer-core` |
| FFmpeg and ffprobe on `PATH` | Audio editing, loudness measurement and MP4 encoding; requires libx264/AAC support |
| NumPy and Pillow | Synthesized score/SFX and contact sheets |
| Optional `faster-whisper` or `vosk` | Local speech recognition for narration timings |
| A properly licensed Persian font | Production typography; system fallback is preview-only |

These versions are suggested baselines, not a tested support matrix. The scaffold currently declares `puppeteer-core` as `^24.0.0`. Keep the generated `package-lock.json` in your own video project for reproducibility.

Create a fresh video project outside the installed skill folder:

```sh
python "path/to/craft-reel/scripts/init_reel.py" my-reel
cd my-reel
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell, or `source .venv/bin/activate` in a POSIX shell. Then:

```sh
python -m pip install numpy pillow
npm install
ffmpeg -version
ffprobe -version
```

For Whisper transcription, optionally run `python -m pip install faster-whisper`. This can download a model on first use. Vosk requires `python -m pip install vosk` and a separately obtained compatible model directory. Manual word timings are also supported; ASR is optional.

If browser detection fails, set `CHROME_PATH` to your browser executable. In PowerShell: `$env:CHROME_PATH = 'C:\path\to\chrome.exe'`. In a POSIX shell: `export CHROME_PATH='/path/to/chromium'`.

## Preview the starter

Run from the generated video project's root:

```sh
node build/render.mjs shot 2 6 11
python build/contact_sheet.py build/shots build/sheet.jpg 3
node build/render.mjs cover
node build/render.mjs sfx
python build/score_synth.py
```

This creates stills, a cover, cue data and music/SFX stems. A finished narrated MP4 additionally needs voice audio and rendered frames.

### Production fonts and textures

The original upload contained eight IRANYekan fonts and two raster textures without accompanying redistribution terms. They are excluded from this public edition. The starter uses local system fonts and CSS backgrounds instead, so its appearance differs from the original package.

Before final layout QA, configure a Persian font you are allowed to use as the `Y` family in `css/style.css`. For example, after putting a properly licensed font at `fonts/Persian-Bold.woff2`:

```css
@font-face {
  font-family: Y;
  src: url('../fonts/Persian-Bold.woff2') format('woff2');
  font-weight: 700;
}
```

Map the other available weights too; the design uses weights from 100 to 950. Local system fallback cannot reproduce those weights reliably. In the preparation smoke check, the stock CTA headline clipped horizontally with the fallback font: the fallback is not production-ready typography. Adjust text sizes and rerun visual QA after configuring the production font. Do not redistribute paid fonts or unverified media merely because this repository is MIT-licensed. See [third-party asset notes](THIRD_PARTY_NOTICES.md).

## Make the film selected by the user

Start with `SKILL.md`, not with the old demo's narrative or style. Choose the route using [production-routes.md](references/production-routes.md). The existing scaffold and preview commands above exercise the original toolkit; they do not select a style or automatically change its format.

For the original narrated Persian poster route, see [the optional preset](references/poster-preset.md) and its audio/playbook links. For English ASR use `--lang en`; Persian uses `--lang fa`. Review bilingual speech and timings explicitly. For silent/music-led work, skip narration tools and author an appropriate encode. For footage, implement deterministic media timing rather than capturing real-time playback.

The bundled renderer, engine, mix and QA scripts retain their defaults. Other dimensions/fps require coordinated changes in the generated project. Stock QA assumes 30 fps and audio; use brief-matched checks for other deliveries. Do not claim all styles are instantly available through a config file.

## Operational limitations

- Run the copied `build/` scripts from the video project root, not from this repository. `mix.py` and `qa.py` derive their root from the script location.
- Use the same explicit `--lead` for alignment and mixing. Automatic lead inference uses the first word's film timestamp and can over-delay narration containing initial silence.
- Frames are cached by filename/size. Remove affected generated frames before rendering changed scenes. A failed render chunk can still exit with status zero; verify a continuous sequence of `round(duration * 30)` frames before mixing.
- Scene helpers insert HTML/SVG strings into the DOM. Use trusted authored copy; this is not a safe renderer for arbitrary untrusted HTML.
- Rendering opens local pages with file access enabled. Treat scene JavaScript as executable code. There is no hosted rendering service or built-in telemetry client in the reviewed package.
- `--force` scaffolding overwrites matching files; use a fresh folder. Other pipeline steps overwrite their generated audio/images. QA removes earlier `qa_*.jpg` files in its selected output directory.
- The original poster recipes in design-language.md, narration-and-score.md and production-playbook.md are optional; they must not override other selected styles.
- The orchestral route in the references is optional guidance. Its sampler, samples and orchestral scripts are not included.
- Exact results depend on the model, agent host, browser, fonts and local dependencies. No claim is made that all named models/hosts have been tested.

## License and author

Prepared for publication by **70thblackman** under the [MIT License](LICENSE). MIT permits reuse, modification and commercial use while requiring preservation of its copyright and license notice. External dependencies and user-supplied fonts, voices, logos and media retain their own terms. The publisher must have the right to license the included source.

Installation references: [Codex](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills), [Antigravity](https://antigravity.google/docs/skills), [Qwen Code](https://github.com/QwenLM/qwen-code/blob/main/docs/users/features/skills.md). License reference: [MIT](https://choosealicense.com/licenses/mit/).
