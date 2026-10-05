#!/usr/bin/env python3
"""Generate the static MRAC site into _site/ from content/*.json.

Usage: python3 build.py            # build into ./_site
       python3 build.py --serve    # build, then serve at http://localhost:8000
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
site = json.loads((ROOT / "content/site.json").read_text())
members = json.loads((ROOT / "content/members.json").read_text())

e = html.escape

NAV = [
    ("Home", "index.html#home"),
    ("Key Areas", "index.html#key-areas"),
    ("Members", "index.html#members"),
    ("Recommendations", "meetings.html#recommendations"),
    ("Meetings", "meetings.html#meetings"),
    ("Education", "education.html"),
]


def nav_links(base, cls=""):
    return "\n".join(f'<li><a class="{cls}" href="{base}{href}">{e(label)}</a></li>' for label, href in NAV)


def page(title, body, base="", description=None):
    desc = e(description or site["tagline"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="{base}assets/img/favicon-32.png" sizes="32x32">
<link rel="icon" href="{base}assets/img/favicon-192.png" sizes="192x192">
<link rel="apple-touch-icon" href="{base}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500&family=Roboto+Slab:wght@400&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/css/style.css">
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="{base}index.html" aria-label="Maryland Responsible AI Council home">
      <img src="{base}assets/img/logo-horizontal.svg" alt="Maryland Responsible AI Council" width="160" height="50">
    </a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
    <nav id="primary-nav" class="primary-nav" aria-label="Main">
      <ul>
{nav_links(base)}
      </ul>
    </nav>
  </div>
</header>
<main id="content">
{body}
</main>
<footer class="site-footer">
  <div class="dots" aria-hidden="true"></div>
  <div class="container footer-inner">
    <img class="footer-logo" src="{base}assets/img/logo-vertical-negative.svg" alt="Maryland Responsible AI Council" width="180" height="160">
    <nav aria-label="Footer"><ul class="footer-nav">
{nav_links(base)}
    </ul></nav>
    <p class="address">{e(site["address"])}. <a href="tel:{site["phone"]}">{e(site["phone"])}</a></p>
    <p class="copyright">&copy; <span data-year></span> Maryland Responsible AI Council</p>
  </div>
</footer>
<script src="{base}assets/js/main.js"></script>
</body>
</html>
"""


def subtitle(m):
    return " – ".join(x for x in (m["role"], m["affiliation"]) if x)


def member_card(m):
    sub = f'<p class="member-sub">{e(subtitle(m))}</p>' if subtitle(m) else ""
    return f"""<li class="member">
  <a href="members/{m["slug"]}.html">
    <img src="{m["image"]}" alt="" loading="lazy" width="180" height="180">
    <h3>{e(m["name"])}</h3>
  </a>
  {sub}
</li>"""


def render_bio(lines):
    """Lines become paragraphs; short label lines become headings; '– x' lines become lists."""
    out, items = [], []

    def flush():
        if items:
            out.append("<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>")
            items.clear()

    for line in lines:
        if line.startswith(("– ", "- ")):
            items.append(line[2:])
            continue
        flush()
        if len(line) < 40 and not re.search(r"[.;]$", line):
            out.append(f"<h2>{e(line.rstrip(':'))}</h2>")
        else:
            out.append(f"<p>{e(line)}</p>")
    flush()
    return "\n".join(out)


def build_index():
    will = "".join(f"<li>{e(x)}</li>" for x in site["council_will"])
    areas_lists = "".join(
        f'<div class="area"><h3>{e(a["title"])}</h3><ul>{"".join(f"<li>{e(i)}</li>" for i in a["items"])}</ul></div>'
        for a in site["key_areas"] if a["items"]
    )
    areas_plain = "".join(f'<div class="area"><h3>{e(a["title"])}</h3></div>' for a in site["key_areas"] if not a["items"])
    founding = "\n".join(member_card(m) for m in members if m["group"] == "founding")
    council = "\n".join(member_card(m) for m in members if m["group"] == "council")
    body = f"""
<section id="home" class="hero">
  <div class="container hero-inner">
    <div class="hero-logo">
      <img src="assets/img/logo-vertical.svg" alt="Maryland Responsible AI Council logo" width="360" height="320">
    </div>
    <div class="hero-card">
      <p class="lead">{e(site["intro"])}</p>
      <p>The Council will:</p>
      <ul>{will}</ul>
    </div>
  </div>
</section>

<section id="key-areas" class="tinted">
  <div class="container">
    <h2 class="section-title">MRAC Will Focus On The Following Key Areas:</h2>
    <div class="areas">{areas_lists}</div>
    <div class="areas areas-plain">{areas_plain}</div>
  </div>
</section>

<section id="members" class="tinted members-section">
  <div class="container">
    <h2 class="section-title">MRAC Founding Members</h2>
    <ul class="member-grid">
{founding}
    </ul>
    <h2 class="section-title">MRAC Council Members</h2>
    <ul class="member-grid">
{council}
    </ul>
  </div>
</section>
"""
    return page(f'{site["title"]} - A Technology and process innovator', body)


def build_member(m):
    body = f"""
<section class="bio">
  <div class="container bio-inner">
    <aside class="bio-aside">
      <img src="../{m["image"]}" alt="Portrait of {e(m["name"])}" width="300" height="300">
      <h1>{e(m["name"])}</h1>
      <p class="member-sub">{e(subtitle(m))}</p>
      <a class="back" href="../index.html#members">&larr; All members</a>
    </aside>
    <article class="bio-body">
{render_bio(m["bio"])}
    </article>
  </div>
</section>
"""
    return page(f'{m["name"]} - Maryland Responsible AI Council', body, base="../",
                description=m["bio"][0][:160] if m["bio"] else None)


def build_meetings():
    if site["meetings"]:
        meetings = "".join(
            f'<li><time>{e(x["date"])}</time><div><strong>{e(x["title"])}</strong>'
            + (f'<p>{e(x["description"])}</p>' if x.get("description") else "") + "</div></li>"
            for x in site["meetings"]
        )
        meetings = f'<ul class="listing">{meetings}</ul>'
    else:
        meetings = '<p class="empty">Upcoming meeting dates will be posted here.</p>'

    def rec(r):
        t = e(r["title"])
        t = f'<a href="{e(r["url"])}">{t}</a>' if r.get("url") else t
        return f'<li><time>{e(r["date"])}</time><div><strong>{t}</strong></div></li>'

    recs = f'<ul class="listing">{"".join(rec(r) for r in site["recommendations"])}</ul>'
    body = f"""
<section id="meetings" class="tinted">
  <div class="container narrow">
    <h1 class="section-title">Meetings</h1>
    {meetings}
  </div>
</section>
<section id="recommendations">
  <div class="container narrow">
    <h2 class="section-title">Recommendations</h2>
    {recs}
  </div>
</section>
"""
    return page("Meetings & Recommendations - Maryland Responsible AI Council", body)


def build_education():
    body = """
<section class="tinted">
  <div class="container narrow">
    <h1 class="section-title">Education</h1>
    <p class="empty">Educational resources from the Council are coming soon.</p>
  </div>
</section>
"""
    return page("Education - Maryland Responsible AI Council", body)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "members").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("")
    (OUT / "index.html").write_text(build_index())
    (OUT / "meetings.html").write_text(build_meetings())
    (OUT / "education.html").write_text(build_education())
    (OUT / "404.html").write_text(page("Page not found - Maryland Responsible AI Council",
        '<section class="tinted"><div class="container narrow"><h1 class="section-title">Page not found</h1>'
        '<p class="empty"><a href="index.html">Return to the home page</a></p></div></section>'))
    for m in members:
        (OUT / "members" / f'{m["slug"]}.html').write_text(build_member(m))
    print(f"Built {3 + len(members)} pages into {OUT}")

    if "--serve" in sys.argv:
        import functools, http.server
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
        print("Serving at http://localhost:8000")
        http.server.ThreadingHTTPServer(("", 8000), handler).serve_forever()


if __name__ == "__main__":
    main()
