"""Render every README section graphic in the city theme, light and dark.

Edit the data blocks below (CONTACT, PROJECTS, STACK, HISTORY) and re-run.

Usage: python scripts/make_sections.py
Writes: assets/<name>-dark.svg and assets/<name>-light.svg
"""
from datetime import date
from html import escape
from pathlib import Path
from textwrap import wrap

from theme import FONT_MONO, FONT_SANS, THEMES, iso_box, shade

OUT = Path("assets")

CONTACT = [
    ("portfolio", "has-nain.dev", "https://has-nain.dev", False),
    ("linkedin", "in/hasnainaftab", "https://linkedin.com/in/hasnainaftab", False),
    ("email", "contact@has-nain.dev", "mailto:contact@has-nain.dev", False),
    ("resume", "view pdf", "https://drive.google.com/file/d/1nRNyTThlNpX6LQX5nNEKfYHSsv71wsxT/view?usp=sharing", True),
]

GH = "https://github.com/hasnain833/"
PORTFOLIO = "https://has-nain.dev"
# slug, title, stack, description, link, building height, featured
PROJECTS = [
    ("ai4home", "AI4Home Warranty Portal", "Next.js · Prisma · PostgreSQL · Claude · pgvector",
     "Multi-tenant SaaS for home builders with AI sales agents, semantic search and CRM integrations",
     GH + "ai4home-portal", 54, True),
    ("security", "AI Security Suite", "Python · LangChain · Chroma · FAISS · Splunk",
     "RAG-based malware and phishing detection middleware that plugs into Splunk",
     GH + "Splunk_middleware", 44, False),
    ("enrichflow", "EnrichFlow", "Next.js · Supabase · Prisma · n8n",
     "Dashboard automating Apollo-based contact enrichment across multiple data providers",
     GH + "cesarEnrichFlow", 36, False),
    ("pocketpinky", "Pocket Pinky", "React Native · Node.js",
     "AI dating coach app with a conversational UI",
     GH + "pocketpinky", 30, False),
    ("habibi", "Habibi Market", "MERN · Tailwind · JWT · Stripe",
     "E-commerce platform with 400+ listings, real-time chat and payments",
     PORTFOLIO, 40, False),
    ("turo", "Turo", "Next.js · Node.js · MongoDB",
     "Vehicle rental platform for car, airplane and boat bookings",
     PORTFOLIO, 34, False),
    ("calmbot", "CalmBot", "Python · LangChain · OpenAI · FAISS",
     "CBT therapy assistant with a RAG pipeline and mood tracking",
     PORTFOLIO, 28, False),
    ("meditrack", "MediTrack", "C# · .NET · WPF",
     "Desktop pharmacy management system with an auto-updater module",
     GH + "MediTrack_DotNet", 24, False),
]

STACK = [
    ("frontend", ["React", "Next.js", "TypeScript", "Tailwind", "Redux", "HTML", "CSS", "JavaScript"], False),
    ("backend", ["Node.js", "Express", "Python", "PHP", "Laravel", "GraphQL", ".NET"], False),
    ("data · tools", ["MongoDB", "PostgreSQL", "MySQL", "Prisma", "Supabase", "Docker", "AWS", "Git", "Postman"], False),
    ("mobile", ["React Native", "Flutter", "Android Studio"], False),
    ("ai · llm", ["Claude API", "OpenAI API", "LangChain", "RAG pipelines", "pgvector", "FAISS", "Chroma"], True),
]

# (year, month, place, role, above_road)
HISTORY = [
    (2022, 1, "CafeVista", "Frontend Developer", True),
    (2023, 7, "Freelance", "Full stack · clients in 3 countries", False),
    (2025, 8, "BitzSol", "Full Stack Web Developer", True),
    (2026, 2, "NUML Islamabad", "BS Information Technology", False),
]

STYLE = (
    "<style>.t{font-family:" + FONT_SANS + "}.m{font-family:" + FONT_MONO + "}"
    ".fade{opacity:0;animation:f .6s ease-out forwards}"
    "@keyframes f{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}</style>"
)


def svg(w: int, h: int, label: str, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{escape(label)}">{STYLE}{body}</svg>')


def rise(inner: str, delay: float, dur: float = .5) -> str:
    """Wrap content so it grows up from its own baseline (origin must be the base)."""
    return (f'<g transform="scale(1,0)"><animateTransform attributeName="transform" type="scale" '
            f'from="1 0" to="1 1" begin="{delay:.2f}s" dur="{dur}s" fill="freeze"/>{inner}</g>')


def faces(t: dict, green: bool) -> tuple[str, str, str]:
    if green:
        return t["accent"], t["accent_dim"], t["accent_deep"]
    return t["block"], t["block_l"], t["block_r"]


# ---------------------------------------------------------------- contact
def contact(t, label, value, accent):
    w, h = 205, 48
    col = t["accent"] if accent else t["border"]
    txt = t["accent"] if accent else t["text"]
    body = (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="8" fill="{t["panel"]}" stroke="{col}"/>'
            f'<text x="16" y="20" class="m" font-size="11" fill="{t["muted"]}">'
            f'<tspan fill="{t["accent"]}">$</tspan> open {label}</text>'
            f'<text x="16" y="37" class="t" font-size="13" font-weight="600" fill="{txt}">{escape(value)}</text>'
            f'<text x="{w - 16}" y="31" text-anchor="end" class="t" font-size="15" fill="{t["muted"]}">↗</text>')
    return svg(w, h, f"{label}: {value}", body)


# ---------------------------------------------------------------- projects
def project(t, i, title, stack, desc, height, featured):
    w, h = 420, 132
    top, left, right = faces(t, featured)
    lines = wrap(desc, 44)[:3]
    stroke = t["accent"] if featured else t["border"]
    body = [f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="{t["panel"]}" stroke="{stroke}"/>']
    # little ground tile + building on the right
    bx, by = 362, 104
    body.append(f'<polygon points="{bx},{by - 17} {bx + 34},{by} {bx},{by + 17} {bx - 34},{by}" fill="none" '
                f'stroke="{t["border"]}" stroke-dasharray="3 3"/>')
    building = iso_box(0, 0, 20, height, top, left, right)
    # windows on the front faces
    win = "".join(
        f'<rect x="{fx}" y="{-height + 10 + k * 8}" width="2.4" height="2.4" fill="{t["window"] if featured else t["panel"]}" '
        f'opacity="{.9 if featured else .55}"/>'
        for k in range(max(0, int((height - 12) / 8))) for fx in (-13, -7, 6, 12)
        if (k * 7 + fx + i) % 3)
    body.append(f'<g transform="translate({bx},{by})">{rise(building + win, .3 + i * .08, .6)}</g>')
    tag = "featured" if featured else None
    y = 34
    body.append(f'<g class="fade" style="animation-delay:{.1 + i * .08:.2f}s">')
    body.append(f'<text x="20" y="{y}" class="t" font-size="16" font-weight="600" fill="{t["text"]}">{escape(title)}</text>')
    if tag:
        tw = len(title) * 8.6 + 28
        body.append(f'<rect x="{tw}" y="{y - 13}" width="62" height="18" rx="9" fill="none" stroke="{t["accent"]}"/>'
                    f'<text x="{tw + 31}" y="{y}" text-anchor="middle" class="m" font-size="10" fill="{t["accent"]}">{tag}</text>')
    body.append(f'<text x="20" y="{y + 20}" class="m" font-size="10.5" fill="{t["accent"] if featured else t["muted"]}">'
                f'{escape(stack)}</text>')
    for k, line in enumerate(lines):
        body.append(f'<text x="20" y="{y + 48 + k * 18}" class="t" font-size="12.5" fill="{t["body"]}">{escape(line)}</text>')
    body.append("</g>")
    return svg(w, h, f"{title} — {desc}. Built with {stack}.", "".join(body))


# ---------------------------------------------------------------- stack
def stack(t):
    w = 860
    col_w = w / len(STACK)
    rows = max(len(items) for _, items, _ in STACK)
    h = 150 + rows * 22 + 20
    body = [f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>']
    base_y = 104
    for gi, (name, items, green) in enumerate(STACK):
        cx = col_w * gi + col_w / 2
        top, left, right = faces(t, green)
        if gi:
            body.append(f'<line x1="{col_w * gi:.0f}" y1="24" x2="{col_w * gi:.0f}" y2="{h - 24}" stroke="{t["border"]}"/>')
        # one voxel per tool, stacked; each appears in turn
        for k in range(len(items)):
            y = base_y - k * 8
            blk = iso_box(0, 0, 16, 8, top, left, right)
            body.append(f'<g transform="translate({cx:.1f},{y})" opacity="0">'
                        f'<animate attributeName="opacity" to="1" begin="{.2 + gi * .15 + k * .07:.2f}s" dur=".2s" fill="freeze"/>'
                        f'{blk}</g>')
        body.append(f'<text x="{cx:.1f}" y="{base_y + 34}" text-anchor="middle" class="m" font-size="12" '
                    f'fill="{t["accent"] if green else t["muted"]}">{escape(name)} · {len(items)}</text>')
        body.append(f'<g class="fade" style="animation-delay:{.4 + gi * .15:.2f}s">')
        for k, item in enumerate(items):
            body.append(f'<text x="{cx:.1f}" y="{base_y + 64 + k * 22}" text-anchor="middle" class="t" font-size="13.5" '
                        f'fill="{t["text"] if green else t["body"]}">{escape(item)}</text>')
        body.append("</g>")
    label = "Tech stack. " + " ".join(f"{n}: {', '.join(i)}." for n, i, _ in STACK)
    return svg(w, int(h), label, "".join(body))


# ---------------------------------------------------------------- history
def history(t):
    w, h = 860, 210
    x0, x1, road_y = 50, 810, 108
    start, end = date(2021, 10, 1), date.today()
    span = (end - start).days

    def xpos(y, m):
        return x0 + (date(y, m, 1) - start).days / span * (x1 - x0)

    body = [f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>',
            f'<line x1="{x0}" y1="{road_y}" x2="{x1}" y2="{road_y}" stroke="{t["road"]}" stroke-width="14" stroke-linecap="round"/>',
            f'<line x1="{x0}" y1="{road_y}" x2="{x1}" y2="{road_y}" stroke="{t["faint"]}" stroke-width="1" stroke-dasharray="7 7" opacity=".7"/>']
    for i, (yr, mo, place, role, above) in enumerate(HISTORY):
        x = xpos(yr, mo)
        current = place == "BitzSol"
        col = t["accent"] if current else t["block"]
        stem_end = road_y - 22 if above else road_y + 22
        ty = road_y - 70 if above else road_y + 46
        d = .3 + i * .25
        body.append(
            f'<g class="fade" style="animation-delay:{d:.2f}s">'
            f'<line x1="{x:.1f}" y1="{road_y}" x2="{x:.1f}" y2="{stem_end}" stroke="{col}" stroke-width="1.2"/>'
            f'<circle cx="{x:.1f}" cy="{road_y}" r="6" fill="{t["panel"]}" stroke="{col}" stroke-width="2.5"/>'
            f'<text x="{x:.1f}" y="{ty}" text-anchor="middle" class="m" font-size="10.5" fill="{t["muted"]}">'
            f'{date(yr, mo, 1).strftime("%b %Y")}</text>'
            f'<text x="{x:.1f}" y="{ty + 18}" text-anchor="middle" class="t" font-size="14" font-weight="600" '
            f'fill="{t["accent"] if current else t["text"]}">{escape(place)}</text>'
            f'<text x="{x:.1f}" y="{ty + 35}" text-anchor="middle" class="t" font-size="12" fill="{t["body"]}">'
            f'{escape(role)}</text></g>')

    # "now" marker that pulses at the end of the road
    body.append(
        f'<g class="fade" style="animation-delay:1.4s">'
        f'<circle cx="{x1}" cy="{road_y}" r="7" fill="{t["accent"]}"/>'
        f'<circle cx="{x1}" cy="{road_y}" r="7" fill="none" stroke="{t["accent"]}">'
        f'<animate attributeName="r" values="7;16" dur="1.8s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values=".8;0" dur="1.8s" repeatCount="indefinite"/></circle>'
        f'<text x="{x1}" y="{road_y - 22}" text-anchor="middle" class="m" font-size="11" fill="{t["accent"]}">now</text></g>')
    # a car driving the career road
    body.append(f'<rect width="10" height="5" rx="2" y="-2.5" x="-5" fill="{t["car_a"]}">'
                f'<animateMotion dur="7s" repeatCount="indefinite" path="M{x0},{road_y} L{x1},{road_y}"/></rect>')
    label = "Career: " + "; ".join(f"{date(y, m, 1):%b %Y} {p}, {r}" for y, m, p, r, _ in HISTORY) + "."
    return svg(w, h, label, "".join(body))


def main():
    OUT.mkdir(exist_ok=True)
    n = 0
    for mode, t in THEMES.items():
        def save(name, content):
            nonlocal n
            (OUT / f"{name}-{mode}.svg").write_text(content, encoding="utf-8")
            n += 1
        for label, value, _, accent in CONTACT:
            save(f"contact-{label}", contact(t, label, value, accent))
        for i, (slug, title, stk, desc, _, height, featured) in enumerate(PROJECTS):
            save(f"project-{slug}", project(t, i % 2, title, stk, desc, height, featured))
        save("stack", stack(t))
        save("history", history(t))
    print(f"wrote {n} files to {OUT}/")


if __name__ == "__main__":
    main()
