#!/usr/bin/env python3
"""Brand consistency checks. Run before committing a brand change.

    python3 scripts/check.py

1. Tokens: every color constant in build.py must match its --color-* value in
   DESIGN.md §14 (the Tailwind block). Until tokens are emitted from a single
   source, these are hand-kept copies and this catches drift.
2. OpenDesign: the local OpenDesign brand project must hold the same DESIGN.md
   and generated assets as this repo. Skipped if OpenDesign isn't installed.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
OPEN_DESIGN = (Path.home() / "Library/Application Support/Open Design/namespaces/release-stable/data"
               / "projects/brand-reciam-design-system-9c50f8")
ALIASES = {"DEEP": "deep-900"}  # build.py constant → token name, where they differ


def check_tokens():
    design = (ROOT / "DESIGN.md").read_text()
    tailwind = design[design.index("## 14. Implementation"):]
    tokens = {name: value.upper() for name, value in re.findall(r"--color-([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})", tailwind)}
    errors = []
    for names, values in re.findall(r'^([A-Z_0-9, ]+?)\s*=\s*("#.+)$', (ROOT / "build.py").read_text(), re.M):
        for const, value in zip([n.strip() for n in names.split(",")], re.findall(r'"(#[0-9A-Fa-f]{6})"', values)):
            token = ALIASES.get(const, const.lower().replace("_", "-"))
            if token not in tokens:
                errors.append(f"build.py {const}: no --color-{token} in DESIGN.md §14")
            elif tokens[token] != value.upper():
                errors.append(f"build.py {const} = {value}, but DESIGN.md §14 --color-{token} = {tokens[token]}")
    return errors


def check_open_design():
    if not OPEN_DESIGN.exists():
        print("· OpenDesign project not found, skipping")
        return []
    pairs = [("DESIGN.md", "context/input-DESIGN.md"), ("build.py", "build.py")]
    for folder in ("logos", "illustrations", "sheets"):
        pairs += [(str(p.relative_to(ROOT)),) * 2 for p in sorted((ROOT / folder).glob("*.svg"))]
    errors = []
    for ours, theirs in pairs:
        other = OPEN_DESIGN / theirs
        if not other.exists():
            errors.append(f"OpenDesign is missing {theirs}")
        elif other.read_bytes() != (ROOT / ours).read_bytes():
            errors.append(f"OpenDesign {theirs} differs from {ours}")
    for folder in ("logos", "illustrations", "sheets"):
        for p in sorted((OPEN_DESIGN / folder).glob("*.svg")):
            if not (ROOT / folder / p.name).exists():
                errors.append(f"OpenDesign has {folder}/{p.name}, the repo doesn't")
    return errors


if __name__ == "__main__":
    failed = False
    for label, check in (("tokens", check_tokens), ("OpenDesign", check_open_design)):
        errors = check()
        print(f"{'✗' if errors else '✓'} {label}")
        for e in errors:
            print(f"    {e}")
        failed |= bool(errors)
    sys.exit(1 if failed else 0)
