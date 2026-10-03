# REC brand

The design system and brand assets for every REC product (Paramtune, StillUp and whatever comes next). Owned by RECIAM SAS. Private.

- **[DESIGN.md](DESIGN.md)**: the spec. It covers principles, logos, color, type, layout, components, voice, accessibility and Tailwind v4 tokens. Start here.
- **`build.py`**: generates every SVG below from shared geometry and tokens. Don't hand-edit the output.
- **`logos/`**: marks, lockups, micro marks, favicons and app icons per product, in `ink` and `cream` colorways.
- **`illustrations/`**: page headers, empty states and the motif kit.
- **`sheets/`**: overview sheets (logo family, mark construction, app icons, illustrations).
- **`fonts/`**: Archivo, Figtree and Geist Mono (all SIL OFL). `build.py` uses them to outline wordmarks.

## Rebuild

```sh
python3 -m venv .venv && .venv/bin/pip install fonttools
.venv/bin/python build.py
```

Commit the regenerated SVGs together with the change that produced them. Before committing, run `python3 scripts/check.py` (token consistency + OpenDesign sync). The full release steps are in [AGENTS.md](AGENTS.md).

## Using it in a project

- **Assets:** copy the SVGs a project needs into it. Don't use submodules or symlinks. Note the brand version you copied from (e.g. `brand v1.2.0`) so drift is easy to spot.
- **Tokens:** copy the Tailwind v4 block from DESIGN.md §14.
- **AI assistants:** point the project's `CLAUDE.md` at this repo's `DESIGN.md` and §16 (review checklist).

## Versioning

`DESIGN.md` carries the version and changelog (§17). When it changes, bump the version, add a changelog row, and tag the commit `vX.Y.Z`.
