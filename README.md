# Maryland Responsible AI Council (MRAC) website

Static rebuild of [marylandresponsibleai.org](https://marylandresponsibleai.org), deployed with GitHub Pages.

## Editing content

All text lives in `content/` — no HTML editing needed for routine updates:

- `content/site.json` — intro, "The Council will" list, key areas, meetings, recommendations
- `content/members.json` — members (`group` is `founding` or `council`), bios, photo paths

Headshots go in `assets/img/members/`. The header and lighthouse photos are set under `photos` in `site.json` (Unsplash License; credits are shown in the footer). Keep large photos under ~700 KB. In a bio, a short line without ending punctuation becomes a heading, and lines starting with `– ` become a bulleted list.

To add a meeting, append to `meetings` in `site.json`:

```json
{ "date": "Jan 15, 2027", "title": "Quarterly Council Meeting", "description": "Virtual, 10am–12pm" }
```

## Preview locally

```bash
python3 build.py --serve
```

Then open http://localhost:8000. Requires only Python 3 (no dependencies).

## Deploying

Pushing to `main` runs `.github/workflows/pages.yml`, which builds the site and publishes it to GitHub Pages.
One-time setup in the GitHub repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

To serve it at `marylandresponsibleai.org`, set the custom domain under Settings → Pages and point the domain's DNS at GitHub Pages.
