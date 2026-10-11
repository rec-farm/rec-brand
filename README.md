# R.E.C. brand

The design system and brand assets for every R.E.C. product (Paramtune, StillUp, Handstamp, Valtr and whatever comes next), the self-hosted, open-source tools at [rec.farm](https://rec.farm/). The names and marks belong to RECIAM SAS; see [License](#license).

- **[DESIGN.md](DESIGN.md)**: the spec. It covers principles, logos, color, type, layout, components, voice, accessibility and Tailwind v4 tokens. Start here. Its YAML front matter holds the machine-readable tokens in Google's [DESIGN.md format](https://github.com/google-labs-code/design.md), which `npx @google/design.md lint DESIGN.md` validates.
- **`build.py`**: generates every SVG below from shared geometry and tokens. Don't hand-edit the output.
- **`logos/`**: marks, lockups, micro marks, favicons and app icons per product, in `ink` and `cream` colorways.
- **`illustrations/`**: page headers, empty states and the motif kit.
- **`sheets/`**: overview sheets (logo family, mark construction, app icons, illustrations).
- **`fonts/`**: Archivo, Figtree and Geist Mono (all SIL OFL 1.1, see [`fonts/OFL.txt`](fonts/OFL.txt)). `build.py` uses them to outline wordmarks.

## Rebuild

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python build.py
```

Commit the regenerated SVGs together with the change that produced them. Before committing, run `python3 scripts/check.py` (token consistency, `design.md lint` and OpenDesign sync; the lint needs Node for `npx`). The full release steps are in [AGENTS.md](AGENTS.md).

## Using it in a project

Anyone may copy the tokens (DESIGN.md front matter and §14), the rest of DESIGN.md (with attribution, CC BY 4.0) and the code. The logos, marks, app icons and illustrations are not open-licensed: use them only as [TRADEMARKS.md](TRADEMARKS.md) allows, which in short means unmodified, to refer to the R.E.C. projects. Your own product needs its own name and logo.

- **Assets** (R.E.C. projects): copy the SVGs a project needs into it. Don't use submodules or symlinks. Note the brand version you copied from (e.g. `brand v1.2.0`) so drift is easy to spot.
- **Tokens:** copy the Tailwind v4 block from DESIGN.md §14. Tools that read the DESIGN.md format (Stitch, OpenDesign, `design.md export --format dtcg`) can use the front matter directly.
- **AI assistants:** point the project's `CLAUDE.md` at this repo's `DESIGN.md` and §16 (review checklist).

## Versioning

`DESIGN.md` carries the version and changelog (§17). When it changes, bump the version, add a changelog row, and tag the commit `vX.Y.Z`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

- **Code** (`build.py`, `scripts/`): [MIT](LICENSE) · © 2026 Rodrigo Espinosa Curbelo. See [NOTICE](NOTICE).
- **DESIGN.md and other docs:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · attribution: Rodrigo Espinosa Curbelo.
- **Logos, marks, wordmarks, app icons, favicons, sheets** (`logos/`, `sheets/`) **and illustrations** (`illustrations/`): not open-licensed. The names and marks are trademarks of RECIAM SAS; see [TRADEMARKS.md](TRADEMARKS.md).
- **Fonts** (`fonts/`): SIL Open Font License 1.1, see [`fonts/OFL.txt`](fonts/OFL.txt).
