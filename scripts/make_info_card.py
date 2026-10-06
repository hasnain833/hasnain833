"""Neofetch-style info card that prints line by line next to the portrait.

Edit ROWS below when your role or stack changes, then re-run.

Usage: python scripts/make_info_card.py
Env:   STATIC=1 -> emit a frozen frame (no animation)
Writes: assets/card-dark.svg, assets/card-light.svg
"""
import os
import re
from html import escape

from theme import FONT_MONO, THEMES

STATIC = os.environ.get("STATIC") == "1"

USER, HOST = "hasnain", "github"
ROWS = [
    ("Role",      "Full Stack Engineer · AI Integration"),
    ("Now",       "Full Stack Web Developer @ BitzSol"),
    ("Freelance", "Intl. clients in 3 countries, since 2023"),
    ("Prev",      "Frontend Developer @ CafeVista"),
    ("Stack",     "Next.js · React · Node.js · TypeScript"),
    ("AI",        "Claude · OpenAI · LangChain · RAG"),
    ("Data",      "PostgreSQL · MongoDB · Prisma · pgvector"),
    ("Shipped",   "10+ production apps at BitzSol"),
    ("Edu",       "BS IT · NUML Islamabad"),
    ("Location",  "Islamabad, PK · open to onsite"),
    ("Web",       "has-nain.dev"),
]
HIGHLIGHT = {"Now", "AI"}     # rows whose value gets the green accent

W = 490
PAD_X = 20
TITLE_H = 30
SIZE = 12.5
LINE = 19
KEY_W = 92
START, STEP = 0.4, 0.12


def portrait_height(mode: str) -> int:
    """Match the portrait's height so both panels line up side by side."""
    try:
        head = open(f"assets/portrait-{mode}.svg", encoding="utf-8").read(400)
        return int(re.search(r'height="(\d+)"', head).group(1))
    except (OSError, AttributeError):
        return 0


def build(t: dict, mode: str) -> str:
    n_lines = 2 + len(ROWS) + 2
    content_h = TITLE_H + 24 + n_lines * LINE
    H = max(content_h, portrait_height(mode))
    top = TITLE_H + 24 + max(0, (H - content_h) // 2)

    css = (f"text{{font-family:{FONT_MONO};font-size:{SIZE}px}}"
           f".k{{fill:{t['muted']}}}.v{{fill:{t['body']}}}.g{{fill:{t['accent']}}}.d{{fill:{t['faint']}}}")
    if not STATIC:
        css += (".ln{opacity:0;animation:in .35s ease-out forwards}"
                "@keyframes in{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}")

    def line(i: int, body: str) -> str:
        delay = "" if STATIC else f' style="animation-delay:{START + i * STEP:.2f}s"'
        return f'<g class="ln"{delay}>{body}</g>'

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="Hasnain Aftab. ' + escape(". ".join(f"{k}: {v}" for k, v in ROWS)) + '">',
        f"<style>{css}</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{t["panel"]}" stroke="{t["border"]}"/>',
        f'<path d="M0.5 {TITLE_H} H{W - 0.5}" stroke="{t["border"]}"/>',
        f'<circle cx="18" cy="15" r="5" fill="{t["border"]}"/>',
        f'<circle cx="34" cy="15" r="5" fill="{t["border"]}"/>',
        f'<circle cx="50" cy="15" r="5" fill="{t["accent"]}"/>',
        f'<text x="{W / 2}" y="19" text-anchor="middle" class="d" style="font-size:11px">'
        f"{USER}@{HOST}: ~ — neofetch</text>",
    ]

    i, y = 0, top
    out.append(line(i, f'<text x="{PAD_X}" y="{y}"><tspan class="g" font-weight="700">{USER}</tspan>'
                       f'<tspan class="d">@</tspan><tspan class="g" font-weight="700">{HOST}</tspan></text>'))
    i += 1; y += LINE
    out.append(line(i, f'<text x="{PAD_X}" y="{y}" class="d">{"─" * 20}</text>'))
    i += 1; y += LINE
    for key, val in ROWS:
        cls = "g" if key in HIGHLIGHT else "v"
        out.append(line(i, f'<text x="{PAD_X}" y="{y}" class="k">{escape(key)}</text>'
                           f'<text x="{PAD_X + KEY_W}" y="{y}" class="{cls}">{escape(val)}</text>'))
        i += 1; y += LINE

    # contribution-level swatches instead of neofetch's rainbow colour bar
    y += LINE * 0.4
    sw = "".join(f'<rect x="{PAD_X + j * 26}" y="{y - 12:.0f}" width="22" height="14" rx="3" fill="{c}" '
                 f'stroke="{t["border"]}" stroke-width=".5"/>' for j, c in enumerate(t["levels"]))
    out.append(line(i, sw))
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    for mode, t in THEMES.items():
        with open(f"assets/card-{mode}.svg", "w", encoding="utf-8") as f:
            f.write(build(t, mode))
    print("wrote assets/card-dark.svg, assets/card-light.svg")
