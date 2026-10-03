---
name: brand-release
description: Ship a change to the REC design system. Covers version bump, rebuild, token consistency check, commit and tag, OpenDesign sync, and downstream heads-up. Use after editing DESIGN.md or build.py, or when the user asks to release, publish, tag or sync the brand.
---

# Brand release

Ship the current brand change end to end, following "Shipping a change" in AGENTS.md. Notes per step:

1. **Check for OpenDesign drift first.** Run `python3 scripts/check.py`. If OpenDesign has files or a `build.py` the repo lacks, show the user the diff and ask whether to pull them in before releasing. Never overwrite OpenDesign-only work without asking.
2. **Review the change.** Run `git diff`. If a color changed, confirm DESIGN.md §3, §14 and the `build.py` constants all agree.
3. **Rebuild** with `.venv/bin/python build.py`. Create the venv first if it's missing (see README).
4. **Version.** Pick patch, minor or major from the change (new assets or rules = minor; fixes = patch; renames or breaking rules = major). Confirm with the user. Update the DESIGN.md header (version and date) and add a §17 changelog row.
5. **Run `python3 scripts/check.py`.** The tokens check must pass. OpenDesign may fail until step 7.
6. **Commit** the source and the regenerated SVGs together. Tag `vX.Y.Z` and push with `--follow-tags`.
7. **Sync OpenDesign** (project `brand-reciam-design-system-9c50f8`). `cp` each changed file into the project folder (path in AGENTS.md), with repo `DESIGN.md` going to `context/input-DESIGN.md`. Then confirm with OpenDesign MCP `search_files` (e.g. the new version string). If rules changed (palette, type, logo, voice), tell the user to re-import the brand in the OpenDesign app, since that regenerates its derived DESIGN.md, tokens and memory rules. Rerun `scripts/check.py`.
8. **Report** the version, the tag, the check results, and which downstream projects should pick up the change.
