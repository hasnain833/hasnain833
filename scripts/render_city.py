"""Render data/contributions.json as an animated isometric city.

Each day of the last year is a tower: height = contributions, colour = GitHub's
level. Towers rise in a wave on load, busy days get lit windows, the best day
gets a flag, and cars drive along the road. Dark mode is a night city with
stars and a moon; light mode is a daytime city with a sun and drifting clouds.

Usage: python scripts/render_city.py
Writes: assets/city-dark.svg, assets/city-light.svg
"""
import hashlib
import json
import random
from datetime import date
from html import escape

from theme import FONT_MONO, FONT_SANS, THEMES, shade

W, H = 860, 470
S = 9.0                     # half-width of one tower's footprint
ORIGIN_X = W / 2 - 23 * S   # centres the 53x7 grid horizontally
ORIGIN_Y = 138
BILLBOARD = (650, 86, 190, 66)   # x, y, w, h


def iso(x: float, y: float) -> tuple[float, float]:
    return ORIGIN_X + (x - y) * S, ORIGIN_Y + (x + y) * S * 0.5


def tower_height(count: int) -> float:
    return 1.6 if count == 0 else min(72, 3 + 4.2 * count ** 0.8)


def rng_for(key: str) -> random.Random:
    return random.Random(int(hashlib.md5(key.encode()).hexdigest()[:8], 16))


def box(h: float, top: str, left: str, right: str) -> str:
    w = S * 0.92
    return (
        f'<polygon points="0,{-h - w * .5:.1f} {w:.1f},{-h:.1f} 0,{-h + w * .5:.1f} {-w:.1f},{-h:.1f}" fill="{top}"/>'
        f'<polygon points="{-w:.1f},{-h:.1f} 0,{-h + w * .5:.1f} 0,{w * .5:.1f} {-w:.1f},0" fill="{left}"/>'
        f'<polygon points="{w:.1f},{-h:.1f} 0,{-h + w * .5:.1f} 0,{w * .5:.1f} {w:.1f},0" fill="{right}"/>'
    )


def windows(h: float, key: str, color: str) -> str:
    """Little lit windows on both visible faces of a tall tower."""
    r = rng_for(key)
    w = S * 0.92
    out = []
    y = -h + 0.225 * w + 4
    while y < 0.225 * w - 3:
        for fx, op in ((-0.55, 0.95), (0.45, 0.75)):
            if r.random() < 0.55:
                out.append(f'<rect x="{fx * w:.1f}" y="{y:.1f}" width="1.8" height="1.8" '
                           f'fill="{color}" opacity="{op}"/>')
        y += 5.5
    return "".join(out)


def sky(t: dict, mode: str) -> str:
    out = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{t["sky"]}" stroke="{t["border"]}"/>']
    r = random.Random(7)
    if mode == "dark":
        out.append('<g>')
        for _ in range(90):
            x, y = r.uniform(12, W - 12), r.uniform(12, 175)
            if 270 < x < 590 and 18 < y < 82:      # keep the wordmark clean
                continue
            rad = r.uniform(0.4, 1.3)
            dur = r.uniform(2, 5)
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rad:.1f}" fill="#c9d1d9">'
                       f'<animate attributeName="opacity" values="1;.25;1" dur="{dur:.1f}s" '
                       f'begin="{r.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>')
        out.append('</g>')
        # crescent moon
        out.append(f'<circle cx="78" cy="68" r="15" fill="#e6edf3"/><circle cx="85" cy="63" r="13" fill="{t["sky"]}"/>')
    else:
        out.append('<circle cx="78" cy="66" r="16" fill="#ffd33d"/><circle cx="78" cy="66" r="24" fill="#ffd33d" opacity=".18"/>')
        for i, (cy, scale, dur) in enumerate(((52, 1.0, 70), (110, 0.75, 95), (150, 0.9, 80))):
            cloud = (f'<g transform="scale({scale})" fill="#ffffff" opacity=".95">'
                     '<ellipse cx="0" cy="0" rx="26" ry="10"/><ellipse cx="14" cy="-7" rx="15" ry="11"/>'
                     '<ellipse cx="-12" cy="-4" rx="12" ry="8"/></g>')
            start = -60 - i * 280
            out.append(f'<g transform="translate({start},{cy})">{cloud}'
                       f'<animateTransform attributeName="transform" type="translate" '
                       f'values="{start},{cy};{W + 60},{cy}" dur="{dur}s" begin="-{i * 23}s" repeatCount="indefinite"/></g>')
    return "".join(out)


def build(data: dict, mode: str) -> str:
    t = THEMES[mode]
    days = data["days"]
    start = date.fromisoformat(days[0]["date"])
    first_sunday_offset = (start.weekday() + 1) % 7      # Sunday = row 0

    cells = []
    for d in days:
        i = (date.fromisoformat(d["date"]) - start).days + first_sunday_offset
        cells.append({**d, "x": i // 7, "y": i % 7})
    weeks = max(c["x"] for c in cells) + 1

    left_f, right_f = (0.74, 0.52) if mode == "dark" else (0.86, 0.72)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="Hasnain Aftab — {data["total"]} GitHub contributions in the last year, '
        f'drawn as an animated isometric city">',
        f'<style>.t{{font-family:{FONT_SANS}}}.m{{font-family:{FONT_MONO}}}'
        '.fade{opacity:0;animation:f .8s ease-out forwards}'
        '@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style>',
        sky(t, mode),
    ]

    # Wordmark
    out.append(
        f'<g class="fade" style="animation-delay:.1s">'
        f'<text x="{W / 2}" y="54" text-anchor="middle" class="t" font-size="36" font-weight="600" '
        f'letter-spacing="5" fill="{t["text"]}">HASNAIN<tspan fill="{t["accent"]}">.</tspan>DEV</text>'
        f'<text x="{W / 2}" y="80" text-anchor="middle" class="t" font-size="14" fill="{t["muted"]}">'
        f'full stack engineer · ai integration · next.js</text></g>'
    )

    # Ground slab + road along the front edge
    g = [iso(-0.9, -0.9), iso(weeks - 0.1, -0.9), iso(weeks - 0.1, 7.0), iso(-0.9, 7.0)]
    out.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in g)}" fill="{t["ground"]}" '
               f'stroke="{t["border"]}" stroke-width="0.8"/>')
    rd = [iso(-0.9, 7.15), iso(weeks - 0.1, 7.15), iso(weeks - 0.1, 8.1), iso(-0.9, 8.1)]
    out.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in rd)}" fill="{t["road"]}"/>')
    a, b = iso(-0.9, 7.62), iso(weeks - 0.1, 7.62)
    out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{t["faint"]}" '
               f'stroke-width="0.8" stroke-dasharray="5 6" opacity=".7"/>')

    # Towers, back to front
    best = max(cells, key=lambda c: c["count"])
    for c in sorted(cells, key=lambda c: (c["x"] + c["y"], c["x"])):
        x, y = iso(c["x"], c["y"])
        h = tower_height(c["count"])
        top = t["levels"][c["level"]]
        body = box(h, top, shade(top, left_f), shade(top, right_f))
        if c["count"] >= 6:
            body += windows(h, c["date"], t["window"])
        delay = 0.35 + c["x"] * 0.045 + c["y"] * 0.025
        out.append(
            f'<g transform="translate({x:.1f},{y:.1f})"><g transform="scale(1,0)">'
            f'<animateTransform attributeName="transform" type="scale" from="1 0" to="1 1" '
            f'begin="{delay:.2f}s" dur=".55s" fill="freeze" calcMode="spline" keySplines=".2 .8 .3 1" keyTimes="0;1"/>'
            f'{body}</g></g>'
        )
    rise_end = 0.35 + weeks * 0.045 + 7 * 0.025 + 0.55

    # Month labels in front of the road (never covered by towers)
    seen = set()
    for c in cells:
        d = date.fromisoformat(c["date"])
        if d.day <= 7 and d.month not in seen and c["y"] == 0 and 1 <= c["x"] <= weeks - 2:
            seen.add(d.month)
            lx, ly = iso(c["x"] + 1.2, 10.4)
            out.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" class="m" font-size="11" '
                       f'fill="{t["faint"]}">{d.strftime("%b")}</text>')

    # Best-day flag, flipped left if it would hit the billboard
    bx, by = iso(best["x"], best["y"])
    top_y = by - tower_height(best["count"]) - S * 0.46
    label = f'best day · {best["count"]}'
    lw = len(label) * 7 + 10
    bbx, bby, bbw, bbh = BILLBOARD
    right_side = not (bx + 26 + lw > bbx and top_y - 40 < bby + bbh)
    tx = bx + 26 if right_side else bx - 26 - lw
    flag = (f'M{bx:.1f},{top_y - 30:.1f} l18,5 l-18,5 z' if right_side
            else f'M{bx:.1f},{top_y - 30:.1f} l-18,5 l18,5 z')
    out.append(
        f'<g opacity="0"><animate attributeName="opacity" to="1" begin="{rise_end:.2f}s" dur=".5s" fill="freeze"/>'
        f'<line x1="{bx:.1f}" y1="{top_y:.1f}" x2="{bx:.1f}" y2="{top_y - 30:.1f}" stroke="{t["muted"]}" stroke-width="1.2"/>'
        f'<path d="{flag}" fill="{t["flag"]}"/>'
        f'<rect x="{tx:.1f}" y="{top_y - 38:.1f}" width="{lw}" height="18" rx="4" fill="{t["panel"]}" stroke="{t["border"]}"/>'
        f'<text x="{tx + lw / 2:.1f}" y="{top_y - 25:.1f}" text-anchor="middle" class="m" font-size="11" '
        f'fill="{t["body"]}">{escape(label)}</text></g>'
    )

    # Billboard
    out.append(
        f'<g class="fade" style="animation-delay:{rise_end - 0.6:.2f}s">'
        f'<rect x="{bbx}" y="{bby}" width="{bbw}" height="{bbh}" rx="8" fill="{t["panel"]}" stroke="{t["border"]}"/>'
        f'<text x="{bbx + bbw / 2}" y="{bby + 30}" text-anchor="middle" class="t" font-size="22" font-weight="600" '
        f'fill="{t["accent"]}">{data["total"]:,}</text>'
        f'<text x="{bbx + bbw / 2}" y="{bby + 50}" text-anchor="middle" class="t" font-size="12" '
        f'fill="{t["muted"]}">contributions in the last year</text></g>'
    )

    # Streak line, bottom left (empty corner of the diagonal city)
    out.append(
        f'<g class="fade" style="animation-delay:{rise_end - 0.3:.2f}s">'
        f'<text x="32" y="{H - 52}" class="m" font-size="12" fill="{t["muted"]}">'
        f'<tspan fill="{t["accent"]}">$</tspan> streak --current</text>'
        f'<text x="32" y="{H - 32}" class="m" font-size="12" fill="{t["body"]}">'
        f'{data["current_streak"]} days now · longest {data["longest_streak"]}</text></g>'
    )

    # Traffic
    p0, p1 = iso(-0.9, 7.45), iso(weeks - 0.1, 7.45)
    q0, q1 = iso(weeks - 0.1, 7.85), iso(-0.9, 7.85)
    for i, (dur, begin, col, (s0, s1)) in enumerate((
        (9, 0, t["car_a"], (p0, p1)), (9, 4.5, t["car_a"], (p0, p1)),
        (11, 2, t["car_b"], (q0, q1)), (11, 7.5, t["car_b"], (q0, q1)),
    )):
        out.append(f'<circle r="2" fill="{col}" opacity="0"><set attributeName="opacity" to="1" begin="{begin}s"/>'
                   f'<animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" '
                   f'path="M{s0[0]:.1f},{s0[1]:.1f} L{s1[0]:.1f},{s1[1]:.1f}"/></circle>')

    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    data = json.load(open("data/contributions.json"))
    for mode in ("dark", "light"):
        with open(f"assets/city-{mode}.svg", "w", encoding="utf-8") as f:
            f.write(build(data, mode))
    print(f"wrote assets/city-{{dark,light}}.svg ({data['total']} contributions, {data['source']})")
