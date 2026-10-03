#!/usr/bin/env python3
"""Brand consistency checks. Run before committing a brand change.

    python3 scripts/check.py

1. Tokens: the YAML front matter of DESIGN.md is the source of truth. The §3
   tables, the §14 Tailwind block (colors, type sizes, radii) and the color
   constants in build.py are hand-kept copies, and must match it.
2. design.md lint: runs Google's DESIGN.md linter on the front matter (broken
   references, WCAG contrast of component pairs). Errors fail; contrast
   warnings are printed. Skipped if npx isn't installed.
3. OpenDesign: the local OpenDesign brand project must hold the same DESIGN.md
   and generated assets as this repo. Skipped if OpenDesign isn't installed.
"""
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
OD_DATA = Path.home() / "Library/Application Support/Open Design/namespaces/release-stable/data"
OPEN_DESIGN = OD_DATA / "projects/brand-rec-design-system-5bae95"
OPEN_DESIGN_BRAND = OD_DATA / "brands/rec-design-system-5bae95"  # re-imports read context/input-DESIGN.md here
ALIASES = {"DEEP": "deep-900"}  # build.py constant → token name, where they differ
DESIGN_MD_CLI = "@google/design.md@0.4.0"  # pinned: the format is alpha
HEX = r"#[0-9A-Fa-f]{6}"


def front_matter():
    """Parse DESIGN.md's front matter. Handles the subset we write: nested maps of scalars."""
    text = (ROOT / "DESIGN.md").read_text()
    if not text.startswith("---\n"):
        raise SystemExit("DESIGN.md has no front matter")
    root, stack = {}, [(-1, None)]
    stack[0] = (-1, root)
    for line in text[4:text.index("\n---\n", 4)].splitlines():
        line = re.sub(r"\s+#.*$", "", line) if not line.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, _, value = line.strip().partition(":")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        key, value = key.strip('"'), value.strip().strip('"')
        if value:
            parent[key] = value
        else:
            parent[key] = {}
            stack.append((indent, parent[key]))
    return root


def section(design, number):
    start = design.index(f"\n## {number}. ")
    return design[start:design.index("\n## ", start + 1)]


def check_tokens():
    design = (ROOT / "DESIGN.md").read_text()
    fm = front_matter()
    colors = {n: v.upper() for n, v in fm["colors"].items() if re.fullmatch(HEX, v)}
    errors = []

    # §14: every --color-* primitive, type size and radius
    tailwind = section(design, 14)
    tw_colors = {n: v.upper() for n, v in re.findall(rf"--color-([a-z0-9-]+):\s*({HEX})", tailwind)}
    for name in sorted(colors.keys() | tw_colors.keys()):
        if name not in tw_colors:
            errors.append(f"front matter colors.{name}: no --color-{name} in DESIGN.md §14")
        elif name not in colors:
            errors.append(f"DESIGN.md §14 --color-{name}: not in the front matter")
        elif colors[name] != tw_colors[name]:
            errors.append(f"DESIGN.md §14 --color-{name} = {tw_colors[name]}, front matter = {colors[name]}")
    for name, style in fm["typography"].items():
        m = re.search(rf"--text-{re.escape(name)}:\s*([0-9.]+rem)", tailwind)
        if not m or m.group(1) != style["fontSize"]:
            errors.append(f"DESIGN.md §14 --text-{name} = {m and m.group(1)}, front matter = {style['fontSize']}")
    for name, value in fm["rounded"].items():
        m = re.search(rf"--radius-{name}:\s*([0-9]+(?:px)?)", tailwind)
        if not m or m.group(1).removesuffix("px") != value.removesuffix("px"):
            errors.append(f"DESIGN.md §14 --radius-{name} = {m and m.group(1)}, front matter = {value}")

    # §3.2 primitives: every `token` | `#HEX` row, the pastel table (one hex per column) and the extras line
    color = section(design, 3)
    color = color[color.index("### 3.2"):color.index("### 3.3")]
    found = re.findall(rf"\| `([a-z0-9-]+)` \| `({HEX})`", color)
    columns = ["100", "300", "400", "600", "950"]
    for hue, cells in re.findall(r"^\| \*\*(\w+)\*\* \|(.+)$", color, re.M):
        found += [(f"{hue.lower()}-{c}", v) for c, v in zip(columns, re.findall(rf"`({HEX})`", cells))]
    found += re.findall(rf"`([a-z]+-[0-9]+) ({HEX})`", color)
    for name, value in found:
        if name not in colors:
            errors.append(f"DESIGN.md §3 {name}: not in the front matter")
        elif colors[name] != value.upper():
            errors.append(f"DESIGN.md §3 {name} = {value}, front matter = {colors[name]}")

    # build.py constants
    for names, values in re.findall(r'^([A-Z_0-9, ]+?)\s*=\s*("#.+)$', (ROOT / "build.py").read_text(), re.M):
        for const, value in zip([n.strip() for n in names.split(",")], re.findall(rf'"({HEX})"', values)):
            token = ALIASES.get(const, const.lower().replace("_", "-"))
            if token not in colors:
                errors.append(f"build.py {const}: no colors.{token} in the front matter")
            elif colors[token] != value.upper():
                errors.append(f"build.py {const} = {value}, front matter colors.{token} = {colors[token]}")
    return errors


def check_lint():
    if not shutil.which("npx"):
        print("· npx not found, skipping design.md lint")
        return []
    run = subprocess.run(["npx", "--yes", DESIGN_MD_CLI, "lint", str(ROOT / "DESIGN.md")],
                         capture_output=True, text=True)
    try:
        report = json.loads(run.stdout)
    except json.JSONDecodeError:
        return [f"design.md lint didn't return JSON: {(run.stderr or run.stdout).strip()[:300]}"]
    return [("" if f["severity"] == "error" else "! ") + f"{f.get('path', '')}: {f['message']}"
            for f in report["findings"]
            if f["severity"] == "error" or (f["severity"] == "warning" and "contrast" in f["message"])]


def check_open_design():
    if not OPEN_DESIGN.exists():
        print("· OpenDesign project not found, skipping")
        return []
    pairs = [("DESIGN.md", "context/input-DESIGN.md"), ("build.py", "build.py")]
    for folder in ("logos", "illustrations", "sheets"):
        pairs += [(str(p.relative_to(ROOT)),) * 2 for p in sorted((ROOT / folder).glob("*.svg"))]
    errors = []
    brand_input = OPEN_DESIGN_BRAND / "context/input-DESIGN.md"
    if not brand_input.exists():
        errors.append(f"OpenDesign brand is missing {brand_input.relative_to(OD_DATA)}")
    elif brand_input.read_text().strip() != (ROOT / "DESIGN.md").read_text().strip():  # OpenDesign trims it
        errors.append(f"OpenDesign {brand_input.relative_to(OD_DATA)} differs from DESIGN.md (re-imports would use it)")
    for ours, theirs in pairs:
        other = OPEN_DESIGN / theirs
        if not other.exists():
            errors.append(f"OpenDesign is missing {theirs}")
        elif ours == "DESIGN.md" and other.read_text().strip() == (ROOT / ours).read_text().strip():
            continue  # OpenDesign trims it on import
        elif other.read_bytes() != (ROOT / ours).read_bytes():
            errors.append(f"OpenDesign {theirs} differs from {ours}")
    for folder in ("logos", "illustrations", "sheets"):
        for p in sorted((OPEN_DESIGN / folder).glob("*.svg")):
            if not (ROOT / folder / p.name).exists():
                errors.append(f"OpenDesign has {folder}/{p.name}, the repo doesn't")
    return errors


if __name__ == "__main__":
    failed = False
    for label, check in (("tokens", check_tokens), ("design.md lint", check_lint), ("OpenDesign", check_open_design)):
        lines = check()
        errors = [line for line in lines if not line.startswith("! ")]  # "! " = warning, doesn't fail
        print(f"{'✗' if errors else '✓'} {label}")
        for line in lines:
            print(f"    {line}")
        failed |= bool(errors)
    sys.exit(1 if failed else 0)
