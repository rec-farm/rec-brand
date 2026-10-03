# REC brand

The design system and brand assets for every REC product (Paramtune, StillUp and whatever comes next). Owned by RECIAM SAS. Private.

- **[DESIGN.md](DESIGN.md)**: the spec. It covers principles, logos, color, type, layout, components, voice, accessibility and Tailwind v4 tokens. Start here. Its YAML front matter holds the machine-readable tokens in Google's [DESIGN.md format](https://github.com/google-labs-code/design.md), which `npx @google/design.md lint DESIGN.md` validates.
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

Commit the regenerated SVGs together with the change that produced them. Before committing, run `python3 scripts/check.py` (token consistency, `design.md lint` and OpenDesign sync; the lint needs Node for `npx`). The full release steps are in [AGENTS.md](AGENTS.md).

## Using it in a project

- **Assets:** copy the SVGs a project needs into it. Don't use submodules or symlinks. Note the brand version you copied from (e.g. `brand v1.2.0`) so drift is easy to spot.
- **Tokens:** copy the Tailwind v4 block from DESIGN.md §14. Tools that read the DESIGN.md format (Stitch, OpenDesign, `design.md export --format dtcg`) can use the front matter directly.
- **AI assistants:** point the project's `CLAUDE.md` at this repo's `DESIGN.md` and §16 (review checklist).

## Versioning

`DESIGN.md` carries the version and changelog (§17). When it changes, bump the version, add a changelog row, and tag the commit `vX.Y.Z`.
