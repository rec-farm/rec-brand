# Agent notes: REC brand

This repo is the source of truth for the REC design system (DESIGN.md) and its generated assets. Read README.md for the layout. Everything here is used by other projects and by OpenDesign, so a change isn't done until those copies are in sync.

## Rules

- **Never hand-edit generated SVGs** (`logos/`, `illustrations/`, `sheets/`). Change `build.py` and rebuild.
- **Tokens start in the DESIGN.md front matter.** That YAML block ([DESIGN.md format](https://github.com/google-labs-code/design.md), alpha) is the source of truth for colors, the type scale, radii and spacing. Copies live in §3 (tables), §14 (Tailwind block) and the constants at the top of `build.py`. Change the front matter first, then all three copies. `scripts/check.py` compares them all against it.
- **Contrast is linted.** The front matter's `components` lists the text-on-background pairs (dark default, `-light` for Paper). Add one when you add a pair to §13.1. `check.py` runs `design.md lint` and prints any pair below AA.
- **Bump the version for any user-visible change.** That means the header version and date in DESIGN.md, plus a row in §17 Changelog.
- **Run `python3 scripts/check.py` before committing.** It must pass, or you must say why it doesn't (e.g. OpenDesign gets synced in the next step).
- Copy rule: write "R.E.C." in running text, never a bare "REC". The legal name is RECIAM SAS.

## Shipping a change

Use the `/brand-release` skill (`.claude/skills/brand-release/SKILL.md`), or follow the same steps by hand:

1. Edit DESIGN.md and/or `build.py`. For a token change, edit the front matter first, then §3, §14 and `build.py`.
2. Rebuild: `.venv/bin/python build.py` (setup is in the README).
3. Bump the version and add a changelog row.
4. Run `python3 scripts/check.py`. The tokens and design.md lint checks must pass. For a token change, also run `npx @google/design.md@0.4.0 diff <(git show vX.Y.Z:DESIGN.md) DESIGN.md` against the last tag and put the token changes in the changelog row.
5. Commit the source and the regenerated SVGs together, tag `vX.Y.Z`, then `git push --follow-tags`.
6. **Sync OpenDesign.** The brand is "REC Design System": project `brand-rec-design-system-5bae95`, brand `rec-design-system-5bae95`. Both live under `~/Library/Application Support/Open Design/namespaces/release-stable/data/`.
   - **Asset or build.py changes:** copy the changed files into `projects/brand-rec-design-system-5bae95/` at the same paths. Repo `DESIGN.md` goes to `context/input-DESIGN.md` in **both** that project folder and `brands/rec-design-system-5bae95/`. Re-imports read the brand-folder copy, so a stale copy there silently re-imports an old version. Copy with `cp`, not the MCP `write_file` tool: it needs the content inline, which is risky for big files like the 78 KB DESIGN.md. Then confirm OpenDesign sees the change with MCP `search_files`.
   - **Rule changes** (palette, type, logo rules, voice): OpenDesign also keeps derived copies (its own DESIGN.md, `brand.json`, generated tokens, kit pages). Its quick importer can't be trusted with our front matter: it reads any 3-character hex-like text (`500` in `{colors.purple-500}`) as a color. So after a re-import, run an AI refinement in the brand project (MCP `start_run`) telling it to regenerate those files from `context/input-DESIGN.md` only. Then check that its `brand.json` colors are all in our palette, and publish it with the daemon's `POST /api/brands/rec-design-system-5bae95/finalize` (body `{"projectId": "brand-rec-design-system-5bae95"}`; the port is whatever the `daemon-sidecar.mjs` process listens on). Finalize re-renders the kit pages and updates the design system that other OpenDesign projects use. Until then they keep the import's colors. Copy `logos/` and `fonts/` into the project before finalizing, since finalize copies them into the brand.
   - Rerun `scripts/check.py` until OpenDesign shows ✓.
7. Tell the user which downstream projects should pick up the new version: Paramtune, StillUp, and any other project whose `CLAUDE.md` points at this DESIGN.md.

**OpenDesign can get ahead of the repo.** People edit the brand inside OpenDesign too. If `check.py` reports files that exist only in OpenDesign, or a different `build.py`, pull those changes into the repo first (diff, review, rebuild, commit). Don't overwrite them.

## Later: generate the copies

The front matter is the single source, but §3, §14 and the `build.py` constants are still hand-kept copies that `check.py` verifies. If that gets painful (frequent palette changes), have `build.py` read the front matter for its constants and generate the §3 tables. Keep writing §14 by hand: `design.md export --format css-tailwind` outputs a flat `@theme` with no dark/Paper themes, no `data-product` accents and no font fallbacks, so it can't replace §14. Don't build this until it's needed.
