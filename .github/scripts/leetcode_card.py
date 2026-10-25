#!/usr/bin/env python3
"""Build a large LeetCode profile card (SVG).

  python scripts/leetcode_card.py USERNAME            # live data from LeetCode
  python scripts/leetcode_card.py USERNAME --offline  # numbers from SNAPSHOT below
"""
import sys, json, math, html, datetime as dt, urllib.request

OUT = "leetcode-card.svg"

# Numbers copied from the LeetCode profile page, used only with --offline
SNAPSHOT = dict(
    rank=632293, solved=259, total=4087,
    easy=(99, 972), medium=(114, 2131), hard=(46, 984),
    streak=20, max_streak=60, active_days=202, submissions=466,
    badge_count=7, badges=["200 Days Badge 2026", "Jul Badge", "Jun Badge", "May Badge", "Apr Badge"],
    days={},
)

API = "https://leetcode.com/graphql"
Q1 = """query($u:String!){allQuestionsCount{difficulty count}
matchedUser(username:$u){profile{ranking}
submitStatsGlobal{acSubmissionNum{difficulty count}}
badges{displayName creationDate}}}"""
Q2 = """query($u:String!){matchedUser(username:$u){
userCalendar{streak totalActiveDays submissionCalendar}}}"""


def gql(query, user):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": {"u": user}}).encode(),
        headers={"Content-Type": "application/json", "Referer": "https://leetcode.com",
                 "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if out.get("errors"):
        raise RuntimeError(out["errors"])
    return out["data"]


def fetch(user):
    a, b = gql(Q1, user), gql(Q2, user)
    m, cal = a["matchedUser"], b["matchedUser"]["userCalendar"]
    tot = {x["difficulty"]: x["count"] for x in a["allQuestionsCount"]}
    got = {x["difficulty"]: x["count"] for x in m["submitStatsGlobal"]["acSubmissionNum"]}
    days = {}
    for ts, n in json.loads(cal["submissionCalendar"]).items():
        d = dt.datetime.fromtimestamp(int(ts), dt.timezone.utc).date()
        days[d] = days.get(d, 0) + n
    active = sorted(d for d, n in days.items() if n > 0)
    best = run = 0
    prev = None
    for d in active:
        run = run + 1 if prev and (d - prev).days == 1 else 1
        best, prev = max(best, run), d
    today = dt.datetime.now(dt.timezone.utc).date()
    cur, d = 0, today if today in days else today - dt.timedelta(days=1)
    while days.get(d, 0) > 0:
        cur, d = cur + 1, d - dt.timedelta(days=1)
    badges = sorted(m["badges"], key=lambda x: x.get("creationDate") or "", reverse=True)
    return dict(
        rank=m["profile"]["ranking"], solved=got["All"], total=tot["All"],
        easy=(got["Easy"], tot["Easy"]), medium=(got["Medium"], tot["Medium"]),
        hard=(got["Hard"], tot["Hard"]), streak=cur, max_streak=best,
        active_days=cal["totalActiveDays"], submissions=sum(days.values()),
        badge_count=len(badges), badges=[x["displayName"] for x in badges[:6]], days=days)


def render(d):
    e, W, H = html.escape, 900, 530
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         'font-family="Segoe UI, Helvetica, Arial, sans-serif">',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="#1a1a1a" stroke="#333"/>',
         '<text x="40" y="52" font-size="26" font-weight="700" fill="#fff">Umesh-kale9192</text>',
         '<text x="40" y="74" font-size="13" fill="#9a9a9a">LeetCode profile</text>',
         f'<text x="860" y="52" font-size="22" font-weight="700" fill="#ffa116" text-anchor="end">Rank {d["rank"]:,}</text>',
         '<rect x="30" y="90" width="420" height="170" rx="12" fill="#262626"/>',
         '<rect x="470" y="90" width="400" height="170" rx="12" fill="#262626"/>']
    # progress ring
    cx, cy, r = 125, 175, 52
    c = 2 * math.pi * r
    frac = d["solved"] / d["total"]
    s += [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#3a3a3a" stroke-width="8"/>',
          f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#ffa116" stroke-width="8" stroke-linecap="round" '
          f'stroke-dasharray="{c*frac:.1f} {c:.1f}" transform="rotate(-90 {cx} {cy})"/>',
          f'<text x="{cx}" y="{cy+6}" font-size="30" font-weight="700" fill="#fff" text-anchor="middle">{d["solved"]}</text>',
          f'<text x="{cx}" y="{cy+26}" font-size="12" fill="#9a9a9a" text-anchor="middle">of {d["total"]} solved</text>']
    for i, (name, key, col) in enumerate([("Easy", "easy", "#00b8a3"), ("Medium", "medium", "#ffc01e"), ("Hard", "hard", "#ef4743")]):
        got, tot = d[key]
        y = 128 + i * 45
        s += [f'<text x="215" y="{y}" font-size="15" font-weight="600" fill="{col}">{name}</text>',
              f'<text x="425" y="{y}" font-size="15" fill="#fff" text-anchor="end">{got} / {tot}</text>',
              f'<rect x="215" y="{y+8}" width="210" height="6" rx="3" fill="#3a3a3a"/>',
              f'<rect x="215" y="{y+8}" width="{max(4, 210*got/tot):.0f}" height="6" rx="3" fill="{col}"/>']
    # badges panel
    s += [f'<text x="490" y="122" font-size="14" fill="#9a9a9a">Badges</text>',
          f'<text x="490" y="158" font-size="34" font-weight="700" fill="#fff">{d["badge_count"]}</text>']
    x, y = 490, 186
    for name in d["badges"]:
        w = 14 + 7.2 * len(name)
        if x + w > 855:
            x, y = 490, y + 34
        s += [f'<rect x="{x}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="#3a3a3a"/>',
              f'<text x="{x+w/2:.0f}" y="{y+18}" font-size="12" fill="#ffa116" text-anchor="middle">{e(name)}</text>']
        x += w + 8
    # stat tiles
    tiles = [("Current streak", f'{d["streak"]} days'), ("Max streak", f'{d["max_streak"]} days'),
             ("Total active days", d["active_days"]), ("Submissions (1 yr)", d["submissions"])]
    for i, (k, v) in enumerate(tiles):
        tx = 30 + i * 213
        s += [f'<rect x="{tx}" y="278" width="201" height="62" rx="12" fill="#262626"/>',
              f'<text x="{tx+16}" y="302" font-size="12" fill="#9a9a9a">{k}</text>',
              f'<text x="{tx+16}" y="328" font-size="22" font-weight="700" fill="#fff">{v}</text>']
    # heatmap
    s += ['<rect x="30" y="358" width="840" height="152" rx="12" fill="#262626"/>',
          f'<text x="50" y="384" font-size="14" fill="#fff">{d["submissions"]} submissions in the past year</text>']
    if d["days"]:
        today = dt.datetime.now(dt.timezone.utc).date()
        start = today - dt.timedelta(days=(today.weekday() + 1) % 7) - dt.timedelta(weeks=52)
        cols = ["#3a3a3a", "#0e4429", "#006d32", "#26a641", "#39d353"]
        for wk in range(53):
            for dy in range(7):
                day = start + dt.timedelta(days=wk * 7 + dy)
                if day > today:
                    continue
                n = d["days"].get(day, 0)
                lvl = 0 if n == 0 else 1 if n < 2 else 2 if n < 4 else 3 if n < 7 else 4
                s.append(f'<rect x="{50+wk*15}" y="{398+dy*15}" width="12" height="12" rx="2" fill="{cols[lvl]}"/>')
    else:
        s.append('<text x="450" y="452" font-size="14" fill="#9a9a9a" text-anchor="middle">Heatmap fills in after the first daily update</text>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    user = sys.argv[1]
    data = SNAPSHOT if "--offline" in sys.argv else fetch(user)
    open(OUT, "w", encoding="utf-8").write(render(data))
    print("wrote", OUT)
