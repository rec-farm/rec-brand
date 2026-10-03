---
name: brand-release
description: Ship a change to the REC design system. Covers version bump, rebuild, token consistency check, commit and tag, OpenDesign sync, and downstream heads-up. Use after editing DESIGN.md or build.py, or when the user asks to release, publish, tag or sync the brand.
---

# Brand release

Ship the current brand change end to end, following "Shipping a change" in AGENTS.md. Notes per step:

1. **Check for OpenDesign drift first.** Run `python3 scripts/check.py`. If OpenDesign has files or a `build.py` the repo lacks, show the user the diff and ask whether to pull them in before releasing. Never overwrite OpenDesign-only work without asking.
2. **Review the change.** Run `git diff`. If a token changed, it must change in the DESIGN.md front matter first and then in §3, §14 and `build.py`. For a token-level summary, run `git show $(git describe --tags --abbrev=0):DESIGN.md > /tmp/prev-DESIGN.md && npx @google/design.md@0.4.0 diff /tmp/prev-DESIGN.md DESIGN.md` (a real file, not `<(...)`, which reads as empty). Use it for the changelog row and mention any `regression`.
3. **Rebuild** with `.venv/bin/python build.py`. Create the venv first if it's missing (see README).
4. **Version.** Pick patch, minor or major from the change (new assets or rules = minor; fixes = patch; renames or breaking rules = major). Confirm with the user. Update the DESIGN.md header (version and date) and add a §17 changelog row.
5. **Run `python3 scripts/check.py`.** The tokens and design.md lint checks must pass. Report any new `!` contrast warnings to the user. The known ones are listed in §13.1 "Known limits". OpenDesign may fail until step 7.
6. **Commit** the source and the regenerated SVGs together. Tag `vX.Y.Z` and push with `--follow-tags`.
7. **Sync OpenDesign** (project `brand-rec-design-system-5bae95`, brand `rec-design-system-5bae95`). `cp` each changed file into the project folder (paths in AGENTS.md). Repo `DESIGN.md` goes to `context/input-DESIGN.md` in both the project and brand folders. Then confirm with OpenDesign MCP `search_files` (e.g. the new version string). If rules changed (palette, type, logo, voice), follow the re-import plus AI refinement steps in AGENTS.md, and check the result's colors against the front matter. Rerun `scripts/check.py`.
8. **Report** the version, the tag, the check results, and which downstream projects should pick up the change.
