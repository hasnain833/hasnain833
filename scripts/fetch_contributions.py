"""Fetch the last year of GitHub contributions into data/contributions.json.

1. Public calendar HTML (the same one your profile shows; includes private
   contribution counts if "Include private contributions" is on). No token.
2. Fallback: GraphQL API, using GITHUB_TOKEN (provided automatically in Actions).

Usage: python scripts/fetch_contributions.py [username]
"""
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import requests

_args = [a for a in sys.argv[1:] if not a.startswith("--")]
USER = _args[0] if _args else os.environ.get("GH_USER", "hasnain833")
OUT = Path("data/contributions.json")
HEADERS = {"User-Agent": f"{USER}-profile-city"}


def from_html() -> list[dict]:
    r = requests.get(f"https://github.com/users/{USER}/contributions", headers=HEADERS, timeout=30)
    r.raise_for_status()
    html = r.text

    # <td ... data-date="2026-01-03" id="contribution-day-component-6-12" data-level="2" ...>
    cells = {}
    for m in re.finditer(r"<td[^>]*?>", html):
        tag = m.group(0)
        d = re.search(r'data-date="([\d-]+)"', tag)
        if not d:
            continue
        cid = re.search(r'id="([^"]+)"', tag)
        lvl = re.search(r'data-level="(\d)"', tag)
        cells[cid.group(1) if cid else d.group(1)] = {
            "date": d.group(1), "level": int(lvl.group(1)) if lvl else 0, "count": None,
        }

    # <tool-tip for="contribution-day-component-6-12">3 contributions on January 3rd.</tool-tip>
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        cell = cells.get(m.group(1))
        if cell is None:
            continue
        text = m.group(2).strip()
        n = re.match(r"([\d,]+)\s+contribution", text)
        cell["count"] = int(n.group(1).replace(",", "")) if n else 0

    days = sorted(cells.values(), key=lambda c: c["date"])
    if not days:
        raise ValueError("no contribution cells found in HTML")
    # Older markup put counts in data-count; if tooltips were missing, estimate from level
    for c in days:
        if c["count"] is None:
            c["count"] = [0, 1, 3, 6, 10][c["level"]]
    return days


def from_graphql() -> list[dict]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set")
    q = """query($login:String!){user(login:$login){contributionsCollection{
      contributionCalendar{weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": q, "variables": {"login": USER}},
        headers={**HEADERS, "Authorization": f"bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    weeks = r.json()["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    lv = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    return [
        {"date": d["date"], "count": d["contributionCount"], "level": lv[d["contributionLevel"]]}
        for w in weeks for d in w["contributionDays"]
    ]


def stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(days):
        if d["count"]:
            current += 1
        elif current or d["date"] != date.today().isoformat():
            break  # today being empty doesn't break the streak yet
    return {"total": total, "best_date": best["date"], "best_count": best["count"],
            "longest_streak": longest, "current_streak": current}


def main():
    try:
        days = from_html()
        src = "html"
    except Exception as e:  # noqa: BLE001 - fall back on any failure
        print(f"HTML fetch failed ({e}); trying GraphQL")
        days = from_graphql()
        src = "graphql"
    OUT.parent.mkdir(exist_ok=True)
    data = {"user": USER, "source": src, "updated": date.today().isoformat(), "days": days, **stats(days)}
    OUT.write_text(json.dumps(data, indent=1))
    print(f"wrote {OUT}: {len(days)} days, {data['total']} contributions ({src})")


def sample():
    """Realistic placeholder data for local previews (python ... --sample)."""
    import math
    import random
    random.seed(833)
    end = date.today()
    start = end - timedelta(days=end.weekday() + 1 + 52 * 7)  # Sunday, 53 weeks back
    days, d = [], start
    while d <= end:
        i = (d - start).days
        wave = 1.2 + math.sin(i / 23) + 0.8 * math.sin(i / 61 + 1)
        weekday = d.weekday() < 5
        n = max(0, int(random.gauss(wave * (1.6 if weekday else 0.6), 1.6)))
        if random.random() < 0.28:
            n = 0
        days.append({"date": d.isoformat(), "count": n})
        d += timedelta(days=1)
    target = 576
    scale = target / max(1, sum(x["count"] for x in days))
    for x in days:
        x["count"] = round(x["count"] * scale)
    days[-40]["count"] = 23
    mx = max(x["count"] for x in days)
    for x in days:
        c = x["count"]
        x["level"] = 0 if c == 0 else min(4, 1 + int(3 * c / mx * 1.6))
    OUT.parent.mkdir(exist_ok=True)
    data = {"user": USER, "source": "sample", "updated": end.isoformat(), "days": days, **stats(days)}
    OUT.write_text(json.dumps(data, indent=1))
    print(f"wrote SAMPLE {OUT}: {data['total']} contributions")


if __name__ == "__main__":
    if "--sample" in sys.argv:
        sample()
    else:
        main()
