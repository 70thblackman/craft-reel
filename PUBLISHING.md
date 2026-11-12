# Publish the first version

Proposed repository: `70thblackman/craft-reel`. Proposed initial tag: `v0.2.0`.

This package has not been published by the preparation process. The final public upload requires the author's approval.

Before release, confirm that you own or may publish the included scripts, SVG illustrations and instructions under MIT, and that `70thblackman` is the desired copyright attribution. Review the excluded-assets notes and the local review report supplied separately. Keep the original ZIP, private source paths, recordings and unrelated project files outside this repository.

## GitHub website

1. Sign in as `70thblackman` and create a **public** repository named `craft-reel`.
2. Upload the **contents** of the prepared `craft-reel` folder, including `.gitignore`. `README.md`, `LICENSE` and `SKILL.md` should be at the repository root, not inside an extra nested folder. Do not upload the original archive or the separate local review report.
3. Review the file list, then commit with `Prepare Craft Reel v0.2.0`.
4. Use the description: `Portable AI skill for Persian motion graphics with coding agents: custom styles, Persian/English text, user fonts/media and a preserved local 2D toolkit.`
5. Suggested topics: `agent-skills`, `motion-graphics`, `persian`, `video`, `claude-code`, `codex`, `antigravity`, `qwen`.
6. Create a release tagged `v0.2.0`. Describe it as a first public source release; do not imply testing across every agent or model. A real video showcase can be added after its media rights are cleared.

## Git and GitHub CLI alternative

Run only from the prepared folder, after reviewing the contents and authorizing public publication. Requires Git and an authenticated GitHub CLI with permission to create repositories.

```sh
git init -b main
git add .
git diff --cached --stat
# Review staged files before committing.
git commit -m "Prepare Craft Reel v0.2.0"
gh repo create 70thblackman/craft-reel --public --source=. --remote=origin --push
git tag v0.2.0
git push origin v0.2.0
gh release create v0.2.0 --title "Craft Reel v0.2.0" --notes "Portable workflow expansion: portable skill, starter, rendering pipeline and usage documentation. Fonts, narration and unverified raster textures are not bundled. Cross-agent testing is pending."
```

If that repository already exists, inspect it first and choose the appropriate destination rather than overwriting its history. Update the README clone URLs if the final repository name differs.
