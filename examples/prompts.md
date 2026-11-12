# Example briefs

## Minimal bilingual, custom fonts and images

```text
Read Craft Reel. Use my Persian and English font files and supplied photos
to make a 20-second bilingual film. Match the attached minimal editorial
reference: flat type, whitespace and restrained movement. Output 16:9,
music-led with no narration. Preserve source files. Check the tools and
format adaptations, then show storyboard/style frames before the full build.
```

## English footage-led film

```text
Use Craft Reel with the supplied product footage, logo and English font.
Make a 30-second landscape product film with calm titles and the licensed
music I supplied. Keep source audio only for the opening shot. Inspect the
clips, propose trims and deterministic compositing, and show the direction
before rendering. Do not substitute illustrated props for the real product.
```

## Specialized style with a tool check

```text
Use Craft Reel to plan a true 3D product animation from my model and reference.
Check whether an appropriate renderer is installed before promising a result.
If it is unavailable, explain what is missing and offer alternatives for me
to choose. Do not silently replace the request with 2D extruded typography.
```

These are prompts and input examples, not claims of completed productions. First point your agent to the installed `SKILL.md`, or invoke its native skill command. Use a new video project folder.

## Any coding agent

```text
Read path/to/craft-reel/SKILL.md. Use the bundled engine and scripts to create
a 30-second Persian vertical motion-graphics film about turning knowledge
into action. Audience: people who keep saving tutorials but do not practice.
Accent: orange. Use illustrated props and kinetic type, no presenters or
generated human faces. No invented statistics. Propose the script/storyboard
first. Deliver MP4, cover, contact sheet and editable project after approval.
Check local dependencies and report any unavailable tools accurately.
```

## A research-led brand film

```text
Use Craft Reel to create a 60-second Persian 9:16 film explaining our supplied
annual report. Use only figures from the attached report and keep a source
list. Audience: our customers. Accent: our supplied brand blue. I will provide
authorized narration and logos. Propose the script and storyboard before
building. Keep the final result editable and verify the export on a phone.
```

## Revise an existing film

```text
Read Craft Reel and the existing video project. Change the CTA to the supplied
Persian sentence, retain the existing palette, and update the word timings,
cover and sound cues where affected. Show layout stills before the full render.
Invalidate only the affected cached frames and rerun mix and QA.
```

## Manual timings without ASR

Save recognized or manually authored narration-relative timings as JSON:

```json
[
  {"word": "از", "start": 0.0, "end": 0.2},
  {"word": "دانستن", "start": 0.2, "end": 0.6},
  {"word": "تا", "start": 0.6, "end": 0.8},
  {"word": "انجام‌دادن", "start": 0.8, "end": 1.4}
]
```

Run `python build/align_words.py --words narr/words.json --lead 0.10`. Then write scenes for those words: the stock demo references 20 words and cannot be used unchanged with this four-word example. Pass `--lead 0.10` to mixing too. Narration audio must still be supplied for the narrated MP4 pipeline.
