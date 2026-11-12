# Examples

- [Project brief](brief-template.md): language, style, user assets and delivery choices; an agent/human checklist, not machine config.
- [Prompts](prompts.md): portable examples for coding agents.
- [Minimal bilingual study](style-studies/minimal.html): Persian/English, flat type, whitespace, no narration, music, camera push or extrusion.
- [English collage study](style-studies/collage.html): layered illustration, multiple colors, English typography, quiet motion and no narration.

Open either HTML in a desktop browser for a settled preview at 3 seconds. These pages are 6-second deterministic scene studies, not full video players. A coding agent can call `await window.ready; await window.seek(t)` before capturing frames. They load the **unchanged** engine from the package by relative path, so keep the repository structure intact. Use a viewport of 1080×1920. The original poster starter remains in `assets/starter/`.

To make a video, scaffold a separate project and adapt its scenes/styles from the study; author the matching frame capture and audio/silent encode as described in production-routes.md. The stock renderer opens index.html/cover.html in the current video project; it does not accept these HTML paths as a CLI mode.

Fonts in the studies are system fallbacks, not redistributable production fonts. The collage uses a small original SVG illustration; it does not bundle a stock photo or prove footage seeking. Replace its image through a working copy of the user's supplied file when making a real film. Tests and documented directions do not imply all agents or models have been tested.
