# Agent notes: REC brand

This repo is the source of truth for the REC design system (DESIGN.md) and its generated assets. Read README.md for the layout. Everything here is used by other projects and by OpenDesign, so a change isn't done until those copies are in sync.

## Rules

- **Never hand-edit generated SVGs** (`logos/`, `illustrations/`, `sheets/`). Change `build.py` and rebuild.
- **Tokens live in three places.** A color has to match in DESIGN.md §3 (tables), DESIGN.md §14 (Tailwind block) and the constants at the top of `build.py`. If you change one, change all three. `scripts/check.py` checks build.py against §14. It doesn't read §3, so check that table by eye.
- **Bump the version for any user-visible change.** That means the header version and date in DESIGN.md, plus a row in §17 Changelog.
- **Run `python3 scripts/check.py` before committing.** It must pass, or you must say why it doesn't (e.g. OpenDesign gets synced in the next step).
- Copy rule: write "R.E.C." in running text, never a bare "REC". The legal name is RECIAM SAS.

## Shipping a change

Use the `/brand-release` skill (`.claude/skills/brand-release/SKILL.md`), or follow the same steps by hand:

1. Edit DESIGN.md and/or `build.py`, keeping the three token copies in sync.
2. Rebuild: `.venv/bin/python build.py` (setup is in the README).
3. Bump the version and add a changelog row.
4. Run `python3 scripts/check.py`. The tokens check must pass.
5. Commit the source and the regenerated SVGs together, tag `vX.Y.Z`, then `git push --follow-tags`.
6. **Sync OpenDesign.** The brand project is "RECIAM Design System Design System" (`brand-reciam-design-system-9c50f8`).
   - **Asset or build.py changes:** write the changed files into the project with the OpenDesign MCP `write_file` tool, at the same paths. Repo `DESIGN.md` goes to `context/input-DESIGN.md`.
   - **Rule changes** (palette, type, logo rules, voice): OpenDesign also keeps derived copies (its own DESIGN.md, `brand.json`, generated tokens, brand memory rules). Re-import the brand in the OpenDesign app so it regenerates them, then rerun the check.
   - Rerun `scripts/check.py` until OpenDesign shows ✓.
7. Tell the user which downstream projects should pick up the new version: Paramtune, StillUp, and any other project whose `CLAUDE.md` points at this DESIGN.md.

**OpenDesign can get ahead of the repo.** People edit the brand inside OpenDesign too. If `check.py` reports files that exist only in OpenDesign, or a different `build.py`, pull those changes into the repo first (diff, review, rebuild, commit). Don't overwrite them.

## Later: emit tokens from one source

Tokens are hand-kept copies for now (see above). Once that becomes painful (frequent palette changes, or a project caught running an old palette), move them into `tokens.json` and have `build.py` read it and also write `tokens.css` (the §14 Tailwind block) for projects to copy. Then `check.py`'s token check can go. Don't build this until it's needed.
