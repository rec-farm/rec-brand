#!/usr/bin/env python3
"""REC brand asset generator.

Builds every logo, lockup, app icon, sheet and illustration from one set of
geometry so the mark family stays consistent. Wordmarks are converted to
outlines (no font needed to render the SVGs).

    python3 -m venv .venv && .venv/bin/pip install fonttools
    .venv/bin/python build.py
"""
from pathlib import Path
import math

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).parent
FONTS = ROOT / "fonts"

# ── Tokens (mirror DESIGN.md §3) ────────────────────────────────────────────
INK_950, INK_900, INK_850, INK_700, INK_600 = "#0A0B0C", "#101214", "#16191C", "#23272B", "#3A4046"
PAPER_50, PAPER_100, PAPER_200, PAPER_400 = "#FFFCF5", "#F7F1E3", "#EFE8D8", "#DDD3BF"
CREAM, STONE_400, DEEP = "#F4EFE3", "#A8A396", "#14262E"
PURPLE_300, PURPLE_500, PURPLE_600 = "#AC8BFF", "#7638FA", "#6524E8"
SUN_300, SUN_400 = "#F2C641", "#E8B931"
MINT_300, MINT_400, MINT_500 = "#A8D8C2", "#4CC79A", "#2F8F7A"
ROSE_300, ROSE_400, ROSE_500, ROSE_600 = "#F2C9D1", "#F07A9C", "#E8739A", "#C42F52"
LILAC_300 = "#DCD7EE"


# ── Outlined text ───────────────────────────────────────────────────────────
class Face:
    def __init__(self, file, **axes):
        font = instancer.instantiateVariableFont(TTFont(FONTS / file), axes)
        self.font = font
        self.glyphs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm
        self.cap = font["OS/2"].sCapHeight
        self.hmtx = font["hmtx"]

    def size_for_cap(self, cap_px):
        return cap_px * self.upm / self.cap

    def measure(self, s, size, tracking=0.0):
        k = size / self.upm
        w = sum(self.hmtx[self.cmap[ord(c)]][0] * k for c in s)
        return w + tracking * size * (len(s) - 1)

    def path(self, s, size, x=0.0, baseline=0.0, tracking=0.0):
        """Return (svg path d, advance width) for s set at size px."""
        k = size / self.upm
        pen = SVGPathPen(self.glyphs)
        for i, c in enumerate(s):
            name = self.cmap[ord(c)]
            self.glyphs[name].draw(TransformPen(pen, (k, 0, 0, -k, x, baseline)))
            x += self.hmtx[name][0] * k + (tracking * size if i < len(s) - 1 else 0)
        return pen.getCommands(), x

    def text(self, s, size, x=0.0, baseline=0.0, tracking=0.0, fill="#000", anchor="start"):
        if anchor != "start":
            w = self.measure(s, size, tracking)
            x -= w if anchor == "end" else w / 2
        d, _ = self.path(s, size, x, baseline, tracking)
        return f'<path fill="{fill}" d="{d}"/>'


ARCHIVO_X800 = Face("Archivo.ttf", wdth=125, wght=800)  # REC chain, stats
ARCHIVO_X700 = Face("Archivo.ttf", wdth=125, wght=700)  # product wordmarks, stamps
FIGTREE_800 = Face("Figtree.ttf", wght=800)             # StillUp wordmark, titles
FIGTREE_600 = Face("Figtree.ttf", wght=600)             # "by" endorsement
MONO_500 = Face("GeistMono.ttf", wght=500)
MONO_600 = Face("GeistMono.ttf", wght=600)


# ── Mark geometry: 48 × 48 grid (DESIGN.md §2.4) ────────────────────────────
# Primitives shared by every product mark (the REC chain is typographic, see rec_chain):
#   LENS  — almond, 44 × 21, centred.         PUPIL — circle r 8.5 at centre.
#   SPARK — the highlight / accent, always on the 45° up-right axis.
LENS = "M2 24C10 10 38 10 46 24C38 38 10 38 2 24Z"
PUPIL_R = 8.5
SPARK = (27.2, 20.8, 2.6)
STROKE = 3.6  # knock-out / line weight at 48 units (= 1/13 of the grid)
_uid = [0]


def _id(prefix):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


# ── REC master mark: the chain monogram (DESIGN.md §2.4) ────────────────────
# R, E, C in Archivo Expanded 800. The E slides REC_OVERLAP × cap height behind
# R and C; where they overlap, R and C cut a REC_CUT × cap height gap into it.
REC_OVERLAP, REC_CUT = 0.10, 0.085


def _ink_x(face, ch, size):
    bp = BoundsPen(face.glyphs)
    face.glyphs[face.cmap[ord(ch)]].draw(bp)
    k = size / face.upm
    return bp.bounds[0] * k, bp.bounds[2] * k


def rec_chain(fg, cap, x=0.0, top=0.0, letters="REC"):
    """The chain set with its cap line at `top`. Returns (markup, width)."""
    face = ARCHIVO_X800
    size = face.size_for_cap(cap)
    paths, cx = {}, x
    for ch in letters:
        x0, x1 = _ink_x(face, ch, size)
        paths[ch], _ = face.path(ch, size, cx - x0, top + cap)
        cx += x1 - x0 - cap * REC_OVERLAP
    width = cx + cap * REC_OVERLAP - x
    m = _id("m")
    cuts = "".join(f'<path d="{paths[ch]}" fill="#000" stroke="#000" stroke-width="{2 * REC_CUT * cap:.2f}" '
                   f'stroke-linejoin="round"/>' for ch in letters if ch != "E")
    pad = cap
    e = ""
    if "E" in letters:
        e = (f'<mask id="{m}" maskUnits="userSpaceOnUse" x="{x - pad:.2f}" y="{top - pad:.2f}" width="{width + 2 * pad:.2f}" '
             f'height="{3 * cap:.2f}"><rect x="{x - pad:.2f}" y="{top - pad:.2f}" width="{width + 2 * pad:.2f}" '
             f'height="{3 * cap:.2f}" fill="#fff"/>{cuts}</mask>'
             f'<path fill="{fg}" d="{paths["E"]}" mask="url(#{m})"/>')
    front = "".join(f'<path fill="{fg}" d="{paths[ch]}"/>' for ch in letters if ch != "E")
    return e + front, width


def mark_rec(fg):
    """The chain fitted to the 44-unit safe width, centred on the 48 grid."""
    _, w = rec_chain(fg, 10)
    cap = 10 * 44 / w
    body, _ = rec_chain(fg, cap, 2, 24 - cap / 2)
    return body


def micro_rec(fg):
    """≤ 32 px: the R with the E behind it, cropped to the safe square (first pass)."""
    c = _id("k")
    cap = 26
    body, _ = rec_chain(fg, cap, 3, 24 - cap / 2, letters="RE")
    return (f'<defs><clipPath id="{c}"><rect x="2" y="2" width="44" height="44"/></clipPath></defs>'
            f'<g clip-path="url(#{c})">{body}</g>')


PULSE = "M2 24H13.5L17.5 17L23 31L28.5 13.5L32.5 27.5L35 24H46"


def mark_stillup(fg):
    m = _id("m")
    return (f'<defs><mask id="{m}" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48">'
            f'<rect width="48" height="48" fill="#fff"/>'
            f'<path d="{PULSE}" fill="none" stroke="#000" stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'</mask></defs>'
            f'<path d="{LENS}" fill="{fg}" mask="url(#{m})"/>')


def _polar(r, deg, c=24.0):
    a = math.radians(deg)
    return c + r * math.cos(a), c - r * math.sin(a)


def mark_paramtune(fg):
    m = _id("m")
    ticks = ""
    for deg in (225, 180, 135, 90, 45, 0, -45):  # 270° gauge, open at the bottom
        x1, y1 = _polar(16.5, deg)
        x2, y2 = _polar(20.5, deg)
        ticks += f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>'
    px, py = _polar(8.5, 45)  # pointer on the SPARK axis
    return (f'<defs><mask id="{m}" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48">'
            f'<rect width="48" height="48" fill="#fff"/>'
            f'<line x1="24" y1="24" x2="{px:.2f}" y2="{py:.2f}" stroke="#000" stroke-width="{STROKE}" stroke-linecap="round"/>'
            f'<circle cx="24" cy="24" r="3.2" fill="#000"/></mask></defs>'
            f'<g stroke="{fg}" stroke-width="3" stroke-linecap="round">{ticks}</g>'
            f'<circle cx="24" cy="24" r="12.5" fill="{fg}" mask="url(#{m})"/>')


MARKS = {"rec": mark_rec, "stillup": mark_stillup, "paramtune": mark_paramtune}

# Micro marks (≤ 32 px): drop fine detail, thicken knock-outs (DESIGN.md §2.6).
PULSE_MICRO = "M2 24H14L22 12L28 35L33 24H46"


def micro_stillup(fg):
    m = _id("m")
    return (f'<defs><mask id="{m}" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48">'
            f'<rect width="48" height="48" fill="#fff"/>'
            f'<path d="{PULSE_MICRO}" fill="none" stroke="#000" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
            f'</mask></defs><path d="M1 24C9 8 39 8 47 24C39 40 9 40 1 24Z" fill="{fg}" mask="url(#{m})"/>')


def micro_paramtune(fg):
    m = _id("m")
    px, py = _polar(12, 45)
    return (f'<defs><mask id="{m}" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48">'
            f'<rect width="48" height="48" fill="#fff"/>'
            f'<line x1="24" y1="24" x2="{px:.2f}" y2="{py:.2f}" stroke="#000" stroke-width="5.5" stroke-linecap="round"/>'
            f'<circle cx="24" cy="24" r="5" fill="#000"/></mask></defs>'
            f'<circle cx="24" cy="24" r="20" fill="{fg}" mask="url(#{m})"/>')


MICRO = {"rec": micro_rec, "stillup": micro_stillup, "paramtune": micro_paramtune}


def place(markup, x, y, size):
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({size / 48:.4f})">{markup}</g>'


def svg(w, h, body, title=None):
    t = f"<title>{title}</title>" if title else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img"{" aria-label=" + chr(34) + title + chr(34) if title else ""}>{t}{body}</svg>\n')


def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    print("wrote", p.relative_to(ROOT))


# ── Wordmarks & lockups ─────────────────────────────────────────────────────
# Lockup rule: mark = 48, wordmark cap height = 20 (≈ 0.42 × mark),
# gap = 12 (0.25 × mark), caps optically centred on the mark.
# REC has no separate wordmark: its lockup is the chain alone at REC_LOCKUP_CAP.
WORDMARKS = {
    "paramtune": dict(face=ARCHIVO_X700, text="PARAMTUNE", tracking=0.18),
    "stillup":   dict(face=FIGTREE_800,  text="StillUp",   tracking=-0.02),
}
MARK, CAP, GAP = 48, 20, 12
REC_LOCKUP_CAP = 28


def wordmark(name, fill, x, baseline, cap=CAP):
    spec = WORDMARKS[name]
    face = spec["face"]
    size = face.size_for_cap(cap)
    d, end = face.path(spec["text"], size, x, baseline, spec["tracking"])
    return f'<path fill="{fill}" d="{d}"/>', end


def lockup(name, fg, x=0.0, y=0.0, scale=1.0):
    """Horizontal lockup. Returns (markup, width, height) in unscaled units."""
    if name == "rec":
        chain, end = rec_chain(fg, REC_LOCKUP_CAP, 0, MARK / 2 - REC_LOCKUP_CAP / 2)
        return f'<g transform="translate({x:.2f} {y:.2f}) scale({scale})">{chain}</g>', end, MARK
    mark = place(MARKS[name](fg), 0, 0, MARK)
    wm, end = wordmark(name, fg, MARK + GAP, MARK / 2 + CAP / 2)
    body = f'<g transform="translate({x:.2f} {y:.2f}) scale({scale})">{mark}{wm}</g>'
    return body, end, MARK


def endorsed(name, fg, muted, x=0.0, y=0.0, scale=1.0):
    """Product lockup + 'by REC' line, 9 below the wordmark baseline (DESIGN.md §2.5)."""
    body, w, h = lockup(name, fg)
    by_cap = 8
    by_size = FIGTREE_600.size_for_cap(by_cap)
    bx, base = MARK + GAP, MARK / 2 + CAP / 2 + 9 + by_cap
    by_d, bend = FIGTREE_600.path("by", by_size, bx, base)
    chain, cw = rec_chain(muted, by_cap, bend + 5, base - by_cap)
    rend = bend + 5 + cw
    extra = f'<path fill="{muted}" d="{by_d}"/>{chain}'
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({scale})">{body}{extra}</g>', max(w, rend), base + 2


def build_logos():
    for name, fn in MARKS.items():
        for tone, fg in (("ink", DEEP), ("cream", CREAM)):
            write(f"logos/{name}-mark-{tone}.svg", svg(48, 48, fn(fg), f"{name} mark"))
            body, w, h = lockup(name, fg)
            write(f"logos/{name}-lockup-{tone}.svg", svg(math.ceil(w), h, body, f"{name} logo"))
        if name != "rec":
            for tone, fg, muted in (("ink", DEEP, "#4B5B61"), ("cream", CREAM, STONE_400)):
                body, w, h = endorsed(name, fg, muted)
                write(f"logos/{name}-endorsed-{tone}.svg", svg(math.ceil(w), math.ceil(h), body, f"{name} by REC"))


# ── App icons (DESIGN.md §2.7) ──────────────────────────────────────────────
ICONS = {
    "rec":       dict(tile=PURPLE_500, fg=CREAM),
    "stillup":   dict(tile=SUN_300,    fg=DEEP),
    "paramtune": dict(tile=MINT_400,   fg=DEEP),
}


def app_icon(name, x=0, y=0, size=128):
    s = size / 128
    spec = ICONS[name]
    body = (f'<rect x="16" y="16" width="104" height="104" rx="10" fill="{DEEP}"/>'
            f'<rect x="8" y="8" width="104" height="104" rx="10" fill="{spec["tile"]}" stroke="{DEEP}" stroke-width="4"/>'
            + (place(MARKS[name](spec["fg"]), 18, 18, 84) if name == "rec"  # wide mark: fill the tile's width
               else place(MARKS[name](spec["fg"]), 28, 28, 64)))
    return f'<g transform="translate({x} {y}) scale({s})">{body}</g>'


def favicon(name):
    spec = ICONS[name]
    return svg(32, 32, f'<rect width="32" height="32" rx="6" fill="{spec["tile"]}"/>' + place(MICRO[name](spec["fg"]), 3, 3, 26))


def build_icons():
    for name in MARKS:
        write(f"logos/{name}-app-icon.svg", svg(128, 128, app_icon(name), f"{name} app icon"))
        write(f"logos/{name}-favicon.svg", favicon(name))
        for tone, fg in (("ink", DEEP), ("cream", CREAM)):
            write(f"logos/{name}-micro-{tone}.svg", svg(48, 48, MICRO[name](fg), f"{name} micro mark"))


# ── Sheets (previews embedded in DESIGN.md) ─────────────────────────────────
def stamp(text, x, y, fill, cap=7):
    return ARCHIVO_X700.text(text.upper(), ARCHIVO_X700.size_for_cap(cap), x, y, 0.14, fill)


def build_logo_sheet():
    W, H = 1200, 780
    out = [f'<rect width="{W}" height="{H}" fill="{PAPER_100}"/>',
           f'<rect width="{W // 2}" height="{H}" fill="{INK_950}"/>']
    for col, (bg, fg, muted, label) in enumerate(((INK_950, CREAM, STONE_400, "Dark (default)"),
                                                  (PAPER_100, DEEP, "#4B5B61", "Paper (light)"))):
        ox = col * 600 + 56
        out.append(stamp(label, ox, 56, muted))
        y = 96
        for name in ("rec", "stillup", "paramtune"):
            body, w, h = lockup(name, fg, ox, y, 1.0)
            out.append(body)
            y += 96
        body, w, h = endorsed("stillup", fg, muted, ox, y)
        out.append(body)
        body, w, h = endorsed("paramtune", fg, muted, ox, y + 100)
        out.append(body)
        out.append(stamp("Marks · micro", ox, 624, muted))
        for i, name in enumerate(("rec", "stillup", "paramtune")):
            out.append(place(MARKS[name](fg), ox + i * 96, 648, 64))
            out.append(place(MICRO[name](fg), ox + 300 + i * 48, 664, 24))
    out.append(f'<rect x="0" y="{H - 1}" width="{W}" height="1" fill="{INK_700}"/>')
    write("sheets/logo-sheet.svg", svg(W, H, "".join(out), "REC logo family"))

    # App icons + favicons sheet
    W, H = 760, 260
    out = [f'<rect width="{W}" height="{H}" fill="{PAPER_200}"/>', stamp("App icons · favicons", 40, 40, "#4B5B61")]
    for i, name in enumerate(("rec", "stillup", "paramtune")):
        x = 40 + i * 240
        out.append(app_icon(name, x, 64, 128))
        spec = ICONS[name]
        fx = x + 150
        out.append(f'<g transform="translate({fx} 96)"><rect width="32" height="32" rx="6" fill="{spec["tile"]}"/>'
                   + place(MICRO[name](spec["fg"]), 3, 3, 26) + "</g>")
        out.append(f'<g transform="translate({fx} 140)"><rect width="16" height="16" rx="3" fill="{spec["tile"]}"/>'
                   + place(MICRO[name](spec["fg"]), 1.5, 1.5, 13) + "</g>")
        out.append(stamp(name, x, 228, DEEP))
    write("sheets/app-icons.svg", svg(W, H, "".join(out), "REC app icons"))


def build_construction():
    S = 6  # 48 units × 6 = 288px per mark
    W, H = 1080, 470
    out = [f'<rect width="{W}" height="{H}" fill="{PAPER_50}"/>']
    sx, sy, _ = SPARK
    for i, name in enumerate(("rec", "stillup", "paramtune")):
        ox, oy = 48 + i * 336, 64
        g = [f'<rect width="48" height="48" fill="{PAPER_100}"/>']
        for k in range(0, 49, 4):  # 4-unit grid
            w = 0.12 if k % 12 else 0.22
            g.append(f'<path d="M{k} 0V48M0 {k}H48" stroke="{PAPER_400}" stroke-width="{w}"/>')
        g.append(f'<rect x="2" y="2" width="44" height="44" fill="none" stroke="{ROSE_400}" stroke-width="0.2" stroke-dasharray="0.8 0.8"/>')
        g.append(MARKS[name](DEEP + "E6"))
        if name == "rec":
            # keylines: cap line and baseline, plus the overlap zones where the E slides behind R and C
            _, w = rec_chain(DEEP, 10)
            cap = 10 * 44 / w
            top, base = 24 - cap / 2, 24 + cap / 2
            g.append(f'<path d="M0 {top:.2f}H48M0 {base:.2f}H48" stroke="{PURPLE_500}" stroke-width="0.25"/>')
            size = ARCHIVO_X800.size_for_cap(cap)
            x = 2.0
            for ch in "RE":
                x0, x1 = _ink_x(ARCHIVO_X800, ch, size)
                x += x1 - x0
                ox = x - cap * REC_OVERLAP
                g.append(f'<rect x="{ox:.2f}" y="{top:.2f}" width="{cap * REC_OVERLAP:.2f}" height="{cap:.2f}" '
                         f'fill="{MINT_500}" fill-opacity="0.35"/>')
                x = ox
        else:  # lens / pupil / gauge keylines and the spark axis
            g.append(f'<path d="{LENS}" fill="none" stroke="{PURPLE_500}" stroke-width="0.25"/>')
            g.append(f'<circle cx="24" cy="24" r="{PUPIL_R}" fill="none" stroke="{PURPLE_500}" stroke-width="0.25"/>')
            g.append(f'<circle cx="24" cy="24" r="12.5" fill="none" stroke="{PURPLE_500}" stroke-width="0.25" stroke-dasharray="1 0.6"/>')
            x2, y2 = _polar(30, 45)
            g.append(f'<path d="M24 24L{x2:.2f} {y2:.2f}" stroke="{MINT_500}" stroke-width="0.35" stroke-dasharray="1 0.6"/>')
            g.append(f'<circle cx="{sx}" cy="{sy}" r="0.8" fill="{MINT_500}"/>')
        out.append(f'<g transform="translate({ox} {oy}) scale({S})">{"".join(g)}</g>')
        out.append(stamp(name, ox, 40, DEEP, 8))
    leg = [("Keylines (cap · lens · gauge)", PURPLE_500), ("Spark axis · overlap", MINT_500), ("Safe area (2u)", ROSE_400)]
    for j, (txt, c) in enumerate(leg):
        lx = 48 + j * 300
        out.append(f'<rect x="{lx}" y="{H - 58}" width="14" height="3" fill="{c}"/>')
        out.append(MONO_500.text(txt, 13, lx + 22, H - 52, fill=DEEP))
    out.append(MONO_500.text("48 × 48 grid · 4u minor / 12u major · stroke & knock-outs 3.6u", 13, 48, H - 24, fill="#4B5B61"))
    write("sheets/mark-construction.svg", svg(W, H, "".join(out), "Mark construction"))


# ── Illustrations (DESIGN.md §8) ────────────────────────────────────────────
def halftone(pid, color, step=7, r=1.4):
    return (f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{step / 2}" cy="{step / 2}" r="{r}" fill="{color}"/></pattern>')


def starburst(cx, cy, r_out, r_in, points, fill):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi / points * i - math.pi / 2
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}"/>'


def eye_panel(cx, cy, w, ink, white, lashes=True):
    """Big illustrated eye: almond, pupil, spark, lashes."""
    h = w * 0.5
    x0, x1 = cx - w / 2, cx + w / 2
    c = h * 0.67
    almond = (f"M{x0} {cy}C{x0 + w * 0.18} {cy - c} {x1 - w * 0.18} {cy - c} {x1} {cy}"
              f"C{x1 - w * 0.18} {cy + c} {x0 + w * 0.18} {cy + c} {x0} {cy}Z")
    out = []
    if lashes:
        for deg in (150, 120, 90, 60, 30, -30, -60, -90, -120, -150):
            a = math.radians(deg)
            r1, r2 = h * 0.62, h * 0.86
            rx = w / h * 0.55
            x1_, y1_ = cx + r1 * math.cos(a) * rx, cy - r1 * math.sin(a)
            x2_, y2_ = cx + r2 * math.cos(a) * rx, cy - r2 * math.sin(a)
            out.append(f'<line x1="{x1_:.1f}" y1="{y1_:.1f}" x2="{x2_:.1f}" y2="{y2_:.1f}" stroke="{ink}" stroke-width="5" stroke-linecap="round"/>')
    out.append(f'<path d="{almond}" fill="{white}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>')
    pr = h * 0.42
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{pr}" fill="{ink}"/>')
    out.append(f'<circle cx="{cx + pr * 0.38:.1f}" cy="{cy - pr * 0.38:.1f}" r="{pr * 0.24:.1f}" fill="{white}"/>')
    return "".join(out)


ILLOS = []


def illo(rel, content):
    write(rel, content)
    ILLOS.append((rel, content))


def build_illustration_sheet():
    """Each illustration on the surface it is designed for."""
    cells = {  # key: x, y, w, h, surface
        "header-stillup-light": (0, 0, 600, 360, PAPER_100), "header-paramtune-dark": (600, 0, 600, 360, INK_950),
        "empty-state-stillup-light": (0, 360, 600, 260, PAPER_50), "empty-state-paramtune-dark": (600, 360, 600, 260, INK_900),
        "header-stillup-dark": (0, 620, 600, 360, INK_950), "empty-state-stillup-dark": (600, 620, 600, 360, INK_900),
        "motif-kit": (0, 980, 1200, 200, PAPER_100),
    }
    out = []
    for rel, content in ILLOS:
        key = Path(rel).stem
        x, y, w, h, bg = cells[key]
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>')
        inner = content.split(">", 1)[1].rsplit("</svg>", 1)[0]
        vb = content.split('viewBox="')[1].split('"')[0]
        iw, ih = map(float, vb.split()[2:])
        out.append(f'<svg x="{x + (w - iw) / 2}" y="{y + (h - ih) / 2}" width="{iw}" height="{ih}" viewBox="{vb}">{inner}</svg>')
    write("sheets/illustrations.svg", svg(1200, 1180, "".join(out), "REC illustrations"))

def build_header_stillup():
    W, H = 520, 320
    panels = [  # x, y, w, h, fill
        (24, 34, 270, 236, ROSE_500),
        (294, 34, 200, 118, SUN_300),
        (294, 152, 200, 118, MINT_400),
    ]
    shadow = f'<rect x="36" y="46" width="470" height="236" fill="{DEEP}"/>'
    body = [f'<defs>{halftone("ht", ROSE_600, 7, 1.5)}{halftone("ht2", "#C99A17", 7, 1.2)}</defs>', shadow]
    for x, y, w, h, fill in panels:
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>')
    body.append(f'<rect x="24" y="190" width="270" height="80" fill="url(#ht)" opacity="0.55"/>')
    body.append(f'<rect x="420" y="34" width="74" height="118" fill="url(#ht2)" opacity="0.5"/>')
    body.append(eye_panel(159, 152, 196, DEEP, PAPER_50))
    body.append(starburst(394, 93, 40, 14, 8, DEEP))
    body.append(f'<path d="M314 211H350L362 186L378 238L394 176L408 222L416 211H474" fill="none" stroke="{DEEP}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    for x, y, w, h, _ in panels:
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{DEEP}" stroke-width="5"/>')
    g = f'<g transform="rotate(-2 260 160)">{"".join(body)}</g>'
    return illo("illustrations/header-stillup-light.svg", svg(W, H, g, "StillUp header illustration"))


def build_header_stillup_dark():
    """Dark sibling of the StillUp header: untilted, ink panels on a dot grid, cream line art,
    one Sun accent on the 45° spark axis (the raised starburst), ink-600 shadow ledge."""
    W, H = 520, 320
    body = [f'<defs>{halftone("sdg", INK_600, 8, 1)}</defs>']
    body.append(f'<path d="M36 74H306V60H496V282H36Z" fill="{INK_600}"/>')  # shadow ledge
    # eye panel
    body.append(f'<rect x="24" y="62" width="270" height="210" fill="{INK_900}"/><rect x="24" y="62" width="270" height="210" fill="url(#sdg)"/>')
    body.append(eye_panel(159, 167, 190, CREAM, INK_950))
    body.append(f'<rect x="24" y="62" width="270" height="210" fill="none" stroke="{CREAM}" stroke-width="3"/>')
    # pulse panel
    body.append(f'<rect x="294" y="152" width="190" height="120" fill="{INK_900}"/><rect x="294" y="152" width="190" height="120" fill="url(#sdg)"/>')
    body.append(f'<path d="M312 214H346L358 189L374 241L390 179L404 225L412 214H466" fill="none" stroke="{CREAM}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(f'<rect x="294" y="152" width="190" height="120" fill="none" stroke="{CREAM}" stroke-width="3"/>')
    # raised spark panel (up-right): the single accent
    body.append(f'<rect x="312" y="26" width="180" height="112" fill="{INK_600}"/>')
    body.append(f'<rect x="304" y="18" width="180" height="112" fill="{INK_950}" stroke="{CREAM}" stroke-width="3"/>')
    body.append(starburst(394, 74, 36, 13, 8, SUN_400))
    return illo("illustrations/header-stillup-dark.svg", svg(W, H, "".join(body), "StillUp header illustration"))


def build_empty_stillup_dark():
    """Dark sibling of the StillUp empty state: untilted raised chip, cream type, Sun method stamp,
    uptime ticks keep their status meaning (mint healthy, rose failing) at -400 strength."""
    W, H = 400, 220
    body = [f'<defs>{halftone("sdg2", INK_700, 8, 1)}</defs>',
            f'<rect x="40" y="10" width="320" height="200" fill="url(#sdg2)"/>',
            f'<rect x="90" y="34" width="236" height="72" fill="{INK_600}"/>',
            f'<rect x="82" y="26" width="236" height="72" fill="{INK_900}" stroke="{CREAM}" stroke-width="3"/>',
            f'<rect x="100" y="50" width="40" height="24" rx="2" fill="{SUN_400}"/>',
            MONO_600.text("GET", 13, 120, 67, fill=INK_950, anchor="middle"),
            MONO_500.text("/health", 24, 152, 70, fill=CREAM),
            f'<circle cx="284" cy="61" r="14" fill="{INK_950}" stroke="{CREAM}" stroke-width="3"/>',
            f'<path d="M277 61.5l5 5 9-10" fill="none" stroke="{CREAM}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>']
    pattern = "mmmmrmmmmmmrmmmmmmmrmmmmmmm"
    for i, k in enumerate(pattern):
        c = ROSE_400 if k == "r" else MINT_400
        body.append(f'<rect x="{66 + i * 10.4:.1f}" y="136" width="6" height="30" rx="1.5" fill="{c}"/>')
    return illo("illustrations/empty-state-stillup-dark.svg", svg(W, H, "".join(body), "Meet your first API check"))


def build_header_paramtune():
    W, H = 520, 320
    body = [f'<defs>{halftone("dg", INK_600, 8, 1)}</defs>']
    # shadow ledge
    body.append(f'<path d="M36 74H276V60H496V282H36Z" fill="{INK_600}"/>')
    # dial panel
    body.append(f'<rect x="24" y="62" width="240" height="210" fill="{INK_900}"/><rect x="24" y="62" width="240" height="210" fill="url(#dg)"/>')
    cx, cy, r = 144, 167, 62
    ticks = []
    for i in range(24):
        deg = 225 - i * (270 / 23)
        x1, y1 = _polar(r + 12, deg, 0)
        x2, y2 = _polar(r + (24 if i % 4 == 0 else 18), deg, 0)
        ticks.append(f'<line x1="{cx + x1:.1f}" y1="{cy + y1:.1f}" x2="{cx + x2:.1f}" y2="{cy + y2:.1f}"/>')
    body.append(f'<g stroke="{CREAM}" stroke-width="3" stroke-linecap="round">{"".join(ticks)}</g>')
    body.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK_950}" stroke="{CREAM}" stroke-width="4"/>')
    px, py = _polar(48, 58, 0)
    body.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + px:.1f}" y2="{cy + py:.1f}" stroke="{CREAM}" stroke-width="6" stroke-linecap="round"/>')
    body.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{MINT_400}" stroke="{CREAM}" stroke-width="3"/>')
    body.append(f'<rect x="24" y="62" width="240" height="210" fill="none" stroke="{CREAM}" stroke-width="3"/>')
    # braces panel (raised)
    body.append(f'<rect x="282" y="26" width="202" height="112" fill="{INK_600}"/>')
    body.append(f'<rect x="274" y="18" width="202" height="112" fill="{INK_950}" stroke="{CREAM}" stroke-width="3"/>')
    body.append(MONO_600.text("{ }", 64, 375, 96, fill=CREAM, anchor="middle"))
    # slider panel
    body.append(f'<rect x="264" y="148" width="220" height="124" fill="{INK_900}"/><rect x="264" y="148" width="220" height="124" fill="url(#dg)"/>')
    body.append(f'<path d="M290 236H458" stroke="{CREAM}" stroke-width="3"/>')
    body.append(f'<path d="M352 236L398 190H446" fill="none" stroke="{STONE_400}" stroke-width="2.5" stroke-dasharray="6 5"/>')
    for x in (296, 352):
        body.append(f'<rect x="{x - 7}" y="229" width="14" height="14" fill="{INK_950}" stroke="{CREAM}" stroke-width="3"/>')
    body.append(f'<rect x="446" y="228" width="16" height="16" fill="{MINT_400}" stroke="{CREAM}" stroke-width="3"/>')
    body.append(f'<rect x="440" y="183" width="14" height="14" fill="{INK_950}" stroke="{CREAM}" stroke-width="2.5"/>')
    body.append(f'<rect x="264" y="148" width="220" height="124" fill="none" stroke="{CREAM}" stroke-width="3"/>')
    return illo("illustrations/header-paramtune-dark.svg", svg(W, H, "".join(body), "Paramtune header illustration"))


def build_empty_stillup():
    W, H = 400, 220
    chip = [f'<rect x="88" y="34" width="236" height="72" fill="{DEEP}"/>',
            f'<rect x="80" y="26" width="236" height="72" fill="{SUN_300}" stroke="{DEEP}" stroke-width="4"/>',
            MONO_600.text("GET", 15, 108, 68, fill=DEEP),
            MONO_500.text("/health", 24, 150, 70, fill=DEEP),
            f'<circle cx="282" cy="61" r="14" fill="{MINT_300}" stroke="{DEEP}" stroke-width="3"/>',
            f'<path d="M275 61.5l5 5 9-10" fill="none" stroke="{DEEP}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>']
    bars = []
    pattern = "mmmmrmmmmmmrmmmmmmmrmmmmmmm"
    for i, k in enumerate(pattern):
        c = ROSE_400 if k == "r" else MINT_500
        bars.append(f'<rect x="{66 + i * 10.4:.1f}" y="136" width="6" height="30" rx="1.5" fill="{c}"/>')
    body = f'<g transform="rotate(-3 200 66)">{"".join(chip)}</g>' + "".join(bars)
    return illo("illustrations/empty-state-stillup-light.svg", svg(W, H, body, "Meet your first API check"))


def build_empty_paramtune():
    W, H = 400, 220
    body = [f'<defs>{halftone("dg2", INK_700, 8, 1)}</defs>',
            f'<rect x="40" y="10" width="320" height="200" fill="url(#dg2)"/>',
            f'<rect x="128" y="40" width="160" height="110" fill="{INK_600}"/>',
            f'<rect x="120" y="32" width="160" height="110" fill="{INK_900}" stroke="{CREAM}" stroke-width="3"/>',
            MONO_600.text("{}", 58, 200, 108, fill=SUN_400, anchor="middle"),
            f'<rect x="150" y="164" width="100" height="26" rx="2" fill="{INK_850}" stroke="{INK_600}" stroke-width="1.5"/>',
            MONO_500.text("v1.0.0", 13, 200, 182, fill=STONE_400, anchor="middle"),
            f'<circle cx="280" cy="32" r="11" fill="{INK_950}" stroke="{SUN_400}" stroke-width="2.5" stroke-dasharray="4 3"/>']
    return illo("illustrations/empty-state-paramtune-dark.svg", svg(W, H, "".join(body), "Versions still at {}"))


def build_motifs():
    W, H = 840, 190
    out = [f'<rect width="{W}" height="{H}" fill="{PAPER_100}"/>']
    T = 96
    motifs = []
    # 1 eye
    motifs.append(("Eye", eye_panel(48, 50, 64, DEEP, PAPER_50, lashes=False)))
    # 2 pulse
    motifs.append(("Pulse", f'<path d="M12 50H32L38 38L46 64L54 30L60 56L64 50H84" fill="none" stroke="{DEEP}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
                            f'<circle cx="84" cy="50" r="5" fill="{MINT_400}" stroke="{DEEP}" stroke-width="2.5"/>'))
    # 3 dial
    d = [f'<circle cx="48" cy="50" r="24" fill="{PAPER_50}" stroke="{DEEP}" stroke-width="4"/>']
    for i in range(7):
        x1, y1 = _polar(29, 225 - i * 45, 0)
        x2, y2 = _polar(35, 225 - i * 45, 0)
        d.append(f'<line x1="{48 + x1:.1f}" y1="{50 + y1:.1f}" x2="{48 + x2:.1f}" y2="{50 + y2:.1f}" stroke="{DEEP}" stroke-width="3.5" stroke-linecap="round"/>')
    px, py = _polar(17, 45, 0)
    d.append(f'<line x1="48" y1="50" x2="{48 + px:.1f}" y2="{50 + py:.1f}" stroke="{DEEP}" stroke-width="4.5" stroke-linecap="round"/><circle cx="48" cy="50" r="5" fill="{MINT_400}" stroke="{DEEP}" stroke-width="2.5"/>')
    motifs.append(("Dial", "".join(d)))
    # 4 braces
    motifs.append(("Braces", MONO_600.text("{ }", 46, 48, 66, fill=DEEP, anchor="middle")))
    # 5 starburst
    motifs.append(("Spark", starburst(48, 50, 30, 11, 8, DEEP) + f'<circle cx="48" cy="50" r="5" fill="{SUN_300}"/>'))
    # 6 slider
    motifs.append(("Slider", f'<path d="M14 64H82" stroke="{DEEP}" stroke-width="4"/><path d="M44 64L60 40H76" fill="none" stroke="{DEEP}" stroke-width="2.5" stroke-dasharray="5 4"/>'
                             f'<rect x="12" y="58" width="12" height="12" fill="{PAPER_50}" stroke="{DEEP}" stroke-width="3"/>'
                             f'<rect x="38" y="58" width="12" height="12" fill="{PAPER_50}" stroke="{DEEP}" stroke-width="3"/>'
                             f'<rect x="72" y="57" width="14" height="14" fill="{PURPLE_500}" stroke="{DEEP}" stroke-width="3"/>'
                             f'<rect x="72" y="34" width="11" height="11" fill="{PAPER_50}" stroke="{DEEP}" stroke-width="2.5"/>'))
    # 7 terminal
    motifs.append(("Prompt", f'<path d="M22 36L38 50L22 64" fill="none" stroke="{DEEP}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
                             f'<path d="M46 66H72" stroke="{PURPLE_500}" stroke-width="5" stroke-linecap="round"/>'))
    for i, (label, art) in enumerate(motifs):
        x = 24 + i * 116
        out.append(f'<rect x="{x + 5}" y="29" width="{T}" height="{T}" fill="{DEEP}"/>')
        out.append(f'<rect x="{x}" y="24" width="{T}" height="{T}" fill="{PAPER_50}" stroke="{DEEP}" stroke-width="3"/>')
        out.append(f'<g transform="translate({x} 24)">{art}</g>')
        out.append(stamp(label, x, 160, DEEP))
    return illo("illustrations/motif-kit.svg", svg(W, H, "".join(out), "REC illustration motifs"))


if __name__ == "__main__":
    build_logos()
    build_icons()
    build_logo_sheet()
    build_construction()
    build_header_stillup()
    build_header_paramtune()
    build_empty_stillup()
    build_empty_paramtune()
    build_header_stillup_dark()
    build_empty_stillup_dark()
    build_motifs()
    build_illustration_sheet()
