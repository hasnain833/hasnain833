"""Turn source-prepped.png into a self-typing monochrome ASCII portrait.

Each row is revealed by a left-to-right clip wipe with a block cursor riding
the edge, staggered top to bottom. Plays once, then freezes (SMIL, which
GitHub runs inside SVGs embedded with <img>).

Usage: python scripts/make_ascii_svg.py
Env:   STATIC=1  -> emit the finished frame with no animation
Writes: assets/portrait-dark.svg, assets/portrait-light.svg
"""
import os
from html import escape

import numpy as np
from PIL import Image, ImageOps

SRC = "source-prepped.png"
from theme import THEMES
NBSP = "\u00a0"       # renderers trim plain spaces; NBSP keeps the grid
STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense); space clears background
COLS = 104
CHAR_ASPECT = 0.5        # glyph cell width / height

# Panel geometry (SVG units == px at the README's width="370")
W, H = 370, 346        # min height; matches info-card.svg so the panels align
PAD = 16
TITLE_H = 30

ROW_STAGGER = 0.055      # s between rows starting
ROW_DUR = 0.32           # s for one row to wipe across
START = 0.3


def to_rows() -> list[str]:
    img = Image.open(SRC).convert("L")
    # Crop to the subject's bounding box (anything not near-white)
    arr = np.array(img)
    ys, xs = np.where(arr < 245)
    x0, x1, y0 = xs.min(), xs.max() + 1, ys.min()
    # Head-and-shoulders framing: keep the top ~78% of the subject's width
    # in height so the face gets more characters than the jacket.
    y1 = min(arr.shape[0], y0 + int((x1 - x0) * 0.74))
    img = img.crop((x0, y0, x1, y1))
    img = ImageOps.autocontrast(img, cutoff=1)

    w, h = img.size
    rows = int(round(COLS * (h / w) * CHAR_ASPECT))
    small = np.array(img.resize((COLS, rows), Image.LANCZOS), dtype=np.float32)

    # Darken mid-tones so the (bright) face picks up visible glyphs while the
    # pure-white background still maps to spaces.
    small = 255 * (small / 255) ** 1.6
    idx = ((255 - small) / 255 * (len(RAMP) - 1)).round().astype(int)
    lines = ["".join(RAMP[i] for i in row) for row in idx]
    # Drop empty rows at the top/bottom
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def build(lines: list[str], t: dict) -> str:
    inner_w = W - 2 * PAD
    cell_w = inner_w / COLS
    cell_h = cell_w / CHAR_ASPECT
    art_h = cell_h * len(lines)
    height = max(H, int(TITLE_H + 2 * PAD + art_h))
    top = TITLE_H + (height - TITLE_H - art_h - 8) / 2   # centre the art (8px for cursor line)
    font_size = cell_h * 0.95

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" '
        f'width="{W}" height="{height}" role="img" aria-label="ASCII portrait of Hasnain Aftab">',
        "<defs>",
    ]
    if not STATIC:
        for i in range(len(lines)):
            y = top + i * cell_h
            b = START + i * ROW_STAGGER
            out.append(
                f'<clipPath id="r{i}"><rect x="{PAD}" y="{y:.2f}" width="0" height="{cell_h + 1:.2f}">'
                f'<animate attributeName="width" from="0" to="{inner_w}" begin="{b:.3f}s" '
                f'dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
            )
    out.append("</defs>")

    # Terminal window chrome
    out += [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="10" '
        f'fill="{t["panel"]}" stroke="{t["border"]}"/>',
        f'<path d="M0.5 {TITLE_H} H{W - 0.5}" stroke="{t["border"]}"/>',
        f'<circle cx="18" cy="15" r="5" fill="{t["border"]}"/>',
        f'<circle cx="34" cy="15" r="5" fill="{t["border"]}"/>',
        f'<circle cx="50" cy="15" r="5" fill="{t["accent"]}"/>',
        f'<text x="{W / 2}" y="19" text-anchor="middle" fill="{t["muted"]}" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11">'
        "hasnain@city: ~/portrait</text>",
        f'<g fill="{t["body"]}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Courier New\',monospace" '
        f'font-size="{font_size:.2f}" xml:space="preserve">',
    ]

    for i, line in enumerate(lines):
        if not line.strip():
            continue
        y = top + (i + 0.8) * cell_h
        clip = "" if STATIC else f' clip-path="url(#r{i})"'
        # textLength pins every row to the grid regardless of the viewer's font
        out.append(
            f'<text x="{PAD}" y="{y:.2f}" textLength="{inner_w}" '
            f'lengthAdjust="spacingAndGlyphs"{clip}>{escape(line).replace(" ", NBSP)}</text>'
        )
    out.append("</g>")

    if not STATIC:
        # One cursor block that rides each row's wipe edge, then blinks at the end
        n = len(lines)
        total = ROW_STAGGER * (n - 1) + ROW_DUR
        end = START + total
        out.append(
            f'<rect x="{PAD}" y="{top:.2f}" width="{cell_w * 1.6:.2f}" height="{cell_h:.2f}" '
            f'fill="{t["accent"]}" opacity="0">'
        )
        out.append(f'<set attributeName="opacity" to="0.9" begin="{START}s"/>')
        for i in range(n):
            b = START + i * ROW_STAGGER
            y = top + i * cell_h
            out.append(
                f'<animate attributeName="x" from="{PAD}" to="{PAD + inner_w:.2f}" '
                f'begin="{b:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            )
            out.append(f'<set attributeName="y" to="{y:.2f}" begin="{b:.3f}s"/>')
        # Park the cursor on a prompt line below the art and blink
        out.append(f'<set attributeName="x" to="{PAD}" begin="{end:.3f}s"/>')
        out.append(f'<set attributeName="y" to="{top + art_h + 4:.2f}" begin="{end:.3f}s"/>')
        out.append(
            f'<animate attributeName="opacity" values="0.9;0.9;0;0" keyTimes="0;0.5;0.5;1" '
            f'dur="1.1s" begin="{end:.3f}s" repeatCount="5" fill="freeze"/>'
        )
        out.append("</rect>")

    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    rows = to_rows()
    os.makedirs("assets", exist_ok=True)
    for mode, t in THEMES.items():
        with open(f"assets/portrait-{mode}.svg", "w", encoding="utf-8") as f:
            f.write(build(rows, t))
    print(f"wrote assets/portrait-{{dark,light}}.svg ({len(rows)} rows x {COLS} cols)")
