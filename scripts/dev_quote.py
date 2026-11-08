#!/usr/bin/env python3
"""Pick a random developer quote and write it as dev-quote.svg.

Run it again and you get a different quote (it never repeats the current one).
"""
import html, random, re, textwrap

OUT = "dev-quote.svg"

QUOTES = [
    ("Talk is cheap. Show me the code.", "Linus Torvalds"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.", "Harold Abelson"),
    ("Premature optimization is the root of all evil.", "Donald Knuth"),
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra"),
    ("First, solve the problem. Then, write the code.", "John Johnson"),
    ("Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "Martin Fowler"),
    ("Make it work, make it right, make it fast.", "Kent Beck"),
    ("The best way to predict the future is to invent it.", "Alan Kay"),
    ("Everyone knows that debugging is twice as hard as writing a program in the first place.", "Brian Kernighan"),
    ("Measuring programming progress by lines of code is like measuring aircraft building progress by weight.", "Bill Gates"),
    ("Before software can be reusable it first has to be usable.", "Ralph Johnson"),
    ("Good code is its own best documentation.", "Steve McConnell"),
    ("Testing leads to failure, and failure leads to understanding.", "Burt Rutan"),
    ("The function of good software is to make the complex appear to be simple.", "Grady Booch"),
    ("Programming isn't about what you know; it's about what you can figure out.", "Chris Pine"),
    ("Fix the cause, not the symptom.", "Steve Maguire"),
    ("Software is eating the world.", "Marc Andreessen"),
    ("Optimism is an occupational hazard of programming; feedback is the treatment.", "Kent Beck"),
    ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
    ("Learning to write programs stretches your mind, and helps you think better.", "Bill Gates"),
]


def current():
    try:
        m = re.search(r"<title>(.*?)</title>", open(OUT, encoding="utf-8").read(), re.S)
        return html.unescape(m.group(1)) if m else None
    except FileNotFoundError:
        return None


def render(text, author):
    e = html.escape
    lines = textwrap.wrap(text, 62)
    h = 96 + 30 * len(lines)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="860" height="{h}" viewBox="0 0 860 {h}" '
         'font-family="Segoe UI, Helvetica, Arial, sans-serif">',
         f'<title>{e(text)}</title>',
         f'<rect x="1" y="1" width="858" height="{h-2}" rx="14" fill="#161b22" stroke="#30363d"/>',
         f'<rect x="1" y="1" width="8" height="{h-2}" rx="4" fill="#00d4ff"/>',
         '<text x="40" y="38" font-size="12" letter-spacing="2" fill="#8b949e">DEVELOPER QUOTE</text>']
    for i, ln in enumerate(lines):
        pre = "\u201c" if i == 0 else ""
        post = "\u201d" if i == len(lines) - 1 else ""
        s.append(f'<text x="40" y="{76 + 30*i}" font-size="21" font-style="italic" fill="#e6edf3">{e(pre + ln + post)}</text>')
    s.append(f'<text x="820" y="{h-24}" font-size="15" fill="#00d4ff" text-anchor="end">\u2014 {e(author)}</text>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    now = current()
    pool = [q for q in QUOTES if q[0] != now] or QUOTES
    text, author = random.choice(pool)
    open(OUT, "w", encoding="utf-8").write(render(text, author))
    print("wrote", OUT, "-", text)
