#!/usr/bin/env python3
"""Generate the static MRAC site into _site/ from content/*.json.

Usage: python3 build.py            # build into ./_site
       python3 build.py --serve    # build, then serve at http://localhost:8000
"""
import hashlib
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


def asset_version(path):
    """Short content hash appended to CSS/JS URLs so browsers fetch new versions after deploys."""
    return hashlib.sha1((ROOT / path).read_bytes()).hexdigest()[:8]


CSS_V = asset_version("assets/css/style.css")
JS_V = asset_version("assets/js/main.js")

NAV = [
    ("Home", "index.html#home"),
    ("Key Areas", "index.html#key-areas"),
    ("Members", "index.html#members"),
    ("Recommendations", "meetings.html#recommendations"),
    ("Meetings", "meetings.html#meetings"),
    ("Education", "education.html"),
]


def nav_links(base):
    return "\n".join(f'<li><a href="{base}{href}">{e(label)}</a></li>' for label, href in NAV)


def icon(name):
    return f'<i class="ti ti-{name}" aria-hidden="true"></i>'


def photo_credits():
    return " · ".join(
        f'{label} photo: <a href="{e(p["credit_url"])}">{e(p["credit"])}</a> / Unsplash'
        for label, p in (("Header", site["photos"]["hero"]), ("Lighthouse", site["photos"]["band"]))
    )


def page(title, body, base="", description=None, overlay=False):
    """overlay=True makes the header transparent over a full-bleed hero until the page scrolls."""
    desc = e(description or site["tagline"])
    header_cls = "site-header overlay" if overlay else "site-header"
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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css" rel="stylesheet">
<link rel="stylesheet" href="{base}assets/css/style.css?v={CSS_V}">
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="{header_cls}">
  <div class="flag-stripe" aria-hidden="true"><span></span><span></span><span></span></div>
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
  <div class="flag-stripe" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="container footer-inner">
    <div class="footer-brand">
      <img class="footer-logo" src="{base}assets/img/logo-vertical-negative.svg" alt="Maryland Responsible AI Council" width="150" height="133">
      <p>{e(site["tagline"])}</p>
    </div>
    <nav aria-label="Footer"><ul class="footer-nav">
{nav_links(base)}
    </ul></nav>
  </div>
  <div class="container footer-meta">
    <p>&copy; <span data-year></span> Maryland Responsible AI Council</p>
    <p class="credits">{photo_credits()}</p>
  </div>
</footer>
<script src="{base}assets/js/main.js?v={JS_V}"></script>
</body>
</html>
"""


def subtitle(m):
    return " – ".join(x for x in (m["role"], m["affiliation"]) if x)


def member_card(m):
    sub = f'<p class="member-sub">{e(subtitle(m))}</p>' if subtitle(m) else ""
    return f"""<li class="member">
  <a href="members/{m["slug"]}.html">
    <img src="{m["image"]}" alt="" loading="lazy" width="160" height="160">
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


def page_hero(title, eyebrow, base):
    """Compact photo banner used at the top of inner pages."""
    return f"""
<section class="page-hero" style="--hero-img: url('{base}{site["photos"]["hero"]["src"]}')">
  <div class="container">
    <p class="eyebrow">{e(eyebrow)}</p>
    <h1>{e(title)}</h1>
  </div>
</section>"""


def rec_item(r):
    t = e(r["title"])
    t = f'<a href="{e(r["url"])}">{t}</a>' if r.get("url") else t
    return f'<li><time>{e(r["date"])}</time><div><strong>{t}</strong></div></li>'


def build_index():
    hero, band = site["photos"]["hero"], site["photos"]["band"]
    will = "".join(f"<li><span class=\"num\">{i:02d}</span><p>{e(x)}</p></li>"
                   for i, x in enumerate(site["council_will"], 1))

    def area(i, a):
        items = f'<ul>{"".join(f"<li>{e(x)}</li>" for x in a["items"])}</ul>' if a["items"] else ""
        cls = "area-card" + (" wide" if a["items"] else "")
        return (f'<div class="{cls}"><div class="area-head"><span class="area-icon">{icon(a["icon"])}</span>'
                f'<span class="num">{i:02d}</span></div><h3>{e(a["title"])}</h3>{items}</div>')

    areas = "".join(area(i, a) for i, a in enumerate(site["key_areas"], 1))
    recs = "".join(
        f'<a class="rec-card" href="meetings.html#recommendations"><span class="tag">Recommendation</span>'
        f'<strong>{e(r["title"])}</strong><time>{e(r["date"])}</time></a>'
        for r in site["recommendations"]
    )
    founding = "\n".join(member_card(m) for m in members if m["group"] == "founding")
    council = "\n".join(member_card(m) for m in members if m["group"] == "council")
    body = f"""
<section id="home" class="hero">
  <img class="hero-img" src="{hero["src"]}" alt="{e(hero["alt"])}" width="1800" height="1419" fetchpriority="high">
  <div class="hero-shade" aria-hidden="true"></div>
  <div class="container hero-content">
    <p class="eyebrow">Maryland Responsible AI Council</p>
    <h1>{e(site["headline"])}</h1>
    <p class="hero-lead">{e(site["intro"])}</p>
    <div class="hero-actions">
      <a class="btn btn-gold" href="meetings.html#recommendations">Read our recommendations</a>
      <a class="btn btn-ghost" href="#members">Meet the council</a>
    </div>
  </div>
  <a class="scroll-cue" href="#mission" aria-label="Scroll to mission">{icon("chevron-down")}</a>
</section>

<section id="mission" class="section">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow">Our charge</p>
      <h2>The Council will</h2>
    </div>
    <ol class="charge-list">{will}</ol>
  </div>
</section>

<section id="key-areas" class="section tinted">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow">Focus</p>
      <h2>MRAC will focus on the following key areas</h2>
    </div>
    <div class="area-grid">{areas}</div>
  </div>
</section>

<section class="photo-band" aria-label="{e(band["alt"])}">
  <img class="band-img" src="{band["src"]}" alt="" loading="lazy" width="2000" height="1125">
  <div class="band-shade" aria-hidden="true"></div>
  <div class="container band-content">
    <p class="band-quote">{e(site["tagline"])}</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head split">
      <div><p class="eyebrow">Our work</p><h2>Latest recommendations</h2></div>
      <a class="text-link" href="meetings.html#recommendations">All recommendations {icon("arrow-right")}</a>
    </div>
    <div class="rec-grid">{recs}</div>
  </div>
</section>

<section id="members" class="section tinted">
  <div class="container">
    <div class="section-head">
      <p class="eyebrow">Leadership</p>
      <h2>Founding members</h2>
    </div>
    <ul class="member-grid">
{founding}
    </ul>
    <div class="section-head">
      <p class="eyebrow">Council</p>
      <h2>Council members</h2>
    </div>
    <ul class="member-grid">
{council}
    </ul>
  </div>
</section>
"""
    return page(f'{site["title"]} - Ethical AI for the State of Maryland', body, overlay=True)


def build_member(m):
    body = f"""
{page_hero(m["name"], subtitle(m) or "Council member", "../")}
<section class="section bio">
  <div class="container bio-inner">
    <aside class="bio-aside">
      <img src="../{m["image"]}" alt="Portrait of {e(m["name"])}" width="300" height="300">
      <a class="text-link" href="../index.html#members">{icon("arrow-left")} All members</a>
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

    recs = f'<ul class="listing">{"".join(rec_item(r) for r in site["recommendations"])}</ul>'
    body = f"""
{page_hero("Meetings and recommendations", "Council activity", "")}
<section id="meetings" class="section">
  <div class="container narrow">
    <h2>Meetings</h2>
    {meetings}
  </div>
</section>
<section id="recommendations" class="section tinted">
  <div class="container narrow">
    <h2>Recommendations</h2>
    {recs}
  </div>
</section>
"""
    return page("Meetings & Recommendations - Maryland Responsible AI Council", body)


def build_education():
    body = f"""
{page_hero("Education", "Resources", "")}
<section class="section">
  <div class="container narrow">
    <p class="empty">Educational resources from the Council are coming soon.</p>
  </div>
</section>
"""
    return page("Education - Maryland Responsible AI Council", body)


def build_404():
    body = f"""
{page_hero("Page not found", "404", "")}
<section class="section">
  <div class="container narrow">
    <p class="empty"><a href="index.html">Return to the home page</a></p>
  </div>
</section>
"""
    return page("Page not found - Maryland Responsible AI Council", body)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "members").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("")
    (OUT / "index.html").write_text(build_index())
    (OUT / "meetings.html").write_text(build_meetings())
    (OUT / "education.html").write_text(build_education())
    (OUT / "404.html").write_text(build_404())
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
