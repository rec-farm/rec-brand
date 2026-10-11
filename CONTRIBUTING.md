# Contributing

Thanks for helping. Please follow the R.E.C. [Code of Conduct](https://github.com/rec-farm/.github/blob/main/CODE_OF_CONDUCT.md).

## Setup

You need Python 3 and, for the `design.md` lint, Node (for `npx`).

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

## Making a change

- **Tokens start in the DESIGN.md front matter.** Change the YAML block first, then its copies in
  §3, §14 and the constants at the top of `build.py`.
- **Never hand-edit generated SVGs** (`logos/`, `illustrations/`, `sheets/`). Change `build.py`
  and rebuild with `.venv/bin/python build.py`. Commit the regenerated SVGs with the change.
- **Bump the version for user-visible changes:** the header version and date in DESIGN.md, plus
  a row in §17 Changelog.
- Write "R.E.C." in running text, never a bare "REC".
- One change per pull request.

## Before opening a pull request

```sh
.venv/bin/python build.py
python3 scripts/check.py
```

The token and `design.md lint` checks must pass. The OpenDesign check only applies to the
maintainer's local setup; it is fine if it fails for you.

## Licensing

By contributing you agree that code is licensed under MIT and docs under CC BY 4.0. Logos,
marks and illustrations are not open-licensed; see [TRADEMARKS.md](TRADEMARKS.md).
